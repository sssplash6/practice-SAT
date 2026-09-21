/* ============================================================================
   SAT Freshman -- shell

   One source of truth for the rail, so six pages cannot drift apart. A page
   declares where it is with <body data-nav="mock"> and the rail renders
   itself around that.

   The drawn marks are hand-built rather than pulled from an icon set on
   purpose: the whole product is line art of physical objects, and no icon
   library carries a cassette, a record and a sticker sheet in one voice.
   ========================================================================== */

(() => {
  'use strict';

  /* ------------------------------------------------------------ the mark
     A rounded square with four gaps cut mid-edge. One corner piece, rotated
     four times, so the geometry is stated once. */
  const CORNER = 'M45 8 H30 A22 22 0 0 0 8 30 V45 H34 V41 A7 7 0 0 1 41 34 H45 Z';

  const mark = (size, fill = 'currentColor') => `
    <svg width="${size}" height="${size}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
      <g fill="${fill}">
        ${[0, 90, 180, 270].map(a =>
          `<path d="${CORNER}"${a ? ` transform="rotate(${a} 50 50)"` : ''}/>`).join('')}
      </g>
    </svg>`;

  /* ------------------------------------------------------------ nav marks
     18px, 1.5 stroke, drawn in the same voice as the object pages. */
  const S = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"';
  const icon = body => `<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${body}</svg>`;

  const ICONS = {
    overview:   icon(`<rect x="3.2" y="4.2" width="17.6" height="15.6" rx="2.4" ${S}/><path d="M3.2 9.4h17.6" ${S}/>`),
    diagnostic: icon(`<rect x="3.2" y="3.2" width="17.6" height="17.6" rx="4.6" ${S}/><rect x="9.6" y="9.6" width="4.8" height="4.8" rx="1.2" ${S}/>`),
    mock:       icon(`<rect x="2.6" y="5.6" width="18.8" height="12.8" rx="2.4" ${S}/><circle cx="9" cy="12" r="2.1" ${S}/><circle cx="15" cy="12" r="2.1" ${S}/>`),
    domain:     icon(`<circle cx="12" cy="12" r="8.8" ${S}/><circle cx="12" cy="12" r="3.4" ${S}/><circle cx="12" cy="12" r=".9" fill="currentColor"/>`),
    mixed:      icon(`<path d="M5 3.4h9.2L19 8.2v12.4H5z" ${S}/><path d="M14 3.6v4.8h4.8" ${S}/>`),
    duels:      icon(`<path d="M12 3.6v16.8" ${S}/><path d="M4.4 9.2 7.8 12l-3.4 2.8M19.6 9.2 16.2 12l3.4 2.8" ${S}/>`),
  };

  /* ------------------------------------------------------------ the rail */
  const NAV = [
    { id: 'overview',   href: 'overview',   label: 'Overview' },
    { id: 'diagnostic', href: 'diagnostic', label: 'Diagnostic', soon: true },
    { id: 'mock',       href: 'mock',       label: 'Mock tests' },
    { id: 'domain',     href: 'domain',     label: 'Domain practice' },
    { id: 'mixed',      href: 'mixed',      label: 'Mixed practice' },
    { id: 'duels',      href: 'duels',      label: 'Duels', soon: true },
  ];

  const SUBJECTS = [
    { id: 'math',    name: 'Math' },
    { id: 'verbal',  name: 'Reading and Writing' },
  ];

  /* rating -> level, per spec/rating.md: floor at 800, eight 150-wide bands,
     open top at 2001. */
  const levelOf = r =>
    r <= 800 ? 1 : r >= 2001 ? 10 : Math.min(9, 2 + Math.floor((r - 801) / 150));

  const PLAYER = { rating: 1120, placed: true };   // stand-in until there is a back end

  /* ---------------------------------------------------------- rendering */

  const root = () => {
    // pages sit one directory deep, except the overview at the web root
    const depth = document.body.dataset.nav === 'overview' ? '' : '../';
    return depth;
  };

  function railHTML(activeId, subject) {
    const r = root();
    const lvl = levelOf(PLAYER.rating);
    const other = SUBJECTS.find(s => s.id !== subject.id);

    const items = NAV.map(n => {
      const href = n.id === 'overview' ? `${r}index.html` : `${r}${n.href}/`;
      const on = n.id === activeId;
      return `<a href="${href}"${on ? ' aria-current="page"' : ''}${n.soon ? ' data-state="soon"' : ''}>
        ${ICONS[n.id]}<span>${n.label}</span>
      </a>`;
    }).join('');

    return `
      <a class="rail-brand" href="${r}index.html" aria-label="SAT Freshman, overview">
        ${mark(28, '#F18508')}
        <span class="rail-word"><span>SAT</span><span>Freshman</span></span>
      </a>

      <button class="subject" type="button" data-subject-toggle
              aria-label="Subject: ${subject.name}. Switch to ${other.name}.">
        <span>
          <span class="subject-k">Subject</span>
          <span class="subject-v" data-subject-name>${subject.name}</span>
        </span>
        <svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M4 8.5h13.5L14 5M20 15.5H6.5L10 19" ${S}/>
        </svg>
      </button>

      <nav class="nav" aria-label="Sections">
        <p class="nav-label">Practice</p>
        ${items}
      </nav>

      <div class="rail-foot">
        <div class="level">
          ${badgeHTML(lvl)}
          <span class="level-txt">
            <span class="level-n">Level ${lvl}</span>
            <span class="level-r">${PLAYER.rating} rating</span>
          </span>
        </div>
      </div>`;
  }

  /* the mark as the level badge: the ring fills in ten steps and the counter
     takes the digit. Progression is how much is filled, never a colour ramp. */
  function badgeHTML(level) {
    const y = 100 - level * 10;
    return `
      <svg class="level-badge" width="40" height="40" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
        <defs><clipPath id="lvlclip"><rect x="0" y="${y}" width="100" height="${100 - y}"/></clipPath></defs>
        <g fill="#E4E1DC">
          ${[0, 90, 180, 270].map(a => `<path d="${CORNER}"${a ? ` transform="rotate(${a} 50 50)"` : ''}/>`).join('')}
        </g>
        <g fill="#F18508" clip-path="url(#lvlclip)">
          ${[0, 90, 180, 270].map(a => `<path d="${CORNER}"${a ? ` transform="rotate(${a} 50 50)"` : ''}/>`).join('')}
        </g>
        <text x="50" y="51" text-anchor="middle" dominant-baseline="central"
              font-family="Archivo, sans-serif" font-weight="900" font-size="34" fill="#3F3F3F">${level}</text>
      </svg>`;
  }

  /* ---------------------------------------------------------- subject */

  const readSubject = () => {
    let id = 'math';
    try { id = localStorage.getItem('satf.subject') || 'math'; } catch (_) {}
    return SUBJECTS.find(s => s.id === id) || SUBJECTS[0];
  };

  const writeSubject = id => { try { localStorage.setItem('satf.subject', id); } catch (_) {} };

  function setSubject(next, announce) {
    const btn = document.querySelector('[data-subject-toggle]');
    const other = SUBJECTS.find(s => s.id !== next.id);
    if (btn) {
      btn.querySelector('[data-subject-name]').textContent = next.name;
      btn.setAttribute('aria-label', `Subject: ${next.name}. Switch to ${other.name}.`);
    }
    document.body.dataset.subject = next.id;
    document.querySelectorAll('[data-subject-echo]').forEach(el => { el.textContent = next.name; });
    writeSubject(next.id);
    if (announce) document.dispatchEvent(new CustomEvent('satf:subject', { detail: next }));
  }

  /* ---------------------------------------------------------- boot */

  function boot() {
    const rail = document.querySelector('.rail');
    if (!rail) return;

    const subject = readSubject();
    rail.innerHTML = railHTML(document.body.dataset.nav || '', subject);
    document.body.dataset.subject = subject.id;
    document.querySelectorAll('[data-subject-echo]').forEach(el => { el.textContent = subject.name; });

    rail.querySelector('[data-subject-toggle]').addEventListener('click', () => {
      const now = SUBJECTS.find(s => s.id === document.body.dataset.subject) || SUBJECTS[0];
      setSubject(SUBJECTS.find(s => s.id !== now.id), true);
    });

    // mobile: the rail is a panel, so it needs a way in and a way out
    const toggle = document.querySelector('.rail-toggle');
    if (toggle) {
      toggle.addEventListener('click', () => {
        const open = document.body.dataset.rail === 'open';
        document.body.dataset.rail = open ? '' : 'open';
        toggle.setAttribute('aria-expanded', String(!open));
      });
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && document.body.dataset.rail === 'open') {
          document.body.dataset.rail = '';
          toggle.setAttribute('aria-expanded', 'false');
          toggle.focus();
        }
      });
      rail.addEventListener('click', e => {
        if (e.target.closest('a')) document.body.dataset.rail = '';
      });
    }
  }

  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', boot)
    : boot();

  window.SATF = { levelOf, subject: readSubject, mark };
})();
