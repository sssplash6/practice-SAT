/* ============================================================================
   Compete Overview /compete/ (spec/rebuild-v2.md 3.7 §3; compete.md C2, C5-C7, C9, C10,
   C12, C18, C21, C23-C25, C27; decision 7: only what the student needs, details on demand)
   Reads GET /api/compete (the hub), /api/compete/me, /api/contests, /api/compete/rivals,
   /api/qotd and /api/leaderboard; every card loads, fails and retries on its own.
   ========================================================================== */
(() => {
  const h = UI.h, C = UI.compete, $ = s => document.querySelector(s);
  const num = C.num, mmss = C.mmss;
  const pct = x => (x === null || x === undefined ? '—' : `${Math.round(x * 100)}%`);
  const api = (p, o) => UI.api(p, o);
  const S = { hub: null, me: null, live: null, board: null };
  const WHY = { ghost: 'Sat after the contest closed: it shows where you would have placed.', repeat: 'A second sitting of this contest.', fast: 'Answers came in faster than the questions can be read.' };

  const card = (id, ...kids) => { const el = $(id); el.replaceChildren(...kids.filter(Boolean)); return el; };
  const head = (title, ...right) => h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: title }), right.some(Boolean) ? h('div', { class: 'card-act' }, right) : null);
  const kline = (text, right) => h('div', { class: 'card-head' }, h('span', { class: 'k', text }), right || null);
  const quiet = (text, onClick, o = {}) => { const b = h(o.href ? 'a' : 'button', { class: 'quiet', type: o.href ? null : 'button', href: o.href || null, text }); if (onClick) b.addEventListener('click', onClick); return b; };
  const fail = (sel, retry, text) => { const el = $(sel); el.replaceChildren(); UI.cardError(el, retry, text || 'The server is not answering.'); };
  const skel = (sel, shape) => { const el = $(sel); if (!el.childElementCount) UI.skel(el, shape); };
  const busy = async (b, fn) => { b.disabled = true; try { await fn(); } catch (e) { UI.toast(e.message || 'Couldn’t start. Try again.'); } finally { b.disabled = false; } };
  const drill = async body => { const r = await api('/drill', { method: 'POST', body }); if (r && r.session) location.href = `/practice/session/?id=${encodeURIComponent(r.session)}`; };
  const idOf = kind => ((S.live || []).find(c => c.kind === kind) || {}).id;

  /* ------------------------------------------------------------ header */
  $('#subnav').replaceWith(C.subnav('overview'));
  $('#join').addEventListener('click', () => C.join());
  $('#create').addEventListener('click', () => C.create());
  $('#join-create').addEventListener('click', () => {
    const s = UI.sheet({ title: 'Join or create', size: 's', body: b => b.append(
      h('div', { class: 'row-act' }, quiet('Join with a code', () => { s.close(); C.join(); }), quiet('+ Create a contest', () => { s.close(); C.create(); }))) });
  });

  /* ------------------------------------------------------------ A. the Daily Challenge */
  const ladder = C.ladder, parLine = C.parLine, fieldLine = C.fieldLine;
  function followChip(fu) {
    if (!fu) return null;
    if (fu.won_back !== null && fu.won_back !== undefined && fu.of) return h('span', { class: 'chip-s', text: `Won back ${num(fu.won_back)}/${num(fu.of)}` });
    if (fu.due) return h('a', { class: 'chip-s on', href: fu.session ? `/practice/session/?id=${encodeURIComponent(fu.session)}` : C.href(S.hub.daily.id), text: `Rematch · ${C.dayLabel(fu.due, { weekday: true }).split(',')[0]}` });
    return null;
  }
  let stopNext = null;
  async function renderDaily() {
    const c = S.hub.daily, me = c.me || {};
    const el = $('#daily');
    const day = String(c.id).slice(6);
    const next = h('span', { class: 'meta' });
    const midnight = new Date(); midnight.setHours(24, 0, 0, 0);
    const streak = S.hub.me && S.hub.me.challenge_streak;
    const best = S.me && S.me.streak && S.me.streak.best;
    const chip = streak ? h('span', { class: 'chip-s', text: `${num(streak)}-day streak` }) : null;
    if (chip) UI.tooltip(chip, `Daily Challenges in a row${best > streak ? ` · best ${num(best)}` : ''}`);
    const top = h('div', { class: 'daily-top' }, h('span', { class: 'k', text: `DAILY CHALLENGE · ${C.dayLabel(day).toUpperCase()}` }),
      h('span', { class: 'daily-top-r' }, chip, h('span', { class: 'meta' }, 'Next one in ', next)));
    next.setAttribute('aria-live', 'off');
    if (stopNext) stopNext();
    const cd = UI.countdown(next, midnight.toISOString(), { label: 'Next Daily', onEnd: () => load() });
    stopNext = typeof cd === 'function' ? cd : cd && cd.stop;
    const body = [top];
    const done = me.status === 'finished';
    // before a sitting: the questions and the rules; after it, the result leads and the rules belong to the lobby
    if (!done) {
      const lad = h('div'); ladder(lad, c); body.push(lad);
      body.push(h('div', { class: 'daily-lines' },
        h('p', { class: 'line' }, `${c.count} questions · ${mmss(c.seconds)} answer clock · one sitting · ranked `, C.info('The clock runs only while a question is open. Skipped and voided questions score 0.', 'About the clock')),
        parLine(c), fieldLine(c)));
    }
    // More: the day's quieter jobs in one menu
    const yday = new Date(); yday.setDate(yday.getDate() - 1);
    const yid = `daily-${yday.getFullYear()}-${String(yday.getMonth() + 1).padStart(2, '0')}-${String(yday.getDate()).padStart(2, '0')}`;
    const moreBtn = extra => {
      const b = h('button', { type: 'button', class: 'quiet', 'aria-haspopup': 'menu', text: 'More ▾' });
      UI.menu.bind(b, () => [...extra, { label: 'Past days', href: C.href(yid) }, { label: 'Daily reminder', onClick: () => C.reminder() }], { label: 'More' });
      return b;
    };
    const st = h('div', { class: 'daily-status' });
    if (me.status === 'new') {
      const go = h('button', { type: 'button', class: 'pill', text: 'Start the challenge' });
      go.addEventListener('click', () => {
        if (C.rulesSeen('daily')) busy(go, () => C.start(c.id, { kind: 'daily' }));
        else location.href = C.href(c.id);
      });
      const warm = quiet('Warm up · 6', ev => busy(ev.currentTarget, async () => {
        const r = await api(`/contest/${encodeURIComponent(c.id)}/warmup`, { method: 'POST', body: {} });
        location.href = `/practice/session/?id=${encodeURIComponent(r.session)}`;
      }));
      UI.tooltip(warm, 'Two questions on each of your three lowest-chance skills, from other question types. Offered only before you start.');
      st.append(h('div', { class: 'row-act' }, go, warm, moreBtn([])));
    } else if (me.status === 'progress') {
      const go = h('button', { type: 'button', class: 'pill', text: 'Resume' });
      go.addEventListener('click', () => busy(go, () => C.start(c.id)));
      st.append(h('div', { class: 'row-act' }, go, h('span', { class: 'meta', text: `${num(me.answered)} of ${num(c.count)} answered${me.clock ? ` · ${mmss(me.clock.left)} on the clock` : ''}` }), moreBtn([])));
    } else {
      const r = me.result || {};
      const place = S.board && S.board.you;
      const players = (S.board && S.board.players) || (c.field && c.field.players);
      // the result is the headline: the contest page's big rank, scaled down, the score beneath
      const big = h('div', { class: 'big-rank daily-rank' });
      if (place && place.rank && me.ranked !== false) {
        big.append(h('span', { class: 'num', text: `${place.tie ? '=' : ''}#${place.rank}` }), h('span', { class: 'of', text: `of ${num(players)}` }));
        if (players >= 10) big.append(h('span', { class: 'chip-s', text: `Top ${Math.ceil(place.rank / players * 100)}%` }));
      }
      st.append(...[big.childElementCount ? big : null,
        h('p', { class: 'daily-res', text: [`${num(r.right)}/${num(r.asked || c.count)}`, `${num(r.points)} pts`, me.clock ? mmss(me.clock.used) : null].filter(Boolean).join(' · ') })].filter(Boolean));
      if (me.ranked === false) st.append(h('p', { class: 'line' }, h('span', { class: 'chip-s', text: 'Unranked' }), ' ', WHY[me.why] || ''));
      UI.strip(st, C.marks(r), { onPick: i => { location.href = `${C.href(c.id)}#q${i + 1}`; }, label: 'Your answers' });
      const chips = h('div', { class: 'row-act' });
      if (r.rating_after !== undefined && r.rating_before !== undefined) {
        const d = Math.round(r.rating_after - r.rating_before);
        chips.append(h('span', { class: 'chip-s', text: `${d >= 0 ? '+' : '−'}${Math.abs(d)} → ${num(Math.round(r.rating_after))} · Level ${C.levelOf(r.rating_after)}` }));
      }
      const fu = followChip(me.followup);
      if (fu) chips.append(fu);
      if (chips.childElementCount) st.append(chips);
      const copy = { label: 'Copy result', onClick: () => UI.copyText(C.copyResult(c, { ...r, secs: me.clock ? me.clock.used : undefined }, { rank: place && place.rank, players })) };
      st.append(h('div', { class: 'row-act' }, h('a', { class: 'pill', href: `${C.href(c.id)}#board`, text: 'See the board' }),
        quiet('Review answers', null, { href: `${C.href(c.id)}#review` }), moreBtn([copy])));
    }
    body.push(st);
    // a make-up shows only when yesterday was missed and there is a streak for it to keep
    const strip = S.me && S.me.streak && S.me.streak.strip;
    const ystate = strip && (strip.find(x => x.day === yid.slice(6)) || {}).state;
    const keep = ystate === 'missed' ? C.streakBefore(strip, yid.slice(6)) : 0;
    if (keep >= 1) body.push(h('div', { class: 'row-act' }, h('a', { class: 'chip-s on', href: C.href(yid), text: `Keep your ${num(keep)}-day streak: make up ${C.dayLabel(yid.slice(6), { weekday: false })}` })));
    if (done) body.push(h('div', { class: 'daily-foot' }, fieldLine(c)));
    el.replaceChildren(...body);
  }

  /* ------------------------------------------------------------ B. contests */
  const TRAINS = { daily: 'the ten skills of the day', sprint: 'fluency in the week’s domain', weekly: 'module pace and routing', final: 'a full adaptive section',
    trap: 'this week’s trap', rush: 'your ceiling, one question at a time', words: 'Words in Context and Transitions', private: 'the skills your friends picked' };
  let tab = 'live', shown = 10;
  const counts = { live: null, upcoming: null, finished: null, private: null };
  function crow(c) {
    const me = c.me || {}, k = C.kind(c);
    const title = c.series && c.round ? `${c.title} · round ${c.round}${c.spec && c.spec.repeat ? ` of ${c.spec.repeat.rounds}` : ''}` : C.title(c);
    let chip = null;
    if (me.status === 'progress') chip = `In progress${me.clock && me.clock.left !== undefined ? ` · ${mmss(me.clock.left)} left` : ''}`;
    else if (me.status === 'finished') chip = me.result && me.result.points !== undefined ? `Finished · ${num(me.result.points)} pts` : 'Finished';
    let act;
    if (c.status === 'upcoming') act = quiet('Add to calendar', () => UI.ics({ title: `SAT Freshman · ${title}`, start: new Date(c.opens), minutes: 30, url: `${location.origin}${C.href(c.id)}` }));
    else if (me.status === 'progress') act = quiet('Resume', ev => busy(ev.currentTarget, () => C.start(c.id)));
    else if (me.status === 'finished') act = quiet('Results', null, { href: C.href(c.id) });
    else if (c.status === 'live') act = quiet('Start', null, { href: C.href(c.id) });
    else act = quiet('Open', null, { href: C.href(c.id) });
    const par = me.status === 'new' && me.par && me.par.base && ['daily', 'weekly', 'final', 'trap'].includes(c.kind) ? ` · par ${num(me.par.base)}` : '';
    return h('div', { class: 'crow' }, C.icon(c.kind),
      h('div', {}, h('a', { class: 't link', href: C.href(c.id), text: title }),
        h('span', { class: 'w', text: C.windowLine(c) }),
        h('span', { class: 'f', text: C.facts(c) + par }),
        TRAINS[c.kind] ? h('span', { class: 'f tr', text: `Trains ${TRAINS[c.kind]}` }) : null),
      chip ? h('span', { class: 'st chip-s', text: chip }) : h('span'),
      h('span', { class: 'act' }, act));
  }
  let filter = null;
  async function renderContests() {
    const el = $('#contests');
    if (!filter) {
      const hd = h('div', { class: 'card-head' }, h('h2', { class: 'h2', id: 'contests-h', text: 'Contests' }));
      const box = h('div', { id: 'crows' });
      el.replaceChildren(hd, box);
      filter = C.under(hd, [{ value: 'live', label: 'Live' }, { value: 'upcoming', label: 'Upcoming' }, { value: 'finished', label: 'Finished' }, { value: 'private', label: 'Private' }],
        { value: tab, label: 'Show', onChange: v => { tab = v; shown = 10; loadRows(); } });
      filter.el.style.marginLeft = 'auto';
    }
    Object.entries(counts).forEach(([k, n]) => filter.count(k, n));
    loadRows();
  }
  async function loadRows() {
    const box = $('#crows');
    box.replaceChildren(); UI.skel(box, 'rows:3');
    try {
      const r = await api(`/contests?status=${tab}&limit=${shown}`);
      // the Daily card owns today's Daily: the Live list leaves every daily out, and its count with it
      if (tab === 'live') { const n0 = r.contests.length; r.contests = r.contests.filter(c => c.kind !== 'daily'); r.total = Math.max(0, (r.total || 0) - (n0 - r.contests.length)); }
      counts[tab] = r.total; filter.count(tab, r.total);
      if (tab === 'live') S.live = r.contests;
      const rows = r.contests.map(crow);
      if (!rows.length) {
        box.replaceChildren(tab === 'private'
          ? h('div', { class: 'crows-empty' }, h('p', { text: 'No private contests yet.' }), h('div', { class: 'row-act' }, quiet('+ Create a contest', () => C.create()), quiet('Join with a code', () => C.join())))
          : h('p', { class: 'crows-empty', text: tab === 'finished' ? 'No finished contests yet.' : 'Nothing here right now.' }));
        return;
      }
      box.replaceChildren(...rows);
      if (r.total > shown) box.append(h('div', { class: 'row-act' }, quiet(`Show ${Math.min(10, r.total - shown)} more`, () => { shown += 10; loadRows(); })));
      if (tab === 'live') renderSeason();
    } catch (e) { box.replaceChildren(); UI.cardError(box, loadRows, 'The server is not answering.'); }
  }
  async function loadCounts() {
    for (const k of ['finished', 'private']) {
      try { const r = await api(`/contests?status=${k}&limit=0`); counts[k] = r.total; if (filter) filter.count(k, r.total || null); } catch (_) {}
    }
  }

  /* ------------------------------------------------------------ C. question of the day */
  async function renderQotd() {
    const el = $('#qotd');
    try {
      const q = await api('/qotd');
      const m = q.mine, qq = q.question || {};
      // one header row with one way in; before an answer only its skill and difficulty (the user: no need to display the question)
      const go = quiet(m ? 'See it ›' : 'Answer ›', null, { href: `${C.href('daily')}#qotd` });
      const kids = [h('div', { class: 'card-head' }, h('span', { class: 'k', text: 'QUESTION OF THE DAY' }), h('div', { class: 'card-act' }, go))];
      if (!m) {
        kids.push(h('p', { class: 'meta', text: [qq.topic_name || (qq.topic && C.topicName(qq.topic)), C.TIER[qq.difficulty]].filter(Boolean).join(' · ') }));
      } else if (m.correct) kids.push(h('p', { class: 'line', text: ['Right', m.share !== undefined ? `${pct(m.share)} of ${num(m.n)} got it` : null, m.streak ? `${m.streak}-day streak` : null].filter(Boolean).join(' · ') }));
      else kids.push(h('p', { class: 'line', text: m.mistake || m.reason ? `Fell for: ${m.mistake || m.reason}` : 'Wrong' }));
      el.replaceChildren(...kids);
    } catch (e) { fail('#qotd', renderQotd); }
  }

  /* ------------------------------------------------------------ D. your stats */
  function renderStats() {
    const hub = S.hub, me = hub.me || {}, mine = S.me || {};
    const boards = mine.boards || {};
    const players = hub.board_preview && hub.board_preview.players;
    const rating = me.rating;
    const lin = !me.provisional ? C.levelIn(rating, false) : null;
    const kids = [head('Your stats', quiet('Your rankings ›', null, { href: '/compete/rankings/' }))];
    // one ladder: the level is read from the rating on the spec/rating.md ladder, the ring and the words alike
    if (!me.provisional) kids.push(h('div', { class: 'me-rate' }, UI.level(rating, false, 48),
      h('div', {}, h('span', { class: 'num', text: num(Math.round(rating)) }), h('p', { class: 'line', text: `Contest rating · Level ${C.levelOf(rating)}` }))));
    else {
      // placing: one line with its progress; answers counted from ranked contests until the server sends its count
      const n = Math.min(29, me.rated ?? S.rated ?? 0);
      const m = h('div', { class: 'placing' });
      UI.meter(m, { label: 'Placing', value: n, max: 30, text: `${num(n)} of 30 answers` });
      kids.push(m);
      if (me.rated === undefined && S.rated === undefined) api('/compete/history?limit=50').then(x => { S.rated = (x.history || []).filter(r => r.ranked).reduce((a, r) => a + ((r.result || {}).asked || 0), 0); if (S.rated) renderStats(); }).catch(() => { S.rated = 0; });
    }
    // decision 7: a tile shows only with a value that no other tile or card here already says
    const tile = (label, value, sub) => (value == null ? null : h('div', { class: 'stat' }, h('span', { class: 'stat-k', text: label }), h('span', { class: 'stat-v', text: value }), sub ? h('span', { class: 'stat-sub', text: sub }) : null));
    const ranked = me.week || me.all;
    const pass = b => b && b.cheapest ? `${num(b.cheapest)} pts to #${b.rank - 1}` : null;
    const move = b => b && b.move ? `${b.move > 0 ? '▲' : '▼'}${Math.abs(b.move)}` : null;
    const wk = boards.week;
    const bestD = mine.records && mine.records.bests && mine.records.bests.daily;
    const today = hub.daily && hub.daily.me;
    const bestIsToday = bestD && today && today.status === 'finished' && (bestD.session ? bestD.session === today.session : today.result && today.result.points === bestD.value);
    const tiles = ranked && h('div', { class: 'stat-grid' },
      tile('Week rank', me.week ? `#${me.week}${players ? ` of ${num(players)}` : ''}` : null, [move(wk), pass(wk)].filter(Boolean).join(' · ')),
      me.all && me.all !== me.week ? tile('All-time rank', `#${me.all}`, pass(boards.all)) : null,
      me.country ? tile('Country', `#${me.country}`) : null,
      tile('This week', wk ? num(wk.value) : null, wk ? 'points' : null),
      tile('Contests', me.played ? num(me.played) : null),
      bestIsToday ? null : tile('Best Daily', bestD ? num(bestD.value) : null));
    if (lin) kids.push(h('p', { class: 'meta', text: `Level ${lin.level} in +${num(lin.gap)} ≈ ${lin.rights} hard right${lin.rights === 1 ? '' : 's'}` }));
    if (tiles) kids.push(tiles);   // before a first rank the Daily card beside it holds the one way in
    if (new Date().getDay() === 1 && hub.week_line && hub.week_line.text && (hub.week_line.daily || hub.week_line.weekly)) kids.push(h('p', { class: 'meta', text: hub.week_line.text }));
    card('#stats', ...kids);
  }

  /* ------------------------------------------------------------ Rivals (C9) */
  async function renderRivals() {
    try {
      const r = await api('/compete/rivals');
      const list = (r.rivals || []).slice(0, 3);
      const kids = [head('Rivals')];
      if (!list.length) {
        kids.push(h('p', { class: 'help', text: 'Rivals appear when 3 students near your level have played in the last two weeks. Until then, race your best run.' }),
          h('div', { class: 'row-act' }, quiet('Race your best', null, { href: C.href('daily', { race: 'best' }) })));
      } else {
        const ul = h('ul', { class: 'mini-rows' });
        list.forEach(x => {
          const r2 = x.h2h || {};
          const rec = r2.you > r2.them ? `You lead ${r2.you}–${r2.them}` : r2.you < r2.them ? `${x.name} leads ${r2.them}–${r2.you}` : r2.you ? `Level ${r2.you}–${r2.them}` : null;
          ul.append(h('li', {}, h('span', { class: 'mt' }, UI.level(null, false, 20, { level: x.level, ring: x.ring }), x.name),
            h('span', { class: 'mm', text: [rec ? `${rec} this season` : null, x.last_shared ? `last shared ${C.dayLabel(String(x.last_shared).slice(0, 10), { weekday: false })}` : null].filter(Boolean).join(' · ') || 'No shared contest yet' }),
            h('span', { class: 'ma' }, quiet('Race', null, { href: C.href('daily', { race: x.pid }) }))));
        });
        kids.push(ul);
      }
      card('#rivals', ...kids);
    } catch (e) { fail('#rivals', renderRivals); }
  }

  /* ------------------------------------------------------------ H. season */
  function renderSeason() {
    const hub = S.hub; if (!hub) return;
    const s = hub.season || {};
    const days = s.closes ? Math.max(0, Math.ceil((new Date(`${s.closes}T23:59:59`) - Date.now()) / 864e5)) : null;
    const mine = (S.me && S.me.boards && S.me.boards.season) || null;
    const fin = (S.live || []).find(c => c.kind === 'final');
    const kids = [kline(`SEASON · ${String(s.name || '').toUpperCase()}`, h('span', {}, days !== null ? h('span', { class: 'meta', text: `${days} day${days === 1 ? '' : 's'} left ` }) : null, C.info('Every ranked contest adds to your season points.', 'About season points')))];
    if (s.opens && s.closes) {
      const a = new Date(s.opens), b = new Date(`${s.closes}T23:59:59`);
      kids.push(h('div', { class: 'season-bar', role: 'img', 'aria-label': 'Season elapsed' }, h('i', { style: `width:${Math.min(100, Math.max(0, (Date.now() - a) / (b - a) * 100))}%` })));
    }
    const wk = S.me && S.me.boards && S.me.boards.week;
    if (mine && mine.rank && !(wk && wk.rank === mine.rank && wk.value === mine.value)) kids.push(h('p', { class: 'line mono', text: `#${mine.rank} · ${num(mine.value)} pts` }));
    if (fin) {
      const end = new Date(new Date(fin.closes).getTime() - 864e5);
      kids.push(h('p', { class: 'line' }, `Season Final · ${new Date(fin.opens).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })} – ${end.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })} · full Math section `,
        quiet('Add to calendar', () => UI.ics({ title: 'SAT Freshman · Season Final', start: fin.opens.slice(0, 10), url: `${location.origin}${C.href(fin.id)}` }))));
    }
    kids.push(h('div', { class: 'foot-links' }, quiet('Season standings ›', null, { href: '/compete/leaderboard/?period=season' })));
    card('#season', ...kids);
  }

  /* ------------------------------------------------------------ E. this week's board (C10, C6) */
  let metric = 'points';
  async function renderPreview() {
    const el = $('#preview');
    const hd = kline('THIS WEEK');
    C.under(hd, [{ value: 'points', label: 'Points' }, { value: 'net', label: 'Over par' }, { value: 'climb', label: 'Climb' }], { value: metric, label: 'Board', onChange: v => { metric = v; renderPreview(); } });
    const box = h('div');
    el.replaceChildren(hd, box);
    UI.skel(box, 'rows:5');
    try {
      const q = `metric=${metric}&period=week&limit=5`;
      const top = metric === 'points' && S.hub.board_preview ? S.hub.board_preview : await api(`/leaderboard?${q}`);
      let rows = [...(top.entries || [])];
      const you = top.you;
      if (you && you.rank > 5) {
        if (you.rank > 7) rows.push({ sep: true });
        const near = await api(`/leaderboard?metric=${metric}&period=week&offset=${Math.max(5, you.rank - 3)}&limit=5`);
        (near.entries || []).forEach(e => { if (!rows.some(x => x.pid === e.pid)) rows.push(e); });
      }
      const ul = h('ul', { class: 'mini-rows' });
      const fmt = v => metric === 'net' ? `${v > 0 ? '+' : ''}${num(v)}` : num(v);
      rows.forEach(e => {
        if (e.sep) { ul.append(h('li', { class: 'sep', 'aria-hidden': 'true' })); return; }
        const gap = you && !e.you && you.value !== undefined ? e.value - you.value : null;
        ul.append(h('li', { class: e.you ? 'you' : null },
          h('span', { class: 'mt' }, h('span', { class: 'mono', text: `${e.tie ? '=' : ''}${e.rank}` }), UI.level(null, false, 20, { level: e.level, ring: e.ring }), e.name, e.you ? h('span', { class: 'chip-s', text: 'You' }) : null),
          h('span', { class: 'mm', text: [e.move ? `${e.move > 0 ? '▲' : '▼'}${Math.abs(e.move)}` : null, gap ? `${gap > 0 ? '+' : '−'}${num(Math.abs(gap))}` : null].filter(Boolean).join(' · ') }),
          h('span', { class: 'ma mono', text: fmt(e.value) })));
      });
      // fewer than 5 players: today's par rows fill the empty places (C6)
      if (rows.filter(e => !e.sep).length < 5 && metric === 'points') {
        const pars = ((S.board && S.board.pars) || []).filter(p => [3, 5, 7, 9].includes(p.level)).sort((a, b) => b.points - a.points);
        pars.slice(0, 5 - rows.length).forEach(p => ul.append(h('li', { class: 'par' }, h('span', { class: 'mt', text: `L${p.level} par · today’s Daily` }), h('span', { class: 'ma mono', text: num(p.points) }))));
      }
      if (!rows.length && !ul.childElementCount) ul.append(h('li', {}, h('span', { class: 'mm', text: 'No one has scored this week yet.' })));
      box.replaceChildren(ul, h('div', { class: 'foot-links' }, quiet('Full board ›', null, { href: `/compete/leaderboard/?metric=${metric}&period=week` })));
    } catch (e) { box.replaceChildren(); UI.cardError(box, renderPreview); }
  }

  /* ------------------------------------------------------------ Traps this week (C12) */
  /* ------------------------------------------------------------ Champions (C27) */
  function renderChamps() {
    const list = S.hub.champions || [];
    const last = list[0];
    const kids = [head('Champions', last ? null : C.info('Last week’s podiums show here once a week closes, Mondays at 12:00 UTC.', 'About champions'))];
    if (last) {
      const b = last.boards || {};
      const names = arr => (arr || []).slice(0, 3);
      const table = h('table', { class: 'table compact' }, h('caption', { text: `${last.kind === 'season' ? 'Season' : 'Week'} ${last.period}` }),
        h('thead', {}, h('tr', {}, h('th', { scope: 'col', text: '' }), h('th', { scope: 'col', text: 'Points' }), h('th', { scope: 'col', text: 'Over par' }), h('th', { scope: 'col', text: 'Most improved' }))),
        h('tbody', {}, [0, 1, 2].map(i => h('tr', {}, h('td', { class: 'n', text: `#${i + 1}` }),
          ['points', 'net', 'change'].map(k => { const e = names(b[k])[i]; return h('td', { class: e && e.you ? 'you' : null, text: e ? `${e.name}${e.you ? ' (you)' : ''}` : '—' }); })))));
      kids.push(h('div', { class: 'table-wrap' }, table));
      if (b.bands) kids.push(h('p', { class: 'meta', text: Object.entries(b.bands).map(([band, e]) => `Levels ${band}: ${(e && (e.name || (e[0] && e[0].name))) || '—'}`).join(' · ') }));
    }
    kids.push(h('div', { class: 'foot-links' }, quiet('Hall of champions ›', null, { href: '/compete/rankings/#champions' })));
    card('#champs', ...kids);
  }

  /* ------------------------------------------------------------ F. next badges (C23) */
  function goFor(b) {
    if (b.go && b.go.href) return b.go;
    const daily = { href: C.href(S.hub.daily.id), label: S.hub.daily.me && S.hub.daily.me.status === 'finished' ? 'Tomorrow’s Daily' : 'Start the challenge' };
    const kindGo = (k, label) => (idOf(k) ? { href: C.href(idOf(k)), label } : null);
    const map = {
      'first-contest': daily, 'daily-7': daily, 'daily-30': daily, 'perfect-ten': daily, 'top-ten': daily, podium: daily, 'over-par': daily, 'won-back': daily,
      'pace-setter': { href: C.href(S.hub.daily.id, { race: 'pace' }), label: 'Race SAT pace' },
      sprinter: kindGo('sprint', 'Sprint'), 'weekly-4': kindGo('weekly', 'Weekly Module'), 'dress-rehearsal': kindGo('final', 'Season Final'),
      'level-5': kindGo('rush', 'Rush'), 'level-8': kindGo('rush', 'Rush'), 'all-rounder': kindGo('rush', 'Rush'), rush: kindGo('rush', 'Rush'),
      'trap-week': kindGo('trap', 'Trap of the week'), 'trap-hunter': { href: '/review/', label: 'Fix mistakes' },
      'season-top-10': { href: '/compete/leaderboard/?period=season', label: 'Season standings' },
      'streak-7': { href: '/', label: 'Up next' }, consistency: { href: '/', label: 'Up next' }, 'solved-1000': { href: '/practice/', label: 'Practise' },
    };
    return map[b.id] || null;
  }
  function renderBadges() {
    const list = S.hub.next_badges || [];
    const kids = [head('Next badges', quiet('All badges ›', null, { href: '/compete/rankings/#badges' }))];
    const ul = h('ul', { class: 'mini-rows' });
    list.forEach(b => {
      const li = h('li', { class: 'badge-row' });
      const go = goFor(b);
      const m = h('div', { class: 'mm' });
      UI.meter(m, { label: b.rule, value: b.have, max: b.need, text: `${num(b.have)}/${num(b.need)}` });
      li.append(h('span', { class: 'mt', text: b.name }), m);
      if (go) li.append(h('span', { class: 'ma' }, quiet('Go', null, { href: go.href })));
      if (go) UI.tooltip(li.querySelector('.ma a'), go.label);
      ul.append(li);
    });
    kids.push(list.length ? ul : h('p', { class: 'help', text: 'Every badge is earned. New ladders open as you climb.' }));
    card('#badges', ...kids);
  }

  /* ------------------------------------------------------------ G. your private contests (C18) */
  async function renderPrivate() {
    try {
      const r = await api('/contests?status=private&limit=50');
      const codes = (() => { try { return JSON.parse(localStorage.getItem('satf.contest.codes') || '{}'); } catch (_) { return {}; } })();
      // one row per series (its live round, else the next) and per open one-off
      const by = new Map();
      (r.contests || []).forEach(c => {
        if (c.status === 'closed') return;
        const key = c.series || c.id, cur = by.get(key);
        if (!cur || (c.status === 'live' && cur.status !== 'live') || (c.status === cur.status && (c.round || 0) < (cur.round || 0))) by.set(key, c);
      });
      const kids = [head('Your private contests', by.size ? null : C.info('Private contests are for friends: make one and share the link.', 'About private contests'))];
      if (!by.size) {
        kids.push(h('div', { class: 'row-act' }, quiet('+ Create a contest', () => C.create()), quiet('Join with a code', () => C.join())));
      } else {
        const ul = h('ul', { class: 'mini-rows' });
        by.forEach((c, key) => {
          const code = c.code || codes[key] || codes[c.id];
          const ents = c.entrants || [];
          const dots = h('span', { class: 'edots' }, ents.map(e => { const d = h('i', { class: `edot${e.status === 'finished' ? 'done' : e.status === 'progress' ? 'progress' : ''}`, tabindex: '0' });
            UI.tooltip(d, `${e.name}: ${e.status === 'finished' ? 'done' : e.status === 'progress' ? 'in progress' : 'not yet'}`); return d; }));
          const acts = h('span', { class: 'ma' });
          if (code) acts.append(quiet('Copy link', () => UI.copyText(`${location.origin}/compete/contest/?code=${code}`)));
          const mePid = S.board && S.board.you && S.board.you.pid;
          const waiting = ents.filter(e => e.status === 'new' && e.name !== 'Anonymous' && e.pid && e.pid !== mePid);
          if (waiting.length && c.status === 'live') {
            const nb = h('button', { type: 'button', class: 'quiet', text: 'Nudge' });
            UI.menu.bind(nb, () => waiting.map(e => ({ label: e.name, onClick: async () => {
              try { await api('/compete/nudge', { method: 'POST', body: { contest: c.id, member: e.pid } }); UI.toast(`Nudged ${e.name}`); }
              catch (err) { UI.toast(err.status === 429 ? `${e.name} was already nudged this round.` : 'Couldn’t nudge. Try again.'); }
            } })), { label: 'Nudge' });
            acts.append(nb);
          }
          ul.append(h('li', {}, h('a', { class: 'mt link', href: C.href(c.id), text: c.title }),
            h('span', { class: 'mm' }, C.windowLine(c), ents.length ? ' · ' : '', dots), acts));
        });
        kids.push(ul, h('div', { class: 'foot-links' }, quiet('+ Create a contest', () => C.create()), quiet('Join with a code', () => C.join())));
      }
      card('#private', ...kids);
    } catch (e) { fail('#private', renderPrivate); }
  }

  /* ------------------------------------------------------------ the season recap (C21) */
  async function renderRecap() {
    if (!S.hub || !S.hub.recap) return;   // the hub says when a closed season has a recap
    try {
      const r = await api('/compete/recap');
      const text = r && (r.text || r.line);
      const id = r && (r.season || r.id);
      let off = null; try { off = localStorage.getItem('satf.recap.off'); } catch (_) {}
      if (!text || (id && off === id)) return;
      const el = $('#recap');
      const dismiss = quiet('Dismiss', () => { try { localStorage.setItem('satf.recap.off', id || '1'); } catch (_) {} el.replaceChildren(); });
      el.replaceChildren(h('section', { class: 'card', 'aria-label': 'Season recap' }, kline('SEASON RECAP'), h('p', { class: 'line', text }),
        r.goal ? h('p', { class: 'meta', text: r.goal }) : null,
        h('div', { class: 'row-act' }, quiet('Copy recap', () => UI.copyText(text)), dismiss)));
    } catch (_) {}
  }

  /* ------------------------------------------------------------ load */
  function paintSkeletons() {
    skel('#daily', 'card:4'); skel('#contests', 'rows:3'); skel('#qotd', 'line'); skel('#stats', 'card:3');
    skel('#rivals', 'rows:3'); skel('#season', 'lines:2'); skel('#preview', 'rows:5');
    skel('#champs', 'lines:3'); skel('#badges', 'rows:3'); skel('#private', 'lines:2');
  }
  function renderHub() {
    try { renderDaily(); } catch (e) { console.error(e); }
    renderStats(); renderSeason(); renderChamps(); renderBadges(); renderRecap();
  }
  async function load() {
    paintSkeletons();
    let hubP;
    try {
      hubP = UI.cached('/compete', hub => { S.hub = hub; renderHub(); renderPreview(); });
      const [, me] = await Promise.all([hubP, UI.cached('/compete/me', me => { S.me = me; if (S.hub) renderHub(); })]);
      S.me = me;
    } catch (e) {
      if (!S.hub) ['#daily', '#stats', '#season', '#preview', '#champs', '#badges'].forEach(s => fail(s, load));
      return;
    }
    const d = S.hub.daily;
    try { S.board = await api(`/contest/${encodeURIComponent(d.id)}/board?limit=5`); } catch (_) {}
    renderDaily();
    if (!(S.hub.board_preview && S.hub.board_preview.players >= 5)) renderPreview();
  }
  load();
  renderContests(); loadCounts();
  renderQotd(); renderRivals(); renderPrivate();

  // Enter starts or resumes the Daily while focus is on the page body (C24)
  UI.keys.register('compete-overview', {
    Enter: { does: 'Start or resume the Daily Challenge', run: () => {
      const d = S.hub && S.hub.daily; if (!d) return;
      if (d.me && d.me.status === 'finished') location.href = C.href(d.id);
      else if (d.me && d.me.status === 'progress') C.start(d.id);
      else if (C.rulesSeen('daily')) C.start(d.id, { kind: 'daily' });
      else location.href = C.href(d.id);
    } },
  }, { label: 'This page', when: () => { const a = document.activeElement; return !a || a === document.body || a.id === 'main'; } });
})();
