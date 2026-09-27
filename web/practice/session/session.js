/* ============================================================================
   SAT Freshman -- the practice session, /practice/session/?id=ID (spec 3.3 part 2,
   practice.md P1-P25). One GET /api/drill/{id}; UI.runner (F3) draws the set and
   this file wires its callbacks to the session endpoints:
     load  GET /q/{qid} for a served slot, POST /next at the frontier
     check POST /answer (retry's Show answer: POST /reveal); the verdict's `next`
           preview is preloaded and committed with POST /time {ms: 0} when shown
     time  POST /time (keepalive) whenever the runner leaves a question
     strike, notes, marks, flag, pause, resume, more, hint, why
   A finished set opens on the Summary (2.11); ?print=1 is the print view (2.12);
   ?q=TEMPLATE:SEED starts a one-question set and replaces the URL.
   ========================================================================== */
(() => {
  const h = UI.h, $ = s => document.querySelector(s);
  const url = new URLSearchParams(location.search);
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const icon = (name, size = 18) => h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.svg(UI.ICON[name] || UI.ICON.dot, size) });
  const pct = x => (x === null || x === undefined ? '—' : `${Math.round(x * 100)}%`);
  const mmss = ms => UI.mmss(Math.round((ms || 0) / 1000));
  const cap = t => (t ? t[0].toUpperCase() + t.slice(1) : '');
  const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + 's'}`;
  const when = iso => { try { return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }); } catch (_) { return ''; } };
  const day = iso => { try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }); } catch (_) { return ''; } };
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const topicName = t => (UI.TOPIC[t] || {}).short || t;
  const api = (path, o) => UI.api(path, o);
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  // hide_timer and open_explanations are not server prefs (§2.7): this viewer's, in localStorage
  const LOCAL_PREFS = 'satf.session.prefs';
  const SERVER_PREFS = new Set(['first_tap', 'option_reasons', 'show_stopwatch', 'pace_alert', 'calc_mode', 'confidence', 'text']);

  const runHost = $('#run'), view = $('#view');
  let sid = url.get('id');
  let st = null, run = null, total = null, ending = false, exhausted = false;
  let ids = [];                        // qid per slot, in served order
  const answered = new Set();          // qids with an answer on the server
  let frontier = null;                 // a pending POST /next (a skip already asked for it)
  // the stopwatch: /answer adds its ms and /time adds each visit, so each slot sends only
  // what the server does not have yet (counted: the runner's total, sent: the server's)
  const counted = [], sent = [];
  let closed = false;
  const challenge = () => st && st.kind === 'challenge';
  const endMode = () => st && st.feedback === 'end';
  const drillPath = p => `/drill/${encodeURIComponent(sid)}${p || ''}`;

  /* ---------------- states */
  function state(text, extra = []) {
    runHost.replaceChildren();
    view.hidden = false;
    view.replaceChildren(h('div', { class: 'ps-state', role: 'alert' }, h('p', { text }),
      h('div', { class: 'acts' }, h('a', { class: 'pill', href: '/practice/', text: 'Back to Practice' }), extra)));
  }
  function skeleton() {
    const box = h('div', { class: 'ps-skel', 'aria-busy': 'true', 'aria-label': 'Loading the set' });
    if (UI.skel) { UI.skel(box, 'lines:3'); for (let k = 0; k < 4; k++) UI.skel(box, { w: '100%', h: 56, r: 12 }); }
    runHost.replaceChildren(box);
  }
  async function create(body, suffix = '') {
    try {
      const s = await api('/drill', { method: 'POST', body: Object.assign({ subject: (st && st.subject) || 'math' }, body) });
      location.href = `/practice/session/?id=${encodeURIComponent(s.id)}${suffix}`;
    } catch (e) {
      const d = e && e.detail;
      toast(`Couldn’t start it: ${(d && (d.reason || d.detail)) || e.message}`);
    }
  }

  /* ---------------- the server's question, as UI.workspace reads it */
  // the runner's mark styles and the notes table's (api_notes.STYLES) name the same looks differently
  const TO_SERVER = { ask: 'box', given: 'highlight', ignore: 'strike', under: 'underline' };
  const FROM_SERVER = Object.fromEntries(Object.entries(TO_SERVER).map(([a, b]) => [b, a]));
  const marksIn = list => (list || []).map(m => Object.assign({}, m, { style: FROM_SERVER[m.style] || m.style }));
  const marksOut = list => (list || []).map(m => Object.assign({}, m, { style: TO_SERVER[m.style] || m.style }));
  const whyText = w => (!w ? null : typeof w === 'string' ? w : w.detail || w.text || null);
  function mapQ(q, d = {}) {
    if (!q) return null;
    return Object.assign({}, q, {
      name: q.type_name || q.name, number: q.n, why: challenge() ? null : whyText(q.why),
      template: d.template || q.template, seed: d.seed ?? q.seed, subject: (st && st.subject) || 'math',
    });
  }
  function detailsOf(d, q, fb) {
    const hist = d.type_history || [];
    const right = hist.filter(x => x.correct).length;
    const tier = TIER[q.difficulty] || cap(q.difficulty || '');
    const lvl = q.level ? ` · level ${q.level} of 7${q.rough ? ', rough' : ', measured'}` : ' · level not measured yet';
    const odds = q.odds && Number.isFinite(q.odds.you) ? ` · your odds were ${pct(q.odds.you)}` : '';
    const crowd = fb && fb.crowd;
    return {
      difficulty: tier ? `${tier}${lvl}${odds}` : null,
      you: hist.length ? `${hist.length} answered · ${right} right · last ${day(hist[0].at)}` : 'First time',
      everyone: crowd && crowd.n >= 20 && Number.isFinite(crowd.rate) ? `${pct(crowd.rate)} right first try${crowd.top ? ` · most common mistake: ${crowd.top.label || crowd.top}` : ''}` : null,
      formula: fb && Array.isArray(fb.formula) ? fb.formula.map(f => f.text).filter(Boolean).join(' · ') || null : null,
      open: !challenge() || !!(st.can && st.can.permalink),
    };
  }
  function itemOf(d) {
    const q = mapQ(d.question, d);
    const it = { q, why: q.why, marks: marksIn(d.marks), note: d.note || '', attempts: (d.type_history || []).length,
      state: { struck: d.strikes || [] } };
    const given = d.given;
    if (d.feedback) it.fb = Object.assign({ given }, d.feedback);
    else if (given !== null && given !== undefined && given !== '') {
      if (endMode()) Object.assign(it.state, Number.isInteger(given) ? { selected: given } : { value: String(given) }, { saved: given });
    }
    // retry: the wrong tries so far come back, so the tries left are right after a reload
    const tries = (d.tries || []).filter(t => t.correct === false && !t.cover);
    if (!it.fb && tries.length && st.feedback === 'retry') it.state.tries = tries.map(t => ({ given: t.given, reason: t.mistake || null }));
    it.details = detailsOf(d, q, it.fb);
    if (d.feedback || (given !== null && given !== undefined && given !== '')) answered.add(q.id);
    return it;
  }
  // until S10's flag endpoint lands, a mark is kept here too (state reads the flags table)
  const localMarks = () => new Set(ls.get(`satf.marks.${sid}`, []));
  const cellOf = s => ({ status: s.status, flag: !!s.marked || localMarks().has(s.id), note: !!s.has_note, tier: s.difficulty, level: s.level, topic: s.topic,
    topic_name: topicName(s.topic), ms: s.ms || 0, budget_ms: s.budget_ms, conf: s.conf, repair: !!s.repair });

  function setTitle() {
    if (!st) return 'Practice';
    if (challenge()) return 'Daily challenge';
    const pool = st.pool;
    if (pool === 'marked' || pool === 'saved') return 'Marked for review';
    if (pool === 'redo') return 'Missed questions';
    const names = (st.topics || []).map(topicName);
    if (!names.length) return st.total === 1 ? 'One question' : 'Practice';
    return names.length > 1 ? `${names[0]} + ${names.length - 1}` : names[0];
  }

  /* ---------------- boot */
  async function boot() {
    const permalink = url.get('q');
    if (permalink && !sid) {
      skeleton();
      try {
        const s = await api('/drill', { method: 'POST', body: { item: permalink, count: 1, source: 'map' } });
        sid = s.id;
        history.replaceState(null, '', `/practice/session/?id=${encodeURIComponent(sid)}`);
      } catch (e) { return state(e.status === 422 ? 'That question link is not valid.' : 'That question didn’t load.'); }
    }
    if (!sid) return state('That set does not exist.');
    if (!url.get('print')) skeleton();
    try { st = await api(drillPath()); }
    catch (e) {
      if (e.status === 404) return state('That set does not exist.');
      if (e.status === 403) return state('This set belongs to a different device code.', [h('a', { class: 'btn', href: '/me/', text: 'Use that code here' })]);
      return state(e.offline ? 'You’re offline. The set will load when you’re back.' : 'That set didn’t load.', [h('button', { type: 'button', class: 'btn', text: 'Try again', onclick: () => location.reload() })]);
    }
    ids = (st.served || []).map(s => s.id);
    total = st.total ?? null;
    if (url.get('print')) return printView();
    if (st.finished) return endSet(true);
    start();
  }

  /* ---------------- the runner */
  async function start() {
    let prefs = {};
    try { prefs = Object.assign({}, await UI.prefs()); } catch (_) {}
    Object.assign(prefs, ls.get(LOCAL_PREFS, {}));
    const cells = (st.served || []).map(cellOf);
    (st.served || []).forEach((s, k) => { counted[k] = sent[k] = s.ms || 0; });
    (st.served || []).forEach(s => { if (!['unanswered', 'skipped', 'future'].includes(s.status)) answered.add(s.id); });
    if (total !== null) for (let k = cells.length; k < total; k++) cells.push({ status: 'future' });
    const pos = ls.get(`satf.pos.${sid}`, null);
    const srv = ids.indexOf(st.at || st.current);
    const at = Number.isInteger(pos) && pos >= 0 && pos < Math.max(1, ids.length) ? pos : srv >= 0 ? srv : Math.max(0, ids.length - 1);
    const can = st.can || {};
    document.title = `${setTitle()} · SAT Freshman`;
    runHost.replaceChildren();
    run = UI.runner(runHost, {
      mode: 'practice', feedback: st.feedback || 'instant', sid, title: setTitle(), short: null, cells, total, at,
      clock: st.timed ? { secondsLeft: st.seconds_left ?? 0, paused: !!st.paused } : { elapsed: st.elapsed || 0 },
      pausable: !!(can.pause && st.timed && !challenge()), challenge: challenge(), resumed: st.answered > 0,
      prefs, confActive: !!st.conf_active, hideSkill: st.hide_skill ? 'Mix-up' : false, source: 'drill',
      workspace: {
        coverTool: !challenge(),
        onHint: can.hint ? async () => api(drillPath('/hint'), { method: 'POST', body: { question_id: ids[run.at] } }) : null,
        onTrap: can.more ? async (i, reason) => more({ question_id: ids[run.at], want: String(reason || '').slice(0, 300) }) : null,
        onCause: kind => api(drillPath('/why'), { method: 'POST', body: { question_id: ids[run.at], kind }, quiet: true }).catch(() => toast('Not saved. Try again.')),
        onLadder: can.more ? () => more({ question_id: ids[run.at], ladder: true }) : null,
        onOwn: (own, meta) => check(run.at, null, Object.assign({}, meta, { own })),
      },
      actions: can.more ? {
        source: 'drill', session: sid, axes: ['easier', 'harder', 'grid', 'ask'],
        more: (axis, n) => twinAxis(axis, n),
      } : null,
      more: () => moreItems(),
      on: {
        load: (i, how) => load(i, how),
        check: (i, a, meta) => check(i, a, meta),
        show: (i, it) => { const id = it && it.q && it.q.id; if (id && !ids.includes(id)) commit(i, id); },
        time: (i, ms) => {
          counted[i] = (counted[i] || 0) + Math.max(0, Math.round(ms));
          const add = counted[i] - (sent[i] || 0);
          if (!ids[i] || closed || add <= 0) return;
          sent[i] = counted[i];
          api(drillPath('/time'), { method: 'POST', body: { question_id: ids[i], ms: add }, keepalive: true, quiet: true }).catch(() => {});
        },
        strike: (i, k, v) => { if (ids[i]) api(drillPath('/strike'), { method: 'POST', body: { question_id: ids[i], choice: k, on: !!v }, quiet: true }).catch(() => {}); },
        mark: (i, v) => mark(ids[i], v),
        note: (i, text) => api('/notes', { method: 'POST', body: { session: sid, question_id: ids[i], note: text } }),
        marks: (i, m) => { api('/notes', { method: 'POST', body: { session: sid, question_id: ids[i], marks: marksOut(m) }, quiet: true }).catch(() => toast('Highlight not saved. Try again.')); },
        skip: i => { if (i === ids.length - 1) frontier = api(drillPath('/next'), { method: 'POST', body: { skip: true } }); },
        pref: (key, v) => pref(key, v),
        pause: () => api(drillPath('/pause'), { method: 'POST' }),
        resume: () => api(drillPath('/resume'), { method: 'POST' }),
        exit: how => exit(how),
        finish: () => endSet(),
      },
    });
  }

  async function load(i, how) {
    if (i < ids.length) return itemOf(await api(drillPath(`/q/${encodeURIComponent(ids[i])}`)));
    // the frontier: a new question. End mode moves on freely, so an unanswered one is set aside.
    const skip = i > 0 && !answered.has(ids[i - 1]) && how !== 'start';
    const r = await (frontier || api(drillPath('/next'), { method: 'POST', body: { skip } }));
    frontier = null;
    if (r.done || !r.question) {
      exhausted = !!r.exhausted;
      setTimeout(() => endSet(), 0);
      return new Promise(() => {});                 // the summary replaces the runner
    }
    const q = r.question;
    const known = ids.indexOf(q.id);
    if (known >= 0 && known !== i) { setTimeout(() => run.go(known, 'jump'), 0); return new Promise(() => {}); }
    ids[i] = q.id;
    if (r.total !== undefined && r.total !== null && total !== null && r.total > total) grow(r.total);
    return itemOf(await api(drillPath(`/q/${encodeURIComponent(q.id)}`)));
  }
  // a preloaded preview goes into served when it shows (P23)
  function commit(i, qid) {
    ids[i] = qid;
    api(drillPath('/time'), { method: 'POST', body: { question_id: qid, ms: 0 }, quiet: true }).catch(() => {});
  }
  function grow(to) {
    if (total === null || !run) return;
    while (total < to) { run.addSlot({}); total++; }
  }

  async function check(i, a, meta) {
    const qid = ids[i];
    try {
      if (meta.show) return await api(drillPath('/reveal'), { method: 'POST', body: { question_id: qid } });
      const conf = meta.conf && meta.conf !== 'auto' ? meta.conf : null;
      const spent = Math.round(meta.ms || 0), add = Math.max(0, spent - (sent[i] || 0));
      const body = { question_id: qid, answer: a, ms: add || null, conf, guess: conf === 'guess', hints: Math.min(5, meta.hints || 0) };
      if (meta.own) { body.own = String(meta.own).slice(0, 40); if (a === null) delete body.answer; }
      const fb = await api(drillPath('/answer'), { method: 'POST', body });
      sent[i] = Math.max(sent[i] || 0, spent);
      if (fb.saved || fb.final !== false) answered.add(qid);
      if (fb.total !== undefined && fb.total !== null) grow(fb.total);
      // G9 / P23: the next question came with the verdict; render it now, commit it when shown
      if (fb.next && i === ids.length - 1 && (total === null || i + 1 < total) && run) run.preload(i + 1, itemOf({ question: fb.next, marks: [], strikes: [] }));
      return fb;
    } catch (e) {
      const d = e && e.detail;
      if (e.status === 409 && !(d && /paused/i.test(JSON.stringify(d)))) { endSet(); }
      throw e;
    }
  }

  async function more(body) {
    const r = await api(drillPath('/more'), { method: 'POST', body });
    if (r.total !== undefined && r.total !== null) grow(r.total);
    if (run) run.discardPreload(run.at + 1);
    toast(body.ladder ? 'Next: Learn this type, step by step' : 'Next: one like this, with new numbers');
    return r;
  }
  function twinAxis(axis, n = 1) {
    const qid = ids[run.at];
    const q = (run.ws && run.ws.q) || {};
    if (axis === 'print') return create({ source: 'worksheet', templates: q.template ? [q.template] : [], count: 10, feedback: 'end', timing: 'off' }, '&print=1');
    if (axis === 'learn') return more({ question_id: qid, ladder: true });
    return more({ question_id: qid, axis: ['same', 'easier', 'harder', 'grid', 'ask'].includes(axis) ? axis : 'same', n: Math.max(1, Math.min(3, n)) });
  }

  // Mark for review: Review's flag endpoint (S10); /api/saved until it lands
  async function mark(qid, on) {
    try { await api(`/session/${encodeURIComponent(sid)}/flag`, { method: 'POST', body: { question_id: qid, on: !!on }, quiet: true }); }
    catch (e) {
      if (e.status !== 404 && e.status !== 405) throw e;
      await api('/saved', { method: 'POST', body: { session: sid, question_id: qid, on: !!on } });
      const m = localMarks();
      if (on) m.add(qid); else m.delete(qid);
      ls.set(`satf.marks.${sid}`, [...m]);
    }
  }

  function pref(key, v) {
    if (SERVER_PREFS.has(key)) { if (UI.prefs && UI.prefs.set) UI.prefs.set({ [key]: v }).catch(() => toast('Setting not saved.')); return; }
    const local = ls.get(LOCAL_PREFS, {});
    local[key] = v;
    ls.set(LOCAL_PREFS, local);
  }

  function copySheet(kind) {
    const retake = kind === 'retake';
    const clean = h('input', { type: 'checkbox', checked: true });
    UI.sheet({ title: retake ? 'Start over with these exact questions?' : 'Rematch: same types, new numbers?', size: 's', body: b => {
      b.append(h('p', { text: retake ? 'Starts a new copy of this set with the same questions. It tests memory as much as skill. This one stays in your history.'
        : 'The same types in the same order, with new numbers. We compare the two question by question.' }));
      b.append(h('label', { class: 'check' }, clean, retake ? 'Start clean: hide my highlights, notes, strikes and rules on this copy' : 'Start clean: hide my notes and highlights on this copy'));
    }, actions: [{ label: 'Cancel', quiet: true }, { label: retake ? 'Start over' : 'Rematch', primary: true,
      onClick: () => { create({ [kind]: sid, clean: clean.checked, source: retake ? 'builder' : 'rematch' }); } }] });
  }
  async function share() {
    try {
      const r = await api('/sets', { method: 'POST', body: { kind: 'set', session: sid, cfg: { fresh: true } } });
      UI.copyText(r.url ? new URL(r.url, location.origin).href : `${location.origin}/practice/?share=${r.code}`, { toast: 'Link copied: each friend gets their own twins' });
    } catch (e) { toast(`Couldn’t share it: ${e.message}`); }
  }
  function moreItems() {
    if (challenge()) return [];
    return [
      { label: 'Rematch: same types, new numbers', onClick: () => copySheet('rematch') },
      { label: 'Start over with these exact questions (tests memory)', onClick: () => copySheet('retake') },
      { label: 'New set, same settings', onClick: () => create({ again: sid, source: 'builder' }) },
      { label: 'Share this set', onClick: () => share() },
      { label: 'Print this set', onClick: () => { location.href = `/practice/session/?id=${encodeURIComponent(sid)}&print=1`; } },
    ];
  }

  async function exit(how) {
    if (how === 'end') return endSet();
    if (how === 'quiet') {               // nothing answered: the set is dropped from your lists
      try { await api(drillPath('/finish'), { method: 'POST', quiet: true, keepalive: true }); } catch (_) {}
    }
    if (how === 'pause') { try { await api(drillPath('/pause'), { method: 'POST' }); } catch (_) {} }
    location.href = '/practice/';
  }

  async function endSet(already) {
    if (ending) return;
    ending = true;
    let r;
    try { r = await api(drillPath('/finish'), { method: 'POST' }); }
    catch (e) {
      ending = false;
      if (already) return state('The summary didn’t load.', [h('button', { type: 'button', class: 'btn', text: 'Try again', onclick: () => location.reload() })]);
      toast(e.offline ? 'You’re offline. Finish again when you’re back.' : 'Couldn’t finish. Try again.');
      return;
    }
    if (r.deleted) { location.href = '/practice/'; return; }
    closed = true;
    if (run) { try { run.destroy(); } catch (_) {} run = null; }
    if (!already) { try { st = await api(drillPath()); } catch (_) {} }
    summary(r);
  }

  /* ---------------- 2.11 Summary */
  function summary(r) {
    runHost.replaceChildren();
    document.title = `Set complete · ${setTitle()} · SAT Freshman`;
    const lm = localMarks();
    const qs = (r.questions || []).map(q => (lm.has(q.id) ? Object.assign({}, q, { marked: true }) : q));
    const endless = st.total === null || st.total === undefined;
    const counts = {};
    qs.forEach(q => { counts[q.status] = (counts[q.status] || 0) + 1; });
    const col = h('div', { class: 'psum' });
    view.hidden = false;
    view.replaceChildren(h('header', { class: 'sm-top' },
      h('a', { class: 'sm-exit', href: '/practice/', 'aria-label': 'Exit' }, icon('x', 20), h('span', { text: 'Exit' })),
      h('span', { class: 'sm-title', text: setTitle() })), col);
    const sec = (title, ...kids) => h('section', { class: 'sm-sec' }, h('h2', { text: title }), kids);

    // 1. ScoreHead
    const answeredN = qs.filter(q => !['unanswered', 'skipped'].includes(q.status)).length;
    const head = h('div', { class: 'sm-head' }, h('p', { class: 'k', text: `Set complete · ${when(st.finished || new Date().toISOString())}` }));
    if (endless) head.append(h('div', { class: 'sm-score' }, h('span', { class: 'num', text: String(answeredN) }), h('span', { class: 'acc', text: `answered · ${r.right} right` })));
    else head.append(h('div', { class: 'sm-score' }, h('span', { class: 'num', text: `${r.right} / ${qs.length}` }), h('span', { class: 'acc', text: `${pct(r.accuracy)} first-try accuracy` })));
    head.append(h('p', { class: 'sm-before', text: r.before_accuracy !== null && r.before_accuracy !== undefined
      ? `Before this set: ${pct(r.before_accuracy)} first try in these skills` : 'Before this set: no first tries yet in these skills' }));
    const chips = h('div', { class: 'sm-chips' });
    (r.topics || []).forEach(t => chips.append(h('span', { class: 'chip' }, UI.glyph ? UI.glyph(t.topic) : null, h('span', { text: topicName(t.topic) }))));
    head.append(chips);
    if (exhausted || (r.exhausted)) head.append(h('p', { class: 'sm-note', text: 'We ran out of unseen questions for these settings. Widen the levels or skills to keep going.' }));
    col.append(head);

    // 2. StatTiles
    const tiles = h('div', { class: 'stats six' });
    const spent = qs.reduce((s, q) => s + (q.ms || 0), 0);
    const tile = (label, value, sub) => UI.tile(tiles, { label, value, sub });
    tile('Correct', counts.correct || 0);
    tile('Incorrect', counts.incorrect || 0);
    if (st.feedback === 'retry' || r.mixed) tile('Mixed', r.mixed || 0, 'right on a later try');
    tile('Skipped', r.skipped || 0);
    tile('Unanswered', r.unanswered || 0);
    tile('Time', UI.mmss(Math.round(spent / 1000)));
    const budgetAvg = qs.length ? qs.reduce((s, q) => s + (q.budget_ms || 0), 0) / qs.length : 0;
    tile('Per question', r.avg_ms ? mmss(r.avg_ms) : '—', budgetAvg ? `pace ${mmss(budgetAvg)}` : null);
    tile('Right but guessed', r.guessed_right || 0);
    if (r.helped) tile('Right with help', r.helped);
    col.append(tiles);

    // what else this set shows (P3 P5 P6 P7 P8 P10 P11 P12 P13 P16 P17 P19), one line each
    const extra = [];
    const line = (b, text) => extra.push(h('li', {}, h('b', { text: `${b}: ` }), text));
    (r.moved || []).filter(m => m.rate_after !== null && m.rate_after !== undefined).forEach(m =>
      line(`Moved · ${topicName(m.topic)}`, `first try ${pct(m.rate_before)} → ${pct(m.rate_after)}${m.gain_after !== null && m.gain_after !== undefined ? ` · ≈ +${Math.round(m.gain_after)} pts on the table` : ''}`));
    if (r.expected) line('Expected vs got', `expected ${r.expected.expected}, got ${r.expected.got} (${r.expected.above >= 0 ? '+' : ''}${r.expected.above})`);
    const cal = r.calibration && r.calibration.conf;
    if (cal && r.calibration.tagged) line('Calibration', Object.entries(cal).filter(([k, v]) => k !== 'untagged' && v.right + v.wrong).map(([k, v]) => `${cap(k)} ${v.right}/${v.right + v.wrong}`).join(' · '));
    const causes = Object.entries(r.causes || {}).filter(([, n]) => n);
    if (causes.length) line('Why you missed', causes.map(([k, n]) => `${cap(k)} ${n}`).join(' · '));
    if (r.dodged && r.dodged.offered) line('Traps on offer', `${r.dodged.dodged} of ${r.dodged.offered} dodged`);
    if (r.strikes && r.strikes.n) line('Strikes', `${r.strikes.n} struck${r.strikes.struck_key ? ` · the key struck ${r.strikes.struck_key}×` : ''}`);
    if (r.retrieval && r.retrieval.reviews) line('Reviews', `${r.retrieval.held} of ${r.retrieval.reviews} held${r.retrieval.slipped.length ? ` · slipped: ${r.retrieval.slipped.join(', ')}` : ''}`);
    if (r.final) line('Final round', `${r.final.right} of ${r.final.n} right${r.final.still_open.length ? ` · still open: ${r.final.still_open.join(', ')}` : ''}`);
    (r.mixup || []).forEach(m => line(`Mix-up · ${m.name}`, `${m.right}/${m.asked}${m.usual !== null ? ` · usually ${pct(m.usual)}` : ''}`));
    if (r.calc && (r.calc.on || r.calc.without) && r.calc.on) line('Desmos', `${r.calc.right_with}/${r.calc.on} right with it · ${r.calc.right_without}/${r.calc.without} without`);
    if (r.covered && r.covered.n) line('Solved first', `${r.covered.right} of ${r.covered.n} right with the choices covered`);
    (r.official || []).forEach(o => line(`Twin of CB ${o.cb_id}`, `${o.right}/${o.twins} right`));
    if (r.passes) line('Two passes', `first pass ${r.passes.one.right}/${r.passes.one.answered} · second pass ${r.passes.two.right}/${r.passes.two.answered}`);
    if (r.head && r.head.closed) line('Mistakes closed', String(r.head.closed));
    if (extra.length) col.append(sec('What this set moved', h('ul', { class: 'sm-lines' }, extra)));
    if ((r.slots || []).length) {
      col.append(sec('Then → Now', h('ul', { class: 'sm-lines' }, r.slots.map(s => h('li', {}, h('b', { text: `Q${s.n} · ${s.type_name || ''}: ` }),
        `${cap(s.then.status)}${s.then.ms ? ` ${mmss(s.then.ms)}` : ''} → ${cap(s.now.status || '')}${s.now.ms ? ` ${mmss(s.now.ms)}` : ''}${s.change ? ` · ${s.change}` : ''}`)))));
    }

    // 3. By skill
    const byType = r.by_type || [];
    const skillRows = h('div', { class: 'sm-rows' });
    (r.topics || []).forEach(t => {
      const inTopic = qs.filter(q => q.topic === t.topic && q.ms);
      const avg = inTopic.length ? inTopic.reduce((s, q) => s + q.ms, 0) / inTopic.length : 0;
      const before = Math.max(0, Math.min(1, t.before || 0)), after = Math.max(0, Math.min(1, t.after || 0));
      const wBefore = UI.masteryWord(t.before, 1), wAfter = UI.masteryWord(t.after, t.asked);
      skillRows.append(h('div', { class: 'sm-row' },
        UI.glyph ? h('span', {}, UI.glyph(t.topic)) : h('span'),
        h('span', { text: t.name || topicName(t.topic) }),
        h('span', { class: 'n', text: `${t.right} / ${t.asked}` }),
        h('span', { class: 't', text: avg ? `avg ${mmss(avg)}` : '—' }),
        h('span', { class: 'sm-mb' }, h('span', { class: 'bar2', role: 'img', 'aria-label': `${wBefore} to ${wAfter}` },
          h('i', { class: 'g', style: `width:${Math.max(before, after) * 100}%` }), h('i', { class: 'a', style: `width:${after * 100}%` })),
          h('span', { class: 'w', text: wBefore === wAfter ? wAfter : `${wBefore} → ${wAfter}` })),
        h('a', { class: 'btn sm', href: `/practice/?skills=${encodeURIComponent(t.topic)}`, text: 'Practise' })));
    });
    const typesBox = byType.length ? h('details', { class: 'sm-types' }, h('summary', { text: `By question type · ${byType.length}` }),
      h('ul', {}, byType.map(t => h('li', { text: `${t.name} · ${t.right} / ${t.asked} · ${mmss(t.asked ? t.ms / t.asked : 0)}` })))) : null;
    if ((r.topics || []).length) col.append(sec('By skill', skillRows, typesBox));

    // 4. By difficulty
    const diff = h('div', { class: 'sm-diff' });
    ['easy', 'medium', 'hard'].forEach(k => {
      const d = (r.by_difficulty || {})[k];
      if (!d || !d.asked) return;
      diff.append(h('div', { class: 'r' }, h('span', { text: TIER[k] }), h('span', { class: 't', text: `${d.right} / ${d.asked}` }),
        h('span', { class: 'fill', role: 'img', 'aria-label': `${d.right} of ${d.asked} right` }, h('i', { style: `width:${(d.right / d.asked) * 100}%` })),
        h('span', { class: 't', text: mmss(d.ms / d.asked) })));
    });
    const lv = r.levels_seen || [];
    if (diff.children.length) col.append(sec('By difficulty', diff, lv.length ? h('p', { class: 'sm-legend', text: `Levels seen: ${lv[0]}${lv.length > 1 ? `–${lv[lv.length - 1]}` : ''} (${r.measured_seen || 0} measured)` }) : null));

    // 5. Time per question
    const timed = qs.filter(q => q.ms);
    if (timed.length) {
      const over = timed.filter(q => q.budget_ms && q.ms > q.budget_ms).length;
      const ms = timed.map(q => q.ms);
      const box = h('div', { class: 'sm-chart' });
      const tsec = sec('Time per question', box, h('p', { class: 'sm-legend', text: `Over budget ${over} · fastest ${mmss(Math.min(...ms))} · slowest ${mmss(Math.max(...ms))}` }),
        (r.time_sinks || []).length ? h('p', { class: 'sm-legend', text: `Time sinks · ${r.time_sinks.length}` }) : null);
      col.append(tsec);
      if (UI.barChart) {
        try {
          UI.barChart(box, qs.map(q => ({ key: String(q.n), label: String(q.n), value: Math.round((q.ms || 0) / 1000), budget: q.budget_ms ? Math.round(q.budget_ms / 1000) : null,
            status: q.budget_ms && q.ms > q.budget_ms ? 'over' : null, tip: `Q${q.n} · ${mmss(q.ms)}${q.budget_ms ? ` / ${mmss(q.budget_ms)}` : ''}` })),
          { unit: 's', labels: 'label', height: 160, label: 'Time per question', budget: true });
        } catch (e) { console.error(e); }
      }
    }

    // 6. Mistakes
    const opened = r.opened || [], closed = r.closed || [];
    if (opened.length || closed.length) {
      const m = h('div', { class: 'sm-mist' });
      if (opened.length) m.append(h('div', {}, h('h3', { text: `Opened · ${opened.length}` }), h('ul', {}, opened.map(o => h('li', {},
        h('span', { text: cap(o.label) }), h('span', { class: 's', text: topicName(o.topic) }),
        h('button', { type: 'button', class: 'btn sm', text: 'Fix now', onclick: () => create({ pool: 'mistakes', templates: [o.template], source: 'mistakes' }) }))))));
      if (closed.length) m.append(h('div', {}, h('h3', { text: `Fixed · ${closed.length}` }), h('ul', {}, closed.map(o => h('li', {}, icon('check', 16), h('span', { text: cap(o.label) }), h('span', { class: 's', text: topicName(o.topic) }))))));
      m.append(h('a', { class: 'link', href: '/mistakes/', text: 'Still open from before · see Mistakes' }));
      col.append(sec('Mistakes', m));
    }

    // 7. ReviewList
    if (qs.length) col.append(reviewList(qs));

    // 8. NextActions
    col.append(nextActions(r, qs));
  }

  function reviewList(qs) {
    const slow = q => q.budget_ms && q.ms > q.budget_ms;
    const F = {
      all: () => true, incorrect: q => q.status === 'incorrect', mixed: q => q.status === 'mixed', marked: q => q.marked,
      slow, guessed: q => q.guess || q.conf === 'guess', skipped: q => q.status === 'skipped' || q.status === 'unanswered', note: q => q.has_note,
    };
    const LABEL = { all: 'All', incorrect: 'Incorrect', mixed: 'Mixed', marked: 'Marked', slow: 'Slow', guessed: 'Guessed', skipped: 'Skipped', note: 'Has note' };
    const rows = qs.map((q, i) => {
      const b = h('button', { type: 'button', class: 'sm-rl-row', 'data-status': q.status },
        UI.cell(q.status, q.n ?? i + 1, { static: true, flag: q.marked || null, note: q.has_note || null, tier: q.difficulty, repair: q.repair || null }),
        h('span', { class: 'ty' }, UI.glyph ? UI.glyph(q.topic) : null, h('span', { text: q.type_name || topicName(q.topic) })),
        h('span', { class: 'chip sm', text: `${TIER[q.difficulty] || ''}${q.level ? ` · L${q.level}` : ''}` }),
        h('span', { class: 't', text: q.ms ? mmss(q.ms) : '—' }),
        h('span', { class: 'm', text: q.mistake ? cap(q.mistake) : '—' }),
        h('span', { class: 'fl', text: [q.marked ? 'Marked' : '', q.has_note ? 'Note' : ''].filter(Boolean).join(' · ') }));
      b.addEventListener('click', () => openReview(qs, i));
      return b;
    });
    const list = h('div', { class: 'sm-rl', role: 'list' }, rows);
    const opts = Object.keys(F).map(k => ({ value: k, label: LABEL[k], n: qs.filter(F[k]).length })).filter(o => o.value === 'all' || o.n || ['incorrect', 'skipped'].includes(o.value));
    const segHost = h('div');
    const apply = v => { rows.forEach((row, i) => { row.hidden = !F[v](qs[i]); }); };
    UI.chips(segHost, opts, { value: 'all', label: 'Show', onChange: v => apply(v) });
    const incorrect = qs.filter(F.incorrect);
    const markAll = incorrect.length ? h('button', { type: 'button', class: 'quiet', text: 'Mark all incorrect for review', onclick: async e => {
      e.currentTarget.disabled = true;
      try { for (const q of incorrect) await mark(q.id, true); incorrect.forEach(q => { q.marked = true; }); toast(`${plural(incorrect.length, 'question')} marked for review`); }
      catch (_) { toast('Not saved. Try again.'); e.currentTarget.disabled = false; }
    } }) : null;
    return h('section', { class: 'sm-sec' }, h('div', { class: 'sm-rl-head' }, h('h2', { text: 'Review' }), markAll), segHost, list);
  }
  function openReview(qs, at) {
    if (!UI.review) return;
    const items = qs.map((q, i) => ({ n: q.n ?? i + 1, status: q.status, flag: q.marked, ms: q.ms, budget_ms: q.budget_ms }));
    UI.review(null, items, { mode: 'dialog', at, session: sid, title: setTitle(), hash: false, on: {
      load: async i => {
        const d = await api(drillPath(`/q/${encodeURIComponent(qs[i].id)}`));
        const it = itemOf(d);
        return { q: it.q, fb: it.fb || { given: d.given }, status: d.status, flag: d.marked, marks: marksIn(d.marks), note: d.note || '', ms: d.ms, session: sid,
          links: it.q.template ? { exact: `${location.origin}/practice/session/?q=${encodeURIComponent(`${it.q.template}:${it.q.seed}`)}` } : null };
      },
      mark: (item, on) => mark(qs[item.n - 1] ? qs[item.n - 1].id : null, on),
    } });
  }
  function nextActions(r, qs) {
    const box = h('div', { class: 'sm-next' });
    const misses = qs.filter(q => q.status === 'incorrect' || q.status === 'mixed').length;
    const prim = h('div', { class: 'primary' });
    if (challenge()) {
      prim.append(h('a', { class: 'pill', href: '/compete/', text: 'Board' }));
      if (r.contest && r.contest.rank) prim.append(h('span', { class: 'acc', text: `#${r.contest.rank} of ${r.contest.of || r.contest.n || '?'}` }));
    } else if (r.next_set) {
      const ns = r.next_set;
      prim.append(h('button', { type: 'button', class: 'pill', onclick: () => create(ns.body) }, `${ns.title} · ${plural(ns.count, 'question')} · ≈ ${ns.minutes} min`));
    } else if (r.next && (r.next.topics || []).length) {
      prim.append(h('button', { type: 'button', class: 'pill', onclick: () => create({ topics: r.next.topics, count: r.next.count || 10, source: 'coach' }) }, 'Keep going'),
        h('p', { class: 'help', text: `${r.next.topics.map(topicName).join(' · ')} · ${r.next.count || 10} questions` }));
    }
    box.append(h('h2', { text: 'Next' }), prim);
    const acts = h('div', { class: 'quiet-acts' });
    const q = (label, onClick, href) => acts.append(href ? h('a', { class: 'btn', href, text: label }) : h('button', { type: 'button', class: 'btn', text: label, onclick: onClick }));
    if (misses && !challenge()) q(`Fix my ${plural(misses, 'miss', 'misses')}`, () => create({ from_session: sid, source: 'result' }));
    if (!challenge()) {
      q('Rematch · same types, new numbers', () => copySheet('rematch'));
      q('Rematch in 3 days', async () => { try { await api(drillPath('/rematch-due'), { method: 'POST', body: { days: 3 } }); toast('It comes back in Up next in 3 days'); } catch (_) { toast('Not saved. Try again.'); } });
      q('Retake these exact questions (tests memory)', () => create({ retake: sid, clean: true, source: 'builder' }));
      q('Same settings, new questions', () => create({ again: sid, source: 'builder' }));
      q('Share this set', () => share());
      q('Print', null, `/practice/session/?id=${encodeURIComponent(sid)}&print=1`);
    }
    if (r.words_due) q(`SAT words · ${r.words_due} due`, null, '/words/');
    q('Back to Practice', null, '/practice/');
    box.append(acts);
    return h('section', { class: 'sm-sec' }, box);
  }

  /* ---------------- 2.12 Print view */
  async function printView() {
    runHost.replaceChildren();
    view.hidden = false;
    const wrap = h('div', { class: 'pv' });
    const status = h('p', { class: 'meta', text: 'Getting every question…' });
    view.replaceChildren(wrap);
    wrap.append(status);
    // a worksheet is an end-mode set left in progress: serve every slot so all of them print
    if (!st.finished && total !== null && st.feedback === 'end') {
      let guard = 0;
      while (ids.length < total && guard++ < total + 2) {
        let r;
        try { r = await api(drillPath('/next'), { method: 'POST', body: { skip: true } }); } catch (_) { break; }
        if (!r.question || r.done) break;
        if (!ids.includes(r.question.id)) ids.push(r.question.id);
      }
    }
    const details = [];
    for (const id of ids) { try { details.push(await api(drillPath(`/q/${encodeURIComponent(id)}`))); } catch (_) {} }
    const withKey = details.some(d => d.feedback);
    const include = h('input', { type: 'checkbox', checked: true, id: 'pvKey' });
    include.addEventListener('change', () => wrap.classList.toggle('nokey', !include.checked));
    const ctl = h('div', { class: 'pv-ctl' },
      h('label', { class: 'check', for: 'pvKey' }, include, 'Include answer key and explanations'),
      h('button', { type: 'button', class: 'pill', text: 'Print / Save as PDF', onclick: () => window.print() }),
      !st.finished ? h('a', { class: 'btn', href: `/practice/session/?id=${encodeURIComponent(sid)}`, text: 'Enter answers online' }) : null,
      h('a', { class: 'quiet', href: st.finished ? `/practice/session/?id=${encodeURIComponent(sid)}` : '/practice/', text: st.finished ? 'Back to the summary' : 'Back to Practice' }));
    const names = (st.topics || []).map(topicName).join(', ') || setTitle();
    const head = h('div', { class: 'pv-head' }, h('div', {}, h('h1', { text: names }), h('p', { class: 'meta', text: `${day(st.started)} · ${plural(details.length, 'question')}` })),
      h('span', { class: 'pv-name', text: 'Name ________________' }));
    const qsBox = h('div', {});
    details.forEach((d, i) => {
      const q = mapQ(d.question, d);
      const box = h('div', { class: 'pv-q' }, h('div', { class: 'pv-n', text: `${i + 1}.` }));
      qsBox.append(box);
      try {
        const fb = d.feedback ? Object.assign({ given: d.given }, d.feedback) : null;
        UI.workspace(box, q, fb ? { mode: 'review', fb, bar: false, toolbar: false, head: false, prefs: { open_explanations: true, option_reasons: true } }
          : { mode: 'exam', bar: false, toolbar: false, head: false, pad: false });
      } catch (e) { box.append(h('p', { text: q.stem || '' })); }
    });
    const key = h('div', { class: 'pv-key' }, h('h2', { text: 'Answer key and explanations' }));
    if (withKey) {
      key.append(h('ol', {}, details.map(d => {
        const f = d.feedback;
        if (!f) return h('li', { text: '—' });
        const L = 'ABCD';
        return h('li', {}, h('b', { text: `Answer: ${f.answer}${f.accepted && f.accepted.length ? ` (also ${f.accepted.join(', ')})` : ''}` }),
          f.rationale ? h('p', { text: f.rationale }) : null,
          (f.reasons || []).map((why, k) => (why && k !== f.answer_index ? h('p', { class: 'opt-l', text: `${L[k]}: ${why}` }) : null)),
          (f.steps || []).length ? h('ol', {}, f.steps.map(s => h('li', { text: typeof s === 'string' ? s : s.text || '' }))) : null);
      })));
    } else key.append(h('p', { class: 'meta', text: 'The key prints once the set is finished: enter your answers online, or finish the set, then print again.' }));
    status.remove();
    wrap.append(ctl, head, qsBox, key);
  }

  boot();
})();
