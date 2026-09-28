/* ============================================================================
   SAT Freshman -- Tests, /tests/ (spec 3.4 section 2; tests.md X1, X2, X13-X18, X20, X23)

   One GET /api/tests (painted from the cached copy first) fills the page; the sittings list
   reads GET /api/history?all=1 (S6's rows, sitting_row's shape; the old shape is read too).
     #score    T1 the estimate, its facts, the gate, and What moves this band (X15)
     #next     T2 Up next, in §3.1 item 11's order
     #cycle    Test → Fix → Prove (X16)            #live   T3 In progress
     #habits   How you take tests (X17)            #kinds  T4 New test
     #papers   T5 Papers with their filters (X20)  #sittings  T6 Your sittings, filters, CSV
   Every Start is one tap into the lobby (/test/?s=ID); Options opens the start sheet (start.js).
   ========================================================================== */
(() => {
  const h = UI.h, $ = s => document.querySelector(s);
  const url = new URLSearchParams(location.search);
  const api = (p, o) => UI.api(p, o);
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  const mmss = s => UI.mmss(Math.max(0, Math.round(s || 0)));
  const plural = (n, one, many) => `${UI.num ? UI.num(n) : n} ${n === 1 ? one : many || one + 's'}`;
  const num = n => (UI.num ? UI.num(n) : String(n));
  const day = d => (d ? UI.date(d, 'short') : '');
  const band = e => (e && e.low !== null && e.low !== undefined ? `${Math.round(e.low)}–${Math.round(e.high)}` : null);
  const icon = (name, size = 16) => h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.svg(UI.ICON[name] || UI.ICON.dot || '', size) });
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const S = window.TestStart;
  let D = null;                 // /api/tests
  let rows = [];                // the sittings, newest first
  let rowsState = 'loading';    // loading | ok | error
  let shown = 20;
  let sitBar = null, paperBar = null, papersAll = false;
  let picked = [], cmpBar = null, onlyIds = null, sitPaint = null;     // X18's two ticked rows; X17's "Which sittings?"
  let habitsView = { last: 'all', scope: 'timed' };

  UI.shell({ page: 'tests', now: false });

  /* ---------------- actions shared by every card */
  async function drill(body, btn) {
    if (btn) btn.setAttribute('aria-busy', 'true');
    try { const r = await api('/drill', { method: 'POST', body }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
    catch (e) { if (btn) btn.removeAttribute('aria-busy'); toast(e.status === 409 ? (e.data && e.data.detail && e.data.detail.reason) || e.message : 'Couldn’t start that. Try again.'); }
  }
  const start = (body, btn) => S.go(body, btn).catch(() => {});
  const lobby = id => `/test/?s=${encodeURIComponent(id)}`;
  const report = (id, q) => `/results/report/?id=${encodeURIComponent(id)}${q ? `&q=${q}` : ''}`;
  function action(a, btn, ctx = {}) {
    if (!a) return null;
    if (a.preset) return S.preset(a.preset, btn);
    if (a.kind || (a.body && a.body.kind)) return start(a.body || a, btn);
    if (a.body) return drill(a.body, btn);
    if (a.templates) return drill({ templates: a.templates, count: 5, source: 'coach' }, btn);
    if (a.href) { location.href = a.href; return null; }
    if (ctx.fallback) return ctx.fallback();
    return null;
  }
  const btn = (label, o = {}) => {
    const b = h(o.href ? 'a' : 'button', { class: o.cls || 'btn', type: o.href ? null : 'button', href: o.href || null, text: label, id: o.id || null, 'aria-label': o.aria || null });
    if (o.run) b.addEventListener('click', () => o.run(b));
    return b;
  };

  /* ---------------- T1: the estimated score (#score) */
  const CONF = { high: 'High', medium: 'Medium', low: 'Low' };
  const CAUSE = { trap: 'Traps', clock: 'Clock', slip: 'Slips', entry: 'Entry', gap: 'Gaps', changed: 'Changed answers' };
  function sourceLine(latest) {
    const r = rows.find(x => x.id === latest.id);
    const name = r ? `${r.kind_label}${r.number ? ` #${r.number}` : ''}` : (UI.KIND[latest.kind] || 'Sitting');
    return [`From ${name}`, day(latest.at), latest.route === 'upper' ? 'harder module 2' : latest.route === 'lower' ? 'easier module 2 · 580 cap' : null,
      /extended|time and a half|double/.test(latest.why || '') ? 'extended time' : null].filter(Boolean).join(' · ');
  }
  function headline(e) {
    const L = e.latest, P = e.previous, t = D.target;
    if (!L) return null;
    const bits = [];
    if (P) {
      const d = Math.round(((L.mid ?? (L.low + L.high) / 2) - (P.mid ?? (P.low + P.high) / 2)) / 10) * 10;
      bits.push(Math.abs(d) < 20 ? `Level with ${day(P.at)}` : d > 0 ? `Up ${d} since ${day(P.at)}` : `Down ${-d} since ${day(P.at)}`);
    } else bits.push('Your first estimate');
    if (t) {
      const mid = L.mid ?? (L.low + L.high) / 2;
      bits.push(mid >= t ? `At your ${t} target` : `${Math.round((t - mid) / 10) * 10} short of your ${t} target`);
    }
    return bits.join(' · ');
  }
  function scoreCard() {
    const host = $('#score');
    host.replaceChildren();
    const e = D.estimate || {};
    const L = e.latest;
    const conf = e.confidence || {};
    const left = h('div', { class: 'sc-left' });
    const chip = h('span', { class: `conf ${L ? conf.level : 'none'}`, text: L ? CONF[conf.level] || 'Low' : 'No data' });
    left.append(h('div', { class: 'sc-k' }, h('h2', { class: 'k', id: 'scoreH', text: 'Estimated Math score' }), chip));
    left.append(h('p', { class: 'num sc-band', text: band(L) || '—' }));
    if (L) {
      left.append(h('p', { class: 'sc-head', text: headline(e) }), h('p', { class: 'meta', text: sourceLine(L) }));
      const reason = h('div', { class: 'sc-reason' }, h('p', { class: 'help', text: conf.reason || '' }));
      if (conf.level === 'low') reason.append(btn('Full section · 70 min', { cls: 'btn sm', run: b => start({ kind: 'section' }, b) }));
      else if (conf.level === 'medium') reason.append(btn('One more section makes this High · Start', { cls: 'btn sm', run: b => start({ kind: 'section' }, b) }));
      left.append(reason);
    } else {
      left.append(h('p', { class: 'sc-empty', text: 'No estimate yet. A full section gives a band about 140 points wide; one module or the diagnostic, about 200.' }));
    }
    const right = h('div', { class: 'sc-right' });
    const chart = h('div', { class: 'sc-chart' });
    right.append(chart);
    const pts = rows.filter(r => r.estimate && r.estimate.low !== null && r.estimate.low !== undefined).slice(0, 8).reverse()
      .map(r => ({ id: r.id, at: r.finished || r.started, low: r.estimate.low, high: r.estimate.high, kind: r.paper ? 'paper' : r.kind === 'section' ? 'mock' : r.kind,
        label: `${r.kind_label}${r.number ? ' #' + r.number : ''}`, href: report(r.id) }));
    if (UI.bandChart) {
      try {
        UI.bandChart(chart, pts, { height: innerWidth < 760 ? 110 : 120, target: D.target || undefined, min: 200, max: 800, label: 'Your last scored sittings' });
      } catch (_) {}
    }
    if (L) {
      const facts = h('dl', { class: 'sc-facts' });
      const fact = (k, v, o = {}) => { if (v === null || v === undefined || v === '') return; const dd = h('dd', {}, typeof v === 'string' ? h(o.href ? 'a' : 'span', { href: o.href || null, text: v }) : v); facts.append(h('div', { class: 'sc-fact' }, h('dt', { class: 'k', text: k }), dd)); };
      fact('Best', band(e.best));
      if (e.combined) fact('Combined, last 3 sections', band(e.combined));
      if (e.range && e.range.low !== null && e.range.low !== undefined && e.range.low !== e.range.high) fact('Range of your sittings', band(e.range));
      const g = D.gate || {};
      if (g.sections) {
        const gv = h('span', { class: 'sc-gate' }, h('span', { text: `routed up ${g.up} of ${g.sections}` }));
        if (UI.spark && (g.margins || []).length > 1) { const sp = h('span', { class: 'sc-spark' }); UI.spark(sp, g.margins.slice(-6), { label: 'Module 1 margins to the harder module 2', w: 72, h: 20, ref: 0 }); gv.append(sp); }
        fact('Gate', gv);
      }
      fact('Target', D.target ? `${D.target} (Plan)` : 'Set a target', { href: '/plan/' });
      fact('Exam', D.exam ? `${day(D.exam.date)} · ${plural(D.exam.days, 'day')}` : 'Set a date', { href: '/plan/' });
      right.append(facts);
      const c = e.counted || {};
      const parts = [c.sections && plural(c.sections, 'section'), c.modules && plural(c.modules, 'module'), c.diagnostics && plural(c.diagnostics, 'diagnostic')].filter(Boolean);
      right.append(h('p', { class: 'meta', text: `Counted: ${plural(c.sittings || 0, 'sitting')}${parts.length ? ' · ' + parts.join(', ') : ''}${c.ranked ? ` · ${c.ranked} ranked` : ''}` }));
    }
    const top = h('div', { class: 'sc-top' }, left, right);
    host.append(top);
    if (!L) return;

    // the gate's warning, the total, the projection, growth and calibration (X14, X15)
    const more = h('div', { class: 'sc-lines' });
    const g = D.gate || {};
    if (g.lower_recent) {
      const p = h('p', { class: 'sc-line' }, h('span', { text: 'Your last sections routed lower, so they top out at 580. One more right in module 1 lifts the cap.' }));
      if (g.protect && g.protect.body) p.append(btn(`Protect the gate · ${g.protect.body.count || 12}`, { cls: 'btn sm', run: b => drill(g.protect.body, b) }));
      more.append(p);
    }
    const T = D.total;
    if (T && T.low !== undefined && T.low !== null) more.append(h('p', { class: 'sc-line', text: `Total ${T.low}–${T.high}${T.rw ? ` · with your R&W ${T.rw}${T.rw_day || T.at ? ` (entered ${day(T.rw_day || T.at)})` : ''}` : ''}` }));
    else more.append(h('p', { class: 'sc-line' }, h('span', { class: 'meta', text: 'Math only.' }),
      btn('Add your R&W score', { cls: 'quiet', run: () => (UI.addScore ? UI.addScore({ rw: true }) : (location.href = '/me/#scores')) })));
    const P = D.projection;
    if (P) more.append(h('p', { class: 'sc-line', text: P.verdict || P.label || (P.low ? `On pace: about ${P.low}–${P.high}${P.to ? ` on ${day(P.to)}` : ''}${D.target ? ` · target ${D.target}` : ''}` : '') }));
    const G = D.growth;
    if (G && G.delta !== undefined) more.append(h('p', { class: 'sc-line', text: `Since your first section: ${G.delta >= 0 ? '+' : '−'}${Math.abs(G.delta)} · more than ${Math.round((G.pct ?? G.percentile ?? 0) * (G.pct > 1 ? 1 : 100))}% of students who started near ${G.start} (${plural(G.n, 'student')})` }));
    const C = D.calibration;
    if (C && C.latest) {
      const x = C.latest;
      more.append(h('p', { class: 'sc-line', text: `Your ${x.source === 'official' ? 'official SAT' : 'Bluebook test'}: ${x.math ?? x.score} (${day(x.day)}) · our estimate then: ${band(x.estimate || x)} · ${x.inside ? 'inside' : 'outside'}` }));
    }
    host.append(more);
    host.append(movesBand());
  }
  function movesBand() {
    const L = D.levers || {};
    const box = h('section', { class: 'sc-moves', 'aria-labelledby': 'movesH' }, h('h3', { class: 'h2', id: 'movesH', text: 'What moves this band' }));
    const causes = (L.causes || []).filter(c => c.n);
    if (!causes.length && !(L.skills || []).length) {
      box.append(h('p', { class: 'help', text: 'Sit a full section to see where your points went.' }), btn('Full section · 70 min', { cls: 'pill sm', run: b => start({ kind: 'section' }, b) }));
      return box;
    }
    if (causes.length) {
      box.append(h('p', { class: 'k', text: `Where the points went · last ${plural(L.sittings || 3, 'sitting')}` }));
      const list = h('ul', { class: 'mv-rows' });
      causes.forEach(c => {
        const li = h('li', { class: 'mv-row' }, h('span', { class: 'mv-name', text: CAUSE[c.cause] || c.cause }),
          h('span', { class: 'mv-n', text: plural(c.n, 'question') }), h('span', { class: 'mv-pts mono', text: c.pts ? `≈ +${c.pts}` : '' }));
        const a = c.action;
        if (a) {
          const label = a.label || 'Start';
          li.append(btn(label, { cls: 'btn sm', run: b => action(a, b, { fallback: () => { if (c.cause === 'changed' && rows[0]) location.href = report(rows[0].id) + '&filter=changed'; } }) }));
        } else li.append(h('span'));
        list.append(li);
      });
      box.append(list);
    }
    if (L.route && (L.route.text || L.route.pts)) box.append(h('p', { class: 'sc-line', text: L.route.text || `One more right in module 1 would have lifted the 580 cap · up to +${L.route.pts}` }));
    if ((L.skills || []).length && UI.skillRow) {
      box.append(h('div', { class: 'mv-skh' }, h('p', { class: 'k', text: 'Skills worth the most' }), h('a', { class: 'quiet', href: '/#gain', text: 'All skills' })));
      const sk = h('div', { class: 'mv-skills' });
      L.skills.slice(0, 3).forEach(s => UI.skillRow(sk, Object.assign({ answered: s.evidence, right: Math.round((s.accuracy || 0) * (s.evidence || 0)), mastery: s.mastery ?? s.accuracy }, s), { practise: { count: 10 } }));
      box.append(sk);
    }
    if (L.both && L.both.pts && causes.length > 1) {
      const t = D.target, bb = L.both.band;
      box.append(h('p', { class: 'sc-line', text: `${causes.slice(0, 2).map(c => (CAUSE[c.cause] || c.cause).toLowerCase()).join(' and ').replace(/^./, x => x.toUpperCase())} together ≈ +${L.both.pts}${t && bb && bb.high >= t ? ` · your ${t} target is inside` : ''}` }));
    }
    box.append(h('p', { class: 'help', text: 'Worked out by re-marking your own sittings with those questions right.' }));
    return box;
  }

  /* ---------------- T2: Up next (#next) */
  function nextCard() {
    const host = $('#next');
    host.replaceChildren();
    const u = D.up_next || { kind: 'section' };
    const live = (D.in_progress || []).find(r => r.id === u.session);
    const papers = D.papers || [];
    const weekly = papers.find(p => p.newest);
    const lastDays = rows.find(r => r.status === 'completed') ? Math.floor((Date.now() - new Date(rows.find(r => r.status === 'completed').finished).getTime()) / 864e5) : null;
    let t = 'Full section', meta = lastDays !== null ? (lastDays ? `Your last was ${plural(lastDays, 'day')} ago` : 'Your last was today') : '44 questions · 70 min', go = b => start({ kind: 'section' }, b), label = 'Start', alt = null;
    switch (u.kind) {
      case 'resume':
        if (live) { t = `Finish ${live.kind_label}${live.number ? ' #' + live.number : ''}`; meta = stateLine(live); label = live.status === 'not_begun' ? 'Begin' : live.status === 'timed_out' ? 'Continue' : 'Resume'; go = () => { location.href = live.href || lobby(live.id); }; }
        break;
      case 'pressure': {
        const r = rows.find(x => x.id === u.session);
        t = 'Pressure check'; meta = `${r ? `${r.kind_label}${r.number ? ' #' + r.number : ''} · ` : ''}open until you open its report`; label = 'Start';
        go = async b => { b.setAttribute('aria-busy', 'true'); try { const x = await api(`/session/${encodeURIComponent(u.session)}/pressure`, { method: 'POST' }); location.href = `/practice/session/?id=${encodeURIComponent(x.id)}`; } catch (e) { b.removeAttribute('aria-busy'); toast(e.message); } };
        break;
      }
      case 'traps':
        if (u.reason === 'prove') { const c = D.cycle || {}; t = `Prove ${c.label || 'your fixes'}${c.number ? ' #' + c.number : ''}`; meta = 'Due today · a Trap test from its misses'; go = b => start(u.body, b); }
        else { const k = kindOf('traps'); t = 'Trap test'; meta = `${k && k.ready ? plural(k.ready, 'trap') + ' ready · ' : ''}do you still take them?`; go = b => start({ kind: 'custom', custom: { source: 'traps', traps: 'all', neutral: 0.25 } }, b); }
        break;
      case 'diagnostic': t = 'Start with the diagnostic'; meta = '20 questions · 32 min · all four domains evenly'; go = b => start({ kind: 'diagnostic' }, b); break;
      case 'contest': t = 'The Season Final is open'; meta = 'The dress rehearsal: twins, ranked, this weekend'; label = 'Go to the Final'; go = () => { location.href = '/compete/'; }; break;
      case 'paper': {
        const p = papers.find(x => x.n === u.paper) || weekly || {};
        t = p.source && String(p.source).startsWith('final-') ? `${p.label}` : `New this week: Paper #${p.n}`;
        meta = [p.sat_by ? `Sat by ${num(p.sat_by)} so far` : null, `${p.questions || 44} questions · 70 min`].filter(Boolean).join(' · ');
        go = b => start({ kind: 'paper', paper: p.n }, b);
        break;
      }
      case 'trainer': t = 'Route-up trainer'; meta = 'Your last sections routed lower · 22 questions · 35 min'; go = b => start({ kind: 'module', module: 'm1', trainer: 'route', conditions: 'test_day' }, b); break;
      case 'module':
        if (u.preset === 'pacing') { t = 'Pacing practice'; meta = 'Your points leak to time: module 1 in Training with a tight clock'; go = b => S.preset('pacing', b); }
        else { t = u.reason === 'plan' ? 'Today’s test: module' : 'Module 1'; meta = '22 questions · 35 min'; go = b => (u.preset ? S.preset(u.preset, b) : start({ kind: 'module', module: 'm1' }, b)); }
        break;
      case 'section':
        if (u.reason === 'plan') {
          t = 'Today’s test: full section'; meta = '44 questions · 70 min'; go = b => S.preset(u.preset || 'like_test_day', b);
          if (weekly && weekly.yours && weekly.yours.status === 'not_sat') alt = btn(`Sit this week’s Paper #${weekly.n} instead`, { cls: 'quiet', run: b => start({ kind: 'paper', paper: weekly.n }, b) });
        }
        break;
      default: break;
    }
    host.append(h('p', { class: 'k', text: 'Up next' }), h('h2', { class: 'nx-title', text: t }), h('p', { class: 'meta', text: meta }));
    const acts = h('div', { class: 'nx-acts' }, btn(label, { cls: 'pill', id: 'nextGo', run: go }));
    if (alt) acts.append(alt);
    host.append(acts);
    const plan = UI.shellData && UI.shellData() && UI.shellData().plan;
    if (!plan) host.append(h('a', { class: 'quiet nx-plan', href: '/plan/', text: 'Plan your test days' }));
  }

  /* ---------------- T3b: Test → Fix → Prove (#cycle) */
  function cycleCard() {
    const host = $('#cycle');
    const c = D.cycle;
    host.hidden = !c;
    if (!c) return;
    host.replaceChildren();
    const today = new Date().toISOString().slice(0, 10);
    const seg = (name, state, act) => h('li', { class: 'cy-seg' + (state.done ? ' done' : '') }, h('i', { 'aria-hidden': 'true' }), h('b', { text: name }), h('span', { class: 'meta', text: state.text }), act || null);
    const fix = c.fix || {}, prove = c.prove || {}, twin = c.twin || {};
    const proveDue = prove.due && prove.due <= today;
    const twinOpen = twin.from && twin.from <= today;
    host.append(h('div', { class: 'card-head' }, h('p', { class: 'k', text: 'Test → Fix → Prove' }), h('h2', { class: 'h2', text: `${c.label}${c.number ? ' #' + c.number : ''} · ${plural(c.misses, 'miss', 'misses')}` })));
    host.append(h('ol', { class: 'cy-steps' },
      seg('Fix', { done: fix.done, text: fix.done ? 'Done' : fix.open ? `${fix.open} open` : '' }, fix.done ? null : btn(`Fix ${c.misses}`, { cls: 'btn sm', run: b => drill(fix.body, b) })),
      seg(prove.due ? `Prove (due ${day(prove.due)})` : 'Prove', { text: prove.due ? (proveDue ? 'Due now' : `Opens ${day(prove.due)}`) : 'After the fix, 3 days on' },
        proveDue ? btn('Prove now', { cls: 'btn sm', run: b => start(prove.body, b) }) : null),
      seg(twin.from ? `Twin (from ${day(twin.from)})` : 'Twin', { text: twinOpen ? 'Ready' : twin.from ? `Opens ${day(twin.from)}` : '' },
        twinOpen ? btn('Retake as twin', { cls: 'btn sm', run: b => start(twin.body, b) }) : null)));
    const pr = c.proved;
    if (pr && pr.of) host.append(h('p', { class: 'sc-line', text: `Proved ${pr.n || 0} of ${pr.of}${pr.pts ? ` · worth ≈ +${pr.pts} on ${c.label}${c.number ? ' #' + c.number : ''}` : ''}` }));
  }

  /* ---------------- T3: In progress (#live) */
  function stateLine(r) {
    const left = r.left_seconds;
    const won = r.conditions !== 'training' && r.ranked === false ? ' · won’t rank' : '';
    if (r.status === 'not_begun') return 'Not begun';
    if (r.status === 'paused') return left === null || left === undefined ? `Paused · untimed${won}` : `Paused · ${mmss(left)} left${won}`;
    if (r.status === 'timed_out') return 'Time ran out · answers saved';
    if (left === null || left === undefined) return `Untimed · ${Math.round((r.ms || 0) / 60000)} min so far`;
    return `Clock running · ${mmss(left)} left`;
  }
  function liveCard() {
    const host = $('#live');
    const list = D.in_progress || [];
    host.hidden = !list.length;
    if (!list.length) return;
    host.replaceChildren(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'In progress' }), h('span', { class: 'meta', text: String(list.length) })));
    list.slice(0, 3).forEach(r => host.append(liveRow(r)));
    if (list.length > 3) host.append(btn(`Show all ${list.length}`, { cls: 'quiet', run: () => { if (sitBar) sitBar.set('status', 'in_progress'); $('#sittings').scrollIntoView({ behavior: 'smooth' }); } }));
  }
  function liveRow(r) {
    const n = r.module === 2 ? '' : '';
    const of = (r.modules || []).length > 1 || r.kind === 'section' || r.paper ? `Module ${r.module || 1} of 2 · ` : '';
    const count = r.asked || (r.kind === 'diagnostic' ? 20 : 22);
    const el = h('div', { class: 'lv-row', 'data-id': r.id });
    const label = r.status === 'not_begun' ? 'Begin' : r.status === 'timed_out' ? 'Continue' : 'Resume';
    el.append(h('div', { class: 'lv-l' },
      h('p', { class: 'lv-title', text: `${r.kind_label}${r.number ? ' #' + r.number : ''}${n}` }),
      h('p', { class: 'meta', text: `${of}${r.answered || 0} of ${count} answered` }),
      h('p', { class: 'lv-state mono', text: stateLine(r) }),
      h('p', { class: 'meta', text: `Started ${UI.relTime ? UI.relTime(r.started) : day(r.started)}` })));
    const acts = h('div', { class: 'lv-acts' },
      h('a', { class: 'pill sm', href: r.href || lobby(r.id), text: label }),
      r.status !== 'not_begun' ? h('a', { class: 'quiet', href: `${lobby(r.id)}#review`, text: 'Hand in' }) : null,
      btn('Discard', { cls: 'quiet', run: () => discard(r, el) }));
    el.append(acts);
    return el;
  }
  async function discard(r, el) {
    const name = `${r.kind_label}${r.number ? ' #' + r.number : ''}`;
    const ok = await UI.confirm({ title: `Discard ${name}?`, text: `Its ${plural(r.answered || 0, 'answer')} won’t count anywhere. This can’t be undone.`, confirm: 'Discard', cancel: 'Keep it', destructive: true });
    if (!ok) return;
    try {
      await api(`/session/${encodeURIComponent(r.id)}/discard`, { method: 'POST' });
      if (el) { el.classList.add('out'); setTimeout(() => load(true), 180); } else load(true);
    } catch (e) { toast(`Couldn’t discard: ${e.message}`); }
  }

  /* ---------------- T7: How you take tests (#habits, X17) */
  function habitsCard() {
    const host = $('#habits');
    host.replaceChildren();
    const H = D.habits || { rows: [] };
    const head = h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'How you take tests' }));
    if (H.from_n && H.n && H.from_n < H.n) head.append(h('span', { class: 'meta', text: `from ${H.from_n} of ${H.n} tests` }));
    host.append(head);
    const filtered = habitsView.last !== 'all' || habitsView.scope !== 'timed';
    if ((H.n || 0) >= 2 || filtered) {
      const bar = h('div', { class: 'hb-bar' });
      UI.seg(bar, [{ value: '5', label: 'Last 5' }, { value: '10', label: '10' }, { value: 'all', label: 'All' }], { value: habitsView.last, label: 'Sittings', onChange: v => loadHabits({ last: v }) });
      UI.seg(bar, [{ value: 'sections', label: 'Sections and papers' }, { value: 'timed', label: 'All timed' }], { value: habitsView.scope, label: 'Which tests', onChange: v => loadHabits({ scope: v }) });
      host.append(bar);
    }
    if ((H.n || 0) < 2 || !(H.rows || []).length) {
      host.append(h('p', { class: 'help', text: 'Sit 2 timed tests to see how you take them: pacing, blanks, answer changes, marking and confidence.' }),
        btn('Full section · 70 min', { cls: 'btn sm', run: b => start({ kind: 'section' }, b) }));
      return;
    }
    const list = h('ul', { class: 'hb-rows' });
    const sorted = [...H.rows].sort((a, b) => (a.verdict === 'costs' ? 0 : 1) - (b.verdict === 'costs' ? 0 : 1) || (a.points || 0) - (b.points || 0));
    sorted.forEach(r => {
      const li = h('li', { class: 'hb-row' + (r.verdict === 'costs' ? ' costs' : ' good') },
        h('span', { class: 'hb-g', 'aria-label': r.verdict === 'costs' ? 'Costs points' : 'Good', text: r.verdict === 'costs' ? '!' : '✓' }),
        h('div', { class: 'hb-t' }, h('b', { text: r.title }), h('span', { class: 'mono hb-ev', text: r.evidence || '' }), r.trend ? h('span', { class: 'meta', text: r.trend }) : null));
      const sp = h('span', { class: 'hb-spark' });
      if (UI.spark && (r.series || []).length > 1) UI.spark(sp, r.series, { label: r.title, w: 60, h: 20 });
      li.append(sp);
      const acts = h('span', { class: 'hb-acts' });
      if (r.action) acts.append(btn(r.action.label || 'Start', { cls: 'btn sm', run: b => action(r.action, b) }));
      if (r.why) { const w = btn('Why', { cls: 'quiet', aria: `Why: ${r.title}` }); if (UI.tooltip) UI.tooltip(w, r.why); else w.title = r.why; acts.append(w); }
      if ((r.sittings || []).length) acts.append(btn('Which sittings?', { cls: 'quiet', run: () => showOnly(r.sittings, r.title) }));
      li.append(acts);
      list.append(li);
    });
    host.append(list);
  }

  async function loadHabits(patch) {
    Object.assign(habitsView, patch);
    // GET /api/tests reads habits_last (5 | 10 | all) and habits_scope (sections | timed) for this card
    try {
      const r = await api(`/tests?habits_last=${habitsView.last}&habits_scope=${habitsView.scope}`, { quiet: true });
      if (r && r.habits) D.habits = r.habits;
      habitsCard();
    } catch (_) { toast('Couldn’t load those habits. Try again.'); }
  }
  function showOnly(ids, label) {
    onlyIds = { ids: new Set(ids), label };
    shown = 20;
    if (sitPaint) sitPaint(); else sittingsCard();
    $('#sittings').scrollIntoView({ behavior: UI.reduced && UI.reduced() ? 'auto' : 'smooth' });
  }

  /* ---------------- active filters as removable chips under a bar (X20, T6) */
  function activeChips(host, bar, filters, v, extra) {
    host.replaceChildren();
    filters.filter(f => f.type !== 'sort' && v[f.key]).forEach(f => {
      const o = (f.options || []).find(x => String(x.value) === String(v[f.key]));
      host.append(btn(`${f.label}: ${o ? o.label : v[f.key]}`, { cls: 'tag fchip', aria: `Remove the filter ${f.label}: ${o ? o.label : v[f.key]}`, run: () => bar.set(f.key, '') }));
    });
    if (extra) host.append(extra);
    host.hidden = !host.childNodes.length;
  }

  /* ---------------- T4: New test (#kinds) */
  const kindOf = id => (D.kinds || []).find(k => k.id === id);
  const INFO = {
    section: { title: 'Full section', tags: ['Adaptive', 'Official timing', '8/7/4/3 each module'], facts: '44 questions · 70 min · 2 modules', body: { kind: 'section' }, opts: { kind: 'section' } },
    module1: { title: 'Module 1', tags: ['Mixed difficulty', 'Official timing'], facts: '22 questions · 35 min', body: { kind: 'module', module: 'm1' }, opts: { kind: 'modules', mods: ['m1'] } },
    module2u: { title: 'Module 2 · harder', tags: ['Fixed', 'Leans hard'], facts: '22 questions · 35 min', help: 'What a strong module 1 earns you.', body: { kind: 'module', module: 'm2u' }, opts: { kind: 'modules', mods: ['m2u'] } },
    module2l: { title: 'Module 2 · easier', tags: ['Fixed', 'Leans easy'], facts: '22 questions · 35 min', help: 'Its score tops out at 580, as on the SAT.', body: { kind: 'module', module: 'm2l' }, opts: { kind: 'modules', mods: ['m2l'] } },
    custom: { title: 'Custom test', tags: ['Your skills or mistakes', 'Test rules'], facts: '5–60 questions · you choose', help: 'No answers until you hand in, like a real module.', sheet: true, opts: { kind: 'custom' } },
    diagnostic: { title: 'Diagnostic', tags: ['All four domains evenly'], facts: '20 questions · 32 min', help: 'Asks for your name and email before the result.', body: { kind: 'diagnostic' }, opts: { kind: 'diagnostic' } },
    twin: { title: 'Twin', tags: ['Same slots', 'New numbers'], facts: 'The same length as the original', help: 'Every question the same kind, at the same difficulty and position, with new numbers: an equal test, to see whether you’ve improved.', opts: { kind: 'twin' } },
    trainer: { title: 'Route-up trainer', tags: ['Module 1', 'Official timing', 'Test-day'], facts: '22 questions · 35 min', help: 'The line: 14 of 22 right routes you up.', body: { kind: 'module', module: 'm1', trainer: 'route', conditions: 'test_day' }, opts: { kind: 'trainer' } },
    traps: { title: 'Trap test', tags: ['Your traps', 'Test rules'], facts: '6–22 questions · 95 s each', help: 'Every question offers a wrong answer you’ve fallen for before. Do you still take it?', body: { kind: 'custom', custom: { source: 'traps', traps: 'all', neutral: 0.25 } }, opts: { kind: 'traps' } },
  };
  function recommendedKind() {
    const u = D.up_next || {};
    return { section: 'section', module: u.preset === 'pacing' ? null : 'module1', diagnostic: 'diagnostic', trainer: 'trainer', traps: 'traps' }[u.kind] || null;
  }
  function pips(list, n = 5) {
    const box = h('span', { class: 'pips-row', role: 'img', 'aria-label': `${(list || []).filter(Boolean).length} of the last ${(list || []).length} made it` });
    (list || []).slice(-n).forEach(x => box.append(h('i', { class: x ? 'on' : '' })));
    return box;
  }
  function kindsCard() {
    const host = $('#kinds');
    host.replaceChildren();
    const tm = D.types_met || {};
    const head = h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'New test' }));
    host.append(head);
    if (tm.total && tm.tests) host.append(h('p', { class: 'meta ts-met' }, `Question types met under the clock: ${num(tm.tests || 0)} of ${num(tm.total)} · `, h('a', { class: 'quiet', href: '/me/#atlas?met=tests', text: 'Which ones?' })));
    const grid = h('div', { class: 'ts-grid' });
    const rec = recommendedKind();
    const est = D.estimate || {};
    const ids = ['section', 'module1', 'module2u', 'module2l', 'custom', 'diagnostic'];
    if (D.twin) ids.push('twin');
    ids.push('trainer', 'traps');
    ids.forEach(id => {
      const k = kindOf(id) || {};
      const I = INFO[id];
      const card = h('article', { class: 'ts-card kind', 'data-kind': id, tabindex: '-1' });
      const title = id === 'twin' && D.twin ? `Twin of ${D.twin.label}` : I.title;
      card.append(h('div', { class: 'tc-head' }, h('h3', { class: 'tc-title', text: title }),
        btn('Report', { cls: 'quiet tc-rep', aria: `Report a problem with ${title}`, run: () => UI.report && UI.report({ kind: 'catalog', source: 'tests', page: `kind:${id}` }) })));
      card.append(h('div', { class: 'tc-tags' }, I.tags.map((t, i) => h('span', { class: 'tag' + (t === 'Adaptive' ? ' wash' : ''), text: t }))));
      card.append(h('p', { class: 'tc-facts mono', text: I.facts }));
      if (I.help) card.append(h('p', { class: 'help', text: I.help }));
      const stats = h('div', { class: 'tc-stats' });
      const stat = (label, v, sub) => { if (v === null || v === undefined || v === '') return; stats.append(h('div', { class: 'stat sm' }, h('span', { class: 'stat-k', text: label }), h('span', { class: 'stat-v', text: String(v) }), sub ? h('span', { class: 'stat-sub', text: sub }) : null)); };
      if (id === 'traps') stat('Traps ready', k.ready || 0);
      else if (id === 'twin') stat('Original', D.twin && D.twin.band ? band(D.twin.band) : null);
      else {
        if (k.yours) stat('You', k.last !== null && k.last !== undefined ? `≈${Math.round(k.last)}` : 'Practice');
        if (k.best !== null && k.best !== undefined && k.yours > 1) stat('Best', `≈${Math.round(k.best)}`);
        if (id === 'section' && est.latest) stat('Adds', est.confidence && est.confidence.level === 'high' ? 'Keeps it High' : '+1 section → High confidence');
        if (k.everyone) stat('Everyone', plural(k.everyone, 'sitting'));
      }
      if (stats.childNodes.length) card.append(stats);
      if (k.percentile !== null && k.percentile !== undefined) card.append(h('p', { class: 'meta', text: `Your last beats ${Math.round(k.percentile)}% of fresh ${id === 'section' ? 'sections' : 'sittings'}` }));
      // goals: the trainer's streak and the gauntlet (X14)
      if (id === 'trainer') card.append(h('div', { class: 'tc-goal' }, h('span', { text: 'Route up 3 times in a row' }), pips(k.pips), k.best_streak ? h('span', { class: 'meta', text: `Best streak ${k.best_streak}` }) : null));
      if (id === 'module2u' && k.gauntlet && k.gauntlet.shown) card.append(h('div', { class: 'tc-goal' }, h('span', { text: `${k.gauntlet.goal || 18} of 22 on the harder module 2` }), pips(k.gauntlet.pips)));
      const acts = h('div', { class: 'tc-acts' });
      const primary = rec === id ? 'pill' : 'btn';
      const body = id === 'twin' ? { kind: 'twin', twin_of: D.twin && D.twin.source } : id === 'module2u' && k.gauntlet && k.gauntlet.shown ? Object.assign({}, I.body, { trainer: 'gauntlet' }) : I.body;
      const disabled = id === 'traps' && !k.ready;
      const go = btn(disabled ? 'No traps ready yet' : 'Start', { cls: primary, run: b => (I.sheet ? S.open(I.opts) : start(body, b)) });
      if (disabled) go.disabled = true;
      acts.append(go, btn('Options', { cls: 'quiet', run: () => S.open(Object.assign({ step: id === 'diagnostic' ? 1 : 1 }, I.opts)) }));
      if (id === 'section') acts.append(btn('Race friends', { cls: 'quiet', run: () => race({ count: 22, minutes: 35, twin: true, open_for: 72 }) }));
      card.append(acts);
      grid.append(card);
    });
    host.append(grid);
  }
  function race(body) {
    // Compete owns private contests (decision 5: an invite code, no classes)
    if (UI.createContest) return UI.createContest(Object.assign({ preset: true }, body));
    location.href = `/compete/?create=${encodeURIComponent(JSON.stringify(body))}`;
    return null;
  }

  /* ---------------- T5: Papers (#papers, X20) */
  const PF = {
    diff: [['harder', 'Harder for me'], ['about', 'About my level'], ['easier', 'Easier for me']],
    status: [['not_sat', 'Not sat'], ['in_progress', 'In progress'], ['completed', 'Completed'], ['fix', 'Misses to fix']],
    for: [['traps', 'Has my open mistake types'], ['new', 'Types I haven’t met']],
    src: [['weekly', 'Weekly'], ['launch', 'Launch'], ['road', 'Road to']],
  };
  const paperTest = {
    diff: (p, v) => ((p.rating || {}).you || {}).chip === v,
    status: (p, v) => (v === 'fix' ? (p.yours || {}).misses_to_fix > 0 : ((p.yours || {}).status || 'not_sat') === v),
    for: (p, v) => (v === 'traps' ? p.open_traps > 0 : p.types_new > 0),
    src: (p, v) => (v === 'road' ? String(p.source || '').startsWith('final-') || p.kind === 'road' : (p.kind || p.source) === v),
  };
  function paperFilter(list, vals, skip) {
    return list.filter(p => Object.keys(PF).every(k => k === skip || !vals[k] || paperTest[k](p, vals[k])));
  }
  const bestFor = p => (((p.yours || {}).status || 'not_sat') === 'not_sat' ? 1000 : 0) + 3 * (p.open_traps || 0) + (p.types_new || 0);
  const SORTS = {
    best: (a, b) => bestFor(b) - bestFor(a) || b.n - a.n,
    new: (a, b) => b.n - a.n, old: (a, b) => a.n - b.n,
    hard: (a, b) => (((a.rating || {}).you || {}).expect_m1 ?? 99) - (((b.rating || {}).you || {}).expect_m1 ?? 99),
    easy: (a, b) => (((b.rating || {}).you || {}).expect_m1 ?? -1) - (((a.rating || {}).you || {}).expect_m1 ?? -1),
    crowd: (a, b) => (((a.rating || {}).everyone || {}).expect_m1 ?? 99) - (((b.rating || {}).everyone || {}).expect_m1 ?? 99),
    most: (a, b) => (b.sat_by || 0) - (a.sat_by || 0),
  };
  function papersCard() {
    const host = $('#papers');
    host.replaceChildren();
    const list = D.papers || [];
    host.append(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'Papers' }), h('span', { class: 'meta', text: String(list.length) })),
      h('p', { class: 'help ts-sub', text: 'The same question types in the same order for everyone, each with their own numbers, so scores compare and answers can’t be passed around. A new paper every Monday.' }));
    const barHost = h('div', { class: 'ts-bar', id: 'paperFilters' });
    const chipHost = h('div', { class: 'ts-chips', hidden: true });
    host.append(barHost, chipHost);
    const gridHost = h('div', { class: 'ts-grid' });
    const foot = h('div', { class: 'ts-foot' });
    host.append(gridHost, foot);
    const hasEst = !!(D.estimate && D.estimate.latest);
    const counts = vals => Object.fromEntries(Object.entries(PF).map(([k, opts]) => [k, Object.fromEntries(opts.map(([v]) => [v, paperFilter(list, Object.assign({}, vals, { [k]: v }), null).length]))]));
    const filters = [
      { key: 'p.diff', label: 'Difficulty', options: PF.diff.map(([value, label]) => ({ value, label })) },
      { key: 'p.status', label: 'Status', options: PF.status.map(([value, label]) => ({ value, label })) },
      { key: 'p.for', label: 'For me', options: PF.for.map(([value, label]) => ({ value, label })) },
      { key: 'p.src', label: 'Source', options: PF.src.map(([value, label]) => ({ value, label })) },
      { key: 'p.sort', label: 'Sort', type: 'sort', default: hasEst ? 'best' : 'new',
        options: [['best', 'Best for me'], ['new', 'Newest'], ['old', 'Oldest'], ['hard', 'Hardest for me'], ['easy', 'Easiest for me'], ['crowd', 'Hardest for everyone'], ['most', 'Most sat']].map(([value, label]) => ({ value, label })) },
    ];
    const vals = v => ({ diff: v['p.diff'], status: v['p.status'], for: v['p.for'], src: v['p.src'] });
    const paint = v => {
      const cur = vals(v);
      const c = counts(cur);
      Object.keys(PF).forEach(k => paperBar && paperBar.counts(`p.${k}`, c[k]));
      if (paperBar) activeChips(chipHost, paperBar, filters, v);
      const shownList = paperFilter(list, cur).sort(SORTS[v['p.sort']] || SORTS.new);
      gridHost.replaceChildren();
      foot.replaceChildren();
      if (!shownList.length) {
        gridHost.append(h('div', { class: 'ts-empty' }, h('p', { text: 'No papers match these filters.' }), btn('Clear filters', { cls: 'btn sm', run: () => paperBar.clear() })));
        return;
      }
      shownList.slice(0, papersAll ? shownList.length : 6).forEach(p => gridHost.append(paperCard(p)));
      if (shownList.length > 6 && !papersAll) foot.append(btn(`Show all ${shownList.length}`, { cls: 'quiet', run: () => { papersAll = true; paint(paperBar.values()); } }));
    };
    paperBar = UI.filterBar(barHost, filters, { url: true, store: 'satf.tests.paperFilters', label: 'Paper filters', onChange: v => paint(v) });
    paint(paperBar.values());
  }
  function ratingChips(p) {
    const r = p.rating || {};
    const you = r.you || {}, ev = r.everyone || {};
    const box = h('div', { class: 'tc-rate' });
    if (you.chip) {
      const e1 = you.expect_m1 !== undefined ? Math.round(you.expect_m1) : null;
      const text = { harder: 'Harder for you', easier: 'Easier for you', about: 'About your level' }[you.chip] || 'About your level';
      const c = h('span', { class: 'tag wash', text: e1 !== null ? `${text} · expect ${e1} of 22` : text });
      const tip = [e1 !== null ? `Expect ${e1} of 22 in module 1` : null, you.typical_m1 !== undefined ? `${Math.round(you.typical_m1)} on most papers` : null,
        you.source === 'types' ? 'from how hard its types have been' : 'from your skill ratings'].filter(Boolean).join(' · ');
      if (UI.tooltip) UI.tooltip(c, tip); else c.title = tip;
      box.append(c);
    }
    if (ev.label) {
      const w = { harder: 'harder than most', easier: 'easier than most', typical: 'typical' }[ev.label] || ev.label;
      const c = h('span', { class: 'tag', text: `Everyone: ${w}` });
      const tip = ev.source === 'measured' ? `Measured from ${plural(ev.n, 'first ranked sitting')}` : 'Predicted from its types';
      if (UI.tooltip) UI.tooltip(c, tip); else c.title = tip;
      box.append(c);
    }
    return box;
  }
  function paperCard(p) {
    const y = p.yours || {};
    const status = y.status || 'not_sat';
    const card = h('article', { class: 'ts-card paper', 'data-paper': String(p.n), tabindex: '-1' });
    card.append(h('div', { class: 'tc-head' }, h('h3', { class: 'tc-title', text: `Paper #${p.n}` }), p.newest ? h('span', { class: 'tag wash', text: 'New this week' }) : null,
      btn('Report', { cls: 'quiet tc-rep', aria: `Report a problem with Paper #${p.n}`, run: () => UI.report && UI.report({ kind: 'paper', source: 'tests', paper: p.n }) })));
    const road = String(p.source || '').startsWith('final-');
    card.append(h('p', { class: 'meta', text: [road ? p.label : p.kind === 'launch' || p.source === 'launch' ? 'Launch set' : p.label, { not_sat: 'Not sat', in_progress: 'In progress', completed: 'Sat' }[status]].filter(Boolean).join(' · ') }));
    if (road) card.append(h('div', { class: 'tc-tags' }, h('span', { class: 'tag', text: `Season Final${p.sat_by ? ` · ${num(p.sat_by)} sat it live` : ''}` })));
    card.append(ratingChips(p));
    const stats = h('div', { class: 'tc-stats' });
    const stat = (k, v, sub) => { if (v === null || v === undefined || v === '') return; stats.append(h('div', { class: 'stat sm' }, h('span', { class: 'stat-k', text: k }), h('span', { class: 'stat-v', text: String(v) }), sub ? h('span', { class: 'stat-sub', text: sub }) : null)); };
    if (p.sat_by) stat('Sat by', num(p.sat_by), p.ranked_n ? `${num(p.ranked_n)} ranked` : null);
    if (p.average) stat('Average', Math.round(p.average), p.ranked_n >= 20 ? 'ranked' : null);
    if (status === 'completed' && y.last) stat('You', band(y.last) || Math.round(y.last), y.first_percentile !== null && y.first_percentile !== undefined ? `beats ${Math.round(y.first_percentile)}%` : null);
    else if (status === 'in_progress') stat('You', 'In progress');
    if (stats.childNodes.length) card.append(stats);
    if (p.hist && UI.scale) { const sc = h('div', { class: 'tc-hist' }); try { UI.scale(sc, { hist: p.hist, compact: true, band: y.last && y.last.low ? y.last : undefined, target: D.target || undefined }); } catch (_) {} card.append(sc); }
    const line = [p.open_traps ? `Has ${num(p.open_traps)} of your open mistake types` : null, p.types_new ? `${plural(p.types_new, 'type')} you haven’t met under the clock` : null].filter(Boolean);
    if (line.length) card.append(h('p', { class: 'meta tc-line', text: line.join(' · ') }));
    if (p.hardest) card.append(h('p', { class: 'meta', text: typeof p.hardest === 'string' ? p.hardest : `Hardest: ${String(p.hardest.slot || '').replace(/^m(1|2u|2l):(\d+)$/, (_, m, i) => `${{ 1: 'M1', '2u': 'M2 harder', '2l': 'M2 easier' }[m]} Q${i}`)}${p.hardest.right !== undefined ? ` · ${Math.round(p.hardest.right * 100)}% right` : ''}${p.hardest.you !== undefined ? ` · you ${p.hardest.you ? 'got it' : 'missed it'}` : ''}` }));
    const u = D.up_next || {};
    const rec = u.kind === 'paper' && u.paper === p.n;
    const label = status === 'in_progress' ? 'Resume' : status === 'completed' ? 'Retake' : 'Start';
    const acts = h('div', { class: 'tc-acts' });
    acts.append(btn(label, { cls: rec ? 'pill' : 'btn', run: b => (status === 'in_progress' && y.live_session ? (location.href = lobby(y.live_session)) : start({ kind: 'paper', paper: p.n }, b)) }));
    acts.append(btn('Options', { cls: 'quiet', run: () => S.open({ kind: 'paper', paper: p.n, step: 1 }) }));
    acts.append(btn(`Questions & discussion${p.posts ? ' ' + p.posts : ''}${p.gated ? ' · opens after you sit it' : ''}`, { cls: 'quiet tc-talk', run: () => talk(p) }));
    if (status === 'completed' && y.last_session) acts.append(btn('Again, exactly', { cls: 'quiet', aria: 'Again, exactly · tests memory', run: b => start({ kind: 'paper', paper: p.n, exact: true }, b) }));
    acts.append(btn('Race friends', { cls: 'quiet', run: () => race({ paper: p.n, count: 22, minutes: 35, twin: true, open_for: 72 }) }));
    card.append(acts);
    return card;
  }
  function talk(p, o = {}) {
    if (!window.TestsTalk) return null;
    return TestsTalk.open(p, Object.assign({ start: b => start({ kind: 'paper', paper: p.n }, b) }, o));
  }

  /* ---------------- T6: Your sittings (#sittings) */
  const TESTS = new Set(['section', 'mock', 'module', 'custom', 'diagnostic', 'paper', 'twin', 'shared']);
  function norm(r) {
    const mods = r.modules || null;
    const sum = k => (mods || []).reduce((a, m) => a + ((m[k] || []).length), 0);
    if (r.status) return Object.assign({}, r, { misses: sum('missed'), blanks: sum('blank') });
    // the old /api/history row, until S6 serves sitting_row's shape
    const kind = r.kind === 'mock' ? 'section' : r.kind;
    return { id: r.id, kind, kind_label: UI.KIND.label(r), number: null, status: r.finished ? 'completed' : 'in_progress', started: r.started, finished: r.finished,
      estimate: r.estimate && r.estimate.low !== undefined ? { low: r.estimate.low, high: r.estimate.high } : null, right: r.right, asked: r.asked,
      modules: null, misses: r.asked !== null && r.asked !== undefined && r.right !== null && r.right !== undefined ? r.asked - r.right : 0, blanks: 0 };
  }
  const kindKey = r => (r.trainer ? 'trainer' : /trap/i.test(r.kind_label || '') ? 'traps' : r.paper ? 'paper' : r.twin_of || r.kind === 'twin' ? 'twin'
    : r.shared_from || r.kind === 'shared' ? 'shared' : r.kind === 'mock' ? 'section' : r.kind);
  const SF = {
    kind: [['section', 'Full sections'], ['paper', 'Papers'], ['module', 'Modules'], ['custom', 'Custom'], ['diagnostic', 'Diagnostics'], ['twin', 'Twins'], ['shared', 'Shared'], ['traps', 'Trap tests'], ['trainer', 'Trainer']],
    status: [['completed', 'Completed'], ['in_progress', 'In progress'], ['timed_out', 'Timed out'], ['pressure', 'Pressure losses']],
    route: [['upper', 'Harder module 2'], ['lower', 'Easier module 2'], ['fixed', 'Fixed route']],
    timing: [['official', 'Official'], ['extended', 'Extended'], ['untimed', 'Untimed']],
    cond: [['test_day', 'Test-day'], ['training', 'Training']],
  };
  const sitTest = {
    kind: (r, v) => kindKey(r) === v,
    status: (r, v) => (v === 'in_progress' ? ['in_progress', 'paused', 'not_begun'].includes(r.status) : v === 'pressure' ? !!(r.pressure && r.pressure.buckets && (r.pressure.buckets.pressure || []).length) : r.status === v),
    route: (r, v) => (v === 'fixed' ? !!r.fixed_route : r.route === v),
    timing: (r, v) => (v === 'extended' ? ['x1.5', 'x2'].includes(r.timing) : (r.timing || 'official') === v),
    cond: (r, v) => (r.conditions || 'test_day') === v,
  };
  const mid = r => (r.estimate && r.estimate.low !== null && r.estimate.low !== undefined ? (r.estimate.low + r.estimate.high) / 2 : r.asked ? (r.right || 0) / r.asked * 1000 - 10000 : -1e9);
  const SSORT = {
    new: (a, b) => String(b.started).localeCompare(String(a.started)), old: (a, b) => String(a.started).localeCompare(String(b.started)),
    high: (a, b) => mid(b) - mid(a), low: (a, b) => (mid(a) === -1e9) - (mid(b) === -1e9) || mid(a) - mid(b),
    hard: (a, b) => (b.mean_weight || 0) - (a.mean_weight || 0), easy: (a, b) => (a.mean_weight || 9) - (b.mean_weight || 9),
    missed: (a, b) => (b.misses || 0) - (a.misses || 0),
  };
  function sitFilter(vals, skip) { return rows.filter(r => (!onlyIds || onlyIds.ids.has(r.id)) && Object.keys(SF).every(k => k === skip || !vals[k] || sitTest[k](r, vals[k]))); }
  function sittingsCard() {
    const host = $('#sittings');
    host.replaceChildren();
    const head = h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'Your sittings' }), h('span', { class: 'meta', id: 'sitN', text: rowsState === 'ok' ? String(rows.length) : '' }));
    const csv = btn('Export CSV', { cls: 'quiet', id: 'csv', run: () => exportCsv() });
    head.append(h('span', { class: 'card-act' }, csv));
    host.append(head);
    const barHost = h('div', { class: 'ts-bar', id: 'filters' });
    const chipHost = h('div', { class: 'ts-chips', hidden: true });
    const list = h('div', { class: 'st-list', role: 'list', 'aria-label': 'Your sittings' });
    const foot = h('div', { class: 'ts-foot' });
    host.append(barHost, chipHost, list, foot);
    cmpBar = UI.actionBar ? UI.actionBar(host, { actions: [
      { label: 'Compare', primary: true, onClick: () => compare() },
      { label: 'Clear', quiet: true, onClick: () => { picked = []; host.querySelectorAll('.sr-cmp input').forEach(x => { x.checked = false; }); pickedBar(); } }] }) : null;
    if (cmpBar) cmpBar.el.classList.add('st-cmp');
    sitPaint = null;
    if (rowsState === 'loading') { if (UI.skel) UI.skel(list, 'rows:4'); return; }
    if (rowsState === 'error') { if (UI.cardError) UI.cardError(list, () => loadRows(), 'Couldn’t load your sittings.'); return; }
    if (!rows.length) { csv.hidden = true; list.append(h('div', { class: 'ts-empty' }, h('p', { text: 'Nothing sat yet. Your first full section gives your first score estimate.' }), btn('Full section · 70 min', { cls: 'btn sm', run: b => start({ kind: 'section' }, b) }))); return; }
    const filters = [
      ...Object.entries(SF).map(([key, opts]) => ({ key, label: { kind: 'Kind', status: 'Status', route: 'Route', timing: 'Timing', cond: 'Conditions' }[key], options: opts.map(([value, label]) => ({ value, label })) })),
      { key: 'sort', label: 'Sort', type: 'sort', default: 'new', options: [['new', 'Newest'], ['old', 'Oldest'], ['high', 'Highest'], ['low', 'Lowest'], ['hard', 'Hardest'], ['easy', 'Easiest'], ['missed', 'Most missed']].map(([value, label]) => ({ value, label })) },
    ];
    const paint = v => {
      const counts = Object.fromEntries(Object.entries(SF).map(([k, opts]) => [k, Object.fromEntries(opts.map(([o]) => [o, sitFilter(Object.assign({}, v, { [k]: o }), null).length]))]));
      Object.keys(SF).forEach(k => sitBar && sitBar.counts(k, counts[k]));
      const out = sitFilter(v).sort(SSORT[v.sort] || SSORT.new);
      list.replaceChildren();
      foot.replaceChildren();
      csv.hidden = !out.length;
      activeChips(chipHost, sitBar, filters, v, onlyIds ? btn(`Only: ${onlyIds.label}`, { cls: 'tag fchip', aria: `Show every sitting, not only ${onlyIds.label}`, run: () => { onlyIds = null; paint(sitBar.values()); } }) : null);
      if (!out.length) { list.append(h('div', { class: 'ts-empty' }, h('p', { text: 'No sittings match these filters.' }), btn('Clear filters', { cls: 'btn sm', run: () => sitBar.clear() }))); return; }
      out.slice(0, shown).forEach(r => list.append(sitRow(r)));
      if (out.length > shown) foot.append(btn(`Show ${Math.min(20, out.length - shown)} more`, { cls: 'quiet', run: () => { shown += 20; paint(sitBar.values()); } }));
      list.dataset.count = String(Math.min(out.length, shown));
      pickedBar();
    };
    sitBar = UI.filterBar(barHost, filters, { url: true, store: 'satf.tests.filters', label: 'Sitting filters', onChange: v => { shown = 20; paint(v); } });
    sitPaint = () => paint(sitBar.values());
    sitPaint();
  }
  function missChips(r) {
    const box = h('span', { class: 'sr-miss' });
    const mods = r.modules || [];
    let left = innerWidth < 760 ? 6 : 8;
    mods.forEach(m => {
      const all = [...(m.missed || []).map(p => ['incorrect', p]), ...(m.blank || []).map(p => ['blank', p])].sort((a, b) => a[1] - b[1]);
      if (!all.length) return;
      const g = h('span', { class: 'sr-mg' }, h('span', { class: 'k', text: `M${m.n}` }));
      all.forEach(([st, p]) => {
        if (left <= 0) return;
        left--;
        g.append(UI.cell(st, p, { href: report(r.id, `M${m.n}-${p}`), size: 'sm', label: `M${m.n} Q${p} · ${st === 'blank' ? 'blank' : 'wrong'}`, tip: `M${m.n} Q${p} · ${st === 'blank' ? 'blank' : 'wrong'}` }));
      });
      box.append(g);
    });
    const total = mods.reduce((a, m) => a + (m.missed || []).length + (m.blank || []).length, 0);
    const cap = innerWidth < 760 ? 6 : 8;
    if (total > cap) box.append(h('span', { class: 'meta', text: `+${total - cap}` }));
    return box;
  }
  function scoreChips(r) {
    const c = [];
    if (r.route === 'upper') c.push('Harder M2');
    if (r.route === 'lower') c.push('Easier M2');
    if (r.capped) c.push('580 cap');
    if (r.fixed_route) c.push('Fixed route');
    if (r.extended) c.push('Extended');
    if (r.pauses && r.status === 'completed') c.push(`Paused ${r.pauses}×`);
    if (r.status === 'completed' && r.ranked === false && r.conditions !== 'training' && r.unranked_why) c.push(`Unranked · ${r.unranked_why}`);
    if (r.conditions === 'training') c.push('Training');
    if (r.offline_ms) c.push(`offline ${mmss(r.offline_ms / 1000)}`);
    if (r.gate && r.gate.margin !== undefined && r.gate.margin !== null) c.push(r.gate.margin >= 0 ? `Gate +${r.gate.margin}` : `Gate ${r.gate.margin}`);
    const pb = r.pressure && r.pressure.buckets;
    if (pb && ((pb.pressure || []).length || (pb.knowledge || []).length)) c.push(`Pressure ${(pb.pressure || []).length} · Knowledge ${(pb.knowledge || []).length}`);
    if (r.pass2 && r.pass2.pts) c.push(`2nd pass +${r.pass2.pts}`);
    return h('span', { class: 'sr-chips' }, c.map(t => h('span', { class: 'tag sm', text: t })));
  }
  function sitRow(r) {
    const live = ['in_progress', 'paused', 'not_begun'].includes(r.status);
    const el = h('div', { class: 'sr-row', role: 'listitem', 'data-id': r.id, tabindex: '-1' });
    const mods = r.modules || [];
    const score = band(r.estimate) || (r.right !== null && r.right !== undefined && r.asked ? `${r.right}/${r.asked}` : live ? '' : 'Practice');
    const sub = [r.paper || r.kind === 'section' || r.kind === 'mock' ? (r.fixed_route ? 'fixed route' : 'adaptive') : null,
      r.timing && r.timing !== 'official' ? { 'x1.5': 'time and a half', x2: 'double time', untimed: 'untimed', 'x0.85': 'tight clock' }[r.timing] : 'official'].filter(Boolean).join(' · ');
    const when = r.started ? `${day(r.started)} · ${new Date(r.started).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', hour12: false })}` : '';
    const mins = r.ms ? Math.round(r.ms / 60000) : null;
    el.append(h('div', { class: 'sr-l1' },
      h('span', { class: 'sr-n mono', text: r.number ? `#${r.number}` : '' }),
      h('span', { class: 'sr-d mono', text: when }),
      h('span', { class: 'sr-k' }, h('b', { text: r.kind_label + (r.retake ? ` · Retake ${r.retake}` : '') }), h('span', { class: 'sr-ks', text: live ? stateLine(r) : sub })),
      h('span', { class: 'sr-s' }, h('b', { class: 'sr-band', text: score }), scoreChips(r)),
      h('span', { class: 'sr-m mono', 'aria-label': mods[0] ? `Module 1: ${mods[0].right} of ${mods[0].asked}` : null, text: mods[0] ? `${mods[0].right}/${mods[0].asked}` : '' }),
      h('span', { class: 'sr-m mono', text: mods[1] ? `${mods[1].right}/${mods[1].asked}` : mods[0] ? '—' : '' }),
      h('span', { class: 'sr-t mono', text: mins !== null ? `${r.timing === 'untimed' ? 'Untimed · ' : ''}${mins} min` : '' }),
      missChips(r)));
    const acts = h('div', { class: 'sr-acts' });
    if (!live) {
      const cb = h('input', { type: 'checkbox', 'aria-label': `Compare ${r.kind_label}${r.number ? ' #' + r.number : ''}` });
      cb.checked = picked.includes(r.id);
      cb.addEventListener('change', () => pick(r.id, cb.checked));
      acts.append(h('label', { class: 'sr-cmp' }, cb, h('span', { text: 'Compare' })));
    }
    if (live) acts.append(h('a', { class: 'quiet', href: r.href || lobby(r.id), text: r.status === 'not_begun' ? 'Begin' : 'Resume' }));
    else {
      acts.append(h('a', { class: 'quiet', href: report(r.id), text: 'Review' }));
      if (r.misses || r.blanks) acts.append(btn(`Fix ${r.misses + r.blanks}`, { cls: 'quiet', run: b => drill({ from_session: r.id, scope: 'misses', source: 'fix' }, b) }));
      if (['section', 'mock', 'module', 'paper', 'twin', 'shared'].includes(r.kind) || r.paper) acts.append(btn('Twin', { cls: 'quiet', run: b => start({ kind: 'twin', twin_of: r.id }, b) }));
      if (r.paper) acts.append(btn('Retake', { cls: 'quiet', run: b => start({ kind: 'paper', paper: r.paper }, b) }));
      if (r.route === 'lower') acts.append(btn('Try the harder module 2', { cls: 'quiet', run: b => start({ kind: 'module', module: 'm2u' }, b) }));
      acts.append(btn('Share', { cls: 'quiet', run: () => share(r) }));
    }
    const noteEl = h('p', { class: 'sr-note', text: r.note || '', hidden: !r.note });
    acts.append(btn(r.note ? 'Edit note' : 'Note', { cls: 'quiet', run: b => editNote(r, el, noteEl, b) }));
    el.append(h('div', { class: 'sr-l2' }, acts, noteEl));
    return el;
  }
  function pick(id, on) {
    picked = picked.filter(x => x !== id);
    if (on) picked.push(id);
    while (picked.length > 2) {
      const drop = picked.shift();
      const cb = document.querySelector(`.sr-row[data-id="${CSS.escape(drop)}"] .sr-cmp input`);
      if (cb) cb.checked = false;
    }
    pickedBar();
  }
  function pickedBar() {
    if (!cmpBar) return;
    picked = picked.filter(id => rows.some(r => r.id === id));
    const tagOf = id => { const r = rows.find(x => x.id === id); return r && r.number ? `#${r.number}` : r ? r.kind_label : ''; };
    cmpBar.set(picked.length === 2 ? `Compare ${tagOf(picked[0])} and ${tagOf(picked[1])}` : picked.length === 1 ? `${tagOf(picked[0])} · tick one more to compare` : '', picked.length);
    const go = cmpBar.el.querySelector('.pill, .primary, button');
    if (go) go.disabled = picked.length !== 2;
  }
  function compare(ids) {
    const list = ids || picked;
    if (list.length === 2 && window.TestsCompare) TestsCompare.open(list, { rows, drill, start });
  }
  function editNote(r, el, noteEl, trigger) {
    if (el.querySelector('.sr-ed')) return;
    const ta = h('textarea', { class: 'field', rows: 3, maxlength: 1000, 'aria-label': 'Your note on this sitting', placeholder: 'e.g. ran out of time on 18–22' });
    ta.value = r.note || '';
    const count = UI.counter ? UI.counter(ta, 1000) : null;
    const box = h('div', { class: 'sr-ed' }, ta, h('div', { class: 'sr-ed-acts' }, count,
      btn('Cancel', { cls: 'quiet', run: () => { box.remove(); trigger.focus(); } }),
      btn('Save', { cls: 'btn sm', run: async b => {
        b.setAttribute('aria-busy', 'true');
        try {
          await api(`/session/${encodeURIComponent(r.id)}/note`, { method: 'PUT', body: { text: ta.value.slice(0, 1000) } });
          r.note = ta.value.trim(); noteEl.textContent = r.note; noteEl.hidden = !r.note; trigger.textContent = r.note ? 'Edit note' : 'Note';
          box.remove(); trigger.focus();
        } catch (e) { b.removeAttribute('aria-busy'); toast(`Note not saved: ${e.message}`); }
      } })));
    el.append(box);
    ta.focus();
  }
  function share(r) {
    if (!UI.sheet) return null;
    let fresh = true, showScore = true, link = null, how = 'link';
    const who = `${r.kind_label}${r.number ? ' #' + r.number : ''}`;
    return UI.sheet({ title: `Share ${who}`, size: 'm', className: 'share-sheet', body: b => {
      const linkBox = h('div', { class: 'sh-pane' }), raceBox = h('div', { class: 'sh-pane', hidden: true });
      UI.seg(b, [{ value: 'link', label: 'Any time (a link)' }, { value: 'race', label: 'A race with a deadline' }], { value: 'link', label: 'How',
        onChange: v => { how = v; linkBox.hidden = how !== 'link'; raceBox.hidden = how !== 'race'; } });
      b.append(linkBox, raceBox);
      // a link: twins by default, or exactly these questions
      const help = h('p', { class: 'help' });
      const say = () => { help.textContent = fresh ? 'The same kinds of question in the same order, with their own numbers. Answers can’t be passed around, and you still compare question by question.' : 'The same questions as yours.'; };
      const field = h('input', { class: 'field', readonly: true, 'aria-label': 'Share link', placeholder: 'Copy makes the link' });
      const reset = () => { link = null; field.value = ''; };
      UI.seg(linkBox, [{ value: 'twins', label: 'Twins' }, { value: 'exact', label: 'Exactly these questions' }], { value: 'twins', label: 'What they sit', onChange: v => { fresh = v === 'twins'; say(); reset(); } });
      say();
      linkBox.append(help);
      UI.switch(linkBox, { label: 'Show my score to people who sit it', checked: true, onChange: v => { showScore = v; reset(); } });
      const make = async x => {
        x.setAttribute('aria-busy', 'true');
        try {
          const s2 = await api('/sets', { method: 'POST', body: { kind: 'test', session: r.id, show_score: showScore, cfg: { fresh } } });
          link = new URL(s2.url || `/tests/?shared=${encodeURIComponent(s2.code)}`, location.origin).href;
          field.value = link;
          if (UI.copyText) UI.copyText(link, { toast: 'Link copied' });
        } catch (e) { toast(`Couldn’t make the link: ${e.message}`); }
        finally { x.removeAttribute('aria-busy'); }
      };
      linkBox.append(h('div', { class: 'sh-link' }, field, btn('Copy', { cls: 'pill sm', run: x => (link ? UI.copyText(link, { toast: 'Link copied' }) : make(x)) })));
      linkBox.append(h('p', { class: 'help', text: 'Anyone with the link sits the same question types in the same order with their own numbers (or these exact questions, if you chose that). They see no answers until they finish, and you’ll see how they did.' }));
      if (navigator.share) linkBox.append(btn('More ways to share', { cls: 'quiet', run: async x => { if (!link) await make(x); if (link) navigator.share({ url: link, title: 'SAT Freshman test' }).catch(() => {}); } }));
      // a race: Compete's private contest by invite code (decision 5: no classes, no roles)
      raceBox.append(h('p', { class: 'help', text: 'Module 1’s question types as twins: 22 questions, 35 minutes, open for 3 days. Anyone with the code joins; Compete keeps the board.' }));
      const out = h('div', { class: 'sh-race', hidden: true });
      const create = btn('Create the race', { cls: 'pill sm', run: async x => {
        x.setAttribute('aria-busy', 'true');
        const body = { from_session: r.id, count: 22, minutes: 35, twin: true, open_for: 72 };
        try {
          const c = await api('/contests', { method: 'POST', quiet: true, body });
          const code = c.code || (c.contest && c.contest.code);
          if (!code) throw new Error('no code');
          const url2 = new URL(c.url || `/compete/contest/?code=${encodeURIComponent(code)}`, location.origin).href;
          const f = h('input', { class: 'field', readonly: true, value: url2, 'aria-label': 'Race link' });
          out.replaceChildren(h('p', { class: 'sh-code' }, h('span', { class: 'k', text: 'Invite code' }), h('b', { class: 'mono', text: code }),
            btn('Copy code', { cls: 'quiet', run: () => UI.copyText(code, { toast: 'Code copied' }) })), h('div', { class: 'sh-link' }, f, btn('Copy', { cls: 'pill sm', run: () => UI.copyText(url2, { toast: 'Link copied' }) })));
          out.hidden = false;
          create.hidden = true;
        } catch (_) { race(body); }
        finally { x.removeAttribute('aria-busy'); }
      } });
      raceBox.append(create, out, h('a', { class: 'quiet', href: '/compete/', text: 'Races you made' }));
    } });
  }
  function exportCsv() {
    const v = sitBar ? sitBar.values() : {};
    const out = sitFilter(v).sort(SSORT[v.sort] || SSORT.new);
    const nMods = Math.max(1, ...out.map(r => (r.modules || []).length));
    const esc = x => { const s = x === null || x === undefined ? '' : String(x); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
    const head = ['number', 'date', 'kind', 'band', ...Array.from({ length: nMods }, (_, i) => `Math M${i + 1}`), 'route', 'conditions', 'ranked', 'timing', 'minutes', 'misses', 'blanks', 'note'];
    const lines = [head.join(',')].concat(out.map(r => [r.number || '', (r.started || '').slice(0, 10), r.kind_label, band(r.estimate) || '',
      ...Array.from({ length: nMods }, (_, i) => ((r.modules || [])[i] ? `${r.modules[i].right}/${r.modules[i].asked}` : '')),
      r.route || '', r.conditions || '', r.ranked === undefined ? '' : r.ranked ? 'yes' : 'no', r.timing || '', r.ms ? Math.round(r.ms / 60000) : '',
      r.misses || 0, r.blanks || 0, r.note || ''].map(esc).join(',')));
    const a = h('a', { href: URL.createObjectURL(new Blob([lines.join('\n') + '\n'], { type: 'text/csv;charset=utf-8' })), download: 'sat-freshman-sittings.csv' });
    document.body.append(a); a.click(); a.remove();
  }

  /* ---------------- How scoring works (#howScored) */
  function howScored() {
    if (!UI.sheet) return;
    const pts = [
      'Every test is built when you start it, from questions you haven’t seen. Papers give everyone the same question types in the same slots, each with their own numbers.',
      'The estimate is an ordinal heuristic from how many you got right and which module 2 you reached. It is not IRT.',
      'Bands: about ±70 for a section or paper, ±100 for a module or the diagnostic.',
      'The route: 14 of 22 right in module 1 (60%) earns the harder module 2, which can reach 800. The easier module 2 tops out at 580, as on the SAT.',
      'A harder or easier module 1, a single module 2 and custom tests are practice, not a score estimate.',
      'Test-day sittings rank; Training sittings keep their score and never rank. Pausing, extended time, a fixed route, a break of more than 75 s between modules or more than 2 minutes away also keeps the score and drops the rank. Losing Wi-Fi doesn’t.',
      'Combined, paper stats and every percentile count ranked first sittings only, from 20 of them.',
      'A pressure check never changes a band. A question removed after a report (a wrong key, no right answer) leaves both right and asked.',
      'Confidence: High takes 3 sections in 30 days within 100 points; one section is Medium; a module or the diagnostic is Low.',
      'Floor-score sittings still count.',
    ];
    const cal = D && D.calibration;
    pts.push(cal && cal.checked >= 50 ? `Checked against ${num(cal.checked)} Bluebook and official scores.` : 'Not yet checked against real scores.');
    UI.sheet({ title: 'How scoring works', size: 'm', body: b => {
      b.append(h('div', { class: 'hs-route', role: 'img', 'aria-label': 'Module 1: 14 of 22 right routes to the harder module 2 (up to 800); fewer, to the easier module 2 (up to 580)' },
        h('span', { class: 'hs-box', text: 'Module 1' }), h('span', { class: 'hs-arrow mono', text: '14 of 22 →' }),
        h('span', { class: 'hs-split' }, h('span', { class: 'hs-box on', text: 'Harder module 2 · up to 800' }), h('span', { class: 'hs-box', text: 'Easier module 2 · up to 580' }))));
      b.append(h('ul', { class: 'hs-list' }, pts.map(t => h('li', { text: t }))));
    } });
  }

  /* ---------------- keys (X23): J / K move, Enter starts, O options, F filters */
  function keys() {
    if (!UI.keys || !UI.keys.register) return;
    const items = () => [...document.querySelectorAll('.ts-card, .sr-row')].filter(e => e.offsetParent);
    const move = d => { const l = items(); if (!l.length) return; const i = l.indexOf(document.activeElement); const n = l[Math.max(0, Math.min(l.length - 1, i < 0 ? 0 : i + d))]; n.focus(); n.scrollIntoView({ block: 'nearest' }); };
    const cur = () => document.activeElement && document.activeElement.closest && document.activeElement.closest('.ts-card, .sr-row');
    UI.keys.register('tests', {
      J: { does: 'Next card or row', run: () => move(1) },
      K: { does: 'Previous card or row', run: () => move(-1) },
      Enter: { does: 'Start, or resume a paused row', run: () => { const c = cur(); if (!c) return false; const b = c.querySelector('.tc-acts > :first-child, .sr-acts > a, .sr-acts > button'); if (b) b.click(); return undefined; } },
      O: { does: 'Options', run: () => { const c = cur(); const b = c && [...c.querySelectorAll('button')].find(x => x.textContent === 'Options'); if (b) b.click(); else return false; return undefined; } },
      D: { does: 'Questions & discussion (papers)', run: () => { const c = cur(); const b = c && c.querySelector('.tc-talk'); if (b) b.click(); else return false; return undefined; } },
      X: { does: 'Compare (rows)', run: () => { const c = cur(); const cb = c && c.querySelector('.sr-cmp input'); if (!cb) return false; cb.checked = !cb.checked; cb.dispatchEvent(new Event('change')); return undefined; } },
      F: { does: 'The first filter', run: () => { const b = document.querySelector('#sittings .filters .dd, #papers .filters .dd'); if (b) b.focus(); } },
    }, { label: 'Tests' });
  }

  /* ---------------- load and paint */
  function sections() {
    const list = [];
    const H = D.habits || {};
    list.push({ id: 'habits', label: `Habits${(H.rows || []).length ? ' ' + H.rows.length : ''}` });
    list.push({ id: 'kinds', label: `New test ${document.querySelectorAll('#kinds .ts-card').length}` });
    list.push({ id: 'papers', label: `Papers ${(D.papers || []).length}` });
    if ((D.in_progress || []).length) list.push({ id: 'live', label: `In progress ${D.in_progress.length}` });
    list.push({ id: 'sittings', label: `Your sittings${rowsState === 'ok' && rows.length ? ' ' + rows.length : ''}` });
    const bar = UI.sections(list);
    // counts in DM Mono beside each label
    if (bar) bar.querySelectorAll(':scope > a').forEach(a => { const m = /^(.*?)\s(\d+)$/.exec(a.textContent); if (m) a.replaceChildren(m[1], ' ', h('span', { class: 'n mono', text: m[2] })); });
  }
  function paint() {
    if (!D) return;
    S.use(D, rows);
    try { scoreCard(); } catch (e) { console.error(e); if (UI.cardError) UI.cardError($('#score'), () => load(true), 'Couldn’t load your score.'); }
    nextCard(); cycleCard(); liveCard(); habitsCard(); kindsCard(); papersCard();
    sittingsCard();
    sections();
  }
  async function loadRows() {
    try {
      const r = D && D.sittings ? { sessions: D.sittings } : await api('/history?all=1', { quiet: true });
      const list = (r.sessions || r.rows || r || []).map(norm).filter(x => TESTS.has(x.kind) || x.paper);
      const live = (D && D.in_progress || []).map(norm);
      const seen = new Set(list.map(x => x.id));
      rows = live.filter(x => !seen.has(x.id)).concat(list).sort(SSORT.new);
      rowsState = 'ok';
    } catch (_) { rowsState = 'error'; }
    if (!D) return;
    S.use(D, rows);
    try { scoreCard(); } catch (e) { console.error(e); }
    nextCard();
    sittingsCard();
    sections();
  }
  function skeleton() {
    ['#score', '#next', '#kinds', '#papers', '#sittings'].forEach(id => { const el = $(id); if (el && UI.skel) { el.replaceChildren(); if (id === '#kinds' || id === '#papers') { const g = h('div', { class: 'ts-grid' }); [0, 1, 2].forEach(() => UI.skel(g, 'card')); el.append(g); } else UI.skel(el, 'lines:3'); } });
  }
  async function load(fresh) {
    if (!D) skeleton();
    try {
      if (UI.cached && !fresh) {
        await new Promise((resolve, reject) => {
          let done = false;
          UI.cached('/tests', (d, fromCache) => { D = d; paint(); if (!done) { done = true; resolve(); } }, { key: 'satf.tests.v2', store: 'session' }).catch(e => { if (!done) { done = true; reject(e); } });
        });
      } else { D = await api('/tests'); paint(); }
    } catch (e) {
      if (!D) {
        ['#score', '#kinds', '#papers'].forEach(id => { const el = $(id); el.replaceChildren(); if (UI.cardError) UI.cardError(el, () => load(true), id === '#papers' ? 'Couldn’t load papers.' : 'Couldn’t load your tests.'); });
        $('#next').replaceChildren();
      }
      return;
    }
    await loadRows();
  }

  $('#howBtn').addEventListener('click', () => howScored());
  keys();
  load().then(() => {
    // deep links: ?start=…, ?shared=CODE (the start sheet), ?compare=a,b (X18)
    const st = url.get('start'), shared = url.get('shared');
    if (shared) S.open({ shared, kind: 'shared', step: 1 });
    else if (st) {
      const m = /^paper:(\d+)$/.exec(st);
      const map = { section: { kind: 'section', step: 1 }, modules: { kind: 'modules' }, module1: { kind: 'modules', mods: ['m1'] }, module2u: { kind: 'modules', mods: ['m2u'] },
        module2l: { kind: 'modules', mods: ['m2l'] }, custom: { kind: 'custom' }, diagnostic: { kind: 'diagnostic', step: 0 }, twin: { kind: 'twin' }, traps: { kind: 'traps' }, trainer: { kind: 'trainer' } };
      S.open(m ? { kind: 'paper', paper: +m[1], step: 1 } : map[st] || {});
    }
    const cmp = url.get('compare');
    if (cmp) compare(cmp.split(',').filter(Boolean).slice(0, 2));
    if (location.hash) { const el = document.getElementById(location.hash.slice(1)); if (el && !el.hidden) el.scrollIntoView(); }
  });
})();
