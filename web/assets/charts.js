/* ============================================================================
   SAT Freshman -- charts (spec/rebuild-v2.md 2.4 charts.js row; Shell 3.6 and 3.9,
   Today 6 and 9, Results 2.3 and 2.4, Report 1.3, Plan 3i and 3j, Compete 6, Words;
   v2-upgrades U7, U9, U16, T10, T17, X3, X12, X17, X20, X21, SR1, SR4, SR5, SR7,
   SR13, SR21, V9, P13, L6, L13, L21)

   Loaded after ui.js and kit.js; adds to window.UI with Object.assign. It uses kit's
   UI.tooltip, UI.pop, UI.seg and formatters when present and draws without them.

   Every chart is a <figure class="chart ...">: the drawing carries role=img and an
   aria-label summary, a visually hidden table (div.sr.chart-data > table) holds every number, and
   anything a student acts on is a real button laid over the drawing (one Tab stop,
   arrow keys move, Enter opens; hover and keyboard focus show the tooltip, a tap
   shows it with the action). The two month grids are role=grid (their cells are the
   controls); their scale legend is the role=img with the summary. SVG charts are drawn
   at the host's own width, so labels keep their CSS size, and redraw when it changes.
   Colours come from ui.css tokens, so dark mode and print need nothing here.

   A host may be null: the figure is returned for the caller to place. Each returns
   {el, set(data?, opts?)}; set() merges opts and redraws.

   Days are local 'YYYY-MM-DD' strings (X-Tz); times are ISO strings, Dates or ms.

   UI.bandChart(host, points, opts)                    also UI.trend, UI.scoreChart
     points: [{id, at | finished | day, low, high (or estimate {low, high}, or value for
       one number), mid?, kind: mock | paper | custom | module | diagnostic | outside,
       outside: 'Bluebook' | true (an added score: a hollow diamond), label ('Section #7'),
       detail ('31/44 · harder M2'), right, asked, href, tip}]
     opts: {height (200; 160 on a phone; under 110 draws the mini trend), min, max, grid,
       fit (y fitted to the data ±50, gridlines every 50), x: 'sitting' | 'time', from, to,
       target, exam, estimate {low, high}, outside (false hides added scores), now,
       projection {low, high, mid, to, label} | null (null: the "three modules" line),
       pace {from {day, value}, to {day, value}, aims [{day, value, beaten}]},
       gaps [{from, to, text | questions, minutes, fixed, moved, delta}] (ids or indexes),
       pairs [[idA, idB]], rw [{day, value, source}], onPick(point), compare(newer, older),
       filters (Range and kind controls), store (localStorage key for them), legend,
       empty {text, action {label, href, onClick}}, label}
   UI.gauge(host, {band {low, high}, target, previous {low, high, label}, today, second,
       whatif, subject, sub, caption, animate, min, max}) -> {el, set}
       layers bottom to top: scale, previous, today (dotted), with a second look (hollow),
       what if (dashed, replaces today), this sitting (orange, graphite midpoint), target
   UI.scale(host, {band, target, start, previous, estimate, min, max, ticks [{value,
       label}], dot, label (band text above), animate, hist {counts, min, bin, avg, you},
       compact})
   UI.barChart(host, rows, opts)
     rows: [{key | day | label, value | <series key>: n, planned, line, budget, status,
       today, exam, tip, href, sub}]
     opts: {series [{key, label, look: ink | soft | amber | hatch | mat}], down [{...}]
       (drawn below the axis), stacked, norm (100%), planned, pace (n | {value, label}),
       line {key, label}, budget, unit: min | s | q | pts | '%', format(v), noun ('due'), labels:
       weekday | date | label | fn, today: ring | amber, height, max, onPick(row, i),
       legend, label}
   UI.calendar(host, {month, days, plan, marks {exam, start, end, today}, onPick(day, row),
       onMonth(month), min, max, goal, metric: minutes | questions | accuracy | fixed,
       metrics (the metric seg), look: heat | plan, compact, selected, legend})
       -> {el, go(month), select(day), set}                          also UI.monthGrid
     days: [{day, minutes, questions, right, fixed, rest, spare_used, due {checks},
       load}]; plan: [{day, kind: practice | test | rest | off | eve, state: done |
       partial | missed | skipped | madeup | future, minutes, tasks {done, of}, own,
       phase, phase_start, load}]
   UI.heatmap(host, days, {weeks, end, onPick(day, row), range, onRange(weeks), stats
       {active_days, streak, best, minutes}, legend})
   UI.lineChart(host, series, {bands [{from, to, label}], height, invert, log, min, max,
       grid [values], x: time | index, format(y), xFormat(x), onPick(point, series),
       annotate [{x, text}], label})
     series: [{key, label, points [{x | day | at, y, label, href, star, tip}], dashed, you}]
   UI.spread(host, options, {n, label, noun})
     options: [{label, text, share | n, key, pick, reason}]
   UI.quadrant(host, points, {x: seconds | ratio, xRef, y: accuracy, yRef, log, xMin,
       xMax, names {slow_right, fast_wrong, slow_wrong, fast_right}, onPick, list, action(point, q),
       actions {q: {label, href | onClick(points)}} | fn(q, count),
       height, label})
     points: [{id, label, topic, x, y (0-1), n, href}]
   UI.spark(host, series, {label, w, h, format, ref})
   UI.stackBar(host, segments, {onPick(seg), unit, approx, format, total, largest,
       legend, noun, label})
     segments: [{key, label, value, n, tip, hatch}]
   UI.clockLane(host, visits, {items {qid: {label, status, changed, flag}}, duration,
       budgets {qid: ms}, order [qid], marks [{t, kind: flag | change | end, qid}],
       onPick(qid), label})
     visits: [[qid, t_in, t_out]] in module-elapsed ms
   UI.dotStrip(host, counts, {min, bin, band {low, high}, you, avg, noun, label})
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI = window.UI || {};
  const doc = document;
  const NS = 'http://www.w3.org/2000/svg';

  /* ------------------------------------------------------------ helpers */
  let seq = 0;
  const uid = p => `ch${p}${++seq}`;
  function h(tag, attrs = {}, ...kids) {
    const e = doc.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k === 'style') e.style.cssText = v;
      else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat(3)) if (k !== null && k !== undefined && k !== false) e.append(k instanceof Node ? k : String(k));
    return e;
  }
  function sv(tag, attrs = {}, parent) {
    const e = doc.createElementNS(NS, tag);
    for (const k in attrs) if (attrs[k] !== null && attrs[k] !== undefined && attrs[k] !== false) e.setAttribute(k, attrs[k]);
    if (parent) parent.append(e);
    return e;
  }
  const r1 = v => Math.round(v * 10) / 10;
  function tx(parent, x, y, text, attrs = {}) {
    const t = sv('text', { x: r1(x), y: r1(y), ...attrs }, parent);
    t.textContent = text;
    return t;
  }
  const put = (host, el) => { if (host) host.append(el); return el; };
  const media = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
  const phone = () => media('(max-width: 759px)');
  const still = () => media('(prefers-reduced-motion: reduce)') || doc.documentElement.dataset.motion === 'reduce';
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const isNum = v => typeof v === 'number' && isFinite(v);
  const n0 = v => (isNum(+v) ? +v : 0);
  const sum = a => a.reduce((s, v) => s + n0(v), 0);
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const textW = (s, px = 11) => String(s).length * px * 0.62;       // DM Mono is about 0.6em a glyph
  // labels keep clear of the drawing: the first candidate [x, baseline, anchor] whose text box
  // meets no obstacle box [x0, y0, x1, y1] (placed labels join obs), else null
  function clearOf(cands, text, obs, px = 11) {
    const w = textW(text, px);
    for (const [x, y, a] of cands) {
      const x0 = a === 'end' ? x - w : a === 'middle' ? x - w / 2 : x;
      const b = [x0 - 2, y - px, x0 + w + 2, y + 3];
      if (!obs.some(o => o[0] < b[2] && o[2] > b[0] && o[1] < b[3] && o[3] > b[1])) { obs.push(b); return [x, y, a]; }
    }
    return null;
  }
  // a polyline as boxes every few px, so a label can keep off the line as well as its dots
  function lineBoxes(pts, r = 5, step = 6) {
    const out = [];
    pts.forEach(([x, y], i) => {
      if (i) {
        const [ax, ay] = pts[i - 1], n = Math.floor(Math.hypot(x - ax, y - ay) / step);
        for (let k = 1; k < n; k++) { const px = ax + (x - ax) * k / n, py = ay + (y - ay) * k / n; out.push([px - r, py - r, px + r, py + r]); }
      }
      out.push([x - r, y - r, x + r, y + r]);
    });
    return out;
  }

  /* dates: local days at noon, so a day never slips across midnight */
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const DOWL = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  function toDate(d) {
    if (d instanceof Date) return d;
    if (typeof d === 'number') return new Date(d);
    const s = String(d ?? '');
    const m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m ? new Date(+m[1], +m[2] - 1, +m[3], 12) : new Date(s);
  }
  const iso = d => { d = toDate(d); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
  const addDays = (d, n) => { const x = toDate(iso(d)); x.setDate(x.getDate() + n); return iso(x); };
  const today = () => iso(new Date());
  const monOf = d => { const x = toDate(iso(d)); return addDays(x, -((x.getDay() + 6) % 7)); };   // the Monday of its week
  const ym = d => iso(d).slice(0, 7);
  const fdate = d => (UI.date ? UI.date(d) : `${MON[toDate(d).getMonth()]} ${toDate(d).getDate()}`);
  const flong = d => (UI.date ? UI.date(d, 'long') : `${DOW[toDate(d).getDay()]}, ${fdate(d)}`);
  const fnum = v => (v === null || v === undefined || v === '' || !isFinite(v) ? '—' : (UI.num ? UI.num(v) : String(Math.round(v))));
  const fdur = m => (UI.dur ? UI.dur(m) : `${Math.round(m)}m`);
  const fmin = m => (Math.round(m) < 60 ? `${Math.round(m)} min` : fdur(m));
  const fmmss = s => (UI.mmss ? UI.mmss(s) : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`);
  const fband = (lo, hi) => (lo === hi ? fnum(lo) : `${fnum(lo)}–${fnum(hi)}`);
  const pct = v => `${Math.round(v * 100)}%`;
  const plural = (n, word) => `${fnum(n)} ${word}${n === 1 ? '' : 's'}`;
  const hm = t => { const d = toDate(t); return `${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`; };
  const kindName = k => (UI.KIND && UI.KIND[k]) || ({ mock: 'Section', module: 'Module', diagnostic: 'Diagnostic', outside: 'Added score' })[k] || (k ? k[0].toUpperCase() + k.slice(1) : 'Sitting');
  const glyphOf = st => (UI.STATES && UI.STATES[st] && UI.STATES[st].glyph) || '';
  const labelOf = st => (UI.STATES && UI.STATES[st] && UI.STATES[st].label) || (st ? st[0].toUpperCase() + st.slice(1).replace(/_/g, ' ') : '');
  const byDay = rows => {
    const m = new Map();
    if (Array.isArray(rows)) rows.forEach(r => r && r.day && m.set(iso(r.day), r));
    else if (rows && typeof rows === 'object') Object.entries(rows).forEach(([d, r]) => m.set(iso(d), { day: d, ...(typeof r === 'object' ? r : { value: r }) }));
    return m;
  };
  function niceMax(v) {
    if (!(v > 0)) return 1;
    const p = Math.pow(10, Math.floor(Math.log10(v))), f = v / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p;
  }

  /* ------------------------------------------------------------ the frame */
  function frame(host, cls, o = {}) {
    const el = h('figure', { class: `chart ${cls}` + (o.className ? ' ' + o.className : '') });
    const plot = h('div', { class: 'chart-plot' });
    el.append(plot);
    put(host, el);
    return { el, plot };
  }
  function svgRoot(W, H, label) {
    return sv('svg', { viewBox: `0 0 ${Math.round(W)} ${Math.round(H)}`, width: Math.round(W), height: Math.round(H), role: 'img', 'aria-label': label, focusable: 'false' });
  }
  // a 45-degree hatch, drawn in the ink of its class (ch-hatch-ln), for tests, relapses and R&W
  function hatch(svg, cls = '') {
    const id = uid('h');
    const defs = sv('defs', {}, svg);
    const p = sv('pattern', { id, width: 5, height: 5, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, defs);
    sv('rect', { width: 5, height: 5, class: 'ch-hatch-bg' + (cls ? ' ' + cls : '') }, p);
    sv('line', { x1: 1, y1: 0, x2: 1, y2: 5, class: 'ch-hatch-ln' + (cls ? ' ' + cls : '') }, p);
    return `url(#${id})`;
  }
  // every number in a hidden table; cells may be strings or numbers
  // (a table ignores width and overflow, so a 1px .sr box holds it, or it would widen the page)
  function dataTable(caption, head, rows) {
    return h('div', { class: 'sr chart-data' }, h('table', {},
      h('caption', { text: caption }),
      h('thead', {}, h('tr', {}, head.map(c => h('th', { scope: 'col', text: c })))),
      h('tbody', {}, rows.map(r => h('tr', {}, r.map((c, i) => h(i ? 'td' : 'th', i ? {} : { scope: 'row' }, c === null || c === undefined || c === '' ? '—' : String(c))))))));
  }
  function setTable(el, t) {
    const old = el.querySelector(':scope > .chart-data');
    if (old) old.replaceWith(t); else el.append(t);
  }
  // draw at the plot's pixel width and again whenever the width changes
  function sized(plot, draw) {
    let w = -1;
    const run = force => {
      const nw = Math.round(plot.clientWidth) || 0;
      if (!force && nw && Math.abs(nw - w) < 2) return;
      if (!force && !nw && w > 0) return;
      w = nw;
      draw(nw || 640);
    };
    if (window.ResizeObserver) new ResizeObserver(() => requestAnimationFrame(() => run(false))).observe(plot);
    else addEventListener('resize', () => run(false));
    return { redraw: () => run(true) };
  }

  // the controls over a drawing: one Tab stop, arrows move, Enter picks; a tap shows the tip with its action
  function hitLayer(plot, items, o = {}) {
    const old = plot.querySelector(':scope > .chart-hits');
    if (old) old.remove();
    if (!items.length) return null;
    const layer = h('div', { class: 'chart-hits', role: 'group', 'aria-label': o.label || 'Chart points' });
    let cur = clamp(o.start ?? items.length - 1, 0, items.length - 1), ptr = '';
    const btns = items.map((it, i) => {
      const b = h('button', {
        type: 'button', class: 'chart-hit' + (it.pick ? ' go' : '') + (it.cls ? ' ' + it.cls : ''), tabindex: i === cur ? '0' : '-1', 'aria-label': it.label,
        'aria-pressed': it.pressed === undefined ? null : String(!!it.pressed),
        style: `left:${r1(it.x)}px;top:${r1(it.y)}px;width:${r1(Math.max(1, it.w))}px;height:${r1(Math.max(1, it.h))}px`,
      });
      if (it.tip && UI.tooltip) UI.tooltip(b, it.tip, { delay: 60 });
      b.addEventListener('pointerdown', e => { ptr = e.pointerType; });
      b.addEventListener('focus', () => { cur = i; btns.forEach((x, k) => { x.tabIndex = k === i ? 0 : -1; }); if (o.onFocus) o.onFocus(it, i); });
      b.addEventListener('blur', () => { if (o.onFocus) o.onFocus(null); });
      b.addEventListener('pointerenter', e => { if (e.pointerType === 'mouse' && o.onFocus) o.onFocus(it, i); });
      b.addEventListener('pointerleave', () => { if (o.onFocus && doc.activeElement !== b) o.onFocus(null); });
      b.addEventListener('click', e => {
        const touch = ptr === 'touch' || ptr === 'pen';
        ptr = '';
        if (touch && it.tip && UI.pop) {
          UI.pop(b, (el, res) => [
            h('p', { class: 'chart-pop-t', text: typeof it.tip === 'function' ? it.tip() : it.tip }),
            it.pick ? h('button', { type: 'button', class: 'btn sm', onclick: ev => { res.close(); it.pick(ev); } }, it.action || 'Open') : null,
          ].filter(Boolean), { label: it.label });
          return;
        }
        if (it.pick) it.pick(e);
      });
      return b;
    });
    layer.addEventListener('keydown', e => {
      const i = btns.indexOf(doc.activeElement);
      if (i < 0) return;
      const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
      let j = null;
      if (step) j = clamp(i + step, 0, btns.length - 1);
      else if (e.key === 'Home') j = 0;
      else if (e.key === 'End') j = btns.length - 1;
      if (j === null) return;
      e.preventDefault();
      btns[j].focus();
    });
    layer.append(...btns);
    plot.append(layer);
    return { layer, btns };
  }

  // a legend of chart marks: [{key: swatch kind, label, n}]
  function keySwatch(kind) {
    const s = sv('svg', { class: 'ch-key', width: 18, height: 12, viewBox: '0 0 18 12', 'aria-hidden': 'true', focusable: 'false' });
    const f = kind === 'hatch' || kind === 'rw' || kind === 'bar-hatch' ? hatch(s) : null;
    const S = {
      band: () => sv('rect', { x: 6, y: 0, width: 6, height: 12, rx: 2, class: 'ch-band sec' }, s),
      mod: () => sv('rect', { x: 6, y: 0, width: 6, height: 12, rx: 2, class: 'ch-band mod' }, s),
      diag: () => sv('rect', { x: 6.5, y: .75, width: 5, height: 10.5, rx: 2, class: 'ch-band diag' }, s),
      now: () => sv('rect', { x: 6, y: 0, width: 6, height: 12, rx: 2, class: 'ch-band now' }, s),
      diamond: () => sv('path', { d: 'M9 1.5 L13.5 6 L9 10.5 L4.5 6 Z', class: 'ch-dia' }, s),
      line: () => sv('path', { d: 'M1 6 H17', class: 'ch-trend' }, s),
      target: () => sv('path', { d: 'M1 6 H17', class: 'ch-target' }, s),
      pace: () => sv('path', { d: 'M1 6 H17', class: 'ch-pace' }, s),
      dash: () => sv('path', { d: 'M1 6 H17', class: 'ch-line dashed' }, s),
      zone: () => sv('rect', { x: 1, y: 2, width: 16, height: 8, class: 'ch-zone' }, s),
      cone: () => sv('path', { d: 'M1 6 L17 1 L17 11 Z', class: 'ch-cone' }, s),
      bracket: () => sv('path', { d: 'M2 3 V9 H16 V3', class: 'ch-bracket' }, s),
      rw: () => sv('rect', { x: 1, y: 3, width: 16, height: 6, rx: 2, fill: f, class: 'ch-rw-sw' }, s),
      exam: () => sv('path', { d: 'M9 0 V12', class: 'ch-exam' }, s),
      dot: () => sv('circle', { cx: 9, cy: 6, r: 4, class: 'ch-dot' }, s),
      star: () => sv('path', { d: starPath(9, 6, 5), class: 'ch-star' }, s),
      'bar-hatch': () => sv('rect', { x: 3, y: 1, width: 12, height: 10, rx: 2, fill: f, class: 'ch-f-hatch' }, s),
      'bar-plan': () => sv('rect', { x: 3.75, y: 1.75, width: 10.5, height: 8.5, rx: 2, class: 'ch-plan' }, s),
    };
    if (S[kind]) S[kind]();
    else if (kind && kind.startsWith('bar-')) sv('rect', { x: 3, y: 1, width: 12, height: 10, rx: 2, class: `ch-f-${kind.slice(4)}` }, s);
    else if (kind && kind.startsWith('shade-')) sv('rect', { x: 3, y: 1, width: 12, height: 10, rx: 2, class: `sb-shade`, 'data-shade': kind.slice(6) }, s);
    return s;
  }
  function chartKey(items) {
    return h('ul', { class: 'legend chart-key', 'aria-label': 'Legend' }, items.filter(Boolean).map(it =>
      h('li', { class: it.disabled ? 'off' : null }, it.swatch || keySwatch(it.key), h('span', { text: it.label }),
        it.n !== undefined && it.n !== null ? h('b', { text: typeof it.n === 'number' ? fnum(it.n) : it.n }) : null)));
  }
  function starPath(cx, cy, r) {
    const p = [];
    for (let k = 0; k < 10; k++) {
      const a = Math.PI / 5 * k - Math.PI / 2, rr = k % 2 ? r * .45 : r;
      p.push(`${r1(cx + rr * Math.cos(a))} ${r1(cy + rr * Math.sin(a))}`);
    }
    return `M${p.join(' L')} Z`;
  }
  const emptyAct = a => (a ? h(a.href ? 'a' : 'button', { class: 'btn sm', href: a.href || null, type: a.href ? null : 'button', onclick: a.onClick || null }, a.label) : null);
  function emptyNote(plot, e = {}, def) {
    const old = plot.querySelector(':scope > .chart-empty');
    if (old) old.remove();
    if (!e) return;
    plot.append(h('div', { class: 'chart-empty' }, h('p', { text: e.text || def }), emptyAct(e.action)));
  }
  // the same, in flow, for a chart with no plot to lay it over (spread, stackBar)
  const emptyBlock = (e = {}, def) => h('div', { class: 'empty' }, h('p', { class: 'empty-text', text: e.text || def }), emptyAct(e.action));
  function note(el, cls, text) {
    let p = el.querySelector(`:scope > .${cls}`);
    if (!text) { if (p) p.remove(); return; }
    if (!p) { p = h('p', { class: `chart-note ${cls}` }); el.append(p); }
    p.textContent = text;
  }
  // bar with its data end rounded (up: the top; down: the bottom), square at the baseline
  function barPath(x, y0, y1, w, round) {
    const top = Math.min(y0, y1), ht = Math.abs(y1 - y0);
    const r = round ? Math.min(4, w / 2, ht) : 0;
    if (!r) return `M${r1(x)} ${r1(top)}h${r1(w)}v${r1(ht)}h${r1(-w)}Z`;
    if (y1 < y0) return `M${r1(x)} ${r1(y0)}V${r1(y1 + r)}Q${r1(x)} ${r1(y1)} ${r1(x + r)} ${r1(y1)}H${r1(x + w - r)}Q${r1(x + w)} ${r1(y1)} ${r1(x + w)} ${r1(y1 + r)}V${r1(y0)}Z`;
    return `M${r1(x)} ${r1(y0)}V${r1(y1 - r)}Q${r1(x)} ${r1(y1)} ${r1(x + r)} ${r1(y1)}H${r1(x + w - r)}Q${r1(x + w)} ${r1(y1)} ${r1(x + w)} ${r1(y1 - r)}V${r1(y0)}Z`;
  }

  /* ============================================================ UI.bandChart */
  function normPoint(p, i) {
    const e = p.estimate || p.band || p;
    let low = +e.low, high = +e.high;
    const v = p.value ?? p.math ?? p.score;
    if (!isNum(low) && v !== undefined && v !== null && isNum(+v)) low = high = +v;
    if (!isNum(high)) high = low;
    const outside = p.outside || (p.kind === 'outside' ? (p.source || true) : null);
    return { ...p, _i: i, low, high, mid: isNum(p.mid) ? p.mid : (low + high) / 2,
      at: toDate(p.at ?? p.finished ?? p.day ?? p.date ?? Date.now()),
      outside, kind: outside ? 'outside' : (p.kind || 'mock') };
  }
  const bandKind = p => (p.kind === 'outside' ? 'dia' : p.kind === 'module' ? 'mod' : p.kind === 'diagnostic' ? 'diag' : 'sec');
  function pointName(p) {
    if (p.outside) return typeof p.outside === 'string' ? p.outside : (p.source || 'Added score');
    return p.label || (p.seq ? `${kindName(p.kind)} #${p.seq}` : kindName(p.kind));
  }
  function pointTip(p, sameDay) {
    if (p.tip) return p.tip;
    const when = sameDay ? `${fdate(p.at)} ${hm(p.at)}` : fdate(p.at);
    const score = p.outside ? fband(p.low, p.high) + ' · added by you' : fband(p.low, p.high);
    const detail = p.detail || (isNum(p.right) && isNum(p.asked) ? `${p.right}/${p.asked}` : '');
    return [when, pointName(p), score, detail].filter(Boolean).join(' · ');
  }
  function gapText(g, a, b) {
    if (g.text) return g.text;
    const bits = [`${fdate(a.at)} → ${fdate(b.at)}:`];
    const rest = [
      isNum(g.questions) && `${fnum(g.questions)} questions`,
      isNum(g.minutes) && fdur(g.minutes),
      isNum(g.fixed) && `${fnum(g.fixed)} mistake${g.fixed === 1 ? '' : 's'} fixed`,
      ...[].concat(g.moved || []).map(m => (typeof m === 'string' ? m : `${m.label || m.topic} → ${m.to}`)),
      isNum(g.delta) && `${g.delta > 0 ? '+' : ''}${g.delta}`,
    ].filter(Boolean);
    return `${bits[0]} ${rest.join(' · ') || `${fband(a.low, a.high)} → ${fband(b.low, b.high)}`}`;
  }

  function bandChart(host, points, o = {}) {
    const { el, plot } = frame(host, 'band-chart', o);
    const opts = { ...o };
    let all = [];
    const ctl = h('div', { class: 'chart-ctl' });
    const foot = h('div', { class: 'chart-foot' });
    el.prepend(ctl);
    el.append(foot);
    const filt = { range: 'all', off: [], ...(opts.store ? ls.get(opts.store, {}) : {}) };
    let comparing = false, picked = [];

    function shown() {
      let p = all.filter(x => opts.outside !== false || !x.outside);
      if (!opts.filters) return p;
      const off = new Set(filt.off || []);
      p = p.filter(x => !off.has(bandKind(x)));
      if (filt.range === '10') p = p.slice(-10);
      else if (filt.range === '30') { const cut = Date.now() - 30 * 864e5; p = p.filter(x => +x.at >= cut); }
      return p;
    }
    function buildCtl() {
      ctl.replaceChildren();
      ctl.hidden = !opts.filters;
      if (!opts.filters || !UI.seg) return;
      const save = () => { if (opts.store) ls.set(opts.store, filt); sz.redraw(); };
      UI.seg(ctl, [{ value: '10', label: 'Last 10' }, { value: '30', label: '30 days' }, { value: 'all', label: 'All' }],
        { value: filt.range, label: 'Range', onChange: v => { filt.range = v; save(); } });
      const count = k => all.filter(x => bandKind(x) === k).length;
      const kinds = [['sec', 'Sections'], ['mod', 'Modules'], ['diag', 'Diagnostic'], ['dia', 'Added']].filter(([k]) => count(k));
      if (kinds.length > 1) {
        UI.seg(ctl, kinds.map(([value, label]) => ({ value, label, n: count(value) })),
          { multi: true, value: kinds.map(k => k[0]).filter(k => !(filt.off || []).includes(k)), label: 'Kinds',
            onChange: on => { filt.off = kinds.map(k => k[0]).filter(k => !on.includes(k)); save(); } });
      }
    }

    function draw(W) {
      const pts = shown();
      const ph = phone();
      const H = opts.height ?? (ph ? 160 : 200);
      const mini = H < 110;
      const L = mini ? 4 : 36, R = mini ? 4 : 10, T = mini ? 6 : 16, B = mini ? 6 : 24;
      const rw = !mini && Array.isArray(opts.rw) && opts.rw.length ? opts.rw.map(r => ({ ...r, at: toDate(r.day ?? r.at), value: +r.value })).filter(r => isNum(r.value)).sort((a, b) => a.at - b.at) : [];
      const laneH = rw.length ? 58 : 0;
      const TH = H + (laneH ? laneH + 12 : 0);
      const scored = pts.filter(p => !p.outside);
      const last = scored[scored.length - 1] || null;
      const proj = opts.projection && last ? opts.projection : null;
      const examT = opts.exam ? toDate(opts.exam) : proj && proj.to ? toDate(proj.to) : null;
      const lastT = pts.length ? pts[pts.length - 1].at : null;
      const endT = examT && (!lastT || examT > lastT) ? examT : null;

      // y
      let lo = opts.min ?? 200, hi = opts.max ?? 800, step = opts.grid ?? 100;
      if ((opts.fit || (mini && opts.min === undefined && opts.max === undefined)) && pts.length) {
        const vals = [...pts.flatMap(p => [p.low, p.high]), opts.target, proj && proj.low, proj && proj.high,
          opts.pace && opts.pace.from && opts.pace.from.value, opts.pace && opts.pace.to && opts.pace.to.value].filter(isNum);
        step = opts.grid ?? 50;
        lo = Math.max(opts.min ?? 200, Math.floor((Math.min(...vals) - 50) / step) * step);
        hi = Math.min(opts.max ?? 800, Math.ceil((Math.max(...vals) + 50) / step) * step);
        if (hi - lo < step * 2) hi = lo + step * 2;
      }
      const y = v => T + (H - T - B) * (1 - (clamp(v, lo, hi) - lo) / (hi - lo));
      const plotW = W - L - R;

      // x: by sitting (evenly, newest right, the exam in a last slot) or by time
      let xs, xOf, slot;
      if (opts.x === 'time') {
        const t0 = toDate(opts.from ?? (pts[0] ? pts[0].at : Date.now())), t1 = toDate(opts.to ?? endT ?? lastT ?? Date.now());
        const span = Math.max(864e5, t1 - t0), pad = mini ? 4 : 12;
        xOf = t => L + pad + (plotW - 2 * pad) * clamp((toDate(t) - t0) / span, 0, 1);
        xs = pts.map(p => xOf(p.at));
        const gaps = xs.slice(1).map((x, i) => x - xs[i]).filter(g => g > 0);
        slot = Math.min(44, gaps.length ? Math.min(...gaps) : 44);
      } else {
        const used = pts.length + (endT ? 1 : 0);
        const slots = Math.max(used, mini ? used : 6, 1);
        slot = plotW / slots;
        const off = slots - used;
        xs = pts.map((p, i) => L + slot * (off + i + .5));
        const A = pts.map((p, i) => [+p.at, xs[i]]);
        if (endT) A.push([+endT, L + slot * (slots - .5)]);
        xOf = t => {
          t = +toDate(t);
          if (!A.length) return L + plotW / 2;
          if (A.length === 1) return A[0][1];
          const seg = (a, b) => (b[0] > a[0] ? a[1] + (t - a[0]) / (b[0] - a[0]) * (b[1] - a[1]) : b[1]);
          if (t <= A[0][0]) return Math.max(L, seg(A[0], A[1]));
          for (let i = 1; i < A.length; i++) if (t <= A[i][0]) return seg(A[i - 1], A[i]);
          return Math.min(W - R, seg(A[A.length - 2], A[A.length - 1]));
        };
      }
      const bw = clamp(slot * .5, 3, mini ? 10 : 14);

      const sumBits = [];
      const svg = svgRoot(W, TH, '');
      const hatchFill = rw.length ? hatch(svg, 'rw') : null;
      // gridlines and the scale
      const grid = sv('g', { class: 'ch-grid' }, svg);
      if (!mini) for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) {
        sv('line', { x1: L, x2: W - R, y1: r1(y(v)), y2: r1(y(v)) }, grid);
        tx(grid, L - 7, y(v) + 3.5, v, { 'text-anchor': 'end', class: 'ch-ytick' });
      }
      else sv('line', { x1: L, x2: W - R, y1: H - B, y2: H - B }, grid);
      // estimate zone
      const est = opts.estimate && isNum(+opts.estimate.low) ? opts.estimate : null;
      if (est) sv('rect', { x: L, width: plotW, y: r1(y(est.high)), height: r1(Math.max(2, y(est.low) - y(est.high))), class: 'ch-zone' }, svg);
      // projection cone from the newest sitting to the exam date
      if (proj && isNum(+proj.low) && isNum(+proj.high)) {
        const xa = xs[pts.indexOf(last)], xe = xOf(proj.to || examT || last.at);
        sv('path', { class: 'ch-cone', d: `M${r1(xa)} ${r1(y(last.low))} L${r1(xe)} ${r1(y(proj.low))} L${r1(xe)} ${r1(y(proj.high))} L${r1(xa)} ${r1(y(last.high))} Z` }, svg);
        const pm = isNum(+proj.mid) ? +proj.mid : (+proj.low + +proj.high) / 2;
        sv('path', { class: 'ch-cone-mid', d: `M${r1(xa)} ${r1(y(last.mid))} L${r1(xe)} ${r1(y(pm))}` }, svg);
        sumBits.push(proj.label || `if this pace held, ${fband(proj.low, proj.high)}${proj.to || examT ? ` on ${fdate(proj.to || examT)}` : ''}`);
      }
      // the plan's pace line, its checkpoints filled when beaten
      const pace = opts.pace && opts.pace.from && opts.pace.to ? opts.pace : null;
      if (pace) {
        sv('path', { class: 'ch-pace', d: `M${r1(xOf(pace.from.day))} ${r1(y(pace.from.value))} L${r1(xOf(pace.to.day))} ${r1(y(pace.to.value))}` }, svg);
        (pace.aims || []).forEach(a => sv('circle', { cx: r1(xOf(a.day)), cy: r1(y(a.value)), r: mini ? 2.5 : 3.5, class: 'ch-aim' + (a.beaten ? ' on' : '') }, svg));
      }
      // target
      const tgt = isNum(+opts.target) && opts.target !== null && opts.target !== '' ? +opts.target : null;
      if (tgt !== null) {
        sv('line', { x1: L, x2: W - R, y1: r1(y(tgt)), y2: r1(y(tgt)), class: 'ch-target' }, svg);
        if (!mini) tx(svg, W - R, y(tgt) - 5, `Target ${tgt}`, { 'text-anchor': 'end', class: 'ch-lab' });
      }
      // the exam date
      if (examT) {
        const xe = xOf(examT);
        sv('line', { x1: r1(xe), x2: r1(xe), y1: T - (mini ? 0 : 4), y2: H - B, class: 'ch-exam' }, svg);
        if (!mini) tx(svg, xe - 4, H - 8, `SAT ${fdate(examT)}`, { 'text-anchor': 'end', class: 'ch-lab ch-sat' });
      }
      if (opts.now) {
        const xn = xOf(opts.now === true ? Date.now() : opts.now);
        sv('line', { x1: r1(xn), x2: r1(xn), y1: T, y2: H - B, class: 'ch-now' }, svg);
      }
      // the trend through our sittings' middles
      if (scored.length > 1) sv('polyline', { class: 'ch-trend', points: scored.map(p => `${r1(xs[pts.indexOf(p)])},${r1(y(p.mid))}`).join(' ') }, svg);
      // bands, middles, added scores
      pts.forEach((p, i) => {
        const x = xs[i], now = p === last;
        if (p.outside) {
          const s = mini ? 4 : 5.5, cy = y(p.mid);
          sv('path', { class: 'ch-dia', d: `M${r1(x)} ${r1(cy - s)} L${r1(x + s)} ${r1(cy)} L${r1(x)} ${r1(cy + s)} L${r1(x - s)} ${r1(cy)} Z`,
            'aria-label': `${pointName(p)} ${fband(p.low, p.high)}` }, svg);
          return;
        }
        const yt = y(p.high), yb = y(p.low);
        sv('rect', { class: `ch-band ${bandKind(p)}${now ? ' now' : ''}`, x: r1(x - bw / 2), width: r1(bw), y: r1(yt), height: r1(Math.max(3, yb - yt)), rx: r1(Math.min(bw / 2, 4)) }, svg);
        sv('circle', { class: 'ch-mid' + (now ? ' now' : ''), cx: r1(x), cy: r1(y(p.mid)), r: mini ? 3 : now ? 4.5 : 4 }, svg);
      });
      // twin brackets
      const byId = new Map(pts.map(p => [String(p.id), p]));
      let bi = 0;
      (opts.pairs || []).forEach(pr => {
        const [a, b] = Array.isArray(pr) ? pr : [pr.a ?? pr.from, pr.b ?? pr.to];
        const pa = byId.get(String(a)), pb = byId.get(String(b));
        if (!pa || !pb) return;
        const x1 = xs[pts.indexOf(pa)], x2 = xs[pts.indexOf(pb)];
        const yb = H - B - 3 - (bi++ % 3) * 4;
        sv('path', { class: 'ch-bracket', d: `M${r1(x1)} ${r1(yb - 5)} V${r1(yb)} H${r1(x2)} V${r1(yb - 5)}` }, svg);
      });
      // what happened between two sittings; the biggest gain is labelled once
      const gaps = (opts.gaps || []).map((g, k) => {
        const find = v => (isNum(v) && !byId.has(String(v)) ? scored[v] : byId.get(String(v)));
        const a = g.from !== undefined ? find(g.from) : scored[k], b = g.to !== undefined ? find(g.to) : scored[k + 1];
        return a && b && a !== b ? { ...g, a, b, text: gapText(g, a, b), delta: isNum(g.delta) ? g.delta : b.mid - a.mid } : null;
      }).filter(Boolean);
      const best = gaps.reduce((m, g) => (g.best || (!m || g.delta > m.delta) ? g : m), null);
      if (best && best.delta > 0 && !mini) {
        const xa = xs[pts.indexOf(best.a)], xb = xs[pts.indexOf(best.b)];
        const lab = best.short || `+${Math.round(best.delta)}`;
        if (xb - xa > textW(lab) + 8) tx(svg, (xa + xb) / 2, Math.max(T + 8, Math.min(y(best.a.high), y(best.b.high)) - 6), lab, { 'text-anchor': 'middle', class: 'ch-lab ch-gain' });
      }
      // x labels
      if (!mini) {
        const xl = sv('g', { class: 'ch-xl' }, svg);
        if (opts.x === 'time') {
          const t0 = toDate(opts.from ?? (pts[0] ? pts[0].at : Date.now())), t1 = toDate(opts.to ?? endT ?? lastT ?? Date.now());
          let m = new Date(t0.getFullYear(), t0.getMonth() + (t0.getDate() > 1 ? 1 : 0), 1, 12), lastX = -99;
          for (; m <= t1; m = new Date(m.getFullYear(), m.getMonth() + 1, 1, 12)) {
            const x = xOf(m);
            sv('line', { x1: r1(x), x2: r1(x), y1: H - B, y2: H - B + 4, class: 'ch-tick' }, xl);
            const satX = examT ? xOf(examT) : null, satW = examT ? textW(`SAT ${fdate(examT)}`, 11) + 8 : 0;
            const clash = satX !== null && x + 3 < satX && x + 30 > satX - satW;
            if (x - lastX > 34 && !clash && x + 24 < W) { tx(xl, x + 3, H - 8, MON[m.getMonth()], { class: 'ch-xtick' }); lastX = x; }
          }
        } else {
          const every = Math.max(1, Math.ceil(52 / slot));
          const days = pts.map(p => iso(p.at));
          pts.forEach((p, i) => {
            if ((pts.length - 1 - i) % every) return;
            const same = days.filter(d => d === days[i]).length > 1 && slot >= 72;
            if (examT && xs[i] > xOf(examT) - textW(`SAT ${fdate(examT)}`, 11) - 30 && xs[i] < xOf(examT)) return;
            tx(xl, xs[i], H - 8, same ? `${fdate(p.at)} ${hm(p.at)}` : fdate(p.at), { 'text-anchor': 'middle', class: 'ch-xtick' });
          });
        }
      }
      // R&W you entered: a hatched step line in its own 200-800 lane
      if (rw.length) {
        const y0 = H + 12, yR = v => y0 + 12 + (laneH - 22) * (1 - (clamp(v, 200, 800) - 200) / 600);
        sv('rect', { x: L, y: y0, width: plotW, height: laneH, rx: 6, class: 'ch-lane' }, svg);
        tx(svg, L + 6, y0 + 11, 'R&W (yours)', { class: 'ch-lab' });
        let d = '';
        rw.forEach((r, k) => {
          const x = xOf(r.at);
          d += k ? ` H${r1(x)} V${r1(yR(r.value))}` : `M${r1(x)} ${r1(yR(r.value))}`;
        });
        d += ` H${r1(Math.max(xOf(rw[rw.length - 1].at) + 8, xOf(rw[rw.length - 1].at)))}`;
        sv('path', { d, class: 'ch-rw', stroke: hatchFill }, svg);
        rw.forEach(r => sv('rect', { x: r1(xOf(r.at) - 3.5), y: r1(yR(r.value) - 3.5), width: 7, height: 7, rx: 1.5, class: 'ch-rw-pt' }, svg));
      }

      // summary
      const bestP = scored.reduce((m, p) => (!m || p.mid > m.mid ? p : m), null);
      const sumTxt = pts.length
        ? [`${opts.label || 'Score over time'}, ${scored.length} scored sitting${scored.length === 1 ? '' : 's'}${pts.length > scored.length ? ` and ${pts.length - scored.length} added score${pts.length - scored.length === 1 ? '' : 's'}` : ''} from ${fdate(pts[0].at)} to ${fdate(pts[pts.length - 1].at)}`,
          last && `latest ${fband(last.low, last.high)} (middle ${Math.round(last.mid)})`,
          bestP && scored.length > 1 && `best ${fband(bestP.low, bestP.high)}`,
          tgt !== null && `target ${tgt}`, est && `current estimate ${fband(est.low, est.high)}`, ...sumBits].filter(Boolean).join('; ') + '.'
        : `${opts.label || 'Score over time'}: no scored sittings yet.`;
      svg.setAttribute('aria-label', sumTxt);

      // empty: the frame, a ghost band and the action
      if (!pts.length) {
        const cx = L + 16, m = lo + (hi - lo) * .7, g = (hi - lo) / 12;   // clear of the centred note and its button
        sv('rect', { class: 'ch-ghost', x: r1(cx - 7), width: 14, y: r1(y(m + g)), height: r1(y(m - g) - y(m + g)), rx: 4 }, svg);
      }
      const oldSvg = plot.querySelector(':scope > svg');
      if (oldSvg) oldSvg.replaceWith(svg); else plot.prepend(svg);
      emptyNote(plot, pts.length ? null : (opts.empty || {}), 'Your first test puts a point here.');

      // controls: a point per sitting, a strip per gap
      const items = [];
      const sameDay = pts.map(p => pts.filter(q => iso(q.at) === iso(p.at)).length > 1);
      pts.forEach((p, i) => {
        const g = gaps.find(x => x.a === p);
        const hw = Math.min(22, Math.max(2, (g && slot >= 30 ? slot - 16 : slot) / 2));
        const tip = pointTip(p, sameDay[i]);
        items.push({
          _p: p, x: xs[i] - hw, y: T - 4, w: hw * 2, h: H - T - B + 4, label: tip, tip, action: 'Open report',
          pressed: opts.compare && comparing ? picked.includes(p) : undefined,
          pick: () => {
            if (comparing) {
              if (picked.includes(p)) picked = picked.filter(x => x !== p); else picked.push(p);
              if (picked.length === 2) {
                const [a, b] = [...picked].sort((u, v) => u.at - v.at);
                comparing = false; picked = [];
                footer();
                sz.redraw();
                opts.compare(b, a);
                return;
              }
              sz.redraw();
              return;
            }
            if (opts.onPick) opts.onPick(p);
            else if (p.href) location.href = p.href;
          },
        });
        if (g && slot >= 30) {
          const xa = xs[i], xb = xs[pts.indexOf(g.b)];
          if (xb > xa) items.push({ x: (xa + xb) / 2 - 7, y: T - 4, w: 14, h: H - T - B + 4, label: g.text, tip: g.text, cls: 'gap' });
        }
      });
      rw.forEach(r => {
        const t = `R&W ${r.value} · ${fdate(r.at)}${r.source ? ` · ${r.source}` : ''} · entered by you`;
        items.push({ x: xOf(r.at) - 12, y: H + 12, w: 24, h: laneH, label: t, tip: t });
      });
      hitLayer(plot, items, { label: 'Sittings', start: Math.max(0, items.findIndex(it => it._p && it._p === last)) });

      // the hidden table
      const rows = pts.map((p, i) => [sameDay[i] ? `${fdate(p.at)} ${hm(p.at)}` : fdate(p.at), pointName(p), fband(p.low, p.high),
        p.outside ? '' : Math.round(p.mid), p.detail || (isNum(p.right) && isNum(p.asked) ? `${p.right}/${p.asked}` : '')]);
      if (tgt !== null) rows.push(['Target', '', tgt, '', '']);
      if (est) rows.push(['Estimate', '', fband(est.low, est.high), Math.round((+est.low + +est.high) / 2), '']);
      if (proj) rows.push(['Projected', proj.to || examT ? fdate(proj.to || examT) : '', fband(proj.low, proj.high), Math.round(isNum(+proj.mid) ? +proj.mid : (+proj.low + +proj.high) / 2), proj.label || 'if this pace held']);
      if (pace) {
        rows.push(['Pace', `${fdate(pace.from.day)} → ${fdate(pace.to.day)}`, `${pace.from.value} → ${pace.to.value}`, '', 'the plan’s line']);
        (pace.aims || []).forEach(a => rows.push(['Checkpoint', fdate(a.day), `aim ${a.value}`, '', a.beaten ? 'beaten' : '']));
      }
      if (examT) rows.push(['SAT', fdate(examT), '', '', '']);
      gaps.forEach(g => rows.push(['Between', `${fdate(g.a.at)} → ${fdate(g.b.at)}`, '', '', g.text]));
      rw.forEach(r => rows.push(['R&W (yours)', fdate(r.at), r.value, '', r.source || 'entered by you']));
      setTable(el, dataTable(sumTxt, ['Date', 'Sitting', 'Band', 'Middle', 'Detail'], rows));

      footer(pts, { tgt, est, proj, pace, rw, examT, mini, scored });
    }

    let lastFoot = null;
    function footer(pts, f) {
      if (pts) lastFoot = { pts, f }; else if (lastFoot) ({ pts, f } = lastFoot); else return;
      foot.replaceChildren();
      if (opts.projection === null) foot.append(h('p', { class: 'chart-note', text: opts.noProjection || 'Three modules over three weeks start a projection.' }));
      if (opts.legend === false || f.mini || !pts.length) return;
      const k = x => pts.filter(p => bandKind(p) === x).length;
      const items = [
        k('sec') && { key: 'band', label: 'Section', n: k('sec') }, k('mod') && { key: 'mod', label: 'Module', n: k('mod') },
        k('diag') && { key: 'diag', label: 'Diagnostic', n: k('diag') }, f.scored.length && { key: 'now', label: 'Newest' },
        k('dia') && { key: 'diamond', label: 'A score you added', n: k('dia') },
        f.scored.length > 1 && { key: 'line', label: 'Trend of the middles' },
        f.tgt !== null && { key: 'target', label: `Target ${f.tgt}` }, f.est && { key: 'zone', label: 'Current estimate' },
        f.proj && { key: 'cone', label: f.proj.label || `If this pace held: ${fband(f.proj.low, f.proj.high)}${f.proj.to || f.examT ? ` on ${fdate(f.proj.to || f.examT)}` : ''}` }, f.pace && { key: 'pace', label: 'Plan pace' },
        (opts.pairs || []).length && { key: 'bracket', label: 'Twin pair' }, f.rw.length && { key: 'rw', label: 'R&W you entered', n: f.rw.length },
      ];
      const key = chartKey(items);
      foot.append(key);
      if (opts.compare && f.scored.length > 1) {
        const b = h('button', { type: 'button', class: 'quiet sm chart-compare', 'aria-pressed': String(comparing) },
          comparing ? (picked.length ? 'Pick one more' : 'Pick two points') : 'Compare two');
        b.addEventListener('click', () => { comparing = !comparing; picked = []; footer(); sz.redraw(); });
        foot.append(b);
      }
    }

    const sz = sized(plot, draw);
    function set(p, o2) {
      if (o2) Object.assign(opts, o2);
      if (p) all = p.map(normPoint).filter(x => isNum(x.low)).sort((a, b) => a.at - b.at);
      buildCtl();
      sz.redraw();
    }
    set(points || []);
    return { el, set, update: set };
  }

  /* ============================================================ UI.gauge */
  function gauge(host, o = {}) {
    const el = h('figure', { class: 'chart gauge' + (o.className ? ' ' + o.className : '') });
    const plot = h('div', { class: 'chart-plot gauge-plot' });
    const big = h('span', { class: 'gauge-v' }), sub = h('span', { class: 'gauge-s' });
    plot.append(h('div', { class: 'gauge-c', 'aria-hidden': 'true' }, big, sub));
    const key = h('div', { class: 'gauge-key' }), cap = h('figcaption', { class: 'chart-note' });
    el.append(plot, key, cap);
    put(host, el);
    const opts = { ...o };
    const CX = 130, CY = 124, RR = 98, SW = 16;
    let refs = null;
    const lo = () => opts.min ?? 200, hi = () => opts.max ?? 800;
    const ang = v => -120 + 240 * (clamp(v, lo(), hi()) - lo()) / (hi() - lo());
    const pt = (a, r) => [r1(CX + r * Math.sin(a * Math.PI / 180)), r1(CY - r * Math.cos(a * Math.PI / 180))];
    function sector(l, u, r0 = RR - SW / 2, r2 = RR + SW / 2) {
      let a0 = ang(Math.min(l, u)), a1 = ang(Math.max(l, u));
      if (a1 - a0 < 1.6) { const m = (a0 + a1) / 2; a0 = m - .8; a1 = m + .8; }
      const lg = a1 - a0 > 180 ? 1 : 0;
      const [x0, y0] = pt(a0, r2), [x1, y1] = pt(a1, r2), [x2, y2] = pt(a1, r0), [x3, y3] = pt(a0, r0);
      return `M${x0} ${y0} A${r2} ${r2} 0 ${lg} 1 ${x1} ${y1} L${x2} ${y2} A${r0} ${r0} 0 ${lg} 0 ${x3} ${y3} Z`;
    }
    const radial = (v, r0, r2) => { const [x0, y0] = pt(ang(v), r0), [x1, y1] = pt(ang(v), r2); return `M${x0} ${y0} L${x1} ${y1}`; };
    const okBand = b => b && isNum(+b.low) && isNum(+(b.high ?? b.low));
    const bOf = b => ({ low: +b.low, high: +(b.high ?? b.low) });
    const subject = () => (UI.SUBJECT && UI.SUBJECT[opts.subject || 'math'] ? UI.SUBJECT[opts.subject || 'math'].label : 'Math');

    function render() {
      const band = okBand(opts.band) ? bOf(opts.band) : null;
      const prev = okBand(opts.previous) ? bOf(opts.previous) : null;
      const whatif = okBand(opts.whatif) ? bOf(opts.whatif) : null;
      const todayB = !whatif && okBand(opts.today) ? bOf(opts.today) : null;
      const second = okBand(opts.second) ? bOf(opts.second) : null;
      const tgt = isNum(+opts.target) && opts.target !== null && opts.target !== '' ? +opts.target : null;
      const svg = svgRoot(260, 196, '');
      svg.setAttribute('viewBox', '-32 -8 324 214');
      svg.removeAttribute('width'); svg.removeAttribute('height');
      // 1. the scale and its ticks
      const [sx, sy] = pt(-120, RR), [ex, ey] = pt(120, RR);
      sv('path', { class: 'g-track', d: `M${sx} ${sy} A${RR} ${RR} 0 1 1 ${ex} ${ey}` }, svg);
      const ticks = [];
      for (let v = lo(); v <= hi(); v += (hi() - lo()) / 3) ticks.push(Math.round(v));
      ticks.forEach(v => {
        sv('path', { class: 'g-tick', d: radial(v, RR + SW / 2 + 2, RR + SW / 2 + 6) }, svg);
        if (tgt !== null && Math.abs(ang(v) - ang(tgt)) < 14) return;
        const [lx, ly] = pt(ang(v), RR + SW / 2 + 22);
        tx(svg, lx, ly + 4, v, { 'text-anchor': 'middle', class: 'g-lab' });
      });
      // 2. the previous same-kind band, a ghost
      if (prev) sv('path', { class: 'g-prev', d: sector(prev.low, prev.high) }, svg);
      // 3-5. today (dotted), with a second look (hollow), what if (dashed)
      if (todayB) sv('path', { class: 'g-out dotted', d: sector(todayB.low, todayB.high, RR - SW / 2 - 3, RR + SW / 2 + 3) }, svg);
      if (second) sv('path', { class: 'g-out', d: sector(second.low, second.high, RR - SW / 2 - 3, RR + SW / 2 + 3) }, svg);
      if (whatif) sv('path', { class: 'g-out dashed', d: sector(whatif.low, whatif.high, RR - SW / 2 - 3, RR + SW / 2 + 3) }, svg);
      // 6. this sitting, with its middle
      const bandP = sv('path', { class: 'g-band', d: band ? sector(band.low, band.high) : '' }, svg);
      const midP = sv('path', { class: 'g-mid', d: band ? radial((band.low + band.high) / 2, RR - SW / 2 - 3, RR + SW / 2 + 3) : '' }, svg);
      // 7. the target
      if (tgt !== null) {
        sv('path', { class: 'g-target', d: radial(tgt, RR - SW / 2 - 6, RR + SW / 2 + 8) }, svg);
        const a = ang(tgt), [lx, ly] = pt(a, RR + SW / 2 + 22);
        const anchor = a < -30 ? 'end' : a > 30 ? 'start' : 'middle';
        if (anchor === 'middle') tx(svg, lx, ly + 4, `Target ${tgt}`, { 'text-anchor': anchor, class: 'g-lab g-tl' });
        else {
          const t = tx(svg, lx, ly - 3, 'Target', { 'text-anchor': anchor, class: 'g-lab g-tl' });
          const t2 = sv('tspan', { x: lx, dy: 13 }, t);
          t2.textContent = String(tgt);
        }
      }
      const old = plot.querySelector(':scope > svg');
      if (old) old.replaceWith(svg); else plot.prepend(svg);
      refs = { bandP, midP };

      const prevName = (opts.previous && opts.previous.label) || 'Previous';
      const mid = band ? Math.round((band.low + band.high) / 2) : null;
      const summary = [`${subject()} score gauge, ${lo()} to ${hi()}`,
        band ? `this sitting ${fband(band.low, band.high)}, middle ${mid}` : 'no score yet',
        prev && `${prevName} ${fband(prev.low, prev.high)}`, todayB && `today about ${fband(todayB.low, todayB.high)}`,
        second && `with a second look ${fband(second.low, second.high)}`, whatif && `what if ${fband(whatif.low, whatif.high)}`,
        tgt !== null && `target ${tgt}`].filter(Boolean).join('; ') + '.';
      svg.setAttribute('aria-label', summary);
      sub.textContent = opts.sub ?? (band ? `${subject()} · middle ${mid}` : 'No score yet');
      key.replaceChildren(chartKey([
        band && { swatch: gSw('g-band'), label: 'This sitting', n: fband(band.low, band.high) },
        prev && { swatch: gSw('g-prev'), label: prevName, n: fband(prev.low, prev.high) },
        second && { swatch: gSw('g-out'), label: 'With a second look', n: fband(second.low, second.high) },
        todayB && { swatch: gSw('g-out dotted'), label: 'Today ≈', n: fband(todayB.low, todayB.high) },
        whatif && { swatch: gSw('g-out dashed'), label: 'What if', n: fband(whatif.low, whatif.high) },
        tgt !== null && { swatch: gSw('g-target', true), label: 'Target', n: String(tgt) },
      ]));
      cap.textContent = opts.caption || '';
      cap.hidden = !opts.caption;
      setTable(el, dataTable(summary, ['Layer', 'Low', 'High', 'Middle'], [
        band && ['This sitting', band.low, band.high, mid], prev && [prevName, prev.low, prev.high, Math.round((prev.low + prev.high) / 2)],
        todayB && ['Today', todayB.low, todayB.high, Math.round((todayB.low + todayB.high) / 2)],
        second && ['With a second look', second.low, second.high, Math.round((second.low + second.high) / 2)],
        whatif && ['What if', whatif.low, whatif.high, Math.round((whatif.low + whatif.high) / 2)],
        tgt !== null && ['Target', tgt, tgt, tgt]].filter(Boolean)));
      return { band, prev };
    }
    function gSw(cls, tick) {
      const s = sv('svg', { class: 'ch-key', width: 18, height: 12, viewBox: '0 0 18 12', 'aria-hidden': 'true', focusable: 'false' });
      if (tick) sv('path', { d: 'M9 0 V12', class: cls }, s);
      else sv('rect', { x: 1.5, y: 2, width: 15, height: 8, rx: 2, class: cls }, s);
      return s;
    }
    function paint(l, u) {
      big.textContent = fband(Math.round(l / 10) * 10, Math.round(u / 10) * 10);
      if (!refs) return;
      refs.bandP.setAttribute('d', sector(l, u));
      refs.midP.setAttribute('d', radial((l + u) / 2, RR - SW / 2 - 3, RR + SW / 2 + 3));
    }
    function show(animate) {
      const { band, prev } = render();
      if (!band) { big.textContent = '—'; return; }
      el.removeAttribute('data-animate');
      if (!animate || still()) { big.textContent = fband(band.low, band.high); return; }
      el.setAttribute('data-animate', '');
      const from = prev || { low: lo(), high: lo() }, t0 = performance.now();
      const step = t => {
        const k = Math.min(1, (t - t0) / 1200), e = 1 - Math.pow(1 - k, 3);
        paint(from.low + (band.low - from.low) * e, from.high + (band.high - from.high) * e);
        if (k < 1) requestAnimationFrame(step); else big.textContent = fband(band.low, band.high);
      };
      paint(from.low, from.high);
      requestAnimationFrame(step);
    }
    show(!!opts.animate);
    return { el, set(o2 = {}) { Object.assign(opts, o2); show(!!o2.animate); } };
  }

  /* ============================================================ UI.scale */
  function scale(host, o = {}) {
    const el = h('figure', { class: 'chart scale' + (o.compact ? ' sm' : '') + (o.className ? ' ' + o.className : '') });
    put(host, el);
    const opts = { ...o };
    function draw(animate) {
      const lo = opts.min ?? 200, hi = opts.max ?? 800;
      const at = v => (clamp(+v, lo, hi) - lo) / (hi - lo) * 100;
      const okB = b => b && isNum(+b.low);
      const band = okB(opts.band) ? { low: +opts.band.low, high: +(opts.band.high ?? opts.band.low) } : null;
      const prev = okB(opts.previous) ? { low: +opts.previous.low, high: +(opts.previous.high ?? opts.previous.low) } : null;
      const est = isNum(+opts.estimate) && opts.estimate !== null && opts.estimate !== '' ? +opts.estimate : okB(opts.estimate) ? (+opts.estimate.low + +(opts.estimate.high ?? opts.estimate.low)) / 2 : null;
      const tgt = isNum(+opts.target) && opts.target !== null && opts.target !== '' ? +opts.target : null;
      const start = isNum(+opts.start) && opts.start !== null && opts.start !== '' ? +opts.start : null;
      const ticks = (opts.ticks || []).filter(t => isNum(+t.value));
      const dot = isNum(+opts.dot) && opts.dot !== null && opts.dot !== '' ? +opts.dot : null;

      const vis = h('div', { class: 'scale-vis', role: 'img' });
      // the distribution strip over the track (X20): ranked midpoints, the average, your band, your target
      const hist = opts.hist && (Array.isArray(opts.hist) ? { counts: opts.hist } : opts.hist);
      if (hist && hist.counts && hist.counts.length) {
        const hs = sv('svg', { class: 'scale-hist', viewBox: '0 0 100 32', preserveAspectRatio: 'none', 'aria-hidden': 'true' });
        const hlo = hist.min ?? lo, bin = hist.bin ?? (hi - lo) / hist.counts.length, mx = Math.max(1, ...hist.counts);
        if (band) sv('rect', { x: at(band.low), width: Math.max(.6, at(band.high) - at(band.low)), y: 0, height: 32, class: 'sh-band' }, hs);
        hist.counts.forEach((c, i) => {
          const x0 = at(hlo + i * bin), x1 = at(hlo + (i + 1) * bin), hh = c ? Math.max(1.5, c / mx * 30) : 0;
          if (hh) sv('rect', { x: r1(x0 + .15), width: r1(Math.max(.2, x1 - x0 - .3)), y: r1(32 - hh), height: r1(hh), class: 'sh-bar' }, hs);
        });
        if (isNum(+hist.avg)) sv('rect', { x: at(hist.avg) - .25, width: .5, y: 0, height: 32, class: 'sh-avg' }, hs);
        if (tgt !== null) sv('rect', { x: at(tgt) - .3, width: .6, y: 0, height: 32, class: 'sh-target' }, hs);
        vis.append(hs);
      }
      const topRow = h('div', { class: 'scale-row top' });
      const track = h('div', { class: 'scale-track' });
      const botRow = h('div', { class: 'scale-row bot' });
      const lab = (row, v, text, cls) => row.append(h('span', { class: 'scale-l' + (cls ? ' ' + cls : '') + (at(v) < 6 ? ' l' : at(v) > 94 ? ' r' : ''), style: `left:${r1(at(v))}%`, text }));
      if (prev) track.append(h('i', { class: 'scale-prev', style: `left:${r1(at(prev.low))}%;width:${r1(Math.max(.8, at(prev.high) - at(prev.low)))}%` }));
      if (band) {
        const b = h('i', { class: 'scale-band', style: `left:${r1(at(band.low))}%;width:${r1(Math.max(.8, at(band.high) - at(band.low)))}%` }, h('b'));
        if (animate && !still()) b.classList.add('grow');
        track.append(b);
      } else if (est !== null) track.append(h('i', { class: 'scale-est', style: `left:${r1(at(est))}%` }));
      if (start !== null) { track.append(h('i', { class: 'scale-tick start', style: `left:${r1(at(start))}%` })); lab(botRow, start, `Start ${fnum(start)}`, 'start'); }
      ticks.forEach(t => { track.append(h('i', { class: 'scale-tick', style: `left:${r1(at(t.value))}%` })); lab(botRow, t.value, t.label ?? String(t.value)); });
      if (dot !== null) track.append(h('i', { class: 'scale-dot', style: `left:${r1(at(dot))}%` }));
      if (tgt !== null) { track.append(h('i', { class: 'scale-tick target', style: `left:${r1(at(tgt))}%` })); lab(topRow, tgt, opts.targetLabel ?? fnum(tgt), 'target'); }
      if (hist && isNum(+hist.avg)) lab(topRow, hist.avg, `avg ${Math.round(hist.avg)}`, 'avg');
      let bandLab = null;
      if (band && opts.label) { bandLab = h('span', { class: 'scale-l band', style: `left:${r1(at((band.low + band.high) / 2))}%`, text: fband(band.low, band.high) }); topRow.append(bandLab); }
      // the ends, unless a tick label sits on them
      const near = v => [start, tgt, ...ticks.map(t => +t.value)].some(x => x !== null && Math.abs(at(x) - at(v)) < 9);
      if (!near(lo)) botRow.append(h('span', { class: 'scale-l end lo', text: fnum(lo) }));
      if (!near(hi)) botRow.append(h('span', { class: 'scale-l end hi', text: fnum(hi) }));
      vis.append(topRow, track, botRow);
      unclash = () => {
        // the band's numbers win the top row; a target that would touch them drops under the track, the average hides
        const tl = topRow.querySelector('.target');
        if (tl && tl.parentNode !== topRow) topRow.append(tl);
        topRow.querySelectorAll('.scale-l').forEach(e => { e.hidden = false; });
        const rs = [...topRow.querySelectorAll('.scale-l.band')].map(e => e.getBoundingClientRect());
        for (const e of [tl, topRow.querySelector('.avg')]) {
          if (!e) continue;
          const r = e.getBoundingClientRect();
          if (!r.width) return;
          if (rs.some(p => r.left < p.right + 8 && r.right > p.left - 8)) { if (e === tl) botRow.append(e); else e.hidden = true; }
          else rs.push(r);
        }
      };
      const summary = [`Scale ${fnum(lo)} to ${fnum(hi)}`, band && `${opts.bandLabel || 'band'} ${fband(band.low, band.high)}`, !band && est !== null && `estimate ${fnum(est)}`,
        prev && `previous ${fband(prev.low, prev.high)}`, tgt !== null && `target ${fnum(tgt)}`, start !== null && `plan start ${fnum(start)}`,
        dot !== null && `now ${fnum(dot)}`, ...ticks.map(t => `${t.label || 'mark'} ${fnum(t.value)}`),
        hist && `${plural(sum(hist.counts), 'ranked sitting')}${isNum(+hist.avg) ? `, average ${fnum(hist.avg)}` : ''}`].filter(Boolean).join('; ') + '.';
      vis.setAttribute('aria-label', summary);
      el.replaceChildren(vis);
      unclash();
      el.append(dataTable(summary, ['Mark', 'Value'], [
        band && [opts.bandLabel || 'Band', fband(band.low, band.high)], !band && est !== null && ['Estimate', Math.round(est)],
        prev && ['Previous', fband(prev.low, prev.high)], tgt !== null && ['Target', tgt], start !== null && ['Plan start', start],
        dot !== null && ['Now', dot], ...ticks.map(t => [t.label || 'Mark', t.value]),
        ...(hist ? hist.counts.map((c, i) => { const b0 = (hist.min ?? lo) + i * (hist.bin ?? (hi - lo) / hist.counts.length); return [`${Math.round(b0)}–${Math.round(b0 + (hist.bin ?? (hi - lo) / hist.counts.length)) - 1}`, c]; }) : []),
      ].filter(Boolean)));
      // the band's numbers count up once
      if (bandLab && animate && !still()) {
        const from = prev || { low: lo, high: lo }, t0 = performance.now();
        const step = t => {
          const k = Math.min(1, (t - t0) / 600), e = 1 - Math.pow(1 - k, 3);
          bandLab.textContent = fband(Math.round((from.low + (band.low - from.low) * e) / 10) * 10, Math.round((from.high + (band.high - from.high) * e) / 10) * 10);
          if (k < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }
    }
    let unclash = () => {};
    draw(!!opts.animate);
    if (window.ResizeObserver) new ResizeObserver(() => unclash()).observe(el);
    return { el, set(o2 = {}) { Object.assign(opts, o2); draw(!!o2.animate); } };
  }

  /* ============================================================ UI.barChart */
  function barChart(host, rows, o = {}) {
    const { el, plot } = frame(host, 'bar-chart', o);
    const opts = { ...o };
    let data = [];
    const foot = h('div', { class: 'chart-foot' });
    el.append(foot);
    const fmt = v => {
      if (opts.format) return opts.format(v);
      if (opts.unit === 'min') return fmin(v);
      if (opts.unit === 's') return fmmss(v);
      if (opts.unit === '%') return `${Math.round(v)}%`;
      return fnum(v) + (opts.unit && opts.unit !== 'q' ? ` ${opts.unit}` : '');
    };
    const rowKey = (r, i) => r.key ?? r.day ?? r.label ?? i;
    const val = (r, k) => n0(r[k] ?? (r.parts && r.parts[k]) ?? (r.down && r.down[k]));
    const seriesOf = () => opts.series || (data.some(r => r.parts) ? [...new Set(data.flatMap(r => Object.keys(r.parts || {})))].map(k => ({ key: k, label: k })) : [{ key: 'value', label: opts.valueLabel || opts.label || 'Value', look: opts.look }]);
    const rowName = r => (r.day ? flong(r.day) : String(r.label ?? r.key ?? ''));

    function draw(W) {
      const S = seriesOf(), D = opts.down || [];
      const n = data.length;
      const stacked = opts.stacked || opts.norm || D.length > 0 || S.length === 1;
      const H = opts.height ?? (phone() ? 140 : 160);
      const mini = H < 90;
      const R = mini ? 2 : 8, T = mini ? 4 : 14, B = mini ? (opts.labels === false ? 4 : 14) : 20;
      let L = mini ? 2 : 36;
      const upOf = r => (stacked ? sum(S.map(s => val(r, s.key))) : Math.max(0, ...S.map(s => val(r, s.key))));
      const downOf = r => sum(D.map(s => val(r, s.key)));
      const pace = opts.pace === undefined || opts.pace === null ? null : typeof opts.pace === 'object' ? opts.pace : { value: +opts.pace };
      const lineK = opts.line ? (typeof opts.line === 'string' ? { key: opts.line, label: opts.line } : opts.line) : null;
      let maxUp = opts.norm ? 100 : Math.max(0, ...data.map(upOf), ...data.map(r => n0(r.planned)), ...data.map(r => n0(r.budget)),
        ...(lineK ? data.map(r => n0(r[lineK.key])) : []), pace ? pace.value : 0);
      const maxDn = Math.max(0, ...data.map(downOf));
      maxUp = opts.max ?? (opts.norm ? 100 : niceMax(maxUp || (maxDn ? 0 : 1)));
      const dn = maxDn ? niceMax(maxDn) : 0;
      const span = (maxUp || 0) + dn || 1;
      const y0 = T + (H - T - B) * (maxUp / span);
      const yv = v => y0 - (H - T - B) * (v / span);
      const ticks = opts.norm ? [0, 50, 100] : [0, maxUp / 2, maxUp];
      const tickText = v => (opts.norm ? `${v}%` : fmt(v));
      if (!mini) L = Math.max(L, 10 + Math.max(0, ...ticks.filter(Boolean).map(v => textW(tickText(v), 10.5)), dn ? textW(fmt(dn), 10.5) : 0));
      const plotW = W - L - R;
      const slot = plotW / Math.max(n, 1);
      const k = stacked ? 1 : S.length;
      const bw = Math.max(2, Math.min(24, (slot - 2) * (stacked ? .64 : .8) / k));
      const svg = svgRoot(W, H, '');
      const hf = hatch(svg);
      const grid = sv('g', { class: 'ch-grid' }, svg);
      if (!mini) {
        ticks.forEach(v => {
          sv('line', { x1: L, x2: W - R, y1: r1(yv(v)), y2: r1(yv(v)) }, grid);
          if (v) tx(grid, L - 6, yv(v) + 3.5, tickText(v), { 'text-anchor': 'end', class: 'ch-ytick' });
        });
        if (dn) { sv('line', { x1: L, x2: W - R, y1: r1(yv(-dn)), y2: r1(yv(-dn)) }, grid); tx(grid, L - 6, yv(-dn) + 3.5, fmt(dn), { 'text-anchor': 'end', class: 'ch-ytick' }); }
      }
      sv('line', { x1: L, x2: W - R, y1: r1(y0), y2: r1(y0), class: 'ch-base' }, svg);
      const look = (s, r) => (r && r.status ? null : r && r.today && opts.today === 'amber' ? 'amber' : s.look || (S.length === 1 && !D.length ? 'ink' : null));
      const LOOKS = ['ink', 'soft', 'hatch', 'mat'];
      const lookOf = (s, i, r) => look(s, r) || LOOKS[i % LOOKS.length];
      const cls = l => `ch-bar ch-f-${l}`;
      const cx = i => L + slot * (i + .5);
      data.forEach((r, i) => {
        const x = cx(i);
        const tot = upOf(r), dt = downOf(r);
        if (opts.planned !== false && isNum(+r.planned) && r.planned > 0) {
          const pw = stacked ? bw : bw * k;
          sv('path', { class: 'ch-plan', d: barPath(x - pw / 2, y0, yv(opts.norm ? 100 : r.planned), pw, true) }, svg);
        }
        if (!tot && !dt) sv('line', { x1: r1(x - bw / 2), x2: r1(x + bw / 2), y1: r1(y0), y2: r1(y0), class: 'ch-zero' }, svg);
        if (stacked) {
          let acc = 0;
          const parts = S.map((s, j) => [s, j, val(r, s.key)]).filter(p => p[2] > 0);
          parts.forEach(([s, j, v], m) => {
            const a = opts.norm && tot ? acc / tot * 100 : acc, b = opts.norm && tot ? (acc + v) / tot * 100 : acc + v;
            const top = m === parts.length - 1;
            const ya = yv(a) - (m ? 1 : 0), yb = yv(b) + (top ? 0 : 1);
            if (ya - yb > .5) {
              const l = lookOf(s, j, r);
              const e = sv('path', { class: r.status ? 'ch-bar ch-st' : cls(l), d: barPath(x - bw / 2, ya, yb, bw, top), 'data-status': r.status || null }, svg);
              if (l === 'hatch' && !r.status) e.setAttribute('fill', hf);
            }
            acc += v;
          });
        } else {
          S.forEach((s, j) => {
            const v = val(r, s.key);
            if (!v) return;
            const bx = x - (bw * k) / 2 + bw * j + (j ? 1 : 0);
            const l = lookOf(s, j, r);
            const e = sv('path', { class: cls(l), d: barPath(bx, y0, yv(v), bw - (j ? 1 : 0), true) }, svg);
            if (l === 'hatch') e.setAttribute('fill', hf);
          });
        }
        let acc = 0;
        const dparts = D.map((s, j) => [s, j, val(r, s.key)]).filter(p => p[2] > 0);
        dparts.forEach(([s, j, v], m) => {
          const bot = m === dparts.length - 1;
          const ya = yv(-acc) + (m ? 1 : 0), yb = yv(-(acc + v)) - (bot ? 0 : 1);
          if (yb - ya > .5) {
            const l = s.look || ['ink', 'hatch', 'soft'][j % 3];
            const e = sv('path', { class: cls(l), d: barPath(x - bw / 2, ya, yb, bw, bot) }, svg);
            if (l === 'hatch') e.setAttribute('fill', hf);
          }
          acc += v;
        });
        if (isNum(+r.budget) && r.budget > 0) sv('line', { x1: r1(x - bw / 2 - 1), x2: r1(x + bw / 2 + 1), y1: r1(yv(r.budget)), y2: r1(yv(r.budget)), class: 'ch-budget' }, svg);
        if (r.today && opts.today !== 'amber') {
          const yt = Math.min(yv(Math.max(opts.norm && tot ? 100 : tot, n0(r.planned))), y0 - 4) - 3, yb = (dt ? yv(-dt) : y0) + 3;
          sv('rect', { class: 'ch-today', x: r1(x - (stacked ? bw : bw * k) / 2 - 3), width: r1((stacked ? bw : bw * k) + 6), y: r1(yt), height: r1(yb - yt), rx: 5 }, svg);
        }
        if (r.status && !mini && slot >= 11) tx(svg, x, yv(tot) - 3, glyphOf(r.status), { 'text-anchor': 'middle', class: 'ch-glyph' });
        if (r.exam) { sv('line', { x1: r1(x), x2: r1(x), y1: T - 4, y2: y0, class: 'ch-exam' }, svg); tx(svg, x, T - 5 < 8 ? 8 : T - 5, 'SAT', { 'text-anchor': 'middle', class: 'ch-lab' }); }
      });
      if (lineK) {
        const pts = data.map((r, i) => (isNum(+r[lineK.key]) && r[lineK.key] !== null ? [cx(i), yv(+r[lineK.key])] : null)).filter(Boolean);
        if (pts.length > 1) sv('polyline', { class: 'ch-line', points: pts.map(p => p.map(r1).join(',')).join(' ') }, svg);
        pts.forEach(([x, yy]) => sv('circle', { cx: r1(x), cy: r1(yy), r: 3.5, class: 'ch-dot thin' }, svg));
      }
      const paceLab = pace && (pace.label || `Pace ${fmt(pace.value)}`);
      if (pace && isNum(pace.value)) {
        const yp = yv(pace.value);
        sv('line', { x1: L, x2: W - R, y1: r1(yp), y2: r1(yp), class: 'ch-pace' }, svg);
        const bars = data.map((r, i) => [cx(i) - slot / 2 + 1, Math.min(yv(Math.max(opts.norm && upOf(r) ? 100 : upOf(r), n0(r.planned))), y0) - 4, cx(i) + slot / 2 - 1, y0 + (downOf(r) ? yv(-downOf(r)) - y0 : 0)]);
        const at = mini ? null : clearOf([[W - R, yp - 4, 'end'], [W - R, yp + 13, 'end'], [L + 4, yp - 4, 'start'], [L + 4, yp + 13, 'start']].filter(([, y]) => y > 10 && y < H - B), paceLab, bars);
        if (at) tx(svg, at[0], at[1], paceLab, { 'text-anchor': at[2], class: 'ch-lab' });
      }
      // x labels
      if (opts.labels !== false && B > 8) {
        const lf = typeof opts.labels === 'function' ? opts.labels
          : opts.labels === 'weekday' || (!opts.labels && data.every(r => r.day) && n <= 14) ? r => (r.day ? DOW[toDate(r.day).getDay()][0] : '')
          : opts.labels === 'date' || (!opts.labels && data.every(r => r.day)) ? r => fdate(r.day) : r => String(r.label ?? r.key ?? '');
        const every = Math.max(1, Math.ceil(Math.max(...data.map(r => textW(lf(r), 10.5)), 8) / (slot - 2)));
        data.forEach((r, i) => {
          if ((n - 1 - i) % every) return;
          tx(svg, cx(i), H - (mini ? 3 : 6), lf(r), { 'text-anchor': 'middle', class: 'ch-xtick' + (r.today ? ' on' : '') });
        });
      }
      const total = sum(data.map(upOf));
      const maxR = data.reduce((m, r) => (!m || upOf(r) > upOf(m) ? r : m), null);
      const summary = n ? [`${opts.label || 'Bar chart'}, ${plural(n, 'bar')}`, S.length === 1 && !opts.norm && `total ${fmt(total)}`,
        maxR && upOf(maxR) > 0 && !opts.norm && `highest ${rowName(maxR)} at ${fmt(upOf(maxR))}`,
        S.length > 1 && S.map(s => `${s.label} ${fmt(sum(data.map(r => val(r, s.key))))}`).join(', '),
        D.length && D.map(s => `${s.label} ${fmt(sum(data.map(r => val(r, s.key))))}`).join(', '),
        pace && `reference line ${pace.label || fmt(pace.value)}`].filter(Boolean).join('; ') + '.' : `${opts.label || 'Bar chart'}: nothing yet.`;
      svg.setAttribute('aria-label', summary);
      const old = plot.querySelector(':scope > svg');
      if (old) old.replaceWith(svg); else plot.prepend(svg);
      emptyNote(plot, n ? null : (opts.empty || {}), 'Nothing logged yet');

      const hasPlan = r => opts.planned !== false && isNum(+r.planned) && r.planned > 0;
      const tipOf = r => r.tip || [rowName(r),
        S.length === 1 ? (hasPlan(r) ? `${fmt(upOf(r))} of ${fmt(r.planned)}` : opts.noun ? `${fmt(upOf(r))} ${opts.noun}` : fmt(upOf(r))) : S.map(s => `${s.label} ${fmt(val(r, s.key))}`).join(' · '),
        S.length > 1 && hasPlan(r) && `planned ${fmt(r.planned)}`,
        ...D.map(s => `${s.label} ${fmt(val(r, s.key))}`), lineK && isNum(+r[lineK.key]) && `${lineK.label} ${fmt(r[lineK.key])}`,
        isNum(+r.budget) && r.budget > 0 && `budget ${fmt(r.budget)}`, r.status && labelOf(r.status), r.sub].filter(Boolean).join(' · ');
      hitLayer(plot, data.map((r, i) => ({
        x: L + slot * i, y: T - 4, w: slot, h: H - T - (mini ? 0 : B) + 4, label: tipOf(r), tip: tipOf(r), action: opts.action || 'Open',
        pick: opts.onPick ? () => opts.onPick(r, i) : r.href ? () => { location.href = r.href; } : null,
      })), { label: opts.label || 'Bars', start: Math.max(0, data.findIndex(r => r.today)) });

      const head = [opts.rowLabel || (data.every(r => r.day) ? 'Day' : 'Item'), ...S.map(s => s.label), ...D.map(s => s.label),
        ...(data.some(r => isNum(+r.planned) && r.planned > 0) ? ['Planned'] : []), ...(lineK ? [lineK.label] : []),
        ...(data.some(r => isNum(+r.budget)) ? ['Budget'] : []), ...(data.some(r => r.status) ? ['Status'] : [])];
      setTable(el, dataTable(summary, head, data.map(r => [rowName(r), ...S.map(s => fmt(val(r, s.key))), ...D.map(s => fmt(val(r, s.key))),
        ...(data.some(x => isNum(+x.planned) && x.planned > 0) ? [isNum(+r.planned) ? fmt(r.planned) : ''] : []), ...(lineK ? [isNum(+r[lineK.key]) ? fmt(r[lineK.key]) : ''] : []),
        ...(data.some(x => isNum(+x.budget)) ? [isNum(+r.budget) ? fmt(r.budget) : ''] : []), ...(data.some(x => x.status) ? [labelOf(r.status)] : [])])));

      foot.replaceChildren();
      const keyItems = [
        ...(S.length > 1 || D.length || opts.planned || lineK ? S.map((s, j) => ({ key: `bar-${lookOf(s, j)}`, label: s.label, n: fmt(sum(data.map(r => val(r, s.key)))) })) : []),
        ...D.map((s, j) => ({ key: `bar-${s.look || ['ink', 'hatch', 'soft'][j % 3]}`, label: s.label, n: fmt(sum(data.map(r => val(r, s.key)))) })),
        opts.planned && data.some(r => n0(r.planned) > 0) && { key: 'bar-plan', label: opts.plannedLabel || 'Planned', n: fmt(sum(data.map(r => r.planned))) },
        lineK && { key: 'line', label: lineK.label },
        data.some(r => isNum(+r.budget)) && { key: 'pace', label: 'Budget' },
        pace && isNum(pace.value) && { key: 'pace', label: paceLab },
        ...[...new Set(data.map(r => r.status).filter(Boolean))].map(st => ({ swatch: h('i', { class: 'sw', 'data-status': st, 'aria-hidden': 'true' }), label: labelOf(st), n: data.filter(r => r.status === st).length })),
      ].filter(Boolean);
      if (opts.legend !== false && keyItems.length && !mini) foot.append(chartKey(keyItems));
    }
    const sz = sized(plot, draw);
    function set(r, o2) { if (o2) Object.assign(opts, o2); if (r) data = r.map((x, i) => ({ ...x, key: rowKey(x, i) })); sz.redraw(); }
    set(rows || []);
    return { el, set, update: set };
  }

  /* ============================================================ UI.calendar */
  const METRICS = {
    minutes: { label: 'Minutes', of: r => n0(r.minutes) },
    questions: { label: 'Questions', of: r => n0(r.questions ?? r.answered) },
    accuracy: { label: 'Accuracy', of: r => (n0(r.questions ?? r.answered) ? n0(r.right) / n0(r.questions ?? r.answered) : 0) },
    fixed: { label: 'Fixed', of: r => n0(r.fixed) },
  };
  function heatLevel(metric, r, goal) {
    if (!r) return 0;
    const v = METRICS[metric].of(r);
    if (metric === 'minutes') {
      if (!v) return 0;
      if (goal > 0) return v >= goal ? 3 : v >= goal / 2 ? 2 : 1;
      return v >= 45 ? 3 : v >= 15 ? 2 : 1;
    }
    if (metric === 'questions') return !v ? 0 : v >= 30 ? 3 : v >= 10 ? 2 : 1;
    if (metric === 'fixed') return !v ? 0 : v >= 4 ? 3 : v >= 2 ? 2 : 1;
    const q = n0(r.questions ?? r.answered);
    if (!q) return 0;
    return v >= .8 ? 3 : v >= .6 ? 2 : 1;
  }
  const PLAN_STATE = { done: 'done', partial: 'partly done', missed: 'missed', skipped: 'skipped', madeup: 'made up', future: '' };
  function calendar(host, o = {}) {
    const opts = { look: 'heat', metric: 'minutes', ...o };
    const el = h('figure', { class: 'chart cal' });
    put(host, el);
    let month = ym(opts.month || opts.selected || today()), sel = opts.selected ? iso(opts.selected) : today(), focusDay = sel;
    const dmap = () => byDay(opts.days), pmap = () => byDay(opts.plan);
    const marks = () => opts.marks || {};
    const minM = () => (opts.min ? ym(opts.min) : null), maxM = () => (opts.max ? ym(opts.max) : null);
    const inRange = m => (!minM() || m >= minM()) && (!maxM() || m <= maxM());
    const shiftM = (m, k) => { const d = new Date(+m.slice(0, 4), +m.slice(5, 7) - 1 + k, 1, 12); return ym(d); };
    const planLook = () => opts.look === 'plan';
    const inPlan = d => { const mk = marks(); return (!mk.start || d >= iso(mk.start)) && (!mk.end || d <= iso(mk.end)); };

    function cellText(d, r, p) {
      const mk = marks(), bits = [flong(d).replace(',', '')];
      if (mk.exam && iso(mk.exam) === d) bits.push('SAT');
      if (planLook()) {
        if (p) {
          const kind = p.kind === 'eve' ? 'rest before the SAT' : p.kind === 'off' ? 'day off' : p.kind;
          bits.push(kind);
          if (isNum(+p.minutes) && p.minutes > 0) bits.push(`${p.minutes} minutes`);
          if (p.tasks && isNum(+p.tasks.of)) bits.push(`${n0(p.tasks.done)} of ${p.tasks.of} tasks`);
          if (p.own) bits.push('your own task');
          if (p.state && PLAN_STATE[p.state]) bits.push(PLAN_STATE[p.state]);
          if (p.phase_start && p.phase) bits.push(`${p.phase} starts`);
        } else bits.push('no plan');
        return bits.join(', ');
      }
      const q = n0(r && (r.questions ?? r.answered));
      if (r && (n0(r.minutes) || q)) {
        bits.push(`${Math.round(n0(r.minutes))} minutes`, `${q} question${q === 1 ? '' : 's'}`);
        if (q) bits.push(`${Math.round(n0(r.right) / q * 100)}% right`);
        if (n0(r.fixed)) bits.push(`${r.fixed} fixed`);
      } else if (d <= today()) bits.push('nothing logged');
      if (r && r.rest) bits.push('rest day, streak safe');
      if (r && r.spare_used) bits.push('spare day used, streak kept');
      if (p && p.kind && d >= today()) bits.push(`planned ${p.kind}${p.load ? ` ${p.load}` : ''}`);
      if (p && p.state === 'skipped') bits.push('skipped');
      const due = r && r.due ? n0(r.due.checks ?? r.due) : 0;
      if (due && d >= today()) bits.push(`${due} due`);
      return bits.join(', ');
    }

    function draw(focus) {
      const D = dmap(), P = pmap(), mk = marks(), td = today();
      const [yy, mm] = month.split('-').map(Number);
      const first = `${month}-01`;
      const days = new Date(yy, mm, 0).getDate();
      const lead = (toDate(first).getDay() + 6) % 7;
      const start = addDays(first, -lead);
      const weeks = Math.ceil((lead + days) / 7);
      el.className = `chart cal${planLook() ? ' plan' : ''}${opts.compact ? ' compact' : ''}`;
      // header
      const prevB = h('button', { type: 'button', class: 'ibtn cal-nav', 'aria-label': 'Previous month', disabled: !inRange(shiftM(month, -1)) || null, text: '‹' });
      const nextB = h('button', { type: 'button', class: 'ibtn cal-nav', 'aria-label': 'Next month', disabled: !inRange(shiftM(month, 1)) || null, text: '›' });
      const title = h('h3', { class: 'cal-title', 'aria-live': 'polite', text: `${MONTH[mm - 1]} ${yy}` });
      prevB.addEventListener('click', () => go(shiftM(month, -1)));
      nextB.addEventListener('click', () => go(shiftM(month, 1)));
      const head = h('div', { class: 'cal-head' }, prevB, title, nextB);
      if (ym(td) !== month && inRange(ym(td))) head.append(h('button', { type: 'button', class: 'quiet sm cal-jump', text: 'Today', onclick: () => { sel = td; focusDay = td; go(ym(td), true); } }));
      const parts = [head];
      if (opts.metrics && !planLook() && UI.seg) {
        const box = h('div', { class: 'cal-metric' });
        UI.seg(box, Object.entries(METRICS).map(([value, m]) => ({ value, label: m.label })), { value: opts.metric, label: 'Colour by', onChange: v => { opts.metric = v; if (opts.onMetric) opts.onMetric(v); draw(); } });
        parts.push(box);
      }
      // grid
      const grid = h('div', { class: 'cal-grid', role: 'grid', 'aria-label': `${MONTH[mm - 1]} ${yy}` });
      grid.append(h('div', { role: 'row', class: 'cal-dow' }, ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'].map((t, i) => h('span', { role: 'columnheader', 'aria-label': DOWL[(i + 1) % 7], text: t }))));
      const cells = [];
      let active = 0, totMin = 0, totQ = 0, activeDays = 0;
      for (let w = 0; w < weeks; w++) {
        const row = h('div', { role: 'row', class: 'cal-row' });
        for (let k = 0; k < 7; k++) {
          const d = addDays(start, w * 7 + k), out = d.slice(0, 7) !== month;
          const r = D.get(d), p = P.get(d);
          if (!out && r) { totMin += n0(r.minutes); totQ += n0(r.questions ?? r.answered); if (n0(r.questions ?? r.answered) || n0(r.minutes)) activeDays++; }
          const blank = out || (planLook() && !inPlan(d));
          if (blank) { row.append(h('span', { role: 'gridcell', class: 'cal-d blank' + (out ? ' out' : ''), 'aria-hidden': out ? 'true' : null }, !(out && planLook()) ? h('span', { class: 'cal-n', text: String(toDate(d).getDate()) }) : null)); continue; }
          const exam = mk.exam && iso(mk.exam) === d;
          const hl = planLook() ? 0 : heatLevel(opts.metric, r, opts.goal);
          const q = n0(r && (r.questions ?? r.answered));
          const b = h('button', {
            type: 'button', role: 'gridcell', class: 'cal-d print-keep', tabindex: '-1', 'data-day': d,
            'data-h': hl || null, 'data-hollow': !planLook() && opts.metric === 'accuracy' && q > 0 && q < 5 ? '' : null,
            'data-exam': exam ? '' : null, 'data-today': d === td ? '' : null, 'aria-selected': d === sel ? 'true' : 'false',
            'data-rest': r && r.rest ? '' : null, 'data-spare': r && r.spare_used ? '' : null,
            'data-kind': p && p.kind ? p.kind : null, 'data-state': p && p.state ? p.state : null,
            'aria-current': d === td ? 'date' : null, 'aria-label': cellText(d, r, p),
          });
          b.append(h('span', { class: 'cal-n', text: String(toDate(d).getDate()), 'aria-hidden': 'true' }));
          if (exam) b.append(h('span', { class: 'cal-sat', 'aria-hidden': 'true', text: 'SAT' }));
          else if (p && p.kind === 'eve' && planLook()) b.append(h('span', { class: 'cal-meta', 'aria-hidden': 'true', text: 'Rest' }));
          else if (p && p.kind && p.kind !== 'off' && p.kind !== 'eve') b.append(h('i', { class: 'cal-mark', 'aria-hidden': 'true' }));
          if (!planLook() && r && r.rest && !q) b.append(h('i', { class: 'cal-shield', 'aria-hidden': 'true' }));
          if (planLook() && p) {
            if (isNum(+p.minutes) && p.minutes > 0 && !exam && !['rest', 'off', 'eve'].includes(p.kind)) b.append(h('span', { class: 'cal-meta', 'aria-hidden': 'true', text: `${p.minutes}m` }));
            if (p.own) b.append(h('i', { class: 'cal-own', 'aria-hidden': 'true' }));
            if (p.phase_start && p.phase) b.append(h('span', { class: 'cal-phase', 'aria-hidden': 'true', text: p.phase }));
            if (p.phase) b.dataset.phase = p.current_phase ? 'now' : 'other';
          } else if (d >= td && !exam) {
            const due = r && r.due ? n0(r.due.checks ?? r.due) : 0;
            const load = p && p.load;
            if ((due || load) && !opts.compact) b.append(h('span', { class: 'cal-meta', 'aria-hidden': 'true', text: due ? `${due} due` : load }));
          }
          b.addEventListener('click', () => { sel = d; focusDay = d; mark(); if (opts.onPick) opts.onPick(d, r || null, p || null); });
          b.addEventListener('focus', () => { focusDay = d; cells.forEach(c => { c.tabIndex = c === b ? 0 : -1; }); });
          if (d === focusDay) active = cells.length;
          cells.push(b);
          row.append(b);
        }
        grid.append(row);
      }
      if (!cells.some(c => c.dataset.day === focusDay)) {
        const t = cells.findIndex(c => c.dataset.day === td);
        active = t >= 0 ? t : 0;
      }
      if (cells[active]) cells[active].tabIndex = 0;
      grid.addEventListener('keydown', e => onKey(e, cells));
      parts.push(grid);
      // legend: the scale is the role=img that carries the month's summary
      const summary = planLook()
        ? `${MONTH[mm - 1]} ${yy} plan: ${[...P.values()].filter(p => p.day.startsWith(month) && ['practice', 'test'].includes(p.kind)).length} study days${mk.exam && iso(mk.exam).startsWith(month) ? `, SAT on ${fdate(mk.exam)}` : ''}.`
        : `${MONTH[mm - 1]} ${yy}: ${activeDays} active day${activeDays === 1 ? '' : 's'}, ${fdur(totMin)}, ${fnum(totQ)} questions${mk.exam && iso(mk.exam).startsWith(month) ? `, SAT on ${fdate(mk.exam)}` : ''}.`;
      if (opts.legend !== false) parts.push(calLegend(summary, D, P));
      parts.push(dataTable(summary, planLook() ? ['Date', 'Kind', 'Minutes', 'Tasks', 'State'] : ['Date', 'Minutes', 'Questions', 'Right', 'Fixed', 'Plan'],
        [...Array(days).keys()].map(i => {
          const d = `${month}-${String(i + 1).padStart(2, '0')}`, r = D.get(d) || {}, p = P.get(d) || {};
          if (planLook()) return [fdate(d), p.kind || '', p.minutes ?? '', p.tasks ? `${n0(p.tasks.done)} of ${p.tasks.of}` : '', PLAN_STATE[p.state] || ''];
          const q = n0(r.questions ?? r.answered);
          return [fdate(d), fnum(n0(r.minutes)), fnum(q), q ? `${Math.round(n0(r.right) / q * 100)}%` : '', fnum(n0(r.fixed)),
            [p.kind, p.state, r.rest && 'rest day', r.spare_used && 'spare day', mk.exam && iso(mk.exam) === d && 'SAT'].filter(Boolean).join(', ')];
        })));
      el.replaceChildren(...parts);
      if (focus && cells[active]) cells[active].focus();
    }
    function calLegend(summary, D, P) {
      const sc = h('span', { class: 'cal-scale', role: 'img', 'aria-label': summary });
      const box = h('div', { class: 'cal-key' });
      if (planLook()) {
        const items = [['practice', 'Practice'], ['test', 'Test'], ['rest', 'Rest'], ['off', 'Day off'], ['done', 'Done'], ['partial', 'Partly done'], ['missed', 'Missed'], ['skipped', 'Skipped'], ['madeup', 'Made up'], ['sat', 'SAT']];
        sc.append(...items.map(([k, t]) => h('span', { class: 'cal-k' }, h('i', { class: `cal-sw ${k}`, 'aria-hidden': 'true' }), t)));
        box.append(sc);
        return box;
      }
      sc.append(h('span', { text: 'Less' }), ...[0, 1, 2, 3].map(k => h('i', { class: 'cal-sw', 'data-h': k || null })), h('span', { text: 'More' }));
      box.append(sc);
      const vals = [...P.values()];
      const extra = [
        vals.some(p => p.kind === 'practice') && ['practice', 'study day'], vals.some(p => p.kind === 'test') && ['test', 'test day'],
        vals.some(p => p.state === 'skipped') && ['skipped', 'skipped'],
        [...D.values()].some(r => r.rest) && ['shield', 'rest day'], [...D.values()].some(r => r.spare_used) && ['spare', 'spare day'],
        marks().exam && ['sat', 'SAT'],
      ].filter(Boolean);
      extra.forEach(([k, t]) => box.append(h('span', { class: 'cal-k' }, h('i', { class: `cal-sw ${k}`, 'aria-hidden': 'true' }), t)));
      return box;
    }
    function onKey(e, cells) {
      const i = cells.indexOf(doc.activeElement);
      if (i < 0) return;
      const d = cells[i].dataset.day;
      const dow = (toDate(d).getDay() + 6) % 7;
      let to = null;
      if (e.key === 'ArrowRight') to = addDays(d, 1);
      else if (e.key === 'ArrowLeft') to = addDays(d, -1);
      else if (e.key === 'ArrowDown') to = addDays(d, 7);
      else if (e.key === 'ArrowUp') to = addDays(d, -7);
      else if (e.key === 'Home') to = addDays(d, -dow);
      else if (e.key === 'End') to = addDays(d, 6 - dow);
      else if (e.key === 'PageUp' || e.key === 'PageDown') {
        const m = shiftM(month, e.key === 'PageUp' ? -1 : 1);
        if (!inRange(m)) return;
        const last = new Date(+m.slice(0, 4), +m.slice(5, 7), 0).getDate();
        to = `${m}-${String(Math.min(+d.slice(8), last)).padStart(2, '0')}`;
      } else if (e.key === 't' || e.key === 'T') to = today();
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); cells[i].click(); return; }
      if (!to) return;
      e.preventDefault();
      const c = cells.find(x => x.dataset.day === to);
      if (c) { c.focus(); return; }
      if (ym(to) !== month && inRange(ym(to))) { focusDay = to; go(ym(to), true); }
    }
    function mark() { el.querySelectorAll('.cal-d[data-day]').forEach(c => c.setAttribute('aria-selected', String(c.dataset.day === sel))); }
    function go(m, focus) {
      m = ym(`${m}`.length === 7 ? `${m}-01` : m);
      if (!inRange(m)) return;
      const moved = m !== month;
      month = m;
      if (!focusDay.startsWith(m)) focusDay = sel.startsWith(m) ? sel : `${m}-01`;
      draw(focus);
      if (moved && opts.onMonth) opts.onMonth(m);
    }
    draw();
    return {
      el, get month() { return month; }, go,
      select(d) { sel = iso(d); focusDay = sel; if (ym(sel) !== month) go(ym(sel)); else mark(); },
      set(o2 = {}) { Object.assign(opts, o2); if (o2.month) month = ym(o2.month.length === 7 ? `${o2.month}-01` : o2.month); draw(); },
    };
  }

  /* ============================================================ UI.heatmap */
  function heatmap(host, days, o = {}) {
    const opts = { ...o };
    const el = h('figure', { class: 'chart heatmap' });
    put(host, el);
    let data = byDay(days), focusDay = null;
    const lvl = q => (!q ? 0 : q < 10 ? 1 : q < 25 ? 2 : q < 50 ? 3 : 4);
    function cellText(d, r) {
      const q = n0(r && (r.questions ?? r.answered));
      if (r && r.spare_used && !q) return `${flong(d)} · spare day used · streak kept`;
      if (r && r.rest && !q) return `${flong(d)} · rest day (plan) · streak kept`;
      if (!q && !n0(r && r.minutes)) return `${flong(d)} · nothing logged`;
      return [flong(d), `${fnum(q)} question${q === 1 ? '' : 's'}`, fmin(n0(r.minutes)), `${fnum(n0(r.right))} right`, r.rest && 'rest day (plan)'].filter(Boolean).join(' · ');
    }
    function draw(focus) {
      const want = opts.weeks || 26;
      const weeks = phone() ? Math.min(want, 20) : want;
      const end = iso(opts.end || today());
      const firstMon = addDays(monOf(end), -7 * (weeks - 1));
      const grid = h('div', { class: 'heat', role: 'grid', style: `--weeks:${weeks}` });
      if (UI.nearTap) UI.nearTap(grid, 'button.heat-c');
      // month labels over the first column that holds a 1st, and the M / W / F row labels
      const firsts = [];
      for (let w = 0; w < weeks; w++) {
        const d1 = [...Array(7).keys()].map(k => addDays(firstMon, w * 7 + k)).find(d => d.endsWith('-01') && d <= end);
        if (d1) firsts.push([w, d1]);
      }
      if (!firsts.length || firsts[0][0] > 2) firsts.unshift([0, firstMon]);
      firsts.forEach(([w, d1], i) => {
        if (i && w - firsts[i - 1][0] < 3) return;
        grid.append(h('span', { class: 'heat-m', 'aria-hidden': 'true', style: `grid-column:${w + 2}/span 3;grid-row:1`, text: MON[toDate(d1).getMonth()] }));
      });
      const cells = [];
      let active = 0, activeDays = 0, minutes = 0, questions = 0;
      for (let k = 0; k < 7; k++) {
        const row = h('div', { role: 'row', class: 'heat-r' });
        row.append(h('span', { role: 'rowheader', class: 'heat-d', style: `grid-column:1;grid-row:${k + 2}`, 'aria-label': DOWL[(k + 1) % 7], text: k % 2 === 0 && k < 6 ? DOW[(k + 1) % 7][0] : '' }));
        for (let w = 0; w < weeks; w++) {
          const d = addDays(firstMon, w * 7 + k);
          if (d > end) { row.append(h('span', { role: 'gridcell', class: 'heat-c pad', style: `grid-column:${w + 2};grid-row:${k + 2}` })); continue; }
          const r = data.get(d);
          const q = n0(r && (r.questions ?? r.answered));
          if (q) { activeDays++; questions += q; }
          minutes += n0(r && r.minutes);
          const t = cellText(d, r);
          const b = h('button', {
            type: 'button', role: 'gridcell', class: 'heat-c print-keep', tabindex: '-1', 'data-day': d, 'data-h': lvl(q) || null,
            'data-rest': r && r.rest && !q ? '' : null, 'data-spare': r && r.spare_used ? '' : null,
            'aria-current': d === today() ? 'date' : null, 'aria-label': t, style: `grid-column:${w + 2};grid-row:${k + 2}`,
          });
          if (UI.tooltip) UI.tooltip(b, t, { delay: 60 });
          b.addEventListener('click', () => { if (opts.onPick) opts.onPick(d, r || null); });
          b.addEventListener('focus', () => { focusDay = d; cells.forEach(c => { c.tabIndex = c === b ? 0 : -1; }); });
          cells.push(b);
          row.append(b);
        }
        grid.append(row);
      }
      const want0 = focusDay || end;
      active = Math.max(0, cells.findIndex(c => c.dataset.day === want0));
      if (cells[active]) cells[active].tabIndex = 0;
      grid.addEventListener('keydown', e => {
        const i = cells.indexOf(doc.activeElement);
        if (i < 0) return;
        const d = cells[i].dataset.day;
        const to = { ArrowUp: addDays(d, -1), ArrowDown: addDays(d, 1), ArrowLeft: addDays(d, -7), ArrowRight: addDays(d, 7) }[e.key]
          ?? (e.key === 'Home' ? cells[0].dataset.day : e.key === 'End' ? end : null);
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); cells[i].click(); return; }
        if (!to) return;
        e.preventDefault();
        const c = cells.find(x => x.dataset.day === to);
        if (c) c.focus();
      });
      // the stats row, when given, is the one source for these facts (rule 5); else the grid's own count
      const st = opts.stats;
      const facts = st ? [isNum(+st.active_days) && plural(+st.active_days, 'active day'), isNum(+st.streak) && `current streak ${fnum(st.streak)}`,
        isNum(+(st.best ?? st.best_streak)) && `best ${fnum(st.best ?? st.best_streak)}`, isNum(+(st.minutes ?? st.minutes_total)) && `study time ${fdur(st.minutes ?? st.minutes_total)}`].filter(Boolean)
        : [plural(activeDays, 'active day'), plural(questions, 'question'), fdur(minutes)];
      const summary = `Activity, ${weeks} weeks to ${fdate(end)}${st ? '. ' + cap1(facts.join(', ')) : `: ${facts.join(', ')}`}. Colour by questions a day: none, 1 to 9, 10 to 24, 25 to 49, 50 or more.`;
      grid.setAttribute('aria-label', `Activity, ${weeks} weeks`);
      const parts = [];
      if (opts.range && !phone() && UI.seg) {
        const box = h('div', { class: 'chart-ctl' });
        UI.seg(box, [{ value: 26, label: '26 weeks' }, { value: 52, label: '52 weeks' }], {
          value: want, label: 'Range',
          onChange: async v => { opts.weeks = v; if (opts.onRange) { const more = await opts.onRange(v); if (more) data = byDay(more); } draw(); },
        });
        parts.push(box);
      }
      parts.push(h('div', { class: 'heat-wrap' }, grid));
      const vals = [...data.values()];
      const scale = h('span', { class: 'heat-scale', role: 'img', 'aria-label': summary },
        h('span', { text: 'Less' }), [0, 1, 2, 3, 4].map(k => h('i', { 'data-h': k || null })), h('span', { text: 'More' }));
      if (opts.legend !== false) {
        parts.push(h('div', { class: 'heat-key' }, scale,
          vals.some(r => r.rest && !n0(r.questions ?? r.answered)) ? h('span', { class: 'heat-k' }, h('i', { class: 'heat-c', 'data-rest': '' }), 'rest day') : null,
          vals.some(r => r.spare_used) ? h('span', { class: 'heat-k' }, h('i', { class: 'heat-c', 'data-spare': '' }), 'spare day') : null));
      } else parts.push(h('span', { class: 'sr', role: 'img', 'aria-label': summary }));
      if (st) parts.push(h('p', { class: 'heat-stats' }, [
        isNum(+st.active_days) && `Active days ${fnum(st.active_days)}`, isNum(+st.streak) && `Current streak ${fnum(st.streak)}`,
        isNum(+(st.best ?? st.best_streak)) && `Best ${fnum(st.best ?? st.best_streak)}`, isNum(+(st.minutes ?? st.minutes_total)) && `Study time ${fdur(st.minutes ?? st.minutes_total)}`,
        isNum(+st.spares) && st.spares > 0 && `${st.spares} spare${st.spares === 1 ? '' : 's'} banked`,
      ].filter(Boolean).join(' · ')));
      const rows = [...data.values()].filter(r => r.day >= firstMon && r.day <= end && (n0(r.questions ?? r.answered) || n0(r.minutes) || r.rest || r.spare_used)).sort((a, b) => (a.day < b.day ? 1 : -1));
      parts.push(dataTable(summary, ['Day', 'Questions', 'Right', 'Minutes', 'Note'],
        rows.map(r => [flong(r.day), fnum(n0(r.questions ?? r.answered)), fnum(n0(r.right)), fnum(n0(r.minutes)), [r.rest && 'rest day', r.spare_used && 'spare day used'].filter(Boolean).join(', ')])));
      el.replaceChildren(...parts);
      if (focus && cells[active]) cells[active].focus();
    }
    draw();
    let wasPhone = phone();
    addEventListener('resize', () => { if (phone() !== wasPhone) { wasPhone = phone(); draw(); } });
    return { el, set(d, o2) { if (o2) Object.assign(opts, o2); if (d) data = byDay(d); draw(); } };
  }

  /* ============================================================ UI.lineChart */
  function lineChart(host, series, o = {}) {
    const { el, plot } = frame(host, 'line-chart', o);
    const opts = { ...o };
    let S = [];
    const foot = h('div', { class: 'chart-foot' });
    el.append(foot);
    const isIdx = () => opts.x === 'index';
    const fy = v => (opts.format ? opts.format(v) : fnum(v));
    const fx = x => (opts.xFormat ? opts.xFormat(x) : isIdx() ? `Q${x}` : fdate(x));
    function norm(list) {
      return (list || []).map((s, j) => ({ ...s, key: s.key ?? j, label: s.label ?? `Series ${j + 1}`,
        points: (s.points || []).map(p => ({ ...p, x: isIdx() ? +(p.x ?? p.n) : +toDate(p.x ?? p.day ?? p.at), y: +(p.y ?? p.value) })).filter(p => isNum(p.x) && isNum(p.y)).sort((a, b) => a.x - b.x) }));
    }
    function draw(W) {
      const H = opts.height ?? 120;
      const mini = H < 90;
      const all = S.flatMap(s => s.points);
      const R = mini ? 6 : 14, T = mini ? 6 : 10, B = mini ? 6 : 20;
      let L = mini ? 4 : 40;
      const xsAll = [...new Set(all.map(p => p.x))].sort((a, b) => a - b);
      const x0 = xsAll[0] ?? 0, x1 = xsAll[xsAll.length - 1] ?? 1;
      const xOf = x => L + (xsAll.length > 1 ? (x - x0) / (x1 - x0) : .5) * plotW;
      let lo = opts.min ?? Math.min(...all.map(p => p.y), ...(opts.bands || []).map(b => +b.from).filter(isNum));
      let hi = opts.max ?? Math.max(...all.map(p => p.y), ...(opts.bands || []).map(b => +b.to).filter(isNum));
      if (!isFinite(lo) || !isFinite(hi)) { lo = 0; hi = 1; }
      if (hi === lo) { hi += 1; lo -= 1; }
      if (opts.min === undefined && !opts.log && !opts.bands) { const pad = (hi - lo) * .08; lo -= pad; hi += pad; }
      const t = v => (opts.log ? (Math.log(Math.max(v, 1e-9)) - Math.log(lo)) / (Math.log(hi) - Math.log(lo)) : (v - lo) / (hi - lo));
      const yOf = v => T + (H - T - B) * (opts.invert ? t(clamp(v, lo, hi)) : 1 - t(clamp(v, lo, hi)));
      const gv = opts.grid || (() => { const m = niceMax((hi - lo) / 3); const out = []; for (let v = Math.ceil(lo / m) * m; v <= hi; v += m) out.push(v); return out; })();
      if (!mini) L = Math.max(L, 10 + Math.max(0, ...gv.map(v => textW(fy(v), 10.5))));
      const plotW = W - L - R;
      const svg = svgRoot(W, H, '');
      // every series as boxes, and the labels to draw over them once the lines are down
      const obs = mini ? [] : S.flatMap(s => lineBoxes(s.points.map(p => [xOf(p.x), yOf(p.y)])));
      const labels = [], bandReq = [];
      (opts.bands || []).forEach((b, i) => {
        const ya = yOf(clamp(+b.from, lo, hi)), yb = yOf(clamp(+b.to, lo, hi));
        const top = Math.min(ya, yb), bot = Math.max(ya, yb);
        sv('rect', { x: L, width: plotW, y: r1(top), height: r1(bot - top), class: 'ch-stripe' + (i % 2 ? ' alt' : '') }, svg);
        if (mini || !b.label || bot - top <= 12) return;
        bandReq.push([[[L + 4, top + 11, 'start'], [W - R - 4, top + 11, 'end'], [L + 4, bot - 4, 'start'], [W - R - 4, bot - 4, 'end'], [L + plotW / 2, top + 11, 'middle']], b.label]);
      });
      const grid = sv('g', { class: 'ch-grid' }, svg);
      let lastY = null;
      if (!mini) [...gv].sort((a, b) => yOf(a) - yOf(b)).forEach(v => { sv('line', { x1: L, x2: W - R, y1: r1(yOf(v)), y2: r1(yOf(v)) }, grid); if (lastY === null || yOf(v) - lastY >= 12) { tx(grid, L - 6, yOf(v) + 3.5, fy(v), { 'text-anchor': 'end', class: 'ch-ytick' }); lastY = yOf(v); } });
      (opts.annotate || []).forEach(a => {
        const x = xOf(isIdx() ? +a.x : +toDate(a.x));
        sv('line', { x1: r1(x), x2: r1(x), y1: T, y2: H - B, class: 'ch-now' }, svg);
        if (a.text && !mini) tx(svg, x + 4, T + 9, a.text, { class: 'ch-lab' });
      });
      const cross = sv('line', { x1: 0, x2: 0, y1: T, y2: H - B, class: 'ch-cross', visibility: 'hidden' }, svg);
      S.forEach((s, j) => {
        if (!s.points.length) return;
        const d = s.points.map((p, k) => `${k ? 'L' : 'M'}${r1(xOf(p.x))} ${r1(yOf(p.y))}`).join(' ');
        sv('path', { d, class: `ch-line${s.dashed ? ' dashed' : ''}${s.you ? ' you' : ''}${j && !s.you && !s.dashed ? ' soft' : ''}` }, svg);
        const dots = !mini && s.points.length <= 40;
        s.points.forEach((p, k) => {
          const x = xOf(p.x), yy = yOf(p.y);
          if (p.star) sv('path', { d: starPath(x, yy, mini ? 4 : 6), class: 'ch-star' }, svg);
          else if (dots || (k === s.points.length - 1 && !s.dashed)) sv('circle', { cx: r1(x), cy: r1(yy), r: mini ? 2.5 : 4, class: 'ch-dot' + (s.you ? ' you' : '') }, svg);
        });
        const lp = s.points[s.points.length - 1];
        if (!mini && (s.you || j === 0) && opts.endLabel !== false) {
          const lab = fy(lp.y), x = xOf(lp.x), y = yOf(lp.y), fits = x + textW(lab) + 8 <= W;
          const c = [-7, 15, 25, -17].flatMap(dy => [[x + 7, y + dy, 'start'], [x - 8, y + dy, 'end']]).filter(([, yy, a]) => (a === 'end' || fits) && yy > 10 && yy < H - B + 4);
          labels.push([clearOf(c, lab, obs) || c[0], lab, 'ch-lab ch-end']);
        }
      });
      // the values first, then the band names in what room is left
      bandReq.forEach(([c, text]) => labels.push([clearOf(c, text, obs) || c[0], text, 'ch-lab']));
      labels.forEach(([[x, y, a], text, cls]) => tx(svg, x, y, text, { 'text-anchor': a, class: cls }));
      if (!mini && xsAll.length) {
        const every = Math.max(1, Math.ceil((Math.max(...xsAll.map(x => textW(fx(x), 10.5))) + 10) / Math.max(1, plotW / xsAll.length)));
        xsAll.forEach((x, i) => {
          if ((xsAll.length - 1 - i) % every) return;
          const half = textW(fx(x), 10.5) / 2;
          const a = xsAll.length > 1 && i === 0 && xOf(x) - half < 0 ? 'start' : xOf(x) + half > W ? 'end' : 'middle';
          tx(svg, a === 'start' ? Math.max(0, xOf(x) - half) : a === 'end' ? W : xOf(x), H - 5, fx(x), { 'text-anchor': a, class: 'ch-xtick' });
        });
      }
      const summary = all.length ? `${opts.label || 'Line chart'}: ` + S.map(s => {
        if (!s.points.length) return `${s.label}, no points`;
        const a = s.points[0], b = s.points[s.points.length - 1];
        return `${s.label} from ${fy(a.y)} (${fx(a.x)}) to ${fy(b.y)} (${fx(b.x)}), ${plural(s.points.length, 'point')}`;
      }).join('; ') + '.' : `${opts.label || 'Line chart'}: nothing yet.`;
      svg.setAttribute('aria-label', summary);
      const old = plot.querySelector(':scope > svg');
      if (old) old.replaceWith(svg); else plot.prepend(svg);
      emptyNote(plot, all.length ? null : (opts.empty || {}), 'Nothing yet.');
      // one control per x: its tip lists every series there, the hairline follows it
      const col = x => S.map(s => [s, s.points.find(p => p.x === x)]).filter(([, p]) => p);
      const tipAt = x => { const c = col(x); const p0 = c[0] && c[0][1]; return (p0 && p0.tip) || [p0 && p0.label ? `${fx(x)} · ${p0.label}` : fx(x), ...c.map(([s, p]) => `${S.length > 1 ? `${s.label} ` : ''}${fy(p.y)}${p.star ? ' · record' : ''}`)].join(' · '); };
      hitLayer(plot, xsAll.map((x, i) => {
        const xa = i ? (xOf(xsAll[i - 1]) + xOf(x)) / 2 : L - 6, xb = i < xsAll.length - 1 ? (xOf(x) + xOf(xsAll[i + 1])) / 2 : W - R + 6;
        const c = col(x);
        const target = c.find(([s]) => s.you) || c[0];
        return { x: xa, y: T - 4, w: Math.max(8, xb - xa), h: H - T - B + 8, label: tipAt(x), tip: tipAt(x), _x: xOf(x),
          pick: opts.onPick && target ? () => opts.onPick(target[1], target[0]) : target && target[1].href ? () => { location.href = target[1].href; } : null };
      }), { label: opts.label || 'Points', onFocus: it => { if (it) { cross.setAttribute('x1', r1(it._x)); cross.setAttribute('x2', r1(it._x)); cross.setAttribute('visibility', 'visible'); } else cross.setAttribute('visibility', 'hidden'); } });
      setTable(el, dataTable(summary, [isIdx() ? 'Question' : 'Date', ...S.map(s => s.label)],
        xsAll.map(x => [fx(x), ...S.map(s => { const p = s.points.find(q => q.x === x); return p ? fy(p.y) + (p.star ? ' (record)' : '') : ''; })])));
      foot.replaceChildren();
      if (S.length > 1 && opts.legend !== false && !mini) foot.append(chartKey(S.map(s => ({ key: s.dashed ? 'dash' : s.you ? 'target' : 'line', label: s.label, swatch: lineSw(s) }))));
    }
    function lineSw(s) {
      const sw = sv('svg', { class: 'ch-key', width: 18, height: 12, viewBox: '0 0 18 12', 'aria-hidden': 'true', focusable: 'false' });
      sv('path', { d: 'M1 6 H17', class: `ch-line${s.dashed ? ' dashed' : ''}${s.you ? ' you' : ''}` }, sw);
      return sw;
    }
    const sz = sized(plot, draw);
    function set(s, o2) { if (o2) Object.assign(opts, o2); if (s) S = norm(s); sz.redraw(); }
    set(series || []);
    return { el, set, update: set };
  }

  /* ============================================================ UI.spread */
  function spread(host, options, o = {}) {
    const el = h('figure', { class: 'chart spread' + (o.className ? ' ' + o.className : '') });
    put(host, el);
    const opts = { ...o };
    function draw(list) {
      const total = opts.n ?? sum(list.map(x => x.n));
      const rows = list.map(x => ({ ...x, share: isNum(+x.share) && x.share !== null ? (x.share > 1 ? x.share / 100 : +x.share) : total ? n0(x.n) / total : 0 }));
      const vis = h('div', { class: 'spread-vis', role: 'img' });
      rows.forEach(x => {
        const tags = [x.key && h('span', { class: 'spread-tag key', text: '✓ Right answer' }), x.pick && h('span', { class: 'spread-tag pick', text: x.key ? 'Your pick' : '✕ Your pick' })];
        vis.append(h('div', { class: 'spread-row', 'data-key': x.key ? '' : null, 'data-pick': x.pick ? '' : null },
          h('span', { class: 'spread-l', text: x.label ?? '' }),
          h('span', { class: 'spread-main' },
            x.text ? h('span', { class: 'spread-t', text: x.text }) : null,
            h('span', { class: 'spread-bar' }, h('i', { style: `width:${r1(x.share * 100)}%` }))),
          h('span', { class: 'spread-v', text: pct(x.share) }),
          (x.reason || tags.some(Boolean)) ? h('span', { class: 'spread-why' }, tags, !x.key && x.reason ? h('span', { text: x.reason }) : null) : null));
      });
      const summary = rows.length ? `${opts.label || 'How everyone answered'}${total ? `, ${fnum(total)} ${opts.noun || 'answers'}` : ''}: ` +
        rows.map(x => `${x.label ?? x.text} ${pct(x.share)}${x.key ? ' (right)' : x.reason ? ` (${x.reason})` : ''}${x.pick ? ', your pick' : ''}`).join('; ') + '.'
        : `${opts.label || 'How everyone answered'}: nothing yet.`;
      vis.setAttribute('aria-label', summary);
      if (!rows.length) { el.replaceChildren(vis, emptyBlock(opts.empty, 'How everyone answered shows here once others answer this question.')); return; }
      el.replaceChildren(vis, dataTable(summary, ['Option', 'Share', 'Answers', 'Misconception'],
        rows.map(x => [`${x.label ?? ''}${x.text ? ` ${x.text}` : ''}${x.key ? ' (right)' : ''}${x.pick ? ' (your pick)' : ''}`.trim(), pct(x.share), isNum(+x.n) ? fnum(x.n) : '', x.key ? '' : x.reason || ''])));
    }
    draw(options || []);
    return { el, set(list, o2) { if (o2) Object.assign(opts, o2); draw(list || []); } };
  }

  /* ============================================================ UI.quadrant */
  const QNAMES = { slow_right: 'You know it, slowly', fast_wrong: 'Rushing', slow_wrong: 'Time sink', fast_right: 'Banked' };
  function quadrant(host, points, o = {}) {
    const { el, plot } = frame(host, 'quad-chart', o);
    const opts = { x: 'seconds', xRef: 95, ...o };
    let P = [], view = 'chart';
    const ctl = h('div', { class: 'chart-ctl quad-ctl' }), list = h('div', { class: 'quad-list', hidden: '' }), foot = h('div', { class: 'chart-foot' });
    el.prepend(ctl);
    el.append(list, foot);
    const names = () => ({ ...QNAMES, ...(opts.names || {}) });
    const yRef = () => opts.yRef ?? (P.length ? sum(P.map(p => p.y)) / P.length : .7);
    const quad = p => `${p.x > opts.xRef ? 'slow' : 'fast'}_${p.y >= yRef() ? 'right' : 'wrong'}`;
    const fxv = v => (opts.x === 'ratio' ? `${(Math.round(v * 100) / 100).toFixed(2).replace(/0$/, '')}× budget` : fmmss(v));
    function draw(W) {
      const ph = phone();
      const H = opts.height ?? (ph ? 300 : 280);
      const L = 40, R = 12, T = 22, B = 30;
      const plotW = W - L - R;
      const lg = opts.log ?? opts.x === 'ratio';
      const xMin = opts.xMin ?? (opts.x === 'ratio' ? .5 : 0), xMax = opts.xMax ?? (opts.x === 'ratio' ? 2 : Math.max(opts.xRef * 2, ...P.map(p => p.x * 1.1)));
      const tX = v => (lg ? (Math.log(clamp(v, xMin, xMax)) - Math.log(xMin)) / (Math.log(xMax) - Math.log(xMin)) : (clamp(v, xMin, xMax) - xMin) / (xMax - xMin));
      const xOf = v => L + tX(v) * plotW, yOf = v => T + (H - T - B) * (1 - clamp(v, 0, 1));
      const svg = svgRoot(W, H, '');
      const xr = xOf(opts.xRef), yr = yOf(yRef()), nm = names();
      const boxes = [];                               // placed text, which a dot's label keeps clear of
      const textBox = (x, base, text, anchor, px = 11) => { const w = textW(text, px); const x0 = anchor === 'end' ? x - w : x; boxes.push([x0, base - 10, x0 + w, base + 3]); };
      const counts = {};
      P.forEach(p => { counts[quad(p)] = (counts[quad(p)] || 0) + 1; });
      const dots = P.map(p => { const x = xOf(p.x), yy = yOf(p.y); return [x - 10, yy - 10, x + 10, yy + 10]; });
      // quadrant tints and names with counts; a name takes the zone's outer corner, else another corner clear of the dots
      [['fast_right', L, T, xr - L, yr - T], ['slow_right', xr, T, W - R - xr, yr - T], ['fast_wrong', L, yr, xr - L, H - B - yr], ['slow_wrong', xr, yr, W - R - xr, H - B - yr]].forEach(([k, x, yy, w, hh]) => {
        sv('rect', { x: r1(x), y: r1(yy), width: r1(Math.max(0, w)), height: r1(Math.max(0, hh)), class: `q-zone ${k}` }, svg);
        const right = k.startsWith('slow'), top = k.endsWith('right'), zt = `${nm[k]} · ${counts[k] || 0}`;
        const sx = [right ? [x + w - 6, 'end'] : [x + 6, 'start'], right ? [x + 6, 'start'] : [x + w - 6, 'end']];
        const sy = top ? [yy + 13, yy + hh - 7] : [yy + hh - 7, yy + 13];
        const c = [[sx[0][0], sy[0], sx[0][1]], [sx[0][0], sy[1], sx[0][1]], [sx[1][0], sy[0], sx[1][1]], [sx[1][0], sy[1], sx[1][1]]];
        const [zx, zy, za] = clearOf(c, zt, [...dots, ...boxes]) || c[0];
        tx(svg, zx, zy, zt, { 'text-anchor': za, class: 'ch-lab q-name' });
        textBox(zx, zy, zt, za);
      });
      const grid = sv('g', { class: 'ch-grid' }, svg);
      [0, .25, .5, .75, 1].forEach(v => { sv('line', { x1: L, x2: W - R, y1: r1(yOf(v)), y2: r1(yOf(v)) }, grid); tx(grid, L - 6, yOf(v) + 3.5, pct(v), { 'text-anchor': 'end', class: 'ch-ytick' }); });
      const xt = opts.x === 'ratio' ? [.5, 1, 2] : (() => { const m = niceMax(xMax / 4); const out = []; for (let v = 0; v <= xMax; v += m) out.push(v); return out; })();
      xt.forEach(v => tx(grid, xOf(v), H - B + 14, opts.x === 'ratio' ? `${v}×` : fmmss(v), { 'text-anchor': 'middle', class: 'ch-xtick' }));
      tx(svg, W - R, H - 3, opts.xLabel || (opts.x === 'ratio' ? 'time ÷ budget' : 'median time on right answers'), { 'text-anchor': 'end', class: 'ch-lab' });
      sv('line', { x1: r1(xr), x2: r1(xr), y1: T, y2: H - B, class: 'q-ref' }, svg);
      sv('line', { x1: L, x2: W - R, y1: r1(yr), y2: r1(yr), class: 'q-ref' }, svg);
      const xl = opts.xRefLabel || (opts.x === 'ratio' ? 'on budget' : `test pace ${fmmss(opts.xRef)}`);
      tx(svg, xr + 4, T - 8, xl, { class: 'ch-lab' });
      textBox(xr + 4, T - 8, xl, 'start');
      const yl = opts.yRefLabel || (opts.yRef === undefined ? `your mean ${pct(yRef())}` : `${pct(yRef())} right`);
      tx(svg, L + 4, yr - 4, yl, { class: 'ch-lab' });
      textBox(L + 4, yr - 4, yl, 'start');
      // dots with their labels; a label that would touch another dot or label is left to the tooltip and the table
      const hits = (a, b) => !(a[2] < b[0] || a[0] > b[2] || a[3] < b[1] || a[1] > b[3]);
      P.forEach((p, i) => {
        const x = xOf(p.x), yy = yOf(p.y);
        if (p.topic && UI.glyph) {
          const g = UI.glyph(p.topic);
          g.setAttribute('x', r1(x - 8)); g.setAttribute('y', r1(yy - 8)); g.setAttribute('width', 16); g.setAttribute('height', 16);
          sv('circle', { cx: r1(x), cy: r1(yy), r: 10, class: 'q-halo' }, svg);
          svg.append(g);
        } else sv('circle', { cx: r1(x), cy: r1(yy), r: 4.5, class: 'ch-dot' }, svg);
        const lab = p.short || p.label || '';
        const w = textW(lab, 11.5);
        for (const [lx, anchor] of [[x + 12, 'start'], [x - 12, 'end']]) {
          const bx = anchor === 'start' ? lx : lx - w;
          if (bx < L || bx + w > W - R) continue;
          const box = [bx, yy - 7, bx + w, yy + 7];
          if (boxes.some(b => hits(box, b)) || dots.some((d, j) => j !== i && hits(box, d))) continue;
          boxes.push(box);
          tx(svg, lx, yy + 4, lab, { 'text-anchor': anchor, class: 'q-lab' });
          break;
        }
      });
      const summary = P.length ? `${opts.label || 'Pace by skill'}: ${Object.keys(QNAMES).map(k => `${counts[k] || 0} ${nm[k].toLowerCase()}`).join(', ')}. The line across is ${pct(yRef())} right; the line down is ${fxv(opts.xRef)}.` : `${opts.label || 'Pace by skill'}: nothing timed yet.`;
      svg.setAttribute('aria-label', summary);
      const old = plot.querySelector(':scope > svg');
      if (old) old.replaceWith(svg); else plot.prepend(svg);
      emptyNote(plot, P.length ? null : (opts.empty || {}), 'Answer with the clock on to see your pace.');
      const tipOf = p => p.tip || [p.label, `${fxv(p.x)}`, `${pct(p.y)} right`, isNum(+p.n) && `${p.n} answers`, nm[quad(p)]].filter(Boolean).join(' · ');
      hitLayer(plot, P.map(p => ({ x: xOf(p.x) - 12, y: yOf(p.y) - 12, w: 24, h: 24, label: tipOf(p), tip: tipOf(p),
        pick: opts.onPick ? () => opts.onPick(p, quad(p)) : p.href ? () => { location.href = p.href; } : null })), { label: opts.label || 'Skills', start: 0 });
      setTable(el, dataTable(summary, [opts.rowLabel || 'Skill', opts.x === 'ratio' ? 'Time ÷ budget' : 'Median time', 'Right', 'Answers', 'Group'],
        P.map(p => [p.label, fxv(p.x), pct(p.y), isNum(+p.n) ? p.n : '', nm[quad(p)]])));
      // the list view (the phone's Chart | List)
      list.replaceChildren(...P.map(p => h('div', { class: 'quad-row' },
        h('span', { class: 'quad-n', text: p.label }), h('span', { class: 'mono', text: `${fxv(p.x)} · ${pct(p.y)}` }),
        h('span', { class: 'quad-chip', 'data-q': quad(p), text: nm[quad(p)] }), opts.action ? opts.action(p, quad(p)) : null)));
      foot.replaceChildren();
      if (opts.actions) {
        foot.append(h('div', { class: 'quad-acts' }, ['fast_right', 'slow_right', 'fast_wrong', 'slow_wrong'].map(k => {
          const a = typeof opts.actions === 'function' ? opts.actions(k, counts[k] || 0) : opts.actions[k];
          if (!a) return null;
          const btn = a instanceof Node ? a : h(a.href ? 'a' : 'button', { class: 'btn sm', href: a.href || null, type: a.href ? null : 'button',
            disabled: !a.href && !(counts[k] || 0) || null, onclick: a.onClick ? () => a.onClick(P.filter(p => quad(p) === k)) : null }, a.label);
          return h('div', { class: 'quad-act', 'data-q': k }, h('span', { class: 'quad-an' }, nm[k], h('b', { text: String(counts[k] || 0) })), btn);
        })));
      }
    }
    function views() {
      ctl.replaceChildren();
      const on = opts.list !== false && phone() && UI.seg;
      ctl.hidden = !on;
      if (!on) { view = 'chart'; plot.hidden = false; list.hidden = true; return; }
      UI.seg(ctl, [{ value: 'chart', label: 'Chart' }, { value: 'list', label: 'List' }], { value: view, label: 'View', onChange: v => { view = v; plot.hidden = v !== 'chart'; list.hidden = v !== 'list'; if (v === 'chart') sz.redraw(); } });
      plot.hidden = view !== 'chart'; list.hidden = view !== 'list';
    }
    const sz = sized(plot, draw);
    let wasPhone = phone();
    addEventListener('resize', () => { if (phone() !== wasPhone) { wasPhone = phone(); views(); } });
    function set(p, o2) { if (o2) Object.assign(opts, o2); if (p) P = p.map(x => ({ ...x, x: +x.x, y: +x.y })).filter(x => isNum(x.x) && isNum(x.y)); views(); sz.redraw(); }
    set(points || []);
    return { el, set, update: set };
  }

  /* ============================================================ UI.spark */
  function spark(host, series, o = {}) {
    const v = (series || []).map(x => (typeof x === 'object' && x ? +(x.value ?? x.y) : +x)).filter(isNum);
    const labels = (series || []).map((x, i) => (typeof x === 'object' && x && (x.day || x.label) ? (x.day ? fdate(x.day) : x.label) : `#${i + 1}`));
    const w = o.w ?? 60, hh = o.h ?? 20, f = o.format || fnum;
    const summary = v.length ? `${o.label || 'Trend'}: ${f(v[0])} to ${f(v[v.length - 1])} over ${o.noun ? `${fnum(v.length)} ${o.noun}` : plural(v.length, 'point')}; low ${f(Math.min(...v))}, high ${f(Math.max(...v))}.` : `${o.label || 'Trend'}: nothing yet.`;
    const el = h('span', { class: 'spark' });
    const s = sv('svg', { viewBox: `0 0 ${w} ${hh}`, width: w, height: hh, role: 'img', 'aria-label': summary, focusable: 'false' }, el);
    if (v.length > 1) {
      const lo = Math.min(...v, isNum(+o.ref) ? +o.ref : Infinity), hi = Math.max(...v, isNum(+o.ref) ? +o.ref : -Infinity), span = hi - lo || 1;
      const yy = x => hh - 2 - (x - lo) / span * (hh - 4);
      if (isNum(+o.ref) && o.ref !== null) sv('line', { x1: 0, x2: w, y1: r1(yy(+o.ref)), y2: r1(yy(+o.ref)), class: 'ch-grid-l' }, s);
      const pts = v.map((x, i) => `${r1(1.5 + i / (v.length - 1) * (w - 3))},${r1(yy(x))}`);
      sv('polyline', { points: pts.join(' '), class: 'spark-l' }, s);
      const [lx, ly] = pts[pts.length - 1].split(',');
      sv('circle', { cx: lx, cy: ly, r: 1.8, class: 'spark-d' }, s);
    }
    el.append(dataTable(summary, [o.rowLabel || 'Point', o.label || 'Value'], v.map((x, i) => [labels[i], f(x)])));
    return put(host, el);
  }

  /* ============================================================ UI.stackBar */
  function stackBar(host, segments, o = {}) {
    const el = h('figure', { class: 'chart stackbar' + (o.className ? ' ' + o.className : '') });
    put(host, el);
    const opts = { approx: false, ...o };
    const fmt = v => (opts.format ? opts.format(v) : `${opts.approx ? '≈ ' : ''}${fnum(v)}${opts.unit ? ` ${opts.unit}` : ''}`);
    function draw(list) {
      const segs = (list || []).map((s, i) => ({ ...s, key: s.key ?? i, value: Math.max(0, n0(s.value ?? s.pts)) }));
      const total = opts.total ?? sum(segs.map(s => s.value));
      const on = segs.filter(s => s.value > 0);
      const top = opts.largest === false ? null : on.reduce((m, s) => (!m || s.value > m.value ? s : m), null);
      const lab = s => `${s.label} ${fmt(s.value)}${isNum(+s.n) && s.n !== null ? ` (${fnum(s.n)})` : ''}`;
      const tipOf = s => s.tip || [s.label, isNum(+s.n) && s.n !== null && `${fnum(s.n)} ${opts.noun || 'misses'}`, fmt(s.value), total ? `${Math.round(s.value / total * 100)}%` : ''].filter(Boolean).join(' · ');
      let shade = 0;
      const bar = h('div', { class: 'sb-bar', role: 'img' }, on.map(s => {
        const d = h('span', { class: 'sb-seg' + (s === top ? ' top' : '') + (s.hatch ? ' hatch' : ''), 'data-shade': s === top || s.hatch ? null : String(shade++ % 5), 'data-k': String(s.key), style: `flex-grow:${s.value}` },
          h('span', { class: 'sb-l', text: lab(s) }));
        return d;
      }));
      if (!on.length) bar.append(h('span', { class: 'sb-seg empty', style: 'flex-grow:1' }));
      const summary = on.length ? `${opts.label || 'Split'}${total ? `, ${fmt(total)} in all` : ''}: ${segs.map(s => `${lab(s)}${total ? `, ${Math.round(s.value / total * 100)}%` : ''}`).join('; ')}.`
        : `${opts.label || 'Split'}: nothing yet.`;
      bar.setAttribute('aria-label', summary);
      const wrap = h('div', { class: 'sb-wrap' }, bar);
      if (opts.onPick && on.length) {
        const hits = h('div', { class: 'sb-hits', role: 'group', 'aria-label': opts.label || 'Segments' }, on.map((s, i) => {
          const b = h('button', { type: 'button', class: 'sb-hit', style: `flex-grow:${s.value}`, 'aria-label': tipOf(s), tabindex: i ? '-1' : '0' });
          if (UI.tooltip) UI.tooltip(b, tipOf(s), { delay: 60 });
          b.addEventListener('click', () => opts.onPick(s));
          return b;
        }));
        hits.addEventListener('keydown', e => {
          const bs = [...hits.children], i = bs.indexOf(doc.activeElement);
          const k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
          if (i < 0 || !k) return;
          e.preventDefault();
          const j = clamp(i + k, 0, bs.length - 1);
          bs.forEach((b, m) => { b.tabIndex = m === j ? 0 : -1; });
          bs[j].focus();
        });
        wrap.append(hits);
      }
      let sh = 0;
      const key = opts.legend === false ? null : h('ul', { class: 'legend chart-key sb-key', 'aria-label': 'Legend' }, segs.map(s => {
        const sw = h('i', { class: 'sb-sw' + (s === top ? ' top' : '') + (s.hatch ? ' hatch' : ''), 'data-shade': s === top || s.hatch || !s.value ? null : String(sh++ % 5), 'aria-hidden': 'true' });
        return h('li', { class: s.value ? null : 'off', 'data-k': String(s.key) }, sw, h('span', { text: s.label }), h('b', { text: fmt(s.value) }),
          isNum(+s.n) && s.n !== null ? h('span', { class: 'sb-n', text: `(${fnum(s.n)})` }) : null);
      }));
      el.replaceChildren(wrap, on.length ? '' : emptyBlock(opts.empty, 'Nothing counted yet.'), segs.length ? key || '' : '', dataTable(summary, ['Part', opts.valueLabel || 'Value', opts.noun ? cap1(opts.noun) : 'Count', 'Share'],
        segs.map(s => [s.label, fmt(s.value), isNum(+s.n) && s.n !== null ? fnum(s.n) : '', total ? `${Math.round(s.value / total * 100)}%` : ''])));
      requestAnimationFrame(fit);
    }
    // a label that doesn't fit its segment is left to the legend, never clipped
    function fit() {
      el.querySelectorAll('.sb-seg').forEach(s => { const l = s.firstChild; if (l) l.classList.toggle('hide', l.scrollWidth > s.clientWidth - 12); });
      // legend: 'auto' keeps only the parts whose label doesn't show in the bar (a legend repeating the bar said each number twice)
      if (opts.legend !== 'auto') return;
      const key = el.querySelector('.sb-key');
      if (!key) return;
      const segs = [...el.querySelectorAll('.sb-seg:not(.empty)')];
      const lis = [...key.children];
      lis.forEach(li => { const sg = segs.find(x => x.dataset.k === li.dataset.k); const l = sg && sg.firstChild; li.hidden = !!(l && getComputedStyle(l).visibility !== 'hidden'); });
      key.hidden = lis.every(li => li.hidden);
    }
    if (window.ResizeObserver) new ResizeObserver(() => requestAnimationFrame(fit)).observe(el);
    draw(segments);
    return { el, set(list, o2) { if (o2) Object.assign(opts, o2); draw(list); } };
  }
  const cap1 = t => (t ? t[0].toUpperCase() + t.slice(1) : t);

  /* ============================================================ UI.clockLane */
  function clockLane(host, visits, o = {}) {
    const { el, plot } = frame(host, 'clock-lane', o);
    const opts = { duration: 2100000, ...o };
    let V = [];
    const foot = h('div', { class: 'chart-foot' });
    el.append(foot);
    const ord = n => `${n}${n % 10 === 1 && n % 100 !== 11 ? 'st' : n % 10 === 2 && n % 100 !== 12 ? 'nd' : n % 10 === 3 && n % 100 !== 13 ? 'rd' : 'th'}`;
    function draw(W) {
      const vert = phone() && opts.vertical !== false;
      const items = opts.items || {};
      const dur = opts.duration;
      // along the clock (u) and across the lanes (v)
      const U0 = vert ? 14 : 8, Ulen = vert ? Math.max(360, Math.min(560, dur / 60000 * 14)) : W - 16;
      const lanes = { first: [20, 26], again: [50, 16], pace: [70, 8] }, Vlen = 104;
      const Wd = vert ? W : W, Hd = vert ? Ulen + U0 + 14 : Vlen;
      const u = t => U0 + clamp(t / dur, 0, 1) * (Ulen - (vert ? 0 : 0));
      const vOff = vert ? Math.max(0, (W - Vlen) / 2) + 34 : 0;
      const rect = (ua, va, du, dv, attrs, parent) => sv('rect', vert ? { x: r1(va + vOff), y: r1(ua), width: r1(dv), height: r1(du), ...attrs } : { x: r1(ua), y: r1(va), width: r1(du), height: r1(dv), ...attrs }, parent);
      const line = (ua, va, ub, vb, attrs, parent) => sv('line', vert ? { x1: r1(va + vOff), y1: r1(ua), x2: r1(vb + vOff), y2: r1(ub), ...attrs } : { x1: r1(ua), y1: r1(va), x2: r1(ub), y2: r1(vb), ...attrs }, parent);
      const label = (ua, va, text, attrs, parent) => tx(parent, vert ? va + vOff : ua, vert ? ua : va, text, attrs);
      const svg = svgRoot(Wd, Hd, '');
      const hf = hatch(svg);
      // the time axis every 5 minutes
      for (let t = 0; t <= dur; t += 300000) {
        line(u(t), 16, u(t), 80, { class: 'ch-grid-l' }, svg);
        label(u(t), vert ? -4 : 96, fmmss(t / 1000), { 'text-anchor': vert ? 'end' : t === 0 ? 'start' : t + 300000 > dur ? 'end' : 'middle', class: 'ch-xtick', dy: vert ? '3' : null }, svg);
      }
      rect(u(0), lanes.first[0], u(dur) - u(0), lanes.first[1], { class: 'ch-lane', rx: 4 }, svg);
      rect(u(0), lanes.again[0], u(dur) - u(0), lanes.again[1], { class: 'ch-lane', rx: 4 }, svg);
      // visits: first visits on the top lane, revisits under it, fill = the final status
      const seen = {}, blocks = [];
      V.forEach(([q, a, b]) => {
        seen[q] = (seen[q] || 0) + 1;
        const lane = seen[q] === 1 ? lanes.first : lanes.again;
        const it = items[q] || {};
        const du = Math.max(1.5, u(b) - u(a) - 1);
        rect(u(a) + .5, lane[0], du, lane[1], { class: 'ch-bar ch-st', 'data-status': it.status || 'answered', rx: 2 }, svg);
        blocks.push({ q, a, b, nth: seen[q], lane, it });
      });
      // the even pace: where each question's budget would have put you, shaded ahead or behind
      const order = opts.order || (Object.keys(items).length ? Object.keys(items) : [...new Set(V.map(v => v[0]))]);
      const budgets = opts.budgets || {};
      let acc = 0, behindAt = null;
      const firstIn = {};
      V.forEach(([q, a]) => { if (firstIn[q] === undefined) firstIn[q] = a; });
      order.forEach((q, k) => {
        const plan = acc, bud = n0(budgets[q] ?? (dur / Math.max(order.length, 1)));
        acc += bud;
        line(u(plan), lanes.pace[0] - 2, u(plan), lanes.pace[0] + lanes.pace[1] + 2, { class: 'ch-pace-t' }, svg);
        const act = firstIn[q];
        if (act === undefined) return;
        if (Math.abs(act - plan) > 1000) {
          const behind = act > plan;
          const e = rect(u(Math.min(act, plan)), lanes.pace[0], Math.abs(u(act) - u(plan)), lanes.pace[1], { class: behind ? 'ch-behind' : 'ch-ahead' }, svg);
          if (behind) e.setAttribute('fill', hf);
          if (behind && behindAt === null && act - plan > 60000) behindAt = { q, k, by: act - plan };
        }
      });
      line(u(0), lanes.pace[0] + lanes.pace[1] / 2, u(Math.min(acc, dur)), lanes.pace[0] + lanes.pace[1] / 2, { class: 'ch-pace' }, svg);
      // marks: flags, answer changes, the clock's end
      (opts.marks || []).forEach(m => {
        if (m.kind === 'flag') sv('path', vert ? { d: `M${r1(lanes.first[0] + vOff - 2)} ${r1(u(m.t))} l-6 -3 v6 Z`, class: 'ch-flag' } : { d: `M${r1(u(m.t))} ${lanes.first[0] - 2} l3 -6 h-6 Z`, class: 'ch-flag' }, svg);
        else if (m.kind === 'change') label(u(m.t), vert ? lanes.first[0] - 10 : lanes.first[0] - 4, '↺', { 'text-anchor': 'middle', class: 'ch-glyph' }, svg);
        else if (m.kind === 'end') line(u(m.t ?? dur), 12, u(m.t ?? dur), 82, { class: 'ch-exam' }, svg);
      });
      if (!vert) {
        // the lane names keep clear of the marks above the lane and of the revisits in theirs
        const f0 = lanes.first[0], a0 = lanes.again[0];
        const mk = (opts.marks || []).map(m => { const x = u(m.kind === 'end' ? m.t ?? dur : m.t); return m.kind === 'end' ? [x - 1, 12, x + 1, 82] : [x - 5, f0 - 13, x + 5, f0 - 1]; });
        const firstAt = clearOf([[u(0), 12, 'start'], ...mk.map(b => [b[2] + 6, 12, 'start']).sort((a, b) => a[0] - b[0]), [u(dur), 12, 'end']], 'First visits', mk) || [u(0), 12, 'start'];
        tx(svg, firstAt[0], firstAt[1], 'First visits', { 'text-anchor': firstAt[2], class: 'ch-lab' });
        const again = blocks.filter(b => b.nth > 1).map(b => [u(b.a), a0, u(b.b), a0 + lanes.again[1]]);
        const againAt = clearOf([[u(0) + 2, a0 + 11, 'start'], [u(dur) - 2, a0 + 11, 'end']], 'Again', again) || [u(0) + 2, a0 + 11, 'start'];
        tx(svg, againAt[0], againAt[1], 'Again', { 'text-anchor': againAt[2], class: 'ch-lab' });
      }
      const used = V.length ? Math.max(...V.map(v => v[2])) : 0;
      const qn = new Set(V.map(v => v[0])).size;
      const revisits = V.length - qn;
      const nameOf = q => (items[q] && items[q].label) || q;
      const summary = V.length ? `${opts.label || 'Clock replay'}: ${plural(qn, 'question')} in ${plural(V.length, 'visit')} (${revisits} revisit${revisits === 1 ? '' : 's'}), ${fmmss(used / 1000)} of ${fmmss(dur / 1000)} used${behindAt ? `; first more than a minute behind pace at ${nameOf(behindAt.q)}, by ${fmmss(behindAt.by / 1000)}` : ''}.` : `${opts.label || 'Clock replay'}: visit order was not recorded for this sitting.`;
      svg.setAttribute('aria-label', summary);
      const old = plot.querySelector(':scope > svg');
      if (old) old.replaceWith(svg); else plot.prepend(svg);
      emptyNote(plot, V.length ? null : (opts.empty || {}), 'Visit order was not recorded for this sitting.');
      const tipOf = b => b.it.tip || [nameOf(b.q), fmmss((b.b - b.a) / 1000), `${ord(b.nth)} visit`, b.nth === Math.max(...blocks.filter(x => x.q === b.q).map(x => x.nth)) && b.it.changed && `changed ${b.it.changed}`, b.it.status && labelOf(b.it.status)].filter(Boolean).join(' · ');
      hitLayer(plot, blocks.map(b => {
        const ua = u(b.a), du = Math.max(10, u(b.b) - u(b.a));
        const box = vert ? { x: b.lane[0] + vOff - 4, y: ua, w: b.lane[1] + 8, h: du } : { x: ua, y: b.lane[0] - 4, w: du, h: b.lane[1] + 8 };
        return { ...box, label: tipOf(b), tip: tipOf(b), pick: opts.onPick ? () => opts.onPick(b.q) : null };
      }), { label: 'Visits', start: 0 });
      setTable(el, dataTable(summary, ['Visit', 'Question', 'From', 'To', 'Time', 'Status'],
        blocks.map((b, i) => [i + 1, `${nameOf(b.q)}${b.nth > 1 ? ` (${ord(b.nth)} visit)` : ''}`, fmmss(b.a / 1000), fmmss(b.b / 1000), fmmss((b.b - b.a) / 1000), labelOf(b.it.status) + (b.it.changed ? `, changed ${b.it.changed}` : '')])));
      foot.replaceChildren(V.length ? chartKey([{ key: 'pace', label: 'Even pace' }, { key: 'bar-hatch', label: 'Behind pace' }, { swatch: aheadSw(), label: 'Ahead of pace' }, (opts.marks || []).some(m => m.kind === 'change') && { swatch: txtSw('↺'), label: 'Answer changed' }]) : '');
    }
    const aheadSw = () => { const s = sv('svg', { class: 'ch-key', width: 18, height: 12, viewBox: '0 0 18 12', 'aria-hidden': 'true' }); sv('rect', { x: 1, y: 3, width: 16, height: 6, class: 'ch-ahead' }, s); return s; };
    const txtSw = t => h('span', { class: 'ch-key-t', 'aria-hidden': 'true', text: t });
    const sz = sized(plot, draw);
    function set(v, o2) { if (o2) Object.assign(opts, o2); if (v) V = v.map(x => (Array.isArray(x) ? [String(x[0]), +x[1], +x[2]] : [String(x.qid), +(x.in ?? x.t_in), +(x.out ?? x.t_out)])).filter(x => isNum(x[1]) && isNum(x[2])); sz.redraw(); }
    let wasPhone = phone();
    addEventListener('resize', () => { if (phone() !== wasPhone) { wasPhone = phone(); sz.redraw(); } });
    set(visits || []);
    return { el, set, update: set };
  }

  /* ============================================================ UI.dotStrip */
  function dotStrip(host, counts, o = {}) {
    const { el, plot } = frame(host, 'dot-strip', o);
    const opts = { min: 200, bin: 20, ...o };
    let C = [];
    function draw(W) {
      const lo = opts.min, bin = opts.bin, hi = lo + bin * C.length;
      const L = 8, R = 8, B = 22;
      const plotW = W - L - R, colW = plotW / Math.max(C.length, 1);
      const mx = Math.max(1, ...C);
      const r = clamp(Math.min(colW / 2.6, 84 / (mx * 2.3)), 1.1, 3.2), stepV = r * 2.3;
      const H = Math.max(40, Math.ceil(mx * stepV) + 14) + B;
      const xOf = v => L + (clamp(v, lo, hi) - lo) / (hi - lo) * plotW;
      const svg = svgRoot(W, H, '');
      const band = opts.band && isNum(+opts.band.low) ? opts.band : null;
      if (band) sv('rect', { x: r1(xOf(band.low)), width: r1(Math.max(2, xOf(band.high) - xOf(band.low))), y: 4, height: H - B - 4, class: 'ch-zone', rx: 3 }, svg);
      C.forEach((c, i) => {
        const cx = L + colW * (i + .5), mid = lo + bin * (i + .5);
        const inBand = band && mid >= band.low && mid <= band.high;
        for (let k = 0; k < c; k++) sv('circle', { cx: r1(cx), cy: r1(H - B - r - 2 - k * stepV), r: r1(r), class: 'ds-dot' + (inBand ? ' in' : '') }, svg);
      });
      sv('line', { x1: L, x2: W - R, y1: H - B, y2: H - B, class: 'ch-base' }, svg);
      for (let v = lo; v <= hi; v += 200) tx(svg, xOf(v), H - 6, v, { 'text-anchor': v === lo ? 'start' : v === hi ? 'end' : 'middle', class: 'ch-xtick' });
      if (isNum(+opts.avg) && opts.avg !== null) sv('line', { x1: r1(xOf(opts.avg)), x2: r1(xOf(opts.avg)), y1: 4, y2: H - B, class: 'ch-pace' }, svg);
      if (isNum(+opts.you) && opts.you !== null) {
        const x = xOf(opts.you);
        sv('path', { d: `M${r1(x)} ${H - B + 1} l-5 7 h10 Z`, class: 'ds-you' }, svg);
        tx(svg, x, 11, 'You', { 'text-anchor': x < 30 ? 'start' : x > W - 30 ? 'end' : 'middle', class: 'ch-lab' });
      }
      const total = sum(C);
      const below = isNum(+opts.you) ? sum(C.filter((c, i) => lo + bin * (i + 1) <= +opts.you + 1e-9)) + (() => { const i = Math.floor((+opts.you - lo) / bin); return i >= 0 && i < C.length ? Math.round(C[i] * ((+opts.you - (lo + bin * i)) / bin)) : 0; })() : null;
      const summary = `${opts.label || 'First sittings’ middles'}: ${fnum(total)} ${opts.noun || 'sittings'} in ${bin}-point groups from ${lo} to ${hi}${band ? `; your band ${fband(band.low, band.high)}` : ''}${below !== null && total ? `; about ${Math.round(below / total * 100)}% sit at or below your middle ${Math.round(opts.you)}` : ''}${isNum(+opts.avg) && opts.avg !== null ? `; average ${Math.round(opts.avg)}` : ''}.`;
      svg.setAttribute('aria-label', summary);
      const old = plot.querySelector(':scope > svg');
      if (old) old.replaceWith(svg); else plot.prepend(svg);
      setTable(el, dataTable(summary, ['Middle', opts.noun ? cap1(opts.noun) : 'Sittings'], C.map((c, i) => [`${lo + bin * i}–${lo + bin * (i + 1) - 1}`, c])));
    }
    const sz = sized(plot, draw);
    function set(c, o2) { if (o2) Object.assign(opts, o2); if (c) C = (Array.isArray(c) ? c : c.counts || []).map(n0); sz.redraw(); }
    set(counts || []);
    return { el, set, update: set };
  }

  /* ------------------------------------------------------------ export */
  Object.assign(UI, {
    bandChart, trend: bandChart, scoreChart: bandChart, gauge, scale, barChart,
    calendar, monthGrid: calendar, heatmap, lineChart, spread,
    quadrant, spark, stackBar, clockLane, dotStrip,
  });
})();
