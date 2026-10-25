/* ============================================================================
   SAT Freshman -- Results, /results/ (S6)
   (spec/rebuild-v2.md 3.5 §2; v2-upgrades reports.md SR21-SR24; decisions 3, 4, 7;
   the user's order of 2026-09-28: Sittings before Skills)

   Main column: the estimate as the hero figure heading its chart (.card.hero; one Range and Kinds
   button top right), every sitting (UI.sittingCard, in progress, the seg plus one Sort and filter
   menu, filters in the URL, paging), one Trends card with
   tabs (gap, the last 14 days, why you miss, difficulty and format, domains across sections),
   each led by its number, the mistakes, then every skill as rows (a tap opens UI.skillPanel; its
   primary starts a set on that skill only). Right column (1280px+): one surface of rows, the
   estimate's facts, the totals (four, the rest folded), share. The header carries the one primary:
   Practise the top 3, else Fix all open. Hovering a sitting on the chart shows it in the hero figure;
   the chip beside the estimate is the last sitting's change ("Best sitting yet" once when it is the best).

   Reads /api/stats, /api/history, /api/map and /api/skill/{topic}, each with ?share=
   for a read-only progress link. While api_practice's older GET /api/history still
   shadows S6's route (no `counts` in the answer), the list is filtered and paged here.
   ========================================================================== */
