/* ============================================================================
   SAT Freshman -- the start sheet (#start) and one-tap starts, for /tests/
   (spec 3.4 section 3; tests.md X1 presets and conditions, X14 trainers, X16 trap tests)

   TestStart.go(body, btn)    POST /api/mock/new (the diagnostic: POST /api/session) and open
                              the lobby at /test/?s=ID; every setting can still change there
   TestStart.preset(id, btn)  one of the presets row's chips, in one tap
   TestStart.open(o)          the four-step sheet: {kind, step, paper, shared, preset}
   TestStart.use(data, sittings)   the /api/tests payload and the sittings list it reads
   Steps: Test · Modules · Conditions · Tools. Start works from step 2 on; Enter moves on,
   Esc closes. "Save these as my defaults" writes the test_* prefs (R11).
   ========================================================================== */
(() => {
  const h = UI.h;
  const api = (p, o) => UI.api(p, o);
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  // a module's clock is always minutes:seconds ("70:00", never "1:10:00")
  const mmss = s => { const t = Math.max(0, Math.round(s || 0)); return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`; };
  const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + 's'}`;
  let data = null, sittings = [];

  const AIDS = [
    ['pace', 'test_pace', 'Pace guide', 'A tick on the progress strip at the question you should be on, paced to your speed'],
    ['nudges', 'test_nudges', 'Coaching nudges', 'The time sink, the last-minute blanks and the grid-in form'],
    ['confidence', 'test_confidence', 'Confidence tags', 'Your report then shows how often your sure answers were right'],
    ['cover', 'test_cover', 'Cover the choices', 'Work each multiple-choice question out first, then reveal (V)'],
    ['reveal_route', 'test_reveal_route', 'Tell me which module 2 I got', 'Off, as in Bluebook'],
    ['type_notes', 'test_type_notes', 'Your type notes', 'Your note on a kind of question shows under a later one of that kind'],
  ];
  const TIMING = [
    ['official', 'Official', 1], ['x1.5', 'Time and a half', 1.5], ['x2', 'Double time', 2],
    ['untimed', 'Untimed', null], ['x0.85', 'Tight clock (−15%)', 0.85],
  ];
  const KIND = {
    section: { label: 'Full section', facts: '44 questions · 70 min · adaptive', n: 44, mods: 2 },
    modules: { label: 'Choose modules', facts: 'Module 1, a module 2, or both', n: 22, mods: 1 },
    paper: { label: 'A paper', facts: 'The same question types as everyone, your own numbers', n: 44, mods: 2 },
    custom: { label: 'Custom test', facts: '5–60 questions · you choose', n: 22, mods: 1 },
    diagnostic: { label: 'Diagnostic', facts: '20 questions · 32 min · all four domains evenly', n: 20, mods: 1 },
    twin: { label: 'Twin', facts: 'Same slots, new numbers', n: 44, mods: 2 },
    traps: { label: 'Trap test', facts: '6–22 questions · 95 s each', n: 10, mods: 1 },
    trainer: { label: 'Route-up trainer', facts: 'Module 1 · Test-day · 22 questions · 35 min', n: 22, mods: 1 },
    shared: { label: 'Shared test', facts: 'From a link', n: 44, mods: 2 },
  };
  const presetList = () => {
    const p = (data && data.prefs) || {};
    const last = sittings.find(r => r.status === 'completed' && r.kind);
    const x2 = p.test_timing === 'x2';
    return [
      { id: 'like_test_day', label: 'Like test day', tip: 'Full section · Test-day · official timing · adaptive · fullscreen',
        body: { kind: 'section', conditions: 'test_day', timing: 'official', route: 'adaptive', fullscreen: true } },
      last ? { id: 'same', label: 'Same as last time', tip: `${last.kind_label || 'Last sitting'} · ${last.conditions === 'training' ? 'Training' : 'Test-day'} · ${last.timing || 'official'}`,
        body: sameBody(last) } : null,
      { id: 'pacing', label: 'Pacing practice', tip: 'Module 1 · Training · tight clock · pace guide and nudges on',
        body: { kind: 'module', module: 'm1', conditions: 'training', timing: 'x0.85', pace: true, nudges: true } },
      { id: 'routing', label: 'Routing check', tip: 'A Route-up trainer sitting: module 1 · Test-day · 14 of 22 routes you up',
        body: { kind: 'module', module: 'm1', trainer: 'route', conditions: 'test_day', timing: 'official' } },
      { id: 'finisher', label: '700+ finisher', tip: 'The harder module 2 alone · Test-day · the gauntlet',
        body: { kind: 'module', module: 'm2u', trainer: 'gauntlet', conditions: 'test_day', timing: 'official' } },
      { id: 'accom', label: `Accommodations ${x2 ? '2x' : '1.5x'}`, tip: `Full section · Test-day · ${x2 ? 'double time' : 'time and a half'}`,
        body: { kind: 'section', conditions: 'test_day', timing: x2 ? 'x2' : 'x1.5' } },
    ].filter(Boolean);
  };
  function sameBody(r) {
    const b = { conditions: r.conditions || 'test_day', timing: r.timing || 'official' };
    if (r.kind === 'module') return Object.assign(b, { kind: 'module', module: r.module_id || 'm1' });
    if (r.paper) return Object.assign(b, { kind: 'paper', paper: r.paper });
    if (r.kind === 'custom') return Object.assign(b, { kind: 'section' });
    return Object.assign(b, { kind: 'section' });
  }

  /* ---------------- building a sitting */
  async function go(body, btn) {
    const busy = on => { if (!btn) return; if (on) { btn.setAttribute('aria-busy', 'true'); btn.dataset.label = btn.textContent; btn.textContent = 'Building…'; } else { btn.removeAttribute('aria-busy'); if (btn.dataset.label) btn.textContent = btn.dataset.label; } };
    busy(true);
    try {
      const diag = body.kind === 'diagnostic';
      const r = diag ? await api('/session', { method: 'POST', body: body.conditions ? { conditions: body.conditions } : {} })
        : await api('/mock/new', { method: 'POST', body });
      if (r.learner && UI.useLearner) UI.useLearner(r.learner);
      location.href = `/test/?s=${encodeURIComponent(r.id)}`;
      return r;
    } catch (e) {
      busy(false);
      const why = e.status === 429 ? 'You’ve started a lot of tests this hour. Try again in a little while.'
        : e.status === 422 ? `That combination isn’t allowed: ${e.message}` : e.status === 409 ? e.message
        : 'Couldn’t build the test. Check your connection and try again.';
      toast(why);
      throw e;
    }
  }
  const preset = (id, btn) => { const p = presetList().find(x => x.id === id); return p ? go(p.body, btn).catch(() => {}) : null; };

  /* ---------------- the sheet */
  function defaults() {
    const p = (data && data.prefs) || {};
    const aids = {};
    AIDS.forEach(([k, key]) => { aids[k] = p[key] ?? ({ pace: true, nudges: true, type_notes: true })[k] ?? false; });
    return {
      step: 0, kind: 'section', paper: null, m2: 'adaptive', m1: 'standard', mods: new Set(['m1']),
      custom: { source: 'skills', topics: new Set(), count: 22, order: 'ladder', formats: 'both', tiers: new Set(['easy', 'medium', 'hard']), from_session: '' },
      traps: { which: 'all', from_session: '', count: 10, neutral: 0.25 },
      conditions: p.test_conditions || 'test_day', timing: p.test_timing || 'official', minutes: null,
      tools: { fullscreen: p.test_fullscreen !== false, calculator: p.test_calculator !== false, predict: p.test_predict !== false },
      aids, save: true, shared: null, twin: data && data.twin,
    };
  }
  function count(st) {
    if (st.kind === 'modules') return [...st.mods].length * 22;
    if (st.kind === 'custom') return st.custom.source === 'skills' ? st.custom.count : null;
    if (st.kind === 'traps') return st.traps.count;
    if (st.kind === 'shared' && st.shared) return st.shared.questions || 44;
    return KIND[st.kind].n;
  }
  function modulesOf(st) {
    if (st.kind === 'modules') return [...st.mods].length;
    return KIND[st.kind].mods;
  }
  function seconds(st) {
    const f = (TIMING.find(t => t[0] === st.timing) || [])[2];
    if (f === null) return null;
    const n = count(st);
    if (st.kind === 'custom' && st.minutes) return st.minutes * 60;
    const base = ['custom', 'traps', 'diagnostic'].includes(st.kind) ? (n || 22) * 95 : 2100 * modulesOf(st);
    return base * (f || 1);
  }
  function body(st) {
    const tr = st.conditions === 'training';
    const b = { conditions: st.conditions, timing: st.timing === 'x0.85' && !tr ? 'official' : st.timing,
      calculator: st.tools.calculator, fullscreen: st.tools.fullscreen, predict: st.tools.predict };
    if (tr) AIDS.forEach(([k]) => { b[k] = !!st.aids[k]; });
    switch (st.kind) {
      case 'section': return Object.assign(b, { kind: 'section', route: st.m2, m1: st.m1 });
      case 'paper': return Object.assign(b, { kind: 'paper', paper: st.paper, route: st.m2 });
      case 'twin': return Object.assign(b, { kind: 'twin', twin_of: st.twin && st.twin.source });
      case 'shared': return Object.assign(b, { kind: 'shared', shared: st.shared && st.shared.code });
      case 'trainer': return Object.assign(b, { kind: 'module', module: 'm1', trainer: 'route' });
      case 'diagnostic': return { kind: 'diagnostic', conditions: st.conditions };
      case 'modules': {
        const m2 = st.mods.has('m2u') ? 'm2u' : st.mods.has('m2l') ? 'm2l' : null;
        if (st.mods.has('m1') && m2) return Object.assign(b, { kind: 'section', route: m2 === 'm2u' ? 'upper' : 'lower' });
        return Object.assign(b, { kind: 'module', module: st.mods.has('m1') ? 'm1' : m2 || 'm1' });
      }
      case 'custom': {
        const c = st.custom;
        const custom = { source: c.source, order: c.order, formats: c.formats, tiers: [...c.tiers] };
        if (c.source === 'skills') Object.assign(custom, { topics: [...c.topics], count: c.count });
        if (c.source === 'misses' && c.from_session) custom.from_session = c.from_session;
        if (st.minutes && st.timing !== 'untimed') b.minutes = st.minutes;
        return Object.assign(b, { kind: 'custom', custom });
      }
      case 'traps': {
        const t = st.traps;
        const custom = { source: 'traps', traps: t.which === 'session' ? 'all' : t.which, neutral: t.neutral };
        if (t.count) custom.count = t.count;
        if (t.which === 'session' && t.from_session) custom.from_session = t.from_session;
        return Object.assign(b, { kind: 'custom', custom });
      }
      default: return b;
    }
  }
  function blocked(st) {
    if (st.kind === 'modules' && !st.mods.size) return 'Pick at least one module';
    if (st.kind === 'paper' && !st.paper) return 'Pick a paper';
    if (st.kind === 'custom' && st.custom.source === 'skills' && !st.custom.topics.size) return 'Pick at least one skill';
    if (st.kind === 'custom' && st.custom.source === 'misses' && !st.custom.from_session) return 'Pick a sitting';
    if (st.kind === 'custom' && !st.custom.tiers.size) return 'Keep at least one difficulty';
    if (st.kind === 'traps' && st.traps.which === 'session' && !st.traps.from_session) return 'Pick a sitting';
    if (st.kind === 'shared' && !st.shared) return 'This link doesn’t lead to a test';
    if (st.kind === 'twin' && !(st.twin && st.twin.source)) return 'Sit a section first';
    return null;
  }
  function summary(st) {
    const k = st.kind === 'paper' && st.paper ? `Paper #${st.paper}` : st.kind === 'twin' && st.twin ? `Twin of ${st.twin.label}`
      : st.kind === 'shared' && st.shared && st.shared.by ? `Shared by ${st.shared.by}` : KIND[st.kind].label;
    const route = ['section', 'paper'].includes(st.kind) ? { adaptive: 'adaptive', upper: 'always harder', lower: 'always easier' }[st.m2] : null;
    const n = count(st), s = seconds(st);
    const time = s === null ? 'untimed' : `${Math.round(s / 60)} min`;
    return [k, route, n ? plural(n, 'question') : null, time, st.conditions === 'training' ? 'Training' : 'Test-day',
      st.kind !== 'diagnostic' ? (st.tools.calculator ? 'calculator on' : 'no calculator') : null].filter(Boolean).join(' · ');
  }

  function open(o = {}) {
    if (!UI.sheet) return null;
    const st = defaults();
    if (o.kind) st.kind = o.kind;
    if (o.paper) { st.kind = 'paper'; st.paper = +o.paper; }
    if (o.mods) st.mods = new Set(o.mods);
    if (o.shared) st.kind = 'shared';
    if (o.from_session) { st.custom.source = 'misses'; st.custom.from_session = o.from_session; }
    st.step = o.step ?? (o.kind && o.kind !== 'section' ? 1 : 0);
    if (st.kind === 'diagnostic') st.step = 0;
    let pane, stepper, sumEl, back, next, nowB, err;
    const sheet = UI.sheet({ title: 'Start a test', size: 'l', className: 'start-sheet', label: 'Start a test', body: b => {
      stepper = h('ol', { class: 'st-steps', 'aria-label': 'Steps' });
      pane = h('div', { class: 'st-pane' });
      err = h('p', { class: 'error st-err', role: 'alert', hidden: true });
      back = h('button', { type: 'button', class: 'quiet', text: 'Back', onclick: () => { st.step = Math.max(0, st.step - 1); draw(); } });
      sumEl = h('p', { class: 'st-sum mono', 'aria-live': 'polite' });
      next = h('button', { type: 'button', class: 'pill', id: 'startGo', onclick: () => forward() });
      nowB = h('button', { type: 'button', class: 'btn', text: 'Start', hidden: true, onclick: () => start() });
      b.append(stepper, pane, h('div', { class: 'st-foot' }, back, sumEl, h('span', { class: 'st-go' }, nowB, next)), err);
      b.addEventListener('keydown', e => {
        if (e.key !== 'Enter' || e.target.closest('input[type=number], textarea, select, button, a, [role=radio], [role=checkbox]')) return;
        e.preventDefault(); forward();
      });
    } });
    if (o.shared) loadShared(o.shared);

    const steps = () => (st.kind === 'diagnostic' ? ['Test', 'Conditions'] : ['Test', 'Modules', 'Conditions', 'Tools']);
    const lastStep = () => steps().length - 1;
    function forward() {
      if (st.step < lastStep() && !(st.kind === 'diagnostic' && st.step >= 1)) { st.step++; draw(); return; }
      start();
    }
    async function start() {
      const why = blocked(st);
      if (why) { err.textContent = why; err.hidden = false; return; }
      err.hidden = true;
      if (st.save && UI.prefs && UI.prefs.set && st.kind !== 'diagnostic') {
        const p = { test_conditions: st.conditions, test_calculator: st.tools.calculator, test_fullscreen: st.tools.fullscreen, test_predict: st.tools.predict };
        if (st.timing !== 'x0.85' || st.conditions === 'training') p.test_timing = st.timing;
        AIDS.forEach(([k, key]) => { p[key] = !!st.aids[k]; });
        try { await UI.prefs.set(p); } catch (_) {}
      }
      try { await go(body(st), next); }
      catch (_) { err.textContent = 'Couldn’t build the test. Check your connection and try again.'; err.hidden = false; }
    }
    async function loadShared(code) {
      try {
        const r = await api(`/sets/${encodeURIComponent(code)}`, { quiet: true }).catch(() => api(`/shared/${encodeURIComponent(code)}`, { quiet: true }));
        // R18(c)'s public summary: {title, by, created, count, fresh}; no stems
        st.shared = r ? { code, kind_label: r.kind_label || r.title, by: r.by, at: r.at || r.created, questions: r.questions || r.count,
          minutes: r.minutes || (r.count ? Math.round(r.count / 22) * 35 : null), sat_by: r.sat_by, fresh: r.fresh !== false } : null;
      } catch (_) { st.shared = null; }
      draw();
    }

    function draw() {
      const names = steps();
      stepper.replaceChildren(...names.map((n, i) => {
        const li = h('li', { class: 'st-step' + (i <= st.step ? ' on' : ''), 'aria-current': i === st.step ? 'step' : null });
        const lab = i < st.step ? h('button', { type: 'button', class: 'st-step-l', text: n, onclick: () => { st.step = i; draw(); } }) : h('span', { class: 'st-step-l', text: n });
        li.append(h('i', { 'aria-hidden': 'true' }), lab);
        return li;
      }));
      pane.replaceChildren();
      const name = names[st.step];
      if (name === 'Test') stepTest(pane);
      else if (name === 'Modules') stepModules(pane);
      else if (name === 'Conditions') stepConditions(pane);
      else stepTools(pane);
      paintFoot();
    }
    function paintFoot() {
      back.hidden = st.step === 0;
      sumEl.textContent = summary(st);
      const canStart = st.step >= 1 || st.kind === 'diagnostic';
      const atEnd = st.step >= lastStep();
      next.textContent = atEnd || (st.kind === 'diagnostic' && st.step >= 1) ? 'Start' : 'Next';
      const why = canStart ? blocked(st) : null;
      next.disabled = !!(atEnd && why);
      next.title = why || '';
      // Start is available from step 2 on, beside Next
      nowB.hidden = atEnd || !canStart || !!why;
    }

    /* step 1: what do you want to sit? */
    function stepTest(host) {
      host.append(h('h3', { class: 'st-h', text: 'What do you want to sit?' }));
      const pr = h('div', { class: 'st-presets' });
      const rec = data && data.recommended;
      const chips = h('div', { class: 'chips', role: 'group', 'aria-label': 'Presets' });
      presetList().forEach(p => {
        const b = h('button', { type: 'button', class: rec && rec.preset === p.id ? 'pill sm' : 'btn sm', text: p.label, onclick: () => go(p.body, b).catch(() => {}) });
        if (UI.tooltip) UI.tooltip(b, p.tip); else b.title = p.tip;
        chips.append(b);
      });
      pr.append(h('p', { class: 'k', text: 'In one tap' }), chips);
      if (rec && rec.reason) pr.append(h('p', { class: 'help', text: rec.reason }));
      host.append(pr);
      const grid = h('div', { class: 'st-cards', role: 'radiogroup', 'aria-label': 'Test' });
      const list = ['section', 'modules', 'paper', 'custom', 'diagnostic', 'traps', 'trainer'];
      if (st.twin && st.twin.source) list.splice(5, 0, 'twin');
      if (st.kind === 'shared' || o.shared) list.push('shared');
      list.forEach(k => {
        const info = KIND[k];
        const label = k === 'twin' && st.twin ? `Twin of ${st.twin.label}` : k === 'shared' && st.shared ? (st.shared.by ? `Shared by ${st.shared.by}` : st.shared.kind_label || info.label) : info.label;
        const card = h('button', { type: 'button', class: 'st-card', role: 'radio', 'aria-checked': String(st.kind === k), onclick: () => { st.kind = k; if (k === 'paper' && !st.paper) st.paper = firstPaper(); draw(); } },
          h('b', { text: label }), h('span', { class: 'meta', text: info.facts }));
        grid.append(card);
      });
      host.append(grid);
      if (st.kind === 'paper') host.append(paperPick());
    }
    function firstPaper() {
      const ps = (data && data.papers) || [];
      const p = ps.find(x => x.yours && x.yours.status === 'not_sat') || ps[0];
      return p ? p.n : null;
    }
    function paperPick() {
      const ps = (data && data.papers) || [];
      const sel = h('select', { class: 'field sm', 'aria-label': 'Paper' });
      ps.forEach(p => {
        const status = { not_sat: 'not sat', in_progress: 'in progress', completed: 'sat' }[(p.yours || {}).status] || '';
        sel.append(h('option', { value: String(p.n), selected: p.n === st.paper ? true : null, text: `Paper #${p.n} · ${p.newest ? 'this week' : p.label}${status ? ' · ' + status : ''}` }));
      });
      sel.addEventListener('change', () => { st.paper = +sel.value; paintFoot(); });
      return h('label', { class: 'st-field' }, h('span', { class: 'label', text: 'Which paper' }), sel);
    }

    /* step 2: modules (by kind) */
    function trains(text) { return h('p', { class: 'help st-trains', text }); }
    function stepModules(host) {
      const k = st.kind;
      const kinds = Object.fromEntries(((data && data.kinds) || []).map(r => [r.id, r]));
      const last = id => (kinds[id] && kinds[id].last ? ` · last ≈${Math.round(kinds[id].last)}` : '');
      if (k === 'section' || k === 'paper') {
        host.append(h('h3', { class: 'st-h', text: 'Module 2' }));
        UI.seg(host, [{ value: 'adaptive', label: 'Adaptive' }, { value: 'upper', label: 'Always harder' }, { value: 'lower', label: 'Always easier' }],
          { value: st.m2, label: 'Module 2', onChange: v => { st.m2 = v; draw(); } });
        host.append(trains({ adaptive: 'Like the SAT: module 1 decides module 2.', upper: 'Always harder · Trains the 700s: hard questions late in a module.', lower: 'Always easier · Its score tops out at 580.' }[st.m2]));
        if (st.m2 !== 'adaptive') host.append(h('p', { class: 'help', text: 'A fixed module 2 keeps an estimate, scored as if module 1 had routed you there. It is flagged and left out of Combined and percentiles.' }));
        if (k === 'section') {
          host.append(h('h3', { class: 'st-h', text: 'Module 1' }));
          UI.seg(host, [{ value: 'standard', label: 'Standard' }, { value: 'upper', label: 'Harder' }, { value: 'lower', label: 'Easier' }],
            { value: st.m1, label: 'Module 1', onChange: v => { st.m1 = v; draw(); } });
          if (st.m1 !== 'standard') host.append(h('p', { class: 'help', text: 'Harder or easier module 1 is practice, not a score estimate.' }));
        } else {
          host.append(paperPick(), h('p', { class: 'help', text: 'Only the whole paper at official timing counts toward its Sat by and Average.' }));
        }
        return;
      }
      if (k === 'modules') {
        host.append(h('h3', { class: 'st-h', text: 'Choose modules' }));
        const cards = h('div', { class: 'st-mods' });
        [['m1', 'Module 1', '22 questions · 35 min · mixed', `±100 estimate${last('module1')}`, 'Trains the route: 14 of 22 right earns the harder module 2.'],
          ['m2u', 'Module 2 · harder', '22 questions · 35 min', `practice${last('module2u')}`, 'Trains the 700s: hard questions late in a module.'],
          ['m2l', 'Module 2 · easier', '22 questions · 35 min', `practice${last('module2l')}`, 'Tops out at 580, as on the SAT.']].forEach(([id, t, f, y, why]) => {
          const on = st.mods.has(id);
          const b = h('button', { type: 'button', class: 'st-mod', role: 'checkbox', 'aria-checked': String(on), onclick: () => {
            if (on) st.mods.delete(id); else { st.mods.add(id); if (id === 'm2u') st.mods.delete('m2l'); if (id === 'm2l') st.mods.delete('m2u'); }
            draw();
          } }, h('span', { class: 'st-subj mono', text: 'MATH' }), h('b', { text: t }), h('span', { class: 'meta', text: `${f} · ${y}` }), h('span', { class: 'help', text: why }));
          cards.append(b);
        });
        host.append(cards);
        const n = st.mods.size;
        host.append(h('div', { class: 'st-row' },
          h('p', { class: 'meta', text: n ? `${n} of 2 modules · ${n * 22} questions · ${n * 35} min` : 'Pick at least one module' }),
          h('button', { type: 'button', class: 'quiet', text: 'Select all', onclick: () => { st.mods = new Set(['m1', 'm2u']); draw(); } }),
          h('button', { type: 'button', class: 'quiet', text: 'Clear', onclick: () => { st.mods = new Set(); draw(); } })));
        if (st.mods.has('m1') && st.mods.size === 2) host.append(h('p', { class: 'help', text: 'Module 1 plus a module 2 is a section with that fixed route.' }));
        return;
      }
      if (k === 'custom') return stepCustom(host);
      if (k === 'traps') return stepTraps(host);
      if (k === 'twin') {
        const t = st.twin || {};
        host.append(h('p', { class: 'tw-src' }, h('b', { text: t.label || 'Your last test' })), h('p', { class: 'meta', text: 'Same slots, new numbers: every question the same kind, at the same difficulty and position.' }));
        return;
      }
      if (k === 'trainer') {
        host.append(h('p', {}, h('b', { text: 'Route-up trainer' })), h('p', { class: 'meta', text: 'Module 1 · Official timing · Test-day · 22 questions · 35 min' }),
          h('p', { class: 'help', text: 'The line: 14 of 22 right routes you up. The goal is to route up 3 times in a row.' }));
        return;
      }
      if (k === 'shared') {
        const s = st.shared;
        if (!s) { host.append(h('p', { class: 'error', text: 'This link doesn’t lead to a test.' })); return; }
        host.append(h('p', {}, h('b', { text: s.by ? `${s.kind_label || 'A test'} · shared by ${s.by}` : s.kind_label || 'A shared test' })),
          h('p', { class: 'meta', text: [s.at ? UI.date(s.at, 'short') : null, s.questions ? plural(s.questions, 'question') : null, s.minutes ? `${s.minutes} min` : null, s.sat_by ? `Sat by ${s.sat_by}` : null].filter(Boolean).join(' · ') }),
          h('p', { class: 'help', text: s.fresh === false ? `Module 1 is the same as ${s.by ? s.by + '’s' : 'theirs'}. Module 2 matches when you earn the same route.`
            : `Module 1 has the same question types in the same order as ${s.by ? s.by + '’s' : 'theirs'}, with your own numbers. Module 2 matches when you earn the same route.` }));
      }
    }
    function stepCustom(host) {
      const c = st.custom;
      host.append(h('h3', { class: 'st-h', text: 'Questions from' }));
      UI.seg(host, [{ value: 'skills', label: 'Skills' }, { value: 'mistakes', label: 'My open mistakes' }, { value: 'saved', label: 'Saved' }, { value: 'misses', label: 'A sitting’s misses' }],
        { value: c.source, label: 'Questions from', onChange: v => { c.source = v; draw(); } });
      if (c.source === 'mistakes') host.append(h('p', { class: 'help', text: 'One question per open mistake, same kind, new numbers, under test rules: does the fix hold under the clock?' }));
      if (c.source === 'saved') host.append(h('p', { class: 'help', text: 'Your saved questions, exactly as saved.' }));
      if (c.source === 'misses') host.append(sittingPick(c.from_session, v => { c.from_session = v; paintFoot(); }));
      if (c.source === 'skills') {
        const box = h('div', { class: 'st-skills' });
        (UI.DOMAINS || []).forEach(([dom, short]) => {
          const topics = (UI.TOPICS || []).filter(t => t.domain === dom);
          const all = topics.every(t => c.topics.has(t.slug));
          const head = h('button', { type: 'button', class: 'quiet st-dom', 'aria-pressed': String(all), text: short, onclick: () => { topics.forEach(t => (all ? c.topics.delete(t.slug) : c.topics.add(t.slug))); draw(); } });
          const chips = h('div', { class: 'chips' });
          topics.forEach(t => chips.append(h('button', { type: 'button', 'aria-pressed': String(c.topics.has(t.slug)), onclick: () => { c.topics.has(t.slug) ? c.topics.delete(t.slug) : c.topics.add(t.slug); draw(); } },
            UI.glyph ? UI.glyph(t.slug) : null, t.short)));
          box.append(h('div', { class: 'st-domain' }, head, chips));
        });
        host.append(h('div', { class: 'st-row' }, h('button', { type: 'button', class: 'quiet', text: 'All', onclick: () => { (UI.TOPICS || []).forEach(t => c.topics.add(t.slug)); draw(); } }),
          h('button', { type: 'button', class: 'quiet', text: 'Clear', onclick: () => { c.topics.clear(); draw(); } }), h('span', { class: 'meta', text: c.topics.size ? plural(c.topics.size, 'skill') : '' })), box);
        host.append(h('h3', { class: 'st-h', text: 'Length' }));
        const num = h('input', { type: 'number', class: 'field sm st-num', min: 5, max: 60, value: c.count, 'aria-label': 'Number of questions (5–60)' });
        num.addEventListener('change', () => { c.count = Math.max(5, Math.min(60, +num.value || 22)); num.value = c.count; paintFoot(); });
        const lenRow = h('div', { class: 'st-row' });
        UI.seg(lenRow, ['10', '22', '44'].map(n => ({ value: n, label: n })), { value: [10, 22, 44].includes(c.count) ? String(c.count) : null, label: 'Length', onChange: v => { c.count = +v; num.value = c.count; paintFoot(); } });
        lenRow.append(num);
        host.append(lenRow);
      }
      host.append(h('h3', { class: 'st-h', text: 'Order' }));
      UI.seg(host, [{ value: 'ladder', label: 'Easiest first, like a module' }, { value: 'mixed', label: 'Mixed' }], { value: c.order, label: 'Order', onChange: v => { c.order = v; } });
      host.append(h('h3', { class: 'st-h', text: 'Formats' }));
      UI.seg(host, [{ value: 'both', label: 'Both' }, { value: 'mcq', label: 'Multiple choice only' }, { value: 'spr', label: 'Grid-in only' }], { value: c.formats, label: 'Formats', onChange: v => { c.formats = v; } });
      host.append(h('h3', { class: 'st-h', text: 'Difficulty' }));
      const tiers = h('div', { class: 'chips', role: 'group', 'aria-label': 'Difficulty' });
      ['easy', 'medium', 'hard'].forEach(t => tiers.append(h('button', { type: 'button', 'aria-pressed': String(c.tiers.has(t)), text: t[0].toUpperCase() + t.slice(1),
        onclick: () => { if (c.tiers.has(t) && c.tiers.size > 1) c.tiers.delete(t); else c.tiers.add(t); draw(); } })));
      host.append(tiers);
      const n = count(st);
      if (n) host.append(h('p', { class: 'meta', text: `${plural(n, 'question')} · ${mmss(n * 95)} at test pace` }));
    }
    function sittingPick(value, onChange, label = 'Which sitting') {
      const rows = sittings.filter(r => r.status === 'completed' && (r.misses || 0) > 0);
      const sel = h('select', { class: 'field sm', 'aria-label': label }, h('option', { value: '', text: rows.length ? 'Pick a sitting' : 'No finished sitting with misses yet' }));
      rows.slice(0, 40).forEach(r => sel.append(h('option', { value: r.id, selected: r.id === value ? true : null, text: `${r.kind_label}${r.number ? ' #' + r.number : ''} · ${UI.date(r.finished || r.started, 'short')} · ${plural(r.misses, 'miss', 'misses')}` })));
      sel.addEventListener('change', () => onChange(sel.value));
      return h('label', { class: 'st-field' }, h('span', { class: 'label', text: label }), sel);
    }
    function stepTraps(host) {
      const t = st.traps;
      const ready = (((data && data.kinds) || []).find(r => r.id === 'traps') || {}).ready;
      host.append(h('p', { class: 'help', text: 'Every question offers a wrong answer you’ve fallen for before. Do you still take it?' }));
      host.append(h('h3', { class: 'st-h', text: 'Which traps' }));
      UI.seg(host, [{ value: 'all', label: ready ? `All ready ${ready}` : 'All ready' }, { value: 'open', label: 'Open' }, { value: 'due', label: 'Check-ins due' }, { value: 'session', label: 'From a sitting' }],
        { value: t.which, label: 'Which traps', onChange: v => { t.which = v; draw(); } });
      if (t.which === 'session') host.append(sittingPick(t.from_session, v => { t.from_session = v; paintFoot(); }));
      host.append(h('h3', { class: 'st-h', text: 'Length' }));
      UI.seg(host, [{ value: '10', label: '10' }, { value: '22', label: '22' }, { value: '0', label: 'All' }], { value: String(t.count || 0), label: 'Length', onChange: v => { t.count = +v || null; paintFoot(); } });
      host.append(h('h3', { class: 'st-h', text: 'Neutral questions mixed in' }));
      UI.seg(host, [{ value: '0.25', label: '1 in 4' }, { value: '0', label: 'None' }], { value: String(t.neutral), label: 'Neutral questions', onChange: v => { t.neutral = +v; } });
      host.append(h('p', { class: 'help', text: 'Neutral questions come from the same skills with none of your traps on offer, so the test doesn’t give itself away.' }));
    }

    /* step 3: conditions and timing */
    function stepConditions(host) {
      host.append(h('h3', { class: 'st-h', text: 'Conditions' }));
      UI.seg(host, [{ value: 'test_day', label: 'Test-day' }, { value: 'training', label: 'Training' }], { value: st.conditions, label: 'Conditions',
        onChange: v => { st.conditions = v; if (v === 'test_day' && st.timing === 'x0.85') st.timing = 'official'; draw(); } });
      host.append(h('p', { class: 'help', text: st.conditions === 'training' ? 'Pace guide, nudges and the rest. Keeps its score, never ranks.'
        : 'Exactly the SAT: no aids. Ranks among first sittings. A pause keeps your score but drops the rank.' }));
      if (st.kind === 'diagnostic') return;
      host.append(h('h3', { class: 'st-h', text: 'Timing' }));
      const list = h('div', { class: 'st-radios', role: 'radiogroup', 'aria-label': 'Timing' });
      const per = ['custom', 'traps'].includes(st.kind) ? null : 2100;
      TIMING.forEach(([k, label, f]) => {
        const off = k === 'x0.85' && st.conditions !== 'training';
        const clock = f === null ? 'The clock counts up, so you still see your time'
          : per ? `${mmss(per * f)} a module${k === 'x0.85' ? ' · Trains pace' : ''}` : `${Math.round(95 * f)} s a question`;
        const b = h('button', { type: 'button', class: 'st-radio', role: 'radio', 'aria-checked': String(st.timing === k), disabled: off ? true : null,
          onclick: () => { st.timing = k; draw(); } }, h('b', { text: label + (k === 'x0.85' ? ' · Training' : '') }), h('span', { class: 'meta', text: off ? 'Training only' : clock }));
        list.append(b);
      });
      host.append(list);
      if (st.kind === 'custom') {
        const f = h('input', { type: 'number', class: 'field sm st-num', min: 1, max: 180, value: st.minutes || '', placeholder: 'minutes', 'aria-label': 'My own minutes (1–180)' });
        f.addEventListener('change', () => { st.minutes = f.value ? Math.max(1, Math.min(180, +f.value)) : null; paintFoot(); });
        host.append(h('label', { class: 'st-field' }, h('span', { class: 'label', text: 'My own minutes (1–180)' }), f));
      }
    }

    /* step 4: tools */
    function stepTools(host) {
      const t = st.tools;
      const sw = (label, v, set, help, disabled) => {
        UI.switch(host, { label, checked: v, disabled, onChange: x => { set(x); paintFoot(); } });
        if (help) host.append(h('p', { class: 'help st-swh', text: help }));
      };
      if (document.fullscreenEnabled !== false) sw('Fullscreen', t.fullscreen, x => { t.fullscreen = x; }, 'The lobby leads with Enter fullscreen and begin.');
      sw('Calculator', t.calculator, x => { t.calculator = x; }, 'Off gives no-calculator practice, and the tool is hidden.');
      sw('Ask which I missed', t.predict, x => { t.predict = x; }, 'About 20 seconds after each module; your report compares.');
      host.append(h('p', { class: 'k st-aids', text: 'Training aids' }));
      const tr = st.conditions === 'training';
      AIDS.forEach(([k, , label, help]) => sw(label, tr && st.aids[k], x => { st.aids[k] = x; }, tr ? help : 'Training only', !tr));
      const save = h('input', { type: 'checkbox', checked: st.save ? true : null });
      save.addEventListener('change', () => { st.save = save.checked; });
      host.append(h('label', { class: 'check st-save' }, save, 'Save these as my defaults'));
    }

    draw();
    return sheet;
  }

  window.TestStart = { go, preset, open, presets: presetList, use(d, rows) { data = d; sittings = rows || sittings; } };
})();
