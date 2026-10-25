/* ============================================================================
   SAT Freshman -- the score report, /results/report/?id=<sid> (S6)
   (spec/rebuild-v2.md 3.5 §1; v2-upgrades reports.md SR1-SR25; decisions 3, 4, 7;
   the user's UI rules of 2026-09-28)

   One sitting. The header: "Results / the sitting's name" with the actions (the Fix split,
   Review mistakes, More with Retake as a test first), one meta line (date, minutes, timing,
   form, conditions, note). Main column: the score (the page's one hero), where the points went,
   then-vs-now, the mistakes (habits are a group in them), every question (grid or table,
   one row: Show, Filters (Focus inside), View; What if, selection; the grid's module heads carry each
   module's result), one Breakdown card (domain, skill, difficulty, format), judgement and
   pace. Right column (1280px+, sticky): the recovery steps, the summary rows,
   three takeaways, Best value and up next.

   Reads GET /api/session/{sid}/results (api_results.report), painted at once from
   sessionStorage satf.results.<sid> when the runner prefetched it. Writes: /seen,
   /second, /second/state, /why, /note, /whatif (all S6), /api/drill, /api/mock/new,
   /api/notes, /api/saved, PUT /api/me. The player is F3's UI.review; Report is F6's
   UI.report; every drill goes through UI.rx.drill (results-ui.js).

   Never shown to a student (the user's rules): levels, odds, "rough", formula
   paragraphs, a trap a right answer dodged, one number said twice.
   ========================================================================== */
