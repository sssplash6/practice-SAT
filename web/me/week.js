/* ============================================================================
   SAT Freshman -- your week (shell-me U14): last week as receipts, and up to three
   goals for this one. GET /api/me/week, PUT /api/me/week/goals.

   UI.week({onSaved, extra}) -> sheet   opens it (Me › This week, whose study days ride in as extra; F2's UI.autoSheet can load
                                   this file and call it on the first clean load of a week)
   UI.weekTitle(goal)              "Fix the 4 open Circles mistakes"
   UI.weekStart(goal, button)      starts the goal's drill
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h;
  const N = n => UI.num(n);
  const pl = (n, one, many) => `${N(n)} ${n === 1 ? one : many || one + 's'}`;
  const tn = t => UI.topicName(t);

  function title(g) {
    const p = g.params || {}, n = g.target;
    switch (g.kind) {
      case 'fix_traps': return p.topic ? `Fix the ${N(n)} open ${tn(p.topic)} mistakes` : `Fix ${pl(n, 'open mistake')}`;
      case 'pass_checks': return `Pass all ${pl(n, 'check-in')} due this week`;
      case 'reach_word': return `Get ${tn(p.topic)} to ${p.word || 'Strong'}`;
      case 'take_module': return p.day ? `Take a module on ${p.day}` : 'Take a module';
      case 'habit_cap': return `Keep ${String(p.habit || 'a habit').replace(/_/g, ' ')} to ${pl(n, 'miss', 'misses')} or fewer`;
      case 'minutes': return `Study ${UI.dur(n)} this week`;
      default: return g.title || 'A goal';
    }
  }
  function body(g) {
    const p = g.params || {};
    switch (g.kind) {
      case 'fix_traps': return { pool: 'redo', topics: p.topic ? [p.topic] : undefined, source: 'mistakes' };
      case 'pass_checks': return { pool: 'checks', source: 'mistakes' };
      case 'reach_word': return { topics: [p.topic], count: 10, adaptive: true, source: 'skill' };
      case 'habit_cap': return { source: 'habit', habit: p.habit, count: 8 };
      case 'take_module': return null;
      default: return { source: 'coach', count: 10 };
    }
  }
  async function start(g, b) {
    let x = body(g);
    // a goal on an R&W skill opens an R&W set
    if (x && g.params && UI.subjectOf(g.params.topic) === 'rw') x = { ...x, subject: 'rw' };
    if (!x) { location.href = '/tests/'; return; }
    if (b) b.setAttribute('aria-busy', 'true');
    try { await UI.start({ start: { body: x } }); }
    catch (e) { if (!e || !e.offline) UI.toast('Couldn’t start that. Try again.'); }
    finally { if (b) b.removeAttribute('aria-busy'); }
  }
  // "2026-W40" -> the Monday of that ISO week
  function monday(week) {
    const [y, w] = week.split('-W').map(Number);
    const jan4 = new Date(y, 0, 4);
    const m = new Date(jan4);
    m.setDate(jan4.getDate() - ((jan4.getDay() + 6) % 7) + (w - 1) * 7);
    return m;
  }
  function range(week) {
    try {
      const a = monday(week), b = new Date(a); b.setDate(a.getDate() + 6);
      const mon = d => d.toLocaleDateString('en-US', { month: 'short' });
      return mon(a) === mon(b) ? `${mon(a)} ${a.getDate()}–${b.getDate()}` : `${mon(a)} ${a.getDate()} – ${mon(b)} ${b.getDate()}`;
    } catch (_) { return 'this week'; }
  }
  const key = g => `${g.kind}:${JSON.stringify(g.params || {})}`;

  function open(o = {}) {
    let data = null;
    const chosen = new Map();
    return UI.sheet({ title: 'Your week', size: 'm',
      body: (b, sheet) => {
        b.append(UI.skel(null, 'card:4'));
        UI.api('/me/week').then(w => {
          data = w;
          sheet.setTitle(`Your week, ${range(w.week)}`);
          (w.goals || []).forEach(g => chosen.set(key(g), g));
          const r = w.receipts || {};
          const receipts = [r.answered && `${pl(r.answered, 'question')} answered`,
            r.answered && r.accuracy !== null && r.accuracy !== undefined && `${r.accuracy}% right on the first try`,
            r.minutes && `${UI.dur(r.minutes)} of study`, r.fixed && `${pl(r.fixed, 'mistake')} fixed`].filter(Boolean);
          const pick = h('div', { class: 'gap tight wk-pick' });
          const note = h('p', { class: 'help', role: 'status' });
          const options = [...(w.goals || []), ...(w.suggestions || []).filter(s => !chosen.has(key(s)))];
          // each goal is a row-shaped toggle (.choice-row with its drawn checkbox showing, me.css .wk-pick: pick up to three)
          const draw = () => {
            pick.replaceChildren(...options.map(g => {
              const on = chosen.has(key(g)), full = !on && chosen.size >= 3;
              const box = h('input', { type: 'checkbox', checked: on || null, disabled: full ? '' : null });
              box.addEventListener('change', () => { if (box.checked) chosen.set(key(g), g); else chosen.delete(key(g)); draw(); });
              const meta = [g.why && g.why.replace(/_/g, ' '), g.minutes && `about ${UI.dur(g.minutes)}`].filter(Boolean).join(' · ');
              return h('label', { class: 'choice-row', 'aria-disabled': full ? 'true' : null }, box,
                h('span', { style: 'display: grid; gap: 2px; padding-block: 4px' }, h('span', { text: title(g) }), meta ? h('span', { class: 'meta', text: meta }) : null));
            }));
            note.textContent = chosen.size >= 3 ? 'Three is the most a week holds. Untick one to swap it.' : '';
          };
          draw();
          b.replaceChildren(
            // the shell's welcome-back line rides at the top when it opens this sheet for a returning student (F2's autoSheet)
            o.welcome || '',
            h('h3', { class: 'sub-h', text: 'Last week' }),
            receipts.length ? h('ul', { class: 'gap', style: 'gap: 4px; padding-left: 18px; margin: 0' }, receipts.map(t => h('li', { text: t })))
              : h('p', { class: 'soft', text: 'Nothing last week. This week starts fresh.' }),
            (r.new_mistakes || []).length ? h('p', { class: 'help', text: `New mistakes: ${r.new_mistakes.join(' · ')}` }) : '',
            // Profile hands in this week's study days and the weeks met (they left its This week card for this sheet)
            ...(o.extra || []).filter(Boolean),
            h('h3', { class: 'sub-h', text: 'This week: pick up to three' }), pick, note,
            // the plan's own week: busy days, short days, a focus swap (Plan › Shape this week)
            h('p', { class: 'help' }, h('a', { class: 'link', href: '/plan/?shape=1', text: 'Shape this week’s study days in your plan' })));
        }, () => b.replaceChildren(UI.cardError(null, () => { sheet.close(); open(o); })));
      },
      actions: [{ label: 'Not now', quiet: true },
        { label: 'Save my goals', primary: true, onClick: async () => {
          if (!data) return false;
          const goals = [...chosen.values()].slice(0, 3).map(g => ({ kind: g.kind, params: g.params || {}, target: g.target }));
          const r = await UI.api('/me/week/goals', { method: 'PUT', body: { week: data.week, goals } });
          UI.toast(goals.length ? `${pl(goals.length, 'goal')} set for this week` : 'Goals cleared');
          const next = { ...data, goals: r.goals };
          if (o.onSaved) o.onSaved(next);
          return next;
        } }] });
  }

  Object.assign(UI, { week: open, weekTitle: title, weekStart: start });
})();
