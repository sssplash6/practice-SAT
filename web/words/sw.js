/* SAT Freshman -- Words offline (words.md W22). Scoped to /words/; words-ui.js registers it
   when the student takes today's cards offline.

   Network first, so an online page is always fresh; when the network fails, the last copy.
   A page's query is ignored for the fallback, so /words/run/?id=… opens the cached runner,
   which reads its cards from IndexedDB. /api/ is never cached: the cards live in IndexedDB,
   and grades queue there until the signal comes back. */
const CACHE = 'satf-words-1';
const SHELL = ['/words/run/', '/words/', '/assets/ui.css', '/assets/runner.css', '/assets/head.js', '/assets/ui.js', '/assets/kit.js',
  '/assets/charts.js', '/assets/question.js', '/assets/words-ui.js', '/assets/mark.svg', '/manifest.webmanifest'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).catch(() => {}).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('satf-words-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request;
  const u = new URL(r.url);
  if (r.method !== 'GET' || u.pathname.startsWith('/api/')) return;
  const own = u.origin === self.location.origin;
  if (!own && !/^fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) return;
  const key = r.mode === 'navigate' ? u.origin + u.pathname : r;
  e.respondWith(fetch(r).then(res => {
    if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(key, copy)).catch(() => {}); }
    return res;
  }).catch(() => caches.match(key).then(hit => hit || caches.match(r, { ignoreSearch: true })).then(hit => hit || Response.error())));
});
