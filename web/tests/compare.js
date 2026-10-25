/* ============================================================================
   SAT Freshman -- compare two sittings (tests.md X18; §3.1 item 23)

   TestsCompare.open([a, b], {rows, start(body, btn), drill(body, btn)})   a 720px sheet, full height on a phone
     the facts side by side from the two sittings rows (band, modules, route and margin,
     time used, misses, blanks, pauses, conditions), then S6's
     GET /api/session/{a}/compare?with={b} -> {by: 'slot' | 'template', a, b, rows, summary}:
       slot      a twin, rematch or retake of the same root: M1 Q1 ... with a mark per side,
                 "Fixed 5 · Still missed 2 · New 1 · Held 36 · +60", and each still-missed slot's
                 "Same trap both times" or "A different mistake"
       template  Missed both times, Fixed, New misses, each with Fix
     and the domains' bars side by side when the endpoint sends them.
   ========================================================================== */
(() => {
  const h = UI.h;
  const api = (p, o) => UI.api(p, o);
  const num = n => (UI.num ? UI.num(n) : String(n));
  const mmss = s => UI.mmss(Math.max(0, Math.round(s || 0)));
  const band = e => (e && e.low !== null && e.low !== undefined ? `${Math.round(e.low)}–${Math.round(e.high)}` : null);
  const name = r => `${r.kind_label || 'Sitting'}${r.number ? ` #${r.number}` : ''}`;
  const tag = r => (r.number ? `#${r.number}` : name(r));
  const MARK = { right: ['✓', 'right'], correct: ['✓', 'right'], wrong: ['✕', 'wrong'], incorrect: ['✕', 'wrong'], blank: ['–', 'blank'], unanswered: ['–', 'blank'] };
  const NONE = UI.NONE || '\u2013';   // the missing-value glyph, an en dash
  const DOMAIN = { algebra: 'Algebra', advanced: 'Advanced Math', psda: 'Problem-Solving and Data', geometry: 'Geometry and Trigonometry' };

  function facts(r) {
    const m = r.modules || [];
    const g = r.gate && r.gate.margin !== undefined && r.gate.margin !== null ? (r.gate.margin >= 0 ? ` · gate +${r.gate.margin}` : ` · gate ${r.gate.margin}`) : '';
    const route = r.route === 'upper' ? 'Harder module 2' : r.route === 'lower' ? 'Easier module 2' : m.length > 1 ? 'Adaptive' : NONE;
    const cond = r.conditions === undefined ? NONE : r.conditions === 'training' ? 'Training'
      : `Test-day${r.ranked === false ? ` · unranked${r.unranked_why ? ' (' + r.unranked_why + ')' : ''}` : r.ranked ? ' · ranked' : ''}`;
    return {
      when: r.started ? UI.date(r.started, 'short') : NONE,
      band: band(r.estimate) || (r.right !== null && r.right !== undefined && r.asked ? `${r.right}/${r.asked} · practice` : NONE),
      m1: m[0] ? `${m[0].right}/${m[0].asked}` : NONE,
      m2: m[1] ? `${m[1].right}/${m[1].asked}` : NONE,
      route: `${route}${g}`,
      time: r.ms ? `${r.timing === 'untimed' ? 'Untimed · ' : ''}${Math.round(r.ms / 60000)} min` : NONE,
      misses: String(r.misses || 0),
      blanks: String(r.blanks || 0),
      away: r.away_ms ? mmss(r.away_ms / 1000) : r.offline_ms ? `offline ${mmss(r.offline_ms / 1000)}` : NONE,
      pauses: r.pauses ? String(r.pauses) : NONE,
      cond,
    };
  }
  const LABELS = [['when', 'Date'], ['band', 'Band'], ['m1', 'Module 1'], ['m2', 'Module 2'], ['route', 'Route'], ['time', 'Time used'],
    ['misses', 'Wrong'], ['blanks', 'Blank'], ['away', 'Away'], ['pauses', 'Pauses'], ['cond', 'Conditions']];

  function open(ids, o = {}) {
    if (!UI.sheet || !ids || ids.length < 2) return null;
    const find = id => (o.rows || []).find(r => r.id === id) || { id, kind_label: 'Sitting' };
    // older first, so the right-hand column is the newer sitting
    const [a, b] = ids.slice(0, 2).map(find).sort((x, y) => String(x.started || '').localeCompare(String(y.started || '')));
    try { const u = new URL(location.href); u.searchParams.set('compare', `${a.id},${b.id}`); history.replaceState(history.state, '', u); } catch (_) {}
    return UI.sheet({ title: `Compare ${tag(a)} and ${tag(b)}`, size: 'l', className: 'cmp-sheet',
      onClose: () => { try { const u = new URL(location.href); u.searchParams.delete('compare'); history.replaceState(history.state, '', u); } catch (_) {} },
      body: bd => { fill(bd, a, b, o); } });
  }

  function fill(bd, a, b, o) {
    const fa = facts(a), fb = facts(b);
    const t = h('table', { class: 'table compact cmp-facts' },
      h('thead', {}, h('tr', {}, h('th', { scope: 'col', class: 'sr', text: 'Fact' }), h('th', { scope: 'col', text: `${name(a)}` }), h('th', { scope: 'col', text: `${name(b)}` }))),
      h('tbody', {}, LABELS.filter(([k]) => fa[k] !== NONE || fb[k] !== NONE).map(([k, l]) => h('tr', { class: fa[k] !== fb[k] && k !== 'when' ? 'diff' : null }, h('th', { scope: 'row', class: 'k', text: l }), h('td', { text: fa[k] }), h('td', { text: fb[k] })))));
    bd.append(h('div', { class: 'cmp-wrap' }, t));
    const more = h('div', { class: 'cmp-more', 'aria-busy': 'true' });
    bd.append(more);
    if (UI.skel) UI.skel(more, 'rows:3');
    api(`/session/${encodeURIComponent(a.id)}/compare?with=${encodeURIComponent(b.id)}`, { quiet: true }).then(d => {
      more.removeAttribute('aria-busy');
      more.replaceChildren();
      domains(more, d, a, b);
      if (d.by === 'slot') slots(more, d, a, b, o);
      else templates(more, d, a, b, o);
    }).catch(e => {
      more.removeAttribute('aria-busy');
      more.replaceChildren();
      if (e.status === 403) { more.append(h('p', { class: 'help', text: 'Only your own sittings can be compared.' })); return; }
      if (UI.cardError) UI.cardError(more, () => { bd.replaceChildren(); fill(bd, a, b, o); }, 'Couldn’t load the question-by-question comparison.');
    });
  }

  function domains(host, d, a, b) {
    const da = (d.a && d.a.domains) || null, db = (d.b && d.b.domains) || null;
    if (!da || !db) return;
    const keys = [...new Set([...Object.keys(da), ...Object.keys(db)])];
    const bar = x => { const s = x && x.asked ? x.right / x.asked : 0; return h('span', { class: 'cmp-bar', 'aria-hidden': 'true' }, h('i', { style: `width:${Math.round(s * 100)}%` })); };
    const txt = x => (x && x.asked ? `${x.right}/${x.asked}` : NONE);
    host.append(h('h3', { class: 'k', text: 'By domain' }), h('ul', { class: 'cmp-doms' }, keys.map(k => h('li', {},
      h('b', { text: DOMAIN[k] || k }),
      h('span', { class: 'cmp-dom' }, h('span', { text: `${tag(a)} ${txt(da[k])}` }), bar(da[k])),
      h('span', { class: 'cmp-dom' }, h('span', { text: `${tag(b)} ${txt(db[k])}` }), bar(db[k]))))));
  }

  function slots(host, d, a, b, o) {
    const s = d.summary || {};
    const parts = [['fixed', 'Fixed'], ['still', 'Still missed'], ['new', 'New'], ['held', 'Held']].filter(([k]) => s[k] !== undefined).map(([k, l]) => `${l} ${num(s[k])}`);
    if (s.pts) parts.push(`${s.pts > 0 ? '+' : '−'}${Math.abs(s.pts)}`);
    host.append(h('h3', { class: 'k', text: 'Slot by slot' }));
    if (parts.length) host.append(h('p', { class: 'cmp-sum', text: parts.join(' · ') }));
    const mark = v => { const m = MARK[v] || ['·', v || 'not asked']; return h('span', { class: `cmp-m ${m[1]}`, 'aria-label': m[1], text: m[0] }); };
    const rows = (d.rows || []);
    const table = h('table', { class: 'table compact cmp-slots' },
      h('thead', {}, h('tr', {}, h('th', { scope: 'col', text: 'Slot' }), h('th', { scope: 'col', text: 'Type' }), h('th', { scope: 'col', text: tag(a) }), h('th', { scope: 'col', text: tag(b) }), h('th', { scope: 'col', text: '' }))),
      h('tbody', {}, rows.map(r => h('tr', { class: r.a !== r.b ? 'diff' : null },
        h('td', { text: r.slot_label || r.slot || '' }),
        h('td', { text: r.topic_name || r.label || '' }),
        h('td', {}, mark(r.a)), h('td', {}, mark(r.b)),
        h('td', { class: 'meta', text: r.same_trap ? `Same trap both times: ${r.same_trap}` : r.still ? 'A different mistake' : '' })))));
    host.append(h('div', { class: 'cmp-wrap' }, table));
    const still = rows.filter(r => r.still || ((MARK[r.a] || [])[1] !== 'right' && (MARK[r.b] || [])[1] !== 'right'));
    if (still.length && o.drill) host.append(h('div', { class: 'cmp-acts' }, h('button', { type: 'button', class: 'btn sm', text: `Fix the ${still.length} still missed`,
      onclick: e => o.drill({ from_session: b.id, scope: 'misses', source: 'fix' }, e.currentTarget) })));
  }

  function templates(host, d, a, b, o) {
    const rows = d.rows || [];
    const groups = [['both', 'Missed both times'], ['fixed', 'Fixed'], ['new', 'New misses']];
    host.append(h('h3', { class: 'k', text: 'Question types' }));
    let any = false;
    groups.forEach(([k, label]) => {
      const list = rows.filter(r => r.group === k);
      if (!list.length) return;
      any = true;
      const sec = h('section', { class: 'cmp-group' }, h('div', { class: 'cmp-gh' }, h('b', { text: `${label} · ${list.length}` })));
      if (k !== 'fixed' && o.drill) {
        const templatesOf = list.map(r => r.template).filter(Boolean);
        if (templatesOf.length) sec.firstChild.append(h('button', { type: 'button', class: 'quiet', text: `Fix ${list.length}`,
          onclick: e => o.drill({ templates: templatesOf, count: Math.min(20, templatesOf.length * 2), source: 'fix' }, e.currentTarget) }));
      }
      sec.append(h('ul', { class: 'cmp-types' }, list.map(r => h('li', {}, h('span', { text: r.topic_name || r.label || '' }), r.trap ? h('span', { class: 'meta', text: r.trap }) : null))));
      host.append(sec);
    });
    if (!any) host.append(h('p', { class: 'help', text: 'No question type was missed in either sitting.' }));
  }

  window.TestsCompare = { open };
})();
