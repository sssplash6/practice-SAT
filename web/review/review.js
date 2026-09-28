/* ============================================================================
   SAT Freshman -- the Review hub (/review/): spec 3.9, review.md V1-V19, R2, R5, R23.

   One page: a header with today's review (the minutes seg and Start review), notes
   (new misses to walk, a worksheet waiting), six tiles that are the tabs (Due, Redo,
   Marked, Saved, History, Fixed; each number said once, decision 7), the open tab's head,
   its filters, its list beside the question pane (UI.review mode 'pane', F3), and an
   action bar that starts a set from the list or a selection (the drill body, R10).

   Endpoints (S10's api_review.py): /api/review/{counts,due,snooze,redo,marked,saved,fixed,
   history,item,family,ledger,calibration,seen,why,walk,spot}, /api/session/{sid}/void,
   /api/saved, /api/flags, /api/mistakes/*, /api/notes, /api/sets, /api/drill.
   Parts another owner has not landed degrade quietly (UI.x && UI.x(...)).
   ========================================================================== */
(() => {
  'use strict';
  const doc = document;
  const h = UI.h;
  const $ = id => doc.getElementById(id);
  const mq = q => matchMedia(q).matches;
  const phone = () => mq('(max-width: 759px)');
  const wide = () => mq('(min-width: 960px)');
  const fmtN = n => (typeof n === 'number' ? n.toLocaleString('en-US') : String(n ?? ''));
  const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : '');
  const plural = (n, one, many) => `${fmtN(n)} ${n === 1 ? one : (many || one + 's')}`;
  const day = d => (d ? UI.date(d, 'short') : '');
  const mmss = ms => (ms ? UI.mmss(Math.round(ms / 1000)) : '—');
  const toast = (t, o) => UI.toast && UI.toast(t, o);
  const reasonOf = e => {
    const d = e && e.detail;
    const r = (d && typeof d === 'object' && (d.reason || d.message)) || (typeof d === 'string' ? d : null);
    return r ? cap(String(r).replace(/_/g, ' ')) : 'That didn’t work. Try again.';
  };
  const ss = {
    get(k, d) { try { const v = sessionStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  // fractions in math text stack in the line when the kit offers it (the user's rule, 2026-09-28)
  const mtext = (el, text) => {
    const t = String(text ?? '');
    const got = UI.fracText ? UI.fracText(t) : null;
    if (got instanceof Node) el.replaceChildren(got); else el.textContent = t;
    return el;
  };
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const tierBit = t => (TIER[t] ? (UI.dbars ? UI.dbars(t) : h('span', { text: TIER[t] })) : null);
  const SRC = { practice: 'Practice', section: 'Section', module: 'Module', diagnostic: 'Diagnostic', challenge: 'Challenge', qotd: 'Question of the day',
    review: 'Review', shared: 'Shared set', worksheet: 'Worksheet', due: 'Today’s review', outside: 'Logged by you', test: 'Custom test', mock: 'Section' };
  const srcWord = s => SRC[s] || cap(s || '');
  const LET = 'ABCDE';
  const TOPIC = t => (UI.TOPIC && UI.TOPIC[t]) || null;
  const dshort = d => ((UI.DOMAINS || []).find(x => x[0] === d) || [])[1] || d;

  /* ------------------------------------------------------------ state */
  const TABS = [
    { id: 'due', k: 'Due today', short: 'Due' }, { id: 'redo', k: 'Redo', short: 'Redo' }, { id: 'marked', k: 'Marked', short: 'Marked' },
    { id: 'saved', k: 'Saved', short: 'Saved' }, { id: 'history', k: 'History', short: 'History' }, { id: 'fixed', k: 'Fixed', short: 'Fixed' },
  ];
  const S = {
    tab: null, counts: null, countsErr: false, due: null, dueErr: false, prefs: {}, me: null, minutes: 10,
    lists: {}, filters: {}, bar: {}, player: null, playerTab: null, cache: new Map(), token: 0, ledger: null,
    fb: null, marked: 'miss', savedCard: 'all', savedView: 'questions', sinceCal: '30', open: null,
  };
  const Q = () => new URLSearchParams(location.search);
  const selKey = tab => `satf.review.sel.${tab}`;
  const selDefaultAll = tab => tab === 'redo' || tab === 'fixed';
  function sel(tab) {
    if (!S[`sel_${tab}`]) {
      const s = ss.get(selKey(tab), null);
      S[`sel_${tab}`] = s && typeof s === 'object' ? { all: !!s.all, ids: new Set(s.ids || []) } : { all: selDefaultAll(tab), ids: new Set() };
    }
    return S[`sel_${tab}`];
  }
  const saveSel = tab => { const s = sel(tab); ss.set(selKey(tab), { all: s.all, ids: [...s.ids].slice(0, 500) }); };
  const isSel = (tab, key) => { const s = sel(tab); return s.all ? !s.ids.has(key) : s.ids.has(key); };
  function setSel(tab, key, on) {
    const s = sel(tab);
    if (s.all ? on : !on) s.ids.delete(key); else s.ids.add(key);
    saveSel(tab);
  }
  function selCount(tab) {
    const L = S.lists[tab];
    if (!L) return 0;
    const s = sel(tab);
    return s.all ? Math.max(0, L.total - [...s.ids].filter(k => L.items.some(r => keyOf(tab, r) === k)).length) : s.ids.size;
  }
  const selRows = tab => ((S.lists[tab] || {}).items || []).filter(r => isSel(tab, keyOf(tab, r)));
  function keyOf(tab, r) {
    if (tab === 'due') return r.key;
    if (tab === 'redo' || tab === 'fixed') return String(r.id);
    if (tab === 'marked') return `${r.session}|${r.qid}`;
    if (tab === 'saved') return `${r.template}:${r.seed}`;
    return String(r.id);
  }

  /* ------------------------------------------------------------ boot */
  async function boot() {
    paintStartSkeleton();
    paintTabs();
    const [prefs, me] = await Promise.all([UI.prefs().catch(() => ({})), (UI.me ? UI.me() : Promise.resolve(null)).catch(() => null)]);
    S.prefs = prefs || {};
    S.me = me;
    S.minutes = Number.isInteger(S.prefs.review_minutes) ? S.prefs.review_minutes : 10;
    await Promise.all([loadCounts(), loadDue()]);
    const want = Q().get('tab');
    const tab = TABS.some(t => t.id === want) ? want : (S.due && S.due.left > 0 ? 'due' : 'redo');
    S.open = Q().get('open');
    openTab(tab, { push: false });
    registerKeys();
    addEventListener('popstate', () => {
      const t = Q().get('tab');
      if (t && t !== S.tab && TABS.some(x => x.id === t)) openTab(t, { push: false });
    });
    matchMedia('(max-width: 759px)').addEventListener('change', () => { paintBar(); paintListHead(); });
    matchMedia('(min-width: 960px)').addEventListener('change', () => { dropPlayer(); syncPane(); });
    addEventListener('satf:prefs', e => {
      const m = e.detail && e.detail.prefs && e.detail.prefs.review_minutes;
      if (Number.isInteger(m) && m !== S.minutes) { S.minutes = m; loadDue().then(afterDue); }
    });
  }

  async function loadCounts() {
    try { S.counts = await UI.api('/review/counts'); S.countsErr = false; }
    catch (_) { S.countsErr = true; }
    paintTabs(); paintNotes();
    if (S.due) paintStart();
  }
  async function loadDue() {
    try {
      S.due = await UI.api('/review/due');
      S.dueErr = false;
      // the minutes seg re-cuts the same frozen order on the server (V1); the pref is what it reads
      if (S.due.minutes !== undefined && S.due.minutes !== null && S.due.minutes !== S.minutes) S.minutes = S.due.minutes;
    } catch (_) { S.dueErr = true; }
    paintStart(); paintTabs();
  }
  function afterDue() {
    if (S.tab === 'due') { paintHead(); paintList(); syncPane(); }
  }
  let refreshT = 0;
  function refreshSoon(list = true) {
    clearTimeout(refreshT);
    refreshT = setTimeout(async () => {
      await Promise.all([loadCounts(), loadDue()]);
      if (list && S.tab) { if (S.tab === 'due') afterDue(); else loadList(S.tab, { quiet: true }); }
    }, 400);
  }

  /* ------------------------------------------------------------ the header: today's review (V1) */
  function paintStartSkeleton() {
    const box = $('start');
    box.replaceChildren();
    if (UI.skel) { UI.skel(box, 'pill'); UI.skel(box, 'line'); }
  }
  const MINUTES = [5, 10, 15, 20, 30, 45, 60, 0];
  function startBody(boxMin) { return { source: 'due', box: boxMin || null }; }
  function startPlan() {
    const d = S.due, c = S.counts || {};
    const m = S.minutes;
    if (d && d.left > 0) {
      if (!m) return { label: 'All', body: startBody(0), all: true };
      return { label: `Start review · ${m} min`, body: startBody(m) };
    }
    const box = m || 10;
    if ((c.open || 0) > 0) return { label: `Fix ${fmtN(Math.min(c.open, (d && d.cap) || 6))} · ${box} min`, body: startBody(box) };
    return { label: `Keep going · ${box} min`, body: { source: 'next', box } };
  }
  function paintStart() {
    const box = $('start');
    box.replaceChildren();
    if (S.dueErr && !S.due) { UI.cardError ? UI.cardError(box, () => loadDue().then(afterDue), 'Today’s review didn’t load.') : null; return; }
    const d = S.due || {};
    // a new student has one way in, the empty state's start (the user's rule, 2026-09-28)
    if (S.counts && !S.counts.answers && !d.total) { box.hidden = true; return; }
    box.hidden = false;
    const segRow = h('div', { class: 'rh-opt' }, h('span', { class: 'k', text: 'Minutes' }));
    UI.seg(segRow, MINUTES.map(v => ({ value: v, label: v ? String(v) : 'All' })), {
      value: S.minutes, label: 'Review minutes',
      onChange: async v => {
        S.minutes = v;
        try { await UI.prefs.set({ review_minutes: v }); } catch (_) { toast('Not saved. Try again.'); }
        await loadDue();
        afterDue();
        paintTabs();
      },
    });
    const plan = startPlan();
    const main = h('button', { type: 'button', class: 'pill', 'aria-keyshortcuts': 'Shift+R' }, h('span', { text: plan.label }));
    main.addEventListener('click', () => start(plan.body, main));
    const more = h('button', { type: 'button', class: 'pill', 'aria-label': 'See today’s review before starting', 'aria-haspopup': 'dialog', title: 'See the list first' }, h('span', { 'aria-hidden': 'true', text: '▾' }));
    more.addEventListener('click', () => previewSheet(plan.body));
    const split = h('div', { class: 'rh-split' }, main, more);
    const meta = h('p', { class: 'rh-startmeta' });
    const bits = [];
    if (d.left > 0) {
      const k = d.kinds || {};
      if (k.check) bits.push(plural(k.check, 'check-in'));
      if (d.quick_wins) bits.push(plural(d.quick_wins, 'quick win'));
      if (d.closes) bits.push(`closes up to ${plural(d.closes, 'mistake')}`);
    }
    meta.textContent = bits.join(' · ');
    meta.hidden = !bits.length;
    box.append(segRow, split, meta);
    if (plan.all) allLabel(main, meta);
  }
  // All: every frozen key, then every open trap max(owed) times, at most 120 (V1): the preview counts it
  async function allLabel(btn, meta) {
    try {
      const p = await UI.api('/drill/preview', { method: 'POST', body: startBody(0), quiet: true });
      const n = p.count ?? p.total ?? (p.blocks ? p.blocks.length : null);
      const mins = p.minutes ? Math.round(p.minutes) : (n && S.due ? Math.round(n * S.due.median_s / 60) : null);
      if (n) btn.firstChild.textContent = `All · ${plural(n, 'question')}${mins ? ` · about ${mins} min` : ''}`;
    } catch (_) {}
  }
  async function start(body, btn) {
    if (btn) btn.setAttribute('aria-busy', 'true');
    try {
      const d = await UI.api('/drill', { method: 'POST', body });
      location.href = `/practice/session/?id=${encodeURIComponent(d.id)}`;
    } catch (e) {
      if (btn) btn.removeAttribute('aria-busy');
      toast(reasonOf(e));
      return e;
    }
    return null;
  }
  // the ▾: today's list as the set will serve it, one row per question, each with × to drop it (V1)
  async function previewSheet(body) {
    const drop = new Set();
    let data = null;
    const sheet = UI.sheet({
      title: 'Today’s review', size: 'm',
      body: async b => {
        b.append(h('p', { class: 'meta', text: 'Loading…' }));
        try { data = await UI.api('/drill/preview', { method: 'POST', body }); }
        catch (e) { b.replaceChildren(h('p', { class: 'help', text: reasonOf(e) })); return; }
        draw(b);
      },
      actions: [{ label: 'Start', primary: true, onClick: api => { start(Object.assign({}, body, drop.size ? { drop: [...drop] } : {})); return false; } }],
    });
    function draw(b) {
      b.replaceChildren();
      // the server's blocks when it sends them; else today's undone list, which the set serves first
      const blocks = data.blocks || data.items || ((S.due && S.due.items) || []).filter(x => !x.done && !x.snoozed);
      if (!blocks.length) { b.append(h('p', { class: 'help', text: 'Nothing to serve right now.' })); return; }
      const sum = h('p', { class: 'meta' });
      const list = h('ul', { class: 'rh-list', role: 'list' });
      const total = () => blocks.filter(x => !drop.has(x.key)).length;
      const paintSum = () => { sum.textContent = `${plural(total(), 'question')}${data.minutes ? ` · about ${Math.round(data.minutes)} min` : ''}`; };
      blocks.forEach(x => {
        const label = x.label || x.skill || x.name || x.template || '';
        const li = h('li', { class: 'rh-row has-x', style: 'grid-template-columns: 12px minmax(0,1fr)' }, h('span'),
          h('div', { class: 'rh-rb', style: 'cursor: default; grid-template-columns: minmax(0,1fr)' },
            h('div', {}, mtext(h('div', { class: 'l1' }), label), h('div', { class: 'l2' }, x.kind ? h('span', { text: KIND[x.kind] ? KIND[x.kind].text : cap(x.kind) }) : null, x.skill && x.skill !== label ? h('span', { text: x.skill }) : null))));
        if (x.key) {
          const xb = h('button', { type: 'button', class: 'x', 'aria-label': `Drop: ${label}`, text: '×' });
          xb.addEventListener('click', () => { if (drop.has(x.key)) { drop.delete(x.key); li.style.opacity = ''; xb.textContent = '×'; } else { drop.add(x.key); li.style.opacity = '.45'; xb.textContent = '↺'; } paintSum(); });
          li.append(xb);
        }
        list.append(li);
      });
      paintSum();
      b.append(sum, list);
    }
    return sheet;
  }

  /* ------------------------------------------------------------ notes under the header (V2, V18, V19) */
  let notesToken = 0;
  async function paintNotes() {
    const box = $('notes');
    const c = S.counts;
    const my = ++notesToken;
    if (!c) { box.replaceChildren(); return; }
    const out = [];
    if (c.new > 0) {
      const card = h('section', { class: 'card rh-walk', 'aria-label': 'New misses' });
      const txt = h('p', { text: `${plural(c.new, 'new miss', 'new misses')}` });
      const meta = h('span', { class: 'meta', text: `about ${Math.max(1, Math.round(c.new * 1.5))} min` });
      txt.append(meta);
      const go = h('button', { type: 'button', class: 'pill', text: 'Walk them · name each, then prove it' });
      go.addEventListener('click', () => walk({ new: true }, go));
      card.append(h('div', {}, txt), go);
      out.push(card);
      // where they came from: one sitting reads "from Section · Sep 21"
      UI.api('/review/redo?lens=new&sort=recent&limit=100', { quiet: true }).then(r => {
        if (my !== notesToken) return;
        const ss_ = new Map();
        (r.items || []).forEach(x => { if (x.session && !ss_.has(x.session)) ss_.set(x.session, x); });
        if (ss_.size === 1) { const x = [...ss_.values()][0]; txt.firstChild.textContent = `${plural(c.new, 'new miss', 'new misses')} from ${srcWord(x.source)} · ${day(x.last)}`; }
        else if (ss_.size > 1) txt.firstChild.textContent = `${plural(c.new, 'new miss', 'new misses')} from ${ss_.size} sittings`;
      }).catch(() => {});
    }
    if (c.worksheets_waiting > 0) {
      const line = h('p', { class: 'rh-line' }, h('span', { class: 'dot', 'aria-hidden': 'true' }), h('span', { text: `${plural(c.worksheets_waiting, 'worksheet')} waiting for answers` }));
      const a = h('a', { class: 'btn sm', href: '/practice/', text: 'Enter answers' });
      line.append(a);
      out.push(line);
      UI.api('/drill', { quiet: true }).then(r => {
        const w = (r.active || []).find(x => (x.source || (x.cfg && x.cfg.source)) === 'worksheet');
        if (w && w.id) a.href = `/review/sheet/?id=${encodeURIComponent(w.id)}`;
      }).catch(() => {});
    }
    box.replaceChildren(...out);
  }
  async function walk(body, btn) {
    if (btn) btn.setAttribute('aria-busy', 'true');
    try {
      const d = await UI.api('/review/walk', { method: 'POST', body });
      location.href = `/review/walk/?id=${encodeURIComponent(d.id)}`;
    } catch (e) { if (btn) btn.removeAttribute('aria-busy'); toast(reasonOf(e)); }
  }

  /* ------------------------------------------------------------ the tiles are the tabs */
  function tileData(id) {
    const c = S.counts || {};
    const d = S.due;
    const bits = a => a.filter(Boolean).join(' · ');
    if (id === 'due') {
      if (!d) return { v: null, sub: '' };
      if (d.left > 0) return { v: d.left, sub: d.left_minutes ? `about ${d.left_minutes} min` : '' };
      if (d.total > 0) return { v: '✓', sub: 'Done for today', short: '✓' };
      return { v: '', sub: 'Nothing due' };
    }
    if (!S.counts) return { v: null, sub: '' };
    if (id === 'redo') {
      const delta = c.open_week_delta && Math.abs(c.open_week_delta) !== c.open ? `${c.open_week_delta < 0 ? '▼' : '▲'}${fmtN(Math.abs(c.open_week_delta))} this week` : '';
      return { v: c.open || '', sub: bits([c.half && `${fmtN(c.half)} half fixed`, c.relapsed && `${fmtN(c.relapsed)} relapsed`, c.stake_total && `≈ ${fmtN(c.stake_total)} pts at stake`, delta]),
        spark: S.ledger && S.ledger.weeks && S.ledger.weeks.some(w => w.open_end) ? S.ledger.weeks.map(w => w.open_end) : null };
    }
    if (id === 'marked') return { v: c.marked || '', sub: bits([c.marked_right && `${fmtN(c.marked_right)} right`]) };
    if (id === 'saved') return { v: c.saved || '', sub: bits([c.noted && `${fmtN(c.noted)} with notes`, c.saved_unanswered && `${fmtN(c.saved_unanswered)} not answered`]) };
    if (id === 'history') return { v: c.answers || '', sub: '' };
    if (id === 'fixed') return { v: c.fixed || '', sub: bits([c.held && `${fmtN(c.held)} held a check-in`]) };
    return { v: '', sub: '' };
  }
  function paintTabs() {
    const host = $('rhtabs');
    if (!host.children.length) {
      TABS.forEach(t => {
        const b = h('button', { type: 'button', role: 'tab', class: 'rh-tab', id: `tab-${t.id}`, 'aria-controls': 'panel', 'aria-selected': 'false', tabindex: '-1', 'data-tab': t.id },
          h('span', { class: 'stat-k', text: t.k }), h('span', { class: 'rh-tl', text: t.short }), h('span', { class: 'stat-v' }), h('span', { class: 'stat-sub' }));
        b.addEventListener('click', () => openTab(t.id, { push: true }));
        host.append(b);
      });
      host.addEventListener('keydown', e => {
        const btns = [...host.children];
        const i = btns.indexOf(doc.activeElement);
        if (i < 0) return;
        const j = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: btns.length - 1 }[e.key];
        if (j === undefined) return;
        e.preventDefault();
        const b = btns[(j + btns.length) % btns.length];
        b.focus();
        openTab(b.dataset.tab, { push: true });
      });
    }
    TABS.forEach(t => {
      const b = $(`tab-${t.id}`);
      const x = tileData(t.id);
      const v = b.querySelector('.stat-v'), sub = b.querySelector('.stat-sub');
      v.textContent = x.v === null ? '—' : typeof x.v === 'number' ? fmtN(x.v) : x.v;
      sub.textContent = x.sub || '';
      sub.hidden = !x.sub;
      const old = b.querySelector('.stat-spark');
      if (old) old.remove();
      if (x.spark && UI.spark) { const sp = UI.spark(null, x.spark, { label: 'Open mistakes, 12 weeks', h: 18 }); if (sp) { (sp.el || sp).classList.add('stat-spark'); b.append(sp.el || sp); } }
      const on = t.id === S.tab;
      b.setAttribute('aria-selected', String(on));
      b.tabIndex = on ? 0 : -1;
      b.setAttribute('aria-label', `${t.k}${x.v !== '' && x.v !== null ? `, ${x.v === '✓' ? 'done' : x.v}` : ''}${x.sub ? `, ${x.sub}` : ''}`);
    });
    const cur = S.tab && tileData(S.tab);
    $('tabsub').textContent = cur ? cur.sub : '';
  }

  /* ------------------------------------------------------------ tabs */
  function openTab(id, o = {}) {
    const was = S.tab;
    if (was && was !== id) { S.filters[was] = currentFilterValues(); }
    S.tab = id;
    const u = new URL(location.href);
    const keep = new URLSearchParams();
    keep.set('tab', id);
    if (was === id || !was) { for (const [k, v] of u.searchParams) if (k !== 'tab') keep.set(k, v); }
    else {
      const saved = S.filters[id] || {};
      for (const [k, v] of Object.entries(saved)) if (v !== '' && v !== null && !(Array.isArray(v) && !v.length)) keep.set(k, Array.isArray(v) ? v.join(',') : v);
    }
    u.search = keep.toString();
    if (o.push && was !== id) history.pushState({ tab: id }, '', u); else history.replaceState(history.state, '', u);
    if (was !== id) dropPlayer();
    $('panel').setAttribute('aria-labelledby', `tab-${id}`);
    paintTabs();
    paintHead();
    paintFilters();
    if (id === 'due') { paintList(); syncPane(); paintBar(); paintListHead(); }
    else loadList(id);
    if (!S.ledger) UI.api('/review/ledger?weeks=12', { quiet: true }).then(l => { S.ledger = l; paintTabs(); if (S.tab === 'fixed') paintHead(); }).catch(() => {});
  }

  /* ------------------------------------------------------------ filters (UI.filterBar, URL state) */
  let FB = null;
  function topicGroups() {
    return (UI.DOMAINS || []).map(([d, ds]) => ({ label: ds, options: (UI.TOPICS || []).filter(t => t.domain === d).map(t => ({ value: t.slug, label: t.short })) }))
      .filter(g => g.options.length);
  }
  const DATE = { key: 'date', label: 'Date', type: 'date' };
  function filterDefs(tab) {
    const common = [
      { key: 'topics', label: 'Topic', type: 'multi', groups: topicGroups() },
      { key: 'difficulty', label: 'Difficulty', type: 'multi', options: [{ value: 'easy', label: 'Easy' }, { value: 'medium', label: 'Medium' }, { value: 'hard', label: 'Hard' }] },
      { key: 'fmt', label: 'Format', type: 'select', all: 'Any format', options: [{ value: 'mcq', label: 'Multiple choice' }, { value: 'spr', label: 'Grid-in' }] },
    ];
    const c = S.counts || {};
    const search = { key: 'q', label: 'Search', type: 'search', placeholder: tab === 'redo' ? 'Search mistakes' : 'Search questions' };
    const source = { key: 'source', label: 'Source', type: 'select', all: 'Any source', options: ['practice', 'due', 'section', 'module', 'diagnostic', 'challenge', 'qotd', 'review', 'shared', 'worksheet'].map(v => ({ value: v, label: srcWord(v) })) };
    const conf = { key: 'conf', label: 'Confidence', type: 'select', all: 'Any', options: [{ value: 'sure', label: 'Sure' }, { value: 'unsure', label: 'Unsure' }, { value: 'guess', label: 'Guess' }, { value: 'untagged', label: 'Untagged' }] };
    if (tab === 'redo') {
      const pts = c.stake_total !== null && c.stake_total !== undefined;
      return [
        ...common,
        { key: 'kind', label: 'Kind', type: 'select', all: 'Any kind', options: [{ value: 'misconception', label: 'Misconception' }, { value: 'gridin', label: 'Grid-in' }, { value: 'slip', label: 'Slip' }, { value: 'unsure', label: 'Unsure' }] },
        { key: 'status', label: 'Status', type: 'select', all: 'Any status', options: [{ value: 'new', label: 'New', n: c.new || null }, { value: 'blind', label: 'Blind spots · sure and wrong', n: c.blind || null },
          { value: 'open', label: 'Open' }, { value: 'half', label: 'Half fixed', n: c.half || null }, { value: 'relapsed', label: 'Relapsed', n: c.relapsed || null }, { value: 'stuck', label: 'Stuck', n: c.stuck || null }] },
        { key: 'cause', label: 'Cause', type: 'select', all: 'Any cause', options: CAUSES.map(([v, l]) => ({ value: v, label: l })) },
        conf,
        { key: 'sort', label: 'Sort', type: 'sort', options: [...(pts ? [{ value: 'worth', label: 'Most points' }] : []), { value: 'recent', label: 'Most recent' }, { value: 'blind', label: 'Blind spots first' },
          { value: 'hits', label: 'Most missed' }, { value: 'near', label: 'Closest to fixed' }, { value: 'oldest', label: 'Oldest' }, { value: 'topic', label: 'Topic order' }] },
        { key: 'group', label: 'Group by', type: 'sort', options: [{ value: 'topic', label: 'Topic' }, { value: 'domain', label: 'Domain' }, { value: 'habit', label: 'Habit' }, { value: 'norm', label: 'Mistake type' }, { value: 'none', label: 'None' }] },
        search,
      ];
    }
    if (tab === 'marked') return [...common, source, DATE, search];
    if (tab === 'saved') return [...common, source, DATE, search];
    if (tab === 'history') return [...common, source,
      { key: 'result', label: 'Result', type: 'select', all: 'Any result', options: [['right', 'Right'], ['wrong', 'Wrong'], ['repaired', 'Repaired'], ['mixed', 'Mixed'], ['repeat', 'Repeat'], ['slow', 'Slow right'], ['rushed', 'Rushed'], ['changed', 'Changed'], ['discarded', 'Discarded']].map(([v, l]) => ({ value: v, label: l })) },
      conf, DATE,
      { key: 'group', label: 'Group by', type: 'sort', options: [{ value: 'day', label: 'Day' }, { value: 'sitting', label: 'Sitting' }, { value: 'none', label: 'None' }] },
      search];
    if (tab === 'fixed') return [...common,
      { key: 'status', label: 'Status', type: 'select', all: 'Any', options: [{ value: 'unchecked', label: 'Not checked yet' }, { value: 'due', label: 'Check due' }, { value: 'held', label: 'Held' }, { value: 'dismissed', label: 'Dismissed' }] },
      { key: 'sort', label: 'Sort', type: 'sort', options: [{ value: 'recent', label: 'Recently fixed' }, { value: 'unchecked', label: 'Not checked yet first' }, { value: 'long', label: 'Longest to fix' }, { value: 'relapses', label: 'Most relapses' }, { value: 'due', label: 'Check due first' }] },
      DATE, search];
    return [];
  }
  const CAUSES = [['trap', 'Trap'], ['slip', 'Slip'], ['misread', 'Misread'], ['clock', 'Clock'], ['entry', 'Entry'], ['gap', 'Gap']];
  function paintFilters() {
    const host = $('filters');
    host.replaceChildren();
    FB = null;
    const defs = filterDefs(S.tab);
    const c = S.counts || {};
    const whole = { redo: c.open, marked: c.marked, saved: c.saved, history: c.answers, fixed: (c.fixed || 0) + (c.dismissed || 0) }[S.tab];
    const urlSet = defs.some(f => f.type !== 'sort' && Q().get(f.key));
    if (!defs.length || (S.counts && !whole && !urlSet)) return;
    FB = UI.filterBar(host, defs, { url: true, label: 'Filter this list', onChange: () => { if (S.tab !== 'due') loadList(S.tab); } });
  }
  function currentFilterValues() { return FB ? FB.values() : {}; }
  function activeFilters() {
    const v = currentFilterValues();
    return Object.entries(v).filter(([k, x]) => !['sort', 'group'].includes(k) && (Array.isArray(x) ? x.length : x !== '' && x !== null && x !== undefined)).length;
  }
  function dateParams(v) {
    if (!v) return {};
    const iso = d => d.toISOString().slice(0, 10);
    const now = new Date();
    const back = n => { const d = new Date(now); d.setDate(d.getDate() - n); return iso(d); };
    if (v === 'today') return { since: back(0) };
    if (/^\d+$/.test(v)) return { since: back(+v - 1) };
    if (String(v).includes('..')) { const [a, z] = v.split('..'); return Object.assign({}, a ? { since: a } : {}, z ? { until: `${z}T23:59:59` } : {}); }
    return {};
  }
  function listPath(tab, cursor) {
    const v = currentFilterValues();
    const p = new URLSearchParams();
    const put = (k, x) => { if (Array.isArray(x) ? x.length : x !== '' && x !== null && x !== undefined) p.set(k, Array.isArray(x) ? x.join(',') : x); };
    ['topics', 'difficulty', 'fmt', 'q', 'kind', 'cause', 'conf', 'lens', 'source', 'result'].forEach(k => put(k, v[k]));
    if (tab === 'redo') {
      if (v.status === 'blind') p.set('lens', 'blind'); else put('status', v.status);
      const c = S.counts || {};
      put('sort', v.sort || (c.stake_total !== null && c.stake_total !== undefined ? 'worth' : 'recent'));
      put('group', v.group && v.group !== 'none' ? v.group : 'topic');
    }
    if (tab === 'history') { const g = v.group || 'day'; if (g === 'sitting') p.set('group', 'sitting'); }
    Object.entries(dateParams(v.date)).forEach(([k, x]) => p.set(k, x));
    p.set('limit', tab === 'fixed' || tab === 'saved' ? '100' : '50');
    if (cursor !== null && cursor !== undefined) p.set('cursor', cursor);
    return `/review/${tab}?${p}`;
  }

  /* ------------------------------------------------------------ loading a list */
  async function loadList(tab, o = {}) {
    const L = S.lists[tab] || (S.lists[tab] = { items: [], total: 0, next: null, data: null });
    const my = ++S.token;
    if (!o.more && !o.quiet) { paintSkeleton(); }
    try {
      const d = await UI.api(listPath(tab, o.more ? L.next : null));
      if (my !== S.token || S.tab !== tab) return;
      L.items = o.more ? L.items.concat(d.items || []) : (d.items || []);
      L.total = d.total ?? L.items.length;
      L.next = d.next ?? null;
      if (!o.more) L.data = d; else if (d.sittings) L.data.sittings = (L.data.sittings || []).concat(d.sittings.filter(s => !(L.data.sittings || []).some(x => x.session === s.session)));
      if (tab === 'fixed') clientFixed(L);
      if (tab === 'saved') clientSaved(L);
      L.err = false;
    } catch (e) {
      if (my !== S.token || S.tab !== tab) return;
      L.err = true;
      if (!L.data) { const box = $('list'); box.replaceChildren(); box.removeAttribute('aria-busy'); UI.cardError(box, () => loadList(tab), 'This list didn’t load.'); return; }
      toast('Couldn’t refresh the list.');
    }
    paintListHead(); paintList(); syncPane(); paintBar();
    if (tab === 'redo' || tab === 'history' || tab === 'marked' || tab === 'saved' || tab === 'fixed') paintHeadFromList(tab);
  }
  // Fixed's status and sort are not on the server yet: they order and filter the rows loaded (up to 100)
  function fixedState(r) {
    if (r.closed_how === 'dismissed') return 'dismissed';
    if ((r.held || r.checks || 0) > 0) return (r.due && r.due <= new Date().toISOString().slice(0, 10)) ? 'due' : 'held';
    if (r.due && r.due <= new Date().toISOString().slice(0, 10)) return 'due';
    return 'unchecked';
  }
  function clientFixed(L) {
    const v = currentFilterValues();
    let rows = L.items;
    if (v.status) rows = rows.filter(r => fixedState(r) === v.status || (v.status === 'held' && fixedState(r) === 'due' && (r.checks || 0) > 0));
    const ord = { recent: r => -(Date.parse(r.closed) || 0), unchecked: r => (fixedState(r) === 'unchecked' ? 0 : 1), long: r => -(r.days_to_fix || 0),
      relapses: r => -(r.relapses || 0), due: r => (fixedState(r) === 'due' ? 0 : 1) }[v.sort || 'recent'];
    if (ord) rows = rows.map((r, i) => [ord(r), i, r]).sort((a, b) => a[0] - b[0] || a[1] - b[1]).map(x => x[2]);
    if (v.status) L.total = rows.length;
    L.items = rows;
  }
  function clientSaved(L) {
    L.all = L.items;
    const f = S.savedCard;
    if (f === 'due') L.items = L.all.filter(r => r.due);
    else if (f === 'learned') L.items = L.all.filter(r => r.learned);
    if (f !== 'all') L.total = L.items.length;
    // Due first while the deck is spaced (V3)
    if (S.prefs.saved_spaced !== false) L.items = L.items.map((r, i) => [r.due ? 0 : 1, i, r]).sort((a, b) => a[0] - b[0] || a[1] - b[1]).map(x => x[2]);
  }

  function paintSkeleton() {
    const box = $('list');
    box.setAttribute('aria-busy', 'true');
    box.replaceChildren();
    const sk = h('div', { class: 'rh-skel' });
    if (UI.skel) UI.skel(sk, 'rows:6'); else sk.textContent = 'Loading…';
    box.append(sk);
  }

  /* ------------------------------------------------------------ the list head: select all, counts, secondary actions */
  function paintListHead() {
    const host = $('listhead');
    host.replaceChildren();
    const tab = S.tab;
    if (!tab) return;
    const L = tab === 'due' ? null : S.lists[tab];
    if (tab === 'due' || !L || !L.data) { host.hidden = true; return; }
    host.hidden = false;
    if (!L.total) { host.hidden = true; return; }
    const n = selCount(tab);
    const all = h('input', { type: 'checkbox', 'aria-label': 'Select every row' });
    all.checked = n > 0 && n >= L.total;
    all.indeterminate = n > 0 && n < L.total;
    all.addEventListener('change', () => {
      const s = sel(tab);
      s.all = all.checked; s.ids.clear(); saveSel(tab);
      paintList(); paintListHead(); paintBar();
    });
    const lab = h('label', { class: 'check' }, all, h('span', { text: n ? `${fmtN(n)} of ${fmtN(L.total)} selected` : `Select all ${fmtN(L.total)}` }));
    host.append(lab);
    const c = S.counts || {};
    const whole = { redo: c.open, marked: c.marked, saved: c.saved, history: c.answers, fixed: c.fixed }[tab];
    if (activeFilters() && whole && L.total !== whole) host.append(h('span', { class: 'meta', text: `${fmtN(L.total)} of ${fmtN(whole)} match` }));
    const acts = secondaryActions(tab);
    if (acts.length) host.append(h('div', { class: 'rh-acts', role: 'group', 'aria-label': 'More with these' }, ...acts));
  }

  /* ------------------------------------------------------------ the list */
  function paintList() {
    const box = $('list');
    box.removeAttribute('aria-busy');
    const tab = S.tab;
    box.replaceChildren();
    $('body').classList.toggle('no-pane', false);
    if (tab === 'due') return paintDueList(box);
    const L = S.lists[tab];
    if (!L || !L.data) return paintSkeleton();
    if (!L.items.length) return paintEmpty(box, tab);
    if (tab === 'redo') paintRedo(box, L);
    else if (tab === 'marked') paintMarked(box, L);
    else if (tab === 'saved') paintSaved(box, L);
    else if (tab === 'history') paintHistory(box, L);
    else if (tab === 'fixed') paintFixed(box, L);
    box.querySelectorAll('.rh-rb').forEach(flatten);
    if (L.next !== null && L.next !== undefined) {
      const more = h('button', { type: 'button', class: 'btn rh-more', text: `Load 50 more · ${fmtN(L.items.length)} of ${fmtN(L.total)}` });
      more.addEventListener('click', () => { more.setAttribute('aria-busy', 'true'); loadList(tab, { more: true }); });
      box.append(more);
    }
    markCurrent();
  }
  // a row reads: lead · label · tags on the first line, then its meta across the full width under them
  function flatten(btn) {
    if (btn.dataset.flat) return;
    btn.dataset.flat = '';
    const main = [...btn.children].find((k, i) => i > 0 && k.tagName === 'DIV');
    if (!main) return;
    const [first, ...rest] = [...main.children];
    if (!first) return;
    main.replaceWith(first);
    if (rest.length) btn.append(h('div', { class: 'sub' }, ...rest));
  }
  function paintEmpty(box, tab) {
    const c = S.counts || {};
    $('body').classList.add('no-pane');
    if (activeFilters()) {
      const b = h('button', { type: 'button', class: 'btn', text: 'Clear filters' });
      b.addEventListener('click', () => FB && FB.clear());
      box.append(h('div', { class: 'rh-empty' }, h('p', { class: 'empty-text', text: 'Nothing matches these filters.' }), b));
      return;
    }
    const text = {
      redo: c.answers ? 'Nothing open. Every wrong answer lands here, named by the mistake behind it.' : 'Every wrong answer lands here, named by the mistake behind it.',
      marked: 'Flag a question in practice or a test and it waits here.',
      saved: 'Tap the bookmark on any question to keep it.',
      history: 'Every answer you give shows up here.',
      fixed: 'Fixed mistakes move here, and each comes back for a check-in.',
    }[tab];
    const host = h('div', { class: 'rh-empty' });
    box.append(host);
    const sample = tab === 'redo' && !c.answers ? exampleRow : null;
    const nothingOpen = tab === 'redo' && c.answers > 0;
    UI.empty(host, {
      sample: sample ? sample() : null, text,
      action: nothingOpen ? { label: `Keep going · ${S.minutes || 10} min`, body: { source: 'next', box: S.minutes || 10 } } : (!c.answers ? UI.empty.START : null),
      answered: c.answers || 0,
    });
    if (sample) fillExample(host);
  }
  // V16: a sample row built from a real reserved item, tagged Example
  let exampleCache = null;
  function exampleRow() {
    const r = h('div', { class: 'rh-row' }, h('span', { class: 'lead', style: 'display:grid;place-items:center' }, UI.pips ? UI.pips(2, 2) : null),
      h('div', { class: 'rh-rb' }, h('span'), h('div', {}, h('div', { class: 'l1', text: 'Used the diameter where the radius was needed' }), h('div', { class: 'l2' }, h('span', { text: 'Circles' }), h('span', { text: 'Arc length' }), tierBit('medium'), h('span', { text: 'picked C' })))));
    r.dataset.example = '';
    return r;
  }
  async function fillExample(host) {
    try {
      if (!exampleCache) exampleCache = await UI.api('/types/rr.partner/example', { quiet: true });
      const q = exampleCache.question || {};
      const i = (q.reasons || []).findIndex((x, j) => x && j !== q.answer_index);
      const row = host.querySelector('[data-example] .l1');
      if (row && i >= 0) { row.textContent = cap(q.reasons[i]); const l2 = host.querySelector('[data-example] .l2'); l2.replaceChildren(...[h('span', { text: (TOPIC(q.topic) || {}).short || q.topic_name || '' }), h('span', { text: cap(q.skill || '') }), tierBit(q.difficulty), h('span', { text: `picked ${LET[i]}` })].filter(Boolean)); }
    } catch (_) {}
  }

  function rowShell(tab, r, i, o = {}) {
    const key = keyOf(tab, r);
    const row = h('div', { class: 'rh-row' + (o.cls ? ' ' + o.cls : '') + (o.select === false ? ' nosel' : ''), role: 'listitem', 'data-i': String(i), 'data-key': key });
    if (o.select !== false) {
      const cb = h('input', { type: 'checkbox', 'aria-label': `Select: ${o.label || ''}` });
      cb.checked = isSel(tab, key);
      cb.addEventListener('change', () => { setSel(tab, key, cb.checked); paintListHead(); paintBar(); });
      row.append(h('label', { class: 'sel' }, cb));
    } else row.append(h('span', { class: 'sel' }));
    const btn = h('button', { type: 'button', class: 'rh-rb' });
    btn.addEventListener('click', () => openRow(i));
    row.append(btn);
    attachLongPress(row, tab, key);
    return { row, btn };
  }
  // V14: a 500 ms press on a phone selects the row and shows the bar
  function attachLongPress(row, tab, key) {
    let t = 0, fired = false;
    row.addEventListener('pointerdown', e => {
      if (e.pointerType !== 'touch') return;
      fired = false;
      t = setTimeout(() => { fired = true; setSel(tab, key, true); const cb = row.querySelector('.sel input'); if (cb) cb.checked = true; paintListHead(); paintBar(); if (navigator.vibrate) try { navigator.vibrate(10); } catch (_) {} }, 500);
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(ev => row.addEventListener(ev, () => clearTimeout(t)));
    row.addEventListener('click', e => { if (fired) { e.preventDefault(); e.stopPropagation(); fired = false; } }, true);
  }
  function tagsEl(list) {
    const t = h('span', { class: 'tags' });
    list.filter(Boolean).forEach(([text, cls]) => t.append(h('span', { class: 'tag' + (cls ? ' ' + cls : ''), text })));
    return t.children.length ? t : h('span');
  }
  const l2 = bits => { const el = h('div', { class: 'l2' }); bits.filter(Boolean).forEach(b => el.append(b instanceof Node ? (b.tagName === 'SPAN' ? b : h('span', {}, b)) : h('span', { text: b }))); return el; };

  /* Due (V1) */
  const KIND = {
    check: { text: 'Check-in ✓' }, relapsed: { text: 'Relapsed', cls: 'ink' }, sure: { text: 'Sure ✕', cls: 'ink' }, half: { text: 'Half fixed ●○', cls: 'amber' },
    saved: { text: 'Saved' }, fading: { text: 'Fading' }, marked: { text: 'Marked' }, mistake: { text: 'Mistake' }, keep_warm: { text: 'Keep warm' },
  };
  function paintDueList(box) {
    const d = S.due;
    if (S.dueErr && !d) { UI.cardError(box, () => loadDue().then(afterDue), 'Today’s review didn’t load.'); return; }
    if (!d) return paintSkeleton();
    const items = d.items || [];
    if (!items.length) {
      $('body').classList.add('no-pane');
      const c = S.counts || {};
      if (!c.answers) return paintEmpty(box, 'redo');
      return;
    }
    const ol = h('div', { class: 'rh-list' });
    items.forEach((it, i) => {
      const { row, btn } = rowShell('due', it, i, { select: false, label: it.label, cls: 'has-x' });
      if (it.done) row.dataset.done = '';
      if (it.snoozed) row.dataset.snoozed = '';
      const lead = h('span', { class: 'lead', 'aria-hidden': 'true' }, it.done ? h('span', { text: '✓', style: 'font: 700 16px var(--font)' }) : it.owed ? UI.pips(it.owed, 2) : null);
      const k = KIND[it.kind] || { text: cap(it.kind) };
      const main = h('div', {}, mtext(h('div', { class: 'l1' }), it.label || ''),
        l2([it.domain && dshort(it.domain), it.skill && it.skill !== it.label ? it.skill : null, tierBit(it.tier), it.pts ? h('span', { class: 'pts', text: `≈ ${fmtN(it.pts)} pts` }) : null]),
        it.why ? h('div', { class: 'l3 why', text: it.why }) : null);
      btn.append(lead, main, tagsEl([[k.text, k.cls], it.done ? ['Done', 'soft'] : null]));
      btn.setAttribute('aria-label', `${k.text}: ${it.label}${it.done ? ', done' : ''}${it.snoozed ? ', not today' : ''}`);
      const x = h('button', { type: 'button', class: 'x', 'aria-label': it.snoozed ? `Undo not today: ${it.label}` : `Not today: ${it.label}`, title: it.snoozed ? 'Undo' : 'Not today' }, it.snoozed ? 'Undo' : '×');
      if (it.snoozed) { x.style.width = 'auto'; x.style.padding = '0 10px'; x.style.font = '600 12.5px var(--font)'; main.append(h('div', { class: 'l3', text: 'Not today' })); }
      x.addEventListener('click', () => snooze(it, !!it.snoozed, x));
      if (!it.done) row.append(x);
      ol.append(row);
    });
    box.append(ol);
    box.querySelectorAll('.rh-rb').forEach(flatten);
    markCurrent();
  }
  async function snooze(it, undo, btn) {
    btn.setAttribute('aria-busy', 'true');
    try {
      await UI.api('/review/snooze', { method: 'POST', body: undo ? { key: it.key, undo: true } : { key: it.key } });
      await Promise.all([loadDue(), loadCounts()]);
      afterDue();
      if (!undo) toast('Not today', { undo: () => snooze(it, true, h('button')) });
      if (UI.refresh) UI.refresh();
    } catch (e) { btn.removeAttribute('aria-busy'); toast(reasonOf(e)); }
  }

  /* Redo (V2, V4-V7, V11) */
  const STATUS = { open: 'Open', half: 'Half fixed', relapsed: 'Relapsed', stuck: 'Stuck' };
  function groupKey(r, g) {
    if (g === 'topic') return r.topic;
    if (g === 'domain') return r.domain;
    if (g === 'habit') return (r.habit && r.habit.id) || 'other';
    return r.norm;
  }
  function paintRedo(box, L) {
    const g = currentFilterValues().group || 'topic';
    const groups = g === 'none' ? null : (L.data.groups || []);
    const rows = L.items.map((r, i) => [r, i]);
    if (!groups) { const ol = h('div', { class: 'rh-list' }); rows.forEach(([r, i]) => ol.append(redoRow(r, i, g))); box.append(ol); return; }
    const order = [];
    const by = new Map();
    rows.forEach(([r, i]) => { const k = groupKey(r, g); if (!by.has(k)) { by.set(k, []); order.push(k); } by.get(k).push([r, i]); });
    // groups in the server's order when it gave one, else first appearance
    const known = groups.map(x => x.key).filter(k => by.has(k));
    const keys = [...known, ...order.filter(k => !known.includes(k))];
    keys.forEach(k => {
      const meta = groups.find(x => x.key === k) || { key: k, name: k, count: by.get(k).length, questions: 0 };
      const sec = h('section', { class: 'rh-group', 'aria-label': meta.name });
      const members = by.get(k);
      const cb = h('input', { type: 'checkbox', 'aria-label': `Select every mistake in ${meta.name}` });
      const on = members.filter(([r]) => isSel('redo', keyOf('redo', r))).length;
      cb.checked = on === members.length; cb.indeterminate = on > 0 && on < members.length;
      cb.addEventListener('change', () => { members.forEach(([r]) => setSel('redo', keyOf('redo', r), cb.checked)); paintList(); paintListHead(); paintBar(); });
      const head = h('div', { class: 'rh-gh' }, h('label', { class: 'sel', style: 'display:grid;place-items:center;width:44px;height:44px;margin-left:0' }, cb));
      head.append(g === 'topic' && UI.glyph ? UI.glyph(k) : h('span'));
      const gt = h('div', { class: 'gt' }, h('span', { class: 't', text: meta.name }));
      head.append(gt);
      const bits = [plural(meta.count, 'open', 'open'), meta.pts ? `≈ ${fmtN(meta.pts)} pts` : null,
        g === 'topic' && meta.per_test ? `about ${fmtN(Math.round(meta.per_test * 10) / 10)} of 44 a test` : null];
      if (g === 'topic' || g === 'habit' || g === 'norm') { if (meta.domain && g !== 'domain') bits.unshift(dshort(meta.domain)); }
      gt.append(h('span', { class: 'meta', text: bits.filter(Boolean).join(' · ') }));
      const act = h('span', { class: 'act' });
      if (g === 'habit' && k !== 'other') {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Drill this habit · 8' });
        b.addEventListener('click', () => start({ source: 'habit', habit: k, count: 8 }, b));
        act.append(b);
      } else {
        const ids = members.map(([r]) => r.id);
        const qn = members.reduce((s, [r]) => s + (r.owed || 0), 0);
        const b = h('button', { type: 'button', class: 'quiet', text: `Fix · ${plural(qn, 'question')}` });
        b.addEventListener('click', () => start(redoBody({ ids }), b));
        act.append(b);
      }
      const fold = h('button', { type: 'button', class: 'quiet fold', 'aria-label': `Fold ${meta.name}`, 'aria-expanded': 'true' }, h('span', { 'aria-hidden': 'true', text: '▾' }));
      fold.addEventListener('click', () => { const f = sec.toggleAttribute('data-folded'); fold.setAttribute('aria-expanded', String(!f)); });
      act.append(fold);
      head.append(act);
      if (meta.tell) head.append(h('span', { class: 'tell', text: meta.tell }));
      sec.append(head);
      members.forEach(([r, i]) => sec.append(redoRow(r, i, g)));
      box.append(sec);
    });
  }
  function redoRow(r, i, g) {
    const { row, btn } = rowShell('redo', r, i, { label: r.label });
    const of = (r.clean || 0) + (r.owed || 0) || (r.kind === 'unsure' ? 1 : 2);
    const pips = UI.pips ? UI.pips(r.owed, of) : null;
    if (pips) { pips.setAttribute('aria-label', `${of - r.owed} of ${of} clean answers`); pips.title = `${of - r.owed} of ${of} clean answers`; }
    const status = r.stuck ? 'stuck' : r.status;
    const tags = [
      r.new ? ['New', 'new'] : null,
      r.blind ? [r.blind_assumed ? 'Sure ✕ (assumed)' : 'Sure ✕', 'ink'] : null,
      status === 'stuck' ? ['Stuck', 'ink'] : status === 'relapsed' ? [`Relapsed${r.relapses > 1 ? ' ×' + r.relapses : ''}`, 'ink'] : status === 'half' ? ['Half fixed', 'amber'] : null,
      r.kind === 'gridin' ? ['Grid-in'] : r.kind === 'slip' ? ['Slip'] : r.kind === 'unsure' ? ['Unsure'] : null,
      r.kind === 'misconception' && r.cause && r.cause !== 'trap' && CAUSES.find(c => c[0] === r.cause) ? [CAUSES.find(c => c[0] === r.cause)[1], 'soft'] : null,
      r.source === 'outside' ? ['Logged by you'] : null,
      r.elsewhere && r.elsewhere.length ? [`+${r.elsewhere.length} elsewhere`, 'soft'] : null,
    ];
    const bits = [
      g !== 'topic' && g !== 'domain' && r.domain ? dshort(r.domain) : null,
      r.skill && r.skill !== r.label ? r.skill : null,
      tierBit(r.difficulty),
      r.fmt ? (r.fmt === 'spr' ? 'Grid-in' : 'MC') : null,
      r.hits > 1 ? `missed ${r.hits}×` : null,
      r.last ? `last ${day(r.last)}` : null,
      r.source && r.source !== 'outside' ? srcWord(r.source) : null,
      r.given_label ? `picked ${r.given_label}` : null,
      r.dodged_elsewhere ? `dodged in ${plural(r.dodged_elsewhere, 'other type')}` : null,
      r.pts ? h('span', { class: 'pts', text: `≈ ${fmtN(r.pts)} pts` }) : null,
    ];
    btn.append(h('span', { class: 'lead' }, pips), h('div', {}, mtext(h('div', { class: 'l1' }), r.label || ''), l2(bits), r.note ? h('div', { class: 'l3 note', text: r.note }) : null), tagsEl(tags));
    if (r.stuck) {
      const lb = UI.verb ? UI.verb('learn', { sm: true }) : h('button', { type: 'button', class: 'btn sm', text: 'Learn this type' });
      lb.addEventListener('click', () => start({ source: 'learn', templates: [r.template], example: true, count: 3 }, lb));
      row.append(h('div', { class: 'ract' }, lb));
    }
    return row;
  }

  /* Marked (V5) */
  function resultOf(r) {
    if (!r.answered && r.answered !== undefined) return 'unanswered';
    if (r.result) return { right: 'correct', wrong: 'incorrect', repaired: 'repaired', repeat: 'repeat', mixed: 'mixed', slow: 'correct', rushed: 'incorrect', changed: r.correct ? 'correct' : 'incorrect', discarded: 'voided' }[r.result] || (r.correct ? 'correct' : 'incorrect');
    if (r.last_result) return r.last_result === 'right' ? 'correct' : r.last_result === 'wrong' ? 'incorrect' : r.last_result;
    return r.correct ? 'correct' : 'incorrect';
  }
  function pickText(r) {
    if (r.answered === false) return 'Not answered yet';
    if (!r.given_label && r.answer) return `Blank → ${r.answer}`;
    if (r.given_label && r.answer && !r.correct) return `${r.given_label} → ${r.answer}`;
    return r.given_label ? `picked ${r.given_label}` : null;
  }
  function paintMarked(box, L) {
    const by = new Map();
    L.items.forEach((r, i) => { const k = r.session || 'none'; if (!by.has(k)) by.set(k, []); by.get(k).push([r, i]); });
    for (const [sid, members] of by) {
      const r0 = members[0][0];
      const sec = h('section', { class: 'rh-group', 'aria-label': `${srcWord(r0.source)} · ${day(r0.session_at)}` });
      const vis = members.filter(([r]) => r.visits !== undefined && r.visits !== null && r.session_kind !== 'drill');
      const came = vis.length ? ` · ${vis.filter(([r]) => r.visits > 1).length} of ${vis.length} flags came back` : '';
      const head = h('div', { class: 'rh-gh plain' }, h('div', { class: 'gt' }, h('span', { class: 't', text: `${srcWord(r0.source)} · ${day(r0.session_at || r0.at)}` }),
        h('span', { class: 'meta', text: `${members.length} marked${came}` })));
      const href = sittingHref(r0.session_kind, sid);
      head.append(h('span', { class: 'act' }, href ? h('a', { class: 'quiet', href, text: r0.session_kind === 'drill' ? 'Summary' : 'Report' }) : null));
      sec.append(head);
      members.forEach(([r, i]) => {
        const { row, btn } = rowShell('marked', r, i, { label: r.stem });
        const st = resultOf(r);
        const bits = [r.skill, tierBit(r.difficulty), r.fmt === 'spr' ? 'Grid-in' : 'MC', r.ms ? `${mmss(r.ms)}${r.budget_ms ? ` · budget ${mmss(r.budget_ms)}` : ''}` : null, pickText(r)];
        const hist = r.session_kind && r.session_kind !== 'drill' && r.flagged_at_ms !== undefined ? [
          r.flagged_at_ms ? `flagged at ${mmss(r.flagged_at_ms)}` : null, r.visits > 1 ? `came back ${r.visits - 1}×` : null, r.changes ? `changed ${r.changes}×` : null] : [];
        btn.append(h('span', { class: 'lead' }, UI.cell ? UI.cell(st, r.n, { static: true, size: 'sm', flag: true }) : null),
          h('div', {}, mtext(h('div', { class: 'l1 stem' }), r.stem || ''), l2(bits), hist.some(Boolean) ? h('div', { class: 'l3', text: hist.filter(Boolean).join(' · ') }) : null),
          tagsEl([r.during === false ? ['flagged later', 'soft'] : null, r.visits === 1 && r.session_kind !== 'drill' ? ['Never came back', 'ink'] : null]));
        sec.append(row);
      });
      box.append(sec);
    }
  }
  function sittingHref(kind, sid) {
    if (!sid || sid === 'none') return null;
    if (kind === 'drill' || kind === 'challenge') return `/practice/session/?id=${encodeURIComponent(sid)}`;
    return `/results/report/?id=${encodeURIComponent(sid)}`;
  }

  /* Saved (V3) */
  function paintSaved(box, L) {
    const ol = h('div', { class: 'rh-list' });
    L.items.forEach((r, i) => {
      const { row, btn } = rowShell('saved', r, i, { label: r.stem, cls: 'tall' });
      const st = r.answered === false ? 'unanswered' : resultOf(r);
      const sched = S.prefs.saved_spaced === false ? null : r.learned ? 'Learned ✓' : r.due ? 'due today' : r.next ? `next ${day(r.next)}` : null;
      const bits = [(TOPIC(r.topic) || {}).short || r.name, r.skill, tierBit(r.difficulty), r.fmt === 'spr' ? 'Grid-in' : 'MC', r.saved_at || r.at ? `saved ${day(r.saved_at || r.at)}` : null,
        r.answered === false ? 'not answered' : r.given_label ? `answered: ${r.correct ? 'Right' : 'Wrong'} (picked ${r.given_label})` : null,
        r.tries > 1 ? `${r.tries} tries` : null, sched, S.prefs.saved_spaced !== false && !r.learned && r.box !== undefined ? `box ${(r.box || 0) + 1} of 4` : null];
      btn.append(h('span', { class: 'lead' }, UI.cell ? UI.cell(st, '', { static: true, size: 'sm', saved: true }) : null),
        h('div', {}, mtext(h('div', { class: 'l1 stem' }), r.stem || ''), l2(bits), r.note ? h('div', { class: 'l3 note', text: r.note }) : null),
        tagsEl([r.why === 'trick' ? ['Nice trick'] : r.why === 'hard' ? ['Hard'] : null, r.due && !r.learned ? ['Due', 'amber'] : null]));
      const noteB = h('button', { type: 'button', class: 'btn sm', text: r.note ? 'Edit note' : 'Note' });
      noteB.addEventListener('click', () => noteEditor(row, r, noteB));
      const unsave = h('button', { type: 'button', class: 'quiet', text: 'Unsave' });
      unsave.addEventListener('click', () => unsaveRows([r]));
      row.append(h('div', { class: 'ract' }, noteB, unsave));
      ol.append(row);
    });
    box.append(ol);
  }
  function noteEditor(row, r, opener) {
    if (row.querySelector('.rnote')) { row.querySelector('.rnote textarea').focus(); return; }
    const ta = h('textarea', { class: 'field', maxlength: '280', 'aria-label': 'Your note on this question', placeholder: 'The trick, in your own words' });
    ta.value = r.note || '';
    const wrap = h('div', { class: 'rnote' }, ta);
    if (UI.counter) wrap.append(UI.counter(ta, 280));
    let sent = r.note || '';
    const save = async () => {
      const v = ta.value.trim();
      if (v === sent) return;
      const was = r.note;
      r.note = v || null;
      try { await UI.api('/saved', { method: 'PATCH', body: { template: r.template, seed: r.seed, note: v } }); sent = v; toast('Note saved'); refreshSoon(false); }
      catch (e) { r.note = was; toast(reasonOf(e)); }
    };
    ta.addEventListener('blur', save);
    ta.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); save().then(() => { wrap.remove(); paintList(); }); } if (e.key === 'Escape') { wrap.remove(); opener.focus(); } });
    row.querySelector('.ract').before(wrap);
    ta.focus();
  }
  async function unsaveRows(rows) {
    const L = S.lists.saved;
    const keys = new Set(rows.map(r => keyOf('saved', r)));
    const before = L.items;
    L.items = L.items.filter(r => !keys.has(keyOf('saved', r)));
    L.total = Math.max(0, L.total - rows.length);
    paintList(); paintListHead(); paintBar(); syncPane();
    try {
      await Promise.all(rows.map(r => UI.api('/saved', { method: 'POST', body: { template: r.template, seed: r.seed, on: false } })));
      rows.forEach(r => S.cache.delete(`${r.template}:${r.seed}`));
      refreshSoon(false);
      toast(rows.length === 1 ? 'Removed from Saved' : `${rows.length} removed from Saved`, { undo: async () => {
        await Promise.all(rows.map(r => UI.api('/saved', { method: 'POST', body: { template: r.template, seed: r.seed, on: true, note: r.note || undefined } }).catch(() => {})));
        refreshSoon(true);
      } });
    } catch (e) { L.items = before; L.total += rows.length; paintList(); toast(reasonOf(e)); }
  }

  /* History (V8, V12, V13) */
  function paintHistory(box, L) {
    const g = currentFilterValues().group || 'day';
    const row = (r, i) => historyRow(r, i);
    if (g === 'none') { const ol = h('div', { class: 'rh-list' }); L.items.forEach((r, i) => ol.append(row(r, i))); box.append(ol); return; }
    if (g === 'day') {
      const days = new Map((L.data.days || []).map(d => [d.day, d]));
      const by = new Map();
      L.items.forEach((r, i) => { const k = localDay(r.at); if (!by.has(k)) by.set(k, []); by.get(k).push([r, i]); });
      for (const [k, members] of by) {
        const d = days.get(k);
        const head = h('h3', { class: 'rh-dayh' }, h('span', { text: UI.date(k, 'long') }),
          d ? h('span', { class: 'meta', text: `${d.right} / ${d.questions} right · ${UI.dur ? UI.dur(Math.round(d.minutes)) : Math.round(d.minutes) + ' min'}` }) : null);
        const sec = h('section', { class: 'rh-group' }, head);
        members.forEach(([r, i]) => sec.append(row(r, i)));
        box.append(sec);
      }
      return;
    }
    // Group by sitting: V13's header over each sitting's rows; retakes nest under the original
    const sits = (L.data.sittings || []);
    const by = new Map();
    L.items.forEach((r, i) => { const k = r.session || 'none'; if (!by.has(k)) by.set(k, []); by.get(k).push([r, i]); });
    const done = new Set();
    sits.forEach(s => {
      const members = by.get(s.session) || [];
      done.add(s.session);
      box.append(sittingCard(s, members.map(([r, i]) => row(r, i))));
    });
    for (const [k, members] of by) {
      if (done.has(k)) continue;
      const sec = h('section', { class: 'rh-group' }, h('h3', { class: 'rh-dayh', text: 'Other answers' }));
      members.forEach(([r, i]) => sec.append(row(r, i)));
      box.append(sec);
    }
  }
  const localDay = iso => { const d = new Date(iso); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
  function historyRow(r, i) {
    const { row, btn } = rowShell('history', r, i, { label: r.skill, cls: 'compact' });
    const st = resultOf(r);
    const over = r.ms && r.budget_ms && r.ms > r.budget_ms;
    const time = r.ms ? h('span', { class: over ? 'over' : null, text: `${mmss(r.ms)}${r.budget_ms ? ` · budget ${mmss(r.budget_ms)}${over ? ' ▲' : ''}` : ''}` }) : null;
    const t = TOPIC(r.topic);
    const bits = [r.domain ? dshort(r.domain) : null, tierBit(r.difficulty), srcWord(r.source),
      r.correct ? (r.given_label ? `picked ${r.given_label}` : null) : r.given_label || r.answer ? `${r.given_label || '–'} → ${r.answer || ''}`.replace(/ → $/, '') : null, time,
      r.conf ? `said ${cap(r.conf)}` : null];
    btn.append(h('span', { class: 'lead' }, UI.cell ? UI.cell(st, '', { static: true, size: 'sm', flag: r.flagged || null }) : null),
      h('div', {}, h('div', { class: 'l1' }, t && UI.glyph ? UI.glyph(r.topic) : null, ' ', r.skill || ''), l2(bits),
        !r.correct && r.mistake ? h('div', { class: 'l3', text: cap(r.mistake) }) : null),
      tagsEl([r.result === 'mixed' ? ['Mixed'] : null, r.result === 'slow' ? ['Slow right'] : null, r.result === 'rushed' ? ['Rushed', 'ink'] : null,
        r.repeat ? ['Repeat', 'soft'] : null, r.void ? ['Discarded', 'soft'] : null]));
    if (r.tries && r.tries.length > 1) {
      const tg = h('button', { type: 'button', class: 'quiet', 'aria-expanded': 'false', text: `▸ ${r.tries.length} tries` });
      const list = h('div', { class: 'rh-tries', hidden: true }, ...r.tries.map((x, j) => h('span', { text: `#${j + 1} · ${x.given_label || x.given || '–'} · ${mmss(x.ms)} · ${x.correct ? 'Right' : 'Wrong'}${x.reason ? ' · ' + x.reason : ''}` })));
      tg.addEventListener('click', () => { const o = list.hidden; list.hidden = !o; tg.setAttribute('aria-expanded', String(o)); tg.textContent = `${o ? '▾' : '▸'} ${r.tries.length} tries`; });
      row.append(h('div', { class: 'ract' }, tg), list);
    }
    return row;
  }
  function sittingCard(s, rows) {
    const card = h('section', { class: 'rh-sit', 'aria-label': `${srcWord(s.source || s.kind)} · ${day(s.at)}` });
    if (s.void) card.dataset.void = '';
    const topics = (s.topics || []).map(t => (TOPIC(t) || {}).short || t);
    const blanks = (s.blanks || []).length;
    const misses = (s.cells || []).filter(c => ['wrong', 'incorrect', 'rushed'].includes(c.result)).length;
    const asked = s.asked || (s.cells || []).length;
    card.append(h('p', { class: 't' }, `${srcWord(s.source || s.kind)}${topics.length ? ' · ' + topics.slice(0, 3).join(', ') + (topics.length > 3 ? ` +${topics.length - 3}` : '') : ''}`,
      h('span', { class: 'meta', text: [day(s.at), `${fmtN(s.right || 0)} / ${fmtN(asked)}`, s.minutes ? (UI.dur ? UI.dur(Math.round(s.minutes)) : `${Math.round(s.minutes)} min`) : null, blanks ? `${blanks} blank` : null, s.void ? 'discarded' : null].filter(Boolean).join(' · ') })));
    if ((s.cells || []).length && UI.cell) {
      const cells = h('div', { class: 'cells', role: 'group', 'aria-label': 'Every question in this sitting' });
      s.cells.forEach(c => {
        const st = c.blank ? 'blank' : resultOf({ result: c.result, correct: c.result === 'right' });
        const b = UI.cell(st, c.n + 1 || c.n, { size: 'sm', flag: c.flagged || null, onClick: () => openSittingCell(s, c) });
        cells.append(b);
      });
      card.append(cells);
    }
    if (!s.void) {
      const acts = h('div', { class: 'acts' });
      const types = new Set((s.cells || []).map(c => c.template).filter(Boolean)).size || asked;
      const re = h('button', { type: 'button', class: 'pill sm', text: `Rematch · same ${fmtN(types)} types, new numbers · Then → Now` });
      re.addEventListener('click', () => start({ rematch: s.session }, re));
      acts.append(re);
      if (misses || blanks) {
        const w = h('button', { type: 'button', class: 'btn sm', text: `Walk these misses · name each, then prove it · ~${Math.max(1, Math.round((misses + blanks) * 1.5))} min` });
        w.addEventListener('click', () => walk({ session: s.session }, w));
        acts.append(w);
      }
      if (misses) {
        const f = h('button', { type: 'button', class: 'btn sm', text: `Fix ${fmtN(misses)} · Then → Now` });
        f.addEventListener('click', () => start({ rematch: s.session, scope: 'misses', until_fixed: true }, f));
        const fm = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'More ways to fix', 'aria-haspopup': 'menu', text: '▾' });
        fm.addEventListener('click', () => UI.menu(fm, [{ label: 'Fix the misses + slow rights', onClick: () => start({ rematch: s.session, scope: 'weak' }) }], { label: 'Fix' }));
        acts.append(h('span', { class: 'rh-split' }, f, fm));
      }
      if (blanks) {
        const b = h('button', { type: 'button', class: 'btn sm', text: `Blanks · ${blanks} · fresh twins` });
        b.addEventListener('click', () => start({ rematch: s.session, scope: 'blanks' }, b));
        acts.append(b);
      }
      const href = sittingHref(s.kind, s.session);
      if (href) acts.append(h('a', { class: 'quiet', href, text: s.kind === 'drill' ? 'Summary' : 'Report' }));
      const more = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'More for this sitting', 'aria-haspopup': 'menu', text: '⋯' });
      more.addEventListener('click', () => UI.menu(more, [
        { label: 'Again, exactly (tests memory)', onClick: () => start({ retake: s.session }) },
        { separator: true },
        { label: 'Discard this sitting’s answers…', onClick: () => discard(s) },
      ], { label: 'More' }));
      acts.append(more);
      card.append(acts);
    } else {
      const r = h('button', { type: 'button', class: 'btn sm', text: 'Restore' });
      r.addEventListener('click', () => restore(s, r));
      card.append(h('div', { class: 'acts' }, h('span', { class: 'meta', text: 'Not counted' }), r));
    }
    if ((s.children || []).length) {
      card.append(h('p', { class: 'kids', text: `Rematched ×${s.children.length}${s.best !== undefined && s.best !== null ? ` · best ${fmtN(s.best)} / ${fmtN(asked)}` : ''}` }));
    }
    if (rows.length) card.append(h('div', { class: 'rh-list' }, ...rows));
    return card;
  }
  async function openSittingCell(s, c) {
    const L = S.lists.history;
    const i = L.items.findIndex(r => r.session === s.session && r.qid === c.qid);
    if (i >= 0) return openRow(i);
    const b = (s.blanks || []).find(x => x.qid === c.qid);
    if (b) openSingle({ template: b.template, seed: b.seed, blank: true, source: s.source });
  }
  async function discard(s) {
    const n = s.asked || (s.cells || []).length;
    const ok = await UI.confirm({ title: `Discard ${srcWord(s.source || s.kind)} · ${day(s.at)}?`, text: `${plural(n, 'answer')} leave your record: mistakes they opened close, fixes they made reopen. You can undo this.`, confirm: 'Discard', cancel: 'Keep them', destructive: true });
    if (!ok) return;
    try {
      const r = await UI.api(`/session/${encodeURIComponent(s.session)}/void`, { method: 'POST', body: {} });
      toast(`Discarded ${plural(r.answers ?? n, 'answer')}`, { undo: () => restore(s), ms: 6000 });
      refreshSoon(true);
    } catch (e) { toast(reasonOf(e)); }
  }
  async function restore(s, btn) {
    if (btn) btn.setAttribute('aria-busy', 'true');
    try { await UI.api(`/session/${encodeURIComponent(s.session)}/unvoid`, { method: 'POST', body: {} }); toast('Restored'); refreshSoon(true); }
    catch (e) { if (btn) btn.removeAttribute('aria-busy'); toast(reasonOf(e)); }
  }

  /* Fixed (V9, V10) */
  const TIERS = ['easy', 'medium', 'hard'];
  function checkState(r) {
    const st = fixedState(r);
    const next = r.due ? day(r.due) : null;
    const held = r.held ?? r.checks ?? 0;
    if (st === 'dismissed') return ['Dismissed', 'soft'];
    if (st === 'due') return ['Check due', 'amber'];
    if (!held) return [`Not checked yet${next ? ' · first check ' + next : ''}`, 'amber'];
    if (held >= 3) return ['Held all 3 ✓'];
    return [`Held ${held === 1 ? '1 check' : held} ✓${next ? ' · next ' + next : ''}`];
  }
  function paintFixed(box, L) {
    const ol = h('div', { class: 'rh-list' });
    L.items.forEach((r, i) => {
      const { row, btn } = rowShell('fixed', r, i, { label: r.label });
      const [stText, stCls] = checkState(r);
      const proven = new Set(r.tiers_proven || []);
      const avail = (r.tiers_available || []).slice().sort((a, b) => TIERS.indexOf(a) - TIERS.indexOf(b));
      const provenEl = avail.length > 1 ? h('span', { title: 'Proven at', 'aria-label': `Proven at ${avail.filter(t => proven.has(t)).map(t => TIER[t]).join(', ') || 'no level yet'}` },
        ...avail.map(t => h('span', { style: 'margin-right:8px' }, UI.dbars ? UI.dbars(t, { bare: true }) : TIER[t], proven.has(t) ? ' ✓' : ' ○'))) : null;
      const bits = [(TOPIC(r.topic) || {}).short || r.name, r.closed ? `fixed ${day(r.closed)}` : null, r.days_to_fix !== undefined && r.days_to_fix !== null ? `took ${plural(r.days_to_fix, 'day')}` : null,
        r.hits > 1 ? `missed ${r.hits}×` : null, r.relapses ? `relapsed ${r.relapses}×` : null, provenEl];
      btn.append(h('span', { class: 'lead', 'aria-hidden': 'true', text: fixedState(r) === 'dismissed' ? '–' : '✓', style: 'font: 700 15px var(--font)' }),
        h('div', {}, mtext(h('div', { class: 'l1' }), r.label || ''), l2(bits)), tagsEl([[stText, stCls]]));
      const acts = h('div', { class: 'ract' });
      const up = avail.find(t => !proven.has(t) && TIERS.indexOf(t) > Math.max(...[...proven].map(x => TIERS.indexOf(x)), -1));
      if (up && fixedState(r) !== 'dismissed') {
        const b = h('button', { type: 'button', class: 'btn sm', text: `Prove it at ${TIER[up]}` });
        b.addEventListener('click', () => proveIt(r, up));
        acts.append(b);
      }
      if (fixedState(r) === 'dismissed') {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Reopen' });
        b.addEventListener('click', async () => { b.setAttribute('aria-busy', 'true'); try { await UI.api('/mistakes/reopen', { method: 'POST', body: { id: r.id } }); toast('Back in Redo'); refreshSoon(true); } catch (e) { b.removeAttribute('aria-busy'); toast(reasonOf(e)); } });
        acts.append(b);
      }
      if (acts.children.length) row.append(acts);
      ol.append(row);
    });
    box.append(ol);
  }
  function proveIt(r, tier) {
    const body = { templates: [r.template], tiers: [tier], count: 1, source: 'review' };
    if (UI.twinSheet) UI.twinSheet({ body, title: `Prove it at ${TIER[tier]}`, onDone: () => refreshSoon(true) });
    else start(Object.assign({}, body, { source: 'mistakes' }));
  }

  /* ------------------------------------------------------------ tab heads (each part fails on its own, rule 8) */
  function part(host, title, fill) {
    const card = h('section', { class: 'card rh-card', 'aria-label': title || null });
    if (title) card.append(h('div', { class: 'card-head' }, h('h2', { class: 'rh-k', text: title })));
    const body = h('div');
    card.append(body);
    host.append(card);
    const run = async () => {
      body.replaceChildren();
      if (UI.skel) UI.skel(body, 'lines:2');
      try { const keep = await fill(body, card); if (keep === false) card.remove(); }
      catch (e) { body.replaceChildren(); UI.cardError(body, run, 'This part didn’t load.'); }
    };
    run();
    return card;
  }
  function paintHead() {
    const host = $('tabhead');
    host.replaceChildren();
    const tab = S.tab;
    if (tab === 'due') dueHead(host);
    else if (tab === 'redo') redoHead(host);
    else if (tab === 'marked') markedHead(host);
    else if (tab === 'saved') savedHead(host);
    else if (tab === 'history') historyHeadShell(host);
    else if (tab === 'fixed') fixedHead(host);
  }
  function paintHeadFromList(tab) {
    if (tab === 'history') historyHead();
    if (tab === 'fixed') paintHead();
  }

  // Due: today's card (V1)
  function dueHead(host) {
    const d = S.due;
    if (!d) { if (S.dueErr) UI.cardError(host, () => loadDue().then(() => { paintHead(); afterDue(); }), 'Today’s review didn’t load.'); return; }
    const exam = S.me && (S.me.exam_date || (S.me.learner && S.me.learner.exam_date));
    const soon = exam && (Date.parse(exam) - Date.now()) / 864e5 <= 7 && Date.parse(exam) >= Date.now() - 864e5;
    if (!d.total && !(d.forecast || []).some(f => f.checks || f.saved) && !soon) return;
    const card = h('section', { class: 'card rh-card', 'aria-label': 'Today' });
    const box = h('div', { class: 'rh-today' });
    const pct = d.total ? d.done / d.total : 0;
    const ring = h('span', { class: 'ring', style: `--p: ${pct}`, role: 'img', 'aria-label': `${d.done} of ${d.total} done today`, text: d.total ? `${d.done} / ${d.total}` : '0' });
    const mid = h('div');
    if (d.total && d.left === 0) {
      mid.append(h('p', { class: 'rh-big', text: 'Done for today' }));
      const tmr = (d.forecast || [])[1];
      const nt = tmr ? (tmr.checks || 0) + (tmr.saved || 0) : 0;
      if (nt) mid.append(h('p', { class: 'rh-wait', text: `${fmtN(nt)} due tomorrow` }));
    } else if (d.total) {
      const kinds = h('div', { class: 'rh-kinds' });
      const k = d.kinds || {};
      Object.keys(KIND).forEach(id => { if (k[id]) kinds.append(h('span', { class: 'rh-kind' + (KIND[id].cls ? ' ' + KIND[id].cls : '') }, KIND[id].text.replace(/ [✓✕●○]+$/, ''), h('b', { text: fmtN(k[id]) }))); });
      mid.append(kinds);
    } else mid.append(h('p', { class: 'rh-big', text: 'Nothing due today' }));
    if (d.waiting > 0) mid.append(h('p', { class: 'rh-wait', text: `${fmtN(d.waiting)} more wait for later days` }));
    if (soon) mid.append(h('p', { class: 'rh-line', style: 'margin-top:8px' }, h('a', { class: 'btn sm', href: '/plan/?print=sheet', text: 'Your test-day sheet' })));
    box.append(d.total ? ring : h('span'), mid);
    const fc = (d.forecast || []);
    if (fc.some(f => f.checks || f.saved) && UI.barChart) {
      const fh = h('div', { class: 'rh-fc' });
      UI.barChart(fh, fc.map((f, i) => ({ day: f.day, checks: f.checks, saved: f.saved, today: i === 0 })), {
        series: [{ key: 'checks', label: 'Check-ins', look: 'ink' }, { key: 'saved', label: 'Saved', look: 'amber' }], stacked: true, labels: 'weekday', today: 'ring', height: 72, unit: 'q', noun: 'due', legend: true, label: 'Due in the next 7 days' });
      box.append(fh);
    }
    card.append(box);
    host.append(card);
  }

  // Redo: named rate, why you lose points, habits, worth the most (V2, V4, V6, V7)
  function redoHead(host) {
    const c = S.counts || {};
    if (!c.open) return;
    if (c.diag_n >= 5) host.append(h('p', { class: 'rh-line' }, `You named your own mistake ${fmtN(c.diag_right)} of ${fmtN(c.diag_n)} times (${Math.round(100 * c.diag_right / c.diag_n)}%)`));
    part(host, 'Why you lose points · last 30 days', async body => {
      const d = await UI.api('/review/redo?limit=100&sort=worth', { quiet: true });
      let causes = d.causes || null;
      if (!causes && d.total <= (d.items || []).length) {
        causes = {};
        (d.items || []).forEach(x => { const k = x.kind === 'slip' ? 'slip' : x.cause || 'trap'; causes[k] = (causes[k] || 0) + 1; });
      }
      body.replaceChildren();
      // one cause alone says nothing the Redo count doesn't: the bar shows once there are two
      if (causes && Object.keys(causes).filter(k => causes[k]).length > 1 && UI.stackBar) {
        const segs = CAUSES.filter(([k]) => causes[k]).map(([k, l]) => ({ key: k, label: l, value: causes[k] }));
        const fixRow = h('div', { class: 'rh-row2', style: 'margin-top:12px' });
        UI.stackBar(body, segs, { largest: true, legend: false, noun: 'misses', label: 'Why you lose points', onPick: seg => { if (FB) FB.set('cause', seg.key); causeFix(fixRow, seg.key); } });
        body.append(fixRow);
        const cur = currentFilterValues().cause;
        if (cur) causeFix(fixRow, cur);
      } else body.closest('section').remove();
      worth(host, d);
    });
    part(host, 'Habits', async body => {
      const d = await UI.api('/review/redo?group=habit&limit=1', { quiet: true });
      const gs = (d.groups || []).filter(g => g.key !== 'other' && g.count >= 2).sort((a, b) => (b.pts || 0) - (a.pts || 0) || b.count - a.count).slice(0, 3);
      if (!gs.length) return false;
      body.replaceChildren();
      const list = h('div', { class: 'rh-list-p' });
      gs.forEach(g => {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Drill this habit · 8' });
        b.addEventListener('click', () => start({ source: 'habit', habit: g.key, count: 8 }, b));
        list.append(h('div', { class: 'rh-row2' }, h('b', { text: g.name }), g.tell ? h('i', { class: 'meta', style: 'font-family: var(--font)', text: g.tell }) : null,
          h('span', { class: 'meta', text: [plural(g.count, 'miss', 'misses'), g.pts ? `≈ ${fmtN(g.pts)} pts` : null].filter(Boolean).join(' · ') }), b));
      });
      const gaunt = h('button', { type: 'button', class: 'btn sm', text: 'Trap gauntlet · 10' });
      gaunt.addEventListener('click', () => start({ source: 'gauntlet', count: 10 }, gaunt));
      body.append(list, h('div', { class: 'rh-row2', style: 'margin-top:10px' }, gaunt));
    });
  }
  function causeFix(host, k) {
    host.replaceChildren();
    const b = (label, body) => { const x = h('button', { type: 'button', class: 'btn sm', text: label }); x.addEventListener('click', () => start(body, x)); return x; };
    const ids = selRows('redo').filter(r => (r.cause || 'trap') === k).map(r => r.id);
    const fixes = {
      trap: [b('Fix these', redoBody({ ids: ids.length ? ids : null })), S.lists.redo && S.lists.redo.items[0] ? spotBtn() : null],
      slip: [b('Careful set · 8', { pool: 'redo', ids: ids.length ? ids : null, count: 8, feedback: 'instant', source: 'mistakes' }), h('span', { class: 'meta', text: 'You know these. Reread the last line before Check.' })],
      misread: [b('Read the ask', { pool: 'redo', ids: ids.length ? ids : null, count: 8, feedback: 'instant', source: 'mistakes' })],
      clock: [b('Speed drill · 8', { pool: 'redo', ids: ids.length ? ids : null, count: 8, timing: 'pace', source: 'sprint' })],
      entry: [b('Grid-in entry · 8', { formats: ['spr'], count: 8, source: 'mistakes' })],
      gap: [b('Learn this type', { source: 'learn', templates: [...new Set(selRows('redo').filter(r => (r.cause || 'trap') === k).map(r => r.template))].slice(0, 3), example: true, count: 3 })],
    }[k] || [];
    fixes.filter(Boolean).forEach(x => host.append(x));
  }
  function spotBtn() {
    const x = h('button', { type: 'button', class: 'btn sm', text: 'Spot the trap' });
    x.addEventListener('click', () => { const r = (S.lists.redo.items || []).find(y => y.kind === 'misconception'); if (r) spot({ trap_id: r.id, label: r.label }); });
    return x;
  }
  function worth(host, d) {
    const c = S.counts || {};
    const top = (d.items || []).filter(x => x.pts).slice(0, 5);
    if ((c.open || 0) < 5 || top.length < 2) return;
    const card = h('section', { class: 'card rh-card', 'aria-label': 'Worth the most' }, h('div', { class: 'card-head' }, h('h2', { class: 'rh-k', text: 'Worth the most' })));
    const chips = h('div', { class: 'rh-chips' });
    top.forEach(x => {
      const b = h('button', { type: 'button', class: 'btn sm' }, h('span', { class: 'l', text: (x.label || '').length > 40 ? x.label.slice(0, 39) + '…' : x.label }), h('span', { class: 'pts', text: `≈ ${fmtN(x.pts)} pts` }));
      b.addEventListener('click', () => { const i = S.lists.redo ? S.lists.redo.items.findIndex(y => y.id === x.id) : -1; if (i >= 0) openRow(i); else openSingle({ template: x.template, seed: x.seed, trap: x }); });
      chips.append(b);
    });
    const sum = top.reduce((s, x) => s + (x.pts || 0), 0);
    const go = h('button', { type: 'button', class: 'pill sm', text: `Fix ${top.length} · about +${fmtN(sum)} pts` });
    go.addEventListener('click', () => start(redoBody({ ids: top.map(x => x.id) }), go));
    chips.append(go);
    card.append(chips);
    host.append(card);
  }

  // Marked: your instincts (V5)
  function markedHead(host) {
    const c = S.counts || {};
    if (!c.answers) return;
    const card = part(host, 'Your instincts', async body => {
      const since = S.sinceCal === 'all' ? '' : new Date(Date.now() - (+S.sinceCal) * 864e5).toISOString().slice(0, 10);
      const d = await UI.api(`/review/calibration${since ? `?since=${since}` : ''}`, { quiet: true });
      body.replaceChildren();
      const m = d.matrix || {};
      const total = ['sure', 'unsure', 'guess'].reduce((s, k) => s + ((m[k] || {}).right || 0) + ((m[k] || {}).wrong || 0), 0);
      const fl = d.flags || {};
      const ch = d.changes || {};
      if (!total && !fl.n && !ch.n) { body.append(h('p', { class: 'help', text: 'Tag how sure you are, and flag in tests: this shows what each is worth.' })); return; }
      const grid3 = h('div', { class: 'rh-grid3' });
      if (total) {
        const blind = (m.sure || {}).wrong || 0;
        const lucky = ((m.unsure || {}).right || 0) + ((m.guess || {}).right || 0);
        const mx = h('div', { class: 'rh-matrix', role: 'group', 'aria-label': 'How sure you were, against the result' }, h('span'), h('span', { class: 'h', text: 'Right' }), h('span', { class: 'h', text: 'Wrong' }));
        [['sure', 'Sure'], ['unsure', 'Unsure'], ['guess', 'Guess']].forEach(([k, l]) => {
          const row = m[k] || {};
          const n = (row.right || 0) + (row.wrong || 0);
          mx.append(h('span', { class: 'rl' }, l, k === 'sure' && row.assumed ? h('small', { text: `${fmtN(row.assumed)} assumed` }) : null));
          ['right', 'wrong'].forEach(res => {
            const v = row[res] || 0;
            const b = h('button', { type: 'button', 'aria-label': `${l} and ${res}: ${v}`, text: n ? `${fmtN(v)} · ${Math.round(100 * v / n)}%` : '–' });
            if (k === 'sure' && res === 'wrong' && v) b.dataset.hot = '';
            b.addEventListener('click', () => goHistory({ conf: k, result: res === 'right' ? 'right' : 'wrong' }));
            mx.append(b);
          });
        });
        const colA = h('div', {}, h('p', { class: 'rh-big', style: 'margin-bottom:8px', text: [blind ? `Blind spots ${fmtN(blind)}: sure and wrong` : null, lucky ? `Lucky ${fmtN(lucky)}` : null].filter(Boolean).join(' · ') || 'Certainty' }), mx);
        if (m.untagged) colA.append(h('p', { class: 'rh-foot', style: 'margin-top:6px', text: `untagged ${fmtN(m.untagged)}` }));
        grid3.append(colA);
      }
      const colB = h('div', { class: 'rh-list-p' });
      (d.readings || []).forEach(t => colB.append(h('p', { text: t })));
      if (ch.n) {
        colB.append(h('p', {}, h('b', { text: `${plural(ch.n, 'answer change')}` }), ` · ${fmtN(ch.wr)} wrong → right · ${fmtN(ch.rw)} right → wrong${ch.ww ? ` · ${fmtN(ch.ww)} wrong → wrong` : ''}${ch.pts ? ` · net ${ch.net > 0 ? '+' : ''}${fmtN(ch.net)} ≈ ${ch.pts > 0 ? '+' : ''}${fmtN(ch.pts)} pts` : ''}`));
        if (ch.net) colB.append(h('p', { class: 'help', text: ch.net > 0 ? 'Your second looks pay: keep flagging and returning.' : 'Your first answer is usually better: change only for a new reason.' }));
      }
      if (colB.children.length) grid3.append(colB);
      if (fl.n) {
        const colC = h('div', { class: 'rh-list-p' }, h('p', {}, h('b', { text: `${fmtN(fl.n)} flagged` }), ` · ${fmtN(fl.revisited)} came back${fl.never ? ` · ${fmtN(fl.never)} never came back${fl.never_wrong ? ` (${fmtN(fl.never_wrong)} of them wrong)` : ''}` : ''}`));
        if (fl.misses) colC.append(h('p', { text: `Your flags caught ${fmtN(fl.caught)} of your ${fmtN(fl.misses)} test misses (${Math.round(100 * fl.caught / fl.misses)}%)` }));
        const low = (fl.by_topic || []).filter(t => t.misses >= 3).sort((a, b) => a.caught / a.misses - b.caught / b.misses)[0];
        if (low) colC.append(h('p', { class: 'help', text: `${(TOPIC(low.topic) || {}).short || low.topic}: flags caught ${low.caught} of ${low.misses} misses. Flag more there.` }));
        grid3.append(colC);
      }
      body.append(grid3);
    });
    const headEl = card.querySelector('.card-head');
    const seg = UI.seg(null, [{ value: '30', label: '30 days' }, { value: '90', label: '90 days' }, { value: 'all', label: 'All' }], { value: S.sinceCal, label: 'Since', onChange: v => { S.sinceCal = v; paintHead(); } });
    headEl.append(h('span', { class: 'card-act' }, seg.el));
  }
  function goHistory(params) {
    S.filters.history = Object.assign({}, params);
    openTab('history', { push: true });
  }

  // Saved: Questions · Your rules, and the deck cards (V3, V19)
  function savedHead(host) {
    const c = S.counts || {};
    if (!c.saved) return;
    const row = h('div', { class: 'rh-row2' });
    const cards = [{ value: 'all', label: 'All', n: null }];
    if (S.prefs.saved_spaced !== false) {
      if (c.saved_due) cards.push({ value: 'due', label: 'Due today', n: c.saved_due });
      if (c.learned) cards.push({ value: 'learned', label: 'Learned', n: c.learned });
    }
    if (!cards.some(x => x.value === S.savedCard)) S.savedCard = 'all';
    if (cards.length > 1) {
      UI.seg(row, cards, { value: S.savedCard, label: 'Show', onChange: v => { S.savedCard = v; const L = S.lists.saved; if (L && L.all) { L.items = L.all; L.total = L.data.total; clientSaved(L); paintListHead(); paintList(); syncPane(); paintBar(); } } });
    }
    if (row.children.length) host.append(row);
  }

  // History: the summary card, pace and the rushed line (V8, V12)
  function historyHeadShell(host) { host.append(h('div', { id: 'histhead', class: 'rh-headbox', style: 'margin:0' })); }
  function historyHead() {
    const host = $('histhead');
    const L = S.lists.history;
    if (!host || !L || !L.data) return;
    host.replaceChildren();
    const s = L.data.summary;
    if (!s || !s.answers) return;
    const card = h('section', { class: 'card rh-card', 'aria-label': 'These answers' });
    const bits = [];
    bits.push(h('span', {}, h('b', { text: `${fmtN(s.right ?? Math.round((s.accuracy || 0) * s.answers))} / ${fmtN(s.answers)}` }), ' right'));
    if (s.median_ms) bits.push(h('span', {}, 'median ', h('b', { text: mmss(s.median_ms) })));
    if (s.timed && s.timed < s.answers) bits.push(`time known for ${fmtN(s.timed)} of ${fmtN(s.answers)}`);
    if (s.repaired) bits.push(`Repaired ${fmtN(s.repaired)}`);
    if (s.repeats) bits.push(`Repeats ${fmtN(s.repeats)}`);
    if (s.mixed) bits.push(`Mixed ${fmtN(s.mixed)}`);
    if (s.slow && s.slow.n) bits.push(`Slow right ${fmtN(s.slow.n)} · ${UI.dur ? UI.dur(Math.round(s.slow.over_ms / 60000)) : Math.round(s.slow.over_ms / 60000) + ' min'} over budget`);
    if (s.rushed) bits.push(`Rushed ${fmtN(s.rushed)}`);
    if (s.discarded) bits.push(`Discarded ${fmtN(s.discarded)}, not counted`);
    const line = h('p', { class: 'rh-row2', style: 'font: 500 14px/1.5 var(--font)' });
    bits.forEach((b, i) => { if (i) line.append(h('span', { class: 'meta', 'aria-hidden': 'true', text: '·' })); line.append(b instanceof Node ? b : h('span', { text: b })); });
    const bd = s.by_difficulty || {};
    const diff = h('div', { class: 'rh-row2', style: 'margin-top:10px' });
    TIERS.forEach(t => {
      const v = bd[t];
      if (!v) return;
      const n = typeof v === 'object' ? v.n : v, r = typeof v === 'object' ? v.right : null;
      diff.append(h('span', { class: 'rh-kind' }, tierBit(t), h('b', { text: r !== null && r !== undefined ? `${fmtN(r)} / ${fmtN(n)}` : fmtN(n) })));
    });
    const csv = h('button', { type: 'button', class: 'btn sm', text: 'Download CSV' });
    csv.addEventListener('click', () => downloadCsv(csv));
    diff.append(csv);
    card.append(line, diff);
    host.append(card);
    const pace = L.data.pace || [];
    if (pace.length) {
      const pc = h('section', { class: 'card rh-card', 'aria-label': 'Right but slow' }, h('div', { class: 'card-head' }, h('h2', { class: 'rh-k', text: 'Right but slow' })));
      const list = h('div', { class: 'rh-list-p' });
      pace.slice(0, 5).forEach(p => {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Speed drill · 8' });
        b.addEventListener('click', () => start({ templates: [p.template], count: 8, timing: 'pace', source: 'sprint' }, b));
        list.append(h('div', { class: 'rh-row2' }, h('b', { text: cap(p.skill || p.template) }),
          h('span', { class: 'meta', text: [p.median_ms ? `your median ${mmss(p.median_ms)}` : null, p.budget_ms ? `budget ${mmss(p.budget_ms)}` : null, p.right !== undefined && p.n ? `right ${Math.round(100 * p.right / p.n)}%` : p.accuracy !== undefined ? `right ${Math.round(p.accuracy * 100)}%` : null].filter(Boolean).join(' · ') }), b));
      });
      const sprint = h('button', { type: 'button', class: 'pill sm', text: `Fluency sprint · ${plural(Math.min(5, pace.length), 'type')}` });
      sprint.addEventListener('click', () => start({ templates: pace.slice(0, 5).map(p => p.template), count: 10, timing: 'pace', source: 'sprint' }, sprint));
      pc.append(list, h('div', { class: 'rh-row2', style: 'margin-top:10px' }, sprint));
      host.append(pc);
    }
    if (s.rushed >= 3 && currentFilterValues().result !== 'rushed') {
      const see = h('button', { type: 'button', class: 'btn sm', text: 'See them' });
      see.addEventListener('click', () => FB && FB.set('result', 'rushed'));
      host.append(h('p', { class: 'rh-line' }, `${plural(s.rushed, 'miss', 'misses')} in under a quarter of the time: slow down on these`, see));
    }
  }
  async function downloadCsv(btn) {
    btn.setAttribute('aria-busy', 'true');
    try {
      const path = listPath('history', null).replace('/review/history?', '/api/review/history.csv?');
      const r = await fetch(path, { headers: { 'X-Learner': UI.learner(), 'X-Tz': String(new Date().getTimezoneOffset()) } });
      if (!r.ok) throw new Error();
      const url = URL.createObjectURL(await r.blob());
      const a = h('a', { href: url, download: `sat-freshman-answers-${new Date().toISOString().slice(0, 10)}.csv` });
      doc.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch (_) { toast('The download didn’t start. Try again.'); }
    btn.removeAttribute('aria-busy');
  }

  // Fixed: the ledger and the stat line (V9, V10, V4)
  function fixedHead(host) {
    const c = S.counts || {};
    if (!c.fixed && !(S.ledger && S.ledger.weeks && S.ledger.weeks.some(w => w.opened || w.fixed))) return;
    const l = S.ledger;
    const card = h('section', { class: 'card rh-card', 'aria-label': 'Made and fixed, week by week' });
    host.append(card);
    if (!l) { if (UI.skel) UI.skel(card, 'chart'); return; }
    const weeks = (l.weeks || []).slice(phone() ? -8 : -12);
    const withData = weeks.filter(w => w.opened || w.fixed);
    const cur = weeks[weeks.length - 1] || {};
    const net = (cur.fixed || 0) - (cur.opened || 0);
    const head = h('div', { class: 'card-head' }, h('h2', { class: 'rh-k', text: 'Made and fixed' }));
    card.append(head);
    if (withData.length < 2) {
      const made = weeks.reduce((s, w) => s + (w.opened || 0), 0), fixed = weeks.reduce((s, w) => s + (w.fixed || 0), 0);
      card.append(h('p', { class: 'rh-big', text: `${fmtN(made)} made · ${fmtN(fixed)} fixed so far` }));
    } else {
      card.append(h('p', { class: 'rh-big', text: `This week: fixed ${fmtN(cur.fixed || 0)}, made ${fmtN(cur.opened || 0)}, net ${net > 0 ? '−' : net < 0 ? '+' : ''}${fmtN(Math.abs(net))}${c.median_days !== null && c.median_days !== undefined ? ` · median ${plural(c.median_days, 'day')} to fix` : ''}` }));
      if ((cur.fixed || 0) > (cur.opened || 0)) card.append(h('p', { class: 'help', text: 'Fixing them faster than you make them.' }));
      if (UI.barChart) {
        const ch = h('div', { style: 'margin-top:12px' });
        UI.barChart(ch, weeks.map(w => ({ key: w.week, label: day(w.week), fixed: w.fixed || 0, made: Math.max(0, (w.opened || 0) - (w.relapsed || 0)), relapsed: w.relapsed || 0, open: w.open_end || 0,
          tip: `${day(w.week)} week · ${fmtN(w.opened || 0)} made · ${fmtN(w.fixed || 0)} fixed · open ${fmtN(w.open_end || 0)}` })), {
          series: [{ key: 'fixed', label: 'Fixed', look: 'amber' }], down: [{ key: 'made', label: 'Made', look: 'ink' }, { key: 'relapsed', label: 'Relapsed', look: 'hatch' }],
          line: { key: 'open', label: 'Open' }, labels: 'label', height: phone() ? 150 : 180, legend: true, label: 'Mistakes made and fixed, week by week',
          onPick: row => { const d0 = row.key; const e = new Date(Date.parse(d0) + 6 * 864e5).toISOString().slice(0, 10); if (FB) FB.set('date', `${d0}..${e}`); } });
        card.append(ch);
      }
    }
    const f = l.forecast || {}, rate = l.rate || {};
    if (f.zero_on) {
      const exam = S.me && (S.me.exam_date || (S.me.learner && S.me.learner.exam_date));
      const gap = exam ? Math.round((Date.parse(exam) - Date.parse(f.zero_on)) / 864e5) : null;
      card.append(h('p', { style: 'margin-top:10px', text: `At this pace (${fmtN(Math.round(rate.fixed_week || 0))} fixed a week, ${fmtN(Math.round(rate.made_week || 0))} made) open mistakes reach 0 around ${day(f.zero_on)}${gap !== null && gap > 0 ? `, ${plural(gap, 'day')} before your SAT` : ''}.` }));
      if (f.after_exam && f.extra_minutes) card.append(h('p', { class: 'help', text: `That’s after your SAT. About ${fmtN(f.extra_minutes)} more minutes a day clears them in time.` }));
    }
    const st = (S.lists.fixed && S.lists.fixed.data && S.lists.fixed.data.stats) || {};
    const bits = [c.unchecked && `${fmtN(c.unchecked)} not checked yet`, st.relapsed && `${fmtN(st.relapsed)} relapsed${c.fixed ? ` (${Math.round(100 * st.relapsed / c.fixed)}%)` : ''}`,
      (st.recovered_month || c.recovered_month) && `recovered ≈ +${fmtN(st.recovered_month || c.recovered_month)} pts this month`, (st.dismissed || c.dismissed) && `${fmtN(st.dismissed || c.dismissed)} dismissed`].filter(Boolean);
    if (bits.length) card.append(h('p', { class: 'rh-foot', style: 'margin-top:10px', text: bits.join(' · ') }));
  }

  /* ------------------------------------------------------------ secondary actions (visible, never behind a disclosure) */
  function secondaryActions(tab) {
    const rows = selRows(tab);
    const n = selCount(tab);
    const out = [];
    const btn = (label, fn, cls = 'btn sm') => { const b = h('button', { type: 'button', class: cls, text: label }); b.addEventListener('click', () => fn(b)); return b; };
    if (tab === 'redo' && n) {
      out.push(btn(`Walk these · ${fmtN(n)} · ~${Math.max(1, Math.round(n * 1.5))} min`, b => walk({ ids: rows.map(r => r.id) }, b)));
      const blind = rows.filter(r => r.blind);
      if (blind.length) out.push(btn(`Drill my blind spots · ${fmtN(blind.length)}`, b => start({ pool: 'redo', ids: blind.map(r => r.id), level: 'as_missed', source: 'mistakes', feedback: 'instant' }, b)));
      out.push(btn('Print worksheet', () => worksheet('redo', rows.map(r => r.id))));
      out.push(btn(`Ask for help · ${fmtN(Math.min(n, 40))}`, () => askHelp(rows.slice(0, 40).map(r => [r.template, r.seed]))));
      out.push(btn('Share', () => share(rows.slice(0, 40).map(r => [r.template, r.seed]))));
      out.push(h('a', { class: 'quiet', href: '/review/print.html?sheet=log', text: 'Error log' }));
    }
    if (tab === 'marked') {
      const pick = n ? rows : (S.lists.marked || {}).items || [];
      const answered = pick.filter(r => r.answered).length;
      out.push(btn(`Again, exactly${answered ? ` · ${plural(answered, 'will be a repeat', 'will be repeats')}` : ''}`, b => start(barBody('marked', true, pick.length), b)));
      out.push(btn('Share', () => share(pick.slice(0, 40).map(r => [r.template, r.seed]))));
      if (n) out.push(btn('Unmark', () => unmark(rows), 'quiet'));
    }
    if (tab === 'saved') {
      const pick = n ? rows : (S.lists.saved || {}).items || [];
      out.push(btn('Again, exactly', b => start(barBody('saved', true, pick.length), b)));
      out.push(btn('Print worksheet', () => worksheet('saved', pick.map(r => [r.template, r.seed]))));
      out.push(btn('Share', () => share(pick.slice(0, 40).map(r => [r.template, r.seed]))));
      if (n) out.push(btn('Unsave', () => unsaveRows(rows), 'quiet'));
    }
    if (tab === 'history' && n) {
      out.push(btn('Again, exactly', b => start(barBody('history', true, n), b)));
      out.push(btn('Share', () => share(rows.slice(0, 40).map(r => [r.template, r.seed]))));
    }
    return out;
  }
  async function unmark(rows) {
    const L = S.lists.marked;
    const keys = new Set(rows.map(r => keyOf('marked', r)));
    const before = L.items;
    L.items = L.items.filter(r => !keys.has(keyOf('marked', r)));
    L.total = Math.max(0, L.total - rows.length);
    sel('marked').ids.clear(); saveSel('marked');
    paintList(); paintListHead(); paintBar(); syncPane();
    try {
      await Promise.all(rows.map(r => UI.api('/flags', { method: 'POST', body: { session: r.session, question_id: r.qid, on: false } })));
      refreshSoon(false);
      toast(rows.length === 1 ? 'Unmarked' : `${rows.length} unmarked`, { undo: async () => {
        await Promise.all(rows.map(r => UI.api('/flags', { method: 'POST', body: { session: r.session, question_id: r.qid, on: true } }).catch(() => {})));
        refreshSoon(true);
      } });
    } catch (e) { L.items = before; L.total += rows.length; paintList(); toast(reasonOf(e)); }
  }
  async function worksheet(pool, ids) {
    const each = (S.bar[S.tab] || {}).each || 1;
    const body = { pool, ids: ids.slice(0, 40), exact: false, each, feedback: 'end', source: 'worksheet' };
    try {
      const d = await UI.api('/drill', { method: 'POST', body });
      const w = open(`/practice/session/?id=${encodeURIComponent(d.id)}&print=1`, '_blank');
      if (!w) location.href = `/practice/session/?id=${encodeURIComponent(d.id)}&print=1`;
      refreshSoon(false);
    } catch (e) { toast(reasonOf(e)); }
  }
  async function share(items) {
    if (!items.length) return;
    try {
      const d = await UI.api('/sets', { method: 'POST', body: { kind: 'items', items } });
      const url = `${location.origin}${d.url || `/s/?c=${d.code}`}`;
      if (UI.copyText) UI.copyText(url, { toast: 'Link copied' }); else toast(url);
    } catch (e) { toast(reasonOf(e)); }
  }
  // V17: Ask for help carries what you picked and why; the server builds the context
  function askHelp(items) {
    if (!items.length) return;
    let ans = true, note = false;
    UI.sheet({
      title: items.length === 1 ? 'Ask for help with this question' : `Ask for help · ${items.length} questions`, size: 's',
      body: b => {
        UI.switch(b, { checked: true, label: 'Include my answer and the mistake behind it', onChange: v => { ans = v; } });
        UI.switch(b, { checked: false, label: 'Include my note', onChange: v => { note = v; } });
        b.append(h('p', { class: 'help', style: 'margin-top:8px', text: 'The link shows the question with answers hidden. After they try it, they see your pick.' }));
      },
      actions: [{ label: 'Copy link', primary: true, onClick: async api => {
        try {
          const d = await UI.api('/sets', { method: 'POST', body: { kind: 'items', items, cfg: { context: ans, note } } });
          const url = `${location.origin}${d.url || `/s/?c=${d.code}`}`;
          if (UI.copyText) UI.copyText(url, { toast: 'Link copied' });
        } catch (e) { toast(reasonOf(e)); return false; }
      } }],
    });
  }

  /* ------------------------------------------------------------ the action bar: summary, options, primary (V15) */
  function barState(tab) {
    return S.bar[tab] || (S.bar[tab] = { volume: 10, clock: 'off', minutes: 16, level: 'as_missed', feedback: 'instant', each: 1, err: '' });
  }
  function paintBar() {
    const bar = $('actbar');
    const box = $('optsbox');
    bar.replaceChildren(); box.replaceChildren();
    const tab = S.tab;
    if (!tab || tab === 'due') return;
    const L = S.lists[tab];
    if (!L || !L.data || !L.total) return;
    const b = barState(tab);
    const n = selCount(tab);
    if (!n && (tab === 'redo' || tab === 'fixed' || tab === 'history')) return;
    const opts = h('div', { class: 'rh-optrow', role: 'group', 'aria-label': 'Set options' });
    const opt = (k, el) => opts.append(h('span', { class: 'rh-opt' }, h('span', { class: 'k', text: k }), el));
    // Volume: 5 · 10 · 20 · 30 · 40 · 50 · All, and any count
    const vol = h('span', { class: 'rh-opt' });
    const volSeg = UI.seg(null, [5, 10, 20, 30, 40, 50, 0].map(v => ({ value: v, label: v ? String(v) : 'All' })), { value: b.volume || 0, label: 'How many', onChange: v => { b.volume = v || null; field.value = ''; paintSummary(); } });
    const field = h('input', { type: 'number', class: 'field sm', min: '1', max: '120', inputmode: 'numeric', 'aria-label': 'Or type how many', placeholder: '#' });
    if (b.volume && ![5, 10, 20, 30, 40, 50].includes(b.volume)) field.value = b.volume;
    field.addEventListener('input', () => { const v = Math.max(1, Math.min(120, parseInt(field.value, 10) || 0)); if (field.value) { b.volume = v; volSeg.set(-1, true); } else { b.volume = null; volSeg.set(0, true); } paintSummary(); });
    vol.append(h('span', { class: 'k', text: 'Questions' }), volSeg.el, field);
    opts.append(vol);
    const clockSeg = UI.seg(null, [{ value: 'off', label: 'Off' }, { value: 'pace', label: 'Pace' }, { value: 'custom', label: 'Custom' }], { value: b.clock, label: 'Clock', onChange: v => { b.clock = v; mins.hidden = v !== 'custom'; paintSummary(); } });
    const mins = h('input', { type: 'number', class: 'field sm', min: '1', max: '180', value: String(b.minutes), 'aria-label': 'Minutes on the clock', hidden: b.clock !== 'custom' });
    mins.addEventListener('input', () => { b.minutes = Math.max(1, Math.min(180, parseInt(mins.value, 10) || 16)); paintSummary(); });
    opts.append(h('span', { class: 'rh-opt' }, h('span', { class: 'k', text: 'Clock' }), clockSeg.el, mins));
    if (tab === 'marked' || tab === 'saved' || tab === 'history') {
      opt('Feedback', UI.seg(null, [{ value: 'instant', label: 'Instant' }, { value: 'end', label: 'At the end' }], { value: b.feedback, label: 'Feedback', onChange: v => { b.feedback = v; paintSummary(); } }).el);
      opt('Each', UI.seg(null, [1, 2, 3].map(v => ({ value: v, label: `${v}` })), { value: b.each, label: 'New questions per type', onChange: v => { b.each = v; paintSummary(); } }).el);
    }
    if (tab === 'redo' || tab === 'fixed') {
      const lvl = UI.seg(null, [{ value: 'as_missed', label: 'As missed' }, { value: 'any', label: 'Any' }, { value: 'harder', label: 'Harder' }], { value: b.level, label: 'Level', onChange: v => { b.level = v; paintSummary(); } });
      opt('Level', lvl.el);
    }
    const sum = h('div', { class: 'rh-sum', role: 'status' });
    const acts = h('div', { class: 'rh-acts' });
    function paintSummary() {
      const p = primaryFor(tab);
      sum.replaceChildren(h('span', { text: p.summary }));
      const echo = [b.clock === 'pace' ? 'pace clock' : b.clock === 'custom' ? `${b.minutes} min clock` : null,
        (tab === 'redo' || tab === 'fixed') && b.level !== 'as_missed' ? (b.level === 'harder' ? 'harder' : 'any level') : null,
        (tab === 'marked' || tab === 'saved' || tab === 'history') && b.feedback === 'end' ? 'answers at the end' : null,
        (tab === 'marked' || tab === 'saved' || tab === 'history') && b.each > 1 ? `${b.each} each` : null].filter(Boolean);
      if (echo.length) sum.append(h('small', { text: echo.join(' · ') }));
      if (b.err) sum.append(h('span', { class: 'err', text: b.err }));
      acts.replaceChildren();
      const pb = h('button', { type: 'button', class: 'pill', text: p.label });
      pb.addEventListener('click', async () => {
        if (p.run) return p.run();
        b.err = '';
        const e = await start(p.body, pb);
        if (e) { b.err = reasonOf(e); paintSummary(); }
      });
      acts.append(pb);
    }
    paintSummary();
    bar.append(sum, acts);
    box.append(opts);
    bar._repaint = paintSummary;
  }
  const count = (tab, questions) => { const b = barState(tab); return b.volume ? Math.min(b.volume, questions || b.volume) : questions; };
  function clockBody(tab) {
    const b = barState(tab);
    return b.clock === 'pace' ? { timing: 'pace' } : b.clock === 'custom' ? { timing: 'custom', minutes: b.minutes } : {};
  }
  function redoBody(o = {}) {
    const b = barState('redo');
    const v = currentFilterValues();
    const body = Object.assign({ pool: 'redo', ids: o.ids ?? null, level: b.level, source: 'mistakes', feedback: 'instant', repairs: 'next' }, clockBody('redo'));
    if (b.volume) body.count = b.volume;
    if (!body.ids) { if (v.topics && v.topics.length) body.topics = v.topics; if (v.difficulty && v.difficulty.length) body.tiers = v.difficulty; if (v.fmt) body.formats = [v.fmt]; }
    return body;
  }
  function idsFor(tab) {
    const L = S.lists[tab];
    const s = sel(tab);
    const rows = selRows(tab);
    // everything selected but not every row loaded: the pool with the filters the drill body knows
    const v = currentFilterValues();
    const onlyBodyFilters = !['kind', 'status', 'cause', 'conf', 'lens', 'habit', 'source', 'result', 'q', 'date'].some(k => v[k] && (!Array.isArray(v[k]) || v[k].length));
    if (s.all && !s.ids.size && L.total > L.items.length && onlyBodyFilters) return null;
    return rows.map(r => (tab === 'redo' || tab === 'fixed' ? r.id : tab === 'marked' ? [r.session, r.qid] : tab === 'saved' ? [r.template, r.seed] : r.id));
  }
  function barBody(tab, exact, q) {
    const b = barState(tab);
    const n = selCount(tab);
    const pool = { marked: 'marked', saved: 'saved', history: 'history', fixed: 'checks', redo: 'redo' }[tab];
    const body = Object.assign({ pool, source: tab === 'fixed' ? 'mistakes' : 'review', feedback: tab === 'fixed' ? 'instant' : b.feedback }, clockBody(tab));
    body.source = tab === 'fixed' || tab === 'redo' ? 'mistakes' : 'map';
    if (n) body.ids = idsFor(tab);
    else if (tab === 'saved' && S.savedCard !== 'all') body.ids = (S.lists.saved.items || []).map(r => [r.template, r.seed]);
    if (tab !== 'fixed') { body.exact = !!exact; if (!exact) body.each = b.each; }
    if (tab === 'fixed') body.level = b.level;
    if (b.volume) body.count = q ? Math.min(b.volume, q) : b.volume;
    return body;
  }
  function primaryFor(tab) {
    const L = S.lists[tab];
    const n = selCount(tab);
    const b = barState(tab);
    const rows = selRows(tab);
    const mins = q => Math.max(1, Math.round(q * ((S.due && S.due.median_s) || 95) / 60));
    if (tab === 'redo') {
      if (!n) return { label: `Select all ${fmtN(L.total)}`, summary: 'None selected', run: () => { const s = sel('redo'); s.all = true; s.ids.clear(); saveSel('redo'); paintList(); paintListHead(); paintBar(); } };
      const qs = rows.reduce((s, r) => s + (r.owed || 0), 0) || n;
      const types = new Set(rows.map(r => r.template)).size;
      const q = count(tab, qs);
      const harder = b.level === 'harder' ? rows.filter(r => r.difficulty === 'hard').length : 0;
      return { label: `Fix ${fmtN(q)}`, body: redoBody({ ids: idsFor('redo') }),
        summary: `${fmtN(n)} selected · ${plural(types, 'question type')} · ${plural(q, 'question')} · about ${mins(q)} min${harder ? ` · ${harder} can’t go harder` : ''}` };
    }
    if (tab === 'fixed') {
      if (!n) return { label: `Select all ${fmtN(L.total)}`, summary: 'None selected', run: () => { const s = sel('fixed'); s.all = true; s.ids.clear(); saveSel('fixed'); paintList(); paintListHead(); paintBar(); } };
      const q = count(tab, new Set(rows.map(r => r.template)).size || n);
      return { label: `Check these now · ${fmtN(q)}`, body: barBody('fixed', false, q), summary: `${fmtN(n)} selected · ${plural(q, 'question')} · one new one per type` };
    }
    if (tab === 'saved') {
      const c = S.counts || {};
      const due = (S.lists.saved.all || L.items).filter(r => r.due);
      if ((S.savedCard === 'due' || !n) && due.length && S.prefs.saved_spaced !== false) {
        const body = Object.assign({ pool: 'saved', ids: due.map(r => [r.template, r.seed]), exact: false, each: 1, source: 'map', feedback: b.feedback }, clockBody(tab));
        return { label: `Practise due · ${fmtN(due.length)}`, body, summary: n ? `${fmtN(n)} selected · ${plural(due.length, 'due question')}` : `${plural(due.length, 'saved question')} due today` };
      }
      const k = n || L.total;
      const q = count(tab, k * b.each);
      return { label: n ? `Twin this set · ${fmtN(n)} selected` : `Twin this set · all ${fmtN(c.saved || L.total)}`, body: barBody('saved', false, q), summary: `${n ? `${fmtN(n)} selected · ` : ''}${plural(q, 'new question')} · about ${mins(q)} min` };
    }
    if (tab === 'marked') {
      const k = n || L.total;
      const q = count(tab, k * b.each);
      return { label: n ? `Twin this set · ${fmtN(n)} selected` : `Twin this set · all ${fmtN(L.total)}`, body: barBody('marked', false, q), summary: `${n ? `${fmtN(n)} selected · ` : ''}${plural(q, 'new question')} · about ${mins(q)} min` };
    }
    if (tab === 'history') {
      if (!n) return { label: `Select all ${fmtN(Math.min(L.total, 120))}`, summary: 'Select answers to practise them again', run: () => { const s = sel('history'); s.all = true; s.ids.clear(); saveSel('history'); paintList(); paintListHead(); paintBar(); } };
      const types = new Set(rows.map(r => r.template)).size;
      const q = count(tab, types * b.each);
      return { label: `Twin this set · ${fmtN(n)} selected`, body: barBody('history', false, q), summary: `${fmtN(n)} selected · ${plural(types, 'question type')} · ${plural(q, 'new question')}${L.total > 120 && sel('history').all ? ' · first 120' : ''}` };
    }
    return { label: '', summary: '' };
  }

  /* ------------------------------------------------------------ the question pane (UI.review mode 'pane', R23) */
  function rowsFor(tab) { return tab === 'due' ? ((S.due && S.due.items) || []) : ((S.lists[tab] || {}).items || []); }
  function stripOf(tab, r) {
    if (tab === 'redo' || tab === 'due') {
      const status = r.done ? 'correct' : r.stuck ? 'stuck' : r.blind ? 'sure' : r.status || (r.kind === 'half' ? 'half' : r.kind === 'relapsed' ? 'relapsed' : r.kind === 'sure' ? 'sure' : 'open');
      const s = { status, label: r.done ? 'done' : status };
      if (r.owed !== undefined && r.owed !== null) { s.owed = r.owed; s.of = (r.clean || 0) + r.owed || 2; }
      return s;
    }
    if (tab === 'fixed') { const st = fixedState(r); return { status: st === 'held' && (r.held || r.checks) >= 3 ? 'held' : st, label: checkState(r)[0] }; }
    return { status: resultOf(r) };
  }
  function stubs(tab) {
    return rowsFor(tab).map((r, i) => ({ n: i + 1, status: stripOf(tab, r).status, strip: stripOf(tab, r), _row: r, flag: tab === 'marked' ? true : undefined }));
  }
  function openParam(tab, r) {
    if (!r) return null;
    if ((tab === 'redo' || tab === 'fixed') && r.id) return `trap:${r.id}`;
    if (tab === 'due' && r.trap_id) return `trap:${r.trap_id}`;
    if (r.template && r.seed !== undefined && r.seed !== null) return `q:${r.template}:${r.seed}`;
    if (r.saved) return `q:${r.saved[0]}:${r.saved[1]}`;
    return null;
  }
  function indexOfOpen(tab, open) {
    if (!open) return -1;
    const rows = rowsFor(tab);
    return rows.findIndex(r => openParam(tab, r) === open || (open.startsWith('q:') && `q:${r.template}:${r.seed}` === open));
  }
  function dropPlayer() {
    if (S.player) { const p = S.player; S.player = null; try { p.destroy(); } catch (_) {} }
    S.playerTab = null;
    if (wide()) $('pane').replaceChildren();
  }
  function syncPane() {
    const tab = S.tab;
    const rows = rowsFor(tab);
    if (!wide()) return;
    const pane = $('pane');
    if (!rows.length) { dropPlayer(); pane.replaceChildren(); $('body').classList.add('no-pane'); return; }
    $('body').classList.remove('no-pane');
    let at = indexOfOpen(tab, S.open || Q().get('open'));
    if (S.player && S.playerTab === tab && S.playerKind === 'list') {
      const cur = S.player.item && S.player.item._row;
      const keep = cur ? rows.findIndex(r => keyOf(tab, r) === keyOf(tab, cur)) : -1;
      S.player.setItems(stubs(tab), at >= 0 ? at : keep >= 0 ? keep : Math.min(S.player.at, rows.length - 1));
      return;
    }
    if (at < 0 && (S.open || Q().get('open') || '').startsWith('q:') && !S.player) {
      const [, t, sd] = (S.open || Q().get('open')).split(':');
      if (t && sd) { openSingle({ template: t, seed: +sd }); return; }
    }
    dropPlayer();
    S.player = makePlayer(pane, stubs(tab), Math.max(0, at), 'list');
    S.playerTab = tab;
  }
  function makePlayer(host, items, at, kind) {
    const tab = S.tab;
    S.playerKind = kind;
    const p = UI.review(host, items, {
      mode: 'pane', at, listKey: `hub.${tab}`, nKey: ['redo', 'due', 'fixed'].includes(tab) ? 'unseen' : 'miss', prefs: S.prefs, owner: true,
      axes: ['easier', 'harder'],
      // a twin keeps your trap on offer: want is {template: regex} (the drill body, 2.6), matched against the option's norm
      twinBody: it => {
        const q = it.q || {};
        const norm = it.norm && !String(it.norm).startsWith('~') ? it.norm : null;
        return Object.assign({ templates: [q.template], count: 1, source: 'review' },
          norm ? { want: { [q.template]: `^${String(norm).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$` } } : {});
      },
      on: paneOn(tab, kind, kind === 'single' ? items[0]._row : null),
    });
    return p;
  }
  function openRow(i) {
    const tab = S.tab;
    const rows = rowsFor(tab);
    if (!rows[i]) return;
    if (wide()) {
      if (!S.player || S.playerTab !== tab || S.playerKind !== 'list') { dropPlayer(); S.player = makePlayer($('pane'), stubs(tab), i, 'list'); S.playerTab = tab; }
      else S.player.go(i);
      return;
    }
    dropPlayer();
    S.player = makePlayer(null, stubs(tab), i, 'list');
    S.playerTab = tab;
  }
  function openSingle(ref) {
    const item = { n: 1, status: ref.blank ? 'unanswered' : 'incorrect', _row: Object.assign({ template: ref.template, seed: ref.seed }, ref.trap || {}), _single: true };
    dropPlayer();
    S.player = makePlayer(wide() ? $('pane') : null, [item], 0, 'single');
    S.playerTab = S.tab;
  }
  function markCurrent(i) {
    const p = S.player;
    const at = i !== undefined ? i : p && S.playerKind === 'list' && S.playerTab === S.tab ? p.at : -1;
    doc.querySelectorAll('#list .rh-row[aria-current]').forEach(r => r.removeAttribute('aria-current'));
    if (at >= 0 && wide()) { const r = doc.querySelector(`#list .rh-row[data-i="${at}"]`); if (r) r.setAttribute('aria-current', 'true'); return r; }
    return null;
  }

  // where a row's exact question lives: its own pair, or the latest miss on its template
  async function refOf(r) {
    if (r.template && r.seed !== undefined && r.seed !== null && !r.kind_due) return { template: r.template, seed: r.seed };
    if (r.saved) return { template: r.saved[0], seed: r.saved[1] };
    if (r.template) {
      const f = await UI.api(`/review/family?template=${encodeURIComponent(r.template)}&limit=20`, { quiet: true });
      const a = (f.attempts || []).find(x => !x.correct && x.openable !== false) || (f.attempts || []).find(x => x.openable !== false);
      if (a) return { template: r.template, seed: a.seed };
    }
    if (r.topic) {
      const hst = await UI.api(`/review/history?topics=${encodeURIComponent(r.topic)}&limit=1`, { quiet: true });
      const a = (hst.items || [])[0];
      if (a) return { template: a.template, seed: a.seed };
    }
    throw new Error('no question');
  }
  async function fetchItem(template, seed) {
    const key = `${template}:${seed}`;
    if (S.cache.has(key)) { const v = S.cache.get(key); S.cache.delete(key); S.cache.set(key, v); return v; }
    const d = await UI.api(`/review/item?template=${encodeURIComponent(template)}&seed=${encodeURIComponent(seed)}`, { quiet: true });
    S.cache.set(key, d);
    while (S.cache.size > 20) S.cache.delete(S.cache.keys().next().value);
    return d;
  }
  const EVENT = { open: 'opened', miss: 'missed', pip: 'clean ✓', fixed: 'Fixed', check_ok: 'Check-in ✓', relapse: 'Relapsed', dismissed: 'Dismissed', restored: 'Restored', reopened: 'Reopened', discarded: 'Discarded' };
  function toItem(d, r, tab) {
    const q = Object.assign({}, d.question || {}, { template: d.template, seed: d.seed, topic: d.topic, skill: (d.question && d.question.skill) || r.skill, name: r.skill || (d.question && d.question.name) });
    delete q.level;
    const last = (d.attempts || [])[0] || null;
    const mc = q.type !== 'spr';
    const given = last ? (mc && /^\d+$/.test(String(last.given)) ? +last.given : last.given) : null;
    const reveal = d.answer !== null && d.answer !== undefined;
    const fb = reveal ? {
      correct: last ? !!last.correct : null, given, answer: d.answer, answer_index: mc && /^[A-E]$/.test(String(d.answer)) ? LET.indexOf(d.answer) : null,
      reasons: d.reasons, rationale: d.rationale, mistake: last && !last.correct && last.reason ? cap(last.reason) : null, steps: d.steps || undefined,
    } : (last ? { given } : null);
    const res = last ? ({ right: 'correct', wrong: 'incorrect', repaired: 'repaired', repeat: 'repeat', mixed: 'mixed' }[last.result] || (last.correct ? 'correct' : 'incorrect')) : 'unanswered';
    const traps = d.traps || [];
    const tied = r.trap_id || (tab === 'redo' || tab === 'fixed' ? r.id : null);
    const trap = traps.find(t => (tied && t.id === tied) || (r.norm && t.norm === r.norm)) || (tied ? null : traps[0]) || null;
    let mistake = null;
    if (trap) mistake = { status: r.stuck ? 'stuck' : trap.status, owed: trap.owed, of: trap.norm === '~unsure' ? 1 : 2, hits: trap.hits, label: trap.label, relapses: trap.relapses, trap_id: trap.id };
    else if ((tab === 'fixed' && r.closed_how === 'fixed') || (tab === 'due' && r.kind === 'check')) mistake = { status: 'fixed', fixed_at: r.closed || r.since, label: r.label };
    const src = last ? last.source : r.source;
    const sitting = last && last.session ? { label: `${srcWord(src)} · ${day(last.at)}`, href: src === 'review' ? null : sittingHref(['section', 'module', 'diagnostic', 'test'].includes(src) ? 'test' : 'drill', last.session) } : null;
    const story0 = (d.story || []).length > 7 ? [d.story[0], ...d.story.slice(-5)] : (d.story || []);   // the opening and the latest five
    const story = story0.map(n => ({ at: n.at, event: n.event, source: srcWord(n.source), result: n.result, attempt: n.attempt,
      label: [n.pick ? `picked ${n.pick}` : null, EVENT[n.event] || n.event].filter(Boolean).join(' · ') }));
    return {
      q, fb, status: res, _row: r, strip: stripOf(tab, r),
      flag: !!d.flagged, saved: !!d.saved, note: d.note, marks: d.marks, rule: d.rule, path: d.path,
      tries: (d.tries || []).map(t => ({ given_label: mc && /^\d+$/.test(String(t.given)) ? LET[+t.given] : t.given, correct: !!t.correct, ms: t.ms })),
      story: story.length > 1 || (story.length && trap) ? story : null,
      summary: d.summary && d.summary.days_to_fix !== null && d.summary.days_to_fix !== undefined ? d.summary : null,
      elsewhere: (d.elsewhere || []).map(x => ({ skill: cap(x.skill) })), new: !!d.new && !d._revealedHere, diag_choices: d.new ? d.diag_choices : null,
      attempt_id: last ? last.id : null, trap_id: trap ? trap.id : null, norm: trap ? trap.norm : r.norm, session: last ? last.session : null, qid: last ? last.qid : null,
      ms: last ? last.ms : null, budget_ms: d.budget_ms, worth: r.pts !== undefined && r.pts !== null ? r.pts : d.pts, sitting, mistake,
      cause: last && !last.correct ? { cause: r.cause || last.diag_kind || 'trap', auto: !last.diag } : null,
      family: d.family ? { seen: d.family.seen, right: d.family.right, repaired: d.family.repaired, recent: (d.family.recent || []).map(x => ({ result: x })) } : null,
      blank: res === 'unanswered',
    };
  }
  function paneOn(tab, kind, single) {
    const L = () => rowsFor(tab);
    return {
      load: async i => {
        const r = kind === 'single' ? single : L()[i];
        if (!r) throw new Error('gone');
        const ref = await refOf(r);
        const d = await fetchItem(ref.template, ref.seed);
        return toItem(d, r, tab);
      },
      show: (i, item) => {
        const r = item && item._row;
        const op = openParam(tab, r);
        S.open = op;
        const u = new URL(location.href);
        if (op) u.searchParams.set('open', op); else u.searchParams.delete('open');
        history.replaceState(history.state, '', u);
        const row = kind === 'list' ? markCurrent(i) : markCurrent(-1);
        const first = !S._shown; S._shown = true;
        if (row && wide() && !first) { const rc = row.getBoundingClientRect(); if (rc.top < 120 || rc.bottom > innerHeight - 120) row.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
      },
      close: () => {
        S.player = null; S.playerTab = null;
        const u = new URL(location.href); u.searchParams.delete('open'); history.replaceState(history.state, '', u); S.open = null;
      },
      seen: async item => {
        if (!item || !item.attempt_id || item._seenSent) return;
        item._seenSent = true;
        try { await UI.api('/review/seen', { method: 'POST', body: { attempt_id: item.attempt_id }, quiet: true }); dropCache(item); if (item.new) refreshSoon(false); } catch (_) {}
      },
      why: async (item, b) => {
        const d = await UI.api('/review/why', { method: 'POST', body: Object.assign({ attempt_id: item.attempt_id }, b) });
        dropCache(item); refreshSoon(true);
        return { called: !!d.called, label: d.label, cause: d.cause };
      },
      rule: async (item, text) => {
        await UI.api('/notes', { method: 'POST', body: { attempt_id: item.attempt_id, scope: 'type', note: text || '' } });
        dropCache(item);
      },
      save: async (item, on) => {
        await UI.api('/saved', { method: 'POST', body: { template: item.q.template, seed: item.q.seed, on } });
        dropCache(item); refreshSoon(tab === 'saved');
      },
      savedWhy: async (item, why) => { await UI.api('/saved', { method: 'PATCH', body: { template: item.q.template, seed: item.q.seed, why } }); },
      lucky: async item => { await UI.api('/mistakes/add', { method: 'POST', body: { template: item.q.template, seed: item.q.seed } }); toast('Added to Redo'); refreshSoon(tab === 'redo'); },
      mark: async (item, on) => {
        if (item.session && item.qid) await UI.api('/flags', { method: 'POST', body: { session: item.session, question_id: item.qid, on } });
        else if (!on) await UI.api('/flags', { method: 'POST', body: { template: item.q.template, seed: item.q.seed, session: item.session, on: false } });
        else throw new Error('no sitting');
        dropCache(item); refreshSoon(tab === 'marked');
      },
      story: async (item, node) => {
        const f = await UI.api(`/review/family?template=${encodeURIComponent(item.q.template)}&limit=100`, { quiet: true });
        const a = (f.attempts || []).find(x => x.id === node.attempt);
        if (!a) return null;
        const d = await fetchItem(item.q.template, a.seed);
        return toItem(d, Object.assign({}, item._row, { template: item.q.template, seed: a.seed }), tab);
      },
      related: item => start({ pool: 'related', ids: item.norm, each: 1, source: 'mistakes', feedback: 'instant' }),
      spot: item => spot({ trap_id: item.trap_id, label: item.mistake && item.mistake.label }),
      share: item => share([[item.q.template, item.q.seed]]),
      help: item => askHelp([[item.q.template, item.q.seed]]),
      addRedo: async item => { await UI.api('/mistakes/add', { method: 'POST', body: { template: item.q.template, seed: item.q.seed } }); toast('Added to Redo'); dropCache(item); refreshSoon(false); },
      dismiss: async item => {
        const id = item.trap_id;
        if (!id) return;
        await UI.api('/mistakes/dismiss', { method: 'POST', body: { id } });
        dropCache(item);
        toast('Removed from Redo', { undo: async () => { await UI.api('/mistakes/restore', { method: 'POST', body: { id } }).catch(() => {}); refreshSoon(true); } });
        refreshSoon(true);
      },
      closed: (item, fb) => {
        dropCache(item);
        toast(`Fixed: ${(item.mistake && item.mistake.label) || 'your mistake'}`);
        const row = doc.querySelector(`#list .rh-row[data-i="${S.player ? S.player.at : -1}"]`);
        if (row && tab === 'redo') { if (matchMedia('(prefers-reduced-motion: reduce)').matches) row.remove(); else { row.style.transition = 'opacity .25s, max-height .25s'; row.style.overflow = 'hidden'; row.style.maxHeight = row.offsetHeight + 'px'; requestAnimationFrame(() => { row.style.opacity = '0'; row.style.maxHeight = '0px'; }); } }
        refreshSoon(false);
        loadCounts();
      },
      twinAnswer: item => { dropCache(item); refreshSoon(false); },
      note: item => { if (tab === 'saved') { const row = doc.querySelector(`#list .rh-row[data-i="${S.player ? S.player.at : -1}"]`); const r = item._row; if (row && r) noteEditor(row, r, row.querySelector('.ract .btn') || row); } },
    };
  }
  function dropCache(item) { if (item && item.q) S.cache.delete(`${item.q.template}:${item.q.seed}`); }

  // Spot the trap: a fresh question whose options include your trap; which choice is it? (v2 extra)
  async function spot(o) {
    if (!o.trap_id) return;
    let d;
    try { d = await UI.api('/review/spot', { method: 'POST', body: { trap_id: o.trap_id } }); }
    catch (e) { toast(reasonOf(e)); return; }
    const q = d.question || {};
    UI.sheet({
      title: 'Spot the trap', size: 'm',
      body: b => {
        b.append(h('p', { class: 'rh-big', style: 'margin-bottom:10px' }, 'Which choice comes from: ', h('i', { text: d.prompt || o.label || '' }), '?'));
        b.append(mtext(h('p', { class: 'q-stem', style: 'font: 400 var(--q-size, 18px)/1.5 var(--serif); margin-bottom: 12px' }), q.stem || ''));
        const list = h('div', { class: 'rh-list-p', role: 'group', 'aria-label': 'Choices' });
        const out = h('p', { class: 'help', role: 'status', style: 'margin-top:10px' });
        (q.choices || []).forEach((c, i) => {
          const btn = h('button', { type: 'button', class: 'btn', style: 'justify-content:flex-start; text-align:left; height:auto; min-height:44px; padding:8px 12px' }, h('b', { text: `${LET[i]}  ` }), mtext(h('span'), c));
          btn.addEventListener('click', async () => {
            list.querySelectorAll('button').forEach(x => { x.disabled = true; });
            try {
              const r = await UI.api(`/review/spot/${encodeURIComponent(d.id)}`, { method: 'POST', body: { answer: i } });
              const ti = r.trap_index;
              list.querySelectorAll('button').forEach((x, j) => { if (j === ti) x.style.boxShadow = 'inset 0 0 0 1.5px var(--amber)'; if (j === i && j !== ti) x.style.boxShadow = 'inset 0 0 0 1.5px var(--ink)'; });
              out.textContent = r.correct ? `Yes: ${LET[ti]} is the trap.` : `Not quite: the trap is ${LET[ti]}.`;
            } catch (e) { out.textContent = reasonOf(e); }
          });
          list.append(btn);
        });
        b.append(list, out);
      },
      actions: [{ label: 'Done', primary: true }],
    });
  }

  /* ------------------------------------------------------------ keys (R22, §2.8) */
  function registerKeys() {
    try {
      UI.keys.register('review', {
        'Shift+R': { does: 'Start review', run: () => { const b = $('start').querySelector('.rh-split .pill'); if (b) b.click(); } },
        '/': { does: 'Search this list', run: () => { const i = $('filters').querySelector('input[type=search]'); if (i) i.focus(); } },
        X: { does: 'Select the open row', run: () => { const r = doc.querySelector('#list .rh-row[aria-current] .sel input') || (doc.activeElement && doc.activeElement.closest && doc.activeElement.closest('.rh-row') && doc.activeElement.closest('.rh-row').querySelector('.sel input')); if (r) r.click(); } },
      }, { label: 'Review' });
    } catch (_) {}
    $('list').addEventListener('keydown', e => {
      if (!['ArrowDown', 'ArrowUp'].includes(e.key)) return;
      const btns = [...doc.querySelectorAll('#list .rh-rb')].filter(b => b.offsetParent);
      const i = btns.indexOf(doc.activeElement);
      if (i < 0) return;
      e.preventDefault();
      const j = Math.max(0, Math.min(btns.length - 1, i + (e.key === 'ArrowDown' ? 1 : -1)));
      btns[j].focus();
    });
  }

  boot();
})();
