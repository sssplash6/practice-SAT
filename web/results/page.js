/* ============================================================================
   SAT Freshman -- Results, /results/ (S6)
   (spec/rebuild-v2.md 3.5 §2; v2-upgrades reports.md SR21-SR24; decisions 3, 4, 7;
   the user's order of 2026-09-28: Sittings before Skills)

   Where you stand (the estimate and the chart), every sitting (UI.sittingCard, in
   progress, filters in the URL, paging), where the points go (totals, then one Trends
   card with tabs: gap, the last 14 days, why you miss, difficulty and format, domains
   across sections), the top misconceptions, then every skill (a tap opens UI.skillPanel; its primary starts a
   set on that skill only).

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
  const TESTS = ['mock', 'module', 'diagnostic', 'paper', 'custom', 'twin', 'shared'];
  const DOMAIN_ORDER = (UI.DOMAINS || []).map(d => d[0]);
  const topicName = (slug, fb) => ((UI.TOPIC && UI.TOPIC[slug]) || {}).short || fb || slug || '';
  const glyph = slug => (UI.glyph && slug ? UI.glyph(slug) : null);
  const LS = { get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} } };
  const btn = (text, onClick, cls = 'btn sm') => { const b = h('button', { type: 'button', class: cls, text }); b.addEventListener('click', e => onClick(b, e)); return b; };
  const info = text => { const b = h('button', { type: 'button', class: 'quiet rs-info', 'aria-label': text }, 'ⓘ'); if (UI.tooltip) UI.tooltip(b, text); return b; };
  function head(host, o) {
    host.hidden = false;
    host.replaceChildren(h('div', { class: 'card-head' }, o.k ? h('p', { class: 'k', text: o.k }) : null, h(host.closest('#trends') ? 'h3' : 'h2', { text: o.title }),
      o.meta ? h('span', { class: 'meta', text: o.meta }) : null, o.tip ? info(o.tip) : null, o.right ? h('div', { class: 'rs-headr' }, o.right) : null));
    return host;
  }
  const readOnly = !!SHARE;
  const drill = (body, b) => (readOnly ? null : rx.drill(body, b));
  async function startTest(full, b) {
    if (b) b.setAttribute('aria-busy', 'true');
    try { const s = await UI.api('/mock/new', { method: 'POST', body: { full, timed: true } }); location.href = `/test/?s=${encodeURIComponent(s.id)}`; }
    catch (_) { if (b) b.removeAttribute('aria-busy'); UI.toast('Couldn’t start the test. Try again.'); }
  }
  // a region that fails keeps its heading and says so, with Retry (the page never goes blank)
  async function region(id, fn) { try { await fn(); } catch (e) { const el = $(id); el.hidden = false; UI.cardError(el, () => region(id, fn), 'Couldn’t load this.'); } }

  let ST = null, HIST = null, MAP = null;
  // 2.10: a feed that failed on arrival is fetched again by each region that needs it, so a region
  // shows its own error with Try again instead of an empty state; the regions share one request
  const FEED = { ST: ['/stats', r => { ST = r; }, () => ST], HIST: ['/history?limit=200&all=1', r => { HIST = r; }, () => HIST], MAP: ['/map', r => { MAP = r; }, () => MAP] };
  const pend = {};
  const refetch = k => pend[k] || (pend[k] = UI.api(withQ(FEED[k][0]), { quiet: true }).then(FEED[k][1]).finally(() => { delete pend[k]; }));
  const needs = (keys, fn) => () => { const miss = keys.filter(k => !FEED[k][2]()); return miss.length ? Promise.all(miss.map(refetch)).then(() => fn()) : fn(); };

  /* ------------------------------------------------------------ load */
  function skeleton() {
    $('estimate').replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'lines:4'));
    $('overview').replaceChildren(UI.skel(null, 'chart:220'));
    $('totals').replaceChildren(h('div', { class: 'stats' }, Array.from({ length: 8 }, () => UI.skel(null, 'tile'))));
    $('sittings').replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'rows:4'));
    $('skills').replaceChildren(UI.skel(null, 'line.lg'), UI.skel(null, 'rows:3'));
  }
  async function load() {
    skeleton();
    if (readOnly) $('head').after(h('div', { class: 'rs-strip' }, h('b', { text: 'Shared progress · read-only' })));
    headActions();
    const stats = UI.api(withQ('/stats'), { quiet: true });
    const hist = UI.api(withQ('/history?limit=200&all=1'), { quiet: true });
    const map = UI.api(withQ('/map'), { quiet: true });
    try { ST = await stats; } catch (e) {
      if (e && e.status === 404 && readOnly) { $('main').removeAttribute('aria-busy'); $('root').replaceChildren(h('section', { class: 'card' }, h('h2', { class: 'h2', text: 'That progress link doesn’t work any more.' }), h('p', { class: 'rs-helper', text: 'Ask for a new one.' }))); return; }
      ST = null;
    }
    try { HIST = await hist; } catch (_) { HIST = null; }
    try { MAP = await map; } catch (_) { MAP = null; }
    $('main').removeAttribute('aria-busy');
    const tests = () => ((HIST && HIST.sessions) || []).filter(s => TESTS.includes(s.kind));
    // the stats regions: without /api/stats one error card stands in the estimate's place (no
    // repeats), and its Try again draws them all
    const byStats = [['estimate', drawEstimate], ['overview', needs(['HIST'], () => drawChart(tests()))], ['totals', drawTotals], ['trends', drawTrends], ['traps', drawTraps]];
    if (ST) byStats.forEach(([id, fn]) => region(id, fn));
    else {
      const was = byStats.map(([id]) => $(id).hidden);
      byStats.slice(1).forEach(([id]) => { $(id).hidden = true; });
      region('estimate', async () => { await refetch('ST'); byStats.forEach(([id, fn], k) => { $(id).hidden = was[k]; region(id, fn); }); });
    }
    region('sittings', needs(['HIST'], drawSittings));
    region('skills', needs(['MAP'], drawSkills));
    UI.shell({ page: 'results', sections: [{ id: 'estimate', label: 'Estimate' }, { id: 'sittings', label: 'Sittings' }, { id: 'totals', label: 'Totals' },
      { id: 'traps', label: 'Mistakes' }, { id: 'skills', label: 'Skills' }].filter(x => !$(x.id).hidden) });
  }

  /* ------------------------------------------------------------ header */
  function headActions() {
    const box = $('headacts');
    box.replaceChildren();
    const dots = h('button', { type: 'button', class: 'btn icon', 'aria-label': 'More', 'aria-haspopup': 'menu', text: '⋯' });
    dots.addEventListener('click', () => UI.menu(dots, [
      { label: 'Download CSV (all sittings)', onClick: csv },
      { label: 'Print', onClick: () => window.print() },
      !readOnly && { label: 'Share a read-only link', onClick: shareSheet },
    ].filter(Boolean), { label: 'More', align: 'end' }));
    box.append(btn('Share', () => shareChoose(), 'btn sm'), dots);
  }
  // Share: for a parent or a tutor. The student picks a language and a PDF of the progress downloads at once.
  const LANGS = [['uz', 'Oʻzbekcha', 'Uzbek'], ['en', 'English', 'English'], ['ru', 'Русский', 'Russian']];
  async function downloadReport(lang) {
    const r = await fetch(`/api/results/progress.pdf?lang=${lang}${SHARE ? `&share=${encodeURIComponent(SHARE)}` : ''}`,
      { headers: { 'X-Learner': UI.learner(), 'X-Tz': String(new Date().getTimezoneOffset()) } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const a = h('a', { href: URL.createObjectURL(await r.blob()), download: `progress-${lang}-${new Date().toISOString().slice(0, 10)}.pdf` });
    document.body.append(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
  }
  function shareChoose() {
    let sh;
    const tiles = LANGS.map(([code, native, english]) => {
      const b = h('button', { type: 'button', class: 'rs-lang' }, h('span', { text: native }), h('small', { text: english }));
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
      h('div', { class: 'rs-row' }, btn('Copy', () => UI.copyText(url, { toast: 'Link copied · read-only' }), 'pill sm'),
        btn('Stop sharing', async b => { b.setAttribute('aria-busy', 'true'); try { await stop(); sh.close(); UI.toast('Link turned off'); } catch (_) { b.removeAttribute('aria-busy'); UI.toast('Not saved. Try again.'); } }, 'quiet')));
  }

  /* ------------------------------------------------------------ the estimate (2.2, SR21) */
  function drawEstimate() {
    const el = $('estimate');
    el.replaceChildren();
    const E = ST && ST.estimate;
    const band = E && (E.low !== undefined && E.low !== null ? E : E.combined || E.range);
    const pr = (ST && ST.profile) || {};
    if (!E || !E.latest || !band || band.low === undefined) {
      // no scored test: this is the page's only card (the chart, sittings and skills stay out of the way)
      el.style.gridColumn = '1 / -1';
      head(el, { k: 'Current estimate', title: readOnly ? 'No scored test yet' : 'Sit your first test' });
      if (!readOnly) {
        // the two ways in: the section is the most accurate, the module the quick start
        el.append(h('div', { class: 'rs-row' }, btn('Full section · 70 min', b => startTest(true, b), 'pill sm'), btn('One module · 35 min', b => startTest(false, b), 'pill sm')),
          h('p', { class: 'meta', style: 'margin-top: 10px', text: 'A full section is the most accurate. A module is the quick way in.' }),
          h('div', { class: 'rs-row', style: 'margin-top: 14px' }, h('a', { class: 'btn sm', href: '/results/report/?id=sample-section', text: 'Open the sample report' }),
            // S3's add-a-score sheet; hidden until it lands, so no button does nothing
            UI.addScore ? btn('Add a score you already have', () => UI.addScore({ onSaved: () => load() }), 'quiet') : null));
      }
      return;
    }
    el.style.gridColumn = '';
    const low = Math.round(band.low / 10) * 10, high = Math.round(band.high / 10) * 10;
    el.append(h('p', { class: 'k', text: 'Current estimate' }));
    const nSit = (E.counted || {}).sittings || 1;
    const conf = E.confidence || {}, tr = E.trend || {};
    // one hero: the band, with its two chips beside it; the sentences behind them are tooltips
    const chips = h('span', { class: 'rs-chips' });
    if (conf.level) chips.append(h('span', { class: 'badge soft lg', title: conf.reason || '', text: `${cap(conf.level)} confidence` }));
    if (tr.direction && tr.direction !== 'steady' && tr.delta) chips.append(h('span', { class: 'badge lg', text: `${tr.direction === 'up' ? '↑ +' : '↓ −'}${n(Math.abs(tr.delta))} since ${UI.date(tr.since)}` }));
    const from = `${nSit === 1 ? 'From your last scored sitting' : `From your last ${n(nSit)} scored sittings`}. Sections count double; sittings from the last 60 days. Math is measured here; Reading and Writing is your own score until SAT Freshman has R&W questions.`;
    el.append(h('div', { class: 'rs-est' }, h('span', { class: 'rs-big', text: low === high ? `Math ${low}` : `Math ${low}–${high}` }), info(from)), chips);
    // where the band sits against the target, on the 200–800 scale
    if (pr.target) {
      const x = v => `${(Math.max(200, Math.min(800, v)) - 200) / 6}%`;
      el.append(h('div', { class: 'rs-track', role: 'img', 'aria-label': `Estimate ${low} to ${high}, target ${pr.target}, on a 200 to 800 scale` },
        h('b', { class: 'band', style: `left: ${x(low)}; width: calc(${x(high)} - ${x(low)})` }), h('i', { class: 't', style: `left: ${x(pr.target)}` }),
        h('span', { class: 'tl', style: `left: ${x(pr.target)}`, text: String(pr.target) })));
    }
    // three stats, each a label over a value
    const bandOf = x => `${Math.round(x.low)}–${Math.round(x.high)}`;
    const stat = (k, v, sub) => h('div', { class: 'rs-st' }, h('span', { class: 'k', text: k }), h('b', { text: v }), sub ? h('span', { class: 'meta', text: sub }) : null);
    const stats = h('div', { class: 'rs-stats' });
    if (E.best) stats.append(stat('Best', bandOf(E.best), UI.date(E.best.at)));
    if (pr.target) stats.append(stat('Target', String(pr.target), high >= pr.target ? 'reached' : `${n(pr.target - high)} above`));
    if (pr.exam_date) { const d = Math.round((new Date(pr.exam_date) - new Date()) / 864e5); if (d >= 0) stats.append(stat('Exam', UI.date(pr.exam_date), plural(d, 'day'))); }
    if (stats.childNodes.length) el.append(stats);
    if (!readOnly && conf.level && conf.level !== 'high') {
      const b = btn(conf.level === 'low' ? 'A full section → Medium · 70 min' : 'One more full section → High · 70 min', bb => startTest(true, bb));
      el.append(h('div', { class: 'rs-row' }, b));
    }
  }

  /* ------------------------------------------------------------ score over time (2.3, SR21) */
  function drawChart(tests) {
    const el = $('overview');
    const pts = tests.filter(s => s.estimate && s.estimate.low).slice().reverse().map(s => ({
      id: s.id, at: s.finished, low: s.estimate.low, high: s.estimate.high, kind: s.kind, label: `${UI.KIND.label(s)}${s.seq ? ` #${s.seq}` : ''}`,
      detail: [s.asked ? sc(s.right || 0, s.asked) : null, s.route ? (s.route === 'upper' ? 'harder M2' : 'easier M2') : null].filter(Boolean).join(' · '),
      href: rx.reportHref(s.id) + (SHARE ? '' : '') }));
    el.hidden = !pts.length;                        // no scored test yet: the estimate card is the one card
    el.replaceChildren(h('p', { class: 'k', text: 'Score over time' }));
    if (el.hidden) return;
    const E = ST && ST.estimate, band = E && (E.low !== undefined && E.low !== null ? E : E.combined || E.range);
    UI.bandChart(el, pts, { target: (ST && ST.profile || {}).target, estimate: band && band.low ? { low: band.low, high: band.high } : null,
      filters: pts.length > 1, store: 'satf.results.chart', label: 'Score over time', legend: true,
      onPick: p => { location.href = rx.reportHref(p.id); },
      empty: { text: 'Your first test puts a point here.' } });
  }

  /* ------------------------------------------------------------ Trends: five analyses, one card, one read at a time (UI.tabs) */
  async function drawTrends() {
    const el = $('trends');
    const panels = [['gap', 'Gap', drawGap], ['days', 'Last 14 days', drawDays], ['why', 'Why you miss', drawWhy], ['split', 'Difficulty and format', drawSplit],
      ['domtrend', 'Domains', needs(['HIST'], drawDomains)]];
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
    const pr = (ST && ST.profile) || {};
    head(el, { k: 'Gap to target', title: pr.target ? `Target ${pr.target}: where the points are` : 'Where your next points are',
      tip: 'The gain is what reaching Strong on a skill would add to a section, from how often it comes up.' });
    const rows = (g.skills || []).filter(s => s.gain > 0).slice(0, 5);
    const list = h('div', { class: 'rs-bars' });
    const top = Math.max(...rows.map(s => s.gain), 1);
    rows.forEach(s => list.append(h('div', { class: 'rs-bar', style: `--rp: ${s.gain / top}` }, h('span', {}, glyph(s.topic), ' ', topicName(s.topic)), h('span', { class: 't' }, h('i')),
      h('span', { class: 'rs-row' }, h('b', { class: 'rs-num', text: `≈ +${n(s.gain)}` }), readOnly ? '' : btn('Practise', b => drill({ topics: [s.topic], count: 10, adaptive: true, source: 'skill' }, b), 'quiet')))));
    el.append(list);
    if (!readOnly) el.append(h('div', { class: 'rs-row', style: 'margin-top: 18px' }, btn(`Practise the top 3 · ≈ +${n(g.top3.gain)}`, b => drill({ topics: g.top3.topics, count: 12, adaptive: true, source: 'gain' }, b), 'pill sm')));
  }

  /* ------------------------------------------------------------ totals (2.4, SR22) */
  function drawTotals() {
    const el = $('totals');
    el.replaceChildren();
    const s = ST || {};
    el.hidden = !s.answered;                        // a new student has no totals yet (decision 7: no zeros)
    if (el.hidden) return;
    const box = h('div', { class: 'stats' });
    const t = s.tests || {};
    const testsN = (t.mock || 0) + (t.module || 0) + (t.diagnostic || 0);
    const tiles = [
      { label: 'Questions', value: s.answered || 0, sub: 'all time' },
      s.answered && { label: 'Accuracy', value: `${Math.round((s.accuracy || 0) * 100)}%`, sub: s.recent_accuracy !== undefined ? `last 14 days ${Math.round(s.recent_accuracy * 100)}%` : 'all time' },
      s.minutes_total && { label: 'Study time', value: UI.dur(s.minutes_total), sub: s.minutes_week ? `this week ${UI.dur(s.minutes_week)}` : 'tests included' },
      testsN && { label: 'Tests', value: testsN, sub: [t.mock && plural(t.mock, 'section'), t.module && plural(t.module, 'module'), t.diagnostic && plural(t.diagnostic, 'diagnostic')].filter(Boolean).join(' · ') },
      s.streak && { label: 'Streak', value: `${n(s.streak)} ${s.streak === 1 ? 'day' : 'days'}`, sub: s.best_streak > s.streak ? `best ${n(s.best_streak)}` : 'your best' },
      s.traps && (s.traps.open || s.traps.closed) && { label: 'Mistakes', value: `${n(s.traps.open || 0)} open`, sub: s.traps.closed ? `${n(s.traps.closed)} fixed` : '', href: readOnly ? null : '/mistakes/' },
      s.types_met && s.types_met.met && { label: 'Question types met', value: `${n(s.types_met.met)} of ${n(s.types_met.total || s.types_met.of || 0)}`, sub: '', href: readOnly ? null : '/me/#atlas' },
      s.week && s.week.recovered_pts && { label: 'Recovered this week', value: rx.pts(s.week.recovered_pts), sub: s.week.closed ? `${plural(s.week.closed, 'mistake')} closed` : '' },
    ].filter(Boolean);
    tiles.forEach(x => { if (x.sub && String(x.value) && String(x.sub).endsWith(` ${x.value}`)) x.sub = ''; UI.tile(box, { ...x, countUp: false }); });
    box.style.setProperty('--cols', String(Math.min(4, tiles.length)));
    el.append(box);
  }

  /* ------------------------------------------------------------ the last 14 days */
  function drawDays() {
    const el = $('days');
    const days = (ST && ST.days14) || [];
    if (!days.length) { el.hidden = true; return; }
    const q = days.reduce((a, d) => a + (d.questions || 0), 0);
    if (!q && !(ST && ST.answered)) { el.hidden = true; return; }
    head(el, { k: 'Last 14 days', title: q ? `${plural(q, 'question')} in the last two weeks` : 'Nothing in the last two weeks yet' });
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
    head(el, { k: 'Why you miss', title: `${plural(w.total, 'miss', 'misses')} in the last ${n(w.days || 14)} days, by cause` });
    UI.stackBar(el, keys.map(k => ({ key: k, label: (rx.CAUSE[k] || { label: cap(k) }).label, value: by[k] })), { label: 'Misses by cause', noun: 'misses', format: v => n(v), legend: keys.length > 1 ? 'auto' : false });
  }

  /* ------------------------------------------------------------ difficulty and format (2.5) */
  function drawSplit() {
    const el = $('split');
    el.hidden = true;
    const d = (ST && ST.by_difficulty) || [], f = (ST && ST.by_format) || [];
    if (!d.some(r => r.answered)) return;
    head(el, { k: 'Difficulty and format', title: 'Where the points leak, all time' });
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
    head(el, { k: 'Domains across sittings', title: 'Which domain is moving', tip: 'A section is one full SAT Math section: two modules, 44 questions. A module is one half of it (22 questions). Each cell is how many you got right in that domain; ▲ ▼ show the change from the sitting before.' });
    const doms = DOMAIN_ORDER.filter(d => cols.some(c => (c.domains || []).some(x => x.domain === d)));
    const old = i => (cols.length - i > 3 ? 'old' : null);
    const sess = new Map(((HIST && HIST.sessions) || []).map(x => [x.id, x]));
    const kindOf = id => (sess.get(id) || {}).kind;
    const colName = (c, i) => { const k = kindOf(c.id); return `${k === 'module' ? 'Module' : k === 'diagnostic' ? 'Diagnostic' : 'Full section'} #${c.seq || i + 1}`; };
    const colTip = c => { const k = kindOf(c.id); return k === 'module' ? 'One module: 22 questions' : k === 'diagnostic' ? 'The diagnostic: 20 questions' : 'A full section: two modules, 44 questions'; };
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
        const arrow = prev === null ? '' : p > prev + 0.001 ? ' ▲' : p < prev - 0.001 ? ' ▼' : '';
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
  let shown = 5, cards = [], selected = [];
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
    head(el, { k: 'Sittings', title: 'Every sitting' });
    const prog = ((HIST && HIST.in_progress) || []).filter(x => !readOnly);
    if (!all.length && !prog.length) {
      el.hidden = true;                             // nothing finished: no empty card
      return;
    }
    const tools = h('div', { class: 'rs-row' });
    const segOpts = [['all', 'All'], ['tests', 'Tests'], ['practice', 'Practice'], ['challenge', 'Challenge']].filter(([k]) => k === 'all' || counts[k] || SITQ.set === k).map(([value, label]) => ({ value, label, n: counts[value] }));
    const seg = UI.seg(null, segOpts, { value: SITQ.set, label: 'Which sittings', onChange: v => { SITQ.set = v; SITQ.kind = ''; shown = 5; writeQ(); drawSittings(); } });
    tools.append(seg.el);
    if (SITQ.set === 'tests') {
      const ks = [...new Set(all.filter(s => setOf(s) === 'tests').map(s => s.kind))];
      if (ks.length > 1) {
        const sel = h('select', { class: 'field sm', 'aria-label': 'Kind of test' }, h('option', { value: '', text: 'All tests' }), ks.map(k => h('option', { value: k, text: UI.KIND[k] || cap(k), selected: SITQ.kind === k ? '' : null })));
        sel.addEventListener('change', () => { SITQ.kind = sel.value; shown = 5; writeQ(); drawSittings(); });
        tools.append(sel);
      }
    }
    if (all.some(s => s.open)) {
      const oc = h('button', { type: 'button', class: 'chip', 'aria-pressed': String(SITQ.open), text: 'Has open mistakes' });
      oc.addEventListener('click', () => { SITQ.open = !SITQ.open; shown = 5; writeQ(); drawSittings(); });
      tools.append(oc);
    }
    const sorts = [['newest', 'Newest'], ['oldest', 'Oldest'], ['highest', 'Highest'], ['lowest', 'Lowest'], all.some(s => s.recovery) && ['points_open', 'Most points still open']].filter(Boolean);
    const so = h('select', { class: 'field sm', 'aria-label': 'Sort sittings' }, sorts.map(([v, l]) => h('option', { value: v, text: l, selected: SITQ.sort === v ? '' : null })));
    so.addEventListener('change', () => { SITQ.sort = so.value; writeQ(); drawSittings(); });
    tools.append(so);
    el.querySelector('.card-head').append(h('div', { class: 'rs-headr' }, tools));
    if (prog.length) {
      const g = h('div', { class: 'rs-group' }, h('h3', { text: 'In progress' }));
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
    if (!page.length) list.append(h('p', { class: 'rs-helper', text: 'No sittings match.' }));
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
          list.append(h('h3', { class: 'rs-dom-h' }, diff === 0 ? 'This week' : diff === 1 ? 'Last week' : `${UI.date(w)}–${UI.date(end)}`,
            h('span', { class: 'meta', text: ` · ${plural(inWeek.length, 'sitting')}${qn ? ` · ${plural(qn, 'question')}` : ''}` })));
        }
      }
      cards.push(UI.sittingCard(list, s, { share: readOnly, shareToken: SHARE || null, onSelect: pick }));
    });
    el.append(list);
    if (rows.length > shown) {
      el.append(h('div', { class: 'rs-row' }, h('span', { class: 'meta', text: `Showing ${n(shown)} of ${n(rows.length)}` }),
        btn(`Show ${n(Math.min(5, rows.length - shown))} more`, () => { shown += 5; drawSittings(); })));
    }
  }
  function pick(row, on) {
    selected = selected.filter(r => r.id !== row.id);
    if (on) selected.push(row);
    if (selected.length > 2) { const drop = selected.shift(); const c = cards.find(x => x.row.id === drop.id); if (c) c.select(false); }
    const bar = $('cmpbar');
    bar.hidden = selected.length < 2;
    if (bar.hidden) return;
    const [a, b] = selected.slice().sort((x, y) => String(y.finished).localeCompare(String(x.finished)));
    bar.replaceChildren(h('span', { text: `Compare ${UI.KIND.label(a)}${a.seq ? ` #${a.seq}` : ''} with ${UI.KIND.label(b)}${b.seq ? ` #${b.seq}` : ''}` }),
      h('a', { class: 'pill sm', href: `/results/report/?id=${encodeURIComponent(a.id)}&vs=${encodeURIComponent(b.id)}`, text: 'Compare' }),
      btn('Clear', () => { cards.forEach(c => { if (c.selected) c.select(false); }); selected = []; bar.hidden = true; }, 'quiet'));
  }

  /* ------------------------------------------------------------ top misconceptions (2.8) */
  function drawTraps() {
    const el = $('traps');
    const list = (ST && ST.top_traps) || [];
    if (!list.length) {
      if (ST && ST.answered) { head(el, { k: 'Top misconceptions', title: 'No mistakes yet' }); el.append(h('p', { class: 'rs-helper', text: 'Every miss you make lands here with its name.' })); }
      else el.hidden = true;
      return;
    }
    const open = (ST.traps || {}).open || 0;
    let view = 'open';   // the ones still open lead; "All" adds the fixed ones
    const tg = UI.seg(null, [{ value: 'open', label: 'Not fixed' }, { value: 'all', label: 'All' }], { value: view, label: 'Which mistakes', onChange: v => { view = v; drawList(); } });
    head(el, { k: 'Top misconceptions', title: 'The mistakes you make most', right: [tg.el, ...(readOnly ? [] : [open ? btn(`Fix all open · ${n(open)}`, b => drill({ mistakes: true, source: 'fix' }, b), 'pill sm') : null] )] });
    const box = h('div');
    el.append(box);
    function drawList() {
      box.replaceChildren();
      const rows = list.filter(t => view === 'all' || !t.closed).slice(0, 10);
      if (!rows.length) { box.append(h('p', { class: 'rs-helper', text: 'Nothing open: every mistake here is fixed.' })); return; }
      rows.forEach(t => {
        const st = t.closed ? h('span', { class: 'st', text: `✓ Fixed ${UI.date(t.closed)}` }) : h('span', { class: 'st open', text: `Open · ${plural(t.owed || 2, 'correct answer')} to close` });
        box.append(h('div', { class: 'rs-trap' }, glyph(t.topic) || h('span'), h('div', {}, h('h4', { text: cap(t.label) }),
          h('p', { class: 'meta', text: [topicName(t.topic), `×${n(t.hits)}`].join(' · ') }), st),
          readOnly || t.closed ? h('span') : h('div', { class: 'rs-row' }, btn('Fix', b => drill({ pool: 'redo', templates: [t.template], topics: [t.topic], source: 'mistakes' }, b)))));
      });
    }
    drawList();
    if (!readOnly) el.append(h('div', { style: 'display: flex; justify-content: flex-end; margin-top: 8px' }, h('a', { class: 'quiet', href: '/mistakes/', text: 'All mistakes →' })));   // bottom right
  }

  /* ------------------------------------------------------------ skills (2.7): a tap opens its stats, and Practise starts that skill only */
  function drawSkills() {
    const el = $('skills');
    const topics = ((MAP && MAP.topics) || []).filter(t => (t.subject || 'math') === 'math');
    head(el, { k: 'Skills', title: 'Every skill' });
    if (!topics.length) { el.hidden = true; return; }     // no skills yet: no empty card
    let sort = LS.get('satf.results.skills', 'domain');
    const sel = h('select', { class: 'field sm', 'aria-label': 'Sort skills' }, [['domain', 'By domain'], ['weak', 'Weakest first'], ['open', 'Most open mistakes'], ['least', 'Least practised'], ['recent', 'Least recent']]
      .map(([v, l]) => h('option', { value: v, text: l, selected: sort === v ? '' : null })));
    sel.addEventListener('change', () => { sort = sel.value; LS.set('satf.results.skills', sort); draw(); });
    el.querySelector('.card-head').append(h('div', { class: 'rs-headr' }, sel));
    const box = h('div', { class: 'rs-skills' });
    el.append(box);
    const tile = t => {
      const open = (t.traps || []).length;
      const word = UI.masteryWord ? UI.masteryWord(t.mastery, t.answered) : '';
      const b = h('button', { type: 'button', class: 'rs-skill', 'aria-label': `${topicName(t.topic, t.name)}: ${t.answered ? `${n(t.answered)} answered, ${Math.round((t.accuracy || 0) * 100)}%` : 'not started'}. Open its stats.` },
        h('b', {}, glyph(t.topic), topicName(t.topic, t.name)),
        t.answered ? h('div', { class: 'skill-m' }, h('span', { class: 'mbar' }, h('i', { style: `--m: ${Math.max(0, Math.min(1, t.mastery || 0))}` })), h('span', { class: 'skill-word', text: word })) : null,
        t.answered ? h('span', { class: 'meta', text: `${n(t.answered)} answered · ${Math.round((t.accuracy || 0) * 100)}%` }) : null,
        open ? h('span', { class: 'badge n', text: `${n(open)} open` }) : null);
      b.addEventListener('click', () => UI.skillPanel(t.topic, { share: SHARE || null, fallback: { topic: t.topic, domain: t.domain, mastery: t.mastery, answered: t.answered, right: Math.round((t.accuracy || 0) * (t.answered || 0)) } }));
      return b;
    };
    function draw() {
      box.replaceChildren();
      const cmp = { weak: (a, b) => (a.answered ? a.mastery : 2) - (b.answered ? b.mastery : 2), open: (a, b) => (b.traps || []).length - (a.traps || []).length,
        least: (a, b) => (a.answered || 0) - (b.answered || 0), recent: (a, b) => String(a.last || '').localeCompare(String(b.last || '')) }[sort];
      if (!cmp) {
        DOMAIN_ORDER.forEach(d => {
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

  load();
})();
