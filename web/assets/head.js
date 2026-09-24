// Runs in <head>, before first paint (Shell 2.13, U23, G9).
(function () {
  var d = document.documentElement, l = {};
  // 1. Theme, text size and motion from localStorage satf.look (ui.js mirrors prefs there,
  //    non-default values only), so a dark page never flashes light.
  try { l = JSON.parse(localStorage.getItem('satf.look') || '{}') || {}; } catch (e) {}
  try {
    var dark = l.theme === 'dark' || (l.theme === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
    if (l.theme === 'dark' || l.theme === 'system') d.dataset.theme = dark ? 'dark' : 'light';
    if (l.text === 'small' || l.text === 'large') d.dataset.text = l.text;
    if (l.motion === 'reduce') d.dataset.motion = 'reduce';
    var tc = document.querySelector('meta[name="theme-color"]');
    if (tc && dark) tc.content = '#1A1917';
  } catch (e) {}

  var s = function (type, text) { var el = document.createElement('script'); if (type) el.type = type; el.textContent = text; return el; };

  // 2. Page transitions (G9). Chromium checks the new page's opt-in before it has read ui.css,
  //    so the opt-in is inline here; a skipped or interrupted transition rejects its promises,
  //    which are caught so they never reach the console (F1 follow-up).
  try {
    var st = document.createElement('style');
    st.textContent = l.motion === 'reduce' ? '@view-transition{navigation:none}'
      : '@view-transition{navigation:auto}@media (prefers-reduced-motion:reduce){@view-transition{navigation:none}}';
    document.head.appendChild(st);
    var quiet = function (e) {
      var t = e.viewTransition, n = function () {};
      if (t) [t.ready, t.finished, t.updateCallbackDone].forEach(function (p) { if (p) p.catch(n); });
    };
    addEventListener('pagereveal', quiet);
    addEventListener('pageswap', quiet);
  } catch (e) {}

  // 3. Prerender a same-origin link on hover or pointerdown (U23), except pages whose load
  //    starts something or signs someone in. UI.api holds writes until activation.
  try {
    if (HTMLScriptElement.supports && HTMLScriptElement.supports('speculationrules')) {
      var no = ['/practice/session/', '/test/', '/signin/', '/link/', '/admin/', '/api/'];
      var hrefs = [];
      no.forEach(function (p) { hrefs.push(p + '*', p + '*\\?*'); });
      document.head.appendChild(s('speculationrules', JSON.stringify({ prerender: [{
        source: 'document', eagerness: 'moderate',
        where: { and: [
          { href_matches: '/*' },
          { not: { href_matches: hrefs } },
          { not: { href_matches: '/*\\?*(^|&)next=*' } },
          { not: { selector_matches: '[data-noprerender], [data-noprerender] *' } }
        ] }
      }] })));
    }
  } catch (e) {}
})();
