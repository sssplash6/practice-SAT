/* ============================================================================
   SAT Freshman -- the plan wizard (S7; spec 3.6 part 2, plan.md L1, L6, L7, L21)

   UI.planWizard(root, ctx) draws four steps -- where you are, where you're going,
   the time you have, what to focus on -- beside the Glance: the live plan (a compact
   month, week 1 and day 1, from POST /api/plan/preview) and its figures.
     ctx  d        GET /api/plan (draft, proposal, active, sittings, rhythm, points)
          step     1..4       edit  a plan id (PATCH)      fresh  start over
          from     'proposal': the one-tap proposal is the draft
          onDone(reply, 'create' | 'save')   onExit()   step2url(step, replace)
   The draft saves as you go (PUT /api/plan/draft, 600 ms, mirrored to localStorage);
   a failed create never loses it. Enter goes on; Mod+Enter creates from any step
   once step 2 is valid (the later steps keep their defaults).
   ========================================================================== */
(() => {
  'use strict';
  const doc = document, h = UI.h;
  const DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const pad = n => String(n).padStart(2, '0');
  const isoOf = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const toD = s => new Date(`${s}T12:00`);
  const addDays = (s, n) => { const d = toD(s); d.setDate(d.getDate() + n); return isoOf(d); };
  const diff = (a, b) => Math.round((toD(b) - toD(a)) / 864e5);
  const dow = s => (toD(s).getDay() + 6) % 7;
  const today = () => isoOf(new Date());
  const D = (s, st) => UI.date(s, st || 'short');
  const tn = s => (UI.TOPIC[s] || {}).short || String(s || '').replace(/_/g, ' ');
  const pl = (n, w, ws) => `${UI.num(n)} ${n === 1 ? w : (ws || w + 's')}`;
  const r10 = v => Math.round(v / 10) * 10;
  const clone = o => JSON.parse(JSON.stringify(o));
  const btn = (label, cls, onClick, attrs = {}) => h('button', { type: 'button', class: cls, onclick: onClick, ...attrs }, label);
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const DOMAINS = ['Algebra', 'Advanced Math', 'Problem-Solving and Data Analysis', 'Geometry and Trigonometry'];
  const DSHORT = { Algebra: 'Algebra', 'Advanced Math': 'Advanced Math', 'Problem-Solving and Data Analysis': 'Problem-Solving & Data', 'Geometry and Trigonometry': 'Geometry & Trig' };
  const WEIGHT = { Algebra: 0.35, 'Advanced Math': 0.35, 'Problem-Solving and Data Analysis': 0.15, 'Geometry and Trigonometry': 0.15 };
  const RW = [['Information and Ideas', 26, 'its own daily R&W task'], ['Craft and Structure', 28, 'its own task; Words adds new words and in-context items'],
    ['Expression of Ideas', 20, 'its own task; Words adds transition items'], ['Standard English Conventions', 26, 'its own task']];
  const MINUTES = [15, 30, 45, 60, 90, 120, 150, 180, 240];
  const STEPS = ['Where you are', 'Where you’re going', 'Time you have', 'What to focus on'];
  const KEY = 'satf.plan.draft';
  const DEFAULTS = { current: 520, measure: false, target: 650, exam_date: null, booked: false, minutes: 45, day_minutes: null, days: '1111100', off: [],
    tests: 'weekly', test_size: 'module', test_day: null, clock: 'auto', time: '18:00', place: null, ramp: null, checkpoints: 'every_2nd',
    focus: {}, skills: {}, extras: { recheck: true, qotd: false, challenge: false }, rw_current: null, rw_target: null, rw_minutes: 0, rw_focus: {}, custom: [] };
  const stateOf = v => (v && typeof v === 'object' ? v.state : v) || 'normal';

  function planWizard(root, ctx) {
    const d = ctx.d || {};
    const editing = ctx.edit && d.active && d.active.id === ctx.edit ? d.active : null;
    const W = { step: Math.min(4, Math.max(1, ctx.step || 1)), f: null, pv: null, week0: null, map: null, err: null, errStep: 0, saving: false, offline: !!ctx.offline, seq: 0, rwSet: false };
    // boot order: the plan being edited; a fresh start; the proposal; the server draft; the local copy; defaults
    const prop = d.proposal && d.proposal.cfg ? d.proposal.cfg : null;
    let seed = null;
    if (editing) seed = editing.cfg;
    else if (ctx.fresh) { UI.api('/plan/draft', { method: 'DELETE' }).catch(() => {}); ls.set(KEY, null); seed = prop; }
    else if (ctx.from === 'proposal') seed = prop;
    else if (d.draft && d.draft.fields) { seed = d.draft.fields; if (!ctx.step && d.draft.step) W.step = d.draft.step; }
    else if (ls.get(KEY, null)) seed = ls.get(KEY).fields;
    else seed = prop;
    W.f = { ...clone(DEFAULTS), ...clone(seed || {}) };
    const f = W.f;
    if (f.sections && f.sections.rw) { f.rw_focus = f.sections.rw.focus || f.rw_focus || {}; }
    delete f.sections;
    if (!f.exam_date) f.exam_date = (UI.SAT_DATES || []).map(x => x.date || x.day).find(x => x > addDays(today(), 27)) || null;
    // no starting score means the plan measures it (a plan can't have neither)
    if (f.current === null || f.current === undefined) f.measure = true;
    W.rwSet = f.rw_current !== null && f.rw_current !== undefined;
    if (editing && !ctx.edit) W.f.name = editing.name;

    const shell = h('div', { class: 'wz' });
    const stepsEl = h('nav', { class: 'wz-steps', 'aria-label': 'Steps' });
    const stepName = h('p', { class: 'wz-stepname' });
    const body = h('div', { class: 'wz-step', 'data-k': 'body' });
    const glance = h('aside', { class: 'wz-glance', 'aria-label': 'Your plan at a glance' });
    const foot = h('div', { class: 'wz-foot' });
    const err = h('p', { class: 'wz-err', role: 'alert' });
    shell.append(
      h('header', { class: 'wz-top' }, h('div', {}, h('h1', { text: editing ? `Edit plan · ${editing.name && !/^Plan for /.test(editing.name) ? editing.name : `${D(editing.cfg.exam_date)} · ${editing.cfg.target}`}` : 'Create your plan' }),
        h('p', { class: 'meta', style: 'margin-top: 6px', text: 'Your draft saves as you go.' })),
      btn('Exit', 'quiet', () => { flush(); ctx.onExit && ctx.onExit(); })),
      stepsEl, stepName, h('div', { class: 'wz-body' }, body, glance), err, foot);
    root.replaceChildren(shell);
    // while GET /api/plan loads, the stepper works and the fields wait (spec 3.6 6)
    if (ctx.loading) { body.inert = true; glance.inert = true; body.setAttribute('aria-busy', 'true'); }
    doc.title = `${editing ? 'Edit plan' : 'Create your plan'} · SAT Freshman`;

    // skill stats for step 4 (the same board the rest of the site reads)
    UI.api('/map').then(m => { W.map = m; if (W.step === 4) draw(); }).catch(() => { W.map = { topics: [] }; });

    /* ---- validity */
    const v2 = () => !!f.exam_date && f.exam_date > today() && diff(today(), f.exam_date) <= 730 && (f.measure || f.current === null || f.target >= f.current);
    const valid = s => s === 2 ? v2() : s === 1 ? (f.measure || (f.current >= 200 && f.current <= 800)) : true;
    const reach = s => [1, 2, 3, 4].slice(0, s - 1).every(valid);

    /* ---- draft and preview */
    let draftT = 0, prevT = 0;
    function body4save() {
      const out = clone(f);
      if (out.measure) out.current = null;
      if (!W.rwSet) { out.rw_current = null; out.rw_target = null; }
      if (out.rw_target !== null && out.rw_current !== null && out.rw_target < out.rw_current) out.rw_target = out.rw_current;
      if (out.target < (out.current || 200)) out.target = out.current;
      if (!out.place) out.place = null;
      if (out.day_minutes && out.day_minutes.every(x => x === null)) out.day_minutes = null;
      const custom = out.custom || [];
      delete out.custom; delete out.name;
      return { ...out, ...(custom.length ? { custom } : {}), ...(editing ? {} : {}) };
    }
    function save() {
      clearTimeout(draftT);
      if (ctx.loading) return;          // nothing to save until the server's draft is known
      ls.set(KEY, { step: W.step, fields: f, at: Date.now() });
      if (editing) return;
      draftT = setTimeout(() => UI.api('/plan/draft', { method: 'PUT', body: { step: W.step, fields: f }, quiet: true })
        .then(() => { W.offline = false; paintFoot(); }).catch(() => { W.offline = true; paintFoot(); }), 600);
    }
    function flush() { if (draftT) { clearTimeout(draftT); if (!editing) UI.api('/plan/draft', { method: 'PUT', body: { step: W.step, fields: f }, quiet: true, keepalive: true }).catch(() => {}); } }
    function preview() {
      clearTimeout(prevT);
      glance.dataset.stale = '';
      prevT = setTimeout(async () => {
        if (!v2()) { delete glance.dataset.stale; paintGlance(); return; }
        const n = ++W.seq;
        try {
          const pv = await UI.api('/plan/preview', { method: 'POST', body: body4save(), quiet: true });
          if (n !== W.seq) return;
          W.week0 = W.pv ? W.pv.week : null;
          W.pv = pv; W.pvErr = null;
        } catch (e) { if (n === W.seq) W.pvErr = e.status === 422 ? e.message : null; }
        // steps 2-4 read the preview (the target note, the totals, the split): draw them again
        // (not while the student is typing in one of its fields)
        const typing = doc.activeElement && body.contains(doc.activeElement) && /^(INPUT|TEXTAREA)$/.test(doc.activeElement.tagName) && doc.activeElement.type !== 'range';
        if (n === W.seq) { delete glance.dataset.stale; if (W.step > 1 && !typing) draw(); else { paintGlance(); paintLive(); } }
      }, 250);
    }
    function changed(redraw = true) { save(); preview(); if (redraw) draw(); else paintGlance(); }

    /* ---- the shell: stepper, footer, keys */
    function paintSteps() {
      stepsEl.replaceChildren(...STEPS.map((name, i) => {
        const s = i + 1;
        const b = h('button', { type: 'button', 'aria-current': s === W.step ? 'step' : null, 'data-done': s < W.step && valid(s) ? '' : null,
          'data-err': W.errStep === s ? '' : null, disabled: !reach(s) || null, 'aria-label': `Step ${s} of 4: ${name}` },
        h('span', { class: 'c', text: s < W.step && valid(s) ? '✓' : String(s) }), h('span', { text: name }));
        b.addEventListener('click', () => goStep(s));
        return b;
      }));
      stepName.textContent = `Step ${W.step} of 4 · ${STEPS[W.step - 1]}`;
    }
    function paintFoot() {
      const last = W.step === 4;
      const back = btn('Back', 'quiet', () => goStep(W.step - 1), { disabled: W.step === 1 || null });
      const next = btn(last ? (editing ? 'Save changes' : 'Create plan') : 'Next', 'pill', () => (last ? submit(next) : nextStep()),
        { 'aria-busy': W.saving || ctx.loading ? 'true' : null, 'aria-keyshortcuts': 'Enter', disabled: (last && W.offline) || ctx.loading || null });
      const kids = [back, h('span', { class: 'meta', text: `${W.step} / 4` })];
      if (W.offline) kids.push(h('span', { class: 'meta', text: 'Can’t save right now' }));
      else if (!last && v2()) kids.push(h('span', { class: 'hint', text: `${UI.keys && UI.keys.label ? UI.keys.label('Mod+Enter') : '⌘↵'} ${editing ? 'save' : 'create'} now` }));
      if (last && editing) kids.push(btn('Save as new plan', 'btn', e => submit(e.currentTarget, true)));
      kids.push(next);
      foot.replaceChildren(...kids);
    }
    function goStep(s) {
      if (s < 1 || s > 4 || !reach(s)) return;
      W.step = s;
      if (ctx.step2url) ctx.step2url(s);
      save();
      draw();
      scrollTo({ top: 0 });
      const hd = body.querySelector('h2');
      if (hd) { hd.tabIndex = -1; hd.focus({ preventScroll: true }); }
    }
    function nextStep() {
      if (!valid(W.step)) { const bad = body.querySelector('[aria-invalid="true"], [data-need]'); showNeed(); if (bad) bad.focus(); return; }
      goStep(W.step + 1);
    }
    function showNeed() { body.querySelectorAll('[data-need]').forEach(x => { x.hidden = false; }); }
    async function submit(b, asNew) {
      if (!v2()) { goStep(2); showNeed(); return; }
      W.saving = true; err.textContent = ''; W.errStep = 0;
      b.setAttribute('aria-busy', 'true');
      try {
        const payload = body4save();
        const reply = editing && !asNew
          ? await UI.api(`/plan/${encodeURIComponent(editing.id)}`, { method: 'PATCH', body: payload })
          : await UI.api('/plan', { method: 'POST', body: { ...payload, ...(editing && asNew ? { from: editing.id } : {}) } });
        ls.set(KEY, null);
        unkeys();
        ctx.onDone && ctx.onDone(reply, editing && !asNew ? 'save' : 'create');
      } catch (e) {
        W.saving = false;
        b.removeAttribute('aria-busy');
        if (e.status === 422) {
          const m = String(e.message || '');
          W.errStep = /^(current|rw_current)/.test(m) ? 1 : /^(target|rw_target|exam_date)/.test(m) ? 2 : /^(focus|skills|rw|custom|name)/.test(m) ? 4 : 3;
          err.textContent = m.replace(/^\w+: /, '');
        } else err.textContent = 'Couldn’t save the plan. Your draft is kept.';
        paintSteps();
      }
    }
    const reg = UI.keys.register('plan-wizard', {
      Enter: { does: 'Next step', run: e => { if (e.target.closest && e.target.closest('button, a, input, select, textarea')) return false; nextStep(); } },
      'Mod+Enter': { does: 'Create the plan now', run: () => { const b = foot.querySelector('.pill'); if (v2()) submit(b || h('button')); else { goStep(Math.min(2, W.step)); showNeed(); } } },
    }, { label: 'Plan builder', when: () => shell.isConnected && !ctx.loading });
    const unkeys = () => reg.unregister();
    addEventListener('pagehide', flush);

    /* ---- the Glance and the live plan (2a, L6) */
    const live = h('div', { class: 'wz-live' });
    const rowsEl = h('dl', { class: 'wz-grows' });
    glance.append(h('p', { class: 'k', text: 'Live plan' }), live, rowsEl);
    function paintLive() {
      const pv = W.pv;
      if (!pv) { live.replaceChildren(h('p', { class: 'meta', text: v2() ? 'Working it out…' : 'Pick a date to see the plan.' })); return; }
      const cal = h('div');
      UI.calendar(cal, { look: 'plan', compact: true, legend: false, plan: (pv.calendar || []).map(x => ({ day: x.date, kind: x.kind, minutes: x.minutes, phase: x.phase })),
        marks: { start: today(), end: f.exam_date, exam: f.exam_date, today: today() }, min: today(), max: f.exam_date });
      const old = new Map((W.week0 || []).map(x => [x.date, `${x.kind}${x.minutes}${(x.topics || []).join()}`]));
      const wk = h('div', { class: 'wz-wk', role: 'img', 'aria-label': `Week 1: ${(pv.week || []).map(x => `${DOW[dow(x.date)]} ${x.minutes ? x.minutes + ' min' : x.kind}`).join(', ')}` },
        (pv.week || []).map(x => {
          const key = `${x.kind}${x.minutes}${(x.topics || []).join()}`;
          return h('span', { 'data-ch': W.week0 && old.get(x.date) !== key && !UI.reduced() ? '' : null }, DOW[dow(x.date)],
            h('b', { text: x.minutes ? UI.dur(x.minutes) : '—' }), x.kind === 'test' ? 'test' : '');
        }));
      const day1 = h('div', { class: 'trows' });
      ((pv.sample_day && pv.sample_day.tasks) || []).slice(0, 5).forEach(t => UI.taskRow(day1, t, { readonly: true, compact: true }));
      live.replaceChildren(cal, h('p', { class: 'k', text: 'Week 1' }), wk,
        pv.sample_day && pv.sample_day.date ? h('p', { class: 'k', text: `Day 1 · ${D(pv.sample_day.date, 'long')}` }) : '', day1);
      if (W.week0) setTimeout(() => live.querySelectorAll('[data-ch]').forEach(x => x.removeAttribute('data-ch')), 600);
    }
    function paintGlance() {
      const pv = W.pv, rows = [];
      const row = (k, v) => rows.push(h('div', {}, h('dt', { text: k }), h('dd', {}, v)));
      const cur = f.measure ? '?' : f.current;
      row('Score', `${cur} → ${f.target}${f.measure ? ' · measured on day 1' : ` · +${f.target - f.current}`}`);
      if (W.rwSet && f.rw_target) row('Total', `${(f.measure ? 0 : f.current) + f.rw_current} → ${f.target + f.rw_target}`);
      if (f.exam_date) row('Exam', `${D(f.exam_date, 'long')} · ${pl(diff(today(), f.exam_date), 'day')}${f.booked ? '' : ' · not booked'}`);
      if (pv) {
        if (!f.measure) row('Pace', `${UI.num(pv.pace_per_week)} points a week · ${pv.pace_tag}`);
        const week = weekMinutes();
        row('Study', `${f.days.split('').filter(x => x === '1').length} days · ${UI.dur(week)} a week`);
        row('To exam', `${pl(pv.study_days, 'study day')} · ${UI.num(pv.hours)} h · about ${UI.num(pv.questions)} questions`);
        if (pv.tests && pv.tests.count) row('Tests', `${pl(pv.tests.count, pv.tests.size)}${f.test_day !== null && f.test_day !== undefined ? ` · ${DOW[f.test_day]}s` : ''}`);
        const ph = phaseLine(pv);
        if (ph) row('Phases', ph);
      }
      const foc = [...Object.entries(f.focus).filter(([, v]) => stateOf(v) === 'focus').map(([k]) => DSHORT[k] || k),
        ...Object.entries(f.skills).filter(([, v]) => stateOf(v) === 'focus').map(([k]) => tn(k))];
      if (foc.length) row('Focus', foc.join(', '));
      const str = [...Object.entries(f.focus).filter(([, v]) => stateOf(v) === 'strong').map(([k]) => DSHORT[k] || k),
        ...Object.entries(f.skills).filter(([, v]) => stateOf(v) === 'strong').map(([k]) => tn(k))];
      if (str.length) row('Strong', str.join(', '));
      if (f.rw_minutes) row('R&W', `${f.rw_minutes} min × ${f.days.split('').filter(x => x === '1').length} a week`);
      if ((f.custom || []).length) row('Your own', f.custom.map(t => t.title).join(', '));
      const ex = [f.extras.recheck && 'Warm-up', f.extras.qotd && 'Question of the day', f.extras.challenge && 'Daily challenge'].filter(Boolean);
      if (ex.length) row('Extras', ex.join(' · '));
      if (W.pvErr) rows.push(h('p', { class: 'wz-err', text: W.pvErr.replace(/^\w+: /, '') }));
      rowsEl.replaceChildren(...rows);
      if (W.step === 1) paintLive();
    }
    function phaseLine(pv) {
      const ph = pv.phases || [], cal = pv.calendar || [];
      if (!ph.length) return null;
      const out = [];
      for (let i = 0; i < ph.length; i++) if (ph[i] !== ph[i + 1] && i < ph.length - 1) out.push(`${ph[i]} to ${D(cal[i] ? cal[i].date : today())}`);
      out.push(ph[ph.length - 1]);
      return out.join(' · ');
    }
    const dayMin = i => f.days[i] === '1' ? (f.day_minutes && f.day_minutes[i] !== null && f.day_minutes[i] !== undefined ? f.day_minutes[i] : f.minutes) : 0;
    const weekMinutes = () => [0, 1, 2, 3, 4, 5, 6].reduce((s, i) => s + dayMin(i), 0);

    /* ---- steps */
    function field(label, ...kids) { return h('div', { class: 'wz-field' }, label ? h('p', { class: 'label', text: label }) : null, ...kids); }
    function draw() {
      // keep the keyboard where it was across a redraw
      const a = doc.activeElement, zone = a && a.closest && a.closest('[data-k]');
      const key = zone && zone !== body ? zone.dataset.k : null;
      const idx = key ? [...zone.querySelectorAll('button, input, select, a')].indexOf(a) : -1;
      body.replaceChildren(...[null, step1, step2, step3, step4][W.step]());
      paintSteps(); paintFoot(); paintGlance();
      if (W.step !== 1) paintLive();
      if (key) {
        const z = body.querySelector(`[data-k="${CSS.escape(key)}"]`);
        const el = z && [...z.querySelectorAll('button, input, select, a')][idx];
        if (el) el.focus({ preventScroll: true });
      }
    }

    function sittings() { return (d.sittings || []).filter(s => s.kind !== 'outside').slice(-3); }
    function step1() {
      const out = [h('header', {}, h('h2', { class: 'h2', text: 'Where you are' }), h('p', { text: 'Start from your real number, so the plan is built for the gap you have.' }))];
      const sits = sittings();
      const recent = sits.filter(s => diff(String(s.at).slice(0, 10), today()) <= 45);
      const mid = s => r10((s.low + s.high) / 2);
      if (recent.length >= 2) {
        const mean = r10(recent.reduce((a, s) => a + mid(s), 0) / recent.length);
        out.push(h('div', { class: 'wz-note' }, h('p', { text: `Your last ${recent.length} tests average ${mean} · ${recent.map(s => D(String(s.at).slice(0, 10))).join(', ')}` }),
          btn(`Use ${mean}`, 'btn sm', () => { f.current = mean; f.measure = false; changed(); })));
      } else if (recent.length === 1) {
        const s = recent[0];
        out.push(h('div', { class: 'wz-note' }, h('p', { text: `Latest · ${UI.KIND && UI.KIND.label ? UI.KIND.label(s) : s.kind} · ${D(String(s.at).slice(0, 10))} · ${s.low}–${s.high}` }),
          btn(`Use ${mid(s)}`, 'btn sm', () => { f.current = mid(s); f.measure = false; changed(); })));
      } else if (prop && prop.current && !editing) {
        out.push(h('div', { class: 'wz-note' }, h('p', { text: `From your results: about ${prop.current}` }), btn(`Use ${prop.current}`, 'btn sm', () => { f.current = prop.current; f.measure = false; changed(); })));
      }
      const newStudent = !sits.length && !(prop && prop.current) && !editing;
      if (newStudent || f.measure) {
        const choice = h('div', { class: 'wz-choice', role: 'radiogroup', 'aria-label': 'Your starting score', 'data-k': 'measure' },
          [[true, 'Let the plan measure it', 'Day 1 starts with a 20-question diagnostic (about 30 min); Map days follow.'],
            [false, 'I’ll estimate', 'Set it on the slider.']].map(([on, t, s]) => {
            const b = h('button', { type: 'button', role: 'radio', 'aria-checked': String(!!f.measure === on) }, h('b', { text: t }), h('span', { text: s }));
            b.addEventListener('click', () => { f.measure = on; if (!on && !f.current) f.current = 520; changed(); });
            return b;
          }));
        out.push(choice);
      }
      if (!f.measure) {
        const sl = h('div', { 'data-k': 'math' });
        UI.scoreSlider(sl, { min: 200, max: 800, step: 10, value: f.current || 520, label: 'Math', onChange: v => { f.current = v; if (f.target < v) f.target = v; changed(); } });
        out.push(field('Math', sl, rangeBar(sits)));
      }
      // Reading & Writing, beside Math (L21)
      const rw = h('div', { 'data-k': 'rw' });
      if (W.rwSet) {
        UI.scoreSlider(rw, { min: 200, max: 800, step: 10, value: f.rw_current || 500, label: 'Reading and Writing', onChange: v => { f.rw_current = v; if (f.rw_target !== null && f.rw_target < v) f.rw_target = v; changed(); } });
        rw.append(h('div', { class: 'row' }, h('span', { class: 'meta', text: `Total ${(f.measure ? 0 : f.current) + f.rw_current}` }),
          btn('Clear', 'quiet', () => { W.rwSet = false; f.rw_current = null; f.rw_target = null; changed(); })));
      } else rw.append(h('div', { class: 'wz-note' }, h('p', { text: 'Not set · your Total needs it' }),
        btn('Add my R&W score', 'btn sm', () => { W.rwSet = true; f.rw_current = 500; if (!f.rw_target) f.rw_target = 500; changed(); })));
      out.push(field('Reading & Writing', rw));
      out.push(h('p', { class: 'help', text: 'You can update this after any test; the plan will offer it.' }));
      return out;
    }
    function rangeBar(sits) {
      const x = v => `${(Math.max(200, Math.min(800, v)) - 200) / 6}%`;
      const box = h('div', { class: 'wz-range' });
      const mean = sits.length ? sits.reduce((a, s) => a + (s.low + s.high) / 2, 0) / sits.length : null;
      const NS = 'http://www.w3.org/2000/svg';
      const svg = doc.createElementNS(NS, 'svg');
      svg.setAttribute('role', 'img');
      svg.setAttribute('aria-label', `200 to 800${sits.length ? `; your last ${sits.length} tests, averaging ${r10(mean)}` : ''}; you: ${f.current}`);
      const add = (tag, at) => { const e = doc.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); svg.append(e); return e; };
      add('rect', { x: '0', y: '18', width: '100%', height: '4', rx: '2', fill: 'var(--mat)' });
      // a band's width is calc(), which an SVG attribute doesn't take: it goes on the style
      sits.forEach(s => { add('rect', { x: x(s.low), y: '13', height: '14', rx: '3', fill: 'var(--faint)', opacity: '.55', class: 'band' }).style.width = `calc(${x(s.high)} - ${x(s.low)})`; });
      if (sits.length) add('rect', { x: x(mean), y: '9', width: '2', height: '22', fill: 'var(--ink)', class: 'mean' });
      add('circle', { cx: x(f.current || 520), cy: '20', r: '6', fill: 'var(--ink)' });
      [[200, '200'], [505, 'avg 505'], [800, '800']].forEach(([v, t]) => { const e = add('text', { x: x(v), y: '40', 'text-anchor': v === 200 ? 'start' : v === 800 ? 'end' : 'middle', 'font-size': '10.5', fill: 'var(--soft)', 'font-family': 'var(--mono)' }); e.textContent = t; });
      box.append(svg);
      return box;
    }

    function perDate(date) {
      const start = addDays(today(), 1), exam = date;
      let study = 0;
      for (let dd = start; dd < addDays(exam, -1); dd = addDays(dd, 1)) {
        if (f.days[dow(dd)] !== '1') continue;
        if ((f.off || []).some(([a, b]) => dd >= a && dd <= b)) continue;
        study++;
      }
      const weeks = Math.max(1, Math.ceil(diff(today(), exam) / 7));
      const per = f.measure ? null : Math.round((Math.min(f.target, 780) - f.current) / weeks);
      const tag = per === null ? null : per <= 15 ? 'Steady' : per <= 30 ? 'Ambitious' : 'Very ambitious';
      return { study, per, tag };
    }
    function step2() {
      const out = [h('header', {}, h('h2', { class: 'h2', text: 'Where you’re going' }), h('p', { text: 'Your target and date set the pace for every week.' }))];
      const low = f.measure ? 200 : f.current;
      const sl = h('div', { 'data-k': 'target' });
      UI.scoreSlider(sl, { min: low, max: 800, step: 10, value: Math.max(low, f.target), label: 'Math target', onChange: v => { f.target = v; changed(); } });
      const quick = h('div', { 'data-k': 'quick' });
      const opts = [50, 100, 150, 200].map(n => ({ value: `+${n}`, label: `+${n}`, disabled: f.measure || f.current + n > 800 })).concat([700, 750, 800].map(v => ({ value: String(v), label: String(v), disabled: v < low })));
      UI.chips(quick, opts, { label: 'Quick targets', value: null, onChange: v => { f.target = Math.min(800, v[0] === '+' ? f.current + +v.slice(1) : +v); changed(); } });
      out.push(field('Math target', sl, quick));
      if (!f.measure) {
        const x = v => `${(v - 200) / 6}%`;
        out.push(h('div', { class: 'wz-gain' },
          h('div', { class: 'row' }, h('span', { class: 'k', text: 'Now' }), h('span', { class: 'big', text: String(f.current) }), h('span', { class: 'tag or', text: `+${f.target - f.current}` }),
            h('span', { class: 'k', text: 'Target' }), h('span', { class: 'big t', text: String(f.target) })),
          h('div', { class: 'pl-track', 'aria-hidden': 'true' }, h('b', { class: 'gap', style: `left: ${x(f.current)}; width: calc(${x(f.target)} - ${x(f.current)})` }), h('i', { style: `left: ${x(f.current)}` }), h('i', { class: 't', style: `left: ${x(f.target)}` })),
          W.rwSet && f.rw_target ? h('p', { class: 'meta', text: `R&W ${f.rw_current} → ${f.rw_target} (+${f.rw_target - f.rw_current}) · Total ${f.current + f.rw_current} → ${f.target + f.rw_target} (+${f.target + f.rw_target - f.current - f.rw_current})` }) : null,
          h('p', { class: 'sr', 'aria-live': 'polite', text: `From ${f.current} to ${f.target}, ${f.target - f.current} points.` })));
      }
      const tnote = W.pv && W.pv.target_note;
      const pts = W.pv && W.pv.points && W.pv.points.math;
      const notes = [];
      if (tnote) notes.push(`${f.target} is about ${tnote.points_pct}% of the section’s points${pts && pts.skills ? ` · the points you’re most likely missing are in ${pts.skills.slice().sort((a, b) => b.gain - a.gain).slice(0, 3).map(s => tn(s.topic)).join(', ')}` : ''}.`);
      if (f.target > 580) notes.push(pts && pts.route && pts.route.m1 !== null && pts.route.m1 !== undefined ? `Your first modules: about ${Math.round(pts.route.m1 * 100)}% · 14 of 22 routes up.` : 'Above 580 needs the harder second module: 14 of 22 right in module 1 routes you up.');
      if (f.target > 780) notes.push('A perfect section reads 710–800 here; the plan counts 780 as reaching your target.');
      if (notes.length) out.push(h('div', { class: 'help' }, notes.map(t => h('p', { text: t }))));
      // R&W target (L21)
      const rw = h('div', { 'data-k': 'rwt' });
      if (W.rwSet) UI.scoreSlider(rw, { min: f.rw_current, max: 800, step: 10, value: Math.max(f.rw_current, f.rw_target || f.rw_current), label: 'R&W target', onChange: v => { f.rw_target = v; changed(); } });
      else rw.append(h('p', { class: 'help', text: 'Set your R&W score first (step 1).' }), h('input', { type: 'range', disabled: true, 'aria-label': 'R&W target, set your R&W score first' }));
      out.push(field('R&W target', rw));
      // dates (T12's rows)
      const dates = (UI.SAT_DATES || []).map(x => ({ ...x, date: x.date || x.day })).filter(x => x.date > today());
      const rec = dates.find(x => perDate(x.date).tag === 'Steady');
      const list = h('div', { class: 'wz-dates', role: 'radiogroup', 'aria-label': 'SAT date', 'data-k': 'dates' });
      for (const x of dates) {
        const p = perDate(x.date);
        const meta = [`in ${pl(diff(today(), x.date), 'day')}`, pl(p.study, 'study day'), p.per !== null ? `+${p.per} a week` : null, p.tag,
          x.register_by && x.register_by >= today() ? `register by ${D(x.register_by)}` : x.late_by && x.late_by >= today() ? `late registration by ${D(x.late_by)}` : null].filter(Boolean).join(' · ');
        const b = h('button', { type: 'button', role: 'radio', class: 'wz-date', 'aria-checked': String(f.exam_date === x.date) },
          h('b', { text: `${D(x.date)} · ${DOW[dow(x.date)]}` }), h('span', { class: 'meta', text: meta }), x === rec ? h('span', { class: 'badge', text: 'Recommended' }) : null);
        b.addEventListener('click', () => { f.exam_date = x.date; changed(); });
        list.append(b);
      }
      const other = h('input', { type: 'date', class: 'field sm', min: addDays(today(), 1), max: addDays(today(), 730), value: dates.some(x => x.date === f.exam_date) ? '' : f.exam_date || '', 'aria-label': 'Another date' });
      other.addEventListener('change', () => { if (other.value) { f.exam_date = other.value; changed(); } });
      const need = h('p', { class: 'field-err', 'data-need': '', hidden: true, text: !f.exam_date ? 'Pick a date' : 'Pick a date after today' });
      if (v2()) need.removeAttribute('data-need');
      const booked = h('input', { type: 'checkbox', checked: f.booked || null });
      booked.addEventListener('change', () => { f.booked = booked.checked; changed(false); });
      out.push(field('SAT date', list, h('div', { class: 'row', 'data-k': 'other' }, h('span', { class: 'meta', text: 'Other date' }), other), need,
        h('label', { class: 'check' }, booked, 'I’ve registered for this date')));
      if (f.exam_date && !f.measure) {
        const p = perDate(f.exam_date);
        const line = h('p', { class: 'line-t' }, `${pl(diff(today(), f.exam_date), 'day')} · ${pl(p.study, 'study day')} · about ${p.per} points a week `, h('span', { class: p.tag === 'Steady' ? 'tag' : 'tag or', text: p.tag }));
        out.push(line);
        if (p.tag === 'Very ambitious') {
          const later = dates.find(x => x.date > f.exam_date && perDate(x.date).per <= 30);
          if (later) out.push(h('p', { class: 'help' }, `${D(later.date)} brings it to ${perDate(later.date).per} a week. `, btn(`Use ${D(later.date)}`, 'quiet', () => { f.exam_date = later.date; changed(); })));
        }
      }
      return out;
    }

    function step3() {
      const out = [h('header', {}, h('h2', { class: 'h2', text: 'Time you have' }), h('p', { text: 'A plan you keep beats one you drop.' }))];
      const rh = d.rhythm;
      const mc = h('div', { 'data-k': 'minutes' });
      UI.chips(mc, MINUTES.map(v => ({ value: v, label: UI.dur(v) })), { value: f.minutes, label: 'A study day', onChange: v => { f.minutes = v; if (f.ramp && f.ramp.from > v) f.ramp = null; changed(); } });
      const kids = [mc];
      if (rh && rh.active_days >= 7) {
        const pattern = rh.by_dow.map(x => (x.studied >= 2 ? '1' : '0')).join('');
        const snap = Math.max(15, ...MINUTES.filter(v => v <= (rh.median_min || 45)));
        kids.unshift(h('div', { class: 'wz-note' }, h('p', { text: `Last 4 weeks: ${UI.num(rh.days_per_week)} days a week · median ${rh.median_min} min · ${UI.dur(rh.weekly_min)} a week` }),
          btn('Use that', 'btn sm', () => { if (pattern.includes('1')) f.days = pattern; f.minutes = snap; changed(); })));
      }
      out.push(field('A study day', ...kids));
      // weekdays with their own minutes
      const tiles = h('div', { class: 'wz-tiles', 'data-k': 'days' });
      const warn = h('p', { class: 'field-err', hidden: true, text: 'Keep at least one study day' });
      DOW.forEach((name, i) => {
        const on = f.days[i] === '1';
        const tile = h('div', { class: 'wz-wd', 'data-on': on ? '' : null });
        const tb = h('button', { type: 'button', 'aria-pressed': String(on), 'aria-label': `${name}: ${on ? 'study' : 'rest'}` }, h('b', { text: name }), h('span', { text: on ? 'STUDY' : 'REST' }));
        tb.addEventListener('click', () => {
          if (on && f.days.split('').filter(x => x === '1').length === 1) { warn.hidden = false; if (!UI.reduced()) { tile.classList.remove('shake'); void tile.offsetWidth; tile.classList.add('shake'); } return; }
          f.days = f.days.split('').map((x, j) => (j === i ? (on ? '0' : '1') : x)).join('');
          changed();
        });
        tile.append(tb);
        if (on) {
          const own = f.day_minutes && f.day_minutes[i] !== null && f.day_minutes[i] !== undefined ? f.day_minutes[i] : null;
          const sel = h('select', { 'aria-label': `${name} minutes`, class: own !== null ? 'diff' : null },
            h('option', { value: '', text: `${UI.dur(f.minutes)}` }), MINUTES.filter(v => v !== f.minutes).map(v => h('option', { value: String(v), selected: own === v || null, text: UI.dur(v) })));
          sel.addEventListener('change', () => { const dm = f.day_minutes ? f.day_minutes.slice() : [null, null, null, null, null, null, null]; dm[i] = sel.value ? +sel.value : null; f.day_minutes = dm; changed(); });
          tile.append(sel);
        }
        const r = rh && rh.by_dow && rh.by_dow[i];
        if (r && r.studied) tile.append(h('span', { class: 'meta', text: `studied ${r.studied} of ${r.of}${r.median_min ? ` · ~${r.median_min}m` : ''}` }));
        tiles.append(tile);
      });
      const n = f.days.split('').filter(x => x === '1').length;
      const week = weekMinutes();
      out.push(field('Days a week', tiles, warn, h('p', { class: 'meta', text: `${pl(n, 'day')} · ${UI.dur(week)} a week · Rest ${7 - n}` })));
      // too much at once: ramp up (L7)
      if (rh && rh.active_days >= 7 && rh.weekly_min && week > 1.5 * rh.weekly_min && !f.ramp) {
        const from = Math.max(15, Math.min(f.minutes - 5, Math.round(rh.weekly_min / Math.max(1, n) / 5) * 5));
        out.push(h('div', { class: 'wz-note' }, h('p', { text: `You’ve averaged ${UI.dur(rh.weekly_min)} a week; this asks ${UI.dur(week)}.` }),
          btn('Ramp up to it', 'btn sm', () => { f.ramp = { from }; changed(); })));
      }
      if (f.ramp) {
        const weeks = Math.ceil((f.minutes - f.ramp.from) / 5) + 1;
        out.push(h('div', { class: 'wz-note' }, h('p', { text: `Ramp: ${f.ramp.from} → ${f.minutes} min by week ${weeks}` }), btn('Remove', 'quiet', () => { f.ramp = null; changed(); })));
      }
      // days off
      const off = h('div', { class: 'wz-off', 'data-k': 'off' });
      (f.off || []).forEach(([a, b], i) => off.append(h('div', {}, h('span', { class: 'line-t', text: `${D(a)}${a !== b ? ` – ${D(b)}` : ''} · ${pl(diff(a, b) + 1, 'day')}` }),
        btn('×', 'quiet', () => { f.off.splice(i, 1); changed(); }, { 'aria-label': `Remove days off from ${D(a)}` }))));
      const from = h('input', { type: 'date', class: 'field sm', min: today(), max: f.exam_date || '', 'aria-label': 'Days off from' });
      const to = h('input', { type: 'date', class: 'field sm', min: today(), max: f.exam_date || '', 'aria-label': 'Days off to' });
      const offErr = h('p', { class: 'field-err', hidden: true });
      const add = btn('Add days off', 'btn sm', () => {
        const a = from.value, b = to.value || from.value;
        if (!a || b < a || a < today() || (f.exam_date && b > f.exam_date)) { offErr.textContent = 'Pick a start and an end between today and the exam.'; offErr.hidden = false; return; }
        if ((f.off || []).length >= 20) { offErr.textContent = 'At most 20 ranges.'; offErr.hidden = false; return; }
        f.off = [...(f.off || []), [a, b]]; changed();
      });
      off.append(h('div', { class: 'row' }, from, h('span', { class: 'meta', text: 'to' }), to, add), offErr);
      out.push(field('Days off', off));
      // tests
      const tr = h('div', { 'data-k': 'tests' });
      UI.seg(tr, [['none', 'None'], ['weekly', 'Weekly'], ['twice', 'Twice a week'], ['daily', 'Every study day']].map(([value, label]) => ({ value, label })),
        { value: f.tests, label: 'Practice tests', onChange: v => { f.tests = v; changed(); } });
      const kidsT = [tr];
      if (f.tests !== 'none') {
        const size = h('div', { 'data-k': 'size' });
        const maxDay = Math.max(...[0, 1, 2, 3, 4, 5, 6].map(dayMin));
        UI.seg(size, [{ value: 'module', label: 'Module · 22 q · 35 min', disabled: maxDay < 35, why: 'A module needs 35 minutes' },
          { value: 'section', label: 'Section · 44 q · 70 min', disabled: maxDay < 70, why: 'Needs a 70-minute day' }], { value: f.test_size, label: 'Test size', onChange: v => { f.test_size = v; changed(); } });
        kidsT.push(size);
        if (f.tests === 'weekly' || f.tests === 'twice') {
          const sel = h('select', { class: 'field sm', 'aria-label': 'Test day', 'data-k': 'tday' }, h('option', { value: '', text: 'Auto (last study day)' }),
            DOW.map((nm, i) => (f.days[i] === '1' ? h('option', { value: String(i), selected: f.test_day === i || null, text: nm }) : null)));
          sel.addEventListener('change', () => { f.test_day = sel.value === '' ? null : +sel.value; changed(); });
          kidsT.push(h('div', { class: 'row' }, h('span', { class: 'meta', text: 'Test day' }), sel));
        }
        const cp = h('div', { 'data-k': 'cp' });
        UI.seg(cp, [['every', 'Every test'], ['every_2nd', 'Every 2nd test'], ['off', 'Off']].map(([value, label]) => ({ value, label })),
          { value: f.checkpoints, label: 'Checkpoints', onChange: v => { f.checkpoints = v; changed(false); } });
        const tip = h('button', { type: 'button', class: 'quiet', text: 'What’s a checkpoint?' });
        UI.tooltip && UI.tooltip(tip, 'A twin of one of your baseline tests: the same question types with new numbers, so the two compare slot by slot.');
        kidsT.push(h('div', { class: 'row' }, h('span', { class: 'meta', text: 'Checkpoints' }), cp, tip));
        // tests share (L7)
        const pv = W.pv;
        if (pv && pv.tests && pv.hours) {
          const tmin = pv.tests.count * (pv.tests.size === 'section' ? 70 : 35), share = tmin / (pv.hours * 60);
          if (share > 0.3 && f.tests !== 'weekly') kidsT.push(h('div', { class: 'wz-note' }, h('p', { text: `Tests take ${Math.round(share * 100)}% of your time. Tests measure; practice raises the score.` }),
            btn('Weekly instead', 'btn sm', () => { f.tests = 'weekly'; changed(); })));
        }
      }
      out.push(field('Practice tests', ...kidsT));
      const clk = h('div', { 'data-k': 'clock' });
      UI.seg(clk, [['off', 'Off'], ['auto', 'Auto'], ['always', 'Always']].map(([value, label]) => ({ value, label })), { value: f.clock, label: 'Clock on practice sets', onChange: v => { f.clock = v; changed(false); } });
      out.push(field('Clock on practice sets', clk, h('p', { class: 'help', text: 'Auto times sets from Sharpen on, and sooner for a skill you’re slow on. Each question gets its own budget: easy 1:05 · medium 1:35 · hard 2:06.' })));
      // usual time and place
      const tm = h('div', { 'data-k': 'time' });
      const known = { '08:00': 'Morning 8:00', '15:00': 'Afternoon 15:00', '18:00': 'Evening 18:00' };
      UI.chips(tm, [...Object.entries(known).map(([value, label]) => ({ value, label })), { value: 'other', label: 'Other' }],
        { value: known[f.time] ? f.time : 'other', label: 'Usual time', onChange: v => { if (v !== 'other') { f.time = v; changed(false); } else { f.time = f.time || '17:00'; changed(); } } });
      if (!known[f.time]) { const ti = h('input', { type: 'time', class: 'field sm', value: f.time || '17:00', 'aria-label': 'Your time' }); ti.addEventListener('change', () => { f.time = ti.value || null; changed(false); }); tm.append(ti); }
      const place = h('input', { class: 'field sm', maxlength: '30', value: f.place || '', placeholder: 'the library', 'aria-label': 'Where you study' });
      place.addEventListener('change', () => { f.place = place.value.trim() || null; changed(false); });
      out.push(field('Usual time', tm, h('div', { class: 'row' }, h('span', { class: 'meta', text: 'Where' }), place)));
      // R&W time (L21)
      const rwm = h('div', { 'data-k': 'rwm' });
      UI.chips(rwm, [0, 15, 30, 45, 60].map(v => ({ value: v, label: v ? `${v} min` : 'None' })), { value: f.rw_minutes || 0, label: 'R&W time a study day', onChange: v => { f.rw_minutes = v; changed(); } });
      out.push(field('R&W time a study day', rwm, f.rw_minutes ? h('p', { class: 'help', text: `On top of your Math time · ${UI.dur(week)} + ${UI.dur(f.rw_minutes * n)} a week` }) : null));
      const pv = W.pv;
      if (pv) out.push(h('p', { class: 'line-t', text: `Until ${D(f.exam_date)}: ${pl(pv.study_days, 'study day')} · ${UI.num(pv.hours)} h${pv.tests.count ? ` · ${pl(pv.tests.count, 'test')}` : ''} · about ${UI.num(pv.questions)} new questions` }));
      return out;
    }

    function suggestion() {
      const topics = (W.map && W.map.topics) || [];
      const pts = W.pv && W.pv.points && W.pv.points.math;
      const s = { focus: {}, skills: {} };
      if (pts && pts.skills && pts.skills.length) {
        const byV = pts.skills.slice().sort((a, b) => (b.v || 0) - (a.v || 0));
        byV.filter(x => x.gain >= 10).slice(0, 3).forEach(x => { s.skills[x.topic] = 'focus'; });
        const total = pts.skills.reduce((a, x) => a + Math.max(0, x.gain || 0), 0);
        const dom = {};
        pts.skills.forEach(x => { const dn = (UI.TOPIC[x.topic] || {}).domain; dom[dn] = (dom[dn] || 0) + Math.max(0, x.gain || 0); });
        Object.entries(dom).filter(([, g]) => total && g / total >= 0.4).slice(0, 2).forEach(([dn]) => { s.focus[dn] = 'focus'; });
        topics.filter(t => t.mastery >= 0.8 && (pts.skills.find(x => x.topic === t.topic) || {}).gain < 5).forEach(t => { if (!s.skills[t.topic]) s.skills[t.topic] = 'strong'; });
        return s;
      }
      const worked = DOMAINS.map(dn => { const ts = topics.filter(t => t.domain === dn && t.answered); return { dn, m: ts.length ? ts.reduce((a, t) => a + t.mastery, 0) / ts.length : null, traps: topics.filter(t => t.domain === dn).reduce((a, t) => a + (t.traps || []).length, 0) }; });
      const allTraps = worked.reduce((a, x) => a + x.traps, 0);
      const weak = worked.filter(x => x.m !== null && x.m < 0.8).sort((a, b) => a.m - b.m)[0];
      if (weak) s.focus[weak.dn] = 'focus';
      worked.filter(x => allTraps && x.traps / allTraps >= 1 / 3).slice(0, 2).forEach(x => { if (Object.values(s.focus).length < 2) s.focus[x.dn] = 'focus'; });
      worked.filter(x => x.m !== null && x.m >= 0.8).forEach(x => { if (!s.focus[x.dn]) s.focus[x.dn] = 'strong'; });
      return s;
    }
    function step4() {
      const out = [h('header', {}, h('h2', { class: 'h2', text: 'What to focus on' }), h('p', { text: 'Focus gets most of your week. Strong stays on light review.' }))];
      if (!W.map) { out.push(h('span', { class: 'skel', style: 'height: 220px' })); return out; }
      const topics = W.map.topics || [];
      const byTopic = Object.fromEntries(topics.map(t => [t.topic, t]));
      const answered = topics.reduce((a, t) => a + (t.answered || 0), 0);
      const pts = W.pv && W.pv.points && W.pv.points.math;
      const sug = suggestion();
      const dFocus = () => Object.values(f.focus).filter(v => stateOf(v) === 'focus').length;
      const sFocus = () => Object.values(f.skills).filter(v => stateOf(v) === 'focus').length;
      const setSkill = (t, v) => { if (v === 'normal') delete f.skills[t]; else f.skills[t] = v; changed(); };
      const setDom = (dn, v) => { if (v === 'normal') delete f.focus[dn]; else f.focus[dn] = v; changed(); };
      // where your points are (L1)
      const panel = h('section', { class: 'wz-points', 'data-k': 'points' });
      if (pts && pts.skills && pts.skills.length) {
        const top = pts.skills.slice().sort((a, b) => (b.v || 0) - (a.v || 0)).slice(0, 6);
        const top3 = top.slice(0, 3).reduce((a, x) => a + Math.max(0, x.gain || 0), 0);
        panel.append(h('p', { class: 'label', text: 'Where your points are' }), h('p', { class: 'meta', text: `About +${Math.round(pts.total || 0)} on the table · your top 3 together ≈ +${Math.round(top3)}` }));
        for (const s of top) {
          const t = byTopic[s.topic] || {};
          const row = UI.skillRow(null, { topic: s.topic, mastery: t.mastery, answered: t.answered, accuracy: s.accuracy, open: (t.traps || []).length, gain: s.gain, per_test: s.per_test, minutes: s.minutes });
          const on = stateOf(f.skills[s.topic]) === 'focus';
          row.querySelector('.skill-side').append(h('button', { type: 'button', class: 'btn sm', 'aria-pressed': String(on), disabled: !on && sFocus() >= 6 || null, text: '↑ Focus',
            onclick: () => setSkill(s.topic, on ? 'normal' : 'focus') }));
          panel.append(row);
        }
      } else panel.append(h('p', { class: 'help', text: answered >= 30 ? 'Where your points are shows once the plan has your first estimate.' : `Answer 30 questions and this shows where your points are · ${answered} of 30` }));
      out.push(panel);
      // counters and suggestions
      const cnt = h('div', { class: 'row', 'data-k': 'counters' },
        h('span', { class: dFocus() ? 'tag or' : 'tag', text: `${dFocus()}/2 focus` }),
        Object.values(f.focus).filter(v => stateOf(v) === 'strong').length ? h('span', { class: 'tag line', text: `${Object.values(f.focus).filter(v => stateOf(v) === 'strong').length} strong` }) : null,
        sFocus() ? h('span', { class: 'tag', text: `${sFocus()}/6 skills on focus` }) : null,
        answered ? btn('Use suggestions', 'quiet', () => { f.focus = { ...sug.focus }; f.skills = { ...sug.skills }; changed(); }) : null,
        btn('Reset', 'quiet', () => { f.focus = {}; f.skills = {}; changed(); }));
      out.push(cnt);
      if (dFocus() >= 2) out.push(h('p', { class: 'help', text: '2 focus areas at most. Move one back to Normal to pick another.' }));
      if (sFocus() >= 6) out.push(h('p', { class: 'help', text: '6 skills at most.' }));
      // the four domains, each with its skills open (decision 4)
      const rows = h('div', { class: 'wz-rows' });
      for (const dn of DOMAINS) {
        const ts = UI.TOPICS.filter(t => t.domain === dn);
        const st = ts.map(t => byTopic[t.slug] || { answered: 0 });
        const ans = st.reduce((a, x) => a + (x.answered || 0), 0);
        const right = st.reduce((a, x) => a + Math.round((x.accuracy || 0) * (x.answered || 0)), 0);
        const traps = st.reduce((a, x) => a + (x.traps || []).length, 0);
        const state = stateOf(f.focus[dn]);
        const seg = h('div', { 'data-k': `dom:${dn}` });
        UI.seg(seg, [{ value: 'focus', label: '↑ Focus', disabled: state !== 'focus' && dFocus() >= 2 }, { value: 'normal', label: '— Normal' }, { value: 'strong', label: '✓ Strong' }],
          { value: state, label: `${dn}: focus, normal or strong`, onChange: v => setDom(dn, v) });
        const sugState = sug.focus[dn];
        const gain = pts && pts.skills ? pts.skills.filter(x => (UI.TOPIC[x.topic] || {}).domain === dn).reduce((a, x) => a + Math.max(0, x.gain || 0), 0) : 0;
        const onFocus = ts.filter(t => stateOf(f.skills[t.slug]) === 'focus').length;
        const head = h('div', { class: 'wz-dom-head' },
          h('div', {}, h('p', { class: 'h3', text: dn }), h('p', { class: 'meta', text: [`${Math.round(WEIGHT[dn] * 100)}% of the test`, gain >= 5 ? `≈ +${Math.round(gain)} on the table` : null].filter(Boolean).join(' · ') }),
            h('p', { class: 'meta', text: ans ? [`${UI.num(ans)} answered`, `${Math.round(right / ans * 100)}% right`, traps ? pl(traps, 'mistake') : null].filter(Boolean).join(' · ') : 'Not started' }),
            sugState && sugState !== state ? h('span', { class: 'badge soft', text: `Suggested: ${sugState === 'focus' ? 'Focus' : 'Strong'}` }) : null),
          seg);
        const skills = h('div', { class: 'wz-skills' }, h('p', { class: 'meta', text: onFocus ? `${pl(onFocus, 'skill')} on focus` : pl(ts.length, 'skill') }));
        for (const t of ts) {
          const s = byTopic[t.slug] || { answered: 0 };
          const sst = stateOf(f.skills[t.slug]);
          const sseg = h('div', { 'data-k': `sk:${t.slug}` });
          UI.seg(sseg, [{ value: 'focus', label: 'Focus', disabled: sst !== 'focus' && sFocus() >= 6 }, { value: 'normal', label: '—' }, { value: 'strong', label: 'Strong' }],
            { value: sst, label: `${t.short}: focus, normal or strong`, onChange: v => setSkill(t.slug, v) });
          const g = pts && pts.skills && pts.skills.find(x => x.topic === t.slug);
          skills.append(h('div', { class: 'wz-skill' }, h('span', { class: 'nm' }, UI.glyph(t.slug), t.short, (s.traps || []).length ? h('span', { class: 'dot', 'aria-label': pl(s.traps.length, 'open mistake') }) : null),
            h('span', { class: 'meta', text: s.answered ? [`${UI.num(s.answered)} answered`, `${Math.round((s.accuracy || 0) * 100)}% right`, g ? (g.gain >= 5 ? `≈ +${Math.round(g.gain)}` : null) : s.answered < 5 ? 'Not measured yet' : null].filter(Boolean).join(' · ') : 'Not started' }), sseg));
        }
        rows.append(h('div', { class: 'wz-dom', 'data-state': state }, head, skills));
      }
      out.push(rows);
      // the split the scheduler deals (2e SplitBar)
      if (W.pv && W.pv.split) out.push(field('Your practice week', splitBar(W.pv.split, W.pv.base_split, W.pv.split_points && W.pv.split_points.math)));
      // Reading & Writing (L21)
      const rwFocus = () => Object.values(f.rw_focus || {}).filter(v => v === 'focus').length;
      const rwBox = h('div', { class: 'wz-rows' });
      const rwLog = Object.fromEntries(((d.rw_domains) || []).map(x => [x.domain, x]));
      for (const [dn, share, does] of RW) {
        const st = (f.rw_focus || {})[dn] || 'normal';
        const seg = h('div', { 'data-k': `rw:${dn}` });
        UI.seg(seg, [{ value: 'focus', label: '↑ Focus', disabled: st !== 'focus' && rwFocus() >= 2 }, { value: 'normal', label: '— Normal' }, { value: 'strong', label: '✓ Strong' }],
          { value: st, label: `${dn}: focus, normal or strong`, onChange: v => { f.rw_focus = { ...(f.rw_focus || {}) }; if (v === 'normal') delete f.rw_focus[dn]; else f.rw_focus[dn] = v; changed(); } });
        const lg = rwLog[dn];
        rwBox.append(h('div', { class: 'wz-dom', 'data-state': st }, h('div', { class: 'wz-dom-head' },
          h('div', {}, h('p', { class: 'h3', text: dn }), h('p', { class: 'meta', text: `about ${share}% of the R&W section · Focus: ${does}` }),
            h('p', { class: 'meta', text: lg && lg.of ? `${lg.missed} missed of ${lg.of}` : 'No R&W results yet · log them after a Bluebook test' })), seg)));
      }
      out.push(field(`Reading & Writing · ${rwFocus()}/2 focus`, rwBox));
      // auto focus, extras, words, own tasks
      const auto = h('div');
      UI.switch(auto, { checked: (UI.prefs.now && UI.prefs.now().plan_auto_focus) !== false, label: 'Move a skill off Focus when it passes its check',
        onChange: v => UI.api('/me', { method: 'PUT', body: { prefs: { plan_auto_focus: v } } }) });
      const ex = h('div', { class: 'wz-rows' });
      [['recheck', 'Warm-up', 'Questions you got right before, back just as you start to forget them, mixed and unlabelled.'], ['qotd', 'Question of the day', null],
        ['challenge', 'Daily challenge', 'The same 10 question types for everyone, your own numbers.']].forEach(([k, label, help]) => {
        const box = h('div', { style: 'padding: 6px 0' });
        UI.switch(box, { checked: !!f.extras[k], label, onChange: v => { f.extras = { ...f.extras, [k]: v }; changed(false); } });
        if (help) box.append(h('p', { class: 'help', text: help }));
        ex.append(box);
      });
      out.push(field('When a skill is ready', auto), field('Extras', ex, h('p', { class: 'help', text: 'Extras never count against the day’s minutes.' })));
      const words = h('div', { 'data-k': 'words' });
      const goal = UI.prefs.now ? UI.prefs.now().words_goal : 10;
      UI.chips(words, [0, 5, 10, 20].map(v => ({ value: v, label: v ? `${v} new a day` : 'Off' })), { value: goal ?? 10, label: 'Words',
        onChange: v => UI.prefs.set ? UI.prefs.set({ words_goal: v }) : UI.api('/me', { method: 'PUT', body: { prefs: { words_goal: v } } }) });
      out.push(field('Words · SAT words and transitions', words, h('p', { class: 'help', text: 'About 6 minutes a day, counted as Reading & Writing time.' })));
      out.push(field('Your own tasks', ownTasks()));
      return out;
    }
    function splitBar(split, base, points) {
      const box = h('div', { style: 'display: grid; gap: 8px' });
      const bar = (vals, label, focusOrange) => h('div', { class: 'wz-split', role: 'img', 'aria-label': `${label}: ${DOMAINS.map(dn => `${DSHORT[dn]} ${Math.round((vals[dn] || 0) * 100)}%`).join(', ')}` },
        DOMAINS.filter(dn => vals[dn] > 0).map(dn => h('span', { style: `flex-grow: ${vals[dn]}`, 'data-on': focusOrange && stateOf(f.focus[dn]) === 'focus' ? '' : null }, `${DSHORT[dn]} ${Math.round(vals[dn] * 100)}%`)));
      box.append(bar(split, 'Your practice week', true));
      if (base) box.append(h('p', { class: 'meta', text: `was ${DOMAINS.map(dn => Math.round((base[dn] || 0) * 100)).join(' / ')} by the test’s weights` }));
      if (points && Object.values(points).some(Boolean)) box.append(h('p', { class: 'label', style: 'margin: 6px 0 0', text: 'Where your points are' }), bar(points, 'Where your points are', false));
      return box;
    }
    function ownTasks() {
      const box = h('div', { class: 'wz-own', 'data-k': 'own' });
      (f.custom || []).forEach((t, i) => box.append(h('div', { class: 'wz-own-item' }, h('p', { text: `${t.title} · ${t.minutes} min · ${t.repeat === 'study_days' ? 'every study day' : t.repeat ? `weekly on ${DOW[+t.repeat.split(':')[1]]}` : `once on ${D(t.day)}`}` }),
        btn('×', 'quiet', () => { f.custom.splice(i, 1); changed(); }, { 'aria-label': `Remove ${t.title}` }))));
      const form = h('div');
      const open = (pre = {}) => {
        const title = h('input', { class: 'field sm', maxlength: '60', value: pre.title || '', 'aria-label': 'Title', placeholder: 'Title' });
        const mins = h('input', { type: 'number', class: 'field sm', min: '5', max: '240', value: String(pre.minutes || 30), 'aria-label': 'Minutes' });
        const firstSat = (() => { let x = addDays(today(), 7); while (dow(x) !== 5) x = addDays(x, 1); return x; })();
        const rep = h('select', { class: 'field sm', 'aria-label': 'When' }, h('option', { value: 'once', text: 'Once on…' }), h('option', { value: 'study_days', text: 'Every study day' }),
          DOW.map((nm, i) => h('option', { value: `weekly:${i}`, text: `Weekly on ${nm}` })));
        rep.value = pre.repeat || 'once';
        const day = h('input', { type: 'date', class: 'field sm', min: today(), max: f.exam_date ? addDays(f.exam_date, -2) : '', value: pre.day || firstSat, 'aria-label': 'Day' });
        rep.addEventListener('change', () => { day.hidden = rep.value !== 'once'; });
        day.hidden = rep.value !== 'once';
        const e = h('p', { class: 'field-err', hidden: true });
        const add = btn('Add', 'btn sm ink', () => {
          const m = Math.round(+mins.value);
          if (!title.value.trim() || !(m >= 5 && m <= 240)) { e.textContent = 'A title (60 characters at most) and 5 to 240 minutes.'; e.hidden = false; return; }
          if ((f.custom || []).length >= 10) { e.textContent = 'At most 10 of your own tasks.'; e.hidden = false; return; }
          f.custom = [...(f.custom || []), { title: title.value.trim(), minutes: m, ...(rep.value === 'once' ? { day: day.value } : { repeat: rep.value }), ...(pre.type ? { type: pre.type } : {}) }];
          changed();
        });
        form.replaceChildren(h('div', { class: 'wz-form' }, title, mins, rep, day, add), e);
        title.focus();
      };
      const chips = h('div', { class: 'chips' },
        btn('+ Official Bluebook practice test · once', '', () => open({ title: 'Official Bluebook practice test', minutes: 134, type: 'bluebook' })),
        btn('+ Reading & Writing · 30 min · every study day', '', () => { f.rw_minutes = 30; changed(); }, { disabled: f.rw_minutes >= 30 || null }),
        btn('+ Tutor session', '', () => open({ title: 'Tutor session', minutes: 60, repeat: 'weekly:5', type: 'tutor' })),
        btn('+ Other…', '', () => open()));
      box.append(chips, form, h('p', { class: 'help', text: 'They count toward the day’s minutes and are done when you tick them.' }));
      return box;
    }

    draw();
    if (!ctx.loading) { preview(); save(); }
    return { W };
  }

  Object.assign(UI, { planWizard });
})();
