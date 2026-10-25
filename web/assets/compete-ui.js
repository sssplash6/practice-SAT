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
       -> {el, update(data[, opts]), append(data), jump(), highlight(pid)}   update glides moved rows; a poll says "Up N" once
       data: {players, entries [{pid, rank, tie, name, anon, level, ring, title, you, mark,
       n, ...metric}], you, next_offset, marks}. Ties read "=4"; par rows (dashed, a flag,
       no rank) sit at their points and never count (C6); your row is wash + amber edge;
       J K / arrows move rows, Enter opens the row menu, F follows, Esc leaves (C24).
   UI.podium(host, entries, {value(e), sub(e), pars, rise}) -> {el}      2 · 1 · 3; rise: the pedestals rise 3, 2, 1 (a change, never on load)
   UI.debrief(host, data, {onFilter(qids, label), onFix(row), onRematch(when), sid, reached, label(norm)}) -> {el}
       reached: the Set of slots a run served (the rest read "Not reached"); label: a trap's words
       "Where your points went" (C1): the points bar, the headline, one row per lost item
   UI.pacer(host, pacer, you) -> {el, set(pacer, you)}             the race rail (C8)
   UI.compete  KINDS, kind(c), icon(kind), href(cid, q), runner(res), start(cid, o),
       rulesSeen(kind), markRules(kind), windowLine(c), clockText(c), facts(c), marks(result),
       copyResult(c, result, place, pid), copy(button, text), info(text, label), under(host, options, o), subnav(page),
       join(), create(prefill), reminder(), LADDER, levelOf(r), levelIn(r, provisional),
       step(gap, metric, pace), left(iso), when(iso), dayLabel(day), periodText(kind, period), trapWords(items) -> Map,
       trapLabel(norm, words): "Stopped at 2b rather than dividing by 2", never the raw "#" key
       moved(n, cap): a rank's move in words, "up 3" / "Down 2" (no ▲▼ glyphs)
       badgeIcon(achievement, earned, {size: 'sm'}) -> span.bcirc: the one badge art, Profile's and Compete's
   UI.board columns: {label, value(e), phone, par, num, unit, meta, title, head() -> Node, sorted}
       head: a header button (ui.css's sortable th); sorted marks the ordering column (aria-sort)
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
  const num = n => (n === null || n === undefined || n === '' || isNaN(n) ? '–' : Number(n).toLocaleString('en-US', { maximumFractionDigits: 1 }));
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
.lvl b { position: relative; font: 600 calc(var(--s) * .46)/1 var(--font); color: var(--ink); font-variant-numeric: tabular-nums; }
.lvl.top { background: var(--amber); border-radius: 28%; }
.lvl.top b { color: var(--ink-deep); font-size: calc(var(--s) * .4); }
.lvl.ring { box-shadow: 0 0 0 1.5px var(--paper), 0 0 0 3.5px var(--amber); }
.board { position: relative; min-width: 0; }
.board-t { table-layout: auto; }
.board-t :is(th, td) { padding-left: 8px; padding-right: 8px; }
.board-t td { padding-top: 8px; padding-bottom: 8px; }
.board-t td.rk, .board-t th.rk { width: 1%; white-space: nowrap; font: 500 13px var(--font); font-variant-numeric: tabular-nums; padding-right: 6px; }
.board-t td.who { width: 100%; max-width: 0; }
.board-t :is(th, td).n { white-space: nowrap; font-variant-numeric: tabular-nums; }
.board-t .who-l { display: flex; align-items: center; gap: 8px; min-width: 0; }
.board-t .who-n { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }
.board-t .who-t, .board-t .who-m { display: block; margin-top: 2px; font: 500 12.5px var(--font); font-variant-numeric: tabular-nums; color: var(--soft); }
.board-t .who-m { display: none; }
.board-t .mk { display: inline-flex; align-items: center; color: var(--soft); font: 500 11.5px var(--font); font-variant-numeric: tabular-nums; }
.board-t .mk svg { width: 14px; height: 14px; }
.board-t .rowmenu { margin-left: auto; flex: none; width: 32px; height: 32px; border: 0; border-radius: 8px; background: none; color: var(--soft); cursor: pointer; }
.board-t tr { scroll-margin-top: calc(var(--bar, 64px) + 72px); scroll-margin-bottom: 24px; }
/* the row menu shows on hover or focus where there is a mouse, always on touch */
@media (hover: hover) and (pointer: fine) {
  .board-t .rowmenu { opacity: 0; transition: opacity .12s; }
  .board-t tr:hover .rowmenu, .board-t tr:focus-within .rowmenu, .board-t .rowmenu[aria-expanded="true"] { opacity: 1; }
  .board-t .rowmenu:hover { background: var(--well); color: var(--ink); }
}
.board-t tr:focus-visible { outline-offset: -2px; }
/* yours (ui.css .table tr.you): the same height as every row, a wash, 600, the .rank cell amber-deep; no tag, no mark */
.board-t tr.par > * { color: var(--soft); background: none; }
.board-t tr.par > td { border-top: 1px dashed var(--faint); border-bottom: 1px dashed var(--faint); }
.board-t tr.par svg { width: 14px; height: 14px; color: var(--soft); vertical-align: -2px; }
.board-t tr.sep > td { padding: 4px 8px; font: 500 12.5px var(--font); color: var(--soft); background: none; }
.board-t tr.hl > * { background: var(--wash-2, var(--wash)); }
.board-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin-top: 14px; }
.board-empty { margin: 14px 0 0; color: var(--soft); }
/* the You strip: in the flow above the table; sticky only while your own row is out of view, under the
   section bar when that sticks (desktop: 52px from the top; phone: the 56px top bar and the 44px section bar) */
