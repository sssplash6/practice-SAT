/* ============================================================================
   SAT Freshman -- plan-ui.js: the study plan's shared pieces (S7; spec 3.6 3f,
   plan.md L4, L8, L10, L11, L16, L21; decision 7)

   Loaded after ui.js and kit.js by /plan/ and by any page that shows plan tasks
   (Today's plan card, the session summary). Adds to window.UI. Its styles are
   injected once, on ui.css tokens. It fetches nothing: the page owns the calls.

   UI.taskRow(host, task, o) -> {el, task, set(task), busy(on), error(text)}
     task  one Task of GET /api/plan (id, kind, title, detail, topics, count, minutes,
           status, answered, total, result, why [{text, href}], start, type, subject)
     o     readonly  no actions at all (the landing, a shared view)
           primary   the action is the orange pill (the day's first undone counted task)
           future    a later day: "Start early"      past  a frozen day: Review only
           compact   one line, no why and no receipt (Today's list)
           open      'skip' | 'done': the inline reason chips or Did it elsewhere? form, shown
           on(action, task, arg) -> Promise, the page's handler for:
             start · tick {done} · skip · reason {reason} · done {minutes, where} · undo
             · again {kind: misses | more | harder} · review
           menu(task) -> [UI.menu items]   the ⋯ items (Move to…, Swap topics, Edit, Remove)
           extra(task) -> Node | null        a page's own line under the row (R&W Log misses)
           drag(task, pointerdown event)     a handle to drag the row onto another day (L12;
                                             a fine pointer only: touch long-presses, keys use M)
     A rejected on() keeps the row as it was and says why inside it.
   UI.taskTag(task) -> 'Focus' | 'Warm-up' | ...      UI.taskQuestion(task) -> bool
   UI.weekPlanner(host, week) -> {el, value()}   next week's plan, hosted by U14's sheet
     week  {plan, monday, days [{date, kind, minutes, topics, test}], swaps [{topic, name, gain}],
            focus [topic], onSaved(reply)}
     "Looks good" sends PUT /api/plan/{plan}/week/{monday} {days, swap?}.
   ========================================================================== */
