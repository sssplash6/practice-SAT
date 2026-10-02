/* ============================================================================
   SAT Freshman -- Sign in, /signin/ (Shell 5; shell-me U19, U19b, U20, U21)

   Tabs: Passkey · Use your phone · Email code · More (a transfer code), hash #passkey /
   #phone / #email / #code (#pair is #phone). It opens on the method this device used
   last (localStorage satf.lastMethod), else Passkey where a platform authenticator
   exists, else Use your phone. "This is a shared computer" applies to every tab. A
   conditional-mediation passkey request runs from load and is renewed before its
   challenge expires. Every path ends in UI.acct.finish: the carry choice, then /.
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h, A = UI.acct;
  const ls = A.ls;
  const q = new URLSearchParams(location.search);
  // only a path on this site: resolve it and require the same origin (so /\\evil.com and //evil.com cannot leave the site)
  const go = (() => { const raw = q.get('go') || ''; if (!raw.startsWith('/')) return '/'; try { const u = new URL(raw, location.origin); return u.origin === location.origin ? u.pathname + u.search + u.hash : '/'; } catch (_) { return '/'; } })();
  UI.shell('signin');
  document.getElementById('mark').innerHTML = UI.mark(32);
  const body = document.getElementById('body');
  const TABS = [{ id: 'passkey', label: 'Passkey' }, { id: 'phone', label: 'Use your phone' }, { id: 'email', label: 'Email code' }, { id: 'code', label: 'More' }];
  const ERR = { 404: 'No code like that. Check it and try again.', 410: 'That code has expired or was used. Make a new one on your other device.',
    403: 'Your other device said no.', 429: 'Too many tries. Wait 10 minutes.' };
  const errText = (e, fallback) => (e && e.offline ? 'You’re offline. Try again when you’re back.' : (e && ERR[e.status]) || fallback);
  let shared = UI.shared(), local = { answers: 0 }, health = {}, current = null;
  const opts = () => ({ shared, local, to: go });

  async function start() {
    body.replaceChildren(UI.skel(null, 'card:3'));
    const [acc, loc, hl, pk] = await Promise.all([UI.api('/account').catch(() => null), A.localAnswers(),
      fetch('/api/health').then(r => r.json()).catch(() => ({})), A.passkeyReady()]);
    local = loc; health = hl || {};
    if (acc && acc.saved) { signedIn(acc); return; }
    if (q.get('t')) { emailLink(q.get('t')); return; }
    const hash = location.hash.slice(1) === 'pair' ? 'phone' : location.hash.slice(1);
    const last = ls.get('satf.lastMethod', null);
    const first = TABS.some(t => t.id === hash) ? hash : TABS.some(t => t.id === last) ? last : pk ? 'passkey' : 'phone';
    build(first, pk);
  }

  function signedIn(acc) {
    const name = (UI.shellData() && UI.shellData().me && UI.shellData().me.name) || null;
    body.replaceChildren(h('div', { class: 'si-panel' },
      h('p', { text: `You’re signed in${name ? ` as ${name}` : ''}${acc.email_masked ? ` (${acc.email_masked})` : ''}. To sign in as someone else, sign out first.` }),
      h('div', { class: 'acts' }, h('a', { class: 'pill sm', href: '/', text: 'Go to Today' }),
        h('button', { type: 'button', class: 'quiet', text: 'Sign out', onclick: () => UI.signOut() })),
      h('p', { class: 'help' }, 'Signing in another device? On it, open Sign in › Use your phone, then ', h('a', { class: 'link', href: '/pair/', text: 'type its six digits here' }), '.')));
  }

  /* ---- the tabs and the shared-computer box */
  let panel = null, tabs = null;
  function build(first, pk) {
    const google = h('div', { class: 'si-google' });
    const tabHost = h('div');
    panel = h('div', { class: 'si-panel', role: 'tabpanel' });
    const box = h('input', { type: 'checkbox', checked: shared ? '' : null });
    box.addEventListener('change', () => { shared = box.checked; if (current === 'phone') showTab('phone', pk); });
    const sharedRow = h('label', { class: 'check' }, box, 'This is a shared computer');
    UI.tooltip(sharedRow, 'Signs out 15 minutes after you stop, or about a minute after you close the browser. Nothing is kept on this computer.');
    tabs = UI.tabs(tabHost, TABS, { value: first, label: 'Ways to sign in', onChange: id => { history.replaceState(null, '', `#${id}`); showTab(id, pk); } });
    body.replaceChildren(google, tabHost, panel, sharedRow);
    if (health.google && health.google_client_id) googleButton(google);
    showTab(first, pk);
    conditional();
  }
  let stop = [];
  function showTab(id, pk) {
    stop.forEach(f => f()); stop = [];
    current = id;
    if (id === 'passkey') passkeyTab(pk);
    else if (id === 'phone') phoneTab();
    else if (id === 'email') emailTab();
    else codeTab();
  }
  const fail = (el, text) => { el.textContent = text; el.hidden = !text; };

  /* ---- passkeys (U19): the button, and autofill from the email field */
  function passkeyTab(pk) {
    const e = h('p', { class: 'field-err', role: 'alert', hidden: true });
    if (!pk) {
      panel.replaceChildren(h('p', { text: 'This browser has no passkey of its own. Your browser may still offer one from your phone, or your phone can sign you in here.' }),
        h('div', { class: 'acts' }, button('Sign in with a passkey', false, () => modalPasskey(e)), button('Use your phone', true, () => tabs.set('phone'))), e);
      return;
    }
    panel.replaceChildren(h('p', { text: 'Face ID, Touch ID, Windows Hello or your phone: no password.' }),
      h('div', { class: 'acts' }, button('Sign in with a passkey', true, () => modalPasskey(e))), e);
  }
  function button(label, primary, fn) {
    const b = h('button', { type: 'button', class: primary ? 'pill sm' : 'btn sm', text: label });
    b.addEventListener('click', async () => { b.setAttribute('aria-busy', 'true'); try { await fn(b); } finally { b.removeAttribute('aria-busy'); } });
    return b;
  }
  async function passkeyLogin(assert) {
    const res = await UI.api('/passkey/login', { method: 'POST', body: { ...assert.body, carry: false, session_only: shared } });
    await A.finish(res, { ...opts(), method: 'passkey' });
  }
  let condAbort = null, condTimer = 0;
  async function modalPasskey(e) {
    fail(e, '');
    if (condAbort) condAbort.abort();                 // the browser allows one get() at a time
    try { await passkeyLogin(await A.passkeyGet({})); }
    catch (x) {
      if (x && (x.name === 'NotAllowedError' || x.name === 'AbortError')) { conditional(); return; }
      fail(e, x && x.status === 401 ? 'That passkey isn’t one of ours. Try another way.' : errText(x, 'That didn’t work. Try again or use another way.'));
      conditional();
    }
  }
  async function conditional() {
    try { if (!window.PublicKeyCredential || !(await PublicKeyCredential.isConditionalMediationAvailable?.())) return; } catch (_) { return; }
    if (condAbort) condAbort.abort();
    clearTimeout(condTimer);
    const ctl = new AbortController();
    condAbort = ctl;
    // renew before the challenge lapses (30 s before, or sooner for a short SATF_WEBAUTHN_TTL), so a page left open still signs in
    const onOptions = o => {
      const left = new Date(o.expires) - Date.now();
      if (left > 0) condTimer = setTimeout(() => { if (condAbort === ctl && document.visibilityState === 'visible') conditional(); }, Math.max(1000, Math.min(left - 30000, left * 0.8)));
    };
    try {
      // resolves only when the student picks a passkey from the email field's autofill
      await passkeyLogin(await A.passkeyGet({ conditional: true, signal: ctl.signal, onOptions }));
    } catch (x) {
      if (x && x.name === 'AbortError') return;
      if (x && x.status === 401) UI.toast('That passkey isn’t one of ours. Try another way.');
    }
  }
  // back to a hidden tab whose challenge may have lapsed: start a fresh one
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && condAbort) conditional(); });

  /* ---- use your phone (U20): a QR and six digits; the phone approves */
  async function phoneTab() {
    panel.replaceChildren(UI.skel(null, { w: 180, h: 180, r: 10 }));
    let r;
    try { r = await UI.api('/link/request', { method: 'POST', body: { device: A.deviceLabel(), session_only: shared } }); }
    catch (x) { panel.replaceChildren(h('p', { class: 'field-err', text: errText(x, 'Couldn’t make a code. Try again.') }), button('Try again', false, phoneTab)); return; }
    const code = String(r.code);
    const url = `${location.origin}/pair/?r=${encodeURIComponent(r.token)}&c=${code}`;
    const qrBox = h('div', { class: 'qr' });
    const left = h('span');
    const state = h('p', { class: 'help', role: 'status', text: 'Waiting for your phone…' });
    panel.replaceChildren(h('p', { text: 'On your phone, scan this, or open SAT Freshman there and choose Menu › Sign in another device, then type the six digits.' }),
      qrBox, h('p', { class: 'code-big', 'aria-label': `Code ${code.split('').join(' ')}`, text: `${code.slice(0, 3)} ${code.slice(3)}` }),
      h('p', { class: 'meta', style: 'text-align: center' }, `This is ${A.deviceLabel()} · expires in `, left), state);
    try { await UI.need('qr'); qrBox.append(UI.qr(url, { size: 180, label: 'A code for your phone' })); }
    catch (_) { qrBox.append(h('p', { class: 'meta', text: 'Type the six digits on your phone.' })); }
    const stopClock = UI.countdown(left, r.expires, { label: 'Code', onEnd: () => expired() });
    let alive = true;
    const expired = () => { alive = false; state.replaceChildren('That code has expired. ', button('New code', false, phoneTab)); };
    const tick = async () => {
      if (!alive || current !== 'phone') return;
      try {
        const s = await UI.api(`/link/${encodeURIComponent(r.token)}`, { quiet: true });
        if (s.state === 'allowed') { alive = false; state.textContent = 'Approved. Signing in…'; await A.finish(s, { ...opts(), method: 'phone' }); return; }
        if (s.state === 'denied') { alive = false; state.replaceChildren('Your phone said no. ', button('New code', false, phoneTab)); return; }
      } catch (x) {
        if (x.status === 410) { expired(); return; }
      }
      if (alive) setTimeout(tick, 2000);
    };
    setTimeout(tick, 2000);
    stop.push(() => { alive = false; stopClock(); });
  }

  /* ---- email code (Shell 5, U19): a remembered address is one tap */
  function emailTab(prefill) {
    const remembered = shared ? null : ls.get('satf.lastEmail', null);
    const e = h('p', { class: 'field-err', role: 'alert', hidden: true });
    const f = h('input', { class: 'field', type: 'email', autocomplete: 'username webauthn', inputmode: 'email', spellcheck: 'false',
      'aria-label': 'Email', placeholder: 'you@example.com', value: prefill || '' });
    const send = async email => {
      fail(e, '');
      if (!email) { fail(e, 'That email doesn’t look right.'); return; }
      try {
        const r = await UI.api('/account/link', { method: 'POST', body: { email } });
        if (r.delivery === 'outbox') { outbox(); return; }
        codeStep(email, r.email_masked || email);
      } catch (x) { fail(e, x.status === 429 ? 'Wait a minute before asking for another code.' : errText(x, 'Couldn’t send a code. Try again.')); }
    };
    const mask = s => s.replace(/^(.)[^@]*(@.*)$/, (m, a, b) => `${a}•••${b}`);
    panel.replaceChildren(...[
      remembered ? h('div', { class: 'acts' }, button(`Send a code to ${mask(remembered)}`, true, () => send(remembered)),
        h('button', { type: 'button', class: 'quiet', text: 'Another email', onclick: () => { ls.set('satf.lastEmail', null); emailTab(); } })) : null,
      remembered ? null : h('p', { text: 'We send a 6-digit code. No password.' }),
      remembered ? null : h('div', { class: 'acts' }, f, button('Send code', true, () => (f.checkValidity() ? send(f.value.trim()) : fail(e, 'That email doesn’t look right.')))), e].filter(Boolean));
    f.addEventListener('keydown', ev => { if (ev.key === 'Enter') { ev.preventDefault(); if (f.checkValidity()) send(f.value.trim()); } });
  }
  function outbox() {
    panel.replaceChildren(h('p', { text: 'Email codes aren’t switched on for this site yet. Sign in with a passkey, your phone or a transfer code from a signed-in device.' }),
      h('div', { class: 'acts' }, button('Passkey', true, () => tabs.set('passkey')), button('Use your phone', false, () => tabs.set('phone')),
        button('Transfer code', false, () => tabs.set('code'))));
  }
  function codeStep(email, masked) {
    const e = h('p', { class: 'field-err', role: 'alert', hidden: true });
    const otpHost = h('div');
    let tries = 5;
    const otp = UI.otp(otpHost, async code => {
      fail(e, '');
      try {
        const res = await UI.api('/account/verify', { method: 'POST', body: { code, carry: false, session_only: shared } });
        if (!shared) ls.set('satf.lastEmail', email);
        await A.finish(res, { ...opts(), method: 'email' });
      } catch (x) {
        if (otp.invalid) otp.invalid();
        if (x.status === 400) { tries -= 1; fail(e, `That code doesn’t match. ${tries} ${tries === 1 ? 'try' : 'tries'} left.`); }
        else fail(e, x.status === 410 ? 'That code is used up. Send a new one.' : errText(x, 'That didn’t work. Try again.'));
      }
    }, { length: 6, label: 'The 6-digit code' });
    panel.replaceChildren(h('p', {}, 'Enter the code we sent to ', h('b', { text: masked }), '.'), otpHost, e,
      h('div', { class: 'acts' }, h('button', { type: 'button', class: 'quiet', text: 'Use a different email', onclick: () => emailTab(email) })),
      h('p', { class: 'help', text: 'Or tap the link in the email: on this device it signs you in here.' }));
    setTimeout(() => otp.focus && otp.focus(), 50);
  }
  // the email's link (Shell 1 step 4): only the browser that asked finishes with its code
  async function emailLink(token) {
    body.replaceChildren(UI.skel(null, 'lines:2'));
    try {
      const r = await UI.api('/account/verify', { method: 'POST', body: { token, carry: false } });
      if (r.other_device) {
        const code = String(r.code);
        body.replaceChildren(h('div', { class: 'si-panel' },
          h('p', {}, 'You asked on another device. Type ', h('b', { class: 'n', text: `${code.slice(0, 3)} ${code.slice(3)}` }), ' there, or sign in on this device instead.'),
          h('div', { class: 'acts' }, button('Sign in on this device', true, async () => {
            const res = await UI.api('/account/verify', { method: 'POST', body: { token, here: true, carry: false } });
            await A.finish(res, { ...opts(), method: 'email' });
          }))));
        return;
      }
      await A.finish(r, { ...opts(), method: 'email' });
    } catch (x) {
      body.replaceChildren(h('div', { class: 'si-panel' }, h('p', { text: x.status === 410 ? 'That link has expired. Send yourself a new code.' : errText(x, 'That link didn’t work.') }),
        h('a', { class: 'pill sm', href: '/signin/#email', text: 'Send a new code' })));
    }
  }

  /* ---- More: a transfer code from a signed-in device (U21) */
  function codeTab() {
    const e = h('p', { class: 'field-err', role: 'alert', hidden: true });
    const f = h('input', { class: 'field', autocomplete: 'off', autocapitalize: 'characters', spellcheck: 'false', maxlength: '9',
      'aria-label': 'Transfer code', placeholder: 'K7P4 M2QX', style: 'font-family: var(--mono); letter-spacing: .08em' });
    const redeem = async () => {
      const code = f.value.toUpperCase().replace(/[^A-HJ-NP-Z2-9]/g, '');
      if (code.length !== 8) { fail(e, 'Eight letters and digits, as the other device shows them.'); return; }
      try {
        const res = await UI.api('/transfer/redeem', { method: 'POST', body: { code, carry: false, session_only: shared } });
        await A.finish(res, { ...opts(), method: 'code' });
      } catch (x) { fail(e, x.status === 410 ? 'That code has expired or was used.' : x.status === 404 ? 'No code like that.' : errText(x, 'That didn’t work. Try again.')); }
    };
    f.addEventListener('keydown', ev => { if (ev.key === 'Enter') redeem(); });
    panel.replaceChildren(h('p', { text: 'On a signed-in device, open Settings › Account & devices › Move to another device, and type its code here.' }),
      h('div', { class: 'acts' }, f, button('Sign in', true, redeem)), e);
  }

  /* ---- Continue with Google (U19b), only when the deploy has a client ID */
  function googleButton(host) {
    A.googleButton(host, { clientId: health.google_client_id, body: () => ({ session_only: shared }),
      onResult: res => A.finish(res, { ...opts(), method: 'google' }),
      onError: x => UI.toast(errText(x, 'Google sign-in didn’t work. Try another way.')) }).catch(() => host.replaceChildren());
  }

  start();
})();
