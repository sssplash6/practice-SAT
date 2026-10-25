// smoke test for web/index.html (Today): load the page in jsdom with stubbed /api responses, let it paint, report errors
// usage: node run.js <fixture-variant>
const path = require('path'), fs = require('fs');
const { JSDOM, VirtualConsole } = require('/Users/workingmyassof/freshbot/calc/node_modules/jsdom');
const WEB = '/Users/workingmyassof/freshbot/satbank/web';
const variant = process.argv[2] || 'plan';
const F = require('./fixtures.js')(variant);

let html = fs.readFileSync(path.join(WEB, 'index.html'), 'utf8');
// inline the shared scripts so they run in order
html = html.replace(/<script src="\/assets\/([a-z-]+)\.js"><\/script>/g, (m, n) => {
  const p = path.join(WEB, 'assets', n + '.js');
  return fs.existsSync(p) ? `<script>${fs.readFileSync(p, 'utf8').replace(/<\/script>/g, '<\\/script>')}</script>` : '';
});
html = html.replace(/<link[^>]*>/g, '');
const errors = [];
const vc = new VirtualConsole();
vc.on('error', (...a) => errors.push('console.error: ' + a.map(x => (x && x.stack) || String(x)).join(' ')));
vc.on('jsdomError', e => errors.push('jsdomError: ' + ((e && (e.detail && e.detail.stack)) || e.stack || e.message)));
const W = parseInt(process.argv[3] || '1440', 10);
const dom = new JSDOM(html, {
  url: 'http://localhost/', runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
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
      return { ok: true, status: 200, headers: { get: () => null }, json: async () => JSON.parse(JSON.stringify(body)) };
    };
    win.addEventListener('error', e => errors.push('window.error: ' + (e.error && e.error.stack || e.message)));
    win.addEventListener('unhandledrejection', e => errors.push('unhandled: ' + (e.reason && e.reason.stack || e.reason)));
  },
});
const win = dom.window, doc = win.document;
setTimeout(() => {
  const $ = id => doc.getElementById(id);
  if (process.argv[4] === 'act') {
    const click = (sel, root = doc) => { const e = root.querySelector(sel); if (!e) { errors.push('missing ' + sel); return; } e.click(); };
    try {
      click('#qotd .qd-fs'); errors.push('fs full: ' + !!doc.querySelector('.qd-slot.full') + ' btn on: ' + doc.querySelector('.qd-fs').classList.contains('on'));
      doc.querySelectorAll('#qotd [role=tab]')[1].click(); errors.push('full follows tab: ' + (doc.querySelector('.qd-slot.full') || {}).id);
      $('qotd').querySelector('.qd-slot.on').dispatchEvent(new win.KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); errors.push('after Esc full: ' + !!doc.querySelector('.qd-slot.full'));
      click('#next .cardfold'); errors.push('next collapsed: ' + $('next').classList.contains('collapsed')); click('#next .cardfold');
      [...doc.querySelectorAll('#next button.quiet')].find(b => /practice session/.test(b.textContent))?.click();
      errors.push('builder open: ' + !!doc.querySelector('#next .sess') + ' visible ' + !doc.querySelector('#next .sess').parentElement.hidden);
      click('#next .td-foot button.fold');
      click('#since button.fold'); errors.push('since open: ' + doc.querySelector('#since button.fold').getAttribute('aria-expanded'));
      // Score's details are inline now (premium build); Study keeps its fold where it has one
      if (doc.querySelector('#study button.fold')) click('#study button.fold');
      click('#tests button.fold'); errors.push('older test open: ' + doc.querySelector('#tests button.fold').getAttribute('aria-expanded'));
      let fired = false; const rb = doc.querySelector('#hero .td-risk .btn'); rb.addEventListener('click', () => { fired = true; });
      doc.getElementById('hero-h').focus(); doc.dispatchEvent(new win.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
      errors.push('Enter on header h1 fired risk btn: ' + fired + ' (focus ' + doc.activeElement.id + ')');
    } catch (e) { errors.push('act: ' + e.stack); }
  }
  const txt = el => el ? el.textContent.replace(/\s+/g, ' ').trim().slice(0, 260) : '(none)';
  const out = [];
  out.push('main order: ' + [...doc.querySelector('.td-main').children].map(e => e.id).join(','));
  out.push('aside order: ' + [...doc.querySelector('.twocol-side').children].map(e => e.id).join(','));
  ['hero', 'next', 'due', 'sum', 'qotd', 'mist', 'gain', 'exam', 'score', 'pace', 'study', 'cal', 'chal', 'words', 'tests', 'soon'].forEach(id => {
    const e = $(id);
    out.push(`#${id}${e && e.hidden ? ' [hidden]' : ''}: ${txt(e)}`);
  });
  out.push('pills: ' + [...doc.querySelectorAll('#today .pill')].map(b => `${b.closest('section, header') ? (b.closest('section, header').id) : '?'}:${b.textContent.trim()}`).join(' | '));
  out.push('drows: ' + [...doc.querySelectorAll('#due .drow')].map(r => `${r.dataset.key}[${[...r.querySelectorAll('.dact button')].map(b => b.className).join('+')}]`).join(' '));
  console.log(out.join('\n'));
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n---\n') : 'NO ERRORS');
  process.exit(0);
}, 2500);
