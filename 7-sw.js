const SHELL = "nabd-shell-v1";
const ASSETS = ["./index.html", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== SHELL && k !== "nabd-data").map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.pathname.endsWith("data.json")) {
    e.respondWith(
      caches.open("nabd-data").then(async c => {
        try { const r = await fetch(e.request); c.put("./data.json", r.clone()); return r; }
        catch (err) { const hit = await c.match("./data.json"); if (hit) return hit; throw err; }
      })
    );
    return;
  }
  if (e.request.mode === "navigate" || ASSETS.some(a => url.pathname.endsWith(a.replace("./", "/")))) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      const cl = r.clone(); caches.open(SHELL).then(c => c.put(e.request, cl)); return r;
    })));
  }
});
