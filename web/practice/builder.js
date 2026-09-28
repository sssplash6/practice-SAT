/* ============================================================================
   SAT Freshman -- the practice builder, /practice/ (spec 3.3 part 1, practice.md
   P3 P5 P6 P7 P10-P17 P19 P21 P22). One read (GET /api/bank), one debounced
   POST /api/drill/preview for every count and the Start gate, POST /api/drill to
   start. Settings 1-9 save to prefs (PUT /api/me) 600 ms after a change; a deep
   link's settings apply to this visit only. Nothing auto-starts.
   ========================================================================== */
(() => {
  const h = UI.h, $ = s => document.querySelector(s);
  const icon = (name, size = 18) => h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.svg(UI.ICON[name] || UI.ICON.dot, size) });
  const url = new URLSearchParams(location.search);
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const pct = x => (x === null || x === undefined ? '—' : `${Math.round(x * 100)}%`);
  const n0 = n => (n === null || n === undefined ? '…' : UI.num ? UI.num(n) : String(n));
  const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + 's'}`;
  const mmss = ms => UI.mmss(Math.round((ms || 0) / 1000));
  const cap = t => (t ? t[0].toUpperCase() + t.slice(1) : '');
  const DAY = 864e5;
  function ago(iso) {
    if (!iso) return '—';
    const d = Math.floor((Date.now() - new Date(iso).getTime()) / DAY);
    if (d < 1) return 'today';
    if (d < 14) return `${d}d ago`;
    if (d < 60) return `${Math.floor(d / 7)}w ago`;
    return `${Math.floor(d / 30)}mo ago`;
  }
  const when = iso => { try { return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }); } catch (_) { return iso || ''; } };
  // one bar and its one word (Learning · Getting there · Strong); the word says it, so the bar is decoration
  const mbar = (m, answered) => h('span', { class: 'mcell' }, h('span', { class: 'mbar', 'aria-hidden': 'true' }, h('i', { style: `--m:${answered ? Math.max(0, Math.min(1, m || 0)) : 0}` })),
    h('span', { class: 'w', text: UI.masteryWord(m, answered) }));
  // an explanation on hover, keyboard focus or a tap (decision 7), and to a screen reader as the control's description
  const FOC = 'button, input, select, textarea, [tabindex="0"]';
  const tipped = new WeakSet();
  let lastPt = 'mouse';
  addEventListener('pointerdown', e => { lastPt = e.pointerType; }, true);
  const noHover = () => { try { return matchMedia('(hover: none)').matches; } catch (_) { return false; } };
  // a tap has no hover: show the tip once the tap's own work is done; a repaint may have swapped the control, so find its twin under the finger
  function tapTip(e) {
    if (e._tip) return;                    // the innermost tip wins
    e._tip = true;
    const pt = e.pointerType || (e.detail ? lastPt : '');     // '' is a keyboard click: focus already shows it
    if (!pt || (pt === 'mouse' && !noHover())) return;
    const el = e.currentTarget, x = e.clientX, y = e.clientY;
    setTimeout(() => {
      let t = el.isConnected ? el : document.elementFromPoint(x, y);
      while (t && !tipped.has(t)) t = t.parentElement;
      if (t) t.dispatchEvent(new PointerEvent('pointerenter', { pointerType: 'mouse' }));
    });
  }
  function tip(el, text) {
    if (!el || !text) return el;
    const say = typeof text === 'function' ? text : () => text;
    if (UI.tooltip) { UI.tooltip(el, say); tipped.add(el); el.addEventListener('click', tapTip); }
    if (!el.matches(FOC)) el.querySelectorAll(FOC).forEach(f => {
      if (typeof text === 'string') f.setAttribute('aria-description', text);
      f.addEventListener('focus', () => { try { if (f.matches(':focus-visible')) el.dispatchEvent(new PointerEvent('pointerenter', { pointerType: 'mouse' })); } catch (_) {} });
      f.addEventListener('blur', () => el.dispatchEvent(new PointerEvent('pointerleave')));
    });
    return el;
  }
  const TIERS = ['easy', 'medium', 'hard'];
  const TIER_WORD = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const LEVELS = [1, 2, 3, 4, 5, 6, 7];
  const LEVEL_TIER = l => (l <= 2 ? 'easy' : l <= 5 ? 'medium' : 'hard');
  const REASON = {
    no_templates: 'Pick at least one skill',
    'no_grid-in_questions': 'Nothing here makes grid-ins at these levels',
    'no_multiple-choice_questions': 'Nothing here makes multiple choice at these levels',
    no_open_mistakes: 'No open mistakes in these skills',
    no_checks_due: 'No check-ins due in these skills',
    nothing_due: 'Nothing due for review in these skills',
    filters_removed_all: 'These filters leave nothing to serve',
    pool_empty: 'Nothing in that pool for these skills',
    no_desmos_types: 'No type here has a Desmos way yet',
    no_official_types: 'No type here is built from official questions',
    no_bank: 'That subject’s bank is coming',
    finish_that_sitting_first: 'Finish that sitting first',
  };
  const reasonText = r => (r ? REASON[r] || cap(String(r).replace(/_/g, ' ')) : '');

  /* ---------------------------------------------------------------- state */
  const DEF = {
    pool: 'new', exact: false, result: 'any', from: 'both', count: 10, box: null,
    zone: 'stretch', tiers: TIERS.slice(), adaptive: false, tier_mix: 'any', levels: LEVELS.slice(), unmeasured: true,
    formats: ['mcq', 'spr'], has: [], timing: 'off', minutes: 16, pace_alert: true, two_passes: true,
    feedback: 'instant', confidence: 'ask', hints: true, cover: 'off', worked_first: true,
    repairs: 'next', final_round: true, review_mix: 20, review_from: 'picked', words_mix: 'off', order: 'mixed', mix: 'even',
  };
  const B = {
    bank: null, byT: new Map(), skills: new Map(), sel: new Set(), st: Object.assign({}, DEF), prefs: {}, saved: null,
    preset: 'coach', source: null, fromLink: false, preview: null, search: '', open: new Set(ls.get('satf.tree.open', null) || []),
    closed: new Set(ls.get('satf.tree.closed', []) || []), sort: ls.get('satf.tree.sort', null), view: 'skills', sets: null, owned: null,
    subject: url.get('subject') === 'rw' ? 'rw' : 'math', presetBody: null, me: null,
  };

  function fromPrefs(p) {
    const st = Object.assign({}, DEF);
    if (Number.isInteger(p.set_length)) st.count = p.set_length === 0 ? null : p.set_length;
    if (p.clock) st.timing = p.clock;
    if (p.clock_minutes) st.minutes = p.clock_minutes;
    ['tiers', 'levels', 'formats'].forEach(k => { if (Array.isArray(p[k]) && p[k].length) st[k] = p[k].slice(); });
    ['adaptive', 'unmeasured', 'pace_alert'].forEach(k => { if (typeof p[k] === 'boolean') st[k] = p[k]; });
    ['feedback', 'repairs', 'order', 'mix', 'confidence'].forEach(k => { if (p[k]) st[k] = p[k]; });
    if (p.pool) st.pool = p.pool === 'checks' ? 'checks' : p.pool;
    const pm = ((p.practice || {}).math) || {};
    ['zone', 'review_mix', 'review_from', 'cover', 'words_mix'].forEach(k => { if (pm[k] !== undefined) st[k] = pm[k]; });
    ['final_round', 'hints', 'worked_first', 'two_passes'].forEach(k => { if (typeof pm[k] === 'boolean') st[k] = pm[k]; });
    return st;
  }
  function toPrefs(st) {
    return {
      set_length: st.count === null ? 0 : st.count, clock: st.timing, clock_minutes: st.minutes, tiers: st.tiers, adaptive: st.adaptive,
      levels: st.levels, unmeasured: st.unmeasured, formats: st.formats, feedback: st.feedback, repairs: st.repairs,
      order: st.order === 'mixup' ? 'mixed' : st.order, mix: st.mix, pool: st.pool, confidence: st.confidence, pace_alert: st.pace_alert,
      practice: { math: { zone: st.zone, review_mix: st.review_mix, review_from: st.review_from, final_round: st.final_round, hints: st.hints,
        worked_first: st.worked_first, two_passes: st.two_passes, cover: st.cover, words_mix: st.words_mix } },
    };
  }
  let saveT = 0;
  function savePrefs() {
    if (B.fromLink) return;
    clearTimeout(saveT);
    saveT = setTimeout(async () => {
      const now = toPrefs(B.st), was = B.saved ? toPrefs(B.saved) : {};
      const diff = {};
      Object.keys(now).forEach(k => {
        if (k === 'practice') {
          const cur = Object.assign({}, ((B.prefs.practice || {}).math) || {}, now.practice.math);
          if (JSON.stringify(now.practice.math) !== JSON.stringify((was.practice || {}).math)) diff.practice = Object.assign({}, B.prefs.practice || {}, { math: cur });
        } else if (JSON.stringify(now[k]) !== JSON.stringify(was[k])) diff[k] = now[k];
      });
      if (!Object.keys(diff).length) return;
      try { await UI.prefs.set(diff); B.saved = Object.assign({}, B.st); footNote('Saved as your defaults'); }
      catch (_) { footNote('Not saved as your defaults. They apply to this set.'); }
    }, 600);
  }

  /* ---------------------------------------------------------------- the selection */
  const typesOf = sk => sk.types || [];
  const allTypes = () => [...B.byT.values()];
  const selOf = sk => typesOf(sk).filter(t => B.sel.has(t.template)).length;
  const triOf = (n, of) => (n === 0 ? 'false' : n === of ? 'true' : 'mixed');
  function setSkill(sk, on) { typesOf(sk).forEach(t => (on ? B.sel.add(t.template) : B.sel.delete(t.template))); }
  function selectedSkills() { return [...B.skills.values()].filter(sk => selOf(sk)); }
  const standard = () => B.st.zone === 'off';
  function tierOk(t, d) {
    const lv = (t.levels || {})[d];
    if (!standard()) return true;
    if (!B.st.tiers.includes(d)) return false;
    const L = lv ? lv.level : t.level;
    if (L && !B.st.levels.includes(L)) return false;
    if (lv && lv.rough && !B.st.unmeasured) return false;
    return true;
  }
  function fits(t) {
    if (!t.formats.some(f => B.st.formats.includes(f))) return false;
    if (B.st.has.includes('desmos') && !t.desmos) return false;
    if (B.st.has.includes('official') && !t.official) return false;
    return (t.tiers || []).some(d => tierOk(t, d));
  }
  function whyNot(ts) {
    if (!ts.length || ts.some(fits)) return '';
    if (!ts.some(t => t.formats.some(f => B.st.formats.includes(f)))) return B.st.formats.includes('spr') ? 'no grid-in types' : 'no multiple-choice types';
    if (B.st.has.includes('desmos') && !ts.some(t => t.desmos)) return 'no Desmos-way types';
    if (B.st.has.includes('official') && !ts.some(t => t.official)) return 'no types built from official questions';
    if (standard() && !ts.some(t => (t.tiers || []).some(d => B.st.tiers.includes(d)))) return `no ${B.st.tiers.map(d => TIER_WORD[d]).join(' or ')} types`;
    return `no types at level ${B.st.levels.join(', ')}`;
  }

  /* ---------------------------------------------------------------- the drill body */
  function selectionBody() {
    const skills = selectedSkills();
    const full = skills.every(sk => selOf(sk) === typesOf(sk).length);
    if (full) return { topics: skills.map(sk => sk.slug) };
    const ts = [...B.sel];
    // ponytail: the server takes at most 120 templates; a bigger partial pick widens to its skills
    if (ts.length > 120) return { topics: skills.map(sk => sk.slug) };
    return { templates: ts };
  }
  function body(extra = {}) {
    const st = B.st;
    const b = Object.assign({ subject: 'math', source: B.source || 'builder' }, selectionBody());
    if (B.presetBody) Object.assign(b, B.presetBody);
    b.count = st.box ? null : st.count;
    if (st.box) b.box = st.box;
    b.pool = st.pool;
    if (['seen', 'marked', 'saved'].includes(st.pool)) b.exact = !!st.exact;
    if (st.pool === 'seen') { b.result = st.result; b.from = st.from; }
    b.zone = st.zone;
    if (standard()) Object.assign(b, { tiers: st.tiers, adaptive: st.adaptive && st.order !== 'ramp', tier_mix: st.tier_mix, levels: st.levels, unmeasured: st.unmeasured });
    b.formats = st.formats;
    if (st.has.length) b.has = st.has;
    const endless = b.count === null;
    b.timing = endless && st.timing === 'pace' ? 'off' : st.timing;
    if (b.timing === 'custom') b.minutes = st.minutes;
    Object.assign(b, { feedback: st.feedback, repairs: st.feedback === 'end' && st.repairs === 'next' ? 'end' : st.repairs, final_round: st.final_round,
      review_mix: st.review_mix, review_from: st.review_from, words_mix: st.words_mix, order: endless && st.order === 'ramp' ? 'mixed' : st.order,
      mix: st.mix, hints: st.hints, cover: st.cover, worked_first: st.worked_first, two_passes: st.two_passes });
    return Object.assign(b, extra);
  }

  /* ---------------------------------------------------------------- preview */
  let pvT = 0, pvN = 0;
  function preview() {
    clearTimeout(pvT);
    paintBar();
    pvT = setTimeout(async () => {
      const k = ++pvN;
      if (!B.bank || B.subject !== 'math') return;
      let p = null;
      if (!B.sel.size && !B.presetBody) p = { servable: false, reason: 'no_templates', pools: (B.preview && B.preview.pools) || B.bank.counts };
      else {
        try { p = await UI.api('/drill/preview', { method: 'POST', body: body(), quiet: true }); }
        catch (e) { p = { servable: false, reason: e.detail && e.detail.reason ? e.detail.reason : e.offline ? 'offline' : (e.detail && e.detail.field ? `${e.detail.field}: ${e.detail.reason}` : 'unavailable') }; }
      }
      if (k !== pvN) return;
      B.preview = p;
      paintPools(); paintBar(); paintHelpers();
    }, 200);
  }

  /* ---------------------------------------------------------------- page header */
  function paintHead() {
    const b = B.bank, t = b.totals || {};
    $('#meta').textContent = `${t.skills} skills · ${t.types} question types · unlimited questions, never repeated`;
    const pts = $('#points');
    const g = b.gains;
    pts.replaceChildren();
    if (g && (g.total || g.points)) pts.append(h('a', { href: '/results/', class: 'qlink', text: `${g.range ? `Math ${g.range} · ` : ''}≈ ${Math.round(g.total || g.points)} points on the table` }));
    pts.hidden = !pts.childNodes.length;
    const route = $('#route');
    route.replaceChildren();
    if (b.route && (b.route.text || b.route.line)) {
      route.append(h('span', { text: b.route.text || b.route.line }));
      route.append(h('button', { type: 'button', class: 'btn sm', text: 'Practise the harder module’s mix', onclick: () => applyPreset('route') }));
      route.hidden = false;
    } else route.hidden = true;
    const c = b.counts || {};
    const act = (B.sets && B.sets.active) || [];
    const link = (label, n, href, onClick, dot) => {
      const inner = [dot && n ? h('span', { class: 'dot', 'aria-hidden': 'true' }) : null, h('span', { text: label }), n ? h('span', { class: 'n on', text: `· ${n}` }) : null];
      return href ? h('a', { href }, inner) : h('button', { type: 'button', onclick: onClick }, inner);
    };
    $('#links').replaceChildren(
      link('Mistakes', c.mistakes, '/mistakes/', null, true),
      link('Marked', c.marked, '/mistakes/#marked'),
      link('Saved', c.saved, null, () => { setPool('saved'); $('#settings').scrollIntoView({ behavior: 'smooth', block: 'start' }); }),
      h('button', { type: 'button', onclick: () => $('#sets').scrollIntoView({ behavior: 'smooth' }) }, h('span', { text: 'Your sets' }), act.length ? h('span', { class: 'n on', text: `· ${act.length} in progress` }) : null));
  }
  function paintSubject() {
    const host = $('#subject');
    host.replaceChildren();
    UI.seg(host, [{ value: 'math', label: 'Math' }, { value: 'rw', label: 'Reading & Writing' }], {
      value: B.subject, label: 'Subject',
      onChange: v => { B.subject = v; const u = new URL(location.href); if (v === 'rw') u.searchParams.set('subject', 'rw'); else u.searchParams.delete('subject'); history.replaceState(null, '', u); showSubject(); },
    });
  }
  function showSubject() {
    const math = B.subject === 'math';
    ['#ready', '#presetSec', '#searchSec', '#grid', '#sets'].forEach(s => { const e = $(s); if (e) e.hidden = !math || (s === '#ready' && !$('#ready').childNodes.length); });
    $('#abar').hidden = !math;
    $('#rw').hidden = math;
    if (!math) rwPanel();
  }

  /* ---------------------------------------------------------------- R&W (P15): no dead end */
  let rwBank = null;
  async function rwPanel() {
    const host = $('#rw');
    if (!rwBank) {
      host.replaceChildren(h('div', { class: 'card line' }, UI.skel ? UI.skel(null, 'lines:4') : 'Loading…'));
      try { rwBank = await UI.api('/bank?subject=rw', { quiet: true }); } catch (_) { host.replaceChildren(); UI.cardError(host, () => { rwBank = null; rwPanel(); }, 'The server is not answering.'); return; }
    }
    const b = rwBank;
    const skills = [];
    const off = h('div', { class: 'card line' }, h('h3', { class: 'h2', text: 'Practise official Reading & Writing questions now' }),
      h('p', { class: 'help', text: 'College Board’s own bank, by skill. Our R&W questions come with the R&W bank.' }),
      (b.domains || []).map(d => h('div', { class: 'rwd' }, h('b', { text: d.name }), (d.skills || []).map(s => {
        skills.push(s.name);
        return h('div', { class: 'rws' }, h('span', { text: s.name }), h('a', { class: 'qlink', target: '_blank', rel: 'noopener', href: 'https://satsuitequestionbank.collegeboard.org/digital/search', text: `Official on College Board · ${s.cb_count ?? '—'}` }));
      }))));
    const form = h('form', {});
    const idF = h('input', { class: 'field', id: 'rwId', placeholder: 'A College Board question ID, or paste the question' });
    const skF = h('select', { class: 'field', id: 'rwSkill' }, h('option', { value: '', text: 'Skill' }), skills.map(s => h('option', { value: s, text: s })));
    const leF = h('select', { class: 'field', id: 'rwLetter' }, h('option', { value: '', text: 'The letter you picked' }), ['A', 'B', 'C', 'D'].map(l => h('option', { value: l, text: l })));
    const msg = h('p', { class: 'help', 'aria-live': 'polite' });
    form.append(h('label', { class: 'k', for: 'rwId', text: 'Log a missed R&W question' }), idF, skF, leF, h('button', { type: 'submit', class: 'btn', text: 'Log it' }), msg);
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const v = idF.value.trim();
      if (!v) { msg.textContent = 'Paste an ID or the question first.'; return; }
      const isId = /^[0-9a-f]{8}$/i.test(v);
      try {
        await UI.api('/mistakes/log', { method: 'POST', body: Object.assign({ subject: 'rw', skill: skF.value || null, letter: leF.value || null }, isId ? { cb_id: v } : { text: v }) });
        msg.textContent = 'Logged. It waits in Review’s Outside list for the R&W bank.'; idF.value = '';
      } catch (err) { msg.textContent = `Not logged: ${err.message}`; }
    });
    const w = b.words || {};
    const words = h('div', { class: 'card line' }, h('h3', { class: 'h2', text: 'Words drills ready now' }),
      h('div', { class: 'rws' }, h('span', { text: w.title || `SAT words · ${w.due || 0} due` }), h('a', { class: 'btn sm', href: '/words/', text: 'Start' })),
      h('div', { class: 'rws' }, h('span', { text: `Transitions · ${((w.preview || {}).transitions) ?? ''}`.replace(/ · $/, '') }), h('a', { class: 'btn sm', href: '/words/', text: 'Start' })));
    host.replaceChildren(off, h('div', { class: 'card line' }, form), words,
      h('p', { class: 'help', text: b.note || 'R&W practice questions come with the R&W bank. What you log here is waiting for it.' }));
  }

  /* ---------------------------------------------------------------- banners: resume and shared */
  function paintBanners() {
    const host = $('#banners');
    host.replaceChildren();
    const act = (B.sets && B.sets.active) || [];
    if (act.length) {
      const s = act[0];
      const names = (s.topics || []).map(t => (B.skills.get(t) || {}).name || t).slice(0, 3).join(', ');
      const clock = s.paused ? 'paused' : s.timed && Number.isFinite(s.seconds_left) ? `${UI.mmss(s.seconds_left)} left` : `untimed · ${mmss(s.ms)} so far`;
      const endB = h('button', { type: 'button', class: 'quiet', text: 'End it' });
      endB.addEventListener('click', async () => {
        const ok = await UI.confirm({ title: 'End this set?', text: 'End this set and see its summary?', confirm: 'End set', cancel: 'Cancel' });
        if (!ok) return;
        try { await UI.api(`/drill/${s.id}/finish`, { method: 'POST', body: {} }); location.href = `/practice/session/?id=${encodeURIComponent(s.id)}`; }
        catch (e) { UI.toast(`Couldn’t end it: ${e.message}`); }
      });
      host.append(h('div', { class: 'pr-banner', role: 'region', 'aria-label': 'Set in progress' },
        h('p', { text: `Set in progress · ${names || 'Practice'} · ${s.answered} of ${s.total ?? '∞'} answered · ${clock}` }),
        h('div', { class: 'acts' }, h('a', { class: 'pill sm', href: `/practice/session/?id=${encodeURIComponent(s.id)}`, text: 'Resume' }), endB,
          act.length > 1 ? h('button', { type: 'button', class: 'qlink', text: `+${act.length - 1} more`, onclick: () => { setsTab('active'); $('#sets').scrollIntoView({ behavior: 'smooth' }); } }) : null)));
    }
    const code = url.get('share');
    if (code) sharedBanner(host, code);
    host.hidden = !host.childNodes.length && !code;
  }
  async function sharedBanner(host, code) {
    const box = h('div', { class: 'pr-banner', role: 'region', 'aria-label': 'Shared set' }, h('p', { text: 'Loading the shared set…' }));
    host.append(box); host.hidden = false;
    let s;
    try { s = await UI.api(`/sets/${encodeURIComponent(code)}`, { quiet: true }); }
    catch (e) {
      box.replaceChildren(h('p', { class: 'error', text: e.status === 410 ? 'Whoever shared this set has stopped sharing it.' : 'That shared set does not exist.' }),
        h('div', { class: 'acts' }, h('button', { type: 'button', class: 'quiet', text: 'Dismiss', onclick: () => dismissShare(box) })));
      return;
    }
    const me = B.me || {};
    const name = ((me.profile || me).name || '').trim();
    const show = h('input', { type: 'checkbox', id: 'showName', disabled: name ? null : true });
    const topics = (s.topics || []).map(t => (B.skills.get(t) || {}).name || t).join(', ');
    const fb = { instant: 'answers after each', retry: 'answers after a retry', end: 'answers at the end' }[s.feedback] || 'answers after each';
    const start = h('button', { type: 'button', class: 'pill sm', text: 'Start this set' });
    start.addEventListener('click', async () => {
      start.setAttribute('aria-busy', 'true'); start.textContent = 'Building…';
      try {
        const r = await UI.api(`/sets/${encodeURIComponent(code)}/start`, { method: 'POST', body: { show_name: show.checked } });
        location.href = `/practice/session/?id=${encodeURIComponent(r.id || r.session)}`;
      } catch (e) { start.removeAttribute('aria-busy'); start.textContent = 'Start this set'; UI.toast(e.status === 410 ? 'Whoever shared this set has stopped sharing it.' : `Couldn’t start it: ${e.message}`); }
    });
    box.replaceChildren(
      h('p', {}, h('b', { text: `Shared set · ${plural(s.count || 0, 'question')}` }), topics ? ` · ${topics}` : '', s.timed ? ` · timed ${s.minutes || ''} min` : ' · untimed', ` · ${fb}`),
      h('p', { class: 'meta', text: [s.by ? `from ${s.by}` : null, s.n !== undefined ? `taken by ${s.n}` : null, s.fresh ? 'each taker gets their own twins' : 'the exact questions'].filter(Boolean).join(' · ') }),
      h('label', { class: 'check' }, show, h('span', { text: 'Show my name to the person who shared this' })),
      name ? null : h('p', { class: 'help' }, 'Set a board name on ', h('a', { href: '/me/', text: 'Me' }), ' first.'),
      h('p', { class: 'help', text: 'Uses the sharer’s questions and settings, not yours.' }),
      h('div', { class: 'acts' }, start, h('button', { type: 'button', class: 'quiet', text: 'Dismiss', onclick: () => dismissShare(box) })));
  }
  function dismissShare(box) {
    box.remove();
    const u = new URL(location.href); u.searchParams.delete('share'); history.replaceState(null, '', u);
    $('#banners').hidden = !$('#banners').childNodes.length;
  }

  /* ---------------------------------------------------------------- Ready row (P15) */
  let ready = [];
  async function paintReady() {
    const host = $('#ready');
    const last = ((B.sets && B.sets.recent) || []).find(r => r.kind !== 'challenge');
    let next = [];
    const shell = UI.shellData ? UI.shellData() : null;   // GET /api/next only once the server has it (U1), as the shell does
    if (!(shell && shell.has && !shell.has.next)) try { const r = await UI.api('/next?limit=3', { quiet: true }); next = (Array.isArray(r) ? r : r.items || []).slice(0, 3); } catch (_) { next = []; }
    ready = next.map(x => ({ title: x.title, meta: x.meta || [x.count ? `${x.count} q` : null, x.minutes ? `${Math.round(x.minutes)} min` : null, x.points ? `≈ ${x.points} pts` : null].filter(Boolean).join(' · '),
      why: x.reason || x.why || '', body: x.start || x.body, reason: x.unavailable || null }));
    if (last) ready.push({ title: 'Again: your last set', meta: `${(last.topics || []).map(t => (B.skills.get(t) || {}).short || t).slice(0, 2).join(', ')} · ${last.total ?? last.answered} q`, why: `${last.right}/${last.answered} right`, body: { again: last.id, source: 'builder' } });
    host.replaceChildren();
    if (!ready.length) { host.hidden = true; return; }
    const row = h('div', { class: 'pr-ready' });
    ready.forEach(c => {
      const go = h('button', { type: 'button', class: 'pill sm', text: 'Start' });
      go.addEventListener('click', () => create(c.body, go));
      row.append(h('div', { class: 'pr-card' }, h('b', { text: c.title }), c.meta ? h('span', { class: 'meta', text: c.meta }) : null, c.why ? h('span', { class: 'help', text: c.why }) : null,
        h('div', { class: 'acts' }, c.reason ? h('span', { class: 'help', text: c.reason }) : go,
          c.body && !c.body.again ? h('button', { type: 'button', class: 'quiet', text: 'Edit', onclick: () => { loadBody(c.body); linkNote('Settings from Up next'); } }) : null)));
    });
    host.append(row);
    host.hidden = B.subject !== 'math';
    paintSearchHelp();
  }

  /* ---------------------------------------------------------------- presets and mentor line */
  function presets() {
    const b = B.bank, c = b.counts || {}, seen = c.seen || {};
    const sk = [...B.skills.values()];
    const weak = sk.filter(s => s.answered >= 5).sort((a, z) => (a.mastery || 0) - (z.mastery || 0)).slice(0, 3);
    const gains = sk.filter(s => s.gain).sort((a, z) => z.gain - a.gain).slice(0, 3);
    const f0 = B.me && (B.me.profile || B.me).focus;
    const focus = Array.isArray(f0) ? f0 : typeof f0 === 'string' && f0 ? f0.split(',') : f0 && typeof f0 === 'object' ? Object.keys(f0).filter(k => f0[k]) : [];
    const focusSkills = sk.filter(s => focus.includes(s.domain) || focus.includes(s.slug));
    const untried = sk.filter(s => !s.placed && !s.answered).slice(0, 3);
    const list = [
      { id: 'coach', label: 'Mentor’s pick', about: coachWhy() },
      { id: 'weak', label: 'Weakest 3', why: weak.length < 3 ? 'Needs 5 answers in 3 skills' : null, skills: weak },
      { id: 'focus', label: 'Plan focus', why: focusSkills.length ? null : 'No Focus domain in your plan yet: set one in Plan', skills: focusSkills, href: focusSkills.length ? null : '/plan/' },
      { id: 'full', label: 'Full section mix' },
      { id: 'gains', label: `Biggest gains · ${gains.length || 3} skills`, why: (b.totals.answered || 0) < 30 || !gains.length ? 'Needs 30 answers' : null, skills: gains },
      { id: 'mistakes', label: 'My mistakes', why: c.mistakes ? null : 'No open mistakes yet' },
      { id: 'missed', label: `Missed${seen.missed ? ` · ${seen.missed}` : ''}`, why: seen.missed ? null : 'Nothing missed yet' },
      { id: 'marked', label: 'Marked', why: c.marked ? null : 'Nothing marked yet' },
      { id: 'saved', label: 'Saved', why: c.saved ? null : 'Nothing saved yet' },
      { id: 'due', label: `Due for review${c.review || c.due ? ` · ${c.review || c.due}` : ''}`, why: c.review || c.due ? null : 'Nothing due for review' },
      { id: 'solve', label: 'Solve first · 10' },
      { id: 'probe', label: `Check ${untried.length || 3} skills I haven’t tried`, why: untried.length ? null : 'Every skill has answers', skills: untried },
    ];
    if (b.top_habit) list.push({ id: 'habit', label: `Your top habit · ${b.top_habit.name || b.top_habit.id}` });
    if (b.desmos_way) { const n = allTypes().filter(t => t.desmos).length; list.push({ id: 'desmos', label: `Desmos drills${n ? ` · ${n}` : ''}`, why: n ? null : 'No Desmos-way types yet' }); }
    ((((B.prefs.practice || {}).math) || {}).presets || []).forEach((p, i) => list.push({ id: `mine:${i}`, label: p.name, mine: p }));
    list.push({ id: 'custom', label: 'Custom', inert: true });
    return list;
  }
  function paintPresets() {
    const host = $('#presets');
    host.replaceChildren();
    // decision 7: the chips that can't run yet wait behind More, each with its reason one tap away
    const all = presets(), later = p => (p.why || p.inert) && B.preset !== p.id;
    const nLater = all.filter(later).length;
    const chips = all.filter(p => !later(p)).concat(B.morePresets ? all.filter(later) : []);
    chips.forEach(p => {
      const on = B.preset === p.id;
      const chip = h('button', { type: 'button', class: 'pr-chip', 'aria-pressed': String(on), 'aria-disabled': p.why || p.inert ? 'true' : null, 'data-preset': p.id },
        h('span', { text: p.label }));
      // decision 7: a dimmed chip says why on hover or focus, not in a second line
      const about = p.why || p.about;
      if (about) { chip.setAttribute('aria-description', about); tip(chip, about); }
      if (!p.why && !p.inert) chip.addEventListener('click', () => applyPreset(p.id, p));
      else if (p.href) chip.addEventListener('click', () => { location.href = p.href; });
      host.append(chip);
      if (p.mine) {
        const more = h('button', { type: 'button', class: 'quiet', 'aria-label': `${p.label}: rename or delete`, text: '⋯' });
        UI.menu.bind(more, () => [{ label: 'Rename', onClick: () => renamePreset(+p.id.split(':')[1]) }, { label: 'Delete', onClick: () => deletePreset(+p.id.split(':')[1]) }], { label: p.label });
        host.append(more);
      }
    });
    if (nLater) host.append(h('button', { type: 'button', class: 'quiet', 'aria-expanded': String(!!B.morePresets), 'data-more': '', text: B.morePresets ? 'Fewer presets' : 'More presets',
      onclick: () => { B.morePresets = !B.morePresets; paintPresets(); const m = host.querySelector('[data-more]'); if (m) m.focus(); } }));
    host.append(h('button', { type: 'button', class: 'quiet', text: 'Save as preset', onclick: savePreset }),
      h('button', { type: 'button', class: 'quiet', text: 'Copy link', onclick: () => UI.copyText(deepLink(), { toast: 'Link copied: it opens these settings' }) }),
      h('button', { type: 'button', class: 'quiet', text: 'Reset', onclick: () => { B.st = fromPrefs(B.prefs); B.fromLink = false; applyPreset('coach'); linkNote(null); } }));
    if (!(B.bank.totals || {}).answered) host.append(tip(h('a', { class: 'quiet', href: '/diagnostic/', text: 'Diagnostic' }), 'A starting score in 20 questions'));
  }
  // why the mentor picked these skills: the Mentor's pick chip's tooltip, not a permanent line
  function coachWhy() {
    const b = B.bank;
    if (!b.coach) return null;
    const R = b.coach.reasons || {};
    const bits = (b.coach.topics || []).map(t => {
      const r = R[t] || {}, s = B.skills.get(t) || {}, name = s.name || t;
      if (r.kind === 'mistakes' || r.traps) return `${name}: ${plural(r.traps || 0, 'open mistake')}`;
      if (r.kind === 'weak') return `${name}: weakest, ${UI.masteryWord(r.mastery, s.answered)}, ${pct(r.first_try_rate)} first try`;
      if (r.kind === 'review' && r.since_days) return `${name}: not practised for ${r.since_days} days`;
      if (r.kind === 'focus') return `${name}: in your plan’s focus`;
      if (s.gain) return `${name} ≈ +${Math.round(s.gain)} (${s.per_test ? `${s.per_test} a test, ` : ''}${pct(s.accuracy)} first try)`;
      return null;
    }).filter(Boolean);
    if (bits.length) return bits.join(' · ');
    const d = [...b.domains].sort((a, z) => z.weight - a.weight)[0];
    return d ? `Where the test puts the most questions: ${d.name}, ${Math.round(d.weight * 100)}% of it` : null;
  }
  function applyPreset(id, p) {
    const b = B.bank, st = B.st;
    B.presetBody = null; B.source = null;
    const pickSkills = list => { B.sel.clear(); list.forEach(s => setSkill(s, true)); };
    st.pool = 'new'; st.exact = false; st.box = null;
    if (id === 'coach') { pickSkills((b.coach.topics || []).map(t => B.skills.get(t)).filter(Boolean)); if (b.coach.count) st.count = b.coach.count; }
    else if (id === 'weak' || id === 'focus' || id === 'gains') pickSkills(p.skills);
    else if (id === 'full') { pickSkills([...B.skills.values()]); st.count = 44; st.mix = 'blueprint'; st.order = 'mixed'; }
    else if (id === 'mistakes') { pickSkills([...B.skills.values()].filter(s => (s.traps || []).length || s.open_n)); if (!B.sel.size) pickSkills([...B.skills.values()]); st.pool = 'redo'; }
    else if (id === 'missed') { pickSkills([...B.skills.values()]); st.pool = 'seen'; st.result = 'missed'; st.exact = true; }
    else if (id === 'marked') { pickSkills([...B.skills.values()]); st.pool = 'marked'; st.exact = true; }
    else if (id === 'saved') { pickSkills([...B.skills.values()]); st.pool = 'saved'; st.exact = false; }
    else if (id === 'due') { pickSkills([...B.skills.values()]); st.pool = 'review'; }
    else if (id === 'solve') { if (!B.sel.size) pickSkills((b.coach.topics || []).map(t => B.skills.get(t)).filter(Boolean)); st.cover = 'all'; st.count = 10; }
    else if (id === 'probe') { pickSkills(p.skills); B.source = 'probe'; st.count = 8 * p.skills.length; st.feedback = 'end'; }
    else if (id === 'habit') { pickSkills([...B.skills.values()]); B.source = 'habit'; B.presetBody = { habits: [b.top_habit.id] }; }
    else if (id === 'desmos') { pickSkills([...B.skills.values()]); st.has = ['desmos']; }
    else if (id === 'route') { st.zone = 'off'; st.tier_mix = 'module2_upper'; }
    else if (p && p.mine) { loadBody(p.mine.body); }
    B.preset = id;
    paintAll();
  }
  function markCustom() { if (B.preset !== 'custom') { B.preset = 'custom'; B.source = null; B.presetBody = null; paintPresets(); } }
  async function savePreset() {
    const name = await UI.confirm({ title: 'Save as preset', text: 'These skills and settings become a chip in the preset bar.', confirm: 'Save', input: { label: 'Name', value: '', maxlength: 24 } });
    if (!name) return;
    const pm = Object.assign({}, ((B.prefs.practice || {}).math) || {});
    const list = (pm.presets || []).slice();
    if (list.length >= 8) { UI.toast('You have 8 presets. Delete one first.'); return; }
    list.push({ name: String(name).slice(0, 24), body: body() });
    await putPresets(list);
  }
  async function putPresets(list) {
    const practice = Object.assign({}, B.prefs.practice || {}, { math: Object.assign({}, ((B.prefs.practice || {}).math) || {}, { presets: list }) });
    try { const pr = await UI.prefs.set({ practice }); B.prefs = pr.prefs || B.prefs; paintPresets(); }
    catch (e) { UI.toast(`Not saved: ${e.message}`); }
  }
  async function renamePreset(i) {
    const list = ((((B.prefs.practice || {}).math) || {}).presets || []).slice();
    const name = await UI.confirm({ title: 'Rename preset', confirm: 'Rename', input: { label: 'Name', value: list[i].name, maxlength: 24 } });
    if (!name) return;
    list[i] = Object.assign({}, list[i], { name: String(name).slice(0, 24) });
    putPresets(list);
  }
  function deletePreset(i) { const list = ((((B.prefs.practice || {}).math) || {}).presets || []).slice(); list.splice(i, 1); putPresets(list); }
  function linkNote(text) {
    const el = $('#linkNote');
    el.replaceChildren();
    if (!text) { el.hidden = true; return; }
    el.append(h('span', { text }), h('button', { type: 'button', class: 'quiet', text: 'Use my defaults', onclick: () => { B.fromLink = false; B.st = fromPrefs(B.prefs); applyPreset('coach'); linkNote(null); } }));
    el.hidden = false;
  }

  /* ---------------------------------------------------------------- search and the command line (P15) */
  const norm = s => String(s || '').toLowerCase();
  function matches(q) {
    const words = norm(q).split(/\s+/).filter(Boolean);
    if (!words.length) return null;
    const hit = new Set();
    allTypes().forEach(t => {
      const sk = B.skills.get(t.topic) || {};
      const hay = norm(`${t.name} ${t.about} ${(t.labels || []).join(' ')} ${sk.name} ${t.template}`);
      if (words.every(w => hay.includes(w))) hit.add(t.template);
    });
    return hit;
  }
  let parsed = null;
  function onSearch() {
    const q = $('#q').value;
    B.search = q;
    parsed = null;
    const line = $('#sline');
    line.replaceChildren();
    if (q.trim() && UI.parseSet) {
      try { parsed = UI.parseSet(q, { count: B.st.count ?? 0, types: allTypes().map(t => ({ template: t.template, name: t.name })), source: 'builder' }); } catch (_) { parsed = null; }
    }
    const hits = matches(q);
    paintSearch(hits);
    if (hits) {
      if (hits.size) line.append(h('span', { class: 'mono', text: `${plural(hits.size, 'type')} match` }), h('button', { type: 'button', class: 'btn sm', text: `Select all ${hits.size}`, onclick: () => { hits.forEach(t => B.sel.add(t)); markCustom(); paintSel(); preview(); } }));
      else if (!(parsed && parsed.chips && parsed.chips.length)) line.append(h('span', { class: 'help', text: `No question type matches “${q.trim()}”. Try a skill name.` }));
    }
    if (parsed && parsed.chips && parsed.chips.length) {
      line.append(...parsed.chips.map(c => h('span', { class: 'chipx', text: typeof c === 'string' ? c : c.label || c.text || '' })));
      line.append(h('span', { class: 'meta', text: `→ ${parsed.text || 'a set'} · Enter to start · Shift+Enter applies it below` }));
    }
    if (!q.trim()) paintSearchHelp();
  }
  function paintSearchHelp() {
    const line = $('#sline');
    if (B.search.trim()) return;
    line.replaceChildren();
    if (ready[0]) line.append(h('span', { class: 'help', text: `Enter starts: ${ready[0].title}${ready[0].meta ? ` · ${ready[0].meta}` : ''}` }));
  }
  function paintSearch(hits) {
    document.querySelectorAll('.trow').forEach(r => { r.hidden = !!hits && !hits.has(r.dataset.t); });
    document.querySelectorAll('.srow').forEach(r => {
      const sk = B.skills.get(r.dataset.s);
      const any = !hits || typesOf(sk).some(t => hits.has(t.template));
      r.hidden = !any;
      const panel = r.nextElementSibling;
      if (hits && any && hits.size <= 60) openSkill(sk, true);
      if (panel && panel.classList.contains('spanel')) panel.hidden = !any || !B.open.has(sk.slug);
      const nm = r.querySelector('.sname');
      if (nm) highlight(nm, sk.name, B.search);
    });
    document.querySelectorAll('.trow .tname').forEach(n => highlight(n, (B.byT.get(n.closest('.trow').dataset.t) || {}).name, B.search));
    document.querySelectorAll('.dcard').forEach(c => { c.hidden = !!hits && ![...c.querySelectorAll('.srow')].some(r => !r.hidden); });
  }
  function highlight(el, text, q) {
    const w = norm(q).split(/\s+/).filter(x => x.length > 1);
    el.replaceChildren();
    if (!w.length) { el.textContent = text; return; }
    const low = norm(text);
    let i = 0;
    const spans = [];
    w.forEach(x => { let k = low.indexOf(x); while (k >= 0) { spans.push([k, k + x.length]); k = low.indexOf(x, k + 1); } });
    spans.sort((a, z) => a[0] - z[0]);
    spans.forEach(([a, z]) => { if (a < i) return; el.append(text.slice(i, a), h('mark', { class: 'hit', text: text.slice(a, z) })); i = z; });
    el.append(text.slice(i));
  }
  function searchKeys(e) {
    const f = $('#q');
    if (e.key === 'Escape') { if (f.value) { e.preventDefault(); e.stopPropagation(); f.value = ''; onSearch(); } return; }
    if (e.key === 'ArrowUp' && !f.value) { const hist = ls.get('satf.cmd', []); if (hist.length) { e.preventDefault(); f.value = hist[0]; onSearch(); } return; }
    if (e.key !== 'Enter') return;
    e.preventDefault();
    const v = f.value.trim();
    if (!v) { if (ready[0] && ready[0].body) create(ready[0].body); return; }
    const hist = [v, ...ls.get('satf.cmd', []).filter(x => x !== v)].slice(0, 10);
    ls.set('satf.cmd', hist);
    if (parsed && parsed.body && parsed.chips && parsed.chips.length) {
      if (e.shiftKey) { loadBody(parsed.body); f.value = ''; onSearch(); return; }
      create(Object.assign({ subject: 'math', source: 'builder' }, parsed.body));
    }
  }

  /* ---------------------------------------------------------------- the tree */
  function skillOrder(skills) {
    const by = B.sort || 'test';
    const s = skills.slice();
    const key = {
      points: x => -(x.gain || 0), weak: x => (x.answered ? x.mastery || 0 : 2), mistakes: x => -((x.traps || []).length || x.open_n || 0),
      overdue: x => -(x.due_n || 0), slow: x => -(x.types || []).filter(t => t.slow_right).length, least: x => x.answered || 0,
      recent: x => -(x.last ? new Date(x.last).getTime() : 0),
    }[by];
    if (key) s.sort((a, z) => key(a) - key(z));
    return s;
  }
  let paintExpand = () => {};
  function paintTreeHead() {
    const host = $('#thead');
    host.replaceChildren();
    const count = h('span', { class: 'pr-count', id: 'treeCount' });
    const sort = h('select', { id: 'sort', 'aria-label': 'Sort' });
    const hasPts = [...B.skills.values()].some(s => s.gain);
    [['points', 'Most points'], ['test', 'Test order'], ['weak', 'Weakest first'], ['mistakes', 'Most mistakes'], ['overdue', 'Most overdue'], ['slow', 'Slowest vs budget'], ['least', 'Least practised'], ['recent', 'Recently practised']]
      .filter(([v]) => v !== 'points' || hasPts).forEach(([v, l]) => sort.append(h('option', { value: v, text: l })));
    if (!B.sort) B.sort = hasPts ? 'points' : 'test';
    sort.value = B.sort;
    sort.addEventListener('change', () => { B.sort = sort.value; ls.set('satf.tree.sort', B.sort); paintTree(); });
    const expand = h('button', { type: 'button', class: 'ibtn', id: 'expandAll' });
    const allOpen = () => [...B.skills.values()].every(s => B.open.has(s.slug));
    paintExpand = () => {
      const o = allOpen();
      if (expand.getAttribute('aria-label') === (o ? 'Collapse all' : 'Expand all')) return;
      expand.setAttribute('aria-label', o ? 'Collapse all' : 'Expand all');
      expand.innerHTML = UI.svg(`<path d="${o ? 'M7 4l5 5 5-5M7 20l5-5 5 5' : 'M7 9l5-5 5 5M7 15l5 5 5-5'}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>`, 20);
    };
    tip(expand, () => expand.getAttribute('aria-label'));
    expand.addEventListener('click', () => { const open = !allOpen(); B.skills.forEach(s => (open ? B.open.add(s.slug) : B.open.delete(s.slug))); ls.set('satf.tree.open', [...B.open]); paintTree(); paintExpand(); });
    paintExpand();
    const viewHost = h('div', {});
    UI.seg(viewHost, [{ value: 'skills', label: 'Skills' }, { value: 'map', label: 'Map' }, { value: 'habits', label: 'Habits' }], { value: B.view, label: 'Show', onChange: v => { B.view = v; paintTree(); } });
    host.append(h('div', { class: 'ttl' }, h('h2', { class: 'h2', text: 'Skills' }), count),
      h('div', { class: 'ctl' }, viewHost,
        h('button', { type: 'button', class: 'quiet', text: 'Select all', onclick: () => { B.skills.forEach(s => setSkill(s, true)); markCustom(); paintSel(); preview(); } }),
        h('button', { type: 'button', class: 'quiet', text: 'Clear', onclick: () => { B.sel.clear(); markCustom(); paintSel(); preview(); } }),
        expand, h('label', { class: 'sr', for: 'sort', text: 'Sort' }), sort));
    const jump = $('#jump');
    jump.onclick = () => $('#settings').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function paintTree() {
    const host = $('#treeBody');
    host.classList.remove('skel-tree');
    host.replaceChildren();
    if (B.view === 'map') return paintMap(host);
    if (B.view === 'habits') return paintHabits(host);
    B.bank.domains.forEach(d => host.append(domainCard(d)));
    paintSel(); paintAvail();
    if (B.search) paintSearch(matches(B.search));
  }
  function tri(label, onClick) {
    const b = h('button', { type: 'button', class: 'tri', role: 'checkbox', 'aria-checked': 'false', 'aria-label': label });
    b.addEventListener('click', e => { e.stopPropagation(); onClick(b.getAttribute('aria-checked') !== 'true'); });
    b.addEventListener('pointerdown', e => e.stopPropagation());
    return b;
  }
  const chev = (label, open) => h('button', { type: 'button', class: 'chev', 'aria-label': label, 'aria-expanded': String(open), html: UI.svg(UI.ICON.chev, 18) });
  // a small orange count, only when something is open (decision 7)
  function openBadge(n) {
    if (!n) return null;
    const b = h('span', { class: 'obadge' }, String(n), h('span', { class: 'sr', text: ` open ${n === 1 ? 'mistake' : 'mistakes'}` }));
    return tip(b, plural(n, 'open mistake'));
  }
  const factLines = lines => h('div', { class: 'facts' }, ...lines.map(l => l.filter(Boolean)).filter(l => l.length).map(l => h('p', { text: l.join(' · ') })));
  function domainCard(d) {
    const open = !B.closed.has(d.name);
    const card = h('section', { class: 'dcard', 'data-d': d.name });
    const skills = skillOrder(d.skills);
    const tb = tri(`Select every skill in ${d.name}`, on => { skills.forEach(s => setSkill(s, on)); markCustom(); paintSel(); preview(); });
    const ch = chev(`Show or hide ${d.name}`, open);
    const traps = d.skills.reduce((a, s) => a + ((s.traps || []).length || s.open_n || 0), 0);
    // the name, what is picked and its share of the test; the rest only once it says something
    const facts = [
      d.answered ? mbar(d.mastery, d.answered) : null,
      d.answered ? h('span', { text: `${d.answered} answered · ${pct(d.right / Math.max(1, d.answered))} first try` }) : null,
      d.gain ? h('span', { text: `≈ +${Math.round(d.gain)} on the table` }) : null,
      d.due_n ? h('span', { text: `${d.due_n} due for review` }) : null,
      d.ready_n ? h('span', { text: `${d.ready_n} of ${d.types_n} types ready` }) : null,
    ].filter(Boolean);
    const head = h('div', { class: 'dhead', role: 'button', tabindex: '0', 'aria-expanded': String(open) },
      tb, h('span', { class: 'dname' }, h('span', { text: d.name }), h('span', { class: 'dsub', text: `~${Math.round(d.weight * 44)} of 44 on the test` })),
      h('span', { class: 'dright' }, openBadge(traps), h('span', { class: 'dsel', 'data-dsel': d.name })),
      facts.length ? h('span', { class: 'dline' }, facts) : null,
      ch);
    const bodyEl = h('div', { class: 'dbody', hidden: !open });
    const toggle = () => { const o = bodyEl.hidden; bodyEl.hidden = !o; head.setAttribute('aria-expanded', String(o)); ch.setAttribute('aria-expanded', String(o)); o ? B.closed.delete(d.name) : B.closed.add(d.name); ls.set('satf.tree.closed', [...B.closed]); };
    head.addEventListener('click', e => { if (!e.target.closest('.tri')) toggle(); });
    head.addEventListener('keydown', e => { if (e.target === head && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); toggle(); } });
    card._tri = tb;
    skills.forEach(s => { const r = skillRow(s); bodyEl.append(r, r._panel); });
    card.append(head, bodyEl);
    return card;
  }
  let paint = null;
  addEventListener('pointerup', () => { paint = null; });
  // the row: checkbox, name, and once started one mastery word; open mistakes only above 0. The rest is in the panel.
  function skillRow(s) {
    const open = B.open.has(s.slug);
    const tb = tri(`Select ${s.name}`, on => { setSkill(s, on); markCustom(); paintSel(); preview(); });
    const ch = chev('Show stats and question types', open);
    const types = typesOf(s);
    const traps = (s.traps || []).length || s.open_n || 0;
    const row = h('div', { class: 'srow', 'data-s': s.slug, tabindex: '0', 'aria-expanded': String(open) },
      tb, h('div', { class: 'nm' }, h('div', { class: 'sname', text: s.name }), h('div', { class: 'reason', 'data-reason': '' })),
      h('span', { class: 'sright' }, s.answered ? mbar(s.mastery, s.answered) : null, openBadge(traps)),
      ch);
    const panel = h('div', { class: 'spanel', hidden: !open, 'data-panel': s.slug });
    row._panel = panel; row._tri = tb;
    if (open) fillPanel(s, panel);
    const toggleSel = () => { setSkill(s, selOf(s) !== types.length); markCustom(); paintSel(); preview(); };
    row.addEventListener('click', e => {
      if (e.target.closest('.chev')) { openSkill(s, !B.open.has(s.slug)); return; }
      if (e.target.closest('.tri')) return;
      if (paint && paint.moved) return;
      toggleSel();
    });
    row.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse' || e.target.closest('.chev, .tri')) return; paint = { on: selOf(s) !== types.length, moved: false, start: s.slug }; });
    row.addEventListener('pointerenter', () => {
      if (!paint || paint.start === s.slug && !paint.moved) return;
      if (!paint.moved) { paint.moved = true; setSkill(B.skills.get(paint.start), paint.on); }
      setSkill(s, paint.on); markCustom(); paintSel(); preview();
    });
    row.addEventListener('keydown', e => {
      if (e.target !== row) return;
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); toggleSel(); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); openSkill(s, true); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); openSkill(s, false); }
    });
    return row;
  }
  function openSkill(s, open) {
    const row = document.querySelector(`.srow[data-s="${s.slug}"]`);
    if (!row) return;
    open ? B.open.add(s.slug) : B.open.delete(s.slug);
    ls.set('satf.tree.open', [...B.open]);
    row.setAttribute('aria-expanded', String(open));
    row.querySelector('.chev').setAttribute('aria-expanded', String(open));
    const panel = row._panel;
    if (open && !panel.childNodes.length) { fillPanel(s, panel); paintSel(); paintAvail(); if (B.search) paintSearch(matches(B.search)); }
    panel.hidden = !open;
    paintCount(); paintExpand();
  }
  function fillPanel(s, panel) {
    const types = typesOf(s);
    const bt = s.by_tier || {};
    const tierN = d => types.filter(t => (t.tiers || []).includes(d)).length;
    const grid = types.filter(t => t.formats.includes('spr')).length;
    const held = s.mastery >= UI.STRONG && s.answered ? (s.held_after ? `held after ${s.held_after} days` : 'not yet tested after a gap') : null;
    panel.append(factLines([
      [plural(types.length, 'type'), ...TIERS.map(d => (tierN(d) ? `${TIER_WORD[d]} ${tierN(d)}` : null)), grid ? `${grid} grid-in` : null,
        s.crowd_rate !== null && s.crowd_rate !== undefined ? `everyone ${pct(s.crowd_rate)} first try` : null],
      s.answered ? [`${s.answered} answered · ${pct(s.accuracy ?? s.right / Math.max(1, s.answered))} first try`, s.last ? `practised ${ago(s.last)}` : null,
        ...TIERS.filter(d => (bt[d] || [0, 0])[1]).map(d => `${TIER_WORD[d]} ${bt[d][0]}/${bt[d][1]}`), s.avg_ms ? `average ${mmss(s.avg_ms)} a question` : null] : [],
      [s.due_n ? `${s.due_n} due for review` : null, held, s.fluent_n ? `Fluent ${s.fluent_n} of ${types.length}` : null, s.solve_first ? `solve-first ${pct(s.solve_first)}` : null,
        s.sure_rate && s.sure_rate.n ? `Sure-accuracy ${pct(s.sure_rate.rate)} (${s.sure_rate.n})` : null,
        s.calc_split ? `With Desmos ${pct(s.calc_split.with)} (${s.calc_split.with_n ?? ''}) · without ${pct(s.calc_split.without)} (${s.calc_split.without_n ?? ''})` : null],
      s.gain ? [`≈ +${Math.round(s.gain)} points on the table`, `about ${s.per_test ?? '—'} of 44 on the test`, s.to_strong ? `you miss ~${s.to_strong}` : null]
        : [s.per_test ? `about ${s.per_test} of 44 on the test` : null],
    ]));
    const traps = s.traps || [];
    if (traps.length) {
      panel.append(h('h4', { text: 'Open mistakes in this skill' }), ...traps.map(t => h('div', { class: 'omis' },
        h('span', {}, h('span', { class: 'dot', 'aria-hidden': 'true' }), ` ${cap(t.label)} · ${(B.byT.get(t.template) || {}).name || t.template} · ${plural(t.owed ?? 2, 'clean answer')} left`),
        h('button', { type: 'button', class: 'quiet', text: 'Fix', onclick: () => create({ subject: 'math', source: 'mistakes', pool: 'redo', templates: [t.template] }) }))));
    }
    panel.append(h('div', { class: 'btns' },
      h('button', { type: 'button', class: 'btn', text: `Finish ${s.short || s.name} · ${Math.min(40, types.length * 2)} questions`, onclick: () => create({ subject: 'math', source: 'finish', topics: [s.slug] }) }),
      h('button', { type: 'button', class: 'btn', text: 'Check my level · 8 questions', onclick: () => create({ subject: 'math', source: 'probe', topics: [s.slug], count: 8 }) }),
      h('button', { type: 'button', class: 'btn', text: 'Mix it up · 8', onclick: () => create({ subject: 'math', source: 'mixup', order: 'mixup', topics: [s.slug], count: 8 }) }),
      s.cb_count ? h('a', { class: 'btn', target: '_blank', rel: 'noopener', href: 'https://satsuitequestionbank.collegeboard.org/digital/search', text: `Official questions on College Board · ${s.cb_count}` }) : null));
    const labels = (s.labels || []).length > 1 ? s.labels : [{ label: null, templates: types.map(t => t.template) }];
    const tt = h('div', { class: 'ttypes' });
    labels.forEach(l => {
      const list = l.templates.map(t => B.byT.get(t)).filter(Boolean);
      if (!list.length) return;
      if (l.label && list.length > 1) {        // a one-type group's header would only repeat its row
        const lt = tri(`Select every ${l.label} type`, on => { list.forEach(t => (on ? B.sel.add(t.template) : B.sel.delete(t.template))); markCustom(); paintSel(); preview(); });
        lt.dataset.group = l.templates.join(' ');
        const ready = list.filter(t => t.state === 'ready').length, open = list.filter(t => (t.traps || []).length).length;
        tt.append(h('div', { class: 'lhead' }, lt, h('span', { text: `${cap(l.label)} · ${plural(list.length, 'type')}` }),
          ready || open ? h('span', { class: 'meta', text: [ready ? `${ready} ready` : null, open ? `${open} open` : null].filter(Boolean).join(' · ') }) : null));
      }
      list.forEach(t => tt.append(typeRow(t)));
    });
    panel.append(tt);
  }
  function typeRow(t) {
    const tb = tri(`Select ${t.name}`, on => { on ? B.sel.add(t.template) : B.sel.delete(t.template); markCustom(); paintSel(); preview(); });
    const lv = Object.values(t.levels || {});
    const level = lv.length ? lv.map(x => `L${x.level}${x.rough ? ` · rough${x.n ? ` (${x.n})` : ''}` : ''}`).join(' / ') : t.level ? `L${t.level}` : '';
    const traps = (t.traps || []).length;
    const tiers = t.tiers || [];
    const tryB = h('button', { type: 'button', class: 'quiet', text: 'Try one ▾' });
    UI.menu.bind(tryB, () => [
      { label: 'Try one, these settings', onClick: () => create(Object.assign(body(), { templates: [t.template], topics: undefined, count: 1, pool: 'new', box: undefined })) },
      ...tiers.map(d => ({ label: `Try one · ${TIER_WORD[d]}`, onClick: () => create({ subject: 'math', source: 'builder', templates: [t.template], count: 1, zone: 'off', tiers: [d] }) })),
      ...(t.formats.includes('spr') && t.formats.includes('mcq') ? [{ label: 'Try one · as a grid-in', onClick: () => create({ subject: 'math', source: 'builder', templates: [t.template], count: 1, formats: ['spr'] }) }] : []),
    ], { label: `Try ${t.name}` });
    const more = h('button', { type: 'button', class: 'quiet', 'aria-label': `More for ${t.name}`, text: '⋯' });
    UI.menu.bind(more, () => [
      { label: 'See the traps', onClick: () => traps_(t) },
      { label: 'Mix it up with look-alikes', disabled: !(t.lookalikes || []).length, onClick: () => create({ subject: 'math', source: 'mixup', order: 'mixup', templates: [t.template, ...(t.lookalikes || [])].slice(0, 6), count: 8 }) },
    ], { label: t.name });
    // what sets this type apart; the defaults (all three tiers, multiple choice, not yet tried) go unsaid
    const chips = [
      tiers.length < 3 ? h('span', { text: `${tiers.map(d => TIER_WORD[d]).join(' + ')} only` }) : null,
      t.formats.includes('spr') ? h('span', { text: t.formats.includes('mcq') ? 'MC + grid-in' : 'Grid-in only' }) : null,
      level ? h('span', { class: 'mono', text: level }) : null,
      Number.isFinite(t.odds) ? h('span', { text: `your odds ~${Math.round(t.odds * 100)}%` }) : null,
      t.answered ? h('span', { text: `${t.right} of ${t.answered} right` }) : null,
      t.crowd && t.crowd.n >= 20 ? h('span', { text: `everyone ${pct(t.crowd.rate)}` }) : null,
      openBadge(traps),
      t.marked ? h('span', { text: `Marked ${t.marked}` }) : null,
      t.state === 'ready' ? h('span', { text: 'Ready' }) : null,
      t.due ? h('span', { text: 'Due today' }) : t.next_return ? h('span', { text: `Back ${UI.date ? UI.date(t.next_return, 'short') : t.next_return}${t.k ? ` · held ${t.k}` : ''}` }) : null,
      t.fluent ? h('span', { text: `Fluent${t.best_ms ? ` · best ${mmss(t.best_ms)}` : ''}` }) : t.slow_right ? h('span', { text: `Slow: right but ${mmss(t.median_ms)} median` }) : null,
      t.desmos ? h('span', { text: 'Desmos way' }) : null,
      t.official ? h('span', { text: `Built from ${plural(t.official, 'official question')}` }) : null,
      t.type_note ? tip(h('span', { text: '✎ your rule' }), t.type_note) : null,
    ].filter(Boolean);
    const row = h('div', { class: 'trow', 'data-t': t.template }, tb,
      h('div', { class: 'tmain' }, h('span', { class: 'tname', text: t.name }), t.about ? h('span', { class: 'tabout', text: t.about }) : null,
        chips.length ? h('span', { class: 'tchips' }, chips) : null, h('span', { class: 'reason help', 'data-reason': '' })),
      h('div', { class: 'tacts' }, tryB,
        h('button', { type: 'button', class: 'quiet', text: 'Learn', 'aria-label': `Learn ${t.name}`, onclick: () => create({ subject: 'math', source: 'learn', templates: [t.template] }) }), more));
    row._tri = tb;
    return row;
  }
  async function traps_(t) {
    let list = [];
    try { const cat = await UI.types(); const x = (cat.list || []).find(y => y.template === t.template); list = (x && (x.mistakes || x.traps)) || []; } catch (_) {}
    UI.sheet({ title: `${t.name}: the traps`, size: 'm', body: b => {
      b.append(h('p', { class: 'help', text: t.about || '' }));
      if (!list.length) b.append(h('p', { text: 'Its wrong choices are near values, not named traps.' }));
      else b.append(h('ul', {}, list.map(m => h('li', { text: cap(typeof m === 'string' ? m : m.label || m.reason || '') }))));
    }, actions: [{ label: 'Practise this type', primary: true, onClick: () => { create({ subject: 'math', source: 'builder', templates: [t.template], count: 5 }); } }, { label: 'Close', quiet: true }] });
  }
  function paintSel() {
    let skillsN = 0;
    B.bank.domains.forEach(d => {
      const card = document.querySelector(`.dcard[data-d="${CSS.escape(d.name)}"]`);
      let dn = 0, dof = 0, sOn = 0;
      d.skills.forEach(s => {
        const n = selOf(s), of = typesOf(s).length;
        dn += n; dof += of; if (n) { sOn++; skillsN++; }
        const row = document.querySelector(`.srow[data-s="${s.slug}"]`);
        if (row) row._tri.setAttribute('aria-checked', triOf(n, of));
        if (row && row._panel.childNodes.length) {
          row._panel.querySelectorAll('.trow').forEach(r => r._tri.setAttribute('aria-checked', String(B.sel.has(r.dataset.t))));
          row._panel.querySelectorAll('.lhead .tri').forEach(b => { const ts = b.dataset.group.split(' '); b.setAttribute('aria-checked', triOf(ts.filter(x => B.sel.has(x)).length, ts.length)); });
        }
      });
      if (card) { card._tri.setAttribute('aria-checked', triOf(dn, dof)); const c = card.querySelector('[data-dsel]'); if (c) c.textContent = sOn ? `${sOn} of ${d.skills.length} selected` : plural(d.skills.length, 'skill'); }
    });
    paintCount();
    paintBar();
  }
  // "3 skills"; the type count joins only while a skill is open to show its types
  function paintCount() {
    const c = $('#treeCount');
    if (!c) return;
    const n = selectedSkills().length, anyOpen = B.view === 'skills' && [...B.open].some(k => B.skills.has(k));
    c.textContent = n ? `${plural(n, 'skill')}${anyOpen ? ` · ${plural(B.sel.size, 'type')}` : ''}` : '';
  }
  function paintAvail() {
    B.skills.forEach(s => {
      const row = document.querySelector(`.srow[data-s="${s.slug}"]`);
      if (!row) return;
      const why = whyNot(typesOf(s));
      row.classList.toggle('dim', !!why);
      row.querySelector('[data-reason]').textContent = why ? cap(why) : '';
      row._panel.querySelectorAll('.trow').forEach(r => { const t = B.byT.get(r.dataset.t); const w = whyNot([t]); r.classList.toggle('dim', !!w); r.querySelector('[data-reason]').textContent = w; });
    });
  }
  function paintMap(host) {
    const box = h('div', { class: 'pr-map' });
    box.append(h('p', { class: 'help', text: 'Every question type as a cell: filled when you have met it, ringed when ready. Tap a cell to select it.' }));
    B.bank.domains.forEach(d => d.skills.forEach(s => {
      const r = h('div', { class: 'mrow' }, h('div', { class: 'mh' }, h('span', { text: s.name }), h('span', { class: 'meta', text: `${s.ready_n || 0} of ${typesOf(s).length} ready` })));
      const cells = h('div', { class: 'quick' });
      typesOf(s).forEach(t => cells.append(UI.cell(t.state === 'ready' ? 'correct' : t.state === 'met' ? 'mixed' : 'unanswered', null, {
        label: `${t.name}, ${t.state || 'unmet'}${B.sel.has(t.template) ? ', selected' : ''}`, current: B.sel.has(t.template), size: 18,
        onClick: () => { B.sel.has(t.template) ? B.sel.delete(t.template) : B.sel.add(t.template); markCustom(); preview(); paintTree(); } })));
      r.append(cells);
      box.append(r);
    }));
    host.append(box);
    paintBar();
  }
  function paintHabits(host) {
    const list = B.bank.habits || [];
    const box = h('div', { class: 'pr-habits' });
    if (!list.length) box.append(h('p', { class: 'pr-new', text: 'Habits show up after about 30 answers: the kinds of trap you fall for across skills, and the ones you reliably rule out.' }));
    list.forEach(x => box.append(h('div', { class: 'hrow' }, h('div', {}, h('b', { text: x.name || x.id }), h('p', { class: 'help', text: [x.tell, x.week ? `${x.week} this week` : null, x.here ? `${x.here} in your picks` : null].filter(Boolean).join(' · ') })),
      h('button', { type: 'button', class: 'btn sm', text: 'Drill it', onclick: () => create({ subject: 'math', source: 'habit', habits: [x.id] }) }))));
    host.append(box);
  }

  /* ---------------------------------------------------------------- settings */
  const ctl = {};
  function group(host, label, id, cls) {
    const g = h('div', { class: 'sgrp' + (cls ? ' ' + cls : ''), id: id || null });
    if (label) g.append(h('span', { class: 'k', text: label }));
    host.append(g);
    return g;
  }
  const helpLine = (host, text) => { const p = h('p', { class: 'help', text: text || '' }); host.append(p); return p; };
  function setPool(v) { B.st.pool = v; if (['marked', 'history'].includes(v)) B.st.exact = true; else if (['seen', 'saved'].includes(v)) B.st.exact = false; changed(); paintSettings(); }
  function changed() { markCustom(); savePrefs(); preview(); paintAvail(); paintSel(); }
  // What to practise sits in the panel beside the tree; how the set runs sits in the Settings sheet (decision 7).
  let sheetBody = null;
  function paintSettings() {
    const k = focusKey();
    paintPanel();
    if (sheetBody) paintSheet();
    paintHelpers(); paintFormatHelp(); paintPools();
    refocus(k);
  }
  // a repaint keeps keyboard focus on the same control
  function focusKey() {
    const a = document.activeElement;
    if (!a || !a.closest || !a.closest('#settings, .pr-sheet')) return null;
    if (a.type === 'radio') return `input[name="${a.name}"][value="${a.value}"]`;
    const g = a.closest('.sgrp[id]');
    return g ? [g.id, [...g.querySelectorAll(FOC)].indexOf(a)] : null;
  }
  function refocus(k) {
    if (!k) return;
    const g = typeof k === 'string' ? null : document.getElementById(k[0]);
    const el = typeof k === 'string' ? document.querySelector(k) : g && g.querySelectorAll(FOC)[k[1]];
    if (el && el !== document.activeElement) el.focus({ preventScroll: true });
  }
  function openSettings() {
    if (sheetBody) return;
    const s = UI.sheet({ title: 'Settings', size: 'm', body: b => { sheetBody = h('div', { class: 'pr-sheet' }); b.append(sheetBody); paintSheet(); paintHelpers(); paintFormatHelp(); },
      actions: [{ label: 'Done' }] });
    s.closed.then(() => { sheetBody = null; });
  }
  const lab = (host, text) => host.append(h('span', { class: 'lab', text }));
  function paintPanel() {
    const host = $('#settings');
    const st = B.st;
    host.replaceChildren();
    const grid = h('div', { class: 'sgrid sset' });
    host.append(grid);
    // 1. Questions from
    const g1 = group(grid, 'Questions from', 'sPool', 'wide');
    const P = (B.preview && B.preview.pools) || B.bank.counts || {};
    const seen = P.seen || {};
    const rows = [
      ['new', `New questions`, 'types', P.new, 'Generated for you now. You have never seen any of them.'],
      ['redo', 'Fresh numbers on my open mistakes', 'types', P.mistakes, 'Each type you fell for, twice. Two clean answers close a mistake.'],
      ['checks', 'Check-ins on mistakes you fixed', 'due', P.checks, 'A fixed mistake comes back once to prove it stayed fixed.'],
      ['review', 'Fresh numbers on types due for review', 'types', P.review, forecastText()],
      ['untried', 'Fresh numbers on types I’ve never tried', 'types', P.untried, null],
      ['seen', 'Questions I’ve seen', '', seen.any, null],
      ['marked', 'Marked for review', '', P.marked, 'A marked question you get right here leaves your Marked list, unless you tick Keep marked on it.'],
      ['saved', 'Saved', '', P.saved, 'Questions you saved for good. Twins test the skill; Exactly replays the question.'],
    ];
    const name = 'pool';
    rows.forEach(([v, label, unit, n, helper]) => {
      const off = n === 0 && st.pool !== v;
      const inp = h('input', { type: 'radio', name, value: v, checked: st.pool === v ? true : null, disabled: off ? true : null });
      inp.addEventListener('change', () => setPool(v));
      const row = h('label', { class: 'radio-row' + (off ? ' off' : ''), 'data-pool': v, 'data-unit': unit ? ' ' + unit : '' }, inp,
        h('span', { class: 'rl', text: label }), h('span', { class: 'rn', text: n ? `${n0(n)}${unit ? ' ' + unit : ''}` : '' }));
      g1.append(tip(row, helper));
      if (st.pool === v && ['seen', 'marked', 'saved'].includes(v)) {
        const sub = h('div', { class: 'sub' });
        const how = UI.seg(sub, [{ value: false, label: 'Fresh twins' }, { value: true, label: 'Exactly as they were' }], { value: !!st.exact, label: 'How', onChange: x => { st.exact = x; changed(); } });
        tip(how.btns[0], 'Each one comes back as a twin: the same type and trap, new numbers.');
        tip(how.btns[1], 'The same questions again, exactly as they were.');
        if (v === 'seen') {
          UI.seg(sub, [{ value: 'any', label: 'Any', n: seen.any }, { value: 'missed', label: 'Missed', n: seen.missed }, { value: 'right', label: 'Right', n: seen.right }, { value: 'guessed', label: 'Guessed', n: seen.guessed }],
            { value: st.result, label: 'Result', onChange: x => { st.result = x; changed(); } });
          UI.seg(sub, [{ value: 'both', label: 'Practice and tests' }, { value: 'practice', label: 'Practice' }, { value: 'tests', label: 'Tests' }], { value: st.from, label: 'From', onChange: x => { st.from = x; changed(); } });
        }
        g1.append(sub);
      }
    });
    // 2. Questions
    const g2 = group(grid, 'Questions', 'sCount');
    const cv = st.box ? `b${st.box}` : st.count === null ? 'inf' : [5, 10, 20, 30, 40, 50].includes(st.count) ? st.count : 'other';
    const opts = [5, 10, 20, 30, 40, 50].map(n => ({ value: n, label: String(n) })).concat([{ value: 'inf', label: '∞' }, { value: 'b15', label: '15 min' }, { value: 'b30', label: '30 min' }, { value: 'other', label: 'Other' }]);
    ctl.count = UI.seg(g2, opts, { value: cv, label: 'Questions', onChange: v => {
      if (v === 'other') { other.hidden = false; other.focus(); return; }
      other.hidden = true;
      if (v === 'inf') { st.count = null; st.box = null; } else if (v === 'b15' || v === 'b30') { st.box = +v.slice(1); } else { st.count = v; st.box = null; }
      changed(); paintSettings();
    } });
    const other = h('input', { class: 'field', type: 'number', min: 1, max: 120, value: cv === 'other' ? st.count : '', hidden: cv !== 'other', 'aria-label': 'How many questions (1–120)' });
    other.addEventListener('change', () => { const n = Math.max(1, Math.min(120, Math.round(+other.value || 10))); other.value = n; st.count = n; st.box = null; changed(); });
    other.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); other.dispatchEvent(new Event('change')); start(); } });
    tip(ctl.count.btns.find(b => b._opt.value === 'inf'), 'Endless: stop whenever you like.');
    g2.append(h('div', { class: 'inline' }, other));
    ctl.countHelp = helpLine(g2, '');
    // 3. Difficulty (P11)
    const g3 = group(grid, 'Difficulty', 'sDiff');
    const dz = UI.seg(g3, [{ value: 'forme', label: 'For me' }, { value: 'standard', label: 'Standard' }], { value: standard() ? 'standard' : 'forme', label: 'Difficulty', onChange: v => { st.zone = v === 'standard' ? 'off' : (st._zone || 'stretch'); changed(); paintSettings(); } });
    tip(dz.btns[0], 'Aimed at your odds: chosen from how you’ve done in each skill and how hard each type has been for everyone.');
    tip(dz.btns[1], 'Pick the tiers and levels yourself.');
    if (!standard()) {
      const aim = UI.seg(g3, [{ value: 'warm', label: 'Warm-up' }, { value: 'stretch', label: 'Stretch' }, { value: 'challenge', label: 'Challenge' }], { value: st.zone, label: 'Aim', onChange: v => { st.zone = v; st._zone = v; changed(); paintBar(); } });
      ['80% or more likely right', '60–80% likely right', '35–60% likely right'].forEach((t, i) => tip(aim.btns[i], t));
      const unplaced = selectedSkills().filter(s => !s.placed);
      if (unplaced.length) helpLine(g3, `For me starts after 8 answers in a skill. Not placed yet: ${unplaced.slice(0, 4).map(s => `${s.short || s.name} (${s.to_place ?? 8} to go)`).join(', ')}${unplaced.length > 4 ? ` +${unplaced.length - 4}` : ''}. Those are served like module 1 (7 Easy · 8 Medium · 7 Hard).`);
    } else {
      const tierCount = d => [...B.sel].filter(t => ((B.byT.get(t) || {}).tiers || []).includes(d)).length;
      ctl.tiers = UI.seg(g3, TIERS.map(d => ({ value: d, label: TIER_WORD[d], n: tierCount(d) })), { multi: true, value: st.tiers, label: 'Tiers', onChange: v => {
        if (!v.length) { ctl.tiers.set(st.tiers, true); ctl.tiers.el.classList.remove('shake'); void ctl.tiers.el.offsetWidth; ctl.tiers.el.classList.add('shake'); tierHelp.textContent = 'Keep at least one difficulty'; return; }
        st.tiers = v; tierHelp.textContent = ''; changed();
      } });
      const tierHelp = helpLine(g3, '');
      const lv = h('div', { class: 'lvls', role: 'group', 'aria-label': 'Levels 1 to 7' });
      const lvCount = L => [...B.sel].filter(t => Object.values((B.byT.get(t) || {}).levels || {}).some(x => x.level === L)).length;
      LEVELS.forEach(L => {
        const b = h('button', { type: 'button', 'aria-pressed': String(st.levels.includes(L)), 'data-tier': LEVEL_TIER(L), 'aria-label': `Level ${L}, ${lvCount(L)} types` }, h('span', { text: `L${L}` }), h('small', { text: String(lvCount(L)) }));
        b.addEventListener('click', () => {
          const on = st.levels.includes(L);
          if (on && st.levels.length === 1) { lv.classList.remove('shake'); void lv.offsetWidth; lv.classList.add('shake'); return; }
          st.levels = on ? st.levels.filter(x => x !== L) : [...st.levels, L].sort();
          b.setAttribute('aria-pressed', String(!on)); changed();
        });
        lv.append(b);
      });
      g3.append(lv);
      const rough = allTypes().filter(t => Object.values(t.levels || {}).some(x => x.rough)).length;
      tip(UI.triCheck(g3, { label: `Include rough levels · ${rough}`, checked: st.unmeasured, onChange: v => { st.unmeasured = v; changed(); } }).el,
        'A level is rough until 20 students have answered that type; ratings move with every clean first try.');
      const tmix = UI.seg(g3, [{ value: 'any', label: 'Any' }, { value: 'module1', label: 'Like module 1 (7/8/7)' }, { value: 'module2_upper', label: 'Like the harder module 2 (3/8/11)' }], { value: st.tier_mix, label: 'Mix', onChange: v => { st.tier_mix = v; changed(); } });
      tip(tmix.btns[2], 'Aiming above 580? The harder module 2 is 11 Hard of 22.');
      const ad = UI.switch(g3, { checked: st.adaptive && st.order !== 'ramp', label: 'Adaptive: step up a tier after 2 first-try rights in a skill, down after a miss', disabled: st.order === 'ramp', onChange: v => { st.adaptive = v; changed(); } });
      if (st.order === 'ramp') helpLine(g3, 'Off while Order is Easiest first.');
      void ad;
    }
  }
  function paintSheet() {
    const st = B.st;
    const grid = h('div', { class: 'sset' });
    sheetBody.replaceChildren(grid);
    // 4. Format
    const g4 = group(grid, 'Format', 'sFormat');
    const fv = st.formats.length === 2 ? 'both' : st.formats[0];
    UI.seg(g4, [{ value: 'both', label: 'Both' }, { value: 'mcq', label: 'Multiple choice' }, { value: 'spr', label: 'Grid-in' }], { value: fv, label: 'Format', onChange: v => { st.formats = v === 'both' ? ['mcq', 'spr'] : [v]; changed(); paintFormatHelp(); } });
    ctl.fmtHelp = helpLine(g4, '');
    const selT = () => [...B.sel].map(t => B.byT.get(t)).filter(Boolean);
    const hasBox = (key, label) => UI.triCheck(g4, { label, checked: st.has.includes(key), onChange: v => { st.has = v ? [...st.has, key] : st.has.filter(x => x !== key); changed(); } });
    if (B.bank.desmos_way) hasBox('desmos', `Only types with a Desmos way (${selT().filter(t => t.desmos).length})`);
    hasBox('official', `Only types built from official questions (${allTypes().filter(t => t.official).length} of ${B.byT.size})`);
    // 5. Timing
    const g5 = group(grid, 'Timing', 'sTiming');
    const endless = st.count === null || !!st.box;
    const tm = UI.seg(g5, [{ value: 'off', label: 'Untimed' }, { value: 'pace', label: 'Test pace', disabled: endless, why: endless ? 'An endless set has no length to pace' : null }, { value: 'custom', label: endless && !st.box ? 'Sprint' : 'Custom' }],
      { value: endless && st.timing === 'pace' ? 'off' : st.timing, label: 'Timing', onChange: v => { st.timing = v; changed(); paintSettings(); } });
    tip(tm.btns[0], 'A stopwatch counts up.');
    tip(tm.btns[1], 'Paced to each question’s difficulty, like the test.');
    if (st.timing === 'custom') {
      const m = h('input', { class: 'field', type: 'number', min: 1, max: 180, value: st.minutes, 'aria-label': 'Minutes' });
      m.addEventListener('change', () => { st.minutes = Math.max(1, Math.min(180, Math.round(+m.value || 16))); m.value = st.minutes; changed(); });
      g5.append(h('div', { class: 'inline' }, m, h('span', { class: 'meta', text: endless && !st.box ? 'minutes: as many as you can' : 'minutes' })));
    }
    ctl.timeHelp = helpLine(g5, '');
    if (st.timing !== 'off' || st.box) {
      tip(UI.switch(g5, { checked: st.pace_alert, label: 'Pace alert on each question', onChange: v => { st.pace_alert = v; savePrefs(); } }).el, 'The stopwatch turns amber-deep past that question’s budget.');
      UI.switch(g5, { checked: st.two_passes, label: 'Two passes: offer Skip past 1.5× the budget', onChange: v => { st.two_passes = v; changed(); } });
    }
    // 6. Answers shown
    const g6 = group(grid, 'Answers shown', 'sFeedback', 'wide');
    [['instant', 'After each question', 'The key, your mistake by name and the explanation, right away.'],
      ['retry', 'After I retry', 'Wrong? We name the mistake your answer comes from, not the key. Up to 3 tries; only the first counts.'],
      ['end', 'At the end, like a test', 'No feedback until you finish. Change answers, skip around, Check Your Work.']].forEach(([v, l, help]) => {
      const inp = h('input', { type: 'radio', name: 'feedback', value: v, checked: st.feedback === v ? true : null });
      inp.addEventListener('change', () => { st.feedback = v; if (v === 'end' && st.repairs === 'next') st.repairs = 'end'; changed(); paintSettings(); });
      g6.append(tip(h('label', { class: 'radio-row', 'data-feedback': v }, inp, h('span', { class: 'rl', text: l })), help));
    });
    const sub6 = h('div', { class: 'sub' });
    g6.append(sub6);
    lab(sub6, 'Ask how sure');
    tip(UI.seg(sub6, [{ value: 'ask', label: 'Ask' }, { value: 'off', label: 'Off' }], { value: st.confidence, label: 'Check asks how sure (Sure · Unsure · Guess)', onChange: v => { st.confidence = v; savePrefs(); } }).el,
      'Check asks how sure (Sure · Unsure · Guess). A Guess counts half and opens the explanation.');
    UI.switch(sub6, { checked: st.hints, label: 'Hints before I answer', onChange: v => { st.hints = v; changed(); } });
    lab(sub6, 'Solve before seeing choices');
    tip(UI.seg(sub6, [{ value: 'off', label: 'Off' }, { value: 'hard', label: 'Medium and Hard' }, { value: 'all', label: 'All' }], { value: st.cover, label: 'Solve before seeing choices', onChange: v => { st.cover = v; changed(); } }).el,
      'The options stay covered until you type what you got.');
    UI.switch(sub6, { checked: st.worked_first, label: 'New types: show me one worked first', onChange: v => { st.worked_first = v; changed(); } });
    // 7. After a miss
    const g7 = group(grid, 'After a miss', 'sRepairs');
    const endM = st.feedback === 'end';
    tip(UI.seg(g7, [{ value: 'next', label: 'Next question', disabled: endM, why: endM ? 'In test mode, misses become a Fix set at the end.' : null }, { value: 'later', label: '3 questions later', disabled: endM }, { value: 'end', label: 'At the end' }, { value: 'off', label: 'Off' }],
      { value: st.repairs, label: 'After a miss', onChange: v => { st.repairs = v; changed(); } }).el, 'One like it follows a miss: the same trap, new numbers.');
    UI.triCheck(g7, { label: 'Final round: re-ask what I missed at the end, new numbers', checked: st.final_round, onChange: v => { st.final_round = v; changed(); } });
    // 7a. Mix in reviews (P12)
    const g7a = group(grid, 'Mix in reviews', 'sReviews');
    UI.seg(g7a, [{ value: 'off', label: 'Off' }, { value: 2, label: '2 per set' }, { value: 20, label: '20%' }], { value: st.review_mix, label: 'Mix in reviews', onChange: v => { st.review_mix = v; changed(); } });
    UI.triCheck(g7a, { label: 'Only from the skills I picked', checked: st.review_from === 'picked', onChange: v => { st.review_from = v ? 'picked' : 'all'; changed(); } });
    helpLine(g7a, forecastText());
    lab(g7a, 'Mix in due SAT words');
    tip(UI.seg(g7a, [{ value: 'off', label: 'Off' }, { value: 2, label: '2 per set' }, { value: 'all', label: 'All due' }], { value: st.words_mix, label: 'Mix in due SAT words', onChange: v => { st.words_mix = v; changed(); } }).el,
      'Reviewed at set breaks, filed to Words, never counted in Math.');
    // 8. Order
    const g8 = group(grid, 'Order', 'sOrder');
    const ord = UI.seg(g8, [{ value: 'mixed', label: 'Mixed' }, { value: 'grouped', label: 'Grouped by skill' }, { value: 'ramp', label: 'Easiest first', disabled: endless, why: endless ? 'An endless set has no end to ramp to' : null }, { value: 'mixup', label: 'Mix-up' }],
      { value: st.order, label: 'Order', onChange: v => { st.order = v; changed(); paintSettings(); } });
    ['Never serves 3 questions of one type in a row.', 'One skill at a time.', 'By level where measured, by tier otherwise.', 'Look-alike types interleaved, so you learn which method applies.'].forEach((t, i) => tip(ord.btns[i], t));
    // 9. Spread
    const g9 = group(grid, 'Spread', 'sSpread');
    const oneDomain = new Set(selectedSkills().map(s => s.domain)).size <= 1;
    const spr = UI.seg(g9, [{ value: 'even', label: 'Even across skills' }, { value: 'blueprint', label: 'Like the test', disabled: oneDomain, why: oneDomain ? 'Your pick sits in one domain' : null }],
      { value: oneDomain ? 'even' : st.mix, label: 'Spread', onChange: v => { st.mix = v; changed(); } });
    tip(spr.btns[1], 'Algebra and Advanced Math 35% each, the other two 15%.');
    // 10. Repeats
    const g10 = group(grid, null, 'sRepeats', 'wide');
    g10.append(h('p', { class: 'lock' }, icon('save', 16), h('span', { text: 'Never repeats. Nothing you were shown in a set, a test or the diagnostic comes back, except the exact replays you ask for above. No practice question copies a College Board question.' })));
    // 11. Footer
    const foot = h('div', { class: 'sfoot' }, h('span', { class: 'help', id: 'sfootNote', text: B.foot || (B.fromLink ? 'Settings from the link, not your defaults' : 'Saved as your defaults') }),
      h('button', { type: 'button', class: 'quiet', text: 'Reset to defaults', onclick: () => { B.st = Object.assign({}, DEF); B.fromLink = false; B.foot = null; changed(); paintSettings(); } }),
      h('button', { type: 'button', class: 'btn sm', id: 'worksheet', text: 'Printable worksheet', disabled: $('#start').disabled || null, onclick: worksheet }));
    grid.append(foot);
  }
  function footNote(text) { B.foot = text; const e = $('#sfootNote'); if (e) e.textContent = text; }
  function forecastText() {
    const f = B.bank.forecast || [];
    const c = B.bank.counts || {};
    const sum = l => l.reduce((a, x) => a + (x.fading || 0) + (x.checks || 0), 0);
    const week = sum(f.slice(0, 7)), all = sum(f);
    return [c.review ? `${c.review} due now` : null, week ? `${week} ${c.review ? 'more ' : ''}this week` : null, all > week ? `next 14 days: ${all}` : null].filter(Boolean).join(' · ') || null;
  }
  function paintFormatHelp() {
    if (!ctl.fmtHelp) return;
    const sel = [...B.sel].map(t => B.byT.get(t)).filter(Boolean);
    ctl.fmtHelp.textContent = `${sel.filter(t => t.formats.includes('spr')).length} of ${sel.length} selected types make grid-ins`;
  }
  function paintPools() {
    const P = (B.preview && B.preview.pools) || null;
    if (!P) return;
    const map = { new: P.new, redo: P.mistakes, checks: P.checks, review: P.review, untried: P.untried, seen: (P.seen || {}).any, marked: P.marked, saved: P.saved };
    document.querySelectorAll('#sPool .radio-row').forEach(r => {
      const v = r.dataset.pool, n = map[v];
      const rn = r.querySelector('.rn');
      if (rn) rn.textContent = n ? `${n0(n)}${r.dataset.unit || ''}` : '';
      const off = n === 0 && B.st.pool !== v;
      r.classList.toggle('off', off);
      r.querySelector('input').disabled = off;
    });
  }
  function paintHelpers() {
    const p = B.preview || {};
    const st = B.st;
    // the set's length is in the bar; these say only what the bar does not
    const put = (el, t) => { if (el) { el.textContent = t; el.hidden = !t; } };
    put(ctl.countHelp, st.box ? `about ${p.count || Math.round(st.box * 60 / 95)} questions for you in ${st.box} min` : '');
    put(ctl.timeHelp, st.timing === 'pace' && st.count ? `${p.minutes ? UI.mmss(Math.round(p.minutes * 60)) : '…'} for these ${st.count} · added questions add their time`
      : st.timing === 'off' ? '' : st.count === null && !st.box ? `Sprint: as many as you can in ${st.minutes} min` : `${st.minutes} min for the set`);
  }

  /* ---------------------------------------------------------------- the action bar */
  const FB_WORD = { instant: 'answers after each', retry: 'answers after a retry', end: 'answers at the end' };
  const REP_WORD = { next: 'repairs next', later: 'repairs 3 later', end: 'repairs at the end', off: 'repairs off' };
  const POOL_WORD = { new: 'New questions', redo: 'Open mistakes', checks: 'Check-ins', review: 'Due for review', untried: 'Never tried', seen: 'Seen before', marked: 'Marked', saved: 'Saved' };
  const dur = m => (m < 60 ? `~${Math.max(1, Math.round(m))} min` : `~${Math.round(m / 30) / 2} h`);
  // One line: how many and how long. The rest of the summary is the Settings button's tooltip; the skills are the checkmarks.
  function paintBar() {
    if (!B.bank) return;
    const st = B.st, p = B.preview;
    const skills = selectedSkills();
    const sprint = st.count === null && !st.box && st.timing === 'custom';
    const cnt = st.box ? `${st.box}-minute set` : sprint ? 'Sprint' : st.count === null ? 'Endless' : plural(st.count, 'question');
    const long = st.box ? (p && p.count ? `about ${plural(p.count, 'question')}` : null)
      : sprint || (st.timing === 'custom' && st.count !== null) ? `${st.minutes} min` : st.count !== null && p && p.minutes ? dur(p.minutes) : null;
    $('#l1').textContent = [cnt, long].filter(Boolean).join(' · ');
    const ts = [...B.sel].map(t => B.byT.get(t)).filter(Boolean).filter(fits).length;
    const diff = standard() ? (st.tiers.length === 3 ? 'all levels' : st.tiers.map(d => TIER_WORD[d]).join(' + ')) : `For me: ${{ warm: 'Warm-up', stretch: 'Stretch', challenge: 'Challenge' }[st.zone]}`;
    const fmt = st.formats.length === 2 ? 'both formats' : st.formats[0] === 'spr' ? 'grid-ins only' : 'multiple choice only';
    const gain = skills.reduce((a, s) => a + (s.gain || 0), 0);
    B.sumText = [plural(skills.length, 'skill'), plural(ts, 'type'), diff, fmt, gain ? `works on ≈ +${Math.round(gain)}` : null].filter(Boolean).join(' · ');
    const time = st.timing === 'off' ? 'Untimed' : st.timing === 'pace' ? 'Test pace' : sprint ? `Sprint ${st.minutes} min` : `Timed ${st.minutes} min`;
    B.setText = [time, FB_WORD[st.feedback], REP_WORD[st.repairs], st.final_round ? 'final round on' : null, st.review_mix !== 'off' ? `${st.review_mix === 2 ? '2 reviews' : '20% reviews'} mixed in` : null,
      { mixed: 'mixed', grouped: 'grouped', ramp: 'easiest first', mixup: 'mix-up' }[st.order]].filter(Boolean).join(' · ');
    $('#openSettings').setAttribute('aria-description', B.setText);
    $('#jump').textContent = `${POOL_WORD[st.pool] || 'Questions'} · ${diff} ↓`;
    const startB = $('#start'), reason = $('#reason');
    if (starting) return;
    let why = '';
    if (!B.sel.size && !B.presetBody) why = 'Pick at least one skill';
    else if (!p) why = '';
    else if (!p.servable) why = p.reason === 'offline' ? 'The server is not answering.' : reasonText(p.reason);
    startB.disabled = !!why || !p;
    startB.textContent = p || why ? 'Start practice' : 'Loading…';
    reason.textContent = why;
    reason.hidden = !why;
    const ws = $('#worksheet');
    if (ws) ws.disabled = startB.disabled;
  }

  /* ---------------------------------------------------------------- starting */
  let starting = false;
  async function create(b, btn) {
    if (starting) return;
    starting = true;
    const startB = btn || $('#start');
    const label = startB.textContent;
    startB.setAttribute('aria-busy', 'true'); startB.textContent = 'Building…';
    $('#abarErr').hidden = true;
    try {
      const r = await UI.api('/drill', { method: 'POST', body: b });
      const id = r.id || r.session;
      location.href = `/practice/session/?id=${encodeURIComponent(id)}${b.source === 'worksheet' ? '&print=1' : ''}`;
    } catch (e) {
      starting = false;
      startB.removeAttribute('aria-busy'); startB.textContent = label;
      const msg = e.detail && e.detail.reason ? reasonText(e.detail.reason) : e.message;
      const err = $('#abarErr');
      err.replaceChildren(h('span', { text: `Couldn’t start: ${msg}` }), ' ', h('button', { type: 'button', class: 'quiet', text: 'Try again', onclick: () => create(b, btn) }));
      err.hidden = false;
      paintBar();
    }
  }
  const start = () => { if (!$('#start').disabled) create(body()); };
  const worksheet = () => { if (!$('#start').disabled) create(body({ source: 'worksheet', feedback: 'end', timing: 'off', repairs: 'end', final_round: false })); };

  /* ---------------------------------------------------------------- deep links (1.10) */
  function fromLink() {
    const g = k => url.get(k);
    if (![...url.keys()].some(k => !['share', 'subject', 'search', 'theme'].includes(k))) return false;
    const st = B.st;
    const list = k => (g(k) || '').split(',').map(x => x.trim()).filter(Boolean);
    if (g('skills') || g('types')) {
      B.sel.clear();
      list('skills').forEach(s => { const sk = B.skills.get(s); if (sk) setSkill(sk, true); });
      list('types').forEach(t => { if (B.byT.has(t)) B.sel.add(t); });
    }
    if (g('count')) st.count = g('count') === '0' || g('count') === 'inf' ? null : Math.max(1, Math.min(120, +g('count') || 10));
    if (g('box')) st.box = Math.max(5, Math.min(60, +g('box')));
    if (g('pool')) st.pool = { mistakes: 'redo' }[g('pool')] || g('pool');
    if (g('result')) st.result = g('result');
    if (g('marked') === '1') st.pool = 'marked';
    if (g('from')) st.from = g('from');
    if (g('tiers')) { st.tiers = list('tiers').filter(x => TIERS.includes(x)); st.zone = 'off'; }
    if (g('levels')) { st.levels = list('levels').flatMap(x => { const m = x.split('-').map(Number); return m.length === 2 ? LEVELS.filter(l => l >= m[0] && l <= m[1]) : [m[0]]; }).filter(l => LEVELS.includes(l)); st.zone = 'off'; }
    if (g('unmeasured')) st.unmeasured = g('unmeasured') !== '0';
    if (g('formats')) st.formats = list('formats').filter(x => x === 'mcq' || x === 'spr');
    if (g('timing')) { const t = g('timing'); if (t.startsWith('custom')) { st.timing = 'custom'; st.minutes = +t.split(':')[1] || 16; } else st.timing = t === 'untimed' ? 'off' : t; }
    if (g('feedback')) st.feedback = g('feedback');
    if (g('repairs')) st.repairs = g('repairs') === '0' ? 'off' : g('repairs');
    if (g('order')) st.order = g('order');
    if (g('mix')) st.mix = g('mix');
    if (g('zone')) st.zone = g('zone');
    if (g('tier_mix')) st.tier_mix = g('tier_mix');
    if (g('review_mix')) st.review_mix = g('review_mix') === 'off' ? 'off' : +g('review_mix');
    if (g('final_round')) st.final_round = g('final_round') !== '0';
    if (g('cover')) st.cover = g('cover');
    if (g('has')) st.has = list('has');
    if (g('words_mix')) st.words_mix = g('words_mix') === 'all' ? 'all' : g('words_mix') === 'off' ? 'off' : 2;
    if (g('habits')) { B.source = 'habit'; B.presetBody = { habits: list('habits') }; }
    if (g('rematch')) { B.presetBody = { rematch: g('rematch'), clean: g('clean') === '1' }; B.source = 'rematch'; }
    if (g('cb')) { B.presetBody = { pool: 'official', ids: list('cb') }; B.source = 'official'; }
    ['formats', 'tiers', 'levels'].forEach(k => { if (!st[k].length) st[k] = DEF[k].slice(); });
    return true;
  }
  function loadBody(b) {
    const st = B.st;
    if (b.topics || b.templates) { B.sel.clear(); (b.topics || []).forEach(s => { const sk = B.skills.get(s); if (sk) setSkill(sk, true); }); (b.templates || []).forEach(t => { if (B.byT.has(t)) B.sel.add(t); }); }
    ['pool', 'exact', 'result', 'from', 'zone', 'tiers', 'adaptive', 'tier_mix', 'levels', 'unmeasured', 'formats', 'has', 'timing', 'minutes', 'feedback', 'hints', 'cover', 'worked_first', 'repairs', 'final_round', 'review_mix', 'review_from', 'words_mix', 'order', 'mix', 'two_passes']
      .forEach(k => { if (b[k] !== undefined) st[k] = b[k]; });
    if (b.pool === 'mistakes') st.pool = 'redo';
    if (b.count !== undefined) st.count = b.count;
    st.box = b.box || null;
    B.preset = 'custom';
    paintAll();
  }
  function deepLink() {
    const st = B.st, u = new URL('/practice/', location.origin);
    const sb = selectionBody();
    if (sb.topics) u.searchParams.set('skills', sb.topics.join(',')); else u.searchParams.set('types', sb.templates.join(','));
    u.searchParams.set('subject', 'math');
    u.searchParams.set('count', st.count === null ? '0' : st.count);
    if (st.box) u.searchParams.set('box', st.box);
    u.searchParams.set('pool', st.pool);
    if (st.pool === 'seen') { u.searchParams.set('result', st.result); u.searchParams.set('from', st.from); }
    u.searchParams.set('zone', st.zone);
    if (standard()) { u.searchParams.set('tiers', st.tiers.join(',')); u.searchParams.set('levels', st.levels.join(',')); u.searchParams.set('unmeasured', st.unmeasured ? '1' : '0'); }
    u.searchParams.set('formats', st.formats.join(','));
    u.searchParams.set('timing', st.timing === 'custom' ? `custom:${st.minutes}` : st.timing === 'off' ? 'untimed' : st.timing);
    u.searchParams.set('feedback', st.feedback);
    u.searchParams.set('repairs', st.repairs);
    u.searchParams.set('order', st.order);
    u.searchParams.set('mix', st.mix);
    return u.href;
  }

  /* ---------------------------------------------------------------- Your sets */
  let setsTabV = 'active', setsLimit = 10, setsFilter = { topic: '', kind: '', misses: false };
  function setsTab(v) { setsTabV = v; setsLimit = 10; paintSets(); }
  async function loadSets() {
    try { B.sets = await UI.api('/drill', { quiet: true }); } catch (_) { B.sets = { active: [], recent: [], shared: [], error: true }; }
    try { B.owned = await UI.api('/sets', { quiet: true }); } catch (_) { B.owned = []; }
  }
  const setTitle = r => (r.topics || []).map(t => (B.skills.get(t) || {}).short || (B.skills.get(t) || {}).name || t);
  function paintSets() {
    const host = $('#sets');
    host.replaceChildren(h('h2', { class: 'h2', text: 'Your sets' }));
    if (!B.sets) { host.append(UI.skel(null, 'rows:3')); return; }
    const S = B.sets;
    const owned = (B.owned || []).filter(x => x.kind === 'set' && !x.revoked);
    const recent = (S.recent || []).filter(r => r.answered > 0);
    const tabHost = h('div', {});
    UI.seg(tabHost, [{ value: 'active', label: 'In progress', n: (S.active || []).length }, { value: 'recent', label: 'Finished', n: recent.length }, { value: 'shared', label: 'Shared by me', n: owned.length }, { value: 'official', label: 'Official questions you brought', n: (S.official || []).length }],
      { value: setsTabV, label: 'Your sets', onChange: setsTab });
    host.append(tabHost);
    if (S.error) { UI.cardError(host, async () => { await loadSets(); paintSets(); }, 'Your sets didn’t load.'); return; }
    let rows = [];
    if (setsTabV === 'active') rows = S.active || [];
    else if (setsTabV === 'recent') {
      const f = h('div', { class: 'filters' });
      const skSel = h('select', { 'aria-label': 'Skill' }, h('option', { value: '', text: 'All skills' }), [...B.skills.values()].map(s => h('option', { value: s.slug, text: s.name, selected: setsFilter.topic === s.slug ? true : null })));
      const kind = h('select', { 'aria-label': 'Kind' }, [['', 'All'], ['drill', 'Practice'], ['shared', 'Shared with me'], ['challenge', 'Challenge']].map(([v, l]) => h('option', { value: v, text: l, selected: setsFilter.kind === v ? true : null })));
      const res = h('select', { 'aria-label': 'Result' }, [['', 'All'], ['1', 'With misses']].map(([v, l]) => h('option', { value: v, text: l, selected: (setsFilter.misses ? '1' : '') === v ? true : null })));
      [skSel, kind, res].forEach(x => x.addEventListener('change', () => { setsFilter = { topic: skSel.value, kind: kind.value, misses: res.value === '1' }; paintSets(); }));
      f.append(skSel, kind, res);
      host.append(f);
      rows = recent.filter(r => (!setsFilter.topic || (r.topics || []).includes(setsFilter.topic)) && (!setsFilter.kind || (setsFilter.kind === 'shared' ? r.source === 'shared' : r.kind === setsFilter.kind))
        && (!setsFilter.misses || r.right < r.answered));
    } else if (setsTabV === 'shared') rows = owned;
    else rows = S.official || [];
    const empty = { active: 'Nothing in progress. A set you leave halfway waits here, on any device with your code.', recent: 'Sets you finish show up here, with their review.',
      shared: 'Share a finished set so friends each get their own twins of it, then see how they did.', official: 'College Board questions you log from Review show up here, each with twins to practise.' }[setsTabV];
    if (!rows.length) { host.append(h('p', { class: 'help', text: empty })); return; }
    rows.slice(0, setsLimit).forEach(r => host.append(setsTabV === 'shared' ? ownedRow(r) : setRow(r)));
    if (rows.length > setsLimit) host.append(h('button', { type: 'button', class: 'quiet', text: `Show ${Math.min(20, rows.length - setsLimit)} more`, onclick: () => { setsLimit += 20; paintSets(); } }));
  }
  function setRow(r) {
    const chips = setTitle(r);
    const ch = r.kind === 'challenge' || r.kind === 'contest';
    const mode = [r.timed ? `Timed${r.seconds_left !== null && r.seconds_left !== undefined ? '' : ''}` : 'Untimed', { instant: 'After each', retry: 'Retry', end: 'Test mode' }[r.feedback] || ''].filter(Boolean).join(' · ');
    const acts = h('div', { class: 'acts' });
    const go = `/practice/session/?id=${encodeURIComponent(r.id)}`;
    if (!r.finished) {
      acts.append(h('a', { class: 'pill sm', href: go, text: 'Resume' }), h('button', { type: 'button', class: 'quiet', text: 'End', onclick: async () => {
        if (!(await UI.confirm({ title: 'End this set?', text: 'End this set and see its summary?', confirm: 'End set' }))) return;
        try { await UI.api(`/drill/${r.id}/finish`, { method: 'POST', body: {} }); location.href = go; } catch (e) { UI.toast(`Couldn’t end it: ${e.message}`); }
      } }));
    } else if (ch) acts.append(h('a', { class: 'quiet', href: '/challenge/', text: 'Challenge' }), h('a', { class: 'quiet', href: go, text: 'Review' }));
    else {
      acts.append(h('a', { class: 'quiet', href: go, text: 'Review' }),
        h('button', { type: 'button', class: 'quiet', text: 'Rematch', onclick: () => confirmCopy(r.id, 'rematch') }),
        h('button', { type: 'button', class: 'quiet', text: 'Retake exact', onclick: () => confirmCopy(r.id, 'retake') }),
        h('button', { type: 'button', class: 'quiet', text: 'Same settings', onclick: () => create({ again: r.id, source: 'builder', subject: 'math' }) }),
        h('button', { type: 'button', class: 'quiet', text: 'Share', onclick: () => shareSheet(r.id) }),
        h('a', { class: 'quiet', href: `${go}&print=1`, text: 'Print' }));
    }
    return h('div', { class: 'setrow' },
      h('span', { class: 'mono', text: `${ch ? '🏆 ' : ''}${when(r.started)}` }),
      h('span', { class: 'skills' }, chips.slice(0, 3).map(c => h('span', { text: c })), chips.length > 3 ? h('span', { text: `+${chips.length - 3}` }) : null),
      h('span', { class: 'meta', text: mode }),
      h('span', { class: 'mono', text: r.total ? `${r.answered} / ${r.total}` : `${r.answered} answered` }),
      h('span', { class: 'mono', text: r.answered ? `${r.right} right · ${pct(r.right / r.answered)}` : '—' }),
      h('span', { class: 'mono', text: mmss(r.ms) }), acts);
  }
  async function confirmCopy(sid, kind) {
    const retake = kind === 'retake';
    const clean = h('input', { type: 'checkbox', checked: retake ? true : null });
    UI.sheet({ title: retake ? 'Retake these exact questions?' : 'Rematch: same types, new numbers?', size: 's', body: b => {
      b.append(h('p', { text: retake ? 'Starts a new copy of this set with the same questions. It tests memory as much as skill. This one stays in your history.' : 'The same types in the same order, with new numbers. We compare the two question by question.' }),
        h('label', { class: 'check' }, clean, h('span', { text: 'Start clean: hide my highlights, notes, strikes and rules on this copy' })));
    }, actions: [{ label: 'Cancel', quiet: true }, { label: retake ? 'Retake' : 'Rematch', primary: true, onClick: () => { create({ subject: 'math', source: retake ? 'builder' : 'rematch', [kind]: sid, clean: clean.checked }); } }] });
  }
  function shareSheet(sid) {
    let exact = false;
    UI.sheet({ title: 'Share this set', size: 's', body: b => {
      UI.seg(b, [{ value: false, label: 'Twins for each person' }, { value: true, label: 'Exactly these questions' }], { value: false, label: 'What they get', onChange: v => { exact = v; } });
      b.append(h('p', { class: 'help', text: 'Twins: each friend gets their own numbers on the same types in the same order, so answers can’t be passed around. You see how they did per question.' }),
        h('p', { class: 'help' }, 'Want to race on the clock? ', h('a', { href: '/compete/', text: 'Race friends on this instead' }), '.'));
    }, actions: [{ label: 'Cancel', quiet: true }, { label: 'Copy link', primary: true, onClick: async () => {
      try {
        const r = await UI.api('/sets', { method: 'POST', body: { kind: 'set', session: sid, cfg: { fresh: !exact } } });
        UI.copyText(r.url || `${location.origin}/practice/?share=${r.code}`, { toast: exact ? 'Link copied: friends get these exact questions' : 'Link copied: each friend gets their own twins' });
        loadSets().then(paintSets);
      } catch (e) { UI.toast(`Couldn’t share it: ${e.message}`); return false; }
    } }] });
  }
  function ownedRow(r) {
    const link = r.url || `${location.origin}/practice/?share=${r.code}`;
    return h('div', { class: 'setrow' },
      h('span', { class: 'mono', text: when(r.created) }),
      h('span', { text: r.title || `${plural(r.count || 0, 'question')}` }),
      h('span', { class: 'meta', text: r.fresh ? 'Twins for each person' : 'Exact questions' }),
      h('span', { class: 'mono', text: `Opened ${r.opened || 0}` }), h('span', {}), h('span', {}),
      h('div', { class: 'acts' },
        h('button', { type: 'button', class: 'quiet', text: 'Results', onclick: () => sharedResults(r.code) }),
        h('button', { type: 'button', class: 'quiet', text: 'Copy link', onclick: () => UI.copyText(link, { toast: 'Link copied' }) }),
        h('button', { type: 'button', class: 'quiet', text: 'Stop sharing', onclick: async () => {
          if (!(await UI.confirm({ title: 'Stop sharing?', text: 'The link stops working for everyone. Results stay yours.', confirm: 'Stop sharing', destructive: true }))) return;
          try { await UI.api(`/sets/${r.code}`, { method: 'DELETE' }); await loadSets(); paintSets(); } catch (e) { UI.toast(`Couldn’t stop it: ${e.message}`); }
        } })));
  }
  async function sharedResults(code) {
    let d;
    try { d = await UI.api(`/sets/${code}/results`); } catch (e) { UI.toast(`Results didn’t load: ${e.message}`); return; }
    UI.sheet({ title: d.title || 'Shared set results', size: 'l', body: b => {
      const takers = d.takers || [];
      if (!takers.length) { b.append(h('p', { text: 'Nobody has taken this set yet. Copy the link to send it.' })); return; }
      const tiles = h('div', { class: 'tiles' });
      UI.tile(tiles, { label: 'Taken', value: takers.length });
      UI.tile(tiles, { label: 'Average', value: d.avg_right !== undefined && d.avg_right !== null ? `${(+d.avg_right).toFixed(1)} / ${d.count}` : '—' });
      UI.tile(tiles, { label: 'Median time', value: d.median_ms ? mmss(d.median_ms) : '—' });
      b.append(tiles);
      UI.table(b, [{ key: 'n', label: '#', num: true }, { key: 'type_name', label: 'Type' }, { key: 'difficulty', label: 'Difficulty' },
        { key: 'right', label: 'Right', render: q => `${q.right}/${q.asked}` },
        { key: 'top', label: 'Most common wrong answer', render: q => (q.top_wrong ? `${cap(q.top_wrong.reason || q.top_wrong.norm || '')} (${q.top_wrong.count})` : '—') }], d.questions || [], { compact: true, label: 'Per question' });
      UI.table(b, [{ key: 'name', label: 'Taker', render: (t, i) => t.name || `Student ${i + 1}` }, { key: 'right', label: 'Score', render: t => `${t.right} / ${t.asked}` }, { key: 'ms', label: 'Time', render: t => mmss(t.ms) }],
        takers.map((t, i) => Object.assign({ _i: i }, t)).map(t => Object.assign(t, { name: t.name || `Student ${t._i + 1}` })), { compact: true, label: 'Takers' });
    } });
  }

  /* ---------------------------------------------------------------- loading, errors, painting */
  function paintAll() { paintPresets(); paintTree(); paintSettings(); paintSel(); paintBar(); preview(); }
  function skeleton() {
    const host = $('#treeBody');
    host.replaceChildren();
    for (let i = 0; i < 4; i++) host.append(h('div', { class: 'dcard skel-card' }, UI.skel(null, 'lines:3')));
    $('#settings').replaceChildren(h('p', { class: 'meta', text: 'Settings load with your preferences…' }));
  }
  async function load() {
    skeleton();
    paintSubject();
    let prefs = {};
    try { prefs = await UI.prefs(); } catch (_) {}
    B.prefs = prefs || {};
    B.st = fromPrefs(B.prefs);
    B.saved = Object.assign({}, B.st);
    try { B.me = await UI.me(); } catch (_) { B.me = null; }
    let bank;
    try { bank = await UI.api('/bank?subject=math', { quiet: true }); }
    catch (e) {
      const host = $('#treeBody');
      host.replaceChildren();
      UI.cardError(host, () => load(), 'The server is not answering.');
      $('#start').disabled = true; $('#start').textContent = 'Start practice';
      $('#reason').textContent = 'The server is not answering.'; $('#reason').hidden = false;
      return;
    }
    B.bank = bank;
    B.byT.clear(); B.skills.clear();
    bank.domains.forEach(d => d.skills.forEach(s => { s.domain = s.domain || d.name; B.skills.set(s.slug, s); (s.types || []).forEach(t => { t.topic = t.topic || s.slug; B.byT.set(t.template, t); }); }));
    B.fromLink = fromLink();
    if (!B.fromLink) applyPreset('coach', null);
    else { B.preset = 'custom'; linkNote('Settings from the link, not your defaults'); }
    paintHead(); paintTreeHead(); paintAll();
    if (url.get('search')) { $('#q').value = url.get('search'); onSearch(); }
    await loadSets();
    paintHead(); paintBanners(); paintSets(); paintReady();
    showSubject();
  }

  $('#q').addEventListener('input', onSearch);
  $('#q').addEventListener('keydown', searchKeys);
  $('#start').addEventListener('click', start);
  $('#openSettings').prepend(icon('settings', 18));
  $('#openSettings').addEventListener('click', openSettings);
  if (UI.tooltip) UI.tooltip($('#openSettings'), () => B.setText || '');   // a tap opens the sheet, which says it all
  tip($('#l1'), () => B.sumText || '');
  if (UI.keys && UI.keys.register) {
    try { UI.keys.register('page', { '/': { does: 'Search or build a set', run: () => { $('#q').focus(); } } }, { label: 'Practice' }); } catch (_) {}
  } else addEventListener('keydown', e => { if (e.key === '/' && !/input|textarea|select/i.test((document.activeElement || {}).tagName)) { e.preventDefault(); $('#q').focus(); } });
  load();
})();
