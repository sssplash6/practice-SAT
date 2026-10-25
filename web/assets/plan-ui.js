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
           led       the page's own Start button starts this row: no second Start, the
                     row shows as the one up next
           n         a number in place of the checkbox (a preview's rows, readonly)
           future    a later day: "Start early"      past  a frozen day: Review only
           compact   one line, no why and no receipt (Today's list)
           open      'skip' | 'done': the inline reason chips or Did it elsewhere? form, shown
           on(action, task, arg) -> Promise, the page's handler for:
             start · tick {done} · skip · reason {reason} · done {minutes, where} · undo
             · again {kind: misses | more | harder} · review
           menu(task) -> [UI.menu items]   the page's ⋯ items (Move to…, Swap topics, Edit,
                                             Remove), after the row's own Skip, Mark done and Why
           extra(task) -> Node | null        a page's own line under the row (R&W Log misses)
           drag(task, pointerdown event)     a handle to drag the row onto another day (L12;
                                             a fine pointer only: touch long-presses, keys use M)
     A rejected on() keeps the row as it was and says why inside it.
   UI.taskTag(task) -> 'Focus' | 'Warm-up' | ...      UI.taskQuestion(task) -> bool
   UI.infoTip(text, label) -> button   the shared "?" (UI.why, kit.js) under its old name: the plan's
                                        callers use UI.why; label 'About X' becomes its about 'X'
   UI.weekPlanner(host, week) -> {el, value(), save(), error(text)}   a week's shape (Plan › Shape week)
     week  {plan, monday, today, start, last, days [{date, kind, minutes, topics, test}],
            swaps [{topic, name, gain}], focus [topic], button, onSaved(reply)}
     save(): a week not yet begun goes as PUT /api/plan/{plan}/week/{monday} {days}; otherwise each changed day
     as PUT /api/plan/{plan}/day/{date}; a swap puts the new skill in place of the old on each day that holds it.
     button: false leaves the Save to the host (a sheet's own action).
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
  const name = slug => (UI.topicName ? UI.topicName(slug) : (UI.TOPIC && UI.TOPIC[slug] && UI.TOPIC[slug].short) || String(slug || '').replace(/_/g, ' '));
  const mins = m => (UI.dur ? UI.dur(m) : `${Math.round(m)}m`);
  const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
  // key hints only where there is a keyboard
  const fine = () => { try { return matchMedia('(hover: hover) and (pointer: fine)').matches; } catch (_) { return false; } };
  const phone = () => { try { return matchMedia('(max-width: 759px)').matches; } catch (_) { return false; } };

  const CSS = `
  .trows { display: grid; gap: 0; }
  .trow { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto; gap: 4px 12px; align-items: start;
    padding: 10px 0; border-top: 1px solid var(--line); position: relative; }
  .trows > .trow:first-child { border-top: 0; }
  .trow-box { appearance: none; width: 28px; height: 28px; margin-top: 1px; border-radius: 50%; border: 1.5px solid var(--faint);
    background: var(--paper); display: grid; place-items: center; cursor: pointer; color: transparent; padding: 0; position: relative; }
  .trow-box::before { content: ""; position: absolute; inset: -8px; }
  .trow-box svg { width: 16px; height: 16px; }
  .trow-box { transition: background-color .16s var(--ease), border-color .16s var(--ease), color .16s var(--ease); }
  @media (hover: hover) and (pointer: fine) { .trow-box:not(:disabled):hover { border-color: var(--ink); } }
  .trow-kind { display: inline-grid; place-items: center; width: 16px; height: 16px; flex: none; color: var(--soft); align-self: center; }
  .trow-kind svg { width: 16px; height: 16px; }
  .trow-head .trow-kind + .trow-title { margin-left: -2px; }
  .trow[data-status="active"] .trow-box { background: linear-gradient(90deg, var(--ink) 50%, var(--paper) 50%); border-color: var(--ink); }
  .trow[data-status="done"] .trow-box, .trow[data-status="marked"] .trow-box, .trow[data-status="made_up"] .trow-box { background: var(--ink); border-color: var(--ink); color: var(--on-ink); }
  .trow[data-status="skipped"] .trow-box::after { content: ""; width: 12px; height: 1.5px; background: var(--soft); }
  .trow[data-status="moved"] .trow-box::after { content: "\\2192"; color: var(--soft); font: 600 13px var(--font); }
  .trow[data-status="skipped"], .trow[data-status="moved"] { opacity: .55; }
  .trow[data-status="skipped"]:focus-within, .trow[data-status="moved"]:focus-within { opacity: 1; }
  .trow-box:disabled { cursor: default; }
  .trow-main { min-width: 0; display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 12px; }
  .trow-main > .trow-detail, .trow-main > .trow-why, .trow-main > .trow-sub, .trow-main > .trow-err, .trow-main > .help { flex: 1 0 100%; }
  .trow-main > .trow-detail { display: none; }
  /* only the next task shows its detail on a mouse (rows never change height under a drag); a focused row, and every
     row on a touch screen, shows it too, so nothing lives only in the row's hover title */
  .trow[data-next] .trow-main > .trow-detail, .trow:focus-within .trow-main > .trow-detail { display: flex; }
  @media (pointer: coarse) { .trow-main > .trow-detail { display: flex; } }
  /* one line: a long title wraps inside itself, never under its kind mark */
  .trow-head { display: flex; align-items: center; gap: 4px 8px; min-height: 28px; }
  .trow-head > :not(.trow-title) { flex: none; }
  .trow-n { width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center; background: var(--tile-2);
    font: 500 12.5px var(--font); font-variant-numeric: tabular-nums; color: var(--ink); }
  .trow-title { min-width: 0; font: 600 14.5px/1.35 var(--font); color: var(--ink); }
  .trow-detail { margin: 0; font: 400 12.5px/1.45 var(--font); color: var(--ink); display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: center; }
  .trow-detail .chip { height: 28px; padding: 0 9px 0 6px; gap: 6px; }
  .trow-detail .chip .glyph { width: 16px; height: 16px; }
  .trow-meta { margin: 0; font: 500 12.5px/1.4 var(--font); color: var(--soft); font-variant-numeric: tabular-nums; }
  .trow-meta b { font-weight: 500; color: var(--ink); }
  .trow-why { margin: 2px 0 0; padding: 0; list-style: none; display: grid; gap: 4px; font: 400 12.5px/1.45 var(--font); color: var(--soft); }
  .trow-why a { color: inherit; text-decoration: underline; text-decoration-color: var(--line); text-underline-offset: 3px; }
  .trow-why a:hover { color: var(--ink); }
  .trow-act { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; justify-content: flex-end; margin-top: -2px; }
  /* the grip sits in the card's left padding (16px), shown on hover, so every title starts at the same x */
  .trow-grip { display: none; position: absolute; left: -16px; top: 13px; width: 16px; height: 22px; place-items: center; color: var(--soft); cursor: grab; touch-action: none; opacity: 0; transition: opacity .12s; }
  .trow-grip svg { width: 16px; height: 16px; }
  .trow:hover .trow-grip, .trow:focus-within .trow-grip { opacity: 1; }
  @media (hover: hover) and (pointer: fine) { .trow-grip { display: grid; } }
  .trow-sub { display: flex; flex-wrap: wrap; gap: 6px 8px; align-items: center; margin-top: 4px; }
  .trow-sub .k { margin-right: 2px; }
  .trow-sub .field { width: 76px; height: 36px; font: 500 16px var(--font); font-variant-numeric: tabular-nums; text-align: center; }
  .trow-sub .chips > button { min-height: 34px; padding: 0 12px; }
  .trow-err { margin: 2px 0 0; font: 500 12.5px/1.4 var(--font); color: var(--ink); }
  .trow-err:empty { display: none; }
  .trow-err::before { content: ""; display: inline-block; width: 7px; height: 7px; margin-right: 7px; border-radius: 50%; background: var(--ink); vertical-align: 1px; }
  .trow[aria-busy="true"] .trow-act { opacity: .5; pointer-events: none; }
  .trow.compact { padding: 8px 0; }
  @media (max-width: 759px) {
    .trow { grid-template-columns: 32px minmax(0, 1fr); }
    .trow-act { grid-column: 2; justify-content: flex-start; }
    .trow-act .quiet, .trow-act .btn, .trow-act .pill, .trow-more, .trow-sub .quiet, .trow-sub .btn, .trow-detail .quiet { min-height: var(--touch); }
    .trow-more { width: var(--touch); }
    .trow-act { margin-top: 0; }
    /* the ⋯ sits top right; the line under the row holds only Start, Review or Undo */
    .trow-act .trow-more { position: absolute; top: 6px; right: -6px; }
    .trow:has(.trow-more) .trow-main { padding-right: 40px; }
    .trow-act:has(> .trow-more:only-child) { height: 0; }
  }
  .wplan { display: grid; gap: 16px; }
  .wplan-key { margin: -4px 0 0; }
  /* the week as seven bars (a day's minutes after the changes, a busy day a hatched stub) under its total */
  .wplan-week { display: grid; gap: 8px; }
  .wplan-total { margin: 0; display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
    font: 600 14.5px var(--font); font-variant-numeric: tabular-nums; color: var(--ink-strong, var(--ink)); }
  .wplan-chart { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 8px; }
  .wplan-bar { display: grid; grid-template-rows: 56px auto; gap: 4px; justify-items: center; }
  /* the planned week in graphite; a day you change turns ink, so the chart shows the change */
  .wplan-bar > i { align-self: end; width: 100%; max-width: 28px; border-radius: 6px 6px 3px 3px; background: color-mix(in srgb, var(--ink) 22%, transparent);
    transition: height .2s var(--ease), background-color .2s var(--ease); }
  .wplan-bar[data-ch] > i { background: var(--ink); }
  .wplan-bar[data-zero] > i { height: 2px !important; background: var(--line); }
  .wplan-bar[data-off] > i { background: repeating-linear-gradient(-45deg, var(--mat) 0 1.5px, transparent 1.5px 4px), var(--well); box-shadow: inset 0 0 0 1px var(--line); }
  .wplan-bar[data-past] > i { background: color-mix(in srgb, var(--ink) 10%, transparent); }
  .wplan-bar > b { font: 500 11.5px var(--font); color: var(--soft); }
  .wplan-bar[data-ch] > b { color: var(--ink); font-weight: 600; }
  .wplan-days { display: grid; }
  .wplan-day { display: grid; grid-template-columns: 64px minmax(0, 1fr) auto; align-items: center; gap: 4px 12px; min-height: var(--row-h); padding: 6px 0; border-top: 1px solid var(--line); }
  .wplan-day:first-child { border-top: 0; }
  .wplan-d { font: 600 14px var(--font); font-variant-numeric: tabular-nums; }
  .wplan-w { min-width: 0; font: 400 12.5px/1.4 var(--font); color: var(--soft); overflow-wrap: anywhere; }
  .wplan-day[data-past] .wplan-d { color: var(--soft); font-weight: 500; }
  .wplan-c { justify-self: end; }
  .wplan-c.seg > button { padding: 0 10px; font-variant-numeric: tabular-nums; }
  /* the day as planned: the shared thumb, its label a step quieter than a change (as the builder's Normal) */
  .wplan-c.seg > [data-base][aria-pressed="true"] { font-weight: 500; }
  .wplan-swap { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding-top: 12px; border-top: 1px solid var(--line); }
  .wplan-swap .label { flex: 1 0 100%; margin: 0; }
  .wplan-to { display: inline-grid; color: var(--soft); }
  .wplan-to svg { width: 16px; height: 16px; }
  .wplan-foot { display: flex; justify-content: flex-end; }
  @media (max-width: 759px) {
    .wplan-day { grid-template-columns: 56px minmax(0, 1fr); }
    .wplan-c { grid-column: 1 / -1; justify-self: start; }
  }
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
  const ic = (n, size) => (UI.icon ? UI.icon(n, size) : '');
  // a task's kind as a 16px mark before its title (its word stays in the meta line, or for screen readers)
  const KIND_ICON = { recheck: 'again', fix: 'fix', learn: 'learn', check: 'twin', habit: 'trap', pace: 'clock', map: 'grid', focus: 'bolt',
    test: 'tests', sweep: 'clean', words: 'words', qotd: 'plus', challenge: 'plus', extra: 'plus' };
  const kindIcon = t => (t.kind === 'custom' ? (t.type === 'rw' || t.subject === 'rw' ? 'book' : 'pen') : KIND_ICON[t.kind] || 'plus');
  const WHERE = [['bluebook', 'Bluebook'], ['khan', 'Khan Academy'], ['book', 'A book'], ['tutor', 'A tutor'], ['other', 'Other']];
  const WHERE_LABEL = Object.fromEntries(WHERE);

  // the tag says the kind only when the title doesn't already ("Warm-up [Warm-up]" says it twice)
  const tagOf = t => { const g = taskTag(t), w = g.toLowerCase().replace(/s$/, ''); return String(t.title || '').toLowerCase().includes(w) ? null : g; };
  // Fix mistakes: how many, the names one tap away (its why list)
  const fixCount = t => ((t.start && t.start.body && t.start.body.ids) || []).length || String(t.detail || '').split(', ').filter(Boolean).length;
  function detailOf(t, compact) {
    // on a phone several topics are one line of text: their chips would stack one a line
    // (R&W skills have no sticker glyph: their names are words)
    if (t.topics && t.topics.length && TOPIC_KINDS.has(t.kind)) return compact || !UI.chip || t.subject === 'rw' || (t.topics.length > 1 && phone()) ? t.topics.map(name).join(', ') : t.topics.map(s => UI.chip(s));
    if (t.kind === 'fix' && t.detail) return plural(fixCount(t), 'open mistake');
    // a zero is not news (decision 7): "0 due · due first" says nothing
    const text = String(t.detail || '').split(' · ').filter(x => !/^0 /.test(x) && x !== 'due first')
      .map(x => x.replace(/^(\d+) fading$/, (m, n) => `${n} ${+n === 1 ? 'question' : 'questions'} you’re starting to forget`)).join(' · ');
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
      el.toggleAttribute('data-led', !!(o.primary && o.led));
      let box;
      if (o.n) box = h('span', { class: 'trow-n', 'aria-hidden': 'true', text: String(o.n) });
      else {
        box = h('button', { type: 'button', class: 'trow-box', role: 'checkbox', 'aria-checked': String(done),
          'aria-label': `${t.title}: ${done ? 'mark as not done' : 'mark as done'}`, disabled: o.readonly || o.past || (!t.counted && !own && t.kind !== 'custom') || null });
        box.append(ic('check', 16));
        box.addEventListener('click', () => {
          if (own) return run('tick', { done: !done });
          if (t.status === 'marked') return run('undo');
          if (done) return;
          open = open === 'done' ? null : 'done';
          draw();
        });
      }
      const grip = o.drag && !o.readonly && !o.past && !done && t.status !== 'skipped' && t.status !== 'moved'
        ? h('span', { class: 'trow-grip', 'aria-hidden': 'true', title: 'Drag to another day' }) : null;
      if (grip) { grip.append(ic('grip', 16)); grip.addEventListener('pointerdown', e => o.drag(t, e)); }
      // the kind: a mark before the title, and the meta line's first word ("Focus · 10 questions · 15 min") where the
      // title doesn't say it; a one-line row says it to a screen reader
      const tag = tagOf(t);
      const head = h('div', { class: 'trow-head' }, grip, h('span', { class: 'trow-kind', 'aria-hidden': 'true', title: taskTag(t) }, ic(kindIcon(t), 16)),
        h('span', { class: 'trow-title', text: t.title }), tag && o.compact && h('span', { class: 'sr', text: ` · ${tag}` }),
        t.status === 'skipped' && h('span', { class: 'badge line', text: 'Skipped' }),
        t.status === 'moved' && t.moved_to && h('span', { class: 'meta', text: `Moved to ${UI.date ? UI.date(t.moved_to, 'long') : t.moved_to}` }));
      const main = h('div', { class: 'trow-main' }, head);
      const why = (t.why || []).filter(w => w && (w.text || typeof w === 'string'));
      let whyList = null;
      if (why.length && !o.compact) {
        whyList = h('ul', { class: 'trow-why', id: `why-${String(t.id).replace(/[^\w-]/g, '_')}`, hidden: !o.whyOpen || null },
          why.map(w => typeof w === 'string' ? h('li', { text: w }) : h('li', {}, w.href ? h('a', { href: w.href, text: w.text }) : w.text)));
      }
      const toggleWhy = () => { if (!whyList) return; o.whyOpen = !!whyList.hidden; draw(); };
      const det = detailOf(t, o.compact);
      if (det) {
        const line = h('p', { class: 'trow-detail' }, det);
        // Fix mistakes names its mistakes one tap away
        if (t.kind === 'fix' && whyList && !o.readonly) line.append(h('button', { type: 'button', class: 'quiet', text: whyList.hidden ? 'Show' : 'Hide',
          'aria-expanded': String(!whyList.hidden), 'aria-controls': whyList.id, onclick: toggleWhy }));
        main.append(line);
        main.title = line.textContent.trim();   // the hidden detail of a row that isn't next
      }
      const meta = o.compact ? '' : [tag, metaOf(t)].filter(Boolean).join(' · ');
      const rec = !o.compact && done ? receiptOf(t) : null;
      if (rec) main.append(h('p', { class: 'trow-meta' }, tag ? `${tag} · ` : null, h('b', { text: rec })));
      else if (meta) main.append(h('p', { class: 'trow-meta', text: meta }));
      if (whyList) main.append(whyList);
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
      // one visible action (Start, Review, Undo), the rest in the ⋯ menu (decision 7); on a mouse, a row that isn't
      // next shows them while hovered or focused (.reveal, always on touch)
      const act = h('div', { class: o.primary ? 'trow-act' : 'trow-act reveal' });
      const mine = [];
      if (!o.readonly) {
        const miss = t.result && t.result.asked ? t.result.asked - t.result.right : 0;
        if (o.past) {
          if (t.session && o.on) act.append(h('button', { type: 'button', class: 'quiet', text: 'Review', onclick: () => run('review') }));
        } else if (done) {
          if (t.session) act.append(h('button', { type: 'button', class: 'quiet', text: 'Review', onclick: () => run('review') }));
          if (q && t.kind !== 'test' && t.kind !== 'words') {
            if (miss > 0 && t.session) act.append(h('button', { type: 'button', class: 'btn sm', text: `Again · the ${miss} you missed`, onclick: e => run('again', { kind: 'misses' }, e.currentTarget) }));
            mine.push({ label: 'Again · 10 more', onClick: () => run('again', { kind: 'more' }) });
            if (t.result && t.result.asked && t.result.right / t.result.asked >= 0.9 && !(t.difficulty || []).includes('hard'))
              mine.push({ label: 'Again · harder', onClick: () => run('again', { kind: 'harder' }) });
          }
          if (t.status === 'marked' || own) mine.push({ label: 'Undo', kbd: fine() ? 'S' : null, onClick: () => run('undo') });
        } else if (t.status === 'skipped' || t.status === 'moved') {
          act.append(h('button', { type: 'button', class: 'quiet', text: 'Undo', onclick: e => run('undo', null, e.currentTarget) }));
        } else if (q) {
          const resume = t.status === 'active' && t.total;
          const label = o.future ? 'Start' : resume ? `Resume · ${t.answered} of ${t.total}` : 'Start';
          // a phone shows every row's Start (no hover to hide them): a quiet word, so the day's own Start stays the one button
          if (!(o.primary && o.led)) act.append(h('button', { type: 'button', class: o.primary ? 'pill sm' : o.future || phone() ? 'quiet' : 'btn sm', text: label, onclick: e => run('start', null, e.currentTarget) }));
          mine.push({ label: 'Skip', kbd: fine() ? 'S' : null, onClick: () => run('skip') });
          if (!o.future) mine.push({ label: 'Mark done…', sub: 'Did it elsewhere', onClick: () => { open = 'done'; draw(); } });
        } else if (own && t.kind === 'custom' && t.counted !== false) {
          mine.push({ label: 'Skip', kbd: fine() ? 'S' : null, onClick: () => run('skip') });
        }
        if (whyList && t.kind !== 'fix') mine.push({ label: whyList.hidden ? 'Why this task' : 'Hide why', onClick: toggleWhy });
        const page = () => (!o.past && o.menu ? (o.menu(t) || []).filter(Boolean) : []);
        if ((mine.length || page().length) && UI.menu) {
          const more = h('button', { type: 'button', class: 'ibtn trow-more', 'aria-label': `More for ${t.title}`, 'aria-haspopup': 'menu' });
          more.append(ic('more', 20));
          more.addEventListener('click', () => {
            const p = page();
            UI.menu(more, [...mine, ...(mine.length && p.length ? [{ separator: true }] : []), ...p], { label: t.title });
          });
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
      // S: skip a task to do, undo a skipped, moved or marked one
      skip() {
        if (o.readonly || o.past) return false;
        if (['skipped', 'moved', 'marked'].includes(t.status) || (t.kind === 'custom' && DONE.has(t.status))) return run('undo');
        if (!DONE.has(t.status)) return run('skip');
        return false;
      },
    };
  }

  const infoTip = (text, label) => UI.why(text, { about: String(label || '').replace(/^About /, '') || null });

  /* a week's shape: busy days, short days, a day's minutes, one focus skill swapped. Days already past, or
     outside what the server takes (today up to two days before the exam), are shown and left alone. Each day is one
     choice, Busy or its minutes: 15 (a short day) and its own minutes, 15 less and 15 more */
  const DAY3 = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  function weekPlanner(host, week = {}) {
    const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    const first = week.today || iso(new Date());
    const editable = d => d.date >= first && (!week.last || d.date <= week.last) && (!week.start || d.date >= week.start);
    const study = d => ['practice', 'test', 'off'].includes(d.kind);
    const wasOff = d => d.kind === 'off';
    const days = (week.days || []).map(d => ({ ...d, base: d.minutes || 0, to: d.minutes || 0, off: wasOff(d), edit: editable(d) }));
    const changed = d => d.edit && study(d) && (d.off !== wasOff(d) || (!d.off && d.to !== d.base));
    const minsOf = d => (study(d) && !d.off ? d.to : 0);
    const label = d => (UI.date ? `${UI.date(d.date, 'long').replace(/,.*/, '').slice(0, 3)} ${+d.date.slice(8)}` : d.date);
    let swap = null;
    const el = h('div', { class: 'wplan' });
    const list = h('div', { class: 'wplan-days', role: 'list' });
    // the bars stay put and change height (a day's change moves its bar); the total rolls
    const bars = days.map(d => h('span', { class: 'wplan-bar' }, h('i'), h('b', { text: DAY3[(new Date(`${d.date}T12:00`).getDay() + 6) % 7] })));
    const chart = h('div', { class: 'wplan-chart', role: 'img' }, bars);
    const sum = h('span');
    const total = h('p', { class: 'wplan-total' }, h('span', { class: 'meta', text: 'This week' }), sum);
    // the week before and after the changes, said once
    function drawWeek() {
      const top = Math.max(15, ...days.map(d => Math.max(study(d) && !wasOff(d) ? d.base : 0, minsOf(d))));
      const before = days.reduce((s, d) => s + (study(d) && !wasOff(d) ? d.base : 0), 0), after = days.reduce((s, d) => s + minsOf(d), 0);
      days.forEach((d, i) => {
        const b = bars[i];
        b.toggleAttribute('data-off', d.off);
        b.toggleAttribute('data-zero', !d.off && !minsOf(d));
        b.toggleAttribute('data-past', !d.edit);
        b.toggleAttribute('data-ch', changed(d));
        b.firstChild.style.height = `${d.off ? 14 : Math.round(minsOf(d) / top * 100)}%`;
      });
      chart.setAttribute('aria-label', days.map(d => `${label(d)} ${d.off ? 'busy' : minsOf(d) ? mins(minsOf(d)) : 'rest'}`).join(', '));
      const text = before === after ? mins(after) : `${mins(before)} → ${mins(after)}`;
      if (sum.textContent && sum.textContent !== text && UI.roll) UI.roll(sum, text); else sum.textContent = text;
    }
    function drawDays() {
      list.replaceChildren(...days.map(d => {
        const lab = label(d);
        const what = d.off ? 'Busy' : d.kind === 'test' ? 'Test day' : study(d) ? (d.topics || []).map(name).join(', ') || 'Practice' : 'Rest';
        const row = h('div', { class: 'wplan-day', role: 'listitem', 'data-past': d.edit ? null : '' },
          h('span', { class: 'wplan-d', text: lab }), h('span', { class: 'wplan-w', text: what }));
        if (study(d) && d.edit) {
          // Busy, then the minutes up from 15; the seg's buttons are its only children (Busy first, 15 second)
          const opts = [...new Set([15, d.base - 15, d.base, d.base + 15].filter(m => m >= 15).map(m => Math.min(240, m)))].sort((a, b) => a - b);
          const set = (off, m) => { d.off = off; d.to = m; drawDays(); };
          row.append(h('div', { class: 'seg wplan-c', role: 'group', 'aria-label': `${lab}: busy, or its minutes` },
            h('button', { type: 'button', 'aria-pressed': String(d.off), 'data-base': wasOff(d) ? '' : null, text: 'Busy', onclick: () => set(!d.off, d.to) }),
            opts.map((m, i) => h('button', { type: 'button', 'aria-pressed': String(!d.off && d.to === m), 'data-base': m === d.base && !wasOff(d) ? '' : null, 'aria-label': `${m} minutes${m === d.base && !wasOff(d) ? ', as planned' : ''}`,
              text: i ? String(m) : `${m} min`, onclick: () => set(false, m) }))));
        } else if (study(d)) row.append(h('span', { class: 'wplan-c meta', text: d.date < first ? 'Past' : 'Fixed' }));
        return row;
      }));
      drawWeek();
    }
    drawDays();
    el.append(h('p', { class: 'meta wplan-key', text: 'Busy moves the day’s focus to the next study day. 15 min keeps a short day.' }),
      h('div', { class: 'wplan-week' }, total, chart), list);
    if ((week.swaps || []).length && (week.focus || []).length) {
      const from = h('select', { class: 'field sm', 'aria-label': 'Focus skill to swap out' }, week.focus.map(t => h('option', { value: t, text: name(t) })));
      const to = h('select', { class: 'field sm', 'aria-label': 'Skill to put on Focus' },
        h('option', { value: '', text: 'Keep' }), week.swaps.map(x => h('option', { value: x.topic, text: `${x.name || name(x.topic)}${x.gain ? ` · ≈ +${x.gain}` : ''}` })));
      const sync = () => { swap = to.value ? { from: from.value, to: to.value } : null; };
      from.addEventListener('change', sync); to.addEventListener('change', sync);
      el.append(h('div', { class: 'wplan-swap' }, h('span', { class: 'label', text: 'Swap a focus skill this week' }), from, h('span', { class: 'wplan-to', 'aria-hidden': 'true' }, ic('arrow', 16) || '→'), to));
    }
    const value = () => ({
      days: days.filter(changed).map(d => {
        const out = { date: d.date };
        if (d.off !== wasOff(d)) out.off = d.off;
        if (!d.off && d.to !== d.base) out.minutes = d.to;
        return out;
      }),
      ...(swap ? { swap } : {}),
    });
    // a week that has not begun goes in one call (one entry in the plan's history); otherwise day by day. The
    // swap rides on the days: each day that holds the skill takes the new one in its place.
    async function save() {
      const v = value();
      if (!v.days.length && !v.swap) return null;
      if (!week.plan || !UI.api) throw new Error('There is no plan to save to.');
      const base = `/plan/${encodeURIComponent(week.plan)}`;
      const whole = !!week.monday && week.monday >= first;
      let reply = null;
      if (whole && v.days.length) reply = await UI.api(`${base}/week/${week.monday}`, { method: 'PUT', body: { days: v.days } });
      const per = {};
      if (!whole) v.days.forEach(d => { const b = {}; if ('off' in d) b.off = d.off; if ('minutes' in d) b.minutes = d.minutes; per[d.date] = b; });
      if (v.swap) days.filter(d => d.edit && !d.off && (d.topics || []).includes(v.swap.from)).forEach(d => {
        per[d.date] = { ...(per[d.date] || {}), topics: [...new Set(d.topics.map(t => (t === v.swap.from ? v.swap.to : t)))].slice(0, 3) };
      });
      for (const [date, body] of Object.entries(per)) reply = await UI.api(`${base}/day/${date}`, { method: 'PUT', body });
      return reply;
    }
    const err = h('p', { class: 'trow-err', role: 'status', 'data-nofold': '' });
    const error = msg => { err.textContent = msg || ''; };
    if (week.button !== false) {
      const btn = h('button', { type: 'button', class: 'pill sm', text: 'Save the week' });
      btn.addEventListener('click', () => {
        error('');
        const work = () => save().then(r => { if (week.onSaved) week.onSaved(r); return r; });
        (UI.saving ? UI.saving(btn, work) : work()).catch(e => error((e && e.message) || 'Couldn’t save the week. Try again.'));
      });
      el.append(h('div', { class: 'wplan-foot' }, btn));
    }
    el.append(err);
    if (host) host.append(el);
    return { el, value, save, error };
  }

  Object.assign(UI, { taskRow, taskTag, taskQuestion, weekPlanner, infoTip });
})();
