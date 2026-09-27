/* ============================================================================
   The contest page /compete/contest/?id=… | ?code=… (spec/rebuild-v2.md 3.7 §4;
   compete.md C1-C3, C4 (the test-day card), C5-C9, C15-C20, C22, C24, C25, C27)
   One page for every kind and state: the lobby (upcoming, live), resume, the result
   panel with the debrief and the time block, the board (list or grid), the review, the
   field's traps, the question of the day (daily), entrants and settings (private).
   ========================================================================== */
(() => {
  const h = UI.h, C = UI.compete, $ = s => document.querySelector(s);
  const num = C.num, mmss = C.mmss, pct = C.pct;
  const api = (p, o) => UI.api(p, o);
  const enc = encodeURIComponent;
  const P = new URLSearchParams(location.search);
  let cid = P.get('id') || (P.get('code') ? '' : 'daily');
  const code = P.get('code');
  let race = P.get('race') || '';
  const S = { c: null, board: null, scope: 'all', view: 'round', sort: 'points', grid: false, review: null, filter: 'all', sel: null,
    streak: null, prefs: null, follow: new Set(), rivals: null, polled: 0, api: null };
  const WHY = { ghost: 'Sat after it closed: it shows where you would have placed. It doesn’t count for rank, rating or season points.',
    repeat: 'A second sitting of this contest.', fast: 'Not ranked: answers came in faster than the questions can be read.' };
  const TIMING = { official: 'Official', 'x1.5': '1.5×', x2: '2×' };
  const FACTOR = { official: 1, 'x1.5': 1.5, x2: 2 };
  const STATUS = { correct: '✓', incorrect: '✕', skipped: '»', voided: '⊘', unanswered: '–' };
  const STATUS_WORD = { correct: 'Right', incorrect: 'Wrong', skipped: 'Skipped', voided: 'Voided', unanswered: 'Not answered' };

  const quiet = (text, onClick, o = {}) => { const b = h(o.href ? 'a' : 'button', { class: 'quiet', type: o.href ? null : 'button', href: o.href || null, text }); if (onClick) b.addEventListener('click', onClick); return b; };
  const head2 = (id, title, ...right) => h('div', { class: 'card-head' }, h('h2', { class: 'h2', id, text: title }), right.filter(Boolean).length ? h('div', { class: 'card-act' }, right.filter(Boolean)) : null);
  const show = (sel, on = true) => { const el = $(sel); el.hidden = !on; return el; };
  const busy = async (b, fn) => { if (b) b.disabled = true; try { await fn(); } catch (e) { UI.toast(e.message || 'Couldn’t do that. Try again.'); } finally { if (b) b.disabled = false; } };
  const runner = r => { const to = C.runner(r); if (to) location.href = to; };
  const drill = body => api('/drill', { method: 'POST', body }).then(runner);
  const finished = () => S.c && S.c.me && S.c.me.status === 'finished';
  const open = () => S.c && (finished() || S.c.status === 'closed');
  const dayOf = c => String(c.id).slice(6);
  const todayISO = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
  const shiftDay = (day, n) => { const d = new Date(`${day}T12:00:00`); d.setDate(d.getDate() + n); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
  const stat = (label, value, sub) => h('div', { class: 'stat' }, h('span', { class: 'stat-k', text: label }), h('span', { class: 'stat-v', text: value ?? '—' }), sub ? h('span', { class: 'stat-sub', text: sub }) : null);
  const myPid = () => S.board && S.board.you && S.board.you.pid;
  const localCode = c => { try { const m = JSON.parse(localStorage.getItem('satf.contest.codes') || '{}'); return m[c.series || c.id] || m[c.id] || null; } catch (_) { return null; } };
  const titleParts = c => { const t = C.title(c); const i = t.indexOf(' · '); return i > 0 ? [t.slice(0, i), t.slice(i + 3)] : [C.kind(c).label, t]; };

  /* ------------------------------------------------------------ load */
  async function load() {
    UI.skel($('#head'), 'lines:2'); UI.skel($('#state'), 'card:4');
    try {
      const q = new URLSearchParams();
      if (code) q.set('code', code);
      if (race) q.set('race', race);
      let c;
      try { c = await api(`/contest/${enc(cid || 'lookup')}${q.toString() ? '?' + q : ''}`); }
      catch (e) {
        if (e.status === 403 && race) { UI.toast('This run is private now.'); race = ''; q.delete('race'); c = await api(`/contest/${enc(cid || 'lookup')}${q.toString() ? '?' + q : ''}`); }
        else throw e;
      }
      S.c = c;
      if (c.join) return joinView(c);
      if (cid !== c.id) { cid = c.id; history.replaceState(null, '', C.href(c.id, { race }) + location.hash); }
      document.title = `${c.kind === 'daily' ? `Daily Challenge · ${C.dayLabel(dayOf(c), { weekday: false })}` : c.title} · SAT Freshman`;
    } catch (e) { return errorView(e); }
    const prefsP = UI.prefs ? UI.prefs().catch(() => ({})) : Promise.resolve({});
    const streakP = S.c.kind === 'daily' ? api('/compete/me').then(m => m.streak).catch(() => null) : Promise.resolve(null);
    const boardP = S.c.status === 'upcoming' ? Promise.resolve(null) : fetchBoard().catch(() => null);
    [S.prefs, S.streak, S.board] = await Promise.all([prefsP, streakP, boardP]);
    render();
  }
  function errorView(e) {
    $('#grid').hidden = true;
    const back = h('a', { class: 'btn', href: '/compete/', text: 'Back to Compete' });
    if (e.status === 404) $('#head').replaceChildren(h('a', { class: 'quiet ct-back', href: '/compete/', text: '‹ Compete' }), h('h1', { class: 'h1', text: 'There’s no contest with that link.' }), h('div', { class: 'row-act' }, back));
    else if (e.status === 403) $('#head').replaceChildren(h('a', { class: 'quiet ct-back', href: '/compete/', text: '‹ Compete' }), h('h1', { class: 'h1', text: 'A private contest' }), h('p', { class: 'line', text: 'Join with the code to take part.' }), h('div', { class: 'row-act' }, quiet('Join with a code', () => C.join())));
    else { $('#head').replaceChildren(); UI.cardError($('#head'), () => { $('#grid').hidden = false; load(); }, 'The server is not answering.'); }
  }
  function joinView(c) {
    $('#grid').hidden = true;
    const go = h('button', { type: 'button', class: 'pill', text: 'Join' });
    go.addEventListener('click', () => busy(go, async () => { const r = await api('/join', { method: 'POST', body: { code } }); location.href = C.href(r.id || c.id); }));
    $('#head').replaceChildren(h('a', { class: 'quiet ct-back', href: '/compete/', text: '‹ Compete' }), h('span', { class: 'k', text: 'PRIVATE CONTEST' }),
      h('h1', { class: 'h1', text: c.title }), h('p', { class: 'meta', text: [c.count && `${c.count} questions`, c.closes && `closes ${C.when(c.closes)}`].filter(Boolean).join(' · ') }),
      h('p', { class: 'line', text: 'Entrants see your board name here (Anonymous if your name is off on Me).' }), h('div', { class: 'row-act' }, go));
  }
  const fetchBoard = () => api(`/contest/${enc(cid)}/board?scope=${S.scope}${S.view === 'series' ? '&view=series&sort=' + (S.sort === 'net' ? 'net' : 'points') : ''}`);

  function render() {
    renderHead();
    renderState();
    renderRules();
    renderEntrants();
    renderOwner();
    if (S.c.kind === 'daily') renderQotd();
    if (S.c.status !== 'upcoming') renderBoard();
    if (finished()) { renderDebrief(); renderTime(); }
    if (S.c.status !== 'upcoming') renderReview();
    if (open()) renderTraps();   // the field's traps would name what you are about to sit
    renderThumb();
    if (P.get('card') === '1') testDayCard();
    if (location.hash && /^#q\d+$/.test(location.hash)) setTimeout(() => openItem(+location.hash.slice(2)), 400);
    else if (location.hash === '#board' || location.hash === '#review') setTimeout(() => { const el = $(location.hash); if (el && !el.hidden) el.scrollIntoView(); }, 300);
  }

  /* ------------------------------------------------------------ header */
  function renderHead() {
    const c = S.c;
    const [kind, name] = titleParts(c);
    const rounds = c.spec && c.spec.repeat && c.spec.repeat.rounds;
    let k = c.kind === 'daily' ? 'DAILY CHALLENGE' : kind.toUpperCase();
    if (c.kind === 'private') k = `PRIVATE CONTEST${c.by ? ` · BY ${String(c.by).toUpperCase()}` : ''}${c.round && rounds ? ` · ROUND ${c.round} OF ${rounds}` : ''}`;
    const title = c.kind === 'daily' ? C.dayLabel(dayOf(c)) : c.kind === 'private' ? c.title : name;
    const chip = h('span', { class: 'chip-s' + (c.status === 'live' ? ' on' : ''), text: { upcoming: 'Upcoming', live: 'Live', closed: 'Closed' }[c.status] || c.status });
    const kids = [h('a', { class: 'quiet ct-back', href: '/compete/', text: '‹ Compete' }), h('span', { class: 'k', text: k }),
      h('div', { class: 'ct-title' }, h('h1', { class: 'h1', text: title }), chip), h('p', { class: 'meta', text: C.windowLine(c) })];
    if (c.kind === 'daily') {
      const day = dayOf(c), today = todayISO();
      const prev = h('a', { class: 'btn sm', href: C.href(`daily-${shiftDay(day, -1)}`), text: `‹ ${C.dayLabel(shiftDay(day, -1), { weekday: false })}` });
      const nextDay = shiftDay(day, 1);
      const next = day >= today ? h('button', { type: 'button', class: 'btn sm', disabled: true, text: `${C.dayLabel(nextDay, { weekday: false })} ›` })
        : h('a', { class: 'btn sm', href: C.href(`daily-${nextDay}`), text: `${C.dayLabel(nextDay, { weekday: false })} ›` });
      const pick = h('input', { class: 'field', type: 'date', value: day, max: today, 'aria-label': 'Pick a day' });
      pick.addEventListener('change', () => { if (pick.value && pick.value <= today) location.href = C.href(`daily-${pick.value}`); });
      kids.push(h('div', { class: 'day-nav' }, prev, pick, next));
      if (S.streak && S.streak.strip) {
        const strip = h('div', { class: 'day-strip', role: 'list', 'aria-label': 'The last 30 days' },
          S.streak.strip.map(x => { const a = h('a', { role: 'listitem', href: C.href(`daily-${x.day}`), 'data-s': x.state === 'made up' ? 'madeup' : x.state, 'aria-current': x.day === day ? 'page' : null,
            'aria-label': `${C.dayLabel(x.day, { weekday: false })}: ${x.state}` }); UI.tooltip(a, `${C.dayLabel(x.day)}: ${x.state}`); return a; }));
        kids.push(strip, h('div', { class: 'day-legend' }, h('span', {}, h('i', { class: 'sat' }), 'sat'), h('span', {}, h('i', { class: 'madeup' }), 'made up'), h('span', {}, h('i', { class: 'ghost' }), 'ghost'), h('span', {}, h('i'), 'missed')));
      }
    }
    $('#head').replaceChildren(...kids);
  }

  /* ------------------------------------------------------------ the state panel */
  function timingNow() {
    const p = S.prefs || {};
    let t = p.contest_timing && p.contest_timing !== 'follow' ? p.contest_timing : p.test_timing || 'official';
    if (!TIMING[t]) t = 'official';
    return t;
  }
  function timingRow(c) {
    const t = timingNow();
    const box = h('div', { class: 'sub-block' });
    const change = h('button', { type: 'button', class: 'quiet', text: 'Change' });
    change.addEventListener('click', () => UI.menu(change, ['official', 'x1.5', 'x2'].map(v => ({ label: TIMING[v], radio: true, checked: v === t,
      onClick: async () => { try { await UI.prefs.set({ contest_timing: v }); S.prefs = { ...S.prefs, contest_timing: v }; renderState(); } catch (e) { UI.toast('Not saved. Try again.'); } } })), { label: 'Contest timing' }));
    const clock = C.kind(c).clock === 'answer' && c.seconds ? ` · ${mmss(Math.round(c.seconds * FACTOR[t]))} answer clock` : C.kind(c).clock === 'wall' ? ` · ${Math.round(c.seconds * FACTOR[t] / 60)} min` : '';
    box.append(h('p', { class: 'line' }, `Your time: ${TIMING[t]}${clock} `, change),
      h('p', { class: 'help', text: c.kind === 'private' ? 'Ranked with everyone in this private contest. Nobody sees your timing.'
        : t === 'official' ? 'Official time: placed on the public board.'
        : 'Extended time: on this board you’re placed among extended-time sittings (only you see where). Rating, Over par and Climb count you with everyone.' }));
    return box;
  }
  function timingSheet(t) {
    return new Promise(resolve => {
      let v = null;
      const s = UI.sheet({ title: `${TIMING[t]} time in contests`, size: 's',
        body: b => b.append(h('p', { class: 'line', text: `You have ${TIMING[t]} time set for tests. In contests, extended sittings are placed apart on Points, Season and contest boards, shown only to you, and counted with everyone on Rating, Over par and Climb.` })),
        actions: [{ label: `Use ${TIMING[t]}`, primary: true, onClick: () => { v = 'keep'; } }, { label: 'Use official time for contests', quiet: true, onClick: () => { v = 'official'; } }] });
      s.closed.then(async () => {
        if (!v) return resolve(false);
        try { await UI.prefs.set(v === 'official' ? { contest_timing: 'official', contest_timing_seen: true } : { contest_timing_seen: true }); } catch (_) {}
        S.prefs = { ...S.prefs, contest_timing_seen: true, ...(v === 'official' ? { contest_timing: 'official' } : {}) };
        resolve(true);
      });
    });
  }
  async function doStart(btn) {
    const c = S.c, t = timingNow();
    if (t !== 'official' && c.kind !== 'private' && !(S.prefs || {}).contest_timing_seen && c.me.status === 'new') { if (!(await timingSheet(t))) return; }
    const sel = $('#race-sel');
    await busy(btn, () => C.start(c.id, { race: sel ? sel.value : race, kind: c.kind, domain: ($('#rush-dom') || {}).value }));
  }
  function raceRow(c) {
    const box = h('div', { class: 'sub-block' });
    const sel = h('select', { class: 'field', id: 'race-sel', 'aria-label': 'Race' });
    const opts = [['', 'No one'], ['best', 'Your best'], ['pace', 'SAT pace'], ['median', 'Field median'], ['par:3', 'Level 3 par'], ['par:5', 'Level 5 par'], ['par:7', 'Level 7 par']];
    if (race && !opts.some(o => o[0] === race)) opts.push([race, (c.race && c.race.label) || 'The link’s sender']);
    (S.rivals || []).forEach(r => { if (!opts.some(o => o[0] === r.pid)) opts.push([r.pid, `${r.name} (rival)`]); });
    opts.forEach(([v, l]) => sel.append(h('option', { value: v, text: l, selected: v === race ? true : null })));
    if (!race && ['sprint', 'rush'].includes(c.kind)) sel.value = 'best';
    sel.addEventListener('change', () => { race = sel.value; history.replaceState(null, '', C.href(c.id, { race })); load(); });
    box.append(h('div', { class: 'race-row' }, h('label', { class: 'label', for: 'race-sel', text: 'Race', style: 'margin:0' }), sel));
    if (c.race) box.append(h('p', { class: 'line mono', text: `Race ${c.race.label}${c.race.right !== undefined ? ` · ${num(c.race.right)}/${num(c.count)}` : ''}${c.race.points !== undefined ? ` · ${num(c.race.points)} pts` : ''}${c.race.secs ? ` · ${mmss(c.race.secs)}` : ''}` }));
    box.append(h('p', { class: 'help', text: 'Racing never changes your rank: the pacer runs on your answer clock, and shows only where it was, never its answers.' }));
    return box;
  }
  function renderState() {
    const c = S.c, me = c.me || {}, el = $('#state');
    const kids = [];
    if (me.status === 'finished') { renderResult(el); return; }
    if (c.status === 'upcoming') {
      const cd = h('span', { class: 'ct-count' });
      kids.push(h('span', { class: 'k', text: 'OPENS IN' }), cd);
      UI.countdown(cd, c.opens, { label: 'Opens in', onEnd: () => load() });
    }
    if (me.status === 'progress') {
      const go = h('button', { type: 'button', class: 'pill', text: 'Resume' });
      go.addEventListener('click', () => busy(go, () => C.start(c.id)));
      kids.push(h('div', { class: 'row-act' }, go, h('span', { class: 'meta', text: `${num(me.answered)} of ${num(c.count)} answered${me.clock && me.clock.left !== undefined ? ` · ${mmss(me.clock.left)} on the clock` : ''}` })));
      el.replaceChildren(...kids);
      return;
    }
    if ((c.ladder || []).length) { const lad = h('div', { class: 'sub-block' }); C.ladder(lad, c); kids.push(lad); }
    if (c.kind === 'final') kids.push(h('p', { class: 'meta', text: 'Module 2 · 22 questions · easier or harder by your module 1' }));
    if (c.kind === 'trap') {
      const tb = h('div', { class: 'sub-block' });
      kids.push(tb);
      trapOf(c).then(t => {
        if (!t) { tb.remove(); return; }
        const skills = new Set((c.ladder || []).map(q => q.topic)).size;
        tb.append(h('span', { class: 'k', text: 'TRAP OF THE WEEK' }), h('p', { class: 'line', text: t.name }), t.tell ? h('p', { class: 'line' }, h('i', { text: t.tell })) : '',
          h('p', { class: 'meta', text: [t.field_share ? `caught ${pct(t.field_share)} of the field this week` : null, `${num(c.count)} questions in ${num(skills)} skills, each with this trap in it`].filter(Boolean).join(' · ') }));
      });
    }
    const lines = h('div', { class: 'daily-lines' });
    lines.append(h('p', { class: 'line', text: C.facts({ ...c, field: null }) }));
    if (c.status !== 'upcoming') lines.append(C.fieldLine(c, 'in'));
    const par = C.parLine(c); if (par) lines.append(par);
    kids.push(lines);
    if (['weekly', 'final'].includes(c.kind)) kids.push(h('p', { class: 'help', text: `Runs in the test window: move between questions, mark for review, hand in when ready. Answers and explanations appear at hand-in.${c.kind === 'final' ? ' No pace guide: test conditions.' : ''}` }));
    if (c.kind === 'rush') {
      const dom = h('select', { class: 'field', id: 'rush-dom', 'aria-label': 'Domain' }, [['all', 'All domains'], ...(UI.DOMAINS || []).map(([d, s]) => [d, s])].map(([v, l]) => h('option', { value: v, text: l })));
      kids.push(h('div', { class: 'race-row sub-block' }, h('label', { class: 'label', for: 'rush-dom', text: 'Domain', style: 'margin:0' }), dom));
    }
    const closedGhost = c.status === 'closed';
    if (c.status === 'live' && !['weekly', 'final'].includes(c.kind)) kids.push(raceRow(c));
    if (c.status !== 'upcoming' && !closedGhost) kids.push(timingRow(c));
    const act = h('div', { class: 'row-act' });
    if (c.status === 'upcoming') {
      act.append(h('button', { type: 'button', class: 'pill', text: 'Add to calendar', onclick: () => UI.ics({ title: `SAT Freshman · ${c.title}`, start: new Date(c.opens), minutes: 30, url: `${location.origin}${C.href(c.id)}` }) }));
    } else if (closedGhost) {
      const go = h('button', { type: 'button', class: 'pill', text: 'Sit it now (unranked)' });
      go.addEventListener('click', () => busy(go, () => C.start(c.id, { kind: c.kind })));
      act.append(go);
    } else {
      const go = h('button', { type: 'button', class: 'pill', id: 'start', text: c.kind === 'daily' ? 'Start the challenge' : 'Start' });
      go.addEventListener('click', () => doStart(go));
      act.append(go);
    }
    if (me.status === 'new' && c.status !== 'closed' && ['daily', 'weekly', 'final', 'trap', 'private'].includes(c.kind) && (c.ladder || []).length) {
      const low = [...c.ladder].sort((a, b) => (a.chance ?? 1) - (b.chance ?? 1)).slice(0, 3).map(q => C.topicName(q.topic));
      const warm = quiet('Warm up · 6', ev => busy(ev.currentTarget, async () => runner(await api(`/contest/${enc(c.id)}/warmup`, { method: 'POST', body: {} }))));
      UI.tooltip(warm, `Two questions each on ${[...new Set(low)].join(' · ')}, from other question types, key after each.`);
      act.append(warm);
    }
    kids.push(act);
    if (closedGhost) {
      kids.push(h('p', { class: 'help', text: 'Twin questions, same skills. You’ll see where you would have placed. It doesn’t count for rank, rating or season points.' }));
      if (c.kind === 'daily' && dayOf(c) >= shiftDay(todayISO(), -2) && S.streak && (S.streak.strip || []).some(x => x.day === dayOf(c) && x.state === 'missed')) {
        const leftH = Math.max(0, Math.round((new Date(`${shiftDay(dayOf(c), 3)}T00:00:00`) - Date.now()) / 36e5));
        kids.push(h('p', { class: 'line', text: `Make up ${C.dayLabel(dayOf(c), { weekday: false })} · keeps your streak · ${leftH >= 24 ? `${Math.floor(leftH / 24)} day${leftH >= 48 ? 's' : ''}` : `${leftH}h`} left` }));
      }
    } else if (c.status === 'live') kids.push(h('p', { class: 'help', text: C.kind(c).clock === 'answer' ? 'The clock runs only while a question is open. Skipped and voided questions score 0.' : 'A wall clock, like the real test.' }));
    el.replaceChildren(...kids);
    if (c.status === 'live' && !S.rivals) api('/compete/rivals').then(r => { S.rivals = (r.rivals || []).slice(0, 5); if (S.c.me.status === 'new') renderState(); }).catch(() => { S.rivals = []; });
  }

  async function trapOf(c) {
    if (!S.trapIdx) { try { S.trapIdx = await api('/compete/traps-index'); } catch (_) { S.trapIdx = []; } }
    const name = String(c.title || '').split(' · ').slice(1).join(' · ');
    return (S.trapIdx || []).find(x => x.name === name || (c.spec && c.spec.family && x.family === c.spec.family)) || null;
  }

  /* ------------------------------------------------------------ the result panel */
  function renderResult(el) {
    const c = S.c, me = c.me, r = me.result || {};
    const you = S.board && S.board.you;
    const players = (S.board && S.board.players) || (c.field && c.field.players) || 0;
    const kids = [];
    const rank = h('div', { class: 'big-rank' });
    if (me.why === 'ghost') rank.append(h('span', { class: 'line', text: r.would_be ? `Would have placed #${r.would_be} of ${num(players)}` : 'A ghost sitting: not ranked' }));
    else if (you && you.extended) rank.append(h('span', { class: 'num', text: `#${you.extended.rank}` }), h('span', { class: 'of', text: `of ${num(you.extended.of)} with extended time` }));
    else if (you && you.rank && me.ranked !== false) {
      rank.append(h('span', { class: 'num', text: `${you.tie ? '=' : ''}#${you.rank}` }), h('span', { class: 'of', text: `of ${num(players)}` }));
      if (players >= 10) rank.append(h('span', { class: 'chip-s', text: `Top ${Math.ceil(you.rank / players * 100)}%` }));
    }
    kids.push(rank);
    const band = r.band || r.estimate || null;
    const bandTxt = band && (band.low ?? band[0]) !== undefined ? `${band.low ?? band[0]}–${band.high ?? band[1]}` : null;
    if (c.kind === 'final' && bandTxt) {
      const route = { hard: 'harder', harder: 'harder', easy: 'easier', easier: 'easier' }[r.route] || r.route;
      kids.push(h('div', { class: 'final-band' }, h('span', { class: 'k', text: 'SECTION ESTIMATE' }), h('span', { class: 'num', text: bandTxt }),
        route ? h('span', { class: 'line', text: `Route: ${route} module 2` }) : '',
        r.route_kept || me.route_kept ? h('span', { class: 'meta', text: 'Route kept: decided before confirms' }) : ''));
    }
    if (c.kind === 'weekly' && bandTxt) kids.push(h('p', { class: 'line', text: `Module estimate ${bandTxt}` }));
    if (c.kind === 'sprint' && you && you.points !== undefined) kids.push(h('p', { class: 'line', text: `Best this week ${num(you.points)} pts${you.runs ? ` · ${num(you.runs)} run${you.runs === 1 ? '' : 's'}` : ''}. Every run draws fresh questions; only your best counts.` }));
    if (me.ranked === false && me.why !== 'ghost') kids.push(h('p', { class: 'line' }, h('span', { class: 'chip-s', text: 'Unranked' }), ' ', WHY[me.why] || ''));
    const parts = r.points_parts || {};
    const par = r.par || {};
    const tiles = h('div', { class: 'stats res-tiles' },
      stat('Score', `${num(r.right)}/${num(r.asked || c.count)}`),
      stat('Points', num(r.points), parts.base !== undefined ? `${num(parts.base)} + ${num(parts.pace || 0)} pace + ${num(parts.finish || 0)} finish` : null),
      stat(C.kind(c).clock === 'wall' ? 'Time used' : 'Answer time', me.clock ? mmss(me.clock.used) : r.secs !== undefined ? mmss(r.secs) : null),
      r.net !== undefined && par.base !== undefined ? stat('Par', `${r.net >= 0 ? '+' : '−'}${num(Math.abs(r.net))}`, `${r.net >= 0 ? 'over' : 'under'} par · base ${num(parts.base)} vs par ${num(par.base)}`) : null,
      r.rating_after !== undefined && r.rating_before !== undefined ? stat('Contest rating', `${r.rating_after >= r.rating_before ? '+' : '−'}${num(Math.abs(Math.round(r.rating_after - r.rating_before)))} → ${num(Math.round(r.rating_after))}`,
        C.levelOf(r.rating_after) !== C.levelOf(r.rating_before) ? `Level ${C.levelOf(r.rating_before)} → ${C.levelOf(r.rating_after)}` : `Level ${C.levelOf(r.rating_after)}`) : null);
    [...tiles.children].forEach(t => { if (!t) tiles.removeChild(t); });
    kids.push(tiles);
    const right = r.right || 0, wrong = r.wrong ?? Math.max(0, (r.asked || 0) - right - (r.skipped || 0) - (r.voided || 0));
    const brk = h('p', { class: 'line res-brk', text: `${num(right)} right${r.confirmed ? ` (${num(r.confirmed)} confirmed)` : ''} · ${num(wrong)} wrong · ${num(r.skipped || 0)} skipped · ${num(r.voided || 0)} voided` });
    if (you && you.mark === 'clean') brk.append(' ', h('span', { class: 'chip-s', text: 'Clean run' }));
    kids.push(brk);
    if (r.race) { const who = r.race.label || r.race.them_label || 'the pacer'; kids.push(h('p', { class: 'line', text: r.race.won ? `Beat ${who} by ${num(Math.abs((r.race.you || 0) - (r.race.them || 0)))} pts` : `${who.replace(/^./, x => x.toUpperCase())} by ${num(Math.abs((r.race.them || 0) - (r.race.you || 0)))} pts` })); }
    const pars = ((S.board && S.board.pars) || []).slice().sort((a, b) => a.points - b.points);
    if (pars.length && r.points !== undefined && ['daily', 'weekly', 'final', 'trap', 'private'].includes(c.kind)) {
      const below = pars.filter(p => p.points <= r.points).pop(), above = pars.find(p => p.points > r.points);
      kids.push(h('p', { class: 'meta', text: below && above ? `Between Level ${below.level} and Level ${above.level} par` : below ? `Above Level ${below.level} par` : `Below Level ${above.level} par` }));
    }
    if (c.status === 'live' && c.kind !== 'private' && me.why !== 'ghost') { const rl = h('p', { class: 'line', hidden: true }); kids.push(rl); rivalsToday(rl, r.points); }
    if (r.trap) {
      const caught = (r.questions || []).filter(q => q.status === 'incorrect' && q.mistake).map(q => `Q${q.n} (${C.topicName(q.topic)})`);
      const tl = h('div', { class: 'sub-block' }, h('p', { class: 'line', text: [`Resisted ${num(r.trap.resisted)} of ${num(r.trap.chances)}`,
        r.trap.field_mean !== null && r.trap.field_mean !== undefined ? `field ${r.trap.field_mean}` : null, caught.length ? `caught on ${caught.join(' and ')}` : null].filter(Boolean).join(' · ') }));
      const act0 = h('div', { class: 'row-act' }, quiet('Drill this habit · 8', ev => busy(ev.currentTarget, () => drill({ habit: r.trap.family, count: 8, source: 'habit' }))));
      tl.append(act0);
      trapOf(c).then(t => { if (t && t.tell) tl.insertBefore(h('p', { class: 'line' }, h('i', { text: t.tell })), act0); });
      kids.push(tl);
    }
    if (c.kind === 'rush') {
      const top = r.top_item === true || r.top_item === 'top' ? 'the top of the bank' : r.top_item ? `L${r.top_item} items` : null;
      kids.push(h('p', { class: 'line', text: [`${num(r.right || 0)} right`, top ? `reached ${top}` : null, you && you.right !== undefined ? `best this week ${num(you.right)}` : null].filter(Boolean).join(' · ') }));
      const st = (Array.isArray(r.strikes) ? r.strikes : []).filter(x => x && typeof x === 'object');
      const tpl = [...new Set(st.map(x => x.template).filter(Boolean))];
      if (st.length) kids.push(h('div', { class: 'row-act' }, h('span', { class: 'line', text: `Your ${st.length} strike${st.length === 1 ? '' : 's'}: ${st.map(x => x.label || x.reason || 'slow').join(' · ')}` }),
        tpl.length ? quiet(`Practice these ${tpl.length}`, ev => busy(ev.currentTarget, () => drill({ templates: tpl, count: Math.min(10, tpl.length * 2), source: 'result' }))) : ''));
    }
    if (c.kind === 'words') {
      kids.push(h('p', { class: 'line', text: [`Score ${Number(r.score ?? 0).toFixed(1)}`, `${num(r.right || 0)} right`, `${num(r.wrong || 0)} wrong`, you && you.score !== undefined ? `best this week ${Number(you.score).toFixed(1)}` : null].filter(Boolean).join(' · ') }));
      if ((r.traps || []).length) kids.push(h('p', { class: 'line', text: `Traps: ${r.traps.map(t => `${t.n} × ${t.label || t.trap}`).join(' · ')}` }));
    }
    if ((r.records_new || []).length) kids.push(h('div', { class: 'row-act' }, r.records_new.map(x => h('span', { class: 'chip-s on', html: `${C.svg(C.SVG.star, 14)} ` }, `New best ${x.kind === 'daily' ? 'Daily' : x.kind} · ${num(x.value)}${x.was !== null && x.was !== undefined ? ` (was ${num(x.was)})` : ''}`))));
    const fu = me.followup || {};
    if (fu.won_back !== null && fu.won_back !== undefined && fu.of) kids.push(h('p', { class: 'line', text: `Won back ${num(fu.won_back)} of ${num(fu.of)}${fu.due ? ` · ${C.dayLabel(fu.due)}` : ''}` }));
    else if (fu.due) kids.push(h('p', { class: 'line' }, h('span', { class: 'chip-s on', text: `Rematch · ${C.dayLabel(fu.due)}` })));
    // the answer strip: each square jumps to its review item
    const strip = h('div', { class: 'sub-block' });
    UI.strip(strip, C.marks(r), { onPick: i => openItem(i + 1), label: 'Your answers' });
    kids.push(strip);
    // the practice summary's study value, kept
    const topics = r.topics || [];
    if (topics.length) {
      kids.push(h('div', { class: 'sub-block' }, h('span', { class: 'k', text: 'SKILLS IN THIS SITTING' }), h('div', { class: 'topic-rows' }, topics.map(t => h('div', { class: 'topic-row' },
        h('span', { class: 'line', text: C.topicName(t.topic) }), h('span', { class: 'meta', text: `${num(t.right)}/${num(t.asked)}` }),
        h('span', { class: 'mbar', role: 'img', 'aria-label': `Mastery ${Math.round((t.before || 0) * 100)}% → ${Math.round((t.after || 0) * 100)}%` },
          h('i', { style: `width:${Math.round((t.after || 0) * 100)}%` }), h('b', { style: `left:${Math.round((t.before || 0) * 100)}%` })))))));
    }
    if ((r.opened || []).length || (r.closed || []).length) {
      kids.push(h('div', { class: 'sub-block' }, h('span', { class: 'k', text: 'MISTAKES' }), h('ul', { class: 'mist' },
        (r.opened || []).map(m => h('li', {}, h('a', { class: 'link', href: `/review/?open=trap:${m.id}`, text: m.label }))),
        (r.closed || []).map(m => h('li', { class: 'closed', text: m.label })))));
    }
    // the name prompt: once, while the board shows a default handle
    if (you && /^Student [0-9A-F]{4}$/i.test(you.name || '')) kids.push(namePrompt(you.name));
    // actions
    const act = h('div', { class: 'row-act' });
    act.append(h('button', { type: 'button', class: 'pill', text: 'See the board', onclick: () => $('#board').scrollIntoView({ behavior: 'smooth' }) }));
    if (['sprint', 'rush'].includes(c.kind)) {
      const again = h('button', { type: 'button', class: 'btn', text: c.kind === 'rush' ? 'Run again' : 'Run again' });
      again.addEventListener('click', () => busy(again, () => C.start(c.id, { kind: c.kind })));
      act.append(again, quiet(`Race your best${r.points !== undefined ? ` · ${num(r.points)}` : ''}`, ev => busy(ev.currentTarget, () => C.start(c.id, { race: 'best', kind: c.kind }))));
    }
    const fieldTraps = quiet('Practice the field’s traps', ev => busy(ev.currentTarget, practiceTraps));
    const copy = quiet('Copy result', () => UI.copyText(C.copyResult(c, { ...r, secs: me.clock ? me.clock.used : r.secs }, { rank: you && you.rank, players }, myPid())));
    const link = quiet('Race link', () => UI.copyText(`${location.origin}${C.href(c.id, { race: myPid() })}`));
    const friend = quiet('Challenge a friend', () => C.create({ count: [5, 10, 15, 22].includes(c.count) ? c.count : 10, topics: [...new Set((c.ladder || []).map(q => q.topic))], twin: true, sheetTitle: 'Challenge a friend' }));
    act.append(...[fieldTraps, copy, myPid() && link, (c.kind === 'daily' || c.kind === 'private') && friend].filter(Boolean));
    kids.push(act);
    if (c.kind === 'final') {
      kids.push(h('div', { class: 'row-act' }, quiet('Test-day card', null, { href: `${C.href(c.id)}&card=1` })));
      finalFocus(kids);
    }
    el.replaceChildren(...kids.filter(Boolean));
    requestAnimationFrame(() => { if (!sessionReveal()) return; el.querySelectorAll('.big-rank, .res-tiles').forEach(x => x.animate([{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], { duration: 320, easing: 'cubic-bezier(.23,1,.32,1)' })); });
  }
  // "Rivals today: beat Maya · lost to Sam · Lee hasn't sat yet" (C9)
  // ponytail: reads the board's first page; a rival placed below #50 reads "hasn't sat yet" until the board returns rival rows
  async function rivalsToday(el, mine) {
    try {
      if (!S.rivals) S.rivals = ((await api('/compete/rivals')).rivals || []).slice(0, 5);
      const list = S.rivals.slice(0, 3);
      if (!list.length || mine === undefined) return;
      const entries = (S.board && S.board.entries) || [];
      el.textContent = `Rivals today: ${list.map(x => { const e = entries.find(y => y.pid === x.pid); return !e ? `${x.name} hasn’t sat yet` : e.points > mine ? `lost to ${x.name}` : e.points < mine ? `beat ${x.name}` : `level with ${x.name}`; }).join(' · ')}`;
      el.hidden = false;
    } catch (_) {}
  }
  // the rank reveal plays once per sitting (C21), never with reduced motion
  function sessionReveal() {
    if ((UI.reduced && UI.reduced()) || matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
    const k = `satf.revealed.${S.c.me.session}`;
    try { if (localStorage.getItem(k)) return false; localStorage.setItem(k, '1'); } catch (_) { return false; }
    return true;
  }
  function namePrompt(handle) {
    const f = h('input', { class: 'field', id: 'bname', maxlength: '24', autocomplete: 'off', placeholder: 'A board name' });
    const msg = h('p', { class: 'help', role: 'status', text: 'Shown on public boards. Don’t use your full name.' });
    const save = h('button', { type: 'button', class: 'btn', text: 'Save' });
    save.addEventListener('click', () => busy(save, async () => {
      const v = f.value.trim();
      if (!/^[A-Za-z0-9 _.\-]{3,24}$/.test(v)) { msg.textContent = '3 to 24 letters, digits, spaces or _ . -'; return; }
      try { await api('/me', { method: 'PUT', body: { handle: v } }); UI.toast('Saved'); S.board = await fetchBoard(); renderBoard(); renderState(); }
      catch (e) { msg.textContent = e.status === 409 ? 'Someone already has that name.' : e.status === 422 ? 'That name is reserved.' : 'Not saved. Try again.'; }
    }));
    f.addEventListener('keydown', e => { if (e.key === 'Enter') save.click(); });
    return h('div', { class: 'sub-block' }, h('label', { class: 'label', for: 'bname', text: `On the board as ${handle}` }), h('div', { class: 'name-form' }, f, save), msg);
  }
  async function practiceTraps() {
    if (!S.review) await loadReviewData();
    const items = (S.review && S.review.items) || [];
    const tr = S.traps || [];
    const want = new Set(tr.map(t => t.norm));
    let keys = items.filter(it => ((it.field && it.field.mistakes) || []).some(m => want.has(m.norm))).map(it => it.question.key);
    if (!keys.length) keys = [...items].sort((a, b) => ((a.field || {}).right ?? 1) - ((b.field || {}).right ?? 1)).slice(0, 5).map(it => it.question.key);
    keys = [...new Set(keys)].slice(0, 5);
    if (!keys.length) { UI.toast('The field’s traps open after the contest closes.'); return; }
    await drill({ templates: keys, count: Math.min(10, keys.length * 2), source: 'result' });
  }
  async function finalFocus(kids) {
    const box = h('div', { class: 'sub-block' });
    kids.push(box);
    try {
      const f = await api('/compete/final-focus');
      if (!f) return;
      box.append(h('span', { class: 'k', text: f.mode === 'last_week' ? 'YOUR LAST WEEK' : 'FINAL FOCUS' }));
      const labels = f.trap_norms || [], ids = f.traps || [];
      if (labels.length) box.append(h('p', { class: 'line', text: `${labels.length} trap${labels.length === 1 ? '' : 's'} to fix` }), h('ul', { class: 'mini-rows' }, labels.map((l, i) => h('li', {}, h('span', { class: 'mt', text: l }),
        ids[i] ? h('span', { class: 'ma' }, quiet('Fix it · 3', ev => busy(ev.currentTarget, () => drill({ pool: 'redo', ids: [ids[i]], each: 3, source: 'twin' })))) : ''))));
      if ((f.skip_first || []).length) box.append(h('p', { class: 'line', text: `Skip first on test day: ${f.skip_first.map(C.topicName).join(', ')}` }));
      if (f.mode !== 'last_week') box.append(h('p', { class: 'help', text: f.exam_date ? `Your SAT is ${C.dayLabel(f.exam_date, { weekday: false })}. These lead your final week when it starts.` : 'Set your SAT date and these lead your final week.' }));
      if (!f.exam_date && UI.examDate) box.append(h('div', { class: 'row-act' }, quiet('Set date', ev => UI.examDate(ev.currentTarget, { onSave: async v => { await UI.prefs.set({ exam_date: v }); UI.toast('Saved'); render(); } }))));
    } catch (_) { box.remove(); }
  }
  async function testDayCard() {
    try {
      const d = await api(`/contest/${enc(cid)}/card`);
      document.body.classList.add('print-card');
      $('#grid').hidden = true;
      $('#head').replaceChildren(h('a', { class: 'quiet ct-back no-print', href: C.href(cid), text: '‹ Back to the result' }),
        h('section', { class: 'card card-print' }, h('span', { class: 'k', text: 'TEST-DAY CARD' }),
          h('h1', { class: 'h1', text: `SAT · ${C.dayLabel(d.date)}` }),
          h('p', { class: 'line', text: `Move on at 2× the budget and come back: easy ${d.pace.easy} · medium ${d.pace.medium} · hard ${d.pace.hard}` }),
          (d.skip_first || []).length ? h('p', { class: 'line', text: `Skip first: ${d.skip_first.map(C.topicName).join(', ')}` }) : null,
          (d.traps || []).length ? h('div', {}, h('span', { class: 'k', text: 'WATCH FOR' }), h('ul', { class: 'mist' }, d.traps.map(t => h('li', { text: t })))) : null,
          d.band ? h('p', { class: 'line', text: `Season Final: ${d.band.low ?? d.band[0]}–${d.band.high ?? d.band[1]}${d.route ? ` · ${d.route} module 2` : ''}` }) : null,
          h('p', { class: 'line', text: d.doors }),
          h('div', { class: 'row-act no-print' }, h('button', { type: 'button', class: 'pill', text: 'Print', onclick: () => print() }))));
    } catch (e) { UI.toast(e.status === 403 ? 'Finish your Final first.' : 'Couldn’t load the card.'); }
  }

  /* ------------------------------------------------------------ the debrief and the time block */
  async function renderDebrief() {
    const el = show('#debrief');
    UI.skel(el, 'card:3');
    try {
      const d = await api(`/contest/${enc(cid)}/debrief`);
      el.replaceChildren();
      UI.debrief(el, d, {
        onFilter: (qids, label) => setFilter('sel', { qids, label }),
        onFix: (row, label) => fix(row, label),
        onRematch: async when => {
          const r = await api(`/contest/${enc(cid)}/rematch`, { method: 'POST', body: { when } });
          if (r.session) runner(r);
          else if (r.due) { UI.toast(`Rematch set for ${C.dayLabel(r.due)}`); S.c.me.followup = { ...(S.c.me.followup || {}), due: r.due }; renderState(); }
        },
      });
    } catch (e) { if (e.status === 403) el.hidden = true; else { el.replaceChildren(); UI.cardError(el, renderDebrief); } }
  }
  function fix(row, label) {
    const sid = S.c.me.session;
    if (/^Speed/.test(label)) return drill({ templates: [row.template], count: 8, timed: true, source: 'result' }).catch(e => UI.toast(e.message));
    const body = { from_session: sid, only: [row.qid], each: /^Try/.test(label) ? 1 : 3, source: 'twin', parent: sid };
    if (row.norm) body.want = { template: row.norm };
    if (UI.twinSheet) return UI.twinSheet({ body, title: /^Try/.test(label) ? 'Try it now' : 'Fix it', recall: row.label });
    return drill(body).catch(e => UI.toast(e.message));
  }
  function renderTime() {
    const r = S.c.me.result || {}, qs = r.questions || [];
    if (!qs.length || C.kind(S.c).clock === 'wall' && qs.every(q => !q.ms)) return;
    const el = show('#time');
    const max = Math.max(...qs.map(q => Math.max(q.ms || 0, q.budget_ms || 0)), 1);
    const sinks = qs.filter(q => q.ms && q.budget_ms && q.ms > 2 * q.budget_ms);
    const rows = h('div', { class: 'time-rows' }, qs.map(q => h('div', { class: 'time-row' },
      h('span', { text: `Q${q.n}` }),
      h('span', { class: 'tb', role: 'img', 'aria-label': `Q${q.n}: ${mmss((q.ms || 0) / 1000)} against a budget of ${mmss((q.budget_ms || 0) / 1000)}, ${STATUS_WORD[q.status] || q.status}` },
        h('i', { class: q.status === 'correct' ? 'right' : null, style: `width:${Math.round((q.ms || 0) / max * 100)}%` }),
        q.budget_ms ? h('b', { style: `left:${Math.round(q.budget_ms / max * 100)}%` }) : null),
      h('span', { class: 'n', text: `${mmss((q.ms || 0) / 1000)} ${STATUS[q.status] || ''}` }))));
    const kids = [head2('time-h', 'Time', h('span', { class: 'meta', text: 'bar: your time · tick: its budget' })), rows];
    if (sinks.length) {
      const spent = sinks.reduce((s, q) => s + q.ms, 0), budget = sinks.reduce((s, q) => s + q.budget_ms, 0);
      kids.push(h('p', { class: 'line', text: `Time sinks · ${sinks.length}: ${mmss(spent / 1000)} on ${sinks.length} question${sinks.length === 1 ? '' : 's'}${sinks.every(q => q.status !== 'correct') ? ', all wrong' : ''}. Moving on at the budget would have left ${mmss((spent - budget) / 1000)}.` }));
    }
    const easy = qs.filter(q => q.difficulty === 'easy' && q.ms);
    if (easy.length) {
      const med = easy.map(q => q.ms).sort((a, b) => a - b)[Math.floor(easy.length / 2)];
      const banked = easy.reduce((s, q) => s + Math.max(0, (q.budget_ms || 0) - q.ms), 0);
      if (banked > 0) kids.push(h('p', { class: 'meta', text: `Banked: easy median ${mmss(med / 1000)} against ${mmss((easy[0].budget_ms || 65000) / 1000)} · ${mmss(banked / 1000)} banked for the hard ones` }));
    }
    el.replaceChildren(...kids);
  }

  /* ------------------------------------------------------------ the board */
  function columns(c) {
    const pts = e => num(e.points), time = e => (e.secs !== undefined && e.secs !== null ? mmss(e.secs) : null);
    const score = e => (e.right !== undefined && e.asked ? `${num(e.right)}/${num(e.asked)}` : null);
    const net = e => (e.net === undefined || e.net === null ? null : `${e.net > 0 ? '+' : e.net < 0 ? '−' : ''}${num(Math.abs(e.net))}`);
    const move = e => (e.move ? `${e.move > 0 ? '▲' : '▼'}${Math.abs(e.move)}` : e.move === 0 ? '–' : null);
    const you = S.board && S.board.you;
    const gap = e => (!you || e.you || e.par || you.points === undefined || e.points === undefined ? null : `${e.points - you.points >= 0 ? '+' : '−'}${num(Math.abs(e.points - you.points))}`);
    const M = { label: 'Move', value: move, title: 'Places since yesterday' }, G = { label: 'Gap', value: gap, title: 'Their points minus yours' };
    if (S.view === 'series') return [{ label: 'Rounds sat', value: e => e.rounds ?? e.sat }, { label: 'Points', value: pts, phone: true }, { label: 'Over par', value: net }, M];
    if (c.kind === 'sprint') return [{ label: 'Best points', value: pts, phone: true }, { label: 'Right/answered', value: score }, { label: 'Runs', value: e => e.runs }, M];
    if (c.kind === 'rush') return [{ label: 'Right', value: e => num(e.right), phone: true }, { label: 'Top item', value: e => e.top_item ? (e.top === true ? 'Top' : `L${e.top_item}`) : null }, { label: 'Runs', value: e => e.runs }, M];
    if (c.kind === 'words') return [{ label: 'Score', value: e => (e.score !== undefined ? Number(e.score).toFixed(1) : null), phone: true }, { label: 'Right', value: e => e.right }, { label: 'Wrong', value: e => e.wrong }, { label: 'Runs', value: e => e.runs }, M];
    const list = [{ label: 'Score', value: score }];
    if (c.kind === 'trap') list.push({ label: 'Resisted', value: e => e.resisted });
    if (c.kind === 'final') list.push({ label: 'Band', value: e => (e.band ? `${e.band.low ?? e.band[0]}–${e.band.high ?? e.band[1]}` : null) });
    list.push({ label: 'Points', value: pts, phone: true, par: true }, { label: 'Over par', value: net, title: 'Base points minus the player’s par' },
      { label: 'Time', value: time, title: C.kind(c).clock === 'wall' ? 'Time used, start to hand-in' : 'Answer clock used: only while a question was open' }, M, G);
    return list;
  }
  function parsOn() { try { return localStorage.getItem('satf.pars') !== 'off'; } catch (_) { return true; } }
  function sorted(b) {
    if (S.sort !== 'net' || S.view === 'series') return b;
    const es = [...(b.entries || [])].sort((x, y) => (y.net ?? -1e9) - (x.net ?? -1e9));
    let last = null, rank = 0;
    es.forEach((e, i) => { if (e.net !== last) { rank = i + 1; last = e.net; } e = Object.assign(e, { rank, tie: es.filter(x => x.net === e.net).length > 1 }); });
    const you = b.you ? es.find(e => e.you) || b.you : null;
    return { ...b, entries: es, you };
  }
  function youText(you) {
    const c = S.c;
    if (you.extended) return `You · #${you.extended.rank} of ${num(you.extended.of)} with extended time`;
    if (!you.rank) return 'Finish this contest to see where you stand.';
    const val = S.sort === 'net' ? you.net : you.points;
    const unit = S.sort === 'net' ? 'over par' : 'pts';
    const toPass = you.cheapest || (you.gap ? you.gap + 1 : null);
    return [`You · #${you.rank}`, `${num(val)} ${unit}`, you.anon ? 'shown as Anonymous' : null, toPass && you.rank > 1 ? `${num(toPass)} to pass #${you.rank - 1}` : null,
      toPass && you.rank > 1 && c.status === 'live' ? C.step(toPass, S.sort === 'net' ? 'net' : 'points', !!C.kind(c).pace) : null].filter(Boolean).join(' · ');
  }
  function rowMenu(e) {
    const c = S.c, items = [];
    if (finished()) items.push({ label: 'Compare', onClick: () => compare(e) });
    if (finished() || c.status === 'closed') items.push({ label: 'Race', href: C.href(c.id, { race: e.pid }) });
    const on = S.follow.has(e.pid);
    items.push({ label: on ? 'Unfollow' : 'Follow', onClick: () => follow(e) });
    items.push({ separator: true }, { label: 'Report name', onClick: () => reportName(e) });
    return items;
  }
  async function follow(e) {
    const on = S.follow.has(e.pid);
    try {
      if (on) { await api(`/follows/${enc(e.pid)}`, { method: 'DELETE' }); S.follow.delete(e.pid); UI.toast(`Unfollowed ${e.name}`); }
      else { await api('/follows', { method: 'POST', body: { pid: e.pid } }); S.follow.add(e.pid); UI.toast(`Following ${e.name}`); }
    } catch (err) { UI.toast(err.status === 403 ? 'This student is private.' : err.status === 409 ? 'You follow 50 students already.' : 'Not saved. Try again.'); }
  }
  async function reportName(e) {
    const ok = await UI.confirm({ title: `Report the name “${e.name}”?`, text: 'After 3 reports from different ranked players, the name resets to its default handle.', confirm: 'Report' });
    if (!ok) return;
    try { await api('/report-name', { method: 'POST', body: { pid: e.pid } }); UI.toast('Reported'); } catch (err) { UI.toast(err.message || 'Not sent. Try again.'); }
  }
  async function compare(e) {
    const body = h('div', {}); UI.skel(body, 'lines:3');
    UI.sheet({ title: `You vs ${e.name}`, size: 'm', body: b => b.append(body) });
    try {
      const d = await api(`/contest/${enc(cid)}/compare/${enc(e.pid)}`);
      const st = v => (v === true ? 'correct' : v === false ? 'incorrect' : v === null ? 'skipped' : v);
      const rowOf = (label, arr) => { const r = h('div', { class: 'sub-block' }, h('span', { class: 'k', text: label })); UI.strip(r, (arr || []).map(st), { label }); return r; };
      body.replaceChildren(rowOf('YOU', d.you), rowOf(e.name.toUpperCase(), d.them),
        h('p', { class: 'line', text: `Both right ${num(d.both)} · only you ${num(d.only_you)} · only them ${num(d.only_them)} · neither ${num(d.neither)}` }),
        d.h2h ? h('p', { class: 'meta', text: `This season: you ${d.h2h.you}–${d.h2h.them}` }) : null);
    } catch (err) { body.replaceChildren(h('p', { class: 'line', text: err.status === 403 ? 'Compare opens once you have both finished.' : 'Couldn’t load this.' })); }
  }
  function renderBoard() {
    const c = S.c, el = show('#board');
    const meta = h('span', { class: 'meta', id: 'board-meta' });
    const ctl = h('div', { class: 'board-ctl' });
    const host = h('div', { id: 'board-host' });
    const extra = h('div', { id: 'board-extra' });
    el.replaceChildren(head2('board-h', 'Board', meta), ctl, extra, host);
    if (c.series) C.under(ctl, [{ value: 'round', label: 'This round' }, { value: 'series', label: 'Series' }], { value: S.view, label: 'Board', onChange: v => { S.view = v; S.grid = false; reloadBoard(); } });
    if (S.view !== 'series' && !['rush', 'words'].includes(c.kind)) {
      C.under(ctl, [{ value: 'all', label: 'Everyone' }, { value: 'near', label: 'Near me' }, { value: 'following', label: 'Following' }, { value: 'level', label: 'My level' }, { value: 'country', label: 'Country' }],
        { value: S.scope, label: 'Scope', onChange: v => { S.scope = v; reloadBoard(); } });
    }
    if (open() && !['sprint', 'rush', 'words'].includes(c.kind) && S.view !== 'series') C.under(ctl, [{ value: false, label: 'List' }, { value: true, label: 'Grid' }], { value: S.grid, label: 'View', onChange: v => { S.grid = v; drawBoard(); } });
    if (!['sprint', 'rush', 'words'].includes(c.kind)) {
      C.under(ctl, [{ value: 'points', label: 'Points' }, { value: 'net', label: 'Over par' }], { value: S.sort, label: 'Order', onChange: v => { S.sort = v; S.view === 'series' ? reloadBoard() : drawBoard(); } });
      if (UI.switch && S.view !== 'series') UI.switch(ctl, { checked: parsOn(), label: 'Pars', onChange: on => { try { localStorage.setItem('satf.pars', on ? 'on' : 'off'); } catch (_) {} drawBoard(); } });
    }
    const find = h('input', { class: 'field', type: 'search', id: 'find', placeholder: 'Find a student', 'aria-label': 'Find a student', autocomplete: 'off' });
    const findMsg = h('span', { class: 'meta', role: 'status' });
    find.addEventListener('keydown', ev => { if (ev.key === 'Enter') { ev.preventDefault(); findMsg.textContent = S.api && S.api.find(find.value) ? '' : 'No public student has that name here.'; } });
    ctl.append(find, findMsg);
    if (!S.board) { UI.skel(host, 'table:6'); reloadBoard(); } else drawBoard();
  }
  async function reloadBoard(silent) {
    try { S.board = await fetchBoard(); S.polled = Date.now(); drawBoard(); }
    catch (e) { if (!silent) { const host = $('#board-host'); host.replaceChildren(); UI.cardError(host, () => reloadBoard()); } }
  }
  function drawBoard() {
    const c = S.c, host = $('#board-host'); if (!host) return;
    const b = sorted(S.board || {});
    const meta = $('#board-meta');
    if (meta) meta.textContent = `${num(b.players || 0)} ranked · updated ${S.polled && Date.now() - S.polled > 5000 ? `${Math.round((Date.now() - S.polled) / 1000)} s ago` : 'just now'}`;
    const extra = $('#board-extra');
    extra.replaceChildren();
    if (c.me && c.me.ranked === false && c.me.status === 'finished') extra.append(h('p', { class: 'line', text: `Your sitting is unranked: ${WHY[c.me.why] || c.me.why}` }));
    const top = (b.entries || []).filter(e => e.rank === 1);
    if (top.length > 1) extra.append(h('p', { class: 'meta', text: `=1 · ${top.length} ${top[0].points === 260 ? 'perfect runs' : 'share the top'}` }));
    if (S.grid) return drawGrid(host);
    const pars = () => (!parsOn() || S.sort !== 'points' || S.view === 'series' || S.scope !== 'all' ? [] :
      (b.pars || []).map(p => ({ label: `${[3, 5, 7, 9].includes(p.level) ? `Level ${p.level}` : `Your level (${p.level})`} par${p.rough ? ' (estimated)' : ''} · ${num(p.right)} right`, value: p.points })));
    host.replaceChildren();
    S.api = UI.board(host, b, {
      label: `${c.title} board`, columns: columns(c), pars, rowMenu, onFollow: follow, youText,
      value: e => (S.sort === 'net' ? e.net : e.points),
      empty: S.scope === 'near' && !(c.me && c.me.status === 'finished') ? 'Finish this contest to see who’s around you.' : 'No one else has finished yet.',
      onMore: off => api(`/contest/${enc(cid)}/board?scope=${S.scope}&offset=${off}`),
      onJump: you => { if (you.rank) api(`/contest/${enc(cid)}/board?scope=${S.scope}&offset=${Math.floor((you.rank - 1) / 50) * 50}`).then(d => { S.board = d; drawBoard(); S.api.jump(); }); },
    });
    renderThumb();
  }
  async function drawGrid(host) {
    host.replaceChildren(); UI.skel(host, 'table:6');
    try {
      const g = await api(`/contest/${enc(cid)}/grid`);
      const n = Math.max(...(g.rows || []).map(r => (r.marks || []).length), (g.footer || []).length, 0);
      const ST = { right: 'correct', wrong: 'incorrect', skip: 'skipped', void: 'voided' };
      const lad = S.c.ladder || [];
      const thead = h('thead', {}, h('tr', {}, h('th', { class: 'gn', scope: 'col', text: 'Student' }), Array.from({ length: n }, (_, i) => {
        const f = (g.footer || [])[i] || {}, q = lad[i] || {};
        const b = h('button', { type: 'button', text: String(i + 1) });
        b.addEventListener('click', () => openItem(i + 1));
        UI.tooltip(b, [`Q${i + 1}`, q.topic && C.topicName(q.topic), C.TIER[q.tier], f.right_share !== undefined ? `${pct(f.right_share)} right` : null, f.top && f.top.label ? `top trap: ${f.top.label}` : null].filter(Boolean).join(' · '));
        return h('th', { scope: 'col' }, b);
      })));
      const tbody = h('tbody', {}, (g.rows || []).map(r => h('tr', { class: r.you ? 'you' : null },
        h('th', { class: 'gn', scope: 'row', text: `${r.rank ? `${r.rank}. ` : ''}${r.name}${r.you ? ' (you)' : ''}` }),
        (r.marks || []).map((m, i) => h('td', {}, UI.cell(ST[m] || m, i + 1, { static: true, noun: 'Question' }))))));
      const tfoot = h('tfoot', {}, h('tr', {}, h('th', { class: 'gn', scope: 'row', text: '% right · median' }),
        Array.from({ length: n }, (_, i) => { const f = (g.footer || [])[i] || {}; return h('td', { text: `${f.right_share !== undefined ? Math.round(f.right_share * 100) : '—'}${f.median_ms ? ` ${mmss(f.median_ms / 1000)}` : ''}` }); })));
      const wrap = h('div', { class: 'grid-wrap', tabindex: '0', 'aria-label': 'The field’s answers' }, h('table', { class: 'grid-t' }, thead, tbody, tfoot));
      const kids = [];
      if ((g.where || []).length && S.c.kind === 'private') {
        kids.push(h('div', { class: 'sub-block' }, h('span', { class: 'k', text: 'WHERE WE WENT WRONG' }), h('ul', { class: 'mini-rows' }, g.where.slice(0, 3).map(w => h('li', {},
          h('span', { class: 'mt', text: w.label }), h('span', { class: 'mm', text: `${num(w.fell)} of ${num(w.of)}` }),
          w.you ? h('span', { class: 'ma' }, quiet('Fix it · 3', () => fix({ qid: w.qid, norm: w.norm, label: w.label }, 'Fix it · 3'))) : null)))));
      }
      kids.push(wrap);
      UI.legend && kids.push(UI.legend(null, ['correct', 'incorrect', 'skipped', 'voided']).el);
      if (g.next_offset !== null && g.next_offset !== undefined) kids.push(h('p', { class: 'meta', text: 'Showing the first 50 players.' }));
      host.replaceChildren(...kids);
    } catch (e) {
      host.replaceChildren(h('p', { class: 'line', text: e.status === 403 ? 'The grid opens when you finish, or after the contest closes.' : 'Couldn’t load the grid.' }));
    }
  }

  /* ------------------------------------------------------------ review */
  async function loadReviewData() {
    try { S.review = await api(`/contest/${enc(cid)}/review`); } catch (e) { S.review = null; S.reviewErr = e; }
  }
  function statusOf(it, i) {
    const q = ((S.c.me && S.c.me.result && S.c.me.result.questions) || [])[i];
    if (q && q.status) return { blank: 'unanswered' }[q.status] || q.status;
    return it.given === null || it.given === undefined ? 'skipped' : it.correct ? 'correct' : 'incorrect';
  }
  async function renderReview() {
    const el = show('#review');
    el.replaceChildren(head2('review-h', 'Review'));
    const box = h('div'); el.append(box); UI.skel(box, 'rows:4');
    if (!S.review && open()) await loadReviewData();
    if (!S.review) {
      box.replaceChildren(h('p', { class: 'line', text: !open() || (S.reviewErr && S.reviewErr.status === 403) ? 'Answers open when you finish, or after the contest closes.' : 'Couldn’t load the review.' }));
      return;
    }
    const items = S.review.items || [];
    const st = items.map(statusOf);
    const n = k => st.filter(s => s === k).length;
    const hardest = [...items.keys()].sort((a, b) => ((items[a].field || {}).right ?? 1) - ((items[b].field || {}).right ?? 1)).slice(0, 3);
    const opts = [{ value: 'all', label: 'All' }, { value: 'incorrect', label: 'Wrong', n: n('incorrect') }, { value: 'correct', label: 'Right', n: n('correct') },
      { value: 'skipped', label: 'Skipped', n: n('skipped') }, { value: 'voided', label: 'Voided', n: n('voided') }, { value: 'hard', label: 'Hardest for the field' }]
      .filter(o => o.n === undefined || o.n > 0);
    if (S.sel) opts.push({ value: 'sel', label: `Selected · ${S.sel.qids.length}` });
    const filt = C.under(null, opts, { value: S.filter, label: 'Show', onChange: v => { S.filter = v; if (v !== 'sel') S.sel = null; apply(); } });
    const list = h('div', { class: 'review-list' });
    items.forEach((it, i) => list.append(reviewRow(it, i, st[i])));
    box.replaceChildren(filt.el, list);
    function apply() {
      [...list.children].forEach((row, i) => {
        const s = st[i];
        row.hidden = !(S.filter === 'all' || (S.filter === 'hard' ? hardest.includes(i) : S.filter === 'sel' ? S.sel && S.sel.qids.includes(items[i].question.id) : s === S.filter));
      });
    }
    apply();
    S.applyReview = apply;
  }
  function setFilter(v, sel) {
    S.filter = v; S.sel = sel || null;
    renderReview().then(() => $('#review').scrollIntoView({ behavior: 'smooth' }));
  }
  function reviewRow(it, i, s) {
    const q = it.question, f = it.field || {};
    const mine = ((S.c.me && S.c.me.result && S.c.me.result.questions) || [])[i] || {};
    const d = h('details', { class: 'crv', id: `q${i + 1}` });
    const sum = h('summary', {},
      h('span', { class: 'q', text: `Q${i + 1}` }),
      h('span', { class: 's' }, UI.glyph ? UI.glyph(q.topic) : null, h('span', { text: q.type_name || C.topicName(q.topic) }), UI.dbars ? UI.dbars(q.difficulty, { bare: true }) : null),
      h('span', { class: 'mark', text: STATUS[s] || '', 'aria-label': STATUS_WORD[s] || s }),
      h('span', { class: 'm', text: [f.right !== undefined && f.players ? `field ${pct(f.right)} right` : null,
        mine.ms ? `you ${mmss(mine.ms / 1000)}` : null, f.median_ms ? `field median ${mmss(f.median_ms / 1000)}` : null].filter(Boolean).join(' · ') }));
    d.append(sum);
    let built = false;
    d.addEventListener('toggle', () => {
      if (!d.open || built) return;
      built = true;
      const body = h('div', { class: 'crv-body' });
      d.append(body);
      const qh = h('div');
      body.append(qh);
      const fb = { answer: q.answer, correct: it.correct, given: it.given, rationale: q.rationale, reasons: q.reasons };
      try { (UI.workspace || UI.question)(qh, q, { mode: 'review', fb, bar: false }); }
      catch (e) { qh.append(h('p', { class: 'line', text: q.stem }), h('p', { class: 'line', text: `Answer: ${q.answer}` }), h('p', { class: 'meta', text: q.rationale || '' })); }
      // how the field answered: one bar per misconception across the twins
      const opts = [{ label: 'Right', share: f.right || 0, key: true, pick: it.correct }];
      (f.mistakes || []).forEach(m => opts.push({ label: m.label, share: m.share, n: m.count, pick: !!mine.mistake && String(mine.mistake).toLowerCase() === String(m.norm).toLowerCase() }));
      if (f.skipped) opts.push({ label: 'Skipped / blank', share: f.skipped });
      if (f.voided) opts.push({ label: 'Voided', share: f.voided });
      const sp = h('div', {}, h('span', { class: 'k', text: f.players >= 5 ? `HOW THE FIELD ANSWERED · ${num(f.players)}` : 'HOW THE FIELD ANSWERED · ON THIS TYPE, ALL MODES' }));
      if (UI.spread) UI.spread(sp, opts, { label: 'How the field answered', noun: 'players' });
      body.append(sp);
      const act = h('div', { class: 'row-act' }, quiet('Another like this', ev => busy(ev.currentTarget, () => drill({ templates: [q.key], count: 5, source: 'result' }))));
      if (s === 'incorrect' || s === 'skipped') act.append(quiet(s === 'skipped' ? 'Try it now' : 'Fix it · 3', () => fix({ qid: q.id, norm: mine.mistake ? String(mine.mistake).toLowerCase() : null, label: mine.mistake || q.type_name }, s === 'skipped' ? 'Try it now' : 'Fix it · 3')));
      body.append(act);
      // the Player region's keys (§2.8): B save, R report, while focus is inside this item (C24)
      const sid = S.c.me && S.c.me.session;
      if (UI.questionActions && sid && finished()) {
        const qa = UI.questionActions(null, q, { revealed: true, source: 'challenge', session: sid, question_id: q.id,
          on: { save: v => api('/saved', { method: 'POST', body: { session: sid, question_id: q.id, on: v } }) } });
        act.prepend(qa.el);
        UI.keys.register(`compete-review-${i}`, {
          B: { does: 'Save the question', run: () => qa.run('save') },
          R: { does: 'Report a problem', run: () => qa.run('report') },
        }, { label: 'Review item', within: d });
      }
    });
    return d;
  }
  function openItem(n) {
    const d = document.getElementById(`q${n}`);
    if (!d) { if ($('#review').hidden) return; setTimeout(() => openItem(n), 300); return; }
    if (d.hidden) { S.filter = 'all'; S.sel = null; renderReview().then(() => openItem(n)); return; }
    d.open = true;
    d.scrollIntoView({ behavior: 'smooth', block: 'start' });
    d.querySelector('summary').focus({ preventScroll: true });
  }

  /* ------------------------------------------------------------ the field's traps */
  async function renderTraps() {
    const el = show('#traps');
    try {
      const d = await api(`/contest/${enc(cid)}/traps`);
      S.traps = (d.traps || []).slice(0, 5);
      if (!S.traps.length) { el.hidden = true; return; }
      const mineTraps = new Set((((S.c.me && S.c.me.result) || {}).questions || []).map(q => String(q.mistake || '').toLowerCase()).filter(Boolean));
      const inMine = norm => ((S.review && S.review.items) || []).some(it => ((it.field || {}).mistakes || []).some(m => m.norm === norm));
      const players = (S.c.field && S.c.field.players) || 0;
      const ul = h('ul', { class: 'mini-rows traps-list' }, S.traps.map(t => h('li', {},
        h('span', { class: 'mt', text: t.label }),
        h('span', { class: 'mm', text: [players ? `${num(t.fell)} answer${t.fell === 1 ? '' : 's'} fell for it` : null,
          !finished() ? null : mineTraps.has(String(t.norm).toLowerCase()) ? 'you too' : inMine(t.norm) ? 'you avoided it' : S.review ? 'not in your questions' : null].filter(Boolean).join(' · ') }))));
      const go = h('button', { type: 'button', class: 'pill sm', text: `Practice these ${S.traps.length}` });
      go.addEventListener('click', () => busy(go, practiceTraps));
      el.replaceChildren(head2('traps-h', 'Where the field went wrong'), ul, h('div', { class: 'row-act' }, go));
    } catch (e) { el.hidden = true; }
  }

  /* ------------------------------------------------------------ side: rules, entrants, settings, the question of the day */
  function renderRules() {
    const c = S.c, k = C.kind(c);
    const li = (b, t) => h('li', {}, h('b', { text: b }), ` ${t}`);
    const rules = [];
    if (c.kind === 'rush') rules.push(li('Three strikes:', 'a miss, or an answer over 1.5× its time budget, is a strike; three end the run.'), li('It climbs:', 'each right answer serves a harder question, each miss an easier one.'), li('Board:', 'right answers, then the hardest item solved. Every run ranks; time never breaks a tie.'));
    else if (c.kind === 'words') rules.push(li('Score:', 'right − wrong ÷ 3, so guessing doesn’t pay. Skips score 0.'), li('Clock:', '4 minutes. Your best run this week counts.'));
    else {
      rules.push(li('Points:', '10 / 20 / 30 for each easy / medium / hard answer right.'));
      if (k.pace) rules.push(li('Pace bonus:', '+5 for each right answer within its time budget (easy 1:05 · medium 1:35 · hard 2:06).'));
      if (c.kind !== 'sprint') rules.push(li('Finish bonus:', '+10 for answering every question with none skipped or voided.'));
      rules.push(k.clock === 'answer' ? li('Answer clock:', 'it runs only while a question is open. Reading the key and the rationale is free.') : li('Wall clock:', 'like the real test; the board ranks on points.'));
      rules.push(li('Skip:', 'scores 0 and shows the key at once.'));
      if (c.kind !== 'private' || (c.spec && c.spec.strict)) rules.push(li('Confirms:', 'leaving the tab or window, or copying the question and leaving, means a quick confirm on new numbers at the end. A right confirm keeps its points.'));
      rules.push(li('Ties:', 'equal points share a rank; time never breaks a tie.'));
      if (['daily', 'weekly', 'final', 'trap'].includes(c.kind)) rules.push(li('Par:', 'what a student at your rating is expected to score on these questions. Over par = base points − par.'));
      if (k.twins || (c.spec && c.spec.twin)) rules.push(li('Twins:', 'your own twin questions: same types, your own numbers.'));
      rules.push(li('Ranked:', c.kind === 'sprint' ? 'every run; your best run this week counts.' : c.kind === 'private' ? 'your first sitting in the round. No rating or season points.' : 'your first sitting counts.'));
    }
    $('#rules').replaceChildren(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'How it’s ranked' })), h('ul', { class: 'rules' }, rules));
  }
  function renderEntrants() {
    const c = S.c;
    if (c.kind !== 'private' || !(c.entrants || []).length) return;
    const el = show('#entrants');
    const done = c.entrants.filter(e => e.status === 'finished').length;
    el.replaceChildren(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: `Entrants (${c.entrants.length})` }), h('span', { class: 'meta', text: done ? `${done} done` : '' })),
      h('ul', { class: 'ent' }, c.entrants.map(e => h('li', {}, h('i', { class: `edot${e.status === 'finished' ? 'done' : e.status === 'progress' ? 'progress' : ''}`, 'aria-hidden': 'true' }),
        e.name, h('span', { class: 'sr', text: e.status === 'finished' ? ' finished' : e.status === 'progress' ? ' in progress' : ' not started' })))),
      h('div', { class: 'day-legend' }, h('span', {}, h('i', { class: 'sat', style: 'border-radius:50%;background:var(--ink)' }), 'finished'), h('span', {}, h('i', { style: 'border-radius:50%;background:linear-gradient(90deg,var(--ink) 50%,var(--mat) 50%)' }), 'in progress'), h('span', {}, h('i', { style: 'border-radius:50%' }), 'not yet')));
  }
  function renderOwner() {
    const c = S.c;
    if (c.kind !== 'private') return;
    const k = c.code || localCode(c);
    if (!c.owner && !k) return;
    const el = show('#owner');
    const link = k ? `${location.origin}/compete/contest/?code=${k}` : null;
    const act = h('div', { class: 'row-act' });
    if (link) act.append(quiet('Copy link', () => UI.copyText(link)), quiet('Copy code', () => UI.copyText(k)));
    const patch = async (body, done) => { try { await api(`/contest/${enc(c.id)}`, { method: 'PATCH', body }); UI.toast(done); load(); } catch (e) { UI.toast(e.status === 403 ? 'Only the creator can change settings.' : e.message || 'Not saved.'); } };
    const owner = [
      quiet('Rename', async () => { const t = await UI.confirm({ title: 'Rename the contest', input: { label: 'Title', value: c.title, maxlength: 40 }, confirm: 'Save' }); if (t && t.trim()) patch({ title: t.trim() }, 'Renamed'); }),
      quiet('Extend 24 h', async () => { if (await UI.confirm({ title: 'Extend by 24 hours?', text: `It will close ${C.when(new Date(new Date(c.closes).getTime() + 864e5).toISOString())}.`, confirm: 'Extend' })) patch({ extend: 24 }, 'Extended'); }),
      quiet('Close now', async () => { if (await UI.confirm({ title: 'Close the contest now?', text: 'Nobody can start it after this. Sittings in progress can still finish.', confirm: 'Close now', destructive: true })) patch({ close: true }, 'Closed'); }),
      quiet('Remove an entrant', ev => UI.menu(ev.currentTarget, (c.entrants || []).filter(e => e.pid && e.pid !== myPid()).map(e => ({ label: e.name, onClick: async () => {
        if (!(await UI.confirm({ title: `Remove ${e.name}?`, text: 'Their sittings leave this contest’s board.', confirm: 'Remove', destructive: true }))) return;
        try { await api(`/contest/${enc(c.id)}/members/${enc(e.pid)}`, { method: 'DELETE' }); UI.toast('Removed'); load(); } catch (err) { UI.toast(err.message || 'Not removed.'); }
      } })), { label: 'Remove an entrant' })),
      quiet('Delete', async () => { if (!(await UI.confirm({ title: 'Delete this contest?', text: 'Every round, sitting and board goes. This cannot be undone.', confirm: 'Delete', destructive: true }))) return;
        try { await api(`/contest/${enc(c.id)}`, { method: 'DELETE' }); location.href = '/compete/'; } catch (e) { UI.toast(e.status === 403 ? 'Only the creator can delete it.' : 'Not deleted.'); } }),
    ];
    el.replaceChildren(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'Contest settings' })),
      k ? h('p', { class: 'cx-code', style: 'font-size:28px', text: k }) : null, act,
      h('div', { class: 'row-act' }, owner), h('p', { class: 'help', text: 'You see what every entrant sees: the board and, once they finish, the grid.' }));
  }
  async function renderQotd() {
    const el = show('#qotd');
    const day = dayOf(S.c);
    el.replaceChildren(h('div', { class: 'card-head' }, h('span', { class: 'k', text: 'QUESTION OF THE DAY' })));
    const box = h('div'); el.append(box); UI.skel(box, 'lines:3');
    try {
      const d = await api(`/qotd?day=${day}`);
      const q = d.question, m = d.mine;
      box.replaceChildren();
      const qh = h('div'); box.append(qh);
      const ws = UI.workspace || UI.question;
      if (m) {
        ws(qh, q, { mode: 'review', fb: { answer: m.answer ?? m.key, correct: m.correct, given: m.given ?? m.pick, rationale: m.rationale, reasons: m.reasons }, bar: false });
        if ((m.options || d.options || []).length && UI.spread) UI.spread(box, (m.options || d.options).map((o, i) => ({ label: 'ABCD'[o.index ?? i], share: o.share, key: o.key, pick: o.pick, reason: o.mistake })), { label: 'How everyone answered' });
      } else {
        const past = day < todayISO();
        box.prepend(h('p', { class: 'help', text: past ? 'Answer, unranked: it doesn’t count for your streak.' : 'Today’s question; answering it here counts like on Today.' }));
        ws(qh, q, { mode: 'practice', feedback: 'instant', onCheck: async answer => {
          const r = await api('/qotd', { method: 'POST', body: { day, answer } });
          return { ...r, given: answer };
        } });
      }
      if ((d.days || []).length) box.append(h('div', { class: 'day-strip' }, d.days.map(x => h('a', { href: C.href(`daily-${x.day}`) + '#qotd', 'data-s': x.state === 'right' ? 'sat' : x.state === 'wrong' ? 'ghost' : 'missed', 'aria-label': `${x.day}: ${x.state}` }))));
    } catch (e) { box.replaceChildren(); UI.cardError(box, renderQotd); }
  }

  /* ------------------------------------------------------------ the phone thumb bar (C24) */
  function renderThumb() {
    const c = S.c, bar = $('#thumb'); if (!c) return;
    const me = c.me || {};
    let primary = null;
    if (me.status === 'progress') primary = h('button', { type: 'button', class: 'pill', text: 'Resume', onclick: ev => busy(ev.currentTarget, () => C.start(c.id)) });
    else if (me.status === 'finished') primary = h('button', { type: 'button', class: 'pill', text: 'See the board', onclick: () => $('#board').scrollIntoView({ behavior: 'smooth' }) });
    else if (c.status === 'live') primary = h('button', { type: 'button', class: 'pill', text: 'Start', onclick: ev => doStart(ev.currentTarget) });
    if (!primary) { bar.hidden = true; return; }
    const jump = S.board && S.board.you ? quiet('Jump to me', () => S.api && S.api.jump()) : null;
    bar.replaceChildren(primary, ...(jump ? [jump] : []));
    bar.hidden = false;
    $('#main').classList.add('has-thumb');
  }

  /* ------------------------------------------------------------ keys (C24) and the live poll */
  UI.keys.register('compete-contest', {
    'Shift+B': { does: 'Jump to the board', run: () => { const b = $('#board'); if (!b.hidden) b.scrollIntoView({ behavior: 'smooth' }); } },
    'Shift+V': { does: 'Jump to Review', run: () => { const b = $('#review'); if (!b.hidden) b.scrollIntoView({ behavior: 'smooth' }); } },
    'Shift+Y': { does: 'Jump to your row', run: () => S.api && S.api.jump() },
    ',': { does: 'Previous day', run: () => { if (S.c && S.c.kind === 'daily') location.href = C.href(`daily-${shiftDay(dayOf(S.c), -1)}`); } },
    '.': { does: 'Next day', run: () => { if (S.c && S.c.kind === 'daily' && dayOf(S.c) < todayISO()) location.href = C.href(`daily-${shiftDay(dayOf(S.c), 1)}`); } },
    '/': { does: 'Find a student', run: () => { const f = $('#find'); if (f) f.focus(); } },
  }, { label: 'This page' });
  setInterval(() => {
    if (document.visibilityState !== 'visible' || !S.c || S.c.status !== 'live' || S.view === 'series' || S.grid) return;
    reloadBoard(true);
  }, 30000);
  load();
})();
