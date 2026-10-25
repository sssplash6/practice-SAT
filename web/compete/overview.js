/* ============================================================================
   Compete Overview /compete/ (spec/rebuild-v2.md 3.7 §3; compete.md C2, C5-C7, C9, C10,
   C12, C18, C21, C23-C25, C27; decision 7: only what the student needs, details on demand)
   Reads GET /api/compete (the hub), /api/compete/me, /api/contests, /api/compete/rivals,
   /api/qotd and /api/leaderboard; every card loads, fails and retries on its own.
   ========================================================================== */
(() => {
  const h = UI.h, C = UI.compete, $ = s => document.querySelector(s);
  const num = C.num, mmss = C.mmss;
  const api = (p, o) => UI.api(p, o);
  const S = { hub: null, me: null, live: null, board: null, subject: UI.subject.get() };
  const WHY = { ghost: 'Sat after the contest closed: it shows where you would have placed.', repeat: 'A second sitting of this contest.', fast: 'Answers came in faster than the questions can be read.' };
  // the page shows one subject (the switch under the title): its Daily, contests, rating, rivals and board
  const sub = p => `${p}${p.includes('?') ? '&' : '?'}subject=${S.subject}`;
  const dailyAlias = () => (S.subject === 'rw' ? 'daily-rw' : 'daily');
  const sfx = () => (S.subject === 'rw' ? '-rw' : '');      // daily-YYYY-MM-DD-rw

  const card = (id, ...kids) => { const el = $(id); el.replaceChildren(...kids.filter(Boolean)); return el; };
  const head = (title, ...right) => h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: title }), right.some(Boolean) ? h('div', { class: 'card-act' }, right) : null);
  const quiet = (text, onClick, o = {}) => { const b = h(o.href ? 'a' : 'button', { class: 'quiet', type: o.href ? null : 'button', href: o.href || null, text }); if (onClick) b.addEventListener('click', onClick); return b; };
  const CHEV = () => h('span', { class: 'chev', 'aria-hidden': 'true', html: UI.svg(UI.ICON.chev, 16) });
  const fail = (sel, retry, text) => { const el = $(sel); el.replaceChildren(); UI.cardError(el, retry, text || 'The server is not answering.'); };
  const skel = (sel, shape) => { const el = $(sel); if (!el.childElementCount) UI.skel(el, shape); };
  // a press that waits: the button says so (ui.css draws the spinner after 300ms at the same width)
  const busy = async (b, fn) => { b.disabled = true; b.setAttribute('aria-busy', 'true'); try { await fn(); } catch (e) { UI.toast(e.message || 'Couldn’t start. Try again.'); } finally { b.disabled = false; b.removeAttribute('aria-busy'); } };
  const idOf = kind => ((S.live || []).find(c => c.kind === kind) || {}).id;

  /* ------------------------------------------------------------ header */
  $('#subnav').replaceWith(C.subnav('overview'));
  UI.subjectSeg($('#subject'), { value: S.subject, onChange: v => {
    S.subject = v; S.hub = S.me = S.board = S.live = null; S.rated = undefined; tab = 'live'; shown = 10; filter = null;
    Object.keys(counts).forEach(k => { counts[k] = null; });
    load(); renderContests(); loadCounts(); renderRivals(); renderPrivate(); renderQotd();
  } });
  $('#join').addEventListener('click', () => C.join());
  $('#create').addEventListener('click', () => C.create());
  $('#join-create').addEventListener('click', () => {
    const s = UI.sheet({ title: 'Join or create', size: 's', body: b => b.append(
      h('div', { class: 'row-act' }, quiet('Join with a code', () => { s.close(); C.join(); }), quiet('Create a contest', () => { s.close(); C.create(); }))) });
  });

  /* ------------------------------------------------------------ A. the Daily Challenge */
  const ladder = C.ladder, fieldLine = C.fieldLine;
  function followChip(fu) {
    if (!fu) return null;
    if (fu.won_back !== null && fu.won_back !== undefined && fu.of) return h('span', { class: 'badge soft', text: `Won back ${num(fu.won_back)}/${num(fu.of)}` });
    if (fu.due) return h('a', { class: 'btn sm', href: fu.session ? `/practice/session/?id=${encodeURIComponent(fu.session)}` : C.href(S.hub.daily.id), text: `Rematch · ${C.dayLabel(fu.due, { weekday: true }).split(',')[0]}` });
    return null;
  }
  let stopNext = null;
  async function renderDaily() {
    const c = S.hub.daily, me = c.me || {};
    const el = $('#daily');
    const day = String(c.id).slice(6, 16);
    const next = h('span', { class: 'meta' });
    const midnight = new Date(); midnight.setHours(24, 0, 0, 0);
    const streak = S.hub.me && S.hub.me.challenge_streak;
    const best = S.me && S.me.streak && S.me.streak.best;
    // the challenge streak (Daily Challenges in a row), not the study streak the sidebar shows: a flame and the count by the title
    const chip = streak ? h('span', { class: 'd-streak', tabindex: '0', 'aria-label': `${num(streak)}-day challenge streak` },
      UI.ICON && UI.ICON.flame ? h('span', { 'aria-hidden': 'true', html: UI.svg(UI.ICON.flame, 16) }) : null, h('span', { 'aria-hidden': 'true', text: num(streak) })) : null;
    if (chip) UI.tooltip(chip, `${num(streak)}-day challenge streak: Daily Challenges in a row${best > streak ? ` · best ${num(best)}` : ''}`);
    // today's sitting extended it: the flame fills once (a day, on this device)
    if (chip && me.status === 'finished' && UI.fx && UI.motion && UI.motion.once(`d-streak.${day}`, 'local')) setTimeout(() => UI.fx.flame($('#daily .d-streak')), 400);   // the card may repaint once fresh data lands
    const top = h('div', { class: 'card-head' }, h('h2', { class: 'h2', id: 'daily-h', text: 'Daily Challenge' }), h('span', { class: 'meta', text: C.dayLabel(day) }), chip);
    next.setAttribute('aria-live', 'off');
    if (stopNext) stopNext();
    const cd = UI.countdown(next, midnight.toISOString(), { label: 'Next Daily', onEnd: () => load() });
    stopNext = typeof cd === 'function' ? cd : cd && cd.stop;
    const body = [top];
    const done = me.status === 'finished';
    const nextLine = done ? h('p', { class: 'meta' }, 'Next one in ', next) : null;
    // before a sitting: one facts line, the way in, then the ten questions; after it, the result leads
    if (!done) {
      body.push(h('div', { class: 'daily-lines' },
        h('p', { class: 'line' }, `${c.count} questions · ${mmss(c.seconds)} to answer · ranked${(par => par && par.base !== undefined && par.base !== null ? ` · expected score ${UI.num(par.points ?? par.base)} (about ${UI.num(par.right)} right)` : '')(c.me && c.me.par)} `, C.info('The clock runs only while a question is open. Skipped and voided questions score 0. Expected score is what a student at your rating scores on these questions, on average.', 'About the clock'))));
    }
    // More: the day's quieter jobs in one menu behind a quiet dots button (Warm up joined it)
    const yday = new Date(); yday.setDate(yday.getDate() - 1);
    const yid = `daily-${yday.getFullYear()}-${String(yday.getMonth() + 1).padStart(2, '0')}-${String(yday.getDate()).padStart(2, '0')}${sfx()}`;
    const moreBtn = extra => {
      const b = h('button', { type: 'button', class: 'ibtn d-more', 'aria-label': 'More' }, UI.icon('more', 20));
      UI.menu.bind(b, () => [...extra, { label: 'Past days', href: C.href(yid) }, { label: 'Daily reminder', onClick: () => C.reminder() }], { label: 'More' });
      UI.tooltip(b, 'More');
      return b;
    };
    const st = h('div', { class: 'daily-status' });
    if (me.status === 'new') {
      const go = h('button', { type: 'button', class: 'pill', text: 'Start the challenge' });
      go.addEventListener('click', () => {
        if (C.rulesSeen('daily')) busy(go, () => C.start(c.id, { kind: 'daily' }));
        else location.href = C.href(c.id);
      });
      // Warm up waits in the menu: two questions on each of your three lowest-chance skills, offered only before you start
      const warm = { label: 'Warm up · 6', sub: 'Two on each of your 3 lowest-chance skills', onClick: async () => {
        try { const r = await api(`/contest/${encodeURIComponent(c.id)}/warmup`, { method: 'POST', body: {} }); location.href = `/practice/session/?id=${encodeURIComponent(r.session)}`; }
        catch (e) { UI.toast(e.message || 'Couldn’t start. Try again.'); }
      } };
      st.append(h('div', { class: 'row-act d-act' }, go, moreBtn([warm, { separator: true }])));
    } else if (me.status === 'progress') {
      const go = h('button', { type: 'button', class: 'pill', text: 'Resume' });
      go.addEventListener('click', () => busy(go, () => C.start(c.id)));
      st.append(h('div', { class: 'row-act d-act' }, go, h('span', { class: 'meta', text: `${num(me.answered)} of ${num(c.count)} answered${me.clock ? ` · ${mmss(me.clock.left)} on the clock` : ''}` }), moreBtn([])));
    } else {
      const r = me.result || {};
      const place = S.board && S.board.you;
      const players = (S.board && S.board.players) || (c.field && c.field.players);
      // the result is the headline: the contest page's big rank, scaled down, the score beneath
      const big = h('div', { class: 'big-rank daily-rank' });
      if (place && place.rank && me.ranked !== false) {
        big.append(h('span', { class: 'num', text: `${place.tie ? '=' : ''}#${place.rank}` }), h('span', { class: 'of', text: `of ${num(players)}` }));
        if (players >= 10) big.append(h('span', { class: 'badge soft', text: `Top ${Math.ceil(place.rank / players * 100)}%` }));
      }
      st.append(...[big.childElementCount ? big : null,
        h('p', { class: 'daily-res', text: [`${num(r.right)}/${num(r.asked || c.count)}`, `${num(r.points)} pts`, me.clock ? mmss(me.clock.used) : null].filter(Boolean).join(' · ') })].filter(Boolean));
      if (me.ranked === false) st.append(h('p', { class: 'line' }, h('span', { class: 'badge soft', text: 'Unranked' }), ' ', WHY[me.why] || ''));
      UI.strip(st, C.marks(r), { onPick: i => { location.href = `${C.href(c.id)}#q${i + 1}`; }, label: 'Your answers' });
      const chips = h('div', { class: 'row-act' });
      if (r.rating_after !== undefined && r.rating_before !== undefined) {
        const d = Math.round(r.rating_after - r.rating_before);
        chips.append(h('span', { class: 'badge soft', text: `${d >= 0 ? '+' : '−'}${Math.abs(d)} → ${num(Math.round(r.rating_after))} · Level ${C.levelOf(r.rating_after)}` }));
      }
      const fu = followChip(me.followup);
      if (fu) chips.append(fu);
      if (chips.childElementCount) st.append(chips);
      const copy = { label: 'Copy result', onClick: () => UI.copyText(C.copyResult(c, { ...r, secs: me.clock ? me.clock.used : undefined }, { rank: place && place.rank, players })) };
      st.append(h('div', { class: 'row-act d-act' }, h('a', { class: 'pill', href: `${C.href(c.id)}#board`, text: 'See the board' }),
        quiet('Review answers', null, { href: `${C.href(c.id)}#review` }), moreBtn([copy, { separator: true }])));
    }
    body.push(st);
    if (!done) { const lad = h('div', { class: 'sub-block' }); ladder(lad, c); body.push(lad); }
    // a make-up shows only when yesterday was missed and there is a streak for it to keep
    const strip = S.me && S.me.streak && S.me.streak.strip;
    const yday0 = yid.slice(6, 16);
    const ystate = strip && (strip.find(x => x.day === yday0) || {}).state;
    const keep = ystate === 'missed' ? C.streakBefore(strip, yday0) : 0;
    if (keep >= 1) body.push(h('div', { class: 'row-act' }, h('a', { class: 'btn sm', href: C.href(yid), text: `Keep your ${num(keep)}-day streak: make up ${C.dayLabel(yday0, { weekday: false })}` })));
    // the foot: who has sat it, and the question of the day as one row (it was a card of its own)
    body.push(h('div', { class: 'daily-foot' }, fieldLine(c), nextLine, qotdRow));
    el.replaceChildren(...body);
  }

  /* ------------------------------------------------------------ B. contests */
  const TRAINS = { daily: 'the ten skills of the day', sprint: 'speed in the week’s domain', weekly: 'module pace and routing', final: 'a full adaptive section',
    trap: 'this week’s recurring mistake', rush: 'your top level, one question at a time', words: 'Words in Context and Transitions', private: 'the skills your friends picked' };
  let tab = 'live', shown = 10;
  const counts = { live: null, upcoming: null, finished: null, private: null };
  function crow(c) {
    const me = c.me || {}, k = C.kind(c);
    const title = c.series && c.round ? `${c.title} · round ${c.round}${c.spec && c.spec.repeat ? ` of ${c.spec.repeat.rounds}` : ''}` : C.title(c);
    let chip = null;
    if (me.status === 'progress') chip = `In progress${me.clock && me.clock.left !== undefined ? ` · ${mmss(me.clock.left)} left` : ''}`;
    else if (me.status === 'finished') chip = me.result && me.result.points !== undefined ? `Finished · ${num(me.result.points)} pts` : 'Finished';
    const par = me.status === 'new' && me.par && me.par.base && ['daily', 'weekly', 'final', 'trap'].includes(c.kind) ? num(me.par.base) : null;
    // the row is a title and a timer; a tap opens the details in a window with Start
    const open = () => contestSheet(c, title, chip, par);
    const row = h('div', { class: 'crow', role: 'button', tabindex: '0', 'data-key': c.id, 'aria-label': `${title}. Open the details.` }, C.icon(c.kind),
      h('div', {}, h('span', { class: 't', text: title }), timerFor(c)),
      chip ? h('span', { class: 'st badge soft', text: chip }) : h('span'), CHEV());
    row.addEventListener('click', open);
    row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    return row;
  }
  // "Ends in 2d 07:44:02", ticking (the window line for contests that are not live)
  function timerFor(c) {
    if (c.status !== 'live' || !UI.countdown) return h('span', { class: 'w', text: C.windowLine(c) });
    const tm = h('b', { class: 'mono' });
    UI.countdown(tm, c.closes, { label: 'Time left' });
    return h('span', { class: 'w' }, c.series && c.round ? `Round ${c.round}${c.spec && c.spec.repeat && c.spec.repeat.rounds ? ` of ${c.spec.repeat.rounds}` : ''} · ` : '', 'Ends in ', tm);
  }
  // every detail of a contest in one window: what it is, the clock, who is in, and the way in
  function contestSheet(c, title, chip, par) {
    const me = c.me || {}, k = C.kind(c);
    const rows = [];
    const row = (label, value) => value ? rows.push(h('div', { class: 'cs-row' }, h('span', { class: 'k', text: label }), h('b', { text: value }))) : null;
    if (c.kind === 'sprint') row('Questions', 'As many as you answer');
    else if (c.kind === 'rush') row('Questions', 'The difficulty climbs with you');
    else row('Questions', c.count ? `${c.count}` : null);
    row('Time', C.clockText(c));
    if (k.twins || (c.kind === 'private' && c.spec && c.spec.twin)) row(c.subject === 'rw' ? 'Passages' : 'Numbers', 'Different for everyone');
    const n = c.field && c.field.players;
    row('Entered', n ? `${num(n)}` : null);
    row('Expected score', par);
    const tm = h('b', { class: 'mono' });
    const ends = c.status === 'live' && UI.countdown ? (UI.countdown(tm, c.closes, { label: 'Time left' }), h('p', { class: 'cs-ends' }, 'Ends in ', tm)) : h('p', { class: 'cs-ends', text: C.windowLine(c) });
    const act = c.status === 'upcoming' ? { label: 'Add to calendar', onClick: () => { UI.ics({ title: `SAT Freshman · ${title}`, start: new Date(c.opens), minutes: 30, url: `${location.origin}${C.href(c.id)}` }); return false; } }
      : me.status === 'progress' ? { label: 'Resume', primary: true, onClick: () => { C.start(c.id); return false; } }
      : me.status === 'finished' ? { label: 'Results', primary: true, onClick: () => { location.href = C.href(c.id); return false; } }
      : c.status === 'live' ? { label: 'Start', primary: true, onClick: () => { location.href = C.href(c.id); return false; } }
      : { label: 'Open', primary: true, onClick: () => { location.href = C.href(c.id); return false; } };
    UI.sheet({ title, size: 's', body: b => b.append(h('div', { class: 'cs' },
      h('div', { class: 'cs-top' }, C.icon(c.kind), h('span', { class: 'meta', text: k.label }), chip ? h('span', { class: 'badge soft st', text: chip }) : null),
      ends, h('div', { class: 'cs-rows' }, rows),
      TRAINS[c.kind] ? h('p', { class: 'help', text: `Practises ${TRAINS[c.kind]}.` }) : null,
      h('a', { class: 'quiet', href: C.href(c.id), text: 'Open the contest page' }))),
      actions: [act] });
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
    }
    Object.entries(counts).forEach(([k, n]) => filter.count(k, n));
    loadRows();
  }
  async function loadRows() {
    const box = $('#crows');
    // the rows on screen stay while the next list loads, so the change can glide; a first load shows the skeleton
    const had = box.querySelector('.crow');
    if (!had) { box.replaceChildren(); UI.skel(box, 'rows:3'); }
    box.setAttribute('aria-busy', 'true');
    const swap = (...kids) => { box.removeAttribute('aria-busy'); return had && UI.glide ? UI.glide(box, () => box.replaceChildren(...kids)) : box.replaceChildren(...kids); };
    try {
      const r = await api(sub(`/contests?status=${tab}&limit=${shown}`));
      // the Daily card owns today's Daily: the Live list leaves every daily out, and its count with it
      if (tab === 'live') { const n0 = r.contests.length; r.contests = r.contests.filter(c => c.kind !== 'daily'); r.total = Math.max(0, (r.total || 0) - (n0 - r.contests.length)); }
      counts[tab] = r.total; filter.count(tab, r.total);
      if (tab === 'live') S.live = r.contests;
      const rows = r.contests.map(crow);
      if (!rows.length) {
        swap(tab === 'private'
          ? h('p', { class: 'crows-empty', text: 'No private contests yet. Make one for friends from Create a contest, or join with a code.' })
          : h('p', { class: 'crows-empty', text: tab === 'finished' ? 'No finished contests yet.' : 'Nothing here right now.' }));
        return;
      }
      swap(...rows);
      if (r.total > shown) box.append(h('div', { class: 'row-act' }, quiet(`Show ${Math.min(10, r.total - shown)} more`, () => { shown += 10; loadRows(); })));
      if (tab === 'live') renderSeason();
    } catch (e) { box.removeAttribute('aria-busy'); box.replaceChildren(); UI.cardError(box, loadRows, 'The server is not answering.'); }
  }
  async function loadCounts() {
    for (const k of ['finished', 'private']) {
      try { const r = await api(sub(`/contests?status=${k}&limit=0`)); counts[k] = r.total; if (filter) filter.count(k, r.total || null); } catch (_) {}
    }
  }

  /* ------------------------------------------------------------ C. question of the day: one row in the Daily card's foot */
  const qotdRow = h('div', { class: 'qotd-row', role: 'group', 'aria-label': 'Question of the day' });
  async function renderQotd() {
    try {
      // the subject's own question of the day (R&W's passage slot in the R&W view), else no row
      const all = await api('/qotd');
      const q = (all.slots || []).find(x => x.subject === S.subject);
      if (!q) { qotdRow.replaceChildren(); return; }
      const m = q.mine, qq = q.question || {};
      // one row with one way in; before an answer only its skill and difficulty (the user: no need to display the question)
      const go = quiet(m ? 'See it' : 'Answer', null, { href: `${C.href(dailyAlias())}#qotd` });
      const line = !m ? [qq.topic_name || (qq.topic && C.topicName(qq.topic)), C.TIER[qq.difficulty]].filter(Boolean).join(' · ')
        : m.correct ? ['Right', m.share !== undefined && m.n ? `${num(Math.round(m.share * m.n))} of ${num(m.n)} got it` : null, m.streak ? `${m.streak}-day streak` : null].filter(Boolean).join(' · ')
        : m.mistake || m.reason ? `Fell for: ${m.mistake || m.reason}` : 'Wrong';
      qotdRow.replaceChildren(h('span', { class: 't', text: 'Question of the day' }), h('span', { class: m ? 'line' : 'meta', text: line }), go);
    } catch (e) { qotdRow.replaceChildren(); UI.cardError(qotdRow, renderQotd, 'The question of the day didn’t load.'); }
  }

  /* ------------------------------------------------------------ D. your stats */
  function renderStats() {
    const hub = S.hub, me = hub.me || {}, mine = S.me || {};
    const boards = mine.boards || {};
    const players = hub.board_preview && hub.board_preview.players;
    const rating = me.rating;
    const lin = !me.provisional ? C.levelIn(rating, false) : null;
    const kids = [head('Your stats', quiet('Your rankings', null, { href: '/compete/rankings/' }))];
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
    const move = b => C.moved(b && b.move);
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
      const r = await api(sub('/compete/rivals'));
      const list = (r.rivals || []).slice(0, 3);
      const kids = [head('Rivals')];
      if (!list.length) {
        kids.push(h('p', { class: 'help', 'data-nofold': '', text: 'Rivals appear when 3 students near your level have played in the last two weeks. Until then, race your best run.' }),
          h('div', { class: 'row-act' }, quiet('Race your best', null, { href: C.href(dailyAlias(), { race: 'best' }) })));
      } else {
        const ul = h('ul', { class: 'mini-rows' });
        list.forEach(x => {
          const r2 = x.h2h || {};
          const rec = r2.you > r2.them ? `You lead ${r2.you}–${r2.them}` : r2.you < r2.them ? `${x.name} leads ${r2.them}–${r2.you}` : r2.you ? `Level ${r2.you}–${r2.them}` : null;
          ul.append(h('li', {}, h('span', { class: 'mt' }, UI.level(null, false, 20, { level: x.level, ring: x.ring }), x.name),
            h('span', { class: 'mm', text: [rec ? `${rec} this season` : null, x.last_shared ? `last shared ${C.dayLabel(C.localDay(x.last_shared), { weekday: false })}` : null].filter(Boolean).join(' · ') || 'No shared contest yet' }),
            h('span', { class: 'ma' }, quiet('Race', ev => busy(ev.currentTarget, async () => {
              // racing a rival replays their run on today's Daily, so they must have finished it
              try { await api(`/contest/${dailyAlias()}?race=${encodeURIComponent(x.pid)}`); location.href = C.href(dailyAlias(), { race: x.pid }); }
              catch (err) { UI.toast(err.status === 404 ? `${x.name} hasn’t finished today’s Daily yet.` : 'Couldn’t start the race. Try again.'); }
            })))));
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
    // the season's name and days left sit under the title (in the head they wrapped to a row of their own, pushed right)
    const kids = [head('Season', C.info('Every ranked contest adds to your season points.', 'About season points')),
      h('p', { class: 'meta', text: [s.name, days !== null ? `${days} day${days === 1 ? '' : 's'} left` : null].filter(Boolean).join(' · ') })];
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
    kids.push(h('div', { class: 'foot-links' }, quiet('Season standings', null, { href: sub('/compete/leaderboard/?period=season') })));
    card('#season', ...kids);
  }

  /* ------------------------------------------------------------ E. this week's board (C10, C6) */
  let metric = 'points';
  async function renderPreview() {
    const el = $('#preview');
    // the shared dropdown at the control height (a native select stood taller than every other control on the card)
    const pick = UI.dropdown(null, { label: 'Board', sm: true, plain: true, noAll: true, value: metric, options: [{ value: 'points', label: 'Points' }, { value: 'net', label: 'Over expected' }, { value: 'climb', label: 'Climb' }],
      onChange: v => { metric = v; renderPreview(); } });
    pick.el.classList.add('pick-sm');
    const hd = h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'This week' }), pick.el);
    const box = h('div');
    el.replaceChildren(hd, box);
    UI.skel(box, 'rows:5');
    try {
      const q = `metric=${metric}&period=week&limit=5&subject=${S.subject}`;
      const top = metric === 'points' && S.hub.board_preview ? S.hub.board_preview : await api(`/leaderboard?${q}`);
      let rows = [...(top.entries || [])];
      const you = top.you;
      if (you && you.rank > 5) {
        if (you.rank > 7) rows.push({ sep: true });
        const near = await api(sub(`/leaderboard?metric=${metric}&period=week&offset=${Math.max(5, you.rank - 3)}&limit=5`));
        (near.entries || []).forEach(e => { if (!rows.some(x => x.pid === e.pid)) rows.push(e); });
      }
      const ul = h('ul', { class: 'mini-rows' });
      const fmt = v => metric === 'net' ? `${v > 0 ? '+' : ''}${num(v)}` : num(v);
      rows.forEach(e => {
        if (e.sep) { ul.append(h('li', { class: 'sep', 'aria-hidden': 'true' })); return; }
        const gap = you && !e.you && you.value !== undefined ? e.value - you.value : null;
        ul.append(h('li', { class: e.you ? 'you' : null },
          h('span', { class: 'mt' }, h('span', { class: 'mono', text: `${e.tie ? '=' : ''}${e.rank}` }), UI.level(null, false, 20, { level: e.level, ring: e.ring }), e.you ? `${e.name} (you)` : e.name),
          h('span', { class: 'mm', text: [C.moved(e.move), gap ? `${gap > 0 ? '+' : '−'}${num(Math.abs(gap))}` : null].filter(Boolean).join(' · ') }),
          h('span', { class: 'ma mono', text: fmt(e.value) })));
      });
      // fewer than 5 players: today's par rows fill the empty places (C6)
      if (rows.filter(e => !e.sep).length < 5 && metric === 'points') {
        const pars = ((S.board && S.board.pars) || []).filter(p => [3, 5, 7, 9].includes(p.level)).sort((a, b) => b.points - a.points);
        pars.slice(0, 5 - rows.length).forEach(p => ul.append(h('li', { class: 'par' }, h('span', { class: 'mt', text: `L${p.level} par · today’s Daily` }), h('span', { class: 'ma mono', text: num(p.points) }))));
      }
      if (!rows.length && !ul.childElementCount) ul.append(h('li', {}, h('span', { class: 'mm', text: 'No one has scored this week yet.' })));
      box.replaceChildren(ul, h('div', { class: 'foot-links' }, quiet('Full board', null, { href: sub(`/compete/leaderboard/?metric=${metric}&period=week`) })));
    } catch (e) { box.replaceChildren(); UI.cardError(box, renderPreview); }
  }

  /* Champions (C27) live on Your rankings (#champions), with the band winners line */
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
      'season-top-10': { href: sub('/compete/leaderboard/?period=season'), label: 'Season standings' },
      'streak-7': { href: '/', label: 'Up next' }, consistency: { href: '/', label: 'Up next' }, 'solved-1000': { href: '/practice/', label: 'Practise' },
    };
    return map[b.id] || null;
  }
  function renderBadges() {
    const list = S.hub.next_badges || [];
    const kids = [head('Next badges', quiet('All badges', null, { href: '/compete/rankings/#badges' }))];
    const ul = h('ul', { class: 'mini-rows' });
    list.forEach(b => {
      const li = h('li', { class: 'badge-row' });
      const go = goFor(b);
      const m = h('div', { class: 'mm' });
      const mt = UI.meter(m, { label: b.rule, value: b.have, max: b.need, text: `${num(b.have)}/${num(b.need)}` });
      if (!b.have && mt && mt.el) { const bar = mt.el.querySelector('.meter-bar'); if (bar) bar.style.display = 'none'; }   // no grey bar until there is progress
      li.append(h('span', { class: 'mt' }, C.badgeIcon ? C.badgeIcon(b, false, { size: 'sm' }) : null, b.name), m);
      // the way to it says where it goes (it read "Go", with the place only in a tooltip)
      if (go) li.append(h('span', { class: 'ma' }, quiet(go.label, null, { href: go.href })));
      ul.append(li);
    });
    kids.push(list.length ? ul : h('p', { class: 'help', text: 'Every badge is earned. New ladders open as you climb.' }));
    card('#badges', ...kids);
  }

  /* ------------------------------------------------------------ G. your private contests (C18) */
  async function renderPrivate() {
    try {
      const r = await api(sub('/contests?status=private&limit=50'));
      const codes = (() => { try { return JSON.parse(localStorage.getItem('satf.contest.codes') || '{}'); } catch (_) { return {}; } })();
      // one row per series (its live round, else the next) and per open one-off
      const by = new Map();
      (r.contests || []).forEach(c => {
        if (c.status === 'closed') return;
        const key = c.series || c.id, cur = by.get(key);
        if (!cur || (c.status === 'live' && cur.status !== 'live') || (c.status === cur.status && (c.round || 0) < (cur.round || 0))) by.set(key, c);
      });
      const kids = [head('Your private contests')];
      // none yet: the card stays out (the header's Create and Join, and the Private tab, say the rest)
      $('#private').hidden = !by.size;
      if (by.size) {
        const ul = h('ul', { class: 'mini-rows' });
        by.forEach((c, key) => {
          const code = c.code || codes[key] || codes[c.id];
          const ents = c.entrants || [];
          const dots = h('span', { class: 'edots' }, ents.map(e => { const d = h('i', { class: `edot ${e.status === 'finished' ? 'done' : e.status === 'progress' ? 'progress' : ''}`.trim(), tabindex: '0' });
            UI.tooltip(d, `${e.name}: ${e.status === 'finished' ? 'done' : e.status === 'progress' ? 'in progress' : 'not yet'}`); return d; }));
          const acts = h('span', { class: 'ma' });
          if (code) acts.append(quiet('Copy link', ev => C.copy(ev.currentTarget, `${location.origin}/compete/contest/?code=${code}`)));
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
            h('span', { class: 'mm' }, timerFor(c), ents.length ? ' · ' : '', dots), acts));
        });
        kids.push(ul);
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
      el.replaceChildren(h('section', { class: 'card', 'aria-label': 'Season recap' }, head('Season recap'), h('p', { class: 'line', text }),
        r.goal ? h('p', { class: 'meta', text: r.goal }) : null,
        h('div', { class: 'row-act' }, quiet('Copy recap', ev => C.copy(ev.currentTarget, text)), dismiss)));
    } catch (_) {}
  }

  /* ------------------------------------------------------------ load */
  function paintSkeletons() {
    skel('#daily', 'card:4'); skel('#contests', 'rows:3'); skel('#stats', 'card:3');
    skel('#rivals', 'rows:3'); skel('#season', 'lines:2'); skel('#preview', 'rows:5');
    skel('#badges', 'rows:3'); skel('#private', 'lines:2');
  }
  function renderHub() {
    try { renderDaily(); } catch (e) { console.error(e); }
    renderStats(); renderSeason(); renderBadges(); renderRecap();
  }
  async function load() {
    paintSkeletons();
    let hubP;
    try {
      hubP = UI.cached(sub('/compete'), hub => { S.hub = hub; renderHub(); renderPreview(); });
      const [, me] = await Promise.all([hubP, UI.cached(sub('/compete/me'), me => { S.me = me; if (S.hub) renderHub(); })]);
      S.me = me;
    } catch (e) {
      if (!S.hub) { ['#daily', '#stats', '#season', '#preview', '#badges'].forEach(s => fail(s, load)); $('#daily').append(h('div', { class: 'daily-foot' }, qotdRow)); }
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
