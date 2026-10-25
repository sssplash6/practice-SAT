// practice fixtures: the Today set plus /bank, /drill, /sets, /next, /drill/preview
const base = require(__dirname + '/fixtures.js');
module.exports = v => {
  const F = base(v);
  const ty = (t, n) => ({ template: t, name: n, about: 'about ' + n, formats: ['mcq', 'spr'], tiers: ['easy', 'medium'], state: 'met', traps: [] });
  const sk = (slug, name, extra) => Object.assign({ slug, name, short: name, answered: 12, mastery: .5, accuracy: .6, gain: 4, traps: [{ label: 'sign slip', template: slug + '.a' }], types: [ty(slug + '.a', name + ' A'), ty(slug + '.b', name + ' B')] }, extra || {});
  const bank = { domains: [
      { name: 'Algebra', weight: .35, answered: 20, right: 12, mastery: .5, gain: 9, skills: [sk('linear_equations', 'Linear equations'), sk('systems', 'Systems', { traps: [], gain: 0 })] },
      { name: 'Advanced Math', weight: .35, skills: [sk('quadratics', 'Quadratics', { answered: 0, traps: [] })] },
      { name: 'Problem-Solving', weight: .15, skills: [sk('percent', 'Percent')] },
      { name: 'Geometry', weight: .15, skills: [sk('circles', 'Circles', { traps: [] })] } ],
    counts: { mistakes: 4, saved: 12, marked: 2, review: 3, seen: { any: 40, missed: 6 } }, totals: { answered: 60 },
    coach: { topics: ['linear_equations'], count: 10, reasons: {} }, gains: { total: 30, range: '560-600' }, habits: [], forecast: [] };
  if (process.env.NEW) { bank.totals.answered = 0; bank.domains.forEach(d => { d.answered = 0; d.skills.forEach(s => { s.answered = 0; s.traps = []; }); }); bank.counts = { mistakes: 0, saved: 0, marked: 0, review: 0, seen: {} }; bank.gains = null; }
  return Object.assign({}, F, {
    '/bank': bank,
    '/drill/preview': { servable: true, count: 10, minutes: 15, pools: { new: 100, mistakes: 4, checks: 0, review: 3, untried: 20, seen: { any: 40 }, marked: 2, saved: 12 } },
    '/drill': process.env.QUICKQ ? ((u, o) => (o.method === 'POST' && !/\/next|\/answer|\/finish/.test(u.pathname) ? { id: 'q1', question: { id: 'x1', topic: 'circles', skill: 'Circles', name: 'Arc length', type: 'mcq', stem: 'What is 2 + 2?', choices: ['1', '2', '3', '4'], difficulty: 'easy' } } : o.method === 'POST' ? { correct: true, answer: 'D' } : { active: [], recent: [], shared: [], official: [] })) : process.env.NEW ? { active: [], recent: [], shared: [], official: [] } : { active: [{ id: 's1', topics: ['circles'], answered: 3, total: 10, ms: 60000 }], recent: [{ id: 's0', topics: ['percent'], answered: 10, right: 7, total: 10, finished: true, started: new Date().toISOString(), ms: 300000 }], shared: [], official: [] },
    '/sets': [],
    '/next': { items: [{ key: 'a', title: 'Plan · Linear', start: { path: '/api/drill', body: { count: 10 } }, minutes: 10 }, { key: 'b', title: 'Review due', start: { path: '/api/drill', body: { count: 5 } }, minutes: 5, reason: 'three due' }] },
  });
};
