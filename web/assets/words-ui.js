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
.wtabs { display: inline-flex; gap: 2px; padding: 3px; border-radius: 12px; background: var(--tile); max-width: 100%; overflow-x: auto; }
.wtabs a { display: inline-flex; align-items: center; gap: 7px; min-height: calc(var(--ctl) - 6px); padding: 0 16px; border-radius: 9px;
  font: 600 14px var(--font); color: var(--ink); text-decoration: none; white-space: nowrap; }
.wtabs a[aria-current="page"] { background: var(--wash); box-shadow: inset 0 0 0 1.5px var(--amber); }
.wtabs .n { font: 500 12px var(--mono); color: var(--soft); }
.wtabs .s { display: none; }
@media (hover: hover) and (pointer: fine) { .wtabs a:not([aria-current]):hover { background: var(--tile-2); } }
@media (max-width: 419px) { .wtabs { display: flex; } .wtabs a { flex: 1; justify-content: center; padding: 0 8px; } .wtabs .l { display: none; } .wtabs .s { display: inline; } }
.today-words { display: grid; gap: 12px; }
.tw-top { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 14px; }
.tw-top h2 { font: 700 17px var(--font); letter-spacing: -.01em; }
.tw-facts { font: 500 13px var(--mono); color: var(--soft); }
.tw-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; }
.tw-row .pill { min-width: 150px; }
.tw-box { display: inline-flex; align-items: center; gap: 8px; margin-left: auto; }
.tw-box .k { white-space: nowrap; }
.tw-note { font: 400 13.5px/1.45 var(--font); color: var(--ink); }
.tw-note b { font-weight: 600; }
@media (max-width: 759px) { .tw-row .pill { flex: 1 1 100%; min-height: 48px; } .tw-row > .btn { flex: 1 1 calc(33% - 8px); min-height: var(--touch); padding: 0 8px; } .tw-box { margin-left: 0; } }
.wfin { display: grid; gap: 10px; }
.wfin-l { font: 400 14px/1.5 var(--font); }
.wfin-l b { font-weight: 600; }
.wfin .chips { flex-wrap: wrap; }
.wfin details summary { cursor: pointer; font: 600 13.5px var(--font); }
.wfin details p { margin-top: 6px; font: 400 13px/1.5 var(--font); color: var(--soft); max-width: 70ch; }
dialog.sheet.wsheet { max-width: min(720px, calc(100vw - 32px)); max-height: 88vh; }
.wsheet > .sheet-head { position: sticky; top: 0; background: inherit; z-index: 1; }
.wsheet > .sheet-head h2 { font: 800 32px/1.05 var(--font) !important; letter-spacing: -.03em; overflow-wrap: break-word; flex: 0 1 auto; }
.ws-mode .seg { --ctl: 30px; }
.ws-tools { display: flex; flex: none; align-items: center; gap: 2px; margin-left: auto; }
.ws-tools .btn.icon { background: none; }
.ws-tools .btn[aria-pressed="true"] { color: var(--amber-deep); }
.ws-tools .btn[aria-pressed="true"] svg path { fill: var(--amber); stroke: var(--amber-deep); }
.ws-sub { display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: center; margin: -4px 0 12px; font: 500 13px var(--mono); color: var(--soft); }
.ws-chips { display: flex; flex-wrap: wrap; gap: 6px 8px; align-items: center; margin-bottom: 16px; }
.wtag { display: inline-flex; align-items: center; gap: 6px; min-height: 26px; padding: 0 10px; border-radius: 999px; background: var(--tile); font: 500 12.5px var(--font); color: var(--ink); }
.wtag.m { font-family: var(--mono); font-size: 12px; color: var(--soft); background: none; padding: 0; }
.wb { padding: 14px 0; border-top: 1px solid var(--line); }
.wb:first-of-type { border-top: 0; }
.wb > .k { display: block; margin-bottom: 8px; }
.wb .meaning { font: 400 19px/1.5 var(--serif); }
.wb .ex { font: 400 16.5px/1.55 var(--serif); margin: 4px 0; }
.wb .ex mark, .fsent mark { background: var(--wash); color: inherit; box-shadow: inset 0 -2px 0 var(--amber); padding: 0 1px; }
.wb .src { font: 400 12.5px var(--font); color: var(--soft); font-style: italic; }
.wb .line { font: 400 14px/1.5 var(--font); }
.wb .line + .line { margin-top: 4px; }
.wchips { display: flex; flex-wrap: wrap; gap: 6px; }
.wchip { appearance: none; border: 0; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; min-height: 32px; padding: 0 12px;
  border-radius: 8px; background: var(--tile); font: 600 14px var(--font); color: var(--ink); }
