/* ============================================================================
   SAT Freshman -- Profile, /me/ (Shell 3; shell-me U4-U14, U22, U25, U26, U29; R25, R31)
   and, with window.ME_SHARE set, the read-only progress view /share/?t= (Shell 6).

   One call builds the page: GET /api/me/summary (painted from its cached copy first),
   with /api/me, /api/account, /api/me/activity, /api/me/week and /api/me/feed beside it.
   Each card loads, fails and retries on its own. Thirteen cards: the work and the charts in
   the main column, who you are and your goals in the aside from 1280px (one column below, in
   the phone order), a section bar, and a fold on each card kept in localStorage satf.me.collapsed.

   The user's rules (2026-09-28) hold throughout: no calibration words (rough, levels,
   odds), scores read "7 / 11", no timestamps in history lines, no card repeats another
   card's numbers, zeros and defaults stay out.
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h, A = UI.acct;
  const N = n => UI.num(n);
  const pl = (n, one, many) => `${N(n)} ${n === 1 ? one : many || one + 's'}`;
  const tn = t => UI.topicName(t);
  const day = d => UI.date(d, 'short');
  const band = b => (b ? `${b.low}–${b.high}` : '');
  const mid = b => Math.round((b.low + b.high) / 2);
  const pct = x => `${Math.round((x || 0) * 100)}%`;
  // an unknown name draws nothing (it used to draw an orange dot, which hid typos)
  const ic = (name, size = 16) => h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.ICON[name] ? UI.svg(UI.ICON[name], size) : '' });
  const ls = A.ls;
  const phone = () => matchMedia('(max-width: 759px)').matches;
  const query = new URLSearchParams(location.search);
  const SHARE = window.ME_SHARE || null;
  const RO = !!SHARE;
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
    const b = h(tag, { class: o.primary ? (o.lg ? 'pill' : 'pill sm') : o.quiet ? 'quiet' : o.link ? 'link' : 'btn sm', type: o.href ? null : 'button',
      href: o.href || null, 'aria-label': o.aria || null }, label);
    if (o.body) b.addEventListener('click', () => start(o.body, b));
    else if (o.onClick) b.addEventListener('click', e => o.onClick(e, b));
    return b;
  }
  const tag = t => h('span', { class: 'tag' }, UI.glyph(t), tn(t));
  // ponytail: these server levers print a raw {low, high}, a topic slug or the met count instead of the
  // figure on the card, so they stay unwired (the card's "?" explains them); drop a key once its lever reads right
  const HELD = new Set(['band', 'points', 'readiness', 'band:rw', 'points:rw', 'readiness:rw']);
  const fact = (el, key, label) => {
    if (RO || !key || HELD.has(key)) return el;
    el.dataset.fact = key; if (label) el.dataset.factLabel = label;
    if (el.tagName !== 'BUTTON') el.tabIndex = 0;
    return el;
  };

  /* ---- the cards: col L is the aside (who you are, goals, context), col R the main column (the work and the
     charts); o is the one-column order below 1280px. A part is a second list inside a card, with its own id
     (a hash target) and its own painter: Habits in Mistakes, Recent in Activity. */
  const CARDS = [
    { id: 'you', title: 'You', col: 'P', o: 1 },   // the identity plate: full width above both columns, the page's one hero
    { id: 'goals', title: 'Goals', col: 'L', o: 3, help: 'routing' },
    { id: 'snapshot', title: 'Snapshot', col: 'L', o: 4, help: 'band' },
    { id: 'badges', title: 'Achievements', col: 'L', o: 11, chip: 'Badges', me: true },
    { id: 'saved', title: 'Saved & in progress', col: 'L', o: 13, chip: 'Saved', me: true },
    { id: 'account', title: 'Account', col: 'L', o: 14, me: true, help: 'devices' },
    { id: 'week', title: 'This week', col: 'R', o: 2 },
    { id: 'skills', title: 'Skills', col: 'R', o: 6, help: 'points', subj: true },
    { id: 'readiness', title: 'Test-day readiness', col: 'R', o: 7, chip: 'Readiness', help: 'readiness', subj: true },
    { id: 'trend', title: 'Score trend', col: 'R', o: 8, chip: 'Trend', help: 'projection', subj: true },
    { id: 'pace', title: 'Pace', col: 'R', o: 9, me: true, help: 'pace', subj: true },
    { id: 'catching', title: 'Mistakes', col: 'R', o: 10, help: 'mistakes', subj: true, parts: [{ id: 'habits', title: 'Habits', help: 'habits' }] },
    { id: 'activity', title: 'Activity', col: 'R', o: 12, help: 'streak', parts: [{ id: 'recent', title: 'Recent' }] },
  ].filter(c => !RO || !c.me);
  const CHIPS = ['week', 'goals', 'skills', 'snapshot', 'readiness', 'trend', 'pace', 'catching', 'badges', 'activity', 'saved', 'account'];
  const C = {};
  const folded = new Set(RO ? [] : ls.get('satf.me.collapsed', null) || []);
  // the analytics start folded, once per device, so a card opened later stays open; each keeps its one-line answer
  if (!RO && !ls.get('satf.me.fold2', false)) {
    ['snapshot', 'trend', 'pace', 'catching', 'activity'].forEach(id => folded.add(id));
    ls.set('satf.me.collapsed', [...folded]); ls.set('satf.me.fold2', true);
  }
  function makeCard(c) {
    const title = c.id === 'you' ? null : h('h2', { id: `${c.id}-h`, text: c.title });
    const act = h('div', { class: 'card-act' });
    const fold = RO ? null : h('button', { type: 'button', class: 'ibtn card-fold', html: UI.svg(UI.ICON.chev, 18) });
    const head = h('div', { class: 'card-head' }, title, c.help && !RO ? A.helpBtn(c.help, c.title) : null, act, fold);
    const sum = h('p', { class: 'card-sum' });
    const body = h('div', { class: 'card-body' });
    const parts = (c.parts || []).map(p => {
      const pAct = h('div', { class: 'card-act' }), pBody = h('div', { class: 'card-body' });
      const pEl = h('div', { class: 'card-part', id: p.id, role: 'group', 'aria-labelledby': `${p.id}-h` },
        h('div', { class: 'part-head' }, h('h3', { class: 'sub-h', id: `${p.id}-h`, text: p.title }), p.help && !RO ? A.helpBtn(p.help, p.title) : null, pAct), pBody);
      C[p.id] = { el: pEl, act: pAct, sum: h('p'), body: pBody, part: true };
      return pEl;
    });
    const el = h('section', { class: 'card' + (c.id === 'you' ? ' hero id-card' : ''), id: c.id, style: `--o: ${c.o}`,
      'aria-labelledby': title ? title.id : null, 'aria-label': title ? null : 'You' }, head, sum, body, ...parts);
    const setFold = on => {
      el.toggleAttribute('data-collapsed', on);
      if (fold) { fold.setAttribute('aria-expanded', String(!on)); fold.setAttribute('aria-label', `${on ? 'Expand' : 'Collapse'} ${c.title}`); }
      if (on) folded.add(c.id); else folded.delete(c.id);
    };
    if (fold) fold.addEventListener('click', () => { setFold(!el.hasAttribute('data-collapsed')); ls.set('satf.me.collapsed', [...folded]); });
    el.addEventListener('satf:open', () => { if (el.hasAttribute('data-collapsed')) { setFold(false); ls.set('satf.me.collapsed', [...folded]); } });
    setFold(folded.has(c.id));
    if (c.col === 'P') document.getElementById('grid').before(h('div', { class: 'me-grid me-plate' }, el));
    else document.getElementById(c.col === 'L' ? 'colL' : 'colR').append(el);
    C[c.id] = { el, act, sum, body, title };
  }
  CARDS.forEach(makeCard);
  /* ---- one subject switch (?subject=), in the Skills card's header: Skills, readiness, trend, pace and mistakes
     show one subject at a time; the rest of Me (Goals, Snapshot) shows Total, R&W and Math side by side */
  let SUBJ = UI.subject.get();
  const SUBJ_CARDS = CARDS.filter(c => c.subj).map(c => c.id).concat('habits', 'saved');   // (saved: its sets follow the switch)
  { const host = h('div', { class: 'me-subj' });
    UI.subjectSeg(host, { value: SUBJ, short: true, onChange: v => { SUBJ = v; paint(...SUBJ_CARDS); } });
    if (C.skills) C.skills.el.querySelector('.card-head').append(host); }    // after the title's fold, before the card's own actions
  const part = () => (S.subjects && S.subjects[SUBJ]) || (S.subjects || {}).math || {};
  const rwOn = () => SUBJ === 'rw';
  // a set on an R&W skill says its subject (the server reads it; Math is the default)
  const subj = body => (rwOn() ? { ...body, subject: 'rw' } : body);
  // page entry (once per visit, kit.js): the plate and the two columns rise; the one holding Start is never delayed
  { const main = document.getElementById('main'), grid = document.getElementById('grid');
    if (grid) grid.setAttribute('data-m-now', '');
    if (main) main.setAttribute('data-m', 'stagger'); }
  const fill = (id, ...kids) => { if (C[id]) C[id].body.replaceChildren(...kids.flat(3).filter(k => k !== null && k !== undefined && k !== false)); };
  const acts = (id, ...kids) => { if (C[id]) C[id].act.replaceChildren(...kids.flat().filter(Boolean)); };
  const said = (id, text) => { if (C[id]) C[id].sum.textContent = text || ''; };
  Object.keys(C).forEach(id => fill(id, UI.skel(null, id === 'you' ? 'card:5' : 'card:3')));

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
    return UI.me(fresh).then(r => { P = r.profile; paint('you', 'goals', 'snapshot', 'week'); }, failOn('profile', () => loadProfile(true), ['you', 'goals']));
  }
  function loadAccount() {
    return Promise.all([UI.api('/account'), UI.api('/devices').catch(() => null), UI.api('/passkeys').catch(() => null)])
      .then(([a, d, k]) => { ACC = a; DEV = d; PK = k; paint('account', 'you'); }, failOn('account', loadAccount, ['account']));
  }
  let weeks = ls.get('satf.me.weeks', 26);
  function loadActivity() {
    return UI.api(`/me/activity?weeks=${weeks}`).then(d => { ACT = d; paint('activity', 'week'); }, failOn('activity', loadActivity, ['activity']));
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
      const pick = h('button', { type: 'button', class: 'ibtn av-edit', 'aria-label': 'Change avatar', html: UI.svg(UI.ICON.pen, 14) });
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
    // the plate: the mark, who you are on one line, what you've gained, the last three badges; the four figures under it
    fill('you', h('div', { class: 'id-top' }, avWrap, h('div', { class: 'id-who' }, RO ? null : nameBox, RO ? null : lines, outcomes()), RO ? null : shelf()), tiles());
    said('you', [name, st.answered ? `${N(st.answered)} answered` : null, st.streak ? `streak ${N(st.streak)}` : null].filter(Boolean).join(' · '));
  };
  function boardLine(prof, name) {
    const offer = prof.name && !prof.handle && A.HANDLE_OK.test(prof.name);
    // the words, then the ways to change them as one unit, so a narrow plate wraps between the two, never inside
    const acts = h('span', { class: 'id-board-acts' });
    const line = h('span', { class: 'id-board' }, h('span', {}, 'On boards: ', prof.handle ? h('b', { text: prof.handle }) : 'no name yet',
      prof.board && prof.board !== 'name' ? ` · ${prof.board === 'anon' ? 'anonymous' : 'hidden'}` : null), acts);
    // the first time a name is set, one tap puts it on the boards too (U29)
    if (offer) acts.append(btn(`Use ${prof.name}`, { quiet: true, aria: `Use ${prof.name} on boards too`, onClick: async () => {
      try { P = await A.saveMe({ handle: prof.name }); UI.toast(`On boards: ${prof.name}`); paint('you'); }
      catch (x) { if (x.status === 409) { UI.toast('Someone already has that board name. Pick another.'); boardPop(line); } else UI.toast(A.handleError(x)); }
    } }), ' · ');
    acts.append(btn(prof.handle ? 'Change' : offer ? 'Other' : 'Choose one', { quiet: true, aria: 'Change your board name', onClick: (e, b) => boardPop(b) }));
    return line;
  }
  function boardPop(anchor) {
    const prof = P || {};
    UI.pop(anchor, () => {
      const f = h('input', { class: 'field', value: prof.handle || '', maxlength: '24', 'aria-label': 'Board name', autocomplete: 'off',
        placeholder: prof.name && A.HANDLE_OK.test(prof.name) ? `${prof.name.replace(/\s+/g, '_')}2` : 'Board name' });
      const e = h('p', { class: 'field-err', hidden: true, role: 'alert' });
      const save = h('button', { type: 'button', class: 'pill sm', text: 'Save' });
      // Save, Saving, Saved in place (UI.saving announces it); the pop stays open to show it
      save.addEventListener('click', () => {
        const v = f.value.trim();
        if (!A.HANDLE_OK.test(v)) { e.textContent = A.handleError({ status: 422 }); e.hidden = false; return; }
        e.hidden = true;
        UI.saving(save, () => A.saveMe({ handle: v })).then(r => { P = r; }, x => { e.textContent = A.handleError(x); e.hidden = false; });
      });
      f.addEventListener('keydown', ev => { if (ev.key === 'Enter') save.click(); });
      const vis = h('div');
      UI.seg(vis, [{ value: 'name', label: 'By name' }, { value: 'anon', label: 'Anonymous' }, { value: 'hidden', label: 'Don’t list me' }],
        { value: prof.board || 'name', label: 'Show me on boards', onChange: async v => {
          try { P = await A.saveMe({ board: v }); UI.toast('Saved'); } catch (_) { UI.toast('Not saved. Try again.'); }
        } });
      return [h('div', { class: 'pop-form' }, h('label', { class: 'label', text: 'Board name' }), f, e,
        h('p', { class: 'help', text: 'The only name boards, contests and ranks show. Your own name stays private.' }), save,
        h('span', { class: 'label', text: 'Show me on boards' }), vis,
        h('p', { class: 'help', text: 'Anonymous shows a student number. Unlisted still shows you your own rank.' }))];
    // the You card repaints once the pop closes (the shell refresh skips it while a pop in it is open), so the anchor
    // stays put while "Saved" shows; focus that was on the old Change button goes to the new one
    }, { label: 'Board name', onClose: () => {
      const lost = !document.activeElement || document.activeElement === document.body || document.activeElement === anchor;
      paint('you');
      const b = lost && document.querySelector('#you [aria-label="Change your board name"]');
      if (b) b.focus({ preventScroll: true });
    } });
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
  // the last three badges earned (or, before any, the three closest) in the badge art, and the way to all of them
  function shelf() {
    const all = S.achievements || [];
    if (!all.length) return null;
    const won = a => !!(a.earned && a.earned.length);
    const earned = all.filter(won).sort((a, b) => (lastAt(a) < lastAt(b) ? 1 : -1));
    const near = all.filter(a => a.next && !won(a)).sort((a, b) => (b.have || 0) / b.next - (a.have || 0) / a.next);
    const three = [...earned, ...near].slice(0, 3);
    // a badge earned since this device last looked pops once (a reward); the first visit only remembers
    const seen = ls.get('satf.me.badges', null), ids = earned.map(a => a.id);
    if (!seen || ids.some(id => !seen.includes(id))) ls.set('satf.me.badges', ids);
    const fresh = [];
    const shelfEl = h('div', { class: 'shelf' },
      h('div', { class: 'shelf-row', role: 'list', 'aria-label': earned.length ? 'Your latest badges' : 'The badges you are closest to' },
        three.map(a => {
          const say = won(a) ? `${a.name} · ${day(lastAt(a))}` : `${a.name} · ${N(a.have || 0)} / ${N(a.next)}`;
          const el = h('span', { role: 'img', 'aria-label': say }, badgeIcon(a, won(a)));
          if (UI.tooltip) UI.tooltip(el, say); else el.title = say;
          if (seen && won(a) && !seen.includes(a.id)) fresh.push(el);
          return h('span', { role: 'listitem' }, el);
        })),
      btn(`${N(earned.length)} of ${N(all.length)} · All badges`, { quiet: true, onClick: () => allBadges(all) }));
    if (fresh.length && UI.fx) requestAnimationFrame(() => fresh.forEach((el, i) => setTimeout(() => UI.fx.pop(el), i * 60)));
    return shelfEl;
  }
  function outcomes() {
    const out = h('div', { class: 'outs' });
    // each subject with two scored sittings: how far it has come (R&W first, College Board's order)
    let any = 0;
    ['rw', 'math'].forEach(s => {
      const sc = ((S.subjects || {})[s] || {}).score || (s === 'math' ? S.score : {});
      const sit = (sc.points || []).slice().sort((a, b) => (a.at < b.at ? -1 : 1));
      any += sit.length;
      if (sit.length < 2 || !sc.latest) return;
      const d = mid(sc.latest) - mid(sit[0]);
      out.append(fact(h('button', { type: 'button', class: 'out' }, h('b', { text: `${d >= 0 ? '+' : '−'}${N(Math.abs(d))}` }), `${UI.subjectLabel(s, true)} since you started`,
        h('span', { class: 'meta', text: `${band(sit[0])} → ${band(sc.latest)}` })), 'band', 'Since you started'));
    });
    if (!out.childNodes.length && !RO) {
      out.append(h('a', { class: 'out', href: '/tests/' }, any ? 'Your next module shows how far you’ve come.' : 'Your first module sets your start.'));
    }
    const gs = ['math', 'rw'].map(s => ((S.subjects || {})[s] || {}).gains).filter(x => x && x.total);
    if (gs.length) {
      const g = gs[0];
      out.append(fact(h('button', { type: 'button', class: 'out' }, 'About ', h('b', { text: N(gs.reduce((n, x) => n + x.total, 0)) }), 'points to gain',
        gs.length === 1 && g.top3 && g.top3.gain ? h('span', { class: 'meta', text: `${N(g.top3.gain)} in your top 3 skills` }) : null), 'points', 'Points to gain'));
    }
    const ck = S.stats.checks;
    if (ck && ck.due) out.append(h('div', { class: 'out' }, h('b', { text: `${N(ck.passed)} / ${N(ck.due)}` }), 'fixes held'));
    out.querySelectorAll('button:not([data-fact])').forEach(b => b.replaceWith(h('div', { class: 'out' }, ...b.childNodes)));
    return out.childNodes.length ? out : null;
  }
  function tiles() {
    const st = S.stats, ser = st.series || {};
    const sum = (a, i, j) => (a || []).slice(i, j).reduce((x, y) => x + (y || 0), 0);
    const wk = k => sum(ser[k], 7, 14);
    const spares = (SHELL && SHELL.spares) || 0;
    // four tiles open; streak (the shell shows it), tests, words and rating behind More stats
    const host = h('div', { class: 'stats' }), rest = h('div', { class: 'stats' });
    let to = host;
    // decision 7: a tile only once it has a value; a new student saw eight tiles of dashes
    const T = o => {
      if (o.value === null || o.value === undefined || o.value === 0) return;
      // label, value and one quiet line, always shown: a hover-only week, change and sparkline left a blank band at
      // rest and drew stair-steps on a phone; the trends live on Results, where each tile goes
      UI.tile(to, RO ? { ...o, href: null, fact: null } : o);
    };
    T({ label: 'Answered', value: st.answered || null, sub: wk('answered') ? `${N(wk('answered'))} this week` : null, href: '/results/' });
    T({ label: 'First-try accuracy', value: st.accuracy ?? null, format: v => `${v}%`,
      sub: st.accuracy7 !== null && st.accuracy7 !== undefined && st.accuracy7 !== st.accuracy ? `${st.accuracy7}% last 7 days` : null,
      href: '/results/#skills' });
    T({ label: 'Study time', value: st.minutes_total ? UI.dur(st.minutes_total) : null, sub: st.minutes_week ? `${UI.dur(st.minutes_week)} this week` : null,
      fact: 'minutes:week' });
    T({ label: 'Mistakes fixed', value: st.mistakes_fixed || null, sub: st.mistakes_open ? `${N(st.mistakes_open)} open` : null,
      href: '/review/' });
    to = rest;
    T({ label: 'Streak', value: st.streak || null, unit: st.streak ? (st.streak === 1 ? 'day' : 'days') : null,
      sub: st.streak ? [`best ${N(st.best_streak)}`, spares ? `${spares} spare banked` : null].filter(Boolean).join(' · ') : null,
      missing: 'Answer one question to start', fact: 'streak' });
    T({ label: 'Tests', value: st.tests || null, href: '/tests/#history', missing: 'Take a module',
      sub: [st.sections && pl(st.sections, 'section'), st.modules && pl(st.modules, 'module'), st.diagnostics && pl(st.diagnostics, 'diagnostic')].filter(Boolean).join(' · ') || null });
    const w = S.words;
    T({ label: 'Words', value: w && w.known ? w.known : null, sub: w && w.due ? `${N(w.due)} due` : null, missing: w ? 'Start in Words' : null, href: '/words/' });
    T({ label: 'Rating', value: S.challenge && S.challenge.played ? S.challenge.rating : null, missing: 'Play a contest to get one', href: '/compete/',
      sub: S.challenge && S.challenge.rw_rating ? `Math · R&W ${N(S.challenge.rw_rating)}` : null });
    // with no open tile yet, the rest show open; otherwise they wait one tap away
    if (!host.children.length) return rest.children.length ? rest : null;
    const open = ls.get('satf.me.morestats', false);
    const more = rest.children.length ? h('details', { class: 'more-stats', open: open && !RO ? '' : null },
      h('summary', { text: `More stats (${rest.children.length})` }), rest) : null;
    if (more && !RO) more.addEventListener('toggle', () => ls.set('satf.me.morestats', more.open));
    return [host, more];
  }

  /* ================================================================ This week (U14) */
  PAINT.week = () => {
    if (RO) { const w = S && S.week; if (!w || !w.goals || !w.goals.length) { C.week.el.hidden = true; return; } WEEK = w; }
    if (!ready('week', 'week')) return;
    const goals = WEEK.goals || [];
    const rc = WEEK.receipts || {};
    const receipt = [rc.answered && `${N(rc.answered)} answered`, rc.accuracy !== null && rc.accuracy !== undefined && rc.answered && `${rc.accuracy}% first try`,
      rc.minutes && UI.dur(rc.minutes), rc.fixed && pl(rc.fixed, 'mistake') + ' fixed'].filter(Boolean);
    // a goal met since this device last looked draws its check once (UI.fx.check); the first visit only remembers
    const gk = g => `${WEEK.week || ''}:${g.kind}:${JSON.stringify(g.params || {})}`;
    const metSeen = RO ? null : ls.get('satf.me.met', null), drawn = [];
    const list = h('div', { class: 'list' }, goals.map(g => h('div', { class: 'lrow' },
      g.done ? (() => { const c = h('span', { class: 'chk', 'aria-hidden': 'true', html: UI.svg(UI.ICON.check, 16) }); if (metSeen && !metSeen.includes(gk(g))) drawn.push(c); return c; })()
        : h('span', { class: 'odot', 'aria-hidden': 'true' }),
      h('div', {}, h('p', { class: 't', text: UI.weekTitle ? UI.weekTitle(g) : g.title }),
        UI.meter(null, { value: Math.min(g.have || 0, g.target || 0), max: g.target || 0, text: `${N(g.have || 0)} / ${N(g.target || 0)}` }).el),
      g.done ? h('span', { class: 'meta', text: 'Met' }) : null)));
    const first = goals.find(g => !g.done);
    // the last six weeks that had goals: "Met 4 of the last 6 weeks", six bars, the best one named (U14)
    const hist = (WEEK.history || []).filter(w => w.total).slice(-6);
    const met = w => w.met >= w.total;
    const best = hist.slice().sort((a, b) => b.met / b.total - a.met / a.total)[0];
    const histEl = hist.length >= 2 ? h('div', { class: 'wk-hist' },
      h('span', { class: 'wk-bars', role: 'img', 'aria-label': hist.map(w => `${w.start ? day(w.start) : w.week}: ${w.met} of ${w.total}`).join(', ') },
        hist.map(w => h('i', { class: met(w) ? 'met' : '', style: `--h: ${Math.min(1, w.met / w.total)}` }))),
      h('span', { class: 'meta', text: [`Met ${hist.filter(met).length} of the last ${hist.length} weeks`,
        best && best.start && best.met ? `best: week of ${day(best.start)}` : null].filter(Boolean).join(' · ') })) : null;
    // the plan's study days and minutes for this week (it was Goals' weekly row): needs the profile and the activity
    const prof = P || {};
    const wk = !RO && prof.plan && prof.days ? weekParts(prof) : null;
    const onSaved = w => { WEEK = w; paint('week'); UI.refresh(); };
    // the study days, the weeks met and last week's receipts sit in the Your week sheet; one row here says them in a line
    const extra = wk || histEl ? [h('h3', { class: 'sub-h', text: 'Study days' }), wk && wk.el, histEl].filter(Boolean) : null;
    const openWeek = () => UI.week && UI.week({ onSaved, extra });
    const sumBits = [wk && wk.line, hist.length >= 2 && `met ${hist.filter(met).length} of the last ${hist.length} weeks`,
      receipt.length && `last week ${receipt[0]}`].filter(Boolean);
    const sumText = sumBits.join(' · ').replace(/^./, x => x.toUpperCase());
    const sumRow = !sumBits.length ? null : RO ? h('p', { class: 'meta wk-line', text: sumText })
      : h('button', { type: 'button', class: 'wk-sum', 'aria-haspopup': 'dialog', onclick: openWeek },
        h('span', { class: 'wk-sum-t', text: 'Your week' }), h('span', { class: 'meta', text: sumText }),
        h('span', { class: 'wk-sum-c', 'aria-hidden': 'true', html: UI.svg(UI.ICON.chev, 16) }));
    fill('week',
      goals.length ? list : h('p', { class: 'soft', text: 'Pick up to three goals for this week. They show here as you go.' }),
      sumRow,
      RO ? null : h('div', { class: 'card-foot' },
        first && UI.weekStart ? btn('Start the first', { primary: true, lg: true, onClick: (e, b) => UI.weekStart(first, b) }) : null,
        btn(goals.length ? 'Change goals' : 'Plan your week', { primary: !goals.length, lg: !goals.length, onClick: openWeek })));
    said('week', goals.length ? `${goals.filter(g => g.done).length} / ${goals.length} goals met` : 'No goals yet');
    if (!RO) {
      const met = goals.filter(g => g.done).map(gk);
      if (!metSeen || met.some(k => !metSeen.includes(k))) ls.set('satf.me.met', [...new Set([...(metSeen || []), ...met])].slice(-30));
      if (drawn.length && UI.fx) requestAnimationFrame(() => drawn.forEach(c => UI.fx.check(c)));
    }
  };

  /* ================================================================ Goals (Shell 3.3, U4) */
  PAINT.goals = () => {
    if (!ready('goals', 'summary', ...(RO ? [] : ['profile']))) return;
    const g = S.goals || {}, prof = P || {};
    const target = RO ? g.subjects.math.target : prof.target;
    const rwT = RO ? g.subjects.rw.target : prof.rw_target;
    // the server's ranges, side by side: Total, then R&W, then Math (a total is never two ranges added)
    const SC = S.scores || { total: {}, rw: {}, math: g.subjects && g.subjects.math.band || S.score.latest || {} };
    const has = b => b && b.low !== null && b.low !== undefined;
    const exam = RO ? g.exam_date : prof.exam_date;
    const plan = RO ? null : prof.plan;
    const rows = h('div', { class: 'rows' });
    // Target: the 1600 total when both targets are set, then each section's
    const tv = target && rwT ? [h('b', { text: String(target + rwT) }), h('span', { class: 'soft', text: ` · R&W ${rwT} · Math ${target}` })]
      : target ? ['Math ', h('b', { text: String(target) })]
      : rwT ? ['R&W ', h('b', { text: String(rwT) })] : 'No target yet';
    const tRow = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Target' }), h('span', { class: 'v grow' }, tv),
      btn(target || rwT ? 'Edit' : 'Set a target', { quiet: true, aria: 'Edit target', onClick: (e, b) => targetPop(b) }));
    if (target || rwT) {
      // the bar: the total on 400-1600 with both targets, else the one section on 200-800
      const total = target && rwT;
      const [L, T, lo, span] = total ? [SC.total, target + rwT, 400, 1200] : target ? [SC.math, target, 200, 600] : [SC.rw, rwT, 200, 600];
      const x = v => `${Math.max(0, Math.min(100, (v - lo) / span * 100))}%`;
      tRow.append(h('div', { class: 'gbar full', role: 'img',
        'aria-label': has(L) ? `Now ${band(L)}, target ${T}` : `Target ${T}` },
        has(L) ? h('span', { class: 'bd', style: `left: ${x(L.low)}; width: calc(${x(L.high)} - ${x(L.low)})` }) : null,
        h('span', { class: 'tk', style: `left: ${x(T)}` })));
      const go = has(L) ? T - mid(L) : null;
      tRow.append(h('p', { class: 's' }, has(L) ? `${band(L)} now · ${go > 0 ? `+${go} to go` : 'target reached'}` : 'Your first module shows where you are against it.',
        has(L) && go <= 0 && !total && target && target < 800 ? [' · ', btn(`Raise to ${Math.min(800, target + 50)}?`, { quiet: true, onClick: () => saveTarget({ target: Math.min(800, target + 50) }) })] : null));
      // each section against its own target, one quiet line
      const each = [['rw', 'R&W', rwT], ['math', 'Math', target]].filter(([, , t]) => t)
        .map(([s, nm, t]) => `${nm} ${has(SC[s]) ? `${band(SC[s])}${SC[s].source === 'yours' ? ' (yours)' : ''}` : 'not measured'} → ${t}`);
      if (total) tRow.append(h('p', { class: 's', text: each.join(' · ') }));
      if (!total && !RO) tRow.append(h('p', { class: 's' }, btn(target ? 'Add your R&W target for a total' : 'Add your Math target for a total', { quiet: true, onClick: (e, b) => targetPop(b) })));
      // what each target takes, in right answers (it speaks to the student, not to a parent reading the link)
      [['R&W', g.need_rw, rwT], ['Math', g.need, target]].forEach(([nm, need, t]) => {
        if (RO || !need || !t) return;
        if (need.reachable && need.right_of_44) {
          const where = (need.where || []).slice(0, 3).map(tn), of = need.of || 44, m1 = need.m1_of || 22;
          tRow.append(h('p', { class: 's help', text: `What ${nm} ${t} takes: about ${need.right_of_44} of ${of} right` +
            (need.m1_min ? `, with at least ${need.m1_min} of ${m1} in module 1 to reach the harder module 2` : '') +
            (need.now_of_44 !== null && need.now_of_44 !== undefined ? `. You’re near ${need.now_of_44}.` : '.') +
            (where.length ? ` The ones you’re most likely missing are in ${where.join(', ').replace(/, ([^,]*)$/, ' and $1')}.` : '') }));
        } else if (need.reachable === false) {
          tRow.append(h('p', { class: 's help', text: `Our score model tops out at ${need.ceiling} for a perfect ${nm} paper, so ${t} is past what a sitting here can show.` }));
        }
      });
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
        eRow.append(h('div', { class: 'gbar thin full', role: 'img', 'aria-label': `${pl(left, 'day')} to go` },
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
        dRow.append(h('div', { class: 'full' }, UI.meter(null, { value: today.minutes || 0, max: prof.minutes, unit: 'min', label: 'Today' }).el));
        rows.append(dRow);
      }
      const focus = prof.focus && (prof.focus.topics || prof.focus.on || []);
      if (focus && focus.length) rows.append(h('div', { class: 'row' }, h('span', { class: 'k', text: 'Focus' }),
        h('span', { class: 'v grow', text: focus.map(tn).join(', ') }), btn('Edit', { quiet: true, href: '/plan/?step=4', aria: 'Edit focus' })));
    } else if (!RO) {
      kids.push(h('div', { class: 'card-foot' }, h('p', { class: 'soft grow', text: 'No plan yet. Four questions, about a minute.' }),
        btn('Build my plan', { href: '/plan/' })));
    }
    const time = (UI.prefs.now() || {}).study_time;
    if (!RO && time) rows.append(h('div', { class: 'row' }, h('span', { class: 'k', text: 'Preferred time' }),
      h('span', { class: 'v grow', text: time }), btn('Change', { quiet: true, href: '/me/settings/#study' })));
    fill('goals', kids);
    acts('goals', btn('Open plan', { quiet: true, href: '/plan/' }));
    said('goals', [target && rwT ? `Target ${target + rwT}` : target ? `Math target ${target}` : rwT ? `R&W target ${rwT}` : null, exam ? UI.date(exam, 'short') : null].filter(Boolean).join(' · ') || 'No goals yet');
  };
  function weekParts(prof) {
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
    const r = h('div', { class: 'wk-days' }, h('p', {}, h('span', { class: 'k', text: 'Weekly goal ' }),
      h('b', { text: [perWeek ? UI.dur(perWeek) : null, daysText(study)].filter(Boolean).join(' · ') })));
    if (perWeek) r.append(UI.meter(null, { value: mins, max: perWeek, label: 'This week', text: `${UI.dur(mins)} of ${UI.dur(perWeek)}` }).el);
    r.append(h('div', { class: 'dots7', role: 'img', 'aria-label': 'This week’s days' }, dots));
    return { el: r, line: perWeek ? `${UI.dur(mins)} of ${UI.dur(perWeek)} studied` : `study days ${daysText(study)}` };
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
    const SC = (S && S.scores) || { rw: {}, math: (S && S.score.latest) || {} };
    const at = b => (b && b.mid !== null && b.mid !== undefined ? Math.round(b.mid / 10) * 10 : null);
    // an unset section target starts 50 above its score (or at 600), so the total is always both parts
    let t = prof.target || Math.min(800, (at(SC.math) || 550) + 50), rw = prof.rw_target || Math.min(800, (at(SC.rw) || 550) + 50);
    let rwNow = prof.rw_now || null;
    // R&W "now" is typed only until an R&W test or a logged Bluebook score measures it
    const typedRw = !SC.rw || !SC.rw.source || SC.rw.source === 'yours';
    UI.pop(anchor, (p, res) => {
      const total = h('p', { class: 'total' });
      const live = h('p', { class: 'help' }), rlive = h('p', { class: 'help' });
      const save = h('button', { type: 'button', class: 'pill sm', text: 'Save', disabled: true });
      const math = UI.scoreSlider(null, { min: 200, max: 800, step: 10, value: t, label: 'Math target', onInput: v => { t = v; sync(); }, onChange: v => { t = v; sync(); } });
      const chips = UI.chips(null, [600, 650, 700, 750, 800].map(v => ({ value: v, label: String(v) })), { value: t, label: 'Math target',
        onChange: v => { t = v; math.set(v); sync(); } });
      const rwS = UI.scoreSlider(null, { min: 200, max: 800, step: 10, value: rw, label: 'Reading and Writing target', onInput: v => { rw = v; sync(); }, onChange: v => { rw = v; sync(); } });
      const rwChips = UI.chips(null, [600, 650, 700, 750, 800].map(v => ({ value: v, label: String(v) })), { value: rw, label: 'Reading and Writing target',
        onChange: v => { rw = v; rwS.set(v); sync(); } });
      const nowBox = h('div', { class: 'gap', hidden: !rwNow || null });
      const rwN = UI.scoreSlider(nowBox, { min: 200, max: 800, step: 10, value: rwNow || 500, label: 'Your R&W score now', onInput: v => { rwNow = v; sync(); }, onChange: v => { rwNow = v; sync(); } });
      nowBox.prepend(h('span', { class: 'help', text: 'Your R&W score now, until an R&W test measures it' }));
      const addNow = h('button', { type: 'button', class: 'quiet', text: rwNow ? 'Clear my R&W score' : 'Add my R&W score',
        onclick: () => { const on = nowBox.hidden; nowBox.hidden = !on; rwNow = on ? rwN.value : null; addNow.textContent = on ? 'Clear my R&W score' : 'Add my R&W score'; sync(); } });
      // what the chosen target takes, live, from Plan's own preview (U4, S7's plan.pace): the module-1
      // route line, and "40 days · 30 study days · about 30 points a week · Ambitious" with an exam date
      const takes = h('p', { class: 'help', hidden: true }), paceLine = h('p', { class: 'help', hidden: true });
      let timer = 0, asked = 0;
      const preview = () => {
        clearTimeout(timer);
        if (!prof.exam_date) return;
        timer = setTimeout(async () => {
          const n = ++asked;
          try {
            const r = await UI.api('/plan/preview', { method: 'POST', quiet: true,
              body: { exam_date: prof.exam_date, target: t, minutes: prof.minutes || 30, days: prof.days || '1111111' } });
            if (n !== asked) return;
            const tn2 = r.target_note || {};
            takes.textContent = tn2.route_up && tn2.route_right ? `At least ${tn2.route_right} of ${tn2.route_of || 22} right in module 1 to reach the harder module 2.` : '';
            takes.hidden = !takes.textContent;
            const left = Math.round((new Date(prof.exam_date + 'T00:00') - new Date(new Date().toDateString())) / 864e5);
            const later = r.later_date && (r.later_date.date || r.later_date);
            paceLine.replaceChildren([pl(left, 'day'), r.study_days && pl(r.study_days, 'study day'),
              r.pace_per_week && `about ${N(Math.round(r.pace_per_week))} points a week`, r.pace_tag].filter(Boolean).join(' · '));
            if (typeof later === 'string' && r.pace_tag && r.pace_tag !== 'Steady') paceLine.append(' · ', btn(`${day(later)} makes it Steady`, { quiet: true, onClick: async () => {
              res.close(); P = await A.saveMe({ exam_date: later }); UI.toast(`Exam: ${UI.date(later, 'long')}`); reloadMe();
            } }));
            paceLine.hidden = false;
          } catch (_) { if (n === asked) { takes.hidden = true; paceLine.hidden = true; } }
        }, 250);
      };
      const vsNow = (v, b) => (at(b) !== null ? (v > at(b) ? `+${v - at(b)} from your score now` : 'At or below your score now') : '');
      function sync() {
        total.replaceChildren('Total ', h('b', { text: String(t + rw) }));
        live.textContent = vsNow(t, SC.math);
        rlive.textContent = vsNow(rw, typedRw && rwNow ? { mid: rwNow } : SC.rw);
        save.disabled = t === prof.target && rw === prof.rw_target && rwNow === (prof.rw_now || null);
        preview();
      }
      save.addEventListener('click', () => { res.close(); saveTarget({ target: t, rw_target: rw, ...(typedRw ? { rw_now: rwNow } : {}) }); });
      sync();
      // College Board's order: the total, then Reading and Writing, then Math
      return [h('div', { class: 'target-pop' }, total,
        h('div', { class: 'gap' }, h('span', { class: 'label', text: 'Reading and Writing' }), rwS.el, rwChips.el, rlive,
          typedRw ? nowBox : null, typedRw ? h('div', {}, addNow) : null),
        h('div', { class: 'gap' }, h('span', { class: 'label', text: 'Math' }), math.el, chips.el, live, takes, paceLine,
          h('a', { class: 'link', href: '/help/#routing', text: 'What a Math target takes' })),
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
    const prof = P || {};
    const SC = S.scores || { total: {}, rw: {}, math: S.score.latest || {} };
    const has = b => b && b.low !== null && b.low !== undefined;
    const rows = h('div', { class: 'rows' });
    // the scores side by side, College Board's order: Total, then Reading and Writing, then Math; each range is the
    // server's (20 points), the total its own range, never the two added
    const score = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Scores' }));
    if (has(SC.rw) || has(SC.math)) {
      const line = (s, nm) => {
        const b = SC[s], sub = ((S.subjects || {})[s] || {}).score || (s === 'math' ? S.score : {});
        const L = sub.latest, B = sub.best;
        if (!has(b)) return h('div', { class: 'sc-row' }, h('span', { class: 'sc-k', text: nm }), h('span', { class: 'soft', text: 'Not measured yet' }),
          RO ? null : btn(s === 'rw' ? 'Take an R&W module' : 'Take a module', { quiet: true, href: `/tests/?subject=${s}` }));
        // append() writes a null as the text "null" (the shared view had "520–580null"): only real nodes go in
        const said_ = b.source === 'yours' ? 'your estimate' : L ? [KIND[L.kind] || 'Sitting', day(L.at)].join(' · ') : '';
        return h('div', { class: 'sc-row' }, ...[h('span', { class: 'sc-k', text: nm }),
          fact(h('b', { class: 'n', text: band(b) }), s === 'rw' ? 'band:rw' : 'band', `${nm} score`),
          said_ ? h('span', { class: 'meta', text: said_ }) : null,
          L && L.id && L.kind !== 'outside' && b.source !== 'yours' && !RO ? h('a', { class: 'link', href: `/results/report/?id=${encodeURIComponent(L.id)}`, text: 'Report' }) : null,
          B && L && b.source !== 'yours' && (B.low !== L.low || B.high !== L.high) ? h('span', { class: 'meta', text: `best ${band(B)}` }) : null].filter(Boolean));
      };
      score.append(h('div', { class: 'sc full' }, ...[has(SC.total) ? h('div', { class: 'sc-row total' }, h('span', { class: 'sc-k', text: 'Total' }), h('b', { class: 'big', text: band(SC.total) })) : null,
        line('rw', 'R&W'), line('math', 'Math')].filter(Boolean)));
    } else {
      score.append(h('span', { class: 'v grow soft', text: 'No score yet' }),
        h('div', { class: 'acts full' }, btn('Take a module', { href: '/tests/' }), btn('Diagnostic · 20', { quiet: true, href: '/diagnostic/' })));
    }
    rows.append(score);
    // practice ranks: right answers over the last 7 days (R3, U11)
    const R = S.ranks || {};
    const boardHref = scope => `/compete/leaderboard/?metric=right&period=7d${scope ? `&scope=${scope}` : ''}`;
    const rank = h('div', { class: 'row' }, h('span', { class: 'k', text: 'Practice rank' }));
    const rline = (label, r, scope) => {
      if (!r || !r.rank) return null;
      return h('div', { class: 'row sub' },
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
    // "Math: started 440–460 · +90 · ahead of 74% of 212" (U11): each section's gain against students who started near you
    for (const [c, nm] of [[R.climb_rw, 'R&W'], [R.climb, 'Math']]) {
      if (!c) continue;
      const ahead = c.of > 1 ? Math.round(100 * (c.of - c.rank) / c.of) : null;
      rank.append(h('span', { class: 's', text: [`${nm}: ${c.window ? `started ${c.lo}–${c.hi}` : 'everyone who has sat a module'}`,
        c.gain !== undefined && c.gain !== null ? `${c.gain >= 0 ? '+' : '−'}${Math.abs(c.gain)}` : null,
        ahead !== null ? `ahead of ${ahead}% of ${N(c.of)}` : `#${N(c.rank)} of ${N(c.of)}`].filter(Boolean).join(' · ') }));
    }
    if (R.self && R.self.days >= 8) {
      const x = R.self;
      const parts = [x.estimate !== null && x.estimate !== undefined && `${x.estimate >= 0 ? '+' : '−'}${Math.abs(x.estimate)} on your Math score`,
        x.skills_to_strong && `${pl(x.skills_to_strong, 'skill')} to Strong`, x.fixed && `${pl(x.fixed, 'mistake')} fixed`].filter(Boolean);
      if (parts.length) rank.append(h('span', { class: 's', text: `Last ${x.days} days: ${parts.join(' · ')}` }));
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
    said('snapshot', [has(SC.total) ? `Total ${band(SC.total)}` : has(SC.math) ? `Math ${band(SC.math)}` : has(SC.rw) ? `R&W ${band(SC.rw)}` : 'No score yet', R.all && R.all.rank ? `#${N(R.all.rank)} of ${N(R.all.of)}` : null].filter(Boolean).join(' · '));
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
    // a set is one subject's: saved and marked follow the Skills switch; mistakes get a button per subject that has them
    part('Saved questions', st.saved, btn('Practise saved', { body: subj({ pool: 'saved', exact: true, source: 'review' }) }), btn('See all', { quiet: true, href: '/review/?tab=saved' }));
    part('Saved words', w.saved, btn('Review them', { href: '/words/?s=saved' }));
    part('Marked for review', sh.review && sh.review.marked, btn('Practise marked', { body: subj({ pool: 'marked', source: 'review' }) }));
    const by = st.mistakes_open_by || {}, both = (by.rw || 0) && (by.math || 0);
    part('Open mistakes', st.mistakes_open, ...['rw', 'math'].filter(s => by[s]).map(s => btn(both ? `Fix ${UI.subjectLabel(s, true)} · ${N(by[s])}` : 'Fix all',
      { body: { pool: 'redo', source: 'mistakes', subject: s } })));
    (S.resume || []).slice(0, 3).forEach(r => {
      const left = r.seconds_left ? ` · ${Math.ceil(r.seconds_left / 60)} min left` : '';
      rows.append(h('div', { class: 'row' }, h('span', { class: 'v grow', text: `${KIND[r.kind] || 'Set'} · ${N(r.answered)} / ${N(r.total)} answered${left}` }),
        btn('Resume', { href: r.href || `/practice/session/?id=${encodeURIComponent(r.id)}` })));
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
      if (!ACC.verified) kids.push(h('p', { class: 'help' }, h('span', { class: 'odot', 'aria-hidden': 'true' }),
        h('a', { class: 'link', href: '/me/settings/#account', text: 'Add your email' }), ': it’s how you sign in now.'));
      const live = DEV && DEV.items ? DEV.items.filter(d => !d.revoked).length : 0;
      if (live > 1) kids.push(h('p', {}, h('a', { class: 'link', href: '/me/settings/#devices', text: `Signed in on ${live} devices` })));
      kids.push(prefsRow(), h('div', { class: 'card-foot' }, btn('Manage', { href: '/me/settings/#account' }),
        btn([ic('signout'), ' Sign out'], { quiet: true, onClick: () => UI.signOut() })));
    } else {
      // email is the only way in (2026-10-20): a learner from before it adds an address to keep access
      kids.push(h('p', { text: 'This device only. Add your email: it’s how you sign in now, here and on any device.' }),
        h('div', { class: 'acts mt' }, btn('Add your email', { primary: true, href: '/me/settings/#account' })), prefsRow(),
        h('div', { class: 'card-foot' }, btn('Share with a parent or tutor', { quiet: true, href: '/me/settings/#privacy' }),
          btn('Leave this device…', { quiet: true, onClick: () => UI.signOut() })));
    }
    fill('account', kids);
    said('account', ACC.saved ? 'Saved' : 'This device only');
  };
  /* ================================================================ Practice defaults (Shell 3.4, U15, R31)
     One row in Account: the stage or mode and the set length; every key is a row in Settings › Practice. */
  function prefsRow() {
    const s = SHELL && SHELL.stage, pr = UI.prefs.now() || {};
    const names = { learn: 'Learn', build: 'Build', test: 'Test-like', final: 'Final week', custom: 'Custom' };
    const mode = s && s.name && pr.stage_auto !== false ? s.name : pr.mode;
    const bits = [mode && names[mode] ? names[mode] : null, setLen() ? `${setLen()} a set` : null].filter(Boolean);
    return h('div', { class: 'rows prefs-row', id: 'prefs' }, h('div', { class: 'row' }, h('span', { class: 'k', text: 'Practice and test defaults' }),
      h('span', { class: 'v grow', text: bits.join(' · ') || 'Mode, clock and tests' }), btn('All settings', { quiet: true, href: '/me/settings/#practice' })));
  }

  /* ================================================================ Skills (Shell 3.5, U4, U5) */
  let skillView = ls.get('satf.me.skills', null);
  const openDoms = new Set(ls.get('satf.me.doms', []));
  let skillsShown = 5;   // the points list starts at five skills; Show more adds five
  PAINT.skills = () => {
    if (!ready('skills', 'summary')) return;
    const X = part(), g = X.gains || null, DOMS = X.domains || [];
    const byTopic = {};
    DOMS.forEach(d => d.skills.forEach(s => { byTopic[s.topic] = s; }));
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
    acts('skills', ...head);
    let nRow = 0;
    const row = (s, extra = {}) => {
      const el = UI.skillRow(null, { topic: s.topic, name: tn(s.topic), mastery: s.mastery, answered: s.answered, right: s.right, open: s.traps, ...extra },
        { practise: RO ? null : { count: setLen(), label: `Practise · ${setLen()}`, body: subj({ topics: [s.topic], count: setLen(), adaptive: true, source: 'skill' }) },
          href: RO ? null : `/results/#${s.topic}` });
      // "Not started" already says it: the kit's "no answers yet" beside it is the same fact twice (decision 7)
      if (!s.answered) { const m = el.querySelector('.skill-m .meta'); if (m) m.remove(); }
      // with nothing answered anywhere, the empty bars say it; nineteen "Not started" would not
      if (!s.answered && !S.stats.answered) { const w = el.querySelector('.skill-word'); if (w) w.remove(); }
      // no grey bar until a skill has answers: "Not started" says it
      if (!s.answered) { const b = el.querySelector('.skill-m .mbar'); if (b) b.remove(); }
      // the first row keeps its Practise in view; the others show it on hover or focus (always on touch)
      el.classList.add('reveal-host');
      const side = el.querySelector('.skill-side');
      if (nRow++ && !RO && side && side.lastElementChild) side.lastElementChild.classList.add('reveal');
      return [el, more(s)];
    };
    function more(s) {
      const bits = [];
      if (s.trend14 !== null && s.trend14 !== undefined && Math.abs(s.trend14) >= 0.05) bits.push(h('span', { text: `${s.trend14 > 0 ? '▲' : '▼'} 14 days` }));
      if (s.last5 && s.last5.length) bits.push(h('span', { class: 'last5', role: 'img', 'aria-label': `Last ${s.last5.length}: ${s.last5.map(x => (x ? 'right' : 'wrong')).join(', ')}` },
        s.last5.map(x => h('i', { class: x ? 'y' : 'n', text: x ? '✓' : '✕' }))));
      if (s.fading && !RO) bits.push(h('span', { text: `Fading${s.last ? ` · last ${day(s.last)}` : ''}` }), btn('Keep warm · 3', { quiet: true, body: subj({ pool: 'review', topics: [s.topic], count: 3, source: 'review' }) }));
      if (s.answered && s.answered < 5 && !RO) bits.push(btn('Try 5 more', { quiet: true, body: subj({ topics: [s.topic], count: 5, source: 'skill' }) }));
      return bits.length ? h('div', { class: 'sk-x' }, bits) : null;
    }
    const kids = [];
    if (!g && !RO) kids.push(h('p', { class: 'soft' }, 'Answer 30 questions and this shows where your points are.'),
      h('div', { class: 'card-foot' }, btn(`Today’s set · ${setLen()}`, { body: subj({ source: 'coach', count: setLen() }) })));
    // Sharpen (U5): 12 questions over the 4-6 skills with the most test weight and the fewest answers
    const nOf = s => s.evidence ?? s.answered ?? 0;
    const thin = Object.values(byTopic).filter(s => nOf(s) < 10);
    if (thin.length && S.stats.answered && !RO) {
      const share = t => ((g && g.skills.find(x => x.topic === t)) || {}).per_test || 1;
      const topics = thin.map(s => [s.topic, share(s.topic) * (1 - nOf(s) / 10)]).sort((a, b) => b[1] - a[1]).slice(0, 6).map(x => x[0]);
      kids.push(h('p', { class: 'help sharpen' }, `${thin.length === 1 ? '1 skill needs' : `${thin.length} skills need`} more answers: 12 questions, about ${rwOn() ? 14 : 19} min.`,
        btn('Sharpen · 12', { quiet: true, body: subj({ source: 'probe', topics, count: 12, order: 'mixed' }) })));
    }
    if (view === 'points') {
      const ranked = g.skills.filter(x => x.evidence >= 5 && byTopic[x.topic]).sort((a, b) => b.gain - a.gain);
      ranked.slice(0, skillsShown).forEach((x, i) => {
        const [el, ex] = row(byTopic[x.topic], { gain: x.gain, per_test: x.per_test, need_right: x.to_strong, minutes: x.minutes, accuracy: x.accuracy });
        if (i === 0 && x.gain >= 5) { const side = el.querySelector('.skill-side'); if (side) side.prepend(h('span', { class: 'badge', text: 'Most points' })); }
        kids.push(el, ex);
      });
      if (ranked.length > 5) {   // Show more adds five; Show less goes back to five
        const more_ = ranked.length > skillsShown ? btn(`Show ${Math.min(5, ranked.length - skillsShown)} more`, { quiet: true, onClick: () => { skillsShown += 5; paint('skills'); } }) : null;
        const less_ = skillsShown > 5 ? btn('Show less', { quiet: true, onClick: () => { skillsShown = 5; paint('skills'); } }) : null;
        kids.push(h('div', { class: 'more-row' }, more_, less_));
      }
      const rest = Object.values(byTopic).filter(s => !ranked.some(x => x.topic === s.topic));
      const started = rest.filter(s => s.answered), fresh = rest.filter(s => !s.answered);
      if (started.length) kids.push(h('details', { class: 'skills-rest' },
        h('summary', { text: `${pl(started.length, 'skill')} with under 5 answers` }), started.flatMap(s => row(s))));
      if (fresh.length) kids.push(h('details', { class: 'skills-rest' }, h('summary', { text: `${pl(fresh.length, 'skill')} not started` }),
        fresh.map(s => row(s)[0])));
      if (g.top3 && g.top3.topics && g.top3.topics.length && !RO) kids.push(h('div', { class: 'card-foot' },
        btn('Practise the top 3 · 15', { body: subj({ topics: g.top3.topics, count: 15, order: 'mixed', adaptive: true, source: 'skill' }) })));
    } else if (S.stats.answered || RO) {
      DOMS.forEach(d => {
        const weak = d.skills.filter(s => s.answered).sort((a, b) => a.mastery - b.mastery)[0];
        const open = openDoms.has(d.domain);
        const box = h('div', { class: 'dom', 'data-open': open ? '' : null });
        const hd = h('button', { type: 'button', class: 'dom-h', 'aria-expanded': String(open) },
          h('span', { class: 'nm', text: d.domain }),
          h('span', { class: 'mbar6', role: 'img', 'aria-label': `${d.domain}: ${UI.masteryWord(d.mastery, d.answered)}` }, h('i', { style: `--m: ${d.mastery || 0}` })),
          h('span', { class: 'meta', text: d.answered ? `${N(d.right)} of ${N(d.answered)} right` : '' }),
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
    // bottom right, on the same row as the card's own button when it has one
    const allB = btn('All skills in Results', { quiet: true, href: `/results/${rwOn() ? '?subject=rw' : ''}#skills` });
    if (allB.classList) allB.classList.add('push');
    const foot = kids.find(k => k && k.classList && k.classList.contains('card-foot'));
    if (foot) foot.append(allB);
    else kids.push(h('div', { class: 'card-foot' }, allB));
    fill('skills', kids);
    if (sorted.length >= 2) {
      const best = sorted[sorted.length - 1], worst = sorted[0];
      said('skills', `Weakest ${tn(worst.topic)} ${N(worst.right)} / ${N(worst.answered)} · strongest ${tn(best.topic)}`);
    } else said('skills', answered.length ? `${tn(answered[0].topic)} started` : 'Not started');
  };

  /* ================================================================ Test-day readiness (U8) */
  const readyOpen = new Set(ls.get('satf.me.readydoms', []));
  PAINT.readiness = () => {
    if (!ready('readiness', 'summary', 'types')) return;
    const cov = part().coverage || {};
    const types = cov.types || {};
    const counts = { unmet: 0, met: 0, ready: 0 };
    const gaps = [];
    const grid = h('div', { role: 'grid', 'aria-label': 'Question types by skill' });
    // Math's types come from the shell's catalogue; R&W's name themselves in the summary (topic, name, about)
    const byTopic = rwOn() ? {} : TYPES.byTopic;
    if (rwOn()) Object.entries(types).forEach(([template, c]) => (byTopic[c.topic] = byTopic[c.topic] || []).push({ template, name: c.name, about: c.about }));
    const doms = rwOn() ? UI.RW_DOMAINS.map(d => [d.name, d.skills.map(slug => ({ slug }))])
      : UI.DOMAINS.map(([dom]) => [dom, UI.TOPICS.filter(t => t.domain === dom)]);
    doms.forEach(([dom, topics]) => {
      // each domain folds to one line ("Algebra · 3 / 105 ready") and starts closed
      const sum = h('summary', { class: 'rd-sum' });
      const box = h('details', { class: 'ready-dom' }, sum);
      box.open = readyOpen.has(dom);
      box.addEventListener('toggle', () => { if (box.open) readyOpen.add(dom); else readyOpen.delete(dom); ls.set('satf.me.readydoms', [...readyOpen]); });
      let domReady = 0, domTotal = 0;
      topics.forEach(t => {
        const list = (byTopic[t.slug] || []).map(x => {
          const c = types[x.template] || {};
          const status = (c.right || 0) >= 2 ? 'ready' : c.met ? 'met' : 'unmet';
          counts[status] += 1;
          if (c.open && status === 'met') counts.open = (counts.open || 0) + 1;
          if (status !== 'ready') gaps.push(x.template);
          return { template: x.template, label: x.name, status, open: c.open || null, c };
        }).sort((a, b) => ({ unmet: 0, met: 1, ready: 2 }[b.status] - { unmet: 0, met: 1, ready: 2 }[a.status]));
        if (!list.length) return;
        const at = UI.atlas(null, list, { sm: true, label: tn(t.slug),
          tip: x => [x.label, x.c.met ? `met ${x.c.met} · right ${x.c.right || 0}` : 'not met yet', x.c.last ? `last ${day(x.c.last)}` : null, x.open ? 'open mistake' : null].filter(Boolean).join(' · '),
          onPick: RO ? null : x => typeSheet(x) });
        const nReady = list.filter(x => x.status === 'ready').length, unmet = list.filter(x => x.status === 'unmet').length;
        domReady += nReady; domTotal += list.length;
        box.append(h('div', { class: 'atlas-row' }, h('span', {}, tn(t.slug),
          unmet ? btn(`Practise ${Math.min(unmet, setLen())} unmet`, { quiet: true, body: subj({ topics: [t.slug], pool: 'untried', count: Math.min(unmet, setLen()), source: 'map' }) }) : null),
          at.el, h('span', { text: `${nReady} / ${list.length} ready` })));
      });
      sum.replaceChildren(h('span', { class: 'rd-nm', text: dom }),
        h('span', { class: 'rd-bar', role: 'img', 'aria-label': `${domReady} of ${domTotal} ready` }, h('i', { style: `width: ${domTotal ? Math.round(domReady / domTotal * 100) : 0}%` })),
        h('span', { class: 'rd-n', text: `${N(domReady)} / ${N(domTotal)} ready` }), h('span', { class: 'rd-chev', 'aria-hidden': 'true' }));
      grid.append(box);
    });
    const legend = h('div');
    UI.legend(legend, ['unmet', 'met', 'ready', { key: 'open', label: 'Met · open mistake' }], counts);   // an orange dot: met, with a mistake still open
    const total = counts.unmet + counts.met + counts.ready;
    const readyPct = Math.round((cov.readiness || 0) * 100);
    if (!(counts.met + counts.ready)) {
      fill('readiness', h('p', { class: 'soft' }, `Each of the ${N(total)} question types you meet fills in here.`),
        RO ? null : h('div', { class: 'card-foot' }, btn(`Today’s set · ${setLen()}`, { quiet: true, body: subj({ source: 'coach', count: setLen() }) })));
      said('readiness', 'no question types met yet');
      return;
    }
    fill('readiness',
      h('p', { class: 'acts' }, fact(h('span', { class: 'big', text: `${readyPct}%` }), rwOn() ? 'readiness:rw' : 'readiness', 'Test-day readiness'),
        h('span', { class: 'meta', text: `${N(counts.met + counts.ready)} of ${N(total)} question types met` })),
      legend, grid,
      RO ? null : h('div', { class: 'card-foot' }, gaps.length
        ? btn('Practise my biggest gaps', { body: subj({ templates: gaps.slice(0, Math.min(120, setLen())), count: setLen(), source: 'map' }) })
        : h('p', { class: 'soft', text: 'Every type ready.' })));
    said('readiness', `${readyPct}% ready · ${N(counts.met + counts.ready)} of ${N(total)} types met`);
  };
  function typeSheet(x) {
    UI.sheet({ title: x.label, size: 'm',
      body: b => {
        b.append(UI.skel(null, 'lines:4'));
        UI.api(`/types/${encodeURIComponent(x.template)}/example`).then(r => {
          // the key stays out: the example is to recognise the form, not to answer (U8)
          const { answer, rationale, reasons, spr_reasons, steps, step_of, ...q } = r.question || {};
          const host = h('div', { class: 'ex-q' });
          const plain = () => host.replaceChildren(h('p', { text: q.stem || '' }),
            (q.choices || []).length ? h('ol', { type: 'A' }, q.choices.map(c => h('li', { text: c }))) : null);
          b.replaceChildren(...[h('p', { class: 'k', text: 'An example, new numbers each time' }), host,
            h('p', { class: 'help', text: [x.c.met ? `Met ${x.c.met} · right ${x.c.right || 0}` : 'Not met yet', x.open ? 'an open mistake' : null].filter(Boolean).join(' · ') })]);
          // the one question renderer, so figures, tables, math and fractions read as they do in a set
          // shown to read, not to answer: inert, with the entry and help rows hidden (me.css .ex-q)
          UI.need('question').then(() => { UI.workspace(host, q, { mode: 'review', hidden: true, bar: false, toolbar: false, head: false }); host.inert = true; })
            .catch(plain);
        }, () => b.replaceChildren(h('p', { class: 'soft', text: 'Couldn’t load an example.' })));
      },
      actions: [{ label: 'Log a mistake on it', onClick: () => { UI.quick('mistake'); } },
                { label: 'Practise 5 of this type', primary: true, onClick: () => start(subj({ templates: [x.template], count: 5, source: 'map' })).then(() => false) }] });
  }

  /* ================================================================ Score trend (Shell 3.6, U9) */
  PAINT.trend = () => {
    if (!ready('trend', 'summary')) return;
    const X = part(), sc = X.score || S.score;
    const pts = (sc.points || []).map(p => ({ id: p.session || p.id, at: p.at, low: p.low, high: p.high, kind: p.kind === 'outside' ? 'outside' : p.kind,
      label: KIND[p.kind] || 'Sitting', href: !RO && (p.session || p.id) && p.kind !== 'outside' ? `/results/report/?id=${encodeURIComponent(p.session || p.id)}` : null }));
    const host = h('div');
    fill('trend', host);
    const g = S.goals || {};
    const o = { height: phone() ? 160 : 200, target: X.target, exam: g.exam_date,
      empty: { text: 'Your first module puts a point here.', action: RO ? null : { label: 'Start a module', href: `/tests/${rwOn() ? '?subject=rw' : ''}` } },
      onPick: p => { if (p.href) location.href = p.href; }, label: `${UI.subjectLabel(SUBJ)} score over time` };
    if (sc.projection !== undefined) o.projection = pts.length ? sc.projection : undefined;
    if (sc.gaps) o.gaps = sc.gaps;
    UI.bandChart(host, pts, o);
    said('trend', pts.length ? pl(pts.length, 'scored sitting') : 'No sittings yet');
  };

  /* ================================================================ Pace (U7) */
  PAINT.pace = () => {
    if (!ready('pace', 'summary')) return;
    const pc = part().pace, rw = rwOn();
    const skills = pc && pc.skills ? Object.entries(pc.skills).filter(([, v]) => v && v.n >= 5) : [];
    if (skills.length < 3) {
      fill('pace', h('p', { class: 'soft', text: 'Answer with the clock on to see where your minutes go.' }),
        h('div', { class: 'card-foot' }, btn('Timed set · 10', { body: subj({ count: 10, timing: 'pace', source: 'skill' }) })));
      said('pace', 'Not enough timed answers yet');
      return;
    }
    const f = pc.forecast || {};
    // ponytail: progress.pace forecasts on Math's module (22 slots, 35:00) for both subjects, so R&W shows no forecast until it is per subject
    const head = f.seconds && !rw ? `At your pace a module takes ${UI.mmss(f.seconds)} of ${UI.mmss(f.limit || 2100)}${f.blanks ? `: about ${pl(f.blanks, 'question')} left blank` : ''}.` : '';
    const host = h('div');
    const QN = { slow_right: ['You know it, slowly', 'Speed drill · 8', t => subj({ topics: [t], count: 8, timed: true, minutes: rw ? 7 : 9, source: 'skill' })],
      fast_wrong: ['Rushing', 'Careful set · 8', t => subj({ topics: [t], count: 8, feedback: 'instant', source: 'skill' })],
      slow_wrong: ['Time sink', 'Learn it untimed · 8', t => subj({ topics: [t], count: 8, source: 'skill' })],
      fast_right: ['Banked', 'Keep warm · 3', t => subj({ pool: 'review', topics: [t], count: 3, source: 'review' })] };
    const points = skills.map(([t, v]) => ({ id: t, topic: t, label: tn(t), x: (v.median_ms || v.ms || 0) / 1000, y: v.accuracy, n: v.n }));
    fill('pace', head ? h('p', { text: head }) : null, host,
      pc.guess && pc.guess.n >= 20 ? h('p', { class: 'help', text: `Your guesses are right ${Math.round(100 * pc.guess.right / pc.guess.n)}% of the time (chance is 25%).` }) : null,
      pc.struck2 && pc.struck2.n >= 20 ? h('p', { class: 'help', text: `When you strike two options first you’re right ${Math.round(100 * pc.struck2.right / pc.struck2.n)}%: strike, then guess.` }) : null,
      // half a module at the section's clock: Math 11 at 95 s, R&W 14 at 71 s, both about 17 minutes
      h('div', { class: 'card-foot' }, btn(`Pacing drill · ${rw ? 14 : 11}`, { body: subj({ mix: 'blueprint', count: rw ? 14 : 11, timed: true, minutes: 17, source: 'skill' }) }),
        RO ? null : h('span', { class: 'meta', text: '17 min, timed like a module' })));
    if (UI.quadrant) UI.quadrant(host, points, { x: 'seconds', xRef: rw ? 71 : 95, y: 'accuracy', label: 'Seconds and accuracy by skill',
      names: Object.fromEntries(Object.entries(QN).map(([k, v]) => [k, v[0]])),
      action: RO ? null : (p, q) => (QN[q] ? { label: QN[q][1], onClick: () => start(QN[q][2](p.topic)) } : null) });
    said('pace', head || `${skills.length} skills timed`);
  };

  /* ================================================================ What keeps catching you (Shell 3.7, U6) */
  PAINT.catching = () => {
    if (!ready('catching', 'summary')) return;
    const list = part().catching || (rwOn() ? [] : S.catching || []);
    // the gauntlet replays named Math traps; R&W misses are unnamed, so R&W has none
    acts('catching', list.length && !rwOn() ? btn('Trap gauntlet · 10', { body: { source: 'gauntlet', count: 10 } }) : null);
    fill('catching', list.length ? h('div', { class: 'list' }, list.map(x => h('div', { class: 'lrow' },
      x.open ? h('span', { class: 'odot', 'aria-label': 'Open' }) : h('span', { class: 'chk', 'aria-label': 'Fixed', text: '✓' }),
      h('div', {}, h('p', { class: 't', text: x.label || x.reason || 'A named mistake' }),
        h('p', { class: 'd' }, tag(x.topic), h('span', { text: `×${N(x.hits)}` }), x.last ? h('span', { text: `last ${day(x.last)}` }) : null,
          x.source === 'outside' ? h('span', { text: 'Logged by you' }) : null)),
      h('span', { class: 'lside' }, btn('Practise', { body: subj({ templates: [x.template], count: 3, source: 'mistakes' }) }))))) :
      h('p', { class: 'soft', text: rwOn() ? 'No R&W mistakes yet.' : 'No named mistakes yet. When you miss, the mistake gets a name here.' }),
      list.length && !RO ? h('div', { class: 'card-foot' }, btn('All mistakes', { quiet: true, href: `/review/${rwOn() ? '?subject=rw' : ''}` })) : null);
    said('catching', list.length ? list[0].label || '' : 'No mistakes yet');
  };

  /* ================================================================ Your habits (U6) */
  PAINT.habits = () => {
    if (!ready('habits', 'summary')) return;
    // habits are families of Math reasons; under R&W the part stays out of sight
    if (C.habits) C.habits.el.hidden = rwOn();
    if (rwOn()) return;
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
  // the badge art is shared with Compete (compete-ui.js UI.compete.badgeIcon): one drawing per achievement
  const badgeIcon = (a, on) => UI.compete.badgeIcon(a, on);
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
      const list = h('div', { class: 'ach-list' });
      const chipHost = h('div', { class: 'chips-host' });
      const draw = () => {
        const pick = all.filter(a => show === 'all' || (show === 'earned' ? a.earned && a.earned.length : a.next && !(a.earned && a.earned.length)));
        const groups = {};
        pick.forEach(a => { (groups[a.group || 'Other'] = groups[a.group || 'Other'] || []).push(a); });
        list.replaceChildren(...Object.entries(groups).map(([g, items]) => h('section', {}, h('h3', { class: 'sub-h', text: g }),
          items.map(a => h('div', { class: 'brow' }, badgeIcon(a, a.earned && a.earned.length),
            h('div', { class: 'gap tight' }, h('p', { class: 'nm', text: a.name }),
              a.rule && a.rule !== a.name ? h('p', { class: 'help', text: a.rule }) : null,
              h('p', { class: 'ladder' }, (a.tiers || []).map((t, i) => h('span', { class: i < (a.earned || []).length ? 'on' : '', text: N(t) }))),
              (a.earned || []).length ? h('p', { class: 'meta', text: (a.earned || []).map(e => day(e.at)).filter(x => x !== UI.NONE).join(' · ') }) : null,
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
      if (!S || !S.days) { C.activity.body.hidden = true; return; }
      ACT = ACT || { days: S.days, active_days: S.stats.active_days };
    }
    if (!ready('activity', 'activity')) return;
    if (!ACT.active_days && !(ACT.days || []).some(d => d && (d.n || d.count || d.q))) {
      fill('activity', h('p', { class: 'soft', text: 'Every day you study lights up a square here.' }));
      said('activity', 'No activity yet');
      return;
    }
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
      const chipHost = h('div', { class: 'chips-host' });
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
      // a session is one row: the title (its link), the result in the right-hand slot, what it changed under it,
      // and Again / Follow up shown on hover or focus (always on touch)
      const acts0 = RO || (!x.again && !x.follow_up) ? null : h('div', { class: 'fx reveal' },
        x.again ? btn('Again · new numbers', { quiet: true, body: { ...x.again, source: 'review' } }) : null,
        x.follow_up ? btn(`Follow up · ${Math.min(3, e.opened || 3)}`, { quiet: true, body: { ...x.follow_up, source: 'review' } }) : null);
      kids.push(h('div', { class: 'lrow feed-row reveal-host' },
        href ? h('a', { class: 't feed-link', href, text: title }) : h('p', { class: 't', text: title }),
        h('span', { class: 'feed-n', text: x.detail ? score(x.detail) : '' }),
        eff.length || acts0 ? h('div', { class: 'feed-sub' }, h('p', { class: 'd', text: eff.join(' · ') }), acts0) : null));
    });
    const empty = FEED.kind === 'unread' ? h('p', { class: 'soft', text: 'Nothing new since you last looked.' })
      : h('div', { class: 'gap' }, h('p', { class: 'soft', text: 'Nothing yet. Your first set shows up here.' }),
        btn(`Start today’s set · ${setLen()}`, { body: { source: 'coach', count: setLen() } }));
    fill('recent', C.recent.chips || null, h('div', { class: 'list' }, kids.length ? kids : empty),
      FEED.next && !RO ? h('div', { class: 'card-foot' }, btn('Show more', { onClick: (ev, b) => { b.setAttribute('aria-busy', 'true'); loadFeed(false); } })) : null);
    said('recent', FEED.items.length ? FEED.items[0].title : 'Nothing yet');
  };

  /* ---- a signed-out device paints none of the student's data (Shell 3 States) */
  addEventListener('satf:retired', () => Object.keys(C).forEach(id => (C[id].part ? fill(id) : fill(id, h('p', { class: 'soft' }, 'This device was signed out. ',
    h('a', { class: 'link', href: '/signin/', text: 'Sign in' }), ' to see your progress.')))));

  /* ---- go */
  if (RO) {
    UI.api(`/shared/${encodeURIComponent(SHARE)}`).then(d => {
      S = d;
      if (window.ME_SHARED) window.ME_SHARED(d);
      Object.keys(C).forEach(id => paint(id));
      loadTypes();
    }, e => { if (window.ME_SHARED) window.ME_SHARED(null, e); });
    return;
  }
  UI.shell({ page: 'me', ownPrimary: true, sections: CHIPS.filter(id => C[id]).map(id => ({ id, label: (CARDS.find(c => c.id === id).chip) || CARDS.find(c => c.id === id).title })) });
  // a pop open in the You card (board name, avatar) keeps its anchor: that card waits for the pop to close
  UI.onShell(d => { SHELL = d; paint(...(document.querySelector('#you .card-body [aria-expanded="true"]') ? [] : ['you']), 'goals', 'saved', 'account'); });
  loadSummary(); loadProfile(); loadAccount(); loadActivity(); loadWeek(); loadTypes(); loadFeed(true);
  // a hash opens its card, folded or not; older anchors and the ones other pages and the server send still land
  // (#achievements, #types, #atlas, #boards, #route, #points-<topic>, #preferences, the cards merged into others)
  const ALIAS = { achievements: 'badges', types: 'readiness', coverage: 'readiness', atlas: 'readiness', feed: 'recent',
    preferences: 'account', prefs: 'account', boards: 'you', route: 'goals' };
  const TAB = { achievements: 'badges', week: 'week', settings: '/me/settings/' };
  const tab = TAB[query.get('tab')];
  if (tab && tab[0] === '/') location.replace(tab);
  else if (tab && !location.hash) history.replaceState(null, '', `#${tab}`);
  const toHash = (wait) => {
    let id = location.hash.slice(1);
    if (/^points-/.test(id)) id = 'skills';
    const el = id && (document.getElementById(id) || document.getElementById(ALIAS[id]));
    const card = el && el.closest('.card');
    if (card) { card.dispatchEvent(new CustomEvent('satf:open')); setTimeout(() => el.scrollIntoView({ block: 'start' }), wait); }
  };
  toHash(300);
  addEventListener('hashchange', () => toHash(0));
})();
