// check for UI.weekPlanner's save(): which requests a week sends. node weekplanner.js (exit 1 on a failure)
const fs = require('fs'), assert = require('assert');
const { JSDOM } = require('/Users/workingmyassof/freshbot/calc/node_modules/jsdom');
const src = fs.readFileSync('/Users/workingmyassof/freshbot/satbank/web/assets/plan-ui.js', 'utf8');

// bodies are copied out of jsdom's realm (JSON), so deepStrictEqual compares values, not prototypes
function planner(week) {
  const dom = new JSDOM('<!doctype html><body></body>', { runScripts: 'outside-only' });
  const calls = [];
  dom.window.UI = { api: async (p, o) => { calls.push([p, o.method, JSON.parse(JSON.stringify(o.body))]); return { ok: true }; }, TOPIC: {} };
  dom.window.eval(src);
  return { p: dom.window.UI.weekPlanner(null, { ...week, button: false }), calls, doc: dom.window.document };
}
const days = [
  { date: '2026-10-19', kind: 'practice', minutes: 30, topics: ['circles'] },
  { date: '2026-10-20', kind: 'practice', minutes: 30, topics: ['circles', 'lines'] },
  { date: '2026-10-21', kind: 'rest', minutes: 0, topics: [] },
  { date: '2026-10-22', kind: 'practice', minutes: 45, topics: ['lines'] },
];
// rows are labelled by UI.date when kit is loaded, else by the ISO date (as here)
const press = (root, date, label) => [...root.querySelectorAll('.wplan-day')].find(r => r.textContent.includes(date))
  .querySelector(`button[aria-pressed]${label === 'Busy' ? ':nth-of-type(1)' : ':nth-of-type(2)'}`).click();

(async () => {
  // a week not begun: one PUT week with the changed days
  let t = planner({ plan: 'p1', monday: '2026-10-19', today: '2026-10-18', last: '2026-12-01', days });
  press(t.p.el, '2026-10-20', 'Busy');
  press(t.p.el, '2026-10-22', 'Short');
  await t.p.save();
  assert.deepStrictEqual(t.calls, [['/plan/p1/week/2026-10-19', 'PUT', { days: [{ date: '2026-10-20', off: true }, { date: '2026-10-22', minutes: 15 }] }]]);

  // the current week: day by day, and past days are left alone
  t = planner({ plan: 'p1', monday: '2026-10-19', today: '2026-10-20', last: '2026-12-01', days });
  assert.strictEqual(t.p.el.querySelectorAll('.wplan-day[data-past]').length, 1, 'Monday is past');
  press(t.p.el, '2026-10-22', 'Busy');
  await t.p.save();
  assert.deepStrictEqual(t.calls, [['/plan/p1/day/2026-10-22', 'PUT', { off: true }]]);

  // a swap puts the new skill in place of the old on each editable day that holds it
  t = planner({ plan: 'p1', monday: '2026-10-19', today: '2026-10-20', last: '2026-12-01', days, focus: ['circles', 'lines'], swaps: [{ topic: 'ratios' }] });
  const [from, to] = t.p.el.querySelectorAll('.wplan-swap select');
  from.value = 'circles'; from.dispatchEvent(new t.doc.defaultView.Event('change'));
  to.value = 'ratios'; to.dispatchEvent(new t.doc.defaultView.Event('change'));
  await t.p.save();
  assert.deepStrictEqual(t.calls, [['/plan/p1/day/2026-10-20', 'PUT', { topics: ['ratios', 'lines'] }]]);

  // nothing changed: no request
  t = planner({ plan: 'p1', monday: '2026-10-19', today: '2026-10-18', days });
  assert.strictEqual(await t.p.save(), null);
  assert.strictEqual(t.calls.length, 0);
  console.log('weekPlanner: 4 checks passed');
})().catch(e => { console.error(e); process.exit(1); });
