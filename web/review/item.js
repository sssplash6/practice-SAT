/* ============================================================================
   SAT Freshman -- one Review item, shared by the hub (/review/) and the walk (/review/walk/):
   GET /api/review/item's answer turned into a UI.review item (runner.js's items contract).
   window.ReviewItem = {toItem(d, row, tab, strip), srcWord(source), sittingHref(kind, sid)}
   ========================================================================== */
(() => {
  'use strict';
  const cap = s => (s ? s[0].toUpperCase() + s.slice(1) : '');
  const day = d => (d ? UI.date(d, 'short') : '');
  const LET = 'ABCDE';
  const SRC = { practice: 'Practice', section: 'Section', module: 'Module', diagnostic: 'Diagnostic', challenge: 'Challenge', qotd: 'Question of the day',
    review: 'Review', shared: 'Shared set', worksheet: 'Worksheet', due: 'Today’s review', outside: 'Logged by you', test: 'Custom test', mock: 'Section' };
  const srcWord = s => SRC[s] || cap(s || '');
  function sittingHref(kind, sid) {
    if (!sid || sid === 'none') return null;
    if (kind === 'drill' || kind === 'challenge') return `/practice/session/?id=${encodeURIComponent(sid)}`;
    return `/results/report/?id=${encodeURIComponent(sid)}`;
  }
  const EVENT = { open: 'opened', miss: 'missed', pip: 'clean ✓', fixed: 'Fixed', check_ok: 'Check-in ✓', relapse: 'Relapsed', dismissed: 'Dismissed', restored: 'Restored', reopened: 'Reopened', discarded: 'Discarded' };
  function toItem(d, r, tab, strip) {
    const q = Object.assign({}, d.question || {}, { template: d.template, seed: d.seed, topic: d.topic, skill: (d.question && d.question.skill) || r.skill, name: r.skill || (d.question && d.question.name) });
    delete q.level;
    const last = (d.attempts || [])[0] || null;
    const mc = q.type !== 'spr';
    const given = last ? (mc && /^\d+$/.test(String(last.given)) ? +last.given : last.given) : null;
    const reveal = d.answer !== null && d.answer !== undefined;
    const fb = reveal ? {
      correct: last ? !!last.correct : null, given, answer: d.answer, answer_index: mc && /^[A-E]$/.test(String(d.answer)) ? LET.indexOf(d.answer) : null,
      reasons: d.reasons, rationale: d.rationale, mistake: last && !last.correct && last.reason ? cap(last.reason) : null, steps: d.steps || undefined,
    } : (last ? { given } : null);
    const res = last ? ({ right: 'correct', wrong: 'incorrect', repaired: 'repaired', repeat: 'repeat', mixed: 'mixed' }[last.result] || (last.correct ? 'correct' : 'incorrect')) : 'unanswered';
    const traps = d.traps || [];
    const tied = r.trap_id || (tab === 'redo' || tab === 'fixed' ? r.id : null);
    const trap = traps.find(t => (tied && t.id === tied) || (r.norm && t.norm === r.norm)) || (tied ? null : traps[0]) || null;
    let mistake = null;
    if (trap) mistake = { status: r.stuck ? 'stuck' : trap.status, owed: trap.owed, of: trap.norm === '~unsure' ? 1 : 2, hits: trap.hits, label: trap.label, relapses: trap.relapses, trap_id: trap.id };
    else if ((tab === 'fixed' && r.closed_how === 'fixed') || (tab === 'due' && r.kind === 'check')) mistake = { status: 'fixed', fixed_at: r.closed || r.since, label: r.label };
    const src = last ? last.source : r.source;
    const sitting = last && last.session ? { label: `${srcWord(src)} · ${day(last.at)}`, href: src === 'review' ? null : sittingHref(['section', 'module', 'diagnostic', 'test'].includes(src) ? 'test' : 'drill', last.session) } : null;
    const story0 = (d.story || []).length > 7 ? [d.story[0], ...d.story.slice(-5)] : (d.story || []);   // the opening and the latest five
    const story = story0.map(n => ({ at: n.at, event: n.event, source: srcWord(n.source), result: n.result, attempt: n.attempt,
      label: [n.pick ? `picked ${n.pick}` : null, EVENT[n.event] || n.event].filter(Boolean).join(' · ') }));
    return {
      q, fb, status: res, _row: r, strip,
      flag: !!d.flagged, saved: !!d.saved, note: d.note, marks: d.marks, rule: d.rule, path: d.path,
      tries: (d.tries || []).map(t => ({ given_label: mc && /^\d+$/.test(String(t.given)) ? LET[+t.given] : t.given, correct: !!t.correct, ms: t.ms })),
      story: story.length > 1 || (story.length && trap) ? story : null,
      summary: d.summary && d.summary.days_to_fix !== null && d.summary.days_to_fix !== undefined ? d.summary : null,
      elsewhere: (d.elsewhere || []).map(x => ({ skill: cap(x.skill) })), new: !!d.new && !d._revealedHere, diag_choices: d.new ? d.diag_choices : null,
      attempt_id: last ? last.id : null, trap_id: trap ? trap.id : null, norm: trap ? trap.norm : r.norm, session: last ? last.session : null, qid: last ? last.qid : null,
      ms: last ? last.ms : null, budget_ms: d.budget_ms, worth: r.pts !== undefined && r.pts !== null ? r.pts : d.pts, sitting, mistake,
      cause: last && !last.correct ? { cause: r.cause || last.diag_kind || 'trap', auto: !last.diag } : null,
      family: d.family ? { seen: d.family.seen, right: d.family.right, repaired: d.family.repaired, recent: (d.family.recent || []).map(x => ({ result: x })) } : null,
      blank: res === 'unanswered',
    };
  }
  window.ReviewItem = { toItem, srcWord, sittingHref };
})();
