/* ============================================================================
   SAT Freshman -- Report a problem, and Send feedback: one modal everywhere
   (spec/rebuild-v2.md R17, Shell 2.10; v2-upgrades U3, V6, W18, X10, SR19, P25)

   Loaded after ui.js and kit.js on every page (it needs UI.sheet and UI.chips).
   Adds to window.UI. Its few styles are injected once, on tokens from ui.css.

   UI.report(ctx) -> the sheet api, or the open one
     ctx  kind      'question' | 'sitting' | 'page' | 'word' | 'paper' | 'catalog'
                    (inferred as the server does: a question with session and
                    question_id, template and seed, or source qotd | challenge; else page)
          source    'drill' | 'test' | 'report' | 'qotd' | 'challenge' | 'quick' | 'review'
                    | 'library' | 'words' | 'page' ...
          session, question_id, day, template, seed, word, paper, page
          revealed, live   the caller's view; the server's own records decide
          category  preselected: an id or its label ('Wrong mistake label', V6)
          option    the option a label report is about (V6), sent as the answer
          include_answer   tick "Include my answer" (Report now after hand-in, X10)
          label     'Module 1 · Q7' in place of 'Question 7 of 22'
          meaning   a word's current text, prefilled by "Suggest a better meaning" (W18)
          onSent(result)   after a send, with {id, status, check?, thanks?}: P25 voids
                           and replaces on check.outcome 'broken', flips on 'remarked'
          onLater(ctx)     "Remind me after the test"; default POST /api/session/{id}/state
                           {report_later: question_id} (X10)
     With no ctx it is Send feedback about this page; ?feedback on any URL opens it.
     A live sitting (the server says so) opens on "Remind me after the test", its
     one-tap chips under it, no marking and no key dispute (R17, X10).
   UI.report.send(ctx, {category, title, details, answer, quiet}) -> Promise<result>
     no dialog: W18's "Another choice also fits"; toasts "Sent" unless quiet
   UI.report.sent(ctx) -> the report id sent for that question on this page load, or null
   UI.report.trail() -> the last 10 actions on this page load (path, control, API path
     and status), kept in memory only and sent only with "Include device details"
   document 'satf:report' event, detail {ctx, result}, after every send
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI = window.UI || {};
  const doc = document;
  const MB = 1 << 20;

  /* ------------------------------------------------------------ helpers */
  function h(tag, attrs = {}, ...kids) {
    const e = doc.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat(3)) if (k !== null && k !== undefined && k !== false) e.append(k instanceof Node ? k : String(k));
    return e;
  }
  const media = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  const bytes = n => (n >= MB ? `${(n / MB).toFixed(n >= 10 * MB ? 0 : 1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);
  const cap1 = s => (s ? s[0].toUpperCase() + s.slice(1) : s);
  const store = {
    get(k) { try { return JSON.parse(sessionStorage.getItem(k) || 'null'); } catch (_) { return null; } },
    set(k, v) { try { if (v === null) sessionStorage.removeItem(k); else sessionStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const learner = () => (UI.learner && UI.learner()) || '';
  const headers = () => ({ 'X-Learner': learner(), 'X-Tz': String(new Date().getTimezoneOffset()) });

  async function take(r) {
    const swap = r.headers.get('X-Learner-Swap');
    if (swap && /^d:[0-9a-z]{32}$/.test(swap) && UI.useLearner) UI.useLearner(swap, { same: true });
    let body = null;
    try { body = await r.json(); } catch (_) {}
    if (!r.ok) {
      const d = body && body.detail;
      throw Object.assign(new Error(typeof d === 'string' ? d : `HTTP ${r.status}`), { status: r.status, detail: d });
    }
    return body;
  }
  async function call(path, o = {}) {
    if (UI.ready && typeof UI.ready.then === 'function') await UI.ready;
    let r;
    try {
      r = await fetch('/api' + path, { method: o.method || 'GET', headers: { ...headers(), 'content-type': 'application/json' },
                                       body: o.body === undefined ? undefined : JSON.stringify(o.body) });
    } catch (_) { throw Object.assign(new Error('offline'), { status: 0 }); }
    return take(r);
  }
  async function postReport(data, files) {
    if (UI.ready && typeof UI.ready.then === 'function') await UI.ready;
    const fd = new FormData();
    fd.append('data', JSON.stringify(data));
    for (const f of files) fd.append('files', f, f.name);
    let r;
    try { r = await fetch('/api/report', { method: 'POST', headers: headers(), body: fd }); }
    catch (_) { throw Object.assign(new Error('offline'), { status: 0 }); }
    return take(r);
  }
  const qs = o => new URLSearchParams(Object.entries(o).filter(([, v]) => v !== null && v !== undefined && v !== '')).toString();

  /* ------------------------------------------------------------ styles */
  const CSS = `
dialog.sheet.rp { max-width: min(560px, calc(100vw - 32px)); }
@media (max-width: 759px) {
  dialog.sheet.rp, dialog.sheet.rp[data-size] { inset: 0; margin: 0; width: 100%; max-width: 100%; height: 100dvh; max-height: 100dvh; border-radius: 0; }
  dialog.sheet.rp::before { display: none; }
}
.rp .sheet-body { display: grid; gap: 18px; align-content: start; }
.rp-sec { display: grid; gap: 8px; min-width: 0; }
.rp-sec > .label, .rp-sec > .help, .rp-sec > .k { margin: 0; }
.rp-req { font-weight: 500; color: var(--soft); }
.rp-box { display: grid; gap: 3px; padding: 12px 14px; border-radius: var(--radius); background: var(--tile);
  font: 400 12.5px/1.55 var(--mono); color: var(--ink); overflow-wrap: anywhere; font-variant-numeric: tabular-nums; }
.rp-box .rp-skill { font: 600 13px/1.4 var(--font); display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; }
.rp-box .check { min-height: 34px; font: 500 13.5px/1.35 var(--font); }
.rp-show { appearance: none; border: 0; background: none; padding: 4px 2px; cursor: pointer; font: 500 13px var(--font); color: var(--soft);
  text-decoration: underline; text-underline-offset: 3px; }
.rp-show:hover { color: var(--ink); }
.rp-dev { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 2px 12px; margin: 2px 0 4px; }
.rp-dev dt { color: var(--soft); }
.rp-dev dd { margin: 0; min-width: 0; }
.rp-dev ol { margin: 0; padding-left: 18px; }
.rp-live { display: grid; gap: 10px; padding: 14px 16px; border-radius: 12px; background: var(--wash); }
.rp-live .pill { justify-self: start; }
.rp-metoo { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; padding: 12px 14px; border-radius: var(--radius);
  background: var(--wash); font: 500 14px/1.4 var(--font); color: var(--ink); }
.rp-metoo > span { flex: 1 1 220px; min-width: 0; }
.rp-files { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
.rp-file { display: grid; grid-template-columns: 44px minmax(0, 1fr) auto; align-items: center; gap: 4px 12px; padding: 6px;
  border-radius: var(--radius); background: var(--tile); }
.rp-file .th { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; background: var(--tile-2);
  display: grid; place-items: center; font: 600 10px var(--mono); color: var(--soft); text-transform: uppercase; }
.rp-file .nm { min-width: 0; font: 500 13.5px/1.3 var(--font); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rp-file .sz { display: block; font: 500 12px var(--mono); color: var(--soft); }
.rp-file[data-bad] { background: var(--paper); box-shadow: inset 0 0 0 1px var(--line); }
.rp-file .why { grid-column: 2 / -1; font: 500 12.5px/1.4 var(--font); color: var(--ink); }
.rp-drop { border-radius: var(--radius); transition: box-shadow .16s var(--ease), background-color .16s var(--ease); }
.rp-drop.drag { background: var(--wash); box-shadow: 0 0 0 1.5px var(--amber); }
.rp-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; }
.rp-pv { min-height: 22px; font: 500 14px var(--font); color: var(--soft); }
.rp-pv .frac { display: inline-flex; flex-direction: column; vertical-align: middle; text-align: center; line-height: 1.05; }
.rp-pv .fd { border-top: 1.5px solid currentColor; }
.rp-ans > button { min-width: 52px; justify-content: center; font-family: var(--mono); }
.rp-out { font: 400 15.5px/1.55 var(--font); color: var(--ink); text-wrap: pretty; }
.rp-out a, .rp-thanks a { color: inherit; text-underline-offset: 3px; }
.rp-why { padding: 12px 14px; border-radius: var(--radius); background: var(--tile); font: 400 15px/1.55 var(--serif); color: var(--ink); }
.rp-acts { display: grid; gap: 8px; justify-items: start; }
.rp-err { margin: 0; }
.rp-rec { position: fixed; z-index: 90; left: 50%; bottom: calc(20px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%);
  display: flex; align-items: center; gap: 12px; padding: 6px 6px 6px 16px; border-radius: 999px;
  background: var(--ink); color: var(--on-ink); box-shadow: var(--shadow-pop); font: 600 14px var(--font); }
.rp-rec .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--amber); }
.rp-rec .t { font-family: var(--mono); font-variant-numeric: tabular-nums; }
.rp-rec button { min-height: 34px; }
@media print { .rp-rec { display: none; } }
`;
  function styles() {
    if (doc.getElementById('rp-css')) return;
    doc.head.append(h('style', { id: 'rp-css', text: CSS }));
  }

  /* ------------------------------------------------------------ the last 10 actions (U3's breadcrumb)
     A click on a control and every same-origin /api call, in memory for this page load
     only; listed under "Include device details › Show" and sent only with that box. */
  const TRAIL = [];
  const note = e => {
    TRAIL.push({ at: new Date().toTimeString().slice(0, 8), path: location.pathname, ...e });
    if (TRAIL.length > 10) TRAIL.shift();
  };
  const labelOf = el => (el.getAttribute('aria-label') || el.textContent || el.value || el.title || el.tagName.toLowerCase())
    .replace(/\s+/g, ' ').trim().slice(0, 60);
  doc.addEventListener('click', e => {
    const c = e.target instanceof Element && e.target.closest(
      'button, a[href], summary, [role="button"], [role="tab"], [role="radio"], [role="option"], [role="menuitem"], [role="switch"], input[type="checkbox"], input[type="radio"]');
    if (c && !c.closest('.rp, .rp-rec')) note({ control: labelOf(c) });
  }, true);
  // long codes in a path (share codes, tokens) never leave in the breadcrumb
  const bare = p => p.replace(/\/[A-Za-z0-9:_-]{16,}(?=\/|$)/g, '/…');
  if (typeof window.fetch === 'function' && !window.fetch.rpTrail) {
    const plain = window.fetch;
    const traced = function (input, init) {
      const p = plain.apply(this, arguments);
      try {
        const u = new URL(typeof input === 'string' || input instanceof URL ? String(input) : input.url, location.href);
        if (u.origin === location.origin && u.pathname.startsWith('/api/') && !/^\/api\/(reports?|health)(\/|$)/.test(u.pathname)) {
          const m = String((init && init.method) || (input && input.method) || 'GET').toUpperCase();
          const api = `${m} ${bare(u.pathname)}`;
          p.then(r => note({ api, status: r.status }), () => note({ api, status: 'no answer' }));
        }
      } catch (_) {}
      return p;
    };
    traced.rpTrail = true;
    window.fetch = traced;
  }

  /* ------------------------------------------------------------ device details */
  let health = null;
  const healthy = () => health || (health = fetch('/api/health').then(r => r.json()).catch(() => ({})));
  function agent() {
    const ua = navigator.userAgent;
    const first = list => { for (const [re, name, ver] of list) { const m = ua.match(re); if (m) return ver && m[1] ? `${name} ${m[1].split(/[._]/)[0]}` : name; } return ''; };
    return {
      browser: first([[/Edg\/([\d.]+)/, 'Edge', 1], [/OPR\/([\d.]+)/, 'Opera', 1], [/FxiOS\/([\d.]+)/, 'Firefox', 1],
                      [/Firefox\/([\d.]+)/, 'Firefox', 1], [/CriOS\/([\d.]+)/, 'Chrome', 1], [/Chrome\/([\d.]+)/, 'Chrome', 1],
                      [/Version\/([\d.]+).*Safari/, 'Safari', 1]]) || ua.slice(0, 80),
      os: first([[/iPhone OS ([\d_]+)/, 'iOS', 1], [/iPad.*? OS ([\d_]+)/, 'iPadOS', 1], [/Android ([\d.]+)/, 'Android', 1],
                 [/CrOS/, 'ChromeOS'], [/Mac OS X/, 'macOS'], [/Windows/, 'Windows'], [/Linux/, 'Linux']]),
    };
  }
  async function device() {
    const hl = await healthy();
    const a = agent();
    let tz = '';
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (_) {}
    const off = -new Date().getTimezoneOffset();
    const d = { browser: a.browser, os: a.os, viewport: `${innerWidth}×${innerHeight}`,
                timezone: `${tz}${tz ? ' ' : ''}(UTC${off >= 0 ? '+' : '−'}${Math.floor(Math.abs(off) / 60)}${Math.abs(off) % 60 ? ':' + String(Math.abs(off) % 60).padStart(2, '0') : ''})`,
                app: hl.version || hl.build || null, url: location.href.replace(/=([A-Za-z0-9:_-]{16,})/g, '=…'),
                actions: TRAIL.map(x => ({ ...x })) };
    if (!d.app) delete d.app;
    return d;
  }
  const DEVICE_LABEL = { browser: 'Browser', os: 'System', viewport: 'Window', timezone: 'Time zone', app: 'App version', url: 'Page', actions: 'Last actions' };
  function deviceList(d) {
    const dl = h('dl', { class: 'rp-dev' });
    for (const [k, v] of Object.entries(d)) {
      if (k === 'actions') {
        dl.append(h('dt', { text: DEVICE_LABEL[k] }), h('dd', {}, v.length
          ? h('ol', {}, v.map(x => h('li', { text: [x.at, x.path, x.control, x.api, x.status].filter(y => y !== undefined && y !== null).join(' · ') })))
          : 'none yet'));
      } else dl.append(h('dt', { text: DEVICE_LABEL[k] || k }), h('dd', { text: String(v || '—') }));
    }
    return dl;
  }

  /* ------------------------------------------------------------ files (U3)
     Up to 10: PNG, JPEG and WebP stills downscaled to 2000px on the long edge and
     re-encoded (WebP, JPEG where WebP encoding is missing), 10 MB after that; a GIF as
     it is and a screen recording (WebM, MP4) up to 50 MB each; 200 MB a report. A file
     over its cap is refused in its row, with the reason, before anything is sent. */
  const CAP = { 'image/png': 10 * MB, 'image/jpeg': 10 * MB, 'image/webp': 10 * MB,
                'image/gif': 50 * MB, 'video/webm': 50 * MB, 'video/mp4': 50 * MB };
  const STILL = ['image/png', 'image/jpeg', 'image/webp'];
  const MAX_FILES = 10, TOTAL = 200 * MB, EDGE = 2000, RECORD_S = 60;
  const what = t => (t.startsWith('video/') ? 'video' : t === 'image/gif' ? 'GIF' : 'image');
  async function shrink(file) {
    if (!STILL.includes(file.type) || typeof createImageBitmap !== 'function') return file;
    let bmp;
    try { bmp = await createImageBitmap(file); } catch (_) { return file; }
    const k = Math.min(1, EDGE / Math.max(bmp.width, bmp.height));
    // a small screenshot is kept as it is, so its text stays sharp
    if (k === 1 && file.size <= 1.5 * MB) { if (bmp.close) bmp.close(); return file; }
    const c = doc.createElement('canvas');
    c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
    const g = c.getContext('2d');
    g.fillStyle = '#fff';               // JPEG has no alpha: transparent pixels land on white, not black
    g.fillRect(0, 0, c.width, c.height);
    g.drawImage(bmp, 0, 0, c.width, c.height);
    if (bmp.close) bmp.close();
    let blob = await new Promise(r => c.toBlob(r, 'image/webp', 0.9));
    if (!blob || blob.type !== 'image/webp') blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.9));
    if (!blob) return file;
    const ext = blob.type === 'image/webp' ? 'webp' : 'jpg';
    return new File([blob], `${(file.name || 'image').replace(/\.[^.]+$/, '')}.${ext}`, { type: blob.type });
  }
  const canRecord = () => !!(navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia && window.MediaRecorder)
    && !media('(pointer: coarse)');

  function fileBox(items, o) {
    const input = h('input', { type: 'file', multiple: true, hidden: true, accept: Object.keys(CAP).join(',') });
    const list = h('ul', { class: 'rp-files', 'aria-label': 'Files', hidden: true });
    const msg = h('p', { class: 'help', role: 'status' });
    const good = () => items.filter(x => !x.err);
    const total = () => good().reduce((n, x) => n + x.size, 0);
    const addBtn = h('button', { type: 'button', class: 'btn sm', onclick: () => input.click() }, 'Add files');
    const recBtn = canRecord() ? h('button', { type: 'button', class: 'btn sm', onclick: () => o.onRecord() }, 'Record screen') : null;
    function draw() {
      list.replaceChildren(...items.map(x => {
        const th = x.url && x.type.startsWith('image/') ? h('img', { class: 'th', src: x.url, alt: '' })
          : x.url && x.type.startsWith('video/') ? h('video', { class: 'th', src: x.url, muted: true, preload: 'metadata', 'aria-hidden': 'true' })
          : h('span', { class: 'th', 'aria-hidden': 'true', text: (x.name.split('.').pop() || '?').slice(0, 4) });
        const rm = h('button', { type: 'button', class: 'x', 'aria-label': `Remove ${x.name}`, onclick: () => {
          const i = items.indexOf(x);
          if (i >= 0) items.splice(i, 1);
          if (x.url) URL.revokeObjectURL(x.url);
          draw();
          addBtn.focus();
        } }, h('span', { 'aria-hidden': 'true', text: '×' }));
        return h('li', { class: 'rp-file', 'data-bad': x.err ? '' : null }, th,
          h('span', { class: 'nm', title: x.name }, x.name, h('span', { class: 'sz', text: x.err ? 'not sent' : bytes(x.size) })), rm,
          x.err ? h('span', { class: 'why', text: x.err }) : null);
      }));
      list.hidden = !items.length;
      const n = good().length;
      addBtn.disabled = n >= MAX_FILES;
      if (recBtn) recBtn.disabled = n >= MAX_FILES;
      msg.textContent = n >= MAX_FILES ? `Up to ${MAX_FILES} files.`
        : n ? `${n} of ${MAX_FILES} files · ${bytes(total())}`
        : 'Paste or drop images and screen recordings. Images are shrunk to 2000px; GIFs and videos go as they are, up to 50 MB each.';
    }
    async function add(fs) {
      for (const f0 of [...fs]) {
        if (good().length >= MAX_FILES) { msg.textContent = `Up to ${MAX_FILES} files.`; break; }
        const row = { name: f0.name || 'file', size: f0.size, type: f0.type || '' };
        if (!CAP[row.type]) row.err = 'That isn’t an image or a video: PNG, JPEG, WebP, GIF, WebM or MP4.';
        else {
          const f = await shrink(f0);
          Object.assign(row, { file: f, name: f.name || row.name, size: f.size, type: f.type });
          if (f.size > CAP[f.type]) row.err = `This ${what(f.type)} is ${bytes(f.size)}. The limit is ${bytes(CAP[f.type])}.`;
          else if (total() + f.size > TOTAL) row.err = `That would pass ${bytes(TOTAL)} for this report.`;
          else row.url = URL.createObjectURL(f);
        }
        items.push(row);
      }
      draw();
    }
    input.addEventListener('change', () => { add(input.files); input.value = ''; });
    const el = h('div', { class: 'rp-sec' }, h('div', { class: 'rp-row' }, addBtn, recBtn), msg, list, input);
    draw();
    return { el, add, draw, files: () => good().map(x => x.file),
      refuse(name, text) {                     // a 413 / 415 from the server, back in its row
        const x = good().find(y => y.name === name) || good()[0];
        if (x) { x.err = text; if (x.url) { URL.revokeObjectURL(x.url); x.url = null; } draw(); }
      } };
  }

  // screen recording: the report closes while it runs, so the page can be used; Stop (or
  // 60 s, or the browser's own Stop sharing) opens it again with the clip in its list
  let recording = null;
  async function record(onDone) {
    if (recording) return false;
    let stream;
    try { stream = await navigator.mediaDevices.getDisplayMedia({ video: { frameRate: 15 }, audio: false }); }
    catch (_) { return false; }                         // refused at the browser's own prompt
    const type = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm', 'video/mp4']
      .find(t => MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) || '';
    let rec;
    try { rec = new MediaRecorder(stream, { mimeType: type || undefined, videoBitsPerSecond: 2500000 }); }
    catch (_) { stream.getTracks().forEach(t => t.stop()); return false; }
    const chunks = [];
    let got = 0, sec = 0;
    const t = h('span', { class: 't', text: '0:00' });
    const stop = () => { if (rec.state !== 'inactive') rec.stop(); };
    const bar = h('div', { class: 'rp-rec', role: 'status', 'aria-live': 'polite' },
      h('span', { class: 'dot', 'aria-hidden': 'true' }), h('span', {}, 'Recording ', t),
      h('button', { type: 'button', class: 'btn sm', onclick: stop }, 'Stop'));
    const tick = setInterval(() => {
      sec++;
      t.textContent = `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;
      if (sec >= RECORD_S) stop();
    }, 1000);
    rec.ondataavailable = e => {
      if (!e.data || !e.data.size) return;
      chunks.push(e.data);
      got += e.data.size;
      if (got > CAP['video/webm'] - 2 * MB) stop();     // stop before the 50 MB cap
    };
    rec.onstop = () => {
      clearInterval(tick);
      stream.getTracks().forEach(x => x.stop());
      bar.remove();
      recording = null;
      const kind = (rec.mimeType || type || 'video/webm').split(';')[0];
      const blob = new Blob(chunks, { type: kind });
      onDone(blob.size ? new File([blob], `screen-recording-${sec}s.${kind === 'video/mp4' ? 'mp4' : 'webm'}`, { type: kind }) : null);
    };
    stream.getVideoTracks().forEach(x => x.addEventListener('ended', stop));
    rec.start(1000);
    recording = rec;
    doc.body.append(bar);
    bar.querySelector('button').focus({ preventScroll: true });
    return true;
  }

  /* ------------------------------------------------------------ what a report is about */
  const kindOf = c => c.kind || (c.session && c.question_id || c.template || c.source === 'qotd' || c.source === 'challenge' ? 'question' : 'page');
  const TITLE = { question: 'Report a problem with this question', word: 'Report a problem with this word',
                  sitting: 'Report a problem with this sitting', paper: 'Report a problem with this paper',
                  catalog: 'Report a problem', page: 'Send feedback' };
  const day = d => (UI.date ? UI.date(d) : d);
  const sittingName = st => [(UI.KIND && UI.KIND[st.kind]) || cap1(st.kind || 'sitting'), st.number ? `#${st.number}` : null].filter(Boolean).join(' ');
  const pageName = () =>(doc.title || '').replace(/\s*[·|–-]\s*SAT Freshman\s*$/, '').trim() || location.pathname;
  const keyOf = c => 'satf.report.' + [c.kind, c.source, c.session, c.question_id, c.day, c.template, c.seed, c.word, c.paper,
    c.kind === 'page' ? c.page : ''].map(x => (x === undefined || x === null ? '' : x)).join('|');
  const qKey = c => (c.session && c.question_id ? `${c.session}|${c.question_id}` : c.template ? `${c.template}|${c.seed}`
    : c.day ? `${c.source}|${c.day}|${c.question_id || ''}` : null);
  const SENT = new Map();                 // question -> report id, for this page load
  const KEPT = new Map();                 // context key -> its files, kept across a close
  const wire = c => ({ kind: c.kind, source: c.source || 'page', session: c.session || null,
    question_id: c.question_id || null, day: c.day || null, template: c.template || null,
    seed: c.seed === undefined || c.seed === null || c.seed === '' ? null : Number(c.seed),
    word: c.word || null, paper: c.paper === undefined || c.paper === null ? null : String(c.paper), page: c.page || null });

  function reported(ctx, res, opener) {
    const k = qKey(ctx);
    if (k && res && res.id) SENT.set(k, res.id);
    // the question's Report button reads "Reported" and is disabled for that question
    if (opener && opener.isConnected && opener.tagName === 'BUTTON' && (ctx.kind === 'question' || ctx.kind === 'word')
        && (opener.classList.contains('qa-report') || 'report' in opener.dataset)) {
      const lab = opener.querySelector('.qa-l') || (opener.children.length ? null : opener);
      if (lab) lab.textContent = 'Reported';
      opener.disabled = true;
    }
    try { if (ctx.onSent) ctx.onSent(res); } catch (e) { setTimeout(() => { throw e; }); }
    doc.dispatchEvent(new CustomEvent('satf:report', { detail: { ctx, result: res } }));
  }

  function errText(e) {
    if (!e || e.status === 0) return 'Couldn’t send. Your text is kept.';
    if (e.status === 429) return e.message && !/^HTTP/.test(e.message) ? e.message : 'That’s a lot of reports in an hour. Try again later.';
    if (e.status === 413 || e.status === 415) return 'One file can’t be sent. It is marked in the list.';
    if (e.status === 422 && Array.isArray(e.detail)) return 'Something in the form isn’t right: ' + e.detail.map(x => x.msg).join('; ');
    if (e.detail && e.detail.allowed) return 'That category isn’t open here.';
    return e.message && !/^HTTP/.test(e.message) ? e.message : 'That didn’t work. Try again.';
  }

  /* ------------------------------------------------------------ the modal */
  let current = null;
  function report(ctx0) {
    styles();
    if (current && current.el.isConnected && current.el.open) { current.el.focus(); return current; }
    const ctx = { ...(ctx0 || {}) };
    ctx.kind = kindOf(ctx);
    if (!ctx.page && ['page', 'catalog', 'paper', 'sitting'].includes(ctx.kind)) ctx.page = location.pathname + location.hash;
    const opener = doc.activeElement;
    const key = keyOf(ctx);
    const draft = store.get(key) || {};
    const saveDraft = () => store.set(key, draft);
    if (!KEPT.has(key)) KEPT.set(key, []);
    const items = KEPT.get(key);

    const foot = h('div', { class: 'sheet-foot' });
    const s = UI.sheet({ title: TITLE[ctx.kind] || TITLE.page, className: 'rp', label: TITLE[ctx.kind],
      body: b => { b.append(h('div', { class: 'rp-box', 'aria-hidden': 'true' }, h('span', { class: 'skel line', style: 'width:60%' }),
        h('span', { class: 'skel line', style: 'width:40%' }))); },
      onClose: () => { if (current === s) current = null; } });
    s.el.append(foot);
    current = s;
    const setFoot = (...btns) => foot.replaceChildren(...btns.filter(Boolean));
    const quiet = (label, fn) => h('button', { type: 'button', class: 'quiet', onclick: fn }, label);
    const closeBtn = () => h('button', { type: 'button', class: 'pill sm', onclick: () => s.close() }, 'Close');
    setFoot(quiet('Cancel', () => s.close()));

    let pv = null;
    const load = async () => {
      try {
        pv = await call('/reports/context?' + qs({ ...wire(ctx), category: ctx.category }));
        form();
      } catch (e) {
        const again = h('button', { type: 'button', class: 'btn sm', onclick: () => { s.body.replaceChildren(); load(); } }, 'Retry');
        const asPage = ctx.kind !== 'page' ? h('button', { type: 'button', class: 'btn sm', onclick: () => {
          s.close();
          report({ kind: 'page', page: location.pathname, source: 'page', title: TITLE[ctx.kind] });
        } }, 'Send it as feedback about this page') : null;
        s.body.replaceChildren(h('div', { class: 'card-err', role: 'alert' },
          h('span', { text: e.status === 0 ? 'Couldn’t reach SAT Freshman.' : `Couldn’t load what this report is about: ${errText(e)}` }), again, asPage));
      }
    };

    /* ---------- the form */
    function form() {
      const box = pv.box || {};
      ctx.kind = pv.kind;
      const live = !!box.live;
      const isQ = !!box.template;
      const labels = pv.labels || {};
      const allowed = pv.allowed || [];
      let category = draft.category && allowed.includes(draft.category) ? draft.category : pv.category;
      const body = s.body;
      body.replaceChildren();

      /* live: "Remind me after the test" first (X10) */
      if (live && ctx.session && ctx.question_id) {
        const end = ctx.source === 'challenge' ? 'the challenge' : /test|mock|diagnostic|paper/.test(ctx.source || box.sitting_kind || 'test') ? 'the test' : 'the set';
        const later = h('button', { type: 'button', class: 'pill', onclick: async () => {
          later.setAttribute('aria-busy', 'true');
          try {
            if (ctx.onLater) await ctx.onLater(ctx);
            else await call(`/session/${encodeURIComponent(ctx.session)}/state`, { method: 'POST', body: { report_later: ctx.question_id } });
            s.close();
            toast(end === 'the test' ? 'We’ll ask after you hand in' : `We’ll ask after ${end}`);
          } catch (e) {
            later.removeAttribute('aria-busy');
            fail.textContent = e.status === 0 ? 'Couldn’t reach SAT Freshman. Report it now instead.' : 'Couldn’t save that. Report it now instead.';
            fail.hidden = false;
          }
        } }, `Remind me after ${end}`);
        body.append(h('div', { class: 'rp-live' }, later,
          h('p', { class: 'help', text: 'Or report it now: pick what’s wrong and Send. The clock keeps running.' })));
      }

      /* what's wrong? (radio chips, required) */
      const chipSec = h('div', { class: 'rp-sec' }, h('p', { class: 'label', id: 'rp-cat', text: 'What’s wrong?' }));
      const chips = UI.chips(chipSec, allowed.map(id => ({ value: id, label: labels[id] || id })),
        { value: category || null, label: 'What’s wrong?', onChange: v => { category = v; draft.category = v; saveDraft(); shape(); metoo(); } });
      chips.el.setAttribute('aria-labelledby', 'rp-cat');

      /* sent with this */
      const lines = [];
      if (isQ) {
        const diff = box.difficulty ? (UI.dbars ? UI.dbars(box.difficulty) : h('span', { class: 'meta', text: cap1(box.difficulty) })) : null;
        lines.push(h('div', { class: 'rp-skill' }, h('span', { text: box.skill || box.topic_name || box.template }), diff));
        const where = ctx.label || (box.n ? `Question ${box.n}${box.of ? ` of ${box.of}` : ''}` : null);
        if (where) lines.push(h('div', { text: where }));
        if (box.given && box.marked) lines.push(h('div', { text: `Your answer: ${box.given} · marked ${box.marked}` }));
        if (ctx.option) lines.push(h('div', { text: `About option ${ctx.option}${ctx.reason ? `: ${ctx.reason}` : ''}` }));
        lines.push(h('div', { text: `We have this exact question (${box.template} · seed ${box.seed}). No screenshot needed.` }));
      }
      if (ctx.kind === 'word' && box.word) lines.unshift(h('div', { class: 'rp-skill', text: box.word }));
      if (ctx.kind === 'sitting' && box.sitting) {
        const st = box.sitting;
        lines.push(h('div', { class: 'rp-skill', text: sittingName(st) }),
          h('div', { text: [st.date && day(st.date), st.band, st.finished ? null : 'in progress'].filter(Boolean).join(' · ') }));
      }
      if (ctx.kind === 'paper') lines.push(h('div', { class: 'rp-skill', text: box.paper_label || `Paper ${box.paper}` }));
      if (!isQ && (ctx.kind === 'page' || ctx.kind === 'catalog' || ctx.kind === 'paper')) {
        lines.push(h('div', { text: `${ctx.kind === 'catalog' ? 'Tests' : pageName()} · ${box.page || ctx.page}` }));
      }
      let include = null;
      if (box.given && !box.marked) {
        include = h('input', { type: 'checkbox' });
        include.checked = draft.include !== undefined ? !!draft.include : !!ctx.include_answer;
        include.addEventListener('change', () => { draft.include = include.checked; saveDraft(); });
        lines.push(h('label', { class: 'check' }, include, `Include my answer (${box.given})`));
      }
      const withDev = h('input', { type: 'checkbox', checked: true });
      const devList = h('div', { id: 'rp-dev', hidden: true });
      const devShow = h('button', { type: 'button', class: 'rp-show', 'aria-expanded': 'false', 'aria-controls': 'rp-dev', onclick: async () => {
        const open = devList.hidden;
        if (open) devList.replaceChildren(deviceList(await device()));
        devList.hidden = !open;
        devShow.setAttribute('aria-expanded', String(open));
        devShow.textContent = open ? 'Hide' : 'Show';
      } }, 'Show');
      lines.push(h('div', { class: 'rp-row' }, h('label', { class: 'check' }, withDev, 'Include device details'), devShow), devList);
      const boxSec = h('div', { class: 'rp-sec' }, h('p', { class: 'k', text: 'Sent with this' }), h('div', { class: 'rp-box' }, lines));

      /* me too (U3), outside a live sitting */
      const metooSec = h('div', { hidden: true });
      let parent = null;
      async function metoo() {
        if (!isQ || live) return;
        let sim = pv.similar;
        if (category) {
          try { sim = await call('/reports/similar?' + qs({ session: ctx.session, qid: ctx.question_id, day: ctx.day, source: ctx.source,
                                                             template: ctx.session ? null : ctx.template, seed: ctx.session ? null : ctx.seed, category })); }
          catch (_) { return; }
        }
        drawMetoo(sim);
      }
      function drawMetoo(sim) {
        parent = null;
        metooSec.replaceChildren();
        metooSec.hidden = !sim || (!sim.open && !sim.mine);
        if (metooSec.hidden) return;
        const others = sim.open === 1 ? '1 other' : `${sim.open} others`;
        if (sim.mine) {
          metooSec.append(h('div', { class: 'rp-metoo' }, h('span', {},
            sim.open ? `You and ${others} reported this · ${sim.status_label}` : `You reported this · ${sim.status_label}`),
            h('a', { class: 'link', href: '/me/settings/#reports' }, 'Your reports')));
          return;
        }
        parent = sim.id;
        const add = h('button', { type: 'button', class: 'btn sm', onclick: () => send({ parent: sim.id, category: category || sim.category }) }, 'Add me to it');
        metooSec.append(h('div', { class: 'rp-metoo' },
          h('span', {}, `Reported by ${others} · ${sim.status_label}`, h('br'), h('span', { class: 'meta', text: sim.category_label })), add));
      }
      drawMetoo(pv.similar);

      /* summary */
      const title = h('input', { class: 'field', id: 'rp-title', maxlength: '200', autocomplete: 'off' });
      title.value = draft.title !== undefined ? draft.title : ctx.title || pv.title || ({
        page: pageName(), catalog: 'Tests', paper: box.paper_label || `Paper ${box.paper || ''}`.trim(), word: box.word || '',
        sitting: box.sitting ? [sittingName(box.sitting), box.sitting.date && day(box.sitting.date)].filter(Boolean).join(' · ') : '' }[ctx.kind] || '');
      title.addEventListener('input', () => { draft.title = title.value; saveDraft(); });
      const titleSec = h('div', { class: 'rp-sec' }, h('label', { class: 'label', for: 'rp-title', text: 'Summary' }), title);
      if (UI.counter) UI.counter(title, 200);

      /* which answer do you get? (key_wrong: A-D chips, or the grid-in field) */
      const ansSec = h('div', { class: 'rp-sec', hidden: true });
      let answer = draft.answer || '';
      const mc = box.fmt !== 'spr';
      if (mc) {
        ansSec.append(h('p', { class: 'label', id: 'rp-ans', text: 'Which answer do you get?' }));
        const ac = UI.chips(ansSec, ['A', 'B', 'C', 'D'], { value: answer || (box.marked === 'wrong' ? box.given : null) || null, className: 'rp-ans',
          label: 'Which answer do you get?', onChange: v => { answer = v; draft.answer = v; saveDraft(); } });
        answer = ac.value || '';
      } else {
        const f = h('input', { class: 'field', id: 'rp-ans', inputmode: 'decimal', maxlength: '8', autocomplete: 'off', spellcheck: 'false',
          placeholder: (UI.spr && UI.spr.PLACEHOLDER) || 'e.g. 2/3, −1.5, 12' });
        const pvEl = h('div', { class: 'rp-pv', 'aria-live': 'polite' });
        f.value = answer || (box.marked === 'wrong' ? box.given || '' : '');
        const paint = () => {
          answer = f.value.trim();
          draft.answer = answer; saveDraft();
          if (UI.spr && UI.spr.preview) UI.spr.preview(pvEl, f.value);
          else pvEl.textContent = answer ? `Answer preview: ${answer.replace(/-/g, '−')}` : '';
        };
        f.addEventListener('input', paint);
        ansSec.append(h('label', { class: 'label', for: 'rp-ans', text: 'Which answer do you get?' }), f, pvEl);
        paint();
      }

      /* details */
      const details = h('textarea', { class: 'field', id: 'rp-details', rows: '4', maxlength: '5000', placeholder: 'What happened? What did you expect?' });
      details.value = draft.details || '';
      details.addEventListener('input', () => { draft.details = details.value; saveDraft(); });
      const req = h('span', { class: 'rp-req', hidden: true, text: ' (required)' });
      const detailSec = h('div', { class: 'rp-sec' }, h('label', { class: 'label', for: 'rp-details' }, 'Details', req), details);
      if (UI.counter) UI.counter(details, 5000);

      /* files: behind "Add files" for a question, which we can regenerate exactly */
      const files = fileBox(items, { onRecord: startRecording });
      const fileSec = h('div', { class: 'rp-sec rp-drop' });
      if (isQ && !items.length) {
        const open = h('button', { type: 'button', class: 'quiet', 'aria-expanded': 'false', onclick: () => {
          open.remove(); fileSec.append(files.el); files.el.querySelector('button').focus();
        } }, 'Add files');
        fileSec.append(open);
      } else fileSec.append(h('p', { class: 'label', text: 'Images and recordings' }), files.el);

      /* reply to */
      const email = h('input', { class: 'field', id: 'rp-email', type: 'email', autocomplete: 'email', maxlength: '200', placeholder: 'you@example.com' });
      email.value = draft.email !== undefined ? draft.email : pv.email || '';
      email.addEventListener('input', () => { draft.email = email.value; saveDraft(); });
      const emailSec = h('div', { class: 'rp-sec' }, h('label', { class: 'label', for: 'rp-email' }, 'Reply to ', h('span', { class: 'rp-req', text: '(optional)' })),
        email, h('p', { class: 'help', text: 'Replies also appear under Settings › Your reports.' }));

      const fail = h('p', { class: 'field-err rp-err', role: 'alert', hidden: true });

      // X10: under the live row, the one-tap chips come first
      if (live) body.append(chipSec, boxSec, titleSec, detailSec, fileSec, emailSec, fail);
      else body.append(boxSec, metooSec, titleSec, chipSec, ansSec, detailSec, fileSec, emailSec, fail);

      function shape() {
        ansSec.hidden = category !== 'key_wrong';
        req.hidden = !(pv.needs_details || []).includes(category);
        if (category === 'suggest' && !details.value && ctx.meaning) { details.value = ctx.meaning; draft.details = details.value; saveDraft(); }
        if (category === 'label' && !answer && ctx.option) answer = ctx.option;
      }
      shape();

      // paste and drop, anywhere in the sheet
      s.el.addEventListener('paste', e => {
        const fs = [...((e.clipboardData && e.clipboardData.files) || [])];
        if (!fs.length) return;
        e.preventDefault();
        if (!files.el.isConnected) { fileSec.replaceChildren(h('p', { class: 'label', text: 'Images and recordings' }), files.el); }
        files.add(fs);
      });
      s.el.addEventListener('dragover', e => { if ([...e.dataTransfer.items].some(i => i.kind === 'file')) { e.preventDefault(); fileSec.classList.add('drag'); } });
      s.el.addEventListener('dragleave', e => { if (!s.el.contains(e.relatedTarget)) fileSec.classList.remove('drag'); });
      s.el.addEventListener('drop', e => {
        if (!e.dataTransfer.files.length) return;
        e.preventDefault(); fileSec.classList.remove('drag');
        if (!files.el.isConnected) { fileSec.replaceChildren(h('p', { class: 'label', text: 'Images and recordings' }), files.el); }
        files.add(e.dataTransfer.files);
      });
      s.el.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && sendBtn.isConnected) { e.preventDefault(); sendBtn.click(); } });

      async function startRecording() {
        const ok = await record(file => {
          if (file) items.push({ file, name: file.name, size: file.size, type: file.type, url: URL.createObjectURL(file),
            err: file.size > CAP[file.type] ? `This video is ${bytes(file.size)}. The limit is ${bytes(CAP[file.type])}.` : null });
          report(ctx0);                        // back, with the draft and every file
        });
        if (ok) s.close();
      }

      const sendBtn = h('button', { type: 'button', class: live ? 'btn sm' : 'pill sm', onclick: () => send() }, 'Send');
      setFoot(quiet('Cancel', () => s.close()), sendBtn);

      async function send(extra = {}) {
        fail.hidden = true;
        const cat = extra.category || category;
        if (!cat) { fail.textContent = 'Pick what’s wrong.'; fail.hidden = false; (chips.el.querySelector('[tabindex="0"]') || chips.el).focus(); return; }
        if (!extra.parent && (pv.needs_details || []).includes(cat) && !details.value.trim()) {
          fail.textContent = 'Say what happened in the details.'; fail.hidden = false; details.focus(); return;
        }
        if (!extra.parent && cat === 'key_wrong' && !answer) {
          fail.textContent = 'Which answer do you get?'; fail.hidden = false; (ansSec.querySelector('input, [tabindex="0"]') || ansSec).focus(); return;
        }
        const mail = email.value.trim();
        if (mail && !email.checkValidity()) { fail.textContent = 'That email doesn’t look right.'; fail.hidden = false; email.focus(); return; }
        const data = { ...wire(ctx), category: cat, title: title.value.trim().slice(0, 200), details: details.value.slice(0, 5000),
          answer: (cat === 'key_wrong' || cat === 'label') && answer ? String(answer).slice(0, 40) : null,
          email: mail || null, include_answer: include ? include.checked : false, parent: extra.parent || null,
          device: withDev.checked ? await device() : null };
        const btns = [...foot.querySelectorAll('button'), ...metooSec.querySelectorAll('button')];
        btns.forEach(b => { b.disabled = true; });
        sendBtn.setAttribute('aria-busy', 'true');
        let res;
        try { res = await postReport(data, files.files()); }
        catch (e) {
          btns.forEach(b => { b.disabled = false; });
          sendBtn.removeAttribute('aria-busy');
          if ((e.status === 413 || e.status === 415) && e.detail && typeof e.detail === 'object') {
            files.refuse(e.detail.file, e.status === 415 ? 'The server says this isn’t an image or a video.'
              : `This file is over the limit of ${bytes(e.detail.limit || 0)}.`);
            if (!files.el.isConnected) fileSec.replaceChildren(files.el);
          }
          fail.textContent = errText(e);
          fail.hidden = false;
          if (e.status === 0) sendBtn.textContent = 'Retry';
          return;
        }
        store.set(key, null);
        items.splice(0).forEach(x => x.url && URL.revokeObjectURL(x.url));
        KEPT.delete(key);
        reported(ctx, res, opener);
        after(res, { parent: extra.parent, live });
      }
      const first = live ? body.querySelector('.rp-live .pill') : chips.el.querySelector('[tabindex="0"]');
      if (first) first.focus({ preventScroll: true });
    }

    /* ---------- after sending: the check (U3), or thanks */
    function thanks(res, extra = {}) {
      const p = h('p', { class: 'rp-out rp-thanks' });
      if (extra.parent) p.append(`Thanks. You’re added to report #${extra.parent}. `);
      else p.append(`Thanks. Report #${res.id} is in. `);
      p.append('You’ll see our answer under ', h('a', { href: '/me/settings/#reports' }, 'Settings › Your reports'),
        ', and fixes are listed at ', h('a', { href: '/help/#fixed' }, 'Help › Fixed from your reports'), '.');
      const out = [p];
      if (extra.live) out.push(h('p', { class: 'help', text: 'Nothing is checked until you hand in. The clock kept running.' }));
      if (extra.disputed) out.push(h('p', { class: 'help', text: 'It doesn’t count against you while it’s checked.' }));
      s.body.replaceChildren(...out);
      setFoot(closeBtn());
      foot.querySelector('button').focus({ preventScroll: true });
    }

    function after(res, extra) {
      const c = res.check;
      if (!c) return thanks(res, { ...extra, disputed: res.disputed });
      s.setTitle && s.setTitle(c.outcome === 'broken' ? 'You found a broken question' : c.outcome === 'remarked' ? 'You were right' : 'We checked it');
      const out = [h('p', { class: 'rp-out', text: c.text })];
      const acts = c.actions || [];
      if (c.rationale && acts.length) out.push(h('p', { class: 'k', text: 'How it works' }), h('p', { class: 'rp-why', text: c.rationale }));
      if (!acts.length) {
        out.push(h('p', { class: 'help' }, `Report #${res.id}. Our answer lands under `, h('a', { class: 'link', href: '/me/settings/#reports' }, 'Settings › Your reports'), '.'));
        s.body.replaceChildren(...out);
        setFoot(closeBtn());
        foot.querySelector('button').focus({ preventScroll: true });
        return;
      }
      const box = h('div', { class: 'rp-acts' });
      const sense = h('button', { type: 'button', class: 'pill sm', onclick: async () => {
        sense.setAttribute('aria-busy', 'true');
        try {
          await call(`/reports/${res.id}/accept`, { method: 'POST' });
          s.body.replaceChildren(h('p', { class: 'rp-out', text: `Thanks. Report #${res.id} is closed: Checked, no change. It used none of your dispute slots.` }));
          setFoot(closeBtn());
          foot.querySelector('button').focus({ preventScroll: true });
        } catch (e) { sense.removeAttribute('aria-busy'); err.textContent = errText(e); err.hidden = false; }
      } }, 'That makes sense');
      const wording = h('button', { type: 'button', class: 'btn sm', onclick: () => escalate(res, 'wording') }, 'The wording or figure is wrong');
      const person = h('button', { type: 'button', class: 'btn sm', onclick: () => escalate(res, 'person') }, 'Still wrong: send to a person');
      const err = h('p', { class: 'field-err rp-err', role: 'alert', hidden: true });
      box.append(sense, wording, person);
      out.push(box, err);
      s.body.replaceChildren(...out);
      setFoot(quiet('Close', () => s.close()));
      sense.focus({ preventScroll: true });
    }

    // the two "send it to a person" steps, with the check attached on the server
    function escalate(res, how) {
      const out = [];
      let cat = how === 'person' ? 'key_wrong' : null;
      let hold = null;
      if (how === 'wording') {
        s.setTitle && s.setTitle('Send it to a person');
        const sec = h('div', { class: 'rp-sec' }, h('p', { class: 'label', text: 'What’s wrong with it?' }));
        UI.chips(sec, [{ value: 'wording', label: 'Unclear wording' }, { value: 'figure', label: 'Figure or table wrong' },
                       { value: 'explanation', label: 'Explanation unclear' }], { value: null, label: 'What’s wrong with it?', onChange: v => { cat = v; } });
        out.push(sec);
      } else {
        s.setTitle && s.setTitle('Send it to a person');
        const full = (pv.open_disputes || 0) >= ((pv.limits && pv.limits.disputes) || 5);
        hold = h('input', { type: 'checkbox', checked: !full, disabled: full });
        out.push(h('div', { class: 'rp-sec' }, h('label', { class: 'check' }, hold, 'Don’t count this question against me while it’s checked'),
          full ? h('p', { class: 'help', text: `You have ${(pv.limits && pv.limits.disputes) || 5} answers waiting to be checked.` })
               : h('p', { class: 'help', text: 'Mastery and accuracy leave it out until a person answers. A test or challenge score never changes this way.' })));
      }
      const more = h('textarea', { class: 'field', id: 'rp-more', rows: '3', maxlength: '5000',
        placeholder: how === 'person' ? 'Why is your answer right? Your working helps.' : 'What’s wrong with the wording, the figure or the explanation?' });
      out.push(h('div', { class: 'rp-sec' }, h('label', { class: 'label', for: 'rp-more' }, 'Details ', h('span', { class: 'rp-req', text: '(optional)' })), more));
      const err = h('p', { class: 'field-err rp-err', role: 'alert', hidden: true });
      out.push(err);
      s.body.replaceChildren(...out);
      const go = h('button', { type: 'button', class: 'pill sm', onclick: async () => {
        if (!cat) { err.textContent = 'Pick what’s wrong.'; err.hidden = false; return; }
        go.setAttribute('aria-busy', 'true');
        try {
          const r = await call(`/reports/${res.id}/escalate`, { method: 'POST',
            body: { category: cat, dispute: !!(hold && hold.checked && !hold.disabled), details: more.value.trim() || null } });
          if (r && r.dispute) pv.open_disputes = (pv.open_disputes || 0) + 1;
          thanks(res, { disputed: !!(r && r.dispute) });
        } catch (e) { go.removeAttribute('aria-busy'); err.textContent = errText(e); err.hidden = false; }
      } }, 'Send to a person');
      setFoot(quiet('Back', () => after(res, {})), go);
      (s.body.querySelector('[tabindex="0"], input:not(:disabled), textarea') || go).focus({ preventScroll: true });
    }

    load();
    return s;
  }

  /* ------------------------------------------------------------ no dialog (W18) */
  report.send = async (ctx0, f = {}) => {
    const ctx = { ...(ctx0 || {}) };
    ctx.kind = kindOf(ctx);
    const res = await postReport({ ...wire(ctx), category: f.category || ctx.category, title: (f.title || '').slice(0, 200),
      details: (f.details || '').slice(0, 5000), answer: f.answer ? String(f.answer).slice(0, 40) : null, device: await device() }, []);
    reported(ctx, res, null);
    if (!f.quiet) toast(`Sent. Report #${res.id}`, { href: '/me/settings/#reports', action: 'Your reports' });
    return res;
  };
  report.sent = ctx => SENT.get(qKey({ ...ctx })) || null;
  report.trail = () => TRAIL.map(x => ({ ...x }));
  UI.report = report;

  /* ?feedback on any URL opens Send feedback (Shell 2.10) */
  if (/[?&]feedback(=|&|$)/.test(location.search)) {
    const u = new URL(location.href);
    u.searchParams.delete('feedback');
    try { history.replaceState(history.state, '', u); } catch (_) {}
    const go = () => { if (UI.sheet && UI.chips) report(); };
    if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', go, { once: true }); else setTimeout(go);
  }
})();