.youbar { z-index: 5; display: flex; flex-wrap: wrap; align-items: center; gap: 6px 24px; margin-bottom: 12px; padding: 10px 14px; border-radius: 10px; background: var(--wash); font: 500 14px var(--font); font-variant-numeric: tabular-nums; color: var(--ink); }
.youbar.stuck { position: sticky; top: 60px; background: color-mix(in srgb, var(--amber) 10%, var(--raised, var(--paper))); box-shadow: var(--shadow-2, 0 1px 0 var(--line)); }
.youbar > span { flex: 1 1 240px; min-width: 0; }
.board-t .up-n { flex: none; }
.youbar[hidden], .debrief-rows li[hidden] { display: none; }
@media (max-width: 759px) {
  .youbar.stuck { top: calc(108px + env(safe-area-inset-top, 0px)); }
  .board-t .who-m { display: block; }
  .board-t :is(th, td).off-phone { display: none; }
}
.podium { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); align-items: end; gap: 12px; }
/* stepped pedestals on the page (the leaderboard's hero): raised, #1 the tallest and one shadow step higher */
.pod { display: grid; align-content: end; justify-items: center; gap: 4px; min-width: 0; padding: 12px 8px 14px; border-radius: 12px; background: var(--raised, var(--paper)); box-shadow: var(--shadow-1, inset 0 0 0 1px var(--line)); text-align: center; }
.pod.p1 { min-height: 136px; box-shadow: var(--shadow-2, inset 0 0 0 1px var(--line)); } .pod.p2 { min-height: 112px; } .pod.p3 { min-height: 96px; }
.pod.you { background: var(--wash); }
.pod.you .num { color: var(--amber-deep); }
.pod.open, .pod.parp { background: none; box-shadow: inset 0 0 0 1px var(--line); color: var(--soft); }   /* an open place: a hairline on the page, no dashes */
.pod .num { font-size: 22px; }
.pod.p1 .num { font-size: 28px; }
.pod .pod-r { display: inline-flex; align-items: center; gap: 4px; }
.pod .pod-who { display: inline-flex; align-items: center; gap: 6px; max-width: 100%; min-width: 0; }
.pod .pod-n { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }
.pod .pod-v { font: 600 14px var(--font); font-variant-numeric: tabular-nums; } .pod .pod-s { font: 500 12.5px var(--font); font-variant-numeric: tabular-nums; color: var(--soft); }
.pod svg.tro { width: 16px; height: 16px; color: var(--ink); }
.debrief { display: grid; gap: 14px; }
.debrief-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; }
.debrief-line { font: 600 14.5px/1.4 var(--font); }
.debrief-rows { display: grid; gap: 0; margin: 0; padding: 0; list-style: none; }
.debrief-rows li { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 4px 14px; padding: 10px 0; border-top: 1px solid var(--line); }
.debrief-rows .dr-t { font: 500 14px/1.4 var(--font); }
.debrief-rows .dr-m { display: block; margin-top: 2px; font: 500 12.5px var(--font); font-variant-numeric: tabular-nums; color: var(--soft); }
.debrief-rows .badge { margin-left: 6px; }
.debrief-act { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 28px; }
.debrief .sb-l { display: none; }   /* each part is named once, in the legend */
.debrief .sb-bar { height: 12px; }   /* a slim bar, like every meter; the legend under it names the parts */
.ladder-row { display: flex; align-items: center; gap: 10px; }
.ladder-row > .ladder { flex: 1 1 auto; min-width: 0; max-width: calc(var(--cols, 10) * 76px); }
.pacer { display: grid; gap: 4px; }
.pacer-tr { position: relative; height: 6px; border-radius: 3px; background: var(--track); }
.pacer-tr > i { position: absolute; inset: 0 auto 0 0; border-radius: inherit; background: var(--amber); }
.pacer-tr.them > i { background: var(--ink); }
.pacer-l { font: 500 12.5px var(--font); font-variant-numeric: tabular-nums; color: var(--soft); text-align: right; }
/* the Compete tabs sit on the title's row (.cx-head); on a phone they wrap under it, first label flush */
.subnav { display: flex; flex-wrap: wrap; gap: 0 4px; margin: 0; }
@media (max-width: 759px) { .subnav { flex: 1 0 100%; margin-left: -9px; } }
.subnav a { position: relative; display: inline-flex; align-items: center; height: 36px; padding: 0 9px; font: 500 14px var(--font); color: var(--soft); text-decoration: none; }
.subnav a[aria-current="page"] { color: var(--ink); font-weight: 600; }
.subnav a[aria-current="page"]::after { content: ""; position: absolute; left: 9px; right: 9px; bottom: 4px; height: 2px; border-radius: 2px; background: var(--amber); }
@media (hover: hover) and (pointer: fine) { .subnav a:hover { color: var(--ink); } }
.cx-form { display: grid; gap: 18px; }
.cx-form fieldset { margin: 0; padding: 0; border: 0; min-width: 0; }
.cx-form legend { padding: 0; margin-bottom: 6px; font: 600 14px/1.3 var(--font); }
.cx-skills { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 18px; }
.cx-skills .dom { display: grid; gap: 4px; align-content: start; }
.cx-skills label { display: flex; align-items: center; gap: 8px; min-height: 30px; font: 500 14px var(--font); }
.cx-skills .dom > label:first-child { font-weight: 600; }
.cx-radio { display: grid; gap: 4px; }   /* rows of label.choice-row: the radio inside, the row shows it picked */
.cx-sum { font: 500 12.5px var(--font); font-variant-numeric: tabular-nums; color: var(--soft); }
.cx-code { font: 500 28px/1.1 var(--mono); letter-spacing: .12em; }
.cx-err { color: var(--ink); font-weight: 600; }
.cx-code-in { font-family: var(--mono); letter-spacing: .2em; text-transform: uppercase; max-width: 220px; }   /* a code input keeps its caps */
.cx-num { max-width: 120px; } .cx-time { max-width: 160px; }
@media (max-width: 759px) { .cx-skills { grid-template-columns: minmax(0, 1fr); } }
/* one badge style for Profile and Compete (UI.compete.badgeIcon): a 44px disc, the drawing dead centre; earned is a warm
   wash with an amber-deep drawing and a fine amber edge (a solid amber disc per badge made the shelf shout) */