(() => {
  'use strict';
  const UI = window.UI = window.UI || {};
  const doc = document;
  const h = (tag, attrs = {}, ...kids) => {
    const e = doc.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kids.flat(3)) if (c !== null && c !== undefined && c !== false) e.append(c instanceof Node ? c : String(c));
    return e;
  };
  const name = slug => (UI.TOPIC && UI.TOPIC[slug] && UI.TOPIC[slug].short) || String(slug || '').replace(/_/g, ' ');
  const mins = m => (UI.dur ? UI.dur(m) : `${Math.round(m)}m`);
  const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;

  const CSS = `
  .trows { display: grid; gap: 0; }
  .trow { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto; gap: 4px 12px; align-items: start;
    padding: 14px 0; border-top: 1px solid var(--line); }
  .trows > .trow:first-child { border-top: 0; }
  .trow-box { appearance: none; width: 28px; height: 28px; margin-top: 1px; border-radius: 50%; border: 1.5px solid var(--faint);
    background: var(--paper); display: grid; place-items: center; cursor: pointer; color: transparent; padding: 0; position: relative; }
  .trow-box::before { content: ""; position: absolute; inset: -8px; }
  .trow-box svg { width: 16px; height: 16px; }
  .trow[data-status="active"] .trow-box { background: linear-gradient(90deg, var(--ink) 50%, var(--paper) 50%); border-color: var(--ink); }
  .trow[data-status="done"] .trow-box, .trow[data-status="marked"] .trow-box, .trow[data-status="made_up"] .trow-box { background: var(--ink); border-color: var(--ink); color: var(--on-ink); }
  .trow[data-status="skipped"] .trow-box::after { content: ""; width: 12px; height: 1.5px; background: var(--soft); }
  .trow[data-status="moved"] .trow-box::after { content: "\\2192"; color: var(--soft); font: 600 13px var(--font); }
  .trow[data-status="skipped"], .trow[data-status="moved"] { opacity: .55; }
  .trow[data-status="skipped"]:focus-within, .trow[data-status="moved"]:focus-within { opacity: 1; }
  .trow-box:disabled { cursor: default; }
  .trow-main { min-width: 0; display: grid; gap: 4px; }
  .trow-head { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; }
  .trow-title { font: 600 15px/1.3 var(--font); color: var(--ink); }
  .trow[data-next] .trow-title { font-weight: 700; }
  .trow-detail { margin: 0; font: 400 13.5px/1.45 var(--font); color: var(--ink); display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: center; }
  .trow-detail .chip { height: 28px; padding: 0 9px 0 6px; gap: 6px; font-size: 13px; }
  .trow-detail .chip .glyph { width: 16px; height: 16px; }
  .trow-meta { margin: 0; font: 500 12.5px/1.4 var(--mono); color: var(--soft); font-variant-numeric: tabular-nums; }
  .trow-meta b { font-weight: 500; color: var(--ink); }
  .trow-why { margin: 2px 0 0; padding: 0; list-style: none; display: grid; gap: 3px; font: 400 13px/1.45 var(--font); color: var(--soft); }
  .trow-why a { color: inherit; text-decoration: underline; text-decoration-color: var(--line); text-underline-offset: 3px; }
  .trow-why a:hover { color: var(--ink); }
  .trow-act { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; justify-content: flex-end; }
  .trow-act .quiet { min-height: 32px; }
  .trow-more { width: 32px; height: 32px; }
  .trow-grip { display: none; width: 18px; height: 22px; margin-left: -4px; place-items: center; color: var(--faint); cursor: grab; touch-action: none; }
  .trow:hover .trow-grip { color: var(--soft); }
  @media (hover: hover) and (pointer: fine) { .trow-grip { display: inline-grid; } }
  .trow-sub { display: flex; flex-wrap: wrap; gap: 6px 8px; align-items: center; margin-top: 4px; }
  .trow-sub .k { margin-right: 2px; }
  .trow-sub .field { width: 76px; height: 34px; font: 500 14px var(--mono); text-align: center; }
  .trow-sub .chips > button { min-height: 34px; padding: 0 12px; font-size: 13px; }
  .trow-err { margin: 2px 0 0; font: 500 13px/1.4 var(--font); color: var(--ink); }
  .trow-err:empty { display: none; }
  .trow-err::before { content: ""; display: inline-block; width: 7px; height: 7px; margin-right: 7px; border-radius: 50%; background: var(--ink); vertical-align: 1px; }
  .trow[aria-busy="true"] .trow-act { opacity: .5; pointer-events: none; }
  .trow.compact { padding: 9px 0; }
  @media (max-width: 759px) {
    .trow { grid-template-columns: 32px minmax(0, 1fr); }
    .trow-act { grid-column: 2; justify-content: flex-start; }
    .trow-act .quiet, .trow-act .btn, .trow-more { min-height: var(--touch); }
    .trow-more { width: var(--touch); }
  }
  .wplan { display: grid; gap: 14px; }
  .wplan-days { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 6px; }
  .wplan-day { display: grid; gap: 6px; align-content: start; padding: 10px 8px; border-radius: 10px; background: var(--tile); min-width: 0; }
  .wplan-day[data-off] { background: repeating-linear-gradient(-45deg, var(--tile) 0 5px, var(--mat) 5px 6px); }
  .wplan-day .k { letter-spacing: .08em; }
  .wplan-day p { margin: 0; font: 400 12px/1.35 var(--font); color: var(--ink); overflow-wrap: anywhere; }
  .wplan-day select { width: 100%; height: 32px; border-radius: 8px; border: 0; background: var(--paper); font: 500 12.5px var(--mono); }
  .wplan-day .btn.sm { width: 100%; justify-content: center; padding: 0 4px; }
  @media (max-width: 759px) { .wplan-days { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
  `;
  if (!doc.getElementById('plan-ui-css')) doc.head.append(h('style', { id: 'plan-ui-css' }, CSS));

  const TAGS = { recheck: 'Warm-up', fix: 'Mistakes', learn: 'Learn it', check: 'Check', habit: 'Habit', pace: 'Pace',
    map: 'Map', focus: 'Focus', test: 'Test', sweep: 'Sweep', words: 'Words', qotd: 'Extra', challenge: 'Extra', extra: 'Extra' };
  function taskTag(t) {
    if (t.kind === 'test') return t.rehearsal ? 'Rehearsal' : (t.start && t.start.body && t.start.body.kind === 'twin') || /^Checkpoint/.test(t.title || '') ? 'Checkpoint' : 'Test';
    if (t.kind === 'custom') return t.type === 'rw' || t.subject === 'rw' ? 'R&W' : 'Your own';
    return TAGS[t.kind] || 'Extra';
  }
  // a task the student answers here (a drill, a test, a Words run), against one done on their own
  const taskQuestion = t => !!t.start && t.kind !== 'custom';
  const DONE = new Set(['done', 'marked', 'made_up']);
  const TOPIC_KINDS = new Set(['focus', 'map', 'learn', 'check', 'pace', 'habit']);
  const CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const GRIP = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><g fill="currentColor"><circle cx="9" cy="6" r="1.6"/><circle cx="15" cy="6" r="1.6"/><circle cx="9" cy="12" r="1.6"/><circle cx="15" cy="12" r="1.6"/><circle cx="9" cy="18" r="1.6"/><circle cx="15" cy="18" r="1.6"/></g></svg>';
  const DOTS = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="5.5" cy="12" r="2" fill="currentColor"/><circle cx="12" cy="12" r="2" fill="currentColor"/><circle cx="18.5" cy="12" r="2" fill="currentColor"/></svg>';
  const WHERE = [['bluebook', 'Bluebook'], ['khan', 'Khan Academy'], ['book', 'A book'], ['tutor', 'A tutor'], ['other', 'Other']];
  const WHERE_LABEL = Object.fromEntries(WHERE);

  function detailOf(t, compact) {
    if (t.topics && t.topics.length && TOPIC_KINDS.has(t.kind)) return compact || !UI.chip ? t.topics.map(name).join(', ') : t.topics.map(s => UI.chip(s));
    // a zero is not news (decision 7): "0 due · due first" says nothing
    const text = String(t.detail || '').split(' · ').filter(x => !/^0 /.test(x) && x !== 'due first').join(' · ');
    return text || null;
  }
  function metaOf(t) {
    const bits = [];
    if (t.kind === 'words') bits.push(`${Math.round(t.minutes)} min`);
    else if (taskQuestion(t) && t.count) bits.push(plural(t.count, 'question'), `${Math.round(t.minutes)} min`);
    else if (t.minutes) bits.push(`${Math.round(t.minutes)} min`);
    const d = t.difficulty || (t.start && t.start.body && t.start.body.tiers);
    if (Array.isArray(d) && d.length && d.length < 3) bits.push(d.map(x => x[0].toUpperCase() + x.slice(1)).join('–'));
    const body = (t.start && t.start.body) || {};
    if (t.timed || body.timing === 'pace' || body.timed) bits.push('Timed');
    if (t.aim) bits.push(`aim ${Math.round(t.aim / 10) * 10}+`);
    if (t.kind === 'custom' && t.repeat === 'study_days') bits.push('every study day');
    return bits.join(' · ');
  }
  function receiptOf(t) {
    const r = t.result;
    const m = t.minutes_done || (r && r.minutes), where = t.where || (r && r.where);
    if (t.status === 'marked' && m) return `Marked done · ${Math.round(m)} min${where && WHERE_LABEL[where] ? ` in ${WHERE_LABEL[where]}` : ''}`;
    if (t.status === 'marked') return 'Marked done';
    if (!r || !r.asked) return t.status === 'made_up' ? 'Made up' : null;
    const bits = [`${r.right} of ${r.asked} right`];
    if (r.fixed && r.fixed.length) bits.push(`${r.fixed.length} fixed`);
    if (r.opened && r.opened.length) bits.push(plural(r.opened.length, 'new mistake'));
    if (r.ms) bits.push(mins(r.ms / 60000));
    if (r.verdict) bits.push(r.verdict === 'beat' ? 'beat the aim' : r.verdict === 'under' ? 'under the aim' : 'within the band');
    return bits.join(' · ');
  }

  function taskRow(host, task, o = {}) {
    const el = h('div', { class: 'trow' + (o.compact ? ' compact' : '') });
    let t = task, open = o.open || null;       // open: the inline form showing (skip | done)
    const err = h('p', { class: 'trow-err', role: 'status' });
    const fail = e => { err.textContent = (e && e.rowText) || 'Couldn’t save that. Try again.'; };
    async function run(action, arg, btn) {
      if (!o.on) return;
      err.textContent = '';
      el.setAttribute('aria-busy', 'true');
      if (btn) btn.setAttribute('aria-busy', 'true');
      try { await o.on(action, t, arg); }
      catch (e) { if (!(e && e.offline)) fail(e); }
      finally { el.removeAttribute('aria-busy'); if (btn) btn.removeAttribute('aria-busy'); }
    }
    function draw() {
      const q = taskQuestion(t), done = DONE.has(t.status), own = t.kind === 'custom';
      el.dataset.status = t.status || 'todo';
      el.dataset.kind = t.kind;
      el.toggleAttribute('data-next', !!o.primary);
      const box = h('button', { type: 'button', class: 'trow-box', role: 'checkbox', 'aria-checked': String(done),
        'aria-label': `${t.title}: ${done ? 'mark as not done' : 'mark as done'}`, disabled: o.readonly || o.past || (!t.counted && !own && t.kind !== 'custom') || null });
      box.innerHTML = CHECK;
      box.addEventListener('click', () => {
        if (own) return run('tick', { done: !done });
        if (t.status === 'marked') return run('undo');
        if (done) return;
        open = open === 'done' ? null : 'done';
        draw();
      });
      const grip = o.drag && !o.readonly && !o.past && !done && t.status !== 'skipped' && t.status !== 'moved'
        ? h('span', { class: 'trow-grip', 'aria-hidden': 'true', title: 'Drag to another day' }) : null;
      if (grip) { grip.innerHTML = GRIP; grip.addEventListener('pointerdown', e => o.drag(t, e)); }
      const head = h('div', { class: 'trow-head' }, grip, h('span', { class: 'trow-title', text: t.title }),
        h('span', { class: 'badge soft', text: taskTag(t) }),
        t.status === 'skipped' && h('span', { class: 'badge line', text: 'Skipped' }),
        t.status === 'moved' && t.moved_to && h('span', { class: 'meta', text: `Moved to ${UI.date ? UI.date(t.moved_to, 'long') : t.moved_to}` }));
      const main = h('div', { class: 'trow-main' }, head);
      const det = detailOf(t, o.compact);
      if (det) main.append(h('p', { class: 'trow-detail' }, det));
      const meta = o.compact ? '' : metaOf(t);
      const rec = !o.compact && done ? receiptOf(t) : null;
      if (rec) main.append(h('p', { class: 'trow-meta' }, h('b', { text: rec })));
      else if (meta) main.append(h('p', { class: 'trow-meta', text: meta }));
      const why = (t.why || []).filter(w => w && (w.text || typeof w === 'string'));
      let whyList = null;
      if (why.length && !o.compact) {
        whyList = h('ul', { class: 'trow-why', id: `why-${String(t.id).replace(/[^\w-]/g, '_')}`, hidden: !o.whyOpen || null },
          why.map(w => typeof w === 'string' ? h('li', { text: w }) : h('li', {}, w.href ? h('a', { href: w.href, text: w.text }) : w.text)));
        main.append(whyList);
      }
      if (open === 'skip') main.append(h('div', { class: 'trow-sub' }, h('span', { class: 'k', text: 'Why?' }),
        [['no_time', 'No time'], ['too_hard', 'Too hard'], ['know', 'I know this']].map(([r, label]) =>
          h('button', { type: 'button', class: 'btn sm', text: label, onclick: e => { open = null; run('reason', { reason: r }, e.currentTarget); } })),
        h('button', { type: 'button', class: 'quiet', text: 'Close', onclick: () => { open = null; draw(); } })));
      if (open === 'done') {
        const f = h('input', { type: 'number', class: 'field', min: '1', max: '240', value: String(Math.max(1, Math.round(t.minutes || 20))), inputmode: 'numeric', 'aria-label': 'Minutes you spent' });
        let where = null;
        const chips = UI.chips ? UI.chips(null, WHERE.map(([value, label]) => ({ value, label })), { label: 'Where', value: null, onChange: v => { where = v; } }) : null;
        const save = h('button', { type: 'button', class: 'btn sm ink', text: 'Save', onclick: e => {
          const m = Math.round(+f.value);
          if (!(m >= 1 && m <= 240)) { f.setAttribute('aria-invalid', 'true'); err.textContent = 'Minutes from 1 to 240.'; return; }
          open = null; run('done', { minutes: m, where }, e.currentTarget);
        } });
        main.append(h('div', { class: 'trow-sub' }, h('span', { class: 'k', text: 'Did it elsewhere?' }), f, h('span', { class: 'meta', text: 'min' }),
          chips && chips.el, save, h('button', { type: 'button', class: 'quiet', text: 'Cancel', onclick: () => { open = null; draw(); } })));
      }
      if (o.extra && !o.readonly) { const x = o.extra(t); if (x) main.append(x); }
      main.append(err);
      const act = h('div', { class: 'trow-act' });
      if (!o.readonly) {
        if (o.past) {
          if (t.session && o.on) act.append(h('button', { type: 'button', class: 'quiet', text: 'Review', onclick: () => run('review') }));
        } else if (done) {
          if (t.session) act.append(h('button', { type: 'button', class: 'quiet', text: 'Review', onclick: () => run('review') }));
          const miss = t.result && t.result.asked ? t.result.asked - t.result.right : 0;
          if (q && t.kind !== 'test' && t.kind !== 'words') {
            if (miss > 0 && t.session) act.append(h('button', { type: 'button', class: 'btn sm', text: `Again · the ${miss} you missed`, onclick: e => run('again', { kind: 'misses' }, e.currentTarget) }));
            act.append(h('button', { type: 'button', class: 'quiet', text: 'Again · 10 more', onclick: e => run('again', { kind: 'more' }, e.currentTarget) }));
            if (t.result && t.result.asked && t.result.right / t.result.asked >= 0.9 && !(t.difficulty || []).includes('hard'))
              act.append(h('button', { type: 'button', class: 'quiet', text: 'Again · harder', onclick: e => run('again', { kind: 'harder' }, e.currentTarget) }));
          }
          if (t.status === 'marked' || own) act.append(h('button', { type: 'button', class: 'quiet', text: 'Undo', onclick: e => run('undo', null, e.currentTarget) }));
        } else if (t.status === 'skipped' || t.status === 'moved') {
          act.append(h('button', { type: 'button', class: 'quiet', text: 'Undo', onclick: e => run('undo', null, e.currentTarget) }));
        } else if (q) {
          const resume = t.status === 'active' && t.total;
          const label = o.future ? 'Start early' : resume ? `Resume · ${t.answered} of ${t.total}` : t.kind === 'words' ? 'Start' : 'Start';
          act.append(h('button', { type: 'button', class: o.primary ? 'pill sm' : o.future ? 'quiet' : 'btn sm', text: label, onclick: e => run('start', null, e.currentTarget) }));
          act.append(h('button', { type: 'button', class: 'quiet', text: 'Skip', 'aria-expanded': open === 'skip' ? 'true' : null,
            onclick: e => run('skip', null, e.currentTarget) }));
          act.append(h('button', { type: 'button', class: 'quiet', text: 'Mark done', 'aria-expanded': String(open === 'done'),
            onclick: () => { open = open === 'done' ? null : 'done'; draw(); } }));
        } else if (own && t.kind === 'custom' && t.counted !== false) {
          act.append(h('button', { type: 'button', class: 'quiet', text: 'Skip', onclick: e => run('skip', null, e.currentTarget) }));
        }
        if (whyList) {
          const wb = h('button', { type: 'button', class: 'quiet', text: 'Why', 'aria-expanded': String(!whyList.hidden), 'aria-controls': whyList.id });
          wb.addEventListener('click', () => { whyList.hidden = !whyList.hidden; o.whyOpen = !whyList.hidden; wb.setAttribute('aria-expanded', String(!whyList.hidden)); });
          act.append(wb);
        }
        const items = !o.past && o.menu ? (o.menu(t) || []).filter(Boolean) : [];
        if (items.length && UI.menu) {
          const more = h('button', { type: 'button', class: 'quiet trow-more', 'aria-label': `More for ${t.title}`, 'aria-haspopup': 'menu' });
          more.innerHTML = DOTS;
          more.addEventListener('click', () => UI.menu(more, o.menu(t).filter(Boolean), { label: t.title }));
          act.append(more);
        }
      } else if (whyList) whyList.hidden = true;
      el.replaceChildren(box, main, act);
    }
    draw();
    if (host) host.append(el);
    return {
      el, get task() { return t; },
      set(nt) { t = nt; draw(); },
      busy(on) { if (on) el.setAttribute('aria-busy', 'true'); else el.removeAttribute('aria-busy'); },
      error(text) { err.textContent = text || ''; },
      openSkip() { open = 'skip'; draw(); },
    };
  }

  function weekPlanner(host, week = {}) {
    const days = (week.days || []).map(d => ({ ...d, change: 0, off: d.kind === 'off', short: false }));
    let swap = null;
    const el = h('div', { class: 'wplan' });
    const grid = h('div', { class: 'wplan-days' });
    function drawDays() {
      grid.replaceChildren(...days.map(d => {
        const study = ['practice', 'test', 'off'].includes(d.kind);
        const tile = h('div', { class: 'wplan-day', 'data-off': d.off ? '' : null },
          h('span', { class: 'k', text: UI.date ? UI.date(d.date, 'long').replace(/,.*/, '') + ' ' + d.date.slice(8).replace(/^0/, '') : d.date }),
          h('p', { text: d.off ? 'Busy' : d.kind === 'test' ? 'Test day' : study ? (d.topics || []).map(name).join(', ') || 'Practice' : 'Rest' }));
        if (study) {
          const base = d.minutes || 0;
          const sel = h('select', { 'aria-label': `Minutes on ${d.date}`, disabled: d.off || d.short || null },
            [-15, 0, 15].map(k => h('option', { value: String(k), selected: d.change === k || null, text: k ? `${k > 0 ? '+' : '−'}15 · ${Math.max(5, base + k)}m` : `${base}m` })));
          sel.addEventListener('change', () => { d.change = +sel.value; });
          const busy = h('button', { type: 'button', class: 'btn sm', 'aria-pressed': String(d.off), text: 'Busy', onclick: () => { d.off = !d.off; if (d.off) d.short = false; drawDays(); } });
          const short = h('button', { type: 'button', class: 'btn sm', 'aria-pressed': String(d.short), text: 'Short', disabled: d.off || null, onclick: () => { d.short = !d.short; drawDays(); } });
          tile.append(sel, busy, short);
        }
        return tile;
      }));
    }
    drawDays();
    el.append(grid);
    if ((week.swaps || []).length && (week.focus || []).length) {
      const from = h('select', { class: 'field sm', 'aria-label': 'Focus skill to swap out' }, week.focus.map(t => h('option', { value: t, text: name(t) })));
      const to = h('select', { class: 'field sm', 'aria-label': 'Skill to put on Focus' },
        h('option', { value: '', text: 'Keep' }), week.swaps.map(s => h('option', { value: s.topic, text: `${s.name || name(s.topic)}${s.gain ? ` · ≈ +${s.gain}` : ''}` })));
      const sync = () => { swap = to.value ? { from: from.value, to: to.value } : null; };
      from.addEventListener('change', sync); to.addEventListener('change', sync);
      el.append(h('div', { class: 'trow-sub' }, h('span', { class: 'label', text: 'Swap a focus skill' }), from, h('span', { text: '→' }), to));
    }
    const value = () => ({
      days: days.filter(d => d.off !== (d.kind === 'off') || d.change || d.short).map(d => {
        const out = { date: d.date };
        if (d.off !== (d.kind === 'off')) out.off = d.off;
        if (d.short) out.minutes = 15;
        else if (d.change) out.minutes = Math.max(5, (d.minutes || 0) + d.change);
        return out;
      }),
      ...(swap ? { swap } : {}),
    });
    const err = h('p', { class: 'trow-err', role: 'status' });
    const save = h('button', { type: 'button', class: 'pill sm', text: 'Looks good' });
    save.addEventListener('click', async () => {
      if (!week.plan || !UI.api) return;
      err.textContent = '';
      save.setAttribute('aria-busy', 'true');
      try {
        const r = await UI.api(`/plan/${encodeURIComponent(week.plan)}/week/${week.monday}`, { method: 'PUT', body: value() });
        if (UI.toast) UI.toast('Next week saved');
        if (week.onSaved) week.onSaved(r);
      } catch (e) { err.textContent = (e && e.message) || 'Couldn’t save the week. Try again.'; }
      finally { save.removeAttribute('aria-busy'); }
    });
    el.append(h('div', { class: 'trow-sub' }, save), err);
    if (host) host.append(el);
    return { el, value };
  }

  Object.assign(UI, { taskRow, taskTag, taskQuestion, weekPlanner });
})();
