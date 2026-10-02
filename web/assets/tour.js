/* ============================================================================
   SAT Freshman -- the first-visit page tour (loaded on first use by UI.shell)

   UI.tour.start(page, { force })   walk the page's steps; remembered per page in localStorage
                                    satf.tour.<page> once finished or skipped
   UI.tour.has(page)                does this page have a tour
   A step is { sel, title, text, try?: { label, sel } }: sel is a selector or a list of selectors
   (the first one that is on screen wins). A step whose target is not on screen is left out, so a
   new account that has no sittings yet simply gets a shorter tour. Skip, Esc and the end all set the
   "seen" mark; "Show this page's tour" in the account menu runs it again.
   ============================================================================ */
(() => {
  'use strict';
  const doc = document, h = UI.h;
  const KEY = p => `satf.tour.${p}`;
  const get = k => { try { return localStorage.getItem(k); } catch (_) { return null; } };
  const set = k => { try { localStorage.setItem(k, '1'); } catch (_) {} };

  const TOURS = {
    today: [
      { sel: '#next', title: 'Up next', text: 'The best next thing for you today. Tap Start and the app chooses the questions.' },
      { sel: '#due', title: 'Due today', text: 'Mistakes and saved questions that are ready to look at again. A few minutes here stops old mistakes coming back.' },
      { sel: '#qotd', title: 'Question of the day', text: 'One question a day, the same for everyone. Answer it to keep your streak going.' },
      { sel: '#gain', title: 'Points on the table', text: 'Shows which skills would raise your score the most. It fills in after about 30 answers.' },
      { sel: ['#bar .side-item[data-id="practice"]', '#tabs [data-id="practice"]', '#tabs a'], title: 'Your menu', text: 'Practice builds your own sets, Review fixes mistakes, Words trains vocabulary, Tests gives full tests and Plan schedules your days.' },
    ],
    practice: [
      { sel: '#searchSec', title: 'Type a set', text: 'Describe what you want, like “circles hard 10 in 15 min”, and press Enter.' },
      { sel: '#presetSec', title: 'Presets', text: 'Ready-made starting points. Open this to pick one, or save your own.' },
      { sel: ['#tree', '#grid'], title: 'Pick your skills', text: 'Tick the skills you want to practise. Each row is a skill, and it opens to show its question types.' },
      { sel: '#abar', title: 'Start', text: 'Start opens the options (how many questions, timing, feedback), then you begin.' },
    ],
    tests: [
      { sel: '#score', title: 'Your estimated score', text: 'A range based on your recent tests. The more full sections you sit, the narrower and more reliable it gets.' },
      { sel: '#next', title: 'Up next', text: 'The test the app suggests for you right now.' },
      { sel: '#kinds', title: 'New test', text: 'Pick a full section, one module, a custom test or the diagnostic. The ⋯ on each card holds more options.' },
      { sel: '#papers', title: 'Papers', text: 'A new paper arrives every Monday. Everyone gets the same question types, with their own numbers.' },
      { sel: '#sittings', title: 'Your sittings', text: 'Every test you have taken. Review it, fix what you missed, or tick two to compare.' },
      { sel: '#habits', title: 'How you take tests', text: 'Habits such as pacing, blanks and answer changes, and what each one costs you.' },
    ],
    plan: [
      { sel: '.pl-hero', title: 'Your study plan', text: 'Answer four short questions (your score, target and exam date) and the app builds a day-by-day plan for you.' },
      { sel: '.pl-how', title: 'How it works', text: 'Each day has a few tasks that fit your time. If you miss one, the plan moves things around for you.' },
      { sel: '.pl-tiles', title: 'At a glance', text: 'Days to the exam, your score goal, days studied and this week’s time.' },
      { sel: '.pl-tabbar', title: 'Plan, Progress, Plans', text: 'Plan is your schedule. Progress shows how you are tracking. Plans holds your other plans.' },
      { sel: ['#plan .trows', '#plan .pl-day-go'], title: 'Today’s tasks', text: 'Tick tasks off or tap Start. The ⋯ on a task lets you skip or move it.' },
      { sel: '#plan .cal', title: 'Calendar', text: 'The whole plan on one page. Tap a day to see its tasks.' },
    ],
    review: [
      { sel: '#start', title: 'Start a review', text: 'Choose how many minutes you have, then Start. What is due comes first.' },
      { sel: ['#rhtabs', '.rh-tabs'], title: 'Your lists', text: 'Due today, Redo (open mistakes), Marked, Saved, History and Fixed. Tap one to open it.' },
      { sel: '#list', title: 'The list', text: 'Tap a row to look at the question. Tick rows to practise several at once.' },
    ],
    words: [
      { sel: '#today', title: 'Today’s words', text: 'Start mixes reviews and new words. Or pick Review cards, Learn or Quiz.' },
      { sel: '#wtabs', title: 'Four views', text: 'Library holds every word. Flashcards and Quiz are practice modes. My words is what you have touched.' },
      { sel: '#colls', title: 'Collections', text: 'Open this to browse sets like SAT core, Transitions and Roots.' },
      { sel: '#fbar', title: 'Search and filters', text: 'Find a word, or narrow the list by topic, difficulty or status.' },
      { sel: '#gridSec', title: 'The word grid', text: 'Tap a word for its meaning and examples. The gear beside the filters holds Meanings and Select.' },
    ],
    results: [
      { sel: '#estimate', title: 'Your score estimate', text: 'Where you stand now, and how far you are from your target.' },
      { sel: '#overview', title: 'Score over time', text: 'Each point is a test. Tap one to open its report.' },
      { sel: '#sittings', title: 'Every sitting', text: 'Tests and practice sets. Review one, Fix what you missed, or open the Peek.' },
      { sel: '#traps', title: 'Mistakes you make most', text: 'The wrong ideas behind your misses. Fix them one at a time, or all at once.' },
      { sel: '#skills', title: 'Every skill', text: 'Tap a skill to see its stats and practise it.' },
    ],
    compete: [
      { sel: '#daily', title: 'Daily Challenge', text: 'Ten questions, the same for everyone today. Your score goes on the board.' },
      { sel: '#contests', title: 'Contests', text: 'Tap a contest to see its details and start it. Each one has a live timer.' },
      { sel: '#join-create', title: 'Create or join', text: 'Make a private contest for friends, or join one with a code.' },
      { sel: '#rivals', title: 'Rivals', text: 'People you have played against. Race replays their run on today’s Daily.' },
      { sel: '#badges', title: 'Next badges', text: 'Earn badges by playing. Go takes you straight to the next one.' },
    ],
    me: [
      { sel: '#you', title: 'You', text: 'Your name, board name, goal and exam date.' },
      { sel: '#skills', title: 'Skills', text: 'How strong you are in each skill, and which ones would earn you the most points.' },
      { sel: '#readiness', title: 'Test-day readiness', text: 'How much of the test you are ready for. Open a domain to see each question type.' },
      { sel: '#badges', title: 'Achievements', text: 'Badges you have earned and the ones that are next.' },
    ],
  };

  const phone = () => matchMedia('(max-width: 759px)').matches;
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  const onScreen = e => {
    if (!e || !e.isConnected) return false;
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 12 && r.height > 12 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('[hidden], [inert]');
  };
  const find = sel => { for (const s of [].concat(sel)) { const e = doc.querySelector(s); if (onScreen(e)) return e; } return null; };

  const CSS = `
.tour-catch { position: fixed; inset: 0; z-index: 9990; background: transparent; }
.tour-ring { position: fixed; z-index: 9991; pointer-events: none; border-radius: 14px; box-shadow: 0 0 0 2px var(--amber, #F28C18), 0 0 0 9999px rgba(10, 10, 10, .5); transition: top .25s, left .25s, width .25s, height .25s; }
.tour-card { position: fixed; z-index: 9992; width: min(340px, calc(100vw - 24px)); box-sizing: border-box; padding: 16px 18px 14px; border-radius: 16px; background: var(--paper, #fff); color: var(--ink, #111); box-shadow: 0 12px 40px rgba(0, 0, 0, .35), inset 0 0 0 1px var(--line, rgba(0,0,0,.12)); outline: none; font: 400 14.5px/1.5 var(--font, system-ui, sans-serif); }
.tour-card h2 { margin: 0 0 6px; font: 700 17px/1.25 var(--font, system-ui, sans-serif); letter-spacing: -.01em; }
.tour-card p { margin: 0; color: var(--soft, #555); }
.tour-foot { display: flex; align-items: center; gap: 8px; margin-top: 14px; }
.tour-dots { display: flex; gap: 5px; margin-right: auto; }
.tour-dots i { width: 6px; height: 6px; border-radius: 50%; background: var(--faint, #bbb); }
.tour-dots i.on { background: var(--amber, #F28C18); width: 16px; border-radius: 3px; }
.tour-card .tour-skip { margin-right: 4px; }
.tour-chip { position: fixed; z-index: 9992; left: 50%; bottom: 20px; transform: translateX(-50%); display: flex; gap: 6px; align-items: center; padding: 6px 8px 6px 14px; border-radius: 999px; background: var(--ink, #111); color: var(--on-ink, #fff); font: 600 14px var(--font, system-ui, sans-serif); box-shadow: 0 8px 24px rgba(0, 0, 0, .35); }
.tour-chip button { appearance: none; border: 0; cursor: pointer; padding: 6px 14px; border-radius: 999px; background: var(--amber, #F28C18); color: var(--ink-deep, #111); font: 700 13.5px var(--font, system-ui, sans-serif); }
@media (max-width: 759px) { .tour-card { left: 12px !important; right: 12px; bottom: calc(12px + env(safe-area-inset-bottom, 0px)); top: auto !important; width: auto; } }
@media (prefers-reduced-motion: reduce) { .tour-ring { transition: none; } }
`;

  let live = null;   // the tour being shown

  function start(page, o = {}) {
    const steps = TOURS[page];
    if (!steps || live) return false;
    if (!o.force && get(KEY(page))) return false;
    const list = steps.map(s => ({ ...s, el: find(s.sel) })).filter(s => s.el);
    if (!list.length) return false;
    if (!doc.getElementById('tour-css')) doc.head.append(h('style', { id: 'tour-css', text: CSS }));
    const opener = doc.activeElement;
    const catcher = h('div', { class: 'tour-catch', 'aria-hidden': 'true' });
    const ring = h('div', { class: 'tour-ring', 'aria-hidden': 'true' });
    const card = h('div', { class: 'tour-card', role: 'dialog', 'aria-label': 'Page tour', tabindex: '-1' });
    doc.body.append(catcher, ring, card);
    let i = 0, chip = null;

    const finish = () => {
      set(KEY(page));
      [catcher, ring, card, chip].forEach(x => x && x.remove());
      removeEventListener('resize', place); removeEventListener('scroll', place, true); doc.removeEventListener('keydown', onKey, true);
      live = null;
      try { if (opener && opener.focus && opener.isConnected) opener.focus({ preventScroll: true }); } catch (_) {}
    };
    function place() {
      const s = list[i]; if (!s) return;
      const el = onScreen(s.el) ? s.el : find(s.sel);
      if (!el) return;
      s.el = el;
      const r = el.getBoundingClientRect(), pad = 6;
      Object.assign(ring.style, { top: `${r.top - pad}px`, left: `${r.left - pad}px`, width: `${r.width + pad * 2}px`, height: `${r.height + pad * 2}px` });
      if (phone()) return;
      const cw = card.offsetWidth || 340, ch = card.offsetHeight || 160, gap = 14;
      let top = r.bottom + gap, left = Math.min(Math.max(12, r.left), innerWidth - cw - 12);
      if (top + ch > innerHeight - 12) top = r.top - ch - gap;                       // not enough room below: above
      if (top < 12) { top = Math.min(innerHeight - ch - 12, Math.max(12, r.top + 16)); left = r.right + gap + cw < innerWidth ? r.right + gap : Math.max(12, r.left + 16); }   // tall target: beside or over it
      Object.assign(card.style, { top: `${Math.max(12, top)}px`, left: `${left}px` });
    }
    function show(n) {
      i = Math.max(0, Math.min(list.length - 1, n));
      const s = list[i];
      s.el.scrollIntoView({ block: phone() ? 'start' : 'center', behavior: reduced() ? 'auto' : 'smooth' });
      const last = i === list.length - 1;
      const btn = (label, cls, on) => { const b = h('button', { type: 'button', class: cls, text: label }); b.addEventListener('click', on); return b; };
      card.replaceChildren(
        h('h2', { text: s.title }), h('p', { text: s.text }),
        h('div', { class: 'tour-foot' },
          h('span', { class: 'tour-dots', 'aria-label': `Step ${i + 1} of ${list.length}` }, list.map((_, k) => h('i', { class: k === i ? 'on' : '' }))),
          last ? null : btn('Skip', 'quiet tour-skip', finish),
          i > 0 ? btn('Back', 'quiet', () => show(i - 1)) : null,
          s.try ? btn(s.try.label || 'Try it', 'btn sm', () => tryIt(s)) : null,
          btn(last ? 'Done' : 'Next', 'pill sm', () => (last ? finish() : show(i + 1)))));
      place(); setTimeout(place, reduced() ? 0 : 350);     // again once the scroll has settled
      card.focus({ preventScroll: true });
    }
    // Try it: hide the tour, let the real control do its thing, offer a way back
    function tryIt(s) {
      const t = find(s.try.sel || s.sel); if (t) t.click();
      [catcher, ring, card].forEach(x => { x.hidden = true; });
      chip = h('div', { class: 'tour-chip', role: 'status' }, 'Tour paused', h('button', { type: 'button', text: 'Back to the tour', onclick: () => { chip.remove(); chip = null; [catcher, ring, card].forEach(x => { x.hidden = false; }); show(i + 1 < list.length ? i + 1 : i); } }));
      doc.body.append(chip);
    }
    function onKey(e) {
      if (card.hidden) return;
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); finish(); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); i < list.length - 1 ? show(i + 1) : finish(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1); }
      else if (e.key === 'Tab') {   // keep Tab inside the card
        const f = [...card.querySelectorAll('button')]; if (!f.length) return;
        const at = f.indexOf(doc.activeElement);
        e.preventDefault(); f[(at + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus();
      }
    }
    addEventListener('resize', place); addEventListener('scroll', place, true); doc.addEventListener('keydown', onKey, true);
    live = { finish };
    show(0);
    return true;
  }

  // a page's first visit: wait for its cards to fill in (up to ~8 s), stay out of the way of sheets and dialogs
  function auto(page) {
    if (!TOURS[page] || get(KEY(page)) || new URLSearchParams(location.search).has('print')) return;
    let tries = 0;
    const attempt = () => {
      if (live || get(KEY(page))) return;
      const busy = doc.querySelector('dialog[open], .sheet[open], [role=dialog]:not(.tour-card)');
      if (!busy && start(page)) return;
      if (++tries < 8) setTimeout(attempt, busy ? 2500 : 1000);
    };
    setTimeout(attempt, 1800);
  }

  UI.tour = { start, auto, has: p => !!TOURS[p], seen: p => !!get(KEY(p)) };
  if (UI.__tourPage) auto(UI.__tourPage);
})();
