/* ============================================================================
   SAT Freshman -- Words, shared (spec/rebuild-v2.md 3.8 §1, §4, §10, §11;
   v2-upgrades/words.md W1-W14, W21; decisions 2, 4, 7)

   Loaded after ui.js and kit.js on every Words page (and wherever a page wants the
   sheet or the add sheet). Adds to window.UI. question.js is loaded on first use
   (the sheet's SAT-style sample). Styles are injected once, on ui.css tokens.

     UI.wordsTabs(host, active)              Library · Flashcards · Quiz · My words
     UI.todayWords(host, {lib})              the Today's words panel (W11) -> {el, refresh}
     UI.wordsFinish(host, insights, {lib})   By exam day (W12)
     UI.word.open(slug, {list, covered, onChange, onClose})   the word sheet (§4, W1, W3,
                                             W4, W7, W9, W13, W14); ?w= follows it
     UI.word.status(row) UI.word.level(m) UI.word.pips(row) UI.word.label(row)
     UI.word.index()                         GET /api/words/index once -> {bySlug, byWord}
     UI.startWords(body, {from, fallback})   POST /api/words/run, then /words/run/?id=
     UI.addWord(prefill)                     the Add sheet (§10, R29); prefill.id edits
     UI.addWordFromSelection(root, {source}) -> unbind   selecting 1–6 words in root floats
         Add to my words; source is a string or () => string ("From a Circles question")
     UI.bringWords('text' | 'list' | 'missed' | 'import')   Bring words (W19): matched in the browser
     UI.gloss(el, {exclude, ref})            tap-to-define in Words texts (§11)
     UI.speak(text) (UI.speak.ok())          the device's en-US voice
   ========================================================================== */
