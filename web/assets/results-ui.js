/* ============================================================================
   SAT Freshman -- results-ui.js: the sittings card and the skill panel (S6)
   (spec/rebuild-v2.md 2.4's results-ui.js row, 3.5 §2.7 and §2.9, R26, R35;
   v2-upgrades reports.md SR6, SR7, SR14, SR18, SR23; F1 follow-up: chips by
   (subject, module) through UI.qlabel)

   Loaded after ui.js, kit.js and charts.js by /results/, the report, Tests and
   Today. Adds to window.UI. Its styles are injected once, on ui.css tokens.

   UI.sittingCard(host, row, o) -> {el, peek(on), select(on), selected}
     row  an /api/history item: {id, kind, seq, label, kind_label, started, finished,
          right, asked, estimate {low, high}, pct, delta, ms, route, modules [{n, subject,
          right, asked, wrong [n], blank [n], fixed [n]}], open, twins {n, right}, note,
          ledger {total, by_cause}, recovery {recovered, open, slipping, points_open},
          reviewed {n, of}, causes {cause: n}, pair {with, label, fixed}}
          or an in_progress row: {id, kind, seq, started, module, answered, total,
          seconds_left, expired} with o.progress
     o    {progress, share (read-only: no actions), peek (default true), subjects,
           onSelect(row, on), onFix(row), fixLabel}
   UI.skillPanel(topic, {share, fallback, onClose}) -> the sheet api
       a right drawer (a bottom sheet on a phone): GET /api/skill/{topic}; "Practise
       this skill" starts a set on that skill only
   UI.rx  the helpers both results pages share:
       worth(w) -> '≈ +15' | 'under 5' | ''    pts(n) -> '≈ 60'
       drill(body, btn) posts /api/drill and opens the set (a toast on failure)
       band(e) -> '540–560'    CAUSE {key: {label, letter}}
       kv(rows, {label}) -> ul.rx-kv: [{label, value, sub, href, onClick, title, why, after}]
           why: a "?" (UI.why) after the label, on a plain row; after: a Node under the row (a meter)
       info(text, label) -> UI.why(text, {about}) (kit's one "?"; 'About X' becomes about X)
   ========================================================================== */
