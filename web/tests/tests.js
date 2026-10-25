/* ============================================================================
   SAT Freshman -- Tests, /tests/ (spec 3.4 section 2; tests.md X1, X2, X13-X18, X20, X23)

   One GET /api/tests (painted from the cached copy first) fills the page; the sittings list
   reads GET /api/history?all=1 (S6's rows, sitting_row's shape; the old shape is read too).
   Main column (the task):
     #next     T2 the next test and its Start, the page's one primary, in §3.1 item 11's order
     #live     T3 In progress                      #cycle  Test → Fix → Prove (X16)
     #kinds    T4 New test, a row each             #papers T5 Papers, a tile each (preview, then text), filters (X20)
     #sittings T6 Your sittings, filters, CSV
   Aside (.twocol-side, context):
     #score    T1 the estimate, its facts and the gate (X14); #estLine repeats it in one line under 1280px
     #levers   What moves this band: #moves (where the points went, X15) | #habits (how you take tests, X17)
   Every Start is one tap into the lobby (/test/?s=ID); Options (the ⋯ menu, O) opens the start sheet (start.js).
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
  const r10 = v => Math.round(v / 10) * 10;      // a single score figure, on tens like every range
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const S = window.TestStart;
  // the page's one subject (the switch under the title); TestStart puts it on every start. sp() is a module's size,
  // seconds, pace and route line for it
  let subject = S.subject;
  const sp = s => S.spec(s || subject);
  const mins = s => Math.round(sp(s).secs / 60);
  const ofSubject = r => (r.subject || 'math') === subject;
  const secFacts = () => `${2 * sp().n} questions · ${2 * mins()} min`;
  const modFacts = () => `${sp().n} questions · ${mins()} min`;
  const diagFacts = () => `20 questions · ${Math.round(20 * sp().pace / 60)} min`;
  // the full SAT: both sections and the break between them (2 h 14 min of testing)
  const fullFacts = () => `${S.FULL.n} questions · ${Math.floor(S.FULL.mins / 60)} h ${S.FULL.mins % 60} min + a ${S.FULL.breakMins}-minute break`;
  let D = null;                 // /api/tests
  let rows = [];                // the sittings, newest first
  let rowsState = 'loading';    // loading | ok | error
  let shown = 20;
  let sitBar = null, paperBar = null, papersAll = false;
  let picked = [], cmpBar = null, onlyIds = null, sitPaint = null;     // X18's two ticked rows; X17's "Which sittings?"
  let habitsView = { last: 'all', scope: 'timed' };
  let leversView = ls.get('satf.tests.levers', 'points');   // which half of What moves this band: points | habits
  let leversSeg = null;

  UI.shell({ page: 'tests', now: false, ownPrimary: true });   // Up next's Start in the sidebar is a .btn: the hero keeps the one orange

  /* ---------------- actions shared by every card */
  async function drill(body, btn) {
    if (btn) btn.setAttribute('aria-busy', 'true');
    try { const r = await api('/drill', { method: 'POST', body }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
    catch (e) { if (btn) btn.removeAttribute('aria-busy'); toast(e.status === 409 ? (e.data && e.data.detail && e.data.detail.reason) || e.message : 'Couldn’t start that. Try again.'); }
  }
  const start = (body, btn) => S.go(body, btn).catch(() => {});
  const lobby = id => `/test/?s=${encodeURIComponent(id)}`;
  const report = (id, q) => `/results/report/?id=${encodeURIComponent(id)}${q ? `&q=${q}` : ''}`;
  const fullHref = id => `/results/full/?id=${encodeURIComponent(id)}`;    // a full SAT's result: the total, then each section
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

  /* ---------------- T1: the estimated score (#score, aside) */
  const CONF = { high: 'Consistent', medium: 'Mixed', low: 'Rough' };
  const CAUSE = { trap: 'Traps', clock: 'Clock', slip: 'Slips', entry: 'Entry', gap: 'Gaps', changed: 'Changed answers' };
  // two plain lines: how far from the target (what matters), then which way the estimate moved
  function headline(e) {
    // the move is the last sitting's on the one before; the target is measured from the current score (range)
    const L = e.latest, P = e.previous, t = D.target, C = e.range || L;
    if (!L) return [null, null];
    const mid = L.mid ?? (L.low + L.high) / 2, cur = C.mid ?? (C.low + C.high) / 2;
    let move = 'Your first estimate';
    if (P) {
      const d = Math.round((mid - (P.mid ?? (P.low + P.high) / 2)) / 10) * 10;
      move = Math.abs(d) < 20 ? `Level with ${day(P.at)}` : d > 0 ? `Up ${d} points since ${day(P.at)}` : `Down ${-d} points since ${day(P.at)}`;
    }
    const goal = !t ? null : cur >= t ? `You're at your ${t} target` : `${Math.round((t - cur) / 10) * 10} points below your ${t} target`;
    return [goal, move];
  }
  function scoreCard() {
    const host = $('#score');
    host.replaceChildren();
    const e = D.estimate || {};
    const L = e.latest;
    const conf = e.confidence || {};
    // number first: the title with which way the band moved directly under it, the confidence top right, then the
    // band with its scale beside it, then how far from the target
    const title = h('div', { class: 'sc-title' }, h('h2', { class: 'h2', id: 'scoreH', text: `Estimated ${UI.subjectLabel(subject)} score` }));
    const head = h('div', { class: 'card-head' }, title);
    host.append(head);
    const est = $('#estLine');
    if (!L) {
      // a dimmed sample of what lands here (the band and its chart), then what fills it
      if (UI.empty) UI.empty(host, { sample: ghostEstimate, tag: false, text: 'No estimate yet. A full section, one module or the diagnostic gives your first.' });
      else host.append(h('p', { class: 'sc-empty', text: 'No estimate yet' }));
      if (est) est.hidden = true;
      return;
    }
    // the confidence, its reason one tap away (a tooltip alone never reached touch or the keyboard); it sits beside
    // the band's scale, so a long title never leaves it alone on a line
    const level = CONF[conf.level] || 'Low';
    const confEl = h('span', { class: 'sc-conf' }, h('span', { class: 'badge' + (conf.level === 'high' ? '' : conf.level === 'medium' ? ' soft' : ' line'), text: level }),
      conf.reason ? UI.why(conf.reason, { about: `${level.toLowerCase()} confidence` }) : null);
    const [goal, move] = headline(e);
    title.append(h('p', { class: 'meta', text: move }));
    // the one number the page is about, at the hero step: the current score (estimate.range, the one rule Results,
    // Me and the total use too); it rolls when it differs from the band last seen here
    const b = band(e.range || L), seen = ls.get(`satf.tests.band.${subject}`, null);
    const fig = keepBand('fig', () => h('span', { class: 'sc-band hero-num' }), b);
    host.append(h('p', { class: 'sc-fig' }, fig, h('span', { class: 'sc-unit', text: 'of 800' }), confEl));
    if (goal) host.append(h('p', { class: 'sc-head', text: goal }));     // native append prints a null as "null"
    // a quiet way to firm the band up (the next test above carries the page's one orange Start)
    if (conf.level === 'low') host.append(btn(`Full section · ${2 * mins()} min`, { cls: 'quiet', run: b => start({ kind: 'section' }, b) }));
    else if (conf.level === 'medium') host.append(btn('Sit one more section', { cls: 'quiet', run: b => start({ kind: 'section' }, b) }));
    const estB = est ? keepBand('est', () => h('b'), b) : null;
    if (est) { est.replaceChildren(estB, ` · ${[level, goal || move].filter(Boolean).join(' · ')}`); est.hidden = false; }
    ls.set(`satf.tests.band.${subject}`, b);
    [fig, estB].forEach(x => { if (x && x._fresh && seen && seen !== b && UI.roll) { x.textContent = seen; UI.roll(x, b); } if (x) x._fresh = false; });

    const chart = h('div', { class: 'sc-chart' });
    host.append(chart);
    const pts = subjRows().filter(r => r.estimate && r.estimate.low !== null && r.estimate.low !== undefined).slice(0, 8).reverse()
      .map(r => ({ id: r.id, at: r.finished || r.started, low: r.estimate.low, high: r.estimate.high, kind: r.paper ? 'paper' : r.kind === 'section' ? 'mock' : r.kind,
        label: `${r.kind_label}${r.number ? ' #' + r.number : ''}`, href: report(r.id) }));
    if (UI.bandChart) {
      try {
        UI.bandChart(chart, pts, { height: 110, target: D.target || undefined, min: 200, max: 800, label: 'Your last scored sittings' });
      } catch (_) {}
    }
    const facts = h('dl', { class: 'sc-facts' });
    const fact = (k, v, o = {}) => { if (v === null || v === undefined || v === '') return; const dd = h('dd', {}, typeof v === 'string' ? h(o.href ? 'a' : 'span', { href: o.href || null, text: v }) : v); facts.append(h('div', { class: 'sc-fact' }, h('dt', { class: 'k', text: k }), dd)); };
    fact('Best', band(e.best));
    fact('Target', D.target ? `${D.target} (Plan)` : 'Set a target', { href: '/plan/' });
    fact('Exam', D.exam ? `${day(D.exam.date)} · ${plural(D.exam.days, 'day')}` : 'Set a date', { href: '/plan/' });
    host.append(facts);

    // the total, the projection, growth and calibration (X14, X15): one tap away in a fold, its open state remembered
    const more = [];
    const line = text => more.push(h('p', { class: 'sc-line', text }));
    const T = D.total;
    // the server's total (estimate.total: R&W's centre plus Math's, 20 wide), its two halves R&W first, each by source
    const part = p => `${UI.subjectLabel(p.subject, true)} ${p.low !== undefined && p.low !== p.high ? `${p.low}–${p.high}` : p.value}${p.source === 'self' ? ' (you entered)' : p.source && p.source !== 'measured' ? ` (${p.source === 'official' ? 'official SAT' : 'Bluebook'})` : ''}`;
    if (T && T.low !== undefined && T.low !== null) line(`Total ${T.low}–${T.high}${(T.parts || []).length ? ` · ${T.parts.map(part).join(' · ')}` : ''}`);
    const P = D.projection;
    if (P) line(P.verdict || P.label || (P.low ? `On pace: about ${P.low}–${P.high}${P.to ? ` on ${day(P.to)}` : ''}${D.target ? ` · target ${D.target}` : ''}` : ''));
    const G = D.growth;
    if (G && G.delta !== undefined) line(`Since your first section: ${G.delta >= 0 ? '+' : '−'}${Math.abs(G.delta)} · more than ${Math.round((G.pct ?? G.percentile ?? 0) * (G.pct > 1 ? 1 : 100))}% of students who started near ${G.start} (${plural(G.n, 'student')})`);
    const C = D.calibration;
    if (C && C.latest) {
      const x = C.latest;
      line(`Your ${x.source === 'official' ? 'official SAT' : 'Bluebook test'}: ${x.math ?? x.score} (${day(x.day)}) · our estimate then: ${band(x.estimate || x)} · ${x.inside ? 'inside' : 'outside'}`);
    }
    if (more.length) {
      const d = h('details', { class: 'fold sc-more' }, h('summary', { class: 'fold-s', text: 'Total, pace and growth' }), ...more);
      d.open = !!ls.get('satf.tests.scoreMore', false);
      d.addEventListener('toggle', () => ls.set('satf.tests.scoreMore', d.open));
      host.append(d);
    }
  }

  // a band node: a repaint with the same band keeps the node (so a roll in flight carries on), a new band is a new
  // node marked _fresh (scoreCard rolls it from the band last seen on this device: a change, never a first visit)
  const bands = {};
  function keepBand(slot, make, b) {
    if (bands[slot] && bands[slot].dataset.band === b) return bands[slot];
    const el = make();
    el.dataset.band = b;
    el.textContent = b;
    el._fresh = true;
    return (bands[slot] = el);
  }
  // the empty estimate's sample: a made-up band over three made-up sittings
  function ghostEstimate() {
    const chart = h('div', { class: 'sc-chart' });
    const now = Date.now();
    if (UI.bandChart) {
      try {
        UI.bandChart(chart, [[21, 470, 490], [12, 510, 530], [3, 540, 560]].map(([d, low, high]) => ({ at: new Date(now - d * 864e5).toISOString(), low, high, kind: 'mock' })),
          { height: 110, min: 200, max: 800, label: 'An example' });
      } catch (_) {}
    }
    // its Example tag takes the confidence's place beside the scale (the shared corner tag sat on the band)
    return h('div', { class: 'sc-ghost' }, h('p', { class: 'sc-fig' }, h('span', { class: 'sc-band', text: '540–560' }), h('span', { class: 'sc-unit', text: 'of 800' }),
      h('span', { class: 'sc-conf' }, h('span', { class: 'badge soft', text: 'Example' }))), chart);
  }

  /* ---------------- What moves this band (#levers, aside): one card, two halves behind a seg */
  function leversCard() {
    const host = $('#levers .mv-seg');
    host.replaceChildren();
    leversSeg = UI.seg(host, [{ value: 'points', label: 'Where points went' }, { value: 'habits', label: 'Habits' }],
      { value: leversView, label: 'What moves this band', onChange: v => { leversView = v; ls.set('satf.tests.levers', v); syncLevers(true); } });
    syncLevers();
    movesBand();
    habitsCard();
  }
  function syncLevers(e) {
    $('#moves').hidden = leversView !== 'points';
    $('#habits').hidden = leversView !== 'habits';
    if (e && UI.motion) UI.motion.enter($(leversView === 'habits' ? '#habits' : '#moves'), 'fade');   // a switch crossfades; the first paint does not
  }
  function movesBand() {
    const host = $('#moves');
    host.replaceChildren();
    const L = D.levers || {};
    const causes = (L.causes || []).filter(c => c.n);
    if (!causes.length && !(L.skills || []).length) {
      // two dimmed sample rows of what lands here
      const sample = () => h('ul', { class: 'mv-rows' }, [['Traps', 3, 30], ['Clock', 2, 20]].map(([name, n, pts]) =>
        h('li', { class: 'mv-row' }, h('span', { class: 'mv-name', text: name }), h('span', { class: 'mv-n', text: plural(n, 'question') }), h('span', { class: 'mv-pts', text: `≈ +${pts}` }), h('span'))));
      if (UI.empty) UI.empty(host, { sample, text: 'Sit a full section to see where your points went.' });
      else host.append(h('p', { class: 'help', text: 'Sit a full section to see where your points went.' }));
      return;
    }
    if (causes.length) {
      host.append(h('p', { class: 'meta', text: `From your last ${plural(L.sittings || 3, 'sitting')}` }));
      const list = h('ul', { class: 'mv-rows' });
      causes.forEach(c => {
        const li = h('li', { class: 'mv-row' }, h('span', { class: 'mv-name', text: CAUSE[c.cause] || c.cause }),
          h('span', { class: 'mv-n', text: plural(c.n, 'question') }), h('span', { class: 'mv-pts', text: c.pts ? `≈ +${c.pts}` : '' }));
        const a = c.action;
        if (a) {
          const label = a.label || 'Start';
          // the row reads name, count, points; its action shows on hover or focus with a mouse (.reveal), always on touch
          li.append(btn(label, { cls: 'btn sm reveal', run: b => action(a, b, { fallback: () => { if (c.cause === 'changed' && rows[0]) location.href = report(rows[0].id) + '&filter=changed'; } }) }));
        } else li.append(h('span'));
        list.append(li);
      });
      host.append(list);
    }
    if (L.route && (L.route.text || L.route.pts)) host.append(h('p', { class: 'sc-line', text: L.route.text || `One more right in module 1 would have lifted the 580 cap · up to +${L.route.pts}` }));
    if (L.both && L.both.pts && causes.length > 1) {
      const t = D.target, bb = L.both.band;
      host.append(h('p', { class: 'sc-line', text: `${causes.slice(0, 2).map(c => (CAUSE[c.cause] || c.cause).toLowerCase()).join(' and ').replace(/^./, x => x.toUpperCase())} together ≈ +${L.both.pts}${t && bb && bb.high >= t ? ` · your ${t} target is inside` : ''}` }));
    }
    if ((L.skills || []).length && UI.skillRow) {
      // the skills worth the most fold under one line, their open state remembered like the estimate's
      const sk = h('div', { class: 'mv-skills' });
      L.skills.slice(0, 3).forEach(s => UI.skillRow(sk, Object.assign({ answered: s.evidence, right: Math.round((s.accuracy || 0) * (s.evidence || 0)), mastery: s.mastery ?? s.accuracy }, s), { practise: { count: 10 } }));
      const d = h('details', { class: 'fold mv-fold' }, h('summary', { class: 'fold-s', text: `Skills worth the most · ${L.skills.slice(0, 3).length}` }),
        sk, h('a', { class: 'quiet', href: '/#gain', text: 'All skills' }));
      d.open = !!ls.get('satf.tests.skillsMore', false);
      d.addEventListener('toggle', () => ls.set('satf.tests.skillsMore', d.open));
      host.append(d);
    }
  }

  /* ---------------- T2: the next test (#next): the page's one primary; a different source from the shell's Up next */
  function nextCard() {
    const host = $('#next');
    const u = D.up_next || { kind: 'section' };
    const live = (D.in_progress || []).find(r => r.id === u.session);
    const papers = D.papers || [];
    const weekly = papers.find(p => p.newest);
    const lastDays = rows.find(r => r.status === 'completed') ? Math.floor((Date.now() - new Date(rows.find(r => r.status === 'completed').finished).getTime()) / 864e5) : null;
    let t = 'Full section', meta = [secFacts(), lastDays === null ? null : lastDays ? `your last was ${plural(lastDays, 'day')} ago` : 'your last was today'].filter(Boolean).join(' · '), go = b => start({ kind: 'section' }, b), label = 'Start', alt = null;
    switch (u.kind) {
      case 'resume':
        if (live) {
          // a full SAT's Math half, not begun, is its break: the way back is Resume testing
          const fullNo = live.full && (live.full.number || null), brk = live.full && live.full.part === 2 && live.status === 'not_begun';
          t = `Finish ${live.kind_label}${fullNo || live.number ? ' #' + (fullNo || live.number) : ''}`;
          meta = `${UI.subjectLabel(live.subject || 'math')} · ${brk ? 'after the break' : stateLine(live)}`;     // In progress lists both subjects
          label = brk ? 'Resume testing' : live.status === 'not_begun' ? 'Begin' : live.status === 'timed_out' ? 'Continue' : 'Resume'; go = () => { location.href = live.href || lobby(live.id); };
        }
        break;
      case 'pressure': {
        const r = rows.flatMap(x => (x.parts ? x.parts.map(norm) : [x])).find(x => x.id === u.session);    // a full SAT's half too
        t = 'Pressure check'; meta = `${r ? `${r.kind_label}${r.number ? ' #' + r.number : ''} · ` : ''}open until you open its report`; label = 'Start';
        go = async b => { b.setAttribute('aria-busy', 'true'); try { const x = await api(`/session/${encodeURIComponent(u.session)}/pressure`, { method: 'POST' }); location.href = `/practice/session/?id=${encodeURIComponent(x.id)}`; } catch (e) { b.removeAttribute('aria-busy'); toast(e.message); } };
        break;
      }
      case 'traps':
        if (u.reason === 'prove') { const c = D.cycle || {}; t = `Prove ${c.label || 'your fixes'}${cycNo(c) ? ' #' + cycNo(c) : ''}`; meta = 'Due today · a Trap test from its misses'; go = b => start(u.body, b); }
        else { const k = kindOf('traps'); t = 'Trap test'; meta = `${k && k.ready ? plural(k.ready, 'trap') + ' ready · ' : ''}your old wrong answers on offer`; go = b => start({ kind: 'custom', custom: { source: 'traps', traps: 'all', neutral: 0.25 } }, b); }
        break;
      case 'diagnostic': t = 'Start with the diagnostic'; meta = `${diagFacts()} · all four domains evenly`; go = b => start({ kind: 'diagnostic' }, b); break;
      case 'full': t = 'Full SAT'; meta = `Reading and Writing, then Math · ${fullFacts()}`; go = b => start({ kind: 'full' }, b); break;
      case 'contest': t = 'The Season Final is open'; meta = 'Twins, ranked, this weekend'; label = 'Go to the Final'; go = () => { location.href = '/compete/'; }; break;
      case 'paper': {
        const p = papers.find(x => x.n === u.paper) || weekly || {};
        t = p.source && String(p.source).startsWith('final-') ? `${p.label}` : `New this week: Paper #${p.n}`;
        meta = [p.sat_by ? `Sat by ${num(p.sat_by)} so far` : null, `${p.questions || 2 * sp().n} questions · ${2 * mins()} min`].filter(Boolean).join(' · ');
        go = b => start({ kind: 'paper', paper: p.n }, b);
        break;
      }
      case 'trainer': t = 'Route-up trainer'; meta = `Your last sections routed lower · ${modFacts()}`; go = b => start({ kind: 'module', module: 'm1', trainer: 'route', conditions: 'test_day' }, b); break;
      case 'module':
        if (u.preset === 'pacing') { t = 'Pacing practice'; meta = 'Module 1 · Training · tight clock'; go = b => S.preset('pacing', b); }
        else { t = u.reason === 'plan' ? 'Today’s test: module' : 'Module 1'; meta = modFacts(); go = b => (u.preset ? S.preset(u.preset, b) : start({ kind: 'module', module: 'm1' }, b)); }
        break;
      case 'section':
        if (u.reason === 'plan') {
          t = 'Today’s test: full section'; meta = secFacts(); go = b => S.preset(u.preset || 'like_test_day', b);
          if (weekly && weekly.yours && weekly.yours.status === 'not_sat') alt = btn(`Paper #${weekly.n} instead`, { cls: 'quiet', aria: `Sit this week’s Paper #${weekly.n} instead`, run: b => start({ kind: 'paper', paper: weekly.n }, b) });
        }
        break;
      default: break;
    }
    const text = h('div', { class: 'nx-text' }, h('p', { class: 'k', text: 'Next test' }), h('h2', { class: 'h2', text: t }), meta ? h('p', { class: 'meta', text: meta }) : null);
    const plan = UI.shellData && UI.shellData() && UI.shellData().plan;
    // a resume: In progress leaves this sitting to the card, so its Hand in and Discard come along
    const own = u.kind === 'resume' && live ? [live.status !== 'not_begun' ? h('a', { class: 'quiet', href: `${lobby(live.id)}#review`, text: 'Hand in' }) : null,
      btn('Discard', { cls: 'quiet', run: () => discard(live, null) })] : [];
    const goBtn = btn(label, { cls: 'pill', id: 'nextGo', run: go });
    if (UI.icon) goBtn.prepend(UI.icon('play', 16));
    // Plan your test days only beside a fresh test: a resume already carries Hand in and Discard (Plan is in the nav)
    // (a link with the shared link look: as a bold .quiet beside Start it read as a label)
    const acts = h('div', { class: 'nx-acts' }, goBtn, alt, ...own, plan || own.length ? null : h('a', { class: 'link nx-plan', href: '/plan/', text: 'Plan your test days' }));
    // the strips fill once a tab: drawn empty until the sittings behind them are in, then lit left to right
    const grow = !stripsPlayed();
    const fig = shape(u, live, grow);
    const parts = [text, acts, fig].filter(Boolean);
    // the same hero as on screen (cached copy to fresh, the sittings arriving): keep its nodes, so a fill carries on
    const sig = parts.map(x => x.textContent).join('|');
    if (host.dataset.sig !== sig || !host.childNodes.length) {
      host.dataset.sig = sig;
      host.replaceChildren(...parts);
      host._fill = fig && fig._fill;
    }
    if (grow && rowsState !== 'loading') fillStrips(host);
  }
  const stripsPlayed = () => { try { return sessionStorage.getItem('satf.tests.strips') === '1'; } catch (_) { return true; } };
  function fillStrips(host) {
    try { sessionStorage.setItem('satf.tests.strips', '1'); } catch (_) {}
    const f = host._fill;
    host._fill = null;
    if (f) setTimeout(f, 240);
  }
  // the hero's figure: the test's shape as tick strips, module 1 with the route line at 14 (your last module 1, or
  // what a paper should give you, lit against it), then module 2; for a resume, what is answered so far
  const lastM1 = () => { const r = subjRows().find(x => x.status === 'completed' && (x.modules || []).length > 1 && x.modules[0].asked === sp().n); return r ? r.modules[0].right : null; };
  function shape(u, live, grow) {
    const box = h('div', { class: 'nx-shape' });
    const fills = [];
    // grow: drawn empty, then lit to its value (the meter lights new ticks left to right by itself)
    const meter = o => { const m = UI.meter(box, Object.assign({}, o, grow ? { value: 0 } : {})); if (grow && o.value) fills.push([m, o.value]); };
    box._fill = grow ? () => fills.forEach(([m, v]) => m.set({ value: v })) : null;
    const { n, route } = sp();
    const m1 = (v, what) => meter({ label: 'Module 1', value: v || 0, max: n, ticks: n, tick: route, ink: true, lg: true,
      text: v === null || v === undefined ? `${route} of ${n} right routes you up` : `${what} ${v} of ${n} · ${route} routes you up` });
    const m2 = () => meter({ label: 'Module 2', value: 0, max: n, ticks: n, ink: true, lg: true, text: 'Harder or easier, by module 1' });
    if (live) {
      const count = live.asked || (live.kind === 'diagnostic' ? 20 : sp(live.subject).n);
      meter({ label: (live.modules || []).length > 1 || live.kind === 'section' || live.paper ? `Module ${live.module || 1} of 2` : 'Answered',
        value: live.answered || 0, max: count, ticks: Math.min(count, 27), ink: true, lg: true, text: `${live.answered || 0} of ${count} answered` });
      return box;
    }
    if (u.kind === 'full') return null;
    const k = u.kind === 'resume' ? 'section' : u.kind === 'module' && u.preset === 'pacing' ? 'pacing' : u.kind;   // a resume whose sitting is gone falls back to the full section
    if (k === 'paper') {
      const p = (D.papers || []).find(x => x.n === u.paper) || (D.papers || []).find(x => x.newest) || {};
      const e1 = ((p.rating || {}).you || {}).expect_m1;
      m1(e1 === undefined || e1 === null ? null : Math.round(e1), 'Expect'); m2();
    } else if (k === 'section' || !k) { m1(lastM1(), 'Last time'); m2(); }
    else if (k === 'module' || k === 'trainer' || k === 'pacing') m1(lastM1(), 'Last section');
    else return null;
    box.classList.toggle('two', box.children.length > 1);
    return box;
  }

  const cycNo = c => (c.full && c.full.number) || c.number;    // a full SAT's half: the full SAT's number
  /* ---------------- T3b: Test → Fix → Prove (#cycle) */
  function cycleCard() {
    const host = $('#cycle');
    const c = D.cycle;
    host.hidden = !c;
    if (!c) return;
    host.replaceChildren();
    const today = new Date().toLocaleDateString('en-CA');     // the learner's own day, YYYY-MM-DD
    const seg = (name, state, act) => h('li', { class: 'cy-seg' + (state.done ? ' done' : '') }, h('i', { 'aria-hidden': 'true' }), h('b', { text: name }), h('span', { class: 'meta', text: state.text }), act || null);
    const fix = c.fix || {}, prove = c.prove || {}, twin = c.twin || {};
    const proveDue = prove.due && prove.due <= today;
    const twinOpen = twin.from && twin.from <= today;
    host.append(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: `${c.label}${cycNo(c) ? ' #' + cycNo(c) : ''} · ${plural(c.misses, 'miss', 'misses')}` }), h('span', { class: 'meta', text: 'Test → Fix → Prove' })));
    host.append(h('ol', { class: 'cy-steps' },
      seg('Fix', { done: fix.done, text: fix.done ? 'Done' : fix.open ? `${fix.open} open` : '' }, fix.done ? null : btn(`Fix ${c.misses}`, { cls: 'btn sm', run: b => drill(fix.body, b) })),
      seg(prove.due ? `Prove (due ${day(prove.due)})` : 'Prove', { text: prove.due ? (proveDue ? 'Due now' : `Opens ${day(prove.due)}`) : 'After the fix, 3 days on' },
        proveDue ? btn('Prove now', { cls: 'btn sm', run: b => start(prove.body, b) }) : null),
      seg(twin.from ? `Twin (from ${day(twin.from)})` : 'Twin', { text: twinOpen ? 'Ready' : twin.from ? `Opens ${day(twin.from)}` : '' },
        twinOpen ? btn('Retake as twin', { cls: 'btn sm', run: b => start(twin.body, b) }) : null)));
    const pr = c.proved;
    // the fixes proved against the misses to prove, a block each
    if (pr && pr.of) UI.meter(host, { label: 'Proved', value: pr.n || 0, max: pr.of, ticks: Math.min(pr.of, 22),
      text: `${pr.n || 0} of ${pr.of}${pr.pts ? ` · worth ≈ +${pr.pts} on ${c.label}${cycNo(c) ? ' #' + cycNo(c) : ''}` : ''}` });
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
  // the sittings In progress lists: all but the one the next test card resumes (it shows there with its meter)
  function liveList() {
    const u = D.up_next || {};
    return (D.in_progress || []).filter(r => !(u.kind === 'resume' && r.id === u.session));
  }
  function liveCard() {
    const host = $('#live');
    const list = liveList();
    host.hidden = !list.length;
    if (!list.length) return;
    host.replaceChildren(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'In progress' }), h('span', { class: 'meta', text: String(list.length) })));
    list.slice(0, 3).forEach(r => host.append(liveRow(r)));
    if (list.length > 3) host.append(btn(`Show all ${list.length}`, { cls: 'quiet', run: () => { if (sitBar) sitBar.set('status', 'in_progress'); $('#sittings').scrollIntoView({ behavior: 'smooth' }); } }));
  }
  // one row a sitting: its name; where it stands against how far, answered as blocks; which module and when.
  // Resume is .btn.sm, since the next test above already carries the page's one orange Start
  function liveRow(r) {
    const of = (r.modules || []).length > 1 || r.kind === 'section' || r.paper ? `Module ${r.module || 1} of 2 · ` : '';
    const count = r.asked || (r.kind === 'diagnostic' ? 20 : sp(r.subject).n);
    const el = h('div', { class: 'lv-row', 'data-id': r.id, tabindex: '-1' });
    const label = r.status === 'not_begun' ? 'Begin' : r.status === 'timed_out' ? 'Continue' : 'Resume';
    // In progress lists both subjects, each row named with its own ("Full section #8 · Math")
    const no = (r.full && r.full.number) || r.number;     // a full SAT's half carries the full SAT's number
    const lv = h('div', { class: 'lv-l' }, h('p', { class: 'h3', text: `${r.kind_label}${no ? ' #' + no : ''} · ${UI.subjectLabel(r.subject || 'math')}` }));
    UI.meter(lv, { label: stateLine(r), value: r.answered || 0, max: count, ticks: Math.min(count, 27), ink: true, text: `${r.answered || 0} of ${count} answered` });
    lv.append(h('p', { class: 'meta', text: `${of}started ${UI.relTime ? UI.relTime(r.started) : day(r.started)}` }));
    el.append(lv);
    const acts = h('div', { class: 'lv-acts' },
      h('a', { class: 'btn sm', href: r.href || lobby(r.id), text: label }),
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
      const was = countEls().map(c => c && c.textContent);
      const after = () => load(true).then(() => rollCounts(was));
      if (el) { el.classList.add('out'); setTimeout(after, 180); } else after();
    } catch (e) { toast(`Couldn’t discard: ${e.message}`); }
  }
  // the counts a discard changes (In progress, Your sittings) roll to their new figure: a change on screen, never a load
  const countEls = () => [$('#live .card-head .meta'), $('#sitN')];
  function rollCounts(was) {
    if (UI.roll) countEls().forEach((c, i) => { if (c && was[i] && c.textContent && c.textContent !== was[i]) { const to = c.textContent; c.textContent = was[i]; UI.roll(c, to); } });
  }

  /* ---------------- T7: How you take tests (#habits, X17): the Habits half of What moves this band */
  function habitsCard() {
    const host = $('#habits');
    host.replaceChildren();
    const H = D.habits || { rows: [] };
    if (H.from_n && H.n && H.from_n < H.n) host.append(h('p', { class: 'meta', text: `From ${H.from_n} of ${H.n} tests` }));
    const filtered = habitsView.last !== 'all' || habitsView.scope !== 'timed';
    if ((H.n || 0) >= 2 || filtered) {
      const bar = h('div', { class: 'hb-bar' });
      UI.seg(bar, [{ value: '5', label: 'Last 5' }, { value: '10', label: '10' }, { value: 'all', label: 'All' }], { value: habitsView.last, label: 'Sittings', onChange: v => loadHabits({ last: v }) });
      UI.seg(bar, [{ value: 'sections', label: 'Sections and papers' }, { value: 'timed', label: 'All timed' }], { value: habitsView.scope, label: 'Which tests', onChange: v => loadHabits({ scope: v }) });
      host.append(bar);
    }
    if ((H.n || 0) < 2 || !(H.rows || []).length) {
      // one line: what it will measure, and how far from unlocking it
      const n = Math.min(2, H.n || 0);
      host.append(h('div', { class: 'hb-empty' },
        h('span', { role: 'img', 'aria-label': `${n} of 2 timed tests` }, UI.pips ? UI.pips(2 - n, 2) : null),
        h('p', { class: 'meta', text: 'Pacing, blanks, answer changes, marking and confidence show after 2 timed tests.' })));
      return;
    }
    const list = h('ul', { class: 'hb-rows' });
    const sorted = [...H.rows].sort((a, b) => (a.verdict === 'costs' ? 0 : 1) - (b.verdict === 'costs' ? 0 : 1) || (a.points || 0) - (b.points || 0));
    sorted.forEach(r => {
      const li = h('li', { class: 'hb-row' + (r.verdict === 'costs' ? ' costs' : ' good') },
        h('span', { class: 'hb-g', 'aria-label': r.verdict === 'costs' ? 'Costs points' : 'Good', text: r.verdict === 'costs' ? '!' : '✓' }),
        h('div', { class: 'hb-t' }, h('b', { text: r.title }), h('span', { class: 'hb-ev', text: r.evidence || '' }), r.trend ? h('span', { class: 'meta', text: r.trend }) : null));
      const sp = h('span', { class: 'hb-spark' });
      if (UI.spark && (r.series || []).length > 1) UI.spark(sp, r.series, { label: r.title, w: 60, h: 20 });
      li.append(sp);
      const acts = h('span', { class: 'hb-acts' });
      if (r.action) {
        // "Hard-end practice · 10 hard at 95 s": the verb on the button, its terms beside it (a button never wraps,
        // and the long one ran past the 300px aside)
        const [verb, ...terms] = (r.action.label || 'Start').split(' · ');
        acts.append(btn(verb, { cls: 'btn sm', aria: r.action.label || null, run: b => action(r.action, b) }));
        if (terms.length) acts.append(h('span', { class: 'meta', text: terms.join(' · ') }));
      }
      if (r.why) { const w = UI.why(r.why, { label: 'Why' }); w.setAttribute('aria-label', `Why: ${r.title}`); acts.append(w); }   // the word, named for its row
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
      const r = await api(`/tests?subject=${subject}&habits_last=${habitsView.last}&habits_scope=${habitsView.scope}`, { quiet: true });
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

  const xChip = b => { if (UI.icon) b.append(UI.icon('x', 12)); return b; };    // a removable chip ends in a drawn x
  /* ---------------- active filters as removable chips under the head, at every width (X20, T6): the dropdowns
     live behind "Filters · n", so these are the only place a filter's value shows. The sort stays out beside it. */
  function activeChips(host, bar, filters, v, extra) {
    host.replaceChildren();
    filters.filter(f => f.type !== 'sort' && v[f.key]).forEach(f => {
      const o = (f.options || []).find(x => String(x.value) === String(v[f.key]));
      host.append(xChip(btn(`${f.label}: ${o ? o.label : v[f.key]}`, { cls: 'btn sm fchip', aria: `Remove the filter ${f.label}: ${o ? o.label : v[f.key]}`, run: () => bar.set(f.key, '') })));
    });
    if (extra) host.append(extra);
    host.hidden = !host.childNodes.length;
  }

  /* ---------------- T4: New test (#kinds) */
  const kindOf = id => (D.kinds || []).find(k => k.id === id);
  // a row's facts follow the subject on the switch (getters); the full SAT is both subjects and ignores it
  const rwNow = () => subject === 'rw';
  const INFO = {
    full: { title: 'Full SAT', tags: ['Reading and Writing, then Math', 'Adaptive', 'Official timing'], get facts() { return fullFacts(); }, help: 'The whole test, as on test day: a total and both section scores.', body: { kind: 'full' }, opts: { kind: 'full' } },
    section: { title: 'Full section', get tags() { return ['Adaptive', 'Official timing', rwNow() ? 'A passage with every question' : '8/7/4/3 each module']; }, get facts() { return `${secFacts()} · 2 modules`; }, body: { kind: 'section' }, opts: { kind: 'section' } },
    module1: { title: 'Module 1', tags: ['Mixed difficulty', 'Official timing'], get facts() { return modFacts(); }, body: { kind: 'module', module: 'm1' }, opts: { kind: 'modules', mods: ['m1'] } },
    module2u: { title: 'Module 2 · harder', tags: ['Fixed', 'Leans hard'], get facts() { return modFacts(); }, help: 'What a strong module 1 earns you.', body: { kind: 'module', module: 'm2u' }, opts: { kind: 'modules', mods: ['m2u'] } },
    module2l: { title: 'Module 2 · easier', tags: ['Fixed', 'Leans easy'], get facts() { return modFacts(); }, help: 'Its score tops out at 580, as on the SAT.', body: { kind: 'module', module: 'm2l' }, opts: { kind: 'modules', mods: ['m2l'] } },
    custom: { title: 'Custom test', tags: ['Your skills or mistakes', 'Test rules'], facts: '5–60 questions · you choose', help: 'No answers until you hand in, like a real module.', sheet: true, opts: { kind: 'custom' } },
    diagnostic: { title: 'Diagnostic', tags: ['All four domains evenly'], get facts() { return diagFacts(); }, help: 'Asks for your name and email before the result.', body: { kind: 'diagnostic' }, opts: { kind: 'diagnostic' } },
    twin: { title: 'Twin', get tags() { return ['Same slots', rwNow() ? 'New questions' : 'New numbers']; }, facts: 'The same length as the original',
      get help() { return rwNow() ? 'Each question the same skill, difficulty and position, never one you’ve seen: an equal test of whether you’ve improved.' : 'Each question the same kind, difficulty and position, with new numbers: an equal test of whether you’ve improved.'; }, opts: { kind: 'twin' } },
    trainer: { title: 'Route-up trainer', tags: ['Module 1', 'Official timing', 'Test-day'], get facts() { return modFacts(); }, get help() { return `The line: ${sp().route} of ${sp().n} right routes you up.`; }, body: { kind: 'module', module: 'm1', trainer: 'route', conditions: 'test_day' }, opts: { kind: 'trainer' } },
    traps: { title: 'Trap test', tags: ['Your traps', 'Test rules'], get facts() { return `6–${sp().n} questions · ${sp().pace} s each`; }, help: 'Each question offers a wrong answer you’ve picked before.', body: { kind: 'custom', custom: { source: 'traps', traps: 'all', neutral: 0.25 } }, opts: { kind: 'traps' } },
  };
  // the kind the next test is: its row keeps its Start in view, an amber tick and a Next badge
  function recommendedKind() {
    const u = D.up_next || {};
    return { full: 'full', section: 'section', module: u.preset === 'pacing' ? null : 'module1', diagnostic: 'diagnostic', trainer: 'trainer', traps: 'traps' }[u.kind] || null;
  }
  // a row's ⋯ menu: the items, and the button that opens it
  function moreBtn(items, label) {
    const more = h('button', { type: 'button', class: 'ibtn', 'aria-label': `More for ${label}`, 'aria-haspopup': 'menu' }, UI.icon ? UI.icon('more', 18) : '⋯');   // a quiet menu: a ghost icon until hover
    more.addEventListener('click', () => (UI.menu ? UI.menu(more, items, { label }) : null));
    return more;
  }
  function kindsCard() {
    const host = $('#kinds');
    host.replaceChildren();
    const tm = D.types_met || {};
    const head = h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'New test' }));
    if (tm.total && tm.tests) {
      const met = h('a', { href: '/me/#atlas?met=tests', text: `${num(tm.tests || 0)} of ${num(tm.total)} types met`, 'aria-label': `Question types met under the clock: ${num(tm.tests || 0)} of ${num(tm.total)}. Which ones?` });
      if (UI.tooltip) UI.tooltip(met, 'Question types met under the clock. Which ones?');
      head.append(h('span', { class: 'meta ts-met' }, met));
    }
    host.append(head);
    const list = h('div', { class: 'ts-list' });
    const rec = recommendedKind();
    const ids = ['full', 'section', 'module1', 'module2u', 'module2l', 'custom', 'diagnostic'];
    if (D.twin) ids.push('twin');
    ids.push('trainer', 'traps');
    // four rows show (the next test's kind, the full SAT, Full section, Module 1, Trap test), the rest behind "n more kinds"
    const four = new Set([...new Set([rec, 'full', 'section', 'module1', 'traps', ...ids].filter(Boolean))].slice(0, 4));
    const extra = [];
    ids.forEach(id => {
      const k = kindOf(id) || {};
      const I = INFO[id];
      const mine = id === rec;
      const card = h('article', { class: 'ts-card kind', 'data-kind': id, tabindex: '-1', hidden: four.has(id) ? null : true });
      if (!four.has(id)) extra.push(card);
      const title = id === 'twin' && D.twin ? `Twin of ${D.twin.label}` : I.title;
      // one line: the name, its facts, how it went for you; its tags and what it is for open with ⋯
      const items = [{ group: [I.tags.join(' · '), I.help].filter(Boolean).join(' · ') }, { separator: true }, { label: 'Options', icon: 'settings', onClick: () => options(card) }];
      if (id === 'section') items.push({ label: 'Race friends', icon: 'compete', onClick: () => race({ count: sp().n, minutes: mins(), twin: true, open_for: 72, subject }) });
      items.push({ label: 'Report a problem', icon: 'report', onClick: () => UI.report && UI.report({ kind: 'catalog', source: 'tests', page: `kind:${id}` }) });
      const bits = [];
      // no traps yet: the row says so at its end, where its Start would be (a disabled Start said nothing more)
      const none = id === 'traps' && !k.ready;
      if (id === 'traps') { if (k.ready) bits.push(`${k.ready} traps ready`); }
      else if (id === 'twin') { if (D.twin && D.twin.band) bits.push(`Original ${band(D.twin.band)}`); }
      else {
        if (k.yours) bits.push(k.last !== null && k.last !== undefined ? `You ≈${r10(k.last)}` : 'Practice');
        if (k.best !== null && k.best !== undefined && k.yours > 1) bits.push(`Best ≈${r10(k.best)}`);
      }
      if (id === 'trainer' && k.best_streak) bits.push(`Best streak ${k.best_streak}`);
      card.append(h('div', { class: 'tc-head' }, h('h3', { class: 'h3 tc-title', text: title }), mine ? h('span', { class: 'badge soft', text: 'Next' }) : null,
        h('span', { class: 'meta', text: I.facts }), bits.length ? h('span', { class: 'meta tc-line', text: bits.join(' · ') }) : null));
      const body = id === 'twin' ? { kind: 'twin', twin_of: D.twin && D.twin.source } : id === 'module2u' && k.gauntlet && k.gauntlet.shown ? Object.assign({}, I.body, { trainer: 'gauntlet' }) : I.body;
      // every Start is .btn.sm (the next test card above carries the page's one orange); the next test's row keeps
      // its Start in view, the others show theirs on hover or focus with a mouse
      const go = btn('Start', { cls: 'btn sm', aria: `Start ${title}`, run: b => (I.sheet ? S.open(I.opts) : start(body, b)) });
      const more = moreBtn(items, title);
      if (none) {
        // the words stay; only ⋯ waits for hover or focus (.reveal-host: the row, not the actions box, reveals it)
        card.classList.add('reveal-host');
        if (!mine) more.classList.add('reveal');
        card.append(h('div', { class: 'tc-acts' }, h('span', { class: 'meta', text: 'No traps ready yet' }), more));
      } else card.append(h('div', { class: 'tc-acts' + (mine ? '' : ' reveal') }, go, more));
      list.append(card);
    });
    host.append(list);
    if (extra.length) {
      let open = !!ls.get('satf.tests.moreKinds', false);
      // a disclosure: the label, then a caret that turns while open (icons.css turns a direct-child caret)
      const more = btn('', { cls: 'quiet', run: () => { open = !open; ls.set('satf.tests.moreKinds', open); sync(); if (open && UI.motion) extra.forEach((c, i) => UI.motion.enter(c, 'nudge', { delay: Math.min(i, 7) * 30 })); } });
      const lab = h('span'), caret = UI.icon ? UI.icon('caret_down', 16) : null;
      more.append(lab);
      if (caret) more.append(caret);
      const sync = () => { extra.forEach(c => { c.hidden = !open; }); lab.textContent = open ? 'Fewer kinds' : `${extra.length} more kinds`; more.setAttribute('aria-expanded', String(open)); };
      sync();
      host.append(h('div', { class: 'ts-foot' }, more));
    }
  }
  // Options for a row (the ⋯ menu's first item and the O key): the start sheet, opened on that kind or paper
  function options(card) {
    if (card.dataset.kind) { const I = INFO[card.dataset.kind]; return I ? S.open(Object.assign({ step: 1 }, I.opts)) : null; }
    if (card.dataset.paper) return S.open({ kind: 'paper', paper: +card.dataset.paper, step: 1 });
    return null;
  }
  async function race(body) {
    // Compete's private contest by invite code (decision 5): made here, the code copied, then its page opens
    try {
      const c = await api('/contests', { method: 'POST', quiet: true, body });
      const code = c.code || (c.contest && c.contest.code);
      if (!code) throw new Error('no code');
      const path = c.link || `/compete/contest/?code=${encodeURIComponent(code)}`;
      try { const m = JSON.parse(localStorage.getItem('satf.contest.codes') || '{}'); m[c.id] = code; localStorage.setItem('satf.contest.codes', JSON.stringify(m)); } catch (_) {}   // the contest page shows Copy link / Copy code for it
      if (UI.copyText) UI.copyText(new URL(path, location.origin).href, { toast: `Race made · link copied (code ${code})` });
      setTimeout(() => { location.href = path; }, 900);
    } catch (e) { toast(`Couldn’t make the race: ${e.message}`); }
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
    const barHost = h('div', { class: 'ts-bar ts-bar-head', id: 'paperFilters' });
    // what a paper is sits behind a ? beside the title, so the head is one line before the tiles
    host.append(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'Papers' }), h('span', { class: 'meta', text: String(list.length) }),
      UI.why(`The same question types in the same order for everyone, each with ${rwNow() ? 'different passages' : 'their own numbers'}. A new paper every Monday. Each paper’s blocks are what you should get right in module 1; the line at ${sp().route} routes you up.`, { about: 'papers' }), barHost));
    const chipHost = h('div', { class: 'ts-chips', hidden: true });
    host.append(chipHost);
    const gridHost = h('div', { class: 'ts-list ts-tiles' });
    const u = D.up_next || {};
    const recN = u.kind === 'paper' ? (list.find(x => x.n === u.paper) || list.find(x => x.newest) || {}).n : null;   // the next test's paper: an amber tick and a Next badge
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
        options: [['best', 'Best for me'], ['new', 'Newest'], ['old', 'Oldest'], ['hard', 'Hardest for me'], ['easy', 'Easiest for me'], ['most', 'Most sat']].map(([value, label]) => ({ value, label })) },
    ];
    const vals = v => ({ diff: v['p.diff'], status: v['p.status'], for: v['p.for'], src: v['p.src'] });
    let painted = false;
    const paint = v => (painted && UI.glide ? UI.glide(gridHost, () => draw(v)) : (painted = true, draw(v)));   // a filter or sort change glides the tiles
    const draw = v => {
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
      // ten tiles (five rows of two) before Show all (acceptance 34 wants the 7 launch papers listed)
      shownList.slice(0, papersAll ? shownList.length : 10).forEach(p => gridHost.append(paperCard(p, p.n === recN)));
      if (shownList.length > 10 && !papersAll) foot.append(btn(`Show all ${shownList.length}`, { cls: 'quiet', run: () => { papersAll = true; paint(paperBar.values()); } }));
    };
    paperBar = UI.filterBar(barHost, filters, { url: true, store: 'satf.tests.paperFilters', label: 'Paper filters', pop: true, keep: ['p.sort'], onChange: v => paint(v) });
    paint(paperBar.values());
  }
  // how the paper should go for you: a badge only when it is harder or easier than your usual (About your level on
  // nine papers in ten said nothing); its working (the expected score, the usual one, the source) is the badge's
  // tooltip and the first line of the tile's ⋯ menu; the expected score itself is the preview and the line under it
  function ratingTip(p) {
    const you = (p.rating || {}).you || {};
    if (!you.chip) return [null, null, null];
    const e1 = you.expect_m1 !== undefined ? Math.round(you.expect_m1) : null;
    const text = { harder: 'Harder for you', easier: 'Easier for you' }[you.chip];
    const { n: m1n, route } = sp(p.subject);
    const tip = [e1 !== null ? `Expect ${e1} of ${m1n} in module 1, where ${route} routes you up` : null, you.typical_m1 !== undefined ? `${Math.round(you.typical_m1)} on most papers` : null,
      you.source === 'types' ? 'from how hard its types have been' : 'from your skill ratings'].filter(Boolean).join(' · ');
    const c = text ? h('span', { class: 'badge soft', text }) : null;
    if (c && UI.tooltip) UI.tooltip(c, tip);
    return [c, tip, e1];
  }
  // the preview, a quiet well: what you should get right in module 1 as a block a question, the route line (14 of 22,
  // 17 of 27) (the meter's words stay for screen readers; the line under the name says it once); not rated yet, the
  // blocks unlit
  function paperPreview(e1, s) {
    const rated = e1 !== null && e1 !== undefined;
    const { n, route } = sp(s);
    const box = h('div', { class: 'tc-prev' + (rated ? '' : ' none') });
    UI.meter(box, rated ? { label: 'Expected in module 1', value: e1, max: n, ticks: n, tick: route, ink: true, lg: true }
      : { label: 'Not rated for you yet', value: 0, max: n, ticks: n, tick: route, ink: true, lg: true, text: `${route} routes you up` });
    return box;
  }
  // a paper tile: the preview, then its name with New and a rating that stands out, Start and ⋯ (shown on hover or
  // focus with a mouse, always on touch; the next test's tile keeps them out), then one line: your state and what to
  // expect. The set, the mistake types, the crowd and your band open with ⋯
  function paperCard(p, recommended) {
    const y = p.yours || {};
    const status = y.status || 'not_sat';
    const card = h('article', { class: 'ts-card paper', 'data-paper': String(p.n), 'data-key': `p${p.n}`, tabindex: '-1' });
    const road = String(p.source || '').startsWith('final-');
    const set = road ? `${p.label} · Season Final` : p.kind === 'launch' || p.source === 'launch' ? 'Launch set' : p.label;
    const state = { in_progress: 'In progress', completed: 'Sat' }[status];
    const trap = [p.open_traps ? `${num(p.open_traps)} of your mistake types` : null, p.types_new ? `${plural(p.types_new, 'type')} new to you` : null].filter(Boolean).join(' · ');
    const avg = p.average && typeof p.average === 'object' ? p.average.value : p.average;   // {value, n, basis} from papers.card
    const extra = [p.sat_by ? `${num(p.sat_by)} sat it` : null, avg ? `average ${Math.round(avg)}` : null,
      status === 'completed' && y.last ? `you ${band(y.last) || Math.round(y.last)}` : null].filter(Boolean).join(' · ');
    const label = status === 'in_progress' ? 'Resume' : status === 'completed' ? 'Retake' : 'Start';
    const [rate, tip, e1] = ratingTip(p);
    const about = [set, trap, extra, tip].filter(Boolean).join(' · ');
    const items = [about ? { group: about } : null, about ? { separator: true } : null, { label: 'Options', icon: 'settings', onClick: () => options(card) }];
    if (!p.gated || p.posts) items.push({ label: `Questions & discussion${p.posts ? ' ' + p.posts : ''}`, icon: 'chat', onClick: () => talk(p) });
    if (status === 'completed' && y.last_session) items.push({ label: 'Again, exactly', icon: 'again', onClick: () => start({ kind: 'paper', paper: p.n, exact: true }) });
    const ps = sp(p.subject);
    items.push({ label: 'Race friends', icon: 'compete', onClick: () => race({ paper: p.n, count: ps.n, minutes: Math.round(ps.secs / 60), twin: true, open_for: 72, subject: p.subject || subject }) },
      { label: 'Report a problem', icon: 'report', onClick: () => UI.report && UI.report({ kind: 'paper', source: 'tests', paper: p.n }) });
    const sub = [state, e1 !== null && e1 !== undefined ? `Expect ${e1} of ${ps.n} in module 1` : 'Not rated for you yet'].filter(Boolean).join(' · ');
    card.append(paperPreview(e1, p.subject), h('div', { class: 'tc-head' }, h('h3', { class: 'h3 tc-title', text: `Paper #${p.n}` }), recommended ? h('span', { class: 'badge soft', text: 'Next' }) : null,
      p.newest ? h('span', { class: 'badge line', text: 'New this week' }) : null, rate), h('p', { class: 'meta tc-sub', text: sub }));
    card.append(h('div', { class: 'tc-acts' + (recommended ? '' : ' reveal') },
      btn(label, { cls: 'btn sm', aria: `${label} Paper #${p.n}`, run: b => (status === 'in_progress' && y.live_session ? (location.href = lobby(y.live_session)) : start({ kind: 'paper', paper: p.n }, b)) }),
      moreBtn(items, `Paper #${p.n}`)));
    return card;
  }
  function talk(p, o = {}) {
    if (!window.TestsTalk) return null;
    return TestsTalk.open(p, Object.assign({ start: b => start({ kind: 'paper', paper: p.n }, b) }, o));
  }

  /* ---------------- T6: Your sittings (#sittings) */
  const TESTS = new Set(['full', 'section', 'mock', 'module', 'custom', 'diagnostic', 'paper', 'twin', 'shared']);
  function norm(r) {
    const mods = r.modules || null;
    const sum = k => (mods || []).reduce((a, m) => a + ((m[k] || []).length), 0);
    // a full SAT's half goes by the full SAT's number and name ("Full SAT #1"), never its own sitting's
    const fullNo = r.full && r.full.part && r.full.number;
    if (r.status) return Object.assign({}, r, { misses: sum('missed'), blanks: sum('blank') }, fullNo ? { number: fullNo, kind_label: 'Full SAT' } : {});
    // a /api/history row (api_results.history, or the older one): its modules name misses `wrong`; a full SAT's
    // folded entry keeps its parts
    const kind = r.kind === 'mock' ? 'section' : r.kind;
    const ms = (mods || []).map(m => Object.assign({}, m, { missed: m.missed || m.wrong || [] }));
    const missed = ms.reduce((a, m) => a + m.missed.length, 0), blanks = ms.reduce((a, m) => a + (m.blank || []).length, 0);
    return { id: r.id, kind, kind_label: fullNo ? 'Full SAT' : r.label || UI.KIND.label(r), number: fullNo || r.seq || (r.full && r.full.number) || null, status: r.finished ? 'completed' : 'in_progress', started: r.started, finished: r.finished,
      subject: r.subject, full: r.full || null, parts: r.parts || null, route: r.route, ms: r.ms, note: r.note,
      estimate: r.estimate && r.estimate.low !== undefined ? { low: r.estimate.low, high: r.estimate.high } : null, right: r.right, asked: r.asked,
      modules: ms.length ? ms : null, misses: ms.length ? missed : r.asked !== null && r.asked !== undefined && r.right !== null && r.right !== undefined ? r.asked - r.right : 0, blanks };
  }
  // a full SAT is two sittings (R&W, then Math) linked by full.id: Your sittings lists it once, both subjects, with its
  // total (the server's, 20 wide, on 400-1600). /api/history folds the finished ones ({kind: 'full', parts, estimate});
  // a part still in progress comes from in_progress with its full: {id, part}, and joins its partner here
  function fullRow(id, parts, total) {
    const secs = parts.slice().sort((a, b) => ((a.full || {}).part || 0) - ((b.full || {}).part || 0));
    const live = secs.find(s => ['in_progress', 'paused', 'not_begun', 'timed_out'].includes(s.status));
    const f = Object.assign({}, ...secs.map(s => s.full || {}));
    const done = !live && secs.length > 1;
    return { id, kind: 'full', kind_label: 'Full SAT', number: f.number || null, full: f, sections: secs,
      status: live ? live.status : done ? 'completed' : 'in_progress', href: live ? live.href || lobby(live.id) : null, live,
      started: secs[0].started, finished: done ? secs[secs.length - 1].finished : null, estimate: done ? total || f.total || null : null,
      ms: secs.reduce((a, s) => a + (s.ms || 0), 0), timing: secs[0].timing, conditions: secs[0].conditions,
      ranked: secs.every(s => s.ranked !== false), unranked_why: (secs.find(s => s.ranked === false) || {}).unranked_why, misses: secs.reduce((a, s) => a + (s.misses || 0), 0), blanks: secs.reduce((a, s) => a + (s.blanks || 0), 0),
      modules: secs.flatMap(s => (s.modules || []).map(m => Object.assign({ subject: s.subject || 'math', sid: s.id }, m))) };
  }
  // what Your sittings lists: this subject's sittings, and each full SAT once
  function listed() {
    const out = [], parts = new Map(), totals = {};
    const add = (id, r) => {
      if (!parts.has(id)) { parts.set(id, []); out.push(id); }
      if (r && !parts.get(id).some(x => x.id === r.id)) parts.get(id).push(r);
    };
    rows.forEach(r => {
      if (r.parts && r.parts.length) { add(r.id); r.parts.forEach(p => add(r.id, norm(p))); totals[r.id] = r.estimate; }
      else if (r.kind === 'full' && !(r.full && r.full.part)) out.push(Object.assign({ sections: [] }, r));   // folded, its parts not sent
      else if (r.full && r.full.id) add(r.full.id, r);
      else if (ofSubject(r)) out.push(r);
    });
    return out.map(x => (typeof x === 'string' ? fullRow(x, parts.get(x), totals[x]) : x));
  }
  // this subject's sittings, a full SAT's part among them (the estimate's chart and the route meter read these)
  const subjRows = () => rows.flatMap(r => (r.parts ? r.parts.map(norm) : [r])).filter(ofSubject);
  const kindKey = r => (r.kind === 'full' ? 'full' : r.trainer ? 'trainer' : /trap/i.test(r.kind_label || '') ? 'traps' : r.paper ? 'paper' : r.twin_of || r.kind === 'twin' ? 'twin'
    : r.shared_from || r.kind === 'shared' ? 'shared' : r.kind === 'mock' ? 'section' : r.kind);
  const SF = {
    kind: [['full', 'Full SATs'], ['section', 'Full sections'], ['paper', 'Papers'], ['module', 'Modules'], ['custom', 'Custom'], ['diagnostic', 'Diagnostics'], ['twin', 'Twins'], ['shared', 'Shared'], ['traps', 'Trap tests'], ['trainer', 'Trainer']],
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
  function sitFilter(vals, skip) { return listed().filter(r => (!onlyIds || onlyIds.ids.has(r.id)) && Object.keys(SF).every(k => k === skip || !vals[k] || sitTest[k](r, vals[k]))); }
  function sittingsCard() {
    const host = $('#sittings');
    host.replaceChildren();
    const all = listed();
    const head = h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'Your sittings' }), h('span', { class: 'meta', id: 'sitN', text: rowsState === 'ok' ? String(all.length) : '' }));
    const csv = btn('Export CSV', { cls: 'quiet', id: 'csv', run: () => exportCsv() });
    const barHost = h('div', { class: 'ts-bar ts-bar-head', id: 'filters' });
    head.append(barHost);
    host.append(head);
    const chipHost = h('div', { class: 'ts-chips', hidden: true });
    const list = h('div', { class: 'st-list', role: 'list', 'aria-label': 'Your sittings' });
    const foot = h('div', { class: 'ts-foot' });
    host.append(chipHost, list, foot, h('div', { class: 'ts-export' }, csv));   // Export sits bottom right
    cmpBar = UI.actionBar ? UI.actionBar(host, { actions: [
      { label: 'Compare', primary: true, onClick: () => compare() },
      { label: 'Clear', quiet: true, onClick: () => { picked = []; host.querySelectorAll('.sr-cmp input').forEach(x => { x.checked = false; }); pickedBar(); } }] }) : null;
    if (cmpBar) cmpBar.el.classList.add('st-cmp');
    sitPaint = null;
    if (rowsState === 'loading') { if (UI.skel) UI.skel(list, 'rows:4'); return; }
    if (rowsState === 'error') { if (UI.cardError) UI.cardError(list, () => loadRows(), 'Couldn’t load your sittings.'); return; }
    if (!all.length) {
      csv.hidden = true;
      // a dimmed sample sitting of what lands here, then the smallest action that fills it
      const sample = () => sitRow({ id: 'sample', kind: 'section', kind_label: 'Full section', number: 1, status: 'completed', started: new Date(Date.now() - 2 * 864e5).toISOString(),
        ms: (2 * mins() - 4) * 60000, timing: 'official', route: 'upper', estimate: { low: 550, high: 570 }, misses: 4, blanks: 0, subject,
        modules: [{ n: 1, right: sp().n - 3, asked: sp().n, missed: [7, 12, 19], blank: [] }, { n: 2, right: sp().n - 1, asked: sp().n, missed: [9], blank: [] }] });
      if (UI.empty) {
        const e = UI.empty(list, { sample, text: 'Nothing sat yet. Each test lands here with its band, its modules and what you missed.' });
        // first use: the mark's corners, one of four lit, above the line (UI.spotArt; never on a filtered empty)
        if (UI.spotArt && e) e.querySelector('.empty-text').insertAdjacentHTML('beforebegin', UI.spotArt('start'));
        (e || list).append(btn('Start a full section', { cls: 'quiet', run: b => start({ kind: 'section' }, b) }));
      }
      else list.append(h('div', { class: 'ts-empty' }, h('p', { text: 'Nothing sat yet.' }), btn('Start a full section', { cls: 'quiet', run: b => start({ kind: 'section' }, b) })));
      return;
    }
    const filters = [
      ...Object.entries(SF).map(([key, opts]) => ({ key, label: { kind: 'Kind', status: 'Status', route: 'Route', timing: 'Timing', cond: 'Conditions' }[key], options: opts.map(([value, label]) => ({ value, label })) })),
      { key: 'sort', label: 'Sort', type: 'sort', default: 'new', options: [['new', 'Newest'], ['old', 'Oldest'], ['high', 'Highest'], ['low', 'Lowest'], ['hard', 'Hardest'], ['easy', 'Easiest'], ['missed', 'Most missed']].map(([value, label]) => ({ value, label })) },
    ];
    let painted = false;
    const paint = v => (painted && UI.glide ? UI.glide(list, () => draw(v)) : (painted = true, draw(v)));   // a filter, sort or Show more glides the rows
    const draw = v => {
      const counts = Object.fromEntries(Object.entries(SF).map(([k, opts]) => [k, Object.fromEntries(opts.map(([o]) => [o, sitFilter(Object.assign({}, v, { [k]: o }), null).length]))]));
      Object.keys(SF).forEach(k => sitBar && sitBar.counts(k, counts[k]));
      const out = sitFilter(v).sort(SSORT[v.sort] || SSORT.new);
      list.replaceChildren();
      foot.replaceChildren();
      csv.hidden = !out.length;
      activeChips(chipHost, sitBar, filters, v, onlyIds ? xChip(btn(`Only: ${onlyIds.label}`, { cls: 'btn sm fchip', aria: `Show every sitting, not only ${onlyIds.label}`, run: () => { onlyIds = null; paint(sitBar.values()); } })) : null);
      if (!out.length) { list.append(h('div', { class: 'ts-empty' }, h('p', { text: 'No sittings match these filters.' }), btn('Clear filters', { cls: 'btn sm', run: () => sitBar.clear() }))); return; }
      out.slice(0, shown).forEach(r => list.append(sitRow(r)));
      if (out.length > shown) foot.append(btn(`Show ${Math.min(20, out.length - shown)} more`, { cls: 'quiet', run: () => { shown += 20; paint(sitBar.values()); } }));
      list.dataset.count = String(Math.min(out.length, shown));
      pickedBar();
    };
    sitBar = UI.filterBar(barHost, filters, { url: true, store: 'satf.tests.filters', label: 'Sitting filters', pop: true, keep: ['sort'], onChange: v => { shown = 20; paint(v); } });
    sitPaint = () => paint(sitBar.values());
    sitPaint();
  }
  function missChips(r) {
    const box = h('span', { class: 'sr-miss' });
    const mods = r.modules || [];
    let left = innerWidth < 760 ? 6 : 8, shownN = 0;
    // a full SAT's four modules share the row: two chips each, so every module that has a miss shows one
    const each = r.kind === 'full' ? 2 : Infinity;
    mods.forEach(m => {
      const all = [...(m.missed || []).map(p => ['incorrect', p]), ...(m.blank || []).map(p => ['blank', p])].sort((a, b) => a[1] - b[1]);
      if (!all.length || left <= 0) return;
      // a full SAT's chips say their section ("R&W M1"); each opens its own section's report
      // (a sitting of one block, a diagnostic or a custom test, has no module number)
      const name = [r.kind === 'full' ? UI.subjectLabel(m.subject, true) : '', m.n ? `M${m.n}` : ''].filter(Boolean).join(' ');
      const g = h('span', { class: 'sr-mg' }, name ? h('span', { class: 'k', text: name }) : null);
      all.slice(0, each).forEach(([st, p]) => {
        if (left <= 0) return;
        left--; shownN++;
        const said = `${name ? name + ' ' : ''}Q${p} · ${st === 'blank' ? 'blank' : 'wrong'}`;
        g.append(UI.cell(st, p, { href: report(m.sid || r.id, m.n ? `M${m.n}-${p}` : String(p)), size: 'sm', label: said, tip: said }));
      });
      box.append(g);
    });
    const total = mods.reduce((a, m) => a + (m.missed || []).length + (m.blank || []).length, 0);
    if (total > shownN) box.append(h('span', { class: 'meta', text: `+${total - shownN}` }));
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
    const tips = {};
    const g = r.gate && r.gate.margin;
    if (g !== undefined && g !== null) {
      const t = g >= 0 ? `Route line +${g}` : `Route line −${-g}`;
      c.push(t);
      tips[t] = g >= 0 ? `Module 1: ${g} more right than the harder module 2 needed` : `Module 1: ${-g} short of the harder module 2`;
    }
    const pb = r.pressure && r.pressure.buckets;
    if (pb && ((pb.pressure || []).length || (pb.knowledge || []).length)) c.push(`Pressure ${(pb.pressure || []).length} · Knowledge ${(pb.knowledge || []).length}`);
    if (r.pass2 && r.pass2.pts) { const t = `Second pass +${r.pass2.pts}`; c.push(t); tips[t] = 'Points from questions you came back to and got right'; }
    return h('span', { class: 'sr-chips' }, c.map(t => { const b = h('span', { class: 'badge soft', text: t }); if (tips[t] && UI.tooltip) UI.tooltip(b, tips[t]); return b; }));
  }
  function sitRow(r) {
    if (r.kind === 'full') return fullSitRow(r);
    const live = ['in_progress', 'paused', 'not_begun'].includes(r.status);
    const el = h('div', { class: 'sr-row', role: 'listitem', 'data-id': r.id, 'data-key': r.id, tabindex: '-1' });
    const mods = r.modules || [];
    const score = band(r.estimate) || (r.right !== null && r.right !== undefined && r.asked ? `${r.right}/${r.asked}` : live ? '' : 'Practice');
    const sub = [r.paper || r.kind === 'section' || r.kind === 'mock' ? (r.fixed_route ? 'fixed route' : 'adaptive') : null,
      r.timing && r.timing !== 'official' ? { 'x1.5': 'time and a half', x2: 'double time', untimed: 'untimed', 'x0.85': 'tight clock' }[r.timing] : 'official'].filter(Boolean).join(' · ');
    const when = r.started ? `${day(r.started)} · ${new Date(r.started).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', hour12: false })}` : '';
    const mins = r.ms >= 30000 ? Math.round(r.ms / 60000) : null;
    // one tidy line: tick, date, what it was, the score, the modules, the actions; the misses and a note sit under it
    const cb = live ? null : h('input', { type: 'checkbox', 'aria-label': `Compare ${r.kind_label}${r.number ? ' #' + r.number : ''}` });
    if (cb) { cb.checked = picked.includes(r.id); cb.addEventListener('change', () => pick(r.id, cb.checked)); }
    const noteEl = h('p', { class: 'sr-note', text: r.note || '', hidden: !r.note });
    const acts = h('div', { class: 'sr-acts' });
    if (live) acts.append(h('a', { class: 'btn sm', href: r.href || lobby(r.id), text: r.status === 'not_begun' ? 'Begin' : 'Resume' }));
    else {
      acts.append(h('a', { class: 'btn sm', href: report(r.id), text: 'Review' }));
      if (r.misses || r.blanks) acts.append(btn(`Fix ${r.misses + r.blanks}`, { cls: 'quiet', run: b => drill({ from_session: r.id, scope: 'misses', source: 'fix' }, b) }));
    }
    const items = [];
    if (!live) {
      if (['section', 'mock', 'module', 'paper', 'twin', 'shared'].includes(r.kind) || r.paper) items.push({ label: 'Twin', icon: 'twin', sub: r.subject === 'rw' ? 'same skills, new questions' : 'same kinds, new numbers', onClick: () => start({ kind: 'twin', twin_of: r.id }) });
      if (r.paper) items.push({ label: 'Retake', icon: 'again', onClick: () => start({ kind: 'paper', paper: r.paper }) });
      if (r.route === 'lower') items.push({ label: 'Try the harder module 2', icon: 'up', onClick: () => start({ kind: 'module', module: 'm2u' }) });
      items.push({ label: 'Share', icon: 'link', onClick: () => share(r) });
    }
    items.push({ label: r.note ? 'Edit note' : 'Note', icon: 'note', onClick: () => editNote(r, el, noteEl, { focus() {}, textContent: '' }) });
    acts.append(moreBtn(items, r.kind_label));
    const sm = [mods[0] ? `M1 ${mods[0].right}/${mods[0].asked}` : null, mods[1] ? `M2 ${mods[1].right}/${mods[1].asked}` : null].filter(Boolean);
    const miss = missChips(r);
    el.append(h('div', { class: 'sr-l1' },
      // label.sr-cmp is what X, the compare bar's Clear and a dropped third pick look for (.sr-cmp input)
      cb ? h('label', { class: 'sr-cmp', title: 'Tick two to compare' }, cb) : h('span', { class: 'sr-cmp' }),
      h('span', { class: 'sr-d' }, h('b', { text: when.split(' · ')[0] }), h('span', { text: mins !== null ? `${r.timing === 'untimed' ? 'Untimed · ' : ''}${mins} min` : '' })),
      h('span', { class: 'sr-k' }, h('b', { text: (r.number ? `#${r.number} ` : '') + r.kind_label + (r.retake ? ` · Retake ${r.retake}` : '') }), h('span', { class: 'sr-ks', text: live ? stateLine(r) : sub })),
      h('span', { class: 'sr-s' }, h('b', { class: 'sr-band', text: score }), h('span', { class: 'sr-ks', text: sm.join(' · ') })),
      acts),
      h('div', { class: 'sr-l2' }, scoreChips(r), miss.childNodes.length ? miss : null, noteEl));
    return el;
  }
  // a full SAT's one row: the total (400-1600) where a section's band sits, each section's band under it, Review opens
  // the full result page and the section reports are in the ⋯ menu; no Compare tick (sections compare with sections)
  function fullSitRow(r) {
    const live = !!r.live;
    const el = h('div', { class: 'sr-row', role: 'listitem', 'data-id': r.id, 'data-key': r.id, tabindex: '-1' });
    const secs = r.sections || [];
    const parts = secs.map(s => `${UI.subjectLabel(s.subject, true)} ${band(s.estimate) || (live && s === r.live ? 'now' : '')}`.trim());
    const mins = r.ms >= 30000 ? Math.round(r.ms / 60000) : null;
    const acts = h('div', { class: 'sr-acts' });
    if (live) acts.append(h('a', { class: 'btn sm', href: r.href || lobby(r.live.id), text: r.status === 'not_begun' ? 'Begin' : 'Resume' }));
    else acts.append(h('a', { class: 'btn sm', href: fullHref(r.id), text: 'Review' }));
    acts.append(moreBtn(secs.filter(s => s.status === 'completed').map(s => ({ label: `${UI.subjectLabel(s.subject)} report`, icon: 'report', onClick: () => { location.href = report(s.id); } })), r.kind_label));
    const state = live ? `${UI.subjectLabel(r.live.subject)} · ${r.live.status === 'not_begun' && r.live.subject === 'math' ? 'after the break' : stateLine(r.live)}` : 'R&W, then Math';
    const miss = missChips(r);
    el.append(h('div', { class: 'sr-l1' }, h('span', { class: 'sr-cmp' }),
      h('span', { class: 'sr-d' }, h('b', { text: r.started ? day(r.started) : '' }), h('span', { text: mins !== null ? `${mins} min` : '' })),
      h('span', { class: 'sr-k' }, h('b', { text: (r.number ? `#${r.number} ` : '') + r.kind_label }), h('span', { class: 'sr-ks', text: state })),
      h('span', { class: 'sr-s' }, h('b', { class: 'sr-band', text: band(r.estimate) || '' }), h('span', { class: 'sr-ks', text: parts.join(' · ') })),
      acts),
      h('div', { class: 'sr-l2' }, scoreChips(r), miss.childNodes.length ? miss : null));
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
    const [a, b] = picked.map(tagOf);
    // two sittings of the same name ("Full section and Full section") say what they are once
    const both = a === b ? `Compare these 2 sittings${a && !a.startsWith('#') ? ` (${a.toLowerCase()})` : ''}` : `Compare ${a} and ${b}`;
    cmpBar.set(picked.length === 2 ? both : picked.length === 1 ? `${a} · tick one more to compare` : '', picked.length);
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
        // Saving, then Saved with a drawn check in the button, then the editor closes (no toast)
        const put = () => api(`/session/${encodeURIComponent(r.id)}/note`, { method: 'PUT', body: { text: ta.value.slice(0, 1000) } });
        try {
          await (UI.saving ? UI.saving(b, put) : put());
          r.note = ta.value.trim(); noteEl.textContent = r.note; noteEl.hidden = !r.note; trigger.textContent = r.note ? 'Edit note' : 'Note';
          setTimeout(() => { box.remove(); trigger.focus(); }, UI.saving ? 700 : 0);
        } catch (e) { toast(`Note not saved: ${e.message}`); }
      } })));
    el.append(box);
    ta.focus();
  }
  // a Copy button says Copying, then Copied with a drawn check, in place of a toast
  // (the share link is made on its first Copy: the button is busy while it is)
  const copied = async (x, text) => {
    let t = null;
    x.setAttribute('aria-busy', 'true');
    try { t = await text(); } catch (_) {} finally { x.removeAttribute('aria-busy'); }
    if (t) UI.copyText(t, { button: x });
  };
  function share(r) {
    if (!UI.sheet) return null;
    let fresh = true, showScore = true, link = null, how = 'link';
    const who = `${r.kind_label}${r.number ? ' #' + r.number : ''}`;
    return UI.sheet({ title: `Share ${who}`, size: 'm', className: 'share-sheet', body: b => {
      const linkBox = h('div', { class: 'sh-pane' }), raceBox = h('div', { class: 'sh-pane', hidden: true });
      b.append(h('p', { class: 'k', text: 'How' }));
      UI.seg(b, [{ value: 'link', label: 'Any time (a link)' }, { value: 'race', label: 'A race with a deadline' }], { value: 'link', label: 'How',
        onChange: v => { how = v; linkBox.hidden = how !== 'link'; raceBox.hidden = how !== 'race'; } });
      b.append(linkBox, raceBox);
      // a link: twins by default, or exactly these questions
      const help = h('p', { class: 'help' });
      // one line under the seg: what they sit, then what they and you see
      const say = () => { help.textContent = `${fresh ? `The same question types in the same order, with ${r.subject === 'rw' ? 'different passages' : 'their own numbers'}, so answers can’t be passed around.` : 'The same questions as yours.'} They see no answers until they finish; you see how they did, question by question.`; };
      const field = h('input', { class: 'field', readonly: true, 'aria-label': 'Share link', placeholder: 'Copy makes the link' });
      const reset = () => { link = null; field.value = ''; };
      linkBox.append(h('p', { class: 'k', text: 'What they sit' }));
      UI.seg(linkBox, [{ value: 'twins', label: 'Twins' }, { value: 'exact', label: 'Exactly these questions' }], { value: 'twins', label: 'What they sit', onChange: v => { fresh = v === 'twins'; say(); reset(); } });
      say();
      linkBox.append(help);
      UI.switch(linkBox, { label: 'Show my score to people who sit it', checked: true, onChange: v => { showScore = v; reset(); } });
      const make = async () => {
        try {
          const s2 = await api('/sets', { method: 'POST', body: { kind: 'test', session: r.id, show_score: showScore, cfg: { fresh } } });
          link = new URL(s2.url || `/tests/?shared=${encodeURIComponent(s2.code)}`, location.origin).href;
          field.value = link;
        } catch (e) { toast(`Couldn’t make the link: ${e.message}`); throw e; }
      };
      // Copy makes the link the first time, then copies: Copying, then Copied with a drawn check, in place
      linkBox.append(h('div', { class: 'sh-link' }, field, btn('Copy', { cls: 'pill sm', run: x => copied(x, async () => { if (!link) await make(); return link; }) })));
      if (navigator.share) linkBox.append(btn('More ways to share', { cls: 'quiet', run: async x => {
        if (!link) { x.setAttribute('aria-busy', 'true'); try { await make(); } catch (_) {} finally { x.removeAttribute('aria-busy'); } }
        if (link) navigator.share({ url: link, title: 'SAT Freshman test' }).catch(() => {});
      } }));
      // a race: Compete's private contest by invite code (decision 5: no classes, no roles)
      const rs = sp(r.subject);
      raceBox.append(h('p', { class: 'help', text: `Module 1’s question types as twins: ${rs.n} questions, ${Math.round(rs.secs / 60)} minutes, open for 3 days. Anyone with the code joins; Compete keeps the board.` }));
      const out = h('div', { class: 'sh-race', hidden: true });
      const create = btn('Create the race', { cls: 'pill sm', run: async x => {
        x.setAttribute('aria-busy', 'true');
        const body = { from_session: r.id, count: rs.n, minutes: Math.round(rs.secs / 60), twin: true, open_for: 72 };
        try {
          const c = await api('/contests', { method: 'POST', quiet: true, body });
          const code = c.code || (c.contest && c.contest.code);
          if (!code) throw new Error('no code');
          const url2 = new URL(c.url || `/compete/contest/?code=${encodeURIComponent(code)}`, location.origin).href;
          const f = h('input', { class: 'field', readonly: true, value: url2, 'aria-label': 'Race link' });
          out.replaceChildren(h('p', { class: 'sh-code' }, h('span', { class: 'k', text: 'Invite code' }), h('b', { class: 'mono', text: code }),
            btn('Copy code', { cls: 'quiet', run: x => copied(x, () => code) })), h('div', { class: 'sh-link' }, f, btn('Copy', { cls: 'pill sm', run: x => copied(x, () => url2) })));
          out.hidden = false;
          create.hidden = true;
        } catch (e) { toast(`Couldn’t make the race: ${e.message}`); }
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
    // a full SAT's modules run R&W M1, R&W M2, Math M1, Math M2; its band is the total
    const head = ['number', 'date', 'kind', 'subject', 'band', ...Array.from({ length: nMods }, (_, i) => `module ${i + 1}`), 'route', 'conditions', 'ranked', 'timing', 'minutes', 'misses', 'blanks', 'note'];
    const lines = [head.join(',')].concat(out.map(r => [r.number || '', r.started ? new Date(r.started).toLocaleDateString('en-CA') : '', r.kind_label, r.kind === 'full' ? 'both' : r.subject || 'math', band(r.estimate) || '',
      ...Array.from({ length: nMods }, (_, i) => ((r.modules || [])[i] ? `${r.modules[i].right}/${r.modules[i].asked}` : '')),
      r.route || '', r.conditions || '', r.ranked === undefined ? '' : r.ranked ? 'yes' : 'no', r.timing || '', r.ms ? Math.round(r.ms / 60000) : '',
      r.misses || 0, r.blanks || 0, r.note || ''].map(esc).join(',')));
    const a = h('a', { href: URL.createObjectURL(new Blob([lines.join('\n') + '\n'], { type: 'text/csv;charset=utf-8' })), download: 'sat-freshman-sittings.csv' });
    document.body.append(a); a.click(); a.remove();
  }

  /* ---------------- How scoring works (#howScored) */
  function howScored() {
    if (!UI.sheet) return;
    const { n, route } = sp();
    const pts = [
      `Every test is built when you start it, from questions you haven’t seen. Papers give everyone the same question types in the same slots, each with ${subject === 'rw' ? 'different passages' : 'their own numbers'}.`,
      'The estimate comes from how many you got right and which module 2 you reached.',
      'Every score is a range 20 points wide: a section on 200–800 (say 540–560), a full SAT’s total on 400–1600 (say 1290–1310), the two sections’ middles added. It is an estimate from our questions, not a College Board score.',
      `The route: ${route} of ${n} right in module 1 (60%) earns the harder module 2, which can reach 800. The easier module 2 tops out at 580, as on the SAT${subject === 'rw' ? ' (College Board publishes 580 for Math; Reading and Writing uses the same cap here)' : ''}.`,
      'A harder or easier module 1, a single module 2 and custom tests are practice, not a score estimate.',
      'Test-day sittings rank; Training sittings keep their score and never rank. Pausing, extended time, a fixed route, a break of more than 75 s between modules, a full SAT’s break past 11 minutes or more than 2 minutes away also keeps the score and drops the rank. Losing Wi-Fi doesn’t.',
      'Combined, paper stats and every percentile count ranked first sittings only, from 20 of them.',
      'A pressure check never changes a band. A question removed after a report (a wrong key, no right answer) leaves both right and asked.',
      'Confidence: High takes 3 sections in 30 days within 100 points; one section is Medium; a module or the diagnostic is Low.',
      'Floor-score sittings still count.',
    ];
    const cal = D && D.calibration;
    pts.push(cal && cal.checked >= 50 ? `Checked against ${num(cal.checked)} Bluebook and official scores.` : 'Not yet checked against real scores.');
    UI.sheet({ title: 'How scoring works', size: 'm', body: b => {
      // the route, drawn: module 1 forks to the harder module 2 (amber) or the easier one
      const fork = UI.s('svg', { class: 'hs-fork', viewBox: '0 0 56 100', preserveAspectRatio: 'none', 'aria-hidden': 'true' });
      UI.s('path', { class: 'down', d: 'M0 50 H14 C34 50 30 78 56 78' }, fork);
      UI.s('path', { class: 'up', d: 'M0 50 H14 C34 50 30 22 56 22' }, fork);
      b.append(h('div', { class: 'hs-route', role: 'img', 'aria-label': `Module 1: ${route} of ${n} right routes to the harder module 2 (up to 800); fewer, to the easier module 2 (up to 580)` },
        h('span', { class: 'hs-box', text: 'Module 1' }), h('span', { class: 'hs-forkbox' }, fork),
        h('span', { class: 'hs-split' }, h('span', { class: 'hs-box on', text: `${route} of ${n} right: harder module 2, up to 800` }), h('span', { class: 'hs-box', text: 'Fewer: easier module 2, up to 580' }))));
      b.append(h('ul', { class: 'hs-list' }, pts.map(t => h('li', { text: t }))));
    } });
  }

  /* ---------------- keys (X23): J / K move, Enter starts, O options, F filters */
  function keys() {
    if (!UI.keys || !UI.keys.register) return;
    const items = () => [...document.querySelectorAll('.lv-row, .ts-card, .sr-row')].filter(e => e.offsetParent && !e.closest('[inert]'));
    const move = d => { const l = items(); if (!l.length) return; const i = l.indexOf(document.activeElement); const n = l[Math.max(0, Math.min(l.length - 1, i < 0 ? 0 : i + d))]; n.focus(); n.scrollIntoView({ block: 'nearest' }); };
    const cur = () => document.activeElement && document.activeElement.closest && document.activeElement.closest('.lv-row, .ts-card, .sr-row');
    UI.keys.register('tests', {
      J: { does: 'Next card or row', run: () => move(1) },
      K: { does: 'Previous card or row', run: () => move(-1) },
      Enter: { does: 'Start, or resume a paused row', run: () => { const c = cur(); if (!c) return false; const b = c.querySelector('.lv-acts > :first-child, .tc-acts > :first-child, .sr-acts > a, .sr-acts > button'); if (b) b.click(); return undefined; } },
      O: { does: 'Options (new tests and papers)', run: () => { const c = cur(); if (!c || !options(c)) return false; return undefined; } },
      D: { does: 'Questions & discussion (papers)', run: () => { const c = cur(); const p = c && c.dataset.paper && (D.papers || []).find(x => String(x.n) === c.dataset.paper); if (p && (!p.gated || p.posts)) talk(p); else return false; return undefined; } },
      X: { does: 'Compare (rows)', run: () => { const c = cur(); const cb = c && c.querySelector('.sr-cmp input'); if (!cb) return false; cb.checked = !cb.checked; cb.dispatchEvent(new Event('change')); return undefined; } },
      F: { does: 'Filters', run: () => { const b = document.querySelector('#papers .filters-open, #sittings .filters-open'); if (b) b.focus(); } },
    }, { label: 'Tests' });
  }

  /* ---------------- load and paint */
  // the section bar's chips, in the order the page shows them; under 1280px the aside sits below the main
  // column, so the estimate and Habits get chips there too (at 1280+ the aside is always in view)
  function sections() {
    const list = [];
    if (liveList().length) list.push({ id: 'live', label: `In progress ${liveList().length}` });
    if (D.cycle) list.push({ id: 'cycle', label: 'Test, fix, prove' });
    list.push({ id: 'kinds', label: `New test ${document.querySelectorAll('#kinds .ts-card').length}` });
    list.push({ id: 'papers', label: `Papers ${(D.papers || []).length}` });
    list.push({ id: 'sittings', label: `Your sittings${rowsState === 'ok' && rows.length ? ' ' + rows.length : ''}` });
    if (!matchMedia('(min-width: 1280px)').matches) {
      const H = D.habits || {};
      list.push({ id: 'score', label: 'Estimate' }, { id: 'habits', label: `Habits${(H.rows || []).length ? ' ' + H.rows.length : ''}` });
    }
    UI.sections(list);
  }
  function paint() {
    if (!D) return;
    ['#next', '#levers'].forEach(id => { $(id).hidden = false; });
    S.use(D, rows);
    try { scoreCard(); } catch (e) { console.error(e); if (UI.cardError) UI.cardError($('#score'), () => load(true), 'Couldn’t load your score.'); }
    nextCard(); cycleCard(); liveCard(); leversCard(); kindsCard(); papersCard();
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
    ['#score', '#next', '#moves', '#kinds', '#papers', '#sittings'].forEach(id => { const el = $(id); if (el && UI.skel) { el.replaceChildren(); UI.skel(el, id === '#kinds' || id === '#papers' ? 'rows:4' : 'lines:3'); } });
  }
  async function load(fresh) {
    if (!D) skeleton();
    try {
      if (UI.cached && !fresh) {
        await new Promise((resolve, reject) => {
          let done = false;
          UI.cached(`/tests?subject=${subject}`, (d, fromCache) => { D = d; paint(); if (!done) { done = true; resolve(); } }, { key: `satf.tests.v2.${subject}`, store: 'session' }).catch(e => { if (!done) { done = true; reject(e); } });
        });
      } else { D = await api(`/tests?subject=${subject}`); paint(); }
    } catch (e) {
      if (!D) {
        const text = { '#score': 'Couldn’t load your score.', '#kinds': 'Couldn’t load the test kinds.', '#papers': 'Couldn’t load papers.' };
        Object.keys(text).forEach(id => { const el = $(id); el.replaceChildren(); if (UI.cardError) UI.cardError(el, () => load(true), text[id]); });
        ['#next', '#levers'].forEach(id => { $(id).hidden = true; });
      }
      return;
    }
    await loadRows();
  }

  // the subject switch under the title (in the URL): a switch reloads that subject's estimate, kinds and papers; the
  // sittings are all here already and the list filters
  if (UI.subjectSeg) UI.subjectSeg($('#subject'), { value: subject, onChange: v => { subject = v; S.subject = v; shown = 20; load(); } });
  $('#howBtn').addEventListener('click', () => howScored());
  // the section bar's Habits chip: open that half of What moves this band before it scrolls there
  $('#habits').addEventListener('satf:open', () => { leversView = 'habits'; if (leversSeg && leversSeg.set) leversSeg.set('habits'); syncLevers(); });
  keys();
  load().then(() => {
    // deep links: ?start=…, ?shared=CODE (the start sheet), ?compare=a,b (X18)
    const st = url.get('start'), shared = url.get('shared');
    if (shared) S.open({ shared, kind: 'shared', step: 1 });
    else if (st) {
      const m = /^paper:(\d+)$/.exec(st);
      const map = { full: { kind: 'full', step: 0 }, section: { kind: 'section', step: 1 }, modules: { kind: 'modules' }, module1: { kind: 'modules', mods: ['m1'] }, module2u: { kind: 'modules', mods: ['m2u'] },
        module2l: { kind: 'modules', mods: ['m2l'] }, custom: { kind: 'custom' }, diagnostic: { kind: 'diagnostic', step: 0 }, twin: { kind: 'twin' }, traps: { kind: 'traps' }, trainer: { kind: 'trainer' } };
      S.open(m ? { kind: 'paper', paper: +m[1], step: 1 } : map[st] || {});
    }
    const cmp = url.get('compare');
    if (cmp) compare(cmp.split(',').filter(Boolean).slice(0, 2));
    // older links into the page: #history is Your sittings; #section and #module open the start sheet on that test
    const alias = { history: 'sittings' }[location.hash.slice(1)];
    if (!st && !shared && location.hash === '#section') S.open({ kind: 'section', step: 1 });
    else if (!st && !shared && location.hash === '#module') S.open({ kind: 'modules', mods: ['m1'] });
    else if (location.hash) { const el = document.getElementById(alias || location.hash.slice(1)); if (el) el.dispatchEvent(new CustomEvent('satf:open', { bubbles: true })); if (el && !el.hidden) el.scrollIntoView(); }
  });
})();
