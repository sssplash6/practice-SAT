/* ============================================================================
   SAT Freshman -- Compete's shared pieces (spec/rebuild-v2.md 3.7, 2.4's compete-ui.js
   row; v2-upgrades compete.md C1, C5, C6, C8, C10, C15, C16, C18, C24, C27)

   Loaded after ui.js and kit.js (charts.js too where a page draws a chart) on the
   Compete pages, and by any page that shows a level badge or a board (Me, Results,
   the session summary). Adds to window.UI. Its styles are injected once, on ui.css
   tokens, so a page that loads only this file still draws them.

   UI.level(rating, provisional, size, {level, outline, ring, ringTitle, title}) -> span
       the brand mark's ring filled in ten steps, the digit in the counter; Placing is
       the empty ring with "–"; Level 10 a solid orange square. outline: a Skill rating
       badge (drawn, never filled, C11). ring: a champion's 2px orange ring (C27).
   UI.board(host, data, {columns, label, value(e), pars, mine, rowMenu(e), onFollow(e),
       onMore(offset) -> Promise<data>, onJump(you), youBar, youText(you), empty, find})
       -> {el, update(data), append(data), jump(), highlight(pid)}
       data: {players, entries [{pid, rank, tie, name, anon, level, ring, title, you, mark,
       n, ...metric}], you, next_offset, marks}. Ties read "=4"; par rows (dashed, a flag,
       no rank) sit at their points and never count (C6); your row is wash + amber edge;
       J K / arrows move rows, Enter opens the row menu, F follows, Esc leaves (C24).
   UI.podium(host, entries, {value(e), sub(e), pars}) -> {el}      2 · 1 · 3
   UI.debrief(host, data, {onFilter(qids, label), onFix(row), onRematch(when), sid}) -> {el}
       "Where your points went" (C1): the points bar, the headline, one row per lost item
   UI.pacer(host, pacer, you) -> {el, set(pacer, you)}             the race rail (C8)
   UI.compete  KINDS, kind(c), icon(kind), href(cid, q), runner(res), start(cid, o),
       rulesSeen(kind), markRules(kind), windowLine(c), clockText(c), facts(c), marks(result),
       copyResult(c, result, place, pid), under(host, options, o), subnav(page),
       join(), create(prefill), reminder(), LADDER, levelOf(r), levelIn(r, provisional),
       step(gap, metric, pace), left(iso), when(iso), dayLabel(day)
   ========================================================================== */
