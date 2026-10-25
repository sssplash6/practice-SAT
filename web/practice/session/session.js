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
  // an unknown name draws nothing (it drew an orange dot, which hid typos)
  const icon = (name, size = 18) => h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.ICON[name] ? UI.svg(UI.ICON[name], size) : '' });
  const pct = x => (x === null || x === undefined ? '–' : `${Math.round(x * 100)}%`);
  const mmss = ms => UI.mmss(Math.round((ms || 0) / 1000));
  const cap = t => (t ? t[0].toUpperCase() + t.slice(1) : '');
  const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + 's'}`;
  // the day only: no clock times on screen (the user's rule)
  const when = iso => { try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }); } catch (_) { return ''; } };
  const day = iso => { try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }); } catch (_) { return ''; } };
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const topicName = t => (UI.TOPIC[t] || {}).short || (UI.RW_SKILL || {})[t] || t;
  const api = (path, o) => UI.api(path, o);
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  // hide_timer and open_explanations are not server prefs (§2.7): this viewer's, in localStorage
  const LOCAL_PREFS = 'satf.session.prefs';
  const SERVER_PREFS = new Set(['first_tap', 'option_reasons', 'show_stopwatch', 'pace_alert', 'calc_mode', 'confidence', 'text']);

  const runHost = $('#run'), view = $('#view');
  let sid = url.get('id');
  let st = null, run = null, total = null, asides = 0, ending = false, exhausted = false;
  const notQ = q => !!q && (q.kind === 'example' || q.kind === 'word');
  let ids = [];                        // qid per slot, in served order
  const answered = new Set();          // qids with an answer on the server
  let frontier = null;                 // a pending POST /next (a skip already asked for it)
  // the stopwatch: /answer adds its ms and /time adds each visit, so each slot sends only
  // what the server does not have yet (counted: the runner's total, sent: the server's)
  const counted = [], sent = [];
  let closed = false;
  const challenge = () => st && st.kind === 'challenge';
  // an R&W set: no Math tools, and its "one like it" is a fresh passage, not new numbers
  const rw = () => !!st && st.subject === 'rw';
  // a strict contest (Compete): the runner reports leaving and copying, and the set ends with the spot-check
  const strict = () => !!(st && st.contest && st.contest.strict && !st.finished);
  const fresh = () => (rw() ? 'fresh passages' : 'new numbers');
  const endMode = () => st && st.feedback === 'end';
  const drillPath = p => `/drill/${encodeURIComponent(sid)}${p || ''}`;

  /* ---------------- states */
  function state(text, extra = []) {
    runHost.replaceChildren();
    view.hidden = false;
    view.replaceChildren(h('div', { class: 'ps-state', role: 'alert' }, h('p', { text }),
      h('div', { class: 'acts' }, h('a', { class: 'pill', href: '/practice/', text: 'Back to Practice' }), extra)));
  }
  // the runner's frame (its 64px bar and its column), so nothing jumps when the set arrives
  function skeleton() {
    const col = h('div', { class: 'ps-skel-col' });
    if (UI.skel) { UI.skel(col, 'lines:3'); for (let k = 0; k < 4; k++) UI.skel(col, { w: '100%', h: 56, r: 12 }); }
    runHost.replaceChildren(h('div', { class: 'ps-skel', 'aria-busy': 'true', 'aria-label': 'Loading the set' }, h('div', { class: 'ps-skel-top' }), col));
  }
  async function create(body, suffix = '') {
    try {
      const s = await api('/drill', { method: 'POST', body: Object.assign({ subject: (st && st.subject) || 'math' }, body) });
      location.href = `/practice/session/?id=${encodeURIComponent(s.id)}${suffix}`;
      return true;                      // the button keeps its spinner while the next page loads
    } catch (e) {
      const d = e && e.detail;
      toast(`Couldn’t start it: ${(d && (d.reason || d.detail)) || e.message}`);
      return false;
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
    const crowd = fb && fb.crowd;
    return {
      difficulty: tier || null,
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
  const cellOf = s => ({ n: s.n, aside: notQ(s), status: s.status, flag: !!s.marked || localMarks().has(s.id), note: !!s.has_note, tier: s.difficulty, level: s.level, topic: s.topic,
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
    // a worked example or a word card takes a position but not one of the set's questions
    asides = (st.served || []).filter(s => notQ(s)).length;
    total = st.total == null ? null : st.total + asides;
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
      mode: 'practice', mainId: 'rnMain', feedback: st.feedback || 'instant', sid, title: setTitle(), short: null, cells, total, at,
      clock: st.timed ? { secondsLeft: st.seconds_left ?? 0, paused: !!st.paused } : { elapsed: st.elapsed || 0 },
      pausable: !!(can.pause && st.timed && !challenge()), challenge: challenge(), resumed: st.answered > 0,
      prefs, confActive: !!st.conf_active, hideSkill: st.hide_skill ? 'Mix-up' : false, source: 'drill',
      subject: st.subject || 'math', calc: !rw(), ref: !rw(),          // the calculator and the reference sheet are Math's
      integrity: strict(),
      workspace: {
        coverTool: !challenge(),
        onHint: can.hint ? async () => api(drillPath('/hint'), { method: 'POST', body: { question_id: ids[run.at] } }) : null,
        onTrap: can.more ? async (i, reason) => more({ question_id: ids[run.at], want: String(reason || '').slice(0, 300) }) : null,
        onCause: kind => api(drillPath('/why'), { method: 'POST', body: { question_id: ids[run.at], kind }, quiet: true }).catch(() => toast('Not saved. Try again.')),
        onLadder: can.more ? () => more({ question_id: ids[run.at], ladder: true }) : null,
        onOwn: (own, meta) => check(run.at, null, Object.assign({}, meta, { own })),
      },
      actions: can.more ? {
        source: 'drill', session: sid, axes: rw() ? ['easier', 'harder'] : ['easier', 'harder', 'grid', 'ask'],   // R&W has no grid-ins and no "same setup"
        more: (axis, n) => twinAxis(axis, n),
      } : null,
      more: () => moreItems(),
      on: {
        load: (i, how) => load(i, how),
        check: (i, a, meta) => check(i, a, meta),
        show: (i, it) => { const id = it && it.q && it.q.id; if (id && !ids.includes(id)) { commit(i, id); if (notQ(it.q)) bump(); } },
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
        // strict contest: each leave or copy flags the question on screen (compete.flag, via /spot)
        integrity: e => { if (strict() && ids[e.at]) UI.need('compete-ui').then(() => api(drillPath('/spot'), { method: 'POST', quiet: true, body: UI.compete.spotBody(ids[e.at], e) })).catch(() => {}); },
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
    if (notQ(q)) bump();
    if (r.total !== undefined && r.total !== null && total !== null && r.total + asides > total) grow(r.total + asides);
    return itemOf(await api(drillPath(`/q/${encodeURIComponent(q.id)}`)));
  }
  // a preloaded preview goes into served when it shows (P23)
  function commit(i, qid) {
    ids[i] = qid;
    api(drillPath('/time'), { method: 'POST', body: { question_id: qid, ms: 0 }, quiet: true }).catch(() => {});
  }
  function bump() { asides++; if (total !== null) grow(total + 1); }
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
      if (fb.total !== undefined && fb.total !== null) grow(fb.total + asides);
      // G9 / P23: the next question came with the verdict; render it now, commit it when shown
      // a worked example is not preloaded: it comes with its key from /next then /q
      if (fb.next && !notQ(fb.next) && i === ids.length - 1 && (total === null || i + 1 < total) && run) run.preload(i + 1, itemOf({ question: fb.next, marks: [], strikes: [] }));
      return fb;
    } catch (e) {
      const d = e && e.detail;
      if (e.status === 409 && !(d && /paused/i.test(JSON.stringify(d)))) { endSet(); }
      throw e;
    }
  }

  async function more(body) {
    const r = await api(drillPath('/more'), { method: 'POST', body });
    if (r.total !== undefined && r.total !== null) grow(r.total + asides);
    if (run) run.discardPreload(run.at + 1);
    toast(body.ladder ? 'Next: Learn this type, step by step' : rw() ? 'Next: another one like it' : 'Next: one like this, with new numbers');
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
    try { await api('/flags', { method: 'POST', body: { session: sid, question_id: qid, on: !!on }, quiet: true }); }   // a practice set is flagged through /api/flags (tests use /session/{sid}/flag)
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
    UI.sheet({ title: retake ? 'Retake these exact questions?' : `Rematch: same types, ${fresh()}?`, size: 's', body: b => {
      b.append(h('p', { text: retake ? 'Starts a new copy of this set with the same questions. It tests memory as much as skill. This one stays in your history.'
        : `The same types in the same order, with ${fresh()}. We compare the two question by question.` }));
      b.append(h('label', { class: 'check' }, clean, retake ? 'Start clean: hide my highlights, notes, strikes and rules on this copy' : 'Start clean: hide my notes and highlights on this copy'));
    }, actions: [{ label: 'Cancel', quiet: true }, { label: retake ? 'Retake' : 'Rematch', primary: true,
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
      { label: `Rematch: same types, ${fresh()}`, onClick: () => copySheet('rematch') },
      { label: 'Retake these exact questions (tests memory)', onClick: () => copySheet('retake') },
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
    // a strict contest's spot-check comes before its finish (the finish freezes the points)
    if (!already && strict()) {
      try {
        await UI.need('compete-ui');
        if (run) { try { run.destroy(); } catch (_) {} run = null; }
        await UI.compete.spotCheck(runHost, body => api(drillPath('/confirm'), { method: 'POST', body }));
      } catch (_) {}
    }
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

  /* ---------------- 2.11 Summary (decision 7): the score and what changed lead, then the next
     step, then the Review list; the long breakdowns sit behind disclosures, one tap away */
  const has = x => x !== null && x !== undefined;
  const FOLDS = 'satf.summary.open';               // the breakdowns this viewer keeps open
  const keptOpen = () => { const v = ls.get(FOLDS, []); return Array.isArray(v) ? v : []; };
  // filled at once so it opens in height (details.fold); a chart (lazy) fills on its first open, so it measures a
  // visible box, and opens without the height motion (its content arrives after the open)
  function fold(key, title, fill, lazy) {
    const body = h('div', { class: 'sm-fold-b' });
    const d = h('details', { class: lazy ? 'sm-fold' : 'fold sm-fold' }, h('summary', { text: title }), body);
    let filled = false;
    if (!lazy) { filled = true; fill(body); }
    d.addEventListener('toggle', () => {
      if (d.open && !filled) { filled = true; fill(body); }   // on first open, so a chart measures a visible box
      const keep = new Set(keptOpen());
      if (d.open) keep.add(key); else keep.delete(key);
      ls.set(FOLDS, [...keep]);
    });
    if (keptOpen().includes(key)) d.open = true;
    return d;
  }

  function summary(r) {
    runHost.replaceChildren();
    document.title = `Set complete · ${setTitle()} · SAT Freshman`;
    const lm = localMarks();
    const qs = (r.questions || []).map(q => (lm.has(q.id) ? Object.assign({}, q, { marked: true }) : q));
    const endless = st.total === null || st.total === undefined;
    const n = qs.length;
    // from 1100 wide two columns: the score, what changed and the next step stay put (sticky); Review and the breakdowns scroll
    const lead = h('div', { class: 'sm-lead', 'data-m': 'stagger' }), main = h('div', { class: 'sm-main' });
    const col = h('div', { class: 'psum' }, lead, main);
    view.hidden = false;
    view.replaceChildren(h('header', { class: 'sm-top', 'data-scrolled': '' },
      h('a', { class: 'rn-exit', href: '/practice/', 'aria-label': 'Exit' }, icon('x', 20), h('span', { class: 'rn-exit-l', text: 'Exit' })),
      h('h1', { class: 'sm-title', text: setTitle() })), col);

    // 1. The score card, the page's one hero: the figure, the first-try line, the set's own strip (the receipt), time
    // and pace as two figures; what changed sits under it, flat
    const head = h('section', { class: 'sm-head card hero', 'aria-label': 'Your score' });
    const answeredN = qs.filter(q => !['unanswered', 'skipped'].includes(q.status)).length;
    const acc = r.accuracy, before = r.before_accuracy, P = x => Math.round(x * 100);
    // first-try accuracy is said only when it adds something: it moved, or it differs from the score; a clean set says so in fact
    const move = has(acc) && has(before) ? (P(acc) > P(before) ? `up from ${pct(before)}` : P(acc) < P(before) ? `down from ${pct(before)}` : 'same as before') : null;
    const same = !endless && n && has(acc) && P(acc) === P(r.right / n);
    const lines = [];
    if (has(acc) && (move || (!endless && !same))) lines.push(h('span', { class: 'acc' }, `${pct(acc)} first try`, move ? h('span', { class: 'was', text: ` · ${move}` }) : null));
    else if (!endless && n && r.right === n && has(acc) && P(acc) === 100) lines.push(h('span', { class: 'acc', text: `${n} of ${n}, first try` }));
    // the first view of a finished set (once per set on this device): the score rolls up, the receipt fills, the drawing fills in
    const seen = [].concat(ls.get('satf.sumseen', []) || []);
    const firstView = !seen.includes(sid);
    if (firstView) ls.set('satf.sumseen', [...seen, sid].slice(-60));
    const score = `${r.right} / ${endless ? answeredN : n}`;
    const num = h('span', { class: 'num hero-num', text: firstView ? score.replace(/^\d+/, '0') : score });
    const art = h('span', { class: 'sm-art' + (firstView ? '' : ' seen') });
    head.append(h('div', { class: 'sm-score' }, num, lines.length ? h('span', { class: 'accs' }, lines) : null, art));
    if (firstView) setTimeout(() => (UI.roll ? UI.roll(num, score) : (num.textContent = score)), 120);
    if (n && UI.strip) {
      const rc = UI.strip(head, qs.map(q => ({ status: q.status, flag: q.marked || undefined, note: q.has_note || undefined })), { fit: true });
      if (firstView && rc && rc.el) { rc.el.classList.add('fill-in'); [...rc.el.children].forEach((x, i) => x.style.setProperty('--i', i)); }
    }
    // the set-done drawing: the four domains' mastery as the mark's corners (UI.spotArt 'done'), from the shell's
    // fresh copy (the set just moved them); drawn again only when the numbers change
    if (UI.spotArt && UI.onShell) {
      if (firstView || !(UI.shellData && UI.shellData())) { try { UI.refresh(); } catch (_) {} }
      let drawn = '';
      UI.onShell(d => {
        const ms = d && d.me && d.me.domains && d.me.domains[rw() ? 'rw' : 'math'];   // the set's own subject's four domains
        if (!Array.isArray(ms) || !art.isConnected) return;
        const v = ms.slice(0, 4).map(x => Math.min(1, (+x || 0) / (UI.STRONG || 0.8)));
        if (JSON.stringify(v) === drawn) return;
        drawn = JSON.stringify(v);
        art.innerHTML = UI.spotArt('done', v);
      });
    }
    const spent = qs.reduce((s, q) => s + (q.ms || 0), 0);
    const budgetAvg = n ? qs.reduce((s, q) => s + (q.budget_ms || 0), 0) / n : 0;
    const pairs = [spent ? [mmss(spent), 'in all'] : null, r.avg_ms ? [mmss(r.avg_ms), `a question${budgetAvg ? ` · pace ${mmss(budgetAvg)}` : ''}`] : null].filter(Boolean);
    if (pairs.length) head.append(h('div', { class: 'sm-pairs' }, pairs.map(([v, k]) => h('span', { class: 'sm-pair' }, h('b', { class: 'num', text: v }), h('span', { text: k })))));
    const meta = [`Set complete ${when(st.finished || new Date().toISOString())}`,
      r.guessed_right ? `${r.guessed_right} right but guessed` : null, r.helped ? `${r.helped} right with help` : null].filter(Boolean);
    head.append(h('p', { class: 'sm-meta', text: meta.join(' · ') }));
    if (exhausted || r.exhausted) head.append(h('p', { class: 'sm-note', text: 'We ran out of unseen questions for these settings. Widen the levels or skills to keep going.' }));
    lead.append(head);
    const changed = h('ul', { class: 'sm-changed', 'aria-label': 'What changed' });
    (r.topics || []).forEach(t => {
      const a = UI.masteryWord(t.before, 1), b = UI.masteryWord(t.after, t.asked);
      changed.append(h('li', {}, UI.glyph ? UI.glyph(t.topic) : h('span'), h('span', { class: 'nm', text: topicName(t.topic) || t.name }),
        h('span', { class: 'w' }, a === b ? h('b', { text: b }) : [a, ' → ', h('b', { text: b })])));
    });
    const opened = r.opened || [], fixed = r.closed || [];
    if (opened.length || fixed.length) changed.append(h('li', {}, h('span'), h('span', { class: 'nm', text: 'Mistakes' }),
      h('span', { class: 'w' }, [opened.length ? h('b', { text: `${opened.length} new` }) : null, opened.length && fixed.length ? ' · ' : null, fixed.length ? `${fixed.length} fixed` : null])));
    if (changed.children.length) lead.append(changed);

    // 2. Next
    lead.append(nextActions(r, qs));

    // 3. Review
    if (n) main.append(reviewList(qs));

    // 4. The breakdowns, each one tap away
    const folds = h('div', { class: 'sm-folds' });
    if (opened.length || fixed.length) folds.append(fold('mistakes', 'Mistakes', b => {
      if (opened.length) b.append(h('div', { class: 'sm-mist' }, h('h3', { text: 'New' }), h('ul', { class: 'sm-new' }, opened.map(o => h('li', {},
        h('span', { text: cap(o.label) }), h('span', { class: 's', text: topicName(o.topic) }),
        h('button', { type: 'button', class: 'btn sm', text: 'Fix now', onclick: e => { const b = e.currentTarget; b.setAttribute('aria-busy', 'true'); create({ pool: 'mistakes', templates: [o.template], source: 'mistakes' }).then(ok => { if (!ok) b.removeAttribute('aria-busy'); }); } }))))));
      if (fixed.length) b.append(h('div', { class: 'sm-mist' }, h('h3', { text: 'Fixed' }), h('ul', {}, fixed.map(o => h('li', {},
        icon('check', 16), h('span', { text: cap(o.label) }), h('span', { class: 's', text: topicName(o.topic) }))))));
      b.append(h('a', { class: 'link', href: '/mistakes/', text: 'Older open mistakes' }));
    }));

    const byType = r.by_type || [];
    const moved = Object.fromEntries((r.moved || []).map(m => [m.topic, m]));
    if ((r.topics || []).length) folds.append(fold('skill', 'By skill', b => {
      const rows = h('div', { class: 'sm-rows' });
      r.topics.forEach(t => {
        const inTopic = qs.filter(q => q.topic === t.topic && q.ms);
        const avg = inTopic.length ? inTopic.reduce((s, q) => s + q.ms, 0) / inTopic.length : 0;
        const bf = Math.max(0, Math.min(1, t.before || 0)), af = Math.max(0, Math.min(1, t.after || 0));
        const m = moved[t.topic] || {};
        const rate = has(m.rate_after) ? `first try ${has(m.rate_before) ? `${pct(m.rate_before)} → ` : ''}${pct(m.rate_after)}` : '';
        const gain = has(m.gain_after) ? `≈ +${Math.round(m.gain_after)} pts on the table` : '';
        rows.append(h('div', { class: 'sm-row' },
          UI.glyph ? h('span', {}, UI.glyph(t.topic)) : h('span'),
          h('span', { text: t.name || topicName(t.topic) }),
          h('span', { class: 'n', text: `${t.right} / ${t.asked}` }),
          h('span', { class: 't', text: avg ? `avg ${mmss(avg)}` : '' }),
          h('span', { class: 'sm-mb' }, h('span', { class: 'bar2', role: 'img', 'aria-label': `${UI.masteryWord(t.before, 1)} to ${UI.masteryWord(t.after, t.asked)}` },
            h('i', { class: 'g', style: `width:${Math.max(bf, af) * 100}%` }), h('i', { class: 'a', style: `width:${af * 100}%` })),
            rate || gain ? h('span', { class: 'w', text: [rate, gain].filter(Boolean).join(' · ') }) : null),
          h('a', { class: 'btn sm', href: `/practice/?skills=${encodeURIComponent(t.topic)}`, text: 'Practise' })));
      });
      b.append(rows);
      if (byType.length) b.append(h('div', { class: 'sm-types' }, h('h3', { text: 'By question type' }),
        h('ul', {}, byType.map(t => h('li', {}, h('span', { text: t.name }), h('span', { class: 't', text: `${t.right} / ${t.asked} · ${mmss(t.asked ? t.ms / t.asked : 0)}` }))))));
    }));

    const tiers = ['easy', 'medium', 'hard'].filter(k => ((r.by_difficulty || {})[k] || {}).asked);
    const lv = r.levels_seen || [];
    if (tiers.length) folds.append(fold('difficulty', 'By difficulty', b => {
      const diff = h('div', { class: 'sm-diff' });
      tiers.forEach(k => {
        const d = r.by_difficulty[k];
        diff.append(h('div', { class: 'r' }, h('span', { text: TIER[k] }), h('span', { class: 't', text: `${d.right} / ${d.asked}` }),
          h('span', { class: 'fill', role: 'img', 'aria-label': `${d.right} of ${d.asked} right` }, h('i', { style: `width:${(d.right / d.asked) * 100}%` })),
          h('span', { class: 't', text: mmss(d.ms / d.asked) })));
      });
      b.append(diff, lv.length ? h('p', { class: 'sm-legend', text: `Levels seen: ${lv[0]}${lv.length > 1 ? `–${lv[lv.length - 1]}` : ''} ${r.measured_seen ? ` (${r.measured_seen} measured)` : ''}` }) : null);
    }));

    const timed = qs.filter(q => q.ms);
    if (timed.length) folds.append(fold('time', 'Time per question', b => {
      const over = timed.filter(q => q.budget_ms && q.ms > q.budget_ms).length;
      const ms = timed.map(q => q.ms);
      const box = h('div', { class: 'sm-chart' });
      b.append(box, h('p', { class: 'sm-legend', text: `${over ? `Over pace ${over} · ` : ''}fastest ${mmss(Math.min(...ms))} · slowest ${mmss(Math.max(...ms))}${(r.time_sinks || []).length ? ` · time sinks ${r.time_sinks.length}` : ''}` }));
      if (UI.barChart) {
        try {
          UI.barChart(box, qs.map(q => ({ key: String(q.n), label: String(q.n), value: Math.round((q.ms || 0) / 1000), budget: q.budget_ms ? Math.round(q.budget_ms / 1000) : null,
            status: q.budget_ms && q.ms > q.budget_ms ? 'over' : null, tip: `Q${q.n} · ${mmss(q.ms)}${q.budget_ms ? ` / ${mmss(q.budget_ms)}` : ''}` })),
          { unit: 's', labels: 'label', height: 160, label: 'Time per question', budget: true });
        } catch (e) { console.error(e); }
      }
    }, true));

    // ("More from this set" was removed at the user's word, 2026-09-28: "remove this fully")
    if ((r.slots || []).length) folds.append(fold('then', 'Then and now', b => b.append(h('ul', { class: 'sm-lines' }, r.slots.map(s => h('li', {}, h('b', { text: `Q${s.n} · ${s.type_name || ''}: ` }),
      `${cap(s.then.status)}${s.then.ms ? ` ${mmss(s.then.ms)}` : ''} → ${cap(s.now.status || '')}${s.now.ms ? ` ${mmss(s.now.ms)}` : ''}${s.change ? ` · ${s.change}` : ''}`))))));
    if (folds.children.length) main.append(folds);
  }

  function reviewList(qs) {
    const slow = q => q.budget_ms && q.ms > q.budget_ms;
    const F = {
      all: () => true, incorrect: q => q.status === 'incorrect', mixed: q => q.status === 'mixed', marked: q => q.marked,
      slow, guessed: q => q.guess || q.conf === 'guess', skipped: q => q.status === 'skipped' || q.status === 'unanswered', note: q => q.has_note,
    };
    const LABEL = { all: 'All', incorrect: 'Incorrect', mixed: 'Mixed', marked: 'Marked', slow: 'Slow', guessed: 'Guessed', skipped: 'Skipped', note: 'Has note' };
    // the cell carries status, mark and note; the row adds the type, difficulty, time and the mistake named
    const rows = qs.map((q, i) => {
      const b = h('button', { type: 'button', class: 'sm-rl-row', 'data-status': q.status },
        UI.cell(q.status, q.n ?? i + 1, { static: true, size: 'sm', flag: q.marked || null, note: q.has_note || null, tier: q.difficulty, repair: q.repair || null }),
        h('span', { class: 'ty' }, UI.glyph ? UI.glyph(q.topic) : null, h('span', { text: q.type_name || topicName(q.topic) })),
        h('span', { class: 'd', text: TIER[q.difficulty] || '' }),   // no level: internal calibration stays off screen (the user)
        h('span', { class: 't', text: q.ms ? mmss(q.ms) : '' }),
        h('span', { class: 'm', text: q.mistake ? cap(q.mistake) : '' }));
      b.addEventListener('click', () => openReview(qs, i));
      return b;
    });
    const list = h('div', { class: 'sm-rl', role: 'list' }, rows);
    rows.forEach((r, i) => { r.dataset.key = String(qs[i].id || i); });
    const opts = Object.keys(F).map(k => ({ value: k, label: LABEL[k], n: qs.filter(F[k]).length })).filter(o => o.value === 'all' || o.n);
    const apply = v => { rows.forEach((row, i) => { row.hidden = !F[v](qs[i]); }); };
    // one "Show" menu (it was a row of up to eight chips over the list)
    let showB = null, cur = 'all';
    if (opts.some(o => o.value !== 'all' && o.n < qs.length)) {
      const lab = h('span', { text: 'Show: All' });
      showB = h('button', { type: 'button', class: 'btn sm sm-show', 'aria-haspopup': 'menu', 'aria-expanded': 'false' }, lab);   // ui.css draws the caret
      // the rows that stay close their gaps, the ones that come back nudge in (UI.glide)
      showB.addEventListener('click', () => UI.menu(showB, opts.map(o => ({ label: o.label, meta: String(o.n), radio: 'show', checked: cur === o.value, close: true,
        onClick: () => { cur = o.value; lab.textContent = `Show: ${o.label}`; if (UI.glide) UI.glide(list, () => apply(cur)); else apply(cur); } })), { label: 'Show' }));
    }
    const incorrect = qs.filter(F.incorrect);
    const markAll = incorrect.length ? h('button', { type: 'button', class: 'quiet', text: 'Mark all incorrect for review', onclick: async e => {
      const btn = e.currentTarget;
      btn.disabled = true;
      try {
        for (const q of incorrect) await mark(q.id, true);
        incorrect.forEach(q => { q.marked = true; const c = rows[qs.indexOf(q)].querySelector('.cell'); if (c) c.setAttribute('data-flag', 'true'); });
        toast(`${plural(incorrect.length, 'question')} marked for review`);
      } catch (_) { toast('Not saved. Try again.'); btn.disabled = false; }
    } }) : null;
    return h('section', { class: 'sm-sec' }, h('div', { class: 'sm-rl-head' }, h('h2', { text: 'Review' }), h('div', { class: 'sm-rl-acts' }, showB, markAll)), list);
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
  // the one next step as the pill, the two most used beside it, everything else under More
  function nextActions(r, qs) {
    const box = h('section', { class: 'sm-next', 'aria-label': 'Next', 'data-m-now': '' });   // the page entry never delays the primary
    const misses = qs.filter(q => q.status === 'incorrect' || q.status === 'mixed').length;
    if (challenge()) {
      box.append(h('a', { class: 'pill', href: '/challenge/', text: 'Board' }));
      if (r.contest && r.contest.rank) box.append(h('span', { class: 'sm-rank', text: `#${r.contest.rank} of ${r.contest.of || r.contest.n || '?'}` }));
    } else if (r.next_set) {
      const ns = r.next_set;   // its title already counts the questions: one twin each
      box.append(h('button', { type: 'button', class: 'pill', title: plural(ns.count, 'question'), onclick: e => { const b = e.currentTarget; b.setAttribute('aria-busy', 'true'); create(ns.body).then(ok => { if (!ok) b.removeAttribute('aria-busy'); }); } }, `${ns.title} · ≈ ${ns.minutes} min`));
    } else if (r.next && (r.next.topics || []).length) {
      box.append(h('button', { type: 'button', class: 'pill', title: `${r.next.topics.map(topicName).join(' · ')} · ${r.next.count || 10} questions`,
        onclick: e => { const b = e.currentTarget; b.setAttribute('aria-busy', 'true'); create({ topics: r.next.topics, count: r.next.count || 10, source: 'coach', subject: r.next.subject || 'math' }).then(ok => { if (!ok) b.removeAttribute('aria-busy'); }); } }, 'Keep going'));
    }
    // one pill, one button (Same settings when it is free), the rest in More: a phone shows the pill, then one row
    const pill = box.querySelector('.pill');
    const fixIt = misses ? { label: `Fix my ${plural(misses, 'miss', 'misses')}`, onClick: () => create({ from_session: sid, source: 'result' }) } : null;
    const sameIt = challenge() ? null : { label: 'Same settings, new questions', onClick: () => create({ again: sid, source: 'builder' }) };
    const wordsIt = r.words_due ? { label: `SAT words · ${r.words_due} due`, href: '/words/' } : null;
    const cands = [challenge() || r.next_set ? null : fixIt, sameIt, wordsIt].filter(Boolean);
    const busy = fn => e => { const b = e.currentTarget; b.setAttribute('aria-busy', 'true'); Promise.resolve(fn()).then(ok => { if (!ok) b.removeAttribute('aria-busy'); }); };
    const put = (it, cls) => box.append(it.href ? h('a', { class: cls, href: it.href, text: it.label }) : h('button', { type: 'button', class: cls, text: it.label, onclick: busy(it.onClick) }));
    if (!pill && cands.length) put(cands.shift(), 'pill');
    const second = cands.includes(sameIt) ? sameIt : cands[0];
    if (second) { put(second, 'btn'); cands.splice(cands.indexOf(second), 1); }
    const items = challenge() ? [] : [
      ...cands,
      // the pill is already the fix set, so the plain fix waits here: one count, said once
      misses && r.next_set ? fixIt : null,
      { label: `Rematch: same types, ${fresh()}`, onClick: () => copySheet('rematch') },
      { label: 'Rematch in 3 days', onClick: async () => { try { await api(drillPath('/rematch-due'), { method: 'POST', body: { days: 3 } }); toast('It comes back in Up next in 3 days'); } catch (_) { toast('Not saved. Try again.'); } } },
      { label: 'Retake these exact questions (tests memory)', onClick: () => create({ retake: sid, clean: true, source: 'builder' }) },
      { label: 'Share this set', onClick: () => share() },
      { label: 'Print', href: `/practice/session/?id=${encodeURIComponent(sid)}&print=1` },
      { separator: true },
    ].filter(Boolean);
    items.push({ label: 'Back to Practice', href: '/practice/' });
    const moreB = h('button', { type: 'button', class: 'btn sm-more', 'aria-haspopup': 'menu', 'aria-expanded': 'false' }, h('span', { text: 'More' }));   // ui.css draws the caret
    UI.menu.bind(moreB, items, { label: 'More ways to go on' });
    box.append(moreB);
    return box;
  }

  /* ---------------- 2.12 Print view */
  async function printView() {
    runHost.replaceChildren();
    view.hidden = false;
    const wrap = h('div', { class: 'pv-page' });
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
    const keyed = [];                  // the answered questions' workspaces: unticked, they print as a clean worksheet
    include.addEventListener('change', () => {
      wrap.classList.toggle('nokey', !include.checked);
      keyed.forEach(w => w.setHidden(!include.checked));
    });
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
        const w = UI.workspace(box, q, fb ? { mode: 'review', fb, bar: false, toolbar: false, head: false, prefs: { open_explanations: true, option_reasons: true } }
          : { mode: 'exam', bar: false, toolbar: false, head: false, pad: false });
        if (fb) keyed.push(w);
      } catch (e) { box.append(h('p', { text: q.stem || '' })); }
    });
    const key = h('div', { class: 'pv-key' }, h('h2', { text: 'Answer key and explanations' }));
    if (withKey) {
      key.append(h('ol', {}, details.map(d => {
        const f = d.feedback;
        if (!f) return h('li', { text: '–' });
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
