/* ------------------------------------------------------------ topic glyphs and spot drawings
   (premium build A3, 2026-10-19; ICONS.md 7 and 9). For ui.js, which owns s(), poly() and CORNER.

   SHAPES: drop-in for ui.js's `const SHAPES = {...}` (same shape: SHAPES[name] = g => draws into g with
   s(tag, attrs, parent)). The grid is now 24 units centred on 0, live area +-9 like the icons, so glyph()
   sets viewBox "-12 -12 24 24" (was "-13 -13 26 26"). Classes: .stk closed shape, .stkl line, .stki
   secondary (axes, risers, pans: --faint at full width), .stkb the bold part, .stkd dot. Widths and colours
   come from icons.css (1.4px, held in screen pixels): no stroke-width attributes here (bug 1), and no
   --gb sticker fill, so nothing shows a pale box inside a selected chip (bug 4).
   Kept and re-weighed (12): percent bars die right cross balance cube curveline parabola scatter angle
   (arc now primary) dotcircle (radius added). Redrawn (7): numberline ray errorbar equiv magnifier
   graphline slope. */
const SHAPES = {
  // a number line with taller ticks; the solution dot sits on the middle tick
  numberline: g => { s('path', { class: 'stkl', d: 'M-9 0 H9 M-6 -3.5 V3.5 M0 -3.5 V3.5 M6 -3.5 V3.5' }, g); s('circle', { class: 'stkd', cx: 0, cy: 0, r: 2.3 }, g); },
  // two marked points on the axes (the intercepts) and the line through them
  graphline:  g => { s('path', { class: 'stki', d: 'M-9 5 H9 M-5 -9 V9' }, g); s('path', { class: 'stkl', d: 'M-8 -6 L6 8' }, g); s('circle', { class: 'stkd', cx: -5, cy: -3, r: 1.9 }, g); s('circle', { class: 'stkd', cx: 3, cy: 5, r: 1.9 }, g); },
  // the line with its rise and run
  slope:      g => { s('path', { class: 'stkl', d: 'M-7.7 6 L7.7 -6' }, g); s('path', { class: 'stki', d: 'M-2.6 2 H3.9 V-3' }, g); },
  cross:      g => { s('path', { class: 'stkl', d: 'M-7.7 -5.1 L7.7 6.9 M-7.7 6.9 L7.7 -5.1' }, g); s('circle', { class: 'stkd', cx: 0, cy: .9, r: 2.1 }, g); },
  // closed dot, the bold solution ray, an arrowhead; the rest of the line faint
  ray:        g => { s('path', { class: 'stki', d: 'M-9 0 H-3.5' }, g); s('path', { class: 'stkb', d: 'M-3.5 0 H8 M4.5 -3.5 L8 0 L4.5 3.5' }, g); s('circle', { class: 'stkd', cx: -3.5, cy: 0, r: 2.4 }, g); },
  // an equals sign whose lower bar is split: the same value in another form
  equiv:      g => s('path', { class: 'stkl', d: 'M-7 -3 H7 M-7 3 H-1.5 M1.5 3 H7' }, g),
  curveline:  g => { s('path', { class: 'stkl', d: 'M-7.7 6.9 Q0 -12 7.7 6.9' }, g); s('path', { class: 'stkl', d: 'M-8.6 .9 H8.6' }, g); s('circle', { class: 'stkd', cx: -4.6, cy: .9, r: 1.8 }, g); s('circle', { class: 'stkd', cx: 4.6, cy: .9, r: 1.8 }, g); },
  parabola:   g => { s('path', { class: 'stki', d: 'M-7.7 5.1 H7.7 M0 7.7 V-7.7' }, g); s('path', { class: 'stkl', d: 'M-6.9 -6.9 Q0 12 6.9 -6.9' }, g); },
  balance:    g => { s('path', { class: 'stkl', d: 'M0 -6.9 V6.9 M-6.9 -4.3 H6.9 M-4.3 7.7 H4.3' }, g); s('path', { class: 'stki', d: 'M-6.9 -4.3 L-9 .9 M-6.9 -4.3 L-4.7 .9 M6.9 -4.3 L9 .9 M6.9 -4.3 L4.7 .9 M-9.4 1.3 H-4.3 M4.3 1.3 H9.4' }, g); },
  percent:    g => { s('circle', { class: 'stk', cx: -4.3, cy: -4.3, r: 2.6 }, g); s('circle', { class: 'stk', cx: 4.3, cy: 4.3, r: 2.6 }, g); s('path', { class: 'stkl', d: 'M-6.9 7.7 L6.9 -7.7' }, g); },
  bars:       g => { s('rect', { class: 'stk', x: -7.7, y: .9, width: 4.3, height: 6.9 }, g); s('rect', { class: 'stk', x: -2.1, y: -5.1, width: 4.3, height: 12.9 }, g); s('rect', { class: 'stk', x: 3.4, y: -1.7, width: 4.3, height: 9.4 }, g); s('path', { class: 'stki', d: 'M-9.4 8.1 H9.4' }, g); },
  scatter:    g => { s('path', { class: 'stki', d: 'M-7.7 6.9 H7.7 M-7.7 6.9 V-7.7' }, g); s('path', { class: 'stki', d: 'M-6.9 5.1 L6.9 -5.1' }, g); [[-4.3, 3.4], [-1.7, 1.3], [.9, -.4], [2.6, -3.4], [5.1, -2.1]].forEach(([x, y]) => s('circle', { class: 'stkd', cx: x, cy: y, r: 1.5 }, g)); },
  die:        g => { s('rect', { class: 'stk', x: -7.7, y: -7.7, width: 15.4, height: 15.4, rx: 2.6 }, g); [[-3.9, -3.9], [0, 0], [3.9, 3.9]].forEach(([x, y]) => s('circle', { class: 'stkd', cx: x, cy: y, r: 1.5 }, g)); },
  // a vertical interval with caps over a short baseline (no longer a twin of numberline and ray)
  errorbar:   g => { s('path', { class: 'stki', d: 'M-6 8 H6' }, g); s('path', { class: 'stkl', d: 'M0 -7 V4 M-3 -7 H3 M-3 4 H3' }, g); s('circle', { class: 'stkd', cx: 0, cy: -1.5, r: 2.3 }, g); },
  // a speech bubble holding two bars: a claim about data (no longer the search icon)
  magnifier:  g => { s('path', { class: 'stk', d: 'M-6 -7.5 H6 A2.5 2.5 0 0 1 8.5 -5 V2 A2.5 2.5 0 0 1 6 4.5 H-1 L-5 8.5 V4.5 H-6 A2.5 2.5 0 0 1 -8.5 2 V-5 A2.5 2.5 0 0 1 -6 -7.5 Z' }, g); s('path', { class: 'stkl', d: 'M-2.5 1.5 V-1 M2.5 1.5 V-4' }, g); },
  cube:       g => { s('polygon', { class: 'stk', points: poly(6, 9, -90) }, g); s('path', { class: 'stki', d: 'M0 0 V9 M0 0 L-7.8 -4.5 M0 0 L7.8 -4.5' }, g); },
  angle:      g => { s('path', { class: 'stk', d: 'M-7.7 6.9 L1.7 -7.7 L7.7 6.9 Z' }, g); s('path', { class: 'stkl', d: 'M-1.1 -3.4 A5.1 5.1 0 0 0 3.7 -3' }, g); },
  right:      g => { s('polygon', { class: 'stk', points: '-7.7,7.7 7.7,7.7 7.7,-7.7' }, g); s('path', { class: 'stki', d: 'M7.7 4.3 h-3.4 v3.4' }, g); },
  dotcircle:  g => { s('circle', { class: 'stk', r: 8.1 }, g); s('path', { class: 'stkl', d: 'M0 0 L5.7 -5.7' }, g); s('circle', { class: 'stkd', r: 1.6 }, g); },
};

