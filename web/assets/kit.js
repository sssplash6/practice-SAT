/* ============================================================================
   SAT Freshman -- the kit: overlays, controls, data views and formatters
   (spec/rebuild-v2.md 2.4 kit.js row, R18(b), R20, R35-R37; v2-upgrades G2, G5,
   G6, G11, G12, U8, U10, U17, U22, T6, T8, T12, SR15, SR16, SR25)

   Loaded after ui.js on every page; adds to window.UI with Object.assign and
   needs nothing from ui.js (UI.api, UI.learner and UI.glyph are used when present).
   The markup each component makes is the markup ui.css documents for it.

   A host argument may be null: the element is then returned for the caller to
   place. Components that take a host return an api object with .el.

   Overlays (native <dialog>, or popover="manual" in the top layer; anything opened
   from inside an open modal is mounted inside it, so it stays interactive)
     UI.sheet({title, body, actions, size, label, dismiss, guard, focus, onClose})
         -> {el, body, foot, close(value), closed: Promise, busy(on)}
         a bottom sheet under 760px (drag the handle down to close); Esc and the
         backdrop close it unless dismiss:false; guard() may refuse; focus returns
         actions: [{label, primary, ink, quiet, href, kbd, onClick(api) -> false keeps it open}]
     UI.sheet.top()                          the topmost open modal, or null
     UI.confirm({title, text, confirm, cancel, input, destructive}) -> Promise
         true | false, or the typed string | null when input is set ({label, value, ...})
     UI.pop(anchor | rect | Range | Selection, content, {role, label, anchored,
         className, onClose, focus, options, value, multi, onPick}) -> {el, close}
         role 'dialog' (default) or 'listbox' (content = options or [{group, options}])
         Esc and an outside click close it and focus returns; a second call on the
         same trigger closes it. Under 760px a bottom sheet unless anchored.
     UI.menu(trigger, items, {label, wide, align, last, onClose})    opens now (toggles)
     UI.menu.bind(trigger, items | () => items, opts)                wires click and arrows
         items: {label, icon, sub, kbd, meta, href, onClick, disabled, checked, radio,
                 close} | {separator: true} | {group: 'Label'} | {head: Node} | Node
         Up/Down, Home/End, letters, Enter/Space; Tab and Esc close and return focus
     UI.tooltip(el, text | fn, {kbd, delay}) -> {hide, set, destroy}   hover and focus
     UI.toast(text, {action, href, undo, ms, icon, wait}) -> {el, close}
         at most 3, polite; undo adds Undo (Z) for 6s; wait holds it while a sheet is open
     UI.toast.undo()                         runs the newest visible Undo (F2 binds Z)
     UI.banner(kind, text, actions, {host, dismiss, onDismiss, sys}) -> {close}
         one shows, by priority: retired, offline, storage, first, nudge, then others
     UI.banner.clear(kind)
   Controls
     UI.seg(host, options, {value, multi, onChange, label, full}) -> {el, help, value, set, count, disable}
     UI.chips(host, options, {...same})      radio chips; options: {value, label, n, disabled, why, icon}
     UI.tabs(host, tabs, {counts, value, onChange, label, param}) -> {el, value, set, count}
         tabs: {id, label, n, href, panel (Element | id), disabled}; arrows move and select
     UI.switch(host, {checked, label, onChange, disabled}) -> {el, value, set}
         onChange may return a Promise; a rejection flips it back
     UI.triCheck(host, {label, checked, mixed, n, onChange}) -> {el, input, set(true | false | 'mixed')}
     UI.dropdown(host, {label, options, groups, multi, counts, value, all, onChange, key, url, store})
         -> {el, value, set, counts, open}   a listbox (single) or checkboxes (multi)
     UI.filterBar(host, filters, {url, store, sheet, onChange}) -> {el, values, set, clear, counts}
         filters: {key, label, type: select | multi | pills | date | sort | search,
                   options, groups, value, counts}; "Filters · n" sheet under 760px
     UI.otp(host, onComplete, {length, label}) -> {el, value, clear, invalid, focus}
     UI.counter(field, max) -> el           "12/200", .near at 90%, .over past it
     UI.scoreSlider(host, {min, max, step, value, label, onChange, onInput}) -> {el, value, set}
     UI.images(host, {max, maxBytes, maxEdge, onChange, label}) -> {el, files, clear}
         PNG, JPEG, WebP, GIF; stills downscaled to maxEdge; paste and drop
     UI.examDate(anchor, {value, dates, onSave}) -> pop
         dates: 'YYYY-MM-DD' or {date, study_days, per_week, tag, register_by, late_by, projected}
     UI.actionBar(host, {text, actions}) -> {el, set(text, n)}   sticky, hidden without text
     UI.selbar(host, {actions, onClear}) -> {el, update(n)}      "4 selected" + actions(n)
   Data
     UI.tile(host, {label, value, unit, sub, href, filter, pressed, onClick, delta,
         spark, fact, format}) -> {el, set}   numbers count up once; null reads "—"
     UI.meter(host, {label, value, max, unit, text, ink, lg, tick}) -> {el, set}
     UI.skel(host, shape)   line | lines[:n] | num | circle | pill | tile | card | row | rows:n
                            | table:n | chart | cells:n | {w, h, r}
     UI.cardError(host, retry, text)
     UI.table(host, cols, rows, {sort, onSort, you, caption, empty, label, compact, hover, onRow})
         cols: {key, label, num, sort, value(row), render(row), title, stick}
         -> {el, update(rows), sortBy(key, dir)}
     UI.pips(owed, of) -> el    UI.dbars(tier) -> el
     UI.cell(state, n, {flag, note, open, fixing, over, saved, current, tier, level,
         filtered, href, onClick, label, size, static}) -> el
     UI.legend(host, keys, counts, {onFilter, pressed}) -> {el, update}
     UI.strip(host, marks, {onPick, fit, marker, label}) -> {el, set}
     UI.atlas(host, types, {sm, label, tip, onPick, selectable, onSelect}) -> {el, selected, select, clear}
         one role=row per call; host becomes the role=grid; arrows move across rows
     UI.masteryWord(m, answered)       UI.STRONG (0.8)
     UI.skillRow(host, skill, {practise, href}) -> el
     UI.avatar(profile, size) -> el    UI.localPhoto.{get, url, set, remove}(learner)
     UI.countdown(el, iso, {boxes, onEnd}) -> stop()
     UI.STATES                          every question state and overlay: label, glyph
   Product (G2, G5, G6, G11, G12, SR16)
     UI.VERBS, UI.verb(id, {count, onClick, href, primary, sm, subject}), UI.KEYS
     UI.pts(el, pts, key)     UI.fact(el, key, {label}); UI.fact.open(el, key)
         any [data-fact] element opens its working on click or Enter (delegated here)
     UI.empty(host, {sample, text, action, tag, answered})   UI.empty.START; with 0 answers
         (o.answered, else UI.answered, which the shell sets from /api/me) the action is START (R55)
     UI.SUBJECT      UI.qlabel(item, sitting); UI.qlabel.addr(item)
   Formatters
     UI.dur(minutes)  UI.mmss(sec)  UI.num(n)  UI.date(d, 'long' | 'short' | 'eyebrow')
     UI.relTime(d)  UI.KIND; UI.KIND.label(row)  UI.copyText(text, {toast})
     UI.ics(event) -> text  (one event, or repeat: 'daily' | 'weekly' | an RRULE)
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI = window.UI || {};
  const doc = document;

  // G9: a page change that gets skipped or interrupted rejects its transition's promises; keep
  // them off the console. The inbound side (pagereveal) fires before this file runs, so head.js
  // owns it; an inbound transition still running is caught through activeViewTransition.
  const quietVT = t => { if (t) [t.ready, t.finished, t.updateCallbackDone].forEach(p => p && p.catch(() => {})); };
  addEventListener('pageswap', e => quietVT(e.viewTransition));
  quietVT(doc.activeViewTransition);

  /* ------------------------------------------------------------ helpers */
  let seq = 0;
  const uid = p => `k${p}${++seq}`;
  function h(tag, attrs = {}, ...kids) {
    const e = doc.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k === 'style') e.style.cssText = v;
      else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat(3)) if (k !== null && k !== undefined && k !== false) e.append(k instanceof Node ? k : String(k));
    return e;
  }
  const NS = 'http://www.w3.org/2000/svg';
  const sv = (tag, attrs = {}, parent) => {
    const e = doc.createElementNS(NS, tag);
    for (const k in attrs) if (attrs[k] !== null && attrs[k] !== undefined) e.setAttribute(k, attrs[k]);
    if (parent) parent.append(e);
    return e;
  };
  const media = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
  const phone = () => media('(max-width: 759px)');
  const coarse = () => media('(pointer: coarse)');
  const still = () => media('(prefers-reduced-motion: reduce)') || doc.documentElement.dataset.motion === 'reduce';
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (_) { return false; } },
  };
  const put = (host, el) => { if (host) host.append(el); return el; };
  const typing = el => !!el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));
  const focusables = root => [...root.querySelectorAll('a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])')]
    .filter(e => !e.closest('[hidden]') && e.getClientRects().length);
  const api = (path, o = {}) => UI.api ? UI.api(path, o) : fetch('/api' + path, {
    method: o.method || 'GET',
    headers: { 'Content-Type': 'application/json', 'X-Learner': (UI.learner && UI.learner()) || '' },
    body: o.body === undefined ? undefined : JSON.stringify(o.body),
  }).then(async r => { if (!r.ok) throw Object.assign(new Error(`HTTP ${r.status}`), { status: r.status }); return r.json(); });
  async function startDrill(body) {
    const s = await api('/drill', { method: 'POST', body });
    location.href = `/practice/session/?id=${encodeURIComponent(s.id)}`;
  }

  /* icons: 24px strokes in currentColor */
  const L = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"';
  const ICON = {
    x:        `<path d="M6 6l12 12M18 6L6 18" ${L} stroke-width="1.7"/>`,
    check:    `<path d="M5 12.5l4.5 4.5L19 7.5" ${L} stroke-width="1.8"/>`,
    calendar: `<rect x="4" y="5.5" width="16" height="14.5" rx="2.5" ${L}/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4" ${L}/>`,
    image:    `<rect x="4" y="5" width="16" height="14" rx="2.5" ${L}/><circle cx="9.5" cy="10" r="1.6" ${L}/><path d="M5 17l4.5-4.5 3.5 3.5 2.5-2.5 3.5 3.5" ${L}/>`,
    plus:     `<path d="M12 5v14M5 12h14" ${L} stroke-width="1.8"/>`,
    filter:   `<path d="M4.5 6.5h15M7.5 12h9M10.5 17.5h3" ${L} stroke-width="1.8"/>`,
    search:   `<circle cx="10.5" cy="10.5" r="6" ${L}/><path d="M15 15l4.5 4.5" ${L} stroke-width="1.8"/>`,
    twin:     `<rect x="4" y="8" width="11" height="11" rx="2.2" ${L}/><path d="M9 5.5A1.5 1.5 0 0 1 10.5 4H18.5A1.5 1.5 0 0 1 20 5.5V13.5A1.5 1.5 0 0 1 18.5 15" ${L}/>`,
    twin_test:`<rect x="4" y="8" width="11" height="11" rx="2.2" ${L}/><path d="M9 5.5A1.5 1.5 0 0 1 10.5 4H18.5A1.5 1.5 0 0 1 20 5.5V9" ${L}/><circle cx="18" cy="16" r="3.6" ${L} stroke-width="1.4"/><path d="M18 14.2V16l1.1.9" ${L} stroke-width="1.3"/>`,
    again:    `<path d="M5.5 12a6.5 6.5 0 1 0 2-4.7" ${L}/><path d="M7.5 3.8v3.7h3.7" ${L}/>`,
    fix:      `<path d="M18.5 12a6.5 6.5 0 1 1-2-4.7" ${L}/><path d="M16.5 3.8v3.7h-3.7" ${L}/>`,
    learn:    `<path d="M4.5 5.5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2h-6zM19.5 5.5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z" ${L}/>`,
    copy:     `<rect x="8.5" y="8.5" width="11" height="11" rx="2" ${L}/><path d="M15.5 8.5V6a1.5 1.5 0 0 0-1.5-1.5H6A1.5 1.5 0 0 0 4.5 6v8A1.5 1.5 0 0 0 6 15.5h2.5" ${L}/>`,
    camera:   `<path d="M4.5 8.5A1.5 1.5 0 0 1 6 7h2l1.5-2h5L16 7h2a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 18 19H6a1.5 1.5 0 0 1-1.5-1.5z" ${L}/><circle cx="12" cy="12.5" r="3.2" ${L}/>`,
  };
  const svgHTML = (inner, size = 18) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${inner}</svg>`;
  function icon(i, size = 18) {
    if (!i) return null;
    if (i instanceof Node) return i;
    const t = doc.createElement('template');
    t.innerHTML = typeof i === 'string' && i.trim().startsWith('<svg') ? i : svgHTML(ICON[i] || (UI.ICON && UI.ICON[i]) || '', size);
    return t.content.firstElementChild;
  }
  const xBtn = (label, onClick) => h('button', { type: 'button', class: 'x', 'aria-label': label, html: svgHTML(ICON.x, 18), onclick: onClick });
  function keycaps(k) {
    if (!k) return null;
    return String(k).split(' ').map(part => part.split('+').map(c => h('kbd', { class: 'kbd', text: c }))).flat();
  }
  // one action button: {label, href, onClick, primary, ink, quiet, sm, kbd, icon, disabled, title}
  function button(a, sm = true) {
    const cls = a.primary ? `pill${sm ? ' sm' : ''}` : a.quiet ? 'quiet' : `btn${a.ink ? ' ink' : ''}${sm ? ' sm' : ''}`;
    const el = h(a.href ? 'a' : 'button', {
      class: cls + (a.className ? ' ' + a.className : ''), type: a.href ? null : 'button', href: a.href || null,
      disabled: !a.href && a.disabled, title: a.title, 'aria-label': a.ariaLabel,
    }, icon(a.icon), a.label, keycaps(a.kbd));
    return el;
  }
  const fmtN = n => typeof n === 'number' && isFinite(n) ? n.toLocaleString('en-US') : (n ?? '');

  /* ------------------------------------------------------------ formatters */
  const MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const DOW = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  function toDate(d) {
    if (d instanceof Date) return d;
    if (typeof d === 'number') return new Date(d);
    const s = String(d);
    const m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m ? new Date(+m[1], +m[2] - 1, +m[3], 12) : new Date(s);
  }
  const isoDay = d => { d = toDate(d); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; };
  const dayDiff = (a, b) => Math.round((toDate(isoDay(b)) - toDate(isoDay(a))) / 864e5);
  function date(d, style = 'short') {
    if (d === null || d === undefined || d === '') return '—';
    d = toDate(d);
    if (isNaN(d)) return '—';
    const yr = d.getFullYear() !== new Date().getFullYear() ? `, ${d.getFullYear()}` : '';
    const mon = MON[d.getMonth()], dow = DOW[d.getDay()];
    if (style === 'eyebrow') return `${dow}, ${mon} ${d.getDate()}${yr}`.toUpperCase();
    if (style === 'long') return `${dow.slice(0, 3)}, ${mon.slice(0, 3)} ${d.getDate()}${yr}`;
    return `${mon.slice(0, 3)} ${d.getDate()}${yr}`;
  }
  function dur(min) {
    if (min === null || min === undefined || isNaN(min)) return '—';
    const m = Math.max(0, Math.round(min)), hr = Math.floor(m / 60), r = m % 60;
    return hr ? (r ? `${hr}h ${r}m` : `${hr}h`) : `${r}m`;
  }
  const mmss = sec => {
    sec = Math.max(0, Math.round(sec || 0));
    const p2 = n => String(n).padStart(2, '0');
    return sec >= 3600 ? `${Math.floor(sec / 3600)}:${p2(Math.floor(sec / 60) % 60)}:${p2(sec % 60)}` : `${Math.floor(sec / 60)}:${p2(sec % 60)}`;
  };
  const num = n => n === null || n === undefined || n === '' || isNaN(n) ? '—' : Number(n).toLocaleString('en-US', { maximumFractionDigits: 1 });
  function relTime(d) {
    if (d === null || d === undefined || d === '') return '—';
    const t = toDate(d), s = Math.round((Date.now() - t) / 1000), a = Math.abs(s), fut = s < 0;
    const say = (n, u) => fut ? `in ${n} ${u}` : `${n} ${u} ago`;
    if (a < 45) return fut ? 'in a moment' : 'just now';
    if (a < 3600) return say(Math.round(a / 60), 'min');
    if (a < 86400 && dayDiff(new Date(), t) === 0) return say(Math.round(a / 3600), 'h').replace(' h', 'h');
    const dd = dayDiff(new Date(), t);
    if (dd === -1) return 'yesterday';
    if (dd === 1) return 'tomorrow';
    if (Math.abs(dd) < 7) return say(Math.abs(dd), 'days');
    return date(t);
  }
  const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;

  // every session kind and its label (R36); KIND.label(row) builds a row's full name
  const KIND = {
    mock: 'Full section', paper: 'Paper', module: 'Module', custom: 'Custom test', diagnostic: 'Diagnostic',
    drill: 'Practice', practice: 'Practice', challenge: 'Challenge', contest: 'Contest', words: 'Words',
    spot: 'Spot the trap', quick: 'Quick questions', twin: 'Twin test',
  };
  Object.defineProperty(KIND, 'label', {
    enumerable: false,
    value(row = {}) {
      if (row.kind_label) return row.kind_label;
      const k = row.kind || '', cfg = row.cfg || {};
      const paper = row.paper || (/^P\d+$/.test(row.mock_id || '') ? row.mock_id.slice(1) : null);
      let base = paper ? `Paper #${paper}`
        : k === 'module' ? `Module ${row.module || ''}`.trim()
        : (cfg.source === 'quick' || row.source === 'quick') ? KIND.quick
        : KIND[k] || cap(k.replace(/_/g, ' ')) || 'Practice';
      if (row.shared_by) base = `Shared by ${row.shared_by}`;
      if (row.twin_of) base = `Twin of #${row.twin_of_number || row.twin_of}`;
      if (row.retake) base += ` · Retake ${row.retake}`;
      return base;
    },
  });

  function copyText(text, o = {}) {
    const done = ok => { if (ok && o.toast !== false) toast(o.toast || 'Copied'); return ok; };
    const fallback = () => {
      const f = h('textarea', { readonly: true, class: 'sr', 'aria-hidden': 'true' });
      f.value = text;
      (topModal() || doc.body).append(f);
      f.select();
      let ok = false;
      try { ok = doc.execCommand('copy'); } catch (_) {}
      f.remove();
      if (!ok) {   // leave it selected in a field the student can copy from
        sheet({ title: 'Copy this', size: 's', body: b => { const g = h('textarea', { class: 'field', readonly: true, rows: 3 }); g.value = text; b.append(g); setTimeout(() => g.select(), 30); } });
      }
      return ok;
    };
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text).then(() => done(true), () => done(fallback()));
    return Promise.resolve(done(fallback()));
  }

  // one calendar event, or a repeating one (R18(b)); floating local times, so a
  // 17:00 reminder stays 17:00 through a clock change. Downloads unless download:false.
  function ics(ev = {}) {
    const pad = n => String(n).padStart(2, '0');
    const esc = s => String(s).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
    const fold = line => { const out = []; let s = line; while (s.length > 74) { out.push(s.slice(0, 74)); s = ' ' + s.slice(74); } out.push(s); return out.join('\r\n'); };
    let start = ev.start instanceof Date ? ev.start : null;
    const dateOnly = !start && /^\d{4}-\d{2}-\d{2}$/.test(String(ev.start || ''));
    if (!start) {
      const s = String(ev.start || isoDay(new Date()));
      start = dateOnly && ev.time ? new Date(`${s}T${ev.time}`) : toDate(s);
    }
    const allDay = ev.allDay ?? (dateOnly && !ev.time);
    const ymd = d => `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
    const stamp = d => `${ymd(d)}T${pad(d.getHours())}${pad(d.getMinutes())}00`;
    const utc = d => d.toISOString().replace(/[-:]/g, '').replace(/\.\d+/, '');
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//SAT Freshman//Calendar//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'BEGIN:VEVENT',
      `UID:${ev.uid || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}@satfreshman`}`, `DTSTAMP:${utc(new Date())}`];
    if (allDay) {
      const end = ev.end ? toDate(ev.end) : new Date(start.getFullYear(), start.getMonth(), start.getDate() + 1);
      lines.push(`DTSTART;VALUE=DATE:${ymd(start)}`, `DTEND;VALUE=DATE:${ymd(end)}`);
    } else {
      const end = ev.end ? toDate(ev.end) : new Date(start.getTime() + (ev.minutes || 30) * 60000);
      lines.push(`DTSTART:${stamp(start)}`, `DTEND:${stamp(end)}`);
    }
    if (ev.repeat) {
      const until = ev.until ? `;UNTIL=${ymd(toDate(ev.until))}${allDay ? '' : 'T235959'}` : '';
      const byday = ev.byday ? `;BYDAY=${[].concat(ev.byday).join(',')}` : '';
      lines.push(`RRULE:${/^FREQ=/.test(ev.repeat) ? ev.repeat : `FREQ=${String(ev.repeat).toUpperCase()}${byday}${until}`}`);
    }
    lines.push(`SUMMARY:${esc(ev.title || 'SAT Freshman')}`);
    const desc = [ev.description, ev.url].filter(Boolean).join('\n');
    if (desc) lines.push(`DESCRIPTION:${esc(desc)}`);
    if (ev.url) lines.push(`URL:${ev.url}`);
    if (ev.location) lines.push(`LOCATION:${esc(ev.location)}`);
    if (ev.alarm !== false && ev.alarm !== undefined && ev.alarm !== null) {
      const m = Math.max(0, Math.round(ev.alarm));
      lines.push('BEGIN:VALARM', 'ACTION:DISPLAY', `DESCRIPTION:${esc(ev.title || 'SAT Freshman')}`,
        `TRIGGER:${m ? `-PT${Math.floor(m / 60) ? Math.floor(m / 60) + 'H' : ''}${m % 60 ? (m % 60) + 'M' : ''}` : 'PT0M'}`, 'END:VALARM');
    }
    lines.push('END:VEVENT', 'END:VCALENDAR');
    const text = lines.map(fold).join('\r\n') + '\r\n';
    if (ev.download !== false) {
      const a = h('a', { href: URL.createObjectURL(new Blob([text], { type: 'text/calendar;charset=utf-8' })),
        download: ev.filename || `${(ev.title || 'sat-freshman').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}.ics` });
      doc.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    }
    return text;
  }

  /* ------------------------------------------------------------ layers
     Popovers, menus and tooltips: popover="manual" so they sit in the top layer,
     mounted inside the open modal when there is one (anything outside a modal is
     inert). One stack; Esc and an outside click close the top of it. */
  const layers = [];
  function topModal() {
    const ds = [...doc.querySelectorAll('dialog[open]')].filter(d => { try { return d.matches(':modal'); } catch (_) { return true; } });
    return ds[ds.length - 1] || null;
  }
  function mount(el, near) {
    const parent = (near instanceof Element && near.closest('dialog[open]')) || topModal() || doc.body;
    if (el.parentNode !== parent) parent.append(el);
    if (el.showPopover) {
      el.setAttribute('popover', 'manual');
      try { if (!el.matches(':popover-open')) el.showPopover(); } catch (_) {}
    }
  }
  function rectOf(a) {
    if (!a) return null;
    if (typeof a.getBoundingClientRect === 'function') return a.getBoundingClientRect();        // Element, Range
    if (typeof a.rangeCount === 'number') return a.rangeCount ? a.getRangeAt(0).getBoundingClientRect() : null;   // Selection
    const left = a.left ?? a.x ?? 0, top = a.top ?? a.y ?? 0;
    return { left, top, right: a.right ?? left + (a.width || 0), bottom: a.bottom ?? top + (a.height || 0) };
  }
  function place(el, anchor, o = {}) {
    const r = rectOf(anchor);
    if (!r) return;
    const gap = o.gap ?? 6, m = 8, w = el.offsetWidth, ht = el.offsetHeight;
    let top = r.bottom + gap;
    if (top + ht > innerHeight - m && r.top - gap - ht >= m) top = r.top - gap - ht;
    top = Math.max(m, Math.min(top, innerHeight - ht - m));
    let left = o.align === 'end' ? r.right - w : o.align === 'center' ? (r.left + r.right - w) / 2 : r.left;
    left = Math.max(m, Math.min(left, innerWidth - w - m));
    el.style.left = `${Math.round(left)}px`;
    el.style.top = `${Math.round(top)}px`;
  }
  function layer({ el, trigger, kind, restore, onClose }) {
    const L = {
      el, trigger, kind, restore, open: true, reposition: () => {},
      close(o = {}) {
        if (!L.open) return;
        const i = layers.indexOf(L);
        layers.slice(i + 1).reverse().forEach(x => x.close({ focus: false }));
        layers.splice(layers.indexOf(L), 1);
        L.open = false;
        const had = el.contains(doc.activeElement);
        try { if (el.matches(':popover-open')) el.hidePopover(); } catch (_) {}
        el.remove();
        if (trigger && trigger.setAttribute && trigger.hasAttribute('aria-expanded')) trigger.setAttribute('aria-expanded', 'false');
        const lost = had || doc.activeElement === doc.body || doc.activeElement === null;
        if (o.focus !== false && restore && restore.isConnected && (lost || o.focus === true)) restore.focus({ preventScroll: true });
        if (onClose) onClose(o.value);
      },
    };
    layers.push(L);
    return L;
  }
  // opening a popover or menu from outside the open ones closes them
  const closeOthers = from => layers.filter(L => L.kind !== 'tip' && !(from instanceof Node && L.el.contains(from))).reverse().forEach(L => L.close({ focus: false }));
  const findOpen = (trigger, kind) => layers.find(L => L.trigger === trigger && L.kind === kind);

  doc.addEventListener('keydown', e => {
    if (e.key !== 'Escape' || !layers.length) return;
    const L = layers[layers.length - 1];
    e.preventDefault();          // also keeps the sheet under it open
    e.stopPropagation();
    L.close({ focus: L.kind !== 'tip' });
  }, true);
  doc.addEventListener('pointerdown', e => {
    for (const L of [...layers].reverse()) {
      if (L.kind === 'tip') { L.close({ focus: false }); continue; }
      if (L.el.contains(e.target) || (L.trigger instanceof Node && L.trigger.contains(e.target))) break;
      L.close({ focus: true });      // back to the trigger; a click on something focusable then moves it on
    }
  }, true);
  doc.addEventListener('focusin', e => {
    for (const L of [...layers].reverse()) {
      if (L.kind === 'tip') continue;
      if (L.el.contains(e.target) || (L.trigger instanceof Node && L.trigger.contains(e.target))) break;
      L.close({ focus: false });
    }
  });
  let rafPending = false;
  const reflow = () => { if (rafPending) return; rafPending = true; requestAnimationFrame(() => { rafPending = false; layers.forEach(L => L.reposition()); }); };
  addEventListener('scroll', reflow, { capture: true, passive: true });
  addEventListener('resize', reflow);
  // a closing dialog takes its popovers with it; toasts move back to the page
  doc.addEventListener('close', e => {
    if (!(e.target instanceof HTMLDialogElement)) return;
    layers.filter(L => e.target.contains(L.el)).reverse().forEach(L => L.close({ focus: false }));
    if (toastHost && e.target.contains(toastHost)) toastRoot();
    if (!topModal()) flushWaiting();
  }, true);

  /* ------------------------------------------------------------ sheet */
  function sheet(o = {}) {
    const opener = doc.activeElement;
    // opened from inside a popover or menu, which closes as focus moves: return to its trigger
    const backup = (layers.find(L => L.el.contains(opener)) || {}).restore;
    const tid = uid('t');
    const d = h('dialog', { class: 'sheet' + (o.className ? ' ' + o.className : ''), 'data-size': o.size || null,
      'aria-labelledby': o.title ? tid : null, 'aria-label': o.title ? null : (o.label || 'Dialog'), tabindex: '-1' });
    const bodyEl = h('div', { class: 'sheet-body' });
    const head = h('div', { class: 'sheet-head' }, h('h2', { id: tid, text: o.title || '' }),
      o.dismiss === false ? null : xBtn('Close', () => tryClose()));
    let resolve;
    const closed = new Promise(r => { resolve = r; });
    let value, closing = false, guarding = false;
    const apiObj = { el: d, body: bodyEl, foot: null, closed,
      close(v) { value = v; closing = true; if (d.open) d.close(); },
      busy(on) { d.querySelectorAll('.sheet-foot > :is(button, a)').forEach(b => { if (on) b.setAttribute('aria-busy', 'true'); else b.removeAttribute('aria-busy'); }); },
      setTitle(t) { head.firstChild.textContent = t; } };
    const tryClose = async v => {
      if (o.guard) {
        if (guarding) return;
        guarding = true;
        let ok = false; try { ok = await o.guard(); } catch (_) {} finally { guarding = false; }
        if (ok === false) return;
      }
      apiObj.close(v);
    };
    d.append(head, bodyEl);
    const content = typeof o.body === 'function' ? o.body(bodyEl, apiObj) : o.body;
    if (typeof content === 'string') bodyEl.append(h('p', { text: content }));
    else if (content instanceof Node || Array.isArray(content)) bodyEl.append(...[].concat(content));

    if (o.actions && o.actions.length) {
      const foot = apiObj.foot = h('div', { class: 'sheet-foot' });
      const err = h('p', { class: 'field-err grow', role: 'alert', hidden: true });
      foot.append(err);
      [...o.actions].sort((a, b) => !!a.primary - !!b.primary).forEach(a => {
        const b = button(a, true);
        if (!a.href) b.addEventListener('click', async () => {
          if (b.getAttribute('aria-busy') === 'true') return;
          err.hidden = true;
          let r;
          b.setAttribute('aria-busy', 'true');
          try { r = a.onClick ? await a.onClick(apiObj) : undefined; }
          catch (x) { err.textContent = (x && x.message) || 'That didn’t work. Try again.'; err.hidden = false; r = false; }
          finally { b.removeAttribute('aria-busy'); }
          if (r !== false && a.close !== false) apiObj.close(r);
        });
        foot.append(b);
      });
      d.append(foot);
    }

    // Esc (and the Android back gesture, which modal dialogs get natively) asks first. Esc is
    // caught on keydown: Chromium honours only one prevented 'cancel' per user activation, so a
    // second Esc would otherwise close a guarded sheet natively.
    d.addEventListener('keydown', e => { if (e.key !== 'Escape' || e.defaultPrevented) return; e.preventDefault(); if (o.dismiss !== false) tryClose(); });
    d.addEventListener('cancel', e => { e.preventDefault(); if (o.dismiss !== false) tryClose(); });
    // the backdrop: a click outside the box
    d.addEventListener('click', e => {
      if (e.target !== d || o.dismiss === false) return;
      const r = d.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) tryClose();
    });
    // drag the handle down to close (a bottom sheet under 760px)
    let y0 = null, dy = 0;
    d.addEventListener('pointerdown', e => {
      if (!phone() || o.dismiss === false || e.button > 0) return;
      const r = d.getBoundingClientRect();
      if (e.clientY - r.top > 48 || e.target.closest('button, a, input, select, textarea')) return;
      y0 = e.clientY; dy = 0; d.setPointerCapture(e.pointerId);
    });
    d.addEventListener('pointermove', e => { if (y0 === null) return; dy = Math.max(0, e.clientY - y0); d.style.transform = dy ? `translateY(${dy}px)` : ''; });
    const drop = () => { if (y0 === null) return; y0 = null; d.style.transform = ''; if (dy > 90) tryClose(); };
    d.addEventListener('pointerup', drop);
    d.addEventListener('pointercancel', drop);
    head.style.touchAction = 'none';

    d.addEventListener('close', () => {
      // a native close that skipped 'cancel' (a repeated back gesture): reopen, then ask
      if (!closing && (o.guard || o.dismiss === false)) {
        d.showModal();
        (o.focus && o.focus.isConnected ? o.focus : d).focus({ preventScroll: true });
        if (o.dismiss !== false) tryClose();
        return;
      }
      d.remove();
      const back = opener && opener.isConnected ? opener : backup;
      if (back && back.isConnected && typeof back.focus === 'function') back.focus({ preventScroll: true });
      if (o.onClose) o.onClose(value);
      resolve(value);
    });
    doc.body.append(d);
    d.showModal();
    const first = o.focus || bodyEl.querySelector('[autofocus]') || bodyEl.querySelector('input:not([type=hidden]):not(:disabled), select, textarea');
    (first || d).focus({ preventScroll: true });
    return apiObj;
  }
  sheet.top = topModal;

  function confirm(o = {}) {
    let field = null, answer = false;
    const s = sheet({
      title: o.title || 'Are you sure?', size: 's', label: o.title,
      body: b => {
        if (o.text) b.append(o.text instanceof Node ? o.text : h('p', { text: o.text }));
        if (o.input) {
          const inp = o.input === true ? {} : o.input;
          const fid = uid('f');
          field = h(inp.rows ? 'textarea' : 'input', { id: fid, class: 'field', type: inp.rows ? null : (inp.type || 'text'),
            placeholder: inp.placeholder, maxlength: inp.maxlength, rows: inp.rows, required: inp.required, autocomplete: 'off' });
          field.value = inp.value || '';
          field.addEventListener('keydown', e => { if (e.key === 'Enter' && !inp.rows) { e.preventDefault(); ok.click(); } });
          b.append(h('div', { style: 'margin-top: 14px' }, inp.label && h('label', { class: 'label', for: fid, text: inp.label }), field, inp.help && h('p', { class: 'help', text: inp.help })));
          if (inp.maxlength) counter(field, inp.maxlength);
        }
      },
      actions: [
        { label: o.cancel || 'Cancel', onClick: () => { answer = false; } },
        { label: o.confirm || 'OK', primary: !o.destructive, ink: !!o.destructive, onClick: () => {
          if (field) {
            const v = field.value.trim();
            if ((o.input.required ?? true) && !v) { field.setAttribute('aria-invalid', 'true'); field.focus(); return false; }
            answer = v;
          } else answer = true;
        } },
      ],
    });
    const ok = s.foot.lastElementChild;
    if (!field) (o.destructive ? s.foot.children[1] : ok).focus({ preventScroll: true });
    return s.closed.then(() => field ? (answer === false ? null : answer) : answer === true);
  }

  /* ------------------------------------------------------------ popover */
  function pop(anchor, content, o = {}) {
    const trigger = o.trigger || (anchor instanceof Element ? anchor : null);
    if (trigger) { const open = findOpen(trigger, 'pop'); if (open) { open.close(); return null; } }
    closeOthers(trigger);
    const role = o.role || 'dialog';
    const el = h('div', { class: `popover${role === 'listbox' ? ' list' : ''}${o.anchored ? ' anchored' : ''}${o.className ? ' ' + o.className : ''}`,
      role, 'aria-label': o.label || null, tabindex: '-1', id: uid('p') });
    const L = layer({ el, trigger, kind: 'pop', restore: o.restore || trigger || doc.activeElement, onClose: o.onClose });
    const res = { el, close: v => L.close({ value: v }), reposition: () => L.reposition(), layer: L };
    L.reposition = () => { if (o.anchored || !phone()) place(el, anchor, o); };
    if (role === 'listbox') listbox(el, content || o.options || [], o, res);
    else {
      const c = typeof content === 'function' ? content(el, res) : content;
      if (typeof c === 'string') el.append(h('p', { text: c }));
      else if (c instanceof Node || Array.isArray(c)) el.append(...[].concat(c));
    }
    mount(el, trigger);
    if (trigger && trigger.setAttribute) { trigger.setAttribute('aria-expanded', 'true'); if (el.id) trigger.setAttribute('aria-controls', el.id); }
    L.reposition();
    if (o.focus !== false) {
      const f = role === 'listbox' ? el : (el.querySelector('[autofocus]') || focusables(el).find(x => !x.classList.contains('x')) || el);
      f.focus({ preventScroll: true });
    }
    return res;
  }

  // options: [{value, label, sub, meta, icon, disabled}] or [{group, options}]; aria-activedescendant
  function listbox(el, options, o, res) {
    el.tabIndex = 0;
    if (o.multi) el.setAttribute('aria-multiselectable', 'true');
    const chosen = new Set([].concat(o.value ?? []).map(String));
    const items = [];
    const add = (parent, opt) => {
      if (typeof opt !== 'object' || opt === null) opt = { value: opt, label: String(opt) };
      const oe = h('div', { role: 'option', id: uid('o'), 'aria-selected': chosen.has(String(opt.value)) ? 'true' : 'false',
        'aria-disabled': opt.disabled ? 'true' : null },
        icon(opt.icon),
        h('span', { class: 'opt-main' }, opt.label, opt.sub && h('span', { class: 'opt-sub', text: opt.sub })),
        opt.meta !== undefined && opt.meta !== null && opt.meta !== '' && h('span', { class: 'opt-meta' }, opt.meta instanceof Node ? opt.meta : fmtN(opt.meta)));
      oe._opt = opt;
      oe.addEventListener('click', () => pick(oe));
      oe.addEventListener('pointermove', () => activate(oe, false));
      items.push(oe);
      parent.append(oe);
    };
    for (const opt of options) {
      if (opt && opt.group !== undefined && Array.isArray(opt.options)) {
        const gid = uid('g');
        const g = h('div', { role: 'group', 'aria-labelledby': gid }, h('div', { class: 'menu-label', id: gid, text: opt.group }));
        opt.options.forEach(x => add(g, x));
        el.append(g);
      } else add(el, opt);
    }
    let active = null;
    const enabled = () => items.filter(x => x.getAttribute('aria-disabled') !== 'true');
    function activate(oe, scroll = true) {
      if (!oe) return;
      if (active) active.classList.remove('active');
      active = oe;
      oe.classList.add('active');
      el.setAttribute('aria-activedescendant', oe.id);
      if (scroll) oe.scrollIntoView({ block: 'nearest' });
    }
    function pick(oe) {
      if (!oe || oe.getAttribute('aria-disabled') === 'true') return;
      activate(oe, false);
      if (o.multi) {
        const on = oe.getAttribute('aria-selected') !== 'true';
        oe.setAttribute('aria-selected', on ? 'true' : 'false');
        o.onPick && o.onPick(items.filter(x => x.getAttribute('aria-selected') === 'true').map(x => x._opt.value), oe._opt);
        return;
      }
      items.forEach(x => x.setAttribute('aria-selected', x === oe ? 'true' : 'false'));
      const keep = o.onPick && o.onPick(oe._opt.value, oe._opt);
      if (keep !== false) res.close(oe._opt.value);
    }
    let typed = '', typedAt = 0;
    el.addEventListener('keydown', e => {
      const list = enabled(), i = list.indexOf(active);
      const go = j => { e.preventDefault(); activate(list[Math.max(0, Math.min(list.length - 1, j))]); };
      if (e.key === 'ArrowDown') go(i < 0 ? 0 : i + 1);
      else if (e.key === 'ArrowUp') go(i < 0 ? list.length - 1 : i - 1);
      else if (e.key === 'Home') go(0);
      else if (e.key === 'End') go(list.length - 1);
      else if (e.key === 'PageDown') go(i + 8);
      else if (e.key === 'PageUp') go(i - 8);
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(active); }
      else if (e.key === 'Tab') res.close();
      else if (e.key.length === 1 && !e.metaKey && !e.ctrlKey) {
        typed = Date.now() - typedAt > 700 ? e.key.toLowerCase() : typed + e.key.toLowerCase();
        typedAt = Date.now();
        const hit = list.find(x => x.textContent.trim().toLowerCase().startsWith(typed));
        if (hit) activate(hit);
      }
    });
    activate(items.find(x => x.getAttribute('aria-selected') === 'true' && x.getAttribute('aria-disabled') !== 'true') || enabled()[0], false);
    res.items = items;
  }

  /* ------------------------------------------------------------ menu */
  function menu(trigger, items, o = {}) {
    const open = trigger && findOpen(trigger, 'menu');
    if (open) { open.close(); return null; }
    closeOthers(trigger);
    const el = h('div', { class: 'menu' + (o.wide ? ' wide' : ''), role: 'menu', id: uid('m'),
      'aria-label': o.label || (trigger && (trigger.getAttribute('aria-label') || trigger.textContent.trim())) || 'Menu' });
    const L = layer({ el, trigger, kind: 'menu', restore: trigger || doc.activeElement, onClose: o.onClose });
    const res = { el, close: () => L.close() };
    const entries = [];
    for (const it of items || []) {
      if (!it) continue;
      if (it instanceof Node) { el.append(it); continue; }
      if (it.separator) { el.append(h('div', { role: 'separator' })); continue; }
      if (it.head) { el.append(h('div', { class: 'menu-head' }, it.head)); continue; }
      if (it.group !== undefined && !it.label) { el.append(h('div', { class: 'menu-label', role: 'presentation', text: it.group })); continue; }
      const role = it.checked === undefined ? 'menuitem' : it.radio ? 'menuitemradio' : 'menuitemcheckbox';
      const b = h(it.href ? 'a' : 'button', { role, type: it.href ? null : 'button', href: it.href || null, tabindex: '-1',
        'aria-checked': it.checked === undefined ? null : String(!!it.checked), 'aria-disabled': it.disabled ? 'true' : null,
        'data-radio': it.radio || null },
        icon(it.icon),
        h('span', { style: 'min-width: 0' }, it.label, it.sub && h('span', { class: 'menu-sub', text: it.sub })),
        it.meta !== undefined && h('span', { class: 'menu-meta' }, it.meta), keycaps(it.kbd));
      b.addEventListener('click', e => {
        if (it.disabled) { e.preventDefault(); return; }
        if (role === 'menuitemcheckbox') {
          const on = b.getAttribute('aria-checked') !== 'true';
          b.setAttribute('aria-checked', String(on));
          if (it.onClick) it.onClick(on, e);
          if (it.close) L.close();
          return;
        }
        if (role === 'menuitemradio') {
          el.querySelectorAll(`[data-radio="${CSS.escape(it.radio)}"]`).forEach(x => x.setAttribute('aria-checked', String(x === b)));
          if (it.onClick) it.onClick(true, e);
          if (it.close) L.close();
          return;
        }
        L.close();                  // focus goes back first, so what opens next returns there
        if (it.onClick) it.onClick(e);
      });
      entries.push(b);
      el.append(b);
    }
    const live = () => entries.filter(b => b.getAttribute('aria-disabled') !== 'true');
    let typed = '', typedAt = 0;
    el.addEventListener('keydown', e => {
      const list = live(), i = list.indexOf(doc.activeElement);
      const go = j => { e.preventDefault(); const n = list.length; if (n) list[((j % n) + n) % n].focus(); };
      if (e.key === 'ArrowDown') go(i + 1);
      else if (e.key === 'ArrowUp') go(i < 0 ? -1 : i - 1);
      else if (e.key === 'Home') go(0);
      else if (e.key === 'End') go(-1);
      else if (e.key === 'Tab') { e.preventDefault(); L.close(); }
      else if (e.key.length === 1 && !e.metaKey && !e.ctrlKey && e.key !== ' ') {
        typed = Date.now() - typedAt > 700 ? e.key.toLowerCase() : typed + e.key.toLowerCase();
        typedAt = Date.now();
        const hit = list.find(x => x.textContent.trim().toLowerCase().startsWith(typed));
        if (hit) hit.focus();
      }
    });
    mount(el, trigger);
    if (trigger) trigger.setAttribute('aria-expanded', 'true');
    L.reposition = () => place(el, trigger || o.anchor, { align: o.align });
    L.reposition();
    const list = live();
    (o.last ? list[list.length - 1] : list[0] || el).focus({ preventScroll: true });
    return res;
  }
  menu.bind = (trigger, items, o = {}) => {
    const get = () => typeof items === 'function' ? items() : items;
    trigger.setAttribute('aria-haspopup', 'menu');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.addEventListener('click', () => menu(trigger, get(), o));
    trigger.addEventListener('keydown', e => {
      if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && !findOpen(trigger, 'menu')) {
        e.preventDefault();
        menu(trigger, get(), { ...o, last: e.key === 'ArrowUp' });
      }
    });
    return trigger;
  };

  /* ------------------------------------------------------------ tooltip */
  function tooltip(el, text, o = {}) {
    let L = null, timer = 0;
    const tid = uid('tip');
    if (typeof text === 'string' && !el.getAttribute('aria-label') && !el.textContent.trim()) el.setAttribute('aria-label', text);
    const show = now => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        if (L || !el.isConnected) return;
        const t = typeof text === 'function' ? text() : text;
        if (!t) return;
        const tip = h('div', { class: 'tip', role: 'tooltip', id: tid }, t instanceof Node ? t : String(t), o.kbd && keycaps(o.kbd));
        L = layer({ el: tip, trigger: el, kind: 'tip', onClose: () => { L = null; el.removeAttribute('aria-describedby'); } });
        L.reposition = () => place(tip, el, { gap: 8, align: 'center' });
        mount(tip, el);
        if (el.getAttribute('aria-label') !== t) el.setAttribute('aria-describedby', tid);
        L.reposition();
      }, now ? 0 : (o.delay ?? 350));
    };
    const hide = () => { clearTimeout(timer); if (L) L.close({ focus: false }); };
    const on = [
      ['pointerenter', e => { if (e.pointerType === 'mouse') show(false); }],
      ['pointerleave', hide],
      ['focus', () => { try { if (el.matches(':focus-visible')) show(true); } catch (_) { show(true); } }],
      ['blur', hide],
    ];
    on.forEach(([k, f]) => el.addEventListener(k, f));
    return { hide, set(t) { text = t; }, destroy() { hide(); on.forEach(([k, f]) => el.removeEventListener(k, f)); } };
  }

  /* ------------------------------------------------------------ toasts */
  let toastHost = null;
  const shown = [], waiting = [];
  function toastRoot() {
    if (!toastHost) toastHost = h('div', { class: 'toasts', 'aria-live': 'polite', role: 'region', 'aria-label': 'Notifications' });
    const parent = topModal() || doc.body;
    if (toastHost.parentNode !== parent) {
      parent.append(toastHost);
      if (toastHost.showPopover) { toastHost.setAttribute('popover', 'manual'); try { toastHost.showPopover(); } catch (_) {} }
    }
    return toastHost;
  }
  function flushWaiting() { waiting.splice(0).forEach(([t, o]) => toast(t, { ...o, wait: false })); }
  function toast(text, o = {}) {
    if (o.wait && topModal()) { waiting.push([text, o]); return null; }
    const host = toastRoot();
    const el = h('div', { class: 'toast' }, icon(o.icon, 22), h('span', { class: 'toast-t' }, text instanceof Node ? text : String(text)));
    let timer = 0, left = o.ms ?? (o.undo ? 6000 : 4000), since = 0;
    const entry = {
      el, undo: o.undo || null,
      close() { clearTimeout(timer); const i = shown.indexOf(entry); if (i >= 0) shown.splice(i, 1); el.remove(); },
      async doUndo() { entry.close(); try { await o.undo(); } catch (_) { toast('Couldn’t undo that.'); } },
    };
    if (o.undo) el.append(h('button', { type: 'button', class: 'act', onclick: () => entry.doUndo() }, 'Undo', h('kbd', { class: 'kbd', text: 'Z' })));
    else if (o.action || o.href) {
      const a = typeof o.action === 'object' && o.action ? o.action : { label: o.action || 'Open', href: o.href };
      const act = h(a.href || o.href ? 'a' : 'button', { class: 'act', href: a.href || o.href || null, type: a.href || o.href ? null : 'button' }, a.label);
      act.addEventListener('click', e => { if (a.onClick) a.onClick(e); entry.close(); });
      el.append(act);
    }
    el.append(xBtn('Dismiss', () => entry.close()));
    const run = () => { if (left > 0) { since = Date.now(); timer = setTimeout(() => entry.close(), left); } };
    const pause = () => { clearTimeout(timer); if (since) left -= Date.now() - since; since = 0; };
    el.addEventListener('pointerenter', pause);
    el.addEventListener('pointerleave', run);
    el.addEventListener('focusin', pause);
    el.addEventListener('focusout', e => { if (!el.contains(e.relatedTarget)) run(); });
    host.append(el);
    shown.push(entry);
    while (shown.length > 3) shown[0].close();
    run();
    return entry;
  }
  toast.undo = () => {
    const t = [...shown].reverse().find(x => x.undo);
    if (!t) return false;
    t.doUndo();
    return true;
  };

  /* ------------------------------------------------------------ banner */
  const BANNER_ORDER = ['retired', 'offline', 'storage', 'first', 'nudge'];
  const SYS = new Set(['retired', 'offline', 'storage']);
  const banners = new Map();
  let bannerEl = null;
  function banner(kind, text, actions = [], o = {}) {
    if (text === null || text === undefined) { banners.delete(kind); drawBanner(); return null; }
    banners.set(kind, { kind, text, actions: actions || [], o });
    drawBanner();
    return { close: () => { banners.delete(kind); drawBanner(); } };
  }
  banner.clear = kind => { banners.delete(kind); drawBanner(); };
  function drawBanner() {
    const rank = k => { const i = BANNER_ORDER.indexOf(k); return i < 0 ? BANNER_ORDER.length : i; };
    const top = [...banners.values()].sort((a, b) => rank(a.kind) - rank(b.kind))[0];
    if (!top) { if (bannerEl) bannerEl.remove(); bannerEl = null; return; }
    const kids = [
      icon(top.o.icon, 20),
      h('div', { class: 'banner-t' }, top.text instanceof Node ? top.text : String(top.text)),
      top.actions.length ? h('div', { class: 'banner-act' }, top.actions.map(a => {
        const b = button(a, true);
        if (a.onClick) b.addEventListener('click', e => a.onClick(e));
        if (a.dismiss) b.addEventListener('click', () => banner.clear(top.kind));
        return b;
      })) : null,
      top.o.dismiss ? xBtn('Dismiss', () => { banner.clear(top.kind); if (top.o.onDismiss) top.o.onDismiss(); }) : null,
    ];
    if (bannerEl && bannerEl.dataset.kind === top.kind) { bannerEl.replaceChildren(...kids.filter(Boolean)); return; }   // updates in place: no second entrance
    if (bannerEl) bannerEl.remove();
    bannerEl = h('div', { class: 'banner' + (SYS.has(top.kind) || top.o.sys ? ' sys' : ''), role: 'status', 'data-kind': top.kind }, kids);
    (top.o.host || doc.querySelector('main') || doc.body).prepend(bannerEl);
  }

  /* ------------------------------------------------------------ choices: seg, chips */
  const normOpt = x => typeof x === 'object' && x !== null ? x : { value: x, label: String(x) };
  function choices(cls, host, options, o = {}) {
    const multi = !!o.multi;
    const opts = options.map(normOpt);
    const firstOn = opts.find(x => !x.disabled);
    let value = multi ? new Set([].concat(o.value ?? [])) : (o.value !== undefined ? o.value : firstOn && firstOn.value);
    const el = h('div', { class: cls + (o.full ? ' full' : '') + (o.className ? ' ' + o.className : ''), role: multi ? 'group' : 'radiogroup', 'aria-label': o.label || null });
    const help = h('p', { class: 'help' });
    const btns = opts.map(opt => {
      const b = h('button', { type: 'button', role: multi ? null : 'radio', title: opt.title || null },
        icon(opt.icon), h('span', { text: opt.label }), h('span', { class: 'n', hidden: opt.n === undefined || opt.n === null, text: fmtN(opt.n) }));
      b._opt = opt;
      b.addEventListener('click', () => choose(b));
      return b;
    });
    el.append(...btns);
    const isOn = b => multi ? value.has(b._opt.value) : value === b._opt.value;
    function sync() {
      btns.forEach(b => {
        b.setAttribute(multi ? 'aria-pressed' : 'aria-checked', String(isOn(b)));
        if (b._opt.disabled) b.setAttribute('aria-disabled', 'true'); else b.removeAttribute('aria-disabled');
      });
      const stop = btns.find(b => isOn(b) && !b._opt.disabled) || btns.find(b => !b._opt.disabled) || btns[0];
      btns.forEach(b => { b.tabIndex = b === stop ? 0 : -1; });
      const why = opts.filter(x => x.disabled && x.why).map(x => `${x.label}: ${x.why}`);
      help.textContent = why.join(' · ');
      help.hidden = !why.length;
    }
    function choose(b, fromKey) {
      if (b._opt.disabled) { if (!fromKey) b.focus(); return; }
      if (multi) value.has(b._opt.value) ? value.delete(b._opt.value) : value.add(b._opt.value);
      else { if (value === b._opt.value) return; value = b._opt.value; }
      sync();
      if (o.onChange) o.onChange(multi ? [...value] : value, b._opt);
    }
    el.addEventListener('keydown', e => {
      const keys = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
      const i = btns.indexOf(doc.activeElement);
      if (i < 0) return;
      let j = null;
      if (keys[e.key]) {
        for (let k = 1; k <= btns.length; k++) { const c = btns[(i + keys[e.key] * k + btns.length * k) % btns.length]; if (!c._opt.disabled) { j = btns.indexOf(c); break; } }
      } else if (e.key === 'Home') j = btns.findIndex(b => !b._opt.disabled);
      else if (e.key === 'End') j = btns.length - 1 - [...btns].reverse().findIndex(b => !b._opt.disabled);
      if (j === null || j < 0) return;
      e.preventDefault();
      btns.forEach((b, k) => { b.tabIndex = k === j ? 0 : -1; });
      btns[j].focus();
      if (!multi) choose(btns[j], true);       // a radio group selects as it moves
    });
    sync();
    if (host) { host.append(el); host.append(help); }
    return {
      el, help, btns,
      get value() { return multi ? [...value] : value; },
      set(v, silent) { value = multi ? new Set([].concat(v ?? [])) : v; sync(); if (!silent && o.onChange) o.onChange(multi ? [...value] : value); },
      count(v, n) { const b = btns.find(x => x._opt.value === v); if (b) { const c = b.querySelector('.n'); c.textContent = fmtN(n); c.hidden = n === null || n === undefined; } },
      disable(v, why) { const opt = opts.find(x => x.value === v); if (opt) { opt.disabled = !!why || why === ''; opt.why = typeof why === 'string' ? why : ''; sync(); } },
    };
  }
  const seg = (host, options, o) => choices('seg', host, options, o);
  const chips = (host, options, o) => choices('chips', host, options, o);

  /* ------------------------------------------------------------ tabs */
  function tabs(host, list, o = {}) {
    const el = h('div', { class: 'tablist', role: 'tablist', 'aria-label': o.label || null });
    const fromUrl = o.param ? new URLSearchParams(location.search).get(o.param) : null;
    const ok = id => list.some(t => t.id === id && !t.disabled);
    let value = [fromUrl, o.value].find(ok) ?? (list.find(t => !t.disabled) || {}).id;     // a deep link wins
    const panelOf = t => typeof t.panel === 'string' ? doc.getElementById(t.panel) : t.panel || null;
    const btns = list.map(t => {
      const b = h(t.href ? 'a' : 'button', { role: 'tab', id: t.tabId || uid('tab'), type: t.href ? null : 'button', href: t.href || null,
        disabled: !t.href && t.disabled },
        icon(t.icon), h('span', { text: t.label }), h('span', { class: 'n' }));
      b._t = t;
      const p = panelOf(t);
      if (p) {
        if (!p.id) p.id = uid('panel');
        b.setAttribute('aria-controls', p.id);
        p.setAttribute('role', 'tabpanel');
        p.setAttribute('aria-labelledby', b.id);
        if (!p.hasAttribute('tabindex')) p.tabIndex = 0;
      }
      if (!t.href) b.addEventListener('click', () => select(t.id, false));
      return b;
    });
    el.append(...btns);
    function count(id, n) {
      const b = btns.find(x => x._t.id === id);
      if (!b) return;
      const c = b.querySelector('.n');
      c.textContent = fmtN(n);
      c.hidden = n === null || n === undefined;
    }
    list.forEach(t => count(t.id, (o.counts && o.counts[t.id] !== undefined) ? o.counts[t.id] : t.n));
    function sync() {
      btns.forEach(b => {
        const on = b._t.id === value;
        b.setAttribute('aria-selected', String(on));
        b.tabIndex = on ? 0 : -1;
        const p = panelOf(b._t);
        if (p) p.hidden = !on;
      });
    }
    function select(id, focus, silent) {
      if (!ok(id)) return;
      const changed = id !== value;
      value = id;
      sync();
      if (focus) btns.find(b => b._t.id === id).focus();
      if (o.param && changed) {
        const u = new URL(location.href);
        u.searchParams.set(o.param, id);
        history.replaceState(history.state, '', u);
      }
      if (changed && !silent && o.onChange) o.onChange(id);
    }
    el.addEventListener('keydown', e => {
      const live = btns.filter(b => !b._t.disabled);
      const i = live.indexOf(doc.activeElement);
      if (i < 0) return;
      const j = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: live.length - 1 }[e.key];
      if (j === undefined) return;
      e.preventDefault();
      const b = live[(j + live.length) % live.length];
      if (b._t.href) { btns.forEach(x => { x.tabIndex = x === b ? 0 : -1; }); b.focus(); }
      else select(b._t.id, true);
    });
    sync();
    put(host, el);
    return { el, get value() { return value; }, set: (id, silent) => select(id, false, silent), count };
  }

  /* ------------------------------------------------------------ switch, triCheck */
  function switchCtl(host, o = {}) {
    if (host && !(host instanceof Node)) { o = host; host = null; }
    let on = !!o.checked;
    const b = h('button', { type: 'button', class: 'switch', role: 'switch', 'aria-checked': String(on), disabled: o.disabled, id: o.id || null,
      'aria-label': o.label ? null : (o.ariaLabel || null) });
    const sync = () => b.setAttribute('aria-checked', String(on));
    b.addEventListener('click', async () => {
      on = !on; sync();
      if (!o.onChange) return;
      try { await o.onChange(on); } catch (_) { on = !on; sync(); }   // an optimistic flip, put back when the save fails
    });
    const el = o.label ? h('label', { class: 'check' }, b, h('span', { text: o.label })) : b;
    put(host, el);
    return { el: b, wrap: el, get value() { return on; }, set(v) { on = !!v; sync(); } };
  }
  function triCheck(host, o = {}) {
    const input = h('input', { type: 'checkbox', name: o.name || null, value: o.value ?? null });
    const el = h('label', { class: 'check' + (o.className ? ' ' + o.className : '') }, input, h('span', { text: o.label || '' }),
      o.n !== undefined && o.n !== null ? h('span', { class: 'n', text: fmtN(o.n) }) : null);
    const set = s => { input.indeterminate = s === 'mixed'; input.checked = s === true; };
    set(o.mixed ? 'mixed' : !!o.checked);
    input.addEventListener('change', () => o.onChange && o.onChange(input.checked));
    put(host, el);
    return { el, input, set, get value() { return input.indeterminate ? 'mixed' : input.checked; } };
  }

  /* ------------------------------------------------------------ URL and store sync */
  const readUrl = key => { const v = new URLSearchParams(location.search).get(key); return v === null ? undefined : v; };
  function writeUrl(pairs) {
    const u = new URL(location.href);
    for (const [k, v] of Object.entries(pairs)) {
      const s = Array.isArray(v) ? v.join(',') : v;
      if (s === undefined || s === null || s === '') u.searchParams.delete(k); else u.searchParams.set(k, s);
    }
    if (u.href !== location.href) history.replaceState(history.state, '', u);
  }

  /* ------------------------------------------------------------ checkbox panel (multi dropdowns) */
  function checkPanel(o, value, onChange) {
    const sel = new Set(value.map(String));
    const wrap = h('div', { class: 'checks' });
    const rows = [];
    const count = v => o.counts && o.counts[v] !== undefined ? o.counts[v] : null;
    const addOpt = (opt, parent, sub) => {
      opt = normOpt(opt);
      const t = triCheck(parent, { label: opt.label, checked: sel.has(String(opt.value)), n: count(opt.value) ?? opt.n, className: sub ? 'sub' : '',
        onChange: on => { on ? sel.add(String(opt.value)) : sel.delete(String(opt.value)); syncGroups(); emit(); } });
      if (opt.disabled) t.input.disabled = true;
      rows.push({ t, v: String(opt.value), raw: opt.value });
      return t;
    };
    const groupRows = [];
    if (o.groups) {
      for (const g of o.groups) {
        const members = [];
        const gt = triCheck(wrap, { label: g.label || g.group, n: g.options.reduce((s, x) => s + (count(normOpt(x).value) || 0), 0) || null,
          onChange: on => { members.forEach(m => { m.t.set(on); on ? sel.add(m.v) : sel.delete(m.v); }); syncGroups(); emit(); } });
        g.options.forEach(x => { addOpt(x, wrap, true); members.push(rows[rows.length - 1]); });
        groupRows.push({ gt, members });
      }
    } else (o.options || []).forEach(x => addOpt(x, wrap, false));
    function syncGroups() {
      groupRows.forEach(({ gt, members }) => {
        const n = members.filter(m => sel.has(m.v)).length;
        gt.set(n === 0 ? false : n === members.length ? true : 'mixed');
      });
    }
    function emit() { onChange(rows.filter(r => sel.has(r.v)).map(r => r.raw)); }
    const all = h('button', { type: 'button', class: 'quiet', text: 'Select all', onclick: () => { rows.forEach(r => { if (!r.t.input.disabled) { sel.add(r.v); r.t.set(true); } }); syncGroups(); emit(); } });
    const none = h('button', { type: 'button', class: 'quiet', text: 'Clear', onclick: () => { sel.clear(); rows.forEach(r => r.t.set(false)); syncGroups(); emit(); } });
    wrap.append(h('div', { class: 'checks-foot' }, all, none));
    wrap.addEventListener('keydown', e => {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      const boxes = [...wrap.querySelectorAll('input:not(:disabled)')];
      const i = boxes.indexOf(doc.activeElement);
      if (i < 0) return;
      e.preventDefault();
      boxes[Math.max(0, Math.min(boxes.length - 1, i + (e.key === 'ArrowDown' ? 1 : -1)))].focus();
    });
    syncGroups();
    return wrap;
  }

  /* ------------------------------------------------------------ dropdown */
  function dropdown(host, o = {}) {
    const multi = !!o.multi;
    const flat = () => (o.groups ? o.groups.flatMap(g => g.options) : o.options || []).map(normOpt);
    const all = o.all ?? 'All';
    const dflt = multi ? [] : (o.default ?? '');
    let counts = o.counts || {};
    const stored = o.store && o.key ? (ls.get(o.store, {}) || {})[o.key] : undefined;
    const fromUrl = o.url && o.key ? readUrl(o.key) : undefined;
    let value = o.value ?? (fromUrl !== undefined ? (multi ? fromUrl.split(',').filter(Boolean) : fromUrl) : stored) ?? dflt;
    const b = h('button', { type: 'button', class: 'btn dd' + (o.sm ? ' sm' : ''), 'aria-haspopup': multi ? 'dialog' : 'listbox', 'aria-expanded': 'false' },
      h('span', { class: 'dd-k', text: o.label }), h('span', { class: 'dd-v' }));
    const labelOf = v => { const x = flat().find(opt => String(opt.value) === String(v)); return x ? x.label : v; };
    const isSet = () => multi ? value.length > 0 : String(value) !== String(dflt);
    const text = () => multi ? (value.length === 0 ? all : value.length === 1 ? labelOf(value[0]) : String(value.length))
      : (value === '' || value === null || value === undefined ? all : labelOf(value));
    function draw() {
      b.querySelector('.dd-v').textContent = text();
      b.classList.toggle('on', isSet() && !o.plain);
      b.setAttribute('aria-label', `${o.label}: ${text()}`);
    }
    function set(v, silent) {
      value = multi ? [].concat(v ?? []) : (v ?? dflt);
      draw();
      if (o.url && o.key) writeUrl({ [o.key]: isSet() ? value : null });
      if (o.store && o.key) { const s = ls.get(o.store, {}) || {}; if (isSet()) s[o.key] = value; else delete s[o.key]; ls.set(o.store, s); }
      if (!silent && o.onChange) o.onChange(multi ? [...value] : value);
    }
    const withCounts = opt => ({ ...opt, meta: counts[opt.value] ?? opt.meta ?? opt.n });
    function open() {
      if (multi) {
        return pop(b, () => [checkPanel({ ...o, counts }, value, v => set(v))], { role: 'dialog', label: o.label, className: 'dd-pop' });
      }
      const opts = o.groups ? o.groups.map(g => ({ group: g.label || g.group, options: g.options.map(normOpt).map(withCounts) }))
        : [...(o.noAll || o.default !== undefined ? [] : [{ value: '', label: all }]), ...flat().map(withCounts)];
      const typed = v => { const x = flat().find(opt => String(opt.value) === String(v)); return x ? x.value : v; };
      return pop(b, opts, { role: 'listbox', label: o.label, value: String(value ?? ''), onPick: v => set(typed(v)), onClose: o.onClose });
    }
    b.addEventListener('click', open);
    b.addEventListener('keydown', e => { if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && !findOpen(b, 'pop')) { e.preventDefault(); open(); } });
    draw();
    put(host, b);
    return { el: b, get value() { return multi ? [...value] : value; }, set, open, isSet, text,
      counts(map) { counts = map || {}; } };
  }

  /* ------------------------------------------------------------ filter bar */
  const DATE_OPTS = [{ value: 'today', label: 'Today' }, { value: '7', label: '7 days' }, { value: '30', label: '30 days' }, { value: 'custom', label: 'Custom' }];
  const rangeText = v => typeof v === 'string' && v.includes('..') ? v.split('..').map(x => x ? date(x) : '…').join(' – ') : null;
  function filterBar(host, filters, o = {}) {
    const state = {}, counts = {}, ctl = {};
    const many = f => f.type === 'multi' || f.type === 'pills';
    const dflt = f => many(f) ? [] : (f.default ?? (f.type === 'sort' ? normOpt((f.options || [])[0] ?? '').value : ''));
    const stored = o.store ? ls.get(o.store, {}) || {} : {};
    for (const f of filters) {
      const u = o.url ? readUrl(f.key) : undefined;
      state[f.key] = u !== undefined ? (many(f) ? u.split(',').filter(Boolean) : u) : stored[f.key] ?? f.value ?? dflt(f);
      if (f.counts) counts[f.key] = f.counts;
    }
    const isSet = f => { const v = state[f.key]; return Array.isArray(v) ? v.length > 0 : String(v ?? '') !== String(dflt(f) ?? ''); };
    const el = h('div', { class: 'filters', role: 'search', 'aria-label': o.label || 'Filters' });
    const keep = o.sheet === false ? ' filters-keep' : '';
    const clearBtn = h('button', { type: 'button', class: 'quiet' + keep, text: o.clear || 'Clear', onclick: () => api_.clear() });
    const openBtn = h('button', { type: 'button', class: 'btn filters-open', 'aria-haspopup': 'dialog', hidden: o.sheet === false }, icon('filter'), h('span'));
    function commit(key) {
      for (const f of filters) if (ctl[f.key]) ctl[f.key]();
      if (o.url) writeUrl(Object.fromEntries(filters.map(f => [f.key, isSet(f) ? state[f.key] : null])));
      if (o.store) ls.set(o.store, Object.fromEntries(filters.filter(isSet).map(f => [f.key, state[f.key]])));
      const n = filters.filter(f => f.type !== 'sort' && isSet(f)).length;
      clearBtn.hidden = !n;
      openBtn.lastChild.textContent = n ? `Filters · ${n}` : 'Filters';
      if (key !== undefined && o.onChange) o.onChange({ ...state }, key);
    }
    const change = (key, v) => { state[key] = v; commit(key); };
    function customDate(anchor, f) {
      const [a, z] = rangeText(state[f.key]) ? state[f.key].split('..') : ['', ''];
      pop(anchor, (p, res) => {
        const from = h('input', { type: 'date', class: 'field sm', value: a, 'aria-label': 'From' });
        const to = h('input', { type: 'date', class: 'field sm', value: z, 'aria-label': 'To' });
        const go = h('button', { type: 'button', class: 'pill sm', text: 'Apply', onclick: () => { if (from.value || to.value) change(f.key, `${from.value}..${to.value}`); res.close(); } });
        return h('div', { class: 'date-form' }, h('label', { class: 'label', text: 'From' }), from, h('label', { class: 'label', text: 'To' }), to, go);
      }, { label: `${f.label || 'Date'}: a range`, onClose: () => ctl[f.key]() });
    }
    for (const f of filters) {
      if (f.type === 'search') {
        const inp = h('input', { type: 'search', class: 'field sm', placeholder: f.placeholder || f.label || 'Search', 'aria-label': f.label || 'Search' });
        let t = 0;
        inp.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => change(f.key, inp.value.trim()), 250); });
        el.append(h('span', { class: 'filters-keep filters-search' }, inp));
        ctl[f.key] = () => { if (doc.activeElement !== inp) inp.value = state[f.key] || ''; };
      } else if (f.type === 'pills') {
        const nOf = x => (counts[f.key] && counts[f.key][x.value] !== undefined ? counts[f.key][x.value] : x.n);
        const opts = f.options.map(normOpt);
        const c = chips(null, opts.map(x => ({ ...x, n: nOf(x) })), { multi: true, value: state[f.key], label: f.label, onChange: v => change(f.key, v) });
        if (keep) c.el.classList.add('filters-keep');
        el.append(c.el);
        ctl[f.key] = () => { c.set(state[f.key], true); opts.forEach(x => c.count(x.value, nOf(x))); };   // the same counts as the phone sheet
      } else {
        const isDate = f.type === 'date';
        const d = dropdown(null, { label: f.label || (isDate ? 'Date' : ''), options: isDate ? DATE_OPTS : f.options, groups: f.groups,
          multi: f.type === 'multi', counts: counts[f.key], default: f.type === 'sort' ? dflt(f) : f.default, noAll: f.type === 'sort',
          all: f.all, plain: f.type === 'sort', value: state[f.key],
          onChange: v => { if (isDate && v === 'custom') customDate(d.el, f); else change(f.key, v); } });
        if (keep) d.el.classList.add('filters-keep');
        el.append(d.el);
        ctl[f.key] = () => {
          d.counts(counts[f.key]);
          const v = state[f.key], r = isDate && rangeText(v);
          d.set(r ? 'custom' : v, true);
          if (r) d.el.querySelector('.dd-v').textContent = r;
        };
      }
    }
    el.append(clearBtn, openBtn);
    // a phone: one "Filters · n" button, and every filter laid out in a bottom sheet
    openBtn.addEventListener('click', () => {
      let body;
      const fill = () => {
        body.replaceChildren();
        for (const f of filters) {
          if (f.type === 'search') continue;
          const sec = h('div', { class: 'filters-sec' }, h('p', { class: 'label', text: f.label || 'Date' }));
          const withN = x => ({ ...x, n: counts[f.key] && counts[f.key][x.value] !== undefined ? counts[f.key][x.value] : x.n });
          if (f.type === 'multi') sec.append(checkPanel({ ...f, counts: counts[f.key] }, [].concat(state[f.key] || []), v => change(f.key, v)));
          else if (f.type === 'pills') chips(sec, f.options.map(normOpt).map(withN), { multi: true, value: state[f.key], label: f.label, onChange: v => change(f.key, v) });
          else if (f.type === 'date') {
            const cur = state[f.key] || '', r = rangeText(cur);
            const from = h('input', { type: 'date', class: 'field sm', 'aria-label': 'From', value: r ? cur.split('..')[0] : '' });
            const to = h('input', { type: 'date', class: 'field sm', 'aria-label': 'To', value: r ? cur.split('..')[1] : '' });
            const range = h('div', { class: 'date-range', hidden: !r }, from, to);
            const upd = () => { if (from.value || to.value) change(f.key, `${from.value}..${to.value}`); };
            from.addEventListener('change', upd);
            to.addEventListener('change', upd);
            chips(sec, [{ value: '', label: 'All' }, ...DATE_OPTS], { value: r ? 'custom' : cur, label: f.label || 'Date',
              onChange: v => { range.hidden = v !== 'custom'; if (v !== 'custom') change(f.key, v); } });
            sec.append(range);
          } else {
            const opts = (f.groups ? f.groups.flatMap(g => g.options) : f.options).map(normOpt).map(withN);
            chips(sec, f.type === 'sort' || f.default !== undefined ? opts : [{ value: '', label: f.all || 'All' }, ...opts], { value: state[f.key], label: f.label, onChange: v => change(f.key, v) });
          }
          body.append(sec);
        }
      };
      sheet({ title: o.title || 'Filters', size: 'm', body: b => { body = b; fill(); },
        actions: [{ label: o.clear || 'Clear', quiet: true, onClick: () => { api_.clear(); fill(); return false; } }, { label: 'Show results', primary: true }] });
    });
    const api_ = {
      el,
      values: () => ({ ...state }),
      set(key, v) { change(key, v); },
      clear() { for (const f of filters) if (f.type !== 'sort') state[f.key] = dflt(f); commit(null); },
      counts(key, map) { counts[key] = map; if (ctl[key]) ctl[key](); },
    };
    commit();
    put(host, el);
    return api_;
  }

  /* ------------------------------------------------------------ otp, counter, score slider */
  function otp(host, onComplete, o = {}) {
    const n = o.length || 6;
    const el = h('div', { class: 'otp', role: 'group', 'aria-label': o.label || `${n}-digit code` });
    const ins = Array.from({ length: n }, (_, i) => h('input', { type: 'text', inputmode: 'numeric', pattern: '[0-9]*',
      autocomplete: i === 0 ? 'one-time-code' : 'off', maxlength: i === 0 ? String(n) : '1', 'aria-label': `Digit ${i + 1} of ${n}` }));
    el.append(...ins);
    const value = () => ins.map(x => x.value).join('');
    const fill = (from, digits) => {
      [...digits].slice(0, n - from).forEach((d, k) => { ins[from + k].value = d; });
      const next = Math.min(n - 1, from + digits.length);
      ins[next].focus();
      el.removeAttribute('aria-invalid');
      if (value().length === n && onComplete) onComplete(value());
    };
    ins.forEach((inp, i) => {
      inp.addEventListener('input', () => {
        const d = inp.value.replace(/\D/g, '');
        inp.value = '';
        if (d) fill(i, d); else inp.value = '';
      });
      inp.addEventListener('keydown', e => {
        if (e.key === 'Backspace' && !inp.value && i > 0) { e.preventDefault(); ins[i - 1].value = ''; ins[i - 1].focus(); }
        else if (e.key === 'ArrowLeft' && i > 0) { e.preventDefault(); ins[i - 1].focus(); }
        else if (e.key === 'ArrowRight' && i < n - 1) { e.preventDefault(); ins[i + 1].focus(); }
      });
      inp.addEventListener('paste', e => {
        const d = (e.clipboardData && e.clipboardData.getData('text') || '').replace(/\D/g, '');
        if (!d) return;
        e.preventDefault();
        fill(d.length >= n ? 0 : i, d);
      });
      inp.addEventListener('focus', () => inp.select());
    });
    put(host, el);
    return {
      el, value,
      clear() { ins.forEach(x => { x.value = ''; }); ins[0].focus(); },
      invalid(on = true) { if (on) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid'); },
      focus() { (ins.find(x => !x.value) || ins[n - 1]).focus(); },
      disable(on = true) { ins.forEach(x => { x.disabled = on; }); },
    };
  }
  function counter(field, max) {
    const el = h('span', { class: 'counter', id: uid('c') });
    let over = false;
    const draw = () => {
      const len = [...field.value].length;
      el.textContent = `${fmtN(len)}/${fmtN(max)}`;
      el.classList.toggle('near', len >= max * 0.9 && len <= max);
      el.classList.toggle('over', len > max);
      if (len > max) field.setAttribute('aria-invalid', 'true');
      else if (over) field.removeAttribute('aria-invalid');
      over = len > max;
    };
    field.setAttribute('aria-describedby', [field.getAttribute('aria-describedby'), el.id].filter(Boolean).join(' '));
    field.addEventListener('input', draw);
    field.after(el);
    draw();
    return el;
  }
  function scoreSlider(host, o = {}) {
    const min = o.min ?? 200, max = o.max ?? 800, step = o.step ?? 10;
    const clamp = v => Math.min(max, Math.max(min, Math.round((Number(v) - min) / step) * step + min));
    let value = clamp(o.value ?? min);
    const range = h('input', { type: 'range', min, max, step, 'aria-label': o.label || 'Score' });
    const field = h('input', { type: 'number', class: 'field', min, max, step, inputmode: 'numeric', 'aria-label': `${o.label || 'Score'}, typed` });
    const bubble = h('span', { class: 'bubble', 'aria-hidden': 'true' });
    const el = h('div', { class: 'score-slider' }, bubble, range, field);
    const paint = () => {
      const p = (value - min) / (max - min);
      el.style.setProperty('--p', p);
      range.style.setProperty('--p', `${p * 100}%`);
      bubble.textContent = fmtN(value);
      range.value = value;
      range.setAttribute('aria-valuetext', fmtN(value));
      if (doc.activeElement !== field) field.value = value;
    };
    range.addEventListener('input', () => { value = +range.value; field.value = value; paint(); if (o.onInput) o.onInput(value); });
    range.addEventListener('change', () => o.onChange && o.onChange(value));
    field.addEventListener('change', () => { if (field.value === '') { field.value = value; return; } value = clamp(field.value); field.value = value; paint(); if (o.onChange) o.onChange(value); });
    field.addEventListener('keydown', e => { if (e.key === 'Enter') field.dispatchEvent(new Event('change')); });
    paint();
    put(host, el);
    return { el, range, field, get value() { return value; }, set(v, silent) { value = clamp(v); paint(); if (!silent && o.onChange) o.onChange(value); } };
  }

  /* ------------------------------------------------------------ images (R17) */
  const IMG_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'];
  async function downscale(file, maxEdge) {
    if (file.type === 'image/gif' || typeof createImageBitmap !== 'function') return file;     // GIFs may move: kept as sent
    let bmp;
    try { bmp = await createImageBitmap(file); } catch (_) { return file; }
    const k = Math.min(1, maxEdge / Math.max(bmp.width, bmp.height));
    if (k === 1) { bmp.close && bmp.close(); return file; }
    const c = doc.createElement('canvas');
    c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
    c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
    bmp.close && bmp.close();
    const blob = await new Promise(r => c.toBlob(r, file.type, 0.9));
    return blob ? new File([blob], file.name, { type: blob.type }) : file;
  }
  function images(host, o = {}) {
    const max = o.max ?? 10, maxBytes = o.maxBytes ?? 10 * 1024 * 1024, maxEdge = o.maxEdge ?? 2000;
    const files = [];
    const input = h('input', { type: 'file', accept: IMG_TYPES.join(','), multiple: true, hidden: true });
    const add = h('button', { type: 'button', class: 'thumbs-add' }, icon('plus'), h('span', { text: o.label || 'Add image' }));
    const el = h('div', { class: 'thumbs', role: 'group', 'aria-label': o.groupLabel || 'Images' }, add, input);
    const status = h('p', { class: 'sr', role: 'status' });
    el.append(status);
    const draw = (emit = true) => { add.hidden = files.length >= max; status.textContent = `${files.length} of ${max} images`; if (emit && o.onChange) o.onChange([...files]); };
    async function take(list) {
      for (const f of [...list]) {
        if (files.length >= max) { toast(`Up to ${max} images`); break; }
        if (!IMG_TYPES.includes(f.type)) { toast('Only PNG, JPEG, WebP or GIF images'); continue; }
        const g = await downscale(f, maxEdge);
        if (g.size > maxBytes) { toast(`${f.name || 'That image'} is over ${Math.round(maxBytes / 1048576)} MB`); continue; }
        const url = URL.createObjectURL(g);
        const fig = h('figure', {}, h('img', { src: url, alt: g.name || 'Image' }));
        const entry = { file: g, url, fig };
        fig.append(xBtn(`Remove ${g.name || 'image'}`, () => { files.splice(files.indexOf(entry), 1); URL.revokeObjectURL(url); fig.remove(); draw(); add.focus(); }));
        files.push(entry);
        el.insertBefore(fig, add);
      }
      draw();
    }
    add.addEventListener('click', () => input.click());
    input.addEventListener('change', () => { take(input.files); input.value = ''; });
    const drop = o.dropTarget || el;
    drop.addEventListener('dragover', e => { if ([...e.dataTransfer.items].some(i => i.kind === 'file')) { e.preventDefault(); drop.classList.add('drag'); } });
    drop.addEventListener('dragleave', () => drop.classList.remove('drag'));
    drop.addEventListener('drop', e => { e.preventDefault(); drop.classList.remove('drag'); take(e.dataTransfer.files); });
    let pasteRoot = null;
    const onPaste = e => {
      if (!el.isConnected) { pasteRoot.removeEventListener('paste', onPaste); return; }
      const fs = [...(e.clipboardData ? e.clipboardData.files : [])].filter(f => f.type.startsWith('image/'));
      if (fs.length) { e.preventDefault(); take(fs); }
    };
    queueMicrotask(() => { pasteRoot = o.pasteTarget || el.closest('dialog, form') || doc; pasteRoot.addEventListener('paste', onPaste); });
    draw(false);                 // building it is not a change
    put(host, el);
    return { el, files: () => files.map(x => x.file), clear() { files.splice(0).forEach(x => { URL.revokeObjectURL(x.url); x.fig.remove(); }); draw(); }, add: take };
  }

  /* ------------------------------------------------------------ exam date (T12, U17) */
  function examDate(anchor, o = {}) {
    const today = isoDay(new Date());
    const cur = o.value || null;
    const src = (o.dates || UI.SAT_DATES || []).map(d => typeof d === 'string' ? { date: d } : d)
      .filter(d => d && d.date >= today).sort((a, b) => a.date < b.date ? -1 : 1);
    const rec = src.find(d => d.tag === 'Steady' && (!cur || d.date > cur));
    const inDays = d => { const n = dayDiff(today, d); return n === 0 ? 'today' : n === 1 ? 'tomorrow' : `in ${fmtN(n)} days`; };
    // a deadline that has passed moves on to the late one, then to closed
    const registration = d => {
      if (d.register_by && d.register_by >= today) return [`register by ${date(d.register_by)}`, d.late_by && `late ${date(d.late_by)}`];
      if (d.late_by && d.late_by >= today) return [`late registration by ${date(d.late_by)}`];
      return d.register_by || d.late_by ? ['registration closed'] : [];
    };
    const save = async v => {
      try { if (o.onSave) await o.onSave(v); }
      catch (_) { toast('Couldn’t save the date. Try again.'); }
    };
    const options = src.map(d => ({
      value: d.date,
      label: `${date(d.date)} · ${DOW[toDate(d.date).getDay()].slice(0, 3)}`,
      sub: [inDays(d.date), d.study_days !== undefined && d.study_days !== null && `${fmtN(d.study_days)} study days`,
        d.per_week !== undefined && d.per_week !== null && `+${fmtN(d.per_week)} a week`, d.tag,
        ...registration(d),
        d.projected !== undefined && d.projected !== null && `~${fmtN(d.projected)}`].filter(Boolean).join(' · '),
      meta: d === rec ? h('span', { class: 'badge', text: 'Recommended' }) : null,
    }));
    options.push({ value: '__other', label: 'Another date…' }, { value: '__none', label: cur ? 'Remove date' : 'No date yet' });
    const trigger = anchor instanceof Element ? anchor : null;
    return pop(anchor, options, { role: 'listbox', label: o.title || 'SAT date', value: cur || (o.none === false ? '' : '__none'), className: 'exam-dates',
      onPick: v => {
        if (v === '__none') { save(null); return; }
        if (v !== '__other') { save(v); return; }
        setTimeout(() => pop(anchor, (p, res) => {
          const f = h('input', { type: 'date', class: 'field sm', min: today, value: cur || '', 'aria-label': 'Your SAT date' });
          const go = h('button', { type: 'button', class: 'pill sm', text: 'Save' });
          const err = h('p', { class: 'field-err', hidden: true, text: 'Pick today or a later date.' });
          go.addEventListener('click', async () => {
            if (!f.value || f.value < today) { err.hidden = false; f.setAttribute('aria-invalid', 'true'); return; }
            await save(f.value); res.close();
          });
          f.addEventListener('keydown', e => { if (e.key === 'Enter') go.click(); });
          return h('div', { class: 'date-form' }, h('label', { class: 'label', text: 'Another date' }), f, err, go);
        }, { label: 'Another SAT date', trigger, restore: trigger }), 0);
      } });
  }

  /* ------------------------------------------------------------ action bar, selection bar */
  function actionBar(host, o = {}) {
    const t = h('span', { class: 'selbar-n', role: 'status' });
    const acts = h('span', { style: 'display: contents' });
    const el = h('div', { class: 'selbar', hidden: true }, t, acts);
    const set = (text, n) => {
      el.hidden = text === null || text === undefined || text === '';
      t.textContent = text || '';
      acts.replaceChildren(...(o.actions || []).map(a => {
        const b = button({ ...a, label: typeof a.label === 'function' ? a.label(n) : a.label }, true);
        if (a.onClick) b.addEventListener('click', e => a.onClick(n, e));
        return b;
      }));
    };
    set(o.text, o.n);
    put(host, el);
    return { el, set };
  }
  function selbar(host, o = {}) {
    const bar = actionBar(host, { actions: [...(o.actions || []), { label: 'Clear', quiet: true, onClick: () => o.onClear && o.onClear() }] });
    return { el: bar.el, update: n => bar.set(n ? `${fmtN(n)} selected` : null, n) };
  }

  /* ------------------------------------------------------------ tile, meter, skeleton, card error */
  // the count runs once, when the tile first shows. The real number stays in the text (screen
  // readers, print, anything reading textContent); the moving one is drawn over it (.counting in ui.css)
  function countUp(el, to, fmt) {
    el.textContent = fmt(to);
    if (still() || !Number.isInteger(to) || to <= 0 || typeof IntersectionObserver !== 'function') return;
    el.classList.add('counting');
    el.dataset.n = fmt(0);
    const io = new IntersectionObserver(es => {
      if (!es.some(e => e.isIntersecting)) return;
      io.disconnect();
      const t0 = performance.now();
      const step = t => {
        const k = Math.min(1, (t - t0) / 600);
        if (k < 1) { el.dataset.n = fmt(Math.round(to * (1 - Math.pow(1 - k, 3)))); requestAnimationFrame(step); }
        else { el.classList.remove('counting'); delete el.dataset.n; }
      };
      requestAnimationFrame(step);
    });
    io.observe(el);
  }
  function spark(values, label) {
    const v = values.map(Number).filter(x => isFinite(x));
    const s = sv('svg', { class: 'stat-spark', viewBox: '0 0 100 24', preserveAspectRatio: 'none', role: 'img',
      'aria-label': v.length ? `${label || 'Trend'}: ${fmtN(v[0])} to ${fmtN(v[v.length - 1])} over ${v.length} days` : 'No trend yet' });
    if (v.length < 2) return s;
    const lo = Math.min(...v), hi = Math.max(...v), span = hi - lo || 1;
    const pts = v.map((x, i) => `${(i / (v.length - 1) * 100).toFixed(2)},${(22 - (x - lo) / span * 20).toFixed(2)}`).join(' ');
    sv('polyline', { points: pts, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', 'vector-effect': 'non-scaling-stroke' }, s);
    return s;
  }
  function tile(host, o = {}) {
    const tag = o.href ? 'a' : (o.filter || o.onClick) ? 'button' : 'div';
    const el = h(tag, { class: 'stat' + (o.className ? ' ' + o.className : ''), href: o.href || null, type: tag === 'button' ? 'button' : null });
    let first = true;
    const kEl = h('span', { class: 'stat-k' }), vEl = h('span', { class: 'stat-v' }), subEl = h('span', { class: 'stat-sub' }),
      dEl = h('span', { class: 'stat-delta' });
    el.append(kEl, vEl, subEl, dEl);
    function set(p = {}) {
      Object.assign(o, p);
      kEl.textContent = o.label || '';
      const fmt = o.format || (x => typeof x === 'number' ? num(x) : String(x));
      const missing = o.value === null || o.value === undefined || o.value === '';
      const valSpan = h('span');
      vEl.replaceChildren(valSpan, o.unit && !missing ? h('small', { text: ` ${o.unit}` }) : '');
      if (missing) valSpan.textContent = '—';
      else if (first && typeof o.value === 'number' && o.countUp !== false) countUp(valSpan, o.value, fmt);
      else valSpan.textContent = fmt(o.value);
      first = false;
      if (o.fact && tag === 'div') fact(vEl, o.fact, { label: o.label, value: missing ? '—' : fmt(o.value) + (o.unit ? ` ${o.unit}` : '') });
      subEl.textContent = missing && o.missing !== false ? (o.missing || o.sub || '') : (o.sub || '');
      subEl.hidden = !subEl.textContent;
      const d = o.delta;
      dEl.textContent = d === null || d === undefined ? '' : typeof d === 'number' ? `${d > 0 ? '▲' : d < 0 ? '▼' : '='} ${fmt(Math.abs(d))}` : d;
      dEl.hidden = !dEl.textContent;
      const old = el.querySelector('.stat-spark');
      if (old) old.remove();
      if (o.spark) el.append(spark(o.spark, o.label));
      if (o.filter) el.setAttribute('aria-pressed', String(!!o.pressed));
    }
    if (tag === 'button') el.addEventListener('click', () => {
      if (o.filter) { o.pressed = !o.pressed; el.setAttribute('aria-pressed', String(o.pressed)); }
      if (o.onClick) o.onClick(o.filter ? o.pressed : undefined);
    });
    set();
    put(host, el);
    return { el, set };
  }
  function meter(host, o = {}) {
    const lid = uid('mk');
    const k = h('span', { class: 'meter-k', id: lid }), n = h('span', { class: 'meter-n' }), fill = h('i'), tick = h('b', { hidden: true });
    const bar = h('div', { class: 'meter-bar', role: 'meter', 'aria-labelledby': lid, 'aria-valuemin': '0' }, fill, tick);
    const el = h('div', { class: 'meter' + (o.ink ? ' ink' : '') + (o.lg ? ' lg' : '') }, k, n, bar);
    function set(p = {}) {
      Object.assign(o, p);
      const max = o.max || 0, v = o.value || 0;
      k.textContent = o.label || '';
      n.textContent = o.text || (max ? `${fmtN(v)} of ${fmtN(max)}${o.unit ? ' ' + o.unit : ''}` : `${fmtN(v)}${o.unit ? ' ' + o.unit : ''}`);
      bar.style.setProperty('--p', max ? Math.min(1, v / max) : 0);
      bar.setAttribute('aria-valuemax', String(max || 1));
      bar.setAttribute('aria-valuenow', String(Math.min(v, max || v)));
      bar.setAttribute('aria-valuetext', n.textContent);
      el.classList.toggle('done', !!max && v >= max);
      tick.hidden = o.tick === undefined || o.tick === null;
      if (!tick.hidden) bar.style.setProperty('--t', max ? o.tick / max : o.tick);
    }
    set();
    put(host, el);
    return { el, set };
  }
  function skel(host, shape = 'line') {
    const s = (cls, style) => h('span', { class: 'skel' + (cls ? ' ' + cls : ''), style: style || null });
    let el;
    const [kind, arg] = typeof shape === 'string' ? shape.split(':') : ['box'];
    const n = Math.max(1, +arg || 3);
    const px = v => typeof v === 'number' ? `${v}px` : v;
    if (typeof shape === 'object') el = s('', `width: ${px(shape.w ?? '100%')}; height: ${px(shape.h ?? 12)}; border-radius: ${px(shape.r ?? 8)}`);
    else if (kind === 'line') el = s('line');
    else if (kind === 'line.lg') el = s('line lg');
    else if (kind === 'lines') el = h('div', {}, Array.from({ length: n }, (_, i) => s('line', i === n - 1 ? 'width: 62%' : '')));
    else if (kind === 'num') el = s('num');
    else if (kind === 'circle') el = s('circle', `width: ${arg || 36}px; height: ${arg || 36}px`);
    else if (kind === 'pill') el = s('pill-s');
    else if (kind === 'tile') el = h('div', { class: 'stat' }, s('line', 'width: 40%; margin-top: 0'), s('num', 'margin-top: 10px'), s('line', 'width: 60%'));
    else if (kind === 'card') el = h('div', {}, s('line lg', 'width: 38%'), Array.from({ length: n }, (_, i) => s('line', i === n - 1 ? 'width: 55%' : '')));
    else if (kind === 'row' || kind === 'rows') el = h('div', {}, Array.from({ length: kind === 'row' ? 1 : n }, () => h('div', { style: 'display: flex; align-items: center; gap: 12px; padding: 10px 0' }, s('circle', 'width: 28px; height: 28px; flex: none'), h('div', { style: 'flex: 1' }, s('line', 'width: 60%; margin: 4px 0'), s('line', 'width: 35%; margin: 6px 0 0')))));
    else if (kind === 'table') el = h('div', {}, Array.from({ length: n }, () => s('line', 'height: 16px; margin: 14px 0')));
    else if (kind === 'chart') el = s('', `height: ${arg || 160}px; border-radius: 10px`);
    else if (kind === 'cells') el = h('div', { class: 'cell-grid' }, Array.from({ length: +arg || 22 }, () => s('', 'width: var(--cell, 40px); height: var(--cell, 40px)')));
    else el = s('line');
    el.setAttribute('aria-hidden', 'true');
    return put(host, el);
  }
  function cardError(host, retry, text) {
    const t = h('span', { text: text || 'Couldn’t load this.' });
    const el = h('div', { class: 'card-err', role: 'alert' }, t);
    if (retry) {
      const b = h('button', { type: 'button', class: 'btn sm', text: 'Retry' });
      b.addEventListener('click', async () => {
        b.setAttribute('aria-busy', 'true');
        try { await retry(); } catch (_) { t.textContent = 'Still couldn’t load this. Check your connection and try again.'; }
        finally { b.removeAttribute('aria-busy'); }
      });
      el.append(b);
    }
    if (host) { [...host.children].forEach(c => { if (!c.classList.contains('card-head')) c.remove(); }); host.append(el); }
    return el;
  }

  /* ------------------------------------------------------------ table */
  function table(host, cols, rows, o = {}) {
    let data = [...(rows || [])];
    let sort = o.sort ? { ...o.sort } : null;
    const wrap = h('div', { class: 'table-wrap', tabindex: '0', role: 'region', 'aria-label': o.label || 'Table, scrolls sideways' });
    const tbl = h('table', { class: 'table' + (o.compact ? ' compact' : '') + (o.hover || o.onRow ? ' hover' : '') });
    if (o.caption) tbl.append(h('caption', { text: o.caption }));
    const thead = h('thead'), tbody = h('tbody');
    const tr = h('tr');
    const lastStick = cols.map(c => !!c.stick).lastIndexOf(true);      // the pinned edge carries the shadow
    const stickCls = (c, i) => [c.stick && (i ? 'stick-2' : 'stick'), c.stick && (c.stickLast || i === lastStick) && 'stick-last'];
    const ths = cols.map((c, i) => {
      const th = h('th', { scope: 'col', class: [c.num && 'n', ...stickCls(c, i)].filter(Boolean).join(' ') || null, style: c.width ? `width: ${c.width}px` : null });
      if (c.sort !== false && (c.sort || o.sortable)) {
        const b = h('button', { type: 'button' }, c.label);
        b.addEventListener('click', () => sortBy(c.key, sort && sort.key === c.key && sort.dir === 'asc' ? 'desc' : (sort && sort.key === c.key ? 'asc' : (c.num ? 'desc' : 'asc'))));
        b.addEventListener('focus', () => th.scrollIntoView({ inline: 'nearest', block: 'nearest' }));
        if (c.title) tooltip(b, c.title);
        th.append(b);
      } else if (c.title) {
        const b = h('button', { type: 'button', 'aria-label': c.ariaLabel || c.title }, c.label);
        b.addEventListener('focus', () => th.scrollIntoView({ inline: 'nearest', block: 'nearest' }));
        tooltip(b, c.title);
        th.append(b);
      } else th.append(c.label ?? '');
      tr.append(th);
      return th;
    });
    thead.append(tr);
    tbl.append(thead, tbody);
    wrap.append(tbl);
    const val = (c, r) => c.value ? c.value(r) : r[c.key];
    function sortBy(key, dir = 'asc', silent) {
      sort = { key, dir };
      if (o.onSort && !silent) { if (o.onSort(key, dir) === true) { draw(); return; } }
      const c = cols.find(x => x.key === key);
      if (c && !o.serverSort) {
        const f = typeof c.sort === 'function' ? c.sort : (a, b) => {
          const x = val(c, a), y = val(c, b);
          if (x === null || x === undefined) return 1;
          if (y === null || y === undefined) return -1;
          return (typeof x === 'number' && typeof y === 'number' ? x - y : String(x).localeCompare(String(y), 'en', { numeric: true })) * (dir === 'desc' ? -1 : 1);
        };
        data = data.map((r, i) => [r, i]).sort((a, b) => f(a[0], b[0]) || a[1] - b[1]).map(x => x[0]);   // stable
      }
      draw();
    }
    function draw() {
      ths.forEach((th, i) => { if (sort && cols[i].key === sort.key) th.setAttribute('aria-sort', sort.dir === 'desc' ? 'descending' : 'ascending'); else th.removeAttribute('aria-sort'); });
      if (!data.length) { tbody.replaceChildren(h('tr', {}, h('td', { colspan: cols.length, class: 'empty-cell', text: o.empty || 'Nothing here yet.' }))); edges(); return; }
      tbody.replaceChildren(...data.map(r => {
        const row = h('tr', { class: o.you && o.you(r) ? 'you' : null });
        cols.forEach((c, i) => {
          const v = c.render ? c.render(r) : val(c, r);
          row.append(h(c.header ? 'th' : 'td', { class: [c.num && 'n', ...stickCls(c, i)].filter(Boolean).join(' ') || null,
            scope: c.header ? 'row' : null, title: c.cellTitle ? c.cellTitle(r) : null },
            v instanceof Node ? v : (v === null || v === undefined || v === '' ? '—' : (typeof v === 'number' ? num(v) : String(v)))));
        });
        if (o.onRow) {
          row.tabIndex = 0;
          row.style.cursor = 'pointer';
          row.addEventListener('click', e => { if (!e.target.closest('a, button, input')) o.onRow(r, e); });
          row.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target === row) o.onRow(r, e); });
        }
        return row;
      }));
      edges();
    }
    function edges() {
      // the second pinned column starts where the first one ends
      const s1 = tbl.querySelector('thead th.stick');
      if (s1 && s1.offsetWidth) wrap.style.setProperty('--stick-1', `${s1.offsetWidth}px`);
      const max = wrap.scrollWidth - wrap.clientWidth;
      wrap.classList.toggle('more-l', wrap.scrollLeft > 1);
      wrap.classList.toggle('more-r', wrap.scrollLeft < max - 1);
      if (max <= 1) wrap.removeAttribute('tabindex'); else wrap.tabIndex = 0;
    }
    wrap.addEventListener('scroll', edges, { passive: true });
    if (typeof ResizeObserver === 'function') new ResizeObserver(edges).observe(wrap);
    wrap.addEventListener('keydown', e => {
      if (e.target !== wrap || (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft')) return;
      e.preventDefault();
      const w = (ths.find(th => !th.classList.contains('stick') && !th.classList.contains('stick-2')) || ths[0]).offsetWidth || 120;
      wrap.scrollBy({ left: e.key === 'ArrowRight' ? w : -w, behavior: still() ? 'auto' : 'smooth' });
    });
    if (sort) sortBy(sort.key, sort.dir, true); else draw();
    put(host, wrap);
    return { el: wrap, table: tbl, update(r) { data = [...(r || [])]; if (sort) sortBy(sort.key, sort.dir, true); else draw(); }, sortBy, get sort() { return sort; } };
  }

  /* ------------------------------------------------------------ question states (2.3, R20, R35, R52, SR25) */
  const STATES = {
    correct: { label: 'Correct', glyph: '✓' }, incorrect: { label: 'Incorrect', glyph: '✕' },
    mixed: { label: 'Mixed', glyph: '~', help: 'right on a retry' }, repaired: { label: 'Repaired', glyph: '↻', help: 'right on the repair after a miss' },
    fixed: { label: 'Fixed since', glyph: '✕✓' }, unanswered: { label: 'Unanswered', glyph: '–' }, blank: { label: 'Blank', glyph: '–' },
    skipped: { label: 'Skipped', glyph: '»' }, voided: { label: 'Voided', glyph: '⊘' }, removed: { label: 'Removed from scoring', glyph: '⊖' },
    repeat: { label: 'Repeat', glyph: '=' }, not_reached: { label: 'Not reached', glyph: '·' }, answered: { label: 'Answered', glyph: '' },
    future: { label: 'Not yet', glyph: '' },
    unmet: { label: 'Unmet', glyph: '' }, met: { label: 'Met', glyph: '' }, ready: { label: 'Ready', glyph: '✓' },
    // overlays
    flag: { label: 'Flagged', overlay: 'flag' }, saved: { label: 'Saved', overlay: 'saved' }, note: { label: 'Has note', overlay: 'note' },
    open: { label: 'Open mistake', overlay: 'open' }, fixing: { label: 'Being fixed', overlay: 'fixing' }, current: { label: 'Current', overlay: 'current' },
    due: { label: 'Check-in due', overlay: 'due' }, over: { label: 'Over its time', overlay: 'over' },
    easy: { label: 'Easy', tier: 'easy' }, medium: { label: 'Medium', tier: 'medium' }, hard: { label: 'Hard', tier: 'hard' },
  };
  const TIERS = { 1: 'easy', 2: 'medium', 3: 'hard', e: 'easy', m: 'medium', h: 'hard', easy: 'easy', medium: 'medium', hard: 'hard' };
  const tierOf = t => TIERS[String(t ?? '').toLowerCase()] || null;
  const overlayWords = o => [o.flag && 'flagged', o.saved && 'saved', o.note && 'has a note', o.open && 'open mistake', o.fixing && 'being fixed', o.due && 'check-in due', o.over && 'over its time'].filter(Boolean);

  function cell(state, n, o = {}) {
    const tag = o.href ? 'a' : o.static ? 'span' : 'button';
    const st = STATES[state] || { label: cap(String(state || '')) };
    const el = h(tag, { class: 'cell' + (o.size ? ' ' + o.size : ''), 'data-status': state, type: tag === 'button' ? 'button' : null, href: o.href || null,
      'data-flag': o.flag, 'data-note': o.note, 'data-open': o.open, 'data-fixing': o.fixing, 'data-over': o.over, 'data-saved': o.saved,
      'data-tier': tierOf(o.tier), 'data-level': o.level ?? null, 'aria-current': o.current ? 'true' : null,
      'data-filtered': o.filtered, tabindex: o.filtered && tag !== 'span' ? '-1' : null,
      'aria-label': o.label || [`${o.noun || 'Question'} ${n}`, st.label, tierOf(o.tier) && STATES[tierOf(o.tier)].label,
        o.level !== undefined && o.level !== null && `level ${o.level}`, ...overlayWords(o), o.current && 'on screen'].filter(Boolean).join(', ') },
      h('span', { class: 'n', text: n ?? '', 'aria-hidden': 'true' }));
    if (o.onClick) el.addEventListener('click', e => o.onClick(e));
    if (o.tip) tooltip(el, o.tip);
    return el;
  }
  function swatch(key) {
    const s = STATES[key] || {};
    const a = { class: 'sw', 'aria-hidden': 'true' };
    if (s.overlay) a[s.overlay === 'current' ? 'data-current' : `data-${s.overlay}`] = '';
    else if (s.tier) a['data-tier'] = s.tier;
    else a['data-status'] = key;
    return h('i', a);
  }
  function legend(host, keys, counts = {}, o = {}) {
    const el = h('ul', { class: 'legend', 'aria-label': o.label || 'Legend' });
    const pressed = new Set(o.pressed || []);
    let cur = { ...counts };
    function draw() {
      el.replaceChildren(...keys.map(k0 => {
        const k = typeof k0 === 'object' ? k0.key : k0;
        const label = (typeof k0 === 'object' && k0.label) || (STATES[k] || {}).label || cap(k);
        const n = cur[k];
        const body = [swatch(k), label, n !== undefined && n !== null ? h('b', { text: fmtN(n) }) : null];
        if (!o.onFilter) return h('li', {}, body);
        const b = h('button', { type: 'button', 'aria-pressed': String(pressed.has(k)), disabled: n === 0 }, body);
        b.addEventListener('click', () => { pressed.has(k) ? pressed.delete(k) : pressed.add(k); b.setAttribute('aria-pressed', String(pressed.has(k))); o.onFilter(k, pressed.has(k), [...pressed]); });
        return h('li', {}, b);
      }));
    }
    draw();
    put(host, el);
    return { el, update(c) { cur = { ...c }; draw(); }, pressed: () => [...pressed] };
  }
  // dense grids (strip, atlas, heatmap; rule 9): cells sit closer than 44px, so no cell can have
  // a 44px box of its own. A tap in the grid's gaps, or in the --touch band .near-tap adds
  // around it on a coarse pointer, picks the nearest cell within 22px.
  function nearTap(box, sel) {
    box.classList.add('near-tap');
    box.addEventListener('click', e => {
      if (e.target.closest(sel) || (e.target !== box && e.target.getAttribute('role') !== 'row')) return;
      let best = null, bd = 22 * 22;
      box.querySelectorAll(sel).forEach(c => {
        if (c.disabled || c.hasAttribute('data-filtered')) return;
        const r = c.getBoundingClientRect();
        const dx = Math.max(r.left - e.clientX, 0, e.clientX - r.right), dy = Math.max(r.top - e.clientY, 0, e.clientY - r.bottom);
        if (dx * dx + dy * dy <= bd) { bd = dx * dx + dy * dy; best = c; }
      });
      if (best) { best.focus({ preventScroll: true }); best.click(); }
    });
    return box;
  }
  function strip(host, marks, o = {}) {
    const el = h('div', { class: 'strip' + (o.fit ? ' fit' : ''), role: o.onPick ? 'group' : 'img' });
    const norm = (m, i) => typeof m === 'string' ? { status: m, n: i + 1 } : { n: i + 1, ...m };
    let list = marks.map(norm);
    function draw() {
      const kids = [];
      list.forEach((m, i) => {
        if (o.marker === i) kids.push(h('i', { class: 'strip-mark', 'aria-hidden': 'true' }));
        const st = STATES[m.status] || { label: m.status };
        const a = { 'data-status': m.status, 'data-flag': m.flag, 'data-open': m.open, 'data-fixing': m.fixing, 'aria-current': m.current ? 'true' : null };
        if (o.onPick) {
          const b = h('button', { type: 'button', ...a, tabindex: '-1', 'aria-label': m.label || [`${o.noun || 'Question'} ${m.n}`, st.label, ...overlayWords(m)].join(', ') });
          b.addEventListener('click', () => o.onPick(i, m));
          kids.push(b);
        } else kids.push(h('span', { ...a, 'aria-hidden': 'true' }));
      });
      if (o.marker === list.length) kids.push(h('i', { class: 'strip-mark', 'aria-hidden': 'true' }));
      el.replaceChildren(...kids);
      if (o.onPick) {
        const bs = [...el.querySelectorAll('button')];
        (bs.find(b => b.getAttribute('aria-current') === 'true') || bs[0] || {}).tabIndex = 0;
      } else {
        const tally = {};
        list.forEach(m => { tally[m.status] = (tally[m.status] || 0) + 1; });
        el.setAttribute('aria-label', o.label || `${list.length} questions: ` + Object.entries(tally).map(([k, v]) => `${v} ${((STATES[k] || {}).label || k).toLowerCase()}`).join(', '));
      }
    }
    el.addEventListener('keydown', e => {
      const bs = [...el.querySelectorAll('button')], i = bs.indexOf(doc.activeElement);
      if (i < 0) return;
      const j = { ArrowRight: i + 1, ArrowDown: i + 1, ArrowLeft: i - 1, ArrowUp: i - 1, Home: 0, End: bs.length - 1 }[e.key];
      if (j === undefined) return;
      e.preventDefault();
      const b = bs[Math.max(0, Math.min(bs.length - 1, j))];
      bs.forEach(x => { x.tabIndex = x === b ? 0 : -1; });
      b.focus();
    });
    if (o.onPick) nearTap(el, 'button');
    draw();
    put(host, el);
    return { el, set(i, m) { list[i] = norm(m, i); draw(); }, update(ms) { list = ms.map(norm); draw(); } };
  }
  const pips = (owed, of = 2) => {
    const given = Math.max(0, Math.min(of, of - (owed || 0)));
    return h('span', { class: 'pips', role: 'img', 'aria-label': `${given} of ${of} clean answers` }, Array.from({ length: of }, (_, i) => h('i', { class: i < given ? 'on' : null })));
  };
  const dbars = (tier, o = {}) => {
    const t = tierOf(tier) || 'medium';
    const word = STATES[t].label;
    return h('span', { class: 'dbars' + (o.bare ? ' bare' : ''), 'data-tier': t, 'aria-label': o.bare ? word : null, role: o.bare ? 'img' : null, text: word });
  };

  /* ------------------------------------------------------------ the type map (U8, P14) */
  function atlas(host, types, o = {}) {
    const el = h('div', { class: 'atlas' + (o.sm ? ' sm' : ''), role: 'row', 'aria-label': o.label || null });
    if (host) { if (!host.closest('[role="grid"]')) { host.setAttribute('role', 'grid'); if (o.gridLabel) host.setAttribute('aria-label', o.gridLabel); } }
    const sel = new Set(types.filter(t => t.selected).map(t => t.template));
    const cells = types.map((t, i) => {
      const st = STATES[t.status] || { label: t.status };
      const c = h(o.onPick || o.selectable ? 'button' : 'span', { type: o.onPick || o.selectable ? 'button' : null, role: 'gridcell',
        'data-status': t.status, 'data-open': t.open, 'data-fixing': t.fixing, 'data-due': t.due,
        'aria-selected': o.selectable ? String(sel.has(t.template)) : null, tabindex: i === 0 ? '0' : '-1',
        'aria-label': [t.label || t.template, st.label, ...overlayWords(t)].filter(Boolean).join(', ') });
      c._t = t;
      if (o.tip) tooltip(c, () => o.tip(t), { delay: 150 });
      return c;
    });
    el.append(...cells);
    if (o.onPick || o.selectable) nearTap(el, '[role="gridcell"]');
    const emit = () => o.onSelect && o.onSelect([...sel]);
    const toggle = (c, on) => {
      on = on ?? !sel.has(c._t.template);
      if (on) sel.add(c._t.template); else sel.delete(c._t.template);
      c.setAttribute('aria-selected', String(on));
    };
    // selecting: a click toggles; a mouse drag paints; on touch, long-press then drag (P14)
    let down = null, painting = null, suppress = false, timer = 0;
    el.addEventListener('click', e => {
      const c = e.target.closest('[role="gridcell"]');
      if (!c) return;
      if (o.selectable) { if (suppress) { suppress = false; return; } toggle(c); emit(); }
      else if (o.onPick) o.onPick(c._t, c);
    });
    if (o.selectable) {
      el.style.touchAction = 'pan-y';
      const cellAt = e => { const t = doc.elementFromPoint(e.clientX, e.clientY); const c = t && t.closest && t.closest('[role="gridcell"]'); return c && c.parentNode === el ? c : null; };
      const paint = c => { if (c && sel.has(c._t.template) !== painting) { toggle(c, painting); emit(); } };
      const begin = c => { painting = !sel.has(c._t.template); suppress = true; paint(c); };
      el.addEventListener('pointerdown', e => {
        const c = e.target.closest('[role="gridcell"]');
        if (!c || e.button > 0) return;
        down = c; painting = null; suppress = false;
        if (e.pointerType !== 'mouse') timer = setTimeout(() => { if (down) begin(down); }, 420);
      });
      el.addEventListener('pointermove', e => {
        if (!down) return;
        const c = cellAt(e);
        if (painting !== null) { paint(c); return; }
        if (e.pointerType === 'mouse' && e.buttons === 1 && c && c !== down) { begin(down); paint(c); }
        else if (e.pointerType !== 'mouse' && c !== down) clearTimeout(timer);
      });
      const end = () => { clearTimeout(timer); down = null; painting = null; };
      el.addEventListener('pointerup', end);
      el.addEventListener('pointercancel', end);
      el.addEventListener('contextmenu', e => { if (painting !== null || down) e.preventDefault(); });
    }
    el.addEventListener('keydown', e => {
      const i = cells.indexOf(doc.activeElement);
      if (i < 0) return;
      let target = null;
      if (e.key === 'ArrowRight') target = cells[i + 1];
      else if (e.key === 'ArrowLeft') target = cells[i - 1];
      else if (e.key === 'Home') target = cells[0];
      else if (e.key === 'End') target = cells[cells.length - 1];
      else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const grid = el.closest('[role="grid"]');
        const rows = grid ? [...grid.querySelectorAll('.atlas[role="row"]')] : [el];
        const r = rows[rows.indexOf(el) + (e.key === 'ArrowDown' ? 1 : -1)];
        if (r) { const rc = [...r.querySelectorAll('[role="gridcell"]')]; target = rc[Math.min(i, rc.length - 1)]; }
      } else if (e.key === ' ' && o.selectable) { e.preventDefault(); toggle(cells[i]); emit(); return; }
      if (!target) return;
      e.preventDefault();
      doc.querySelectorAll('.atlas [role="gridcell"][tabindex="0"]').forEach(x => { if (x.closest('[role="grid"]') === target.closest('[role="grid"]')) x.tabIndex = -1; });
      target.tabIndex = 0;
      target.focus();
    });
    // one Tab stop per grid: only the first row's first cell starts at 0
    queueMicrotask(() => { const g = el.closest('[role="grid"]'); if (g && g.querySelector('.atlas [role="gridcell"][tabindex="0"]') !== cells[0] && cells[0]) cells[0].tabIndex = -1; });
    put(host, el);
    return {
      el, selected: () => [...sel],
      select(ids) { ids.forEach(t => { const c = cells.find(x => x._t.template === t); if (c) toggle(c, true); }); emit(); },
      clear() { cells.forEach(c => toggle(c, false)); emit(); },
    };
  }

  /* ------------------------------------------------------------ mastery, skill row (R37, T6) */
  const STRONG = 0.8;
  function masteryWord(m, answered) {
    if (!answered || m === null || m === undefined) return 'Not started';
    if (m >= STRONG) return 'Strong';
    if (m < 0.4) return 'Learning';
    return 'Getting there';
  }
  const pct = x => `${Math.round((x || 0) * 100)}%`;
  function skillRow(host, s, o = {}) {
    const topic = s.topic || s.slug;
    const name = s.name || (UI.TOPIC && UI.TOPIC[topic] && UI.TOPIC[topic].short) || topic;
    const acc = s.accuracy ?? (s.answered ? (s.right || 0) / s.answered : null);
    const word = masteryWord(s.mastery, s.answered);
    const el = h('div', { class: 'skill-row' + (s.gain !== undefined ? ' gain' : '') });
    const title = o.href || s.href ? h('a', { href: o.href || s.href, class: 'skill-name' }) : h('span', { class: 'skill-name' });
    title.append((UI.glyph && topic) ? UI.glyph(topic) : '', h('span', { text: name }));
    el.append(title);
    const m = h('div', { class: 'skill-m' },
      h('span', { class: 'mbar', role: 'img', 'aria-label': `Mastery: ${word}` }, h('i', { style: `--m: ${Math.max(0, Math.min(1, s.mastery || 0))}` })),
      h('span', { class: 'skill-word', text: word }),
      h('span', { class: 'meta', text: s.answered ? `${pct(acc)} right of ${fmtN(s.answered)}` : 'no answers yet' }));
    el.append(m);
    if (s.gain !== undefined) {
      // a figure only when there is one: under 5 is a quiet note, not the row's headline
      const small = s.gain === null || s.gain < 5;
      el.append(h('span', { class: 'skill-gain' + (small ? ' small' : ''), text: small ? 'under 5' : `≈ +${Math.round(s.gain)}` }));
      const goal = s.to ?? STRONG;
      el.append(h('div', { class: 'skill-track-wrap' },
        h('span', { class: 'skill-track', role: 'img', 'aria-label': `First-try accuracy ${pct(acc)}; the gain assumes ${pct(goal)}` },
          h('i', { class: 'you', style: `--t: ${acc || 0}` }), h('i', { class: 'goal', style: `--t: ${goal}` })),
        h('span', { class: 'meta', text: `${pct(acc)} → ${pct(goal)}` })));
      const meta = [s.per_test !== undefined && `about ${fmtN(s.per_test)} of 44`, s.need_right && `at least ${fmtN(s.need_right)} right`, Math.round(s.minutes || 0) >= 1 && `~${dur(s.minutes)}`].filter(Boolean);
      if (meta.length) el.append(h('p', { class: 'meta skill-meta', text: meta.join(' · ') }));
      if (s.tiers) el.append(h('p', { class: 'meta skill-tiers', text: ['easy', 'medium', 'hard'].filter(t => s.tiers[t] && s.tiers[t][1]).map(t => `${t[0].toUpperCase()} ${s.tiers[t][0]}/${s.tiers[t][1]}`).join(' · ') }));
    }
    const side = h('div', { class: 'skill-side' });
    if (s.open) side.append(h('span', { class: 'skill-open', 'aria-label': `${s.open} open mistake${s.open === 1 ? '' : 's'}` },
      h('span', { class: 'dots', 'aria-hidden': 'true' }, Array.from({ length: Math.min(3, s.open) }, () => h('i'))), h('span', { class: 'meta', text: fmtN(s.open) })));
    // the answer count is the accuracy line's ("of 6"), so the badge only says the figure is rough
    if (s.pts !== undefined && s.gain === undefined) side.append(pts(null, s.pts, `skill:${topic}`) || '');
    const pr = o.practise;
    if (pr) {
      const count = pr.count ?? 10;
      const b = button({ label: pr.label || `Practise · ${count}`, href: pr.href, primary: pr.primary }, true);
      if (!pr.href) b.addEventListener('click', async () => {
        b.setAttribute('aria-busy', 'true');
        try { if (pr.onClick) await pr.onClick(s); else await startDrill(pr.body || { topics: [topic], count, adaptive: true, source: pr.source || 'skill' }); }
        catch (_) { toast('Couldn’t start that set. Try again.'); }
        finally { b.removeAttribute('aria-busy'); }
      });
      side.append(b);
    }
    el.append(side);
    return put(host, el);
  }

  /* ------------------------------------------------------------ avatar (U22) and the local photo */
  const DOMAIN_KEYS = [['Algebra', 'algebra'], ['Advanced Math', 'advanced', 'advanced_math', 'advanced-math'],
    ['Problem-Solving and Data Analysis', 'psda', 'data', 'problem_solving'], ['Geometry and Trigonometry', 'geometry', 'geo', 'geometry_trig']];
  const CORNER = 'M45 8 H30 A22 22 0 0 0 8 30 V45 H34 V41 A7 7 0 0 1 41 34 H45 Z';
  const photoUrls = {};
  function idb(mode, fn) {
    return new Promise((resolve, reject) => {
      if (typeof indexedDB === 'undefined') { reject(new Error('no IndexedDB')); return; }
      const openDb = v => {
        const r = v ? indexedDB.open('satf', v) : indexedDB.open('satf');
        r.onupgradeneeded = () => { if (!r.result.objectStoreNames.contains('photo')) r.result.createObjectStore('photo'); };
        r.onerror = () => reject(r.error);
        r.onsuccess = () => {
          const db = r.result;
          if (!db.objectStoreNames.contains('photo')) { const nv = db.version + 1; db.close(); openDb(nv); return; }
          const tx = db.transaction('photo', mode);
          const req = fn(tx.objectStore('photo'));
          tx.oncomplete = () => { db.close(); resolve(req && req.result); };
          tx.onerror = () => { db.close(); reject(tx.error); };
        };
      };
      openDb();
    });
  }
  const me = l => l || (UI.learner && UI.learner()) || 'me';
  // this device only: never uploaded, no endpoint takes it (U22)
  const localPhoto = {
    async get(learner) { try { return (await idb('readonly', s => s.get(me(learner)))) || null; } catch (_) { return null; } },
    async url(learner) {
      const k = me(learner);
      if (photoUrls[k] !== undefined) return photoUrls[k];
      const b = await localPhoto.get(k);
      return (photoUrls[k] = b ? URL.createObjectURL(b) : null);
    },
    async set(file, learner) {
      const k = me(learner);
      const bmp = await createImageBitmap(file);
      const side = Math.min(bmp.width, bmp.height), c = doc.createElement('canvas');
      c.width = c.height = 256;
      c.getContext('2d').drawImage(bmp, (bmp.width - side) / 2, (bmp.height - side) / 2, side, side, 0, 0, 256, 256);
      bmp.close && bmp.close();
      let blob = await new Promise(r => c.toBlob(r, 'image/webp', 0.85));
      if (!blob || blob.type !== 'image/webp') blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.85));
      await idb('readwrite', s => s.put(blob, k));
      if (photoUrls[k]) URL.revokeObjectURL(photoUrls[k]);
      photoUrls[k] = URL.createObjectURL(blob);
      doc.querySelectorAll('.avatar[data-self]').forEach(a => a.dispatchEvent(new Event('satf:photo')));
      return photoUrls[k];
    },
    async remove(learner) {
      const k = me(learner);
      try { await idb('readwrite', s => s.delete(k)); } catch (_) {}
      if (photoUrls[k]) URL.revokeObjectURL(photoUrls[k]);
      photoUrls[k] = null;
      doc.querySelectorAll('.avatar[data-self]').forEach(a => a.dispatchEvent(new Event('satf:photo')));
    },
  };
  function domainMastery(p) {
    const d = p.domains;
    if (!d) return [0, 0, 0, 0];
    if (Array.isArray(d)) return [0, 1, 2, 3].map(i => +(d[i] && typeof d[i] === 'object' ? d[i].mastery : d[i]) || 0);
    return DOMAIN_KEYS.map(keys => { const k = keys.find(x => d[x] !== undefined); const v = k ? d[k] : 0; return +(v && typeof v === 'object' ? v.mastery : v) || 0; });
  }
  function livingMark(ms, plain) {
    const s = sv('svg', { viewBox: '0 0 100 100', 'aria-hidden': 'true', class: 'mark-live' });
    [0, 90, 180, 270].forEach((a, i) => {
      // quadrant order: Algebra top-left, Advanced Math top-right, Geometry bottom-right, PSDA bottom-left
      const m = plain ? 1 : [ms[0], ms[1], ms[3], ms[2]][i];
      const rot = a ? `rotate(${a} 50 50)` : null;
      const cid = uid('clip');
      const clip = sv('clipPath', { id: cid }, s);
      sv('circle', { cx: 50, cy: 50, r: (7 + Math.min(1, Math.max(0, m / STRONG)) * 53).toFixed(1) }, clip);
      sv('path', { d: CORNER, transform: rot, fill: 'none', stroke: 'var(--mat)', 'stroke-width': 3 }, s);
      if (m > 0) sv('path', { d: CORNER, transform: rot, fill: 'var(--amber)', 'clip-path': `url(#${cid})` }, s);
    });
    return s;
  }
  function avatar(p = {}, size) {
    const cls = typeof size === 'string' ? size : size >= 72 ? 'xl' : size >= 40 ? 'lg' : '';
    const el = h('span', { class: 'avatar' + (cls ? ' ' + cls : ''), role: 'img', 'data-self': p.self ? '' : null,
      style: typeof size === 'number' && ![34, 40, 72].includes(size) ? `width: ${size}px; height: ${size}px; font-size: ${Math.round(size * .38)}px` : null });
    const initial = ((p.name || '').trim()[0] || '?').toUpperCase();
    const ms = domainMastery(p);
    const plainMark = p.board === 'anon' || p.board === 'hidden';
    const choice = plainMark ? 'plain' : p.public && (p.avatar === 'mark' || !p.avatar) ? 'initial' : (p.avatar || 'mark');
    function draw(photo) {
      el.removeAttribute('data-ring');
      el.classList.remove('mark');
      if (photo && p.self && !p.public) {
        el.replaceChildren(h('img', { src: photo, alt: '' }));
        el.setAttribute('aria-label', p.name ? `${p.name}, your photo` : 'Your photo');
        return;
      }
      if (choice === 'plain') { el.replaceChildren(livingMark(ms, true)); el.classList.add('mark'); el.setAttribute('aria-label', p.board === 'hidden' ? 'Anonymous' : (p.name || 'Student')); return; }
      if (choice === 'mark') {
        el.replaceChildren(livingMark(ms, false));
        el.classList.add('mark');
        const say = DOMAIN_KEYS.map((k, i) => `${k[0]} ${masteryWord(ms[i], ms[i] > 0 ? 1 : 0)}`).join(' · ');
        el.setAttribute('aria-label', say);
        el.title = say;
        return;
      }
      if (choice !== 'initial' && UI.glyph && (!UI.TOPIC || UI.TOPIC[choice])) {
        el.replaceChildren(UI.glyph(choice));
        if (p.ring === true || (Array.isArray(p.ring) && p.ring.includes(choice))) el.setAttribute('data-ring', '');
        el.setAttribute('aria-label', p.name ? `${p.name}, ${(UI.TOPIC && UI.TOPIC[choice] && UI.TOPIC[choice].short) || choice}` : choice);
        return;
      }
      el.replaceChildren(initial);
      el.setAttribute('aria-label', p.name || 'Student');
    }
    draw(null);
    if (p.self && !p.public) {
      const load = () => localPhoto.url(p.learner).then(u => draw(u)).catch(() => {});
      el.addEventListener('satf:photo', load);
      load();
    }
    return el;
  }

  /* ------------------------------------------------------------ countdown */
  const ticking = new Set();
  let tickTimer = 0;
  function tickAll() {
    for (const t of [...ticking]) { if (!t.el.isConnected) ticking.delete(t); else t.draw(); }
    if (!ticking.size) { clearInterval(tickTimer); tickTimer = 0; }
  }
  function countdown(el, iso, o = {}) {
    const end = toDate(iso).getTime();
    const parts = s => [Math.floor(s / 86400), Math.floor(s / 3600) % 24, Math.floor(s / 60) % 60, s % 60];
    const two = n => String(n).padStart(2, '0');
    let boxes = null;
    if (o.boxes) {
      boxes = ['Days', 'Hours', 'Min', 'Sec'].map(k => h('span', {}, h('b', { class: 'num' }), h('span', { class: 'k', text: k })));
      el.classList.add('countdown');
      el.replaceChildren(...boxes);
    }
    el.setAttribute('role', 'timer');
    let ended = false, lastMin = -1;
    const t = {
      el,
      draw() {
        const s = Math.max(0, Math.round((end - Date.now()) / 1000));
        const [d, hh, mm, ss] = parts(s);
        if (boxes) [d, hh, mm, ss].forEach((v, i) => { boxes[i].firstChild.textContent = i === 0 ? String(v).padStart(v >= 100 ? 3 : 2, '0') : two(v); });
        else el.textContent = d ? `${d}d ${two(hh)}:${two(mm)}:${two(ss)}` : hh ? `${hh}:${two(mm)}:${two(ss)}` : `${mm}:${two(ss)}`;
        const min = Math.floor(s / 60);
        if (min !== lastMin) { lastMin = min; el.setAttribute('aria-label', `${o.label ? o.label + ': ' : ''}${d ? `${d} days, ` : ''}${hh} hours, ${mm} minutes left`); }
        if (s === 0 && !ended) { ended = true; ticking.delete(t); if (o.onEnd) o.onEnd(); }
      },
    };
    t.draw();
    if (!ended) { ticking.add(t); if (!tickTimer) tickTimer = setInterval(tickAll, 1000); }
    return () => ticking.delete(t);
  }

  /* ------------------------------------------------------------ product vocabulary (G2, R42, R43) */
  const VERBS = {
    twin:      { label: 'Twin', sub: 'same kind, new numbers', sub_rw: 'same kind, new text', helper: 'Same kind of question, new numbers. Counts toward mastery.', key: 'T', icon: svgHTML(ICON.twin) },
    twin_set:  { label: 'Twin this set', sub: 'same types, new numbers', helper: 'The same question types, new numbers.', key: null, icon: svgHTML(ICON.twin) },
    twin_test: { label: 'Twin test', sub: 'same slots, new numbers', helper: 'Same question types in the same places, new numbers, scored like any test.', key: null, icon: svgHTML(ICON.twin_test) },
    again:     { label: 'Again, exactly', sub: 'the very same question', helper: 'The same question again. Doesn’t move mastery.', key: 'E', icon: svgHTML(ICON.again) },
    fix:       { label: 'Fix', sub: 'your open mistakes', helper: 'Two clean answers on questions with that trap close each mistake.', key: 'F', icon: svgHTML(ICON.fix) },
    learn:     { label: 'Learn this type', sub: 'one solved, then three', helper: 'A worked example on new numbers, then three of your own. Counts toward mastery.', key: null, icon: svgHTML(ICON.learn) },
  };
  const KEYS = { twin: 'T', twin_menu: 'Shift+T', details: 'V', guess: 'I', report: 'R', save: 'B', mark: 'M', note: 'O', history: 'Y', desmos: 'Shift+G', again: 'E', fix: 'F' };
  Object.defineProperty(KEYS, 'except', { enumerable: false, value: { E: 'eliminate in a running set', O: 'Open word in words, which has no note' } });
  const SEEN = 'satf.verbs.seen';
  function verbLabel(id, o) {
    const V = VERBS[id];
    if (o.label) return o.label;
    if (id === 'twin' && o.count > 1) return `Twin ×${fmtN(o.count)}`;
    if (id === 'fix' && o.count !== undefined && o.count !== null) return `Fix ${fmtN(o.count)}`;
    return V.label;
  }
  function verb(id, o = {}) {
    const V = VERBS[id];
    if (!V) throw new Error(`unknown verb ${id}`);
    const tag = o.href ? 'a' : 'button';
    const el = h(tag, { class: (o.primary ? 'pill sm' : `btn${o.sm ? ' sm' : ''}`) + ' verb', type: tag === 'button' ? 'button' : null, href: o.href || null,
      'data-verb': id, title: V.key ? `${V.helper} Key: ${V.key}` : V.helper, 'aria-keyshortcuts': V.key || null },
      icon(V.icon), h('span', { class: 'verb-l', text: verbLabel(id, o) }));
    let seen;
    try { seen = (JSON.parse(localStorage.getItem(SEEN) || '{}') || {})[id] || 0; } catch (_) { seen = 0; }   // blocked storage keeps the sublabel
    if (coarse() || seen < 3) el.append(h('span', { class: 'verb-sub', text: (o.subject === 'rw' && V.sub_rw) || V.sub }));
    el.addEventListener('click', e => {
      try { const m = JSON.parse(localStorage.getItem(SEEN) || '{}') || {}; m[id] = (m[id] || 0) + 1; localStorage.setItem(SEEN, JSON.stringify(m)); } catch (_) {}
      if (o.onClick) o.onClick(e);
    });
    return el;
  }

  /* ------------------------------------------------------------ points (G5) and facts (G6) */
  function pts(el, value, key) {
    if (value === null || value === undefined || isNaN(value)) { if (el) { el.replaceChildren(); el.hidden = true; } return null; }
    const v = Math.round(value);
    const b = h('button', { type: 'button', class: 'pts', text: `≈ ${v < 0 ? '−' : '+'}${fmtN(Math.abs(v))} pts` });
    if (key) fact(b, key, { label: 'Points on the table' });
    if (el) { el.hidden = false; el.replaceChildren(b); }
    return b;
  }
  const PAGES = { today: ['Today', '/'], me: ['Me', '/me/'], results: ['Results', '/results/'], plan: ['Plan', '/plan/'], review: ['Review', '/review/'],
    practice: ['Practice', '/practice/'], tests: ['Tests', '/tests/'], compete: ['Compete', '/compete/'], words: ['Words', '/words/'] };
  const factLabel = el => el.dataset.factLabel || (el.closest('.stat') && (el.closest('.stat').querySelector('.stat-k') || {}).textContent) || el.getAttribute('title') || '';
  const factValue = el => (el.dataset.factValue || el.textContent || '').replace('ⓘ', '').trim();
  function decorate(el) {
    if (el.dataset.factReady) return;
    el.dataset.factReady = '1';
    if (!el.matches('button, a[href]')) { el.setAttribute('role', 'button'); if (!el.hasAttribute('tabindex')) el.tabIndex = 0; }
    el.setAttribute('aria-haspopup', 'dialog');
    const label = factLabel(el), value = factValue(el);
    el.setAttribute('aria-label', `${label ? label + ': ' : ''}${value}, show how it’s worked out`);
  }
  function fact(el, key, o = {}) {
    el.dataset.fact = key;
    if (o.label) el.dataset.factLabel = o.label;
    if (o.value !== undefined) el.dataset.factValue = o.value;
    delete el.dataset.factReady;
    decorate(el);
    return el;
  }
  const leverCache = new Map();
  function openFact(el, key) {
    key = key || el.dataset.fact;
    const label = factLabel(el), value = factValue(el);
    return pop(el, (p, res) => {
      const head = h('div', { class: 'popover-head' }, h('span', { text: label || 'How it’s worked out' }), xBtn('Close', () => res.close()));
      const body = h('div', { class: 'fact-body' }, h('p', { class: 'fact-v', text: value }), skel(null, 'lines:3'));
      const load = async () => {
        body.replaceChildren(h('p', { class: 'fact-v', text: value }), skel(null, 'lines:3'));
        try {
          let lever = leverCache.get(key);
          if (!lever || Date.now() - lever.at > 60000) {
            const r = await api(`/levers?keys=${encodeURIComponent(key)}`);
            lever = { at: Date.now(), v: (r && r.levers && r.levers[key]) || (r && r[key]) || null };
            leverCache.set(key, lever);
          }
          body.replaceChildren(...leverParts(lever.v, value));
          res.reposition();
        } catch (_) { body.replaceChildren(h('p', { class: 'fact-v', text: value }), cardError(null, load, 'Couldn’t load how this is worked out.')); }
      };
      load();
      return [head, body];
    }, { role: 'dialog', label: `${label || value}: how it’s worked out`, className: 'fact-pop' });
  }
  fact.open = openFact;
  function leverParts(lv, value) {
    const out = [h('p', { class: 'fact-v', text: lv && lv.value !== undefined ? String(lv.value) : value })];
    if (!lv) { out.push(h('p', { class: 'help', text: 'How this is worked out isn’t available yet.' })); return out; }
    const sec = (k, ...kids) => h('section', { class: 'fact-sec' }, h('h3', { class: 'k', text: k }), ...kids);
    const helpHref = lv.help ? (String(lv.help).startsWith('/') ? lv.help : `/help/#${lv.help}`) : null;
    if (lv.how) out.push(sec('How it’s worked out', h('p', { text: lv.how }), helpHref && h('a', { href: helpHref, class: 'link', text: 'More in Help' })));
    if (lv.inputs && lv.inputs.length) out.push(sec('Your numbers', h('ul', {}, lv.inputs.map(x => h('li', { text: typeof x === 'object' ? [x.label, x.value].filter(v => v !== undefined).join(' · ') : String(x) })))));
    if (lv.excluded && lv.excluded.length) out.push(sec('Left out', h('ul', {}, lv.excluded.map(x => h('li', { text: typeof x === 'object' ? `${fmtN(x.n)} ${x.label}` : String(x) })))));
    if (lv.next || lv.start) {
      const st = lv.start;
      let b = null;
      if (st) {
        b = button({ label: st.label || 'Start', href: st.href || st.path || null, primary: true }, true);
        if (!st.href && !st.path && st.body) b.addEventListener('click', () => startDrill(st.body).catch(() => toast('Couldn’t start that set. Try again.')));
      }
      out.push(sec('What moves it', lv.next && h('p', { text: lv.next }), b));
    }
    if (lv.same_on && lv.same_on.length) {
      const links = lv.same_on.map(pg => { const [t, href] = typeof pg === 'object' ? [pg.label, pg.href] : (PAGES[pg] || [cap(pg), `/${pg}/`]); return h('a', { href, class: 'link', text: t }); });
      out.push(h('p', { class: 'help fact-same' }, 'Same number on: ', links.flatMap((a, i) => i ? [' · ', a] : [a])));
    }
    return out;
  }
  // any [data-fact] opens its working on click or Enter; pages only add the attribute (G6)
  doc.addEventListener('click', e => {
    const el = e.target.closest && e.target.closest('[data-fact]');
    if (!el || el.closest('[aria-disabled="true"]')) return;
    e.preventDefault();
    decorate(el);
    openFact(el);
  });
  doc.addEventListener('keydown', e => {
    if ((e.key !== 'Enter' && e.key !== ' ') || !e.target.closest) return;
    const el = e.target.closest('[data-fact]');
    if (!el || el !== e.target || el.matches('button, a[href]')) return;
    e.preventDefault();
    openFact(el);
  });
  const decorateAll = root => { if (root.querySelectorAll) root.querySelectorAll('[data-fact]:not([data-fact-ready])').forEach(decorate); };
  if (typeof MutationObserver === 'function') {
    const mo = new MutationObserver(ms => ms.forEach(m => {
      if (m.type === 'attributes') { if (m.target.dataset.fact !== undefined) decorate(m.target); }
      else m.addedNodes.forEach(n => { if (n.nodeType === 1) { if (n.dataset && n.dataset.fact !== undefined) decorate(n); decorateAll(n); } });
    }));
    const start = () => { decorateAll(doc); mo.observe(doc.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-fact'] }); };
    if (doc.body) start(); else doc.addEventListener('DOMContentLoaded', start);
  }

  /* ------------------------------------------------------------ empty states (G12, R55) */
  function empty(host, o = {}) {
    const el = h('div', { class: 'empty' });
    if (o.sample) {
      const s = typeof o.sample === 'function' ? o.sample() : o.sample;
      el.append(h('div', { class: 'empty-sample', 'aria-hidden': 'true', inert: '' }, s, o.tag === false ? null : h('span', { class: 'badge soft', text: o.tag || 'Example' })));
    }
    if (o.text) el.append(h('p', { class: 'empty-text', text: o.text }));
    const a = o.action && (o.answered ?? UI.answered) === 0 ? empty.START : o.action;   // the action follows the learner (R55)
    if (a) {
      const label = `${a.label}${a.cost ? ` · ${a.cost}` : ''}`;
      let b;
      if (a.verb) b = verb(a.verb, { count: a.count, label: a.label === undefined ? undefined : label, primary: a.primary !== false, href: a.href });
      else b = button({ label, href: a.href, primary: a.primary !== false }, true);
      if (!a.href) b.addEventListener('click', async () => {
        b.setAttribute('aria-busy', 'true');
        try {
          if (a.onClick) await a.onClick(host, b);
          else if (a.inline && a.body && UI.twinSheet) UI.twinSheet({ body: a.body, onDone: a.onDone });
          else if (a.body) await startDrill(a.body);
        } catch (_) { toast('Couldn’t start that. Try again.'); }
        finally { b.removeAttribute('aria-busy'); }
      });
      el.append(b);
    }
    return put(host, el);
  }
  empty.START = { label: 'Start with 8', cost: 'about 10 min', body: { source: 'start' } };

  /* ------------------------------------------------------------ subject (G11) and question labels (SR16) */
  const SUBJECT = {
    math: { id: 'math', label: 'Math', short: 'Math', min: 200, max: 800 },
    rw:   { id: 'rw', label: 'Reading and Writing', short: 'R&W', min: 200, max: 800 },
  };
  function qlabel(item, sitting) {
    let subject = 'math', module = null, n;
    if (typeof item === 'string' || typeof item === 'number') {
      const m = String(item).match(/^(?:(math|rw)-)?(?:m(\d+)-)?(\d+)$/);
      if (!m) return String(item);
      subject = m[1] || 'math'; module = m[2] ? +m[2] : null; n = +m[3];
    } else {
      subject = item.subject || 'math'; module = item.module ?? null; n = item.n ?? item.number ?? item.q;
    }
    const two = sitting === true || (sitting && (Array.isArray(sitting.subjects) ? new Set(sitting.subjects).size > 1 : sitting.subjects > 1));
    return [two && ((SUBJECT[subject] || {}).short || subject), module && `M${module}`, `Q${n}`].filter(Boolean).join(' ');
  }
  qlabel.addr = item => `${item.subject || 'math'}-${item.module ? `m${item.module}-` : ''}${item.n ?? item.number}`;

  /* ------------------------------------------------------------ export */
  Object.assign(UI, {
    sheet, confirm, pop, menu, tooltip, toast, banner,
    seg, chips, tabs, switch: switchCtl, triCheck, dropdown, filterBar, otp, counter, scoreSlider, images, examDate, actionBar, selbar,
    tile, meter, skel, cardError, table, pips, dbars, cell, legend, strip, nearTap, atlas, masteryWord, STRONG, skillRow, avatar, localPhoto, countdown, STATES,
    VERBS, verb, KEYS, pts, fact, empty, SUBJECT, qlabel,
    dur, mmss, num, date, relTime, KIND, copyText, ics,
  });
})();