.wchip.plain { cursor: default; font-weight: 500; background: none; padding: 0 6px; }
.wchip[aria-current="true"] { background: var(--wash); box-shadow: inset 0 0 0 1.5px var(--amber); }
.wchip small { font: 500 11.5px var(--mono); color: var(--soft); }
@media (hover: hover) and (pointer: fine) { button.wchip:not([aria-current="true"]):hover { background: var(--tile-2); } }
.shades .wchips + .wchips { margin-top: 6px; }
.shade-n { margin-top: 8px; font: 400 14px/1.5 var(--serif); }
.confu { display: grid; gap: 4px; padding: 10px 0; }
.confu + .confu { border-top: 1px dashed var(--line); }
.confu .t { font: 400 15px/1.5 var(--serif); }
.confu .fell { display: flex; align-items: center; gap: 6px; font: 500 12.5px var(--mono); color: var(--ink); }
.confu .acts { display: flex; gap: 14px; margin-top: 2px; }
.ladder { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; margin: 10px 0; }
.ladder span { display: grid; gap: 4px; font: 500 11.5px var(--font); color: var(--soft); text-align: center; }
.ladder span::before { content: ""; height: 6px; border-radius: 3px; background: var(--mat); }
.ladder span.on { color: var(--ink); }
.ladder span.on::before { background: var(--amber); }
.journey { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; margin: 8px 0; }
.journey i { width: 12px; height: 12px; border-radius: 50%; box-shadow: inset 0 0 0 1.5px var(--ink); font-style: normal; }
.journey i.ok { background: var(--amber); box-shadow: inset 0 0 0 1.5px var(--amber-deep); }
.journey i.ctx { border-radius: 3px; }
.journey .nx { font: 500 12px var(--mono); color: var(--soft); margin-left: 6px; }
.hook { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.hook input { flex: 1; }
.wsample .q-stem { font-size: 17.5px; }
.wsample .ws-ask { margin: 6px 0 10px; font: 600 14px var(--font); }
.ws-foot { position: sticky; bottom: 0; }
.ws-foot .grow { flex: 1; }
.wsheet.covered .cov { position: relative; }
.wsheet.covered .cov > :not(.k) { visibility: hidden; }
.wsheet.covered .cov::after { content: "Covered"; position: absolute; left: 0; top: 34px; font: 500 12px var(--mono); color: var(--faint); }
.wsheet.covered .cov-t { visibility: hidden; }
.wsheet.covered .wsample .opt-why, .wsheet.covered .wsample .ws-verdict .mistake, .wsheet.covered .wsample .v-clue { visibility: hidden; }
.ws-mode { font: 500 12px var(--mono); }
.wmsg { padding: 18px 0; font: 400 15px var(--font); }
button.term { appearance: none; border: 0; background: none; padding: 0; font: inherit; color: inherit; cursor: help;
  text-decoration: underline dotted var(--faint); text-decoration-thickness: 1.5px; text-underline-offset: 3px; }
.gpop { display: grid; gap: 6px; max-width: 300px; }
.gpop b { font: 700 16px var(--font); }
.gpop p { font: 400 14px/1.45 var(--font); }
.gpop .acts { display: flex; gap: 8px; flex-wrap: wrap; }
.addw { display: grid; gap: 12px; }
.addw .two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 559px) { .addw .two { grid-template-columns: 1fr; } }
.addw .field-err { margin-top: 4px; }
.addw .dup { font: 400 13.5px var(--font); }
`;
  if (!doc.getElementById('words-ui-css')) doc.head.append(h('style', { id: 'words-ui-css', text: CSS }));

  /* ------------------------------------------------------------ helpers */
  const L = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"';
  const PATHS = {
    speak: `<path d="M4.5 9.5h3l4.5-4v13l-4.5-4h-3z" ${L}/><path d="M15.5 9a4 4 0 0 1 0 6M17.8 6.5a7.5 7.5 0 0 1 0 11" ${L}/>`,
    star: `<path d="M12 4.5l2.3 4.7 5.2.8-3.8 3.6.9 5.1L12 16.3l-4.6 2.4.9-5.1-3.8-3.6 5.2-.8z" ${L}/>`,
    flag: `<path d="M6 20V4.5M6 5h10.5l-2 3.5 2 3.5H6" ${L}/>`,
    left: `<path d="M14.5 6l-6 6 6 6" ${L} stroke-width="1.8"/>`,
    right: `<path d="M9.5 6l6 6-6 6" ${L} stroke-width="1.8"/>`,
    more: `<circle cx="6" cy="12" r="1.3" fill="currentColor"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/><circle cx="18" cy="12" r="1.3" fill="currentColor"/>`,
    plus: `<path d="M12 5v14M5 12h14" ${L} stroke-width="1.8"/>`,
    edit: `<path d="M5 19l1-4 9.5-9.5 3 3L9 18z M13.5 7.5l3 3" ${L}/>`,
  };
  const ic = (n, size = 18) => { const t = doc.createElement('template'); t.innerHTML = `<svg width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${PATHS[n] || ''}</svg>`; return t.content.firstChild; };
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
  const statusLine = s => String(s || '')
    .replace(/\bBack (\d{4}-\d{2}-\d{2})/, (m, d) => { const n = dayDiff(today(), d); return n <= 0 ? 'Back today' : n === 1 ? 'Back tomorrow' : n <= 21 ? `Back in ${n} days` : `Back ${dayName(d)}`; })
    .replace(/\d{4}-\d{2}-\d{2}/g, d => dayName(d));
  const POS = { 'n.': 'noun', 'v.': 'verb', 'adj.': 'adjective', 'adv.': 'adverb', 'phrase.': 'phrase', phrase: 'phrase' };
  const TRAP = { reversed: 'Reverses the meaning', too_strong: 'Too strong', too_weak: 'Too weak', connotation: 'Wrong tone',
    lookalike: 'Looks like the answer', everyday: 'Everyday meaning', topical: 'Fits the subject, not the blank',
    wrong_logic: 'Wrong relationship', reversed_direction: 'Cause and effect swapped' };
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
    return { ...r, given: g, trap, trap_check: trap ? CHECK[trap] : null };
  };
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
  async function startWords(body, o = {}) {
    let r;
    try { r = await UI.api('/words/run', { method: 'POST', body }); }
    catch (e) {
      if (o.fallback && (e.status === 409 || e.status === 400)) return startWords(o.fallback, { ...o, fallback: null });
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
      h('span', { class: 'l', text: l }), h('span', { class: 's', text: s }),
      id === 'mine' && due ? [h('span', { class: 'dot', 'aria-hidden': 'true' }), h('span', { class: 'n', text: String(due), 'aria-label': `${due} due` })] : null)));
    if (host) host.replaceChildren(el);
    return el;
  }

  /* ------------------------------------------------------------ Today's words (W11) */
  function todayWords(host, o = {}) {
    const el = h('section', { class: 'card today-words', 'aria-label': 'Today’s words' });
    if (host) host.replaceChildren(el);
    let box = ls.get('satf.words.box', null);
    async function draw() {
      el.replaceChildren(h('div', { class: 'tw-top' }, h('h2', { text: 'Today’s words' })));
      if (UI.skel) UI.skel(el, 'line'); else el.append(h('p', { class: 'meta', text: 'Loading…' }));
      let d;
      try { d = await UI.api('/words/today', { quiet: true }); }
      catch (_) { el.replaceChildren(h('div', { class: 'tw-top' }, h('h2', { text: 'Today’s words' }))); if (UI.cardError) UI.cardError(el, draw, 'Today’s words did not load.'); return; }
      paint(d.summary || {});
    }
    function paint(s) {
      const lib = o.lib || null, c = (lib && lib.counts) || {};
      const newLeft = Math.max(0, (s.new_goal || 0) - (s.new_today || 0));
      const fresh = lib && !c.learning && !c.known && !c.claimed && !c.due && !s.new_today;
      const facts = [s.due ? `${s.due} due` : null, s.proofs ? `${s.proofs} ${s.proofs === 1 ? 'proof' : 'proofs'}` : null,
        newLeft ? `${newLeft} new` : null, s.minutes ? `about ${Math.max(1, Math.round(s.minutes))} min` : null].filter(Boolean);
      const debt = lib && lib.debt;
      const top = h('div', { class: 'tw-top' }, h('h2', { text: 'Today’s words' }),
        s.done ? h('span', { class: 'tw-facts', text: 'Done for today' }) : facts.length ? h('span', { class: 'tw-facts', text: facts.join(' · ') }) : null);
      const goal = s.new_goal || 10;
      const learn = h('button', { type: 'button', class: 'btn', text: s.done && !newLeft ? `Learn ${goal} more` : `Learn ${goal}`,
        onclick: () => startWords({ mode: 'cards', deck: { source: 'new' }, count: goal }) });
      const review = h('button', { type: 'button', class: 'btn', disabled: !s.due, text: s.due ? `Review cards (${s.due} due)` : 'Review cards',
        title: s.due ? null : 'Nothing is due', onclick: () => startWords({ mode: 'cards', deck: { source: 'due' }, order: 'due' }) });
      const quiz = h('button', { type: 'button', class: 'btn', text: 'Quiz', onclick: () => quizStart({ source: 'today' }, 10) });
      const startBody = () => ({ mode: 'mix', deck: { source: 'today' }, ...(box ? { box } : {}) });
      const row = h('div', { class: 'tw-row' });
      if (fresh) {
        row.append(h('button', { type: 'button', class: 'pill', text: 'Find your level · 3 min', onclick: () => startWords({ mode: 'placement' }) }),
          h('span', { class: 'meta', text: 'or' }), learn);
      } else {
        const start = h('button', { type: 'button', class: 'pill', onclick: () => startWords(startBody()) },
          s.done ? 'Start again' : 'Start', h('span', { class: 'kbd', text: 'Enter', hidden: !o.enter }));
        row.append(start, review, learn, quiz);
        const chips = h('span', { class: 'tw-box' }, h('span', { class: 'k', text: 'Time box' }));
        const seg = UI.chips(chips, [{ value: '5', label: '5 min' }, { value: '10', label: '10' }, { value: '15', label: '15' }],
          { value: box ? String(box) : null, label: 'Time box, minutes', onChange: v => { box = box === +v ? null : +v; ls.set('satf.words.box', box); seg.set(box ? String(box) : null, true); } });
        const prev = h('button', { type: 'button', class: 'btn sm', 'aria-label': 'Preview today’s words', title: 'Preview', onclick: () => preview(s, startBody) }, ic('right', 16));
        chips.append(prev);
        row.append(chips);
      }
      el.replaceChildren(top, row);
      if (debt && debt.due) {
        const days = Math.max(2, Math.ceil(debt.due / Math.max(1, debt.spread || 1)));
        el.append(h('p', { class: 'tw-note' }, h('b', { text: `${debt.due} due` }), debt.away ? ` after ${plural(debt.away, 'day')} away · ` : ' · ',
          h('button', { type: 'button', class: 'quiet', text: `Spread over ${days} days`, onclick: () => spread(days) }), ' · ',
          h('button', { type: 'button', class: 'quiet', text: 'Do all now', onclick: () => startWords({ mode: 'cards', deck: { source: 'due' }, count: Math.min(200, debt.due) }) })));
      }
      if (s.reason && !s.done && !fresh && s.due) el.append(h('p', { class: 'help', text: s.reason }));
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
    const el = h('section', { class: 'card wfin', 'aria-label': 'By exam day' });
    if (host) host.replaceChildren(el);
    const f = (ins && ins.finish) || {};
    if (!f.exam) {
      const b = h('button', { type: 'button', class: 'btn', text: 'Set your SAT date' });
      b.addEventListener('click', () => UI.examDate && UI.examDate(b, { onSave: async v => { await UI.api('/me', { method: 'PUT', body: { exam_date: v } }); if (o.onChange) o.onChange(); } }));
      el.append(h('div', { class: 'tw-top' }, h('h2', { text: 'By exam day' })), h('p', { class: 'wfin-l', text: 'Set your SAT date to see your finish line.' }), h('div', {}, b));
      return el;
    }
    const left = f.left || {}, days = dayDiff(today(), f.exam);
    const bits = [left.core ? `core: ${UI.num(left.core)} left` : 'core: done', left.advanced ? `advanced: ${UI.num(left.advanced)} left` : null,
      left.logics ? `transition logics: ${left.logics} of 9 not yet known` : null].filter(Boolean);
    el.append(h('div', { class: 'tw-top' }, h('h2', { text: 'By exam day' }), h('span', { class: 'tw-facts', text: `${shortDate(f.exam)} · ${plural(days, 'day')}` })),
      h('p', { class: 'wfin-l', text: cap(bits.join(' · ')) }));
    const studied = (f.likely || 0) + (f.at_risk || 0);
    if (studied) {
      el.append(h('p', { class: 'wfin-l' }, h('b', { text: `${UI.num(f.likely || 0)} of ${UI.num(studied)}` }), ' studied words likely to hold on test day',
        f.at_risk ? [` · ${UI.num(f.at_risk)} at risk `, h('button', { type: 'button', class: 'btn sm', text: `Review at risk (${f.at_risk})`,
          onclick: () => startWords({ mode: 'cards', deck: { source: 'atrisk' }, count: Math.min(200, f.at_risk) }) })] : null));
    }
    if (days <= 10) el.append(h('p', { class: 'help', text: 'Final 10 days · reviews and at-risk words only' }));
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
      el.append(row);
    }
    el.append(h('details', {}, h('summary', { text: 'How this is worked out' }),
      h('p', { text: 'Each word you have studied is likely to hold when p = 2^(−t/h) is at least 0.8: h is the word’s current interval, scaled by how well you recall due words and by 0.8 for every lapse, and t is the days from its last right answer to the exam. The finish dates run your schedule forward at your own lapse rate.' })));
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
  function speakBtn(word, cls = 'btn icon') {
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

    function step(n) {
      if (!list.length) return;
      const i = list.indexOf(cur);
      const j = i < 0 ? 0 : i + n;
      if (j < 0 || j >= list.length) return;
      go(list[j], { covered: !!o.covered });   // W14: a covered grid pages front-first
    }
    function go(s, oo = {}) {
      cur = s;
      if (oo.covered !== undefined) selftest = covered = oo.covered;
      setW(s);
      load();
    }
    function uncover() { covered = false; d.classList.remove('covered'); paintFoot(); }
    async function load() {
      api.body.replaceChildren(h('p', { class: 'meta', text: 'Loading…' }));
      foot.replaceChildren();
      tools.replaceChildren();
      d.classList.toggle('covered', covered);
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
      const star = h('button', { type: 'button', class: 'btn icon', 'aria-pressed': String(saved), 'aria-label': saved ? 'Saved' : 'Save', title: 'Save (B)', onclick: toggleSave }, ic('star'));
      const i = list.indexOf(cur);
      tools.replaceChildren(...[speakBtn(data.word), star,
        h('button', { type: 'button', class: 'btn icon', 'aria-label': 'Report a problem with this word', title: 'Report',
          onclick: () => UI.report && UI.report({ kind: 'word', source: 'words', word: data.slug, meaning: data.meaning }) }, ic('flag')),
        ...(list.length > 1 ? [h('button', { type: 'button', class: 'btn icon', 'aria-label': 'Previous word', title: 'Previous (←)', disabled: i <= 0, onclick: () => step(-1) }, ic('left')),
          h('button', { type: 'button', class: 'btn icon', 'aria-label': 'Next word', title: 'Next (→)', disabled: i < 0 || i >= list.length - 1, onclick: () => step(1) }, ic('right'))] : [])]);
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
      // sub line and chips
      body.push(h('p', { class: 'ws-sub' }, w.pos ? h('span', { text: POS[w.pos] || w.pos }) : null,
        (w.also || []).length ? h('span', { text: `also: ${w.also.join(', ')}` }) : null,
        w.sense && w.sense !== 'main' && w.sense !== '' ? h('span', { class: 'wtag', text: w.sense.replace(/_/g, ' ') }) : null,
        own ? h('span', { class: 'wtag', text: 'My word' }) : null,
        coverSeg()));
      const lv = level(w.measured, w.level);
      body.push(h('div', { class: 'ws-chips' },
        w.collection ? h('span', { class: 'wtag', text: collName(w.collection) }) : null,
        (w.lists || []).map(l => h('span', { class: 'wtag', text: collName(l) })),
        (w.subjects || []).map(t => h('span', { class: 'wtag', text: cap(t) })),
        !own ? h('span', { class: 'wtag' }, dbars(lv.tier), lv.text ? h('span', { class: 'meta', text: lv.text }) : null) : null,
        w.corrected ? h('span', { class: 'wtag m', text: `Corrected ${shortDate(w.corrected)} after a student report` }) : null));
      body.push(block('Meaning', h('p', { class: 'meaning', text: w.meaning || '' }), { cover: true }));
      // shades (W3)
      const sh = w.shades && w.shades.words || [];
      if (sh.length > 1) {
        // one row, weakest -> strongest; the tone shows on each chip only when the class mixes tones
        const mixed = new Set(sh.map(x => Math.sign(x.polarity || 0))).size > 1;
        const tone = x => ({ 1: '+', 0: '0', '-1': '−' })[Math.sign(x.polarity || 0)];
        body.push(block(`Shades · ${w.shades.dimension || 'weakest → strongest'}`, [
          h('div', { class: 'wchips', 'aria-label': 'Weakest to strongest' }, sh.map(x => wordChip({ slug: x.slug, word: x.word }, { current: x.slug === w.slug, small: mixed ? tone(x) : null }))),
          h('p', { class: 'help', text: `Weakest → strongest${mixed ? ' · + approving, 0 neutral, − critical' : ''}. The most precise word matches the text’s strength and tone.` }),
          w.shade ? h('p', { class: 'shade-n', text: w.shade }) : null], { cover: true, cls: 'shades' }));
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
      // the sample (W1)
      if (w.sample && w.sample.item) body.push(sampleBlock(w));
      // same / opposite
      const same = await resolveWords(w.same), opp = await resolveWords(w.opposite);
      if (same.length || opp.length || w.no_opposite) {
        body.push(block('Same as · opposite of', [
          same.length ? h('div', { class: 'wchips' }, h('span', { class: 'meta', text: '=' }), same.map(x => wordChip(x))) : null,
          opp.length ? h('div', { class: 'wchips', style: 'margin-top:6px' }, h('span', { class: 'meta', text: '≠' }), opp.map(x => wordChip(x)))
            : w.no_opposite ? h('p', { class: 'help', text: 'No single-word opposite' }) : null], { cover: true }));
      }
      // not the same as
      const conf = w.confusions || [];
      const seen = new Set(conf.map(c => String(c.other).toLowerCase()));
      const looks = (w.lookalikes || []).filter(l => !seen.has(String(l.word).toLowerCase()));
      if (conf.length || looks.length) {
        const ix = await index().catch(() => null);
        const rows = conf.map(c => confRow(c.kind, c.other, c.tell, c, ix)).concat(looks.map(l => confRow('lookalike', l.word, l.tell, {}, ix)));
        body.push(block('Not the same as', rows));
      }
      body.push(recordBlock(w, s));
      if (own) body.push(ownBlock(w));
      api.body.replaceChildren(...body.filter(Boolean));
      d.classList.toggle('covered', covered);
      paintFoot();
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
      const lead = kind === 'lookalike' ? 'looks like ' : kind === 'sense' ? 'other meaning: ' : 'vs ';
      return h('div', { class: 'confu' },
        h('p', { class: 'line' }, lead, hit ? h('button', { type: 'button', class: 'quiet', style: 'margin:0;padding:0 2px', onclick: () => go(hit.slug, { covered: false }) }, h('b', { text: other })) : h('b', { text: other })),
        h('p', { class: 't cov-t', text: tell || '' }),
        c.fell ? h('p', { class: 'fell' }, h('span', { class: 'dot' }), `You picked it for this ${c.fell}×${c.last ? ' · last ' + shortDate(c.last) : ''}`) : null,
        hit ? h('div', { class: 'acts' }, h('button', { type: 'button', class: 'quiet', text: 'Quiz the pair · 6',
          onclick: () => startWords({ mode: 'quiz', deck: { source: 'words', words: [data.slug, hit.slug] }, formats: ['meaning2word', 'word2meaning'], count: 6 }) })) : null);
    }
    function sampleBlock(w) {
      const host = h('div', { class: 'wsample' });
      const sec = block('In an SAT-style question', host);
      let token = w.sample.token;
      const mount = async item => {
        host.replaceChildren(h('p', { class: 'meta', text: 'Loading…' }));
        try { if (!UI.workspace) await UI.need('question'); } catch (_) { host.replaceChildren(h('p', { class: 'help', text: 'Could not load the question.' })); return; }
        const q = { id: item.item_id, type: 'mcq', stem: item.text || '', choices: item.choices || [], latex: [] };
        host.replaceChildren();
        const ws = UI.workspace(host, q, { mode: 'quiz', head: { label: `${KIND[item.kind] || 'Words in Context'}${item.source ? '' : ''}` },
          onCheck: async (answer, meta) => {
            const r = await UI.api('/words/sample/answer', { method: 'POST', body: { token, answer, ms: meta && meta.ms, conf: meta && meta.conf === 'guess' ? 'guess' : undefined } });
            if (o.onChange) o.onChange(w.slug, { graded: true });
            return verdict(r, answer);
          },
          actions: (slot) => slot.append(h('button', { type: 'button', class: 'btn sm', onclick: another }, UI.VERBS ? 'Twin' : 'Another', h('span', { class: 'meta', text: ' same word, new text' }))) });
        const stem = ws.el.querySelector('.q-stem');
        if (stem && item.stem) stem.after(h('p', { class: 'ws-ask', text: item.stem }));
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
        h('p', { class: 'line' }, pips({ state: s }), ' ', h('b', { text: STATUS[st] }), next ? ` · ${next}` : '', s.proven ? ` · proven ${shortDate(s.proven)}` : ''),
        h('div', { class: 'ladder', role: 'list', 'aria-label': 'Proof ladder' }, steps.map(([t, on]) => h('span', { role: 'listitem', class: on ? 'on' : null, 'aria-label': `${t}${on ? ', done' : ''}`, text: t }))),
        r.n ? h('p', { class: 'line', text: `Reviews ${r.n} · right ${r.right}${byKind ? ' · ' + byKind : ''}` }) : null,
        j.length ? h('div', { class: 'journey', role: 'img', 'aria-label': `${j.length} reviews, ${j.filter(x => x.correct).length} right` },
          j.map(x => { const i = h('i', { class: (x.correct ? 'ok' : '') + (CONTEXT_KINDS.has(x.kind) ? ' ctx' : '') }); if (UI.tooltip) UI.tooltip(i, `${shortDate(x.at)} · ${KIND[x.kind] || x.kind} · ${x.correct ? 'right' : x.correct === null ? 'seen' : 'wrong'}${x.given && !x.correct ? ` · picked “${x.given}”` : ''}${x.trap ? ` · ${TRAP[x.trap] || x.trap}` : ''}`); return i; }),
          s.due ? h('span', { class: 'nx', text: `next ${shortDate(s.due)}` }) : null) : null,
        lastWrong && lastWrong.given && !['dontknow', 'know'].includes(lastWrong.given) ? h('p', { class: 'line', text: `Last time you picked “${lastWrong.given}”` }) : null,
        [s.first ? `First seen ${shortDate(s.first)}` : null, w.record && w.record.lookups ? `Looked up ${w.record.lookups}× in Words texts` : null].some(Boolean)
          ? h('p', { class: 'help', text: [s.first ? `First seen ${shortDate(s.first)}` : null, w.record && w.record.lookups ? `Looked up ${w.record.lookups}× in Words texts` : null].filter(Boolean).join(' · ') }) : null,
      ];
      if (!w.own) kids.push(hookRow(w, s));
      return block('Your record', kids, { cls: 'record journey-wrap' });
    }
    function hookRow(w, s) {
      const inp = h('input', { class: 'field sm', maxlength: '140', placeholder: 'My hook: a memory aid in your own words', 'aria-label': 'My hook', value: s.hook || '' });
      const save = h('button', { type: 'button', class: 'btn sm', text: 'Save hook', onclick: async () => {
        try { await UI.api(`/words/${encodeURIComponent(w.slug)}/hook`, { method: 'PUT', body: { text: inp.value.trim() } }); toast(inp.value.trim() ? 'Hook saved · it shows on every card back' : 'Hook removed'); }
        catch (e) { if (!e.offline) toast(e.status === 422 ? cap(e.message) : 'Not saved. Try again.'); }
      } });
      inp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); save.click(); } });
      return h('div', { class: 'hook' }, inp, save);
    }
    function ownBlock(w) {
      return block('My word', [w.notes ? h('p', { class: 'line', text: w.notes }) : null, w.source ? h('p', { class: 'help', text: w.source }) : null,
        h('div', { class: 'acts', style: 'display:flex;gap:10px;margin-top:6px' },
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
        foot.replaceChildren(...[covered ? h('button', { type: 'button', class: 'btn', onclick: uncover }, 'Show', h('span', { class: 'kbd', text: 'Space' })) : null, h('span', { class: 'grow' }),
          h('button', { type: 'button', class: 'btn', onclick: () => grade(false) }, 'Don’t know', h('span', { class: 'kbd', text: '1' })),
          h('button', { type: 'button', class: 'pill sm', onclick: () => grade(true) }, 'Know', h('span', { class: 'kbd', text: '2' }))].filter(Boolean));
        return;
      }
      const lookalikes = (w.confusions || []).map(c => c.other).concat((w.lookalikes || []).map(l => l.word));
      const more = h('button', { type: 'button', class: 'btn icon', 'aria-label': 'More', 'aria-haspopup': 'menu' }, ic('more'));
      more.addEventListener('click', () => UI.menu(more, [{ label: 'Reset progress', onClick: resetProgress }], { align: 'end' }));
      const cardsHere = h('button', { type: 'button', class: w.sample ? 'btn' : 'pill sm', text: 'Flashcards from here',
        onclick: () => startWords({ mode: 'cards', deck: { source: 'words', words: (list.length ? list : [w.slug]).slice(0, 200), start: w.slug }, order: 'az', count: Math.min(200, list.length || 1) }) });
      foot.replaceChildren(...[
        w.sample && !w.own ? (UI.verb ? UI.verb('twin', { count: 10, primary: true, subject: 'rw', onClick: () => practise10(w) }) : h('button', { type: 'button', class: 'pill sm', text: 'Practise 10 in context', onclick: () => practise10(w) })) : null,
        cardsHere,
        lookalikes.length ? h('button', { type: 'button', class: 'quiet', text: 'Quiz it with its lookalikes', onclick: async () => {
          const ix = await index().catch(() => null);
          const slugs = [w.slug, ...lookalikes.map(x => ix && ix.byWord.get(String(x).toLowerCase())).filter(Boolean).map(x => x.slug)];
          quizStart({ source: 'words', words: [...new Set(slugs)] }, 6);
        } }) : null,
        h('span', { class: 'grow' }), more].filter(Boolean));
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
      if (i >= 0 && i < list.length - 1) go(list[i + 1], { covered: true }); else load();
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
        field('pos', 'Part of speech', h('select', { class: 'field' }, ['', 'n.', 'v.', 'adj.', 'adv.', 'phrase'].map(p => h('option', { value: p, selected: (pre.pos || '') === p ? true : null, text: p ? POS[p] : '—' })))),
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
      let r;
      try { r = await UI.api(editing ? `/words/mine/${encodeURIComponent(pre.id)}` : '/words/mine', { method: editing ? 'PUT' : 'POST', body: b }); }
      catch (e) {
        if (e.status === 409) {
          const id = e.detail && e.detail.existing_id;
          msg.append(`You already have “${b.word}”. `, id ? h('button', { type: 'button', class: 'quiet', text: 'Edit it', onclick: () => { sh.close(); word.open(id); } }) : null);
          return false;
        }
        throw new Error(e.status === 400 || e.status === 422 ? cap(e.message) : 'Not saved. Try again.');
      }
      if (r && r.library_slug && !r.id) {
        msg.append(`“${b.word}” is in the library. `, h('button', { type: 'button', class: 'btn sm', text: 'Save that one', onclick: async () => {
          try { await UI.api(`/words/${encodeURIComponent(r.library_slug)}/save`, { method: 'POST', body: { on: true } }); toast(`Saved “${b.word}” from the library`); sh.close(); dispatch(); }
          catch (e) { if (!e.offline) toast('Not saved. Try again.'); }
        } }));
        return false;
      }
      toast(editing ? `Saved “${b.word}”` : `Added “${b.word}” to ${b.list}`);
      dispatch();
      if (again) { f.word.value = ''; f.meaning.value = ''; f.example.value = ''; f.same.value = ''; f.opposite.value = ''; f.notes.value = ''; f.word.focus(); return false; }
      return true;
    }
    const dispatch = () => { try { doc.dispatchEvent(new CustomEvent('satf:words', { detail: { added: true } })); } catch (_) {} };
    const sh = UI.sheet({ title: editing ? `Edit “${pre.word}”` : 'Add a word', size: 'm', body,
      actions: [{ label: 'Cancel', quiet: true }, ...(editing ? [] : [{ label: 'Save and add another', onClick: () => save(true) }]), { label: 'Save', primary: true, onClick: () => save(false) }] });
    setTimeout(() => (pre.word ? f.meaning : f.word).focus(), 30);
    return sh;
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
    return bringText();
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
    const side = h('div', {});
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
        hits.size ? h('div', { class: 'wchips', style: 'margin-top:8px' },
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
    const grid = h('div', { style: 'display:grid;grid-template-columns:1fr auto auto;gap:8px;align-items:center' },
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

  Object.assign(UI, { wordsTabs, todayWords, wordsFinish, word, startWords, addWord, gloss, speak, bringWords });
})();
