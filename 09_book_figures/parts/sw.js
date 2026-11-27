// Offline copy of the parts catalogue. It does nothing until the reader asks for an offline copy on the page ("Save for
// offline use"); that creates the cache below, and from then on this worker answers the page's requests from it when the
// network is not there. Without the cache every request goes straight to the network, as if there were no worker.
// The cache name is the same one offline.js uses; change both when the models or the pictures change.
const CACHE = 'c172-parts-v1';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));

self.addEventListener('fetch', (event) => {
  const request = event.request, url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;
  event.respondWith(answer(request, url));
});

async function answer(request, url) {
  // "Update the offline copy" asks the network on purpose, so that a saved picture is not simply saved again.
  if (request.headers.has('x-parts-refresh') || !(await caches.has(CACHE))) return fetch(request);
  const cache = await caches.open(CACHE);
  // Pictures and models do not change under the same name: the saved copy first. Everything else, the network first, so a
  // new version of the page is seen when there is a connection, and the saved copy when there is not.
  if (/\.(webp|glb|png|jpe?g|svg|woff2?)$/i.test(url.pathname)) {
    const saved = await cache.match(request);
    if (saved) return saved;
    try { const response = await fetch(request); if (response.ok) cache.put(request, response.clone()); return response; } catch { return Response.error(); }
  }
  try { const response = await fetch(request); if (response.ok) cache.put(request, response.clone()); return response; }
  catch { return (await cache.match(request, { ignoreSearch: true })) || Response.error(); }
}
