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
  const tn = s => (UI.TOPIC[s] || {}).short || String(s || '').replace(/_/g, ' ');
  const pl = (n, w, ws) => `${UI.num(n)} ${n === 1 ? w : (ws || w + 's')}`;
  const pct = (a, b) => (b ? `${Math.round(a / b * 100)}%` : '—');
  const DOMAINS = ['Algebra', 'Advanced Math', 'Problem-Solving and Data Analysis', 'Geometry and Trigonometry'];
  const card = (title, meta, ...kids) => h('section', { class: 'card' }, h('div', { class: 'card-head' }, h('h2', { text: title }), meta ? h('span', { class: 'meta', text: meta }) : null), ...kids);
  let sortBy = null, domBy = null;

  function planProgress(host, ctx) {
    const d = ctx.d;
    const need = ['bought', 'causes', 'coverage', 'checks', 'weeks', 'checkpoints', 'calibration', 'split_domain', 'rw_domains'].filter(k => !(k in d));
    if (need.length) {
      host.replaceChildren(h('div', { class: 'pg' }, h('div', { class: 'card wide' }, h('span', { class: 'skel', style: 'height: 160px' }))));
      ctx.api('/plan/progress').then(p => { Object.assign(d, p); draw(host, ctx); })
        .catch(() => { host.replaceChildren(); UI.cardError(host, () => planProgress(host, ctx), 'Couldn’t load your progress.'); });
      return;
    }
    draw(host, ctx);
  }

  function draw(host, ctx) {
    const d = ctx.d, a = d.active, c = a.cfg, st = d.stats, t = today();
    const cards = [];
    // checkpoint (L14)
    const cp = (d.checkpoints || [])[0];
    if (cp) cards.push(checkpointCard(cp, ctx).el);
    // since the start
    const nums = [
      st.days_planned ? ['Days done', `${st.days_done}/${st.days_planned}`, pct(st.days_done, st.days_planned)] : null,
      st.minutes_done ? ['Time', UI.dur(st.minutes_done), `of ${UI.dur(st.minutes_planned)}`] : null,
      st.questions ? ['Questions', UI.num(st.questions), `${pct(st.right, st.questions)} right`] : null,
      st.mistakes_closed || st.mistakes_opened ? ['Mistakes fixed', UI.num(st.mistakes_closed), `opened ${st.mistakes_opened} · open ${st.mistakes_open}`] : null,
      st.rechecks_passed ? ['Check-ins held', UI.num(st.rechecks_passed), st.rechecks_due ? `${st.rechecks_due} due` : ''] : null,
      st.tests ? ['Tests', UI.num(st.tests), ''] : null,
      st.longest ? ['Streak', UI.num(st.streak), `longest ${st.longest}`] : null,
    ].filter(Boolean);
    const since = card(`Since ${D(a.start)}`, null, nums.length
      ? h('dl', { class: 'pg-nums' }, nums.map(([k, v, s]) => h('div', {}, h('dt', { text: k }), h('dd', {}, v, s ? h('small', { text: ` ${s}` }) : null))))
      : h('p', { class: 'line-t', text: 'Day 1. Today’s tasks are on the Plan tab.' }));
    if (st.mistakes_open) since.append(h('p', { class: 'help' }, h('a', { href: '/review/', text: `${pl(st.mistakes_open, 'open mistake')} in Review` })));
    cards.push(since);
    // the score path (TrajectoryChart, L13)
    const traj = card('Score path', d.pace && d.pace.math ? d.pace.math.status : null);
    const host2 = h('div');
    traj.append(host2);
    const sits = (d.sittings || []).map(s => ({ id: s.id || s.session, at: s.at, low: s.low, high: s.high, kind: s.kind, href: s.id ? `/results/report/?id=${encodeURIComponent(s.id)}` : null }));
    const aims = d.days.filter(x => x.kind === 'test').map(x => { const tk = x.tasks.find(k => k.kind === 'test'); return tk && tk.aim ? { day: x.date, value: Math.round(tk.aim / 10) * 10, beaten: tk.result && tk.result.verdict === 'beat' } : null; }).filter(Boolean);
    const proj = d.projection && d.projection.math;
    UI.bandChart(host2, sits, {
      height: 220, fit: true, x: 'time', from: a.start, to: c.exam_date, target: Math.min(c.target, 780), exam: c.exam_date,
      pace: c.current !== null && c.current !== undefined ? { from: { day: a.start, value: c.current }, to: { day: c.exam_date, value: Math.min(c.target, 780) }, aims } : null,
      projection: proj && proj.low ? { low: proj.low, high: proj.high, mid: proj.mid, to: c.exam_date, label: 'At this pace' } : undefined,
      empty: { text: 'No test yet', action: nextTest(d) ? { label: 'Start this week’s test', onClick: () => UI.planPage && UI.planPage.startTask(nextTest(d).t, nextTest(d).date) } : null },
      label: 'Math score path',
    });
    if (sits.length) traj.append(h('p', { class: 'help', text: 'A test reads as a band: ±70 for a module or section, ±100 for the diagnostic. The status uses your last 3 tests.' }));
    cards.push(traj);
    // what your time bought (L18)
    if ((d.bought || []).length) {
      const rows = h('div', { class: 'pg-rows' });
      for (const b of d.bought.slice().sort((x, y) => y.minutes - x.minutes)) {
        const acc = s => (s && s.of ? `${Math.round(s.right / s.of * 100)}%` : 'new');
        const r = h('div', { class: 'pg-row' }, h('span', { class: 'h3', text: tn(b.topic) }),
          h('span', { class: 'meta', text: `${UI.dur(b.minutes)}` }),
          h('span', { class: 'meta', text: [`${acc(b.before)} → ${acc(b.after)} first try`, b.fixed ? `${b.fixed} fixed` : null, checkText(b.check), b.claimed ? `≈ +${b.claimed}` : null].filter(Boolean).join(' · ') }));
        if (b.not_moving) r.append(h('p', { class: 'meta', style: 'grid-column: 1 / -1; color: var(--ink)', text: `Not moving · ${acc(b.before)} → ${acc(b.after)} over 20 answers each · ${UI.dur(b.minutes_14d)} in 14 days` }),
          h('div', { class: 'row', style: 'grid-column: 1 / -1' }, h('button', { type: 'button', class: 'btn sm', text: 'Learn it · untimed', onclick: e => start(e.currentTarget, { source: 'learn', topics: [b.topic], example: true, count: 3 }) }),
            h('a', { class: 'quiet', href: `/review/?topic=${encodeURIComponent(b.topic)}`, text: 'See its misses' })));
        rows.append(r);
      }
      cards.push(Object.assign(card('What your time bought', null, rows), { className: 'card wide' }));
    }
    // why you lose points (T7)
    const cz = d.causes;
    if (cz && cz.total) {
      const NAME = { trap: 'Named traps', slip: 'Slips', clock: 'Ran out of time', entry: 'Grid-in entry', gap: 'Not learned yet', misread: 'Misread', changed: 'Changed a right answer' };
      const segs = Object.entries(cz.by || {}).filter(([, n]) => n).map(([k, n]) => ({ key: k, label: NAME[k] || k, value: n }));
      const box = h('div');
      UI.stackBar(box, segs, { noun: 'misses', label: 'Why you lose points' });
      cards.push(card('Why you lose points', `${pl(cz.total, 'miss', 'misses')} since ${D(a.start)}`, box));
    }
    // ready on every skill? (L2)
    const cov = d.coverage && d.coverage.math;
    if (cov && (cov.cells || []).length) cards.push(coverageCard(cov, d));
    // domains: by points or by accuracy (L18, L21)
    cards.push(domainCard(d, () => draw(host, ctx)));
    // the split: time against points (T17)
    if ((d.split_domain || []).some(x => x.minutes_planned)) {
      const rows = h('div', { class: 'pg-rows' });
      for (const x of d.split_domain) rows.append(h('div', { class: 'pg-row' }, h('span', { text: x.domain }),
        h('span', { class: 'meta', text: `${Math.round(x.time_share * 100)}% of your time${x.points_share ? ` · ${Math.round(x.points_share * 100)}% of your points` : ''}` })));
      const kinds = Object.entries(st.split_planned || {}).filter(([, m]) => m > 0);
      const box = h('div', { style: 'margin-top: 12px' });
      const LBL = { focus: 'Focus', fix: 'Mistakes', recheck: 'Warm-up', test: 'Tests', learn: 'Learn it', check: 'Checks', map: 'Map', words: 'Words', custom: 'Your own', pace: 'Pace', habit: 'Habit', sweep: 'Sweep' };
      if (kinds.length) UI.stackBar(box, kinds.map(([k, m]) => ({ key: k, label: LBL[k] || k, value: Math.round(m) })), { unit: 'min', label: 'Planned minutes by task' });
      cards.push(card('How the plan splits your time', null, rows, box));
    }
    // all 19 skills, open (L18: 19 rows on load)
    cards.push(skillsCard(d));
    // study time per day (StudyTimeChart)
    const past = d.days.filter(x => x.date <= t && (x.minutes || x.minutes_done));
    const sc = card('Study time per day', past.length ? `${UI.dur(past.reduce((s, x) => s + (x.minutes_done || 0), 0))} studied of ${UI.dur(past.reduce((s, x) => s + (x.minutes || 0), 0))} planned` : null);
    const box = h('div');
    sc.append(box);
    if (past.some(x => x.minutes_done)) UI.barChart(box, past.slice(-28).map(x => ({ day: x.date, studied: Math.round(x.minutes_done || 0), planned: x.minutes, today: x.date === t,
      tip: `${D(x.date, 'long')} · ${Math.round(x.minutes_done || 0)} of ${x.minutes} min${x.questions ? ` · ${x.questions} questions` : ''}` })),
    { series: [{ key: 'studied', label: 'Studied', look: 'ink' }], unit: 'min', labels: 'date', height: 180, label: 'Study time per day', onPick: row => ctx.pick(row.day) });
    else box.append(h('p', { class: 'soft', text: 'Nothing logged yet' }));
    sc.className = 'card wide';
    cards.push(sc);
    // checks (L3)
    const checks = (d.checks || []).filter(x => x.before);
    if (checks.length) {
      const rows = h('div', { class: 'pg-rows' });
      for (const x of checks) rows.append(h('div', { class: 'pg-row' }, h('span', { class: 'h3', text: tn(x.topic) }),
        h('span', { class: 'tag' + (x.result === 'passed' ? ' or' : ''), text: x.result ? { passed: 'Passed', again: 'Again', learn: 'Learn first' }[x.result] : 'After to come' }),
        h('span', { class: 'meta', text: `before ${x.before.right}/${x.before.of}${x.after ? ` → after ${x.after.right}/${x.after.of} on the same question types` : ''}${x.recent && x.recent.of ? ` · ${x.recent.right} of your last ${x.recent.of}` : ''}` })));
      cards.push(card('Checks', null, rows));
    }
    // weeks (L16)
    const weeks = (d.weeks || []).filter(w => w.to < t && w.tasks_planned);
    if (weeks.length) {
      const rows = h('div', { class: 'pg-rows' });
      for (const w of weeks.slice().reverse()) {
        const days = d.days.filter(x => x.date >= w.from && x.date <= w.to);
        const study = days.filter(x => ['practice', 'test'].includes(x.kind));
        const done = study.filter(x => ['done', 'partial', 'made_up'].includes(x.status)).length;
        rows.append(h('div', { class: 'pg-row' }, h('span', { text: `Week ${w.n} · ${D(w.from)}–${D(w.to)}` }), h('span', { class: 'meta', text: `${w.tasks_done}/${w.tasks_planned} tasks` }),
          h('span', { class: 'meta', text: `days ${done} of ${study.length} · ${UI.dur(days.reduce((s, x) => s + (x.minutes_done || 0), 0))} · ${pl(days.reduce((s, x) => s + (x.questions || 0), 0), 'question')}` })));
      }
      cards.push(card('Weeks', null, rows));
    }
    // pace and calibration (U7, P7)
    const cal = d.calibration, sp = d.skill_pace;
    const paceKids = [];
    if (sp && sp.forecast && sp.forecast.seconds && sp.skills && Object.keys(sp.skills).length) paceKids.push(h('p', { class: 'line-t', text: `A module at your pace takes ${UI.mmss(sp.forecast.seconds)} of ${UI.mmss(sp.forecast.limit)}` }));
    const slow = sp && sp.quadrants ? (sp.quadrants.slow_right || []).slice(0, 3) : [];
    slow.forEach(x => paceKids.push(h('div', { class: 'row' }, h('span', { class: 'line-t', text: tn(x.topic || x) }),
      h('button', { type: 'button', class: 'btn sm', text: 'Speed drill · 8', onclick: e => start(e.currentTarget, { topics: [x.topic || x], count: 8, timing: 'pace', source: 'pace' }) }))));
    const tagged = cal ? ['sure', 'unsure', 'guess'].reduce((s, k) => s + ((cal[k] || {}).of || 0), 0) : 0;
    if (tagged >= 20) paceKids.push(h('p', { class: 'line-t', text: ['sure', 'unsure', 'guess'].filter(k => cal[k] && cal[k].of).map(k => `${{ sure: 'Sure', unsure: 'Unsure', guess: 'Guess' }[k]} ${Math.round(cal[k].accuracy * 100)}% right (${cal[k].of})`).join(' · ') }));
    if (paceKids.length) cards.push(card('Pace and how sure you were', null, ...paceKids, h('a', { class: 'quiet', href: '/me/#pace', text: 'Every skill ›' })));
    // changes (L15)
    const counts = d.changes_counts || (d.changes && d.changes.counts) || {};
    const total = Object.values(counts).reduce((s, n) => s + n, 0);
    if (total) {
      const ch = card('Changes', null, h('p', { class: 'line-t', text: `Your plan changed ${pl(total, 'time')}${[['auto', 'from your answers'], ['mistake', 'from new mistakes'], ['edit', 'from your edits'], ['sitting', 'from tests']].filter(([k]) => counts[k]).map(([k, w]) => ` · ${counts[k]} ${w}`).join('')}` }));
      ch.id = 'changes';
      const list = h('div', { class: 'pg-rows' });
      ch.append(list);
      const more = h('button', { type: 'button', class: 'btn sm', text: 'Show the list' });
      let before = null;
      more.addEventListener('click', async () => {
        more.setAttribute('aria-busy', 'true');
        try {
          const r = await ctx.api(`/plan/${encodeURIComponent(a.id)}/changes${before ? `?before=${before}` : ''}`);
          const items = r.events || r.items || r.changes || [];
          items.forEach(e => list.append(h('div', { class: 'pg-row' }, h('span', { text: UI.planPage ? UI.planPage.pretty(e.text) : e.text }), h('span', { class: 'meta', text: D(String(e.at || e.day).slice(0, 10)) }))));
          before = items.length ? items[items.length - 1].id : null;
          more.textContent = 'Show 20 more';
          if (!before || items.length < 20) more.remove();
        } catch (_) { more.textContent = 'Couldn’t load. Try again'; }
        finally { more.removeAttribute('aria-busy'); }
      });
      ch.append(more);
      ch.className = 'card wide';
      cards.push(ch);
    }
    host.replaceChildren(h('div', { class: 'pg' }, cards));
    if (location.hash === '#changes') { const el = host.querySelector('#changes'); if (el) el.scrollIntoView(); }
  }
  // a check's before and after on the same question types (L3)
  function checkText(x) {
    if (!x) return null;
    if (typeof x === 'string') return x;
    const f = s => (s && s.of ? `${s.right}/${s.of}` : null);
    return f(x.before) ? `check ${f(x.before)}${f(x.after) ? ` → ${f(x.after)}` : ''}` : null;
  }
  function nextTest(d) {
    const t = today(), x = d.days.find(y => y.date >= t && y.kind === 'test');
    const tk = x && x.tasks.find(k => k.kind === 'test' && !['done', 'marked', 'made_up'].includes(k.status));
    return tk ? { t: tk, date: x.date } : null;
  }
  async function start(b, body) {
    b.setAttribute('aria-busy', 'true');
    try { const r = await UI.api('/drill', { method: 'POST', body }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
    catch (_) { UI.toast('Couldn’t start. Try again.'); b.removeAttribute('aria-busy'); }
  }
  function checkpointCard(cp, ctx) {
    const slots = cp.slots || [];
    const n = k => slots.filter(s => s.change === k).length;
    const GL = { fixed: '✗→✓', held: '✓→✓', slipped: '✓→✗', still_missed: '✗→✗' };
    const c = card(`Checkpoint ${cp.n || ''}`.trim(), cp.baseline && cp.checkpoint ? `${cp.baseline.right}/${slots.length} → ${cp.checkpoint.right}/${slots.length}` : null);
    const strip = h('div', { class: 'pl-strip19', style: 'grid-template-columns: repeat(11, minmax(0, 1fr))', role: 'group', 'aria-label': 'Slots of module 1' },
      slots.map((s, i) => h('i', { 'data-on': s.change === 'fixed' || s.change === 'held' ? '' : null, title: `${i + 1} · ${tn(s.topic)} · ${s.change.replace('_', ' ')}${s.practised ? ' · practised' : ''}`, text: GL[s.change] ? GL[s.change][2] : '' })));
    c.append(strip, h('p', { class: 'meta', style: 'margin-top: 8px', text: `fixed ${n('fixed')} · held ${n('held')} · slipped ${n('slipped')} · still missed ${n('still_missed')}` }));
    const redo = slots.filter(s => s.change === 'slipped' || s.change === 'still_missed');
    if (redo.length && cp.session) c.append(h('button', { type: 'button', class: 'pill sm', style: 'margin-top: 10px', text: `Fix these ${redo.length}`,
      onclick: e => start(e.currentTarget, { from_session: cp.session, only: redo.map(s => s.qid), each: 2, sibling: true, source: 'twin', task: `${today()}:extra` }) }));
    c.className = 'card wide';
    return { el: c, ctx };
  }
  function coverageCard(cov, d) {
    const cells = cov.cells;
    const cnt = cov.counts || {};
    const needed = cells.filter(x => x.needed);
    const proven = needed.filter(x => x.state === 'proven').length;
    const head = [`Proven ${proven} of ${needed.length}`, cnt.shaky ? `shaky ${cnt.shaky}` : null, cnt.untested ? `untested ${cnt.untested}` : null, cnt.unplanned ? `${cnt.unplanned} not planned before Final` : null].filter(Boolean).join(' · ');
    const grid = h('div', { class: 'pg-grid', role: 'grid', 'aria-label': 'Every skill by tier' });
    grid.append(h('span', { role: 'columnheader', class: 'hd', style: 'text-align: left', text: 'Skill' }), ...['Easy', 'Medium', 'Hard'].map(x => h('span', { role: 'columnheader', class: 'hd', text: x })));
    const GLY = { proven: '✓', shaky: '~', untested: '·', na: '' };
    for (const dn of DOMAINS) {
      grid.append(h('span', { class: 'dm', text: dn }));
      for (const tp of UI.TOPICS.filter(x => x.domain === dn)) {
        grid.append(h('span', { role: 'rowheader', text: tp.short }));
        for (const tier of ['easy', 'medium', 'hard']) {
          const x = cells.find(y => y.topic === tp.slug && y.tier === tier) || { state: 'na' };
          const label = `${tp.short}, ${tier}: ${x.state}${x.n ? `, ${x.right} of ${x.n}` : ''}${x.needed ? '' : ', not needed'}${x.next ? `, next ${D(x.next)}` : x.needed && x.state !== 'proven' && !x.planned ? ', not planned before Final' : ''}`;
          const b = h('button', { type: 'button', role: 'gridcell', class: 'pg-cell', 'data-s': x.state, 'data-need': x.needed ? '1' : '0', 'aria-label': label, title: label, text: GLY[x.state] || '', disabled: x.state === 'na' || null });
          if (x.state !== 'na') b.addEventListener('click', e => start(e.currentTarget, { topics: [tp.slug], tiers: [tier], count: 5, source: 'plan' }));
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
    const c = card('Ready on every skill?', head, grid);
    if (cov.window_days) c.append(h('p', { class: 'help', text: `Every skill at least once in ${cov.window_days} days at this time. A cell starts 5 questions on that skill and tier.` }));
    return c;
  }
  function domainCard(d, redraw) {
    const gains = d.points && d.points.math && d.points.math.skills;
    const by = domBy || (gains ? 'points' : 'accuracy');
    const seg = h('div');
    UI.seg(seg, [{ value: 'points', label: 'By points', disabled: !gains, why: 'after 30 answers' }, { value: 'accuracy', label: 'By accuracy' }], { value: by, label: 'Order', onChange: v => { domBy = v; redraw(); } });
    const gainOf = dn => (gains || []).filter(x => (UI.TOPIC[x.topic] || {}).domain === dn).reduce((s, x) => s + Math.max(0, x.gain || 0), 0);
    const rows = (d.domains || []).slice().sort((x, y) => by === 'points' ? gainOf(y.domain) - gainOf(x.domain) : (x.answered ? x.right / x.answered : 2) - (y.answered ? y.right / y.answered : 2));
    const list = h('div', { class: 'pg-rows' });
    for (const x of rows) {
      const r = h('a', { class: 'pg-row', href: `/practice/?topics=${UI.TOPICS.filter(t => t.domain === x.domain).map(t => t.slug).join(',')}`, style: 'color: inherit; text-decoration: none' },
        h('span', { class: 'h3' }, x.domain, x.state !== 'normal' ? h('span', { class: x.state === 'focus' ? 'tag or' : 'tag line', style: 'margin-left: 8px', text: x.state === 'focus' ? 'Focus' : 'Strong' }) : null),
        h('span', { class: 'meta', text: x.answered ? `${Math.round(x.right / x.answered * 100)}% right · ${UI.num(x.answered)} answered` : 'Not started' }));
      const m = h('div', { style: 'grid-column: 1 / -1' });
      UI.meter(m, { label: '', value: Math.round((x.mastery || 0) * 100), max: 100, text: [`planned ${Math.round((x.share_planned || 0) * 100)}%`, x.share_done ? `done ${Math.round(x.share_done * 100)}%` : null, gainOf(x.domain) >= 5 ? `≈ +${Math.round(gainOf(x.domain))} on the table` : null].filter(Boolean).join(' · '), ink: true, tick: Math.round((x.start_mastery || 0) * 100) });
      r.append(m);
      list.append(r);
    }
    const c = card('Accuracy by domain', null, seg, list);
    // the R&W section (L21)
    const rw = (d.rw_domains || []);
    const cfg = d.active.cfg;
    if (rw.some(x => x.of || x.minutes_planned) || (cfg.rw_current !== null && cfg.rw_current !== undefined)) {
      const box = h('div', { class: 'pg-rows' });
      for (const x of rw) box.append(h('div', { class: 'pg-row' }, h('span', {}, x.domain, x.state !== 'normal' ? h('span', { class: 'tag', style: 'margin-left: 8px', text: x.state === 'focus' ? 'Focus' : 'Strong' }) : null),
        h('span', { class: 'meta', text: x.of ? `missed ${x.missed} of ${x.of} · ${Math.round(x.missed / x.of * 100)}%` : 'no results yet' }),
        x.minutes_planned ? h('span', { class: 'meta', text: `${Math.round(x.minutes_done)} of ${Math.round(x.minutes_planned)} min` }) : null));
      c.append(h('p', { class: 'label', style: 'margin: 14px 0 0', text: 'Reading & Writing' }), box);
    }
    return c;
  }
  function skillsCard(d) {
    const gains = Object.fromEntries(((d.points && d.points.math && d.points.math.skills) || []).map(x => [x.topic, x.gain]));
    const rows = (d.skills || []).map(s => ({ ...s, name: tn(s.topic), acc: s.answered ? s.right / s.answered : null, gain: gains[s.topic] ?? null }));
    const box = h('div');
    const cols = [
      { key: 'name', label: 'Skill', render: r => h('a', { href: `/practice/?topics=${r.topic}`, text: r.name }) },
      { key: 'answered', label: 'Answered', num: true },
      { key: 'acc', label: '% right', num: true, render: r => (r.acc === null ? '—' : `${Math.round(r.acc * 100)}%`) },
      { key: 'traps', label: 'Open', num: true, render: r => (r.traps ? String(r.traps) : '') },
      { key: 'gain', label: '≈ +', num: true, render: r => (r.gain >= 5 ? `+${Math.round(r.gain)}` : '') },
      { key: 'last', label: 'Last worked', render: r => (r.last ? D(String(r.last).slice(0, 10)) : '') },
    ];
    const def = Object.keys(gains).length ? 'gain' : 'acc';
    UI.table(box, cols, rows, { sort: sortBy || { key: def, dir: def === 'gain' ? 'desc' : 'asc' }, onSort: s => { sortBy = s; }, sortable: true, label: 'All 19 skills', compact: true });
    const c = card('All 19 skills', null, box, h('p', { class: 'help' }, h('a', { href: '/results/', text: 'Every result ›' })));
    c.className = 'card wide';
    return c;
  }

  Object.assign(UI, { planProgress });
})();
