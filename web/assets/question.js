/* ============================================================================
   SAT Freshman -- one question, everywhere (spec/rebuild-v2.md R21, the question.js
   row of 2.4; QBank 2.5-2.6 and 2.9 Calculator, Tests 4.3 and 4.8, Report 1.13 body;
   v2-upgrades P1 P2 P3 P5 P6 P7 P8 P9 P16 P21 P23 P24, G3 G4 G8, R44 R49 R50 R54,
   X4 X6 X7, T4 T5, W1 W2 W6; tests.md item 74)

   Loaded after ui.js and kit.js wherever a question shows. Adds to window.UI. Its
   styles are in runner.css, which it links itself when the page did not.

   UI.workspace(host, q, opts) -> ws                  (UI.question is the old one-tap alias)
     q     the public question: {id, type 'mcq'|'spr', stem, choices, latex, figure, figure_alt,
           table, topic, topic_name, skill, difficulty, level, name, about, template, seed,
           repair, number, type_note, ask_span, watch_for, slip_line, check_anyway, rungs, cover}
     opts  mode      practice | exam | review | quiz | inline | example
           feedback  instant | retry | end (practice, inline); quiz is instant
           tries     3 (retry)        prefs {first_tap, option_reasons, open_explanations,
           rationale, confidence}     confActive
           state     restore {selected, value, struck, tries, hints, covered, own, eliminate, saved}
           fb        review / example: the feedback shown at once   hidden (review: Hide answers)
           bar       its own Check bar (default in practice, inline, quiz, example; the runner
                     passes false and puts UI.splitCheck in its footer)
           toolbar   its own tools row (R50; inline pages)          head  false | {label, glyph}
           hideSkill the skill line's text until the verdict (warm-up, mix-up)
           pad       the answer pad on grid-ins (default: a coarse pointer, satf.pad)
           formNudge X4's repeating-decimal warning   coverTool  offer Cover choices (P5, X7)
           stage     {prompt, options, skip} a staged item: options hidden until step 1 (W2, W6)
           actions   ctx for UI.questionActions under the verdict, or fn(host, fb)
           stemEl    an existing .q-stem node to reuse (V14)     spans  initial stem spans (kind 'chg' draws <mark class=chg>)
           callbacks onCheck(answer, meta) -> fb | Promise | undefined (the page calls reveal)
                     onSelect(answer | null) (exam, end), onEnter (exam grid-in), onStrike(i, on, by),
                     onSkip, onHint -> {kind, choice, reason, step, example}, onShowAnswer -> fb,
                     onOwn(own) -> fb (cover), onCover({covered, own, reveal_ms}), onCause(kind),
                     onTrap(i), onLadder, onKeepMarked(on), onRule(action, text), onExample(ex),
                     onReanswer(answer, correct), onNext, onDone, onReveal(fb), onChange(state),
                     onNotMine(anchor, i) (review: V6's link on your pick), onSpot(i) (SR11)
     ws    {el, q, key(e), check(conf), select(i), choose(i), strike(i, on, by), eliminate(on),
            cover(on), hint(), skip(), reveal(fb), unlock(), answered(), canCheck(), value(),
            state(), setHidden(on), tools(), renderTools(host), focus(), restart(), destroy()}
   UI.splitCheck(host, {confidence, save, onSubmit(conf)}) -> {el, set({enabled, save, firstTry})}
   UI.questionActions(host, q, ctx) -> {el, run(id), has(id)}        G4, R49
   UI.twin(host, ctx) -> {el, run(axis, n), menu()}                   R44, P18
   UI.twinSheet({body, recall, title, onDone}) -> sheet api           T5 (callers go through UI.twin)
   UI.twinInline(host, {body, caption, onBack, backLabel, againLabel, wsOpts(q, n), onAnswer(fb, q, n), session})
       -> {el, sid, answered, ws, finish(), destroy()}                R23, R24: the players' tile, the pane's mini-session
       (UI.twin's ctx.inline(o) hands a player the run instead of opening the sheet)
   UI.stemDiff(old, new) -> [{start, end, kind: 'chg'}]               V14: the numbers that changed, for opts.spans
   UI.pad(field, {onKey}) -> el                                       X6
   UI.calc  {open(o), close, toggle, isOpen, mode, engine, dock(host), sitting(id), onChange(fn),
             onOpen(fn), walkthrough(desmos), setMode(m)}             Desmos, else scientific (item 74)
   UI.tex(el, plain, latex)   UI.katex()   UI.spr {parse, preview, clean, cap, RULE, repeatingCut, directions()}
   UI.qicon(name, size) -> svg                                        this file's icons, for runner.js
   UI.readAloud(q, onEnd)     UI.sciEval(src, deg, ans)
   ========================================================================== */

