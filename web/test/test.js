/* ============================================================================
   The test window.

   One module of questions, one at a time, with the tools a student gets on the
   day. The key never comes down the wire -- answers go up, grading happens on
   the server -- so a student reading the source finds nothing but their own
   responses.
   ========================================================================== */

(() => {
  'use strict';

  const $ = id => document.getElementById(id);
  const API = '/api';

  /* ------------------------------------------------------------ the state */
  const S = {
    id: null,
    mode: 'diagnostic',
    section: 'Section 1, Module 1: Math',
    subject: 'math',
    seconds: 1900,
    qs: [],
    i: 0,
    answers: {},        // qid -> option index, or typed string
    marked: new Set(),
    out: {},            // qid -> Set of struck option indices
    strikeOn: false,
    ended: false,
  };

  /* A module to develop against when no server is up. Replaced wholesale by
     whatever /api/session returns. */
  const SAMPLE = {
    id: 'local',
    section: 'Section 1, Module 1: Math',
    subject: 'math',
    seconds: 380,
    questions: [
      { id:'s1', domain:'Advanced Math', difficulty:'medium', type:'mcq',
        stem:'Which expression is equivalent to x\u00b2 + 3x \u2212 40?',
        choices:['(x \u2212 4)(x + 10)','(x \u2212 5)(x + 8)','(x \u2212 8)(x + 5)','(x \u2212 10)(x + 4)'],
        latex:['(x-4)(x+10)','(x-5)(x+8)','(x-8)(x+5)','(x-10)(x+4)'] },
      { id:'s2', domain:'Algebra', difficulty:'easy', type:'mcq',
        stem:'If 4x + 7 = 31, what is the value of x ?',
        choices:['6','8','9.5','24'], latex:['6','8','9.5','24'] },
      { id:'s3', domain:'Problem-Solving and Data Analysis', difficulty:'medium', type:'mcq',
        stem:'The table shows the number of hours five students studied.\nWhat is the median number of hours?',
        table:[['Student','Hours'],['A','3'],['B','7'],['C','4'],['D','9'],['E','5']],
        choices:['4','5','5.6','7'], latex:['4','5','5.6','7'] },
      { id:'s4', domain:'Geometry and Trigonometry', difficulty:'easy', type:'spr',
        stem:'A square has a side length of 76 units. What is its area, in square units?' },
    ],
  };

  /* ------------------------------------------------------------ rendering */

  const mathify = node => {
    if (!window.renderMathInElement) return;
    try {
      window.renderMathInElement(node, {
        delimiters: [
          { left:'$$', right:'$$', display:true },
          { left:'\\[', right:'\\]', display:true },
          { left:'\\(', right:'\\)', display:false },
          { left:'$', right:'$', display:false },
        ],
        throwOnError: false,
      });
    } catch (_) { /* a stem that will not typeset still has to be readable */ }
  };

  const cur = () => S.qs[S.i];

  /* Every generated chart sets its labels at 11px inside a viewBox a few
     hundred units across, so at natural size they read half the height of the
     17px stem under them, and a 390-wide plot leaves most of a 760 column
     empty. Scaling to 1.45 puts those labels near 16px whatever the viewBox.

     But a taller chart then pushes the answer off the bottom, and hunting for
     the input on a timed test is worse than a slightly smaller chart. So the
     figure takes the most room it can without making the question scroll,
     between its natural size and that 1.45 ceiling, measured rather than
     guessed because how much is left depends on the stem and the options. */
  const FIGURE_MAX = 1.45;
  const FIGURE_MIN = 1.0;

  function sizeFigure(host, pane) {
    const svg = host.querySelector('svg');
    if (!svg) return;
    const vb = svg.viewBox && svg.viewBox.baseVal;
    const natural = (vb && vb.width) || parseFloat(svg.getAttribute('width')) || 0;
    if (!natural) return;

    svg.removeAttribute('width');
    svg.removeAttribute('height');
    const at = k => { svg.style.width = Math.round(natural * k) + 'px'; };

    at(FIGURE_MAX);
    if (!pane) return;
    for (let k = FIGURE_MAX; k > FIGURE_MIN && pane.scrollHeight > pane.clientHeight; k -= 0.05) {
      at(k);
    }
  }

  function render() {
    const q = cur();
    if (!q) return;

    $('sect').textContent = S.section;
    $('navmapTitle').textContent = S.section;
    $('qnum').textContent = S.i + 1;
    $('navLabel').textContent = `Question ${S.i + 1} of ${S.qs.length}`;

    /* reading questions carry a passage, so the pane splits; math does not */
    const split = !!q.passage;
    $('body').dataset.layout = split ? 'split' : 'single';
    $('annotateBtn').hidden = !split;
    $('calcBtn').hidden = S.subject !== 'math';
    $('refBtn').hidden = S.subject !== 'math';
    if (split) {
      $('passage').innerHTML = q.passage;
      mathify($('passage'));
    }

    /* order matters: the prose says "the circle shown" and "the table above",
       so the artwork has to be above the sentence that points at it */
    const fig = $('figure');
    if (q.figure) { fig.hidden = false; fig.innerHTML = q.figure; }
    else { fig.hidden = true; fig.innerHTML = ''; }

    const tw = $('tablewrap');
    if (q.table && q.table.length) { tw.hidden = false; tw.replaceChildren(buildTable(q.table)); }
    else { tw.hidden = true; tw.replaceChildren(); }

    /* stems are plain Unicode -- x\u00b2, \u2212, \u03c0 -- never markup and never
       LaTeX, so they are set as text and their newlines kept by white-space */
    $('stem').textContent = q.stem || '';

    $('markBtn').setAttribute('aria-pressed', String(S.marked.has(q.id)));
    $('abcBtn').setAttribute('aria-pressed', String(S.strikeOn));

    q.type === 'spr' ? paintSPR(q) : paintOptions(q);

    $('backBtn').hidden = S.i === 0;
    $('nextBtn').textContent = S.i === S.qs.length - 1 ? 'Finish' : 'Next';

    /* last, because it measures what the options left behind */
    if (q.figure) sizeFigure($('figure'), $('paneR'));

    $('paneR').scrollTop = 0;
    if (split) $('paneL').scrollTop = 0;
  }

  function paintOptions(q) {
    $('spr').hidden = true;
    const ul = $('opts');
    ul.hidden = false;
    ul.dataset.strike = String(S.strikeOn);
    ul.innerHTML = '';

    const struck = S.out[q.id] || new Set();
    const picked = S.answers[q.id];

    (q.choices || []).forEach((text, n) => {
      const letter = 'ABCD'[n];
      const li = document.createElement('li');
      li.className = 'opt';
      if (struck.has(n)) li.dataset.out = 'true';

      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'choice';
      btn.setAttribute('role', 'radio');
      btn.setAttribute('aria-checked', String(picked === n));
      if (struck.has(n)) btn.dataset.out = 'true';
      btn.innerHTML = `<span class="letter">${letter}</span><span class="body-txt"></span>`;
      setChoice(btn.querySelector('.body-txt'), text, (q.latex || [])[n]);
      btn.addEventListener('click', () => choose(n));

      const strike = document.createElement('button');
      strike.type = 'button';
      strike.className = 'strike';
      strike.textContent = letter;
      strike.setAttribute('aria-label', `Cross out ${letter}`);
      strike.addEventListener('click', () => setStruck(q.id, n, true));

      const undo = document.createElement('button');
      undo.type = 'button';
      undo.className = 'undo';
      undo.textContent = 'Undo';
      undo.addEventListener('click', () => setStruck(q.id, n, false));

      li.append(btn, strike, undo);
      ul.appendChild(li);
    });
  }

  /* The bank gives a plain form and a LaTeX form of every option. They are the
     same string for most items; where they differ it is a fraction or a radical,
     and only then is it worth handing to KaTeX. */
  function setChoice(host, plain, tex) {
    if (tex && tex !== plain && window.katex) {
      try {
        host.innerHTML = window.katex.renderToString(tex, { throwOnError: false });
        return;
      } catch (_) { /* fall through to the plain form, which always reads */ }
    }
    host.textContent = plain;
  }

  /* row 0 is the header */
  function buildTable(rows) {
    const t = document.createElement('table');
    const head = document.createElement('thead');
    const hr = document.createElement('tr');
    rows[0].forEach(c => { const th = document.createElement('th'); th.textContent = c; hr.appendChild(th); });
    head.appendChild(hr);
    const body = document.createElement('tbody');
    rows.slice(1).forEach(r => {
      const tr = document.createElement('tr');
      r.forEach(c => { const td = document.createElement('td'); td.textContent = c; tr.appendChild(td); });
      body.appendChild(tr);
    });
    t.append(head, body);
    return t;
  }

  function paintSPR(q) {
    $('opts').hidden = true;
    $('spr').hidden = false;
    const input = $('sprInput');
    input.value = S.answers[q.id] || '';
    showPreview(input.value);
  }

  const showPreview = v => {
    const p = $('sprPreview');
    p.textContent = v ? `Answer: ${v}` : 'Answer preview';
    p.style.opacity = v ? '1' : '.65';
  };

  /* ------------------------------------------------------------- answering */

  function choose(n) {
    const q = cur();
    const struck = S.out[q.id];
    if (struck && struck.has(n)) return;        // a crossed-out choice is not selectable
    S.answers[q.id] = n;
    post(q.id, n);
    paintOptions(q);
    paintCells();
  }

  function setStruck(qid, n, on) {
    const set = S.out[qid] || (S.out[qid] = new Set());
    on ? set.add(n) : set.delete(n);
    if (on && S.answers[qid] === n) { delete S.answers[qid]; post(qid, null); }
    paintOptions(cur());
    paintCells();
  }

  /* fire and forget: a dropped keystroke must not stall the student */
  function post(qid, value) {
    if (!S.id || S.id === 'local') return;
    fetch(`${API}/session/${S.id}/answer`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ question_id: qid, answer: value }),
    }).catch(() => {});
  }

  /* -------------------------------------------------------------- movement */

  const go = n => {
    S.i = Math.max(0, Math.min(S.qs.length - 1, n));
    render();
    paintCells();
  };

  function next() {
    if (S.i === S.qs.length - 1) return finish();
    go(S.i + 1);
  }

  let leaving = false;
  async function finish() {
    if (leaving) return;
    leaving = true;
    S.ended = true;
    if (!S.id || S.id === 'local') {
      location.href = '../diagnostic/';      // no server behind this; nothing to mark
      return;
    }

    let done = {};
    try {
      const r = await fetch(`${API}/session/${S.id}/finish`, { method: 'POST' });
      done = await r.json();
    } catch (_) { /* the server has every answer already; let them through */ }

    /* A mock runs two modules, and the second is chosen from how the first
       went. Finishing module 1 therefore does not finish the test -- it routes
       and comes back, with no way into module 1 again, as on the day. */
    if (done.next_module) {
      leaving = false;
      S.ended = false;
      await nextModule(done);
      return;
    }

    /* the diagnostic asks who you are before it says anything; practice does
       not, because you chose these questions yourself */
    location.href = S.mode === 'practice'
      ? `../diagnostic/results.html?s=${encodeURIComponent(S.id)}`
      : `../diagnostic/signup.html?s=${encodeURIComponent(S.id)}`;
  }

  function nextModule(done) {
    return new Promise(resolve => {
      const sheet = $('gateSheet');
      $('gateTitle').textContent = `End of Module ${done.finished_module}`;
      $('gateBody').textContent =
        'You cannot return to this module. The next one starts when you continue.';
      sheet.showModal();
      $('gateGo').onclick = async () => {
        sheet.close();
        const r = await fetch(`${API}/session/${S.id}`);
        const data = await r.json();
        S.section = data.section || S.section;
        S.seconds = data.seconds;
        S.qs = data.questions || [];
        S.answers = data.answers || {};
        S.marked = new Set();
        S.out = {};
        S.i = 0;
        render();
        paintCells();
        startClock();
        resolve();
      };
    });
  }

  /* ------------------------------------------------------------- navigator */

  function paintCells() {
    const ul = $('cells');
    ul.innerHTML = '';
    S.qs.forEach((q, n) => {
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'cell';
      b.textContent = n + 1;
      if (S.answers[q.id] !== undefined) b.dataset.done = 'true';
      if (S.marked.has(q.id)) b.dataset.mark = 'true';
      if (n === S.i) b.setAttribute('aria-current', 'true');
      b.addEventListener('click', () => { closeNav(); go(n); });
      li.appendChild(b);
      ul.appendChild(li);
    });
  }

  const closeNav = () => {
    $('navmap').hidden = true;
    $('navBtn').setAttribute('aria-expanded', 'false');
  };

  /* ---------------------------------------------------------------- clock */

  let ticker = null;
  function startClock() {
    if (ticker) clearInterval(ticker);      // module 2 must not inherit module 1's
    let left = S.seconds;
    const el = $('clock');
    const paint = () => {
      const m = Math.floor(Math.max(0, left) / 60);
      const s = Math.max(0, left) % 60;
      el.textContent = `${m}:${String(s).padStart(2, '0')}`;
    };
    paint();
    if (left === null) return;
    let warned = false;
    ticker = setInterval(() => {
      if (S.ended) return;
      left -= 1;
      paint();
      /* Bluebook shows a five-minute warning, and unhides the clock to show
         it, because a student who hid the timer still has to be told. */
      if (!warned && left <= 300) {
        warned = true;
        el.dataset.hidden = 'false';
        $('hideBtn').textContent = 'Hide';
        $('clockNote').hidden = false;
        setTimeout(() => { $('clockNote').hidden = true; }, 6000);
      }
      if (left <= 0) { clearInterval(ticker); ticker = null; finish(); }
    }, 1000);
  }

  /* ----------------------------------------------------------- calculator
     Desmos, as on the real test. The key below is the one Desmos publishes
     for trying the API out; a live deployment needs its own. */
  const DESMOS_KEY = 'dcb31709b452b1cf9dc26972add0fda6';
  let calcReady = false;

  function openCalc() {
    const panel = $('calc');
    panel.hidden = false;
    $('calcBtn').setAttribute('aria-pressed', 'true');
    if (calcReady) return;
    calcReady = true;

    const s = document.createElement('script');
    s.src = `https://www.desmos.com/api/v1.11/calculator.js?apiKey=${DESMOS_KEY}`;
    s.onload = () => {
      if (!window.Desmos) return fallback('The calculator could not start.');
      $('calcFallback').remove();
      window.Desmos.GraphingCalculator($('calcHost'), {
        keypad: true, expressions: true, settingsMenu: true,
        border: false, lockViewport: false,
      });
    };
    s.onerror = () => fallback('The calculator needs a network connection.');
    document.head.appendChild(s);
  }

  const fallback = msg => { const f = $('calcFallback'); if (f) f.textContent = msg; };

  function closeCalc() {
    $('calc').hidden = true;
    $('calcBtn').setAttribute('aria-pressed', 'false');
  }

  /* drag by the title bar, clamped so the panel cannot be lost off-screen */
  function dragCalc() {
    const panel = $('calc'), bar = $('calcBar');
    let dx = 0, dy = 0, on = false;

    bar.addEventListener('pointerdown', e => {
      if (e.target.closest('button')) return;
      on = true;
      const r = panel.getBoundingClientRect();
      dx = e.clientX - r.left; dy = e.clientY - r.top;
      panel.style.right = 'auto'; panel.style.bottom = 'auto';
      bar.setPointerCapture(e.pointerId);
    });
    bar.addEventListener('pointermove', e => {
      if (!on) return;
      const r = panel.getBoundingClientRect();
      const x = Math.min(Math.max(0, e.clientX - dx), innerWidth - r.width);
      const y = Math.min(Math.max(0, e.clientY - dy), innerHeight - 44);
      panel.style.left = x + 'px';
      panel.style.top = y + 'px';
    });
    const stop = () => { on = false; };
    bar.addEventListener('pointerup', stop);
    bar.addEventListener('pointercancel', stop);
  }

  /* ------------------------------------------------------------- reference
     The sheet College Board actually gives you, from the official practice
     test: ten formulas, two special right triangles, three facts. Nothing
     else -- no slope, no quadratic formula, no statistics. Drawn rather than
     screenshotted, and each caption typeset here because the captions are
     LaTeX bodies with no delimiters for the auto-renderer to find. */
  const REF = [
    ['<circle cx="34" cy="30" r="24" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M34 30h24" stroke="currentColor" stroke-width="1.4"/><text x="44" y="26" font-size="12" font-family="Source Serif 4, serif" font-style="italic">r</text>',
     ['A = \\pi r^{2}', 'C = 2\\pi r']],
    ['<rect x="10" y="12" width="48" height="34" fill="none" stroke="currentColor" stroke-width="1.6"/><text x="34" y="56" font-size="12" text-anchor="middle" font-family="Source Serif 4, serif" font-style="italic">ℓ</text><text x="4" y="32" font-size="12" font-family="Source Serif 4, serif" font-style="italic">w</text>',
     ['A = \\ell w']],
    ['<path d="M8 44 L60 44 L40 12 Z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M40 12 L40 44" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/><text x="46" y="30" font-size="11" font-family="Source Serif 4, serif" font-style="italic">h</text><text x="32" y="56" font-size="11" font-family="Source Serif 4, serif" font-style="italic">b</text>',
     ['A = \\tfrac{1}{2}bh']],
    ['<path d="M12 44 L54 44 L54 12 Z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M50 44 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="30" y="56" font-size="11" font-family="Source Serif 4, serif" font-style="italic">b</text><text x="58" y="30" font-size="11" font-family="Source Serif 4, serif" font-style="italic">a</text><text x="28" y="26" font-size="11" font-family="Source Serif 4, serif" font-style="italic">c</text>',
     ['c^{2} = a^{2} + b^{2}']],
    ['<path d="M10 45 L54 45 L54 20 Z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M50 45 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="13" y="41" font-size="8.5" font-family="Source Serif 4, serif">30\u00b0</text><text x="44" y="29" font-size="8.5" font-family="Source Serif 4, serif">60\u00b0</text>',
     ['x,\\ x\\sqrt{3},\\ 2x'], 'Special right triangles'],
    ['<path d="M16 45 L52 45 L52 9 Z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M48 45 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="19" y="41" font-size="8.5" font-family="Source Serif 4, serif">45\u00b0</text><text x="40" y="20" font-size="8.5" font-family="Source Serif 4, serif">45\u00b0</text>',
     ['s,\\ s,\\ s\\sqrt{2}']],
    ['<rect x="14" y="20" width="30" height="24" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M14 20 L26 11 L56 11 L44 20 M44 44 L56 35 L56 11" fill="none" stroke="currentColor" stroke-width="1.4"/>',
     ['V = \\ell w h']],
    ['<ellipse cx="34" cy="16" rx="17" ry="6" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M17 16v24a17 6 0 0 0 34 0V16" fill="none" stroke="currentColor" stroke-width="1.5"/>',
     ['V = \\pi r^{2} h']],
    ['<circle cx="34" cy="30" r="20" fill="none" stroke="currentColor" stroke-width="1.6"/><ellipse cx="34" cy="30" rx="20" ry="7" fill="none" stroke="currentColor" stroke-width="1.1" stroke-dasharray="3 3"/>',
     ['V = \\tfrac{4}{3}\\pi r^{3}']],
    ['<path d="M34 9 L54 43 L14 43 Z" fill="none" stroke="currentColor" stroke-width="1.6"/><ellipse cx="34" cy="43" rx="20" ry="6" fill="none" stroke="currentColor" stroke-width="1.2"/>',
     ['V = \\tfrac{1}{3}\\pi r^{2} h']],
    ['<path d="M34 9 L57 40 L11 40 Z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M11 40 L22 47 L57 47 L57 40" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M34 9 L57 47" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M22 47 L34 9" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>',
     ['V = \\tfrac{1}{3}\\ell w h']],
  ];

  const tex = src => {
    if (!window.katex) return src;
    try { return window.katex.renderToString(src, { throwOnError: false }); }
    catch (_) { return src; }
  };

  function buildRef() {
    $('refBody').innerHTML = REF.map(([art, lines, note]) => `
      <figure>
        <svg width="68" height="60" viewBox="0 0 68 60" aria-hidden="true">${art}</svg>
        <figcaption>
          ${note ? `<span class="ref-note">${note}</span>` : ''}
          ${lines.map(tex).join('<br>')}
        </figcaption>
      </figure>`).join('');
  }

  /* The wording College Board prints on the directions page, kept as it is
     written rather than paraphrased: a student who has read these should meet
     the same sentences on the day. */
  const DIRECTIONS = {
    math: `
      <p>The questions in this section address a number of important math skills.
         Use of a calculator is permitted for all questions.</p>
      <p><b>NOTES</b><br>Unless otherwise indicated:</p>
      <ul>
        <li>All variables and expressions represent real numbers.</li>
        <li>Figures provided are drawn to scale.</li>
        <li>All figures lie in a plane.</li>
        <li>The domain of a given function <i>f</i> is the set of all real numbers
            <i>x</i> for which <i>f</i>(<i>x</i>) is a real number.</li>
      </ul>
      <p>For <b>multiple-choice questions</b>, solve each problem and choose the
         correct answer from the choices provided. Each multiple-choice question
         has a single correct answer.</p>
      <p>For <b>student-produced response questions</b>, solve each problem and
         enter your answer as described below.</p>
      <ul>
        <li>If you find <b>more than one correct answer</b>, enter only one answer.</li>
        <li>You can enter up to 5 characters for a <b>positive</b> answer and up to
            6 characters (including the negative sign) for a <b>negative</b> answer.</li>
        <li>If your answer is a <b>fraction</b> that doesn't fit in the provided space,
            enter the decimal equivalent.</li>
        <li>If your answer is a <b>decimal</b> that doesn't fit in the provided space,
            enter it by truncating or rounding at the fourth digit.</li>
        <li>If your answer is a <b>mixed number</b> (such as 3&frac12;), enter it as an
            improper fraction (7/2) or its decimal equivalent (3.5).</li>
        <li>Don't enter <b>symbols</b> such as a percent sign, comma, or dollar sign.</li>
      </ul>`,
    verbal: `
      <p>The questions in this section address a number of important reading and
         writing skills. Each question includes one or more passages, which may
         include a table or graph. Read each passage and question carefully, and
         then choose the best answer to the question based on the passage.</p>
      <p>All questions in this section are multiple-choice with four answer choices.
         Each question has a single best answer.</p>`,
  };

  /* ------------------------------------------------------------------ boot */

  async function load() {
    const url = new URL(location.href);
    const want = url.searchParams.get('s');
    try {
      const r = await fetch(want ? `${API}/session/${want}` : `${API}/session`,
                           want ? undefined : { method: 'POST' });
      if (!r.ok) throw new Error(r.status);
      return await r.json();
    } catch (_) {
      return SAMPLE;                      // no server: the window still works
    }
  }

  async function boot() {
    const data = await load();
    S.id = data.id;
    S.mode = data.mode || 'diagnostic';
    S.section = data.section || S.section;
    S.subject = data.subject || 'math';
    /* ?? treats the server's explicit null as absent and falls back, so the
       mode decides this rather than the value: practice has no clock. */
    S.seconds = S.mode === 'practice' ? null : (data.seconds ?? S.seconds);
    S.qs = data.questions || [];
    if (!S.qs.length) { $('stem').textContent = 'This test has no questions.'; return; }

    /* A test you lose by reloading is not a test. Putting the session in the
       URL means the back button and a refresh both land back in it. */
    if (S.id && S.id !== 'local') {
      const u = new URL(location.href);
      if (u.searchParams.get('s') !== S.id) {
        u.searchParams.set('s', S.id);
        history.replaceState(null, '', u);
      }
    }

    if (data.finished) { S.ended = true; return finish(); }
    S.answers = data.answers || {};          // what they had already put down

    $('dirsBody').innerHTML = DIRECTIONS[S.subject] || DIRECTIONS.math;
    $('who').textContent = data.name || '';
    buildRef();
    render();
    paintCells();

    /* Practice is not an exam, so it is not on a clock. A timer over questions
       a student chose for themselves only teaches them to rush. */
    if (S.seconds === null) { $('top-clock').hidden = true; }
    else startClock();
  }

  /* ---------------------------------------------------------------- wiring */

  $('nextBtn').addEventListener('click', next);
  $('backBtn').addEventListener('click', () => go(S.i - 1));

  $('markBtn').addEventListener('click', () => {
    const q = cur();
    S.marked.has(q.id) ? S.marked.delete(q.id) : S.marked.add(q.id);
    $('markBtn').setAttribute('aria-pressed', String(S.marked.has(q.id)));
    paintCells();
  });

  $('abcBtn').addEventListener('click', () => {
    S.strikeOn = !S.strikeOn;
    $('abcBtn').setAttribute('aria-pressed', String(S.strikeOn));
    $('opts').dataset.strike = String(S.strikeOn);
  });

  $('hideBtn').addEventListener('click', () => {
    const c = $('clock');
    const hidden = c.dataset.hidden === 'true';
    c.dataset.hidden = hidden ? 'false' : 'true';
    $('hideBtn').textContent = hidden ? 'Hide' : 'Show';
  });

  $('navBtn').addEventListener('click', () => {
    const open = $('navmap').hidden === false;
    $('navmap').hidden = open;
    $('navBtn').setAttribute('aria-expanded', String(!open));
  });
  document.addEventListener('click', e => {
    if ($('navmap').hidden) return;
    if (e.target.closest('#navmap, #navBtn')) return;
    closeNav();
  });

  $('calcBtn').addEventListener('click', () =>
    $('calc').hidden ? openCalc() : closeCalc());
  $('calcX').addEventListener('click', closeCalc);
  $('calcBig').addEventListener('click', () => {
    const p = $('calc');
    p.dataset.big = p.dataset.big === 'true' ? 'false' : 'true';
  });
  dragCalc();

  $('dirsBtn').addEventListener('click', () => $('dirsSheet').showModal());
  $('refBtn').addEventListener('click', () => $('refSheet').showModal());
  $('moreBtn').addEventListener('click', () => $('moreSheet').showModal());
  $('endBtn').addEventListener('click', () => { $('moreSheet').close(); finish(); });

  /* Most sheets can be dismissed. The module gate cannot: moving on is a
     decision, and clicking past it would leave the test between modules. */
  document.querySelectorAll('.sheet').forEach(d => {
    const x = d.querySelector('[data-close]');
    if (!x) return;
    x.addEventListener('click', () => d.close());
    d.addEventListener('click', e => { if (e.target === d) d.close(); });
  });
  $('gateSheet').addEventListener('cancel', e => e.preventDefault());   // no escape out

  $('sprInput').addEventListener('input', e => {
    const q = cur();
    const v = e.target.value.trim();
    v ? (S.answers[q.id] = v) : delete S.answers[q.id];
    showPreview(v);
    post(q.id, v || null);
    paintCells();
  });

  /* the keys a student reaches for without being told */
  document.addEventListener('keydown', e => {
    if (e.target.matches('input, textarea')) return;
    const q = cur();
    if (!q) return;
    const k = e.key.toUpperCase();
    if (q.type !== 'spr' && 'ABCD'.includes(k) && !e.metaKey && !e.ctrlKey) {
      choose('ABCD'.indexOf(k));
    } else if (e.key === 'ArrowRight') { next(); }
    else if (e.key === 'ArrowLeft' && S.i > 0) { go(S.i - 1); }
    else if (e.key === 'Escape') { closeNav(); }
  });

  boot();
})();
