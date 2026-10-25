/* ============================================================================
   SAT Freshman -- the plan's Progress tab (S7; spec 3.6 3j, plan.md L2, L3, L13,
   L14, L15, L16, L18, L21; decision 7: a card shows when it has something to say,
   the core ones keep their frame and say what will fill them)

   UI.planProgress(host, ctx)   ctx {d: GET /api/plan, api, pick(date)}
   GET /api/plan already carries every Progress figure; /api/plan/progress is read
   only when a field is missing. Every chart has its hidden table (charts.js).
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h;
  const DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const pad = n => String(n).padStart(2, '0');
  const isoOf = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const today = () => isoOf(new Date());
  const D = (s, st) => UI.date(s, st || 'short');
  const tn = s => UI.topicName(s);
  const pl = (n, w, ws) => `${UI.num(n)} ${n === 1 ? w : (ws || w + 's')}`;
  const pct = (a, b) => (b ? `${Math.round(a / b * 100)}%` : '–');
  // each subject's domains in order, with their skills (UI.TOPICS for Math, UI.RW_DOMAINS for R&W)
  const DOMAINS = {
    math: ['Algebra', 'Advanced Math', 'Problem-Solving and Data Analysis', 'Geometry and Trigonometry']
      .map(name => ({ name, skills: UI.TOPICS.filter(t => t.domain === name).map(t => t.slug) })),
    rw: UI.RW_DOMAINS,
  };
  const domainOf = t => (UI.TOPIC[t] || {}).domain || ((UI.RW_DOMAINS || []).find(x => x.skills.includes(t)) || {}).name;
  let subject = null;                         // the switch at the top of the tab: Math or R&W
  const card = (title, meta, ...kids) => h('section', { class: 'card' }, h('div', { class: 'card-head' }, h('h2', { text: title }), meta ? h('span', { class: 'meta', text: meta }) : null), ...kids);
  let sortBy = null;

  function planProgress(host, ctx) {
    const d = ctx.d;
    const need = ['bought', 'causes', 'coverage', 'checks', 'weeks', 'checkpoints', 'calibration', 'split_domain', 'rw_domains', 'by_subject'].filter(k => !(k in d));
    if (need.length) {
      host.replaceChildren(h('div', { class: 'pg' }, h('div', { class: 'card' }, h('span', { class: 'skel', style: 'height: 160px' }))));
      ctx.api('/plan/progress').then(p => { Object.assign(d, p); draw(host, ctx); })
        .catch(() => { host.replaceChildren(); UI.cardError(host, () => planProgress(host, ctx), 'Couldn’t load your progress.'); });
      return;
    }
    draw(host, ctx);
  }

  // main: the charts, grids and tables; beside them (from 1280px) the short summaries
  function draw(host, ctx) {
    const a = ctx.d.active, c = a.cfg, st = ctx.d.stats, t = today();
    const s = subject = subject || UI.subject.get();
    // the chosen subject's evidence over the plan's own figures (time, days and weeks count both)
    const pick = o => (o ? o[s] : undefined);
    const mine = (ctx.d.score || {})[s] || {};
    const d = { ...ctx.d, ...((ctx.d.by_subject || {})[s] || {}), coverage: ctx.d.coverage, s, rw: s === 'rw',
      start: s === 'rw' ? c.rw_current : c.current, target: s === 'rw' ? c.rw_target : c.target,   // no R&W target: no target line
      checks: (ctx.d.checks || []).filter(x => (x.subject || 'math') === s),
      checkpoints: (ctx.d.checkpoints || []).filter(x => (x.subject || 'math') === s) };
    if (mine.target) d.target = mine.target;
    const main = [], side = [];
    // the switch stays put while the tab under it redraws (focus and its thumb stay where they are)
    host._ctx = ctx;
    if (!host._body || !host.contains(host._body)) {
      const seg = h('div', { class: 'pg-subject' });
      UI.subjectSeg(seg, { value: s, onChange: v => { subject = v; draw(host, host._ctx); } });
      host._body = h('div');
      host.replaceChildren(seg, host._body);
    }
    // since the start: what the status block doesn't already say, as rows
    const openLink = st.mistakes_open ? h('a', { href: '/review/', text: `open ${st.mistakes_open}` }) : null;
    const nums = [
      st.minutes_done ? ['Time', UI.dur(st.minutes_done), `of ${UI.dur(st.minutes_planned)}`] : null,
      st.questions ? ['Questions', UI.num(st.questions), `${pct(st.right, st.questions)} right`] : null,
      st.mistakes_closed || st.mistakes_opened ? ['Mistakes fixed', UI.num(st.mistakes_closed), [st.mistakes_opened ? `opened ${st.mistakes_opened}` : null, openLink]] : null,
      st.rechecks_passed ? ['Check-ins held', UI.num(st.rechecks_passed), st.rechecks_due ? `${st.rechecks_due} due` : ''] : null,
      st.tests ? ['Tests', UI.num(st.tests), ''] : null,
    ].filter(Boolean);
    side.push(card(`Since ${D(a.start)}`, null, nums.length
      ? h('dl', { class: 'pg-nums' }, nums.map(([k, v, s]) => {
        const sub = (Array.isArray(s) ? s : [s]).filter(Boolean);
        return h('div', {}, h('dt', { text: k }), h('dd', {}, v, sub.length ? h('small', {}, ' ', sub.flatMap((x, i) => (i ? [' · ', x] : [x]))) : null));
      }))
      : h('p', { class: 'line-t', text: 'Day 1. Today’s tasks are on the Plan tab.' })));
    // checkpoint (L14)
    const cp = (d.checkpoints || [])[0];
    if (cp) side.push(checkpointCard(cp, ctx).el);
    // the score path (TrajectoryChart, L13): the empty state and its action in the header
    const sits = (d.sittings || []).map(s => ({ id: s.id || s.session, at: s.at, low: s.low, high: s.high, kind: s.kind, href: s.id ? `/results/report/?id=${encodeURIComponent(s.id)}` : null }));
    const nt = nextTest(d);
    const trajMeta = h('span', { class: 'meta pl-hmeta' }, sits.length ? (pick(d.pace) ? pick(d.pace).status : null) : 'No test yet',
      !sits.length && nt ? h('button', { type: 'button', class: 'quiet', text: nt.date === t ? 'Take today’s test' : 'Take this week’s test', onclick: e => { e.currentTarget.setAttribute('aria-busy', 'true'); UI.planPage && UI.planPage.startTask(nt.t, nt.date).catch(() => UI.toast('Couldn’t start. Try again.')); } }) : null);
    const traj = h('section', { class: 'card pg-traj' }, h('div', { class: 'card-head' }, h('h2', { text: 'Score path' }), trajMeta));
    const host2 = h('div');
    traj.append(host2);
    // this subject's tests only (a full SAT's aim is a total, not on this scale)
    const aims = d.days.filter(x => x.kind === 'test').map(x => { const tk = x.tasks.find(k => k.kind === 'test' && (k.subject || 'math') === s); return tk && tk.aim ? { day: x.date, value: Math.round(tk.aim / 10) * 10, beaten: tk.result && tk.result.verdict === 'beat' } : null; }).filter(Boolean);
    const proj = pick(d.projection);
    const tgt = d.target ? Math.min(d.target, 780) : null;          // a section without a target draws none
    const begun = d.start !== null && d.start !== undefined;
    // the y-axis spans the plan's own range, not 200-800
    const lows = [...(tgt ? [tgt] : []), ...(begun ? [d.start] : []), ...sits.map(x => x.low).filter(v => v > 0), ...aims.map(x => x.value)];
    const highs = [...(tgt ? [tgt] : []), ...(begun ? [d.start] : []), ...sits.map(x => x.high).filter(v => v > 0)];
    const low = lows.length ? Math.min(...lows) : 400, high = highs.length ? Math.max(...highs) : 600;   // (nothing yet: the middle)
    UI.bandChart(host2, sits, {
      height: 220, fit: true, x: 'time', from: a.start, to: c.exam_date, target: tgt, exam: c.exam_date,
      min: Math.max(200, Math.floor((low - 60) / 50) * 50), max: Math.min(800, Math.ceil((high + 60) / 50) * 50), grid: 50,
      pace: begun && tgt ? { from: { day: a.start, value: d.start }, to: { day: c.exam_date, value: tgt }, aims } : null,
      projection: proj && proj.low ? { low: proj.low, high: proj.high, mid: proj.mid, to: c.exam_date, label: 'At this pace' } : undefined,
      label: `${UI.subjectLabel(s)} score path`,
    });
    // "Target 680" reads from the left end of its line, clear of the exam day's line
    const tidy = () => {
      const svg = host2.querySelector('svg'), ln = svg && svg.querySelector('.ch-target');
      const lab = svg && [...svg.querySelectorAll('text')].find(x => /^Target /.test(x.textContent));
      if (ln && lab && lab.getAttribute('text-anchor') !== 'start') { lab.setAttribute('x', String(+ln.getAttribute('x1') + 6)); lab.setAttribute('text-anchor', 'start'); }
    };
    tidy();
    // one watcher per Progress host: a redraw replaces the last one instead of adding another
    if (host._pgObs) host._pgObs.forEach(o => o.disconnect());
    host._pgObs = [];
    const mo = new MutationObserver(tidy);
    mo.observe(host2, { childList: true, subtree: true });
    host._pgObs.push(mo);
    if (sits.length) traj.querySelector('h2').append(UI.why('Each test shows as a 20-point range around its score. The status uses your last 3 tests.', { about: 'the score path' }));
    main.push(traj);
    // what your time bought (L18)
    if ((d.bought || []).length) {
      const rows = h('div', { class: 'pg-rows' });
      for (const b of d.bought.slice().sort((x, y) => y.minutes - x.minutes)) {
        const acc = s => (s && s.of ? `${Math.round(s.right / s.of * 100)}%` : 'new');
        const r = h('div', { class: 'pg-row' }, h('span', { class: 'h3', text: tn(b.topic) }),
          h('span', { class: 'meta', text: `${UI.dur(b.minutes)}` }),
          h('span', { class: 'meta', text: [`${acc(b.before)} → ${acc(b.after)} first try`, b.fixed ? `${b.fixed} fixed` : null, checkText(b.check), b.claimed ? `≈ +${b.claimed}` : null].filter(Boolean).join(' · ') }));
        if (b.not_moving) r.append(h('p', { class: 'meta pg-stuck', text: `Not moving · ${acc(b.before)} → ${acc(b.after)} over 20 answers each · ${UI.dur(b.minutes_14d)} in 14 days` }),
          h('div', { class: 'row pg-wide' }, h('button', { type: 'button', class: 'btn sm', text: 'Learn it · untimed', onclick: e => start(e.currentTarget, { source: 'learn', topics: [b.topic], example: true, count: 3 }) }),
            h('a', { class: 'quiet', href: `/review/?topic=${encodeURIComponent(b.topic)}${d.rw ? '&subject=rw' : ''}`, text: 'See its misses' })));
        rows.append(r);
      }
      main.push(card('What your time bought', null, rows));
    }
    // ready on every skill? (L2)
    const cov = pick(d.coverage);
    if (cov && (cov.cells || []).length) main.push(coverageCard(cov, s));
    // why you lose points (T7)
    const cz = d.causes;
    if (cz && cz.total) {
      const NAME = { trap: 'Named traps', slip: 'Slips', clock: 'Ran out of time', entry: 'Grid-in entry', gap: 'Not learned yet', misread: 'Misread', changed: 'Changed a right answer' };
      const segs = Object.entries(cz.by || {}).filter(([, n]) => n).map(([k, n]) => ({ key: k, label: NAME[k] || k, value: n }));
      const box = h('div');
      UI.stackBar(box, segs, { noun: 'misses', label: 'Why you lose points' });
      legendIfNeeded(box, host);
      side.push(card('Why you lose points', `${pl(cz.total, 'miss', 'misses')} since ${D(a.start)}`, box));
    }
    // pace and calibration (U7, P7): how sure you were, as three bars
    const cal = d.calibration, sp = d.skill_pace;
    const paceKids = [];
    if (!d.rw && sp && sp.forecast && sp.forecast.seconds && sp.skills && Object.keys(sp.skills).length) paceKids.push(h('p', { class: 'line-t', text: `A module at your pace takes ${UI.mmss(sp.forecast.seconds)} of ${UI.mmss(sp.forecast.limit)}` }));
    const slow = sp && sp.quadrants ? (sp.quadrants.slow_right || []).slice(0, 3) : [];
    slow.forEach(x => paceKids.push(h('div', { class: 'row' }, h('span', { class: 'line-t', text: tn(x.topic || x) }),
      h('button', { type: 'button', class: 'btn sm', text: 'Speed drill · 8', onclick: e => start(e.currentTarget, { topics: [x.topic || x], count: 8, timing: 'pace', source: 'pace' }) }))));
    const tagged = cal ? ['sure', 'unsure', 'guess'].reduce((s, k) => s + ((cal[k] || {}).of || 0), 0) : 0;
    if (tagged >= 20) {
      const bars = h('div', { class: 'pg-conf', role: 'group', 'aria-label': 'How sure you were, and how often right' });
      ['sure', 'unsure', 'guess'].filter(k => cal[k] && cal[k].of).forEach(k => UI.meter(bars, { label: { sure: 'Sure', unsure: 'Unsure', guess: 'Guess' }[k],
        value: Math.round(cal[k].accuracy * 100), max: 100, text: `${Math.round(cal[k].accuracy * 100)}% right · ${cal[k].of}`, ink: true }));
      paceKids.push(bars);
    }
    if (paceKids.length) side.push(card('Pace and how sure you were', null, ...paceKids, h('p', { class: 'help' }, h('a', { class: 'quiet', href: `/me/?subject=${s}#pace`, text: 'Every skill' }))));
    // the plan's minutes by task: focus in orange, the rest in three greys, named in the key
    const split = splitCard(d);
    if (split) side.push(split);
    // domains: accuracy, time and points in one table (L18, L21, T17)
    main.push(domainCard(d));
    // all 19 skills (L18): a long table, folded until opened (remembered)
    main.push(skillsCard(d));
    // study time per day (StudyTimeChart)
    const past = d.days.filter(x => x.date <= t && (x.minutes || x.minutes_done));
    const sc = card('Study time per day', past.length ? `${UI.dur(past.reduce((s, x) => s + (x.minutes_done || 0), 0))} studied of ${UI.dur(past.reduce((s, x) => s + (x.minutes || 0), 0))} planned` : null);
    const box = h('div');
    sc.append(box);
    if (past.some(x => x.minutes_done)) UI.barChart(box, past.slice(-28).map(x => ({ day: x.date, studied: Math.round(x.minutes_done || 0), planned: x.minutes, today: x.date === t,
      tip: `${D(x.date, 'long')} · ${Math.round(x.minutes_done || 0)} of ${x.minutes} min${x.questions ? ` · ${x.questions} questions` : ''}` })),
    { series: [{ key: 'studied', label: 'Studied', look: 'ink' }], unit: 'min', labels: 'date', height: 180, label: 'Study time per day', onPick: row => ctx.pick(row.day) });
    else {
      // nothing logged yet: a dimmed sample week says what will fill it
      const ghost = h('div', { class: 'pg-sample', 'aria-hidden': 'true', inert: true });
      const mon = new Date(`${a.start}T12:00`);
      UI.barChart(ghost, [20, 35, 0, 45, 30, 0, 40].map((v, i) => { const x = new Date(mon); x.setDate(x.getDate() + i); return { day: isoOf(x), studied: v, planned: 45 }; }),
        { series: [{ key: 'studied', label: 'Studied', look: 'ink' }], unit: 'min', labels: 'date', height: 120, label: 'Sample week' });
      box.append(ghost, h('p', { class: 'soft', text: 'Nothing logged yet. Each study day shows here as you go.' }));
    }
    main.push(sc);
    // checks (L3)
    const checks = (d.checks || []).filter(x => x.before);
    if (checks.length) {
      const rows = h('div', { class: 'pg-rows' });
      for (const x of checks) rows.append(h('div', { class: 'pg-row' }, h('span', { class: 'h3', text: tn(x.topic) }),
        h('span', { class: x.result === 'passed' ? 'badge' : 'badge soft', text: x.result ? { passed: 'Passed', again: 'Again', learn: 'Learn first' }[x.result] : 'After to come' }),
        h('span', { class: 'meta', text: `before ${x.before.right}/${x.before.of}${x.after ? ` → after ${x.after.right}/${x.after.of} on the same question types` : ''}${x.recent && x.recent.of ? ` · ${x.recent.right} of your last ${x.recent.of}` : ''}` })));
      main.push(card('Checks', null, rows));
    }
    // weeks (L16): days studied and time; tasks once there are some
    const weeks = (d.weeks || []).filter(w => w.to < t);
    if (weeks.length) {
      const rows = h('div', { class: 'pg-rows' });
      for (const w of weeks.slice().reverse()) {
        const days = d.days.filter(x => x.date >= w.from && x.date <= w.to);
        const study = days.filter(x => ['practice', 'test'].includes(x.kind));
        const done = study.filter(x => ['done', 'partial', 'made_up'].includes(x.status)).length;
        const q = days.reduce((s, x) => s + (x.questions || 0), 0);
        rows.append(h('div', { class: 'pg-row' }, h('span', { text: `Week ${w.n} · ${w.from.slice(0, 7) === w.to.slice(0, 7) ? `${D(w.from)}–${+w.to.slice(8)}` : `${D(w.from)}–${D(w.to)}`}` }),
          h('span', { class: 'meta', text: `${done} of ${pl(study.length, 'day')} studied` }),
          h('span', { class: 'meta', text: [UI.dur(days.reduce((s, x) => s + (x.minutes_done || 0), 0)), q ? pl(q, 'question') : null, w.tasks_done ? `${w.tasks_done} of ${pl(w.tasks_planned, 'task')}` : null].filter(Boolean).join(' · ') })));
      }
      main.push(card('Weeks', null, rows));
    }
    host._body.replaceChildren(h('div', { class: 'twocol pg' }, h('div', { class: 'pg-main' }, main), h('aside', { class: 'twocol-side', 'aria-label': 'Progress at a glance' }, side)));
  }
  // a stack bar's legend only while a segment is too narrow to carry its own label
  function legendIfNeeded(box, host) {
    const sync = () => requestAnimationFrame(() => requestAnimationFrame(() => {
      const key = box.querySelector('.sb-key');
      if (key) key.style.display = box.querySelector('.sb-l.hide') ? '' : 'none';
    }));
    sync();
    if (window.ResizeObserver) { const ro = new ResizeObserver(sync); ro.observe(box); if (host && host._pgObs) host._pgObs.push(ro); }
  }

  // a check's before and after on the same question types (L3)
  function checkText(x) {
    if (!x) return null;
    if (typeof x === 'string') return x;
    const f = s => (s && s.of ? `${s.right}/${s.of}` : null);
    return f(x.before) ? `check ${f(x.before)}${f(x.after) ? ` → ${f(x.after)}` : ''}` : null;
  }
  function nextTest(d) {
    const t = today(), mine = k => k.kind === 'test' && (k.subject || 'math') === d.s && !['done', 'marked', 'made_up'].includes(k.status);
    const x = d.days.find(y => y.date >= t && y.kind === 'test' && y.tasks.some(mine));
    const tk = x && x.tasks.find(mine);
    return tk ? { t: tk, date: x.date } : null;
  }
  async function start(b, body) {
    b.setAttribute('aria-busy', 'true');
    if (subject === 'rw') body = { ...body, subject: 'rw' };       // a drill reads Math unless told
    try { const r = await UI.api('/drill', { method: 'POST', body }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
    catch (_) { UI.toast('Couldn’t start. Try again.'); b.removeAttribute('aria-busy'); }
  }
  function checkpointCard(cp, ctx) {
    const slots = cp.slots || [];
    const n = k => slots.filter(s => s.change === k).length;
    const GL = { fixed: '✗→✓', held: '✓→✓', slipped: '✓→✗', still_missed: '✗→✗' };
    const c = card(`Checkpoint ${cp.n || ''}`.trim(), cp.baseline && cp.checkpoint ? `${cp.baseline.right}/${slots.length} → ${cp.checkpoint.right}/${slots.length}` : null);
    const strip = h('div', { class: 'pl-strip19', role: 'group', 'aria-label': 'Slots of module 1' },
      slots.map((s, i) => h('i', { 'data-on': s.change === 'fixed' || s.change === 'held' ? '' : null, title: `${i + 1} · ${tn(s.topic)} · ${s.change.replace('_', ' ')}${s.practised ? ' · practised' : ''}`, text: GL[s.change] ? GL[s.change][2] : '' })));
    c.append(strip, h('p', { class: 'meta pl-after', text: `fixed ${n('fixed')} · held ${n('held')} · slipped ${n('slipped')} · still missed ${n('still_missed')}` }));
    // what the squares say on hover, in words (a phone has no hover)
    const which = k => [...new Set(slots.filter(s => s.change === k).map(s => tn(s.topic)))].join(', ');
    const said = [n('slipped') ? `Slipped: ${which('slipped')}` : null, n('still_missed') ? `Still missed: ${which('still_missed')}` : null].filter(Boolean);
    if (said.length) c.append(h('p', { class: 'help', text: said.join('. ') }));
    const redo = slots.filter(s => s.change === 'slipped' || s.change === 'still_missed');
    if (redo.length && cp.session) c.append(h('div', { class: 'card-foot' }, h('button', { type: 'button', class: 'pill sm', text: `Fix these ${redo.length}`,
      onclick: e => start(e.currentTarget, { from_session: cp.session, only: redo.map(s => s.qid), each: 2, sibling: true, source: 'twin', task: `${today()}:extra` }) })));
    return { el: c, ctx };
  }
  function coverageCard(cov, s) {
    const cells = cov.cells;
    const cnt = cov.counts || {};
    const needed = cells.filter(x => x.needed);
    const proven = needed.filter(x => x.state === 'proven').length;
    const WORD = { proven: 'proven', shaky: 'shaky', untested: 'not tried' };
    const head = [proven ? `${proven} proven` : null, cnt.shaky ? `${cnt.shaky} shaky` : null, cnt.untested ? `${cnt.untested} not tried` : null].filter(Boolean).join(' · ');
    const grid = h('div', { class: 'pg-grid', role: 'grid', 'aria-label': 'Every skill by tier' });
    grid.append(h('span', { role: 'columnheader', class: 'hd', style: 'text-align: left', text: 'Skill' }), ...['Easy', 'Medium', 'Hard'].map(x => h('span', { role: 'columnheader', class: 'hd', text: x })));
    for (const dm of DOMAINS[s]) {
      grid.append(h('span', { class: 'dm', text: dm.name }));
      for (const tp of dm.skills.map(slug => ({ slug, short: tn(slug) }))) {
        grid.append(h('span', { role: 'rowheader', text: tp.short }));
        for (const tier of ['easy', 'medium', 'hard']) {
          const x = cells.find(y => y.topic === tp.slug && y.tier === tier) || { state: 'na' };
          const label = `${tp.short}, ${tier}: ${WORD[x.state] || x.state}${x.n ? `, ${x.right} of ${x.n}` : ''}${x.needed ? '' : ', not needed'}${x.next ? `, next ${D(x.next)}` : x.needed && x.state !== 'proven' && !x.planned ? ', not planned before Final' : ''}`;
          const b = h('button', { type: 'button', role: 'gridcell', class: 'pg-cell', 'data-s': x.state, 'data-need': x.needed ? '1' : '0', 'aria-label': label, disabled: x.state === 'na' || null });
          if (x.state !== 'na') {
            if (UI.tooltip) UI.tooltip(b, `${label}. Starts 5 questions.`);
            b.addEventListener('click', e => start(e.currentTarget, { topics: [tp.slug], tiers: [tier], count: 5, source: 'plan' }));
          }
          grid.append(b);
        }
      }
    }
    // arrows move between cells
    grid.addEventListener('keydown', e => {
      const all = [...grid.querySelectorAll('.pg-cell:not(:disabled)')], i = all.indexOf(document.activeElement);
      const k = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: 3, ArrowUp: -3 }[e.key];
      if (i < 0 || !k) return;
      e.preventDefault();
      const j = Math.max(0, Math.min(all.length - 1, i + k));
      all[j].focus();
    });
    const key = h('div', { class: 'pg-key', 'aria-hidden': 'true' }, [['proven', 'Proven'], ['shaky', 'Shaky'], ['untested', 'Not tried']].map(([s, t]) => h('span', {}, h('i', { class: 'pg-cell', 'data-s': s }), t)));
    const c = card('Ready on every skill?', head, key, grid);
    const why = [cov.window_days ? `Every skill at least once in ${cov.window_days} days at this time.` : null, 'A cell starts 5 questions on that skill and tier.',
      cnt.unplanned ? `${cnt.unplanned} of them aren’t planned before Final.` : null].filter(Boolean).join(' ');
    c.querySelector('h2').append(UI.why(why, { about: 'this grid' }));
    return c;
  }
  // one table: how you do, where the time goes, where the points are (decision 7: said once)
  function domainCard(d) {
    const gains = d.points && d.points[d.s] && d.points[d.s].skills;
    const gainOf = dn => (gains || []).filter(x => domainOf(x.topic) === dn).reduce((s, x) => s + Math.max(0, x.gain || 0), 0);
    const split = Object.fromEntries((d.split_domain || []).map(x => [x.domain, x]));
    const rows = (d.domains || []).map(x => ({ ...x, acc: x.answered ? x.right / x.answered : null, time: split[x.domain] ? split[x.domain].time_share : x.share_planned || 0,
      pts: split[x.domain] ? split[x.domain].points_share || null : null, gain: gainOf(x.domain) }));
    const box = h('div');
    const skillsIn = dn => (DOMAINS[d.s].find(x => x.name === dn) || { skills: [] }).skills;
    const cols = [
      { key: 'domain', label: 'Domain', render: r => h('span', { class: 'pg-dn' }, h('a', { href: `/practice/?topics=${skillsIn(r.domain).join(',')}${d.rw ? '&subject=rw' : ''}`, text: r.domain }),
        r.state && r.state !== 'normal' ? h('span', { class: r.state === 'focus' ? 'badge' : 'badge line', text: r.state === 'focus' ? 'Focus' : 'Strong' }) : null) },
      { key: 'acc', label: '% right', num: true, render: r => (r.acc === null ? '' : `${Math.round(r.acc * 100)}% (${UI.num(r.answered)})`) },
      { key: 'time', label: 'Time share', num: true, render: r => `${Math.round(r.time * 100)}%${r.share_done ? ` · ${Math.round(r.share_done * 100)}% done` : ''}` },
      { key: 'pts', label: 'Points share', num: true, render: r => (r.pts ? `${Math.round(r.pts * 100)}%` : '') },
      { key: 'gain', label: 'Points to gain', num: true, render: r => (r.gain >= 5 ? `+${Math.round(r.gain)}` : '') },
    ];
    UI.table(box, cols, rows, { sort: gains ? { key: 'gain', dir: 'desc' } : { key: 'acc', dir: 'asc' }, sortable: true, label: 'Domains', compact: true });
    const c = card('Domains', null, box);
    // R&W misses logged from a Bluebook test (L21) say what they found, under the table they add to
    const logged = d.rw ? (d.rw_domains || []).filter(x => x.of) : [];
    if (logged.length) c.append(h('p', { class: 'help', text: `From Bluebook: ${logged.map(x => `${x.domain} missed ${x.missed} of ${x.of}`).join(' · ')}` }));
    return c;
  }
  // the plan's minutes by task: focus in orange, the rest in three greys, named in the key
  function splitCard(d) {
    const kinds = Object.entries(d.stats.split_planned || {}).filter(([, m]) => m > 0);
    if (!kinds.length) return null;
    const GROUP = { focus: 'Focus', test: 'Tests', fix: 'Mistakes and warm-up', recheck: 'Mistakes and warm-up', sweep: 'Mistakes and warm-up' };
    const sum = {};
    for (const [k, m] of kinds) { const g = GROUP[k] || 'Everything else'; sum[g] = (sum[g] || 0) + m; }
    const order = ['Focus', 'Mistakes and warm-up', 'Tests', 'Everything else'].filter(g => sum[g]);
    const total = order.reduce((s, g) => s + sum[g], 0);
    const say = g => `${g} ${Math.round(sum[g] / total * 100)}%`;
    return card('Planned time by task', null,
      h('div', { class: 'pg-split', role: 'img', 'aria-label': `Planned time by task: ${order.map(say).join(', ')}` }, order.map((g, i) => h('span', { style: `flex-grow: ${sum[g]}`, 'data-g': g === 'Focus' ? 'focus' : String(i) }))),
      h('div', { class: 'pg-key' }, order.map((g, i) => h('span', {}, h('i', { class: 'pg-sw', 'data-g': g === 'Focus' ? 'focus' : String(i) }), `${say(g)} · ${UI.dur(Math.round(sum[g]))}`))));
  }
  function skillsCard(d) {
    const gains = Object.fromEntries(((d.points && d.points[d.s] && d.points[d.s].skills) || []).map(x => [x.topic, x.gain]));
    const of = d.rw ? '&subject=rw' : '';
    const all = (d.skills || []).map(s => ({ ...s, name: tn(s.topic), acc: s.answered ? s.right / s.answered : null, gain: gains[s.topic] ?? null }));
    const rows = all.filter(s => s.answered), untried = all.filter(s => !s.answered);
    const box = h('div');
    const cols = [
      { key: 'name', label: 'Skill', render: r => h('a', { href: `/practice/?topics=${r.topic}${of}`, text: r.name }) },
      { key: 'answered', label: 'Answered', num: true },
      { key: 'acc', label: '% right', num: true, render: r => `${Math.round(r.acc * 100)}%` },
      { key: 'traps', label: 'Open', num: true, render: r => (r.traps ? String(r.traps) : '') },
      { key: 'gain', label: 'Points to gain', num: true, render: r => (r.gain >= 5 ? `+${Math.round(r.gain)}` : '') },
      { key: 'last', label: 'Last worked', render: r => (r.last ? D(String(r.last).slice(0, 10)) : '') },
    ];
    const def = Object.keys(gains).length ? 'gain' : 'acc';
    if (rows.length) UI.table(box, cols, rows, { sort: sortBy || { key: def, dir: def === 'gain' ? 'desc' : 'asc' }, onSort: s => { sortBy = s; }, sortable: true, label: 'Skills you’ve worked', compact: true });
    const c = card(`All ${all.length} ${d.rw ? 'R&W ' : ''}skills`, null, box);
    if (untried.length) c.append(h('details', { class: 'pg-untried' }, h('summary', { text: `Not tried yet (${untried.length})` }),
      h('div', { class: 'pg-utl' }, untried.sort((a, b) => (b.gain || 0) - (a.gain || 0)).map(s => h('a', { href: `/practice/?topics=${s.topic}${of}` }, s.name, s.gain >= 5 ? h('span', { class: 'meta', text: ` +${Math.round(s.gain)}` }) : null)))));
    c.append(h('p', { class: 'help' }, h('a', { class: 'quiet', href: `/results/?subject=${d.s}`, text: 'Every result' })));
    // closed until opened; the choice is remembered
    const KEY = 'satf.plan.skills';
    const isOpen = () => { try { return localStorage.getItem(KEY) === '1'; } catch (_) { return false; } };
    c.append(h('p', { class: 'card-sum', text: [rows.length ? `${rows.length} worked` : null, untried.length ? `${untried.length} not tried yet` : null].filter(Boolean).join(' · ') || 'None worked yet' }));
    const fold = h('button', { type: 'button', class: 'ibtn card-fold', 'aria-label': 'Show the skills table', html: UI.svg(UI.ICON.chev, 18) });
    const set = open => {
      c.toggleAttribute('data-collapsed', !open);
      fold.setAttribute('aria-expanded', String(open));
      fold.setAttribute('aria-label', open ? 'Hide the skills table' : 'Show the skills table');
    };
    fold.addEventListener('click', () => { const open = c.hasAttribute('data-collapsed'); set(open); try { localStorage.setItem(KEY, open ? '1' : '0'); } catch (_) {} });
    c.querySelector('.card-head').append(fold);
    set(isOpen());
    return c;
  }

  Object.assign(UI, { planProgress });
})();
