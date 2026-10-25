/* ============================================================================
   SAT Freshman -- the walk (/review/walk/?id=<drill id>): review.md V2.

   Each miss runs up to four steps in UI.review mode 'walk' (F3): Try again (only while its
   key was never shown), What happened?, The trap, Prove it (new numbers, or another passage for R&W). The walk drill's
   cfg.walk {items, i, step} is the position; every move posts /api/review/walk/{id}/at, so a
   reload or another device comes back to the same mistake and step.

   Also opens from ?session=<sid> | ?ids=<trap ids> | ?new=1 (it creates the walk first).
   Reads the walk from GET /api/review/walk/{id} (or cfg.walk on GET /api/drill/{id});
   until the server offers either, it says so and points to the Redo tab.
   ========================================================================== */
(() => {
  'use strict';
  const doc = document;
  const h = UI.h;
  // the back link's caret is drawn (UI.ICON), not a text glyph
  const backEl = document.querySelector('.rw-back');
  if (backEl && UI.icon) backEl.prepend(UI.icon('caret_left', 16));
  const $ = id => doc.getElementById(id);
  const enc = encodeURIComponent;
  const Q = new URLSearchParams(location.search);
  const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : '');
  const plural = (n, one, many) => `${n} ${n === 1 ? one : (many || one + 's')}`;
  const toast = t => UI.toast && UI.toast(t);
  const reasonOf = e => {
    const d = e && e.detail;
    const r = (d && typeof d === 'object' && (d.reason || d.message)) || (typeof d === 'string' ? d : null);
    return r ? cap(String(r)) : 'That didn’t work. Try again.';
  };
  const STEP = { try: 1, why: 2, key: 3, prove: 4, done: 4 };
  const NAME = [null, 'try', 'why', 'key', 'prove'];
  const BLANK = [['clock', 'Ran out of time'], ['gap', 'Didn’t know how to start'], ['skipped', 'Skipped it to come back and never did']];
  const GENERAL = [['misread', 'Misread the question'], ['slip', 'A slip: I knew how'], ['gap', 'Didn’t know how to start']];
  const FILLER = 'A near-miss number, not a named mistake';
  // progress.norm on the client: numbers fold to #, so an option's label names the same trap
  const norm = t => String(t || '').toLowerCase().replace(/[-−]?\d[\d.,/]*/g, '#').split(/\s+/).filter(Boolean).join(' ');
  const box = $('walk');
  let sid = Q.get('id'), entries = [], items = [], pos = { i: 0, step: 1 }, summary = null, prefs = {};
  // a walk is one subject: the link's (or the one last picked) until the walk's own questions say which
  let subject = UI.subject.get();
  const redoHref = () => `/review/?tab=redo&subject=${subject}`;
  if (backEl) backEl.href = redoHref();

  const btn = (text, cls, onclick) => h('button', { type: 'button', class: cls, text, onclick });
  const link = (text, href, cls = 'btn') => h('a', { class: cls, href, text });
  const toReview = () => link('Back to Review', redoHref(), 'btn');
  function card(title, sub, acts, extra) {
    box.removeAttribute('aria-busy');
    box.replaceChildren(h('div', { class: 'card rw-card' }, h('p', { class: 't', text: title }), sub ? h('p', { class: 's', text: sub }) : null, extra || null,
      h('div', { class: 'rw-acts' }, ...acts.filter(Boolean))));
  }
  function fail(retry, text) {
    box.removeAttribute('aria-busy');
    box.replaceChildren();
    UI.cardError(box, retry, text);
  }

  /* ------------------------------------------------------------ create, read */
  async function create() {
    const s = Q.get('session'), ids = Q.get('ids');
    // a sitting and trap ids name their subject (the server reads it from them); new misses are the subject's
    const body = s ? { session: s } : ids ? { ids: ids.split(',').map(Number).filter(n => n > 0) } : { new: true, subject };
    if (body.new) {                                          // nothing new: say so without asking for a walk
      const c = await UI.api(`/review/counts?subject=${subject}`, { quiet: true }).catch(() => null);
      if (c && !c.new) { nothing(); return false; }
    }
    try {
      const d = await UI.api('/review/walk', { method: 'POST', body });
      sid = d.id;
      history.replaceState(null, '', `/review/walk/?id=${enc(sid)}`);
      return true;
    } catch (e) {
      // only "no missed questions" is nothing to walk; another 409 (a test not handed in yet) says what it is
      const why = String((e.detail && e.detail.reason) || e.detail || '');
      if (e.status === 409 && !e.offline && /no missed/i.test(why)) {
        if (s) card('No misses in this sitting.', null, [link('See its report', `/results/report/?id=${enc(s)}`, 'pill'), toReview()]);
        else nothing();
      } else if (e.status === 409 && !e.offline && /after the test/i.test(why)) {
        card('This test isn’t handed in yet.', 'Its misses can be walked once it’s finished.', [toReview()]);
      } else fail(boot, reasonOf(e));
      return false;
    }
  }
  const nothing = () => card('Nothing to walk right now.', 'New misses from a test or an end-of-set review wait here until you walk them.', [toReview()]);
  async function readWalk() {
    try {
      const d = await UI.api(`/review/walk/${enc(sid)}`, { quiet: true });
      if (d && Array.isArray(d.items)) return d;
    } catch (e) { if (e.status !== 404 && e.status !== 405) throw e; }
    const d = await UI.api(`/drill/${enc(sid)}`, { quiet: true });
    const w = (d.cfg && d.cfg.walk) || d.walk;
    return w && Array.isArray(w.items) ? w : null;
  }

  /* ------------------------------------------------------------ one walk item */
  function choices(d, e, a) {
    if (e.blank) return BLANK.map(([id, text]) => ({ id, text }));
    if ((d.diag_choices || []).length) return d.diag_choices;
    const seen = new Set(), out = [];
    (d.reasons || []).forEach(t => {
      if (!t || t === FILLER) return;
      const id = norm(t);
      if (!seen.has(id)) { seen.add(id); out.push({ id, text: t }); }
    });
    GENERAL.forEach(([id, text]) => out.push({ id, text }));
    let s = (a && a.id) || 7;                          // shuffled the same way on every load
    for (let i = out.length - 1; i > 0; i--) { s = (s * 9301 + 49297) % 233280; const j = Math.floor((s / 233280) * (i + 1)); [out[i], out[j]] = [out[j], out[i]]; }
    return out.slice(0, 6);
  }
  async function build(i) {
    const e = entries[i];
    const d = await UI.api(`/review/item?template=${enc(e.template)}&seed=${enc(e.seed)}`, { quiet: true });
    const a = e.attempt ? (d.attempts || []).find(x => x.id === e.attempt) : null;
    if (a) d.attempts = [a, ...d.attempts.filter(x => x !== a)];
    const it = window.ReviewItem.toItem(d, { template: e.template, seed: e.seed, norm: a ? a.norm : null }, 'walk', null);
    Object.assign(it, {
      n: i + 1, try: !!e.try, blank: !!e.blank, attempt_id: e.attempt || null,
      revealed: e.blank ? true : !!(a && a.revealed), diag_choices: choices(d, e, a),
    });
    if (e.blank) it.status = 'unanswered';
    else if (!it.mistake) it.status = 'fixed';           // closed since by a correct answer elsewhere: "Incorrect · fixed since"
    items[i] = it;
    return it;
  }

  /* ------------------------------------------------------------ the player */
  const on = {
    load: i => build(i),
    at: (i, step, diag) => {
      const e = entries[i];
      if (!e) return;
      pos = { i, step };
      const body = Object.assign({ i, step: NAME[step] || 'why' }, diag && e.blank ? { diag } : {});
      UI.api(`/review/walk/${enc(sid)}/at`, { method: 'POST', body, quiet: true }).catch(() => {});
    },
    why: async (it, b) => {
      if (it.blank || !it.attempt_id) return { called: false };
      const d = await UI.api('/review/why', { method: 'POST', body: Object.assign({ attempt_id: it.attempt_id }, b) });
      return { called: !!d.called, label: d.label, cause: d.cause };
    },
    seen: it => {
      if (!it || !it.attempt_id || it._seenSent) return;
      it._seenSent = true;
      UI.api('/review/seen', { method: 'POST', body: { attempt_id: it.attempt_id }, quiet: true }).catch(() => {});
    },
    // Try again files through a one-question drill; progress.record makes it a repeat, so it never counts
    walkAnswer: async (it, answer) => {
      const d = await UI.api('/drill', { method: 'POST', body: { list: 'items', ids: [[it.q.template, it.q.seed]], exact: true, count: 1, source: 'review' } });
      const q = d.question || (await UI.api(`/drill/${enc(d.id)}`)).question;
      if (!q) return null;
      const r = await UI.api(`/drill/${enc(d.id)}/answer`, { method: 'POST', body: { question_id: q.id, answer } });
      return r.feedback || r;
    },
    rule: (it, text) => UI.api('/notes', { method: 'POST', body: { attempt_id: it.attempt_id, scope: 'type', note: text || '' } }),
    save: (it, v) => UI.api('/saved', { method: 'POST', body: { template: it.q.template, seed: it.q.seed, on: v } }),
    again: open => again(open),
    done: s => {
      summary = s;
      UI.api(`/review/walk/${enc(sid)}/at`, { method: 'POST', body: { i: entries.length - 1, step: 'done' }, quiet: true }).catch(() => {});
    },
    close: () => paused(),
  };
  // Prove it: a fresh question of the same type at the tier of the miss, with the same trap on offer
  function proveBody(it) {
    const q = it.q || {};
    const n = it.norm && !String(it.norm).startsWith('~') ? it.norm : null;
    return Object.assign({ templates: [q.template], count: 1, source: 'review' },
      q.difficulty ? { tiers: [q.difficulty] } : {},
      n ? { want: { [q.template]: `^${String(n).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$` } } : {});
  }
  function play(at, step) {
    box.removeAttribute('aria-busy');
    box.replaceChildren();
    summary = null;
    UI.review(null, items.map((x, i) => x || { n: i + 1, blank: !!entries[i].blank, try: !!entries[i].try, status: entries[i].blank ? 'unanswered' : 'incorrect' }), {
      mode: 'walk', at, step, title: 'Walk your misses', owner: true, prefs, proveBody, on,
    });
  }
  function paused() {
    const n = entries.length;
    if (summary) {
      const s = summary;
      const named = s.n - s.blanks;
      // the hero: how many you named, at the hero size; the rest of the walk in one line under it
      const line = [`${s.n} reviewed`, `${s.proven} proven on ${subject === 'rw' ? 'another one' : 'new numbers'}`, s.open ? `${s.open} still open` : null, s.blanks ? plural(s.blanks, 'blank') : null].filter(Boolean).join(' · ');
      card('Walk done', named ? null : line, [link('Back to Review', redoHref(), 'pill')],   // Walk the n still open is on the end card
        named ? h('div', { class: 'rw-done' }, h('p', { class: 'hero-num' }, h('span', { text: '0' }), h('small', { text: `of ${named} named` })), h('p', { class: 's', text: line })) : null);
      box.firstChild.classList.add('hero');
      const fig = box.querySelector('.hero-num > span');
      if (fig && UI.roll) UI.roll(fig, s.named);   // the walk just ended: the figure rolls up from 0 once
      return;
    }
    const dots = h('div', { class: 'rw-dots', 'aria-hidden': 'true' });
    entries.forEach((_, i) => dots.append(h('i', { 'data-on': i === pos.i ? '' : null, 'data-done': i < pos.i ? '' : null })));
    card(`Mistake ${pos.i + 1} of ${n}`, `Step ${pos.step} of 4`,
      [btn('Resume the walk', 'pill', () => play(pos.i, pos.step)), toReview()], dots);
    box.firstChild.classList.add('hero');
  }
  async function again(open) {
    const ids = [...new Set(open.map(x => x.trap_id).filter(Boolean))];
    if (!ids.length) { toast('Nothing left to walk.'); return; }
    try {
      const d = await UI.api('/review/walk', { method: 'POST', body: { ids } });
      location.href = `/review/walk/?id=${enc(d.id)}`;
    } catch (e) { toast(reasonOf(e)); }
  }

  /* ------------------------------------------------------------ boot */
  async function boot() {
    box.setAttribute('aria-busy', 'true');
    box.replaceChildren();
    if (UI.skel) UI.skel(box, 'card');
    if (!sid && !(await create())) return;
    let w;
    try { w = await readWalk(); } catch (e) {
      if (e.status === 404 || e.status === 403) card('This walk isn’t on this device’s account.', 'Start one from Review.', [toReview()]);
      else fail(boot, 'The walk didn’t load.');
      return;
    }
    if (!w || !w.items.length) {
      card('This walk can’t be opened yet.', 'The same steps run in Review’s pane: open a new miss there.', [link('Open new misses', `${redoHref()}&lens=new`, 'pill'), toReview()]);
      return;
    }
    entries = w.items;
    subject = UI.subjectOf(entries[0].template);   // the walk's questions are one subject: Review opens on it
    if (backEl) backEl.href = redoHref();
    if (w.step === 'done') { card('Walk done', 'What’s still open waits in Review’s Redo tab.', [link('Back to Review', redoHref(), 'pill')]); return; }
    items = new Array(entries.length).fill(null);
    const blanks = entries.filter(e => e.blank).length, misses = entries.length - blanks;
    $('sub').textContent = [misses ? plural(misses, 'miss', 'misses') : null, blanks ? `${blanks} not answered` : null, `about ${Math.max(1, Math.round(entries.length * 1.5))} min`].filter(Boolean).join(' · ');
    const at = Math.min(Math.max(0, w.i || 0), entries.length - 1);
    pos = { i: at, step: STEP[w.step] || (entries[at].try && !entries[at].blank ? 1 : 2) };
    try { prefs = (await UI.prefs()) || {}; } catch (_) { prefs = {}; }
    try { await build(at); } catch (_) { fail(boot, 'This question didn’t load.'); return; }
    play(at, pos.step);
  }
  boot();
})();
