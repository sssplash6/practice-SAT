/* ============================================================================
   SAT Freshman -- a paper's sheet, #talk (spec 3.4 §2.7; tests.md X21, §3.1 items 4, 22, 73)

   TestsTalk.open(paper, {start(btn), tab: 'q' | 'd', about})   one 880px sheet, full height on a phone
     gated     nothing is sent before a finished sitting: the count and "Start Paper #8"
     Questions GET /api/papers/{n}/crowd: every slot with the crowd's result (this paper's
               first ranked sittings from 20, site-wide first tries before that, always
               labelled), the trap that caught most people, your cheapest points, sort and filters;
               a row expands to the spread, Try one like this, Discuss and Open my review
     Discussion GET/POST /api/papers/{n}/posts, Helpful, Reply (one level), Report,
               Edit and Delete for 15 minutes, the About filter and the composer
   Post and note text is always set with textContent (4.11).
   ========================================================================== */
(() => {
  const h = UI.h;
  const api = (p, o) => UI.api(p, o);
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  const num = n => (UI.num ? UI.num(n) : String(n));
  const plural = (n, one, many) => `${num(n)} ${n === 1 ? one : many || one + 's'}`;
  const pct = x => `${Math.round((x || 0) * 100)}%`;
  const mmss = ms => (ms === null || ms === undefined ? null : UI.mmss(Math.round(ms / 1000)));
  const SHORT = { m1: 'M1', m2u: 'M2 harder', m2l: 'M2 easier' };
  const MODULE = { m1: 'Module 1', m2u: 'Module 2 (harder)', m2l: 'Module 2 (easier)' };
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const slotName = slot => { const [m, i] = String(slot || '').split(':'); return `${SHORT[m] || String(m).toUpperCase()} Q${i}`; };
  const slotMod = slot => String(slot || '').split(':')[0];
  const btn = (label, o = {}) => {
    const b = h('button', { type: 'button', class: o.cls || 'quiet', text: label, 'aria-label': o.aria || null, 'aria-pressed': o.pressed === undefined ? null : String(!!o.pressed) });
    if (o.run) b.addEventListener('click', e => o.run(b, e));
    return b;
  };
  const report = (sid, q) => `/results/report/?id=${encodeURIComponent(sid)}${q ? `&q=${encodeURIComponent(q)}` : ''}`;

  function open(p, o = {}) {
    if (!UI.sheet) return null;
    return UI.sheet({ title: `Paper #${p.n}`, size: 'l', className: 'talk-sheet', label: `Paper #${p.n}: questions and discussion`,
      body: (b, sh) => { build(b, p, o, sh); } });
  }

  function build(b, p, o, sh) {
    const box = h('div', { class: 'tk-box', 'aria-busy': 'true' });
    b.append(box);
    if (UI.skel) UI.skel(box, 'rows:3');
    Promise.all([api(`/papers/${p.n}/crowd`, { quiet: true }), api(`/papers/${p.n}/posts?sort=top`, { quiet: true })]).then(([crowd, posts]) => {
      box.removeAttribute('aria-busy');
      box.replaceChildren();
      if (crowd.gated || posts.gated) return gated(box, p, o, crowd.count ?? posts.count ?? p.posts, sh);
      const sid = crowd.session || (p.yours || {}).last_session || null;
      const qPanel = h('div', { class: 'tk-panel' }), dPanel = h('div', { class: 'tk-panel' });
      const ctx = { p, sid, crowd, posts, qPanel, dPanel, sh, tabs: null, disc: null };
      ctx.tabs = UI.tabs(null, [{ id: 'q', label: 'Questions', panel: qPanel }, { id: 'd', label: 'Discussion', n: posts.count || 0, panel: dPanel }],
        { value: o.tab === 'd' ? 'd' : 'q', label: `Paper #${p.n}` });
      box.append(ctx.tabs.el, qPanel, dPanel);
      questions(ctx);
      ctx.disc = discussion(ctx, o.about || null);
    }).catch(() => {
      box.removeAttribute('aria-busy');
      box.replaceChildren();
      if (UI.cardError) UI.cardError(box, () => { box.remove(); build(b, p, o, sh); }, 'Couldn’t load this paper’s questions and discussion.');
    });
  }

  function gated(box, p, o, count, sh) {
    box.append(h('p', { class: 'tw-lead tk-gate', text: `Sit Paper #${p.n} first. The questions and discussion talk about its traps.` }));
    if (count) box.append(h('p', { class: 'meta', text: `Discussion · ${plural(count, 'post')}` }));
    box.append(h('div', {}, btn(`Start Paper #${p.n}`, { cls: 'pill', run: x => { if (o.start) o.start(x); } })));
    if (sh && sh.el) setTimeout(() => { const f = box.querySelector('.pill'); if (f) f.focus(); }, 0);
  }

  /* ---------------- Questions (X21) */
  const SORTS = {
    hard: (a, b) => (a.right ?? 2) - (b.right ?? 2),
    mine: (a, b) => mineRank(a) - mineRank(b) || a.order - b.order,
    crowd: (a, b) => beat(b, 'crowd') - beat(a, 'crowd') || a.order - b.order,
    you: (a, b) => beat(b, 'you') - beat(a, 'you') || a.order - b.order,
    order: (a, b) => a.order - b.order,
    talk: (a, b) => (b.posts || 0) - (a.posts || 0) || a.order - b.order,
  };
  const stateOf = r => (r.you ? r.you.state : null);
  function mineRank(r) { const s = stateOf(r); return s === 'wrong' ? 0 : s === 'blank' ? 1 : s === 'right' ? 2 : 3; }
  function beat(r, who) {
    const s = stateOf(r);
    if (r.right === null || r.right === undefined || !s) return -1;
    if (who === 'crowd') return s !== 'right' ? r.right : -1;          // most of them got it, you didn't
    return s === 'right' ? 1 - r.right : -1;                           // few got it, you did
  }
  function questions(ctx) {
    const { crowd, qPanel: host, sid } = ctx;
    const slots = (crowd.slots || []).map((s, i) => Object.assign({ order: i }, s));
    const own = crowd.source === 'paper';
    host.append(h('p', { class: 'meta tk-src', text: own ? `From ${plural(crowd.n_first, 'first sitting')}`
      : `Site-wide data for each type until this paper has 20 first sittings${crowd.n_first ? ` · ${num(crowd.n_first)} so far` : ''}` }));

    // the top blocks: the paper's traps, and your cheapest points
    const tops = h('div', { class: 'tk-tops' });
    if ((crowd.traps || []).length) {
      tops.append(h('section', { class: 'tk-top' }, h('h3', { class: 'k', text: 'Traps of this paper' }),
        h('ul', { class: 'tk-traps' }, crowd.traps.slice(0, 3).map(t => h('li', { text: t.label })))));
    }
    const cheap = crowd.cheapest || [];
    if (cheap.length) {
      const list = h('div', { class: 'tk-cheap' });
      cheap.forEach(c => list.append(btn(`${slotName(c.slot)} · ${pct(c.right)} right · ${c.source === 'paper' ? 'this paper' : 'site-wide'}`, {
        cls: 'btn sm', aria: `${slotName(c.slot)}: ${pct(c.right)} got it right; you ${c.you === 'blank' ? 'left it blank' : 'missed it'}`,
        run: () => openRow(c.slot) })));
      tops.append(h('section', { class: 'tk-top' }, h('h3', { class: 'k', text: `Your cheapest points: ${plural(cheap.length, 'question')} 80% or more got right` }), list));
    }
    if (tops.childNodes.length) host.append(tops);

    // sort and filters
    const bar = h('div', { class: 'tk-bar' });
    host.append(bar);
    const list = h('div', { class: 'tk-list' });
    host.append(list);
    const v = { sort: 'hard', mod: '', src: '' };
    const mods = [...new Set(slots.map(s => s.module))];
    UI.dropdown(bar, { label: 'Sort', value: 'hard', default: 'hard', noAll: true, sm: true,
      options: [['hard', 'Hardest for everyone'], ['mine', 'Your misses'], ['crowd', 'Where the crowd beat you'], ['you', 'Where you beat the crowd'], ['order', 'In order'], ['talk', 'Most discussed']].map(([value, label]) => ({ value, label })),
      onChange: x => { v.sort = x || 'hard'; paint(); } });
    UI.dropdown(bar, { label: 'Module', sm: true, options: mods.map(m => ({ value: m, label: MODULE[m] || m })), onChange: x => { v.mod = x || ''; paint(); } });
    if (slots.some(s => s.source === 'paper') && slots.some(s => s.source === 'site'))
      UI.dropdown(bar, { label: 'Source', sm: true, options: [{ value: 'paper', label: 'This paper' }, { value: 'site', label: 'Site-wide' }], onChange: x => { v.src = x || ''; paint(); } });

    const rowEls = new Map();
    function paint() {
      list.replaceChildren();
      rowEls.clear();
      const out = slots.filter(s => (!v.mod || s.module === v.mod) && (!v.src || s.source === v.src)).sort(SORTS[v.sort] || SORTS.hard);
      const on = out.filter(s => s.on_route !== false), off = out.filter(s => s.on_route === false);
      const group = (label, rows) => {
        if (!rows.length) return;
        if (label) list.append(h('h3', { class: 'k tk-group', text: `${label} · ${rows.length}` }));
        const ul = h('ul', { class: 'tk-rows' });
        rows.forEach(s => { const li = row(ctx, s, sid); rowEls.set(s.slot, li); ul.append(li); });
        list.append(ul);
      };
      group(null, on);
      group('Not on your route', off);
      if (!out.length) list.append(h('p', { class: 'help', text: 'No questions match these filters.' }));
    }
    function openRow(slot) {
      let li = rowEls.get(slot);
      if (!li) { v.mod = ''; v.src = ''; paint(); li = rowEls.get(slot); }
      if (!li) return;
      const t = li.querySelector('.tk-head');
      if (t && t.getAttribute('aria-expanded') !== 'true') t.click();
      li.scrollIntoView({ block: 'nearest' });
      if (t) t.focus();
    }
    paint();
  }

  function row(ctx, s, sid) {
    const li = h('li', { class: 'tk-row', 'data-slot': s.slot });
    const you = s.you || null;
    const glyph = !you ? null : you.state === 'right' ? ['✓', 'you got it', 'Right'] : you.state === 'wrong' ? ['✕', 'you missed it', 'Missed'] : ['–', 'you left it blank', 'Blank'];
    const rightText = s.right === null || s.right === undefined ? 'No answers on this type yet' : `${pct(s.right)} right`;
    const srcText = s.n ? `${num(s.n)} ${s.source === 'paper' ? (s.n === 1 ? 'first sitting' : 'first sittings') : 'answers site-wide'}` : '';
    const bar = s.right === null || s.right === undefined ? null : h('span', { class: 'tk-bar-r', 'aria-hidden': 'true' }, h('i', { style: `width:${Math.round(s.right * 100)}%` }));
    const head = h('button', { type: 'button', class: 'tk-head', 'aria-expanded': 'false' },
      h('span', { class: 'tk-slot', text: slotName(s.slot) }),
      h('span', { class: 'tk-topic' }, h('b', { text: s.topic_name || s.topic || '' }),
        h('span', { class: 'tk-tier' }, UI.dbars ? UI.dbars(s.tier) : h('span', { text: TIER[s.tier] || s.tier || '' }), s.fmt === 'spr' ? h('span', { text: '· grid-in' }) : null)),
      h('span', { class: 'tk-right' }, h('span', { class: 'tk-rt', text: rightText }), bar, srcText ? h('span', { class: 'meta', text: srcText }) : null),
      glyph ? h('span', { class: 'tk-you ' + you.state, 'aria-label': glyph[1] }, h('b', { 'aria-hidden': 'true', text: glyph[0] }), h('small', { 'aria-hidden': 'true', text: glyph[2] })) : h('span', { class: 'tk-you' }));
    li.append(head);
    const lines = h('div', { class: 'tk-lines' });
    const times = [s.median_right_ms ? `Median right ${mmss(s.median_right_ms)}` : null, you && you.ms ? `you ${mmss(you.ms)}` : null].filter(Boolean);
    if (times.length) lines.append(h('p', { class: 'meta', text: times.join(' · ').replace(/^you/, 'You') }));
    const top = (s.spread || [])[0];
    if (top) lines.append(h('p', { class: 'tk-trap', text: `${pct(top.share)} · ${top.label}` }));
    else if ((s.designed || []).length) lines.append(h('p', { class: 'tk-trap soft', text: `Built to catch: ${s.designed.slice(0, 2).join(' · ')}` }));
    if (s.posts) lines.append(h('p', { class: 'meta tk-post1' }, h('span', { text: plural(s.posts, 'post') }), s.top_post ? h('span', { text: ` · “${String(s.top_post).slice(0, 120)}”` }) : null));
    li.append(lines);
    const more = h('div', { class: 'tk-more', hidden: true });
    li.append(more);
    head.addEventListener('click', () => {
      const on = head.getAttribute('aria-expanded') !== 'true';
      head.setAttribute('aria-expanded', String(on));
      more.hidden = !on;
      if (on && !more.childNodes.length) expand(ctx, s, sid, more);
    });
    return li;
  }

  function expand(ctx, s, sid, host) {
    if (s.fmt === 'spr' && (s.spr_top || []).length && UI.spread) {
      UI.spread(host, s.spr_top.map(x => ({ label: x.value, text: `Answered ${x.value}`, share: x.share })), { n: s.n, label: `${slotName(s.slot)}: the top answers`, noun: 'answers' });
    } else if ((s.spread || []).length && UI.spread) {
      UI.spread(host, s.spread.map(x => ({ label: x.label, text: x.label, share: x.share, key: x.norm })), { n: s.n, label: `${slotName(s.slot)}: the wrong answers by mistake`, noun: 'answers' });
    } else if ((s.designed || []).length > 2) {
      host.append(h('p', { class: 'tk-trap soft', text: `Also built to catch: ${s.designed.slice(2).join(' · ')}` }));
    }
    const acts = h('div', { class: 'tk-acts' });
    const you = s.you;
    const qid = you && (you.qid || (s.module === 'm1' ? `m1q${String(s.position).padStart(2, '0')}` : null));
    if (sid && qid) acts.append(btn('Try one like this', { cls: 'btn sm', run: async b => {
      b.setAttribute('aria-busy', 'true');
      try { const r = await api('/drill', { method: 'POST', body: { from_session: sid, only: [qid], each: 1, source: 'try' } }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
      catch (e) { b.removeAttribute('aria-busy'); toast(`Couldn’t start one: ${e.message}`); }
    } }));
    acts.append(btn('Discuss', { cls: 'quiet', run: () => { ctx.tabs.set('d'); if (ctx.disc) ctx.disc.about(s.slot, true); } }));
    if (sid && you && you.q) acts.append(h('a', { class: 'quiet', href: report(sid, you.q), text: 'Open my review' }));
    host.append(acts);
  }

  /* ---------------- Discussion (§2.7) */
  function aboutOptions(slots) {
    const by = {};
    (slots || []).forEach(s => { (by[s.module] = by[s.module] || []).push(s); });
    return by;
  }
  function discussion(ctx, about0) {
    const { p, dPanel: host, crowd, sid } = ctx;
    const by = aboutOptions(crowd.slots);
    const onRoute = new Set((crowd.slots || []).filter(s => s.on_route !== false).map(s => s.slot));
    const qOf = new Map((crowd.slots || []).filter(s => s.you && s.you.q).map(s => [s.slot, s.you.q]));
    let sort = 'top', filter = '', data = ctx.posts, replyTo = null;
    const controls = h('div', { class: 'tk-bar' });
    host.append(controls);
    UI.seg(controls, [{ value: 'top', label: 'Top' }, { value: 'new', label: 'Newest' }], { value: 'top', label: 'Sort', onChange: x => { sort = x; load(); } });
    const groups = [{ label: 'Where', options: [{ value: 'paper', label: 'The whole paper' }, ...Object.keys(by).map(m => ({ value: m, label: MODULE[m] || m }))] },
      ...Object.keys(by).map(m => ({ label: MODULE[m] || m, options: by[m].map(s => ({ value: s.slot, label: slotName(s.slot) })) }))];
    const aboutDd = UI.dropdown(controls, { label: 'About', sm: true, groups, onChange: x => { filter = x || ''; paint(); } });
    const list = h('div', { class: 'tk-posts', 'aria-live': 'polite' });
    host.append(list);

    // the composer, sticky at the bottom of the panel
    const comp = h('form', { class: 'tk-compose', 'aria-label': 'Write a post' });
    const nameLine = h('div', { class: 'tk-name', hidden: true });
    const replyLine = h('p', { class: 'tk-reply meta', hidden: true });
    const ta = h('textarea', { class: 'field', rows: 2, maxlength: 500, 'aria-label': 'Your post', placeholder: 'Ask about a question, or say how the paper went' });
    ta.addEventListener('input', () => { ta.rows = Math.min(6, Math.max(2, ta.value.split('\n').length)); });
    const count = UI.counter ? UI.counter(ta, 500) : null;
    const sel = h('select', { class: 'field sm', 'aria-label': 'About' }, h('option', { value: '', text: 'The whole paper' }),
      Object.keys(by).map(m => h('optgroup', { label: MODULE[m] || m }, by[m].map(s => h('option', { value: s.slot, text: slotName(s.slot) })))));
    const send = h('button', { type: 'submit', class: 'btn icon', 'aria-label': 'Send', html: UI.svg && (UI.ICON || {}).arrow ? UI.svg(UI.ICON.arrow, 18) : 'Send' });
    const err = h('p', { class: 'error', role: 'alert', hidden: true });
    comp.append(nameLine, replyLine, h('div', { class: 'tk-comp-row' }, ta, send), h('div', { class: 'tk-comp-meta' }, sel, count), err);
    host.append(comp);
    comp.addEventListener('submit', e => { e.preventDefault(); post(); });
    ta.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); post(); } });

    // no board name: a line above the composer (PUT /api/me {name})
    let named = true;
    if (UI.me) UI.me().then(m => {
      const name = ((m && (m.profile || m)) || {}).name;
      if (name && String(name).trim()) return;
      named = false;
      const f = h('input', { class: 'field sm', maxlength: 24, 'aria-label': 'Your name on the board', placeholder: 'Your name' });
      nameLine.append(h('span', { class: 'k', text: 'Your name on the board' }), f, btn('Save', { cls: 'btn sm', run: async b => {
        const v = f.value.trim();
        if (!v) { f.focus(); return; }
        // Saving, then Saved with a drawn check in the button (no toast), then the line goes
        try { await UI.saving(b, () => api('/me', { method: 'PUT', body: { name: v } })); named = true; setTimeout(() => { nameLine.hidden = true; }, 900); if (UI.me) UI.me(true); }
        catch (x) { toast(`Name not saved: ${x.message}`); }
      } }));
      nameLine.hidden = false;
    }).catch(() => {});

    async function post() {
      const text = ta.value.trim();
      if (!text) { ta.focus(); return; }
      if (!named) { err.textContent = 'Set your name on the board first.'; err.hidden = false; nameLine.querySelector('input').focus(); return; }
      err.hidden = true;
      send.setAttribute('aria-busy', 'true');
      try {
        await api(`/papers/${p.n}/posts`, { method: 'POST', quiet: true, body: Object.assign({ text }, replyTo ? { parent: replyTo.id } : sel.value ? { about: sel.value } : {}) });
        ta.value = ''; ta.rows = 2; if (count && ta.dispatchEvent) ta.dispatchEvent(new Event('input'));
        setReply(null);
        await load();
      } catch (e) {
        err.replaceChildren(h('span', { text: e.status === 429 ? 'You’ve posted 20 times today.' : e.status === 422 && /name/.test(e.message) ? 'Set your name on the board first.' : 'Couldn’t send. ' }),
          e.status === 429 ? '' : btn('Retry', { cls: 'quiet', run: () => post() }));
        err.hidden = false;
      } finally { send.removeAttribute('aria-busy'); }
    }
    function setReply(t) {
      replyTo = t;
      replyLine.hidden = !t;
      sel.disabled = !!t;
      replyLine.replaceChildren();
      if (t) { replyLine.append(h('span', { text: `Replying to ${t.name || 'Student'}` }), btn('Cancel', { cls: 'quiet', aria: 'Cancel the reply', run: () => setReply(null) })); ta.focus(); }
    }

    async function load() {
      list.setAttribute('aria-busy', 'true');
      if (UI.skel && !list.childNodes.length) UI.skel(list, 'rows:3');
      try { data = await api(`/papers/${p.n}/posts?sort=${sort}`, { quiet: true }); paint(); }
      catch (_) { list.replaceChildren(); if (UI.cardError) UI.cardError(list, () => load(), 'Couldn’t load the discussion.'); }
      finally { list.removeAttribute('aria-busy'); }
    }
    const matches = t => !filter || (filter === 'paper' ? !t.about : filter.includes(':') ? t.about === filter : slotMod(t.about) === filter);
    function paint() {
      list.replaceChildren();
      const threads = ((data && data.threads) || []).filter(matches);
      if (ctx.tabs) ctx.tabs.count('d', (data && data.count) || 0);
      if (!threads.length) { list.append(h('p', { class: 'help tk-empty', text: filter ? 'No posts about this yet. Start one below.' : 'No posts yet. Ask about a question, or say how the paper went.' })); return; }
      threads.forEach(t => list.append(postEl(t, false)));
    }
    function postEl(t, reply) {
      const el = h('article', { class: 'tk-post' + (reply ? ' reply' : ''), 'data-id': String(t.id) });
      const when = [UI.relTime ? UI.relTime(t.at) : '', t.edited ? 'edited' : null].filter(Boolean).join(' · ');
      const head = h('div', { class: 'tk-ph' }, h('b', { text: t.name || 'Student' }), h('span', { class: 'tk-when', text: when }));
      if (t.about) {
        const on = onRoute.has(t.about), q = qOf.get(t.about);
        head.append(on && sid && q ? h('a', { class: 'badge soft', href: report(sid, q), text: slotName(t.about) })
          : h('span', { class: 'badge soft', text: on ? slotName(t.about) : `${slotName(t.about)} · not on your route` }));
      }
      el.append(head);
      const text = h('p', { class: 'tk-text', text: t.text });
      el.append(text);
      if (t.hidden) el.append(h('p', { class: 'meta', text: 'Hidden after reports. Only you can see it.' }));
      const acts = h('div', { class: 'tk-pa' });
      const help = btn(`Helpful${t.helpful ? ' ' + t.helpful : ''}`, { pressed: !!t.voted, aria: `Helpful, ${t.helpful || 0}`, run: async b => {
        if (t.mine || t.voted) return;
        try { const r = await api(`/posts/${t.id}/helpful`, { method: 'POST', quiet: true }); t.voted = true; t.helpful = r.helpful; b.textContent = `Helpful ${r.helpful}`; b.setAttribute('aria-pressed', 'true'); b.setAttribute('aria-label', `Helpful, ${r.helpful}`); }
        catch (e) { toast(`Couldn’t mark it: ${e.message}`); }
      } });
      if (t.mine) help.disabled = true;
      acts.append(help);
      if (!reply) acts.append(btn('Reply', { run: () => setReply(t) }));
      if (!t.mine) acts.append(btn('Report', { aria: `Report ${t.name || 'Student'}’s post`, run: async () => {
        const ok = await UI.confirm({ title: 'Report this post?', text: 'Three reports from different students hide it until a moderator looks.', confirm: 'Report', cancel: 'Keep it' });
        if (!ok) return;
        try { const r = await api(`/posts/${t.id}/report`, { method: 'POST', quiet: true }); toast(r.hidden ? 'Reported. It’s hidden now.' : 'Reported. Thanks.'); if (r.hidden) load(); }
        catch (e) { toast(e.status === 409 ? 'You’ve reported this already.' : `Couldn’t report it: ${e.message}`); }
      } }));
      if (t.editable) {
        acts.append(btn('Edit', { run: () => edit(t, el, text) }), btn('Delete', { run: async () => {
          const ok = await UI.confirm({ title: 'Delete this post?', text: t.replies && t.replies.length ? `Its ${plural(t.replies.length, 'reply', 'replies')} go too.` : 'This can’t be undone.', confirm: 'Delete', cancel: 'Keep it', destructive: true });
          if (!ok) return;
          try { await api(`/posts/${t.id}`, { method: 'DELETE', quiet: true }); load(); }
          catch (e) { toast(e.status === 409 ? 'Posts can be changed for 15 minutes.' : `Couldn’t delete it: ${e.message}`); }
        } }));
      }
      el.append(acts);
      const reps = t.replies || [];
      if (reps.length) {
        const rl = h('div', { class: 'tk-replies' });
        reps.slice(0, 2).forEach(x => rl.append(postEl(x, true)));
        if (reps.length > 2) {
          const more = btn(`Show ${reps.length - 2} more ${reps.length - 2 === 1 ? 'reply' : 'replies'}`, { run: () => { more.remove(); reps.slice(2).forEach(x => rl.append(postEl(x, true))); } });
          rl.append(more);
        }
        el.append(rl);
      }
      return el;
    }
    function edit(t, el, text) {
      if (el.querySelector('.tk-edit')) return;
      const f = h('textarea', { class: 'field', rows: 3, maxlength: 500, 'aria-label': 'Edit your post' });
      f.value = t.text;
      const box = h('div', { class: 'tk-edit' }, f, h('div', { class: 'tk-edit-acts' }, UI.counter ? UI.counter(f, 500) : null,
        btn('Cancel', { run: () => { box.remove(); text.hidden = false; } }),
        btn('Save', { cls: 'btn sm', run: async b => {
          const v = f.value.trim();
          if (!v) return;
          b.setAttribute('aria-busy', 'true');
          try { await api(`/posts/${t.id}`, { method: 'PUT', quiet: true, body: { text: v } }); load(); }
          catch (e) { b.removeAttribute('aria-busy'); toast(e.status === 409 ? 'Posts can be changed for 15 minutes.' : `Not saved: ${e.message}`); }
        } })));
      text.hidden = true;
      text.after(box);
      f.focus();
    }

    paint();
    const api_ = {
      about(slot, compose) {
        filter = slot || '';
        if (aboutDd && aboutDd.set) aboutDd.set(filter);
        paint();
        if (compose) { setReply(null); sel.value = slot || ''; ta.focus(); }
      },
    };
    if (about0) api_.about(about0, true);
    return api_;
  }

  window.TestsTalk = { open };
})();
