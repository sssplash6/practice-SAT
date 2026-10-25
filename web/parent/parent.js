/* The parent view, /parent/: a student's invite link, the parent's own sign in, then a short summary per child
   with a toggle when there is more than one. English, Uzbek and Russian; the choice is remembered. */
(() => {
  'use strict';
  const T = {"en": {"loc": "en-US", "title": "Your child’s progress", "signin": "Sign in to follow your child", "invited": "You were invited to follow a student’s SAT practice. Sign in with your email to accept.", "plain": "Sign in with your email to see how your child is doing.", "name": "Your name", "email": "Email", "go": "Continue", "nopass": "No password: your email is how you sign in on any device.", "bad_email": "That email doesn’t look right.", "fail": "Something went wrong. Try again.", "joined": "You are now following {name}.", "gone": "This invite has expired or was already used. Ask your child to send a new one.", "own": "This is your own invite. Send it to your parent instead.", "none": "No student linked yet", "none_p": "Ask your child to open Settings, then Privacy and data, then Parents, and press Invite a parent. Then open the link they send you.", "child": "Child", "last": "Last active", "never": "never", "today": "today", "yesterday": "yesterday", "ago": "{n} days ago", "week": "This week", "wk_q": "Questions this week", "wk_up": "{n} more than last week", "wk_down": "{n} fewer than last week", "wk_same": "Same as last week", "wk_days": "Days practised this week", "acc": "Accuracy", "time": "Time studied", "hm": "{h} h {m} min", "m": "{m} min", "days": "Active days", "streak": "Day streak", "tests": "Tests taken", "days14": "Last 14 days", "days14s": "Questions answered each day", "strong": "Doing well", "weak": "Needs attention", "few": "Not enough answers yet to say.", "recent": "Recent tests", "range": "score", "none_t": "No tests taken yet.", "goal": "Goal", "target": "Target score", "exam": "SAT date", "left": "{n} days to go", "plan": "Study plan", "yes": "Set up", "no": "Not set up yet", "mist": "Mistakes still to fix", "stop": "Stop following {name}", "sure": "Tap again to confirm", "right": "right", "kinds": {"mock": "Full test", "section": "Full section", "module": "Module", "paper": "Paper", "twin": "Twin", "custom": "Custom test", "diagnostic": "Diagnostic", "shared": "Shared test"}, "student": "Your child"}, "uz": {"loc": "uz-UZ", "title": "Farzandingiz natijalari", "signin": "Farzandingizni kuzatish uchun kiring", "invited": "Sizni o‘quvchining SAT tayyorgarligini kuzatishga taklif qilishdi. Qabul qilish uchun elektron pochtangiz bilan kiring.", "plain": "Farzandingiz qanday o‘qiyotganini ko‘rish uchun elektron pochtangiz bilan kiring.", "name": "Ismingiz", "email": "Elektron pochta", "go": "Davom etish", "nopass": "Parol kerak emas: istalgan qurilmada elektron pochtangiz orqali kirasiz.", "bad_email": "Elektron pochta noto‘g‘ri ko‘rinadi.", "fail": "Xatolik yuz berdi. Qayta urinib ko‘ring.", "joined": "Endi siz {name} natijalarini kuzatyapsiz.", "gone": "Taklif muddati tugagan yoki allaqachon ishlatilgan. Farzandingizdan yangi taklif yuborishini so‘rang.", "own": "Bu o‘zingizning taklifingiz. Uni ota-onangizga yuboring.", "none": "Hali hech kim bog‘lanmagan", "none_p": "Farzandingizdan Sozlamalar, so‘ng Maxfiylik va ma’lumotlar, so‘ng Ota-onalar bo‘limini ochib, “Ota-onani taklif qilish” tugmasini bosishini so‘rang. Keyin u yuborgan havolani oching.", "child": "Farzand", "last": "Oxirgi faollik", "never": "hech qachon", "today": "bugun", "yesterday": "kecha", "ago": "{n} kun oldin", "week": "Bu hafta", "wk_q": "Bu haftadagi savollar", "wk_up": "O‘tgan haftadan {n} ta ko‘p", "wk_down": "O‘tgan haftadan {n} ta kam", "wk_same": "O‘tgan haftadagidek", "wk_days": "Bu hafta mashq qilingan kunlar", "acc": "Aniqlik", "time": "O‘qish vaqti", "hm": "{h} soat {m} daqiqa", "m": "{m} daqiqa", "days": "Faol kunlar", "streak": "Ketma-ket kunlar", "tests": "Topshirilgan testlar", "days14": "So‘nggi 14 kun", "days14s": "Har kuni yechilgan savollar", "strong": "Yaxshi natijalar", "weak": "E’tibor kerak", "few": "Xulosa qilish uchun hali yetarli javob yo‘q.", "recent": "So‘nggi testlar", "range": "ball", "none_t": "Hali test topshirilmagan.", "goal": "Maqsad", "target": "Maqsadli ball", "exam": "SAT sanasi", "left": "{n} kun qoldi", "plan": "O‘quv reja", "yes": "Tuzilgan", "no": "Hali tuzilmagan", "mist": "Tuzatilishi kerak bo‘lgan xatolar", "stop": "{name} natijalarini kuzatishni to‘xtatish", "sure": "Tasdiqlash uchun yana bosing", "right": "to‘g‘ri", "kinds": {"mock": "To‘liq test", "section": "To‘liq bo‘lim", "module": "Modul", "paper": "Variant", "twin": "Juft test", "custom": "Maxsus test", "diagnostic": "Diagnostika", "shared": "Ulashilgan test"}, "student": "Farzandingiz"}, "ru": {"loc": "ru-RU", "title": "Успехи вашего ребёнка", "signin": "Войдите, чтобы следить за успехами ребёнка", "invited": "Вас пригласили следить за подготовкой ученика к SAT. Чтобы принять приглашение, войдите по электронной почте.", "plain": "Войдите по электронной почте, чтобы увидеть, как занимается ваш ребёнок.", "name": "Ваше имя", "email": "Электронная почта", "go": "Продолжить", "nopass": "Пароль не нужен: вы входите по электронной почте с любого устройства.", "bad_email": "Похоже, адрес почты указан неверно.", "fail": "Что-то пошло не так. Попробуйте ещё раз.", "joined": "Теперь вы следите за успехами: {name}.", "gone": "Срок приглашения истёк или оно уже использовано. Попросите ребёнка отправить новое.", "own": "Это ваше собственное приглашение. Отправьте его родителю.", "none": "Пока никто не подключён", "none_p": "Попросите ребёнка открыть Настройки, затем «Конфиденциальность и данные», затем «Родители» и нажать «Пригласить родителя». Затем откройте ссылку, которую он пришлёт.", "child": "Ребёнок", "last": "Последняя активность", "never": "никогда", "today": "сегодня", "yesterday": "вчера", "ago": "{n} дн. назад", "week": "Эта неделя", "wk_q": "Вопросов за неделю", "wk_up": "На {n} больше, чем на прошлой неделе", "wk_down": "На {n} меньше, чем на прошлой неделе", "wk_same": "Столько же, сколько на прошлой неделе", "wk_days": "Дней занятий на этой неделе", "acc": "Точность", "time": "Время занятий", "hm": "{h} ч {m} мин", "m": "{m} мин", "days": "Дней с занятиями", "streak": "Дней подряд", "tests": "Пройдено тестов", "days14": "Последние 14 дней", "days14s": "Решено вопросов по дням", "strong": "Получается хорошо", "weak": "Нужно подтянуть", "few": "Пока слишком мало ответов для выводов.", "recent": "Недавние тесты", "range": "баллов", "none_t": "Тестов пока нет.", "goal": "Цель", "target": "Целевой балл", "exam": "Дата SAT", "left": "До экзамена: {n} дн.", "plan": "План занятий", "yes": "Составлен", "no": "Пока не составлен", "mist": "Ошибок, которые ещё нужно исправить", "stop": "Больше не следить: {name}", "sure": "Нажмите ещё раз для подтверждения", "right": "верно", "kinds": {"mock": "Полный тест", "section": "Полный раздел", "module": "Модуль", "paper": "Вариант", "twin": "Парный тест", "custom": "Свой тест", "diagnostic": "Диагностика", "shared": "Общий тест"}, "student": "Ваш ребёнок"}};
  Object.assign(T.en, { mail_on: 'Email me a weekly summary and updates', total14: '{n} in 14 days', wk_of: '{n} of 7 days practised',
    none_lead: 'Ask your child to do this in their account:', none_s: ['Open Settings.', 'Go to Privacy and data, then Parents.', 'Press Invite a parent and send you the link.'],
    none_end: 'Then open the link they send you.',
    sc: 'Scores', now: 'Now', aim: 'Target', total: 'Total', rw: 'Reading and Writing', math: 'Math', full: 'Full SAT',
    yours: '* typed by your child, not measured yet' });
  Object.assign(T.uz, {
    sc: 'Ballar', now: 'Hozir', aim: 'Maqsad', total: 'Umumiy ball', rw: 'O‘qish va yozish', math: 'Matematika', full: 'To‘liq SAT',
    yours: '* farzandingiz o‘zi kiritgan, hali o‘lchanmagan', mail_on: 'Haftalik xulosa va yangiliklarni elektron pochtamga yuborish', total14: '14 kunda {n} ta', wk_of: '7 kundan {n} kuni mashq qilindi',
    none_lead: 'Farzandingizdan o‘z hisobida quyidagilarni bajarishini so‘rang:', none_s: ['Sozlamalarni ochish.', 'Maxfiylik va ma’lumotlar, so‘ng Ota-onalar bo‘limiga o‘tish.', '“Ota-onani taklif qilish” tugmasini bosib, havolani sizga yuborish.'],
    none_end: 'Keyin u yuborgan havolani oching.' });
  Object.assign(T.ru, {
    sc: 'Баллы', now: 'Сейчас', aim: 'Цель', total: 'Общий балл', rw: 'Чтение и письмо', math: 'Математика', full: 'Полный SAT',
    yours: '* указано ребёнком, ещё не измерено', mail_on: 'Присылать мне итоги недели и новости на почту', total14: '{n} за 14 дней', wk_of: '{n} из 7 дней с занятиями',
    none_lead: 'Попросите ребёнка сделать в своём аккаунте:', none_s: ['Открыть Настройки.', 'Перейти в «Конфиденциальность и данные», затем «Родители».', 'Нажать «Пригласить родителя» и отправить вам ссылку.'],
    none_end: 'Затем откройте ссылку, которую он пришлёт.' });
  const h = UI.h, A = UI.acct;
  const root = document.getElementById('root');
  const q = new URLSearchParams(location.search);
  const invite = q.get('invite') || '';
  const LS = { get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (_) {} } };
  const guess = () => { const n = (navigator.language || 'en').toLowerCase(); return n.startsWith('ru') ? 'ru' : n.startsWith('uz') ? 'uz' : 'en'; };
  let lang = T[LS.get('satf.parent.lang')] ? LS.get('satf.parent.lang') : guess();
  let kid = LS.get('satf.parent.kid') || '';
  let redraw = () => {};
  let signed = false, prefs = { lang: null, mail: true };
  let entered = false;      // the page entry plays once, on the first dashboard paint (kit.js runs it on a fresh visit)
  const savePrefs = patch => { if (signed) UI.api('/parent/prefs', { method: 'PUT', body: patch, quiet: true }).catch(() => {}); };
  const t = (k, v) => String(T[lang][k] ?? T.en[k]).replace(/\{(\w+)\}/g, (_, x) => (v && v[x] !== undefined ? v[x] : ''));
  const num = n => (n === null || n === undefined ? '-' : Number(n).toLocaleString(T[lang].loc));
  const pct = x => (x === null || x === undefined ? '-' : `${Math.round(x * 100)}%`);
  const date = s => (s ? new Date(s).toLocaleDateString(T[lang].loc, { month: 'short', day: 'numeric', year: 'numeric' }) : '-');
  const short = s => new Date(s).toLocaleDateString(T[lang].loc, { month: 'short', day: 'numeric' });
  const mins = m => (m >= 60 ? t('hm', { h: Math.floor(m / 60), m: m % 60 }) : t('m', { m }));
  const ago = s => {
    if (!s) return t('never');
    const d = Math.floor((Date.now() - new Date(s).getTime()) / 864e5);
    return d <= 0 ? t('today') : d === 1 ? t('yesterday') : d < 30 ? t('ago', { n: d }) : date(s);
  };
  const stat = (v, l, sub) => h('div', { class: 'stat' }, h('span', { class: 'stat-k', text: l }), h('span', { class: 'stat-v', text: v }), sub ? h('span', { class: 'stat-sub', text: sub }) : null);
  const card = (title, sub, ...kids) => h('section', { class: 'card par-card' },
    h('div', { class: 'card-head' }, h('h2', { text: title }), sub ? h('span', { class: 'meta', text: sub }) : null), ...kids);

  function top(extra) {
    const seg = h('div');
    UI.seg(seg, [{ value: 'en', label: 'EN' }, { value: 'uz', label: 'O‘Z' }, { value: 'ru', label: 'РУ' }],
      { value: lang, label: 'Language', onChange: v => { lang = v; LS.set('satf.parent.lang', v); document.documentElement.lang = v; savePrefs({ lang: v }); redraw(); } });
    return h('div', { class: 'par-top' }, h('span', { html: UI.mark(28) }), h('h1', { class: 'h1 grow', text: t('title') }), seg);
  }
  const page = (...kids) => { document.title = `${t('title')} · SAT Freshman`; root.replaceChildren(top(), ...kids.filter(Boolean)); };

  /* sign in: name + email, closed beta lets the email in with no code, otherwise the normal welcome page does the code */
  function signIn() {
    const err = h('p', { class: 'field-err', role: 'alert', hidden: true });
    const say = m => { err.textContent = m || ''; err.hidden = !m; };
    const name = h('input', { class: 'field', type: 'text', autocomplete: 'given-name', 'aria-label': t('name'), placeholder: t('name'), maxlength: '40' });
    const email = h('input', { class: 'field', type: 'email', autocomplete: 'email', inputmode: 'email', spellcheck: 'false', 'aria-label': t('email'), placeholder: 'name@example.com' });
    const back = location.pathname + location.search;
    const send = async () => {
      say('');
      if (!email.checkValidity() || !email.value.trim()) { say(t('bad_email')); email.focus(); return; }
      try {
        if (name.value.trim()) await UI.api('/me', { method: 'PUT', body: { name: name.value.trim() } });
        try {
          const res = await UI.api('/account/beta', { method: 'POST', body: { email: email.value.trim() }, quiet: true });
          await A.finish(res, { shared: false, local: { answers: 0 }, to: back, method: 'email' });
        } catch (x) {
          if (x.status !== 404) throw x;
          location.href = `/welcome/?go=${encodeURIComponent(back)}`;
        }
      } catch (x) { say(t('fail')); }
    };
    [name, email].forEach(f => f.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); send(); } }));
    const go = h('button', { type: 'button', class: 'pill', text: t('go') }); go.addEventListener('click', send);
    // one raised card, like Sign in: the form no longer floats on the page
    page(h('section', { class: 'card hero par-in' }, h('h2', { class: 'h2', text: t('signin') }), h('p', { class: 'par-lead', text: invite ? t('invited') : t('plain') }),
      h('div', { class: 'par-form' }, name, email, err, go, h('p', { class: 'help', text: t('nopass') }))));
  }

  function message(title, body) { page(h('h2', { class: 'h2', text: title }), h('p', { class: 'par-lead', text: body })); }
  // no child linked yet: the first-use drawing, then the three steps the child takes
  function noKid() {
    page(UI.spotArt ? h('div', { html: UI.spotArt('start') }) : null, h('h2', { class: 'h2', text: t('none') }), h('p', { class: 'par-lead', text: t('none_lead') }),
      h('ol', { class: 'par-steps' }, (T[lang].none_s || T.en.none_s).map(x => h('li', { text: x }))), h('p', { class: 'par-lead', text: t('none_end') }));
  }
  // while /account and the child's numbers load: the This week card at its final size, static (rule 8)
  const weekSkel = () => h('section', { class: 'card par-card hero', 'aria-busy': 'true', 'aria-label': t('week') },
    UI.skel(null, 'line.lg'), UI.skel(null, { w: 160, h: 56 }), UI.skel(null, { w: '55%', h: 12 }), UI.skel(null, { h: 72 }));

  function dash(list, d) {
    const cur = list.find(c => c.id === kid) || list[0];
    const wk = d.week, diff = wk.answers - wk.prev_answers;
    const max = Math.max(1, ...d.last14.map(x => x.answers));
    const days = d.goal.exam_date ? Math.ceil((new Date(d.goal.exam_date + 'T00:00:00') - Date.now()) / 864e5) : null;
    const skill = s => h('li', {}, h('div', { class: 'par-sk' }, s.name, s.subject ? h('span', { class: 'par-subj', text: ` · ${t(s.subject)}` }) : null,
      h('span', { class: 'par-meter' }, h('i', { style: `width: ${Math.round(s.accuracy * 100)}%` }))), h('b', { text: pct(s.accuracy) }));
    const kv = rows => h('dl', { class: 'par-kv' }, rows.filter(Boolean).flatMap(([k, v]) => [h('dt', { text: k }), h('dd', { text: v })]));
    // scores side by side, College Board's order: Total, R&W, Math; each now a 20-point range from the server, and its target
    const sc = d.scores || {}, rng = x => (x && x.low !== null && x.low !== undefined ? `${x.low}–${x.high}${x.source === 'yours' ? '*' : ''}` : '-');   // scores read bare, never 1,200
    const scRows = ['total', 'rw', 'math'].filter(k => sc[k] && (sc[k].low !== null || sc[k].target));
    const scores = scRows.length ? card(t('sc'), null, h('div', { class: 'par-sc' }, h('span'), h('span', { class: 'k', text: t('now') }), h('span', { class: 'k', text: t('aim') }),
      ...scRows.flatMap(k => [h('span', { class: k === 'total' ? 'par-sc-t' : '', text: t(k) }), h('b', { text: rng(sc[k]) }), h('span', { text: sc[k].target ? String(sc[k].target) : '-' })])),
      scRows.some(k => sc[k].source === 'yours') ? h('p', { class: 'meta', text: t('yours') }) : null) : null;
    const testName = x => (x.kind === 'full' ? t('full') : `${t(x.subject === 'rw' ? 'rw' : 'math')} · ${T[lang].kinds[x.kind] || x.kind}${x.number ? ` #${x.number}` : ''}`);
    const mailBox = h('input', { type: 'checkbox', checked: prefs.mail });
    mailBox.addEventListener('change', () => { prefs.mail = mailBox.checked; savePrefs({ mail: mailBox.checked }); });
    let sure = false;
    const stop = h('button', { type: 'button', class: 'quiet', text: t('stop', { name: cur.name || t('student') }) });
    stop.addEventListener('click', async () => {
      if (!sure) { sure = true; stop.textContent = t('sure'); return; }
      try { await UI.api(`/parent/children/${encodeURIComponent(cur.id)}`, { method: 'DELETE' }); kid = ''; start(); } catch (_) { stop.textContent = t('fail'); }
    });
    // the 14 bars: a pointer or a tap names its day in the axis row between the first and last dates (a fixed slot,
    // nothing floats over the bars); at rest it shows the 14-day total. The label carries every day for screen readers
    const total = d.last14.reduce((a, x) => a + (x.answers || 0), 0);
    const read = h('span', { class: 'par-read', 'aria-hidden': 'true' });
    const bars = h('div', { class: 'par-bars', role: 'img', 'aria-label': `${t('days14s')}: ${d.last14.map(x => `${short(x.day)} ${num(x.answers)}`).join(', ')}` },
      d.last14.map(x => h('i', { class: x.answers ? 'on' : '', 'data-m': 'bar', style: `height: ${Math.max(2, Math.round(x.answers / max * 100))}%` })));
    const say = k => {
      read.textContent = k === null ? t('total14', { n: num(total) }) : `${short(d.last14[k].day)}: ${num(d.last14[k].answers)}`;
      [...bars.children].forEach((b, i) => b.toggleAttribute('data-at', i === k));
    };
    const at = e => { const r = bars.getBoundingClientRect(); return r.width ? Math.max(0, Math.min(13, Math.floor((e.clientX - r.left) / r.width * 14))) : null; };
    bars.addEventListener('pointermove', e => say(at(e)));
    bars.addEventListener('pointerdown', e => say(at(e)));
    bars.addEventListener('pointerleave', e => { if (e.pointerType === 'mouse') say(null); });
    say(null);
    if (!entered) { entered = true; root.setAttribute('data-m', 'stagger'); }
    let picker = null;
    if (list.length > 1) { picker = h('div'); UI.seg(picker, list.map(c => ({ value: c.id, label: c.name || t('student') })), { value: cur.id, label: t('child'), onChange: v => { kid = v; LS.set('satf.parent.kid', v); load(list); } }); }
    // this week leads: its two figures and the last 14 days in one card; the all-time totals sit under it as a quiet row
    page(picker, h('div', {}, h('h2', { class: 'h2', text: cur.name || t('student') }), h('p', { class: 'meta', text: `${t('last')}: ${ago(d.last)}` })),
      h('section', { class: 'card par-card hero' },
        h('div', { class: 'card-head' }, h('h2', { text: t('week') })),
        h('div', { class: 'par-fig' }, h('span', { class: 'stat-k', text: t('wk_q') }), h('span', { class: 'hero-num', text: num(wk.answers) }),
          h('p', { class: 'par-sub' }, h('span', { text: diff ? t(diff > 0 ? 'wk_up' : 'wk_down', { n: num(Math.abs(diff)) }) : t('wk_same') }),
            h('span', { text: t('wk_of', { n: num(wk.active_days) }) }))),
        h('p', { class: 'k', text: `${t('days14')} · ${t('days14s')}` }),
        // no answers in 14 days: one line instead of 14 empty bars
        ...(total ? [bars, h('div', { class: 'par-axis' }, h('span', { text: short(d.last14[0].day) }), read, h('span', { text: short(d.last14[13].day) }))]
          : [h('p', { class: 'par-empty', text: t('total14', { n: num(0) }) })])),
      h('div', { class: 'stats par-tot' }, stat(pct(d.totals.accuracy), t('acc')), stat(mins(d.totals.minutes), t('time')),
        stat(num(d.totals.streak), t('streak')), stat(num(d.totals.tests), t('tests'))),
      scores,
      h('div', { class: 'par-cols' },
        card(t('strong'), null, d.strong.length ? h('ul', { class: 'par-list' }, d.strong.map(skill)) : h('p', { class: 'par-empty', text: t('few') })),
        card(t('weak'), null, d.focus.length ? h('ul', { class: 'par-list' }, d.focus.map(skill)) : h('p', { class: 'par-empty', text: t('few') }))),
      card(t('recent'), null, d.tests.length ? h('ul', { class: 'par-list' }, d.tests.map(x => h('li', {}, h('span', { text: `${date(x.finished)} · ${testName(x)}` }),
        h('b', { text: x.low ? `${x.low}–${x.high}` : (x.asked ? `${x.right} / ${x.asked}` : '-') })))) : h('p', { class: 'par-empty', text: t('none_t') })),
      card(t('goal'), null, kv([d.goal.exam_date ? [t('exam'), `${date(d.goal.exam_date)}${days !== null && days >= 0 ? ` · ${t('left', { n: days })}` : ''}`] : null,
        [t('plan'), d.goal.has_plan ? t('yes') : t('no')], [t('mist'), num(d.open_mistakes)]].filter(r => !r || r[1] !== null))),
      h('div', { class: 'par-foot' }, h('label', { class: 'check' }, mailBox, t('mail_on')), stop));
    if (total && UI.motion && UI.motion.once('parent-bars')) UI.motion.draw(bars);
  }

  async function load(list) {
    const cur = list.find(c => c.id === kid) || list[0];
    kid = cur.id;
    redraw = () => load(list);
    try { dash(list, await UI.api(`/parent/children/${encodeURIComponent(cur.id)}`)); }
    catch (_) { message(t('title'), t('fail')); }
  }

  async function start() {
    redraw = start;
    if (!root.firstChild) page(weekSkel());
    let acc = null;
    try { acc = await UI.api('/account'); } catch (_) {}
    if (!acc || !acc.saved) { redraw = signIn; signIn(); return; }
    signed = true;
    if (invite) {
      try {
        const r = await UI.api('/parent/join', { method: 'POST', body: { code: invite }, quiet: true });
        kid = r.child.id; LS.set('satf.parent.kid', kid);
        history.replaceState(null, '', '/parent/');
        UI.toast && UI.toast(t('joined', { name: r.child.name || t('student') }));
      } catch (x) {
        history.replaceState(null, '', '/parent/');
        if (x.status === 409) { redraw = () => message(t('title'), t('own')); redraw(); return; }
        if (x.status !== 410) { message(t('title'), t('fail')); return; }
        const had = await UI.api('/parent/children').catch(() => null);
        if (!had || !had.children.length) { redraw = () => message(t('title'), t('gone')); redraw(); return; }
      }
    }
    const got = await UI.api('/parent/children').catch(() => ({ children: [] }));
    const list = got.children;
    if (got.prefs) { prefs = got.prefs; if (!prefs.lang) savePrefs({ lang }); else if (!LS.get('satf.parent.lang') && T[prefs.lang]) { lang = prefs.lang; document.documentElement.lang = lang; } }
    if (!list.length) { redraw = noKid; redraw(); return; }
    load(list);
  }
  document.documentElement.lang = lang;
  start();
})();