(() => {
  'use strict';
  const UI = window.UI;
  if (!UI || !UI.rx) return;
  const { h, rx } = UI;
  const doc = document;
  const $ = id => doc.getElementById(id);
  const P = new URLSearchParams(location.search);
  const SHARE = P.get('share') || '';
  const q = SHARE ? `share=${encodeURIComponent(SHARE)}` : '';
  const withQ = (path, extra) => { const s = [extra, q].filter(Boolean).join('&'); return s ? `${path}${path.includes('?') ? '&' : '?'}${s}` : path; };
  UI.shell('results');

  const n = x => UI.num(x);
  const pc = (a, b) => (b ? Math.round(a / b * 100) : 0);
  const sc = (a, b) => `${n(a)} / ${n(b)}`;
  const tm = ms => (ms ? UI.mmss(ms / 1000) : '');
  const plural = (k, one, many) => `${n(k)} ${k === 1 ? one : (many || one + 's')}`;
  const cap = t => (t ? t[0].toUpperCase() + t.slice(1) : '');
  const TIER = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
  const FORMAT = { mcq: 'Multiple choice', spr: 'Grid-in' };
  const TESTS = ['full', 'mock', 'module', 'diagnostic', 'paper', 'custom', 'twin', 'shared'];
  // the page's subject (Both | Math | Reading and Writing under the title, in the URL): Math or R&W shows that
  // section's estimate, chart, trends and skills on 200-800; Both shows the total on 400-1600, every sitting (a full
  // SAT as one row) and both subjects' skills
  let SUBJ = UI.subject ? UI.subject.get({ both: true }) : 'math';
  const both = () => SUBJ === 'both';
  const statSubj = () => (both() ? 'math' : SUBJ);     // /api/stats is per section; Both reads its totals and the total
  const MINS = { math: [70, 35], rw: [64, 32] };     // a section's and a module's minutes
  const domainOrder = s => (s === 'rw' ? (UI.RW_DOMAINS || []).map(d => d.name) : (UI.DOMAINS || []).map(d => d[0]));
  const topicName = (slug, fb) => (UI.topicName ? UI.topicName(slug) : ((UI.TOPIC && UI.TOPIC[slug]) || {}).short) || fb || slug || '';
  const glyph = slug => (UI.glyph && slug && !/^rw_/.test(slug) ? UI.glyph(slug) : null);    // Math's skills have glyphs; R&W's go by name
  const LS = { get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} } };
  const btn = (text, onClick, cls = 'btn sm') => { const b = h('button', { type: 'button', class: cls, text }); b.addEventListener('click', e => onClick(b, e)); return b; };
  const info = (text, about) => UI.why(text, { about });
  // a card's head: its title (no kicker over it); a Trends panel gets one h3 line under the tabs instead. fig: [figure,
  // unit] leads with the number (28, its unit small on the same baseline) in place of a title
  function head(host, o) {
    host.hidden = false;
    const panel = !!host.closest('#trends');
    const title = o.fig ? h(panel ? 'h3' : 'h2', { class: 'rs-fig' }, h('b', { text: o.fig[0] }), h('span', { text: ` ${o.fig[1]}` }))
      : h(panel ? 'h3' : 'h2', { class: panel ? 'h3' : null, text: o.title });
    host.replaceChildren(h('div', { class: panel ? 'rs-ph' : 'card-head' }, title,
      o.meta ? h('span', { class: 'meta', text: o.meta }) : null, o.tip ? info(o.tip, o.about) : null, o.right ? h('div', { class: 'rs-headr' }, o.right) : null));
    return host;
  }
  const readOnly = !!SHARE;
  const drill = (body, b) => (readOnly ? null : rx.drill(body, b));
  // kind: full (the full SAT) | section | module (module 1), of the page's subject (Math under Both)
  async function startTest(kind, b) {
    if (b) b.setAttribute('aria-busy', 'true');
    const body = kind === 'full' ? { kind } : kind === 'module' ? { kind, module: 'm1', subject: statSubj() } : { kind, subject: statSubj() };
    try { const s = await UI.api('/mock/new', { method: 'POST', body }); location.href = `/test/?s=${encodeURIComponent(s.id)}`; }
    catch (_) { if (b) b.removeAttribute('aria-busy'); UI.toast('Couldn’t start the test. Try again.'); }
  }
  // a region that fails keeps its heading and says so, with Retry (the page never goes blank)
  async function region(id, fn) { try { await fn(); } catch (e) { const el = $(id); el.hidden = false; UI.cardError(el, () => region(id, fn), 'Couldn’t load this.'); } }

  let ST = null, HIST = null, MAP = null, RWE = null;    // RWE: R&W's estimate, read only by Both with no total yet
  // the header's one primary: 'gap' (Practise the top 3) or 'fix' (Fix all open); the card that also holds that
  // action shows it only when the header does not
  let PRIMARY = '';
  // a subject's figure is its current score (estimate.range = estimate.current: the one rule Tests, Me and the total
  // use too), never the latest sitting on one page and a mean on another
  const bandOf = E => E && (E.low !== undefined && E.low !== null ? E : E.range || E.combined);
  // Both is about the total (estimate.total: R&W's centre plus Math's, 20 wide on 400-1600)
  // (until /api/stats carries it, the last full SAT's total stands in: the server's range, its sections as the parts)
  const lastFull = () => {
    const f = ((HIST && HIST.sessions) || []).find(s => s.kind === 'full' && s.estimate && s.estimate.low);
    return f && Object.assign({}, f.estimate, { parts: (f.parts || []).map(p => Object.assign({ subject: p.subject, at: p.finished, source: 'measured', id: p.id }, p.estimate)) });
  };
  const total = () => { const t = (ST && ST.total) || lastFull(); return t && t.low !== undefined && t.low !== null ? t : null; };
  const hasBand = () => { if (both()) return !!total(); const E = ST && ST.estimate, b = bandOf(E); return !!(E && E.latest && b && b.low !== undefined); };
  // 2.10: a feed that failed on arrival is fetched again by each region that needs it, so a region
  // shows its own error with Try again instead of an empty state; the regions share one request
  // the skills of Both come from two maps, one a subject, merged by topic
  const getMap = () => (both() ? Promise.all(['math', 'rw'].map(s => UI.api(withQ(`/map?subject=${s}`), { quiet: true })))
    .then(([a, b]) => { const seen = new Set(); return { topics: [...(a.topics || []), ...(b.topics || [])].filter(t => !seen.has(t.topic) && seen.add(t.topic)) }; })
    : UI.api(withQ(`/map?subject=${SUBJ}`), { quiet: true }));
  const FEED = { ST: [() => `/stats?subject=${statSubj()}`, r => { ST = r; }, () => ST], HIST: [() => `/history?limit=200&all=1&subject=${SUBJ}`, r => { HIST = r; }, () => HIST],
    MAP: [null, r => { MAP = r; }, () => MAP] };
  const pend = {};
  const refetch = k => pend[k] || (pend[k] = (k === 'MAP' ? getMap() : UI.api(withQ(FEED[k][0]()), { quiet: true })).then(FEED[k][1]).finally(() => { delete pend[k]; }));
  const needs = (keys, fn) => () => { const miss = keys.filter(k => !FEED[k][2]()); return miss.length ? Promise.all(miss.map(refetch)).then(() => fn()) : fn(); };

  /* ------------------------------------------------------------ load */
  function skeleton() {
    $('estimate').replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'lines:4'));
    $('overview').replaceChildren(UI.skel(null, 'chart:220'));
    $('totals').replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'rows:6'));
    $('sittings').replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'rows:4'));
    $('skills').replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'rows:3'));
  }
  async function load() {
    skeleton();
    if (readOnly && !$('root').querySelector('.rs-strip')) $('head').after(h('div', { class: 'rs-strip', 'data-nofold': '' }, h('b', { text: 'Shared progress · read-only' })));
    ST = HIST = MAP = null;
    const stats = UI.api(withQ(FEED.ST[0]()), { quiet: true });
    const hist = UI.api(withQ(FEED.HIST[0]()), { quiet: true });
    const map = getMap();
    try { ST = await stats; } catch (e) {
      if (e && e.status === 404 && readOnly) { $('main').removeAttribute('aria-busy'); $('root').replaceChildren(h('section', { class: 'card' }, h('h2', { class: 'h2', text: 'That progress link doesn’t work any more.' }), h('p', { class: 'rs-helper', text: 'Ask for a new one.' }))); return; }
      ST = null;
    }
    try { HIST = await hist; } catch (_) { HIST = null; }
    try { MAP = await map; } catch (_) { MAP = null; }
    // Both with no total yet shows each section's current score: R&W's comes from its own stats
    RWE = null;
    if (both() && ST && !total()) { try { RWE = (await UI.api(withQ('/stats?subject=rw'), { quiet: true })).estimate || null; } catch (_) { RWE = null; } }
    $('main').removeAttribute('aria-busy');
    headActions();
    drawShare();
    const tests = () => ((HIST && HIST.sessions) || []).filter(s => TESTS.includes(s.kind));
    // the stats regions: without /api/stats one error card stands in the estimate's place (no
    // repeats), and its Try again draws them all
    const byStats = [['estimate', drawEstimate], ['overview', () => drawOverview(tests)], ['totals', drawTotals], ['trends', drawTrends], ['traps', drawTraps]];
    if (ST) byStats.forEach(([id, fn]) => region(id, fn));
    else {
      const was = byStats.map(([id]) => $(id).hidden);
      byStats.slice(1).forEach(([id]) => { $(id).hidden = true; });
      region('estimate', async () => { await refetch('ST'); headActions(); drawShare(); byStats.forEach(([id, fn], k) => { $(id).hidden = was[k]; region(id, fn); }); });
    }
    region('sittings', needs(['HIST'], drawSittings));
    region('skills', needs(['MAP'], drawSkills));
    // the page's own pill (the header's, or a first test's Full section) is its one orange: Up next's Start goes .btn
    UI.shell({ page: 'results', ownPrimary: !!$('root').querySelector('.pill'), sections: [{ id: hasBand() ? 'overview' : 'estimate', label: 'Estimate' }, { id: 'sittings', label: 'Sittings' }, { id: 'totals', label: 'Totals' },
      { id: 'traps', label: 'Mistakes' }, { id: 'skills', label: 'Skills' }].filter(x => !$(x.id).hidden) });
  }

  /* ------------------------------------------------------------ header */
  function headActions() {
    const box = $('headacts');
    box.replaceChildren();
    const g = ST && ST.gap, open = ST ? (ST.traps || {}).open || 0 : 0;
    // a student with no scored test has the estimate card's "Full section" as the page's primary
    PRIMARY = readOnly || !ST || !hasBand() || both() ? '' : g && g.top3 && g.top3.gain > 0 ? 'gap' : open ? 'fix' : '';
    if (PRIMARY === 'gap') box.append(btn(`Practise the top 3 · ≈ +${n(g.top3.gain)}`, b => drill({ topics: g.top3.topics, count: 12, adaptive: true, source: 'gain' }, b), 'pill'));
    else if (PRIMARY === 'fix') box.append(btn(`Fix all open · ${n(open)}`, b => drill({ mistakes: true, source: 'fix', subject: statSubj() }, b), 'pill'));
  }
  // the right column's last row: Share (a PDF for a parent or a tutor), and CSV, Print and the read-only link behind ⋯
  function drawShare() {
    const box = $('share');
    box.hidden = !!ST && !ST.answered;
    const dots = h('button', { type: 'button', class: 'btn sm icon', 'aria-label': 'More', 'aria-haspopup': 'menu' }, UI.icon('more', 18));
    dots.addEventListener('click', () => UI.menu(dots, [
      { label: 'Download CSV (all sittings)', onClick: csv },
      { label: 'Print', onClick: () => window.print() },
      !readOnly && { label: 'Share a read-only link', onClick: shareSheet },
    ].filter(Boolean), { label: 'More', align: 'end' }));
    box.replaceChildren(btn('Share progress', () => shareChoose(), 'btn sm'), dots);
  }
  // Share: for a parent or a tutor. The student picks a language and a PDF of the progress downloads at once.
  const LANGS = [['uz', 'O’zbekcha', 'Uzbek'], ['en', 'English', 'English'], ['ru', 'Русский', 'Russian']];
  async function downloadReport(lang) {
    const r = await fetch(`/api/results/progress.pdf?lang=${lang}${SHARE ? `&share=${encodeURIComponent(SHARE)}` : ''}`,
      { headers: { 'X-Learner': UI.learner(), 'X-Tz': String(new Date().getTimezoneOffset()) } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const a = h('a', { href: URL.createObjectURL(await r.blob()), download: `progress-${lang}-${new Date().toLocaleDateString('en-CA')}.pdf` });
    document.body.append(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
  }
  function shareChoose() {
    let sh;
    const tiles = LANGS.map(([code, native, english]) => {
      const b = h('button', { type: 'button', class: 'choice-row' }, h('span', { text: native }), h('span', { class: 'meta', text: english }));
      b.addEventListener('click', async () => {
        if (b.getAttribute('aria-busy') === 'true') return;
        b.setAttribute('aria-busy', 'true');
        try { await downloadReport(code); UI.toast(`Downloaded · progress report in ${english}`); sh.close(); }
        catch (_) { b.removeAttribute('aria-busy'); UI.toast('Couldn’t make the PDF. Try again.'); }
      });
      return b;
    });
    const body = h('div', { class: 'rs-est' },
      h('p', { class: 'rs-helper', text: 'Send your progress to a parent or a tutor. Pick a language and a PDF downloads right away.' }),
      h('div', { class: 'rs-langs', role: 'group', 'aria-label': 'Language' }, tiles),
      readOnly ? null : h('div', { class: 'rs-row' }, btn('Or share a read-only link', () => { sh.close(); shareSheet(); }, 'quiet')));
    sh = UI.sheet({ title: 'Share progress', body, size: 's' });
  }
  // R18(a): the progress link is S1's POST /api/share; until it lands, the plan's view link is the same token kind
  async function shareSheet() {
    const body = h('div', { class: 'rs-est', 'aria-busy': 'true' }, UI.skel(null, 'lines:2'));
    const sh = UI.sheet({ title: 'Share my progress', body, size: 's' });
    let token = null, stop = null;
    try { const r = await UI.api('/share', { method: 'POST', body: { on: true }, quiet: true }); token = r.token || r.view_token; stop = () => UI.api('/share', { method: 'POST', body: { on: false } }); }
    catch (_) {
      try {
        const plan = await UI.api('/plan', { quiet: true });
        const pid = plan && (plan.id || (plan.plan && plan.plan.id));
        if (pid) { const r = await UI.api(`/plan/${encodeURIComponent(pid)}/links`, { method: 'POST', body: { view: true }, quiet: true }); token = r.view_token; stop = () => UI.api(`/plan/${encodeURIComponent(pid)}/links`, { method: 'POST', body: { view: false } }); }
      } catch (_) { token = null; }
    }
    body.removeAttribute('aria-busy');
    body.replaceChildren();
    if (!token) {
      body.append(h('p', { class: 'rs-line', text: 'Your progress link comes with your study plan.' }), h('a', { class: 'pill sm', href: '/plan/', text: 'Make a plan' }));
      return;
    }
    const url = `${location.origin}/results/?share=${encodeURIComponent(token)}`;
    const field = h('input', { class: 'field', readonly: '', value: url, 'aria-label': 'Read-only progress link' });
    body.append(h('p', { class: 'rs-helper', text: 'Anyone with this link sees your Results, read-only.' }), field,
      // Copy confirms in place (Copying, Copied); a copy the browser refuses opens kit's "Copy this" sheet
      h('div', { class: 'rs-row' }, btn('Copy', b => UI.copyText(url, { button: b, fail: 'Copy it from the box' }), 'pill sm'),
        btn('Stop sharing', async b => { b.setAttribute('aria-busy', 'true'); try { await stop(); sh.close(); UI.toast('Link turned off'); } catch (_) { b.removeAttribute('aria-busy'); UI.toast('Not saved. Try again.'); } }, 'quiet')));
  }

  /* ------------------------------------------------------------ the estimate (2.2, SR21) */
  // with a band: the facts behind the hero (confidence, the target on its track, best, the exam) as rows of the right
  // column; the band itself heads the chart (drawOverview). Without one, the card that starts a first test
  function drawEstimate() {
    const el = $('estimate');
    el.replaceChildren();
    const E = ST && ST.estimate;
    const pr = (ST && ST.profile) || {};
    const secs = both() && !total() ? [['rw', RWE], ['math', E]].map(([s, x]) => [s, x && x.range && x.range.low ? x.range : null]) : [];
    if (secs.some(([, b]) => b)) {
      // Both, one section measured: no total yet, so each section's own score, and the full SAT that makes one
      $('rsmain').prepend(el);
      el.classList.add('rs-est', 'hero');
      head(el, { title: 'Total' });
      el.append(h('p', { class: 'rs-line', 'data-nofold': '', text: 'Not yet: a total needs a Reading and Writing score and a Math score.' }),
        rx.kv(secs.map(([s, b]) => ({ label: UI.subjectLabel(s), value: b ? `${b.low}–${b.high}` : 'Not measured yet', href: `/results/?subject=${s}` })), { label: 'Section scores' }));
      if (!readOnly) el.append(h('div', { class: 'rs-row' }, btn('Full SAT', b => startTest('full', b), 'pill sm')), h('p', { class: 'meta', text: 'Both sections and a 10-minute break, 2 h 14 min: a total and both scores.' }));
      return;
    }
    if (!hasBand()) {
      // no scored test: the card leads the main column (the chart, sittings and skills stay out of the way)
      $('rsmain').prepend(el);
      el.classList.add('rs-est', 'hero');
      head(el, { title: readOnly ? 'No scored test yet' : 'Sit your first test' });
      if (!readOnly) {
        // a dimmed example of what lands here, then the two ways in: the section (or, for Both, the full SAT) is the
        // most accurate, the module the quick start
        if (UI.empty && UI.bandChart) UI.empty(el, { sample: sampleChart });
        // the minutes live in the line under them, so the two buttons share one row on a phone
        const [sec, mod] = MINS[statSubj()];
        el.append(h('div', { class: 'rs-row' }, both() ? btn('Full SAT', b => startTest('full', b), 'pill sm') : btn('Full section', b => startTest('section', b), 'pill sm'),
          btn('One module', b => startTest('module', b), 'btn sm')),
          h('p', { class: 'meta', text: both() ? `A full SAT (2 h 14 min and a break) gives a total. A Math module (${mod} min) is the quick way in.`
            : `A full section (${sec} min) is the most accurate. A module (${mod} min) is the quick way in.` }),
          h('div', { class: 'rs-row' }, h('a', { class: 'btn sm', href: '/results/report/?id=sample-section', text: 'Open the sample report' }),
            // S3's add-a-score sheet; hidden until it lands, so no button does nothing
            UI.addScore ? btn('Add a score you already have', () => UI.addScore({ onSaved: () => load() }), 'quiet') : null));
      }
      return;
    }
    $('sidecard').prepend(el);
    el.classList.remove('rs-est', 'hero');
    const { low, high } = heroBand();
    const days0 = pr.exam_date ? Math.round((new Date(pr.exam_date) - new Date()) / 864e5) : -1;
    if (both()) {
      // the total's two halves, R&W first (College Board's order), each from its latest sitting or logged score
      head(el, { title: 'Total' });
      const parts = (total().parts || []).filter(p => p.low !== undefined);
      el.append(rx.kv([...parts.map(p => ({ label: UI.subjectLabel(p.subject), value: `${p.low}–${p.high}`,
        sub: p.source && p.source !== 'measured' ? (p.source === 'self' ? 'the score you entered' : `your ${p.source === 'official' ? 'official SAT' : 'Bluebook test'}`) : p.at ? UI.date(p.at) : '' })),
      days0 >= 0 && { label: 'Exam', value: UI.date(pr.exam_date), sub: `in ${plural(days0, 'day')}` }], { label: 'Total facts' }));
      return;
    }
    const conf = E.confidence || {};
    head(el, { title: 'Estimate' });
    // the target on the 200–800 scale: the band in ink, the target a tick, under the target's row
    const pos = v => `${(Math.max(200, Math.min(800, v)) - 200) / 6}%`;
    const track = pr.target ? h('span', { class: 'rs-track', role: 'img', 'aria-label': `Estimate ${low} to ${high}, target ${pr.target}, on a 200 to 800 scale` },
      h('b', { style: `left: ${pos(low)}; width: calc(${pos(high)} - ${pos(low)})` }), h('i', { style: `left: ${pos(pr.target)}` })) : null;
    const bandTxt = x => `${Math.round(x.low)}–${Math.round(x.high)}`;
    const days = pr.exam_date ? Math.round((new Date(pr.exam_date) - new Date()) / 864e5) : -1;
    el.append(rx.kv([
      conf.level && { label: 'Confidence', value: cap(conf.level), why: conf.reason || null },
      pr.target && { label: `Target ${pr.target}`, value: high >= pr.target ? 'Reached' : `${n(pr.target - high)} to go`, after: track },
      E.best && { label: 'Best sitting', value: bandTxt(E.best), sub: UI.date(E.best.at) },
      days >= 0 && { label: 'Exam', value: UI.date(pr.exam_date), sub: `in ${plural(days, 'day')}` },
    ], { label: 'Estimate facts' }));
    if (!readOnly && conf.level && conf.level !== 'high') {
      el.append(btn(`Sit a full section for ${conf.level === 'low' ? 'medium' : 'high'} confidence (${MINS[SUBJ][0]} min)`, bb => startTest('section', bb), 'quiet'));
    }
  }
  // the first-test card's example: three sittings climbing into an estimate (inert, under an "Example" badge)
  function sampleChart() {
    const f = h('div'), ago = d => new Date(Date.now() - d * 864e5).toISOString();
    UI.bandChart(f, [{ id: 'x1', at: ago(40), low: 470, high: 490, kind: 'module' }, { id: 'x2', at: ago(24), low: 510, high: 530 }, { id: 'x3', at: ago(8), low: 550, high: 570 }],
      { height: 150, estimate: { low: 550, high: 570 }, legend: false, grid: 200, label: 'Example: score over time' });
    return f;
  }
  const heroBand = () => { const b = both() ? total() : bandOf(ST.estimate); return { low: Math.round(b.low / 10) * 10, high: Math.round(b.high / 10) * 10 }; };
  // the hero: the estimate at 56-64 with its scale beside it; what it is made of is the ?. The chip beside it is about
  // the last sitting (the chart's orange band), never the estimate: its change on the sitting before, and "Best sitting
  // yet" once when it is the best. The estimate's own facts (best sitting, target) are the right column's. Both: the
  // total, its halves in the right column
  function hero() {
    const E = ST.estimate || {}, { low, high } = heroBand();
    const R0 = E.range || {};
    const from = both() ? 'Your current Reading and Writing and Math scores added: each one’s middle, summed, shown to ±10. A full SAT measures both in one sitting. An estimate from our questions, not a College Board score.'
      : R0.n === 0 ? 'The score you entered. Your first scored sitting replaces it.'
        : `${R0.n > 1 ? `The middle of your latest ${n(R0.n)} scored sittings and logged scores` : 'Your latest scored sitting'}, shown to ±10. An estimate from our questions, not a College Board score.`;
    const name = both() ? 'Total' : `${UI.subjectLabel(SUBJ)} estimate`;
    const band = low === high ? String(low) : `${low}–${high}`;
    const fv = h('span', { text: band });
    const said = h('span', { class: 'meta rs-said', hidden: true });
    const chip = both() ? null : lastChip(E);
    HERO = { fv, band, said, quiet: [chip].filter(Boolean) };
    return h('div', { class: 'rs-hero' },
      h('p', { class: 'k' }, h('span', { 'aria-hidden': 'true', text: name }), info(from, both() ? 'the total' : 'this estimate')),
      h('div', { class: 'rs-figrow' },
        h('h2', { class: 'hero-num' }, h('span', { class: 'sr', text: `${name} ` }), fv, h('small', { text: both() ? '/1600' : '/800' })), chip, said));
  }
  // the last sitting against the one before (estimate.py's trend: the two middles); within 20 points says nothing.
  // "Best sitting yet" leads it once, the first time Results is seen after the last sitting became the best
  function lastChip(E) {
    const L = E.latest, P = E.previous, tr = E.trend || {};
    const moved = tr.direction && tr.direction !== 'steady' && tr.delta;
    const best = !readOnly && L && P && E.best && E.best.id === L.id && L.mid > P.mid && ![L.id, L.at].includes(LS.get('satf.results.best', ''));   // (.at: what the old "New best" stored)
    if (!moved && !best) return null;
    if (best) LS.set('satf.results.best', L.id);
    const what = L && L.outside ? 'Added score' : 'Last sitting', up = tr.delta > 0;
    const change = moved ? `${up ? '+' : '−'}${n(Math.round(Math.abs(tr.delta) / 10) * 10)} vs the one before` : '';   // on tens, like every score
    const b = h('span', { class: 'badge lg' + (up || best ? '' : ' soft') }, moved ? UI.icon(up ? 'caret_up' : 'caret_down', 12) : null,
      best ? ['Best sitting yet', change ? `, ${change}` : ''].join('') : `${what} ${change}`);
    if (best && UI.fx) requestAnimationFrame(() => UI.fx.pop(b));
    return b;
  }
  // a sitting hovered or focused on the chart shows in the hero figure (its band, name and day); off it, the estimate
  let HERO = null;
  function heroShow(p) {
    if (!HERO || !HERO.fv.isConnected) return;
    HERO.fv.textContent = p ? (p.low === p.high ? String(Math.round(p.low)) : `${Math.round(p.low)}–${Math.round(p.high)}`) : HERO.band;
    HERO.said.textContent = p ? [p.label || 'Sitting', UI.date(p.at), p.detail].filter(Boolean).join(' · ') : '';   // the chart's tooltip stays quiet: this is the readout
    HERO.said.hidden = !p;
    HERO.quiet.forEach(x => { x.hidden = !!p; });
  }

  /* ------------------------------------------------------------ score over time (2.3, SR21) */
  // the head first, from /stats: a history that fails to load keeps the hero (UI.cardError keeps .card-head)
  function drawOverview(tests) {
    const el = $('overview');
    el.hidden = false;
    const ctl = h('div');
    el.classList.toggle('hero', hasBand());
    if (hasBand()) el.replaceChildren(h('div', { class: 'card-head rs-hd' }, hero(), h('div', { class: 'rs-headr' }, ctl)));
    else head(el, { title: 'Score over time', right: ctl });
    return needs(['HIST'], () => drawChart(tests(), ctl))();
  }
  function drawChart(tests, ctl) {
    const el = $('overview');
    // oldest first, ties by id as estimate.py breaks them, so the orange newest band is the hero chip's last sitting
    const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
    // Both charts the full SATs' totals on 400-1600; a subject charts its sections on 200-800 (never the two mixed)
    const href = s => (s.kind === 'full' ? `/results/full/?id=${encodeURIComponent(s.id)}` : rx.reportHref(s.id));
    const pts = tests.filter(s => s.estimate && s.estimate.low && (s.kind === 'full') === both()).slice().sort((a, b) => cmp(String(a.finished), String(b.finished)) || cmp(String(a.id), String(b.id))).map(s => ({
      id: s.id, at: s.finished, low: s.estimate.low, high: s.estimate.high, kind: s.kind, label: `${s.kind === 'full' ? 'Full SAT' : UI.KIND.label(s)}${s.seq ? ` #${s.seq}` : ''}`,
      detail: [s.asked ? sc(s.right || 0, s.asked) : null, s.route ? (s.route === 'upper' ? 'harder M2' : 'easier M2') : null].filter(Boolean).join(' · '),
      href: href(s) }));
    el.querySelectorAll(':scope > :not(.card-head)').forEach(x => x.remove());
    ctl.replaceChildren();
    el.hidden = !pts.length && !hasBand();          // no scored test yet: the estimate card is the one card
    if (!pts.length) return;                        // a band with no sitting in the list: the hero alone
    const band = both() ? total() : bandOf(ST && ST.estimate);
    const scale = both() ? { min: 400, max: 1600 } : { target: (ST && ST.profile || {}).target };
    UI.bandChart(el, pts, Object.assign(scale, { estimate: band && band.low ? { low: band.low, high: band.high } : null,
      filters: pts.length > 1, store: 'satf.results.chart', label: both() ? 'Total over time' : 'Score over time', legend: 'fold', ctlHost: ctl, grid: 200,
      onPick: p => { location.href = p.href || rx.reportHref(p.id); }, onFocus: heroShow,
      empty: { text: 'Your first test puts a point here.' } }));
  }

  /* ------------------------------------------------------------ Trends: five analyses, one card, one read at a time (UI.tabs) */
  async function drawTrends() {
    const el = $('trends');
    // Both keeps the one panel that counts both subjects (the last 14 days); the rest are a section's own
    const panels = [['gap', 'Gap', drawGap], ['days', 'Last 14 days', drawDays], ['why', 'Why you miss', drawWhy], ['split', 'Difficulty and format', drawSplit],
      ['domtrend', 'Domains', needs(['HIST'], drawDomains)]].filter(([id, , fn]) => (both() && id !== 'days' ? (($(id).hidden = true), false) : fn));
    await Promise.all(panels.map(async ([id,, fn]) => {      // each panel hides itself when it has nothing to say
      try { await fn(); } catch (_) { const p = $(id); p.hidden = false; UI.cardError(p, drawTrends, 'Couldn’t load this.'); }
    }));
    const live = panels.filter(([id]) => !$(id).hidden);
    el.hidden = !live.length;
    $('trendtabs').replaceChildren();
    if (live.length) UI.tabs($('trendtabs'), live.map(([id, label]) => ({ id, label, panel: $(id) })), { label: 'Trends' });
  }

  /* ------------------------------------------------------------ gap to target (SR22, U4's gains) */
  function drawGap() {
    const el = $('gap');
    el.hidden = true;
    const g = ST && ST.gap;
    if (!g || !g.top3 || !(g.top3.gain > 0)) return;
    head(el, { title: 'Where your next points are', tip: 'The gain is what reaching Strong on a skill would add to a section, from how often it comes up.', about: 'the gain' });
    const rows = (g.skills || []).filter(s => s.gain > 0).slice(0, 5);
    const list = h('div', { class: 'rs-bars' });
    const top = Math.max(...rows.map(s => s.gain), 1);
    rows.forEach(s => list.append(h('div', { class: 'rs-bar', style: `--rp: ${s.gain / top}` }, h('span', {}, glyph(s.topic), ' ', topicName(s.topic)), h('span', { class: 't' }, h('i')),
      h('span', { class: 'rs-row' }, h('b', { class: 'rs-num', text: `≈ +${n(s.gain)}` }), readOnly ? '' : btn('Practise', b => drill({ topics: [s.topic], count: 10, adaptive: true, source: 'skill' }, b), 'quiet')))));
    el.append(list);
    if (!readOnly && PRIMARY !== 'gap') el.append(h('div', { class: 'rs-row rs-more' }, btn(`Practise the top 3 · ≈ +${n(g.top3.gain)}`, b => drill({ topics: g.top3.topics, count: 12, adaptive: true, source: 'gain' }, b))));
  }

  /* ------------------------------------------------------------ totals (2.4, SR22) */
  function drawTotals() {
    const el = $('totals');
    el.replaceChildren();
    const s = ST || {};
    el.hidden = !s.answered;                        // a new student has no totals yet (decision 7: no zeros)
    if (el.hidden) return;
    const t = s.tests || {};
    const testsN = (t.full || 0) + (t.mock || 0) + (t.module || 0) + (t.diagnostic || 0) + (t.custom || 0);
    const tiles = [
      { label: 'Questions', value: s.answered || 0, sub: 'all time' },
      s.answered && { label: 'Accuracy', value: `${Math.round((s.accuracy || 0) * 100)}%`, sub: s.recent_accuracy !== undefined ? `last 14 days ${Math.round(s.recent_accuracy * 100)}%` : 'all time' },
      s.minutes_total && { label: 'Study time', value: UI.dur(s.minutes_total), sub: s.minutes_week ? `this week ${UI.dur(s.minutes_week)}` : 'tests included' },
      testsN && { label: 'Tests', value: testsN, sub: [t.full && plural(t.full, 'full SAT'), t.mock && plural(t.mock, 'section'), t.module && plural(t.module, 'module'), t.diagnostic && plural(t.diagnostic, 'diagnostic'), t.custom && plural(t.custom, 'custom test')].filter(Boolean).join(' · ') },
      s.streak && { label: 'Streak', value: `${n(s.streak)} ${s.streak === 1 ? 'day' : 'days'}`, sub: s.best_streak > s.streak ? `best ${n(s.best_streak)}` : 'your best' },
      s.traps && (s.traps.open || s.traps.closed) && { label: 'Mistakes', value: `${n(s.traps.open || 0)} open`, sub: s.traps.closed ? `${n(s.traps.closed)} fixed` : '', href: readOnly ? null : '/mistakes/' },
      s.types_met && s.types_met.met && { label: 'Question types met', value: `${n(s.types_met.met)} of ${n(s.types_met.total || s.types_met.of || 0)}`, sub: '', href: readOnly ? null : '/me/#atlas' },
      s.week && s.week.recovered_pts && { label: 'Recovered this week', value: rx.pts(s.week.recovered_pts), sub: s.week.closed ? `${plural(s.week.closed, 'mistake')} closed` : '' },
    ].filter(Boolean);
    tiles.forEach(x => { if (x.sub && String(x.value) && String(x.sub).endsWith(` ${x.value}`)) x.sub = ''; });
    // four rows in view; the rest (streak, mistakes, types met, recovered) behind one fold
    const cut = tiles.length > 5 ? 4 : tiles.length;
    el.append(h('div', { class: 'card-head' }, h('h2', { text: 'Totals' })), rx.kv(tiles.slice(0, cut), { label: 'Totals' }));
    if (tiles.length > cut) el.append(h('details', { class: 'fold rs-tmore' }, h('summary', { class: 'fold-s', text: `${n(tiles.length - cut)} more` }), rx.kv(tiles.slice(cut), { label: 'More totals' })));
  }

  /* ------------------------------------------------------------ the last 14 days */
  function drawDays() {
    const el = $('days');
    const days = (ST && ST.days14) || [];
    if (!days.length) { el.hidden = true; return; }
    const q = days.reduce((a, d) => a + (d.questions || 0), 0);
    if (!q && !(ST && ST.answered)) { el.hidden = true; return; }
    head(el, q ? { fig: [n(q), `${q === 1 ? 'question' : 'questions'} in the last two weeks`] } : { title: 'Nothing in the last two weeks yet' });
    UI.barChart(el, days.map(d => ({ day: d.day, right: d.right || 0, wrong: Math.max(0, (d.questions || 0) - (d.right || 0)),
      tip: `${UI.date(d.day)} · ${plural(d.questions || 0, 'question')}${d.questions ? ` · ${pc(d.right, d.questions)}%` : ''}${d.minutes ? ` · ${UI.dur(d.minutes)}` : ''}` })),
    { series: [{ key: 'right', label: 'Right', look: 'amber' }, { key: 'wrong', label: 'Wrong', look: 'ink' }], stacked: true, labels: 'weekday', unit: 'q', legend: !!q, label: 'Questions a day, the last 14 days' });
  }

  /* ------------------------------------------------------------ why you miss (SR22) */
  function drawWhy() {
    const el = $('why');
    el.hidden = true;
    const w = ST && ST.why;
    if (!w || !w.total) return;
    const by = w.by || {};
    const keys = ['trap', 'slip', 'misread', 'clock', 'entry', 'gap', 'changed'].filter(k => by[k]);
    head(el, { fig: [n(w.total), `${w.total === 1 ? 'miss' : 'misses'} in the last ${n(w.days || 14)} days, by cause`] });
    UI.stackBar(el, keys.map(k => ({ key: k, label: (rx.CAUSE[k] || { label: cap(k) }).label, value: by[k] })), { label: 'Misses by cause', noun: 'misses', format: v => n(v), legend: keys.length > 1 ? 'auto' : false });
  }

  /* ------------------------------------------------------------ difficulty and format (2.5) */
  function drawSplit() {
    const el = $('split');
    el.hidden = true;
    const d = (ST && ST.by_difficulty) || [], f = (ST && ST.by_format) || [];
    if (!d.some(r => r.answered)) return;
    const all = d.reduce((t, r) => t + (r.answered || 0), 0), right = d.reduce((t, r) => t + (r.right || 0), 0);
    head(el, { fig: [n(right), `of ${n(all)} right, all time`] });      // a count over a percentage; the rows keep theirs
    const bars = h('div', { class: 'rs-bars' });
    const row = (lab, r) => bars.append(h('div', { class: 'rs-bar', style: `--rp: ${r.answered ? r.right / r.answered : 0}` }, h('span', {}, lab), h('span', { class: 't' }, h('i')),
      h('span', { class: 'rs-num', text: [`${sc(r.right, r.answered)} · ${pc(r.right, r.answered)}%`, r.avg_ms ? `avg ${tm(r.avg_ms)}` : null].filter(Boolean).join(' · ') })));
    d.filter(r => r.answered).forEach(r => row(UI.dbars ? UI.dbars(r.difficulty || r.key) : TIER[r.key], r));
    if (f.filter(r => r.answered).length > 1) f.forEach(r => row(FORMAT[r.format || r.key] || r.key, r));
    el.append(bars);
  }

  /* ------------------------------------------------------------ domains across sections (2.6) */
  function drawDomains() {
    const el = $('domtrend');
    el.hidden = true;
    const cols = ((ST && ST.domains_over_time) || []).slice().reverse();
    if (!cols.length) return;
    const m = SUBJ === 'rw' ? 27 : 22, name = UI.subjectLabel(SUBJ);
    head(el, { title: 'Each domain, sitting by sitting', about: 'this table', tip: `A section is one full SAT ${name} section: two modules, ${2 * m} questions. A module is one half of it (${m} questions). Each cell is how many you got right in that domain; the small triangles show the change from the sitting before.` });
    const doms = domainOrder(SUBJ).filter(d => cols.some(c => (c.domains || []).some(x => x.domain === d)));
    const old = i => (cols.length - i > 3 ? 'old' : null);
    const sess = new Map(((HIST && HIST.sessions) || []).map(x => [x.id, x]));
    const kindOf = id => (sess.get(id) || {}).kind;
    const colName = (c, i) => { const k = kindOf(c.id); return `${k === 'module' ? 'Module' : k === 'diagnostic' ? 'Diagnostic' : 'Full section'} #${c.seq || i + 1}`; };
    const colTip = c => { const k = kindOf(c.id); return k === 'module' ? `One module: ${m} questions` : k === 'diagnostic' ? 'The diagnostic: 20 questions' : `A full section: two modules, ${2 * m} questions`; };
    const t = h('table', { class: 'rs-dt' });
    t.append(h('thead', {}, h('tr', {}, h('th', { scope: 'col', text: 'Domain' }), cols.map((c, i) => {
      const at = (sess.get(c.id) || {}).finished;
      return h('th', { scope: 'col', class: old(i), title: colTip(c) }, h('a', { href: rx.reportHref(c.id), text: colName(c, i) }), at ? h('div', { class: 'meta', text: UI.date(at) }) : null);
    }))));
    const tb = h('tbody');
    doms.forEach(d => {
      const tr = h('tr', {}, h('th', { scope: 'row', text: d }));
      let prev = null;
      cols.forEach((c, i) => {
        const x = (c.domains || []).find(y => y.domain === d);
        if (!x || !x.asked) { tr.append(h('td', { class: old(i) })); prev = null; return; }
        const p = x.right / x.asked;
        const arrow = prev === null ? '' : p > prev + 0.001 ? ' ▴' : p < prev - 0.001 ? ' ▾' : '';
        const tip = prev === null ? `${sc(x.right, x.asked)} right` : `${sc(x.right, x.asked)} right · was ${Math.round(prev * 100)}%`;
        tr.append(h('td', { class: old(i), 'data-s': '', style: `--s: ${p}`, title: tip },
          h('div', { class: 'rs-pct' }, h('b', { text: `${Math.round(p * 100)}%` }), arrow ? h('span', { class: 'rs-arrow', text: arrow.trim() }) : null),
          h('div', { class: 'meta', text: sc(x.right, x.asked) })));
        prev = p;
      });
      tb.append(tr);
    });
    t.append(tb);
    el.append(h('div', { class: 'table-wrap' }, t));
  }

  /* ------------------------------------------------------------ sittings (2.9, SR23) */
  const SITQ = { set: P.get('set') || 'all', kind: P.get('kind') || '', open: P.get('open') === '1', sort: P.get('sort') || 'newest' };
  let shown = 5, cards = [], selected = [], more = '';   // more: the count before Show more, which rolls to the new one
  function writeQ() {
    const u = new URL(location.href);
    [['set', SITQ.set === 'all' ? '' : SITQ.set], ['kind', SITQ.kind], ['open', SITQ.open ? '1' : ''], ['sort', SITQ.sort === 'newest' ? '' : SITQ.sort]].forEach(([k, v]) => { if (v) u.searchParams.set(k, v); else u.searchParams.delete(k); });
    if (u.href !== location.href) history.replaceState(history.state, '', u);
  }
  const setOf = s => (TESTS.includes(s.kind) ? 'tests' : s.kind === 'challenge' || s.kind === 'contest' ? 'challenge' : 'practice');
  const weekStart = d => { const x = new Date(d); x.setHours(0, 0, 0, 0); x.setDate(x.getDate() - ((x.getDay() + 6) % 7)); return x; };
  function drawSittings() {
    const el = $('sittings');
    const all = ((HIST && HIST.sessions) || []).filter(s => s.kind !== 'words');
    const counts = (HIST && HIST.counts) || { all: all.length, tests: all.filter(s => setOf(s) === 'tests').length, practice: all.filter(s => setOf(s) === 'practice').length, challenge: all.filter(s => setOf(s) === 'challenge').length };
    head(el, { title: 'Sittings' });
    const prog = ((HIST && HIST.in_progress) || []).filter(x => !readOnly);
    if (!all.length && !prog.length) {
      el.hidden = true;                             // nothing finished: no empty card
      return;
    }
    const tools = h('div', { class: 'rs-row' });
    const segOpts = [['all', 'All'], ['tests', 'Tests'], ['practice', 'Practice'], ['challenge', 'Challenge']].filter(([k]) => k === 'all' || counts[k] || SITQ.set === k).map(([value, label]) => ({ value, label, n: counts[value] }));
    const seg = UI.seg(null, segOpts, { value: SITQ.set, label: 'Which sittings', onChange: v => { SITQ.set = v; SITQ.kind = ''; shown = 5; writeQ(); drawSittings(); } });
    tools.append(seg.el);
    // the kind of test, Has open mistakes and the sort: one menu button beside the seg, its count the filters on
    const ks = SITQ.set === 'tests' ? [...new Set(all.filter(s => setOf(s) === 'tests').map(s => s.kind))] : [];
    const anyOpen = all.some(s => s.open);
    const sorts = [['newest', 'Newest'], ['oldest', 'Oldest'], ['highest', 'Highest'], ['lowest', 'Lowest'], all.some(s => s.recovery) && ['points_open', 'Most points still open']].filter(Boolean);
    const on = (SITQ.kind ? 1 : 0) + (SITQ.open ? 1 : 0), name = ks.length > 1 || anyOpen ? 'Sort and filter' : 'Sort';
    const fb = h('button', { type: 'button', class: 'btn sm dd' + (on ? ' on' : ''), id: 'sitfilt' }, h('span', { text: on ? `${name} · ${n(on)}` : name }));
    // a pick redraws the card once the menu has closed, and focus comes back to the new button
    const redo = fn => () => { fn(); setTimeout(() => { drawSittings(); const t = $('sitfilt'); if (t) t.focus(); }); };
    UI.menu.bind(fb, () => [
      (ks.length > 1 || anyOpen) && { group: 'Filter' },
      ...(ks.length > 1 ? [['', 'All tests'], ...ks.map(k => [k, k === 'full' ? 'Full SAT' : UI.KIND[k] || cap(k)])] : []).map(([v, l]) => ({ label: l, radio: 'kind', checked: SITQ.kind === v, close: true,
        onClick: redo(() => { SITQ.kind = v; shown = 5; writeQ(); }) })),
      anyOpen && { label: 'Has open mistakes', checked: SITQ.open, close: true, onClick: redo(() => { SITQ.open = !SITQ.open; shown = 5; writeQ(); }) },
      (ks.length > 1 || anyOpen) && { separator: true },
      { group: 'Sort' },
      ...sorts.map(([v, l]) => ({ label: l, radio: 'sort', checked: SITQ.sort === v, close: true, onClick: redo(() => { SITQ.sort = v; writeQ(); }) })),
    ], { label: 'Sort and filter sittings', align: 'end' });
    tools.append(fb);
    el.querySelector('.card-head').append(h('div', { class: 'rs-headr' }, tools));
    if (prog.length) {
      const g = h('div', { class: 'rs-group' }, h('h3', { class: 'rs-wk', text: 'In progress' }));
      const list = h('div', { class: 'rs-list' });
      prog.forEach(r => UI.sittingCard(list, r, { progress: true }));
      g.append(list);
      el.append(g);
    }
    const score = s => (s.estimate && s.estimate.low ? (s.estimate.low + s.estimate.high) / 2 : s.asked ? s.right / s.asked * 800 : 0);
    let rows = all.filter(s => (SITQ.set === 'all' || setOf(s) === SITQ.set) && (!SITQ.kind || s.kind === SITQ.kind) && (!SITQ.open || s.open));
    const by = { newest: (a, b) => String(b.finished).localeCompare(String(a.finished)), oldest: (a, b) => String(a.finished).localeCompare(String(b.finished)),
      highest: (a, b) => score(b) - score(a), lowest: (a, b) => score(a) - score(b), points_open: (a, b) => ((b.recovery || {}).points_open || 0) - ((a.recovery || {}).points_open || 0) }[SITQ.sort];
    rows = rows.slice().sort(by);
    cards = [];
    const list = h('div', { class: 'rs-list' });
    const page = rows.slice(0, shown);
    // a filtered list that comes up empty says so once, with the way back
    if (!page.length) list.append(h('div', { class: 'rs-row' }, h('p', { class: 'rs-helper', text: 'No sittings match.' }),
      SITQ.kind || SITQ.open ? btn('Clear', () => { SITQ.kind = ''; SITQ.open = false; shown = 5; writeQ(); drawSittings(); }, 'quiet') : null));
    const grouped = SITQ.sort === 'newest' || SITQ.sort === 'oldest';
    let wk = null;
    const now = weekStart(new Date());
    page.forEach(s => {
      if (grouped) {
        const w = weekStart(s.finished).getTime();
        if (w !== wk) {
          wk = w;
          const diff = Math.round((now - w) / (7 * 864e5));
          const end = new Date(w + 6 * 864e5);
          const inWeek = rows.filter(x => weekStart(x.finished).getTime() === w);
          const qn = inWeek.reduce((a, x) => a + (x.asked || 0), 0);
          list.append(h('h3', { class: 'rs-wk' }, diff === 0 ? 'This week' : diff === 1 ? 'Last week' : `${UI.date(w)}–${UI.date(end)}`,
            h('span', { class: 'meta', text: ` · ${plural(inWeek.length, 'sitting')}${qn ? ` · ${plural(qn, 'question')}` : ''}` })));
        }
      }
      cards.push(UI.sittingCard(list, s, { share: readOnly, shareToken: SHARE || null, onSelect: pick, subjects: both() ? 2 : 1 }));
    });
    el.append(list);
    if (rows.length > shown) {
      const cnt = h('span', { text: n(shown) });
      el.append(h('div', { class: 'rs-row rs-more' }, h('span', { class: 'meta' }, 'Showing ', cnt, ` of ${n(rows.length)}`),
        btn(`Show ${n(Math.min(5, rows.length - shown))} more`, () => { more = n(shown); shown += 5; drawSittings(); })));
      if (more && more !== cnt.textContent) { const to = cnt.textContent; cnt.textContent = more; UI.roll(cnt, to); }
    }
    more = '';
  }
  function pick(row, on) {
    selected = selected.filter(r => r.id !== row.id);
    if (on) selected.push(row);
    if (selected.length > 2) { const drop = selected.shift(); const c = cards.find(x => x.row.id === drop.id); if (c) c.select(false); }
    const bar = $('cmpbar'), was = bar.hidden;
    bar.hidden = selected.length < 2;
    if (bar.hidden) return;
    if (was && UI.motion) UI.motion.enter(bar, 'nudge');
    const [a, b] = selected.slice().sort((x, y) => String(y.finished).localeCompare(String(x.finished)));
    bar.replaceChildren(h('span', { text: `Compare ${UI.KIND.label(a)}${a.seq ? ` #${a.seq}` : ''} with ${UI.KIND.label(b)}${b.seq ? ` #${b.seq}` : ''}` }),
      h('a', { class: 'pill sm', href: `/results/report/?id=${encodeURIComponent(a.id)}&vs=${encodeURIComponent(b.id)}`, text: 'Compare' }),
      btn('Clear', (b, e) => {
        cards.forEach(c => { if (c.selected) c.select(false); });
        selected = [];
        const gone = () => { bar.hidden = true; if (bar.getAnimations) bar.getAnimations().forEach(a => a.cancel()); };
        if (UI.motion && UI.motion.ok(e)) UI.motion.exit(bar, 'nudge').then(gone); else gone();
      }, 'quiet'));
  }

  /* ------------------------------------------------------------ mistakes (2.8): the misconceptions you hit most */
  function drawTraps() {
    const el = $('traps');
    if (both()) { el.hidden = true; return; }       // a subject's own: Both would show Math's alone
    const list = (ST && ST.top_traps) || [];
    if (!list.length) {
      if (ST && ST.answered) head(el, { title: 'Mistakes', meta: 'None yet', tip: 'Every miss you make lands here with its name.', about: 'mistakes' });
      else el.hidden = true;
      return;
    }
    const open = (ST.traps || {}).open || 0;
    let view = 'open', all = false;   // the ones still open lead; "All" adds the fixed ones; five rows until Show all
    const tg = UI.seg(null, [{ value: 'open', label: 'Not fixed' }, { value: 'all', label: 'All' }], { value: view, label: 'Which mistakes', onChange: v => { view = v; drawList(); } });
    head(el, { title: 'Mistakes', right: [tg.el,
      !readOnly && open && PRIMARY !== 'fix' ? btn(`Fix all open · ${n(open)}`, b => drill({ mistakes: true, source: 'fix', subject: statSubj() }, b)) : null,
      readOnly ? null : h('a', { class: 'quiet', href: '/mistakes/', text: 'All mistakes' })] });
    const box = h('div');
    el.append(box);
    function drawList() {
      box.replaceChildren();
      const rows = list.filter(t => view === 'all' || !t.closed).slice(0, 10);
      if (!rows.length) { box.append(h('div', { class: 'rs-clear' }, view === 'open' && UI.spotArt ? h('span', { html: UI.spotArt('clear') }) : null, h('p', { class: 'rs-helper', text: 'Nothing open: every mistake here is fixed.' }))); return; }
      rows.slice(0, all ? 10 : 5).forEach(t => {
        const st = t.closed ? h('span', { class: 'st', text: `✓ Fixed ${UI.date(t.closed)}` }) : h('span', { class: 'st open', text: `Open, ${plural(t.owed || 2, 'correct answer')} to close` });
        box.append(h('div', { class: 'rs-trap' }, glyph(t.topic) || h('span'), h('div', {}, h('h4', { text: cap(t.label) }),
          h('p', { class: 'meta' }, `${[topicName(t.topic), `×${n(t.hits)}`].join(' · ')} · `, st)),
          readOnly || t.closed ? h('span') : h('div', { class: 'rs-row reveal' }, btn('Fix', b => drill({ pool: 'redo', templates: [t.template], topics: [t.topic], source: 'mistakes' }, b)))));
      });
      if (rows.length > 5) box.append(h('div', { class: 'rs-row rs-more' }, btn(all ? 'Show fewer' : `Show all ${n(rows.length)}`, () => { all = !all; drawList(); }, 'quiet')));
    }
    drawList();
  }

  /* ------------------------------------------------------------ skills (2.7): one row each; a tap opens its stats, and Practise starts that skill only */
  function drawSkills() {
    const el = $('skills');
    // the subject's skills (Both: R&W's then Math's); an R&W skill's domain from UI.RW_DOMAINS when the map has none
    const subjOf = t => t.subject || (UI.subjectOf ? UI.subjectOf(t.topic) : 'math');
    const rwDom = slug => ((UI.RW_DOMAINS || []).find(d => d.skills.includes(slug)) || {}).name;
    const topics = ((MAP && MAP.topics) || []).filter(t => both() || subjOf(t) === SUBJ)
      .map(t => (subjOf(t) === 'rw' && !(UI.RW_DOMAINS || []).some(d => d.name === t.domain) ? Object.assign({}, t, { domain: rwDom(t.topic) || t.domain }) : t));
    if (!topics.length) { head(el, { title: 'Skills' }); el.hidden = true; return; }     // no skills yet: no empty card
    // a count, not a percentage: how many are Strong (or, before any is, how many are started)
    const strong = topics.filter(t => t.answered && (t.mastery || 0) >= (UI.STRONG || 0.8)).length, started = topics.filter(t => t.answered).length;
    head(el, { title: 'Skills', meta: strong ? `${n(strong)} of ${n(topics.length)} strong` : `${n(started)} of ${n(topics.length)} started` });
    let sort = LS.get('satf.results.skills', 'domain');
    const sel = UI.dropdown(null, { label: 'Sort', sm: true, plain: true, noAll: true, default: 'domain', value: sort,
      options: [['domain', 'By domain'], ['weak', 'Weakest first'], ['open', 'Most open mistakes'], ['least', 'Least practised'], ['recent', 'Least recent']].map(([value, label]) => ({ value, label })),
      onChange: v => { sort = v; LS.set('satf.results.skills', sort); draw(); } });
    el.querySelector('.card-head').append(h('div', { class: 'rs-headr' }, sel.el));
    const box = h('div', { class: 'rs-skills' });
    el.append(box);
    // a row: glyph, name, mastery bar, right of answered, open mistakes; the mastery word and the counts are its
    // tooltip and label, and the panel a tap opens
    const tile = t => {
      const open = (t.traps || []).length;
      const name = topicName(t.topic, t.name);
      const word = UI.masteryWord ? UI.masteryWord(t.mastery, t.answered) : '';
      const pct = Math.round((t.accuracy || 0) * 100), right = Math.round((t.accuracy || 0) * (t.answered || 0));
      const said = t.answered ? `${word ? `${word}, ` : ''}${n(t.answered)} answered, ${pct}% right` : 'not started';
      const b = h('button', { type: 'button', class: 'rs-skill', title: `${name}: ${said}`, 'aria-label': `${name}: ${said}${open ? `, ${n(open)} open mistakes` : ''}. Open its stats.` },
        (subjOf(t) === 'math' && glyph(t.topic)) || h('span'), h('span', { class: 'rs-sn', text: name }),
        t.answered ? h('span', { class: 'mbar', 'aria-hidden': 'true' }, h('i', { style: `--m: ${Math.max(0, Math.min(1, t.mastery || 0))}` })) : h('span'),
        h('span', { class: 'rs-sv', text: t.answered ? `${n(right)}/${n(t.answered)}` : '' }),
        open ? h('span', { class: 'rs-open', text: `${n(open)} open` }) : h('span'));
      b.addEventListener('click', () => UI.skillPanel(t.topic, { share: SHARE || null, fallback: { topic: t.topic, domain: t.domain, mastery: t.mastery, answered: t.answered, right } }));
      return b;
    };
    function draw() {
      box.replaceChildren();
      const cmp = { weak: (a, b) => (a.answered ? a.mastery : 2) - (b.answered ? b.mastery : 2), open: (a, b) => (b.traps || []).length - (a.traps || []).length,
        least: (a, b) => (a.answered || 0) - (b.answered || 0), recent: (a, b) => String(a.last || '').localeCompare(String(b.last || '')) }[sort];
      if (!cmp) {
        (both() ? [...domainOrder('rw'), ...domainOrder('math')] : domainOrder(SUBJ)).forEach(d => {
          const ts = topics.filter(t => t.domain === d);
          if (!ts.length) return;
          box.append(h('h3', { class: 'rs-dom-h', text: d }));
          ts.forEach(t => box.append(tile(t)));
        });
      } else topics.slice().sort(cmp).forEach(t => box.append(tile(t)));
    }
    draw();
  }

  /* ------------------------------------------------------------ CSV of every sitting */
  async function csv() {
    let rows = [];
    try {
      for (let off = 0; off < 5000; off += 200) {
        const r = await UI.api(withQ(`/history?limit=200&offset=${off}&all=1`), { quiet: true });
        const s = r.sessions || [];
        rows = rows.concat(s);
        if (!r.counts || s.length < 200) break;     // the older route returns everything at once
      }
    } catch (_) { UI.toast('Couldn’t export. Try again.'); return; }
    const esc = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const lines = [['finished', 'kind', 'number', 'right', 'asked', 'band_low', 'band_high', 'minutes', 'open_mistakes', 'report'].join(',')]
      .concat(rows.map(s => [s.finished, UI.KIND.label(s), s.seq || '', s.right ?? '', s.asked ?? '', (s.estimate || {}).low ?? '', (s.estimate || {}).high ?? '',
        s.ms ? Math.round(s.ms / 60000) : '', s.open || '', `${location.origin}${rx.reportHref(s.id)}`].map(esc).join(',')));
    const a = h('a', { href: URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' })), download: 'sat-freshman-results.csv' });
    doc.body.append(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  /* ------------------------------------------------------------ keys (page scope results, SR23) */
  if (UI.keys && UI.keys.register) {
    const at = () => cards.findIndex(c => c.el === doc.activeElement || c.el.contains(doc.activeElement));
    const move = d => () => { if (!cards.length) return false; const i = at(); const c = cards[Math.max(0, Math.min(cards.length - 1, i < 0 ? 0 : i + d))]; c.el.focus(); c.el.scrollIntoView({ block: 'nearest' }); };
    UI.keys.register('results', {
      J: { does: 'Next sitting', run: move(1) }, K: { does: 'Previous sitting', run: move(-1) },
      F: { does: 'Fix this sitting', run: () => { const i = at(); if (i < 0) return false; cards[i].fix(); } },
      X: { does: 'Select for Compare', run: () => { const i = at(); if (i < 0) return false; cards[i].select(); } },
    }, { label: 'Results', when: () => !doc.querySelector('dialog[open]') });
  }

  // the switch reloads the page's regions for that subject; the URL keeps it (links and reloads agree)
  if (UI.subjectSeg) UI.subjectSeg($('subject'), { both: true, value: SUBJ, onChange: v => { SUBJ = v; shown = 5; SITQ.kind = ''; writeQ(); load(); } });
  load();
})();
