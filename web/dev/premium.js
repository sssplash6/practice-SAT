/* /dev/premium.html: live specimens of the premium proposals (spec/redesign-2026-10-19/premium/DEMO.md).
   Every proposed style lives in premium.html under .pro; this file builds the specimens and plays the motion.
   "Current" uses the shipped kit where one exists (UI.seg, UI.tabs, UI.saving, UI.roll, UI.toast, UI.sheet). */
(() => {
  'use strict';
  const doc = document, root = doc.documentElement;
  const $ = (s, r = doc) => r.querySelector(s);
  const $$ = (s, r = doc) => [...r.querySelectorAll(s)];
  const frag = html => { const t = doc.createElement('template'); t.innerHTML = html.trim(); return t.content.firstElementChild; };
  const wait = ms => new Promise(r => setTimeout(r, ms));
  // reduced motion: the OS setting or the page switch (as kit.js still())
  const off = () => matchMedia('(prefers-reduced-motion: reduce)').matches || root.dataset.motion === 'reduce';
  const EASE = 'cubic-bezier(.23, 1, .32, 1)', MOVE = 'cubic-bezier(.77, 0, .175, 1)';
  // the springs are read from the .pro tokens, so CSS and JS share one copy
  const probe = frag('<div class="pro" hidden></div>');
  doc.body.append(probe);
  const tok = n => getComputedStyle(probe).getPropertyValue(n).trim();
  const SPRING = () => tok('--spring') || EASE, SOFT = () => tok('--spring-soft') || EASE, POP = () => tok('--spring-pop') || EASE;
  const anim = (el, kf, o = {}) => el.animate(kf, { easing: EASE, ...o });
  // under reduced motion an entry is a 120ms fade (MOTION 2, "Reduced")
  const enter = (el, kf, o = {}) => off() ? anim(el, [{ opacity: 0 }, { opacity: 1 }], { duration: 120 }) : anim(el, kf, o);

  const ic = (name, size = 18) => UI.svg(UI.ICON[name] || '', size);
  const MORE = '<circle cx="6" cy="12" r="1.6" fill="currentColor"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/><circle cx="18" cy="12" r="1.6" fill="currentColor"/>';
  const CK = '<svg class="pd-ck" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path pathLength="1" d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  const ARR = '<svg class="pd-arr" viewBox="0 0 10 10" aria-hidden="true"><path class="l" d="M0 5h7"/><path class="t" d="M1 1l4 4-4 4"/></svg>';
  const draw = (svg, ms = 240, delay = 0) => { const p = svg && $('path', svg); if (p && !off()) anim(p, [{ strokeDashoffset: 1 }, { strokeDashoffset: 0 }], { duration: ms, delay, fill: 'backwards' }); };
  // a label that changes: the new text rises 4px and fades in, 160 (MOTION C3, C13); no blur (MOTION: opacity and translate only)
  const swapText = (el, text) => { el.textContent = text; if (!off()) anim(el, [{ opacity: 0, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }], { duration: 160 }); };

  /* ------------------------------------------------------------ the page: theme and motion switches */
  const sw = (sel, on, set) => {
    const b = $(sel), sync = () => b.setAttribute('aria-checked', String(on()));
    sync();
    b.addEventListener('click', () => { set(!on()); sync(); });
  };
  sw('#pd-dark', () => root.dataset.theme === 'dark', v => { root.dataset.theme = v ? 'dark' : 'light'; });
  sw('#pd-calm', () => root.dataset.motion === 'reduce', v => { if (v) root.dataset.motion = 'reduce'; else delete root.dataset.motion; });

  /* ------------------------------------------------------------ one specimen card */
  // Phosphor arrow-counter-clockwise, for Replay
  const REPLAY = '<svg class="i" width="16" height="16" viewBox="0 0 256 256" aria-hidden="true" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="24 56 24 104 72 104" stroke="currentColor"/><path d="M67.59,192A88,88,0,1,0,65.77,65.77L24,104" stroke="currentColor"/></svg>';
  function spec(group, id, title, src, o = {}) {
    const card = frag(`<article class="pd-spec${o.wide ? ' wide' : ''}" id="${id}" aria-labelledby="${id}-t">
      <div class="pd-head"><span class="pd-id">${id}</span><h3 class="pd-title" id="${id}-t">${title}</h3><div class="pd-ctl"></div></div>
      <p class="pd-src">${src}</p><div class="pd-stage pro${o.cls ? ' ' + o.cls : ''}"></div></article>`);
    $('#g' + group).append(card);
    const stage = $('.pd-stage', card), ctl = $('.pd-ctl', card);
    stage.innerHTML = o.html || '';
    const S = { card, stage, q: s => $(s, stage), qa: s => $$(s, stage), pro: () => stage.classList.contains('pro'), mode: null, replay: null };
    if (!o.fixed) {
      // a small neutral two-way switch (the page's chrome, not a proposal)
      const m = frag(`<div class="pd-mode" role="group" aria-label="${id}: current or proposed"><button type="button" aria-pressed="false">Current</button><button type="button" aria-pressed="true">Proposed</button></div>`);
      const [bc, bp] = m.children;
      const set = pro => {
        if (pro === S.pro()) return;
        bc.setAttribute('aria-pressed', String(!pro)); bp.setAttribute('aria-pressed', String(pro));
        stage.classList.toggle('pro', pro);
        if (S.mode) S.mode(pro);
      };
      bc.addEventListener('click', () => set(false));
      bp.addEventListener('click', () => set(true));
      ctl.append(m);
    }
    if (o.replay) {
      const b = frag(`<button type="button" class="pd-replay" aria-label="Replay ${id}" title="Replay">${REPLAY}</button>`);
      b.addEventListener('click', () => S.replay && S.replay());
      ctl.append(b);
    }
    if (o.build) o.build(S);
    return S;
  }
  const states = (cls, label, list) => `<div class="pd-row">${list.map(([k, extra, body]) =>
    `<div class="pd-col"><span class="${cls} ${extra}" aria-hidden="true">${body || label}</span><span class="pd-cap">${k}</span></div>`).join('')}</div>`;

  /* ============================================================ A. Buttons */
  // the proposed saving flow: busy label, spinner only after 300ms, drawn check, back after 1200 (MOTION C3)
  async function saving(S, b, busy, done, ms = 1100) {
    if (b._run) return;
    const lab = $('.pd-lab', b), rest = lab.textContent;
    if (!S.pro()) { b._run = true; await UI.saving(b, () => wait(ms), { busy, done }).catch(() => {}); b._run = false; return; }
    b._run = true;
    b.style.minWidth = `${b.offsetWidth}px`;
    b.setAttribute('aria-busy', 'true');
    swapText(lab, busy);
    const t = setTimeout(() => { const sp = frag('<span class="pd-spin" aria-hidden="true"></span>'); b.prepend(sp); enter(sp, [{ opacity: 0 }, { opacity: 1 }], { duration: 120 }); }, 300);
    await wait(ms);
    clearTimeout(t);
    const sp = $('.pd-spin', b); if (sp) sp.remove();
    const ck = frag(CK); b.prepend(ck); draw(ck);
    swapText(lab, done);
    b.removeAttribute('aria-busy');
    await wait(1200);
    ck.remove();
    lab.textContent = rest;
    if (!off()) anim(lab, [{ opacity: 0 }, { opacity: 1 }], { duration: 160 });
    b.style.minWidth = '';
    b._run = false;
  }

  spec('A', 'A1', 'Primary .pill: rest, hover, press, focus, loading, success',
    '<b>R1</b> full recipe (sheen, lit edge, dark inset, ring one step darker, amber-tinted drop) with Vercel-style hover as a fill step, no lift; focus is the thin amber-deep ring 2px out (<b>C4</b>); <b>MOTION C1</b> press 100ms, release on the soft spring; <b>C3</b> saving (spinner only after 300ms, drawn check). 42 high, 10px corners.', {
    html: states('pill', 'Start practice', [['Rest', ''], ['Hover', 'is-hover'], ['Press', 'is-press'], ['Focus', 'is-focus'],
      ['Loading', 'is-busy', '<span class="pd-spin"></span>Building'], ['Success', '', `${CK}Ready`], ['Disabled', 'is-off']]) +
      `<div class="pd-row"><button type="button" class="pill" data-go><span class="pd-lab">Start practice</span></button><span class="pd-cap">Live: hover it, press it, Tab to it, click it for loading then success.</span></div>`,
    build(S) { const b = S.q('[data-go]'); b.addEventListener('click', () => saving(S, b, 'Building', 'Ready')); },
  });

  const pair = `<div class="pd-row"><div class="pd-col"><button type="button" class="pill">Start practice</button><button type="button" class="pill sm">Start</button><span class="pd-cap">Full (R1)</span></div>
    <div class="pd-col"><button type="button" class="pill lite">Start practice</button><button type="button" class="pill sm lite">Start</button><span class="pd-cap">Lite (R1b)</span></div></div>`;
  spec('A', 'A2', 'Full and lite orange pill, side by side, light and dark',
    '<b>R1</b> full: three background layers (sheen, fill gradient, lighter edge) and four shadows. <b>R1b</b> lite: flat #F18508 with a top highlight, bottom shade, darker ring and a 2px drop (Raycast and Kitchen pattern). Pick one.', {
    cls: 'split', html: `<div class="pd-pair"><div class="pd-light">${pair}</div><div class="pd-dark">${pair}</div></div>`,
  });

  spec('A', 'A3', 'Small primary .pill.sm in a row',
    '<b>R1</b> at 34px; the same hover, press and focus. The Today row Start (pages/today.md 3).', {
    html: states('pill sm', 'Start', [['Rest', ''], ['Hover', 'is-hover'], ['Press', 'is-press'], ['Focus', 'is-focus']]) +
      `<div class="pd-rows" style="margin-top:16px"><div><span><b>Linear Equations in One Variable</b><span class="meta">10 questions · 12 min · from your plan</span></span><button type="button" class="pill sm">Start</button></div>
      <div><span><b>Percentages</b><span class="meta">8 questions · 10 min</span></span><button type="button" class="pill sm">Start</button></div></div>`,
  });

  spec('A', 'A4', 'Secondary .btn, on paper and on a card',
    '<b>R2</b> and <b>BUILD 10</b>: a white face with a light top edge, a fine alpha ring and a 1px contact shadow; hover steps the face a shade warmer; press sinks (inset shade); <b>.btn.ink</b> takes the Kitchen dark stack; disabled is one flat tint, the same as the pill\'s. Pressed and expanded stay wash-2 with the amber ring.', {
    html: states('btn', 'Options', [['Rest', ''], ['Hover', 'is-hover'], ['Press', 'is-press'], ['Focus', 'is-focus']]) +
      `<div class="pd-row"><button type="button" class="btn" aria-pressed="true" data-tog>Timed</button><button type="button" class="btn sm">Save as preset</button><button type="button" class="btn ink">Delete set</button><button type="button" class="btn" disabled>Skip</button></div>
      <div class="card" style="margin-top:16px"><div class="pd-row"><span class="h3" style="margin-right:auto">On a card</span><button type="button" class="btn sm">Details</button><button type="button" class="btn sm" aria-expanded="true">Mentor's pick</button></div></div>`,
    build(S) { const t = S.q('[data-tog]'); t.addEventListener('click', () => t.setAttribute('aria-pressed', String(t.getAttribute('aria-pressed') !== 'true'))); },
  });

  spec('A', 'A5', 'Quiet .quiet and the hover arrow',
    '<b>R3</b>: no fill, no shadow; the underline fades in amber in 140 instead of snapping. <b>R23</b> Stripe hover arrow on links that go somewhere: the stem fades in, the tip moves 3px, 150ms.', {
    html: states('quiet', 'Undo', [['Rest', ''], ['Hover', 'is-hover']]) +
      `<div class="pd-row"><span class="quiet go is-hover" aria-hidden="true">See all skills ${ARR}</span><span class="pd-cap">Arrow, hovered</span></div>
      <div class="pd-row"><button type="button" class="quiet">Undo</button><button type="button" class="quiet">Details</button><a class="quiet go" href="#A5">See all skills ${ARR}</a><a class="quiet go" href="#A5">Open the report ${ARR}</a></div>`,
  });

  const bm = `<span class="pd-two-l">${UI.svg(UI.ICON.bookmark, 20, 'o')}${UI.svg(UI.ICON.bookmark, 20, 'f')}</span>`;
  spec('A', 'A6', 'Icon buttons',
    '<b>MOTION C1, C2</b>: hover is a fill in 140, press .94 on the soft spring; an "on" button is a raised key (<b>R4</b> e1) rather than a grey fill; <b>DISCOVER I3</b> the bookmark swaps outline to amber fill with a small scale (ICONS.md 5, status toggles).', {
    html: `<div class="pd-row">${[['Rest', ''], ['Hover', 'is-hover'], ['Press', 'is-press']].map(([k, c]) =>
      `<div class="pd-col"><span class="ibtn ${c}" aria-hidden="true">${ic('search', 20)}</span><span class="pd-cap">${k}</span></div>`).join('')}
      <div class="pd-col"><span class="ibtn" aria-pressed="true" aria-hidden="true">${bm}</span><span class="pd-cap">On</span></div></div>
      <div class="pd-row"><button type="button" class="ibtn" aria-label="Search">${ic('search', 20)}</button>
      <button type="button" class="ibtn" aria-label="Save question" aria-pressed="false" data-tog>${bm}</button>
      <button type="button" class="ibtn" aria-label="Calculator" aria-pressed="false" data-tog>${ic('calc', 20)}</button>
      <button type="button" class="ibtn" aria-label="More">${UI.svg(MORE, 20)}</button>
      <button type="button" class="ibtn" aria-label="Settings">${ic('settings', 20)}</button>
      <button type="button" class="ibtn" aria-label="Close">${ic('x', 20)}</button><span class="pd-cap">Live: the bookmark and calculator toggle.</span></div>`,
    build(S) { S.qa('[data-tog]').forEach(t => t.addEventListener('click', () => t.setAttribute('aria-pressed', String(t.getAttribute('aria-pressed') !== 'true')))); },
  });

  spec('A', 'A7', 'Segmented control',
    '<b>R12</b> thumb: paper with the amber ring plus a lifted key shadow, on a recessed track (<b>R22</b>); <b>MOTION C6</b> it slides on the soft spring, 420 (today 200 ease); keys move it at once. Dark thumb is one step lighter (DISCOVER K1).', {
    html: '<div class="pd-col" data-a></div><div class="pd-col" data-b style="margin-top:14px"></div>',
    build(S) {
      UI.seg(S.q('[data-a]'), ['Math', 'Reading and Writing'], { value: 'Math', label: 'Subject' });
      UI.seg(S.q('[data-b]'), [{ value: 's', label: 'Skills' }, { value: 'm', label: 'Map' }, { value: 'h', label: 'Habits' }], { value: 's', label: 'View' });
    },
  });

  spec('A', 'A8', 'Tabs',
    '<b>R13</b> one 2px underline; <b>MOTION C5</b> it slides on the soft spring 420 (today 200 ease), the label colour in 140; keys move it at once.', {
    html: '<div data-t></div>',
    build(S) {
      UI.tabs(S.q('[data-t]'), [{ id: 'all', label: 'All', n: 24 }, { id: 'open', label: 'Open', n: 6 }, { id: 'fixed', label: 'Fixed', n: 18 }, { id: 'saved', label: 'Saved', n: 3 }], { value: 'open', label: 'Mistakes' });
    },
  });

  /* ============================================================ B. Depth */
  const lv = [['e0', 'Card at rest'], ['e1', 'Clickable card, hover'], ['e2', 'Focal card'], ['e3', 'Menu, popover, toast'], ['e4', 'Sheet, palette']];
  const lvls = `<div class="pd-lvls">${lv.map(([k, t], i) => `<div class="pd-lv" data-e="${i}"><b>${k}</b>${t}</div>`).join('')}</div>`;
  spec('B', 'B1', 'Warm elevation scale, five levels, light and dark',
    '<b>R4</b> (Vercel materials structure, warm graphite tint <b>R6</b>): every level is a 1px alpha ring plus 1 to 3 soft layers; e3 replaces --shadow-float, e4 replaces --shadow-pop. Dark: black shadows at 4 to 8 times the alpha, a 4% top highlight, and higher surfaces get lighter (K1). Current: cards are tile + solid line, floats use the two shadow tokens.', {
    wide: true, cls: 'split', html: `<div class="pd-pair"><div class="pd-light">${lvls}</div><div class="pd-dark">${lvls}</div></div>`,
  });

  spec('B', 'B2', 'A card at rest and a clickable card',
    '<b>R4</b> alpha ring instead of the grey hairline, <b>R5</b> inner top highlight, a soft warm shadow (DISCOVER D2). Clickable: paper, hover steps to e2 and lifts 1px at most (<b>R9</b>), press .985.', {
    html: `<div class="pd-two"><div class="card"><div class="card-head"><h3>Percentages</h3><span class="meta">Proficient</span></div>
      <div class="meter"><span class="meter-k">14 of 18 right</span><span class="meter-n">78%</span><div class="meter-bar"><i style="--p:.78"></i></div></div><p class="pd-note">Last practised 2 days ago</p></div>
      <a class="card pd-tile" href="#B2"><span class="k">Practice test 4</span><span class="h3">Full test, 98 questions</span><span class="meta">2 h 14 min · Bluebook timing</span></a></div>`,
  });

  spec('B', 'B3', 'Today: Up next as the one raised hero',
    '<b>pages/today.md 3</b>: paper over the page, a warm layered shadow, a faint wash in the corner and a top sheen (<b>R7</b>); the lead task at 20/600 with a clock meta and the full 42px pill with a trailing play glyph. No other card on Today gets elevation.', {
    html: `<div class="v-cur card"><div class="card-head"><h3>Up next</h3><span class="meta">about 25 min · fits your 30-min goal</span></div><div class="pd-rows">
      <div><span><b>Linear Equations in One Variable</b><span class="meta">10 questions · 12 min · Plan</span></span><button type="button" class="pill sm">Start</button></div>
      <div><span><b>Words: 15 due</b><span class="meta">6 min</span></span><button type="button" class="quiet">Start</button></div>
      <div><span><b>Fix 4 mistakes</b><span class="meta">Circles, Percentages · 8 min</span></span><button type="button" class="quiet">Start</button></div></div></div>
      <div class="v-pro pd-hero"><div class="pd-row" style="justify-content:space-between"><span class="k">Up next</span><span class="meta">about 25 min · fits your 30-min goal</span></div>
      <div class="pd-col" style="gap:6px"><span class="pd-lead-t">Linear Equations in One Variable</span><span class="meta pd-meta-i">${ic('clock', 14)}12 min · 10 questions · from your plan</span></div>
      <div><button type="button" class="pill">Start ${ic('play', 16)}</button></div>
      <div class="pd-rows"><div><span><b>Words: 15 due</b><span class="meta">6 min</span></span><button type="button" class="quiet">Start</button></div>
      <div><span><b>Fix 4 mistakes</b><span class="meta">Circles, Percentages · 8 min</span></span><button type="button" class="quiet">Start</button></div></div></div>`,
  });

  spec('B', 'B4', 'Practice: the Your set card',
    '<b>pages/practice.md 3</b>: the only elevated, tinted surface on Practice. Preset trigger at its head, the figure "10" at 28/600 tabular, topic glyph chips, Start practice full width, the Diagnostic as one quiet foot line for a new student.', {
    html: `<div class="v-cur pd-cur-set"><div><p class="l1">10 questions · ~14 min</p><p class="l2">3 skills · 24 types · Mentor's pick</p></div><button type="button" class="pill wide">Start practice</button></div>
      <div class="v-pro pd-hero"><div class="pd-row" style="justify-content:space-between"><span class="k">Your set</span><button type="button" class="btn sm dd" aria-expanded="false" data-dd>Mentor's pick</button></div>
      <div class="pd-figline"><span class="pd-fig">10</span><span>questions · ~14 min</span></div>
      <div class="pd-chiprow" data-chips></div>
      <button type="button" class="pill wide">Start practice</button>
      <span class="meta">New here? <a class="link" href="#B4">Diagnostic, 20 questions</a></span></div>`,
    build(S) {
      const host = S.q('[data-chips]');
      [['linear_equations_in_one_variable', 'Linear Equations in One Variable'], ['circles', 'Circles']].forEach(([slug, name]) => {
        const c = frag(`<span class="pd-chip"></span>`);
        const g = UI.glyph ? UI.glyph(slug) : null;
        if (g) { g.style.cssText = 'width:18px;height:18px;--gb:transparent'; c.append(g); }
        c.append(name);
        host.append(c);
      });
      host.append(frag('<span class="pd-chip" style="padding-left:9px">+3</span>'));
      const dd = S.q('[data-dd]');
      dd.addEventListener('click', () => dd.setAttribute('aria-expanded', String(dd.getAttribute('aria-expanded') !== 'true')));
    },
  });

  const opts = [['A', '3'], ['B', '5'], ['C', '7'], ['D', '15']];
  const question = (cls = '') => `<div class="pd-sheet ${cls}"><div class="pd-qhead"><span>Question 7 of 10</span><span>Linear Equations in One Variable</span></div>
    <p class="q-stem">If 3x + 7 = 22, what is the value of x?</p>
    <div class="opts">${opts.map(([l, t]) => `<button type="button" class="opt" data-k="${l}"><span class="l">${l}</span><span class="t">${t}</span></button>`).join('')}</div></div>`;
  spec('B', 'B5', 'Practice: a raised question sheet over a warm tile',
    '<b>pages/runner.md 3</b> (practice only, never the test window): the page ground turns --tile, the question sits on a paper sheet (14px corners, one light from above); options are raised keys; a pick sinks in with the amber edge and a 3px wash halo. Phone: full bleed, no sheet.', {
    cls: 'pd-ground', html: question(),
    build(S) { S.qa('.opt').forEach(o => o.addEventListener('click', () => S.qa('.opt').forEach(x => x.classList.toggle('picked', x === o)))); },
  });

  /* ============================================================ C. Highlights and states */
  spec('C', 'C1', 'Selected chip',
    '<b>MOTION C8</b>: at rest a chip wears the .btn face (<b>R2</b>: white, light top edge, fine ring); picked keeps today\'s wash-2 and amber ring; a press and a 140 fill; the count turns ink when picked.', {
    html: '<div data-c></div>',
    build(S) {
      UI.chips(S.q('[data-c]'), [{ value: 'easy', label: 'Easy', n: 42 }, { value: 'medium', label: 'Medium', n: 57 }, { value: 'hard', label: 'Hard', n: 31 }, { value: 'timed', label: 'Timed' }], { multi: true, value: ['medium', 'hard'], label: 'Difficulty' });
    },
  });

  const navItems = [['today', 'Today', ''], ['practice', 'Practice', ''], ['review', 'Review', '6'], ['words', 'Words', '15'], ['tests', 'Tests', '']];
  spec('C', 'C2', 'Current nav item',
    '<b>MOTION N2</b>: one mark, the wash band alone (no side stripe), slides from the old item to the new, 260 ease-move, instead of the highlight jumping. Click another item; arrow keys move it at once.', {
    html: `<div class="pd-nav" role="group" aria-label="Sections"><span class="pd-navmark" aria-hidden="true"></span>${navItems.map(([k, t, m], i) =>
      `<button type="button" class="side-item"${i === 1 ? ' aria-current="page"' : ''}>${ic(k, 18)}<span class="side-text">${t}</span><span class="side-meta">${m}</span></button>`).join('')}</div>`,
    build(S) {
      const mark = S.q('.pd-navmark'), items = S.qa('.side-item');
      const place = still => {
        const cur = items.find(b => b.hasAttribute('aria-current'));
        mark.style.transition = still ? 'none' : '';
        mark.style.transform = `translateY(${cur.offsetTop}px)`;
        if (still) void mark.offsetWidth;
      };
      items.forEach(b => b.addEventListener('click', e => {
        items.forEach(x => x.removeAttribute('aria-current'));
        b.setAttribute('aria-current', 'page');
        place(e.detail === 0 || off());
      }));
      S.q('.pd-nav').addEventListener('keydown', e => {
        const i = items.indexOf(doc.activeElement), d = { ArrowDown: 1, ArrowUp: -1 }[e.key];
        if (i < 0 || !d) return;
        e.preventDefault();
        items[(i + d + items.length) % items.length].focus();
      });
      requestAnimationFrame(() => place(true));
      S.mode = () => requestAnimationFrame(() => place(true));
    },
  });

  const board = [['1', 'Aziza R.', '1,420'], ['2', 'Timur K.', '1,380'], ['3', 'Dilnoza S.', '1,310'], ['4', 'You', '1,240'], ['5', 'Bekzod A.', '1,190']];
  spec('C', 'C3', 'Row hover, picked row and your row',
    '<b>pages/practice.md 2</b> and <b>DISCOVER H3</b>: rows lose their hairlines; hover is a --tile-2 band with 8px corners in 140; a picked row is a wash-2 band; your row is the lighter wash band set in 600, its rank in amber-deep, with no side stripe and no badge. Row 2 is shown hovered; click a row to pick it.', {
    html: `<div class="pd-list" role="list" aria-label="Daily challenge, today">${board.map(([r, n, p], i) =>
      `<div class="pd-li${i === 3 ? ' you' : ''}${i === 1 ? ' is-hover' : ''}" role="listitem"><span class="rk">#${r}</span><span>${n}</span><span class="r">${p} pts</span></div>`).join('')}</div>`,
    build(S) {
      const rows = S.qa('.pd-li');
      const pick = r => rows.forEach(x => { x.setAttribute('aria-selected', String(x === r)); x.tabIndex = x === r ? 0 : -1; });
      rows.forEach((r, i) => { r.tabIndex = i ? -1 : 0; r.addEventListener('click', () => { pick(r); r.focus(); }); });
      S.q('.pd-list').addEventListener('keydown', e => {
        const i = rows.indexOf(doc.activeElement), d = { ArrowDown: 1, ArrowUp: -1 }[e.key];
        if (i < 0) return;
        if (d) { e.preventDefault(); const n = rows[(i + d + rows.length) % rows.length]; pick(n); n.focus(); }
      });
    },
  });

  spec('C', 'C4', 'Focus ring',
    '<b>R11</b>, revised after review: a thin amber-deep ring 2px out that follows each control\'s corners and leaves its own shadow under it; never ink, never thick. A text link gets no box: its underline turns amber-deep at 2px on a faint wash. A field is white with a fine edge (a grey well read as disabled); focused, the edge turns amber-deep with a soft halo. :focus-visible only; Tab through the last row.', {
    html: `<div class="pd-row"><div class="pd-col"><span class="pill is-focus" aria-hidden="true">Start practice</span><span class="pd-cap">Primary</span></div>
      <div class="pd-col"><span class="btn is-focus" aria-hidden="true">Options</span><span class="pd-cap">Secondary</span></div>
      <div class="pd-col"><span class="link is-focus" aria-hidden="true" style="padding:2px 0">Diagnostic</span><span class="pd-cap">Link</span></div></div>
      <div class="pd-row"><div class="pd-col" style="flex:1 1 240px"><span class="field is-focus" aria-hidden="true" style="display:flex;align-items:center">circles hard 10</span><span class="pd-cap">Field, focused</span></div>
      <div class="pd-col" style="flex:1 1 240px"><span class="field" aria-hidden="true" style="display:flex;align-items:center;color:var(--faint)">Search skills</span><span class="pd-cap">Field at rest</span></div></div>
      <div class="pd-row"><button type="button" class="pill">Start practice</button><button type="button" class="btn">Options</button><a class="link pd-flink" href="#C4">Diagnostic</a><input class="field sm" style="flex:1 1 200px;width:auto" placeholder="Tab here" aria-label="Try focus"></div>`,
  });

  spec('C', 'C5', 'Highlight, search hit and selection',
    '<b>DISCOVER H4</b>: a highlight is wash-2 with 2px corners and a thin amber underline that wraps cleanly across lines; a search hit is the lighter wash with an amber hairline; the text selection is a warmer orange. Select some words to see it.', {
    html: `<p class="pd-pass">Arctic terns follow a route of nearly 70,000 kilometers each year, the longest <mark>migration</mark> recorded for any animal. Researchers tracking eleven birds found that the <mark class="hit">terns</mark> rarely fly in a straight line; instead, they <mark>follow prevailing winds across the Atlantic</mark>, trading distance for energy.</p>`,
  });

  spec('C', 'C6', 'New and unread markers, badges',
    '<b>RE linear statusPulse</b> (REFERENCES 1.1, R19 done pulse): a new dot pings once (600ms, never loops) and carries a 2px paper ring so it reads on any row; the count badge gets the pill\'s edge (<b>R1b</b> in small); "New" is an outlined amber word, not a filled block.', {
    replay: true,
    html: `<div class="pd-mk"><div class="side-item">${ic('review', 18)}<span class="side-text">Review</span><span class="side-meta"><span class="badge n">6</span></span></div>
      <div class="side-item">${ic('words', 18)}<span class="side-text">Words</span><span class="side-meta"><span class="badge new">New</span></span></div>
      <div class="side-item">${ic('results', 18)}<span class="side-text">Your test 4 report is ready</span><span class="side-meta"><span class="pd-dot"></span></span></div></div>
      <div class="pd-row" style="margin-top:14px"><span class="badge">Resume</span><span class="badge n">12</span><span class="badge soft">Example</span><span class="badge ink">Hard</span><span class="badge new">New</span></div>`,
    build(S) {
      S.replay = () => { const d = S.q('.pd-dot'); d.classList.remove('ping'); void d.offsetWidth; if (!off()) d.classList.add('ping'); };
      S.replay();
    },
  });

  /* ============================================================ D. Motion */
  // R14 / MOTION D1: only the changed digits move; the new one comes from below when the value rises (above when it
  // falls), the old one leaves the other way, on the spring (370). Never on load. Same length only; else a plain swap.
  function roll(el, to) {
    const from = el._v ?? el.textContent, text = String(to);
    el._v = text;
    el._rid = (el._rid || 0) + 1;
    const n = el._rid;
    if (off() || from.length !== text.length) { el.textContent = text; return; }
    const up = +text.replace(/\D/g, '') >= +from.replace(/\D/g, ''), dir = up ? 1 : -1;
    el.replaceChildren(...[...text].map((ch, i) => ch === from[i] ? doc.createTextNode(ch)
      : frag(`<span class="c"><span>${ch}</span><span aria-hidden="true">${from[i]}</span></span>`)));
    const runs = [];
    $$('.c', el).forEach(c => {
      const [nw, old] = c.children;
      runs.push(anim(nw, [{ transform: `translateY(${.6 * dir}em)`, opacity: 0 }, { transform: 'none', opacity: 1 }], { duration: 370, easing: SPRING() }));
      runs.push(anim(old, [{ transform: 'none', opacity: 1 }, { transform: `translateY(${-.6 * dir}em)`, opacity: 0 }], { duration: 370, easing: SPRING(), fill: 'forwards' }));
    });
    Promise.all(runs.map(a => a.finished)).then(() => { if (el._rid === n) el.textContent = text; }, () => {});
  }

  spec('D', 'D1', 'Page entry stagger, capped',
    '<b>MOTION M1</b> (<b>R15</b> at app scale): direct children rise 8px and fade in, 200 ease, 30ms apart, at most 6 steps (later blocks arrive with the 6th); the block holding the page\'s primary is never delayed. First paint of a page only, never on back navigation. Current: main fades for 120ms (N1).', {
    replay: true,
    html: `<div class="pd-mini" data-page>
      <div><div class="h1" style="font-size:20px">Good evening, Malika</div><div class="meta" style="margin-top:4px">Monday, October 19 · SAT in 40 days</div></div>
      <div class="pd-blk hero" data-m-now><span><b>Linear Equations in One Variable</b><span class="meta" style="display:block">12 min · 10 questions</span></span><button type="button" class="pill sm">Start</button></div>
      ${['Question of the day', 'Fix 4 mistakes', 'Score estimate 540–580', 'Pace: on track for 650', 'Daily challenge: #4 of 30', 'Words: 15 due'].map(t => `<div class="pd-blk">${t}</div>`).join('')}</div>`,
    build(S) {
      S.replay = () => {
        const host = S.q('[data-page]');
        if (!S.pro()) { anim(host, [{ opacity: 0 }, { opacity: 1 }], { duration: 120 }); return; }
        let k = 0;
        [...host.children].forEach(el => {
          const i = el.hasAttribute('data-m-now') ? 0 : Math.min(k++, 5);
          enter(el, [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], { duration: 200, delay: off() ? 0 : i * 30, fill: 'backwards' });
        });
      };
    },
  });

  // FLIP: measure, change, then slide what moved from where it was (200 ease-move)
  const flip = (host, mutate) => {
    const first = new Map([...host.children].map(k => [k, k.getBoundingClientRect().top]));
    mutate();
    if (off()) return;
    [...host.children].forEach(k => {
      const f = first.get(k);
      const d = f === undefined ? 0 : f - k.getBoundingClientRect().top;
      if (d) anim(k, [{ transform: `translateY(${d}px)` }, { transform: 'none' }], { duration: 200, easing: MOVE });
    });
  };
  const pool = ['Right Triangles and Trigonometry · question 3', 'Linear Functions · question 15', 'Area and Volume · question 6', 'Equivalent Expressions · question 11', 'Probability and Conditional Probability · question 2'];
  spec('D', 'D2', 'List: a row added, a row removed',
    '<b>MOTION L1, L2</b> (<b>R16</b>): a new row fades in from 4px below, 200 ease, and the rows under it make room by FLIP, 200 ease-move; a removed row fades and settles to .98 in 140, then the gap closes by FLIP. Current: rows appear and vanish in one frame.', {
    html: '<div class="pd-flip" data-list></div><div class="pd-acts"><button type="button" class="btn sm" data-add>Log a mistake</button></div>',
    build(S) {
      const list = S.q('[data-list]'), add = S.q('[data-add]');
      let n = 0;
      const row = t => {
        const [skill, q] = t.split(' · ');
        const r = frag(`<div><span>${skill}<span class="meta">${q}</span></span><button type="button" class="btn sm">Fixed</button></div>`);
        const b = $('button', r);
        b.setAttribute('aria-label', `Mark ${skill}, ${q} fixed`);
        b.addEventListener('click', () => remove(r));
        return r;
      };
      ['Circles · question 12', 'Percentages · question 4', 'Systems of Two Linear Equations in Two Variables · question 9'].forEach(t => list.append(row(t)));
      async function remove(r) {
        if (r._out) return;
        r._out = true;
        const next = r.nextElementSibling || r.previousElementSibling;
        if (S.pro() && !off()) {
          r.style.pointerEvents = 'none';
          await anim(r, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'scale(.98)' }], { duration: 140, fill: 'forwards' }).finished.catch(() => {});
        }
        if (S.pro()) flip(list, () => r.remove()); else r.remove();
        (next && next.isConnected ? $('button', next) : add).focus();
      }
      add.addEventListener('click', () => {
        const r = row(pool[n++ % pool.length]);
        if (!S.pro()) { list.prepend(r); return; }
        flip(list, () => list.prepend(r));
        enter(r, [{ opacity: 0, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }], { duration: 200 });
      });
    },
  });

  spec('D', 'D3', 'Sheet: open and close',
    '<b>MOTION S1, S2</b> (<b>R17</b>): on a desktop it enters from 8px below at .98, 260 ease, backdrop 200, and now also leaves (fades 4px down in 180, backdrop 140) where today it vanishes. Under 760px a bottom sheet rises on the spring (370) and drops in 200. Surface <b>e4</b>. Current: the real UI.sheet.', {
    html: `<button type="button" class="btn" data-open>Save as preset</button>
      <dialog class="sheet" data-size="s" aria-labelledby="d3-h"><div class="sheet-head"><h2 id="d3-h">Save as preset</h2><button type="button" class="x" aria-label="Close" data-x>${ic('x', 18)}</button></div>
      <div class="sheet-body"><label class="label" for="d3-f">Name</label><input class="field" id="d3-f" value="Weak spots, hard"><p class="pd-note">3 skills · 10 questions · Hard only</p></div>
      <div class="sheet-foot"><button type="button" class="btn" data-x>Cancel</button><button type="button" class="pill" data-x>Save</button></div></dialog>`,
    build(S) {
      const dlg = S.q('dialog'), live = [];
      const phone = () => matchMedia('(max-width: 759px)').matches;
      const bd = (kf, o) => { try { return dlg.animate(kf, { easing: EASE, ...o, pseudoElement: '::backdrop' }); } catch (_) { return null; } };
      const clear = () => { live.splice(0).forEach(a => a && a.cancel()); };
      let closing = false;
      S.q('[data-open]').addEventListener('click', () => {
        if (!S.pro()) {
          UI.sheet({ title: 'Save as preset', size: 's', body: frag('<div><label class="label" for="d3-c">Name</label><input class="field" id="d3-c" value="Weak spots, hard"></div>'), actions: [{ label: 'Cancel' }, { label: 'Save', primary: true }] });
          return;
        }
        clear();
        dlg.showModal();
        if (off()) { live.push(anim(dlg, [{ opacity: 0 }, { opacity: 1 }], { duration: 120 })); return; }
        live.push(phone() ? anim(dlg, [{ transform: 'translateY(100%)' }, { transform: 'none' }], { duration: 370, easing: SPRING() })
          : anim(dlg, [{ opacity: 0, transform: 'translateY(8px) scale(.98)' }, { opacity: 1, transform: 'none' }], { duration: 260 }));
        live.push(bd([{ opacity: 0 }, { opacity: 1 }], { duration: 200 }));
      });
      async function close() {
        if (closing || !dlg.open) return;
        closing = true;
        if (!off()) {
          const a = phone() ? anim(dlg, [{ transform: 'none' }, { transform: 'translateY(100%)' }], { duration: 200, fill: 'forwards' })
            : anim(dlg, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(4px)' }], { duration: 180, fill: 'forwards' });
          live.push(a, bd([{ opacity: 1 }, { opacity: 0 }], { duration: phone() ? 200 : 140, fill: 'forwards' }));
          await a.finished.catch(() => {});
        }
        dlg.close();
        clear();
        closing = false;
      }
      S.qa('[data-x]').forEach(b => b.addEventListener('click', close));
      dlg.addEventListener('cancel', e => { e.preventDefault(); close(); });
      dlg.addEventListener('click', e => { if (e.target === dlg) close(); });
    },
  });

  const presets = [['Mentor\'s pick', '3 skills you are close on'], ['Weakest 3', 'Circles, Percentages, Linear Functions'], ['Mixed review', 'Everything you have practised'], ['Full section mix', 'Like the real Math section']];
  spec('D', 'D4', 'Menu: scales in from its trigger, fades out',
    '<b>MOTION S3, S4</b> (Emil: origin at the trigger): opacity and scale .96 from the trigger\'s corner, 160 ease (the More menu opens upward, so it grows from its bottom right); exit is a 100ms fade where today it vanishes; opened by a key it shows at once. A pick flashes its row for 80ms (<b>DISCOVER H2</b>). Surface <b>e3</b>.', {
    html: `<div class="pd-menu-host">
      <button type="button" class="btn dd" aria-haspopup="menu" aria-expanded="false" data-t="a" style="position:absolute;left:0;top:0">Mentor's pick</button>
      <div class="pd-menu" role="menu" aria-label="Presets" data-m="a" hidden style="left:0;top:44px;transform-origin:top left">${presets.map(([t, s], i) =>
        `<button type="button" role="menuitemradio" aria-checked="${i === 0}" data-name="${t}"><span>${t}<span class="sub">${s}</span></span></button>`).join('')}</div>
      <button type="button" class="btn icon" aria-label="More" aria-haspopup="menu" aria-expanded="false" data-t="b" style="position:absolute;right:0;bottom:0">${UI.svg(MORE, 18)}</button>
      <div class="pd-menu" role="menu" aria-label="More" data-m="b" hidden style="right:0;bottom:44px;transform-origin:bottom right">${['Save as preset', 'Copy link', 'My defaults'].map(t =>
        `<button type="button" role="menuitem">${t}</button>`).join('')}</div></div>`,
    build(S) {
      const pair = k => [S.q(`[data-t="${k}"]`), S.q(`[data-m="${k}"]`)];
      const items = m => $$('[role^="menuitem"]', m);
      let openK = null;
      function show(k, e) {
        const [t, m] = pair(k);
        if (openK) hide(openK, true);
        openK = k;
        m.getAnimations().forEach(a => a.cancel());
        m.hidden = false;
        t.setAttribute('aria-expanded', 'true');
        if (e && e.detail === 0) { items(m)[0].focus(); return; }          // by key: at once
        if (S.pro()) enter(m, [{ opacity: 0, transform: 'scale(.96)' }, { opacity: 1, transform: 'none' }], { duration: 160 });
        else anim(m, [{ opacity: 0, transform: 'translateY(4px) scale(.98)' }, { opacity: 1, transform: 'none' }], { duration: 150 });   // today's pop
      }
      async function hide(k, instant, back) {
        const [t, m] = pair(k);
        if (openK === k) openK = null;
        t.setAttribute('aria-expanded', 'false');
        if (back) t.focus();
        if (S.pro() && !instant && !off()) await anim(m, [{ opacity: 1 }, { opacity: 0 }], { duration: 100, fill: 'forwards' }).finished.catch(() => {});
        if (openK !== k) { m.hidden = true; m.getAnimations().forEach(a => a.cancel()); }
      }
      ['a', 'b'].forEach(k => {
        const [t, m] = pair(k);
        t.addEventListener('click', e => (openK === k ? hide(k) : show(k, e)));
        items(m).forEach(it => it.addEventListener('click', async e => {
          if (it.dataset.name) { items(m).forEach(x => x.setAttribute('aria-checked', String(x === it))); t.textContent = it.dataset.name; }
          if (S.pro() && !off() && e.detail !== 0) { it.style.background = 'var(--wash)'; await wait(80); it.style.background = ''; }
          hide(k, e.detail === 0, true);
        }));
        m.addEventListener('keydown', e => {
          const list = items(m), i = list.indexOf(doc.activeElement);
          if (e.key === 'Escape') { e.preventDefault(); hide(k, true, true); }
          else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); list[(i + (e.key === 'ArrowDown' ? 1 : -1) + list.length) % list.length].focus(); }
          else if (e.key === 'Tab') hide(k, true);
        });
      });
      doc.addEventListener('pointerdown', e => { if (openK && !pair(openK).some(x => x.contains(e.target))) hide(openK); });
    },
  });

  const msgs = ['Saved to your set', 'Added to Words: ubiquitous', 'Plan updated: 62 study days to Nov 7', 'Mistake fixed: Circles, question 12'];
  spec('D', 'D5', 'Toast stack: enter, stack, exit',
    '<b>R18</b> (Geist stack): the newest in front, the next 8px higher at .95, the third 16px at .9, older ones fade; hover or focus fans them out and pauses their timers. <b>MOTION S6</b>: enter from 8px below in 200, leave with a 140 fade; an Undo toast carries a 2px countdown line. Surface <b>e3</b>. Current: the real UI.toast, at the bottom of the window.', {
    html: `<div class="pd-row"><button type="button" class="btn sm" data-add>Show a toast</button><button type="button" class="btn sm" data-undo>Delete a note</button></div>
      <div class="pd-toast-host" style="margin-top:14px"><div class="pd-toasts" aria-live="polite"></div></div>`,
    build(S) {
      const host = S.q('.pd-toasts');
      let k = 0, open = false;
      const list = () => $$('.toast:not(.out)', host);
      function layout() {
        let y = 0;
        list().forEach((t, i) => {
          t.style.zIndex = String(20 - i);
          if (open) { t.style.transform = `translateY(${-y}px)`; t.style.opacity = i > 3 ? '0' : '1'; y += t.offsetHeight + 8; }
          else { t.style.transform = i ? `translateY(${-8 * i}px) scale(${1 - .05 * i})` : 'none'; t.style.opacity = i > 2 ? '0' : '1'; }
        });
      }
      async function close(t, now) {
        if (t.classList.contains('out')) return;
        t.classList.add('out');
        t._timer.cancel();
        layout();
        const tf = t.style.transform && t.style.transform !== 'none' ? t.style.transform : '';
        if (!now && !off()) await anim(t, [{ opacity: 1, transform: tf || 'none' }, { opacity: 0, transform: `${tf} translateY(4px)`.trim() }], { duration: 140, fill: 'forwards' }).finished.catch(() => {});
        t.remove();
      }
      function add(text, undo) {
        if (!S.pro()) { UI.toast(text, undo ? { undo: () => UI.toast('Note restored') } : {}); return; }
        const t = frag(`<div class="toast" role="status"><span class="toast-t">${text}</span>${undo ? '<button type="button" class="act">Undo</button>' : ''}<button type="button" class="x" aria-label="Dismiss">${ic('x', 16)}</button><i class="cd" aria-hidden="true"></i></div>`);
        host.prepend(t);
        layout();
        enter(t, [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], { duration: 200 });
        t._timer = $('.cd', t).animate([{ transform: 'scaleX(1)' }, { transform: 'scaleX(0)' }], { duration: undo ? 6000 : 4000, easing: 'linear', fill: 'forwards' });
        if (open) t._timer.pause();
        t._timer.finished.then(() => close(t), () => {});
        $('.x', t).addEventListener('click', () => close(t));
        const act = $('.act', t);
        if (act) act.addEventListener('click', () => { close(t); add('Note restored'); });
        list().slice(5).forEach(x => close(x, true));
      }
      const fan = on => { if (open === on) return; open = on; list().forEach(t => (on ? t._timer.pause() : t._timer.play())); layout(); };
      host.addEventListener('pointerenter', () => fan(true));
      host.addEventListener('pointerleave', () => fan(host.contains(doc.activeElement)));
      host.addEventListener('focusin', () => fan(true));
      host.addEventListener('focusout', e => { if (!host.contains(e.relatedTarget)) fan(false); });
      S.q('[data-add]').addEventListener('click', () => add(msgs[k++ % msgs.length]));
      S.q('[data-undo]').addEventListener('click', () => add('Note deleted', true));
    },
  });

  spec('D', 'D6', 'Digit roll on a score',
    '<b>R14</b> (Stripe ticker, NumberFlow) with <b>MOTION D1</b>: only the digits that change move; up comes from below, down from above; the old digit leaves the other way, both on the spring (370). Tabular figures, so nothing shifts. Never on load. Current: UI.roll scrolls a 0 to 9 column in 220.', {
    html: `<div class="k">Estimated score</div><div class="pd-score"><span class="num pd-roll" data-n>560</span><span class="band pd-roll" data-b>540–580</span></div>
      <div class="pd-acts"><button type="button" class="btn sm" data-d="20">Score +20</button><button type="button" class="btn sm" data-d="-20">Score −20</button><button type="button" class="btn sm" data-d="110">Score +110</button></div>`,
    build(S) {
      const n = S.q('[data-n]'), b = S.q('[data-b]');
      let v = 560;
      S.qa('[data-d]').forEach(x => x.addEventListener('click', () => {
        v = Math.max(400, Math.min(780, v + +x.dataset.d));
        if (v === 780 && +x.dataset.d > 0 && n.textContent === '780') v = 560;
        const band = `${v - 20}–${v + 20}`;
        if (S.pro()) { roll(n, v); roll(b, band); } else { UI.roll(n, v); UI.roll(b, band); }
      }));
      S.mode = () => { n._v = null; b._v = null; n.textContent = String(v); b.textContent = `${v - 20}–${v + 20}`; };
    },
  });

  spec('D', 'D7', 'Tick meter filling, progress fill',
    '<b>MOTION D3</b>: new ticks light left to right, 20ms apart, each in 240; at the goal the meter reads done. <b>R21</b> progress fill: a recessed track and a lit amber fill that grows by clip-path (no width animation), 480 on the first reveal and 240 on a change. Current: all ticks at once; the bar animates its width in 200.', {
    replay: true,
    html: `<div data-m></div><div style="margin-top:18px"><div class="meter lg"><span class="meter-k">This week</span><span class="meter-n" data-pn>3 of 5 study days</span><div class="meter-bar pd-fill" data-pb><i></i></div></div></div>
      <div class="pd-acts"><button type="button" class="btn sm" data-plus>Practise 6 min</button><button type="button" class="btn sm" data-day>Finish a study day</button></div>`,
    build(S) {
      let v = 18, days = 3;
      const m = UI.meter(S.q('[data-m]'), { label: 'Today', value: v, max: 30, unit: 'min', ticks: 10 });
      const pb = S.q('[data-pb]'), pn = S.q('[data-pn]');
      const lit = () => $$('.meter-bar > i[data-on]', m.el).length;
      const setV = (to, from) => {
        m.set({ value: to });
        if (!S.pro() || off()) return;
        const fresh = $$('.meter-bar > i[data-on]', m.el).slice(from);
        fresh.forEach(t => t.removeAttribute('data-on'));
        fresh.forEach((t, i) => setTimeout(() => t.setAttribute('data-on', ''), 20 * (i + 1)));
      };
      const setDays = (d, ms) => { pb.style.setProperty('--pd-d', `${ms}ms`); pb.style.setProperty('--p', d / 5); pn.textContent = `${d} of 5 study days`; };
      setDays(days, 0);
      S.q('[data-plus]').addEventListener('click', () => { const was = lit(); v = v >= 30 ? 0 : Math.min(30, v + 6); setV(v, v ? was : 0); });
      S.q('[data-day]').addEventListener('click', () => { days = days >= 5 ? 3 : days + 1; setDays(days, 240); });
      S.replay = () => {
        m.set({ value: 0 });
        setDays(0, 0);
        void pb.offsetWidth;
        requestAnimationFrame(() => { setV(v, 0); setDays(days, 480); });
      };
    },
  });

  const tasks = [['Fix 4 mistakes', '8 min'], ['Words: 15 due', '6 min'], ['Linear Functions, 10 questions', '12 min']];
  spec('D', 'D8', 'Task done: tick draws, title strikes through',
    '<b>MOTION C9</b>: the box fills and its check draws in 160; then a line strikes the title (220, after 80); <b>R19</b> one done pulse rings out from the box (600, once). Today\'s "task done" (pages/today.md 7). Current: the tick and the line appear at once.', {
    html: `<div class="pd-list">${tasks.map(([t, m]) => `<div class="pd-task"><button type="button" class="pd-box" role="checkbox" aria-checked="false" aria-label="Done: ${t}">${CK}</button><span class="t">${t}</span><span class="meta">${m}</span></div>`).join('')}</div>`,
    build(S) {
      S.qa('.pd-box').forEach(b => b.addEventListener('click', () => {
        const on = b.getAttribute('aria-checked') !== 'true';
        b.setAttribute('aria-checked', String(on));
        b.closest('.pd-task').classList.toggle('done', on);
        if (!on || !S.pro() || off()) return;
        draw($('.pd-ck', b), 160);
        const ring = frag('<span class="pd-pulse" aria-hidden="true"></span>');
        b.append(ring);
        anim(ring, [{ opacity: .7, transform: 'scale(1)' }, { opacity: 0, transform: 'scale(1.9)' }], { duration: 600, easing: 'cubic-bezier(.215, .61, .355, 1)' }).finished.then(() => ring.remove(), () => ring.remove());
      }));
    },
  });

  spec('D', 'D9', 'Practice: right-answer stamp, wrong-answer moment',
    '<b>MOTION F1</b>: the key fills in 120, its letter disc settles from .85 on the pop spring (the only bounce in the flow), the verdict rises 4px in 200 and its check draws, the progress segment fills (F11, 240). <b>F2</b>: the key fills with no pop, the pick dims and a drawn line strikes it in 160; no shake, no red. Practice only: the test window stays still. Pick an option and press Check, or use the two Play buttons.', {
    cls: 'pd-ground', replay: true,
    html: `<div class="pd-segs" aria-hidden="true"><i data-on="r"></i><i data-on="r"></i><i data-on="w"></i><i data-on="r"></i><i data-on="r"></i><i data-on="r"></i><i data-cur></i><i></i><i></i><i></i></div>${question()}
      <div class="pd-acts"><button type="button" class="pill sm" data-check>Check</button><button type="button" class="btn sm" data-right>Play right</button><button type="button" class="btn sm" data-wrong>Play wrong</button></div>`,
    build(S) {
      const sheet = S.q('.pd-sheet'), box = S.q('.opts'), seg = S.q('[data-cur]'), all = S.qa('.opt');
      const slot = frag('<div></div>');
      sheet.append(slot);
      let last = 'B';
      const reset = () => { box.classList.remove('done'); all.forEach(x => x.classList.remove('ok', 'no', 'picked')); slot.replaceChildren(); seg.removeAttribute('data-on'); };
      all.forEach(o => o.addEventListener('click', () => { if (box.classList.contains('done')) reset(); all.forEach(x => x.classList.toggle('picked', x === o)); }));
      function check(k) {
        reset();
        void box.offsetWidth;                // a replay restarts the fills from rest
        last = k;
        const pick = all.find(o => o.dataset.k === k), key = all.find(o => o.dataset.k === 'B'), right = pick === key;
        box.classList.add('done');
        key.classList.add('ok');
        if (!right) pick.classList.add('no');
        seg.setAttribute('data-on', right ? 'r' : 'w');
        const v = frag(right ? `<div class="pd-verdict right" role="status"><span class="g">${CK}</span>Right. 3x = 15, so x = 5.</div>`
          : `<div class="pd-verdict wrong" role="status"><span class="g">${ic('x', 16)}</span>Not quite. The answer is B, 5.</div>`);
        slot.append(v);
        if (!S.pro()) { anim(v, [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], { duration: 240 }); return; }   // today's rise
        if (off()) return;
        enter(v, [{ opacity: 0, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }], { duration: 200 });
        anim(seg, [{ transform: 'scaleX(0)' }, { transform: 'none' }], { duration: 240 });
        if (right) {
          anim($('.l', key), [{ transform: 'scale(.85)' }, { transform: 'none' }], { duration: 570, easing: POP() });
          anim($('.g', v), [{ transform: 'scale(.8)' }, { transform: 'none' }], { duration: 570, easing: POP() });
          draw($('.pd-ck', v), 240, 60);
        } else {
          anim($('.t', pick), [{ backgroundSize: '0% 1px' }, { backgroundSize: '100% 1px' }], { duration: 160 });
        }
      }
      S.q('[data-check]').addEventListener('click', () => { const p = all.find(o => o.classList.contains('picked')); if (p) check(p.dataset.k); });
      S.q('[data-right]').addEventListener('click', () => check('B'));
      S.q('[data-wrong]').addEventListener('click', () => check('C'));
      S.replay = () => check(last);
    },
  });

  spec('D', 'D10', 'Goal ring closing',
    '<b>MOTION D4, F6</b>: the arc sweeps from the old minutes to the new, 600 ease (a registered custom property lets the conic gradient animate), the figure rolls, then one beat (scale 1, 1.06, 1 in 400), the check draws and the line reads "Goal met". Once a day. Current: the arc and the figure jump.', {
    replay: true,
    html: `<div class="pd-ring-row"><span class="ring pd-ring" style="--p:.6;--pro-ring:.6"><span class="pd-roll" data-v>18</span></span><div><div class="h3" data-h>Today</div><div class="meta" data-m>18 of 30 min</div></div></div>
      <div class="pd-acts"><button type="button" class="btn sm" data-go>Practise 12 min</button></div>`,
    build(S) {
      const ring = S.q('.pd-ring'), v = S.q('[data-v]'), hd = S.q('[data-h]'), mt = S.q('[data-m]');
      const setP = (p, still) => {
        if (still) ring.style.transition = 'none';
        ring.style.setProperty('--p', p);
        ring.style.setProperty('--pro-ring', p);
        if (still) { void ring.offsetWidth; ring.style.transition = ''; }
      };
      let run = 0;
      async function meet() {
        const me = ++run;
        setP(.6, true);
        v._v = null; v.textContent = '18'; hd.textContent = 'Today'; mt.textContent = '18 of 30 min';
        await new Promise(r => requestAnimationFrame(r));
        setP(1);
        mt.textContent = '30 of 30 min';
        if (!S.pro() || off()) { v.innerHTML = CK; hd.textContent = 'Goal met'; return; }
        roll(v, 30);
        await wait(600);
        if (me !== run) return;
        anim(ring, [{ transform: 'scale(1)' }, { transform: 'scale(1.06)' }, { transform: 'scale(1)' }], { duration: 400 });
        v._v = null;
        v.innerHTML = CK;
        draw($('.pd-ck', v));
        swapText(hd, 'Goal met');
      }
      S.q('[data-go]').addEventListener('click', meet);
      S.replay = meet;
    },
  });

  spec('D', 'D11', 'Streak extended',
    '<b>MOTION F5</b> (<b>DISCOVER F1</b> tier 2): after the first session of the day the number rolls up on the spring while the flame goes from outline to filled amber in 300 and settles from .85 on the pop spring. Once a day; milestones (7, 30, 100) add one toast, no confetti. Current: the number and the flame change in one frame.', {
    replay: true,
    html: `<div class="pd-streak"><span class="pd-flame">${UI.svg(UI.ICON.flame, 28, 'o')}${UI.svg(UI.ICON.flame, 28, 'f')}</span><span class="num pd-roll" data-n>23</span><span class="meta">day streak</span></div>
      <div class="pd-acts"><button type="button" class="btn sm" data-go>Finish today's first session</button></div>`,
    build(S) {
      const fl = S.q('.pd-flame'), n = S.q('[data-n]');
      const go = () => {
        fl.classList.remove('on');
        n._v = null; n.textContent = '23';
        void fl.offsetWidth;
        requestAnimationFrame(() => {
          fl.classList.add('on');
          if (!S.pro()) { n.textContent = '24'; return; }
          roll(n, 24);
          if (!off()) anim(fl, [{ transform: 'scale(.85)' }, { transform: 'none' }], { duration: 570, easing: POP() });
        });
      };
      S.q('[data-go]').addEventListener('click', go);
      S.replay = go;
    },
  });

  spec('D', 'D12', 'Skeleton to content',
    '<b>DISCOVER E2</b>: nothing for the first 300ms (most loads finish by then), then a static skeleton at the final size (no shimmer, ui.css rule 8); <b>MOTION M2</b>: the content fades in over it, 160 ease, no travel. Current: the skeleton shows at once and the content swaps in one frame.', {
    replay: true,
    html: '<div class="card pd-skel-card" data-c></div>',
    build(S) {
      const c = S.q('[data-c]');
      const content = '<div><div class="card-head"><h3>Score estimate</h3><span class="meta">from 3 tests</span></div><div class="pd-score"><span class="num" style="font-size:34px">560</span><span class="band">540–580</span></div><p class="pd-note">Up 30 since your last test</p></div>';
      const skel = '<span class="skel line lg" style="width:40%"></span><span class="skel num"></span><span class="skel line" style="width:70%"></span>';
      let run = 0;
      c.innerHTML = content;
      S.replay = async () => {
        const me = ++run;
        if (!S.pro()) { c.innerHTML = skel; await wait(1200); if (me === run) c.innerHTML = content; return; }
        c.innerHTML = '';
        await wait(300);
        if (me !== run) return;
        c.innerHTML = skel;
        await wait(900);
        if (me !== run) return;
        c.innerHTML = content;
        anim(c.firstElementChild, [{ opacity: 0 }, { opacity: 1 }], { duration: off() ? 120 : 160 });
      };
    },
  });

  /* ============================================================ E. Calm layout */
  const ALG = [['Linear Equations in One Variable', .7, 1], ['Linear Functions', .4], ['Linear Equations in Two Variables', 0], ['Systems of Two Linear Equations in Two Variables', .55, 1, 2], ['Linear Inequalities in One or Two Variables', 0]];
  const GEO = [['Area and Volume', 0], ['Lines, Angles, and Triangles', .8], ['Right Triangles and Trigonometry', 0], ['Circles', .3, 1, 1]];
  const bar = v => `<span class="pd-mbar" aria-hidden="true"><i style="--v:${v}"></i></span>`;
  const tri = (label, on) => `<button type="button" class="pd-tri" role="checkbox" aria-checked="${on}" aria-label="${label}"></button>`;
  const segStatic = (label, opts) => `<div class="seg" role="radiogroup" aria-label="${label}">${opts.map((o, i) => `<button type="button" role="radio" aria-checked="${i === 0}">${o}</button>`).join('')}</div>`;
  const dcard = (name, rows, pts) => `<div class="dcard" data-g><div class="dhead">${tri(`All of ${name}`, 'mixed')}<div style="flex:1;min-width:0"><div class="dname">${name}</div><div class="dsel">${pts}</div>${bar(.45)}</div></div>
    <div class="dbody">${rows.map(([n, v, on, open]) => `<div class="srow" data-r${on ? ' data-on' : ''}>${tri(n, !!on)}<span>${n}</span><span style="display:flex;gap:6px;align-items:center">${open ? `<span class="badge n">${open}</span>` : ''}${bar(v)}</span></div>`).join('')}</div></div>`;
  const grp = (name, rows, pts) => `<div class="grp" data-g><div class="grp-h">${tri(`All of ${name}`, 'mixed')}<span>${name}</span><span class="meta">${pts}</span></div>
    ${rows.map(([n, v, on, open]) => `<div class="sk" data-r${on ? ' data-on' : ''}>${tri(n, !!on)}<span>${n}</span><span class="r">${open ? `<span class="badge soft">${open}</span>` : ''}${v ? bar(v) : ''}</span></div>`).join('')}</div>`;
  const setCur = '<div class="pd-cur-set"><div><p class="l1">10 questions · ~14 min</p><p class="l2">3 skills · 24 types · Mentor\'s pick</p></div><button type="button" class="pill wide">Start practice</button></div>';
  const setPro = `<div class="pd-hero"><div class="pd-row" style="justify-content:space-between"><span class="k">Your set</span><button type="button" class="btn sm dd" aria-expanded="false" data-dd>Mentor's pick</button></div>
    <div class="pd-figline"><span class="pd-fig">10</span><span>questions · ~14 min</span></div><div class="pd-chiprow" data-chips></div>
    <button type="button" class="pill wide">Start practice</button><span class="meta">New here? <a class="link" href="#E1">Diagnostic, 20 questions</a></span></div>`;
  const fillChips = host => {
    [['linear_equations_in_one_variable', 'Linear Equations in One Variable'], ['circles', 'Circles'], ['', '+1']].forEach(([slug, name]) => {
      const c = frag('<span class="pd-chip"></span>');
      let g = null;
      try { g = slug && UI.glyph ? UI.glyph(slug) : null; } catch (_) { g = null; }
      if (!slug) c.style.paddingLeft = '9px';
      if (g) { g.style.cssText = 'width:18px;height:18px;--gb:transparent'; c.append(g); }
      c.append(name);
      host.append(c);
    });
  };
  // the tree's checkboxes: a row toggles, a group's box sets all of its rows, the head box and count follow
  function wireTree(box, count, fmt) {
    const rows = $$('[data-r]', box), master = $('[data-all]', box);
    const state = rs => { const on = rs.filter(r => r.hasAttribute('data-on')).length; return on === 0 ? 'false' : on === rs.length ? 'true' : 'mixed'; };
    const sync = () => {
      rows.forEach(r => $('.pd-tri', r).setAttribute('aria-checked', String(r.hasAttribute('data-on'))));
      $$('[data-g]', box).forEach(g => $('.pd-tri', g).setAttribute('aria-checked', state($$('[data-r]', g))));
      if (master) master.setAttribute('aria-checked', state(rows));
      if (count) count.textContent = fmt(rows.filter(r => r.hasAttribute('data-on')).length, rows.length);
    };
    rows.forEach(r => r.addEventListener('click', () => { r.toggleAttribute('data-on'); sync(); }));
    $$('[data-g]', box).forEach(g => $('.pd-tri', g).addEventListener('click', e => {
      e.stopPropagation();
      const rs = $$('[data-r]', g), to = state(rs) !== 'true';
      rs.forEach(r => r.toggleAttribute('data-on', to));
      sync();
    }));
    if (master) master.addEventListener('click', () => { const to = state(rows) !== 'true'; rows.forEach(r => r.toggleAttribute('data-on', to)); sync(); });
    const clear = $('[data-clear]', box);
    if (clear) clear.addEventListener('click', () => { rows.forEach(r => r.removeAttribute('data-on')); sync(); });
    sync();
  }

  spec('E', 'E1', 'Practice, first screen: as it is, and calm',
    '<b>pages/practice.md 2</b> and <b>DISCOVER 2.0</b> (C1 one control row, C2 filters behind one trigger, C3 the list is the picker, C5 space between groups, C6 nothing drawn for empty data, C7 one orange). Calm: title with the subject switch, the search alone, one tree-head line (a master box, "3 of 9 selected · Clear", one View trigger), plain groups with one hairline under each head and 28px between them, bars only where there are answers, presets behind the trigger on the Your set card. Two domains shown; fake data.', {
    wide: true,
    html: `<div class="v-cur pd-e-layout"><div class="cur-pr" data-tree>
        <div class="hd"><span class="h1">Practice</span>${segStatic('Subject', ['Math', 'Reading and Writing'])}<span class="meta" style="margin-left:auto">≈ +19 pts available</span></div>
        <div class="srch"><input class="field" placeholder="Search a skill, or type circles hard 10" aria-label="Search skills"></div>
        <div class="chrow"><div class="chips"><button type="button" aria-pressed="true">Mentor's pick</button><button type="button" aria-pressed="false">Full section mix</button><button type="button" aria-pressed="false">Solve first · 10</button><button type="button" aria-pressed="false">Check 3 skills</button></div>
          <button type="button" class="quiet">All presets</button><button type="button" class="quiet">Options</button><a class="quiet" href="#E1">Diagnostic</a></div>
        <div class="thead"><div><span class="h2">Domains</span> <span class="meta" data-count></span></div><div class="ctl">${segStatic('View', ['Skills', 'Map', 'Habits'])}<button type="button" class="quiet">Select all</button><button type="button" class="quiet" data-clear>Clear</button><select class="field" aria-label="Order"><option>Test order</option><option>Weakest first</option></select></div></div>
        <div class="dgrid">${dcard('Algebra', ALG, '+12 pts')}${dcard('Geometry and Trigonometry', GEO, '+7 pts')}</div></div>
        <aside>${setCur}</aside></div>
      <div class="v-pro pd-e-layout"><div class="calm-pr" data-tree>
        <div class="hd"><span class="h1">Practice</span>${segStatic('Subject', ['Math', 'Reading and Writing'])}</div>
        <div class="srch">${ic('search', 20)}<input class="field" placeholder="Search a skill, or type circles hard 10" aria-label="Search skills"><kbd class="kbd">/</kbd></div>
        <div class="thead">${tri('Select all skills', 'mixed').replace('class="pd-tri"', 'class="pd-tri" data-all')}<span class="h2">Skills</span><span class="meta" data-count></span><button type="button" class="quiet" data-clear>Clear</button><button type="button" class="btn sm dd" aria-expanded="false">View: Test order</button></div>
        <div class="tree">${grp('Algebra', ALG, '+12 pts')}${grp('Geometry and Trigonometry', GEO, '+7 pts')}</div></div>
        <aside>${setPro}</aside></div>`,
    build(S) {
      const [cur, calm] = S.qa('[data-tree]');
      wireTree(cur, $('[data-count]', cur), (n, all) => `${n} of ${all} selected`);
      wireTree(calm, $('[data-count]', calm), (n, all) => `${n} of ${all} selected ·`);
      fillChips(S.q('[data-chips]'));
      const dd = S.q('[data-dd]');
      dd.addEventListener('click', () => dd.setAttribute('aria-expanded', String(dd.getAttribute('aria-expanded') !== 'true')));
    },
  });

  const chev = ic('chev', 16), play = ic('play', 16);
  const aRow = (k, v) => `<button type="button" class="pd-arow"><span>${k}</span><span class="v">${v}</span>${chev}</button>`;
  spec('E', 'E2', 'Today, first screen: as it is, and calm',
    '<b>pages/today.md 2, 3</b>: greeting and date on one line; the lifted Up next with the lead task featured (20px title, one meta line, the 42px Start), two compact rows and one quiet footer line in place of three fold rows; the aside loses its four cards: the Today block open (goal ring, streak, plan, since yesterday) then five one-line rows that open in place. Orange on screen: Start, the ring arc, the flame.', {
    wide: true,
    html: `<div class="v-cur pd-e-layout"><div class="pd-col" style="gap:16px;justify-items:stretch">
        <div><div class="h1">Good evening, Malika</div><div class="meta" style="margin-top:4px">Monday, October 19</div></div>
        <div class="card"><div class="card-head"><h3>Up next</h3><span class="meta">about 25 min · fits your 30-min goal</span></div><div class="pd-rows">
          <div><span><b>Linear Equations in One Variable</b><span class="meta">10 questions · 12 min · Plan</span></span><button type="button" class="pill sm">Start</button></div>
          <div><span><b>Words: 15 due</b><span class="meta">6 min · Plan</span></span><button type="button" class="btn sm icon" aria-label="Start Words">${play}</button></div>
          <div><span><b>Fix 4 mistakes</b><span class="meta">Circles, Percentages · 8 min</span></span><button type="button" class="btn sm icon" aria-label="Start fixing">${play}</button></div>
          <div><span>2 more due</span>${chev}</div><div><span>1 done</span>${chev}</div><div><span>Or a practice session</span>${chev}</div></div></div></div>
        <aside class="pd-col" style="gap:12px;justify-items:stretch">
          <div class="card"><div class="card-head"><h3>Today</h3>${chev}</div><div class="pd-row" style="gap:8px"><span class="pd-row" style="gap:4px;color:var(--amber)">${ic('flame', 18)}</span><b>23 day streak</b><span class="meta">best 31</span></div>
            <div data-tm style="margin-top:10px"></div><p class="pd-note">Plan: <a class="link" href="#E2">1 of 3 done</a></p><p class="pd-note">Since yesterday: Percentages reached Proficient. 2 mistakes fixed.</p></div>
          <div class="card"><div class="card-head"><h3>SAT</h3>${chev}</div><div class="pd-row" style="justify-content:space-between"><b>40 days</b><button type="button" class="btn sm">Nov 28</button></div><p class="pd-note">Register by Oct 31</p><button type="button" class="quiet" style="margin-top:6px">Details</button></div>
          <div class="card"><div class="card-head"><h3>Score</h3>${chev}</div><div class="stat-v">560–600</div><div class="pd-row" style="margin-top:8px"><button type="button" class="quiet">Details</button><button type="button" class="quiet">Add a score</button></div></div>
          <div class="card"><div class="card-head"><h3>Pace</h3>${chev}</div><div class="stat-v">31:20</div><div class="pd-row" style="margin-top:8px"><button type="button" class="btn sm">Drill: 5 timed</button><button type="button" class="quiet">Details</button></div></div></aside></div>
      <div class="v-pro pd-e-layout"><div class="pd-col" style="gap:24px;justify-items:stretch">
        <div class="pd-row" style="align-items:baseline;gap:4px 12px"><span class="h1">Good evening, Malika</span><span class="meta">Monday, October 19</span></div>
        <div class="pd-hero"><div class="pd-row" style="justify-content:space-between"><span class="k">Up next</span><span class="meta">25 min left of your 30</span></div>
          <div class="pd-col" style="gap:6px"><span class="pd-lead-t">Linear Equations in One Variable</span><span class="meta pd-meta-i">${ic('clock', 14)}12 min · 10 questions · from your plan</span></div>
          <div><button type="button" class="pill">Start ${play}</button></div>
          <div class="pd-rows"><div><span><b>Words: 15 due</b><span class="meta">6 min</span></span><button type="button" class="quiet">Start</button></div>
            <div><span><b>Fix 4 mistakes</b><span class="meta">Circles, Percentages · 8 min</span></span><button type="button" class="quiet">Start</button></div></div>
          <div class="pd-row" style="justify-content:space-between;gap:8px 16px"><span class="meta"><a class="link" href="#E2">2 more due</a> · <a class="link" href="#E2">1 done</a></span><button type="button" class="quiet">Or a practice session</button></div></div></div>
        <aside class="pd-today"><div class="pd-tday"><span class="ring" style="--rs:44px;--p:.6">18</span><div><div class="pd-row" style="gap:6px"><span style="display:inline-flex;color:var(--amber)">${ic('flame', 18)}</span><b>23 day streak</b></div><div class="meta">18 of 30 min · Plan 1 of 3 done</div></div>
            <p class="pd-note" style="grid-column:1 / -1;margin:4px 0 0">Since yesterday: Percentages reached Proficient. 2 mistakes fixed.</p></div>
          ${aRow('SAT', '40 days')}${aRow('Score', '560–600')}${aRow('Pace', '31:20 of 35:00')}${aRow('Challenge', '#4 of 30')}${aRow('Words', '12 due · 5 new')}</aside></div>`,
    build(S) { UI.meter(S.q('[data-tm]'), { label: 'Today', value: 18, max: 30, unit: 'min', ticks: 10 }); },
  });

  /* ============================================================ F. Icons (ICONS.md) */
  // Phosphor regular and fill (MIT, core commit 2b75f3ad12b4), on the 256 grid; strokes are held at 1.4px by svg.i
  const PS = 'fill="none" stroke="currentColor"';
  const PH = {
    today: [`<rect x="40" y="40" width="176" height="176" rx="8" ${PS}/><line x1="176" y1="24" x2="176" y2="56" ${PS}/><line x1="80" y1="24" x2="80" y2="56" ${PS}/><line x1="40" y1="88" x2="216" y2="88" ${PS}/><circle cx="128" cy="152" r="16" fill="currentColor"/>`,
      '<path d="M208,32H184V24a8,8,0,0,0-16,0v8H88V24a8,8,0,0,0-16,0v8H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM128,168a16,16,0,1,1,16-16A16,16,0,0,1,128,168Zm80-88H48V48H72v8a8,8,0,0,0,16,0V48h80v8a8,8,0,0,0,16,0V48h24Z"/>'],
    practice: [`<rect x="48" y="48" width="64" height="64" rx="8" ${PS}/><rect x="144" y="48" width="64" height="64" rx="8" ${PS}/><rect x="48" y="144" width="64" height="64" rx="8" ${PS}/><rect x="144" y="144" width="64" height="64" rx="8" ${PS}/>`,
      '<path d="M120,56v48a16,16,0,0,1-16,16H56a16,16,0,0,1-16-16V56A16,16,0,0,1,56,40h48A16,16,0,0,1,120,56Zm80-16H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V56A16,16,0,0,0,200,40Zm-96,96H56a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,104,136Zm96,0H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,200,136Z"/>'],
    review: [`<polyline points="128 80 128 128 168 152" ${PS}/><polyline points="72 104 32 104 32 64" ${PS}/><path d="M67.6,192A88,88,0,1,0,65.77,65.77C54,77.69,44.28,88.93,32,104" ${PS}/>`,
      '<path d="M224,128A96,96,0,0,1,62.11,197.82a8,8,0,1,1,11-11.64A80,80,0,1,0,71.43,71.43C67.9,75,64.58,78.51,61.35,82L77.66,98.34A8,8,0,0,1,72,112H32a8,8,0,0,1-8-8V64a8,8,0,0,1,13.66-5.66L50,70.7c3.22-3.49,6.54-7,10.06-10.55A96,96,0,0,1,224,128ZM128,72a8,8,0,0,0-8,8v48a8,8,0,0,0,3.88,6.86l40,24a8,8,0,1,0,8.24-13.72L136,123.47V80A8,8,0,0,0,128,72Z"/>'],
    words: [`<rect x="32" y="80" width="160" height="128" rx="8" ${PS}/><path d="M64,48H216a8,8,0,0,1,8,8V176" ${PS}/>`,
      '<path d="M200,88V200a16,16,0,0,1-16,16H40a16,16,0,0,1-16-16V88A16,16,0,0,1,40,72H184A16,16,0,0,1,200,88Zm16-48H64a8,8,0,0,0,0,16H216V176a8,8,0,0,0,16,0V56A16,16,0,0,0,216,40Z"/>'],
    tests: [`<line x1="96" y1="120" x2="160" y2="120" ${PS}/><line x1="96" y1="152" x2="160" y2="152" ${PS}/><path d="M160,40h40a8,8,0,0,1,8,8V216a8,8,0,0,1-8,8H56a8,8,0,0,1-8-8V48a8,8,0,0,1,8-8H96" ${PS}/><path d="M88,72V64a40,40,0,0,1,80,0v8Z" ${PS}/>`,
      '<path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Zm32,128H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Zm0-32H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Z"/>'],
    plan: [`<circle cx="200" cy="200" r="24" ${PS}/><path d="M72,56h96a32,32,0,0,1,0,64H72a40,40,0,0,0,0,80H176" ${PS}/>`,
      '<path d="M228,200a28,28,0,0,1-54.83,8H72a48,48,0,0,1,0-96h96a24,24,0,0,0,0-48H72a8,8,0,0,1,0-16h96a40,40,0,0,1,0,80H72a32,32,0,0,0,0,64H173.17A28,28,0,0,1,228,200Z"/>'],
    results: [`<polyline points="224 208 32 208 32 48" ${PS}/><polyline points="200 72 128 144 96 112 32 176" ${PS}/><polyline points="160 72 200 72 200 112" ${PS}/>`,
      '<path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM200,192H56a8,8,0,0,1-8-8V72a8,8,0,0,1,16,0v76.69l34.34-34.35a8,8,0,0,1,11.32,0L128,132.69,172.69,88H144a8,8,0,0,1,0-16h48a8,8,0,0,1,8,8v48a8,8,0,0,1-16,0V99.31l-50.34,50.35a8,8,0,0,1-11.32,0L104,131.31l-40,40V176H200a8,8,0,0,1,0,16Z"/>'],
    compete: [`<path d="M32,208V104a8,8,0,0,1,8-8H88" ${PS}/><path d="M88,208V56a8,8,0,0,1,8-8h64a8,8,0,0,1,8,8V208" ${PS}/><path d="M224,208V144a8,8,0,0,0-8-8H168" ${PS}/><polyline points="120 100 132 96 132 136" ${PS}/><line x1="16" y1="208" x2="240" y2="208" ${PS}/>`,
      '<path d="M240,200h-8V144a16,16,0,0,0-16-16H176V56a16,16,0,0,0-16-16H96A16,16,0,0,0,80,56V88H40a16,16,0,0,0-16,16v96H16a8,8,0,0,0,0,16H240a8,8,0,0,0,0-16ZM80,200H40V104H80Zm60-64a8,8,0,0,1-16,0V107.1l-1.47.49a8,8,0,0,1-5.06-15.18l12-4A8,8,0,0,1,140,96Zm76,64H176V144h40Z"/>'],
    profile: [`<circle cx="128" cy="128" r="96" ${PS}/><circle cx="128" cy="120" r="40" ${PS}/><path d="M63.8,199.37a72,72,0,0,1,128.4,0" ${PS}/>`,
      '<path d="M172,120a44,44,0,1,1-44-44A44.05,44.05,0,0,1,172,120Zm60,8A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88.09,88.09,0,0,0-91.47-87.93C77.43,41.89,39.87,81.12,40,128.25a87.65,87.65,0,0,0,22.24,58.16A79.71,79.71,0,0,1,84,165.1a4,4,0,0,1,4.83.32,59.83,59.83,0,0,0,78.28,0,4,4,0,0,1,4.83-.32,79.71,79.71,0,0,1,21.79,21.31A87.62,87.62,0,0,0,216,128Z"/>'],
    check: [`<polyline points="40 144 96 200 224 72" ${PS}/>`],
    x: [`<line x1="200" y1="56" x2="56" y2="200" ${PS}/><line x1="200" y1="200" x2="56" y2="56" ${PS}/>`],
    more: ['<circle cx="128" cy="128" r="12" fill="currentColor"/><circle cx="196" cy="128" r="12" fill="currentColor"/><circle cx="60" cy="128" r="12" fill="currentColor"/>'],
    down: [`<polyline points="208 96 128 176 48 96" ${PS}/>`],
    info: [`<circle cx="128" cy="128" r="96" ${PS}/><path d="M120,120a8,8,0,0,1,8,8v40a8,8,0,0,0,8,8" ${PS}/><circle cx="124" cy="84" r="12" fill="currentColor"/>`],
    left: [`<polyline points="160 208 80 128 160 48" ${PS}/>`],
    right: [`<polyline points="96 48 176 128 96 208" ${PS}/>`],
  };
  const ph = (name, size, fill, cls = '') => `<svg class="i ${cls}" width="${size}" height="${size}" viewBox="0 0 256 256" aria-hidden="true" focusable="false" stroke-linecap="round" stroke-linejoin="round"${fill ? ' fill="currentColor"' : ''}>${PH[name][fill ? 1 : 0]}</svg>`;

  const NAV9 = [['today', 'Today', 'today'], ['practice', 'Practice', 'practice'], ['review', 'Review', 'review'], ['words', 'Words', 'words'], ['tests', 'Tests', 'tests'], ['plan', 'Plan', 'plan'], ['results', 'Results', 'results'], ['compete', 'Compete', 'trophy'], ['profile', 'Me', 'profile']];
  spec('F', 'F1', 'The nine nav icons',
    '<b>ICONS.md 2, 4, 5</b>: Phosphor regular held at a 1.4px stroke at any size (1.3px in dark), new metaphors where the old ones misled (Review is a clock turning back, not undo; Words are cards, not "A="; Results is a rising line; Compete a podium); the current item swaps to the filled twin with a 150ms crossfade; hover only darkens soft to ink. The wash band stays the one orange mark (no side stripe). Click an item.', {
    html: `<div class="pd-two"><div class="pd-snav" role="group" aria-label="Sections">${NAV9.map(([k, t, cur], i) =>
      `<button type="button" class="side-item"${i === 1 ? ' aria-current="page"' : ''}><span class="ico">${UI.svg(UI.ICON[cur] || '', 20, 'cur')}${ph(k, 20, false, 'o')}${ph(k, 20, true, 'f')}</span><span class="side-text">${t}</span><span class="side-meta"></span></button>`).join('')}</div>
      <div class="pd-icons">${NAV9.map(([k, t, cur]) => `<div class="pd-ic"><span class="pd-row" style="gap:10px"><span class="pd-cur-only">${UI.svg(UI.ICON[cur] || '', 24)}</span><span class="pd-pro-only">${ph(k, 24, false)}</span><span class="pd-pro-only">${ph(k, 24, true)}</span></span>${t}</div>`).join('')}</div></div>`,
    build(S) {
      const items = S.qa('.side-item');
      items.forEach(b => b.addEventListener('click', () => { items.forEach(x => x.removeAttribute('aria-current')); b.setAttribute('aria-current', 'page'); }));
    },
  });

  const dual = (uni, name, size = 16) => `<span class="pd-cur-only">${uni}</span><span class="pd-pro-only">${ph(name, size, false)}</span>`;
  const MARKS = [['Check', '✓', 'check'], ['Cross', '✕', 'x'], ['More', '⋯', 'more'], ['Disclosure', '▾', 'down'], ['Info', 'ⓘ', 'info'], ['Back', '‹', 'left'], ['Forward', '›', 'right']];
  spec('F', 'F2', 'Inline marks: Unicode now, drawn icons proposed',
    '<b>ICONS.md 1a, 6</b>: Geist has none of ✓ ✕ ⋯ ▾ ⓘ, so each draws from the device\'s symbol font (weight, width and baseline change per phone). Proposed: the same Phosphor outlines, drawn at the text\'s size (a small marks font, or masks, for CSS content); ‹ › become caret icons on buttons. The table shows both at once; the row above follows the switch.', {
    html: `<div class="pd-row"><span class="badge lg">${dual('✓', 'check', 12)} Fixed</span><button type="button" class="btn sm">Details ${dual('▾', 'down')}</button><button type="button" class="btn sm icon" aria-label="More">${dual('⋯', 'more', 18)}</button>
      <span class="h3" style="display:inline-flex;align-items:center;gap:6px">Score estimate ${dual('ⓘ', 'info')}</span><a class="quiet" href="#F2">${dual('‹', 'left')} Compete</a>
      <span style="display:inline-flex;gap:4px"><button type="button" class="btn sm icon" aria-label="Previous week">${dual('‹', 'left', 18)}</button><button type="button" class="btn sm icon" aria-label="Next week">${dual('›', 'right', 18)}</button></span></div>
      <div class="pd-marks" style="margin-top:18px"><span class="hd">Mark</span><span class="hd">Now (fallback font)</span><span class="hd">Drawn (Phosphor, 16px)</span>
      ${MARKS.map(([k, u, n]) => `<span>${k}</span><span style="font-size:15px">${u} Fixed</span><span>${ph(n, 16, false)} Fixed</span>`).join('')}</div>`,
  });

  spec('F', 'F3', 'Status cells with drawn corner glyphs',
    '<b>ICONS.md 6</b> (fallback without a font file): the cell\'s corner glyph is drawn as a mask in --st-mark instead of a 9px character from the symbol font; the --st-* contract stays. Shown: correct, incorrect, skipped, then mixed and unanswered, which keep their in-font marks (~ and the en dash).', {
    html: '<div class="pd-row" data-a></div><div class="pd-row" data-b></div>',
    build(S) {
      const list = [['correct', 1], ['incorrect', 2], ['skipped', 3], ['mixed', 4], ['unanswered', 5]];
      list.forEach(([st, n]) => S.q('[data-a]').append(UI.cell(st, n, { static: true })));
      list.forEach(([st, n]) => { const c = UI.cell(st, n + 5, { static: true }); c.classList.add('lg'); S.q('[data-b]').append(c); });
    },
  });

  const CORNER = 'M45 8 H30 A22 22 0 0 0 8 30 V45 H34 V41 A7 7 0 0 1 41 34 H45 Z';
  const spot = kind => `<svg class="i" viewBox="-10 -10 120 120" width="72" height="72" aria-hidden="true">${[0, 90, 180, 270].map((a, i) => {
    let tf = a ? `rotate(${a} 50 50)` : '';
    if (kind === 'lost') { const d = [[-6, -6], [6, -6], [6, 6], [-6, 6]][i]; tf = `translate(${d[0]} ${d[1]}) rotate(${a + [-4, 3, -3, 5][i]} 50 50)`; }
    const amber = kind === 'clear' || (kind === 'start' && a === 270);
    const line = `<path class="${amber ? 'am' : 'ln'}" d="${CORNER}" transform="${tf}" stroke="currentColor"/>`;
    return kind === 'done' ? line + `<path class="am dn" d="${CORNER}" transform="${tf}"/>` : line;
  }).join('')}</svg>`;
  spec('F', 'F4', 'Spot drawings from the logo\'s four corners',
    '<b>ICONS.md 9</b>: the only illustration is the mark\'s own geometry, outlined in --faint at the icon weight (--line vanished on the page colour) with one piece in amber; 72px on a desktop, 56 on a phone; above the empty line, never in sheets or filtered empties. Start (first use), clear (all done), lost (404), done (corners fill 40ms apart, 240 each, after the student\'s action; Replay). Current: text only.', {
    replay: true,
    html: `<div class="pd-two">
      <div class="pd-spot">${spot('start')}<p class="empty-text">Questions you miss land here, so you can fix them later.</p><button type="button" class="btn sm">Start practice</button></div>
      <div class="pd-spot">${spot('clear')}<p class="empty-text">Nothing to review. Every mistake is fixed.</p></div>
      <div class="pd-spot">${spot('lost')}<p class="empty-text">This page has moved. Today has what you need.</p><a class="btn sm" href="#F4">Go to Today</a></div>
      <div class="pd-spot" data-done>${spot('done')}<p class="empty-text">Set finished: 8 of 10 right, Circles up to Proficient.</p></div></div>`,
    build(S) {
      S.replay = () => {
        const parts = S.qa('[data-done] .dn');
        parts.forEach((p, i) => { p.getAnimations().forEach(a => a.cancel()); if (!off()) anim(p, [{ opacity: 0 }, { opacity: 1 }], { duration: 240, delay: 120 + i * 40, fill: 'backwards' }); });
      };
    },
  });
})();
