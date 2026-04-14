/*
 * ═══════════════════════════════════════════════════════════
 * Grundke IT-Service · Service Worker
 * Version: 1.0.0
 * Autor: Andreas Grundke / Grundke IT-Service
 * Datum: 2026-04-11
 * ═══════════════════════════════════════════════════════════
 *
 * Strategie:
 *   - Static Assets (CSS, JS, Bilder, Fonts, Manifest, Icons)
 *     -> Cache-First, Background-Update
 *   - HTML-Navigation
 *     -> Network-First mit Cache-Fallback und 404.html als
 *        Offline-Fallback
 *
 * Cache-Versionierung ueber CACHE_NAME — bei jedem Release
 * den Suffix erhoehen, dann werden alte Caches beim activate
 * geloescht.
 *
 * Aenderungshistorie:
 *   1.0.0 / 2026-04-11 — Initial Release-2 PWA-Setup
 */

const CACHE_NAME    = 'grundke-it-v1.2.1';
const RUNTIME_CACHE = 'grundke-it-runtime-v2';

/* Pre-Cache: minimaler Kern fuer Offline-First-Boot */
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/404.html',
  '/site.webmanifest',
  '/assets/css/style.css',
  '/assets/css/fonts.css',
  '/assets/js/main.js',
  '/assets/js/lenis.min.js',
  '/assets/img/logo-grundke-it-badge.png',
  '/favicon.ico',
  '/favicon-32x32.png',
  '/favicon-16x16.png',
  '/apple-touch-icon.png',
  '/android-chrome-192x192.png',
  '/android-chrome-512x512.png'
];

/* ── Install: Pre-Cache befuellen ── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS).catch(err => {
        console.warn('[SW] Pre-Cache teilweise fehlgeschlagen:', err);
      }))
      .then(() => self.skipWaiting())
  );
});

/* ── Activate: alte Caches loeschen ── */
self.addEventListener('activate', event => {
  const allowList = [CACHE_NAME, RUNTIME_CACHE];
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => !allowList.includes(k))
            .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

/* ── Fetch: Routing ── */
self.addEventListener('fetch', event => {
  const req = event.request;

  /* nur GET behandeln, kein POST/PUT etc */
  if (req.method !== 'GET') return;

  /* Cross-Origin: durchreichen, nicht cachen */
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  /* Navigation (HTML-Seiten) -> Network-First */
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(req)
        .then(res => {
          /* erfolgreiche Antwort cachen */
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then(c => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req)
          .then(cached => cached || caches.match('/404.html'))
        )
    );
    return;
  }

  /* Static Assets -> Cache-First mit Background-Update */
  event.respondWith(
    caches.match(req).then(cached => {
      const networkFetch = fetch(req).then(res => {
        if (res && res.status === 200) {
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then(c => c.put(req, copy));
        }
        return res;
      }).catch(() => cached);
      return cached || networkFetch;
    })
  );
});

/* ── Message: erlaubt manuelles skipWaiting via postMessage ── */
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