(() => {
  'use strict';
  const UI = window.UI = window.UI || {};
  const doc = document;

  /* ------------------------------------------------------------ helpers */
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
  const media = q => { try { return matchMedia(q).matches; } catch (_) { return false; } };
  const phone = () => media('(max-width: 759px)');
  const coarse = () => media('(pointer: coarse)');
  const still = () => media('(prefers-reduced-motion: reduce)') || doc.documentElement.dataset.motion === 'reduce';
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (_) { return false; } },
  };
  const bump = (k, max) => { const n = ls.get(k, 0) || 0; if (n < max) ls.set(k, n + 1); return n; };
  let seq = 0;
  const uid = p => `w${p}${++seq}`;
  const LETTERS = 'ABCDE';
  const minus = s => String(s ?? '').replace(/-/g, '−');
  const mmss = ms => { const s = Math.max(0, Math.round((ms || 0) / 1000)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; };
  const cap1 = t => t ? t[0].toUpperCase() + t.slice(1) : '';
  const low1 = t => t ? t[0].toLowerCase() + t.slice(1) : '';
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const toast = (t, o) => (UI.toast ? UI.toast(t, o) : null);
  const api = (path, o) => UI.api(path, o);
  const pct = x => Math.round(x <= 1 ? x * 100 : x);

  // the styles live in runner.css; a page that shows a question without the runner still gets them
  if (!doc.querySelector('link[href*="runner.css"]')) {
    const me = doc.currentScript && doc.currentScript.src;
    doc.head.append(h('link', { rel: 'stylesheet', href: me ? new URL('runner.css', me).href : '/assets/runner.css' }));
  }

  /* icons: the shared set (UI.icon, ui.js; Phosphor at one stroke weight, filled twins for "on" toggles).
     UI.qicon stays as its alias for older callers. A name the set lacks draws nothing (and warns on localhost). */
  const icon = (name, size = 18) => (UI.icon ? UI.icon(name, size) : '');
  const markIcon = (name, size = 18) => { const s = icon(name, size); return s || h('span', { text: name === 'check' ? '✓' : '✕' }); };
  const kbd = k => h('kbd', { class: 'kbd', text: k });
  const quiet = (text, onClick, o = {}) => h('button', { type: 'button', class: 'quiet' + (o.cls ? ' ' + o.cls : ''), 'aria-label': o.label, title: o.title, onclick: onClick }, o.icon && icon(o.icon, 16), text);

  /* ------------------------------------------------------------ math: one render helper (G8) */
  const KATEX = 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.11/';
  let katexP = null;
  function katex() {
    if (window.katex) return Promise.resolve(window.katex);
    if (!katexP) {
      katexP = new Promise((res, rej) => {
        if (!doc.querySelector('link[href*="katex"]')) doc.head.append(h('link', { rel: 'stylesheet', href: KATEX + 'katex.min.css', crossorigin: 'anonymous' }));
        const old = doc.querySelector('script[src*="katex"]');
        const s = old || h('script', { src: KATEX + 'katex.min.js', crossorigin: 'anonymous' });
        s.addEventListener('load', () => (window.katex ? res(window.katex) : rej(new Error('KaTeX did not load'))));
        s.addEventListener('error', () => rej(new Error('KaTeX did not load')));
        if (!old) doc.head.append(s);
      });
      katexP.catch(() => { katexP = null; });
    }
    return katexP;
  }
  // The bank gives a plain and a LaTeX form of every option. Where they differ it is a
  // fraction or a radical, and only then is it handed to KaTeX; the plain form shows first.
  function tex(el, plain, latex) {
    fracText(el, plain ?? '');
    if (!latex || latex === plain) return el;
    // a thousands comma is part of the number, not punctuation: 1{,}225, never "1, 225"
    latex = String(latex).replace(/(\d),(?=\d{3}(?!\d))/g, '$1{,}');
    const go = k => { try { el.innerHTML = k.renderToString(latex, { throwOnError: false, output: 'htmlAndMathml' }); el.classList.add('tex'); } catch (_) {} };
    if (window.katex) go(window.katex); else katex().then(go, () => {});
    return el;
  }
  // text with $...$ math inside (steps, Desmos expressions)
  function texText(el, str) {
    el.replaceChildren();
    const parts = String(str ?? '').split(/(\$[^$]+\$)/);
    parts.forEach((part, i) => {
      if (/^\$[^$]+\$$/.test(part)) {
        const m = tex(h('span'), part.slice(1, -1), part.slice(1, -1) + ' ');
        // the punctuation after the math stays on its line
        const p = (parts[i + 1] || '').match(/^[.,;:!?)]+/);
        if (p) { parts[i + 1] = parts[i + 1].slice(p[0].length); el.append(h('span', { style: 'white-space: nowrap' }, m, p[0])); } else el.append(m);
      } else if (part) el.append(...fracNodes(part));
    });
    return el;
  }

  /* ------------------------------------------------------------ fractions: stacked, in the line */
  // The user's rule: "8/(x − 14)", "34π/5" and "(2/19)s" draw as a numerator over a bar over a denominator, in the line.
  // Every character stays in the DOM (the slash and a group's outer brackets are only visually hidden), so textContent
  // offsets for highlights and notes stay valid and a screen reader still reads the slash. Units and words (km/h, and/or,
  // 5 m/s, 4.50/hour) are not fractions; neither is a/b/c.
  const SUP = '⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ';
  const INT = '(?:\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.\\d+)?';
  const NUM_END = new RegExp(`(?:(?:${INT})?√(?:${INT}|[A-Za-zπ])|√?${INT}[A-Za-zπθ]*|√?[A-Za-zπθ]+)[${SUP}]*$`);
  const DEN_START = new RegExp(`^(?:√?${INT}[${SUP}]*|[A-Z]{2,3}(?![A-Za-z])|[A-Za-zπθ][${SUP}]*(?![A-Za-z]))`);
  // Radicals and powers in the line: √(…), ³√(…), √2, x^(a/b), 5^x. Every character stays in the DOM (the √, ^ and
  // brackets are visually hidden), so offsets are unchanged; a radical is drawn as a stretchy sign with a bar over its
  // radicand, an exponent as a raised, smaller run.
  const SUPD = '²³⁴⁵⁶⁷⁸⁹';
  const hid = t => h('span', { class: 'fh', text: t });
  const group = (s, i) => { let d = 0; for (let j = i; j < s.length; j++) { if (s[j] === '(') d++; else if (s[j] === ')' && !--d) return j; } return -1; };
  // the ranges inside √( ) and ^( ): a slash there belongs to that group, not to a fraction around it
  const holes = s => { const r = []; for (let i = 0; i < s.length; i++) if ((s[i] === '√' || s[i] === '^') && s[i + 1] === '(') { const e = group(s, i + 1); if (e > 0) r.push([i + 2, e]); } return r; };
  function richNodes(str) {
    if (!/[√^]/.test(str)) return [doc.createTextNode(str)];
    const out = [];
    let at = 0;
    const text = (a, b) => { if (b > a) out.push(doc.createTextNode(str.slice(a, b))); };
    for (let p = 0; p < str.length; p++) {
      const c = str[p];
      if (c === '^') {
        let e, inner, tail = '';
        if (str[p + 1] === '(') { e = group(str, p + 1); if (e < 0) continue; inner = str.slice(p + 2, e); }
        else { const m = str.slice(p + 1).match(/^[−-]?(?:\d+(?:\.\d+)?|[A-Za-zπ])/); if (!m || p === 0 || /[\s(]/.test(str[p - 1])) continue; inner = m[0]; e = p + m[0].length; tail = 'x'; }
        text(at, p);
        out.push(hid('^'), ...(tail ? [] : [hid('(')]), h('span', { class: inner.includes('/') ? 'sp spf' : 'sp' }, fracNodes(inner)), ...(tail ? [] : [hid(')')]));
        at = e + 1;
        p = at - 1;
      } else if (c === '√') {
        let e, inner;
        if (str[p + 1] === '(') { e = group(str, p + 1); if (e < 0) continue; inner = str.slice(p + 2, e); }
        else { const m = str.slice(p + 1).match(/^(?:\d+(?:\.\d+)?|[A-Za-zπ])/); if (!m) continue; inner = m[0]; e = p + m[0].length; }
        // an index, ³√ or ⁴√, is the raised digits right before the sign, unless they are a power of what comes before
        let a = p;
        while (a > at && SUPD.includes(str[a - 1])) a--;
        if (a < p && /[A-Za-z0-9)]/.test(str[a - 1] || '')) a = p;
        text(at, a);
        const open = str[p + 1] === '(';
        out.push(h('span', { class: 'rad' }, a < p ? h('span', { class: 'ri' }, str.slice(a, p)) : null, hid('√'), h('span', { class: 'rs', 'aria-hidden': 'true' }),
          h('span', { class: 'rr' }, open ? hid('(') : null, fracNodes(inner), open ? hid(')') : null)));
        at = e + 1;
        p = at - 1;
      }
    }
    text(at, str.length);
    return out;
  }
  function fracNodes(str) {
    str = String(str ?? '');
    if (!str.includes('/')) return richNodes(str);
    const out = [];
    let at = 0;
    const skip = holes(str);
    const back = i => { let d = 0; for (let j = i; j >= at; j--) { if (str[j] === ')') d++; else if (str[j] === '(' && !--d) return j; } return -1; };
    const fwd = i => { let d = 0; for (let j = i; j < str.length; j++) { if (str[j] === '(') d++; else if (str[j] === ')' && !--d) return j; } return -1; };
    const part = (t, group) => (group ? [hid('('), ...fracNodes(t.slice(1, -1)), hid(')')] : fracNodes(t));
    for (let k = str.indexOf('/'); k > 0; k = str.indexOf('/', k + 1)) {
      if (k < at || /[\s/]/.test(str[k - 1]) || /[\s/]/.test(str[k + 1] || ' ') || skip.some(([x, y]) => k >= x && k < y)) continue;
      let a, nGroup = false;
      if (str[k - 1] === ')') {
        a = back(k - 1);
        if (a < 0) continue;
        nGroup = true;
        // f(x)/2, 2(x + 1)/3, √(x)/2: the brackets belong to the numerator and stay
        const pre = str.slice(at, a).match(new RegExp(`(?:(?:${INT})?[${SUPD}]*√|${INT}|[A-Za-z]+)$`));
        if (pre) { a -= pre[0].length; nGroup = false; }
      } else if (str[k - 1] === '|') {
        a = str.lastIndexOf('|', k - 2);                                     // |x|/a
        if (a < at) continue;
      } else {
        const m = str.slice(at, k).match(NUM_END);
        if (!m) continue;
        a = k - m[0].length;
      }
      // x^2/3 and (1 + r)^2/4: a power is one thing, so its base belongs to the numerator
      while (a > at && str[a - 1] === '^') {
        const j = a - 1;
        if (str[j - 1] === ')') { const s0 = back(j - 1); if (s0 < at) break; a = s0; }
        else { const m = str.slice(at, j).match(/(?:\d+(?:\.\d+)?|[A-Za-z])$/); if (!m) break; a = j - m[0].length; }
        nGroup = false;
      }
      let b, dGroup = false;
      if (str[k + 1] === '(') { b = fwd(k + 1); if (b < 0) continue; b += 1; dGroup = true; }
      else {
        const rd = str.slice(k + 1).match(new RegExp(`^[${SUPD}]*√`));
        if (rd) {                                                            // ⁴√(z⁸), √2: a radical is a whole denominator
          const j = k + 1 + rd[0].length;
          if (str[j] === '(') { const e = group(str, j); if (e < 0) continue; b = e + 1; }
          else { const m = str.slice(j).match(new RegExp(`^(?:${INT}|[A-Za-zπ])`)); if (!m) continue; b = j + m[0].length; }
        } else {
          const m = str.slice(k + 1).match(DEN_START); if (!m) continue; b = k + 1 + m[0].length;
          // f(n)/g(n): a function over a function keeps the denominator's brackets
          if (nGroup === false && str[k - 1] === ')' && /^[A-Za-z]$/.test(m[0]) && str[b] === '(') { const e = group(str, b); if (e > 0) b = e + 1; }
        }
      }
      // 1/2^x, 5/(x + 1)^2: the denominator takes its power
      while (str[b] === '^') {
        if (str[b + 1] === '(') { const e = group(str, b + 1); if (e < 0) break; b = e + 1; }
        else { const m = str.slice(b + 1).match(/^[−-]?(?:\d+(?:\.\d+)?|[A-Za-z])/); if (!m) break; b += 1 + m[0].length; }
        dGroup = false;
      }
      if (str[b] === '/' || str[a - 1] === '/') continue;                    // a/b/c: leave the chain
      const num0 = str.slice(a, k), den0 = str.slice(k + 1, b);
      if (/^[A-Za-z]+$/.test(num0) && /\d\s$/.test(str.slice(0, a))) continue;   // 5 m/s
      // words and units with no number (km/h, lb/ft³, and/or) stay; segment ratios (BC/AB) and cd/3 are fractions
      const word = t => /^[A-Za-z]{2,}[${SUP}]*$/.test(t), seg = t => /^[A-Z]{2,3}$/.test(t);
      if ((word(num0) || word(den0)) && !(seg(num0) && seg(den0)) && !/\d/.test(num0 + den0)) continue;
      if (str[a - 1] === '$') continue;                                        // $4.50/h
      // a lone fraction in brackets, (2/19)s: the brackets go with the bar
      let wl = '', wr = '';
      if (!nGroup && !dGroup && str[a - 1] === '(' && str[b] === ')' && a - 1 >= at && !/[A-Za-z√\d]/.test(str[a - 2] || '')) { a -= 1; b += 1; wl = '('; wr = ')'; }
      if (a > at) out.push(...richNodes(str.slice(at, a)));
      out.push(h('span', { class: 'frac' }, wl ? hid(wl) : null, h('span', { class: 'fn' }, part(num0, nGroup)), hid('/'),
        h('span', { class: 'fd' }, part(den0, dGroup)), wr ? hid(wr) : null));
      at = b;
      k = b - 1;
    }
    if (at < str.length) out.push(...richNodes(str.slice(at)));
    return out;
  }
  // UI.fracText(el, text) fills el; UI.fracText(text) returns a span to insert (the Review and Results pages call it so)
  const fracText = (el, str) => {
    if (!(el instanceof Element)) { const s = h('span'); s.append(...fracNodes(el)); return s; }
    el.replaceChildren(...fracNodes(str)); return el;
  };

  /* ------------------------------------------------------------ the grid-in rules */
  const num = x => /^(\d+\.?\d*|\.\d+)$/.test(x);
  const DIGIT_ZEROS = [0x660, 0x6f0, 0x966, 0x9e6, 0xa66, 0xae6, 0xb66, 0xbe6, 0xc66, 0xce6, 0xd66, 0xe50, 0xed0, 0xf20, 0x1040];
  const spr = {
    RULE: 'Up to 5 characters, 6 with a minus. Fractions with /, no mixed numbers. Long decimals may be cut or rounded.',
    PLACEHOLDER: 'e.g. 2/3, −1.5, 12',
    EXAM_PLACEHOLDER: 'Enter your answer (e.g., 5.566, −5.566, 2/3, −2/3)',
    BAD: 'Use digits, one ".", one "/", and a leading "−"',
    LONG: 'Too long: 5 characters at most, 6 with a minus',
    ZERO: 'A fraction can’t have 0 below the bar',
    HINT_BAD: 'Only digits, one decimal point or fraction bar, and a leading minus',
    HINT_LONG: '5 characters at most, 6 with a minus sign',
    clean: s => String(s ?? '').normalize('NFKC').replace(/[\u00ad\u200b-\u200f\u202a-\u202e\u2060\u2066-\u2069\ufeff]/g, '')
      .replace(/[\u2044\u2215\u29f8\u00f7]/g, '/').replace(/\u066b/g, '.').replace(/\p{Nd}/gu, d => { const c = d.codePointAt(0), z = DIGIT_ZEROS.find(z => c >= z && c < z + 10); return z === undefined ? d : c - z; }).replace(/[\u2212\u2010-\u2015\u207b\u208b\u02d7\ufe58\ufe63\uff0d\u2796]/g, '-').replace(/\s+/g, ''),
    cap: s => (spr.clean(s).startsWith('-') ? 6 : 5),
    charsOk: s => /^-?[0-9./]*$/.test(s) && (s.match(/\./g) || []).length <= 1 && (s.match(/\//g) || []).length <= 1,
    parse(raw) {
      const s = spr.clean(raw);
      if (!s) return { empty: true, s };
      if (!spr.charsOk(s)) return { error: spr.BAD, s };
      if (s.length > spr.cap(s)) return { error: spr.LONG, s };
      const neg = s.startsWith('-');
      const body = neg ? s.slice(1) : s;
      if (body.includes('/')) {
        const [a, b] = body.split('/');
        if (!num(a) || !num(b)) return { partial: true, s };
        if (+b === 0) return { error: spr.ZERO, s };
        return { ok: true, s, neg, frac: { n: a, d: b }, value: (neg ? -1 : 1) * (+a) / (+b) };
      }
      if (!num(body)) return { partial: true, s };
      return { ok: true, s, neg, value: (neg ? -1 : 1) * +body };
    },
    // "Answer preview:" and the value typeset: a fraction stacked with a real minus, then its decimal
    preview(el, raw) {
      el.replaceChildren();
      const p = spr.parse(raw);
      if (p.empty || p.error) return p;
      const v = h('span', { class: 'pv' });
      if (p.frac) {
        v.append(p.neg ? '−' : '', h('span', { class: 'frac', role: 'img', 'aria-label': `${p.neg ? 'minus ' : ''}${p.frac.n} over ${p.frac.d}` },
          h('span', { class: 'fn', text: p.frac.n, 'aria-hidden': 'true' }), h('span', { class: 'fd', text: p.frac.d, 'aria-hidden': 'true' })));
        const r = Math.round(p.value * 1e4) / 1e4;
        const shown = r.toFixed(4).replace(/0+$/, '').replace(/\.$/, '');
        v.append(h('span', { class: 'approx', text: `${Math.abs(p.value - r) < 1e-12 ? '=' : '≈'} ${minus(shown)}` }));
      } else v.append(minus(p.s));
      el.append(h('span', { class: 'k-pre', text: 'Answer preview:' }), ' ', v);
      return p;
    },
    // X4: a short cut of a repeating decimal (thirds, sixths, ninths) that does not fill the grid
    repeatingCut(str) {
      const s = spr.clean(str);
      const m = s.match(/^-?\d*\.(\d{2,})$/);
      if (!m || s.length >= spr.cap(s)) return false;
      const d = m[1].length, got = +m[1], scale = 10 ** d;
      for (const n of [3, 6, 9]) {
        for (let j = 1; j < n; j++) {
          if ((n / gcd(j, n)) % 3) continue;               // terminates: 3/6, 3/9 ...
          const x = j * scale / n;
          if (got === Math.floor(x) || got === Math.round(x)) return true;
        }
      }
      return false;
    },
  };
  function gcd(a, b) { return b ? gcd(b, a % b) : a; }
  spr.repeatingCut.__test = [['.66', true], ['.33', true], ['1.33', true], ['.667', true], ['.45', false], ['.64', false],
    ['.15', false], ['.85', false], ['.6666', false], ['.6667', false], ['0.5', false], ['.142', false]];
  function selfTest() {
    const bad = spr.repeatingCut.__test.filter(([s, want]) => spr.repeatingCut(s) !== want).map(([s]) => s);
    let n = 0;
    for (let i = 1; i < 100; i++) if (spr.repeatingCut('.' + String(i).padStart(2, '0'))) n++;
    if (n !== 15) bad.push(`${n} two-digit cuts, not 15`);
    const sci = sciEval.__test.filter(([src, want]) => { try { return Math.abs(sciEval(src, true, 0) - want) > 1e-9; } catch (_) { return true; } }).map(([s]) => s);
    const diff = stemDiff.__test.filter(([a, b, want]) => JSON.stringify(stemDiff(a, b).map(s => b.slice(s.start, s.end))) !== JSON.stringify(want)).map(([a]) => a);
    // fractions: [text, how many stack]; the text itself never changes (highlight offsets)
    const frac = [['10x²/(x² − 196) − 5x/(x + 14) = 8/(x − 14)', 3], ['P = (2/19)s − 1/9', 2], ['the ratio BC/AB', 1], ['|x|/a − 6', 1],
      ['√(z⁹)/⁴√(z⁸) = z^(a/b)', 1], ['f(w)/g(w), for w > 5', 1], ['5(1/2^x) and x²/3', 2], ['2√3/3', 1], ['12√65 and 5^x', 0], ['60 km/h and/or more', 0], ['at 5 m/s', 0], ['$4.50/hour', 0], ['a/b/c', 0], ['lb/ft³', 0]].filter(([t, want]) => {
      const box = h('span', {}, fracNodes(t));
      return box.textContent !== t || box.querySelectorAll(':scope > .frac').length !== want || fracText(t).textContent !== t;
    }).map(([t]) => t);
    return { ok: !bad.length && !sci.length && !diff.length && !frac.length, spr: bad, sci, diff, frac };
  }

  const DIRECTIONS = [
    'Enter one answer, even when more than one is right.',
    'Up to 5 characters for a positive answer, 6 with a minus sign.',
    'A fraction that doesn’t fit: enter its decimal.',
    'A decimal that doesn’t fit: cut it or round it so it fills the space.',
    'No mixed numbers: 3½ is 7/2 or 3.5.',
    'No %, commas or $ signs.',
  ];
  const EXAMPLES = [['3.5', '3.5, 3.50, 7/2', '31/2, 3 1/2'], ['2/3', '2/3, .6666, .6667, 0.666, 0.667', '0.66, .66, 0.67, .67'], ['−1/3', '−1/3, −.3333, −0.333', '−.33, −0.33']];
  function directions() {
    return h('div', { class: 'spr-dirs' },
      h('h3', { class: 'spr-dirs-h', text: 'Entering your answer' }),
      h('ul', {}, DIRECTIONS.map(t => h('li', { text: t }))),
      h('table', { class: 'table compact' },
        h('thead', {}, h('tr', {}, ['Answer', 'Accepted', 'Not accepted'].map(t => h('th', { scope: 'col', text: t })))),
        h('tbody', {}, EXAMPLES.map(r => h('tr', {}, r.map(c => h('td', { text: c })))))));
  }
  spr.directions = directions;

  /* ------------------------------------------------------------ read aloud (G8) */
  // ponytail: a 12-rule replacer, not MathSpeak; move to Speech Rule Engine if students report misreads
  const SAY = [
    [/(\d)\s*\/\s*(\d)/g, '$1 over $2'], [/π/g, ' pi '], [/²/g, ' squared '], [/³/g, ' cubed '],
    [/√/g, ' the square root of '], [/≤/g, ' is at most '], [/≥/g, ' is at least '], [/≠/g, ' is not equal to '],
    [/[−–]/g, ' minus '], [/×/g, ' times '], [/÷/g, ' divided by '], [/°/g, ' degrees '],
  ];
  const speakable = t => SAY.reduce((s, [re, to]) => s.replace(re, to), String(t || '')).replace(/_{3,}/g, ' blank ').replace(/\s+/g, ' ').trim();
  let speaking = null;
  const canSpeak = () => !!(window.speechSynthesis && window.SpeechSynthesisUtterance);
  function readAloud(q, onEnd) {
    const synth = window.speechSynthesis;
    if (!canSpeak()) return false;
    if (speaking) { const done = speaking.done; speaking = null; synth.cancel(); if (done) done(); return false; }
    // R&W reads its passage first, as prose: no maths words for dashes or symbols
    const say = q.text ? t => String(t || '').replace(/<\/?u>/g, '').replace(/_{3,}/g, ' blank ').replace(/\s+/g, ' ').trim() : speakable;
    const text = [q.text, q.stem, q.figure && (q.figure_alt || 'There is a figure.'), q.table && q.table.length && 'There is a table.',
      ...(q.choices || []).map((c, i) => `${LETTERS[i]}, ${c}.`)].filter(Boolean).map(say).join(' ');
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95;
    const me = { done: onEnd };
    u.onend = u.onerror = () => { if (speaking === me) { speaking = null; if (onEnd) onEnd(); } };
    speaking = me;
    synth.cancel();
    synth.speak(u);
    return true;
  }

  /* ------------------------------------------------------------ the question body */
  function figure(q) {
    const fig = h('figure', { class: 'q-figure q-fig', role: 'img', 'aria-label': q.figure_alt || 'Figure for this question' });
    fig.innerHTML = q.figure;
    const svg = fig.querySelector('svg');
    if (svg) {
      svg.setAttribute('aria-hidden', 'true');
      svg.removeAttribute('role');
      const vb = svg.viewBox && svg.viewBox.baseVal;
      const natural = (vb && vb.width) || parseFloat(svg.getAttribute('width')) || 360;
      svg.removeAttribute('width');
      svg.removeAttribute('height');
      svg.style.width = Math.round(Math.min(natural * 1.3, 620)) + 'px';
    }
    return fig;
  }
  // an R&W passage: paragraphs on blank lines, lines kept (poems, notes), <u> underlined, ______ a blank
  function passage(q) {
    // 'p': highlights and notes anchor here; never folded, read before answering
    const el = h('div', { class: 'q-passage', 'data-addr': 'p', 'data-nofold': '' });
    // the text is never changed, only wrapped: highlights and notes are offsets into textContent
    q.text.split(/\n{2,}/).forEach(par => {
      const p = h('p', { class: /^Text \d$/.test(par.trim()) ? 'q-tlabel' : null });
      par.split('\n').forEach((line, i) => {
        // a notes bullet is its own hanging line; any other line break stays a <br>
        const li = /^• /.test(line) ? h('span', { class: 'q-li' }) : null;
        if (i && !li && !(p.lastChild && p.lastChild.classList && p.lastChild.classList.contains('q-li'))) p.append(h('br', {}));
        const host = li || p;
        if (li) { li.append(h('span', { class: 'q-bul', 'aria-hidden': 'true' }, '• ')); line = line.slice(2); }
        line.split(/(<u>.*?<\/u>|_{3,})/).forEach(bit => {
          if (/^_{3,}$/.test(bit)) host.append(h('span', { class: 'blank', role: 'img', 'aria-label': 'blank' }, bit));
          else if (bit.startsWith('<u>')) host.append(h('u', { text: bit.slice(3, -4) }));
          else if (bit) host.append(bit);
        });
        if (li) p.append(li);
      });
      el.append(p);
    });
    return el;
  }
  function dataTable(q) {
    const [head, ...rows] = q.table;
    return h('div', { class: 'q-table' }, h('table', {},
      h('caption', { class: q.table_title ? 'q-table-title' : 'sr', text: q.table_title || `Table for question${q.number ? ' ' + q.number : ''}` }),
      h('thead', {}, h('tr', {}, head.map((c, j) => h('th', { scope: 'col', 'data-addr': `t:0:${j}`, text: c })))),
      h('tbody', {}, rows.map((r, i) => h('tr', {}, r.map((c, j) => h('td', { 'data-addr': `t:${i + 1}:${j}`, text: c })))))));
  }
  // the stem's text with ranges marked (Read the ask, a quiz's clue and idea spans) and blanks drawn;
  // the text itself is untouched, so offsets into textContent stay valid for UI.annotate
  function stemText(el, text, spans) {
    el.replaceChildren();
    const put = str => str.split(/(_{3,})/).forEach(p => {
      if (!p) return;
      el.append(...(/^_{3,}$/.test(p) ? [h('span', { class: 'blank', role: 'img', 'aria-label': 'blank' }, p)] : fracNodes(p)));
    });
    let at = 0;
    (spans || []).filter(s => s && s.end > s.start).sort((a, b) => a.start - b.start).forEach(s => {
      if (s.start < at) return;
      put(text.slice(at, s.start));
      el.append(s.kind === 'chg' ? h('mark', { class: 'chg' }, text.slice(s.start, s.end))
        : h('span', { class: `span-${s.kind || 'mark'}`, 'data-label': s.label || null, title: s.label || null }, text.slice(s.start, s.end)));
      at = s.end;
    });
    put(text.slice(at));
  }
  // V14: the tokens of b that are not in a (numbers and words, LCS over /(\d[\d.,/]*|\s+)/),
  // as spans of kind 'chg' in b's text; stems are ~400 characters, so the table stays small
  function stemDiff(a, b) {
    const split = s => String(s || '').split(/(\d[\d.,/]*|\s+)/).filter(x => x !== '');
    const A = split(a), B = split(b), n = A.length, m = B.length;
    if (!n || !m || n * m > 400000) return [];
    const L = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) L[i][j] = A[i] === B[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
    const out = [];
    let i = 0, j = 0, pos = 0;
    while (j < m) {
      if (i < n && A[i] === B[j]) { pos += B[j].length; i++; j++; continue; }
      if (i < n && L[i + 1][j] >= L[i][j + 1]) { i++; continue; }
      if (!/^\s+$/.test(B[j])) {
        const last = out[out.length - 1];
        if (last && last.end === pos) last.end = pos + B[j].length; else out.push({ start: pos, end: pos + B[j].length, kind: 'chg' });
      }
      pos += B[j].length; j++;
    }
    return out;
  }
  stemDiff.__test = [
    ['A circle has a diameter of 32 inches.', 'A circle has a diameter of 70 inches.', ['70']],
    ['x = 144 and 2π', 'x = 120 and 3π', ['120', '3']],
    ['same text', 'same text', []],
  ];
  const keyIndex = fb => {
    if (!fb) return null;
    if (Number.isInteger(fb.answer_index)) return fb.answer_index;
    return typeof fb.answer === 'string' && /^[A-E]$/.test(fb.answer) ? LETTERS.indexOf(fb.answer) : null;
  };
  const givenIndex = g => (Number.isInteger(g) ? g : typeof g === 'string' && /^[A-E]$/.test(g) ? LETTERS.indexOf(g) : null);

  /* ------------------------------------------------------------ the workspace */
  function workspace(host, q, opts = {}) {
    const o = opts;
    const mode = o.mode || 'practice';
    const live = mode === 'practice' || mode === 'inline' || mode === 'quiz';      // a Check that files
    const fbMode = mode === 'quiz' ? 'instant' : (o.feedback || 'instant');
    const endMode = live && fbMode === 'end';
    const prefs = Object.assign({ first_tap: false, option_reasons: true, open_explanations: false, rationale: 'miss', confidence: 'ask' }, o.prefs || {});
    const mc = q.type !== 'spr';
    const choices = q.choices || [];
    const n = choices.length;
    const maxTries = o.tries || 3;
    const st = o.state || {};
    const S = {
      selected: Number.isInteger(st.selected) ? st.selected : null,
      value: st.value || '',
      struck: new Set(st.struck || []),
      hintStruck: new Set(st.hint_struck || []),
      eliminate: !!(st.eliminate ?? o.eliminate),
      tries: (st.tries || []).slice(),
      hints: st.hints || 0,
      covered: !!(st.covered ?? (mc && o.cover)),
      own: st.own || '',
      saved: st.saved ?? null,
      stage: mc && o.stage && !st.stage_done ? 'on' : null,
      stagePick: null,
      answered: false, fb: null, busy: false, pending: false, hidden: !!o.hidden, fastOk: false,
      queued: 0, selAt: 0, shownAt: performance.now(), awayAt: null, awayMs: 0, coverAt: null, lastConf: 'auto',
    };
    const nudged = o.nudgeSeen || new Set();
    const cleanups = [];

    const el = h('div', { class: `ws ws-${mode}${live ? ' fb-' + fbMode : ''}`, 'data-qid': q.id || null, 'data-type': mc ? 'mcq' : 'spr' });
    const status = h('p', { class: 'sr', role: 'status' });
    const headEl = headLine();
    const ruleTip = typeRule();
    // V14: a twin can take over the stem node it replaces, so only its changed numbers move
    const stemEl = o.stemEl || h('div', { class: 'q-stem', 'data-addr': 's' });
    const watchEl = q.watch_for && q.watch_for.length && live
      ? h('p', { class: 'ws-watch' }, h('b', { text: 'Watch for: ' }), q.watch_for.join(' · ')) : null;
    const hintBox = h('div', { class: 'ws-hintbox', hidden: true, 'aria-live': 'polite' });
    const slipEl = q.slip_line && live ? h('p', { class: 'ws-slip', text: q.slip_line }) : null;
    const underEl = h('div', { class: 'ws-under' });
    const errLine = h('div', { class: 'ws-err', role: 'alert', hidden: true });
    const localEl = h('p', { class: 'ws-local', hidden: true, 'aria-live': 'polite' });
    const verdictEl = h('div', { class: 'verdict ws-verdict', hidden: true });
    const toolsEl = o.toolbar ? h('div', { class: 'tools-row', role: 'toolbar', 'aria-label': 'Tools' }) : null;
    const wantBar = o.bar ?? (mode === 'practice' || mode === 'inline' || mode === 'quiz' || mode === 'example');
    const barEl = wantBar ? h('div', { class: 'ws-bar' }) : null;
    let splitCtl = null;

    /* choices */
    let list = null, wrap = null, rows = [], coverEl = null, stageEl = null, whyToggle = null;
    let field = null, fieldWrap = null, sprBox = null, previewEl = null, errEl = null, hintEl = null, nudgeEl = null, padEl = null, localCheck = null;
    let lastPointer = 'mouse', swallow = false;

    if (mc) buildChoices(); else buildField();

    el.append(...[headEl, ruleTip].filter(Boolean));
    // figure, table and passage render inline here by default; the practice runner moves
    // these same nodes into its .rn-passage pane on wide screens (ws.passageNodes below)
    // rather than building them twice
    const figEl = q.figure ? figure(q) : null;
    const tableEl = q.table && q.table.length ? dataTable(q) : null;
    const passEl = q.text ? passage(q) : null;
    el.append(...[figEl, tableEl, passEl].filter(Boolean));
    el.append(stemEl, ...[watchEl, hintBox].filter(Boolean));
    if (stageEl) el.append(stageEl);
    if (whyToggle) el.append(whyToggle);
    el.append(mc ? wrap : sprBox);
    el.append(...[slipEl, underEl, errLine, localEl, toolsEl, verdictEl, barEl, status].filter(Boolean));
    paintStem(o.spans);

    /* ---------------- head: skill, type, difficulty, format, Again */
    function headLine() {
      if (o.head === false) return null;
      const hd = h('div', { class: 'q-skill ws-headline' });
      if (o.head && typeof o.head === 'object') {
        hd.append(o.head.glyph instanceof Node ? o.head.glyph : '', h('span', { class: 'ws-skill', text: o.head.label || '' }));
        return hd;
      }
      const t = UI.TOPIC && UI.TOPIC[q.topic];
      const skill = h('span', { class: 'ws-skill' },
        h('span', { class: 'ws-skill-name', text: o.hideSkill || (t ? t.short : q.topic_name || '') }));
      hd.append(skill);
      if (!o.hideSkill && q.name) hd.append(h('span', { class: 'ws-type', text: q.name }));
      if (q.difficulty) {
        const d = UI.dbars ? UI.dbars(q.difficulty) : h('span', { text: cap1(q.difficulty) });
        hd.append(h('span', { class: 'ws-diff' }, d));       // the difficulty only: the internal level stays off screen (the user)
      }
      if (!mc && o.fmt !== false) hd.append(h('span', { class: 'badge soft ws-fmt', text: 'Grid-in' }));   // fmt: false when the page labels the format
      if (q.repair || o.again) hd.append(h('span', { class: 'again', text: 'Again', title: q.text ? 'Another one like the one you missed'
        : q.repair_of ? `Same trap as question ${q.repair_of}, new numbers` : 'Same trap, new numbers' }));
      return hd;
    }
    function unhideSkill() {
      if (!o.hideSkill || !headEl) return;
      const t = UI.TOPIC && UI.TOPIC[q.topic];
      const nm = headEl.querySelector('.ws-skill-name');
      if (nm) nm.textContent = t ? t.short : q.topic_name || '';
      if (q.name && !headEl.querySelector('.ws-type')) headEl.querySelector('.ws-skill').after(h('span', { class: 'ws-type', text: q.name }));
    }

    /* ---------------- your rule for this type (P21): a study aid the server sends only in practice and review */
    function typeRule() {
      const tn = q.type_note;
      if (!tn) return null;
      const text = typeof tn === 'string' ? tn : tn.text;
      const day = tn.day && UI.date ? UI.date(tn.day, 'short') : tn.day;
      const d = h('details', { class: mode === 'exam' ? 'ws-rule' : 'fold ws-rule' },   // .fold opens in height; the test window keeps still
        h('summary', {}, h('b', { text: `Your rule${day ? ' · ' + day : ''}: ` }), text, icon('caret_down', 14)),
        h('p', { class: 'ws-rule-q' }, 'Still useful? ',
          quiet('Keep', () => { d.open = false; if (o.onRule) o.onRule('keep', text); }),
          ' · ',
          quiet('Remove', () => { d.remove(); if (o.onRule) o.onRule('remove', text); toast('Rule removed'); })));
      return d;
    }

    function paintStem(extra) {
      const spans = [];
      if (q.ask_span && live && !S.answered) spans.push({ start: q.ask_span[0], end: q.ask_span[1], kind: 'ask' });
      (extra || []).forEach(s => spans.push(s));
      stemText(stemEl, q.stem || '', spans);
    }

    /* ---------------- multiple choice */
    function buildChoices() {
      list = h('ol', { class: 'opts', role: 'radiogroup', 'aria-label': 'Answer choices' });
      rows = choices.map((c, i) => {
        const Lt = LETTERS[i];
        const t = q.text ? h('span', { class: 't', 'data-addr': `o:${i}`, text: c })      // R&W options are prose, never maths
          : tex(h('span', { class: 't', 'data-addr': `o:${i}` }), c, (q.latex || [])[i]);
        const mk = h('span', { class: 'mk', 'aria-hidden': 'true' });
        const cap = h('span', { class: 'opt-cap' });
        const b = h('button', { type: 'button', class: 'opt', role: 'radio', 'aria-checked': 'false', 'data-i': i }, h('span', { class: 'l', text: Lt }), t, cap, mk);
        const strikeB = h('button', { type: 'button', class: 'strike', 'aria-label': `Eliminate ${Lt}`, title: `Eliminate ${Lt} (Shift+${Lt})`, hidden: true }, h('span', { text: Lt }));
        const undoB = h('button', { type: 'button', class: 'quiet undo', 'aria-label': `Undo eliminating ${Lt}`, text: 'Undo', hidden: true });
        const why = h('div', { class: 'opt-why', hidden: true });
        const crowd = h('div', { class: 'opt-crowd', hidden: true });
        const li = h('li', { class: 'opt-row', role: 'none', 'data-i': i }, b, strikeB, undoB, why, crowd);
        b.addEventListener('pointerdown', e => { lastPointer = e.pointerType || 'mouse'; press(i, e); });
        b.addEventListener('click', () => tap(i));
        b.addEventListener('keydown', e => {
          if (e.key === 'Enter' && !e.metaKey && !e.ctrlKey) {
            e.preventDefault();
            lastPointer = 'keyboard';
            if (S.selected === i && canCheck()) check(e.shiftKey ? 'unsure' : 'auto'); else tap(i);
          }
        });
        b.addEventListener('contextmenu', e => {             // X6: right-click strikes, unless highlighting
          if (o.annotating && o.annotating()) return;
          if (!strikeAllowed()) return;
          e.preventDefault();
          strike(i);
        });
        strikeB.addEventListener('click', () => strike(i, true));
        undoB.addEventListener('click', () => { strike(i, false); b.focus({ preventScroll: true }); });
        return { li, b, t, mk, cap, strikeB, undoB, why, crowd };
      });
      list.append(...rows.map(r => r.li));
      list.addEventListener('keydown', e => {                  // roving focus inside the radiogroup
        const d = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
        const at = rows.findIndex(r => r.b === doc.activeElement);
        if (!d || at < 0) return;
        e.preventDefault();
        const next = rows[(at + d + n) % n];
        rows.forEach(r => { r.b.tabIndex = r === next ? 0 : -1; });
        next.b.focus();
      });
      const short = mode !== 'quiz' && !q.figure && n === 4 && choices.every(c => String(c).length <= 14);
      if (short) list.classList.add('two');
      wrap = h('div', { class: 'opts-wrap' }, list);
      if (mode === 'review' || mode === 'example') {
        const off = ls.get('satf.whyoff', false);
        el.classList.toggle('why-off', !!off);
        whyToggle = h('button', { type: 'button', class: 'quiet ws-whyhead', 'aria-expanded': String(!off) },
          h('span', { text: 'Why each wrong answer is wrong' }), icon('caret_down', 16));
        whyToggle.addEventListener('click', () => {
          const now = !el.classList.contains('why-off');
          el.classList.toggle('why-off', now);
          whyToggle.setAttribute('aria-expanded', String(!now));
          ls.set('satf.whyoff', now);
        });
        whyToggle.hidden = true;
      }
      if (coverAllowed() || S.covered) buildCover();
      if (S.stage) buildStage();
    }

    // X6: a 450ms hold strikes an option on touch, unless highlighting (the OS selection wins)
    let pressTimer = 0;
    function press(i, e) {
      if (e.pointerType !== 'touch' && e.pointerType !== 'pen') return;
      if (!strikeAllowed() || (o.annotating && o.annotating())) return;
      const r = rows[i];
      const x0 = e.clientX, y0 = e.clientY;
      r.li.classList.add('pressing');
      const stop = () => { clearTimeout(pressTimer); r.li.classList.remove('pressing'); r.b.removeEventListener('pointermove', move); };
      const move = ev => { if (Math.hypot(ev.clientX - x0, ev.clientY - y0) > 10) stop(); };
      r.b.addEventListener('pointermove', move);
      r.b.addEventListener('pointerup', stop, { once: true });
      r.b.addEventListener('pointercancel', stop, { once: true });
      r.b.addEventListener('pointerleave', stop, { once: true });
      clearTimeout(pressTimer);
      pressTimer = setTimeout(() => { stop(); swallow = true; strike(i); try { navigator.vibrate && navigator.vibrate(8); } catch (_) {} }, 450);
    }

    function tap(i) {
      if (swallow) { swallow = false; return; }
      if (mode === 'review' && S.hidden) return localPick(i);
      if (!canChoose()) return;
      if (S.struck.has(i)) { status.textContent = `${LETTERS[i]} is eliminated. Undo to choose it.`; return; }
      if (S.tries.some(t => t.given === i)) return;
      if (S.selected === i) {
        // P23: on touch, a second tap on the chosen option checks it
        if (live && !endMode && (lastPointer === 'touch' || lastPointer === 'pen') && performance.now() - S.selAt > 250 && canCheck()) return check('auto');
        if (mode === 'exam') return;                          // Bluebook: an answer is changed, never cleared
        return select(null);
      }
      select(i);
      if ((prefs.first_tap || o.firstTap) && live && !endMode) check('auto');
    }

    function select(i) {
      if (i !== null && (!mc || i < 0 || i >= n || S.struck.has(i))) return false;
      if (!canChoose()) return false;
      S.selected = i;
      S.selAt = performance.now();
      if (mode === 'exam' || endMode) { if (S.saved !== i) S.saved = null; if (o.onSelect) o.onSelect(i); }
      paint();
      changed();
      return true;
    }

    function strike(i, on, by = 'you') {
      if (!mc || i < 0 || i >= n || !strikeAllowed()) return false;
      if (on === undefined) on = !S.struck.has(i);
      if (on === S.struck.has(i)) return false;
      if (!on && S.hintStruck.has(i)) return false;             // a hint's strike has no Undo
      if (on) {
        S.struck.add(i);
        if (by === 'hint') S.hintStruck.add(i);
        if (S.selected === i) { S.selected = null; if ((mode === 'exam' || endMode) && o.onSelect) o.onSelect(null); }
      } else S.struck.delete(i);
      paint();
      status.textContent = on ? `${LETTERS[i]} eliminated` : `${LETTERS[i]} back`;
      if (o.onStrike) o.onStrike(i, on, by);
      changed();
      return true;
    }
    function eliminate(on = !S.eliminate) {
      if (!strikeAllowed() && on) return false;
      S.eliminate = !!on;
      paint();
      changed();
      return true;
    }

    /* ---------------- P5: cover the choices and solve first */
    function coverNumeric() {
      if (q.cover === 'field') return true;
      if (q.cover === 'ready') return false;
      return choices.every(c => spr.parse(String(c).replace(/,/g, '')).ok);
    }
    function buildCover() {
      const withField = coverNumeric();
      coverEl = h('div', { class: 'ws-cover', hidden: true, role: 'group', 'aria-label': 'Choices covered' });
      const lead = h('p', { class: 'cover-lead' }, h('b', { text: 'Choices covered' }), ' · work it out, then reveal');
      coverEl.append(lead);
      if (withField) {
        const fid = uid('own');
        const own = h('input', { id: fid, class: 'field', type: 'text', autocomplete: 'off', spellcheck: 'false', maxlength: '7', placeholder: spr.PLACEHOLDER, value: S.own });
        const pv = h('p', { class: 'preview spr-preview' });
        const err = h('p', { class: 'field-err', hidden: true });
        const go = h('button', { type: 'button', class: 'btn', text: o.onOwn ? 'Check my answer' : 'Keep my answer', disabled: true });
        const sync = () => {
          const p = spr.preview(pv, own.value);
          S.own = spr.clean(own.value);
          err.hidden = !p.error;
          err.textContent = p.error || '';
          go.disabled = !p.ok || S.busy;
        };
        own.addEventListener('input', sync);
        own.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); if (!go.disabled) go.click(); } });
        go.addEventListener('click', () => (o.onOwn ? checkOwn() : cover(false)));
        coverEl.append(h('label', { class: 'label', for: fid, text: 'Your answer' }), own, pv, err,
          h('div', { class: 'cover-acts' }, go, quiet('Show choices', () => cover(false))));
        coverEl._own = own;
        sync();
      } else {
        coverEl.append(h('div', { class: 'cover-acts' }, h('button', { type: 'button', class: 'btn', text: 'Ready: show choices', onclick: () => cover(false) })));
      }
      wrap.append(coverEl);
    }
    function cover(on = !S.covered) {
      if (!mc || S.answered) return false;
      if (on && !coverEl) buildCover();
      if (!coverEl) return false;
      const was = S.covered;
      S.covered = !!on;
      if (on && !was) S.coverAt = performance.now();
      if (!on && was && o.onCover) o.onCover({ covered: false, own: S.own || null, reveal_ms: Math.round(performance.now() - (S.coverAt || S.shownAt)) });
      if (on && o.onCover) o.onCover({ covered: true });
      paint();
      if (on && coverEl._own) setTimeout(() => coverEl._own.focus({ preventScroll: true }), 30);
      changed();
      return true;
    }
    async function checkOwn() {
      if (S.busy || !S.own) return;
      S.busy = true; paint();
      let fb;
      try { fb = await o.onOwn(S.own, meta(S.lastConf)); }
      catch (e) { S.busy = false; paint(); return showErr(e, () => checkOwn()); }
      S.busy = false;
      if (!fb) return paint();
      if (fb.cover === 'none') {
        S.covered = false;
        paint();
        showLocal(`No choice is ${minus(S.own)}. Recheck, then pick.`);
        return;
      }
      S.covered = false;
      take(fb, fb.given ?? keyIndex(fb));
    }

    /* ---------------- a staged item (W2 relationship first, W6 predict the blank) */
    function buildStage() {
      const s = o.stage;
      stageEl = h('div', { class: 'ws-stage' }, h('p', { class: 'stage-q', text: s.prompt || 'Before the choices: what does the blank need?' }));
      if (s.options && s.options.length) {
        const ol = h('ol', { class: 'stage-opts' });
        s.options.forEach((t, i) => ol.append(h('li', {}, h('button', { type: 'button', class: 'btn', onclick: () => stageDone(i) }, h('span', { class: 'kbd', text: String(i + 1) }), t))));
        stageEl.append(ol);
      }
      stageEl.append(quiet(s.skip || 'Show the choices', () => stageDone(null)), h('span', { class: 'meta', text: ' Enter' }));
    }
    function stageDone(i) {
      if (S.stage !== 'on') return;
      S.stage = 'done';
      S.stagePick = i;
      stageEl.hidden = true;
      if (o.stage.onPick) o.stage.onPick(i);
      paint();
      const first = rows[0];
      if (first && lastPointer === 'keyboard') first.b.focus({ preventScroll: true });
      changed();
    }

    /* ---------------- grid-in */
    function buildField() {
      const fid = uid('f'), rid = uid('r'), eid = uid('e');
      const exam = mode === 'exam';
      const padOn = mode !== 'review' && mode !== 'example' && (o.pad ?? (coarse() && ls.get('satf.pad', true) !== false));
      field = h('input', { id: fid, class: 'field', type: 'text', autocomplete: 'off', autocapitalize: 'off', autocorrect: 'off', spellcheck: 'false',
        maxlength: '7', placeholder: exam ? spr.EXAM_PLACEHOLDER : spr.PLACEHOLDER, inputmode: padOn ? 'none' : 'text', enterkeyhint: exam ? 'next' : 'done',
        'aria-describedby': `${rid} ${eid}` });
      field.value = S.value;
      fieldWrap = h('div', { class: 'grid-in' }, field);
      previewEl = h('p', { class: 'preview spr-preview', 'aria-live': 'polite' });
      errEl = h('p', { class: 'field-err', id: eid, hidden: true });
      hintEl = h('p', { class: 'help spr-hint', hidden: true, role: 'status' });
      nudgeEl = h('p', { class: 'spr-nudge', hidden: true, role: 'status' });
      const rulesBtn = h('button', { type: 'button', class: 'qlink spr-all', text: 'Entry rules', 'aria-haspopup': 'dialog' });
      rulesBtn.addEventListener('click', () => (UI.pop ? UI.pop(rulesBtn, directions(), { label: 'Entering your answer' }) : null));
      const rule = h('p', { class: 'help spr-rule', id: rid }, h('span', { class: 'sr', text: spr.RULE }), rulesBtn);
      if (mode === 'review') {                                   // answers hidden: check here, file nothing
        localCheck = h('button', { type: 'button', class: 'btn', text: 'Check', hidden: true, onclick: () => localPick(spr.clean(field.value)) });
        fieldWrap.append(localCheck);
      }
      const box = sprBox = h('div', { class: 'spr' }, h('label', { class: 'label', for: fid, text: 'Your answer' }), fieldWrap, previewEl, errEl, hintEl, nudgeEl, rule);
      if (padOn) { padEl = pad(field); box.append(padEl); }
      let good = S.value, hintTimer = 0, selTimer = 0;
      const flash = text => { hintEl.textContent = text; hintEl.hidden = false; clearTimeout(hintTimer); hintTimer = setTimeout(() => { hintEl.hidden = true; }, 3000); };
      field.addEventListener('input', () => {
        let v = spr.clean(field.value);
        if (exam) {                                             // Tests 4.3: a rejected key keeps the value
          if (!spr.charsOk(v) || (v.includes('-') && !v.startsWith('-'))) { field.value = good; return flash(spr.HINT_BAD); }
          if (v.length > spr.cap(v)) { field.value = good; return flash(spr.HINT_LONG); }
        }
        good = field.value;
        S.value = v;
        field.classList.remove('tried');
        onValue();
        if (mode === 'exam' || endMode) { clearTimeout(selTimer); selTimer = setTimeout(() => { if (o.onSelect) o.onSelect(spr.parse(S.value).ok ? S.value : null); }, 400); }
        if (mode === 'review' && localCheck) localCheck.hidden = !spr.parse(v).ok;
        changed();
      });
      field.addEventListener('keydown', e => {
        if (e.key !== 'Enter') return;
        e.preventDefault();
        if (mode === 'exam') { if (o.onEnter) o.onEnter(); return; }
        if (mode === 'review' && S.hidden) { if (spr.parse(field.value).ok) localPick(spr.clean(field.value)); return; }
        if (canCheck()) check(e.shiftKey ? 'unsure' : 'auto');
      });
      if (live && !S.answered && o.autofocus !== false && media('(hover: hover)')) setTimeout(() => { if (!S.answered && field.isConnected) field.focus({ preventScroll: true }); }, 60);
    }
    function onValue() {
      const p = spr.preview(previewEl, S.value);
      errEl.hidden = !p.error;
      errEl.textContent = p.error || '';
      field.setAttribute('aria-invalid', p.error ? 'true' : 'false');
      if (o.formNudge && p.ok && spr.repeatingCut(S.value) && !nudged.has(S.value)) {
        nudged.add(S.value);
        nudgeEl.textContent = 'If it repeats, fill the grid: .6666 or .6667, or enter 2/3. A short repeating decimal is marked wrong.';
        nudgeEl.hidden = false;
        if (o.onNudge) o.onNudge({ kind: 'form', value: S.value });
        setTimeout(() => { nudgeEl.hidden = true; }, 6000);
      }
      paint();
    }

    /* ---------------- rules for what is allowed now */
    function canChoose() {
      if (S.answered && !(mode === 'review' && S.hidden)) return false;
      if (S.busy || S.covered || S.stage === 'on') return false;
      if (mode === 'example') return false;
      if (mode === 'review') return S.hidden || !!o.canPick;
      return true;
    }
    function strikeAllowed() {
      return mc && !S.answered && !S.covered && S.stage !== 'on' && mode !== 'review' && mode !== 'example';
    }
    function coverAllowed() {
      return mc && !S.answered && (o.coverTool ?? (mode === 'practice' || mode === 'inline')) && !S.stage;
    }
    function hintAllowed() {
      return !!o.onHint && !S.answered && live && !endMode && (q.rungs || []).length > S.hints;
    }
    function value() {
      if (mc) return S.selected;
      const p = spr.parse(S.value);
      return p.ok ? p.s : null;
    }
    function canCheck() {
      if (S.answered || S.busy || S.stage === 'on') return false;
      if (mode === 'exam' || mode === 'example') return false;
      if (mode === 'review') return false;
      if (S.covered) return !!(o.onOwn && spr.parse(S.own).ok);
      return mc ? S.selected !== null : spr.parse(S.value).ok;
    }
    function elapsed() {
      const away = S.awayMs + (S.awayAt ? performance.now() - S.awayAt : 0);
      return Math.max(0, Math.round(performance.now() - S.shownAt - away));
    }
    const onVis = () => {
      if (doc.hidden) S.awayAt = performance.now();
      else if (S.awayAt) { S.awayMs += performance.now() - S.awayAt; S.awayAt = null; }
    };
    doc.addEventListener('visibilitychange', onVis);
    cleanups.push(() => doc.removeEventListener('visibilitychange', onVis));
    function meta(conf) {
      return { qid: q.id, conf: S.tries.length ? null : conf, hints: S.hints, struck: [...S.struck], hint_struck: [...S.hintStruck],
        ms: elapsed(), try: S.tries.length + 1, own: S.own || null, stage: S.stagePick, covered: !!q.cover_used || !!S.coverAt };
    }

    /* ---------------- painting */
    function paint() {
      el.classList.toggle('answers-hidden', mode === 'review' && S.hidden);
      el.classList.toggle('is-busy', S.busy);
      if (mc) {
        const stop = S.selected ?? rows.findIndex((r, i) => !S.struck.has(i));
        rows.forEach((r, i) => {
          const on = S.selected === i;
          const out = S.struck.has(i);
          const tried = S.tries.some(t => t.given === i);
          r.b.classList.toggle('picked', on && (!S.answered || (mode === 'review' && S.hidden)));
          r.b.classList.toggle('saved', on && S.saved === i);
          r.b.setAttribute('aria-checked', String(on));
          r.li.classList.toggle('out', out);
          r.li.classList.toggle('tried', tried && !S.answered);
          r.b.setAttribute('aria-disabled', String(out || tried || !canChoose()));
          r.strikeB.hidden = !(S.eliminate && !out && strikeAllowed());
          r.undoB.hidden = !(out && strikeAllowed() && !S.hintStruck.has(i));
          r.b.tabIndex = i === stop ? 0 : -1;
        });
        list.classList.toggle('eliminating', S.eliminate && strikeAllowed());
        list.classList.toggle('done', S.answered && !(mode === 'review' && S.hidden));
        list.classList.toggle('covered', S.covered);
        list.classList.toggle('staged', S.stage === 'on');
        if (coverEl) coverEl.hidden = !S.covered;
        if (whyToggle) whyToggle.hidden = !S.answered || (mode === 'review' && S.hidden);
      } else {
        field.readOnly = (S.answered && !(mode === 'review' && S.hidden)) || S.busy || mode === 'example' || (mode === 'review' && !S.hidden);
        fieldWrap.classList.toggle('saved', S.saved !== null && S.saved === S.value && !!S.value);
        if (padEl) padEl.hidden = field.readOnly;
      }
      renderUnder();
      syncBar();
      if (toolsEl) renderTools(toolsEl);
    }

    function renderUnder() {
      underEl.replaceChildren();
      if (S.answered) { underEl.hidden = true; return; }
      if (hintAllowed()) {
        const total = q.rungs.length;
        underEl.append(h('button', { type: 'button', class: 'quiet ws-hint', 'aria-keyshortcuts': 'W', title: 'Hint (W)', onclick: () => hint() },
          icon('hint', 16), `Hint · ${S.hints + 1} of ${total}`));
      }
      if (fbMode === 'retry' && live && S.tries.length) {
        const left = Math.max(0, maxTries - S.tries.length);
        underEl.append(h('span', { class: 'ws-tries', text: `${left} ${left === 1 ? 'try' : 'tries'} left` }),
          quiet('Show answer', () => showAnswer()));
      }
      if (o.onSkip && live && !S.busy) underEl.append(quiet('Skip for now', () => skip(), { cls: 'ws-skip', title: 'Skip (S)' }));
      if (mc && live && !endMode && S.selected !== null && coarse()) {     // P23: shown in a learner's first 3 questions
        if (S.tapHint === undefined) { S.tapHint = ls.get('satf.tap', 0) < 3; if (S.tapHint) bump('satf.tap', 3); }
        if (S.tapHint) underEl.append(h('span', { class: 'ws-taphint', text: 'Tap again to check' }));
      }
      if (S.fastAsk) {
        underEl.append(h('span', { class: 'ws-fast', text: `That took ${mmss(elapsed())}. Check anyway?` }),
          h('button', { type: 'button', class: 'btn sm', text: 'Check anyway', onclick: () => check(S.lastConf) }), h('span', { class: 'meta', text: 'Enter' }));
      }
      underEl.hidden = !underEl.children.length;
    }

    function syncBar() {
      if (!barEl) return;
      if (mode === 'example') {
        if (!barEl.children.length && o.onDone) barEl.append(h('button', { type: 'button', class: 'pill', text: o.doneLabel || 'Your turn', onclick: () => o.onDone() }));
        barEl.hidden = !o.onDone;
        return;
      }
      if (S.answered) {
        if (splitCtl) { barEl.replaceChildren(); splitCtl = null; }
        if (o.onNext && !barEl.querySelector('.ws-next')) {
          const nx = h('button', { type: 'button', class: 'pill ws-next' }, o.nextLabel || 'Next', h('kbd', { class: 'kbd', text: 'Enter' }));
          nx.addEventListener('click', () => o.onNext());
          barEl.append(nx);
        }
        barEl.hidden = !barEl.children.length;
        return;
      }
      if (!live || S.stage === 'on') { barEl.hidden = true; return; }
      if (!splitCtl) splitCtl = splitCheck(barEl, { confidence: prefs.confidence, save: endMode, onSubmit: conf => check(conf) });
      splitCtl.set({ enabled: canCheck(), firstTry: S.tries.length === 0, save: endMode });
      barEl.hidden = false;
    }

    /* ---------------- checking */
    async function check(conf = 'auto') {
      if (S.busy || S.answered) return false;
      if (S.covered && mc) { if (o.onOwn && spr.parse(S.own).ok) checkOwn(); return false; }
      if (!canCheck()) return false;
      if (conf === 'auto' && prefs.confidence !== 'off' && !S.tries.length) conf = 'sure';   // D: no unrated first try
      S.lastConf = conf;
      // P8: a fast answer on a slip-prone type asks once
      if (q.check_anyway && !S.fastOk && elapsed() < (q.check_anyway.under_ms || 0)) {
        S.fastOk = true; S.fastAsk = true; renderUnder();
        return false;
      }
      S.fastAsk = false;
      const a = value();
      const m = meta(conf);
      if (endMode) {                                             // Save & next: nothing revealed
        S.busy = true; paint();
        try { if (o.onCheck) await o.onCheck(a, Object.assign(m, { save: true })); }
        catch (e) { S.busy = false; paint(); return showErr(e, () => check(conf)); }
        S.busy = false;
        S.saved = a;
        errLine.hidden = true;
        paint(); changed();
        return true;
      }
      if (!o.onCheck) return false;
      S.busy = true; errLine.hidden = true; paint();
      status.textContent = 'Checking';
      let fb;
      try { fb = await o.onCheck(a, m); }
      catch (e) { S.busy = false; paint(); return showErr(e, () => check(conf)); }
      S.busy = false;
      if (fb === undefined) { S.pending = true; paint(); return true; }   // the page reveals
      if (!fb) { paint(); return false; }
      take(fb, a);
      return true;
    }
    function take(fb, a) {
      if (fbMode === 'retry' && live && fb.correct === false && fb.final === false) return wrongTry(fb, a);
      reveal(Object.assign({ given: a, conf: S.tries.length ? null : S.lastConf }, fb), { fresh: true });
    }
    // the answer lands: the key fills (its CSS transition), its letter pops once and its check draws; a wrong pick
    // dims, is struck and its cross draws; the verdict's disc draws its mark. UI.fx is a no-op under reduced
    // motion and in the test window (which never reveals anyway)
    function land(key, g, right) {
      if (!UI.fx || !live) return;
      const r = rows[key];
      if (r) { r.b.classList.add('land'); UI.fx.pop(r.b.querySelector('.l')); UI.fx.check(r.mk, { delay: 60 }); }
      const w = g !== null && g !== key ? rows[g] : null;
      if (w) { w.b.classList.add('land'); UI.fx.check(w.mk); }
      const vg = verdictEl.querySelector('.v-glyph');
      if (vg && vg.querySelector('svg')) UI.fx.check(vg, { delay: right ? 120 : 60 });
    }
    function wrongTry(fb, a) {
      S.tries.push({ given: a, reason: fb.mistake || fb.reason || null, filler: !!fb.filler });
      const reason = fb.mistake || fb.reason;
      const text = fb.filler ? 'That’s a near value. Check your arithmetic.'
        : reason ? `That answer comes from: ${low1(reason)}. Try another.` : 'Not right. Try another.';
      if (mc) {
        S.selected = null;
        const r = rows[a];
        if (r) {
          r.mk.replaceChildren(markIcon('x'));
          r.why.replaceChildren(h('p', { class: 'opt-why-l mine', text })); r.why.hidden = false;
          if (UI.fx) UI.fx.check(r.mk);              // the cross draws on the try (no shake)
        }
      } else {
        field.classList.add('tried');
        showLocal(fb.mistake ? `${cap1(fb.mistake)}.` : 'Not right.');
      }
      const left = fb.tries_left ?? Math.max(0, maxTries - S.tries.length);
      status.textContent = `Not right. ${left} ${left === 1 ? 'try' : 'tries'} left.`;
      paint(); changed();
    }
    async function showAnswer() {
      if (S.busy || S.answered) return;
      S.busy = true; paint();
      let fb;
      try { fb = o.onShowAnswer ? await o.onShowAnswer() : o.onCheck ? await o.onCheck(null, Object.assign(meta(null), { show: true })) : null; }
      catch (e) { S.busy = false; paint(); return showErr(e, () => showAnswer()); }
      S.busy = false;
      if (fb) reveal(Object.assign({ given: null, shown: true }, fb)); else paint();
    }
    function showErr(e, retry) {
      const offline = navigator.onLine === false || (e && e.offline);
      errLine.replaceChildren(h('p', { class: 'error', text: offline ? 'You’re offline. Your answer will be sent when you’re back.' : 'Could not send your answer.' }),
        retry ? h('button', { type: 'button', class: 'quiet', text: 'Try again', onclick: () => { errLine.hidden = true; retry(); } }) : null);
      errLine.hidden = false;
      if (offline && retry) {
        const once = () => { removeEventListener('online', once); if (!S.answered && !errLine.hidden) { errLine.hidden = true; retry(); } };
        addEventListener('online', once);
        cleanups.push(() => removeEventListener('online', once));
      }
      return false;
    }
    function showLocal(text) { localEl.textContent = text; localEl.hidden = !text; }

    /* ---------------- hints (P2) and skip */
    async function hint() {
      if (!hintAllowed() || S.busy) return false;
      S.busy = true; paint();
      let r;
      try { r = await o.onHint(q.id); }
      catch (e) { S.busy = false; paint(); showLocal((e && e.message) || 'No hint for this one right now.'); return false; }
      S.busy = false;
      if (!r) { paint(); return false; }
      S.hints++;
      if (r.kind === 'strike' && Number.isInteger(r.choice)) {
        strike(r.choice, true, 'hint');
        // a passage question's reason is the option's own sentence, not a step that went wrong
        hintMsg(`Struck ${LETTERS[r.choice]}`, !r.reason ? 'a trap, not the answer.' : q.text ? r.reason : `that’s what you get if you ${low1(r.reason)}.`);
      } else if (r.kind === 'step') hintMsg('First step', r.step);
      else if (r.kind === 'example' && !r.example) hintMsg('No worked example left', 'you have met every question of this kind.');
      else if (r.kind === 'example') {
        const open = () => (o.onExample ? o.onExample(r.example) : r.example && exampleSheet(r.example));
        open();
        // closing it keeps a way back (the user: closed the auto pop-up and had no way to open it again)
        hintBox.append(h('p', { class: 'ws-hint-l' }, h('b', { text: 'Worked twin: ' }), quiet('Show it', () => open()),
          ' · this one still counts as yours.'));
        hintBox.hidden = false;
      }
      paint(); changed();
      return true;
    }
    function hintMsg(head, text) {
      hintBox.append(h('p', { class: 'ws-hint-l' }, h('b', { text: head + ': ' }), texText(h('span'), text)));
      hintBox.hidden = false;
    }
    function skip() {
      if (!o.onSkip || S.answered) return false;
      o.onSkip(q.id, meta(null));
      return true;
    }

    /* ---------------- review with answers hidden: a pick reveals here, and files only if the page says */
    function localPick(a) {
      const fb = S.fb || o.fb;
      if (!fb) return;
      let right;
      if (mc) {
        right = a === keyIndex(fb);
        S.selected = a;
        markRows(keyIndex(fb), a, 'Your pick');
        optionLines(fb, a);
      } else {
        const forms = (fb.accepted || [fb.answer]).map(x => spr.clean(x));
        const pv = spr.parse(a), kv = spr.parse(fb.answer);
        right = forms.includes(spr.clean(a)) || (pv.ok && kv.ok && Math.abs(pv.value - kv.value) < 1e-9);
        fieldWrap.classList.toggle('ok', right);
        fieldWrap.classList.toggle('no', !right);
      }
      const was = fb.correct === true;
      const shown = mc ? LETTERS[a] : minus(a);
      showLocal(`${shown} · ${right ? (was ? 'right again' : 'right this time') : (was ? 'wrong this time' : 'wrong again')}`);
      S.hidden = false;
      paint();
      if (o.onReanswer) o.onReanswer(a, right);
    }
    function setHidden(on) {
      S.hidden = !!on;
      // hidden means hidden to every reader: no key or pick classes (the pick's strike), labels or status text left behind
      if (on) { showLocal(''); S.selected = null; status.textContent = ''; if (mc) markRows(null, null, ''); if (field) { field.value = ''; S.value = ''; fieldWrap.classList.remove('ok', 'no'); onValue(); } }
      else if (S.fb) {
        S.selected = givenIndex(S.fb.given);
        if (mc) { markRows(keyIndex(S.fb), S.selected, 'Your answer'); optionLines(S.fb); }
        if (field && S.fb.given != null) field.value = minus(S.fb.given);
        if (fieldWrap) { fieldWrap.classList.toggle('ok', S.fb.correct === true); fieldWrap.classList.toggle('no', S.fb.correct === false); }
      }
      paint();
    }

    /* ---------------- the reveal */
    function reveal(fb, ro = {}) {
      S.answered = true; S.fb = fb; S.busy = false; S.pending = false; S.covered = false; S.fastAsk = false;
      if (S.stage === 'on') { S.stage = 'done'; if (stageEl) stageEl.hidden = true; }
      el.classList.add('revealed');
      el.classList.toggle('right', fb.correct === true);
      el.classList.toggle('wrong', fb.correct === false);
      unhideSkill();
      const key = keyIndex(fb), g = mc ? givenIndex(fb.given) : null;
      if (mc) {
        S.selected = g;
        if (fb.reasons && list.classList.contains('two')) list.classList.remove('two');   // reasons read better in rows
        markRows(key, g, 'Your answer');
        optionLines(fb);
        crowdBars(fb);
      } else {
        if (fb.given !== undefined && fb.given !== null && !field.value) { field.value = minus(fb.given); S.value = spr.clean(fb.given); }
        fieldWrap.classList.toggle('ok', fb.correct === true);
        fieldWrap.classList.toggle('no', fb.correct === false);
        previewEl.replaceChildren();
        errEl.hidden = true;
        if (padEl) padEl.hidden = true;
      }
      paintStem(fb.spans);
      verdictSlot(fb, ro);
      paint();
      if (ro.fresh && mc) land(key, g, fb.correct === true);
      else if (ro.fresh && UI.fx && live) { const vg = verdictEl.querySelector('.v-glyph'); if (vg && vg.querySelector('svg')) UI.fx.check(vg, { delay: 60 }); }
      if (!ro.keepLocal) showLocal('');
      const keyText = mc && key !== null ? LETTERS[key] : minus(fb.answer);
      status.textContent = fb.correct ? 'Right' : (fb.given === null || fb.given === undefined) ? `The answer is ${keyText}` : `Wrong. The answer is ${keyText}`;
      if (fb.closed && fb.closed.length && UI.refresh && live) { try { UI.refresh(); } catch (_) {} }
      if (o.onReveal) o.onReveal(fb);
      changed();
    }

    // the key, your pick and earlier tries, each with a glyph and a word (R20: never colour alone)
    function markRows(key, g, mine) {
      rows.forEach((r, i) => {
        r.b.classList.remove('picked');
        r.b.classList.toggle('ok', i === key);
        r.b.classList.toggle('no', i === g && i !== key);
        const tried = S.tries.some(t => t.given === i);
        r.b.classList.toggle('tried', tried && i !== g);
        r.mk.replaceChildren(...(i === key ? [markIcon('check')] : (i === g || tried) ? [markIcon('x')] : []));
        r.cap.textContent = i === key ? (i === g ? `${mine} · Correct` : 'Correct answer') : i === g ? mine : tried ? 'Tried' : '';
        r.b.setAttribute('aria-label', `${LETTERS[i]}, ${choices[i]}${i === key ? ', the answer' : ''}${i === g ? `, ${mine.toLowerCase()}` : ''}`);
      });
    }

    // every option's misconception, with its value, where it leaves the steps, and a drill (P1, W1)
    function optionLines(fb, pick) {
      const reasons = fb.reasons;
      if (!reasons || (prefs.option_reasons === false && live && mode !== 'quiz')) return;
      const key = keyIndex(fb), g = pick !== undefined ? pick : givenIndex(fb.given);
      rows.forEach((r, i) => {
        r.why.replaceChildren();
        const reason = reasons[i];
        const filler = (fb.filler && fb.filler[i]) || (!reason && i !== key);
        if (i === key && !reason) { r.why.hidden = true; return; }
        const mine = i === g && i !== key && mode === 'review';
        const share = fb.crowd && Array.isArray(fb.crowd.option_share) && i !== key ? fb.crowd.option_share[i] : null;   // SR12, n >= 20
        const line = h('p', { class: 'opt-why-l' + (i === g ? ' mine' : '') + (i === key ? ' key' : '') },
          // just the reason: the letter and the value sit right above it, rendered (a raw "w^2" here read as a bug)
          mine ? 'Your pick · ' : null, cap1(filler ? 'a nearby value, not tied to a specific mistake' : reason),
          mine && fb.pick_note ? h('span', { class: 'opt-why-note', text: ` · ${fb.pick_note}` }) : null,
          share !== null && share !== undefined ? h('span', { class: 'opt-why-share', text: ` · ${pct(share)}% of students who miss it pick this one` }) : null);
        // V6: the student corrects the label on their own filed pick (not a local pick made while hidden)
        if (mine && pick === undefined && o.onNotMine) line.append(' ', h('button', { type: 'button', class: 'qlink opt-notmine', 'aria-haspopup': 'menu', text: 'Not what I did?', onclick: e => o.onNotMine(e.currentTarget, i) }));
        const acts = h('span', { class: 'opt-why-acts' });
        if (mine && !filler && o.onSpot) acts.append(quiet('Spot this trap', () => o.onSpot(i)));          // SR11
        if (!filler && i !== key && fb.steps && fb.option_steps && Number.isInteger(fb.option_steps[i])) {
          acts.append(quiet(`See where ${LETTERS[i]} comes from`, () => outlineStep(fb.option_steps[i])));
        }
        if (!filler && i !== key && o.onTrap && live) {
          acts.append(quiet('Practise this trap', async e => {
            if (S.queued >= 3) { toast('Three are queued for this question already'); return; }
            const btn = e.currentTarget;
            btn.disabled = true;
            try { await o.onTrap(i, reason); S.queued++; addLine('v-queued', 'Next: one with this trap'); }
            catch (_) { btn.disabled = false; toast('Couldn’t add it. Try again.'); }
          }));
        }
        r.why.append(line);
        if (acts.children.length) r.why.append(acts);
        r.why.hidden = false;
      });
    }
    function crowdBars(fb) {
      const c = fb.crowd;
      if (!c || !Array.isArray(c.options) || (c.n !== undefined && c.n < 20)) return;
      rows.forEach((r, i) => {
        const p = c.options[i];
        if (p === undefined || p === null) return;
        const v = pct(p);
        const bar = h('span', { class: 'bar' }, h('i', { style: `width:${Math.max(0, Math.min(100, v))}%` }));
        r.crowd.replaceChildren(bar, h('span', { class: 'meta', text: `${v}% chose this` }));
        r.crowd.hidden = false;
      });
    }

    function addLine(cls, ...kids) {
      const p = h('p', { class: 'v-line ' + cls }, ...kids);
      const x = verdictEl.querySelector(':scope > .x-fold, :scope > .ws-actions');
      if (x) x.before(p); else verdictEl.append(p);
      return p;
    }

    /* ---------------- the verdict slot (G4), top to bottom */
    function verdictSlot(fb, ro) {
      const v = verdictEl;
      v.replaceChildren();
      v.hidden = false;
      const key = keyIndex(fb), g = mc ? givenIndex(fb.given) : null;
      const blank = mc ? g === null : (fb.given === null || fb.given === undefined || fb.given === '');
      const right = fb.correct === true;

      // 1. verdict and key
      v.append(vHead(fb, right, blank));
      freshNow = !!ro.fresh;
      if (!mc) v.append(...gridLines(fb, right, blank));
      // the options carry Your answer and Correct answer; the boxes only say what they can't: that nothing was picked
      else if (mode === 'review' && blank) v.append(answerBoxes(fb, key, g, blank));

      // 2. a mistake that closed
      const closed = (fb.closed || []).map(c => (typeof c === 'string' ? { label: c } : c)).filter(c => c && c.label);
      // the server's next step ("That closes it: X is fixed · a check-in comes back in 3 days") would repeat the line
      // above it: its check-in joins the Fixed line and the next-step line goes
      const closesStep = !!closed.length && /^That closes it:/.test(fb.next_step || '');
      const checkIn = closesStep ? (String(fb.next_step).match(/check-in comes back in (.+)$/) || [])[1] : null;
      closed.forEach((c, ci) => {
        const bits = [c.hits ? `caught you ${c.hits}×${c.since ? ' since ' + (UI.date ? UI.date(c.since, 'short') : c.since) : ''}` : null,
          c.days !== undefined || c.questions !== undefined ? [c.days !== undefined ? `${c.days} day${c.days === 1 ? '' : 's'}` : null, c.questions !== undefined ? `${c.questions} question${c.questions === 1 ? '' : 's'}` : null].filter(Boolean).join(', ') : null].filter(Boolean);
        v.append(h('p', { class: 'v-fixed' + (still() ? '' : ' pop') }, icon('check', 16), h('b', { text: 'Fixed' }), ` · ${low1(c.label)}`, bits.map(b => ` · ${b}`),
          checkIn && ci === 0 ? ` · check-in in ${checkIn}` : null));
      });

      // 3. the named mistake, confidence, traps on offer, causes, habit
      if (!right && !blank) {
        const reason = mc ? (fb.mistake || (fb.reasons && fb.reasons[g])) : null;
        // the pick's own reason already sits under its option (optionLines): the line would say it twice
        const same = (x, y) => String(x || '').trim().replace(/\.$/, '').toLowerCase() === String(y || '').trim().replace(/\.$/, '').toLowerCase();   // case and a full stop aside
        const onOption = mc && fb.reasons && same(fb.reasons[g], reason) && !fb.trap && !fb.trap_check && mode !== 'quiz' && !(prefs.option_reasons === false && live);
        if (mc && reason && !onOption) {
          v.append(h('p', { class: 'mistake' },
            fb.trap ? h('span', { class: 'badge soft trap-chip', text: cap1(String(fb.trap).replace(/_/g, ' ')) }) : null,
            h('span', { text: cap1(reason) }),
            fb.trap_check ? h('span', { class: 'mistake-check', text: fb.trap_check }) : null));
        }
        if (fb.sure_miss || fb.conf === 'sure') v.append(h('p', { class: 'v-note' }, h('b', { text: 'Sure, but wrong.' }), ' It comes back first.'));
      }
      if (fb.cover === 'key') v.append(h('p', { class: 'v-line v-ok', text: 'Solved without the choices' }));
      else if (fb.cover === 'distractor' && g !== null && S.own) {
        v.append(h('p', { class: 'v-line', text: `Your ${minus(S.own)} is choice ${LETTERS[g]}${fb.reasons && fb.reasons[g] ? `: you ${low1(fb.reasons[g])}` : ''}.` }));
      }
      if (mc && fb.reasons && !blank && mode !== 'quiz') v.append(...trapsLines(fb, key, g, right));
      if (!right && !blank && fb.cause && o.onCause) v.append(causeChips(fb.cause));
      if (fb.habit && fb.habit.name) v.append(habitChip(fb.habit));
      // the verdict's headline already names the trap the answer came from: the new-mistake line then only says what it takes
      const named = g !== null && fb.reasons && fb.reasons[g] ? String(fb.reasons[g]).trim().toLowerCase() : null;
      (fb.opened || []).map(x => (typeof x === 'string' ? { label: x } : x)).filter(x => x && x.label).forEach(x => {
        const same = named && String(x.label).trim().toLowerCase() === named;
        v.append(h('p', { class: 'v-line v-new' }, h('b', { text: same ? 'New mistake to fix' : 'New mistake to fix: ' }), same ? '' : cap1(x.label),
          ` · ${x.clean ?? 0} of ${x.of ?? 2} correct answers · `, h('a', { class: 'qlink', href: x.href || '/review/?tab=redo', text: 'See it in Review' })));
      });
      if (fb.repair_next) v.append(h('p', { class: 'v-line', text: q.text ? 'Next: another one like this' : 'Next: one like this, with new numbers' }));

      // 4. the next step; then the tail (mastery, then vs now, the saved note, the formula, everyone), one group
      // that a wide practice runner shows in its Details column instead (.v-tail is display: contents here)
      const openedNow = (fb.opened || []).map(x => String((typeof x === 'string' ? x : x && x.label) || '').toLowerCase()).filter(Boolean);
      if (fb.next_step && !closesStep && !openedNow.some(l => fb.next_step.toLowerCase().startsWith(l))) v.append(h('p', { class: 'v-line v-next', text: fb.next_step }));
      const tail = h('div', { class: 'v-tail' });
      if (fb.mastery && UI.masteryWord) tail.append(masteryLine(fb.mastery));
      if (fb.then) tail.append(h('p', { class: 'v-line v-then', text: fb.then }));
      // V3: a fresh version from the Saved pool brings back the note on the saved one
      const sn = typeof fb.saved_note === 'string' ? { text: fb.saved_note } : fb.saved_note;
      if (sn && sn.text) tail.append(h('p', { class: 'v-line v-snote' }, h('b', { text: `Your note on the saved one${sn.at ? ' · ' + (UI.date ? UI.date(sn.at, 'short') : sn.at) : ''}: ` }), sn.text));
      (fb.formula || []).forEach(f => tail.append(formulaLine(f)));
      if (fb.crowd && fb.crowd.first_rate !== undefined && (fb.crowd.n === undefined || fb.crowd.n >= 20)) {
        const top = fb.crowd.top;
        tail.append(h('p', { class: 'v-line v-crowd' }, `Everyone: ${pct(fb.crowd.first_rate)}% right on the first try`,
          top && top.label ? ` · most common mistake: ${low1(top.label)}${top.share !== undefined ? ` (${pct(top.share)}% of misses)` : ''}` : ''));
      } else if (fb.crowd && fb.crowd.text) tail.append(h('p', { class: 'v-line v-crowd', text: fb.crowd.text }));
      if (tail.children.length) v.append(tail);
      if (fb.twice && o.onLadder) {
        v.append(h('p', { class: 'v-line v-ladder' }, h('button', { type: 'button', class: 'btn sm', onclick: () => o.onLadder() },
          icon('book', 16), 'Missed this type twice. Learn it step by step'), h('span', { class: 'meta', text: ' 3 questions · ~4 min' })));
      }
      if (fb.unmarked) {
        const cb = h('input', { type: 'checkbox', id: uid('km') });
        cb.addEventListener('change', () => { if (o.onKeepMarked) o.onKeepMarked(cb.checked); });
        v.append(h('p', { class: 'v-line v-unmark' }, 'Removed from Marked · ', h('label', { class: 'check-inline' }, cb, ' Keep marked')));
      }
      if (fb.rule_prompt && o.onRule) v.append(rulePrompt(fb.rule_prompt));
      if (mode === 'quiz' && fb.needs) {
        const clue = (fb.spans || []).find(s => s.kind === 'clue');
        v.append(h('p', { class: 'v-line v-clue' }, h('b', { text: 'Clue: ' }), clue ? `“${(q.stem || '').slice(clue.start, clue.end)}” → ` : '', `the blank needs “${fb.needs}”`));
      }
      if (mode === 'quiz' && fb.relation) v.append(h('p', { class: 'v-line v-clue' }, h('b', { text: 'How the ideas relate: ' }), fb.relation));

      // 5. the explanation
      const x = explanation(fb, right, ro);
      if (x) v.append(...x);

      // 6. the action row
      if (o.actions) {
        const slot = h('div', { class: 'ws-actions' });
        v.append(slot);
        if (typeof o.actions === 'function') o.actions(slot, fb);
        else questionActions(slot, q, Object.assign({ surface: mode === 'inline' ? 'inline' : mode === 'review' ? 'player' : 'runner' }, o.actions, { fb, missed: !right, revealed: true }));
      }
    }

    function vHead(fb, right, blank) {
      let word;
      const tries = fb.try ?? (S.tries.length + 1);
      const hints = fb.hints ?? S.hints;
      if (mode === 'example') {
        const k = keyIndex(fb);
        return h('p', { class: 'v-head ok' }, h('span', { class: 'v-glyph', 'aria-hidden': 'true' }, markIcon('check', 16)),
          h('b', { text: 'Worked example' }), h('span', { class: 'v-bit', text: ` · the answer is ${k !== null && mc ? LETTERS[k] : minus(fb.answer)}` }));
      }
      if (blank && !right) word = fb.shown ? 'Answer shown' : 'Not answered';
      else if (right && tries > 1) word = `Right on try ${tries}${hints ? ` after ${hints} hint${hints === 1 ? '' : 's'}` : ''} · counts as Mixed`;
      else if (right) word = hints ? `Correct with ${hints} hint${hints === 1 ? '' : 's'} · counts half` : 'Correct';
      else word = 'Incorrect';
      const bits = [];
      const ms = fb.ms ?? (live ? elapsed() : null);
      if (ms && !blank) bits.push(mmss(ms));
      if (fb.budget_ms) bits.push(fb.fluency === 'fluent' ? `fluent (budget ${mmss(fb.budget_ms)})` : `budget ${mmss(fb.budget_ms)}`);
      else if (fb.avg_ms) bits.push(`your average on this type ${mmss(fb.avg_ms)}`);
      if (right && fb.conf === 'guess') bits.push('a guess counts half');
      const best = fb.best ? h('span', { class: 'badge soft v-best' }, icon('trophy', 14), 'New best on this type') : null;
      return h('p', { class: 'v-head ' + (right ? 'ok' : blank ? 'blank' : 'no') },
        h('span', { class: 'v-glyph', 'aria-hidden': 'true' }, right ? markIcon('check', 16) : blank ? '–' : markIcon('x', 14)),
        h('b', { text: word }), bits.map(b => h('span', { class: 'v-bit', text: ` · ${b}` })), best);
    }
    // mastery moves: on a fresh verdict the bar slides from where it was to where it is (runner.css times it) and
    // the word changes as it lands (Developing to Proficient); a revisit draws it where it is
    let freshNow = false;
    function masteryLine(m) {
      const t = UI.TOPIC && UI.TOPIC[m.topic];
      const i = h('i');
      const was = UI.masteryWord(m.before, 1), now = UI.masteryWord(m.after, 1);
      const moving = freshNow && live && !(UI.motion && UI.motion.off && UI.motion.off());
      i.style.setProperty('--m', ((moving ? m.before : m.after) || 0).toFixed(3));
      const word = h('span', { class: 'v-mword', text: moving ? was : now });
      const line = h('p', { class: 'v-mastery' }, UI.glyph ? UI.glyph(m.topic) : '', h('span', { text: t ? t.short : UI.topicName ? UI.topicName(m.topic) : m.topic }), ' · ', word,
        h('span', { class: 'mbar', 'aria-hidden': 'true' }, i));
      if (moving) {
        requestAnimationFrame(() => requestAnimationFrame(() => i.style.setProperty('--m', (m.after || 0).toFixed(3))));
        if (was !== now) setTimeout(() => { word.textContent = now; if (UI.motion) UI.motion.enter(word, 'nudge', { force: true }); }, 700);
      }
      return line;
    }
    function answerBoxes(fb, key, g, blank) {
      const opt = i => h('span', {}, h('b', { text: LETTERS[i] }), ' · ', q.text ? h('span', { text: choices[i] }) : tex(h('span'), choices[i], (q.latex || [])[i]));
      return h('div', { class: 'abox-pair' },
        h('div', { class: 'abox mine' + (fb.correct ? ' ok' : blank ? ' blank' : ' no') }, h('span', { class: 'k', text: 'Your answer' }),
          h('span', { class: 'abox-v' }, blank ? 'Not answered' : opt(g))),
        key !== null && (fb.correct !== true) ? h('div', { class: 'abox ok' }, h('span', { class: 'k', text: 'Correct answer' }), h('span', { class: 'abox-v' }, opt(key))) : null);
    }
    function gridLines(fb, right, blank) {
      const out = [];
      const acc = (fb.accepted || []).filter(f => spr.clean(f) !== spr.clean(fb.given));
      if (right) {
        if (acc.length) out.push(h('p', { class: 'v-line', text: `Also accepted: ${acc.map(minus).join(' · ')}` }));
      } else if (mode === 'example') {
        const also = (fb.accepted || []).filter(f => spr.clean(f) !== spr.clean(fb.answer));
        out.push(h('p', { class: 'grid-key' }, 'Answer: ', h('b', { text: minus(fb.answer) }), also.length ? ` (also ${also.map(minus).join(', ')})` : ''));
      } else {
        const also = (fb.accepted || []).filter(f => spr.clean(f) !== spr.clean(fb.answer));
        if (mode === 'review') {
          out.push(h('div', { class: 'abox-pair' },
            h('div', { class: 'abox mine' + (blank ? ' blank' : ' no') }, h('span', { class: 'k', text: 'Your answer' }), h('span', { class: 'abox-v', text: blank ? 'Not answered' : minus(fb.given) })),
            h('div', { class: 'abox ok' }, h('span', { class: 'k', text: 'Correct answer' }), h('span', { class: 'abox-v', text: minus(fb.answer) }))));
          if (fb.diagnosis && fb.diagnosis.text && !blank) out.push(h('p', { class: 'v-line v-diag', text: fb.diagnosis.text }));   // SR10
          if (also.length) out.push(h('p', { class: 'v-line', text: `Also accepted: ${also.map(minus).join(' · ')}` }));
        } else {
          out.push(h('p', { class: 'grid-key' }, 'Correct answer: ', h('b', { text: minus(fb.answer) }), also.length ? ` (also ${also.map(minus).join(', ')})` : ''));
        }
        if (!blank) {
          if (fb.mistake) out.push(h('p', { class: 'mistake' }, `Your answer ${minus(fb.given)} is what you get if you ${low1(fb.mistake)}`));
          else if (fb.entry && fb.entry.text) out.push(h('p', { class: 'mistake', text: fb.entry.text }));
          else if (!fb.diagnosis && (fb.reasons !== undefined || fb.named === false)) out.push(h('p', { class: 'v-line v-soft', text: 'No named mistake for this value.' }));
        }
      }
      return out;
    }
    // P6: the traps this question set, and how the strikes were graded
    function trapsLines(fb, key, g, right) {
      const out = [];
      const struck = fb.struck || [...S.struck];
      struck.forEach(i => {
        if (i === key) out.push(h('p', { class: 'v-line v-struck-key', text: `You struck the key (${LETTERS[i]})` }));
        else if (fb.reasons[i]) out.push(h('p', { class: 'v-line v-struck', text: `struck ${LETTERS[i]}: ${low1(fb.reasons[i])}` }));
      });
      return out;
    }
    // P8, R47: why you missed, pre-selected, corrected in one tap
    function causeChips(cause) {
      const list = [['trap', 'Fell for a trap'], ['slip', 'Slip: I knew it'], ['misread', 'Misread the question'], ['clock', 'Ran out of time'],
        ['entry', 'Entered it wrong'], ['gap', 'Didn’t know how to start']].filter(([k]) => k !== 'entry' || !mc);
      const box = h('div', { class: 'v-cause' }, h('p', { class: 'k', text: 'What happened?' }));
      if (UI.chips) {
        UI.chips(box, list.map(([value, label]) => ({ value, label })), { value: cause.kind, label: 'What happened?', onChange: k => o.onCause(k) });
      }
      if (cause.why) box.append(h('p', { class: 'help', text: cause.why }));
      return box;
    }
    function habitChip(hb) {
      const b = h('button', { type: 'button', class: 'chip v-habit', 'aria-haspopup': 'dialog' }, h('span', { text: `Habit: ${low1(hb.name)}` }));
      b.addEventListener('click', () => {
        if (!UI.pop) return;
        UI.pop(b, h('div', { class: 'habit-pop' }, h('p', { class: 'k', text: 'Habit' }), h('p', { text: cap1(hb.name) }),
          hb.tell ? h('p', { class: 'help', text: hb.tell }) : null, hb.href ? h('a', { class: 'quiet', href: hb.href, text: 'See the habit' }) : null), { label: 'Habit' });
      });
      return h('p', { class: 'v-line' }, b);
    }
    function formulaLine(f) {
      const p = h('p', { class: 'v-line v-formula' });
      const tx = texText(h('span', { class: 'v-f' }), f.tex ? `$${f.tex}$` : f.text);
      if (f.on_sheet !== false) {
        p.append('Used: ', tx, ' · on the reference sheet · ');
        p.append(h('button', { type: 'button', class: 'qlink', text: 'Open it (F)', 'aria-label': 'Open the reference sheet at this formula',
          onclick: () => (UI.ref && UI.ref.open ? UI.ref.open({ id: f.id, highlight: f.id }) : null) }));
      } else p.append('Not on the sheet: ', tx, ' · learn it');
      return p;
    }
    function rulePrompt(text) {
      const box = h('div', { class: 'v-rule' });
      const fid = uid('rule');
      const inp = h('input', { id: fid, class: 'field sm', type: 'text', maxlength: '140', placeholder: 'Same slope + same intercept = infinitely many' });
      const save = h('button', { type: 'button', class: 'btn sm', text: 'Save rule' });
      save.addEventListener('click', async () => {
        const t = inp.value.trim();
        if (!t) return inp.focus();
        save.setAttribute('aria-busy', 'true');
        try { await o.onRule('save', t); box.replaceChildren(h('p', { class: 'v-line', text: `Saved: it shows on every ${q.name || 'question of this type'}` })); }
        catch (_) { save.removeAttribute('aria-busy'); toast('Not saved. Try again.'); }
      });
      inp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); save.click(); } });
      box.append(h('label', { class: 'label', for: fid, text }), h('div', { class: 'v-rule-row' }, inp, save));
      if (UI.counter) box.append(UI.counter(inp, 140));
      return box;
    }

    // P1 and P3: the explanation card, Steps (or Method) · Short · Desmos way
    let stepRows = [];
    function explanation(fb, right, ro) {
      const steps = fb.steps && fb.steps.length ? fb.steps : null;
      const method = !steps && fb.method ? fb.method : null;
      const short = fb.rationale;
      const dz = fb.desmos && fb.desmos.exprs ? fb.desmos : null;
      if (!steps && !method && !short && !dz && !(fb.typed && fb.typed.length)) return null;
      const card = h('section', { class: 'x-card', 'aria-label': 'Explanation' });
      const name = fb.type_name || q.name, about = fb.about || q.about;
      if (name || about) card.append(h('div', { class: 'x-head' }, h('p', { class: 'x-type' }, name ? h('b', { text: name }) : null, name && about ? ' · ' : '', about || '')));
      const panels = [];
      if (steps) panels.push({ id: 'steps', label: 'Steps', panel: stepsPanel(fb, steps, right) });
      else if (method) panels.push({ id: 'method', label: 'Method', panel: h('div', { class: 'x-panel' }, texText(h('p', { class: 'why' }), method)) });
      if (short) panels.push({ id: 'short', label: 'Short', panel: h('div', { class: 'x-panel' }, texText(h('p', { class: 'why' }), short)) });
      if (dz) panels.push({ id: 'desmos', label: 'Desmos way', panel: desmosPanel(dz) });
      if (panels.length > 1 && UI.tabs) {
        const holder = h('div', { class: 'x-tabs' });
        card.append(holder);
        panels.forEach(p => card.append(p.panel));
        card._tabs = UI.tabs(holder, panels.map(p => ({ id: p.id, label: p.label, panel: p.panel })), { label: 'Explanation views' });
      } else panels.forEach(p => card.append(p.panel));
      if (fb.typed && fb.typed.length) {
        card.append(h('div', { class: 'x-typed' }, h('p', { class: 'k', text: 'What you typed in Desmos' }),
          h('ol', {}, fb.typed.map(t => h('li', {}, tex(h('span'), t, t))))));
      }
      const open = ro.open || mode === 'review' || mode === 'example' || mode === 'quiz' || prefs.open_explanations || prefs.rationale === 'always'
        || fb.conf === 'guess' || fb.sure_miss || (!right && prefs.rationale !== 'tap');
      // one control, the shared fold's own look (details.fold, .fold-s): open where the card must show, else closed
      // unless an Explanation was left open before (satf.fold 'explanation', the id ui.js's fold remembers it by)
      const d = h('details', { class: 'fold x-fold' }, h('summary', { class: 'fold-s', text: 'Explanation' }), card);
      let was = d.open = !!open || foldKept();
      d.addEventListener('toggle', () => { if (d.open !== was) { was = d.open; foldKeep(was); } });   // the student's taps, not the first open
      return [d];
    }
    const foldList = () => { const a = ls.get('satf.fold', []); return Array.isArray(a) ? a : []; };
    const foldKept = () => foldList().includes('explanation');
    function foldKeep(on) {
      const a = foldList().filter(x => x !== 'explanation');
      if (on) a.push('explanation');
      ls.set('satf.fold', a.slice(-300));
    }
    function stepsPanel(fb, steps, right) {
      const box = h('div', { class: 'x-panel' });
      const ol = h('ol', { class: 'steps' });
      const div = !right && Number.isInteger(fb.diverge) ? fb.diverge : null;
      const g = givenIndex(fb.given);
      stepRows = steps.map((s, i) => {
        const text = typeof s === 'string' ? s : s.text;
        const li = h('li', { class: 'step', tabindex: i === 0 ? '0' : '-1' });
        const body = texText(h('span', { class: 'step-t' }), text);
        li.append(h('span', { class: 'step-n', text: String(i + 1), 'aria-hidden': 'true' }), body);
        if (div !== null && i < div) li.append(h('span', { class: 'step-had', text: '✓ you likely had this' }));
        if (div !== null && i === div) {
          li.classList.add('diverge');
          li.append(h('div', { class: 'step-cmp' },
            h('div', {}, h('b', { text: 'Right: ' }), texText(h('span'), text)),
            h('div', {}, h('b', { text: `Your ${g !== null && mc ? LETTERS[g] : 'answer'}: ` }), texText(h('span'), fb.wrong_step || ''),
              mc && g !== null && fb.reasons && fb.reasons[g] ? h('span', { class: 'step-why', text: ` · ${low1(fb.reasons[g])}` }) : fb.mistake ? h('span', { class: 'step-why', text: ` · ${low1(fb.mistake)}` }) : null)));
        }
        ol.append(li);
        return li;
      });
      ol.addEventListener('keydown', e => {                    // roving: arrows move while the list has focus
        const d = { ArrowDown: 1, ArrowUp: -1 }[e.key];
        const at = stepRows.indexOf(doc.activeElement);
        if (!d || at < 0) return;
        e.preventDefault();
        e.stopPropagation();
        const nx = stepRows[Math.max(0, Math.min(stepRows.length - 1, at + d))];
        stepRows.forEach(r => { r.tabIndex = r === nx ? 0 : -1; });
        nx.focus();
      });
      box.append(ol);
      return box;
    }
    function outlineStep(i) {
      const card = verdictEl.querySelector('.x-card');
      if (!card) return;
      const d = card.closest('details');
      if (d) d.open = true;
      if (card._tabs) card._tabs.set('steps');
      stepRows.forEach(r => r.classList.remove('see'));
      const r = stepRows[i];
      if (!r) return;
      r.classList.add('see');
      r.scrollIntoView({ block: 'nearest', behavior: still() ? 'auto' : 'smooth' });
    }
    function desmosPanel(dz) {
      const box = h('div', { class: 'x-panel x-desmos' });
      box.append(h('ol', { class: 'x-exprs' }, dz.exprs.map(x => h('li', {}, tex(h('span'), x.latex, x.latex), x.label ? h('span', { class: 'meta', text: ` ${x.label}` }) : null))));
      if (dz.note) box.append(h('p', { class: 'help', text: dz.note }));
      box.append(h('button', { type: 'button', class: 'btn sm', title: 'Shift+G', onclick: () => calc.walkthrough(dz) }, icon('graph', 16), 'Show me in Desmos'));
      return box;
    }

    /* ---------------- tools (R50): one list for the strip, the phone tools row and inline pages */
    function tools() {
      const t = [];
      if (mc && strikeAllowed()) t.push({ id: 'eliminate', label: 'Eliminate', icon: 'eliminate', key: 'E', pressed: S.eliminate, run: () => eliminate(!S.eliminate) });
      if (coverAllowed()) t.push({ id: 'cover', label: S.covered ? 'Show choices' : 'Cover choices', icon: 'cover', pressed: S.covered, run: () => cover(!S.covered) });
      // Hint is not here: its "Hint · 1 of 3" button sits under the choices on every screen size (P2)
      if (canSpeak() && (o.readAloud ?? mode !== 'exam')) t.push({ id: 'read', label: speaking ? 'Stop' : 'Read aloud', icon: speaking ? 'stop' : 'speak', pressed: !!speaking,
        run: () => { readAloud(q, () => paint()); paint(); } });
      if (o.calc !== false) t.push({ id: 'calc', label: 'Calculator', icon: 'calc', key: 'G', pressed: calc.isOpen, run: () => calc.toggle() });
      if (o.ref !== false && UI.ref) t.push({ id: 'ref', label: 'Reference', icon: 'ref', key: 'F', run: () => UI.ref.open() });
      if (S.fb && S.fb.desmos && S.fb.desmos.exprs) t.push({ id: 'desmos', label: 'Desmos way', icon: 'graph', key: 'Shift+G', run: () => calc.walkthrough(S.fb.desmos) });
      return t;
    }
    function renderTools(where) {
      where.replaceChildren(...tools().map(t => {
        const b = h('button', { type: 'button', class: 'tool', 'data-tool': t.id, 'aria-pressed': t.pressed === undefined ? null : String(!!t.pressed),
          title: t.key ? `${t.label} (${t.key})` : t.label }, icon(t.icon, 20), h('span', { text: t.label }));
        b.addEventListener('click', () => { t.run(); if (where.isConnected) renderTools(where); });
        return b;
      }));
      where.hidden = !where.children.length;
    }
    const onCalc = () => { if (toolsEl) renderTools(toolsEl); };
    cleanups.push(calc.onOpen(onCalc));

    /* ---------------- keys: the runner and the players call this; inline pages get it on focus */
    function key(e) {
      if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return false;
      const t = e.target;
      if (t && t.closest && t.closest('input, textarea, select, [contenteditable="true"], .calc')) return false;
      const k = e.key;
      if (S.stage === 'on') {
        const i = '123456'.indexOf(k);
        if (k.length === 1 && i >= 0 && o.stage.options && i < o.stage.options.length) { stageDone(i); return true; }
        if (k === 'Enter') { stageDone(null); return true; }
        return false;
      }
      if (mc && k.length === 1) {
        const up = k.toUpperCase();
        let i = LETTERS.slice(0, n).indexOf(up);
        const letter = i >= 0;
        if (!letter) i = '12345'.slice(0, n).indexOf(k);
        if (i >= 0) {
          if (e.shiftKey && letter) return strike(i) || true;
          if (e.shiftKey) return false;
          if (mode === 'review' && S.hidden) { localPick(i); return true; }
          if (!canChoose()) return false;
          if (S.selected !== i) { lastPointer = 'keyboard'; tap(i); }
          // focus follows the key, so a later Enter checks this choice and not the one focus was on
          if (list.contains(doc.activeElement) && rows[i] && !S.answered) rows[i].b.focus({ preventScroll: true });
          return true;
        }
      }
      if (k === 'Enter') {
        if (S.fastAsk) { check(S.lastConf); return true; }
        if (!canCheck()) return false;
        check(e.shiftKey ? 'unsure' : 'auto');
        return true;
      }
      if (e.shiftKey) return false;
      const lk = k.toLowerCase();
      if (lk === 'i' && live && prefs.confidence !== 'off' && canCheck() && !S.tries.length) { check('guess'); return true; }
      if (lk === 'e' && strikeAllowed()) { eliminate(!S.eliminate); return true; }
      if (lk === 'w' && hintAllowed()) { hint(); return true; }
      if (lk === 's' && o.onSkip && live && !S.answered) { skip(); return true; }
      return false;
    }
    if (mode === 'inline' || mode === 'quiz' || o.ownKeys) {
      el.addEventListener('keydown', e => { if (key(e)) e.preventDefault(); });
    }

    /* ---------------- restore */
    if (o.fb && (mode === 'review' || mode === 'example' || o.fb.correct !== undefined)) {
      const hidden = S.hidden;
      reveal(o.fb, { open: mode !== 'review' ? true : undefined });
      if (hidden) setHidden(true);
    } else {
      if (!mc && S.value) onValue();
      paint();
    }

    function changed() { if (o.onChange) o.onChange(state()); }
    function state() {
      return { selected: S.selected, value: S.value, struck: [...S.struck], hint_struck: [...S.hintStruck], eliminate: S.eliminate,
        tries: S.tries.slice(), hints: S.hints, covered: S.covered, own: S.own, saved: S.saved, answered: S.answered, busy: S.busy,
        canCheck: canCheck(), stage_done: S.stage === 'done', ms: elapsed() };
    }

    const ws = {
      el, q, key, check, select, strike, eliminate, cover, hint, skip, tools, renderTools, setHidden, state, value, canCheck,
      // a page that reveals for itself (the verdict came back) gets the same landing as a Check here
      reveal: (fb, ro) => reveal(fb, Object.assign({ fresh: true }, ro)),
      passageNodes: [figEl, tableEl, passEl].filter(Boolean),
      choose(i) { if (select(i) && live && !endMode) check('auto'); },
      unlock() { S.busy = false; S.pending = false; paint(); },
      answered: () => S.answered,
      get feedback() { return S.fb; },
      get hidden() { return S.hidden; },
      set annotating(v) { o.annotating = typeof v === 'function' ? v : () => !!v; },
      elapsed,
      // a pre-rendered question (G9) starts its clock when it is shown, not when it was built
      restart() { S.shownAt = performance.now(); S.awayMs = 0; S.awayAt = doc.hidden ? performance.now() : null; },
      focus() {
        const target = mc ? (rows.find(r => r.b.tabIndex === 0) || rows[0] || {}).b : field;
        if (target) target.focus({ preventScroll: true });
      },
      destroy() {
        cleanups.splice(0).forEach(f => { try { f(); } catch (_) {} });
        if (speaking) readAloud(q);
        el.remove();
      },
      // the old UI.question fields, for pages not rebuilt yet
      get buttons() { return rows.map(r => r.b); }, get list() { return list; }, get input() { return field; }, get wrap() { return fieldWrap; }, get preview() { return previewEl; },
    };
    if (host) { if (o.append) host.append(el); else host.replaceChildren(el); }
    return ws;
  }

  // the old one-tap renderer: onAnswer(given), then the page calls reveal(fb)
  function question(host, q, o = {}) {
    return workspace(host, q, {
      mode: 'practice', feedback: 'instant', firstTap: true, bar: q.type === 'spr', again: o.again, prefs: { confidence: 'off' },
      onCheck: o.onAnswer ? a => { o.onAnswer(a); return undefined; } : null,
    });
  }

  /* ------------------------------------------------------------ the split Check (P7, R54) */
  function splitCheck(host, o = {}) {
    const el = h('div', { class: 'split-check', role: 'group', 'aria-label': 'Check your answer' });
    const main = h('button', { type: 'button', class: 'pill sc-main', 'data-conf': 'auto', disabled: true }, h('span', { class: 'sc-l' }), h('kbd', { class: 'kbd', text: 'Enter' }));
    // D: the rating is the button, three of one shape
    // the key is in each tooltip too: the runner shows the chips only on hover, focus and a learner's first sets
    const sure = h('button', { type: 'button', class: 'pill sc-part', 'data-conf': 'sure', title: 'Sure (Enter)' }, 'Sure', h('kbd', { class: 'kbd', text: 'Enter' }));
    const unsure = h('button', { type: 'button', class: 'btn sc-part', 'data-conf': 'unsure', title: 'Not sure (Shift+Enter)' }, 'Not sure', h('kbd', { class: 'kbd', text: '⇧Enter' }));
    const guess = h('button', { type: 'button', class: 'btn sc-part', 'data-conf': 'guess', title: 'Guessing (I)' }, 'Guessing', h('kbd', { class: 'kbd', text: 'I' }));
    el.append(main, sure, unsure, guess);
    let enabled = false;
    [main, sure, unsure, guess].forEach(b => b.addEventListener('click', () => { if (enabled && o.onSubmit) o.onSubmit(b.dataset.conf); }));
    function set(p = {}) {
      Object.assign(o, p);
      if ('enabled' in p) enabled = !!p.enabled;
      const split = o.confidence !== 'off' && o.firstTry !== false;
      [sure, unsure, guess].forEach(b => { b.hidden = !split; b.disabled = !enabled; });
      main.hidden = split;
      main.disabled = !enabled;
      main.querySelector('.sc-l').textContent = o.save ? 'Save & next' : 'Check';
      main.title = `${o.save ? 'Save & next' : 'Check'} (Enter)`;
      el.classList.toggle('split', split);
    }
    set({});
    if (host) host.append(el);
    return { el, set, get enabled() { return enabled; } };
  }

  /* ------------------------------------------------------------ the answer pad (X6) */
  function pad(field, o = {}) {
    const el = h('div', { class: 'pad', role: 'group', 'aria-label': 'Answer pad' });
    const names = { '⌫': 'Delete', '−': 'Minus sign', '/': 'Fraction bar', '.': 'Decimal point' };
    ['7', '8', '9', '⌫', '4', '5', '6', '/', '1', '2', '3', '.', '−', '0', 'Clear'].forEach(k =>
      el.append(h('button', { type: 'button', class: 'pad-k' + (k === 'Clear' ? ' wide' : ''), 'data-k': k, 'aria-label': names[k] || k, text: k })));
    el.addEventListener('pointerdown', e => { if (e.target.closest('.pad-k')) e.preventDefault(); });   // the field keeps focus
    el.addEventListener('click', e => {
      const b = e.target.closest('.pad-k');
      if (!b || field.readOnly || field.disabled) return;
      const k = b.dataset.k;
      let v = spr.clean(field.value);
      if (k === '⌫') v = v.slice(0, -1);
      else if (k === 'Clear') v = '';
      else if (k === '−') v = v.startsWith('-') ? v.slice(1) : '-' + v;
      else v += k;
      field.value = v;
      field.dispatchEvent(new Event('input', { bubbles: true }));
      if (o.onKey) o.onKey(k);
    });
    field.setAttribute('inputmode', 'none');
    return el;
  }

  /* ------------------------------------------------------------ one action row (G4, R49) */
  function questionActions(host, q, ctx = {}) {
    const row = h('div', { class: 'q-actions', role: 'group', 'aria-label': 'Question actions' });
    const on = ctx.on || {};
    const acts = {};
    const put = (id, el, run) => { acts[id] = run || (() => el.click()); row.append(el); };
    const btn = (label, ic, keyName, onClick, o = {}) => {
      const b = h(o.href ? 'a' : 'button', { type: o.href ? null : 'button', href: o.href || null, class: 'btn sm qa-' + keyName.id,
        title: keyName.key ? `${label} (${keyName.key})` : label, 'aria-keyshortcuts': keyName.key || null, 'aria-pressed': o.pressed === undefined ? null : String(!!o.pressed) },
        icon(ic, 16), h('span', { class: 'qa-l', text: label }));
      if (onClick) b.addEventListener('click', onClick);
      return b;
    };
    const K = UI.KEYS || {};
    const toggle = (id, off, onLabel, ic, key, state, fn) => {
      let v = !!state;
      const b = btn(v ? onLabel : off, ic, { id, key }, null, { pressed: v });
      b.addEventListener('click', async () => {
        v = !v;
        b.setAttribute('aria-pressed', String(v));
        b.querySelector('.qa-l').textContent = v ? onLabel : off;
        try { await fn(v); }
        catch (_) { v = !v; b.setAttribute('aria-pressed', String(v)); b.querySelector('.qa-l').textContent = v ? onLabel : off; toast('Not saved. Try again.'); }
      });
      return b;
    };
    const fb = ctx.fb || {};
    if (ctx.challengeOpen) { if (host) host.append(row); return { el: row, run: () => false, has: () => false }; }   // R19
    const liveNow = !!ctx.live;
    if (!liveNow && (on.twin || ctx.more || ctx.body || q.template || ctx.trap_id)) {
      // the verdict region's primary after a miss; a .btn after a right answer, and always in the practice runner,
      // whose footer Next is the screen's one orange
      const tw = twin(null, Object.assign({ primary: !!ctx.missed && ctx.surface !== 'runner', template: q.template, question_id: q.id, q }, ctx));
      row.append(tw.el);
      acts.twin = () => tw.run('same');
      acts.twin_menu = () => tw.menu();
    }
    const dz = ctx.desmos || fb.desmos;
    if (!liveNow && dz && dz.exprs) put('desmos', btn('Desmos way', 'graph', { id: 'desmos', key: K.desmos || 'Shift+G' }, () => calc.walkthrough(dz)));
    // compact (the practice runner): its question strip already has Mark, Note, History and Report, one of each
    if (!ctx.compact) {
      // V3: a save asks why, in one optional 5 s toast (the player's top-bar Save does the same)
      const saveThen = async v => { const r = await on.save(v); if (v) savedToast(q, { text: 'Saved to Review', revealed: ctx.revealed !== false, onNote: on.note || null, onAsk: on.help || null, onWhy: on.savedWhy || null, onLucky: on.lucky || null }); return r; };
      if (!liveNow && on.save) put('save', toggle('save', 'Save', 'Saved', 'bookmark', K.save || 'B', ctx.saved, saveThen));
      if (on.mark && (ctx.session || ctx.inSitting)) put('mark', toggle('mark', 'Mark', 'Marked', 'flag', K.mark || 'M', ctx.marked, on.mark));
      if (on.note) put('note', btn(ctx.rule ? 'My rule' : ctx.hasNote ? 'My note' : 'Note', 'note', { id: 'note', key: K.note || 'O' }, () => on.note()));
      if (!liveNow) {
        const hist = on.history || (UI.history && (q.template || ctx.session) ? () => UI.history(q.template ? { template: q.template } : { session: ctx.session, question_id: q.id }) : null);
        if (hist) put('history', btn('History', 'history', { id: 'history', key: K.history || 'Y' }, () => hist()));
        if (on.again && ctx.surface !== 'runner' && ctx.surface !== 'inline') {
          const b = UI.verb ? UI.verb('again', { sm: true, onClick: () => on.again() }) : btn('Again, exactly', 'history', { id: 'again', key: 'E' }, () => on.again());
          put('again', b);
        }
        // "About this type" pointed at /types/, a page that does not exist (404), so it is gone until that page is built
      }
      const report = () => {
        const f = on.report || UI.report;
        if (!f) return null;
        return f(on.report ? undefined : Object.assign({ kind: 'question', source: ctx.source, session: ctx.session, question_id: q.id,
          revealed: !!ctx.revealed, live: liveNow, template: q.template, seed: q.seed }, ctx.report || {}));
      };
      put('report', btn('Report', 'report', { id: 'report', key: K.report || 'R' }, report), report);
    }
    if (host) host.append(row);
    return { el: row, run: id => (acts[id] ? (acts[id](), true) : false), has: id => !!acts[id] };
  }

  /* ------------------------------------------------------------ the twin control (R44, P18, G3) */
  const AXIS = {
    same: 'Twin', easier: 'Easier', harder: 'Harder', grid: 'As a grid-in, no choices to lean on',
    ask: 'Same setup, a different question', related: 'Same trap, other types',
  };
  function twin(host, ctx = {}) {
    const wrapEl = h('span', { class: 'split split-btn twin' + (ctx.primary ? ' primary' : '') });
    const main = UI.verb
      ? UI.verb('twin', { primary: !!ctx.primary, sm: true, subject: written() ? 'rw' : ctx.subject, onClick: () => run('same') })
      : h('button', { type: 'button', class: ctx.primary ? 'pill sm' : 'btn sm', onclick: () => run('same') }, icon('twin', 16), 'Twin');
    main.setAttribute('aria-keyshortcuts', 'T');
    const caret = h('button', { type: 'button', class: (ctx.primary ? 'pill sm' : 'btn sm') + ' split-caret', 'aria-label': 'More ways to twin', 'aria-haspopup': 'menu', 'aria-expanded': 'false', title: 'Shift+T' }, icon('caret_down', 16));
    caret.addEventListener('click', () => menu());
    wrapEl.append(main, caret);
    function items() {
      // a written (R&W) item has no new-numbers version, grid-in form or second ask on its setup
      const rw = written();
      const ax = new Set((ctx.axes || []).filter(a => !rw || (a !== 'grid' && a !== 'ask')));
      const sib = ctx.siblings || {};
      const list = [{ label: 'Twin', sub: rw ? 'same kind, another passage' : 'same kind, new numbers', kbd: 'T', onClick: () => run('same') }];
      // SR16, V11: on a trap or gap miss, a worked example first (never filed), then Your turn
      if (ctx.onSolved) list.push({ label: 'See one solved first', sub: rw ? 'one worked, then your turn' : 'your mistake marked on new numbers', onClick: () => ctx.onSolved() });
      if (ax.has('easier')) list.push({ label: sib.easier ? `Easier: ${sib.easier}` : 'Easier', onClick: () => run('easier') });
      if (ax.has('harder')) list.push({ label: sib.harder ? `Harder: ${sib.harder}` : 'Harder', onClick: () => run('harder') });
      if (ax.has('grid')) list.push({ label: AXIS.grid, onClick: () => run('grid') });
      if (ax.has('ask')) list.push({ label: AXIS.ask, sub: ctx.ask_hint || null, onClick: () => run('ask') });
      if (ctx.related_n) list.push({ label: `${AXIS.related} · ${ctx.related_n}`, onClick: () => run('related') });
      list.push({ separator: true }, { label: 'Twin ×5', onClick: () => run('same', 5) });
      if (ctx.template && ctx.learn !== false) list.push({ label: 'Learn this type', sub: 'one solved, then three', onClick: () => run('learn') });
      if (ctx.template && ctx.print !== false) list.push({ label: 'Print 10 with key', onClick: () => run('print') });
      return list;
    }
    function written() { return ctx.subject ? ctx.subject === 'rw' : !!(ctx.q && ctx.q.text) || UI.subjectOf(ctx.template) === 'rw'; }
    function menu() { return UI.menu ? UI.menu(caret, items(), { label: 'Twin' }) : null; }
    async function run(axis, n = 1) {
      try {
        if (ctx.more) return await ctx.more(axis, n);                       // inside a running set: POST /more {axis}
        const t = ctx.template;
        if (axis === 'learn') return ctx.onLearn ? ctx.onLearn() : start({ source: 'learn', templates: [t], example: true, count: 3 });
        if (axis === 'print') return start({ source: 'worksheet', templates: [t], count: 10 }, '&print=1');
        const body = Object.assign({}, ctx.body || (ctx.trap_id ? { pool: 'redo', ids: [ctx.trap_id], source: 'try' } : { templates: [t], source: 'twin' }), { count: n });
        if (axis !== 'same') body.axis = axis;
        const to = { body, recall: ctx.recall, title: n > 1 ? `Twin ×${n}` : 'Twin', onDone: ctx.onDone, count: n, axis };
        // R23: the players answer the twin in their own column (R24's inline drill), not in a sheet
        if (ctx.inline) return ctx.inline(to);
        return twinSheet(to);
      } catch (e) {
        toast((e && e.message) || 'That didn’t start. Try again.');
        return null;
      }
    }
    async function start(body, suffix = '') {
      const s = await api('/drill', { method: 'POST', body });
      location.href = `/practice/session/?id=${encodeURIComponent(s.id)}${suffix}`;
    }
    if (host) host.append(wrapEl);
    return { el: wrapEl, run, menu };
  }

  /* ------------------------------------------------------------ a twin, answered in place (T5, R23, R24)
     One inline drill behind the twin sheet, the players' twin tile and the Review pane's
     mini-session: POST /drill {body}; answers through /drill/{id}/answer; Another through
     /more then /next (a fresh one-question drill until /more exists); a miss's queued repair
     through /next ("Try the repair"); /finish once, when something was answered. */
  function twinRun(qhost, msg, foot, o = {}) {
    let sid = null, ws = null, answered = 0, right = null, lastQ = null, lastFb = null, closedDone = false, shown = 0;
    const again = h('button', { type: 'button', class: 'btn twin-again', text: o.againLabel || 'Another twin', hidden: true });
    foot.prepend(again);
    const drillQ = async id => {
      const stt = await api(`/drill/${encodeURIComponent(id)}`);
      return stt.question || (await api(`/drill/${encodeURIComponent(id)}/next`, { method: 'POST' })).question;
    };
    async function load() {
      try {
        const d = await api('/drill', { method: 'POST', body: o.body });
        sid = d.id;
        const q = d.question || await drillQ(sid);
        if (!q) throw new Error('We ran out of questions like this one for now.');
        show(q);
      } catch (e) {
        qhost.replaceChildren(h('p', { class: 'error', text: e && e.status === 409 && o.body && o.body.from_session
          ? 'Finish the test first: its questions stay closed until then.' : (e && e.message) || 'That didn’t load.' }));
        if (o.onError) o.onError(e);
      }
    }
    function show(q) {
      lastQ = q; lastFb = null;
      msg.textContent = '';
      again.hidden = true;
      if (ws) ws.destroy();
      ws = workspace(qhost, q, Object.assign({
        mode: 'inline', feedback: 'instant', prefs: o.prefs, autofocus: true,
        onCheck: (a, m) => api(`/drill/${encodeURIComponent(sid)}/answer`, { method: 'POST', body: { question_id: q.id, answer: a, ms: m.ms, conf: m.conf, hints: m.hints } }),
        onReveal: fb => {
          answered++; lastFb = fb;
          right = !!fb.correct;
          again.textContent = !fb.correct && fb.repair_next ? 'Try the repair' : (o.againLabel || 'Another twin');
          again.hidden = false;
          if (o.onAnswer) o.onAnswer(fb, q, answered);
          (o.focusAfter ? o.focusAfter() : again).focus({ preventScroll: true });
        },
      }, o.wsOpts ? o.wsOpts(q, shown) : {}));
      shown++;
      if (o.onShow) o.onShow(q, ws);
    }
    again.addEventListener('click', async () => {
      again.setAttribute('aria-busy', 'true');
      try {
        let r = null;
        if (lastFb && !lastFb.correct && lastFb.repair_next) {                   // the repair the drill queued (the set grows)
          try { r = await api(`/drill/${encodeURIComponent(sid)}/next`, { method: 'POST' }); } catch (_) { r = null; }
        }
        if (!r || r.done || !r.question) {
          try { await api(`/drill/${encodeURIComponent(sid)}/more`, { method: 'POST', body: { question_id: lastQ.id, axis: o.axis || 'same' } }); r = await api(`/drill/${encodeURIComponent(sid)}/next`, { method: 'POST' }); }
          catch (_) { r = null; }
        }
        if (!r || r.done || !r.question) {                         // no /more yet: a fresh one-question drill
          finish();
          const d = await api('/drill', { method: 'POST', body: Object.assign({}, o.body, { count: 1 }) });
          sid = d.id; closedDone = false;
          r = { question: d.question || await drillQ(sid) };
        }
        show(r.question);
      } catch (e) { toast((e && e.message) || 'That didn’t load. Try again.'); }
      finally { again.removeAttribute('aria-busy'); }
    });
    function finish() {
      if (o.finish === false) return;                            // Review 8: the pane's drills are never finished
      if (sid && answered && !closedDone) { closedDone = true; api(`/drill/${encodeURIComponent(sid)}/finish`, { method: 'POST' }).catch(() => {}); }
    }
    load();
    return { load, finish, again, get sid() { return sid; }, get answered() { return answered; }, get right() { return right; }, get ws() { return ws; } };
  }
  function twinSheet(o = {}) {
    let run = null;
    const qhost = h('div', { class: 'twin-q' });
    const msg = h('p', { class: 'twin-msg', role: 'status' });
    const foot = h('div', { class: 'twin-foot' });
    const done = h('button', { type: 'button', class: 'pill', text: 'Done' });
    foot.append(done);
    const kicker = h('p', { class: 'k twin-k', text: 'Same kind of question' });
    const sheet = UI.sheet({
      title: o.title || 'Twin', size: 'l', className: 'twin-sheet',
      body: b => {
        if (o.recall) b.append(recallBox(o.recall));
        b.append(kicker, qhost, msg, foot);
        UI.skel ? UI.skel(qhost, 'lines:3') : qhost.append(h('p', { class: 'meta', text: 'Loading…' }));
      },
      onClose: () => { if (run) { run.finish(); if (o.onDone) o.onDone({ right: run.right, answered: run.answered, session: run.sid }); } },
    });
    function recallBox(r) {
      const d = h('details', { class: 'twin-recall' }, h('summary', {}, r.text || 'The original question'));
      if (r.q) {
        const inner = h('div', { class: 'twin-recall-q' });
        d.append(inner);
        d.addEventListener('toggle', () => { if (d.open && !inner.children.length) workspace(inner, r.q, { mode: 'review', fb: r.fb, bar: false, head: false }); });
      }
      return d;
    }
    done.addEventListener('click', () => sheet.close());
    // the kicker says what changed once the twin is on screen: a written item is another passage
    run = twinRun(qhost, msg, foot, Object.assign({}, o, { focusAfter: () => done, onShow: (q, w) => {
      kicker.textContent = q && q.text ? 'Same kind of question, another passage' : 'Same kind of question, new numbers';
      if (o.onShow) o.onShow(q, w);
    } }));
    return sheet;
  }
  // the players' tile (Report 1.13) and the pane's mini-session (Review 8): the same run, in a host
  function twinInline(host, o = {}) {
    const el = h('section', { class: 'twin-tile', 'aria-label': o.caption || 'Same question type' });
    const qhost = h('div', { class: 'twin-q' });
    const msg = h('p', { class: 'twin-msg', role: 'status' });
    const foot = h('div', { class: 'twin-foot' });
    const kicker = o.caption !== false ? h('p', { class: 'k twin-k', text: o.caption || 'Same question type' }) : null;
    if (kicker) el.append(kicker);
    el.append(qhost, msg, foot);
    const keep = o.session !== false ? h('a', { class: 'quiet twin-keep', hidden: true, text: 'Keep going in a session' }) : null;
    if (o.onBack) foot.append(h('button', { type: 'button', class: 'quiet twin-back', text: o.backLabel || 'Back to the original', onclick: () => o.onBack() }));
    if (keep) foot.append(keep);
    if (!o.wsOpts && UI.skel) UI.skel(qhost, 'lines:3');
    if (host) { if (o.prepend) host.prepend(el); else host.append(el); }
    let run = null;
    run = twinRun(qhost, msg, foot, Object.assign({ againLabel: 'Another like this' }, o, {
      onShow: (q, w) => {
        if (kicker && !o.caption) kicker.textContent = q && q.text ? 'Same question type, another passage' : 'Same question type, new numbers';
        if (keep && run && run.sid) { keep.href = `/practice/session/?id=${encodeURIComponent(run.sid)}`; keep.hidden = false; }
        if (o.onShow) o.onShow(q, w);
      },
    }));
    return Object.assign(run, { el, destroy() { run.finish(); if (run.ws) run.ws.destroy(); el.remove(); } });
  }

  function exampleSheet(ex) {
    if (!UI.sheet || !ex) return null;
    const exQ = ex.question || ex;
    return UI.sheet({ title: 'A worked twin', size: 'l', className: 'twin-sheet',
      body: b => { b.append(h('p', { class: 'k', text: exQ.text ? 'Solved on another passage' : 'Solved on other numbers' })); const hst = h('div'); b.append(hst);
        workspace(hst, ex.question || ex, { mode: 'example', fb: ex.feedback || ex, bar: false }); } });
  }

  /* ------------------------------------------------------------ the calculator (QBank 2.9, Tests 4.8, P3, X8, item 74) */
  const TRIAL_KEY = 'dcb31709b452b1cf9dc26972add0fda6';
  const calc = (() => {
    let panel = null, titleEl, walkBar, walkNote, hostEl, grip, modeBtn, expandBtn, engine = null, loading = null;
    let mode = 'float', dockHost = null, sid = null, big = false, walking = null, quietUntil = 0, saveTimer = 0, changeTimer = 0, sheetH = 62;
    const subs = new Set(), openSubs = new Set();
    const emitOpen = () => openSubs.forEach(f => { try { f(isOpen()); } catch (_) {} });
    const isOpen = () => !!panel && !panel.hidden && panel.isConnected;   // a closed modal takes a panel mounted in it along

    function build() {
      panel = h('div', { class: 'calc', role: 'dialog', 'aria-label': 'Calculator', hidden: true, tabindex: '-1' });
      titleEl = h('span', { class: 'calc-title', text: 'Desmos' });
      modeBtn = h('button', { type: 'button', class: 'calc-btn' }, icon('dock', 16), h('span', { text: 'Dock' }));
      expandBtn = h('button', { type: 'button', class: 'calc-btn' }, icon('expand', 16), h('span', { text: 'Expand' }));
      const x = h('button', { type: 'button', class: 'x', 'aria-label': 'Close calculator' }, icon('x', 18));
      const bar = h('div', { class: 'calc-bar' }, h('span', { class: 'calc-grab', 'aria-hidden': 'true' }), titleEl, h('span', { class: 'calc-acts' }, modeBtn, expandBtn, x));
      walkNote = h('span', { class: 'calc-walk-note' });
      walkBar = h('div', { class: 'calc-walk', hidden: true }, walkNote, h('button', { type: 'button', class: 'btn sm', text: 'Back to my graph', onclick: () => walkBack() }));
      hostEl = h('div', { class: 'calc-host' }, h('p', { class: 'calc-note', text: 'Loading the calculator…' }));
      grip = h('span', { class: 'calc-grip', 'aria-hidden': 'true' });
      panel.append(bar, walkBar, hostEl, grip);
      doc.body.append(panel);
      x.addEventListener('click', () => close());
      modeBtn.addEventListener('click', () => setMode(mode === 'dock' ? 'float' : 'dock'));
      expandBtn.addEventListener('click', () => { big = !big; place(); });
      panel.addEventListener('keydown', e => { if (e.key === 'Escape') { e.stopPropagation(); close(); } });
      dragBar(bar);
      resizeGrip();
      addEventListener('pagehide', save);
      addEventListener('resize', () => { if (isOpen() && mode === 'float') clampFloat(); });
    }
    function wide() { return innerWidth >= 1100; }
    function place() {
      if (!panel) return;
      panel.classList.toggle('docked', mode === 'dock');
      panel.classList.toggle('sheet', mode === 'sheet');
      panel.classList.toggle('floating', mode === 'float');
      panel.classList.toggle('big', mode === 'float' && big);
      if (mode === 'dock' && dockHost) {
        if (panel.parentNode !== dockHost) dockHost.append(panel);
        panel.style.cssText = '';
      } else {
        // inside an open modal (the review player) or everything outside it is inert
        const top = (UI.sheet && UI.sheet.top && UI.sheet.top()) || doc.body;
        if (panel.parentNode !== top) top.append(panel);
      }
      if (mode === 'float') {
        const p = ls.get('satf.calc.pos', null);
        panel.style.cssText = '';
        if (p && !big) Object.assign(panel.style, { left: p.x + 'px', top: p.y + 'px', right: 'auto', width: p.w + 'px', height: p.h + 'px' });
        clampFloat();
      }
      if (mode === 'sheet') { panel.style.cssText = ''; panel.style.height = sheetH + 'dvh'; }
      const sheetOn = mode === 'sheet' && isOpen();
      doc.documentElement.classList.toggle('calc-sheet-open', sheetOn);
      doc.documentElement.style.setProperty('--calc-sheet-h', sheetOn ? sheetH + 'dvh' : '0px');
      if (dockHost) dockHost.classList.toggle('has-calc', mode === 'dock' && isOpen());
      modeBtn.hidden = !dockHost || phone();
      modeBtn.replaceChildren(icon(mode === 'dock' ? 'float' : 'dock', 16), h('span', { text: mode === 'dock' ? 'Float' : 'Dock' }));
      expandBtn.hidden = mode !== 'float';
      expandBtn.replaceChildren(icon(big ? 'shrink' : 'expand', 16), h('span', { text: big ? 'Shrink' : 'Expand' }));
      grip.hidden = mode !== 'float' || big;
      if (engine && engine.kind === 'desmos') try { engine.calc.resize(); } catch (_) {}
    }
    function clampFloat() {
      const r = panel.getBoundingClientRect();
      if (!r.width) return;
      const x = Math.min(Math.max(0, r.left), Math.max(0, innerWidth - Math.min(r.width, innerWidth)));
      const y = Math.min(Math.max(0, r.top), Math.max(0, innerHeight - 44));
      if (x !== r.left || y !== r.top) Object.assign(panel.style, { left: x + 'px', top: y + 'px', right: 'auto' });
    }
    function keepPos() {
      const r = panel.getBoundingClientRect();
      ls.set('satf.calc.pos', { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) });
    }
    function dragBar(bar) {
      let dx = 0, dy = 0, on = false, y0 = 0, h0 = 0;
      bar.addEventListener('pointerdown', e => {
        if (e.target.closest('button') || e.button > 0) return;
        on = true;
        const r = panel.getBoundingClientRect();
        dx = e.clientX - r.left; dy = e.clientY - r.top; y0 = e.clientY; h0 = r.height;
        bar.setPointerCapture(e.pointerId);
      });
      bar.addEventListener('pointermove', e => {
        if (!on) return;
        if (mode === 'float' && !big) {
          const r = panel.getBoundingClientRect();
          Object.assign(panel.style, { left: Math.min(Math.max(0, e.clientX - dx), innerWidth - r.width) + 'px', top: Math.min(Math.max(0, e.clientY - dy), innerHeight - 44) + 'px', right: 'auto' });
        } else if (mode === 'sheet') {
          panel.style.height = Math.max(20, Math.min(92, (h0 + (y0 - e.clientY)) / innerHeight * 100)) + 'dvh';
        }
      });
      const stop = () => {
        if (!on) return;
        on = false;
        if (mode === 'float' && !big) keepPos();
        if (mode === 'sheet') {                                // snap to 40, 60 or 90
          const now = panel.getBoundingClientRect().height / innerHeight * 100;
          if (now < 25) { close(); return; }
          sheetH = [40, 62, 90].reduce((a, b) => (Math.abs(b - now) < Math.abs(a - now) ? b : a));
          ls.set('satf.calc.sheet', sheetH);
          place();
        }
      };
      bar.addEventListener('pointerup', stop);
      bar.addEventListener('pointercancel', stop);
    }
    function resizeGrip() {
      let on = false, x0, y0, w0, h0;
      grip.addEventListener('pointerdown', e => {
        on = true; x0 = e.clientX; y0 = e.clientY;
        const r = panel.getBoundingClientRect(); w0 = r.width; h0 = r.height;
        Object.assign(panel.style, { left: r.left + 'px', top: r.top + 'px', right: 'auto' });
        grip.setPointerCapture(e.pointerId);
        e.preventDefault();
      });
      grip.addEventListener('pointermove', e => {
        if (!on) return;
        const r = panel.getBoundingClientRect();
        panel.style.width = Math.max(320, Math.min(innerWidth - r.left, w0 + e.clientX - x0)) + 'px';
        panel.style.height = Math.max(360, Math.min(innerHeight - r.top, h0 + e.clientY - y0)) + 'px';
      });
      const stop = () => { if (!on) return; on = false; keepPos(); if (engine && engine.kind === 'desmos') try { engine.calc.resize(); } catch (_) {} };
      grip.addEventListener('pointerup', stop);
      grip.addEventListener('pointercancel', stop);
    }

    function load() {
      if (loading) return loading;
      const key = UI.DESMOS_KEY !== undefined ? UI.DESMOS_KEY : TRIAL_KEY;
      loading = new Promise(res => {
        const fall = why => res(scientific(why));
        if (!key) return fall('the graphing calculator is unavailable');
        if (window.Desmos) return res(desmos());
        let settled = false;
        const fin = f => { if (!settled) { settled = true; f(); } };
        const sc = doc.createElement('script');
        sc.src = `https://www.desmos.com/api/v1.11/calculator.js?apiKey=${encodeURIComponent(key)}`;
        sc.onload = () => fin(() => (window.Desmos ? res(desmos()) : fall('the graphing calculator didn’t load')));
        sc.onerror = () => fin(() => fall('the graphing calculator didn’t load'));
        setTimeout(() => fin(() => (window.Desmos ? res(desmos()) : fall('the graphing calculator is taking too long'))), 8000);
        doc.head.append(sc);
      }).then(e => { engine = e; restore(); return e; });
      return loading;
    }
    function desmos() {
      hostEl.replaceChildren();
      // Desmos follows the site's look: inverted colours on a dark page
      const dark = () => { const t = doc.documentElement.dataset.theme; return t ? t === 'dark' : media('(prefers-color-scheme: dark)'); };
      const c = window.Desmos.GraphingCalculator(hostEl, { keypad: true, expressions: true, settingsMenu: true, border: false, invertedColors: dark() });
      const relook = () => { try { c.updateSettings({ invertedColors: dark() }); } catch (_) {} };
      new MutationObserver(relook).observe(doc.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
      try { matchMedia('(prefers-color-scheme: dark)').addEventListener('change', relook); } catch (_) {}
      c.observeEvent('change', changed);
      titleEl.textContent = 'Desmos';
      return {
        kind: 'desmos', calc: c,
        getState: () => c.getState(), setState: s => c.setState(s), blank: () => c.setBlank(),
        exprs: () => c.getExpressions().filter(x => x.latex).map(x => String(x.latex).slice(0, 200)).slice(0, 30),
      };
    }
    function scientific(why) {
      hostEl.replaceChildren();
      titleEl.textContent = 'Calculator';
      let deg = true, ans = 0, lines = [];
      const hist = h('ol', { class: 'sci-hist', 'aria-label': 'History' });
      const inp = h('input', { class: 'field sci-in', type: 'text', 'aria-label': 'Calculator input', autocomplete: 'off', spellcheck: 'false', placeholder: '2^10, sin(30), √(2)' });
      const out = h('p', { class: 'sci-out', 'aria-live': 'polite' });
      const degBtn = h('button', { type: 'button', class: 'btn sm sci-deg', 'aria-pressed': 'true', text: 'Deg' });
      const paintHist = () => hist.replaceChildren(...lines.slice(-40).map(l => h('li', {},
        h('button', { type: 'button', class: 'sci-line', title: 'Use this result', onclick: () => { insert(fmt(l.v)); } }, h('span', { class: 'sci-e', text: minus(l.e) }), h('b', { text: '= ' + minus(fmt(l.v)) })),
        h('button', { type: 'button', class: 'quiet sm', text: 'Copy', onclick: () => (UI.copyText ? UI.copyText(fmt(l.v), { toast: 'Copied' }) : null) }))));
      const insert = s => {
        const a = inp.selectionStart ?? inp.value.length, b = inp.selectionEnd ?? inp.value.length;
        inp.value = inp.value.slice(0, a) + s + inp.value.slice(b);
        inp.focus();
        inp.setSelectionRange(a + s.length, a + s.length);
      };
      const run = () => {
        const src = inp.value.trim();
        if (!src) return;
        try {
          const v = sciEval(src, deg, ans);
          ans = v; lines.push({ e: src, v }); inp.value = ''; out.textContent = `= ${minus(fmt(v))}`;
          paintHist(); hist.scrollTop = hist.scrollHeight; changed();
        } catch (e) { out.textContent = e.message; }
      };
      inp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); run(); } });
      degBtn.addEventListener('click', () => { deg = !deg; degBtn.textContent = deg ? 'Deg' : 'Rad'; degBtn.setAttribute('aria-pressed', String(deg)); });
      const KEYS = [['sin', 'sin('], ['cos', 'cos('], ['tan', 'tan('], ['π', 'π'], ['sin⁻¹', 'asin('], ['cos⁻¹', 'acos('], ['tan⁻¹', 'atan('], ['e', 'e'],
        ['x²', '^2'], ['^', '^'], ['√', '√('], ['1/x', '^(-1)'], ['(', '('], [')', ')'], ['ans', 'ans'], ['÷', '÷'],
        ['7', '7'], ['8', '8'], ['9', '9'], ['×', '×'], ['4', '4'], ['5', '5'], ['6', '6'], ['−', '−'], ['1', '1'], ['2', '2'], ['3', '3'], ['+', '+'],
        ['0', '0'], ['.', '.'], ['⌫', null], ['=', null]];
      const keys = h('div', { class: 'sci-keys' }, KEYS.map(([label, ins]) => h('button', { type: 'button', class: 'sci-k' + (label === '=' ? ' eq' : /^[0-9.]$/.test(label) ? ' d' : ''), text: label,
        'aria-label': { '⌫': 'Delete', '=': 'Equals', '√': 'Square root', 'x²': 'Squared', '^': 'Power', '1/x': 'Reciprocal', '−': 'Minus', '×': 'Times', '÷': 'Divided by' }[label] || label,
        onclick: () => { if (label === '=') run(); else if (label === '⌫') { inp.value = inp.value.slice(0, -1); inp.focus(); } else insert(ins); } })));
      hostEl.append(h('div', { class: 'sci' },
        h('p', { class: 'sci-why' }, h('b', { text: 'Calculator: scientific' }), ` · ${why}`),
        hist, h('div', { class: 'sci-row' }, inp, degBtn, h('button', { type: 'button', class: 'quiet sm', text: 'Clear', onclick: () => { lines = []; paintHist(); out.textContent = ''; inp.value = ''; } })),
        out, keys));
      return {
        kind: 'scientific', why,
        getState: () => ({ deg, ans, lines: lines.slice(-40) }),
        setState: s => { if (!s) return; deg = s.deg !== false; ans = +s.ans || 0; lines = Array.isArray(s.lines) ? s.lines : []; degBtn.textContent = deg ? 'Deg' : 'Rad'; paintHist(); },
        blank: () => { lines = []; ans = 0; inp.value = ''; out.textContent = ''; paintHist(); },
        exprs: () => lines.slice(-20).map(l => l.e.slice(0, 200)),
      };
    }
    function fmt(v) {
      if (!isFinite(v)) return String(v);
      if (Math.abs(v) < 1e-12) return '0';
      const s = String(+v.toPrecision(12));
      return s;
    }
    function changed() {
      if (Date.now() < quietUntil || walking) return;
      clearTimeout(changeTimer);
      changeTimer = setTimeout(() => {
        if (!engine || walking) return;
        const exprs = engine.exprs();
        subs.forEach(f => { try { f({ exprs, engine: engine.kind }); } catch (_) {} });
      }, 1000);
    }
    function save() {
      if (!engine || !sid || walking) return;
      try { localStorage.setItem('satf.calc.' + sid, JSON.stringify(engine.getState())); } catch (_) {}
    }
    // a sitting's own graph comes back; a sitting with none starts blank, never with another's
    function restore(fresh) {
      if (!engine || !sid) return;
      const s = ls.get('satf.calc.' + sid, null);
      if (!s && !fresh) return;
      quietUntil = Date.now() + 1500;
      try { if (s) engine.setState(s); else engine.blank(); } catch (_) {}
    }
    async function open(o = {}) {
      if (!panel) build();
      sheetH = ls.get('satf.calc.sheet', 62) || 62;
      mode = o.mode || (phone() ? 'sheet' : ls.get('satf.calc.mode', null) || (dockHost && wide() ? 'dock' : 'float'));
      if (mode === 'dock' && (!dockHost || phone())) mode = phone() ? 'sheet' : 'float';
      panel.hidden = false;
      place();
      clearInterval(saveTimer);
      saveTimer = setInterval(save, 10000);
      emitOpen();
      // focus now, so Esc closes it while Desmos is still loading; again once it has, unless the student moved on
      if (o.focus !== false) panel.focus({ preventScroll: true });
      const e = await load();
      if (e.kind === 'desmos') try { e.calc.resize(); } catch (_) {}
      if (o.focus !== false && isOpen() && (doc.activeElement === panel || doc.activeElement === doc.body)) panel.focus({ preventScroll: true });
      return e;
    }
    function close() {
      if (!panel || panel.hidden) return;
      save();
      clearInterval(saveTimer);
      panel.hidden = true;
      place();
      emitOpen();
    }
    function setMode(m) {
      mode = m;
      if (!phone()) ls.set('satf.calc.mode', m === 'sheet' ? null : m);
      place();
      emitOpen();
    }
    async function walkthrough(d) {
      if (!d || !d.exprs || !d.exprs.length) return false;
      const e = await open({ focus: false });
      if (e.kind !== 'desmos') { toast('Needs the graphing calculator'); return false; }
      const c = e.calc;
      if (!walking) walking = c.getState();
      c.setBlank();
      const add = (x, i) => c.setExpression({ id: 'walk' + i, latex: x.latex, hidden: !!x.hidden, label: x.label || undefined, showLabel: !!x.label });
      if (still()) d.exprs.forEach(add);
      else for (let i = 0; i < d.exprs.length; i++) { add(d.exprs[i], i); await sleep(300); }
      if (d.bounds) try { c.setMathBounds(d.bounds); } catch (_) {}
      if (d.point) c.setExpression({ id: 'walkp', latex: `(${d.point.x},${d.point.y})`, label: d.point.label || '', showLabel: !!d.point.label, color: '#F18508' });
      walkNote.textContent = d.note || 'The Desmos way for this question';
      walkBar.hidden = false;
      return true;
    }
    function walkBack() {
      if (walking && engine && engine.kind === 'desmos') { quietUntil = Date.now() + 1500; engine.calc.setState(walking); }
      walking = null;
      walkBar.hidden = true;
    }
    return {
      open, close, toggle: () => (isOpen() ? close() : open()), setMode, walkthrough, walkBack, load,
      get isOpen() { return isOpen(); }, get mode() { return mode; }, get engine() { return engine ? engine.kind : null; },
      get el() { return panel; },
      get desmos() { return engine && engine.kind === 'desmos' ? engine.calc : null; },   // X8 diffs getState().expressions
      dock(el) { dockHost = el || null; if (panel) { if (!dockHost && mode === 'dock') mode = 'float'; place(); } },
      sitting(id) { if (id === sid) return; const had = sid; save(); sid = id || null; if (engine) restore(!!had); },
      state: () => (engine ? engine.getState() : null),
      exprs: () => (engine ? engine.exprs() : []),
      onChange(f) { subs.add(f); return () => subs.delete(f); },
      onOpen(f) { openSubs.add(f); return () => openSubs.delete(f); },
    };
  })();

  /* the scientific engine: a shunting-yard evaluator, no eval (tests.md item 74) */
  const FUNCS = ['asin', 'acos', 'atan', 'sqrt', 'sin', 'cos', 'tan', 'abs', 'ln', 'log'];
  const CONSTS = ['ans', 'pi', 'e'];
  function sciTokens(src) {
    const s = String(src).toLowerCase().replace(/\s+/g, '').replace(/[×·]/g, '*').replace(/÷/g, '/').replace(/[−–]/g, '-').replace(/π/g, 'pi').replace(/√/g, 'sqrt');
    const out = [];
    let i = 0;
    while (i < s.length) {
      const c = s[i];
      const m = s.slice(i).match(/^(\d+\.?\d*|\.\d+)(e[+-]?\d+)?/);
      if (m && /[\d.]/.test(c)) { out.push({ t: 'n', v: parseFloat(m[0]) }); i += m[0].length; continue; }
      if (/[a-z]/.test(c)) {
        const name = [...FUNCS, ...CONSTS].find(w => s.startsWith(w, i));
        if (!name) throw new Error('Unknown name: ' + s.slice(i).match(/^[a-z]+/)[0]);
        out.push(FUNCS.includes(name) ? { t: 'f', v: name } : { t: 'c', v: name });
        i += name.length;
        continue;
      }
      if ('+-*/^()'.includes(c)) { out.push({ t: c === '(' || c === ')' ? c : 'o', v: c }); i++; continue; }
      throw new Error(`Can’t read “${c}”`);
    }
    // implicit multiplication: 2π, 3(2+1), (1)(2), 2sin30
    const full = [];
    out.forEach((tk, k) => {
      const pv = full[full.length - 1];
      if (pv && (pv.t === 'n' || pv.t === 'c' || pv.t === ')') && (tk.t === 'n' || tk.t === 'c' || tk.t === 'f' || tk.t === '(')) full.push({ t: 'o', v: '*' });
      full.push(tk);
    });
    return full;
  }
  function sciEval(src, deg = true, ans = 0) {
    const toks = sciTokens(src);
    if (!toks.length) throw new Error('Type an expression');
    const PREC = { '+': 1, '-': 1, '*': 2, '/': 2, neg: 3, f: 3, '^': 4 };
    const outQ = [], ops = [];
    let prev = null;
    for (const tk of toks) {
      if (tk.t === 'n' || tk.t === 'c') outQ.push(tk);
      else if (tk.t === 'f') ops.push(tk);
      else if (tk.t === '(') ops.push(tk);
      else if (tk.t === ')') {
        while (ops.length && ops[ops.length - 1].t !== '(') outQ.push(ops.pop());
        if (!ops.length) throw new Error('Check the brackets');
        ops.pop();
      } else {
        const unary = tk.v === '-' && (!prev || prev.t === 'o' || prev.t === '(' || prev.t === 'f' || prev.t === 'neg');
        if (tk.v === '+' && (!prev || prev.t === 'o' || prev.t === '(' || prev.t === 'f' || prev.t === 'neg')) continue;
        if (unary) { const u = { t: 'neg', v: 'neg' }; ops.push(u); prev = u; continue; }
        const p = PREC[tk.v], right = tk.v === '^';
        while (ops.length) {
          const top = ops[ops.length - 1];
          if (top.t === '(') break;
          const tp = top.t === 'f' ? PREC.f : top.t === 'neg' ? PREC.neg : PREC[top.v];
          if (tp > p || (tp === p && !right)) outQ.push(ops.pop()); else break;
        }
        ops.push(tk);
      }
      prev = tk;
    }
    while (ops.length) { const x = ops.pop(); if (x.t === '(') throw new Error('Check the brackets'); outQ.push(x); }
    const rad = x => (deg ? x * Math.PI / 180 : x), back = x => (deg ? x * 180 / Math.PI : x);
    const F = { sin: x => Math.sin(rad(x)), cos: x => Math.cos(rad(x)), tan: x => Math.tan(rad(x)), asin: x => back(Math.asin(x)), acos: x => back(Math.acos(x)),
      atan: x => back(Math.atan(x)), sqrt: Math.sqrt, abs: Math.abs, ln: Math.log, log: Math.log10 };
    const st = [];
    for (const tk of outQ) {
      if (tk.t === 'n') st.push(tk.v);
      else if (tk.t === 'c') st.push(tk.v === 'pi' ? Math.PI : tk.v === 'e' ? Math.E : +ans || 0);
      else if (tk.t === 'neg' || tk.t === 'f') {
        if (!st.length) throw new Error('That expression is incomplete');
        const a = st.pop();
        st.push(tk.t === 'neg' ? -a : F[tk.v](a));
      } else {
        if (st.length < 2) throw new Error('That expression is incomplete');
        const b = st.pop(), a = st.pop();
        st.push(tk.v === '+' ? a + b : tk.v === '-' ? a - b : tk.v === '*' ? a * b : tk.v === '/' ? a / b : Math.pow(a, b));
      }
    }
    if (st.length !== 1) throw new Error('That expression is incomplete');
    let v = st[0];
    if (Number.isNaN(v)) throw new Error('Not a real number');
    if (!isFinite(v)) throw new Error('Can’t divide by zero');
    // trig in degrees: sin(30) is 0.5 exactly, not 0.49999999999999994
    v = +v.toPrecision(12);
    return v;
  }
  sciEval.__test = [['2^10', 1024], ['sin(30)', 0.5], ['2+3*4', 14], ['(2+3)*4', 20], ['-3^2', -9], ['2^-1', 0.5], ['√16', 4], ['√(2)*√(2)', 2],
    ['2π', 2 * Math.PI], ['cos(60)+1', 1.5], ['asin(0.5)', 30], ['10/4', 2.5], ['3(2+1)', 9], ['ln(e)', 1], ['log(1000)', 3], ['2*-3', -6], ['-2*3', -6], ['2sin30', 1]];

  /* ------------------------------------------------------------ the Save toast (Review V3): why you saved it, optional
     UI.savedToast(q, {text, onWhy(kind), onLucky(), onAsk(), onNote()}) -> the toast, 5 s:
     Saved · Nice trick · Hard · Got lucky · Ask a tutor · Note. Tapping nothing stores nothing.
     Defaults: why -> PATCH /api/saved {template, seed, why}; Got lucky -> POST /api/mistakes/add {template, seed}.
     Got lucky shows once the key has shown (revealed); Ask a tutor and Note only with their hook. */
  function savedToast(q, o = {}) {
    const text = o.text || 'Saved';
    if (!q || !q.template || q.seed === undefined || q.seed === null) return toast(text);
    const row = h('span', { class: 'saved-why' }, h('span', { class: 'saved-why-t', text }));
    const body = { template: q.template, seed: q.seed };
    let t = null;
    const chip = (label, run, done) => {
      const b = h('button', { type: 'button', class: 'chip', text: label });
      b.addEventListener('click', async () => {
        if (t) t.close();
        try { await run(); if (done) toast(done); } catch (e) { toast((e && e.message) || 'Not saved. Try again.'); }
      });
      row.append(b);
    };
    const why = kind => (o.onWhy ? o.onWhy(kind) : api('/saved', { method: 'PATCH', body: Object.assign({ why: kind }, body) }));
    chip('Nice trick', () => why('trick'), 'Noted');
    chip('Hard', () => why('hard'), 'Noted');
    if (o.revealed !== false) chip('Got lucky', () => (o.onLucky ? o.onLucky() : api('/mistakes/add', { method: 'POST', body })), 'In Redo: one correct answer closes it');
    if (o.onAsk) chip('Ask a tutor', () => o.onAsk());
    if (o.onNote) chip('Note', () => o.onNote());
    t = toast(row, { ms: 5000 });
    return t;
  }

  /* ------------------------------------------------------------ export */
  Object.assign(UI, {
    workspace, question, splitCheck, questionActions, twin, twinSheet, twinInline, stemDiff, pad, calc, tex, katex, spr, readAloud, sciEval, savedToast, fracText, fracNodes,
    workspaceSelfTest: selfTest, qicon: icon,
  });
  if (location.pathname.startsWith('/dev/')) {
    const r = selfTest();
    if (!r.ok) console.error('question.js self-test failed', r);
  }
})();