(() => {
  const UI = window.UI = window.UI || {};
  const doc = document;
  const h = UI.h || function (tag, attrs = {}, ...kids) {
    const e = doc.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v;
      else if (k === 'html') e.innerHTML = v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat(3)) if (k !== null && k !== undefined && k !== false) e.append(k);
    return e;
  };
  const num = n => (n === null || n === undefined || n === '' || isNaN(n) ? '—' : Number(n).toLocaleString('en-US', { maximumFractionDigits: 1 }));
  const mmss = s => { s = Math.max(0, Math.round(s || 0)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; };
  const tip = (el, t) => { if (!t) return el; if (UI.tooltip) UI.tooltip(el, t); else el.title = t; return el; };
  const api = (p, o) => UI.api(p, o);
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  const put = (host, el) => { if (host) host.append(el); return el; };

  /* ------------------------------------------------------------ styles */
  const CSS = `
.lvl { --s: 20px; position: relative; display: inline-grid; place-items: center; flex: none; width: var(--s); height: var(--s); vertical-align: middle; border-radius: 30%; }
.lvl svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.lvl path { fill: none; stroke-width: 2.4; }
.lvl .t { stroke: var(--mat); } .lvl .f { stroke: var(--amber); } .lvl.outline .t { stroke: var(--soft); }
.lvl b { position: relative; font: 500 calc(var(--s) * .46)/1 var(--mono); color: var(--ink); font-variant-numeric: tabular-nums; }
.lvl.top { background: var(--amber); border-radius: 28%; }
.lvl.top b { color: var(--ink-deep); font-size: calc(var(--s) * .4); font-weight: 700; }
.lvl.ring { box-shadow: 0 0 0 1.5px var(--paper), 0 0 0 3.5px var(--amber); }
.board { position: relative; min-width: 0; }
.board-t { table-layout: auto; }
.board-t :is(th, td) { padding-left: 8px; padding-right: 8px; }
.board-t td { padding-top: 8px; padding-bottom: 8px; }
.board-t td.rk, .board-t th.rk { width: 1%; white-space: nowrap; font: 500 13px var(--mono); padding-right: 6px; }
.board-t td.who { width: 100%; max-width: 0; }
.board-t :is(th, td).n { white-space: nowrap; }
.board-t .who-l { display: flex; align-items: center; gap: 8px; min-width: 0; }
.board-t .who-n { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }
.board-t .who-t, .board-t .who-m { display: block; margin-top: 2px; font: 500 12px var(--mono); color: var(--soft); }
.board-t .who-m { display: none; }
.board-t .you-tag { font: 500 10.5px var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--ink); padding: 2px 6px; border-radius: 5px; background: var(--paper); }
.board-t .mk { display: inline-flex; align-items: center; color: var(--soft); font: 500 11.5px var(--mono); }
.board-t .mk svg { width: 14px; height: 14px; }
.board-t .rowmenu { margin-left: auto; flex: none; width: 32px; height: 32px; border: 0; border-radius: 8px; background: none; color: var(--soft); cursor: pointer; font: 700 16px/1 var(--font); letter-spacing: .05em; }
@media (hover: hover) and (pointer: fine) { .board-t .rowmenu:hover { background: var(--tile-2); color: var(--ink); } }
.board-t tr:focus-visible { outline: 2px solid var(--ink); outline-offset: -2px; }
.board-t tr.par > * { color: var(--soft); background: none; }
.board-t tr.par > td { border-top: 1px dashed var(--faint); border-bottom: 1px dashed var(--faint); }
.board-t tr.par svg { width: 14px; height: 14px; color: var(--soft); vertical-align: -2px; }
.board-t tr.sep > td { padding: 4px 12px; font: 500 11px var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--soft); background: none; }
.board-t tr.hl > * { background: var(--wash-2, var(--wash)); }
.board-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin-top: 14px; }
.board-empty { margin: 14px 0 0; color: var(--soft); }
.youbar { position: sticky; bottom: 0; z-index: 5; display: flex; flex-wrap: wrap; align-items: center; gap: 6px 14px; margin-top: 12px; padding: 10px 14px; border-radius: 10px; background: var(--wash); box-shadow: inset 3px 0 0 var(--amber), 0 -8px 16px -12px rgba(30, 30, 30, .35); font: 500 13px var(--mono); color: var(--ink); }
.youbar > span { flex: 1 1 240px; min-width: 0; }
.youbar[hidden], .debrief-rows li[hidden] { display: none; }
@media (max-width: 759px) {
  .board-t .who-m { display: block; }
  .board-t :is(th, td).off-phone { display: none; }
  .youbar { bottom: calc(64px + env(safe-area-inset-bottom, 0px)); }
}
.podium { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); align-items: end; gap: 12px; }
.pod { display: grid; align-content: end; justify-items: center; gap: 6px; min-width: 0; padding: 14px 10px 16px; border-radius: 12px; background: var(--tile); text-align: center; }
.pod.p1 { min-height: 156px; background: var(--tile-2); } .pod.p2 { min-height: 132px; } .pod.p3 { min-height: 116px; }
.pod.you { background: var(--wash); box-shadow: inset 0 0 0 1.5px var(--amber); }
.pod.open, .pod.parp { background: none; box-shadow: inset 0 0 0 1.5px var(--line); }
.pod.parp { box-shadow: none; border: 1.5px dashed var(--faint); }
.pod .num { font-size: 30px; }
.pod .pod-n { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 700; }
.pod .pod-v { font: 500 14px var(--mono); } .pod .pod-s { font: 500 11.5px var(--mono); color: var(--soft); }
.pod svg.tro { width: 18px; height: 18px; color: var(--ink); }
.debrief { display: grid; gap: 14px; }
.debrief-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; }
.debrief-line { font: 600 15px/1.4 var(--font); }
.debrief-rows { display: grid; gap: 0; margin: 0; padding: 0; list-style: none; }
.debrief-rows li { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 4px 14px; padding: 10px 0; border-top: 1px solid var(--line); }
.debrief-rows .dr-t { font: 500 14px/1.4 var(--font); }
.debrief-rows .dr-m { display: block; margin-top: 2px; font: 500 12px var(--mono); color: var(--soft); }
.debrief-rows .chip-s { display: inline-block; margin-left: 6px; padding: 1px 6px; border-radius: 5px; background: var(--tile-2); font: 500 11px var(--mono); color: var(--ink); vertical-align: 1px; }
.debrief-act { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; }
.pacer { display: grid; gap: 4px; }
.pacer-tr { position: relative; height: 6px; border-radius: 3px; background: var(--mat); }
.pacer-tr > i { position: absolute; inset: 0 auto 0 0; border-radius: inherit; background: var(--amber); }
.pacer-tr.them > i { background: var(--ink); }
.pacer-l { font: 500 12px var(--mono); color: var(--soft); text-align: right; }
.subnav { display: flex; flex-wrap: wrap; gap: 0 4px; margin: 10px 0 22px -9px; }
.subnav a { position: relative; display: inline-flex; align-items: center; height: 38px; padding: 0 9px; font: 600 15px var(--font); color: var(--faint); text-decoration: none; }
.subnav a[aria-current="page"] { color: var(--ink); }
.subnav a[aria-current="page"]::after { content: ""; position: absolute; left: 9px; right: 9px; bottom: 4px; height: 2px; border-radius: 2px; background: var(--amber); }
@media (hover: hover) and (pointer: fine) { .subnav a:hover { color: var(--ink); } }
.cx-form { display: grid; gap: 18px; }
.cx-form fieldset { margin: 0; padding: 0; border: 0; min-width: 0; }
.cx-form legend { padding: 0; margin-bottom: 6px; font: 600 13.5px/1.3 var(--font); }
.cx-skills { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 18px; }
.cx-skills .dom { display: grid; gap: 4px; align-content: start; }
.cx-skills label { display: flex; align-items: center; gap: 8px; min-height: 30px; font: 500 14px var(--font); }
.cx-skills .dom > label:first-child { font-weight: 700; }
.cx-radio { display: grid; gap: 6px; } .cx-radio label { display: flex; align-items: flex-start; gap: 8px; font: 500 14px/1.4 var(--font); }
.cx-sum { font: 500 13px var(--mono); color: var(--soft); }
.cx-code { font: 500 44px/1 var(--mono); letter-spacing: .12em; }
.cx-err { color: var(--ink); font-weight: 600; }
@media (max-width: 759px) { .cx-skills { grid-template-columns: minmax(0, 1fr); } }
`;
  if (!doc.getElementById('compete-ui-css')) doc.head.append(h('style', { id: 'compete-ui-css', text: CSS }));

  /* ------------------------------------------------------------ icons */
  const L = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"';
  const SVG = {
    flag: `<path ${L} d="M6 21V4M6 4h10l-2 4 2 4H6"/>`,
    sheet: `<path ${L} d="M7 3h7l4 4v14H7zM14 3v4h4M10 12h5M10 16h5"/>`,
    trap: `<circle ${L} cx="12" cy="12" r="8"/><path ${L} d="M8 8l8 8M12 4v4"/>`,
    strikes: `<path ${L} d="M4 9l4 6M8 9l-4 6M10 9l4 6M14 9l-4 6M16 9l4 6M20 9l-4 6"/>`,
    star: `<path ${L} d="M12 4l2.4 5 5.4.6-4 3.7 1.1 5.3L12 16l-4.9 2.6 1.1-5.3-4-3.7 5.4-.6z"/>`,
    clean: `<circle ${L} cx="12" cy="12" r="8"/><path ${L} d="M8.5 12.2l2.4 2.4 4.6-5"/>`,
    dots: `<circle cx="6" cy="12" r="1.6" fill="currentColor"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/><circle cx="18" cy="12" r="1.6" fill="currentColor"/>`,
  };
  const svgOf = (inner, size = 18, cls = '') => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"${cls ? ` class="${cls}"` : ''}>${inner}</svg>`;
  function icon(kind, size = 20) {
    const k = KINDS[kind] || KINDS.daily;
    const inner = SVG[k.icon] || (UI.ICON && UI.ICON[k.icon]) || SVG.flag;
    return h('span', { class: 'kind-ic', 'aria-hidden': 'true', html: svgOf(inner, size) });
  }

  /* ------------------------------------------------------------ the contest model on screen */
  const KINDS = {
    daily: { label: 'Daily Challenge', icon: 'trophy', clock: 'answer', pace: true, twins: true },
    sprint: { label: 'Sprint', icon: 'bolt', clock: 'answer', runs: true },
    weekly: { label: 'Weekly Module', icon: 'sheet', clock: 'wall', twins: true },
    final: { label: 'Season Final', icon: 'flag', clock: 'wall', twins: true },
    private: { label: 'Private contest', icon: 'users', clock: 'answer', pace: true },
    trap: { label: 'Trap of the week', icon: 'trap', clock: 'answer', pace: true, twins: true },
    rush: { label: 'Rush', icon: 'strikes', clock: 'none', runs: true },
    words: { label: 'Word Sprint', icon: 'words', clock: 'answer', runs: true },
  };
  const kind = c => KINDS[(c && c.kind) || 'daily'] || KINDS.daily;
  // a contest's title as students read it: "Sprint · Geometry & Trig week", "Weekly Module · Week 40"
  function title(c) {
    const dshort = d => ((UI.DOMAINS || []).find(x => x[0] === d) || [])[1] || d;
    const wk = String(c.id || '').match(/-(\d{4})-W(\d{2})/);
    if (c.kind === 'sprint' && c.spec && c.spec.theme) return `Sprint · ${dshort(c.spec.theme)} week`;
    if (c.kind === 'weekly' && wk) return `Weekly Module · Week ${+wk[2]}`;
    if (c.kind === 'final' && c.spec && c.spec.sat_date) return `Season Final · Road to ${dayLabel(c.spec.sat_date, { weekday: false })}`;
    return String(c.title || kind(c).label).replace(/(\d{4})-W(\d{2})/, (_, y, w) => `Week ${+w}`);
  }
  const href = (cid, q = {}) => {
    const p = new URLSearchParams({ id: cid, ...Object.fromEntries(Object.entries(q).filter(([, v]) => v !== null && v !== undefined && v !== '')) });
    return `/compete/contest/?${p}`;
  };
  function runner(res) {
    if (!res || !res.session) return null;
    if (res.runner === 'test') return `/test/?s=${encodeURIComponent(res.session)}`;
    if (res.runner === 'words') return `/words/run/?id=${encodeURIComponent(res.session)}`;
    return `/practice/session/?id=${encodeURIComponent(res.session)}`;
  }
  const RULES_KEY = k => `satf.rules.${k}`;
  const rulesSeen = k => { try { return !!localStorage.getItem(RULES_KEY(k)); } catch (_) { return false; } };
  const markRules = k => { try { localStorage.setItem(RULES_KEY(k), '1'); } catch (_) {} };
  async function start(cid, o = {}) {
    const q = new URLSearchParams();
    if (o.race) q.set('race', o.race);
    if (o.domain && o.domain !== 'all') q.set('domain', o.domain);
    if (o.kind) markRules(o.kind);
    const res = await api(`/contest/${encodeURIComponent(cid)}/start${q.toString() ? '?' + q : ''}`, { method: 'POST', body: {} });
    const to = runner(res);
    if (to) location.href = to;
    return res;
  }

  const when = iso => { try { return new Date(iso).toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' }); } catch (_) { return ''; } };
  const dayLabel = (day, o = {}) => { try { return new Date(`${day}T12:00:00`).toLocaleDateString('en-US', { weekday: o.weekday === false ? undefined : 'short', month: 'short', day: 'numeric' }); } catch (_) { return day; } };
  function left(iso, now = Date.now()) {
    let s = Math.max(0, Math.round((new Date(iso) - now) / 1000));
    const d = Math.floor(s / 86400); s -= d * 86400;
    const hh = Math.floor(s / 3600); s -= hh * 3600;
    const m = Math.floor(s / 60);
    if (d) return `${d}d ${String(hh).padStart(2, '0')}h`;
    if (hh) return `${hh}h ${String(m).padStart(2, '0')}m`;
    return `${Math.max(1, m)}m`;
  }
  function windowLine(c) {
    if (!c) return '';
    if (c.kind === 'daily' && c.status === 'live') return 'Open until 11:59 PM your time';
    if (c.series && c.round) {
      const r = `Round ${c.round}${c.spec && c.spec.repeat && c.spec.repeat.rounds ? ` of ${c.spec.repeat.rounds}` : ''}`;
      return c.status === 'upcoming' ? `${r} · opens ${when(c.opens)}` : c.status === 'live' ? `${r} · closes ${when(c.closes)}` : `${r} · ended ${when(c.closes)}`;
    }
    if (c.status === 'upcoming') return `Opens ${when(c.opens)} · in ${left(c.opens)}`;
    if (c.status === 'live') return `Ends ${when(c.closes)} · in ${left(c.closes)}`;
    return `Ended ${when(c.closes)}`;
  }
  function clockText(c) {
    const k = kind(c);
    if (c.kind === 'rush') return '3 strikes';
    if (k.clock === 'wall') return `${Math.round((c.seconds || 2100) / 60)} min${c.kind === 'final' ? ' · 2 modules' : ''}`;
    return c.seconds ? `${mmss(c.seconds)} answer clock` : 'answer clock';
  }
  function facts(c) {
    const out = [];
    if (c.kind === 'sprint') out.push('as many as you answer');
    else if (c.kind === 'rush') out.push('difficulty climbs with you');
    else if (c.count) out.push(`${c.count} questions`);
    out.push(clockText(c));
    if (kind(c).twins || (c.kind === 'private' && c.spec && c.spec.twin)) out.push('your own twin questions');
    const n = c.field && c.field.players;
    if (n) out.push(`${num(n)} in`);
    return out.join(' · ');
  }
  // UI.STATES keys for a finished sitting's answer squares
  function marks(result) {
    const qs = (result && result.questions) || [];
    return qs.map(q => ({ status: { correct: 'correct', incorrect: 'incorrect', skipped: 'skipped', voided: 'voided', blank: 'unanswered', unanswered: 'unanswered' }[q.status] || q.status || 'unanswered', n: q.n }));
  }
  const glyphOf = s => ({ correct: '■', incorrect: '□' }[s] || '·');
  function copyResult(c, r, place = {}, pid = null) {
    const k = kind(c);
    const day = c.kind === 'daily' ? ` · ${dayLabel(String(c.id).slice(6), { weekday: false })}` : '';
    const clock = r && r.secs !== undefined ? ` · ${mmss(r.secs)}` : '';
    const rank = place.rank ? ` · #${place.rank} of ${num(place.players)}` : '';
    const url = `${location.origin}${href(c.id, pid ? { race: pid } : {})}`;
    return [`SAT Freshman · ${k.label}${day}`,
      `${num(r.right)}/${num(r.asked || c.count)} · ${num(r.points)} pts${clock}${rank}`,
      marks(r).map(m => glyphOf(m.status)).join(''),
      pid ? `Beat ${num(r.points)}: ${url}` : url].join('\n');
  }

  /* ------------------------------------------------------------ the ladder, par and field lines (C5, C7) */
  const pct = x => (x === null || x === undefined ? '—' : `${Math.round(x * 100)}%`);
  function ladder(host, c) {
    const n = (c.ladder || []).length;
    const cells = h('div', { class: 'ladder', role: 'list', style: n > 10 ? `--cols:${Math.min(11, n)}` : null, 'aria-label': 'The questions: skill, difficulty and your chance' });
    (c.ladder || []).forEach(q => {
      const name = topicName(q.topic);
      const label = [`Q${q.slot}`, name, TIER[q.tier] || q.tier, q.format === 'spr' ? 'grid-in' : null,
        q.chance !== undefined && q.chance !== null ? `your chance ${pct(q.chance)}` : null].filter(Boolean).join(' · ');
      const cell = h('div', { class: 'lad', role: 'listitem', tabindex: '0', 'aria-label': label },
        h('span', { class: 'n', text: String(q.slot) }),
        UI.glyph ? UI.glyph(q.topic) : null,
        UI.dbars ? UI.dbars(q.tier, { bare: true }) : null,
        q.format === 'spr' ? h('span', { class: 'gi', text: 'GI' }) : null,
        q.chance !== undefined && q.chance !== null ? h('span', { class: 'ch', 'aria-hidden': 'true' }, h('i', { style: `width:${Math.round(q.chance * 100)}%` })) : null);
      tip(cell, label);
      cells.append(cell);
    });
    put(host, cells);
    put(host, h('p', { class: 'meta ladder-legend', text: 'Bars: difficulty · GI: grid-in, you type the answer · underline: your chance' }));
    return cells;
  }
  function parLine(c) {
    const p = c.me && c.me.par, f = c.me && c.me.forecast;
    if (!p || p.base === undefined || p.base === null) return null;
    const el = h('p', { class: 'line' }, `${p.rough ? 'Your par (rough)' : 'Your par'} ${num(p.base)} · about ${num(p.right)} right`,
      f ? ` · likely #${f.lo}–#${f.hi} of ~${num(f.of)}` : '');
    tip(el, 'What a student at your rating scores on these questions, on average.' + (p.rough ? ' Rough while you are placing or the questions are new.' : ''));
    return el;
  }
  function fieldLine(c, verb = 'finished') {
    const f = c.field || {};
    if (!f.players) return h('p', { class: 'meta', text: 'No one has finished yet.' });
    return h('p', { class: 'meta', text: [`${num(f.players)} ${verb}`, f.sitting_now ? `${num(f.sitting_now)} sitting now` : null,
      f.median_points !== null && f.median_points !== undefined ? `median ${num(f.median_points)} pts` : null,
      f.best !== null && f.best !== undefined ? `best ${num(f.best)}` : null].filter(Boolean).join(' · ') });
  }

  /* ------------------------------------------------------------ levels (spec/rating.md) */
  const LADDER = [800, 950, 1100, 1250, 1400, 1550, 1700, 1850, 2000];
  const levelOf = r => 1 + LADDER.filter(x => (r || 0) > x).length;
  const rangeOf = n => n === 1 ? '800 or less' : n === 10 ? '2,001 and up' : `${num(LADDER[n - 2] + 1)}–${num(LADDER[n - 1])}`;
  // "Level 4 in +17 ≈ 2 hard rights" (C11): ceil(gap / (K × (1 − E_hard)))
  // ponytail: E_hard uses the hard tier's prior (1,300) until the server sends the mean hard item rating
  function levelIn(rating, provisional, hardItem = 1300) {
    const n = levelOf(rating);
    if (n >= 10 || rating === null || rating === undefined) return null;
    const gap = LADDER[n - 1] + 1 - rating;
    const K = provisional ? 32 : 12;
    const E = 1 / (1 + Math.pow(10, (hardItem - rating) / 400));
    return { level: n + 1, gap: Math.ceil(gap), rights: Math.max(1, Math.ceil(gap / (K * (1 - E)))) };
  }
  const SEGS = [[2.5, 22.5], [27.5, 47.5], [52.5, 72.5], [77.5, 97.5]];
  const RING = 'M12 2.8H15.4A6.2 6.2 0 0 1 21.2 8.6V15.4A6.2 6.2 0 0 1 15.4 21.2H8.6A6.2 6.2 0 0 1 2.8 15.4V8.6A6.2 6.2 0 0 1 8.6 2.8Z';
  function fillDash(len) {
    const out = [0]; let pos = 0;
    for (const [a, b] of SEGS) { const e = Math.min(b, len); if (e <= a) break; out.push(a - pos, e - a); pos = e; }
    out.push(100);
    return out.join(' ');
  }
  function level(rating, provisional, size = 20, o = {}) {
    const n = o.level ?? (rating === null || rating === undefined ? null : levelOf(rating));
    const placing = !!provisional || n === null || n === undefined;
    const el = h('span', { class: 'lvl' + (o.outline ? ' outline' : '') + (o.ring ? ' ring' : '') + (!placing && n >= 10 && !o.outline ? ' top' : ''),
      style: `--s:${size}px`, role: 'img', 'aria-label': (placing ? 'Placing' : `Level ${n}`) + (o.outline ? ', skill rating' : '') });
    if (!placing && n >= 10 && !o.outline) el.append(h('b', { text: '10' }));
    else {
      el.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="t" pathLength="100" stroke-dasharray="20 5" stroke-dashoffset="-2.5" d="${RING}"/>${placing || o.outline ? '' : `<path class="f" pathLength="100" stroke-dasharray="${fillDash(n * 10)}" d="${RING}"/>`}</svg>`;
      el.append(h('b', { text: placing ? '–' : String(n) }));
    }
    tip(el, o.title || [placing ? 'Placing: the level shows after 30 rated answers' : `Level ${n} · rating ${rangeOf(n)}`, o.ringTitle].filter(Boolean).join(' · '));
    return el;
  }

  /* ------------------------------------------------------------ the cheapest step past the next student (C10) */
  function step(gap, metric = 'points', pace = true) {
    if (!gap || gap <= 0) return '';
    if (metric === 'rating') return `about ${Math.max(1, Math.ceil(gap / 9))} hard rights at your level`;
    if (metric === 'right') return `${num(gap)} right answer${gap === 1 ? '' : 's'}`;
    if (metric === 'net') return `beat par by ${num(gap)} more`;
    if (metric !== 'points') return '';
    const tiers = pace ? [[15, 'easy'], [25, 'medium'], [35, 'hard']] : [[10, 'easy'], [20, 'medium'], [30, 'hard']];
    const one = tiers.find(([v]) => v >= gap);
    if (one) return `one ${one[1]} right${pace ? ' at pace' : ''}`;
    const hard = tiers[2][0];
    return `${Math.ceil(gap / hard)} hard rights`;
  }
  const titleText = t => t ? `Champion · ${t.period_label || t.period || ''}${t.board ? ` · ${{ points: 'Points', net: 'Over par', change: 'Most improved' }[t.board] || t.board}` : ''}${t.place ? ` #${t.place}` : ''}` : '';

  /* ------------------------------------------------------------ underline choice (the .choices style) */
  function under(host, options, o = {}) {
    let value = o.value !== undefined ? o.value : options[0] && (options[0].value ?? options[0]);
    const el = h('div', { class: 'choices' + (o.className ? ' ' + o.className : ''), role: 'group', 'aria-label': o.label || null });
    const btns = options.map(x0 => {
      const x = typeof x0 === 'object' ? x0 : { value: x0, label: String(x0) };
      const b = h('button', { type: 'button', 'aria-pressed': 'false', disabled: x.disabled || null }, x.label,
        x.n !== undefined && x.n !== null ? h('span', { class: 'n', text: ` (${num(x.n)})` }) : null);
      b._x = x;
      if (x.why) tip(b, x.why);
      b.addEventListener('click', () => { if (b.disabled || value === x.value) return; value = x.value; sync(); if (o.onChange) o.onChange(value, x); });
      return b;
    });
    el.append(...btns);
    el.addEventListener('keydown', e => {
      const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      const i = btns.indexOf(doc.activeElement);
      if (!d || i < 0) return;
      e.preventDefault();
      const j = (i + d + btns.length) % btns.length;
      btns[j].focus();
    });
    function sync() { btns.forEach(b => b.setAttribute('aria-pressed', String(b._x.value === value))); }
    sync();
    put(host, el);
    return {
      el, get value() { return value; },
      set(v, silent) { value = v; sync(); if (!silent && o.onChange) o.onChange(v); },
      count(v, n) { const b = btns.find(x => x._x.value === v); if (b) { let s = b.querySelector('.n'); if (!s) { s = h('span', { class: 'n' }); b.append(s); } s.textContent = n === null || n === undefined ? '' : ` (${num(n)})`; } },
      disable(v, why) { const b = btns.find(x => x._x.value === v); if (b) { b.disabled = !!why; b.title = why || ''; } },
    };
  }

  function subnav(page) {
    const items = [['overview', '/compete/', 'Overview'], ['leaderboard', '/compete/leaderboard/', 'Leaderboard'], ['rankings', '/compete/rankings/', 'Your rankings']];
    return h('nav', { class: 'subnav', 'aria-label': 'Compete' },
      items.map(([id, href0, label]) => h('a', { href: href0, 'aria-current': id === page ? 'page' : null, text: label })));
  }

  /* ------------------------------------------------------------ UI.board */
  const FLAG = svgOf(SVG.flag, 14);
  function board(host, data, o = {}) {
    const el = h('div', { class: 'board' });
    const legendLine = h('p', { class: 'meta board-legend', hidden: true });
    const wrap = h('div', { class: 'table-wrap' });
    const table = h('table', { class: 'table board-t hover', role: 'grid', 'aria-label': o.label || 'Board' });
    const thead = h('thead'), tbody = h('tbody');
    const empty = h('p', { class: 'board-empty', hidden: true });
    const foot = h('div', { class: 'board-foot' });
    const bar = h('div', { class: 'youbar', hidden: true, role: 'status' });
    table.append(thead, tbody);
    wrap.append(table);
    el.append(legendLine, wrap, empty, foot);
    if (o.youBar !== false) el.append(bar);
    put(host, el);
    const val = o.value || (e => e.points ?? e.value);
    let d = data || {}, list = [], youRow = null, obs = null;
    const cols = () => (o.columns || []).filter(c => list.some(e => !e.sep && (!e.par || c.par) && c.value(e) !== null && c.value(e) !== undefined && c.value(e) !== ''));

    function markEl(e) {
      if (e.mark === 'clean') return tip(h('span', { class: 'mk', html: svgOf(SVG.clean, 14), role: 'img', 'aria-label': 'Clean' }), 'Clean: nothing flagged');
      if (e.mark === 'confirmed') return tip(h('span', { class: 'mk', text: `✓${e.n || ''}` }), `${e.n || 'All'} answer${e.n === 1 ? '' : 's'} confirmed on new numbers`);
      return null;
    }
    function menuBtn(e) {
      if (!o.rowMenu || e.you || e.par || e.sep || !e.pid || e.name === 'Anonymous') return null;
      const b = h('button', { type: 'button', class: 'rowmenu', 'aria-label': `More for ${e.name}`, 'aria-haspopup': 'menu', html: svgOf(SVG.dots, 18) });
      b.addEventListener('click', ev => { ev.stopPropagation(); const items = o.rowMenu(e); if (items && items.length && UI.menu) UI.menu(b, items, { label: e.name }); });
      return b;
    }
    function row(e, cs) {
      if (e.sep) return h('tr', { class: 'sep' }, h('td', { colspan: 2 + cs.length, text: e.sep }));
      const tr = h('tr', { class: [e.you && 'you', e.par && 'par'].filter(Boolean).join(' ') || null, tabindex: '-1',
        'aria-current': e.you ? 'true' : null, 'data-pid': e.pid || null });
      tr._e = e;
      const rank = e.par ? h('td', { class: 'rk', html: FLAG, title: 'Par: never ranked' }) : h('td', { class: 'rk', text: `${e.tie ? '=' : ''}${e.rank ?? ''}` });
      const off = cs.filter(c => !c.phone).map(c => { const v = c.value(e); return v === null || v === undefined || v === '' ? null : (c.short ? `${v}` : v); }).filter(Boolean);
      const who = h('td', { class: 'who' },
        h('span', { class: 'who-l' },
          e.par ? null : level(null, false, 20, { level: e.level, ring: e.ring, ringTitle: titleText(e.title) }),
          h('span', { class: 'who-n', text: e.par ? e.label : e.name }),
          e.you ? h('span', { class: 'you-tag', text: 'You' }) : null,
          markEl(e), menuBtn(e)),
        e.title && !e.par ? h('span', { class: 'who-t', text: titleText(e.title) }) : null,
        off.length ? h('span', { class: 'who-m', text: off.join(' · ') }) : null);
      tr.append(rank, who, ...cs.map(c => { const v = e.par && !c.par ? '' : c.value(e); return h('td', { class: (c.num !== false ? 'n' : '') + (c.phone ? '' : ' off-phone'), text: v === null || v === undefined ? '—' : String(v) }); }));
      return tr;
    }
    function withPars(entries) {
      const pars = o.pars ? (o.pars() || []) : [];
      if (!pars.length) return entries;
      const out = [...entries];
      pars.forEach(p => {
        const at = out.findIndex(e => !e.par && !e.sep && (val(e) ?? -Infinity) < p.value);
        const row0 = { par: true, label: p.label, value: p.value, points: p.value };
        if (at < 0) out.push(row0); else out.splice(at, 0, row0);
      });
      return out;
    }
    function draw() {
      list = withPars((d.entries || []).slice());
      const cs = cols();
      thead.replaceChildren(h('tr', {}, h('th', { scope: 'col', class: 'rk', text: 'Rank' }), h('th', { scope: 'col', text: 'Student' }),
        cs.map(c => { const th = h('th', { scope: 'col', class: (c.num !== false ? 'n' : '') + (c.phone ? '' : ' off-phone'), text: c.label }); if (c.title) tip(th, c.title); return th; })));
      tbody.replaceChildren(...list.map(e => row(e, cs)));
      const rows = [...tbody.rows].filter(r => r._e);
      rows.forEach((r, i) => { r.tabIndex = i === 0 ? 0 : -1; });
      const real = (d.entries || []).length;
      empty.hidden = real > 0;
      empty.textContent = real ? '' : (o.empty || 'No one has finished yet.');
      if (d.marks && (d.marks.clean || d.marks.confirmed)) {
        legendLine.hidden = false;
        legendLine.replaceChildren(h('span', { class: 'mk', html: svgOf(SVG.clean, 14) }), ` ${num(d.marks.clean || 0)} clean`,
          d.marks.confirmed ? ` · ✓ ${num(d.marks.confirmed)} with confirms` : '');
        tip(legendLine, 'Clean: nothing was flagged. ✓n: n answers were confirmed on new numbers. No mark: a confirm failed, so the Voided count says it.');
      } else legendLine.hidden = true;
      foot.replaceChildren();
      if (d.next_offset !== null && d.next_offset !== undefined && o.onMore) {
        const b = h('button', { type: 'button', class: 'btn', text: 'Show 50 more' });
        b.addEventListener('click', async () => {
          b.disabled = true;
          try { const more = await o.onMore(d.next_offset); api0.append(more); } catch (_) { b.disabled = false; toast('Couldn’t load more. Try again.'); }
        });
        foot.append(b);
      } else if (real) foot.append(h('p', { class: 'meta', text: `That’s everyone: ${num(d.players ?? real)} student${(d.players ?? real) === 1 ? '' : 's'}.` }));
      youRow = rows.find(r => r._e.you) || null;
      drawBar();
    }
    function drawBar() {
      if (obs) { obs.disconnect(); obs = null; }
      const you = d.you;
      if (!you || o.youBar === false) { bar.hidden = true; return; }
      const text = o.youText ? o.youText(you) : `You · #${you.rank} · ${num(val(you))}`;
      if (!text) { bar.hidden = true; return; }
      const jump = h('button', { type: 'button', class: 'quiet', text: 'Jump to me' });
      jump.addEventListener('click', () => api0.jump());
      bar.replaceChildren(h('span', { text }), ...(youRow || o.onJump ? [jump] : []));
      if (youRow && 'IntersectionObserver' in window) {
        obs = new IntersectionObserver(es => { bar.hidden = es.some(x => x.isIntersecting); }, { threshold: 0.6 });
        obs.observe(youRow);
      } else bar.hidden = false;
    }
    table.addEventListener('keydown', e => {
      if (e.target.closest('button') && e.key !== 'Escape') return;
      const rows = [...tbody.rows].filter(r => r._e);
      const i = rows.indexOf(e.target.closest('tr'));
      const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
      if (k === 'j' || k === 'ArrowDown' || k === 'k' || k === 'ArrowUp') {
        if (e.shiftKey || e.metaKey || e.ctrlKey || e.altKey) return;
        e.preventDefault();
        const j = Math.max(0, Math.min(rows.length - 1, (i < 0 ? 0 : i) + (k === 'j' || k === 'ArrowDown' ? 1 : -1)));
        rows.forEach(r => { r.tabIndex = -1; });
        rows[j].tabIndex = 0; rows[j].focus();
      } else if (k === 'Enter' && i >= 0) {
        const b = rows[i].querySelector('.rowmenu');
        if (b) { e.preventDefault(); b.click(); }
      } else if (k === 'f' && i >= 0 && o.onFollow && !e.metaKey && !e.ctrlKey) {
        const r = rows[i]._e;
        if (!r.you && !r.par && r.pid && r.name !== 'Anonymous') { e.preventDefault(); o.onFollow(r); }
      } else if (k === 'Escape') {
        e.preventDefault(); e.stopPropagation();
        wrap.tabIndex = -1; wrap.focus();
      }
    });
    const api0 = {
      el,
      update(nd) { d = nd || {}; draw(); },
      append(more) { d = { ...d, ...more, entries: [...(d.entries || []), ...((more && more.entries) || [])] }; draw(); },
      jump() {
        if (youRow) { youRow.scrollIntoView({ block: 'center', behavior: UI.reduced && UI.reduced() ? 'auto' : 'smooth' }); youRow.tabIndex = 0; youRow.focus({ preventScroll: true }); }
        else if (o.onJump && d.you) o.onJump(d.you);
      },
      highlight(pid) {
        const r = [...tbody.rows].find(x => x._e && x._e.pid === pid);
        tbody.querySelectorAll('tr.hl').forEach(x => x.classList.remove('hl'));
        if (!r) return false;
        r.classList.add('hl'); r.scrollIntoView({ block: 'center' }); r.tabIndex = 0; r.focus({ preventScroll: true });
        return true;
      },
      find(name) {
        const q = String(name || '').trim().toLowerCase();
        const e = (d.entries || []).find(x => x.name && x.name.toLowerCase() === q && x.name !== 'Anonymous');
        return e ? api0.highlight(e.pid) : false;
      },
      get data() { return d; },
    };
    draw();
    return api0;
  }

  /* ------------------------------------------------------------ UI.podium */
  const TROPHY = UI.ICON && UI.ICON.trophy ? svgOf(UI.ICON.trophy, 18, 'tro') : '';
  function podium(host, entries, o = {}) {
    const el = h('div', { class: 'podium', role: 'list', 'aria-label': 'Top three' });
    const value = o.value || (e => num(e.value ?? e.points));
    [1, 0, 2].forEach(i => {
      const e = entries[i];
      const p = !e && o.pars && o.pars[i];
      const card = h('div', { role: 'listitem', class: `pod p${i + 1}${e && e.you ? ' you' : ''}${!e ? (p ? ' parp' : ' open') : ''}` });
      if (e) {
        if (i === 0 && TROPHY) card.append(h('span', { html: TROPHY }));
        card.append(
          h('span', { class: 'num', text: `${e.tie ? '=' : ''}${e.rank}` }),
          level(null, false, 32, { level: e.level, ring: e.ring, ringTitle: titleText(e.title) }),
          h('span', { class: 'pod-n', text: e.you ? `${e.name} (you)` : e.name }),
          h('span', { class: 'pod-v', text: value(e) }),
          ...(o.sub && o.sub(e) ? [h('span', { class: 'pod-s', text: o.sub(e) })] : []));
      } else if (p) card.append(h('span', { html: FLAG }), h('span', { class: 'pod-n', text: p.label }), h('span', { class: 'pod-v', text: num(p.value) }), h('span', { class: 'pod-s', text: 'par' }));
      else card.append(h('span', { class: 'num', text: String(i + 1) }), h('span', { class: 'pod-s', text: 'Open' }));
      el.append(card);
    });
    put(host, el);
    return { el };
  }

  /* ------------------------------------------------------------ UI.debrief (C1) */
  const CAUSE = { trap: 'Traps', slip: 'Slips', clock: 'Clock', entry: 'Entry', gap: 'Gaps', skip: 'Skipped', void: 'Voided', pace: 'Over budget', finish: 'Finish bonus' };
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const topicName = t => (UI.TOPIC && UI.TOPIC[t] ? UI.TOPIC[t].short : String(t || '').replace(/_/g, ' '));
  function debrief(host, d, o = {}) {
    const el = h('section', { class: 'debrief', 'aria-label': 'Where your points went' });
    put(host, el);
    if (!d || d.max === undefined) return { el };
    const lost = d.lost || [];
    const miss = d.max - d.points;
    const ranked = (d.players || 0) >= 2;
    el.append(h('div', { class: 'debrief-head' }, h('h2', { class: 'h2', text: 'Where your points went' }),
      h('span', { class: 'meta', text: miss > 0 ? `${num(miss)} of ${num(d.max)} left` : `${num(d.points)} of ${num(d.max)}` })));
    if (!lost.length || miss <= 0) {
      el.append(h('p', { class: 'debrief-line', text: `Nothing left on the table. ${num(d.points)} of ${num(d.max)}.` }));
      return { el };
    }
    // the points bar: scored, then each cause; a segment filters Review to its questions
    const groups = {};
    lost.forEach(r => { const g = groups[r.kind] || (groups[r.kind] = { key: r.kind, label: CAUSE[r.kind] || r.kind, value: 0, n: 0, qids: [] }); g.value += r.pts; g.n += 1; if (r.qid) g.qids.push(r.qid); });
    const segs = [{ key: 'scored', label: 'Scored', value: d.points, n: null }, ...Object.values(groups).sort((a, b) => b.value - a.value)];
    const barHost = h('div');
    el.append(barHost);
    if (UI.stackBar) {
      UI.stackBar(barHost, segs.map(s => ({ ...s, label: s.key === 'scored' ? `${num(d.max)} possible → scored` : `${s.label} −`, tip: s.key === 'scored' ? null : `${s.label}: −${num(s.value)} on ${s.n} question${s.n === 1 ? '' : 's'}` })),
        { total: d.max, unit: 'pts', noun: 'questions', label: 'Where your points went', legend: true,
          onPick: s => { if (s.key !== 'scored' && o.onFilter) o.onFilter(groups[s.key].qids, `${groups[s.key].label} · ${groups[s.key].n}`); } });
    } else {
      barHost.append(h('p', { class: 'meta', text: segs.slice(1).map(s => `${s.label} −${num(s.value)} (${s.n})`).join(' · ') }));
    }
    if (o.onFilter && !UI.stackBar) {
      const chips = h('div', { class: 'debrief-act' }, segs.slice(1).map(s => {
        const b = h('button', { type: 'button', class: 'quiet', text: `${s.label} −${num(s.value)} (${s.n})` });
        b.addEventListener('click', () => o.onFilter(s.qids, `${s.label} · ${s.n}`));
        return b;
      }));
      el.append(chips);
    }
    // the headline: the one fix that moves you most, else all of them
    const best = ranked ? lost.filter(r => r.places > 0).sort((a, b) => b.places - a.places || b.pts - a.pts)[0] : null;
    if (ranked) {
      el.append(h('p', { class: 'debrief-line', text: best
        ? `Q${best.slot} right would have put you #${best.rank_if}${best.rank_if <= 3 ? ': one fix from the podium.' : '.'}`
        : `All of them right → #${d.all_right_rank} of ${num(d.players)}.` }));
    }
    const rows = [...lost].sort((a, b) => (b.places || 0) - (a.places || 0) || b.pts - a.pts);
    const ul = h('ul', { class: 'debrief-rows' });
    rows.forEach(r => {
      const what = r.kind === 'trap' || r.kind === 'slip' || r.kind === 'entry' ? `fell for ${r.label}` : (CAUSE[r.kind] || r.kind).toLowerCase();
      const text = [`Q${r.slot}`, r.topic && topicName(r.topic), TIER[r.tier], what, `−${num(r.pts)}`].filter(Boolean).join(' · ');
      const sub = ranked && r.rank_if ? `right → #${r.rank_if}${r.places ? ` (+${r.places} place${r.places === 1 ? '' : 's'})` : ''}` : '';
      let act = null;
      if (o.onFix) {
        const label = ['trap', 'slip', 'gap', 'entry'].includes(r.kind) ? 'Fix it · 3' : r.kind === 'clock' || r.kind === 'pace' ? 'Speed drill · 8' : r.kind === 'skip' ? 'Try it now' : null;
        if (label) { act = h('button', { type: 'button', class: 'quiet', text: label }); act.addEventListener('click', () => o.onFix(r, label)); }
      }
      ul.append(h('li', {}, h('span', { class: 'dr-t' }, text, r.rushed ? tip(h('span', { class: 'chip-s', text: 'rushed' }), 'Answered in under a quarter of its time budget') : null,
        sub ? h('span', { class: 'dr-m', text: sub }) : null), act));
    });
    if (ranked && d.all_right_rank) ul.append(h('li', {}, h('span', { class: 'dr-t', text: `All of them right → #${d.all_right_rank}` })));
    el.append(ul);
    // the five that move you most show; the rest are one tap away (decision 7)
    const extra = [...ul.children].slice(5, rows.length);
    if (extra.length > 1) {
      extra.forEach(li => { li.hidden = true; });
      const more = h('button', { type: 'button', class: 'quiet', text: `Show all ${rows.length}` });
      more.addEventListener('click', () => { extra.forEach(li => { li.hidden = false; }); more.remove(); });
      el.append(h('div', { class: 'debrief-act' }, more));
    }
    if ((d.by_norm || []).length) {
      const top = d.by_norm.slice(0, 3);
      el.append(h('p', { class: 'help', text: `Lost ${num(top.reduce((s, x) => s + x.pts, 0))}: ` + top.map(x => `${num(x.pts)} to ${x.label}${x.slots > 1 ? ` (${x.slots} slots)` : ''}`).join(' · ') }));
    }
    if (o.onRematch) {
      const n = lost.filter(r => !['pace', 'finish'].includes(r.kind)).length;
      if (n) {
        let whenV = 'later';
        const act = h('div', { class: 'debrief-act' });
        const go = h('button', { type: 'button', class: 'pill sm', text: `Rematch my misses · ${n}` });
        go.addEventListener('click', async () => { go.disabled = true; try { await o.onRematch(whenV); } finally { go.disabled = false; } });
        act.append(go);
        under(act, [{ value: 'later', label: 'In 2 days' }, { value: 'now', label: 'Now' }], { value: 'later', label: 'When', onChange: v => { whenV = v; } });
        el.append(act, h('p', { class: 'help', text: 'Same types, new numbers, the same traps. Coming back in 2 days fixes them for longer.' }));
      }
    }
    return { el };
  }

  /* ------------------------------------------------------------ UI.pacer (C8): the race rail */
  function pacer(host, p, you = {}) {
    const el = h('div', { class: 'pacer', role: 'status' });
    put(host, el);
    function set(pc, me = {}) {
      if (!pc) { el.hidden = true; return; }
      el.hidden = false;
      const total = pc.total || me.total || 10;
      const w = n => `${Math.min(100, Math.round((n || 0) / total * 100))}%`;
      el.replaceChildren(
        h('div', { class: 'pacer-tr', 'aria-hidden': 'true' }, h('i', { style: `width:${w(me.answered)}` })),
        h('div', { class: 'pacer-tr them', 'aria-hidden': 'true' }, h('i', { style: `width:${w(pc.at)}` })),
        h('span', { class: 'pacer-l', text: `You ${num(me.right || 0)} ✓ · ${num(me.points || 0)} · ${pc.label || 'Pacer'} ${num((pc.marks || []).filter(Boolean).length)} ✓ · ${num(pc.points_at || 0)} at this point` }));
    }
    set(p, you);
    return { el, set };
  }

  /* ------------------------------------------------------------ sheets: join, create, reminder */
  function join() {
    const field = h('input', { class: 'field', id: 'cx-code', maxlength: '6', autocomplete: 'off', autocapitalize: 'characters', spellcheck: 'false', inputmode: 'text', style: 'font-family: var(--mono); letter-spacing: .2em; text-transform: uppercase; max-width: 220px' });
    const msg = h('p', { class: 'cx-err', role: 'alert', hidden: true });
    const sheet = UI.sheet({
      title: 'Join with a code', size: 's',
      body: b => b.append(h('label', { class: 'label', for: 'cx-code', text: 'Contest code' }), field, h('p', { class: 'help', text: 'Six letters and digits, from the person who made the contest.' }), msg),
      actions: [{ label: 'Join', primary: true, onClick: () => { go(); return false; } }],
      focus: field,
    });
    field.addEventListener('input', () => { field.value = field.value.toUpperCase().replace(/[^A-Z0-9]/g, ''); msg.hidden = true; });
    field.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); go(); } });
    async function go() {
      const code = field.value.trim();
      if (code.length !== 6) { msg.hidden = false; msg.textContent = 'A code has six characters.'; return; }
      sheet.busy && sheet.busy(true);
      try {
        const r = await api('/join', { method: 'POST', body: { code } });
        location.href = href(r.id || r.contest || '', {});
      } catch (e) {
        msg.hidden = false;
        if (e.status === 404) msg.textContent = 'No contest has that code.';
        else if (e.status === 409 || e.status === 410) {
          msg.replaceChildren('That contest has ended. ', h('a', { class: 'link', href: `/compete/contest/?code=${encodeURIComponent(code)}`, text: 'Sit it unranked' }));
        } else msg.textContent = e.message || 'Couldn’t join. Try again.';
      } finally { sheet.busy && sheet.busy(false); }
    }
    return sheet;
  }

  function create(prefill = {}) {
    const f = { title: prefill.title || '', count: prefill.count || 10, source: 'skills', topics: new Set(prefill.topics || (UI.TOPICS || []).map(t => t.slug)),
      difficulty: 'all', format: 'both', clock: prefill.minutes ? 'custom' : 'auto', minutes: prefill.minutes || 16, open_for: 24, repeat: 'once', rounds: 7,
      twin: prefill.twin ?? false, reveal: 'each', strict: false };
    const form = h('div', { class: 'cx-form' });
    const sum = h('p', { class: 'cx-sum', role: 'status' });
    const err = h('p', { class: 'cx-err', role: 'alert', hidden: true });
    const row = (label, ...kids) => h('fieldset', {}, h('legend', { text: label }), ...kids);
    const title = h('input', { class: 'field', id: 'cx-title', maxlength: '40', value: f.title, placeholder: 'Your name’s challenge', autocomplete: 'off' });
    title.addEventListener('input', () => { f.title = title.value; });
    form.append(h('div', {}, h('label', { class: 'label', for: 'cx-title', text: 'Title' }), title, h('p', { class: 'help', text: '3–40 characters. Empty: “{your name}’s challenge”.' })));
    let srcCtl;
    const src = row('Questions from');
    srcCtl = under(src, [{ value: 'skills', label: 'Skills I pick' }, { value: 'my_traps', label: 'My open mistakes' }, { value: 'our_traps', label: 'Our open mistakes' }],
      { value: 'skills', onChange: v => { f.source = v; skillsBox.hidden = v !== 'skills'; srcHelp.textContent = SRC_HELP[v]; draw(); } });
    const SRC_HELP = { skills: '', my_traps: 'Your open mistakes’ question types, each with the same trap: beat me on the traps that catch me.', our_traps: 'From round 2: the mistakes most of you hold open. Nobody is told who holds which.' };
    const srcHelp = h('p', { class: 'help' });
    src.append(srcHelp);
    form.append(src);
    const cnt = row('Questions');
    under(cnt, [5, 10, 15, 22].map(n => ({ value: n, label: String(n) })), { value: f.count, onChange: v => { f.count = v; draw(); } });
    form.append(cnt);
    // the skill picker: 4 domains, select-all per domain
    const skillsBox = row('Skills');
    const grid = h('div', { class: 'cx-skills' });
    (UI.DOMAINS || []).forEach(([dname, dshort]) => {
      const topics = (UI.TOPICS || []).filter(t => t.domain === dname);
      const all = h('input', { type: 'checkbox' });
      const boxes = topics.map(t => { const c = h('input', { type: 'checkbox', value: t.slug }); c.checked = f.topics.has(t.slug); c.addEventListener('change', () => { c.checked ? f.topics.add(t.slug) : f.topics.delete(t.slug); syncAll(); draw(); }); return [c, t]; });
      const syncAll = () => { const on = boxes.filter(([c]) => c.checked).length; all.checked = on === boxes.length; all.indeterminate = on > 0 && on < boxes.length; };
      all.addEventListener('change', () => { boxes.forEach(([c, t]) => { c.checked = all.checked; all.checked ? f.topics.add(t.slug) : f.topics.delete(t.slug); }); draw(); });
      syncAll();
      grid.append(h('div', { class: 'dom' }, h('label', {}, all, dshort), boxes.map(([c, t]) => h('label', {}, c, t.short))));
    });
    skillsBox.append(grid);
    form.append(skillsBox);
    const diff = row('Difficulty');
    under(diff, [{ value: 'all', label: 'Easy → hard' }, { value: 'easy', label: 'Easy' }, { value: 'medium', label: 'Medium' }, { value: 'hard', label: 'Hard' }], { value: 'all', onChange: v => { f.difficulty = v; } });
    form.append(diff);
    const fmt = row('Format');
    under(fmt, [{ value: 'both', label: 'Both' }, { value: 'mcq', label: 'Multiple choice' }, { value: 'spr', label: 'Grid-in' }], { value: 'both', onChange: v => { f.format = v; } });
    form.append(fmt);
    const clock = row('Clock');
    const mins = h('input', { class: 'field', type: 'number', min: '5', max: '70', value: String(f.minutes), style: 'max-width: 120px', 'aria-label': 'Minutes', hidden: f.clock !== 'custom' });
    mins.addEventListener('input', () => { f.minutes = Math.max(5, Math.min(70, parseInt(mins.value, 10) || 16)); draw(); });
    under(clock, [{ value: 'auto', label: 'Auto (95 s a question)' }, { value: 'custom', label: 'Minutes' }], { value: f.clock, onChange: v => { f.clock = v; mins.hidden = v !== 'custom'; draw(); } });
    clock.append(mins);
    form.append(clock);
    const openFor = row('Open for');
    const openCtl = under(openFor, [{ value: 1, label: '1 hour' }, { value: 24, label: '24 hours' }, { value: 72, label: '3 days' }, { value: 168, label: '7 days' }], { value: 24, onChange: v => { f.open_for = v; draw(); } });
    form.append(openFor);
    const rep = row('Repeat');
    const rounds = h('input', { class: 'field', type: 'number', min: '2', max: '30', value: String(f.rounds), style: 'max-width: 120px', 'aria-label': 'Rounds', hidden: true });
    rounds.addEventListener('input', () => { f.rounds = Math.max(2, Math.min(30, parseInt(rounds.value, 10) || 2)); draw(); });
    under(rep, [{ value: 'once', label: 'Once' }, { value: 'day', label: 'Every day' }, { value: 'week', label: 'Every week' }], { value: 'once', onChange: v => {
      f.repeat = v; rounds.hidden = v === 'once';
      if (v !== 'once') { f.rounds = v === 'day' ? 7 : 4; rounds.value = String(f.rounds); }
      openFor.hidden = v !== 'once';
      srcCtl.disable('our_traps', v === 'once' ? 'Our open mistakes starts from round 2 of a series.' : '');
      if (v === 'once' && f.source === 'our_traps') srcCtl.set('skills');
      draw();
    } });
    rep.append(h('label', { class: 'label', text: 'Rounds', hidden: true }), rounds, h('p', { class: 'help', text: 'One code and link join every round.' }));
    form.append(rep);
    srcCtl.disable('our_traps', 'Our open mistakes starts from round 2 of a series.');
    const radios = (name, opts, v, set) => h('div', { class: 'cx-radio' }, opts.map(([val0, label]) => {
      const r = h('input', { type: 'radio', name, value: String(val0) }); r.checked = v === val0; r.addEventListener('change', () => set(val0));
      return h('label', {}, r, h('span', { text: label }));
    }));
    form.append(row('Questions for each student', radios('cx-twin', [[false, 'Same questions for everyone: good for going over them together'], [true, 'Everyone gets their own twin: same skills and difficulty, different numbers']], f.twin, v => { f.twin = v; })));
    form.append(row('Show answers', radios('cx-reveal', [['each', 'After each question'], ['end', 'At the end']], 'each', v => { f.reveal = v; })));
    const strictRow = row('Strict');
    if (UI.switch) UI.switch(strictRow, { checked: false, label: 'Strict', onChange: v => { f.strict = v; } });
    strictRow.append(h('p', { class: 'help', text: 'Leaving the tab or window, or copying the question and leaving, means a quick confirm on new numbers at the end.' }));
    form.append(strictRow);
    form.append(sum, err);
    function draw() {
      const secs = f.clock === 'auto' ? f.count * 95 : f.minutes * 60;
      const closes = new Date(Date.now() + (f.repeat === 'once' ? f.open_for : f.repeat === 'day' ? 24 : 168) * 3600e3);
      const whenS = closes.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
      const src0 = f.source === 'skills' ? '' : f.source === 'my_traps' ? ' · from your open mistakes' : ' · from your group’s open mistakes (round 2 on)';
      sum.textContent = `${f.count} questions · ${Math.round(secs / 60)} min${src0} · ${f.repeat === 'once' ? `open until ${whenS}` : `${f.rounds} rounds, ${f.repeat === 'day' ? 'daily' : 'weekly'}`}`;
    }
    draw();
    const sheet = UI.sheet({
      title: prefill.sheetTitle || 'Create a contest', size: 'l', body: b => b.append(form),
      actions: [{ label: 'Create', primary: true, onClick: () => { submit(); return false; } }],
    });
    async function submit() {
      err.hidden = true;
      const body = { count: f.count, source: f.source, twin: f.twin, reveal: f.reveal, strict: f.strict, format: f.format,
        difficulty: f.difficulty === 'all' ? ['easy', 'medium', 'hard'] : [f.difficulty] };
      if (f.title.trim()) body.title = f.title.trim();
      if (f.source === 'skills') {
        if (!f.topics.size) { err.hidden = false; err.textContent = 'Pick at least one skill.'; return; }
        body.topics = [...f.topics];
      }
      if (f.clock === 'custom') body.minutes = f.minutes;
      if (f.repeat === 'once') body.open_for = f.open_for;
      else body.repeat = { every: f.repeat, rounds: f.rounds };
      sheet.busy && sheet.busy(true);
      try {
        const r = await api('/contests', { method: 'POST', body });
        try { const m = JSON.parse(localStorage.getItem('satf.contest.codes') || '{}'); m[r.id] = r.code; localStorage.setItem('satf.contest.codes', JSON.stringify(m)); } catch (_) {}
        done(r);
      } catch (e) {
        err.hidden = false;
        err.textContent = typeof e.detail === 'string' ? e.detail.replace(/^./, c => c.toUpperCase()) : (e.message || 'Couldn’t create it. Try again.');
      } finally { sheet.busy && sheet.busy(false); }
    }
    function done(r) {
      const link = `${location.origin}${r.link || `/compete/contest/?code=${r.code}`}`;
      const copyCode = h('button', { type: 'button', class: 'btn', text: 'Copy code' });
      const copyLink = h('button', { type: 'button', class: 'btn', text: 'Copy link' });
      copyCode.addEventListener('click', () => UI.copyText(r.code));
      copyLink.addEventListener('click', () => UI.copyText(link));
      const body = sheet.body || sheet.el.querySelector('.sheet-body');
      body.replaceChildren(h('div', { class: 'cx-form' },
        h('p', { class: 'k', text: r.rounds > 1 ? `Code for all ${r.rounds} rounds` : 'Code' }),
        h('p', { class: 'cx-code', text: r.code }),
        h('p', { class: 'meta', text: link }),
        h('div', { class: 'debrief-act' }, copyCode, copyLink, h('a', { class: 'pill sm', href: href(r.id), text: 'Open contest' }))));
      if (sheet.foot) sheet.foot.replaceChildren();
    }
    return sheet;
  }

  function reminder() {
    const t = h('input', { class: 'field', type: 'time', id: 'cx-rem', value: '17:00', style: 'max-width: 160px' });
    return UI.sheet({
      title: 'Daily reminder', size: 's',
      body: b => b.append(h('label', { class: 'label', for: 'cx-rem', text: 'Time' }), t, h('p', { class: 'help', text: 'A calendar event that repeats every day and links to the Daily Challenge.' })),
      actions: [{ label: 'Add to calendar', primary: true, onClick: () => {
        const today = new Date(); const day = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        UI.ics({ title: 'SAT Freshman · Daily Challenge', start: day, time: t.value || '17:00', minutes: 20, repeat: 'daily', url: `${location.origin}/compete/contest/?id=daily`, filename: 'daily-challenge.ics' });
        toast('Reminder downloaded');
      } }],
    });
  }

  Object.assign(UI, {
    level, board, podium, debrief, pacer,
    compete: { KINDS, kind, title, icon, svg: svgOf, SVG, href, runner, start, rulesSeen, markRules, windowLine, clockText, facts, marks,
      copyResult, under, subnav, join, create, reminder, ladder, parLine, fieldLine, pct, LADDER, levelOf, rangeOf, levelIn, step, left, when, dayLabel, titleText, topicName, TIER, num, mmss },
  });
})();
