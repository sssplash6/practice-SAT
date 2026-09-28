/* SAT Freshman -- /sw.js, the notification-only service worker (shell-me.md U18b, §2.14 as
   replaced). It handles push and notificationclick; there is no fetch handler and no cache, so
   nothing is served offline (the shell's offline banner covers that). It is registered only
   when the student turns on "Notify me on this device" (UI.notify.on, or Settings' switch).

   Pushes carry no payload. The worker asks POST /api/push/next {endpoint} for the words, which
   the server works out from the Up next queue at send time, so they are never stale:
     {title, body (or text), url, kind, tag}      every field optional
   A tap opens url (default /?next=1&from=push, which starts Up next item 1). A tab already on
   that page is reused; any other tab is left alone, so a session or test is never navigated
   away. Every notification carries Stop: POST /api/push/stop {endpoint, kind} turns that kind
   off, and when that fails Settings › Study opens, where the switches are. */

const HOME = '/?next=1&from=push';
const SETTINGS = '/me/settings/#study';

// lifecycle only: a new worker takes over at once, and claims the open tabs so a tap can reuse one
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

async function post(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`${path} ${r.status}`);
  return r.status === 204 ? {} : r.json();
}
const endpoint = () => self.registration.pushManager.getSubscription().then(s => s && s.endpoint, () => null);

self.addEventListener('push', e => e.waitUntil((async () => {
  let d = {};
  try { d = (await post('/api/push/next', { endpoint: await endpoint() })) || {}; } catch (_) {}
  const kind = d.kind || 'study';
  // a push must always show something (userVisibleOnly): without words, the calendar feed's line
  await self.registration.showNotification(d.title || 'SAT Math · Up next', {
    body: d.body || d.text || 'Open to see what’s due now.',
    icon: '/assets/icon-192.png',
    tag: d.tag || kind,                       // one per kind: a newer one replaces the last
    data: { url: d.url || HOME, kind },
    actions: [{ action: 'stop', title: 'Stop' }],
  });
})()));

async function open(url) {
  const to = new URL(url, self.location.origin);
  const tabs = await self.clients.matchAll({ type: 'window' });
  const same = tabs.find(c => new URL(c.url).pathname === to.pathname);
  if (same) {
    try { await same.focus(); await same.navigate(to.href); return; } catch (_) {}
  }
  await self.clients.openWindow(to.href);
}

self.addEventListener('notificationclick', e => {
  const n = e.notification;
  const { url, kind } = n.data || {};
  n.close();
  e.waitUntil(e.action === 'stop'
    ? endpoint().then(ep => post('/api/push/stop', { endpoint: ep, kind })).catch(() => open(SETTINGS))
    : open(url || HOME));
});
