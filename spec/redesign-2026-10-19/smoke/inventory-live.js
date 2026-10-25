// inventory.js against the LIVE app on 8071 (real /api answers for learner LRN, default a:v2revresults01) instead of fixtures:
// used where the fixture run crashes (/compete/, /compete/rankings/). usage: LRN=<id> node inventory-live.js <web root> <page path> [width]
const path = require('path'), fs = require('fs');
process.on('unhandledRejection', () => {}); process.on('uncaughtException', () => {});   // a stub gap must not stop the dump
const { JSDOM, VirtualConsole } = require('/Users/workingmyassof/freshbot/calc/node_modules/jsdom');
const WEB = process.argv[2], PAGE = process.argv[3], W = parseInt(process.argv[4] || '1440', 10);
// FIX=practice adds /bank, /drill/preview, /sets and /next (Practice); the default stays the Today set
const LRN = process.env.LRN || 'a:v2revresults01';

const file = path.join(WEB, PAGE.endsWith('.html') ? PAGE : path.join(PAGE === '.' ? '' : PAGE, 'index.html'));
let html = fs.readFileSync(file, 'utf8');
// inline every local script so they run in order (module scripts run as classic ones: none use import)
html = html.replace(/<script([^>]*)\ssrc="(\/[^"]+\.js)"([^>]*)><\/script>/g, (m, a, src) => {
  const p = path.join(WEB, src);
  return fs.existsSync(p) ? `<script>${fs.readFileSync(p, 'utf8').replace(/<\/script>/g, '<\\/script>')}</script>` : '';
});
html = html.replace(/<link[^>]*>/g, '');
const errors = [];
const vc = new VirtualConsole();
vc.on('error', (...a) => errors.push('console.error: ' + a.map(x => (x && x.stack) || String(x)).join(' ')));
vc.on('jsdomError', e => errors.push('jsdomError: ' + ((e && (e.detail && e.detail.stack)) || e.stack || e.message)));
const dom = new JSDOM(html, {
  url: 'http://localhost' + (PAGE === '.' ? '/' : PAGE.endsWith('.html') ? '/' + PAGE : '/' + PAGE.replace(/^\/|\/$/g, '') + '/'),
  runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
  beforeParse(win) {
    win.localStorage.setItem('satf.learner', LRN); win.localStorage.setItem('satf.me.fold2', 'true'); win.localStorage.setItem('satf.me.collapsed', '[]');
    win.localStorage.setItem('satf.welcomed', '1');
    win.matchMedia = q => {
      let m = false;
      const mw = /max-width:\s*(\d+)px/.exec(q), nw = /min-width:\s*(\d+)px/.exec(q);
      if (mw) m = W <= +mw[1]; if (nw) m = W >= +nw[1];
      if (/hover: hover|pointer: fine/.test(q)) m = true;
      if (/pointer: coarse|prefers-reduced-motion/.test(q)) m = false;
      return { matches: m, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} };
    };
    win.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
    win.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
    win.Element.prototype.scrollIntoView = function () {};
    // jsdom has no Web Animations: a no-op that finishes at once (the motion layer calls el.animate)
    if (!win.Element.prototype.animate) win.Element.prototype.animate = function () {
      const a = { finished: Promise.resolve(), onfinish: null, cancel() {}, play() {}, pause() {}, reverse() {}, finish() {}, commitStyles() {}, playState: 'finished', currentTime: 0, effect: null };
      Promise.resolve().then(() => { if (typeof a.onfinish === 'function') a.onfinish(); });
      a.finished.then(() => a); return a;
    };
    if (!win.Element.prototype.getAnimations) win.Element.prototype.getAnimations = function () { return []; };

    win.Element.prototype.scrollTo = function () {};
    win.HTMLElement.prototype.showPopover = function () {};
    win.HTMLElement.prototype.hidePopover = function () {};
    win.HTMLDialogElement && (win.HTMLDialogElement.prototype.showModal = function () { this.open = true; });
    win.HTMLDialogElement && (win.HTMLDialogElement.prototype.close = function (v) { const was = this.open; this.open = false; if (v !== undefined) this.returnValue = v; if (was) this.dispatchEvent(new win.Event('close')); });
    win.CSS = win.CSS || {}; win.CSS.escape = s => String(s).replace(/[^a-zA-Z0-9_-]/g, c => '\\' + c);
    win.scrollTo = () => {};
    win.fetch = async (url, o = {}) => {
      const u = new URL(url, 'http://127.0.0.1:8071/');
      const r = await fetch('http://127.0.0.1:8071' + u.pathname + u.search, { method: o.method || 'GET', headers: { 'content-type': 'application/json', 'X-Learner': LRN, 'X-Tz': '-300' }, body: o.body });
      const t = await r.text();
      return { ok: r.ok, status: r.status, headers: { get: () => null }, json: async () => JSON.parse(t), text: async () => t };
    };
    win.addEventListener('error', e => errors.push('window.error: ' + (e.error && e.error.stack || e.message)));
    win.addEventListener('unhandledrejection', e => errors.push('unhandled: ' + (e.reason && e.reason.stack || e.reason)));
  },
});
setTimeout(() => {
  const doc = dom.window.document;
  const name = el => (el.getAttribute('aria-label') || el.textContent || el.title || '').replace(/\s+/g, ' ').trim().slice(0, 60);
  const scope = doc.body;
  const inv = {
    href: [...scope.querySelectorAll('a[href]')].map(a => a.getAttribute('href').replace(/[?#].*$/, '')).filter(h => h && !h.startsWith('javascript')),
    button: [...scope.querySelectorAll('button, [role=button], [role=tab], [role=menuitem]')].map(name).filter(Boolean),
    id: [...scope.querySelectorAll('[id]')].map(e => e.id).filter(i => !/^(ui|uid|u|x|f|t|tip|pop|m|sheet|lbl|hd|d)[-_]?\d+/.test(i)),
    field: [...scope.querySelectorAll('input, select, textarea')].map(e => e.name || e.getAttribute('aria-label') || e.type),
  };
  for (const k in inv) inv[k] = [...new Set(inv[k])].sort();
  console.log(JSON.stringify(inv));
  process.exit(0);
}, +(process.env.WAIT || 5000));