(() => {
  'use strict';
  const UI = window.UI || (window.UI = {});
  const doc = document;
  const h = UI.h;

  /* ------------------------------------------------------------ styles */
  const CSS = `
.wtabs { display: inline-flex; gap: 2px; padding: 3px; border-radius: 10px; background: var(--well); box-shadow: inset 0 1px 2px rgb(var(--sh) / .08); max-width: 100%; overflow-x: auto; }
.wtabs a { position: relative; isolation: isolate; display: inline-flex; align-items: center; gap: 6px; min-height: calc(var(--ctl) - 4px); padding: 0 12px; border-radius: 8px;
  font: 500 14px var(--font); color: var(--ink); text-decoration: none; white-space: nowrap; }
.wtabs a[aria-current="page"] { font-weight: 600; }
/* the current tab's thumb (the .seg thumb) is its own named layer, so a page change slides it to the new tab */
.wtabs .wt-mark { position: absolute; inset: 0; z-index: -1; border-radius: inherit; background: var(--thumb, var(--face)); box-shadow: var(--seg-thumb);
  pointer-events: none; view-transition-name: wtab-mark; }
::view-transition-group(wtab-mark) { animation-duration: var(--m-slow, 260ms); animation-timing-function: var(--ease-move, ease); }
.wtabs .n { font: 500 12.5px var(--font); color: var(--soft); font-variant-numeric: tabular-nums; }
.wtabs .dot { background: var(--ink-2); }   /* graphite, as the shell's count dots: the page's orange is its Start */
.wtabs .s { display: none; }
@media (hover: hover) and (pointer: fine) { .wtabs a:not([aria-current]):hover { background: var(--hover); } }
@media (max-width: 419px) { .wtabs { display: flex; } .wtabs a { flex: 1; justify-content: center; padding: 0 8px; } .wtabs .l { display: none; } .wtabs .s { display: inline; } }
.today-words { display: grid; gap: 12px; }
.tw-top { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; }
.tw-top h2, .tw-line h2 { font: 600 16px/1.3 var(--font); letter-spacing: -.01em; }
.tw-facts { font: 500 12.5px var(--font); color: var(--soft); font-variant-numeric: tabular-nums; }
.tw-fig { margin-top: -4px; }
.tw-row { display: flex; align-items: center; gap: 8px; }
/* the goal met: the ticks go to the calm amber tone, so Start under them is the one orange */
.today-words .meter.done.ticks .meter-bar > i[data-on] { background: var(--amber-200); }
.tw-row > .pill, .tw-row > .split-btn, .tw-row > .split-btn > .pill:first-child { flex: 1 1 auto; }
.tw-done { display: flex; align-items: center; gap: 12px; }
.tw-done .spot { width: 48px; height: 48px; }
.tw-note { font: 400 14px/1.45 var(--font); color: var(--ink); }
.tw-note b { font-weight: 600; }
.tw-find { display: grid; gap: 6px; }
.tw-find .field { width: 100%; }
.tw-find-h { margin: 0; }
.today-words .tw-off { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 0; padding-top: 12px; border-top: 1px solid var(--line); }
.tw-line { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; }
.tw-line .btn { margin-left: auto; }
@media (max-width: 759px), (pointer: coarse) { .today-words .tw-row :is(.pill, .btn) { height: var(--touch); } }
.wfin { display: grid; gap: 8px; }
.wfin .tw-top { align-items: center; }
.wfin .tw-top > .btn { margin-left: auto; }
.wfin-l { font: 400 14px/1.5 var(--font); }
.wfin-l b { font-weight: 600; }
.wfin .chips { flex-wrap: wrap; margin-top: 8px; }
.wfin > details > .fold-s { display: flex; flex-wrap: wrap; width: 100%; align-items: center; gap: 4px 12px; color: var(--ink); }
.wfin .fold-s h2 { font: 600 16px/1.3 var(--font); letter-spacing: -.01em; }
.wfin > details[open] > .fold-s { margin-bottom: 8px; }
.wfin > details[open] > .fold-s .tw-facts { display: none; }
.wfin-body { display: grid; gap: 8px; }
.wfin-left { font: 500 12.5px var(--font); color: var(--soft); }
@media (max-width: 759px) { .wfin .chips { flex-wrap: nowrap; overflow-x: auto; padding: 3px 2px; scrollbar-width: none; } .wfin .chips > * { flex: none; } }
@media (min-width: 760px) { dialog.sheet.wsheet { max-width: min(720px, calc(100vw - 32px)); max-height: 88vh; } }
@media (max-width: 759px) { .wsheet > .sheet-head { flex-wrap: wrap; } .wsheet .ws-tools { order: 3; flex-basis: 100%; margin: 0 0 0 -8px; } }
.wsheet > .sheet-head { position: sticky; top: 0; background: inherit; z-index: 1; }
dialog.sheet.wsheet > .sheet-head > h2 { font: 600 22px/1.2 var(--font); letter-spacing: -.02em; overflow-wrap: normal; word-break: normal; flex: 0 1 auto; }
.ws-mode { margin-left: auto; }
.ws-mode .seg { --ctl: 30px; }
.ws-tools { display: flex; flex: none; align-items: center; gap: 2px; margin-left: auto; }
.ws-sub { display: flex; flex-wrap: wrap; gap: 4px 8px; align-items: center; margin: -4px 0 12px; font: 500 12.5px var(--font); color: var(--soft); }
.ws-lv { display: inline-flex; align-items: center; gap: 6px; }
.wb { padding: 12px 0; border-top: 1px solid var(--line); }
.wb:first-of-type { border-top: 0; }
.wsheet.covered .wb.cov { border-top-color: transparent; }   /* the face-down plates separate the blocks; no hairline between them */
.wb > .k { display: block; margin-bottom: 8px; }
.wb .meaning { font: 400 19px/1.5 var(--serif); }
.wb .ex { font: 400 16.5px/1.55 var(--serif); margin: 4px 0; }
.wb .ex mark, .fsent mark { background: var(--wash); color: inherit; box-shadow: inset 0 -2px 0 var(--amber); padding: 0 1px; }
.wb .src { font: 400 12.5px var(--font); color: var(--soft); font-style: italic; }
.wb .line { font: 400 14px/1.5 var(--font); }
.wb .line + .line { margin-top: 4px; }
.wb .acts { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.wb details.fold { margin-top: 8px; }
.wchips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.wchips + .wchips { margin-top: 6px; }
.wchip { appearance: none; border: 0; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; min-height: 32px; padding: 0 12px;
  border-radius: 8px; background: var(--face); box-shadow: var(--shadow-btn); font: 500 14px var(--font); color: var(--ink);
  transition: background-color .14s var(--ease), box-shadow .14s var(--ease); }
button.wchip:not([aria-current="true"]):active { box-shadow: var(--shadow-btn-down); transition-duration: .05s; }
.wchip.plain { cursor: default; background: none; box-shadow: none; padding: 0 6px; }
.wchip[aria-current="true"] { background: var(--sel-bg); box-shadow: var(--sel-edge); font-weight: 600; }
.wchip small { font: 500 11.5px var(--font); color: var(--soft); }
@media (hover: hover) and (pointer: fine) { button.wchip:not([aria-current="true"]):hover { background: var(--face-hover); } }
.shade-n { margin-top: 8px; font: 400 14px/1.5 var(--serif); }
.shade-bar { height: 1px; margin-top: 8px; background: var(--line); }
.confu { display: grid; gap: 4px; padding: 8px 0; }
.confu + .confu { border-top: 1px solid var(--line); }
.confu h3 { font: 600 14.5px var(--font); }
.confu .wlink { margin: 0; padding: 0; font: inherit; }
.confu .t { font: 400 15px/1.5 var(--serif); }
.confu .fell { display: flex; align-items: center; gap: 6px; font: 500 12.5px var(--font); color: var(--ink); }
.confu .acts { display: flex; gap: 12px; margin-top: 8px; }
.ladder { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; margin: 8px 0; }
.ladder span { display: grid; gap: 4px; font: 500 11.5px var(--font); color: var(--soft); text-align: center; }
.ladder span::before { content: ""; height: 6px; border-radius: 3px; background: var(--track); }
.ladder span.on { color: var(--ink); }
.ladder span.on::before { background: var(--amber); }
.journey { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; margin: 8px 0; }
.journey i { width: 12px; height: 12px; border-radius: 50%; box-shadow: inset 0 0 0 1.5px var(--ink); font-style: normal; }
.journey i.ok { background: var(--amber); box-shadow: inset 0 0 0 1.5px var(--amber-deep); }
.journey i.ctx { border-radius: 3px; }
.journey .nx { font: 500 12.5px var(--font); color: var(--soft); margin-left: 6px; }
.hook { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.hook input { flex: 1; }
.wsample .q-stem { font-size: 17.5px; }
.wsample .ws-ask { margin: 6px 0 10px; font: 600 14px var(--font); }
.ws-foot { position: sticky; bottom: 0; flex-wrap: nowrap; }
.ws-foot .grow { flex: 1; }
.ws-foot > .btn.icon { flex: none; }
@media (max-width: 419px) { .ws-foot .l { display: none; } }
.wsheet.covered .cov { position: relative; }
.wsheet.covered .cov > :not(.k) { visibility: hidden; }
/* a covered block reads as a face-down card: a plate where the text will be */
.wsheet.covered .cov::after { content: "Covered"; position: absolute; inset: 32px 0 12px; min-height: 28px; display: grid; place-items: center; border-radius: 8px;
  background: var(--well); font: 500 12.5px var(--font); color: var(--soft); }
.wsheet.covered .cov-t { visibility: hidden; }
.wsheet.covered .wsample .opt-why, .wsheet.covered .wsample .ws-verdict .mistake, .wsheet.covered .wsample .v-clue { visibility: hidden; }
.wmsg { padding: 16px 0; font: 400 14.5px var(--font); }
button.term { appearance: none; border: 0; background: none; padding: 0; font: inherit; color: inherit; cursor: help;
  text-decoration: underline dotted var(--faint); text-decoration-thickness: 1.5px; text-underline-offset: 3px; }
.gpop { display: grid; gap: 6px; max-width: 300px; }
.gpop b { font: 600 16px var(--font); }
.gpop p { font: 400 14px/1.45 var(--font); }
.gpop .acts { display: flex; gap: 8px; flex-wrap: wrap; }
.addw { display: grid; gap: 12px; }
.addw .two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 559px) { .addw .two { grid-template-columns: 1fr; } }
.addw .field-err { margin-top: 4px; }
.addw .dup { font: 400 14px var(--font); }
.addw .w-side { display: grid; gap: 8px; }
.bm-grid { display: grid; grid-template-columns: 1fr auto auto; gap: 8px; align-items: center; }
.wsample .trap-chip, .wr .trap-chip { display: none; }
`;
  if (!doc.getElementById('words-ui-css')) doc.head.append(h('style', { id: 'words-ui-css', text: CSS }));

  /* ------------------------------------------------------------ helpers */
  // icons come from the shared map (UI.icon, Phosphor). Words' left / right were the steppers' chevrons; in the
  // map left / right are arrows, so they read as the carets here
  const ICON_AS = { left: 'caret_left', right: 'caret_right' };
  const ic = (n, size = 18) => (UI.icon && UI.icon(ICON_AS[n] || n, size)) || null;
  const toast = (t, o) => UI.toast ? UI.toast(t, o) : null;
  const cap = s => (s ? String(s)[0].toUpperCase() + String(s).slice(1) : '');
  const plural = (n, one, many) => `${UI.num ? UI.num(n) : n} ${n === 1 ? one : (many || one + 's')}`;
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const iso = d => { const x = new Date(d.getTime() - d.getTimezoneOffset() * 60000); return x.toISOString().slice(0, 10); };
  const today = () => iso(new Date());
  const addDays = (day, n) => { const d = new Date(day + 'T12:00:00'); d.setDate(d.getDate() + n); return iso(d); };
  const dayDiff = (a, b) => Math.round((new Date(b + 'T12:00:00') - new Date(a + 'T12:00:00')) / 864e5);
  const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  // 'Thu, Sep 26'; 'today' / 'tomorrow' when close
  function dayName(day, o = {}) {
    if (!day) return '';
    const d = String(day).slice(0, 10), n = dayDiff(today(), d);
    if (!o.plain && n === 0) return 'today';
    if (!o.plain && n === 1) return 'tomorrow';
    const x = new Date(d + 'T12:00:00');
    return `${DAYS[x.getDay()]}, ${MONTHS[x.getMonth()]} ${x.getDate()}`;
  }
  const shortDate = day => { if (!day) return ''; const x = new Date(String(day).slice(0, 10) + 'T12:00:00'); return `${MONTHS[x.getMonth()]} ${x.getDate()}`; };
  // the server's status lines carry ISO days: "Back 2026-09-30" -> "Back Wed, Sep 30"
  // a second sense lives after the dot in its slug: account.explanation reads "account · explanation"
  const senseOf = slug => (/^(u:|root:)/.test(slug || '') ? '' : (/\.(.+)$/.exec(slug || '') || [0, ''])[1].replace(/[-_]/g, ' '));
  const nameOf = (slug, w) => (senseOf(slug) ? `${w} · ${senseOf(slug)}` : w);
  const statusLine = s => String(s || '')
    .replace(/\bBack (\d{4}-\d{2}-\d{2})/, (m, d) => { const n = dayDiff(today(), d); return n <= 0 ? 'Back today' : n === 1 ? 'Back tomorrow' : n <= 21 ? `Back in ${n} days` : `Back ${dayName(d)}`; })
    .replace(/\d{4}-\d{2}-\d{2}/g, d => dayName(d));
  const POS = { 'n.': 'noun', 'v.': 'verb', 'adj.': 'adjective', 'adv.': 'adverb', 'phrase.': 'phrase', phrase: 'phrase' };
  const TRAP = { reversed: 'Reverses the meaning', too_strong: 'Too strong', too_weak: 'Too weak', connotation: 'Wrong tone',
    lookalike: 'Looks like the answer', everyday: 'Everyday meaning', topical: 'Fits the subject, not the blank',
    wrong_logic: 'Wrong relationship', reversed_direction: 'Cause and effect swapped', meaning: 'Different meaning' };
  // traps.json's check lines, shown under the reason (W1)
  const CHECK = { reversed: 'Does the passage favor this idea or push against it?', too_strong: 'Does the evidence justify that degree of certainty?',
    too_weak: 'Is the passage firmer than this word suggests?', connotation: 'Is the writer approving, disapproving, or neutral?',
    lookalike: 'Which of the similar-looking words actually means this?', everyday: 'What does this word mean in this particular sentence?',
    topical: 'What action or quality must the missing word express?', wrong_logic: 'Do the ideas add, contrast, explain, or follow from each other?',
    reversed_direction: 'Which event is the cause, and which is the result?' };
  // a verdict from the Words server in UI.workspace's feedback shape
  // (the daily items file the pick's index as a string: "2")
  const verdict = (r, answer) => {
    const g = Number.isInteger(r.given_index) ? r.given_index : Number.isInteger(r.given) ? r.given
      : typeof r.given === 'string' && /^[0-3]$/.test(r.given) ? +r.given : answer;
    const trap = r.trap !== undefined ? r.trap : r.traps && Number.isInteger(g) ? r.traps[g] : null;
    return { ...r, given: g, trap, trap_check: trap ? CHECK[trap] : null, ...(trap && MISS[trap] ? { mistake: MISS[trap] } : {}) };
  };
  const MISS = { meaning: 'You picked a word with a different meaning', reversed: 'You picked a word that reverses the meaning', too_strong: 'You picked a word that is too strong',
    too_weak: 'You picked a word that is too weak', connotation: 'You picked a word with the wrong tone', lookalike: 'You picked a word that looks like the answer',
    everyday: 'You picked the everyday meaning, not the one in this text', topical: 'You picked a word that fits the subject, not the blank',
    wrong_logic: 'You picked the wrong relationship', reversed_direction: 'You swapped cause and effect' };
  // a "most nearly means" item that still has a blank is an in-context item (a server mislabel guard)
  const blankNearly = it => !!it && it.kind === 'nearly' && /_{3,}/.test(it.text || '');
  const stemOf = it => (blankNearly(it) ? 'Which choice completes the text with the most logical and precise word or phrase?' : it && it.stem);
  const kindLabel = it => (it && it.kind === 'nearly' && /_{3,}/.test(it.text || '') ? 'In context' : (it && (it.head || KIND[it.kind])) || 'Words');
  const KIND = { card: 'Card', learn: 'Learn card', fix: 'Fix card', commit: 'Card', meaning2word: 'Meaning → word', word2meaning: 'Word → meaning',
    cloze: 'Fill the blank', incontext: 'In context', nearly: 'Most nearly means', precise: 'Most precise', order: 'Order the ladder',
    transition: 'Transitions', decode: 'Decode it', rootshare: 'Which root?', typed: 'Type it', placement: 'Placement', placement_check: 'Check',
    sort: 'Sort', sheet: 'Sheet' };
  const CONTEXT_KINDS = new Set(['incontext', 'nearly', 'precise', 'transition']);

  /* ------------------------------------------------------------ word facts (one reading of a library row) */
  const boxOf = w => (w && w.state && +w.state.box) || 0;
  function status(w) {
    if (!w) return 'new';
    const b = boxOf(w);
    if (b >= 4) return 'known';
    if (b === 3 && !w.proven) return 'claimed';
    if (b >= 1) return 'learning';
    if (w.placed === 2) return 'probable';
    return 'new';
  }
  const STATUS = { new: 'New', learning: 'Learning', claimed: 'Claimed', known: 'Known', probable: 'Probably known' };
  // W18: the shown level is the crowd blend; before any answer it is the prior, marked est.
  function level(m, fallback) {
    if (!m) return { tier: fallback || 'medium', text: '' };
    const p = m.pct;
    const tier = p >= 75 ? 'easy' : p >= 45 ? 'medium' : 'hard';
    return { tier, text: m.n ? `${p}% right in context · ${plural(m.n, 'answer')}` : 'est.', n: m.n };
  }
  function pips(w) {
    const b = Math.min(5, boxOf(w));
    return h('span', { class: 'pips', role: 'img', 'aria-label': `strength ${b} of 5` }, [0, 1, 2, 3, 4].map(i => h('i', { class: i < b ? 'on' : null })));
  }
  const dbars = tier => (UI.dbars ? UI.dbars(tier) : h('span', { class: 'dbars', 'data-tier': tier, text: cap(tier) }));
  // "mitigate, verb, science, medium, learning, due today, saved" (§14)
  function label(w) {
    return [w.word, POS[w.pos] || null, w.sense && w.sense !== 'main' ? w.sense.replace(/_/g, ' ') : null, (w.topics || [])[0] || null,
      level(w.measured, w.difficulty).tier, STATUS[status(w)].toLowerCase(), w.is_due ? 'due today' : null, w.saved ? 'saved' : null,
      w.proven ? 'proven' : null, w.stubborn ? 'stubborn' : null, w.trap ? 'fell for a trap' : null].filter(Boolean).join(', ');
  }

  let indexP = null;
  function index() {
    if (!indexP) {
      indexP = UI.api('/words/index', { quiet: true }).then(d => {
        const bySlug = new Map(), byWord = new Map();
        (d.words || []).forEach(w => { bySlug.set(w.slug, w); const k = w.word.toLowerCase(); if (!byWord.has(k)) byWord.set(k, w); });
        return { bySlug, byWord, words: d.words || [], common: d.common || [] };
      });
      indexP.catch(() => { indexP = null; });
    }
    return indexP;
  }

  /* ------------------------------------------------------------ start a run */
  function remember(from) { try { sessionStorage.setItem('satf.words.from', from || (location.pathname + location.search)); } catch (_) {} }
  // one start at a time (premium bug 8): the POST takes 200-600 ms, so the button that asked says busy (aria-busy, ui.css)
  // and a second tap gets the same promise instead of a second run. window.event is the click that called us, if any.
  let starting = null, busyBtn = null;
  addEventListener('pageshow', e => { if (e.persisted && busyBtn) busyBtn.removeAttribute('aria-busy'); });   // back from the run
  function busy(work, trigger) {
    if (starting) return starting;
    const ev = window.event;
    const btn = trigger || (ev && ev.type === 'click' && ev.target instanceof Element ? ev.target.closest('button, a') : null);
    if (btn) { btn.setAttribute('aria-busy', 'true'); busyBtn = btn; }
    starting = work().then(r => { if (!r && btn) btn.removeAttribute('aria-busy'); return r; }).finally(() => { starting = null; });
    return starting;
  }
  function startWords(body, o = {}) { return busy(() => postRun(body, o), o.trigger); }
  async function postRun(body, o = {}) {
    let r;
    try { r = await UI.api('/words/run', { method: 'POST', body }); }
    catch (e) {
      if (o.fallback && (e.status === 409 || e.status === 400)) return postRun(o.fallback, { ...o, fallback: null });
      if (!e.offline) toast(e.status === 409 || e.status === 400 || e.status === 422 ? cap(e.message) : 'Couldn’t start it. Try again.');
      return null;
    }
    remember(o.from);
    location.href = `/words/run/?id=${encodeURIComponent(r.id)}`;
    return r;
  }
  // the quick quiz: in context where the words have frames, else the two meaning types
  const QUIZ_FORMATS = ['meaning2word', 'word2meaning', 'incontext'];
  const quizBody = (deck, count) => ({ mode: 'quiz', deck, formats: QUIZ_FORMATS, count: count || 10 });
  const quizStart = (deck, count, o) => startWords(quizBody(deck, count), { ...o, fallback: { ...quizBody(deck, count), formats: ['meaning2word', 'word2meaning'] } });

  /* ------------------------------------------------------------ tabs (§1) */
  function wordsTabs(host, active, o = {}) {
    const due = o.due ?? ((UI.shellData && UI.shellData() && UI.shellData().words) || {}).due ?? 0;
    const T = [['library', '/words/', 'Library', 'Library'], ['cards', '/words/study/?mode=cards', 'Flashcards', 'Cards'],
      ['quiz', '/words/study/?mode=quiz', 'Quiz', 'Quiz'], ['mine', '/words/mine/', 'My words', 'Mine']];
    const el = h('nav', { class: 'wtabs', 'aria-label': 'Words' }, T.map(([id, href, l, s]) => h('a', { href, 'aria-current': id === active ? 'page' : null },
      id === active ? h('span', { class: 'wt-mark', 'aria-hidden': 'true' }) : null, h('span', { class: 'l', text: l }), h('span', { class: 's', text: s }),
      id === 'mine' && due ? [h('span', { class: 'dot', 'aria-hidden': 'true' }), h('span', { class: 'n', text: String(due), 'aria-label': `${due} due` })] : null)));
    if (host) host.replaceChildren(el);
    return el;
  }

  /* ------------------------------------------------------------ Today's words (W11) */
  /* "10 cards on transitions", "quiz 5 saved", "20 science": a count, cards or a quiz, and what to draw from.
     A saved / missed / due... keyword picks that deck; anything else matches a collection, a topic, a list, a root,
     a part of speech or the start of a word, and the set is drawn from the matches. */
  const FIND_DECKS = { due: 'due', new: 'new', saved: 'saved', missed: 'missed', mine: 'mine', stubborn: 'stubborn', 'looked up': 'looked_up', hard: 'hard_for_you' };
  function parseFind(text, words) {
    const t = String(text || '').toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').replace(/\s+/g, ' ').trim();
    if (!t) return null;
    const m = t.match(/\b(\d{1,3})\b/);
    const count = m ? Math.max(1, Math.min(200, +m[1])) : 10;
    const mode = /\b(quiz|test)\b/.test(t) ? 'quiz' : 'cards';
    let rest = t.replace(/\b\d{1,3}\b/g, ' ').replace(/\b(cards?|flashcards?|words?|quiz|test|on|about|for|of|from|with|me|the|a|some|my)\b/g, ' ').replace(/\s+/g, ' ').trim();
    const key = Object.keys(FIND_DECKS).find(k => rest === k || rest === k + 's');
    if (key || !rest) return { mode, count, label: key || 'new words', deck: { source: key ? FIND_DECKS[key] : 'new' }, n: null };
    const has = (w, term) => [w.collection, w.pos, ...(w.topics || []), ...(w.lists || []), ...(w.roots || []).map(x => (typeof x === 'string' ? x : x.root || x.id || ''))]
      .some(x => x && String(x).toLowerCase().replace(/_/g, ' ').includes(term)) || String(w.word || '').toLowerCase().startsWith(term);
    const hit = (words || []).filter(w => has(w, rest));
    if (!hit.length) return { mode, count, label: rest, none: true };
    const pick = hit.slice().sort(() => Math.random() - .5).slice(0, count).map(w => w.slug);
    return { mode, count: pick.length, label: rest, deck: { source: 'words', words: pick }, n: hit.length };
  }
  function todayWords(host, o = {}) {
    // the full card is the library's hero (premium): the due figure, the new-words ticks, Start and one Other ways menu.
    // o.card false: the page gives it its surface (the library wraps it with the daily questions and By exam day)
    const el = h('section', { class: (o.card === false ? '' : 'card ') + 'today-words', 'aria-label': 'Today’s words' });
    if (host) host.replaceChildren(el);
    let box = ls.get('satf.words.box', null), kept = null, taking = false;
    async function draw() {
      el.replaceChildren(h('div', { class: 'tw-top' }, h('h2', { text: 'Today’s words' })));
      if (UI.skel) UI.skel(el, 'line'); else el.append(h('p', { class: 'meta', text: 'Loading…' }));
      let d;
      try { d = await UI.api('/words/today', { quiet: true }); }
      catch (e) {
        el.replaceChildren(h('div', { class: 'tw-top' }, h('h2', { text: 'Today’s words' })));
        const k = e.offline ? await offline.stored() : null;
        if (k) {
          el.append(h('div', { class: 'tw-row' }, h('a', { class: 'pill', href: `/words/run/?id=${encodeURIComponent(k.id)}`, text: `Offline cards · ${k.left} left` })),
            h('p', { class: 'help', 'data-nofold': '', text: 'Grades wait on this device and sync when you’re back. Quizzes need a connection.' }));
          return;
        }
        if (UI.cardError) UI.cardError(el, draw, 'Today’s words did not load.');
        return;
      }
      paint(d.summary || {});
      // W22: a line at the foot only while the day's cards are kept on this device; taking them is in Other ways
      if (offline.ok() && !o.compact) offlineRow();
    }
    async function offlineRow() {
      kept = await offline.stored();
      el.querySelectorAll('.tw-off').forEach(x => x.remove());
      if (kept) el.append(h('p', { class: 'help tw-off', 'data-nofold': '' }, `${plural(kept.left, 'card')} on this device · `,
        h('a', { class: 'quiet', href: `/words/run/?id=${encodeURIComponent(kept.id)}`, text: 'Open' })));
    }
    async function takeOffline() {
      if (taking) return;
      taking = true;
      const r = await offline.take();
      taking = false;
      if (r) { toast(`${plural(r.items.length, 'card')} on this device · they work with no signal`); offlineRow(); }
    }
    function paint(s) {
      const lib = o.lib || null, c = (lib && lib.counts) || {};
      const goal = s.new_goal || 10, nt = s.new_today || 0;
      const newLeft = Math.max(0, (s.new_goal || 0) - nt);
      const fresh = lib && !c.learning && !c.known && !c.claimed && !c.due && !nt;
      // nothing due today: when the next ones come back (the library's forecast)
      const nextDay = !s.due && lib ? (lib.forecast || []).find(x => x.n > 0 && x.day > lib.today) : null;
      const newFact = nt ? (nt >= goal ? `${nt} new · goal met` : `${nt} of ${goal} new`) : newLeft ? `${newLeft} new` : null;
      // the full card shows the daily new-words goal as a tick meter, so its figure leaves the facts line
      const meterOn = !o.compact && !fresh && !!(s.new_goal || nt) && !!UI.meter;
      const mins = s.minutes ? `about ${Math.max(1, Math.round(s.minutes))} min` : null;
      const debt = lib && lib.debt;
      const startBody = () => ({ mode: 'mix', deck: { source: 'today' }, ...(box ? { box } : {}) });
      // compact (My words): one line and a quiet button, so the page's own primary stays the one orange button
      if (o.compact) {
        const line = h('div', { class: 'tw-line' }, h('h2', { text: 'Today’s words' }),
          h('span', { class: 'tw-facts', text: s.done ? 'Done for today' : [s.due ? `${s.due} due` : null, mins].filter(Boolean).join(' · ') }),
          fresh ? h('button', { type: 'button', class: 'btn', text: 'Find your level · 3 min', onclick: () => startWords({ mode: 'placement' }) })
            : h('button', { type: 'button', class: 'btn', text: s.done ? 'Start again' : 'Start today’s words', onclick: () => startWords(startBody()) }));
        el.classList.add('compact');
        el.replaceChildren(line);
        return;
      }
      // the due count is the figure (the one number the library is about); everything else is one facts line
      const fig = s.due && !s.done && !fresh ? h('p', { class: 'hero-num tw-fig' }, UI.num ? UI.num(s.due) : String(s.due), h('small', { text: 'due today' })) : null;
      const top = h('div', { class: 'tw-top' }, h('h2', { text: 'Today’s words' }));
      const doneEl = s.done ? h('div', { class: 'tw-done' }, UI.spotArt ? h('span', { 'aria-hidden': 'true', html: UI.spotArt('clear') }) : null,
        h('span', { class: 'tw-facts', text: ['Done for today', meterOn ? null : newFact].filter(Boolean).join(' · ') })) : null;
      const factsEl = h('p', { class: 'tw-facts' });
      const setFacts = () => {
        factsEl.textContent = (fresh ? [] : [s.done || s.due ? null : nextDay ? `${nextDay.n} due ${dayName(nextDay.day)}` : null,
          s.done ? null : s.proofs ? `${s.proofs} ${s.proofs === 1 ? 'proof' : 'proofs'}` : null,
          s.done || meterOn ? null : newFact, s.done ? null : mins, box ? `stops at ${box} min` : null]).filter(Boolean).join(' · ');
        factsEl.hidden = !factsEl.textContent;
      };
      setFacts();
      // the ticks learnt since this tab last showed them light in turn (UI.meter animates a change, never a first paint)
      const seen = (() => { try { return JSON.parse(sessionStorage.getItem('satf.words.ticks')); } catch (_) { return null; } })();
      const grew = meterOn && seen && seen.day === today() && nt > seen.n ? seen.n : null;
      try { sessionStorage.setItem('satf.words.ticks', JSON.stringify({ day: today(), n: nt })); } catch (_) {}
      // past the goal it says so plainly ("101 · goal 10" under "New words today"), not "101 of 10"
      const goalText = v => (v > goal ? `${UI.num ? UI.num(v) : v} · goal ${goal}` : null);
      const meter = meterOn ? UI.meter(null, { label: 'New words today', value: grew ?? nt, max: goal, ticks: Math.min(goal, 10), text: goalText(grew ?? nt) }) : null;
      const target = meter ? meter.el : null;
      if (target) {
        target.querySelector('.meter-k').append(' ', UI.why('New words a day is your daily goal, set in Plan. It is never a cap.', { about: 'new words a day' }));
        const bar = target.querySelector('.meter-bar');   // named by its label alone, not the ? inside it
        bar.removeAttribute('aria-labelledby'); bar.setAttribute('aria-label', 'New words today');
      }
      // Make a set: a typed request becomes a custom set on Enter; the field opens from Other ways
      const words = lib && lib.words;
      let find = null, input = null;
      if (words && words.length) {
        input = h('input', { type: 'search', class: 'field sm', 'aria-label': 'Make a set', placeholder: 'Make a set: “10 cards on transitions”, “quiz 5 saved”', autocomplete: 'off', enterkeyhint: 'go' });
        const hint = h('p', { class: 'help tw-find-h', hidden: true, 'data-nofold': '' });
        const plan = () => parseFind(input.value, words);
        input.addEventListener('input', () => {
          const pl_ = plan();
          hint.hidden = !pl_;
          if (pl_) hint.textContent = pl_.none ? `No words match “${pl_.label}”` : `${pl_.mode === 'quiz' ? 'Quiz' : 'Cards'} · ${plural(pl_.count, 'word')} · ${pl_.label}${pl_.n ? ` (${pl_.n} match)` : ''} · Enter to start`;
        });
        input.addEventListener('keydown', e => {
          if (e.key === 'Escape' && !input.value) { find.hidden = true; more.focus(); return; }
          if (e.key !== 'Enter') return;
          e.preventDefault();
          const p_ = plan();
          if (!p_) return;
          if (p_.none) { toast(`No words match “${p_.label}”`); return; }
          if (p_.mode === 'quiz') quizStart(p_.deck, p_.count);
          else startWords({ mode: 'cards', deck: p_.deck, count: p_.count });
        });
        find = h('div', { class: 'tw-find', hidden: true }, input, hint);
      }
      const n = (s.due || 0) + newLeft;
      // a fresh learner has one way in: placement sizes the first words (the user: why is Learn 10 an option here)
      const ways = () => [
        ...(fresh ? [] : [
          { label: 'Review cards', sub: s.due ? `${UI.num ? UI.num(s.due) : s.due} due, as cards` : 'Nothing is due', disabled: !s.due, onClick: () => startWords({ mode: 'cards', deck: { source: 'due' }, order: 'due' }) },
          { label: s.done && !newLeft ? `Learn ${goal} more` : `Learn ${goal}`, sub: 'New words as cards', onClick: () => startWords({ mode: 'cards', deck: { source: 'new' }, count: goal }) },
          { label: 'Quiz', sub: '10 questions on today’s words', onClick: () => quizStart({ source: 'today' }, 10) },
          { separator: true },
          { group: 'Time box' },
          ...[null, 5, 10, 15].map(v => ({ label: v ? `${v} min` : 'No time box', radio: 'box', checked: box === v,
            onClick: () => { box = v; ls.set('satf.words.box', box); setFacts(); } })),
          { separator: true },
          { label: 'Preview today’s words', onClick: () => preview(s, startBody) }]),
        find ? { label: 'Make a set', sub: 'Type what you want: “10 cards on transitions”', onClick: () => { find.hidden = false; input.focus(); } } : null,
        offline.ok() && (kept || n) ? { label: 'Take today’s cards offline', sub: kept ? `${plural(kept.left, 'card')} on this device now` : 'They work with no signal', onClick: takeOffline } : null,
      ];
      // Start and its menu are one split button (A1 .split-btn); a fresh learner with nothing else to offer gets the one button
      const more = h('button', { type: 'button', class: 'pill tw-more', 'aria-label': 'Other ways to practice', title: 'Other ways' }, UI.icon('caret_down', 16));
      UI.menu.bind(more, ways, { align: 'end', label: 'Other ways to practice' });
      const go = fresh ? h('button', { type: 'button', class: 'pill', text: 'Find your level · 3 min', onclick: () => startWords({ mode: 'placement' }) })
        : h('button', { type: 'button', class: 'pill', onclick: () => startWords(startBody()) }, s.done ? 'Start again' : 'Start', h('span', { class: 'kbd', text: 'Enter', hidden: !o.enter }));
      const row = h('div', { class: 'tw-row' }, ways().some(Boolean) ? h('div', { class: 'split-btn', role: 'group', 'aria-label': 'Start today’s words' }, go, more) : go);
      el.replaceChildren(...[top, doneEl, fig, factsEl, target, row, find].filter(Boolean));
      if (meter && grew !== null) ticksGrow(meter, nt, goal, grew, goalText(nt));   // grew is 0 on the day's first words
      if (debt && debt.due) {
        const days = Math.max(2, Math.ceil(debt.due / Math.max(1, debt.spread || 1)));
        el.append(h('p', { class: 'tw-note', 'data-nofold': '' }, h('b', { text: `${debt.due} due` }), debt.away ? ` after ${plural(debt.away, 'day')} away · ` : ' · ',
          h('button', { type: 'button', class: 'quiet', text: `Spread over ${days} days`, onclick: () => spread(days) }), ' · ',
          h('button', { type: 'button', class: 'quiet', text: 'Do all now', onclick: () => startWords({ mode: 'cards', deck: { source: 'due' }, count: Math.min(200, debt.due) }) })));
      }
      // the reason only when it says something the facts above do not ("52 come back today" restates "52 due")
      if (s.reason && !s.done && !fresh && s.due && !new RegExp(`\\b${s.due}\\b`).test(s.reason)) el.append(h('p', { class: 'help', text: s.reason }));
    }
    // the meter moves to today's count once it is on screen; reaching the goal just now draws a check by its label
    function ticksGrow(m, nt, goal, from, text) {
      requestAnimationFrame(() => {
        m.set({ value: nt, text });
        if (from < goal && nt >= goal && UI.fx) { const k = m.el.querySelector('.meter-k'); const c = UI.icon('check', 14); if (k && c) { k.append(' ', c); UI.fx.check(c); } }
      });
    }
    async function spread(days) {
      try { await UI.prefs.set({ words_spread: addDays(today(), days) }); toast(`Spread over ${days} days · new words pause until you catch up`); draw(); if (o.onChange) o.onChange(); }
      catch (e) { if (!e.offline) toast('Not saved. Try again.'); }
    }
    function preview(s, body) {
      const p = s.preview || {};
      const rows = [['Fix cards', p.fix], ['Due reviews', p.due], ['Proofs in context', p.proofs], ['New words', p.new], ['Transitions', p.transitions]].filter(r => r[1]);
      UI.sheet({ title: 'Today’s words', size: 's',
        body: rows.length ? h('div', { class: 'wb' }, rows.map(([k, n]) => h('p', { class: 'line' }, h('b', { text: String(n) }), ` ${k.toLowerCase()}`)),
          h('p', { class: 'help', text: `About ${Math.max(1, Math.round(s.minutes || 1))} min${box ? ` · stops at ${box} min` : ''}. Due words come first, in the format they are ready for.` }))
          : h('p', { text: 'Nothing is waiting. Start adds new words up to your daily goal.' }),
        actions: [{ label: 'Start', primary: true, kbd: 'Enter', onClick: () => { startWords(body()); } }] });
    }
    draw();
    return { el, refresh: draw };
  }

  /* ------------------------------------------------------------ By exam day (W12) */
  function wordsFinish(host, ins, o = {}) {
    const el = h('section', { class: (o.card === false ? '' : 'card ') + 'wfin', 'aria-label': 'By exam day' });   // card false: a row in the page's own surface
    if (host) host.replaceChildren(el);
    const f = (ins && ins.finish) || {};
    if (!f.exam) {
      // no date yet: one line, the title and the way to set it
      const b = h('button', { type: 'button', class: 'btn sm', text: 'Set your SAT date' });
      b.addEventListener('click', () => UI.examDate && UI.examDate(b, { onSave: async v => { await UI.api('/me', { method: 'PUT', body: { exam_date: v } }); if (o.onChange) o.onChange(); } }));
      el.append(h('div', { class: 'tw-top' }, h('h2', { text: 'By exam day' }), b));
      return el;
    }
    const left = f.left || {}, days = dayDiff(today(), f.exam), on = shortDate(f.exam);
    const togo = [left.core ? `SAT core ${UI.num(left.core)}` : null, left.advanced ? `advanced ${UI.num(left.advanced)}` : null, left.logics ? `transitions ${left.logics}` : null].filter(Boolean);
    const studied = (f.likely || 0) + (f.at_risk || 0);
    const headline = f.at_risk ? `${plural(f.at_risk, 'word')} at risk by ${on}` : studied ? `All ${plural(studied, 'studied word')} should hold on ${on}` : `SAT on ${on}`;
    const body = h('div', { class: 'wfin-body' },
      h('p', { class: 'wfin-l' }, h('b', { text: headline }), f.at_risk ? [' ', h('button', { type: 'button', class: 'btn sm', text: 'Review them',
        onclick: () => startWords({ mode: 'cards', deck: { source: 'atrisk' }, count: Math.min(200, f.at_risk) }) })] : null),
      h('p', { class: 'wfin-left', text: [left.core ? null : 'SAT core done', togo.length ? `To learn: ${togo.join(' · ')}` : null].filter(Boolean).join(' · ') }));
    if (o.collapsible) {
      // Library: one line until opened; the open state is remembered
      const det = h('details', { class: 'fold' }, h('summary', { class: 'fold-s' }, h('h2', { text: 'By exam day' }), h('span', { class: 'tw-facts', text: f.at_risk ? `${UI.num(f.at_risk)} at risk` : on })), body);
      det.open = !!ls.get('satf.words.finOpen', false);
      det.addEventListener('toggle', () => ls.set('satf.words.finOpen', det.open));
      el.append(det);
    } else el.append(h('div', { class: 'tw-top' }, h('h2', { text: 'By exam day' })), body);
    if (days <= 10) body.append(h('p', { class: 'help', text: 'Final 10 days · reviews and at-risk words only' }));
    const chips = f.chips || [];
    if (chips.length) {
      const cur = UI.prefs && UI.prefs.now ? UI.prefs.now().words_goal : null;
      const opts = chips.map(c => ({ value: String(c.goal), label: `${c.auto ? 'Auto · ' : ''}${c.goal}`,
        why: [c.core_done ? `core done ${shortDate(c.core_done)}` : 'core not done by the exam', c.load_2w ? `about ${c.load_2w} reviews a day` : null, c.minutes ? `${Math.round(c.minutes)} min` : null].filter(Boolean).join(' · ') }));
      const row = h('div', {}, h('p', { class: 'k', text: 'New words a day' }));
      const line = h('p', { class: 'help' });
      const sel = UI.chips(row, opts, { value: cur === 'auto' ? String((chips.find(c => c.auto) || {}).goal) : String(cur ?? 10), label: 'New words a day',
        onChange: async v => {
          const c = chips.find(x => String(x.goal) === v); line.textContent = (opts.find(x => x.value === v) || {}).why || '';
          try { await UI.prefs.set({ words_goal: c && c.auto ? 'auto' : +v }); toast(`${v} new words a day`); if (o.onChange) o.onChange(); }
          catch (e) { if (!e.offline) toast('Not saved. Try again.'); }
        } });
      line.textContent = (opts.find(x => x.value === sel.value) || {}).why || '';
      row.append(line);
      body.append(row);
    }
    return el;
  }

  /* ------------------------------------------------------------ speak */
  function voice() {
    try { const vs = speechSynthesis.getVoices(); return vs.find(v => /en[-_]US/i.test(v.lang)) || vs.find(v => /^en/i.test(v.lang)) || null; } catch (_) { return null; }
  }
  function speak(text) {
    try { const u = new SpeechSynthesisUtterance(String(text || '')); const v = voice(); if (v) u.voice = v; u.lang = 'en-US'; speechSynthesis.cancel(); speechSynthesis.speak(u); } catch (_) {}
  }
  speak.ok = () => { try { return 'speechSynthesis' in window && speechSynthesis.getVoices().length > 0; } catch (_) { return false; } };
  function speakBtn(word, cls = 'ibtn') {
    const b = h('button', { type: 'button', class: cls, 'aria-label': `Say ${word}`, title: 'Say it (P)', onclick: () => speak(word) }, ic('speak'));
    const upd = () => { b.hidden = !speak.ok(); };
    upd();
    try { speechSynthesis.addEventListener('voiceschanged', upd, { once: true }); } catch (_) {}
    return b;
  }

  /* ------------------------------------------------------------ marked text */
  // "[[word]]" -> the word in wash with an amber underline
  function marked(text, cls = 'ex') {
    const p = h('p', { class: cls });
    String(text || '').split(/(\[\[[^\]]+\]\])/).forEach(part => {
      const m = /^\[\[([^\]]+)\]\]$/.exec(part);
      p.append(m ? h('mark', { text: m[1] }) : doc.createTextNode(part));
    });
    return p;
  }
  // a plain sentence with the word (or its forms) marked
  function markWord(text, forms, cls = 'ex') {
    const p = h('p', { class: cls });
    const list = [...new Set((forms || []).filter(Boolean))].sort((a, b) => b.length - a.length).map(f => f.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    if (!list.length) { p.textContent = text || ''; return p; }
    const re = new RegExp(`\\b(${list.join('|')})\\b`, 'i');
    const m = re.exec(text || '');
    if (!m) { p.textContent = text || ''; return p; }
    p.append(text.slice(0, m.index), h('mark', { text: m[0] }), text.slice(m.index + m[0].length));
    return p;
  }

  /* ------------------------------------------------------------ the word sheet (§4) */
  const COVER_KEY = 'satf.words.cover';
  const word = {};
  let openSheet = null;
  function setW(slug) {
    try { const u = new URL(location.href); if (slug) u.searchParams.set('w', slug); else u.searchParams.delete('w'); history.replaceState(history.state, '', u); } catch (_) {}
  }
  word.open = function open(slug, o = {}) {
    if (openSheet) { openSheet.go(slug, o); return openSheet; }
    const list = o.list || [];
    // covered: the answer-giving blocks are hidden; selftest: the footer grades (W14), through Show and after it
    let cur = slug, data = null, covered = !!o.covered, selftest = covered, shownAt = 0;
    const tools = h('div', { class: 'ws-tools' });
    const foot = h('div', { class: 'sheet-foot ws-foot' });
    const api = UI.sheet({ className: 'wsheet', title: '…', body: b => { b.append(h('p', { class: 'meta', text: 'Loading…' })); },
      onClose: () => { openSheet = null; setW(null); if (keys) keys.unregister(); if (o.onClose) o.onClose(); } });
    const d = api.el;
    const head = d.querySelector('.sheet-head');
    head.insertBefore(tools, head.lastChild);
    d.append(foot);
    let keys = null;
    if (UI.keys && UI.keys.register) {
      keys = UI.keys.register('wordsheet', {
        ArrowLeft: { does: 'Previous word', run: () => step(-1) },
        ArrowRight: { does: 'Next word', run: () => step(1) },
        Space: { does: 'Show the covered blocks', run: () => { if (covered) uncover(); } },
        1: { does: 'Don’t know (covered)', run: () => { if (selftest) grade(false); } },
        2: { does: 'Know (covered)', run: () => { if (selftest) grade(true); } },
        P: { does: 'Say it', run: () => data && speak(data.word) },
        B: { does: 'Save', run: () => data && toggleSave() },
      }, { within: d, label: 'Word sheet' });
    }
    const api2 = { el: d, go, close: () => api.close() };
    openSheet = api2;

    // paging slides the body 12px the way it went (a pointer; keys stay instant), once the next word has painted
    let slide = 0;
    const slideIn = () => {
      if (slide && UI.motion && UI.motion.ok() && api.body.animate) api.body.animate([{ opacity: 0, transform: `translateX(${slide * 12}px)`, offset: 0 }], { duration: 160, easing: 'cubic-bezier(.23, 1, .32, 1)' });
      slide = 0;
    };
    function step(n) {
      if (!list.length) return;
      const i = list.indexOf(cur);
      const j = i < 0 ? 0 : i + n;
      if (j < 0 || j >= list.length) return;
      slide = n;
      go(list[j], { covered: !!o.covered });   // W14: a covered grid pages front-first
    }
    function go(s, oo = {}) {
      cur = s;
      if (oo.covered !== undefined) selftest = covered = oo.covered;
      setW(s);
      load();
    }
    // Show: the face-down blocks wipe open top to bottom (a pointer; Space stays instant)
    function uncover() {
      covered = false; d.classList.remove('covered'); paintFoot();
      if (UI.motion && UI.motion.ok()) d.querySelectorAll('.cov > :not(.k)').forEach(x => x.animate && x.animate([{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }], { duration: 200, easing: 'cubic-bezier(.23, 1, .32, 1)' }));
    }
    async function load() {
      api.body.replaceChildren(h('p', { class: 'meta', text: 'Loading…' }));
      foot.replaceChildren();
      tools.replaceChildren();
      d.classList.toggle('covered', covered);
      // a slug the index does not hold: a typed word finds its entry, else the message, with no request
      if (!/^(u:|root:)/.test(cur)) {
        const ix = await index().catch(() => null);
        if (ix && !ix.bySlug.has(cur)) {
          const hit = ix.byWord.get(cur.toLowerCase());
          if (!hit) { data = null; api.setTitle('Words'); api.body.replaceChildren(h('p', { class: 'wmsg', text: `No word called “${cur}”.` })); return; }
          cur = hit.slug; setW(cur);
        }
      }
      const path = cur.startsWith('root:') ? `/words/root/${encodeURIComponent(cur.slice(5))}` : `/words/${encodeURIComponent(cur)}`;
      try { data = await UI.api(path, { quiet: true }); }
      catch (e) {
        data = null;
        api.setTitle('Words');
        api.body.replaceChildren(h('p', { class: 'wmsg', text: e.status === 404 ? `No word called “${cur.replace(/^root:/, '')}”.` : 'This word did not load.' }),
          e.status === 404 ? null : h('button', { type: 'button', class: 'btn', text: 'Retry', onclick: load }));
        return;
      }
      shownAt = performance.now();
      if (cur.startsWith('root:')) return paintRoot();
      paint();
    }
    function toolsRow() {
      const saved = !!(data.state && data.state.saved);
      const star = h('button', { type: 'button', class: 'ibtn', 'aria-pressed': String(saved), 'aria-label': saved ? 'Saved' : 'Save', title: 'Save (B)', onclick: toggleSave }, ic('star'));
      const i = list.indexOf(cur);
      tools.replaceChildren(...[speakBtn(data.word), star,
        h('button', { type: 'button', class: 'ibtn', 'aria-label': 'Report a problem with this word', title: 'Report',
          onclick: () => UI.report && UI.report({ kind: 'word', source: 'words', word: data.slug, meaning: data.meaning }) }, ic('flag')),
        ...(list.length > 1 ? [h('button', { type: 'button', class: 'ibtn', 'aria-label': 'Previous word', title: 'Previous (←)', disabled: i <= 0, onclick: () => step(-1) }, ic('left')),
          h('button', { type: 'button', class: 'ibtn', 'aria-label': 'Next word', title: 'Next (→)', disabled: i < 0 || i >= list.length - 1, onclick: () => step(1) }, ic('right'))] : [])]);
    }
    async function toggleSave() {
      if (!data || !data.slug) return;
      const on = !(data.state && data.state.saved);
      try { await UI.api(`/words/${encodeURIComponent(data.slug)}/save`, { method: 'POST', body: { on } }); data.state = { ...(data.state || {}), saved: on ? 1 : 0 }; toolsRow(); toast(on ? `Saved · ${data.word} goes to the front of New` : 'Removed from Saved'); if (o.onChange) o.onChange(data.slug, { saved: on }); }
      catch (e) { if (!e.offline) toast('Not saved. Try again.'); }
    }
    const block = (k, kids, o2 = {}) => h('section', { class: 'wb' + (o2.cover ? ' cov' : '') + (o2.cls ? ' ' + o2.cls : '') }, h('span', { class: 'k', text: k }), kids);
    function wordChip(w, o2 = {}) {
      const text = typeof w === 'string' ? w : w.word;
      const slug = typeof w === 'string' ? null : w.slug;
      if (!slug) return h('span', { class: 'wchip plain', text });
      return h('button', { type: 'button', class: 'wchip', 'aria-current': o2.current ? 'true' : null, onclick: () => go(slug, { covered: false }) }, text, o2.small ? h('small', { text: o2.small }) : null);
    }
    async function resolveWords(arr) {
      let ix = null;
      try { ix = await index(); } catch (_) {}
      return (arr || []).map(x => {
        if (x && typeof x === 'object') return x;
        const hit = ix && (ix.bySlug.get(x) || ix.byWord.get(String(x).toLowerCase()));
        return hit ? { slug: hit.slug, word: hit.word } : String(x);
      });
    }
    async function paint() {
      const w = data, s = w.state || {}, own = !!w.own;
      api.setTitle(w.word);
      toolsRow();
      const body = [];
      // one meta line: part of speech, other forms, its tags, the level; Covered / Open at its end
      const lv = level(w.measured, w.level);
      body.push(h('div', { class: 'ws-sub' }, w.pos ? h('span', { text: POS[w.pos] || w.pos }) : null,
        (w.also || []).length ? h('span', { text: `also: ${w.also.join(', ')}` }) : null,
        w.sense && w.sense !== 'main' && w.sense !== '' ? h('span', { class: 'badge soft', text: w.sense.replace(/_/g, ' ') }) : null,
        own ? h('span', { class: 'badge soft', text: 'My word' }) : null,
        w.collection ? h('span', { class: 'badge soft', text: collName(w.collection) }) : null,
        (w.lists || []).map(l => h('span', { class: 'badge soft', text: collName(l) })),
        (w.subjects || []).map(t => h('span', { class: 'badge soft', text: cap(t) })),
        !own ? h('span', { class: 'ws-lv' }, dbars(lv.tier), lv.text ? h('span', { text: lv.text }) : null) : null,
        w.corrected ? h('span', { text: `Corrected ${shortDate(w.corrected)} after a student report` }) : null,
        coverSeg()));
      body.push(block('Meaning', h('p', { class: 'meaning', text: w.meaning || '' }), { cover: true }));
      // shades (W3)
      const sh = w.shades && w.shades.words || [];
      if (sh.length > 1) {
        // one row, weakest -> strongest; the tone shows on each chip only when the class mixes tones
        const mixed = new Set(sh.map(x => Math.sign(x.polarity || 0))).size > 1;
        const tone = x => ({ 1: '+', 0: '0', '-1': '−' })[Math.sign(x.polarity || 0)];
        const shades = block(`Shades · ${w.shades.dimension || 'weakest → strongest'}`, [
          h('div', { class: 'wchips', 'aria-label': 'Weakest to strongest' }, sh.map(x => wordChip({ slug: x.slug, word: x.word }, { current: x.slug === w.slug, small: mixed ? tone(x) : null }))),
          h('div', { class: 'shade-bar', 'aria-hidden': 'true' }),
          w.shade ? h('p', { class: 'shade-n', text: w.shade }) : null], { cover: true, cls: 'shades' });
        shades.querySelector('.k').append(' ', UI.why(`Weakest → strongest${mixed ? ' · + approving, 0 neutral, − critical' : ''}. The most precise word matches the text’s strength and tone.`, { about: 'shades' }));
        body.push(shades);
      }
      // built from (W4)
      if ((w.roots || []).length) {
        body.push(block('Built from', h('div', { class: 'wchips' }, w.roots.map(r => h('button', { type: 'button', class: 'wchip', onclick: () => go('root:' + r.id, { covered: false }) },
          (r.forms || [r.id])[0], h('small', { class: 'cov-t', text: r.meaning || '' })))), {}));
        const g = w.roots.find(r => r.gloss);
        if (g) body[body.length - 1].append(h('p', { class: 'help cov-t', text: `${g.split || ''} · ${g.gloss}` }));
      }
      if ((w.uses || []).length) body.push(block('How the SAT uses it', w.uses.map(u => h('p', { class: 'line', text: `In answer choices: “${u}”` }))));
      (w.other_senses || []).forEach(os => body.push(h('p', { class: 'line wb' }, 'Other meaning · ', wordChip({ slug: os.slug, word: os.short || os.word || os.slug }), os.status ? ` · ${STATUS[os.status] || os.status}` : '')));
      // examples
      const ex = (w.examples || []).map(e => marked(e));
      if (ex.length || w.partners) body.push(block(own ? 'Example' : 'Examples', [ex, w.partners ? h('p', { class: 'line', text: `Common partners: ${w.partners}` }) : null], { cover: true }));
      // same / opposite
      const same = await resolveWords(w.same), opp = await resolveWords(w.opposite);
      if (same.length || opp.length || w.no_opposite) {
        body.push(block('Same as · opposite of', [
          same.length ? h('div', { class: 'wchips' }, h('span', { class: 'meta', text: '=' }), same.map(x => wordChip(x))) : null,
          opp.length ? h('div', { class: 'wchips' }, h('span', { class: 'meta', text: '≠' }), opp.map(x => wordChip(x)))
            : w.no_opposite ? h('p', { class: 'help', text: 'No single-word opposite' }) : null], { cover: true }));
      }
      // not the same as
      const conf = w.confusions || [];
      const seen = new Set(conf.map(c => String(c.other).toLowerCase()));
      const looks = (w.lookalikes || []).filter(l => !seen.has(String(l.word).toLowerCase()));
      if (conf.length || looks.length) {
        const ix = await index().catch(() => null);
        const rows = conf.map(c => confRow(c.kind, c.other, c.tell, c, ix)).concat(looks.map(l => confRow('lookalike', l.word, l.tell, {}, ix)));
        body.push(block('Easy to mix up', rows));
      }
      // the sample (W1), after what the word means and what it is not
      if (w.sample && w.sample.item) body.push(sampleBlock(w));
      body.push(recordBlock(w, s));
      if (own) body.push(ownBlock(w));
      api.body.replaceChildren(...body.filter(Boolean));
      d.classList.toggle('covered', covered);
      paintFoot();
      slideIn();
      if (UI.gloss) api.body.querySelectorAll('.wb .ex').forEach(p => UI.gloss(p, { exclude: [w.word], ref: 'sheet' }));
    }
    // W14: Covered · Open, remembered per browser
    function coverSeg() {
      const host = h('span', { class: 'ws-mode' });
      UI.seg(host, [{ value: 'covered', label: 'Covered' }, { value: 'open', label: 'Open' }], { value: covered ? 'covered' : 'open', label: 'Sheet view',
        onChange: v => { selftest = covered = v === 'covered'; ls.set(COVER_KEY, v); d.classList.toggle('covered', covered); paintFoot(); } });
      return host;
    }
    function collName(id) { return (UI.word._coll && UI.word._coll[id]) || cap(String(id).replace(/-/g, ' ')); }
    function confRow(kind, other, tell, c, ix) {
      const hit = ix && ix.byWord.get(String(other).toLowerCase());
      const me = data.word;
      return h('div', { class: 'confu' },
        h('h3', {}, `${me} or `, hit ? h('button', { type: 'button', class: 'quiet wlink', onclick: () => go(hit.slug, { covered: false }) }, other) : other, '?'),
        h('p', { class: 't cov-t', text: tell || '' }),
        c.fell ? h('p', { class: 'fell' }, h('span', { class: 'dot' }), `You picked it for this ${c.fell}×${c.last ? ' · last ' + shortDate(c.last) : ''}`) : null,
        hit ? h('div', { class: 'acts' }, h('button', { type: 'button', class: 'quiet', text: `Quiz ${me} vs ${other} (6)`,
          onclick: () => startWords({ mode: 'quiz', deck: { source: 'words', words: [data.slug, hit.slug] }, formats: ['meaning2word', 'word2meaning'], count: 6 }) })) : null);
    }
    function sampleBlock(w) {
      const host = h('div', { class: 'wsample' });
      const sec = block(`SAT-style · ${kindLabel(w.sample.item)}`, host);
      let token = w.sample.token;
      const mount = async item => {
        host.replaceChildren(h('p', { class: 'meta', text: 'Loading…' }));
        try { if (!UI.workspace) await UI.need('question'); } catch (_) { host.replaceChildren(h('p', { class: 'help', text: 'Could not load the question.' })); return; }
        const q = { id: item.item_id, type: 'mcq', stem: item.text || '', choices: item.choices || [], latex: [] };
        host.replaceChildren();
        sec.querySelector('.k').textContent = `SAT-style · ${kindLabel(item)}`;
        const ws = UI.workspace(host, q, { mode: 'quiz', head: false,
          onCheck: async (answer, meta) => {
            const r = await UI.api('/words/sample/answer', { method: 'POST', body: { token, answer, ms: meta && meta.ms, conf: meta && meta.conf === 'guess' ? 'guess' : undefined } });
            if (o.onChange) o.onChange(w.slug, { graded: true });
            return verdict(r, answer);
          },
          actions: (slot) => slot.append(h('button', { type: 'button', class: 'btn sm', onclick: another }, UI.VERBS ? 'Twin' : 'Another', h('span', { class: 'meta', text: ' same word, new text' }))) });
        const stem = ws.el.querySelector('.q-stem');
        if (stem && stemOf(item)) stem.after(h('p', { class: 'ws-ask', text: stemOf(item) }));
        if (item.source && stem) stem.after(h('p', { class: 'src', text: `Adapted from ${item.source.author}, ${item.source.title}, ${item.source.year}` }));
      };
      async function another() {
        try { const r = await UI.api('/words/sample', { method: 'POST', body: { slug: w.slug, like: 'word' } }); token = r.token; mount(r.item); }
        catch (e) { if (!e.offline) toast(e.status === 409 ? 'No other text for this word yet.' : 'Couldn’t load another.'); }
      }
      mount(w.sample.item);
      return sec;
    }
    function recordBlock(w, s) {
      const st = status({ state: s, proven: s.proven, placed: s.placed });
      const bk = w.record && w.record.reviews && w.record.reviews.by_kind || {};
      const rightIn = ks => ks.some(k => bk[k] && bk[k].right > 0);
      const steps = [['Seen', !!s.first], ['Recalled', (s.box || 0) >= 2], ['Picked', rightIn(['meaning2word', 'word2meaning', 'cloze'])],
        ['In context', rightIn(['incontext', 'nearly', 'precise', 'transition'])], ['Known', (s.box || 0) >= 4]];
      const r = (w.record && w.record.reviews) || { n: 0, right: 0 };
      const byKind = Object.entries(bk).map(([k, v]) => `${KIND[k] || k} ${v.right}/${v.n}`).join(' · ');
      const j = w.journey || [];
      const lastWrong = [...j].reverse().find(x => x.correct === 0 || x.correct === false);
      const next = s.due ? (s.due <= today() ? 'due today' : `next review ${dayName(s.due, { plain: true })}`) : null;
      const kids = [
        h('p', { class: 'line' }, h('b', { text: STATUS[st] }), next ? ` · ${next}` : '', s.proven ? ` · proven ${shortDate(s.proven)}` : ''),
        h('div', { class: 'ladder', role: 'list', 'aria-label': 'Proof ladder' }, steps.map(([t, on]) => h('span', { role: 'listitem', class: on ? 'on' : null, 'aria-label': `${t}${on ? ', done' : ''}`, text: t }))),
        j.length ? h('div', { class: 'journey', role: 'img', 'aria-label': `${j.length} reviews, ${j.filter(x => x.correct).length} right` },
          j.map(x => { const i = h('i', { class: (x.correct ? 'ok' : '') + (CONTEXT_KINDS.has(x.kind) ? ' ctx' : '') }); if (UI.tooltip) UI.tooltip(i, `${shortDate(x.at)} · ${KIND[x.kind] || x.kind} · ${x.correct ? 'right' : x.correct === null ? 'seen' : 'wrong'}${x.given && !x.correct ? ` · picked “${x.given}”` : ''}${x.trap ? ` · ${TRAP[x.trap] || x.trap}` : ''}`); return i; }),
          s.due ? h('span', { class: 'nx', text: `next ${shortDate(s.due)}` }) : null) : null,
        lastWrong && lastWrong.given && !['dontknow', 'know'].includes(lastWrong.given) ? h('p', { class: 'line', text: `Last time you picked “${lastWrong.given}”` }) : null,
      ];
      // the counts behind the record, one tap away
      const more = [r.n ? `Reviews ${r.n} · right ${r.right}${byKind ? ' · ' + byKind : ''}` : null, s.first ? `First seen ${shortDate(s.first)}` : null,
        w.record && w.record.lookups ? `Looked up ${w.record.lookups}× in Words texts` : null].filter(Boolean);
      if (more.length) kids.push(h('details', { class: 'fold' }, h('summary', { class: 'fold-s', text: 'Reviews and history' }), more.map(t => h('p', { class: 'help', text: t }))));
      if (!w.own) kids.push(hookRow(w, s));
      return block('Your record', kids, { cls: 'record journey-wrap' });
    }
    function hookRow(w, s) {
      const inp = h('input', { class: 'field sm', maxlength: '140', placeholder: 'My hook: a memory aid in your own words', 'aria-label': 'My hook', value: s.hook || '' });
      const save = h('button', { type: 'button', class: 'btn', text: 'Save hook', onclick: async () => {
        try { await UI.api(`/words/${encodeURIComponent(w.slug)}/hook`, { method: 'PUT', body: { text: inp.value.trim() } }); toast(inp.value.trim() ? 'Hook saved · it shows on every card back' : 'Hook removed'); }
        catch (e) { if (!e.offline) toast(e.status === 422 ? cap(e.message) : 'Not saved. Try again.'); }
      } });
      inp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); save.click(); } });
      return h('div', { class: 'hook' }, inp, save);
    }
    function ownBlock(w) {
      return block('My word', [w.notes ? h('p', { class: 'line', text: w.notes }) : null, w.source ? h('p', { class: 'help', text: w.source }) : null,
        h('div', { class: 'acts' },
          h('button', { type: 'button', class: 'btn sm', text: 'Edit', onclick: () => { api.close(); addWord({ id: w.slug, word: w.word, meaning: w.meaning, pos: w.pos, example: (w.examples || [])[0], same: w.same, opposite: w.opposite, notes: w.notes, list: w.collection }); } }),
          h('button', { type: 'button', class: 'btn sm', text: 'Delete', onclick: async () => {
            if (!await UI.confirm({ title: `Delete “${w.word}”?`, text: `Delete “${w.word}” and its review history?`, confirm: 'Delete', destructive: true })) return;
            try { await UI.api(`/words/mine/${encodeURIComponent(w.slug)}`, { method: 'DELETE' }); toast(`Deleted “${w.word}”`); api.close(); if (o.onChange) o.onChange(w.slug, { deleted: true }); }
            catch (e) { if (!e.offline) toast('Not deleted. Try again.'); }
          } }))]);
    }
    function paintFoot() {
      if (!data || !data.slug) { foot.replaceChildren(); return; }
      const w = data;
      if (selftest) {
        foot.replaceChildren(...[covered ? h('button', { type: 'button', class: 'btn sm', onclick: uncover }, 'Show', h('span', { class: 'kbd', text: 'Space' })) : null, h('span', { class: 'grow' }),
          h('button', { type: 'button', class: 'btn sm', onclick: () => grade(false) }, 'Don’t know', h('span', { class: 'kbd', text: '1' })),
          h('button', { type: 'button', class: 'pill sm', onclick: () => grade(true) }, 'Know', h('span', { class: 'kbd', text: '2' }))].filter(Boolean));
        return;
      }
      const lookalikes = (w.confusions || []).map(c => c.other).concat((w.lookalikes || []).map(l => l.word));
      const quizLooks = async () => {
        const ix = await index().catch(() => null);
        const slugs = [w.slug, ...lookalikes.map(x => ix && ix.byWord.get(String(x).toLowerCase())).filter(Boolean).map(x => x.slug)];
        quizStart({ source: 'words', words: [...new Set(slugs)] }, 6);
      };
      const more = h('button', { type: 'button', class: 'ibtn', 'aria-label': 'More', 'aria-haspopup': 'menu' }, ic('more'));
      more.addEventListener('click', () => UI.menu(more, [lookalikes.length ? { label: 'Quiz with lookalikes', onClick: quizLooks } : null,
        { label: 'Reset progress', onClick: resetProgress }].filter(Boolean), { align: 'end' }));
      const primary = w.sample && !w.own;
      const cardsHere = h('button', { type: 'button', class: primary ? 'btn sm' : 'pill sm',
        onclick: () => {
          // the list from this word on, wrapping round, so the deck always holds it
          const i = list.indexOf(w.slug);
          const from = i < 0 ? [w.slug, ...list] : [...list.slice(i), ...list.slice(0, i)];
          startWords({ mode: 'cards', deck: { source: 'words', words: from.slice(0, 200), start: w.slug }, order: 'az', count: Math.min(200, from.length) });
        } }, h('span', {}, 'Flashcards', h('span', { class: 'l', text: ' from here' })));
      foot.replaceChildren(...[
        primary ? h('button', { type: 'button', class: 'pill sm', title: 'Ten in-context questions on this word, each a new text', onclick: () => practise10(w) }, h('span', {}, 'Practice 10', h('span', { class: 'l', text: ' like this' }))) : null,
        cardsHere, h('span', { class: 'grow' }), more].filter(Boolean));
    }
    const practise10 = w => startWords({ mode: 'quiz', deck: { source: 'words', words: [w.slug] }, formats: ['incontext', 'nearly'], count: 10 });
    async function resetProgress() {
      if (!await UI.confirm({ title: `Reset “${data.word}”?`, text: 'Its box, due date and saved star go back to new. Its review history stays.', confirm: 'Reset', destructive: true })) return;
      try { await UI.api('/words/reset', { method: 'POST', body: { words: [data.slug] } }); toast('Progress reset'); load(); if (o.onChange) o.onChange(data.slug, { reset: true }); }
      catch (e) { if (!e.offline) toast('Not reset. Try again.'); }
    }
    async function grade(ok) {
      if (!data) return;
      const slug = data.slug;
      try {
        const r = await UI.api(`/words/${encodeURIComponent(slug)}/grade`, { method: 'POST', body: { ok, ms: Math.round(performance.now() - shownAt) } });
        toast(`${ok ? 'Know' : 'Don’t know'} · ${statusLine(r.status_line || r.status)}`);
        if (o.onChange) o.onChange(slug, { graded: true, box: r.box });
      } catch (e) { if (!e.offline) toast('Not saved. Try again.'); return; }
      const i = list.indexOf(slug);
      if (i >= 0 && i < list.length - 1) { slide = 1; go(list[i + 1], { covered: true }); } else load();
    }
    function paintRoot() {
      const r = data;
      api.setTitle((r.forms || [r.id]).join(' · '));
      tools.replaceChildren();
      const fam = r.words || [];
      api.body.replaceChildren(...[
        h('p', { class: 'ws-sub' }, h('span', { text: cap(r.kind || 'root') }), r.origin ? h('span', { text: r.origin }) : null),
        block('Meaning', h('p', { class: 'meaning', text: r.meaning || '' })),
        r.false_friend ? block('False friend', h('p', { class: 'line', text: r.false_friend })) : null,
        block(`Family · ${fam.length}`, [h('div', { class: 'wchips' }, fam.map(x => h('button', { type: 'button', class: 'wchip', onclick: () => go(x.slug, { covered: false }) },
          pips({ state: { box: x.box } }), x.word, h('small', { text: x.split || '' })))),
          fam.some(x => x.gloss) ? fam.filter(x => x.gloss).map(x => h('p', { class: 'line', text: `${x.split} · ${x.gloss}` })) : null]),
        h('p', { class: 'line wb', text: `Knowing “${(r.forms || [r.id])[0].replace(/-/g, '')}” helps with ${plural(r.total ?? fam.length, 'word')}${r.known ? ` (${r.known} known)` : ''}.` })].filter(Boolean));
      if (fam.length) foot.replaceChildren( h('button', { type: 'button', class: 'pill sm', text: `Flashcards · ${fam.length}`, onclick: () => startWords({ mode: 'cards', deck: { source: 'root', value: r.id }, count: fam.length }) }));
    }
    setW(cur);
    load();
    return api2;
  };
  word.status = status;
  word.STATUS = STATUS;
  word.level = level;
  word.pips = pips;
  word.label = label;
  word.index = index;
  word.statusLine = statusLine;
  word.dayName = dayName;
  word.shortDate = shortDate;
  word.POS = POS;
  word.TRAP = TRAP;
  word.KIND = KIND;
  word.CHECK = CHECK;
  word.verdict = verdict;
  word.marked = marked;
  word.markWord = markWord;
  word.speakBtn = speakBtn;
  word.icon = ic;
  word.quizStart = quizStart;
  word.nameOf = nameOf;
  word.kindLabel = kindLabel;
  word.stemOf = stemOf;
  word.today = today;
  word.dayDiff = dayDiff;
  word.coverPref = () => ls.get(COVER_KEY, null);
  word._coll = {};

  /* ------------------------------------------------------------ the Add sheet (§10) */
  function addWord(pre = {}) {
    const editing = !!pre.id;
    const f = {};
    const field = (k, lab, el, o2 = {}) => { f[k] = el; const err = h('p', { class: 'field-err', hidden: true }); f[k + 'Err'] = err;
      return h('div', {}, h('label', { class: 'label', for: el.id = 'aw-' + k, text: lab + (o2.req ? ' *' : '') }), el, err); };
    const lists = [...new Set(['My words', ...(UI.word._lists || [])])];
    const dl = h('datalist', { id: 'aw-lists' }, lists.map(l => h('option', { value: l })));
    const msg = h('div', { class: 'dup', 'aria-live': 'polite' });
    const body = h('div', { class: 'addw' },
      field('word', 'Word', h('input', { class: 'field', maxlength: '60', value: pre.word || '', autocomplete: 'off' }), { req: true }),
      field('meaning', 'Meaning', h('textarea', { class: 'field', rows: '3', maxlength: '400' }, pre.meaning || ''), { req: true }),
      h('div', { class: 'two' },
        field('pos', 'Part of speech', h('select', { class: 'field' }, ['', 'n.', 'v.', 'adj.', 'adv.', 'phrase'].map(p => h('option', { value: p, selected: (pre.pos || '') === p ? true : null, text: p ? POS[p] : '\u2013' })))),
        field('list', 'List', h('input', { class: 'field', maxlength: '30', list: 'aw-lists', value: pre.list || 'My words' }))),
      field('example', 'Example', h('input', { class: 'field', maxlength: '300', value: pre.example || '' })),
      h('div', { class: 'two' },
        field('same', 'Same as', h('input', { class: 'field', placeholder: 'comma list', value: [].concat(pre.same || []).join(', ') })),
        field('opposite', 'Opposite of', h('input', { class: 'field', placeholder: 'comma list', value: [].concat(pre.opposite || []).join(', ') }))),
      field('notes', 'Notes', h('textarea', { class: 'field', rows: '2', maxlength: '1000' }, pre.notes || '')),
      pre.source ? h('p', { class: 'help', text: pre.source }) : null, dl, msg);
    const commas = s => String(s || '').split(',').map(x => x.trim()).filter(Boolean).slice(0, 10);
    async function save(again) {
      ['word', 'meaning'].forEach(k => { f[k + 'Err'].hidden = true; });
      msg.replaceChildren();
      const b = { word: f.word.value.trim(), meaning: f.meaning.value.trim(), pos: f.pos.value || null, example: f.example.value.trim() || null,
        same: commas(f.same.value), opposite: commas(f.opposite.value), notes: f.notes.value.trim() || null, list: f.list.value.trim() || 'My words', source: pre.source || null };
      let bad = false;
      if (!b.word) { f.wordErr.textContent = 'Add the word'; f.wordErr.hidden = false; bad = true; }
      if (!b.meaning) { f.meaningErr.textContent = 'Add what it means'; f.meaningErr.hidden = false; bad = true; }
      if (bad) return false;
      // the button says Adding, then Added (Saving, Saved when editing); a duplicate or a library word is "Not added"
      const NOT = {};
      const send = async () => {
        let r;
        try { r = await UI.api(editing ? `/words/mine/${encodeURIComponent(pre.id)}` : '/words/mine', { method: editing ? 'PUT' : 'POST', body: b }); }
        catch (e) {
          if (e.status === 409) {
            const id = e.detail && e.detail.existing_id;
            msg.append(`You already have “${b.word}”. `, id ? h('button', { type: 'button', class: 'quiet', text: 'Edit it', onclick: () => { sh.close(); word.open(id); } }) : null);
            throw NOT;
          }
          throw new Error(e.status === 400 || e.status === 422 ? cap(e.message) : 'Not saved. Try again.');
        }
        if (r && r.library_slug && !r.id) {
          msg.append(`“${b.word}” is in the library. `, h('button', { type: 'button', class: 'btn sm', text: 'Save that one', onclick: async () => {
            try { await UI.api(`/words/${encodeURIComponent(r.library_slug)}/save`, { method: 'POST', body: { on: true } }); toast(`Saved “${b.word}” from the library`); sh.close(); dispatch(); }
            catch (e) { if (!e.offline) toast('Not saved. Try again.'); }
          } }));
          throw NOT;
        }
        return r;
      };
      const btn = sh.foot && sh.foot.querySelector(again ? '.aw-again' : '.aw-save');
      try { await (btn && UI.saving ? UI.saving(btn, send, editing ? {} : { busy: 'Adding', done: 'Added', fail: 'Not added' }) : send()); }
      catch (e) { if (e === NOT) return false; throw e; }
      dispatch();
      // add another: the button's Added is the confirmation; Save closes the sheet, so a toast says it
      if (again) { f.word.value = ''; f.meaning.value = ''; f.example.value = ''; f.same.value = ''; f.opposite.value = ''; f.notes.value = ''; f.word.focus(); return false; }
      toast(editing ? `Saved “${b.word}”` : `Added “${b.word}” to ${b.list}`);
      return true;
    }
    const dispatch = () => { try { doc.dispatchEvent(new CustomEvent('satf:words', { detail: { added: true } })); } catch (_) {} };
    const sh = UI.sheet({ title: editing ? `Edit “${pre.word}”` : 'Add a word', size: 'm', body,
      actions: [{ label: 'Cancel', quiet: true }, ...(editing ? [] : [{ label: 'Save and add another', className: 'aw-again', onClick: () => save(true) }]), { label: 'Save', primary: true, className: 'aw-save', onClick: () => save(false) }] });
    setTimeout(() => (pre.word ? f.meaning : f.word).focus(), 30);
    return sh;
  }

  /* ------------------------------------------------------------ Add a selection (§1) */
  function addWordFromSelection(root, o = {}) {
    if (!root || /^\/test(\/|$)/.test(location.pathname)) return () => {};   // never in the test window
    let open = null;
    const check = () => setTimeout(() => {
      const sel = getSelection();
      const text = sel && sel.rangeCount && !sel.isCollapsed ? sel.toString().replace(/\s+/g, ' ').trim().replace(/^[^\p{L}]+|[^\p{L}]+$/gu, '') : '';
      if (!text || text.split(' ').length > 6 || !root.contains(sel.anchorNode) || !root.contains(sel.focusNode)) return;
      if (open) open.close();
      const src = typeof o.source === 'function' ? o.source() : o.source;
      const day = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      const res = open = UI.pop(sel.getRangeAt(0).cloneRange(), h('button', { type: 'button', class: 'btn sm primary', text: 'Add to my words',
        onclick: () => { res.close(); addWord({ word: text, source: `${src || 'From a question'} · ${day}` }); } }),
        { label: 'Add to my words', anchored: true, focus: false, onClose: () => { if (open === res) open = null; } });
    }, 0);
    const evs = ['mouseup', 'keyup', 'touchend'];
    evs.forEach(e => root.addEventListener(e, check));
    return () => { evs.forEach(e => root.removeEventListener(e, check)); if (open) open.close(); };
  }

  /* ------------------------------------------------------------ tap-to-define (§11) */
  const looked = new Set();
  let reCache = null;
  async function gloss(el, o = {}) {
    if (!el || (UI.prefs && UI.prefs.now && UI.prefs.now().gloss === false)) return;
    let ix;
    try { ix = await index(); } catch (_) { return; }
    if (!reCache) {
      const forms = [];
      ix.words.forEach(w => [w.word, ...(w.also || [])].forEach(f => { if (f && f.length > 3) forms.push([f.toLowerCase(), w]); }));
      forms.sort((a, b) => b[0].length - a[0].length);
      const map = new Map(forms);
      reCache = { map, re: new RegExp(`\\b(${[...map.keys()].map(x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`, 'gi') };
    }
    const skip = new Set((o.exclude || []).map(x => String(x).toLowerCase()));
    const used = new Set();
    let n = 0;
    const walker = doc.createTreeWalker(el, NodeFilter.SHOW_TEXT, { acceptNode: t => t.parentElement && t.parentElement.closest('.opts, button, mark, .blank, input, textarea') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const t of nodes) {
      if (n >= 3) break;
      const text = t.nodeValue;
      reCache.re.lastIndex = 0;
      let m, done = false;
      while (!done && n < 3 && (m = reCache.re.exec(text))) {
        const w = reCache.map.get(m[0].toLowerCase());
        if (!w || used.has(w.slug) || skip.has(w.word.toLowerCase()) || skip.has(m[0].toLowerCase())) continue;
        used.add(w.slug); n++;
        const after = t.splitText(m.index);
        after.nodeValue = after.nodeValue.slice(m[0].length);
        const b = h('button', { type: 'button', class: 'term', text: m[0], 'aria-haspopup': 'dialog', onclick: () => pop(b, w, o) });
        t.after(b);
        done = true;   // the rest of this node is in `after`; later matches are found on the next pass
        nodes.splice(nodes.indexOf(t) + 1, 0, after);
      }
    }
  }
  function pop(anchor, w, o) {
    if (!looked.has(w.slug)) {
      looked.add(w.slug);
      UI.api('/words/lookup', { method: 'POST', body: { slug: w.slug, where: 'words', ref: o.ref || location.pathname }, quiet: true }).catch(() => {});
    }
    const content = h('div', { class: 'gpop' }, h('b', { text: w.word }), h('p', { text: w.short || '' }),
      h('div', { class: 'acts' }, speakBtn(w.word, 'btn sm'),
        h('button', { type: 'button', class: 'btn sm', text: 'Save', onclick: async e => { try { await UI.api(`/words/${encodeURIComponent(w.slug)}/save`, { method: 'POST', body: { on: true } }); e.target.textContent = 'Saved'; } catch (_) {} } }),
        o.open === false ? null : h('button', { type: 'button', class: 'btn sm', text: 'Open', onclick: () => { p.close(); word.open(w.slug); } })));
    const p = UI.pop(anchor, content, { label: w.word });
    return p;
  }

  /* ------------------------------------------------------------ Bring words (W19): a text, a word list, a missed question */
  let libP = null;
  const libRows = () => (libP = libP || UI.api('/words', { quiet: true }).then(d => new Map((d.words || []).map(w => [w.slug, w])))).catch(e => { libP = null; throw e; });
  const dayLabel = () => shortDate(today());
  async function saveList(name, slugs) {
    try { await UI.api('/words/lists', { method: 'POST', body: { name: name.slice(0, 30), words: slugs } }); toast(`Saved “${name.slice(0, 30)}” · ${plural(slugs.length, 'word')}`, { action: { label: 'Study them', onClick: () => startWords({ mode: 'cards', deck: { source: 'words', words: slugs.slice(0, 200) } }) } }); return true; }
    catch (e) { if (!e.offline) toast(e.status === 409 ? 'You already have a list with that name.' : cap(e.message || 'Not saved.')); return false; }
  }
  function bringWords(kind = 'text') {
    if (kind === 'list') return bringList();
    if (kind === 'missed') return bringMissed();
    if (kind === 'import') return bringImport();
    return bringText();
  }
  // Import a file or a paste (W19): word and meaning per line become own words; a word alone matched in the
  // library joins the list. Duplicates and lines it cannot read are named before anything is sent.
  function bringImport() {
    const fmt = n => (UI.num ? UI.num(n) : String(n));
    const ta = h('textarea', { class: 'field', rows: '8', placeholder: 'One per line: the word, then a tab, a hyphen or a colon, then the meaning' });
    const list = h('input', { class: 'field sm', value: 'My words', maxlength: '30', 'aria-label': 'List', list: 'imp-lists' });
    const dl = h('datalist', { id: 'imp-lists' }, [...new Set(['My words', ...(word._lists || [])])].map(n => h('option', { value: n })));
    const prev = h('div', { 'aria-live': 'polite' });
    const show = (...kids) => prev.replaceChildren(...kids.flat().filter(Boolean));
    const LABEL = { new: 'new', dup: 'duplicate', lib: 'in the library', bad: 'not understood' };
    let ix = null, rows = [], done = false, sh = null, all = [];
    index().then(x => { ix = x; upd(); }).catch(() => {});
    UI.api('/words', { quiet: true }).then(d => { all = d.words || []; upd(); }).catch(() => {});
    const ownWords = () => new Set(all.filter(w => w.own).map(w => w.word.toLowerCase()));
    // a tab, " - ", a spaced em dash or ":" splits word from meaning; a CSV with a word,meaning header too;
    // a line with neither is a word to match against the library
    const SPLIT = /^(.+?)(?:\t| - | \u2014 |:)\s*(.+)$/;
    const parse = () => {
      const lines = ta.value.split('\n').map(l => l.trim()).filter(Boolean);
      const csv = lines.length && /^word\s*,\s*meaning/i.test(lines[0]);
      const own = ownWords();
      return (csv ? lines.slice(1) : lines).map(l => {
        const m = csv ? l.match(/^([^,]+),(.*)$/) : l.match(SPLIT);
        const w = (m ? m[1] : l).trim().replace(/^"|"$/g, ''), meaning = m ? m[2].trim().replace(/^"|"$/g, '') : '';
        const hit = ix && ix.byWord.get(w.toLowerCase());
        const st = meaning ? (own.has(w.toLowerCase()) ? 'dup' : 'new') : hit ? 'lib' : 'bad';
        return { word: w, meaning, st, slug: hit && hit.slug };
      });
    };
    const addBtn = () => sh && sh.foot && sh.foot.querySelector('.pill, [data-primary], button:last-child');
    function upd() {
      if (done) return;
      rows = parse();
      const n = rows.filter(r => r.st === 'new' || r.st === 'lib').length;
      const b = addBtn();
      if (b) { b.textContent = n ? `Add ${fmt(n)} ${n === 1 ? 'word' : 'words'}` : 'Add them'; b.disabled = !n; }
      if (!rows.length) { show(h('p', { class: 'help', 'data-nofold': '', text: 'A Quizlet export pastes in as is. A CSV with a word,meaning header works too.' })); return; }
      show(h('div', { class: 'table-wrap' }, h('table', { class: 'table compact' },
        h('thead', {}, h('tr', {}, h('th', { text: 'Word' }), h('th', { text: 'Meaning' }), h('th', { text: '' }))),
        h('tbody', {}, rows.slice(0, 60).map(r => h('tr', {}, h('td', { class: 'w', text: r.word }), h('td', { text: r.meaning || (r.st === 'lib' ? 'the library’s meaning' : '\u2013') }),
          h('td', { class: 'meta', text: LABEL[r.st] })))))),
        rows.length > 60 ? h('p', { class: 'help', text: `and ${fmt(rows.length - 60)} more` }) : null);
    }
    async function addToList(name, slugs) {
      try { await UI.api('/words/lists', { method: 'POST', body: { name, words: slugs } }); }
      catch (e) {
        if (e.status !== 409) throw e;
        const had = all.filter(w => (w.lists || []).includes(name)).map(w => w.slug);
        await UI.api(`/words/lists/${encodeURIComponent(name)}`, { method: 'PUT', body: { words: [...new Set([...had, ...slugs])] } });
      }
    }
    ta.addEventListener('input', upd);
    sh = UI.sheet({ title: 'Import words', size: 'm', body: h('div', { class: 'addw' }, ta, h('label', { class: 'label', text: 'List' }), list, dl, prev),
      actions: [{ label: 'Cancel', quiet: true }, { label: 'Add them', primary: true, onClick: async () => {
        if (done) return true;
        rows = parse();
        const name = list.value.trim().slice(0, 30) || 'My words';
        const own = rows.filter(r => r.st === 'new'), lib = rows.filter(r => r.st === 'lib');
        if (!own.length && !lib.length) return false;
        let added = 0;
        const skipped = rows.filter(r => r.st === 'dup' || r.st === 'bad').map(r => ({ word: r.word, why: r.st === 'dup' ? 'you already have it' : 'no meaning, and not in the library' }));
        try {
          if (own.length) {
            const r = await UI.api('/words/mine/import', { method: 'POST', body: { text: own.map(x => `${x.word}\t${x.meaning}`).join('\n'), list: name } });
            added += r.added || 0;
            (r.skipped || []).forEach(x => skipped.push({ word: (own[(x.line || 1) - 1] || {}).word || `line ${x.line}`, why: /existing/.test(String(x.why)) ? 'you already have it' : String(x.why) }));
          }
          if (lib.length) { await addToList(name, [...new Set(lib.map(x => x.slug))]); added += lib.length; }
        } catch (e) { if (!e.offline) show(h('p', { class: 'field-err', text: 'Not added. Try again.' })); return false; }
        done = true;
        show(h('p', { class: 'line' }, h('b', { text: `Added ${fmt(added)}` }), skipped.length ? ` · skipped ${fmt(skipped.length)}` : ''),
          skipped.length ? h('ul', { class: 'help', 'data-nofold': '' }, skipped.slice(0, 30).map(x => h('li', { text: `${x.word}: ${x.why}` }))) : null);
        const b = addBtn(); if (b) { b.textContent = 'Done'; b.disabled = false; }
        sh.foot.querySelectorAll('button').forEach(x => { if (x !== b) x.hidden = true; });
        ta.disabled = true;
        try { doc.dispatchEvent(new CustomEvent('satf:words', { detail: { imported: added } })); } catch (_) {}
        return false;
      } }] });
    upd();
    setTimeout(() => ta.focus(), 30);
    return sh;
  }
  function bringList() {
    const ta = h('textarea', { class: 'field', rows: '8', maxlength: '20000', placeholder: 'One word per line, or comma-separated (up to 1,000)' });
    const out = h('div', { 'aria-live': 'polite' });
    const name = h('input', { class: 'field sm', maxlength: '30', value: `Word list · ${dayLabel()}`, 'aria-label': 'List name' });
    let found = [], missing = [];
    const sh = UI.sheet({ title: 'Bring a word list', size: 'm', body: h('div', { class: 'addw' }, ta, out, h('label', { class: 'label', text: 'Save as' }), name),
      actions: [{ label: 'Cancel', quiet: true }, { label: 'Match', onClick: async () => { await match(); return false; } },
        { label: 'Save as a list', primary: true, onClick: async () => { if (!found.length) await match(); if (!found.length) return false; return (await saveList(name.value.trim() || 'Word list', found)) ? true : false; } }] });
    async function match() {
      if (!ta.value.trim()) { out.replaceChildren(h('p', { class: 'help', text: 'Paste some words first.' })); return; }
      const r = await UI.api('/words/lists/match', { method: 'POST', body: { text: ta.value } });
      found = r.found || []; missing = r.missing || [];
      const n = found.length + missing.length;
      out.replaceChildren(h('p', { class: 'line', text: `${found.length} of ${n} found in the library${missing.length ? ` · ${missing.length} not in it` : ''}` }),
        missing.length ? h('div', { class: 'wchips' }, missing.slice(0, 60).map(m => h('button', { type: 'button', class: 'wchip', title: 'Make it my word', onclick: () => { sh.close(); addWord({ word: m, source: 'From a word list' }); } }, m, h('small', { text: '+ mine' })))) : null);
    }
    setTimeout(() => ta.focus(), 30);
    return sh;
  }
  function bringText() {
    const ta = h('textarea', { class: 'field', rows: '7', maxlength: '20000', placeholder: 'Paste a passage (up to 20,000 characters). Nothing is sent until you save.' });
    const view = h('div', { class: 'wb' });
    const side = h('div', { class: 'w-side' });
    const body = h('div', { class: 'addw' }, ta, view, side);
    let hits = new Map(), odd = [];
    // the index and the learner's statuses load when the sheet opens: matching the text sends nothing
    index().catch(() => {}); libRows().catch(() => {});
    const sh = UI.sheet({ title: 'Bring words from a text', size: 'l', body });
    let t = 0;
    ta.addEventListener('input', () => { clearTimeout(t); t = setTimeout(scan, 250); });
    async function scan() {
      const text = ta.value;
      if (!text.trim()) { view.replaceChildren(); side.replaceChildren(); return; }
      let ix, lib;
      try { [ix, lib] = await Promise.all([index(), libRows()]); } catch (_) { side.replaceChildren(h('p', { class: 'help', text: 'The library did not load.' })); return; }
      const forms = new Map();
      ix.words.forEach(w => [w.word, ...(w.also || [])].forEach(f => { if (f) forms.set(f.toLowerCase(), w); }));
      const common = new Set(ix.common || []);
      hits = new Map(); odd = [];
      const p = h('p', { class: 'ex' });
      String(text).split(/(\b[A-Za-z][A-Za-z'’-]*\b)/).forEach(tok => {
        const key = tok.toLowerCase().replace(/['’]s$/, '');
        const w = /^[A-Za-z]/.test(tok) ? forms.get(key) : null;
        if (w) {
          const st = status(lib.get(w.slug));
          const mark = st === 'known' ? '●' : st === 'new' || st === 'probable' ? '○' : '◐';
          hits.set(w.slug, { w, st });
          p.append(h('mark', { title: `${w.word}: ${w.short || ''} · ${STATUS[st]}`, text: tok }), h('small', { class: 'meta', text: mark }));
        } else {
          if (/^[A-Za-z]{7,}$/.test(tok) && !common.has(key) && !odd.includes(key)) odd.push(key);
          p.append(tok);
        }
      });
      view.replaceChildren(p);
      const groups = { new: [], learning: [], known: [] };
      hits.forEach(({ w, st }) => groups[st === 'known' ? 'known' : st === 'new' || st === 'probable' ? 'new' : 'learning'].push(w));
      const checks = new Map();
      const col = (k, lab) => groups[k].length ? h('div', {}, h('p', { class: 'k', text: `${groups[k].length} ${lab}` }),
        h('div', { class: 'wchips' }, groups[k].map(w => { const cb = h('input', { type: 'checkbox', checked: true, 'aria-label': w.word }); checks.set(w.slug, cb); return h('label', { class: 'wchip' }, cb, w.word); }))) : null;
      const chosen = () => [...checks.entries()].filter(([, cb]) => cb.checked).map(([s]) => s);
      const name = h('input', { class: 'field sm', maxlength: '30', value: `From pasted text · ${dayLabel()}`, 'aria-label': 'List name' });
      side.replaceChildren(...[col('new', 'new'), col('learning', 'learning'), col('known', 'known'),
        hits.size ? h('div', { class: 'wchips' },
          groups.new.length ? h('button', { type: 'button', class: 'btn sm', text: `Star the ${groups.new.length} new`, onclick: async () => {
            await Promise.all(groups.new.map(w => UI.api(`/words/${encodeURIComponent(w.slug)}/save`, { method: 'POST', body: { on: true } }).catch(() => null)));
            toast(`Starred ${groups.new.length} · they go to the front of New`); } }) : null,
          name, h('button', { type: 'button', class: 'pill sm', text: 'Save as a list', onclick: async () => { const s = chosen(); if (s.length && await saveList(name.value.trim() || 'From pasted text', s)) sh.close(); } })) : h('p', { class: 'help', text: 'No library words in this text yet.' }),
        odd.length ? h('div', {}, h('p', { class: 'k', text: `Not in the library · ${odd.length}` }),
          h('div', { class: 'wchips' }, odd.slice(0, 40).map(o2 => h('button', { type: 'button', class: 'wchip', title: 'Make it my word', onclick: () => { sh.close(); addWord({ word: o2, source: 'From a pasted text' }); } }, o2, h('small', { text: '+ mine' }))))) : null].filter(Boolean));
    }
    setTimeout(() => ta.focus(), 30);
    return sh;
  }
  function bringMissed() {
    const dl = h('datalist', { id: 'bm-words' });
    index().then(ix => ix.words.slice(0, 2000).forEach(w => dl.append(h('option', { value: w.word })))).catch(() => {});
    const inputs = [0, 1, 2, 3].map(i => h('input', { class: 'field sm', list: 'bm-words', maxlength: '60', 'aria-label': `Choice ${'ABCD'[i]}`, placeholder: `Choice ${'ABCD'[i]}` }));
    const radio = (nm, i) => h('input', { type: 'radio', name: nm, value: String(i), 'aria-label': `${nm === 'bm-key' ? 'Right answer' : 'My pick'} ${'ABCD'[i]}` });
    const keys = [0, 1, 2, 3].map(i => radio('bm-key', i)), picks = [0, 1, 2, 3].map(i => radio('bm-pick', i));
    const text = h('textarea', { class: 'field', rows: '3', maxlength: '2000', placeholder: 'The text (optional)' });
    const label = h('input', { class: 'field sm', maxlength: '30', placeholder: 'Bluebook · Test 4 · Q12', 'aria-label': 'Where it was from' });
    const grid = h('div', { class: 'bm-grid' },
      h('span', { class: 'k', text: 'Choices' }), h('span', { class: 'k', text: 'Right' }), h('span', { class: 'k', text: 'I picked' }),
      inputs.map((inp, i) => [inp, keys[i], picks[i]]));
    const out = h('div', { 'aria-live': 'polite' });
    return UI.sheet({ title: 'A question I missed', size: 'm', body: h('div', { class: 'addw' }, h('p', { class: 'help', text: 'A Words in Context or Transitions question from Bluebook or anywhere else.' }), grid, text, label, dl, out),
      actions: [{ label: 'Cancel', quiet: true }, { label: 'Save', primary: true, onClick: async () => {
        const choices = inputs.map(i => i.value.trim());
        const k = keys.findIndex(r => r.checked), p = picks.findIndex(r => r.checked);
        if (choices.some(c => !c) || k < 0 || p < 0) { out.replaceChildren(h('p', { class: 'field-err', text: 'Fill the four choices, the right one and your pick.' })); return false; }
        const r = await UI.api('/words/outside', { method: 'POST', body: { choices, key: choices[k], picked: choices[p], text: text.value.trim() || undefined, label: label.value.trim() || undefined } });
        out.replaceChildren(h('p', { class: 'line' }, h('b', { text: r.trap ? (TRAP[r.trap] || r.trap) : 'Not classified' }), ` · saved to “${r.list}”; both words are starred and due today.`),
          h('div', { class: 'wchips' }, r.run && r.run.id ? h('button', { type: 'button', class: 'pill sm', text: '3 twins · same trap, new word', onclick: () => { remember(); location.href = `/words/run/?id=${encodeURIComponent(r.run.id)}`; } }) : null,
            h('button', { type: 'button', class: 'btn sm', text: 'Quiz the set', onclick: async () => { const ix = await index().catch(() => null); const slugs = choices.map(c => ix && ix.byWord.get(c.toLowerCase())).filter(Boolean).map(x => x.slug); quizStart({ source: 'words', words: slugs }, 4); } })));
        return false;
      } }] });
  }

  /* ------------------------------------------------------------ list keys (§2.8 Lists) */
  // J K or ↑ ↓ move through the items, Enter opens one (they are buttons or rows), X selects it
  function listKeys(scope, sel, o = {}) {
    if (!UI.keys || !UI.keys.register) return null;
    const items = () => [...doc.querySelectorAll(sel)].filter(e => e.offsetParent);
    const at = () => items().indexOf(doc.activeElement);
    const move = n => {
      const a = items();
      if (!a.length) return;
      const i = at();
      const t = a[Math.max(0, Math.min(a.length - 1, i < 0 ? 0 : i + n))];
      t.focus();
      t.scrollIntoView({ block: 'nearest' });
    };
    const on = () => at() >= 0;
    return UI.keys.register(scope, {
      J: { does: 'Next word', run: () => move(1) },
      K: { does: 'Previous word', run: () => move(-1) },
      ArrowDown: { does: 'Next word', when: on, run: () => move(1) },
      ArrowUp: { does: 'Previous word', when: on, run: () => move(-1) },
      X: { does: 'Select it', when: () => on() && !!o.select, run: () => o.select(doc.activeElement) },
    }, { label: o.label || 'Words list' });
  }

  /* ------------------------------------------------------------ share a list or a view (W20) */
  async function share(o = {}) {
    let r;
    try {
      r = o.list ? await UI.api(`/words/lists/${encodeURIComponent(o.list)}/share`, { method: 'POST' })
        : await UI.api('/sets', { method: 'POST', body: { kind: 'words', title: String(o.title || 'Words').slice(0, 60),
          items: (o.words || []).slice(0, 200).map(s => (s.startsWith('u:') ? 'own:' + s : s)) } });
    } catch (e) {
      if (o.quiet404 && e.status === 404) return false;
      if (!e.offline) toast(e.status >= 400 && e.status < 500 ? cap(e.message) : 'Couldn’t make the link. Try again.');
      return null;
    }
    if (!r || r.available === false || !r.url) { toast('Sharing is not available yet.'); return null; }
    const url = new URL(r.url, location.origin).href;
    const field = h('input', { class: 'field', type: 'text', readonly: true, value: url, 'aria-label': 'Link', onfocus: e => e.target.select() });
    UI.sheet({ title: o.list || o.title || 'Share', size: 's',
      body: h('div', { class: 'addw' }, h('p', { class: 'line', text: plural(r.count || (o.words || []).length, 'word') }), field),
      actions: [navigator.share ? { label: 'Share…', onClick: () => { navigator.share({ title: o.list || o.title || 'Words', url }).catch(() => {}); return false; } } : null,
        { label: 'Open', href: url, quiet: true },
        { label: 'Copy link', primary: true, onClick: () => { UI.copyText ? UI.copyText(url, { toast: 'Link copied' }) : field.select(); return false; } }].filter(Boolean) });
    return r;
  }

  /* ------------------------------------------------------------ worksheets (W20) */
  // the 4-option types a pencil can answer; Type it and Order the ladder stay on screen
  const PRINTABLE = ['incontext', 'transition', 'precise', 'meaning2word', 'word2meaning', 'nearly', 'cloze'];
  function printSheet(deck, o = {}) { return busy(() => postPrint(deck, o)); }
  async function postPrint(deck, o = {}) {
    const formats = (o.formats || []).filter(f => PRINTABLE.includes(f));
    const body = { mode: 'print', deck, formats: formats.length ? formats : ['incontext', 'meaning2word'], count: Math.max(10, Math.min(40, o.count || 20)) };
    let r;
    try { r = await UI.api('/words/run', { method: 'POST', body }); }
    catch (e) {
      if (e.status === 409 || e.status === 400 || e.status === 422) {
        try { r = await UI.api('/words/run', { method: 'POST', body: { ...body, formats: ['meaning2word', 'word2meaning'] } }); } catch (e2) { if (!e2.offline) toast(cap(e2.message)); return null; }
      } else { if (!e.offline) toast('Couldn’t make the worksheet. Try again.'); return null; }
    }
    remember(o.from);
    location.href = `/words/print/?id=${encodeURIComponent(r.id)}`;
    return r;
  }
  // the code on a sheet is its run id with W- for w:; letters are one A–D per item
  const sheetId = code => { const c = String(code || '').trim().replace(/^w[-:]/i, ''); return c ? 'w:' + c : ''; };
  function gradeSheet(pre = {}) {
    const code = h('input', { class: 'field', maxlength: '40', value: pre.code || '', placeholder: 'W-…', 'aria-label': 'Worksheet code', autocomplete: 'off', spellcheck: 'false' });
    const letters = h('input', { class: 'field', maxlength: '40', placeholder: 'CABD…', 'aria-label': 'Letters, one per question', autocomplete: 'off', spellcheck: 'false',
      oninput: () => { letters.value = letters.value.toUpperCase().replace(/[^A-D]/g, ''); n.textContent = `${letters.value.length}${pre.count ? ` of ${pre.count}` : ''}`; } });
    const n = h('span', { class: 'meta', text: pre.count ? `0 of ${pre.count}` : '' });
    const out = h('div', { 'aria-live': 'polite' });
    return UI.sheet({ title: 'Grade a worksheet', size: 's',
      body: h('div', { class: 'addw' }, pre.code ? null : [h('label', { class: 'label', text: 'Code, from the top of the sheet' }), code],
        h('label', { class: 'label', text: 'The letters, in order' }), letters, n, out),
      focus: pre.code ? letters : code,
      actions: [{ label: 'Cancel', quiet: true }, { label: 'Grade', primary: true, onClick: async () => {
        const id = sheetId(pre.code || code.value);
        if (!id) { out.replaceChildren(h('p', { class: 'field-err', text: 'Add the code' })); return false; }
        try { await UI.api(`/words/run/${encodeURIComponent(id)}/grade`, { method: 'POST', body: { letters: letters.value } }); }
        catch (e) {
          if (!e.offline) out.replaceChildren(h('p', { class: 'field-err', text: e.status === 404 || e.status === 403 ? 'No worksheet with that code on this account.'
            : e.status === 409 ? 'That code is not a worksheet.' : e.status === 422 ? 'One letter, A to D, for every question.' : 'Not graded. Try again.' }));
          return false;
        }
        location.href = `/words/run/?id=${encodeURIComponent(id)}`;
      } }] });
  }

  /* ------------------------------------------------------------ offline cards (W22) */
  // one IndexedDB store; every read and write is caught, and a failure reads as "not kept"
  const idb = (() => {
    let p = null;
    const open = () => p || (p = new Promise((res, rej) => {
      const r = indexedDB.open('satf-words', 1);
      r.onupgradeneeded = () => r.result.createObjectStore('kv');
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    }).catch(e => { p = null; throw e; }));
    const tx = async (mode, fn) => {
      const db = await open();
      return new Promise((res, rej) => { const t = db.transaction('kv', mode); const q = fn(t.objectStore('kv')); t.oncomplete = () => res(q && q.result); t.onerror = t.onabort = () => rej(t.error); });
    };
    const safe = f => (...a) => { try { return f(...a); } catch (e) { return Promise.reject(e); } };
    return {
      get: k => safe(tx)('readonly', s => s.get(k)).catch(() => undefined),
      set: (k, v) => safe(tx)('readwrite', s => s.put(v, k)).then(() => true, () => false),
    };
  })();
  let flushing = false;
  const offline = {
    ok: () => { try { return 'serviceWorker' in navigator && typeof indexedDB !== 'undefined' && isSecureContext; } catch (_) { return false; } },
    register() { try { return navigator.serviceWorker.register('/words/sw.js', { scope: '/words/' }).catch(() => null); } catch (_) { return Promise.resolve(null); } },
    // today's due and new cards as one cards run, its faces kept on this device
    async take() {
      await offline.register();
      let r;
      try { r = await UI.api('/words/run', { method: 'POST', body: { mode: 'cards', deck: { source: 'today' }, count: 60 } }); }
      catch (e) { if (!e.offline) toast(e.status === 409 ? cap(e.message) : 'Couldn’t save them. Try again.'); return null; }
      if (!(r.items || []).length) { toast('Nothing to take today.'); return null; }
      const ok = await idb.set('run:' + r.id, { ...r, done: [] });
      if (!ok || !(await idb.set('today', { id: r.id, day: today(), n: r.items.length }))) { toast('This browser won’t keep them. Try again with more free space.'); return null; }
      return r;
    },
    async stored() {
      const t = await idb.get('today');
      if (!t || t.day !== today()) return null;
      const run = await idb.get('run:' + t.id);
      return run ? { id: t.id, left: Math.max(0, (run.items || []).length - (run.done || []).length) } : null;
    },
    run: id => idb.get('run:' + id),
    async done(id, itemId) {
      const run = await idb.get('run:' + id);
      if (run && !(run.done || []).includes(itemId)) { run.done = [...(run.done || []), itemId]; await idb.set('run:' + id, run); }
    },
    async queue(entry) {
      const q = (await idb.get('queue')) || [];
      q.push(entry);
      const ok = await idb.set('queue', q);
      offline.banner(q.length);
      return ok;
    },
    async pending() { return ((await idb.get('queue')) || []).length; },
    banner(n) {
      if (!UI.banner) return;
      if (n && !navigator.onLine) UI.banner('words-offline', `Offline · ${plural(n, 'grade')} will sync`, [], { dismiss: false });
      else if (UI.banner.clear) UI.banner.clear('words-offline');
    },
    // replay in order; the server claims each answer once, so a replay is safe, and a
    // refused one (already claimed, or older than 72 hours) is dropped
    async flush() {
      if (flushing) return;
      flushing = true;
      try {
        let q = (await idb.get('queue')) || [];
        while (q.length) {
          const e = q[0];
          try { await UI.api(`/words/run/${encodeURIComponent(e.run)}/answer`, { method: 'POST', quiet: true, body: { item_id: e.item_id, answer: e.answer, ms: e.ms, at: e.at } }); }
          catch (err) { if (err.offline) break; }
          q = q.slice(1);
          await idb.set('queue', q);
        }
        offline.banner(q.length);
        if (!q.length) doc.dispatchEvent(new CustomEvent('satf:words'));
      } finally { flushing = false; }
    },
  };
  if (offline.ok()) {
    addEventListener('online', () => offline.flush());
    addEventListener('offline', () => offline.pending().then(n => offline.banner(n)));
    offline.pending().then(n => { if (n) { if (navigator.onLine) offline.flush(); else offline.banner(n); } });
  }

  word.listKeys = listKeys;
  word.share = share;
  word.print = printSheet;
  word.gradeSheet = gradeSheet;
  word.sheetId = sheetId;
  word.PRINTABLE = PRINTABLE;
  word.offline = offline;
  Object.assign(UI, { wordsTabs, todayWords, wordsFinish, word, startWords, addWord, addWordFromSelection, gloss, speak, bringWords });
})();
