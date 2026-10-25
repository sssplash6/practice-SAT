/* ============================================================================
   The leaderboard /compete/leaderboard/ (spec/rebuild-v2.md 3.7 §5; compete.md C5, C6,
   C9, C10, C11, C14, C16, C17, C24, C27; R3: Questions right over 7 days is the practice rank)
   Controls live in the URL (?metric&period&scope&domain&subject&at&sort). A switch paints
   from the in-page cache at once and revalidates (C24); the other scopes prefetch when idle.
   ========================================================================== */
(() => {
  const h = UI.h, C = UI.compete, $ = s => document.querySelector(s);
  const num = C.num, mmss = C.mmss;
  const api = (p, o) => UI.api(p, o);
  const U = new URLSearchParams(location.search);
  const S = { metric: U.get('metric') || 'points', period: U.get('period') || 'week', scope: U.get('scope') || 'all',
    domain: U.get('domain') || '', subject: UI.subject.get(), at: U.get('at') || '', sort: U.get('sort') || 'value', data: null, board: null, pars: null, at0: 0 };
  // the subject's domains as [name, short] (R&W's names are short enough already)
  const domainsOf = () => (S.subject === 'rw' ? (UI.RW_DOMAINS || []).map(d => [d.name, d.name]) : UI.DOMAINS || []);
  const dailyOf = () => (S.subject === 'rw' ? 'daily-rw' : 'daily');
  const METRICS = [
    { value: 'points', label: 'Points', short: 'Points', col: 'Points', help: '10 / 20 / 30 for each easy / medium / hard answer right in ranked contests, +5 within each question’s time budget, +10 for finishing. A sprint counts its best run each week.' },
    { value: 'net', label: 'Over expected', short: 'Exp.', col: 'Over expected', help: 'Base points minus your par, over ranked contests. Beat what a student at your rating is expected to score. Placed students with 3 sittings in the period.' },
    { value: 'rating', label: 'Contest rating', short: 'Rating', col: 'Contest rating', help: 'Contest rating moves only on ranked contest answers, weighted by how hard each question is. One rating for each subject. Level 1–10.' },
    { value: 'skill', label: 'Skill rating', short: 'Skill', col: 'Skill rating', help: 'From every first try in practice, tests and contests. Contest rating counts ranked contests only.' },
    { value: 'right', label: 'Questions right', short: 'Right', col: 'Right', help: 'Right answers in any mode: practice, tests, contests.' },
    { value: 'test', label: 'Test score', short: 'Test', col: 'Section score', help: 'Best timed full section in the period, by the middle of its 20-point estimate.' },
    { value: 'climb', label: 'Climb', short: 'Climb', col: 'Climb', help: 'Gain since your first scored section, among students who started near you.' },
  ];
  const PERIODS = [{ value: '7d', label: '7 days', short: '7d' }, { value: 'week', label: 'Week', short: 'Week' }, { value: 'month', label: 'Month', short: 'Month' },
    { value: 'season', label: 'Season', short: 'Season' }, { value: 'year', label: 'Year', short: 'Year' }, { value: 'all', label: 'All time', short: 'All' }];
  const NO_PERIOD = { rating: 'Contest rating is one number a subject: the period decides who is listed.', skill: 'A Skill rating has no period.', climb: 'Climb runs since you started.' };
  const cache = new Map();
  const mOf = () => METRICS.find(m => m.value === S.metric) || METRICS[0];
  // a stale or hand-edited link falls back to the defaults instead of a 422
  if (!METRICS.some(m => m.value === S.metric)) S.metric = 'points';
  if (!PERIODS.some(p => p.value === S.period)) S.period = 'week';
  if (!['all', 'near', 'following', 'level', 'country', 'exam'].includes(S.scope)) S.scope = 'all';

  $('#subnav').replaceWith(C.subnav('leaderboard'));
  // one subject a board (no mixing); a domain belongs to one subject, so a switch clears it
  UI.subjectSeg($('#subject'), { value: S.subject, onChange: v => { S.subject = v; S.domain = ''; S.pars = null; go(); } });

  /* ------------------------------------------------------------ periods: ids for the ‹ › stepper (C27) */
  const pad = n => String(n).padStart(2, '0');
  function isoWeek(d) {
    const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    const day = t.getUTCDay() || 7; t.setUTCDate(t.getUTCDate() + 4 - day);
    const y0 = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
    return `${t.getUTCFullYear()}-W${pad(Math.ceil(((t - y0) / 864e5 + 1) / 7))}`;
  }
  function weekStart(id) { const [y, w] = id.split('-W').map(Number); const d = new Date(Date.UTC(y, 0, 4)); const day = d.getUTCDay() || 7; d.setUTCDate(d.getUTCDate() - day + 1 + (w - 1) * 7); return d; }
  function stepAt(dir) {
    const now = new Date();
    if (S.period === 'week') {
      const cur = S.at ? weekStart(S.at) : weekStart(isoWeek(now));
      cur.setUTCDate(cur.getUTCDate() + dir * 7);
      const id = isoWeek(new Date(cur.getUTCFullYear(), cur.getUTCMonth(), cur.getUTCDate()));
      return id >= isoWeek(now) ? '' : id;
    }
    if (S.period === 'month') {
      const [y, m] = (S.at || `${now.getFullYear()}-${pad(now.getMonth() + 1)}`).split('-').map(Number);
      const d = new Date(y, m - 1 + dir, 1);
      const id = `${d.getFullYear()}-${pad(d.getMonth() + 1)}`;
      return id >= `${now.getFullYear()}-${pad(now.getMonth() + 1)}` ? '' : id;
    }
    if (S.period === 'year') { const y = Number(S.at || now.getFullYear()) + dir; return y >= now.getFullYear() ? '' : String(y); }
    return null;
  }
  const periodName = () => {
    if (!S.at) return { week: 'This week', month: 'This month', year: 'This year', season: 'This season', '7d': 'Last 7 days', all: 'All time' }[S.period];
    if (S.period === 'week') return `Week ${Number(S.at.split('-W')[1])}`;
    if (S.period === 'month') { const [y, m] = S.at.split('-').map(Number); return new Date(y, m - 1, 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }); }
    if (S.period === 'season') return `Road to ${C.dayLabel(S.at.slice(5), { weekday: false })}`;
    return S.at;
  };

  /* ------------------------------------------------------------ controls */
  function sync() {
    const q = new URLSearchParams();
    q.set('metric', S.metric); q.set('period', S.period); q.set('scope', S.scope);
    if (S.domain) q.set('domain', S.domain);
    q.set('subject', S.subject);
    if (S.at) q.set('at', S.at);
    if (S.metric === 'rating' && S.sort === 'change') q.set('sort', 'change');
    history.replaceState(null, '', `?${q}`);
  }
  // from 1280px the controls sit in the side column: the metric as a list of rows, the period as one seg, the
  // stepper under it, who and which domain, Find. Below that they wait in a sheet behind one summary button on the
  // title row ("Points · This week · Everyone"), so the podium leads
  const SCOPES = [['all', 'Everyone'], ['near', 'Near me'], ['following', 'Following'], ['level', 'My level'], ['country', 'Country'], ['exam', 'Same exam date']];
  function renderControls() {
    const box = $('#ctl');
    box.replaceChildren();
    const m = mOf();
    const list = h('div', { class: 'lb-metrics', role: 'group', 'aria-label': 'Metric' }, METRICS.map(x => {
      const b = h('button', { type: 'button', class: 'choice-row', 'aria-pressed': String(x.value === S.metric), text: x.label });
      b.addEventListener('click', () => { if (x.value !== S.metric) setMetric(x.value); });
      return b;
    }));
    box.append(h('div', { class: 'k-row' }, h('span', { class: 'k', text: 'Ranked by' }), C.info(m.help, `About ${m.label}`)), list);
    if (S.metric === 'rating') {
      const r = h('div', { class: 'row' }, h('span', { class: 'meta', text: 'Sort:' }));
      C.under(r, [{ value: 'value', label: 'Rating' }, { value: 'change', label: 'Change' }], { value: S.sort, label: 'Sort', onChange: v => { S.sort = v; go(); } });
      box.append(r);
    }
    // the period: one seg; a metric with no period says so instead of six greyed options
    const r2 = h('div', { class: 'row lb-period' });
    const periods = PERIODS.filter(p => p.value !== '7d' || S.metric === 'right' || S.period === '7d');
    if (NO_PERIOD[S.metric] && S.metric !== 'rating') r2.append(h('p', { class: 'meta', text: NO_PERIOD[S.metric] }));
    else UI.seg(r2, periods.map(p => ({ value: p.value, label: p.short, title: p.label })), { value: S.period, label: 'Period', onChange: v => { S.period = v; S.at = ''; go(); } });
    box.append(r2);
    // the ‹ › stepper to any closed week, month or year, with when this one resets beside its name
    const canStep = ['week', 'month', 'year'].includes(S.period) && !['rating', 'skill', 'climb'].includes(S.metric);
    const rs = h('span', { id: 'resets', class: 'resets' }), rsI = h('span', { id: 'resets-i' });
    const r3 = h('div', { class: 'row' });
    if (['week', 'month', 'year', 'season'].includes(S.period) && !['rating', 'skill', 'climb'].includes(S.metric)) {
      const prev = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'Previous period', disabled: !canStep || null }, UI.icon('caret_left', 18));
      const next = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'Next period', disabled: !canStep || !S.at || null }, UI.icon('caret_right', 18));
      prev.addEventListener('click', () => step(-1));
      next.addEventListener('click', () => step(1));
      if (S.period === 'season') UI.tooltip(prev, 'Past seasons are on Your rankings, under Seasons');
      r3.append(h('span', { class: 'stepper' }, prev, h('span', { text: periodName() }), rs, next), rsI);
    } else r3.append(rs, rsI);
    box.append(r3);
    // who is on the board and the domain (the subject is the switch under the title). Contest points have no
    // domain (the server never split them), so a domain ranks Questions right and Skill rating only
    const domOK = ['right', 'skill'].includes(S.metric);
    const domWhy = domOK ? null : S.metric === 'rating' ? 'Contest rating is one number; pick Skill rating to rank a domain' : 'A domain applies to Questions right and Skill rating';
    const sel = (host, label, value, opts, onChange, disabled) => {
      const s0 = h('select', { class: 'field', 'aria-label': label, disabled: disabled ? true : null }, opts.map(([v, l]) => h('option', { value: v, text: l, selected: v === value ? true : null })));
      s0.addEventListener('change', () => onChange(s0.value));
      if (disabled) UI.tooltip(s0, disabled);
      host.append(s0);
      return s0;
    };
    const filters = h('div', { class: 'lb-filters' });
    sel(filters, 'Scope', S.scope, SCOPES, v => { S.scope = v; go(); });
    sel(filters, 'Domain', S.domain, [['', 'All domains'], ...domainsOf().map(([d, s0]) => [d, s0])], v => { S.domain = v; go(); }, domWhy);
    box.append(filters);
    // the summary on the title row says the board in words
    const dshort = (domainsOf().find(x => x[0] === S.domain) || [])[1];
    const words = [m.label, NO_PERIOD[S.metric] && S.metric !== 'rating' ? null : periodName(), (SCOPES.find(x => x[0] === S.scope) || SCOPES[0])[1], dshort].filter(Boolean).join(' · ');
    const sum = $('#lb-sum');
    sum.replaceChildren(h('span', { text: words }));
    sum.setAttribute('aria-label', `Board: ${words}. Change`);
  }
  // below 1280px the side column is hidden: its two blocks move into a sheet and come back when it closes
  function openControls(focusFind) {
    const ctlEl = $('#ctl'), findEl = $('#find'), home = ctlEl.parentNode;
    if (home.closest('.sheet-body')) return;
    // focus lands on Find when asked (/), else on the metric in use: never a field ringed on open
    const sh = UI.sheet({ title: 'Board', size: 's', body: b => b.append(ctlEl, findEl), focus: focusFind ? $('#find-in') : ctlEl.querySelector('[aria-pressed="true"]') || undefined });
    if (sh && sh.closed) sh.closed.then(() => home.append(ctlEl, findEl));
  }
  $('#lb-sum').addEventListener('click', () => openControls(false));
  function setMetric(v) {
    S.metric = v; S.sort = 'value';
    if (!['right', 'skill'].includes(v)) S.domain = '';
    if (['rating', 'skill', 'climb'].includes(v)) S.at = '';
    if (S.period === '7d' && v !== 'right') S.period = 'week';
    go();
  }
  function step(dir) {
    const id = stepAt(dir);
    if (id === null) return;
    S.at = id; go();
  }

  /* ------------------------------------------------------------ data */
  const query = (o = {}) => {
    const q = new URLSearchParams({ metric: S.metric, period: ['rating', 'skill', 'climb'].includes(S.metric) && S.metric !== 'rating' ? 'all' : S.period, scope: o.scope || S.scope, subject: S.subject, limit: '50', offset: String(o.offset || 0) });
    if (S.domain && ['right', 'skill'].includes(S.metric)) q.set('domain', S.domain);
    if (S.at) q.set('at', S.at);
    if (S.metric === 'rating' && S.sort === 'change') q.set('sort', 'change');
    if (o.find) q.set('find', o.find);
    return `/leaderboard?${q}`;
  };
  async function fetchQ(path) {
    const d = await api(path);
    cache.set(path, { d, at: Date.now() });
    return d;
  }
  async function go() {
    S.nearEnd = false;
    sync();
    renderControls();
    const path = query();
    const hit = cache.get(path);
    // a board on screen stays until the next one arrives, then its rows glide to their new places; a first load shows skeletons
    if (hit) { S.data = hit.d; S.at0 = hit.at; draw(); }
    else if (S.board && S.board.el.isConnected) $('#table').setAttribute('aria-busy', 'true');
    else { $('#table').replaceChildren(); UI.skel($('#table'), 'table:8'); $('#podium').replaceChildren(); UI.skel($('#podium'), { h: 120, r: 12 }); }
    try { S.data = await fetchQ(path); S.at0 = Date.now(); draw(); prefetch(); }
    catch (e) {
      if (hit) return;
      S.board = null;
      $('#podium').replaceChildren();
      $('#table').removeAttribute('aria-busy');
      $('#table').replaceChildren();
      UI.cardError($('#table'), go, e.status === 400 ? (e.message || 'That board isn’t available.') : 'The server is not answering.');
    }
  }
  function prefetch() {
    const idle = window.requestIdleCallback || (fn => setTimeout(fn, 400));
    idle(() => {
      ['all', 'near', 'following', 'level', 'country'].filter(s => s !== S.scope).forEach(s => { const p = query({ scope: s }); if (!cache.has(p)) fetchQ(p).catch(() => {}); });
      if (S.data && S.data.next_offset) { const p = query({ offset: S.data.next_offset }); if (!cache.has(p)) fetchQ(p).catch(() => {}); }
    });
  }

  /* ------------------------------------------------------------ drawing */
  const fmtVal = (v, e) => {
    if (v === null || v === undefined) return null;
    if (S.metric === 'net' || S.metric === 'climb' || (S.metric === 'rating' && S.sort === 'change')) return `${v > 0 ? '+' : v < 0 ? '−' : ''}${num(Math.abs(Math.round(v)))}`;
    if (S.metric === 'rating' || S.metric === 'skill') return num(Math.round(v));
    return num(v);
  };
  function resetsLine(d) {
    const el = $('#resets'), ie = $('#resets-i');
    if (!el) return;
    ie.replaceChildren();
    const inStep = !!el.closest('.stepper');
    if (d.closed) { el.textContent = `${inStep ? ' · ' : ''}final standings${d.window && d.window.end ? `, closed ${C.dayLabel(String(d.window.end).slice(0, 10))}` : ''}`; return; }
    if (S.metric === 'climb') { el.textContent = 'Since you started'; return; }
    if (!d.resets_at || S.period === 'all') { el.textContent = ''; return; }
    const at = new Date(`${d.resets_at}T00:00:00Z`);
    const local = at.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
    if (S.period === 'season') { el.textContent = ` · ends ${C.dayLabel(shift(d.resets_at, -1), { weekday: false })}, ${C.left(at.toISOString())} left`; return; }
    el.textContent = `${inStep ? ' · ' : ''}resets in ${C.left(at.toISOString())}`;
    ie.append(C.info(`${{ week: 'Weekly', month: 'Monthly', year: 'Yearly', '7d': 'Rolling 7-day' }[S.period] || ''} boards reset ${S.period === 'week' ? 'Monday' : ''} 00:00 UTC (${local} your time).`.replace('  ', ' '), 'About resets'));
  }
  const shift = (day, n) => { const d = new Date(`${day}T12:00:00Z`); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
  function youText(you) {
    const d = S.data || {};
    if (you.extended) return `You · #${you.extended.rank} of ${num(you.extended.of)} with extended time`;
    if (!you.rank) return 'You’re not on this board yet: finish a ranked contest.';
    const unit = { points: 'pts', net: 'over par', right: 'right', rating: '', skill: '', test: '', climb: '' }[S.metric] || '';
    const gap = you.cheapest || (you.gap ? Math.ceil(you.gap) + 1 : null);
    const parts = [`You · #${you.rank}`, `${fmtVal(you.value)}${unit ? ` ${unit}` : ''}`];
    if (you.anon) parts.push('shown as Anonymous');
    if (gap && you.rank > 1) {
      parts.push(`${num(gap)} ${unit || 'points'} to pass #${you.rank - 1}`);
      if (!d.closed) { const st = C.step(gap, S.metric === 'points' ? 'points' : S.metric, true); if (st) parts.push(st); }
    }
    // the way up (it was its own line under the podium): to the top 10, to the podium
    if (S.scope !== 'near' && !d.closed) {
      const es = d.entries || [];
      const tenth = es.find(e => e.rank === 10) || es[9], third = es.find(e => e.rank === 3) || es[2];
      if (you.rank > 10 && tenth) parts.push(`${num(Math.ceil(tenth.value - you.value + 1))} to top 10`);
      if (you.rank > 4 && third) parts.push(`${num(Math.ceil(third.value - you.value + 1))} to the podium`);
    }
    return parts.join(' · ');
  }
  function levelSeps(entries) {
    if (S.metric !== 'rating' || S.sort !== 'value') return entries;
    const out = []; let last = null;
    entries.forEach(e => {
      const lv = C.levelOf(e.value);     // one ladder: the level of the rating in the row (spec/rating.md)
      if (lv !== last) { out.push({ sep: `Level ${lv}` }); last = lv; }
      out.push({ ...e, level: lv });
    });
    return out;
  }
  async function nearest() {
    for (const p of ['week', 'month', 'season', 'year', 'all'].filter(x => x !== S.period)) {
      try {
        const q = new URLSearchParams({ metric: S.metric, period: p, scope: S.scope, subject: S.subject, limit: '1' });
        const x = await api(`/leaderboard?${q}`);
        if (x.players) return { period: p, players: x.players, label: { week: 'This week', month: 'This month', season: 'This season', year: 'This year', all: 'All time' }[p] };
      } catch (_) { return null; }
    }
    return null;
  }
  async function parsForEmpty() {
    if (S.pars) return S.pars;
    try { const b = await api(`/contest/${dailyOf()}/board?limit=1`); S.pars = (b.pars || []).filter(p => [3, 5, 7, 9].includes(p.level)); } catch (_) { S.pars = []; }
    return S.pars;
  }
  async function draw() {
    const d = S.data || {};
    resetsLine(d);
    const m = mOf();
    const entries = d.entries || [];
    // podium (not for Near me); the way up is in the You strip
    const pod = $('#podium');
    // the pedestals rise 3, 2, 1 when the metric or the period changes; never on the first draw
    const podKey = [S.metric, S.period, S.at, S.sort].join('|');
    const rise = !!S.podKey && S.podKey !== podKey;
    S.podKey = podKey;
    pod.replaceChildren();
    const top = S.scope !== 'near' ? (d.podium && d.podium.length ? d.podium : entries).slice(0, 3) : [];
    // nobody placed yet: no podium (three par pedestals repeated the par rows the card lists under them)
    if (top.length) {
      // fewer than 3 players: the empty places show par rows (C6)
      const parList = top.length < 3 && S.metric === 'points' ? [...(await parsForEmpty())].sort((a, b) => b.points - a.points).map(p => ({ label: `L${p.level} par`, value: p.points })) : [];
      const podPars = [0, 1, 2].map(i => (i < top.length ? null : parList[i - top.length] || null));
      UI.podium(pod, top, { value: e => fmtVal(e.value), sub: e => [e.accuracy !== undefined ? `${Math.round(e.accuracy * 100)}%` : null, e.avg_secs ? `${mmss(e.avg_secs)} avg` : null].filter(Boolean).join(' · ') || null, pars: podPars, rise });
    }
    const you = d.you;
    // find a student (C9)
    const fbox = $('#find');
    if (!fbox.childElementCount) {
      const f = h('input', { class: 'field', type: 'search', id: 'find-in', placeholder: 'Find a student', 'aria-label': 'Find a student', autocomplete: 'off' });
      const msg = h('span', { class: 'meta', role: 'status' });
      f.addEventListener('keydown', async ev => {
        if (ev.key !== 'Enter' || !f.value.trim()) return;
        ev.preventDefault();
        msg.textContent = '';
        try {
          const r = await api(query({ find: f.value.trim() }));
          const hit = (r.entries || []).find(e => e.name && e.name.toLowerCase() === f.value.trim().toLowerCase() && e.name !== 'Anonymous');
          if (!hit) { msg.textContent = 'No public student has that name.'; return; }
          if (!S.board || !S.board.highlight(hit.pid)) {
            const page = await fetchQ(query({ offset: Math.floor((hit.rank - 1) / 50) * 50 }));
            S.data = page; await draw(); S.board.highlight(hit.pid);
          }
          msg.textContent = `#${hit.rank}`;
        } catch (e) { msg.textContent = 'Couldn’t search. Try again.'; }
      });
      fbox.append(f, msg);
    }
    // the table
    const host = $('#table');
    host.removeAttribute('aria-busy');
    const keep = entries.length && S.board && S.board.el.parentNode === host ? S.board.el : null;
    [...host.children].forEach(c => { if (c !== keep) c.remove(); });
    if (!entries.length) {
      S.board = null;
      const pars = await parsForEmpty();
      if (!d.nearest_nonempty && !S.at && ['points', 'net', 'right', 'test'].includes(S.metric)) d.nearest_nonempty = await nearest();
      const empty = h('div', { class: 'lb-empty' },
        h('p', { class: 'line', text: `No ranked contests yet ${{ week: 'this week', month: 'this month', year: 'this year', season: 'this season', '7d': 'in the last 7 days', all: '' }[S.period] || ''}.`.replace(' .', '.') }),
        d.nearest_nonempty ? h('p', {}, h('a', { class: 'link', href: `?metric=${S.metric}&period=${d.nearest_nonempty.period}&subject=${S.subject}`, text: `${d.nearest_nonempty.label || d.nearest_nonempty.period}: ${num(d.nearest_nonempty.players)} students` })) : null,
        pars.length && S.metric === 'points' ? h('ul', { class: 'mini-rows sub-block' }, [...pars].sort((a, b) => b.points - a.points).map(p => h('li', { class: 'par' }, h('span', { class: 'mt', text: `L${p.level} par · today’s Daily` }), h('span', { class: 'ma mono', text: num(p.points) })))) : null,
        h('p', { class: 'meta', text: 'Your spot appears after your first ranked contest.' }),
        h('div', { class: 'row-act' }, h('a', { class: 'pill', href: C.href(dailyOf()), text: 'Start the challenge' })));
      host.append(empty);
      return;
    }
    const cols = [{ label: S.metric === 'skill' && S.domain ? `Skill rating · ${(domainsOf().find(x => x[0] === S.domain) || [])[1] || S.domain}` : S.metric === 'rating' && S.sort === 'change' ? 'Change' : m.col, value: e => fmtVal(e.value), phone: true }];
    if (S.metric === 'rating' && S.sort === 'value') cols.push({ label: 'Change', value: e => (e.change !== undefined && e.change !== null ? `${e.change > 0 ? '+' : e.change < 0 ? '−' : ''}${num(Math.abs(Math.round(e.change)))}` : null) });
    cols.push({ label: 'Accuracy', value: e => (e.accuracy !== undefined && e.accuracy !== null ? `${Math.round(e.accuracy * 100)}%` : null) },
      { label: 'Avg time', value: e => (e.avg_secs ? mmss(e.avg_secs) : null) },
      { label: S.metric === 'test' ? 'Sections' : 'Contests', value: e => e.contests ?? e.sections ?? null, unit: S.metric === 'test' ? 'sections' : 'contests' });
    if (!d.closed) cols.push({ label: 'Move', value: e => C.moved(e.move, true), title: S.period === 'week' ? 'Places since yesterday' : 'Places since 7 days ago' });
    cols.push({ label: 'Gap', value: e => (!you || e.you || you.value === undefined || e.value === undefined ? null : `${e.value - you.value >= 0 ? '+' : '−'}${num(Math.abs(Math.round((e.value - you.value) * 10) / 10))}`), title: 'Their value minus yours', meta: false });
    const opts = {
      label: `${m.label} board`, columns: cols, value: e => e.value, youText,
      rowMenu: e => [{ label: 'Follow', onClick: () => api('/follows', { method: 'POST', body: { pid: e.pid } }).then(() => UI.toast(`Following ${e.name}`), err => UI.toast(err.status === 403 ? 'This student is private.' : 'Not saved.')) }],
      onFollow: e => api('/follows', { method: 'POST', body: { pid: e.pid } }).then(() => UI.toast(`Following ${e.name}`), () => UI.toast('Not saved.')),
      onMore: off => fetchQ(query({ offset: off })).then(x => ({ ...x, entries: levelSeps(x.entries || []) })),
      onJump: y => { if (y.rank) fetchQ(query({ offset: Math.floor((y.rank - 1) / 50) * 50 })).then(x => { S.data = x; draw().then(() => S.board.jump()); }); },
      empty: 'No one on this board yet.',
    };
    const data = { ...d, entries: levelSeps(entries) };
    // the same board takes the new rows (they glide), or a first one is drawn
    if (keep) S.board.update(data, opts); else S.board = UI.board(host, data, opts);
    if (S.scope === 'near' && you && you.rank && entries.length) {
      const first = entries[0].rank, last = entries[entries.length - 1].rank;
      const more = async (dir, b) => {
        b.disabled = true;
        try {
          const off = dir < 0 ? Math.max(0, first - 11) : last;
          const lim = dir < 0 ? Math.min(10, first - 1) : 10;
          const x = await fetchQ(query({ scope: 'all', offset: off }).replace(/limit=\d+/, `limit=${lim}`));
          const seen = new Set(entries.map(e => e.pid));
          const add = (x.entries || []).filter(e => !seen.has(e.pid));
          if (dir > 0 && x.next_offset === null) S.nearEnd = true;
          S.data = { ...S.data, entries: dir < 0 ? [...add, ...entries] : [...entries, ...add] };
          draw();
        } catch (_) { b.disabled = false; UI.toast('Couldn’t load more. Try again.'); }
      };
      const row = h('div', { class: 'row-act' });
      if (first > 1) row.append(h('button', { type: 'button', class: 'btn', text: 'Show 10 more above', onclick: ev => more(-1, ev.currentTarget) }));
      if (!S.nearEnd) row.append(h('button', { type: 'button', class: 'btn', text: 'Show 10 more below', onclick: ev => more(1, ev.currentTarget) }));
      host.append(row);
    }
    if (you && you.anon) host.append(h('p', { class: 'help' }, 'You’re shown as Anonymous to others. ', h('a', { class: 'link', href: '/me/settings/#account', text: 'Change in Settings' })));
    const ago = Math.round((Date.now() - S.at0) / 1000);
    if (ago > 5) host.append(h('p', { class: 'meta', text: `Updated ${ago} s ago` }));
  }

  /* ------------------------------------------------------------ keys (C24) */
  const cycle = (list, v, d = 1) => list[(list.findIndex(x => x.value === v) + d + list.length) % list.length].value;
  UI.keys.register('compete-leaderboard', {
    '/': { does: 'Find a student', run: () => { const f = $('#find-in'); if (!f) return; if (f.offsetParent) f.focus(); else openControls(true); } },
    'Shift+Y': { does: 'Jump to your row', run: () => S.board && S.board.jump() },
    M: { does: 'Next metric', run: () => setMetric(cycle(METRICS, S.metric)) },
    P: { does: 'Next period', run: () => { if (NO_PERIOD[S.metric] && S.metric !== 'rating') return; S.period = cycle(PERIODS.filter(p => p.value !== '7d' || S.metric === 'right'), S.period); S.at = ''; go(); } },
    ',': { does: 'Previous period', run: () => step(-1) },
    '.': { does: 'Next period', run: () => step(1) },
  }, { label: 'This page' });
  go();
})();
