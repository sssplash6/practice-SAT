/* ============================================================================
   SAT Freshman -- the command palette (spec/rebuild-v2.md Shell 2.8 and acceptance 11;
   shell-me.md U1, U2, U24 and override 12; practice.md P15; product.md G7, G12)

   Loaded by ui.js on first use (UI.palette is a stub until then). Opens with ⌘K / Ctrl K,
   `/`, the Search button and the phone's Search. Markup is ui.css's dialog.palette.

     UI.palette(query?) -> {el, close}
   Groups, in order: the composed set ("circles hard 5 timed" -> Practise Circles · Hard ·
   5 questions · timed, or "15 min" -> Up next for 15 minutes), Commands (target, exam,
   every pref by name and value: "timer off", "dark", "set 22"), Skills (glyph, mastery
   bar, open mistakes; Tab: Practise · Practise hard · Fix mistakes · Open stats),
   Question types (386, Shift+Enter opens the type's page), Mistakes (named
   misconceptions across types), Pages, Actions, Settings (every registry key with its
   value), Help (answers.json). With no query: Suggested (Up next), Recent (the last 5
   run, localStorage satf.palette), Skills, Pages, Actions.
   Keys: ↑ ↓ move, Enter runs, Shift+Enter the alternative, Tab the row's sub-actions,
   Esc closes and focus returns.
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI;
  const doc = document;
  const h = UI.h;
  const RECENT = 'satf.palette';
  const lget = (k, d) => { try { const v = JSON.parse(localStorage.getItem(k) || 'null'); return v === null ? d : v; } catch (_) { return d; } };
  const lput = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} };
  const fmt = n => Number(n || 0).toLocaleString('en-US');
  const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
  const words = s => String(s || '').toLowerCase().replace(/&/g, ' and ').replace(/[‐-―-]/g, ' ')
    .replace(/[^a-z0-9∞\s]/g, ' ').split(/\s+/).filter(Boolean);
  const icon = (name, size = 20) => { const t = doc.createElement('template'); t.innerHTML = UI.svg(UI.ICON[name] || '', size); return t.content.firstElementChild; };
  const setLength = () => { const n = (UI.prefs.now() || {}).set_length; return n === 0 ? null : (n || 10); };
  const qn = n => n ? `${fmt(n)} ${n === 1 ? 'question' : 'questions'}` : 'Endless';

  /* ---- matching: every typed word is a word prefix of the text, or (3+ letters) inside it */
  function score(toks, text, extra) {
    if (!toks.length) return 1;
    const ws = words(text).concat(extra ? words(extra) : []);
    const flat = ws.join(' ');
    let s = 0;
    for (const t of toks) {
      if (ws.some(w => w === t)) s += 4;
      else if (ws.some(w => w.startsWith(t))) s += 3;
      else if (t.length >= 4 && flat.includes(t)) s += 1;
      else return 0;
    }
    if (words(text)[0] && words(text)[0].startsWith(toks[0])) s += 2;
    return s;
  }
  const best = (rows, toks, key, n) => rows.map(r => [score(toks, key(r), r.also), r]).filter(x => x[0] > 0)
    .sort((a, b) => b[0] - a[0]).slice(0, n).map(x => x[1]);

  /* ---- data, each arriving when it arrives; the palette repaints as it does */
  const data = { map: null, types: null, mistakes: null, prefs: null, help: null, me: null, next: null };
  function load(repaint) {
    UI.cached('/map', d => { data.map = d; repaint(); }, { api: { quiet: true } }).catch(() => {});
    UI.types().then(t => { data.types = t; data.mistakes = null; repaint(); }, () => { data.types = { list: [], byTopic: {}, failed: true }; repaint(); });
    let reg = null;
    try { reg = JSON.parse(sessionStorage.getItem('satf.prefs.registry') || 'null'); } catch (_) {}
    if (Array.isArray(reg)) data.prefs = reg;
    else UI.api('/prefs', { quiet: true }).then(p => {
      data.prefs = p;
      try { sessionStorage.setItem('satf.prefs.registry', JSON.stringify(p)); } catch (_) {}
      repaint();
    }, () => {});
    UI.me().then(m => { data.me = m; repaint(); }, () => {});
    if (UI.has('help') && !data.help) fetch('/help/answers.json').then(r => r.ok ? r.json() : null).then(a => { data.help = helpRows(a); if (data.help.length) repaint(); }, () => {});
    if (UI.has('next')) UI.api('/next?limit=5', { quiet: true }).then(r => { if (r && Array.isArray(r.items)) { data.next = r.items; repaint(); } }, () => {});
  }
  function helpRows(a) {
    const list = Array.isArray(a) ? a : (a && (a.answers || a.items)) || [];
    return list.map(x => ({ q: x.q || x.question || x.title || '', a: String(x.a || x.answer || x.text || '').split('\n')[0],
      id: x.id || x.anchor || x.slug || '' })).filter(x => x.q);
  }
  // one row per named misconception, across every type that sets it
  function mistakeIndex() {
    if (data.mistakes || !data.types) return data.mistakes || [];
    const by = new Map();
    for (const t of data.types.list) for (const r of t.reasons) {
      let m = by.get(r.norm);
      if (!m) by.set(r.norm, m = { norm: r.norm, label: cap(r.label), templates: [], topics: new Set() });
      m.templates.push(t.template);
      m.topics.add(t.topic);
    }
    return (data.mistakes = [...by.values()]);
  }

  /* ---- running things */
  let say = () => {};
  function remember(entry) {
    if (!entry) return;
    const list = lget(RECENT, []).filter(x => x && x.label !== entry.label);
    lput(RECENT, [entry, ...list].slice(0, 5));
  }
  async function drill(body, recent) {
    say('Starting…');
    try {
      const r = await UI.api('/drill', { method: 'POST', body });
      remember(recent);
      location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`;
    } catch (e) {
      const d = e.detail || {};
      say(e.offline ? 'Can’t reach SAT Freshman.' : e.status === 409 ? `Nothing to serve: ${(d.reason || e.message || '').replace(/_/g, ' ')}` :
        e.status === 422 ? `That set can’t be made: ${d.reason || d.field || e.message}` : 'Couldn’t start it. Try again.');
    }
  }
  async function mock(full, recent) {
    say('Starting…');
    try {
      const s = await UI.api('/mock/new', { method: 'POST', body: { full, timed: true } });
      remember(recent);
      location.href = `/test/?s=${encodeURIComponent(s.id)}`;
    } catch (e) { say('Couldn’t start it. Try again.'); }
  }
  const go = (href, recent) => { remember(recent); location.href = href; };
  // a change with an Undo toast (U24): "Target 700 · Undo"
  async function change(put, undo, text) {
    close();
    try { await put(); } catch (e) { if (UI.toast) UI.toast(e.status === 422 ? `Not saved: ${e.detail || e.message}` : 'Not saved. Try again.'); return; }
    if (UI.toast) UI.toast(text, { undo: async () => { await undo(); UI.refresh(); } });
    UI.refresh();
  }
  const ACTIONS = {                      // re-runnable from Recent by id
    quick: () => UI.quick('question'), mistake: () => UI.quick('mistake'), word: () => UI.quick('word'),
    module: () => mock(false), section: () => mock(true), phone: () => UI.continueOnPhone(),
    feedback: () => UI.feedback(), keys: () => UI.keys.sheet(), signout: () => UI.signOut(),
  };
  function replay(act) {
    if (!act) return;
    if (act.drill) drill(act.drill, null);
    else if (act.href) go(act.href);
    else if (act.run && ACTIONS[act.run]) { close(); ACTIONS[act.run](); }
  }

  /* ---- rows. {label, sub, meta, icon, run(alt), subs, recent, bold} */
  const drillRow = (label, body, o = {}) => ({ ...o, label, run: () => drill(body, { label: typeof label === 'string' ? label : o.text, sub: o.sub, act: { drill: body } }) });

  const typedCount = toks => toks.some(t => /^\d{1,3}(q|qs)?$/.test(t) && +t.replace(/\D/g, '') >= 1 && +t.replace(/\D/g, '') <= 120);
  function composed(parse, toks) {
    if (!parse.any || parse.unknown.length) return [];
    // one skill or one type alone is its own row below; compose only what adds to it
    const extra = parse.chips.filter(c => !c.key.startsWith('topic:') && c.key !== 'type' && (c.key !== 'count' || typedCount(toks)));
    if (!extra.length && (parse.body.topics || []).length < 2) return [];
    const label = h('span', {});
    if (parse.box && !parse.body.topics && parse.body.source === 'next') label.append('Up next for ', h('b', { text: `${parse.box} minutes` }));
    else {
      label.append('Practise ');
      parse.chips.forEach((c, i) => {
        if (i) label.append(' · ');
        label.append(c.key.startsWith('topic:') || c.key === 'type' ? h('b', { text: c.label }) : c.label);
      });
    }
    return [drillRow(label, parse.body, { text: parse.text, icon: icon(parse.box ? 'clock' : 'play', 18), kbd: 'Enter' })];
  }

  function suggested() {
    const items = (data.next || UI.nextItems()).slice(0, 5);
    if (items.length) return items.map(it => ({ label: it.title, sub: [it.reason, it.minutes ? `${fmt(it.minutes)} min` : null].filter(Boolean).join(' · '),
      icon: icon('play', 18), run: () => { say('Starting…'); UI.start(it).catch(() => say('Couldn’t start it. Try again.')); } }));
    // before Up next exists (U1's next.py): the day's own starts
    const s = UI.shellData() || {}, out = [];
    const coach = data.map && data.map.coach && data.map.coach.topics;
    const cn = (data.map && data.map.coach && data.map.coach.count) || setLength();   // the plan's per-session count, as Today starts it
    if (coach && coach.length) out.push(drillRow(`Today’s set · ${coach.map(t => (UI.TOPIC[t] || {}).short || t).join(', ')}`,
      { topics: coach, count: cn, source: 'coach' }, { sub: qn(cn), icon: icon('today', 18) }));
    if (s.mistakes) out.push(drillRow(`Fix all mistakes (${fmt(s.mistakes)})`, { pool: 'redo', source: 'palette' }, { icon: icon('review', 18) }));
    if (s.resume) out.push({ label: s.resume.kind === 'drill' ? 'Resume your set' : `Resume ${s.resume.kind}`, sub: s.resume.total ? `${fmt(s.resume.answered)}/${fmt(s.resume.total)}` : null,
      icon: icon('play', 18), run: () => go(s.resume.href) });
    if (s.challenge && !s.challenge.done) out.push({ label: 'Today’s challenge', icon: icon('trophy', 18), run: () => go('/compete/', { label: 'Today’s challenge', act: { href: '/compete/' } }) });
    return out;
  }

  function skillRows(toks, only) {
    const topics = new Map(((data.map && data.map.topics) || []).map(t => [t.topic, t]));
    const all = UI.TOPICS.map(t => ({ t, also: `${t.slug.replace(/_/g, ' ')} ${(UI.ALIASES[t.slug] || []).join(' ')}` }));
    const hit = only ? all.filter(x => only.includes(x.t.slug)) : toks.length ? best(all, toks, x => x.t.short, 19) : all;
    return hit.map(({ t }) => {
      const m = topics.get(t.slug) || {}, open = (m.traps || []).length, n = setLength();
      const meta = h('span', { style: 'display: inline-flex; align-items: center; gap: 10px' },
        h('span', { class: 'mbar', role: 'img', 'aria-label': `Mastery ${Math.round((m.mastery || 0) * 100)}%` }, h('i', { style: `--m: ${Math.max(0, Math.min(1, m.mastery || 0))}` })),
        open ? h('span', { 'aria-label': `${open} open mistakes` }, h('i', { class: 'dot', 'aria-hidden': 'true' }), ` ${fmt(open)}`) : null);
      const body = extra => ({ topics: [t.slug], count: n, source: 'palette', ...extra });
      const subs = [
        drillRow(`Practise · ${qn(n)}`, body(), {}),
        drillRow('Practise hard', body({ tiers: ['hard'] }), {}),
        open ? drillRow(`Fix mistakes (${fmt(open)})`, { pool: 'redo', topics: [t.slug], source: 'palette' }, {}) : null,
        { label: 'Open stats', run: () => go(`/results/#${t.slug}`) },
      ].filter(Boolean);
      return { ...drillRow(t.short, body(), { sub: t.dshort, icon: UI.glyph(t.slug), meta }), subs };
    });
  }

  // types named by the words typed; a skill alone ("circles") lists that skill's types
  function typeMatches(toks, parse, n) {
    if (!parse.unknown.length && parse.body.topics) return data.types.list.filter(t => parse.body.topics.includes(t.topic)).slice(0, n);
    return best(data.types.list.map(t => ({ ...t, also: t.about })), parse.unknown.length ? parse.unknown : toks, x => x.name, n);
  }
  function typeRows(toks, parse, cap_) {
    if (!data.types) return [{ label: 'Loading question types…', disabled: true }];
    const set = {};
    ['tiers', 'adaptive', 'timed', 'formats', 'feedback'].forEach(k => { if (parse.body[k] !== undefined) set[k] = parse.body[k]; });
    const count = typedCount(toks) && parse.body.count ? parse.body.count : 5;
    const rows = typeMatches(toks, parse, cap_);
    return rows.map(t => {
      const body = { templates: [t.template], count, source: 'palette', ...set };
      return { ...drillRow(t.name, body, { sub: [(UI.TOPIC[t.topic] || {}).short, t.about].filter(Boolean).join(' · '), icon: UI.glyph(t.topic), meta: `Practise this type · ${count}` }),
        alt: () => go(`/types/?t=${encodeURIComponent(t.template)}`) };
    });
  }

  function mistakeRows(toks, n) {
    return best(mistakeIndex(), toks, x => x.label, n).map(m => {
      const names = [...m.topics].map(s => (UI.TOPIC[s] || {}).short || s);
      const templates = m.templates.slice(0, 120);
      const body = { templates, want: Object.fromEntries(templates.map(t => [t, m.norm])), count: setLength() || 10, source: 'palette' };
      return drillRow(m.label, body, { sub: `${names.slice(0, 2).join(', ')}${names.length > 2 ? ` +${names.length - 2}` : ''} · ${m.templates.length === 1 ? '1 type' : `${m.templates.length} types`}`,
        icon: icon('review', 18), meta: 'Drill it' });
    });
  }

  function pageRows() {
    const s = UI.shellData() || {}, saved = !!(s.me && s.me.linked);
    const pages = UI.NAV.map(n => ({ label: n.label, href: n.href, icon: n.icon, kbd: `G ${n.key}` }))
      .concat([{ label: 'Settings', href: '/me/settings/', icon: 'settings', kbd: 'G S' },
        { label: 'Help & FAQ', href: '/help/', icon: 'help', kbd: 'G H' },
        { label: 'Your reports', href: '/me/settings/#reports', icon: 'chat' },
        saved ? null : { label: 'Sign in', href: '/signin/', icon: 'signin' },
        { label: 'Sign in another device', href: '/pair/', icon: 'devices' }]).filter(Boolean);
    return pages.map(p => ({ label: p.label, icon: icon(p.icon, 18), kbd: p.kbd, also: 'page go open',
      run: () => go(p.href, { label: p.label, act: { href: p.href } }) }));
  }

  function actionRows() {
    const s = UI.shellData() || {}, saved = !!(s.me && s.me.linked), n = setLength();
    const act = (label, run, o = {}) => ({ label, icon: icon(o.icon || 'arrow', 18), kbd: o.kbd, sub: o.sub, also: o.also,
      run: () => { if (o.id) remember({ label, act: { run: o.id } }); close(); run(); } });
    const rows = [
      act('Quick question', ACTIONS.quick, { icon: 'bolt', kbd: 'Q', id: 'quick', also: 'one' }),
      act('Log a mistake', ACTIONS.mistake, { icon: 'plus', id: 'mistake', also: 'bluebook school outside missed bring misses question id' }),
      act('Add a word', ACTIONS.word, { icon: 'words', id: 'word', also: 'vocabulary vocab' }),
      { label: 'Start a module', sub: '22 q · 35 min', icon: icon('tests', 18), also: 'test timed',
        run: () => mock(false, { label: 'Start a module', act: { run: 'module' } }) },
      { label: 'Start a full section', sub: '44 q · 70 min', icon: icon('tests', 18), also: 'test timed mock',
        run: () => mock(true, { label: 'Start a full section', act: { run: 'section' } }) },
      { label: 'Take the diagnostic', icon: icon('tests', 18), also: 'placement score band', run: () => go('/diagnostic/', { label: 'Take the diagnostic', act: { href: '/diagnostic/' } }) },
      s.saved ? drillRow(`Practise saved (${fmt(s.saved)})`, { pool: 'saved', exact: true, count: Math.min(s.saved, 120), source: 'palette' }, { icon: icon('bookmark', 18), also: 'bookmarks' }) : null,
      s.mistakes ? drillRow(`Fix all mistakes (${fmt(s.mistakes)})`, { pool: 'redo', source: 'palette' }, { icon: icon('review', 18), also: 'redo review' }) : null,
      drillRow('Practise types I haven’t met', { pool: 'untried', count: n || 10, source: 'palette' }, { icon: icon('practice', 18), also: 'new untried unseen' }),
      act('Send feedback', ACTIONS.feedback, { icon: 'chat', id: 'feedback', also: 'report a bug problem idea' }),
      UI.has('pair') ? act('Continue on your phone', ACTIONS.phone, { icon: 'devices', id: 'phone', also: 'pair qr mobile' }) : null,
      saved ? null : { label: 'Save progress', icon: icon('save', 18), also: 'email account keep', run: () => go('/me/settings/#account') },
      UI.learner().startsWith('a:') ? act('Copy device code', () => UI.copyText && UI.copyText(UI.learner(), { toast: 'Copied' }), { icon: 'devices' }) : null,
      UI.has('share') ? { label: 'Copy progress link', icon: icon('arrow', 18), also: 'share parent tutor', run: shareLink } : null,
      UI.has('export') ? { label: 'Download my data', icon: icon('save', 18), also: 'export', run: () => go('/api/me/export') } : null,
      ...['light', 'dark', 'system'].map(v => ({ label: `Theme: ${cap(v)}`, icon: icon('moon', 18), also: 'look appearance mode',
        run: () => { const was = (UI.prefs.now() || {}).theme || 'light'; change(() => UI.prefs.set({ theme: v }), () => UI.prefs.set({ theme: was }), `Theme: ${cap(v)}`); } })),
      act('Keyboard shortcuts', ACTIONS.keys, { icon: 'keyboard', kbd: '?', id: 'keys', also: 'keys' }),
      act(saved || UI.shared() ? 'Sign out' : 'Leave this device', ACTIONS.signout, { icon: 'signout', also: 'log out' }),
    ];
    return rows.filter(Boolean);
  }
  async function shareLink() {
    say('Making a link…');
    try {
      const r = await UI.api('/share', { method: 'POST', body: {} });
      const url = r.url || `${location.origin}/share/?t=${encodeURIComponent(r.token)}`;
      close();
      if (UI.copyText) UI.copyText(url, { toast: 'Progress link copied' });
    } catch (e) { say(e.status === 404 || e.status === 405 ? 'Progress links aren’t available yet.' : 'Couldn’t make a link. Try again.'); }
  }

  /* ---- Commands (U24): target, exam date, and any pref by its name and a value */
  const valLabel = (spec, v) => {
    if (spec.kind === 'bool') return v ? 'On' : 'Off';
    if (Array.isArray(v)) return v.map(x => valLabel(spec, x)).join(', ');
    const hit = (spec.values || []).find(x => x.v === v);
    return hit ? hit.label : v === null || v === undefined || v === '' ? 'Off' : String(v);
  };
  const BOOL = { on: true, yes: true, true: true, show: true, off: false, no: false, false: false, hide: false, none: false };
  function prefCommands(toks) {
    if (!data.prefs || !toks.length) return [];
    const now = UI.prefs.now() || {};
    const out = [];
    for (const spec of data.prefs) {
      if (!['bool', 'choice', 'subset', 'int'].includes(spec.kind)) continue;
      const names = [spec.label, ...(spec.synonyms || [])].map(words);
      const one = toks.length === 1;
      const headOk = head => head.length && (one ? (spec.synonyms || []).map(words).some(ws => ws.length === 1 && ws[0] === head[0])
        : names.some(ws => head.every(t => ws.some(w => w === t || (t.length >= 3 && w.startsWith(t))))));
      const valueOf = val => {
        if (!val.length) return undefined;
        if (spec.kind === 'bool') return val.length === 1 && val[0] in BOOL ? BOOL[val[0]] : undefined;
        if (spec.kind === 'int') {
          const n = val.length === 1 && /^\d+$/.test(val[0]) ? +val[0] : NaN;
          const [lo, hi] = spec.range || [0, 120];
          return n >= lo && n <= hi ? n : undefined;
        }
        const hit = (spec.values || []).filter(x => val.every(t => words(x.label).some(w => w === t || (!one && t.length >= 2 && w.startsWith(t))) || String(x.v) === t));
        if (hit.length !== 1) return undefined;
        return spec.kind === 'subset' ? [hit[0].v] : hit[0].v;
      };
      let v;
      for (let k = toks.length; k >= 0 && v === undefined; k--) {
        const head = toks.slice(0, k), val = toks.slice(k);
        if (k === 0) { if (toks.length === 1 && headOk(toks)) v = valueOf(toks); }        // "dark", "hard", "grid"
        else if (k === toks.length) { if (spec.kind === 'bool' && headOk(head) && !(now[spec.key] ?? spec.default)) v = true; }
        else if (headOk(head)) v = valueOf(val);
      }
      if (v === undefined) continue;
      const cur = now[spec.key] ?? spec.default;
      if (JSON.stringify(cur) === JSON.stringify(v)) continue;        // already so: Settings shows it
      out.push({ label: `${spec.label}: ${valLabel(spec, cur)} → ${valLabel(spec, v)}`, icon: icon('settings', 18),
        run: () => change(() => UI.prefs.set({ [spec.key]: v }), () => UI.prefs.set({ [spec.key]: cur }), `${spec.label}: ${valLabel(spec, v)}`) });
      if (out.length >= 4) break;
    }
    return out;
  }
  const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
  function dateOf(val) {                 // "dec 5", "december 5", "12/5", "2026-12-05" -> the next such day
    const s = val.join(' ');
    let m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(val[0] || '');
    if (m) return `${m[1]}-${m[2]}-${m[3]}`;
    let mon = -1, dd = 0;
    if (val.length === 2 && /^\d{1,2}$/.test(val[1])) { mon = MONTHS.findIndex(x => val[0].startsWith(x)); dd = +val[1]; }
    else if ((m = /^(\d{1,2}) (\d{1,2})$/.exec(s))) { mon = +m[1] - 1; dd = +m[2]; }
    if (mon < 0 || dd < 1 || dd > 31) return null;
    const t = new Date(); t.setHours(12, 0, 0, 0);
    let y = t.getFullYear();
    const iso = yy => `${yy}-${String(mon + 1).padStart(2, '0')}-${String(dd).padStart(2, '0')}`;
    if (new Date(iso(y) + 'T12:00:00') < new Date(t.toDateString())) y += 1;
    return iso(y);
  }
  const niceDay = iso => { const d = new Date(iso + 'T12:00:00'); return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }); };
  function goalCommands(toks) {
    const p = (data.me && data.me.profile) || {}, out = [];
    if (toks[0] === 'target' || toks[0] === 'goal') {
      const n = Number(toks[1]);
      if (toks.length === 2 && n >= 200 && n <= 800) {
        const v = Math.round(n / 10) * 10, was = p.target ?? null;
        out.push({ label: `Target: ${was ? fmt(was) : 'none'} → ${fmt(v)}`, icon: icon('plan', 18), sub: 'Math, 200 to 800',
          run: () => change(() => UI.api('/me', { method: 'PUT', body: { target: v } }), () => UI.api('/me', { method: 'PUT', body: { target: was } }), `Target ${fmt(v)}`) });
      } else if (toks.length === 2 && n > 800 && n <= 1600) {
        out.push({ label: `Target ${fmt(n)} is a total: type the Math part, 200 to 800`, icon: icon('plan', 18), disabled: true });
      }
    }
    if ((toks[0] === 'exam' || toks[0] === 'sat' || toks[0] === 'test') && toks.length >= 2) {
      const iso = dateOf(toks.slice(1));
      if (iso) {
        const was = p.exam_date || null;
        const official = (UI.SAT_DATES || []).find(x => x.date === iso || x.day === iso);
        const days = Math.round((new Date(iso + 'T12:00:00') - new Date(new Date().toDateString() + ' 12:00')) / 864e5);
        const bits = [`in ${fmt(days)} ${days === 1 ? 'day' : 'days'}`];
        if (official && official.register_by) bits.push(`register by ${UI.day(official.register_by)}`);
        if (!official) bits.push('not an official SAT date');
        out.push({ label: `Exam: ${was ? UI.day(was) : 'none'} → ${niceDay(iso)}`, sub: bits.join(' · '), icon: icon('today', 18),
          run: () => change(() => UI.api('/me', { method: 'PUT', body: { exam_date: iso } }), () => UI.api('/me', { method: 'PUT', body: { exam_date: was } }), `Exam ${niceDay(iso)}`) });
      }
    }
    return out;
  }

  /* ---- Settings: every registry key by label and synonym, with its value */
  function settingRows(toks) {
    if (!data.prefs || !toks.length) return [];
    const now = UI.prefs.now() || {};
    const specs = data.prefs.filter(s => ['bool', 'choice', 'subset', 'int', 'time', 'date'].includes(s.kind));
    return best(specs, toks, s => `${s.label} ${(s.synonyms || []).join(' ')}`, 6).map(spec => {
      const cur = now[spec.key] ?? spec.default;
      const row = { label: spec.label, sub: spec.helper || null, meta: valLabel(spec, cur), icon: icon('settings', 18), also: (spec.synonyms || []).join(' ') };
      if (spec.kind === 'bool') row.run = () => change(() => UI.prefs.set({ [spec.key]: !cur }), () => UI.prefs.set({ [spec.key]: cur }), `${spec.label}: ${cur ? 'Off' : 'On'}`);
      else if (spec.kind === 'choice' || spec.kind === 'subset') {
        row.subs = (spec.values || []).map(x => {
          const v = spec.kind === 'subset' ? [x.v] : x.v;
          return { label: x.label, run: () => change(() => UI.prefs.set({ [spec.key]: v }), () => UI.prefs.set({ [spec.key]: cur }), `${spec.label}: ${x.label}`) };
        });
        row.run = null;                  // Enter opens the values, as Tab does
      } else row.run = () => go('/me/settings/');
      return row;
    });
  }
  function helpRowsFor(toks) {
    if (!data.help || !toks.length) return [];
    return best(data.help, toks, x => x.q, 5).map(x => ({ label: x.q, sub: x.a, icon: icon('help', 18), run: () => go(`/help/#${encodeURIComponent(x.id)}`) }));
  }

  /* ---- the dialog */
  let cur = null;
  function close() { if (cur) cur.close(); }
  function palette(initial = '') {
    if (cur) { cur.input.focus(); return cur; }
    const opener = doc.activeElement;
    const dlg = h('dialog', { class: 'palette', 'aria-label': 'Search' });
    const listId = 'pal-list';
    const input = h('input', { type: 'text', role: 'combobox', 'aria-expanded': 'true', 'aria-controls': listId, 'aria-autocomplete': 'list',
      'aria-label': 'Search skills, question types, pages and actions', placeholder: 'Search skills, question types, pages and actions',
      autocomplete: 'off', autocapitalize: 'off', spellcheck: 'false', enterkeyhint: 'go' });
    const qbar = h('div', { class: 'palette-q' }, icon('search', 20), input);
    const list = h('div', { class: 'palette-list', role: 'listbox', id: listId, 'aria-label': 'Results' });
    const status = h('span', { role: 'status', style: 'margin-left: auto; color: var(--ink)' });
    const foot = h('div', { class: 'palette-foot' }, h('span', { text: '↑↓ move' }), h('span', { text: 'Enter run' }),
      h('span', { text: 'Tab more' }), h('span', { text: 'Esc close' }), status);
    dlg.append(qbar, list, foot);
    say = t => { status.textContent = t; };
    let entries = [], active = 0, expanded = null, seq = 0, typeCap = 8;

    function groupsFor(q) {
      const toks = words(q);
      const parse = UI.parseSet(q, { count: setLength(), types: data.types ? data.types.list : null });
      if (!toks.length) {
        const recent = lget(RECENT, []).filter(x => x && x.label).map(x => ({ label: x.label, sub: x.sub, icon: icon('clock', 18), run: () => replay(x.act) }));
        return [['Suggested', suggested()], ['Recent', recent], ['Skills', skillRows([])], ['Pages', pageRows()], ['Actions', actionRows()]];
      }
      const types = typeRows(toks, parse, typeCap);
      const more = data.types && typeCap < 50 && typeMatches(toks, parse, 50).length > typeCap;
      if (more) types.push({ label: 'Show more question types', icon: icon('chev', 18), keep: true, run: () => { typeCap = 50; paint(); } });
      const pages = ['Pages', best(pageRows(), toks, r => r.label, 6)], actions = ['Actions', best(actionRows(), toks, r => r.label, 8)];
      // a page or action named by what was typed ("test", "settings") comes before the bank's rows
      const named = ([, rows]) => rows.some(r => typeof r.label === 'string' && (words(r.label)[0] || '').startsWith(toks[0]));
      const early = [pages, actions].filter(named), late = [pages, actions].filter(g => !named(g));
      return [
        ['', composed(parse, toks)],
        ['Commands', goalCommands(toks).concat(prefCommands(toks))],
        ['Skills', !parse.unknown.length && parse.body.topics ? skillRows(toks, parse.body.topics) : skillRows(toks)],
        ...early,
        ['Question types', types],
        // every word a set word ("hard", "grid"): the misconceptions that contain it are noise
        ['Mistakes', parse.unknown.length || !parse.any ? mistakeRows(toks, 6) : []],
        ...late,
        ['Settings', settingRows(toks)],
        ['Help', helpRowsFor(toks)],
      ];
    }
    function option(row, sub) {
      const el = h('div', { role: 'option', id: `pal-o${++seq}`, 'aria-selected': 'false', 'aria-disabled': row.disabled ? 'true' : null,
        class: sub ? 'btn sm' : null },
        sub ? null : row.icon || null,
        h('span', { class: 'opt-main' }, row.label, row.sub ? h('span', { class: 'opt-sub', text: row.sub }) : null),
        row.meta ? h('span', { class: 'opt-meta' }, row.meta) : null,
        row.kbd && !sub ? h('span', { class: 'opt-meta' }, UI.keys.caps(row.kbd)) : null);
      const entry = { el, row };
      el.addEventListener('pointermove', () => { if (entries[active] !== entry) activate(entries.indexOf(entry), false); });
      el.addEventListener('click', e => { activate(entries.indexOf(entry), false); run(e.shiftKey); });
      return entry;
    }
    function paint() {
      const q = input.value;
      const groups = groupsFor(q).filter(([, rows]) => rows.length);
      list.replaceChildren();
      entries = [];
      groups.forEach(([label, rows], gi) => {
        const gid = `pal-g${gi}`;
        const g = h('div', { role: 'group', 'aria-labelledby': label ? gid : null, 'aria-label': label ? null : 'Composed set' });
        if (label) g.append(h('div', { class: 'palette-group', id: gid, text: label }));
        rows.forEach(row => {
          const e = option(row);
          g.append(e.el);
          entries.push(e);
          if (expanded && expanded === rowKey(row) && row.subs) {
            const box = h('div', { class: 'palette-sub', role: 'group', 'aria-label': `${typeof row.label === 'string' ? row.label : 'More'}: more` });
            row.subs.forEach(sr => { const se = option(sr, true); se.parent = e; box.append(se.el); entries.push(se); });
            g.append(box);
          }
        });
        list.append(g);
      });
      if (!entries.length) {
        list.append(h('p', { class: 'palette-empty', text: 'No match. Try a skill like “circles”, a type like “central angle”, or “percent 10 hard”.' }));
      }
      activate(Math.min(active, Math.max(0, entries.length - 1)), true);
    }
    const rowKey = row => typeof row.label === 'string' ? row.label : (row.text || '');
    function activate(i, scroll = true) {
      entries.forEach((e, k) => e.el.setAttribute('aria-selected', k === i ? 'true' : 'false'));
      active = i;
      const e = entries[i];
      if (e) { input.setAttribute('aria-activedescendant', e.el.id); if (scroll) e.el.scrollIntoView({ block: 'nearest' }); }
      else input.removeAttribute('aria-activedescendant');
    }
    function run(alt) {
      const e = entries[active];
      if (!e || e.row.disabled) return;
      if (alt && e.row.alt) { e.row.alt(); return; }
      if (e.row.run) e.row.run(alt);
      else if (e.row.subs) toggle(e);
    }
    function toggle(e) {
      const key = rowKey((e.parent || e).row);
      expanded = expanded === key && !e.parent ? null : key;
      const at = entries.indexOf(e.parent || e);
      paint();
      const first = entries.findIndex((x, k) => k > at && x.parent);
      activate(expanded && first >= 0 ? first : at);
    }
    input.addEventListener('input', () => { active = 0; expanded = null; typeCap = 8; say(''); paint(); });
    input.addEventListener('keydown', e => {
      const n = entries.length;
      if (e.key === 'ArrowDown') { e.preventDefault(); if (n) activate((active + 1) % n); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); if (n) activate((active - 1 + n) % n); }
      else if (e.key === 'PageDown') { e.preventDefault(); if (n) activate(Math.min(n - 1, active + 8)); }
      else if (e.key === 'PageUp') { e.preventDefault(); if (n) activate(Math.max(0, active - 8)); }
      else if (e.key === 'Enter') { e.preventDefault(); run(e.shiftKey); }
      else if (e.key === 'Tab') {
        e.preventDefault();
        const x = entries[active];
        if (!x) return;
        if (e.shiftKey) { if (expanded) { const p = x.parent || x; expanded = null; const at = entries.indexOf(p); paint(); activate(at); } return; }
        if (x.parent) { const next = entries[active + 1]; activate(next && next.parent === x.parent ? active + 1 : entries.indexOf(x.parent)); return; }
        if (x.row.subs) toggle(x);
      }
    });
    // the phone: full screen, the input pinned above the keyboard
    const vv = window.visualViewport;
    const kb = () => { if (vv) dlg.style.setProperty('--kb', `${Math.max(0, Math.round(innerHeight - vv.height - vv.offsetTop))}px`); };
    if (vv) { vv.addEventListener('resize', kb); vv.addEventListener('scroll', kb); }
    dlg.addEventListener('click', e => { if (e.target === dlg) api.close(); });
    dlg.addEventListener('close', () => {
      if (vv) { vv.removeEventListener('resize', kb); vv.removeEventListener('scroll', kb); }
      dlg.remove();
      cur = null;
      say = () => {};
      if (opener && opener.isConnected && typeof opener.focus === 'function') opener.focus({ preventScroll: true });
    });
    const api = { el: dlg, input, close: () => { if (dlg.open) dlg.close(); } };
    cur = api;
    doc.body.append(dlg);
    dlg.showModal();
    input.value = initial || '';
    input.focus();
    let pending = 0;
    load(() => { if (!pending) pending = requestAnimationFrame(() => { pending = 0; if (dlg.open) paint(); }); });
    paint();
    return api;
  }

  UI.palette = palette;
})();
