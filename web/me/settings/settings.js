/* ============================================================================
   SAT Freshman -- Settings, /me/settings/ (Shell 4; shell-me U11, U15, U18a, U19, U19b,
   U20, U21, U22, U24, U29; R11)

   Six sections on the shell's section bar. Every pref row is UI.prefRow over the one
   registry (GET /api/prefs): it saves the moment it changes, says Saved, and reverts
   and says why when a save fails. Every registry key has a row, placed by its group.
   Account & devices is account.py's: email (the one way in since 2026-10-20) and devices.
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h, A = UI.acct;
  const N = n => UI.num(n);
  const pl = (n, one, many) => `${N(n)} ${n === 1 ? one : many || one + 's'}`;
  const day = d => UI.date(d, 'short');
  const $ = id => document.querySelector(`#${id} .card-body`);
  const ls = A.ls;
  const sub = (host, text) => host.append(h('h3', { class: 'sub-h', text }));
  const help = (host, text) => host.append(h('p', { class: 'help', text }));
  function btn(label, o = {}) {
    const b = h(o.href ? 'a' : 'button', { class: o.primary ? 'pill sm' : o.quiet ? 'quiet' : 'btn sm', type: o.href ? null : 'button', href: o.href || null }, label);
    if (o.onClick) b.addEventListener('click', async e => {
      if (b.getAttribute('aria-busy') === 'true') return;
      b.setAttribute('aria-busy', 'true');
      try { await o.onClick(e, b); } finally { b.removeAttribute('aria-busy'); }
    });
    return b;
  }
  const errText = (e, fallback) => (e && e.offline ? 'You’re offline. Try again when you’re back.' : fallback);
  // Copy says Copied in place (kit.js UI.copyText with its button); a browser that refuses gets kit's copy sheet
  const copyIn = (b, text) => UI.copyText(text, { button: b });

  const SECTIONS = [
    { id: 'practice', label: 'Practice', icon: 'practice' }, { id: 'display', label: 'Tools & display', icon: 'settings' }, { id: 'study', label: 'Study', icon: 'calendar' },
    { id: 'account', label: 'Account & devices', icon: 'devices' }, { id: 'reports', label: 'Your reports', icon: 'chat' }, { id: 'privacy', label: 'Privacy & data', icon: 'shield' }];
  UI.shell({ page: 'settings', sections: SECTIONS });
  // the aside from 1280px: the same sections as a list, each with its one-line state (the section bar has the chips)
  const idxMeta = {};
  document.getElementById('set-index').append(...SECTIONS.map(x => {
    idxMeta[x.id] = h('span', { class: 'meta' });
    return h('a', { href: `#${x.id}` }, h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.ICON[x.icon] ? UI.svg(UI.ICON[x.icon], 18) : '' }),
      h('span', { text: x.label }), idxMeta[x.id]);
  }));
  const idxSay = (id, text) => { if (idxMeta[id]) idxMeta[id].textContent = text || ''; };

  // each section's "?" opens its Help answer (U13)
  [['practice', 'stages'], ['study', 'reminders'], ['account', 'devices'], ['reports', 'report'], ['privacy', 'data']].forEach(([id, a]) => {
    const t = document.getElementById(`${id}-h`);
    if (t) t.after(A.helpBtn(a, t.textContent));
  });

  let P = null;
  UI.me().then(r => { P = r.profile; paintStudyPlan(); paintBoards(); }, () => {});
  // what this deploy has switched on: mail, google (+ google_client_id), push
  let HEALTH = null;
  const health = () => HEALTH || (HEALTH = fetch('/api/health').then(r => r.json()).catch(() => ({})));

  /* ================================================================ prefs, placed by group */
  // internal or retired keys: stored by the pages that own them, never a setting
  const HIDDEN = new Set(['practice', 'levels', 'unmeasured', 'snooze', 'contest_timing_seen', 'hide_timer']);
  const PLACE = {
    practice: ['mode', 'stage_auto', 'set_length', 'clock', 'clock_minutes', 'tiers', 'adaptive', 'formats', 'feedback', 'repairs', 'rationale',
      'open_explanations', 'option_reasons', 'first_tap', 'confidence', 'type_rules', 'second_look', 'order', 'mix', 'pool', 'keep_warm',
      'confirm_end', 'keys', 'review_minutes', 'saved_spaced'],
    tests: ['test_timing', 'test_conditions', 'test_calculator', 'test_pace', 'test_confidence', 'test_reveal_route', 'test_fullscreen',
      'test_nudges', 'test_cover', 'test_predict', 'test_type_notes'],
    display: ['show_timer', 'show_stopwatch', 'pace_alert', 'calc_button', 'calc_mode', 'ref_button', 'theme', 'text', 'motion', 'week_start',
      'race_rail', 'contest_timing'],
    study: ['study_time', 'remind', 'quiet', 'registered', 'plan_auto_focus', 'plan_auto_drift'],
    words: ['words_goal', 'words_from', 'gloss', 'words_autonext', 'words_commit', 'words_method', 'words_relation', 'words_spread'],
  };
  const GROUP_HOME = { practice: 'practice', session: 'display', look: 'display', words: 'words', reminders: 'study', tests: 'tests',
    review: 'practice', compete: 'display', plan: 'study' };
  // four open per group (premium 2026-10-19: a calm first screen); the rest of each wait one tap away under "More ... options"
  const OPEN = new Set(['mode', 'set_length', 'clock', 'tiers',
    'test_timing', 'test_calculator', 'test_pace', 'test_fullscreen',
    'theme', 'text', 'motion', 'show_timer',
    'study_time', 'remind', 'quiet', 'registered',
    'words_goal', 'words_from', 'gloss', 'words_method']);
  const hosts = {};
  function prefRows(listing) {
    const placed = new Set(Object.values(PLACE).flat());
    const extra = {};
    (listing || []).forEach(p => {
      if (!p || HIDDEN.has(p.key) || placed.has(p.key)) return;
      (extra[GROUP_HOME[p.group] || 'practice'] = extra[GROUP_HOME[p.group] || 'practice'] || []).push(p.key);
    });
    const known = new Set((listing || []).map(p => p.key));
    const rows = (host, name, more) => {
      const keys = [...PLACE[name], ...(extra[name] || [])].filter(k => !listing || known.has(k));
      const rest = more ? keys.filter(k => !OPEN.has(k)) : [];
      const box = rest.length ? h('div') : null;
      keys.forEach(k => {
        const to = box && rest.includes(k) ? box : host;
        UI.prefRow(to, k, k === 'study_time' ? { onChange: v => { quietNote(); offerNudge(v); } } : k === 'quiet' ? { onChange: quietNote } : undefined);
        if (k === 'text') to.append(h('p', { class: 'preview-q', 'aria-hidden': 'true', text: 'If 3x + 5 = 20, what is x?' }));
        if (k === 'quiet') to.append(quietLine);
      });
      if (box) host.append(h('details', { class: 'set-more' }, h('summary', { text: `${more} (${rest.length})` }), box));
    };
    // Practice
    const pr = $('practice');
    pr.replaceChildren();
    const stage = h('p', { class: 'help set-intro', hidden: true });
    pr.append(stage);
    hosts.practice = h('div'); pr.append(hosts.practice); rows(hosts.practice, 'practice', 'More practice options');
    sub(pr, 'Tests'); hosts.tests = h('div'); pr.append(hosts.tests); rows(hosts.tests, 'tests', 'More test options');
    pr.append(h('div', { class: 'card-foot' },
      btn('Reset practice defaults', { quiet: true, onClick: () => resetPractice(false) }),
      btn('Use stage defaults', { quiet: true, onClick: () => resetPractice(true) })));
    const paintStage = () => {
      const s = UI.shellData() && UI.shellData().stage;
      const names = { learn: 'Learn', build: 'Build', test: 'Test-like', final: 'Final week' };
      stage.textContent = s && s.name ? [names[s.name] || s.name, s.days_to_exam !== undefined && s.days_to_exam !== null ? `${pl(s.days_to_exam, 'day')} to your exam` : null,
        s.next && s.next.on ? `${names[s.next.name] || s.next.name} starts ${day(s.next.on)}` : null].filter(Boolean).join(' · ') : '';
      stage.hidden = !stage.textContent;
      idxSay('practice', s && s.name ? names[s.name] || s.name : '');
    };
    UI.onShell(paintStage);
    // Tools & display
    const ds = $('display');
    ds.replaceChildren();
    hosts.display = h('div'); ds.append(hosts.display); rows(hosts.display, 'display', 'More display options');
    // Study keeps its plan and calendar block first, then the reminders and Words
    hosts.study = h('div'); hosts.words = h('div');
    const push = h('div');
    studyBody().append(push, hosts.study);
    rows(hosts.study, 'study', 'More study options');
    quietNote();
    paintPush(push);
    sub(studyBody(), 'Words');
    studyBody().append(hosts.words);
    rows(hosts.words, 'words', 'More Words options');
  }
  async function resetPractice(onlyStage) {
    const pr = UI.prefs.now(), src = (UI.shellData() && UI.shellData().pref_source) || {};
    const keys = [...PLACE.practice, ...PLACE.tests].filter(k => k in pr && (onlyStage ? src[k] === 'yours' : src[k] !== 'default'));
    if (!keys.length) { UI.toast(onlyStage ? 'Nothing of yours to put back.' : 'Already the defaults.'); return; }
    const before = Object.fromEntries(keys.map(k => [k, pr[k]]));
    try {
      await UI.prefs.set(Object.fromEntries(keys.map(k => [k, null])));
      UI.toast(onlyStage ? 'Back to your stage' : 'Practice defaults reset', { undo: () => UI.prefs.set(before).then(() => location.reload()) });
      setTimeout(() => location.reload(), 900);
    } catch (e) { UI.toast(errText(e, 'Not saved. Try again.')); }
  }
  let studyEl = null;
  function studyBody() {
    if (!studyEl) { studyEl = $('study'); studyEl.replaceChildren(h('div', { id: 'study-plan' })); }
    return studyEl;
  }
  /* ---- quiet hours never hold back the reminder the student timed (U18b) */
  const quietLine = h('p', { class: 'help quiet-line', hidden: true });
  function quietNote() {
    const pr = UI.prefs.now() || {}, t = pr.study_time, q = pr.quiet;
    const inside = t && q && q.from && q.to && (q.from < q.to ? t >= q.from && t < q.to : t >= q.from || t < q.to);
    quietLine.textContent = inside ? `Your ${t} reminder still rings. Quiet hours only hold back extra nudges.` : '';
    quietLine.hidden = !inside;
  }

  /* ---- Notify me on this device (U18b). It shows once /api/health says push, the server serves
     GET /api/push/key and F2's /sw.js is there, and asks the browser only on a tap. The
     subscription goes to POST /api/push/subscribe {endpoint, keys, kinds}, PUT {endpoint, kinds},
     DELETE {endpoint}. */
  const KINDS = [['study', 'Study reminders', 'At your study time, less the reminder lead.', true],
    ['streak', 'One question keeps your streak', 'At 20:30 on a study day with nothing done yet.', false],
    ['contest', 'A contest you joined closes soon', 'Three hours before it closes.', true]];
  const b64 = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), c => c.charCodeAt(0));
  async function paintPush(host) {
    if (!(await health()).push) return;                                                   // off, or not built yet
    let key = null;
    try { key = (await UI.api('/push/key', { quiet: true })).key; } catch (_) { return; }
    if (!key) return;
    const ios = /iPhone|iPad|iPod/.test(navigator.userAgent) && !matchMedia('(display-mode: standalone)').matches;
    if (ios || !('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) {
      host.append(h('div', { class: 'pref' }, h('span', { class: 'pref-k', text: 'Notify me on this device' }),
        h('p', { class: 'help' }, ios ? 'On iPhone, notifications come from the home-screen app. ' : 'This browser can’t show notifications. ',
          h('a', { class: 'link', href: '/help/#install', text: 'How to add it' }))));
      return;
    }
    let reg = await navigator.serviceWorker.getRegistration('/').catch(() => null);
    let subn = reg ? await reg.pushManager.getSubscription().catch(() => null) : null;
    let kinds = ls.get('satf.push.kinds', null) || Object.fromEntries(KINDS.map(k => [k[0], k[3]]));
    const kindsBox = h('div');
    const note = h('p', { class: 'help', hidden: true });
    const drawKinds = () => kindsBox.replaceChildren(...(subn ? KINDS.map(([id, label, helper]) => {
      const ctl = h('div', { class: 'pref-ctl' });
      UI.switch(ctl, { checked: !!kinds[id], label, onChange: async v => {
        const next = { ...kinds, [id]: v };
        await UI.api('/push/subscribe', { method: 'PUT', body: { endpoint: subn.endpoint, kinds: next } });
        kinds = next; ls.set('satf.push.kinds', kinds);
      } });
      return h('div', { class: 'pref' }, h('span', { class: 'pref-k', text: label }), h('p', { class: 'help', text: helper }), ctl);
    }) : []));
    async function enable() {                                      // only ever called from a tap
      const perm = await Notification.requestPermission();
      if (perm !== 'granted') { note.textContent = 'Your browser said no. Allow notifications for this site in its settings, then try again.'; note.hidden = false; throw new Error('denied'); }
      try {
        reg = reg || await navigator.serviceWorker.register('/sw.js');
        await navigator.serviceWorker.ready;
        subn = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64(key) });
        const j = subn.toJSON();
        await UI.api('/push/subscribe', { method: 'POST', body: { endpoint: j.endpoint, keys: j.keys, kinds } });
        drawKinds();
        UI.toast('Notifications on for this device');
      } catch (e) {
        subn = null; note.textContent = 'Couldn’t turn them on here. Try again, or use Add to calendar.'; note.hidden = false; throw e;
      }
    }
    const main = h('div', { class: 'pref-ctl' });
    const sw = UI.switch(main, { checked: !!subn, label: 'Notify me on this device', onChange: async on => {
      note.hidden = true;
      if (on) return enable();
      if (subn) { await UI.api('/push/subscribe', { method: 'DELETE', body: { endpoint: subn.endpoint } }).catch(() => null); await subn.unsubscribe().catch(() => null); }
      subn = null; drawKinds();
    } });
    host.append(h('div', { class: 'pref' }, h('span', { class: 'pref-k', text: 'Notify me on this device' }),
      h('p', { class: 'help', text: 'A nudge that says what’s due, from this browser. Quiet hours below hold back only the extra ones.' }), main), note, kindsBox);
    drawKinds();
    // the one offer, right after a study time is set (U18b); never on load
    offerNudge = time => {
      if (subn || !time || ls.get('satf.push.offered', 0)) return;
      ls.set('satf.push.offered', 1);
      UI.toast(`Want a nudge at ${time}?`, { ms: 8000, action: { label: 'Notify me', onClick: () => enable().then(() => sw.set(true), () => {}) } });
    };
  }
  let offerNudge = () => {};
  UI.api('/prefs').then(prefRows, () => prefRows(null));

  /* ================================================================ Study: the plan line and the calendar (U18a) */
  function paintStudyPlan() {
    const host = studyBody().querySelector('#study-plan');
    if (!host || !P) return;
    const p = P, pr = UI.prefs.now() || {};
    const bits = [p.exam_date && UI.date(p.exam_date, 'short'), p.target && String(p.target), p.minutes && `${p.minutes} min`, p.days && daysText(p.days)].filter(Boolean);
    host.replaceChildren(
      h('div', { class: 'acts' }, h('span', { class: 'grow', text: p.plan ? bits.join(' · ') || 'Your plan' : 'No plan yet.' }),
        btn(p.plan ? 'Edit plan' : 'Build a plan', { quiet: !!p.plan, href: '/plan/' })),
      h('div', { class: 'acts mt' }, p.plan
        ? btn('Add to calendar', { onClick: () => calendarSheet(p, pr) })
        : h('p', { class: 'soft', text: 'Build a plan first: the calendar follows your study days.' })));
  }
  const DAYS = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
  function daysText(days) {
    const n = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const on = days.split('').map((c, i) => (c === '1' ? i : -1)).filter(i => i >= 0);
    if (on.length === 7) return 'every day';
    return on.length > 2 && on[on.length - 1] - on[0] === on.length - 1 ? `${n[on[0]]}–${n[on[on.length - 1]]}` : on.map(i => n[i]).join(', ');
  }
  function nextStudy(p, time) {
    const [hh, mm] = (time || '19:00').split(':').map(Number);
    const d = new Date();
    for (let i = 0; i < 8; i++) {
      const c = new Date(d.getFullYear(), d.getMonth(), d.getDate() + i, hh, mm);
      if (c > d && (!p.days || p.days[(c.getDay() + 6) % 7] === '1')) return c;
    }
    return new Date(d.getTime() + 864e5);
  }
  const stamp = d => `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}${String(d.getMinutes()).padStart(2, '0')}00`;
  function download(name, text, type) {
    const a = h('a', { href: URL.createObjectURL(new Blob([text], { type })), download: name });
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }
  function calendarSheet(p, pr) {
    const start = nextStudy(p, pr.study_time);
    const mins = p.minutes || 30;
    const end = new Date(start.getTime() + mins * 60000);
    const byday = p.days ? DAYS.filter((_, i) => p.days[i] === '1').join(',') : DAYS.join(',');
    const tz = (() => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (_) { return ''; } })();
    const google = 'https://calendar.google.com/calendar/render?' + new URLSearchParams({ action: 'TEMPLATE', text: `SAT · Up next · ${mins} min`,
      dates: `${stamp(start)}/${stamp(end)}`, ctz: tz, details: `Open to see what's due now: ${location.origin}/?next=1`,
      recur: `RRULE:FREQ=WEEKLY;BYDAY=${byday}${p.exam_date ? `;UNTIL=${p.exam_date.replace(/-/g, '')}T235959Z` : ''}` });
    const pid = typeof p.plan === 'string' ? p.plan : p.plan && p.plan.id;
    let tab = 'google';
    UI.sheet({ title: 'Add to calendar', size: 'm', body: b => {
      const panel = h('div', { class: 'gap' });
      const tabsHost = h('div');
      const draw = () => {
        if (tab === 'google') panel.replaceChildren(
          h('p', { text: 'A recurring event on your study days, so your own Google notifications apply.' }),
          h('a', { class: 'pill sm', href: google, target: '_blank', rel: 'noopener', text: 'Add to Google Calendar' }),
          h('p', { class: 'help', text: 'Or subscribe to the feed below, then in Google Calendar: Settings › this calendar › Event notifications › Add notification.' }));
        else if (tab === 'apple') panel.replaceChildren(
          h('p', { text: 'Subscribe, and in the dialog untick Remove Alerts so the reminders ring.' }),
          btn('Subscribe', { primary: true, onClick: () => subscribe(pid) }),
          h('p', { class: 'help', text: 'Or download one recurring event with its alert: an imported event keeps it.' }),
          btn('Download .ics', { onClick: () => downloadPlan(p, pr, start, mins, byday) }));
        else panel.replaceChildren(
          h('p', { text: 'Download the recurring event: imported events keep their alert. Or subscribe and add a reminder in the calendar’s own settings.' }),
          h('div', { class: 'acts' }, btn('Download .ics', { primary: true, onClick: () => downloadPlan(p, pr, start, mins, byday) }),
            btn('Copy the feed link', { onClick: () => subscribe(pid, true) })));
        panel.append(h('div', { class: 'acts mt' }, btn('Test it: an event 2 minutes from now', { quiet: true, onClick: () => {
          const t = new Date(Date.now() + 2 * 60000);
          download('sat-freshman-test.ics', UI.ics({ title: 'SAT Freshman · test reminder', start: t, minutes: 5, alarm: 0 }), 'text/calendar');
        } })));
      };
      UI.tabs(tabsHost, [{ id: 'google', label: 'Google' }, { id: 'apple', label: 'Apple' }, { id: 'other', label: 'Outlook and others' }],
        { value: tab, label: 'Calendar', onChange: v => { tab = v; draw(); } });
      draw();
      b.append(tabsHost, panel);
    } });
  }
  async function downloadPlan(p, pr, start, mins, byday) {
    try {
      const r = await fetch('/api/plan/ics', { headers: { 'X-Learner': UI.learner(), 'X-Tz': String(new Date().getTimezoneOffset()) } });
      if (!r.ok) throw new Error(String(r.status));
      download('sat-freshman-plan.ics', await r.text(), 'text/calendar');
    } catch (_) {
      download('sat-freshman-plan.ics', UI.ics({ title: `SAT · Up next · ${mins} min`, start, minutes: mins, repeat: 'weekly', byday: byday.split(','),
        until: p.exam_date || null, url: `${location.origin}/?next=1`, description: 'Open to see what’s due now.', alarm: pr.remind ?? 10 }), 'text/calendar');
    }
  }
  async function subscribe(pid, copy) {
    try {
      const r = await UI.api(`/plan/${encodeURIComponent(pid)}/links`, { method: 'POST', body: { cal: true } });
      const url = `${location.host}${r.cal}`;
      if (copy) { UI.copyText(`${location.protocol}//${url}`, { toast: 'Feed link copied' }); return; }
      location.href = `webcal://${url}`;
    } catch (e) { UI.toast(errText(e, 'Couldn’t make the feed. Try Download instead.')); }
  }

  /* ================================================================ Account & devices (Shell 4.4, U11, U19, U20, U21, U29) */
  const acc = $('account');
  // email is the only way in (2026-10-20): no Google, passkey, phone or transfer-code blocks
  const blocks = { boards: h('div'), email: h('div'), devices: h('div', { id: 'devices' }), family: h('div'), out: h('div') };
  acc.replaceChildren(...Object.values(blocks));
  blocks.devices.style.scrollMarginTop = '72px';
  let ACC = null, DEV = null;
  async function loadAccount() {
    try {
      [ACC, DEV] = await Promise.all([UI.api('/account'), UI.api('/devices').catch(() => null)]);
      paintEmail(); paintDevices(); paintFamily(); paintOut();
      const w = ways();
      idxSay('account', ACC && ACC.saved ? ['Saved', w.length ? `${pl(w.length, 'way')} to sign in` : null].filter(Boolean).join(' · ') : 'This device only');
    } catch (e) {
      if (e && e.retired) return;
      blocks.email.replaceChildren(UI.cardError(null, loadAccount));
    }
  }
  const ways = () => [ACC && ACC.verified ? 'email' : null].filter(Boolean);

  function paintBoards() {
    const b = blocks.boards, p = P;
    if (!p) return;
    b.replaceChildren();
    sub(b, 'Boards');
    // Save says Saving, then Saved, in place (UI.saving announces it); the row stays, so nothing jumps
    const field = (label, value, max, save, rule, after) => {
      const f = h('input', { class: 'field', value: value || '', maxlength: String(max), 'aria-label': label });
      const e = h('p', { class: 'field-err', role: 'alert', hidden: true });
      const go = h('button', { type: 'button', class: 'btn sm', text: 'Save' });
      go.addEventListener('click', () => {
        const v = f.value.trim();
        const bad = rule(v);
        if (bad) { e.textContent = bad; e.hidden = false; return; }
        e.hidden = true;
        UI.saving(go, () => save(v)).then(r => { P = r; if (after) after(r); },
          x => { e.textContent = label === 'Your name' ? A.nameError(x) : A.handleError(x); e.hidden = false; });
      });
      f.addEventListener('keydown', ev => { if (ev.key === 'Enter') go.click(); });
      return h('label', { class: 'fieldrow' }, h('span', { class: 'pref-k', text: label }), h('span', { class: 'acts' }, f, go), e);
    };
    b.append(field('Your name', p.name, 40, v => A.saveMe({ name: v || null }), v => (v && !A.NAME_OK.test(v) ? 'Names can’t contain digits, @, < or >.' : '')));
    help(b, 'Shown only to you: your profile, the menu, your emails and progress links you share.');
    const shows = r => (r.handle ? `Boards, contests and ranks show ${r.handle}.` : 'Boards show a student number until you choose one.');
    b.append(field('Board name', p.handle, 24, v => A.saveMe({ handle: v }), v => (A.HANDLE_OK.test(v) ? '' : A.handleError({ status: 422 })),
      r => { handleHelp.textContent = shows(r); }));
    const handleHelp = h('p', { class: 'help', text: shows(p) });
    b.append(handleHelp);
    const vis = h('div', { class: 'pref' }, h('span', { class: 'pref-k', text: 'Show me on boards' }));
    const segHost = h('div', { class: 'pref-ctl' });
    UI.seg(segHost, [{ value: 'name', label: 'With my board name' }, { value: 'anon', label: 'Anonymously' }, { value: 'hidden', label: 'Don’t list me' }],
      { value: p.board || 'name', label: 'Show me on boards', onChange: async v => {
        try { P = await A.saveMe({ board: v }); UI.toast('Saved'); } catch (e) { UI.toast(errText(e, 'Not saved. Try again.')); }
      } });
    vis.append(segHost);
    b.append(vis);
    help(b, 'Anonymous shows a student number. Unlisted still shows you your own rank. It applies to the challenge boards and the practice ranks.');
    const country = h('div', { class: 'pref' }, h('span', { class: 'pref-k', text: 'Country' }),
      h('div', { class: 'pref-ctl' }, A.countrySelect(p.country || '', async v => {
        try { P = await A.saveMe({ country: v }); UI.toast(v ? `Country: ${A.countryName(v)}` : 'Country cleared'); }
        catch (e) { UI.toast(errText(e, 'Not saved. Try again.')); throw e; }
      })));
    b.append(country);
    help(b, 'Only for the Country board. We never detect where you are.');
    b.append(h('p', { class: 'help' }, 'Avatar and photo: ', h('a', { class: 'link', href: '/me/#you', text: 'change them on your profile' }), '.'));
  }

  /* ---- email (2026-10-20): the one way to sign in. A learner from before the switch adds an address here,
     with no code (prod sends no mail): account.beta_account links it to this progress */
  function paintEmail() {
    const b = blocks.email;
    b.replaceChildren();
    sub(b, 'Email');
    if (ACC && ACC.verified) {
      b.append(h('p', {}, h('span', { class: 'chk', 'aria-hidden': 'true', text: '✓' }), `You sign in with ${ACC.email_masked || ACC.email}`,
        ACC.since ? h('span', { class: 'soft', text: ` · since ${day(ACC.since)}` }) : null));
      return;
    }
    b.append(h('p', { text: 'Add your email. It’s how you sign in now, on this device and any other.' }));
    const f = h('input', { class: 'field', type: 'email', autocomplete: 'email', inputmode: 'email', spellcheck: 'false', 'aria-label': 'Email' });
    const e = h('p', { class: 'field-err', role: 'alert', hidden: true });
    const save = btn('Save', { primary: true, onClick: async () => {
      const email = f.value.trim();
      if (!email || !f.checkValidity()) { e.textContent = 'That email doesn’t look right.'; e.hidden = false; return; }
      try {
        const res = await UI.api('/account/beta', { method: 'POST', body: { email } });
        await A.finish(res, { method: 'email', to: '/me/settings/#account', local: await A.localAnswers() });
      } catch (x) { e.textContent = x.status === 429 ? 'Too many tries. Wait a while.' : errText(x, 'Couldn’t save it. Try again.'); e.hidden = false; }
    } });
    f.addEventListener('keydown', ev => { if (ev.key === 'Enter') save.click(); });
    b.append(h('div', { class: 'acts mt' }, f, save), e);
  }

  /* ---- devices (U21) */
  function paintDevices() {
    const b = blocks.devices;
    b.replaceChildren();
    sub(b, 'Devices');
    const live = ((DEV && DEV.items) || []).filter(d => !d.revoked);
    if (!live.length) {
      b.append(h('p', { class: 'soft', text: ACC && ACC.saved ? 'Only this browser.' : 'Once your progress is saved, every browser signed in to it is listed here, and each can be signed out.' }));
    }
    live.forEach(d => {
      const bits = [d.this && 'this device', d.session_only && 'shared computer',
        d.this ? 'active now' : d.last_seen && UI.relTime(d.last_seen),
        d.method === 'swap' ? `moved to its own key ${day(d.created)}` : `signed in ${day(d.created)}${d.method ? ` by ${{ email: 'email', passkey: 'passkey', phone: 'phone', transfer: 'transfer code', save: 'saving', google: 'Google' }[d.method] || d.method}` : ''}`];
      b.append(h('div', { class: 'dev' }, h('span', { class: 't', text: d.label || 'Browser' }),
        btn('Sign out', { quiet: true, onClick: async () => {
          if (d.this) { UI.signOut(); return; }
          try { await UI.api(`/devices/${encodeURIComponent(d.id)}`, { method: 'DELETE' }); UI.toast(`${d.label || 'That device'} signed out`); loadAccount(); }
          catch (e) { UI.toast(errText(e, 'Couldn’t sign it out. Try again.')); }
        } }),
        h('span', { class: 'd', text: bits.filter(Boolean).join(' · ') })));
    });
    if (DEV && DEV.old_code_until && new Date(DEV.old_code_until) > new Date()) {
      b.append(h('p', { class: 'help', text: `Your old code still works until ${day(DEV.old_code_until)} for browsers that haven’t visited since you saved. Sign out all other devices ends it now.` }));
    }
    if (live.filter(d => !d.this).length || (DEV && DEV.old_code_until && new Date(DEV.old_code_until) > new Date())) {
      b.append(h('div', { class: 'acts mt' }, btn('Sign out all other devices', { onClick: async () => {
        const ok = await UI.confirm({ title: 'Sign out all other devices?', text: 'Other devices will need to sign in again.', confirm: 'Sign them out', destructive: true });
        if (!ok) return;
        try { await UI.api('/devices/signout-others', { method: 'POST' }); UI.toast('Other devices signed out'); loadAccount(); }
        catch (e) { UI.toast(errText(e, 'Couldn’t sign them out. Try again.')); }
      } })));
    }
  }

  /* ---- a family device (U21): off by default, never on a shared computer */
  function paintFamily() {
    const b = blocks.family;
    b.replaceChildren();
    if (UI.shared()) return;
    sub(b, 'This is a family device');
    const row = h('div', { class: 'pref' }, h('span', { class: 'pref-k', text: 'Let other students use this browser' }));
    const ctl = h('div', { class: 'pref-ctl' });
    UI.switch(ctl, { checked: !!ls.get('satf.family', 0), ariaLabel: 'This is a family device', onChange: async on => {
      if (on) {
        const ok = await UI.confirm({ title: 'Let other students use this browser?', text: 'Each keeps their own progress, and anyone here can switch to them from the menu.', confirm: 'Turn on' });
        if (!ok) throw new Error('cancelled');
        ls.set('satf.family', 1);
        UI.toast('Students on this device is in the menu now');
        return;
      }
      const me = UI.learner();
      const others = ls.get('satf.profiles', []).filter(p => p.cred !== me && !p.parked);
      const unsaved = others.filter(p => !/^d:/.test(p.cred));
      if (others.length) {
        const ok = await UI.confirm({ title: 'Turn off the family device?', confirm: 'Turn off', destructive: true,
          text: `${pl(others.length, 'other student')} will be signed out here.${unsaved.length ? ` ${unsaved.map(p => p.name).join(', ')} ${unsaved.length === 1 ? 'isn’t' : 'aren’t'} saved: this device forgets that progress.` : ''}` });
        if (!ok) throw new Error('cancelled');
      }
      others.forEach(p => { if (/^d:/.test(p.cred)) { try { fetch('/api/devices/this', { method: 'DELETE', keepalive: true, headers: { 'X-Learner': p.cred } }); } catch (_) {} } });
      ls.set('satf.profiles', ls.get('satf.profiles', []).filter(p => p.cred === me || p.parked));
      ls.set('satf.family', null);
      UI.toast('Family device turned off');
    } });
    row.append(ctl);
    b.append(row);
    help(b, 'When on, the menu lists up to four students on this device, each with their own progress.');
  }

  function paintOut() {
    const b = blocks.out;
    b.replaceChildren();
    sub(b, 'This device');
    b.append(h('div', { class: 'acts' },
      ACC && ACC.saved ? null : btn('Sign in', { href: '/signin/' }),
      btn([h('span', { class: 'ic', 'aria-hidden': 'true', html: UI.svg(UI.ICON.signout, 16) }), ACC && ACC.saved ? ' Sign out of this device' : ' Leave this device…'],
        { quiet: true, onClick: () => UI.signOut() })));
    if (UI.shared()) help(b, 'Shared computer: this ends 15 minutes after you stop, or about a minute after you close the browser.');
  }
  paintBoards();
  loadAccount();

  /* ================================================================ Your reports (Shell 4.5, U3) */
  async function loadReports() {
    const b = $('reports');
    b.replaceChildren(UI.skel(null, 'rows:3'));
    try {
      const list = await UI.api('/reports');
      if (!list.length) { b.replaceChildren(h('p', { class: 'soft', text: 'No reports yet. Use Report on any question, or Send feedback.' })); return; }
      const fresh = list.filter(r => r.unread).length;
      idxSay('reports', fresh ? `${pl(fresh, 'new reply', 'new replies')}` : pl(list.length, 'report'));
      b.replaceChildren(...list.map(r => h('div', { class: 'rep' },
        h('p', { class: 't' }, r.unread ? h('span', { class: 'odot', 'aria-label': 'New reply' }) : null, `#${r.id}`, h('span', { text: r.category_label || r.category }),
          r.context_chip ? h('span', { class: 'badge soft', text: r.context_chip }) : null, h('span', { class: 'badge', text: r.status_label || r.status })),
        h('p', { class: 'meta', text: r.date || day(r.at) }),
        r.title ? h('p', { text: r.title }) : null,
        r.outcome_text ? h('p', { class: 'help', text: r.outcome_text }) : null,
        r.reply ? h('details', { open: r.unread ? '' : null }, h('summary', { text: `Our reply${r.replied_date ? ` · ${r.replied_date}` : ''}` }), h('p', { text: r.reply })) : null)),
        h('p', { class: 'help' }, 'Fixes are listed at ', h('a', { class: 'link', href: '/help/#fixed', text: 'Help › Fixed from your reports' }), '.'));
      if (list.some(r => r.unread)) UI.whenVisible(() => UI.api('/reports/seen', { method: 'POST', quiet: true }).then(() => UI.refresh(), () => {}));
    } catch (e) { if (!e || !e.retired) b.replaceChildren(UI.cardError(null, loadReports)); }
  }
  loadReports();

  /* ================================================================ Privacy & data (Shell 4.6, R18a) */
  async function loadPrivacy() {
    const b = $('privacy');
    const links = h('div');
    const fam = h('div');
    b.replaceChildren(h('h3', { class: 'sub-h', text: 'Parents' }),
      h('p', { class: 'help set-intro', text: 'Invite a parent with a link. They sign in with their own email and see a short summary: how much you practise, your score trend, strengths and what needs work. They can’t change anything, and you can remove them any time.' }), fam,
      h('h3', { class: 'sub-h', text: 'Share with a tutor' }),
      h('p', { class: 'help set-intro', text: 'They see your stats, skills, score trend, activity and open mistakes. Never your email or device code.' }), links,
      h('h3', { class: 'sub-h', text: 'Your data' }),
      h('div', { class: 'acts' }, btn('Download my data', { onClick: exportData }), btn('Delete everything…', { quiet: true, onClick: deleteAll })));
    const draw = list => {
      links.replaceChildren(...list.map(l => {
        const url = `${location.origin}/share/?t=${encodeURIComponent(l.token)}`;
        return h('div', { class: 'dev' }, h('span', { class: 't', text: `Link created ${day(l.created)}` }),
          h('span', { class: 'acts' }, btn('Copy', { quiet: true, onClick: (e, b) => copyIn(b, url) }),
            btn('Turn off', { quiet: true, onClick: async () => {
              try { await UI.api(`/share/${encodeURIComponent(l.token)}`, { method: 'DELETE' }); UI.toast('Link turned off'); refresh(); }
              catch (e) { UI.toast(errText(e, 'Couldn’t turn it off. Try again.')); }
            } })),
          h('span', { class: 'd', text: l.views ? `Viewed ${pl(l.views, 'time')}${l.last_view ? `, last ${day(l.last_view)}` : ''}` : 'Not viewed yet' }));
      }), h('div', { class: 'acts mt' }, btn(list.length ? 'Create another link' : 'Create a link', { onClick: async () => {
        try { const r = await UI.api('/share', { method: 'POST' }); UI.copyText(`${location.origin}${r.url}`, { toast: 'Link created and copied' }); refresh(); }
        catch (e) { UI.toast(errText(e, 'Couldn’t make a link. Try again.')); }
      } })));
    };
    const refresh = () => UI.api('/share').then(draw, e => { if (!e || !e.retired) links.replaceChildren(UI.cardError(null, refresh)); });
    refresh();

    const drawFam = g => {
      const full = u => `${location.origin}${u}`;
      fam.replaceChildren(
        ...g.parents.map(p => h('div', { class: 'dev' }, h('span', { class: 't', text: p.name || 'A parent' }),
          h('span', { class: 'acts' }, btn('Remove', { quiet: true, onClick: async () => {
            try { await UI.api(`/guardians/${encodeURIComponent(p.id)}`, { method: 'DELETE' }); UI.toast('Parent removed'); loadFam(); }
            catch (e) { UI.toast(errText(e, 'Couldn’t remove them. Try again.')); }
          } })), h('span', { class: 'd', text: `Following you since ${day(p.since)}` }))),
        ...g.invites.map(i => h('div', { class: 'dev' }, h('span', { class: 't', text: 'Invite not used yet' }),
          h('span', { class: 'acts' }, btn('Copy link', { quiet: true, onClick: (e, b) => copyIn(b, full(i.url)) }),
            btn('Cancel', { quiet: true, onClick: async () => {
              try { await UI.api(`/guardians/invites/${encodeURIComponent(i.code)}`, { method: 'DELETE' }); loadFam(); }
              catch (e) { UI.toast(errText(e, 'Couldn’t cancel it. Try again.')); }
            } })), h('span', { class: 'd', text: `Works until ${day(i.expires)}, for one parent` }))),
        h('div', { class: 'acts mt' }, btn('Invite a parent', { onClick: async () => {
          try { const r = await UI.api('/guardians/invite', { method: 'POST' }); UI.copyText(full(r.url), { toast: 'Invite link copied. Send it to your parent' }); loadFam(); }
          catch (e) { UI.toast(errText(e, 'Couldn’t make an invite. Try again.')); }
        } })));
    };
    const loadFam = () => UI.api('/guardians').then(drawFam, e => { if (!e || !e.retired) fam.replaceChildren(UI.cardError(null, loadFam)); });
    loadFam();
  }
  async function exportData() {
    try {
      const d = await UI.api('/me/export');
      const now = new Date();
      download(`sat-freshman-${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}.json`,
        JSON.stringify(d, null, 2), 'application/json');
    } catch (e) { UI.toast(errText(e, 'Couldn’t download it. Try again.')); }
  }
  async function deleteAll() {
    const typed = await UI.confirm({ title: 'Delete everything?', destructive: true, confirm: 'Delete everything',
      text: 'This deletes your answers, mistakes, saved questions, sittings, plan, email link, passkeys, devices, share links and reports. Your past challenge results stay on the boards as an anonymous student.',
      input: { label: 'Type DELETE to confirm', value: '' } });
    if (typed === null || typed === false || typed === undefined) return;
    if (String(typed).trim() !== 'DELETE') { UI.toast('Nothing deleted: type DELETE to confirm.'); return; }
    try {
      await UI.api('/me', { method: 'DELETE', body: { confirm: 'DELETE' } });
      UI.cached.clear();
      UI.freshLearner();
      A.flash('Deleted');
      location.href = '/';
    } catch (e) { UI.toast(errText(e, 'Nothing was deleted. Try again.')); }
  }
  loadPrivacy();

  // a deep link (#devices, #study) lands on its section once the rows are in
  if (location.hash) setTimeout(() => { const el = document.getElementById(location.hash.slice(1)); if (el) el.scrollIntoView({ block: 'start' }); }, 400);
})();