.bcirc { width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; flex: none; background: var(--well); color: var(--soft); }
.bcirc > * { display: grid; place-items: center; width: 24px; height: 24px; line-height: 0; }
.bcirc svg, .bcirc .glyph { width: 22px; height: 22px; display: block; margin: 0; }
.bcirc.on { background: var(--wash-2, var(--wash)); color: var(--amber-deep); box-shadow: inset 0 0 0 1px rgb(from var(--amber) r g b / .45), 0 1px 2px rgb(140 70 0 / .12); }
/* the spot-check sits where the runner was (any host layout): its own width, the page's column */
.spot { box-sizing: border-box; display: grid; gap: 14px; align-content: start; align-self: start; justify-self: center; width: min(760px, calc(100vw - 32px)); height: auto; margin: 24px auto; }
.bcirc.sm { width: 32px; height: 32px; } .bcirc.sm > * { width: 18px; height: 18px; } .bcirc.sm svg, .bcirc.sm .glyph { width: 16px; height: 16px; }
`;
  if (!doc.getElementById('compete-ui-css')) doc.head.append(h('style', { id: 'compete-ui-css', text: CSS }));

  /* ------------------------------------------------------------ icons */
  // the shared map (ui.js UI.ICON, Phosphor); UI.compete.SVG keeps its old names for callers (dots is more)
  const I = UI.ICON || {};
  const SVG = { flag: I.flag, sheet: I.sheet, trap: I.trap, strikes: I.strikes, star: I.star, clean: I.clean, dots: I.more };
  const svgOf = (inner, size = 18, cls = '') => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"${cls ? ` class="${cls}"` : ''}>${inner || ''}</svg>`;
  // Rush ends after three misses: three rings, its three chances (the shared "strikes" read as a typed "xxx" at 20px)
  const OWN = { chances: '<g class="ph" fill="none" stroke="currentColor" stroke-width="16" transform="scale(.09375)"><circle cx="44" cy="128" r="26"/><circle cx="128" cy="128" r="26"/><circle cx="212" cy="128" r="26"/></g>' };
  function icon(kind, size = 20) {
    const k = KINDS[kind] || KINDS.daily;
    return h('span', { class: 'kind-ic', 'aria-hidden': 'true', html: svgOf(OWN[k.icon] || I[k.icon] || I.flag, size) });
  }
  // a rank's move in words ("up 3", "down 2"; Up/Down to start a cell): the ▲▼ triangles came from the device's font
  const moved = (n, cap) => (!n ? null : `${n > 0 ? (cap ? 'Up' : 'up') : (cap ? 'Down' : 'down')} ${Math.abs(n)}`);

  /* ------------------------------------------------------------ the contest model on screen */
  const KINDS = {
    daily: { label: 'Daily Challenge', icon: 'trophy', clock: 'answer', pace: true, twins: true },
    sprint: { label: 'Sprint', icon: 'bolt', clock: 'answer', runs: true },
    weekly: { label: 'Weekly Module', icon: 'sheet', clock: 'wall', twins: true },
    final: { label: 'Season Final', icon: 'flag', clock: 'wall', twins: true },
    private: { label: 'Private contest', icon: 'users', clock: 'answer', pace: true },
    trap: { label: 'Trap of the week', icon: 'trap', clock: 'answer', pace: true, twins: true },
    rush: { label: 'Rush', icon: 'chances', clock: 'none', runs: true },
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
  // a timestamp's day where the learner is (the server's are UTC: 01:00 in Tashkent is the day before in UTC);
  // a plain YYYY-MM-DD (a Daily's id, a period) is already a day and stays as it is
  const pad2 = n => String(n).padStart(2, '0');
  const localDay = iso => { const s = String(iso || ''), d = new Date(s); return !s.includes('T') || isNaN(d) ? s.slice(0, 10) : `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`; };
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
    if (c.kind === 'rush') return 'ends after 3 misses';
    if (k.clock === 'wall') return `${Math.round((c.seconds || 2100) / 60)} min${c.kind === 'final' ? ' · 2 modules' : ''}`;
    return c.seconds ? `${mmss(c.seconds)} to answer` : 'answer time';
  }
  // what each entrant gets: a twin with its own numbers, or (R&W, written items) their own item of the same skill and tier
  const ownWords = c => (c.subject === 'rw' ? 'a different passage for everyone' : 'different numbers for everyone');
  function facts(c) {
    const out = [];
    if (c.kind === 'sprint') out.push('as many as you answer');
    else if (c.kind === 'rush') out.push('difficulty climbs with you');
    else if (c.count) out.push(`${c.count} questions`);
    out.push(clockText(c));
    if (kind(c).twins || (c.kind === 'private' && c.spec && c.spec.twin)) out.push(ownWords(c));
    const n = c.field && c.field.players;
    if (n) out.push(`${num(n)} entered`);
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
    // daily-YYYY-MM-DD, R&W's with -rw after the date
    const day = c.kind === 'daily' ? ` · ${dayLabel(String(c.id).slice(6, 16), { weekday: false })}` : '';
    const clock = r && r.secs !== undefined ? ` · ${mmss(r.secs)}` : '';
    const rank = place.rank ? ` · #${place.rank} of ${num(place.players)}` : '';
    const url = `${location.origin}${href(c.id, pid ? { race: pid } : {})}`;
    return [`SAT Freshman · ${k.label}${c.subject === 'rw' ? ' · R&W' : ''}${day}`,
      `${num(r.right)}/${num(r.asked || c.count)} · ${num(r.points)} pts${clock}${rank}`,
      marks(r).map(m => glyphOf(m.status)).join(''),
      pid ? `Beat ${num(r.points)}: ${url}` : url].join('\n');
  }

  /* ------------------------------------------------------------ the ladder, par and field lines (C5, C7) */
  const pct = x => (x === null || x === undefined ? '–' : `${Math.round(x * 100)}%`);
  function ladder(host, c) {
    const n = (c.ladder || []).length;
    const cells = h('div', { class: 'ladder', role: 'list', style: n !== 10 && n ? `--cols:${Math.min(11, n)}` : null, 'aria-label': 'The questions: skill, difficulty and your chance' });
    (c.ladder || []).forEach(q => {
      const name = topicName(q.topic);
      const label = [`Q${q.slot}`, name, TIER[q.tier] || q.tier, q.format === 'spr' ? 'grid-in' : null,
        q.chance !== undefined && q.chance !== null ? `your chance ${pct(q.chance)}` : null].filter(Boolean).join(' · ');
      // a well per slot: the skill and its difficulty; Q3 is in the label and the tip, your chance fills the well's floor
      const cell = h('div', { class: 'lad', role: 'listitem', tabindex: '0', 'aria-label': label },
        UI.glyph ? UI.glyph(q.topic) : null,
        UI.dbars ? UI.dbars(q.tier, { bare: true }) : null,
        q.chance !== undefined && q.chance !== null ? h('span', { class: 'ch', 'aria-hidden': 'true' }, h('i', { style: `width:${Math.round(q.chance * 100)}%` })) : null);
      tip(cell, label);
      cells.append(cell);
    });
    // no grid-in note: each tile names itself (skill, difficulty, grid-in, your chance) on hover or focus
    put(host, h('div', { class: 'ladder-row' }, cells));
    return cells;
  }
  function parLine(c) {
    const p = c.me && c.me.par, f = c.me && c.me.forecast;
    if (!p || p.base === undefined || p.base === null) return null;
    const el = h('p', { class: 'line' }, `Your par ${num(p.points ?? p.base)} · about ${num(p.right)} right`,
      f ? ` · likely #${f.lo}–#${f.hi} of ~${num(f.of)}` : '');
    tip(el, 'What a student at your rating scores on these questions, on average, with pace and finish bonuses.');
    return el;
  }
  function fieldLine(c, verb = 'finished') {
    const f = c.field || {};
    if (!f.players) return null;
    return h('p', { class: 'meta', text: [`${num(f.players)} ${verb}`, f.sitting_now ? `${num(f.sitting_now)} sitting now` : null,
      f.median_points !== null && f.median_points !== undefined ? `median ${num(f.median_points)} pts` : null,
      f.best !== null && f.best !== undefined ? `best ${num(f.best)}` : null].filter(Boolean).join(' · ') });
  }

  // the challenge streak a make-up of `day` keeps: the run of sat or made-up days just before it
  const SAT = new Set(['sat', 'made_up', 'made up']);
  function streakBefore(strip, day) {
    const list = [...(strip || [])].sort((a, b) => (a.day < b.day ? -1 : 1));
    let i = list.findIndex(x => x.day === day), n = 0;
    if (i < 0) return 0;
    while (--i >= 0 && SAT.has(list[i].state)) n += 1;
    return n;
  }
  const DAY_WORD = { sat: 'sat', made_up: 'made up', 'made up': 'made up', ghost: 'sat late, unranked', missed: 'missed' };

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
  // a champion's title as students read it: the server sends raw ids ("road-2026-10-03", "2026-W39", board "band")
  const periodText = (kind, p) => { p = p || ''; const road = /^road-(\d{4}-\d{2}-\d{2})$/.exec(p), wk = /^\d{4}-W(\d{2})$/.exec(p);
    return road ? `Road to ${dayLabel(road[1], { weekday: false })}` : wk ? `Week ${+wk[1]}` : kind === 'final' && /^\d{4}-\d{2}-\d{2}$/.test(p) ? `Final ${dayLabel(p, { weekday: false })}` : p; };
  // R&W's podiums are its boards with an rw: prefix (rw:points)
  const BOARD_NAMES = { points: 'Points', net: 'Over expected', change: 'Most improved', band: 'Level band' };
  const boardName = b => { const rw = /^rw:/.test(b || ''), k = String(b || '').replace(/^rw:/, ''); return `${rw ? 'R&W ' : ''}${BOARD_NAMES[k] || k}`; };
  const titleText = t => t ? `Champion · ${t.period_label || periodText(t.kind, t.period)}${t.board ? ` · ${boardName(t.board)}` : ''}${t.place ? ` #${t.place}` : ''}` : '';

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
  let boardSeq = 0;
  const boardKeys = [];
  function board(host, data, o = {}) {
    const el = h('div', { class: 'board' });
    const wrap = h('div', { class: 'table-wrap' });
    const table = h('table', { class: 'table board-t hover', role: 'grid', 'aria-label': o.label || 'Board' });
    const thead = h('thead'), tbody = h('tbody');
    const empty = h('p', { class: 'board-empty', hidden: true });
    const foot = h('div', { class: 'board-foot' });
    const bar = h('div', { class: 'youbar', hidden: true, role: 'status' });
    table.append(thead, tbody);
    wrap.append(table);
    if (o.youBar !== false) el.append(bar);
    el.append(wrap, empty, foot);
    put(host, el);
    const val = o.value || (e => e.points ?? e.value);
    let d = data || {}, list = [], youRow = null, obs = null;
    const cols = () => (o.columns || []).filter(c => list.some(e => !e.sep && (!e.par || c.par) && c.value(e) !== null && c.value(e) !== undefined && c.value(e) !== ''));

    // only the exception is marked: a clean run is the default and shows nothing (decision 7)
    function markEl(e) {
      if (e.mark === 'confirmed') return tip(h('span', { class: 'mk', text: `✓${e.n || ''}` }), `Left or copied, then kept ${e.n || 'every'} answer${e.n === 1 ? '' : 's'} by the spot-check`);
      if (e.mark === 'voided') return tip(h('span', { class: 'mk', text: `⊘${e.n || ''}` }), `${e.n} answer${e.n === 1 ? '' : 's'} not counted: left or copied, and not kept by the spot-check`);
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
      const rank = e.par ? h('td', { class: 'rk', html: FLAG, title: 'Par: never ranked' }) : h('td', { class: 'rk rank', text: `${e.tie ? '=' : ''}${e.rank ?? ''}` });
      const off = cs.filter(c => !c.phone && c.meta !== false).map(c => { const v = c.value(e); return v === null || v === undefined || v === '' ? null : c.unit ? `${v} ${c.unit}` : `${v}`; }).filter(Boolean);
      const who = h('td', { class: 'who' },
        h('span', { class: 'who-l' },
          e.par ? null : level(null, false, 20, { level: e.level, ring: e.ring, ringTitle: titleText(e.title) }),
          h('span', { class: 'who-n', text: e.par ? e.label : e.you ? `${e.name} (you)` : e.name }),
          e.you ? null : markEl(e), menuBtn(e)),
        e.title && !e.par ? h('span', { class: 'who-t', text: titleText(e.title) }) : null,
        off.length ? h('span', { class: 'who-m', text: off.join(' · ') }) : null);
      tr.append(rank, who, ...cs.map(c => { const v = e.par && !c.par ? '' : c.value(e); return h('td', { class: (c.num !== false ? 'n' : '') + (c.phone ? '' : ' off-phone'), text: v === null || v === undefined ? '–' : String(v) }); }));
      return tr;
    }
    function withPars(entries) {
      const pars = o.pars ? (o.pars() || []) : [];
      if (!pars.length) return entries;
      const out = [...entries];
      // highest par first, each placed above the first row (player or par) below it
      [...pars].sort((x, y) => y.value - x.value).forEach(p => {
        const at = out.findIndex(e => !e.sep && (e.par ? e.value : val(e) ?? -Infinity) < p.value);
        const row0 = { par: true, label: p.label, value: p.value, points: p.value };
        if (at < 0) out.push(row0); else out.splice(at, 0, row0);
      });
      return out;
    }
    // g: {glide, was} from update(): rows that moved slide to their place (UI.glide, keyed by player), and a rise
    // since the last poll (was: your old rank) says "Up N" on your row, once
    function draw(g = {}) {
      list = withPars((d.entries || []).slice());
      const cs = cols();
      thead.replaceChildren(h('tr', {}, h('th', { scope: 'col', class: 'rk', text: 'Rank' }), h('th', { scope: 'col', text: 'Student' }),
        cs.map(c => { const th = h('th', { scope: 'col', class: (c.num !== false ? 'n' : '') + (c.phone ? '' : ' off-phone'), 'aria-sort': c.sorted ? 'descending' : null }, c.head ? c.head() : c.label); if (c.title && !c.head) tip(th, c.title); return th; })));
      const fill = () => tbody.replaceChildren(...list.map(e => row(e, cs)));
      if (g.glide && UI.glide && tbody.rows.length) UI.glide(tbody, fill, { key: k => (k.dataset && k.dataset.pid) || k, enter: false }); else fill();
      const rows = [...tbody.rows].filter(r => r._e);
      rows.forEach((r, i) => { r.tabIndex = i === 0 ? 0 : -1; });
      const real = (d.entries || []).length;
      empty.hidden = real > 0;
      empty.textContent = real ? '' : (o.empty || 'No one has finished yet.');
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
      const now = youRow && youRow._e.rank;
      if (g.was && now && now < g.was) {
        const up = h('span', { class: 'badge soft up-n', text: `Up ${g.was - now}` });
        youRow.querySelector('.who-l').append(up);
        if (UI.fx) UI.fx.pop(up);
      }
      drawBar();
    }
    // at rest the strip sits in the flow above the table and covers nothing; it sticks under the
    // top bar only while your own row is out of view
    function drawBar() {
      if (obs) { obs.disconnect(); obs = null; }
      bar.classList.remove('stuck');
      const you = d.you;
      if (!you || o.youBar === false) { bar.hidden = true; return; }
      const text = o.youText ? o.youText(you) : `You · #${you.rank} · ${num(val(you))}`;
      if (!text) { bar.hidden = true; return; }
      const jump = h('button', { type: 'button', class: 'quiet', text: 'Jump to me' });
      jump.addEventListener('click', () => api0.jump());
      bar.replaceChildren(h('span', { text }), ...(youRow || o.onJump ? [jump] : []));
      bar.hidden = false;
      if (youRow && 'IntersectionObserver' in window) {
        obs = new IntersectionObserver(es => {
          const stuck = !es.some(x => x.isIntersecting), was = bar.classList.contains('stuck');
          bar.classList.toggle('stuck', stuck);
          if (stuck && !was && UI.motion) UI.motion.enter(bar, 'nudge');   // it slides in as it sticks
        }, { rootMargin: '-110px 0px 0px 0px' });
        obs.observe(youRow);
      }
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
    // the ? sheet lists the board region's keys (§2.8, C24); the table's own handler above acts first
    if (UI.keys && UI.keys.register) {
      // one Board heading in the ? sheet: drop the keys of boards no longer on the page
      boardKeys.splice(0).forEach(([t, r]) => { if (t.isConnected && t !== table) boardKeys.push([t, r]); else r.unregister(); });
      const shown = () => false;
      const reg = UI.keys.register(`compete-board-${++boardSeq}`, {
        J: { does: 'Next row', run: shown }, K: { does: 'Previous row', run: shown },
        ArrowDown: { does: 'Next row', run: shown }, ArrowUp: { does: 'Previous row', run: shown },
        Enter: { does: 'Row menu', run: shown },
        ...(o.onFollow ? { F: { does: 'Follow the student', run: shown } } : {}),
        Escape: { does: 'Leave the board', run: shown },
      }, { label: 'Board', within: table, when: () => table.isConnected });
      boardKeys.push([table, reg]);
    }
    const api0 = {
      el,
      // update(data) after a poll (rows glide, "Up N" once); update(data, opts) after a control change (new columns or
      // label: rows glide, no "Up N", since a different board is no move)
      update(nd, opts) {
        const was = opts ? null : (d.you && d.you.rank) || null;
        d = nd || {};
        if (opts) { Object.assign(o, opts); table.setAttribute('aria-label', o.label || 'Board'); }
        draw({ glide: true, was });
      },
      append(more) { d = { ...d, ...more, entries: [...(d.entries || []), ...((more && more.entries) || [])] }; draw(); },
      jump() {
        if (youRow) {
          youRow.scrollIntoView({ block: 'center', behavior: UI.reduced && UI.reduced() ? 'auto' : 'smooth' }); youRow.tabIndex = 0; youRow.focus({ preventScroll: true });
          if (UI.fx) [...youRow.cells].forEach(c => UI.fx.glow(c, { remove: false }));   // the row's wash flares and fades back
        }
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
        card.append(
          h('span', { class: 'pod-r' }, i === 0 && TROPHY ? h('span', { html: TROPHY }) : null, h('span', { class: 'num', text: `${e.tie ? '=' : ''}${e.rank}` })),
          h('span', { class: 'pod-who' }, level(null, false, 20, { level: e.level, ring: e.ring, ringTitle: titleText(e.title) }),
            h('span', { class: 'pod-n', text: e.you ? `${e.name} (you)` : e.name })),
          h('span', { class: 'pod-v', text: value(e) }),
          ...(o.sub && o.sub(e) ? [h('span', { class: 'pod-s', text: o.sub(e) })] : []));
      } else if (p) card.append(h('span', { html: FLAG }), h('span', { class: 'pod-n', text: p.label }), h('span', { class: 'pod-v', text: num(p.value) }));
      else card.append(h('span', { class: 'num', text: String(i + 1) }), h('span', { class: 'pod-s', text: 'Open' }));
      el.append(card);
    });
    put(host, el);
    if (o.rise && UI.motion) [[2, 0], [0, 60], [1, 120]].forEach(([i, delay]) => UI.motion.enter(el.children[i], 'rise', { delay }));
    return { el };
  }

  /* ------------------------------------------------------------ UI.debrief (C1) */
  const CAUSE = { trap: 'Traps', slip: 'Slips', clock: 'Clock', entry: 'Entry', gap: 'Gaps', skip: 'Skipped', void: 'Voided', pace: 'Over budget', finish: 'Finish bonus', reach: 'Not reached' };
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const topicName = t => (UI.topicName ? UI.topicName(t) : String(t || '').replace(/_/g, ' '));   // Math and R&W skills
  // a trap's name as the student reads it: the server folds numbers into # (progress.norm); the
  // student's own choices still carry the numbers, so a matching reason gives the wording back
  const normOf = r => String(r || '').toLowerCase().replace(/[-−]?\d[\d.,/]*/g, '#').split(/\s+/).filter(Boolean).join(' ');
  const cap = t => t.charAt(0).toUpperCase() + t.slice(1);
  function trapWords(items) {
    const m = new Map();
    (items || []).forEach(it => {
      const q = (it && it.question) || it || {};
      [...(q.reasons || []), ...(q.spr_reasons || []).map(x => (Array.isArray(x) ? x[0] : x))].forEach(r => { if (r && typeof r === 'string' && !m.has(normOf(r))) m.set(normOf(r), r); });
    });
    return m;
  }
  const OTHER = new Set(['other mistake', 'other', 'wrong']);
  function trapLabel(norm, words) {
    const n = String(norm || '');
    if (!n || OTHER.has(n)) return 'Other slips';
    const raw = words && words.get(n);
    return cap(raw || n.replace(/#/g, '…'));
  }
  function debrief(host, d, o = {}) {
    const el = h('section', { class: 'debrief', 'aria-label': 'Where your points went' });
    put(host, el);
    if (!d || d.max === undefined) return { el };
    // a run's slots past the last one served were never reached: not a skip, not a miss to rematch
    const lost = (d.lost || []).map(r => (o.reached && r.kind === 'skip' && !o.reached.has(r.slot) ? { ...r, kind: 'reach', places: 0 } : r));
    const label = r => (o.label ? o.label(r.norm) : r.label);
    const miss = d.max - d.points;
    const ranked = (d.players || 0) >= 2;
    el.append(h('div', { class: 'debrief-head' }, h('h2', { class: 'h2', text: 'Where your points went' }),
      h('span', { class: 'meta', text: miss > 0 ? `−${num(miss)} of ${num(d.max)}` : `${num(d.points)} of ${num(d.max)}` })));
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
      UI.stackBar(barHost, segs.map(s => ({ ...s, label: s.key === 'scored' ? 'Scored' : `${s.label} −`, tip: s.key === 'scored' ? null : `${s.label}: −${num(s.value)} on ${s.n} question${s.n === 1 ? '' : 's'}` })),
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
    const podium = best && best.rank_if <= 3 && (d.rank || Infinity) > 3;
    if (ranked) {
      el.append(h('p', { class: 'debrief-line', text: best
        ? `Q${best.slot} right would have put you #${best.rank_if}${podium ? ': one fix from the podium.' : '.'}`
        : d.rank && d.all_right_rank >= d.rank ? `Fixes add points here, not places: you hold #${d.rank}.`   // "all right → #1" read oddly at #1
        : `All of them right → #${d.all_right_rank} of ${num(d.players)}.` }));
    }
    const unreached = lost.filter(r => r.kind === 'reach');
    const rows = lost.filter(r => r.kind !== 'reach').sort((a, b) => (b.places || 0) - (a.places || 0) || b.pts - a.pts);
    const ul = h('ul', { class: 'debrief-rows' });
    rows.forEach(r => {
      const what = r.kind === 'trap' || r.kind === 'slip' || r.kind === 'entry' ? `fell for ${String(label(r)).replace(/^./, x => x.toLowerCase())}` : (CAUSE[r.kind] || r.kind).toLowerCase();
      const text = [`Q${r.slot}`, r.topic && topicName(r.topic), TIER[r.tier], what, `−${num(r.pts)}`].filter(Boolean).join(' · ');
      // the place it buys shows only where it moves you and says something the headline doesn't
      const sub = ranked && r.places > 0 && r !== best && r.rank_if !== (best && best.rank_if) ? `right → #${r.rank_if} (+${r.places} place${r.places === 1 ? '' : 's'})` : '';
      let act = null;
      if (o.onFix) {
        const label = ['trap', 'slip', 'gap', 'entry'].includes(r.kind) ? 'Fix it · 3' : r.kind === 'clock' || r.kind === 'pace' ? 'Speed drill · 8' : r.kind === 'skip' ? 'Try it now' : null;
        if (label) { act = h('button', { type: 'button', class: 'quiet', text: label }); act.addEventListener('click', () => o.onFix(r, label)); }
      }
      ul.append(h('li', {}, h('span', { class: 'dr-t' }, text, r.rushed ? tip(h('span', { class: 'badge soft', text: 'Rushed' }), 'Answered in under a quarter of its time budget') : null,
        sub ? h('span', { class: 'dr-m', text: sub }) : null), act));
    });
    if (unreached.length) ul.append(h('li', {}, h('span', { class: 'dr-t', text: `Not reached · ${num(unreached.length)} question${unreached.length === 1 ? '' : 's'} · −${num(unreached.reduce((x, r) => x + r.pts, 0))}` })));
    if (ranked && best && d.all_right_rank) ul.append(h('li', {}, h('span', { class: 'dr-t', text: `All of them right → #${d.all_right_rank}` })));
    el.append(ul);
    // the five that move you most show; the rest are one tap away (decision 7)
    const extra = [...ul.children].slice(5, rows.length);
    if (extra.length > 1) {
      extra.forEach(li => { li.hidden = true; });
      const more = h('button', { type: 'button', class: 'quiet', text: `Show all ${rows.length}` });
      more.addEventListener('click', () => { extra.forEach(li => { li.hidden = false; }); more.remove(); });
      el.append(h('div', { class: 'debrief-act' }, more));
    }
    if (o.onRematch) {
      const n = lost.filter(r => !['pace', 'finish', 'reach'].includes(r.kind)).length;
      if (n) {
        let whenV = 'later';
        const act = h('div', { class: 'debrief-act' });
        const go = h('button', { type: 'button', class: 'btn sm', text: `Rematch my misses · ${n}` });
        go.addEventListener('click', async () => { go.disabled = true; try { await o.onRematch(whenV); } finally { go.disabled = false; } });
        act.append(go);
        under(act, [{ value: 'later', label: 'In 2 days' }, { value: 'now', label: 'Now' }], { value: 'later', label: 'When', onChange: v => { whenV = v; } });
        act.append(info(d.subject === 'rw' ? 'Same skills and difficulty, passages you haven’t seen. Coming back in 2 days fixes them for longer.'
          : 'Same types, new numbers, the same traps. Coming back in 2 days fixes them for longer.', 'About rematches'));
        el.append(act);
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
    const field = h('input', { class: 'field cx-code-in', id: 'cx-code', maxlength: '6', autocomplete: 'off', autocapitalize: 'characters', spellcheck: 'false', inputmode: 'text' });
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

  // seconds a question on the auto clock (the server's deps.PACE)
  const PACE = { math: 95, rw: 71 };
  // every skill of a subject, by slug: the create sheet's default pick
  const skillsOf = s => (s === 'rw' ? (UI.RW_DOMAINS || []).flatMap(d => d.skills) : (UI.TOPICS || []).map(t => t.slug));
  function create(prefill = {}) {
    // one subject a contest: the friend challenge's skills say which, else the subject in use
    const subject = prefill.subject || (prefill.topics && prefill.topics.length && UI.subjectOf ? UI.subjectOf(prefill.topics[0]) : UI.subject ? UI.subject.get() : 'math');
    const f = { subject, title: prefill.title || '', count: prefill.count || 10, source: 'skills', topics: new Set(prefill.topics || skillsOf(subject)),
      difficulty: 'all', format: 'both', clock: prefill.minutes ? 'custom' : 'auto', minutes: prefill.minutes || 16, open_for: 24, repeat: 'once', rounds: 7,
      twin: prefill.twin ?? false, reveal: 'each', strict: false, mode: 'custom', paper: null };
    const form = h('div', { class: 'cx-form' });
    const sum = h('p', { class: 'cx-sum', role: 'status' });
    const err = h('p', { class: 'cx-err', role: 'alert', hidden: true });
    const row = (label, ...kids) => h('fieldset', {}, h('legend', { text: label }), ...kids);
    const title = h('input', { class: 'field', id: 'cx-title', maxlength: '40', value: f.title, placeholder: 'Your name’s challenge', autocomplete: 'off' });
    title.addEventListener('input', () => { f.title = title.value; });
    form.append(h('div', {}, h('label', { class: 'label', for: 'cx-title', text: 'Title' }), title, h('p', { class: 'help', text: '3–40 characters. Empty: “{your name}’s challenge”.' })));
    const subjRow = row('Subject');
    under(subjRow, ['math', 'rw'].map(v => ({ value: v, label: UI.subjectLabel ? UI.subjectLabel(v) : v })), { value: f.subject, label: 'Subject', onChange: v => setSubject(v) });
    form.append(subjRow);
    // Papers or Custom: a race on one of the weekly papers, or on skills you pick (papers are Math)
    const modeRow = row('Contest on');
    under(modeRow, [{ value: 'custom', label: 'Custom' }, { value: 'papers', label: 'Papers' }], { value: 'custom', onChange: v => setMode(v) });
    form.append(modeRow);
    const papersBox = row('Papers');
    papersBox.hidden = true;
    form.append(papersBox);
    let srcCtl;
    const src = row('Questions from');
    srcCtl = under(src, [{ value: 'skills', label: 'Skills I pick' }, { value: 'my_traps', label: 'My open mistakes' }, { value: 'our_traps', label: 'Our open mistakes' }],
      { value: 'skills', onChange: v => {
        f.source = v; skillsBox.hidden = v === 'my_traps'; srcHelp.textContent = SRC_HELP[v];
        // the group's mistakes come from earlier rounds, so picking it makes a series rather than being a dead option (the user)
        if (v === 'our_traps' && f.repeat === 'once') repCtl.set('week');
        draw(); } });
    const SRC_HELP = { skills: '', my_traps: 'Your open mistakes’ question types, each with the same trap: beat me on the traps that catch me.', our_traps: 'A series: round 1 uses the skills below, then each round draws on the mistakes most of you hold open. Nobody is told who holds which.' };
    const srcHelp = h('p', { class: 'help' });
    src.append(srcHelp);
    form.append(src);
    const cnt = row('Questions');
    under(cnt, [5, 10, 15, 22].map(n => ({ value: n, label: String(n) })), { value: f.count, onChange: v => { f.count = v; draw(); } });
    form.append(cnt);
    // the skill picker: the subject's 4 domains, select-all per domain
    const skillsBox = row('Skills');
    const grid = h('div', { class: 'cx-skills' });
    function drawSkills() {
      const groups = f.subject === 'rw' ? (UI.RW_DOMAINS || []).map(d => [d.name, d.skills.map(s => ({ slug: s, short: topicName(s) }))])
        : (UI.DOMAINS || []).map(([dname, dshort]) => [dshort, (UI.TOPICS || []).filter(t => t.domain === dname)]);
      grid.replaceChildren(...groups.map(([dshort, topics]) => {
        const all = h('input', { type: 'checkbox' });
        const boxes = topics.map(t => { const c = h('input', { type: 'checkbox', value: t.slug }); c.checked = f.topics.has(t.slug); c.addEventListener('change', () => { c.checked ? f.topics.add(t.slug) : f.topics.delete(t.slug); syncAll(); draw(); }); return [c, t]; });
        const syncAll = () => { const on = boxes.filter(([c]) => c.checked).length; all.checked = on === boxes.length; all.indeterminate = on > 0 && on < boxes.length; };
        all.addEventListener('change', () => { boxes.forEach(([c, t]) => { c.checked = all.checked; all.checked ? f.topics.add(t.slug) : f.topics.delete(t.slug); }); draw(); });
        syncAll();
        return h('div', { class: 'dom' }, h('label', {}, all, dshort), boxes.map(([c, t]) => h('label', {}, c, t.short)));
      }));
    }
    drawSkills();
    skillsBox.append(grid);
    form.append(skillsBox);
    const diff = row('Difficulty');
    under(diff, [{ value: 'all', label: 'Easy → hard' }, { value: 'easy', label: 'Easy' }, { value: 'medium', label: 'Medium' }, { value: 'hard', label: 'Hard' }], { value: 'all', onChange: v => { f.difficulty = v; } });
    form.append(diff);
    const fmt = row('Format');
    under(fmt, [{ value: 'both', label: 'Both' }, { value: 'mcq', label: 'Multiple choice' }, { value: 'spr', label: 'Grid-in' }], { value: 'both', onChange: v => { f.format = v; } });
    form.append(fmt);
    const clock = row('Clock');
    const mins = h('input', { class: 'field cx-num', type: 'number', min: '5', max: '70', value: String(f.minutes), 'aria-label': 'Minutes', hidden: f.clock !== 'custom' });
    mins.addEventListener('input', () => { f.minutes = Math.max(5, Math.min(70, parseInt(mins.value, 10) || 16)); draw(); });
    const autoText = () => `Auto (${PACE[f.subject]} s a question)`;
    const clockCtl = under(clock, [{ value: 'auto', label: autoText() }, { value: 'custom', label: 'Minutes' }], { value: f.clock, onChange: v => { f.clock = v; mins.hidden = v !== 'custom'; draw(); } });
    clock.append(mins);
    form.append(clock);
    const openFor = row('Open for');
    const openCtl = under(openFor, [{ value: 1, label: '1 hour' }, { value: 24, label: '24 hours' }, { value: 72, label: '3 days' }, { value: 168, label: '7 days' }], { value: 24, onChange: v => { f.open_for = v; draw(); } });
    form.append(openFor);
    const rep = row('Repeat');
    const rounds = h('input', { class: 'field cx-num', type: 'number', min: '2', max: '30', value: String(f.rounds), 'aria-label': 'Rounds', hidden: true });
    rounds.addEventListener('input', () => { f.rounds = Math.max(2, Math.min(30, parseInt(rounds.value, 10) || 2)); draw(); });
    const repCtl = under(rep, [{ value: 'once', label: 'Once' }, { value: 'day', label: 'Every day' }, { value: 'week', label: 'Every week' }], { value: 'once', onChange: v => {
      f.repeat = v; rounds.hidden = v === 'once';
      if (v !== 'once') { f.rounds = v === 'day' ? 7 : 4; rounds.value = String(f.rounds); }
      openFor.hidden = v !== 'once';
      if (v === 'once' && f.source === 'our_traps') srcCtl.set('skills');
      draw();
    } });
    rep.append(h('label', { class: 'label', text: 'Rounds', hidden: true }), rounds, h('p', { class: 'help', text: 'One code and link join every round.' }));
    form.append(rep);
    const radios = (name, opts, v, set) => h('div', { class: 'cx-radio' }, opts.map(([val0, label]) => {
      const r = h('input', { type: 'radio', name, value: String(val0) }); r.checked = v === val0; r.addEventListener('change', () => set(val0));
      return h('label', { class: 'choice-row' }, r, h('span', { text: label }));
    }));
    // a twin has its own numbers; a written R&W item has none, so each student gets their own item instead
    const twinText = () => (f.subject === 'rw' ? 'Everyone gets their own questions: same skills and difficulty, a different passage'
      : 'Everyone gets their own twin: same skills and difficulty, different numbers');
    const twinBox = radios('cx-twin', [[false, 'Same questions for everyone: good for going over them together'], [true, twinText()]], f.twin, v => { f.twin = v; });
    form.append(row('Questions for each student', twinBox));
    form.append(row('Show answers', radios('cx-reveal', [['each', 'After each question'], ['end', 'At the end']], 'each', v => { f.reveal = v; })));
    const strictRow = row('Strict');
    if (UI.switch) UI.switch(strictRow, { checked: false, label: 'Strict', onChange: v => { f.strict = v; } });
    const strictText = () => 'Leaving the tab or window, or copying or pasting, flags the question. Before finishing, each flagged right answer gets one more question of the same skill and difficulty; a wrong one scores 0.';
    const strictHelp = h('p', { class: 'help', text: strictText() });
    strictRow.append(strictHelp);
    form.append(strictRow);
    const customRows = [src, cnt, skillsBox, diff, fmt];
    let papersLoaded = false;
    function setMode(v) {
      f.mode = v;
      customRows.forEach(x => { x.hidden = v === 'papers'; });
      if (v === 'custom') { skillsBox.hidden = f.source === 'my_traps'; fmt.hidden = f.subject === 'rw'; }
      papersBox.hidden = v !== 'papers';
      if (v === 'papers') { f.count = 22; f.twin = true; if (!papersLoaded) loadPapers(); }
      draw();
    }
    // R&W: its own skills, no grid-ins (no Format), no papers, 71 s a question
    function setSubject(v) {
      f.subject = v; f.topics = new Set(skillsOf(v));
      if (v === 'rw' && f.mode === 'papers') setMode('custom');
      modeRow.hidden = v === 'rw';
      fmt.hidden = v === 'rw' || f.mode === 'papers';
      drawSkills();
      clockCtl.el.querySelector('button').firstChild.textContent = autoText();
      twinBox.querySelector('input[value="true"] + span').textContent = twinText();
      strictHelp.textContent = strictText();
      draw();
    }
    async function loadPapers() {
      papersLoaded = true;
      papersBox.append(h('p', { class: 'help', text: 'Loading the papers…' }));
      try {
        const d = await api('/tests', { quiet: true });
        const list = (d.papers || []).slice().sort((a, b) => b.n - a.n);
        papersBox.replaceChildren(h('legend', { text: 'Papers' }));
        if (!list.length) { papersBox.append(h('p', { class: 'help', text: 'No papers yet.' })); return; }
        papersBox.append(h('p', { class: 'help', text: 'Module 1 of the paper: 22 questions, a new set of numbers for each student.' }),
          h('div', { class: 'cx-radio' }, list.map(p => {
            const r = h('input', { type: 'radio', name: 'cx-paper', value: String(p.n) });
            r.addEventListener('change', () => { f.paper = p.n; });
            const st = ((p.yours || {}).status);
            return h('label', { class: 'choice-row' }, r, h('span', { text: `Paper #${p.n} · ${p.label || ''}${st === 'completed' ? ' · sat' : st === 'in_progress' ? ' · in progress' : ''}` }));
          })));
      } catch (e) { papersLoaded = false; papersBox.replaceChildren(h('legend', { text: 'Papers' }), h('p', { class: 'help', text: 'Couldn’t load the papers. Switch to Custom and back to retry.' })); }
    }
    form.append(sum, err);
    modeRow.hidden = fmt.hidden = f.subject === 'rw';
    function draw() {
      const secs = f.clock === 'auto' ? f.count * PACE[f.subject] : f.minutes * 60;
      const closes = new Date(Date.now() + (f.repeat === 'once' ? f.open_for : f.repeat === 'day' ? 24 : 168) * 3600e3);
      const whenS = closes.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
      const src0 = f.source === 'skills' ? '' : f.source === 'my_traps' ? ' · from your open mistakes' : ' · from the mistakes you hold open together (round 2 on)';
      sum.textContent = `${f.count} questions · ${Math.round(secs / 60)} min${src0} · ${f.repeat === 'once' ? `open until ${whenS}` : `${f.rounds} rounds, ${f.repeat === 'day' ? 'daily' : 'weekly'}`}`;
    }
    draw();
    const sheet = UI.sheet({
      title: prefill.sheetTitle || 'Create a contest', size: 'l', body: b => b.append(form),
      actions: [{ label: 'Create', primary: true, onClick: () => { submit(); return false; } }],
    });
    async function submit() {
      err.hidden = true;
      const body = { subject: f.subject, count: f.count, source: f.source, twin: f.twin, reveal: f.reveal, strict: f.strict, format: f.subject === 'rw' ? 'mcq' : f.format,
        difficulty: f.difficulty === 'all' ? ['easy', 'medium', 'hard'] : [f.difficulty] };
      if (f.title.trim()) body.title = f.title.trim();
      if (f.mode === 'papers') {
        if (!f.paper) { err.hidden = false; err.textContent = 'Pick a paper.'; return; }
        body.paper = f.paper; body.count = 22; body.twin = true; body.source = 'skills';
      } else
      // round 1 of an our-mistakes series is drawn from the skills too (compete.create_contest needs them)
      if (f.source !== 'my_traps') {
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
      copyCode.addEventListener('click', () => copy(copyCode, r.code));
      copyLink.addEventListener('click', () => copy(copyLink, link));
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
    const t = h('input', { class: 'field cx-time', type: 'time', id: 'cx-rem', value: '17:00' });
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

  /* ------------------------------------------------------------ badge art (Profile and Compete draw achievements the same)
     one drawing per achievement on a 24 grid in the app's 1.6 stroke; a skill badge uses its topic glyph */
  const BADGE_PATHS = {
    streak: 'M12 3c1 3.2 4.5 5.2 4.5 9.2a4.5 4.5 0 0 1-9 0c0-2 1-3.2 2.2-4.4.1 1.8.9 2.6 1.8 2.8C11 7.8 11 5.4 12 3z',
    on_target: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9zM12 11a1 1 0 1 0 0 2 1 1 0 0 0 0-2z',
    consistency: 'M4 6l5-2 6 2 5-2v14l-5 2-6-2-5 2zM9 4v14M15 6v14',
    qotd: 'M3 17h18M7 17a5 5 0 0 1 10 0M12 5v3M5.2 9.2l1.8 1.8M18.8 9.2L17 11M2 21h20',
    answered: 'M6 21V4M6 5h12l-3 3.5L18 12H6',
    hard_right: 'M2.5 19L9 8l4.5 7.5 2-3L21.5 19zM9 8V4l3.5 1.5L9 7',
    hours: 'M7 3.5h10M7 20.5h10M8 3.5c0 5 8 5.5 8 8.5s-8 3.500-8 8.500M16 3.5c0 5-8 5.5-8 8.5s8 3.500 8 8.500',
    fixed: 'M3 20h18M5 20v-4M19 20v-4M5 16a7 7 0 0 1 14 0M9 16v-6M12 16V8.500M15 16v-6',
    clean_set: 'M5 7h14M5 12h9M5 17h6M14.500 16.500l2 2 4-4.500',
    never_twice: 'M12 7.500a2.500 2.500 0 1 0 0-5 2.500 2.500 0 0 0 0 5zM12 7.500V21M7 12h10M4.500 15c0 3.500 3.500 6 7.500 6s7.500-2.500 7.500-6',
    explorer: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM15.700 8.300l-2.200 5.200-5.200 2.200 2.200-5.200z',
    first_module: 'M12 21v-9M12 12C12 8 9 6 5 6c0 4 3 6 7 6zM12 15c0-3 2.500-5 6.500-5 0 3-2.500 5-6.500 5z',
    first_section: 'M2.500 20L12 4l9.500 16zM12 4v16M8.500 20L12 13l3.500 7',
    sections: 'M8 9a4 4 0 0 1 8 0v11H8zM8 14h8M10 9V6.500M14 9V6.500M16 12h2.500a1 1 0 0 1 1 1v7H16',
    upper_route: 'M6 21L10 4M18 21L14 4M12 21v-3M12 14.500v-3.500M12 8V6',
    climbing: 'M3.500 17.500l6-6 4 4 7-8.500M15 7h5.500v5.500',
    challenge: 'M7 3.500h10a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-13a2 2 0 0 1 2-2zM8.500 9h7M8.500 13h7M8.500 17h4',
    podium: 'M3 20.500h18M4 20.500v-5h5v5M9.500 20.500V10.500h5v10M15 20.500v-3h5v3M12 4.500l.7 1.500 1.600.2-1.200 1.100.3 1.600-1.400-.8-1.400.8.3-1.600L9.700 6.200 11.300 6z',
    first_place: 'M3.500 18.500l1.800-9.500 4.700 4 2-7 2 7 4.700-4 1.800 9.500zM4.500 21h15',
    perfect: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM8 12.500l2.700 2.700L16.300 9',
    'pace-setter': 'M12 21a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM12 13l3-3M10 2.500h4M12 5V2.500',
    'top-ten': 'M12 3l2.700 5.600 6.100.9-4.400 4.300 1 6.100L12 17l-5.400 2.900 1-6.100L3.200 9.500l6.100-.9z',
    'weekly-4': 'M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM8 3v4M16 3v4M4 10h16M8 14h2M14 14h2M8 17h2M14 17h2',
    sprinter: 'M13.500 3L5 14h6l-1 7 8.500-11h-6z',
    'dress-rehearsal': 'M6 21V4M6 5h12v8H6M10 5v8M14 5v8M6 9h12',
    'season-top-10': 'M12 20a5.500 5.500 0 1 0 0-11 5.500 5.500 0 0 0 0 11zM9 9L7 3h4l1 3.500M15 9l2-6h-4l-1 3.500',
    'level-5': 'M6 14l6-6 6 6M6 19l6-6 6 6',
    'level-8': 'M6 8l6-6 6 6M6 13l6-6 6 6M6 18l6-6 6 6',
    'all-rounder': 'M9 3.500a5.500 5.500 0 1 0 0 11 5.500 5.500 0 0 0 0-11zM15 3.500a5.500 5.500 0 1 0 0 11 5.500 5.500 0 0 0 0-11zM12 9.500a5.500 5.500 0 1 0 0 11 5.500 5.500 0 0 0 0-11z',
    'words-50': 'M4 20l6-16 6 16M6.500 14.500h7M19 3v5M16.500 5.500h5',
    'words-250': 'M20 4c-9 0-14 5-14 12v4.500l4.500-4.500c6.500 0 9.500-6.500 9.500-12zM6 20.500L16 10.500',
    'words-1000': 'M12 6c-2.500-2-5.500-2-8.500-1v13c3-1 6-1 8.500 1 2.500-2 5.500-2 8.500-1V5c-3-1-6-1-8.500 1zM12 6v13',
    'words-collection': 'M4 4v16M9 4v16M13 6.500l5 13.500M17 4.500l-1.500 1',
    'words-review-streak': 'M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM8 3v4M16 3v4M4 10h16M8.500 15l2.500 2.500 4.500-5',
    'domain:Algebra': 'M6 6l12 12M18 6L6 18M20 4v.01M4 20v.01',
    'domain:Advanced Math': 'M18 5H6.500L13 12l-6.500 7H18',
    'domain:Problem-Solving and Data Analysis': 'M4 20.500h16M6 20.500v-8M11 20.500V5M16 20.500v-10M21 20.500v-6',
    'domain:Geometry and Trigonometry': 'M4 19.500L15 5v14.500zM9.500 19.500a5.500 5.500 0 0 0 1-3.200',
  };
  const badgeSvg = (id, size) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${BADGE_PATHS[id]}"/></svg>`;
  // badgeIcon({id, icon}, earned, {size: 'sm'}) -> span.bcirc
  function badgeIcon(a, on, o = {}) {
    const id = String((a && a.id) || ''), topic = id.startsWith('skill:') ? id.slice(6) : null;
    const T = UI.TOPIC || {};
    const inner = topic && T[topic] && UI.glyph ? UI.glyph(topic)
      : BADGE_PATHS[id] ? h('span', { class: 'ic', html: badgeSvg(id, 24) })
      : a && BADGE_PATHS[a.icon] ? h('span', { class: 'ic', html: badgeSvg(a.icon, 24) })   // explorer:rw draws as explorer
      : a && T[a.icon] && UI.glyph ? UI.glyph(a.icon)
      : h('span', { class: 'ic', html: UI.svg ? UI.svg((UI.ICON && UI.ICON[a && a.icon]) || (UI.ICON && UI.ICON.trophy) || '', 22) : '' });
    return h('span', { class: 'bcirc' + (on ? ' on' : '') + (o.size === 'sm' ? ' sm' : ''), 'aria-hidden': 'true' }, inner);
  }

  /* ------------------------------------------------------------ strict mode (the runner's integrity seam)
     A runner's integrity event as compete.flag's vocabulary; the flag's body for /spot. */
  const SPOT_WHY = { blur: 'blur', hidden: 'left', fullscreen: 'left', copy: 'copyleave', paste: 'paste' };
  const spotBody = (qid, e) => ({ question_id: qid, why: SPOT_WHY[e.kind] || 'left', secs: Math.min(3600, Math.round((e.ms || 0) / 100) / 10) });
  // UI.compete.spotCheck(host, post): the spot-check before a strict contest finishes (compete.confirm_next).
  // post(body) is the sitting's /confirm. For each question answered right while the student was away, one
  // more of the same skill and difficulty: right keeps that question's points, wrong or skipped voids them.
  // Resolves once none is due (at once when nothing was flagged); never blocks a finish on an error.
  async function spotCheck(host, post) {
    let r;
    try { r = await post({}); } catch (_) { return; }
    let n = 0;
    while (r && r.due && r.question) {
      n += 1;
      const of = n + (r.left || 1) - 1;
      const answer = await new Promise(res => {
        let picked = null;
        const box = h('div', { class: 'spot-q' });
        const go = h('button', { type: 'button', class: 'pill', text: 'Submit', disabled: true });
        const skip = h('button', { type: 'button', class: 'quiet', text: 'Skip' });
        host.replaceChildren(h('section', { class: 'card spot', 'aria-labelledby': 'spot-h' },
          h('h2', { class: 'h2', id: 'spot-h', text: of > 1 ? `Spot-check · ${n} of ${of}` : 'Spot-check' }),
          h('p', { class: 'line', 'data-nofold': '', text: `You left the contest or copied during Q${r.slot || '?'}. Answer one more question of the same skill and difficulty: right keeps Q${r.slot || '?'}’s points; wrong or skipped, they don’t count.` }),
          box, h('div', { class: 'row-act' }, go, skip)));
        (UI.workspace || UI.question)(box, r.question, { mode: 'exam', onSelect: a => { picked = a; go.disabled = a === null || a === undefined || a === ''; } });
        go.addEventListener('click', () => res(picked));
        skip.addEventListener('click', () => res('_skip'));
      });
      try { r = await post({ answer }); } catch (_) { return; }
      if (r && r.last) toast(r.last.kept ? 'Kept: those points stand' : 'Not kept: that question’s points don’t count');
    }
  }

  // an explanation on demand (decision 7): the shared "?" (kit.js UI.why); "About the clock" names it
  // Copy says Copied in place (kit.js UI.saving announces it); a refused copy gets kit's copy sheet
  const copy = (b, text) => UI.copyText(text, { button: b });
  const info = (text, label) => UI.why(text, { about: label && label !== 'More about this' ? label.replace(/^About /, '') : null, anchored: true });

  Object.assign(UI, {
    level, board, podium, debrief, pacer,
    compete: { KINDS, kind, title, icon, svg: svgOf, SVG, href, runner, start, rulesSeen, markRules, windowLine, clockText, facts, marks,
      copyResult, under, subnav, join, create, reminder, ladder, parLine, fieldLine, pct, LADDER, levelOf, rangeOf, levelIn, step, left, when, dayLabel, localDay, titleText, periodText, topicName, TIER, num, mmss, info, copy,
      trapWords, trapLabel, normOf, streakBefore, DAY_WORD, badgeIcon, BADGE_PATHS, moved, spotBody, spotCheck },
  });
})();
