/* ============================================================================
   SAT Freshman -- Profile, /me/ (Shell 3; shell-me U4-U14, U22, U25, U26, U29; R25, R31)
   and, with window.ME_SHARE set, the read-only progress view /share/?t= (Shell 6).

   One call builds the page: GET /api/me/summary (painted from its cached copy first),
   with /api/me, /api/account, /api/me/activity, /api/me/week and /api/me/feed beside it.
   Each card loads, fails and retries on its own. Sixteen cards, two columns from 1024px
   (one column below, in the phone order), a section bar with every card, and a fold on
   each card kept in localStorage satf.me.collapsed.

   The user's rules (2026-09-28) hold throughout: no calibration words (rough, levels,
   odds), scores read "7 / 11", no timestamps in history lines, no card repeats another
   card's numbers, zeros and defaults stay out.
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h, A = UI.acct;
  const N = n => UI.num(n);
  const pl = (n, one, many) => `${N(n)} ${n === 1 ? one : many || one + 's'}`;
  const tn = t => (UI.TOPIC[t] && UI.TOPIC[t].short) || String(t || '').replace(/_/g, ' ');
  const day = d => UI.date(d, 'short');
  const band = b => (b ? `${b.low}–${b.high}` : '');
  const mid = b => Math.round((b.low + b.high) / 2);
  const pct = x => `${Math.round((x || 0) * 100)}%`;
  const ic = (name, size = 16) => h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.svg(UI.ICON[name] || UI.ICON.dot, size) });
  const ls = A.ls;
  const phone = () => matchMedia('(max-width: 759px)').matches;
  const query = new URLSearchParams(location.search);
  const SHARE = window.ME_SHARE || null;
  const RO = !!SHARE;
  const PENCIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const KIND = { module: 'Module', section: 'Section', mock: 'Practice test', paper: 'Official paper', diagnostic: 'Diagnostic',
    outside: 'Added score', drill: 'Practice', challenge: 'Challenge' };
  const setLen = () => { const n = (UI.prefs.now() || {}).set_length; return n > 0 ? n : 10; };

  /* ---- actions: none at all on the shared view */
  function start(body, b) {
    if (b) b.setAttribute('aria-busy', 'true');
    return UI.start({ start: { body } }).catch(e => { if (!e || !e.offline) UI.toast('Couldn’t start that. Try again.'); })
      .finally(() => { if (b) b.removeAttribute('aria-busy'); });
  }
  function btn(label, o = {}) {
    if (RO) return document.createTextNode('');       // placed anywhere a control would be, it adds nothing
    const tag = o.href ? 'a' : 'button';
    const b = h(tag, { class: o.primary ? 'pill sm' : o.quiet ? 'quiet' : o.link ? 'link' : 'btn sm', type: o.href ? null : 'button',
      href: o.href || null, 'aria-label': o.aria || null }, label);
    if (o.body) b.addEventListener('click', () => start(o.body, b));
    else if (o.onClick) b.addEventListener('click', e => o.onClick(e, b));
    return b;
  }
  const tag = t => h('span', { class: 'tag' }, UI.glyph(t), tn(t));
  const fact = (el, key, label) => { if (!RO && key) { el.dataset.fact = key; if (label) el.dataset.factLabel = label; } return el; };

  /* ---- the cards */
  const CARDS = [
    { id: 'you', title: 'You', col: 'L', o: 1 },
    { id: 'snapshot', title: 'Snapshot', col: 'L', o: 5, help: 'band' },
    { id: 'saved', title: 'Saved & in progress', col: 'L', o: 15, chip: 'Saved', me: true },
    { id: 'account', title: 'Account', col: 'L', o: 16, me: true, help: 'devices' },
    { id: 'week', title: 'This week', col: 'R', o: 2 },
    { id: 'goals', title: 'Goals', col: 'R', o: 3, help: 'routing' },
    { id: 'prefs', title: 'Learning preferences', col: 'R', o: 14, chip: 'Preferences', me: true, help: 'stages' },
    { id: 'skills', title: 'Skills', col: 'R', o: 4, help: 'points' },
    { id: 'readiness', title: 'Test-day readiness', col: 'R', o: 6, chip: 'Readiness', help: 'readiness' },
    { id: 'trend', title: 'Score trend', col: 'R', o: 7, chip: 'Trend', help: 'projection' },
    { id: 'pace', title: 'Pace', col: 'R', o: 8, me: true, help: 'pace' },
    { id: 'catching', title: 'What keeps catching you', col: 'R', o: 9, chip: 'Catching you', help: 'mistakes' },
    { id: 'habits', title: 'Your habits', col: 'R', o: 10, chip: 'Habits', help: 'habits' },
    { id: 'badges', title: 'Achievements', col: 'R', o: 11, chip: 'Badges', me: true },
    { id: 'activity', title: 'Activity', col: 'R', o: 12, help: 'streak' },
    { id: 'recent', title: 'Recent activity', col: 'R', o: 13, chip: 'Recent' },
  ].filter(c => !RO || !c.me);
  const CHIPS = ['you', 'week', 'goals', 'snapshot', 'readiness', 'skills', 'trend', 'pace', 'catching', 'habits', 'badges',
    'activity', 'recent', 'prefs', 'saved', 'account'];
  const C = {};
  const folded = new Set(RO ? [] : ls.get('satf.me.collapsed', []));
  function makeCard(c) {
    const title = c.id === 'you' ? null : h('h2', { id: `${c.id}-h`, text: c.title });
    const act = h('div', { class: 'card-act' });
    const fold = RO ? null : h('button', { type: 'button', class: 'ibtn card-fold', html: UI.svg(UI.ICON.chev, 18) });
    const head = h('div', { class: 'card-head' }, title, c.help && !RO ? A.helpBtn(c.help, c.title) : null, act, fold);
    const sum = h('p', { class: 'card-sum' });
    const body = h('div', { class: 'card-body' });
    const el = h('section', { class: 'card' + (c.id === 'you' ? ' id-card' : ''), id: c.id, style: `--o: ${c.o}`,
      'aria-labelledby': title ? title.id : null, 'aria-label': title ? null : 'You' }, head, sum, body);
    const setFold = on => {
      el.toggleAttribute('data-collapsed', on);
      if (fold) { fold.setAttribute('aria-expanded', String(!on)); fold.setAttribute('aria-label', `${on ? 'Expand' : 'Collapse'} ${c.title}`); }
      if (on) folded.add(c.id); else folded.delete(c.id);
    };
    if (fold) fold.addEventListener('click', () => { setFold(!el.hasAttribute('data-collapsed')); ls.set('satf.me.collapsed', [...folded]); });
    el.addEventListener('satf:open', () => { if (el.hasAttribute('data-collapsed')) { setFold(false); ls.set('satf.me.collapsed', [...folded]); } });
    setFold(folded.has(c.id));
    document.getElementById(c.col === 'L' ? 'colL' : 'colR').append(el);
    C[c.id] = { el, act, sum, body, title };
  }
  CARDS.forEach(makeCard);
  const fill = (id, ...kids) => { if (C[id]) C[id].body.replaceChildren(...kids.flat(3).filter(k => k !== null && k !== undefined && k !== false)); };
  const acts = (id, ...kids) => { if (C[id]) C[id].act.replaceChildren(...kids.flat().filter(Boolean)); };
  const said = (id, text) => { if (C[id]) C[id].sum.textContent = text || ''; };
  CARDS.forEach(c => fill(c.id, UI.skel(null, c.id === 'you' ? 'card:5' : 'card:3')));

  /* ---- the data, each piece on its own */
  let S = null, P = null, ACC = null, DEV = null, PK = null, ACT = null, WEEK = null, TYPES = null, SHELL = null;
  const FEED = { items: null, next: null, unread: 0, kind: query.get('feed') === 'unread' ? 'unread' : 'all' };
  const err = {};
  const DATA = { summary: () => S, profile: () => P, account: () => ACC, activity: () => ACT, week: () => WEEK, types: () => TYPES, feed: () => FEED.items };
  function ready(id, ...keys) {
    for (const k of keys) {
      if (DATA[k]()) continue;
      if (err[k]) fill(id, UI.cardError(null, err[k]));
      return false;
    }
    return true;
  }
  const PAINT = {};
  const paint = (...ids) => ids.forEach(id => { if (C[id] && PAINT[id]) { try { PAINT[id](); } catch (e) { console.error(e); fill(id, UI.cardError(null, () => paint(id))); } } });
  const SUMMARY = ['you', 'snapshot', 'saved', 'goals', 'skills', 'readiness', 'trend', 'pace', 'catching', 'habits', 'badges'];
  const failOn = (k, retry, ids) => e => { if (e && e.retired) return; err[k] = () => { delete err[k]; return retry(); }; paint(...ids); };

  function loadSummary() {
    return UI.cached('/me/summary', d => { S = d; paint(...SUMMARY); }).catch(e => { if (!S) failOn('summary', loadSummary, SUMMARY)(e); });
  }
  function loadProfile(fresh) {
    return UI.me(fresh).then(r => { P = r.profile; paint('you', 'goals', 'snapshot'); }, failOn('profile', () => loadProfile(true), ['you', 'goals']));
  }
  function loadAccount() {
    return Promise.all([UI.api('/account'), UI.api('/devices').catch(() => null), UI.api('/passkeys').catch(() => null)])
      .then(([a, d, k]) => { ACC = a; DEV = d; PK = k; paint('account', 'you'); }, failOn('account', loadAccount, ['account']));
  }
  let weeks = ls.get('satf.me.weeks', 26);
  function loadActivity() {
    return UI.api(`/me/activity?weeks=${weeks}`).then(d => { ACT = d; paint('activity', 'goals'); }, failOn('activity', loadActivity, ['activity']));
  }
  function loadWeek() {
    return UI.api('/me/week').then(d => { WEEK = d; paint('week'); }, failOn('week', loadWeek, ['week']));
  }
  function loadTypes() {
    return UI.types().then(t => { TYPES = t; paint('readiness'); }, failOn('types', loadTypes, ['readiness']));
  }
  async function loadFeed(reset) {
    const qs = new URLSearchParams({ limit: '20' });
    if (FEED.kind === 'unread') qs.set('unread', '1');
    else if (FEED.kind !== 'all') qs.set('kind', FEED.kind);
    if (!reset && FEED.next) qs.set('before', FEED.next);
    try {
      const r = await UI.api(`/me/feed?${qs}`);
      FEED.items = reset || !FEED.items ? r.items : FEED.items.concat(r.items);
      FEED.next = r.next;
      FEED.unread = r.unread || 0;
      paint('recent');
      if (FEED.kind === 'unread' && r.items.length) UI.whenVisible(() => UI.api('/me/feed/seen', { method: 'POST', quiet: true }).then(() => UI.refresh(), () => {}));
    } catch (e) { failOn('feed', () => loadFeed(true), ['recent'])(e); }
  }
  const reloadMe = () => { loadSummary(); loadProfile(true); };

  /* ================================================================ You (Shell 3.1, U10, U22, U29) */
  PAINT.you = () => {
    if (!ready('you', 'summary', ...(RO ? [] : ['profile']))) return;
    const st = S.stats, me = (SHELL && SHELL.me) || {}, prof = P || {};
    const name = prof.name || (RO ? S.name : me.name) || prof.handle || (RO ? '' : 'Student');
    const av = UI.avatar({ self: !RO, name: name || 'Student', avatar: RO ? 'mark' : prof.avatar || null, domains: S.domains,
      ring: me.avatar && me.avatar.ring, learner: RO ? null : UI.learner() }, 72);
    const avWrap = h('div', { class: 'av' }, av);
    if (!RO) {
      const pick = h('button', { type: 'button', class: 'av-edit', 'aria-label': 'Change avatar', html: PENCIL });
      pick.addEventListener('click', () => avatarPicker(pick));
      avWrap.append(pick);
    }
    const nameBox = h('div', { class: 'id-name' });
    const showName = () => {
      nameBox.replaceChildren(h('h1', { text: name || 'Your progress' }));
      if (!RO) nameBox.append(btn('Edit', { quiet: true, aria: 'Edit name', onClick: editName }));
    };
    function editName() {
      const f = h('input', { class: 'field', value: prof.name || '', maxlength: '40', 'aria-label': 'Your name', autocomplete: 'given-name' });
      const e = h('p', { class: 'field-err', hidden: true, role: 'alert' });
      nameBox.replaceChildren(f, e);
      f.focus(); f.select();
      f.addEventListener('keydown', async ev => {
        if (ev.key === 'Escape') { ev.preventDefault(); showName(); }
        if (ev.key !== 'Enter') return;
        const v = f.value.trim();
        if (v === (prof.name || '')) { showName(); return; }
        if (v && !A.NAME_OK.test(v)) { e.textContent = 'Names can’t contain digits, @, < or >.'; e.hidden = false; return; }
        try { P = await A.saveMe({ name: v || null }); UI.toast('Saved'); paint('you'); }
        catch (x) { e.textContent = A.nameError(x); e.hidden = false; }
      });
    }
    showName();
    const lines = h('div', { class: 'id-lines' });
    if (!RO) {
      lines.append(boardLine(prof, name));
      if (st.answered && st.since) lines.append(h('span', { text: `Studying since ${day(st.since)}` }));
      if (ACC) lines.append(ACC.saved
        ? h('span', {}, h('span', { class: 'chk', 'aria-hidden': 'true', text: '✓' }), ACC.email_masked || 'Progress saved')
        : h('span', {}, h('span', { class: 'odot', 'aria-hidden': 'true' }), 'This device only · ', h('a', { class: 'link', href: '/me/settings/#account', text: 'Save progress' })));
    }
    fill('you', h('div', { class: 'id-top' }, avWrap, RO ? null : nameBox), RO ? null : lines, outcomes(), tiles());
    said('you', [name, st.answered ? `${N(st.answered)} answered` : null, st.streak ? `streak ${N(st.streak)}` : null].filter(Boolean).join(' · '));
  };
  function boardLine(prof, name) {
    const offer = prof.name && !prof.handle && A.HANDLE_OK.test(prof.name);
    const line = h('span', { class: 'id-board' }, 'On boards: ', prof.handle ? h('b', { text: prof.handle }) : 'no name yet',
      prof.board && prof.board !== 'name' ? ` · ${prof.board === 'anon' ? 'anonymous' : 'hidden'}` : null, ' · ');
    // the first time a name is set, one tap puts it on the boards too (U29)
    if (offer) line.append(btn(`Use ${prof.name}`, { quiet: true, aria: `Use ${prof.name} on boards too`, onClick: async () => {
      try { P = await A.saveMe({ handle: prof.name }); UI.toast(`On boards: ${prof.name}`); paint('you'); }
      catch (x) { if (x.status === 409) { UI.toast('Someone already has that board name. Pick another.'); boardPop(line); } else UI.toast(A.handleError(x)); }
    } }), ' · ');
    line.append(btn(prof.handle ? 'Change' : offer ? 'Other' : 'Choose one', { quiet: true, aria: 'Change your board name', onClick: (e, b) => boardPop(b) }));
    return line;
  }
  function boardPop(anchor) {
    const prof = P || {};
    UI.pop(anchor, (p, res) => {
      const f = h('input', { class: 'field', value: prof.handle || '', maxlength: '24', 'aria-label': 'Board name', autocomplete: 'off',
        placeholder: prof.name && A.HANDLE_OK.test(prof.name) ? `${prof.name.replace(/\s+/g, '_')}2` : 'Board name' });
      const e = h('p', { class: 'field-err', hidden: true, role: 'alert' });
      const save = h('button', { type: 'button', class: 'pill sm', text: 'Save' });
      save.addEventListener('click', async () => {
        const v = f.value.trim();
        if (!A.HANDLE_OK.test(v)) { e.textContent = A.handleError({ status: 422 }); e.hidden = false; return; }
        try { P = await A.saveMe({ handle: v }); res.close(); UI.toast(`On boards: ${v}`); paint('you'); }
        catch (x) { e.textContent = A.handleError(x); e.hidden = false; }
      });
      f.addEventListener('keydown', ev => { if (ev.key === 'Enter') save.click(); });
      const vis = h('div');
      UI.seg(vis, [{ value: 'name', label: 'By name' }, { value: 'anon', label: 'Anonymous' }, { value: 'hidden', label: 'Don’t list me' }],
        { value: prof.board || 'name', label: 'Show me on boards', onChange: async v => {
          try { P = await A.saveMe({ board: v }); UI.toast('Saved'); paint('you'); } catch (_) { UI.toast('Not saved. Try again.'); }
        } });
      return [h('div', { class: 'pop-form' }, h('label', { class: 'label', text: 'Board name' }), f, e,
        h('p', { class: 'help', text: 'The only name boards, contests and ranks show. Your own name stays private.' }), save,
        h('span', { class: 'label', text: 'Show me on boards' }), vis,
        h('p', { class: 'help', text: 'Anonymous shows a student number. Unlisted still shows you your own rank.' }))];
    }, { label: 'Board name' });
  }
  function avatarPicker(anchor) {
    const prof = P || {};
    const skills = {};
    (S.domains || []).forEach(d => d.skills.forEach(s => { skills[s.topic] = s; }));
    UI.pop(anchor, (p, res) => {
      const grid = h('div', { class: 'av-grid', role: 'group', 'aria-label': 'Avatar' });
      const choose = async v => {
        try { P = await A.saveMe({ avatar: v }); res.close(); UI.toast('Saved'); paint('you'); } catch (_) { UI.toast('Not saved. Try again.'); }
      };
      if (!UI.shared()) {
        const picker = (label, extra) => {
          const file = h('input', { type: 'file', accept: 'image/*', hidden: true, ...extra });
          file.addEventListener('change', async () => {
            if (!file.files[0]) return;
            try { await UI.localPhoto.set(file.files[0]); res.close(); UI.toast('Photo set on this device'); paint('you'); }
            catch (_) { UI.toast('That photo couldn’t be used. Try another.'); }
          });
          const b = h('button', { type: 'button', class: 'wide' }, ...label);
          b.addEventListener('click', () => file.click());
          grid.append(b, file);
          return b;
        };
        const photo = picker(['Your photo', h('small', { text: 'this device only' })]);
        // a phone can take one with its front camera (U22)
        if (matchMedia('(pointer: coarse)').matches) picker(['Take one', h('small', { text: 'front camera' })], { capture: 'user' });
        UI.localPhoto.get().then(b => {
          if (!b) return;
          const rm = h('button', { type: 'button', class: 'wide' }, 'Remove your photo');
          rm.addEventListener('click', async () => {
            const ok = await UI.confirm({ title: 'Remove your photo?', text: `Your ${prof.avatar ? tn(prof.avatar) + ' glyph' : 'living mark'} will be shown instead.`, confirm: 'Remove' });
            if (ok) { await UI.localPhoto.remove(); res.close(); paint('you'); }
          });
          photo.after(rm);
        });
      }
      const tile = (value, label, content, extra = {}) => {
        const b = h('button', { type: 'button', 'aria-pressed': String((prof.avatar || null) === value),
          'aria-label': `${label}${(prof.avatar || null) === value ? ', selected' : ''}${extra.note ? `. ${extra.note}` : ''}`, 'data-ring': extra.ring ? '' : null }, content);
        if (extra.note) UI.tooltip(b, extra.note);
        b.addEventListener('click', () => choose(value));
        return b;
      };
      grid.append(tile(null, 'Living mark', UI.avatar({ avatar: 'mark', domains: S.domains }, 'mk')));
      UI.TOPICS.forEach(t => {
        const s = skills[t.slug] || {};
        const strong = s.answered && s.mastery >= UI.STRONG;
        grid.append(tile(t.slug, t.short, UI.glyph(t.slug), { ring: strong,
          note: strong ? `Strong in ${t.short}` : `Strong in ${t.short} adds the ring · ${pct(s.mastery)}` }));
      });
      return [h('div', { class: 'av-pick' }, grid,
        h('p', { class: 'help', text: 'Boards show your glyph or initial. Only you and your progress links see the living mark, and only this device sees your photo.' }))];
    }, { label: 'Change avatar' });
  }
  function outcomes() {
    const out = h('div', { class: 'outs' });
    const sit = (S.score.points || []).slice().sort((a, b) => (a.at < b.at ? -1 : 1));
    const L = S.score.latest;
    if (sit.length >= 2 && L) {
      const d = mid(L) - mid(sit[0]);
      out.append(fact(h('button', { type: 'button', class: 'out' }, h('b', { text: `${d >= 0 ? '+' : '−'}${N(Math.abs(d))}` }), 'since you started',
        h('span', { class: 'meta', text: `${band(sit[0])} → ${band(L)}` })), 'band', 'Since you started'));
    } else if (!RO) {
      out.append(h('a', { class: 'out', href: '/tests/' }, sit.length ? 'Your next module shows how far you’ve come.' : 'Your first module sets your start.'));
    }
    const g = S.gains;
    if (g && g.total) {
      out.append(fact(h('button', { type: 'button', class: 'out' }, h('b', { text: `≈ ${N(g.total)}` }), 'points on the table',
        g.top3 && g.top3.gain ? h('span', { class: 'meta', text: `your top 3 hold ${N(g.top3.gain)}` }) : null), 'points', 'Points on the table'));
    }
    const ck = S.stats.checks;
    if (ck && ck.due) out.append(h('div', { class: 'out' }, h('b', { text: `${N(ck.passed)} / ${N(ck.due)}` }), 'fixes held'));
    if (RO) out.querySelectorAll('button').forEach(b => b.replaceWith(h('div', { class: 'out' }, ...b.childNodes)));
    return out.childNodes.length ? out : null;
  }
  function tiles() {
    const st = S.stats, ser = st.series || {};
    const sum = (a, i, j) => (a || []).slice(i, j).reduce((x, y) => x + (y || 0), 0);
    const wk = k => sum(ser[k], 7, 14), prev = k => sum(ser[k], 0, 7);
    const sign = d => (d > 0 ? '▲' : '▼');
    const delta = (k, f = v => N(v)) => { if (!prev(k)) return null; const d = wk(k) - prev(k); return d ? `${sign(d)} ${f(Math.abs(d))}` : null; };
    const spark = k => (sum(ser[k], 0, 14) ? ser[k] : null);
    const spares = (SHELL && SHELL.spares) || 0;
    const host = h('div', { class: 'stats' });
    const T = o => UI.tile(host, RO ? { ...o, href: null, fact: null } : o);
    T({ label: 'Streak', value: st.streak || null, unit: st.streak ? (st.streak === 1 ? 'day' : 'days') : null,
      sub: st.streak ? [`best ${N(st.best_streak)}`, spares ? `${spares} spare banked` : null].filter(Boolean).join(' · ') : null,
      missing: 'Answer one question to start', fact: 'streak' });
    T({ label: 'Answered', value: st.answered || null, sub: wk('answered') ? `${N(wk('answered'))} this week` : null,
      delta: delta('answered'), spark: spark('answered'), href: '/results/' });
    const accD = prev('answered') && wk('answered') && st.delta && st.delta.accuracy ? `${sign(st.delta.accuracy)} ${Math.abs(st.delta.accuracy)} pts` : null;
    T({ label: 'First-try accuracy', value: st.accuracy ?? null, format: v => `${v}%`,
      sub: st.accuracy7 !== null && st.accuracy7 !== undefined && st.accuracy7 !== st.accuracy ? `${st.accuracy7}% last 7 days` : null,
      delta: accD, spark: (ser.accuracy || []).some(v => v !== null) ? ser.accuracy : null, href: '/results/#skills' });
    T({ label: 'Study time', value: st.minutes_total ? UI.dur(st.minutes_total) : null, sub: st.minutes_week ? `${UI.dur(st.minutes_week)} this week` : null,
      delta: delta('minutes', v => UI.dur(v)), spark: spark('minutes'), fact: 'minutes:week' });
    T({ label: 'Tests', value: st.tests || null, href: '/tests/#history', missing: 'Take a module',
      sub: [st.sections && pl(st.sections, 'section'), st.modules && pl(st.modules, 'module'), st.diagnostics && pl(st.diagnostics, 'diagnostic')].filter(Boolean).join(' · ') || null });
    T({ label: 'Mistakes fixed', value: st.mistakes_fixed || null, sub: st.mistakes_open ? `${N(st.mistakes_open)} open` : null,
      delta: delta('fixed'), spark: spark('fixed'), href: '/review/' });
    const w = S.words;
    T({ label: 'Words', value: w && w.known ? w.known : null, sub: w && w.due ? `${N(w.due)} due` : null, missing: w ? 'Start in Words' : null, href: '/words/' });
    T({ label: 'Rating', value: S.challenge && S.challenge.played ? S.challenge.rating : null, missing: 'Play a contest to get one', href: '/compete/' });
    return host;
  }

  /* ================================================================ This week (U14) */
  PAINT.week = () => {
    if (RO) { const w = S && S.week; if (!w || !w.goals || !w.goals.length) { C.week.el.hidden = true; return; } WEEK = w; }
    if (!ready('week', 'week')) return;
    const goals = WEEK.goals || [];
    const rc = WEEK.receipts || {};
    const receipt = [rc.answered && `${N(rc.answered)} answered`, rc.accuracy !== null && rc.accuracy !== undefined && rc.answered && `${rc.accuracy}% first try`,
      rc.minutes && UI.dur(rc.minutes), rc.fixed && pl(rc.fixed, 'mistake') + ' fixed'].filter(Boolean);
    const list = h('div', { class: 'list' }, goals.map(g => h('div', { class: 'lrow' },
      g.done ? h('span', { class: 'chk', 'aria-hidden': 'true', text: '✓' }) : h('span', { class: 'odot', 'aria-hidden': 'true' }),
      h('div', {}, h('p', { class: 't', text: UI.weekTitle ? UI.weekTitle(g) : g.title }),
        UI.meter(null, { value: Math.min(g.have || 0, g.target || 0), max: g.target || 0, text: `${N(g.have || 0)} / ${N(g.target || 0)}` }).el),
      g.done ? h('span', { class: 'meta', text: 'Met' }) : null)));
    const first = goals.find(g => !g.done);
    fill('week',
      goals.length ? list : h('p', { class: 'soft', text: 'Pick up to three goals for this week. They show on your Profile item as you go.' }),
      receipt.length ? h('p', { class: 'help', text: `Last week: ${receipt.join(' · ')}` }) : null,
      RO ? null : h('div', { class: 'card-foot' },
        first && UI.weekStart ? btn('Start the first', { primary: true, onClick: (e, b) => UI.weekStart(first, b) }) : null,
        btn(goals.length ? 'Change goals' : 'Plan your week', { primary: !goals.length, onClick: () => UI.week && UI.week({ onSaved: w => { WEEK = w; paint('week'); UI.refresh(); } }) })));
    said('week', goals.length ? `${goals.filter(g => g.done).length} / ${goals.length} goals met` : 'No goals yet');
  };

  /* ================================================================ Goals (Shell 3.3, U4) */
  PAINT.goals = () => {
    if (!ready('goals', 'summary', ...(RO ? [] : ['profile']))) return;
    const g = S.goals || {}, prof = P || {};
    const target = RO ? g.subjects.math.target : prof.target;
    const rwT = RO ? g.subjects.rw.target : prof.rw_target;
    const L = g.subjects && g.subjects.math.band || S.score.latest;
    const exam = RO ? g.exam_date : prof.exam_date;
    const plan = RO ? null : prof.plan;
    const rows = h('div', { class: 'rows' });
    // Target: the 1600 total when R&W is set, the Math part on the bar
    const tv = target
      ? (rwT ? [h('b', { text: N(target + rwT) }), ` = Math ${target} + R&W ${rwT}`, h('span', { class: 'soft', text: ' (your R&W estimate)' })]
        : ['Math ', h('b', { text: String(target) })])
      : 'No target yet';
    const tRow = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Target' }), h('span', { class: 'v grow' }, tv),
      btn(target ? 'Edit' : 'Set a target', { quiet: true, aria: 'Edit target', onClick: (e, b) => targetPop(b) }));
    if (target) {
      const x = v => `${Math.max(0, Math.min(100, (v - 200) / 6))}%`;
      tRow.append(h('div', { class: 'gbar', role: 'img', style: 'flex: 1 0 100%',
        'aria-label': L ? `Latest ${band(L)}, target ${target}` : `Target ${target}` },
        L ? h('span', { class: 'bd', style: `left: ${x(L.low)}; width: calc(${x(L.high)} - ${x(L.low)})` }) : null,
        h('span', { class: 'tk', style: `left: ${x(target)}` })));
      const go = L ? target - mid(L) : null;
      tRow.append(h('p', { class: 's' }, L ? `${band(L)} now · ${target} target · ${go > 0 ? `+${go} to go` : 'target reached'}` : 'Your first module shows where you are against it.',
        L && go <= 0 && target < 800 ? [' · ', btn(`Raise to ${Math.min(800, target + 50)}?`, { quiet: true, onClick: () => saveTarget({ target: Math.min(800, target + 50) }) })] : null));
      if (!rwT && !RO) tRow.append(h('p', { class: 's' }, btn('Add your R&W target for a total', { quiet: true, onClick: (e, b) => targetPop(b) })));
      const need = g.need;
      if (need && need.reachable && need.right_of_44) {
        const where = (need.where || []).slice(0, 3).map(tn);
        tRow.append(h('p', { class: 's', text: `What ${target} takes: about ${need.right_of_44} of 44 right` +
          (need.m1_min ? `, with at least ${need.m1_min} of 22 in module 1 to reach the harder module 2` : '') +
          (need.now_of_44 !== null && need.now_of_44 !== undefined ? `. You’re near ${need.now_of_44}.` : '.') +
          (where.length ? ` The ones you’re most likely missing are in ${where.join(', ').replace(/, ([^,]*)$/, ' and $1')}.` : '') }));
      } else if (need && need.reachable === false) {
        tRow.append(h('p', { class: 's', text: `Our score model tops out at ${need.ceiling} for a perfect paper; a ${need.ceiling} puts 800 inside your band.` }));
      }
    }
    rows.append(tRow);
    // Exam date
    const eRow = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Exam' }));
    if (exam) {
      const left = Math.round((new Date(exam + 'T00:00') - new Date(new Date().toDateString())) / 864e5);
      eRow.append(h('span', { class: 'v grow' }, UI.date(exam, 'long'), h('span', { class: 'soft', text: ` · ${left === 0 ? 'today' : pl(left, 'day')}` })));
      eRow.append(btn('Edit', { quiet: true, aria: 'Edit exam date', onClick: (e, b) => examPop(b) }));
      const first = g.first_day;
      if (first && first < exam) {
        const span = (new Date(exam) - new Date(first)) / 864e5, done = (Date.now() - new Date(first)) / 864e5;
        eRow.append(h('div', { class: 'gbar thin', style: 'flex: 1 0 100%', role: 'img', 'aria-label': `${pl(left, 'day')} to go` },
          h('span', { class: 'fill', style: `width: ${Math.max(0, Math.min(100, done / span * 100))}%` })));
      }
      const reg = SHELL && SHELL.registration;
      if (!RO && reg && reg.register_by && reg.registered !== exam) eRow.append(h('p', { class: 's', text: `Register by ${day(reg.register_by)}${reg.late_by ? ` · late ${day(reg.late_by)}` : ''}` }));
    } else {
      eRow.append(h('span', { class: 'v grow soft', text: 'No exam date yet' }), btn('Pick a date', { quiet: true, onClick: (e, b) => examPop(b) }));
    }
    rows.append(eRow);
    const kids = [rows];
    if (!RO && plan) {
      const today = (SHELL && SHELL.today) || {};
      if (prof.minutes) {
        const dRow = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Daily goal' }),
          h('span', { class: 'v grow', text: `${prof.minutes} min a day` }), btn('Edit', { quiet: true, href: '/plan/?step=3', aria: 'Edit daily goal' }));
        dRow.append(h('div', { style: 'flex: 1 0 100%' }, UI.meter(null, { value: today.minutes || 0, max: prof.minutes, unit: 'min', label: 'Today' }).el));
        rows.append(dRow);
      }
      if (prof.days) rows.append(weekRow(prof));
      const focus = prof.focus && (prof.focus.topics || prof.focus.on || []);
      if (focus && focus.length) rows.append(h('div', { class: 'row' }, h('span', { class: 'k', text: 'Focus' }),
        h('span', { class: 'v grow', text: focus.map(tn).join(', ') }), btn('Edit', { quiet: true, href: '/plan/?step=4', aria: 'Edit focus' })));
    } else if (!RO) {
      kids.push(h('div', { class: 'card-foot' }, h('p', { class: 'soft grow', text: 'No plan yet. Four questions, about a minute.' }),
        btn('Build my plan', { primary: true, href: '/plan/' })));
    }
    const time = (UI.prefs.now() || {}).study_time;
    if (!RO && time) rows.append(h('div', { class: 'row' }, h('span', { class: 'k', text: 'Preferred time' }),
      h('span', { class: 'v grow', text: time }), btn('Change', { quiet: true, href: '/me/settings/#study' })));
    fill('goals', kids);
    acts('goals', btn('Open plan', { quiet: true, href: '/plan/' }));
    said('goals', [target ? `Target ${rwT ? target + rwT : target}` : null, exam ? UI.date(exam, 'short') : null].filter(Boolean).join(' · ') || 'No goals yet');
  };
  function weekRow(prof) {
    const ws = (UI.prefs.now() || {}).week_start === 'sun' ? 6 : 0;          // Monday-first days string
    const names = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
    const order = Array.from({ length: 7 }, (_, i) => (i + ws) % 7);
    const study = prof.days.split('').map(c => c === '1');
    const today = new Date(), dow = (today.getDay() + 6) % 7;
    const monday = new Date(today); monday.setDate(today.getDate() - dow);
    const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    const byDay = {};
    ((ACT && ACT.days) || []).forEach(d => { byDay[d.day] = d; });
    let mins = 0;
    const dots = order.map(i => {
      const d = new Date(monday); d.setDate(monday.getDate() + i - (ws && i === 6 ? 7 : 0));
      const r = byDay[iso(d)] || {};
      mins += r.minutes || 0;
      const done = prof.minutes ? (r.minutes || 0) >= prof.minutes : (r.questions || 0) > 0;
      return h('span', { class: [study[i] ? 'study' : 'rest', done ? 'done' : '', i === dow ? 'today' : ''].join(' ').trim(),
        title: `${names[i]}${study[i] ? '' : ' · rest day'}${done ? ' · done' : ''}`, text: names[i][0] });
    });
    const perWeek = (prof.minutes || 0) * study.filter(Boolean).length;
    const r = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Weekly goal' }),
      h('span', { class: 'v grow', text: [perWeek ? UI.dur(perWeek) : null, daysText(study)].filter(Boolean).join(' · ') }));
    if (perWeek) r.append(h('div', { style: 'flex: 1 0 100%' }, UI.meter(null, { value: mins, max: perWeek, label: 'This week', text: `${UI.dur(mins)} of ${UI.dur(perWeek)}` }).el));
    r.append(h('div', { class: 'dots7', role: 'img', 'aria-label': 'This week’s days' }, dots));
    return r;
  }
  function daysText(study) {
    const n = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const on = study.map((v, i) => (v ? i : -1)).filter(i => i >= 0);
    if (on.length === 7) return 'every day';
    const run = on.length > 2 && on[on.length - 1] - on[0] === on.length - 1;
    return run ? `${n[on[0]]}–${n[on[on.length - 1]]}` : on.map(i => n[i]).join(', ');
  }
  async function saveTarget(body) {
    const prof = P || {};
    const old = { target: prof.target, rw_target: prof.rw_target, rw_now: prof.rw_now };
    try {
      P = await A.saveMe(body);
      const t = (P.target || 0) + (P.rw_target || 0);
      UI.toast(`Saved · your plan uses ${t} now`, { undo: async () => { P = await A.saveMe(old); reloadMe(); } });
      reloadMe();
    } catch (x) { UI.toast(x.status === 422 ? A.detail(x) : 'Not saved. Try again.'); }
  }
  function targetPop(anchor) {
    const prof = P || {};
    let t = prof.target || 600, rw = prof.rw_target || null, rwNow = prof.rw_now || null;
    const L = S && S.score.latest;
    UI.pop(anchor, (p, res) => {
      const total = h('p', { class: 'total' });
      const live = h('p', { class: 'help' });
      const save = h('button', { type: 'button', class: 'pill sm', text: 'Save', disabled: true });
      const math = UI.scoreSlider(null, { min: 200, max: 800, step: 10, value: t, label: 'Math target', onInput: v => { t = v; sync(); }, onChange: v => { t = v; sync(); } });
      const chips = UI.chips(null, [600, 650, 700, 750, 800].map(v => ({ value: v, label: String(v) })), { value: t, label: 'Math target',
        onChange: v => { t = v; math.set(v); sync(); } });
      const opts = (none) => [h('option', { value: '', text: none }), ...Array.from({ length: 61 }, (_, i) => 200 + i * 10).map(v => h('option', { value: String(v), text: String(v) }))];
      const rwT = h('select', { class: 'field', 'aria-label': 'R&W target' }, opts('No R&W target'));
      const rwN = h('select', { class: 'field', 'aria-label': 'Your R&W now' }, opts('Not sure'));
      rwT.value = rw ? String(rw) : ''; rwN.value = rwNow ? String(rwNow) : '';
      rwT.addEventListener('change', () => { rw = rwT.value ? +rwT.value : null; sync(); });
      rwN.addEventListener('change', () => { rwNow = rwN.value ? +rwN.value : null; sync(); });
      function sync() {
        total.replaceChildren('Total ', h('b', { text: String(t + (rw || 0)) }));
        total.hidden = !rw;                            // the slider already says the Math part
        live.textContent = L ? (t > mid(L) ? `+${t - mid(L)} from your latest band` : 'At or below your latest band') : '';
        save.disabled = t === prof.target && rw === (prof.rw_target || null) && rwNow === (prof.rw_now || null);
      }
      save.addEventListener('click', () => { res.close(); saveTarget({ target: t, rw_target: rw, rw_now: rwNow }); });
      sync();
      return [h('div', { class: 'target-pop' }, total,
        h('div', { class: 'gap' }, h('span', { class: 'label', text: 'Math' }), math.el, chips.el, live,
          h('a', { class: 'link', href: '/help/#routing', text: 'What a Math target takes' })),
        h('div', { class: 'gap' }, h('span', { class: 'label', text: 'Reading and Writing' }),
          h('label', { class: 'gap' }, h('span', { class: 'help', text: 'Your R&W now' }), rwN),
          h('label', { class: 'gap' }, h('span', { class: 'help', text: 'R&W target' }), rwT),
          h('p', { class: 'help', text: 'R&W is your own estimate for now. Words is our first R&W piece; R&W practice comes later.' })),
        h('div', { class: 'acts' }, save, h('button', { type: 'button', class: 'quiet', text: 'Cancel', onclick: () => res.close() })))];
    }, { label: 'Target' });
  }
  function examPop(anchor) {
    const prof = P || {};
    UI.examDate(anchor, { value: prof.exam_date || null, onSave: async v => {
      const old = prof.exam_date || null;
      P = await A.saveMe({ exam_date: v || null });
      UI.toast(v ? `Exam: ${UI.date(v, 'long')}` : 'Exam date removed', { undo: async () => { P = await A.saveMe({ exam_date: old }); reloadMe(); } });
      reloadMe();
    } });
  }

  /* ================================================================ Snapshot (Shell 3.2, U4, U11) */
  PAINT.snapshot = () => {
    if (!ready('snapshot', 'summary')) return;
    const sc = S.score, L = sc.latest, B = sc.best, prof = P || {};
    const rows = h('div', { class: 'rows' });
    const score = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Math score' }));
    if (L) {
      score.append(h('span', { class: 'grow' }, fact(h('span', { class: 'big', text: band(L), tabindex: RO ? null : '0' }), 'band', 'Math score')),
        L.id && !RO ? h('a', { class: 'link', href: `/results/report/?id=${encodeURIComponent(L.id)}`, text: 'Report' }) : null,
        h('span', { class: 's', text: [KIND[L.kind] || 'Sitting', day(L.at)].join(' · ') }));
      if (B && (B.low !== L.low || B.high !== L.high)) score.append(h('span', { class: 's', text: `Best ${band(B)} · ${day(B.at)}` }));
      const tot = S.goals && S.goals.total;
      if (tot && tot.now_low) score.append(h('span', { class: 's', text: `SAT total ${tot.now_low}–${tot.now_high} · R&W ${S.goals.subjects.rw.now} (yours)` }));
    } else {
      score.append(h('span', { class: 'v grow soft', text: 'No score yet' }),
        h('div', { class: 'acts', style: 'flex: 1 0 100%' }, btn('Take a module · 22 q', { href: '/tests/' }), btn('Diagnostic · 20 q', { quiet: true, href: '/diagnostic/' })));
    }
    rows.append(score);
    // practice ranks: right answers over the last 7 days (R3, U11)
    const R = S.ranks || {};
    const boardHref = scope => `/compete/leaderboard/?metric=right&period=7d${scope ? `&scope=${scope}` : ''}`;
    const rank = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Practice rank' }));
    const rline = (label, r, scope) => {
      if (!r || !r.rank) return null;
      return h('div', { class: 'row', style: 'padding: 6px 0; border: 0' },
        h('span', { class: 'rline' }, `${label} `, h('b', { class: 'n', text: `#${N(r.rank)}` }), ` of ${N(r.of)}`,
          r.move ? h('span', { class: 'meta', text: ` ${r.move > 0 ? '▲' : '▼'} ${Math.abs(r.move)}` }) : null,
          !RO && prof.board === 'hidden' ? h('span', { class: 'soft', text: ' (only you see this)' }) : null),
        btn('Board', { quiet: true, href: boardHref(scope) }),
        r.gap && r.rank > 1 ? h('span', { class: 's', text: `${pl(r.gap, 'right answer')} to pass #${r.rank - 1}` }) : null);
    };
    const lines = [rline('Everyone', R.all), rline(`Sitting ${S.goals && S.goals.exam_date ? day(S.goals.exam_date) : ''}`.trim(), R.exam, 'exam'),
      R.country ? rline(A.countryName(prof.country || ''), R.country, 'country') : null].filter(Boolean);
    if (lines.length) {
      rank.append(h('span', { class: 's', text: 'Right answers in the last 7 days' }), ...lines);
      if (!RO && !prof.country) rank.append(h('span', { class: 's' }, 'Add your country to see your country rank · ',
        btn('Add country', { quiet: true, onClick: (e, b) => countryPop(b) })));
    } else rank.append(h('span', { class: 'v grow soft', text: 'Answer a question this week to be ranked.' }));
    if (R.climb) {
      const c = R.climb;
      rank.append(h('span', { class: 's', text: `${c.window ? `Started ${c.lo}–${c.hi}` : 'Everyone who has sat a module'} · #${N(c.rank)} of ${N(c.of)} by points gained` }));
    }
    if (R.self && R.self.days >= 8) {
      const x = R.self;
      const parts = [x.estimate !== null && x.estimate !== undefined && `${x.estimate >= 0 ? '+' : '−'}${Math.abs(x.estimate)} on your score`,
        x.skills_to_strong && `${pl(x.skills_to_strong, 'skill')} to Strong`, x.fixed && `${pl(x.fixed, 'mistake')} fixed`].filter(Boolean);
      if (parts.length) rank.append(h('span', { class: 's', text: `You, ${x.days} days ago: ${parts.join(' · ')}` }));
    }
    rows.append(rank);
    // the daily challenge
    const ch = S.challenge || {};
    const cParts = [ch.week_rank && `This week #${N(ch.week_rank)}${ch.week_players ? ` of ${N(ch.week_players)}` : ''}`,
      ch.best_rank && `Best day #${N(ch.best_rank)} · ${day(ch.best_day)}`, ch.played && `Played ${N(ch.played)}`].filter(Boolean);
    rows.append(h('div', { class: 'row' }, h('span', { class: 'k', text: 'Daily challenge' }),
      h('span', { class: `v grow${cParts.length ? '' : ' soft'}`, text: cParts.length ? cParts.join(' · ') : 'Not played yet' }),
      cParts.length ? null : btn('Play today’s', { quiet: true, href: '/compete/contest/?id=daily' })));
    const qd = S.stats.qotd || {};
    rows.append(h('div', { class: 'row' }, h('span', { class: 'k', text: 'Question of the day' }),
      qd.answered ? h('span', { class: 'v grow' }, h('b', { text: `${N(qd.right)} / ${N(qd.answered)}` }), ' right', qd.run > 1 ? ` · ${qd.run}-day run` : '')
        : h('span', { class: 'v grow soft', text: 'Not answered yet' }),
      qd.answered ? null : btn('Today’s question', { quiet: true, href: '/#qotd' })));
    fill('snapshot', rows);
    said('snapshot', [L ? band(L) : 'No score yet', R.all && R.all.rank ? `#${N(R.all.rank)} of ${N(R.all.of)}` : null].filter(Boolean).join(' · '));
  };
  function countryPop(anchor) {
    UI.pop(anchor, (p, res) => [h('div', { class: 'pop-form' }, h('span', { class: 'label', text: 'Country' }),
      A.countrySelect((P || {}).country || '', async v => {
        try { P = await A.saveMe({ country: v }); res.close(); UI.toast(v ? `Country: ${A.countryName(v)}` : 'Country cleared'); loadSummary(); }
        catch (x) { UI.toast('Not saved. Try again.'); throw x; }
      }),
      h('p', { class: 'help', text: 'Shown on the Country board. Change or clear it in Settings › Account & devices. We never detect where you are.' }))],
    { label: 'Country' });
  }

  /* ================================================================ Saved & in progress (Shell 3.12, R31) */
  PAINT.saved = () => {
    if (!ready('saved', 'summary')) return;
    const st = S.stats, w = S.words || {}, sh = SHELL || {};
    const rows = h('div', { class: 'rows' });
    const part = (label, n, ...a) => { if (n) rows.append(h('div', { class: 'row' }, h('span', { class: 'v grow' }, `${label} `, h('b', { text: N(n) })), ...a)); };
    part('Saved questions', st.saved, btn('Practise saved', { body: { pool: 'saved', exact: true, source: 'review' } }), btn('See all', { quiet: true, href: '/review/?tab=saved' }));
    part('Saved words', w.saved, btn('Review them', { href: '/words/?s=saved' }));
    part('Marked for review', sh.review && sh.review.marked, btn('Practise marked', { body: { pool: 'marked', source: 'review' } }));
    part('Open mistakes', st.mistakes_open, btn('Fix all', { body: { pool: 'redo', source: 'mistakes' } }));
    (S.resume || []).slice(0, 3).forEach(r => {
      const left = r.seconds_left ? ` · ${Math.ceil(r.seconds_left / 60)} min left` : '';
      rows.append(h('div', { class: 'row' }, h('span', { class: 'v grow', text: `${KIND[r.kind] || 'Set'} · ${N(r.answered)} / ${N(r.total)} answered${left}` }),
        btn('Resume', { primary: true, href: r.href || `/practice/session/?id=${encodeURIComponent(r.id)}` })));
    });
    fill('saved', rows.childNodes.length ? rows : h('p', { class: 'soft', text: 'Nothing saved or in progress.' }),
      h('div', { class: 'card-foot' }, btn('Log a missed question', { quiet: true, onClick: () => UI.quick('mistake') })));
    said('saved', [st.saved && `${N(st.saved)} saved`, st.mistakes_open && `${N(st.mistakes_open)} open`].filter(Boolean).join(' · ') || 'Nothing saved');
  };

  /* ================================================================ Account (Shell 3.13, U19, U21) */
  PAINT.account = () => {
    if (!ready('account', 'account')) return;
    const kids = [];
    if (ACC.saved) {
      const ways = [PK && PK.items && PK.items.length ? 'passkey' : null, ACC.verified ? 'email' : null, ACC.google ? 'Google' : null].filter(Boolean);
      kids.push(h('p', {}, ways.length ? `You can sign in ${ways.length === 1 ? 'one way' : `${ways.length} ways`}: ${ways.join(', ')}` : 'Your progress is saved.'));
      if (ways.length === 1) kids.push(h('p', { class: 'help' }, h('span', { class: 'odot', 'aria-hidden': 'true' }),
        h('a', { class: 'link', href: '/me/settings/#account', text: ways[0] === 'email' ? 'Add a passkey' : 'Add an email' }), ' so you can’t get locked out.'));
      const live = DEV && DEV.items ? DEV.items.filter(d => !d.revoked).length : 0;
      if (live > 1) kids.push(h('p', {}, h('a', { class: 'link', href: '/me/settings/#devices', text: `Signed in on ${live} devices` })));
      kids.push(h('div', { class: 'card-foot' }, btn('Manage', { href: '/me/settings/#account' }),
        btn([ic('signout'), ' Sign out'], { quiet: true, onClick: () => UI.signOut() })));
    } else {
      const save = h('div', { class: 'acts', style: 'margin-top: 14px' });
      kids.push(h('p', { text: 'This device only. Clearing this browser loses it.' }), save,
        h('div', { class: 'card-foot' }, btn('Use it on another device', { quiet: true, href: '/pair/' }),
          btn('Share with a parent or tutor', { quiet: true, href: '/me/settings/#privacy' }),
          btn('Leave this device…', { quiet: true, onClick: () => UI.signOut() })));
      A.passkeyReady().then(ok => {
        save.replaceChildren(...[ok ? btn('Save with a passkey', { primary: true, onClick: (e, b) => savePasskey(b) }) : null,
          btn(ok ? 'Save by email' : 'Save progress', { primary: !ok, href: '/me/settings/#account' })].filter(Boolean));
      });
    }
    fill('account', kids);
    said('account', ACC.saved ? 'Saved' : 'This device only');
  };
  async function savePasskey(b) {
    b.setAttribute('aria-busy', 'true');
    try {
      await A.savePasskey();
      UI.toast('Saved. This passkey signs you in wherever your passwords sync.');
      loadAccount();
    } catch (e) {
      if (!e || e.name !== 'NotAllowedError') UI.toast('Couldn’t save a passkey here. Try email instead.');
    } finally { b.removeAttribute('aria-busy'); }
  }

  /* ================================================================ Learning preferences (Shell 3.4, U15, R31) */
  let prefsBuilt = false;
  PAINT.prefs = () => {
    if (RO || prefsBuilt) return;
    prefsBuilt = true;
    const main = h('div', { class: 'set-sec' }), tests = h('div', { class: 'set-sec' });
    const stageLine = h('p', { class: 'help' });
    ['mode', 'stage_auto', 'set_length', 'clock', 'tiers', 'adaptive', 'rationale', 'calc_button', 'words_goal', 'words_from'].forEach(k => UI.prefRow(main, k));
    ['test_timing', 'test_calculator', 'test_pace', 'test_confidence', 'test_reveal_route', 'test_fullscreen'].forEach(k => UI.prefRow(tests, k));
    const stage = () => {
      const s = SHELL && SHELL.stage;
      const names = { learn: 'Learn', build: 'Build', test: 'Test-like', final: 'Final week' };
      stageLine.textContent = s && s.name ? [names[s.name] || s.name, s.days_to_exam !== undefined && s.days_to_exam !== null ? `${pl(s.days_to_exam, 'day')} to your exam` : null,
        s.next && s.next.on ? `${names[s.next.name] || s.next.name} starts ${day(s.next.on)}` : null].filter(Boolean).join(' · ') : '';
      stageLine.hidden = !stageLine.textContent;
    };
    stage();
    UI.onShell(stage);
    fill('prefs', stageLine, main, h('h3', { class: 'sub-h', text: 'Tests' }), tests,
      h('div', { class: 'card-foot' }, btn('All settings', { quiet: true, href: '/me/settings/' })));
    said('prefs', 'Mode, set length, clock, difficulty and test defaults');
  };

  /* ================================================================ Skills (Shell 3.5, U4, U5) */
  let skillView = ls.get('satf.me.skills', null);
  const openDoms = new Set(ls.get('satf.me.doms', []));
  PAINT.skills = () => {
    if (!ready('skills', 'summary')) return;
    const g = S.gains;
    const byTopic = {};
    S.domains.forEach(d => d.skills.forEach(s => { byTopic[s.topic] = s; }));
    const view = g ? (skillView || 'points') : 'domain';
    const answered = Object.values(byTopic).filter(s => s.answered);
    const sorted = answered.slice().sort((a, b) => a.mastery - b.mastery);
    const head = [];
    if (g && !RO) {
      const segHost = h('div');
      UI.seg(segHost, [{ value: 'points', label: 'By points' }, { value: 'domain', label: 'By domain' }], { value: view, label: 'Order skills',
        onChange: v => { skillView = v; ls.set('satf.me.skills', v); paint('skills'); } });
      head.push(segHost);
    }
    head.push(btn('All skills in Results', { quiet: true, href: '/results/#skills' }));
    acts('skills', ...head);
    const row = (s, extra = {}) => {
      const el = UI.skillRow(null, { topic: s.topic, name: tn(s.topic), mastery: s.mastery, answered: s.answered, right: s.right, open: s.traps, ...extra },
        { practise: RO ? null : { count: setLen(), label: `Practise · ${setLen()}`, body: { topics: [s.topic], count: setLen(), adaptive: true, source: 'skill' } },
          href: RO ? null : `/results/#${s.topic}` });
      // "Not started" already says it: the kit's "no answers yet" beside it is the same fact twice (decision 7)
      if (!s.answered) { const m = el.querySelector('.skill-m .meta'); if (m) m.remove(); }
      return [el, more(s)];
    };
    function more(s) {
      const bits = [];
      if (s.trend14 !== null && s.trend14 !== undefined && Math.abs(s.trend14) >= 0.05) bits.push(h('span', { text: `${s.trend14 > 0 ? '▲' : '▼'} 14 days` }));
      if (s.last5 && s.last5.length) bits.push(h('span', { class: 'last5', role: 'img', 'aria-label': `Last ${s.last5.length}: ${s.last5.map(x => (x ? 'right' : 'wrong')).join(', ')}` },
        s.last5.map(x => h('i', { class: x ? 'y' : 'n', text: x ? '✓' : '✕' }))));
      if (s.fading && !RO) bits.push(h('span', { text: `Fading${s.last ? ` · last ${day(s.last)}` : ''}` }), btn('Keep warm · 3', { quiet: true, body: { pool: 'review', topics: [s.topic], count: 3, source: 'review' } }));
      if (s.answered && s.answered < 5 && !RO) bits.push(btn('Try 5 more', { quiet: true, body: { topics: [s.topic], count: 5, source: 'skill' } }));
      return bits.length ? h('div', { class: 'sk-x' }, bits) : null;
    }
    const kids = [];
    if (!g && !RO) kids.push(h('p', { class: 'help', style: 'margin: 0 0 12px' }, 'Answer 30 questions and this shows where your points are. ',
      btn(`Today’s set · ${setLen()}`, { quiet: true, body: { source: 'coach', count: setLen() } })));
    // Sharpen (U5): 12 questions over the 4-6 skills with the most test weight and the fewest answers
    const nOf = s => s.evidence ?? s.answered ?? 0;
    const thin = Object.values(byTopic).filter(s => nOf(s) < 10);
    if (thin.length && S.stats.answered && !RO) {
      const share = t => ((g && g.skills.find(x => x.topic === t)) || {}).per_test || 1;
      const topics = thin.map(s => [s.topic, share(s.topic) * (1 - nOf(s) / 10)]).sort((a, b) => b[1] - a[1]).slice(0, 6).map(x => x[0]);
      kids.push(h('p', { class: 'help sharpen' }, `${thin.length === 1 ? '1 skill needs' : `${thin.length} skills need`} more answers. `,
        btn('Sharpen · 12 questions · ~19 min', { quiet: true, body: { source: 'probe', topics, count: 12, order: 'mixed' } })));
    }
    if (view === 'points') {
      const ranked = g.skills.filter(x => x.evidence >= 5 && byTopic[x.topic]).sort((a, b) => b.gain - a.gain);
      ranked.forEach((x, i) => {
        const [el, ex] = row(byTopic[x.topic], { gain: x.gain, per_test: x.per_test, need_right: x.to_strong, minutes: x.minutes, accuracy: x.accuracy });
        if (i === 0 && x.gain >= 5) { const side = el.querySelector('.skill-side'); if (side) side.prepend(h('span', { class: 'badge', text: 'Most points' })); }
        kids.push(el, ex);
      });
      const rest = Object.values(byTopic).filter(s => !ranked.some(x => x.topic === s.topic));
      const started = rest.filter(s => s.answered), fresh = rest.filter(s => !s.answered);
      if (started.length) {
        kids.push(h('p', { class: 'k', style: 'margin: 18px 0 4px', text: 'Five answers each show their points' }));
        started.forEach(s => kids.push(...row(s)));
      }
      if (fresh.length) kids.push(h('details', { class: 'skills-rest' }, h('summary', { text: `${pl(fresh.length, 'skill')} not started` }),
        fresh.map(s => row(s)[0])));
      if (g.top3 && g.top3.topics && g.top3.topics.length && !RO) kids.push(h('div', { class: 'card-foot' },
        btn('Practise the top 3 · 15', { primary: true, body: { topics: g.top3.topics, count: 15, order: 'mixed', adaptive: true, source: 'skill' } })));
    } else {
      S.domains.forEach(d => {
        const weak = d.skills.filter(s => s.answered).sort((a, b) => a.mastery - b.mastery)[0];
        const open = openDoms.has(d.domain);
        const box = h('div', { class: 'dom', 'data-open': open ? '' : null });
        const hd = h('button', { type: 'button', class: 'dom-h', 'aria-expanded': String(open) },
          h('span', { class: 'nm', text: d.domain }),
          h('span', { class: 'mbar6', role: 'img', 'aria-label': `${d.domain}: ${UI.masteryWord(d.mastery, d.answered)}` }, h('i', { style: `--m: ${d.mastery || 0}` })),
          h('span', { class: 'meta', text: d.answered ? `${N(d.answered)} answered · ${pct(d.right / d.answered)} right` : 'Not started' }),
          weak ? h('span', { class: 'weak', text: `Weakest: ${tn(weak.topic)}` }) : null);
        hd.addEventListener('click', () => {
          if (!phone()) return;
          const on = !box.hasAttribute('data-open');
          box.toggleAttribute('data-open', on); hd.setAttribute('aria-expanded', String(on));
          if (on) openDoms.add(d.domain); else openDoms.delete(d.domain);
          ls.set('satf.me.doms', [...openDoms]);
        });
        box.append(hd);
        d.skills.forEach(s => box.append(...row(s).filter(Boolean)));
        kids.push(box);
      });
    }
    fill('skills', kids);
    if (sorted.length >= 2) {
      const best = sorted[sorted.length - 1], worst = sorted[0];
      said('skills', `Weakest ${tn(worst.topic)} ${pct(worst.right / worst.answered)} · strongest ${tn(best.topic)}`);
    } else said('skills', answered.length ? `${tn(answered[0].topic)} started` : 'Not started');
  };

  /* ================================================================ Test-day readiness (U8) */
  PAINT.readiness = () => {
    if (!ready('readiness', 'summary', 'types')) return;
    const cov = S.subjects.math.coverage || {};
    const types = cov.types || {};
    const counts = { unmet: 0, met: 0, ready: 0 };
    const gaps = [];
    const grid = h('div', { role: 'grid', 'aria-label': 'Question types by skill' });
    UI.DOMAINS.forEach(([dom]) => {
      const topics = UI.TOPICS.filter(t => t.domain === dom);
      const box = h('div', { class: 'ready-dom' }, h('span', { class: 'k', text: dom }));
      topics.forEach(t => {
        const list = (TYPES.byTopic[t.slug] || []).map(x => {
          const c = types[x.template] || {};
          const status = (c.right || 0) >= 2 ? 'ready' : c.met ? 'met' : 'unmet';
          counts[status] += 1;
          if (status !== 'ready') gaps.push(x.template);
          return { template: x.template, label: x.name, status, open: c.open || null, c };
        }).sort((a, b) => ({ unmet: 0, met: 1, ready: 2 }[b.status] - { unmet: 0, met: 1, ready: 2 }[a.status]));
        if (!list.length) return;
        const at = UI.atlas(null, list, { sm: true, label: tn(t.slug),
          tip: x => [x.label, x.c.met ? `met ${x.c.met} · right ${x.c.right || 0}` : 'not met yet', x.c.last ? `last ${day(x.c.last)}` : null, x.open ? 'open mistake' : null].filter(Boolean).join(' · '),
          onPick: RO ? null : x => typeSheet(x) });
        const nReady = list.filter(x => x.status === 'ready').length, unmet = list.filter(x => x.status === 'unmet').length;
        box.append(h('div', { class: 'atlas-row' }, h('span', {}, tn(t.slug),
          unmet ? btn(`Practise ${Math.min(unmet, setLen())} unmet`, { quiet: true, body: { topics: [t.slug], pool: 'untried', count: Math.min(unmet, setLen()), source: 'map' } }) : null),
          at.el, h('span', { text: `${nReady} / ${list.length} ready` })));
      });
      grid.append(box);
    });
    const legend = h('div');
    UI.legend(legend, ['unmet', 'met', 'ready'], counts);
    const total = counts.unmet + counts.met + counts.ready;
    const readyPct = Math.round((cov.readiness || 0) * 100);
    fill('readiness',
      h('p', { class: 'acts' }, fact(h('span', { class: 'big', text: `${readyPct}%`, tabindex: RO ? null : '0' }), 'readiness', 'Test-day readiness'),
        h('span', { class: 'meta', text: `${N(counts.met + counts.ready)} of ${N(total)} question types met` })),
      legend, grid,
      RO ? null : h('div', { class: 'card-foot' }, gaps.length
        ? btn('Practise my biggest gaps', { primary: true, body: { templates: gaps.slice(0, Math.min(120, setLen())), count: setLen(), source: 'map' } })
        : h('p', { class: 'soft', text: 'Every type ready.' })));
    said('readiness', `${readyPct}% ready · ${N(counts.met + counts.ready)} of ${N(total)} types met`);
  };
  function typeSheet(x) {
    UI.sheet({ title: x.label, size: 'm',
      body: b => {
        b.append(UI.skel(null, 'lines:4'));
        UI.api(`/types/${encodeURIComponent(x.template)}/example`).then(r => {
          const q = r.question || {};
          b.replaceChildren(h('p', { class: 'k', text: 'An example, new numbers each time' }),
            q.figure ? h('div', { class: 'ex-fig', html: q.figure }) : null,
            h('div', { class: 'ex-q' }, h('p', { text: q.stem || '' }), q.choices ? h('ol', { type: 'A' }, q.choices.map(c => h('li', { text: c }))) : null),
            h('p', { class: 'help', text: [x.c.met ? `Met ${x.c.met} · right ${x.c.right || 0}` : 'Not met yet', x.open ? 'an open mistake' : null].filter(Boolean).join(' · ') }));
        }, () => b.replaceChildren(h('p', { class: 'soft', text: 'Couldn’t load an example.' })));
      },
      actions: [{ label: 'Log a mistake on it', onClick: () => { UI.quick('mistake'); } },
                { label: 'Practise 5 of this type', primary: true, onClick: () => start({ templates: [x.template], count: 5, source: 'map' }).then(() => false) }] });
  }

  /* ================================================================ Score trend (Shell 3.6, U9) */
  PAINT.trend = () => {
    if (!ready('trend', 'summary')) return;
    const pts = (S.score.points || []).map(p => ({ id: p.session || p.id, at: p.at, low: p.low, high: p.high, kind: p.kind === 'outside' ? 'outside' : p.kind,
      label: KIND[p.kind] || 'Sitting', href: !RO && (p.session || p.id) && p.kind !== 'outside' ? `/results/report/?id=${encodeURIComponent(p.session || p.id)}` : null }));
    const host = h('div');
    fill('trend', host);
    const g = S.goals || {};
    const o = { height: phone() ? 160 : 200, target: g.subjects && g.subjects.math.target, exam: g.exam_date,
      empty: { text: 'Your first module puts a point here.', action: RO ? null : { label: 'Start a module', href: '/tests/' } },
      onPick: p => { if (p.href) location.href = p.href; }, label: 'Math score over time' };
    if (S.score.projection !== undefined) o.projection = pts.length ? S.score.projection : undefined;
    if (S.score.gaps) o.gaps = S.score.gaps;
    UI.bandChart(host, pts, o);
    said('trend', pts.length ? pl(pts.length, 'scored sitting') : 'No sittings yet');
  };

  /* ================================================================ Pace (U7) */
  PAINT.pace = () => {
    if (!ready('pace', 'summary')) return;
    const pc = S.subjects && S.subjects.math.pace;
    const skills = pc && pc.skills ? Object.entries(pc.skills).filter(([, v]) => v && v.n >= 5) : [];
    if (skills.length < 3) {
      fill('pace', h('p', { class: 'soft', text: 'Answer with the clock on to see where your minutes go.' }),
        h('div', { class: 'card-foot' }, btn('Timed set · 10', { primary: true, body: { count: 10, timing: 'pace', source: 'skill' } })));
      said('pace', 'Not enough timed answers yet');
      return;
    }
    const f = pc.forecast || {};
    const head = f.seconds ? `At your pace a module takes ${UI.mmss(f.seconds)} of 35:00${f.blanks ? `: about ${pl(f.blanks, 'question')} left blank` : ''}.` : '';
    const host = h('div');
    const QN = { slow_right: ['You know it, slowly', 'Speed drill · 8', t => ({ topics: [t], count: 8, timed: true, minutes: 9, source: 'skill' })],
      fast_wrong: ['Rushing', 'Careful set · 8', t => ({ topics: [t], count: 8, feedback: 'instant', source: 'skill' })],
      slow_wrong: ['Time sink', 'Learn it untimed · 8', t => ({ topics: [t], count: 8, source: 'skill' })],
      fast_right: ['Banked', 'Keep warm · 3', t => ({ pool: 'review', topics: [t], count: 3, source: 'review' })] };
    const points = skills.map(([t, v]) => ({ id: t, topic: t, label: tn(t), x: (v.median_ms || v.ms || 0) / 1000, y: v.accuracy, n: v.n }));
    fill('pace', head ? h('p', { text: head }) : null, host,
      pc.guess && pc.guess.n >= 20 ? h('p', { class: 'help', text: `Your guesses are right ${Math.round(100 * pc.guess.right / pc.guess.n)}% of the time (chance is 25%).` }) : null,
      pc.struck2 && pc.struck2.n >= 20 ? h('p', { class: 'help', text: `When you strike two options first you’re right ${Math.round(100 * pc.struck2.right / pc.struck2.n)}%: strike, then guess.` }) : null,
      h('div', { class: 'card-foot' }, btn('Pacing drill · 11 q · 17 min', { primary: true, body: { mix: 'blueprint', count: 11, timed: true, minutes: 17, source: 'skill' } })));
    if (UI.quadrant) UI.quadrant(host, points, { x: 'seconds', xRef: 95, y: 'accuracy', label: 'Seconds and accuracy by skill',
      names: Object.fromEntries(Object.entries(QN).map(([k, v]) => [k, v[0]])),
      action: RO ? null : (p, q) => (QN[q] ? { label: QN[q][1], onClick: () => start(QN[q][2](p.topic)) } : null) });
    said('pace', head || `${skills.length} skills timed`);
  };

  /* ================================================================ What keeps catching you (Shell 3.7, U6) */
  PAINT.catching = () => {
    if (!ready('catching', 'summary')) return;
    const list = S.catching || [];
    acts('catching', list.length ? btn('Trap gauntlet · 10', { body: { source: 'gauntlet', count: 10 } }) : null);
    fill('catching', list.length ? h('div', { class: 'list' }, list.map(x => h('div', { class: 'lrow' },
      x.open ? h('span', { class: 'odot', 'aria-label': 'Open', style: 'margin-top: 6px' }) : h('span', { class: 'chk', 'aria-label': 'Fixed', text: '✓' }),
      h('div', {}, h('p', { class: 't', text: x.label || x.reason || 'A named mistake' }),
        h('p', { class: 'd' }, tag(x.topic), h('span', { text: `×${N(x.hits)}` }), x.last ? h('span', { text: `last ${day(x.last)}` }) : null,
          x.source === 'outside' ? h('span', { text: 'Logged by you' }) : null)),
      h('span', { class: 'lside' }, btn('Practise', { body: { templates: [x.template], count: 3, source: 'mistakes' } }))))) :
      h('p', { class: 'soft', text: 'No mistakes yet. When you miss, the mistake gets a name here.' }),
      list.length && !RO ? h('div', { class: 'card-foot' }, btn('All mistakes', { quiet: true, href: '/review/' })) : null);
    said('catching', list.length ? list[0].label || '' : 'No mistakes yet');
  };

  /* ================================================================ Your habits (U6) */
  PAINT.habits = () => {
    if (!ready('habits', 'summary')) return;
    const list = (S.habits || S.subjects.math.habits || []).slice(0, 3);
    fill('habits', list.length ? h('div', { class: 'list' }, list.map(x => h('div', { class: 'lrow' },
      h('span', { class: 'ic' }, ic('dot', 12)),
      h('div', {}, h('p', { class: 't', text: x.name }),
        h('p', { class: 'd' }, h('span', { text: `${pl(x.misses, 'miss', 'misses')}${(x.skills || []).length > 1 ? ` across ${pl(x.skills.length, 'skill')}` : ''}` }),
          // the change against the 30 days before, only when there was a before
          x.trend && x.trend !== x.misses ? h('span', { text: x.trend < 0 ? `↓ ${Math.abs(x.trend)} fewer` : `↑ ${x.trend} more` }) : null),
        h('p', { class: 'd' }, (x.skills || []).map(tag)),
        x.tell ? h('p', {}, h('em', { text: x.tell })) : null),
      h('span', { class: 'lside' }, btn('Drill this habit · 8', { body: { source: 'habit', habit: x.id, count: 8 } }))))) :
      h('p', { class: 'soft', text: 'Miss a few questions and the habits behind them show up here.' }));
    said('habits', list.length ? list[0].name : 'No habits yet');
  };

  /* ================================================================ Achievements (Shell 3.8, R25, U13) */
  const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'];
  const lastAt = a => (a.earned || []).reduce((m, e) => (e && e.at > m ? e.at : m), '');
  function badgeIcon(a, on) {
    const inner = UI.TOPIC[a.icon] ? UI.glyph(a.icon) : ic(UI.ICON[a.icon] ? a.icon : 'trophy', 22);
    return h('span', { class: 'bcirc' + (on ? ' on' : ''), 'aria-hidden': 'true' }, inner);
  }
  function badgeTile(a) {
    const on = !!(a.earned && a.earned.length);
    const tierN = on ? a.earned.length : 0;
    return h('div', { class: 'btile' }, badgeIcon(a, on),
      h('p', { class: 'nm' }, a.name, tierN ? h('span', { class: 'meta', text: ` ${ROMAN[tierN - 1] || tierN}` }) : null),
      a.next ? [h('span', { class: 'meta', text: `${N(a.have || 0)} / ${N(a.next)}` }),
        h('span', { class: 'bprog', role: 'img', 'aria-label': `${N(a.have || 0)} of ${N(a.next)}` }, h('i', { style: `--p: ${Math.min(1, (a.have || 0) / a.next)}` }))] : null,
      on ? h('span', { class: 'meta', text: day(lastAt(a)) }) : null,
      a.next && a.go ? goBtn(a) : null);
  }
  function goBtn(a) {
    const g = a.go;
    return btn(`Go · ${g.label}`, { quiet: true, href: g.href || null, body: g.href ? null : g.body });
  }
  PAINT.badges = () => {
    if (!ready('badges', 'summary')) return;
    const all = S.achievements || [];
    const earned = all.filter(a => a.earned && a.earned.length).sort((a, b) => (lastAt(a) < lastAt(b) ? 1 : -1)).slice(0, 3);
    const close = all.filter(a => a.next && !earned.includes(a)).sort((a, b) => (b.have || 0) / b.next - (a.have || 0) / a.next).slice(0, 6 - earned.length);
    acts('badges', btn(`View all (${all.length})`, { quiet: true, onClick: () => allBadges(all) }));
    fill('badges', h('div', { class: 'bgrid' }, [...earned, ...close].map(badgeTile)));
    said('badges', `${all.filter(a => a.earned && a.earned.length).length} of ${all.length} earned`);
  };
  function allBadges(all) {
    let show = 'all';
    UI.sheet({ title: `Achievements (${all.length})`, size: 'l', body: b => {
      const list = h('div');
      const chipHost = h('div');
      const draw = () => {
        const pick = all.filter(a => show === 'all' || (show === 'earned' ? a.earned && a.earned.length : a.next && !(a.earned && a.earned.length)));
        const groups = {};
        pick.forEach(a => { (groups[a.group || 'Other'] = groups[a.group || 'Other'] || []).push(a); });
        list.replaceChildren(...Object.entries(groups).map(([g, items]) => h('section', {}, h('h3', { class: 'sub-h', text: g }),
          items.map(a => h('div', { class: 'brow' }, badgeIcon(a, a.earned && a.earned.length),
            h('div', { class: 'gap', style: 'gap: 4px' }, h('p', { class: 'nm', style: 'font: 600 14.5px var(--font)', text: a.name }),
              a.rule && a.rule !== a.name ? h('p', { class: 'help', style: 'margin: 0', text: a.rule }) : null,
              h('p', { class: 'ladder' }, (a.tiers || []).map((t, i) => h('span', { class: i < (a.earned || []).length ? 'on' : '', text: N(t) }))),
              (a.earned || []).length ? h('p', { class: 'meta', text: (a.earned || []).map(e => day(e.at)).filter(x => x !== '—').join(' · ') }) : null,
              a.next && a.go ? goBtn(a) : null))))));
        if (!pick.length) list.replaceChildren(h('p', { class: 'soft', text: show === 'earned' ? 'None earned yet.' : 'Nothing in progress.' }));
      };
      UI.chips(chipHost, [{ value: 'all', label: 'All' }, { value: 'earned', label: 'Earned' }, { value: 'progress', label: 'In progress' }],
        { value: show, label: 'Show', onChange: v => { show = v; draw(); } });
      draw();
      b.append(chipHost, list);
    } });
  }

  /* ================================================================ Activity (Shell 3.9, U16) */
  PAINT.activity = () => {
    if (RO) {
      if (!S || !S.days) { C.activity.el.hidden = true; return; }
      ACT = ACT || { days: S.days, active_days: S.stats.active_days };
    }
    if (!ready('activity', 'activity')) return;
    const host = h('div');
    fill('activity', host);
    UI.heatmap(host, ACT.days, { weeks: phone() ? 20 : weeks, end: ACT.today, range: !RO,
      onRange: async w => {
        weeks = w; ls.set('satf.me.weeks', w);
        try { ACT = await UI.api(`/me/activity?weeks=${w}`); return ACT.days; } catch (_) { UI.toast('Couldn’t load that range.'); return null; }
      }, stats: { active_days: ACT.active_days }, label: 'Questions answered each day' });
    said('activity', ACT.active_days ? pl(ACT.active_days, 'active day') : 'No activity yet');
  };

  /* ================================================================ Recent activity (Shell 3.10, U12, U25) */
  const FILTERS = [['all', 'All'], ['practice', 'Practice'], ['test', 'Tests'], ['mistakes', 'Mistakes'], ['challenge', 'Challenge'],
    ['achievements', 'Achievements'], ['unread', 'Unread']];
  const FEED_ICON = { practice: 'practice', test: 'tests', challenge: 'trophy', mistakes: 'review', achievements: 'trophy', reports: 'chat', goal: 'check', correction: 'check' };
  const score = t => String(t || '').replace(/^(\d+) of (\d+) right$/, '$1 / $2');
  const hrefOf = x => (x.href ? x.href.replace(/^\/results\/report\/\?s=/, '/results/report/?id=').replace(/^\/me\/\?tab=achievements$/, '#badges') : null);
  function dayHead(at) {
    const d = new Date(at), t = new Date();
    const k = x => x.toDateString();
    const y = new Date(t); y.setDate(t.getDate() - 1);
    return k(d) === k(t) ? 'Today' : k(d) === k(y) ? 'Yesterday' : UI.date(at, 'long');
  }
  PAINT.recent = () => {
    if (RO) { FEED.items = FEED.items || (S && S.feed) || []; }
    if (!ready('recent', 'feed')) return;
    if (!RO) {
      const chipHost = h('div');
      UI.chips(chipHost, FILTERS.map(([v, l]) => ({ value: v, label: l, n: v === 'unread' && FEED.unread ? FEED.unread : undefined })),
        { value: FEED.kind, label: 'Show', onChange: v => { FEED.kind = v; FEED.next = null; loadFeed(true); } });
      acts('recent');
      C.recent.chips = chipHost;
    }
    const kids = [];
    let lastHead = '';
    FEED.items.forEach(x => {
      const head = x.at ? dayHead(x.at) : '';
      if (head && head !== lastHead) { kids.push(h('p', { class: 'k feed-day', text: head })); lastHead = head; }
      const href = RO ? null : hrefOf(x);
      const e = x.effect || {};
      const eff = [...(e.words || []).map(w => `${tn(w.topic)}: ${w.from} → ${w.to}`), e.fixed && `${pl(e.fixed, 'mistake')} fixed`,
        e.opened && `${N(e.opened)} opened`, e.pts && Math.abs(e.pts) >= 5 && `≈ ${e.pts > 0 ? '+' : '−'}${Math.abs(e.pts)} pts`].filter(Boolean);
      const title = x.kind === 'achievements' && !/^Earned/.test(x.title || '') ? `Earned: ${x.title}` : x.title;
      kids.push(h('div', { class: 'lrow' }, h('span', { class: 'ic' }, ic(FEED_ICON[x.kind] || 'dot')),
        h('div', {}, href ? h('a', { class: 't feed-link', href, text: title }) : h('p', { class: 't', text: title }),
          x.detail ? h('p', { class: 'd', text: score(x.detail) }) : null,
          eff.length ? h('p', { class: 'd', text: eff.join(' · ') }) : null),
        href ? h('a', { class: 'ibtn feed-go', href, tabindex: '-1', 'aria-hidden': 'true', html: UI.svg(UI.ICON.chev, 16) }) : h('span'),
        RO || (!x.again && !x.follow_up) ? null : h('div', { class: 'fx' },
          x.again ? btn('Again · new numbers', { quiet: true, body: { ...x.again, source: 'review' } }) : null,
          x.follow_up ? btn(`Follow up · ${Math.min(3, e.opened || 3)}`, { quiet: true, body: { ...x.follow_up, source: 'review' } }) : null)));
    });
    const empty = FEED.kind === 'unread' ? h('p', { class: 'soft', text: 'Nothing new since you last looked.' })
      : h('div', { class: 'gap' }, h('p', { class: 'soft', text: 'Nothing yet. Your first set shows up here.' }),
        btn(`Start today’s set · ${setLen()}`, { primary: true, body: { source: 'coach', count: setLen() } }));
    fill('recent', C.recent.chips || null, h('div', { class: 'list', style: 'margin-top: 12px' }, kids.length ? kids : empty),
      FEED.next && !RO ? h('div', { class: 'card-foot' }, btn('Show more', { onClick: (ev, b) => { b.setAttribute('aria-busy', 'true'); loadFeed(false); } })) : null);
    said('recent', FEED.items.length ? FEED.items[0].title : 'Nothing yet');
  };

  /* ---- a signed-out device paints none of the student's data (Shell 3 States) */
  addEventListener('satf:retired', () => CARDS.forEach(c => fill(c.id, h('p', { class: 'soft' }, 'This device was signed out. ',
    h('a', { class: 'link', href: '/signin/', text: 'Sign in' }), ' to see your progress.'))));

  /* ---- go */
  if (RO) {
    UI.api(`/shared/${encodeURIComponent(SHARE)}`).then(d => {
      S = d;
      if (window.ME_SHARED) window.ME_SHARED(d);
      CARDS.forEach(c => paint(c.id));
      loadTypes();
    }, e => { if (window.ME_SHARED) window.ME_SHARED(null, e); });
    return;
  }
  UI.shell({ page: 'me', sections: CHIPS.filter(id => C[id]).map(id => ({ id, label: (CARDS.find(c => c.id === id).chip) || CARDS.find(c => c.id === id).title })) });
  UI.onShell(d => { SHELL = d; paint('you', 'goals', 'saved'); });
  loadSummary(); loadProfile(); loadAccount(); loadActivity(); loadWeek(); loadTypes(); loadFeed(true);
  paint('prefs');
  // a hash opens its card, folded or not; the spec's older anchors still land (#achievements, #types)
  const ALIAS = { achievements: 'badges', types: 'readiness', coverage: 'readiness', feed: 'recent', preferences: 'prefs' };
  const toHash = (wait) => {
    const id = location.hash.slice(1);
    const el = id && document.getElementById(ALIAS[id] || id);
    if (el) { el.dispatchEvent(new CustomEvent('satf:open')); setTimeout(() => el.scrollIntoView({ block: 'start' }), wait); }
  };
  toHash(300);
  addEventListener('hashchange', () => toHash(0));
})();
