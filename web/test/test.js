/* ============================================================================
   SAT Freshman -- the test window, /test/?s=ID (spec 3.4 section 4; tests.md X1-X14, X23)

   One GET /api/session/{id} decides the screen:
     lobby    not begun, paused, left without Save and exit, or expired while away (4.2)
     runner   UI.runner in exam mode (F3) draws the module; this file wires its callbacks
              to the sitting endpoints through one UI.saveQueue (answers and state, with
              X1's pid / el / hid / off stamps), plus a bare stamp every 30 s and on pagehide
     between  module 1 handed in, module 2 not begun: UI.between (X11)
     timeup   the clock hit 0 (4.7)       done   the hand-in moment (X12)
     problem  404 / 403 / network / discarded
   No questions exist on the page before Begin or while paused: the server sends none.
   ========================================================================== */
(() => {
  const h = UI.h, $ = s => document.querySelector(s);
  const url = new URLSearchParams(location.search);
  const sid = url.get('s');
  if (!sid) { location.replace('/tests/?start=diagnostic'); return; }

  const view = $('#view'), runHost = $('#run');
  const api = (p, o) => UI.api(p, o);
  const path = p => `/session/${encodeURIComponent(sid)}${p || ''}`;
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  const mmss = s => UI.mmss(Math.max(0, Math.round(s || 0)));
  const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + 's'}`;
  const cap = t => (t ? t[0].toUpperCase() + t.slice(1) : '');
  const reduced = () => (UI.reduced ? UI.reduced() : matchMedia('(prefers-reduced-motion: reduce)').matches);
  const ss = {
    get(k) { try { return sessionStorage.getItem(k); } catch (_) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, v); } catch (_) {} },
  };
  const icon = (name, size = 18) => h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.svg(UI.ICON[name] || UI.ICON.dot || '', size) });
  const subjectLabel = s => ((UI.SUBJECT || {})[s] || {}).label || cap(s || 'math');
  const LIVE = `satf.test.live.${sid}`;
  let wantReview = location.hash === '#review';     // Tests' "Hand in" on an in-progress row
  const TRAINING_AIDS = [
    ['pace', 'Pace guide', 'Paced to your own speed on the progress strip and under the clock'],
    ['nudges', 'Coaching nudges', 'The time sink, the last-minute blanks and the grid-in form'],
    ['confidence', 'Confidence tags', 'Sure, Unsure or Guess on each question; the report shows how often sure was right'],
    ['cover', 'Cover the choices', 'Work each multiple-choice question out, then reveal the options (V)'],
    ['reveal_route', 'Tell me my module 2', 'Say which module 2 you earned, with your margin'],
    ['type_notes', 'Your type notes', 'Your own note on a kind of question shows under a later one of that kind'],
  ];
  const TIMINGS = [
    ['official', 'Official', 1], ['x1.5', 'Time and a half', 1.5], ['x2', 'Double time', 2],
    ['untimed', 'Untimed', null], ['x0.85', 'Tight clock (−15%)', 0.85],
  ];

  let S = null;                 // the session payload
  let run = null, queue = null, liveGate = null, openGate = null;
  let cellsM1 = null, labelsM1 = null, qidsM1 = null, paceM1 = null, lastSummary = null, lastRoute = null;
  let handing = false, endAtSent = false, stampT = 0;
  const awaySent = { ms: 0, n: 0 };

  /* ---------------- helpers over the payload */
  const two = () => (S.modules || []).length > 1;
  const lastModule = () => !two() || (S.module || 1) >= (S.modules || []).length;
  const training = () => S.conditions === 'training';
  const qidsAnswered = () => Object.values(S.answers || {}).filter(v => v !== null && v !== undefined && v !== '').length;
  const marked = () => Object.entries(S.qstate || {}).filter(([k, v]) => k !== '_session' && v && v.marked).length;
  const baseSeconds = () => {
    if (S.duration) return Math.round(S.duration / (S.factor || 1));
    return ['custom', 'diagnostic'].includes(S.kind) ? (S.question_count || 22) * 95 : 2100;
  };
  const title = () => `${S.kind_label}${S.number ? ` #${S.number}` : ''}`;
  function timingText(t, per) {
    const b = baseSeconds();
    const each = per || (two() ? ' for each module' : '');
    if (t === 'untimed') return 'Untimed · the clock counts up';
    const f = (TIMINGS.find(x => x[0] === t) || [])[2] || 1;
    const t0 = Math.round(b * f);
    const clock = `${Math.floor(t0 / 60)}:${String(t0 % 60).padStart(2, '0')}`;
    const extra = { 'x1.5': ' · time and a half', x2: ' · double time', 'x0.85': ' · tight clock' }[t] || '';
    if (S.kind === 'custom' && t === 'official') return `95 s a question · ${clock}`;
    return `${clock}${each}${extra}`;
  }
  function rankLine() {
    if (S.contest) return S.contest.ranked === false ? `Contest · won’t rank${S.contest.why ? ': ' + S.contest.why : ''}` : 'Contest · this sitting counts on the board';
    if (training()) return 'Training · keeps its score, doesn’t rank';
    if (S.ranked === false && S.why) return `Test-day · won’t rank: ${S.why}`;
    return 'Test-day · this sitting ranks among first sittings';
  }
  const elNow = () => {
    const t = run && run.timer;
    if (!t) return null;
    if (t.timed) return Math.max(0, ((S.duration || 0) - t.left) * 1000);
    return Math.max(0, (t.elapsed || 0) * 1000);
  };

  /* ---------------- the save queue: answers and state, in order, stamped (X1) */
  const TO_SERVER = { ask: 'box', given: 'highlight', ignore: 'strike', under: 'underline' };
  const FROM_SERVER = Object.fromEntries(Object.entries(TO_SERVER).map(([a, b]) => [b, a]));
  const marksOut = list => (list || []).map(m => {
    const o = { start: m.start, end: m.end, style: TO_SERVER[m.style] || m.style, at: !m.addr || m.addr === 's' ? 'stem' : m.addr };
    if (m.note) o.note = m.note;
    return o;
  });
  const marksIn = list => (list || []).map(m => ({ addr: !m.at || m.at === 'stem' ? 's' : m.at, start: m.start, end: m.end,
    style: FROM_SERVER[m.style] || m.style, note: m.note || '' }));
  function makeQueue() {
    if (queue) return queue;
    liveGate = new Promise(r => { openGate = r; });
    queue = UI.saveQueue(sid, async (it, st) => {
      await liveGate;
      const body = Object.assign({}, it.body);
      const el = body._el;
      delete body._el;
      const stamps = { pid: st.pid, hid: st.hid, off: st.off };
      const e2 = el ?? st.el;
      if (Number.isFinite(e2)) stamps.el = Math.round(e2);
      if (it.kind === 'answer') {
        return api(path('/answer'), { method: 'POST', quiet: true,
          body: Object.assign({ question_id: it.qid, answer: body.value ?? null, made_left: body.made_left ?? null }, stamps) });
      }
      const q = it.qid && !it.qid.startsWith('_') ? { question_id: it.qid } : {};
      return api(path('/state'), { method: 'POST', quiet: true, body: Object.assign(q, body, stamps) });
    }, { el: elNow, onConflict: conflict, onDrop: (e, it) => { if (it.kind === 'answer') toast('One answer couldn’t be saved: ' + (e.message || 'refused')); } });
    return queue;
  }
  const stampsNow = () => {
    const st = queue ? queue.stamps() : {};
    const out = {};
    if (st.pid) Object.assign(out, { pid: st.pid, hid: st.hid, off: st.off });
    const e = elNow();
    if (Number.isFinite(e)) out.el = Math.round(e);
    return out;
  };
  function putState(qid, patch) {
    if (!queue || !patch || !Object.keys(patch).length) return;
    const e = elNow();
    queue.state(qid, Object.assign({}, patch, Number.isFinite(e) ? { _el: Math.round(e) } : {}));
  }
  function conflict(e) {
    const why = String((e && (e.detail || e.message)) || '');
    if (/time is up/.test(why)) return timeUp();
    if (/finished/.test(why)) return finishedAway();
    if (/discarded/.test(why)) return discarded();
    if (/paused|Begin first/.test(why)) return reload();
    return null;
  }
  function beat(on) {
    clearInterval(stampT);
    if (!on) return;
    // a bare stamp every 30 s while the clock runs, so an idle student is never read as a closed page
    stampT = setInterval(() => { if (queue && run && run.timer && !run.timer.paused) queue.push('state', '_stamp', {}); }, 30000);
  }
  addEventListener('pagehide', () => {
    if (!queue || !run) return;
    try { fetch(`/api${path('/state')}`, { method: 'POST', keepalive: true, headers: { 'content-type': 'application/json', 'X-Learner': UI.learner() }, body: JSON.stringify(stampsNow()) }); } catch (_) {}
  });

  /* ---------------- screens */
  function frame(o = {}) {
    destroyRun();
    runHost.hidden = true;
    view.hidden = false;
    const exit = o.exit === null ? null : h('button', { type: 'button', class: 'tw-exit', 'aria-label': o.exitLabel || 'Back to Tests', title: o.exitLabel || 'Back to Tests',
      onclick: o.exit || (() => { location.href = '/tests/'; }) }, icon('x', 20), h('span', { class: 'tw-exit-l', text: o.exitLabel || 'Back to Tests' }));
    const top = h('header', { class: 'tw-top' }, exit, h('span', { class: 'tw-title', text: o.title || '' }));
    const body = h('div', { class: 'tw-body' + (o.wide ? ' wide' : '') });
    view.replaceChildren(top, body);
    if (o.hash !== undefined) try { history.replaceState(null, '', o.hash ? `#${o.hash}` : location.pathname + location.search); } catch (_) {}
    window.scrollTo(0, 0);
    return body;
  }
  function loading(text) {
    const b = frame({ title: text || '', exit: null });
    const box = h('div', { class: 'tw-card', 'aria-busy': 'true', 'aria-label': text || 'Loading the test' });
    if (UI.skel) { UI.skel(box, 'lines:3'); UI.skel(box, { w: '100%', h: 44, r: 999 }); }
    b.append(box);
    return b;
  }
  function problem(text, extra = []) {
    const b = frame({ title: '', hash: '' });
    b.append(h('div', { class: 'tw-card', role: 'alert' }, h('p', { class: 'tw-lead', text }),
      h('div', { class: 'tw-acts' }, extra, h('a', { class: extra.length ? 'btn' : 'pill', href: '/tests/', text: 'Back to Tests' }))));
  }
  const discarded = () => problem('This test was discarded.');
  function finishedAway() {
    if (S && S.kind === 'diagnostic') location.replace(`/diagnostic/signup.html?s=${encodeURIComponent(sid)}`);
    else location.replace(`/results/report/?id=${encodeURIComponent(sid)}`);
  }
  function reload() { destroyRun(); boot(); }
  function destroyRun() {
    beat(false);
    if (run) { try { run.destroy(); } catch (_) {} run = null; }
    runHost.replaceChildren();
  }

  /* ---------------- boot */
  async function boot() {
    loading();
    try { S = await api(path(), { quiet: true }); }
    catch (e) {
      if (e.status === 404) return problem('This test doesn’t exist.');
      if (e.status === 403) return problem('This test belongs to another device’s code. Open it there, or switch codes in Me.', [h('a', { class: 'pill', href: '/me/', text: 'Switch codes in Me' })]);
      return problem('Can’t reach the server. Nothing is lost.', [h('button', { type: 'button', class: 'pill', text: 'Retry', onclick: () => boot() })]);
    }
    document.title = `${title()} · SAT Freshman`;
    if (S.abandoned) return discarded();
    if (S.finished) return finishedAway();
    if (two() && (S.module || 1) > 1 && !S.begun && !S.paused) return between();
    if (!S.begun || S.paused) return lobby();
    if (S.seconds !== null && S.seconds !== undefined && S.seconds <= 0) return lobby('expired');
    if (!ss.get(LIVE)) return lobby('left');
    start();
  }

  /* ---------------- the lobby (4.2, X1, X2) */
  function fact(text, ic) { return h('li', {}, icon(ic || 'dot', 18), h('span', { text })); }
  function lobby(how) {
    const paused = !!S.paused, fresh = !S.begun && !paused;
    const b = frame({ title: S.section, hash: 'lobby' });
    const card = h('section', { class: 'tw-card lobby', id: 'lobby', 'aria-labelledby': 'lobbyH' });
    const n = S.question_count || 0;
    const answered = qidsAnswered();
    card.append(h('p', { class: 'k', text: paused ? 'Paused' : `${subjectLabel(S.subject)}${S.number ? ` · #${S.number}` : ''}` }),
      h('h1', { class: 'h1', id: 'lobbyH', text: paused || how ? title() : S.kind_label }));
    const facts = h('ul', { class: 'tw-facts' });
    if (fresh) {
      if (two()) {
        facts.append(fact(`${S.modules.length} modules · ${S.modules[0].questions} questions each`, 'tests'));
        facts.append(fact(S.why === 'fixed route' ? 'Module 2 is fixed, whatever module 1 gives' : 'Module 2 is chosen by how module 1 goes', 'arrow'));
        facts.append(fact('Once you move on, you can’t go back to a module', 'check'));
      } else facts.append(fact(`${plural(n, 'question')}`, 'tests'));
      const shared = S.new_to_you !== undefined && S.new_to_you < n;
      facts.append(fact(shared ? `${S.new_to_you} of its ${n} questions are new to you` : 'Every question is new to you', 'plus'));
      const hd = S.holds;
      if (hd && hd.domains) {
        const parts = Object.entries(hd.domains).filter(([, v]) => v).map(([k, v]) => `${k} ${v}`);
        if (hd.grid_ins) parts.push(plural(hd.grid_ins, 'grid-in'));
        facts.append(fact(`What it holds: ${parts.join(' · ')}`, 'text'));
        const nt = hd.never && hd.never === hd.new_types ? [`${plural(hd.never, 'question type')} you’ve never met`]
          : [hd.new_types ? `${plural(hd.new_types, 'question type')} you haven’t met under the clock` : null, hd.never ? `${hd.never} you’ve never met at all` : null].filter(Boolean);
        if (nt.length) facts.append(fact(nt.join(' · '), 'search'));
      }
      if (/trainer/i.test(S.kind_label)) facts.append(fact(`The line: ${Math.ceil(0.6 * n)} of ${n} right routes you up`, 'trophy'));
    } else {
      const m = S.module || 1;
      const where = two() ? `Module ${m} of ${S.modules.length} · ` : '';
      facts.append(fact(`${where}${answered} of ${n} answered${marked() ? ` · ${marked()} marked` : ''}`, 'tests'));
      const left = S.seconds;
      if (how === 'expired') facts.append(fact(`Time ran out while you were away. Your ${plural(answered, 'answer')} ${answered === 1 ? 'is' : 'are'} saved.`, 'clock'));
      else if (how === 'left') facts.append(fact(left === null ? 'You left without Save and exit. The clock counts up from where it was.' : `You left without Save and exit, so the clock kept running: ${mmss(left)} left.`, 'clock'));
      else facts.append(fact(left === null ? 'Untimed. The clock is stopped until you resume.' : `${mmss(left)} left. The clock is stopped until you resume.`, 'clock'));
      if (!training() && S.ranked === false && S.why) facts.append(fact(`This sitting keeps its score but won’t rank (${S.why}).`, 'help'));
    }
    card.append(facts);

    // the settings rows, each with Change until Begin (POST /cfg)
    if (fresh) {
      const rows = h('div', { class: 'tw-set' });
      const row = (k, v, change, help, id) => {
        const r = h('div', { class: 'tw-row', id: id || null }, h('span', { class: 'k', text: k }), h('span', { class: 'v', text: v }),
          change ? h('button', { type: 'button', class: 'quiet', text: 'Change', 'aria-label': `Change ${k.toLowerCase()}`, onclick: change }) : h('span'));
        if (help) r.append(h('p', { class: 'help', text: help }));
        rows.append(r);
      };
      row('Conditions', rankLine(), S.contest ? null : () => changeConditions(),
        'Pausing, extended time, a fixed route, a break between modules or more than 2 minutes away keeps your score but drops the rank. Losing Wi-Fi doesn’t.', 'rowCond');
      row('Timing', timingText(S.timing), S.contest ? null : () => changeTiming(), null, 'rowTiming');
      const scientific = UI.DESMOS_KEY === '';
      const calc = !S.calculator ? 'No calculator on this test'
        : scientific ? 'Calculator: scientific · the graphing calculator is unavailable' : 'Calculator and reference sheet on every question';
      row('Tools', [calc, S.predict !== false ? 'asks which you think you missed' : null].filter(Boolean).join(' · '), S.contest ? null : () => changeTools());
      if (training()) {
        const on = TRAINING_AIDS.filter(([k]) => (k === 'type_notes' ? S.type_notes !== false : !!S[k])).map(([, l]) => l);
        let txt = on.length ? on.join(' · ') : 'None on';
        if (S.pace && S.pace.budget_s) txt += S.pace.source === 'you' ? ` · paced to your speed (${UI.num ? UI.num(S.pace.n_answers) : S.pace.n_answers} timed answers)` : ' · SAT tier pace (65 / 95 / 126 s)';
        row('Training aids', txt, () => changeAids());
      }
      card.append(rows);
    }

    // the buttons
    const acts = h('div', { class: 'tw-acts' });
    const fsOk = document.fullscreenEnabled && S.fullscreen !== false;
    const go = (fs, label, primary) => h('button', { type: 'button', class: primary ? 'pill' : 'quiet', text: label, id: primary ? 'begin' : 'beginPlain',
      onclick: e => begin(fs, e.currentTarget, how === 'expired') });
    if (how === 'expired') acts.append(go(false, 'Continue', true));
    else if (how === 'left') acts.append(go(fsOk, 'Continue', true));
    else if (paused) acts.append(go(fsOk, 'Resume', true));
    else if (fsOk) acts.append(go(true, 'Enter fullscreen and begin', true), go(false, 'Begin without fullscreen', false));
    else acts.append(go(false, 'Begin', true));
    card.append(acts);
    const err = h('p', { class: 'error', id: 'lobbyErr', hidden: true, role: 'alert' });
    card.append(err);
    const links = h('p', { class: 'tw-links' },
      h('button', { type: 'button', class: 'quiet', text: 'Directions', onclick: () => UI.directions && UI.directions({}) }),
      h('button', { type: 'button', class: 'quiet', text: 'Keyboard shortcuts', onclick: () => keysSheet() }));
    if (paused) {
      links.append(h('button', { type: 'button', class: 'quiet', text: `Hand in module ${S.module || 1}`, onclick: e => begin(false, e.currentTarget, false, true) }),
        h('button', { type: 'button', class: 'quiet', text: 'Discard this test', onclick: () => discard() }));
    } else if (fresh && !S.contest && S.kind !== 'diagnostic') {
      links.append(h('button', { type: 'button', class: 'quiet', text: 'Start over with other modules', onclick: () => startOver() }));
    }
    card.append(links);
    b.append(card);
    const first = card.querySelector('#begin');
    if (first) setTimeout(() => first.focus({ preventScroll: true }), 0);
    if (wantReview && !fresh && how !== 'expired') { wantReview = false; begin(false, first, false, true); }
  }

  async function cfg(body) {
    const r = await api(path('/cfg'), { method: 'POST', body });
    S = r;
    lobby();
    return r;
  }
  function sheetWith(titleText, fill, save) {
    if (!UI.sheet) return;
    let get = null;
    UI.sheet({ title: titleText, size: 'm', body: b => { get = fill(b); },
      actions: [{ label: 'Cancel', quiet: true }, { label: 'Save', primary: true, onClick: async sh => {
        try { sh.busy(true); await save(get()); } catch (e) { sh.busy(false); toast(`Not saved: ${e.message || 'try again'}`); return false; }
        return undefined;
      } }] });
  }
  function changeConditions() {
    sheetWith('Conditions', b => {
      let v = S.conditions;
      const help = h('p', { class: 'help' });
      const say = () => { help.textContent = v === 'training' ? 'Pace guide, nudges and the rest. Keeps its score, never ranks.' : 'Exactly the SAT: no aids. Ranks among first sittings. A pause keeps your score but drops the rank.'; };
      UI.seg(b, [{ value: 'test_day', label: 'Test-day' }, { value: 'training', label: 'Training' }], { value: v, label: 'Conditions', onChange: x => { v = x; say(); } });
      say();
      b.append(help);
      return () => v;
    }, v => cfg(v === 'test_day' && S.timing === 'x0.85' ? { conditions: v, timing: 'official' } : { conditions: v }));
  }
  function changeTiming() {
    sheetWith('Timing', b => {
      let v = S.timing, minutes = S.kind === 'custom' && S.duration ? Math.round(S.duration / 60 / (S.factor || 1)) : null;
      const list = h('div', { class: 'tw-radios', role: 'radiogroup', 'aria-label': 'Timing' });
      TIMINGS.forEach(([k, label]) => {
        const off = k === 'x0.85' && !training();
        const id = `tm-${k.replace('.', '')}`;
        const inp = h('input', { type: 'radio', name: 'tm', id, value: k, checked: v === k ? true : null, disabled: off ? true : null });
        inp.addEventListener('change', () => { v = k; });
        list.append(h('label', { class: 'tw-radio' + (off ? ' off' : ''), for: id }, inp,
          h('span', {}, h('b', { text: label }), h('span', { class: 'meta', text: off ? 'Training only' : timingText(k, ' a module') }))));
      });
      b.append(list);
      let mins = null;
      if (S.kind === 'custom') {
        mins = h('input', { type: 'number', class: 'field sm', min: 1, max: 180, value: minutes || '', 'aria-label': 'My own minutes' });
        b.append(h('label', { class: 'label', text: 'My own minutes (1–180), in place of the timing above' }), mins);
      }
      return () => ({ timing: v, minutes: mins && mins.value ? Math.max(1, Math.min(180, +mins.value)) : null });
    }, x => cfg(x.minutes ? { timing: x.timing, minutes: x.minutes } : { timing: x.timing }));
  }
  function changeTools() {
    sheetWith('Tools', b => {
      const v = { calculator: S.calculator !== false, predict: S.predict !== false, fullscreen: S.fullscreen !== false };
      UI.switch(b, { label: 'Calculator', checked: v.calculator, onChange: x => { v.calculator = x; } });
      b.append(h('p', { class: 'help', text: 'Off gives no-calculator practice, and the tool is hidden.' }));
      UI.switch(b, { label: 'Ask which I think I missed', checked: v.predict, onChange: x => { v.predict = x; } });
      b.append(h('p', { class: 'help', text: 'About 20 seconds after each module; your report compares.' }));
      if (document.fullscreenEnabled) UI.switch(b, { label: 'Fullscreen', checked: v.fullscreen, onChange: x => { v.fullscreen = x; } });
      return () => v;
    }, v => cfg(v));
  }
  function changeAids() {
    sheetWith('Training aids', b => {
      const v = {};
      TRAINING_AIDS.forEach(([k, label, help]) => {
        v[k] = k === 'type_notes' ? S.type_notes !== false : !!S[k];
        UI.switch(b, { label, checked: v[k], onChange: x => { v[k] = x; } });
        b.append(h('p', { class: 'help', text: help }));
      });
      return () => v;
    }, v => cfg(v));
  }
  function keysSheet() {
    const rows = [['A–D or 1–4', 'Choose'], ['Shift+A–D', 'Eliminate or undo'], ['E', 'Eliminate mode'], ['M', 'Mark for review'],
      ['U', 'Next unanswered'], ['Shift+M', 'Next marked'], ['Z', 'Save to Review'], ['← →', 'Back, Next'], ['N', 'Navigator'],
      ['Shift+R', 'Check your work'], ['G', 'Calculator'], ['F', 'Reference'], ['L', 'Highlights & Notes'], ['Shift+L', 'Scratch'],
      ['H', 'Hide or show the clock'], ['K', 'Confidence (Training)'], ['V', 'Cover the choices (Training)'], ['?', 'Shortcuts'], ['Esc', 'Close the top sheet']];
    if (!UI.sheet) return;
    UI.sheet({ title: 'Keyboard shortcuts', size: 'm', body: b => b.append(
      h('table', { class: 'table compact' }, h('tbody', {}, rows.map(([k, d]) => h('tr', {}, h('td', {}, h('kbd', { class: 'kbd', text: k })), h('td', { text: d }))))),
      h('p', { class: 'help', text: 'In a test, A–D only choose: Save is Z and Details isn’t offered.' })) });
  }
  async function discard() {
    const n = qidsAnswered();
    const ok = await UI.confirm({ title: `Discard ${title()}?`, text: `Its ${plural(n, 'answer')} won’t count anywhere. This can’t be undone.`, confirm: 'Discard', cancel: 'Keep it', destructive: true });
    if (!ok) return;
    try { await api(path('/discard'), { method: 'POST' }); ss.set(LIVE, ''); location.href = '/tests/'; }
    catch (e) { toast(`Couldn’t discard: ${e.message}`); }
  }
  async function startOver() {
    const ok = await UI.confirm({ title: 'Start over with other modules?', text: 'This unbegun test is discarded and the start sheet opens.', confirm: 'Start over', cancel: 'Keep it' });
    if (!ok) return;
    try { await api(path('/discard'), { method: 'POST' }); } catch (_) {}
    location.href = `/tests/?start=${S.kind === 'module' ? 'modules' : S.kind === 'custom' ? 'custom' : 'section'}`;
  }

  /* ---------------- Begin (and Resume, Continue) */
  async function begin(fs, btn, expired, toReview) {
    if (fs) { try { document.documentElement.requestFullscreen().catch(() => {}); } catch (_) {} }
    const err = $('#lobbyErr');
    if (err) err.hidden = true;
    if (btn) { btn.setAttribute('aria-busy', 'true'); btn.disabled = true; }
    makeQueue();
    const firstBegin = !S.begun && !S.paused && (S.module || 1) === 1;
    try {
      if (expired) { S = await api(path()); return timeUp(); }
      S = await api(path('/begin'), { method: 'POST', body: stampsNow() });
    } catch (e) {
      if (btn) { btn.removeAttribute('aria-busy'); btn.disabled = false; }
      if (e.status === 409 && /finished/.test(e.message)) return finishedAway();
      if (err) { err.textContent = e.offline ? 'Can’t reach the server. Check your connection and try again.' : `Couldn’t begin: ${e.message}`; err.hidden = false; }
      return;
    }
    start({ first: firstBegin, review: toReview });
  }

  /* ---------------- the runner (4.3-4.12) */
  async function start(o = {}) {
    if (wantReview) { wantReview = false; o = Object.assign({}, o, { review: true }); }
    makeQueue();
    ss.set(LIVE, '1');
    if (!S.questions || !S.questions.length) return lobby();
    let prefs = {};
    try { prefs = Object.assign({}, await UI.prefs()); } catch (_) {}
    const qst = S.qstate || {};
    const ans = S.answers || {};
    const cells = [], items = [];
    const budget = i => (S.pace && S.pace.budget_s ? S.pace.budget_s[i] * 1000 : undefined);
    let elapsed = 0;
    S.questions.forEach((q, i) => {
      const st = qst[q.id] || {};
      const pending = queue.pendingFor(q.id);
      const a = pending !== undefined ? pending : ans[q.id];
      const has = a !== null && a !== undefined && a !== '';
      elapsed += st.ms || 0;
      cells.push({ n: i + 1, qid: q.id, status: has ? 'answered' : 'unanswered', flag: !!st.marked, conf: st.conf || null, ms: st.ms || 0,
        budget_ms: budget(i), tier: q.difficulty, topic_name: q.topic_name, note: !!(st.note || (st.marks && st.marks.length)) });
      items.push({ q: Object.assign({}, q, { number: i + 1 }),
        state: { selected: q.type === 'spr' ? undefined : (has ? a : undefined), value: q.type === 'spr' ? (has ? a : '') : undefined,
          struck: st.struck || [], covered: st.covered, own: st.own },
        marks: marksIn(st.marks), note: st.note || '', marked: !!st.marked, conf: st.conf || null, scratch: st.scratch || null });
    });
    const timed = S.seconds !== null && S.seconds !== undefined;
    destroyRun();
    view.hidden = true;
    runHost.hidden = false;
    endAtSent = !!(qst._session && qst._session.end_at);
    awaySent.ms = (qst._session && qst._session.away_ms) || 0;
    awaySent.n = (qst._session && qst._session.away_n) || 0;
    const tr = training();
    try { history.replaceState(null, '', location.pathname + location.search); } catch (_) {}
    // the runner keeps one position per sitting (satf.pos.{sid}); a new module opens at its question 1, not at the last
    // module's last question (module 2 opened on Q22, so Review then Hand in skipped 21 unseen questions)
    const modNow = S.module || 1, modKey = `satf.posmod.${sid}`;
    let posMod = null; try { posMod = Number(localStorage.getItem(modKey)) || null; } catch (_) {}
    try { localStorage.setItem(modKey, String(modNow)); } catch (_) {}
    run = UI.runner(runHost, {
      at: posMod && posMod !== modNow ? 0 : undefined,
      mode: 'exam', sid, title: S.section, short: `M${S.module || 1}`, cells, total: cells.length, items,
      clock: timed ? { secondsLeft: S.seconds } : { elapsed: Math.round(elapsed / 1000) },
      conditions: S.conditions, confidence: tr && S.confidence, pace: tr && S.pace ? Object.assign({ duration_s: S.duration }, S.pace) : null,
      nudges: tr && S.nudges, odds: tr ? S.odds || null : null,
      calc: S.calculator !== false, ref: true, annotate: true, scratch: true, directions: true,
      prefs: Object.assign({}, prefs, { test_pace: prefs.test_pace !== false }), queue, who: S.name || null, source: 'test',
      fullscreen: S.fullscreen !== false, guardLeave: timed, resumed: !o.first && qidsAnswered() > 0,
      finishLabel: lastModule() ? 'Hand in' : `Move on to module ${(S.module || 1) + 1}`,
      workspace: { formNudge: tr && S.nudges, coverTool: tr && S.cover, cover: tr && S.cover,
        onCover: c => { const i = run && run.at; if (i >= 0) putState(S.questions[i].id, { covered: !!c.covered, reveal_ms: c.reveal_ms || undefined, own: c.own || undefined }); } },
      on: {
        select: (i, a, meta) => { const e = elNow(); queue.push('answer', S.questions[i].id, { value: a ?? null, made_left: meta && meta.made_left !== undefined ? meta.made_left : null, _el: Number.isFinite(e) ? Math.round(e) : undefined }); },
        time: (i, ms) => { if (ms > 0 && S.questions[i]) putState(S.questions[i].id, { ms: Math.min(600000, Math.round(ms)) }); },
        state: (i, patch) => {
          const p = Object.assign({}, patch);
          if (p.marks) p.marks = marksOut(p.marks);
          if (p.scratch !== undefined) p.scratch = p.scratch || {};
          if (S.questions[i]) putState(S.questions[i].id, p);
        },
        mark: (i, on) => {
          putState(S.questions[i].id, { marked: !!on });
          // Review's flags (R5, S10): the same mark in the flags table, so Review lists it
          api(path('/flag'), { method: 'POST', quiet: true, body: { question_id: S.questions[i].id, on: !!on } }).catch(() => {});
        },
        note: (i, text) => { putState(S.questions[i].id, { note: String(text || '').slice(0, 500) }); },
        save: (i, on) => api('/saved', { method: 'POST', body: { session: sid, question_id: S.questions[i].id, on: !!on } }),
        away: a => {
          const dm = Math.max(0, Math.round((a.away_ms || 0) - awaySent.ms)), dn = Math.max(0, (a.away_n || 0) - awaySent.n);
          awaySent.ms = Math.max(awaySent.ms, a.away_ms || 0); awaySent.n = Math.max(awaySent.n, a.away_n || 0);
          if (dm || dn) putState('_session', { away_ms: Math.min(3600000, dm), away_n: Math.min(10, dn) });
        },
        nudge: n => putState('_session', { nudge: { kind: n.kind === 'sink' || n.kind === 'grid' ? n.kind : 'last_minute', qid: n.qid || undefined, took: n.took ?? undefined } }),
        view: (name, i) => {
          if (endAtSent) return;
          if (name === 'review' || (name === 'q' && i === cells.length - 1)) {
            endAtSent = true;
            const e = elNow();
            if (Number.isFinite(e)) putState('_session', { end_at: Math.round(e) });
          }
        },
        report: (i, q) => UI.report && UI.report({ kind: 'question', source: 'test', session: sid, question_id: q.id, live: true,
          label: `Module ${S.module || 1} · Q${i + 1}` }),
        pref: (key, v) => {
          const body = key === 'text' ? { text: v } : /^test_/.test(key) ? { [key]: v } : null;
          if (body && UI.prefs && UI.prefs.set) UI.prefs.set(body).catch(() => toast('Setting not saved.'));
        },
        remind: () => remind(),
        exit: how => saveAndExit(how),
        finish: () => handIn(),
        timeUp: () => timeUp(),
        discard: () => discardLive(),
      },
    });
    openGate();
    beat(timed);
    if (o.first && run.directions && !(UI.directions && UI.directions.skipped && UI.directions.skipped())) setTimeout(() => run && run.directions(true), 60);
    if (o.review) setTimeout(() => run && run.review(), 0);
  }

  function remind() {
    if (!UI.ics) return;
    const left = run && run.timer && run.timer.timed ? ` · ${mmss(run.timer.left)} left` : '';
    const at = (UI.prefs && UI.prefs.now && (UI.prefs.now() || {}).study_time) || '19:00';
    const d = new Date();
    const [hh, mm] = at.split(':').map(Number);
    d.setHours(hh || 19, mm || 0, 0, 0);
    if (d < new Date()) d.setDate(d.getDate() + 1);
    UI.ics({ title: `Finish ${title()}${left}`, start: d, minutes: 30, url: `${location.origin}/test/?s=${encodeURIComponent(sid)}#lobby`, alarm: 0 });
    toast('Reminder downloaded. Open it to add it to your calendar.');
  }
  async function saveAndExit() {
    handing = true;
    const b = loading('Saving…');
    b.querySelector('.tw-card').append(h('p', { class: 'meta', text: 'Saving your answers, then stopping the clock.' }));
    try {
      await Promise.race([queue.wait(), new Promise(r => setTimeout(r, 8000))]);
      await api(path('/pause'), { method: 'POST', body: stampsNow() });
      ss.set(LIVE, '');
      location.href = '/tests/#live';
    } catch (e) {
      handing = false;
      problem(e.offline ? 'You’re offline. Your answers are kept on this device. Stay on this page until you reconnect.' : `Couldn’t pause: ${e.message}`,
        [h('button', { type: 'button', class: 'pill', text: 'Back to the test', onclick: () => reload() })]);
    }
  }
  async function discardLive() {
    try { await api(path('/discard'), { method: 'POST' }); ss.set(LIVE, ''); destroyRun(); location.href = '/tests/'; }
    catch (e) { toast(`Couldn’t discard: ${e.message}`); }
  }

  /* ---------------- handing in (4.7, X11, X12) */
  function snapshotM1() {
    if (!run || !S.questions) return;
    cellsM1 = run.cells.map(c => ({ n: c.n, status: c.status, ms: c.ms || 0 }));
    paceM1 = S.pace && S.pace.budget_s ? S.pace.budget_s.slice() : null;
    // a two-word skill label; a joining word takes the third ("Area and volume")
    // the site's short skill names ("Ratios & rates"), found from the full name's slug; the first words of the full name read
    // "Ratios Rates" and "Systems of Linear"
    // (the part before a colon; else the one slug that starts with its first two words: "Ratios, Rates, Proportional ...")
    const shortOf = q => {
      if (!UI.TOPIC) return null;
      const slug = String(q.topic_name || '').split(':')[0].toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
      if (UI.TOPIC[slug]) return UI.TOPIC[slug].short;
      const pre = slug.split('_').slice(0, 2).join('_') + '_', hits = Object.keys(UI.TOPIC).filter(k => k.startsWith(pre));
      return hits.length === 1 ? UI.TOPIC[hits[0]].short : null;
    };
    labelsM1 = S.questions.map(q => { if (shortOf(q)) return shortOf(q); const w = String(q.topic_name || '').replace(/[:,]/g, '').split(/\s+/); return w.slice(0, /^(and|of|in|the|to)$/i.test(w[1] || '') ? 3 : 2).join(' '); });
    qidsM1 = S.questions.map(q => q.id);
  }
  async function flushOrWait(body) {
    if (!queue || !queue.size) return;
    const line = h('p', { class: 'meta', 'aria-live': 'polite' });
    body.append(line);
    const paint = info => { line.textContent = info.state === 'offline' ? `Handing in when you reconnect · ${plural(info.n || info.size, 'answer')} waiting` : info.size ? `${plural(info.n || info.size, 'answer')} still saving…` : ''; };
    const off = queue.onStatus(paint);
    await queue.wait();
    off();
  }
  async function handIn(how) {
    if (handing) return;
    handing = true;
    const final = lastModule();
    const timedOut = how === 'timeup';
    let predicted = null;
    if (final && !timedOut && S.predict !== false && run && run.cells.some(c => c.status === 'answered') && UI.predictSheet) {
      snapshotM1();
      predicted = await new Promise(res => {
        const sh = UI.predictSheet(cellsM1, { labels: i => labelsM1[i], onDone: list => res(list || []) });
        if (!sh) res([]); else sh.closed.then(() => res([]));
      });
    }
    snapshotM1();
    const qids = (S.questions || []).map(q => q.id);
    const body = loading(timedOut ? 'Time’s up' : final ? 'Marking your test…' : 'Handing in module 1…');
    body.querySelector('.tw-card').prepend(h('p', { class: 'tw-lead', text: timedOut ? 'Time’s up. Handing in…' : final ? 'Marking your test…' : `Handing in module ${S.module || 1}…` }));
    await flushOrWait(body.querySelector('.tw-card'));
    let res;
    try { res = await api(path('/finish'), { method: 'POST', body: stampsNow() }); }
    catch (e) {
      handing = false;
      if (e.status === 409 && /discarded/.test(e.message)) return discarded();
      if (e.status === 409 && /paused|Begin/.test(e.message)) return reload();
      return problem(e.offline ? 'You’re offline. Your answers are safe on this device; hand in when you’re back.' : `Couldn’t hand in: ${e.message}`,
        [h('button', { type: 'button', class: 'pill', text: 'Try again', onclick: () => { handing = false; handIn(how); } })]);
    }
    ss.set(LIVE, '');
    try { if (document.fullscreenElement && final) await document.exitFullscreen(); } catch (_) {}
    if (predicted && predicted.length) predicted.forEach(i => api(path('/state'), { method: 'POST', quiet: true, body: { question_id: qids[i], predict: 'miss' } }).catch(() => {}));
    handing = false;
    if (res.next_module) {
      lastSummary = res.summary || null;
      lastRoute = res.route ? res : null;
      try { S = await api(path()); } catch (_) {}
      if (timedOut) return timeUpScreen(false);
      return between();
    }
    if (timedOut) return timeUpScreen(true, res.done);
    return done(res.done || {});
  }
  function timeUp() {
    if (handing) return;
    if (run) { try { run.done(); } catch (_) {} }
    const pending = queue ? queue.answers : 0;
    handIn('timeup');
    if (pending) toast(`${plural(pending, 'answer')} you gave in time ${pending === 1 ? 'is' : 'are'} being sent.`);
  }
  function timeUpScreen(final, d) {
    const b = frame({ title: S.section, hash: 'timeup' });
    const s = lastSummary || {};
    const of = (cellsM1 || []).length;
    const answered = cellsM1 ? cellsM1.filter(c => c.status === 'answered').length : s.answered;
    const m = final ? (S.module || 1) : 1;
    const card = h('section', { class: 'tw-card', id: 'timeup', 'aria-labelledby': 'tuH' },
      h('h1', { class: 'h1', id: 'tuH', text: 'Time’s up' }),
      h('p', { class: 'tw-lead', text: `Module ${m} was handed in with ${answered ?? '—'} of ${of || s.answered + s.unanswered || '—'} answered. Every answer you gave is saved.` }));
    const next = h('button', { type: 'button', class: 'pill', text: final ? 'Continue' : 'Continue to module 2', onclick: () => (final ? done(d || {}) : between()) });
    card.append(h('div', { class: 'tw-acts' }, next));
    b.append(card);
    setTimeout(() => next.focus(), 0);
  }

  /* ---------------- between modules (4.6, X11, X14) */
  function between() {
    const tr = training();
    const m = S.module || 2;
    const leave = async () => {
      if (!tr) {
        const ok = await UI.confirm({ title: 'Leave now?', text: `Module ${m} would start when you’re back, and this sitting won’t rank.`, confirm: 'Leave', cancel: 'Stay' });
        if (!ok) return;
      }
      location.href = '/tests/#live';
    };
    const b = frame({ title: S.section, hash: 'between', exit: leave, exitLabel: 'Save and exit' });
    const s = lastSummary || {};
    const n2 = (S.modules[m - 1] || {}).questions || S.question_count || 22;
    const tools = S.calculator === false ? 'no calculator' : 'calculator and reference sheet on every question';
    let route = null;
    if (lastRoute && lastRoute.route) {
      const g = lastRoute.gate || {};
      route = `${lastRoute.route === 'upper' ? 'You earned the harder module 2.' : 'You got the easier module 2.'}${g.margin !== undefined ? ' ' + gateLine(g) : ''}`;
    }
    // Training: module 1's pace, your cumulative time against the plan's (X3)
    let extra = null;
    if (tr && paceM1 && cellsM1 && UI.lineChart) {
      let plan = 0, you = 0, worst = 0, at = -1;
      const P = [], Y = [];
      cellsM1.forEach((c, i) => {
        plan += paceM1[i] || 0; you += (c.ms || 0) / 1000;
        P.push({ x: i + 1, y: Math.round(plan) }); Y.push({ x: i + 1, y: Math.round(you) });
        if (you - plan > worst) { worst = you - plan; at = i; }
      });
      extra = h('div', { class: 'tw-pace' }, h('p', { class: 'k', text: 'Module 1 pace' }));
      UI.lineChart(extra, [{ key: 'plan', label: 'Pace guide', points: P, dashed: true }, { key: 'you', label: 'You', points: Y, you: true }],
        { height: 64, x: 'index', format: v => mmss(v), xFormat: x => `Q${x}`, label: 'Module 1: your time against the pace guide' });
      extra.append(h('p', { class: 'meta', text: at >= 0 && worst >= 30 ? `At Q${at + 1} you were ${mmss(worst)} behind` : 'You kept to the pace guide' }));
    }
    const api2 = UI.between(b, {
      conditions: S.conditions, seconds: 60,
      stats: s.answered !== undefined ? { answered: s.answered, of: s.answered + s.unanswered, marked: s.marked, used_s: Math.round((s.ms || 0) / 1000), away_s: Math.round((s.away_ms || 0) / 1000) } : {},
      next: `Module ${m} · ${n2} questions · ${S.seconds !== null && S.seconds !== undefined ? mmss(S.seconds) : 'untimed'} · ${tools}`,
      route, cells: cellsM1 || null, labels: i => (labelsM1 || [])[i] || '', predict: S.predict !== false && !!cellsM1, extra,
      onPredict: list => {
        const ids = qidsM1 || [];
        (list || []).forEach(i => api(path('/state'), { method: 'POST', quiet: true, body: { question_id: ids[i], predict: 'miss' } }).catch(() => {}));
      },
      onBegin: async ({ between_ms }) => {
        makeQueue();
        try { S = await api(path('/begin'), { method: 'POST', body: Object.assign(stampsNow(), { between_ms }) }); }
        catch (e) { api2.busy(false); toast(e.offline ? 'Can’t reach the server. Try again.' : `Couldn’t begin: ${e.message}`); return; }
        cellsM1 = null;
        await start({ first: false });
        if (run) run.say(`Module ${m} started`);
      },
    });
  }
  function gateLine(g) {
    if (!g || g.margin === undefined || g.margin === null) return '';
    if (g.margin >= 0) return g.margin ? `Routed up with ${g.margin} to spare` : 'Routed up, with none to spare';
    const cheap = (g.cheap_misses || []).length;
    return `${-g.margin} short of the harder module 2${cheap ? ` · ${cheap} of your misses were easy or medium` : ''}`;
  }

  /* ---------------- the hand-in moment (X12, X13, X10) */
  function done(d) {
    const b = frame({ title: S.section, hash: 'done', wide: true });
    const diag = S.kind === 'diagnostic';
    const card = h('section', { class: 'tw-card done', id: 'done', 'aria-labelledby': 'doneH' });
    const rankChip = d.ranked === undefined || d.ranked === null || d.scored === false ? null
      : h('span', { class: 'tw-chip' + (d.ranked ? ' ranked' : ''), text: d.ranked ? 'Ranked' : `Unranked${d.unranked_why ? ' · ' + d.unranked_why : ''}` });
    card.append(h('p', { class: 'tw-kline' }, h('span', { class: 'k', text: `${d.kind_label || S.kind_label}${d.number || S.number ? ` #${d.number || S.number}` : ''} · handed in` }), rankChip));
    const est = d.estimate;
    if (est && !diag) {
      const day = s => String(s || '').replace(/\d{4}-\d{2}-\d{2}/g, x => (UI.date ? UI.date(x, 'short') : x));
      card.append(h('h1', { class: 'h1', id: 'doneH', text: day(d.headline) || 'Your estimate' }));
      const sc = h('div', { class: 'tw-scale' });
      card.append(sc);
      if (UI.scale) UI.scale(sc, { band: { low: est.low, high: est.high }, previous: est.previous || undefined, target: est.target || undefined,
        animate: !reduced(), label: `${est.low}–${est.high}`, min: 200, max: 800 });
      else sc.append(h('p', { class: 'num tw-band', text: `${est.low}–${est.high}` }));
    } else if (!diag) {
      card.append(h('h1', { class: 'h1', id: 'doneH', text: d.right !== undefined && d.right !== null ? `${d.right} of ${d.asked} right` : 'Handed in' }),
        h('p', { class: 'meta', text: d.not_scored ? `Practice, no estimate · ${d.not_scored}` : 'Practice, no estimate' }));
    } else {
      card.append(h('h1', { class: 'h1', id: 'doneH', text: 'The diagnostic is in' }),
        h('p', { class: 'tw-lead', text: 'Your result is one step away.' }));
    }
    if (!diag && (d.route || d.gate)) {
      const line = h('p', { class: 'tw-route' });
      if (d.route) line.append(h('span', { class: 'tw-chip', text: d.route === 'upper' ? 'Harder module 2' : 'Easier module 2' }));
      const g = gateLine(d.gate);
      if (g) line.append(h('span', { text: g }));
      card.append(line);
    }
    if (!diag && d.gate && (/trainer/i.test(d.kind_label || S.kind_label || '') || S.trainer)) card.append(trainerBlock(d.gate));
    if (!diag && d.moments && d.moments.length) {
      card.append(h('ul', { class: 'tw-moments' }, d.moments.slice(0, 2).map(m => h('li', {}, icon(m.id === 'best' || m.id === 'first_upper' ? 'trophy' : 'check', 18), h('span', { text: m.text })))));
    }
    if (d.report_later && d.report_later.length) {
      const box = h('div', { class: 'tw-later' });
      d.report_later.forEach(qid => {
        const m = /^m(\d)q0?(\d+)$/.exec(qid) || [];
        const label = m[1] ? `Module ${m[1]} · Q${m[2]}` : qid;
        box.append(h('p', {}, h('span', { text: `You flagged ${m[2] ? 'Q' + m[2] : qid} to report` }),
          h('button', { type: 'button', class: 'quiet', text: 'Report now', onclick: () => UI.report && UI.report({ kind: 'question', source: 'test', session: sid, question_id: qid, include_answer: true, label }) })));
      });
      card.append(box);
    }
    const acts = h('div', { class: 'tw-acts' });
    const report = diag ? `/diagnostic/signup.html?s=${encodeURIComponent(sid)}` : `/results/report/?id=${encodeURIComponent(sid)}`;
    const p = d.pressure || {};
    if (p.eligible) {
      acts.append(h('button', { type: 'button', class: 'pill', id: 'pressureGo', text: `Pressure check · ${plural(p.n, 'question')} · ~${p.minutes} min`, onclick: e => pressure(e.currentTarget) }));
      acts.append(h('a', { class: 'btn', href: report, text: diag ? 'See your result' : 'See your report' }));
    } else acts.append(h('a', { class: 'pill', href: report, text: diag ? 'See your result' : 'See your report' }));
    const toFix = (d.misses || 0) + (d.blanks || 0);
    if (!diag && toFix) acts.append(h('button', { type: 'button', class: 'quiet', text: `Fix ${toFix} now`, onclick: e => fix(e.currentTarget) }));
    acts.append(S.contest ? h('a', { class: 'quiet', href: '/compete/', text: 'Back to Compete' }) : h('a', { class: 'quiet', href: '/tests/', text: 'Back to Tests' }));
    card.append(acts);
    if (p.eligible) card.append(h('p', { class: 'help', text: `${plural(p.n, 'question')} like ones you missed, left blank, guessed or spent long on. Same kind, same difficulty, new numbers, no clock.` }));
    b.append(card);
    const first = acts.querySelector('.pill');
    if (first) setTimeout(() => first.focus({ preventScroll: true }), 0);
  }
  // X14: the Route-up trainer's hand-in: where the line fell, what cost the route, and the next go
  function trainerBlock(g) {
    const box = h('section', { class: 'tw-trainer', 'aria-label': 'The route line' });
    const qs = S.questions || [];
    if (Array.isArray(g.rights) && qs.length) {
      const rights = new Set(g.rights);
      let k = 0, line = null;
      qs.forEach((q, i) => { if (rights.has(i + 1) && ++k === g.needed) line = i + 1; });
      const strip = h('div', { class: 'tw-strip', role: 'img', 'aria-label': `${g.right} of ${qs.length} right; ${g.needed} routes you up${line ? `, reached at Q${line}` : ''}` });
      qs.forEach((q, i) => strip.append(h('i', { class: (rights.has(i + 1) ? 'on' : '') + (line === i + 1 ? ' line' : '') })));
      box.append(strip);
    }
    const cheap = (g.cheap_misses || []).filter(p => qs[p - 1]);
    if (cheap.length) {
      const tier = p => ({ easy: 'easy', medium: 'medium', hard: 'hard' })[qs[p - 1].difficulty] || '';
      const list = h('ul', { class: 'tw-cost' });
      cheap.forEach(p => list.append(h('li', {}, h('span', { text: `Q${p}${tier(p) ? ` (${tier(p)})` : ''}` }),
        h('button', { type: 'button', class: 'quiet', text: 'Try a twin', onclick: e => twinOf([qs[p - 1].id], 1, e.currentTarget, 'twin') }))));
      box.append(h('p', { class: 'k', text: 'These cost the route' }), list);
    }
    const acts = h('div', { class: 'tw-acts' });
    if (cheap.length) acts.append(h('button', { type: 'button', class: 'btn', text: 'Fix what cost the route', onclick: e => twinOf(cheap.map(p => qs[p - 1].id), 2, e.currentTarget, 'gate') }));
    acts.append(h('button', { type: 'button', class: 'quiet', text: 'Next module 1', onclick: async e => {
      const b = e.currentTarget;
      b.setAttribute('aria-busy', 'true');
      try { const r = await api('/mock/new', { method: 'POST', body: { kind: 'module', module: 'm1', trainer: 'route', conditions: 'test_day' } }); location.href = `/test/?s=${encodeURIComponent(r.id)}`; }
      catch (x) { b.removeAttribute('aria-busy'); toast(`Couldn’t build it: ${x.message}`); }
    } }));
    box.append(acts);
    return box;
  }
  async function twinOf(only, each, btn, source) {
    btn.setAttribute('aria-busy', 'true');
    try { const r = await api('/drill', { method: 'POST', body: { from_session: sid, only, each, source } }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
    catch (e) { btn.removeAttribute('aria-busy'); toast(`Couldn’t start it: ${e.message}`); }
  }
  async function pressure(btn) {
    btn.setAttribute('aria-busy', 'true');
    try { const r = await api(path('/pressure'), { method: 'POST' }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
    catch (e) { btn.removeAttribute('aria-busy'); toast(e.status === 409 ? 'The pressure check has closed for this sitting.' : `Couldn’t start it: ${e.message}`); }
  }
  async function fix(btn) {
    btn.setAttribute('aria-busy', 'true');
    try { const r = await api('/drill', { method: 'POST', body: { from_session: sid, scope: 'misses', source: 'fix' } }); location.href = `/practice/session/?id=${encodeURIComponent(r.id)}`; }
    catch (e) { btn.removeAttribute('aria-busy'); toast(`Couldn’t start it: ${e.message}`); }
  }

  boot();
})();
