/* ============================================================================
   SAT Freshman -- shared by every page

   The shell (top bar, phone tabs), the API client, the nineteen topics with
   their glyphs, and one question renderer used by practice, the question of
   the day and every review. A page declares itself with <body data-page="...">
   and calls UI.shell().
   ========================================================================== */

(() => {
  'use strict';

  /* ------------------------------------------------------------ identity
     A learner is a token in this browser. It is the same key the sticker
     sheet used, so anyone who practised there keeps their history. */
  const LEARNER_KEY = 'satf.learner';
  let memo = null;
  function learner() {
    if (memo) return memo;
    try {
      memo = localStorage.getItem(LEARNER_KEY);
      if (!memo) {
        memo = 'a:' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
        localStorage.setItem(LEARNER_KEY, memo);
      }
    } catch (_) {
      memo = memo || 'a:' + Math.random().toString(36).slice(2, 12);   // private window: this tab only
    }
    return memo;
  }
  function useLearner(token) {
    memo = token;
    try { localStorage.setItem(LEARNER_KEY, token); } catch (_) {}
  }

  /* ------------------------------------------------------------ the API */
  async function api(path, { method = 'GET', body } = {}) {
    const r = await fetch('/api' + path, {
      method,
      headers: {
        'content-type': 'application/json',
        'X-Learner': learner(),
        'X-Tz': String(new Date().getTimezoneOffset()),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    let data = null;
    try { data = await r.json(); } catch (_) {}
    if (!r.ok) {
      const d = data && data.detail;
      const e = new Error(typeof d === 'string' ? d : (d ? JSON.stringify(d) : `HTTP ${r.status}`));
      e.status = r.status;
      e.data = data;
      throw e;
    }
    return data;
  }

  /* ------------------------------------------------------------ dom */
  const $ = (sel, root = document) => root.querySelector(sel);
  const NS = 'http://www.w3.org/2000/svg';
  function h(tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat()) if (k !== null && k !== undefined && k !== false) e.append(k);
    return e;
  }
  function s(tag, attrs = {}, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  const svg = (inner, size = 24, cls = '') =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"${cls ? ` class="${cls}"` : ''}>${inner}</svg>`;
  const L = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"';

  /* ------------------------------------------------------------ the mark
     A rounded square with four gaps cut mid-edge: one corner, rotated. */
  const CORNER = 'M45 8 H30 A22 22 0 0 0 8 30 V45 H34 V41 A7 7 0 0 1 41 34 H45 Z';
  const mark = (size = 26, fill = '#F18508') =>
    `<svg width="${size}" height="${size}" viewBox="0 0 100 100" role="img" aria-label="SAT Freshman"><g fill="${fill}">${
      [0, 90, 180, 270].map(a => `<path d="${CORNER}"${a ? ` transform="rotate(${a} 50 50)"` : ''}/>`).join('')}</g></svg>`;

  /* ------------------------------------------------------------ icons */
  const ICON = {
    today:    `<rect x="4" y="5" width="16" height="15" rx="3" ${L}/><path d="M4 10h16" ${L}/><circle cx="12" cy="15" r="1.7" fill="currentColor"/>`,
    practice: `<rect x="4" y="4" width="7" height="7" rx="2" ${L}/><rect x="13" y="4" width="7" height="7" rx="2" ${L}/><rect x="4" y="13" width="7" height="7" rx="2" ${L}/><rect x="13" y="13" width="7" height="7" rx="2" ${L}/>`,
    tests:    `<path d="M6.5 3.5h8l4 4v13h-12z" ${L}/><path d="M14.5 3.5v4h4" ${L}/><path d="M9.5 12.5h5M9.5 16.5h5" ${L}/>`,
    plan:     `<circle cx="6" cy="18" r="2" ${L}/><circle cx="18" cy="6" r="2" ${L}/><path d="M8 18h6.5a3 3 0 0 0 0-6h-5a3 3 0 0 1 0-6H16" ${L}/>`,
    results:  `<path d="M5.5 20v-8M12 20V5M18.5 20v-5.5" ${L} stroke-width="1.9"/>`,
    flame:    `<path class="flame" d="M12 3.2c.9 2.9 4.6 4.6 4.6 9a4.6 4.6 0 0 1-9.2 0c0-2.1 1-3.5 2.2-4.5-.1 1.6.8 2.7 1.8 2.9-.5-3.2-.3-5.4.6-7.4z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>`,
    x:        `<path d="M6 6l12 12M18 6L6 18" ${L} stroke-width="1.7"/>`,
    calc:     `<rect x="5" y="3.5" width="14" height="17" rx="2.5" ${L}/><path d="M8.5 7.5h7" ${L}/><circle cx="9" cy="12" r=".9" fill="currentColor"/><circle cx="12" cy="12" r=".9" fill="currentColor"/><circle cx="15" cy="12" r=".9" fill="currentColor"/><circle cx="9" cy="15.5" r=".9" fill="currentColor"/><circle cx="12" cy="15.5" r=".9" fill="currentColor"/><circle cx="15" cy="15.5" r=".9" fill="currentColor"/>`,
    ref:      `<path d="M4.5 5.5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2h-6zM19.5 5.5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z" ${L}/>`,
    bookmark: `<path d="M7 4.5h10v15l-5-3.6-5 3.6z" ${L}/>`,
    clock:    `<circle cx="12" cy="13.6" r="7.3" ${L} stroke-width="1.5"/><path d="M9.8 3.2h4.4M12 3.2v3.1M18.2 6.9l1.2-1.2" ${L} stroke-width="1.5"/><path class="hand" d="M12 13.6V9.4" ${L}/>`,
    arrow:    `<path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5" ${L}/>`,
    trophy:   `<path d="M8 4.5h8v4a4 4 0 0 1-8 0zM8 6H5.5a2.5 2.5 0 0 0 2.6 3.5M16 6h2.5a2.5 2.5 0 0 1-2.6 3.5M12 12.5V16M8.5 19.5h7M9.5 19.5c0-2 1-3.5 2.5-3.5s2.5 1.5 2.5 3.5" ${L}/>`,
  };

  /* ------------------------------------------------------------ topics
     The nineteen SAT Math topics, in the bank's slugs, with the short name a
     tile has room for and the sticker glyph drawn for it. */
  const DOMAINS = [
    ['Algebra', 'Algebra'],
    ['Advanced Math', 'Advanced Math'],
    ['Problem-Solving and Data Analysis', 'Problem-Solving & Data'],
    ['Geometry and Trigonometry', 'Geometry & Trig'],
  ];
  const TOPICS = [
    ['linear_equations_in_one_variable', 'Linear equations', 'numberline', 0],
    ['linear_equations_in_two_variables', 'Two-variable equations', 'graphline', 0],
    ['linear_functions', 'Linear functions', 'slope', 0],
    ['systems_of_linear_equations', 'Systems of equations', 'cross', 0],
    ['linear_inequalities', 'Linear inequalities', 'ray', 0],
    ['equivalent_expressions', 'Equivalent expressions', 'equiv', 1],
    ['nonlinear_equations_and_systems', 'Nonlinear equations', 'curveline', 1],
    ['nonlinear_functions', 'Nonlinear functions', 'parabola', 1],
    ['ratios_rates_proportions_and_units', 'Ratios & rates', 'balance', 2],
    ['percentages', 'Percentages', 'percent', 2],
    ['one_variable_data', 'One-variable data', 'bars', 2],
    ['two_variable_data', 'Two-variable data', 'scatter', 2],
    ['probability', 'Probability', 'die', 2],
    ['sample_statistics_and_margin_of_error', 'Margin of error', 'errorbar', 2],
    ['evaluating_statistical_claims', 'Statistical claims', 'magnifier', 2],
    ['area_and_volume', 'Area & volume', 'cube', 3],
    ['lines_angles_and_triangles', 'Lines, angles & triangles', 'angle', 3],
    ['right_triangles_and_trigonometry', 'Right triangles & trig', 'right', 3],
    ['circles', 'Circles', 'dotcircle', 3],
  ].map(([slug, short, shape, d]) => ({ slug, short, shape, domain: DOMAINS[d][0], dshort: DOMAINS[d][1] }));
  const TOPIC = Object.fromEntries(TOPICS.map(t => [t.slug, t]));

  const poly = (n, r, rot = -90) => Array.from({ length: n }, (_, i) => {
    const a = (rot + i * 360 / n) * Math.PI / 180;
    return (r * Math.cos(a)).toFixed(2) + ',' + (r * Math.sin(a)).toFixed(2);
  }).join(' ');

  const SHAPES = {
    numberline: g => { s('path', { class: 'stkl', d: 'M-10 2 H10 M-6 -1 V5 M0 -1 V5 M6 -1 V5' }, g); s('circle', { class: 'stkd', cx: 3, cy: 2, r: 2.6 }, g); },
    graphline:  g => { s('path', { class: 'stki', d: 'M-9 7 H9 M-7 9 V-9' }, g); s('path', { class: 'stkl', d: 'M-9 6 L9 -7' }, g); },
    slope:      g => { s('path', { class: 'stkl', d: 'M-9 7 L9 -7' }, g); s('path', { class: 'stki', d: 'M-3 2.3 H4.6 V-3.6' }, g); },
    cross:      g => { s('path', { class: 'stkl', d: 'M-9 -6 L9 8 M-9 8 L9 -6' }, g); s('circle', { class: 'stkd', cx: 0, cy: 1, r: 2.4 }, g); },
    ray:        g => { s('path', { class: 'stkl', d: 'M-10 2 H10' }, g); s('path', { class: 'stkl', d: 'M-.4 2 H9', 'stroke-width': 3.2 }, g); s('circle', { class: 'stk', cx: -3, cy: 2, r: 2.8 }, g); },
    equiv:      g => s('path', { class: 'stkl', d: 'M-7 -5 H7 M-7 0 H7 M-7 5 H7', 'stroke-width': 1.8 }, g),
    curveline:  g => { s('path', { class: 'stkl', d: 'M-9 8 Q0 -14 9 8' }, g); s('path', { class: 'stkl', d: 'M-10 1 H10' }, g); s('circle', { class: 'stkd', cx: -5.4, cy: 1, r: 2.1 }, g); s('circle', { class: 'stkd', cx: 5.4, cy: 1, r: 2.1 }, g); },
    parabola:   g => { s('path', { class: 'stki', d: 'M-9 6 H9 M0 9 V-9' }, g); s('path', { class: 'stkl', d: 'M-8 -8 Q0 14 8 -8' }, g); },
    balance:    g => { s('path', { class: 'stkl', d: 'M0 -8 V8 M-8 -5 H8 M-5 9 H5' }, g); s('path', { class: 'stki', d: 'M-8 -5 L-10.5 1 M-8 -5 L-5.5 1 M8 -5 L10.5 1 M8 -5 L5.5 1 M-11 1.5 H-5 M5 1.5 H11' }, g); },
    percent:    g => { s('circle', { class: 'stk', cx: -5, cy: -5, r: 3 }, g); s('circle', { class: 'stk', cx: 5, cy: 5, r: 3 }, g); s('path', { class: 'stkl', d: 'M-8 9 L8 -9' }, g); },
    bars:       g => { s('rect', { class: 'stk', x: -9, y: 1, width: 5, height: 8 }, g); s('rect', { class: 'stk', x: -2.5, y: -6, width: 5, height: 15 }, g); s('rect', { class: 'stk', x: 4, y: -2, width: 5, height: 11 }, g); s('path', { class: 'stki', d: 'M-11 9.5 H11' }, g); },
    scatter:    g => { s('path', { class: 'stki', d: 'M-9 8 H9 M-9 8 V-9' }, g); s('path', { class: 'stki', d: 'M-8 6 L8 -6' }, g); [[-5, 4], [-2, 1.5], [1, -.5], [3, -4], [6, -2.5]].forEach(([x, y]) => s('circle', { class: 'stkd', cx: x, cy: y, r: 1.7 }, g)); },
    die:        g => { s('rect', { class: 'stk', x: -9, y: -9, width: 18, height: 18, rx: 3 }, g); [[-4.5, -4.5], [0, 0], [4.5, 4.5]].forEach(([x, y]) => s('circle', { class: 'stkd', cx: x, cy: y, r: 1.8 }, g)); },
    errorbar:   g => { s('path', { class: 'stkl', d: 'M-9 0 H9 M-9 -3.5 V3.5 M9 -3.5 V3.5' }, g); s('circle', { class: 'stkd', cx: 0, cy: 0, r: 2.8 }, g); },
    magnifier:  g => { s('circle', { class: 'stk', cx: -2, cy: -2, r: 6.5 }, g); s('path', { class: 'stkl', d: 'M2.8 2.8 L9 9', 'stroke-width': 2.4 }, g); },
    cube:       g => { s('polygon', { class: 'stk', points: poly(6, 10.5, -90) }, g); s('path', { class: 'stki', d: 'M0 0 L0 10.5 M0 0 L-9.1 -5.25 M0 0 L9.1 -5.25' }, g); },
    angle:      g => { s('path', { class: 'stk', d: 'M-9 8 L2 -9 L9 8 z', 'fill-opacity': 0 }, g); s('path', { class: 'stki', d: 'M-1.26 -3.96 A6 6 0 0 0 4.29 -3.45' }, g); },
    right:      g => { s('polygon', { class: 'stk', points: '-9,9 9,9 9,-9' }, g); s('path', { class: 'stki', d: 'M9 5 h-4 v4' }, g); },
    dotcircle:  g => { s('circle', { class: 'stk', r: 9.5 }, g); s('circle', { class: 'stkd', r: 1.6 }, g); },
  };
  function glyph(slug) {
    const g = document.createElementNS(NS, 'svg');
    g.setAttribute('viewBox', '-13 -13 26 26');
    g.setAttribute('aria-hidden', 'true');
    g.setAttribute('focusable', 'false');
    g.setAttribute('class', 'glyph');
    const t = TOPIC[slug];
    (SHAPES[t ? t.shape : 'dotcircle'])(g);
    return g;
  }
  const chip = slug => h('span', { class: 'chip' }, glyph(slug), (TOPIC[slug] || {}).short || slug);

  /* ------------------------------------------------------------ helpers */
  const mmss = sec => {
    sec = Math.max(0, Math.round(sec));
    return Math.floor(sec / 60) + ':' + String(sec % 60).padStart(2, '0');
  };
  const minutesFor = n => Math.max(1, Math.round(n * 95 / 60));      // the real test's pace
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const day = iso => { const d = new Date(iso.length === 10 ? iso + 'T12:00:00' : iso); return `${MONTHS[d.getMonth()]} ${d.getDate()}`; };
  const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
  const band = e => e ? `${e.low}–${e.high}` : '—';
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* a snapshot kept for one tab, so a page can animate from where it was */
  const snap = {
    get(k) { try { return JSON.parse(sessionStorage.getItem('satf.' + k) || 'null'); } catch (_) { return null; } },
    set(k, v) { try { sessionStorage.setItem('satf.' + k, JSON.stringify(v)); } catch (_) {} },
  };

  /* ------------------------------------------------------------ the shell */
  const NAV = [
    ['today', '/', 'Today'],
    ['practice', '/practice/', 'Practice'],
    ['tests', '/tests/', 'Tests'],
    ['plan', '/plan/', 'Plan'],
    ['results', '/results/', 'Results'],
  ];
  const SECTION = { session: 'practice', mistakes: 'practice', report: 'results', challenge: 'today', diagnostic: 'tests' };

  function shell() {
    const page = document.body.dataset.page || '';
    const here = SECTION[page] || page;
    const bar = $('#bar');
    if (bar) {
      bar.className = 'bar';
      bar.innerHTML = `<div class="bar-in">
        <a class="brand" href="/" aria-label="SAT Freshman, today">${mark(26)}</a>
        <nav class="nav" aria-label="Sections">${NAV.map(([id, href, label]) =>
          `<a href="${href}"${id === here ? ' aria-current="page"' : ''}>${label}</a>`).join('')}</nav>
        <div class="bar-end">
          <a class="streak" id="streak" href="/results/" aria-label="Streak" hidden>${svg(ICON.flame, 16)}<span></span></a>
          <a class="avatar" id="avatar" href="/me/" aria-label="Me"></a>
        </div></div>`;
      const onScroll = () => bar.classList.toggle('scrolled', scrollY > 4);
      addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }
    const tabs = $('#tabs');
    if (tabs) {
      tabs.className = 'tabs';
      tabs.setAttribute('aria-label', 'Sections');
      tabs.innerHTML = NAV.map(([id, href, label]) =>
        `<a href="${href}"${id === here ? ' aria-current="page"' : ''}>${svg(ICON[id], 22)}<span>${label}</span></a>`).join('');
    }
    paintMe();
  }

  let meCache = null;
  async function me(fresh = false) {
    if (meCache && !fresh) return meCache;
    meCache = await api('/me');
    return meCache;
  }
  async function paintMe() {
    const av = $('#avatar'), st = $('#streak');
    if (!av) return;
    av.innerHTML = mark(16, '#8A847C');
    try {
      const m = await me();
      const name = m.profile.name;
      if (name) av.textContent = name.trim()[0].toUpperCase();
      const n = m.days.streak;
      if (st) {
        st.hidden = !m.days.total;
        st.classList.toggle('on', n > 0);
        st.querySelector('span').textContent = n;
        st.setAttribute('aria-label', `${n} day streak`);
      }
    } catch (_) { /* no server: the shell still stands */ }
  }

  /* ------------------------------------------------------------ a question
     Renders one question into host. Stems and options are plain Unicode from
     the bank, set as text; figures are the bank's own SVG. The page decides
     what an answer does; reveal() paints what the server said about it. */
  function question(host, q, { onAnswer, again = false } = {}) {
    host.replaceChildren();
    const t = TOPIC[q.topic];
    const skill = h('p', { class: 'q-skill' }, glyph(q.topic), h('span', { text: t ? t.short : (q.topic_name || '') }));
    if (again || q.repair) skill.append(h('span', { class: 'again', text: 'Again' }));
    host.append(skill);

    if (q.figure) {
      const fig = h('div', { class: 'q-fig', html: q.figure });
      const el = fig.querySelector('svg');
      if (el) {
        const vb = el.viewBox && el.viewBox.baseVal;
        const natural = (vb && vb.width) || parseFloat(el.getAttribute('width')) || 360;
        el.removeAttribute('width');
        el.removeAttribute('height');
        el.style.width = Math.round(Math.min(natural * 1.3, 620)) + 'px';
      }
      host.append(fig);
    }
    if (q.table && q.table.length) {
      const tb = h('table');
      q.table.forEach((row, i) => tb.append(h('tr', {}, row.map(c => h(i ? 'td' : 'th', { text: c })))));
      host.append(h('div', { class: 'q-table' }, tb));
    }
    host.append(h('div', { class: 'q-stem', text: q.stem || '' }));

    const verdict = h('div', { class: 'verdict', hidden: true });
    let answered = false;
    const api_ = { answered: () => answered, reveal, choose: null };

    if (q.type === 'mcq') {
      const list = h('ol', { class: 'opts' });
      const buttons = (q.choices || []).map((c, i) => {
        const b = h('button', { type: 'button', class: 'opt', 'data-i': i },
          h('span', { class: 'l', text: 'ABCD'[i] }), h('span', { class: 't', text: c }));
        b.addEventListener('click', () => pick(i));
        list.append(h('li', {}, b));
        return b;
      });
      host.append(list);
      function pick(i) {
        if (answered || !onAnswer) return;
        answered = true;
        buttons[i].classList.add('picked');
        list.classList.add('done');
        onAnswer(i);
      }
      api_.choose = pick;
      api_.buttons = buttons;
      api_.list = list;
    } else {
      const input = h('input', { class: 'field', type: 'text', inputmode: 'decimal', autocomplete: 'off',
                                 spellcheck: 'false', maxlength: '6', 'aria-label': 'Your answer',
                                 placeholder: '' });
      const go = h('button', { type: 'button', class: 'pill', text: 'Check', disabled: true });
      const preview = h('p', { class: 'preview' });
      const wrap = h('div', { class: 'grid-in' }, input, go);
      input.addEventListener('input', () => {
        const v = input.value.trim().replace(/-/g, '−');
        preview.textContent = v ? v : '';
        go.disabled = !input.value.trim();
      });
      const submit = () => {
        const v = input.value.trim();
        if (answered || !v || !onAnswer) return;
        answered = true;
        input.readOnly = true;
        go.hidden = true;
        onAnswer(v);
      };
      go.addEventListener('click', submit);
      input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); submit(); } });
      host.append(wrap, preview);
      api_.input = input;
      api_.wrap = wrap;
      api_.preview = preview;
      setTimeout(() => { if (matchMedia('(hover: hover)').matches) input.focus({ preventScroll: true }); }, 60);
    }
    host.append(verdict);

    function reveal(fb, { open } = {}) {
      answered = true;
      if (q.type === 'mcq') {
        api_.list.classList.add('done');
        api_.buttons.forEach(b => b.classList.remove('picked'));
        if (fb.given !== undefined && fb.given !== null && !fb.correct) api_.buttons[fb.given]?.classList.add('no');
        if (fb.answer_index !== null && fb.answer_index !== undefined) api_.buttons[fb.answer_index]?.classList.add('ok');
      } else {
        if (fb.given !== undefined && api_.input && !api_.input.value) api_.input.value = fb.given;
        api_.input && (api_.input.readOnly = true);
        api_.wrap.querySelector('.pill')?.remove();
        api_.wrap.classList.add(fb.correct ? 'ok' : 'no');
        if (!fb.correct) {
          api_.preview.replaceWith(h('p', { class: 'grid-key' }, h('b', { text: String(fb.answer).replace(/-/g, '−') })));
        } else api_.preview.textContent = '';
      }
      verdict.replaceChildren();
      if (!fb.correct && fb.mistake) verdict.append(h('p', { class: 'mistake', text: fb.mistake }));
      if (fb.rationale) {
        const why = h('p', { class: 'why', text: fb.rationale, hidden: fb.correct && !open });
        if (fb.correct && !open) {
          const tog = h('button', { type: 'button', class: 'quiet why-toggle', text: 'Why' });
          tog.addEventListener('click', () => { why.hidden = false; tog.remove(); });
          verdict.append(tog);
        }
        verdict.append(why);
      }
      verdict.hidden = false;
    }
    return api_;
  }

  /* ------------------------------------------------------------ calculator
     Desmos, as on the test. The key is the one Desmos publishes for trying the
     API; a live deployment needs its own. */
  const DESMOS_KEY = 'dcb31709b452b1cf9dc26972add0fda6';
  let calcPanel = null;
  const calc = {
    open() {
      if (calcPanel) { calcPanel.hidden = false; return; }
      calcPanel = h('div', { class: 'calc', role: 'dialog', 'aria-label': 'Calculator' });
      const x = h('button', { type: 'button', class: 'x', 'aria-label': 'Close calculator', html: svg(ICON.x, 18) });
      const bar = h('div', { class: 'calc-bar' }, h('span', { text: 'Desmos' }), x);
      const host = h('div', { class: 'calc-host' }, h('p', { class: 'calc-note', text: 'Loading' }));
      calcPanel.append(bar, host);
      document.body.append(calcPanel);
      x.addEventListener('click', () => calc.close());
      drag(calcPanel, bar);
      const sc = document.createElement('script');
      sc.src = `https://www.desmos.com/api/v1.11/calculator.js?apiKey=${DESMOS_KEY}`;
      sc.onload = () => {
        if (!window.Desmos) return;
        host.replaceChildren();
        window.Desmos.GraphingCalculator(host, { keypad: true, expressions: true, settingsMenu: true, border: false });
      };
      sc.onerror = () => { host.firstChild.textContent = 'The calculator needs a connection.'; };
      document.head.append(sc);
    },
    close() { if (calcPanel) calcPanel.hidden = true; },
    toggle() { calcPanel && !calcPanel.hidden ? calc.close() : calc.open(); },
    get open_() { return !!calcPanel && !calcPanel.hidden; },
  };
  function drag(panel, handle) {
    let dx = 0, dy = 0, on = false;
    handle.addEventListener('pointerdown', e => {
      if (e.target.closest('button')) return;
      on = true;
      const r = panel.getBoundingClientRect();
      dx = e.clientX - r.left; dy = e.clientY - r.top;
      panel.style.right = 'auto';
      handle.setPointerCapture(e.pointerId);
    });
    handle.addEventListener('pointermove', e => {
      if (!on) return;
      const r = panel.getBoundingClientRect();
      panel.style.left = Math.min(Math.max(0, e.clientX - dx), innerWidth - r.width) + 'px';
      panel.style.top = Math.min(Math.max(0, e.clientY - dy), innerHeight - 44) + 'px';
    });
    const stop = () => { on = false; };
    handle.addEventListener('pointerup', stop);
    handle.addEventListener('pointercancel', stop);
  }

  /* ------------------------------------------------------------ reference
     The sheet the test gives you: ten formulas, two special right triangles,
     three facts, and nothing else. */
  const F = 'font-family="Source Serif 4, serif" font-style="italic"';
  const REF = [
    [`<circle cx="30" cy="28" r="20" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M30 28h20" stroke="currentColor" stroke-width="1.3"/><text x="38" y="24" font-size="11" ${F}>r</text>`, '<i>A</i> = π<i>r</i>²<br><i>C</i> = 2π<i>r</i>'],
    [`<rect x="8" y="12" width="44" height="30" fill="none" stroke="currentColor" stroke-width="1.5"/><text x="30" y="54" font-size="11" text-anchor="middle" ${F}>ℓ</text><text x="1" y="31" font-size="11" ${F}>w</text>`, '<i>A</i> = ℓ<i>w</i>'],
    [`<path d="M6 42 L56 42 L38 12 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M38 12 L38 42" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/><text x="42" y="30" font-size="10" ${F}>h</text><text x="28" y="54" font-size="10" ${F}>b</text>`, '<i>A</i> = ½<i>bh</i>'],
    [`<path d="M10 42 L50 42 L50 12 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M46 42 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="28" y="54" font-size="10" ${F}>b</text><text x="54" y="30" font-size="10" ${F}>a</text><text x="24" y="24" font-size="10" ${F}>c</text>`, '<i>c</i>² = <i>a</i>² + <i>b</i>²'],
    [`<path d="M8 43 L52 43 L52 18 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M48 43 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="11" y="39" font-size="8" font-family="Source Serif 4, serif">30°</text><text x="41" y="27" font-size="8" font-family="Source Serif 4, serif">60°</text>`, '<small>Special right triangles</small><i>x</i>, <i>x</i>√3, 2<i>x</i>'],
    [`<path d="M14 43 L50 43 L50 7 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M46 43 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="17" y="39" font-size="8" font-family="Source Serif 4, serif">45°</text><text x="38" y="18" font-size="8" font-family="Source Serif 4, serif">45°</text>`, '<i>s</i>, <i>s</i>, <i>s</i>√2'],
    [`<rect x="12" y="20" width="28" height="22" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 20 L23 12 L51 12 L40 20 M40 42 L51 34 L51 12" fill="none" stroke="currentColor" stroke-width="1.3"/>`, '<i>V</i> = ℓ<i>wh</i>'],
    [`<ellipse cx="30" cy="15" rx="16" ry="5.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M14 15v22a16 5.5 0 0 0 32 0V15" fill="none" stroke="currentColor" stroke-width="1.4"/>`, '<i>V</i> = π<i>r</i>²<i>h</i>'],
    [`<circle cx="30" cy="28" r="18" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="30" cy="28" rx="18" ry="6.5" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>`, '<i>V</i> = <sup>4</sup>⁄<sub>3</sub>π<i>r</i>³'],
    [`<path d="M30 8 L49 41 L11 41 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="30" cy="41" rx="19" ry="5.5" fill="none" stroke="currentColor" stroke-width="1.1"/>`, '<i>V</i> = <sup>1</sup>⁄<sub>3</sub>π<i>r</i>²<i>h</i>'],
    [`<path d="M30 8 L52 38 L8 38 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 38 L19 45 L52 45 L52 38" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M30 8 L52 45" fill="none" stroke="currentColor" stroke-width="1.1"/>`, '<i>V</i> = <sup>1</sup>⁄<sub>3</sub>ℓ<i>wh</i>'],
  ];
  let refSheet = null;
  const ref = {
    open() {
      if (!refSheet) {
        refSheet = h('dialog', { class: 'sheet', 'aria-label': 'Reference' });
        const x = h('button', { type: 'button', class: 'x', 'aria-label': 'Close', html: svg(ICON.x, 18) });
        x.addEventListener('click', () => refSheet.close());
        refSheet.addEventListener('click', e => { if (e.target === refSheet) refSheet.close(); });
        refSheet.append(h('div', { class: 'sheet-in' },
          h('div', { class: 'sheet-head' }, h('span', { class: 'k', text: 'Reference' }), x),
          h('div', { class: 'ref', html: REF.map(([art, cap]) =>
            `<figure><svg width="60" height="56" viewBox="0 0 60 56" aria-hidden="true">${art}</svg><figcaption>${cap}</figcaption></figure>`).join('') }),
          h('p', { class: 'ref-facts', html:
            'The number of degrees of arc in a circle is 360.<br>The number of radians of arc in a circle is 2π.<br>The sum of the measures in degrees of the angles of a triangle is 180.' })));
        document.body.append(refSheet);
      }
      refSheet.showModal();
    },
  };

  /* ------------------------------------------------------------ export */
  window.UI = {
    api, learner, useLearner, h, s, svg, mark, ICON, TOPICS, TOPIC, DOMAINS, glyph, chip,
    question, calc, ref, shell, me, snap, mmss, minutesFor, day, cap, band, reduced, $,
  };
})();
