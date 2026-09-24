/* ============================================================================
   SAT Freshman -- the quick sheet (spec/rebuild-v2.md Shell 2.7, R29 and acceptance 12
   and 13; shell-me.md U1 and U2 with override 11, U26; product.md G4; words.md W19)

   Loaded by ui.js on first use (UI.quick is a stub until then). Q, the bolt in the sidebar
   and the phone bar, the menu sheet's Quick, and the palette open it. Never on the practice
   session or the test window, which have no shell. Built from kit's UI.sheet, UI.seg and
   UI.chips; the question is F3's UI.workspace (inline) when question.js is on the site,
   else ui.js's UI.question.

     UI.quick(tab?) -> {el, tab(name), close}     tab: question | mistake | word; the last
                                    one used is kept in localStorage satf.quick.tab
   Quick question: POST /api/drill {source: 'quick', count: null}, the skill and a live tally,
     a Got time? row of time boxes, the verdict with Save and Report, Another (Enter or N),
     and Practise {skill}. Closing, or leaving the page, finishes the sitting (keepalive);
     with no answers that deletes it. After an answer, closing offers Up next.
   Log a mistake (U2): One question: a College Board ID, pasted text or a few words find the
     question type (GET /api/types/match, POST /api/types/match, or the local index), each
     with a generated example; or Pick by skill instead. Then which answer, what went wrong,
     where, and Add to my mistakes (POST /api/mistakes/log), with the fix path in place: the
     trap in an example, Try one now, Practise 3. A whole test: two 22-cell grids; each missed
     cell takes a skill, then Build my follow-up.
   Add a word: hands the word or a pasted text to S9's UI.addWord (words-ui.js).
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI;
  const doc = document;
  const h = UI.h;
  const TAB_KEY = 'satf.quick.tab';
  const lget = (k, d) => { try { const v = JSON.parse(localStorage.getItem(k) || 'null'); return v === null ? d : v; } catch (_) { return d; } };
  const lput = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} };
  const fmt = n => Number(n || 0).toLocaleString('en-US');
  const plural = (n, one, many = one + 's') => `${fmt(n)} ${n === 1 ? one : many}`;
  const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
  const icon = (name, size = 18) => { const t = doc.createElement('template'); t.innerHTML = UI.svg(UI.ICON[name] || '', size); return t.content.firstElementChild; };
  const prefs = () => UI.prefs.now() || {};
  const setLength = () => { const n = prefs().set_length; return n === 0 ? null : (n || 10); };
  const short = slug => (UI.TOPIC[slug] || {}).short || slug;
  const words = s => String(s || '').toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter(Boolean);
  const btn = (label, o = {}) => {
    const b = h(o.href ? 'a' : 'button', { class: o.cls || 'btn sm', type: o.href ? null : 'button', href: o.href || null,
      'aria-pressed': o.pressed === undefined ? null : String(!!o.pressed) }, o.icon ? icon(o.icon) : null, label, o.kbd ? UI.keys.caps(o.kbd) : null);
    if (o.onClick) b.addEventListener('click', o.onClick);
    return b;
  };
  const busy = async (b, fn) => {
    if (b.getAttribute('aria-busy') === 'true') return;
    b.setAttribute('aria-busy', 'true');
    try { return await fn(); } finally { b.removeAttribute('aria-busy'); }
  };
  const errText = e => e && e.offline ? 'Can’t reach SAT Freshman.' : 'That didn’t work. Try again.';
  async function startDrill(body) {
    const r = await UI.api('/drill', { method: 'POST', body });
    location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`;
  }

  /* F3's workspace when it is on the site; ui.js's renderer otherwise */
  let wsLoad = null;
  const workspace = () => wsLoad || (wsLoad = typeof UI.workspace === 'function' ? Promise.resolve(true)
    : UI.has('question') ? UI.need('question').then(() => typeof UI.workspace === 'function', () => false) : Promise.resolve(false));

  // a generated item, read-only: stem, figure, table and choices; with `trap`, the key and
  // the trap's option marked, with the rationale (U2's fix path)
  function example(q, o = {}) {
    const box = h('div', { class: 'quick-example', style: 'padding: 14px 16px; border-radius: 12px; background: var(--tile); margin-top: 10px' });
    const ctl = UI.question(box, q, {});
    if (q.type !== 'mcq') {
      const grid = box.querySelector('.grid-in'); if (grid) grid.remove();
      const pv = box.querySelector('.preview'); if (pv) pv.remove();
      box.append(h('p', { class: 'help', text: o.trap ? `The answer is ${String(q.answer).replace(/-/g, '−')}.` : 'A grid-in: you type the answer.' }));
    } else if (ctl.buttons) ctl.buttons.forEach(b => { b.disabled = true; });
    if (o.trap && q.type === 'mcq') {
      const ai = 'ABCD'.indexOf(q.answer);
      ctl.reveal({ correct: false, given: o.trapIndex ?? null, answer: q.answer, answer_index: ai,
        mistake: o.trapIndex !== null && o.trapIndex !== undefined ? cap((q.reasons || [])[o.trapIndex] || '') : null, rationale: q.rationale }, { open: true });
      const tb = ctl.buttons && ctl.buttons[o.trapIndex];
      // an example, not the student's answer: no "Wrong", and the trap named as the trap
      box.querySelectorAll('[role="status"]').forEach(x => { x.textContent = ''; });
      if (tb) {
        tb.querySelectorAll('.sr').forEach(x => { if (/your answer/.test(x.textContent)) x.remove(); });
        tb.append(h('span', { class: 'badge', text: 'This is the trap', style: 'margin-left: auto' }));
      }
    }
    box.querySelectorAll('.q-stem').forEach(s => { s.style.fontSize = '17px'; });
    return box;
  }

  /* ------------------------------------------------------------ Quick question */
  function questionPane(sheet) {
    const el = h('div', { class: 'quick-q' });
    const chipHost = h('span', { style: 'display: inline-flex; flex-wrap: wrap; align-items: center; gap: 6px 8px; min-height: 28px; min-width: 0' });
    const tally = h('span', { class: 'mono', style: 'font-size: 12.5px; color: var(--soft)', 'aria-live': 'polite' });
    const top = h('div', { style: 'display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 6px 12px' }, chipHost, tally);
    const boxes = UI.boxChips ? UI.boxChips(false, [5, 15, 30]) : null;
    if (boxes) boxes.style.margin = '10px 0 4px';
    const body = h('div', { style: 'margin-top: 14px' });
    const acts = h('div', { style: 'display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px', hidden: true });
    el.append(top, boxes, body, acts);
    const another = btn('Another', { cls: 'pill', kbd: 'Enter', onClick: () => next() });
    const checkSlot = h('span', { style: 'display: contents' });     // a grid-in's Check, in the bottom bar (U26)
    const practise = btn('Practise', { cls: 'quiet', onClick: e => busy(e.currentTarget, async () => {
      if (!q) return;
      await finish();
      await startDrill({ topics: [q.topic], count: setLength(), source: 'map' });
    }).catch(() => UI.toast && UI.toast('Couldn’t start it. Try again.')) });
    another.hidden = true;
    practise.hidden = true;
    let sid = null, q = null, ctrl = null, answered = 0, right = 0, t0 = 0, fb = null, finished = false, loading = false;

    const paintTally = () => { tally.textContent = answered ? `${plural(answered, 'answered', 'answered')} · ${fmt(right)} right` : ''; };
    function loadingState() {
      body.replaceChildren(UI.skel ? UI.skel(null, 'lines:3') : h('p', { class: 'help', text: 'Loading…' }));
      acts.hidden = true; another.hidden = true; checkSlot.replaceChildren();
    }
    function failed(e) {
      body.replaceChildren(h('p', { text: e && e.offline ? 'Can’t reach SAT Freshman.' : 'Couldn’t get a question.' }),
        btn('Retry', { onClick: () => (sid ? next() : start()) }));
    }
    async function start() {
      loading = true;
      loadingState();
      const p = prefs(), b = { source: 'quick', count: null };
      if (Array.isArray(p.tiers) && p.tiers.length && p.tiers.length < 3) b.tiers = p.tiers;
      if (Array.isArray(p.formats) && p.formats.length === 1) b.formats = p.formats;
      try {
        const r = await UI.api('/drill', { method: 'POST', body: b });
        sid = r.id;
        await show(r.question);
      } catch (e) { failed(e); }
      finally { loading = false; }
    }
    async function next() {
      if (loading || !sid) return;
      if (q && !fb) return;                 // the verdict first
      loading = true;
      loadingState();
      try {
        const r = await UI.api(`/drill/${encodeURIComponent(sid)}/next`, { method: 'POST' });
        if (r.done || !r.question) { body.replaceChildren(h('p', { text: 'That’s every question we have for you here right now.' })); return; }
        await show(r.question);
      } catch (e) { failed(e); }
      finally { loading = false; }
    }
    async function show(question) {
      q = question; fb = null; ctrl = null;
      const same = q.skill && words(q.skill).join(' ') === words(short(q.topic)).join(' ');
      chipHost.replaceChildren(...[UI.chip(q.topic), q.skill && !same ? h('span', { class: 'help', style: 'margin: 0', text: cap(q.skill) }) : null,
        q.repair ? h('span', { class: 'badge', text: 'Again · new numbers' }) : null].filter(Boolean));
      practise.replaceChildren(`Practise ${short(q.topic)} · ${setLength() ? fmt(setLength()) : 'endless'}`);
      practise.hidden = false;
      another.hidden = true;
      acts.hidden = true;
      body.replaceChildren();
      t0 = performance.now();
      if (await workspace()) {
        ctrl = UI.workspace(body, q, { mode: 'inline', feedback: 'instant', prefs: prefs(),
          onCheck: given => send(given) });
      } else {
        ctrl = UI.question(body, q, { onAnswer: given => { send(given).then(f => { if (f) reveal(f); }); } });
        const line = body.querySelector('.q-skill');           // the header above says it
        const check = body.querySelector('.grid-in > .pill');
        if (check) checkSlot.append(check);
        if (line) line.remove();
      }
      if (ctrl && ctrl.focus) ctrl.focus();
    }
    async function send(given) {
      const ms = Math.round(performance.now() - t0);
      try {
        const f = await UI.api(`/drill/${encodeURIComponent(sid)}/answer`, { method: 'POST', body: { question_id: q.id, answer: given, ms } });
        answered += 1;
        if (f.correct) right += 1;
        paintTally();
        fb = f;
        verdict(f);
        return f;
      } catch (e) {
        if (ctrl && ctrl.unlock) ctrl.unlock();
        if (UI.toast) UI.toast(e.offline ? 'Can’t reach SAT Freshman. Your answer wasn’t sent.' : 'Not sent. Try again.');
        return null;
      }
    }
    function reveal(f) {
      const how = prefs().rationale || 'miss';
      ctrl.reveal(f, { open: how === 'always' });
      if (how === 'tap' && !f.correct) {            // the explanation on tap, even after a miss
        const why = body.querySelector('.why');
        if (why && !why.hidden) {
          why.hidden = true;
          const tog = h('button', { type: 'button', class: 'quiet why-toggle', text: 'Why' });
          tog.addEventListener('click', () => { why.hidden = false; tog.remove(); });
          why.before(tog);
        }
      }
    }
    function verdict(f) {
      const save = btn('Save', { icon: 'bookmark', pressed: false });
      save.addEventListener('click', () => busy(save, async () => {
        const on = save.getAttribute('aria-pressed') !== 'true';
        try {
          await UI.api('/saved', { method: 'POST', body: { session: sid, question_id: q.id, on } });
          save.setAttribute('aria-pressed', String(on));
          save.lastChild.textContent = on ? 'Saved' : 'Save';
        } catch (e) { if (UI.toast) UI.toast('Not saved. Try again.'); }
      }));
      save.lastChild.replaceWith(h('span', { text: 'Save' }));
      const kids = [save];
      if (UI.has('report')) kids.push(btn('Report', { icon: 'chat', onClick: () => UI.report({ kind: 'question', source: 'quick', session: sid, question_id: q.id, revealed: true }) }));
      if (f.opened && f.opened.length) kids.push(h('span', { class: 'help', style: 'align-self: center; margin: 0', text: 'Added to your mistakes. Another brings the same trap with new numbers.' }));
      acts.replaceChildren(...kids);
      acts.hidden = false;
      checkSlot.replaceChildren();
      another.hidden = false;
      if (!doc.activeElement || doc.activeElement === doc.body || !sheet.el.contains(doc.activeElement)) another.focus({ preventScroll: true });
    }
    async function finish(keepalive = true) {
      if (!sid || finished) return;
      finished = true;
      try { await UI.api(`/drill/${encodeURIComponent(sid)}/finish`, { method: 'POST', keepalive, quiet: true }); } catch (_) {}
    }
    const keys = {
      Enter: { does: 'Another', run: () => { if (fb) { next(); return true; } return false; } },
      N: { does: 'Another', run: () => { if (fb) { next(); return true; } return false; } },
    };
    ['A', 'B', 'C', 'D'].forEach((L, i) => {
      const run = () => {
        if (!q || fb || q.type !== 'mcq' || !ctrl) return false;
        if (ctrl.select && UI.workspace) ctrl.select(i); else if (ctrl.choose) ctrl.choose(i);
        return true;
      };
      keys[L] = { does: 'Choose', run };
      keys[String(i + 1)] = { does: 'Choose', run, hidden: true };
    });
    return { el, foot: [practise, checkSlot, another], keys, start: () => { if (!sid) start(); },
      get answered() { return answered; }, get right() { return right; }, finish, get topic() { return q && q.topic; } };
  }

  /* ------------------------------------------------------------ Log a mistake (U2) */
  const ORIGINS = [
    { value: 'school', label: 'School' }, { value: 'bluebook', label: 'Bluebook' },
    { value: 'cb_qbank', label: 'College Board question bank' }, { value: 'official', label: 'Official practice' },
    { value: 'book', label: 'Book' }, { value: 'other', label: 'Other' },
  ];
  function mistakePane(sheet, close) {
    const el = h('div', { class: 'quick-m' });
    const mode = UI.seg(null, [{ value: 'one', label: 'One question' }, { value: 'test', label: 'A whole test' }],
      { value: 'one', label: 'Log one question or a whole test', onChange: v => paint(v) });
    const view = h('div', { style: 'margin-top: 16px' });
    el.append(mode.el, view);
    const add = btn('Add to my mistakes', { cls: 'pill', onClick: () => submit() });
    const build = btn('Build my follow-up', { cls: 'pill', onClick: () => follow() });
    const again = btn('Log another', { cls: 'btn', onClick: () => { reset(); paint('one'); } });
    const status = h('p', { class: 'field-err grow', role: 'alert', hidden: true });
    let st;
    const reset = () => { st = { picked: null, reason: undefined, other: '', letter: null, value: '', origin: null, note: '', reasons: null, auto: null }; };
    reset();
    let cat = null;
    UI.types().then(c => { cat = c; if (helper.isConnected) helper.textContent = coverage(); }, () => {});
    const coverage = () => {
      const cb = (cat && cat.cb) || {};
      return cb.known ? `We know ${fmt(cb.known)} of College Board’s ${fmt(cb.bank)} Math question IDs. For any other, paste the question.`
        : 'A College Board question ID, or the question pasted in, or a few words about it.';
    };
    const helper = h('p', { class: 'help' });
    const say = t => { status.textContent = t || ''; status.hidden = !t; };

    function paint(which) {
      say('');
      add.hidden = which !== 'one'; build.hidden = which !== 'test'; again.hidden = true;
      if (which === 'test') return wholeTest();
      oneQuestion();
    }

    /* ---- one question: find its type */
    let field, results;
    function oneQuestion() {
      if (st.done) return doneView(st.done);
      field = h('textarea', { class: 'field', rows: 2, id: 'qm-find', autocomplete: 'off', spellcheck: 'false',
        placeholder: 'e.g. 23c5fcce, or “a circle, the arc is 40°…”', style: 'min-height: 56px; resize: vertical' });
      helper.textContent = coverage();
      results = h('div', { style: 'margin-top: 12px' });
      const pick = btn('Pick by skill instead', { cls: 'quiet', onClick: () => picker() });
      view.replaceChildren(h('label', { class: 'label', for: 'qm-find', text: 'Question ID, or paste or describe the question' }),
        field, helper, h('div', { style: 'margin-top: 6px' }, pick), results);
      let timer = 0, seq = 0;
      field.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => find(++seq), 350); });
      field.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); clearTimeout(timer); find(++seq); } });
      const find = async n => {
        const text = field.value.trim();
        if (!text) { results.replaceChildren(); return; }
        const id = /^[0-9a-f]{8}$/i.test(text) ? text.toLowerCase() : null;
        results.replaceChildren(UI.skel ? UI.skel(null, 'rows:2') : h('p', { class: 'help', text: 'Looking…' }));
        try {
          let rows;
          if (id && UI.has('match')) rows = (await UI.api(`/types/match?id=${id}`, { quiet: true })).rows || [];
          else if (text.length > 60 && UI.has('match')) rows = (await UI.api('/types/match', { method: 'POST', body: { text: text.slice(0, 2000) }, quiet: true })).rows || [];
          else rows = local(text);
          if (n !== seq) return;
          if (id && rows.length === 1 && rows[0].via === 'none') return unknownId(id);
          cards(rows, !!id);
        } catch (e) {
          if (n !== seq) return;
          results.replaceChildren(h('p', { text: e.status === 429 ? 'That’s a lot of lookups. Try again in a while, or pick by skill.' : errText(e) }),
            btn('Pick by skill instead', { cls: 'quiet', onClick: () => picker() }));
        }
      };
    }
    // short text: the palette's index, type names and named mistakes
    function local(text) {
      if (!cat) return [];
      const toks = words(text);
      const hit = (s) => { const ws = words(s); return toks.every(t => ws.some(w => w.startsWith(t))); };
      const byName = cat.list.filter(t => hit(`${t.name} ${t.about}`)).slice(0, 5);
      const byReason = cat.list.filter(t => !byName.includes(t) && t.reasons.some(r => hit(r.label))).slice(0, 5 - Math.min(5, byName.length));
      return byName.concat(byReason).map(t => ({ template: t.template, topic: t.topic, via: 'label' }));
    }
    function unknownId(id) {
      results.replaceChildren(h('p', {}, 'We don’t have ', h('b', { class: 'mono', text: id }), ' yet. Paste the question text, or pick its skill.'),
        skillChips(slug => picker(slug)));
      field.value = '';
      field.placeholder = 'Paste the question text here';
      field.focus();
    }
    const typeOf = t => (cat && cat.list.find(y => y.template === t)) || null;
    const nameOf = t => { const x = typeOf(t); return x ? x.name : cap(String(t).split('.').pop().replace(/_/g, ' ')); };
    const aboutOf = t => { const x = typeOf(t); return x && x.about ? h('span', { class: 'help', style: 'flex-basis: 100%; margin: 0', text: x.about }) : null; };
    function cards(rows, byId) {
      if (!rows.length) {
        results.replaceChildren(h('p', { class: 'help', text: 'No close match. Try other words, or pick by skill.' }),
          btn('Pick by skill instead', { cls: 'quiet', onClick: () => picker() }));
        return;
      }
      results.replaceChildren(...rows.slice(0, 3).map(r => {
        const word = r.via === 'id' ? 'Exact' : r.via === 'text' ? (r.score >= 0.45 ? 'Close' : 'Possible') : null;
        const card = h('div', { style: 'padding: 14px 16px; border: 1px solid var(--line); border-radius: 12px; margin-bottom: 10px' });
        const exHost = h('div');
        card.append(h('div', { style: 'display: flex; flex-wrap: wrap; align-items: center; gap: 8px' },
          word ? h('span', { class: 'badge', text: word }) : null, UI.chip(r.topic), h('b', { text: nameOf(r.template), style: 'font-weight: 600' }), aboutOf(r.template)),
        exHost,
        h('div', { style: 'display: flex; gap: 8px; margin-top: 10px' },
          btn('This one', { cls: 'pill sm', onClick: () => chosen({ template: r.template, topic: r.topic, cb_id: r.via === 'id' ? r.cb_id : null, via: r.via }) })));
        loadExample(exHost, r.template);
        return card;
      }), btn('None of these', { cls: 'quiet', onClick: () => picker() }));
    }
    const examples = new Map();
    async function loadExample(host, template, o = {}) {
      host.replaceChildren(UI.skel ? UI.skel(null, 'lines:2') : '');
      const key = template + (o.want || '');
      try {
        const ex = examples.get(key) || await UI.api(`/types/${encodeURIComponent(template)}/example${o.want ? `?want=${encodeURIComponent(o.want)}` : ''}`, { quiet: true });
        examples.set(key, ex);
        host.replaceChildren(example(ex.question, o.want ? { trap: true, trapIndex: ex.trap_index } : {}));
        return ex;
      } catch (_) { host.replaceChildren(h('p', { class: 'help', text: 'No example to show.' })); return null; }
    }
    function skillChips(onPick, filter = '') {
      const wrap = h('div', { style: 'display: grid; gap: 12px; margin-top: 10px' });
      UI.DOMAINS.forEach(([dom, dshort]) => {
        const ts = UI.TOPICS.filter(t => t.domain === dom && (!filter || words(`${t.short} ${t.slug} ${(UI.ALIASES[t.slug] || []).join(' ')}`).some(w => w.startsWith(filter.toLowerCase()))));
        if (!ts.length) return;
        const row = h('div', { class: 'chips', role: 'group', 'aria-label': dshort });
        ts.forEach(t => { const b = h('button', { type: 'button' }, UI.glyph(t.slug), t.short); b.addEventListener('click', () => onPick(t.slug)); row.append(b); });
        wrap.append(h('div', {}, h('p', { class: 'k', text: dshort, style: 'margin-bottom: 6px' }), row));
      });
      if (!wrap.childNodes.length) wrap.append(h('p', { class: 'help', text: 'No skill by that name.' }));
      return wrap;
    }

    /* ---- the picker: skill, then its types (the steps "Pick by skill instead" keeps) */
    function picker(slug) {
      if (!slug) {
        const filter = h('input', { class: 'field sm', type: 'search', placeholder: 'Filter skills', 'aria-label': 'Filter skills', autocomplete: 'off' });
        const list = h('div');
        const draw = () => list.replaceChildren(skillChips(s => picker(s), filter.value.trim()));
        filter.addEventListener('input', draw);
        draw();
        view.replaceChildren(h('p', { class: 'label', text: 'Which skill?' }), filter, list,
          h('div', { style: 'margin-top: 12px' }, btn('Back to search', { cls: 'quiet', onClick: () => oneQuestion() })));
        filter.focus();
        return;
      }
      const types = (cat && cat.byTopic[slug]) || [];
      const rows = h('div', { style: 'display: grid; gap: 8px; margin-top: 8px' });
      types.forEach(t => {
        const exHost = h('div', { hidden: true });
        const show = btn('Show an example', { cls: 'quiet' });
        show.addEventListener('click', () => {
          exHost.hidden = !exHost.hidden;
          show.textContent = exHost.hidden ? 'Show an example' : 'Hide the example';
          if (!exHost.hidden && !exHost.childNodes.length) loadExample(exHost, t.template);
        });
        rows.append(h('div', { style: 'padding: 10px 12px; border: 1px solid var(--line); border-radius: 12px' },
          h('div', { style: 'display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px' },
            h('span', { style: 'font-weight: 600; min-width: 0' }, t.name, t.about ? h('span', { class: 'help', style: 'display: block; margin: 2px 0 0; font-weight: 400', text: t.about }) : null),
            h('span', { style: 'display: flex; gap: 6px' }, show,
              btn('This one', { cls: 'pill sm', onClick: () => chosen({ template: t.template, topic: t.topic, via: 'pick' }) }))),
          exHost));
      });
      const n = 5;
      rows.append(h('div', { style: 'padding: 10px 12px; border: 1px dashed var(--line); border-radius: 12px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px' },
        h('span', {}, h('b', { text: 'Not sure', style: 'font-weight: 600' }), h('span', { class: 'help', style: 'display: block; margin: 2px 0 0', text: 'Practise the skill instead of logging it.' })),
        btn(`Practise ${short(slug)} · ${n}`, { cls: 'btn sm', onClick: e => busy(e.currentTarget, () => startDrill({ topics: [slug], count: n, source: 'outside' })).catch(() => say('Couldn’t start it. Try again.')) })));
      view.replaceChildren(h('p', { class: 'label' }, 'Which kind of question? ', UI.chip(slug)),
        types.length ? rows : h('p', { class: 'help', text: cat ? 'No question types for this skill.' : 'Loading…' }),
        h('div', { style: 'margin-top: 12px' }, btn('Another skill', { cls: 'quiet', onClick: () => picker() })));
    }

    /* ---- the type is chosen: which answer, what went wrong, where */
    async function chosen(pick) {
      st.picked = pick;
      st.reason = undefined; st.auto = null; st.letter = null;
      const t = cat && cat.list.find(x => x.template === pick.template);
      st.reasons = t ? t.reasons : [];
      const head = h('div', { style: 'display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 12px 14px; border-radius: 12px; background: var(--wash)' },
        UI.chip(pick.topic), h('b', { text: nameOf(pick.template), style: 'font-weight: 600' }),
        pick.cb_id ? h('span', { class: 'mono help', style: 'margin: 0', text: pick.cb_id }) : null,
        h('span', { style: 'margin-left: auto' }, btn('Change', { cls: 'quiet', onClick: () => { st.picked = null; oneQuestion(); } })),
        aboutOf(pick.template));
      const ex = examples.get(pick.template);
      const spr = ex && ex.question && ex.question.type === 'spr';
      // which answer did you pick?
      const ans = h('div', { style: 'margin-top: 18px' }, h('p', { class: 'label', text: 'Which answer did you pick?' }));
      const letters = UI.chips(null, ['A', 'B', 'C', 'D'].map(L => ({ value: L, label: L })).concat([{ value: '', label: 'It was a grid-in' }]),
        { value: null, label: 'Your answer', onChange: v => { st.letter = v || null; gridBox.hidden = v !== ''; if (v) fromLetter(v); } });
      const gridIn = h('input', { class: 'field sm', type: 'text', maxlength: 8, placeholder: 'What you typed', 'aria-label': 'What you typed', autocomplete: 'off', style: 'max-width: 200px' });
      const preview = h('span', { class: 'mono help', style: 'margin-left: 10px' });
      gridIn.addEventListener('input', () => { st.value = gridIn.value.trim(); preview.textContent = st.value ? st.value.replace(/-/g, '−') : ''; });
      const gridBox = h('div', { style: 'margin-top: 8px; display: flex; align-items: center', hidden: !spr }, gridIn, preview);
      if (spr) letters.set('', true);
      ans.append(letters.el, gridBox);
      // what went wrong?
      const why = h('div', { style: 'margin-top: 18px' });
      const drawReasons = () => {
        const name = 'qm-reason';
        const list = h('div', { class: 'checks', role: 'radiogroup', 'aria-label': 'What went wrong?' });
        const opt = (value, label, extra) => {
          const r = h('input', { type: 'radio', name, value });
          if (st.reason === value) r.checked = true;
          r.addEventListener('change', () => { st.reason = value; other.hidden = value !== '__other'; if (value === '__other') other.focus(); });
          return h('label', { class: 'check' }, r, h('span', {}, label, extra ? h('span', { class: 'help', style: 'display: block; margin: 2px 0 0', text: extra }) : null));
        };
        (st.reasons || []).forEach(r => list.append(opt(r.norm, cap(r.label), st.auto === r.norm ? 'From the answer you picked' : null)));
        list.append(opt('__other', 'Something else'), opt('__none', 'I don’t know'));
        const other = h('input', { class: 'field sm', type: 'text', maxlength: 80, placeholder: 'What went wrong, in a few words', 'aria-label': 'Something else',
          hidden: st.reason !== '__other', style: 'margin-top: 6px' });
        other.value = st.other;
        other.addEventListener('input', () => { st.other = other.value; });
        if (UI.counter) UI.counter(other, 80);
        why.replaceChildren(h('p', { class: 'label' }, 'What went wrong? ', h('span', { class: 'help', style: 'display: inline; font-weight: 400', text: 'optional' })), list, other);
      };
      drawReasons();
      // with an exact ID, the letter names the mistake (U2)
      async function fromLetter(L) {
        if (!pick.cb_id || !UI.has('match')) return;
        try {
          const r = await UI.api('/types/match/pick', { method: 'POST', body: { cb_id: pick.cb_id, letter: L }, quiet: true });
          if (r && r.reason) {
            const hit = (st.reasons || []).find(x => x.label === r.reason || x.norm === r.reason);
            st.auto = hit ? hit.norm : null;
            if (hit) st.reason = hit.norm;
            drawReasons();
          }
        } catch (_) {}
      }
      // where was it?
      const where = h('div', { style: 'margin-top: 18px' }, h('p', { class: 'label' }, 'Where was it? ', h('span', { class: 'help', style: 'display: inline; font-weight: 400', text: 'optional' })));
      st.origin = pick.cb_id ? 'cb_qbank' : st.origin;
      const originChips = UI.chips(null, ORIGINS, { value: st.origin, label: 'Where was it?', onChange: v => { st.origin = v; } });
      const note = h('input', { class: 'field sm', type: 'text', maxlength: 200, placeholder: 'A note, e.g. “Practice test 4, question 17”', 'aria-label': 'Note', style: 'margin-top: 8px' });
      note.addEventListener('input', () => { st.note = note.value; });
      if (UI.counter) UI.counter(note, 200);
      where.append(originChips.el, note);
      view.replaceChildren(head, ans, why, where);
      add.hidden = false;
      add.focus({ preventScroll: true });
    }
    async function submit() {
      if (!st.picked) { say('Find the question first, or pick by skill.'); return; }
      say('');
      const body = { template: st.picked.template, origin: st.origin || 'other' };
      if (st.reason && !st.reason.startsWith('__')) body.reason = st.reason;
      if (st.reason === '__other' && st.other.trim()) body.note = st.other.trim().slice(0, 80);
      if (st.note.trim()) body.where_note = st.note.trim().slice(0, 200);
      if (st.picked.cb_id) body.cb_id = st.picked.cb_id;
      if (st.letter) body.letter = st.letter;
      await busy(add, async () => {
        let r;
        try { r = await UI.api('/mistakes/log', { method: 'POST', body }); }
        catch (e) {
          say(e.status === 429 ? 'That’s the most for one day. Log the rest tomorrow.' : e.status === 422 ? `Not added: ${(e.detail && e.detail.reason) || e.message}` : errText(e));
          return;
        }
        const trap = r.trap || {};
        st.done = { trap, template: body.template, topic: st.picked.topic, reason: body.reason || null };
        UI.refresh();
        if (UI.toast) UI.toast('Added. Two clean answers on this type close it.', { wait: true, action: { label: 'Practise now · 3',
          onClick: () => startDrill({ pool: 'redo', ids: [trap.id], count: 3, source: 'outside' }).catch(() => UI.toast('Couldn’t start it. Try again.')) } });
        doneView(st.done);
      });
    }
    // the fix path, in place: the trap, Try one now, Practise 3
    function doneView(d) {
      add.hidden = true; again.hidden = false;
      const trapHost = h('div');
      const tryHost = h('div', { style: 'margin-top: 10px' });
      const tryBtn = btn('Try one now', { cls: 'btn sm', onClick: () => tryOne(tryHost, d, tryBtn) });
      const three = btn('Practise 3', { cls: 'pill sm', onClick: e => busy(e.currentTarget, () => startDrill({ pool: 'redo', ids: [d.trap.id], count: 3, source: 'outside' }))
        .catch(() => say('Couldn’t start it. Try again.')) });
      view.replaceChildren(
        h('p', { style: 'font-weight: 600' }, 'Added to your mistakes', h('span', { class: 'help', style: 'display: block; margin: 4px 0 0; font-weight: 400',
          text: `${short(d.topic)} · ${nameOf(d.template)}. Check-ins follow 3, 10 and 30 days after you fix it.` })),
        h('p', { class: 'label', style: 'margin-top: 16px', text: d.reason ? 'The trap, in one of ours' : 'One like it' }), trapHost,
        h('div', { style: 'display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px' }, tryBtn, three), tryHost);
      loadExample(trapHost, d.template, d.reason ? { want: d.reason } : {});
    }
    // one inline question on this type, offering the trap (R24 inline, source try)
    async function tryOne(host, d, b) {
      b.hidden = true;
      host.replaceChildren(UI.skel ? UI.skel(null, 'lines:3') : '');
      const body = { templates: [d.template], count: 1, source: 'try' };
      if (d.reason) body.want = { [d.template]: d.reason };
      try {
        const r = await UI.api('/drill', { method: 'POST', body });
        host.replaceChildren();
        const q = r.question, t0 = performance.now();
        const ctl = UI.question(host, q, { onAnswer: async given => {
          try {
            const f = await UI.api(`/drill/${encodeURIComponent(r.id)}/answer`, { method: 'POST', body: { question_id: q.id, answer: given, ms: Math.round(performance.now() - t0) } });
            ctl.reveal(f, { open: true });
            UI.api(`/drill/${encodeURIComponent(r.id)}/finish`, { method: 'POST', quiet: true }).catch(() => {});
            UI.refresh();
          } catch (e) { ctl.unlock(); say(errText(e)); }
        } });
      } catch (e) { host.replaceChildren(h('p', { class: 'help', text: e.status === 409 ? 'No fresh one to try right now.' : errText(e) })); b.hidden = false; }
    }

    /* ---- a whole test: two 22-cell grids, a skill for each miss (U2) */
    const misses = new Map();                // "1-7" -> {module, n, topic|null, letter|null}
    let testDate = null, testScore = null;
    function wholeTest() {
      const today = new Date(), iso = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
      const date = h('input', { class: 'field sm', type: 'date', id: 'qm-date', max: iso, value: iso, style: 'max-width: 190px' });
      const score = UI.has('scores') ? h('input', { class: 'field sm', type: 'number', id: 'qm-score', min: 200, max: 800, step: 10, placeholder: '200–800', style: 'max-width: 140px' }) : null;
      const meta = h('div', { style: 'display: flex; flex-wrap: wrap; gap: 12px 20px' },
        h('div', {}, h('label', { class: 'label', for: 'qm-date', text: 'Date' }), date),
        score ? h('div', {}, h('label', { class: 'label', for: 'qm-score', text: 'Math score' }), score) : null);
      const count = h('p', { class: 'help', 'aria-live': 'polite' });
      const grid = m => {
        const g = h('div', { role: 'group', 'aria-label': `Module ${m}`, style: 'display: grid; grid-template-columns: repeat(auto-fill, minmax(40px, 1fr)); gap: 6px' });
        for (let n = 1; n <= 22; n++) {
          const k = `${m}-${n}`;
          const c = h('button', { type: 'button', class: 'btn sm', style: 'min-width: 0; padding: 0; height: 44px; flex-direction: column; gap: 0' });
          const draw = () => {
            const x = misses.get(k);
            c.replaceChildren(...[h('span', { class: 'mono', text: String(n) }), x && x.topic ? UI.glyph(x.topic) : null].filter(Boolean));
            c.setAttribute('aria-pressed', String(!!x));
            c.setAttribute('aria-label', `Question ${n}${x ? `, missed${x.topic ? `, ${short(x.topic)}` : ''}` : ''}`);
            c.style.boxShadow = x ? 'inset 0 0 0 1.5px var(--amber)' : '';
            c.style.background = x ? 'var(--wash)' : '';
            const t = [...misses.values()].filter(v => v.topic).length;
            count.textContent = misses.size ? `${plural(misses.size, 'missed question')} · ${plural(new Set([...misses.values()].map(v => v.topic).filter(Boolean)).size, 'skill')}` : '';
            build.disabled = !t;
          };
          c.addEventListener('click', () => cellPicker(c, k, m, n, draw));
          draw();
          g.append(c);
        }
        return g;
      };
      view.replaceChildren(meta,
        h('p', { class: 'label', style: 'margin-top: 18px', text: 'Module 1' }), grid(1),
        h('p', { class: 'label', style: 'margin-top: 14px', text: 'Module 2' }), grid(2),
        h('p', { class: 'help', text: 'Tap each question you missed. Bluebook’s review shows each question’s skill.' }), count);
      testDate = date; testScore = score;
    }
    function cellPicker(anchor, k, m, n, draw) {
      if (!UI.pop) return;
      const x = misses.get(k) || { module: m, n, topic: null, letter: null };
      const content = h('div', { style: 'display: grid; gap: 10px; max-width: 340px' },
        h('b', { text: `Module ${m} · Question ${n}` }),
        skillChips(slug => { x.topic = slug; misses.set(k, x); draw(); p.close(); }));
      const letter = UI.chips(null, ['A', 'B', 'C', 'D'].map(L => ({ value: L, label: L })), { value: x.letter, label: 'The answer you picked',
        onChange: v => { x.letter = v; misses.set(k, x); draw(); } });
      content.append(h('div', {}, h('p', { class: 'help', style: 'margin: 0 0 6px', text: 'The answer you picked (optional)' }), letter.el),
        h('div', { style: 'display: flex; gap: 8px' },
          btn('Not sure of the skill', { cls: 'quiet', onClick: () => { x.topic = null; misses.set(k, x); draw(); p.close(); } }),
          misses.has(k) ? btn('Not missed', { cls: 'quiet', onClick: () => { misses.delete(k); draw(); p.close(); } }) : null));
      const p = UI.pop(anchor, content, { label: `Question ${n}` });
    }
    async function follow() {
      const list = [...misses.values()];
      const topics = [...new Set(list.map(x => x.topic).filter(Boolean))];
      if (!topics.length) { say('Tap a question you missed and pick its skill.'); return; }
      say('');
      await busy(build, async () => {
        try {
          let score_id = null;
          const s = testScore && Number(testScore.value);
          if (s && UI.has('scores')) score_id = (await UI.api('/scores', { method: 'POST', body: { day: testDate.value, math: s, source: 'bluebook' } })).id;
          if (UI.has('outside')) {
            const r = await UI.api('/outside/misses', { method: 'POST', body: { score_id, day: testDate.value, misses: list } });
            location.href = `/practice/session/?id=${encodeURIComponent(r.set || r.id)}`;
            return;
          }
          // ponytail: until F5's /api/outside/misses, 2 fresh questions per missed skill, grouped
          await startDrill({ topics, count: Math.min(120, topics.length * 2), order: 'grouped', source: 'outside' });
        } catch (e) { say(errText(e)); }
      });
    }

    return { el, foot: [status, again, add, build], show: () => paint(mode.value), focus: () => { if (field && field.isConnected) field.focus(); } };
  }

  /* ------------------------------------------------------------ Add a word (S9, W19) */
  function wordPane(close) {
    const el = h('div', { class: 'quick-w' });
    const f = h('textarea', { class: 'field', id: 'qw-word', rows: 2, maxlength: 20000, autocomplete: 'off',
      placeholder: 'A word, or paste a passage to pick its words', style: 'min-height: 56px; resize: vertical' });
    const add = btn('Add', { cls: 'pill', onClick: () => go() });
    const note = h('p', { class: 'help' });
    el.append(h('label', { class: 'label', for: 'qw-word', text: 'Word or passage' }), f, note);
    let ready = false;
    const load = typeof UI.addWord === 'function' ? Promise.resolve(true)
      : UI.has('words') ? UI.need('words-ui').then(() => typeof UI.addWord === 'function', () => false) : Promise.resolve(false);
    load.then(ok => {
      ready = ok;
      add.disabled = !ok; f.disabled = !ok;
      note.textContent = ok ? 'A passage opens with its SAT words marked, to pick from.' : 'Adding words opens with the Words section.';
    });
    f.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && f.value.trim().split(/\s+/).length <= 3) { e.preventDefault(); go(); } });
    function go() {
      const v = f.value.trim();
      if (!ready) return;
      close();
      UI.addWord(v.split(/\s+/).length > 6 ? { text: v } : v);
    }
    return { el, foot: [add], focus: () => f.focus() };
  }

  /* ------------------------------------------------------------ the sheet */
  let cur = null;
  function quick(tab) {
    if (cur) { if (tab) cur.tab(tab); return cur; }
    let current = ['question', 'mistake', 'word'].includes(tab) ? tab : lget(TAB_KEY, 'question');
    if (!['question', 'mistake', 'word'].includes(current)) current = 'question';
    const foot = h('div', { class: 'sheet-foot' });
    let reg = null, qp = null;
    const panes = {};
    const s = UI.sheet({
      label: 'Quick',
      body: () => null,
      onClose: () => {
        if (reg) reg.unregister();
        removeEventListener('pagehide', leave);
        cur = null;
        if (qp && qp.answered) {
          const n = qp.answered, r = qp.right;
          qp.finish().then(() => UI.refresh()).then(() => {
            const it = (UI.nextItems() || [])[0];
            if (UI.toast) UI.toast(`${plural(n, 'answered', 'answered')} · ${fmt(r)} right${it ? `. Next: ${it.title}` : ''}`,
              it ? { action: { label: 'Start', onClick: () => UI.start(it).catch(() => {}) } } : {});
          });
        } else if (qp) qp.finish();
      },
    });
    const leave = () => { if (qp) qp.finish(true); };
    addEventListener('pagehide', leave);
    s.el.classList.add('quick');
    const head = s.el.querySelector('.sheet-head');
    const narrow = matchMedia('(max-width: 419px)').matches;       // three labels in one row at 360
    const seg = UI.seg(null, [{ value: 'question', label: narrow ? 'Question' : 'Quick question' }, { value: 'mistake', label: narrow ? 'Mistake' : 'Log a mistake' },
      { value: 'word', label: narrow ? 'Word' : 'Add a word' }],
      { value: current, label: 'Quick', onChange: v => show(v) });
    seg.el.style.minWidth = '0';
    seg.el.style.overflowX = 'auto';
    const h2 = head.querySelector('h2');
    if (h2) h2.replaceWith(seg.el); else head.prepend(seg.el);
    s.el.append(foot);
    const close = () => s.close();

    function pane(name) {
      if (!panes[name]) {
        panes[name] = name === 'question' ? (qp = questionPane(s)) : name === 'mistake' ? mistakePane(s, close) : wordPane(close);
      }
      return panes[name];
    }
    function show(name) {
      current = name;
      lput(TAB_KEY, name);
      if (seg.value !== name) seg.set(name, true);
      const p = pane(name);
      s.body.replaceChildren(p.el);
      s.el.style.height = name === 'word' ? '' : 'min(780px, calc(100dvh - 48px))';   // no jump as questions load
      foot.replaceChildren(...p.foot.filter(Boolean));
      if (name === 'question') p.start();
      if (p.show) p.show();
      if (p.focus) setTimeout(() => p.focus(), 0);
    }
    // A–D, 1–4 and Enter or N inside the sheet, on the question tab (a focused control keeps its Enter)
    const delegate = {};
    ['Enter', 'N', 'A', 'B', 'C', 'D', '1', '2', '3', '4'].forEach(k => {
      delegate[k] = { does: k === 'Enter' || k === 'N' ? 'Another' : 'Choose', hidden: /\d/.test(k),
        run: e => {
          if (!qp || current !== 'question') return false;
          if (k === 'Enter' && e && e.target && e.target.closest && e.target.closest('button, a, [role="radio"], textarea') && !e.target.closest('.opts')) return false;
          return qp.keys[k].run(e);
        } };
    });
    reg = UI.keys.register('quick', delegate, { within: s.el, label: 'Quick question', when: () => current === 'question' });
    show(current);
    cur = { el: s.el, tab: name => show(name), close };
    return cur;
  }

  UI.quick = quick;
})();
