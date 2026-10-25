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
                                    GET /api/shell, painted from sessionStorage satf.shell first;
                                    it sets UI.answered and UI.SAT_DATES
     UI.me(fresh)                   GET /api/me, once per page
     UI.prefs() -> Promise          every pref, defaults merged; UI.prefs.now(), UI.prefs.set()
     UI.prefRow(host, key, {label, helper, onChange})   one settings row that saves instantly
     UI.look(prefs)                 theme, text size and motion, mirrored to satf.look
     UI.keys.register(scope, map, {label, within, when}) -> {unregister}
                                    map: {'G T': fn | {does, run, id, when}}; UI.keys.sheet()
                                    opens the ? sheet; UI.keys.label(combo)
     UI.ROUTES, UI.start(item), UI.nextItems()   where G-keys go; start an Up next item
     UI.run.start(), UI.run.between(host, done, next, {onStop}), UI.run.rail(host, {current})
                                    the day as one run over the Up next queue (G1); ?run=1;
                                    UI.run.on(cfg.run), .label(), .parts(), .state()
     UI.autoSheet(open) -> Promise<sheet | null>   a sheet that opens by itself (U25)
     UI.share(q, {anchor}) -> Promise<url | null>  Send to a friend: a twin by default (U28)
     UI.notify.on(kinds) / .off() / .sub() / .ok() / .offer(time)   push on this device (U18b):
                                    registers /sw.js and asks the browser, from a tap only
     UI.skip()                      the skip link, first on every page with a <main>
   The chrome (Shell 2-2.6, R1, U1, U25, U26):
     UI.shell(page | {page, sections, now, nowBlock, chrome, ownPrimary}) or UI.shell(page, {...})   the sidebar, rail and overlay, the phone top bar,
                                    tabs, grip and hold menus, the Now strip and the section bar,
                                    every meta from /api/shell; UI.shell.toggle() is [ (a click glides it);
                                    chrome: 'focus' (Sign in, Welcome, Pair) draws only a slim brand bar
                                    (mark and wordmark home, Help, the account menu) and sets body.has-focus;
                                    ownPrimary: true (a page whose hero carries its own orange Start: Practice,
                                    Today, Tests) makes the Now strip's, the sidebar's and the section bar's Up next Start a .btn,
                                    so the page shows one orange button (the menu sheet's stays orange)
     Motion here (premium/MOTION.md): the current nav item's .nav-mark and tab's .tab-mark slide on a page
                                    change; the rail collapse and the Now card fold glide (UI.motion.vt);
                                    keycaps flash when their shortcut fires; details.fold and a
                                    .card[data-collapsed] grow open; the sidebar's ring, meter and streak
                                    move when fresh data changes them
     UI.NAV, UI.SECTION             the nine items and the page -> item mapping
     UI.nowStrip(host)              Up next and the Today card as a block (Today places its own
                                    and passes {now: false})
     UI.sections([{id, label}])     the section bar's chips, with scroll-spy; they wait until the page's header has
                                    scrolled away and fade in as the bar sticks (UI.shell({sectionsAlways: true}):
                                    from the top); a chip that gets focus brings them out at once
     UI.menuSheet(trigger)          the phone's menu sheet; UI.accountMenu() the account items
     UI.signOut()                   sign out (saved: Undo for 8 s; shared computer: at once) or,
                                    unsaved, the Leave this device dialog
     UI.quick, UI.palette, UI.report, UI.continueOnPhone   load quick.js, palette.js,
                                    report.js, qr.js on first use; UI.need(file) loads any
     Banners (Shell 2.11, U15, U17, U19): retired and offline from UI.api, storage blocked,
                                    then one of registration deadline, stage change, first
                                    visit (satf.first), save nudge (satf.nudge, 7 days)
     Event toasts (Shell 2.11, U25): achievements and report replies from fresh shell data,
                                    at most 2 a load, each once a tab (satf.toasted), marked seen
   Search and quick (Shell 2.7, 2.8, P15):
     UI.ALIASES                     the words that also name a skill, beside TOPICS
     UI.parseSet(text, {count, types, source}) -> {body, chips, unknown, text, any, box}
                                    "circles hard 5 timed" -> a POST /api/drill body
     UI.types() -> Promise {list, byTopic, cb}   the 386 question types with their named
                                    mistakes, from /api/shell/catalog (sessionStorage satf.types.2)
     UI.boxChips(onTile, [minutes])  "Got time? 5 · 10 · 15 … min", each starting a time box
   Kept for the pages until they are rebuilt: UI.question, UI.calc, UI.ref, UI.plan,
   UI.snap, the topics and glyphs.
   Icons (premium A3, Phosphor): UI.ICON[name] inner strings for UI.svg(inner, size); UI.icon(name, size) -> svg
   node ('' and a warning on localhost for an unknown name); UI.ICON_FILL the fills alone; UI.spotArt(kind, ms)
   -> svg string for an empty state ('start', 'clear', 'lost', 'done' with the four masteries 0..1).
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
  // false when localStorage refuses (the storage-blocked banner, Shell 2.11): sessionStorage
  // alone keeps the code for this tab only, so closing it would lose the progress
  const storable = sput(LS(), 'satf.t', '1') && sput(LS(), 'satf.t', null);

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
      Object.assign(e, { status: r.status, data, detail: d, retired: !!(r.status === 401 && d && d.retired), signin: !!(r.status === 401 && d && d.signin) });
      if (e.retired) retired();
      if (e.signin) toSignin();
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

  /* email-only access (2026-10-20): a browser that never signed in has no learner on the server,
     which answers 401 {signin}; every page but Sign in, Help and a tutor's progress link sends it there, then back */
  function toSignin() {
    if (/^\/(signin|help|share)\//.test(location.pathname)) return;
    location.replace('/signin/?go=' + encodeURIComponent(location.pathname + location.search + location.hash));
  }
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
    if (d && d.signin) { toSignin(); return; }
    shellData = d;
    UI.answered = d.answered;
    // upcoming official dates with their deadlines, for every date picker (R15)
    if (Array.isArray(d.dates)) UI.SAT_DATES = d.dates.map(x => ({ date: x.day, ...x }));
    shellSubs.slice().forEach(fn => { try { fn(d, fromCache); } catch (e) { console.error(e); } });
  }
  function refresh() {
    const first = !shellAsked;
    shellAt = Date.now();
    // the look follows every fresh copy, changed or not, never a cached one
    shellAsked = cached('/shell', takeShell, { key: 'satf.shell', fresh: !first,
                                              onFresh: d => {
                                                if (d && d.prefs) look(d.prefs, true);
                                                // every fresh copy, changed or not, and before the event toasts, so they wait for it
                                                if (shellOn) whenVisible(() => autoSheets(d));
                                              } });
    shellAsked.catch(() => {});
    return shellAsked;
  }
  // another section's route or file exists (/api/shell.has): ask nothing that would 404
  const has = name => !!(shellData && shellData.has && shellData.has[name]);
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

  /* ------------------------------------------------------------ the mark
     A rounded square with four gaps cut mid-edge: one corner, rotated. */
  const CORNER = 'M45 8 H30 A22 22 0 0 0 8 30 V45 H34 V41 A7 7 0 0 1 41 34 H45 Z';
  const mark = (size = 26, fill = '#F18508') =>
    `<svg width="${size}" height="${size}" viewBox="0 0 100 100" role="img" aria-label="SAT Freshman"><g fill="${fill}">${
      [0, 90, 180, 270].map(a => `<path d="${CORNER}"${a ? ` transform="rotate(${a} 50 50)"` : ''}/>`).join('')}</g></svg>`;

  /* SPOT: the mark's four corners as the only illustration (ICONS.md 9). UI.spotArt(kind[, ms]) returns an svg
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

  /* ------------------------------------------------------------ icons (premium build A3, 2026-10-19)
     Drop-in for ui.js's `const ICON = {...}` block (ui.js:438-476). Same call shape: every entry is still
     an inner string for a 24 viewBox, so svg(ICON.x, 18), UI.svg(UI.ICON.x, n) and kit's icon('x') work as
     they are. Every name ui.js, kit.js, runner.js, question.js, words-ui.js, compete-ui.js and contest.js
     draw today is here, plus the missing ones (more, compete, grip, phone, link, calendar_check, caret_*).

     Source: Phosphor Icons, github.com/phosphor-icons/core, raw/regular and raw/fill at commit
     2b75f3ad12b420c9504ef05df8d2564a28f8500e (package 2.1.1). MIT licence, Copyright (c) 2023 Phosphor
     Icons: web/assets/LICENSE-phosphor.txt. Ours, on the same weight rule: dot, eliminate, strikes (24 grid),
     twin_test (Phosphor copy plus a small timer, 256 grid).

     Markup: Phosphor entries sit in <g class="ph" transform="scale(.09375)"> (256 to 24). The one
     stroke-width="16" on that g is only a no-CSS fallback; icons.css sets the real width (1.4px, held in
     screen pixels). No element carries its own stroke-width, so the old duplicate attributes are gone (bug 1).
     Round 3 (same source and commit): external (arrow-up-right; a link that leaves the app, after its text),
     key, envelope, fingerprint, shield and medal (twins; key's dot filled like ours).
     Twins (nine nav items, note, bell, moon, key, envelope, fingerprint, shield, medal; flag, bookmark, star
     in amber): the entry holds two layers,
     <g class="ph ph-f" opacity="0">fill</g><g class="ph ph-o">outline</g>; icons.css shows the fill under
     aria-current, aria-pressed="true", aria-checked="true" or a selected tab. ICON_FILL holds the fills alone.
     flame keeps one layer with class="flame" on its outline (ui.css:413 fills it, ui.js:1545 looks it up).

     Names that do not exist in UI.ICON today: more (index.html:1246 falls back to a local copy).
     Names whose meaning changes, so the caller must switch: question.js `chev` (down) -> caret_down;
     words-ui.js `left`/`right` (carets) -> caret_left/caret_right (here left/right are arrows, as in
     runner.js); ui.js:1426 NAV compete `trophy` -> compete; ui.js:2100 "Save your progress" `dot` -> save. */

  const PHF = {
    today:    '<path d="M208,32H184V24a8,8,0,0,0-16,0v8H88V24a8,8,0,0,0-16,0v8H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM128,168a16,16,0,1,1,16-16A16,16,0,0,1,128,168Zm80-88H48V48H72v8a8,8,0,0,0,16,0V48h80v8a8,8,0,0,0,16,0V48h24Z"/>',
    practice: '<path d="M120,56v48a16,16,0,0,1-16,16H56a16,16,0,0,1-16-16V56A16,16,0,0,1,56,40h48A16,16,0,0,1,120,56Zm80-16H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V56A16,16,0,0,0,200,40Zm-96,96H56a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,104,136Zm96,0H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,200,136Z"/>',
    review:   '<path d="M224,128A96,96,0,0,1,62.11,197.82a8,8,0,1,1,11-11.64A80,80,0,1,0,71.43,71.43C67.9,75,64.58,78.51,61.35,82L77.66,98.34A8,8,0,0,1,72,112H32a8,8,0,0,1-8-8V64a8,8,0,0,1,13.66-5.66L50,70.7c3.22-3.49,6.54-7,10.06-10.55A96,96,0,0,1,224,128ZM128,72a8,8,0,0,0-8,8v48a8,8,0,0,0,3.88,6.86l40,24a8,8,0,1,0,8.24-13.72L136,123.47V80A8,8,0,0,0,128,72Z"/>',
    words:    '<rect x="24" y="72" width="176" height="144" rx="16"/><path d="M216,40H64a8,8,0,0,0,0,16H216V176a8,8,0,0,0,16,0V56A16,16,0,0,0,216,40Z"/>',
    tests:    '<path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Zm32,128H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Zm0-32H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Z"/>',
    plan:     '<path d="M228,200a28,28,0,0,1-54.83,8H72a48,48,0,0,1,0-96h96a24,24,0,0,0,0-48H72a8,8,0,0,1,0-16h96a40,40,0,0,1,0,80H72a32,32,0,0,0,0,64H173.17A28,28,0,0,1,228,200Z"/>',
    results:  '<path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM200,192H56a8,8,0,0,1-8-8V72a8,8,0,0,1,16,0v76.69l34.34-34.35a8,8,0,0,1,11.32,0L128,132.69,172.69,88H144a8,8,0,0,1,0-16h48a8,8,0,0,1,8,8v48a8,8,0,0,1-16,0V99.31l-50.34,50.35a8,8,0,0,1-11.32,0L104,131.31l-40,40V176H200a8,8,0,0,1,0,16Z"/>',
    compete:  '<path d="M240,200h-8V144a16,16,0,0,0-16-16H176V56a16,16,0,0,0-16-16H96A16,16,0,0,0,80,56V88H40a16,16,0,0,0-16,16v96H16a8,8,0,0,0,0,16H240a8,8,0,0,0,0-16ZM80,200H40V104H80Zm60-64a8,8,0,0,1-16,0V107.1l-1.47.49a8,8,0,0,1-5.06-15.18l12-4A8,8,0,0,1,140,96Zm76,64H176V144h40Z"/>',
    profile:  '<path d="M172,120a44,44,0,1,1-44-44A44.05,44.05,0,0,1,172,120Zm60,8A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88.09,88.09,0,0,0-91.47-87.93C77.43,41.89,39.87,81.12,40,128.25a87.65,87.65,0,0,0,22.24,58.16A79.71,79.71,0,0,1,84,165.1a4,4,0,0,1,4.83.32,59.83,59.83,0,0,0,78.28,0,4,4,0,0,1,4.83-.32,79.71,79.71,0,0,1,21.79,21.31A87.62,87.62,0,0,0,216,128Z"/>',
    note:     '<path d="M224,128v80a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V48A16,16,0,0,1,48,32h80a8,8,0,0,1,0,16H48V208H208V128a8,8,0,0,1,16,0Zm5.66-58.34-96,96A8,8,0,0,1,128,168H96a8,8,0,0,1-8-8V128a8,8,0,0,1,2.34-5.66l96-96a8,8,0,0,1,11.32,0l32,32A8,8,0,0,1,229.66,69.66Zm-17-5.66L192,43.31,179.31,56,200,76.69Z"/>',
    bell:     '<path d="M168,224a8,8,0,0,1-8,8H96a8,8,0,1,1,0-16h64A8,8,0,0,1,168,224Zm53.81-48.06C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H208a16,16,0,0,0,13.8-24.06Z"/>',
    moon:     '<path d="M235.54,150.21a104.84,104.84,0,0,1-37,52.91A104,104,0,0,1,32,120,103.09,103.09,0,0,1,52.88,57.48a104.84,104.84,0,0,1,52.91-37,8,8,0,0,1,10,10,88.08,88.08,0,0,0,109.8,109.8,8,8,0,0,1,10,10Z"/>',
    flag:     '<path d="M232,56V176a8,8,0,0,1-2.76,6c-15.28,13.23-29.89,18-43.82,18-18.91,0-36.57-8.74-53-16.85C105.87,170,82.79,158.61,56,179.77V224a8,8,0,0,1-16,0V56a8,8,0,0,1,2.77-6h0c36-31.18,68.31-15.21,96.79-1.12C167,62.46,190.79,74.2,218.76,50A8,8,0,0,1,232,56Z"/>',
    bookmark: '<path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Z"/>',
    star:     '<path d="M234.29,114.85l-45,38.83L203,211.75a16.4,16.4,0,0,1-24.5,17.82L128,198.49,77.47,229.57A16.4,16.4,0,0,1,53,211.75l13.76-58.07-45-38.83A16.46,16.46,0,0,1,31.08,86l59-4.76,22.76-55.08a16.36,16.36,0,0,1,30.27,0l22.75,55.08,59,4.76a16.46,16.46,0,0,1,9.37,28.86Z"/>',
    flame:    '<path d="M143.38,17.85a8,8,0,0,0-12.63,3.41l-22,60.41L84.59,58.26a8,8,0,0,0-11.93.89C51,87.53,40,116.08,40,144a88,88,0,0,0,176,0C216,84.55,165.21,36,143.38,17.85Zm40.51,135.49a57.6,57.6,0,0,1-46.56,46.55A7.65,7.65,0,0,1,136,200a8,8,0,0,1-1.32-15.89c16.57-2.79,30.63-16.85,33.44-33.45a8,8,0,0,1,15.78,2.68Z"/>',
    play:     '<path d="M240,128a15.74,15.74,0,0,1-7.6,13.51L88.32,229.65a16,16,0,0,1-16.2.3A15.86,15.86,0,0,1,64,216.13V39.87a15.86,15.86,0,0,1,8.12-13.82,16,16,0,0,1,16.2.3L232.4,114.49A15.74,15.74,0,0,1,240,128Z"/>',
    key:      '<path d="M216.57,39.43A80,80,0,0,0,83.91,120.78L28.69,176A15.86,15.86,0,0,0,24,187.31V216a16,16,0,0,0,16,16H72a8,8,0,0,0,8-8V208H96a8,8,0,0,0,8-8V184h16a8,8,0,0,0,5.66-2.34l9.56-9.57A79.73,79.73,0,0,0,160,176h.1A80,80,0,0,0,216.57,39.43ZM180,92a16,16,0,1,1,16-16A16,16,0,0,1,180,92Z"/>',
    envelope: '<path d="M224,48H32a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A8,8,0,0,0,224,48ZM98.71,128,40,181.81V74.19Zm11.84,10.85,12,11.05a8,8,0,0,0,10.82,0l12-11.05,58,53.15H52.57ZM157.29,128,216,74.18V181.82Z"/>',
    fingerprint: '<path d="M126.42,24C70.73,24.85,25.21,70.09,24,125.81a103.53,103.53,0,0,0,13.52,53.54,4,4,0,0,0,7.1-.3,119.35,119.35,0,0,0,11.37-51A71.77,71.77,0,0,1,83,71.83a8,8,0,1,1,9.86,12.61A55.82,55.82,0,0,0,72,128.07a135.28,135.28,0,0,1-18.45,68.35,4,4,0,0,0,.61,4.85c2,2,4.09,4,6.25,5.82a4,4,0,0,0,6-1A151.18,151.18,0,0,0,85,158.49a8,8,0,1,1,15.68,3.19,167.33,167.33,0,0,1-21.07,53.64,4,4,0,0,0,1.6,5.63c2.47,1.25,5,2.41,7.57,3.47a4,4,0,0,0,5-1.61A183,183,0,0,0,120,128.28a8.16,8.16,0,0,1,7.44-8.21,8,8,0,0,1,8.56,8,198.94,198.94,0,0,1-25.21,97.16,4,4,0,0,0,2.95,5.92q4.55.63,9.21.86a4,4,0,0,0,3.67-2.1A214.88,214.88,0,0,0,152,128.8c.05-13.25-10.3-24.49-23.54-24.74A24,24,0,0,0,104,128a8.1,8.1,0,0,1-7.29,8,8,8,0,0,1-8.71-8,40,40,0,0,1,40.42-40c22,.23,39.68,19.17,39.57,41.16a231.37,231.37,0,0,1-20.52,94.57,4,4,0,0,0,4.62,5.51,103.49,103.49,0,0,0,10.26-3,4,4,0,0,0,2.35-2.22,243.76,243.76,0,0,0,11.48-34,8,8,0,1,1,15.5,4q-1.12,4.37-2.4,8.7a4,4,0,0,0,6.46,4.17A104,104,0,0,0,126.42,24ZM198,161.08a8,8,0,0,1-7.92,7,8.39,8.39,0,0,1-1-.06,8,8,0,0,1-6.95-8.93,252.57,252.57,0,0,0,1.92-31,56.08,56.08,0,0,0-56-56,56.78,56.78,0,0,0-7,.43,8,8,0,0,1-2-15.89,72.1,72.1,0,0,1,81,71.49A266.93,266.93,0,0,1,198,161.08Z"/>',
    shield:   '<path d="M224,56v56c0,52.72-25.52,84.67-46.93,102.19-23.06,18.86-46,25.27-47,25.53a8,8,0,0,1-4.2,0c-1-.26-23.91-6.67-47-25.53C57.52,196.67,32,164.72,32,112V56A16,16,0,0,1,48,40H208A16,16,0,0,1,224,56Z"/>',
    medal:    '<path d="M216,96A88,88,0,1,0,72,163.83V240a8,8,0,0,0,11.58,7.16L128,225l44.43,22.21A8.07,8.07,0,0,0,176,248a8,8,0,0,0,8-8V163.83A87.85,87.85,0,0,0,216,96ZM56,96a72,72,0,1,1,72,72A72.08,72.08,0,0,1,56,96Zm16,0a56,56,0,1,1,56,56A56.06,56.06,0,0,1,72,96Z"/>',
  };
  const PH = 'transform="scale(.09375)"';     // Phosphor's 256 grid inside our 24 viewBox
  const ph = (s, c = '') => `<g class="ph${c}" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="16" ${PH}>${s}</g>`;
  const phf = (s, c = '') => `<g class="ph${c}" fill="currentColor" ${PH}>${s}</g>`;
  // a twin: the fill (hidden until active, icons.css) under the outline; amber for the status toggles
  const twin = (n, s, amber) => `<g class="ph ph-f${amber ? ' ph-amber' : ''}" fill="currentColor" opacity="0" ${PH}>${PHF[n]}</g>` + ph(s, ' ph-o');
  const ICON = {
    today:          twin('today', '<rect x="40" y="40" width="176" height="176" rx="8"/><line x1="176" y1="24" x2="176" y2="56"/><line x1="80" y1="24" x2="80" y2="56"/><line x1="40" y1="88" x2="216" y2="88"/><circle cx="128" cy="152" r="16" fill="currentColor" stroke="none"/>'),
    practice:       twin('practice', '<rect x="48" y="48" width="64" height="64" rx="8"/><rect x="144" y="48" width="64" height="64" rx="8"/><rect x="48" y="144" width="64" height="64" rx="8"/><rect x="144" y="144" width="64" height="64" rx="8"/>'),
    review:         twin('review', '<polyline points="128 80 128 128 168 152"/><polyline points="72 104 32 104 32 64"/><path d="M67.6,192A88,88,0,1,0,65.77,65.77C54,77.69,44.28,88.93,32,104"/>'),
    words:          twin('words', '<rect x="32" y="80" width="160" height="128" rx="8"/><path d="M64,48H216a8,8,0,0,1,8,8V176"/>'),
    tests:          twin('tests', '<line x1="96" y1="152" x2="160" y2="152"/><line x1="96" y1="120" x2="160" y2="120"/><path d="M160,40h40a8,8,0,0,1,8,8V216a8,8,0,0,1-8,8H56a8,8,0,0,1-8-8V48a8,8,0,0,1,8-8H96"/><path d="M88,72V64a40,40,0,0,1,80,0v8Z"/>'),
    plan:           twin('plan', '<circle cx="200" cy="200" r="24"/><path d="M72,56h96a32,32,0,0,1,0,64H72a40,40,0,0,0,0,80H176"/>'),
    results:        twin('results', '<polyline points="224 208 32 208 32 48"/><polyline points="200 72 128 144 96 112 32 176"/><polyline points="200 112 200 72 160 72"/>'),
    compete:        twin('compete', '<path d="M32,208V104a8,8,0,0,1,8-8H88"/><path d="M88,208V56a8,8,0,0,1,8-8h64a8,8,0,0,1,8,8V208"/><path d="M224,208V144a8,8,0,0,0-8-8H168"/><polyline points="120 100 132 96 132 136"/><line x1="16" y1="208" x2="240" y2="208"/>'),
    profile:        twin('profile', '<circle cx="128" cy="128" r="96"/><circle cx="128" cy="120" r="40"/><path d="M63.8,199.37a72,72,0,0,1,128.4,0"/>'),
    note:           twin('note', '<polygon points="128 160 96 160 96 128 192 32 224 64 128 160"/><line x1="168" y1="56" x2="200" y2="88"/><path d="M216,128v80a8,8,0,0,1-8,8H48a8,8,0,0,1-8-8V48a8,8,0,0,1,8-8h80"/>'),
    bell:           twin('bell', '<line x1="96" y1="224" x2="160" y2="224"/><path d="M56,104a72,72,0,0,1,144,0c0,35.82,8.3,64.6,14.9,76A8,8,0,0,1,208,192H48a8,8,0,0,1-6.88-12C47.71,168.6,56,139.81,56,104Z"/>'),
    moon:           twin('moon', '<path d="M108.11,28.11A96.09,96.09,0,0,0,227.89,147.89,96,96,0,1,1,108.11,28.11Z"/>'),
    flag:           twin('flag', '<line x1="48" y1="224" x2="48" y2="56"/><path d="M48,176c64-55.43,112,55.43,176,0V56C160,111.43,112,.57,48,56"/>', 1),
    bookmark:       twin('bookmark', '<path d="M192,224l-64-40L64,224V48a8,8,0,0,1,8-8H184a8,8,0,0,1,8,8Z"/>', 1),
    star:           twin('star', '<path d="M128,189.09l54.72,33.65a8.4,8.4,0,0,0,12.52-9.17l-14.88-62.79,48.7-42A8.46,8.46,0,0,0,224.27,94L160.36,88.8,135.74,29.2a8.36,8.36,0,0,0-15.48,0L95.64,88.8,31.73,94a8.46,8.46,0,0,0-4.79,14.83l48.7,42L60.76,213.57a8.4,8.4,0,0,0,12.52,9.17Z"/>', 1),
    flame:          ph('<path class="flame" d="M112,96l26.27-72C159.86,41.92,208,88.15,208,144a80,80,0,0,1-160,0c0-30.57,14.42-58.26,31-80Z"/><path d="M136,192c20-3.37,36.61-20,40-40"/>'),
    play:           phf(PHF.play),
    x:              ph('<line x1="200" y1="56" x2="56" y2="200"/><line x1="200" y1="200" x2="56" y2="56"/>'),
    check:          ph('<polyline points="40 144 96 200 224 72"/>'),
    plus:           ph('<line x1="40" y1="128" x2="216" y2="128"/><line x1="128" y1="40" x2="128" y2="216"/>'),
    arrow:          ph('<line x1="40" y1="128" x2="216" y2="128"/><polyline points="144 56 216 128 144 200"/>'),
    right:          ph('<line x1="40" y1="128" x2="216" y2="128"/><polyline points="144 56 216 128 144 200"/>'),
    left:           ph('<line x1="216" y1="128" x2="40" y2="128"/><polyline points="112 56 40 128 112 200"/>'),
    chev:           ph('<polyline points="96 48 176 128 96 208"/>'),
    caret_right:    ph('<polyline points="96 48 176 128 96 208"/>'),
    caret_left:     ph('<polyline points="160 208 80 128 160 48"/>'),
    caret_down:     ph('<polyline points="208 96 128 176 48 96"/>', ' ph-turn'),
    caret_up:       ph('<polyline points="48 160 128 80 208 160"/>'),
    up:             ph('<polyline points="48 160 128 80 208 160"/>'),
    down:           ph('<polyline points="208 96 128 176 48 96"/>'),
    skip:           ph('<polyline points="56 48 136 128 56 208"/><polyline points="136 48 216 128 136 208"/>'),
    more:           ph('<circle cx="128" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="196" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="60" cy="128" r="12" fill="currentColor" stroke="none"/>'),
    dots:           ph('<circle cx="128" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="196" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="60" cy="128" r="12" fill="currentColor" stroke="none"/>'),
    grip:           ph('<circle cx="92" cy="60" r="12" fill="currentColor" stroke="none"/><circle cx="164" cy="60" r="12" fill="currentColor" stroke="none"/><circle cx="92" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="164" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="92" cy="196" r="12" fill="currentColor" stroke="none"/><circle cx="164" cy="196" r="12" fill="currentColor" stroke="none"/>'),
    search:         ph('<circle cx="112" cy="112" r="80"/><line x1="168.57" y1="168.57" x2="224" y2="224"/>'),
    bolt:           ph('<polygon points="160 16 144 96 208 120 96 240 112 160 48 136 160 16"/>'),
    help:           ph('<circle cx="128" cy="180" r="12" fill="currentColor" stroke="none"/><path d="M128,144v-8c17.67,0,32-12.54,32-28s-14.33-28-32-28S96,92.54,96,108v4"/><circle cx="128" cy="128" r="96"/>'),
    chat:           ph('<line x1="96" y1="112" x2="160" y2="112"/><line x1="96" y1="144" x2="160" y2="144"/><path d="M79.93,211.11a96,96,0,1,0-35-35h0L32.42,213.46a8,8,0,0,0,10.12,10.12l37.39-12.47Z"/>'),
    panel:          ph('<line x1="88" y1="48" x2="88" y2="208"/><rect x="32" y="48" width="192" height="160" rx="8"/>'),
    dock:           ph('<line x1="88" y1="48" x2="88" y2="208"/><rect x="32" y="48" width="192" height="160" rx="8"/>'),
    float:          ph('<rect x="32" y="56" width="192" height="144" rx="8"/><polyline points="136 200 136 128 224 128"/>'),
    settings:       ph('<circle cx="104" cy="80" r="24"/><circle cx="168" cy="176" r="24"/><line x1="128" y1="80" x2="216" y2="80"/><line x1="40" y1="80" x2="80" y2="80"/><line x1="192" y1="176" x2="216" y2="176"/><line x1="40" y1="176" x2="144" y2="176"/>'),
    signin:         ph('<line x1="24" y1="128" x2="136" y2="128"/><polyline points="96 88 136 128 96 168"/><polyline points="136 40 200 40 200 216 136 216"/>'),
    signout:        ph('<polyline points="112 40 48 40 48 216 112 216"/><line x1="112" y1="128" x2="224" y2="128"/><polyline points="184 88 224 128 184 168"/>'),
    devices:        ph('<rect x="136" y="104" width="128" height="80" rx="16" transform="translate(344 -56) rotate(90)"/><line x1="128" y1="208" x2="88" y2="208"/><path d="M160,176H40a16,16,0,0,1-16-16V64A16,16,0,0,1,40,48H184a16,16,0,0,1,16,16V80"/><line x1="192" y1="112" x2="208" y2="112"/>'),
    phone:          ph('<rect x="64" y="24" width="128" height="208" rx="16"/><line x1="64" y1="56" x2="192" y2="56"/><line x1="64" y1="200" x2="192" y2="200"/>'),
    text:           ph('<polyline points="144 192 80 56 16 192"/><ellipse cx="200" cy="164" rx="32" ry="28"/><path d="M232,192V132c0-15.46-14.33-28-32-28-9.56,0-18.14,2.18-24,8"/><line x1="125.18" y1="152" x2="34.82" y2="152"/>'),
    keyboard:       ph('<rect x="24" y="56" width="208" height="144" rx="8"/><line x1="56" y1="128" x2="200" y2="128"/><line x1="56" y1="96" x2="200" y2="96"/><line x1="56" y1="160" x2="64" y2="160"/><line x1="96" y1="160" x2="160" y2="160"/><line x1="192" y1="160" x2="200" y2="160"/>'),
    save:           ph('<path d="M112,208H72A56,56,0,1,1,85.92,97.74"/><polyline points="120 160 152 128 184 160"/><line x1="152" y1="208" x2="152" y2="128"/><path d="M80,128a80,80,0,1,1,112,73.34"/>'),
    users:          ph('<circle cx="84" cy="108" r="52"/><path d="M10.23,200a88,88,0,0,1,147.54,0"/><path d="M172,160a87.93,87.93,0,0,1,73.77,40"/><path d="M152.69,59.7A52,52,0,1,1,172,160"/>'),
    pause:          ph('<rect x="152" y="40" width="56" height="176" rx="8"/><rect x="48" y="40" width="56" height="176" rx="8"/>'),
    stop:           ph('<rect x="48" y="48" width="160" height="160" rx="8"/>'),
    clock:          ph('<circle cx="128" cy="136" r="88"/><line x1="128" y1="136" x2="168" y2="96"/><line x1="104" y1="16" x2="152" y2="16"/>'),
    calendar:       ph('<rect x="40" y="40" width="176" height="176" rx="8"/><line x1="176" y1="24" x2="176" y2="56"/><line x1="80" y1="24" x2="80" y2="56"/><line x1="40" y1="88" x2="216" y2="88"/>'),
    calendar_check: ph('<rect x="40" y="40" width="176" height="176" rx="8"/><line x1="176" y1="24" x2="176" y2="56"/><line x1="80" y1="24" x2="80" y2="56"/><line x1="40" y1="88" x2="216" y2="88"/><polyline points="92 152 116 176 164 128"/>'),
    calc:           ph('<rect x="80" y="64" width="96" height="48"/><rect x="32" y="48" width="192" height="160" rx="8" transform="translate(256) rotate(90)"/><circle cx="88" cy="148" r="12" fill="currentColor" stroke="none"/><circle cx="128" cy="148" r="12" fill="currentColor" stroke="none"/><circle cx="168" cy="148" r="12" fill="currentColor" stroke="none"/><circle cx="88" cy="188" r="12" fill="currentColor" stroke="none"/><circle cx="128" cy="188" r="12" fill="currentColor" stroke="none"/><circle cx="168" cy="188" r="12" fill="currentColor" stroke="none"/>'),
    graph:          ph('<line x1="72" y1="128" x2="184" y2="128"/><path d="M56,216H85.29a32,32,0,0,0,31.49-26.28L139.22,66.28A32,32,0,0,1,170.71,40H200"/>'),
    ref:            ph('<line x1="40" y1="72" x2="104" y2="72"/><line x1="72" y1="152" x2="72" y2="216"/><line x1="40" y1="184" x2="104" y2="184"/><line x1="152" y1="168" x2="216" y2="168"/><line x1="152" y1="200" x2="216" y2="200"/><line x1="160" y1="48" x2="208" y2="96"/><line x1="208" y1="48" x2="160" y2="96"/>'),
    learn:          ph('<path d="M128,88a32,32,0,0,1,32-32h72V200H160a32,32,0,0,0-32,32"/><path d="M24,200H96a32,32,0,0,1,32,32V88A32,32,0,0,0,96,56H24Z"/><line x1="160" y1="96" x2="200" y2="96"/><line x1="160" y1="128" x2="200" y2="128"/><line x1="160" y1="160" x2="200" y2="160"/>'),
    book:           ph('<path d="M128,88a32,32,0,0,1,32-32h72V200H160a32,32,0,0,0-32,32"/><path d="M24,200H96a32,32,0,0,1,32,32V88A32,32,0,0,0,96,56H24Z"/><line x1="160" y1="96" x2="200" y2="96"/><line x1="160" y1="128" x2="200" y2="128"/><line x1="160" y1="160" x2="200" y2="160"/>'),
    hint:           ph('<line x1="88" y1="232" x2="168" y2="232"/><path d="M78.7,167A79.87,79.87,0,0,1,48,104.45C47.76,61.09,82.72,25,126.07,24a80,80,0,0,1,51.34,142.9A24.3,24.3,0,0,0,168,186v6a8,8,0,0,1-8,8H96a8,8,0,0,1-8-8v-6A24.11,24.11,0,0,0,78.7,167Z"/><path d="M136,56c20,3.37,36.61,20,40,40"/>'),
    speak:          ph('<path d="M80,168H32a8,8,0,0,1-8-8V96a8,8,0,0,1,8-8H80l72-56V224Z"/><line x1="80" y1="88" x2="80" y2="168"/><path d="M192,106.85a32,32,0,0,1,0,42.3"/><path d="M221.67,80a72,72,0,0,1,0,96"/>'),
    report:         ph('<circle cx="128" cy="128" r="96" stroke-miterlimit="10"/><line x1="128" y1="136" x2="128" y2="80"/><circle cx="128" cy="172" r="12" fill="currentColor" stroke="none"/>'),
    history:        ph('<polyline points="128 80 128 128 168 152"/><polyline points="72 104 32 104 32 64"/><path d="M67.6,192A88,88,0,1,0,65.77,65.77C54,77.69,44.28,88.93,32,104"/>'),
    eye:            ph('<path d="M128,56C48,56,16,128,16,128s32,72,112,72,112-72,112-72S208,56,128,56Z"/><circle cx="128" cy="128" r="40"/>'),
    eyeoff:         ph('<line x1="48" y1="40" x2="208" y2="216"/><path d="M154.91,157.6a40,40,0,0,1-53.82-59.2"/><path d="M135.53,88.71a40,40,0,0,1,32.3,35.53"/><path d="M208.61,169.1C230.41,149.58,240,128,240,128S208,56,128,56a126,126,0,0,0-20.68,1.68"/><path d="M74,68.6C33.23,89.24,16,128,16,128s32,72,112,72a118.05,118.05,0,0,0,54-12.6"/>'),
    cover:          ph('<line x1="48" y1="40" x2="208" y2="216"/><path d="M154.91,157.6a40,40,0,0,1-53.82-59.2"/><path d="M135.53,88.71a40,40,0,0,1,32.3,35.53"/><path d="M208.61,169.1C230.41,149.58,240,128,240,128S208,56,128,56a126,126,0,0,0-20.68,1.68"/><path d="M74,68.6C33.23,89.24,16,128,16,128s32,72,112,72a118.05,118.05,0,0,0,54-12.6"/>'),
    expand:         ph('<polyline points="160 48 208 48 208 96"/><line x1="144" y1="112" x2="208" y2="48"/><polyline points="96 208 48 208 48 160"/><line x1="112" y1="144" x2="48" y2="208"/>'),
    shrink:         ph('<polyline points="144 64 144 112 192 112"/><line x1="208" y1="48" x2="144" y2="112"/><polyline points="64 144 112 144 112 192"/><line x1="48" y1="208" x2="112" y2="144"/>'),
    marker:         ph('<polyline points="88 128 24 192 96 216 136 176"/><path d="M184,160l-26.34,26.34a8,8,0,0,1-11.32,0L77.66,117.66a8,8,0,0,1,0-11.32L104,80"/><path d="M248,112l-50.34,50.34a8,8,0,0,1-11.32,0L101.66,77.66a8,8,0,0,1,0-11.32L152,16"/>'),
    pen:            ph('<path d="M92.69,216H48a8,8,0,0,1-8-8V163.31a8,8,0,0,1,2.34-5.65L165.66,34.34a8,8,0,0,1,11.31,0L221.66,79a8,8,0,0,1,0,11.31L98.34,213.66A8,8,0,0,1,92.69,216Z"/><line x1="136" y1="64" x2="192" y2="120"/>'),
    edit:           ph('<path d="M92.69,216H48a8,8,0,0,1-8-8V163.31a8,8,0,0,1,2.34-5.65L165.66,34.34a8,8,0,0,1,11.31,0L221.66,79a8,8,0,0,1,0,11.31L98.34,213.66A8,8,0,0,1,92.69,216Z"/><line x1="136" y1="64" x2="192" y2="120"/>'),
    erase:          ph('<line x1="96" y1="104" x2="160" y2="168"/><path d="M112,216,219.31,108.69a16,16,0,0,0,0-22.63L177.94,44.69a16,16,0,0,0-22.63,0L36.69,163.31a16,16,0,0,0,0,22.63L66.75,216H216"/>'),
    hl:             ph('<circle cx="128" cy="128" r="96"/><path d="M176,211.16V176a8,8,0,0,0-8-8H88a8,8,0,0,0-8,8v35.16"/><path d="M96,168V144a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8v24"/><path d="M147.84,136l-12-57.63c-1.77-8.49-13.89-8.49-15.66,0l-12,57.63"/>'),
    list:           ph('<line x1="88" y1="64" x2="216" y2="64"/><line x1="88" y1="128" x2="216" y2="128"/><line x1="88" y1="192" x2="216" y2="192"/><circle cx="44" cy="64" r="12" fill="currentColor" stroke="none"/><circle cx="44" cy="128" r="12" fill="currentColor" stroke="none"/><circle cx="44" cy="192" r="12" fill="currentColor" stroke="none"/>'),
    grid:           ph('<rect x="48" y="48" width="64" height="64" rx="8"/><rect x="144" y="48" width="64" height="64" rx="8"/><rect x="48" y="144" width="64" height="64" rx="8"/><rect x="144" y="144" width="64" height="64" rx="8"/>'),
    queue:          ph('<line x1="40" y1="64" x2="216" y2="64"/><line x1="40" y1="128" x2="136" y2="128"/><line x1="40" y1="192" x2="136" y2="192"/><polygon points="240 160 176 200 176 120 240 160"/>'),
    filter:         ph('<line x1="64" y1="136" x2="192" y2="136"/><line x1="24" y1="88" x2="232" y2="88"/><line x1="104" y1="184" x2="152" y2="184"/>'),
    image:          ph('<rect x="32" y="48" width="192" height="160" rx="8"/><circle cx="156" cy="100" r="12" fill="currentColor" stroke="none"/><path d="M147.31,164,173,138.34a8,8,0,0,1,11.31,0L224,178.06"/><path d="M32,168.69l54.34-54.35a8,8,0,0,1,11.32,0L191.31,208"/>'),
    camera:         ph('<path d="M208,208H48a16,16,0,0,1-16-16V80A16,16,0,0,1,48,64H80L96,40h64l16,24h32a16,16,0,0,1,16,16V192A16,16,0,0,1,208,208Z"/><circle cx="128" cy="132" r="36"/>'),
    twin:           ph('<polyline points="168 168 216 168 216 40 88 40 88 88"/><rect x="40" y="88" width="128" height="128"/>'),
    copy:           ph('<polyline points="168 168 216 168 216 40 88 40 88 88"/><rect x="40" y="88" width="128" height="128"/>'),
    link:           ph('<line x1="96" y1="160" x2="160" y2="96"/><path d="M112,76.11l30.06-30a48,48,0,0,1,67.88,67.88L179.88,144"/><path d="M76.11,112l-30,30.06a48,48,0,0,0,67.88,67.88L144,179.88"/>'),
    external:       ph('<line x1="64" y1="192" x2="192" y2="64"/><polyline points="88 64 192 64 192 168"/>'),
    key:            twin('key', '<path d="M93.17,122.83A71.68,71.68,0,0,1,88,95.91c0-38.58,31.08-70.64,69.64-71.87A72,72,0,0,1,232,98.36C230.73,136.92,198.67,168,160.09,168a71.68,71.68,0,0,1-26.92-5.17h0L120,176H96v24H72v24H40a8,8,0,0,1-8-8V187.31a8,8,0,0,1,2.34-5.65l58.83-58.83Z"/><circle cx="180" cy="76" r="12" fill="currentColor" stroke="none"/>'),
    envelope:       twin('envelope', '<polyline points="224 56 128 144 32 56"/><path d="M32,56H224a0,0,0,0,1,0,0V192a8,8,0,0,1-8,8H40a8,8,0,0,1-8-8V56A0,0,0,0,1,32,56Z"/><line x1="110.55" y1="128" x2="34.47" y2="197.74"/><line x1="221.53" y1="197.74" x2="145.45" y2="128"/>'),
    fingerprint:    twin('fingerprint', '<path d="M50.69,184.92A127.52,127.52,0,0,0,64,128a63.85,63.85,0,0,1,24-50"/><path d="M128,128a191.11,191.11,0,0,1-24,93"/><path d="M96,128a32,32,0,0,1,64,0,223.12,223.12,0,0,1-21.28,95.41"/><path d="M218.56,184A289.45,289.45,0,0,0,224,128a96,96,0,0,0-192,0,95.8,95.8,0,0,1-5.47,32"/><path d="M92.81,160a158.92,158.92,0,0,1-18.12,47.84"/><path d="M120,64.5a66,66,0,0,1,8-.49,64,64,0,0,1,64,64,259.86,259.86,0,0,1-2,32"/><path d="M183.94,192q-2.28,8.88-5.18,17.5"/>'),
    shield:         twin('shield', '<path d="M216,112V56a8,8,0,0,0-8-8H48a8,8,0,0,0-8,8v56c0,96,88,120,88,120S216,208,216,112Z"/>'),
    medal:          twin('medal', '<circle cx="128" cy="96" r="80"/><circle cx="128" cy="96" r="48"/><polyline points="176 160 176 240 127.99 216 80 240 80 160.01"/>'),
    again:          ph('<polyline points="24 56 24 104 72 104"/><path d="M67.59,192A88,88,0,1,0,65.77,65.77L24,104"/>'),
    fix:            ph('<polyline points="184 104 232 104 232 56"/><path d="M188.4,192a88,88,0,1,1,1.83-126.23L232,104"/>'),
    info:           ph('<circle cx="128" cy="128" r="96"/><path d="M120,120a8,8,0,0,1,8,8v40a8,8,0,0,0,8,8"/><circle cx="124" cy="84" r="12" fill="currentColor" stroke="none"/>'),
    trap:           ph('<circle cx="128" cy="128" r="96"/><line x1="128" y1="32" x2="128" y2="72"/><line x1="128" y1="184" x2="128" y2="224"/><line x1="32" y1="128" x2="72" y2="128"/><line x1="184" y1="128" x2="224" y2="128"/>'),
    clean:          ph('<polyline points="88 136 112 160 168 104"/><circle cx="128" cy="128" r="96"/>'),
    sheet:          ph('<path d="M200,224H56a8,8,0,0,1-8-8V40a8,8,0,0,1,8-8h96l56,56V216A8,8,0,0,1,200,224Z"/><polyline points="152 32 152 88 208 88"/><line x1="96" y1="136" x2="160" y2="136"/><line x1="96" y1="168" x2="160" y2="168"/>'),
    trophy:         ph('<line x1="96" y1="224" x2="160" y2="224"/><line x1="128" y1="184" x2="128" y2="224"/><path d="M58,128H48A32,32,0,0,1,16,96V80a8,8,0,0,1,8-8H56"/><path d="M198,128h10a32,32,0,0,0,32-32V80a8,8,0,0,0-8-8H200"/><path d="M56,48H200v63.1c0,39.7-31.75,72.6-71.45,72.9A72,72,0,0,1,56,112Z"/>'),
    twin_test:      ph('<polyline points="88 88 88 40 216 40 216 120"/><rect x="40" y="88" width="104" height="128"/><circle cx="192" cy="180" r="40"/><polyline points="192 156 192 180 208 192"/>'),
    eliminate:      '<g class="ph" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M3.5 17l3-9 3 9M4.6 14h3.8M12.5 8h3a2.2 2.2 0 0 1 0 4.4h-3zM12.5 12.4h3.4a2.3 2.3 0 0 1 0 4.6h-3.4zM3 20.5L21 3.5"/></g>',
    strikes:        '<g class="ph" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M4 9l4 6M8 9l-4 6M10 9l4 6M14 9l-4 6M16 9l4 6M20 9l-4 6"/></g>',
    dot:            '<circle cx="12" cy="12" r="4" fill="var(--amber)"/>',
  };
  const ICON_FILL = Object.fromEntries(Object.keys(PHF).filter(n => n !== 'play').map(n => [n, phf(PHF[n])]));

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
  // the ten Reading and Writing skills, by the bank's topic slug (a set's title, never the raw slug)
  const RW_SKILL = {
    rw_central_ideas_and_details: 'Central Ideas and Details', rw_inferences: 'Inferences',
    rw_command_of_evidence: 'Command of Evidence', rw_words_in_context: 'Words in Context',
    rw_text_structure_and_purpose: 'Text Structure and Purpose', rw_cross_text_connections: 'Cross-Text Connections',
    rw_rhetorical_synthesis: 'Rhetorical Synthesis', rw_transitions: 'Transitions', rw_boundaries: 'Boundaries',
    rw_form_structure_and_sense: 'Form, Structure, and Sense',
  };
  // the four R&W domains in Bluebook's order, each with its skills in that order (blueprint.RW_ORDER)
  const RW_DOMAINS = [
    ['Craft and Structure', ['rw_words_in_context', 'rw_text_structure_and_purpose', 'rw_cross_text_connections']],
    ['Information and Ideas', ['rw_central_ideas_and_details', 'rw_command_of_evidence', 'rw_inferences']],
    ['Standard English Conventions', ['rw_boundaries', 'rw_form_structure_and_sense']],
    ['Expression of Ideas', ['rw_transitions', 'rw_rhetorical_synthesis']],
  ].map(([name, skills]) => ({ name, skills }));

  /* ------------------------------------------------------------ subject
     Math or Reading and Writing, one choice for the whole site: ?subject= wins (links and reloads
     agree), else the last one picked (satf.subject), else Math. subjectSeg draws the same switch on
     every page that shows one subject at a time; both: true adds "Both" first, for lists. */
  const SUBJECTS = ['math', 'rw'];
  const SUBJECT_NAME = { math: ['Math', 'Math'], rw: ['Reading and Writing', 'R&W'], both: ['Both', 'Both'] };
  const subjectLabel = (s, short) => (SUBJECT_NAME[s] || SUBJECT_NAME.math)[short ? 1 : 0];
  const subjectOf = topic => (/^rw[_.]/.test(String(topic || '')) ? 'rw' : 'math');
  const topicName = t => RW_SKILL[t] || (TOPIC[t] && TOPIC[t].short) || String(t || '').replace(/^rw_/, '').replace(/_/g, ' ');
  const subject = {
    get(opts = {}) {
      const q = new URLSearchParams(location.search).get('subject');
      // a link that names a subject is a choice too: the next page opens on it
      if (SUBJECTS.includes(q)) { try { localStorage.setItem('satf.subject', q); } catch (_) {} }
      if (SUBJECTS.includes(q) || (opts.both && q === 'both')) return q;
      if (opts.both) return 'both';             // a list opens on everything unless the link says otherwise
      let v = null;
      try { v = localStorage.getItem('satf.subject'); } catch (_) {}
      return SUBJECTS.includes(v) ? v : 'math';
    },
    set(s, opts = {}) {
      try { if (SUBJECTS.includes(s)) localStorage.setItem('satf.subject', s); } catch (_) {}
      if (opts.url !== false) {
        const u = new URL(location.href);
        u.searchParams.set('subject', s);
        history.replaceState(history.state, '', u);
      }
    },
  };
  function subjectSeg(host, o = {}) {
    const opts = (o.both ? ['both'] : []).concat(SUBJECTS).map(v => ({ value: v, label: subjectLabel(v, o.short) }));
    const value = o.value || subject.get({ both: o.both });
    // the page's address carries the subject from the start, so a copied link opens the same view
    if (o.url !== false && !new URLSearchParams(location.search).get('subject')) {
      const u = new URL(location.href);
      u.searchParams.set('subject', value);
      history.replaceState(history.state, '', u);
    }
    return UI.seg(host, opts, {
      value, label: o.label || 'Subject',
      onChange: v => { subject.set(v, { url: o.url }); if (o.onChange) o.onChange(v); },
    });
  }

  /* ------------------------------------------------------------ aliases and the set parser
     (Shell 2.8, practice.md P15). Skills match on a word prefix of their names or on these
     aliases; the first six rows are Shell 2.8's table, the rest are words students type. */
  const ALIASES = {
    nonlinear_functions: ['quadratic', 'quadratics', 'exponential', 'parabola', 'vertex'],
    right_triangles_and_trigonometry: ['trig', 'trigonometry', 'sin', 'cos', 'tan', 'sohcahtoa', 'pythagorean'],
    circles: ['arc', 'arcs', 'sector', 'radian', 'radians', 'chord'],
    ratios_rates_proportions_and_units: ['ratio', 'rate', 'unit', 'units', 'proportion', 'proportions'],
    sample_statistics_and_margin_of_error: ['margin', 'sample', 'inference'],
    evaluating_statistical_claims: ['claim', 'claims', 'study', 'experiment'],
    percentages: ['percent'],
    probability: ['chance', 'odds'],
    linear_inequalities: ['inequality', 'inequalities'],
    systems_of_linear_equations: ['system', 'systems'],
    linear_functions: ['slope', 'intercept'],
    equivalent_expressions: ['factor', 'factoring', 'expand', 'polynomial', 'polynomials'],
    one_variable_data: ['mean', 'median', 'histogram', 'outlier', 'deviation'],
    two_variable_data: ['scatter', 'scatterplot', 'regression'],
    lines_angles_and_triangles: ['angle', 'angles', 'triangle', 'triangles', 'parallel', 'transversal'],
    // Reading and Writing: the words students use for each skill
    rw_words_in_context: ['vocab', 'vocabulary', 'wic'],
    rw_command_of_evidence: ['evidence', 'coe'],
    rw_central_ideas_and_details: ['main idea', 'central idea'],
    rw_text_structure_and_purpose: ['purpose'],
    rw_cross_text_connections: ['cross text', 'paired'],
    rw_rhetorical_synthesis: ['synthesis', 'notes'],
    rw_boundaries: ['punctuation', 'comma', 'commas', 'semicolon'],
    rw_form_structure_and_sense: ['grammar', 'verb', 'verbs', 'agreement', 'tense'],
  };
  const words = s => String(s || '').toLowerCase().replace(/&/g, ' and ').replace(/[‐-―-]/g, ' ')
    .replace(/[^a-z0-9∞\s]/g, ' ').split(/\s+/).filter(Boolean);
  let PHRASES = null;
  function phrases() {                    // every way to name a skill, longest first
    if (!PHRASES) {
      PHRASES = TOPICS.flatMap(t => [t.short, t.slug.replace(/_/g, ' '), ...(ALIASES[t.slug] || [])]
        .map(n => ({ w: words(n), slug: t.slug })))
        .concat(Object.entries(RW_SKILL).flatMap(([slug, name]) => [name, ...(ALIASES[slug] || [])]
          .map(n => ({ w: words(n), slug }))));
      PHRASES.sort((a, b) => b.w.length - a.w.length);
    }
    return PHRASES;
  }
  const wordHit = (tok, w) => tok === w || (tok.length >= 3 && w.startsWith(tok));
  // the skills named at tokens[i..]: {slug, n} for the longest unambiguous phrase
  function skillAt(toks, i) {
    let best = null, len = 0, clash = false;
    for (const p of phrases()) {
      if (p.w.length < len) break;
      if (i + p.w.length > toks.length || !p.w.every((w, k) => wordHit(toks[i + k], w))) continue;
      if (!best || p.w.length > len) { best = p.slug; len = p.w.length; clash = false; }
      else if (p.slug !== best) clash = true;
    }
    return best && !clash ? { slug: best, n: len } : null;
  }
  const FILLER = new Set(['q', 'qs', 'question', 'questions', 'practise', 'practice', 'set', 'of', 'a', 'an', 'the',
    'and', 'with', 'in', 'on', 'some', 'me', 'do']);
  const TIER_WORDS = { easy: 'easy', medium: 'medium', med: 'medium', hard: 'hard' };
  /* UI.parseSet(text, {count, types}) -> {body, chips, unknown, text, any, box}
     count: the default when none is typed (prefs.set_length; 0 = endless). types: the
     catalogue's [{template, name}], so a whole type name selects that type. Unrecognised
     words come back in `unknown` for the caller to search on. */
  function parseSet(text, o = {}) {
    const toks = words(text);
    const topics = [], chips = [], unknown = [];
    const body = {};
    let tiers = null, count, box = null, set = false;
    const addTier = t => { tiers = tiers || new Set(); tiers.add(t); };
    for (let i = 0; i < toks.length; i++) {
      const t = toks[i], next = toks[i + 1];
      const mins = /^(\d{1,2})(m|min|mins|minute|minutes)$/.exec(t);
      if (mins || (/^\d{1,2}$/.test(t) && /^(m|min|mins|minute|minutes)$/.test(next || ''))) {
        box = Number(mins ? mins[1] : t); if (!mins) i++; continue;
      }
      if (t === 'half' && /^hours?$/.test(next || '')) { box = 30; i++; continue; }
      if ((t === 'an' || t === '1' || t === 'one') && /^hours?$/.test(next || '')) { box = 60; i++; continue; }
      if (/^hours?$/.test(t)) { box = 60; continue; }
      const q = /^(\d{1,3})(q|qs)?$/.exec(t);
      if (q && +q[1] >= 1 && +q[1] <= 120) { count = +q[1]; set = true; continue; }
      if (t === 'endless' || t === '∞' || t === 'infinite' || t === 'unlimited') { count = null; set = true; continue; }
      if (TIER_WORDS[t]) { addTier(TIER_WORDS[t]); set = true; continue; }
      if (t === 'mixed' || t === 'all') { tiers = new Set(['easy', 'medium', 'hard']); set = true; continue; }
      if (t === 'adaptive') { body.adaptive = true; set = true; continue; }
      if (t === 'timed' || t === 'pace') { body.timed = true; set = true; continue; }
      if (t === 'untimed') { body.timed = false; set = true; continue; }
      if (t === 'mc' || t === 'mcq' || (t === 'multiple' && next === 'choice')) { body.formats = ['mcq']; if (t === 'multiple') i++; set = true; continue; }
      if (t === 'grid' || t === 'gridin' || t === 'gridins' || t === 'spr') { body.formats = ['spr']; if (next === 'in' || next === 'ins') i++; set = true; continue; }
      if (t === 'mistakes' || t === 'mistake' || t === 'redo') { body.pool = 'redo'; set = true; continue; }
      if (t === 'due' || t === 'checkins' || (t === 'check' && /^ins?$/.test(next || ''))) { body.pool = 'checks'; if (t === 'check') i++; set = true; continue; }
      if (t === 'untried' || t === 'unseen') { body.pool = 'untried'; set = true; continue; }
      if (t === 'marked' || t === 'saved') { body.pool = t; set = true; continue; }
      if (t === 'retry') { body.feedback = 'retry'; set = true; continue; }
      if (t === 'test' && next === 'mode') { body.feedback = 'end'; body.timed = true; i++; set = true; continue; }
      if (t === 'ramp') { body.order = 'ramp'; set = true; continue; }
      if (t === 'warmup' || (t === 'warm' && next === 'up')) { body.zone = 'warm'; if (t === 'warm') i++; set = true; continue; }
      if (t === 'stretch') { body.zone = t; set = true; continue; }
      const sk = skillAt(toks, i);
      if (sk) { if (!topics.includes(sk.slug)) topics.push(sk.slug); i += sk.n - 1; continue; }
      if (!FILLER.has(t)) unknown.push(t);
    }
    // a whole type name ("central angles") picks that type
    let type = null;
    if (o.types && unknown.length && !topics.length) {
      const phrase = unknown.join(' ');
      type = o.types.find(x => words(x.name).join(' ') === phrase) || null;
      if (type) { unknown.length = 0; body.templates = [type.template]; }
    }
    if (topics.length) body.topics = topics;
    if (topics.length && topics.every(t => subjectOf(t) === 'rw')) body.subject = 'rw';
    if (tiers) body.tiers = ['easy', 'medium', 'hard'].filter(x => tiers.has(x));
    const inTime = box && count;                  // "10 in 10 min": the count, with the minutes as its limit
    if (inTime) { body.count = count; body.timing = 'custom'; body.minutes = box; body.timed = true; }
    else if (box) { body.box = box; body.count = null; }
    else if (count !== undefined) body.count = count;
    else { const c = o.count ?? 10; body.count = c ? c : null; }
    body.source = o.source || 'palette';
    const any = set || topics.length > 0 || !!type;
    if (box && !inTime && !any) { for (const k in body) delete body[k]; Object.assign(body, { source: 'next', box }); }

    // chips and the composed line: "Practise Circles · Hard · 5 questions · timed"
    topics.forEach(s => chips.push({ key: 'topic:' + s, label: topicName(s) }));
    if (type) chips.push({ key: 'type', label: type.name });
    const POOL = { redo: 'My mistakes', checks: 'Check-ins due', untried: 'Types I haven’t met', marked: 'Marked', saved: 'Saved' };
    if (body.pool) chips.push({ key: 'pool', label: POOL[body.pool] });
    if (body.adaptive) chips.push({ key: 'adaptive', label: 'Adaptive' });
    if (body.tiers && body.tiers.length < 3) chips.push({ key: 'tiers', label: body.tiers.map(cap).join(', ') });
    else if (body.tiers) chips.push({ key: 'tiers', label: 'Mixed' });
    if (inTime) chips.push({ key: 'count', label: `${count} ${count === 1 ? 'question' : 'questions'} in ${box} min` });
    else if (box) chips.push({ key: 'box', label: `${box} minutes` });
    else chips.push({ key: 'count', label: body.count ? `${body.count} ${body.count === 1 ? 'question' : 'questions'}` : 'Endless' });
    if (body.timed === true && !inTime) chips.push({ key: 'timed', label: body.feedback === 'end' ? 'Test mode' : 'timed' });
    if (body.timed === false) chips.push({ key: 'timed', label: 'untimed' });
    if (body.formats) chips.push({ key: 'formats', label: body.formats[0] === 'spr' ? 'Grid-in' : 'Multiple choice' });
    if (body.feedback === 'retry') chips.push({ key: 'feedback', label: 'Retry first' });
    if (body.order === 'ramp') chips.push({ key: 'order', label: 'Easy to hard' });
    if (body.zone) chips.push({ key: 'zone', label: body.zone === 'warm' ? 'Warm-up' : 'Stretch' });
    const line = box && !inTime && !any ? `Up next for ${box} minutes` : `Practise ${chips.map(c => c.label).join(' · ')}`;
    return { body, chips, unknown, text: line, any: any || !!box, box: inTime ? null : box };
  }

  /* ------------------------------------------------------------ the question-type index
     GET /api/shell/catalog once a session (sessionStorage satf.types.2): the palette's and the
     quick sheet's 386 types with their named mistakes. */
  let typesAsked = null;
  function types() {
    if (!typesAsked) {
      typesAsked = (async () => {
        let raw = null;
        try { raw = JSON.parse(sget(SS(), 'satf.types.2') || 'null'); } catch (_) {}
        if (!raw || !Array.isArray(raw.types)) {
          raw = await api('/shell/catalog', { quiet: true });
          sput(SS(), 'satf.types.2', JSON.stringify(raw));
        }
        const list = raw.types.map(([template, name, topic, rs, about]) =>
          ({ template, name, topic, about: about || '', reasons: rs.map(([norm, label]) => ({ norm, label: label || norm })) }));
        const byTopic = {};
        list.forEach(x => (byTopic[x.topic] = byTopic[x.topic] || []).push(x));
        return { list, byTopic, cb: raw.cb || {} };
      })();
      typesAsked.catch(() => { typesAsked = null; });
    }
    return typesAsked;
  }

  const poly = (n, r, rot = -90) => Array.from({ length: n }, (_, i) => {
    const a = (rot + i * 360 / n) * Math.PI / 180;
    return (r * Math.cos(a)).toFixed(2) + ',' + (r * Math.sin(a)).toFixed(2);
  }).join(' ');

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
    // an R&W skill: lines of text
    lines: g => { s('path', { class: 'stkl', d: 'M-8 -5.5 H8 M-8 0 H8 M-8 5.5 H3' }, g); },
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
  function glyph(slug) {
    const g = document.createElementNS(NS, 'svg');
    g.setAttribute('viewBox', '-12 -12 24 24');
    g.setAttribute('aria-hidden', 'true');
    g.setAttribute('focusable', 'false');
    g.setAttribute('class', 'glyph');
    const t = TOPIC[slug];
    (SHAPES[t ? t.shape : RW_SKILL[slug] ? 'lines' : 'dotcircle'])(g);
    return g;
  }
  const chip = slug => h('span', { class: 'chip' }, glyph(slug), topicName(slug));

  /* ------------------------------------------------------------ helpers */
  const mmss = sec => {
    sec = Math.max(0, Math.round(sec));
    return Math.floor(sec / 60) + ':' + String(sec % 60).padStart(2, '0');
  };
  const minutesFor = n => Math.max(1, Math.round(n * 95 / 60));      // the real test's pace
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const day = iso => { const d = new Date(iso.length === 10 ? iso + 'T12:00:00' : iso); return `${MONTHS[d.getMonth()]} ${d.getDate()}`; };
  const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
  const band = e => e ? `${e.low}–${e.high}` : '\u2013';
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
      if (b.run(e) !== false) { e.preventDefault(); flashKeys(b.key); }
      return;
    }
    if (c !== 'Escape' && active.some(r => [...r.map.keys()].some(k => k.startsWith(c + ' ')))) {
      pending = c; pendingAt = Date.now();
      e.preventDefault();
    }
  }
  doc.addEventListener('keydown', onKey);
  // the keycaps on screen that show a shortcut flash once when it fires (ui.css .m-kflash, motion.css)
  function flashKeys(c) {
    if (UI.motion && UI.motion.calm()) return;
    const parts = combo(c).split(' ').flatMap(st => st.split('+'));
    const want = [parts.map(x => String(CAP[x] || x).toLowerCase()), parts.map(x => x.toLowerCase())];
    const seen = new Set(), lit = [];
    doc.querySelectorAll('kbd').forEach(k => {
      const p = k.parentElement;
      if (!p || seen.has(p)) return;
      seen.add(p);
      const caps = [...p.children].filter(x => x.tagName === 'KBD');
      const got = caps.map(x => x.textContent.trim().toLowerCase());
      if (!want.some(w => w.length === got.length && w.every((x, i) => x === got[i])) || !caps[0].getClientRects().length) return;
      caps.forEach(x => { x.classList.remove('m-kflash'); void x.offsetWidth; x.classList.add('m-kflash'); lit.push(x); });
    });
    if (lit.length) setTimeout(() => lit.forEach(x => x.classList.remove('m-kflash')), 400);
  }

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
    // the quick sheet is absent where there is no shell: the session, the test window (R29)
    Q: { does: 'Quick question · Log a mistake · Add a word', run: () => UI.quick(), when: () => typeof UI.quick === 'function' && chrome() },
    'Mod+K': { does: 'Search', run: () => UI.palette(), when: () => typeof UI.palette === 'function' && chrome() },
    '/': { does: 'Search', run: () => UI.palette(), when: () => typeof UI.palette === 'function' && chrome() },
    '[': { does: 'Collapse or expand the sidebar · hold to peek', run: e => bracket(e), when: () => chrome() && !!sideEl },
    Z: { does: 'Undo the last change', run: () => (UI.toast && UI.toast.undo ? UI.toast.undo() : false) },
    '?': { does: 'Keyboard shortcuts', run: () => keysSheet() },
  });

  /* ------------------------------------------------------------ Up next (U1) */
  function nextItems(d = shellData) {
    let snooze = {};
    try { snooze = JSON.parse(sget(LS(), 'satf.next.snooze') || '{}') || {}; } catch (_) {}
    const day = localDay();
    return ((d && d.next) || []).filter(x => snooze[x.key] !== day);
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

  /* ------------------------------------------------------------ the run (G1)
     UI.run walks the day's Up next queue as one run, each part its own ordinary sitting
     started with run: <local day> (in a drill body, or &run= on an href) and chained by the
     between pane. The queue is the truth (GET /api/next, else /api/shell.next); what this tab
     started or skipped today is sessionStorage satf.run {day, done: [{key, title}], skipped:
     [key]}, left out of the next read. Contests and the challenge keep their own lobby.
     ponytail: per tab, so a second device starts from the queue; read G1's /api/today.due
     rows (with run {on, part, parts}) once S3 serves them. */
  const RUN_NEVER = new Set(['contest', 'challenge']);
  function runState() {
    let st = null;
    try { st = JSON.parse(sget(SS(), 'satf.run') || 'null'); } catch (_) {}
    const day = localDay();
    return st && st.day === day && Array.isArray(st.done) ? { ...st, skipped: Array.isArray(st.skipped) ? st.skipped : [] }
      : { day, done: [], skipped: [] };
  }
  const runKeep = st => sput(SS(), 'satf.run', JSON.stringify(st));
  async function runParts() {
    if (!shellData) await (shellAsked || refresh()).catch(() => null);
    const st = runState(), out = new Set([...st.done.map(x => x.key), ...st.skipped]);
    const keys = [...out];
    while (keys.join(',').length > 400) keys.shift();             // GET /api/next caps exclude at 400
    let items = null;
    if (has('next')) {
      try { items = (await api(`/next?limit=6${keys.length ? '&exclude=' + encodeURIComponent(keys.join(',')) : ''}`, { quiet: true })).items; } catch (_) {}
    }
    if (!Array.isArray(items)) items = (shellData && shellData.next) || [];
    const snoozed = lget('satf.next.snooze', {}) || {};
    const next = items.flatMap(x => x && !x.start && !x.href && x.warmup ? [{ key: 'warmup:eve', kind: 'warm', ...x.warmup }] : [x])
      .filter(x => x && !RUN_NEVER.has(x.kind) && (x.start || x.href) && !out.has(x.key) && snoozed[x.key] !== st.day);
    return { state: st, done: st.done, next, part: st.done.length + 1, parts: st.done.length + next.length,
      minutes: next.reduce((a, x) => a + (x.minutes || 0), 0) };
  }
  function withRun(it, day) {
    if (it.start) return { ...it, start: { ...it.start, body: { ...(it.start.body || {}), run: day } } };
    const u = new URL(it.href, location.origin);
    u.searchParams.set('run', day);
    return { ...it, href: u.pathname + u.search + u.hash };
  }
  async function runGo(it) {
    const st = runState();
    await start(withRun(it, st.day));
    st.done = [...st.done.filter(x => x.key !== it.key), { key: it.key, title: it.title }];
    runKeep(st);
  }
  async function runStart() {
    const it = (await runParts()).next[0];
    if (!it) { if (UI.toast) UI.toast('Nothing left for today.'); return null; }
    try { await runGo(it); } catch (e) { if (UI.toast && !e.offline) UI.toast('Couldn’t start it. Try again.'); }
    return it;
  }
  // "Start today · 4 parts · 38 min", mid-run "Continue today · part 2 of 5"; null when nothing is left
  async function runLabel() {
    const p = await runParts();
    if (!p.next.length) return null;
    return p.done.length ? `Continue today · part ${fmt(p.part)} of ${fmt(p.parts)}`
      : `Start today · ${plural(p.parts, 'part')}${p.minutes ? ` · ${fmt(p.minutes)} min` : ''}`;
  }
  // L8's interstitial: the finished part on the left, the next on the right. done: {title,
  // right, total, minutes}; next: an Up next item, or read from the queue; o.onStop
  let runKeys = null;
  function runBetween(host, done = {}, next = null, o = {}) {
    const el = h('section', { class: 'card run-between', 'aria-label': 'Today’s run',
      style: 'display: grid; gap: 16px 28px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr))' });
    const col = () => h('div', { style: 'display: grid; gap: 4px; align-content: start; min-width: 0' });
    const left = col(), right = col();
    const st = runState(), last = st.done[st.done.length - 1];
    const title = done.title || (last && last.title) || '';
    left.append(h('span', { class: 'k', text: 'Done' }), title ? h('span', { class: 'nextup-t', text: title }) : '',
      done.total ? h('span', { style: 'font: 500 20px var(--mono); font-variant-numeric: tabular-nums', text: `${fmt(done.right || 0)} / ${fmt(done.total)}` }) : '',
      done.minutes ? h('span', { class: 'nextup-m', text: `${fmt(done.minutes)} min` }) : '');
    el.append(left, right);
    let cur = null, contBtn = null;
    const act = (label, cls, kbd, fn) => h('button', { type: 'button', class: cls, onclick: fn }, label,
      kbd && !media('(pointer: coarse)') ? keycaps(kbd) : null);             // no key hints on a touch screen
    const stop = () => { if (o.onStop) o.onStop(); else location.href = '/'; };
    async function cont() {
      if (!cur || !contBtn || contBtn.getAttribute('aria-busy') === 'true') return;
      contBtn.setAttribute('aria-busy', 'true');
      try { await runGo(cur); }
      catch (e) { contBtn.removeAttribute('aria-busy'); if (UI.toast && !e.offline) UI.toast('Couldn’t start it. Try again.'); }
    }
    function skipPart() {                  // moves on without marking the part; it stays undone on Today
      if (!cur) return;
      const s = runState();
      s.skipped = [...s.skipped, cur.key];
      runKeep(s);
      paint(null);
    }
    async function paint(given) {
      cur = null;
      right.replaceChildren(h('span', { class: 'k', text: 'Up next' }), UI.skel ? UI.skel(null, 'lines:2') : '');
      const p = await runParts();
      cur = given && !p.state.skipped.includes(given.key) ? given : p.next[0] || null;
      if (!cur) {                          // the end: keep going, or today's challenge
        const ch = shellData && shellData.challenge;
        right.replaceChildren(h('span', { class: 'k', text: 'Day done' }),
          h('div', { style: 'display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px' },
            startBtn({ start: { path: '/drill', body: { source: 'next', box: 15 } } }, 'Keep going · 15 min'),
            ch && !ch.done ? h('a', { class: 'btn sm', href: '/challenge/', text: 'Today’s challenge' }) : null));
        return;
      }
      const meta = nextMeta(cur);
      contBtn = act('Continue', 'pill sm', 'Enter', cont);
      right.replaceChildren(h('span', { class: 'k', text: `Part ${fmt(p.part)} of ${fmt(Math.max(p.parts, p.part))}` }),
        h('span', { class: 'nextup-t', text: cur.title }), meta ? h('span', { class: 'nextup-m', text: meta }) : '',
        cur.reason ? h('span', { class: 'nextup-r', text: cur.reason }) : '',
        h('div', { style: 'display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 10px' },
          contBtn, act('Skip this part', 'quiet', 'S', skipPart), act('Stop for now', 'quiet', 'Escape', stop)));
    }
    if (runKeys) runKeys.unregister();
    runKeys = register('run', {
      // Enter on another focused control is that control's own
      Enter: { does: 'Continue today', run: e => {
        const t = e && e.target && e.target.closest ? e.target.closest('button, a, input, textarea, select') : null;
        if (!cur || (t && t !== contBtn)) return false;
        cont();
      } },
      S: { does: 'Skip this part', run: () => { if (!cur) return false; skipPart(); } },
      Escape: { does: 'Stop for now', run: () => { if (!cur) return false; stop(); } },
    }, { label: 'Today’s run', when: () => el.isConnected });
    paint(next);
    if (host) host.append(el);
    return { el, refresh: () => paint(null) };
  }
  // L8's day rail, one segment per part: "Today 18 of 38 min" (the minutes studied today of
  // those plus what is left); o.current: false once the last part started is finished
  function runRail(host, o = {}) {
    const el = h('div', { class: 'run-rail', hidden: true, style: 'display: flex; align-items: center; gap: 10px; min-width: 0' });
    async function paint() {
      const p = await runParts();
      const n = p.done.length, all = n + p.next.length;
      el.hidden = !all;
      if (!all) return;
      const t = (shellData && shellData.today) || {}, total = (t.minutes || 0) + p.minutes;
      const at = o.current === false ? -1 : n - 1;
      el.replaceChildren(h('span', { class: 'nextup-m', style: 'white-space: nowrap',
        text: total ? `Today ${fmt(t.minutes || 0)} of ${fmt(total)} min` : `Today · part ${fmt(Math.max(1, n))} of ${fmt(all)}` }),
        h('span', { role: 'img', 'aria-label': `Part ${fmt(Math.max(1, n))} of ${fmt(all)}`, style: 'display: flex; gap: 3px; flex: 1; min-width: 48px' },
          Array.from({ length: all }, (_, i) => h('i', { style: `flex: 1; height: 6px; border-radius: 3px; background: ${i < n ? 'var(--amber)' : 'var(--line)'}${i === at ? '; opacity: .55' : ''}` }))));
    }
    paint();
    if (host) host.append(el);
    return { el, update: paint };
  }
  const run = { start: runStart, between: runBetween, rail: runRail, parts: runParts, label: runLabel,
    state: runState, on: r => !!r && r === localDay() };

  /* ------------------------------------------------------------ sheets that open by themselves (U25)
     (the shell no longer opens any by itself: Today's strip below offers the week sheet and welcome-back)
     UI.autoSheet(open) -> Promise<sheet | null>: open() runs only on a clean load (no query and
     no hash on arrival, a section root, shown rather than prerendered), and at most one sheet a
     local day opens by itself on this device (localStorage satf.sheet.day). Toasts that wait
     (kit's wait) hold until it closes. The shell offers S1's week sheet (UI.week, when it is on
     the page) and then welcome-back; when both are due the week sheet carries welcome-back. */
  const LOADED = { path: location.pathname, clean: !location.search && !location.hash };
  const ROOTS = ['/', '/practice/', '/review/', '/tests/', '/plan/', '/results/', '/me/', '/words/', '/compete/'];
  let autoOpen = null;
  function autoSheet(open) {
    if (doc.prerendering) return whenVisible(() => autoSheet(open));
    const day = localDay();
    if (autoOpen || !LOADED.clean || !ROOTS.includes(LOADED.path) || sget(LS(), 'satf.sheet.day') === day || topModal()) return Promise.resolve(null);
    const s = open() || null;
    if (s) {
      autoOpen = s;
      sput(LS(), 'satf.sheet.day', day);
      if (s.closed) s.closed.then(() => { autoOpen = null; }, () => { autoOpen = null; });
    }
    return Promise.resolve(s);
  }
  function welcomeLines(d) {
    const a = d.away, out = [];
    if (a.checks) out.push({ text: `${plural(a.checks, 'check-in')} due`, href: '/review/' });
    out.push(...contestLines(d));
    if (d.streak) out.push({ text: `Streak ${plural(d.streak, 'day')}${a.spare ? ', kept with a spare' : ''}` });
    return out;
  }
  function weekStart(d) {
    const t = new Date();
    t.setDate(t.getDate() - (t.getDay() - (d.prefs && d.prefs.week_start === 'sun' ? 0 : 1) + 7) % 7);
    return `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}-${String(t.getDate()).padStart(2, '0')}`;
  }
  let offered = false;
  // the day's week / welcome-back offer (S16): a dismissible strip at the top of Today (UI.banner), not a sheet
  // that opens by itself. Same once-a-day stamp (satf.sheet.day) and the same "shown" marks (satf.week.shown,
  // satf.welcome); they are set when the strip is dismissed or its button is tapped.
  function autoSheets(d) {
    if (offered || !d || !d.me || !UI.banner || page() !== 'today') return;
    offered = true;
    const today = localDay();
    if (sget(LS(), 'satf.sheet.day') === today) return;
    const a = d.away, gap = a && (a.since || 'long');
    const lines = a && a.days >= 2 && lget('satf.welcome', null) !== gap ? welcomeLines(d) : null;
    const week = weekStart(d);
    const wk = typeof UI.week === 'function' && lget('satf.week.shown', null) !== week;
    const it = nextItems(d)[0];             // d, not shellData: a fresh copy arrives here before it is taken
    // nothing else waiting: the line says what Pick up starts
    if (lines && !lines.length && it) lines.push({ text: [nextMeta(it), it.reason].filter(Boolean).join(' · ') });
    if (!wk && !lines) return;
    const done = () => {
      sput(LS(), 'satf.sheet.day', today);
      if (wk) lput('satf.week.shown', week);
      if (lines) lput('satf.welcome', gap);
    };
    const welcome = lines && lines.length ? h('span', {}, 'Welcome back', ...lines.flatMap(l => [' · ',
      l.href ? h('a', { class: 'link', href: l.href, text: l.text }) : l.text])) : null;
    const act = wk
      ? { label: 'Plan your week', primary: true, onClick: () => {
          done(); UI.banner.clear('sheet');
          UI.week({ welcome: lines ? h('p', { class: 'run-welcome', style: 'margin: 0 0 12px',
            text: ['Welcome back', ...lines.map(l => l.text)].join(' · ') }) : null });
        } }
      : it ? { label: `Pick up: ${it.title}`, primary: true, onClick: e => { done(); go(e.currentTarget, it); } }
        : { label: 'Practise', primary: true, href: '/practice/', onClick: done };
    UI.banner('sheet', wk ? (welcome || 'A new week: last week’s results and your goals.') : (welcome || 'Welcome back'), [act], { dismiss: true, onDismiss: done });
  }

  /* ------------------------------------------------------------ Send to a friend (U28)
     UI.share(q, {anchor}) -> Promise<url | null>, q {template, seed}. The default sends a twin:
     POST /api/sets {kind: 'set', cfg: {templates: [t], count: 1, fresh: true}, show_score:
     true}, so a friend gets the same kind of question on their own numbers and the sender's
     results card lists both. With an anchor a menu also offers Exactly this question (the ?q=
     permalink, for tutors). A touch screen gets the system share sheet, else the clipboard. */
  async function send(path, toast) {
    const url = new URL(path, location.origin).href;
    if (navigator.share && media('(pointer: coarse)')) {
      try { await navigator.share({ title: 'A question from a friend', url }); return url; }
      catch (e) { if (e && e.name === 'AbortError') return null; }
    }
    if (UI.copyText) UI.copyText(url, { toast });
    return url;
  }
  async function twinLink(q) {
    const r = await api('/sets', { method: 'POST', body: { kind: 'set', cfg: { templates: [q.template], count: 1, fresh: true }, show_score: true } });
    return send(r.url || `/s/?c=${encodeURIComponent(r.code)}`, 'Link copied: their own numbers');
  }
  function share(q, o = {}) {
    if (!q || !q.template) return Promise.resolve(null);
    const fail = e => { if (UI.toast && !(e && e.offline)) UI.toast('Couldn’t make the link. Try again.'); return null; };
    const exact = q.seed !== undefined && q.seed !== null;
    if (!o.anchor || !UI.menu || !exact) return twinLink(q).catch(fail);
    return new Promise(resolve => {
      let picked = false;
      const pick = fn => () => { picked = true; fn().then(resolve, e => resolve(fail(e))); };
      UI.menu(o.anchor, [
        { label: 'Same kind, their own numbers', sub: 'a twin', onClick: pick(() => twinLink(q)) },
        { label: 'Exactly this question', sub: 'for tutors', onClick: pick(() => send(`/practice/session/?q=${encodeURIComponent(`${q.template}:${q.seed}`)}`, 'Link copied')) },
      ], { label: 'Send to a friend', onClose: () => { if (!picked) setTimeout(() => { if (!picked) resolve(null); }); } });
    });
  }

  /* ------------------------------------------------------------ notify (U18b)
     The one way to /sw.js, for Settings › Study and the "Want a nudge at 19:00?" offer right
     after a study time is set (Plan step 3, Settings). The worker is registered and the browser
     asked only inside on(), which only a tap calls: a page load never does. Settings' shapes:
     POST /api/push/subscribe {endpoint, keys, kinds}, DELETE {endpoint}; satf.push.kinds and
     satf.push.offered hold JSON. */
  const notify = (() => {
    const KINDS = { study: true, streak: false, contest: true };
    const ios = () => /iPhone|iPad|iPod/.test(navigator.userAgent) && !matchMedia('(display-mode: standalone)').matches;
    const ok = () => !ios() && 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
    const b64 = t => Uint8Array.from(atob(t.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((t.length + 3) % 4)), c => c.charCodeAt(0));
    const key = () => api('/push/key', { quiet: true }).then(r => (r && r.key) || null, () => null);   // null: push is off here
    const json = k => { try { return JSON.parse(sget(LS(), k)); } catch (_) { return null; } };
    async function sub() {
      const reg = ok() && await navigator.serviceWorker.getRegistration('/').catch(() => null);
      return reg ? reg.pushManager.getSubscription().catch(() => null) : null;
    }
    async function on(kinds) {                 // the prompt comes first, while the tap still counts
      if (!ok()) throw new Error('unsupported');
      if (await Notification.requestPermission() !== 'granted') throw Object.assign(new Error('denied'), { denied: true });
      const k = await key();
      if (!k) throw new Error('push off');
      const reg = await navigator.serviceWorker.register('/sw.js');
      await navigator.serviceWorker.ready;
      const s = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64(k) });
      kinds = kinds || json('satf.push.kinds') || KINDS;
      const j = s.toJSON();
      await api('/push/subscribe', { method: 'POST', body: { endpoint: j.endpoint, keys: j.keys, kinds } });
      sput(LS(), 'satf.push.kinds', JSON.stringify(kinds));
      return s;
    }
    async function off() {
      const s = await sub();
      if (!s) return;
      await api('/push/subscribe', { method: 'DELETE', body: { endpoint: s.endpoint }, quiet: true }).catch(() => null);
      await s.unsubscribe().catch(() => null);
    }
    async function offer(time) {                // once ever, and only where push can work
      if (!time || !ok() || json('satf.push.offered') || Notification.permission === 'denied' || await sub() || !await key()) return;
      sput(LS(), 'satf.push.offered', '1');
      const said = e => UI.toast(e && e.denied ? 'Your browser said no. Allow notifications for this site in its settings.' : 'Couldn’t turn them on here. Try again in Settings.');
      UI.toast(`Want a nudge at ${time}?`, { ms: 8000, action: { label: 'Notify me', onClick: () => on().then(() => UI.toast('Notifications on for this device'), said) } });
    }
    return { ok, sub, on, off, offer };
  })();

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
     (Shell 2-2.6, R1; shell-me U1, U13, U14, U16, U17, U21, U25, U26; review.md R1 badge)
     UI.shell(page | {page, sections, now}) renders the chrome of every page but the session
     and the test window. Into <header id="bar">: the sidebar <nav class="side"> (248px from
     1100px wide; the 68px rail below it, or when collapsed with [ or the toggle, kept in
     localStorage satf.rail; the rail opens the full sidebar over a scrim, and peeks it on a
     400 ms rest or a held [), and the phone top bar .pbar. Into <nav id="tabs">: the five
     phone tabs, their grip (the menu sheet) and 450 ms hold menus. Into <main>: the Now strip
     and the section bar. Every figure is /api/shell's, painted from its cached copy first;
     markup and classes are ui.css's shell contract (F1). */
  const NAV = [
    { id: 'today', href: '/', label: 'Today', key: 'T', icon: 'today', tab: true, group: 'Study' },
    { id: 'practice', href: '/practice/', label: 'Practice', key: 'P', icon: 'practice', tab: true, group: 'Study' },
    { id: 'review', href: '/review/', label: 'Review', key: 'M', icon: 'review', group: 'Study' },
    { id: 'words', href: '/words/', label: 'Words', key: 'W', icon: 'words', group: 'Study' },
    { id: 'tests', href: '/tests/', label: 'Tests', key: 'E', icon: 'tests', tab: true, group: 'Study' },
    { id: 'plan', href: '/plan/', label: 'Plan', key: 'L', icon: 'plan', tab: true, group: 'Study' },
    { id: 'results', href: '/results/', label: 'Results', key: 'R', icon: 'results', tab: true, group: 'Progress' },
    { id: 'compete', href: '/compete/', label: 'Compete', key: 'C', icon: 'compete', group: 'Progress' },
    { id: 'me', href: '/me/', label: 'Profile', key: 'U', icon: 'profile', group: 'Progress' },
  ];
  // the section mapping (Shell 2.2, R1, U26): a page's data-page, and the item it lights
  const SECTION = { session: 'practice', mistakes: 'review', report: 'results', challenge: 'compete',
    diagnostic: 'tests', test: 'tests', settings: 'me', signin: 'me', link: 'me', pair: 'me' };
  const W_SIDE = '(min-width: 1100px)', W_PHONE = '(max-width: 759px)';
  const DAYS3 = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const fmt = n => Number(n || 0).toLocaleString('en-US');
  const cap99 = n => n > 999 ? '999+' : fmt(n);
  const plural = (n, one, many = one + 's') => `${fmt(n)} ${n === 1 ? one : many}`;
  // UI.icon(name, size) -> svg node; an unknown name draws nothing ('' appends as nothing) and warns on localhost
  const icon = (name, size = 20) => {
    if (!ICON[name]) { if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) console.warn(`UI.icon: no icon "${name}"`); return ''; }
    const t = doc.createElement('template'); t.innerHTML = svg(ICON[name], size); return t.content.firstElementChild;
  };
  const dot = () => h('i', { class: 'dot', 'aria-hidden': 'true' });
  const shown = el => !!el && el.offsetWidth > 1;
  const lget = (k, d) => { try { const v = JSON.parse(sget(LS(), k) || 'null'); return v === null ? d : v; } catch (_) { return d; } };
  const lput = (k, v) => sput(LS(), k, v === null ? null : JSON.stringify(v));

  /* ---- what each figure says */
  const planOf = d => d && d.plan && plan.set(d.plan) ? d.plan : null;
  function dayKind(d) {                  // test | practice | rest | exam | none, for today
    const p = planOf(d);
    return p ? plan.dayOf(new Date(), p) : null;
  }
  function nextTest(d) {                 // "Sat": the next test day within 7 days
    const p = planOf(d);
    if (!p) return null;
    if (p.next_test) return DAYS3[new Date(p.next_test + 'T12:00:00').getDay()];
    const t = new Date();
    for (let i = 1; i <= 7; i++) {
      t.setDate(t.getDate() + 1);
      const k = plan.dayOf(t, p);
      if (k === 'test') return DAYS3[t.getDay()];
      if (k === 'exam' || k === 'none') return null;
    }
    return null;
  }
  function dayDone(d) {                  // the Plan section's day rule when it is here (S7)
    const t = d.today || {};
    if (typeof t.done === 'boolean') return t.done;
    if (typeof plan.doneOf === 'function' && planOf(d)) { try { return !!plan.doneOf(d.plan, t); } catch (_) {} }
    return !!(t.goal && t.goal.questions && t.questions >= t.goal.questions);
  }
  const testResume = d => d.resume && d.resume.kind !== 'drill' ? d.resume : null;
  const seenReport = () => sget(LS(), 'satf.seen.report');
  const reportNew = d => !!d.newest_report && d.newest_report !== seenReport();
  function reviewCounts(d) {
    const r = d.review || {};
    return { due: r.due_left || 0, open: r.open ?? d.mistakes ?? 0 };
  }
  const goalsDone = d => (d.goals || []).filter(g => g.done).length;

  // one meta per nav item: {text, node, rail: 'count' | 'dot', count, tip, ring}
  function metaOf(id, d) {
    const t = d.today || {};
    switch (id) {
      case 'today': {
        const goal = t.goal && t.goal.questions;
        const ring = goal ? Math.min(1, (t.questions || 0) / goal) : null;
        if (dayDone(d)) return { node: [icon('check', 14), 'Done'], say: 'Done', tip: 'Today’s plan is done', ring: 1 };
        if (!t.questions) return goal ? { tip: `0 of ${plural(goal, 'question')} today`, ring: 0 } : null;
        return { text: goal ? `${fmt(t.questions)}/${fmt(goal)}` : fmt(t.questions), ring,
                 tip: goal ? `${fmt(t.questions)} of ${plural(goal, 'question')} today` : `${plural(t.questions, 'question')} today` };
      }
      case 'practice': {
        const r = d.resume && d.resume.kind === 'drill' ? d.resume : null;
        return r ? { node: h('span', { class: 'badge soft', text: 'Resume' }), say: 'Resume', rail: 'dot',
                     tip: `Resume your set${r.total ? ` · ${fmt(r.answered)}/${fmt(r.total)}` : ''}` } : null;
      }
      case 'review': {
        const { due, open } = reviewCounts(d);
        if (!due && !open) return null;
        const long = [due ? `${fmt(due)} due today` : null, open ? `${fmt(open)} open` : null].filter(Boolean).join(' · ');
        return { node: due ? `${cap99(due)} due${open ? ` · ${cap99(open)} open` : ''}` : [dot(), `${cap99(open)} open`],
                 rail: 'count', count: cap99(due || open), tip: long };
      }
      case 'words': {
        const n = (d.words && d.words.due) || 0;
        return n ? { text: `${cap99(n)} due`, rail: 'dot', tip: `${plural(n, 'word')} due` } : null;
      }
      case 'tests': {
        const r = testResume(d);
        if (r) {
          const left = r.seconds_left ? ` · ${mmss(r.seconds_left)} left` : r.paused ? ' · paused' : '';
          return { node: h('span', { class: 'badge soft', text: 'Resume' }), say: 'Resume', rail: 'dot',
                   tip: `Resume ${(UI.KIND && UI.KIND[r.kind] || r.kind).toLowerCase()} · ${fmt(r.answered)}/${fmt(r.total)}${left}` };
        }
        return dayKind(d) === 'test' && !d.tested_today ? { text: 'Test day', rail: 'dot', tip: 'Today is a test day in your plan' } : null;
      }
      case 'plan': {
        const k = dayKind(d);
        if (!planOf(d) || k === 'none') return { text: 'Set up', tip: 'No plan yet: set one up in 3 steps' };
        if (k === 'exam') return { text: 'Exam day', tip: 'Today is the SAT. Good luck.' };
        if (k === 'rest') return { text: 'Rest', tip: 'A rest day in your plan: your streak is safe' };
        if (k === 'test') return { text: 'Test day', tip: 'Today is a test day in your plan' };
        const nt = nextTest(d);
        return nt ? { text: `Test ${nt}`, tip: `Your next test day is ${nt}` } : null;
      }
      case 'results':
        return reportNew(d) ? { node: [dot(), 'New'], say: 'New', rail: 'dot', tip: 'A new report since you last looked' } : null;
      case 'compete': {
        const c = d.challenge || {};
        if (c.done) return c.rank ? { text: `#${fmt(c.rank)}`, tip: `Today’s challenge: #${fmt(c.rank)} of ${fmt(c.players)}` } : { text: 'Done', tip: 'Today’s challenge is done' };
        if (c.started) return { text: 'Resume', rail: 'dot', tip: 'Today’s challenge: started, not finished' };
        return { text: 'New', rail: 'dot', tip: 'Today’s challenge: not played yet' };
      }
      case 'me': {
        const g = d.goals || [];
        if (!g.length) return null;
        const tip = h('span', {}, h('b', { text: `This week · ${goalsDone(d)} of ${g.length} goals` }),
          ...g.map(x => h('span', { style: 'display: block' }, `${x.done ? '●' : '○'} ${x.title}`,
            x.target ? h('span', { class: 'm', text: ` · ${fmt(Math.min(x.have || 0, x.target))}/${fmt(x.target)}` }) : null)));
        return { text: `${goalsDone(d)}/${g.length}`, tip };
      }
    }
    return null;
  }

  /* ---- the Today card (Shell 2.2 item 7, U16, U17, U26): the sidebar's, the Now strip's
     and the menu sheet's. Figures open their working (U13, kit's [data-fact]). */
  const flame = (size, spare) => { const e = icon('flame', size); if (spare) e.querySelector('.flame').removeAttribute('class'); return e; };
  const unreadOf = x => (typeof x === 'number' ? x : x && typeof x === 'object' ? Number(x.unread ?? x.count ?? x.n ?? 0) || 0 : 0);
  function streakText(d) {
    const sp = d.spares || 0;
    return `${plural(d.streak || 0, 'day')}${sp ? ` · ${plural(sp, 'spare')}` : ''}`;
  }
  function examLine(d) {
    const e = d.today && d.today.exam;
    if (!e || e.days < 0) return null;
    const when = e.days === 0 ? 'Exam today' : e.days === 1 ? 'Exam tomorrow' : `Exam in ${fmt(e.days)} days`;
    return `${when} · ${UI.date ? UI.date(e.date) : day(e.date)}`;
  }
  function regLine(d) {
    const r = d.registration;
    if (!r) return null;
    const on = UI.date ? UI.date(r.day) : day(r.day);
    return r.late ? `Late registration for ${on} · until ${UI.date ? UI.date(r.late_by) : day(r.late_by)}`
      : `Register for ${on} · ${r.days_left ? plural(r.days_left, 'day') + ' left' : 'last day'}`;
  }
  function contestLines(d) {
    return ((d.today && d.today.contest) || []).map(c => ({
      text: `${c.title || 'Your contest'} closes ${c.when || c.closes_label || (c.closes ? 'at ' + String(c.closes).slice(11, 16) : 'soon')}`,
      href: c.href || '/compete/' }));
  }
  function cardLines(d) {                // the card as text: the rail ring's tooltip
    const t = d.today || {}, goal = t.goal;
    return [`Today · streak ${streakText(d)}`,
      !d.answered ? 'Nothing yet today' : goal && goal.minutes ? `Study time ${fmt(t.minutes)} of ${fmt(goal.minutes)} min` : `${fmt(t.minutes)} min today`,
      regLine(d), ...contestLines(d).map(c => c.text), examLine(d)].filter(Boolean);
  }
  function todayCard(d, o = {}) {
    const card = h('div', { class: 'side-day' });
    if (!d) {
      card.append(h('div', { class: 'side-day-head' }, h('span', { class: 'k', text: 'Today' })));
      if (UI.skel) card.append(UI.skel(null, 'lines:2'));
      return card;
    }
    const t = d.today || {}, goal = t.goal, streak = d.streak || 0;
    // how a figure is worked out opens from GET /api/levers (S1); until it is served the
    // flame goes to the activity heatmap (§2.2.7) and the minutes are plain text
    const facts = has('levers');
    const fact = (key, label, value) => facts ? { 'data-fact': key, 'data-fact-label': label, 'data-fact-value': value } : {};
    const st = h(facts ? 'button' : 'a', { type: facts ? 'button' : null, href: facts ? null : '/me/#activity',
      class: 'streak' + (streak > 0 ? ' on' : ''), ...fact('streak', 'Streak', streakText(d)) },
      flame(16), h('span', { text: o.compact ? plural(streak, 'day') : streakText(d) }),
      // one small outlined flame per banked spare (U16); the narrow sidebar card says it with these
      Array.from({ length: d.spares || 0 }, () => flame(12, true)),
      o.compact && d.spares ? h('span', { class: 'sr', text: ` · ${plural(d.spares, 'spare')}` }) : null);
    st.style.whiteSpace = 'nowrap';
    // the sidebar's card (compact) says the goal as a small ring beside Today, minutes inside, instead of a meter
    // that says the same thing (BUILD A1 hand-off); the menu sheet and Now strip keep the meter
    const ringGoal = o.compact && goal && goal.minutes && (d.answered || t.minutes);
    const today = h('a', { class: 'k', href: '/plan/', text: 'Today', style: 'text-decoration: none' });
    let lead = today;
    if (ringGoal) {
      const say = `${fmt(t.minutes || 0)} of ${fmt(goal.minutes)} min`;
      const gr = h(facts ? 'button' : 'a', { type: facts ? 'button' : null, href: facts ? null : '/plan/', class: 'ring side-goal',
        style: `--p: ${Math.min(1, (t.minutes || 0) / goal.minutes)}; text-decoration: none`, 'aria-label': `Study time: ${say}`,
        ...fact('minutes:today', 'Study time today', say) }, h('span', { 'aria-hidden': 'true', text: fmt(t.minutes || 0) }));
      if (UI.tooltip) UI.tooltip(gr, `Study time · ${say}`);
      lead = h('span', { class: 'side-day-goal' }, gr, today);
    }
    card.append(h('div', { class: 'side-day-head' }, lead, st));
    if (!d.answered && !t.minutes) {
      card.append(h('p', { text: 'Nothing yet today' }));
      if (!goal) card.append(h('a', { class: 'link', href: '/plan/', text: 'Set a daily goal' }));
    } else if (ringGoal) {
      // the ring in the head carries it
    } else if (goal && goal.minutes && UI.meter) {
      const m = UI.meter(card, { label: 'Study time', value: t.minutes || 0, max: goal.minutes, unit: 'min' });
      const n = m.el.querySelector('.meter-n');
      if (n && facts) Object.assign(n.dataset, { fact: 'minutes:today', factLabel: 'Study time today', factValue: n.textContent });
    } else {
      const mins = `${fmt(t.minutes)} min today`;
      card.append(h('p', {}, facts ? h('button', { type: 'button', ...fact('minutes:today', 'Study time today', mins), text: mins }) : mins));
      if (!goal) card.append(h('a', { class: 'link', href: '/plan/', text: 'Set a daily goal' }));
    }
    const reg = regLine(d);
    if (reg) card.append(h('a', { class: 'link', href: 'https://satsuite.collegeboard.org/sat/registration', target: '_blank', rel: 'noopener' }, reg, ' ', icon('external', 14)));
    contestLines(d).forEach(c => card.append(h('p', {}, c.text, ' · ', h('a', { class: 'link', href: c.href, text: 'Start' }))));
    const ex = examLine(d);
    if (ex) card.append(h('a', { class: 'side-day-foot', href: '/plan/', text: ex, style: 'text-decoration: none' }));
    // the rail's form: minutes against the goal as an orange arc, the streak inside
    const ring = h('a', { class: 'ring', href: '/plan/', style: `--p: ${goal && goal.minutes ? Math.min(1, (t.minutes || 0) / goal.minutes) : 0}; text-decoration: none`,
      'aria-label': cardLines(d).join('. '), text: String(streak) });
    card.append(ring);
    if (UI.tooltip) UI.tooltip(ring, () => sideEl && sideEl.classList.contains('rail') ? h('span', {}, ...cardLines(d).map(x => h('span', { style: 'display: block', text: x }))) : '');
    return card;
  }

  /* ---- Up next (U1): the sidebar block, the Now strip cell, the menu sheet's first row */
  const BOXES = [5, 10, 15, 20, 30, 45, 60];        // one set of time boxes everywhere (review.md V1)
  function nextMeta(it) {
    const n = it.start && it.start.body && (it.start.body.count || it.start.body.n);
    return [it.detail || (n ? `${fmt(n)} q` : null), it.minutes ? `${fmt(it.minutes)} min` : null,
      it.pts >= 1 ? `≈ ${fmt(Math.round(it.pts))} pts` : null].filter(Boolean).join(' · ');
  }
  function snooze(it) {
    const s = lget('satf.next.snooze', {}) || {};
    const today = localDay();
    for (const k in s) if (s[k] !== today) delete s[k];
    s[it.key] = today;
    lput('satf.next.snooze', s);
    if (shellData) takeShell(shellData, false);
  }
  async function go(btn, it) {
    if (btn.getAttribute('aria-busy') === 'true') return;
    btn.setAttribute('aria-busy', 'true');
    try { await start(it); }
    catch (e) { btn.removeAttribute('aria-busy'); if (UI.toast && !e.offline) UI.toast('Couldn’t start it. Try again.'); }
  }
  const startBtn = (it, label = 'Start', kbd, cls = 'pill sm') => {
    const b = h(it.href ? 'a' : 'button', { class: cls, href: it.href || null, type: it.href ? null : 'button' }, label, kbd && !media('(pointer: coarse)') ? keycaps(kbd) : null);
    if (!it.href) b.addEventListener('click', () => go(b, it));
    return b;
  };
  // on a --tile surface (the menu sheet) the chips go paper and scroll sideways in one row
  function boxChips(onTile, list = BOXES) {
    return h('div', { class: 'chips', role: 'group', 'aria-label': 'Got time? Start a time box',
      style: onTile ? 'flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; margin-top: 4px' : null },
      h('span', { class: 'help', text: 'Got time?', style: 'margin: 0 4px 0 0; align-self: center; flex: none' }),
      list.map(m => { const b = h('button', { type: 'button', text: `${m} min`, style: onTile ? 'background: var(--paper)' : null });
        b.addEventListener('click', () => go(b, { start: { path: '/drill', body: { source: 'next', box: m } } }));
        return b; }));
  }
  function morePop(trigger) {
    if (!UI.pop) return;
    const list = h('div', { style: 'display: grid; gap: 10px; min-width: 260px; max-width: 340px' });
    const fill = items => {
      list.replaceChildren(h('span', { class: 'k', text: 'Up next' }));
      if (!items.length) list.append(h('p', { class: 'help', text: 'Nothing else is up next right now.' }));
      items.forEach((it, i) => list.append(h('div', { class: 'mup-row' },
        h('b', { text: it.title, style: 'font-weight: 600' }), h('span', { class: 'nextup-m', text: nextMeta(it) }),
        it.reason ? h('span', { class: 'nextup-r', text: it.reason }) : null,
        h('div', { class: 'mup-acts' }, startBtn(it, 'Start'),
          h('button', { type: 'button', class: 'quiet', text: 'Not today', onclick: () => { snooze(it); pop.close(); } })))));
      list.append(boxChips());
    };
    fill(nextItems());
    const pop = UI.pop(trigger, list, { label: 'More up next' });
    // the five after the first come from GET /api/next (U1); the shell carries three
    if (has('next')) api('/next?limit=6', { quiet: true }).then(r => {
      const snoozed = lget('satf.next.snooze', {}) || {}, today = localDay();
      if (r && Array.isArray(r.items) && list.isConnected) { fill(r.items.filter(x => snoozed[x.key] !== today)); pop && pop.reposition && pop.reposition(); }
    }, () => {});
  }
  function nextBlock(d, o = {}) {
    const el = h('div', { class: 'nextup' });
    if (!d) {                             // loading: two skeleton lines
      el.append(h('span', { class: 'k', text: 'Up next' }));
      if (UI.skel) el.append(UI.skel(null, 'lines:2'));
      return el;
    }
    const it = nextItems()[0];
    if (!it) { el.hidden = true; return el; }        // nothing, or an error: the block hides
    el.append(h('span', { class: 'k', text: 'Up next' }), h('span', { class: 'nextup-t', text: it.title }));
    el.title = nextTip(it);   // the title and Start are enough; the check-ins, minutes and reason are a tooltip
    const more = h('button', { type: 'button', class: 'ibtn', 'aria-label': 'More up next', 'aria-haspopup': 'dialog' }, icon('chev', 18));
    more.addEventListener('click', () => morePop(more));
    el.append(h('div', { class: 'nextup-go' }, startBtn(it, 'Start', o.kbd === false ? null : 'G N', o.quiet ? 'btn sm' : undefined), more));
    if (o.boxes) el.append(boxChips(true));
    return el;
  }
  const nextTip = it => `Next: ${it.title}${nextMeta(it) ? ' · ' + nextMeta(it) : ''}${it.reason ? ' · ' + it.reason : ''}`;

  /* ---- the sidebar and the rail */
  let sideEl = null, pbarEl = null, tabsEl = null, scrimEl = null, overlay = null, here = '', rest = 0;
  const refs = { items: {}, tabs: {} };
  const layoutMode = () => media(W_PHONE) ? 'phone' : media(W_SIDE) && sget(LS(), 'satf.rail') !== '1' ? 'side' : 'rail';
  function tip(el, text, kbd) {
    if (!UI.tooltip) return;
    UI.tooltip(el, () => {
      const t = typeof text === 'function' ? text() : text;
      if (!t) return '';
      return kbd && !media('(pointer: coarse)') ? h('span', {}, t, ' ', keycaps(kbd)) : t;
    });
  }
  function navItem(n) {
    // the current item carries the one .nav-mark (motion.css names it), so a page change slides it from
    // the old item to the new (MOTION N2)
    const a = h('a', { class: 'side-item', href: n.href, 'data-id': n.id, 'aria-current': n.id === here ? 'page' : null },
      icon(n.icon), h('span', { class: 'side-text', text: n.label }), h('span', { class: 'side-meta' }),
      n.id === here ? h('span', { class: 'nav-mark', 'aria-hidden': 'true' }) : null);
    refs.items[n.id] = { el: a, meta: null };
    // the rail's tooltip: name, meta, shortcut; the expanded sidebar's: what the meta stands for
    tip(a, () => {
      const m = refs.items[n.id].meta;
      const rail = !shown(a.querySelector('.side-text'));
      if (!rail) return m && m.tip ? m.tip : '';
      const t = m && m.tip;
      return t instanceof Node ? h('span', {}, h('b', { text: n.label }), t) : `${n.label}${t ? ' · ' + t : ''}`;
    }, `G ${n.key}`);
    return a;
  }
  function brand() {
    const box = sideEl.querySelector('.side-brand');
    const railNow = sideEl.classList.contains('rail');
    const word = h('span', { class: 'side-word', html: 'SAT<br>Freshman' });
    // on the rail the mark is the expand toggle, since Today is already a nav item (U26)
    const markEl = railNow
      ? h('button', { type: 'button', class: 'side-mark ibtn', style: '--ib: var(--rt, 44px)', 'aria-label': 'Expand sidebar', 'aria-expanded': 'false', html: mark(26) }, word)
      : h('a', { class: 'side-mark', href: '/', 'aria-label': 'SAT Freshman, Today', html: mark(26) }, word);
    if (railNow) { markEl.addEventListener('click', toggle); tip(markEl, 'Expand sidebar', '['); }
    const wide = media(W_SIDE);
    const label = overlay ? (wide ? 'Keep sidebar open' : 'Close sidebar') : 'Collapse sidebar';
    const tog = h('button', { type: 'button', class: 'ibtn side-toggle', 'aria-label': label, 'aria-expanded': String(!railNow) }, icon('panel'));
    tog.addEventListener('click', toggle);
    tip(tog, () => overlay ? label : 'Collapse', '[');
    box.replaceChildren(markEl, tog);
    paintSide(shellData);                // metas take their rail or full form
  }
  function buildSide() {
    const search = h('button', { type: 'button', class: 'side-search', 'aria-label': 'Search' }, icon('search', 18),
      h('span', { class: 'side-text', text: 'Search' }), keycaps('Mod+K'));
    search.addEventListener('click', () => UI.palette());
    tip(search, () => shown(search.querySelector('.side-text')) ? '' : 'Search', 'Mod+K');
    const quick = h('button', { type: 'button', class: 'side-quick', 'aria-label': 'Quick question, log a mistake or add a word' }, icon('bolt', 18),
      h('span', { class: 'side-text', text: 'Quick' }), keycaps('Q'));
    quick.addEventListener('click', () => UI.quick());
    tip(quick, () => shown(quick.querySelector('.side-text')) ? '' : 'Quick question · Log a mistake · Add a word', 'Q');
    const play = h('a', { class: 'side-play', href: '#', 'aria-label': 'Start Up next', hidden: true }, icon('play', 18));
    play.addEventListener('click', e => { e.preventDefault(); const it = nextItems()[0]; if (it) go(play, it); });
    tip(play, () => { const it = nextItems()[0]; return it ? nextTip(it) : ''; }, 'G N');
    const groups = ['Study', 'Progress'].map(g => {
      const id = `side-${g.toLowerCase()}`;
      return h('div', { class: 'side-group', role: 'group', 'aria-labelledby': id },
        h('span', { class: 'side-label', id, text: g }), NAV.filter(n => n.group === g).map(navItem));
    });
    const help = h('a', { href: '/help/', 'aria-current': here === 'help' ? 'page' : null }, icon('help', 18), h('span', { class: 'side-text', text: 'Help & FAQ' }));
    const fb = h('button', { type: 'button' }, icon('chat', 18), h('span', { class: 'side-text', text: 'Send feedback' }));
    fb.addEventListener('click', feedback);
    tip(help, () => shown(help.querySelector('.side-text')) ? '' : 'Help & FAQ', 'G H');
    tip(fb, () => shown(fb.querySelector('.side-text')) ? '' : 'Send feedback');
    const user = h('button', { type: 'button', class: 'side-user', 'aria-haspopup': 'menu', 'aria-expanded': 'false' }, h('span', { class: 'avatar' }), h('span', { class: 'side-name', text: '' }),
      h('span', { class: 'side-sub', text: '' }), icon('chev', 16));
    menuTrigger(user);
    tip(user, () => {
      const d = shellData || {};
      if (d.device && d.device.session_only) return 'Shared computer: ends 15 minutes after you stop, or about a minute after you close the browser.';
      return shown(user.querySelector('.side-name')) ? '' : `${(d.me && d.me.label) || 'You'} · account`;
    });
    sideEl = h('nav', { class: 'side' + (sget(LS(), 'satf.nowfold') === '1' ? ' now-folded' : ''), 'aria-label': 'Main' },
      h('div', { class: 'side-brand' }), search, h('div', { class: 'nextup' }), play, quick,
      h('div', { class: 'side-nav' }, groups), h('div', { class: 'side-day' }),
      h('div', { class: 'side-foot' }, help, fb), user);
    Object.assign(refs, { search, quick, play, user });
    edgeFade(sideEl.querySelector('.side-nav'));
    // close the overlay when a link in it is followed; peek on a 400 ms rest (U26)
    sideEl.addEventListener('click', e => { if (overlay && e.target.closest('a[href]')) closeOverlay(); });
    sideEl.addEventListener('pointerenter', e => {
      if (e.pointerType !== 'mouse' || !sideEl.classList.contains('rail')) return;
      clearTimeout(rest); rest = setTimeout(() => openOverlay('peek'), 400);
    });
    sideEl.addEventListener('pointerleave', () => {
      clearTimeout(rest);
      // a menu or popover opened from the peek keeps it open
      if (overlay === 'peek' && !sideEl.querySelector('.side-user[aria-expanded="true"], .nextup [aria-expanded="true"]')) closeOverlay();
    });
    return sideEl;
  }

  function layout() {
    if (!sideEl) return;
    if (overlay) closeOverlay(false);
    const m = layoutMode();
    sideEl.classList.toggle('rail', m !== 'side');
    doc.body.classList.toggle('has-side', m === 'side');
    doc.body.classList.toggle('has-rail', m !== 'side');
    brand();
    observeStuck();
    paintStrip();
  }
  function openOverlay(how) {
    clearTimeout(rest);                  // a click or [ beats the pending peek, and Esc then stays closed
    if (overlay || !sideEl.classList.contains('rail') || media(W_PHONE)) return;
    overlay = how;
    sideEl.classList.remove('rail');
    sideEl.classList.add('open');
    scrimEl = h('div', { class: 'scrim', 'aria-hidden': 'true' });
    scrimEl.addEventListener('click', () => closeOverlay());
    sideEl.before(scrimEl);
    brand();
    if (how !== 'peek') sideEl.querySelector('.side-toggle').focus({ preventScroll: true });
  }
  function closeOverlay(focus = true) {
    if (!overlay) return;
    const had = sideEl.contains(doc.activeElement);
    overlay = null;
    if (scrimEl) { const sc = scrimEl; if (UI.motion) UI.motion.exit(sc, 'fade').then(() => sc.remove()); else sc.remove(); }
    scrimEl = null;
    sideEl.classList.remove('open');
    sideEl.classList.add('rail');
    brand();
    if (focus && had) { const b = sideEl.querySelector('.side-mark'); if (b) b.focus({ preventScroll: true }); }
  }
  // the toggle and [: collapse or expand (1100px wide and up), or open the overlay (760-1099)
  // a click glides the edge between 248 and 68 (a same-document view transition, motion.css vt-rail); [ is instant
  function toggle(e) {
    if (!sideEl || media(W_PHONE)) return;
    const wide = media(W_SIDE);
    const glide = fn => (UI.motion ? UI.motion.vt(fn, { cls: 'vt-rail', event: e }) : fn());
    if (overlay) { if (wide) glide(() => { sput(LS(), 'satf.rail', null); layout(); }); else closeOverlay(); return; }
    if (wide) { glide(() => { sput(LS(), 'satf.rail', sideEl.classList.contains('rail') ? null : '1'); layout(); focusToggle(); }); return; }
    openOverlay('toggle');
  }
  const focusToggle = () => { const b = sideEl.querySelector(sideEl.classList.contains('rail') ? '.side-mark' : '.side-toggle'); if (b && sideEl.contains(doc.activeElement)) b.focus({ preventScroll: true }); };
  // [ taps toggle; held 300 ms on the rail it peeks until released (U26)
  let brHeld = 0, brPeek = false;
  function bracket(e) {
    if (e.repeat) return;
    brPeek = false;
    clearTimeout(brHeld);
    if (sideEl.classList.contains('rail') && !overlay) brHeld = setTimeout(() => { brPeek = true; openOverlay('peek'); }, 300);
    const up = ev => {
      if (ev.key !== '[') return;
      removeEventListener('keyup', up, true);
      clearTimeout(brHeld);
      if (brPeek) closeOverlay(false); else toggle();
    };
    addEventListener('keyup', up, true);
  }
  addEventListener('keydown', e => {
    if (e.key !== 'Escape' || !overlay || doc.querySelector('.menu, .popover, dialog[open]')) return;
    e.preventDefault();
    e.stopPropagation();
    closeOverlay();
  }, true);

  function paintSide(d) {
    if (!sideEl) { paintUser(d); return; }           // the focus chrome: only its account button
    const rail = sideEl.classList.contains('rail');
    for (const n of NAV) {
      const r = refs.items[n.id], m = d ? metaOf(n.id, d) : null;
      r.meta = m;
      const slot = r.el.querySelector('.side-meta');
      // on the rail a meta is an orange count bubble or a 7px dot (ui.css); its words stay for
      // screen readers, and the tooltip carries them in full
      if (!m) slot.replaceChildren();
      else if (rail && m.rail === 'count') slot.replaceChildren(h('span', { 'aria-hidden': 'true', text: m.count }), h('span', { class: 'sr', text: m.tip }));
      else if (rail && m.rail === 'dot') slot.replaceChildren(m.say || m.text || '');
      else slot.replaceChildren(...[].concat(m.node || m.text || []));
      if (m && m.rail) slot.dataset.rail = m.rail; else delete slot.dataset.rail;
      if (n.id === 'today') {
        if (m && m.ring !== null && m.ring !== undefined) { r.el.dataset.ring = ''; r.el.style.setProperty('--p', m.ring); }
        else { delete r.el.dataset.ring; r.el.style.removeProperty('--p'); }
      }
    }
    const nb = nextBlock(d, { quiet: ownPrimary });
    sideEl.querySelector('.nextup').replaceWith(nb);
    // the Now card folds to one line (title and Start) and remembers it (satf.nowfold); the Today card leaves with it
    if (d && !nb.hidden) {
      const folded = sideEl.classList.contains('now-folded');
      const fold = h('button', { type: 'button', class: 'ibtn now-fold', 'aria-expanded': String(!folded),
        'aria-label': folded ? 'Show Up next and Today in full' : 'Fold Up next and Today to one line' }, icon('chev', 16));
      // the card folds to one line in a glide: Today leaves, the nav slides up (B1, motion.css vt-fold)
      fold.addEventListener('click', e => {
        const go = () => {
          sideEl.classList.toggle('now-folded', !folded);
          sput(LS(), 'satf.nowfold', folded ? '' : '1');
          paintSide(shellData);
          const again = sideEl.querySelector('.now-fold');
          if (again) again.focus();
        };
        if (UI.motion) UI.motion.vt(go, { cls: 'vt-fold', event: e, names: { '.side .nextup': 'm-nextup', '.side .side-day': 'm-day', '.side .side-nav': 'm-nav' } });
        else go();
      });
      tip(fold, () => folded ? 'Show in full' : 'Fold to one line');
      nb.append(fold);
    }
    const it = d && nextItems()[0];
    refs.play.hidden = !it;
    refs.play.classList.toggle('own', ownPrimary);
    if (it) refs.play.setAttribute('aria-label', `Start Up next: ${it.title}`);
    const was = sideEl.querySelector('.side-day'), card = todayCard(d, { compact: true });
    was.replaceWith(card);
    carry(was, card, d);
    paintUser(d);
  }
  // a repaint that moved a figure (fresh data on this page, never the first paint): the ring and the study
  // time sweep from where they were (D4, D3), a goal met beats once a day (F6), a longer streak rolls its
  // number and fills its flame (F5)
  let lastStreak = null;
  function carry(was, card, d) {
    const streak = d ? d.streak || 0 : null, grew = lastStreak !== null && streak > lastStreak;
    if (d) lastStreak = streak;
    if (!d || !UI.fx || !was.querySelector('.streak')) return;
    const r0 = [...was.querySelectorAll('.ring')], r1 = [...card.querySelectorAll('.ring')];
    const met = r0.length === r1.length && r1.some((r, i) => (parseFloat(r0[i].style.getPropertyValue('--p')) || 0) < 1 && (parseFloat(r.style.getPropertyValue('--p')) || 0) >= 1);
    const beat = met && UI.motion.once('goal', 'local');
    if (r0.length === r1.length) r1.forEach((r, i) => {
      const a = parseFloat(r0[i].style.getPropertyValue('--p')) || 0, b = parseFloat(r.style.getPropertyValue('--p')) || 0;
      if (Math.abs(a - b) > .001) { r.style.setProperty('--p', a); UI.fx.ring(r, b, { beat }); }
    });
    const m0 = was.querySelector('.meter-bar'), m1 = card.querySelector('.meter-bar');
    if (m0 && m1) {
      const a = m0.style.getPropertyValue('--p'), b = m1.style.getPropertyValue('--p');
      if (a && a !== b && UI.motion.ok()) { m1.style.setProperty('--p', a); void m1.offsetWidth; m1.style.setProperty('--p', b); }
    }
    if (grew) {
      const st = card.querySelector('.streak'), n0 = was.querySelector('.streak > span'), n1 = st && st.querySelector(':scope > span');
      if (n0 && n1 && UI.roll) { const to = n1.textContent; n1.textContent = n0.textContent; UI.roll(n1, to); }
      if (st) UI.fx.flame(st);
      if (refs.streak && !refs.streak.hidden) UI.fx.flame(refs.streak);
    }
  }
  function paintUser(d) {
    const u = refs.user;
    if (!u) return;
    const me = (d && d.me) || {};
    u.querySelector('.avatar').replaceWith(avatarOf(d, 34));
    u.querySelector('.side-name').textContent = me.label || (d ? 'You' : 'Account');   // no data (offline, retired): a neutral name, never a blank card
    const sub = u.querySelector('.side-sub');
    const sharedPc = d && d.device && d.device.session_only;
    const unread = unreadOf(d && d.inbox);
    if (!d) sub.textContent = '';
    else if (sharedPc) sub.replaceChildren('Shared computer');   // one line; the tooltip and the menu's Sign out say the rest
    else if (me.linked) sub.replaceChildren(me.email_masked || 'Saved');
    else sub.replaceChildren(dot(), 'Not saved yet');
    const old = u.querySelector('.badge.n');
    if (old) old.remove();
    if (unread) u.querySelector('.side-name').append(' ', h('span', { class: 'badge n soft', text: cap99(unread), 'aria-label': `${plural(unread, 'unread item')}` }));
    u.setAttribute('aria-label', `${me.label || 'You'}${d && !me.linked && !sharedPc ? ', not saved yet' : ''}${unread ? `, ${plural(unread, 'unread item')}` : ''}, account menu`);
  }
  function avatarOf(d, size) {
    const me = (d && d.me) || {}, a = me.avatar || {};
    if (!UI.avatar || !d) return h('span', { class: 'avatar' + (size >= 40 ? ' lg' : ''), html: mark(size >= 40 ? 22 : 16, 'var(--soft)') });
    return UI.avatar({ name: me.name || me.label, avatar: a.kind === 'glyph' ? a.glyph : a.kind === 'initial' ? 'initial' : 'mark',
      ring: a.ring, domains: me.domains, self: true, learner: learner() }, size);
  }

  /* ---- the phone: the top bar, the five tabs, the grip and the hold menus (Shell 2.4, U26) */
  function buildPbar() {
    const search = h('button', { type: 'button', class: 'ibtn', 'aria-label': 'Search' }, icon('search'));
    search.addEventListener('click', () => UI.palette());
    const chip = h('a', { class: 'pbar-chip', href: '/review/', hidden: true, 'aria-current': here === 'review' ? 'page' : null });
    // hidden until the shell's figures arrive, so no data never reads as a 0-day streak
    const streak = h('a', { class: 'streak', href: '/me/#activity', hidden: true, style: 'min-height: 40px; padding: 0 2px' }, flame(16), h('span', { text: '' }));
    const quick = h('button', { type: 'button', class: 'ibtn', 'aria-label': 'Quick question or log a mistake' }, icon('bolt'));
    quick.addEventListener('click', () => UI.quick());
    const meBtn = h('button', { type: 'button', class: 'ibtn pbar-me', 'aria-label': 'Menu', 'aria-haspopup': 'dialog' }, h('span', { class: 'avatar' }));
    meBtn.addEventListener('click', () => menuSheet(meBtn));
    pbarEl = h('div', { class: 'pbar' },
      h('a', { class: 'pbar-mark', href: '/', 'aria-label': 'SAT Freshman, Today', html: mark(26) }),
      search, h('span', { class: 'pbar-grow' }), chip, streak, quick, meBtn);
    Object.assign(refs, { chip, streak, meBtn });
    const onScroll = () => pbarEl.classList.toggle('scrolled', scrollY > 4);
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return pbarEl;
  }
  function paintPbar(d) {
    if (!pbarEl || !d) return;
    const { due, open } = reviewCounts(d);
    const chip = refs.chip;
    chip.hidden = !due && !open;
    chip.replaceChildren(...(due ? [dot(), `${cap99(due)}${open ? ' · ' + cap99(open) : ''}`] : [dot(), cap99(open)]));
    chip.setAttribute('aria-label', `Review: ${[due ? `${fmt(due)} due today` : null, open ? `${fmt(open)} open` : null].filter(Boolean).join(', ')}`);
    const st = refs.streak;
    st.hidden = false;
    st.classList.toggle('on', (d.streak || 0) > 0);
    st.querySelector('span').textContent = fmt(d.streak || 0);
    st.setAttribute('aria-label', `Streak: ${streakText(d)}`);
    const me = refs.meBtn, unread = unreadOf(d.inbox), c = d.challenge || {};
    me.replaceChildren(avatarOf(d, 32));
    if (unread) me.append(h('span', { class: 'badge n ink', text: cap99(unread), style: 'position: absolute; top: -2px; right: -4px; box-shadow: 0 0 0 2px var(--paper)' }));
    else if (!c.started) me.append(dot());
    me.setAttribute('aria-label', `Menu${unread ? `, ${plural(unread, 'unread item')}` : !c.started ? ', today’s challenge is new' : ''}`);
  }
  function buildTabs(tabs) {
    tabs.className = 'tabs';
    tabs.setAttribute('aria-label', 'Sections');
    const grip = h('button', { type: 'button', class: 'tabs-grip', 'aria-label': 'Open menu', 'aria-haspopup': 'dialog' });
    grip.addEventListener('click', () => menuSheet(grip));
    tabs.replaceChildren(grip, ...NAV.filter(n => n.tab).map(n => {
      const a = h('a', { href: n.href, 'aria-current': n.id === here ? 'page' : null }, icon(n.icon, 22), h('span', { text: n.label }),
        n.id === here ? h('span', { class: 'tab-mark', 'aria-hidden': 'true' }) : null);
      refs.tabs[n.id] = a;
      holdable(a, n.id);
      return a;
    }));
    tabsEl = tabs;
    whenVisible(hint);
  }
  function paintTabs(d) {
    if (!tabsEl || !d) return;
    const it = nextItems()[0], k = dayKind(d);
    const want = {
      today: (it && it.urgent) || ((k === 'practice' || k === 'test') && !dayDone(d)) ? (it && it.urgent ? `Up next: ${it.title}` : 'Today’s plan is waiting') : null,
      tests: metaOf('tests', d) && metaOf('tests', d).tip,
      results: reportNew(d) ? 'A new report' : null,
    };
    for (const [id, a] of Object.entries(refs.tabs)) {
      a.querySelectorAll('.dot, .sr').forEach(x => x.remove());
      if (want[id]) a.append(dot(), h('span', { class: 'sr', text: `, ${want[id]}` }));
    }
  }
  // hold a tab for 450 ms (8px of movement cancels) to open its shortcuts (U26)
  function holdable(a, id) {
    let timer = 0, x0 = 0, y0 = 0, fired = false;
    a.addEventListener('pointerdown', e => {
      if (e.button > 0) return;
      fired = false; x0 = e.clientX; y0 = e.clientY;
      clearTimeout(timer);
      timer = setTimeout(() => { fired = true; holdMenu(a, id); }, 450);
    });
    a.addEventListener('pointermove', e => { if (Math.hypot(e.clientX - x0, e.clientY - y0) > 8) clearTimeout(timer); });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(k => a.addEventListener(k, () => clearTimeout(timer)));
    a.addEventListener('click', e => { if (fired) { e.preventDefault(); fired = false; } });
    a.addEventListener('contextmenu', e => e.preventDefault());
  }
  function holdItems(id) {
    const d = shellData || {}, it = nextItems()[0], { due, open } = reviewCounts(d);
    const c = d.challenge || {}, r = testResume(d);
    const nx = it ? { label: 'Up next', sub: it.title, icon: 'play', onClick: () => go(refs.tabs.today, it) } : null;
    switch (id) {
      case 'today': return [nx, { label: 'Question of the day', icon: 'today', href: '/#qotd' },
        { label: 'Daily challenge', icon: 'trophy', href: '/compete/contest/?id=daily', meta: c.done ? (c.rank ? `#${c.rank}` : 'Done') : c.started ? 'Resume' : 'New' }];
      case 'practice': return [{ label: 'Quick question', icon: 'bolt', onClick: () => UI.quick('question') },
        { label: 'Log a mistake', icon: 'plus', onClick: () => UI.quick('mistake') },
        { label: 'Review', icon: 'review', href: '/review/', meta: due || open ? cap99(due || open) : undefined },
        { label: 'Saved', icon: 'bookmark', href: '/review/?tab=saved', meta: d.saved ? cap99(d.saved) : undefined },
        { label: 'Words', icon: 'words', href: '/words/', meta: d.words && d.words.due ? `${cap99(d.words.due)} due` : undefined }];
      case 'tests': return [r ? { label: `Resume ${(UI.KIND && UI.KIND[r.kind] || r.kind).toLowerCase()}`, icon: 'play', href: r.href, meta: `${r.answered}/${r.total}` } : null,
        { label: 'New module', icon: 'tests', href: '/tests/#module' }, { label: 'Full section', icon: 'tests', href: '/tests/#section' },
        { label: 'Diagnostic', icon: 'tests', href: '/diagnostic/' }];
      case 'plan': return [{ label: 'Today’s tasks', icon: 'plan', href: '/plan/#today', meta: metaOf('plan', d) ? metaOf('plan', d).text : undefined },
        { label: 'This week', icon: 'plan', href: '/plan/#week' }];
      case 'results': return [d.newest_report ? { label: 'Latest report', icon: 'results', href: `/results/report/?id=${encodeURIComponent(d.newest_report)}`, meta: reportNew(d) ? 'New' : undefined } : null,
        { label: 'Skills', icon: 'results', href: '/results/#skills' }];
    }
    return [];
  }
  function holdMenu(a, id) {
    lput('satf.hint.hold', 1);
    const h0 = doc.querySelector('.tabs-hint');
    if (h0) h0.remove();
    if (navigator.vibrate) try { navigator.vibrate(10); } catch (_) {}
    if (UI.menu) UI.menu(a, holdItems(id).filter(Boolean), { label: `${NAV.find(n => n.id === id).label} shortcuts` });
  }
  function hint() {
    if (!tabsEl || lget('satf.hint.hold', 0) || !media(W_PHONE)) return;
    // after the page has painted; a page with a docked bar above the tabs (Practice's Start, Plan's builder foot) skips
    // it this visit, since the hint would sit on that bar. Shown, it leaves after 8 s and counts as seen
    setTimeout(() => {
      if (doc.querySelector('.tabs-hint')) return;
      const y = innerHeight - 64 - 40, docked = [innerWidth * .2, innerWidth / 2, innerWidth * .8].some(x =>
        (doc.elementsFromPoint ? doc.elementsFromPoint(x, y) : []).some(e => !e.closest('.tabs, .pbar') && /^(fixed|sticky)$/.test(getComputedStyle(e).position)));
      if (docked) return;
      const x = h('button', { type: 'button', class: 'x', 'aria-label': 'Dismiss' }, icon('x', 16));
      const el = h('div', { class: 'tabs-hint', role: 'note' }, 'Hold a tab for shortcuts', x);
      const done = () => { lput('satf.hint.hold', 1); el.remove(); };
      x.addEventListener('click', done);
      doc.body.append(el);
      setTimeout(done, 8000);
    }, 1500);
  }

  /* ---- the account menu (Shell 2.6, U21, U25, U26): valid menu ARIA, from kit's UI.menu */
  let feed = null;                       // "Since you were last here": the first 3 unread (S1)
  function loadFeed(d) {
    if (!d || !d.inbox) { feed = null; return; }
    if (feed && feed.for === d.inbox) return;
    feed = { for: d.inbox, items: [] };
    api('/me/feed?unread=1&limit=3', { quiet: true }).then(r => { if (feed && r) feed.items = (r.items || r.feed || []).slice(0, 3); }, () => {});
  }
  function markSeen() {
    if (!shellData || !shellData.inbox) return;
    whenVisible(() => api('/me/feed/seen', { method: 'POST', quiet: true }).then(() => refresh(), () => {}));
  }
  const family = () => !shared && sget(LS(), 'satf.family') === '1';
  const profiles = () => { const p = lget('satf.profiles', []); return Array.isArray(p) ? p : []; };
  function keepProfile(d) {              // this device's students (U21), on a family device only
    if (!d || !d.me || shared || (!family() && !profiles().length)) return;
    const list = profiles(), me = learner(), i = list.findIndex(p => p.cred === me);
    const entry = { ...(i >= 0 ? list[i] : {}), cred: me, name: d.me.label, saved: !!d.me.linked, answers: d.answered };
    if (i >= 0) list[i] = entry; else if (family()) list.push(entry); else return;
    lput('satf.profiles', list.slice(0, 4));
  }
  function studentsItems() {
    const list = profiles().filter(p => p.cred !== learner() && (family() || p.parked));
    if (!family() && !list.length) return [];
    const out = [{ group: 'Students on this device' }];
    list.forEach(p => out.push({ label: p.name || 'Student', icon: 'users', sub: `${plural(p.answers || 0, 'answer')} · ${p.saved ? 'saved' : 'not saved'}`,
      onClick: () => { useLearner(p.cred, { session: false }); flash(`Now ${p.name || 'this student'}`); location.reload(); } }));
    if (family() && profiles().length < 4) out.push({ label: 'Add a student', icon: 'plus', onClick: () => {
      keepProfile(shellData);
      freshLearner();
      flash('A new student on this device');
      location.href = '/';
    } });
    return out;
  }
  function head(d, avatarSize = 40) {
    const me = (d && d.me) || {}, f = doc.createDocumentFragment();
    const sharedPc = d && d.device && d.device.session_only;
    f.append(avatarOf(d, avatarSize), h('b', { text: me.label || 'You' }),
      h('span', { class: 'meta', text: me.linked ? (me.email || me.email_masked || 'Saved') : 'This device only' }));
    if (sharedPc) f.append(h('span', { class: 'meta', text: 'Shared computer · ends when you close the browser' }));
    else if (d && d.goals && d.goals.length) f.append(h('span', { class: 'meta', text: `This week · ${goalsDone(d)} of ${plural(d.goals.length, 'goal')}` }));
    return f;
  }
  const isDark = () => doc.documentElement.dataset.theme === 'dark';
  function lookItem(label, iconName, checked, change) {
    return { label, icon: iconName, checked, onClick: (on, e) => {
      const b = e && e.currentTarget;
      prefs.set(change(on)).catch(() => {
        if (b) b.setAttribute('aria-checked', String(!on));
        if (UI.toast) UI.toast('Not saved. Try again.');
      });
    } };
  }
  function accountItems() {
    const d = shellData || {}, me = d.me || {}, saved = !!me.linked;
    const items = [{ head: head(d) }];
    if (d.inbox) {
      items.push({ group: `Since you were last here · ${cap99(d.inbox)}` });
      ((feed && feed.items) || []).forEach(x => items.push({ label: x.title || x.text || 'New', icon: 'bell',
        sub: x.at && UI.relTime ? UI.relTime(x.at) : undefined, href: x.href || '/me/?feed=unread#recent' }));
      items.push({ label: `See all (${fmt(d.inbox)})`, icon: 'bell', href: '/me/?feed=unread#recent' });
      markSeen();
    }
    if (!saved && !shared) items.push({ label: 'Save your progress', sub: 'So clearing this browser can’t lose it', icon: 'save', href: '/me/settings/#account' });
    items.push(...studentsItems());
    items.push({ separator: true },
      { label: 'Profile', icon: 'profile', href: '/me/', kbd: 'G U' },
      { label: d.report_replies ? ['Settings ', dot(), h('span', { class: 'sr', text: `, ${plural(d.report_replies, 'unread reply', 'unread replies')}` })] : 'Settings',
        icon: 'settings', href: '/me/settings/', kbd: 'G S' });
    if (!saved) items.push({ label: 'Sign in', icon: 'signin', href: '/signin/' });
    items.push({ label: 'Help & FAQ', icon: 'help', href: '/help/', kbd: 'G H' },
      tourItem(),
      { label: 'Send feedback', icon: 'chat', onClick: feedback },
      { group: 'Display' },
      lookItem('Dark theme', 'moon', isDark(), on => ({ theme: on ? 'dark' : 'light' })),
      lookItem('Large text', 'text', lookNow.text === 'large', on => ({ text: on ? 'large' : 'normal' })),
      { label: 'Keyboard shortcuts', icon: 'keyboard', kbd: '?', onClick: () => keysSheet() },
      { separator: true },
      saved || shared ? { label: 'Sign out', icon: 'signout', onClick: signOut } : { label: 'Leave this device…', icon: 'signout', onClick: leave });
    return items;
  }
  // kit's menu labels a group with a .menu-label; wrap each group's rows in role=group (U26)
  function groupRows(el) {
    el.querySelectorAll('.menu-label').forEach((lab, i) => {
      const id = `acct-g${i}`;
      lab.id = id;
      const g = h('div', { role: 'group', 'aria-labelledby': id });
      const rows = [];
      for (let n = lab.nextElementSibling; n && n.matches('[role^="menuitem"]'); n = n.nextElementSibling) rows.push(n);
      lab.before(g);
      g.append(lab, ...rows);
    });
  }
  function menuTrigger(btn) {
    const open = last => {
      if (!UI.menu) return;
      const res = UI.menu(btn, accountItems(), { wide: true, label: 'Account', last });
      if (res) groupRows(res.el);
    };
    btn.addEventListener('click', () => open(false));
    btn.addEventListener('keydown', e => {
      if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && btn.getAttribute('aria-expanded') !== 'true') { e.preventDefault(); open(e.key === 'ArrowUp'); }
    });
  }

  /* ---- the phone's menu sheet (Shell 2.4, U26): a scrolling body and a footer always on screen */
  function menuSheet(trigger) {
    const d = shellData, me = (d && d.me) || {}, saved = !!me.linked;
    const dlg = h('dialog', { class: 'more', 'aria-label': 'Menu' });
    const row = (label, iconName, o = {}) => {
      const el = h(o.href ? 'a' : 'button', { class: 'more-row', href: o.href || null, type: o.href ? null : 'button',
        'aria-current': o.current ? 'page' : null }, icon(iconName, 22), h('span', { text: label }), o.meta ? h('span', { class: 'more-meta' }, ...[].concat(o.meta)) : null);
      if (o.onClick) el.addEventListener('click', () => { dlg.close(); o.onClick(); });
      return el;
    };
    const swRow = (label, iconName, checked, change) => {
      const sw = UI.switch ? UI.switch(null, { checked, ariaLabel: label, onChange: on => prefs.set(change(on)).catch(e => {
        if (UI.toast) UI.toast('Not saved. Try again.');
        throw e;                           // the switch flips back
      }) }) : null;
      return h('div', { class: 'more-row' }, icon(iconName, 22), h('span', { text: label }), sw && sw.el);
    };
    const body = h('div', { class: 'more-body' });
    const nb = nextBlock(d, { kbd: false, boxes: true });
    body.append(h('div', { style: 'height: 14px', 'aria-hidden': 'true' }));
    if (!nb.hidden) body.append(nb);
    if (d && d.inbox) {
      const g = h('div', { class: 'more-group', role: 'group', 'aria-label': 'Since you were last here' },
        h('span', { class: 'k', text: `Since you were last here · ${cap99(d.inbox)}`, style: 'padding: 6px 4px 2px' }));
      ((feed && feed.items) || []).forEach(x => g.append(row(x.title || x.text || 'New', 'bell', { href: x.href || '/me/?feed=unread#recent' })));
      g.append(row(`See all (${fmt(d.inbox)})`, 'bell', { href: '/me/?feed=unread#recent' }));
      body.append(g);
      markSeen();
    }
    body.append(todayCard(d));
    const acct = h('a', { class: 'more-head', href: '/me/', 'aria-current': here === 'me' ? 'page' : null }, head(d));
    body.append(acct);
    const st = studentsItems();
    if (st.length) body.append(h('div', { class: 'more-group', role: 'group', 'aria-label': 'Students on this device' },
      st.filter(x => !x.group).map(x => row(x.label, x.icon, { onClick: x.onClick, meta: x.sub }))));
    body.append(h('div', { class: 'more-group' },
      row('Settings', 'settings', { href: '/me/settings/', current: here === 'me' && page() === 'settings', meta: d && d.report_replies ? dot() : null }),
      !saved && !shared ? row('Save your progress', 'save', { href: '/me/settings/#account', meta: dot() }) : null,
      !saved ? row('Sign in', 'signin', { href: '/signin/' }) : null,
      row('Help & FAQ', 'help', { href: '/help/', current: here === 'help' }),
      tourPage ? row('Show this page’s tour', 'help', { onClick: () => need('tour').then(() => UI.tour.start(tourPage, { force: true })).catch(() => {}) }) : null,
      row('Send feedback', 'chat', { onClick: feedback })),
      h('div', { class: 'more-group' },
        swRow('Dark theme', 'moon', isDark(), on => ({ theme: on ? 'dark' : 'light' })),
        swRow('Large text', 'text', lookNow.text === 'large', on => ({ text: on ? 'large' : 'normal' })),
        saved || shared ? row('Sign out', 'signout', { onClick: signOut }) : row('Leave this device…', 'signout', { onClick: leave })));
    // the footer: Review, Words, Compete and Quick, two taps from any page
    const cell = (label, iconName, o = {}) => {
      const el = h(o.href ? 'a' : 'button', { href: o.href || null, type: o.href ? null : 'button', 'aria-current': o.current ? 'page' : null,
        'aria-label': o.aria || null }, icon(iconName, 22), h('span', { text: label }), o.meta ? h('span', { class: 'more-meta' }, ...[].concat(o.meta)) : null);
      if (o.onClick) el.addEventListener('click', () => { dlg.close(); o.onClick(); });
      return el;
    };
    const rc = d ? reviewCounts(d) : { due: 0, open: 0 };
    const cm = d ? metaOf('compete', d) : null, wm = d ? metaOf('words', d) : null;
    const foot = h('div', { class: 'more-foot' },
      cell('Review', 'review', { href: '/review/', current: here === 'review',
        meta: rc.due ? `${cap99(rc.due)} due · ${cap99(rc.open)} open` : rc.open ? [dot(), `${cap99(rc.open)} open`] : null,
        aria: `Review${rc.due ? `, ${fmt(rc.due)} due today` : ''}${rc.open ? `, ${fmt(rc.open)} open` : ''}` }),
      cell('Words', 'words', { href: '/words/', current: here === 'words', meta: wm ? wm.text : null }),
      cell('Compete', 'compete', { href: '/compete/', current: here === 'compete', meta: cm ? cm.text : null }),
      cell('Quick', 'bolt', { onClick: () => UI.quick() }));
    dlg.append(body, foot);
    dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
    // it drops away (motion.css, a transition on display and overlay), then goes; a key closes it at once
    dlg.addEventListener('close', () => {
      let t = 0;
      try { if (UI.motion && UI.motion.ok() && CSS.supports('overlay', 'auto')) t = 440; } catch (_) {}
      dlg.inert = true;
      if (t) setTimeout(() => dlg.remove(), t); else dlg.remove();
      if (trigger && trigger.isConnected) trigger.focus({ preventScroll: true });
    });
    doc.body.append(dlg);
    dlg.showModal();
    body.scrollTop = 0;
    return dlg;
  }

  /* ---- a scroll box shows a soft edge where there is more to scroll (ui.css .fade-s / .fade-e; x: across) */
  function edgeFade(el, x) {
    if (!el) return null;
    if (el._fade) { el._fade(); return el._fade; }
    if (x) el.classList.add('fade-x');
    const paint = () => {
      const pos = x ? el.scrollLeft : el.scrollTop;
      const max = x ? el.scrollWidth - el.clientWidth : el.scrollHeight - el.clientHeight;
      el.classList.toggle('fade-s', pos > 2);
      el.classList.toggle('fade-e', max - pos > 2);
    };
    el._fade = paint;
    el.addEventListener('scroll', paint, { passive: true });
    try { new ResizeObserver(paint).observe(el); } catch (_) {}
    paint();
    return paint;
  }

  /* ---- the Now strip (U26): Up next as one line at the top of main, as text, wherever the
     sidebar is not showing it in full (ui.css decides by media query) */
  const strips = [];                     // the shell's, or the one Today places itself
  function nowStrip(host) {
    const el = h('section', { class: 'now-strip', 'aria-label': 'Up next' });
    el._paint = d => {
      const nb = here1(nextItems(d)[0]) ? h('div', { hidden: true }) : nextBlock(d, { quiet: ownPrimary });
      // one line: the reason moves to the title's tooltip; the Today card stays in the sidebar, the hero and the phone's menu sheet
      const r = nb.querySelector('.nextup-r');
      if (r) nb.querySelector('.nextup-t').title = r.textContent;
      el.replaceChildren(...(nb.hidden ? [] : [nb]));
      el.hidden = !el.children.length;
    };
    el._paint(shellData);
    if (host) host.prepend(el);
    strips.push(el);
    return el;
  }
  const paintStrip = () => strips.forEach(el => el._paint(shellData));     // every shell paint and layout change
  // an Up next that is a link to the page already open: the page shows it, the strip and the bar don't repeat it
  const here1 = it => { try { return !!(it && it.href && new URL(it.href, location.href).pathname === location.pathname); } catch (_) { return false; } };
  let ownStart = false;                  // UI.shell({ now: false }): the page carries its own Start
  let ownPrimary = false;                // UI.shell({ ownPrimary: true }): the page's hero has the orange Start; Up next's goes .btn

  /* ---- the section bar (U26): UI.sections([{id, label}]) renders a page's cards as chips,
     sticky at the top of main, with scroll-spy; "Up next: ... · Start" shows at its end once
     the Now strip has scrolled away, on pages with sections or without */
  // The bar is the only thing the shell puts in main's flow (with the Now strip and a banner, which are content): no
  // sentinel, it watches itself, and while it waits it takes back main's gap too, so a page laying main out with a
  // gap gets no dead air above its header
  let barEl = null, stuckIO = null, spyIO = null, sectionsAlways = false;
  function sectionBar() {
    if (barEl) return barEl;
    barEl = h('nav', { class: 'sections', 'aria-label': 'On this page' });
    // a chip that takes focus while the bar waits brings it out at once (keyboard users never tab into nothing)
    barEl.addEventListener('focusin', () => paintBarNext());
    barEl.addEventListener('focusout', e => { if (!barEl.contains(e.relatedTarget)) setTimeout(paintBarNext); });
    return barEl;
  }
  function paintBarNext() {
    if (!barEl) return;
    const old = barEl.querySelector('.sections-next');
    if (old) old.remove();
    // a page with its own Start (now: false: Today, Plan, Tests) or one Up next points at: the bar doesn't say it again
    const it = shellData && !ownStart && !here1(nextItems()[0]) && nextItems()[0];
    if (it) barEl.append(h('span', { class: 'sections-next' }, 'Up next: ', h('b', { text: it.title }), startBtn(it, 'Start', null, ownPrimary ? 'btn sm' : undefined)));
    const chips = barEl.querySelectorAll(':scope > a').length, stuck = barEl.classList.contains('stuck');
    barEl.hidden = !chips && !it;
    // the chips wait until the page's header has scrolled away (SUGGESTIONS Recommended 6), then fade in as the bar
    // sticks; UI.shell({ sectionsAlways: true }) shows them from the top. Waiting, the bar takes no room and is
    // clear but keeps its landmark, and a chip that gets focus (Tab) brings it out where it is.
    // Without chips it is one Start's height, pulled up by it, and hidden until it sticks.
    const open = !!chips && (sectionsAlways || barEl.contains(doc.activeElement));
    barEl.toggleAttribute('data-m-wait', !!chips && !stuck && !open);
    barEl.style.minHeight = chips ? '' : '40px';
    barEl.style.visibility = chips || stuck ? '' : 'hidden';
    if (open || barEl.hidden) barEl.style.marginBottom = '';
    else if (!stuck) {
      const gap = barEl.parentElement ? parseFloat(getComputedStyle(barEl.parentElement).rowGap) || 0 : 0;   // a flex / grid main's gap
      barEl.style.marginBottom = `-${barEl.offsetHeight + gap}px`;
    }
  }
  function observeStuck() {
    if (!barEl || typeof IntersectionObserver !== 'function') return;
    if (stuckIO) stuckIO.disconnect();
    // where it sticks, as the CSS says (the phone's 56px bar plus the notch's safe area under viewport-fit=cover)
    const top = parseFloat(getComputedStyle(barEl).top) || 0;
    // the bar is its own sentinel: stuck at `top`, its first pixel sits above the line 1px under it, so it is no longer whole
    stuckIO = new IntersectionObserver(([e]) => {
      barEl.classList.toggle('stuck', e.boundingClientRect.height > 0 && e.intersectionRatio < 1 && e.boundingClientRect.top < top + 1);   // a display: none bar is not stuck
      barEl.classList.toggle('scrolled', barEl.classList.contains('stuck'));      // A1's scroll shadow
      paintBarNext();
    }, { rootMargin: `-${top + 1}px 200px 0px 200px`, threshold: [1] });   // side slack: a bar overhanging the page by a
    stuckIO.observe(barEl);                                                 // pixel must still read whole while it is not stuck
  }
  function sections(list) {
    sectionBar();
    barEl.querySelectorAll(':scope > a').forEach(a => a.remove());
    if (spyIO) spyIO.disconnect();
    const chips = (list || []).map(s => {
      const a = h('a', { href: `#${s.id}`, text: s.label, 'data-for': s.id });
      a.addEventListener('click', e => {
        const card = doc.getElementById(s.id);
        if (!card) return;
        e.preventDefault();
        card.dispatchEvent(new CustomEvent('satf:open', { bubbles: true }));     // a collapsed card opens (S1)
        card.scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'start' });
        const h2 = card.querySelector('h2') || card;
        if (!h2.hasAttribute('tabindex')) h2.tabIndex = -1;
        h2.focus({ preventScroll: true });
        try { history.replaceState(history.state, '', `#${s.id}`); } catch (_) {}
        current(a);
      });
      return a;
    });
    barEl.prepend(...chips);
    edgeFade(barEl, true);               // the phone scrolls the chips sideways: soft edges where more are
    const current = a => {
      chips.forEach(c => c.toggleAttribute('aria-current', false));
      if (!a) return;
      a.setAttribute('aria-current', 'true');
      if (barEl.scrollWidth > barEl.clientWidth) barEl.scrollTo({ left: Math.max(0, a.offsetLeft - 16), behavior: reduced() ? 'auto' : 'smooth' });
    };
    if (chips.length && typeof IntersectionObserver === 'function') {
      spyIO = new IntersectionObserver(es => es.forEach(e => {
        if (e.isIntersecting) current(chips.find(c => c.dataset.for === e.target.id));
      }), { rootMargin: '-64px 0px -66% 0px' });
      (list || []).forEach(s => { const el = doc.getElementById(s.id); if (el) spyIO.observe(el); });
    }
    paintBarNext();
    return barEl;
  }

  /* ---- signing out (Shell 1, U21) */
  const KEEP = new Set(['satf.look', 'satf.rail', 'satf.family', 'satf.profiles', 'satf.undo', 'satf.flash', 'satf.hint.hold']);
  function forget(cred) {                // this learner off this browser; the device's own keys stay
    for (const s of [LS(), SS()]) {
      try {
        if (!s) continue;
        for (let i = s.length - 1; i >= 0; i--) { const k = s.key(i); if (k && k.startsWith('satf.') && !KEEP.has(k)) s.removeItem(k); }
      } catch (_) {}
    }
    const list = profiles().filter(p => p.cred !== cred);
    lput('satf.profiles', list.length ? list : null);
    memo = null; shellData = null;
  }
  function revoke(cred) {
    if (!/^d:/.test(cred || '')) return;
    try { fetch('/api/devices/this', { method: 'DELETE', keepalive: true, headers: { ...headers(), 'X-Learner': cred } }).catch(() => {}); } catch (_) {}
  }
  function flash(text, o = {}) { sput(SS(), 'satf.flash', JSON.stringify({ text, ...o })); }
  function signOut() {
    const cred = learner();
    if (shared) {                        // a shared computer: at once, no Undo
      revoke(cred);
      try { const s = SS(); if (s) for (let i = s.length - 1; i >= 0; i--) { const k = s.key(i); if (k && k.startsWith('satf.')) s.removeItem(k); } } catch (_) {}
      shared = false; memo = null;
      flash('Signed out');
      location.href = '/';
      return;
    }
    const entry = profiles().find(p => p.cred === cred) || null;
    sput(SS(), 'satf.undo', JSON.stringify({ cred, entry, until: Date.now() + 8000 }));
    forget(cred);
    flash('Signed out', { undo: true });
    location.href = '/';
  }
  // on the page after Sign out: 8 s of Undo; the revoke goes when that ends or on pagehide
  function pendingSignOut() {
    let u = null;
    try { u = JSON.parse(sget(SS(), 'satf.undo') || 'null'); } catch (_) {}
    if (!u || !u.cred) return null;
    const send = () => { if (!sget(SS(), 'satf.undo')) return; sput(SS(), 'satf.undo', null); revoke(u.cred); };
    const left = u.until - Date.now();
    if (left <= 0) { send(); return null; }
    const timer = setTimeout(send, left);
    addEventListener('pagehide', send);
    return { left, undo: () => {
      clearTimeout(timer);
      removeEventListener('pagehide', send);
      sput(SS(), 'satf.undo', null);
      useLearner(u.cred, { session: false });
      if (u.entry) lput('satf.profiles', [...profiles().filter(p => p.cred !== u.cred), u.entry]);
      location.reload();
    } };
  }
  function leave() {                     // an unsaved device: say what is lost first (Shell 4.4)
    if (!UI.sheet) return;
    const code = learner();
    const masked = code.slice(0, 2) + '•'.repeat(Math.max(0, code.length - 6)) + code.slice(-4);
    UI.sheet({ title: 'Leave this device?', size: 's',
      body: b => {
        b.append(h('p', { text: 'This device’s progress isn’t saved to an email. If you sign out, this browser forgets it.' }),
          h('p', { class: 'help', text: 'Keep this code to bring it back by hand:' }),
          h('p', { style: 'display: flex; align-items: center; gap: 10px; flex-wrap: wrap' }, h('code', { class: 'mono', text: masked }),
            h('button', { type: 'button', class: 'btn sm', text: 'Copy', onclick: () => UI.copyText ? UI.copyText(code, { toast: 'Copied' }) : null })));
      },
      actions: [{ label: 'Cancel', quiet: true },
        { label: 'Sign out anyway', ink: true, onClick: () => { forget(code); freshLearner(); flash('Signed out'); location.href = '/'; return false; } },
        { label: 'Save to email first', primary: true, href: '/me/settings/#account' }] });
  }

  /* ---- feedback, the palette and the quick sheet load on first use (F6's report.js, and
     quick.js / palette.js) */
  const loading = {};
  function need(file) {
    return loading[file] || (loading[file] = new Promise((resolve, reject) => {
      const sc = doc.createElement('script');
      sc.src = `/assets/${file}.js`;
      sc.onload = resolve;
      sc.onerror = () => { delete loading[file]; reject(new Error(`${file}.js`)); };
      doc.head.append(sc);
    }));
  }
  function lazy(name, file) {
    if (typeof UI[name] === 'function') return;
    const stub = (...a) => need(file).then(() => {
      if (UI[name] === stub) throw new Error(`${file}.js has no UI.${name}`);
      return UI[name](...a);
    }).catch(e => { console.warn(e); if (UI.toast) UI.toast('Couldn’t open that. Try again.'); });
    UI[name] = stub;
  }
  lazy('quick', 'quick'); lazy('palette', 'palette'); lazy('report', 'report'); lazy('continueOnPhone', 'qr');
  const feedback = () => UI.report({ kind: 'page', source: location.pathname + location.search });

  /* ---- the first-visit page tour (tour.js loads on first use) */
  const TOUR_PAGES = new Set(['today', 'practice', 'tests', 'plan', 'review', 'words', 'results', 'compete', 'me']);
  let tourPage = null;
  const tourSeen = p => { try { return !!localStorage.getItem(`satf.tour.${p}`); } catch (_) { return true; } };
  const tourItem = () => (tourPage ? { label: 'Show this page’s tour', icon: 'help', onClick: () => need('tour').then(() => UI.tour.start(tourPage, { force: true })).catch(() => {}) } : null);
  /* ---- the focus chrome (chrome: 'focus'; Sign in, Welcome, Pair): a slim brand bar instead of the sidebar,
     rail, tabs and Now strip. The mark and wordmark go home; Help and the account menu sit at the right; the
     body gets .has-focus so the page centres its card. The shortcuts stay (G H, Mod+K, ?). */
  function buildFocus() {
    const help = h('a', { class: 'ibtn', href: '/help/', 'aria-label': 'Help & FAQ' }, icon('help'));
    tip(help, 'Help & FAQ', 'G H');
    const user = h('button', { type: 'button', class: 'side-user focus-user', 'aria-haspopup': 'menu', 'aria-expanded': 'false' },
      h('span', { class: 'avatar' }), h('span', { class: 'side-name', text: '' }), h('span', { class: 'side-sub', text: '' }), icon('chev', 16));
    menuTrigger(user);
    refs.user = user;
    return h('div', { class: 'focus-bar' },
      h('a', { class: 'focus-brand', href: '/', 'aria-label': 'SAT Freshman, Today', html: mark(26) }, h('span', { class: 'focus-word', text: 'SAT Freshman' })),
      h('span', { class: 'focus-grow' }), help, user);
  }
  /* ---- UI.shell */
  let shellOn = false;
  function shell(o = {}, more) {
    if (typeof o === 'string') o = { ...more, page: o };       // UI.shell('words', { now: false }) keeps its options
    if (o.sectionsAlways !== undefined) sectionsAlways = !!o.sectionsAlways;
    if (o.ownPrimary !== undefined) ownPrimary = !!o.ownPrimary;
    if (shellOn) { if (o.sections) sections(o.sections); return; }
    shellOn = true;
    const pg = o.page || page();
    const focus = o.chrome === 'focus';
    here = SECTION[pg] || pg;
    if (!focus && TOUR_PAGES.has(pg) && !(typeof RO !== 'undefined' && RO)) { tourPage = pg; if (!tourSeen(pg) && !new URLSearchParams(location.search).has('print')) { UI.__tourPage = pg; need('tour').catch(() => {}); } }
    keys.chrome = true;
    doc.body.classList.toggle('has-focus', focus);
    const bar = $('#bar');
    if (bar) {
      bar.className = '';
      bar.replaceChildren(...(focus ? [buildFocus()] : [buildSide(), buildPbar()]));
      if (focus && UI.scrolled) UI.scrolled(bar);
    }
    const tabs = $('#tabs');
    if (tabs) { if (focus) tabs.hidden = true; else buildTabs(tabs); }
    const main = focus ? null : doc.querySelector('main');
    if (main) {
      if (!main.id) main.id = 'main';
      sectionBar();
      main.prepend(barEl);
      ownStart = o.now === false;
      // nowBlock: false (Today, Plan): the sidebar's Up next and Today card leave too, the page carries both
      doc.body.classList.toggle('no-now', o.nowBlock === false);
      if (o.now !== false && !doc.querySelector('.now-strip')) barEl.before(nowStrip(null));
      if (o.sections) sections(o.sections); else paintBarNext();
    }
    if (!storable && UI.banner) UI.banner('storage', 'This browser is blocking site data, so progress can’t be kept here.',
      [{ label: 'How to fix', href: '/help/#storage' }], { sys: true });
    for (const q of [W_SIDE, W_PHONE]) { try { matchMedia(q).addEventListener('change', layout); } catch (_) {} }
    layout();
    onShell(paintAll);
    if (!focus) onShell(notices);
    // the first hover on the sidebar in a session fetches the palette's type index (U23)
    if (sideEl) sideEl.addEventListener('pointerenter', () => { types().catch(() => {}); }, { once: true });
    // no shell data at all: Up next and the Today card leave, the nav still works (Shell 2.12)
    // (and a retired code: nothing of that student stays painted)
    const gone = () => {
      if (shellData) return;
      paintSide(null);
      if (sideEl) sideEl.querySelectorAll('.nextup, .side-day').forEach(e => { e.hidden = true; });
      strips.forEach(el => { el.hidden = true; });
      if (refs.chip) refs.chip.hidden = true;
      if (refs.streak) refs.streak.hidden = true;
      Object.values(refs.tabs).forEach(a => a.querySelectorAll('.dot, .sr').forEach(x => x.remove()));
    };
    (shellAsked || refresh()).then(gone, gone);
    (shellAsked || refresh()).then(d => whenVisible(() => autoSheets(d)), () => {});    // data asked before the shell
    addEventListener('satf:retired', gone);
    if (doc.prerendering) whenVisible(() => { if (shellData) paintAll(shellData); });
    const qs = new URLSearchParams(location.search);
    if (qs.has('feedback')) whenVisible(feedback);
    // ?next=1 starts Up next item 1 once (U1, U18); ?run=1 starts the day's run (G1)
    for (const [k, fn] of [['next', startNext], ['run', runStart]]) {
      if (qs.get(k) !== '1') continue;
      qs.delete(k);
      if (qs.get('from') === 'push') qs.delete('from');       // a notification's tap (/sw.js)
      try { history.replaceState(history.state, '', location.pathname + (qs.toString() ? '?' + qs : '') + location.hash); } catch (_) {}
      whenVisible(fn);
    }
  }
  shell.toggle = toggle;
  function paintAll(d) {
    // Results or a report shown: its newest sitting has been seen (satf.seen.report)
    if (here === 'results' && d.newest_report && !doc.prerendering) sput(LS(), 'satf.seen.report', d.newest_report);
    keepProfile(d);
    loadFeed(d);
    paintSide(d);
    paintPbar(d);
    paintTabs(d);
    paintStrip();
    paintBarNext();
  }

  /* ---- banners (Shell 2.11, U15, U17, U19) and event toasts (U25)
     retired, offline and storage are the system's (above); of the student's notices one
     shows at a time, in the spec's order, and kit puts the system's first. */
  const NOTICES = ['deadline', 'stage', 'first', 'nudge'];
  const WEEK_MS = 7 * 864e5;
  const COLLEGE_BOARD = 'https://satsuite.collegeboard.org/sat/registration';
  const daysTo = (from, to) => Math.round((new Date(to + 'T12:00:00') - new Date(from + 'T12:00:00')) / 864e5);
  const STAGE_LINE = {
    build: 'Build starts today: sets run at SAT pace, with the key after each question.',
    test: 'Test-like starts today: sets run at SAT pace with the key at the end.',
    final: 'Final week starts today: sets run at SAT pace with the key at the end.',
  };
  function noticeOf(d) {
    const me = d.me || {}, saved = !!(me.linked || me.saved), today = (d.today && d.today.day) || localDay();
    const r = d.registration;
    if (r && r.day && r.register_by) {
      const left = n => n <= 0 ? 'last day' : `${plural(n, 'day')} left`;
      const text = r.late && r.late_by
        ? `Late registration for ${day(r.day)} closes ${day(r.late_by)} · ${left(daysTo(today, r.late_by))}`
        : `Register for ${day(r.day)} by ${day(r.register_by)} · ${left(r.days_left ?? daysTo(today, r.register_by))}`;
      return { kind: 'deadline', text, o: { icon: 'clock' }, actions: [
        { label: 'I’ve registered', primary: true, onClick: e => {
          const b = e.currentTarget;
          b.setAttribute('aria-busy', 'true');
          prefs.set({ registered: r.day }).then(() => { UI.banner.clear('deadline'); if (shellData) shellData.registration = null; },
            () => { b.removeAttribute('aria-busy'); if (UI.toast) UI.toast('Not saved. Try again.'); });
        } },
        { label: ['Register at College Board', icon('external', 14)], onClick: () => { window.open(COLLEGE_BOARD, '_blank', 'noopener'); } },
        UI.ics ? { label: 'Add deadline to calendar', icon: 'calendar', onClick: () => UI.ics({
          title: `Register for the SAT on ${day(r.day)}`, start: r.late ? r.late_by : r.register_by, allDay: true,
          alarm: 9 * 60, url: COLLEGE_BOARD, description: `Registration for the ${day(r.day)} SAT closes this day.` }) } : null,
      ].filter(Boolean) };
    }
    const st = d.stage, p = d.prefs || {};
    const stageKey = st && `${st.name}:${st.since}`;
    if (st && st.since === today && STAGE_LINE[st.name] && p.stage_auto !== false && lget('satf.stage.seen') !== stageKey) {
      const seen = () => lput('satf.stage.seen', stageKey);
      return { kind: 'stage', text: STAGE_LINE[st.name], o: { dismiss: true, onDismiss: seen }, actions: [
        { label: 'Why?', href: '/help/#stages', onClick: seen },
        { label: 'Keep my settings', onClick: () => { seen(); UI.banner.clear('stage');
          prefs.set({ stage_auto: false }).then(() => { if (UI.toast) UI.toast('Kept. Your exam date no longer changes your settings.'); },
            () => { if (UI.toast) UI.toast('Not saved. Try again.'); }); } },
      ] };
    }
    if (shared || saved) return null;
    // not on the sign-in page itself, where it only repeats the page
    if (!d.answered && !lget('satf.first') && !location.pathname.startsWith('/signin')) {
      // a question for the few with progress elsewhere, so a plain button: the page's own start (Today's Study) stays its one orange
      return { kind: 'first', text: 'Have progress on another device?', actions: [
        { label: 'Sign in', href: '/signin/' },
        { label: 'Dismiss', quiet: true, dismiss: true, onClick: () => lput('satf.first', 1) },
      ] };
    }
    if (d.answered >= 50 && Date.now() - (Number(lget('satf.nudge', 0)) || 0) > WEEK_MS) {
      // one short line (under the fold's 70 characters, so no toggle), beside its icon even on a phone
      return { kind: 'nudge', text: 'Your progress is only in this browser.',
        o: { icon: 'save' }, actions: [
          { label: 'Save to email', href: '/me/settings/#account' },   // a .btn: the page's own Start stays its one orange
          { label: 'Not now', quiet: true, dismiss: true, onClick: () => lput('satf.nudge', Date.now()) },
        ] };
    }
    return null;
  }
  function notices(d, fromCache) {
    if (!d || !UI.banner) return;
    const n = noticeOf(d);
    NOTICES.forEach(k => { if (!n || n.kind !== k) UI.banner.clear(k); });
    if (n) UI.banner(n.kind, n.text, n.actions, n.o || {});
    if (!fromCache) whenVisible(() => eventToasts(d));
  }
  // achievements and report replies: at most 2 toasts a page load, each shown once a tab;
  // what they announce is marked seen (it stays in the inbox, S1's feed)
  let eventsShown = 0;
  const ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI'];
  function eventToasts(d) {
    if (!UI.toast) return;
    let seen = [];
    try { seen = JSON.parse(sget(SS(), 'satf.toasted') || '[]') || []; } catch (_) {}
    const mark = k => { seen.push(k); sput(SS(), 'satf.toasted', JSON.stringify(seen.slice(-60))); };
    const show = (text, o) => { if (eventsShown >= 2) return; eventsShown += 1; UI.toast(text, { ms: 6000, wait: true, ...o }); };
    const ach = ((d.new && d.new.achievements) || []).filter(a => a && !seen.includes(`a:${a.id}:${a.tier || ''}`));
    ach.forEach(a => {
      mark(`a:${a.id}:${a.tier || ''}`);
      const name = a.text || `${a.label || a.name || a.title || a.id}${a.tier > 1 && ROMAN[a.tier] ? ' · ' + ROMAN[a.tier] : ''}`;
      show(`Achievement · ${name}`, { icon: a.glyph && TOPIC[a.glyph] ? glyph(a.glyph) : 'trophy', action: { label: 'See', href: '/me/#achievements' } });
    });
    if (ach.length && has('achievements_seen')) api('/me/achievements/seen', { method: 'POST', quiet: true, body: { ids: ach.map(a => a.id) } }).catch(() => {});
    const n = d.report_replies || 0, rep = d.report;
    const key = `r:${n}:${rep ? rep.id : ''}`;
    if (n > 0 && !seen.includes(key)) {
      mark(key);
      show(n === 1 && rep && rep.unread ? `Report #${rep.id} answered` : `${plural(n, 'report')} answered`,
        { icon: 'chat', action: { label: 'Read', href: '/me/settings/#reports' } });
      if (has('reports_seen')) api('/reports/seen', { method: 'POST', quiet: true }).catch(() => {});
    }
  }

  // a toast carried over a page change: "Signed out · Undo", "Now Maya"
  function flashed() {
    let f = null;
    try { f = JSON.parse(sget(SS(), 'satf.flash') || 'null'); } catch (_) {}
    sput(SS(), 'satf.flash', null);
    const pend = pendingSignOut();
    if (!f || !UI.toast) return;
    if (f.undo && pend) UI.toast(f.text, { undo: pend.undo, ms: pend.left });
    else UI.toast(f.text);
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', flashed); else setTimeout(flashed);

  /* ------------------------------------------------------------ a question
     Renders one question into host. Stems and options are plain Unicode from
     the bank, set as text; figures are the bank's own SVG. The page decides
     what an answer does; reveal() paints what the server said about it. */
  function question(host, q, { onAnswer, again = false } = {}) {
    host.replaceChildren();
    const skill = h('p', { class: 'q-skill' }, glyph(q.topic), h('span', { text: TOPIC[q.topic] || RW_SKILL[q.topic] ? topicName(q.topic) : (q.topic_name || '') }));
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
    if (q.text) host.append(h('div', { class: 'q-passage', text: q.text }));     // an R&W item's passage, above its stem
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

  /* ------------------------------------------------------------ fold: extra detail behind a small toggle
     Long helper text, intro lines, notes and banner text are wrapped in a closed <details> whose one-line label is the
     start of the text (question.js folds the Explanation card itself, as 'explanation' in the same memory). The element itself is moved, not rebuilt, so the pages' references and
     listeners stay valid. Open boxes are remembered per page and text (satf.fold). Opt out with data-nofold. */
  const FOLD_SEL = '.help, .lead, .lead-t, .wz-note, .rp-helper, .rs-helper, .chart-note, .calc-note, .tw-lead, .tw-note, .v-note, .banner-t';
  // a sheet folds only when it asks to (dialog[data-fold]); aria-live="off" is not live; popovers never fold
  const FOLD_SKIP = 'dialog:not([data-fold]), [inert], [hidden], [data-nofold], details, .pref, [role=alert], [aria-live]:not([aria-live="off"]), .field-err, .sr, #bar, #tabs, nav, .skel, .tour, .popover, .tip';
  const FOLD_MIN = 70;
  const FOLD_OFF = /\/(print|help)\b|\/words\/run\b/;
  const foldOff = () => FOLD_OFF.test(location.pathname) || /[?&]print\b/.test(location.search);
  const foldMem = (() => {
    const read = () => { try { return JSON.parse(localStorage.getItem('satf.fold') || '[]'); } catch (_) { return []; } };
    return {
      has: id => read().includes(id),
      set(id, on) {
        let a = read().filter(x => x !== id);
        if (on) a.push(id);
        try { localStorage.setItem('satf.fold', JSON.stringify(a.slice(-300))); } catch (_) {}
      },
    };
  })();
  function foldOne(el) {
    const text = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!text || text.length < FOLD_MIN) return;
    if (el.querySelector('button, input, select, textarea, .pill, .btn')) return;      // never hide a control
    if (el.closest('.ws, .x-card')) return;     // the question workspace; question.js folds its own Explanation
    const first = text.match(/^.{16,64}?(?=[.:;!?]\s|$)/);
    const label = first && first[0].length < text.length - 1 ? first[0] : text.slice(0, 56).replace(/\s\S*$/, '') + '…';
    const id = `${location.pathname}|${text.slice(0, 48).replace(/\d+/g, '#')}`;
    const cs = getComputedStyle(el);
    const d = h('details', { class: 'fold' }, h('summary', { class: 'fold-s', text: label }));
    if (foldMem.has(id)) d.open = true;       // open before it lands, so a remembered box never animates on load
    el.replaceWith(d);
    d.append(el);
    d.style.margin = `${cs.marginTop} ${cs.marginRight} ${cs.marginBottom} ${cs.marginLeft}`;
    for (const p of ['gridColumn', 'gridRow', 'flex', 'alignSelf', 'justifySelf', 'order', 'minWidth']) {
      const v = cs[p];
      if (v && !['auto', 'normal', '0', '0px', '0 1 auto', ''].includes(v)) d.style[p] = v;
    }
    el.style.margin = '6px 0 0';
    d.addEventListener('toggle', () => foldMem.set(id, d.open));
  }
  /* folds move (SUGGESTIONS "Folds open smoothly"): details.fold opens and closes in height and fade; where
     CSS can animate to auto (interpolate-size, motion.css) that is all CSS, elsewhere this does the height.
     A .card[data-collapsed] that opens grows to its height and its content rises 4px; a close is instant. */
  let foldCss = false;
  try { foldCss = CSS.supports('interpolate-size', 'allow-keywords'); } catch (_) {}
  if (!foldCss) doc.addEventListener('click', e => {
    const sm = e.target.closest && e.target.closest('details.fold > summary');
    const d = sm && sm.parentElement;
    if (!d || d._mFold || !UI.motion || !UI.motion.ok(e)) return;
    e.preventDefault();
    d._mFold = true;
    const shut = sm.getBoundingClientRect().bottom - d.getBoundingClientRect().top;
    if (!d.open) { d.open = true; UI.motion.grow(d, shut).then(() => { d._mFold = false; }); return; }
    UI.motion.grow(d, d.offsetHeight, { to: shut, then: () => { d.open = false; } }).then(() => { d._mFold = false; });
  });
  if (typeof MutationObserver === 'function') {
    const cardMo = new MutationObserver(rs => rs.forEach(r => {
      const c = r.target;
      if (r.oldValue === null || c.hasAttribute('data-collapsed') || !UI.motion || !UI.motion.ok()) return;
      const to = c.offsetHeight;
      c.setAttribute('data-collapsed', '');
      const from = c.offsetHeight;
      c.removeAttribute('data-collapsed');
      cardMo.takeRecords();
      UI.motion.grow(c, from, { to });
      [...c.children].filter(k => !k.matches('.card-head, .card-sum')).forEach(k => UI.motion.enter(k, 'nudge'));
    }));
    const watch = () => cardMo.observe(doc.body, { subtree: true, attributes: true, attributeFilter: ['data-collapsed'], attributeOldValue: true });
    if (doc.body) watch(); else doc.addEventListener('DOMContentLoaded', watch);
  }
  function foldScan() {
    if (foldOff()) return;
    doc.querySelectorAll(FOLD_SEL).forEach(el => { if (!el.closest(FOLD_SKIP) && !el.parentElement.closest('.fold') && !el.matches(FOLD_SKIP)) foldOne(el); });
  }
  (() => {
    let t = 0;
    const later = () => { clearTimeout(t); t = setTimeout(foldScan, 180); };
    const ticking = r => { const n = r.target.nodeType === 1 ? r.target : r.target.parentElement; return !!(n && n.closest('.timer, .rn-watch, .t-digits, .rn-between-clock, .rn-segs')); };
    const start = () => { foldScan(); new MutationObserver(rs => { if (!rs.every(ticking)) later(); }).observe(doc.body, { childList: true, subtree: true, characterData: true }); };
    if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start); else start();
    let was = [];
    window.addEventListener('beforeprint', () => { was = [...doc.querySelectorAll('details.fold')].filter(d => !d.open); was.forEach(d => { d.open = true; }); });
    window.addEventListener('afterprint', () => { was.forEach(d => { d.open = false; }); was = []; });
  })();

  /* ------------------------------------------------------------ export */
  Object.assign(UI, {
    learner, useLearner, freshLearner, shared: () => shared, stored: () => storable, ready,
    api, cached, whenVisible, refresh, onShell, shellData: () => shellData, me, prefs, prefRow, look,
    keys, ROUTES, start, nextItems, nextMeta, edgeFade, skip, need, has, types, parseSet, ALIASES, boxChips, feedback, run, autoSheet, share, notify,
    NAV, SECTION, shell, nowStrip, sections, menuSheet, accountMenu: accountItems,
    signOut: () => (shellData && shellData.me && shellData.me.linked) || shared ? signOut() : leave(),
    h, s, svg, mark, ICON, ICON_FILL, icon, spotArt: spot, TOPICS, TOPIC, RW_SKILL, RW_DOMAINS, DOMAINS, glyph, chip,
    SUBJECTS, subject, subjectSeg, subjectLabel, subjectOf, topicName,
    question, calc, ref, snap, mmss, minutesFor, day, cap, band, reduced, plan, $,
  });
})();
