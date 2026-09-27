/* ============================================================================
   Your rankings /compete/rankings/ (spec/rebuild-v2.md 3.7 §6; compete.md C1, C3, C5, C9,
   C10, C11, C12, C21, C22, C23, C27). Reads /api/compete/me, /api/compete/history,
   /api/compete/traps-index, /api/compete/rivals, /api/compete/champions and /api/leaderboard.
   The "How you placed" picker is gone: history rows expand in place (C22).
   ========================================================================== */
(() => {
  const h = UI.h, C = UI.compete, $ = s => document.querySelector(s);
  const num = C.num, mmss = C.mmss, pct = C.pct;
  const api = (p, o) => UI.api(p, o);
  const enc = encodeURIComponent;
  const S = { me: null, hist: [], total: 0, open: 0, kind: '', followup: false, sort: 'new', shown: 20, badgeF: 'all', champMine: false };
  const quiet = (text, onClick, o = {}) => { const b = h(o.href ? 'a' : 'button', { class: 'quiet', type: o.href ? null : 'button', href: o.href || null, text }); if (onClick) b.addEventListener('click', onClick); return b; };
  const head = (id, title, ...right) => h('div', { class: 'card-head' }, h('h2', { class: 'h2', id, text: title }), right.filter(Boolean).length ? h('div', { class: 'card-act' }, right.filter(Boolean)) : null);
  const stat = (label, value, sub) => h('div', { class: 'stat' }, h('span', { class: 'stat-k', text: label }), h('span', { class: 'stat-v', text: value ?? '—' }), sub ? h('span', { class: 'stat-sub', text: sub }) : null);
  const card = (sel, ...kids) => $(sel).replaceChildren(...kids.filter(Boolean));
  const fail = (sel, retry) => { $(sel).replaceChildren(); UI.cardError($(sel), retry, 'The server is not answering.'); };
  const drill = body => api('/drill', { method: 'POST', body }).then(r => { const to = C.runner(r); if (to) location.href = to; }).catch(e => UI.toast(e.message || 'Couldn’t start.'));
  const day = iso => C.dayLabel(String(iso).slice(0, 10), { weekday: false });
  const signed = v => (v === null || v === undefined ? '—' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${num(Math.abs(Math.round(v)))}`);
  const kindLabel = r => (r.kind === 'daily' ? `Daily · ${day(String(r.id).slice(6))}` : C.title(r));

  $('#subnav').replaceWith(C.subnav('rankings'));

  /* ------------------------------------------------------------ 1. the performance summary */
  function renderSummary() {
    const me = S.me, rows = S.hist;
    const right = rows.reduce((s, r) => s + ((r.result || {}).right || 0), 0), asked = rows.reduce((s, r) => s + ((r.result || {}).asked || 0), 0);
    const bests = (me.records && me.records.bests) || {};
    const b = me.boards || {};
    const kids = [head('summary-h', 'Performance summary')];
    if (me.week_line && me.week_line.text && (me.week_line.daily || me.week_line.weekly)) kids.push(h('p', { class: 'line', text: me.week_line.text }));
    kids.push(h('div', { class: 'stats sum-tiles' },
      stat('Contest rating', me.provisional ? 'Placing' : num(Math.round(me.rating)), me.provisional ? null : `Level ${me.level}`),
      stat('Contests played', S.total ? num(S.total) : null),
      stat('Average score', asked ? `${Math.round(right / asked * 100)}%` : null, rows.length ? `over ${num(rows.length)} contests` : null),
      stat('Contest accuracy', asked ? `${num(right)}/${num(asked)}` : null),
      stat('Best Daily', bests.daily ? num(bests.daily.value) : null, bests.daily && bests.daily.at ? day(bests.daily.at) : null),
      stat('Podiums', me.records && me.records.podiums && me.records.podiums.length ? num(me.records.podiums.length) : null, 'top 3 with 10 or more players'),
      stat('Points this week', b.week ? num(b.week.value) : null, b.week && b.week.rank ? `#${b.week.rank}` : null),
      stat('Season rank', b.season && b.season.rank ? `#${b.season.rank}` : null, b.season ? `${num(b.season.value)} pts` : null),
      stat('Challenge streak', me.streak ? num(me.streak.current) : null, me.streak && me.streak.best ? `best ${num(me.streak.best)}` : null),
      stat('Peak rating', bests.peak_rating ? num(Math.round(bests.peak_rating.value)) : null)));
    const roll = trapRollup();
    if (roll) kids.push(roll);
    if (!rows.length) {
      kids.push(h('p', { class: 'help', text: 'Finish a ranked contest to fill this in.' }), h('div', { class: 'row-act' }, h('a', { class: 'pill', href: C.href('daily'), text: 'Start today’s challenge' })));
      card('#summary', ...kids);
      return;
    }
    // the chart: Points or Over par per contest, a point per sitting; a point opens its row
    const chartHost = h('div', { class: 'sub-block' });
    let series = 'points', range = '30';
    const ctl = h('div', { class: 'board-ctl' });
    C.under(ctl, [{ value: 'points', label: 'Points' }, { value: 'net', label: 'Over par' }], { value: series, label: 'Series', onChange: v => { series = v; draw(); } });
    C.under(ctl, [{ value: '30', label: 'Last 30 contests' }, { value: '90', label: '90 days' }, { value: 'all', label: 'All' }], { value: range, label: 'Range', onChange: v => { range = v; draw(); } });
    function draw() {
      let pts = [...rows].reverse();
      if (range === '30') pts = pts.slice(-30);
      if (range === '90') pts = pts.filter(r => Date.now() - new Date(r.finished) < 90 * 864e5);
      const data = pts.filter(r => (series === 'net' ? r.net : r.points) !== null && (series === 'net' ? r.net : r.points) !== undefined)
        .map(r => ({ at: r.finished, y: series === 'net' ? r.net : r.points, star: r.record, tip: `${kindLabel(r)} · ${series === 'net' ? signed(r.net) + ' over par' : num(r.points) + ' pts'}`, id: r.session }));
      chartHost.replaceChildren();
      if (!UI.lineChart || data.length < 2) { chartHost.append(h('p', { class: 'meta', text: data.length ? 'The chart draws from your second contest.' : '' })); return; }
      UI.lineChart(chartHost, [{ key: series, label: series === 'net' ? 'Over par' : 'Points', points: data, you: true }],
        { height: 120, x: 'time', label: series === 'net' ? 'Over par per contest' : 'Points per contest', format: series === 'net' ? signed : num,
          onPick: p => { const i = S.hist.findIndex(r => r.session === p.id); if (i >= 0) openRow(i); } });
    }
    kids.push(ctl, chartHost);
    card('#summary', ...kids);
    draw();
  }

  // "This week: −210 pts to traps, 60% of it one trap: Swapped the columns" + Fix it (C1)
  function trapRollup() {
    const TP = { easy: 10, medium: 20, hard: 30 };
    const by = new Map();
    let total = 0;
    S.hist.filter(r => Date.now() - new Date(r.finished) < 7 * 864e5).forEach(r => ((r.result || {}).questions || []).forEach(q => {
      if (q.status !== 'incorrect' || !q.mistake) return;
      const pts = TP[q.difficulty] || 20;
      const x = by.get(q.mistake) || { label: q.mistake, pts: 0, at: [] };
      x.pts += pts; x.at.push([r.session, q.id]); by.set(q.mistake, x); total += pts;
    }));
    if (!total) return null;
    const top = [...by.values()].sort((a, b) => b.pts - a.pts)[0];
    const sid = top.at[0][0], only = top.at.filter(a => a[0] === sid).map(a => a[1]);
    const fix = quiet('Fix it', () => { const body = { from_session: sid, only, each: 3, source: 'twin', parent: sid }; return UI.twinSheet ? UI.twinSheet({ body, title: 'Fix it', recall: top.label }) : drill(body); });
    return h('div', { class: 'row-act' }, h('span', { class: 'line', text: `This week: −${num(total)} pts to traps${by.size > 1 ? `, ${Math.round(top.pts / total * 100)}% of it one trap` : ''}: ${top.label}` }), fix);
  }

  /* ------------------------------------------------------------ 2. the rating card (C11) and pace (C3) */
  function renderRating() {
    const me = S.me;
    const lin = me.provisional ? null : C.levelIn(me.rating, false);
    const kids = [head('rating-h', 'Rating'),
      h('p', { class: 'help', text: 'Contest rating moves only on ranked contest answers. Skill ratings move on every first try, in practice, tests and contests.' }),
      h('div', { class: 'rate-block sub-block' }, UI.level(me.rating, me.provisional, 48),
        h('div', {}, h('span', { class: 'k', text: 'CONTEST RATING' }), h('div', { class: 'num', text: me.provisional ? 'Placing' : num(Math.round(me.rating)) }),
          h('p', { class: 'line', text: me.provisional ? 'A level shows after 30 rated answers.' : `Level ${me.level}` })))];
    if (lin) kids.push(h('p', { class: 'line mono', text: `Level ${lin.level} in +${num(lin.gap)} ≈ ${lin.rights} hard right${lin.rights === 1 ? '' : 's'} at your level` }));
    const sk = me.skills;
    if (sk && (sk.domains || []).length) {
      const ul = h('ul', { class: 'mini-rows' }, sk.domains.map(d => h('li', {},
        h('span', { class: 'mt' }, UI.level(d.rating, d.placing, 32, { outline: true, level: d.level }), d.name || d.domain),
        h('span', { class: 'mm', text: [`Skill ${num(Math.round(d.rating))}`, d.level ? `Level ${d.level}` : null, `${num(d.n)} answers`, d.delta30 ? `${d.delta30 > 0 ? '▲' : '▼'}${Math.abs(Math.round(d.delta30))} in 30 days` : null].filter(Boolean).join(' · ') }))));
      kids.push(h('div', { class: 'sub-block' }, h('span', { class: 'k', text: 'SKILL RATINGS (ALL PRACTICE)' }), ul));
      const weak = [...sk.domains].filter(d => !d.placing).sort((a, b) => a.rating - b.rating)[0];
      if (weak) kids.push(h('div', { class: 'row-act' }, h('span', { class: 'line', text: `Weakest: ${weak.name || weak.domain}` }),
        h('button', { type: 'button', class: 'pill sm', text: `Practise ${weak.name || weak.domain} · 10`, onclick: () => drill({ topics: (UI.TOPICS || []).filter(t => t.domain === weak.domain).map(t => t.slug), zone: 'stretch', count: 10, source: 'skill' }) })));
    }
    card('#rating', ...kids);
  }
  function renderPace() {
    // ponytail: medians from this page's history rows; switch to /api/compete/me.pace (progress.pace(only='contest')) once the server sends it
    const qs = S.hist.flatMap(r => ((r.result || {}).questions || []).filter(q => q.ms));
    const kids = [head('pace-h', 'Pace')];
    if (S.me.pace) kids.push(h('p', { class: 'meta', text: 'From your contest answers in the last 90 days.' }));
    if (qs.length < 3) {
      kids.push(h('p', { class: 'help', text: 'Median time from question shown to answer, in ranked contests. It fills in after a few timed answers.' }));
      card('#pace', ...kids);
      return;
    }
    const med = a => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor(s.length / 2)] : null; };
    let view = 'difficulty';
    const box = h('div', { class: 'pace-rows' });
    const ctl = h('div', { class: 'board-ctl' });
    C.under(ctl, [{ value: 'difficulty', label: 'By difficulty' }, { value: 'domain', label: 'By domain' }, { value: 'rw', label: 'Right vs wrong' }], { value: view, label: 'Pace view', onChange: v => { view = v; draw(); } });
    function draw() {
      const groups = view === 'difficulty' ? ['easy', 'medium', 'hard'].map(t => [C.TIER[t], qs.filter(q => q.difficulty === t), { tiers: [t] }])
        : view === 'domain' ? (UI.DOMAINS || []).map(([d, s]) => [s, qs.filter(q => (UI.TOPIC[q.topic] || {}).domain === d), {}])
        : ['correct', 'incorrect'].map(st => [st === 'correct' ? 'Right answers' : 'Wrong answers', qs.filter(q => q.status === st)]);
      const max = Math.max(...qs.map(q => Math.max(q.ms, q.budget_ms || 0)));
      const rw = view === 'rw' && groups.every(([, g]) => g.length >= 3) ? med(groups[1][1].map(q => q.ms)) - med(groups[0][1].map(q => q.ms)) : null;
      box.replaceChildren(...groups.map(([label, g, extra]) => {
        if (g.length < 3) return h('div', { class: 'pace-row' }, h('span', { class: 'line', text: label }), h('span', { class: 'meta', text: '—' }));
        const m = med(g.map(q => q.ms)), bud = med(g.map(q => q.budget_ms || 0));
        const acc = g.filter(q => q.status === 'correct').length / g.length;
        return h('div', { class: 'pace-row' }, h('span', { class: 'line', text: label }),
          h('span', { class: 'tb', role: 'img', 'aria-label': `${label}: median ${mmss(m / 1000)} against a budget of ${mmss(bud / 1000)}` }, h('i', { style: `width:${Math.round(m / max * 100)}%` }), bud ? h('b', { style: `left:${Math.round(bud / max * 100)}%` }) : null),
          h('span', { class: 'pm', text: `you ${mmss(m / 1000)}${bud ? ` · budget ${mmss(bud / 1000)}` : ''} · accuracy ${pct(acc)} · ${g.length} answers` }),
          extra ? quadrant(m, bud, acc, g, extra) : '');
      }), rw !== null && Math.abs(rw) >= 5000 ? h('p', { class: 'line', text: `Wrong answers came ${mmss(Math.abs(rw) / 1000)} ${rw < 0 ? 'faster' : 'slower'} than right ones${rw < 0 ? ': the rushing signal' : ''}.` }) : '');
    }
    // U7's quadrants: slow and right → Speed drill; fast and wrong → Careful set; slow and wrong → Learn it untimed; fast and right → Keep warm
    function quadrant(m, bud, acc, g, extra) {
      const topics = [...new Set(g.map(q => q.topic).filter(Boolean))];
      const slow = bud && m > bud, right = acc >= 0.7;
      const [label, body] = slow && right ? ['Speed drill · 8', { timed: true, timing: 'pace', count: 8 }]
        : !slow && !right ? ['Careful set · 8', { count: 8 }]
        : slow ? ['Learn it untimed', { count: 8 }] : ['Keep warm · 5', { count: 5, pool: 'review' }];
      return h('span', { class: 'pa' }, quiet(label, () => drill({ topics, ...extra, ...body, source: 'result' })));
    }
    function trends() {
      const last = [...S.hist].reverse().slice(-10).map(r => (r.result || {}).questions || []).filter(q => q.some(x => x.ms));
      if (last.length < 2) return '';
      const sinks = last.map(q => q.filter(x => x.ms && x.budget_ms && x.ms > 2 * x.budget_ms).reduce((a, x) => a + x.ms, 0));
      const banked = last.map(q => q.filter(x => x.difficulty === 'easy' && x.ms && x.budget_ms).reduce((a, x) => a + Math.max(0, x.budget_ms - x.ms), 0));
      const strip = (label, vals) => { const max = Math.max(...vals, 1); return h('div', { class: 'row-act' }, h('span', { class: 'meta', text: label }),
        h('span', { class: 'trend-strip', role: 'img', 'aria-label': `${label}, last ${vals.length} contests` }, vals.map(v => h('i', { style: `height:${Math.max(2, Math.round(v / max * 28))}px` }))),
        h('span', { class: 'mono', text: mmss(vals[vals.length - 1] / 1000) })); };
      return h('div', { class: 'sub-block' }, strip('Time in sinks per contest', sinks), strip('Banked on easy', banked));
    }
    kids.push(ctl, box, h('p', { class: 'help', text: 'Bar: your median answer time. Tick: each question’s time budget.' }), trends());
    card('#pace', ...kids);
    draw();
  }

  /* ------------------------------------------------------------ 3. your ranks (C10) */
  async function renderRanks() {
    const b = S.me.boards || {};
    const periods = [['week', 'Week'], ['month', 'Month'], ['season', 'Season'], ['all', 'All time']];
    const cell = (you, players, period, scope) => {
      if (!you || !you.rank) return h('td', { text: '—' });
      const txt = `#${you.rank}${players ? ` of ${num(players)}` : ''}${players >= 10 ? ` · top ${Math.ceil(you.rank / players * 100)}%` : ''}${you.move ? ` · ${you.move > 0 ? '▲' : '▼'}${Math.abs(you.move)}` : ''}`;
      return h('td', {}, h('a', { class: 'link', href: `/compete/leaderboard/?metric=points&period=${period}&scope=${scope}`, text: you.anon && you.name === 'Anonymous' ? `#${you.rank} · as Anonymous` : txt }));
    };
    const tbody = h('tbody', {}, h('tr', {}, h('th', { scope: 'row', text: 'Everyone' }), periods.map(([p]) => cell(b[p], null, p, 'all'))));
    const table = h('table', { class: 'table compact' }, h('thead', {}, h('tr', {}, h('th', { scope: 'col', text: '' }), periods.map(([, l]) => h('th', { scope: 'col', text: l })))), tbody);
    card('#ranks', head('ranks-h', 'Your ranks'), h('div', { class: 'table-wrap' }, table),
      h('p', { class: 'meta', text: [S.me.climb ? `Climb ${signed(S.me.climb.gain ?? S.me.climb)}` : null, S.total ? `Contests played ${num(S.total)}` : null].filter(Boolean).join(' · ') }));
    // the other scopes, one row each, filled as they arrive
    for (const [scope, label] of [['following', 'Following'], ['level', 'My level'], ['country', 'Country'], ['exam', 'Same exam date']]) {
      const tr = h('tr', {}, h('th', { scope: 'row', text: label }), periods.map(() => h('td', { text: '…' })));
      tbody.append(tr);
      Promise.all(periods.map(([p]) => api(`/leaderboard?metric=points&period=${p}&scope=${scope}&limit=1`).catch(() => null))).then(rs => {
        if (rs.every(r => !r || !r.you || !r.you.rank)) { tr.remove(); return; }
        tr.replaceChildren(h('th', { scope: 'row', text: label }), ...rs.map((r, i) => cell(r && r.you, r && r.players, periods[i][0], scope)));
      });
    }
  }

  /* ------------------------------------------------------------ records (C21) */
  function renderRecords() {
    const r = (S.me.records || {}).bests || {};
    const NAME = { daily: 'Best Daily', sprint: 'Best Sprint', rush: 'Best Rush', weekly: 'Best Weekly', top_pct: 'Best top %', perfect_fast: 'Fastest perfect Daily', fastest_daily: 'Fastest perfect Daily', challenge_streak: 'Longest challenge streak', peak_rating: 'Peak rating' };
    // a record needs a sitting behind it: no 1,000 peak or 0-day streak before the first contest
    const tiles = Object.entries(r).filter(([k, v]) => v && v.value && (S.total || k === 'challenge_streak'))
      .map(([k, v]) => stat(NAME[k] || k.replace(/_/g, ' '), k === 'perfect_fast' || k === 'fastest_daily' ? mmss(v.value) : num(Math.round(v.value)), v.at ? day(v.at) : null));
    (S.me.records.podiums || []).slice(0, 4).forEach(p => tiles.push(stat(p.label || 'Podium', p.place ? `#${p.place}` : '—', p.period || null)));
    card('#records', head('records-h', 'Records'), tiles.length ? h('div', { class: 'stats sum-tiles' }, tiles) : h('p', { class: 'help', text: 'Your bests show here: points, top %, streaks, peak rating.' }));
  }

  /* ------------------------------------------------------------ the Trap Index (C12) */
  async function renderTraps() {
    try {
      const list = await api('/compete/traps-index');
      const rows = list.map(t => {
        const name = h('span', { text: t.name });
        if (t.tell) UI.tooltip(name, `Tell: ${t.tell}`);
        return h('tr', {}, h('td', {}, name, t.proven ? h('span', { class: 'chip-s on', style: 'margin-left:8px', text: 'Trap-proof' }) : null),
          h('td', { class: 'n', 'data-label': 'Field', text: t.field_share ? `${pct(t.field_share)}${t.field_move ? ` ${t.field_move > 0 ? '▲' : '▼'}${Math.abs(Math.round(t.field_move * 100))}` : ''}` : '—' }),
          h('td', { class: 'n', 'data-label': 'You', text: t.chances ? `${pct(t.you_share)} · ${num(t.chances)} chances` : '—' }),
          h('td', { class: 'n' }, quiet('Drill · 8', () => drill({ habit: t.family, count: 8, source: 'habit' }))));
      });
      card('#traps', head('traps-h', 'Trap Index'),
        h('div', { class: 'table-wrap' }, h('table', { class: 'table compact stack' },
          h('thead', {}, h('tr', {}, h('th', { scope: 'col', text: 'Trap' }), h('th', { scope: 'col', class: 'n', text: 'Field this week' }), h('th', { scope: 'col', class: 'n', text: 'You · chances (30 days)' }), h('th', { scope: 'col', text: '' }))),
          h('tbody', {}, rows))),
        h('p', { class: 'help', text: 'A chance is a first try on a question with that trap among its choices. Trap-proof: 5 chances over 3 question types in 30 days, none fallen for.' }));
    } catch (e) { fail('#traps', renderTraps); }
  }

  /* ------------------------------------------------------------ rivals (C9) */
  async function renderRivals() {
    try {
      const r = await api('/compete/rivals');
      const list = r.rivals || [];
      if (!list.length) { card('#rivals', head('rivals-h', 'Rivals'), h('p', { class: 'help', text: 'Rivals appear when 3 students near your level have played in the last two weeks. Follow a student from any board’s row menu.' })); return; }
      const rows = list.map(x => {
        const hh = x.h2h || {};
        const un = quiet('Unfollow', async ev => {
          try { await api(`/follows/${enc(x.pid)}`, { method: 'DELETE' }); ev.target.closest('tr').remove(); UI.toast(`Unfollowed ${x.name}`); } catch (e) { UI.toast('Not saved. Try again.'); }
        });
        return h('tr', {}, h('td', {}, h('span', { class: 'who-l', style: 'display:flex;gap:8px;align-items:center' }, UI.level(null, false, 20, { level: x.level, ring: x.ring }), x.name)),
          h('td', { class: 'n', 'data-label': 'This season', text: hh.you || hh.them ? `${hh.you}–${hh.them}${hh.ties ? `–${hh.ties}` : ''}` : '—' }),
          h('td', { class: 'n hx-opt', text: x.last_shared ? day(x.last_shared) : '—' }),
          h('td', { class: 'n' }, quiet('Race', null, { href: C.href('daily', { race: x.pid }) }), ' ', un));
      });
      card('#rivals', head('rivals-h', 'Rivals'), h('div', { class: 'table-wrap' }, h('table', { class: 'table compact stack' },
        h('thead', {}, h('tr', {}, h('th', { scope: 'col', text: 'Student' }), h('th', { scope: 'col', class: 'n', text: 'This season' }), h('th', { scope: 'col', class: 'n hx-opt', text: 'Last shared' }), h('th', { scope: 'col', text: '' }))),
        h('tbody', {}, rows))));
    } catch (e) { fail('#rivals', renderRivals); }
  }

  /* ------------------------------------------------------------ badges (C23) */
  const GO = { 'first-contest': 'daily', 'daily-7': 'daily', 'daily-30': 'daily', 'perfect-ten': 'daily', 'top-ten': 'daily', podium: 'daily', 'over-par': 'daily', 'won-back': 'daily', 'pace-setter': 'pace' };
  function goOf(b) {
    if (b.go && b.go.href) return b.go;
    const k = GO[b.id];
    if (k === 'daily') return { href: C.href('daily'), label: 'Start the challenge' };
    if (k === 'pace') return { href: C.href('daily', { race: 'pace' }), label: 'Race SAT pace' };
    if (b.id === 'trap-hunter') return { href: '/review/', label: 'Fix mistakes' };
    if (b.id === 'season-top-10') return { href: '/compete/leaderboard/?period=season', label: 'Season standings' };
    if (['streak-7', 'consistency', 'solved-1000'].includes(b.id)) return { href: '/', label: 'Up next' };
    return { href: '/compete/', label: 'Contests' };
  }
  function renderBadges() {
    const all = S.me.badges || [];
    const earned = all.filter(b => b.earned);
    const list = S.badgeF === 'earned' ? earned : S.badgeF === 'progress' ? all.filter(b => !b.earned) : all;
    const f = C.under(null, [{ value: 'all', label: 'All' }, { value: 'earned', label: 'Earned', n: earned.length }, { value: 'progress', label: 'In progress' }], { value: S.badgeF, label: 'Show', onChange: v => { S.badgeF = v; renderBadges(); } });
    const grid = h('div', { class: 'badge-grid' }, list.map(b => {
      const tile = h('div', { class: `bdg ${b.earned ? 'earned' : 'locked'}` }, h('span', { class: 'bn', text: b.name }), h('span', { class: 'br', text: b.rule }));
      if (b.earned) tile.append(h('span', { class: 'meta', text: `Earned ${day(b.earned)}` }));
      else {
        UI.meter(tile, { label: '', value: b.have, max: b.need, text: `${num(b.have)}/${num(b.need)}` });
        const g = goOf(b);
        tile.append(h('div', {}, quiet('Go', null, { href: g.href })));
        UI.tooltip(tile.lastChild.firstChild, g.label);
      }
      if (b.rarity) tile.append(h('span', { class: 'meta', text: `earned by ${pct(b.rarity)}` }));
      return tile;
    }));
    card('#badges', head('badges-h', 'Badges'), f.el, grid);
    $('#badges').id = 'badges';
  }

  /* ------------------------------------------------------------ seasons, champions, the level ladder */
  function renderSeasons() {
    const s = (S.me.boards || {}).season;
    card('#seasons', head('seasons-h', 'Seasons'), h('div', { class: 'table-wrap' }, h('table', { class: 'table compact' },
      h('thead', {}, h('tr', {}, ['Season', 'Points', 'Rank', 'Final'].map(t => h('th', { scope: 'col', text: t })))),
      h('tbody', {}, h('tr', {}, h('td', {}, 'This season ', h('span', { class: 'chip-s on', text: 'live' })), h('td', { class: 'n', text: s ? num(s.value) : '—' }), h('td', { class: 'n', text: s && s.rank ? `#${s.rank}` : '—' }), h('td', { text: '—' }))))),
      h('div', { class: 'foot-links' }, quiet('Season standings ›', null, { href: '/compete/leaderboard/?period=season' })));
  }
  async function renderChampions() {
    const box = h('div');
    const f = C.under(null, [{ value: false, label: 'All' }, { value: true, label: 'Mine' }], { value: S.champMine, label: 'Show', onChange: v => { S.champMine = v; renderChampions(); } });
    card('#champions', head('champions-h', 'Champions'), f.el, box);
    try {
      const list = await api(`/compete/champions${S.champMine ? '?mine=true' : ''}`);
      if (!list.length) { box.append(h('p', { class: 'help', text: S.champMine ? 'Weeks and seasons where you placed show here.' : 'Every closed week and season lists its podiums here, newest first.' })); return; }
      const names = arr => (arr || []).slice(0, 3).map(e => (e.you ? `${e.name} (you)` : e.name)).join(' · ') || '—';
      box.append(h('ul', { class: 'mini-rows' }, list.map(c => h('li', {}, h('span', { class: 'mt', text: `${c.kind === 'season' ? 'Season' : c.kind === 'final' ? 'Season Final' : 'Week'} ${c.period}` }),
        h('span', { class: 'mm', text: `Points: ${names((c.boards || {}).points)} · Over par: ${names((c.boards || {}).net)} · Most improved: ${names((c.boards || {}).change)}` })))));
    } catch (e) { box.replaceChildren(); UI.cardError(box, renderChampions); }
  }
  function renderLadder() {
    const mine = S.me.provisional ? null : S.me.level;
    const rows = Array.from({ length: 10 }, (_, i) => i + 1).map(n => h('tr', { class: n === mine ? 'you' : null },
      h('td', {}, h('span', { style: 'display:inline-flex;gap:8px;align-items:center' }, UI.level(null, false, 20, { level: n }), `Level ${n}`)),
      h('td', { class: 'n', text: C.rangeOf(n) }), h('td', { class: 'n', text: '—' }), h('td', { class: 'n', text: '—' })));
    card('#ladder', head('ladder-h', 'Level ladder'), h('div', { class: 'table-wrap' }, h('table', { class: 'table compact' },
      h('thead', {}, h('tr', {}, ['Level', 'Contest rating', 'Students at it', 'Timed-section median'].map((t, i) => h('th', { scope: 'col', class: i ? 'n' : null, text: t })))), h('tbody', {}, rows))),
      h('p', { class: 'help', text: 'The median is measured from students at each level with a timed full section in the last 30 days, shown once 20 have one.' }));
  }

  /* ------------------------------------------------------------ contest history (C22) */
  const KINDS = [['', 'All'], ['daily', 'Daily'], ['sprint', 'Sprint'], ['weekly', 'Weekly'], ['final', 'Final'], ['trap', 'Trap'], ['rush', 'Rush'], ['words', 'Words'], ['private', 'Private']];
  async function loadHistory() {
    const q = new URLSearchParams({ limit: '50' });
    if (S.kind) q.set('kind', S.kind);
    if (S.followup) q.set('followup', 'open');
    const r = await api(`/compete/history?${q}`);
    return r;
  }
  function followText(f) {
    if (!f) return '—';
    if (f.won_back !== null && f.won_back !== undefined && f.of) return `Won back ${num(f.won_back)}/${num(f.of)}`;
    if (f.due) return `Rematch ${C.dayLabel(f.due).split(',')[0]}`;
    if (f.open_traps) return `${f.open_traps} open`;
    return '—';
  }
  function renderHistory() {
    const el = $('#history');
    const ctl = h('div', { class: 'hist-ctl' });
    const kind = h('select', { class: 'field', 'aria-label': 'Kind' }, KINDS.map(([v, l]) => h('option', { value: v, text: l, selected: v === S.kind ? true : null })));
    kind.addEventListener('change', async () => { S.kind = kind.value; await reload(); });
    const sort = h('select', { class: 'field', 'aria-label': 'Sort' }, [['new', 'Newest'], ['points', 'Most points'], ['net', 'Best over par']].map(([v, l]) => h('option', { value: v, text: l, selected: v === S.sort ? true : null })));
    sort.addEventListener('change', () => { S.sort = sort.value; drawRows(); });
    ctl.append(kind, sort);
    C.under(ctl, [{ value: false, label: 'All' }, { value: true, label: 'Open follow-ups', n: S.open || null }], { value: S.followup, label: 'Follow-ups', onChange: async v => { S.followup = v; await reload(); } });
    // a placing strip per kind: the last 10 points
    const trend = h('div', { class: 'row-act' });
    const byKind = {};
    S.hist.forEach(r => { (byKind[r.kind] = byKind[r.kind] || []).push(r.points || 0); });
    Object.entries(byKind).forEach(([k, arr]) => {
      const last = arr.slice(0, 10).reverse(), max = Math.max(...last, 1);
      trend.append(h('span', { class: 'meta', text: C.kind({ kind: k }).label }), h('span', { class: 'trend-strip', role: 'img', 'aria-label': `${C.kind({ kind: k }).label}: last ${last.length} points ${last.join(', ')}` }, last.map(v => h('i', { style: `height:${Math.max(2, Math.round(v / max * 28))}px` }))));
    });
    const body = h('tbody');
    el.replaceChildren(...[head('history-h', 'Contest history'), ctl, S.hist.length > 1 ? trend : null].filter(Boolean), h('div', { class: 'table-wrap' }, h('table', { class: 'table compact hist' },
      h('thead', {}, h('tr', {}, ['Date', 'Contest', 'Score', 'R · W · S · V', 'Points', 'Over par', 'Time', 'Ranked', 'Follow-up', ''].map((t, i) =>
        h('th', { scope: 'col', class: [[2, 3, 4, 5, 6].includes(i) ? 'n' : '', [0, 2, 3, 4, 5, 6, 7].includes(i) ? 'hx-opt' : ''].join(' ').trim() || null, text: t })))), body)),
      h('div', { class: 'foot-links', id: 'hist-more' }));
    S.body = body;
    if (!S.hist.length) body.append(h('tr', {}, h('td', { colspan: 10, text: S.followup ? 'No open follow-ups.' : 'No contests yet.' })));
    drawRows();
  }
  function sortedHist() {
    const list = [...S.hist];
    if (S.sort === 'points') list.sort((a, b) => (b.points || 0) - (a.points || 0));
    if (S.sort === 'net') list.sort((a, b) => (b.net ?? -1e9) - (a.net ?? -1e9));
    return list;
  }
  function drawRows() {
    const body = S.body; if (!body || !S.hist.length) return;
    const list = sortedHist().slice(0, S.shown);
    body.replaceChildren(...list.flatMap(r => {
      const res = r.result || {};
      const wrong = res.wrong ?? Math.max(0, (res.asked || 0) - (res.right || 0) - (res.skipped || 0) - (res.voided || 0));
      const x = h('button', { type: 'button', class: 'xbtn', 'aria-expanded': 'false', 'aria-label': `Details for ${kindLabel(r)}`, text: '▸' });
      const tr = h('tr', { 'data-s': r.session },
        h('td', { class: 'hx-opt', text: day(r.finished) }),
        h('td', {}, h('a', { class: 'link', href: C.href(r.id), text: kindLabel(r) }), r.record ? h('span', { class: 'star', title: 'A record was set', html: ` ${C.svg(C.SVG.star, 14)}` }) : null,
          // phone: the row's second line (§6: "8/10 · 8·1·1·0 · 170 pts · +14")
          h('span', { class: 'hx-ph', text: [r.ranked ? 'Ranked' : 'Unranked', res.asked ? `${num(res.right)}/${num(res.asked)}` : null, res.asked ? `${num(res.right || 0)}·${num(wrong)}·${num(res.skipped || 0)}·${num(res.voided || 0)}` : null,
            r.points !== undefined && r.points !== null ? `${num(r.points)} pts` : null, r.net !== undefined && r.net !== null ? `${signed(r.net)} par` : null].filter(Boolean).join(' · ') })),
        h('td', { class: 'n hx-opt', text: res.asked ? `${num(res.right)}/${num(res.asked)}` : '—' }),
        h('td', { class: 'n hx-opt', text: res.asked ? `${num(res.right || 0)}·${num(wrong)}·${num(res.skipped || 0)}·${num(res.voided || 0)}` : '—' }),
        h('td', { class: 'n hx-opt', text: num(r.points) }),
        h('td', { class: 'n hx-opt', text: signed(r.net) }),
        h('td', { class: 'n hx-opt', text: res.secs !== undefined ? mmss(res.secs) : '—' }),
        h('td', { class: 'hx-opt', text: r.ranked ? 'Ranked' : `Unranked${r.why ? ` · ${r.why}` : ''}` }),
        h('td', { text: followText(r.followup) }),
        h('td', {}, x));
      x.addEventListener('click', () => toggle(tr, r, x));
      return [tr];
    }));
    const more = $('#hist-more');
    more.replaceChildren();
    if (S.hist.length > S.shown) more.append(quiet(`Show ${Math.min(20, S.hist.length - S.shown)} more`, () => { S.shown += 20; drawRows(); }));
  }
  async function toggle(tr, r, x) {
    const nxt = tr.nextElementSibling;
    if (nxt && nxt.classList.contains('open-row')) { nxt.remove(); x.setAttribute('aria-expanded', 'false'); return; }
    x.setAttribute('aria-expanded', 'true');
    const box = h('div', { class: 'exp' });
    const row = h('tr', { class: 'open-row' }, h('td', { colspan: 10 }, box));
    tr.after(row);
    UI.skel(box, 'lines:3');
    const res = r.result || {};
    const [board, deb] = await Promise.all([api(`/contest/${enc(r.id)}/board?limit=3`).catch(() => null), api(`/contest/${enc(r.id)}/debrief`).catch(() => null)]);
    const left = h('div', {}, h('span', { class: 'k', text: 'YOUR ANSWERS' }));
    UI.strip(left, C.marks(res), { onPick: i => { location.href = `${C.href(r.id)}#q${i + 1}`; }, label: 'Your answers' });
    const right = h('div', {}, h('span', { class: 'k', text: 'BOARD' }));
    if (board && (board.entries || []).length) {
      const you = board.you;
      const rows = [...board.entries.slice(0, 1)];
      if (you && !rows.some(e => e.you)) rows.push(you);
      right.append(h('ul', { class: 'mini-rows' }, rows.map(e => h('li', { class: e.you ? 'you' : null }, h('span', { class: 'mt', text: `${e.tie ? '=' : ''}#${e.rank} ${e.name}` }), h('span', { class: 'ma mono', text: num(e.points) })))));
      if (you && you.cheapest && you.rank > 1) right.append(h('p', { class: 'meta', text: `${num(you.cheapest)} pts to pass #${you.rank - 1}` }));
    } else right.append(h('p', { class: 'meta', text: '—' }));
    const acts = h('div', { class: 'row-act' });
    const top = deb && (deb.lost || []).sort((a, b) => (b.places || 0) - (a.places || 0) || b.pts - a.pts)[0];
    if (top) {
      left.append(h('p', { class: 'line', text: `Q${top.slot} · ${C.topicName(top.topic)} · ${top.label} · −${num(top.pts)}${top.rank_if ? ` · right → #${top.rank_if}` : ''}` }));
      acts.append(quiet('Fix it · 3', () => { const body = { from_session: r.session, only: [top.qid], each: 3, source: 'twin', parent: r.session }; if (top.norm) body.want = { template: top.norm }; return UI.twinSheet ? UI.twinSheet({ body, title: 'Fix it', recall: top.label }) : drill(body); }));
    }
    const f = r.followup || {};
    if (!f.session && !(f.won_back !== null && f.won_back !== undefined)) acts.append(quiet('Rematch', async () => {
      try { const x2 = await api(`/contest/${enc(r.id)}/rematch`, { method: 'POST', body: { when: 'now' } }); const to = C.runner(x2); if (to) location.href = to; } catch (e) { UI.toast(e.message || 'Nothing to rematch.'); }
    }));
    if (board && board.entries && board.entries[0] && !board.entries[0].you) acts.append(quiet('Race the winner', null, { href: C.href(r.id, { race: board.entries[0].pid }) }));
    acts.append(quiet('Race yourself', null, { href: C.href(r.id, { race: 'best' }) }), quiet('Review ›', null, { href: `${C.href(r.id)}#review` }));
    box.replaceChildren(h('div', { class: 'exp-grid' }, left, right), acts);
  }
  function openRow(i) {
    const r = S.hist[i];
    const tr = S.body && S.body.querySelector(`tr[data-s="${CSS.escape(r.session)}"]`);
    if (!tr) return;
    tr.scrollIntoView({ block: 'center', behavior: 'smooth' });
    const x = tr.querySelector('.xbtn');
    if (x.getAttribute('aria-expanded') !== 'true') x.click();
  }
  async function reload() {
    try { const r = await loadHistory(); S.hist = r.history || []; S.open = r.open_followups; S.shown = 20; renderHistory(); }
    catch (e) { fail('#history', reload); }
  }

  /* ------------------------------------------------------------ load */
  async function load() {
    ['#summary', '#rating', '#pace', '#ranks', '#records', '#traps', '#rivals', '#badges', '#seasons', '#champions', '#ladder', '#history']
      .forEach(s => UI.skel($(s), s === '#summary' ? 'cells:10' : 'card:3'));
    try {
      const [me, hist] = await Promise.all([api('/compete/me'), loadHistory()]);
      S.me = me; S.hist = hist.history || []; S.total = hist.total; S.open = hist.open_followups;
    } catch (e) { ['#summary', '#rating', '#pace', '#ranks', '#records', '#badges', '#seasons', '#ladder', '#history'].forEach(s => fail(s, load)); return; }
    renderSummary(); renderRating(); renderPace(); renderRanks(); renderRecords(); renderBadges(); renderSeasons(); renderLadder(); renderHistory();
    renderTraps(); renderRivals(); renderChampions();
    if (location.hash) setTimeout(() => { const t = document.querySelector(location.hash); if (t) t.scrollIntoView(); }, 200);
  }
  load();
})();
