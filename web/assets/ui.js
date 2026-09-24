/* ============================================================================
   SAT Freshman -- ui.js, loaded on every page after head.js and before kit.js

   The core (F2, spec/rebuild-v2.md 2.4's ui.js row, Shell 1, 2.9, 2.11-2.13, R11, R22,
   R43; shell-me.md U21, U23; product.md G2, G9):
     UI.learner()                   this browser's credential: an `a:` code minted here or a
                                    `d:` device token; localStorage satf.learner, sessionStorage
                                    only on a shared computer (U21)
     UI.useLearner(code, {session, same})   adopt one; a new learner clears cached copies
     UI.freshLearner()              mint a new anonymous code and adopt it
     UI.shared()                    true on a shared-computer session
     UI.ready                       resolves once a new tab of a shared session has asked
                                    its open tabs for the token (at most 300 ms)
     UI.api(path, {method, body, keepalive, quiet, optimistic, failText, signal})
                                    X-Learner and X-Tz; takes X-Learner-Swap; a network error
                                    shows the offline banner and retries at 5, 10, 20, 30 s;
                                    401 retired shows the retired banner; writes wait while the
                                    page is prerendering; optimistic() applies a change at once
                                    and returns its revert, run with a toast on failure
     UI.cached(path, fn(data, fromCache), {store: 'session' | 'local', until: 'day', key, fresh, onFresh})
                                    paint the last copy at once, revalidate, repaint only when
                                    the JSON changed (U23); UI.cached.clear()
     UI.whenVisible(fn)             now, or once a prerendered page is shown (U23)
     UI.refresh() (alias UI.me(true)), UI.onShell(fn(shell, fromCache)), UI.shellData()
                                    GET /api/shell, painted from sessionStorage satf.shell first
     UI.me(fresh)                   GET /api/me, once per page
     UI.prefs() -> Promise          every pref, defaults merged; UI.prefs.now(), UI.prefs.set()
     UI.prefRow(host, key, {label, helper, onChange})   one settings row that saves instantly
     UI.look(prefs)                 theme, text size and motion, mirrored to satf.look
     UI.keys.register(scope, map, {label, within, when}) -> {unregister}
                                    map: {'G T': fn | {does, run, id, when}}; UI.keys.sheet()
                                    opens the ? sheet; UI.keys.label(combo)
     UI.ROUTES, UI.start(item), UI.nextItems()   where G-keys go; start an Up next item
     UI.skip()                      the skip link, first on every page with a <main>
   Kept for the pages until they are rebuilt: the old top bar (UI.shell), UI.question,
   UI.calc, UI.ref, UI.plan, UI.snap, the topics and glyphs.
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI = window.UI || {};
  const doc = document;

  /* ------------------------------------------------------------ storage, quietly */
  const store = name => { try { return window[name] || null; } catch (_) { return null; } };
  const sget = (s, k) => { try { return s ? s.getItem(k) : null; } catch (_) { return null; } };
  const sput = (s, k, v) => {
    try { if (!s) return false; if (v === null) s.removeItem(k); else s.setItem(k, v); return true; } catch (_) { return false; }
  };
  const LS = () => store('localStorage'), SS = () => store('sessionStorage');
  const media = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
  // false when both stores refuse (the storage-blocked banner, Shell 2.11)
  const storable = [LS, SS].some(s => sput(s(), 'satf.t', '1') && sput(s(), 'satf.t', null));

  /* ------------------------------------------------------------ identity (Shell 1, U21)
     The credential is the whole of a learner's access, so a minted code is not guessable.
     It lives in localStorage, or where that is refused, in sessionStorage for the tab.
     Never in window.name, which whichever page came before can set. A shared computer
     keeps it in sessionStorage only; a new tab of that session asks an open one for it on
     a BroadcastChannel and waits up to 300 ms, and with no reply starts signed out. */
  const LEARNER_KEY = 'satf.learner', SHARED_KEY = 'satf.shared';
  const mint = () => 'a:' + Array.from(crypto.getRandomValues(new Uint8Array(12)), b => b.toString(36).padStart(2, '0')).join('');
  let memo = null, shared = false, asking = false, provisional = false, isReady = true;
  function read() {
    const ss = SS(), ls = LS();
    if (sget(ss, SHARED_KEY) === '1' && sget(ss, LEARNER_KEY)) { shared = true; return sget(ss, LEARNER_KEY); }
    for (const s of [ls, ss]) { const v = sget(s, LEARNER_KEY); if (v) return v; }
    return null;
  }
  function keep(code) {
    if (shared) { sput(SS(), LEARNER_KEY, code); sput(SS(), SHARED_KEY, '1'); return; }
    if (!sput(LS(), LEARNER_KEY, code)) sput(SS(), LEARNER_KEY, code);
  }
  function learner() {
    if (!memo) {
      memo = mint();
      if (asking) provisional = true; else keep(memo);
    }
    return memo;
  }
  function useLearner(code, o = {}) {
    const was = memo;
    if (o.session !== undefined) shared = !!o.session;
    if (!shared) { sput(SS(), SHARED_KEY, null); sput(SS(), LEARNER_KEY, null); }
    memo = code;
    provisional = false;
    keep(code);
    if (was && was !== code && !o.same) cached.clear();
    return code;
  }
  const freshLearner = () => useLearner(mint(), { session: false });

  let chan = null;
  try { chan = new BroadcastChannel('satf-session'); } catch (_) {}
  memo = read();
  let ready = Promise.resolve();
  if (!memo && chan) {
    // ponytail: a first visit anywhere waits these 300 ms once; keep a "shared" hint in
    // localStorage if that ever shows in the budgets
    asking = true;
    isReady = false;
    ready = new Promise(resolve => {
      const done = token => {
        clearTimeout(timer);
        chan.removeEventListener('message', on);
        asking = false;
        if (token) { shared = true; memo = token; keep(token); provisional = false; }
        else if (provisional) { keep(memo); provisional = false; }
        isReady = true;
        resolve();
      };
      const on = e => { const t = e.data && e.data.token; if (typeof t === 'string' && /^d:[0-9a-z]{32}$/.test(t)) done(t); };
      const timer = setTimeout(() => done(null), 300);
      chan.addEventListener('message', on);
      chan.postMessage({ ask: true });
    });
  }
  if (chan) chan.addEventListener('message', e => { if (e.data && e.data.ask && shared && memo) chan.postMessage({ token: memo }); });

  /* ------------------------------------------------------------ visible (U23)
     A prerendered page runs its script before the student sees it: anything that marks
     something seen, shows something or writes waits until it is shown. */
  const whenVisible = fn => new Promise(resolve => {
    const go = () => { try { resolve(fn ? fn() : undefined); } catch (e) { resolve(undefined); throw e; } };
    if (doc.prerendering) doc.addEventListener('prerenderingchange', go, { once: true }); else go();
  });

  /* ------------------------------------------------------------ the API */
  const headers = () => ({ 'content-type': 'application/json', 'X-Learner': learner(),
                           'X-Tz': String(new Date().getTimezoneOffset()) });
  const GONE = [502, 503, 504];         // a proxy that can't reach us reads as offline too
  async function api(path, o = {}) {
    const method = (o.method || 'GET').toUpperCase();
    if (!isReady) await ready;
    if (method !== 'GET' && method !== 'HEAD' && doc.prerendering) await whenVisible();
    const revert = typeof o.optimistic === 'function' ? o.optimistic() : null;
    let r;
    try {
      r = await fetch('/api' + path, { method, headers: headers(), keepalive: !!o.keepalive, signal: o.signal,
                                       body: o.body === undefined ? undefined : JSON.stringify(o.body) });
    } catch (e) {
      if (e && e.name === 'AbortError') throw e;
      if (!o.quiet) offline.start();
      throw failed(Object.assign(new Error('Can’t reach SAT Freshman.'), { status: 0, offline: true }), revert, o);
    }
    const swap = r.headers.get('X-Learner-Swap');
    if (swap && /^d:[0-9a-z]{32}$/.test(swap)) useLearner(swap, { same: true });
    if (GONE.includes(r.status)) {
      if (!o.quiet) offline.start();
      throw failed(Object.assign(new Error('Can’t reach SAT Freshman.'), { status: r.status, offline: true }), revert, o);
    }
    offline.stop();
    let data = null;
    if (r.status !== 204) { try { data = await r.json(); } catch (_) {} }
    if (!r.ok) {
      const d = data && data.detail;
      const e = new Error(typeof d === 'string' ? d : (d ? JSON.stringify(d) : `HTTP ${r.status}`));
      Object.assign(e, { status: r.status, data, detail: d, retired: !!(r.status === 401 && d && d.retired) });
      if (e.retired) retired();
      throw failed(e, revert, o);
    }
    return data;
  }
  function failed(e, revert, o) {
    if (revert) {
      try { revert(e); } catch (_) {}
      if (UI.toast) UI.toast(o.failText || 'Not saved. Try again.');
    }
    return e;
  }

  /* offline (Shell 2.11): one banner, retrying at 5, 10, 20, then every 30 s; any answer
     from the server clears it */
  const offline = (() => {
    const STEPS = [5, 10, 20, 30];
    let on = false, step = 0, left = 0, timer = 0, count = null;
    function paint(text) {
      if (!UI.banner) return;
      if (!count || !count.isConnected) {
        count = doc.createElement('span');
        count.setAttribute('aria-hidden', 'true');
        const t = doc.createElement('span');
        const sr = doc.createElement('span');
        sr.className = 'sr';
        sr.textContent = 'It keeps retrying by itself.';
        t.append('Can’t reach SAT Freshman. ', count, sr);
        UI.banner('offline', t, [{ label: 'Retry now', onClick: probe }], { sys: true });
      }
      count.textContent = text;
    }
    function tick() {
      left -= 1;
      if (left <= 0) probe(); else paint(`Retrying in ${left}s`);
    }
    function wait() {
      left = STEPS[Math.min(step, STEPS.length - 1)];
      clearInterval(timer);
      timer = setInterval(tick, 1000);
      paint(`Retrying in ${left}s`);
    }
    async function probe() {
      clearInterval(timer);
      paint('Retrying now…');
      try {
        const r = await fetch('/api/health', { cache: 'no-store' });
        if (r.ok) { stop(); if (shellAsked) refresh(); return; }
      } catch (_) {}
      if (on) { step += 1; wait(); }
    }
    function start() { if (on) return; on = true; step = 0; wait(); }
    function stop() {
      if (!on) return;
      on = false; clearInterval(timer); count = null;
      if (UI.banner) UI.banner.clear('offline');
      dispatchEvent(new Event('satf:online'));
    }
    return { start, stop, get on() { return on; } };
  })();

  /* retired (Shell 1, U21): a rotated-away code, a signed-out device, an ended shared
     session. No cached card of that student is painted after it. */
  let retiredShown = false;
  function retired() {
    cached.clear();
    dispatchEvent(new Event('satf:retired'));
    if (retiredShown || !UI.banner) return;
    retiredShown = true;
    const actions = [{ label: 'Sign in', href: '/signin/', primary: true }];
    if (!shared) actions.push({ label: 'Start fresh', onClick: () => { freshLearner(); location.href = '/'; } });
    UI.banner('retired', shared ? 'This shared-computer session has ended. Sign in again.'
      : 'This device was signed out from another device.', actions, { sys: true });
  }

  /* ------------------------------------------------------------ paint from cache (U23) */
  const CACHE_MAX = 200 * 1024;
  const CACHE_PREFIX = 'satf.c.';
  const localDay = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
  const hashOf = text => { let x = 5381; for (let i = 0; i < text.length; i++) x = (x * 33 + text.charCodeAt(i)) | 0; return (x >>> 0).toString(36) + ':' + text.length; };
  function cached(path, fn, o = {}) {
    const s = o.store === 'local' ? LS() : SS();
    const key = o.key || CACHE_PREFIX + path;
    const day = localDay();
    let seen = null;
    try {
      const c = JSON.parse(sget(s, key) || 'null');
      if (c && c.l === learner() && (o.until !== 'day' || c.day === day)) {
        seen = c.h;
        if (!o.fresh) {
          try { fn(c.d, true); } catch (e) { seen = null; console.error(e); }
        }
      }
    } catch (_) {}
    return api(path, o.api).then(d => {
      const text = JSON.stringify(d);
      const h = hashOf(text);
      sput(s, key, text.length <= CACHE_MAX
        ? `{"l":${JSON.stringify(learner())},"day":"${day}","h":"${h}","d":${text}}` : null);
      if (o.onFresh) o.onFresh(d);
      if (h !== seen) fn(d, false);
      return d;
    });
  }
  cached.clear = () => {
    for (const s of [SS(), LS()]) {
      try {
        if (!s) continue;
        for (let i = s.length - 1; i >= 0; i--) {
          const k = s.key(i);
          if (k && (k.startsWith(CACHE_PREFIX) || k === 'satf.shell')) s.removeItem(k);
        }
      } catch (_) {}
    }
    shellData = null;
  };

  /* ------------------------------------------------------------ the look (Shell 2.13)
     prefs.theme / text / motion on <html>; only values off the default are set and
     mirrored to localStorage satf.look, which head.js reads before first paint. */
  let lookNow = { theme: 'light', text: 'normal', motion: 'system' }, following = false;
  function look(p = {}, mirror = true) {
    const d = doc.documentElement;
    const theme = p.theme || 'light', text = p.text || 'normal', motion = p.motion || 'system';
    const dark = theme === 'dark' || (theme === 'system' && media('(prefers-color-scheme: dark)'));
    if (theme === 'light') delete d.dataset.theme; else d.dataset.theme = dark ? 'dark' : 'light';
    if (text === 'small' || text === 'large') d.dataset.text = text; else delete d.dataset.text;
    if (motion === 'reduce') d.dataset.motion = 'reduce'; else delete d.dataset.motion;
    const tc = doc.querySelector('meta[name="theme-color"]');
    if (tc) tc.content = dark ? '#1A1917' : '#FFFFFF';
    lookNow = { theme, text, motion };
    if (theme === 'system' && !following) {
      following = true;
      try { matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (lookNow.theme === 'system') look(lookNow, false); }); } catch (_) {}
    }
    if (mirror) {
      const keepIt = {};
      if (theme !== 'light') keepIt.theme = theme;
      if (text !== 'normal') keepIt.text = text;
      if (motion !== 'system') keepIt.motion = motion;
      sput(LS(), 'satf.look', Object.keys(keepIt).length ? JSON.stringify(keepIt) : null);
    }
    return lookNow;
  }
  const LOOK_KEYS = ['theme', 'text', 'motion'];

  /* ------------------------------------------------------------ shell data (Shell 2.12)
     GET /api/shell once per page load, painted first from sessionStorage satf.shell;
     again when the tab comes back into view, and on UI.refresh(). */
  let shellData = null, shellAsked = null, shellAt = 0;
  const shellSubs = [];
  function takeShell(d, fromCache) {
    if (d && d.retired) { retired(); return; }
    shellData = d;
    UI.answered = d.answered;
    shellSubs.slice().forEach(fn => { try { fn(d, fromCache); } catch (e) { console.error(e); } });
  }
  function refresh() {
    const first = !shellAsked;
    shellAt = Date.now();
    // the look follows every fresh copy, changed or not, never a cached one
    shellAsked = cached('/shell', takeShell, { key: 'satf.shell', fresh: !first,
                                              onFresh: d => { if (d && d.prefs) look(d.prefs, true); } });
    shellAsked.catch(() => {});
    return shellAsked;
  }
  const onShell = fn => { shellSubs.push(fn); if (shellData) fn(shellData, false); return () => { const i = shellSubs.indexOf(fn); if (i >= 0) shellSubs.splice(i, 1); }; };
  doc.addEventListener('visibilitychange', () => {
    if (doc.visibilityState === 'visible' && shellAsked && Date.now() - shellAt > 15000) refresh();
  });

  let meAsked = null;
  function me(fresh = false) {
    if (fresh) refresh();
    if (!meAsked || fresh) {
      meAsked = api('/me');
      meAsked.catch(() => { meAsked = null; });
    }
    return meAsked;
  }

  /* ------------------------------------------------------------ prefs (R11, §2.7) */
  function prefs() {
    if (shellData && shellData.prefs) return Promise.resolve(shellData.prefs);
    return (shellAsked || refresh()).then(d => (d && d.prefs) || (shellData && shellData.prefs) || {},
                                          () => (shellData && shellData.prefs) || {});
  }
  prefs.now = () => (shellData && shellData.prefs) || {};
  // PUT /api/me {prefs}: resolves to the profile (prefs, pref_source, stage); the look
  // keys apply at once and go back if the save fails
  prefs.set = async changes => {
    const before = { ...lookNow };
    if (LOOK_KEYS.some(k => k in changes)) look({ ...lookNow, ...pick(changes, LOOK_KEYS) }, false);
    let pr;
    try { pr = (await api('/me', { method: 'PUT', body: { prefs: changes } })).profile; }
    catch (e) { look(before, false); throw e; }
    if (shellData) Object.assign(shellData, { prefs: pr.prefs, pref_source: pr.pref_source, stage: pr.stage });
    look(pr.prefs, true);
    dispatchEvent(new CustomEvent('satf:prefs', { detail: pr }));
    return pr;
  };
  const pick = (o, ks) => Object.fromEntries(ks.filter(k => o[k] !== undefined && o[k] !== null).map(k => [k, o[k]]));

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
    for (const k of kids.flat(3)) if (k !== null && k !== undefined && k !== false) e.append(k);
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
  const reduced = () => media('(prefers-reduced-motion: reduce)') || doc.documentElement.dataset.motion === 'reduce';

  /* what a day of the plan holds, from three answers: the exam date, a study
     day's minutes, and which weekdays are study days (Monday first). Plan
     draws its calendar from this and Today leads with it. */
  const plan = {
    iso: d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`,
    dow: d => (d.getDay() + 6) % 7,
    testOf: minutes => minutes >= 70 ? 'section' : minutes >= 35 ? 'module' : null,
    set: p => !!(p && p.exam_date && p.minutes && p.days),
    dayOf(d, p) {
      const s = plan.iso(d);
      if (s === p.exam_date) return 'exam';
      if (s > p.exam_date) return 'none';
      const eve = new Date(p.exam_date + 'T12:00:00'); eve.setDate(eve.getDate() - 1);
      if (s === plan.iso(eve) || p.days[plan.dow(d)] !== '1') return 'rest';   // the day before is off
      if (!plan.testOf(p.minutes)) return 'practice';                        // no test fits the day
      if (p.tests === 'daily') return 'test';                                // a test every study day
      for (let k = plan.dow(d) + 1; k < 7; k++) if (p.days[k] === '1') return 'practice';
      return 'test';                                                         // the week's last study day
    },
  };

  /* a snapshot kept for one tab, so a page can animate from where it was */
  const snap = {
    get(k) { try { return JSON.parse(sessionStorage.getItem('satf.' + k) || 'null'); } catch (_) { return null; } },
    set(k, v) { try { sessionStorage.setItem('satf.' + k, JSON.stringify(v)); } catch (_) {} },
  };


  /* ------------------------------------------------------------ one settings row (R11)
     Label, helper, the control, and "Saved" or why it wasn't. It saves the moment it
     changes; a failed save puts the control back and says so. A key a mode or the exam
     stage sets says so, with the way back (U15). Controls are F1's kit components. */
  let registry = null;
  function prefRegistry() {
    if (!registry) {
      registry = (async () => {
        try { const c = JSON.parse(sget(SS(), 'satf.prefs.registry') || 'null'); if (Array.isArray(c)) return c; } catch (_) {}
        const list = await api('/prefs');
        sput(SS(), 'satf.prefs.registry', JSON.stringify(list));
        return list;
      })();
      registry.catch(() => { registry = null; });
    }
    return registry;
  }
  const STAGE = { learn: 'Learn', build: 'Build', test: 'Test-like', final: 'Final week' };
  const MODE = { learn: 'Learn', build: 'Build', test: 'Test-like', custom: 'Custom' };
  // ponytail: the keys prefs.BUNDLES sets, until GET /api/prefs marks them (F4)
  const BUNDLED = new Set(['clock', 'feedback', 'repairs', 'rationale', 'adaptive', 'tiers', 'confidence']);
  const why = e => e && e.offline ? 'offline' : e && e.status === 422 ? (e.detail || e.message) : 'try again';

  function prefRow(host, key, o = {}) {
    const row = h('div', { class: 'pref', 'data-pref': key });
    const k = h('span', { class: 'pref-k', text: o.label || '' });
    const help = h('p', { class: 'help', hidden: true });
    const src = h('p', { class: 'help pref-src', hidden: true });
    const stateEl = h('span', { class: 'pref-state', role: 'status' });
    const ctl = h('div', { class: 'pref-ctl' }, stateEl);
    row.append(k, help, src, ctl);
    if (host) host.append(row);
    if (!o.label) ctl.prepend(h('span', { class: 'skel', style: 'width: 140px; height: 32px', 'aria-hidden': 'true' }));
    let spec = null, value, control = null, clearTimer = 0;

    const say = (text, err) => {
      clearTimeout(clearTimer);
      stateEl.textContent = text;
      stateEl.classList.toggle('err', !!err);
      if (!err && text) clearTimer = setTimeout(() => { stateEl.textContent = ''; }, 4000);
    };
    function caption(profile) {
      const source = (profile ? profile.pref_source : shellData && shellData.pref_source) || {};
      const stage = profile ? profile.stage : shellData && shellData.stage;
      const p = (profile && profile.prefs) || prefs.now();
      const by = source[key];
      const bundle = stage && p.stage_auto !== false && STAGE[stage.name] ? STAGE[stage.name] : MODE[p.mode];
      src.replaceChildren();
      if (by === 'stage' || by === 'mode') src.append(`Set by ${by === 'stage' ? STAGE[stage && stage.name] || 'your stage' : MODE[p.mode] || 'your mode'}`);
      else if (by === 'yours' && (spec.bundled ?? BUNDLED.has(key)) && bundle && p.mode !== 'custom') {
        src.append('Yours · ', h('button', { type: 'button', class: 'quiet', text: `Back to ${bundle}`, onclick: () => save(null).then(v => set(v), () => {}) }));
      }
      src.hidden = !src.childNodes.length;
    }
    async function save(v) {
      say('Saving…');
      let pr;
      try { pr = await prefs.set({ [key]: v }); }
      catch (e) { say(`Not saved: ${why(e)}`, true); throw e; }
      value = pr.prefs[key];
      say('Saved');
      caption(pr);
      if (o.onChange) o.onChange(value);
      return value;
    }
    // every control calls this: save, and on failure put the control back
    const change = (v, back) => save(v).catch(() => back && back());
    const opts = () => (spec.values || []).map(x => ({ value: x.v, label: x.label }));
    const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

    function build() {
      ctl.replaceChildren(stateEl);
      const label = o.label || spec.label;
      const host2 = h('div', { class: 'pref-in' });
      const kind = spec.kind;
      if (kind === 'bool') {
        control = UI.switch(null, { checked: !!value, ariaLabel: label, onChange: v => save(v) });
        ctl.append(control.el);
      } else if ((kind === 'choice' || kind === 'subset') && opts().length <= (kind === 'subset' ? 7 : 4)) {
        const multi = kind === 'subset';
        control = UI.seg(host2, opts(), { value, multi, label, onChange: v => {
          if (multi && !v.length) { control.set(value, true); say('Pick at least one', true); return; }
          const old = value;
          change(v, () => control.set(old, true));
        } });
        ctl.append(host2);
      } else if (kind === 'choice' || kind === 'subset') {
        const multi = kind === 'subset';
        control = UI.dropdown(host2, { label, options: opts(), value, multi, all: multi ? 'None' : undefined, onChange: v => {
          if (multi && !v.length) { control.set(value, true); say('Pick at least one', true); return; }
          const old = value;
          change(v, () => control.set(old, true));
        } });
        ctl.append(host2);
      } else if (kind === 'words_goal') {
        const list = ['auto', 0, 5, 10, 20];
        if (!list.includes(value)) list.push(value);
        control = UI.seg(host2, list.map(v => ({ value: v, label: v === 'auto' ? 'Auto' : v === 0 ? 'Off' : String(v) })), {
          value, label, onChange: v => { const old = value; change(v, () => control.set(old, true)); } });
        ctl.append(host2);
      } else if (kind === 'int') {
        const [lo, hi] = spec.range || [spec.lo, spec.hi];
        const f = h('input', { class: 'field', type: 'number', inputmode: 'numeric', min: lo, max: hi, step: 1,
                               style: 'width: 96px', 'aria-label': label });
        f.value = value;
        f.addEventListener('change', () => {
          const v = Number(f.value);
          if (!Number.isInteger(v) || v < lo || v > hi) { say(`Not saved: ${lo} to ${hi}`, true); f.value = value; return; }
          const old = value;
          change(v, () => { f.value = old; });
        });
        control = { el: f };
        ctl.append(f);
      } else if (kind === 'time' || kind === 'date') {
        const f = h('input', { class: 'field', type: kind, 'aria-label': label, min: kind === 'date' ? localDay() : null });
        f.value = value || '';
        f.addEventListener('change', () => { const old = value; change(f.value || null, () => { f.value = old || ''; }); });
        ctl.append(f);
        if (spec.nullable !== false) ctl.append(h('button', { type: 'button', class: 'quiet', text: kind === 'time' ? 'Off' : 'Clear',
          onclick: () => { if (value === null) return; const old = value; f.value = ''; change(null, () => { f.value = old || ''; }); } }));
        control = { el: f };
      } else if (kind === 'quiet') {
        const v0 = value || { from: '21:30', to: '07:00' };
        const a = h('input', { class: 'field', type: 'time', 'aria-label': `${label} from` });
        const b = h('input', { class: 'field', type: 'time', 'aria-label': `${label} to` });
        a.value = v0.from; b.value = v0.to;
        const send = () => { if (!a.value || !b.value) return; const old = value; change({ from: a.value, to: b.value }, () => { a.value = (old || v0).from; b.value = (old || v0).to; }); };
        a.addEventListener('change', send); b.addEventListener('change', send);
        ctl.append(a, h('span', { text: 'to' }), b, h('button', { type: 'button', class: 'quiet', text: 'Off', onclick: () => change(null) }));
        control = { el: a };
      } else {
        ctl.append(h('span', { class: 'help', text: 'Changed where it is used' }));
      }
    }
    function set(v) {
      value = v;
      if (!control) return;
      if (control.set) control.set(v, true);
      else if (control.el && 'value' in control.el) control.el.value = v ?? '';
    }
    const ready_ = Promise.all([prefRegistry(), prefs()]).then(([list, p]) => {
      spec = list.find(x => x.key === key);
      if (!spec) throw new Error(`no pref ${key}`);
      value = p[key] !== undefined ? p[key] : spec.default;
      k.textContent = o.label || spec.label;
      const helper = o.helper ?? spec.helper;
      help.textContent = helper || '';
      help.hidden = !helper;
      build();
      caption();
    }).catch(e => {
      ctl.replaceChildren(stateEl);
      say('Couldn’t load this setting', true);
      ctl.append(h('button', { type: 'button', class: 'btn sm', text: 'Retry', onclick: () => { row.replaceWith(prefRow(null, key, o).el); } }));
      if (!k.textContent) k.textContent = key;
      console.warn(e);
    });
    const out = { el: row, ready: ready_, get value() { return value; }, set };
    row._pref = out;
    return out;
  }

  /* ------------------------------------------------------------ keys (R22, R43, §2.8)
     One registry. A scope is 'global', a page's own ('today', 'tests', 'report'...), or a
     question scope ('runner', 'player', 'pane', 'words'), whose keys are checked against
     UI.KEYS. Ignored while typing (Enter and Esc aside), while a dialog is open unless the
     scope is `within` it, and when prefs.keys is off. Sequences are "G T". */
  const MAC = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || '');
  const NAMED = { esc: 'Escape', escape: 'Escape', enter: 'Enter', return: 'Enter', space: 'Space', tab: 'Tab',
    left: 'ArrowLeft', right: 'ArrowRight', up: 'ArrowUp', down: 'ArrowDown', arrowleft: 'ArrowLeft', arrowright: 'ArrowRight',
    arrowup: 'ArrowUp', arrowdown: 'ArrowDown', '←': 'ArrowLeft', '→': 'ArrowRight', '↑': 'ArrowUp', '↓': 'ArrowDown',
    home: 'Home', end: 'End', pageup: 'PageUp', pagedown: 'PageDown', backspace: 'Backspace', delete: 'Delete' };
  const MODS = { mod: 'Mod', cmd: 'Mod', meta: 'Mod', ctrl: 'Mod', control: 'Mod', '⌘': 'Mod', alt: 'Alt', option: 'Alt', shift: 'Shift' };
  const ORDER = ['Mod', 'Alt', 'Shift'];
  function combo(s) {
    return String(s).trim().split(/\s+/).map(step => {
      const parts = step.length > 1 ? step.split('+') : [step];
      let key = parts.pop() || '+';
      const mods = new Set(parts.map(m => MODS[m.toLowerCase()] || m));
      key = NAMED[key.toLowerCase()] || (key.length === 1 ? key.toUpperCase() : key);
      return ORDER.filter(m => mods.has(m)).concat(key).join('+');
    }).join(' ');
  }
  function eventCombo(e) {
    let k = e.key;
    if (!k || k === 'Unidentified' || ['Shift', 'Control', 'Alt', 'Meta', 'CapsLock'].includes(k)) return null;
    if (k === ' ') k = 'Space';
    if (e.altKey && /^Key[A-Z]$/.test(e.code || '')) k = e.code.slice(3);     // Option types a symbol on a Mac
    if (e.altKey && /^Digit\d$/.test(e.code || '')) k = e.code.slice(5);
    const plain = k.length === 1 && /[a-z0-9]/i.test(k);
    if (k.length === 1) k = k.toUpperCase();
    const m = [];
    if (e.metaKey || e.ctrlKey) m.push('Mod');
    if (e.altKey) m.push('Alt');
    if (e.shiftKey && (plain || k.length > 1)) m.push('Shift');
    return m.concat(k).join('+');
  }
  const CAP = { Mod: MAC ? '⌘' : 'Ctrl', Alt: MAC ? '⌥' : 'Alt', Shift: MAC ? '⇧' : 'Shift', Escape: 'Esc', ArrowLeft: '←',
    ArrowRight: '→', ArrowUp: '↑', ArrowDown: '↓', Enter: 'Enter', Space: 'Space' };
  const keyLabel = c => combo(c).split(' ').map(step => step.split('+').map(x => CAP[x] || x).join(MAC ? '' : '+')).join(' ');
  const keycaps = c => combo(c).split(' ').flatMap(step => step.split('+').map(x => h('kbd', { class: 'kbd', text: CAP[x] || x })));

  const QSCOPES = new Set(['runner', 'player', 'pane', 'words']);
  const scopes = [];
  let warned = false;
  function fault(msg) {
    if (location.pathname.startsWith('/dev/')) throw new Error(msg);
    if (!warned) { warned = true; console.warn(msg); }
  }
  // R43 / G2: one key per action across the question scopes
  function check(scope, b) {
    const act = b.id || b.does;
    if (scopes.some(r => r.scope === scope && r.map.has(b.key))) fault(`key ${b.key} already in ${scope}`);
    if (!QSCOPES.has(scope)) return;
    const K = UI.KEYS || {}, except = K.except || {};
    const byKey = Object.keys(K).find(id => combo(K[id]) === b.key);
    if (b.id && K[b.id] && combo(K[b.id]) !== b.key) fault(`${b.id} is ${combo(K[b.id])}, not ${b.key}, in ${scope}`);
    if (byKey && byKey !== b.id && !(b.key in except)) fault(`${b.key} is ${byKey}, not ${act}, in ${scope}`);
    for (const r of scopes) {
      if (r.scope === scope || !QSCOPES.has(r.scope)) continue;
      const other = r.map.get(b.key);
      if (other && (other.id || other.does) !== act && !(b.key in except)) fault(`${b.key} is ${other.id || other.does} in ${r.scope} but ${act} in ${scope}`);
    }
  }
  function register(scope, map, o = {}) {
    const reg = { scope, label: o.label || (scope === 'global' ? 'Global' : 'This page'), within: o.within || null,
                  when: o.when || null, map: new Map() };
    for (const [k, v] of Object.entries(map || {})) {
      const b = typeof v === 'function' ? { run: v } : { ...v };
      b.key = combo(b.key || k);
      b.does = b.does || b.label || b.id || '';
      check(scope, b);
      reg.map.set(b.key, b);
    }
    scopes.push(reg);
    return { unregister() { const i = scopes.indexOf(reg); if (i >= 0) scopes.splice(i, 1); }, scope: reg };
  }
  const typingIn = el => !!el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));
  const topModal = () => [...doc.querySelectorAll('dialog[open]')].filter(d => { try { return d.matches(':modal'); } catch (_) { return true; } }).pop() || null;
  const keysOff = () => prefs.now().keys === false;
  function live() {
    const modal = topModal(), at = doc.activeElement;
    const inner = scopes.filter(r => r.within && r.within.isConnected && (r.within === modal || (!modal && r.within.contains(at)) || (modal && modal.contains(r.within) && r.within.contains(at))));
    const outer = modal ? [] : scopes.filter(r => !r.within && r.scope !== 'global').reverse();
    const glob = modal ? [] : scopes.filter(r => !r.within && r.scope === 'global');
    return inner.reverse().concat(outer, glob).filter(r => !r.when || r.when());
  }
  let pending = null, pendingAt = 0;
  function onKey(e) {
    if (e.defaultPrevented || e.isComposing) return;
    const c = eventCombo(e);
    if (!c) return;
    if (typingIn(e.target) && c !== 'Enter' && c !== 'Escape') return;
    // an open menu or listbox takes its own letters and arrows
    if (e.target.closest && e.target.closest('[role=menu], [role=listbox], [role=combobox]')) return;
    if (keysOff() && c !== 'Escape') return;
    const active = live();
    const find = k => { for (const r of active) { const b = r.map.get(k); if (b && (!b.when || b.when())) return b; } return null; };
    const seq = pending && Date.now() - pendingAt < 1500 ? `${pending} ${c}` : null;
    pending = null;
    const b = (seq && find(seq)) || find(c);
    if (b) {
      if (b.run(e) !== false) e.preventDefault();
      return;
    }
    if (c !== 'Escape' && active.some(r => [...r.map.keys()].some(k => k.startsWith(c + ' ')))) {
      pending = c; pendingAt = Date.now();
      e.preventDefault();
    }
  }
  doc.addEventListener('keydown', onKey);

  // the ? sheet: This page, then every other scope in play, then Global and the verbs
  function keysSheet() {
    if (!UI.sheet) return;
    const groups = new Map();
    const add = (label, b) => {
      if (b.hidden || (b.when && !b.when())) return;
      if (!groups.has(label)) groups.set(label, new Map());
      const rows = groups.get(label);
      const row = rows.get(b.does) || { does: b.does, keys: [] };
      row.keys.push(b.key);
      rows.set(b.does, row);
    };
    const inPlay = scopes.filter(r => !r.when || r.when());
    inPlay.filter(r => r.scope !== 'global').forEach(r => r.map.forEach(b => add(r.label, b)));
    inPlay.filter(r => r.scope === 'global').forEach(r => r.map.forEach(b => add('Global', b)));
    const table = rows => h('table', { class: 'table compact' }, h('tbody', {}, [...rows.values()].map(r =>
      h('tr', {}, h('td', { style: 'white-space: nowrap; width: 1%' }, r.keys.map((k, i) => [i ? h('span', { class: 'help', text: ' or ' }) : null, keycaps(k)])),
        h('td', { text: r.does })))));
    const verbs = UI.VERBS ? Object.values(UI.VERBS).filter(v => v.key) : [];
    UI.sheet({ title: 'Keyboard shortcuts', size: 'l', body: b => {
      if (keysOff()) b.append(h('p', { class: 'help', text: 'Keyboard shortcuts are off. Turn them on to use these.' }));
      const wrap = h('div', { style: 'columns: 2 300px; column-gap: 32px' });
      groups.forEach((rows, label) => wrap.append(h('section', { style: 'break-inside: avoid; margin-bottom: 20px' },
        h('h3', { class: 'k', text: label }), table(rows))));
      if (verbs.length) wrap.append(h('section', { style: 'break-inside: avoid; margin-bottom: 20px' },
        h('h3', { class: 'k', text: 'After a question' }),
        h('table', { class: 'table compact' }, h('tbody', {}, verbs.map(v => h('tr', {},
          h('td', { style: 'white-space: nowrap; width: 1%' }, keycaps(v.key)),
          h('td', {}, h('b', { text: v.label }), ` · ${v.sub}`, h('p', { class: 'help', text: v.helper }))))))));
      b.append(wrap);
      prefRow(b, 'keys', { label: 'Keyboard shortcuts' });
    } });
  }

  /* where the G-keys go (R1, §2.8); Review, Words and Compete are their sections' pages */
  const ROUTES = { today: '/', practice: '/practice/', review: '/review/', words: '/words/', tests: '/tests/',
    plan: '/plan/', results: '/results/', compete: '/compete/', me: '/me/', settings: '/me/settings/', help: '/help/' };
  const page = () => doc.body && doc.body.dataset.page || '';
  const chrome = () => keys.chrome === true;
  const goTo = href => () => { location.href = href; };
  const keys = { register, sheet: keysSheet, label: keyLabel, caps: keycaps, combo, chrome: false };
  const G = [['T', 'today', 'Today'], ['P', 'practice', 'Practice'], ['M', 'review', 'Review'], ['W', 'words', 'Words'],
    ['E', 'tests', 'Tests'], ['L', 'plan', 'Plan'], ['R', 'results', 'Results'], ['C', 'compete', 'Compete'],
    ['U', 'me', 'Profile'], ['S', 'settings', 'Settings'], ['H', 'help', 'Help & FAQ']];
  register('global', {
    ...Object.fromEntries(G.map(([k, id, name]) => [`G ${k}`, { does: `Go to ${name}`, run: goTo(ROUTES[id]), when: chrome }])),
    'G N': { does: 'Start Up next', run: () => { startNext(); }, when: chrome },
    Q: { does: 'Quick question · Log a mistake · Add a word', run: () => UI.quick(), when: () => typeof UI.quick === 'function' && page() !== 'test' },
    'Mod+K': { does: 'Search', run: () => UI.palette(), when: () => typeof UI.palette === 'function' && chrome() },
    '/': { does: 'Search', run: () => UI.palette(), when: () => typeof UI.palette === 'function' && chrome() },
    '[': { does: 'Collapse or expand the sidebar', run: () => UI.shell.toggle(), when: () => chrome() && typeof (UI.shell && UI.shell.toggle) === 'function' },
    Z: { does: 'Undo the last change', run: () => (UI.toast && UI.toast.undo ? UI.toast.undo() : false) },
    '?': { does: 'Keyboard shortcuts', run: () => keysSheet() },
  });

  /* ------------------------------------------------------------ Up next (U1) */
  function nextItems() {
    let snooze = {};
    try { snooze = JSON.parse(sget(LS(), 'satf.next.snooze') || '{}') || {}; } catch (_) {}
    const day = localDay();
    return ((shellData && shellData.next) || []).filter(x => snooze[x.key] !== day);
  }
  async function start(item) {
    if (!item) return;
    if (item.href) { location.href = item.href; return; }
    if (!item.start) return;
    const path = String(item.start.path || '/drill').replace(/^\/api(?=\/)/, '');
    const r = await api(path, { method: 'POST', body: item.start.body || {} });
    location.href = r.href || `/practice/session/?id=${encodeURIComponent(r.id)}`;
  }
  async function startNext() {
    if (!shellData) await (shellAsked || refresh()).catch(() => null);
    const item = nextItems()[0];
    if (!item) { if (UI.toast) UI.toast('Nothing is up next right now.'); return; }
    try { await start(item); } catch (e) { if (UI.toast && !e.offline) UI.toast('Couldn’t start it. Try again.'); }
  }

  /* ------------------------------------------------------------ skip link (Shell 2)
     The first Tab stop on every page with a <main>: "Skip to content", moving focus there. */
  function skip() {
    const main = doc.querySelector('main');
    if (!main || doc.querySelector('a.skip')) return;
    if (!main.id) main.id = 'main';
    if (!main.hasAttribute('tabindex')) main.tabIndex = -1;
    const a = h('a', { class: 'skip', href: '#' + main.id, text: 'Skip to content' });
    a.addEventListener('click', e => { e.preventDefault(); main.focus(); });
    doc.body.prepend(a);
  }

  /* shared computer (U21): a visible page keeps the session alive; closing the last tab
     ends it within a minute (the endpoints are S1's) */
  ready.then(() => {
    if (!shared || !String(memo).startsWith('d:')) return;
    const ping = () => { if (doc.visibilityState === 'visible') api('/devices/this/ping', { method: 'POST', quiet: true }).catch(() => {}); };
    whenVisible(ping);
    setInterval(ping, 5 * 60 * 1000);
    addEventListener('pagehide', () => { try { fetch('/api/devices/this/leaving', { method: 'POST', keepalive: true, headers: headers() }); } catch (_) {} });
  });

  /* ------------------------------------------------------------ the shell
     The old top bar and phone tabs, kept until the sidebar lands; it reads /api/shell. */
  const NAV = [
    ['today', '/', 'Today'],
    ['practice', '/practice/', 'Practice'],
    ['tests', '/tests/', 'Tests'],
    ['plan', '/plan/', 'Plan'],
    ['results', '/results/', 'Results'],
  ];
  const SECTION = { session: 'practice', mistakes: 'practice', report: 'results', challenge: 'today', diagnostic: 'tests' };

  function shell() {
    const page = doc.body.dataset.page || '';
    const here = SECTION[page] || page;
    keys.chrome = true;
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
    if (!storable) {
      const main = doc.querySelector('main');
      main && main.prepend(h('p', { class: 'error', style: 'margin-bottom:16px', text: 'This browser is blocking site data, so nothing here can be kept.' }));
    }
    const av = $('#avatar');
    if (av) av.innerHTML = mark(16, 'var(--soft)');
    onShell(paintBar);
    if (!shellAsked) refresh();
  }
  function paintBar(d) {
    const av = $('#avatar'), st = $('#streak');
    if (av && d.me && d.me.name) av.textContent = d.me.name.trim()[0].toUpperCase();
    if (st) {
      st.hidden = !d.answered;
      st.classList.toggle('on', d.streak > 0);
      st.querySelector('span').textContent = d.streak;
      st.setAttribute('aria-label', `${d.streak} day streak`);
    }
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
    const status = h('p', { class: 'sr', role: 'status' });
    let answered = false;
    const api_ = { answered: () => answered, reveal, choose: null, unlock: () => {} };

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
      // the answer did not reach the server, so it can be given again
      api_.unlock = () => { answered = false; buttons.forEach(b => b.classList.remove('picked')); list.classList.remove('done'); };
    } else {
      // no inputmode: a phone's decimal pad has no minus sign and no slash
      const input = h('input', { class: 'field', type: 'text', autocomplete: 'off', autocapitalize: 'off',
                                 autocorrect: 'off', spellcheck: 'false', maxlength: '6', 'aria-label': 'Your answer',
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
      api_.unlock = () => { answered = false; input.readOnly = false; go.hidden = false; input.focus(); };
      setTimeout(() => { if (!answered && matchMedia('(hover: hover)').matches) input.focus({ preventScroll: true }); }, 60);
    }
    host.append(verdict, status);

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
      status.textContent = fb.correct ? 'Right' : `Wrong. The answer is ${String(fb.answer).replace(/-/g, '−')}`;
      if (q.type === 'mcq') {
        api_.buttons[fb.answer_index]?.append(h('span', { class: 'sr', text: ', the answer' }));
        if (!fb.correct && Number.isInteger(fb.given)) api_.buttons[fb.given]?.append(h('span', { class: 'sr', text: ', your answer' }));
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


  /* ------------------------------------------------------------ start */
  if (doc.body) skip(); else doc.addEventListener('DOMContentLoaded', skip);

  /* ------------------------------------------------------------ export */
  Object.assign(UI, {
    learner, useLearner, freshLearner, shared: () => shared, stored: () => storable, ready,
    api, cached, whenVisible, refresh, onShell, shellData: () => shellData, me, prefs, prefRow, look,
    keys, ROUTES, start, nextItems, skip,
    h, s, svg, mark, ICON, TOPICS, TOPIC, DOMAINS, glyph, chip,
    question, calc, ref, shell, snap, mmss, minutesFor, day, cap, band, reduced, plan, $,
  });
})();
