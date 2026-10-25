// hand-made /api payloads for the Today smoke test
module.exports = variant => {
  const d0 = new Date(), iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const today = iso(d0), add = k => { const d = new Date(d0); d.setDate(d.getDate() + k); return iso(d); };
  const fresh = variant === 'fresh';
  const drill = { path: '/api/drill', body: { source: 'plan' } };
  const t = {
    profile: { name: 'Aziz Karimov', minutes: 30, target: 650, current: 560, exam_date: add(variant === 'stretch' ? 5 : 40), days: '1111100', rw_now: 600, rw_target: 650 },
    days: { today, streak: 5, best: 9, total: 20, recent: [{ minutes: 35 }, { minutes: 10 }], spares: 1 },
    study: { today: 20, week: 80, month: 300, active_days_month: 12, questions_today: 14, right_today: 10, fixed_today: 2, week_goal: 150, week_days_left: 3 },
    exam: { days: variant === 'stretch' ? 5 : 40, register_by: add(10), scores_by: null, readiness: [{ domain: 'algebra', state: 'shaky', open: 2 }] },
    workload: { study_days: 28, capacity: 840, sized: true, fits: true, total: 600, need: { tests_n: 3, traps_n: 4, traps: 40, tests: 105, warmups: 30, target: { target: 650, right_of_44: 34, now_of_44: 29, skills: ['linear_equations'], minutes: 120 } } },
    next: {
      items: variant === 'plan' || variant === 'stretch' ? [{ kind: 'plan', key: 'plan:focus:2026/T1', title: 'Plan · Linear equations', start: drill, minutes: 10, reason: 'r' }]
        : variant === 'test' ? [{ kind: 'test', id: 'x1', title: 'Section · module 1 in progress', href: '/test/?s=x1', action: 'Resume', answered: 5, asked: 22, timed: true, seconds_left: 1500 }]
        : variant === 'review' ? [{ kind: 'review', key: 'review:due:math', title: 'Review what’s due', start: drill, minutes: 5 }] : [],
      box: { options: [5, 15, 30, 45, 60], default: 15 }, count: { options: [5, 10, 22] },
      stage: { mode: variant === 'stretch' ? 'stretch' : 'learn', rehearsals: [{ day: today, done: false }] },
      preview: { blocks: [{ kind: 'skill', topic: 'linear_equations', count: 5, minutes: 7, label: 'Linear', key: 'k1', pts: 3 }, { kind: 'then', label: 'Then review' }], minutes: 15, count: 10 },
    },
    coach: { topics: ['linear_equations'], why: 'new', count: 10, reasons: {} },
    plan: fresh ? null : { id: 'p1', tasks_done: 1, tasks_counted: 3, current: 550, days: [{ date: today, kind: 'practice', minutes: 30 }, { date: add(1), kind: 'practice' }], suggest: null },
    due: fresh ? { rows: [] } : { minutes_left: 15, done: 1, goal_minutes: 30, rows: [
      { key: 'plan:2026/T1', kind: 'plan', title: 'Linear equations', tag: 'focus', minutes: 10, status: 'todo', progress: { have: 0, of: 10 }, why: ['Weak spot · 1 times'], start: drill, task_id: '2026/T1', group: 'plan' },
      { key: 'plan:2026/T2', kind: 'plan', title: 'Circles', tag: 'focus', minutes: 10, status: 'done', progress: { have: 10, of: 10 }, result: { answered: 10, right: 8 }, start: drill, task_id: '2026/T2', group: 'plan' },
      { key: 'plan:2026/T3', kind: 'plan', title: 'Module test', tag: 'test', minutes: 35, status: 'todo', start: drill, task_id: '2026/T3', group: 'plan' },
      { key: 'review', kind: 'review', title: 'Review', status: 'todo', start: drill, group: 'also', minutes: 5, meta: '2 check-ins · 0 fading · ~5 min' },
      { key: 'words', kind: 'words', title: 'Words', status: 'todo', start: { path: '/api/words/run' }, group: 'also', minutes: 4 },
      ...(variant === 'test' ? [{ key: 'test:x1', kind: 'test', title: 'Section', status: 'progress', href: '/test/?s=x1', group: 'also' }] : []),
    ] },
    traps: fresh ? { open: 0 } : { open: 3, top: [{ id: 1, label: 'Sign error', topic: 'linear_equations', template: 't1', hits: 2, owed: 2 }, { id: 2, label: 'Radius vs diameter', topic: 'circles', template: 't2' }], blind: [2], templates: 3, fixed_today: 1, fixed_week: 2, now: variant === 'stretch' ? { n: 2, gain: 6, rows: [] } : null },
    review: fresh ? {} : { due: 2, start: { path: '/api/drill', body: {}, minutes: 10 }, half: 1 },
    warmup: { due: 1, month: { held: 5, of: 8 } },
    words: fresh ? null : { due: 12, new_goal: 5, new_today: 1, minutes: 4.3, reason: 'Fading words first', start: { path: '/api/words/run' }, done: false },
    receipt: variant === 'review' ? { minutes: 35, questions: 20, right: 15, moved: [{ topic: 'circles', to: 'Strong' }], fixed: ['Sign error'], checks: { held: 2, of: 3 }, claimed: 7 } : null,
    at_risk: variant === 'plan' ? { streak: 5, left_ms: 3600000, spare: true, start: { body: {} } } : null,
    brief: fresh ? [] : [{ text: 'Yesterday: 30 of 45 min', href: '#study' }, { kind: 'checks', text: '2 check-ins due' }, { text: 'Challenge #3 of 40' }],
    scores: fresh ? [] : [{ session: 's1', at: add(-9), low: 540, high: 580, kind: 'module' }],
    score: fresh ? null : { low: 540, high: 580, session: 's1', kind: 'module', at: add(-9) },
    outside: fresh ? [] : [{ id: 7, day: add(-20), math: 560, rw: 600, source: 'bluebook' }],
    domains: [], challenge: { done: false, started: false, streak: 2, yesterday: { rank: 4, of: 30, day: add(-1), right: 8 } }, assets: [],
    seconds_per_question: 80, open: { test: variant === 'test' ? { id: 'x1', section: true, module: 1, timed: true, seconds_left: 1500, answered: 5, asked: 22, kind: 'section' } : null },
    week: fresh ? null : { this: { questions: 40, right: 30, minutes: 60, fixed: 2, opened: 3 }, last: { questions: 30, right: 20, minutes: 50, fixed: 1, opened: 4 }, moved: [{ topic: 'circles', now: 0.7, before: 0.5 }] },
    usual_start: '17:00',
  };
  const ins = fresh ? { answers: 4 } : {
    gains: { answers: 120, skills: [{ topic: 'linear_equations', gain: 12, evidence: 10, minutes: 20, accuracy: .6, per_test: 2 }, { topic: 'circles', gain: 5, evidence: 2, per_test: 1.2 }],
      extras: [{ kind: 'spr', gain: 6, detail: { spr: .4, mcq: .7, per_test: 5 } }, { kind: 'pace', gain: 3 }], top3: { gain: 12, topics: ['linear_equations'] }, others: { gain: 3 }, by_domain: [{ domain: 'algebra', gain: 9, mastery: .5, answered: 40, right: 30 }], tiers: {} },
    pace: { seconds: 1980, timed_answers: 40, limit: 2100, strip: [{ tier: 'easy', ms: 60000 }], runs_out_at: null, slow_right: [{ topic: 'circles', ms: 120000, accuracy: .8 }], guard: [], rushing: { n: 3, topic: 'circles', n_topic: 2 }, tests: { modules: 2, ran_out: 1, blanks: 1 }, week_before_ms: 2000000 },
    estimate: { practice_delta: { show: true, since: add(-9), pts: 12, answers: 80 }, evidence: { algebra: 20, geometry: 3 }, thin: ['geometry'], verdict: 'On track for 620 by the SAT', verdict_kind: 'on_track', made_per_week: 8, needs_per_week: 10 },
    causes: { total: 6, by: { trap: 3, slip: 3 }, items: { trap: [1], slip: [2] }, changes: { right_to_wrong: 3, wrong_to_right: 2 } },
    time_split: { minutes: 60, domains: { algebra: 40, geometry: 20 }, points_share: { algebra: .3, geometry: .7 }, kinds: { new: 30, fix: 30 } },
  };
  const q = { day: today, streak: 3, best: 5, month: { right: 10, of: 14 }, slots: [
    { slot: 'math:mcq', subject: 'math', label: 'Math · Multiple choice', question: { id: 'q1', type: 'mcq', stem: 'What is 2 + 2?', choices: ['1', '2', '3', '4'], topic: 'linear_equations' } },
    { slot: 'rw:wic', subject: 'rw', label: 'Words', question: { item_id: 'w1', stem: 'Which word?', choices: ['a', 'b', 'c', 'd'], text: 'A passage that is long enough to sit under the full screen button.' },
      mine: { correct: false, answer_index: 1, given: 0, crowd: { answered: 30, right: 20, picks: [5, 20, 3, 2] }, key_word: 'terse', meaning: 'brief' } },
  ], past: [{ day: add(-1), marks: { 'math:mcq': 'right', 'rw:wic': 'wrong' } }] };
  return {
    '/shell': { me: { name: 'Aziz' }, dates: [{ day: add(40), register_by: add(10) }, { day: add(70) }] },
    '/today/insights': ins,
    '/today': t,
    '/qotd': q,
    '/calendar': { month: today.slice(0, 7), days: [{ day: today, minutes: 20, questions: 14, right: 10 }], first_active: add(-30) },
    '/contest/daily/board': { entries: [{ rank: 1, name: 'A', right: 9, secs: 600 }], players: 30 },
    '/contest/daily': { count: 10, seconds: 950, me: { status: 'new' }, field: { players: 30 } },
    '/history': { sessions: fresh ? [] : [
      { id: 's1', kind: 'module', finished: add(-9) + 'T10:00:00', asked: 22, right: 16, estimate: { low: 540, high: 580 }, route: 'up', minutes: 33, modules: [{ n: 1, missed: [3, 7], blank: [22] }] },
      { id: 's0', kind: 'module', finished: add(-20) + 'T10:00:00', asked: 22, right: 14, estimate: { low: 500, high: 540 } },
    ], total: 2 },
    '/drill/preview': t.next.preview,
  };
};