(() => {
  'use strict';
  const UI = window.UI;
  if (!UI || UI.sittingCard) return;
  const { h } = UI;
  const doc = document;
  const fmt = n => (UI.num ? UI.num(n) : String(n));
  const r5 = x => Math.round(x / 5) * 5;

  const CAUSE = {
    trap: { label: 'Traps', one: 'trap', letter: 'T' }, slip: { label: 'Slips', one: 'slip', letter: 'S' },
    misread: { label: 'Misread', one: 'misread', letter: 'R' }, clock: { label: 'Clock', one: 'clock', letter: 'C' },
    entry: { label: 'Entry', one: 'entry', letter: 'E' }, gap: { label: 'Gaps', one: 'gap', letter: 'G' },
  };
  const rx = {
    CAUSE,
    worth(w) {
      if (w === null || w === undefined) return '';
      if (typeof w === 'number') return w >= 2.5 ? `≈ +${r5(w)}` : w > 0 ? 'under 5' : '';
      if (w.printed) return `≈ +${w.printed}`;
      if (w.under5 || (w.pts > 0 && w.pts < 2.5)) return 'under 5';
      return w.pts >= 2.5 ? `≈ +${r5(w.pts)}` : '';
    },
    wnum(w) { return w === null || w === undefined ? 0 : typeof w === 'number' ? w : +w.pts || 0; },
    pts(n) { return n === null || n === undefined ? '' : `≈ ${fmt(r5(n))}`; },
    band(e) { return e && e.low !== undefined && e.low !== null ? `${e.low}–${e.high}` : ''; },
    async drill(body, btn, to) {
      if (btn) btn.setAttribute('aria-busy', 'true');
      try {
        const s = await UI.api('/drill', { method: 'POST', body });
        location.href = to ? to(s) : `/practice/session/?id=${encodeURIComponent(s.id)}`;
      } catch (e) {
        UI.toast((e && e.status === 409 && e.detail && (e.detail.reason || e.detail)) ? `Nothing to practise there: ${typeof e.detail === 'string' ? e.detail : e.detail.reason}.` : 'Couldn’t start that set. Try again.');
      } finally { if (btn) btn.removeAttribute('aria-busy'); }
    },
    reportHref: (id, addr) => `/results/report/?id=${encodeURIComponent(id)}${addr ? `#q=${addr}` : ''}`,
    // key and value rows: [{label, value, sub, href, onClick, title, why, after}]; a row with href or onClick is a link
    // or a button; why adds kit's "?" beside a plain row's label, after puts a Node (a 4px meter) under the row
    kv(rows, o = {}) {
      const ul = h('ul', { class: 'rx-kv', 'aria-label': o.label || null });
      rows.filter(Boolean).forEach(r => {
        const tag = r.href ? 'a' : r.onClick ? 'button' : 'div';
        const v = r.value === null || r.value === undefined || r.value === '' ? '–' : typeof r.value === 'number' ? fmt(r.value) : r.value;
        const row = h(tag, { class: 'rx-kv-r', href: r.href || null, type: tag === 'button' ? 'button' : null, title: r.title || null },
          h('span', { class: 'rx-kv-k' }, r.label, r.why && tag === 'div' ? UI.why(r.why, { about: String(r.label).toLowerCase() }) : null), h('span', { class: 'rx-kv-v' }, v),
          r.sub ? h('span', { class: 'rx-kv-s', text: r.sub }) : null, r.after ? h('span', { class: 'rx-kv-x' }, r.after) : null);
        if (r.onClick) row.addEventListener('click', () => r.onClick(row));
        ul.append(h('li', {}, row));
      });
      return ul;
    },
    // round one's quiet "?", now kit's UI.why (decision 7: no paragraphs about the UI); kept for old callers
    info(text, label) { return UI.why(text, { about: label && label !== 'How this works' ? label.replace(/^About /, '') : undefined }); },
  };

  /* ------------------------------------------------------------ styles (once) */
  const CSS = `
.sc { display: grid; grid-template-columns: 76px minmax(0, 1fr) auto 102px; gap: 2px 12px; align-items: center; min-height: 48px; padding: 6px 8px; margin: 0 -8px; }
.sc + .sc { border-top: 1px solid var(--line); }
.sc:focus-visible { outline: 2px solid var(--amber-deep); outline-offset: -2px; }
@media (hover: hover) and (pointer: fine) { .sc:not(.sc-prog):not([aria-selected="true"]):hover { background: var(--hover); } }
.sc[aria-selected="true"] { background: var(--sel-bg); }
.sc-when { display: grid; gap: 2px; font: 500 12.5px/1.3 var(--font); color: var(--soft); font-variant-numeric: tabular-nums; }
.sc-main { display: grid; gap: 2px; min-width: 0; }
.sc-title { display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 8px; }
.sc-title a, .sc-title > b { font: 600 14.5px/1.35 var(--font); color: var(--ink); text-decoration: none; }
.sc-title a:hover { text-decoration: underline; text-underline-offset: 3px; }
.sc-sub { font: 400 12.5px/1.35 var(--font); color: var(--soft); }
.sc-scorecell { justify-self: end; }
.sc-score { font: 600 14.5px/1.3 var(--font); color: var(--ink); font-variant-numeric: tabular-nums; white-space: nowrap; }
.sc-delta { font: 500 12.5px var(--font); color: var(--soft); font-variant-numeric: tabular-nums; }
/* Fix and Peek, one column each so every row lines up; on a fine pointer they show on hover or focus (.reveal) */
.sc-side { display: grid; grid-template-columns: 64px 34px; gap: 4px; justify-items: end; align-items: center; }
.sc-side > [data-fix] { grid-column: 1; }
.sc-side > .sc-peekb { grid-column: 2; }
/* an open Peek keeps its button in view */
.sc:has(> .sc-peek:not([hidden])) > .sc-side { opacity: 1; }
.sc-prog > .sc-side { display: flex; justify-content: flex-end; }
.sc-chips { display: grid; gap: 4px; }
.sc-mod { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; font: 500 12.5px var(--font); color: var(--soft); }
.sc-mod > b { font-weight: 600; color: var(--ink); margin-right: 2px; }
.sc-chip { display: inline-grid; place-items: center; min-width: 26px; height: 24px; padding: 0 4px; border-radius: 6px; background: var(--ink); color: var(--on-ink); font: 500 12.5px var(--font); font-variant-numeric: tabular-nums; text-decoration: none; position: relative; }
.sc-chip[data-status="blank"] { background: none; color: var(--soft); outline: 1.5px dashed var(--faint); outline-offset: -1.5px; }
.sc-chip[data-status="fixed"] { background: var(--paper); color: var(--ink); box-shadow: inset 0 0 0 1.5px var(--ink); }
.sc-chip[data-status="fixed"]::after { content: "✓"; position: absolute; right: -3px; bottom: -4px; font: 600 9px var(--font); color: var(--amber-deep); }
.sc-more { font: 500 12.5px var(--font); color: var(--soft); background: none; border: 0; padding: 0 4px; cursor: pointer; min-height: 24px; }
.sc-lines { display: flex; flex-wrap: wrap; gap: 2px 12px; font: 400 12.5px/1.4 var(--font); color: var(--soft); }
.sc-lines .open { color: var(--ink); }
.sc-lines .open::before { content: ""; display: inline-block; width: 6px; height: 6px; margin-right: 6px; border-radius: 50%; background: var(--amber); vertical-align: 1px; }
.sc-note { font: italic 400 12.5px/1.4 var(--font); color: var(--ink); }
.sc-det { grid-column: 1 / -1; display: grid; gap: 4px; min-width: 0; }
.sc-det .sc-ring { justify-self: start; }
.sc-ring { --ring: 0; width: 34px; height: 34px; border-radius: 50%; flex: none; display: inline-grid; place-items: center;
  background: conic-gradient(var(--amber) calc(var(--ring) * 1%), var(--track) 0); }
.sc-ring::before { content: ""; width: 24px; height: 24px; border-radius: 50%; background: var(--surface); grid-area: 1 / 1; }
.sc-ring > span { grid-area: 1 / 1; font: 600 10px var(--font); font-variant-numeric: tabular-nums; color: var(--ink); z-index: 1; }
.sc-peek { grid-column: 1 / -1; display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 12px 24px; padding: 12px 0 4px; margin-top: 4px; border-top: 1px solid var(--line); }
.sc-peek .gauge { max-width: 220px; }
.sc-peek-r { display: grid; gap: 12px; min-width: 0; }
.sc-peek-strips { display: grid; gap: 4px; }
.sc-peek-strips p { font: 500 12.5px var(--font); color: var(--soft); font-variant-numeric: tabular-nums; }
.sc-peek-doms { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 16px; }
.sc-acts { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.sc-prog { grid-template-columns: 76px minmax(0, 1fr) auto; }
@media (max-width: 759px) {
  /* a phone: the name and its score on one line, the day and the actions under them */
  .sc { grid-template-columns: minmax(0, 1fr) auto; grid-template-areas: "main score" "when side"; gap: 4px 12px; padding-block: 8px; }
  .sc > .sc-main { grid-area: main; }
  .sc > .sc-scorecell { grid-area: score; }
  .sc > .sc-when { grid-area: when; display: flex; gap: 8px; }
  .sc > .sc-side { grid-area: side; }
  .sc-prog { grid-template-areas: "main side" "when side"; }
  .sc-peek, .sc-peek-doms { grid-template-columns: minmax(0, 1fr); }
}
dialog.sheet.drawer { margin: 0 0 0 auto; height: 100dvh; max-height: 100dvh; width: min(420px, 100vw); max-width: min(420px, 100vw); border-radius: 0; }
.skp { display: grid; gap: 12px; }
.skp-row { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 4px 12px; font: 400 14.5px/1.4 var(--font); }
.skp-row b { font: 600 14.5px var(--font); font-variant-numeric: tabular-nums; }
.skp-run { display: flex; flex-wrap: wrap; gap: 4px; }
.skp-run i { width: 12px; height: 12px; border-radius: 50%; background: var(--ink); display: inline-grid; place-items: center; font: 600 8px/1 var(--font); color: var(--on-ink); font-style: normal; }
.skp-run i.ok { background: var(--amber); color: var(--ink-deep); }
.skp-list { display: grid; margin: 0; padding: 0; list-style: none; }
.skp-list li { display: grid; gap: 4px; padding: 8px 0; }
.skp-list li + li { border-top: 1px solid var(--line); }
.skp-list .acts { display: flex; flex-wrap: wrap; gap: 8px; }
.skp h3 { margin-top: 4px; font: 600 14.5px/1.35 var(--font); color: var(--ink); }
/* key and value rows (UI.rx.kv): Totals, the score report's summary */
.rx-kv { list-style: none; margin: 0; padding: 0; display: grid; }
.rx-kv > li + li { border-top: 1px solid var(--line); }
.rx-kv-r { appearance: none; border: 0; background: none; width: 100%; display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: baseline; column-gap: 12px;
  min-height: 36px; padding: 8px 0; font: inherit; text-align: left; color: var(--ink); text-decoration: none; }
:is(a, button).rx-kv-r { cursor: pointer; padding-inline: 8px; margin-inline: -8px; width: calc(100% + 16px); border-radius: 8px; }
@media (hover: hover) and (pointer: fine) { :is(a, button).rx-kv-r:hover { background: var(--hover); } }
.rx-kv-k { font: 400 14px/1.35 var(--font); color: var(--soft); }
.rx-kv-v { font: 600 14.5px/1.35 var(--font); font-variant-numeric: tabular-nums; text-align: right; }
:is(a, button).rx-kv-r .rx-kv-v { text-decoration: underline; text-decoration-color: var(--faint); text-underline-offset: 3px; }
.rx-kv-s { grid-column: 1; font: 400 12.5px/1.35 var(--font); color: var(--soft); }
.rx-kv-k > .why-q { vertical-align: 1px; }
.rx-kv-x { grid-column: 1 / -1; display: block; margin-top: 6px; }
@media print { .sc-peekb, .sc-side, .sc-acts .btn, .sc-acts .pill { display: none !important; } }
`;
  const style = h('style', { 'data-for': 'results-ui', text: CSS });
  (doc.head || doc.documentElement).append(style);

  const chev = () => (UI.icon ? UI.icon('caret_down', 18) : '▾');
  const when = t => {
    if (!t) return '';
    // the day only: no clock times in history lines (the user's rule)
    const d = new Date(t), days = Math.round((new Date().setHours(0, 0, 0, 0) - new Date(t).setHours(0, 0, 0, 0)) / 864e5);
    return days === 0 ? 'Today' : days === 1 ? 'Yesterday' : UI.date(d);
  };
  const isTest = k => ['full', 'mock', 'module', 'diagnostic', 'paper', 'custom', 'twin', 'shared'].includes(k);
  const SUBJ_OK = new Set(['math', 'rw']);
  const kindName = row => {
    // a full SAT's half goes by the full SAT's number ("Full SAT #1"); its subtitle names the section
    if (row.full && row.full.part && row.full.number) return `Full SAT #${row.full.number}`;
    const base = row.kind_label || (row.kind === 'full' ? 'Full SAT' : UI.KIND.label(row));
    return row.seq && !/#\d/.test(base) ? `${base} #${row.seq}` : base;
  };
  const subtitle = row => {
    // a full SAT: each section's range, R&W first ("R&W 640–660 · Math 650–670")
    if (row.kind === 'full') return (row.parts || []).map(p => `${UI.subjectLabel ? UI.subjectLabel(p.subject, true) : p.subject} ${rx.band(p.estimate) || '–'}`).join(' · ');
    if (row.full && row.full.part) return [UI.subjectLabel(row.subject), row.route === 'upper' ? 'harder M2' : row.route === 'lower' ? 'easier M2' : null].filter(Boolean).join(' · ');
    if (row.label) return row.label;
    if (row.kind === 'mock' && row.route) return row.route === 'upper' ? 'harder M2' : 'easier M2';
    if (row.kind === 'challenge' && row.rank) return `#${row.rank} of ${fmt(row.players || row.n)}`;
    if (row.topics && row.topics.length) return row.topics.slice(0, 3).map(t => (UI.topicName ? UI.topicName(t) : (UI.TOPIC[t] || {}).short || t)).join(', ');
    return '';
  };

  /* ------------------------------------------------------------ UI.sittingCard */
  function sittingCard(host, row, o = {}) {
    if (o.progress || row.in_progress) return progressCard(host, row, o);
    // a full SAT (/api/history folds its two sections into one entry): its total, its result page, the sections'
    // miss chips each opening its own report; no Peek and no Fix (each section's report has its own)
    const full = row.kind === 'full';
    const href = (full ? `/results/full/?id=${encodeURIComponent(row.id)}` : rx.reportHref(row.id)) + (o.share && o.shareToken ? `&share=${encodeURIComponent(o.shareToken)}` : '');
    // (its four modules' chips would fill the card: the full result and each report list them)
    if (full) row = Object.assign({}, row, { modules: [], asked: 0, right: 0 });
    const el = h('article', { class: 'sc', tabindex: '0', 'data-id': row.id, 'aria-label': `${kindName(row)}, ${when(row.finished)}` });
    const two = o.subjects > 1 || new Set((row.modules || []).map(m => m.subject || 'math')).size > 1;

    const mins = row.ms ? Math.round(row.ms / 60000) : null;
    el.append(h('div', { class: 'sc-when' }, h('span', { text: when(row.finished || row.started) }), mins ? h('span', { text: `${mins} min` }) : null));

    const main = h('div', { class: 'sc-main' });
    const score = row.estimate && row.estimate.low ? rx.band(row.estimate)
      : row.asked ? `${Math.round((row.right || 0) / row.asked * 100)}%` : '';   // the count is the tooltip
    const d = row.delta;
    // the name and what it covered stack on the left, the score is its own cell, then the actions
    // (native append prints a null as "null", so the subtitle joins only when there is one)
    const sub = subtitle(row);
    // a list of both subjects names each row's ("Reading and Writing · Full section #2"); a full SAT is both
    const said = o.subjects > 1 && !full && !(row.full && row.full.part) && SUBJ_OK.has(row.subject) ? `${UI.subjectLabel(row.subject)} · ${kindName(row)}` : kindName(row);
    main.append(h('div', { class: 'sc-title' },
      h('a', { href, text: said, title: o.share ? 'Open' : 'Review' }),
      d !== null && d !== undefined ? h('span', { class: 'sc-delta', text: d === 0 ? '= same as last' : `${d > 0 ? '▴ +' : '▾ −'}${fmt(Math.round(Math.abs(d) / 10) * 10)} vs last` }) : null));
    if (sub) main.append(h('div', { class: 'sc-sub', text: sub }));
    el.append(h('div', { class: 'sc-scorecell' }, score ? h('span', { class: 'sc-score', title: row.asked && !(row.estimate && row.estimate.low) ? `${fmt(row.right)} of ${fmt(row.asked)} right` : null, text: score }) : null));
    if (row.open) el.dataset.open = '';

    // decision (Sittings): the card keeps date, title, band, delta, Review; the miss chips, the Lost line, the
    // recovery ring, reviewed and twins live in the Peek (`det`). A row with no Peek keeps them on the card.
    const peekable = o.peek !== false && !full && (isTest(row.kind) || row.kind === 'drill' || row.kind === 'challenge');
    const det = h('div', { class: 'sc-det' });
    // wrong-question chips, one group per (subject, module): never a hard-coded M1 / M2 pair
    const mods = (row.modules || []).filter(m => (m.wrong || []).length || (m.blank || []).length);
    if (mods.length) {
      const box = h('div', { class: 'sc-chips' });
      for (const m of mods) {
        const fixed = new Set(m.fixed || []);
        const list = [...(m.wrong || []).map(n => ({ n, s: fixed.has(n) ? 'fixed' : 'incorrect' })), ...(m.blank || []).map(n => ({ n, s: 'blank' }))]
          .sort((a, b) => a.n - b.n);
        const head = UI.qlabel({ subject: m.subject || 'math', module: m.n || null, n: 0 }, two ? true : null).replace(/\s*Q0$/, '');
        const line = h('div', { class: 'sc-mod' }, h('b', { text: `${head ? head + ' ' : ''}✕` }));
        const chip = x => h('a', { class: 'sc-chip', 'data-status': x.s, href: rx.reportHref(m.sid || row.id, UI.qlabel.addr({ subject: m.subject || 'math', module: m.n || null, n: x.n })),
          text: String(x.n), 'aria-label': `${UI.qlabel({ subject: m.subject, module: m.n, n: x.n }, two ? true : null)}, ${x.s === 'blank' ? 'not answered' : x.s === 'fixed' ? 'incorrect, fixed since' : 'incorrect'}` });
        list.slice(0, 8).forEach(x => line.append(chip(x)));
        if (list.length > 8) {
          const more = h('button', { type: 'button', class: 'sc-more', text: `+${list.length - 8}`, 'aria-label': `Show ${list.length - 8} more` });
          more.addEventListener('click', () => { more.replaceWith(...list.slice(8).map(chip)); });
          line.append(more);
        }
        box.append(line);
      }
      det.append(box);
    }

    const lines = h('div', { class: 'sc-lines' }), dlines = h('div', { class: 'sc-lines' });
    const causes = row.causes || (row.ledger && row.ledger.by_cause && Object.fromEntries(row.ledger.by_cause.map(c => [c.cause, c.n])));
    const lost = causes ? Object.entries(causes).filter(([, n]) => n > 0).sort((a, b) => b[1] - a[1]) : [];
    if (lost.length) dlines.append(h('span', { text: `Lost ${fmt(lost.reduce((s, [, n]) => s + n, 0))}: ${lost.map(([c, n]) => `${fmt(n)} ${(CAUSE[c] || { one: c }).one}${n === 1 ? '' : 's'}`).join(' · ')}` }));
    if (row.open) lines.append(h('span', { class: 'open', text: `${fmt(row.open)} still open` }));
    if (!peekable && !full && row.reviewed && row.reviewed.of) dlines.append(h('span', { text: `Reviewed ${fmt(row.reviewed.n)} of ${fmt(row.reviewed.of)}` }));
    if (row.twins && row.twins.n) dlines.append(h('span', { text: `Tried ${fmt(row.twins.n)} like this${row.twins.right !== undefined ? ` · ${fmt(row.twins.right)} right` : ''}` }));
    if (row.pair && row.pair.with) lines.append(h('a', { href: `${rx.reportHref(row.id)}&vs=${encodeURIComponent(row.pair.with)}`, text: `vs ${row.pair.label || 'the original'}: fixed ${fmt(row.pair.fixed || 0)}` }));
    if (lines.childNodes.length) main.append(lines);
    if (dlines.childNodes.length) det.append(dlines);
    if (row.note) main.append(h('p', { class: 'sc-note', text: `“${row.note}”` }));
    el.insertBefore(main, el.querySelector('.sc-scorecell'));

    const side = h('div', { class: 'sc-side reveal' });
    const rec = row.recovery;
    if (rec && (rec.recovered || rec.open || rec.slipping)) {
      const n = (Array.isArray(rec.recovered) ? rec.recovered.length : rec.recovered) || 0;
      const of = n + ((Array.isArray(rec.open) ? rec.open.length : rec.open) || 0) + ((Array.isArray(rec.slipping) ? rec.slipping.length : rec.slipping) || 0);
      const text = `Recovered ${fmt(n)} / ${fmt(of)}${rec.points_open ? ` · ${rx.pts(rec.points_open)} open` : ''}`;
      det.append(h('span', { class: 'sc-ring', style: `--ring: ${of ? Math.round(n / of * 100) : 0}`, role: 'img', 'aria-label': text, title: text }, h('span', { text: `${fmt(n)}/${fmt(of)}` })));
    }
    const misses = (row.modules || []).reduce((s, m) => s + (m.wrong || []).length + (m.blank || []).length, 0) || (row.asked ? row.asked - (row.right || 0) : 0);
    let peekEl = null, peekB = null;
    if (!o.share) {
      // a challenge is a fixed set (no repairs), so its Fix drills the skills it covered instead of the exact questions
      const chal = row.kind === 'challenge';
      if (misses && !full && (!chal || (row.topics || []).length)) {
        const fixB = h('button', { type: 'button', class: 'quiet', 'data-fix': '', text: o.fixLabel || `Fix · ${fmt(row.open || misses)}` });
        fixB.addEventListener('click', () => (o.onFix ? o.onFix(row, fixB) : chal ? rx.drill({ topics: row.topics, count: 10, adaptive: true, source: 'skill' }, fixB) : rx.drill({ from_session: row.id, source: 'fix' }, fixB)));
        side.append(fixB);
      }
    }
    if (!peekable) { if (det.childNodes.length) main.append(det); }
    else {
      peekB = h('button', { type: 'button', class: 'btn sm icon sc-peekb', 'aria-expanded': 'false', 'aria-label': 'Peek: a mini report here', title: 'Peek (Space)' }, chev());
      peekB.addEventListener('click', () => peek());
      side.append(peekB);
    }
    el.append(side);

    function peek(on) {
      const open = on ?? !(peekEl && !peekEl.hidden);
      if (!peekB) return;
      peekB.setAttribute('aria-expanded', String(open));
      if (!open) { if (peekEl) peekEl.hidden = true; return; }
      if (peekEl) { peekEl.hidden = false; return; }
      peekEl = h('div', { class: 'sc-peek', 'aria-busy': 'true' }, UI.skel(null, 'circle'), UI.skel(null, 'lines:4'));
      el.append(peekEl);
      UI.api(`/session/${encodeURIComponent(row.id)}/results${o.shareToken ? `?share=${encodeURIComponent(o.shareToken)}` : ''}`, { quiet: true })
        .then(r => drawPeek(r)).catch(() => { peekEl.removeAttribute('aria-busy'); UI.cardError(peekEl.replaceChildren() || peekEl, () => { peekEl.remove(); peekEl = null; peek(true); }, 'Couldn’t load this sitting.'); });
    }
    function drawPeek(r) {
      peekEl.removeAttribute('aria-busy');
      peekEl.replaceChildren();
      const left = h('div');
      if (r.estimate && r.estimate.low && UI.gauge) UI.gauge(left, { band: r.estimate, target: r.profile && r.profile.target, subject: r.subject || 'math', className: 'sm' });
      else left.append(h('p', { class: 'sc-score', text: `${fmt(r.right)} / ${fmt(r.asked)} · ${Math.round((r.right || 0) / (r.asked || 1) * 100)}%` }));
      const right = h('div', { class: 'sc-peek-r' });
      const L = r.ledger;
      if (L && L.by_cause && UI.stackBar) UI.stackBar(right, L.by_cause.map(c => ({ key: c.cause, label: (CAUSE[c.cause] || { label: c.cause }).label, value: c.printed ?? c.pts, n: c.n })), { approx: true, unit: 'pts', label: 'Where the points went', legend: 'auto' });
      const doms = h('div', { class: 'sc-peek-doms' });
      (r.domains || []).forEach(dm => UI.meter(doms, { label: dm.domain, value: dm.right, max: dm.asked, text: `${fmt(dm.right)} / ${fmt(dm.asked)}` }));
      right.append(doms);
      const rv = r.review || [];
      const byMod = new Map();
      const m1 = r.module1 && r.module1.asked;
      rv.forEach((it, i) => {
        const mod = it.module ?? (r.mode === 'mock' && m1 ? (i < m1 ? 1 : 2) : null);
        const n = it.n ?? (mod === 2 ? i + 1 - m1 : i + 1);
        const status = it.status || (it.correct ? 'correct' : it.given === null || it.given === undefined || it.given === '' ? 'blank' : 'incorrect');
        if (!byMod.has(mod)) byMod.set(mod, []);
        byMod.get(mod).push({ n, status: status === 'unanswered' ? 'blank' : status, i, subject: it.subject || 'math', module: mod });
      });
      const strips = h('div', { class: 'sc-peek-strips' });
      for (const [mod, marks] of byMod) {
        strips.append(h('p', { text: `${mod ? `Module ${mod}` : 'Questions'} · ${marks.filter(m => m.status === 'correct').length} / ${marks.length}` }));
        UI.strip(strips, marks, { fit: true, onPick: (m) => openPlayer(r, rv, m.i), noun: mod ? `M${mod} Q` : 'Q' });
      }
      right.append(strips);
      const miss = rv.filter(it => !(it.status ? it.status === 'correct' : it.correct)).length;
      if (r.reviewed || miss) UI.meter(right, { label: 'Reviewed', value: r.reviewed ? r.reviewed.n : 0, max: r.reviewed ? r.reviewed.of : miss });
      const acts = h('div', { class: 'sc-acts' });
      if (!o.share && miss) {
        const fixB = h('button', { type: 'button', class: 'pill sm', text: `Fix these · ${fmt(miss)}` });
        fixB.addEventListener('click', () => rx.drill({ from_session: row.id, source: 'fix' }, fixB));
        acts.append(fixB);
      }
      acts.append(h('a', { class: 'btn sm', href, text: 'Open the report' }));
      right.append(acts);
      peekEl.append(left, right);
      if (det.childNodes.length) peekEl.append(det);
    }
    function openPlayer(r, rv, i) {
      if (!UI.review) { location.href = href; return; }
      UI.review(null, rv.map(x => ({ ...x, session: row.id })), { mode: 'dialog', at: i, hash: false, owner: r.mine !== false && !o.share, session: row.id,
        title: kindName(row) });
    }
    el.addEventListener('keydown', e => {
      if (e.target !== el) return;
      if (e.key === ' ') { e.preventDefault(); peek(); }
      else if (e.key === 'Enter') { e.preventDefault(); location.href = href; }
    });
    let sel = false;
    const api = {
      el, row, peek,
      get selected() { return sel; },
      select(on) { sel = on ?? !sel; el.setAttribute('aria-selected', String(sel)); if (o.onSelect) o.onSelect(row, sel); return sel; },
      fix() { const b = el.querySelector('[data-fix]'); if (b) b.click(); },
    };
    if (host) host.append(el);
    return api;
  }

  function progressCard(host, row, o) {
    const el = h('article', { class: 'sc sc-prog', 'data-id': row.id });
    const kind = row.kind;
    const test = isTest(kind);
    const left = row.seconds_left;
    let text;
    if (row.gated) text = 'Sign up to see these results';
    else if (row.expired) text = 'time ran out';
    else if (test) text = [row.module && (kind === 'mock' || kind === 'full') && `Module ${row.module}`, left !== null && left !== undefined ? `${UI.mmss(left)} left` : `${fmt(row.answered || 0)} of ${fmt(row.total || 0)} answered`].filter(Boolean).join(' · ');
    else text = `${fmt(row.answered || 0)} of ${fmt(row.total || '?')}`;
    el.append(h('div', { class: 'sc-when' }, h('span', { text: when(row.started) })),
      h('div', { class: 'sc-main' }, h('div', { class: 'sc-title' }, h('b', { text: left === null && test && !row.expired ? `Untimed ${kindName(row).toLowerCase()}` : kindName(row) }), h('span', { class: 'sc-sub', text }))));
    const side = h('div', { class: 'sc-side' });
    if (!o.share) {
      if (row.gated) side.append(h('a', { class: 'pill sm', href: `/diagnostic/signup.html?s=${encodeURIComponent(row.id)}`, text: 'Sign up' }));
      else if (row.expired) {
        const b = h('button', { type: 'button', class: 'pill sm', text: 'See your report' });
        b.addEventListener('click', async () => {
          b.setAttribute('aria-busy', 'true');
          try { await UI.api(`/session/${encodeURIComponent(row.id)}/finish`, { method: 'POST', body: {} }); } catch (_) { /* finished already: the report opens either way */ }
          location.href = rx.reportHref(row.id);
        });
        side.append(b);
      } else side.append(h('a', { class: 'pill sm', href: test ? `/test/?s=${encodeURIComponent(row.id)}` : `/practice/session/?id=${encodeURIComponent(row.id)}`, text: 'Resume' }));
    }
    el.append(side);
    if (host) host.append(el);
    return { el, row, peek() {}, select() {}, fix() {} };
  }

  /* ------------------------------------------------------------ UI.skillPanel */
  function skillPanel(topic, o = {}) {
    const T = (UI.TOPIC && UI.TOPIC[topic]) || { short: UI.topicName ? UI.topicName(topic) : topic, domain: '' };   // an R&W skill by its name
    const body = h('div', { class: 'skp', 'aria-busy': 'true' }, UI.skel(null, 'lines:6'));
    const acts = o.share ? [] : [
      { label: 'Practise this skill', primary: true, onClick: sh => { const b = sh.el.querySelector('.sheet-foot .pill'); rx.drill({ topics: [topic], count: 10, adaptive: true, source: 'skill' }, b); return false; } },
    ];
    const sh = UI.sheet({ title: T.short, body, actions: acts, className: 'drawer', onClose: o.onClose });
    const q = o.share ? `?share=${encodeURIComponent(o.share)}` : '';
    UI.api(`/skill/${encodeURIComponent(topic)}${q}`, { quiet: true }).then(fill, () => fill(o.fallback || { topic }));
    function fill(s) {
      body.removeAttribute('aria-busy');
      body.replaceChildren();
      const answered = s.answered || 0, right = s.right || 0;
      body.append(h('p', { class: 'meta', text: s.domain || T.domain || '' }));
      const m = h('div');
      m.append(h('div', { class: 'skill-m' },
        h('span', { class: 'mbar', role: 'img', 'aria-label': `Mastery: ${UI.masteryWord(s.mastery, answered)}` }, h('i', { style: `--m: ${Math.max(0, Math.min(1, s.mastery || 0))}` })),
        h('span', { class: 'skill-word', text: UI.masteryWord(s.mastery, answered) })));
      m.title = 'A practice gauge: recent answers, hard ones counting more.';
      body.append(m);
      body.append(h('div', { class: 'skp-row' }, h('span', { text: 'Answered' }), h('b', { text: fmt(answered) })),
        h('div', { class: 'skp-row' }, h('span', { text: 'Right' }), h('b', { text: answered ? `${fmt(right)} · ${Math.round(right / answered * 100)}%` : '–' })));
      if ((s.by_difficulty || []).length) {
        body.append(h('h3', { text: 'By difficulty' }));
        s.by_difficulty.forEach(d => body.append(h('div', { class: 'skp-row' }, h('span', {}, UI.dbars(d.difficulty)),
          h('b', { text: d.answered ? `${fmt(d.right)} / ${fmt(d.answered)} · ${Math.round(d.right / d.answered * 100)}%${d.avg_ms ? ` · avg ${UI.mmss(d.avg_ms / 1000)}` : ''}` : 'none yet' }))));
      }
      if ((s.recent || []).length) {
        body.append(h('h3', { text: 'Recent run' }), h('div', { class: 'skp-run', role: 'img', 'aria-label': `Last ${s.recent.length}: ${s.recent.filter(Boolean).length} right, newest last` },
          s.recent.map(ok => h('i', { class: ok ? 'ok' : '', text: ok ? '✓' : '✕' }))));
      }
      const open = s.traps_open || [];
      if (open.length) {
        body.append(h('h3', { text: `Open mistakes · ${fmt(open.length)}` }));
        const ul = h('ul', { class: 'skp-list' });
        open.forEach(t => {
          const li = h('li', {}, h('b', { text: t.label }), h('span', { class: 'meta', text: `hit ${fmt(t.hits || 1)}× · ${fmt(t.owed || 2)} to close` }));
          if (!o.share) {
            const acts2 = h('div', { class: 'acts' });
            const f = h('button', { type: 'button', class: 'btn sm', text: 'Fix' });
            f.addEventListener('click', () => rx.drill({ pool: 'redo', templates: [t.template], topics: [topic], source: 'mistakes' }, f));
            acts2.append(f, h('a', { class: 'quiet', href: t.id ? `/review/?open=trap:${t.id}` : '/mistakes/', text: 'Review' }));
            li.append(acts2);
          }
          ul.append(li);
        });
        body.append(ul);
      }
      if (s.traps_closed) body.append(h('div', { class: 'skp-row' }, h('span', { text: 'Fixed' }), h('b', { text: fmt(s.traps_closed) })));
      if (s.last) body.append(h('div', { class: 'skp-row' }, h('span', { text: 'Last worked' }), h('b', { text: UI.relTime(s.last) })));
      if ((s.sittings || []).length) {
        body.append(h('h3', { text: 'Sittings with this skill' }));
        const ul = h('ul', { class: 'skp-list' });
        s.sittings.forEach(x => ul.append(h('li', {}, h('a', { href: rx.reportHref(x.id), text: `${kindName(x)} · ${UI.date(x.finished)}` }), h('span', { class: 'meta', text: `${fmt(x.right)} / ${fmt(x.asked)} right` }))));
        body.append(ul);
      }
      if (!o.share && open.length && sh.foot) {
        const b = h('button', { type: 'button', class: 'btn sm', text: `Fix its mistakes · ${fmt(open.length)}` });
        b.addEventListener('click', () => rx.drill({ pool: 'redo', topics: [topic], source: 'mistakes' }, b));
        sh.foot.prepend(b);
      }
    }
    return sh;
  }

  Object.assign(UI, { sittingCard, skillPanel, rx });
})();
