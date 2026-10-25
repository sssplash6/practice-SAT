/* ============================================================================
   SAT Freshman -- the practice builder, /practice/ (spec 3.3 part 1, practice.md
   P3 P5 P6 P7 P10-P17 P19 P21 P22). One read (GET /api/bank), one debounced
   POST /api/drill/preview for every count and the Start gate, POST /api/drill to
   start. The bar's Start opens a window (tabs of settings); its settings save to prefs (PUT /api/me) 600 ms after a change; a deep
   link's settings apply to this visit only. Nothing auto-starts.
   ========================================================================== */
(() => {
  const h = UI.h, $ = s => document.querySelector(s);
  // the shared icon set (UI.icon); an unknown name draws nothing (it used to draw the orange dot, which hid typos)
  const icon = (name, size = 18) => { const svg = UI.icon(name, size); return svg ? h('span', { class: 'ic', 'aria-hidden': 'true' }, svg) : null; };
  const url = new URLSearchParams(location.search);
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const NONE = UI.NONE;   // the missing-value glyph, an en dash (kit)
  const pct = x => (x === null || x === undefined ? NONE : `${Math.round(x * 100)}%`);
  const n0 = n => (n === null || n === undefined ? '…' : UI.num ? UI.num(n) : String(n));
  const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + 's'}`;
  const mmss = ms => UI.mmss(Math.round((ms || 0) / 1000));
  const cap = t => (t ? t[0].toUpperCase() + t.slice(1) : '');
  // the app's short names (UI.TOPIC, as the palette and the sidebar say them), so a tree row is one line; the full name
  // stays the row's tooltip and accessible name and the skill window's title
  const label = s => (((UI.TOPIC || {})[s.slug] || {}).short) || s.short || s.name;
  const skName = slug => { const s = B.skills.get(slug); return s ? label(s) : UI.topicName(slug); };   // the other subject's skill too (Your sets lists both)
  const dlabel = d => (((UI.TOPIC || {})[((d.skills || [])[0] || {}).slug] || {}).dshort) || d.name;
  const DAY = 864e5;
  function ago(iso) {
    if (!iso) return NONE;
    const d = Math.floor((Date.now() - new Date(iso).getTime()) / DAY);
    if (d < 1) return 'today';
    if (d < 14) return `${d}d ago`;
    if (d < 60) return `${Math.floor(d / 7)}w ago`;
    return `${Math.floor(d / 30)}mo ago`;
  }
  const when = iso => { try { return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }); } catch (_) { return iso || ''; } };
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
    no_lookalikes: 'No type here has look-alikes to mix with',
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
  // the site's one subject choice (UI.subject); a link that names skills or types but no subject (Today's "More
  // options" sends ?topics=) opens on their subject
  const linked = ['skills', 'topics', 'topic', 'types'].map(k => (url.get(k) || '').split(',')[0]).find(Boolean);
  const B = {
    bank: null, byT: new Map(), skills: new Map(), sel: new Set(), st: Object.assign({}, DEF), prefs: {}, saved: null,
    preset: 'coach', source: null, fromLink: false, preview: null, search: '',
    sort: ls.get('satf.tree.sort', null), view: 'skills', sets: null, owned: null,
    subject: linked && !url.get('subject') ? UI.subjectOf(linked) : UI.subject.get(), presetBody: null, me: null,
  };
  const isRW = (s = B.subject) => s === 'rw';
  // R&W items are written passages, not generated numbers: the "one like it" copy says so
  const fresh = s => (isRW(s) ? 'fresh passages' : 'new numbers');

  // a typed number is for this set only (the user: the box should just say Other): only the chip values are remembered as defaults
  const CHIP_COUNTS = [10, 30, 50], CHIP_MINS = [10, 30, 60];
  const typed = new Set();   // which boxes hold a number typed in this visit; the rest read "Other"
  function fromPrefs(p) {
    const st = Object.assign({}, DEF);
    if (Number.isInteger(p.set_length) && (p.set_length === 0 || CHIP_COUNTS.includes(p.set_length))) st.count = p.set_length === 0 ? null : p.set_length;
    if (p.clock && !(p.clock === 'custom' && !CHIP_MINS.includes(p.clock_minutes))) st.timing = p.clock;
    if (p.clock_minutes && CHIP_MINS.includes(p.clock_minutes)) st.minutes = p.clock_minutes;
    ['tiers', 'levels', 'formats'].forEach(k => { if (Array.isArray(p[k]) && p[k].length) st[k] = p[k].slice(); });
    ['adaptive', 'pace_alert'].forEach(k => { if (typeof p[k] === 'boolean') st[k] = p[k]; });
    ['feedback', 'repairs', 'order', 'mix', 'confidence'].forEach(k => { if (p[k]) st[k] = p[k]; });
    if (p.pool) st.pool = p.pool === 'checks' ? 'checks' : p.pool;
    const pm = ((p.practice || {})[B.subject]) || {};   // the server resolves both subjects' keys, defaults included
    SUBJ_KEYS.forEach(k => { if (pm[k] !== undefined && pm[k] !== null) st[k] = pm[k]; });
    return st;
  }
  // the settings each subject keeps for itself (prefs.practice.math / .rw); the rest are shared
  const SUBJ_KEYS = ['zone', 'review_mix', 'review_from', 'cover', 'words_mix', 'final_round', 'hints', 'worked_first', 'two_passes'];
  function toPrefs(st) {
    return {
      set_length: st.count === null ? 0 : CHIP_COUNTS.includes(st.count) ? st.count : DEF.count ?? 10,
      clock: st.timing === 'custom' && !CHIP_MINS.includes(st.minutes) ? (DEF.timing || 'pace') : st.timing, clock_minutes: CHIP_MINS.includes(st.minutes) ? st.minutes : (DEF.minutes ?? 10), tiers: st.tiers, adaptive: st.adaptive,
      levels: st.levels, unmeasured: st.unmeasured, formats: st.formats, feedback: st.feedback, repairs: st.repairs,
      order: st.order === 'mixup' ? 'mixed' : st.order, mix: st.mix, pool: st.pool, confidence: st.confidence, pace_alert: st.pace_alert,
      practice: Object.fromEntries(SUBJ_KEYS.map(k => [k, st[k]])),
    };
  }
  // a subject switch: that subject's own settings and their saved copy; the shared ones stay
  function subjectSettings() {
    const p = fromPrefs(B.prefs);
    SUBJ_KEYS.forEach(k => { B.st[k] = p[k]; if (B.saved) B.saved[k] = p[k]; });
  }
  let saveT = 0;
  function savePrefs() {
    if (B.fromLink) return;
    clearTimeout(saveT);
    saveT = setTimeout(async () => {
      const now = toPrefs(B.st), was = B.saved ? toPrefs(B.saved) : {};
      const diff = {};
      const same = (a, z) => JSON.stringify(a) === JSON.stringify(z);
      Object.keys(now).forEach(k => { if (k !== 'practice' && !same(now[k], was[k])) diff[k] = now[k]; });
      // only the keys that changed, under this subject (the server merges them key by key)
      const sub = SUBJ_KEYS.filter(k => !same(now.practice[k], (was.practice || {})[k]));
      if (sub.length) diff.practice = { [B.subject]: Object.fromEntries(sub.map(k => [k, now.practice[k]])) };
      if (!Object.keys(diff).length) return;
      try { const pr = await UI.prefs.set(diff); B.prefs = (pr && pr.prefs) || B.prefs; B.saved = Object.assign({}, B.st); footNote('Saved as your defaults'); }
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
    return true;
  }
  const fmts = () => (B.subject === 'rw' ? ['mcq'] : B.st.formats);
  function fits(t) {
    if (!t.formats.some(f => fmts().includes(f))) return false;
    if (B.st.has.includes('desmos') && !t.desmos) return false;
    if (B.st.has.includes('official') && !t.official) return false;
    return (t.tiers || []).some(d => tierOk(t, d));
  }
  function whyNot(ts) {
    if (!ts.length || ts.some(fits)) return '';
    if (!ts.some(t => t.formats.some(f => fmts().includes(f)))) return B.st.formats.includes('spr') ? 'no grid-in types' : 'no multiple-choice types';
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
    const b = Object.assign({ subject: B.subject, source: B.source || 'builder' }, selectionBody());
    if (B.presetBody) Object.assign(b, B.presetBody);
    b.count = st.box ? null : st.count;
    if (st.box) b.box = st.box;
    b.pool = st.pool;
    if (['seen', 'marked', 'saved'].includes(st.pool)) b.exact = !!st.exact;
    if (st.pool === 'seen') { b.result = st.result; b.from = st.from; }
    b.zone = st.zone;
    if (standard()) Object.assign(b, { tiers: st.tiers, adaptive: st.adaptive && st.order !== 'ramp', tier_mix: st.tier_mix, levels: st.levels, unmeasured: st.unmeasured });
    b.formats = fmts();
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
      if (!B.bank) return;
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
    const pts = $('#points');
    const g = b.gains;
    pts.replaceChildren();
    if (g && (g.total || g.points)) pts.append(h('a', { href: '/results/', class: 'qlink', text: `${g.range ? `${UI.subjectLabel(B.subject, true)} ${g.range} · ` : ''}≈ ${Math.round(g.total || g.points)} points on the table` }));
    pts.hidden = !pts.childNodes.length;
    const route = $('#route');
    route.replaceChildren();
    if (b.route && (b.route.text || b.route.line)) {
      route.append(h('span', { text: b.route.text || b.route.line }));
      route.append(h('button', { type: 'button', class: 'btn sm', text: 'Practise the harder module’s mix', onclick: () => applyPreset('route') }));
      route.hidden = false;
    } else route.hidden = true;
    const c = b.counts || {};
    // the lists, as icon rows with the count at the end (neutral: a count, not an alarm); a set in progress is the
    // resume row's to say, not repeated here
    const link = (label, n, href, onClick, ic) => {
      const inner = [UI.icon(ic, 18), h('span', { text: label }), n ? h('span', { class: 'n', text: n0(n) }) : null];
      return href ? h('a', { class: 'pr-li', href }, inner) : h('button', { type: 'button', class: 'pr-li', onclick: onClick }, inner);
    };
    $('#links').replaceChildren(
      link('Mistakes', c.mistakes, '/mistakes/', null, 'review'),
      link('Saved', c.saved, null, () => { setPool('saved'); openStart('set'); }, 'bookmark'),
      link('Your sets', 0, null, () => showSets(), 'list'));
  }
  // the site's subject switch (UI.subjectSeg: remembered, kept in the URL); each subject has its own tree and settings
  function paintSubject() {
    const host = $('#subject');
    host.replaceChildren();
    UI.subjectSeg(host, { value: B.subject, onChange: v => {
      B.subject = v;
      if (B.fromLink) { B.fromLink = false; linkNote(null); B.st = fromPrefs(B.prefs); B.saved = Object.assign({}, B.st); }   // a link's settings were for the other subject
      else subjectSettings();
      B.st.has = [];   // Desmos and official filters are Math's, and only for this visit
      if (B.view === 'habits' && isRW()) B.view = 'skills';
      useSubject();
      paintReady();
    } });
  }

  /* ---------------------------------------------------------------- banners: resume and shared */
  function paintBanners() {
    const host = $('#banners');
    host.replaceChildren();
    const act = (B.sets && B.sets.active) || [];
    if (act.length) {
      const s = act[0];
      const names = (s.topics || []).map(skName).slice(0, 3).join(', ');
      const clock = s.paused ? 'paused' : s.timed && Number.isFinite(s.seconds_left) ? `${UI.mmss(s.seconds_left)} left` : `untimed · ${mmss(s.ms)} so far`;
      const endB = h('button', { type: 'button', class: 'quiet', text: 'End it' });
      endB.addEventListener('click', async () => {
        const ok = await UI.confirm({ title: 'End this set?', text: 'End this set and see its summary?', confirm: 'End set', cancel: 'Cancel' });
        if (!ok) return;
        try { await UI.api(`/drill/${s.id}/finish`, { method: 'POST', body: {} }); location.href = `/practice/session/?id=${encodeURIComponent(s.id)}`; }
        catch (e) { UI.toast(`Couldn’t end it: ${e.message}`); }
      });
      // the one place a set in progress shows on this page (the sidebar's Resume badge is the shell's)
      host.append(h('div', { class: 'card pr-box', role: 'region', 'aria-label': 'Set in progress' },
        h('p', {}, h('b', { text: 'Set in progress' })),
        h('p', { class: 'meta', text: `${names || 'Practice'} · ${s.total ? `${s.answered} of ${s.total}` : s.answered} answered · ${clock}` }),
        h('div', { class: 'acts' }, h('a', { class: 'btn sm', href: `/practice/session/?id=${encodeURIComponent(s.id)}`, text: 'Resume' }), endB,
          act.length > 1 ? h('button', { type: 'button', class: 'qlink', text: `+${act.length - 1} more`, onclick: () => { setsTab('active'); showSets(); } }) : null)));
    }
    const code = url.get('share');
    if (code) sharedBanner(host, code);
    host.hidden = !host.childNodes.length && !code;
  }
  async function sharedBanner(host, code) {
    const box = h('div', { class: 'card pr-box', role: 'region', 'aria-label': 'Shared set' }, h('p', { text: 'Loading the shared set…' }));
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
    const topics = (s.topics || []).map(t => (typeof t === 'string' ? skName(t) : skName(t.topic) || t.name)).join(', ');   // /sets sends {topic, name, n}
    const fb = { instant: 'answers after each', retry: 'answers after a retry', end: 'answers at the end' }[s.feedback] || 'answers after each';
    const start = h('button', { type: 'button', class: 'pill sm', text: 'Start this set' });
    start.addEventListener('click', async () => {
      start.setAttribute('aria-busy', 'true');   // the pill's spinner after 300ms, same width (ui.css)
      try {
        const r = await UI.api(`/sets/${encodeURIComponent(code)}/start`, { method: 'POST', body: { show_name: show.checked } });
        location.href = `/practice/session/?id=${encodeURIComponent(r.id || r.session)}`;
      } catch (e) { start.removeAttribute('aria-busy'); UI.toast(e.status === 410 ? 'Whoever shared this set has stopped sharing it.' : `Couldn’t start it: ${e.message}`); }
    });
    box.replaceChildren(
      h('p', {}, h('b', { text: `Shared set · ${plural(s.count || 0, 'question')}` }), topics ? ` · ${topics}` : '', s.timed ? ` · timed ${s.minutes || ''} min` : ' · untimed', ` · ${fb}`),
      h('p', { class: 'meta', text: [s.by ? `from ${s.by}` : null, s.taken ? `taken by ${s.taken}` : null, s.fresh ? 'each taker gets their own twins' : 'the exact questions'].filter(Boolean).join(' · ') }),
      h('label', { class: 'check' }, show, h('span', { text: 'Show my name to the person who shared this' })),
      name ? '' : h('p', { class: 'help' }, 'Set a board name on ', h('a', { href: '/me/', text: 'Me' }), ' first.'),   // replaceChildren prints a null
      h('p', { class: 'help', text: 'Uses the sharer’s questions and settings, not yours.' }),
      h('div', { class: 'acts' }, start, h('button', { type: 'button', class: 'quiet', text: 'Dismiss', onclick: () => dismissShare(box) })));
  }
  function dismissShare(box) {
    box.remove();
    const u = new URL(location.href); u.searchParams.delete('share'); history.replaceState(null, '', u);
    $('#banners').hidden = !$('#banners').childNodes.length;
  }

  /* ---------------------------------------------------------------- Ready rows (P15) */
  // Up next's other items and your last set, as rows in the aside. Up next's first item is the shell's to show (the
  // sidebar or the Now strip), so it is left out here; the empty search's Enter still starts it.
  let ready = [], readyAll = [], nextIn = false, readyRows = null;   // readyRows: the list, kept so a change glides   // nextIn: Up next has answered (or failed), so the Diagnostic line can decide
  async function paintReady() {
    // Up next holds both subjects: this tab lists its own subject's (an item without one is anyone's)
    const mine = x => !x.subject || x.subject === B.subject;
    const last = ((B.sets && B.sets.recent) || []).find(r => r.kind !== 'challenge' && mine({ subject: r.subject || 'math' }));
    let next = [];
    const shell = UI.shellData ? UI.shellData() : null;   // GET /api/next only once the server has it (U1), as the shell does
    if (!(shell && shell.has && !shell.has.next)) try { const r = await UI.api('/next?limit=8', { quiet: true }); next = (Array.isArray(r) ? r : r.items || []).filter(mine).slice(0, 3); } catch (_) { next = []; }
    readyAll = next.map(x => ({ title: x.title, key: x.key, href: x.href, meta: x.meta || UI.nextMeta(x),   // the shell's own meta line
      why: x.reason || x.why || '', item: x.start || x.href ? x : null, body: x.body, reason: x.unavailable || null }));
    nextIn = true;
    if (last) readyAll.push({ title: 'Your last set again', meta: `${(last.topics || []).map(skName).slice(0, 2).join(', ')} · ${last.total ?? last.answered}\u00a0q`, why: `${last.right}/${last.answered} right`, body: { again: last.id, source: 'builder' } });
    renderReady();
  }
  const sameItem = (a, z) => !!(a && z && (a.key && z.key ? a.key === z.key : a.title === z.title));
  const hereHref = it => { try { return !!(it && it.href && new URL(it.href, location.href).pathname === location.pathname); } catch (_) { return false; } };
  function renderReady() {
    paintDiag();
    const host = $('#ready');
    const first = UI.nextItems ? UI.nextItems()[0] : null;
    // the shell shows Up next's first item everywhere, except the Now strip's skip of a link to this page: then only
    // the sidebar shows it, so the row stays and CSS hides it where the sidebar does ([data-upnext])
    ready = readyAll.filter(c => !(UI.shellData && UI.shellData() && sameItem(c, first) && !hereHref(first)));
    if (!ready.length) { host.replaceChildren(); readyRows = null; host.hidden = true; return; }
    const rows = () => ready.map(c => {
      const go = h('button', { type: 'button', class: 'quiet go', 'aria-label': `Start ${c.title}` }, 'Start', UI.icon('arrow', 16));
      go.addEventListener('click', () => startReady(c, go));
      const row = h('div', { class: 'pr-row', 'data-key': c.key || c.title, 'data-upnext': sameItem(c, first) ? '' : null },
        h('div', {}, h('b', { text: c.title }), c.meta ? h('span', { class: 'meta', text: c.meta }) : null),
        c.reason ? h('span', { class: 'help', text: c.reason }) : go);   // no Edit: the builder already tweaks a set
      return c.why ? tip(row, c.why) : row;   // the reason: hover, a tap, or Start's focus and description
    });
    if (readyRows && readyRows.isConnected) {   // Up next changed: rows that stay slide, new ones rise, gone ones fade
      const list = readyRows;
      UI.glide(list, () => list.replaceChildren(...rows()));
    } else {
      readyRows = h('div', { class: 'pr-rows' }, rows());
      // a heading folds the rows (the user); remembered on this device; it opens and closes in height (details.fold)
      const d = h('details', { class: 'pr-fold fold', open: ls.get('satf.pr.ready', true) ? true : null }, h('summary', { text: 'Ready to start' }), readyRows);
      d.addEventListener('toggle', () => ls.set('satf.pr.ready', d.open));
      host.replaceChildren(d);
    }
    host.hidden = false;   // Up next and your last set hold both subjects: the rows show on either tab
    paintSearchHelp();
  }
  if (UI.onShell) UI.onShell(() => { if (readyAll.length) renderReady(); });
  // an Up next item starts as the shell starts it (its path and body, or its link); your last set through the builder
  async function startReady(c, btn) {
    if (!c.item) { if (c.body) create(c.body, btn); return; }
    if (starting) return;
    starting = true;
    btn.setAttribute('aria-busy', 'true');
    try { await UI.start(c.item); }
    catch (e) { starting = false; btn.removeAttribute('aria-busy'); UI.toast(`Couldn’t start it: ${e.message}`); }
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
      // R&W's cover has no answer field: predict the answer, then show the choices (the Feedback tab's control says the same)
      { id: 'solve', label: isRW() ? 'Predict first · 10' : 'Solve first · 10' },
      { id: 'probe', label: `Check ${plural(untried.length || 3, 'skill')} I haven’t tried`, why: untried.length ? null : 'Every skill has answers', skills: untried },
    ];
    if (b.top_habit) list.push({ id: 'habit', label: `Top habit · ${b.top_habit.name || b.top_habit.id}` });
    if (b.desmos_way) { const n = allTypes().filter(t => t.desmos).length; list.push({ id: 'desmos', label: `Desmos drills${n ? ` · ${n}` : ''}`, why: n ? null : 'No Desmos-way types yet' }); }
    myPresets().forEach((p, i) => list.push({ id: `mine:${i}`, label: p.name, mine: p }));
    list.push({ id: 'custom', label: 'Custom', inert: true });
    return list.filter(Boolean);
  }
  // the presets live behind one trigger at the head of Your set (pages/practice.md 2): it reads the preset that is on
  // ("Mentor's pick", "Custom") and opens one menu: Suggested, From your history, Yours, then save, share and reset.
  // A preset that can't run yet is listed, dimmed, with its reason under it. The trigger is made once (index.html):
  // a repaint only renames it, so the menu's focus comes back to it
  const HISTORY = ['mistakes', 'missed', 'marked', 'saved', 'due'];
  function presetLabel() {
    const p = presets().find(x => x.id === B.preset);
    return p ? p.label : B.preset === 'route' ? 'Harder module’s mix' : 'Custom';
  }
  function paintPresets() {
    const t = $('#presets');
    t.disabled = false;
    t.textContent = presetLabel();
    t.setAttribute('aria-label', `Preset: ${t.textContent}`);
    paintDiag();
  }
  function presetItems() {
    if (!B.bank) return [];
    const all = presets().filter(p => !p.inert);
    const item = p => (p.why && p.href
      ? { label: p.label, sub: p.why, href: p.href }           // Plan focus with no focus yet: set one in Plan
      : { label: p.label, sub: p.why || p.about || null, disabled: !!p.why, radio: 'preset', checked: B.preset === p.id, close: true, onClick: () => { const was = picked(); applyPreset(p.id, p); cascade(was); } });
    const group = (name, list) => (list.length ? [{ group: name }, ...list.map(item)] : []);
    const mine = all.filter(p => p.mine);
    return [
      ...group('Suggested', all.filter(p => !p.mine && !HISTORY.includes(p.id))),
      ...group('From your history', all.filter(p => HISTORY.includes(p.id))),
      ...group('Yours', mine),
      { separator: true },
      { label: 'Save as preset', onClick: savePreset },
      { label: 'Copy link', onClick: () => UI.copyText(deepLink(), { toast: 'Link copied: it opens these settings' }) },
      { label: 'My defaults', sub: 'Back to your saved settings', onClick: () => { B.st = fromPrefs(B.prefs); B.fromLink = false; applyPreset('coach'); linkNote(null); } },
      ...mine.flatMap(p => [{ label: `Rename ${p.label}`, onClick: () => renamePreset(+p.id.split(':')[1]) }, { label: `Delete ${p.label}`, onClick: () => deletePreset(+p.id.split(':')[1]) }]),
    ];
  }
  UI.menu.bind($('#presets'), presetItems, { label: 'Presets', wide: true, align: 'end' });
  // a new student's way to a starting score: one quiet line at the foot of Your set, unless Up next already offers the
  // Diagnostic (the sidebar, the Now strip or a Ready row shows it then). Repainted when Up next arrives
  function paintDiag() {
    const diag = $('#diag');
    const inNext = readyAll.some(c => { try { return !!c.href && new URL(c.href, location.href).pathname === '/diagnostic/'; } catch (_) { return false; } });
    diag.hidden = !nextIn || !B.bank || !!(B.bank.totals || {}).answered || inNext;
  }
  // why the mentor picked these skills: the Mentor's pick chip's tooltip, not a permanent line
  function coachWhy() {
    const b = B.bank;
    if (!b.coach) return null;
    const R = b.coach.reasons || {}, mis = [];
    const bits = (b.coach.topics || []).map(t => {
      const r = R[t] || {}, s = B.skills.get(t) || {}, name = s.slug ? label(s) : t;
      if (r.kind === 'mistakes' || r.traps) { mis.push(`${name} ${r.traps || 0}`); return null; }   // one clause for all of them
      if (r.kind === 'weak') return `${name}: weakest, ${UI.masteryWord(r.mastery, s.answered)}, ${pct(r.first_try_rate)} first try`;
      if (r.kind === 'review' && r.since_days) return `${name}: not practised for ${r.since_days} days`;
      if (r.kind === 'focus') return `${name}: in your plan’s focus`;
      if (s.gain) return `${name} ≈ +${Math.round(s.gain)} (${s.per_test ? `${s.per_test} a test, ` : ''}${pct(s.accuracy)} first try)`;
      return null;
    }).filter(Boolean);
    if (mis.length) bits.unshift(`Open mistakes: ${mis.join(', ')}`);
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
    else if (id === 'full') { pickSkills([...B.skills.values()]); st.count = B.subject === 'rw' ? 54 : 44; st.mix = 'blueprint'; st.order = 'mixed'; }
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
  // each subject keeps its own presets (prefs.practice.math.presets / .rw.presets)
  const myPresets = () => ((((B.prefs.practice || {})[B.subject]) || {}).presets || []).slice();
  async function savePreset() {
    const name = await UI.confirm({ title: 'Save as preset', text: 'These skills and settings join your presets, in the menu at the head of Your set.', confirm: 'Save', input: { label: 'Name', value: '', maxlength: 24 } });
    if (!name) return;
    const list = myPresets();
    if (list.length >= 8) { UI.toast('You have 8 presets. Delete one first.'); return; }
    list.push({ name: String(name).slice(0, 24), body: body() });
    if (await putPresets(list, `mine:${list.length - 1}`)) paintPresets();
  }
  // on: the preset that is on afterwards (a save turns the new one on; a delete shifts the ones after it)
  async function putPresets(list, on) {
    try { const pr = await UI.prefs.set({ practice: { [B.subject]: { presets: list } } }); B.prefs = pr.prefs || B.prefs; if (on !== undefined) B.preset = on; paintPresets(); return true; }
    catch (e) { UI.toast(`Not saved: ${e.message}`); return false; }
  }
  async function renamePreset(i) {
    const list = myPresets();
    const name = await UI.confirm({ title: 'Rename preset', confirm: 'Rename', input: { label: 'Name', value: list[i].name, maxlength: 24 } });
    if (!name) return;
    list[i] = Object.assign({}, list[i], { name: String(name).slice(0, 24) });
    putPresets(list);
  }
  function deletePreset(i) {
    const list = myPresets();
    list.splice(i, 1);
    const m = /^mine:(\d+)$/.exec(B.preset), j = m ? +m[1] : -1;
    putPresets(list, j < 0 || j < i ? undefined : j === i ? 'custom' : `mine:${j - 1}`);
  }
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
      const hay = norm(`${t.name} ${t.about} ${(t.labels || []).join(' ')} ${sk.name} ${sk.slug ? label(sk) : ''} ${t.template}`);
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
      if (hits.size) line.append(h('span', { class: 'meta', text: `${plural(hits.size, 'type')} match` }), h('button', { type: 'button', class: 'btn sm', text: `Select all ${hits.size}`, onclick: () => { hits.forEach(t => B.sel.add(t)); markCustom(); paintSel(); preview(); } }));
      else if (!(parsed && parsed.chips && parsed.chips.length)) line.append(h('span', { class: 'help', text: `No question type matches “${q.trim()}”. Try a skill name.` }));
    }
    if (parsed && parsed.chips && parsed.chips.length) {
      line.append(...parsed.chips.map(c => h('span', { class: 'badge soft', text: typeof c === 'string' ? c : c.label || c.text || '' })));
      line.append(h('span', { class: 'meta', text: 'Enter to start · Shift+Enter applies it below' }));   // the chips already say the set
    }
    if (!q.trim()) paintSearchHelp();
  }
  function paintSearchHelp() {
    const line = $('#sline');
    if (B.search.trim()) return;
    line.replaceChildren();
  }
  function paintSearch(hits) {
    document.querySelectorAll('.trow').forEach(r => { r.hidden = !!hits && !hits.has(r.dataset.t); });
    // a search never opens a window; a skill row shows while any of its types match, a domain while any of its skills do
    document.querySelectorAll('.srow').forEach(r => {
      const sk = B.skills.get(r.dataset.s);
      r.hidden = !!hits && !typesOf(sk).some(t => hits.has(t.template));
      const nm = r.querySelector('.sname');
      if (nm) highlight(nm, label(sk), B.search);
    });
    document.querySelectorAll('.trow .tname').forEach(n => highlight(n, (B.byT.get(n.closest('.trow').dataset.t) || {}).name, B.search));
    document.querySelectorAll('.dcard').forEach(c => {
      const d = B.bank.domains.find(x => x.name === c.dataset.d);
      c.hidden = !!hits && !(d && d.skills.some(sk => typesOf(sk).some(t => hits.has(t.template))));
    });
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
    if (!v) { const c = readyAll[0]; if (c) startReady(c, $('#start')); return; }
    const hist = [v, ...ls.get('satf.cmd', []).filter(x => x !== v)].slice(0, 10);
    ls.set('satf.cmd', hist);
    if (parsed && parsed.body && parsed.chips && parsed.chips.length) {
      if (e.shiftKey) { loadBody(parsed.body); f.value = ''; onSearch(); return; }
      // a typed skill or type says its subject (the server infers it); a line that names none is this tab's
      create(Object.assign({ source: 'builder' }, parsed.body.topics || parsed.body.templates ? {} : { subject: B.subject }, parsed.body));
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
  // the tree head is one line (pages/practice.md 2): a master box (all, some, none; it was Select all and Clear), the
  // title, "3 of 19 selected" with Clear while something is picked, and one View trigger at the right that holds
  // what was the Skills / Map / Habits switch and the sort select. The trigger reads the order, or Map or Habits
  const SORTS = [['points', 'Most points'], ['test', 'Test order'], ['weak', 'Weakest first'], ['mistakes', 'Most mistakes'], ['overdue', 'Most overdue'], ['slow', 'Slowest vs budget'], ['least', 'Least practised'], ['recent', 'Recently practised']];
  const VIEWS = { skills: 'Skills', map: 'Map', habits: 'Habits' };
  const hasPts = () => [...B.skills.values()].some(s => s.gain);
  function selChanged() { markCustom(); if (B.view === 'map') paintTree(); else paintSel(); preview(); }
  // the preset cascade (pages/practice.md 5): skills that just got picked fill in tree order, 20ms apart (at most
  // 240ms), so a preset or a box shows where it went. A pointer pick only: a key or reduced motion fills at once
  const picked = () => new Set(selectedSkills().map(s => s.slug));
  function cascade(was) {
    const M = UI.motion;
    if (!M || M.off() || M.kb()) return;
    const rows = [...document.querySelectorAll('#treeBody .srow')].filter(r => !was.has(r.dataset.s) && r._tri && r._tri.getAttribute('aria-checked') !== 'false');
    if (rows.length < 2) return;
    rows.forEach(r => r.classList.add('pr-pre'));
    void getComputedStyle(rows[0]).backgroundColor;   // the unpicked look is where each fill starts
    rows.forEach((r, i) => setTimeout(() => r.classList.remove('pr-pre'), Math.min(i * 20, 240)));
  }
  function paintTreeHead() {
    const host = $('#thead');
    if (!B.sort || (B.sort === 'points' && !hasPts())) B.sort = hasPts() ? 'points' : 'test';
    const all = tri('Select every skill', on => { const was = picked(); B.skills.forEach(s => setSkill(s, on)); selChanged(); cascade(was); });
    all.id = 'treeAll';
    const view = h('button', { type: 'button', class: 'btn sm dd', id: 'view' });
    UI.menu.bind(view, viewItems, { label: 'View and order', align: 'end' });
    host.replaceChildren(all, h('h2', { class: 'h2', text: 'Skills' }), h('span', { class: 'pr-count', id: 'treeCount' }),
      h('button', { type: 'button', class: 'quiet', id: 'treeClear', text: 'Clear', hidden: true, onclick: () => { B.sel.clear(); selChanged(); } }), view);
    paintViewBtn();
  }
  function paintViewBtn() {
    const v = $('#view');
    if (!v) return;
    v.textContent = B.view === 'skills' ? (SORTS.find(([k]) => k === B.sort) || SORTS[1])[1] : VIEWS[B.view];
    v.setAttribute('aria-label', `View and order: ${v.textContent}`);
  }
  function viewItems() {
    if (!B.bank) return [];
    const habits = (B.bank.habits || []).length;
    const show = (v, sub) => ({ label: VIEWS[v], sub, radio: 'view', checked: B.view === v, close: true, onClick: () => { B.view = v; paintTree(); } });
    return [{ group: 'Show' }, show('skills', null), show('map', 'Every question type as a cell'),
      // listed before it has rows (its empty state says when): the switch it replaces showed it from the start.
      // Habits are Math's named traps; R&W has none
      isRW() ? null : show('habits', habits ? 'The kinds of trap you fall for across skills, and the ones you reliably rule out' : 'After about 30 answers'),
      { separator: true }, { group: 'Order skills' },
      ...SORTS.filter(([v]) => v !== 'points' || hasPts()).map(([v, l]) => ({ label: l, radio: 'sort', checked: B.view === 'skills' && B.sort === v, close: true,
        onClick: () => { B.sort = v; ls.set('satf.tree.sort', v); B.view = 'skills'; paintTree(); } }))].filter(Boolean);
  }
  // wide: always-open domain columns (two, four from 1000px: the CSS container query). Narrow: a 2x2 grid of tiles; a
  // tile opens a window of that domain's skills. The tree's own width decides (the aside takes 312px from 1280px).
  const WIDE = 560;
  const wide = () => $('#tree').clientWidth >= WIDE;
  let wasWide = null;
  try { new ResizeObserver(() => { if (B.bank && B.view === 'skills' && wide() !== wasWide) paintTree(); }).observe($('#tree')); } catch (_) {}
  function paintTree() {
    const host = $('#treeBody');
    host.className = B.view === 'skills' ? 'dgrid' : '';
    host.replaceChildren();
    if (B.view === 'map') paintMap(host);
    else if (B.view === 'habits') paintHabits(host);
    else {
      // test order, reading down each column (CSS columns) or across the tiles
      wasWide = wide();
      B.bank.domains.forEach(d => host.append(domainCard(d)));
      paintAvail();
      if (B.search) paintSearch(matches(B.search));
    }
    paintSel(); paintViewBtn();   // the head's box and count follow every view
  }
  function tri(label, onClick) {
    const b = h('button', { type: 'button', class: 'tri', role: 'checkbox', 'aria-checked': 'false', 'aria-label': label });
    b.addEventListener('click', e => { e.stopPropagation(); onClick(b.getAttribute('aria-checked') !== 'true'); });
    b.addEventListener('pointerdown', e => e.stopPropagation());
    return b;
  }
  // a small neutral count, only when something is open (decision 7; the critic: not orange, it is not the thing to do)
  function openBadge(n) {
    if (!n) return null;
    const b = h('span', { class: 'badge n soft' }, String(n), h('span', { class: 'sr', text: ` open ${n === 1 ? 'mistake' : 'mistakes'}` }));
    return tip(b, plural(n, 'open mistake'));
  }
  // a bar only where there is data: no grey track on a skill with no answers (a bar always means something)
  const bar = (m, answered) => (answered ? h('span', { class: 'mbar', 'aria-hidden': 'true' }, h('i', { style: `--m:${Math.max(0, Math.min(1, m || 0))}` })) : null);
  // the facts the column header no longer shows: a tooltip on the header, a line in the phone's domain window, a block in each skill window
  const testN = () => (isRW() ? 54 : 44);   // the section's questions: R&W 2 x 27, Math 2 x 22
  const domFacts = d => [
    ['On the test', `about ${Math.round(d.weight * testN())} of ${testN()}`],
    d.answered ? ['Answered', String(d.answered)] : null,
    d.answered ? ['First try', pct(d.right / Math.max(1, d.answered))] : null,
    d.gain ? ['On the table', `≈ +${Math.round(d.gain)} points`] : null,
    d.due_n ? ['Due for review', String(d.due_n)] : null,
    d.ready_n ? ['Types ready', `${d.ready_n} of ${d.types_n}`] : null,
  ].filter(Boolean);
  function domainCard(d) {
    const isWide = wide();
    const card = h('section', { class: 'dcard', 'data-d': d.name, 'aria-label': d.name });
    const skills = skillOrder(d.skills);
    const tb = tri(`Select every skill in ${d.name}`, on => { const was = picked(); skills.forEach(s => setSkill(s, on)); markCustom(); paintSel(); preview(); cascade(was); });
    tb.dataset.dtri = d.name;
    const traps = d.skills.reduce((a, s) => a + ((s.traps || []).length || s.open_n || 0), 0);
    const pts = Math.round(d.gain || 0);
    // wide: one heading row (the bar small at its right, as on the skill rows); a tile: the bar across its foot
    const dn = dlabel(d);
    const inner = [h('span', { class: 'dname', text: dn, title: dn !== d.name ? d.name : null }),
      isWide ? null : h('span', { class: 'dsel', 'data-dsel': d.name }),
      h('span', { class: 'dright' }, pts > 0 ? h('span', { class: 'dpts', text: `+${pts} pts` }) : null, isWide ? null : openBadge(traps), isWide ? bar(d.mastery, d.answered) : null),
      isWide ? null : bar(d.mastery, d.answered)];
    const open = isWide ? h('div', { class: 'dopen' }, inner) : h('button', { type: 'button', class: 'dopen', 'aria-haspopup': 'dialog', onclick: () => openDomain(d) }, inner);
    const head = h('div', { class: 'dhead' }, tb, open);
    if (isWide) tip(head, domFacts(d).map(([k, v]) => `${k} ${v}`).join(' · '));
    card.append(head);
    if (isWide) card.append(h('div', { class: 'dbody' }, skills.map(skillRow)));
    return card;
  }
  // the phone/tablet window for one domain: its facts, a select-all, and its skills
  function openDomain(d) {
    if (document.querySelector('dialog.dwin')) return;
    const skills = skillOrder(d.skills);
    const w = UI.sheet({ title: d.name, className: 'dwin', body: b => {
      const all = tri(`Select every skill in ${d.name}`, on => { skills.forEach(s => setSkill(s, on)); markCustom(); paintSel(); preview(); });
      all.dataset.dtri = d.name;
      b.append(h('p', { class: 'dfacts', text: domFacts(d).map(([k, v]) => `${k} ${v}`).join(' · ') }),
        h('div', { class: 'dall' }, all, h('span', { text: `All ${plural(skills.length, 'skill')}` })),
        h('div', { class: 'dlist' }, skills.map(skillRow)));
    }, actions: [{ label: 'Done' }] });
    paintSel(); paintAvail(); if (B.search) paintSearch(matches(B.search));
    w.closed.then(() => { paintSel(); paintAvail(); });
  }
  // the row: checkbox (selects), name (opens the skill window), a tiny mastery bar and the open-mistakes count
  function skillRow(s) {
    const tb = tri(`Select ${s.name}`, on => { setSkill(s, on); markCustom(); paintSel(); preview(); });
    const traps = (s.traps || []).length || s.open_n || 0;
    const nm = h('button', { type: 'button', class: 'snm', 'aria-haspopup': 'dialog', 'aria-label': `${s.name}, details and question types` },
      h('span', { class: 'sname', text: label(s), title: label(s) !== s.name ? s.name : null }), h('span', { class: 'reason', 'data-reason': '' }));
    const row = h('div', { class: 'srow', 'data-s': s.slug }, tb, nm,
      h('span', { class: 'sright' }, openBadge(traps), bar(s.mastery, s.answered), s.answered ? h('span', { class: 'sr', text: UI.masteryWord(s.mastery, s.answered) }) : null),
      h('span', { class: 'go', 'aria-hidden': 'true' }, UI.icon('caret_right', 16)));
    row._tri = tb;
    nm.addEventListener('click', () => openSkill(s));
    row.addEventListener('click', e => { if (!e.target.closest('.tri, .snm')) openSkill(s); });
    return row;
  }
  // the skill's window (was the inline panel). Kept callable as openSkill(sk, true); false is a no-op.
  function openSkill(s, open = true) {
    if (typeof s === 'string') s = B.skills.get(s);
    if (!s || open === false || document.querySelector(`dialog.skwin[data-sk="${s.slug}"]`)) return;
    const w = UI.sheet({ title: s.name, size: 'l', className: 'skwin', body: b => fillPanel(s, b), actions: [{ label: 'Done' }] });
    w.el.dataset.sk = s.slug;
    paintSel(); paintAvail(); if (B.search) paintSearch(matches(B.search));
    w.closed.then(() => { paintSel(); paintAvail(); });   // the tree behind it catches up
  }
  function fillPanel(s, panel) {
    const types = typesOf(s);
    const bt = s.by_tier || {};
    const tierN = x => types.filter(t => (t.tiers || []).includes(x)).length;
    const grid = types.filter(t => t.formats.includes('spr')).length;
    const held = s.mastery >= UI.STRONG && s.answered ? (s.held_after ? `held after ${s.held_after} days` : 'not yet tested after a gap') : null;
    const kv = rows => { const r = rows.filter(x => x && x[1] !== null && x[1] !== undefined && x[1] !== ''); return r.length ? h('dl', { class: 'kv' }, r.map(([k, v]) => [h('dt', { text: k }), h('dd', { text: v })])) : null; };
    const cs = s.calc_split;
    const record = s.answered ? [
      ['Answered', String(s.answered)], ['First try', pct(s.accuracy ?? s.right / Math.max(1, s.answered))], ['Last practised', s.last ? ago(s.last) : null],
      ...TIERS.filter(x => (bt[x] || [0, 0])[1]).map(x => [`${TIER_WORD[x]} right`, `${bt[x][0]} of ${bt[x][1]}`]),
      ['Average time', s.avg_ms ? `${mmss(s.avg_ms)} a question` : null], ['Over time', held],
      ['Fluent types', s.fluent_n ? `${s.fluent_n} of ${types.length}` : null], ['Solve-first', s.solve_first ? pct(s.solve_first) : null],
      ['Sure-accuracy', s.sure_rate && s.sure_rate.n ? `${pct(s.sure_rate.rate)} (${s.sure_rate.n})` : null],
      ['With Desmos', cs ? `${pct(cs.with)} (${cs.with_n ?? ''})` : null], ['Without Desmos', cs ? `${pct(cs.without)} (${cs.without_n ?? ''})` : null],
    ] : [];
    const worth = [['On the table', s.gain ? `≈ +${Math.round(s.gain)} points` : null], ['On the test', s.per_test ? `about ${s.per_test} of ${testN()}` : null],
      ['You miss', s.gain && s.to_strong ? `~${s.to_strong}` : null], ['Due for review', s.due_n ? String(s.due_n) : null]];
    const about = [['Question types', String(types.length)], ['By difficulty', TIERS.filter(tierN).map(x => `${TIER_WORD[x]} ${tierN(x)}`).join(' · ')],
      ['Grid-in', grid ? String(grid) : null], ['Everyone', s.crowd_rate !== null && s.crowd_rate !== undefined ? `${pct(s.crowd_rate)} first try` : null]];
    // the window leads with what the student came for: Check my level and the types; the record folds (remembered).
    // The domain's facts are its header's tooltip and the domain window's line.
    panel.append(h('p', { class: 'help', 'data-sreason': s.slug, 'data-nofold': '' }));
    // one way in from the skill (the user: keep Check my level only; Finish, Mix it up and the College Board link went)
    panel.append(h('div', { class: 'btns' },
      h('button', { type: 'button', class: 'btn', text: 'Check my level · 8 questions', onclick: () => create({ subject: B.subject, source: 'probe', topics: [s.slug], count: 8 }) })));
    const rec = h('details', { class: 'pr-fold fold srec', open: ls.get('satf.pr.record', false) ? true : null }, h('summary', { text: 'Your record' }),
      s.answered ? null : h('p', { class: 'help', text: 'Nothing answered in this skill yet.' }), kv([...record, ...worth, ...about]));
    rec.addEventListener('toggle', () => ls.set('satf.pr.record', rec.open));
    panel.append(rec);
    const traps = s.traps || [];
    if (traps.length) {
      panel.append(h('h3', { class: 'sh', text: 'Open mistakes in this skill' }), ...traps.map(t => h('div', { class: 'omis' },
        h('span', {}, h('span', { class: 'dot', 'aria-hidden': 'true' }), ` ${cap(t.label)} · ${(B.byT.get(t.template) || {}).name || t.template} · ${plural(t.owed ?? 2, 'correct answer')} left`),
        h('button', { type: 'button', class: 'quiet', text: 'Fix', onclick: () => create({ subject: B.subject, source: 'mistakes', pool: 'redo', templates: [t.template] }) }))));
    }
    const all = tri(`Select every type in ${s.name}`, on => { setSkill(s, on); markCustom(); paintSel(); preview(); });
    all.dataset.stri = s.slug;
    panel.append(h('div', { class: 'tthead' }, all, h('h3', { class: 'sh', text: `Question types · ${types.length}` })));
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
  const bare = s => norm(s).replace(/[^a-z0-9]/g, '');
  function typeRow(t) {
    const tb = tri(`Select ${t.name}`, on => { on ? B.sel.add(t.template) : B.sel.delete(t.template); markCustom(); paintSel(); preview(); });
    const tiers = t.tiers || [];
    const tryB = h('button', { type: 'button', class: 'quiet', text: 'Try one' });
    UI.menu.bind(tryB, () => [
      { label: 'Try one, these settings', onClick: () => create(Object.assign(body(), { templates: [t.template], topics: undefined, count: 1, pool: 'new', box: undefined })) },
      ...tiers.map(d => ({ label: `Try one · ${TIER_WORD[d]}`, onClick: () => create({ subject: B.subject, source: 'builder', templates: [t.template], count: 1, zone: 'off', tiers: [d] }) })),
      ...(t.formats.includes('spr') && t.formats.includes('mcq') ? [{ label: 'Try one · as a grid-in', onClick: () => create({ subject: B.subject, source: 'builder', templates: [t.template], count: 1, formats: ['spr'] }) }] : []),
    ], { label: `Try ${t.name}` });
    // R&W has no named-traps catalogue (its wrong choices are argued per passage), and most types have no look-alikes:
    // offer only what the type has, and no menu at all when that is nothing
    const moreItems = [
      isRW() ? null : { label: 'See the traps', onClick: () => traps_(t) },
      (t.lookalikes || []).length ? { label: 'Mix it up with look-alikes', onClick: () => create({ subject: B.subject, source: 'mixup', order: 'mixup', templates: [t.template, ...t.lookalikes].slice(0, 6), count: 8 }) } : null,
    ].filter(Boolean);
    const more = moreItems.length ? h('button', { type: 'button', class: 'ibtn', 'aria-label': `More for ${t.name}` }, UI.icon('more', 18)) : null;
    if (more) UI.menu.bind(more, moreItems, { label: t.name });
    // the row's one detail line is its difficulty, only when it isn't all three (the user: keep the difficulty, remove
    // everything else: format, level, odds, record, everyone, open mistakes, marked, ready, due, fluent, Desmos, official, note)
    const chips = [tiers.length < 3 ? h('span', { text: `${tiers.map(d => TIER_WORD[d]).join(' + ')} only` }) : null].filter(Boolean);
    const row = h('div', { class: 'trow', 'data-t': t.template }, tb,
      // most R&W types' about is their name again, punctuated: shown only when it says more
      h('div', { class: 'tmain' }, h('span', { class: 'tname', text: t.name }), t.about && bare(t.about) !== bare(t.name) ? h('span', { class: 'tabout', text: t.about }) : null,
        chips.length ? h('span', { class: 'tchips' }, chips) : null, h('span', { class: 'reason help', 'data-reason': '' })),
      h('div', { class: 'tacts reveal' }, tryB,
        // Learn: one worked, then on your own, then a tier up (R&W's worked one is an unseen bank question)
        h('button', { type: 'button', class: 'quiet', text: 'Learn', 'aria-label': `Learn ${t.name}`, onclick: () => create({ subject: B.subject, source: 'learn', templates: [t.template], count: 3 }) }), more));
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
    }, actions: [{ label: 'Practise this type', primary: true, onClick: () => { create({ subject: B.subject, source: 'builder', templates: [t.template], count: 5 }); } }, { label: 'Close', quiet: true }] });
  }
  function paintSel() {
    const q = (a, v) => document.querySelectorAll(`[${a}="${CSS.escape(v)}"]`);
    B.bank.domains.forEach(d => {
      let dn = 0, dof = 0, sOn = 0;
      d.skills.forEach(s => {
        const n = selOf(s), of = typesOf(s).length;
        dn += n; dof += of; if (n) sOn++;
        q('data-s', s.slug).forEach(r => r._tri && r._tri.setAttribute('aria-checked', triOf(n, of)));
        q('data-stri', s.slug).forEach(b => b.setAttribute('aria-checked', triOf(n, of)));
      });
      q('data-dtri', d.name).forEach(b => b.setAttribute('aria-checked', triOf(dn, dof)));
      q('data-dsel', d.name).forEach(c => { c.replaceChildren(...(sOn ? [`${sOn} of ${d.skills.length}`, h('span', { class: 'sr', text: ' selected' })] : [plural(d.skills.length, 'skill')])); });
    });
    const all = $('#treeAll'), clr = $('#treeClear');
    if (all) all.setAttribute('aria-checked', triOf(B.sel.size, B.byT.size));
    if (clr) clr.hidden = !B.sel.size;
    document.querySelectorAll('.trow').forEach(r => r._tri.setAttribute('aria-checked', String(B.sel.has(r.dataset.t))));
    document.querySelectorAll('.lhead .tri').forEach(b => { const ts = b.dataset.group.split(' '); b.setAttribute('aria-checked', triOf(ts.filter(x => B.sel.has(x)).length, ts.length)); });
    paintCount();
    paintBar();
  }
  // a count, not a percentage: "3 of 19 selected", or "19 skills" with none
  function paintCount() {
    const c = $('#treeCount');
    if (!c) return;
    const n = selectedSkills().length;
    c.replaceChildren(...(n ? [`${n} of ${B.skills.size}`, h('span', { class: 'w', text: ' selected' })] : [plural(B.skills.size, 'skill')]));
  }
  function paintAvail() {
    B.skills.forEach(s => {
      const why = whyNot(typesOf(s)), text = why ? cap(why) : '';
      document.querySelectorAll(`.srow[data-s="${CSS.escape(s.slug)}"]`).forEach(row => {
        row.classList.toggle('dim', !!why);
        row.querySelector('[data-reason]').textContent = text;
        if (text) row.title = text; else row.removeAttribute('title');
        // the name's own tooltip (nearest wins) carries the full name and the reason, so a dimmed row still says why
        const nm = row.querySelector('.sname'), tt = [label(s) !== s.name ? s.name : null, text].filter(Boolean).join(' · ');
        if (nm) { if (tt) nm.title = tt; else nm.removeAttribute('title'); }
      });
      document.querySelectorAll(`[data-sreason="${CSS.escape(s.slug)}"]`).forEach(p => { p.textContent = text; });
    });
    document.querySelectorAll('.trow').forEach(r => { const w = whyNot([B.byT.get(r.dataset.t)]); r.classList.toggle('dim', !!w); r.querySelector('[data-reason]').textContent = w; });
  }
  function paintMap(host) {
    const box = h('div', { class: 'pr-map' });
    box.append(h('p', { class: 'help', text: 'Every question type as a cell: filled with a tick when ready, a dot once met, dashed until you meet it; an orange corner dot is an open mistake. Tap a cell to pick it; picked cells are ringed in orange.' }));
    B.bank.domains.forEach(d => d.skills.forEach(s => {
      const r = h('div', { class: 'mrow' }, h('div', { class: 'mh' }, h('span', { text: s.name }), h('span', { class: 'meta', text: `${s.ready_n || 0} of ${typesOf(s).length} ready` })));
      const cells = h('div', { class: 'mcells' });
      // the type map's own looks (as Me's UI.atlas): an open type is met with its dot
      typesOf(s).forEach(t => {
        const c = UI.cell(t.state === 'ready' ? 'ready' : t.state === 'met' || t.state === 'open' ? 'met' : 'unmet', null, {
          label: `${t.name}, ${t.state === 'open' ? 'open mistake' : t.state || 'unmet'}`, open: t.state === 'open' || null, size: 'sm',
          onClick: () => { B.sel.has(t.template) ? B.sel.delete(t.template) : B.sel.add(t.template); markCustom(); preview(); paintTree(); } });
        c.setAttribute('aria-pressed', String(B.sel.has(t.template)));
        cells.append(c);
      });
      r.append(cells);
      box.append(r);
    }));
    host.append(box);
    paintBar();
  }
  function paintHabits(host) {
    const list = B.bank.habits || [];
    const box = h('div', { class: 'pr-habits' });
    // first use: the start drawing (the mark's corners, one lit) over its line
    if (!list.length) box.append(h('div', { class: 'pr-first' }, h('span', { 'aria-hidden': 'true', html: UI.spotArt ? UI.spotArt('start') : '' }),
      UI.empty(null, { text: 'Habits show up after about 30 answers.' })));
    list.forEach(x => box.append(h('div', { class: 'hrow' }, h('div', {}, h('b', { text: x.name || x.id }), h('p', { class: 'help', text: [x.tell, x.week ? `${x.week} this week` : null, x.here ? `${x.here} in your picks` : null].filter(Boolean).join(' · ') })),
      // a quiet way forward at the row's end, as Ready's Start (ten white buttons down the page read as a wall)
      h('button', { type: 'button', class: 'quiet go', onclick: () => create({ subject: B.subject, source: 'habit', habits: [x.id] }) }, 'Drill it', UI.icon('arrow', 16)))));
    host.append(box);
  }

  /* ---------------------------------------------------------------- settings: the Start window */
  // The page holds no settings. The bar's Start opens one window; the first tab is what matters, the rest are extra tweaks.
  const ctl = {};
  function group(host, label, id, cls) {
    const g = h('div', { class: 'sgrp' + (cls ? ' ' + cls : ''), id: id || null });
    if (label) g.append(h('span', { class: 'k', text: label }));
    host.append(g);
    return g;
  }
  // a switch with the shared ? beside it that says what it does
  function swInfo(host, o, text) {
    const row = h('div', { class: 'pr-swrow' });
    host.append(row);
    const sw = UI.switch(row, o);
    row.append(UI.why(text, { about: o.label }));
    return sw;
  }
  const helpLine = (host, text) => { const p = h('p', { class: 'help', text: text || '' }); host.append(p); return p; };
  function setPool(v) { B.st.pool = v; if (['marked', 'history'].includes(v)) B.st.exact = true; else if (['seen', 'saved'].includes(v)) B.st.exact = false; changed(); paintSettings(); }
  function changed() { markCustom(); savePrefs(); preview(); paintAvail(); paintSel(); }
  const SET_TABS = [
    { id: 'set', label: 'Set', paint: paintSetTab },
    { id: 'feedback', label: 'Feedback', paint: paintFeedbackTab },
    { id: 'miss', label: 'After a miss', paint: paintMissTab },
    { id: 'more', label: 'Order and more', paint: paintMoreTab },
  ];
  let win = null;   // the open window: { sheet, panel, tabs, tab, sum, l1, l2, go }
  function openStart(tab) {
    if (win) { if (tab) win.tabs.set(tab); return; }
    if (!B.bank) return;
    const w = win = { tab: SET_TABS.some(t => t.id === tab) ? tab : 'set' };
    w.sheet = UI.sheet({ title: 'Start practice', size: 'l', className: 'pset', body: (b, s) => {
      const th = h('div', { class: 'pset-tabs' });
      s.el.insertBefore(th, b);        // the tabs stay put while the panel scrolls
      w.panel = h('div', { class: 'pset-panel sset', role: 'tabpanel' });
      b.append(w.panel);
      w.tabs = UI.tabs(th, SET_TABS.map(t => ({ id: t.id, label: t.label, tabId: `pt-${t.id}` })), { label: 'Settings', value: w.tab, onChange: id => { w.tab = id; b.scrollTop = 0; paintSettings(); } });
      if (UI.edgeFade) UI.edgeFade(w.tabs.el, true);   // a phone scrolls the tabs sideways: soft edges where more are
      // under the close button: the same set as a printable worksheet (questions, then the key)
      th.append(h('button', { type: 'button', class: 'quiet', id: 'worksheet', text: 'Print PDF', onclick: worksheet }));
      paintWorksheet();
      paintSettings();
    }, actions: [{ label: 'Cancel', quiet: true }, { label: 'Start', primary: true, onClick: () => { launch(); } }] });
    const foot = w.sheet.foot;
    w.go = foot.lastElementChild;
    w.sum = h('div', { class: 'pset-sum', 'aria-live': 'polite' }, w.l1 = h('span', { class: 'l1' }), w.l2 = h('span', { class: 'l2' }));
    foot.insertBefore(w.sum, foot.firstChild);
    syncWin();
    w.tabs.el.querySelector('[aria-selected="true"]').focus({ preventScroll: true });
    w.sheet.closed.then(() => { win = null; });
  }
  // the footer: what the set is (the bar's line), the choices that shape it, or why it can't start
  function syncWin() {
    if (!win || !win.sum) return;
    const startB = $('#start'), off = startB.disabled && !starting, why = $('#reason').textContent;
    win.l1.textContent = B.l1Text || '';
    win.l2.textContent = off ? why : B.setText || '';
    win.l2.title = off ? '' : B.setText || '';
    win.l2.classList.toggle('why', !!off);
    win.go.disabled = off;
    win.go.title = off ? why : '';
  }
  // Start from the window (or Enter in a number field): the same body the bar's Start used to send
  function launch(extra) {
    if ($('#start').disabled) return;
    if (win) win.sheet.close();
    create(body(extra));
  }
  function paintSettings() {
    if (!win || !win.panel) return;
    const k = focusKey();
    Object.keys(ctl).forEach(x => delete ctl[x]);
    const t = SET_TABS.find(x => x.id === win.tab) || SET_TABS[0];
    win.panel.replaceChildren();
    win.panel.setAttribute('aria-labelledby', `pt-${t.id}`);
    t.paint(win.panel);
    paintHelpers(); paintFormatHelp(); paintPools(); syncWin();
    refocus(k);
  }
  // a repaint keeps keyboard focus on the same control
  function focusKey() {
    const a = document.activeElement;
    if (!a || !a.closest || !a.closest('.pset-panel')) return null;
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
  const lab = (host, text) => host.append(h('span', { class: 'lab', text }));

  // Tab 1, Set: where the questions come from, how many, how hard
  function paintSetTab(host) {
    const st = B.st;
    const grid = h('div', { class: 'sgrid' }), colL = h('div', { class: 'scol' }), colR = h('div', { class: 'scol' });
    grid.append(colL, colR);
    host.append(grid);
    // Questions from
    const g1 = group(colL, 'Questions from', 'sPool');
    const P = (B.preview && B.preview.pools) || B.bank.counts || {};
    const seen = P.seen || {};
    const F = isRW() ? 'Fresh passages' : 'Fresh numbers';
    const rows = [
      ['new', `New questions`, 'types', P.new, isRW() ? 'Questions you have never seen, each on its own passage.' : 'Generated for you now. You have never seen any of them.'],
      ['redo', `${F} on my open mistakes`, 'types', P.mistakes, 'Each type you fell for, twice. Two correct answers close a mistake.'],
      ['checks', 'Check-ins on mistakes you fixed', 'due', P.checks, 'A fixed mistake comes back once to prove it stayed fixed.'],
      ['review', `${F} on types due for review`, 'types', P.review, forecastText()],
      ['untried', `${F} on types I’ve never tried`, 'types', P.untried, null],
      ['seen', 'Questions I’ve seen', '', seen.any, null],
      ['marked', 'Marked for review', '', P.marked, 'A marked question you get right here leaves your Marked list, unless you tick Keep marked on it.'],
      ['saved', 'Saved', '', P.saved, 'Questions you saved for good. Twins test the skill; Exactly replays the question.'],
    ];
    rows.forEach(([v, label, unit, n, helper]) => {
      const off = n === 0 && st.pool !== v;
      const inp = h('input', { type: 'radio', name: 'pool', value: v, checked: st.pool === v ? true : null, disabled: off ? true : null });
      inp.addEventListener('change', () => setPool(v));
      const row = h('label', { class: 'choice-row' + (off ? ' off' : ''), 'aria-disabled': off ? 'true' : null, 'data-pool': v, 'data-unit': unit ? ' ' + unit : '' }, inp,
        h('span', { class: 'rl', text: label }), h('span', { class: 'rn choice-meta', text: n ? `${n0(n)}${unit ? ' ' + unit : ''}` : '' }));
      g1.append(tip(row, () => (row.classList.contains('off') ? reasonText('pool_empty') : helper)));   // a greyed pool says why on hover
      if (st.pool === v && ['seen', 'marked', 'saved'].includes(v)) {
        const sub = h('div', { class: 'sub' });
        const how = UI.seg(sub, [{ value: false, label: 'Fresh twins' }, { value: true, label: 'Exactly as they were' }], { value: !!st.exact, label: 'How', onChange: x => { st.exact = x; changed(); } });
        tip(how.btns[0], isRW() ? 'Each one comes back as another one like it: the same type, a fresh passage.' : 'Each one comes back as a twin: the same type and trap, new numbers.');
        tip(how.btns[1], 'The same questions again, exactly as they were.');
        if (v === 'seen') {
          UI.seg(sub, [{ value: 'any', label: 'Any', n: seen.any }, { value: 'missed', label: 'Missed', n: seen.missed }, { value: 'right', label: 'Right', n: seen.right }, { value: 'guessed', label: 'Guessed', n: seen.guessed }],
            { value: st.result, label: 'Result', onChange: x => { st.result = x; changed(); } });
          UI.seg(sub, [{ value: 'both', label: 'Practice and tests' }, { value: 'practice', label: 'Practice' }, { value: 'tests', label: 'Tests' }], { value: st.from, label: 'From', onChange: x => { st.from = x; changed(); } });
        }
        g1.append(sub);
      }
    });
    // Length: three kinds of set (the user): a number of questions, a number in a time limit, or a time limit alone
    const g2 = group(colR, 'Length', 'sCount');
    // an endless set on a clock (the old Sprint) is a time-only set now
    if (st.count === null && !st.box && st.timing !== 'off') { st.box = Math.max(5, Math.min(180, st.minutes || 15)); st.timing = 'off'; }
    const kind = st.box ? 'time' : st.timing === 'off' || st.count === null ? 'count' : 'both';
    UI.seg(g2, [{ value: 'count', label: 'Questions' }, { value: 'both', label: 'Questions in a time' }, { value: 'time', label: 'Time only' }],
      { value: kind, label: 'Kind of set', onChange: v => {
        if (v === 'count') { st.box = null; st.timing = 'off'; }
        else if (v === 'both') { st.box = null; if (st.count === null) st.count = 10; if (st.timing === 'off') st.timing = 'pace'; }
        else { st.box = st.box || 15; st.timing = 'off'; }
        changed(); paintSettings();
      } });
    // an empty field in the row, the size of a chip, instead of an "Other" chip: type a number, the chips let go
    const ownIn = (segCtl, min, max, value, label, set) => {
      const f = h('input', { class: 'segfield' + (value !== '' ? ' on' : ''), type: 'number', inputmode: 'numeric', min, max, value, 'aria-label': label });
      // reads "Other" like the other cells; a tap clears the word and leaves a blinking caret to type into
      f.placeholder = 'Other';
      f.addEventListener('focus', () => { f.placeholder = ''; });
      f.addEventListener('blur', () => { if (f.value === '') f.placeholder = 'Other'; });
      f.addEventListener('input', () => {
        const n = Math.round(+f.value);
        f.classList.toggle('on', f.value !== '');
        if (f.value === '' || !(n >= min && n <= max)) return;
        segCtl().set(null, true); set(n); changed();
      });
      f.addEventListener('change', () => { if (f.value !== '') { f.value = Math.max(min, Math.min(max, Math.round(+f.value || min))); f.dispatchEvent(new Event('input')); } });
      f.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); f.dispatchEvent(new Event('change')); launch(); } });
      return f;
    };
    if (kind !== 'time') {
      const COUNTS = [10, 30, 50];
      const cv = st.count === null ? 'inf' : COUNTS.includes(st.count) ? st.count : null;   // null: a typed number
      const own = ownIn(() => ctl.count, 1, 120, cv === null && typed.has('count') ? st.count : '', 'How many questions (1–120)', n => { st.count = n; typed.add('count'); });
      ctl.count = UI.seg(g2, COUNTS.map(n => ({ value: n, label: String(n) })).concat(kind === 'count' ? [{ value: 'inf', label: 'Endless' }] : []),
        { value: cv, label: 'How many questions', onChange: v => {
          own.value = ''; own.classList.remove('on'); typed.delete('count');
          st.count = v === 'inf' ? null : v; changed(); paintSettings();
        } });
      ctl.count.el.append(own);
      const inf = ctl.count.btns.find(x => x._opt.value === 'inf');
      if (inf) tip(inf, 'Stop whenever you like.');
    }
    if (kind === 'both') {
      const MINS = [10, 30, 60];
      const tv = st.timing === 'pace' ? 'pace' : MINS.includes(st.minutes) ? st.minutes : null;   // null: a typed number
      const mins = ownIn(() => tseg, 1, 180, tv === null && typed.has('mins') ? st.minutes : '', 'Minutes (1–180)', n => { st.timing = 'custom'; st.minutes = n; typed.add('mins'); });
      const tseg = UI.seg(g2, [{ value: 'pace', label: 'Test pace' }, ...MINS.map(m => ({ value: m, label: `${m} min` }))],
        { value: tv, label: 'Time limit', onChange: v => {
          mins.value = ''; mins.classList.remove('on'); typed.delete('mins');
          if (v === 'pace') st.timing = 'pace'; else { st.timing = 'custom'; st.minutes = v; }
          changed();
        } });
      tseg.el.append(mins);
      tip(tseg.btns[0], 'Paced to each question’s difficulty, like the test.');
    }
    if (kind === 'time') {
      const BOX = [10, 30, 60];
      const bv = BOX.includes(st.box) ? st.box : null;   // null: a typed number of minutes
      const own = ownIn(() => bseg, 5, 180, bv === null && st.box && typed.has('box') ? st.box : '', 'Minutes (5–180)', n => { st.box = n; typed.add('box'); });
      const bseg = UI.seg(g2, BOX.map(m => ({ value: m, label: `${m} min` })), { value: bv, label: 'Time limit: as many as you can', onChange: v => { own.value = ''; own.classList.remove('on'); typed.delete('box'); st.box = v; changed(); } });
      bseg.el.append(own);
    }
    ctl.countHelp = helpLine(g2, '');
    ctl.timeHelp = helpLine(g2, '');
    // Difficulty (P11)
    const g3 = group(colR, 'Difficulty', 'sDiff');
    const dz = UI.seg(g3, [{ value: 'forme', label: 'For me' }, { value: 'standard', label: 'Standard' }], { value: standard() ? 'standard' : 'forme', label: 'Difficulty', onChange: v => { st.zone = v === 'standard' ? 'off' : (st._zone || 'stretch'); changed(); paintSettings(); } });
    tip(dz.btns[0], 'Aimed at you: chosen from how you’ve done in each skill and how hard each type has been for everyone.');
    tip(dz.btns[1], 'Pick the tiers yourself.');
    if (!standard()) {
      const aim = UI.seg(g3, [{ value: 'warm', label: 'Warm-up' }, { value: 'stretch', label: 'Stretch' }, { value: 'challenge', label: 'Challenge' }], { value: st.zone, label: 'Aim', onChange: v => { st.zone = v; st._zone = v; changed(); paintBar(); } });
      ['80% or more likely right', '60–80% likely right', '35–60% likely right'].forEach((t, i) => tip(aim.btns[i], t));
      const unplaced = selectedSkills().filter(s => !s.placed);
      if (unplaced.length) {   // just "practice more"; the skills and counts are the hover text
        const tipTxt = `For me starts after 8 answers in a skill. Not placed yet: ${unplaced.slice(0, 4).map(s => `${s.short || s.name} (${s.to_place ?? 8} to go)`).join(', ')}${unplaced.length > 4 ? ` +${unplaced.length - 4}` : ''}. Those are served like module 1${isRW() ? '' : ' (7 Easy · 8 Medium · 7 Hard)'}.`;
        helpLine(g3, 'Practice more to unlock. ').append(UI.why(tipTxt, { about: 'For me' }));
      }
    } else {
      const tierCount = d => [...B.sel].filter(t => ((B.byT.get(t) || {}).tiers || []).includes(d)).length;
      ctl.tiers = UI.seg(g3, TIERS.map(d => ({ value: d, label: TIER_WORD[d], n: tierCount(d) })), { multi: true, value: st.tiers, label: 'Tiers', onChange: v => {
        if (!v.length) { ctl.tiers.set(st.tiers, true); ctl.tiers.el.classList.remove('shake'); void ctl.tiers.el.offsetWidth; ctl.tiers.el.classList.add('shake'); tierHelp.textContent = 'Keep at least one difficulty'; return; }
        st.tiers = v; tierHelp.textContent = ''; changed();
      } });
      const tierHelp = helpLine(g3, '');
      // the counts are Math's 22-question modules; the server plans R&W sets on the same shares, so R&W shows no counts
      const rw = isRW();
      const tmix = UI.seg(g3, [{ value: 'any', label: 'Any' }, { value: 'module1', label: rw ? 'Like module 1 (9/9/9)' : 'Like module 1 (7/8/7)' }, { value: 'module2_upper', label: rw ? 'Like the harder module 2 (4/10/13)' : 'Like the harder module 2 (3/8/11)' }], { value: st.tier_mix, label: 'Mix', onChange: v => { st.tier_mix = v; changed(); } });
      tip(tmix.btns[2], rw ? 'Aiming above 580? The harder module 2 is about half Hard.' : 'Aiming above 580? The harder module 2 is 11 Hard of 22.');
      UI.switch(g3, { checked: st.adaptive && st.order !== 'ramp', label: 'Adaptive: step up a tier after 2 first-try rights in a skill, down after a miss', disabled: st.order === 'ramp', onChange: v => { st.adaptive = v; changed(); } });
      if (st.order === 'ramp') helpLine(g3, 'Off while Order is Easiest first.');
    }
  }

  // Tab 2, Feedback: what you are told, and the help while you solve
  function paintFeedbackTab(host) {
    const st = B.st;
    const g6 = group(host, 'Answers shown', 'sFeedback');
    [['instant', 'After each question', 'The key, your mistake by name and the explanation, right away.'],
      ['retry', 'After I retry', 'Wrong? We name the mistake your answer comes from, not the key. Up to 3 tries; only the first counts.'],
      ['end', 'At the end, like a test', 'No feedback until you finish. Change answers, skip around, Check Your Work.']].forEach(([v, l, help]) => {
      const inp = h('input', { type: 'radio', name: 'feedback', value: v, checked: st.feedback === v ? true : null });
      inp.addEventListener('change', () => { st.feedback = v; if (v === 'end' && st.repairs === 'next') st.repairs = 'end'; changed(); paintSettings(); });
      g6.append(tip(h('label', { class: 'choice-row', 'data-feedback': v }, inp, h('span', { class: 'rl', text: l })), help));
    });
    const g6b = group(host, 'Asking how sure', 'sSure');
    tip(UI.seg(g6b, [{ value: 'ask', label: 'Ask' }, { value: 'off', label: 'Off' }], { value: st.confidence, label: 'Check asks how sure (Sure · Unsure · Guess)', onChange: v => { st.confidence = v; savePrefs(); } }).el,
      'Check asks how sure (Sure · Unsure · Guess). A Guess counts half and opens the explanation.');
    const g6c = group(host, 'While I solve', 'sSolve');
    UI.switch(g6c, { checked: st.hints, label: 'Hints before I answer', onChange: v => { st.hints = v; changed(); } });
    // R&W's prose choices cover with no answer field (question.js): predict, then show them
    const coverL = isRW() ? 'Predict before seeing choices' : 'Solve before seeing choices';
    lab(g6c, coverL);
    tip(UI.seg(g6c, [{ value: 'off', label: 'Off' }, { value: 'hard', label: 'Medium and Hard' }, { value: 'all', label: 'All' }], { value: st.cover, label: coverL, onChange: v => { st.cover = v; changed(); } }).el,
      isRW() ? 'The choices stay covered while you read and predict the answer in your own words.' : 'The options stay covered until you type what you got.');
    // per subject (prefs.practice): R&W's is off by default, its worked example being a bank question shown with its answer
    UI.switch(g6c, { checked: st.worked_first, label: 'New types: show me one worked first', onChange: v => { st.worked_first = v; changed(); } });
    // pace: moved here from the Set tab (the user); shown for timed sets only, as before
    if (st.box || (st.timing !== 'off' && st.count !== null)) {
      const gp = group(host, 'Pace', 'sPace');
      swInfo(gp, { checked: st.pace_alert, label: 'Pace alert on each question', onChange: v => { st.pace_alert = v; savePrefs(); } },
        'Every question has a time budget, worked out from the real test. With this on, the stopwatch turns amber once you go past the budget, so you notice when you are running slow. It never stops you.');
      swInfo(gp, { checked: st.two_passes, label: 'Two passes: offer Skip past 1.5× the budget', onChange: v => { st.two_passes = v; changed(); } },
        'The real-test habit of skipping a hard question and coming back to it. With this on, once you have spent one and a half times a question’s budget you are offered Skip, and skipped questions wait for a second pass at the end.');
    }
  }

  // Tab 3, After a miss: repairs, the final round, and what else joins the set
  function paintMissTab(host) {
    const st = B.st;
    const g7 = group(host, 'After a miss', 'sRepairs');
    const endM = st.feedback === 'end';
    tip(UI.seg(g7, [{ value: 'next', label: 'Next question', disabled: endM, why: endM ? 'In test mode, misses become a Fix set at the end.' : null }, { value: 'later', label: '3 questions later', disabled: endM }, { value: 'end', label: 'At the end' }, { value: 'off', label: 'Off' }],
      { value: st.repairs, label: 'After a miss', onChange: v => { st.repairs = v; changed(); } }).el, isRW() ? 'Another one like it follows a miss: the same type, a fresh passage.' : 'One like it follows a miss: the same trap, new numbers.');
    UI.triCheck(g7, { label: `Final round: re-ask what I missed at the end, ${fresh()}`, checked: st.final_round, onChange: v => { st.final_round = v; changed(); } });
    const g7a = group(host, 'Mix in reviews', 'sReviews');
    UI.seg(g7a, [{ value: 'off', label: 'Off' }, { value: 2, label: '2 per set' }, { value: 20, label: '20%' }], { value: st.review_mix, label: 'Mix in reviews', onChange: v => { st.review_mix = v; changed(); } });
    UI.triCheck(g7a, { label: 'Only from the skills I picked', checked: st.review_from === 'picked', onChange: v => { st.review_from = v ? 'picked' : 'all'; changed(); } });
    helpLine(g7a, forecastText());
    if (isRW()) return;   // word cards join Math sets only (drill.py)
    const g7b = group(host, 'Mix in due SAT words', 'sWords');
    tip(UI.seg(g7b, [{ value: 'off', label: 'Off' }, { value: 2, label: '2 per set' }, { value: 'all', label: 'All due' }], { value: st.words_mix, label: 'Mix in due SAT words', onChange: v => { st.words_mix = v; changed(); } }).el,
      'Reviewed at set breaks, filed to Words, never counted in Math.');
  }

  // Tab 4, Order and more: order, spread, format, and the defaults
  function paintMoreTab(host) {
    const st = B.st;
    const endless = st.count === null;   // a time-only set has no end to ramp to
    const selT = () => [...B.sel].map(t => B.byT.get(t)).filter(Boolean);
    // Mix-up interleaves look-alike types: offered only when the pick has some (most R&W types have none)
    const look = st.order === 'mixup' || selT().some(t => (t.lookalikes || []).length);
    const g8 = group(host, 'Order', 'sOrder');
    const ord = UI.seg(g8, [{ value: 'mixed', label: 'Mixed' }, { value: 'grouped', label: 'Grouped by skill' }, { value: 'ramp', label: 'Easiest first', disabled: endless, why: endless ? 'An endless set has no end to ramp to' : null },
      look ? { value: 'mixup', label: 'Mix-up' } : null].filter(Boolean),
      { value: st.order, label: 'Order', onChange: v => { st.order = v; changed(); paintSettings(); } });
    ['Never serves 3 questions of one type in a row.', 'One skill at a time.', 'By level where measured, by tier otherwise.', 'Look-alike types interleaved, so you learn which method applies.'].forEach((t, i) => tip(ord.btns[i], t));
    const g9 = group(host, 'Spread', 'sSpread');
    const oneDomain = new Set(selectedSkills().map(s => s.domain)).size <= 1;
    const spr = UI.seg(g9, [{ value: 'even', label: 'Even across skills' }, { value: 'blueprint', label: 'Like the test', disabled: oneDomain, why: oneDomain ? 'Your pick sits in one domain' : null }],
      { value: oneDomain ? 'even' : st.mix, label: 'Spread', onChange: v => { st.mix = v; changed(); } });
    tip(spr.btns[1], B.subject === 'rw' ? 'Information and Ideas 26%, Craft and Structure 28%, Expression of Ideas 20%, Standard English Conventions 26%.' : 'Algebra and Advanced Math 35% each, the other two 15%.');
    // Format, Desmos and official-question filters are Math's: R&W is all multiple choice, with no calculator and no
    // types built from official questions, so its tab has no Format group
    const official = allTypes().filter(t => t.official).length;
    if (!isRW()) {
      const g4 = group(host, 'Format', 'sFormat');
      const fv = st.formats.length === 2 ? 'both' : st.formats[0];
      UI.seg(g4, [{ value: 'both', label: 'Both' }, { value: 'mcq', label: 'Multiple choice' }, { value: 'spr', label: 'Grid-in' }], { value: fv, label: 'Format', onChange: v => { st.formats = v === 'both' ? ['mcq', 'spr'] : [v]; changed(); paintFormatHelp(); } });
      ctl.fmtHelp = helpLine(g4, '');
      const hasBox = (key, label) => UI.triCheck(g4, { label, checked: st.has.includes(key), onChange: v => { st.has = v ? [...st.has, key] : st.has.filter(x => x !== key); changed(); } });
      if (B.bank.desmos_way) hasBox('desmos', `Only types with a Desmos way (${selT().filter(t => t.desmos).length})`);
      if (official) hasBox('official', `Only types built from official questions (${official} of ${B.byT.size})`);
    }
    const g11 = group(host, 'Defaults', 'sDefaults');
    g11.append(tip(h('p', { class: 'lock' }, icon('save', 16), h('span', { text: 'Never repeats a question you were shown' })),
      'Nothing you were shown in a set, a test or the diagnostic comes back, except the exact replays you ask for. No practice question copies a College Board question.'));
    g11.append(h('div', { class: 'sfoot' }, h('span', { class: 'help', id: 'sfootNote', text: B.foot || (B.fromLink ? 'Settings from the link, not your defaults' : 'Saved as your defaults') }),
      h('button', { type: 'button', class: 'quiet', text: 'Reset to defaults', onclick: () => { B.st = Object.assign({}, DEF, isRW() ? { worked_first: false } : null); B.fromLink = false; B.foot = null; changed(); paintSettings(); } })));   // R&W's worked-first default is off (prefs.py)
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
    document.querySelectorAll('#sPool [data-pool]').forEach(r => {
      const v = r.dataset.pool, n = map[v];
      const rn = r.querySelector('.rn');
      if (rn) rn.textContent = n ? `${n0(n)}${r.dataset.unit || ''}` : '';
      const off = n === 0 && B.st.pool !== v;
      r.classList.toggle('off', off);
      if (off) r.setAttribute('aria-disabled', 'true'); else r.removeAttribute('aria-disabled');
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

  /* ---------------------------------------------------------------- the action bar: a short summary and Start (which opens the window) */
  const FB_WORD = { instant: 'answers after each', retry: 'answers after a retry', end: 'answers at the end' };
  const REP_WORD = { next: 'repairs next', later: 'repairs 3 later', end: 'repairs at the end', off: 'repairs off' };
  const dur = m => (m < 60 ? `~${Math.max(1, Math.round(m))} min` : `~${Math.round(m / 30) / 2} h`);
  // Line 1: how many and how long. Line 2: what is picked (B.sumText, also line 1's tooltip; the phone hides it). The choices are the window's footer (B.setText).
  function paintWorksheet() {   // a worksheet needs a fixed number of questions to print
    const ws = $('#worksheet');
    if (!ws) return;
    const open = B.st.count === null || !!B.st.box;
    ws.disabled = $('#start').disabled || open;
    ws.title = open ? 'Pick a number of questions to print' : 'Print this set with an answer key, or save it as a PDF';
  }
  function paintBar() {
    if (!B.bank) return;
    const st = B.st, p = B.preview;
    const skills = selectedSkills();
    const sprint = st.count === null && !st.box && st.timing === 'custom';
    // the set as a figure: "10" large (from 1280px, the hero's number), then the rest of the line on its baseline;
    // the text reads the same as before ("10 questions · ~14 min"), which the Start window's footer copies
    const [fig, unit] = st.box ? [String(st.box), '-minute set'] : sprint ? ['Sprint', ''] : st.count === null ? ['Endless', ''] : [String(st.count), st.count === 1 ? ' question' : ' questions'];
    const long = st.box ? (p && p.count ? `about ${plural(p.count, 'question')}` : null)
      : sprint || (st.timing === 'custom' && st.count !== null) ? `${st.minutes} min` : st.count !== null && p && p.minutes ? dur(p.minutes) : null;
    paintFig(fig, unit + (long ? ` · ${long}` : ''));
    const ts = [...B.sel].map(t => B.byT.get(t)).filter(Boolean).filter(fits).length;
    const diff = standard() ? (st.tiers.length === 3 ? 'all levels' : st.tiers.map(d => TIER_WORD[d]).join(' + ')) : `For me: ${{ warm: 'Warm-up', stretch: 'Stretch', challenge: 'Challenge' }[st.zone]}`;
    const fmt = B.subject === 'rw' ? null : st.formats.length === 2 ? 'both formats' : st.formats[0] === 'spr' ? 'grid-ins only' : 'multiple choice only';
    const gain = skills.reduce((a, s) => a + (s.gain || 0), 0);
    B.sumText = [plural(skills.length, 'skill'), plural(ts, 'type'), diff, fmt, gain ? `works on ≈ +${Math.round(gain)}` : null].filter(Boolean).join(' · ');
    paintGlyphs(skills);
    const time = st.timing === 'off' ? 'Untimed' : st.timing === 'pace' ? 'Test pace' : sprint ? `Sprint ${st.minutes} min` : `Timed ${st.minutes} min`;
    B.setText = [time, FB_WORD[st.feedback], REP_WORD[st.repairs], st.final_round ? 'final round on' : null, st.review_mix !== 'off' ? `${st.review_mix === 2 ? '2 reviews' : '20% reviews'} mixed in` : null,
      { mixed: 'mixed', grouped: 'grouped', ramp: 'easiest first', mixup: 'mix-up' }[st.order]].filter(Boolean).join(' · ');
    // the line under the set: the skills are the chips and the tree head's count, so it starts at the types
    $('#l2').textContent = B.sel.size ? B.sumText.split(' · ').slice(1).join(' · ') : '';
    const startB = $('#start'), reason = $('#reason');
    if (starting) return;
    let why = '';
    if (!B.sel.size && !B.presetBody) why = 'Pick at least one skill';
    else if (!p) why = '';
    else if (!p.servable) why = p.reason === 'offline' ? 'The server is not answering.' : reasonText(p.reason);
    startB.disabled = !!why || !p;   // disabled, not "Loading…", until the first preview answers
    startB.textContent = 'Start practice';
    reason.textContent = why;
    reason.hidden = !why;
    paintWorksheet();
    syncWin();
  }

  // the set's skills as topic glyph chips in the hero, on one line then "+3" (the critic: no chip alone on a line):
  // as many as fit whole, so a name never ends in an ellipsis (only a lone chip may); shown from 1280px (CSS)
  function paintGlyphs(skills) {
    const host = $('#glyphs');
    const fit = n => host.replaceChildren(...skills.slice(0, n).map(sk => h('span', { class: 'chip', title: sk.name }, UI.glyph(sk.slug), h('span', { text: label(sk) }))),
      skills.length > n ? h('span', { class: 'more', text: `+${skills.length - n}` }) : '');
    let n = Math.min(3, skills.length);
    fit(n);
    while (n > 1 && [...host.querySelectorAll('.chip > span')].some(x => x.scrollWidth > x.clientWidth)) fit(--n);
  }
  // the hero's figure: a change of number rolls (UI.roll: only the digits that changed, up on a rise), a word swaps;
  // the first paint just shows it. B.l1Text is the line as text, for the Start window's footer
  function paintFig(fig, rest) {
    const l1 = $('#l1');
    let f = l1.querySelector('.fig');
    if (!f) { l1.replaceChildren(f = h('b', { class: 'fig' }), ''); B.fig = null; }
    if (B.fig !== fig) {
      if (B.fig && /^\d+$/.test(B.fig) && /^\d+$/.test(fig)) UI.roll(f, +fig); else f.textContent = fig;
      B.fig = fig;
    }
    l1.lastChild.nodeValue = rest;
    B.l1Text = fig + rest;
  }

  /* ---------------------------------------------------------------- starting */
  let starting = false;
  async function create(b, btn) {
    if (starting) return;
    starting = true;
    const startB = btn || $('#start');
    const kids = [...startB.childNodes], own = startB.matches('.pill, .btn');   // a pill or button spins after 300ms (ui.css)
    startB.setAttribute('aria-busy', 'true');
    if (!own) startB.textContent = 'Building…';
    $('#abarErr').hidden = true;
    try {
      const r = await UI.api('/drill', { method: 'POST', body: b });
      const id = r.id || r.session;
      location.href = `/practice/session/?id=${encodeURIComponent(id)}${b.source === 'worksheet' ? '&print=1' : ''}`;
    } catch (e) {
      starting = false;
      startB.removeAttribute('aria-busy'); if (!own) startB.replaceChildren(...kids);
      const msg = e.detail && e.detail.reason ? reasonText(e.detail.reason) : e.message;
      const err = $('#abarErr');
      err.replaceChildren(h('span', { text: `Couldn’t start: ${msg}` }), ' ', h('button', { type: 'button', class: 'quiet', text: 'Try again', onclick: () => create(b, btn) }));
      err.hidden = false;
      paintBar();
    }
  }
    const worksheet = () => launch({ source: 'worksheet', feedback: 'end', timing: 'off', repairs: 'end', final_round: false });

  /* ---------------------------------------------------------------- deep links (1.10) */
  function fromLink() {
    const g = k => url.get(k);
    if (![...url.keys()].some(k => !['share', 'subject', 'search', 'theme'].includes(k))) return false;
    const st = B.st;
    const list = k => (g(k) || '').split(',').map(x => x.trim()).filter(Boolean);
    // ?topics= (Today, Plan, Results, the runner) and ?topic= (/s) are other names for ?skills=; ?domain= (Today) is its skills
    const skills = [...list('skills'), ...list('topics'), ...list('topic'),
      ...(g('domain') ? [...B.skills.values()].filter(sk => sk.domain === g('domain')).map(sk => sk.slug) : [])];
    if (skills.length || g('types')) {
      B.sel.clear();
      skills.forEach(s => { const sk = B.skills.get(s); if (sk) setSkill(sk, true); });
      list('types').forEach(t => { if (B.byT.has(t)) B.sel.add(t); });
    }
    if (g('count')) st.count = g('count') === '0' || g('count') === 'inf' ? null : Math.max(1, Math.min(120, +g('count') || 10));
    if (g('box')) st.box = Math.max(5, Math.min(180, +g('box')));
    if (g('pool')) st.pool = { mistakes: 'redo' }[g('pool')] || g('pool');
    if (g('result')) st.result = g('result');
    if (g('marked') === '1') st.pool = 'marked';
    if (g('from')) st.from = g('from');
    if (g('tiers')) { st.tiers = list('tiers').filter(x => TIERS.includes(x)); st.zone = 'off'; }
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
    u.searchParams.set('subject', B.subject);
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
  // Your sets is its own fold under the tree: open it, then scroll
  function showSets() { $('#setsFold').open = true; $('#setsSec').scrollIntoView({ behavior: 'smooth' }); }
  function setsTab(v) { setsTabV = v; setsLimit = 10; paintSets(true); }
  async function loadSets() {
    try { B.sets = await UI.api('/drill', { quiet: true }); } catch (_) { B.sets = { active: [], recent: [], shared: [], error: true }; }
    try { B.owned = await UI.api('/sets', { quiet: true }); } catch (_) { B.owned = []; }
  }
  const setTitle = r => (r.topics || []).map(skName);
  // the rows sit in one list that is kept between paints, so a change made here (a tab, a filter, Show more, Stop
  // sharing) glides: rows that stay slide, new ones rise, gone ones fade (UI.glide); the first paint just shows
  let setList = null;
  function paintSets(move) {
    const host = $('#sets');
    if (!B.sets) { host.replaceChildren(UI.skel(null, 'rows:3')); setList = null; return; }
    const S = B.sets;
    const owned = (B.owned || []).filter(x => x.kind === 'set' && !x.revoked);
    const recent = (S.recent || []).filter(r => r.answered > 0);
    const tabHost = h('div', {});
    UI.seg(tabHost, [{ value: 'active', label: 'In progress', n: (S.active || []).length }, { value: 'recent', label: 'Finished', n: recent.length }, { value: 'shared', label: 'Shared by me', n: owned.length }, { value: 'official', label: 'Official questions', n: (S.official || []).length }],
      { value: setsTabV, label: 'Your sets', onChange: setsTab });
    const segEl = tabHost.querySelector('.seg');
    if (segEl && UI.edgeFade) UI.edgeFade(segEl, true);   // a phone scrolls the tabs sideways: soft edges where more are
    if (S.error) { host.replaceChildren(tabHost); setList = null; UI.cardError(host, async () => { await loadSets(); paintSets(); }, 'Your sets didn’t load.'); return; }
    const head = [tabHost];
    let rows = [];
    if (setsTabV === 'active') rows = S.active || [];
    else if (setsTabV === 'recent' && recent.length) {   // filters only once there is something to filter
      const f = h('div', { class: 'pr-filt' });
      const skSel = h('select', { class: 'field sm', 'aria-label': 'Skill' }, h('option', { value: '', text: 'All skills' }), [...B.skills.values()].map(s => h('option', { value: s.slug, text: s.name, selected: setsFilter.topic === s.slug ? true : null })));
      const kind = h('select', { class: 'field sm', 'aria-label': 'Kind' }, [['', 'All'], ['drill', 'Practice'], ['shared', 'Shared with me'], ['challenge', 'Challenge']].map(([v, l]) => h('option', { value: v, text: l, selected: setsFilter.kind === v ? true : null })));
      const res = h('select', { class: 'field sm', 'aria-label': 'Result' }, [['', 'All'], ['1', 'With misses']].map(([v, l]) => h('option', { value: v, text: l, selected: (setsFilter.misses ? '1' : '') === v ? true : null })));
      [skSel, kind, res].forEach(x => x.addEventListener('change', () => { setsFilter = { topic: skSel.value, kind: kind.value, misses: res.value === '1' }; paintSets(true); }));
      f.append(skSel, kind, res);
      head.push(f);
      rows = recent.filter(r => (!setsFilter.topic || (r.topics || []).includes(setsFilter.topic)) && (!setsFilter.kind || (setsFilter.kind === 'shared' ? r.source === 'shared' : r.kind === setsFilter.kind))
        && (!setsFilter.misses || r.right < r.answered));
    } else if (setsTabV === 'recent') rows = [];
    else if (setsTabV === 'shared') rows = owned;
    else rows = S.official || [];
    const filtered = setsTabV === 'recent' && recent.length > 0 && !rows.length;
    const empty = { active: 'Nothing in progress. A set you leave halfway waits here.', recent: 'Sets you finish show up here, with their review.',
      shared: 'Share a finished set, then see how friends did.', official: 'College Board questions you log from Review show up here.' }[setsTabV];
    const list = setList && setList.isConnected ? setList : (setList = h('div', { class: 'pr-setlist' }));
    const fill = () => {
      host.replaceChildren(...head, list);
      const kids = [];
      // a filter that leaves nothing says so, with Clear (no drawing, no sample); a first-use empty (nothing finished
      // or shared yet) shows kit's empty state with one dimmed example of the row to come; the others one line
      if (filtered) kids.push(h('div', { class: 'pr-none', 'data-key': 'none' }, h('p', { class: 'help', text: 'No finished set matches these filters.' }),
        h('button', { type: 'button', class: 'quiet', text: 'Clear filters', onclick: () => { setsFilter = { topic: '', kind: '', misses: false }; paintSets(true); } })));
      else if (!rows.length) {
        const first = setsTabV === 'shared' ? !owned.length : setsTabV === 'recent';
        const e = UI.empty(null, { text: empty, sample: first ? () => sampleRow(setsTabV) : null });
        e.dataset.key = `empty-${setsTabV}`;
        kids.push(e);
      } else {
        rows.slice(0, setsLimit).forEach(r => kids.push(setsTabV === 'shared' ? ownedRow(r) : setRow(r)));
        if (rows.length > setsLimit) kids.push(h('button', { type: 'button', class: 'quiet', 'data-key': 'more', text: `Show ${Math.min(20, rows.length - setsLimit)} more`, onclick: () => { setsLimit += 20; paintSets(true); } }));
      }
      list.replaceChildren(...kids);
    };
    if (move && list.isConnected) UI.glide(list, fill); else fill();
  }
  function sampleRow(tab) {
    const cells = tab === 'shared' ? ['Oct 12, 18:40', h('span', { class: 'skills', text: '10 questions' }), h('span', { class: 'meta', text: 'Twins for each person' }), 'Opened 3', '', '', '']
      : ['Oct 12, 18:40', h('span', { class: 'skills' }, h('span', { class: 'badge soft', text: 'Circles' }), h('span', { class: 'badge soft', text: 'Percentages' })),
        h('span', { class: 'meta', text: 'Untimed · After each' }), '10 / 10', '8 right · 80%', '12:30', h('span', { class: 'acts', text: 'Review' })];
    return h('div', { class: 'setrow' }, cells.map(c => (typeof c === 'string' ? h('span', { text: c }) : c)));
  }
  function setRow(r) {
    const chips = setTitle(r);
    const ch = r.kind === 'challenge' || r.kind === 'contest';
    const mode = [r.timed ? `Timed${r.seconds_left !== null && r.seconds_left !== undefined ? '' : ''}` : 'Untimed', { instant: 'After each', retry: 'Retry', end: 'Test mode' }[r.feedback] || ''].filter(Boolean).join(' · ');
    const acts = h('div', { class: 'acts' });
    const go = `/practice/session/?id=${encodeURIComponent(r.id)}`;
    if (!r.finished) {
      acts.append(h('a', { class: 'btn sm', href: go, text: 'Resume' }), h('button', { type: 'button', class: 'quiet', text: 'End', onclick: async () => {
        if (!(await UI.confirm({ title: 'End this set?', text: 'End this set and see its summary?', confirm: 'End set' }))) return;
        try { await UI.api(`/drill/${r.id}/finish`, { method: 'POST', body: {} }); location.href = go; } catch (e) { UI.toast(`Couldn’t end it: ${e.message}`); }
      } }));
    } else if (ch) acts.append(h('a', { class: 'quiet', href: '/challenge/', text: 'Challenge' }), h('a', { class: 'quiet', href: go, text: 'Review' }));
    else {
      const more = h('button', { type: 'button', class: 'ibtn', 'aria-label': 'More for this set' }, UI.icon('more', 18));
      // the list holds both subjects: each row's actions follow its own set's subject, never the tab's
      UI.menu.bind(more, () => [
        { label: 'Rematch', sub: `Same types, ${fresh(r.subject)}`, onClick: () => confirmCopy(r.id, 'rematch', r.subject) },
        { label: 'Retake exact', onClick: () => confirmCopy(r.id, 'retake', r.subject) },
        { label: 'Same settings', onClick: () => create({ again: r.id, source: 'builder', subject: r.subject }) },
        { label: 'Share', onClick: () => shareSheet(r.id, r.subject) },
        { label: 'Print', href: `${go}&print=1` },
      ], { label: 'This set' });
      acts.append(h('a', { class: 'quiet', href: go, text: 'Review' }), more);
    }
    return h('div', { class: 'setrow', 'data-key': r.id },
      h('span', { text: when(r.started) }),
      h('span', { class: 'skills' }, ch ? h('span', { class: 'badge', text: 'Challenge' }) : null, chips.slice(0, 3).map(c => h('span', { class: 'badge soft', text: c })), chips.length > 3 ? h('span', { class: 'badge soft', text: `+${chips.length - 3}` }) : null),
      h('span', { class: 'meta', text: mode }),
      h('span', { text: r.total ? `${r.answered} / ${r.total}` : `${r.answered} answered` }),
      h('span', { text: r.answered && Number.isFinite(r.right) ? `${r.right} right · ${pct(r.right / r.answered)}` : NONE }),   // a set in progress may have no tally yet
      h('span', { text: mmss(r.ms) }), acts);
  }
  async function confirmCopy(sid, kind, subject) {
    const retake = kind === 'retake';
    const clean = h('input', { type: 'checkbox', checked: retake ? true : null });
    UI.sheet({ title: retake ? 'Retake these exact questions?' : `Rematch: same types, ${fresh(subject)}?`, size: 's', body: b => {
      b.append(h('p', { text: retake ? 'Starts a new copy of this set with the same questions. It tests memory as much as skill. This one stays in your history.' : `The same types in the same order, with ${fresh(subject)}. We compare the two question by question.` }),
        h('label', { class: 'check' }, clean, h('span', { text: 'Start clean: hide my highlights, notes, strikes and rules on this copy' })));
    }, actions: [{ label: 'Cancel', quiet: true }, { label: retake ? 'Retake' : 'Rematch', primary: true, onClick: () => { create({ subject, source: retake ? 'builder' : 'rematch', [kind]: sid, clean: clean.checked }); } }] });
  }
  function shareSheet(sid, subject) {
    let exact = false;
    UI.sheet({ title: 'Share this set', size: 's', body: b => {
      UI.seg(b, [{ value: false, label: 'Twins for each person' }, { value: true, label: 'Exactly these questions' }], { value: false, label: 'What they get', onChange: v => { exact = v; } });
      b.append(h('p', { class: 'help', text: `Twins: each friend gets their own ${isRW(subject) ? 'questions' : 'numbers'} on the same types in the same order, so answers can’t be passed around. You see how they did per question.` }),
        h('p', { class: 'help' }, 'Want to race on the clock? ', h('a', { href: '/compete/', text: 'Race friends on this instead' }), '.'));
    }, actions: [{ label: 'Cancel', quiet: true }, { label: 'Copy link', primary: true, onClick: async () => {
      try {
        const r = await UI.api('/sets', { method: 'POST', body: { kind: 'set', session: sid, cfg: { fresh: !exact } } });
        UI.copyText(r.url || `${location.origin}/practice/?share=${r.code}`, { toast: exact ? 'Link copied: friends get these exact questions' : 'Link copied: each friend gets their own twins' });
        loadSets().then(() => paintSets(true));
      } catch (e) { UI.toast(`Couldn’t share it: ${e.message}`); return false; }
    } }] });
  }
  function ownedRow(r) {
    const link = r.url || `${location.origin}/practice/?share=${r.code}`;
    return h('div', { class: 'setrow', 'data-key': r.code },
      h('span', { text: when(r.created) }),
      h('span', { class: 'skills', text: r.title || `${plural(r.count || 0, 'question')}` }),
      h('span', { class: 'meta', text: r.fresh ? 'Twins for each person' : 'Exact questions' }),
      h('span', { text: `Opened ${r.opened || 0}` }), h('span', {}), h('span', {}),
      h('div', { class: 'acts' },
        h('button', { type: 'button', class: 'quiet', text: 'Results', onclick: () => sharedResults(r.code) }),
        h('button', { type: 'button', class: 'quiet', text: 'Copy link', onclick: () => UI.copyText(link, { toast: 'Link copied' }) }),
        h('button', { type: 'button', class: 'quiet', text: 'Stop sharing', onclick: async () => {
          if (!(await UI.confirm({ title: 'Stop sharing?', text: 'The link stops working for everyone. Results stay yours.', confirm: 'Stop sharing', destructive: true }))) return;
          try { await UI.api(`/sets/${r.code}`, { method: 'DELETE' }); await loadSets(); paintSets(true); } catch (e) { UI.toast(`Couldn’t stop it: ${e.message}`); }
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
      UI.tile(tiles, { label: 'Average', value: d.avg_right !== undefined && d.avg_right !== null ? `${(+d.avg_right).toFixed(1)} / ${d.count}` : NONE });
      UI.tile(tiles, { label: 'Median time', value: d.median_ms ? mmss(d.median_ms) : NONE });
      b.append(tiles);
      UI.table(b, [{ key: 'n', label: '#', num: true }, { key: 'type_name', label: 'Type' }, { key: 'difficulty', label: 'Difficulty' },
        { key: 'right', label: 'Right', render: q => `${q.right}/${q.asked}` },
        { key: 'top', label: 'Most common wrong answer', render: q => (q.top_wrong ? `${cap(q.top_wrong.reason || q.top_wrong.norm || '')} (${q.top_wrong.count})` : NONE) }], d.questions || [], { compact: true, label: 'Per question' });
      UI.table(b, [{ key: 'name', label: 'Taker', render: (t, i) => t.name || `Student ${i + 1}` }, { key: 'right', label: 'Score', render: t => `${t.right} / ${t.asked}` }, { key: 'ms', label: 'Time', render: t => mmss(t.ms) }],
        takers.map((t, i) => Object.assign({ _i: i }, t)).map(t => Object.assign(t, { name: t.name || `Student ${t._i + 1}` })), { compact: true, label: 'Takers' });
    } });
  }

  /* ---------------------------------------------------------------- loading, errors, painting */
  function paintAll() { paintPresets(); paintTree(); paintSettings(); paintSel(); paintBar(); preview(); }
  function skeleton() {
    const host = $('#treeBody');
    host.replaceChildren();
    host.className = 'skel-tree dgrid';
    for (let i = 0; i < 4; i++) host.append(h('div', { class: 'dcard skel-card' }, UI.skel(null, 'lines:3')));
  }
  async function load() {
    skeleton();
    UI.subject.set(B.subject);   // remembered and in the URL, so Review, Tests and a reload open on it too
    paintSubject();
    let prefs = {};
    try { prefs = await UI.prefs(); } catch (_) {}
    B.prefs = prefs || {};
    B.st = fromPrefs(B.prefs);
    B.saved = Object.assign({}, B.st);
    try { B.me = await UI.me(); } catch (_) { B.me = null; }
    if (!(await useSubject(true))) return;
    await loadSets();
    paintHead(); paintBanners(); paintSets(); paintReady();
  }
  const banks = {}, QPH = $('#q').placeholder;
  // load (once) and show the bank of the tab's subject; first: the page's opening load, which honours a shared link
  async function useSubject(first = false) {
    skeleton();
    let bank;
    try { bank = banks[B.subject] || (banks[B.subject] = await UI.api(`/bank?subject=${B.subject}`, { quiet: true })); }
    catch (e) {
      const host = $('#treeBody');
      host.className = '';
      host.replaceChildren();
      UI.cardError(host, () => load(), 'The server is not answering.');
      $('#start').disabled = true; $('#start').textContent = 'Start practice';
      $('#l1').replaceChildren();   // no skeleton left behind: the reason says why
      $('#reason').textContent = 'The server is not answering.'; $('#reason').hidden = false;
      return false;
    }
    B.bank = bank;
    // the command line's skill words are Math's (UI.parseSet): R&W's box offers the search alone
    $('#q').placeholder = isRW() ? 'Search a skill or a question type' : QPH;
    B.byT.clear(); B.skills.clear(); B.sel.clear();
    bank.domains.forEach(d => d.skills.forEach(s => { s.domain = s.domain || d.name; B.skills.set(s.slug, s); (s.types || []).forEach(t => { t.topic = t.topic || s.slug; B.byT.set(t.template, t); }); }));
    B.fromLink = first && fromLink();
    if (!B.fromLink) applyPreset('coach', null);
    else { B.preset = 'custom'; linkNote('Settings from the link, not your defaults'); }
    paintHead(); paintTreeHead(); paintAll();
    UI.motion.enter($('#treeBody'), 'fade');   // the skills fade in over their skeleton (MOTION M2), on load and on a subject switch
    if (first && url.get('search')) { $('#q').value = url.get('search'); onSearch(); }
    return true;
  }

  $('.pr-sicon').append(UI.icon('search', 20));
  $('#q').addEventListener('input', onSearch);
  $('#q').addEventListener('keydown', searchKeys);
  // Your sets' fold, remembered (first time: as the old Presets fold was, since it lived inside it)
  [['#setsFold', 'satf.pr.sets', ls.get('satf.pr.presets', false)]].forEach(([sel, key, def]) => {
    const d = $(sel);
    d.open = !!ls.get(key, def);
    d.addEventListener('toggle', () => ls.set(key, d.open));
  });
  // below 1280px the bar is fixed: the page keeps its height free at the bottom
  try { new ResizeObserver(() => $('#main').style.setProperty('--abar-h', `${$('#abar').offsetHeight}px`)).observe($('#abar')); } catch (_) {}
  // the search's edge sweeps once on load and then rests lit (CSS, BUILD rule 13): nothing to pause any more
  $('#start').addEventListener('click', () => { if (!$('#start').disabled) openStart(); });   // the bar's Start opens the window; the quick paths (Ready cards, the search's Enter, Your sets) still create directly
  tip($('#l1'), () => B.sumText || '');
  if (UI.keys && UI.keys.register) {
    try { UI.keys.register('page', { '/': { does: 'Search or build a set', run: () => { $('#q').focus(); } } }, { label: 'Practice' }); } catch (_) {}
  } else addEventListener('keydown', e => { if (e.key === '/' && !/input|textarea|select/i.test((document.activeElement || {}).tagName)) { e.preventDefault(); $('#q').focus(); } });
  load();
})();
