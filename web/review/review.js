/* ============================================================================
   SAT Freshman -- the Review hub (/review/): spec 3.9, review.md V1-V19, R2, R5, R23.

   One page: a header row with today's review (Start review; its ▾ holds the minutes and the
   list preview), notes (new misses to walk, a worksheet waiting), a tab row with the counts
   inline (Due, Redo, Marked, Saved, History, Fixed; each number said once, decision 7), the
   open tab's head (short lines, and one closed Insights disclosure), its filters, its list
   beside the question pane (UI.review mode 'pane', F3; a column from 1280px), and an action
   bar that starts a set from the list or a selection (the drill body, R10), with its
   options behind Options. One orange primary per screen: the bar's when it shows, else Start.

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
  const ptsW = n => (Math.abs(n) === 1 ? 'pt' : 'pts');
  const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : '');
  const plural = (n, one, many) => `${fmtN(n)} ${n === 1 ? one : (many || one + 's')}`;
  const day = d => (d ? UI.date(d, 'short') : '');
  const mmss = ms => (ms ? UI.mmss(Math.round(ms / 1000)) : '–');
  const toast = (t, o) => UI.toast && UI.toast(t, o);
  // a polite live line for what the screen already shows (the fix moment beside the pane)
  let live = null;
  const say = t => { if (!live) { live = h('p', { class: 'sr', role: 'status' }); $('main').append(live); } live.textContent = ''; setTimeout(() => { live.textContent = t; }, 50); };
  const reasonOf = e => {
    const d = e && e.detail;
    const r = (d && typeof d === 'object' && (d.reason || d.message)) || (typeof d === 'string' ? d : null);
    return r ? cap(String(r).replace(/_/g, ' ')) : 'That didn’t work. Try again.';
  };
  const ss = {
    get(k, d) { try { const v = sessionStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
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
  const { srcWord, sittingHref } = window.ReviewItem;
  const LET = 'ABCDE';
  const TOPIC = t => (UI.TOPIC && UI.TOPIC[t]) || null;
  const dshort = d => ((UI.DOMAINS || []).find(x => x[0] === d) || [])[1] || d;
  const tname = t => UI.topicName(t);   // a topic's short name, either subject

  /* ------------------------------------------------------------ subject (one at a time, DESIGN 1)
     Every list, count and set here is one subject's: each /review/* read carries it (sub), and so does each
     drill body (start). Math's grid-in and habit tools and the Math samples stay off the R&W view (rw). */
  const sub = p => `${p}${p.includes('?') ? '&' : '?'}subject=${S.subject}`;
  const rw = () => S.subject === 'rw';

  /* ------------------------------------------------------------ state */
  const TABS = [
    { id: 'due', k: 'Due today', short: 'Due' }, { id: 'redo', k: 'Redo', short: 'Redo' }, { id: 'marked', k: 'Marked', short: 'Marked' },
    { id: 'saved', k: 'Saved', short: 'Saved' }, { id: 'history', k: 'History', short: 'History' }, { id: 'fixed', k: 'Fixed', short: 'Fixed' },
  ];
  const S = {
    tab: null, counts: null, countsErr: false, due: null, dueErr: false, prefs: {}, me: null, minutes: 10,
    lists: {}, filters: {}, bar: {}, player: null, playerTab: null, cache: new Map(), token: 0, ledger: null,
    fb: null, marked: 'miss', savedCard: 'all', savedView: new URLSearchParams(location.search).get('view') === 'rules' ? 'rules' : 'questions', sinceCal: '30', open: null,
    subject: UI.subject.get(), sel: {},
  };
  const Q = () => new URLSearchParams(location.search);
  // a selection is one subject's rows (trap ids and pairs never match the other subject's list)
  const selKey = tab => `satf.review.sel.${S.subject}.${tab}`;
  const selDefaultAll = tab => tab === 'redo' || tab === 'fixed';
  function sel(tab) {
    const k = selKey(tab);
    if (!S.sel[k]) {
      const s = ss.get(k, null);
      S.sel[k] = s && typeof s === 'object' ? { all: !!s.all, ids: new Set(s.ids || []) } : { all: selDefaultAll(tab), ids: new Set() };
    }
    return S.sel[k];
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
  const selRows = tab => ((S.lists[tab] || {}).items || []).filter(r => !r._closed && isSel(tab, keyOf(tab, r)));
  function keyOf(tab, r) {
    if (tab === 'due') return r.key;
    if (tab === 'redo' || tab === 'fixed') return String(r.id);
    if (tab === 'marked') return `${r.session}|${r.qid}`;
    if (tab === 'saved') return `${r.template}:${r.seed}`;
    return String(r.id);
  }

  /* ------------------------------------------------------------ boot */
  async function boot() {
    UI.subjectSeg($('subject'), { value: S.subject, onChange: switchSubject });
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
    // the sticky list head takes the scroll shadow while rows slide under it (the list column scrolls from 1280px)
    if (UI.scrolled) UI.scrolled($('listhead'), { root: $('panel') });
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

  // the other subject: its counts, due list and the open tab's list load in place; the filters (a topic of the old
  // subject) and the open question are left behind
  async function switchSubject(v) {
    if (v === S.subject) return;
    S.subject = v;
    S.counts = S.due = S.ledger = savedP = null;
    S.lists = {}; S.filters = {}; S.open = null;
    const u = new URL(location.href);
    u.search = new URLSearchParams(Object.assign({ tab: S.tab, subject: v }, S.tab === 'saved' && S.savedView === 'rules' ? { view: 'rules' } : {})).toString();
    history.replaceState(history.state, '', u);
    dropPlayer();
    paintStartSkeleton();
    await Promise.all([loadCounts(), loadDue()]);
    openTab(S.tab, { push: false });
  }
  async function loadCounts() {
    const s = S.subject;
    try { const c = await UI.api(sub('/review/counts')); if (s !== S.subject) return; S.counts = c; S.countsErr = false; }
    catch (_) { if (s !== S.subject) return; S.countsErr = true; }
    paintTabs(); paintNotes();
    if (S.due) paintStart();
  }
  async function loadDue() {
    const s = S.subject;
    try {
      const d = await UI.api(sub('/review/due'));
      if (s !== S.subject) return;
      S.due = d;
      S.dueErr = false;
      // the minutes seg re-cuts the same frozen order on the server (V1); the pref is what it reads
      if (S.due.minutes !== undefined && S.due.minutes !== null && S.due.minutes !== S.minutes) S.minutes = S.due.minutes;
    } catch (_) { if (s !== S.subject) return; S.dueErr = true; }
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
    if (UI.skel) UI.skel(box, 'pill');
  }
  const MINUTES = [5, 10, 15, 20, 30, 45, 60, 0];
  function startBody(boxMin) { return { source: 'due', box: boxMin || null, subject: S.subject }; }
  function startPlan() {
    const d = S.due, c = S.counts || {};
    const m = S.minutes;
    if (d && d.left > 0) {
      if (!m) return { label: 'All', body: startBody(0), all: true };
      return { label: `Start review · ${m} min`, body: startBody(m) };
    }
    const box = m || 10;
    // nothing due: the box serves the open mistakes (a due box alone would have nothing to serve)
    if ((c.open || 0) > 0) return { label: `Fix ${fmtN(Math.min(c.open, (d && d.cap) || 6))} · ${box} min`, body: Object.assign(startBody(box), { pool: 'redo' }) };
    return { label: `Keep going · ${box} min`, body: { source: 'next', box, subject: S.subject } };
  }
  function paintStart() {
    const box = $('start');
    box.replaceChildren();
    if (S.dueErr && !S.due) { UI.cardError ? UI.cardError(box, () => loadDue().then(afterDue), 'Today’s review didn’t load.') : null; return; }
    const d = S.due || {};
    // a new student has one way in, the empty state's start (the user's rule, 2026-09-28)
    if (S.counts && !S.counts.answers && !d.total) { box.hidden = true; return; }
    box.hidden = false;
    const plan = startPlan();
    const main = h('button', { type: 'button', class: 'pill rh-go', 'aria-keyshortcuts': 'Shift+R' }, h('span', { text: plan.label }));
    main.addEventListener('click', () => start(plan.body, main));
    // the ▾: the list first (what the set will serve), then the minutes as radio items
    const more = h('button', { type: 'button', class: 'pill', 'aria-haspopup': 'menu', 'aria-label': 'Minutes, and the list before starting', title: 'Minutes and the list' }, UI.icon('caret_down', 16));
    const k = d.kinds || {};
    const bits = d.left > 0 ? [k.check && plural(k.check, 'check-in'), d.quick_wins && plural(d.quick_wins, 'quick win'), d.closes && `closes up to ${plural(d.closes, 'mistake')}`].filter(Boolean) : [];
    // a printed worksheet waiting for its answers is one item here too, so every tab reaches it (Due and Redo pin it)
    const ws = (S.counts && S.counts.worksheets_waiting) || 0;
    UI.menu.bind(more, () => [
      { label: 'See the list first', sub: bits.join(' · ') || undefined, onClick: () => previewSheet(plan.body) },
      ...(ws ? [{ label: 'Enter worksheet answers', sub: `${plural(ws, 'worksheet')} waiting`, href: S.wsHref || '/practice/' }] : []),
      { separator: true },
      { group: 'Minutes' },
      ...MINUTES.map(v => ({ label: v ? `${v} min` : 'All', radio: 'min', checked: v === S.minutes, close: true, onClick: () => setMinutes(v) })),
    ], { label: 'Today’s review', align: 'end' });
    box.append(h('div', { class: 'split-btn' }, main, more));
    syncPrimary();
    if (plan.all) allLabel(main);
  }
  async function setMinutes(v) {
    if (v === S.minutes) return;
    S.minutes = v;
    try { await UI.prefs.set({ review_minutes: v }); } catch (_) { toast('Not saved. Try again.'); }
    await loadDue();
    afterDue();
    paintTabs();
  }
  // one orange primary on the screen: the action bar's when it shows, else Start
  function syncPrimary() {
    const bar = !!$('actbar').firstChild;
    $('start').querySelectorAll('.split-btn > button').forEach(b => { b.classList.toggle('pill', !bar); b.classList.toggle('btn', bar); });
    // Redo's bar is its one primary (Fix the selected): the header's own Fix would be a second count beside it
    const split = $('start').querySelector('.split-btn');
    if (split) split.hidden = bar && S.tab === 'redo';
  }
  // All: every frozen key, then every open trap max(owed) times, at most 120 (V1): the preview counts it
  async function allLabel(btn) {
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
      // every set started here is this view's subject (a body that names nothing would be Math's)
      const d = await UI.api('/drill', { method: 'POST', body: Object.assign({ subject: S.subject }, body) });
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
        const li = h('li', { class: 'rh-row plain has-x' }, h('span'),
          h('div', { class: 'rh-rb' },
            h('div', {}, mtext(h('div', { class: 'l1' }), label), h('div', { class: 'l2' }, x.kind ? h('span', { text: KIND[x.kind] ? KIND[x.kind].text : cap(x.kind) }) : null, x.skill && x.skill !== label ? h('span', { text: x.skill }) : null))));
        if (x.key) {
          const xb = h('button', { type: 'button', class: 'x', 'aria-label': `Drop: ${label}` }, UI.icon('x', 18));
          xb.addEventListener('click', () => {
            const was = drop.has(x.key);
            if (was) drop.delete(x.key); else drop.add(x.key);
            li.toggleAttribute('data-dropped', !was);
            xb.replaceChildren(UI.icon(was ? 'x' : 'again', 18));
            xb.setAttribute('aria-label', `${was ? 'Drop' : 'Put back'}: ${label}`);
            paintSum();
          });
          li.append(xb);
        }
        list.append(li);
      });
      paintSum();
      b.append(sum, list);
    }
    return sheet;
  }

  /* ------------------------------------------------------------ notes pinned atop the Due and Redo lists (V2, V18, V19) */
  let notesToken = 0;
  async function paintNotes() {
    const box = $('notes');
    const c = S.counts;
    const my = ++notesToken;
    if (!c) { box.replaceChildren(); return; }
    const out = [];
    if (c.new > 0) {
      const txt = h('span', { text: `${plural(c.new, 'new miss', 'new misses')}` });
      const go = h('button', { type: 'button', class: 'quiet', title: `Name each mistake, then prove it on ${rw() ? 'another one' : 'new numbers'}`, text: 'Walk them' });
      go.addEventListener('click', () => walk({ new: true, subject: S.subject }, go));
      out.push(h('p', { class: 'rh-line', 'aria-label': 'New misses' }, h('span', { class: 'dot', 'aria-hidden': 'true' }), txt,
        h('span', { class: 'meta', text: `about ${Math.max(1, Math.round(c.new * 1.5))} min` }), go));
      // where they came from: one sitting reads "from Section · Sep 21"
      UI.api(sub('/review/redo?lens=new&sort=recent&limit=100'), { quiet: true }).then(r => {
        if (my !== notesToken) return;
        const ss_ = new Map();
        (r.items || []).forEach(x => { if (x.session && !ss_.has(x.session)) ss_.set(x.session, x); });
        if (ss_.size === 1) { const x = [...ss_.values()][0]; txt.textContent = `${plural(c.new, 'new miss', 'new misses')} from ${srcWord(x.source)} · ${day(x.last)}`; }
        else if (ss_.size > 1) txt.textContent = `${plural(c.new, 'new miss', 'new misses')} from ${ss_.size} sittings`;
      }).catch(() => {});
    }
    if (c.worksheets_waiting > 0) {
      const line = h('p', { class: 'rh-line' }, h('span', { class: 'dot', 'aria-hidden': 'true' }), h('span', { text: `${plural(c.worksheets_waiting, 'worksheet')} waiting for answers` }));
      const a = h('a', { class: 'btn sm', href: '/practice/', text: 'Enter answers' });
      line.append(a);
      out.push(line);
      UI.api('/drill', { quiet: true }).then(r => {
        const w = (r.active || []).find(x => (x.source || (x.cfg && x.cfg.source)) === 'worksheet');
        if (w && w.id) a.href = S.wsHref = `/review/sheet/?id=${encodeURIComponent(w.id)}`;
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
      if (d.left > 0) return { v: `${fmtN(d.left)}/${fmtN(d.total)}`, sub: d.left_minutes ? `about ${d.left_minutes} min left today` : '' };
      if (d.total > 0) return { v: '✓', sub: 'Done for today' };
      return { v: '', sub: 'Nothing due' };
    }
    if (!S.counts) return { v: null, sub: '' };
    if (id === 'redo') {
      return { v: c.open || '', sub: bits([c.half && `${fmtN(c.half)} half fixed`, c.relapsed && `${fmtN(c.relapsed)} relapsed`, c.stake_total && `≈ ${fmtN(c.stake_total)} ${ptsW(c.stake_total)} at stake`]) };
    }
    if (id === 'marked') return { v: c.marked || '', sub: bits([c.marked_right && `${fmtN(c.marked_right)} right`]) };
    if (id === 'saved') return { v: c.saved || '', sub: bits([c.noted && `${fmtN(c.noted)} with notes`, c.saved_unanswered && `${fmtN(c.saved_unanswered)} not answered`]) };
    if (id === 'history') return { v: c.answers || '', sub: '' };
    if (id === 'fixed') return { v: c.fixed || '', sub: bits([c.held && `${fmtN(c.held)} held a check-in`]) };
    return { v: '', sub: '' };
  }
  // the tab row: UI.tabs in #rhtabs (arrows, Home, End; one amber underline slides to the open tab), label and count
  // inline (a phone stacks a short label over the count); each tab's sub-line is its title, the open one's leads its list head.
  // openTab owns the URL and the panel (one #panel for every tab), so UI.tabs gets neither param nor panel.
  let T = null;
  function paintTabs() {
    if (!T) {
      const want = Q().get('tab');
      T = UI.tabs($('rhtabs'), TABS.map(t => ({ id: t.id, label: t.k, tabId: `tab-${t.id}` })),
        { value: TABS.some(t => t.id === want) ? want : TABS[0].id, label: 'Review lists', onChange: id => openTab(id, { push: true }) });
      TABS.forEach(t => {
        const b = $(`tab-${t.id}`);
        b.classList.add('rh-tab');
        b.dataset.tab = t.id;
        b.setAttribute('aria-controls', 'panel');
        b.querySelector('span:not(.n)').replaceChildren(h('span', { class: 'rh-tk', text: t.k }), h('span', { class: 'rh-ts', text: t.short }));
      });
      // a click on the open tab reloads it, as it always did (UI.tabs ignores it); capture runs before its own click
      T.el.addEventListener('click', e => { const b = e.target.closest('[role="tab"]'); if (b && b.getAttribute('aria-selected') === 'true') openTab(b.dataset.tab, { push: false }); }, true);
      if (UI.edgeFade) UI.edgeFade(T.el, true);
    }
    if (S.tab && T.value !== S.tab) T.set(S.tab, true);   // only on a change: a set() mid-slide would stop the slide
    const fresh = (S.counts && S.counts.new) || 0;
    TABS.forEach(t => {
      const b = $(`tab-${t.id}`);
      const x = tileData(t.id);
      // History's lifetime figure asks for nothing: it stays in the aria-label only
      // a roll still running holds its target in .roll-t (the overlay digits would garble textContent)
      const n = b.querySelector('.n'), was = n.hidden ? '' : (n.querySelector('.roll-t') || n).textContent;
      const v = t.id === 'history' || x.v === '' ? null : x.v === null ? '–' : x.v;
      T.count(t.id, v);
      // Due done for today: a check, not a glyph; a count that changes (a fix, a snooze) rolls to its new figure
      if (v === '✓') n.replaceChildren(UI.icon('check', 14));
      else if (v !== null && /\d/.test(was) && n.textContent !== was) { n.textContent = was; UI.roll(n, v); }
      b.title = x.sub || '';
      const unread = t.id === 'redo' && fresh > 0;
      b.toggleAttribute('data-new', unread);   // index.html: an unread dot while new misses wait
      b.setAttribute('aria-label', `${t.k}${x.v !== '' && x.v !== null ? `, ${x.v === '✓' ? 'done' : x.v}` : ''}${unread ? `, ${fmtN(fresh)} new` : ''}${x.sub ? `, ${x.sub}` : ''}`);
    });
  }

  /* ------------------------------------------------------------ tabs */
  function openTab(id, o = {}) {
    const was = S.tab;
    $('main').classList.add('rh-ready');   // index.html: from here the open tab shows as open
    if (was && was !== id) { S.filters[was] = currentFilterValues(); }
    S.tab = id;
    $('main').dataset.tab = id;   // index.html: the pinned notes show on Due and Redo only
    const u = new URL(location.href);
    const keep = new URLSearchParams();
    keep.set('tab', id);
    keep.set('subject', S.subject);   // links and reloads open the same subject
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
    if (!S.ledger) { const s = S.subject; UI.api(sub('/review/ledger?weeks=12'), { quiet: true }).then(l => { if (s !== S.subject) return; S.ledger = l; paintTabs(); if (S.tab === 'fixed') paintHead(); }).catch(() => {}); }
  }

  /* ------------------------------------------------------------ filters (UI.filterBar, URL state) */
  let FB = null;
  function topicGroups() {
    if (rw()) return UI.RW_DOMAINS.map(d => ({ label: d.name, options: d.skills.map(s => ({ value: s, label: tname(s) })) }));
    return (UI.DOMAINS || []).map(([d, ds]) => ({ label: ds, options: (UI.TOPICS || []).filter(t => t.domain === d).map(t => ({ value: t.slug, label: t.short })) }))
      .filter(g => g.options.length);
  }
  const DATE = { key: 'date', label: 'Date', type: 'date' };
  function filterDefs(tab) {
    const common = [
      { key: 'topics', label: rw() ? 'Skill' : 'Topic', type: 'multi', groups: topicGroups() },
      // chips in the Filters sheet, orange while pressed; a set tier shows as a token in the list head
      { key: 'difficulty', label: 'Difficulty', type: 'pills', options: [{ value: 'easy', label: 'Easy' }, { value: 'medium', label: 'Medium' }, { value: 'hard', label: 'Hard' }] },
      rw() ? null : { key: 'fmt', label: 'Format', type: 'select', all: 'Any format', options: [{ value: 'mcq', label: 'Multiple choice' }, { value: 'spr', label: 'Grid-in' }] },
    ].filter(Boolean);   // R&W is all multiple choice: no Format
    const c = S.counts || {};
    const search = { key: 'q', label: 'Search', type: 'search', placeholder: tab === 'redo' ? 'Search mistakes' : 'Search questions' };
    const source = { key: 'source', label: 'Source', type: 'select', all: 'Any source', options: ['practice', 'due', 'section', 'module', 'diagnostic', 'challenge', 'qotd', 'review', 'shared', 'worksheet'].map(v => ({ value: v, label: srcWord(v) })) };
    const conf = { key: 'conf', label: 'Confidence', type: 'select', all: 'Any', options: [{ value: 'sure', label: 'Sure' }, { value: 'unsure', label: 'Unsure' }, { value: 'guess', label: 'Guess' }, { value: 'untagged', label: 'Untagged' }] };
    if (tab === 'redo') {
      const pts = c.stake_total !== null && c.stake_total !== undefined;
      return [
        ...common,
        { key: 'kind', label: 'Kind', type: 'select', all: 'Any kind', options: [{ value: 'misconception', label: 'Misconception' }, rw() ? null : { value: 'gridin', label: 'Grid-in' }, { value: 'slip', label: 'Slip' }, { value: 'unsure', label: 'Unsure' }].filter(Boolean) },
        { key: 'status', label: 'Status', type: 'select', all: 'Any status', options: [{ value: 'new', label: 'New', n: c.new || null }, { value: 'blind', label: 'Blind spots · sure and wrong', n: c.blind || null },
          { value: 'open', label: 'Open' }, { value: 'half', label: 'Half fixed', n: c.half || null }, { value: 'relapsed', label: 'Relapsed', n: c.relapsed || null }, { value: 'stuck', label: 'Stuck', n: c.stuck || null }] },
        { key: 'cause', label: 'Cause', type: 'select', all: 'Any cause', options: CAUSES.filter(([v]) => !(rw() && v === 'entry')).map(([v, l]) => ({ value: v, label: l })) },
        conf,
        { key: 'sort', label: 'Sort', type: 'sort', options: [...(pts ? [{ value: 'worth', label: 'Most points' }] : []), { value: 'recent', label: 'Most recent' }, { value: 'blind', label: 'Blind spots first' },
          { value: 'hits', label: 'Most missed' }, { value: 'near', label: 'Closest to fixed' }, { value: 'oldest', label: 'Oldest' }, { value: 'topic', label: rw() ? 'Skill order' : 'Topic order' }] },
        // habits are Math's; an R&W type holds one open mistake (named by the type), so grouping by it adds nothing
        { key: 'group', label: 'Group by', type: 'sort', options: rw() ? [{ value: 'topic', label: 'Skill' }, { value: 'domain', label: 'Domain' }, { value: 'none', label: 'None' }]
          : [{ value: 'topic', label: 'Topic' }, { value: 'domain', label: 'Domain' }, { value: 'habit', label: 'Habit' }, { value: 'norm', label: 'Mistake type' }, { value: 'none', label: 'None' }] },
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
    // Search and Sort (data-fkey, index.html) stay in the row; the rest sit behind "Filters · n", and each one set shows as a
    // token in the list head (paintListHead)
    FB = UI.filterBar(host, defs, { url: true, label: 'Filter this list', onChange: () => { if (S.tab !== 'due') loadList(S.tab, { glide: true }); } });
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
    p.set('subject', S.subject);
    return `/review/${tab}?${p}`;
  }

  /* ------------------------------------------------------------ loading a list */
  async function loadList(tab, o = {}) {
    const L = S.lists[tab] || (S.lists[tab] = { items: [], total: 0, next: null, data: null });
    const my = ++S.token;
    // a filter or sort change keeps the rows (dimmed) until the new list lands, then glides them; else the skeleton
    const glide = o.glide && L.data && $('list').querySelector('.rh-row');
    if (glide) $('list').setAttribute('aria-busy', 'true');
    else if (!o.more && !o.quiet) paintSkeleton();
    try {
      const [d, saved] = await Promise.all([UI.api(listPath(tab, o.more ? L.next : null)), PIN.includes(tab) ? savedSet() : null]);
      if (my !== S.token || S.tab !== tab) return;
      L.items = o.more ? L.items.concat(d.items || []) : (d.items || []);
      L.total = d.total ?? L.items.length;
      L.next = d.next ?? null;
      if (!o.more) L.data = d; else if (d.sittings) L.data.sittings = (L.data.sittings || []).concat(d.sittings.filter(s => !(L.data.sittings || []).some(x => x.session === s.session)));
      if (tab === 'fixed') clientFixed(L);
      if (tab === 'saved') clientSaved(L);
      if (saved) pinSaved(L, saved, tab !== 'marked');
      L.err = false;
    } catch (e) {
      if (my !== S.token || S.tab !== tab) return;
      L.err = true;
      if (!L.data) { const box = $('list'); box.replaceChildren(); box.removeAttribute('aria-busy'); UI.cardError(box, () => loadList(tab), 'This list didn’t load.'); return; }
      toast('Couldn’t refresh the list.');
    }
    paintListHead();
    if (glide) glideRows(paintList); else paintList();
    // a tab's first list fades in over its placeholder (no shimmer); a key-driven switch is instant (UI.motion)
    if (!glide && !o.quiet && !o.more && UI.motion) UI.motion.enter($('list'), 'fade');
    syncPane(); paintBar();
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
  // saved first (a pinned list): rows whose question you saved lead Redo and Fixed (inside each Redo group) and each
  // Marked sitting, in the list's own order, so its sort and filters still apply and nothing is hidden. History stays a
  // log, Due keeps the order it serves, Saved is all saved. The list head counts them; each carries a Saved tag.
  const PIN = ['redo', 'fixed', 'marked'];
  let savedP = null;
  // ponytail: the newest 100 saved questions (the endpoint's page cap); older ones are not pinned, never hidden
  const savedSet = () => (!(S.counts && S.counts.saved) ? Promise.resolve(new Set()) : savedP || (savedP = UI.api(sub('/review/saved?limit=100'), { quiet: true })
    .then(d => new Set((d.items || []).map(r => `${r.template}:${r.seed}`)), () => { savedP = null; return new Set(); })));
  function pinSaved(L, set, lead) {
    L.items.forEach(r => { r._saved = set.has(`${r.template}:${r.seed}`); });
    if (lead) L.items = [...L.items.filter(r => r._saved), ...L.items.filter(r => !r._saved)];
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

  // the list glides (a filter, a sort, a row that leaves): UI.glide over every row by its data-key, group sections
  // included (rows that stay slide, new ones nudge in, rows that left fade where they stood; keys and reduced motion instant)
  function glideRows(paint) { return UI.glide($('list'), paint, { rows: '.rh-row[data-key]' }); }
  function paintSkeleton() {
    const box = $('list');
    box.setAttribute('aria-busy', 'true');
    box.replaceChildren();
    const sk = h('div', { class: 'rh-skel' });
    if (UI.skel) UI.skel(sk, 'rows:6'); else sk.textContent = 'Loading…';
    box.append(sk);
  }

  /* ------------------------------------------------------------ the list head: select all, the tab's figures, set filters, More */
  // the selection differs from the tab's default: every row shows its box (index.html .rh-selmode)
  const selChanged = tab => { const s = sel(tab); return s.ids.size > 0 || s.all !== selDefaultAll(tab); };
  function paintListHead() {
    const host = $('listhead');
    host.replaceChildren();
    const tab = S.tab;
    if (!tab) return;
    $('main').classList.toggle('rh-selmode', tab !== 'due' && selChanged(tab));
    // the open tab's figures lead its list ("≈ 140 pts at stake", "about 12 min left today"); the tab's tooltip keeps them all
    const c = S.counts || {};
    const sub = tab === 'redo' && c.stake_total ? `≈ ${fmtN(c.stake_total)} ${ptsW(c.stake_total)} at stake` : tileData(tab).sub;
    if (tab === 'due') {
      host.hidden = !(S.due && (S.due.items || []).length && sub);
      if (!host.hidden) host.append(h('span', { class: 'rh-lh-m', text: sub }));
      return;
    }
    const L = S.lists[tab];
    if (!L || !L.data || !L.total) { host.hidden = true; return; }
    host.hidden = false;
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
    const whole = { redo: c.open, marked: c.marked, saved: c.saved, history: c.answers, fixed: c.fixed }[tab];
    const pinned = PIN.includes(tab) ? L.items.filter(r => r._saved && !r._closed).length : 0;
    const lm = [activeFilters() && whole && L.total !== whole ? `${fmtN(L.total)} of ${fmtN(whole)} match` : sub || null, pinned ? `${fmtN(pinned)} saved${tab === 'marked' ? '' : ' first'}` : null].filter(Boolean);
    if (lm.length) host.append(h('span', { class: 'rh-lh-m', text: lm.join(' · ') }));
    if (secondaryActions(tab).length) {
      const more = h('button', { type: 'button', class: 'btn sm rh-lh-more', text: 'More' });
      UI.menu.bind(more, () => secondaryActions(tab), { label: 'More with these', align: 'end' });
      host.append(more);
    }
    const toks = filterTokens(tab);
    if (toks) host.append(toks);
    // the sticky group heads sit under the list head (index.html --rh-lh), which grows a line while tokens show
    requestAnimationFrame(() => { if (host.offsetHeight) $('main').style.setProperty('--rh-lh', `${host.offsetHeight}px`); });
  }
  // a set filter as a token ("Medium ×", "Half fixed ×"): its × clears that value; Clear clears them all (two or more)
  const DATE_WORD = { today: 'Today', 7: 'Last 7 days', 30: 'Last 30 days' };
  function filterTokens(tab) {
    if (!FB) return null;
    const v = currentFilterValues();
    const out = [];
    filterDefs(tab).forEach(f => {
      if (f.type === 'sort' || f.type === 'search') return;
      const x = v[f.key];
      const opts = f.groups ? f.groups.flatMap(g => g.options) : (f.options || []);
      const word = y => (f.type === 'date' ? DATE_WORD[y] || String(y).split('..').map(d => (d ? day(d) : '…')).join(' – ')
        : (opts.find(o => String(o.value) === String(y)) || {}).label || String(y));
      const tok = (y, next) => {
        const b = h('button', { type: 'button', class: 'btn sm', 'aria-label': `Remove filter ${f.label}: ${word(y)}` }, word(y), UI.icon('x', 14));
        b.addEventListener('click', () => FB.set(f.key, next));
        out.push(b);
      };
      if (Array.isArray(x)) x.forEach(y => tok(y, x.filter(z => z !== y)));
      else if (x !== '' && x !== null && x !== undefined) tok(x, '');
    });
    if (!out.length) return null;
    if (out.length > 1) out.push(h('button', { type: 'button', class: 'quiet', text: 'Clear', onclick: () => FB.clear() }));
    return h('div', { class: 'rh-toks', role: 'group', 'aria-label': 'Filters set' }, ...out);
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
      const more = h('button', { type: 'button', class: 'btn sm rh-more', text: `Load 50 more · ${fmtN(L.items.length)} of ${fmtN(L.total)}` });
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
      redo: c.answers ? 'Nothing open.' : 'Every wrong answer lands here, named by the mistake behind it.',
      marked: 'Flag a question in practice or a test and it waits here.',
      saved: 'Tap the bookmark on any question to keep it.',
      history: 'Every answer you give shows up here.',
      fixed: 'Fixed mistakes move here, and each comes back for a check-in.',
    }[tab];
    const host = h('div', { class: 'rh-empty' });
    box.append(host);
    const sample = tab === 'redo' && !c.answers ? exampleRow : tab === 'marked' ? () => sampleRow('marked') : tab === 'saved' ? () => sampleRow('saved') : null;
    const nothingOpen = tab === 'redo' && c.answers > 0;
    // UI.empty swaps in its START (Math's body) when answered is 0: R&W hands its own START, with the subject, and skips the swap
    const first = rw() ? Object.assign({}, UI.empty.START, { body: { source: 'start', subject: 'rw' } }) : UI.empty.START;
    UI.empty(host, {
      sample: sample ? sample() : null, text,
      // a secondary: the header's Start is this screen's primary
      action: nothingOpen ? { label: `Keep going · ${S.minutes || 10} min`, body: { source: 'next', box: S.minutes || 10, subject: S.subject }, primary: false } : (!c.answers ? first : null),
      answered: rw() ? 1 : c.answers || 0,
    });
    // a drawing where no sample row shows: all clear on Redo, first use on History and Fixed (never on a filtered empty)
    const art = nothingOpen ? 'clear' : !sample && (tab === 'history' || tab === 'fixed') ? 'start' : null;
    const em = host.querySelector('.empty');
    if (art && em) em.prepend(spotEl(art));
    if (sample && !rw()) fillExample(host);   // an R&W example would spend an unseen bank item: its sample stays as drawn
  }
  // UI.spotArt's svg string as a node
  function spotEl(kind) {
    const t = doc.createElement('template');
    t.innerHTML = (UI.spotArt && UI.spotArt(kind)) || '';
    return t.content.firstElementChild || '';
  }
  // V16: a sample row built from a real reserved item, tagged Example
  let exampleCache = null;
  function exampleRow() {
    const r = h('div', { class: 'rh-row' }, h('div', { class: 'rh-rb' }, h('span', { class: 'lead' }, UI.pips ? UI.pips(2, 2) : null),
      rw() ? h('div', {}, h('div', { class: 'l1', text: 'Blank completion, negated frame' }), h('div', { class: 'l2' }, h('span', { text: 'Words in Context' }), h('span', {}, tierBit('medium')), h('span', { text: 'picked C' })))
        : h('div', {}, h('div', { class: 'l1', text: 'Used the diameter where the radius was needed' }), h('div', { class: 'l2' }, h('span', { text: 'Circles' }), h('span', { text: 'Arc length' }), h('span', {}, tierBit('medium')), h('span', { text: 'picked C' })))));
    r.dataset.example = '';
    return r;
  }
  // Marked and Saved when empty: a dimmed row of what lands here (UI.empty tags it Example)
  function sampleRow(tab) {
    const marked = tab === 'marked';
    const lead = UI.cell ? UI.cell(marked ? 'incorrect' : 'correct', marked ? 7 : '', { static: true, size: 'sm', flag: marked || null, saved: !marked || null }) : null;
    return h('div', { class: 'rh-row' }, h('div', { class: 'rh-rb' }, h('span', { class: 'lead' }, lead),
      h('div', {}, h('div', { class: 'l1 stem', text: rw() ? 'Which choice completes the text with the most logical and precise word or phrase?' : 'If 3x + 5 = 20, what is the value of 6x?' }),
        h('div', { class: 'l2' }, h('span', { text: rw() ? 'Words in Context' : 'Linear equations' }), h('span', {}, tierBit('medium')), h('span', { text: marked ? 'Section · picked B' : 'saved today · due in 2 days' })))));
  }
  async function fillExample(host) {
    try {
      if (!exampleCache) exampleCache = await UI.api('/types/rr.partner/example', { quiet: true });
      const q = exampleCache.question || {};
      const i = (q.reasons || []).findIndex((x, j) => x && j !== q.answer_index);
      const row = host.querySelector('[data-example] .l1');
      if (row && i >= 0) { row.textContent = cap(q.reasons[i]); const l2 = host.querySelector('[data-example] .l2'); l2.replaceChildren(...[h('span', { text: (TOPIC(q.topic) || {}).short || q.topic_name || '' }), h('span', { text: cap(q.skill || '') }), TIER[q.difficulty] ? h('span', {}, tierBit(q.difficulty)) : null, h('span', { text: `picked ${LET[i]}` })].filter(Boolean)); }
    } catch (_) {}
  }

  function rowShell(tab, r, i, o = {}) {
    const key = keyOf(tab, r);
    const row = h('div', { class: 'rh-row' + (o.cls ? ' ' + o.cls : '') + (o.select === false ? ' nosel' : ''), role: 'listitem', 'data-i': String(i), 'data-key': key, 'data-saved': r._saved ? '' : null });
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
  // a row's status tags: the shared .badge (ink for the hard ones, plain for half-way and due, soft for the rest)
  // counts and statuses that are not alerts stay neutral (orange is the one thing to do and the selection)
  const BADGE = { ink: 'badge ink', amber: 'badge line', new: 'badge line', soft: 'badge line' };
  // a row's tags: badges as [text, look], or a node (the Saved bookmark)
  function tagsEl(list) {
    const t = h('span', { class: 'tags' });
    list.filter(Boolean).forEach(x => t.append(x instanceof Node ? x : h('span', { class: BADGE[x[1]] || 'badge soft', text: x[0] })));
    return t.children.length ? t : h('span');
  }
  // a saved question: the bookmark outline in soft ink (the row's label says "saved")
  const savedMark = () => { const s = UI.icon('bookmark', 16); if (s) { s.classList.add('rh-saved'); s.setAttribute('aria-label', 'Saved'); s.setAttribute('role', 'img'); s.removeAttribute('aria-hidden'); } return s || null; };
  // a row's actions: on a mouse they sit over the row's end while it is hovered or focused; on touch one ⋯ opens
  // them as a menu (index.html). Each menu item clicks its button, so both paths run the same code
  function rowActs(row, label, btns) {
    btns = btns.filter(Boolean);
    if (!btns.length) return null;
    const acts = h('div', { class: 'ract reveal' }, ...btns);
    const more = h('button', { type: 'button', class: 'ibtn rh-rmore', 'aria-haspopup': 'menu', 'aria-label': `Actions: ${label || ''}` }, UI.icon('more', 18));
    more.addEventListener('click', () => UI.menu(more, btns.map(b => ({ label: b.dataset.menu || b.textContent, onClick: () => b.click() })), { label: 'Actions', align: 'end' }));
    row.append(acts, more);
    return acts;
  }
  // each fact is one span (its dot is drawn before it); the tier bars sit in a span of their own, since .dbars::before is the bars
  const l2 = bits => { const el = h('div', { class: 'l2' }); bits.filter(Boolean).forEach(b => el.append(b instanceof Node ? (b.tagName === 'SPAN' && !b.classList.contains('dbars') ? b : h('span', {}, b)) : h('span', { text: b }))); return el; };

  /* Due (V1) */
  const KIND = {
    check: { text: 'Check-in' }, relapsed: { text: 'Relapsed', cls: 'ink' }, sure: { text: 'Blind spot', cls: 'ink' }, half: { text: 'Half fixed', cls: 'amber' },
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
      // the line the tab's sub-line used to carry; Start (Fix, or Keep going) is the way on
      box.append(h('div', { class: 'rh-empty' }, h('div', { class: 'empty' }, spotEl('clear'), h('p', { class: 'empty-text', text: 'Nothing due today.' }))));
      return;
    }
    const ol = h('div', { class: 'rh-list' });
    items.forEach((it, i) => {
      const { row, btn } = rowShell('due', it, i, { select: false, label: it.label, cls: 'has-x' });
      if (it.done) row.dataset.done = '';
      if (it.snoozed) row.dataset.snoozed = '';
      const lead = h('span', { class: 'lead', 'aria-hidden': 'true' }, it.done ? h('span', { class: 'tick' }, UI.icon('check', 18)) : it.owed ? UI.pips(it.owed, 2) : null);
      const k = KIND[it.kind] || { text: cap(it.kind) };
      // trimmed like Redo's: the tier and the points (right); the domain and the question type ride on the tooltip and label
      const where = [it.domain && dshort(it.domain), it.skill && it.skill !== it.label ? it.skill : null].filter(Boolean).join(' · ');
      const meta = l2([tierBit(it.tier), it.pts ? h('span', { class: 'pts', text: `≈ ${fmtN(it.pts)} ${ptsW(it.pts)}` }) : null]);
      meta.classList.add('trim');
      const main = h('div', {}, mtext(h('div', { class: 'l1' }), it.label || ''), meta,
        it.why ? h('div', { class: 'l3 why', text: it.why }) : null);
      btn.append(lead, main, tagsEl([it.kind === 'half' ? null : [k.text, k.cls]]));
      if (where) btn.title = where;
      btn.setAttribute('aria-label', `${k.text}: ${it.label}${where ? `, ${where}` : ''}${it.done ? ', done' : ''}${it.snoozed ? ', not today' : ''}`);
      const x = h('button', { type: 'button', class: it.snoozed ? 'x undo' : 'x reveal','aria-label': it.snoozed ? `Undo not today: ${it.label}` : `Not today: ${it.label}`, title: it.snoozed ? 'Undo' : 'Not today' }, it.snoozed ? 'Undo' : UI.icon('x', 18));
      if (it.snoozed) main.append(h('div', { class: 'l3', text: 'Not today' }));
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
      await UI.api(sub('/review/snooze'), { method: 'POST', body: undo ? { key: it.key, undo: true } : { key: it.key } });
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
    const rows = L.items.map((r, i) => [r, i]).filter(([r]) => !r._closed);   // a mistake fixed in the pane leaves (paneOn closed)
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
      const head = h('div', { class: 'rh-gh' }, h('label', { class: 'sel' }, cb));
      head.append(g === 'topic' && UI.glyph && !rw() ? UI.glyph(k) : h('span'));   // the glyphs are the Math topics'
      // the head reads "4 open · ≈ 24 pts"; the domain and the per-test figure ride on the title's tooltip
      const more = [g !== 'domain' && meta.domain ? dshort(meta.domain) : null, g === 'topic' && meta.per_test ? `≈ ${fmtN(Math.round(meta.per_test * 10) / 10)} a test` : null].filter(Boolean).join(' · ');
      const gt = h('div', { class: 'gt' }, h('span', { class: 't', text: meta.name, title: more || null }));
      head.append(gt);
      gt.append(h('span', { class: 'meta' }, [plural(meta.count, 'open', 'open'), meta.pts ? `≈ ${fmtN(meta.pts)} ${ptsW(meta.pts)}` : null].filter(Boolean).join(' · '), more ? h('span', { class: 'sr', text: ` · ${more}` }) : null));
      const act = h('span', { class: 'act' });
      if (g === 'habit' && k !== 'other') {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Drill this habit · 8' });
        b.addEventListener('click', () => start({ source: 'habit', habit: k, count: 8 }, b));
        act.append(b);
      } else {
        const ids = members.map(([r]) => r.id);
        const qn = members.reduce((s, [r]) => s + (r.owed || 0), 0);
        const b = h('button', { type: 'button', class: 'quiet', text: `Fix ${plural(qn, 'question')}` });
        b.addEventListener('click', () => start(redoBody({ ids }), b));
        act.append(b);
      }
      const fold = h('button', { type: 'button', class: 'quiet rh-gfold', 'aria-label': `Fold ${meta.name}`, 'aria-expanded': 'true' }, UI.icon('caret_down', 16));
      // the group closes and opens in height (UI.motion.grow); folding flips its state at the end of the close
      fold.addEventListener('click', () => {
        const open = !sec.hasAttribute('data-folded'), from = sec.offsetHeight;
        fold.setAttribute('aria-expanded', String(!open));
        if (UI.motion.kb()) sec.toggleAttribute('data-folded', open);   // keys are instant
        else if (open) UI.motion.grow(sec, from, { to: head.offsetHeight, then: () => sec.setAttribute('data-folded', '') });
        else { sec.removeAttribute('data-folded'); UI.motion.grow(sec, from); }
      });
      act.append(fold);
      head.append(act);
      if (meta.tell) head.append(h('span', { class: 'tell', text: meta.tell }));
      sec.append(head);
      members.forEach(([r, i]) => sec.append(redoRow(r, i, g)));
      box.append(sec);
    });
  }
  // a Redo row, trimmed: the title (New as an unread dot before it), one status badge (Blind spot, else Relapsed, Stuck,
  // Half fixed), and three facts: tier bars, the last date, the points as a figure on the right. Everything else (skill,
  // format, times missed, source, your pick, kind, cause, other types) is in the pane head and in the row's tooltip and label
  function redoRow(r, i, g) {
    const { row, btn } = rowShell('redo', r, i, { label: r.label });
    const of = (r.clean || 0) + (r.owed || 0) || (r.kind === 'unsure' ? 1 : 2);
    const pips = UI.pips ? UI.pips(r.owed, of) : null;
    if (pips) { pips.setAttribute('aria-label', `${of - r.owed} of ${of} correct answers`); pips.title = `${of - r.owed} of ${of} correct answers`; }
    const status = r.stuck ? 'stuck' : r.status;
    const badge = r.blind ? [r.blind_assumed ? 'Blind spot (assumed)' : 'Blind spot', 'ink']
      : status === 'relapsed' ? [`Relapsed${r.relapses > 1 ? ' ×' + r.relapses : ''}`, 'ink'] : status === 'stuck' ? ['Stuck', 'ink'] : null;   // half fixed: the pips say it
    const facts = [
      g !== 'topic' && g !== 'domain' && r.domain ? dshort(r.domain) : null,
      r.skill && r.skill !== r.label ? r.skill : null,
      r.fmt && !rw() ? (r.fmt === 'spr' ? 'Grid-in' : 'MC') : null,
      r.hits > 1 ? `missed ${r.hits}×` : null,
      r.source === 'outside' ? 'logged by you' : r.source ? srcWord(r.source) : null,
      r.given_label ? `picked ${r.given_label}` : null,
      r.dodged_elsewhere ? `avoided in ${plural(r.dodged_elsewhere, 'other type')}` : null,
      r.kind === 'gridin' ? 'grid-in entry' : r.kind === 'slip' ? 'slip' : r.kind === 'unsure' ? 'unsure' : null,
      r.kind === 'misconception' && r.cause && r.cause !== 'trap' && CAUSES.find(c => c[0] === r.cause) ? `cause: ${CAUSES.find(c => c[0] === r.cause)[1].toLowerCase()}` : null,
      r.elsewhere && r.elsewhere.length ? `a trap in ${plural(r.elsewhere.length, 'other type')} too` : null,
    ].filter(Boolean);
    const bits = [
      // a flat or habit list has no topic head over the row: its topic stays in sight
      g !== 'topic' && g !== 'domain' && r.topic ? tname(r.topic) || null : null,
      tierBit(r.difficulty),
      r.last ? `last ${day(r.last)}` : null,
      r.pts ? h('span', { class: 'pts', text: `≈ ${fmtN(r.pts)} ${ptsW(r.pts)}` }) : null,
    ];
    const meta = l2(bits);
    meta.classList.add('trim');
    const title = mtext(h('div', { class: 'l1' }), r.label || '');
    if (r.new) title.prepend(h('span', { class: 'dot', 'aria-hidden': 'true' }));
    btn.title = facts.join(' · ');
    btn.setAttribute('aria-label', [`${r.new ? 'New: ' : ''}${r.label || ''}`, badge ? badge[0] : status === 'half' ? 'Half fixed' : null, `${of - r.owed} of ${of} correct answers`, TIER[r.difficulty],
      r.last && `last ${day(r.last)}`, r.pts && `about ${fmtN(r.pts)} points`, ...facts, r._saved && 'saved', r.note && `your note: ${r.note}`].filter(Boolean).join(', '));
    btn.append(h('span', { class: 'lead' }, pips), h('div', {}, title, meta, r.note ? h('div', { class: 'l3 note', text: r.note }) : null), tagsEl([badge, r._saved ? savedMark() : null]));
    if (r.stuck) {
      const lb = UI.verb ? UI.verb('learn', { sm: true }) : h('button', { type: 'button', class: 'btn sm', text: 'Learn this type' });
      lb.dataset.menu = 'Learn this type';
      lb.addEventListener('click', () => start({ source: 'learn', templates: [r.template], example: true, count: 3 }, lb));
      rowActs(row, r.label, [lb]);
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
    for (const [sid, all] of by) {
      const members = [...all.filter(([r]) => r._saved), ...all.filter(([r]) => !r._saved)];   // saved first in each sitting
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
        const bits = [r.skill, tierBit(r.difficulty), rw() ? null : r.fmt === 'spr' ? 'Grid-in' : 'MC', r.ms ? `${mmss(r.ms)}${r.budget_ms ? ` · budget ${mmss(r.budget_ms)}` : ''}` : null, pickText(r)];
        const hist = r.session_kind && r.session_kind !== 'drill' && r.flagged_at_ms !== undefined ? [
          r.flagged_at_ms ? `flagged at ${mmss(r.flagged_at_ms)}` : null, r.visits > 1 ? `came back ${r.visits - 1}×` : null, r.changes ? `changed ${r.changes}×` : null] : [];
        btn.append(h('span', { class: 'lead' }, UI.cell ? UI.cell(st, r.n, { static: true, size: 'sm', flag: true }) : null),
          h('div', {}, mtext(h('div', { class: 'l1 stem' }), r.stem || ''), l2(bits), hist.some(Boolean) ? h('div', { class: 'l3', text: hist.filter(Boolean).join(' · ') }) : null),
          tagsEl([r.during === false ? ['flagged later', 'soft'] : null, r.visits === 1 && r.session_kind !== 'drill' ? ['Never came back', 'ink'] : null, r._saved ? savedMark() : null]));
        sec.append(row);
      });
      box.append(sec);
    }
  }

  /* Saved (V3) */
  function paintSaved(box, L) {
    const ol = h('div', { class: 'rh-list' });
    L.items.forEach((r, i) => {
      const { row, btn } = rowShell('saved', r, i, { label: r.stem, cls: 'tall' });
      const st = r.answered === false ? 'unanswered' : resultOf(r);
      const sched = S.prefs.saved_spaced === false ? null : r.learned ? 'Learned' : r.due ? 'due today' : r.next ? `next ${day(r.next)}` : null;
      const bits = [tname(r.topic) || r.name, r.skill, tierBit(r.difficulty), rw() ? null : r.fmt === 'spr' ? 'Grid-in' : 'MC', r.saved_at || r.at ? `saved ${day(r.saved_at || r.at)}` : null,
        r.answered === false ? 'not answered' : r.given_label ? `answered: ${r.correct ? 'Right' : 'Wrong'} (picked ${r.given_label})` : null,
        r.tries > 1 ? `${r.tries} tries` : null, sched, S.prefs.saved_spaced !== false && !r.learned && r.box !== undefined ? `box ${(r.box || 0) + 1} of 4` : null];
      btn.append(h('span', { class: 'lead' }, UI.cell ? UI.cell(st, '', { static: true, size: 'sm', saved: true }) : null),
        h('div', {}, mtext(h('div', { class: 'l1 stem' }), r.stem || ''), l2(bits), r.note ? h('div', { class: 'l3 note', text: r.note }) : null),
        tagsEl([r.why === 'trick' ? ['Nice trick'] : r.why === 'hard' ? ['Hard'] : null]));
      const noteB = h('button', { type: 'button', class: 'btn sm', text: r.note ? 'Edit note' : 'Note' });
      noteB.addEventListener('click', () => noteEditor(row, r, noteB));
      const unsave = h('button', { type: 'button', class: 'quiet', text: 'Unsave' });
      unsave.addEventListener('click', () => unsaveRows([r]));
      rowActs(row, r.stem, [noteB, unsave]);
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
    glideRows(paintList); paintListHead(); paintBar(); syncPane();   // the rows that left close their gap
    savedP = null;
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
    const time = r.ms ? h('span', { class: over ? 'over' : null, text: `${mmss(r.ms)}${r.budget_ms ? ` · budget ${mmss(r.budget_ms)}${over ? ', over' : ''}` : ''}` }) : null;
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
      const tg = h('button', { type: 'button', class: 'quiet', 'aria-expanded': 'false', text: `${r.tries.length} tries` });
      const list = h('div', { class: 'rh-tries', hidden: true }, ...r.tries.map((x, j) => h('span', { text: `#${j + 1} · ${x.given_label || x.given || '–'} · ${mmss(x.ms)} · ${x.correct ? 'Right' : 'Wrong'}${x.reason ? ' · ' + x.reason : ''}` })));
      tg.addEventListener('click', () => { const o = list.hidden; list.hidden = !o; tg.setAttribute('aria-expanded', String(o)); tg.textContent = o ? `Hide ${r.tries.length} tries` : `${r.tries.length} tries`; });
      rowActs(row, r.skill, [tg]);
      row.append(list);
    }
    return row;
  }
  function sittingCard(s, rows) {
    const card = h('section', { class: 'rh-sit', 'aria-label': `${srcWord(s.source || s.kind)} · ${day(s.at)}` });
    if (s.void) card.dataset.void = '';
    const hd = h('div', { class: 'rh-sit-h' });
    const topics = (s.topics || []).map(tname);
    const blanks = (s.blanks || []).length;
    const misses = (s.cells || []).filter(c => ['wrong', 'incorrect', 'rushed'].includes(c.result)).length;
    const asked = s.asked || (s.cells || []).length;
    hd.append(h('p', { class: 't' }, `${srcWord(s.source || s.kind)}${topics.length ? ' · ' + topics.slice(0, 3).join(', ') + (topics.length > 3 ? ` +${topics.length - 3}` : '') : ''}`,
      h('span', { class: 'meta', text: [day(s.at), `${fmtN(s.right || 0)} / ${fmtN(asked)}`, s.minutes ? (UI.dur ? UI.dur(Math.round(s.minutes)) : `${Math.round(s.minutes)} min`) : null, blanks ? `${blanks} blank` : null, s.void ? 'discarded' : null].filter(Boolean).join(' · ') })));
    if ((s.cells || []).length && UI.cell) {
      const cells = h('div', { class: 'cells', role: 'group', 'aria-label': 'Every question in this sitting' });
      s.cells.forEach(c => {
        const st = c.blank ? 'blank' : resultOf({ result: c.result, correct: c.result === 'right' });
        const b = UI.cell(st, c.n + 1 || c.n, { size: 'sm', flag: c.flagged || null, onClick: () => openSittingCell(s, c) });
        cells.append(b);
      });
      hd.append(cells);
    }
    if (!s.void) {
      const acts = h('div', { class: 'acts' });
      const types = new Set((s.cells || []).map(c => c.template).filter(Boolean)).size || asked;
      const re = h('button', { type: 'button', class: 'btn sm', title: `Same ${plural(types, 'type')}, ${rw() ? 'new passages' : 'new numbers'}`, text: 'Rematch' });
      re.addEventListener('click', () => start({ rematch: s.session }, re));
      acts.append(re);
      if (misses || blanks) {
        const w = h('button', { type: 'button', class: 'btn sm', title: `Name each, then prove it · about ${Math.max(1, Math.round((misses + blanks) * 1.5))} min`, text: `Walk ${plural(misses + blanks, 'miss', 'misses')}` });
        w.addEventListener('click', () => walk({ session: s.session }, w));
        acts.append(w);
      }
      if (misses) {
        const f = h('button', { type: 'button', class: 'btn sm', title: 'Until each is fixed', text: `Fix ${fmtN(misses)}` });
        f.addEventListener('click', () => start({ rematch: s.session, scope: 'misses', until_fixed: true }, f));
        const fm = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'More ways to fix', 'aria-haspopup': 'menu' }, UI.icon('caret_down', 16));
        fm.addEventListener('click', () => UI.menu(fm, [{ label: 'Fix the misses + slow rights', onClick: () => start({ rematch: s.session, scope: 'weak' }) }], { label: 'Fix' }));
        acts.append(h('span', { class: 'split-btn' }, f, fm));
      }
      if (blanks) {
        const b = h('button', { type: 'button', class: 'btn sm', title: 'New versions of the ones left blank', text: `Redo ${plural(blanks, 'blank')}` });
        b.addEventListener('click', () => start({ rematch: s.session, scope: 'blanks' }, b));
        acts.append(b);
      }
      const href = sittingHref(s.kind, s.session);
      if (href) acts.append(h('a', { class: 'quiet', href, text: s.kind === 'drill' ? 'Summary' : 'Report' }));
      const more = h('button', { type: 'button', class: 'ibtn', 'aria-label': 'More for this sitting', 'aria-haspopup': 'menu' }, UI.icon('more', 18));
      more.addEventListener('click', () => UI.menu(more, [
        { label: 'Same questions again', sub: 'Tests memory', onClick: () => start({ retake: s.session }) },
        { separator: true },
        { label: 'Discard this sitting’s answers…', onClick: () => discard(s) },
      ], { label: 'More' }));
      acts.append(more);
      hd.append(acts);
    } else {
      const r = h('button', { type: 'button', class: 'btn sm', text: 'Restore' });
      r.addEventListener('click', () => restore(s, r));
      hd.append(h('div', { class: 'acts' }, h('span', { class: 'meta', text: 'Not counted' }), r));
    }
    if ((s.children || []).length) {
      hd.append(h('p', { class: 'kids', text: `Rematched ×${s.children.length}${s.best !== undefined && s.best !== null ? ` · best ${fmtN(s.best)} / ${fmtN(asked)}` : ''}` }));
    }
    card.append(hd);
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
    if (held >= 3) return ['Held all 3'];
    return [`Held ${held === 1 ? '1 check' : held}${next ? ' · next ' + next : ''}`];
  }
  function paintFixed(box, L) {
    const ol = h('div', { class: 'rh-list' });
    L.items.forEach((r, i) => {
      const { row, btn } = rowShell('fixed', r, i, { label: r.label });
      // the badge names the state; its date ("first check Oct 22", "next Oct 30") joins the meta line (a long badge was clipped in the list column)
      const [stText, stCls] = checkState(r);
      const [stWord, ...stWhen] = stText.split(' · ');
      const proven = new Set(r.tiers_proven || []);
      const avail = (r.tiers_available || []).slice().sort((a, b) => TIERS.indexOf(a) - TIERS.indexOf(b));
      const provenEl = avail.length > 1 ? h('span', { class: 'proven', title: 'Proven at', 'aria-label': `Proven at ${avail.filter(t => proven.has(t)).map(t => TIER[t]).join(', ') || 'no level yet'}` },
        ...avail.map(t => h('span', {}, UI.dbars ? UI.dbars(t, { bare: true }) : TIER[t], proven.has(t) ? ' ✓' : ' ○'))) : null;
      const bits = [tname(r.topic) || r.name, r.closed ? `fixed ${day(r.closed)}` : null, r.days_to_fix !== undefined && r.days_to_fix !== null ? `took ${plural(r.days_to_fix, 'day')}` : null, stWhen.join(' · ') || null,
        r.hits > 1 ? `missed ${r.hits}×` : null, r.relapses ? `relapsed ${r.relapses}×` : null, provenEl];
      btn.append(h('span', { class: 'lead', 'aria-hidden': 'true' }, h('span', { class: 'tick' }, fixedState(r) === 'dismissed' ? '–' : UI.icon('check', 18))),
        h('div', {}, mtext(h('div', { class: 'l1' }), r.label || ''), l2(bits)), tagsEl([[stWord, stCls], r._saved ? savedMark() : null]));
      const acts = [];
      const up = avail.find(t => !proven.has(t) && TIERS.indexOf(t) > Math.max(...[...proven].map(x => TIERS.indexOf(x)), -1));
      if (up && fixedState(r) !== 'dismissed') {
        const b = h('button', { type: 'button', class: 'btn sm', text: `Prove it at ${TIER[up]}` });
        b.addEventListener('click', () => proveIt(r, up));
        acts.push(b);
      }
      if (fixedState(r) === 'dismissed') {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Reopen' });
        b.addEventListener('click', async () => { b.setAttribute('aria-busy', 'true'); try { await UI.api('/mistakes/reopen', { method: 'POST', body: { id: r.id } }); toast('Back in Redo'); refreshSoon(true); } catch (e) { b.removeAttribute('aria-busy'); toast(reasonOf(e)); } });
        acts.push(b);
      }
      rowActs(row, r.label, acts);
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
  // a tab's insights: one closed disclosure under the tools row, opened by the Insights button at the row's end (its title
  // and figures are the button's tooltip); the open state is remembered per tab; both hide while it is empty (index.html)
  const INS = 'satf.review.ins';
  function insights(title) {
    const tab = S.tab;
    const body = h('div', { class: 'card line rh-ins-b' });
    const d = h('details', { class: 'fold rh-ins', id: `rh-ins-${tab}`, 'aria-label': title }, h('summary', { class: 'fold-s', text: title }), body);
    const btn = h('button', { type: 'button', class: 'btn', 'aria-controls': d.id, 'aria-expanded': 'false', 'aria-label': 'Insights', title }, UI.icon('results', 18), h('span', { text: 'Insights' }));
    btn.addEventListener('click', () => { d.open = !d.open; });
    d.addEventListener('toggle', () => {
      btn.setAttribute('aria-expanded', String(d.open));
      const m = ls.get(INS, {}) || {}; m[tab] = d.open; ls.set(INS, m);
    });
    if ((ls.get(INS, {}) || {})[tab]) { d.open = true; btn.setAttribute('aria-expanded', 'true'); }
    $('insights').replaceChildren(d);
    $('insbtn').replaceChildren(btn);
    // the figures a summary line used to show ("Trap 5, Slip 3") now ride on the button's tooltip
    const meta = { set textContent(v) { btn.title = v ? `${title} · ${v}` : title; } };
    return { d, body, meta };
  }
  // one titled part of an insights card (hairlines between parts); fill() returning false drops it
  function part(host, title, fill) {
    const sec = h('section', { class: 'rh-part', 'aria-label': title || null });
    if (title) sec.append(h('h2', { class: 'rh-k', text: title }));
    const body = h('div');
    sec.append(body);
    host.append(sec);
    const run = async () => {
      body.replaceChildren();
      if (UI.skel) UI.skel(body, 'lines:2');
      try { const keep = await fill(body, sec); if (keep === false) sec.remove(); }
      catch (e) { body.replaceChildren(); UI.cardError(body, run, 'This part didn’t load.'); }
    };
    run();
    return sec;
  }
  function paintHead() {
    const host = $('tabhead');
    host.replaceChildren();
    $('insights').replaceChildren(); $('insbtn').replaceChildren();
    const tab = S.tab;
    $('main').classList.toggle('rh-rules', tab === 'saved' && S.savedView === 'rules');
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

  // Due: exam week (V19)
  function dueHead(host) {
    const d = S.due;
    if (!d) { if (S.dueErr) UI.cardError(host, () => loadDue().then(() => { paintHead(); afterDue(); }), 'Today’s review didn’t load.'); return; }
    const exam = S.me && ((S.me.profile && S.me.profile.exam_date) || S.me.exam_date);
    const soon = exam && (Date.parse(exam) - Date.now()) / 864e5 <= 7 && Date.parse(exam) >= Date.now() - 864e5;
    if (soon) examCard(host, exam);
  }

  // Redo: named rate, why you lose points, habits, worth the most (V2, V4, V6, V7), folded into Insights
  function redoHead(host) {
    const c = S.counts || {};
    if (!c.open) return;
    const ins = insights(rw() ? 'Why you lose points, worth the most' : 'Why you lose points, worth the most, habits');
    if (c.diag_n >= 5) ins.body.append(h('p', { class: 'rh-part rh-big' }, `You named your own mistake ${fmtN(c.diag_right)} of ${fmtN(c.diag_n)} times`));
    // every open mistake (the first 100), not a time window: the server sends no causes for Redo
    part(ins.body, 'Why you lose points · open mistakes', async body => {
      const d = await UI.api(sub('/review/redo?limit=100&sort=worth'), { quiet: true });
      let causes = d.causes || null;
      if (!causes && d.total <= (d.items || []).length) {
        causes = {};
        (d.items || []).forEach(x => { const k = x.kind === 'slip' ? 'slip' : x.cause || 'trap'; causes[k] = (causes[k] || 0) + 1; });
      }
      body.replaceChildren();
      // one cause alone says nothing the Redo count doesn't: the bar shows once there are two
      if (causes && Object.keys(causes).filter(k => causes[k]).length > 1 && UI.stackBar) {
        const segs = CAUSES.filter(([k]) => causes[k]).map(([k, l]) => ({ key: k, label: l, value: causes[k] }));
        ins.meta.textContent = segs.slice().sort((a, b) => b.value - a.value).slice(0, 3).map(x => `${x.label} ${fmtN(x.value)}`).join(', ');
        const fixRow = h('div', { class: 'rh-row2' });
        UI.stackBar(body, segs, { largest: true, legend: false, noun: 'misses', label: 'Why you lose points', onPick: seg => { if (FB) FB.set('cause', seg.key); causeFix(fixRow, seg.key); } });
        body.append(fixRow);
        const cur = currentFilterValues().cause;
        if (cur) causeFix(fixRow, cur);
      } else body.closest('section').remove();
      worth(ins.body, d);
    });
    if (rw()) return;   // habits and the Trap gauntlet are Math's (server/habits.py)
    part(ins.body, 'Habits', async body => {
      const d = await UI.api(sub('/review/redo?group=habit&limit=1'), { quiet: true });
      const gs = (d.groups || []).filter(g => g.key !== 'other' && g.count >= 2).sort((a, b) => (b.pts || 0) - (a.pts || 0) || b.count - a.count).slice(0, 3);
      if (!gs.length) return false;
      body.replaceChildren();
      const list = h('div', { class: 'rh-list-p' });
      gs.forEach(g => {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Drill this habit · 8' });
        b.addEventListener('click', () => start({ source: 'habit', habit: g.key, count: 8 }, b));
        list.append(h('div', { class: 'rh-row2' }, h('b', { text: g.name }), g.tell ? h('i', { class: 'rh-foot', text: g.tell }) : null,
          h('span', { class: 'rh-foot', text: [plural(g.count, 'miss', 'misses'), g.pts ? `≈ ${fmtN(g.pts)} ${ptsW(g.pts)}` : null].filter(Boolean).join(' · ') }), b));
      });
      const gaunt = h('button', { type: 'button', class: 'btn sm', text: 'Trap gauntlet · 10' });
      gaunt.addEventListener('click', () => start({ source: 'gauntlet', count: 10 }, gaunt));
      body.append(list, h('div', { class: 'rh-row2' }, gaunt));
    });
  }
  function causeFix(host, k) {
    host.replaceChildren();
    const b = (label, body) => { const x = h('button', { type: 'button', class: 'btn sm', text: label }); x.addEventListener('click', () => start(body, x)); return x; };
    const ids = selRows('redo').filter(r => (r.cause || 'trap') === k).map(r => r.id);
    const fixes = {
      // Spot the trap needs a named trap: R&W misses are named by their type only
      trap: [b('Fix these', redoBody({ ids: ids.length ? ids : null })), S.lists.redo && S.lists.redo.items[0] && !rw() ? spotBtn() : null],
      slip: [b('Careful set · 8', { pool: 'redo', ids: ids.length ? ids : null, count: 8, feedback: 'instant', source: 'mistakes' }), h('span', { class: 'rh-foot', text: 'You know these. Reread the last line before Check.' })],
      misread: [b('Read the ask', { pool: 'redo', ids: ids.length ? ids : null, count: 8, feedback: 'instant', source: 'mistakes' })],
      clock: [b('Speed drill · 8', { pool: 'redo', ids: ids.length ? ids : null, count: 8, timing: 'pace', source: 'sprint' })],
      entry: rw() ? [] : [b('Grid-in entry · 8', { formats: ['spr'], count: 8, source: 'mistakes' })],
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
    const sec = h('section', { class: 'rh-part', 'aria-label': 'Worth the most' }, h('h2', { class: 'rh-k', text: 'Worth the most' }));
    const chips = h('div', { class: 'rh-chips rh-worth' });
    top.forEach(x => {
      const b = h('button', { type: 'button', class: 'btn sm' }, h('span', { class: 'l', text: (x.label || '').length > 40 ? x.label.slice(0, 39) + '…' : x.label }), h('span', { class: 'n', text: `≈ ${fmtN(x.pts)} ${ptsW(x.pts)}` }));
      b.addEventListener('click', () => { const i = S.lists.redo ? S.lists.redo.items.findIndex(y => y.id === x.id) : -1; if (i >= 0) openRow(i); else openSingle({ template: x.template, seed: x.seed, trap: x }); });
      chips.append(b);
    });
    const sum = top.reduce((s, x) => s + (x.pts || 0), 0);
    const go = h('button', { type: 'button', class: 'btn sm', text: `Fix ${top.length} · about +${fmtN(sum)} ${ptsW(sum)}` });
    go.addEventListener('click', () => start(redoBody({ ids: top.map(x => x.id) }), go));
    sec.append(chips, h('div', { class: 'rh-row2' }, go));
    host.append(sec);
  }

  // Marked: your instincts (V5), folded into Insights
  function markedHead(host) {
    const c = S.counts || {};
    if (!c.answers) return;
    const ins = insights('Your instincts');
    const seg = UI.seg(null, [{ value: '30', label: '30 days' }, { value: '90', label: '90 days' }, { value: 'all', label: 'All' }], { value: S.sinceCal, label: 'Since', onChange: v => { S.sinceCal = v; paintHead(); } });
    ins.body.append(h('div', { class: 'rh-part rh-row2' }, seg.el));
    part(ins.body, null, async body => {
      const since = S.sinceCal === 'all' ? '' : new Date(Date.now() - (+S.sinceCal) * 864e5).toISOString().slice(0, 10);
      const d = await UI.api(sub(`/review/calibration${since ? `?since=${since}` : ''}`), { quiet: true });
      body.replaceChildren();
      const m = d.matrix || {};
      const total = ['sure', 'unsure', 'guess'].reduce((s, k) => s + ((m[k] || {}).right || 0) + ((m[k] || {}).wrong || 0), 0);
      const fl = d.flags || {};
      const ch = d.changes || {};
      if (!total && !fl.n && !ch.n) { body.append(h('p', { class: 'help', 'data-nofold': '', text: 'Tag how sure you are, and flag in tests: this shows what each is worth.' })); return; }
      const grid3 = h('div', { class: 'rh-grid3' });
      if (total) {
        const blind = (m.sure || {}).wrong || 0;
        const lucky = ((m.unsure || {}).right || 0) + ((m.guess || {}).right || 0);
        ins.meta.textContent = [blind ? `${fmtN(blind)} blind spots` : null, lucky ? `${fmtN(lucky)} lucky` : null].filter(Boolean).join(', ');
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
        const colA = h('div', { class: 'rh-list-p' }, h('p', { class: 'rh-big', text: [blind ? `Blind spots ${fmtN(blind)}: sure and wrong` : null, lucky ? `Lucky ${fmtN(lucky)}` : null].filter(Boolean).join(' · ') || 'Certainty' }), mx);
        if (m.untagged) colA.append(h('p', { class: 'rh-foot', text: `untagged ${fmtN(m.untagged)}` }));
        grid3.append(colA);
      }
      const colB = h('div', { class: 'rh-list-p' });
      (d.readings || []).forEach(t => colB.append(h('p', { text: t })));
      if (ch.n) {
        colB.append(h('p', {}, h('b', { text: `${plural(ch.n, 'answer change')}` }), ` · ${fmtN(ch.wr)} wrong to right · ${fmtN(ch.rw)} right to wrong${ch.ww ? ` · ${fmtN(ch.ww)} wrong to wrong` : ''}${ch.pts ? ` · net ${ch.net > 0 ? '+' : ''}${fmtN(ch.net)} ≈ ${ch.pts > 0 ? '+' : ''}${fmtN(ch.pts)} ${ptsW(ch.pts)}` : ''}`));
        if (ch.net) colB.append(h('p', { class: 'help', text: ch.net > 0 ? 'Your second looks pay: keep flagging and returning.' : 'Your first answer is usually better: change only for a new reason.' }));
      }
      if (colB.children.length) grid3.append(colB);
      if (fl.n) {
        const colC = h('div', { class: 'rh-list-p' }, h('p', {}, h('b', { text: `${fmtN(fl.n)} flagged` }), ` · ${fmtN(fl.revisited)} came back${fl.never ? ` · ${fmtN(fl.never)} never came back${fl.never_wrong ? ` (${fmtN(fl.never_wrong)} of them wrong)` : ''}` : ''}`));
        if (fl.misses) colC.append(h('p', { text: `Your flags caught ${fmtN(fl.caught)} of your ${fmtN(fl.misses)} test misses` }));
        const low = (fl.by_topic || []).filter(t => t.misses >= 3).sort((a, b) => a.caught / a.misses - b.caught / b.misses)[0];
        if (low) colC.append(h('p', { class: 'help', text: `${tname(low.topic)}: flags caught ${low.caught} of ${low.misses} misses. Flag more there.` }));
        grid3.append(colC);
      }
      body.append(grid3);
    });
  }
  function goHistory(params) {
    S.filters.history = Object.assign({}, params);
    openTab('history', { push: true });
  }

  // Saved: Questions · Your rules, and the deck cards (V3, V19)
  function savedHead(host) {
    const c = S.counts || {};
    const view = h('div', { class: 'rh-row2' });
    UI.seg(view, [{ value: 'questions', label: 'Questions' }, { value: 'rules', label: 'Your rules' }], { value: S.savedView, label: 'Show', onChange: v => {
      S.savedView = v;
      const u = new URL(location.href);
      if (v === 'rules') u.searchParams.set('view', 'rules'); else u.searchParams.delete('view');
      history.replaceState(history.state, '', u);
      paintHead();
    } });
    host.append(view);
    if (S.savedView === 'rules') { rulesCard(host); return; }
    if (!c.saved) return;
    const cards = [{ value: 'all', label: 'All', n: null }];
    if (S.prefs.saved_spaced !== false) {
      if (c.saved_due) cards.push({ value: 'due', label: 'Due today', n: c.saved_due });
      if (c.learned) cards.push({ value: 'learned', label: 'Learned', n: c.learned });
    }
    if (!cards.some(x => x.value === S.savedCard)) S.savedCard = 'all';
    // the deck cards sit beside the view switch: one row of controls
    if (cards.length > 1) {
      UI.seg(view, cards, { value: S.savedCard, label: 'Show', onChange: v => { S.savedCard = v; const L = S.lists.saved; if (L && L.all) { L.items = L.all; L.total = L.data.total; clientSaved(L); paintListHead(); paintList(); syncPane(); paintBar(); } } });
    }
  }

  // V19: your SAT is days away: the trap sheet, and one fresh question per trap
  function examCard(host, exam) {
    const when = new Date(`${String(exam).slice(0, 10)}T12:00:00`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    const n = Math.min(10, (S.counts && S.counts.open) || 0);
    const line = h('p', { class: 'rh-line', 'aria-label': 'Exam week' }, h('span', { class: 'dot', 'aria-hidden': 'true' }), h('span', { text: `Your SAT is ${when}` }));
    if (n) {
      const go = h('button', { type: 'button', class: 'btn sm', title: 'One fresh question per trap, on the pace clock', text: `Final check · ${n} · about ${Math.max(1, Math.round((n * 95) / 60))} min` });
      go.addEventListener('click', async () => {
        go.setAttribute('aria-busy', 'true');
        try {
          const t = await UI.api(sub('/review/trapsheet'));
          const templates = [...new Set((t.entries || []).map(e => e.template))].slice(0, 10);
          if (!templates.length) throw new Error('none');
          start({ templates, count: templates.length, timing: 'pace', order: 'mixed', source: 'mistakes' }, go);
        } catch (_) { go.removeAttribute('aria-busy'); toast('The final check didn’t start. Try again.'); }
      });
      line.append(go);
    }
    line.append(h('a', { class: 'quiet', href: sub('/review/print.html?sheet=traps'), text: 'Your trap sheet' }));
    host.append(line);
  }

  // V19: Your rules (P21's store): the type's rule, its date, Try one, edit in place, Still useful?
  const RULE_MAX = 140;
  function rulesCard(host) {
    const kept = ls.get('satf.rules.kept', {}) || {};
    const card = h('section', { class: 'card line', 'aria-label': 'Your rules' });
    host.append(card);
    part(card, null, async body => {
      const b = await UI.api(sub('/bank'), { quiet: true });
      const rules = [];
      (b.domains || []).forEach(dm => (dm.skills || []).forEach(sk => (sk.types || []).forEach(t => {
        if (t.type_note) rules.push({ template: t.template, name: t.name || sk.name, note: t.type_note, at: t.type_note_at });
      })));
      rules.sort((x, y) => String(y.at || '').localeCompare(String(x.at || '')));
      if (!rules.length) {
        body.replaceChildren(h('p', { class: 'rh-foot', text: 'Write a rule after a miss (“Next time I will…”) and it waits here for test week.' }));
        return;
      }
      const list = h('div', { class: 'rh-rules-l', role: 'list' });
      rules.forEach(r => list.append(ruleRow(r, kept)));
      body.replaceChildren(list, h('p', { class: 'rh-row2' }, h('a', { class: 'btn sm', href: sub('/practice/?print=rules'), text: 'Print my rules' })));
    });
  }
  // a rule is written against one of your own answers of that type (the server never takes a template from the page)
  async function writeRule(template, note) {
    const f = await UI.api(`/review/family?template=${encodeURIComponent(template)}&limit=1`, { quiet: true });
    const a = (f.attempts || [])[0];
    if (!a) throw new Error('no answer of this type');
    await UI.api('/notes', { method: 'POST', body: { attempt_id: a.id, scope: 'type', note } });
  }
  function ruleRow(r, kept) {
    const row = h('div', { class: 'rh-rule', role: 'listitem' });
    const text = h('p', { class: 'rh-rule-t', text: r.note });
    const tryHost = h('div');
    const acts = h('div', { class: 'rh-row2' });
    const tryB = h('button', { type: 'button', class: 'btn sm', text: 'Try one' });
    tryB.addEventListener('click', () => {
      if (!UI.twinInline) return;
      tryHost.replaceChildren();
      UI.twinInline(tryHost, { body: { templates: [r.template], count: 1, source: 'review' }, caption: `Try one · ${r.name}`, session: false });
    });
    const editB = h('button', { type: 'button', class: 'quiet', text: 'Edit' });
    editB.addEventListener('click', () => {
      const ta = h('textarea', { class: 'field', rows: '2', maxlength: String(RULE_MAX), 'aria-label': `Your rule for ${r.name}` });
      ta.value = r.note;
      const cnt = UI.counter ? UI.counter(ta, RULE_MAX) : null;
      const box = h('div', { class: 'rh-rule-ed' }, ta, cnt);
      text.replaceWith(box);
      ta.focus();
      let done = false;
      const finish = async () => {
        if (done) return;
        done = true;
        const v = ta.value.trim();
        if (v && v !== r.note) {
          try { await writeRule(r.template, v); r.note = v; } catch (_) { toast('Not saved. Try again.'); }
        }
        text.textContent = r.note;
        box.replaceWith(text);
      };
      ta.addEventListener('blur', finish);
      ta.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ta.blur(); }
        if (e.key === 'Escape') { e.preventDefault(); ta.value = r.note; ta.blur(); }
      });
    });
    acts.append(tryB, editB);
    if (!kept[r.template]) {
      const ask = h('span', { class: 'rh-foot rh-rule-ask' }, 'Still useful? ');
      const keep = h('button', { type: 'button', class: 'quiet', text: 'Keep' });
      keep.addEventListener('click', () => { kept[r.template] = 1; ls.set('satf.rules.kept', kept); ask.remove(); });
      const rm = h('button', { type: 'button', class: 'quiet', text: 'Remove' });
      rm.addEventListener('click', async () => {
        const old = r.note;
        try { await writeRule(r.template, ''); } catch (_) { toast('Not removed. Try again.'); return; }
        row.remove();
        toast('Rule removed', { undo: () => writeRule(r.template, old).then(() => { if (S.tab === 'saved') paintHead(); }).catch(() => toast('Not restored.')) });
      });
      ask.append(keep, ' · ', rm);
      acts.append(ask);
    }
    row.append(h('p', { class: 'rh-rule-h' }, h('b', { text: r.name }), r.at ? h('span', { class: 'rh-foot', text: ` · ${day(r.at)}` }) : null), text, acts, tryHost);
    return row;
  }

  // History: one summary line (with the tier figures) and the rushed line stay; Right but slow folds into Insights (V8, V12);
  // Download CSV sits in the list head's More
  function historyHeadShell(host) { host.append(h('div', { id: 'histhead', class: 'rh-hh' })); }
  function historyHead() {
    const host = $('histhead');
    const L = S.lists.history;
    if (!host || !L || !L.data) return;
    host.replaceChildren();
    const s = L.data.summary;
    if (!s || !s.answers) return;
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
    const line = h('p', { class: 'rh-line', 'aria-label': 'These answers' });
    bits.forEach(b => { const el = b instanceof Node ? b : h('span', { text: b }); el.classList.add('rh-bit'); line.append(el); });
    const bd = s.by_difficulty || {};
    TIERS.forEach(t => {
      const v = bd[t];
      if (!v) return;
      const n = typeof v === 'object' ? v.n : v, r = typeof v === 'object' ? v.right : null;
      line.append(h('span', { class: 'badge line lg' }, tierBit(t), h('b', { text: r !== null && r !== undefined ? `${fmtN(r)} / ${fmtN(n)}` : fmtN(n) })));
    });
    host.append(line);
    if (s.rushed >= 3 && currentFilterValues().result !== 'rushed') {
      const see = h('button', { type: 'button', class: 'btn sm', text: 'See them' });
      see.addEventListener('click', () => FB && FB.set('result', 'rushed'));
      host.append(h('p', { class: 'rh-line' }, `${plural(s.rushed, 'miss', 'misses')} in under a quarter of the time: slow down on these`, see));
    }
    const pace = L.data.pace || [];
    if (pace.length) {
      const ins = insights('Right but slow');
      ins.meta.textContent = plural(Math.min(5, pace.length), 'type');
      const list = h('div', { class: 'rh-part rh-list-p' });
      pace.slice(0, 5).forEach(p => {
        const b = h('button', { type: 'button', class: 'btn sm', text: 'Speed drill · 8' });
        b.addEventListener('click', () => start({ templates: [p.template], count: 8, timing: 'pace', source: 'sprint' }, b));
        list.append(h('div', { class: 'rh-row2' }, h('b', { text: cap(p.skill || p.template) }),
          h('span', { class: 'rh-foot', text: [p.median_ms ? `your median ${mmss(p.median_ms)}` : null, p.budget_ms ? `budget ${mmss(p.budget_ms)}` : null, p.right !== undefined && p.n ? `right ${fmtN(p.right)} of ${fmtN(p.n)}` : p.accuracy !== undefined ? `right ${Math.round(p.accuracy * 100)}%` : null].filter(Boolean).join(' · ') }), b));
      });
      const sprint = h('button', { type: 'button', class: 'btn sm', text: `Fluency sprint · ${plural(Math.min(5, pace.length), 'type')}` });
      sprint.addEventListener('click', () => start({ templates: pace.slice(0, 5).map(p => p.template), count: 10, timing: 'pace', source: 'sprint' }, sprint));
      list.append(h('div', { class: 'rh-row2' }, sprint));
      ins.body.append(list);
    }
  }
  async function downloadCsv(btn) {
    if (btn) btn.setAttribute('aria-busy', 'true');
    try {
      const path = listPath('history', null).replace('/review/history?', '/api/review/history.csv?');
      const r = await fetch(path, { headers: { 'X-Learner': UI.learner(), 'X-Tz': String(new Date().getTimezoneOffset()) } });
      if (!r.ok) throw new Error();
      const url = URL.createObjectURL(await r.blob());
      const a = h('a', { href: url, download: `sat-freshman-answers-${new Date().toISOString().slice(0, 10)}.csv` });
      doc.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch (_) { toast('The download didn’t start. Try again.'); }
    if (btn) btn.removeAttribute('aria-busy');
  }

  // Fixed: the headline and the stat line stay; the week-by-week chart and the forecast fold into Insights (V9, V10, V4)
  function fixedHead(host) {
    const c = S.counts || {};
    if (!c.fixed && !(S.ledger && S.ledger.weeks && S.ledger.weeks.some(w => w.opened || w.fixed))) return;
    const l = S.ledger;
    if (!l) { if (UI.skel) UI.skel(host, 'line'); return; }
    const weeks = (l.weeks || []).slice(phone() ? -8 : -12);
    const withData = weeks.filter(w => w.opened || w.fixed);
    const cur = weeks[weeks.length - 1] || {};
    const net = (cur.fixed || 0) - (cur.opened || 0);
    if (withData.length < 2) {
      const made = weeks.reduce((s, w) => s + (w.opened || 0), 0), fixed = weeks.reduce((s, w) => s + (w.fixed || 0), 0);
      host.append(h('p', { class: 'rh-big', text: fixed ? `${fmtN(made)} made · ${fmtN(fixed)} fixed so far` : `${fmtN(made)} made so far` }));
    } else {
      host.append(h('p', { class: 'rh-big', text: `This week: fixed ${fmtN(cur.fixed || 0)}, made ${fmtN(cur.opened || 0)}, net ${net > 0 ? '−' : net < 0 ? '+' : ''}${fmtN(Math.abs(net))}${c.median_days !== null && c.median_days !== undefined ? ` · median ${plural(c.median_days, 'day')} to fix` : ''}` }));
    }
    const st = (S.lists.fixed && S.lists.fixed.data && S.lists.fixed.data.stats) || {};
    const bits = [c.unchecked && `${fmtN(c.unchecked)} not checked yet`, st.relapsed && (c.fixed ? `${fmtN(st.relapsed)} of ${fmtN(c.fixed)} relapsed` : `${fmtN(st.relapsed)} relapsed`),
      (st.recovered_month || c.recovered_month) && `recovered ≈ +${fmtN(st.recovered_month || c.recovered_month)} ${ptsW(st.recovered_month || c.recovered_month)} this month`, (st.dismissed || c.dismissed) && `${fmtN(st.dismissed || c.dismissed)} dismissed`].filter(Boolean);
    if (bits.length) host.append(h('p', { class: 'rh-foot', text: bits.join(' · ') }));
    const ins = insights('Made and fixed, week by week');
    if (withData.length >= 2 && UI.barChart) {
      const ch = h('div', { class: 'rh-part' });
      UI.barChart(ch, weeks.map(w => ({ key: w.week, label: day(w.week), fixed: w.fixed || 0, made: Math.max(0, (w.opened || 0) - (w.relapsed || 0)), relapsed: w.relapsed || 0, open: w.open_end || 0,
        tip: `${day(w.week)} week · ${fmtN(w.opened || 0)} made · ${fmtN(w.fixed || 0)} fixed · open ${fmtN(w.open_end || 0)}` })), {
        // a series only when it has something to draw: no "Fixed 0" or "Relapsed 0" in the legend (decision 7)
        series: weeks.some(w => w.fixed) ? [{ key: 'fixed', label: 'Fixed', look: 'amber' }] : [],
        down: [{ key: 'made', label: 'Made', look: 'ink' }, ...(weeks.some(w => w.relapsed) ? [{ key: 'relapsed', label: 'Relapsed', look: 'hatch' }] : [])],
        line: { key: 'open', label: 'Open' }, labels: 'label', height: phone() ? 150 : 180, legend: true, label: 'Mistakes made and fixed, week by week',
        onPick: row => { const d0 = row.key; const e = new Date(Date.parse(d0) + 6 * 864e5).toISOString().slice(0, 10); if (FB) FB.set('date', `${d0}..${e}`); } });
      ins.body.append(ch);
    }
    const f = l.forecast || {}, rate = l.rate || {};
    if (f.zero_on) {
      const exam = S.me && ((S.me.profile && S.me.profile.exam_date) || S.me.exam_date);
      const gap = exam ? Math.round((Date.parse(exam) - Date.parse(f.zero_on)) / 864e5) : null;
      ins.meta.textContent = `open mistakes reach 0 around ${day(f.zero_on)}${f.after_exam ? ', after your SAT' : ''}`;
      const fc = h('div', { class: 'rh-part' }, h('p', { text: `At this pace (${fmtN(Math.round(rate.fixed_week || 0))} fixed a week, ${fmtN(Math.round(rate.made_week || 0))} made) open mistakes reach 0 around ${day(f.zero_on)}${gap !== null && gap > 0 ? `, ${plural(gap, 'day')} before your SAT` : ''}.` }));
      if (f.after_exam && f.extra_minutes) fc.append(h('p', { class: 'rh-foot', text: `That’s after your SAT. About ${fmtN(f.extra_minutes)} more minutes a day clears them in time.` }));
      ins.body.append(fc);
    }
  }

  /* ------------------------------------------------------------ secondary actions: the list head's More menu */
  function secondaryActions(tab) {
    const rows = selRows(tab);
    const n = selCount(tab);
    const out = [];
    const it = (label, fn, sub) => ({ label, sub, onClick: () => fn(null) });
    if (tab === 'redo' && n) {
      out.push(it(`Walk these · ${fmtN(n)}`, b => walk({ ids: rows.map(r => r.id) }, b), `Name each, then prove it · about ${Math.max(1, Math.round(n * 1.5))} min`));
      const blind = rows.filter(r => r.blind);
      if (blind.length) out.push(it(`Drill my blind spots · ${fmtN(blind.length)}`, b => start({ pool: 'redo', ids: blind.map(r => r.id), level: 'as_missed', source: 'mistakes', feedback: 'instant' }, b)));
      out.push(it('Print worksheet', () => worksheet('redo', rows.map(r => r.id))));
      out.push(it(`Ask for help · ${fmtN(Math.min(n, 40))}`, () => askHelp(rows.slice(0, 40).map(r => [r.template, r.seed]))));
      out.push(it('Share', () => share(rows.slice(0, 40).map(r => [r.template, r.seed]))));
      out.push({ separator: true }, { label: 'Error log', sub: 'Every open mistake, to print', href: sub('/review/print.html?sheet=log') });
    }
    if (tab === 'marked') {
      const pick = n ? rows : (S.lists.marked || {}).items || [];
      const answered = pick.filter(r => r.answered).length;
      out.push(it('Same questions again', b => start(barBody('marked', true, pick.length), b), answered ? plural(answered, 'will be a repeat', 'will be repeats') : undefined));
      out.push(it('Share', () => share(pick.slice(0, 40).map(r => [r.template, r.seed]))));
      if (n) out.push({ separator: true }, it('Unmark', () => unmark(rows)));
    }
    if (tab === 'saved') {
      const pick = n ? rows : (S.lists.saved || {}).items || [];
      out.push(it('Same questions again', b => start(barBody('saved', true, pick.length), b)));
      out.push(it('Print worksheet', () => worksheet('saved', pick.map(r => [r.template, r.seed]))));
      out.push(it('Share', () => share(pick.slice(0, 40).map(r => [r.template, r.seed]))));
      if (n) out.push({ separator: true }, it('Unsave', () => unsaveRows(rows)));
    }
    if (tab === 'history' && n) {
      out.push(it('Same questions again', b => start(barBody('history', true, n), b)));
      out.push(it('Share', () => share(rows.slice(0, 40).map(r => [r.template, r.seed]))));
    }
    if (tab === 'history') out.push(...(out.length ? [{ separator: true }] : []), it('Download CSV', () => downloadCsv(null)));
    return out;
  }
  async function unmark(rows) {
    const L = S.lists.marked;
    const keys = new Set(rows.map(r => keyOf('marked', r)));
    const before = L.items;
    L.items = L.items.filter(r => !keys.has(keyOf('marked', r)));
    L.total = Math.max(0, L.total - rows.length);
    sel('marked').ids.clear(); saveSel('marked');
    glideRows(paintList); paintListHead(); paintBar(); syncPane();   // the rows that left close their gap
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
    const body = { pool, ids: ids.slice(0, 40), exact: false, each, feedback: 'end', source: 'worksheet', subject: S.subject };
    try {
      const d = await UI.api('/drill', { method: 'POST', body });
      const w = open(`/practice/session/?id=${encodeURIComponent(d.id)}&print=1`, '_blank');
      if (!w) { location.href = `/practice/session/?id=${encodeURIComponent(d.id)}&print=1`; return; }
      // V18: its answers go in here once the paper is done; Review's header keeps the same link while it waits
      toast('Worksheet made. Enter its answers when you’re done.', { action: { label: 'Enter answers', href: `/review/sheet/?id=${encodeURIComponent(d.id)}` }, ms: 8000 });
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
        b.append(h('p', { class: 'help', text: 'The link shows the question with answers hidden. After they try it, they see your pick.' }));
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
  // the set options (Questions, Clock, Feedback, Each, Level) sit behind Options: a popover, a sheet on a phone
  // the bar rises in when a selection first shows it and nudges out when the selection empties (its old content
  // stays, inert, while it leaves); repaints while it shows do not move it
  function paintBar() {
    const bar = $('actbar');
    if (bar._out) { bar._out = false; bar.inert = false; if (bar.getAnimations) bar.getAnimations().forEach(a => a.cancel()); }
    const old = [...bar.childNodes];
    bar.replaceChildren();
    paintBarIn(bar);
    if (!old.length && bar.firstChild && UI.motion) UI.motion.enter(bar, 'nudge');
    if (old.length && !bar.firstChild && UI.motion && !UI.motion.off()) {
      bar.replaceChildren(...old);
      bar._out = true; bar.inert = true;
      UI.motion.exit(bar, 'nudge').then(() => {
        if (!bar._out) return;
        bar._out = false; bar.inert = false; bar.replaceChildren();
        if (bar.getAnimations) bar.getAnimations().forEach(a => a.cancel());
        syncPrimary();
      });
      return;
    }
    syncPrimary();
  }
  function paintBarIn(bar) {
    const tab = S.tab;
    if (!tab || tab === 'due') return;
    const L = S.lists[tab];
    if (!L || !L.data || !L.total) return;
    const b = barState(tab);
    const n = selCount(tab);
    if (!n && (tab === 'redo' || tab === 'fixed' || tab === 'history')) return;
    const opts = h('div', { class: 'rh-opts', role: 'group', 'aria-label': 'Set options' });
    const opt = (k, ...el) => opts.append(h('div', { class: 'rh-opt' }, h('span', { class: 'k', text: k }), h('div', {}, ...el)));
    // Volume: 5 · 10 · 20 · 30 · 40 · 50 · All, and any count
    const volSeg = UI.seg(null, [5, 10, 20, 30, 40, 50, 0].map(v => ({ value: v, label: v ? String(v) : 'All' })), { value: b.volume || 0, label: 'How many', onChange: v => { b.volume = v || null; field.value = ''; paintSummary(); } });
    const field = h('input', { type: 'number', class: 'field sm', min: '1', max: '120', inputmode: 'numeric', 'aria-label': 'Or type how many', placeholder: '#' });
    if (b.volume && ![5, 10, 20, 30, 40, 50].includes(b.volume)) field.value = b.volume;
    field.addEventListener('input', () => { const v = Math.max(1, Math.min(120, parseInt(field.value, 10) || 0)); if (field.value) { b.volume = v; volSeg.set(-1, true); } else { b.volume = null; volSeg.set(0, true); } paintSummary(); });
    opt('Questions', volSeg.el, field);
    const clockSeg = UI.seg(null, [{ value: 'off', label: 'Off' }, { value: 'pace', label: 'Pace' }, { value: 'custom', label: 'Custom' }], { value: b.clock, label: 'Clock', onChange: v => { b.clock = v; mins.hidden = v !== 'custom'; paintSummary(); } });
    const mins = h('input', { type: 'number', class: 'field sm', min: '1', max: '180', value: String(b.minutes), 'aria-label': 'Minutes on the clock', hidden: b.clock !== 'custom' });
    mins.addEventListener('input', () => { b.minutes = Math.max(1, Math.min(180, parseInt(mins.value, 10) || 16)); paintSummary(); });
    opt('Clock', clockSeg.el, mins);
    if (tab === 'marked' || tab === 'saved' || tab === 'history') {
      opt('Feedback', UI.seg(null, [{ value: 'instant', label: 'Instant' }, { value: 'end', label: 'At the end' }], { value: b.feedback, label: 'Feedback', onChange: v => { b.feedback = v; paintSummary(); } }).el);
      opt('Each', UI.seg(null, [1, 2, 3].map(v => ({ value: v, label: `${v}` })), { value: b.each, label: 'New questions per type', onChange: v => { b.each = v; paintSummary(); } }).el);
    }
    if (tab === 'redo' || tab === 'fixed') {
      const lvl = UI.seg(null, [{ value: 'as_missed', label: 'As missed' }, { value: 'any', label: 'Any' }, { value: 'harder', label: 'Harder' }], { value: b.level, label: 'Level', onChange: v => { b.level = v; paintSummary(); } });
      opt('Level', lvl.el);
    }
    // one line: "23 selected · about 63 min" (a phone keeps "23 selected"); the set's full figures and the options set
    // away from their defaults head the Options popover, and Options counts them ("Options · 2", named in its tooltip)
    const sum = h('div', { class: 'rh-sum', role: 'status' });
    const acts = h('div', { class: 'rh-acts' });
    const ob = h('button', { type: 'button', class: 'quiet', 'aria-haspopup': 'dialog', text: 'Options' });
    ob.addEventListener('click', () => UI.pop(ob, opts, { label: 'Set options' }));
    const head = h('p', { class: 'rh-opt-h' });
    opts.prepend(head);
    function paintSummary() {
      const p = primaryFor(tab);
      const [first, ...rest] = String(p.short || p.summary).split(' · ');
      sum.replaceChildren(h('span', { class: 'rh-sum-l', title: p.summary }, first, rest.length ? h('span', { class: 'rh-sum-x', text: rest.join(' · ') }) : null));
      const echo = [b.clock === 'pace' ? 'pace clock' : b.clock === 'custom' ? `${b.minutes} min clock` : null,
        (tab === 'redo' || tab === 'fixed') && b.level !== 'as_missed' ? (b.level === 'harder' ? 'harder' : 'any level') : null,
        (tab === 'marked' || tab === 'saved' || tab === 'history') && b.feedback === 'end' ? 'answers at the end' : null,
        (tab === 'marked' || tab === 'saved' || tab === 'history') && b.each > 1 ? `${b.each} each` : null].filter(Boolean);
      head.replaceChildren(p.summary, ...(echo.length ? [h('small', { text: echo.join(' · ') })] : []));
      ob.textContent = echo.length ? `Options · ${echo.length}` : 'Options';
      if (echo.length) ob.title = echo.join(' · '); else ob.removeAttribute('title');
      if (b.err) sum.append(h('span', { class: 'err', text: b.err }));
      // with nothing selected the button selects; it starts nothing, so it is not the orange one
      const pb = h('button', { type: 'button', class: p.run ? 'btn' : 'pill', text: p.label });
      pb.addEventListener('click', async () => {
        if (p.run) return p.run();
        b.err = '';
        const e = await start(p.body, pb);
        if (e) { b.err = reasonOf(e); paintSummary(); }
      });
      acts.replaceChildren(ob, pb);
    }
    paintSummary();
    bar.append(sum, acts);
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
      // the count is questions (owed answers, capped by the set length), so it says so beside "N selected"
      return { label: `Fix · ${plural(q, 'question')}`, body: redoBody({ ids: idsFor('redo') }), short: `${fmtN(n)} selected · about ${mins(q)} min`,
        summary: `${fmtN(n)} selected · ${plural(types, 'question type')} · ${plural(q, 'question')} · about ${mins(q)} min${harder ? ` · ${harder} can’t go harder` : ''}` };
    }
    if (tab === 'fixed') {
      if (!n) return { label: `Select all ${fmtN(L.total)}`, summary: 'None selected', run: () => { const s = sel('fixed'); s.all = true; s.ids.clear(); saveSel('fixed'); paintList(); paintListHead(); paintBar(); } };
      const q = count(tab, new Set(rows.map(r => r.template)).size || n);
      return { label: `Check these now · ${fmtN(q)}`, body: barBody('fixed', false, q), short: `${fmtN(n)} selected · about ${mins(q)} min`, summary: `${fmtN(n)} selected · ${plural(q, 'question')} · one new one per type` };
    }
    if (tab === 'saved') {
      const c = S.counts || {};
      const due = (S.lists.saved.all || L.items).filter(r => r.due);
      if ((S.savedCard === 'due' || !n) && due.length && S.prefs.saved_spaced !== false) {
        const body = Object.assign({ pool: 'saved', ids: due.map(r => [r.template, r.seed]), exact: false, each: 1, source: 'map', feedback: b.feedback }, clockBody(tab));
        return { label: `Practise due · ${fmtN(due.length)}`, body, short: `${n ? `${fmtN(n)} selected` : `${fmtN(due.length)} due`} · about ${mins(due.length)} min`, summary: n ? `${fmtN(n)} selected · ${plural(due.length, 'due question')}` : `${plural(due.length, 'saved question')} due today` };
      }
      const k = n || L.total;
      const q = count(tab, k * b.each);
      return { label: 'Twin this set', body: barBody('saved', false, q), short: `${n ? `${fmtN(n)} selected` : `all ${fmtN(c.saved || L.total)}`} · about ${mins(q)} min`, summary: `${n ? `${fmtN(n)} selected` : `all ${fmtN(c.saved || L.total)}`} · ${plural(q, 'new question')} · about ${mins(q)} min` };
    }
    if (tab === 'marked') {
      const k = n || L.total;
      const q = count(tab, k * b.each);
      return { label: 'Twin this set', body: barBody('marked', false, q), short: `${n ? `${fmtN(n)} selected` : `all ${fmtN(L.total)}`} · about ${mins(q)} min`, summary: `${n ? `${fmtN(n)} selected` : `all ${fmtN(L.total)}`} · ${plural(q, 'new question')} · about ${mins(q)} min` };
    }
    if (tab === 'history') {
      if (!n) return { label: `Select all ${fmtN(Math.min(L.total, 120))}`, summary: 'Select answers to practise them again', run: () => { const s = sel('history'); s.all = true; s.ids.clear(); saveSel('history'); paintList(); paintListHead(); paintBar(); } };
      const types = new Set(rows.map(r => r.template)).size;
      const q = count(tab, types * b.each);
      return { label: 'Twin this set', body: barBody('history', false, q), short: `${fmtN(n)} selected · about ${mins(q)} min`, summary: `${fmtN(n)} selected · ${plural(types, 'question type')} · ${plural(q, 'new question')}${L.total > 120 && sel('history').all ? ' · first 120' : ''}` };
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
      const hst = await UI.api(sub(`/review/history?topics=${encodeURIComponent(r.topic)}&limit=1`), { quiet: true });
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
  const toItem = (d, r, tab) => window.ReviewItem.toItem(d, r, tab, stripOf(tab, r));
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
        savedP = null;   // the pins follow on the list's next load, not under the open row
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
      spot: rw() ? undefined : item => spot({ trap_id: item.trap_id, label: item.mistake && item.mistake.label }),   // no Spot for an unnamed R&W trap
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
      // the mistake closed in the pane: its row leaves, and the group head, list head and bar count it out at once. The
      // list is not refetched (the pane keeps showing the verdict; a refetch would move it to the next mistake)
      closed: (item, fb) => {
        dropCache(item);
        // beside the pane the reward lands in the pane and on the row (a live line says it, no toast); the phone's
        // dialog covers the list, so it keeps the toast, with a check
        const said = `Fixed: ${(item.mistake && item.mistake.label) || 'your mistake'}`;
        if (wide()) say(said); else toast(said, { icon: 'check' });
        const L = S.lists.redo, k = item && item._row;
        const r = tab === 'redo' && L && k && L.items.find(x => x === k || (x.id && x.id === k.id));   // never a single opened outside the list
        const at = r ? L.items.indexOf(r) : -1;
        if (r && !r._closed) {
          r._closed = true;
          L.total = Math.max(0, L.total - 1);
          sel('redo').ids.delete(keyOf('redo', r)); saveSel('redo');
          const g = currentFilterValues().group || 'topic';
          const meta = g !== 'none' && ((L.data && L.data.groups) || []).find(x => x.key === groupKey(r, g));
          if (meta) { meta.count = Math.max(0, (meta.count || 1) - 1); if (meta.pts && r.pts) meta.pts = Math.max(0, meta.pts - r.pts); }
          // the row glows amber and leaves (UI.fx.glow: its gap closes by glide); then the heads and the bar count it out
          const row = doc.querySelector(`#list .rh-row[data-i="${at}"]`);
          const after = () => {
            if (S.tab !== 'redo') return;
            glideRows(() => { if (L.items.some(x => !x._closed)) paintList(); });
            paintListHead(); paintBar();
          };
          // the open row already wears the amber tint: it steps out of the selected look so the glow shows
          if (row) { row.removeAttribute('aria-current'); UI.fx.glow(row).then(after); } else after();
        }
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
        b.append(h('p', { class: 'rh-big' }, 'Which choice comes from: ', h('i', { text: d.prompt || o.label || '' }), '?'));
        b.append(mtext(h('p', { class: 'q-stem rh-spot-q' }), q.stem || ''));
        const list = h('div', { class: 'rh-list-p rh-spot-c', role: 'group', 'aria-label': 'Choices' });
        const out = h('p', { class: 'help', role: 'status' });
        (q.choices || []).forEach((c, i) => {
          const btn = h('button', { type: 'button', class: 'btn' }, h('b', { text: `${LET[i]}  ` }), mtext(h('span'), c));
          btn.addEventListener('click', async () => {
            list.querySelectorAll('button').forEach(x => { x.disabled = true; });
            try {
              const r = await UI.api(`/review/spot/${encodeURIComponent(d.id)}`, { method: 'POST', body: { answer: i } });
              const ti = r.trap_index;
              list.querySelectorAll('button').forEach((x, j) => { if (j === ti) x.dataset.trap = ''; if (j === i && j !== ti) x.dataset.pick = ''; });
              out.textContent = r.correct ? `Yes: ${LET[ti]} is the trap.` : `Not quite: the trap is ${LET[ti]}.`;
              if (r.correct) UI.fx.check(out);   // a right pick: a check draws after the line
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
        'Shift+R': { does: 'Start review', run: () => { const b = $('start').querySelector('.rh-go'); if (b) b.click(); } },
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
