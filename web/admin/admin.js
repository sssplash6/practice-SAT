/* Admin helpers shared by the students board, the student page and Access: the token (asked once, kept for this
   tab, sent as X-Admin) and a few formatters. */
window.AD = (() => {
  'use strict';
  const KEY = 'satf.admin';
  function h(tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
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
  const tok = {
    get() { try { return sessionStorage.getItem(KEY) || ''; } catch (_) { return ''; } },
    set(v) { try { if (v) sessionStorage.setItem(KEY, v); else sessionStorage.removeItem(KEY); } catch (_) {} },
  };
  class Gate extends Error {}
  async function api(path, body) {
    const r = await fetch('/api/admin' + path, body === undefined ? { headers: { 'X-Admin': tok.get() } }
      : { method: 'POST', headers: { 'X-Admin': tok.get(), 'content-type': 'application/json' }, body: JSON.stringify(body) });
    if (r.status === 403) { tok.set(''); throw new Gate('That token is not right.'); }
    if (r.status === 404 && !/\/students\//.test(path)) throw new Gate('The admin panel is off: set SATF_ADMIN_TOKEN on the server.');
    if (!r.ok) throw new Error(r.status === 404 ? 'No such student.' : `HTTP ${r.status}`);
    return r.json();
  }
  // asks for the token, then runs go(); gate errors send you back to the token box
  function boot(root, title, go) {
    const ask = msg => {
      const f = h('input', { class: 'field', type: 'password', autocomplete: 'current-password', 'aria-label': 'Admin token', placeholder: 'Admin token' });
      const err = h('p', { class: 'field-err', role: 'alert', hidden: !msg, text: msg || '' });
      const open = () => { if (f.value.trim()) { tok.set(f.value.trim()); run(); } };
      f.addEventListener('keydown', e => { if (e.key === 'Enter') open(); });
      root.replaceChildren(h('h1', { class: 'h1', text: title }), h('div', { class: 'adm-gate' }, h('label', { class: 'label', text: 'Admin token' }),
        h('div', { class: 'adm-row' }, f, h('button', { type: 'button', class: 'pill sm', text: 'Open', onclick: open })), err,
        h('p', { class: 'help', text: 'It is the SATF_ADMIN_TOKEN on the server. Kept for this tab only.' })));
      f.focus();
    };
    const run = async () => {
      if (!tok.get()) { ask(); return; }
      root.replaceChildren(h('p', { class: 'help', text: 'Loading…' }));
      try { await go(); } catch (e) { if (e instanceof Gate) ask(e.message); else root.replaceChildren(h('p', { class: 'field-err', text: e.message }), h('button', { class: 'btn sm', type: 'button', text: 'Try again', onclick: run })); }
    };
    run();
  }
  const num = n => (n === null || n === undefined ? '-' : Number(n).toLocaleString('en-US'));
  const pct = x => (x === null || x === undefined ? '-' : `${Math.round(x * 100)}%`);
  const dur = m => (m === null || m === undefined ? '-' : m >= 60 ? `${Math.floor(m / 60)} h ${m % 60} min` : `${m} min`);
  const day = s => (s ? new Date(s).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '-');
  const ago = s => {
    if (!s) return 'never';
    const d = (Date.now() - new Date(s).getTime()) / 864e5;
    return d < 1 / 24 ? 'just now' : d < 1 ? `${Math.round(d * 24)} h ago` : d < 2 ? 'yesterday' : d < 30 ? `${Math.round(d)} days ago` : day(s);
  };
  const tone = x => (x === null || x === undefined ? '' : x >= 0.7 ? 'good' : x >= 0.45 ? 'mid' : 'low');
  // a sitting's integrity in a few words: what the teacher looks for first (Tests page, the student page)
  const mmss = ms => { const t = Math.round((ms || 0) / 1000); return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`; };
  const integrity = ig => {
    if (!ig) return '-';
    const bits = [];
    if (ig.left_n) bits.push(`left ${ig.left_n}× · ${mmss(ig.left_ms)}`);
    if (ig.copy_n) bits.push(`copy ${ig.copy_n}`);
    if (ig.paste_n) bits.push(`paste ${ig.paste_n}`);
    if (ig.fs_n) bits.push(`fullscreen off ${ig.fs_n}`);
    return bits.length ? bits.join(' · ') : 'Clean';
  };
  return { h, api, boot, num, pct, dur, day, ago, tone, tok, mmss, integrity };
})();