(() => {
  'use strict';
  const UI = window.UI;
  if (!UI || !UI.rx) return;
  const { h, rx } = UI;
  const doc = document;
  const $ = id => doc.getElementById(id);
  const P = new URLSearchParams(location.search);
  const SID = P.get('id') || '';
  const VS = P.get('vs');
  const FRESH = P.get('fresh') === '1';

  /* ?fresh=1 is read once; ?q=M1-7 (Tests' chips) becomes the player's hash */
  (() => {
    const u = new URL(location.href);
    const q = u.searchParams.get('q');
    if (q && !/^#q=/.test(location.hash)) {
      const m = q.match(/^(?:(math|rw)[-\s]?)?(?:m(\d)[-\s]?)?q?(\d+)$/i);
      if (m) u.hash = `q=${(m[1] || 'math').toLowerCase()}-${m[2] ? `m${m[2]}-` : ''}${+m[3]}`;
    }
    u.searchParams.delete('q');
    u.searchParams.delete('fresh');
    if (u.href !== location.href) history.replaceState(history.state, '', u);
  })();

  UI.shell('report');

  /* ------------------------------------------------------------ formatters */
  const n = x => UI.num(x);
  const pc = (a, b) => (b ? Math.round(a / b * 100) : 0);
  const sc = (a, b) => `${n(a)} / ${n(b)}`;
  const tm = ms => (ms === null || ms === undefined ? '' : UI.mmss(ms / 1000));
  const mins = ms => Math.max(1, Math.round((ms || 0) / 60000));
  const plural = (k, one, many) => `${n(k)} ${k === 1 ? one : (many || one + 's')}`;
  const cap = t => (t ? t[0].toUpperCase() + t.slice(1) : '');
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const TIERS = ['easy', 'medium', 'hard'];
  const FORMAT = { mcq: 'Multiple choice', spr: 'Grid-in' };
  const CAUSES = ['trap', 'slip', 'misread', 'clock', 'entry', 'gap'];
  const causeName = c => (rx.CAUSE[c] || { label: cap(c) }).label;
  const causeOne = c => cap((rx.CAUSE[c] || { one: c }).one);
  const topicName = (slug, fb) => (UI.RW_SKILL && UI.RW_SKILL[slug]) || ((UI.TOPIC && UI.TOPIC[slug]) || {}).short || fb || slug || '';
  const glyph = slug => (UI.glyph && slug && !/^rw_/.test(slug) ? UI.glyph(slug) : null);
  // the sitting's subject orders its domains and sets a question's pace and a module's clock (R&W 71 s and 32:00,
  // Math 95 s and 35:00)
  const rwSit = () => !!R && R.subject === 'rw';
  const domOrder = () => (rwSit() ? (UI.RW_DOMAINS || []).map(d => d.name) : (UI.DOMAINS || []).map(d => d[0]));
  const PACE_MS = () => (rwSit() ? 71111 : 95455);
  const MOD_CLOCK = () => (rwSit() ? '32:00' : '35:00');
  const TESTS = ['full', 'mock', 'module', 'diagnostic', 'paper', 'custom', 'twin', 'shared'];
  const RUSHED = 30000, LONG = 190000;
  const LS = { get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} } };
  const letter = (x, g) => (g === null || g === undefined || g === '' ? null : x.type === 'mcq' && Number.isInteger(+g) && String(g).length < 3 ? 'ABCD'[+g] : String(g));
  const math = t => (UI.fracText && t ? UI.fracText(String(t)) : String(t ?? ''));

  /* kit's one "?": explanations open from it (decision 7) */
  const info = (text, about) => UI.why(text, { about });
  // a card's head: its short title (no kicker over it), a meta, a ? and the controls on the right. fig: [figure, unit]
  // leads with the number (28, its unit small on the same baseline) in place of a title
  function head(host, o) {
    host.hidden = false;
    host.replaceChildren();
    const hd = h('div', { class: 'card-head' },
      o.fig ? h('h2', { class: 'rp-fig' }, h('b', { text: o.fig[0] }), h('span', { text: ` ${o.fig[1]}` })) : h('h2', { text: o.title }),
      o.meta ? h('span', { class: 'meta', text: o.meta }) : null, o.tip ? info(o.tip, o.about) : null,
      o.right ? h('div', { class: 'rp-headr' }, o.right) : null);
    host.append(hd);
    return host;
  }
  const btn = (text, onClick, cls = 'btn sm') => {
    const b = h('button', { type: 'button', class: cls, text });
    b.addEventListener('click', e => onClick(b, e));
    return b;
  };
  const link = (text, href, cls = 'quiet') => h('a', { class: cls, href, text });

  /* ------------------------------------------------------------ state */
  let R = null, IT = [], owner = false, sample = false, scored = false, test = false, drillKind = false, chall = false;
  let sectioned = false, byId = new Map(), player = null, dirty = false, gaugeApi = null, fbar = null;
  const S = { show: P.get('show') || 'all', act: P.get('act') || '', colour: P.get('colour') || '', view: P.get('view') || '' };
  const WI = { on: false, right: new Set(), wrong: new Set(), timer: 0, band: null };
  const SEL = new Set();
  let selbar = null, lastSel = null;
  let reviewGrid = null, reviewTable = null, reviewBody = null, legendApi = null, showApi = null;

  /* ------------------------------------------------------------ load */
  function skeleton() {
    const root = $('root');
    root.querySelectorAll('#head, section').forEach(s => { s.hidden = true; });
    const hero = $('hero');
    hero.hidden = false;
    hero.replaceChildren(h('div', { class: 'rp-hero' }, h('div', { class: 'rp-gauge' }, UI.skel(null, 'circle:200')), h('div', { class: 'rp-facts' }, UI.skel(null, 'line.lg'), UI.skel(null, 'lines:4'))));
    const tiles = $('tiles');
    tiles.hidden = false;
    tiles.replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'rows:5'));
    const rv = $('review');
    rv.hidden = false;
    rv.replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'cells:44'));
  }
  async function load() {
    if (!SID) return notFound();
    let cached = null;
    try { cached = JSON.parse(sessionStorage.getItem(`satf.results.${SID}`) || 'null'); } catch (_) { cached = null; }
    if (cached && cached.review) paint(cached); else skeleton();
    try {
      const r = await UI.api(`/session/${encodeURIComponent(SID)}/results`, { quiet: !!cached });
      try { sessionStorage.removeItem(`satf.results.${SID}`); } catch (_) {}
      if (!cached || JSON.stringify(r) !== JSON.stringify(cached)) paint(r);
    } catch (e) { if (!cached) fail(e); }
  }
  async function refresh() {
    try { paint(await UI.api(`/session/${encodeURIComponent(SID)}/results`, { quiet: true }), true); } catch (_) { /* the page stays as it was */ }
  }
  function fail(e) {
    const st = e && e.status, d = (e && e.detail) || {};
    if (st === 404) return notFound();
    if (st === 409) {
      const k = d.kind || '';
      location.replace(['drill', 'practice', 'challenge', 'words'].includes(k) ? `/practice/session/?id=${encodeURIComponent(SID)}` : `/test/?s=${encodeURIComponent(SID)}`);
      return;
    }
    if (st === 403 && d.need === 'signup') { location.replace(`/diagnostic/signup.html?s=${encodeURIComponent(SID)}`); return; }
    const main = $('main');
    main.removeAttribute('aria-busy');
    const root = $('root');
    if (st === 403) {
      // 1.16: a live challenge says so and offers today's; any other private report just says it is private
      const live = d.kind === 'challenge';
      root.replaceChildren(h('section', { class: 'card rp-alone' },
        h('h1', { class: 'h2', text: live ? 'This challenge is still running today. Its report opens to others tomorrow.' : 'This report is private to the student who sat it.' }),
        h('div', { class: 'rp-row' }, live ? h('a', { class: 'pill sm', href: '/challenge/', text: 'Sit today’s challenge' }) : null, link('All results', '/results/'))));
      return;
    }
    // Try again puts the section shells back (this card replaced them), then loads as on arrival
    const shell = [...root.children];
    const again = btn('Try again', () => { root.replaceChildren(...shell); main.setAttribute('aria-busy', 'true'); skeleton(); load(); });
    root.replaceChildren(h('section', { class: 'card rp-alone', role: 'alert' }, h('h1', { class: 'h2', text: 'Couldn’t load this report.' }), h('div', { class: 'rp-row' }, again, link('All results', '/results/'))));
  }
  function notFound() {
    $('main').removeAttribute('aria-busy');
    $('root').replaceChildren(h('section', { class: 'card rp-alone' }, h('h1', { class: 'h2', text: 'That sitting does not exist.' }),
      h('div', { class: 'rp-row' }, h('a', { class: 'btn', href: '/results/', text: 'All results' }), h('a', { class: 'btn', href: '/tests/', text: 'Tests' }))));
    doc.title = 'Report not found · SAT Freshman';
  }

  /* ------------------------------------------------------------ the model */
  function prep(r) {
    const rec = r.recovery || {};
    const recovered = new Set(rec.recovered || []), slipping = new Set(rec.slipping || []);
    const J = r.judgement || {};
    const sureWrong = new Set(J.sure_wrong || []), guessed = new Set(J.guessed_right || []);
    const budget = {};
    ((r.pace || {}).per_q || []).forEach(p => { budget[p.qid] = p.budget_ms; });
    return (r.review || []).map((x, i) => {
      const raw = x.status;
      const bucket = raw === 'correct' ? 'correct' : raw === 'blank' || raw === 'skipped' ? 'unanswered' : raw === 'not_reached' ? 'not_reached' : 'incorrect';
      const fixed = raw === 'incorrect' && ((x.trap && x.trap.closed) || recovered.has(x.id));
      const trail = (x.changes || []).filter(v => v !== null && v !== '');
      const changed = trail.length > 1 && String(trail[0]) !== String(trail[trail.length - 1]) ? [trail[0], trail[trail.length - 1]] : null;
      const miss = bucket === 'incorrect' || bucket === 'unanswered';
      const b = budget[x.id] || null;
      const it = { ...x, i, raw, bucket, st: fixed ? 'fixed' : raw === 'blank' ? 'unanswered' : raw, miss, changed, budget_ms: b,
        cause: x.cause && x.cause.cause, pts: rx.wnum(x.worth), recovered: recovered.has(x.id), slipping: slipping.has(x.id),
        sureWrong: sureWrong.has(x.id), guessed: guessed.has(x.id), held: !!x.hidden,
        looked: !!(x.seen || x.second) };
      const ms = x.ms;
      it.pace = !ms ? '' : bucket === 'correct' ? (b && ms > 1.5 * b ? 'sink' : b && ms <= b ? 'banked' : '') : miss && b ? (ms < 0.5 * b ? 'rushed' : ms > 1.5 * b ? 'stuck' : '') : '';
      it.time = !ms ? '' : ms < RUSHED && miss ? 'rushed' : ms > LONG ? 'long' : '';
      return it;
    });
  }
  const misses = () => IT.filter(x => x.miss);
  const qids = list => list.map(x => x.id);
  const fixBody = (list, extra = {}) => ({ from_session: SID, only: qids(list), source: 'fix', ...extra });
  const drill = (body, b) => (owner ? rx.drill(body, b) : null);
  const labelOf = x => x.label || `Q${x.n}`;

  /* ------------------------------------------------------------ paint */
  function paint(r, again) {
    R = r;
    if (r.kind === 'words') { location.replace(`/words/run/?id=${encodeURIComponent(SID)}`); return; }
    sample = SID === 'sample-section' || /^sample:/.test(r.learner || '');
    owner = !!r.mine && !sample;
    scored = !!(r.estimate && r.estimate.low !== undefined && r.estimate.low !== null && (r.summary || {}).answered);
    test = TESTS.includes(r.kind);
    drillKind = ['drill', 'practice'].includes(r.kind);
    chall = r.kind === 'challenge' || !!r.contest;
    sectioned = (r.modules || []).length > 1;
    IT = prep(r);
    byId = new Map(IT.map(x => [x.id, x]));
    if (!S.view) S.view = IT.length > 60 ? 'table' : 'grid';
    if (!S.colour) S.colour = 'status';
    $('main').removeAttribute('aria-busy');
    doc.title = `${r.label || 'Report'}${r.seq ? ` #${r.seq}` : ''} · SAT Freshman`;
    drawHead(); drawStrips(); drawHero(); drawRecovery(); drawLedger(); drawCompare(); drawMistakes(); drawValue(); drawTakeaways(); drawTiles();
    drawReview(); drawDomains(); drawSkills(); drawSplit(); drawBreakdown(); drawJudgement();
    drawPace(); drawNext();
    registerSections();
    if (!again) {
      const at = UI.review && UI.review.at ? UI.review.at(IT.map(x => ({ n: x.n, module: x.module, subject: x.subject }))) : -1;
      if (at >= 0) setTimeout(() => openPlayer(at), 0);
    }
  }

  /* ------------------------------------------------------------ header */
  // the sitting's name is the h1; what kind of sitting it is joins the meta line
  function sittingName() {
    const r = R, seq = r.seq ? ` #${r.seq}` : '';
    if (r.kind === 'challenge') return 'Daily challenge';
    if (r.kind === 'diagnostic') return 'Diagnostic';
    if (r.full) return UI.subjectLabel(r.subject || 'math');     // a full SAT's section: the crumb carries "Full SAT"
    if (r.kind === 'mock') return `Full section${seq}`;
    if (r.kind === 'module') return `One module${seq}`;
    if (r.kind === 'paper') return `Paper${seq}`;
    if (r.kind === 'custom') return 'Custom test';
    if (r.kind === 'twin') return `Twin test${seq}`;
    return `Practice set${seq}`;
  }
  function kindBits() {
    const r = R, k = r.kind;
    const src = r.source ? String(({ map: 'Map', mistakes: 'Mistakes', saved: 'Saved', fix: 'Fix these', plan: 'Plan', coach: 'Coach', today: 'Today', learn: 'Learn it', habit: 'Habit drill', twin: 'Try one like this' })[r.source] || r.source) : null;
    if (k === 'mock' || k === 'full') return ['Adaptive', /^\d+\.\d+$/.test(r.mock || '') ? `Form ${r.mock}` : null];
    if (k === 'custom') return [plural(r.asked, 'question')];
    if (TESTS.includes(k) || k === 'challenge') return [];
    return [src ? `From ${src}` : null];
  }
  function drawHead() {
    const el = $('head');
    el.hidden = false;
    el.replaceChildren();
    // "Results / Full section #3": the way up and the name on one line, the actions beside them; the way back to where
    // the student came from (the plan) is its own small line, only when there is one
    try {
      const ret = JSON.parse(sessionStorage.getItem('satf.return') || 'null');
      if (ret && ret.href && /^\/[^/]/.test(ret.href)) el.append(h('nav', { class: 'rp-back', 'aria-label': 'Back' }, h('a', { href: ret.href }, UI.icon('caret_left', 16), ` ${ret.label || 'Back to your plan'}`)));
    } catch (_) {}
    const acts = h('div', { class: 'rp-acts' });
    headActions(acts);
    // a full SAT's section sits under its full SAT: "Results / Full SAT #2 / Reading and Writing"
    const up = R.full ? [h('a', { href: R.full.href || `/results/full/?id=${encodeURIComponent(R.full.id)}`, text: `Full SAT${R.full.number ? ` #${R.full.number}` : ''}` }), h('span', { 'aria-hidden': 'true', text: '/' })] : [];
    el.append(h('div', { class: 'rp-title' }, h('div', { class: 'rp-crumb' }, h('a', { href: '/results/', text: 'Results' }), h('span', { 'aria-hidden': 'true', text: '/' }), ...up,
      h('h1', { class: 'h1', text: sittingName() })), acts));
    // one meta line: the subject, the day (not the clock time: the user's rule), minutes, timing, then only what
    // differs from a standard sitting (decision 7), then the note
    const d = new Date(R.finished || (R.challenge && R.challenge.day) || R.started);
    const c = R.conditions || {}, J = R.judgement || {};
    const bits = [R.full || !test ? null : UI.subjectLabel(R.subject || 'math'), UI.date(d, 'long'), R.ms ? `${mins(R.ms)} min` : null, R.timed ? 'Timed' : 'Untimed', ...kindBits()];
    if (c.timing && c.timing !== 'official' && test) bits.push(c.timing === 'untimed' ? 'Untimed' : `${String(c.timing).replace(/^x/, '')}× time`);
    if (c.calculator === false && !rwSit()) bits.push('Calculator off');     // R&W never has one
    if (c.pauses) bits.push(`Paused ${n(c.pauses)}×`);
    if (J.away && J.away.n) bits.push(`Left the window ${n(J.away.n)}× · ${tm(J.away.ms)}`);
    const meta = h('p', { class: 'rp-meta' }, [...new Set(bits.filter(Boolean))].map(t => h('span', { text: t })));
    // the timing that made it so is in the line already
    if (scored && c.timing && c.timing !== 'official') meta.append(h('span', { class: 'badge soft', text: 'Practice only' }));
    if (R.note) meta.append(h('span', {}, h('q', { text: R.note })));
    el.append(meta);
    noteBox = h('div', { class: 'rp-note', hidden: true });
    el.append(noteBox);
  }
  // the note: written from the More menu (Add a note, Edit note); it shows in the meta line
  let noteBox = null;
  function editNote() {
    const box = noteBox;
    if (!box) return;
    const f = h('input', { class: 'field sm', maxlength: '140', value: R.note || '', 'aria-label': 'A note about this sitting', placeholder: 'tired, after school' });
    const close = () => { box.hidden = true; box.replaceChildren(); };
    const save = btn('Save', async b => {
      b.setAttribute('aria-busy', 'true');
      try { await UI.api(`/session/${encodeURIComponent(SID)}/note`, { method: 'POST', body: { note: f.value.trim() } }); R.note = f.value.trim() || null; drawHead(); }
      catch (_) { UI.toast('Not saved. Try again.'); b.removeAttribute('aria-busy'); }
    });
    f.addEventListener('keydown', e => { if (e.key === 'Enter') save.click(); if (e.key === 'Escape') close(); });
    box.replaceChildren(f, save, btn('Cancel', close, 'quiet'));
    box.hidden = false;
    setTimeout(() => f.focus(), 0);
  }

  /* the Fix primary: misses by points per minute up to the day's minutes (SR2) */
  function fixPlan() {
    const all = misses();
    if (!scored || !R.ledger || !(R.best_value || []).length) return { list: all, pts: null, ms: all.reduce((s, x) => s + (x.budget_ms || PACE_MS()), 0), all: true };
    let cap = null;
    try { const p = UI.prefs && UI.prefs.now && UI.prefs.now(); cap = p && +p.minutes > 0 ? +p.minutes * 60000 : null; } catch (_) { cap = null; }
    const take = [];
    let ms = 0;
    for (const b of R.best_value) {
      const x = byId.get(b.qid);
      if (!x) continue;
      if (cap && take.length && ms + b.budget_ms > cap) break;
      take.push(x);
      ms += b.budget_ms;
    }
    const whole = take.length >= R.best_value.length;
    return { list: take, ms, all: whole, pts: whole ? R.ledger.total : null };
  }
  function fixMenu() {
    const all = misses(), inc = all.filter(x => x.bucket === 'incorrect'), blank = all.filter(x => x.bucket === 'unanswered');
    const open = all.filter(x => x.st !== 'fixed' && !x.recovered);
    const by = c => all.filter(x => x.cause === c);
    const items = [];
    const add = (label, list, extra) => { if (list.length) items.push({ label: `${label} · ${n(extra && extra.each ? list.length * extra.each : list.length)}`, onClick: () => drill(fixBody(list, extra)) }); };
    add('Everything', all, { order: 'given' });
    add('Incorrect only', inc);
    add('Not answered', blank);
    if (open.length !== all.length) add('Still open only', open, { still_open: true });
    add('Each miss twice', all, { each: 2 });
    if (R.causes) {
      items.push({ separator: true });
      add('Traps only', by('trap'));
      add('Slips, timed at pace', by('slip'), { timing: 'pace' });
      add('Clock losses: a paced set', by('clock'), { timing: 'pace' });
      add('Entry: grid-in rules', by('entry'));
      const gaps = by('gap');
      if (gaps.length) items.push({ label: `Gaps: Learn it first · ${plural(new Set(gaps.map(x => x.key)).size, 'type')}`, onClick: () => drill(fixBody(gaps, { source: 'learn' })) });
    }
    const sw = IT.filter(x => x.sureWrong), gr = IT.filter(x => x.guessed);
    if (sw.length || gr.length) items.push({ separator: true });
    add('Sure and wrong', sw);
    if (gr.length) items.push({ label: `Guessed right · ${n(gr.length)}`, onClick: () => drill(fixBody(gr, { scope: 'all' })) });
    if (scored && R.ledger && all.length) { items.push({ separator: true }); items.push({ label: `Prove it: a timed check · ${n(all.length)}`, onClick: () => drill(fixBody(all, { timed: true, feedback: 'end', order: 'mixed' })) }); }
    if (SEL.size) { items.push({ separator: true }); items.push({ label: `Fix the selection · ${n(SEL.size)}`, onClick: () => drill(fixBody([...SEL].map(id => byId.get(id)), { scope: 'all', order: 'given' })) }); }
    while (items.length && items[items.length - 1].separator) items.pop();
    return items.filter((x, i, a) => !(x.separator && (i === 0 || a[i - 1].separator)));
  }
  function headActions(acts) {
    const all = misses();
    const answered = (R.summary || {}).answered || 0;
    const sampleTip = b => { b.disabled = true; if (UI.tooltip) UI.tooltip(b.parentElement || b, 'Sit your own section to use this.'); return b; };
    if (!R.mine && !sample) return;
    // 1. the primary
    let prim;
    if (!answered) prim = h('button', { type: 'button', class: 'pill', text: `Practise all ${n(IT.length)}` }), prim.addEventListener('click', () => drill({ from_session: SID, scope: 'all' }, prim));
    else if (!all.length) {
      prim = h('button', { type: 'button', class: 'pill', text: test ? 'Harder next · New section' : 'Keep going' });
      prim.addEventListener('click', async () => {
        if (!test) { const nx = UI.nextItems ? UI.nextItems()[0] : null; if (nx) UI.start(nx).catch(() => UI.toast('Couldn’t start it. Try again.')); else location.href = '/practice/'; return; }
        prim.setAttribute('aria-busy', 'true');
        try { const s = await UI.api('/mock/new', { method: 'POST', body: { kind: 'section', subject: R.subject || 'math' } }); location.href = `/test/?s=${encodeURIComponent(s.id)}`; }
        catch (_) { prim.removeAttribute('aria-busy'); UI.toast('Couldn’t start a section. Try again.'); }
      });
    } else {
      const plan = fixPlan();
      const ledger = plan.pts !== null || (scored && R.ledger);
      const size = `${plural(plan.list.length, 'question')} · about ${mins(plan.ms)} min`;
      const label = ledger ? `Win back${plan.pts !== null ? ` ${rx.pts(plan.pts)} pts` : ''}` : `Fix these · ${n(all.length)}`;
      const main = h('button', { type: 'button', class: 'pill', text: label, 'aria-keyshortcuts': 'F', title: ledger ? size : null, 'aria-label': ledger ? `${label}: ${size}` : null });
      main.addEventListener('click', () => drill(scored && R.ledger ? fixBody(plan.list, { order: 'given' }) : fixBody(all), main));
      // the split button's menu half: a plain down caret (.split-btn turns it while open; caret_down would turn twice)
      const more = h('button', { type: 'button', class: 'pill', 'aria-label': 'More ways to fix', 'aria-haspopup': 'menu', 'aria-expanded': 'false', id: 'fixmore' }, UI.icon('caret_down', 16));
      // the menu opens on what the primary does, so its size is one tap away on a phone too
      more.addEventListener('click', () => UI.menu(more, [...(ledger ? [{ group: `${label}: ${size}` }] : []), ...fixMenu()], { label: 'Fix' }));
      prim = h('span', { class: 'split-btn' }, main, more);
      if (plan.pts === null && scored && R.ledger && owner) {
        UI.api(`/session/${encodeURIComponent(SID)}/whatif`, { method: 'POST', body: { right: qids(plan.list) }, quiet: true })
          .then(w => { if (w && w.mid !== undefined) { main.textContent = `Win back ${rx.pts(w.mid - R.ledger.mid)} pts`; main.setAttribute('aria-label', `${main.textContent}: ${size}`); } }).catch(() => {});
      }
    }
    acts.append(prim);
    if (sample) (prim.tagName === 'SPAN' ? [...prim.children] : [prim]).forEach(sampleTip);
    // 2. Review mistakes (on a phone it is the first line of More, and the sticky strip's Review)
    if (all.length) acts.append(btn('Review mistakes', () => openPlayer(all[0].i, { filter: 'misses' }), 'btn rp-rv'));
    // 3. more: Retake as a test leads it
    const dots = h('button', { type: 'button', class: 'btn icon', 'aria-label': 'More', 'aria-haspopup': 'menu' }, UI.icon('more', 18));
    dots.addEventListener('click', () => UI.menu(dots, moreItems(dots), { label: 'More', align: 'end' }));
    acts.append(dots);
  }
  // Retake as a test: Tests' twin (S5); until it lands the server makes a fresh section of the same size
  async function retake(b) {
    b.setAttribute('aria-busy', 'true');
    try { const s = await UI.api('/mock/new', { method: 'POST', body: { kind: 'twin', twin_of: SID, full: R.kind !== 'module', timed: true } }); location.href = `/test/?s=${encodeURIComponent(s.id || s.session)}`; }
    catch (_) { b.removeAttribute('aria-busy'); UI.toast('Couldn’t start the retake. Try again.'); }
  }
  function moreItems(dots) {
    const list = [];
    const all = misses();
    if (all.length && matchMedia('(max-width: 759px)').matches) list.push({ label: 'Review mistakes', onClick: () => openPlayer(all[0].i, { filter: 'misses' }) });
    if (['mock', 'full', 'module', 'diagnostic', 'paper'].includes(R.kind) && (R.mine || sample)) {
      list.push(sample ? { label: 'Retake as a test', sub: 'Sit your own section to use this.', disabled: true }
        : { label: 'Retake as a test', sub: rwSit() ? 'Same skills and difficulty, questions you haven’t seen. Scored like any section.' : 'Same question types, new numbers. Scored like any section.', onClick: () => retake(dots) });
    }
    if (list.length) list.push({ separator: true });
    if (owner) {
      if (drillKind) list.push({ label: `Same set, ${rwSit() ? 'new questions' : 'new numbers'} · ${n(IT.length)}`, onClick: () => drill({ from_session: SID, scope: 'all' }) });
      list.push({ label: `Redo as practice · answers shown · ${n(IT.length)}`, onClick: () => drill({ from_session: SID, scope: 'all', timed: true }) });
      list.push({ label: 'Compare with…', onClick: compareSheet });
      list.push({ label: R.note ? 'Edit note' : 'Add a note', onClick: editNote });
      if (scored && R.ledger) list.push({ label: 'What if…', kbd: 'W', onClick: () => whatifMode(true) });
      list.push({ separator: true });
    }
    list.push({ label: 'Copy link to this report', onClick: () => UI.copyText(`${location.origin}/results/report/?id=${encodeURIComponent(SID)}`, { toast: 'Link copied' }) });
    list.push({ label: 'Print / Save as PDF', onClick: () => window.print() });
    if (misses().length) {
      list.push({ label: PACK.repair, kbd: 'P', onClick: () => packSheet('repair') });
      list.push({ label: PACK.retry, onClick: () => packSheet('retry') });
      if (owner) list.push({ label: PACK.tutor, onClick: () => packSheet('tutor') });
    }
    list.push({ label: 'Download CSV', onClick: csv });
    if (owner && UI.report) list.push({ label: 'Report a problem with this sitting', onClick: () => UI.report({ kind: 'sitting', source: 'report', session: SID, label: R.label }) });
    return list;
  }
  async function compareSheet() {
    const body = h('div', { class: 'rp-cmp-list', 'aria-busy': 'true' }, UI.skel(null, 'rows:4'));
    UI.sheet({ title: 'Compare with…', body, size: 's' });
    try {
      const kind = test ? 'tests' : R.kind;
      const r = await UI.api(`/history?kind=${encodeURIComponent(kind)}&limit=20`, { quiet: true });
      const rows = (r.sessions || []).filter(s => s.id !== SID && (!test || TESTS.includes(s.kind)));
      body.removeAttribute('aria-busy');
      body.replaceChildren(rows.length ? h('ul', { class: 'skp-list' }, rows.map(s => h('li', {},
        h('a', { href: `/results/report/?id=${encodeURIComponent(SID)}&vs=${encodeURIComponent(s.id)}`, text: `${UI.KIND.label(s)}${s.seq ? ` #${s.seq}` : ''} · ${UI.date(s.finished)}` }),
        h('span', { class: 'meta', text: s.estimate && s.estimate.low ? rx.band(s.estimate) : sc(s.right || 0, s.asked || 0) })))) : h('p', { class: 'rp-helper', text: 'No other sittings of this kind yet.' }));
    } catch (_) { body.removeAttribute('aria-busy'); UI.cardError(body, compareSheet, 'Couldn’t load your sittings.'); }
  }

  /* ------------------------------------------------------------ strips: sample, shared, re-scored */
  function drawStrips() {
    const el = $('stick');
    el.hidden = true;
    const root = $('root');
    root.querySelectorAll('.rp-strip').forEach(x => x.remove());
    let text = null;
    if (sample) text = [h('b', { text: 'Sample report · not yours' }), h('a', { class: 'pill sm', href: '/tests/', text: 'Sit your own section' })];
    else if (!R.mine) text = [h('b', { text: 'Shared report · read-only' })];
    const res = R.rescored || [];
    const strips = [];
    if (text) strips.push(h('div', { class: 'rp-strip', 'data-nofold': '' }, text));
    res.forEach(x => {
      const it = byId.get(x.qid);
      strips.push(h('div', { class: 'rp-strip', 'data-nofold': '' }, `${it ? labelOf(it) : 'A question'} was corrected on ${UI.date(x.at)} after a report. This sitting was re-scored: ${rx.band(x.before)} → ${rx.band(x.after)}.`));
    });
    strips.reverse().forEach(s => $('head').after(s));
    stickBar();
  }

  /* the phone's sticky strip once the hero scrolls away: the primary, Jump to, Review, more */
  function stickBar() {
    const el = $('stick');
    el.replaceChildren();
    const jump = h('select', { class: 'field sm', 'aria-label': 'Jump to' }, h('option', { value: '', text: 'Jump to' }),
      jumpList().map(s => h('option', { value: s.id, text: s.label })));
    jump.addEventListener('change', () => { const t = $(jump.value); if (t) t.scrollIntoView({ block: 'start' }); jump.value = ''; });
    const all = misses();
    if (owner && all.length) el.append(btn(`Fix · ${n(all.length)}`, b => drill(scored && R.ledger ? fixBody(fixPlan().list, { order: 'given' }) : fixBody(all), b), 'pill sm'));
    el.append(jump);
    if (all.length) el.append(btn('Review', () => openPlayer(all[0].i, { filter: 'misses' })));
    // a scroll check, not an IntersectionObserver: a jump from below the hero to past it crosses no threshold
    const sync = () => { el.hidden = $('hero').getBoundingClientRect().bottom > 0; };
    if (!stickBar.on) { stickBar.on = true; addEventListener('scroll', () => requestAnimationFrame(sync), { passive: true }); }
    sync();
  }
  function jumpList() {
    return [{ id: 'hero', label: 'Score' }, !$('ledger').hidden && { id: 'ledger', label: scored ? 'Points' : 'Why' },
      { id: 'mistakes', label: `Mistakes${misses().length ? ` ${misses().length}` : ''}` }, { id: 'review', label: `Questions ${IT.length}` },
      !$('breakdown').hidden && { id: 'breakdown', label: 'Breakdown' }, !$('judgement').hidden && { id: 'judgement', label: 'Judgement' },
      !$('pace').hidden && { id: 'pace', label: 'Time' }].filter(Boolean);
  }
  // the header's Fix / Win back pill is the page's one orange: Up next's Start goes .btn while it shows
  function registerSections() { UI.shell({ page: 'report', ownPrimary: !!$('head').querySelector('.pill'), sections: jumpList() }); stickBar(); }

  /* ------------------------------------------------------------ recovery (SR6, SR3): four steps, one row each */
  /* Second look (Start, Show answers now) · Fix n/m closed · Check-ins · Prove it by a date. The one Fix / Win back
     action is the header's; Prove it is in its menu. */
  function drawRecovery() {
    const el = $('recovery');
    el.hidden = true;
    el.replaceChildren();
    if (!owner) return;
    const all = misses();
    const s2 = R.second || {};
    const offered = s2.offered && (s2.unseen || []).length;
    if (!offered && !(scored && all.length)) return;
    const closed = (R.mistakes || []).filter(m => m.closed).length, groups = (R.mistakes || []).length;
    const due = new Date(new Date(R.finished).getTime() + 7 * 864e5);
    const step = (done, name, value, more) => h('li', {}, h('span', { class: 'mk' + (done ? ' on' : ''), 'aria-hidden': 'true' }, done ? UI.icon('check', 10) : null),
      h('span', { class: 'nm' }, name, done ? h('span', { class: 'sr', text: ' (done)' }) : null), h('span', { class: 'v' }, value || ''), more || null);
    const rows = [];
    if (offered) {
      const start = btn('Start second look', startSecond, 'btn sm');
      const skip = btn('Show answers now', async b => {
        b.setAttribute('aria-busy', 'true');
        try { await UI.api(`/session/${encodeURIComponent(SID)}/second/state`, { method: 'POST', body: { state: 'skipped' } }); await refresh(); }
        catch (_) { b.removeAttribute('aria-busy'); UI.toast('Not saved. Try again.'); }
      }, 'quiet');
      if (UI.tooltip) UI.tooltip(start, 'Re-work each miss before you see the answer. It tells a slip from a gap, and it makes the fix stick.');
      rows.push(step(false, 'Second look', `about ${n(Math.max(1, s2.minutes || 1))} min`,
        h('div', { class: 'sub' }, h('p', { class: 'meta', text: `${plural(s2.unseen.length, 'miss', 'misses')} · answers hidden` }), h('div', { class: 'acts' }, start, skip))));
    } else if (s2.looked) rows.push(step(s2.looked >= all.length, 'Second look', h('span', { class: 'rp-num', text: `${n(s2.looked)}/${n(all.length)}` })));
    if (scored && all.length) {
      if (groups) rows.push(step(closed >= groups, 'Fix', h('span', {}, h('span', { class: 'rp-num', text: `${n(closed)}/${n(groups)}` }), ' closed')));
      rows.push(step(false, h('a', { href: '/review/', text: 'Check-ins' }), ''));
      rows.push(step(false, 'Prove it', `by ${UI.date(due)}`));
    }
    head(el, { title: 'Recovery', about: 'recovery', tip: 'Four steps turn these misses into points: look again cold, fix them, pass the check-ins, then prove it on a fresh test. Prove it is in the Win back menu.' });
    el.append(h('ol', { class: 'rp-steps' }, rows));
    const done = new Map([...el.querySelectorAll('.rp-steps > li')].filter(li => li.querySelector('.mk.on')).map(li => [li.querySelector('.nm').textContent, li.querySelector('.mk')]));
    if (recDone && UI.fx) done.forEach((mk, k) => { if (!recDone.has(k)) UI.fx.check(mk); });
    recDone = new Set(done.keys());
  }
  let recDone = null;      // the steps done at the last draw: one that turns done on a refresh draws its check

  /* ------------------------------------------------------------ second look (SR3) */
  function startSecond() {
    const s2 = R.second || {};
    const list = (s2.unseen || []).map(id => byId.get(id)).filter(Boolean);
    if (!list.length || !UI.review) return;
    UI.review(null, list.map(playerItem), { mode: 'second', session: SID, owner: true, title: 'Second look', source: 'report',
      on: {
        second: async (it, answer, meta = {}) => {
          const r = await UI.api(`/session/${encodeURIComponent(SID)}/second`, { method: 'POST', body: { question_id: it.q.id, answer, conf: meta.conf || null, ms: meta.ms || null } });
          dirty = true;
          return { ...r, given: answer };
        },
        seen: it => markSeen([it.q.id]),
        twins: xs => drill(fixBody(xs.map(x => byId.get(x.q ? x.q.id : x.id)).filter(Boolean), { each: 1 })),
        learn: xs => drill(fixBody(xs.map(x => byId.get(x.q ? x.q.id : x.id)).filter(Boolean), { source: 'learn' })),
        done: async () => { try { await UI.api(`/session/${encodeURIComponent(SID)}/second/state`, { method: 'POST', body: { state: 'done' } }); } catch (_) {} dirty = true; },
        close: () => { if (dirty) { dirty = false; refresh(); } },
      } });
  }
  let seenQ = [], seenT = 0;
  function markSeen(ids) {
    if (!owner) return;
    ids.forEach(id => { const x = byId.get(id); if (x && !x.looked) { x.looked = true; seenQ.push(id); } });
    clearTimeout(seenT);
    seenT = setTimeout(async () => {
      const send = seenQ.splice(0);
      if (!send.length) return;
      try { await UI.api(`/session/${encodeURIComponent(SID)}/seen`, { method: 'POST', body: { qids: send }, quiet: true }); dirty = true; } catch (_) {}
      reviewedLine();
    }, 400);
  }

  /* ------------------------------------------------------------ hero */
  function drawHero() {
    const el = $('hero');
    el.hidden = false;
    el.replaceChildren();
    if (chall) return heroChallenge(el);
    if (!scored) return heroCount(el);
    const e = R.estimate, prev = R.previous && R.previous.estimate && R.previous.estimate.low ? R.previous : null;
    const rec = R.recovery || {}, s2 = R.second || {};
    const wrap = h('div', { class: 'rp-hero' });
    const g = h('div', { class: 'rp-gauge' });
    const mid = Math.round((e.low + e.high) / 2);
    const prevName = prev ? `${R.label} #${prev.seq}` : null;
    const differs = x => x && (Math.round(x.low) !== e.low || Math.round(x.high) !== e.high) ? x : null;   // a layer that says nothing new is left out
    const today = (rec.recovered || []).length ? differs(rec.now) : null;
    const sweep = FRESH && !drawHero.swept;
    drawHero.swept = true;
    gaugeApi = UI.gauge(g, { band: e, target: (R.profile || {}).target, previous: prev ? { ...prev.estimate, label: prevName } : null, today, second: differs(s2.with),
      subject: R.subject || 'math', sub: `${UI.SUBJECT ? UI.SUBJECT[R.subject || 'math'].label : 'Math'} · middle ${mid}`, animate: sweep });
    wrap.append(g);
    const f = h('div', { class: 'rp-facts' });
    // movement, and what the score is made of behind a "?" (it was a folded caption under the dial)
    const about = info(`This sitting’s ${UI.subjectLabel(R.subject || 'math')} range, from how many you got right and which module 2 you reached. An estimate from our questions, shown to ±10 points, not a College Board score.`, 'this score');
    let chip;
    if (prev) {
      const d = Math.round(((e.low + e.high) - (prev.estimate.low + prev.estimate.high)) / 20) * 10;   // on tens
      chip = h('span', { class: 'badge lg' + (d > 0 ? '' : ' soft'), text: `${d > 0 ? '+' : d < 0 ? '−' : '±'}${n(Math.abs(d))} vs ${prevName} (${UI.date(prev.finished)})` });
    } else chip = h('span', { class: 'badge soft lg', text: `First ${kindWord()}` });
    f.append(h('div', { class: 'rp-row' }, sweep && UI.spotArt ? h('span', { class: 'rp-done', html: UI.spotArt('done', doneMs()) }) : null, chip, about));
    // the change lands after the sweep, once (the gauge sweeps 1200ms)
    if (sweep && UI.motion) UI.motion.enter(chip, 'nudge', { delay: 1200 });
    // target and the path to it (SR2); the number itself is on the dial, right above
    const tgt = (R.profile || {}).target, path = R.path;
    if (tgt) {
      let line;
      if (path && path.state === 'reached') line = h('p', { class: 'rp-line' }, h('b', { text: 'Target reached' }), ' on this section.');
      else if (path && path.state === 'out_of_reach') line = h('p', { class: 'rp-line' }, `All right on this route reaches ${Math.round(path.estimate.high)}; your target needs the harder Module 2.`);
      else if (path && path.state === 'reachable') line = h('p', { class: 'rp-line' }, h('b', { text: `${plural(path.n, 'question')} from your target` }), ' on this section: ', qchips(path.qids.map(id => byId.get(id)).filter(Boolean)));
      else line = h('p', { class: 'rp-line' }, e.high >= tgt ? h('b', { text: 'Target reached' }) : [h('b', { text: `${n(tgt - e.high)} to your target` }), ' from the high end']);
      f.append(line);
    } else if (owner) f.append(h('p', { class: 'rp-line' }, link('Set a target', '/plan/')));
    // one percentile in view (nationally, else students here); the rest sits under Details (SR5)
    const det = [];
    const rk = R.rank || {}, nat = rk.national;
    const natOk = nat && nat.low_pct !== undefined, stu = rk.pct !== null && rk.pct !== undefined;
    const stuLine = () => h('p', { class: 'rp-line' }, h('b', { text: `${Math.round(rk.pct * (rk.pct <= 1 ? 100 : 1))}%` }), ` of students here scored at or below you on their first ${kindWord()} (${n(rk.n)} students) `,
      h('span', { class: 'badge soft', text: rk.ranked ? 'Ranked · your first' : `Not ranked · retake #${rk.attempt}` }));
    if (natOk) f.append(h('p', { class: 'rp-line' }, `About the `, h('b', { text: pctTxt(nat) }), ' percentile nationally ',
      info(`Your band ${rx.band(e)} sits at about this percentile of SAT takers (College Board, ${nat.year}). Our band is an estimate. This places it on College Board’s published table; it is not a College Board score.`, 'the percentile')));
    if (stu) { if (natOk) det.push(stuLine()); else f.append(stuLine()); }
    else if (!rk.ranked && rk.attempt > 1) {
      const b = h('span', { class: 'badge soft', text: `Not ranked · retake #${rk.attempt}` });
      if (UI.tooltip) UI.tooltip(b, 'Only first sittings are ranked, so retakes can’t inflate it.');
      det.push(h('p', { class: 'rp-line' }, b));
    }
    // the route (Module 1 decides Module 2)
    const m1 = R.module1, rule = R.route_rule || {};
    if (['mock', 'full'].includes(R.kind) && m1 && m1.asked) {
      const up = R.route === 'upper';
      f.append(h('p', { class: 'rp-line' }, `Module 1: `, h('b', { text: `${sc(m1.right, m1.asked)} (${pc(m1.right, m1.asked)}%)` }),
        up ? ' earned the harder Module 2.' : ` → easier Module 2, which tops out at ${rule.lower_ceiling || 580}.${e.capped ? ` Capped at ${rule.lower_ceiling || 580} by the easier route.` : ''}`));
    }
    // Details: what if the easy misses were right (SR2's preset as a fact), recovered since (SR6), twins tried, the total or the R&W field (SR4)
    const fe = R.flip_easy;
    if (fe && fe.count && fe.estimate) det.push(h('p', { class: 'rp-line' }, `${plural(fe.count, `${fe.tier} miss`, `${fe.tier} misses`)}: with them right, `, h('b', { text: rx.band(fe.estimate) }), '.'));
    const nr = (rec.recovered || []).length, no = (rec.open || []).length + (rec.slipping || []).length;
    if (nr) det.push(h('p', { class: 'rp-line' }, h('b', { text: `Recovered ${n(nr)} of ${n(nr + no)}` }), ` · ${rx.pts(rec.points_recovered)} since`, no ? ` · ${n(no)} open (${rx.pts(rec.points_open)})` : ''));
    if (R.twins && R.twins.n) det.push(h('p', { class: 'rp-line' }, h('a', { href: '#mistakes', text: `Tried ${n(R.twins.n)} like this since · ${n(R.twins.right)} right` })));
    const tot = totalBlock();
    if (tot) det.push(tot);
    if (det.length) f.append(h('details', { class: 'fold' }, h('summary', { class: 'fold-s', text: 'Details' }), h('div', {}, det)));
    wrap.append(f);
    el.append(wrap);
    if (!(R.summary || {}).answered) { el.replaceChildren(h('p', { class: 'rp-line', text: 'Nothing answered, so there is no estimate.' })); gaugeApi = null; }
  }
  // the four domains' mastery for the mark (Algebra, Advanced Math, PSDA, Geometry), 0 to 1 of Strong
  const doneMs = () => (rwSit() ? domOrder() : ['Algebra', 'Advanced Math', 'Problem-Solving', 'Geometry']).map(k => { const d = (R.domains || []).find(x => String(x.domain).startsWith(k)); return d ? Math.min(1, (d.mastery || 0) / (UI.STRONG || 0.8)) : 0; });
  // "full section", "module"; a full SAT's section says "full SAT" (its kind keeps the acronym)
  // "84th–86th", or one figure when a 20-point range sits inside one percentile ("1st", never "1st–1st")
  const pctTxt = p => (ord(p.low_pct) === ord(p.high_pct) ? ord(p.low_pct) : `${ord(p.low_pct)}–${ord(p.high_pct)}`);
  const kindWord = () => (R.full ? 'full SAT' : String(R.label || 'section').toLowerCase());
  const ord = v => { const x = Math.round(v); const s = ['th', 'st', 'nd', 'rd'], m = x % 100; return x + (s[(m - 20) % 10] || s[m] || s[0]); };
  // the total this sitting makes with the other section (estimate.total: this one plus the other subject's latest,
  // R&W first); a full SAT's section links its full result instead
  function totalBlock() {
    const t = R.total;
    if (R.full) return h('p', { class: 'rp-line' }, h('a', { href: R.full.href || `/results/full/?id=${encodeURIComponent(R.full.id)}`, text: 'This full SAT’s total and both sections' }));
    if (t && t.low) {
      const said = p => `${UI.subjectLabel(p.subject, true)} ${p.low !== undefined && p.low !== p.high ? `${p.low}–${p.high}` : p.value}${p.id === SID ? ' here' : p.source && p.source !== 'measured' ? ` (${p.source === 'self' ? 'you entered' : cap(p.source)}${p.at ? `, ${UI.date(p.at)}` : ''})` : p.at ? ` (${UI.date(p.at)})` : ''}`;
      return h('div', { class: 'rp-line' }, h('b', { text: `Total ${n(t.low)}–${n(t.high)}` }),
        t.pct ? ` · about the ${pctTxt(t.pct)} percentile` : '',
        (t.parts || []).length ? h('p', { class: 'rp-helper', text: t.parts.map(said).join(' · ') }) : null);
    }
    // no total yet: a Math sitting can take a typed R&W score (a Bluebook or official one); R&W has no Math field
    if (!owner || rwSit()) return '';
    const box = h('div', { class: 'rp-rw' });
    const f = h('input', { class: 'field sm', type: 'number', min: '200', max: '800', step: '10', inputmode: 'numeric', 'aria-label': 'Your R&W score, 200 to 800', placeholder: 'R&W' });
    const src = h('select', { class: 'field sm', 'aria-label': 'Where it is from' }, ['Bluebook', 'Official', 'Other'].map(s => h('option', { value: s.toLowerCase(), text: s })));
    const save = btn('Save', async b => {
      const v = Math.round(+f.value / 10) * 10;
      if (!(v >= 200 && v <= 800)) { f.setAttribute('aria-invalid', 'true'); f.focus(); return; }
      b.setAttribute('aria-busy', 'true');
      try { await UI.api('/me', { method: 'PUT', body: { rw_now: v, rw_source: src.value } }); UI.toast('Saved'); await refresh(); }
      catch (_) { b.removeAttribute('aria-busy'); UI.toast('Not saved. Try again.'); }
    });
    box.append(h('span', { class: 'rp-helper', text: 'Add your R&W score for a total' }), f, src, save);
    return box;
  }
  function heroCount(el) {
    const s = R.summary || {};
    const wrap = h('div', { class: 'rp-hero' });
    const left = h('div', { class: 'rp-gauge rp-count' }, h('span', { class: 'hero-num', text: sc(s.correct || 0, R.asked || 0) }), h('span', { class: 'rp-num', text: `${pc(s.correct || 0, R.asked || 0)}%` }));
    const f = h('div', { class: 'rp-facts' });
    const repairs = IT.filter(x => x.repair && x.bucket !== 'not_reached').length;
    const topics = [...new Set(IT.map(x => topicName(x.topic, x.topic_name)))].slice(0, 3);
    f.append(h('p', { class: 'rp-line', text: [repairs ? `${n((R.asked || 0) - repairs)} asked + ${plural(repairs, 'repair')}` : null, R.ms ? `${mins(R.ms)} min` : null, topics.join(', ')].filter(Boolean).join(' · ') }));
    const opened = (R.mistakes || []).length, fixed = (R.mistakes || []).filter(m => m.closed).length;
    if (opened) f.append(h('p', { class: 'rp-line' }, h('a', { href: '#mistakes', text: plural(opened, 'mistake') + ' opened' }), fixed ? [' · ', h('a', { href: '#mistakes', text: `${n(fixed)} fixed` })] : ''));
    if (R.twins && R.twins.n) f.append(h('p', { class: 'rp-line', text: `Tried ${n(R.twins.n)} like this since · ${n(R.twins.right)} right` }));
    if (!s.answered) f.append(h('p', { class: 'rp-line', text: 'Nothing answered in this set.' }));
    wrap.append(left, f);
    el.append(wrap);
  }
  function heroChallenge(el) {
    const s = R.summary || {}, c = R.challenge || {}, ct = R.contest || {};
    const wrap = h('div', { class: 'rp-hero' });
    wrap.append(h('div', { class: 'rp-gauge rp-count' }, h('span', { class: 'hero-num', text: sc(s.correct || 0, R.asked || 0) }), R.ms ? h('span', { class: 'rp-num', text: tm(R.ms) }) : null));
    const f = h('div', { class: 'rp-facts' });
    if (ct.points !== undefined && ct.points !== null) {
      const pp = ct.points_parts || {};
      f.append(h('p', { class: 'rp-line' }, h('b', { text: `Points ${n(ct.points)}` }), Object.keys(pp).length ? ` · ${Object.entries(pp).map(([k, v]) => `${k} ${n(v)}`).join(' · ')}` : ''));
      f.append(h('p', { class: 'rp-line', text: [`right ${n(s.correct || 0)}`, `wrong ${n(s.incorrect || 0)}`, ct.skipped ? `skipped ${n(ct.skipped)}` : null, ct.voided ? `voided ${n(ct.voided)}` : null].filter(Boolean).join(' · ') }));
    }
    if (c.rank) f.append(h('p', { class: 'rp-line' }, h('b', { text: `#${n(c.rank)} of ${n(c.players)} today` }), c.average ? ` · average ${n(c.average)} / ${n(R.asked)}` : '', ' · ', link('Board', '/challenge/')));
    wrap.append(f);
    el.append(wrap);
  }
  function qchips(list, o = {}) {
    const box = h('span', { class: 'rp-row rp-inline' });
    list.forEach(x => {
      const b = h('button', { type: 'button', class: 'rp-chip rp-qchip', text: `${labelOf(x)}${o.meta ? ` · ${o.meta(x)}` : ''}` });
      b.addEventListener('click', () => openPlayer(x.i));
      box.append(b);
    });
    return box;
  }

  /* ------------------------------------------------------------ where the points went (SR1) */
  function drawLedger() {
    const el = $('ledger');
    el.hidden = true;
    const all = misses();
    if (!all.length) return;
    const L = R.ledger;
    if (!scored || !L) {
      const by = {};
      all.forEach(x => { if (x.cause) by[x.cause] = (by[x.cause] || 0) + 1; });
      if (!Object.keys(by).length) return;
      head(el, { fig: [n(all.length), `${all.length === 1 ? 'miss' : 'misses'}, by cause`] });
      UI.stackBar(el, CAUSES.filter(c => by[c]).map(c => ({ key: c, label: causeName(c), value: by[c], n: by[c] })), { label: 'Misses by cause', noun: 'misses', format: v => n(v),
        onPick: s => setFilter('cause', s.key) });
      return;
    }
    let mode = LS.get('satf.report.ledger', 'cause');
    const seg = UI.seg(null, [{ value: 'cause', label: 'By cause' }, { value: 'tier', label: 'By difficulty' }], { value: mode, label: 'Split the points', onChange: v => { mode = v; LS.set('satf.report.ledger', v); draw(); } });
    head(el, { fig: [rx.pts(L.total), `pts below all right on this route (${rx.band({ low: Math.round(L.all_right.low), high: Math.round(L.all_right.high) })})`], about: 'the points',
      tip: 'Each group’s points are what fixing it is worth on average, whatever you fix first, so the groups add up to the whole gap. Re-scored with this report’s own scoring, on the route you took.', right: seg.el });
    const box = h('div');
    el.append(box);
    function draw() {
      box.replaceChildren();
      const rows = mode === 'tier' ? (L.by_tier || []).slice().sort((a, b) => TIERS.indexOf(a.tier) - TIERS.indexOf(b.tier)).map(t => ({ key: t.tier, label: TIER[t.tier], value: t.printed ?? t.pts, n: t.n }))
        : CAUSES.map(c => (L.by_cause || []).find(x => x.cause === c)).filter(Boolean).map(t => ({ key: t.cause, label: causeName(t.cause), value: t.printed ?? t.pts, n: t.n }));
      UI.stackBar(box, rows.filter(r => r.n), { approx: true, unit: 'pts', label: 'Where your points went', noun: 'misses',
        onPick: s => setFilter(mode === 'tier' ? 'difficulty' : 'cause', s.key) });
    }
    draw();
    const rt = L.route;
    if (rt && rt.short_by > 0 && rt.short_by <= 3) {
      const savers = (rt.savers || []).map(id => byId.get(id)).filter(Boolean);
      el.append(h('p', { class: 'rp-line' }, `Module 1: ${sc(rt.m1_right, rt.m1_asked)} (${pc(rt.m1_right, rt.m1_asked)}%). `,
        h('b', { text: `${n(rt.short_by)} more right would have earned the harder Module 2.` }), savers.length ? [' Your easiest Module 1 misses: ', qchips(savers)] : ''));
      if (rt.cap_cost > 0) el.append(h('p', { class: 'rp-helper', text: `On the easier Module 2 this section tops out at ${(R.route_rule || {}).lower_ceiling || 580}; all right here would have been ${Math.round(L.all_right.high + rt.cap_cost)}.` }));
    }
  }

  /* ------------------------------------------------------------ then vs now (SR7) */
  async function drawCompare() {
    const el = $('compare');
    if (!VS || !owner) { el.hidden = true; return; }
    head(el, { title: 'Then vs now' });
    el.append(UI.skel(null, 'lines:3'));
    let c;
    try { c = await UI.api(`/session/${encodeURIComponent(SID)}/compare?with=${encodeURIComponent(VS)}`, { quiet: true }); }
    catch (e) { UI.cardError(el, drawCompare, e && e.status === 403 ? 'Only your own sittings can be compared.' : 'Couldn’t load the comparison.'); return; }
    const w = c.with || {};
    head(el, { title: 'Then vs now', meta: `with ${w.label || 'that sitting'}${w.seq ? ` #${w.seq}` : ''} · ${c.paired === IT.length ? `same ${n(c.paired)} question types` : `${n(c.paired)} question types appear in both`}` });
    if (c.band && c.band.then && c.band.now) el.append(h('p', { class: 'rp-line' }, h('b', { text: `${rx.band(c.band.then)} → ${rx.band(c.band.now)} (${c.band.delta > 0 ? '+' : ''}${n(c.band.delta)})` })));
    const k = c.counts || {};
    const misses0 = (k.fixed || 0) + (k.still_missing || 0);
    const bits = [misses0 ? `${n(k.fixed || 0)} of your ${n(misses0)} misses are now right` : null, k.slipped ? `${n(k.slipped)} slipped` : null,
      c.ms_per_q && c.ms_per_q.then && c.ms_per_q.now ? `${n(Math.abs(Math.round((c.ms_per_q.then - c.ms_per_q.now) / 1000)))} s ${c.ms_per_q.now < c.ms_per_q.then ? 'faster' : 'slower'} a question` : null].filter(Boolean);
    if (bits.length) el.append(h('p', { class: 'rp-line', text: bits.join(' · ') }));
    if (c.explained && (c.explained.fixed_pts || c.explained.slipped_pts)) el.append(h('p', { class: 'rp-helper', text: `${n(k.fixed || 0)} fixed (${rx.pts(c.explained.fixed_pts)}), ${n(k.slipped || 0)} slipped (${rx.pts(c.explained.slipped_pts).replace('≈ ', '≈ −')})` }));
    if (c.module2 === 'different_route') el.append(h('p', { class: 'rp-line', text: 'Module 2: a different route this time.' }));
    const chipRow = h('div', { class: 'rp-row' });
    [['fixed', 'Fixed'], ['slipped', 'Slipped'], ['still_missing', 'Still missing'], ['held', 'Held']].forEach(([key, lab]) => {
      if (k[key]) chipRow.append(h('span', { class: 'badge soft lg', text: `${lab} · ${n(k[key])}${key === 'still_missing' && k.same_trap ? ` (same trap again ${n(k.same_trap)})` : ''}` }));
    });
    el.append(chipRow);
    const mods = new Map();
    (c.slots || []).forEach(s => { const m = s.module || 0; if (!mods.has(m)) mods.set(m, []); mods.get(m).push(s); });
    const st = x => (!x ? 'not_reached' : x.status === 'blank' ? 'unanswered' : x.status);
    for (const [m, slots] of mods) {
      const g = h('div', { class: 'rp-grid-group' }, h('h3', { text: m ? `Module ${m} · then above, now below` : 'Then above, now below' }));
      UI.strip(g, slots.map(s => ({ status: st(s.then), label: `Slot ${s.n}, then ${st(s.then)}` })), { fit: true, label: 'Then' });
      UI.strip(g, slots.map(s => ({ status: st(s.now), label: `Slot ${s.n}, now ${st(s.now)}` })), { fit: true, onPick: (i) => { const x = slots[i].now && byId.get(slots[i].now.qid); if (x) openPlayer(x.i); } });
      el.append(g);
    }
  }

  /* ------------------------------------------------------------ takeaways (SR14) */
  function drawTakeaways() {
    const el = $('takeaways');
    el.hidden = true;
    // the misses count is the Incorrect tile's and the Fix pill's already: a takeaway never repeats it (the user's rule)
    const list = ((R.debrief || {}).takeaways || []).filter(t => t.kind !== 'misses').slice(0, 3);
    if (!list.length || !owner) return;
    head(el, { title: 'Takeaways' });
    const box = h('ul', { class: 'rp-takes' });
    const all = misses();
    const rushed = IT.filter(x => x.time === 'rushed');
    list.forEach(t => {
      let act = null;
      if (t.kind === 'misses' && all.length) act = btn(scored && R.ledger ? `Fix the top ${Math.min(all.length, fixPlan().list.length)}` : `Fix these ${all.length}`, b => drill(scored && R.ledger ? fixBody(fixPlan().list, { order: 'given' }) : fixBody(all), b));
      else if (t.kind === 'pace' && rushed.length) act = btn(`Careful set · ${n(rushed.length)}`, b => drill(fixBody(rushed, { timing: 'careful' }), b));
      else if (t.kind === 'changes') act = btn('See them', () => setShow('changed'));
      else if (all.length) act = btn('Review', () => openPlayer(all[0].i, { filter: 'misses' }));
      box.append(h('li', {}, h('p', { text: cap(t.text) }), act));
    });
    el.append(box);
  }

  /* ------------------------------------------------------------ tiles */
  function drawTiles() {
    const el = $('tiles');
    el.hidden = false;
    el.replaceChildren();
    const s = R.summary || {};
    const L = R.ledger;
    const tiles = [];
    const filt = key => ({ onClick: () => setShow(S.show === key ? 'all' : key) });
    // "n still open" only when some are closed: all open would repeat the tile's own number
    const openN = IT.filter(x => x.bucket === 'incorrect' && x.trap && x.trap.open).length;
    const openTraps = openN < (s.incorrect || 0) ? openN : 0;
    if (drillKind || chall) {
      const repairs = IT.filter(x => x.repair).length;
      tiles.push({ label: 'Incorrect', value: s.incorrect, sub: openTraps ? `${n(openTraps)} still open` : '', ...filt('incorrect') });
      if (s.unanswered) tiles.push({ label: 'Unanswered', value: s.unanswered, ...filt('unanswered') });
      const repRight = IT.filter(x => x.repair && x.raw === 'correct').length;
      if (repairs) tiles.push({ label: 'Repairs', value: repairs, sub: repRight ? `${n(repRight)} right` : '' });
      const mixed = IT.filter(x => x.raw === 'mixed').length;
      if (mixed) tiles.push({ label: 'Mixed', value: mixed, sub: 'right on a later try', ...filt('mixed') });
      if (s.ms) tiles.push({ label: 'Time', value: tm(s.ms), sub: R.clock_ms && R.timed ? `of ${tm(R.clock_ms)}` : '' });
      if (s.avg_ms) tiles.push({ label: 'Per question', value: tm(s.avg_ms), sub: `test pace ${tm(s.pace_ms)}` });
      const opened = (R.mistakes || []).length, fixed = (R.mistakes || []).filter(m => m.closed).length;
      if (!chall && opened) tiles.push({ label: 'Opened', value: opened, sub: 'named mistakes', href: '#mistakes' });
      if (!chall && fixed) tiles.push({ label: 'Fixed', value: fixed, sub: 'closed since' });
    } else {
      // Correct (with %), Time, Per question and at most one of Unanswered / Flagged / Changed. Incorrect and Accuracy
      // are Correct's own numbers; Second look and Recovered are in Recovery and under the score's Details; what the
      // target needs is the score's own line (one number said once); the "Show" chips filter, so the rows do not.
      tiles.push({ label: 'Correct', value: sc(s.correct || 0, R.asked || 0), sub: [`${Math.round((s.accuracy || 0) * 100)}%`, s.unanswered ? `${Math.round((s.accuracy_answered || 0) * 100)}% of answered` : null].filter(Boolean).join(' · ') });
      const ch = s.changed || {};
      if (s.unanswered) tiles.push({ label: 'Unanswered', value: s.unanswered, sub: [L && L.blank_pts ? `${rx.pts(L.blank_pts).replace('≈ ', '≈ −')} pts` : null, 'a guess costs nothing'].filter(Boolean).join(' · ') });
      else if (s.flagged) tiles.push({ label: 'Flagged', value: s.flagged, sub: s.flagged_wrong ? `${n(s.flagged_wrong)} of them wrong` : 'all right' });
      else if (ch.total) tiles.push({ label: 'Changed', value: ch.total, sub: ch.right_to_wrong ? `${n(ch.right_to_wrong)} right → wrong` : `${n(ch.wrong_to_right)} wrong → right` });
      if (s.ms) tiles.push({ label: 'Time', value: tm(s.ms), sub: R.timed && R.clock_ms ? `of ${tm(R.clock_ms)}` : 'untimed' });
      if (s.avg_ms) tiles.push({ label: 'Per question', value: tm(s.avg_ms), sub: `test pace ${tm(s.pace_ms)}` });
    }
    el.append(h('div', { class: 'card-head' }, h('h2', { text: 'Summary' })), rx.kv(tiles, { label: 'Summary' }));
  }

  /* ------------------------------------------------------------ habits (SR11): a group in Mistakes */
  function habitGroup() {
    const fam = R.habits || [], norms = R.norms || [];
    if (!fam.length && !norms.length) return null;
    const box = h('div', { class: 'rp-group' }, h('h3', { text: 'Habits: the same slip in more than one place' }));
    fam.forEach(f => {
      const list = f.qids.map(id => byId.get(id)).filter(Boolean);
      box.append(h('div', { class: 'rp-vrow' }, h('div', {}, h('h4', { class: 'h3', text: `${f.name} · ${n(list.length)} of your ${n(misses().length)} misses` }),
        f.tell ? h('p', { class: 'rp-helper' }, h('i', { text: f.tell })) : null, qchips(list)),
        owner ? btn('Drill this habit · 8', b => drill({ source: 'habit', habit: f.id, count: 8 }, b)) : ''));
    });
    norms.forEach(m => {
      const list = m.qids.map(id => byId.get(id)).filter(Boolean);
      box.append(h('div', { class: 'rp-vrow' }, h('div', {}, h('h4', { class: 'h3', text: `${cap(m.label)} ×${n(m.hits_all_time || list.length)}` }),
        h('p', { class: 'meta', text: `${plural((m.templates || []).length || 1, 'question type')}` }), qchips(list)),
        owner ? btn('Trap drill · 10', b => drill({ pool: 'related', ids: [m.norm], count: 10 }, b)) : ''));
    });
    return box;
  }

  /* ------------------------------------------------------------ mistakes */
  function mistakeRows() {
    const rows = [];
    const seen = new Set();
    (R.mistakes || []).forEach(m => {
      const list = m.qids.map(id => byId.get(id)).filter(Boolean);
      if (!list.length) return;
      list.forEach(x => seen.add(x.id));
      rows.push({ m, list, first: list[0], group: list.some(x => x.sureWrong) ? 'sure' : (m.closed || list.every(x => x.recovered)) ? 'fixed' : 'open',
        pts: Math.max(...list.map(x => x.pts)) });
    });
    IT.filter(x => x.bucket === 'incorrect' && !seen.has(x.id)).forEach(x => rows.push({ m: null, list: [x], first: x, group: x.sureWrong ? 'sure' : x.st === 'fixed' ? 'fixed' : 'open', pts: x.pts }));
    const blanks = IT.filter(x => x.bucket === 'unanswered');
    return { rows, blanks };
  }
  function drawMistakes() {
    const el = $('mistakes');
    const all = misses();
    const { rows, blanks } = mistakeRows();
    const named = rows.filter(r => r.m && r.m.kind === 'misconception').length, grid = rows.filter(r => r.first.type === 'spr').length;
    const fixed = rows.filter(r => r.group === 'fixed').length;
    head(el, { ...(all.length ? { fig: [n(all.length), all.length === 1 ? 'miss' : 'misses'] } : { title: 'Mistakes' }),
      meta: [named ? `${n(named)} named` : null, grid ? plural(grid, 'grid-in') : null, blanks.length ? `${n(blanks.length)} not answered` : null, fixed ? `${n(fixed)} fixed since` : null].filter(Boolean).join(' · ') });
    if (!all.length) {
      const right = !!(R.summary || {}).answered;
      el.append(h('div', { class: 'rp-clear' }, right && UI.spotArt ? h('span', { html: UI.spotArt('clear') }) : null, h('p', { class: 'rp-helper', text: right ? 'Every question right.' : 'Nothing answered, so nothing to fix yet.' })));
      const hg = habitGroup(); if (hg) el.append(hg); return;
    }
    // "Reviewed 3 of 7" joins the head's one meta line
    const hd = el.querySelector('.card-head');
    let meta = hd.querySelector(':scope > .meta');
    if (!meta) { meta = h('span', { class: 'meta' }); hd.firstElementChild.after(meta); }
    meta.append(h('span', { id: 'reviewed', 'data-sep': meta.textContent ? ' · ' : '' }));
    reviewedLine();
    const sorts = [...(scored && R.ledger ? [{ value: 'points', label: 'Most points' }] : []), { value: 'order', label: 'Question order' }, { value: 'open', label: 'Open first' }, { value: 'topic', label: 'By topic' }, { value: 'hits', label: 'Most hit' }];
    let sort = sorts[0].value;
    const sel = UI.dropdown(null, { label: 'Sort', sm: true, plain: true, noAll: true, default: sort, value: sort, options: sorts, onChange: v => { sort = v; draw(); } });
    hd.append(h('div', { class: 'rp-headr' }, sel.el));
    const body = h('div');
    el.append(body);
    const heldAny = IT.some(x => x.held);
    function draw() {
      body.replaceChildren();
      const order = {
        points: (a, b) => b.pts - a.pts || a.first.i - b.first.i, order: (a, b) => a.first.i - b.first.i,
        open: (a, b) => (a.group === 'open' ? 0 : 1) - (b.group === 'open' ? 0 : 1) || a.first.i - b.first.i,
        topic: (a, b) => String(a.first.topic).localeCompare(String(b.first.topic)) || a.first.i - b.first.i,
        hits: (a, b) => ((b.m && b.m.hits_all_time) || 1) - ((a.m && a.m.hits_all_time) || 1) || a.first.i - b.first.i }[sort];
      const groups = [['sure', 'Sure and wrong'], ['open', 'Open'], ['fixed', 'Fixed since']];
      groups.forEach(([g, lab]) => {
        const rs = rows.filter(r => r.group === g).sort(order);
        if (!rs.length) return;
        const box = h('div', { class: 'rp-group' }, h('h3', { text: `${lab} (${n(rs.length)})` }));
        rs.forEach(r => box.append(missRow(r)));
        body.append(box);
      });
      if (blanks.length) {
        const box = h('div', { class: 'rp-group' }, h('h3', { text: `Not answered (${n(blanks.length)})` }));
        box.append(h('div', { class: 'rp-row' }, qchips(blanks, { meta: x => topicName(x.topic, x.topic_name) }),
          owner ? btn(`Practise these ${n(blanks.length)}`, b => drill(fixBody(blanks), b), 'quiet') : ''));
        body.append(box);
      }
      const hg = habitGroup();
      if (hg) body.append(hg);
      if (heldAny) body.append(h('p', { class: 'rp-helper', 'data-nofold': '', text: 'Misconceptions show once you’ve looked at each miss again.' }));
    }
    draw();
  }
  function reviewedLine() {
    const el = $('reviewed');
    if (!el) return;
    const all = misses(), done = all.filter(x => x.looked).length;
    el.textContent = done ? `${el.dataset.sep || ''}Reviewed ${n(done)} of ${n(all.length)}` : '';
  }
  function missRow(r) {
    const x = r.first, m = r.m;
    const fixed = r.group === 'fixed';
    // a held key names the skill, not the same "hidden" line on every row; the second-look banner says why once
    const label = x.held ? topicName(x.topic, x.topic_name) : m ? cap(m.label) : x.type === 'spr' ? (x.diagnosis && x.diagnosis.text) || `Missed grid-in: ${math(x.answer)}` : cap(x.mistake || 'Incorrect');
    const full = [r.list.map(labelOf).join(' · '), x.held ? null : topicName(x.topic, x.topic_name), TIER[x.difficulty], r.list.length > 1 ? `×${r.list.length} here` : null,
      m && m.hits_all_time > 1 ? `×${n(m.hits_all_time)} all time` : null, rx.worth(x.worth) || null, x.cause ? causeOne(x.cause) : null, x.raw === 'mixed' ? 'right on a later try' : null].filter(Boolean);
    const shown = [r.list.map(labelOf).join(' · '), x.held ? null : topicName(x.topic, x.topic_name), rx.worth(x.worth) || (x.cause ? causeOne(x.cause) : null)].filter(Boolean);
    const state = fixed ? h('span', { class: 'st', text: `✓ Fixed${m && m.closed ? ` ${UI.date(m.closed)}` : ''}` })
      : m && m.open ? h('span', { class: 'st rp-dot', text: `Open, ${n(m.owed || 2)} to close` }) : null;
    const stateText = fixed ? `Fixed${m && m.closed ? ` ${UI.date(m.closed)}` : ''}` : m && m.open ? `Open, ${plural(m.owed || 2, 'correct answer')} to close` : '';
    // the title is the row's Review button (its ::after covers the row); Try one like this and Fix sit in the row menu
    const title = h('button', { type: 'button', class: 'rp-mtitle', text: label, title: [full.join(' · '), stateText].filter(Boolean).join(' · '),
      'aria-label': `${label}. ${full.join(', ')}${stateText ? `. ${stateText}` : ''}. Review ${r.list.map(labelOf).join(', ')}` });
    title.addEventListener('click', () => openPlayer(x.i));
    let menu = null;
    if (owner) {
      const items = [{ label: 'Review', onClick: () => openPlayer(x.i) }];
      if (!x.held) items.push({ label: 'Try one like this', onClick: () => openPlayer(x.i, { twin: true }) });
      items.push({ label: 'Fix', onClick: () => drill(fixBody(r.list, { each: 2 })) });
      menu = h('button', { type: 'button', class: 'btn sm icon rp-menu reveal', 'aria-label': `More for ${labelOf(x)}`, 'aria-haspopup': 'menu' }, UI.icon('more', 18));
      menu.addEventListener('click', () => UI.menu(menu, items, { label: `${labelOf(x)}`, align: 'end' }));
    }
    return h('div', { class: 'rp-mrow' + (fixed ? ' fixed' : '') }, glyph(x.topic) || h('span'), h('div', {}, h('h4', {}, title), h('p', { class: 'meta' }, shown.join(' · '), state ? [' · ', state] : null)), menu);
  }

  /* ------------------------------------------------------------ best value next (SR2) */
  async function drawValue() {
    const el = $('value');
    el.hidden = true;
    const bv = R.best_value || [];
    // ponytail: /whatif is owner-only on the server today (SR2 says any reader); the sample and shared views skip Best value until it opens
    if (!scored || !R.ledger || !bv.length || !owner) return;
    const byTopic = new Map();
    bv.forEach(b => { const x = byId.get(b.qid); if (!x) return; const t = b.topic || x.topic; if (!byTopic.has(t)) byTopic.set(t, { topic: t, list: [], ms: 0 }); const g = byTopic.get(t); g.list.push(x); g.ms += b.budget_ms; });
    const groups = [...byTopic.values()];
    head(el, { title: 'Best value', about: 'best value', tip: 'Cheapest points first: re-scored on this test with those questions right. A guide to order, not a promise.' });
    const body = h('div', { 'aria-busy': 'true' }, UI.skel(null, 'rows:3'));
    el.append(body);
    const rescore = async ids => { try { return await UI.api(`/session/${encodeURIComponent(SID)}/whatif`, { method: 'POST', body: { right: ids }, quiet: true }); } catch (_) { return null; } };
    const got = await Promise.all(groups.slice(0, 8).map(g => rescore(qids(g.list))));
    groups.slice(0, 8).forEach((g, i) => { g.pts = got[i] ? got[i].mid - R.ledger.mid : null; });
    const shown = groups.slice(0, 8).filter(g => g.pts !== null).sort((a, b) => b.pts / b.ms - a.pts / a.ms);
    body.removeAttribute('aria-busy');
    body.replaceChildren();
    if (!shown.length) { el.hidden = true; return; }
    const top = Math.max(...shown.map(g => g.pts)) || 1;
    shown.forEach(g => {
      const row = h('div', { class: 'rp-vrow' },
        h('div', {}, h('b', { class: 'h3' }, glyph(g.topic), ' ', topicName(g.topic, g.list[0].topic_name)), h('p', { class: 'meta', text: `${plural(g.list.length, 'miss', 'misses')} · about ${mins(g.ms)} min` })),
        h('b', { class: 'rp-num', text: `${rx.worth(g.pts) || 'under 5'}` }),
        h('span', { class: 'rp-vbar', style: `--rp: ${Math.max(0.04, g.pts / top)}` }, h('i')));
      if (owner) row.append(h('div', { class: 'rp-row' }, btn(`Fix these ${n(g.list.length)}`, b => drill(fixBody(g.list, { order: 'given' }), b)),
        link('Practise skill', `/practice/?topics=${encodeURIComponent(g.topic)}`)));
      body.append(row);
    });
    if (shown.length >= 2) {
      const top3 = shown.slice(0, 3);
      const w = await rescore(qids(top3.flatMap(g => g.list)));
      const tgt = (R.profile || {}).target;
      if (w) body.append(h('p', { class: 'rp-line' }, `Fix the top ${top3.length}: this test re-scores at `, h('b', { text: rx.band(w) }),
        tgt && w.low <= tgt && w.high >= tgt ? ' · your target falls inside' : '', '.'));
    }
  }

  /* ------------------------------------------------------------ question review */
  function showOk(x, k) {
    switch (k) {
      case 'misses': return x.miss;
      case 'incorrect': return x.bucket === 'incorrect';
      case 'unanswered': return x.bucket === 'unanswered';
      case 'correct': return x.bucket === 'correct';
      case 'flagged': return !!x.flagged;
      case 'saved': return !!x.saved;
      case 'changed': return !!x.changed;
      case 'mixed': case 'skipped': case 'voided': case 'removed': return x.raw === k;
      default: return true;
    }
  }
  function passes(x) {
    const v = fbar ? fbar.values() : {};
    if (!showOk(x, S.show) || (v.result && !showOk(x, v.result))) return false;
    if (v.module && String(x.module) !== v.module) return false;
    if (v.domain && x.domain !== v.domain) return false;
    if (v.topic && x.topic !== v.topic) return false;
    if (v.difficulty && x.difficulty !== v.difficulty) return false;
    if (v.format && x.type !== v.format) return false;
    if (v.time && x.time !== v.time) return false;
    if (v.cause && x.cause !== v.cause) return false;
    const a = S.act;
    if (a === 'hardall' && !(x.miss && x.crowd && x.crowd.n >= 20 && x.crowd.rate <= 0.35)) return false;
    if (a === 'surewrong' && !x.sureWrong) return false;
    if (a === 'guessed' && !x.guessed) return false;
    if (a === 'recovered' && !x.recovered) return false;
    if (a === 'slipping' && !x.slipping) return false;
    if (a === 'unseen' && !(x.miss && !x.looked)) return false;
    if (a === 'note' && !x.note) return false;
    if (['banked', 'sink', 'rushed', 'stuck'].includes(a) && x.pace !== a) return false;
    return true;
  }
  const ACTS = [['unseen', 'Not looked at'], ['surewrong', 'Sure and wrong'], ['guessed', 'Guessed right'], ['recovered', 'Recovered'], ['slipping', 'Slipping'], ['hardall', 'Hard for everyone'], ['note', 'Has note'],
    ['banked', 'Banked'], ['sink', 'Time sink'], ['rushed', 'Rushed'], ['stuck', 'Stuck']];
  function drawReview() {
    const el = $('review');
    head(el, { title: 'Questions' });
    const tools = h('div', { class: 'rp-tools' });
    // Show, with live counts; a 0 is left out (decision 7)
    const cnt = {
      all: IT.length, incorrect: IT.filter(x => x.bucket === 'incorrect').length, unanswered: IT.filter(x => x.bucket === 'unanswered').length,
      correct: IT.filter(x => x.bucket === 'correct').length, flagged: IT.filter(x => x.flagged).length, saved: IT.filter(x => x.saved).length,
      changed: IT.filter(x => x.changed).length, mixed: IT.filter(x => x.raw === 'mixed').length, skipped: IT.filter(x => x.raw === 'skipped').length,
      voided: IT.filter(x => x.raw === 'voided').length, removed: IT.filter(x => x.raw === 'removed').length };
    // Show: the five that matter; the other results (Correct, Saved, Mixed, ...) are a "Result" filter in the Filters sheet
    const SHOW = [['all', 'All'], ['incorrect', 'Incorrect'], ['unanswered', 'Unanswered'], ['flagged', 'Flagged'], ['changed', 'Changed']];
    const MORE = [['correct', 'Correct'], ['saved', 'Saved'], ['mixed', 'Mixed'], ['skipped', 'Skipped'], ['voided', 'Voided'], ['removed', 'Removed from scoring']].filter(([k]) => cnt[k]);
    if (S.show === 'misses') S.show = 'all';
    if (!(S.show in cnt) || (!cnt[S.show] && S.show !== 'all')) S.show = 'all';
    showApi = UI.chips(null, [...SHOW, ...MORE.filter(([k]) => k === S.show)].filter(([k]) => k === 'all' || cnt[k] || k === S.show).map(([value, label]) => ({ value, label, n: cnt[value] })),
      { value: S.show, label: 'Show', onChange: v => { S.show = v; writeQ('show', v === 'all' ? '' : v); applyFilter(); } });
    // Focus ("Act on": not looked at, sure and wrong, time sinks...) leads the Filters sheet
    const actN = Object.fromEntries(ACTS.map(([k]) => [k, IT.filter(x => { const keep = S.act; S.act = k; const ok = passesAct(x); S.act = keep; return ok; }).length]));
    const focusOpts = ACTS.filter(([k]) => actN[k] || S.act === k).map(([value, label]) => ({ value, label, n: actN[value] }));
    // filters (the existing "Filters · n" sheet, on every screen)
    const doms = [...new Set(IT.map(x => x.domain).filter(Boolean))].sort((a, b) => domOrder().indexOf(a) - domOrder().indexOf(b));
    const topics = [...new Set(IT.map(x => x.topic).filter(Boolean))];
    const opt = (list, f) => list.map(v => ({ value: v, label: f ? f(v) : v, n: undefined }));
    const causesHere = CAUSES.filter(c => IT.some(x => x.miss && x.cause === c));
    const filters = [
      focusOpts.length && { key: 'act', label: 'Focus', all: 'Everything', options: focusOpts },
      MORE.length && { key: 'result', label: 'Result', all: 'Any result', options: MORE.map(([value, label]) => ({ value, label, n: cnt[value] })) },
      sectioned && { key: 'module', label: 'Module', all: 'All modules', options: (R.modules || []).map(m => ({ value: String(m.n), label: `Module ${m.n}` })) },
      doms.length > 1 && { key: 'domain', label: 'Domain', all: 'All domains', options: opt(doms) },
      topics.length > 1 && { key: 'topic', label: 'Skill', all: 'All skills', options: opt(topics, t => topicName(t)) },
      { key: 'difficulty', label: 'Difficulty', all: 'All difficulties', options: TIERS.filter(t => IT.some(x => x.difficulty === t)).map(t => ({ value: t, label: TIER[t] })) },
      IT.some(x => x.type === 'spr') && IT.some(x => x.type === 'mcq') && { key: 'format', label: 'Format', all: 'All formats', options: [{ value: 'mcq', label: 'Multiple choice' }, { value: 'spr', label: 'Grid-in' }] },
      IT.some(x => x.time) && { key: 'time', label: 'Time', all: 'Any time', options: [{ value: 'rushed', label: 'Rushed' }, { value: 'long', label: 'Long' }].filter(o => IT.some(x => x.time === o.value)) },
      causesHere.length && { key: 'cause', label: 'Cause', all: 'Any cause', options: causesHere.map(c => ({ value: c, label: causeName(c) })) },
    ].filter(Boolean);
    fbar = UI.filterBar(null, filters, { url: true, label: 'Question filters', onChange: (v, key) => { if (key === 'act' || key === null) S.act = v.act || ''; applyFilter(); } });
    // colour by and view: one small menu
    const colours = [['status', 'Status'], ['difficulty', 'Difficulty'], IT.some(x => x.ms) && ['time', 'Time'], causesHere.length && ['cause', 'Cause'], scored && R.ledger && ['points', 'Points']].filter(Boolean);
    if (!colours.some(([k]) => k === S.colour)) S.colour = 'status';
    const viewBtn = h('button', { type: 'button', class: 'btn sm', 'aria-haspopup': 'menu', text: 'View' });
    viewBtn.addEventListener('click', () => UI.menu(viewBtn, [
      { group: 'Colour by' },
      ...colours.map(([value, label]) => ({ label, radio: 'colour', checked: S.colour === value, close: true, onClick: () => { S.colour = value; writeQ('colour', value === 'status' ? '' : value); drawCells(); drawLegend(); } })),
      { separator: true }, { group: 'View' },
      ...[['grid', 'Grid'], ['table', 'Table']].map(([value, label]) => ({ label, radio: 'view', checked: S.view === value, close: true, onClick: () => { S.view = value; writeQ('view', value === (IT.length > 60 ? 'table' : 'grid') ? '' : value); drawBody(); } })),
    ], { label: 'Colour by and view' }));
    const reset = btn('Reset', () => { S.show = 'all'; S.act = ''; fbar.clear(); writeQ('show', ''); writeQ('act', ''); drawReview(); }, 'quiet');
    reset.id = 'rvreset';
    // one row: Show on the left; Filters (Focus inside), View and Reset on the right. What if stays in More (W)
    tools.append(h('div', { class: 'rp-row' }, showApi.el, h('div', { class: 'rp-tr' }, fbar.el, viewBtn, reset)));
    const wiBox = h('div', { id: 'wibox', hidden: !WI.on });
    tools.append(wiBox);
    el.append(tools);
    reviewBody = h('div', { id: 'rvbody' });
    // the key sits under the grid, at meta size
    el.append(reviewBody, h('div', { class: 'rp-legend', id: 'rvlegend' }), printTable());
    drawLegend();
    drawBody();
    applyFilter();
    if (WI.on) whatifMode(true, true);
  }
  /* §1.17: paper gets every question as a table (your answer, key, mistake, time), whatever the screen shows */
  function printTable() {
    const timed = IT.some(x => x.ms);
    const heads = ['#', 'Skill', 'Your answer', 'Correct', 'Result', 'Mistake', timed && 'Time'].filter(Boolean);
    return h('table', { class: 'rp-ptable', 'aria-hidden': 'true' },
      h('thead', {}, h('tr', {}, heads.map(t => h('th', { text: t })))),
      h('tbody', {}, IT.map(x => h('tr', {}, [
        labelOf(x), topicName(x.topic, x.topic_name),
        x.bucket === 'unanswered' ? 'Not answered' : String(letter(x, x.given) ?? ''),
        x.held ? 'Hidden' : String(x.answer ?? ''),
        `${(UI.STATES[x.st] || {}).glyph || ''} ${(UI.STATES[x.st] || {}).label || x.st}`,
        x.miss && !x.held ? cap(x.mistake || (x.diagnosis && x.diagnosis.text) || '') : '',
        timed && (x.ms ? tm(x.ms) : ''),
      ].filter(v => v !== false).map(v => h('td', { text: v }))))));
  }
  function passesAct(x) {
    const a = S.act;
    if (a === 'hardall') return !!(x.miss && x.crowd && x.crowd.n >= 20 && x.crowd.rate <= 0.35);
    if (a === 'surewrong') return x.sureWrong;
    if (a === 'guessed') return x.guessed;
    if (a === 'recovered') return x.recovered;
    if (a === 'slipping') return x.slipping;
    if (a === 'unseen') return x.miss && !x.looked;
    if (a === 'note') return !!x.note;
    return x.pace === a;
  }
  function writeQ(k, v) {
    const u = new URL(location.href);
    if (v) u.searchParams.set(k, v); else u.searchParams.delete(k);
    if (u.href !== location.href) history.replaceState(history.state, '', u);
  }
  function setShow(v) { S.show = v; writeQ('show', v === 'all' ? '' : v); drawReview(); scrollToReview(); }
  function setAct(v) { S.act = v; writeQ('act', v); drawReview(); scrollToReview(); }
  function setFilter(key, v) {
    S.show = 'all'; writeQ('show', '');
    drawReview();
    if (fbar) fbar.set(key, v);
    scrollToReview();
  }
  const scrollToReview = () => $('review').scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  function applyFilter() {
    const keep = IT.filter(passes).length;
    const v = fbar ? fbar.values() : {};
    const any = S.show !== 'all' || S.act || Object.entries(v).some(([, x]) => x);
    const r = $('rvreset');
    if (r) r.hidden = !any;
    if (S.view === 'table') drawBody(); else drawCells();
    // the count: a filter changed on screen rolls it (a redrawn card starts plain)
    let m = $('rvcount');
    if (!m) { m = h('span', { class: 'meta', id: 'rvcount' }); $('review').querySelector('.card-head').append(m); }
    const old = m.querySelector('.rp-n'), was = old ? old.textContent : '', to = n(any ? keep : IT.length);
    const num = h('span', { class: 'rp-n', text: to });
    m.replaceChildren(num, any ? ` of ${n(IT.length)} shown` : '');
    if (was && was !== to) { num.textContent = was; UI.roll(num, to); }
  }
  function drawLegend() {
    const box = $('rvlegend');
    if (!box) return;
    box.replaceChildren();
    const c = S.colour;
    if (c === 'status') {
      const keys = [['correct'], ['incorrect'], IT.some(x => x.st === 'fixed') && ['fixed'], IT.some(x => x.bucket === 'unanswered') && ['unanswered'], IT.some(x => x.raw === 'mixed') && ['mixed'],
        IT.some(x => x.raw === 'skipped') && ['skipped'], IT.some(x => x.raw === 'voided') && ['voided'], IT.some(x => x.raw === 'removed') && ['removed'],
        IT.some(x => x.raw === 'not_reached') && ['not_reached'], IT.some(x => x.flagged) && ['flag'], IT.some(x => x.repair) && ['repaired'],
        IT.some(x => x.miss && x.trap && x.trap.open) && ['open']].filter(Boolean).map(([k]) => k);
      UI.legend(box, keys);
      if ((R.ledger && R.ledger.route && R.ledger.route.savers || []).length) box.append(h('p', { class: 'rp-helper', text: '▴ would have routed you up' }));
    } else if (c === 'difficulty') UI.legend(box, TIERS);
    else box.append(h('div', { class: 'rp-steps-key' }, ...shadeKey(c).map((t, i) => h('span', {}, h('i', { style: `background: var(--sh-${i})` }), t))));
  }
  function shadeKey(c) {
    if (c === 'time') { const p = PACE_MS() / 1000; return ['under 0:30', `to ${tm(p * 1000)}`, `to ${tm(2 * p * 1000)}`, `${tm(2 * p * 1000)}+`]; }   // the subject's pace and twice it
    if (c === 'points') return ['under 5', '≈ 5–10', '≈ 10–15', '≈ 15+'];
    if (c === 'cause') return CAUSES.filter(k => IT.some(x => x.miss && x.cause === k)).slice(0, 4).map(k => `${(rx.CAUSE[k] || {}).letter || '?'} ${causeName(k)}`);
    return [];
  }
  function shade(x) {
    const c = S.colour;
    if (c === 'time') { if (!x.ms) return null; const s = x.ms / 1000; const p = PACE_MS() / 1000; return { s: s < 30 ? 0 : s < p ? 1 : s < 2 * p ? 2 : 3, corner: '' }; }
    if (c === 'points') { if (!x.miss || !x.pts) return null; return { s: x.pts < 5 ? 0 : x.pts < 10 ? 1 : x.pts < 15 ? 2 : 3, corner: rx.worth(x.worth).replace('≈ ', '') }; }
    if (c === 'cause') { if (!x.miss || !x.cause) return null; const list = CAUSES.filter(k => IT.some(y => y.miss && y.cause === k)); return { s: Math.min(3, list.indexOf(x.cause)), corner: (rx.CAUSE[x.cause] || {}).letter || '' }; }
    return null;
  }
  function cellLabel(x) {
    return [labelOf(x), x.bucket === 'unanswered' ? 'not answered' : (UI.STATES[x.st] || {}).label || x.st, TIER[x.difficulty] && TIER[x.difficulty].toLowerCase(), x.ms ? tm(x.ms) : null,
      x.miss && x.cause ? causeOne(x.cause).toLowerCase() : null, x.miss && rx.worth(x.worth) ? `about ${rx.worth(x.worth).replace('≈ +', '')} points` : null,
      x.flagged ? 'flagged' : null, x.changed ? `changed ${letter(x, x.changed[0])} to ${letter(x, x.changed[1])}` : null].filter(Boolean).join(', ');
  }
  // a module's one line: Module 2 · harder · 31 / 44 · 70% · 31:20 of 35:00 · 2 flagged
  function modLine(m, list) {
    const mod = (R.modules || []).find(x => x.n === m) || ((R.modules || []).length === 1 && !sectioned ? R.modules[0] : null);
    const right = list.filter(x => x.bucket === 'correct').length, asked = list.filter(x => x.bucket !== 'not_reached').length;
    const ms = (mod && mod.ms) || list.reduce((s, x) => s + (x.ms || 0), 0);
    const flagged = (mod && mod.flagged) || list.filter(x => x.flagged).length;
    const route = mod && sectioned ? (mod.n === 2 ? (mod.route === 'upper' ? 'harder' : mod.route === 'lower' ? 'easier' : '') : 'mixed') : '';
    const timed = R.timed && (sectioned || R.kind === 'module');
    return { name: m ? `Module ${m}` : 'Questions', bits: [route || null, sc(right, asked), `${pc(right, asked)}%`, ms ? `${tm(ms)}${timed ? ` of ${MOD_CLOCK()}` : ''}` : null, flagged ? `${n(flagged)} flagged` : null].filter(Boolean).join(' · ') };
  }
  function modGroups() {
    const groups = new Map();
    IT.forEach(x => { const k = sectioned ? x.module : 0; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(x); });
    return groups;
  }
  function drawBody() {
    if (!reviewBody) return;
    reviewBody.replaceChildren();
    if (S.view === 'table') {
      // the table has no module heads: their lines sit above it
      if (sectioned || R.kind === 'module') reviewBody.append(h('div', { class: 'rp-modsum' }, [...modGroups()].map(([m, list]) => { const l = modLine(m, list); return h('p', { class: 'meta' }, h('b', { text: l.name }), ` · ${l.bits}`); })));
      return drawTable();
    }
    reviewGrid = h('div', { class: 'rp-cells', 'data-colour': S.colour });
    for (const [m, list] of modGroups()) {
      const l = modLine(m, list);
      const g = h('div', { class: 'rp-grid-group' }, h('h3', {}, `${l.name} · `, h('span', { class: 'meta', text: l.bits })));
      const cells = h('div', { class: 'cell-grid', role: 'group', 'aria-label': m ? `Module ${m}` : 'Questions' });
      list.forEach(x => cells.append(makeCell(x)));
      g.append(cells);
      reviewGrid.append(g);
    }
    reviewBody.append(reviewGrid);
    drawCells();
  }
  const savers = () => new Set((R.ledger && R.ledger.route && R.ledger.route.savers) || []);
  function makeCell(x) {
    const c = UI.cell(x.st, x.n, { flag: x.flagged ? '' : null, open: x.miss && x.trap && x.trap.open && x.st !== 'fixed' ? '' : null, saved: x.saved ? '' : null, note: x.note ? '' : null, tier: x.difficulty,
      label: cellLabel(x), onClick: e => cellClick(x, e) });
    c.dataset.id = x.id;
    if (savers().has(x.id)) { c.setAttribute('data-saver', ''); c.append(h('i', { class: 'rp-saver', 'aria-hidden': 'true', text: '▴' })); }
    if (x.crowd && x.crowd.n >= 20 && chall && x.crowd.rate !== null) c.append(h('small', { text: `${Math.round(x.crowd.rate * 100)}%` }));
    if (UI.tooltip && matchMedia('(hover: hover)').matches) UI.tooltip(c, () => hoverText(x));
    return c;
  }
  function hoverText(x) {
    return [labelOf(x), (UI.STATES[x.st] || {}).label || x.st, x.miss && x.cause ? causeOne(x.cause) : null, x.miss ? rx.worth(x.worth) || null : null,
      x.crowd && x.crowd.n >= 20 && x.crowd.rate !== null ? `${Math.round(x.crowd.rate * 100)}% of students right` : null,
      x.ms ? `${tm(x.ms)}${x.budget_ms ? ` (budget ${tm(x.budget_ms)})` : ''}` : null].filter(Boolean).join(' · ');
  }
  function drawCells() {
    if (!reviewGrid || S.view === 'table') return;
    reviewGrid.setAttribute('data-colour', S.colour);
    reviewGrid.querySelectorAll('.cell').forEach(c => {
      const x = byId.get(c.dataset.id);
      if (!x) return;
      const off = !passes(x);
      c.toggleAttribute('data-filtered', off);
      c.tabIndex = off ? -1 : 0;
      const sh = shade(x);
      if (sh) { c.dataset.shade = String(sh.s); c.dataset.corner = sh.corner; } else { delete c.dataset.shade; delete c.dataset.corner; }
      c.setAttribute('aria-selected', String(SEL.has(x.id)));
      if (WI.right.has(x.id)) c.dataset.whatif = 'right'; else if (WI.wrong.has(x.id)) c.dataset.whatif = 'wrong'; else delete c.dataset.whatif;
    });
  }
  function drawTable() {
    const rows = IT.filter(passes);
    const held = x => x.held;
    const ans = x => (x.bucket === 'unanswered' ? 'Not answered' : math(letter(x, x.given) || ''));
    const key = x => (held(x) ? 'Hidden' : math(x.answer ?? ''));
    const cols = [
      { key: 'n', label: '#', sort: true, stick: true, value: x => x.i, render: x => labelOf(x) },
      { key: 'skill', label: 'Skill', stick: true, value: x => topicName(x.topic, x.topic_name), render: x => h('span', {}, glyph(x.topic), ' ', topicName(x.topic, x.topic_name), x.skill ? h('small', { class: 'meta', text: ` ${x.skill}` }) : '') },
      { key: 'difficulty', label: 'Difficulty', sort: true, value: x => TIERS.indexOf(x.difficulty), render: x => (UI.dbars ? UI.dbars(x.difficulty) : TIER[x.difficulty]) },
      { key: 'format', label: 'Format', value: x => x.type, render: x => (x.type === 'spr' ? 'Grid-in' : 'MC') },
      IT.some(x => x.ms) && { key: 'time', label: 'Time', sort: true, num: true, value: x => x.ms || 0, render: x => (x.ms ? `${tm(x.ms)}${x.budget_ms ? ` / ${tm(x.budget_ms)}` : ''}` : '') },
      { key: 'given', label: 'Your answer', value: ans, render: x => h('span', { class: 'ans', title: ans(x), text: ans(x) }) },
      { key: 'key', label: 'Correct', value: key, render: x => h('span', { class: 'ans', title: key(x), text: key(x) }) },
      { key: 'result', label: 'Result', sort: true, value: x => ['correct', 'fixed', 'incorrect', 'unanswered'].indexOf(x.st), render: x => h('span', {}, (UI.STATES[x.st] || {}).glyph || '', ' ', (UI.STATES[x.st] || {}).label || x.st) },
      IT.some(x => x.cause) && { key: 'cause', label: 'Cause', sort: true, value: x => (x.miss && x.cause) || '', render: x => (x.miss && x.cause ? causeOne(x.cause) : '') },
      scored && R.ledger && { key: 'worth', label: 'Worth', sort: true, num: true, value: x => (x.miss ? x.pts : 0), render: x => (x.miss ? rx.worth(x.worth) : '') },
      IT.some(x => x.second) && { key: 'second', label: '2nd', title: 'Second look', value: x => (x.second ? (x.second.correct ? 2 : 1) : 0), render: x => (x.second ? (x.second.correct ? '✓' : '✕') : '') },
      IT.some(x => x.crowd && x.crowd.n >= 20) && { key: 'crowd', label: 'Students right', sort: true, num: true, value: x => (x.crowd && x.crowd.n >= 20 ? x.crowd.rate : -1), render: x => (x.crowd && x.crowd.n >= 20 && x.crowd.rate !== null ? `${Math.round(x.crowd.rate * 100)}%` : '') },
      IT.some(x => x.changed) && { key: 'changed', label: '↺', title: 'Answer changed', value: x => (x.changed ? 1 : 0), render: x => (x.changed ? `${letter(x, x.changed[0])}→${letter(x, x.changed[1])}` : '') },
      IT.some(x => x.flagged) && { key: 'flag', label: '⚑', title: 'Flagged', value: x => (x.flagged ? 1 : 0), render: x => (x.flagged ? '⚑' : '') },
      IT.some(x => x.note) && { key: 'note', label: '✎', title: 'Has note', value: x => (x.note ? 1 : 0), render: x => (x.note ? '✎' : '') },
      { key: 'mistake', label: 'Mistake', value: x => x.mistake || '', render: x => h('span', { class: 'mist', title: held(x) ? 'Hidden' : x.mistake || '', text: x.miss ? (held(x) ? 'Hidden' : cap(x.mistake || (x.diagnosis && x.diagnosis.text) || '')) : '' }) },
    ].filter(Boolean);
    reviewTable = UI.table(reviewBody, cols, rows, { label: 'Question table, scrolls sideways', sort: { key: 'n', dir: 'asc' }, onRow: x => openPlayer(x.i), compact: true, empty: 'No questions match these filters.' });
    reviewTable.el.classList.add('rp-table');
  }
  function cellClick(x, e) {
    if (WI.on) return whatifFlip(x);
    if (owner && (e.shiftKey || e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      if (e.shiftKey && lastSel !== null) {
        const a = Math.min(lastSel, x.i), b = Math.max(lastSel, x.i);
        IT.slice(a, b + 1).filter(passes).forEach(y => SEL.add(y.id));
      } else if (SEL.has(x.id)) SEL.delete(x.id); else SEL.add(x.id);
      lastSel = x.i;
      drawCells();
      drawSel();
      return;
    }
    openPlayer(x.i);
  }
  function drawSel() {
    if (!selbar) {
      selbar = UI.selbar($('review'), { onClear: () => { SEL.clear(); drawCells(); drawSel(); },
        actions: k => [{ label: `Fix these ${k}`, primary: true, onClick: () => drill(fixBody([...SEL].map(id => byId.get(id)), { scope: 'all', order: 'given' })) },
          scored && R.ledger && { label: 'What if these were right', onClick: () => { whatifMode(true); [...SEL].forEach(id => { const x = byId.get(id); if (x.miss) WI.right.add(id); }); whatifRun(); } }].filter(Boolean) });
    }
    selbar.update(SEL.size);
  }

  /* ------------------------------------------------------------ What if (SR2) */
  function whatifMode(on, silent) {
    if (!scored || !R.ledger || !owner) return;
    WI.on = on;
    const b = $('wibtn');
    if (b) b.setAttribute('aria-pressed', String(on));
    const box = $('wibox');
    if (!on) { WI.right.clear(); WI.wrong.clear(); WI.band = null; if (gaugeApi) gaugeApi.set({ whatif: null }); if (box) box.hidden = true; drawCells(); return; }
    if (!box) return;
    box.hidden = false;
    box.className = 'rp-whatif';
    box.replaceChildren();
    const line = h('span', { id: 'wiline', class: 'rp-line', text: 'What if: tap a miss to mark it right, or a right answer to mark it wrong.' });
    const preset = (label, list) => (list.length ? btn(`${label} · ${n(list.length)}`, () => { WI.right.clear(); WI.wrong.clear(); list.forEach(x => (x.miss ? WI.right : WI.wrong).add(x.id)); whatifRun(); }) : null);
    const all = misses();
    box.append(line, preset('Flip my slips', all.filter(x => x.cause === 'slip')), preset('Flip easy misses', all.filter(x => x.difficulty === 'easy')),
      preset('Flip clock losses', all.filter(x => x.cause === 'clock')), preset('Drop guessed rights', IT.filter(x => x.guessed)),
      btn('Reset', () => { WI.right.clear(); WI.wrong.clear(); whatifRun(); }, 'quiet'), btn('Done', () => whatifMode(false), 'quiet'));
    if (!silent) scrollToReview();
    drawCells();
  }
  function whatifFlip(x) {
    if (x.bucket === 'not_reached') return;
    if (x.miss) { if (WI.right.has(x.id)) WI.right.delete(x.id); else WI.right.add(x.id); }
    else if (WI.wrong.has(x.id)) WI.wrong.delete(x.id); else WI.wrong.add(x.id);
    whatifRun();
  }
  function whatifRun() {
    drawCells();
    clearTimeout(WI.timer);
    WI.timer = setTimeout(async () => {
      const line = $('wiline');
      const k = WI.right.size + WI.wrong.size;
      if (!k) { if (gaugeApi) gaugeApi.set({ whatif: null }); if (line) line.textContent = 'What if: tap a miss to mark it right, or a right answer to mark it wrong.'; return; }
      try {
        const w = await UI.api(`/session/${encodeURIComponent(SID)}/whatif`, { method: 'POST', body: { right: [...WI.right], wrong: [...WI.wrong] }, quiet: true });
        WI.band = w;
        if (gaugeApi) gaugeApi.set({ whatif: { low: w.low, high: w.high } });
        const d = Math.round(w.mid - R.ledger.mid);
        if (line) {
          // the band rolls from the last answer to this one as cells flip
          const old = line.querySelector('.rp-wb'), was = old ? old.textContent : '', to = rx.band(w);
          const b = h('b', { class: 'rp-wb', text: to });
          line.replaceChildren('What if: ', b, ` (${d >= 0 ? '+' : '−'}${n(Math.abs(d))}) · ${n(k)} flipped · Module 2 stays as you sat it`);
          if (was && was !== to) { b.textContent = was; UI.roll(b, to); }
        }
      } catch (_) { if (line) line.textContent = 'Couldn’t re-score that. Try again.'; }
    }, 150);
  }

  /* ------------------------------------------------------------ domains, skills (the modules are the question grid's heads) */
  function drawDomains() {
    const el = $('domains');
    el.hidden = true;
    const doms = (R.domains || []).filter(d => d.asked);
    if (!doms.length) return;
    const L = R.ledger;
    const lost = d => ((L && L.by_domain) || []).find(x => x.domain === d.domain);
    let mode = scored && L ? LS.get('satf.report.domains', 'points') : 'sat';
    let order = null;
    if (scored && L) {
      order = UI.dropdown(null, { label: 'Order', sm: true, plain: true, noAll: true, default: 'points', value: mode,
        options: [{ value: 'points', label: 'By points' }, { value: 'sat', label: 'SAT order' }], onChange: v => { mode = v; LS.set('satf.report.domains', mode); draw(); } }).el;
    }
    el.hidden = false;
    el.replaceChildren(h('div', { class: 'rp-domtools' }, order, info('A domain is a handful of questions, so read one weak one as a hint, not a verdict.', 'domains')));
    const box = h('div', { class: 'rp-doms' });
    el.append(box);
    const check = h('div', { class: 'rp-domnote' });
    el.append(check);
    function draw() {
      box.replaceChildren();
      check.replaceChildren();
      const list = doms.slice().sort(mode === 'points' ? (a, b) => ((lost(b) || {}).pts || 0) - ((lost(a) || {}).pts || 0) : (a, b) => domOrder().indexOf(a.domain) - domOrder().indexOf(b.domain));
      list.forEach(d => {
        const qs = IT.filter(x => x.domain === d.domain);
        const lo = lost(d);
        const card = h('div', { class: 'rp-dom' }, h('h3', { text: d.domain }),
          h('div', { class: 'rp-row' }, h('span', { class: 'v', text: `${Math.round((d.pct || 0) * 100)}%` }), h('span', { class: 'meta', text: sc(d.right, d.asked) })));
        const word = d.band || UI.masteryWord(d.mastery, d.asked);
        card.append(h('div', { class: 'skill-m' }, h('span', { class: 'mbar', role: 'img', 'aria-label': `Mastery: ${word}`, title: 'Weighted by difficulty, like the domain bars on an official score report.' },
          h('i', { style: `--m: ${Math.max(0, Math.min(1, d.mastery || 0))}` })), h('span', { class: 'skill-word', text: word })));
        UI.strip(card, qs.map(x => ({ status: x.st, label: cellLabel(x) })), { fit: true, onPick: i => openPlayer(qs[i].i) });
        card.append(h('p', { class: 'meta', text: `${plural(d.asked, 'question')} · ${Math.round((d.share || 0) * 100)}% of the sitting` }));
        if (d.previous && d.previous.asked) { const dd = d.right - d.previous.right; card.append(h('p', { class: 'meta', text: `${dd >= 0 ? '+' : '−'}${n(Math.abs(dd))} correct vs last time` })); }
        if (lo && lo.pts && L.total) card.append(h('p', { class: 'meta', text: `${rx.pts(lo.printed ?? lo.pts).replace('≈ ', '≈ −')} pts · ${Math.round(lo.pts / L.total * 100)}% of your gap` }));
        const dm = qs.filter(x => x.miss);
        if (owner && dm.length) card.append(h('div', { class: 'rp-row' }, btn(`Fix this domain · ${n(dm.length)}`, b => drill(fixBody(dm), b))));
        box.append(card);
      });
      if (L && L.total) {
        const odd = doms.map(d => ({ d, lostShare: ((lost(d) || {}).pts || 0) / L.total, share: d.share || 0 })).filter(x => Math.abs(x.lostShare - x.share) >= 0.1).sort((a, b) => b.lostShare - a.lostShare)[0];
        if (odd) check.append(h('p', { class: 'rp-helper', text: `${odd.d.domain} is ${Math.round(odd.share * 100)}% of the section and ${Math.round(odd.lostShare * 100)}% of the points you lost.` }));
      }
    }
    draw();
  }
  function drawSkills() {
    const el = $('skills');
    el.hidden = true;
    const ts = (R.topics || []).filter(t => t.topic && t.asked);
    if (!ts.length) return;
    el.hidden = false;
    el.replaceChildren();
    const box = h('div', { role: 'list' });
    ts.slice().sort((a, b) => (b.asked - b.right) - (a.asked - a.right) || b.asked - a.asked).forEach(t => {
      const row = h('div', { class: 'rp-srow', role: 'listitem', tabindex: '0', 'aria-label': `${topicName(t.topic, t.name)}, ${t.right} of ${t.asked} right. Show its questions.` },
        h('span', { class: 'nm' }, glyph(t.topic), topicName(t.topic, t.name), h('span', { class: 'meta', text: t.domain || '' })),
        h('span', { class: 'rp-num', text: `${sc(t.right, t.asked)}` }),
        h('span', { class: 'rp-mb', style: `--a: ${Math.max(0, Math.min(1, t.after || 0))}; --b: ${Math.max(0, Math.min(1, t.before || 0))}`, role: 'img', 'aria-label': `Mastery ${UI.masteryWord(t.before)} before, ${UI.masteryWord(t.after)} now` }, h('i'), h('b')),
        h('span', { class: 'rp-row' }, t.open ? h('span', { class: 'rp-dot meta', text: ` ${n(t.open)} open` }) : null, h('a', { class: 'quiet', href: `/practice/?topics=${encodeURIComponent(t.topic)}`, text: 'Practise' })));
      const go = e => { if (e.target.closest('a')) return; setFilter('topic', t.topic); };
      row.addEventListener('click', go);
      row.addEventListener('keydown', e => { if (e.key === 'Enter') go(e); });
      box.append(row);
    });
    el.append(box);
  }

  /* ------------------------------------------------------------ judgement (SR9) */
  function drawJudgement() {
    const el = $('judgement');
    el.hidden = true;
    const J = R.judgement || {};
    const s = R.summary || {};
    const panels = [];
    const cf = J.conf || {};
    if ((J.tagged || 0) >= 5) {
      const p = h('div', {}, h('h3', { text: 'Confidence' }));
      const grid = h('div', { class: 'rp-conf' }, h('span', { class: 'h' }), h('span', { class: 'h', text: 'Right' }), h('span', { class: 'h', text: 'Wrong' }));
      ['sure', 'unsure', 'guess'].forEach(k => { const c = cf[k] || {}; grid.append(h('span', { class: 'h', text: cap(k) }), h('span', { text: n(c.right || 0) }), h('span', { text: n(c.wrong || 0) })); });
      p.append(grid);
      const sw = IT.filter(x => x.sureWrong), gr = IT.filter(x => x.guessed);
      if (sw.length) p.append(h('p', { class: 'rp-line' }, h('b', { text: `Sure and wrong · ${n(sw.length)}` }), ': misconceptions you believe ', owner ? btn(`Fix these ${n(sw.length)}`, b => drill(fixBody(sw), b)) : ''));
      if (gr.length) p.append(h('p', { class: 'rp-line' }, h('b', { text: `Guessed right · ${n(gr.length)}` }), ': points you don’t own yet', J.without_guesses ? ` · without them ${rx.band(J.without_guesses)}` : ''));
      panels.push(p);
    } else if (owner && test) {
      const p = h('div', {}, h('h3', { text: 'Confidence' }));
      const b = btn('Ask how sure I am on my next test', async bb => {
        bb.setAttribute('aria-busy', 'true');
        try { await UI.prefs.set({ confidence: 'ask' }); bb.replaceWith(h('p', { class: 'rp-line', text: 'On. Your next test asks Sure · Unsure · Guess on each question.' })); }
        catch (_) { bb.removeAttribute('aria-busy'); UI.toast('Not saved. Try again.'); }
      });
      if (UI.tooltip) UI.tooltip(b, 'One tap a question, and the report shows which mistakes you were sure of.');
      p.append(b);
      panels.push(p);
    }
    const fl = J.flags || {};
    if (fl.flagged) {
      panels.push(h('div', {}, h('h3', { text: 'Flags' }), h('p', { class: 'rp-line', text: [`Flagged ${n(fl.flagged)}`, fl.revisited ? `went back to ${n(fl.revisited)}` : null, fl.changed_right ? `${n(fl.changed_right)} changed wrong → right` : null, fl.left_wrong ? `${n(fl.left_wrong)} flagged and left wrong` : null].filter(Boolean).join(' · ') }),
        h('p', { class: 'rp-helper', text: fl.changed_right ? 'Keep flagging and coming back.' : fl.flagged - (fl.revisited || 0) >= 2 ? 'Leave 3 minutes at the end for your flags.' : '' })));
    }
    const ch = s.changed || {};
    if (ch.total) {
      const p = h('div', {}, h('h3', { text: 'Answer changes' }));
      const b = h('button', { type: 'button', class: 'rp-chip', text: `You changed ${plural(ch.total, 'answer')}: ${[ch.wrong_to_right && `${n(ch.wrong_to_right)} wrong → right`, ch.right_to_wrong && `${n(ch.right_to_wrong)} right → wrong`, ch.wrong_to_wrong && `${n(ch.wrong_to_wrong)} wrong → wrong`].filter(Boolean).join(' · ')}` });
      b.addEventListener('click', () => setShow('changed'));
      p.append(b);
      const net = (ch.wrong_to_right || 0) - (ch.right_to_wrong || 0);
      if (ch.right_to_wrong || ch.wrong_to_right) p.append(h('p', { class: 'rp-helper', text: net < 0 ? `Second-guessing cost ${plural(-net, 'question')}.` : net > 0 ? `Changing paid off ${net === 1 ? 'once' : `${n(net)} times`}.` : 'Changes broke even.' }));
      const ins = J.instinct || {};
      if (ins.changes >= 5) p.append(h('p', { class: 'rp-helper', text: `When you change an answer you end up right ${pc(ins.right, ins.changes)}% of the time (${n(ins.changes)} changes).` }));
      panels.push(p);
    }
    // time away and pauses are in the header's meta line
    const ck = (J.crossed_key || []).map(id => byId.get(id)).filter(Boolean);
    if (ck.length) panels.push(h('div', {}, h('h3', { text: 'Eliminations' }), h('p', { class: 'rp-line' }, `You crossed out the right answer ${n(ck.length)}× `, qchips(ck))));
    if (!panels.length) return;
    head(el, { title: 'Judgement' });
    el.append(h('div', { class: 'rp-judge' }, panels));
  }

  /* ------------------------------------------------------------ difficulty and format */
  function drawSplit() {
    const el = $('split'), fe = $('format');
    el.hidden = fe.hidden = true;
    const d = R.by_difficulty || [], f = R.by_format || [];
    if (!d.length) return;
    const budget = t => { const xs = IT.filter(x => x.difficulty === t && x.budget_ms); return xs.length ? xs[0].budget_ms : null; };
    const row = (lab, r, key, val, extra) => {
      const b = h('button', { type: 'button', class: 'rp-bar', style: `--rp: ${r.asked ? r.right / r.asked : 0}` }, h('span', {}, lab),
        h('span', { class: 't' }, h('i')), h('span', { class: 'rp-num', text: [`${sc(r.right, r.asked)} · ${pc(r.right, r.asked)}%`, r.avg_ms ? `avg ${tm(r.avg_ms)}` : null, extra].filter(Boolean).join(' · ') }));
      b.addEventListener('click', () => setFilter(key, val));
      return b;
    };
    const bars = h('div', { class: 'rp-bars' });
    d.forEach(r => bars.append(row(UI.dbars ? UI.dbars(r.key) : TIER[r.key], r, 'difficulty', r.key, r.avg_ms && budget(r.key) ? `budget ${tm(budget(r.key))}` : null)));
    el.hidden = false;
    el.replaceChildren(bars);
    if (f.length > 1) {
      const fb = h('div', { class: 'rp-bars' });
      f.forEach(r => fb.append(row(FORMAT[r.key] || r.key, r, 'format', r.key)));
      fe.hidden = false;
      fe.replaceChildren(fb);
    }
  }

  /* one Breakdown card: Domain, Skill, Difficulty, Format behind a segmented control (the panels above fill themselves) */
  function drawBreakdown() {
    const el = $('breakdown');
    const panels = [['domains', 'Domain'], ['skills', 'Skill'], ['split', 'Difficulty'], ['format', 'Format']].filter(([id]) => !$(id).hidden);
    el.hidden = !panels.length;
    el.querySelector(':scope > .card-head')?.remove();
    if (!panels.length) return;
    let mode = LS.get('satf.report.breakdown', 'domains');
    if (!panels.some(([id]) => id === mode)) mode = panels[0][0];
    const show = () => panels.forEach(([id]) => { $(id).hidden = id !== mode; });
    const seg = panels.length > 1 ? UI.seg(null, panels.map(([value, label]) => ({ value, label })), { value: mode, label: 'Break down by', onChange: v => { mode = v; LS.set('satf.report.breakdown', v); show(); } }) : null;
    el.prepend(h('div', { class: 'card-head' }, h('h2', { text: 'Breakdown' }), seg ? h('div', { class: 'rp-headr' }, seg.el) : null));
    show();
  }

  /* ------------------------------------------------------------ pace (SR13) */
  function drawPace() {
    const el = $('pace');
    el.hidden = true;
    if (!test && !drillKind) return;
    head(el, { title: 'Time' });
    const timed = IT.filter(x => x.ms);
    if (!timed.length) { el.append(h('p', { class: 'rp-helper', text: 'Times were not recorded for this sitting.' })); return; }
    const groups = new Map();
    IT.forEach(x => { const k = sectioned ? x.module : 0; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(x); });
    for (const [m, list] of groups) {
      const box = h('div', { class: 'rp-grid-group' }, m ? h('h3', { text: `Module ${m}` }) : null);
      clockReplay(box, m, list);
      UI.barChart(box, list.map(x => ({ key: labelOf(x), label: String(x.n), value: Math.min(300, (x.ms || 0) / 1000), status: x.st, budget: x.budget_ms ? x.budget_ms / 1000 : null,
        tip: `${labelOf(x)} · ${tm(x.ms)} · ${(UI.STATES[x.st] || {}).label || x.st} · ${TIER[x.difficulty] || ''}` })),
      { unit: 's', pace: { value: ((R.summary || {}).pace_ms || PACE_MS()) / 1000, label: `Test pace ${tm((R.summary || {}).pace_ms || PACE_MS())}` }, max: 300, labels: 'label',
        label: m ? `Seconds per question, Module ${m}` : 'Seconds per question', onPick: r => { const x = list.find(y => labelOf(y) === r.key); if (x) openPlayer(x.i); } });
      el.append(box);
    }
    if (!(R.pace || {}).visits_recorded && test) el.append(h('p', { class: 'rp-helper', text: 'Visit order was not recorded for this sitting.' }));
    const chipRow = h('div', { class: 'rp-row' });
    [['banked', 'Banked'], ['sink', 'Time sink'], ['rushed', 'Rushed'], ['stuck', 'Stuck']].forEach(([k, lab]) => {
      const c = IT.filter(x => x.pace === k).length;
      if (!c) return;
      const b = h('button', { type: 'button', class: 'rp-chip', 'aria-pressed': String(S.act === k), text: `${lab} · ${n(c)}` });
      b.addEventListener('click', () => setAct(S.act === k ? '' : k));
      chipRow.append(b);
    });
    if (chipRow.childNodes.length) el.append(chipRow);
    const sink = IT.filter(x => x.pace === 'sink'), blanks = IT.filter(x => x.bucket === 'unanswered');
    if (sink.length) el.append(h('p', { class: 'rp-line', text: `Time sinks cost ${tm(sink.reduce((s, x) => s + x.ms - (x.budget_ms || 0), 0))}.${blanks.length ? ` At budget you would have had time to open your ${plural(blanks.length, 'blank')}.` : ''}` }));
    if (blanks.length && R.ledger && R.ledger.blank_pts) el.append(h('p', { class: 'rp-line', text: `Those ${plural(blanks.length, 'blank')} are worth ${rx.pts(R.ledger.blank_pts).replace('≈ ', '≈ +')} if right.` }));
    if (blanks.length && scored) el.append(h('p', { class: 'rp-line', text: blanks.some(x => x.type === 'mcq') ? 'A guess on a multiple-choice blank is right 1 time in 4. Never leave one blank.' : 'Enter your best estimate: a blank grid-in scores nothing.' }));
    if (owner) {
      const rushed = IT.filter(x => x.pace === 'rushed'), stuck = IT.filter(x => x.pace === 'stuck');
      const acts = h('div', { class: 'rp-row' });
      if (sink.length) acts.append(btn(`Speed set · ${n(sink.length)}`, b => drill(fixBody(sink, { scope: 'all', timing: 'pace' }), b)));
      if (rushed.length) acts.append(btn(`Careful set · ${n(rushed.length)}`, b => drill(fixBody(rushed, { timing: 'careful' }), b)));
      if (stuck.length) acts.append(btn(`Learn it · ${n(new Set(stuck.map(x => x.key)).size)}`, b => drill(fixBody(stuck, { source: 'learn' }), b)));
      if (acts.childNodes.length) el.append(acts);
    }
  }

  /* SR13's clock replay: one lane per module from the runner's visit log (pace.modules[].visits),
     with its auto lines; a sitting without visits keeps the bars and the line above */
  function clockReplay(box, m, list) {
    const pm = ((R.pace || {}).modules || []).find(p => Number(p.n) === (m || 1));
    if (!pm || !(pm.visits || []).length || !UI.clockLane) return;
    const byId = new Map(list.map(x => [x.id, x]));
    const items = {}, budgets = {};
    list.forEach(x => {
      items[x.id] = { label: labelOf(x), status: x.st, flag: !!x.flagged, changed: x.changed ? `${letter(x, x.changed[0])} → ${letter(x, x.changed[1])}` : '' };
      if (x.budget_ms) budgets[x.id] = x.budget_ms;
    });
    const dur = R.clock_ms ? R.clock_ms / Math.max(1, (R.modules || []).length) : 0;
    const lane = h('div', { class: 'rp-lane' });
    UI.clockLane(lane, pm.visits, { items, budgets, order: qids(list), duration: dur || undefined, marks: dur ? [{ t: dur, kind: 'end' }] : [],
      label: m ? `Clock replay, Module ${m}` : 'Clock replay', onPick: q => { const x = byId.get(q); if (x) openPlayer(x.i); } });
    box.append(lane);
    const lab = q => (byId.get(q) ? labelOf(byId.get(q)) : '');
    const lines = [];
    if (pm.behind_at && pm.behind_ms) {
      const rest = list.length - list.findIndex(x => x.id === pm.behind_at) - 1;
      lines.push(`${tm(pm.behind_ms)} behind pace by ${lab(pm.behind_at)}${pm.left_for_rest_ms != null && rest > 0 ? `, with ${tm(pm.left_for_rest_ms)} left for the last ${n(rest)}` : ''}`);
    }
    if (pm.returns_worked) lines.push(`Skip and return worked ${pm.returns_worked === 1 ? 'once' : `${n(pm.returns_worked)} times`}`);
    if ((pm.never_opened || []).length) lines.push(`${plural(pm.never_opened.length, 'blank')} ${pm.never_opened.length === 1 ? 'was' : 'were'} never opened`);
    (pm.starved || []).forEach(s => {
      const after = (s.after || []).map(q => byId.get(q)).filter(Boolean);
      if (!after.length) return;
      const span = after.length > 1 ? `${labelOf(after[0])}–${after[after.length - 1].n}` : labelOf(after[0]);
      lines.push(`${lab(s.qid)} took ${tm(s.ms)} and was wrong; ${span} got ${tm(after.reduce((t, x) => t + (x.ms || 0), 0))} between them`);
    });
    lines.forEach(t => box.append(h('p', { class: 'rp-line', text: t })));
  }

  /* ------------------------------------------------------------ up next */
  function drawNext() {
    const el = $('next');
    el.hidden = true;
    if (!owner) return;
    head(el, { title: 'Up next' });
    const rows = h('div');
    // one row each: what it is and its size, Start on the right
    const row = (name, meta, go) => h('div', { class: 'rp-vrow' }, h('div', {}, h('h4', { class: 'h3', text: name }), h('p', { class: 'meta', text: meta })), btn('Start', go));
    // the Pressure check, offered by the test window's hand-in (X13); gone once it has run
    let pr = null;
    try { pr = R.pressure ? null : JSON.parse(sessionStorage.getItem(`satf.pressure.${SID}`) || 'null'); } catch (_) {}
    if (pr) rows.append(row('Pressure check', `${pr.n} ${pr.n === 1 ? 'question' : 'questions'} · about ${pr.minutes} min`, async b => {
      b.setAttribute('aria-busy', 'true');
      try { const x = await UI.api(`/session/${encodeURIComponent(SID)}/pressure`, { method: 'POST' }); location.href = `/practice/session/?id=${encodeURIComponent(x.id)}`; }
      catch (e) { b.removeAttribute('aria-busy'); UI.toast(e.status === 409 ? 'The pressure check has closed for this sitting.' : `Couldn’t start it: ${e.message}`); }
    }));
    const bv = R.best_value || [];
    if (scored && bv.length) {
      const top = bv[0], x = byId.get(top.qid);
      const same = x ? IT.filter(y => y.miss && y.topic === x.topic) : [];
      if (same.length) {
        rows.append(row(topicName(x.topic, x.topic_name), `${rx.worth(top.pts) || 'under 5'} · about ${mins(same.reduce((s, y) => s + (y.budget_ms || PACE_MS()), 0))} min`, b => drill(fixBody(same, { order: 'given' }), b)));
      }
    }
    el.append(rows, h('div', { class: 'rp-row' }, link('New section', `/tests/?subject=${R.subject || 'math'}`)));
  }

  /* ------------------------------------------------------------ the player (F3's UI.review) */
  function playerItem(x) {
    const Q = ['id', 'type', 'stem', 'choices', 'latex', 'figure', 'figure_alt', 'table', 'topic', 'topic_name', 'skill', 'name', 'about', 'difficulty', 'seed', 'subject', 'repair', 'filler', 'desmos', 'ask', 'text'];
    const q = { template: x.key, number: x.n };
    Q.forEach(k => { if (x[k] !== undefined) q[k] = x[k]; });
    const fb = { correct: x.raw === 'correct', given: x.given, answer: x.answer, reasons: x.reasons, rationale: x.rationale, accepted: x.accepted, steps: x.steps, method: x.method,
      option_steps: x.option_steps, diverge: x.diverge, wrong_step: x.wrong_step, diagnosis: x.diagnosis ? x.diagnosis.text || x.diagnosis : null, mistake: x.mistake, about: x.about };
    if (x.held) { delete fb.answer; delete fb.reasons; delete fb.rationale; }
    if (x.raw === 'correct') delete fb.reasons;   // a right answer never lists the traps it dodged (the user's rule)
    // the students' line only once measured (n >= 20): never levels, odds or "rough" (the user's rules)
    const crowd = x.crowd && x.crowd.n >= 20 && x.crowd.rate !== null && x.crowd.rate !== undefined ? { n: x.crowd.n, rate: x.crowd.rate, median_ms_right: x.crowd.median_ms_right } : null;
    const hist = (x.history || []).slice().reverse().map(a => ({ result: a.correct ? 'right' : 'wrong', ms: a.ms, at: a.at }));
    const all = [...hist.filter(a => a.at < R.finished), { result: x.bucket === 'correct' ? 'right' : x.bucket === 'unanswered' ? 'unanswered' : 'wrong', ms: x.ms, current: true }, ...hist.filter(a => a.at >= R.finished)];
    const family = { seen: all.filter(a => a.result !== 'unanswered').length, right: all.filter(a => a.result === 'right').length, recent: all,
      verdict: x.recovered ? 'Recovered' : x.slipping ? 'Slipping' : null };
    const ev = x.cause && !x.held ? [x.ms ? `${tm(x.ms)} on it` : null, x.bucket === 'unanswered' ? 'left blank' : null].filter(Boolean) : [];
    return {
      q, fb: x.held ? { correct: false, given: x.given } : fb, n: x.n, module: x.module, subject: x.subject || 'math', status: x.st, flag: x.flagged, saved: x.saved, reported: x.reported,
      changed: x.changed, ms: x.ms, budget_ms: x.budget_ms, worth: x.miss && x.worth && x.worth.printed ? x.worth.printed : null, crowd,
      cause: x.miss && x.cause ? { cause: x.cause, auto: (R.review[x.i].cause || {}).auto !== false, evidence: ev.length ? ev : null } : null,
      mistake: x.trap ? { status: x.trap.closed || x.recovered ? 'fixed' : 'open', owed: x.trap.owed, of: 2, hits: x.trap.hits, fixed_at: x.trap.closed, label: x.held ? null : x.trap.label } : null,
      tries: (x.tries || []).map(t => ({ ...t, given_label: letter(x, t.given) })), marks: x.held ? [] : x.marks, note: x.note, family,
      seen: x.miss && !x.held ? !!x.looked : undefined, session: SID, blank: x.bucket === 'unanswered', id: x.id,
    };
  }
  function openPlayer(i, o = {}) {
    if (!UI.review) return;
    const list = IT.map(playerItem);
    const f = o.filter === 'misses' ? (it, k) => IT[k].miss : (it, k) => passes(IT[k]);
    const on = {
      seen: it => markSeen([it.q.id]),
      close: () => { player = null; if (dirty) { dirty = false; refresh(); } },
      show: () => {},
      twinAnswer: () => { dirty = true; },
      closed: () => { dirty = true; },
    };
    if (owner) {
      on.why = async (it, body) => {
        const r = await UI.api(`/session/${encodeURIComponent(SID)}/why`, { method: 'POST', body: { question_id: it.q.id, ...body } });
        dirty = true;
        return { called: false, ...r, cause: r.cause && r.cause.cause ? r.cause.cause : r.cause };
      };
      on.rule = async (it, text) => {
        await UI.api('/notes', { method: 'POST', body: { session: SID, question_id: it.q.id, note: text, scope: 'type' } });
        return true;
      };
      // the held-back banner's two buttons: the second look, or the answers now
      if (R.second && R.second.offered && (R.second.unseen || []).length) {
        on.startSecond = () => { if (player) player.close(); setTimeout(startSecond, 200); };   // ponytail: wait out the closing dialog's history.back()
        on.showNow = async it => {
          try { await UI.api(`/session/${encodeURIComponent(SID)}/second/state`, { method: 'POST', body: { state: 'skipped' } }); }
          catch (_) { UI.toast('Not saved. Try again.'); return null; }
          await refresh();
          const x = byId.get(it.id);
          return x ? playerItem(x) : null;
        };
      }
      // Save needs /api/saved to accept finished tests (S10); practice sets work today
      if (!test) on.save = async (it, v) => { await UI.api('/saved', { method: 'POST', body: { session: SID, question_id: it.q.id, on: v } }); dirty = true; };
    }
    const filtered = IT.some((x, k) => !f(null, k));
    player = UI.review(null, list, { mode: 'dialog', at: i, session: SID, owner, title: `${R.label || 'Report'}${R.seq ? ` #${R.seq}` : ''}`, source: 'report',
      sitting: { subjects: 1 }, filter: filtered ? f : null, filterLabel: o.filter === 'misses' ? 'misses' : S.show !== 'all' ? S.show : '', on });
    // "Try one like this" from a list: the player's own twin button, once its action row is built
    if (o.twin && player) {
      let tries = 0;
      const go = () => {
        const t = doc.querySelector('dialog.rv-dlg[open] .ws-actions .split.twin > :first-child');
        if (t) t.click(); else if (tries++ < 20) setTimeout(go, 60);
      };
      setTimeout(go, 60);
    }
  }
  doc.addEventListener('satf:report', e => {
    const d = e.detail || {}, c = d.ctx || {};
    if (c.session === SID && c.question_id && byId.get(c.question_id)) { byId.get(c.question_id).reported = true; dirty = true; }
  });

  /* ------------------------------------------------------------ CSV */
  function csv() {
    const held = IT.filter(x => x.held).length;
    const head0 = ['question', 'module', 'n', 'skill', 'type', 'difficulty', 'format', 'time_s', 'your_answer', 'correct', 'result', 'cause', 'cause_auto', 'worth', 'changed', 'flagged', 'mistake'];
    const q = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const lines = IT.map(x => [labelOf(x), x.module || '', x.n, topicName(x.topic, x.topic_name), x.skill || '', x.difficulty || '', FORMAT[x.type] || x.type, x.ms ? Math.round(x.ms / 1000) : '',
      x.bucket === 'unanswered' ? '' : letter(x, x.given), x.held ? 'Hidden' : x.answer ?? '', (UI.STATES[x.st] || {}).label || x.st, x.miss ? x.cause || '' : '',
      x.miss && R.review[x.i].cause ? String(!!R.review[x.i].cause.auto) : '', x.miss ? rx.worth(x.worth) : '', x.changed ? `${letter(x, x.changed[0])}>${letter(x, x.changed[1])}` : '',
      x.flagged ? 'yes' : '', x.held ? 'Hidden' : x.mistake || ''].map(q).join(','));
    const text = [held ? `# ${held} answers hidden until your second look` : null, head0.join(','), ...lines].filter(Boolean).join('\n');
    const a = h('a', { href: URL.createObjectURL(new Blob([text], { type: 'text/csv' })), download: `sat-freshman-${(R.label || 'report').toLowerCase().replace(/\s+/g, '-')}${R.seq ? `-${R.seq}` : ''}.csv` });
    doc.body.append(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  /* ------------------------------------------------------------ SR20: repair pack, retry sheet, tutor packet */
  const PACK = { repair: 'Print repair pack', retry: 'Print retry sheet', tutor: 'Print tutor packet' };
  function packSheet(kind) {
    const pool = kind === 'retry' ? (SEL.size ? IT.filter(x => SEL.has(x.id)) : IT.filter(passes)).filter(x => x.miss) : misses();
    if (!pool.length) { UI.toast(kind === 'retry' ? 'No misses in this view.' : 'No misses to print.'); return; }
    const each = h('select', { class: 'field', id: 'packeach' }, [1, 2, 3].map(k => h('option', { value: String(k), text: String(k), selected: k === 2 })));
    UI.sheet({ title: PACK[kind], size: 's',
      body: h('div', { class: 'rp-col' }, h('label', { class: 'label', for: 'packeach', text: 'Fresh questions per miss' }), each,
        h('p', { class: 'meta', text: `${plural(pool.length, 'miss', 'misses')}${kind === 'retry' && SEL.size ? ' selected' : ''}` })),
      actions: [{ label: 'Print', primary: true, onClick: api => { api.close(); printPack(kind, pool, Number(each.value)); } }, { label: 'Cancel', quiet: true }] });
  }
  async function printPack(kind, pool, each) {
    const s2 = R.second || {};
    if (kind !== 'retry' && owner && s2.offered && (s2.unseen || []).length) {
      const go = await UI.confirm({ title: 'Print the answers?', text: `This prints the answers and ends your second look for ${plural(s2.unseen.length, 'question')}.`, confirm: 'Print anyway' });
      if (!go) return;
      try { await UI.api(`/session/${encodeURIComponent(SID)}/second/state`, { method: 'POST', body: { state: 'skipped' } }); await refresh(); }
      catch (_) { UI.toast('Couldn’t end the second look. Try again.'); return; }
      pool = pool.map(x => IT.find(y => y.id === x.id) || x);
    }
    let fresh = null;
    try { fresh = await UI.api(`/review/worksheet?session=${encodeURIComponent(SID)}&qids=${pool.map(x => encodeURIComponent(x.id)).join(',')}&each=${each}`, { quiet: true }); } catch (_) { fresh = null; }
    const freshItems = fresh ? (fresh.items || fresh.questions || []) : [];
    if (kind === 'retry' && !freshItems.length) { UI.toast('Couldn’t build the retry sheet. Try again.'); return; }
    let briefing = null;
    if (kind === 'tutor') { try { briefing = await UI.api(`/session/${encodeURIComponent(SID)}/briefing`, { quiet: true }); } catch (_) { briefing = null; } }
    const pack = $('pack') || doc.body.appendChild(h('div', { id: 'pack', class: 'rp-pack', 'aria-hidden': 'true' }));
    pack.replaceChildren();
    const page = (...kids) => pack.appendChild(h('section', { class: 'rp-ppage' }, kids));
    const ws = (host, q, o) => { try { UI.workspace(host, q, { bar: false, toolbar: false, ...o }); } catch (_) { host.append(h('p', { text: q.stem || '' })); } return host; };
    if (briefing && ((briefing.rules || []).length || (briefing.pace || []).length || briefing.changes || briefing.route)) {
      const t = v => (typeof v === 'string' ? v : (v && (v.text || v.note)) || '');
      page(h('h2', { class: 'h2', text: `Briefing from ${R.label || 'this sitting'}` }),
        h('ul', {}, [...(briefing.rules || []), ...(briefing.pace || []), briefing.changes, briefing.route].map(t).filter(Boolean).map(x => h('li', { text: x }))));
    }
    if (kind !== 'retry') {
      page(...['hero', 'ledger', 'value'].map(id => $(id)).filter(e => e && !e.hidden).map(e => { const c = e.cloneNode(true); c.removeAttribute('id'); return c; }));
      if (owner) pool.filter(x => !x.held).forEach(x => {
        const it = playerItem(x);
        page(h('h3', { class: 'h3', text: `${labelOf(x)} · ${topicName(x.topic, x.topic_name)}` }), ws(h('div'), it.q, { mode: 'review', fb: it.fb }));
      });
    }
    if (freshItems.length) {
      page(h('h2', { class: 'h2', text: 'Fresh practice' }), ...freshItems.map((q, k) =>
        h('div', { class: 'rp-pfresh' }, h('h3', { class: 'h3', text: `Fresh ${k + 1}` }), ws(h('div'), q, { mode: 'exam' }), h('div', { class: 'rp-pwork' }))));
      if (fresh.code) pack.append(h('p', { class: 'meta', text: `These answers are not filed. Enter them online: ${location.origin}/s/?c=${fresh.code}` }));
    }
    const keyRows = [...(kind === 'retry' ? [] : pool.filter(x => !x.held && owner).map(x => ({ label: labelOf(x), q: x }))),
      ...freshItems.map((q, k) => ({ label: `Fresh ${k + 1}`, q }))];
    if (keyRows.length) {
      page(h('h2', { class: 'h2', text: 'Key' }), h('table', { class: 'rp-ptable' },
        h('thead', {}, h('tr', {}, ['#', 'Answer', 'What each wrong option means'].map(t => h('th', { text: t })))),
        h('tbody', {}, keyRows.map(({ label, q }) => h('tr', {}, h('td', { text: label }),
          h('td', { text: q.answer === undefined || q.answer === null ? 'Hidden' : String(letter(q, q.answer) ?? q.answer) }),
          h('td', {}, (q.reasons || []).map((r, i) => (r ? h('div', { text: `${'ABCD'[i]}: ${r}` }) : null))))))));
    }
    doc.body.classList.toggle('rp-packonly', kind !== 'tutor');
    doc.body.classList.add('rp-packing');
    const done = () => { doc.body.classList.remove('rp-packing', 'rp-packonly'); window.removeEventListener('afterprint', done); };
    window.addEventListener('afterprint', done);
    window.print();
  }

  /* ------------------------------------------------------------ keys (page scope report) */
  if (UI.keys && UI.keys.register) {
    const jump = k => () => { const s = jumpList()[k]; const t = s && $(s.id); if (t) t.scrollIntoView({ block: 'start' }); };
    const map = {};
    for (let k = 1; k <= 9; k++) map[String(k)] = { does: `Jump to section ${k}`, run: jump(k - 1) };
    map.N = { does: 'Open the first miss', run: () => { const m = misses()[0]; if (m) openPlayer(m.i, { filter: 'misses' }); } };
    map.F = { does: 'Open the Fix menu', run: () => { const b = $('fixmore'); if (b) b.click(); } };
    map.W = { does: 'What if mode', run: () => whatifMode(!WI.on) };
    map.P = { does: 'Print a repair pack', run: () => (misses().length ? packSheet('repair') : false) };
    map.Escape = { does: 'Leave What if or the selection', run: () => { if (WI.on) whatifMode(false); else if (SEL.size) { SEL.clear(); drawCells(); drawSel(); } else return false; } };
    UI.keys.register('report', map, { label: 'Report', when: () => !doc.querySelector('dialog[open]') && !!R });
  }

  load();
})();
