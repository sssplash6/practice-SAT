/* ============================================================================
   SAT Freshman -- Sign in, /signin/ (email-only access, 2026-10-20)

   The one way in: an email, then the full name for a new account. POST /api/account/beta
   answers {needs_name, name} for a new account (the approved list's name prefills it), and a
   credential once it can sign in; 403 {reason: not_registered} for an address that is not on the
   approved list. Every browser that has not signed in lands here (ui.js toSignin, ?go= the page
   it wanted), and every path ends in UI.acct.finish, then ?go= or /.
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h, A = UI.acct;
  const ls = A.ls;
  const q = new URLSearchParams(location.search);
  // only a path on this site: resolve it and require the same origin (so /\\evil.com and //evil.com cannot leave the site)
  const go = (() => { const raw = q.get('go') || ''; if (!raw.startsWith('/')) return '/'; try { const u = new URL(raw, location.origin); return u.origin === location.origin ? u.pathname + u.search + u.hash : '/'; } catch (_) { return '/'; } })();
  UI.shell({ page: 'signin', now: false, nowBlock: false, chrome: 'focus' });   // the slim brand bar, no app chrome
  document.getElementById('mark').innerHTML = UI.mark(40);
  const body = document.getElementById('body');
  const err = h('p', { class: 'field-err', role: 'alert', hidden: true });
  const say = t => { err.textContent = t || ''; err.hidden = !t; };
  const why = x => x && x.offline ? 'You’re offline. Try again when you’re back.'
    : x && x.status === 403 ? 'That email isn’t registered. Check it, or ask your teacher to add it.'
    : x && x.status === 429 ? 'Too many tries. Wait a few minutes.'
    : 'That didn’t work. Try again.';
  let local = { answers: 0 };

  async function start() {
    body.replaceChildren(UI.skel(null, 'card:2'));
    const [acc, loc] = await Promise.all([UI.api('/account', { quiet: true }).catch(() => null), A.localAnswers()]);
    local = loc;
    if (acc && acc.saved) { signedIn(acc); return; }
    emailStep(ls.get('satf.lastEmail', null) || '');
  }

  function signedIn(acc) {
    const name = (UI.shellData() && UI.shellData().me && UI.shellData().me.name) || null;
    body.replaceChildren(h('div', { class: 'si-panel' },
      h('p', { text: `You’re signed in${name ? ` as ${name}` : ''}${acc.email_masked ? ` (${acc.email_masked})` : ''}. To sign in as someone else, sign out first.` }),
      h('div', { class: 'acts' }, h('a', { class: 'pill sm', href: go, text: 'Continue' }),
        h('button', { type: 'button', class: 'quiet', text: 'Sign out', onclick: () => UI.signOut() }))));
  }

  function button(label, fn) {
    const b = h('button', { type: 'button', class: 'pill wide', text: label });
    b.addEventListener('click', async () => {
      if (b.getAttribute('aria-busy')) return;
      b.setAttribute('aria-busy', 'true');
      try { await fn(); } finally { b.removeAttribute('aria-busy'); }
    });
    return b;
  }
  // a browser whose old device key was signed out starts from a new code, then asks again
  async function post(payload) {
    try { return await UI.api('/account/beta', { method: 'POST', body: payload, quiet: true }); }
    catch (x) {
      if (!x || !x.retired) throw x;
      UI.freshLearner();
      return UI.api('/account/beta', { method: 'POST', body: payload, quiet: true });
    }
  }
  async function done(res, email) {
    ls.set('satf.lastEmail', email);
    await A.finish(res, { shared: false, local, to: go, method: 'email' });
  }

  function emailStep(prefill) {
    say('');
    const f = h('input', { class: 'field', type: 'email', autocomplete: 'email', inputmode: 'email', spellcheck: 'false',
      'aria-label': 'Email', placeholder: 'you@example.com', value: prefill || '' });
    const send = async () => {
      const email = f.value.trim();
      if (!email || !f.checkValidity()) { say('That email doesn’t look right.'); f.focus(); return; }
      say('');
      try {
        const r = await post({ email });
        if (r.needs_name) { nameStep(email, r.name || ''); return; }
        await done(r, email);
      } catch (x) { say(why(x)); f.focus(); }
    };
    const b = button('Continue', send);
    f.addEventListener('keydown', ev => { if (ev.key === 'Enter') { ev.preventDefault(); b.click(); } });
    body.replaceChildren(h('div', { class: 'si-panel' },
      h('p', { text: 'Enter your email to sign in.' }), h('div', { class: 'acts' }, f, b), err));
    f.focus();
  }

  function nameStep(email, suggested) {
    say('');
    const f = h('input', { class: 'field', type: 'text', autocomplete: 'name', 'aria-label': 'Full name',
      placeholder: 'First and last name', maxlength: '40', value: suggested });
    const save = async () => {
      const name = f.value.trim().replace(/\s+/g, ' ');
      if (name.split(' ').length < 2) { say('Write your first and last name.'); f.focus(); return; }
      if (/[\d<>@]/.test(name)) { say('Use letters only.'); f.focus(); return; }
      say('');
      try { await done(await post({ email, name }), email); }
      catch (x) { say(x && x.status === 422 ? 'Use letters only, up to 40.' : why(x)); f.focus(); }
    };
    const b = button('Continue', save);
    f.addEventListener('keydown', ev => { if (ev.key === 'Enter') { ev.preventDefault(); b.click(); } });
    body.replaceChildren(h('div', { class: 'si-panel' },
      h('p', { text: 'Welcome. What’s your full name?' }), h('div', { class: 'acts' }, f, b), err,
      h('div', { class: 'acts' }, h('button', { type: 'button', class: 'quiet', text: 'Use a different email', onclick: () => emailStep(email) }))));
    f.focus();
    if (suggested) f.select();
  }

  start();
})();
