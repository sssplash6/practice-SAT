/* ============================================================================
   SAT Freshman -- /plan/ (S7; spec 3.6, plan.md L1-L21, decisions 4 and 7)

   One route. The URL holds the mode: /plan/ (the plan view, or the landing with no
   active plan), ?tab=progress|plans, ?day=YYYY-MM-DD, ?setup=1&step=1..4 and
   ?edit=<id>&step=1..4 (the wizard, wizard.js), ?id=<id> (an older plan, read-only),
   ?view=<token> (a shared read-only plan). Every number comes from server/plan.py
   through GET /api/plan; this file draws it and sends the student's changes.
   The Progress tab is progress.js (UI.planProgress); rows are plan-ui.js (UI.taskRow).
   ========================================================================== */
(() => {
  'use strict';
  const doc = document, h = UI.h;
  const root = doc.getElementById('plan');
  let Q = new URLSearchParams(location.search);
  const S = { d: null, sel: Q.get('day'), tab: Q.get('tab') || 'plan', open: null, trim: null, kb: -1, shown: 20, readonly: false, older: null };
  const R = {};
  const DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const LETTER = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
  const pad = n => String(n).padStart(2, '0');
  const isoOf = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const toD = s => new Date(`${s}T12:00`);
  const addDays = (s, n) => { const d = toD(s); d.setDate(d.getDate() + n); return isoOf(d); };
  const diff = (a, b) => Math.round((toD(b) - toD(a)) / 864e5);
  const dow = s => (toD(s).getDay() + 6) % 7;
  const monday = s => addDays(s, -dow(s));
  const today = () => isoOf(new Date());
  const D = (s, style) => UI.date(s, style || 'short');
  const dayName = s => `${DOW[dow(s)]} ${D(s)}`;
  const tn = slug => (UI.TOPIC[slug] || {}).short || String(slug || '').replace(/_/g, ' ');
  const pl = (n, w, ws) => `${UI.num(n)} ${n === 1 ? w : (ws || w + 's')}`;
  const enc = encodeURIComponent;
  const api = (p, o) => UI.api(p, o);
  const pid = () => S.d.active.id;
  const cfg = () => S.d.active.cfg;
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const STUDY = new Set(['practice', 'test']);
  const DONE = new Set(['done', 'marked', 'made_up']);
  const KIND = { practice: 'Practice', test: 'Test day', rest: 'Rest', off: 'Day off', eve: 'Rest before the SAT', exam: 'SAT', before: 'Before the plan', after: 'After the SAT' };
  const STATUS = { done: 'Done', partial: 'Partly done', missed: 'Missed', skipped: 'Skipped', made_up: 'Made up' };
  const CB = 'https://satsuite.collegeboard.org/sat/registration';
  // the server's week themes still carry slugs and ISO dates: say them as words
  const TASKNAME = { fix: 'Fix mistakes', recheck: 'warm-up', focus: 'focus set', test: 'test', learn: 'Learn it', check: 'check', habit: 'habit task', pace: 'pace set', map: 'Map', sweep: 'sweep', words: 'Words', custom: 'own task', extra: 'extra set' };
  const pretty = text => String(text || '')
    .replace(/\b(\d{4}-\d{2}-\d{2}):([a-z]+)(?::([a-z_]+))?/g, (m, dd, k, tp) => `${DOW[dow(dd)]}’s ${TASKNAME[k] || k}${tp && UI.TOPIC[tp] ? ` on ${UI.TOPIC[tp].short}` : ''}`)
    .replace(/\b\d{4}-\d{2}-\d{2}\b/g, m => DOW[dow(m)]).replace(/\b[a-z]+(?:_[a-z]+)*\b/g, m => UI.TOPIC[m] ? UI.TOPIC[m].short : m);
  const rowErr = text => Object.assign(new Error(text), { rowText: text });
  const btn = (label, cls, onClick, attrs = {}) => h('button', { type: 'button', class: cls, onclick: onClick, ...attrs }, label);
  async function busy(b, fn) {
    if (b) b.setAttribute('aria-busy', 'true');
    try { return await fn(); } finally { if (b) b.removeAttribute('aria-busy'); }
  }
  const dayOf = date => (S.d && S.d.days || []).find(x => x.date === date) || null;
  const questionTask = t => UI.taskQuestion(t);
  const undone = t => !DONE.has(t.status) && t.status !== 'skipped' && t.status !== 'moved';

  /* ------------------------------------------------------------ boot and routing */
  function url(params, push) {
    const u = new URL(location.href);
    u.search = '';
    for (const [k, v] of Object.entries(params)) if (v !== null && v !== undefined && v !== '') u.searchParams.set(k, v);
    history[push ? 'pushState' : 'replaceState'](null, '', u);
    Q = new URLSearchParams(u.search);
  }
  function go(params) { url(params, true); route(); scrollTo(0, 0); }
  addEventListener('popstate', () => { Q = new URLSearchParams(location.search); S.tab = Q.get('tab') || 'plan'; S.sel = Q.get('day') || S.sel; route(); });

  function skeleton() {
    root.replaceChildren(
      h('div', { class: 'pl-title' }, h('span', { class: 'skel line lg', style: 'width: 240px' })),
      h('div', { class: 'pl-tiles' }, [0, 1, 2, 3].map(() => h('div', { class: 'stat' }, h('span', { class: 'skel line', style: 'width: 60%' }), h('span', { class: 'skel num' })))),
      h('div', { class: 'pl-cols' }, h('div', { class: 'card' }, h('span', { class: 'skel', style: 'height: 180px' })), h('div', { class: 'card' }, h('span', { class: 'skel', style: 'height: 180px' }))),
      h('div', { class: 'card pl-sec' }, h('span', { class: 'skel', style: 'height: 90px' })));
  }
  function failPage() {
    root.replaceChildren();
    UI.cardError(root, () => { skeleton(); load(); }, 'The server is not answering.');
  }
  function load(fresh) {
    return UI.cached('/plan', (d, fromCache) => {
      S.d = d;
      S.stale = fromCache;
      route();
    }, { store: 'local', until: 'day', fresh: !!fresh, onFresh: () => { S.stale = false; if (R.upd) R.upd.hidden = true; } })
      .catch(e => { if (!S.d) failPage(); throw e; });
  }
  // after a change: the whole payload again, so tiles, week and stats agree
  let reloading = null;
  function reload() {
    reloading = api('/plan').then(d => { S.d = d; route(true); return d; }).catch(() => null).finally(() => { reloading = null; });
    return reloading;
  }

  function route(keep) {
    if (Q.get('view')) return sharedView();
    if (Q.has('setup') || Q.has('edit')) return wizard();
    if (!S.d) return;
    if (Q.get('id') && (!S.d.active || Q.get('id') !== S.d.active.id)) return olderPlan(Q.get('id'));
    S.readonly = false;
    if (!S.d.active) return landing();
    view(keep);
  }

  function wizard() {
    if (!UI.planWizard) { root.replaceChildren(h('p', { class: 'line-t', text: 'The plan builder did not load. Reload the page.' })); return; }
    const start = d => UI.planWizard(root, {
      d, step: +(Q.get('step') || 1), edit: Q.get('edit'), fresh: Q.has('fresh'), from: Q.get('from'),
      onDone: (reply, how) => {
        S.d = reply;
        const days = reply.active ? reply.stats.study_days_total : 0;
        if (how === 'create' && reply.active) UI.toast(`Plan made · ${pl(days, 'study day')} to ${D(reply.active.cfg.exam_date)}`);
        else if (how === 'save') UI.toast('Plan updated');
        S.tab = 'plan'; S.sel = null;
        url({});
        UI.cached.clear && UI.cached.clear();
        route();
        scrollTo(0, 0);
        focusStart();
      },
      onExit: () => { history.length > 1 && doc.referrer.includes(location.host) ? history.back() : go({}); },
      step2url: (step, replace) => url({ ...(Q.get('edit') ? { edit: Q.get('edit') } : { setup: 1 }), step }, !replace),
    });
    if (S.d) start(S.d);
    else { skeleton(); api('/plan').then(d => { S.d = d; start(d); }).catch(failPage); }
  }

  /* ------------------------------------------------------------ the landing (no active plan) */
  function landing() {
    const d = S.d, pr = d.proposal || null, pc = pr && pr.cfg, pv = pr && pr.preview;
    doc.title = 'Plan · SAT Freshman';
    const withData = !!(pc && pc.current !== null && pc.current !== undefined) || (UI.answered || 0) >= 30;
    const draft = d.draft && d.draft.fields ? d.draft : null;
    const left = h('div', {},
      h('p', { class: 'k', text: 'Study plan' }),
      h('h1', { text: 'A plan to your score, one day at a time' }),
      h('p', { class: 'lead', text: 'Mistakes first, then your focus skills, and a fresh test each week, up to exam day. Skip, move or add anything; miss a day and it redraws from today.' }));
    const acts = h('div', { class: 'row' });
    if (withData && pc) {
      const use = btn('Use this plan', 'pill', () => busy(use, () => useProposal(pc)));
      acts.append(use, btn('Adjust…', 'btn', () => go({ setup: 1, step: 1, from: 'proposal' })));
    } else acts.append(btn(draft ? 'Start over' : 'Create my plan', 'pill', () => go({ setup: 1, step: 1, ...(draft ? { fresh: 1 } : {}) })));
    left.append(acts, h('p', { class: 'meta', text: 'About a minute · free · as many plans as you like' }));
    const right = withData && pv ? readyPanel(pc, pv) : miniTiles(pc);
    const hero = h('section', { class: 'pl-hero', 'aria-label': 'Study plan' }, left, right);
    if (draft) hero.append(draftTile(draft));
    const parts = [hero];
    const pts = pv && pv.points && pv.points.math;
    if (withData && pts) parts.push(numbersCard(pts));
    parts.push(bankStats(d.bank || {}), howItWorks());
    if (!withData && pv && pv.sample_day && pv.sample_day.tasks.length) {
      const c = h('section', { class: 'card pl-sec' }, h('div', { class: 'card-head' }, h('h2', { text: 'A day in your plan' }),
        pv.sample_day.date && h('span', { class: 'meta', text: `day 1 · ${D(pv.sample_day.date, 'long')}` })));
      const list = h('div', { class: 'trows' });
      pv.sample_day.tasks.forEach(t => UI.taskRow(list, t, { readonly: true }));
      c.append(list);
      parts.push(c);
    }
    if ((d.plans || []).length) parts.push(plansCard(d.plans, null));
    root.replaceChildren(...parts);
  }
  function planLine(c) {
    const days = c.days.split('').map((x, i) => x === '1' ? DOW[i] : null).filter(Boolean);
    const focus = Object.entries(c.focus || {}).filter(([, v]) => (v.state || v) === 'focus').map(([k]) => k)
      .concat(Object.entries(c.skills || {}).filter(([, v]) => (v.state || v) === 'focus').map(([k]) => tn(k)));
    return [D(c.exam_date), c.current !== null && c.current !== undefined ? `${c.current} → ${c.target}` : `? → ${c.target}`,
      `${c.minutes} min × ${days.length === 5 && c.days === '1111100' ? 'Mon–Fri' : days.join(', ')}`, testsLabel(c),
      focus.length ? `Focus ${focus.join(', ')}` : null].filter(Boolean).join(' · ');
  }
  function testsLabel(c) {
    if (c.tests === 'none') return 'no tests';
    const size = c.test_size === 'section' ? 'section' : 'module';
    return c.tests === 'weekly' ? `${size} weekly${c.test_day !== null && c.test_day !== undefined ? ` · ${DOW[c.test_day]}` : ''}` : c.tests === 'twice' ? `${size} twice a week` : `${size} every study day`;
  }
  function readyPanel(pc, pv) {
    const box = h('div', { class: 'pl-ready' }, h('p', { class: 'k', text: 'Your plan, ready' }), h('p', { class: 'line-t', text: planLine(pc) }));
    const cal = h('div');
    box.append(cal);
    const rows = (pv.calendar || []).map(x => ({ day: x.date, kind: x.kind, minutes: x.minutes, phase: x.phase }));
    if (UI.calendar && rows.length) UI.calendar(cal, { look: 'plan', compact: true, plan: rows, legend: false,
      marks: { start: today(), end: pc.exam_date, exam: pc.exam_date, today: today() }, min: today(), max: pc.exam_date });
    if (pv.sample_day && pv.sample_day.tasks.length) {
      const list = h('div', { class: 'trows' });
      pv.sample_day.tasks.slice(0, 5).forEach(t => UI.taskRow(list, t, { readonly: true, compact: true }));
      box.append(h('p', { class: 'k', text: `Day 1 · ${D(pv.sample_day.date, 'long')}` }), list);
    }
    return box;
  }
  function miniTiles(pc) {
    const sh = (UI.shellData && UI.shellData()) || {};
    const open = sh.mistakes && typeof sh.mistakes === 'object' ? sh.mistakes.open : sh.mistakes;
    const box = h('div', { class: 'pl-mini' });
    const now = pc && pc.current;
    UI.tile(box, { label: 'Math now', value: now || null, missing: '', sub: now ? 'your starting point' : null });
    if (!now) box.lastChild.append(h('a', { class: 'quiet', href: '/tests/', text: 'Take a test' }));
    if (pc && pc.exam_date) UI.tile(box, { label: 'Next SAT', value: D(pc.exam_date), sub: `${pl(diff(today(), pc.exam_date), 'day')}` });
    if (open) UI.tile(box, { label: 'Open mistakes', value: open, href: '/review/' });
    return box;
  }
  function draftTile(draft) {
    const f = draft.fields || {};
    const bits = [`Draft · step ${draft.step || 1} of 4`, f.exam_date && D(f.exam_date), f.target && `${f.current || '?'} → ${f.target}`].filter(Boolean);
    const box = h('div', { class: 'pl-draft' }, h('p', { text: bits.join(' · ') }));
    const cont = btn('Continue', 'pill sm', () => go({ setup: 1, step: draft.step || 1 }));
    const discard = btn('Discard', 'quiet', () => {
      box.replaceChildren(h('p', { text: 'Discard draft?' }),
        btn('Discard', 'btn sm ink', async e => busy(e.currentTarget, async () => { await api('/plan/draft', { method: 'DELETE' }); S.d.draft = null; landing(); })),
        btn('Keep', 'quiet', () => box.replaceWith(draftTile(draft))));
    });
    box.append(cont, discard);
    return box;
  }
  function numbersCard(pts) {
    const top = (pts.skills || []).slice().sort((a, b) => (b.v || 0) - (a.v || 0)).slice(0, 3).map(s => tn(s.topic));
    const route = pts.route;
    const lines = [pts.total ? `≈ +${Math.round(pts.total)} on the table${top.length ? ` · ${top.join(', ')}` : ''}` : null,
      route && route.m1 !== null && route.m1 !== undefined ? `First modules about ${Math.round(route.m1 * 100)}% · 14 of 22 routes up` : null].filter(Boolean);
    if (!lines.length) return h('span', { hidden: true });
    return h('section', { class: 'card pl-sec' }, h('div', { class: 'card-head' }, h('h2', { text: 'Your numbers' })),
      lines.map(t => h('p', { class: 'line-t', text: t })));
  }
  function bankStats(b) {
    const w = b.words || {};
    const tile = (n, label, line, extra) => h('div', { class: 'card' }, n ? h('span', { class: 'n', text: n }) : null, h('h3', { class: 'h3', text: label }), extra || null, h('p', { text: line }));
    return h('section', { class: 'pl-bank pl-sec', 'aria-label': 'What the plan draws on' },
      tile('∞', 'Practice sections', 'A new adaptive section every sitting, built to the published blueprint.'),
      tile(UI.num(b.templates || 386), `Question types · ${b.topics || 19} skills`, 'Every question new to you. None repeat.'),
      h('div', { class: 'card' }, h('h3', { class: 'h3', text: 'Every wrong answer is named' }),
        b.example && h('p', { class: 'line-t', text: `“${b.example.label}”` }), b.example && b.example.topic && UI.chip(b.example.topic),
        h('p', { text: 'The next question is the same trap with new numbers.' })),
      tile(w.known ? `≈ ${UI.num(w.known)}` : null, w.known ? 'SAT words you know' : 'Words · SAT words and transitions',
        'Spaced review that measures itself: the first part of Reading & Writing here.'));
  }
  function howItWorks() {
    const step = (n, t, p) => h('div', { class: 'card' }, h('span', { class: 'num-c', text: String(n) }), h('h3', { class: 'h3', text: t }), h('p', { text: p }));
    return h('section', { class: 'pl-how pl-sec', 'aria-label': 'How it works' },
      step(1, 'Four questions', 'Your score, your target and date, your time, your focus. Filled in from your results where there are any.'),
      step(2, 'Every day planned', 'Open mistakes first, then focus skills, a test on your test day. Harder and timed as the exam gets close.'),
      step(3, 'It keeps up', 'Skip, move or add tasks; take a day off; a new test offers to move your starting score.'));
  }
  async function useProposal(pc) {
    try {
      const r = await api('/plan', { method: 'POST', body: pc });
      S.d = r; S.tab = 'plan'; S.sel = null;
      ls.set('satf.plan.built', { id: r.active.id, day: today() });
      url({});
      UI.toast(`Plan made · ${pl(r.stats.study_days_total, 'study day')} to ${D(r.active.cfg.exam_date)}`);
      route();
      focusStart();
      if (!UI.reduced || !UI.reduced()) root.querySelectorAll('.cal-d[data-kind]').forEach((c, i) => c.animate &&
        c.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160, delay: Math.min(240, i * 6), fill: 'backwards' }));
    } catch (e) { UI.toast(e.status === 422 ? e.message : 'Couldn’t make the plan. Try again.'); }
  }

  // after a create: Start today, or the day itself on a rest day
  function focusStart() {
    const el = R.start || R.day;
    if (!el) return;
    if (!R.start) el.tabIndex = -1;
    el.focus();
  }

  /* ------------------------------------------------------------ the plan view */
  function titleOf() {
    const a = S.d.active, c = a.cfg;
    const total = c.rw_target && c.rw_current !== null && c.rw_current !== undefined ? c.target + c.rw_target : null;
    const auto = !a.name || /^Plan for \d{4}-\d{2}-\d{2}$/.test(a.name);
    return auto ? `${D(c.exam_date)} · ${total || c.target}` : a.name;
  }
  function view(keep) {
    const d = S.d, a = d.active, c = a.cfg;
    const t = today();
    if (!S.sel || !dayOf(S.sel)) S.sel = dayOf(t) ? t : t < a.start ? a.start : c.exam_date;
    doc.title = `${titleOf()} · Plan · SAT Freshman`;
    const had = keep && R.shell && R.shell.isConnected;
    const scrollY = window.scrollY;
    const focusId = doc.activeElement && doc.activeElement.closest && doc.activeElement.closest('[data-task]') ? doc.activeElement.closest('[data-task]').dataset.task : null;
    const title = titleRow();
    R.tiles = h('div', { class: 'pl-tiles' });
    R.banners = h('div', { class: 'pl-banners' });
    R.upd = h('p', { class: 'meta', role: 'status', hidden: !S.stale || null, text: 'Updating…' });
    R.pPlan = h('div'); R.pProg = h('div'); R.pPlans = h('div');
    const bar = h('div', { class: 'pl-tabbar' });
    R.tabs = UI.tabs(bar, [{ id: 'plan', label: 'Plan', panel: R.pPlan }, { id: 'progress', label: 'Progress', panel: R.pProg },
      { id: 'plans', label: 'Plans', panel: R.pPlans, n: (d.plans || []).length > 1 ? d.plans.length : null }],
    { value: S.tab, label: 'Plan views', onChange: id => { S.tab = id; url(paramsNow(), true); drawTab(); } });
    R.thumb = h('div', { class: 'pl-thumb' });
    R.shell = h('div', {}, R.upd, title, R.tiles, R.banners, bar, R.pPlan, R.pProg, R.pPlans, R.thumb);
    root.replaceChildren(R.shell);
    drawTiles(); drawBanners(); drawPlanTab(); drawTab();
    if (had) {
      scrollTo(0, scrollY);
      const back = focusId && root.querySelector(`[data-task="${CSS.escape(focusId)}"] button`);
      if (back) back.focus({ preventScroll: true });
    }
  }
  function paramsNow() {
    const p = {};
    if (S.tab !== 'plan') p.tab = S.tab;
    if (S.tab === 'plan' && S.sel && S.sel !== today()) p.day = S.sel;
    if (S.readonly && S.older) p.id = S.older;
    return p;
  }
  function drawTab() {
    if (S.tab === 'progress' && UI.planProgress) UI.planProgress(R.pProg, { d: S.d, api, pick: date => { S.tab = 'plan'; R.tabs.set('plan', true); pick(date); url(paramsNow(), true); drawTab(); } });
    if (S.tab === 'plans') drawPlansTab();
    drawThumb();
  }
  function titleRow() {
    const a = S.d.active, c = a.cfg;
    const days = c.days.split('').filter(x => x === '1').length;
    const focus = Object.entries(c.focus || {}).filter(([, v]) => (v.state || v) === 'focus').map(([k]) => k)
      .concat(Object.entries(c.skills || {}).filter(([, v]) => (v.state || v) === 'focus').map(([k]) => tn(k)));
    const sub = [`${days} ${days === 1 ? 'day' : 'days'}`, `${c.minutes} min`, testsLabel(c), focus.length ? `Focus ${focus.join(', ')}` : null].filter(Boolean).join(' · ');
    const total = c.rw_target && c.rw_current !== null && c.rw_current !== undefined;
    const left = h('div', {}, h('h1', { text: titleOf() }), h('p', { class: 'meta', text: total ? `Math ${c.target} · ${sub}` : sub }));
    const right = h('div', { class: 'row' });
    if (!S.readonly) {
      right.append(h('a', { class: 'quiet', href: `/plan/?edit=${enc(a.id)}&step=1`, text: 'Edit' }));
      const more = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'Plan menu', 'aria-haspopup': 'menu', html: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="6" cy="12" r="1.6" fill="currentColor"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/><circle cx="18" cy="12" r="1.6" fill="currentColor"/></svg>' });
      more.addEventListener('click', () => UI.menu(more, planMenu(), { label: 'Plan' }));
      right.append(more);
    }
    return h('header', { class: 'pl-title' }, left, right);
  }
  function planMenu() {
    const a = S.d.active;
    return [
      { label: 'Rename', onClick: async () => {
        const v = await UI.confirm({ title: 'Rename this plan', confirm: 'Save', input: { label: 'Name', value: titleOf(), maxlength: 40 } });
        if (v && v.trim()) await patchPlan({ name: v.trim().slice(0, 40) }, 'Plan renamed');
      } },
      { label: 'Duplicate', onClick: () => duplicate(a.id) },
      { label: 'Calendar…', onClick: () => calendarSheet() },
      { label: 'Share read-only…', onClick: () => shareSheet() },
      { label: 'Print', onClick: () => print() },
      { separator: true },
      { label: 'Archive', onClick: async () => {
        if (!await UI.confirm({ title: 'Archive this plan?', text: 'It stays under Plans, with its record. You can make it active again.', confirm: 'Archive', destructive: true })) return;
        const id = a.id;
        S.d = await api(`/plan/${enc(id)}/archive`, { method: 'POST' });
        UI.toast('Plan archived', { undo: async () => { S.d = await api(`/plan/${enc(id)}/activate`, { method: 'POST' }); route(); } });
        route();
      } },
    ];
  }
  async function duplicate(id) {
    try { await api(`/plan/${enc(id)}/duplicate`, { method: 'POST' }); S.d = null; go({ setup: 1, step: 1 }); }
    catch (_) { UI.toast('Couldn’t copy the plan. Try again.'); }
  }
  async function patchPlan(body, toast, undoBody) {
    const r = await api(`/plan/${enc(pid())}`, { method: 'PATCH', body });
    S.d = r;
    route(true);
    if (toast) UI.toast(toast, undoBody ? { undo: async () => { S.d = await api(`/plan/${enc(pid())}`, { method: 'PATCH', body: undoBody }); route(true); } } : {});
    return r;
  }
  function undoOf(body) {
    const c = cfg(), out = {};
    for (const k of Object.keys(body)) out[k] = k === 'current' ? c.current : c[k] === undefined ? null : c[k];
    return out;
  }

  /* ---- stat tiles (3b, L13, L16, L21) */
  function drawTiles() {
    const d = S.d, a = d.active, c = a.cfg, st = d.stats, t = today();
    const days = d.days;
    const ahead = days.filter(x => x.date >= t);
    const studyLeft = ahead.filter(x => STUDY.has(x.kind)).length;
    const testsLeft = ahead.filter(x => x.kind === 'test').length;
    const left = diff(t, c.exam_date);
    // 1 days to exam, with the time against the work left
    const t1 = h('button', { type: 'button', class: 'stat', 'aria-label': `${left} days to the SAT; show the calendar` });
    t1.addEventListener('click', () => R.cal && R.cal.scrollIntoView({ behavior: 'smooth', block: 'start' }));
    t1.append(h('span', { class: 'stat-k', text: 'Days to exam' }),
      h('span', { class: 'pl-big', text: d.state === 'exam' ? 'SAT today' : d.state === 'after' ? 'Done' : String(left) }),
      h('p', { class: 'stat-sub', text: d.state === 'eve' ? 'SAT tomorrow' : d.state === 'after' ? `SAT was ${D(c.exam_date, 'long')}` : `to ${D(c.exam_date, 'long')}` }),
      studyLeft ? h('p', { class: 'stat-sub', text: [pl(studyLeft, 'study day'), testsLeft ? pl(testsLeft, 'test') + ' left' : null].filter(Boolean).join(' · ') }) : null);
    const w = d.workload || {};
    if (w.fits === true && w.spare_h !== null && w.spare_h !== undefined) t1.append(h('p', { class: 'stat-sub', text: `fits with ${UI.num(w.spare_h)} h to spare` }));
    if (w.fits === false) {
      t1.append(h('p', { class: 'stat-sub ink', text: `short by ${UI.num(w.short_h)} h` }));
      if (w.suggest_minutes) {
        const set = btn(`Set ${w.suggest_minutes} min`, 'btn sm', e => { e.stopPropagation(); busy(set, () => patchPlan({ minutes: w.suggest_minutes }, `Days set to ${w.suggest_minutes} min`, undoOf({ minutes: 1 }))); });
        t1.append(set);
      }
    }
    if (!c.booked && d.state !== 'after') {
      const nb = h('a', { class: 'tag line', href: `/plan/?edit=${enc(a.id)}&step=2`, text: 'not booked' });
      nb.addEventListener('click', e => e.stopPropagation());
      t1.append(nb);
    }
    // 2 score
    const t2 = h('div', { class: 'stat' });
    const start = c.current, target = c.target;
    t2.append(h('span', { class: 'stat-k', text: 'Score' }),
      h('span', { class: 'pl-big' }, start === null || start === undefined ? '?' : String(start), h('small', { text: ' → ' }), String(target)));
    if (start === null || start === undefined) t2.append(h('p', { class: 'stat-sub', text: 'measured on day 1' }));
    else {
      const track = h('div', { class: 'pl-track', role: 'img', 'aria-label': `From ${start} to ${target} on a 200 to 800 scale` });
      const x = v => `${(Math.max(200, Math.min(800, v)) - 200) / 6}%`;
      track.append(h('b', { class: 'gap', style: `left: ${x(start)}; width: calc(${x(target)} - ${x(start)})` }));
      const mean = d.pace && d.pace.math && d.pace.math.mean;
      if (mean) track.append(h('b', { class: 'band', style: `left: ${x(mean - 35)}; width: calc(${x(mean + 35)} - ${x(mean - 35)})` }));
      track.append(h('i', { style: `left: ${x(start)}` }), h('i', { class: 't', style: `left: ${x(target)}` }));
      t2.append(track);
      const p = d.pace && d.pace.math;
      const chip = !p ? 'No test yet' : p.status === 'Ahead' ? `Ahead · +${p.delta}` : p.status === 'Behind' ? `Behind · ${Math.abs(p.delta)}` : p.status;
      t2.append(h('div', { class: 'row' }, h('span', { class: p && p.status !== 'Behind' ? 'tag or' : 'tag', text: chip }),
        h('span', { class: 'stat-sub', text: `+${target - start} to go` })));
      const v = d.verdict && d.verdict.math, proj = d.projection && d.projection.math;
      if (proj && proj.low) t2.append(h('p', { class: 'stat-sub', text: `At this pace: ${Math.round(proj.low / 10) * 10}–${Math.round(proj.high / 10) * 10} on ${D(c.exam_date)}` }));
      else if (!p) {
        const next = d.days.find(x => x.date >= t && x.kind === 'test');
        const nt = next && next.tasks.find(k => k.kind === 'test' && undone(k));
        if (nt) t2.append(btn('Take this week’s test now', 'quiet', e => busy(e.currentTarget, () => startTask(nt, next.date))));
      }
      if (v && v.needs_per_week) t2.append(h('p', { class: 'stat-sub', text: v.made_per_week !== null && v.made_per_week !== undefined
        ? `Making +${UI.num(v.made_per_week)} a week · needs +${UI.num(v.needs_per_week)}` : `Needs +${UI.num(v.needs_per_week)} a week` }));
    }
    const tot = d.score && d.score.rw && c.rw_current !== null && c.rw_current !== undefined && c.rw_target;
    if (tot) t2.append(h('p', { class: 'stat-sub', text: `R&W ${c.rw_current} → ${c.rw_target} · Total ${(start || 0) + c.rw_current} → ${target + c.rw_target}` }));
    if ((d.levers || []).length) {
      const lv = btn('What changes it ›', 'quiet', () => leversPop(lv));
      t2.append(lv);
    }
    // 3 plan done, against the schedule
    const pct = st.study_days_total ? Math.round(st.days_done / st.study_days_total * 100) : 0;
    const pastStudy = days.filter(x => x.date < t && STUDY.has(x.kind));
    const missed = pastStudy.filter(x => x.status === 'missed').length;
    const t3 = h('button', { type: 'button', class: 'stat', 'aria-label': `Plan ${pct}% done; show the calendar` });
    t3.addEventListener('click', () => R.cal && R.cal.scrollIntoView({ behavior: 'smooth', block: 'start' }));
    t3.append(h('span', { class: 'stat-k', text: 'Plan done' }), h('span', { class: 'pl-big', text: `${pct}%` }),
      h('p', { class: 'stat-sub', text: `${st.days_done} of ${pl(st.study_days_total, 'study day')}` }));
    UI.meter(t3, { label: '', value: st.days_done, max: st.study_days_total || 1, text: ' ', ink: true });
    if (pastStudy.length) t3.append(h('p', { class: 'stat-sub', text: missed ? `${missed} behind` : 'on schedule' }));
    // 4 this week
    const wk = st.week || {};
    const mon = monday(t);
    const t4 = h('button', { type: 'button', class: 'stat', 'aria-label': 'This week; show the week' });
    t4.addEventListener('click', () => { pick(t); R.week && R.week.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    t4.append(h('span', { class: 'stat-k', text: 'This week' }),
      h('span', { class: 'pl-big' }, UI.dur(wk.minutes_done || 0), wk.minutes_planned ? h('small', { text: ` of ${UI.dur(wk.minutes_planned)}` }) : null));
    if (wk.minutes_planned) UI.meter(t4, { label: '', value: wk.minutes_done || 0, max: wk.minutes_planned, text: ' ' });
    const dots = h('div', { class: 'pl-dots', role: 'img' });
    const said = [];
    for (let i = 0; i < 7; i++) {
      const date = addDays(mon, i), x = dayOf(date);
      if (!x || !STUDY.has(x.kind)) continue;
      const s = date > t ? 'future' : x.status;
      dots.append(h('span', { 'data-s': s, 'data-today': date === t ? '' : null }, h('i'), LETTER[i]));
      said.push(`${DOW[i]} ${STATUS[s] || (date === t ? 'today' : 'planned')}`);
    }
    dots.setAttribute('aria-label', said.join(', ') || 'No study days this week');
    if (said.length) t4.append(dots);
    if (st.longest) t4.append(h('p', { class: 'stat-sub', text: `Streak ${st.streak} · longest ${st.longest}` }));
    R.tiles.replaceChildren(t1, t2, t3, t4);
  }
  function leversPop(anchor) {
    UI.pop(anchor, (p, res) => {
      const box = h('div', { style: 'display: grid; gap: 8px; max-width: 360px' }, h('p', { class: 'k', text: 'What changes it' }));
      for (const lv of S.d.levers.slice(0, 3)) {
        const e = lv.effect || {};
        const say = [lv.label, e.fits === true && e.spare_h !== null ? `fits with ${UI.num(e.spare_h)} h to spare` : null,
          e.fits === false ? `short by ${UI.num(e.short_h)} h` : null, e.needs_per_week ? `needs +${UI.num(e.needs_per_week)} a week` : null].filter(Boolean).join(' · ');
        const b = btn(say, 'btn', async () => busy(b, async () => { await patchPlan(lv.patch, 'Plan updated', undoOf(lv.patch)); res.close(); }), { style: 'justify-content: flex-start; text-align: left; height: auto; padding: 10px 12px' });
        box.append(b);
      }
      return box;
    }, { label: 'What changes it' });
  }

  /* ---- banners (3c, L3, L6, L17) */
  const dismissed = () => ls.get('satf.plan.dismiss', {});
  function dismiss(key) { const m = dismissed(); m[key] = today(); ls.set('satf.plan.dismiss', m); drawBanners(); }
  function banner(key, text, actions = [], o = {}) {
    if (!o.keep && dismissed()[key]) return null;
    const b = h('div', { class: 'pl-banner', role: 'region', 'aria-label': o.label || 'Plan notice' }, h('p', {}, text));
    b.append(h('button', { type: 'button', class: 'x', 'aria-label': 'Dismiss', onclick: () => (o.onDismiss ? o.onDismiss() : dismiss(key)), html: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>' }));
    if (o.help) b.append(h('p', { class: 'help', text: o.help }));
    if (actions.length) b.append(h('div', { class: 'acts' }, actions));
    return b;
  }
  function drawBanners() {
    const d = S.d, c = cfg(), t = today(), out = [];
    if (S.readonly) { R.banners.replaceChildren(); return; }
    const built = ls.get('satf.plan.built', null);
    if (built && built.id === pid() && diff(built.day, t) < 3) {
      const chips = builtChips();
      out.push(banner(`built:${pid()}`, 'Built from your results', [chips], { label: 'Built from your results', onDismiss: () => { ls.set('satf.plan.built', null); drawBanners(); } }));
    }
    for (const b of d.banners || []) {
      if (b.kind === 'drift') {
        const s = b.suggest, n = (s.sessions || []).length;
        const key = `drift:${(s.sessions || []).join(',')}`;
        const notNow = btn(s.kind === 'target' ? `Keep ${c.target}` : 'Not now', 'quiet', e => busy(e.currentTarget, async () => {
          await api(`/plan/${enc(pid())}/drift`, { method: 'POST', body: { dismiss: s.sessions || [] } }); dismiss(key); }));
        if (s.kind === 'target') {
          const up = Math.min(800, Math.ceil((c.target + 50) / 10) * 10);
          out.push(banner(key, `Your last ${pl(n, 'test')} average ${s.current}, past your ${c.target} target.`,
            [btn(`Raise to ${up}`, 'pill sm', e => busy(e.currentTarget, () => patchPlan({ target: up }, `Target raised to ${up}`, { target: c.target }))), notNow]));
        } else out.push(banner(key, `Your last ${pl(n, 'test')} average ${s.current}. The plan starts from ${c.current}.`,
          [btn(`Start from ${s.current}`, 'pill sm', e => busy(e.currentTarget, () => patchPlan({ current: s.current }, `Starting score set to ${s.current}`, { current: c.current }))), notNow],
          { help: s.preview || null }));
      } else if (b.kind === 'registration') {
        const r = b.data || {}, by = r.register_by || r.deadline || null;
        const text = [`${D(b.date)} isn’t booked yet`, by ? `register by ${D(by)}` : null, by && diff(t, by) >= 0 ? pl(diff(t, by), 'day') + ' left' : null].filter(Boolean).join(' · ');
        out.push(banner(`reg:${b.date}`, text, [
          btn('I’ve registered', 'btn sm', e => busy(e.currentTarget, async () => { await api('/me', { method: 'PUT', body: { prefs: { registered: b.date } } }); await reload(); UI.toast('Marked as booked'); })),
          h('a', { class: 'quiet', href: CB, target: '_blank', rel: 'noopener', text: 'College Board ↗' })]));
      } else if (b.text) out.push(banner(`${b.kind}:${b.topic || ''}`, b.text, (b.actions || []).map(x => x.patch
        ? btn(x.label, x.primary ? 'pill sm' : 'btn sm', e => busy(e.currentTarget, () => patchPlan(x.patch, 'Plan updated', undoOf(x.patch)))) : null).filter(Boolean)));
    }
    const bh = d.behind;
    if (bh) {
      const miss = bh.planned - bh.done;
      const acts = [btn('Catch up · 15 min', 'pill sm', e => busy(e.currentTarget, () => catchUp()))];
      for (const f of bh.fixes || []) acts.push(btn(f.label, 'btn sm', e => busy(e.currentTarget, () => patchPlan(f.patch, 'Plan updated', undoOf(f.patch)))));
      out.push(banner(`behind:${t}`, `${miss} of ${pl(bh.planned, 'study day')} missed in the last 7 · you average ${bh.avg_minutes} min on a study day; the plan asks ${c.minutes}.`, acts));
    }
    // the last study day, missed
    const last = [...d.days].reverse().find(x => x.date < t && STUDY.has(x.kind));
    if (last && last.status === 'missed' && diff(last.date, t) <= 3) {
      const task = last.tasks.find(k => k.counted && questionTask(k) && undone(k));
      const what = task ? `${task.title}${task.topics && task.topics.length ? ` on ${task.topics.map(tn).join(', ')}` : ''}` : KIND[last.kind];
      const acts = task ? [btn('Do it now', 'btn sm', e => busy(e.currentTarget, () => startTask(task, last.date)))] : [];
      out.push(banner(`missed:${last.date}`, `Missed ${D(last.date, 'long')} · ${what}`, acts,
        { help: d.stats.streak ? `Make it up to keep your ${d.stats.streak}-day streak.` : null }));
    }
    R.banners.replaceChildren(...out.filter(Boolean));
  }
  function builtChips() {
    const c = cfg(), box = h('div', { class: 'chips' });
    const days = c.days.split('').map((x, i) => x === '1' ? DOW[i] : null).filter(Boolean).join(', ');
    const focus = Object.entries(c.focus || {}).filter(([, v]) => (v.state || v) === 'focus').map(([k]) => k);
    const chip = (text, edit) => { const b = h('button', { type: 'button', text: `${text} ✎` }); b.addEventListener('click', () => edit(b)); box.append(b); };
    if (c.current !== null && c.current !== undefined) chip(`Start ${c.current}`, b => numberPop(b, 'Starting score', c.current, v => patchPlan({ current: v }, `Start ${v}`, { current: c.current })));
    chip(`Target ${c.target}`, b => numberPop(b, 'Target', c.target, v => patchPlan({ target: v }, `Target ${v}`, { target: c.target })));
    chip(`${D(c.exam_date)}${c.booked ? '' : ' · not booked'}`, b => UI.examDate(b, { value: c.exam_date, dates: UI.SAT_DATES, onSave: v => v && patchPlan({ exam_date: v }, `SAT on ${D(v)}`, { exam_date: c.exam_date }) }));
    chip(`${c.minutes} min × ${days}`, b => UI.pop(b, (p, res) => {
      const box2 = h('div', { style: 'display: grid; gap: 10px' }, h('p', { class: 'label', text: 'A study day' }));
      UI.chips(box2, [15, 30, 45, 60, 90, 120].map(v => ({ value: v, label: UI.dur(v) })), { value: c.minutes, label: 'Minutes a study day',
        onChange: async v => { res.close(); await patchPlan({ minutes: v }, `Days set to ${v} min`, { minutes: c.minutes }); } });
      return box2;
    }, { label: 'Minutes a study day' }));
    chip(testsLabel(c).replace(/^./, x => x.toUpperCase()), b => UI.pop(b, (p, res) => {
      const box2 = h('div', { style: 'display: grid; gap: 10px' }, h('p', { class: 'label', text: 'Practice tests' }));
      UI.seg(box2, [['none', 'None'], ['weekly', 'Weekly'], ['twice', 'Twice a week'], ['daily', 'Every study day']].map(([value, label]) => ({ value, label })),
        { value: c.tests, label: 'Practice tests', onChange: async v => { res.close(); await patchPlan({ tests: v }, 'Tests changed', { tests: c.tests }); } });
      return box2;
    }, { label: 'Practice tests' }));
    if (focus.length) chip(`Focus ${focus.join(', ')}`, () => go({ edit: pid(), step: 4 }));
    return box;
  }
  function numberPop(anchor, label, value, save) {
    UI.pop(anchor, (p, res) => {
      const f = h('input', { type: 'number', class: 'field sm', min: '200', max: '800', step: '10', value: String(value), 'aria-label': label });
      const err = h('p', { class: 'field-err', hidden: true, text: 'A score from 200 to 800 in tens.' });
      const ok = btn('Save', 'pill sm', async () => {
        const v = Math.round(+f.value / 10) * 10;
        if (!(v >= 200 && v <= 800)) { err.hidden = false; return; }
        res.close();
        try { await save(v); } catch (e) { UI.toast(e.message || 'Couldn’t save. Try again.'); }
      });
      f.addEventListener('keydown', e => { if (e.key === 'Enter') ok.click(); });
      return h('div', { style: 'display: grid; gap: 8px' }, h('label', { class: 'label', text: label }), f, err, ok);
    }, { label });
  }
  async function catchUp() {
    const t = today(), next = S.d.days.find(x => x.date >= t && STUDY.has(x.kind));
    const topics = next ? [...new Set(next.tasks.flatMap(k => k.topics || []))].slice(0, 3) : [];
    const r = await api('/drill', { method: 'POST', body: { count: 9, source: 'plan', task: `${t}:extra`, ...(topics.length ? { topics } : {}) } });
    location.href = `/practice/session/?id=${enc(r.id)}`;
  }

  /* ---- the Plan tab (3e-3i) */
  function drawPlanTab() {
    R.log = changeLog();
    R.day = h('section', { class: 'card', 'aria-label': 'The day' });
    R.week = h('section', { class: 'card', 'aria-label': 'The week' });
    R.up = h('section', { class: 'card', 'aria-label': 'Coming up' });
    R.side = h('aside', { class: 'pl-stack' }, R.up);
    const map = mapTile();
    if (map) R.side.append(map);
    R.phase = h('section', { class: 'card pl-sec', 'aria-label': 'Phases' });
    R.cal = h('section', { class: 'card pl-sec', 'aria-label': 'Calendar' });
    R.pPlan.replaceChildren(R.log || '', h('div', { class: 'pl-cols' }, h('div', { class: 'pl-stack' }, R.day, R.week), R.side), R.phase, R.cal);
    drawDay(); drawWeek(); drawUp(); drawPhase(); drawCal();
  }
  function changeLog() {
    const ch = S.d.changes;
    if (!ch || !(ch.today || []).length) return null;
    const t = today();
    const since = ch.since && diff(ch.since, t) > 1 ? `Since ${DOW[dow(ch.since)]}` : 'Since this morning';
    // the same change said twice is one line with a count (decision 7)
    const lines = [];
    for (const x of ch.today) {
      const text = pretty(x.text), last = lines[lines.length - 1];
      if (last && last.text === text && last.day === x.day) last.n++; else lines.push({ text, day: x.day, n: 1 });
    }
    return h('div', { class: 'pl-log', 'aria-label': 'What changed' }, h('p', { class: 'k', text: `${since} · ${pl(ch.today.length, 'change')}` }),
      lines.map(x => h('button', { type: 'button', onclick: () => x.day && pick(x.day) }, x.text, x.n > 1 ? ` ×${x.n}` : '',
        x.day && !x.text.includes(DOW[dow(x.day)]) ? h('span', { class: 'soft meta', text: dayName(x.day) }) : null)));
  }
  function pick(date) {
    if (!dayOf(date)) return;
    S.sel = date; S.trim = null; S.kb = -1; S.open = null;
    url(paramsNow());
    drawDay(); drawWeek(); drawThumb();
    if (R.calApi) R.calApi.select(date);
  }

  // the day's tasks in the order they run, then the extras
  const ordered = day => [...day.tasks.filter(t => t.counted), ...day.tasks.filter(t => !t.counted)];
  function nextOf(day) { return day ? ordered(day).find(t => t.counted && questionTask(t) && undone(t)) || null : null; }

  function drawDay() {
    const day = dayOf(S.sel), c = cfg(), t = today();
    const card = R.day;
    // a redraw keeps the keyboard where it was: the same button in the same row, else the
    // row, else the chosen chip, else the day itself
    const a = doc.activeElement, had = a && card.contains(a) && a !== card;
    const was = had ? { task: a.closest('[data-task]') && a.closest('[data-task]').dataset.task, text: a.textContent } : null;
    card.replaceChildren();
    if (!day) return;
    if (was) queueMicrotask(() => {
      const row = was.task && card.querySelector(`[data-task="${CSS.escape(was.task)}"]`);
      const pool = [...(row || card).querySelectorAll('button, a, input')];
      const el = pool.find(x => x.textContent === was.text) || (row && (row.querySelector('.trow-act button') || row))
        || card.querySelector('[aria-checked="true"]') || card;
      if (el === card) card.tabIndex = -1;
      if (!card.contains(doc.activeElement) || doc.activeElement === doc.body) el.focus({ preventScroll: true });
    });
    const isToday = day.date === t, past = day.date < t, future = day.date > t;
    const study = STUDY.has(day.kind);
    const head = h('div', { class: 'pl-dayhead' });
    const k = h('p', { class: 'k', text: isToday ? `Today · ${D(day.date, 'eyebrow')}` : D(day.date, 'eyebrow') });
    const tags = h('div', { class: 'row' }, h('span', { class: day.kind === 'exam' ? 'tag or' : 'tag', text: KIND[day.kind] || day.kind }),
      day.phase && study ? h('span', { class: 'tag', text: day.phase }) : null,
      past && STATUS[day.status] ? h('span', { class: 'tag line', text: STATUS[day.status] }) : null,
      day.overridden ? h('span', { class: 'meta', text: 'changed' }) : null);
    const right = h('div', { class: 'row' });
    if (day.minutes) right.append(h('span', { class: 'meta', text: `${day.minutes} min planned` }));
    if (!past && !S.readonly && day.kind !== 'exam' && day.kind !== 'after') {
      const m = h('button', { type: 'button', class: 'btn sm', 'aria-haspopup': 'menu', text: 'Day ⋯' });
      m.addEventListener('click', () => UI.menu(m, dayMenu(day), { label: 'Day' }));
      right.append(m);
    }
    head.append(h('div', { class: 'row spread' }, h('div', { style: 'display: grid; gap: 8px' }, k, tags), right));
    if (c.place && study) head.append(h('p', { class: 'meta', text: `${c.time || ''}${c.time ? ' · ' : ''}${c.place}` }));
    card.append(head);
    R.start = null;
    const counted = day.tasks.filter(x => x.counted);
    // Start today (L8) and Today I have (L9)
    if (!S.readonly && !past && (study || day.kind === 'rest')) {
      const go2 = h('div', { class: 'pl-day-go' });
      const next = nextOf(day);
      if (isToday && next) {
        const left = counted.filter(x => questionTask(x) && undone(x));
        const mid = day.tasks.some(x => x.status === 'active') || counted.some(x => DONE.has(x.status));
        const label = mid ? `Resume today · task ${counted.indexOf(next) + 1} of ${counted.length}` : `Start today · ${pl(left.length, 'task')} · ${Math.round(left.reduce((s, x) => s + (x.minutes || 0), 0))} min`;
        R.start = btn(label, 'pill', e => busy(e.currentTarget, () => startTask(next, day.date).catch(err => { UI.toast(err.rowText || 'Couldn’t start. Try again.'); })), { 'aria-keyshortcuts': 'Shift+Enter' });
        go2.append(R.start);
      }
      if (go2.childNodes.length) card.append(go2);
      card.append(haveChips(day));
      if (S.trim && S.trim.date === day.date) card.append(trimBox(day));
    }
    // progress on the day
    if (counted.length && (isToday || past)) {
      const done = counted.filter(x => DONE.has(x.status)).length;
      const mBox = h('div', { class: 'pl-meter' });
      const leftMin = Math.max(0, Math.round((day.minutes || 0) - (day.minutes_done || 0)));
      UI.meter(mBox, { label: `${done} of ${pl(counted.length, 'task')}`, value: Math.round(day.minutes_done || 0), max: day.minutes || 1,
        text: `${Math.round(day.minutes_done || 0)} of ${day.minutes} min${leftMin && !past ? ` · ${leftMin} min left` : ''}` });
      if (day.questions) mBox.append(h('p', { class: 'meta', style: 'margin-top: 6px', text: `${pl(day.questions, 'question')} · ${day.right} right` }));
      card.append(mBox);
    }
    // the rows
    const list = h('div', { class: 'trows', role: 'list', 'aria-label': 'Tasks' });
    const primary = isToday ? nextOf(day) : null;
    let seenOwn = false;
    ordered(day).forEach((task, i) => {
      const row = UI.taskRow(list, task, {
        primary: primary && task.id === primary.id, future, past, readonly: S.readonly,
        open: S.open && S.open.id === task.id ? S.open.kind : null,
        on: (a, tk, arg) => onTask(a, tk, arg, day.date), menu: tk => taskMenu(tk, day),
      });
      row.el.dataset.task = task.id;
      row.el.setAttribute('role', 'listitem');
      row.el.tabIndex = -1;
      if (i === S.kb) row.el.dataset.kb = '';
      if (task.kind === 'custom' && !seenOwn && String(task.id).startsWith('pt:')) {
        seenOwn = true;
        if (!DONE.has(task.status)) row.el.querySelector('.trow-main').append(h('p', { class: 'help', text: 'Do this one on your own, then tick it.' }));
      }
    });
    if (day.tasks.length) card.append(list);
    card.append(dayFoot(day));
  }
  function haveChips(day) {
    const box = h('div', { class: 'pl-have' });
    const rest = !STUDY.has(day.kind);
    box.append(h('span', { class: 'k', text: rest ? 'Practice anyway' : 'Today I have' }));
    const opts = [10, 15, 30, 45, 60, 90];
    const cur = rest ? null : (S.trim && S.trim.date === day.date ? S.trim.m : day.minutes);
    if (!rest && !opts.includes(day.minutes) && day.minutes) opts.push(day.minutes), opts.sort((a, b) => a - b);
    UI.chips(box, opts.map(v => ({ value: v, label: `${v}` })), { value: cur, label: rest ? 'Practice anyway, minutes' : 'Today I have, minutes',
      onChange: v => rest ? practiceAnyway(v) : chooseTrim(day, v) });
    box.append(h('span', { class: 'meta', text: 'min' }));
    return box;
  }
  async function practiceAnyway(m) {
    const t = today(), next = S.d.days.find(x => x.date > t && STUDY.has(x.kind));
    const topics = next ? [...new Set(next.tasks.flatMap(k => k.topics || []))].slice(0, 3) : [];
    try {
      const r = await api('/drill', { method: 'POST', body: { count: Math.max(3, Math.floor(m * 60 / 95)), source: 'plan', ...(topics.length ? { topics } : {}) } });
      location.href = `/practice/session/?id=${enc(r.id)}`;
    } catch (_) { UI.toast('Couldn’t start. Try again.'); }
  }
  async function chooseTrim(day, m) {
    if (m === day.minutes) { S.trim = null; drawDay(); return; }
    S.trim = { date: day.date, m, loading: true };
    drawDay();
    try {
      const p = await api(`/plan/day/${day.date}?minutes=${m}`);
      if (!S.trim || S.trim.m !== m) return;
      S.trim = { date: day.date, m, preview: p };
    } catch (_) { S.trim = { date: day.date, m, error: true }; }
    drawDay();
  }
  function trimBox(day) {
    const tr = S.trim, box = h('div', { class: 'pl-trim', role: 'status' });
    if (tr.loading) { box.append(h('p', { class: 'soft', text: 'Working out what fits…' })); return box; }
    if (tr.error) { box.append(h('p', { text: 'Couldn’t work that out. Try again.' })); return box; }
    const p = tr.preview, kept = (p.tasks || []).filter(x => x.counted);
    const short = x => ({ recheck: 'Warm-up', fix: 'Fix', focus: 'Focus', map: 'Map', words: 'Words', test: 'Test', learn: 'Learn it', check: 'Check', pace: 'Pace', habit: 'Habit', sweep: 'Sweep' }[x.kind] || x.title);
    const fits = kept.map(x => `${short(x)} ${x.kind === 'words' ? Math.round(x.minutes) : x.count || Math.round(x.minutes)}`);
    const total = kept.reduce((s, x) => s + (x.minutes || 0), 0);
    const cut = (p.budget && p.budget.cut) || p.cut || [];
    const later = cut.map(x => {
      const what = { fix: 'Fix', focus: 'Focus', recheck: 'Warm-up', check: 'Check', learn: 'Learn it', test: 'Test', habit: 'Habit', pace: 'Pace', sweep: 'Sweep', words: 'Words' }[x.kind] || x.kind;
      return `${what}${x.count ? ` ${x.count} q` : ''}${x.to ? ` → ${DOW[dow(x.to)]}` : ''}${x.kind === 'focus' ? ' (its topics come back sooner)' : ''}`;
    });
    box.append(h('p', {}, h('b', { text: 'Fits: ' }), `${fits.join(' · ') || 'nothing counted'} · ${Math.round(total * 10) / 10} min`));
    if (later.length) box.append(h('p', { class: 'soft', text: `Left for later: ${later.join(' · ')}` }));
    const test = cut.find(x => x.kind === 'test');
    if (test && test.to) box.append(h('p', { text: `Module test moves to ${DOW[dow(test.to)]} · it needs 35 min` }));
    const apply = btn('Apply', 'btn sm ink', e => busy(e.currentTarget, async () => {
      const before = day.overridden ? { minutes: day.minutes } : null;
      await dayPut(day.date, { minutes: tr.m, trim: true }, `Today set to ${tr.m} min`, before);
      S.trim = null;
    }), { 'aria-keyshortcuts': 'Enter' });
    box.append(h('div', { class: 'row' }, apply, btn('Cancel', 'quiet', () => { S.trim = null; drawDay(); })));
    return box;
  }
  function dayFoot(day) {
    const t = today(), counted = day.tasks.filter(x => x.counted), foot = h('div');
    const nextStudy = S.d.days.find(x => x.date > day.date && STUDY.has(x.kind));
    if (day.kind === 'rest') foot.append(h('div', { class: 'pl-rest' }, h('p', { text: `Rest day${nextStudy ? ` · next study day ${D(nextStudy.date, 'long')}` : ''}` })));
    else if (day.kind === 'off') {
      const f = h('div', { class: 'pl-rest' }, h('p', { text: 'Day off' }));
      if (day.overridden && day.date >= t && !S.readonly) f.append(btn('Undo day off', 'btn sm', e => busy(e.currentTarget, () => dayPut(day.date, { off: false }, 'Day off undone'))));
      foot.append(f);
    } else if (day.kind === 'eve' || day.kind === 'exam') {
      foot.append(h('div', { class: 'pl-rest' }, h('p', { text: day.kind === 'eve' ? 'Rest before the SAT' : 'SAT today · good luck' }), checklist()));
    } else if (day.kind === 'after' || (S.d.state === 'after' && day.date >= cfg().exam_date)) foot.append(resultPanel());
    else if (counted.length && counted.every(x => DONE.has(x.status))) {
      const f = h('div', { class: 'pl-foot' }, h('p', { text: 'Day done ✓' }));
      if (day.date === t && !S.readonly) {
        const topics = [...new Set(day.tasks.flatMap(k => k.topics || []))].slice(0, 3);
        f.append(btn('Keep going · 10 more', 'quiet', e => busy(e.currentTarget, async () => {
          const r = await api('/drill', { method: 'POST', body: { count: 10, source: 'plan', task: `${t}:extra`, ...(topics.length ? { topics } : {}) } });
          location.href = `/practice/session/?id=${enc(r.id)}`;
        })));
        const tn2 = nextStudy && nextStudy.tasks.find(k => k.kind === 'focus' && undone(k));
        if (tn2) f.append(btn('Start tomorrow’s focus set', 'quiet', e => busy(e.currentTarget, () => startTask(tn2, nextStudy.date))));
      }
      foot.append(f);
    } else if (counted.length && counted.every(x => x.status === 'skipped' || x.status === 'moved') && day.date >= t) {
      const moved = counted.filter(x => x.status === 'moved');
      const f = h('div', { class: 'pl-foot' }, h('p', { text: `Nothing left today${moved.length ? ` · ${moved.length} moved to ${DOW[dow(moved[0].moved_to || nextStudy.date)]}` : ''}` }));
      const ahead = nextStudy && nextOf(nextStudy);
      if (ahead && !S.readonly) f.append(btn('Work ahead', 'btn sm', e => busy(e.currentTarget, () => startTask(ahead, nextStudy.date))));
      foot.append(f);
    }
    return foot;
  }
  function checklist() {
    const items = ['Bluebook installed and updated', 'Admission ticket', 'Photo ID', 'Device charged, and a charger', 'Pencils for scratch paper', 'Calculator (optional; Desmos is in Bluebook)'];
    const saved = ls.get('satf.plan.checklist', {});
    return h('div', { class: 'pl-check', role: 'group', 'aria-label': 'What to bring' }, items.map((x, i) => {
      const box = h('input', { type: 'checkbox', checked: saved[i] || null });
      box.addEventListener('change', () => { const m = ls.get('satf.plan.checklist', {}); m[i] = box.checked; ls.set('satf.plan.checklist', m); });
      return h('label', { class: 'check' }, box, x);
    }));
  }
  function resultPanel() {
    const a = S.d.active, res = a.result;
    const box = h('div', { class: 'pl-rest' });
    if (res && res.math) {
      const st = S.d.stats;
      box.append(h('p', { text: `Days done ${st.days_done} of ${st.study_days_total} · ${UI.dur(st.minutes_done)} · ${UI.num(st.questions)} questions · ${st.mistakes_closed} mistakes fixed · Target ${a.cfg.target} · got ${res.math}` }),
        btn('Plan the next one', 'pill sm', () => duplicate(a.id)));
      return box;
    }
    const math = h('input', { type: 'number', class: 'field sm', min: '200', max: '800', step: '10', 'aria-label': 'Math score', placeholder: 'Math', style: 'width: 110px' });
    const rw = h('input', { type: 'number', class: 'field sm', min: '200', max: '800', step: '10', 'aria-label': 'Reading and Writing score (optional)', placeholder: 'R&W', style: 'width: 110px' });
    const err = h('p', { class: 'field-err', hidden: true });
    const save = btn('Save', 'pill sm', e => busy(e.currentTarget, async () => {
      const m = Math.round(+math.value / 10) * 10, r = rw.value ? Math.round(+rw.value / 10) * 10 : null;
      if (!(m >= 200 && m <= 800) || (r !== null && !(r >= 200 && r <= 800))) { err.textContent = 'Scores run from 200 to 800.'; err.hidden = false; return; }
      await api(`/plan/${enc(a.id)}/result`, { method: 'POST', body: r ? { math: m, rw: r } : { math: m } });
      await reload();
    }));
    box.append(h('p', { text: 'How did it go?' }), h('div', { class: 'row' }, math, rw, save), err, h('p', { class: 'help', text: 'Enter it when your scores are out.' }));
    return box;
  }

  /* ---- task actions (L8, L10, 3f) */
  async function startTask(t, date) {
    if (navigator.onLine === false) throw rowErr('Starting needs a connection.');
    if (t.status === 'active' && t.session) {
      location.href = t.kind === 'test' ? `/test/?s=${enc(t.session)}` : `/practice/session/?id=${enc(t.session)}`;
      return;
    }
    if (!t.start) throw rowErr('This one is done on your own.');
    const body = { ...(t.start.body || {}) };
    if (date === today()) body.run = today();
    if (t.kind === 'words') {
      const p = new URLSearchParams({ today: '1', task: t.id });
      if (body.run) p.set('run', body.run);
      if (body.box) p.set('box', body.box);
      location.href = `/words/run/?${p}`;
      return;
    }
    const path = String(t.start.path || '/api/drill').replace(/^\/api(?=\/)/, '');
    let r;
    try { r = await api(path, { method: 'POST', body }); }
    catch (e) { throw rowErr(e.status === 409 && e.message ? e.message : 'Couldn’t start. Try again.'); }
    location.href = t.kind === 'test' ? `/test/?s=${enc(r.id)}` : r.href || `/practice/session/?id=${enc(r.id)}`;
  }
  function applyDays(days) {
    for (const x of days || []) {
      const i = S.d.days.findIndex(y => y.date === x.date);
      if (i >= 0) S.d.days[i] = x;
      if (S.d.today && S.d.today.date === x.date) S.d.today = x;
    }
  }
  const taskPath = t => `/plan/${enc(pid())}/tasks/${enc(t.id)}`;
  async function patchTask(t, body, toast, undoBody, fail) {
    let r;
    try { r = await api(taskPath(t), { method: 'PATCH', body }); }
    catch (e) { throw rowErr(fail || (e.status === 422 || e.status === 409 ? e.message : 'Couldn’t save that. Try again.')); }
    applyDays(r.days);
    drawDay(); drawWeek();
    if (toast) UI.toast(toast, undoBody ? { undo: async () => { const r2 = await api(taskPath(t), { method: 'PATCH', body: undoBody }); applyDays(r2.days); S.open = null; drawDay(); drawWeek(); reload(); } } : {});
    reload();
    return r;
  }
  async function onTask(action, t, arg, date) {
    S.kb = -1;
    switch (action) {
      case 'start': return startTask(t, date);
      case 'review': location.href = t.kind === 'test' ? `/results/report/?id=${enc(t.session)}` : `/practice/session/?id=${enc(t.session)}`; return;
      case 'tick': {
        const r = await patchTask(t, { day: date, status: arg.done ? 'done' : 'todo' }, arg.done ? 'Marked done' : null, arg.done ? { day: date, status: 'todo' } : null);
        if (r && r.next === 'score_sheet') scoreSheet(t, date);
        return;
      }
      case 'skip': S.open = { id: t.id, kind: 'skip' }; return patchTask(t, { day: date, status: 'skipped' }, 'Skipped', { day: date, status: 'todo' });
      case 'reason': {
        S.open = null;
        if (arg.reason === 'know') {
          const r = await api(taskPath(t), { method: 'PATCH', body: { day: date, status: 'skipped', reason: 'know' } }).catch(e => { throw rowErr(e.message || 'Couldn’t start the test-out. Try again.'); });
          if (r.test_out) {
            const s = await api('/drill', { method: 'POST', body: { ...r.test_out, source: 'plan' } });
            location.href = `/practice/session/?id=${enc(s.id)}`;
          }
          return;
        }
        const r = await patchTask(t, { day: date, status: 'skipped', reason: arg.reason }, null, null);
        const moved = r.days && r.days.length > 1 ? r.days[1].date : null;
        UI.toast(arg.reason === 'no_time' && moved ? `Moved to ${D(moved, 'long')}` : 'A Learn it task comes before its next focus set',
          { undo: async () => { const r2 = await api(taskPath(t), { method: 'PATCH', body: { day: date, status: 'todo' } }); applyDays(r2.days); drawDay(); drawWeek(); reload(); } });
        return;
      }
      case 'done': S.open = null; return patchTask(t, { day: date, status: 'done', minutes: arg.minutes, ...(arg.where ? { where: arg.where } : {}) }, 'Marked done', { day: date, status: 'todo' });
      case 'undo': S.open = null; return patchTask(t, { day: date, status: 'todo' }, null, null);
      case 'again': {
        const x = today(), task = `${x}:extra`;
        const body = arg.kind === 'misses' ? { rematch: t.session, scope: 'misses', task, source: 'plan' }
          : { ...(t.topics && t.topics.length ? { topics: t.topics } : { pool: 'redo' }), count: 10, source: 'plan', task, ...(arg.kind === 'harder' ? { tiers: ['hard'] } : {}) };
        let r;
        try { r = await api('/drill', { method: 'POST', body }); } catch (e) { throw rowErr(e.status === 409 && e.message ? e.message : 'Couldn’t start. Try again.'); }
        location.href = `/practice/session/?id=${enc(r.id)}`;
        return;
      }
    }
  }
  function studyAfter(date, n = 7) {
    const exam = cfg().exam_date, out = [];
    for (const x of S.d.days) {
      if (x.date <= date || x.date >= addDays(exam, -1) || !STUDY.has(x.kind)) continue;
      out.push(x);
      if (out.length >= n) break;
    }
    return out;
  }
  function taskMenu(t, day) {
    if (S.readonly || day.date < today()) return [];
    const items = [];
    const own = String(t.id).startsWith('pt:');
    if (!own && t.counted && t.kind !== 'custom' && undone(t)) {
      items.push({ label: 'Move to…', onClick: () => setTimeout(() => moveMenu(t, day), 0) });
    }
    if (t.kind === 'focus' && (t.alternatives || []).length) items.push({ label: 'Swap topics', sub: t.alternatives[0].map ? t.alternatives[0].map(tn).join(', ') : null,
      onClick: () => patchTask(t, { day: day.date, swap: t.alternatives[0] }, 'Topics swapped').catch(e => UI.toast(e.rowText)) });
    if (t.kind === 'test' && undone(t)) {
      const section = /Section/.test(t.title) || (t.start && t.start.body && t.start.body.full);
      if (section) items.push({ label: 'Make it a module', onClick: () => dayPut(day.date, { test: 'module' }, 'Now a module') });
      else if (day.minutes >= 70) items.push({ label: 'Make it a section', onClick: () => dayPut(day.date, { test: 'section' }, 'Now a section') });
    }
    if (own) {
      items.push({ label: 'Edit', onClick: () => ownForm(day, t) });
      items.push({ label: 'Remove', onClick: async () => {
        try { const r = await api(`/plan/${enc(pid())}/tasks/${enc(t.id)}`, { method: 'DELETE' }); applyDays(r.days); drawDay(); UI.toast('Task removed'); reload(); }
        catch (_) { UI.toast('Couldn’t remove it. Try again.'); }
      } });
    }
    return items;
  }
  function moveMenu(t, day) {
    const trigger = R.day.querySelector(`[data-task="${CSS.escape(t.id)}"] .trow-more`) || R.day;
    const opts = studyAfter(day.date).map(x => ({
      label: D(x.date, 'long'), meta: `${x.minutes} → ${Math.round(x.minutes + (t.minutes || 0))}m`,
      disabled: t.kind === 'test' && x.minutes < 35, sub: t.kind === 'test' && x.minutes < 35 ? 'a test needs 35 min' : null,
      onClick: () => doMove(t, day, x.date),
    }));
    opts.push({ separator: true }, { label: 'Another date…', onClick: () => setTimeout(() => UI.pop(trigger, (p, res) => {
      const f = h('input', { type: 'date', class: 'field sm', min: addDays(day.date, 1), max: addDays(cfg().exam_date, -2), 'aria-label': 'Move to' });
      const ok = btn('Move', 'pill sm', async () => { if (!f.value) return; res.close(); doMove(t, day, f.value); });
      return h('div', { style: 'display: grid; gap: 8px' }, h('label', { class: 'label', text: 'Move to' }), f, ok);
    }, { label: 'Move to a date' }), 0) });
    UI.menu(trigger, opts, { label: `Move ${t.title}` });
  }
  function doMove(t, day, to) {
    return patchTask(t, { day: day.date, to }, `Moved to ${D(to, 'long')}`, { day: day.date, status: 'todo' }, 'Couldn’t move. Try again.')
      .catch(e => { const row = R.day.querySelector(`[data-task="${CSS.escape(t.id)}"] .trow-err`); if (row) row.textContent = e.rowText || 'Couldn’t move. Try again.'; });
  }
  async function dayPut(date, body, toast, undoBody) {
    const path = `/plan/${enc(pid())}/day/${date}`;
    try {
      const r = await api(path, { method: 'PUT', body });
      applyDays(r.days);
      drawDay(); drawWeek();
      if (toast) UI.toast(toast, { undo: async () => {
        const r2 = undoBody ? await api(path, { method: 'PUT', body: undoBody }) : await api(path, { method: 'DELETE' });
        applyDays(r2.days); drawDay(); drawWeek(); reload();
      } });
      reload();
    } catch (e) { UI.toast(e.status === 422 ? e.message : 'Couldn’t change the day. Try again.'); }
  }
  function dayMenu(day) {
    const items = [];
    const study = STUDY.has(day.kind);
    if (study) items.push({ label: day.date === today() ? 'Change today’s time…' : 'Change this day’s time…', onClick: () => setTimeout(() => {
      const anchor = R.day.querySelector('[aria-haspopup="menu"]') || R.day;
      UI.pop(anchor, (p, res) => {
        const box = h('div', { style: 'display: grid; gap: 10px' }, h('p', { class: 'label', text: 'Minutes this day' }));
        UI.chips(box, [15, 30, 45, 60, 90, 120, 150, 180].map(v => ({ value: v, label: UI.dur(v) })), { value: day.minutes, label: 'Minutes this day',
          onChange: v => { res.close(); dayPut(day.date, { minutes: v }, `${D(day.date)} set to ${v} min`, day.overridden ? { minutes: day.minutes } : null); } });
        return box;
      }, { label: 'Minutes this day' });
    }, 0) });
    if (study) items.push({ label: 'Take the day off', sub: 'its focus topics move to the next practice day', onClick: () => dayPut(day.date, { off: true }, 'Day off', { off: false }) });
    if (day.kind === 'off' && day.overridden) items.push({ label: 'Undo day off', onClick: () => dayPut(day.date, { off: false }, 'Day off undone', { off: true }) });
    if (day.date <= addDays(cfg().exam_date, -2)) items.push({ label: 'Add a task', onClick: () => setTimeout(() => ownForm(day), 0) });
    if (day.overridden) items.push({ label: 'Reset this day', onClick: async () => {
      try { const r = await api(`/plan/${enc(pid())}/day/${day.date}`, { method: 'DELETE' }); applyDays(r.days); drawDay(); drawWeek(); UI.toast('Day reset'); reload(); }
      catch (_) { UI.toast('Couldn’t reset the day. Try again.'); }
    } });
    return items;
  }
  function ownForm(day, task) {
    const title = h('input', { class: 'field sm', maxlength: '60', value: task ? task.title : '', 'aria-label': 'Title', placeholder: 'What you’ll do' });
    const minutes = h('input', { type: 'number', class: 'field sm', min: '5', max: '240', value: String(task ? task.minutes : 30), 'aria-label': 'Minutes' });
    let repeat = task ? (task.repeat || 'once') : 'once';
    const rep = h('div');
    if (!task) UI.seg(rep, [{ value: 'once', label: `Once · ${D(day.date)}` }, { value: 'study_days', label: 'Every study day' }, { value: `weekly:${dow(day.date)}`, label: `Weekly on ${DOW[dow(day.date)]}` }],
      { value: 'once', label: 'Repeat', onChange: v => { repeat = v; } });
    const quick = h('div', { class: 'chips' }, !task && [
      ['+ Official Bluebook practice test · once', { type: 'bluebook', title: 'Official Bluebook practice test', minutes: 134 }],
      ['+ Tutor session', { type: 'tutor', title: 'Tutor session', minutes: 60 }],
    ].map(([label, v]) => btn(label, '', () => { title.value = v.title; minutes.value = String(v.minutes); quick.dataset.type = v.type; })));
    const err = h('p', { class: 'field-err', hidden: true });
    UI.sheet({
      title: task ? 'Edit your task' : 'Add a task',
      body: h('div', { style: 'display: grid; gap: 12px' }, quick, h('label', { class: 'label', text: 'Title' }), title, h('label', { class: 'label', text: 'Minutes' }), minutes, rep, err),
      actions: [{ label: task ? 'Save' : 'Add task', primary: true, onClick: async s => {
        const m = Math.round(+minutes.value);
        if (!title.value.trim() || !(m >= 5 && m <= 240)) { err.textContent = 'A title, and 5 to 240 minutes.'; err.hidden = false; return false; }
        s.busy(true);
        try {
          if (task) {
            const r = await api(taskPath(task), { method: 'PATCH', body: { title: title.value.trim(), minutes: m } });
            applyDays(r.days); UI.toast('Task updated');
          } else {
            const body = { title: title.value.trim(), minutes: m, ...(repeat === 'once' ? { day: day.date } : { repeat }), ...(quick.dataset.type ? { type: quick.dataset.type } : {}) };
            const r = await api(`/plan/${enc(pid())}/tasks`, { method: 'POST', body });
            applyDays(r.days); UI.toast('Task added');
          }
          drawDay(); drawWeek(); reload();
        } catch (e) { s.busy(false); err.textContent = e.message || 'Couldn’t save the task. Try again.'; err.hidden = false; return false; }
      } }, { label: 'Cancel', quiet: true }],
    });
    setTimeout(() => title.focus(), 50);
  }
  // Ticking a Bluebook test: its scores feed the plan (L11). The Math and R&W scores go
  // to /api/scores (S3's add_outside_score); the R&W misses by domain to the plan's rwlog.
  function scoreSheet(t, date) {
    const f = (label) => h('input', { type: 'number', class: 'field sm', min: '200', max: '800', step: '10', 'aria-label': label, placeholder: label });
    const math = f('Math'), rw = f('Reading & Writing');
    const doms = ['Information and Ideas', 'Craft and Structure', 'Expression of Ideas', 'Standard English Conventions'];
    const pairs = doms.map(dname => ({ dname, missed: h('input', { type: 'number', class: 'field sm', min: '0', max: '40', 'aria-label': `${dname} missed`, style: 'width: 70px' }),
      of: h('input', { type: 'number', class: 'field sm', min: '1', max: '40', 'aria-label': `${dname} questions`, style: 'width: 70px' }) }));
    const err = h('p', { class: 'field-err', hidden: true });
    UI.sheet({
      title: 'Your Bluebook scores',
      body: h('div', { style: 'display: grid; gap: 12px' }, h('div', { class: 'row' }, math, rw),
        h('p', { class: 'label', text: 'R&W questions missed, from Bluebook’s report (optional)' }),
        pairs.map(p => h('div', { class: 'row' }, h('span', { style: 'flex: 1 1 200px', text: p.dname }), p.missed, h('span', { class: 'meta', text: 'missed of' }), p.of)), err),
      actions: [{ label: 'Save', primary: true, onClick: async s => {
        s.busy(true);
        try {
          const m = math.value ? Math.round(+math.value / 10) * 10 : null, r = rw.value ? Math.round(+rw.value / 10) * 10 : null;
          if (m || r) await api('/scores', { method: 'POST', body: { day: date, source: 'bluebook', ...(m ? { math: m } : {}), ...(r ? { rw: r } : {}) } });
          const rows = pairs.filter(p => p.of.value).map(p => ({ domain: p.dname, missed: +p.missed.value || 0, of: +p.of.value }));
          if (rows.length) await api(`/plan/${enc(pid())}/rwlog`, { method: 'POST', body: { day: date, task: t.id, rows } });
          UI.toast('Scores saved'); reload();
        } catch (e) { s.busy(false); err.textContent = e.status === 404 ? 'Scores can’t be saved here yet. Your tick is kept.' : (e.message || 'Couldn’t save. Try again.'); err.hidden = false; return false; }
      } }, { label: 'Add the score later', quiet: true }],
    });
  }

  /* ---- week strip, coming up, map, phases, month (3g-3i, L2, L16) */
  function drawWeek() {
    const d = S.d, a = d.active, t = today();
    const mon = monday(S.sel), sun = addDays(mon, 6);
    const wk = (d.weeks || []).find(w => w.from <= S.sel && S.sel <= w.to) || null;
    const box = R.week;
    const prev = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'Previous week', text: '‹', disabled: mon <= a.start || null, onclick: () => pick(clampDay(addDays(S.sel, -7))) });
    const next = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'Next week', text: '›', disabled: sun >= a.cfg.exam_date || null, onclick: () => pick(clampDay(addDays(S.sel, 7))) });
    const head = h('div', { class: 'pl-weekhead' }, h('h2', { class: 'h3', text: `${wk ? `Week ${wk.n} of ${d.weeks.length} · ` : ''}${D(mon)}–${D(sun)}` }), prev, next);
    if (monday(t) !== mon && dayOf(t)) head.append(btn('This week', 'quiet', () => pick(t)));
    const kids = [head];
    if (wk && wk.tasks_planned) {
      const m = h('div', { style: 'margin-top: 8px' });
      UI.meter(m, { label: 'Tasks', value: wk.tasks_done, max: wk.tasks_planned, text: `${wk.tasks_done} of ${wk.tasks_planned} tasks · ${Math.round(wk.tasks_done / wk.tasks_planned * 100)}%`, ink: true });
      kids.push(m);
    }
    if (wk && wk.theme) kids.push(h('p', { class: 'pl-theme', text: pretty(wk.theme) }));
    const grid = h('div', { class: 'pl-week', role: 'group', 'aria-label': 'Days of the week' });
    for (let i = 0; i < 7; i++) {
      const date = addDays(mon, i), x = dayOf(date);
      if (!x) { grid.append(h('span', { class: 'pl-wd', style: 'visibility: hidden', 'aria-hidden': 'true' })); continue; }
      const planned = x.tasks_planned || 0;
      const b = h('button', { type: 'button', class: 'pl-wd', 'aria-pressed': String(date === S.sel), 'data-today': date === t ? '' : null,
        'data-kind': x.kind, 'data-status': x.status, 'aria-label': `${D(date, 'long')}, ${KIND[x.kind] || x.kind}${x.minutes ? `, ${x.minutes} minutes` : ''}${planned ? `, ${x.tasks_done} of ${planned} tasks` : ''}${STATUS[x.status] ? `, ${STATUS[x.status]}` : ''}` },
        h('span', { class: 'k', text: `${DOW[i]} ${+date.slice(8)}` }),
        h('i', { class: 'ic', 'aria-hidden': 'true', text: x.kind === 'exam' ? 'SAT' : '' }),
        h('span', { class: 'mono', text: x.minutes ? `${x.minutes}m` : x.kind === 'off' ? 'off' : x.kind === 'rest' || x.kind === 'eve' ? 'rest' : '' }),
        planned ? h('span', { class: 'mono soft', text: `${x.tasks_done}/${planned}` }) : null,
        planned ? h('span', { class: 'bar', style: `--p: ${Math.min(1, (x.tasks_done || 0) / planned)}` }, h('i')) : null,
        x.status === 'done' ? h('span', { class: 'dotc', 'aria-hidden': 'true', text: '✓' }) : null);
      b.addEventListener('click', () => pick(date));
      grid.append(b);
    }
    kids.push(grid);
    box.replaceChildren(...kids);
  }
  const clampDay = date => { const a = S.d.active; return date < a.start ? a.start : date > a.cfg.exam_date ? a.cfg.exam_date : date; };
  function drawUp() {
    const t = today(), d = S.d;
    const rows = d.days.filter(x => x.date > t && STUDY.has(x.kind)).slice(0, 5);
    const list = h('div', { class: 'pl-up' });
    for (const x of rows) {
      const main = x.tasks.find(k => ['test', 'focus', 'map'].includes(k.kind)) || x.tasks.find(k => k.counted);
      const topics = [...new Set(x.tasks.filter(k => ['focus', 'map', 'learn', 'check'].includes(k.kind)).flatMap(k => k.topics || []))].slice(0, 3);
      const what = x.kind === 'test' ? (main ? main.title : 'Test') : main ? (main.kind === 'focus' ? 'Focus' : main.title) : 'Practice';
      list.append(h('button', { type: 'button', onclick: () => pick(x.date) }, h('span', { class: 'd', text: `${dayName(x.date)} · ${x.minutes}m` }),
        h('span', { class: 't', text: [what, topics.map(tn).join(', ')].filter(Boolean).join(' · ') })));
    }
    const notes = [];
    const rest = d.days.find(x => x.date > t && (x.kind === 'rest' || x.kind === 'off'));
    if (rest) notes.push(`Next rest ${dayName(rest.date)}`);
    const nowPhase = (dayOf(t) || {}).phase;
    const change = d.days.find(x => x.date > t && x.phase && x.phase !== nowPhase && STUDY.has(x.kind));
    if (change) notes.push(`${change.phase} starts ${D(change.date)}${change.phase === 'Sharpen' ? ' · harder, timed' : change.phase === 'Final' ? ' · full sections and your open mistakes' : ''}`);
    R.up.replaceChildren(h('div', { class: 'card-head' }, h('h2', { text: 'Coming up' })), rows.length ? list : h('p', { class: 'soft', text: 'No more study days before the SAT.' }),
      notes.length ? h('p', { class: 'meta', style: 'margin-top: 10px', text: notes.join(' · ') }) : null);
  }
  function mapTile() {
    const m = S.d.map;
    if (!m || !m.on) return null;
    const skills = S.d.skills || [];
    const strip = h('div', { class: 'pl-strip19', role: 'img', 'aria-label': `${m.measured} of ${m.of} skills measured` },
      UI.TOPICS.map(tp => { const s = skills.find(x => x.topic === tp.slug); const on = s && s.answered >= 6; return h('i', { 'data-on': on ? '' : null, title: tp.short, text: on ? '✓' : '' }); }));
    return h('section', { class: 'card', 'aria-label': 'Map progress' }, h('div', { class: 'card-head' }, h('h2', { text: 'Map' }), h('span', { class: 'meta', text: `${m.measured} of ${m.of} skills measured` })),
      h('p', { class: 'line-t', text: 'Map days measure each skill with a few mixed questions, so focus goes where your points are.' }), strip);
  }
  function drawPhase() {
    const d = S.d, t = today(), parts = [];
    for (const x of d.days) {
      if (!x.phase || x.kind === 'exam') continue;
      const last = parts[parts.length - 1];
      if (last && last.name === x.phase) { last.to = x.date; last.n++; } else parts.push({ name: x.phase, from: x.date, to: x.date, n: 1 });
    }
    const now = (dayOf(t) || {}).phase;
    const LINE = { Build: 'Weak skills and new ground, every difficulty.', Sharpen: 'Harder, mixed, on the clock.', Final: 'Full sections and your open mistakes.' };
    R.phase.replaceChildren(h('div', { class: 'card-head' }, h('h2', { text: 'Phases' })),
      h('div', { class: 'pl-phases' }, parts.map(p => h('div', { class: 'pl-ph', style: `--w: ${p.n}`, 'data-now': p.name === now ? '' : null },
        h('b', { text: p.name }), h('span', { class: 'mono', text: `${D(p.from)} – ${D(p.to)}` }), h('span', { text: LINE[p.name] || '' })))));
  }
  function drawCal() {
    const d = S.d, a = d.active, t = today(), now = (dayOf(t) || {}).phase;
    const seen = new Set();
    const plan = d.days.map(x => {
      const first = x.phase && !seen.has(x.phase) && x.kind !== 'exam';
      if (first) seen.add(x.phase);
      const state = { done: 'done', partial: 'partial', missed: 'missed', skipped: 'skipped', made_up: 'madeup' }[x.status] || (x.date >= t && STUDY.has(x.kind) ? 'future' : null);
      return { day: x.date, kind: x.kind === 'exam' ? null : x.kind, state, minutes: x.minutes, tasks: x.tasks_planned ? { done: x.tasks_done, of: x.tasks_planned } : null,
        own: x.custom || x.tasks.some(k => String(k.id).startsWith('pt:')), phase: x.phase, phase_start: first && x.date !== a.start, current_phase: x.phase === now };
    });
    const host = h('div');
    R.cal.replaceChildren(h('div', { class: 'card-head' }, h('h2', { text: 'Calendar' })), host);
    R.calApi = UI.calendar(host, { look: 'plan', plan, selected: S.sel, legend: true,
      marks: { start: a.start, end: a.cfg.exam_date, exam: a.cfg.exam_date, today: t }, min: a.start, max: a.cfg.exam_date, onPick: day => pick(day) });
    // arrow keys move the selection with the focus (28)
    host.addEventListener('focusin', e => { const c = e.target.closest && e.target.closest('.cal-d[data-day]'); if (c && c.dataset.day !== S.sel && host.matches(':focus-within') && e.target.matches(':focus-visible')) pick(c.dataset.day); });
  }
  function drawThumb() {
    if (!R.thumb) return;
    const day = dayOf(today()), next = S.tab === 'plan' && !S.readonly ? nextOf(day) : null;
    R.thumb.hidden = !next;
    if (!next) { R.thumb.replaceChildren(); return; }
    R.thumb.replaceChildren(h('p', {}, h('span', { class: 'soft', text: 'Next' }), `${next.title}${next.count ? ` · ${next.count} q` : ''}`),
      btn('Start', 'pill sm', e => busy(e.currentTarget, () => startTask(next, today()).catch(err => UI.toast(err.rowText || 'Couldn’t start. Try again.')))));
  }

  /* ---- the Plans tab (3k, L20) */
  function drawPlansTab() {
    R.pPlans.replaceChildren(plansCard(S.d.plans || [], S.d.active ? S.d.active.id : null, true));
  }
  function plansCard(plans, activeId, tab) {
    const card = h('section', { class: 'card' + (tab ? '' : ' pl-sec') }, h('div', { class: 'card-head' }, h('h2', { text: 'Your plans' }),
      h('span', { class: 'card-act' }, btn('New plan', 'pill sm', () => go({ setup: 1, step: 1, fresh: 1 })))));
    if (!plans.length) { card.append(h('p', { class: 'soft', text: 'No plans yet. Plans you make stay here, so you can switch when your date or target changes.' })); return card; }
    const list = h('div', { class: 'pl-plans' });
    plans.slice(0, S.shown).forEach(p => list.append(planRow(p, activeId)));
    card.append(list);
    if (plans.length > S.shown) card.append(btn(`Show 20 more · ${plans.length - S.shown} left`, 'btn sm', () => { S.shown += 20; tab ? drawPlansTab() : landing(); }));
    card.append(h('p', { class: 'help', text: 'Changing your date or target? Edit keeps this plan’s record. Save as new keeps this one here.' }));
    return card;
  }
  function planRow(p, activeId) {
    const r = p.record || {};
    const finished = p.result && p.result.math;
    const status = p.status === 'active' ? h('span', { class: 'tag or', text: 'Active' }) : finished ? h('span', { class: 'tag', text: `Finished · ${p.result.math}` }) : h('span', { class: 'tag', text: 'Archived' });
    const here = (S.older || activeId) === p.id ? h('span', { class: 'meta', text: 'You are here' }) : null;
    const name = !p.name || /^Plan for \d{4}-/.test(p.name) ? `${D(p.exam)} · ${p.total_target || p.target}` : p.name;
    const line = [`Built ${D(p.built)}`, `${D(p.start)} → ${D(p.exam)}`, `target ${p.total_target || p.target}`,
      p.days_left > 0 ? `${pl(p.days_left, 'day')} left` : null, p.tasks_done ? `${pl(p.tasks_done, 'task')} done` : null,
      p.adherence ? `${Math.round(p.adherence * 100)}% of days` : null].filter(Boolean).join(' · ');
    const row = h('div', { class: 'pl-prow' }, h('h3', { class: 'h3' }, name, status, here), h('p', { class: 'meta', text: line }));
    if (p.status !== 'active' && r.hours) {
      row.append(h('p', { class: 'meta', text: [`${r.days_pct}% of days`, `${UI.num(r.hours)} h`, r.start_mid && r.end_mid ? `${r.start_mid} → ${r.end_mid} (${r.end_mid - r.start_mid >= 0 ? '+' : ''}${r.end_mid - r.start_mid})` : null,
        r.fixed ? `${r.fixed} fixed` : null, r.relapsed ? `${r.relapsed} relapsed` : null].filter(Boolean).join(' · ') }));
      if ((r.by_dow || []).some(Boolean)) row.append(h('div', { class: 'pl-dow', role: 'img', 'aria-label': r.by_dow.map((v, i) => `${DOW[i]} ${v}%`).join(', ') },
        r.by_dow.map((v, i) => h('span', {}, h('b', { text: DOW[i] }), `${v}%`))));
    }
    if ((p.recent_events || []).length) row.append(h('p', { class: 'meta', text: p.recent_events.slice(0, 3).map(e => `${D(e.at || e.day)} ${pretty(e.text)}`).join(' · ') }));
    const acts = h('div', { class: 'acts' });
    if (p.status !== 'active') {
      acts.append(h('a', { class: 'btn sm', href: `/plan/?id=${enc(p.id)}`, text: 'Open' }));
      const mk = btn('Make active', 'btn sm', () => {
        acts.replaceChildren(h('span', { class: 'line-t', text: 'Switch to this plan? Your current one is kept.' }),
          btn('Switch', 'btn sm ink', e => busy(e.currentTarget, async () => { S.d = await api(`/plan/${enc(p.id)}/activate`, { method: 'POST' }); S.older = null; UI.toast('Switched to this plan'); go({}); })),
          btn('Keep', 'quiet', () => row.replaceWith(planRow(p, activeId))));
      });
      acts.append(mk);
    }
    acts.append(btn('Duplicate', 'quiet', () => duplicate(p.id)));
    if (p.status !== 'active') acts.append(btn('Remove', 'quiet', () => {
      acts.replaceChildren(h('span', { class: 'line-t', text: 'Remove this plan for good?' }),
        btn('Remove', 'btn sm ink', e => busy(e.currentTarget, async () => { await api(`/plan/${enc(p.id)}`, { method: 'DELETE' }); S.d = await api('/plan'); route(); })),
        btn('Keep', 'quiet', () => row.replaceWith(planRow(p, activeId))));
    }));
    row.append(acts);
    return row;
  }
  // ?id=: an older plan. GET /api/plan?id= is asked for; until the server serves it, the
  // page shows that plan's record from the list with both ways out.
  async function olderPlan(id) {
    let d = null;
    try { d = await api(`/plan?id=${enc(id)}`); } catch (_) {}
    const p = ((S.d && S.d.plans) || []).find(x => x.id === id);
    const back = [h('a', { class: 'btn sm', href: '/plan/', text: 'Back to active plan' }),
      btn('Make this my plan', 'pill sm', e => busy(e.currentTarget, async () => { S.d = await api(`/plan/${enc(id)}/activate`, { method: 'POST' }); UI.toast('Switched to this plan'); go({}); }))];
    if (d && d.active && d.active.id === id) {
      S.readonly = true; S.older = id;
      const keep = S.d; S.d = d;
      view();
      R.banners.replaceChildren(banner(`older:${id}`, `You are viewing an older plan · ${D(d.active.start)} → ${D(d.active.cfg.exam_date)} · not your active plan`, back, { keep: true, onDismiss: () => go({}) }));
      S.d = d; S.keep = keep;
      return;
    }
    S.older = id;
    root.replaceChildren(banner(`older:${id}`, p ? `You are viewing an older plan · ${D(p.start)} → ${D(p.exam)} · not your active plan` : 'That plan isn’t in your list.', back, { keep: true, onDismiss: () => go({}) }) || '',
      p ? h('section', { class: 'card pl-sec' }, planRow(p, S.d.active && S.d.active.id)) : '');
  }
  // ?view=: a shared read-only plan (R18a), with no learner code
  async function sharedView() {
    skeleton();
    try {
      const r = await fetch(`/api/plan/shared/${enc(Q.get('view'))}`);
      if (!r.ok) throw new Error(String(r.status));
      S.d = await r.json();
      S.readonly = true;
      view();
    } catch (_) {
      root.replaceChildren(h('section', { class: 'card' }, h('h1', { class: 'h2', text: 'This link is off' }), h('p', { class: 'line-t', text: 'The student turned this link off, or it was typed wrong.' })));
    }
  }

  /* ---- calendar and share (3l, R18) */
  function calendarSheet() {
    const a = S.d.active;
    const out = h('p', { class: 'line-t' });
    const dl = btn('Download .ics', 'btn', e => busy(e.currentTarget, async () => {
      try {
        const r = await fetch(`/api/plan/${enc(a.id)}/ics`, { headers: { 'X-Learner': UI.learner(), 'X-Tz': String(new Date().getTimezoneOffset()) } });
        if (!r.ok) throw new Error();
        const blob = await r.blob(), link = h('a', { href: URL.createObjectURL(blob), download: 'sat-plan.ics' });
        doc.body.append(link); link.click(); link.remove();
      } catch (_) { out.textContent = 'Couldn’t make the file. Try again.'; }
    }));
    const sub = btn('Subscribe', 'btn', e => busy(e.currentTarget, async () => {
      const r = await api(`/plan/${enc(a.id)}/links`, { method: 'POST', body: { cal: true } });
      const link = `${location.origin}${r.cal}`;
      UI.copyText(link, { toast: 'Link copied' });
      out.replaceChildren('Feed link, copied: ', h('span', { class: 'mono', style: 'word-break: break-all', text: link }));
    }));
    const offB = btn('Turn off link', 'quiet', e => busy(e.currentTarget, async () => { await api(`/plan/${enc(a.id)}/links`, { method: 'POST', body: { cal: false } }); out.textContent = 'The feed link is off.'; }));
    UI.sheet({ title: 'Calendar', body: h('div', { style: 'display: grid; gap: 12px' }, h('div', { class: 'row' }, dl, sub, offB), out,
      h('p', { class: 'help', text: 'Some calendar apps ignore reminders in subscribed calendars; the download keeps them.' })) });
  }
  function shareSheet() {
    const a = S.d.active;
    const out = h('p', { class: 'line-t' });
    const on = btn('Make a link', 'btn', e => busy(e.currentTarget, async () => {
      const r = await api(`/plan/${enc(a.id)}/links`, { method: 'POST', body: { view: true } });
      const link = `${location.origin}/plan/?view=${enc(r.view_token)}`;
      UI.copyText(link, { toast: 'Link copied' });
      out.replaceChildren('Read-only link, copied: ', h('span', { class: 'mono', style: 'word-break: break-all', text: link }));
    }));
    const offB = btn('Turn off link', 'quiet', e => busy(e.currentTarget, async () => { await api(`/plan/${enc(a.id)}/links`, { method: 'POST', body: { view: false } }); out.textContent = 'The link is off.'; }));
    UI.sheet({ title: 'Share read-only', body: h('div', { style: 'display: grid; gap: 12px' }, h('div', { class: 'row' }, on, offB), out,
      h('p', { class: 'help', text: 'Anyone with the link sees this plan and its progress, not your code.' })) });
  }

  /* ---- keys (L12, §2.8 scope plan) */
  const rows = () => [...(R.day ? R.day.querySelectorAll('.trow') : [])];
  const selTask = () => { const r = rows()[S.kb]; if (!r) return null; const day = dayOf(S.sel); return day && day.tasks.find(x => x.id === r.dataset.task); };
  function kbMove(k) {
    const all = rows();
    if (!all.length) return;
    S.kb = Math.max(0, Math.min(all.length - 1, (S.kb < 0 ? (k > 0 ? -1 : all.length) : S.kb) + k));
    all.forEach((r, i) => r.toggleAttribute('data-kb', i === S.kb));
    all[S.kb].focus();
  }
  const inPlan = () => !!(S.d && S.d.active && !S.readonly && !Q.has('setup') && !Q.has('edit'));
  UI.keys.register('plan', {
    J: { does: 'Next task', run: () => kbMove(1) }, K: { does: 'Previous task', run: () => kbMove(-1) },
    ArrowDown: { does: 'Next task', run: () => (S.kb >= 0 ? kbMove(1) : false) }, ArrowUp: { does: 'Previous task', run: () => (S.kb >= 0 ? kbMove(-1) : false) },
    Enter: { does: 'Start the selected task', run: () => { const t = selTask(); if (!t || doc.activeElement !== rows()[S.kb]) return false; startTask(t, S.sel).catch(e => UI.toast(e.rowText)); } },
    X: { does: 'Done or not done', run: () => { const t = selTask(); if (!t) return false; const btnEl = rows()[S.kb].querySelector('.trow-box'); if (btnEl && !btnEl.disabled) btnEl.click(); } },
    S: { does: 'Skip or undo', run: () => { const t = selTask(); if (!t) return false; const b = [...rows()[S.kb].querySelectorAll('.trow-act button')].find(x => /^(Skip|Undo)$/.test(x.textContent)); if (b) b.click(); } },
    M: { does: 'Move the selected task', run: () => { const t = selTask(); if (!t) return false; moveMenu(t, dayOf(S.sel)); } },
    ArrowLeft: { does: 'Previous day', run: () => (S.kb < 0 ? pick(clampDay(addDays(S.sel, -1))) : false) },
    ArrowRight: { does: 'Next day', run: () => (S.kb < 0 ? pick(clampDay(addDays(S.sel, 1))) : false) },
    'Shift+ArrowLeft': { does: 'Previous week', run: () => pick(clampDay(addDays(S.sel, -7))) },
    'Shift+ArrowRight': { does: 'Next week', run: () => pick(clampDay(addDays(S.sel, 7))) },
    T: { does: 'Today', run: () => pick(clampDay(today())) },
    1: { does: 'Plan tab', run: () => R.tabs.set('plan') }, 2: { does: 'Progress tab', run: () => R.tabs.set('progress') }, 3: { does: 'Plans tab', run: () => R.tabs.set('plans') },
    'Shift+Enter': { does: 'Start today', run: () => (R.start ? R.start.click() : false) },
  }, { label: 'Plan', when: inPlan });
  doc.addEventListener('focusin', e => { if (S.kb >= 0 && !(e.target.closest && e.target.closest('.trow'))) { S.kb = -1; rows().forEach(r => r.removeAttribute('data-kb')); } });

  UI.planPage = { S, reload, pick, startTask, tn, pretty };
  if (Q.get('view') || Q.has('setup') || Q.has('edit')) route();
  else { skeleton(); load(); }
})();
