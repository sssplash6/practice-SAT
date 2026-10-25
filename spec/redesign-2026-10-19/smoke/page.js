// smoke test for any page: load it in jsdom with Today's stubbed /api responses (unknown endpoints answer {}),
// let it paint for 2.5 s, print the JS errors. usage: node page.js <web root> <page path> [width]
const path = require('path'), fs = require('fs');
const { JSDOM, VirtualConsole } = require('/Users/workingmyassof/freshbot/calc/node_modules/jsdom');
const WEB = process.argv[2], PAGE = process.argv[3], W = parseInt(process.argv[4] || '1440', 10);
// FIX=practice adds /bank, /drill/preview, /sets and /next (Practice); the default stays the Today set
const F = require(__dirname + (process.env.FIX ? `/fixtures-${process.env.FIX}.js` : '/fixtures.js'))('plan');

const file = path.join(WEB, PAGE.endsWith('.html') ? PAGE : path.join(PAGE, 'index.html'));
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
  url: 'http://localhost' + (PAGE.endsWith('.html') ? '/' + PAGE : '/' + PAGE.replace(/^\/|\/$/g, '') + '/'),
  runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
  beforeParse(win) {
    win.localStorage.setItem('satf.learner', 'd:' + 'a'.repeat(32));
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
      const u = new URL(url, 'http://localhost/');
      const p = u.pathname.replace(/^\/api/, '');
      const key = Object.keys(F).find(k => k === p) || Object.keys(F).find(k => p.startsWith(k));
      const body = key ? (typeof F[key] === 'function' ? F[key](u, o) : F[key]) : {};
      return { ok: true, status: 200, headers: { get: () => null }, json: async () => JSON.parse(JSON.stringify(body)), text: async () => JSON.stringify(body) };
    };
    win.addEventListener('error', e => errors.push('window.error: ' + (e.error && e.error.stack || e.message)));
    win.addEventListener('unhandledrejection', e => errors.push('unhandled: ' + (e.reason && e.reason.stack || e.reason)));
  },
});
setTimeout(() => {
  const doc = dom.window.document;
  const main = doc.querySelector('main');
  console.log('main text: ' + (main ? main.textContent.replace(/\s+/g, ' ').trim().slice(0, 160) : '(no main)'));
  console.log(errors.length ? 'ERRORS:\n' + errors.map(e => e.split('\n').slice(0, 3).join(' | ')).join('\n') : 'NO ERRORS');
  process.exit(0);
}, 2500);
