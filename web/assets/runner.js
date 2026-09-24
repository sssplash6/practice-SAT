/* ============================================================================
   SAT Freshman -- the runner: one shell for the practice session and the test window
   (spec/rebuild-v2.md R21, the runner.js row of 2.4, 2.8's runner keys; QBank 2.1-2.4,
   2.7-2.10, 2.14-2.15; Tests 1, 4.3-4.12; v2-upgrades R43 R50 G9, P7 P16 P20 P23 P24 P25,
   X1 X3 X4 X5 X6 X8 X9, tests.md item 74)

   Loaded after ui.js, kit.js and question.js on the two runner pages. Adds to window.UI.
   Pure client components driven by props and callbacks: no page logic, no fetches.
   Styles are runner.css (question.js links it).

   UI.runner(host, opts) -> run                                   the shell (see runner() below)
   UI.timer(el, {secondsLeft, elapsed, hideKey, hidden, paused, onEnd, onHide, onWarn, unhide})
       -> {el, left, elapsed, paused, hidden, set({secondsLeft, elapsed}), pause(), resume(),
           hide(on), delta(text), add(sec, why), destroy()}
   UI.saveQueue(sid, send(item, stamps) -> Promise, {el(), onStatus, onConflict, onDrop})
       -> {pid, answer(qid, value, made_left), state(qid, patch), flush(), retry(), wait(),
           size, answers, status, stamps(), onStatus(fn), destroy()}
       answers mirror to localStorage satf.pending.{sid} as {qid: {value, made_left}}; state
       patches to satf.pendstate.{sid}; sent in order, dropped only on a 2xx (a 409 goes to
       onConflict), retried at 1, 2, 5, 10 s and on 'online'. stamps: {pid, el, hid, off} (X1)
   UI.navigator(host, cells, {mode, views, view, title, current, confidence, pace_ms,
       onPick(i), onFinish, finishLabel, onReview, onGo(list), onTwins(cells), onFix(label, cells)})
       -> {el, update(cells, current), view, focus()}
   UI.checkYourWork(host, cells, {mode, title, meta, lead, left, timed, pace_ms, confidence,
       training, order, saving, onPick(i), onGo(list), onFinish, finishLabel, onBack, backLabel})
       -> {el, foot, update(cells, patch), queue()}
   cells: [{n, status, flag, note, saved, tier, level, topic, topic_name, ms, budget_ms, conf,
            trap, voided, current}]   status is a UI.STATES key (answered, unanswered, correct, ...)
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI = window.UI || {};
  const doc = document;

  /* ------------------------------------------------------------ helpers */
  function h(tag, attrs = {}, ...kids) {
    const e = doc.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k === 'style') e.style.cssText = v;
      else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat(3)) if (k !== null && k !== undefined && k !== false) e.append(k instanceof Node ? k : String(k));
    return e;
  }
  const media = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
  const phone = () => media('(max-width: 759px)');
  const coarse = () => media('(pointer: coarse)');
  const still = () => media('(prefers-reduced-motion: reduce)') || doc.documentElement.dataset.motion === 'reduce';
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (_) { return false; } },
    del(k) { try { localStorage.removeItem(k); } catch (_) {} },
  };
  const mmss = s => { s = Math.max(0, Math.round(s || 0)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; };
  const msx = ms => mmss((ms || 0) / 1000);
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  const plural = (n, one, many) => `${n} ${n === 1 ? one : (many || one + 's')}`;
  const fmtN = n => (UI.num ? UI.num(n) : String(n));
  const LETTERS = 'ABCDE';
  let seq = 0;
  const uid = p => `r${p}${++seq}`;
  const typing = el => !!el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));

  /* icons: question.js's set where it has one, these for the rest (24px strokes in currentColor) */
  const L = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"';
  const RI = {
    x:       `<path d="M6 6l12 12M18 6L6 18" ${L} stroke-width="1.8"/>`,
    pause:   `<path d="M9 5.5v13M15 5.5v13" ${L} stroke-width="2"/>`,
    more:    `<circle cx="5.5" cy="12" r="1.5" fill="currentColor"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/><circle cx="18.5" cy="12" r="1.5" fill="currentColor"/>`,
    marker:  `<path d="M14.5 4.5l5 5-8.5 8.5H6v-5z" ${L}/><path d="M4 20.5h9" ${L}/>`,
    pen:     `<path d="M4.5 19.5l1-4.2L15.8 5a2 2 0 0 1 2.8 0l.4.4a2 2 0 0 1 0 2.8L8.7 18.5z" ${L}/><path d="M13.8 7l3.2 3.2" ${L}/>`,
    info:    `<circle cx="12" cy="12" r="8.5" ${L}/><path d="M12 11v5.2" ${L} stroke-width="1.9"/><circle cx="12" cy="7.9" r="1" fill="currentColor"/>`,
    up:      `<path d="M7 14l5-5 5 5" ${L} stroke-width="1.8"/>`,
    down:    `<path d="M7 10l5 5 5-5" ${L} stroke-width="1.8"/>`,
    left:    `<path d="M19 12H6M11 6.5L5.5 12l5.5 5.5" ${L}/>`,
    right:   `<path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5" ${L}/>`,
    eye:     `<path d="M2.5 12s3.6-6.5 9.5-6.5S21.5 12 21.5 12s-3.6 6.5-9.5 6.5S2.5 12 2.5 12z" ${L}/><circle cx="12" cy="12" r="2.6" ${L}/>`,
    eyeoff:  `<path d="M2.5 12s3.6-6.5 9.5-6.5S21.5 12 21.5 12s-3.6 6.5-9.5 6.5S2.5 12 2.5 12z" ${L}/><path d="M4 20L20 4" ${L}/>`,
    list:    `<path d="M9 7h11M9 12h11M9 17h11" ${L}/><circle cx="5" cy="7" r="1" fill="currentColor"/><circle cx="5" cy="12" r="1" fill="currentColor"/><circle cx="5" cy="17" r="1" fill="currentColor"/>`,
    search:  `<circle cx="10.5" cy="10.5" r="6" ${L}/><path d="M15 15l5 5" ${L}/>`,
    erase:   `<path d="M8.5 19.5h11M4.6 14.9l8.8-8.8a2 2 0 0 1 2.8 0l2.7 2.7a2 2 0 0 1 0 2.8L12.3 18.2a2 2 0 0 1-1.4.6H8.2a2 2 0 0 1-1.4-.6l-2.2-2.2a1 1 0 0 1 0-1.1z" ${L}/>`,
    hl:      `<path d="M5 18.5h14" ${L} stroke-width="3" opacity=".35"/><path d="M8 15.5l1.5-9h5l1.5 9" ${L}/>`,
    play:    `<path d="M8 5.5v13l10-6.5z" ${L}/>`,
    queue:   `<path d="M4 7h10M4 12h10M4 17h6" ${L}/><path d="M17 14l3 3-3 3" ${L}/>`,
  };
  const svgHTML = (inner, size) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${inner}</svg>`;
  function icon(name, size = 18) {
    if (!RI[name] && UI.qicon) return UI.qicon(name, size);
    const t = doc.createElement('template');
    t.innerHTML = svgHTML(RI[name] || '', size);
    return t.content.firstElementChild;
  }

  /* one key registry (F2's UI.keys, R22, R43); a small stand-in until ui.js has it */
  const NAMED = { esc: 'Escape', escape: 'Escape', enter: 'Enter', left: 'ArrowLeft', right: 'ArrowRight', up: 'ArrowUp', down: 'ArrowDown' };
  function combo(s) {
    const parts = String(s).split('+');
    let key = parts.pop() || '+';
    key = NAMED[key.toLowerCase()] || (key.length === 1 ? key.toUpperCase() : key);
    return (parts.includes('Shift') ? 'Shift+' : '') + key;
  }
  function eventCombo(e) {
    let k = e.key;
    if (!k || ['Shift', 'Control', 'Alt', 'Meta'].includes(k)) return null;
    if (e.metaKey || e.ctrlKey || e.altKey) return null;
    if (k === ' ') k = 'Space';
    const plain = k.length === 1 && /[a-z0-9]/i.test(k);
    if (k.length === 1) k = k.toUpperCase();
    return (e.shiftKey && (plain || k.length > 1) ? 'Shift+' : '') + k;
  }
  function keyScope(scope, map, o = {}) {
    if (UI.keys && UI.keys.register) return UI.keys.register(scope, map, o);
    const m = new Map(Object.entries(map).map(([k, v]) => [combo(k), typeof v === 'function' ? { run: v } : v]));
    const fn = e => {
      if (e.defaultPrevented || e.isComposing) return;
      const c = eventCombo(e);
      if (!c) return;
      if (typing(e.target) && c !== 'Enter' && c !== 'Escape') return;
      if (e.target.closest && e.target.closest('[role=menu], [role=listbox]')) return;
      const modal = [...doc.querySelectorAll('dialog[open]')].some(d => { try { return d.matches(':modal'); } catch (_) { return true; } });
      if (modal && c !== 'Escape') return;
      const b = m.get(c);
      if (b && (!b.when || b.when()) && b.run(e) !== false) e.preventDefault();
    };
    doc.addEventListener('keydown', fn);
    return { unregister() { doc.removeEventListener('keydown', fn); } };
  }

  /* ------------------------------------------------------------ UI.timer (QBank 2.2, Tests 4.3, X3, P16) */
  function timer(el, o = {}) {
    const timed = Number.isFinite(o.secondsLeft);
    let base = timed ? +o.secondsLeft : (+o.elapsed || 0);
    let t0 = performance.now(), paused = !!o.paused, pausedAt = t0, added = 0, addedAll = 0;
    let hidden = o.hideKey ? !!ls.get(o.hideKey, !!o.hidden) : !!o.hidden;
    let ended = false, last = null, iv = 0, flashT = 0, deltaText = '';
    const warns = (o.warn || [300, 60]).slice().sort((a, b) => b - a);
    const box = el || h('div');
    box.classList.add('timer');
    box.classList.toggle('untimed', !timed);
    const digits = h('span', { class: 't-digits', role: 'timer', 'aria-live': 'off' });
    const cap = h('span', { class: 't-cap', text: timed ? 'left' : 'elapsed' });
    const hideB = h('button', { type: 'button', class: 't-hide', id: o.hideId || null, title: 'Hide or show the timer (H)' });
    const deltaEl = h('p', { class: 't-delta', hidden: true, 'aria-live': 'off' });
    const extra = h('p', { class: 't-extra', hidden: true });
    box.replaceChildren(h('div', { class: 't-row' }, h('span', { class: 't-read' }, o.label ? h('span', { class: 't-k k', text: o.label }) : null, digits, cap), hideB), deltaEl, extra);
    hideB.addEventListener('click', () => hide(!hidden));
    const secs = () => {
      const ran = ((paused ? pausedAt : performance.now()) - t0) / 1000;
      return timed ? Math.max(0, base + added - ran) : base + ran;
    };
    // thresholds already behind us when the clock loads are not announced again
    const passed = new Set(timed ? warns.filter(w => base >= 0 && base <= w) : []);
    function paint() {
      const raw = secs();
      const s = timed ? Math.ceil(raw - 1e-6) : Math.floor(raw);
      if (timed) {
        for (const w of warns) {
          if (s <= w && !passed.has(w)) {
            passed.add(w);
            if (w === 300 && hidden && o.unhide !== false) hide(false);
            const text = w >= 60 && w % 60 === 0 ? `${plural(w / 60, 'minute')} left` : `${w} seconds left`;
            toast(text, { ms: 6000 });
            if (o.onWarn) o.onWarn(w, text);
            if (w === 60 && !still()) { box.classList.remove('t-pulse'); void box.offsetWidth; box.classList.add('t-pulse'); }
          }
        }
        box.classList.toggle('t-low', s <= 300);
        box.classList.toggle('t-last', s <= 60);
        if (s <= 0 && !ended && !paused) { ended = true; if (o.onEnd) setTimeout(() => o.onEnd(), 0); }
      }
      const txt = hidden ? '— : —' : mmss(s);
      if (txt !== last) { digits.textContent = txt; last = txt; }
      digits.setAttribute('aria-label', hidden ? 'Timer hidden' : `${mmss(s)} ${timed ? 'left' : 'elapsed'}`);
      box.classList.toggle('t-hidden', hidden);
      box.classList.toggle('t-paused', paused);
      hideB.setAttribute('aria-pressed', String(hidden));
      hideB.replaceChildren(icon(hidden ? 'eyeoff' : 'eye', 16), h('span', { class: 't-hide-l', text: hidden ? (o.showLabel || 'Show') : 'Hide' }));
      hideB.setAttribute('aria-label', hidden ? 'Show the timer' : 'Hide the timer');
      deltaEl.hidden = hidden || !deltaText;
    }
    function hide(on) {
      hidden = !!on;
      if (o.hideKey) ls.set(o.hideKey, hidden);
      last = null;
      paint();
      if (o.onHide) o.onHide(hidden);
    }
    function start() { clearInterval(iv); iv = setInterval(paint, 250); paint(); }
    start();
    return {
      el: box,
      get left() { return timed ? secs() : null; },
      get elapsed() { return timed ? null : secs(); },
      get paused() { return paused; },
      get hidden() { return hidden; },
      get timed() { return timed; },
      set(p = {}) {
        if (timed && Number.isFinite(p.secondsLeft)) { base = +p.secondsLeft; added = 0; }
        if (!timed && Number.isFinite(p.elapsed)) base = +p.elapsed;
        t0 = performance.now(); pausedAt = t0;
        if (timed && secs() > 0) ended = false;
        paint();
      },
      pause() { if (paused) return; paused = true; pausedAt = performance.now(); paint(); },
      resume() { if (!paused) return; t0 += performance.now() - pausedAt; paused = false; paint(); },
      hide,
      delta(text) { deltaText = text || ''; deltaEl.textContent = deltaText; paint(); },
      // P16: every added slot adds its own budget: "+1:05 for the repair" for 3 s, then the caption keeps the total
      add(sec, why) {
        if (!timed || !sec) return;
        added += sec; addedAll += sec;
        clearTimeout(flashT);
        extra.textContent = `+${mmss(sec)}${why ? ' for ' + why : ''}`;
        extra.hidden = false;
        flashT = setTimeout(() => { extra.textContent = `incl. +${mmss(addedAll)} added`; }, 3000);
        paint();
      },
      destroy() { clearInterval(iv); clearTimeout(flashT); },
    };
  }

  /* ------------------------------------------------------------ UI.saveQueue (Tests 4.9, X1) */
  const SUM = new Set(['ms', 'ref_ms', 'ref_n', 'away_ms', 'away_n', 'open_ms']);
  function saveQueue(sid, send, o = {}) {
    const KEY = `satf.pending.${sid}`, SKEY = `satf.pendstate.${sid}`;
    const pid = Math.random().toString(36).slice(2, 10);
    let items = [];
    Object.entries(ls.get(KEY, {}) || {}).forEach(([qid, v]) => items.push({ kind: 'answer', qid, body: { value: v.value, made_left: v.made_left } }));
    (ls.get(SKEY, []) || []).forEach(x => { if (x && x.qid) items.push({ kind: 'state', qid: x.qid, body: x.body || {} }); });
    let busy = false, fails = 0, retryT = 0, slowT = 0, state = items.length ? 'waiting' : 'saved', dead = false;
    let hidMs = 0, hidAt = doc.hidden ? performance.now() : null, offMs = 0, offAt = navigator.onLine === false ? performance.now() : null;
    const subs = new Set(o.onStatus ? [o.onStatus] : []);
    const waiters = [];
    const onVis = () => {
      if (doc.hidden) hidAt = performance.now();
      else if (hidAt !== null) { hidMs += performance.now() - hidAt; hidAt = null; }
    };
    const onOff = () => { if (offAt === null) offAt = performance.now(); status(); };
    const onOn = () => { if (offAt !== null) { offMs += performance.now() - offAt; offAt = null; } fails = 0; flush(); };
    doc.addEventListener('visibilitychange', onVis);
    addEventListener('offline', onOff);
    addEventListener('online', onOn);

    function mirror() {
      const a = {};
      items.filter(x => x.kind === 'answer').forEach(x => { a[x.qid] = { value: x.body.value, made_left: x.body.made_left }; });
      if (Object.keys(a).length) ls.set(KEY, a); else ls.del(KEY);
      const s = items.filter(x => x.kind === 'state').map(x => ({ qid: x.qid, body: x.body }));
      if (s.length) ls.set(SKEY, s.slice(-200)); else ls.del(SKEY);
    }
    function stamps() {
      const t = performance.now();
      return { pid, el: o.el ? Math.round(o.el()) : null, hid: Math.round(hidMs + (hidAt !== null ? t - hidAt : 0)), off: Math.round(offMs + (offAt !== null ? t - offAt : 0)) };
    }
    const answers = () => items.filter(x => x.kind === 'answer').length;
    function status(s) {
      if (s) state = s;
      if (!items.length && !busy) state = 'saved';
      const n = answers();
      const waitingText = n ? `${plural(n, 'answer')} waiting` : 'changes waiting';
      const offline = navigator.onLine === false || state === 'offline';
      const text = state === 'saved' ? 'Saved' : state === 'saving' ? 'Saving…'
        : offline ? `Offline · ${waitingText}` : state === 'error' ? 'Couldn’t save' : items.length ? 'Saving…' : 'Saved';
      const info = { state: offline && state !== 'saved' ? 'offline' : state, n, size: items.length, text, retry: api.retry };
      subs.forEach(f => { try { f(info); } catch (_) {} });
      return info;
    }
    function push(kind, qid, body) {
      if (dead) return;
      if (kind === 'answer') {
        items = items.filter(x => !(x.kind === 'answer' && x.qid === qid && !x.flight));
        items.push({ kind, qid, body: Object.assign({}, body) });
      } else {
        const open = [...items].reverse().find(x => x.kind === 'state' && x.qid === qid && !x.flight);
        if (open) {
          for (const [k, v] of Object.entries(body || {})) open.body[k] = SUM.has(k) && typeof v === 'number' && typeof open.body[k] === 'number' ? open.body[k] + v : v;
        } else items.push({ kind, qid, body: Object.assign({}, body) });
      }
      mirror();
      flush();
    }
    async function flush() {
      if (busy || dead) return;
      if (!items.length) { status('saved'); waiters.splice(0).forEach(f => f()); return; }
      busy = true;
      clearTimeout(retryT);
      clearTimeout(slowT);
      slowT = setTimeout(() => { if (busy) status('saving'); }, 400);
      while (items.length && !dead) {
        const it = items[0];
        it.flight = true;
        try {
          await send(it, stamps());
          items.shift();
          fails = 0;
          mirror();
        } catch (e) {
          it.flight = false;
          const st = e && e.status;
          if (st === 409) { items.shift(); mirror(); if (o.onConflict) o.onConflict(e, it); continue; }
          if (st >= 400 && st < 500 && st !== 408 && st !== 429) { items.shift(); mirror(); if (o.onDrop) o.onDrop(e, it); continue; }
          fails++;
          busy = false;
          clearTimeout(slowT);
          status(!st || e.offline ? 'offline' : 'error');
          retryT = setTimeout(flush, [1, 2, 5, 10][Math.min(fails - 1, 3)] * 1000);
          return;
        }
      }
      busy = false;
      clearTimeout(slowT);
      status('saved');
      waiters.splice(0).forEach(f => f());
    }
    const api = {
      pid,
      answer(qid, value, made_left) { push('answer', qid, { value, made_left: made_left ?? null }); },
      state(qid, patch) { if (patch && Object.keys(patch).length) push('state', qid, patch); },
      push,
      flush,
      retry() { fails = 0; flush(); },
      wait() { return items.length ? new Promise(r => { waiters.push(r); flush(); }) : Promise.resolve(); },
      stamps,
      get size() { return items.length; },
      get answers() { return answers(); },
      get status() { return status(); },
      pendingFor(qid) { const a = items.find(x => x.kind === 'answer' && x.qid === qid); return a ? a.body.value : undefined; },
      onStatus(f) { subs.add(f); f(status()); return () => subs.delete(f); },
      destroy() {
        dead = true;
        clearTimeout(retryT); clearTimeout(slowT);
        doc.removeEventListener('visibilitychange', onVis);
        removeEventListener('offline', onOff);
        removeEventListener('online', onOn);
      },
    };
    if (items.length) setTimeout(flush, 0);
    return api;
  }

  /* ------------------------------------------------------------ cells: counts and words */
  const answeredish = s => !['unanswered', 'skipped', 'future', 'not_reached', 'blank'].includes(s);
  const overBudget = (c, pace) => !!c.ms && c.ms > (c.budget_ms || pace || 95000);
  function tally(cells) {
    const t = { total: cells.length, answered: 0, unanswered: 0, skipped: 0, flag: 0, note: 0, guess: 0, right: 0, wrong: 0, served: 0, by: {} };
    cells.forEach(c => {
      if (c.status === 'future') return;
      t.served++;
      if (c.status === 'skipped') t.skipped++;
      else if (answeredish(c.status)) t.answered++;
      else t.unanswered++;
      if (c.flag) t.flag++;
      if (c.note) t.note++;
      if (c.conf === 'guess') t.guess++;
      if (c.status === 'correct' || c.status === 'repaired') t.right++;
      if (c.status === 'incorrect') t.wrong++;
      t.by[c.status] = (t.by[c.status] || 0) + 1;
    });
    return t;
  }
  const CONF = { sure: 'S', unsure: 'U', guess: 'G' };
  function cellLabel(c, i, exam) {
    const st = (UI.STATES && UI.STATES[c.status]) || {};
    const bits = [`Question ${c.n ?? i + 1}`];
    if (exam) bits.push(c.status === 'answered' ? 'answered' : 'unanswered');
    else if (c.status === 'future') bits.push('not served yet');
    else bits.push((st.label || c.status || '').toLowerCase());
    if (c.flag) bits.push(exam ? 'marked for review' : 'marked');
    if (c.note) bits.push('has note');
    if (c.conf && CONF[c.conf]) bits.push(c.conf);
    if (c.tier) bits.push(`${c.tier}${c.level ? ' level ' + c.level : ''}`);
    return bits.join(', ');
  }
  function glyphOf(topic) {
    if (!topic || !UI.glyph) return null;
    const g = UI.glyph(topic);
    if (g instanceof Node) return g;
    if (typeof g === 'string') { const s = h('span', { html: g }); return s.firstElementChild || s; }
    return null;
  }
  const topicName = c => {
    const t = UI.TOPIC && UI.TOPIC[c.topic];
    return (t && (t.short || t.name)) || c.topic_name || c.topic || 'Other';
  };
  // arrows move across a cell grid, Home and End jump; the columns are read from the layout
  function gridKeys(grid) {
    grid.addEventListener('keydown', e => {
      const cells = [...grid.querySelectorAll('.cell:not([data-filtered]):not(:disabled)')];
      const i = cells.indexOf(doc.activeElement);
      if (i < 0) return;
      const cols = Math.max(1, getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length);
      const j = { ArrowRight: i + 1, ArrowLeft: i - 1, ArrowDown: i + cols, ArrowUp: i - cols, Home: 0, End: cells.length - 1 }[e.key];
      if (j === undefined) return;
      e.preventDefault();
      e.stopPropagation();
      const nx = cells[Math.max(0, Math.min(cells.length - 1, j))];
      cells.forEach(c => { c.tabIndex = c === nx ? 0 : -1; });
      nx.focus();
    });
  }
  function roving(grid, current) {
    const cells = [...grid.querySelectorAll('.cell:not([data-filtered]):not(:disabled)')];
    const at = cells.find(c => c.dataset.i === String(current)) || cells[0];
    grid.querySelectorAll('.cell').forEach(c => { c.tabIndex = c === at ? 0 : -1; });
  }

  /* ------------------------------------------------------------ UI.navigator (QBank 2.8, Tests 4.4, P20, X5) */
  const VIEWS = { status: 'Status', difficulty: 'Difficulty', skill: 'Skill', time: 'Time', confidence: 'Confidence', traps: 'Traps' };
  function navPanel(host, cells, o = {}) {
    const exam = o.mode === 'exam';
    const end = !!o.end;
    let list = cells.slice();
    let current = o.current ?? list.findIndex(c => c.current);
    let view = o.view || 'status';
    const pressed = new Set();
    let examFilter = 'all';
    const views = (o.views || (exam ? ['status'] : ['status', 'difficulty', 'skill', 'time', 'confidence', 'traps'])).filter(v => VIEWS[v]);
    const tid = uid('nav');
    const el = h('div', { class: 'navp' + (exam ? ' exam' : ''), role: 'group', 'aria-labelledby': tid });
    const head = h('div', { class: 'navp-head' }, h('h2', { class: 'navp-title', id: tid, text: o.title || (exam ? 'Questions' : 'Question overview') }));
    if (o.onClose) head.append(h('button', { type: 'button', class: 'x', 'aria-label': 'Close', onclick: () => o.onClose() }, icon('x', 18)));
    el.append(head);
    let seg = null;
    if (views.length > 1 && UI.seg) {
      seg = UI.seg(null, views.map(v => ({ value: v, label: VIEWS[v] })), { value: view, label: 'View', onChange: v => { view = v; pressed.clear(); draw(); } });
      el.append(h('div', { class: 'navp-views' }, seg.el));
    }
    const filterRow = h('div', { class: 'navp-filters' });
    const legendRow = h('div', { class: 'navp-legend' });
    const grid = h('div', { class: 'cell-grid navp-grid', role: 'grid', 'aria-label': 'Questions' });
    const foot = h('div', { class: 'navp-foot' });
    el.append(legendRow, filterRow, grid, foot);
    grid.addEventListener('click', e => {
      const b = e.target.closest('.cell');
      if (!b || b.disabled || b.hasAttribute('data-filtered')) return;
      if (o.onPick) o.onPick(+b.dataset.i);
    });
    gridKeys(grid);

    const trapOf = c => (c.trap && (c.trap.label || c.trap)) || null;
    const preds = {
      flag: c => !!c.flag, note: c => !!c.note, over: c => overBudget(c, o.pace_ms),
      answered: c => answeredish(c.status) && c.status !== 'future',
    };
    function match(c) {
      if (c.status === 'future') return !pressed.size && examFilter === 'all';
      if (exam) {
        if (examFilter === 'unanswered' && c.status === 'answered') return false;
        if (examFilter === 'review' && !c.flag) return false;
        if (examFilter === 'guess' && c.conf !== 'guess') return false;
      }
      for (const k of pressed) {
        const [kind, val] = k.includes(':') ? k.split(/:(.+)/) : [null, k];
        if (kind === 'topic') { if (c.topic !== val) return false; }
        else if (kind === 'conf') { if ((c.conf || 'none') !== val) return false; }
        else if (kind === 'trap') { if (trapOf(c) !== val) return false; }
        else if (kind === 'tier') { if (c.tier !== val) return false; }
        else if (preds[val]) { if (!preds[val](c)) return false; }
        else if (c.status !== val) return false;
      }
      return true;
    }
    const toggle = k => { pressed.has(k) ? pressed.delete(k) : pressed.add(k); draw(); };
    function chip(key, label, n, extra) {
      const b = h('button', { type: 'button', class: 'navp-chip', 'aria-pressed': String(pressed.has(key)), disabled: n === 0 ? true : null },
        extra || null, h('span', { text: label }), n !== undefined && n !== null ? h('b', { text: fmtN(n) }) : null);
      b.addEventListener('click', () => toggle(key));
      return h('li', {}, b);
    }
    function legend() {
      legendRow.replaceChildren();
      filterRow.replaceChildren();
      const t = tally(list);
      if (exam) {
        if (UI.legend) UI.legend(legendRow, ['current', 'answered', { key: 'unanswered', label: 'Unanswered' }, { key: 'flag', label: 'For review' }],
          { answered: t.answered, unanswered: t.unanswered, flag: t.flag }, { label: 'Legend' });
        const opts = [{ value: 'all', label: 'All' }, { value: 'unanswered', label: 'Unanswered', n: t.unanswered }, { value: 'review', label: 'For review', n: t.flag }];
        if (o.confidence) opts.push({ value: 'guess', label: 'Guesses', n: t.guess });
        const ch = h('div', { class: 'choices', role: 'group', 'aria-label': 'Show' });
        opts.forEach(x => {
          const b = h('button', { type: 'button', 'aria-pressed': String(examFilter === x.value) }, x.label, x.n !== undefined ? h('span', { class: 'n', text: ` ${x.n}` }) : null);
          b.addEventListener('click', () => { examFilter = x.value; draw(); });
          ch.append(b);
        });
        filterRow.append(ch);
        if (view === 'time') legendRow.append(h('p', { class: 'meta', text: timeLine(list) }));
        return;
      }
      const row = h('ul', { class: 'legend navp-chips', 'aria-label': 'Filter' });
      const note = (cls, ...kids) => h('li', { class: cls }, ...kids);
      const sw = key => (UI.cell ? h('i', Object.assign({ class: 'sw', 'aria-hidden': 'true' }, swatchAttrs(key))) : null);
      if (view === 'status') {
        const keys = end ? ['answered', 'unanswered', 'skipped'] : ['unanswered', 'correct', 'incorrect', 'mixed', 'repaired', 'skipped', 'voided'];
        keys.forEach(k => { const n = k === 'answered' ? t.answered : t.by[k] || 0; if (n || ['unanswered', 'correct', 'incorrect', 'answered'].includes(k)) row.append(chip(k, stateLabel(k), n, sw(k))); });
        row.append(chip('flag', 'Marked', t.flag, sw('flag')), chip('note', 'Has note', t.note, sw('note')));
        row.append(note('navp-cur', sw('current'), 'Current'));
      } else if (view === 'difficulty') {
        let measured = 0;
        ['easy', 'medium', 'hard'].forEach(k => {
          const n = list.filter(c => c.tier === k && c.status !== 'future').length;
          row.append(chip('tier:' + k, stateLabel(k), n, sw(k)));
        });
        list.forEach(c => { if (c.level && c.status !== 'future') measured++; });
        row.append(note('meta', `measured ${measured}`));
      } else if (view === 'skill') {
        const by = new Map();
        list.forEach(c => { if (c.status !== 'future' && c.topic) by.set(c.topic, (by.get(c.topic) || 0) + 1); });
        by.forEach((n, tp) => row.append(chip('topic:' + tp, topicName({ topic: tp, topic_name: (list.find(c => c.topic === tp) || {}).topic_name }), n, glyphOf(tp))));
      } else if (view === 'time') {
        const n = list.filter(c => overBudget(c, o.pace_ms)).length;
        row.append(chip('over', 'Over budget', n, sw('over')), note('meta', timeLine(list)));
      } else if (view === 'confidence') {
        [['sure', 'Sure'], ['unsure', 'Unsure'], ['guess', 'Guess'], ['none', 'Unrated']].forEach(([k, lab]) =>
          row.append(chip('conf:' + k, lab, list.filter(c => c.status !== 'future' && answeredish(c.status) && (c.conf || 'none') === k).length, h('span', { class: 'navp-corner', text: CONF[k] || '·' }))));
        const sureMiss = list.filter(c => c.conf === 'sure' && c.status === 'incorrect').length;
        row.append(note('meta', plural(sureMiss, 'confident miss', 'confident misses')));
      } else if (view === 'traps') {
        const by = new Map();
        list.forEach(c => { const tr = trapOf(c); if (tr) by.set(tr, (by.get(tr) || 0) + 1); });
        if (!by.size) row.append(note('meta', 'No named mistakes in this set yet'));
        by.forEach((n, lab) => row.append(chip('trap:' + lab, lab, n, sw('open'))));
      }
      if (pressed.size) row.append(note('', h('button', { type: 'button', class: 'navp-clear', text: 'Clear', onclick: () => { pressed.clear(); draw(); } })));
      legendRow.append(row);
    }
    function draw() {
      legend();
      grid.dataset.colour = view === 'difficulty' ? 'difficulty' : '';
      if (view !== 'difficulty') grid.removeAttribute('data-colour');
      grid.classList.toggle('timed', view === 'time');
      grid.replaceChildren(...list.map((c, i) => cellEl(c, i)));
      roving(grid, current);
      footer();
    }
    function cellEl(c, i) {
      const ok = match(c);
      const opts = {
        flag: c.flag || null, note: c.note || null, saved: c.saved || null, current: i === current,
        tier: view === 'difficulty' ? c.tier : null, level: view === 'difficulty' ? c.level : null,
        over: view === 'time' && overBudget(c, exam ? o.pace_ms * 2 : o.pace_ms) ? true : null,
        open: view === 'traps' && trapOf(c) ? true : null,
        filtered: ok ? null : true, label: cellLabel(c, i, exam),
      };
      const b = UI.cell ? UI.cell(c.status || 'unanswered', c.n ?? i + 1, opts)
        : h('button', { type: 'button', class: 'cell', 'data-status': c.status, 'aria-label': opts.label }, h('span', { class: 'n', text: c.n ?? i + 1 }));
      b.dataset.i = i;
      if (c.status === 'future') { b.disabled = true; b.title = `Comes after question ${i}`; }
      if (view === 'time' && c.ms) b.append(h('span', { class: 'c-sub', text: msx(c.ms), 'aria-hidden': 'true' }));
      if (view === 'skill' && c.topic) { const g = glyphOf(c.topic); if (g) { g.classList.add('c-glyph'); b.append(g); } }
      if (view === 'confidence' && c.conf && CONF[c.conf]) {
        b.append(h('span', { class: 'c-corner', text: CONF[c.conf], 'aria-hidden': 'true' }));
        if (c.conf === 'sure' && c.status === 'incorrect') b.dataset.over = '';
      }
      return b;
    }
    function footer() {
      foot.replaceChildren();
      const t = tally(list);
      if (exam) {
        const q = queueOf(list, ['unanswered', 'flag']);
        if (o.onGo && q.length) foot.append(h('button', { type: 'button', class: 'pill sm', onclick: () => o.onGo(q) }, `Go through ${q.length}`));
        if (o.onReview) foot.append(h('button', { type: 'button', class: 'quiet', onclick: () => o.onReview() }, 'Go to review page →'));
        return;
      }
      foot.append(h('p', { class: 'meta navp-sum', text: [`${t.answered} answered`, t.skipped ? `${t.skipped} skipped` : null, `${t.flag} marked`].filter(Boolean).join(' · ') }));
      const acts = h('div', { class: 'navp-acts' });
      const shown = list.map((c, i) => ({ c, i })).filter(x => match(x.c) && x.c.status !== 'future');
      if (pressed.size && o.onTwins && shown.length && !(end && !o.finished)) acts.append(h('button', { type: 'button', class: 'btn sm', onclick: () => o.onTwins(shown.map(x => x.i)) }, `Twins of these (${shown.length})`));
      const trapKey = [...pressed].find(k => k.startsWith('trap:'));
      if (trapKey && o.onFix) acts.append(h('button', { type: 'button', class: 'btn sm', onclick: () => o.onFix(trapKey.slice(5), shown.map(x => x.i)) }, 'Fix these'));
      if (o.onFinish) acts.append(h('button', { type: 'button', class: 'pill sm', onclick: () => o.onFinish() }, o.finishLabel || (end ? 'Review & finish' : 'Finish set')));
      foot.append(acts);
    }
    draw();
    if (host) host.append(el);
    return {
      el,
      update(c, cur) { list = c.slice(); if (cur !== undefined) current = cur; draw(); },
      get view() { return view; },
      set view(v) { if (VIEWS[v]) { view = v; if (seg) seg.set(v, true); draw(); } },
      focus() { const b = grid.querySelector('.cell[tabindex="0"]'); if (b) b.focus({ preventScroll: true }); },
    };
  }
  function stateLabel(k) { return ((UI.STATES && UI.STATES[k]) || {}).label || k[0].toUpperCase() + k.slice(1); }
  function swatchAttrs(key) {
    const s = (UI.STATES && UI.STATES[key]) || {};
    if (s.overlay) return { [s.overlay === 'current' ? 'data-current' : `data-${s.overlay}`]: '' };
    if (s.tier) return { 'data-tier': s.tier };
    return { 'data-status': key };
  }
  function timeLine(list) {
    const done = list.filter(c => c.ms && c.status !== 'future');
    const over = done.filter(c => overBudget(c)).length;
    const avg = done.length ? done.reduce((a, c) => a + c.ms, 0) / done.length : 0;
    return `Over budget: ${over} · average ${msx(avg)}`;
  }
  // X5's order: unanswered by position, then marked, then guesses
  function queueOf(list, kinds) {
    const out = [];
    const add = i => { if (!out.includes(i)) out.push(i); };
    if (kinds.includes('unanswered')) list.forEach((c, i) => { if (c.status === 'unanswered' || c.status === 'skipped') add(i); });
    if (kinds.includes('flag')) list.forEach((c, i) => { if (c.flag) add(i); });
    if (kinds.includes('guess')) list.forEach((c, i) => { if (c.conf === 'guess') add(i); });
    return out;
  }

  /* ------------------------------------------------------------ UI.checkYourWork (QBank 2.7, Tests 4.5, P20, X3, X5) */
  function checkYourWork(host, cells, o = {}) {
    const exam = o.mode === 'exam';
    let list = cells.slice();
    let show = 'status';
    let tileFilter = null;
    const qKinds = new Set(o.queue || ['unanswered', 'flag']);
    let order = o.order || 'position';
    let saving = o.saving || null;
    const el = h('section', { class: 'cyw', id: o.id || null, 'aria-labelledby': uid('cyw') });
    const h1 = h('h1', { class: 'h1 cyw-h', id: el.getAttribute('aria-labelledby'), text: o.title || 'Check your work' });
    const meta = h('p', { class: 'meta cyw-meta' });
    const lead = h('p', { class: 'cyw-lead', text: o.lead || (exam ? 'Select a question to go back to it. Once you move on, you can’t come back to this module.' : 'Select a question to go back to it. Skipped and unanswered questions can still be answered before you finish.') });
    const tiles = h('div', { class: 'stats cyw-tiles' });
    const qrow = h('div', { class: 'cyw-queue' });
    const showRow = h('div', { class: 'cyw-show' });
    const grid = h('div', { class: 'cell-grid cyw-grid', role: 'grid', 'aria-label': 'Questions' });
    const lines = h('div', { class: 'cyw-lines', 'aria-live': 'polite' });
    const foot = h('div', { class: 'cyw-foot' });
    el.append(h1, meta, lead, tiles, qrow, showRow, grid, lines);
    if (o.foot !== false) el.append(foot);
    grid.addEventListener('click', e => {
      const b = e.target.closest('.cell');
      if (b && !b.disabled && !b.hasAttribute('data-filtered') && o.onPick) o.onPick(+b.dataset.i);
    });
    gridKeys(grid);

    // Show: Status / Time
    if (UI.seg) {
      const sg = UI.seg(null, [{ value: 'status', label: 'Status' }, { value: 'time', label: 'Time' }], { value: show, label: 'Show', onChange: v => { show = v; draw(); } });
      showRow.append(h('span', { class: 'k', text: 'Show' }), sg.el);
    }
    const pace = () => o.pace_ms || 95000;
    const tileDefs = () => {
      const t = tally(list);
      const d = exam
        ? [['answered', 'Answered', t.answered], ['unanswered', 'Unanswered', t.unanswered], ['flag', 'For review', t.flag]]
        : [['answered', 'Answered', t.answered], ['unanswered', 'Unanswered', t.unanswered], ['skipped', 'Skipped', t.skipped], ['flag', 'Marked', t.flag]];
      if (o.confidence) d.push(['guess', 'Guesses', t.guess]);
      return d;
    };
    const inTile = (c, k) => k === 'answered' ? answeredish(c.status) && c.status !== 'future'
      : k === 'unanswered' ? c.status === 'unanswered' || (exam && c.status === 'skipped')
      : k === 'skipped' ? c.status === 'skipped' : k === 'flag' ? !!c.flag : k === 'guess' ? c.conf === 'guess' : true;
    function queueList() {
      const kinds = [...qKinds];
      let q = queueOf(list, kinds);
      if (order === 'value' && o.value) q = q.slice().sort((a, b) => (o.value(b) || 0) - (o.value(a) || 0));
      return q;
    }
    function draw() {
      const t = tally(list);
      meta.textContent = [o.meta, o.left !== null && o.left !== undefined && o.timed !== false ? `${mmss(o.left)} left` : null].filter(Boolean).join(' · ');
      tiles.style.setProperty('--cols', String(tileDefs().length));
      tiles.replaceChildren(...tileDefs().map(([k, label, n]) => {
        const b = h('button', { type: 'button', class: 'stat', 'aria-pressed': String(tileFilter === k), 'data-tile': k },
          h('span', { class: 'stat-k', text: label }), h('span', { class: 'stat-v', text: fmtN(n) }));
        b.addEventListener('click', () => { tileFilter = tileFilter === k ? null : k; draw(); });
        return b;
      }));
      // X5: one queue, in the order that earns most
      qrow.replaceChildren();
      if (o.onGo) {
        const counts = { unanswered: t.unanswered + (exam ? 0 : t.skipped), flag: t.flag, guess: t.guess };
        const kinds = [['unanswered', 'Unanswered'], ['flag', exam ? 'For review' : 'Marked']];
        if (o.confidence) kinds.push(['guess', 'Guesses']);
        const chips = h('div', { class: 'choices cyw-qchips', role: 'group', 'aria-label': 'Go through' });
        kinds.forEach(([k, label]) => {
          const b = h('button', { type: 'button', 'aria-pressed': String(qKinds.has(k)), disabled: counts[k] ? null : true }, label, h('span', { class: 'n', text: ` ${counts[k]}` }));
          b.addEventListener('click', () => { qKinds.has(k) ? qKinds.delete(k) : qKinds.add(k); draw(); });
          chips.append(b);
        });
        const q = queueList();
        const go = h('button', { type: 'button', class: 'pill cyw-go', disabled: q.length ? null : true, title: 'Enter' }, `Go through ${q.length}`);
        go.addEventListener('click', () => { const l = queueList(); if (l.length) o.onGo(l); });
        qrow.append(chips, go);
        if (o.training && o.value && UI.seg) {
          const og = UI.seg(null, [{ value: 'position', label: 'By position' }, { value: 'value', label: 'Best value first' }], { value: order, label: 'Order', onChange: v => { order = v; draw(); } });
          qrow.append(h('span', { class: 'cyw-order' }, h('span', { class: 'k', text: 'Order' }), og.el));
        }
      }
      grid.classList.toggle('timed', show === 'time');
      grid.replaceChildren(...list.map((c, i) => {
        const opts = { flag: c.flag || null, note: c.note || null, filtered: tileFilter && !inTile(c, tileFilter) ? true : null, label: cellLabel(c, i, exam),
          over: show === 'time' && c.ms > 2 * (c.budget_ms || pace()) ? true : null };
        const b = UI.cell ? UI.cell(c.status || 'unanswered', c.n ?? i + 1, opts) : h('button', { type: 'button', class: 'cell', 'aria-label': opts.label }, c.n ?? i + 1);
        b.dataset.i = i;
        if (c.status === 'future') b.disabled = true;
        if (show === 'time') b.append(h('span', { class: 'c-sub', text: c.ms ? msx(c.ms) : '0:00', 'aria-hidden': 'true' }));
        if (queueList().includes(i)) b.dataset.queued = '';
        return b;
      }));
      roving(grid, list.findIndex(c => c.current));
      // the lines, each only when it applies (P20's order; Tests 4.5)
      lines.replaceChildren();
      if (show === 'time') lines.append(h('p', { class: 'meta', text: `Pace is ${msx(pace())} a question${exam ? ' · a ring is over twice that' : ''}` }));
      const blanks = list.map((c, i) => ({ c, i })).filter(x => x.c.status === 'unanswered' || x.c.status === 'skipped');
      if (blanks.length) {
        const text = exam
          ? `${plural(blanks.length, 'question')} unanswered. A blank is marked wrong, and a wrong answer costs no more than a blank, so guess before you move on.`
          : `${plural(blanks.length, 'question')} unanswered. A blank scores the same as a wrong answer: put your best guess on each.`;
        lines.append(line(text, o.triage !== false ? blanks.slice(0, 12).map(x => x.i) : []));
      }
      if (!exam && o.triage !== false) {
        const unsure = list.map((c, i) => ({ c, i })).filter(x => x.c.conf === 'unsure' && answeredish(x.c.status));
        if (o.end && unsure.length) lines.append(line(`${plural(unsure.length, 'answer')} marked Unsure: revisit them`, unsure.slice(0, 12).map(x => x.i)));
        const marked = list.map((c, i) => ({ c, i })).filter(x => x.c.flag);
        if (marked.length) lines.append(line(`${marked.length} marked for review`, marked.slice(0, 12).map(x => x.i)));
      }
      if (Number.isFinite(o.left) && o.timed !== false) {
        const todo = queueList().length || blanks.length;
        const keep = o.training ? 180 : 0;
        const per = todo ? Math.max(0, (o.left - keep) / todo) : 0;
        lines.append(h('p', { class: 'cyw-pace', text: [`${mmss(o.left)} left`, keep ? `keep ${mmss(keep)} for checking` : null, todo ? `about ${per >= 60 ? mmss(per) : Math.round(per) + ' s'} for each ${blanks.length ? 'unanswered question' : 'of these'}` : null].filter(Boolean).join(' · ') }));
      }
      if (saving && saving.size) {
        const offline = saving.state === 'offline';
        lines.append(h('p', { class: 'cyw-saving' },
          offline ? 'You’re offline. Your answers are kept on this device and sent when you reconnect.' : `${plural(saving.n || saving.size, 'answer')} ${saving.n === 1 || saving.size === 1 ? 'is' : 'are'} still saving`,
          saving.retry && !offline ? h('button', { type: 'button', class: 'quiet', text: 'Retry', onclick: () => saving.retry() }) : null));
      }
      // the footer: the save status, Back to question N, the move-on pill
      foot.replaceChildren();
      const stat = h('p', { class: 'cyw-status mono', text: saving ? saving.text || '' : '' });
      const acts = h('div', { class: 'cyw-acts' });
      if (o.onBack) acts.append(h('button', { type: 'button', class: 'quiet', onclick: () => o.onBack() }, o.backLabel || 'Back to questions'));
      if (o.onFinish) {
        const blocked = saving && saving.size && saving.state !== 'offline' && !o.ackSaving;
        const b = h('button', { type: 'button', class: 'pill cyw-finish', disabled: blocked ? true : null }, o.finishLabel || (exam ? 'Hand in' : 'Finish set'));
        b.addEventListener('click', () => o.onFinish());
        acts.append(b);
      }
      foot.append(stat, acts);
    }
    function line(text, goto) {
      const p = h('div', { class: 'cyw-line' }, h('p', { class: 'mistake', text }));
      if (goto && goto.length && o.onPick) p.append(h('div', { class: 'cyw-gos' }, goto.map(i => h('button', { type: 'button', class: 'btn sm', onclick: () => o.onPick(i) }, `Go to ${list[i].n ?? i + 1}`))));
      return p;
    }
    draw();
    if (host) host.append(el);
    return {
      el, foot,
      update(c, patch = {}) { if (c) list = c.slice(); Object.assign(o, patch); if ('saving' in patch) saving = patch.saving; draw(); },
      queue: queueList,
      focus() { const b = qrow.querySelector('.cyw-go:not(:disabled)') || tiles.querySelector('button'); if (b) b.focus({ preventScroll: true }); },
    };
  }

  /* ------------------------------------------------------------ UI.annotate (QBank 2.5, Tests 4.8, X9)
     Marks are {addr, start, end, style, note}: offsets into the text of the [data-addr] node
     ('s' the stem, 't:r:c' a table cell, 'o:i' an option). A node with math or a figure
     in it takes a whole-node mark (start = end = 0). The text is never rewritten, so a
     render only wraps ranges in <mark class="hl">; unwrap puts the text back. */
  const HL = [
    ['ask', 'Asked for', 'Box: what the question asks for'], ['given', 'Given', 'Highlight: what you are given'],
    ['ignore', 'Ignore', 'Strike: information that doesn’t matter'], ['strong', 'Strong', 'Strong highlight'],
    ['under', 'Underline', 'Underline'], ['dashed', 'Dashed', 'Dashed underline'], ['dotted', 'Dotted', 'Dotted underline'],
  ];
  const HL_IDS = new Set(HL.map(x => x[0]));
  function annotate(host, marks = [], o = {}) {
    const clean = m => ({ addr: String(m.addr || 's'), start: Math.max(0, +m.start || 0), end: Math.max(0, +m.end || 0),
      style: HL_IDS.has(m.style) ? m.style : 'given', note: String(m.note || '').slice(0, 500) });
    let list = (marks || []).map(clean).filter(m => m.end > m.start || (m.start === 0 && m.end === 0));
    let editable = !!o.editable, dead = false, bar = null, pop = null, selT = 0;
    const node = addr => [...host.querySelectorAll('[data-addr]')].find(e => e.dataset.addr === addr) || null;
    const whole = el => !!(el && el.querySelector('.katex, svg, img, math'));
    const addrOf = n => { const e = n && (n.nodeType === 3 ? n.parentElement : n); const a = e && e.closest && e.closest('[data-addr]'); return a && host.contains(a) ? a : null; };
    const offsetIn = (el, n, off) => { const r = doc.createRange(); r.setStart(el, 0); r.setEnd(n, off); return r.toString().length; };
    function unwrap() {
      const touched = new Set();
      host.querySelectorAll('mark.hl').forEach(m => { touched.add(m.parentNode); m.replaceWith(...m.childNodes); });
      touched.forEach(p => p && p.normalize && p.normalize());
      host.querySelectorAll('[data-hl]').forEach(e => { e.removeAttribute('data-hl'); e.removeAttribute('data-hl-note'); e.removeAttribute('data-k'); });
    }
    function wrap(el, m, k) {
      if (m.start === 0 && m.end === 0) { el.dataset.hl = m.style; el.dataset.k = k; if (m.note) el.dataset.hlNote = ''; return; }
      const w = doc.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      const nodes = [];
      for (let t = w.nextNode(); t; t = w.nextNode()) nodes.push(t);
      let pos = 0;
      for (const tn of nodes) {
        const len = tn.data.length, a = pos;
        pos += len;
        if (pos <= m.start || a >= m.end) continue;
        const s0 = Math.max(0, m.start - a), e0 = Math.min(len, m.end - a);
        let t = tn;
        if (e0 < len) t.splitText(e0);
        if (s0 > 0) t = t.splitText(s0);
        const mk = h('mark', { class: `hl hl-${m.style}`, 'data-k': k, 'data-note': m.note ? '' : null, title: m.note || null });
        t.parentNode.insertBefore(mk, t);
        mk.append(t);
      }
    }
    function render() {
      if (dead) return;
      unwrap();
      list.forEach((m, k) => { const el = node(m.addr); if (el) wrap(el, m, k); });
      host.classList.toggle('annotating', editable);
    }
    // a new mark takes the characters it covers from older ones (one style per character)
    function carve(addr, s, e) {
      const out = [];
      list.forEach(m => {
        if (m.addr !== addr || m.end <= s || m.start >= e || (m.start === 0 && m.end === 0 && s !== 0)) { out.push(m); return; }
        if (m.start < s) out.push(Object.assign({}, m, { end: s }));
        if (m.end > e) out.push(Object.assign({}, m, { start: e }));
      });
      list = out;
    }
    function changed() { render(); if (o.onChange) o.onChange(list.map(m => Object.assign({}, m))); }
    function add(sel, style, note = '') {
      const m = sel.whole ? { addr: sel.addr, start: 0, end: 0, style, note } : { addr: sel.addr, start: sel.start, end: sel.end, style, note };
      if (sel.whole) list = list.filter(x => x.addr !== sel.addr); else carve(sel.addr, sel.start, sel.end);
      list.push(m);
      list.sort((a, b) => a.addr.localeCompare(b.addr) || a.start - b.start);
      changed();
      return list.indexOf(m);
    }
    function selInfo() {
      const sel = getSelection && getSelection();
      if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
      const r = sel.getRangeAt(0);
      const el = addrOf(r.startContainer);
      if (!el) return null;
      if (whole(el)) return { el, addr: el.dataset.addr, start: 0, end: 0, whole: true, range: r };
      let endN = r.endContainer, endO = r.endOffset;
      if (!el.contains(endN)) { endN = el; endO = el.childNodes.length; }
      const start = offsetIn(el, r.startContainer, r.startOffset), end = offsetIn(el, endN, endO);
      if (end <= start) return null;
      return { el, addr: el.dataset.addr, start, end, range: r };
    }
    const overlaps = s => list.some(m => m.addr === s.addr && (s.whole || (m.start === 0 && m.end === 0) || (m.end > s.start && m.start < s.end)));
    function swatches(onPick, current) {
      return h('div', { class: 'hl-sw', role: 'group', 'aria-label': 'Mark style' }, HL.map(([id, label, tip]) => {
        const b = h('button', { type: 'button', class: `hl-b hl-b-${id}`, 'aria-label': label, title: tip, 'aria-pressed': current ? String(current === id) : null },
          h('span', { class: `hl-demo hl-${id}`, text: 'Ab', 'aria-hidden': 'true' }), h('span', { class: 'hl-l', text: label }));
        b.addEventListener('click', () => onPick(id));
        return b;
      }));
    }
    function closeBar() { if (bar) { const b = bar; bar = null; try { b.close(); } catch (_) {} } }
    function showBar(sel) {
      closeBar();
      if (!UI.pop) return;
      const content = h('div', { class: 'hl-bar-in' });
      content.addEventListener('pointerdown', e => { if (!e.target.closest('textarea, input')) e.preventDefault(); });   // the selection stays
      content.append(swatches(style => { add(sel, style); getSelection().removeAllRanges(); closeBar(); }));
      const acts = h('div', { class: 'hl-acts' },
        h('button', { type: 'button', class: 'btn sm', onclick: () => { const k = add(sel, 'given'); getSelection().removeAllRanges(); closeBar(); openMark(k); } }, icon('note', 16), 'Note'));
      if (overlaps(sel)) acts.append(h('button', { type: 'button', class: 'quiet sm', onclick: () => {
        if (sel.whole) list = list.filter(m => m.addr !== sel.addr); else carve(sel.addr, sel.start, sel.end);
        changed(); getSelection().removeAllRanges(); closeBar();
      } }, 'Remove'));
      content.append(acts);
      bar = UI.pop(sel.range, content, { anchored: true, focus: false, className: 'hl-bar', label: 'Highlights and notes', onClose: () => { bar = null; } });
    }
    function openMark(k, anchor) {
      const m = list[k];
      if (!m || !UI.pop) return;
      if (pop) { try { pop.close(); } catch (_) {} pop = null; }
      const at = anchor || host.querySelector(`[data-k="${k}"]`) || node(m.addr);
      const body = h('div', { class: 'hl-pop' });
      const paint = () => {
        body.replaceChildren();
        body.append(h('p', { class: m.note ? 'hl-note' : 'hl-note none', text: m.note || 'No note' }));
        if (!editable) return;
        const ta = h('textarea', { class: 'field hl-ta', rows: '3', maxlength: '500', 'aria-label': 'Note', hidden: true });
        ta.value = m.note;
        const cnt = UI.counter ? UI.counter(ta, 500) : null;
        const save = h('button', { type: 'button', class: 'btn sm', hidden: true, text: 'Save note' });
        const edit = h('button', { type: 'button', class: 'btn sm', text: m.note ? 'Edit note' : 'Add a note' });
        edit.addEventListener('click', () => { ta.hidden = false; save.hidden = false; edit.hidden = true; ta.focus(); });
        save.addEventListener('click', () => { m.note = ta.value.trim().slice(0, 500); changed(); paint(); });
        ta.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) save.click(); });
        body.append(ta, cnt, h('div', { class: 'hl-acts' }, edit, save));
        body.append(swatches(style => { m.style = style; changed(); paint(); }, m.style));
        body.append(h('div', { class: 'hl-acts' },
          h('button', { type: 'button', class: 'quiet sm', text: 'Remove', onclick: () => { list.splice(list.indexOf(m), 1); changed(); if (pop) pop.close(); } }),
          h('button', { type: 'button', class: 'quiet sm', text: 'Close', onclick: () => { if (pop) pop.close(); } })));
      };
      paint();
      pop = UI.pop(at, body, { label: 'Mark', className: 'hl-popover', onClose: () => { pop = null; } });
    }
    const onSel = () => {
      clearTimeout(selT);
      selT = setTimeout(() => {
        if (!editable || dead) return;
        const s = selInfo();
        if (s) showBar(s); else if (bar && !(doc.activeElement && bar.el && bar.el.contains(doc.activeElement))) closeBar();
      }, 160);
    };
    const onClick = e => {
      const mk = e.target.closest && e.target.closest('mark.hl, [data-hl]');
      if (!mk || !host.contains(mk)) return;
      if (!editable && !(o.readonly && list[+mk.dataset.k] && list[+mk.dataset.k].note)) return;
      const s = getSelection && getSelection();
      if (s && !s.isCollapsed) return;                      // a drag that made a selection is not a click on a mark
      e.preventDefault();
      e.stopPropagation();
      openMark(+mk.dataset.k, mk);
    };
    doc.addEventListener('selectionchange', onSel);
    host.addEventListener('click', onClick, true);
    render();
    return {
      el: host,
      marks: () => list.map(m => Object.assign({}, m)),
      notes: () => list.filter(m => m.note).map(m => Object.assign({}, m)),
      get count() { return list.length; },
      set(ms) { list = (ms || []).map(clean); render(); },
      render,
      get editable() { return editable; },
      set editable(v) { editable = !!v; if (!editable) closeBar(); render(); },
      closeBar,
      destroy() {
        dead = true;
        closeBar();
        if (pop) { try { pop.close(); } catch (_) {} }
        doc.removeEventListener('selectionchange', onSel);
        host.removeEventListener('click', onClick, true);
        unwrap();
        host.classList.remove('annotating');
      },
    };
  }
  annotate.STYLES = HL.map(([id, label]) => ({ id, label }));

  /* ------------------------------------------------------------ UI.scratch (X8): a pen layer and a typed box
     data {w, text, strokes: [{t: 'pen' | 'marker', p: [x, y, x, y, ...]}], typed}; w is the column
     width when drawn and text the text size, so the ink lines up again. At most 20 KB. */
  function rdp(pts, eps) {
    if (pts.length <= 4) return pts;
    const n = pts.length / 2, keep = new Uint8Array(n);
    keep[0] = keep[n - 1] = 1;
    const stack = [[0, n - 1]];
    while (stack.length) {
      const [a, b] = stack.pop();
      const ax = pts[a * 2], ay = pts[a * 2 + 1], bx = pts[b * 2], by = pts[b * 2 + 1];
      const dx = bx - ax, dy = by - ay, len = Math.hypot(dx, dy) || 1;
      let far = 0, at = -1;
      for (let i = a + 1; i < b; i++) {
        const d = Math.abs(dy * pts[i * 2] - dx * pts[i * 2 + 1] + bx * ay - by * ax) / len;
        if (d > far) { far = d; at = i; }
      }
      if (far > eps && at > 0) { keep[at] = 1; stack.push([a, at], [at, b]); }
    }
    const out = [];
    for (let i = 0; i < n; i++) if (keep[i]) out.push(Math.round(pts[i * 2] * 10) / 10, Math.round(pts[i * 2 + 1] * 10) / 10);
    return out;
  }
  rdp.__test = () => rdp([0, 0, 1, 0.2, 2, 0, 3, 0.1, 4, 0], 1).length === 4 && rdp([0, 0, 5, 5, 10, 0], 1).length === 6;
  const SCRATCH_MAX = 20000;
  function scratch(host, o = {}) {
    const d0 = o.data || {};
    let data = { w: +d0.w || 0, text: d0.text || doc.documentElement.dataset.text || 'normal', strokes: Array.isArray(d0.strokes) ? d0.strokes.slice() : [], typed: String(d0.typed || '') };
    let editable = !!o.editable, tool = 'pen', dead = false;
    const layer = h('div', { class: 'scratch', 'aria-hidden': 'true' });
    const canvas = h('canvas', { class: 'scratch-c' });
    layer.append(canvas);
    host.classList.add('has-scratch');
    host.append(layer);
    const ctx = canvas.getContext('2d');
    const bar = h('div', { class: 'scratch-bar', role: 'toolbar', 'aria-label': 'Scratch' });
    const tools = [['pen', 'Pen', 'pen'], ['marker', 'Marker', 'marker'], ['eraser', 'Eraser', 'erase']];
    const tb = tools.map(([id, label, ic]) => {
      const b = h('button', { type: 'button', class: 'tool', 'aria-pressed': String(tool === id), 'data-tool': id }, icon(ic, 18), h('span', { text: label }));
      b.addEventListener('click', () => { tool = id; tb.forEach(x => x.setAttribute('aria-pressed', String(x.dataset.tool === id))); });
      return b;
    });
    bar.append(...tb,
      h('button', { type: 'button', class: 'tool', onclick: () => { if (!data.strokes.length) return; data.strokes = []; draw(); save(); } }, icon('x', 18), h('span', { text: 'Clear' })),
      h('button', { type: 'button', class: 'tool scratch-done', onclick: () => { if (o.onDone) o.onDone(); } }, icon('check', 18), h('span', { text: 'Done' })));
    const ta = h('textarea', { class: 'field scratch-ta', rows: '3', maxlength: '1000', spellcheck: 'false', 'aria-label': 'Typed scratch' });
    ta.value = data.typed;
    const typedBox = h('div', { class: 'scratch-typed' }, h('label', { class: 'k', text: 'Typed scratch' }), ta, UI.counter ? UI.counter(ta, 1000) : null);
    let typedT = 0;
    ta.addEventListener('input', () => { clearTimeout(typedT); typedT = setTimeout(() => { data.typed = ta.value.slice(0, 1000); save(); }, 500); });
    const ink = () => getComputedStyle(host).getPropertyValue('--ink').trim() || '#3F3F3F';
    function size() {
      const w = host.clientWidth, hh = Math.max(host.scrollHeight, host.clientHeight);
      const dpr = Math.min(2, devicePixelRatio || 1);
      canvas.style.width = w + 'px'; canvas.style.height = hh + 'px';
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(hh * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const k = data.w ? host.clientWidth / data.w : 1;
      const col = ink();
      data.strokes.forEach(s => {
        const p = s.p || [];
        if (p.length < 2) return;
        ctx.beginPath();
        ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        ctx.strokeStyle = col;
        ctx.globalAlpha = s.t === 'marker' ? 0.28 : 1;
        ctx.lineWidth = s.t === 'marker' ? 12 : 2;
        ctx.moveTo(p[0] * k, p[1] * k);
        for (let i = 2; i < p.length; i += 2) ctx.lineTo(p[i] * k, p[i + 1] * k);
        if (p.length === 2) ctx.lineTo(p[0] * k + 0.1, p[1] * k);
        ctx.stroke();
      });
      ctx.globalAlpha = 1;
    }
    function payload() { return { w: data.w || host.clientWidth, text: data.text, strokes: data.strokes, typed: data.typed }; }
    function save() {
      let p = payload();
      let eps = 2;
      while (JSON.stringify(p).length > SCRATCH_MAX && eps <= 8) {
        data.strokes = data.strokes.map(s => Object.assign({}, s, { p: rdp(s.p, eps) }));
        p = payload();
        eps *= 2;
      }
      if (JSON.stringify(p).length > SCRATCH_MAX) { data.strokes.pop(); draw(); toast('Scratch is full for this question. Clear some to draw more.'); p = payload(); }
      if (o.onChange) o.onChange(p);
    }
    const pointers = new Map();
    let cur = null, lastY = 0;
    const at = e => { const r = host.getBoundingClientRect(); const k = data.w ? data.w / host.clientWidth : 1; return [(e.clientX - r.left) * k, (e.clientY - r.top) * k]; };
    function erase(x, y) {
      const before = data.strokes.length;
      data.strokes = data.strokes.filter(s => { for (let i = 0; i < s.p.length; i += 2) if (Math.hypot(s.p[i] - x, s.p[i + 1] - y) < 10) return false; return true; });
      if (data.strokes.length !== before) draw();
    }
    canvas.addEventListener('pointerdown', e => {
      if (!editable) return;
      pointers.set(e.pointerId, e.clientY);
      if (pointers.size > 1) { cur = null; lastY = e.clientY; return; }        // two fingers scroll
      canvas.setPointerCapture(e.pointerId);
      if (!data.w) data.w = host.clientWidth;
      const [x, y] = at(e);
      if (tool === 'eraser') { cur = { erase: true }; erase(x, y); return; }
      cur = { t: tool, p: [x, y] };
      e.preventDefault();
    });
    canvas.addEventListener('pointermove', e => {
      if (!editable) return;
      if (pointers.size > 1) { const y = e.clientY; scrollBy(0, lastY - y); lastY = y; return; }
      if (!cur) return;
      const [x, y] = at(e);
      if (cur.erase) { erase(x, y); return; }
      cur.p.push(x, y);
      const k = data.w ? host.clientWidth / data.w : 1, p = cur.p, n = p.length;
      ctx.beginPath(); ctx.strokeStyle = ink(); ctx.lineCap = 'round';
      ctx.globalAlpha = cur.t === 'marker' ? 0.28 : 1; ctx.lineWidth = cur.t === 'marker' ? 12 : 2;
      ctx.moveTo(p[n - 4] * k, p[n - 3] * k); ctx.lineTo(p[n - 2] * k, p[n - 1] * k); ctx.stroke(); ctx.globalAlpha = 1;
    });
    const up = e => {
      pointers.delete(e.pointerId);
      if (!cur) return;
      if (cur.erase) { cur = null; save(); return; }
      data.strokes.push({ t: cur.t, p: rdp(cur.p, 1) });
      cur = null;
      draw();
      save();
    };
    canvas.addEventListener('pointerup', up);
    canvas.addEventListener('pointercancel', up);
    let ro = null;
    if (window.ResizeObserver) { ro = new ResizeObserver(() => size()); ro.observe(host); }
    function setEditable(on) {
      editable = !!on;
      layer.classList.toggle('on', editable);
      host.classList.toggle('scratching', editable);
    }
    setEditable(editable);
    requestAnimationFrame(size);
    return {
      el: layer, bar, typed: typedBox,
      data: payload,
      get editable() { return editable; },
      set editable(v) { setEditable(v); },
      set(d) { data = Object.assign({ w: 0, strokes: [], typed: '' }, d || {}); ta.value = data.typed || ''; draw(); },
      redraw: size,
      destroy() { dead = true; if (ro) ro.disconnect(); layer.remove(); bar.remove(); typedBox.remove(); host.classList.remove('has-scratch', 'scratching'); clearTimeout(typedT); },
      get dead() { return dead; },
    };
  }

  /* ------------------------------------------------------------ the reference, searchable (X9, P24)
     The sheet the test gives you, with an id on each entry. ponytail: a copy of ui.js's
     drawings; when ui.js exports them (UI.REF), read those. */
  const F = 'font-family="Source Serif 4, serif" font-style="italic"';
  const REF = [
    ['Area', [
      ['ref-circle', 'Circle', 'circle area circumference radius pi πr', `<circle cx="30" cy="28" r="20" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M30 28h20" stroke="currentColor" stroke-width="1.3"/><text x="38" y="24" font-size="11" ${F}>r</text>`, '<i>A</i> = π<i>r</i>²<br><i>C</i> = 2π<i>r</i>'],
      ['ref-rectangle', 'Rectangle', 'rectangle area length width', `<rect x="8" y="12" width="44" height="30" fill="none" stroke="currentColor" stroke-width="1.5"/><text x="30" y="54" font-size="11" text-anchor="middle" ${F}>ℓ</text><text x="1" y="31" font-size="11" ${F}>w</text>`, '<i>A</i> = ℓ<i>w</i>'],
      ['ref-triangle', 'Triangle', 'triangle area base height', `<path d="M6 42 L56 42 L38 12 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M38 12 L38 42" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/><text x="42" y="30" font-size="10" ${F}>h</text><text x="28" y="54" font-size="10" ${F}>b</text>`, '<i>A</i> = ½<i>bh</i>'],
    ]],
    ['Right triangles', [
      ['ref-pythagorean', 'Pythagorean theorem', 'pythagorean theorem hypotenuse right triangle a2 b2 c2', `<path d="M10 42 L50 42 L50 12 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M46 42 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="28" y="54" font-size="10" ${F}>b</text><text x="54" y="30" font-size="10" ${F}>a</text><text x="24" y="24" font-size="10" ${F}>c</text>`, '<i>c</i>² = <i>a</i>² + <i>b</i>²'],
      ['ref-30-60-90', 'Special right triangle 30-60-90', 'special right triangle 30-60-90 30 60 90 sqrt3', `<path d="M8 43 L52 43 L52 18 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M48 43 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="11" y="39" font-size="8" font-family="Source Serif 4, serif">30°</text><text x="41" y="27" font-size="8" font-family="Source Serif 4, serif">60°</text>`, '<i>x</i>, <i>x</i>√3, 2<i>x</i>'],
      ['ref-45-45-90', 'Special right triangle 45-45-90', 'special right triangle 45-45-90 45 90 isosceles sqrt2', `<path d="M14 43 L50 43 L50 7 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M46 43 v-4 h4" fill="none" stroke="currentColor" stroke-width="1.1"/><text x="17" y="39" font-size="8" font-family="Source Serif 4, serif">45°</text><text x="38" y="18" font-size="8" font-family="Source Serif 4, serif">45°</text>`, '<i>s</i>, <i>s</i>, <i>s</i>√2'],
    ]],
    ['Volume', [
      ['ref-box', 'Rectangular prism', 'box rectangular prism volume length width height', `<rect x="12" y="20" width="28" height="22" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 20 L23 12 L51 12 L40 20 M40 42 L51 34 L51 12" fill="none" stroke="currentColor" stroke-width="1.3"/>`, '<i>V</i> = ℓ<i>wh</i>'],
      ['ref-cylinder', 'Cylinder', 'cylinder volume', `<ellipse cx="30" cy="15" rx="16" ry="5.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M14 15v22a16 5.5 0 0 0 32 0V15" fill="none" stroke="currentColor" stroke-width="1.4"/>`, '<i>V</i> = π<i>r</i>²<i>h</i>'],
      ['ref-sphere', 'Sphere', 'sphere ball volume', `<circle cx="30" cy="28" r="18" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="30" cy="28" rx="18" ry="6.5" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 3"/>`, '<i>V</i> = <sup>4</sup>⁄<sub>3</sub>π<i>r</i>³'],
      ['ref-cone', 'Cone', 'cone volume', `<path d="M30 8 L49 41 L11 41 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="30" cy="41" rx="19" ry="5.5" fill="none" stroke="currentColor" stroke-width="1.1"/>`, '<i>V</i> = <sup>1</sup>⁄<sub>3</sub>π<i>r</i>²<i>h</i>'],
      ['ref-pyramid', 'Pyramid', 'pyramid volume', `<path d="M30 8 L52 38 L8 38 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 38 L19 45 L52 45 L52 38" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M30 8 L52 45" fill="none" stroke="currentColor" stroke-width="1.1"/>`, '<i>V</i> = <sup>1</sup>⁄<sub>3</sub>ℓ<i>wh</i>'],
    ]],
    ['Facts', [
      ['ref-360', 'Degrees in a circle', 'degrees arc circle 360', null, 'The number of degrees of arc in a circle is 360.'],
      ['ref-2pi', 'Radians in a circle', 'radians arc circle 2pi 2π', null, 'The number of radians of arc in a circle is 2π.'],
      ['ref-180', 'Angles of a triangle', 'sum angles triangle 180 degrees', null, 'The sum of the measures in degrees of the angles of a triangle is 180.'],
    ]],
  ];
  function refDock(host, o = {}) {
    const el = h('div', { class: 'refd' });
    const search = h('input', { type: 'search', class: 'field refd-q', placeholder: 'Search: cyl, 30-60-90', 'aria-label': 'Search the reference sheet', autocomplete: 'off', spellcheck: 'false' });
    const groups = REF.map(([name, items]) => {
      const d = h('details', { class: 'refd-g', open: true }, h('summary', { text: name }));
      const rows = items.map(([id, label, keys, art, f]) => {
        const r = h('div', { class: 'refd-e', id: (o.idPrefix || '') + id, 'data-ref': id, 'data-keys': `${label} ${keys}`.toLowerCase() },
          art ? h('span', { class: 'refd-art', html: `<svg width="60" height="56" viewBox="0 0 60 56" aria-hidden="true">${art}</svg>` }) : null,
          h('span', { class: 'refd-t' }, h('b', { text: label }), h('span', { class: 'refd-f', html: f })));
        d.append(r);
        return r;
      });
      return { d, rows };
    });
    const none = h('p', { class: 'meta refd-none', hidden: true, text: 'Nothing on the sheet matches. It gives the formulas above only.' });
    el.append(search, ...groups.map(g => g.d), none);
    function filter(q) {
      const words = String(q || '').toLowerCase().trim().split(/\s+/).filter(Boolean);
      let shown = 0;
      groups.forEach(g => {
        let any = 0;
        g.rows.forEach(r => { const ok = words.every(w => r.dataset.keys.includes(w)); r.hidden = !ok; if (ok) any++; });
        g.d.hidden = !any;
        if (words.length && any) g.d.open = true;
        shown += any;
      });
      none.hidden = !!shown;
    }
    search.addEventListener('input', () => filter(search.value));
    function highlight(id) {
      el.querySelectorAll('.refd-e.lit').forEach(x => x.classList.remove('lit'));
      const r = el.querySelector(`[data-ref="${id}"]`);
      if (!r) return false;
      search.value = ''; filter('');
      r.classList.add('lit');
      const g = r.closest('details'); if (g) g.open = true;
      r.scrollIntoView({ block: 'nearest', behavior: still() ? 'auto' : 'smooth' });
      return true;
    }
    if (o.highlight) setTimeout(() => highlight(o.highlight), 0);
    if (host) host.append(el);
    return { el, highlight, filter, focus() { search.focus({ preventScroll: true }); } };
  }
  // Under the right slot's width (and on a phone) the same list in a half-height sheet
  function refSheet(highlight) {
    if (!UI.sheet) return UI.ref && UI.ref.open ? UI.ref.open() : null;
    let d = null;
    const s = UI.sheet({ title: 'Reference', className: 'ref-sheet', size: 'm', body: b => { d = refDock(b, { highlight }); } });
    return { sheet: s, dock: d };
  }

  /* ------------------------------------------------------------ Directions (Tests 4.8), in College Board's words */
  const DIRECTIONS = `
    <p>The questions in this section address a number of important math skills. Use of a calculator is permitted for all questions.</p>
    <p><b>NOTES</b><br>Unless otherwise indicated:</p>
    <ul>
      <li>All variables and expressions represent real numbers.</li>
      <li>Figures provided are drawn to scale.</li>
      <li>All figures lie in a plane.</li>
      <li>The domain of a given function <i>f</i> is the set of all real numbers <i>x</i> for which <i>f</i>(<i>x</i>) is a real number.</li>
    </ul>
    <p>For <b>multiple-choice questions</b>, solve each problem and choose the correct answer from the choices provided. Each multiple-choice question has a single correct answer.</p>
    <p>For <b>student-produced response questions</b>, solve each problem and enter your answer as described below.</p>
    <ul>
      <li>If you find <b>more than one correct answer</b>, enter only one answer.</li>
      <li>You can enter up to 5 characters for a <b>positive</b> answer and up to 6 characters (including the negative sign) for a <b>negative</b> answer.</li>
      <li>If your answer is a <b>fraction</b> that doesn’t fit in the provided space, enter the decimal equivalent.</li>
      <li>If your answer is a <b>decimal</b> that doesn’t fit in the provided space, enter it by truncating or rounding at the fourth digit.</li>
      <li>If your answer is a <b>mixed number</b> (such as 3½), enter it as an improper fraction (7/2) or its decimal equivalent (3.5).</li>
      <li>Don’t enter <b>symbols</b> such as a percent sign, comma, or dollar sign.</li>
    </ul>`;
  const DIRS_KEY = 'satf.dirs.hide';
  function directionsSheet(o = {}) {
    if (!UI.sheet) return null;
    return UI.sheet({
      title: 'Directions', className: 'dirs-sheet', size: 'l',
      body: b => {
        b.append(h('div', { class: 'dirs', html: DIRECTIONS }));
        const ex = UI.spr && UI.spr.directions ? UI.spr.directions() : null;
        if (ex) { const t = ex.querySelector('table'); if (t) b.append(h('p', { class: 'k', text: 'Examples' }), t); }
        if (o.first) {
          const cb = h('input', { type: 'checkbox', checked: ls.get(DIRS_KEY, false) ? true : null });
          cb.addEventListener('change', () => ls.set(DIRS_KEY, cb.checked));
          b.append(h('label', { class: 'check dirs-skip' }, cb, 'Don’t show at the start'));
        }
      },
      actions: [{ label: 'Close', primary: true }],
    });
  }
  directionsSheet.skipped = () => !!ls.get(DIRS_KEY, false);

  /* ------------------------------------------------------------ UI.runner (R21, QBank 2, Tests 1 and 4)
     run = UI.runner(host, opts)
     opts
       mode        practice | exam                      feedback  instant | retry | end (practice)
       sid         the sitting's id (keys satf.clock.{sid}, satf.pos.{sid}, the calculator per sitting)
       title       'Linear functions + 2' | 'Math · Module 1 of 2'      short 'M1' (the phone footer)
       cells       one per slot: [{status, flag, note, tier, level, topic, ms, budget_ms, conf, trap}]
                   (a fixed set's unserved slots are status 'future')
       total       the set's length, or null for endless (default cells.length)
       items       [{q, state, fb, why, marks, note, marked, saved, conf, scratch, attempts}] known up front
                   (the test window has every question at begin); others come from on.load(i)
       at          the position to open (default satf.pos.{sid}, else 0)
       clock       {secondsLeft | elapsed, paused}   none: no clock
       pausable    practice drill sets             challenge  the daily challenge's rules (QBank 2.13)
       conditions  test_day | training (exam, X1)   confidence  the exam's Sure / Unsure / Guess (Training)
       pace        {budget_s: [..]} (exam Training, X3)   nudges  X4's banners (Training, default on)
       calc, ref, annotate, scratch, directions     which tools show (scratch defaults on in exam)
       prefs       show_timer, hide_timer, show_stopwatch, pace_alert, two_passes, first_tap,
                   option_reasons, open_explanations, confidence, calc_mode
       confActive  P7's active tagger               hideSkill  the skill stays hidden until the verdict
       workspace   extra UI.workspace opts (onHint, onOwn, formNudge, cover, coverTool, pad, ...)
       actions     the verdict's UI.questionActions ctx (practice)     more(items, run) -> items
       queue       a UI.saveQueue: #saved and Check your work follow its status
       who         the profile name (exam footer)   fullscreen, guardLeave   Tests 4.9
       on          load(i, how) -> item | Promise, check(i, answer, meta) -> fb | Promise, select(i, answer, meta),
                   time(i, ms, why), strike(i, k, on, by, struck), mark(i, on), save(i, on), note(i, text),
                   marks(i, marks), conf(i, v), scratch(i, data), state(i, patch), skip(i, meta), reveal(i, fb),
                   show(i, item), view(name, i), exit(how), finish(), pause(), resume(), timeUp(), discard(),
                   report(i, ctx), details(i), history(i), twins(list), fix(label, list), pref(key, value),
                   away({away_ms, away_n}), nudge({kind, qid, at, took}), queue(list)
     run   {el, at, ws, view, cells, timer, show(i, item), go(i), next(), back(), item(i, patch), cell(i, patch),
            setCells(cells, total), preload(i, item), review(), closeReview(i), navigator(), screen(node, foot),
            directions(first), say(text), banner(text, actions), status(info), reveal(fb), destroy()} */
  const G = 16, COL_MIN = 560, SLOT_W = 300;
  function statusOf(fb, q) {
    if (fb.status) return fb.status;
    if (fb.voided) return 'voided';
    if (fb.correct === true) return (fb.try || fb.tries || 1) > 1 ? 'mixed' : q && q.repair ? 'repaired' : 'correct';
    if (fb.correct === false) return 'incorrect';
    return 'answered';
  }
  function runner(host, o = {}) {
    const exam = o.mode === 'exam';
    const fbMode = exam ? 'end' : (o.feedback || 'instant');
    const endMode = !exam && fbMode === 'end';
    const challenge = !!o.challenge;
    const training = exam && o.conditions === 'training';
    const on = o.on || {};
    const emit = (name, ...a) => {
      const f = on[name];
      if (typeof f !== 'function') return undefined;
      try { return f(...a); } catch (e) { console.error(e); return undefined; }
    };
    const prefs = Object.assign({ show_timer: true, show_stopwatch: true, pace_alert: true, two_passes: true, confidence: 'ask', first_tap: false }, o.prefs || {});
    const sid = String(o.sid || 'sitting');
    const cfg = {
      calc: o.calc !== false, ref: o.ref !== false, annotate: o.annotate !== false,
      scratch: o.scratch ?? exam, dirs: o.directions ?? exam, pause: !!o.pausable && !exam && !challenge,
      conf: exam && training && !!o.confidence, pace: training && !!(o.pace && o.pace.budget_s && o.pace.budget_s.length),
      nudges: training && o.nudges !== false, noteMax: exam ? 500 : 1000,
    };
    let cells = (o.cells || []).map((c, i) => Object.assign({ n: i + 1, status: 'unanswered' }, c));
    let total = o.total === null ? null : (o.total ?? cells.length);
    const items = new Map();
    (o.items || []).forEach((it, i) => { if (it) items.set(i, it); });
    const pre = new Map();
    const timeAt = new Map(cells.map((c, i) => [i, +c.ms || 0]));
    let at = -1, ws = null, wsI = -1, view = 'loading', queue = null, dead = false;
    let visStart = null, ann = null, scr = null, annotateOn = false, scratchOn = false, navPop = null, navApi = null, cyw = null;
    let timerApi = null, splitCtl = null, lastOpened = null, slotTab = null, slotFloat = false, refApi = null, calcBase = null, calcOpenAt = null;
    const cleanups = [];
    const say = t => { live.textContent = ''; setTimeout(() => { live.textContent = t; }, 30); };
    const q = () => (items.get(at) || {}).q || {};
    const isMc = () => q().type !== 'spr';
    const msAt = i => (timeAt.get(i) || 0) + (i === at && visStart !== null ? performance.now() - visStart : 0);
    const last = () => total !== null && at >= total - 1;

    /* ---------------- the frame */
    const root = h('div', { class: `rn rn-${exam ? 'exam' : 'practice'}${challenge ? ' rn-challenge' : ''}`, 'data-feedback': fbMode });
    const live = h('p', { class: 'sr', role: 'status', 'aria-live': 'polite' });
    const tool = (id, label, ic, key, run, x = {}) => {
      const b = h('button', { type: 'button', class: 'tool rn-tool' + (x.cls ? ' ' + x.cls : ''), id: x.id || null, 'data-tool': id,
        'aria-pressed': x.toggle ? 'false' : null, title: key ? `${label} (${key})` : label, 'aria-keyshortcuts': key ? key.replace('Shift+', 'Shift+') : null },
        icon(ic, 20), h('span', { class: 'tl', text: label }), x.short ? h('span', { class: 'ts', text: x.short, 'aria-hidden': 'true' }) : null);
      if (x.short) b.setAttribute('aria-label', label);
      b.addEventListener('click', e => run(e, b));
      return b;
    };
    // top bar
    const top = h('header', { class: 'rn-top', id: 'top' });
    const exitB = h('button', { type: 'button', class: 'rn-exit', id: 'exit', 'aria-label': exam ? 'Save and exit' : 'Exit', title: exam ? 'Save and exit' : 'Exit' },
      icon('x', 20), h('span', { class: 'rn-exit-l', text: exam ? 'Save and exit' : 'Exit' }));
    exitB.addEventListener('click', () => exit());
    const titleEl = h('span', { class: 'rn-title', id: 'title', text: o.title || '' });
    const dirsB = cfg.dirs ? h('button', { type: 'button', class: 'quiet rn-dirs', id: 'dirs', 'aria-haspopup': 'dialog', onclick: () => directions() }, 'Directions', icon('down', 16)) : null;
    const condChip = exam && o.conditions ? h('span', { class: 'rn-cond', text: training ? 'Training' : 'Ranked',
      title: training ? 'Training: the aids are on. This sitting keeps its score and doesn’t rank.' : 'Test-day: exactly Bluebook. This sitting ranks.' }) : null;
    top.append(h('div', { class: 'rn-left' }, exitB, h('div', { class: 'rn-titles' }, titleEl, dirsB), condChip));
    const clockBox = h('div', { class: 'rn-clock', id: 'clock' });
    const pauseB = cfg.pause && o.clock ? tool('pause', 'Pause', 'pause', 'P', () => pause(), { id: 'pause' }) : null;
    top.append(h('div', { class: 'rn-mid' }, clockBox, pauseB));
    const toolsTop = h('div', { class: 'rn-tools', id: 'tools', role: 'toolbar', 'aria-label': 'Tools' });
    top.append(toolsTop);
    const annB = cfg.annotate ? tool('annotate', exam ? 'Highlights & Notes' : 'Highlight', 'marker', 'L', () => toggleAnnotate(), { id: 'toolAnnotate', toggle: true, short: exam ? 'Notes' : null }) : null;
    const scrB = cfg.scratch ? tool('scratch', 'Scratch', 'pen', 'Shift+L', () => toggleScratch(), { id: 'toolScratch', toggle: true }) : null;
    const calcB = cfg.calc ? tool('calc', 'Calculator', 'calc', 'G', () => toggleCalc(), { id: 'toolCalc', toggle: true, cls: 'rn-t-calc' }) : null;
    const refB = cfg.ref ? tool('ref', 'Reference', 'ref', 'F', () => toggleRef(), { id: 'toolRef', toggle: true, cls: 'rn-t-ref' }) : null;
    const notesB = tool('notes', 'Notes', 'note', null, () => openSlot('notes'), { id: 'toolNotes', cls: 'rn-t-notes' });
    notesB.hidden = true;
    const moreB = tool('more', 'More', 'more', null, () => more(), { id: 'toolMore' });
    moreB.setAttribute('aria-haspopup', 'menu');
    if (exam) toolsTop.append(...[annB, scrB, notesB, calcB, refB, moreB].filter(Boolean));
    else toolsTop.append(...[scrB, calcB, refB, notesB, moreB].filter(Boolean));

    // progress rail (practice) / strip (exam)
    const rail = h('div', { class: 'rn-rail', id: 'strip' });
    const segs = h('div', { class: 'rn-segs', role: exam ? 'progressbar' : 'group', 'aria-label': 'Progress', 'aria-valuemin': exam ? '0' : null });
    const railText = h('p', { class: 'rn-railtext' });
    rail.append(segs, railText);
    segs.addEventListener('click', e => {
      if (phone() && exam) return toggleNav();
      const b = e.target.closest('[data-i]');
      if (b && !b.disabled) pick(+b.dataset.i);
    });

    // the question strip (practice) / header (exam)
    const strip = h('div', { class: exam ? 'rn-qhead' : 'rn-qstrip' });
    const numEl = h('span', { class: exam ? 'rn-qn' : 'rn-num' });
    const infoEl = h('span', { class: 'rn-qinfo' });
    const qtools = h('div', { class: 'rn-qtools', role: 'toolbar', 'aria-label': 'Question tools' });
    const watchEl = h('span', { class: 'rn-watch', title: 'Time on this question', hidden: true });
    strip.append(h('div', { class: 'rn-qleft' }, numEl, infoEl, exam ? null : watchEl), qtools);
    const markB = tool('mark', 'Mark for review', 'flag', 'M', () => setMark(at), { id: 'markBtn', toggle: true, cls: 'rn-mark', short: 'Mark' });
    const elimB = tool('eliminate', 'Eliminate', 'eliminate', 'E', () => { if (ws) { ws.eliminate(); paintQ(); } }, { id: 'elimBtn', toggle: true });
    const noteB = !exam ? tool('note', 'My note', 'note', 'O', e => openNote(e && e.currentTarget), { id: 'noteBtn', short: 'Note' }) : null;
    const detB = !exam ? tool('details', 'Details', 'info', 'V', () => openDetails(), { id: 'detailsBtn' }) : null;
    const repB = tool('report', 'Report', 'report', 'R', () => report(), { id: 'reportBtn' });
    repB.setAttribute('aria-label', 'Report a problem with this question');
    const attB = !exam ? tool('history', 'Attempts', 'history', 'Y', () => history(), { id: 'attemptsBtn' }) : null;
    const saveB = exam ? tool('save', 'Save', 'bookmark', null, () => toggleSave(), { id: 'saveBtn', toggle: true }) : null;
    let confSeg = null;
    if (cfg.conf) {
      confSeg = h('div', { class: 'choices rn-conf', role: 'group', 'aria-label': 'How sure are you? (K)' });
      [['sure', 'Sure'], ['unsure', 'Unsure'], ['guess', 'Guess']].forEach(([v, lab]) => {
        const b = h('button', { type: 'button', 'data-v': v, 'aria-pressed': 'false', text: lab });
        b.addEventListener('click', () => setConf(at, (cells[at] || {}).conf === v ? null : v));
        confSeg.append(b);
      });
    }
    if (exam) qtools.append(...[markB, confSeg, saveB, h('span', { class: 'rn-spacer' }), elimB, repB].filter(Boolean));
    else qtools.append(...[markB, elimB, annB, noteB, detB, repB, attB].filter(Boolean));
    if (exam && annB) { /* Highlights & Notes sits in the top bar in the test */ }
    const whyEl = h('p', { class: 'rn-why', hidden: true });
    const nudgeEl = h('div', { class: 'rn-nudge', hidden: true, role: 'status' });
    const qHost = h('div', { class: 'rn-q' });
    const addNote = exam ? h('button', { type: 'button', class: 'quiet rn-addnote', onclick: e => openNote(e.currentTarget) }, icon('note', 16), h('span', { text: 'Add a note' })) : null;
    const scratchHost = h('div', { class: 'rn-scratchtools', hidden: true });
    const toolsRow = h('div', { class: 'tools-row rn-toolsrow', role: 'toolbar', 'aria-label': 'Tools', hidden: true });
    const screenEl = h('div', { class: 'rn-screen', hidden: true });
    const qArea = h('div', { class: 'rn-qarea' }, strip, whyEl, nudgeEl, scratchHost, qHost, addNote, toolsRow);
    const col = h('main', { class: 'rn-col', id: o.mainId || 'main', tabindex: '-1' }, rail, qArea, screenEl);
    const passage = h('section', { class: 'rn-passage', hidden: true, 'aria-label': 'Passage' });       // decision 3: kept empty until an R&W bank
    const dock = h('aside', { class: 'rn-dock', 'aria-label': 'Calculator', hidden: true });
    const dockGrip = h('div', { class: 'rn-dock-grip', role: 'separator', 'aria-orientation': 'vertical', 'aria-label': 'Resize the calculator', tabindex: '0' });
    dock.append(dockGrip);
    const slot = h('aside', { class: 'rn-slot', id: 'rightSlot', hidden: true, 'aria-label': 'Reference and notes' });
    const bodyEl = h('div', { class: 'rn-body' }, dock, passage, col, slot);
    // footer
    const foot = h('footer', { class: 'rn-foot', id: 'foot' });
    const backB = h('button', { type: 'button', class: 'quiet rn-back', id: 'back', title: 'Back (←)' }, icon('left', 18), h('span', { class: 'rn-back-l', text: exam ? 'Back' : 'Previous' }));
    backB.addEventListener('click', () => back());
    const markFoot = h('button', { type: 'button', class: 'rn-markfoot', id: 'markFoot', 'aria-pressed': 'false', 'aria-label': 'Mark for review', title: 'Mark for review (M)' }, icon('flag', 20), h('span', { class: 'tl', text: 'Mark' }));
    markFoot.addEventListener('click', () => setMark(at));
    const navB = h('button', { type: 'button', class: 'rn-navb', id: 'navBtn', 'aria-expanded': 'false', 'aria-controls': 'nav', 'aria-haspopup': 'dialog', title: 'Navigator (N)' });
    navB.addEventListener('click', () => toggleNav());
    const checkHost = h('div', { class: 'rn-check' });
    const nextB = h('button', { type: 'button', class: 'pill rn-next', id: 'next' });
    nextB.addEventListener('click', () => nextClick());
    const savedEl = h('span', { class: 'rn-saved', id: 'saved', 'aria-live': 'polite' });
    const whoEl = exam ? (o.who ? h('span', { class: 'rn-who', id: 'who', text: o.who }) : h('a', { class: 'quiet rn-who', id: 'who', href: '/me/', text: 'Set your name in Me' })) : null;
    const fLeft = h('div', { class: 'rn-fl' }), fMid = h('div', { class: 'rn-fm' }), fRight = h('div', { class: 'rn-fr' });
    if (exam) { fLeft.append(whoEl, savedEl); fMid.append(navB); fRight.append(backB, markFoot, nextB); }
    else { fLeft.append(backB, markFoot, savedEl); fMid.append(navB); fRight.append(checkHost, nextB); }
    const footAlt = h('div', { class: 'rn-falt', hidden: true });
    foot.append(fLeft, fMid, fRight, footAlt);
    root.append(live, top, bodyEl, foot);
    if (host) host.replaceChildren(root);
    doc.documentElement.classList.add('has-runner');
    cleanups.push(() => doc.documentElement.classList.remove('has-runner'));

    /* ---------------- the clock */
    if (o.clock) {
      const timed = Number.isFinite(o.clock.secondsLeft);
      timerApi = timer(clockBox, {
        secondsLeft: timed ? o.clock.secondsLeft : undefined, elapsed: timed ? undefined : (o.clock.elapsed || 0), paused: !!o.clock.paused,
        hideKey: exam ? `satf.clock.${sid}` : null, hidden: exam ? false : !!prefs.hide_timer, hideId: 'clockHide',
        label: exam && !timed ? 'Elapsed' : null, showLabel: exam ? 'Show time' : 'Show', unhide: exam,
        onHide: v => { if (!exam) emit('pref', 'hide_timer', v); },
        onWarn: (w, text) => say(text),
        onEnd: () => timeUp(),
      });
    } else clockBox.hidden = true;

    /* ---------------- layout: the calculator on the left, one slot on the right (X9) */
    let dockW = Math.max(320, Math.min(560, +ls.get('satf.calc.w', 420) || 420));
    function layout() {
      if (dead) return;
      const W = root.clientWidth || innerWidth;
      const docked = !!(UI.calc && UI.calc.isOpen && UI.calc.mode === 'dock' && dock.contains(UI.calc.el));
      const slotOn = !slot.hidden;
      dock.hidden = !docked;
      let cw = dockW;
      const colW = w => W - (docked ? w + G : 0) - (slotOn ? SLOT_W + G : 0) - 2 * G;
      slotFloat = false;
      if (colW(cw) < COL_MIN && docked) cw = Math.max(320, cw - (COL_MIN - colW(cw)));
      if (colW(cw) < COL_MIN) {
        if (slotOn && (lastOpened === 'slot' || !docked)) slotFloat = true;
        else if (docked && UI.calc.setMode) { UI.calc.setMode('float'); return layout(); }
      }
      root.style.setProperty('--dock-w', cw + 'px');
      slot.classList.toggle('float', slotOn && slotFloat);
      root.classList.toggle('has-dock', docked);
      root.classList.toggle('has-slot', slotOn && !slotFloat);
      if (calcB) calcB.setAttribute('aria-pressed', String(!!(UI.calc && UI.calc.isOpen)));
      if (refB) refB.setAttribute('aria-pressed', String(slotOn && slotTab === 'ref'));
    }
    if (UI.calc) {
      if (UI.calc.dock) UI.calc.dock(dock);
      if (UI.calc.sitting) UI.calc.sitting(sid);
      if (UI.calc.onOpen) cleanups.push(UI.calc.onOpen(open => { if (open) { lastOpened = 'calc'; calcOpenAt = calcOpenAt || performance.now(); } layout(); renderToolsRow(); }));
    }
    const onResize = () => { layout(); if (!slot.hidden && innerWidth < 1180) { const t = slotTab; closeSlot(); openSlot(t); } };
    addEventListener('resize', onResize);
    cleanups.push(() => removeEventListener('resize', onResize));
    // the dock's width: drag its right edge (320-560)
    (() => {
      let x0 = 0, w0 = 0, drag = false;
      dockGrip.addEventListener('pointerdown', e => { drag = true; x0 = e.clientX; w0 = dock.getBoundingClientRect().width; dockGrip.setPointerCapture(e.pointerId); e.preventDefault(); });
      dockGrip.addEventListener('pointermove', e => { if (!drag) return; dockW = Math.max(320, Math.min(560, w0 + e.clientX - x0)); layout(); });
      const stop = () => { if (!drag) return; drag = false; ls.set('satf.calc.w', Math.round(dockW)); if (UI.calc && UI.calc.desmos) try { UI.calc.desmos.resize(); } catch (_) {} };
      dockGrip.addEventListener('pointerup', stop);
      dockGrip.addEventListener('pointercancel', stop);
      dockGrip.addEventListener('keydown', e => { const d = { ArrowLeft: -20, ArrowRight: 20 }[e.key]; if (!d) return; e.preventDefault(); dockW = Math.max(320, Math.min(560, dockW + d)); ls.set('satf.calc.w', dockW); layout(); });
    })();

    /* ---------------- the right slot: Reference · Notes · Entering your answer */
    const slotHead = h('div', { class: 'rn-slot-head' });
    const slotTabs = h('div', { class: 'rn-slot-tabs', role: 'tablist', 'aria-label': 'Side panel' });
    const slotBody = h('div', { class: 'rn-slot-body', role: 'tabpanel' });
    slotHead.append(slotTabs, h('button', { type: 'button', class: 'x', 'aria-label': 'Close the panel', onclick: () => closeSlot(true) }, icon('x', 18)));
    slot.append(slotHead, slotBody);
    const TABS = () => [['ref', 'Reference'], ['notes', 'Notes'], ...(isMc() ? [] : [['spr', 'Entering your answer']])].filter(([id]) => id !== 'ref' || cfg.ref);
    function openSlot(tab, o2 = {}) {
      if (innerWidth < 1180 || phone()) return sheetFor(tab, o2);
      slotTab = tab;
      lastOpened = 'slot';
      slot.hidden = false;
      paintSlot(o2);
      layout();
      if (tab === 'ref') countRef();
    }
    function closeSlot(byUser) {
      if (byUser && slotTab === 'spr') ls.set('satf.sprhelp', 'closed');
      slot.hidden = true;
      if (slotTab === 'ref') stopRef();
      slotTab = null;
      layout();
    }
    function paintSlot(o2 = {}) {
      slotTabs.replaceChildren(...TABS().map(([id, label]) => {
        const b = h('button', { type: 'button', role: 'tab', 'aria-selected': String(slotTab === id), text: label === 'Notes' ? `Notes ${noteCount() || ''}`.trim() : label });
        b.addEventListener('click', () => { if (slotTab === 'ref' && id !== 'ref') stopRef(); slotTab = id; paintSlot(); if (id === 'ref') countRef(); });
        return b;
      }));
      slotBody.replaceChildren();
      if (slotTab === 'ref') { refApi = refDock(slotBody, { highlight: o2.highlight }); }
      else if (slotTab === 'notes') slotBody.append(notesList(true));
      else if (slotTab === 'spr' && UI.spr && UI.spr.directions) slotBody.append(UI.spr.directions());
    }
    function sheetFor(tab, o2 = {}) {
      if (tab === 'ref') { countRef(); const r = refSheet(o2.highlight); if (r && r.sheet) r.sheet.closed.then(stopRef); return r; }
      if (!UI.sheet) return null;
      if (tab === 'notes') return UI.sheet({ title: 'Notes', size: 'm', body: b => { b.append(notesList(false)); } });
      if (tab === 'spr' && UI.spr) return UI.sheet({ title: 'Entering your answer', size: 'm', body: b => { b.append(UI.spr.directions()); } });
      return null;
    }
    // X9: the runner counts each question's reference opens and time
    let refAt = null;
    function countRef() { if (at < 0) return; refAt = { i: at, t: performance.now() }; saveState(at, { ref_n: 1 }); }
    function stopRef() { if (!refAt) return; saveState(refAt.i, { ref_ms: Math.round(performance.now() - refAt.t) }); refAt = null; }
    function toggleRef(o2 = {}) {
      if (!cfg.ref) return false;
      if (!slot.hidden && slotTab === 'ref' && !o2.highlight) { closeSlot(); return; }
      openSlot('ref', o2);
    }

    /* ---------------- notes: My note, and every note in the sitting */
    const noteOf = i => { const it = items.get(i); return it ? String(it.note || '') : ''; };
    const hasNote = i => { const it = items.get(i); return !!(it && ((it.note && it.note.trim()) || (it.marks || []).some(m => m.note))); };
    const noteCount = () => [...items.keys()].filter(hasNote).length;
    function notesList(inSlot) {
      const box = h('div', { class: 'rn-notes' });
      if (at >= 0 && view === 'q') box.append(noteEditor(at, inSlot));
      const rows = [...items.keys()].sort((a, b) => a - b).filter(i => hasNote(i) || (items.get(i).marks || []).some(m => m.style === 'ask'));
      if (!rows.length) box.append(h('p', { class: 'meta', text: 'Notes you add, and the text you mark “Asked for”, show here by question.' }));
      rows.forEach(i => {
        const it = items.get(i);
        const bits = [];
        if (it.note) bits.push(h('p', { class: 'rn-note-t', text: it.note }));
        (it.marks || []).forEach(m => {
          const text = markText(i, m);
          if (m.style === 'ask' && text) bits.push(h('p', { class: 'rn-note-ask' }, h('b', { text: 'Asked for: ' }), text));
          if (m.note) bits.push(h('p', { class: 'rn-note-t' }, text ? h('span', { class: 'rn-note-q', text: `“${text.slice(0, 60)}” ` }) : null, m.note));
        });
        const b = h('button', { type: 'button', class: 'rn-note-row' }, h('span', { class: 'rn-note-n', text: `Q${(cells[i] || {}).n ?? i + 1}` }), h('div', {}, bits));
        b.addEventListener('click', () => { if (i !== at) go(i, 'note'); });
        box.append(b);
      });
      return box;
    }
    function markText(i, m) {
      if (i !== at || !ws) return m.text || '';
      const el = [...ws.el.querySelectorAll('[data-addr]')].find(e => e.dataset.addr === m.addr);
      if (!el) return '';
      return m.start === 0 && m.end === 0 ? el.textContent.trim() : el.textContent.slice(m.start, m.end).trim();
    }
    function noteEditor(i, inSlot) {
      const id = uid('note');
      const ta = h('textarea', { id, class: 'field rn-note-ta', rows: '3', maxlength: String(cfg.noteMax), 'aria-label': `My note for question ${(cells[i] || {}).n ?? i + 1}` });
      ta.value = noteOf(i);
      const st = h('span', { class: 'meta rn-note-st', 'aria-live': 'polite' });
      const cnt = UI.counter ? UI.counter(ta, cfg.noteMax) : null;
      const saveNote = async () => {
        const v = ta.value.trim().slice(0, cfg.noteMax);
        const it = items.get(i);
        if (!it || v === String(it.note || '')) return;
        it.note = v;
        cells[i].note = hasNote(i);
        st.textContent = 'Saving…';
        try { await emit('note', i, v); st.textContent = 'Saved'; } catch (_) { st.textContent = 'Not saved. Try again.'; }
        paintRail(); paintQ(); if (navApi) navApi.update(cells, at);
      };
      ta.addEventListener('blur', saveNote);
      ta.addEventListener('keydown', e => { if (e.key === 'Escape' && inSlot) { e.stopPropagation(); ta.blur(); } });
      if (inSlot) setTimeout(() => ta.focus({ preventScroll: true }), 0);
      return h('div', { class: 'rn-note-ed' }, h('label', { class: 'k', for: id, text: `My note · Q${(cells[i] || {}).n ?? i + 1}` }), ta, h('div', { class: 'rn-note-foot' }, cnt, st));
    }
    function openNote(anchor) {
      if (view !== 'q' || at < 0) return false;
      if (exam && innerWidth >= 1180) return openSlot('notes');
      if (!UI.pop) return false;
      const box = h('div', { class: 'rn-notepop' }, noteEditor(at, false));
      const p = UI.pop(anchor || noteB || addNote || navB, box, { label: 'My note', className: 'rn-notepop-p' });
      if (p) setTimeout(() => { const t = p.el.querySelector('textarea'); if (t) t.focus({ preventScroll: true }); }, 0);
      return p;
    }

    /* ---------------- the question on screen */
    function wsOpts(i, it) {
      const base = o.workspace || {};
      const call = (name, ...a) => (typeof base[name] === 'function' ? base[name](...a) : undefined);
      return Object.assign({}, base, {
        mode: exam ? 'exam' : 'practice', feedback: fbMode, prefs, bar: false, toolbar: false, head: false,
        confActive: o.confActive, state: it.state || null, fb: it.fb || null, calc: cfg.calc, ref: cfg.ref,
        firstTap: !!prefs.first_tap,
        onCheck: async (a, meta) => {
          meta.ms = Math.round(msAt(i));
          if (Number.isFinite(timerApi && timerApi.left)) meta.made_left = Math.round(timerApi.left);
          return emit('check', i, a, meta);
        },
        onSelect: a => { selected(i, a); call('onSelect', a); },
        onEnter: () => { call('onEnter'); next(); },
        onStrike: (k, v, by) => {
          const s = ws && ws.state ? ws.state() : { struck: [] };
          emit('strike', i, k, v, by, s.struck);
          saveState(i, { struck: s.struck });
          call('onStrike', k, v, by);
        },
        onSkip: !challenge && on.skip ? (id, meta) => skip(i, meta) : null,
        onReveal: fb => { revealed(i, fb); call('onReveal', fb); },
        onChange: s => { changed(i, s); call('onChange', s); },
        annotating: () => annotateOn || scratchOn,
        actions: exam ? null : actionsCtx(i, it),
      });
    }
    function actionsCtx(i, it) {
      if (!o.actions) return null;
      const a = o.actions;
      const onA = Object.assign({}, a.on || {});
      if (on.mark) onA.mark = v => setMark(i, v);
      if (on.note) onA.note = () => openNote(noteB);
      if (on.report || UI.report) onA.report = () => report();
      if (on.history) onA.history = () => history();
      return Object.assign({ surface: 'runner', session: sid, inSitting: true, marked: !!(cells[i] || {}).flag, saved: !!it.saved, hasNote: hasNote(i) }, a, { on: onA });
    }
    function mountWs(i, it, detached) {
      const w = UI.workspace(detached ? null : qHost, it.q, wsOpts(i, it));
      return w;
    }
    function destroyWs() {
      if (ann) { ann.destroy(); ann = null; }
      if (scr) { scr.destroy(); scr = null; }
      if (ws) { try { ws.destroy(); } catch (_) {} ws = null; wsI = -1; }
    }
    function show(i, it, p) {
      if (dead) return;
      destroyWs();
      at = i;
      view = 'q';
      items.set(i, it);
      if (!cells[i]) cells[i] = { n: i + 1, status: 'unanswered' };
      if (cells[i].status === 'future') cells[i].status = 'unanswered';
      cells.forEach((c, k) => { c.current = k === i; });
      if (p && p.ws) { ws = p.ws; qHost.replaceChildren(ws.el); if (ws.restart) ws.restart(); }
      else ws = mountWs(i, it);
      pre.delete(i);
      wsI = i;
      screenEl.hidden = true; screenEl.replaceChildren();
      qArea.hidden = false; rail.hidden = false;
      footAlt.hidden = true; footAlt.replaceChildren();
      [fLeft, fMid, fRight].forEach(x => { x.hidden = false; });
      // highlights and notes, restored
      if (cfg.annotate) ann = annotate(ws.el, it.marks || [], { editable: annotateOn, onChange: m => {
        it.marks = m;
        cells[i].note = hasNote(i);
        emit('marks', i, m);
        saveState(i, { marks: m });
        paintRail(); refreshNotes();
      } });
      if (it.scratch || scratchOn) mountScratch(i, it);
      visStart = doc.hidden ? null : performance.now();
      calcBase = UI.calc && UI.calc.exprs ? UI.calc.exprs().slice() : null;
      calcOpenAt = UI.calc && UI.calc.isOpen ? performance.now() : null;
      sunkShown = false;
      nudge(null);
      ls.set(`satf.pos.${sid}`, i);
      paintQ(); paintRail(); syncFoot(); renderToolsRow(); sprHelp();
      if (navApi) navApi.update(cells, at);
      if (!slot.hidden) paintSlot();
      col.scrollTop = 0;
      if (!p || p.scroll !== false) window.scrollTo({ top: 0, behavior: 'auto' });
      const f = doc.activeElement;
      if (!f || f === doc.body || !f.isConnected || f.closest('[hidden]')) col.focus({ preventScroll: true });
      emit('show', i, it);
      emit('view', 'q', i);
    }
    function sprHelp() {
      if (!exam || isMc() || !ws) return;
      if (innerWidth >= 1180) {
        if (ls.get('satf.sprhelp', 'open') !== 'closed' && (slot.hidden || slotTab !== 'spr') && slot.hidden) openSlot('spr');
        return;
      }
      // narrower: a disclosure under the field, open until the student closes it
      const box = ws.el.querySelector('.spr');
      if (!box || box.querySelector('.rn-sprhelp') || !UI.spr || !UI.spr.directions) return;
      const d = h('details', { class: 'rn-sprhelp', open: ls.get('satf.sprhelp', 'open') !== 'closed' ? true : null },
        h('summary', { text: 'How to enter your answer' }), UI.spr.directions());
      d.addEventListener('toggle', () => ls.set('satf.sprhelp', d.open ? 'open' : 'closed'));
      box.append(d);
    }

    /* ---------------- painting */
    function paintQ() {
      if (at < 0) return;
      const it = items.get(at) || {};
      const qq = it.q || {};
      const c = cells[at] || {};
      const answered = !!(ws && ws.answered && ws.answered());
      numEl.textContent = exam ? `Q${c.n ?? at + 1}` : String(c.n ?? at + 1);
      if (!exam) {
        infoEl.replaceChildren();
        const t = UI.TOPIC && UI.TOPIC[qq.topic];
        const hideSkill = o.hideSkill && !answered;
        const skill = h('span', { class: 'rn-skill' }, !hideSkill ? glyphOf(qq.topic) : null, h('span', { class: 'rn-skill-n', text: hideSkill ? (typeof o.hideSkill === 'string' ? o.hideSkill : 'Mixed') : (t ? t.short : qq.topic_name || '') }));
        infoEl.append(skill);
        if (qq.name && !hideSkill) infoEl.append(h('span', { class: 'rn-type', text: qq.name }));
        if (qq.difficulty) infoEl.append(h('span', { class: 'rn-diff' }, UI.dbars ? UI.dbars(qq.difficulty) : h('span', { text: qq.difficulty }), qq.level ? h('span', { class: 'rn-level', text: `L${qq.level}` }) : null));
        if (qq.type === 'spr') infoEl.append(h('span', { class: 'rn-fmt', text: 'Grid-in' }));
        if (qq.repair) {
          const ag = h('span', { class: 'rn-again', text: 'Again', tabindex: '0' });
          if (UI.tooltip) UI.tooltip(ag, qq.repair_of ? `Same trap as question ${qq.repair_of}, new numbers` : 'Same trap, new numbers');
          infoEl.append(ag);
        }
      }
      // tools
      const s = ws && ws.state ? ws.state() : {};
      const flag = !!c.flag;
      [markB, markFoot].forEach(b => { if (!b) return; b.setAttribute('aria-pressed', String(flag)); b.classList.toggle('on', flag); });
      markB.querySelector('.tl').textContent = flag ? 'Marked' : 'Mark for review';
      markB.querySelector('.ts').textContent = flag ? 'Marked' : 'Mark';
      markB.setAttribute('aria-label', flag ? 'Marked for review' : 'Mark for review');
      markB.disabled = challenge && !answered;
      if (challenge && !answered) markB.title = 'Mark it after you answer';
      elimB.hidden = !isMc() || (answered && !exam);
      elimB.setAttribute('aria-pressed', String(!!s.eliminate));
      if (annB) annB.setAttribute('aria-pressed', String(annotateOn));
      if (scrB) scrB.setAttribute('aria-pressed', String(scratchOn));
      if (noteB) noteB.classList.toggle('has', hasNote(at));
      if (addNote) addNote.querySelector('span').textContent = noteOf(at) ? 'Edit your note' : 'Add a note';
      if (saveB) { saveB.setAttribute('aria-pressed', String(!!it.saved)); saveB.querySelector('.tl').textContent = it.saved ? 'Saved' : 'Save'; }
      if (confSeg) confSeg.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(c.conf === b.dataset.v)));
      if (attB) {
        const n = +it.attempts || 0;
        attB.hidden = !(answered || n > 0 || (s.tries && s.tries.length));
        attB.querySelector('.tl').textContent = n ? `Attempts ${n}` : 'Attempts';
      }
      notesB.hidden = !(annotateOn || noteCount());
      notesB.querySelector('.tl').textContent = noteCount() ? `Notes ${noteCount()}` : 'Notes';
      // why this one; a revisit says what it was
      if (!exam) {
        whyEl.replaceChildren();
        const fb = it.fb;
        const bits = [];
        if (answered && fb && it.revisit) bits.push(`Answered · ${stateLabel(statusOf(fb, qq))} · ${msx(msAt(at))}`);
        else if (!challenge && (it.why || qq.why)) bits.push(it.why || qq.why);
        whyEl.textContent = bits.join(' · ');
        whyEl.hidden = !bits.length;
      }
      paintWatch();
    }
    function paintWatch() {
      if (exam || !ws) { watchEl.hidden = true; return; }
      watchEl.hidden = prefs.show_stopwatch === false;
      const ms = msAt(at);
      const budget = +((items.get(at) || {}).q || {}).budget_ms || +(cells[at] || {}).budget_ms || 0;
      const over = budget && ms > budget && !ws.answered();
      watchEl.classList.toggle('over', !!(over && prefs.pace_alert !== false));
      watchEl.replaceChildren(h('span', { class: 'rn-watch-t', text: budget ? `${msx(ms)} / ${msx(budget)}` : msx(ms) }));
      if (budget) watchEl.append(h('span', { class: 'rn-watch-bar', 'aria-hidden': 'true' }, h('i', { style: `width:${Math.min(100, ms / budget * 100).toFixed(1)}%` })));
      watchEl.setAttribute('aria-label', `Time on this question ${msx(ms)}${budget ? ', budget ' + msx(budget) : ''}`);
      // P16: past 1.5 times the budget in a timed set, offer the second pass
      const skipChip = qArea.querySelector('.rn-skipchip');
      const want = !challenge && on.skip && timerApi && timerApi.timed && prefs.two_passes !== false && budget && ms > 1.5 * budget && !ws.answered();
      if (want && !skipChip) whyEl.after(h('button', { type: 'button', class: 'btn sm rn-skipchip', onclick: () => ws && ws.skip() }, 'Skip for now? ', h('kbd', { class: 'kbd', text: 'S' })));
      if (!want && skipChip) skipChip.remove();
    }
    function paintRail() {
      const t = tally(cells);
      const n = total === null ? null : total;
      const fixed = n !== null && n <= 60;
      segs.replaceChildren();
      segs.classList.toggle('bar', !fixed);
      if (fixed) {
        for (let i = 0; i < n; i++) {
          const c = cells[i] || { status: 'future' };
          const st = exam ? (c.status === 'answered' ? 'answered' : 'unanswered') : c.status;
          const b = h('button', { type: 'button', class: 'rn-seg', 'data-i': i, 'data-status': st, 'data-flag': c.flag ? '' : null, 'data-queued': queue && queue.list.includes(i) ? '' : null,
            'aria-current': i === at && view === 'q' ? 'true' : null, tabindex: '-1', disabled: c.status === 'future' && i !== t.served ? true : null,
            'aria-label': cellLabel(c, i, exam) });
          if (!phone() && UI.tooltip && !coarse()) UI.tooltip(b, cellLabel(c, i, exam).replace(/^Question (\d+), /, 'Question $1 · ').replace(/, /g, ' · '));
          segs.append(b);
        }
        const cur = segs.querySelector('[aria-current="true"]') || segs.querySelector('.rn-seg:not(:disabled)');
        if (cur) cur.tabIndex = 0;
      } else {
        const done = total === null ? t.answered : t.answered;
        const of = total === null ? Math.max(t.served, 1) : total;
        segs.append(h('span', { class: 'rn-fill', style: `width:${Math.min(100, done / of * 100).toFixed(1)}%` }));
      }
      if (cfg.pace && timerApi) paceTicks();
      if (exam) {
        segs.setAttribute('aria-valuenow', String(t.answered));
        segs.setAttribute('aria-valuemax', String(n ?? t.served));
        segs.setAttribute('aria-valuetext', `${t.answered} of ${n ?? t.served} answered`);
        railText.textContent = '';
        railText.hidden = true;
      } else {
        let streak = 0;
        for (let i = Math.max(at, t.served - 1); i >= 0; i--) { const s = (cells[i] || {}).status; if (s === 'correct' || s === 'repaired') streak++; else if (s === 'incorrect' || s === 'mixed') break; }
        const bits = [];
        if (phone() || !o.title) bits.push(o.title || '');
        if (total === null) bits.push(`${t.answered} answered`, `${t.right} right`);
        else if (endMode) bits.push(`${Math.min(at + 1, n)} of ${n}`, `${t.answered} answered`);
        else bits.push(`${Math.min(at + 1, n)} of ${n}`, `${t.right} right`);
        if (t.skipped) bits.push(`${t.skipped} skipped`);
        if (!endMode && streak >= 2) bits.push(`${streak} in a row`);
        railText.textContent = bits.filter(Boolean).join(' · ');
        railText.hidden = false;
      }
    }
    // X3: the tick at the question you should be on, and checkpoints after Q7 and Q14
    function paceTicks() {
      const b = o.pace.budget_s, n = b.length;
      const dur = b.reduce((a, x) => a + x, 0) + (o.pace.reserve_s || 0);
      const left = timerApi.left;
      if (!Number.isFinite(left)) return;
      const el = Math.max(0, (o.pace.duration_s || dur) - left);
      let cum = 0, pos = n;
      for (let i = 0; i < n; i++) { cum += b[i]; if (cum > el) { pos = i; break; } }
      const tick = h('i', { class: 'rn-tick', style: `--at:${pos}`, 'aria-hidden': 'true', title: `Pace: question ${pos + 1}` });
      segs.append(tick);
      [7, 14].forEach(k => {
        if (k >= n) return;
        const by = b.slice(0, k).reduce((a, x) => a + x, 0);
        const leftBy = (o.pace.duration_s || dur) - by;
        segs.append(h('i', { class: 'rn-tick cp', style: `--at:${k}`, title: `By Q${k + 1}: ${mmss(leftBy)} left`, 'aria-hidden': 'true' }));
      });
    }
    function syncFoot() {
      if (view !== 'q' || at < 0) return;
      const c = cells[at] || {};
      const answered = !!(ws && ws.answered && ws.answered());
      const s = ws && ws.state ? ws.state() : {};
      backB.disabled = queue ? queue.k <= 0 : at <= 0;
      nextB.disabled = false;
      const n = c.n ?? at + 1;
      const label = queue ? `Going through · ${queue.k + 1} of ${queue.list.length} · Q${n}`
        : exam ? (phone() ? `${o.short || 'M1'} · ${n} of ${total}` : `Question ${n} of ${total}`)
        : total === null ? `Question ${n} · endless` : phone() ? `${n} / ${total}` : `Question ${n} of ${total}`;
      navB.replaceChildren(h('span', { class: 'rn-navl', text: label }), icon('up', 16));
      navB.setAttribute('aria-label', `${label}. Open the navigator`);
      if (exam) {
        nextB.replaceChildren(h('span', { text: queue ? (queue.k >= queue.list.length - 1 ? 'Done' : 'Next') : last() ? 'Review' : 'Next' }), icon('right', 18));
        nextB.hidden = false;
        return;
      }
      if (!splitCtl && UI.splitCheck) {
        splitCtl = UI.splitCheck(checkHost, { confidence: challenge ? prefs.confidence : prefs.confidence, active: o.confActive, save: endMode, onSubmit: conf => submit(conf) });
      }
      const saving = endMode;
      const skipped = c.status === 'skipped';
      const showCheck = !answered && (!saving || true);
      checkHost.hidden = !showCheck;
      if (splitCtl) splitCtl.set({ enabled: !!(ws && ws.canCheck && ws.canCheck()), firstTry: !(s.tries && s.tries.length), save: saving });
      checkHost.classList.toggle('split', !!(splitCtl && splitCtl.el.classList.contains('split')));
      // Next: after the verdict; in end mode alongside Save & next; a skipped question may move on
      const nextLabel = saving ? (last() ? 'Review & finish' : 'Next') : last() ? 'Finish' : 'Next';
      nextB.replaceChildren(h('span', { text: nextLabel }), icon('right', 18), h('kbd', { class: 'kbd rn-enter', text: 'Enter' }));
      nextB.hidden = !(answered || saving || skipped);
      nextB.classList.toggle('quiet', saving && !answered);
      nextB.classList.toggle('pill', !(saving && !answered));
      root.classList.toggle('rn-answered', answered);
    }
    function renderToolsRow() {
      if (!ws || !ws.tools) { toolsRow.hidden = true; return; }
      const list = ws.tools().filter(t => t.id !== 'eliminate');
      toolsRow.replaceChildren(...list.map(t => {
        const b = h('button', { type: 'button', class: 'tool', 'data-tool': t.id, 'aria-pressed': t.pressed === undefined ? null : String(!!t.pressed), title: t.key ? `${t.label} (${t.key})` : t.label },
          icon(t.icon, 20), h('span', { text: t.label }));
        b.addEventListener('click', () => {
          if (t.id === 'ref') toggleRef(); else if (t.id === 'calc') toggleCalc(); else t.run();
          renderToolsRow();
        });
        return b;
      }));
      toolsRow.hidden = !list.length;
    }

    /* ---------------- answering */
    function selected(i, a) {
      const it = items.get(i);
      if (!it) return;
      it.state = Object.assign({}, it.state || {}, ws && ws.state ? ws.state() : {});
      if (exam) {
        cells[i].status = a === null || a === undefined ? 'unanswered' : 'answered';
        paintRail();
        if (navApi) navApi.update(cells, at);
        if (cyw) cyw.update(cells);
      }
      const meta = { ms: Math.round(msAt(i)) };
      if (timerApi && Number.isFinite(timerApi.left)) meta.made_left = Math.round(timerApi.left);
      emit('select', i, a, meta);
      if (exam && a !== null && a !== undefined) say('Answer saved');
    }
    function changed(i, s) {
      const it = items.get(i);
      if (it) it.state = s;
      if (endMode && cells[i]) {
        const saved = s.saved !== null && s.saved !== undefined && s.saved !== '';
        const was = cells[i].status;
        if (saved && was !== 'answered') { cells[i].status = 'answered'; paintRail(); }
      }
      if (i === at) { syncFoot(); paintQ(); renderToolsRow(); }
    }
    function revealed(i, fb) {
      const it = items.get(i);
      if (!it) return;
      it.fb = fb;
      const st = statusOf(fb, it.q);
      if (cells[i]) { cells[i].status = st; if (fb.conf) cells[i].conf = fb.conf; if (fb.trap || fb.mistake) cells[i].trap = fb.trap || fb.mistake; }
      if (fb.unmarked && cells[i]) cells[i].flag = false;
      if (ann) ann.render();
      if (i === at) {
        paintQ(); paintRail(); syncFoot(); renderToolsRow();
        if (!coarse()) setTimeout(() => { if (!nextB.hidden && at === i) nextB.focus({ preventScroll: true }); }, 0);
      }
      if (navApi) navApi.update(cells, at);
      emit('reveal', i, fb);
      paceDelta();
    }
    async function submit(conf) {
      if (!ws || view !== 'q') return;
      const i = at;
      const ok = await ws.check(conf);
      if (endMode && ok && at === i && !dead) {
        cells[i].status = 'answered';
        paintRail();
        if (last()) finish(); else go(i + 1, 'next');
      }
    }
    function skip(i, meta) {
      if (!cells[i] || (ws && ws.answered())) return;
      cells[i].status = 'skipped';
      emit('skip', i, Object.assign({}, meta, { ms: Math.round(msAt(i)) }));
      paintRail();
      if (last()) finish(); else go(i + 1, 'skip');
    }
    function saveState(i, patch) { if (i >= 0 && patch && Object.keys(patch).length) emit('state', i, patch); }

    /* ---------------- moving */
    let loadingAt = null;
    async function go(i, how) {
      if (dead || i < 0) return false;
      if (total !== null && i >= total) return false;
      if (view === 'paused') return false;
      const c = cells[i];
      if (c && c.status === 'future' && i > tally(cells).served) return false;
      leave(how);
      const p = pre.get(i);
      let it = p ? p.it : items.get(i);
      if (!it) {
        if (!on.load) return false;
        loadingAt = i;
        skeleton(i);
        try { it = await emit('load', i, how); }
        catch (e) { if (loadingAt === i) loadError(i, e); return false; }
        if (loadingAt !== i || dead) return false;
        loadingAt = null;
        if (!it) { loadError(i); return false; }
      }
      if (items.get(i) && items.get(i).fb) it.revisit = true;
      show(i, it, p);
      return true;
    }
    function skeleton(i) {
      destroyWs();
      at = i;
      view = 'loading';
      cells.forEach((c, k) => { c.current = k === i; });
      qHost.replaceChildren();
      const sk = h('div', { class: 'rn-skel', 'aria-busy': 'true', 'aria-label': 'Loading the question' });
      if (UI.skel) { UI.skel(sk, 'lines:3'); const opts = h('div', { class: 'rn-skel-opts' }); for (let k = 0; k < 4; k++) UI.skel(opts, { w: '100%', h: 56, r: 12 }); sk.append(opts); }
      qHost.append(sk);
      [nextB, backB].forEach(b => { b.disabled = true; });
      if (splitCtl) splitCtl.set({ enabled: false });
      paintRail();
    }
    function loadError(i, e) {
      view = 'error';
      qHost.replaceChildren(h('div', { class: 'card-err rn-err', role: 'alert' },
        h('p', { text: e && e.offline ? 'You’re offline. The question will load when you’re back.' : 'That question didn’t load.' }),
        h('button', { type: 'button', class: 'btn', text: 'Try again', onclick: () => go(i, 'retry') })));
      backB.disabled = false;
    }
    function leave(how) {
      if (at < 0 || view !== 'q') return;
      const i = at;
      if (visStart !== null) {
        const d = performance.now() - visStart;
        timeAt.set(i, (timeAt.get(i) || 0) + d);
        visStart = doc.hidden ? null : performance.now();
        if (cells[i]) cells[i].ms = Math.round(timeAt.get(i));
        if (d > 250) emit('time', i, Math.round(d), how || 'leave');
      }
      // X8: what was typed into the calculator on this question
      if (UI.calc && UI.calc.exprs && calcBase) {
        const now = UI.calc.exprs();
        const added = now.filter(x => !calcBase.includes(x)).slice(0, 20);
        if (added.length) saveState(i, { calc: { open_ms: calcOpenAt ? Math.round(performance.now() - calcOpenAt) : 0, exprs: added } });
        calcBase = now.slice();
      }
      if (refAt && refAt.i === i) { stopRef(); if (!slot.hidden && slotTab === 'ref') refAt = { i: -1, t: performance.now() }; }
      if (ws && ws.state && items.get(i)) items.get(i).state = ws.state();
    }
    const canForward = () => {
      if (!ws) return true;
      if (exam || endMode) return true;
      const c = cells[at] || {};
      return ws.answered() || c.status === 'skipped';
    };
    function nextClick() {
      if (!exam && !endMode && ws && !ws.answered() && ws.canCheck && ws.canCheck()) return submit('auto');
      next();
    }
    async function next() {
      if (view === 'review') return;
      if (queue) return queueMove(1);
      if (view === 'q' && !canForward()) return;
      if (last()) return finish();
      return go(at + 1, 'next');
    }
    function back() {
      if (view === 'review') return closeReview();
      if (queue) return queueMove(-1);
      if (at > 0) go(at - 1, 'back');
    }
    function pick(i) {
      if (navPop) { try { navPop.close(); } catch (_) {} navPop = null; }
      if (view === 'review') { reviewOff(); }
      queue = null;
      if (i === at && view === 'q') { paintRail(); syncFoot(); return; }
      go(i, 'jump');
    }
    function jumpNext(kind) {
      const n = cells.length;
      for (let k = 1; k <= n; k++) {
        const i = (at + k) % n;
        const c = cells[i];
        if (!c || c.status === 'future') continue;
        if (kind === 'unanswered' ? (c.status === 'unanswered' || c.status === 'skipped') : c.flag) { pick(i); return true; }
      }
      toast(kind === 'unanswered' ? 'No unanswered questions' : 'Nothing marked for review');
      return true;
    }
    // X5: one queue, Next through it, back to Check your work at the end
    function startQueue(list) {
      if (!list || !list.length) return;
      queue = { list: list.slice(), k: 0, start: tally(cells) };
      emit('queue', list);
      reviewOff();
      go(list[0], 'queue').then(() => { syncFoot(); paintRail(); });
    }
    function queueMove(d) {
      if (!queue) return;
      const k = queue.k + d;
      if (k < 0) return;
      if (k >= queue.list.length) {
        const a = tally(cells), s0 = queue.start;
        queue = null;
        openReview();
        toast(`Done: ${a.answered - s0.answered} answered, ${Math.max(0, s0.flag - a.flag)} unmarked`);
        return;
      }
      queue.k = k;
      go(queue.list[k], 'queue').then(() => { syncFoot(); paintRail(); });
    }
    function stopQueue() { queue = null; openReview(); }

    /* ---------------- the navigator */
    function toggleNav() {
      if (navPop) { try { navPop.close(); } catch (_) {} navPop = null; return true; }
      if (!UI.pop) return false;
      const t = tally(cells);
      navApi = navPanel(null, cells, {
        mode: exam ? 'exam' : 'practice', end: endMode, current: at, confidence: cfg.conf, pace_ms: 95000,
        title: exam ? o.title || 'Questions' : 'Question overview',
        views: exam ? (training ? ['status', 'time'] : ['status']) : ['status', 'difficulty', 'skill', 'time', 'confidence', 'traps'],
        onPick: i => pick(i),
        onFinish: exam ? null : () => { if (navPop) navPop.close(); finish(); },
        finishLabel: endMode ? 'Review & finish' : 'Finish set',
        onReview: () => { if (navPop) navPop.close(); openReview(); },
        onGo: exam ? l => { if (navPop) navPop.close(); startQueue(l); } : null,
        onTwins: on.twins ? l => { if (navPop) navPop.close(); emit('twins', l); } : null,
        onFix: on.fix ? (label, l) => { if (navPop) navPop.close(); emit('fix', label, l); } : null,
      });
      navApi.el.id = 'nav';
      navPop = UI.pop(navB, navApi.el, { label: exam ? 'Questions' : 'Question overview', className: 'rn-navpop', align: 'center', onClose: () => { navPop = null; navApi = null; } });
      if (navPop) setTimeout(() => navApi && navApi.focus(), 0);
      void t;
      return true;
    }
    // swipe up on the footer button opens it (X6)
    (() => {
      let y0 = null;
      navB.addEventListener('pointerdown', e => { if (e.pointerType === 'touch') y0 = e.clientY; });
      navB.addEventListener('pointerup', e => { if (y0 !== null && y0 - e.clientY > 40 && !navPop) { e.preventDefault(); toggleNav(); } y0 = null; });
    })();

    /* ---------------- Check your work */
    function finish() {
      if (exam) return openReview();
      const t = tally(cells);
      if (t.skipped || t.unanswered || t.flag || (total !== null && t.served < total && endMode)) return openReview();
      leave('finish');
      emit('finish');
    }
    function reviewOff() {
      if (view !== 'review') return;
      view = 'q';
      cyw = null;
      screenEl.hidden = true; screenEl.replaceChildren();
      qArea.hidden = false; rail.hidden = false;
      footAlt.hidden = true; footAlt.replaceChildren();
      [fLeft, fMid, fRight].forEach(x => { x.hidden = false; });
    }
    function openReview() {
      if (view === 'review') return;
      leave('review');
      if (navPop) { try { navPop.close(); } catch (_) {} navPop = null; }
      view = 'review';
      queue = null;
      const t = tally(cells);
      void t;
      const saving = o.queue ? o.queue.status : null;
      cyw = checkYourWork(null, cells, {
        id: 'review', mode: exam ? 'exam' : 'practice', end: endMode, meta: exam ? o.title : null,
        left: timerApi && Number.isFinite(timerApi.left) ? timerApi.left : null, timed: !!(timerApi && timerApi.timed),
        pace_ms: 95000, confidence: cfg.conf, training, saving, foot: true,
        value: training && o.odds ? i => { const c = cells[i]; const p = o.odds[(c || {}).qid || (items.get(i) || {}).q?.id]; const sec = (o.pace && o.pace.budget_s && o.pace.budget_s[i]) || 95; return p ? p / sec : 0; } : null,
        onPick: i => pick(i),
        onGo: exam || on.queue ? l => startQueue(l) : null,
        onBack: () => closeReview(),
        backLabel: at >= 0 ? `Back to question ${(cells[at] || {}).n ?? at + 1}` : 'Back to questions',
        onFinish: () => { leave('finish'); emit('finish'); },
        finishLabel: o.finishLabel || (exam ? 'Hand in' : 'Finish set'),
      });
      qArea.hidden = true;
      rail.hidden = true;
      screenEl.replaceChildren(cyw.el);
      screenEl.hidden = false;
      // its footer takes the runner's footer
      [fLeft, fMid, fRight].forEach(x => { x.hidden = true; });
      footAlt.replaceChildren(cyw.foot);
      footAlt.hidden = false;
      cyw.el.querySelector('.cyw-foot') && cyw.el.querySelector('.cyw-foot').remove();
      window.scrollTo({ top: 0 });
      const hd = cyw.el.querySelector('h1');
      if (hd) { hd.tabIndex = -1; hd.focus({ preventScroll: true }); }
      emit('view', 'review', at);
      // X5 pass 2 starts when the student first opens review
    }
    function closeReview(i) {
      if (view !== 'review') return;
      reviewOff();
      const to = Number.isInteger(i) ? i : at;
      if (to >= 0 && items.get(to)) { const it = items.get(to); show(to, it); }
      else if (to >= 0) go(to, 'back');
    }

    /* ---------------- tools */
    function toggleAnnotate() {
      if (!cfg.annotate) return false;
      annotateOn = !annotateOn;
      if (annotateOn && scratchOn) toggleScratch();
      if (ann) ann.editable = annotateOn;
      root.classList.toggle('annotating', annotateOn);
      paintQ();
      say(annotateOn ? 'Highlights and notes on: select text to mark it' : 'Highlights and notes off');
      return true;
    }
    function mountScratch(i, it) {
      if (scr) scr.destroy();
      scr = scratch(qArea, { data: it.scratch, editable: scratchOn, onChange: d => { it.scratch = d; emit('scratch', i, d); saveState(i, { scratch: d }); }, onDone: () => { if (scratchOn) toggleScratch(); } });
      scratchHost.replaceChildren(scr.bar);
      scratchHost.hidden = !scratchOn;
      const opts = ws && ws.el.querySelector('.opts-wrap, .spr');
      if (scratchOn && opts) opts.after(scr.typed); else if (scratchOn) qHost.append(scr.typed);
    }
    function toggleScratch() {
      if (!cfg.scratch) return false;
      scratchOn = !scratchOn;
      if (scratchOn && annotateOn) toggleAnnotate();
      const it = items.get(at);
      if (scratchOn && it && !scr) mountScratch(at, it);
      if (scr) {
        scr.editable = scratchOn;
        scratchHost.hidden = !scratchOn;
        if (scratchOn) { const opts = ws && ws.el.querySelector('.opts-wrap, .spr'); if (opts) opts.after(scr.typed); } else scr.typed.remove();
      }
      root.classList.toggle('scratching', scratchOn);
      paintQ();
      return true;
    }
    function toggleCalc() {
      if (!cfg.calc || !UI.calc) return false;
      if (UI.calc.isOpen) UI.calc.close();
      else UI.calc.open({ mode: prefs.calc_mode === 'float' ? 'float' : undefined });
      return true;
    }
    async function setMark(i, v) {
      if (i < 0 || !cells[i]) return false;
      if (challenge && !(ws && ws.answered())) { toast('In the daily challenge, mark a question after you answer it.'); return true; }
      const c = cells[i];
      const was = !!c.flag;
      c.flag = v === undefined ? !was : !!v;
      if (c.flag === was) return true;
      paintQ(); paintRail();
      if (navApi) navApi.update(cells, at);
      if (cyw) cyw.update(cells);
      say(c.flag ? 'Marked for review' : 'Unmarked');
      try { await emit('mark', i, c.flag); }
      catch (_) { c.flag = was; paintQ(); paintRail(); toast('Not saved. Try again.'); }
      return true;
    }
    async function toggleSave() {
      const it = items.get(at);
      if (!it) return;
      const was = !!it.saved;
      it.saved = !was;
      paintQ();
      try { await emit('save', at, it.saved); if (it.saved) toast(exam ? 'Saved to Review. The key shows after you hand in.' : 'Saved to Review'); }
      catch (_) { it.saved = was; paintQ(); toast('Not saved. Try again.'); }
    }
    function setConf(i, v) {
      if (!cfg.conf || i < 0 || !cells[i]) return false;
      cells[i].conf = v || null;
      paintQ();
      emit('conf', i, v || null);
      saveState(i, { conf: v || null });
      return true;
    }
    function cycleConf() {
      const order = [null, 'sure', 'unsure', 'guess'];
      const c = cells[at] || {};
      return setConf(at, order[(order.indexOf(c.conf || null) + 1) % order.length]);
    }
    function report() {
      const it = items.get(at) || {};
      const qq = it.q || {};
      if (on.report) return emit('report', at, qq);
      const ctx = { kind: 'question', source: o.source || (exam ? 'test' : 'practice'), session: sid, question_id: qq.id, template: qq.template, seed: qq.seed,
        revealed: !!(ws && ws.answered && ws.answered() && !exam), live: exam, title: `Question ${(cells[at] || {}).n ?? at + 1}${o.short ? ', ' + o.short : ''}` };
      if (UI.report) return UI.report(ctx);
      toast('Reports open here soon. Use Send feedback in the menu for now.');
      return true;
    }
    function history() {
      const qq = q();
      if (on.history) return emit('history', at, qq);
      if (UI.history) return UI.history({ session: sid, question_id: qq.id, template: qq.template });
      return false;
    }
    function openDetails() {
      if (exam || view !== 'q' || !UI.pop) return false;
      if (on.details) return emit('details', at);
      const it = items.get(at) || {};
      const qq = it.q || {};
      const d = it.details || {};
      const hidden = challenge && !d.open;
      const t = UI.TOPIC && UI.TOPIC[qq.topic];
      const row = (k, v) => (v ? [h('dt', { text: k }), h('dd', {}, v)] : []);
      const idText = qq.template ? `${qq.template} · ${qq.seed ?? ''}`.trim() : qq.id || '';
      const link = qq.template ? `${location.origin}/practice/session/?q=${encodeURIComponent(qq.template)}:${qq.seed ?? ''}` : null;
      const copy = (text, msg) => h('button', { type: 'button', class: 'quiet sm', text: 'Copy', onclick: () => (UI.copyText ? UI.copyText(text, { toast: msg }) : null) });
      const dl = h('dl', { class: 'rn-details' },
        row('Question ID', hidden ? 'Shown after today’s challenge closes' : h('span', {}, h('span', { class: 'mono', text: idText }), ' ', idText ? copy(idText, 'Copied') : null)),
        row('Skill', [t ? t.name || t.short : qq.topic_name || qq.topic || '', qq.skill ? ` · ${qq.skill}` : ''].join('')),
        row('Question type', qq.name ? h('span', {}, h('b', { text: qq.name }), qq.about ? h('span', { class: 'meta', text: ` · ${qq.about}` }) : null) : null),
        row('Difficulty', d.difficulty || (qq.difficulty ? `${qq.difficulty[0].toUpperCase() + qq.difficulty.slice(1)}${qq.level ? ` · level ${qq.level} of 7` : ''}` : null)),
        row('Format', qq.type === 'spr' ? 'Grid-in (student-produced response)' : 'Multiple choice'),
        row('Why this one', !challenge ? it.why || qq.why : null),
        row('You and this type', d.you || null),
        row('Everyone', d.everyone || (!challenge ? 'Not enough answers yet' : null)),
        row('Formula', d.formula || null),
        row('Link to this exact question', hidden ? 'Shown after today’s challenge closes' : link ? copy(link, 'Link copied: anyone who opens it gets this exact question') : null));
      return UI.pop(detB || navB, h('div', { class: 'rn-detpop' }, h('div', { class: 'popover-head', text: 'Details' }), dl), { label: 'Details' });
    }
    function directions(first) {
      if (first && directionsSheet.skipped()) return null;
      return directionsSheet({ first });
    }
    function refreshNotes() {
      notesB.hidden = !(annotateOn || noteCount());
      notesB.querySelector('.tl').textContent = noteCount() ? `Notes ${noteCount()}` : 'Notes';
      if (!slot.hidden && slotTab === 'notes') { const box = slotBody.querySelector('.rn-notes'); if (box && !box.contains(doc.activeElement)) paintSlot(); }
    }

    /* ---------------- More */
    function more() {
      if (!UI.menu) return false;
      const items2 = [];
      const pref = (key, label, v) => ({ label, checked: !!v, onClick: () => { prefs[key] = !v; emit('pref', key, prefs[key]); applyPref(key); } });
      if (exam) {
        if (cfg.dirs) items2.push({ label: 'Directions', icon: 'ref', onClick: () => directions() });
        items2.push({ label: 'Keyboard shortcuts', kbd: '?', onClick: () => shortcuts() });
        const size = doc.documentElement.dataset.text || ls.get('satf.textsize', 'normal') || 'normal';
        items2.push({ group: 'Text size' });
        [['small', 'A− small'], ['normal', 'A normal'], ['large', 'A+ large']].forEach(([v, lab]) => items2.push({ label: lab, radio: true, checked: size === v, onClick: () => textSize(v) }));
        if (training) {
          if (o.pace) items2.push(pref('test_pace', 'Pace guide', o.pace && prefs.test_pace !== false));
          items2.push(pref('test_confidence', 'Confidence tags', cfg.conf));
        }
        items2.push({ label: 'Notes', icon: 'note', onClick: () => openSlot('notes') });
        if (cfg.scratch) items2.push({ label: 'Scratch', icon: 'pen', kbd: 'Shift+L', onClick: () => toggleScratch() });
        if (coarse()) items2.push({ label: 'Use the answer pad', checked: ls.get('satf.pad', true) !== false, onClick: () => { const v = !(ls.get('satf.pad', true) !== false); ls.set('satf.pad', v); toast(v ? 'The answer pad shows on grid-ins' : 'The keyboard shows on grid-ins'); } });
        if (coarse()) items2.push({ head: h('p', { class: 'help', text: 'Hold an option to cross it out (not while highlighting)' }) });
        items2.push({ label: `Report a problem with question ${(cells[at] || {}).n ?? at + 1}`, icon: 'report', onClick: () => report() });
        items2.push({ separator: true });
        items2.push({ label: 'Hand in this module…', onClick: () => openReview() });
        items2.push({ label: 'Save and exit', onClick: () => exit() });
        if (on.discard) items2.push({ label: 'Discard this test…', onClick: () => discard() });
      } else {
        (typeof o.more === 'function' ? o.more([], run) : o.more || []).forEach(x => items2.push(x));
        if (items2.length) items2.push({ separator: true });
        items2.push({ group: 'Settings' });
        items2.push(pref('first_tap', 'Answer on first tap', prefs.first_tap));
        items2.push(pref('open_explanations', 'Always open explanations', prefs.open_explanations));
        items2.push(pref('option_reasons', 'Show every option’s mistake', prefs.option_reasons !== false));
        items2.push(pref('show_stopwatch', 'Show question stopwatch', prefs.show_stopwatch !== false));
        items2.push(pref('pace_alert', 'Pace alert', prefs.pace_alert !== false));
        items2.push({ label: 'Check asks how sure', checked: prefs.confidence !== 'off', onClick: () => { prefs.confidence = prefs.confidence === 'off' ? 'ask' : 'off'; emit('pref', 'confidence', prefs.confidence); applyPref('confidence'); } });
        if (cfg.calc) {
          items2.push({ group: 'Calculator opens' });
          [['closed', 'Closed'], ['dock', 'Docked'], ['float', 'Floating']].forEach(([v, lab]) => items2.push({ label: lab, radio: true, checked: (prefs.calc_mode || 'closed') === v, onClick: () => { prefs.calc_mode = v; emit('pref', 'calc_mode', v); } }));
        }
        if (coarse()) items2.push({ head: h('p', { class: 'help', text: 'Hold an option to cross it out (not while highlighting)' }) });
        items2.push({ separator: true });
        items2.push({ label: 'Keyboard shortcuts', kbd: '?', onClick: () => shortcuts() });
        items2.push({ label: 'End set now', onClick: () => { leave('finish'); emit('finish', 'now'); } });
      }
      UI.menu(moreB, items2, { label: 'More', align: 'end' });
      return true;
    }
    function applyPref(key) {
      if (key === 'show_stopwatch' || key === 'pace_alert') paintWatch();
      if (key === 'confidence' && splitCtl) { splitCtl.el.remove(); splitCtl.tip && splitCtl.tip.remove(); splitCtl = null; syncFoot(); }
      if (key === 'option_reasons' && ws) ws.el.classList.toggle('why-off', prefs.option_reasons === false);
    }
    function textSize(v) {
      doc.documentElement.dataset.text = v === 'normal' ? '' : v;
      if (v === 'normal') delete doc.documentElement.dataset.text;
      ls.set('satf.textsize', v);
      emit('pref', 'text', v);
      if (scr) scr.redraw();
    }
    function shortcuts() {
      if (UI.keys && UI.keys.sheet) return UI.keys.sheet();
      if (!UI.sheet) return null;
      const rows = [];
      keyRegs.forEach(r => Object.entries(r.map).forEach(([k, b]) => { const d = b.does || ''; const row = rows.find(x => x.does === d); if (row) row.keys.push(k); else rows.push({ does: d, keys: [k] }); }));
      return UI.sheet({ title: 'Keyboard shortcuts', size: 'm', body: b => b.append(h('table', { class: 'table compact' }, h('tbody', {}, rows.map(r => h('tr', {}, h('td', {}, r.keys.map(k => h('kbd', { class: 'kbd', text: k.replace('Arrow', '').replace('Left', '←').replace('Right', '→') }))), h('td', { text: r.does })))))) });
    }

    /* ---------------- exit, pause, time's up, discard */
    function exit() {
      leave('exit');
      if (!UI.sheet) return emit('exit', exam ? 'save' : 'keep');
      if (exam) {
        const text = training ? 'Save and exit? The clock stops until you come back, and this test waits under In progress on Tests.'
          : 'Save and exit? The clock stops until you come back. This sitting keeps its score but won’t rank.';
        return UI.sheet({ title: 'Save and exit?', size: 's', body: b => {
          b.append(h('p', { text }));
          if (on.remind) b.append(h('button', { type: 'button', class: 'quiet', text: 'Remind me tonight', onclick: () => emit('remind') }));
        }, actions: [{ label: 'Keep going' }, { label: training ? 'Save and exit' : 'Pause and exit', primary: true, onClick: () => { emit('exit', 'save'); } }] });
      }
      const t = tally(cells);
      if (!t.answered) return emit('exit', 'quiet');
      const pausable = cfg.pause && timerApi && timerApi.timed;
      return UI.sheet({ title: 'Leave this set?', size: 's', body: b => {
        b.append(h('p', { text: `${t.answered} answered${total !== null ? ` of ${total}` : ''}. It stays in your history either way.` }));
        if (challenge) b.append(h('p', { class: 'help', text: 'The clock keeps running while you are away.' }));
      }, actions: [
        { label: 'Cancel', quiet: true },
        { label: 'End and see summary', onClick: () => { emit('exit', 'end'); } },
        { label: pausable ? 'Pause and keep for later' : 'Keep it for later', primary: true, onClick: () => { emit('exit', pausable ? 'pause' : 'keep'); } },
      ] });
    }
    let pausedView = null;
    async function pause() {
      if (!cfg.pause || !timerApi || view === 'paused') return false;
      leave('pause');
      try { await emit('pause'); } catch (_) { toast('Couldn’t pause. Try again.'); return true; }
      timerApi.pause();
      pausedView = view;
      view = 'paused';
      qArea.hidden = true;
      rail.hidden = true;
      const resume = h('button', { type: 'button', class: 'pill', text: 'Resume', onclick: () => resumeRun() });
      screenEl.replaceChildren(h('div', { class: 'rn-paused' }, h('p', { class: 'k', text: 'Paused' }), h('p', { class: 'rn-paused-t mono', text: `${mmss(timerApi.left)} left` }), h('p', { class: 'meta', text: 'The questions are hidden while the clock is stopped.' }), resume));
      screenEl.hidden = false;
      [fLeft, fMid, fRight].forEach(x => { x.hidden = true; });
      resume.focus();
      emit('view', 'paused', at);
      return true;
    }
    async function resumeRun() {
      try { await emit('resume'); } catch (_) { toast('Couldn’t resume. Try again.'); return; }
      timerApi.resume();
      view = pausedView === 'review' ? 'q' : 'q';
      screenEl.hidden = true; screenEl.replaceChildren();
      qArea.hidden = false; rail.hidden = false;
      [fLeft, fMid, fRight].forEach(x => { x.hidden = false; });
      visStart = performance.now();
      if (ws) ws.focus();
      emit('view', 'q', at);
    }
    function timeUp() {
      leave('timeup');
      try { const d = UI.sheet && UI.sheet.top && UI.sheet.top(); if (d && d.close) d.close(); } catch (_) {}
      if (navPop) { try { navPop.close(); } catch (_) {} navPop = null; }
      if (UI.calc && UI.calc.isOpen) UI.calc.close();
      if (ann) ann.closeBar();
      emit('timeUp');
    }
    async function discard() {
      if (!UI.confirm) return emit('discard');
      const ok = await UI.confirm({ title: 'Discard this test?', text: 'Your answers in this sitting are deleted and it won’t count anywhere. This can’t be undone.', confirm: 'Discard', destructive: true });
      if (ok) emit('discard');
    }

    /* ---------------- nudges (X4, Training) and the pace delta (X3, P16) */
    let sunkShown = false, lastMinute = false, lastMinuteAt = -1;
    const cps = new Set();
    function nudge(text, actions = [], kind) {
      if (!text) { nudgeEl.hidden = true; nudgeEl.replaceChildren(); return; }
      nudgeEl.replaceChildren(h('p', { text }), h('div', { class: 'rn-nudge-acts' }, actions.map(a => h('button', { type: 'button', class: a.primary ? 'btn sm' : 'quiet sm', text: a.label, onclick: () => { a.run(); } }))));
      nudgeEl.hidden = false;
      say(text);
      if (kind) emit('nudge', { kind, qid: (q() || {}).id, at: Math.round(timerApi && Number.isFinite(timerApi.left) ? timerApi.left : 0) });
    }
    function budgetAt(i) { return cfg.pace ? o.pace.budget_s[i] * 1000 : +((items.get(i) || {}).q || {}).budget_ms || 95000; }
    function tick() {
      if (dead || view !== 'q' || !ws) return;
      paintWatch();
      if (!cfg.nudges || !timerApi || !timerApi.timed) return;
      const c = cells[at] || {};
      const unans = c.status !== 'answered';
      if (!sunkShown && unans && msAt(at) > Math.max(2 * budgetAt(at), 150000) && !(c._sunk)) {
        sunkShown = true; c._sunk = true;
        nudge(`${msx(msAt(at))} on this one. Your budget for it is ${msx(budgetAt(at))}. Mark it and come back?`,
          [{ label: 'Mark and next', primary: true, run: () => { setMark(at, true); nudge(null); next(); } }, { label: 'Keep going', run: () => nudge(null) }], 'time_sink');
      }
      const left = timerApi.left;
      const blanks = cells.map((x, i) => ({ x, i })).filter(y => y.x.status !== 'answered' && y.x.status !== 'future');
      if (!lastMinute && left <= 60 && blanks.length) {
        lastMinute = true;
        const cycle = () => { const nx = blanks.map(y => y.i).find(i => i > lastMinuteAt) ?? blanks[0].i; lastMinuteAt = nx; pick(nx); };
        nudge(`${blanks.length} unanswered. A guess can’t cost you.`, [{ label: 'Next blank', primary: true, run: cycle }], 'last_minute');
      }
    }
    const tickT = setInterval(tick, 1000);
    cleanups.push(() => clearInterval(tickT));
    function paceDelta() {
      if (!timerApi || !timerApi.timed) return;
      if (exam) {
        if (!cfg.pace) return;
        const b = o.pace.budget_s;
        const dur = o.pace.duration_s || b.reduce((a, x) => a + x, 0) + (o.pace.reserve_s || 0);
        const elapsed = dur - timerApi.left;
        const planned = cells.reduce((a, c, i) => a + (c.status === 'answered' ? (b[i] || 0) : 0), 0);
        const d = planned - elapsed;
        timerApi.delta(`${d >= 0 ? '+' : ''}${mmss(Math.abs(d))} ${d >= 0 ? 'ahead' : 'behind'}`);
        // checkpoint toasts after Q7 and Q14
        [7, 14].forEach(k => {
          if (cps.has(k) || at < k) return;
          const by = b.slice(0, k).reduce((a, x) => a + x, 0);
          const behind = elapsed - by;
          cps.add(k);
          if (behind > 120) toast(`${mmss(behind)} behind at Q${k + 1}. Mark anything past 2:00 and come back.`, { ms: 6000 });
        });
        return;
      }
      // practice (P16): answered budgets minus the time spent on them, and the hard ones left
      let d = 0, hard = 0;
      cells.forEach((c, i) => {
        if (answeredish(c.status) && c.status !== 'future') d += (+c.budget_ms || budgetAt(i)) - msAt(i);
        else if (c.tier === 'hard') hard++;
      });
      const txt = `${mmss(Math.abs(d) / 1000)} ${d >= 0 ? 'ahead of pace' : 'behind'}${hard ? ` · ${hard} Hard left` : ''}`;
      timerApi.delta(txt);
    }
    if (cfg.pace) { const pt = setInterval(() => { paceDelta(); if (view === 'q') paintRail(); }, 5000); cleanups.push(() => clearInterval(pt)); }

    /* ---------------- time on the question: visible and focused only; every 30 s and on leaving */
    const onVis = () => {
      if (view !== 'q' || at < 0) return;
      if (doc.hidden) {
        if (visStart !== null) { const d = performance.now() - visStart; timeAt.set(at, (timeAt.get(at) || 0) + d); if (cells[at]) cells[at].ms = Math.round(timeAt.get(at)); emit('time', at, Math.round(d), 'hidden'); }
        visStart = null;
        if (exam && timerApi && timerApi.timed && !timerApi.paused) { away.n++; away.at = performance.now(); }
      } else {
        visStart = performance.now();
        if (away.at) { away.ms += performance.now() - away.at; away.at = null; emit('away', { away_ms: Math.round(away.ms), away_n: away.n }); }
      }
    };
    const away = { n: 0, ms: 0, at: null };
    doc.addEventListener('visibilitychange', onVis);
    cleanups.push(() => doc.removeEventListener('visibilitychange', onVis));
    const flushT = setInterval(() => {
      if (view !== 'q' || at < 0 || visStart === null) return;
      const d = performance.now() - visStart;
      if (d < 30000) return;
      timeAt.set(at, (timeAt.get(at) || 0) + d);
      visStart = performance.now();
      emit('time', at, Math.round(d), 'tick');
    }, 5000);
    cleanups.push(() => clearInterval(flushT));
    const onHide = () => leave('pagehide');
    addEventListener('pagehide', onHide);
    cleanups.push(() => removeEventListener('pagehide', onHide));
    if (o.guardLeave) {
      const guard = e => { if (timerApi && timerApi.timed && !timerApi.paused && view !== 'done') { e.preventDefault(); e.returnValue = ''; } };
      addEventListener('beforeunload', guard);
      cleanups.push(() => removeEventListener('beforeunload', guard));
    }
    if (o.fullscreen && doc.fullscreenEnabled) {
      const fs = () => {
        if (doc.fullscreenElement || view === 'done') return;
        if (UI.banner) UI.banner('fullscreen', 'You left fullscreen.', [{ label: 'Return to fullscreen', onClick: () => { try { doc.documentElement.requestFullscreen(); } catch (_) {} } }], { host: top.parentNode === root ? null : null, dismiss: true });
      };
      doc.addEventListener('fullscreenchange', fs);
      cleanups.push(() => doc.removeEventListener('fullscreenchange', fs));
    }

    /* ---------------- the save status (#saved) */
    function paintSaved(info) {
      if (!info) { savedEl.textContent = ''; return; }
      savedEl.replaceChildren(h('span', { text: info.text || '' }));
      savedEl.dataset.state = info.state || '';
      if (info.state === 'error' && info.retry) savedEl.append(' · ', h('button', { type: 'button', class: 'qlink', text: 'Retry', onclick: () => info.retry() }));
      if (cyw && view === 'review') cyw.update(null, { saving: info });
      root.classList.toggle('rn-unsaved', info.state === 'offline' || info.state === 'error');
    }
    if (o.queue && o.queue.onStatus) cleanups.push(o.queue.onStatus(paintSaved));

    /* ---------------- phone: swipe the column for Back and Next (X6) */
    (() => {
      let s = null;
      qArea.addEventListener('pointerdown', e => {
        if (e.pointerType !== 'touch' || !phone()) return;
        if (annotateOn || scratchOn || e.target.closest('.q-table, .calc, textarea, input')) return;
        s = { x: e.clientX, y: e.clientY, t: performance.now() };
      });
      qArea.addEventListener('pointerup', e => {
        if (!s) return;
        const dx = e.clientX - s.x, dy = e.clientY - s.y;
        s = null;
        const sel = getSelection && getSelection();
        if (sel && !sel.isCollapsed) return;
        if (Math.abs(dx) < 64 || Math.abs(dy) > Math.abs(dx) * Math.tan(Math.PI / 6)) return;
        if (dx < 0) { if (!canForward()) return; slide('l'); next(); }
        else if (at > 0 || queue) { slide('r'); back(); }
      });
      qArea.addEventListener('pointercancel', () => { s = null; });
      const slide = d => { if (still()) return; qHost.classList.remove('rn-slide-l', 'rn-slide-r'); void qHost.offsetWidth; qHost.classList.add('rn-slide-' + d); };
    })();

    /* ---------------- keys (2.8, R43): question actions in 'runner', tools and moving in 'session' */
    const inQ = () => view === 'q' && !!ws;
    const wsKey = e => (inQ() && ws.key(e) ? undefined : false);
    const qmap = {};
    ['A', 'C', 'D', '1', '2', '3', '4'].forEach(k => { qmap[k] = { does: 'Choose A–D or 1–4', run: wsKey }; });
    qmap.B = { id: 'save', does: 'Choose A–D or 1–4', run: e => {
      if (!inQ()) return false;
      if (!exam && ws.answered()) { const r = ws.el.querySelector('.qa-save'); if (r) { r.click(); return; } return false; }
      return wsKey(e);
    } };
    ['A', 'B', 'C', 'D'].forEach(k => { qmap['Shift+' + k] = { does: 'Strike or unstrike A–D', run: wsKey }; });
    qmap.Enter = { does: exam ? 'Next' : 'Check, Next, or Save & next', run: e => {
      if (e.target && e.target.closest && e.target.closest('button, a, textarea, select, [role=radio], [role=tab], summary, input:not(.grid-in input)')) return false;
      if (view === 'review') { const g = screenEl.querySelector('.cyw-go:not(:disabled)'); if (g) { g.click(); return; } return false; }
      if (!inQ()) return false;
      if (exam) { next(); return; }
      if (ws.key(e)) return;
      if (ws.answered() || endMode || (cells[at] || {}).status === 'skipped') { next(); return; }
      return false;
    } };
    if (!exam) qmap['Shift+Enter'] = { does: 'Check as Unsure', run: e => (inQ() && !(e.target.closest && e.target.closest('textarea')) && ws.key(e) ? undefined : false) };
    qmap.E = { does: 'Eliminate mode', run: e => { const r = wsKey(e); if (r !== false) paintQ(); return r; } };
    qmap.M = { id: 'mark', does: 'Mark for review', run: () => (inQ() ? (setMark(at), undefined) : false) };
    qmap.O = { id: 'note', does: 'My note', run: () => (inQ() ? (openNote(noteB || addNote), undefined) : false) };
    qmap.R = { id: 'report', does: 'Report a problem', run: () => (inQ() ? (report(), undefined) : false) };
    if (exam) {
      if (cfg.conf) qmap.K = { does: 'Confidence: Sure, Unsure, Guess, none', run: () => (inQ() ? (cycleConf(), undefined) : false) };
    } else {
      qmap.I = { id: 'guess', does: 'Check as Guess', run: wsKey };
      qmap.S = { does: 'Skip for now', run: wsKey };
      qmap.W = { does: 'Hint', run: wsKey };
      qmap.V = { id: 'details', does: 'Details', run: () => (inQ() ? (openDetails(), undefined) : false) };
      qmap.Y = { id: 'history', does: 'Attempt history', run: () => (inQ() && (ws.answered() || +(items.get(at) || {}).attempts) ? (history(), undefined) : false) };
      const act = id => () => { if (!inQ() || !ws.answered()) return false; const b = ws.el.querySelector('.q-actions'); if (!b) return false; const btn = b.querySelector(id === 'twin_menu' ? '.split-caret, .qa-twin-menu' : '.qa-twin, .verb, .split > :first-child'); if (!btn) return false; btn.click(); return undefined; };
      qmap.T = { id: 'twin', does: 'Twin: same kind, new numbers', run: act('twin') };
      qmap['Shift+T'] = { id: 'twin_menu', does: 'Twin menu', run: act('twin_menu') };
      qmap['Shift+G'] = { id: 'desmos', does: 'Show me in Desmos', run: () => { const it = items.get(at) || {}; const dz = it.fb && it.fb.desmos; if (!inQ() || !dz || !UI.calc || !UI.calc.walkthrough) return false; UI.calc.walkthrough(dz); return undefined; } };
    }
    const tmap = {
      ArrowLeft: { does: 'Back', run: () => { if (view === 'review') return false; back(); } },
      ArrowRight: { does: 'Next', run: () => { if (view !== 'q' || !canForward()) return false; next(); } },
      N: { does: 'Navigator', run: () => (view === 'q' || view === 'review' ? (toggleNav(), undefined) : false) },
      G: { does: 'Calculator', run: () => (toggleCalc() ? undefined : false) },
      F: { does: 'Reference (formula sheet)', run: () => (cfg.ref ? (toggleRef(), undefined) : false) },
      L: { does: exam ? 'Highlights & Notes' : 'Highlight', run: () => (view === 'q' && toggleAnnotate() ? undefined : false) },
      H: { does: 'Hide or show the timer', run: () => (timerApi ? (timerApi.hide(!timerApi.hidden), undefined) : false) },
      'Shift+R': { does: 'Check your work', run: () => (view === 'q' ? (openReview(), undefined) : false) },
      U: { does: 'Next unanswered', run: () => (view === 'q' ? (jumpNext('unanswered'), undefined) : false) },
      'Shift+M': { does: 'Next marked', run: () => (view === 'q' ? (jumpNext('flag'), undefined) : false) },
      Escape: { does: 'Close', run: () => {
        if (!slot.hidden && slotFloat) { closeSlot(true); return; }
        if (scratchOn) { toggleScratch(); return; }
        if (queue) { stopQueue(); return; }
        return false;
      } },
    };
    if (cfg.scratch) tmap['Shift+L'] = { does: 'Scratch', run: () => (view === 'q' && toggleScratch() ? undefined : false) };
    if (cfg.pause && o.clock) tmap.P = { does: 'Pause', run: () => (view === 'q' ? (pause(), undefined) : false) };
    const keyRegs = [{ map: qmap }, { map: tmap }];
    const regs = [];
    try { regs.push(keyScope('runner', qmap, { label: 'Question' })); } catch (e) { console.warn(e.message); }
    try { regs.push(keyScope('session', tmap, { label: exam ? 'Test window' : 'This set' })); } catch (e) { console.warn(e.message); }

    /* ---------------- the api */
    const run = {
      el: root,
      get at() { return at; },
      get ws() { return ws; },
      get view() { return view; },
      get cells() { return cells; },
      get queueing() { return queue ? { list: queue.list.slice(), k: queue.k } : null; },
      timer: timerApi,
      show(i, it) { items.set(i, it); show(i, it); },
      go, next, back,
      item(i, patch) { const it = items.get(i); if (it) Object.assign(it, patch); else items.set(i, Object.assign({}, patch)); if (i === at) paintQ(); },
      cell(i, patch) { cells[i] = Object.assign(cells[i] || { n: i + 1, status: 'unanswered' }, patch); paintRail(); if (i === at) { paintQ(); syncFoot(); } if (navApi) navApi.update(cells, at); if (cyw) cyw.update(cells); },
      setCells(list, n) { cells = list.map((c, i) => Object.assign({ n: i + 1, status: 'unanswered' }, c, { current: i === at })); if (n !== undefined) total = n; paintRail(); syncFoot(); },
      addSlot(c = {}, budget_s, why) { cells.push(Object.assign({ n: cells.length + 1, status: 'future' }, c)); if (total !== null) total++; paintRail(); syncFoot(); if (timerApi && budget_s) timerApi.add(budget_s, why); },
      // G9: the next question rendered while the verdict shows; Next swaps it in
      preload(i, it) {
        if (!it || !it.q || pre.has(i) || dead) return;
        items.set(i, items.get(i) || it);
        pre.set(i, { it, ws: mountWs(i, it, true) });
      },
      discardPreload(i) { const p = pre.get(i); if (p && p.ws) try { p.ws.destroy(); } catch (_) {} pre.delete(i); if (items.get(i) && !items.get(i).fb) items.delete(i); },
      review: openReview,
      closeReview,
      navigator: toggleNav,
      queue: startQueue,
      screen(node, footNodes) {
        leave('screen');
        view = node ? 'screen' : 'q';
        if (!node) { reviewOff(); screenEl.hidden = true; qArea.hidden = false; rail.hidden = false; [fLeft, fMid, fRight].forEach(x => { x.hidden = false; }); footAlt.hidden = true; return; }
        qArea.hidden = true; rail.hidden = true;
        screenEl.replaceChildren(node); screenEl.hidden = false;
        [fLeft, fMid, fRight].forEach(x => { x.hidden = !!footNodes; });
        footAlt.replaceChildren(...[].concat(footNodes || []));
        footAlt.hidden = !footNodes;
      },
      done() { view = 'done'; leave('done'); },
      directions,
      say,
      banner(text, actions) { nudge(text, actions || []); },
      status: paintSaved,
      reveal(fb) { if (ws) ws.reveal(fb); },
      refAt(id) { toggleRef({ highlight: id }); },
      layout,
      destroy() {
        if (dead) return;
        leave('destroy');
        dead = true;
        destroyWs();
        pre.forEach(p => { try { p.ws.destroy(); } catch (_) {} });
        pre.clear();
        regs.forEach(r => { try { r.unregister(); } catch (_) {} });
        cleanups.splice(0).forEach(f => { try { f(); } catch (_) {} });
        if (timerApi) timerApi.destroy();
        if (UI.calc && UI.calc.dock) UI.calc.dock(null);
        root.remove();
      },
    };

    /* ---------------- start */
    layout();
    paintRail();
    const start = o.at ?? (Number.isInteger(ls.get(`satf.pos.${sid}`, null)) ? ls.get(`satf.pos.${sid}`, null) : 0);
    const first = Math.max(0, Math.min(start, total === null ? start : total - 1));
    if (items.get(first)) show(first, items.get(first));
    else if (on.load) go(first, 'start');
    if (prefs.calc_mode && prefs.calc_mode !== 'closed' && cfg.calc && UI.calc && !UI.calc.isOpen) UI.calc.open({ mode: prefs.calc_mode === 'float' ? 'float' : undefined, focus: false });
    return run;
  }

  /* ------------------------------------------------------------ export */
  Object.assign(UI, { runner, timer, saveQueue, navigator: navPanel, checkYourWork, annotate, scratch, refDock, directions: directionsSheet, rdp });
  if (location.pathname.startsWith('/dev/') && !rdp.__test()) console.error('runner.js self-test failed: rdp');
})();