/* SPOT: the mark's four corners as the only illustration (ICONS.md 9). UI.spot(kind[, ms]) returns an svg
   string; icons.css sizes it (72px, 56px on phones), outlines in --faint at the icon weight, one piece amber.
   Corners: 0 top-left, 1 top-right, 2 bottom-right, 3 bottom-left (CORNER rotated 0/90/180/270).
   Never in sheets, popovers, filtered empties ("No X match these filters": one line plus Clear) or print. */
const corner = (i, cls, extra = '') => `<path class="${cls}" d="${CORNER}"${i ? ` transform="rotate(${i * 90} 50 50)"` : ''}${extra}/>`;
const spotSvg = (kind, inner, box = '0 0 100 100') => `<svg class="spot spot-${kind}" viewBox="${box}" aria-hidden="true" focusable="false">${inner}</svg>`;
const SPOT = {
  // first use (empty lists before any data): words/index.html, tests.js, me.js, plan.js, compete/overview.js
  start: spotSvg('start', [0, 1, 2].map(i => corner(i, 'sp-o')).join('') + corner(3, 'sp-on')),
  // all clear (nothing due, every mistake fixed, the day done): review.js, results/page.js, words-ui.js, Today
  clear: spotSvg('clear', [0, 1, 2, 3].map(i => corner(i, 'sp-on')).join('')),
  // 404: the corners drifted apart and slightly turned (404.html)
  lost: spotSvg('lost', [[-4, -4, -6, 26, 26], [4, -4, 4, 74, 26], [4, 4, -3, 74, 74], [-4, 4, 8, 26, 74]].map(([dx, dy, t, cx, cy], i) =>
    `<g transform="translate(${dx} ${dy}) rotate(${t} ${cx} ${cy})">${corner(i, i === 3 ? 'sp-on' : 'sp-o')}</g>`).join(''), '-8 -8 116 116'),
};
/* set done (runner summary) and test done (test.js finished): the living mark filling to the new mastery,
   corners in turn (icons.css: 240ms each, 40ms apart), only after the student's action. ms: the four
   domains' mastery in kit's livingMark order (Algebra, Advanced Math, PSDA, Geometry), already divided by
   its STRONG, so 0..1. Same geometry as livingMark; kit may call this instead of keeping its own. */
let spotN = 0;
SPOT.done = ms => {
  const id = `spot${++spotN}`;
  return spotSvg('done', [ms[0], ms[1], ms[3], ms[2]].map((m, i) => {
    const r = (7 + Math.min(1, Math.max(0, m || 0)) * 53).toFixed(1);
    return `<clipPath id="${id}-${i}"><circle cx="50" cy="50" r="${r}"/></clipPath>` + corner(i, 'sp-o') +
      (m > 0 ? corner(i, 'sp-on sp-in', ` clip-path="url(#${id}-${i})" style="--i:${i}"`) : '');
  }).join(''));
};
const spot = (kind, ms) => (kind === 'done' ? SPOT.done(ms || [0, 0, 0, 0]) : SPOT[kind] || '');
