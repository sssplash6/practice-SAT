/* ============================================================================
   SAT Freshman -- a full SAT's result, /results/full/?id=<id> (spec/full-sat DESIGN 2)

   One GET /api/full/{id} (id = either part's sitting id): the total first (400-1600, the server's range, 20
   wide), then Reading and Writing and Math in College Board's order, each with its range and its report, then
   what to do next. A full SAT still running says where it stands and resumes. ?fresh=1 (the hand-in) counts the
   total up once.
   ========================================================================== */
(() => {
  'use strict';
  const UI = window.UI;
  if (!UI || !UI.rx) return;
  const { h, rx } = UI;
  const $ = id => document.getElementById(id);
  const P = new URLSearchParams(location.search);
  const ID = P.get('id') || '';
  const FRESH = P.get('fresh') === '1';
  if (FRESH) { const u = new URL(location.href); u.searchParams.delete('fresh'); history.replaceState(history.state, '', u); }
  UI.shell('report');

  const n = x => UI.num(x);
  const band = e => (e && e.low !== undefined && e.low !== null ? `${e.low}–${e.high}` : '');
  const mid = e => (e ? e.mid ?? (e.low + e.high) / 2 : null);
  const ord = v => { const x = Math.round(v); const s = ['th', 'st', 'nd', 'rd'], m = x % 100; return x + (s[(m - 20) % 10] || s[m] || s[0]); };
  const btn = (text, cls, onClick) => { const b = h('button', { type: 'button', class: cls, text }); b.addEventListener('click', () => onClick(b)); return b; };
  const report = s => s.href || `/results/report/?id=${encodeURIComponent(s.id)}`;
  const lobby = id => `/test/?s=${encodeURIComponent(id)}`;

  async function load() {
    if (!ID) return gone();
    let F;
    try { F = await UI.api(`/full/${encodeURIComponent(ID)}`, { quiet: true }); }
    catch (e) { return e && e.status === 404 ? gone() : fail(e); }
    $('main').removeAttribute('aria-busy');
    document.title = `Full SAT${F.number ? ` #${F.number}` : ''} · SAT Freshman`;
    drawHead(F); drawTotal(F); drawSections(F); drawNext(F);
    UI.shell({ page: 'report', ownPrimary: !!$('root').querySelector('.pill') });
  }
  function gone() {
    $('main').removeAttribute('aria-busy');
    $('root').replaceChildren(h('section', { class: 'card' }, h('h1', { class: 'h2', text: 'That full SAT does not exist.' }),
      h('div', { class: 'fs-acts' }, h('a', { class: 'btn', href: '/results/', text: 'All results' }))));
  }
  function fail(e) {
    $('main').removeAttribute('aria-busy');
    const box = h('section', { class: 'card', role: 'alert' });
    $('root').replaceChildren(box);
    UI.cardError(box, () => location.reload(), e && e.status === 403 ? 'This result is private to the student who sat it.' : 'Couldn’t load this result.');
  }

  /* "Results / Full SAT #2", then one meta line: the day, the minutes, and only what differs from a standard sitting */
  function drawHead(F) {
    const secs = F.sections || [];
    const ms = secs.reduce((a, s) => a + (s.ms || 0), 0) || F.ms || 0;
    const bits = [F.finished || F.started ? UI.date(F.finished || F.started, 'long') : null, ms ? `${Math.round(ms / 60000)} min` : null,
      F.status === 'done' ? null : 'In progress'];
    const meta = h('p', { class: 'fs-meta' }, bits.filter(Boolean).map(t => h('span', { text: t })));
    if (F.status === 'done' && F.ranked === false) meta.append(h('span', { class: 'badge soft', text: `Unranked${F.unranked_why ? ` · ${F.unranked_why}` : ''}` }));
    $('head').replaceChildren(h('div', { class: 'fs-crumb' }, h('a', { href: '/results/', text: 'Results' }), h('span', { 'aria-hidden': 'true', text: '/' }),
      h('h1', { class: 'h1', text: `Full SAT${F.number ? ` #${F.number}` : ''}` })), meta);
  }

  /* the total: the hero figure, its place on 400-1600, the change on the last full SAT and the national percentile */
  function drawTotal(F) {
    const el = $('total');
    el.replaceChildren();
    const T = F.total;
    if (!T || T.low === undefined || T.low === null) {
      // not both sections yet: where the test stands, and the way back in
      const math = (F.sections || []).find(s => s.subject === 'math') || {};
      const rw = (F.sections || []).find(s => s.subject === 'rw') || {};
      const [line, href, label] = F.status === 'rw' ? ['Reading and Writing is under way. The total comes once Math is handed in.', rw.id ? lobby(rw.id) : '/tests/#live', 'Resume']
        : F.status === 'break' || F.status === 'math' ? ['Reading and Writing is in. Math is next; the total comes once it is handed in.', math.id ? lobby(math.id) : '/tests/#live', F.status === 'break' ? 'Go to Math' : 'Resume']
          : ['This full SAT stopped after Reading and Writing, so it has no total. Its section stands on its own.', null, null];
      el.append(h('p', { class: 'k', text: 'Total' }), h('h2', { class: 'h2', text: 'No total yet' }), h('p', { class: 'fs-line', 'data-nofold': '', text: line }));
      if (href) el.append(h('div', { class: 'fs-acts' }, h('a', { class: 'pill', href, text: label })));
      return;
    }
    const fig = h('span', { text: band(T) });
    const P0 = F.previous && F.previous.low ? F.previous : null;
    const d = P0 ? Math.round((mid(T) - mid(P0)) / 10) * 10 : null;   // on tens
    const chip = P0 ? h('span', { class: 'badge lg' + (d > 0 ? '' : ' soft'), text: `${d > 0 ? '+' : d < 0 ? '−' : '±'}${n(Math.abs(d))} vs your last full SAT` }) : null;
    el.append(h('p', { class: 'k', 'aria-hidden': 'true', text: 'Total' }),
      h('div', { class: 'fs-figrow' }, h('h2', { class: 'hero-num' }, h('span', { class: 'sr', text: 'Total ' }), fig, h('small', { text: '/1600' })), chip));
    const sc = h('div');
    el.append(sc);
    UI.scale(sc, { band: T, previous: P0 || undefined, min: 400, max: 1600, bandLabel: 'total', animate: FRESH && !(UI.reduced && UI.reduced()) });
    const nat = F.national;
    if (nat && nat.low_pct !== undefined) {
      const pct = ord(nat.low_pct) === ord(nat.high_pct) ? ord(nat.low_pct) : `${ord(nat.low_pct)}–${ord(nat.high_pct)}`;
      el.append(h('p', { class: 'fs-line' }, 'About the ', h('b', { text: pct }), ' percentile nationally ',
        UI.why(`Your total ${band(T)} sits at about this percentile of SAT takers (College Board${nat.year ? `, ${nat.year}` : ''}). It is an estimate from our questions, shown to ±10 points; it is not a College Board score.`, { about: 'the percentile' })));
    }
    // the hand-in moment counts the figure up once, from the last full SAT or the scale's floor
    if (FRESH && UI.roll && !(UI.reduced && UI.reduced())) { const to = fig.textContent; fig.textContent = P0 ? band(P0) : '400–420'; UI.roll(fig, to); }
  }

  /* the sections, R&W then Math: each one's range on 200-800, its count and route, its report */
  function drawSections(F) {
    const el = $('sections');
    const secs = (F.sections || []).filter(s => s.id || s.status);
    el.hidden = !secs.length;
    if (!secs.length) return;
    el.replaceChildren(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'Sections' })));
    secs.forEach(s => {
      const name = UI.subjectLabel(s.subject);
      const done = !!(s.estimate && s.estimate.low);
      const row = h('div', { class: 'fs-sec' });
      const bits = [s.asked ? `${n(s.right || 0)} of ${n(s.asked)} right` : null, s.route === 'upper' ? 'harder module 2' : s.route === 'lower' ? 'easier module 2' : null,
        s.estimate && s.estimate.capped ? 'capped at 580 by the easier route' : null].filter(Boolean);
      // the range is the row's one figure (on 200-800, said once in its label); the total's scale above is the page's one scale
      row.append(h('div', {}, h('h3', { text: name }), h('p', { class: 'meta', text: done ? bits.join(' · ') : s.status === 'not_begun' || !s.id ? 'Not begun' : 'Under way' })),
        h('span', { class: 'fs-band', 'aria-label': done ? `${name} ${band(s.estimate)} of 800` : null, text: done ? band(s.estimate) : '' }));
      const acts = h('div', { class: 'fs-acts' });
      if (done) acts.append(h('a', { class: 'btn sm', href: report(s), text: `${UI.subjectLabel(s.subject, true)} report` }));
      if (s.ranked === false && s.unranked_why) acts.append(h('span', { class: 'badge soft', text: `Unranked · ${s.unranked_why}` }));
      if (acts.childNodes.length) row.append(acts);
      el.append(row);
    });
  }

  /* what to do next: each section's misses to fix (most first), then the next full SAT */
  function drawNext(F) {
    const el = $('next');
    const secs = (F.sections || []).filter(s => s.estimate && s.estimate.low && s.asked);
    if (F.status !== 'done' || !secs.length) { el.hidden = true; return; }
    el.hidden = false;
    el.replaceChildren(h('div', { class: 'card-head' }, h('h2', { class: 'h2', text: 'What to do next' })));
    const row = (title, meta, action) => h('div', { class: 'fs-row' }, h('div', {}, h('h3', { text: title }), meta ? h('p', { class: 'meta', text: meta }) : null), action);
    const missed = s => (s.asked || 0) - (s.right || 0);
    secs.slice().sort((a, b) => missed(b) - missed(a)).forEach(s => {
      if (!missed(s)) return;
      el.append(row(`Fix your ${UI.subjectLabel(s.subject)} misses`, `${n(missed(s))} wrong or blank`,
        btn('Fix', 'btn sm', b => rx.drill({ from_session: s.id, scope: 'misses', source: 'fix' }, b))));
    });
    el.append(row('Another full SAT', 'Best a week or more from this one, once the misses are fixed', btn('Start', 'btn sm', async b => {
      b.setAttribute('aria-busy', 'true');
      try { const r = await UI.api('/mock/new', { method: 'POST', body: { kind: 'full' } }); location.href = lobby(r.id); }
      catch (_) { b.removeAttribute('aria-busy'); UI.toast('Couldn’t build the test. Try again.'); }
    })));
  }

  load();
})();
