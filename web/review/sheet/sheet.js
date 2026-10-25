/* ============================================================================
   SAT Freshman -- a printed worksheet's answer sheet (/review/sheet/?id=<sid>): review.md V18.

   One row per number: A-D, or a grid-in field with UI.spr's filter and preview; an optional
   Minutes taken; Submit files each answer through /api/drill/{id}/answer (end mode, ms =
   minutes / n), then finishes the set. With the key unprinted the seeds were unseen, so
   rights are clean and each miss is named and opens a trap.

   The key (every answer, each option's misconception, the rationale) prints after Submit
   (?key=1). Print the key now, before the answers, confirms first and posts
   /api/drill/{id}/key (cfg.key_printed): answers entered after it file as repeats.
   Entries wait in localStorage (satf.sheet.<sid>) until Submit, so a reload keeps them.
   ========================================================================== */
(() => {
  'use strict';
  const doc = document;
  const h = UI.h;
  // the back link's caret is drawn (UI.ICON), not a text glyph
  const backEl = document.querySelector('.wks-back');
  if (backEl && UI.icon) backEl.prepend(UI.icon('caret_left', 16));
  const $ = id => doc.getElementById(id);
  const enc = encodeURIComponent;
  const Q = new URLSearchParams(location.search);
  const sid = Q.get('id');
  const keyMode = Q.get('key') === '1';
  const LET = 'ABCDE';
  const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : '');
  const plural = (n, one, many) => `${n} ${n === 1 ? one : (many || one + 's')}`;
  const toast = t => UI.toast && UI.toast(t);
  const reasonOf = e => {
    const d = e && e.detail;
    const r = (d && typeof d === 'object' && (d.reason || d.message)) || (typeof d === 'string' ? d : null);
    return r ? cap(String(r)) : 'That didn’t work. Try again.';
  };
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const DRAFT = `satf.sheet.${sid}`, PRINTED = `satf.sheet.key.${sid}`;
  const box = $('sheet');
  let st = null, qs = [], answers = {}, minutes = '', sent = false;

  const api = (p, o) => UI.api(`/drill/${enc(sid)}${p}`, o);
  const btn = (text, cls, onclick) => h('button', { type: 'button', class: cls, text, onclick });
  function card(title, sub, acts, big) {
    box.removeAttribute('aria-busy');
    // the score after Submit is the page's hero: the raised card with the number at the hero size
    box.replaceChildren(h('div', { class: big ? 'card hero wks-card' : 'card wks-card' }, h('p', { class: big ? 'hero-num' : 't', text: title }), sub ? h('p', { class: 's', text: sub }) : null,
      h('div', { class: 'wks-acts' }, ...acts.filter(Boolean))));
  }
  // the worksheet's subject (its set says it once loaded): Review opens on it
  const subj = () => (st && st.subject) || UI.subject.get();
  const toReview = () => h('a', { class: 'btn', href: `/review/?subject=${subj()}`, text: 'Back to Review' });
  const topicName = t => (UI.RW_SKILL && UI.RW_SKILL[t]) || (UI.TOPIC && UI.TOPIC[t] && UI.TOPIC[t].name) || cap(String(t || '').replace(/_/g, ' '));

  /* ------------------------------------------------------------ load */
  async function load() {
    st = await api('');
    const ids = st.served.filter(s => s.kind === 'question').map(s => s.id);
    // a worksheet left in progress may not have served every slot yet (the print view serves them; so does this)
    if (!st.finished && st.total && st.feedback === 'end') {
      let guard = 0;
      while (ids.length < st.total && guard++ < st.total + 2) {
        let r;
        try { r = await api('/next', { method: 'POST', body: { skip: true }, quiet: true }); } catch (_) { break; }
        if (!r.question || r.done) break;
        if (!ids.includes(r.question.id)) ids.push(r.question.id);
      }
    }
    const got = await Promise.all(ids.map(id => api(`/q/${enc(id)}`, { quiet: true }).catch(() => null)));
    qs = got.map((d, i) => d && Object.assign({ qid: ids[i] }, d)).filter(Boolean);
  }
  function head() {
    const date = st.started ? UI.date(st.started, 'short') : '';
    const topics = [...new Set(qs.map(d => d.question && d.question.topic).filter(Boolean))].map(topicName);
    $('sub').textContent = ['Worksheet', date, plural(qs.length, 'question'), topics.slice(0, 3).join(', ')].filter(Boolean).join(' · ');
  }

  /* ------------------------------------------------------------ the answer sheet */
  function paintSheet() {
    box.removeAttribute('aria-busy');
    const draft = store.get(DRAFT, {}) || {};
    answers = draft.answers || {};
    minutes = draft.minutes || '';
    const save = () => store.set(DRAFT, { answers, minutes });
    const list = h('ol', { class: 'wks-list', 'aria-label': 'Your answers' });
    const count = h('span', { class: 'meta' });
    const recount = () => {
      const n = qs.filter(d => answers[d.qid] !== undefined && answers[d.qid] !== '').length;
      count.textContent = n ? `${n} of ${qs.length} entered` : '';
    };
    qs.forEach((d, i) => {
      const q = d.question || {};
      const row = h('li', { class: 'wks-row', 'data-i': String(i) }, h('span', { class: 'wks-n', text: `${i + 1}.` }),
        h('span', { class: 'wks-skill', text: cap(q.skill || q.topic_name || '') }));
      if (q.type === 'spr') {
        const pv = h('span', { class: 'pvw', 'aria-live': 'polite' });
        const inp = h('input', { type: 'text', class: 'field', inputmode: 'decimal', autocomplete: 'off', spellcheck: 'false', 'aria-label': `Answer ${i + 1}`, placeholder: 'e.g. 2/3', value: answers[d.qid] || '' });
        let last = inp.value;
        const show = () => {
          const p = UI.spr ? UI.spr.preview(pv, inp.value) : { ok: true };
          pv.classList.toggle('err', !!(p && p.error));
          if (p && p.error) pv.textContent = p.error;
        };
        inp.addEventListener('input', () => {
          const s = UI.spr ? UI.spr.clean(inp.value) : inp.value;
          if (UI.spr && (!UI.spr.charsOk(s) || s.length > UI.spr.cap(s))) { inp.value = last; return; }   // the usual keystroke filter
          last = inp.value;
          if (s) answers[d.qid] = s; else delete answers[d.qid];
          save(); recount(); show();
        });
        show();
        row.append(h('div', { class: 'wks-grid' }, inp, pv));
      } else {
        const n = Math.min((q.choices || []).length || 4, 5);
        const grp = h('div', { class: 'wks-abcd', role: 'group', 'aria-label': `Answer ${i + 1}` });
        for (let k = 0; k < n; k++) {
          const b = h('button', { type: 'button', text: LET[k], 'aria-pressed': String(answers[d.qid] === k), 'aria-label': `${i + 1}: ${LET[k]}` });
          b.addEventListener('click', () => pick(d, k, grp));
          grp.append(b);
        }
        row.append(grp);
      }
      list.append(row);
    });
    function pick(d, k, grp) {
      if (answers[d.qid] === k) delete answers[d.qid]; else answers[d.qid] = k;   // a second tap clears it
      grp.querySelectorAll('button').forEach((b, j) => b.setAttribute('aria-pressed', String(answers[d.qid] === j)));
      save(); recount();
    }
    // typing A-D (or 1-4) on a row picks it and moves to the next number
    list.addEventListener('keydown', e => {
      if (e.metaKey || e.ctrlKey || e.altKey || (e.target && e.target.tagName === 'INPUT')) return;
      const row = e.target.closest && e.target.closest('.wks-row');
      const grp = row && row.querySelector('.wks-abcd');
      if (!grp) return;
      const k = /^[a-e]$/i.test(e.key) ? LET.indexOf(e.key.toUpperCase()) : /^[1-5]$/.test(e.key) ? +e.key - 1 : -1;
      const btns = grp.querySelectorAll('button');
      if (k < 0 || k >= btns.length) return;
      e.preventDefault();
      if (btns[k].getAttribute('aria-pressed') !== 'true') btns[k].click();   // typing sets it; only a tap clears
      const next = row.nextElementSibling;
      const f = next && next.querySelector('button, input');
      if (f) f.focus();
    });
    const mins = h('input', { type: 'number', class: 'field', min: '1', max: '600', inputmode: 'numeric', id: 'wsmin', value: minutes });
    mins.addEventListener('input', () => { minutes = mins.value; save(); });
    const submit = h('button', { type: 'button', class: 'pill', text: 'Submit answers' });
    submit.addEventListener('click', () => send(submit));
    recount();
    // from 1280px Minutes taken, the count and Submit sit in a sticky right column (index.html); below it the foot sticks
    box.replaceChildren(h('div', { class: 'wks-form' }, list, h('div', { class: 'wks-side' },
      h('p', { class: 'wks-min' }, h('label', { for: 'wsmin', text: 'Minutes taken' }), mins, h('span', { class: 'meta', text: 'optional' })),
      h('div', { class: 'wks-foot' }, count, submit))));
    const first = list.querySelector('button, input');
    if (first && !matchMedia('(pointer: coarse)').matches) first.focus({ preventScroll: true });
  }

  async function send(b) {
    const blank = qs.filter(d => answers[d.qid] === undefined || answers[d.qid] === '').length;
    if (blank && !(await UI.confirm({ title: `${plural(blank, 'answer')} ${blank === 1 ? 'is' : 'are'} blank`, text: 'Blank ones count as not answered. Submit anyway?', confirm: 'Submit' }))) return;
    b.setAttribute('aria-busy', 'true'); b.disabled = true;
    const m = parseInt(minutes, 10);
    const ms = m > 0 ? Math.round((m * 60000) / Math.max(1, qs.length)) : undefined;
    try {
      for (const d of qs) {
        const a = answers[d.qid];
        if (a === undefined || a === '' || d.given !== null && d.given !== undefined && d.given !== '' && d.given !== '_skip') continue;
        await api('/answer', { method: 'POST', body: Object.assign({ question_id: d.qid, answer: a }, ms ? { ms } : {}) });
      }
      await api('/finish', { method: 'POST' });
      store.set(DRAFT, null);
      sent = true;
      await start();
    } catch (e) {
      b.removeAttribute('aria-busy'); b.disabled = false;
      toast(reasonOf(e));
    }
  }

  /* ------------------------------------------------------------ after Submit */
  function paintDone() {
    const right = (st.marks || []).filter(x => x === true).length;
    const printed = store.get(PRINTED, false);
    card(`${right} / ${qs.length}`, printed ? 'Key printed first: these answers don’t count as clean.' : 'Misses are in Review.', [
      h('a', { class: 'pill', href: `/review/sheet/?id=${enc(sid)}&key=1&print=1`, text: 'Print the key' }),
      h('a', { class: 'btn', href: `/practice/session/?id=${enc(sid)}`, text: 'See the summary' }),
      btn('Print another version', 'btn', e => another(e.currentTarget)),
      h('a', { class: 'quiet', href: `/review/?tab=redo&subject=${subj()}`, text: 'Open Review' })], true);
    // just submitted: the score rolls up from 0 once (UI.roll); a later visit shows it still
    const fig = box.querySelector('.hero-num');
    if (sent && fig && UI.roll) { fig.textContent = `0 / ${qs.length}`; UI.roll(fig, `${right} / ${qs.length}`); }
    $('title').textContent = 'Worksheet answers';
  }
  async function another(b) {
    if (b) b.setAttribute('aria-busy', 'true');
    try {
      const d = await UI.api('/drill', { method: 'POST', body: { again: sid } });
      location.href = `/practice/session/?id=${enc(d.id)}&print=1`;
    } catch (e) { if (b) b.removeAttribute('aria-busy'); toast(reasonOf(e)); }
  }
  // More (a quiet icon): print the key now (answers after it are not clean), the worksheet again, another version
  function paintMore() {
    const more = h('button', { type: 'button', class: 'ibtn', 'aria-label': 'More', title: 'More' }, UI.icon('more', 20));
    const items = () => [
      !st.finished ? { label: 'Print the key now', sub: 'Answers entered after this won’t count as clean', onClick: printKeyNow } : null,
      { label: 'Print the worksheet again', href: `/practice/session/?id=${enc(sid)}&print=1` },
      { label: 'Print another version', sub: `${subj() === 'rw' ? 'New passages' : 'New numbers'}, for a second try or another student`, onClick: () => another() },
    ].filter(Boolean);
    if (UI.menu && UI.menu.bind) UI.menu.bind(more, items, { label: 'Worksheet', align: 'end' });
    $('more').replaceChildren(more);
  }
  async function printKeyNow() {
    const ok = await UI.confirm({ title: 'Print the key now?', text: 'Answers entered after this won’t count as clean: they’re filed and named, but they don’t close a mistake or move mastery.', confirm: 'Print the key' });
    if (!ok) return;
    try {
      await api('/key', { method: 'POST', body: {} });
    } catch (e) {
      toast(e.status === 404 || e.status === 405 ? 'Printing the key early isn’t available yet. Submit your answers first.' : reasonOf(e));
      return;
    }
    store.set(PRINTED, true);
    location.href = `/review/sheet/?id=${enc(sid)}&key=1&print=1`;
  }

  /* ------------------------------------------------------------ the key (?key=1) */
  function paintKey() {
    $('title').textContent = 'Answer key';
    const shown = qs.filter(d => d.feedback);
    if (!shown.length) {
      card('The key opens after you submit your answers.', null, [h('a', { class: 'pill', href: `/review/sheet/?id=${enc(sid)}`, text: 'Enter answers' }), toReview()]);
      return;
    }
    box.removeAttribute('aria-busy');
    const wrap = h('div', {});
    qs.forEach((d, i) => {
      const q = Object.assign({}, d.question, { template: d.template, seed: d.seed });
      const el = h('article', { class: 'wks-key-q' }, h('p', { class: 'wks-key-n', text: `${i + 1}.` }));
      const g = d.given;
      if (!d.feedback && g !== null && g !== undefined && g !== '' && g !== '_skip') el.append(h('p', { class: 'wks-key-yours', text: `Your answer: ${Number.isInteger(g) ? LET[g] : g}` }));
      const host = h('div');
      el.append(host);
      wrap.append(el);
      try {
        if (d.feedback) UI.workspace(host, q, { mode: 'review', fb: Object.assign({ given: g }, d.feedback), bar: false, toolbar: false, head: false, prefs: { open_explanations: true, option_reasons: true } });
        else host.append(h('p', { class: 'meta', text: 'Not in the key yet.' }));
      } catch (_) { host.append(h('p', { text: q.stem || '' })); }
    });
    const ctl = h('div', { class: 'wks-acts wks-noprint wks-key-ctl' },
      btn('Print / Save as PDF', 'pill', () => print()),
      h('a', { class: 'btn', href: `/review/sheet/?id=${enc(sid)}`, text: st.finished ? 'Back to the answers' : 'Enter answers' }));
    box.replaceChildren(ctl, wrap);
    if (Q.get('print') === '1') setTimeout(() => { try { print(); } catch (_) {} }, 400);
  }

  /* ------------------------------------------------------------ boot */
  async function start() {
    box.setAttribute('aria-busy', 'true');
    if (!box.firstChild && UI.skel) UI.skel(box, 'rows:6');
    try { await load(); } catch (e) {
      if (e.status === 404 || e.status === 403) card('This worksheet isn’t on this device’s account.', 'Print one from Review’s Redo or Saved tab.', [toReview()]);
      else { box.replaceChildren(); box.removeAttribute('aria-busy'); UI.cardError(box, start, 'The worksheet didn’t load.'); }
      return;
    }
    if (st.source && st.source !== 'worksheet' && !keyMode) {
      card('This set isn’t a printed worksheet.', 'Its answers go in online.', [h('a', { class: 'pill', href: `/practice/session/?id=${enc(sid)}`, text: 'Open the set' }), toReview()]);
      return;
    }
    head();
    paintMore();
    if (backEl) backEl.href = `/review/?subject=${subj()}`;
    if (keyMode) paintKey();
    else if (st.finished) paintDone();
    else paintSheet();
  }
  if (!sid) card('No worksheet here.', 'Print one from Review’s Redo or Saved tab, then enter its answers here.', [toReview()]);
  else start();
})();
