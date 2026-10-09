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
 *   1.1.0 / 2026-08-01 — Cache-Versionen erhoeht. Ohne das behielt jeder
 *                        wiederkehrende Besucher das alte style.css: statische
 *                        Dateien laufen Cache-First, und die Cache-Namen waren
 *                        seit April unveraendert. Der Kopfzeilen-Fix vom
 *                        01.08.2026 lag deshalb zwar auf dem Server, kam aber
 *                        nicht an. Regel steht oben — bei JEDEM Release beide
 *                        Namen erhoehen.
 *   1.1.1 / 2026-08-02 — Position der Ortspille in der Kopfzeile vereinheitlicht
 *                        (style.css), deshalb erneut erhoeht.
 *   1.2.0 / 2026-08-22 — KI-Bereich ergaenzt (vier neue Seiten, neue Navigation,
 *                        geaenderte Startseite). Cache-Versionen erhoeht, sonst
 *                        sieht ein wiederkehrender Besucher die alte Navigation
 *                        ohne den Punkt "KI im Betrieb".
 *   1.2.1 / 2026-08-22 — Umschaltpunkt der Kopfzeile korrigiert (style.css +
 *                        index.html), deshalb erneut erhoeht.
 *   1.2.2 / 2026-08-22 — In der Kopfzeile weicht jetzt die Ortspille statt des
 *                        Menues (index.html), deshalb erneut erhoeht.
 *   1.3.0 / 2026-08-29 — Unverlinkte Seite /ki-arbeitsplatz-onboarding-kit/
 *                        dazugekommen (Arbeitsbuch zum Onboarding). Bewusst
 *                        NICHT im Pre-Cache: die Seite bekommt nur, wer den
 *                        Link hat - sie gehoert nicht auf jedes Geraet.
 *                        Cache-Versionen trotzdem erhoeht, weil robots.txt
 *                        mitgeaendert wurde.
 *   1.3.1 / 2026-09-11 — Kundenstimmen auf der Startseite ueberarbeitet: vierte
 *                        Google-Rezension ergaenzt, Direktstimme Blumenschein
 *                        dazu, zwei Zitate auf den Google-Wortlaut gezogen
 *                        (index.html). Die Seite selbst laeuft zwar
 *                        Network-First und kaeme auch so an, aber '/' und
 *                        '/index.html' liegen im Pre-Cache: ohne Erhoehung
 *                        bleibt die Offline-Kopie auf dem alten Stand.
 *   1.4.0 / 2026-09-23 — Eine Navigation und ein Footer fuer alle Seiten
 *                        (Generator schreibt beides auch in Startseite und
 *                        handgebaute Seiten), aktiver Menuepunkt, Brotkrumen,
 *                        FAQ als Akkordeon, Einstieg fuer den KI-Hub, gemeinsame
 *                        Buttons, style.css geaendert, Inhaltskorrekturen,
 *                        Datenschutzerklaerung ergaenzt.
 *   1.18.0 / 2026-10-02 — Hero der Startseite neu: Chat statt Foto-Slider.
 *   1.19.0 / 2026-10-02 — Hero-Chat in Kundensicht mit Tastatur, neue Faelle.
 *                        Neue Datei assets/js/hero-chat.js (im Pre-Cache),
 *                        Slider-Code aus main.js und style.css entfernt.
 *   1.20.0 / 2026-10-03 — Hero-Chat: Handy-Ansicht ohne unsichtbares Tippen,
 *                        kein Nachholen nach gedrosselten Timern.
 *   1.21.0 / 2026-10-03 — Pre-Cache mit cache:'reload' (nicht mehr aus dem
 *                        HTTP-Cache), Runtime-Cache vor Pre-Cache lesen, damit
 *                        Background-Updates auch ausgeliefert werden.
 *   1.22.0 / 2026-10-07 — Konzept „Sichtbarkeit und Wachstum“: Startseite mit
 *                        Kernsatz und vier Einstiegen, neue Seiten (Software,
 *                        Websites, IT-Betreuer wechseln, E-Rechnung, Digitalbonus,
 *                        Lizenzen, Ratgeber), neues Menue und Fuss, style.css
 *                        (Kontraste) und hero-chat.js geaendert.
 *   1.22.1 / 2026-10-07 — Praxisbeispiele: Videoueberwachung mit KI (Fahrzeuge,
 *                        Kennzeichen), Fallbeispiel E-Rechnung aus CSV entfernt.
 *   1.22.2 / 2026-10-09 — Hero der Startseite ohne die vier Einstiege (nur noch
 *                        der Chat), Fernwartung mit Umschalter Windows/Linux/macOS
 *                        (neue Datei assets/js/fernwartung.js), TeamViewer aus dem Menue.
 *   1.22.3 / 2026-10-09 — Website-Preise: One-Pager neu, Richtwerte 800/1.300/2.000 €,
 *                        Betrieb optional 40 €/Monat.
 *   1.22.4 / 2026-10-09 — IT-Notdienst und Kontakt: Fernwartung ueber eigenen Server
 *                        statt TeamViewer beschrieben.
 *   1.22.5 / 2026-10-09 — Fernwartung ohne TeamViewer-Ausweichlink, Datenschutz
 *                        nennt GitHub (RustDesk fuer den Mac) statt TeamViewer.
 *   1.23.0 / 2026-10-09 — Sofort-Reparatur: Schulungs-Knoepfe (Bausteine in style.css),
 *                        404 mit Schriften, Kartenabstand, Fernwartung als Menuepunkt
 *                        (main.js 1.4.0), Bilder fuer die E-Mail-Signatur.
 */

const CACHE_NAME    = 'grundke-it-v1.23.0';
const RUNTIME_CACHE = 'grundke-it-runtime-v29';

/* Pre-Cache: minimaler Kern fuer Offline-First-Boot */
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/404.html',
  '/site.webmanifest',
  '/assets/css/style.css',
  '/assets/css/fonts.css',
  '/assets/js/main.js',
  '/assets/js/hero-chat.js',
  '/assets/js/lenis.min.js',
  '/assets/img/logo-grundke-it-white.png',
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
      /* cache:'reload' umgeht den HTTP-Cache (max-age=600): sonst landet direkt
         nach einem Release die alte Datei im neuen Pre-Cache */
      .then(cache => cache.addAll(PRECACHE_URLS.map(u => new Request(u, { cache: 'reload' }))).catch(err => {
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

  /* Static Assets -> Cache-First mit Background-Update.
     Zuerst im Runtime-Cache suchen: dorthin schreibt das Background-Update.
     Vorher gewann immer die Pre-Cache-Kopie, Updates kamen nie an. */
  event.respondWith(
    caches.open(RUNTIME_CACHE)
      .then(c => c.match(req))
      .then(hit => hit || caches.match(req))
      .then(cached => {
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
