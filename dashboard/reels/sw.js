/* Reels service worker — offline reading of the last-loaded deck.
 *
 * Strategy:
 *   - JSON (reels.json, world/brief/archive) -> network-first (no-store), cache the copy,
 *     fall back to cache when offline. Keeps the deck fresh but readable on the commute.
 *   - Everything else (shell, glossary, icons) -> stale-while-revalidate.
 * Bump CACHE on shell changes.
 */
const CACHE = "reels-v1";
const SHELL = ["./", "./index.html", "./manifest.json", "../glossary.js",
               "./icon-192.png", "./icon-512.png", "./icon-180.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.allSettled(SHELL.map(u => c.add(u)))));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const isJSON = new URL(req.url).pathname.endsWith(".json");

  if (isJSON) {
    // network-first: never serve a stale deck when we're online
    e.respondWith(
      fetch(req, { cache: "no-store" }).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req, { ignoreSearch: true }))
    );
  } else {
    // stale-while-revalidate: instant shell, refreshed in the background
    e.respondWith(
      caches.match(req, { ignoreSearch: true }).then(hit => {
        const refresh = fetch(req).then(res => {
          caches.open(CACHE).then(c => c.put(req, res.clone()));
          return res;
        }).catch(() => hit);
        return hit || refresh;
      })
    );
  }
});
