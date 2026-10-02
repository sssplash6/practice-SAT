/* ============================================================================
   SAT Freshman -- Welcome, /welcome/ : the first screen a new visitor sees.
   Create an account (first name + email) or sign in (email), both with the 6-digit
   code the email-code sign-in already uses; or carry on without one. Every path
   sets satf.welcomed so this is not shown twice, and ends in UI.acct.finish.
   ============================================================================ */
(() => {
  'use strict';
  const h = UI.h, A = UI.acct;
  const q = new URLSearchParams(location.search);
  const go = (q.get('go') || '').startsWith('/') && !q.get('go').startsWith('//') ? q.get('go') : '/';
  const seen = () => { try { localStorage.setItem('satf.welcomed', '1'); } catch (_) {} };
  UI.shell('welcome');
  document.getElementById('mark').innerHTML = UI.mark(32);
  const body = document.getElementById('body');
  const err = h('p', { class: 'field-err', role: 'alert', hidden: true });
  const say = t => { err.textContent = t || ''; err.hidden = !t; };
  const btn = (label, primary, on) => { const b = h('button', { type: 'button', class: primary ? 'pill' : 'quiet', text: label }); b.addEventListener('click', on); return b; };
  let mode = 'create';

  function form() {
    say('');
    const name = h('input', { class: 'field', type: 'text', autocomplete: 'given-name', 'aria-label': 'First name', placeholder: 'First name', maxlength: '40' });
    const email = h('input', { class: 'field', type: 'email', autocomplete: 'email', inputmode: 'email', spellcheck: 'false', 'aria-label': 'Email', placeholder: 'you@example.com' });
    const send = async () => {
      say('');
      if (mode === 'create' && !name.value.trim()) { say('Add your first name.'); name.focus(); return; }
      if (!email.checkValidity() || !email.value.trim()) { say('That email doesn’t look right.'); email.focus(); return; }
      seen();
      try {
        if (mode === 'create') await UI.api('/me', { method: 'PUT', body: { name: name.value.trim() } });
        const r = await UI.api('/account/link', { method: 'POST', body: { email: email.value.trim() } });
        if (r.delivery === 'outbox') { say('Email codes aren’t switched on for this site yet. You can carry on without an account for now.'); return; }
        codeStep(email.value.trim(), r.email_masked || email.value.trim());
      } catch (x) { say(x.status === 429 ? 'Wait a minute before asking for another code.' : 'Couldn’t send a code. Try again.'); }
    };
    email.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); send(); } });
    name.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); email.focus(); } });
    const tabs = h('div', { class: 'wl-tabs' });
    UI.seg(tabs, [{ value: 'create', label: 'Create account' }, { value: 'signin', label: 'Sign in' }], { value: mode, label: 'Create an account or sign in', full: true, onChange: v => { mode = v; form(); } });
    body.replaceChildren(
      h('p', { class: 'wl-lead', text: mode === 'create' ? 'Practice that remembers your mistakes. Make a free account to keep your progress on any device.' : 'Welcome back. We’ll email you a 6-digit code.' }),
      tabs,
      h('div', { class: 'wl-form' }, mode === 'create' ? name : null, email, err,
        btn(mode === 'create' ? 'Create my account' : 'Send me a code', true, send),
        h('p', { class: 'help', text: 'We email a 6-digit code. No password.' })),
      h('div', { class: 'wl-skip' }, h('a', { class: 'quiet', href: go, text: 'Continue without an account', onclick: seen })));
    (mode === 'create' ? name : email).focus();
  }

  function codeStep(address, masked) {
    say('');
    let tries = 5;
    const otpHost = h('div');
    UI.otp(otpHost, async code => {
      say('');
      try {
        const res = await UI.api('/account/verify', { method: 'POST', body: { code, carry: false, session_only: false } });
        await A.finish(res, { shared: false, local: { answers: 0 }, to: go, method: 'email' });
      } catch (x) {
        if (x.status === 400) { tries -= 1; say(`That code doesn’t match. ${tries} ${tries === 1 ? 'try' : 'tries'} left.`); }
        else say(x.status === 410 ? 'That code is used up. Send a new one.' : 'That didn’t work. Try again.');
      }
    }, { length: 6, label: 'The 6-digit code' });
    body.replaceChildren(h('p', { class: 'wl-lead' }, 'Enter the code we sent to ', h('b', { text: masked }), '.'), otpHost, err,
      h('div', { class: 'acts' }, btn('Use a different email', false, form)));
  }

  seen();
  UI.api('/account').then(acc => { if (acc && acc.saved) location.replace(go); else form(); }, form);
})();
