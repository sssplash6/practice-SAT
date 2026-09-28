/* ============================================================================
   SAT Freshman -- account pieces shared by /me/, /me/settings/, /signin/ and /pair/
   (Shell 1, 4.4, 5; shell-me U11, U19, U19b, U20, U21, U22, U29). Loaded after ui.js
   and kit.js; adds UI.acct. The server is account.py and api_me.py.

   UI.acct.passkeyReady() -> Promise<bool>     a platform authenticator (Face ID, Windows Hello)
   UI.acct.savePasskey()  -> Promise<result>   register one; this browser swaps to its d: token
   UI.acct.passkeyGet({conditional, signal}) -> Promise<assertion body>
   UI.acct.saveMe(body)   -> Promise<profile>  PUT /api/me, then the shell refreshes
   UI.acct.finish(res, {method, shared, local}) the carry choice (U19), adopt, toast, go to /
   UI.acct.localAnswers() -> {answers, since, fresh}   what this browser holds before a sign-in
   UI.acct.countrySelect(value, onChange) -> el        ISO alpha-2, blank by default (U11)
   UI.acct.nameError(e) / UI.acct.handleError(e)       the server's refusal, in words
   UI.acct.deviceLabel()                               "Chrome on Mac"
   ========================================================================== */
(() => {
  'use strict';
  const h = UI.h;
  const N = n => UI.num(n);
  const ls = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { if (v === null || v === undefined) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); } catch (_) {} },
  };
  const b64u = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const unb64u = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), c => c.charCodeAt(0));

  // the server's own list (api_me.COUNTRIES), so a pick is never refused
  const COUNTRIES = ('AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ ' +
    'CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE ' +
    'GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP ' +
    'KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF ' +
    'NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN ' +
    'SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ' +
    'ZM ZW').split(' ');
  let names = null;
  const countryName = code => {
    try { names = names || new Intl.DisplayNames([navigator.language || 'en', 'en'], { type: 'region' }); return names.of(code) || code; }
    catch (_) { return code; }
  };
  const regionGuess = () => {
    try { const r = new Intl.Locale(navigator.language || 'en').maximize().region; return COUNTRIES.includes(r) ? r : null; }
    catch (_) { return null; }
  };

  function deviceLabel() {
    const ua = navigator.userAgent || '';
    const browser = /Edg\//.test(ua) ? 'Edge' : /OPR\//.test(ua) ? 'Opera' : /Firefox\//.test(ua) ? 'Firefox'
      : /Chrome\//.test(ua) ? 'Chrome' : /Safari\//.test(ua) ? 'Safari' : 'Browser';
    const os = /iPhone/.test(ua) ? 'iPhone' : /iPad/.test(ua) ? 'iPad' : /Android/.test(ua) ? 'Android' : /CrOS/.test(ua) ? 'Chromebook'
      : /Windows/.test(ua) ? 'Windows' : /Mac OS X|Macintosh/.test(ua) ? 'Mac' : /Linux/.test(ua) ? 'Linux' : '';
    return os ? `${browser} on ${os}` : browser;
  }

  /* ---- passkeys (U19): SPKI from getPublicKey(), so the server needs no CBOR */
  async function passkeyReady() {
    try { return !!(window.PublicKeyCredential && await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()); }
    catch (_) { return false; }
  }
  async function savePasskey() {
    const o = await UI.api('/passkey/register/options', { method: 'POST', body: {} });
    const cred = await navigator.credentials.create({ publicKey: {
      challenge: unb64u(o.challenge), rp: o.rp,
      user: { id: unb64u(o.user.id), name: o.user.name, displayName: o.user.displayName },
      pubKeyCredParams: o.pubKeyCredParams, authenticatorSelection: o.authenticatorSelection,
      timeout: o.timeout, attestation: 'none' } });
    const r = cred.response;
    if (!r.getPublicKey || !r.getAuthenticatorData) throw new Error('This browser can’t save a passkey here.');
    const res = await UI.api('/passkey/register', { method: 'POST', body: {
      id: cred.id, clientDataJSON: b64u(r.clientDataJSON), authData: b64u(r.getAuthenticatorData()),
      publicKey: b64u(r.getPublicKey()), algorithm: r.getPublicKeyAlgorithm(),
      transports: r.getTransports ? r.getTransports() : [], label: deviceLabel() } });
    if (res && res.credential) UI.useLearner(res.credential, { same: true });
    UI.refresh();
    return res;
  }
  async function passkeyGet({ conditional = false, signal } = {}) {
    const o = await UI.api('/passkey/login/options', { method: 'POST', body: { conditional } });
    const cred = await navigator.credentials.get({ mediation: conditional ? 'conditional' : undefined, signal,
      publicKey: { challenge: unb64u(o.challenge), rpId: o.rpId, allowCredentials: [], userVerification: 'preferred', timeout: o.timeout } });
    const r = cred.response;
    return { expires: o.expires, body: { id: cred.id, clientDataJSON: b64u(r.clientDataJSON),
      authenticatorData: b64u(r.authenticatorData), signature: b64u(r.signature) } };
  }

  /* ---- the profile */
  async function saveMe(body) {
    const r = await UI.api('/me', { method: 'PUT', body });
    UI.refresh();
    return r.profile;
  }
  const detail = e => String((e && (typeof e.detail === 'string' ? e.detail : e.message)) || '');
  const nameError = e => e && e.status === 422 ? 'Names can’t contain digits, @, < or >.' : 'Not saved. Try again.';
  const handleError = e => e && e.status === 409 ? 'Someone already has that board name.'
    : e && e.status === 422 ? '3 to 24 letters, digits, spaces, _ . or -, and not a reserved name.' : 'Not saved. Try again.';

  // a searchable select (typing jumps), blank by default, with the browser's region offered, never set (U11)
  function countrySelect(value, onChange) {
    const sel = h('select', { class: 'field', 'aria-label': 'Country' },
      h('option', { value: '', text: 'No country' }),
      COUNTRIES.map(c => [c, countryName(c)]).sort((a, b) => a[1].localeCompare(b[1]))
        .map(([c, n]) => h('option', { value: c, text: n })));
    sel.value = value || '';
    const guess = regionGuess();
    const chip = h('button', { type: 'button', class: 'btn sm', hidden: true });
    const clear = h('button', { type: 'button', class: 'quiet', text: 'Clear', hidden: true });
    const sync = () => {
      chip.hidden = !!sel.value || !guess;
      if (guess) chip.textContent = `${countryName(guess)}?`;
      clear.hidden = !sel.value;
    };
    const pick = async v => {
      const old = sel.value;
      sel.value = v;
      sync();
      try { await onChange(v); } catch (_) { sel.value = old; sync(); }
    };
    sel.addEventListener('change', () => pick(sel.value));
    chip.addEventListener('click', () => pick(guess));
    clear.addEventListener('click', () => pick(''));
    sync();
    return h('div', { class: 'country' }, sel, chip, clear);
  }

  /* ---- signing in: the carry choice (U19), then this browser adopts the credential */
  async function localAnswers() {
    try {
      const a = await UI.api('/me/activity?weeks=8', { quiet: true });
      const days = (a.days || []).filter(d => d.questions > 0);
      const total = a.total || 0;
      if (!total) return { answers: 0 };
      const last = days.length ? days[days.length - 1].day : null;
      return { answers: total, since: days.length ? days[0].day : null, fresh: last === a.today };
    } catch (_) { return { answers: 0 }; }
  }
  function flash(text) { try { sessionStorage.setItem('satf.flash', JSON.stringify({ text })); } catch (_) {} }
  function park(cred, n) {            // "Don't add them": the old code stays one tap away (U21)
    const list = ls.get('satf.profiles', []).filter(p => p.cred !== cred);
    list.push({ cred, name: `Student ${cred.slice(-4).toUpperCase()}`, answers: n, parked: true });
    ls.set('satf.profiles', list.slice(-4));
  }
  function carrySheet(local, name, preferAdd) {
    const since = local.since ? `, answered here since ${UI.date(local.since, 'short')}` : '';
    let add, skip;
    const s = UI.sheet({ title: 'Bring this device’s answers?', size: 's', dismiss: false,
      body: h('p', { text: `This device has ${N(local.answers)} answer${local.answers === 1 ? '' : 's'}${since}.` }),
      actions: [{ label: 'Don’t add them', onClick: () => 'no' },
                { label: `Add them to ${name ? `${name}’s` : 'this account'}`, primary: true, onClick: () => 'add' }] });
    const btns = s.foot ? [...s.foot.querySelectorAll('button')] : [];
    [skip, add] = btns;
    requestAnimationFrame(() => { const b = preferAdd ? add : skip; if (b) b.focus(); });
    return s.closed.then(v => v || 'no');
  }
  async function finish(res, o = {}) {
    const old = UI.learner();
    const shared = !!o.shared;
    const local = o.local || { answers: 0 };
    UI.useLearner(res.credential, { session: shared });
    let name = null;
    try { const me = await UI.api('/me'); name = me.profile.name || me.profile.handle || null; } catch (_) {}
    let added = 0, note = '';
    if (local.answers > 0 && old !== res.credential && !res.moved) {
      if (shared) note = ' · this computer’s answers stay separate';
      else if (await carrySheet(local, name, !!local.fresh) === 'add') {
        try { added = (await UI.api('/me/carry', { method: 'POST', body: { learner: old } })).moved || 0; }
        catch (_) { note = ' · the answers here weren’t added'; park(old, local.answers); }
      } else park(old, local.answers);
    }
    added = added || res.moved || 0;
    if (!shared && o.method) ls.set('satf.lastMethod', o.method);
    UI.cached.clear();
    flash(`Signed in${name ? ` as ${name}` : ''}${added ? ` · ${N(added)} answers added` : ''}${note}`);
    location.href = o.to || '/';
  }

  UI.acct = { COUNTRIES, countryName, regionGuess, deviceLabel, passkeyReady, savePasskey, passkeyGet,
    saveMe, nameError, handleError, detail, countrySelect, localAnswers, finish, flash, park, ls,
    HANDLE_OK: /^[A-Za-z0-9 _.\-]{3,24}$/, NAME_OK: /^[^\d<>@]{1,40}$/ };
})();
