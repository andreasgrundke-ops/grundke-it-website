# CLAUDE.md — Grundke-IT-Website

> Teil des Workspace `00_KI_Work` · Strang **02_GIT** · Router + globaler Kontext: Root-Master `00_KI_Work\CLAUDE.md` (§0 Projekt-Router).

## Zweck
Eigene Firmen-Website Grundke IT-Service, live unter https://grundke-it.de.
Zwei Saeulen: klassische IT-Betreuung fuer KMU im Raum Muenchen Ost und (seit 08/2026)
KI-Anwendungen fuer den Betrieb.

## Stack / Technik
- Statisches HTML, Vanilla CSS + JS, kein Framework. Dark Mode, PWA-faehig.
- **GitHub Pages**, Deploy durch `git push origin main`. Startseite `Cache-Control: max-age=600`,
  Live-Verifikation deshalb erst nach Build plus bis zu 10 Minuten CDN-Cache.
- **Kanonische Domain: non-www** (`https://grundke-it.de`). Neue URLs immer non-www schreiben.
- `assets/css/style.css` ist gemeinsam, seitenspezifische Styles liegen inline im `<style>`-Block.

### Die zwei Dinge, die man vorher wissen muss
1. **`tools/build_landingpages.py` ist die Single Source of Truth** fuer alle Orts-, Leistungs-
   und KI-Seiten (aktuell 15 Stueck) sowie fuer `sitemap.xml`. Diese `index.html`-Dateien
   niemals von Hand aendern, sondern die Datenlisten `PLACES`/`SERVICES` pflegen und
   `python tools/build_landingpages.py` laufen lassen. Handgebaut sind nur: Startseite,
   kontakt, schulung, fernwartung, empfehlungen, tree, ki-arbeitsplatz-onboarding-kit,
   404 und die Rechtsseiten.
   **Navigation und Footer (`<header class="site-header">`, `<footer class="site-footer">`)
   kommen seit 23.09.2026 fuer ALLE Seiten aus dem Generator** (`NAV_ITEMS`/`nav_html`,
   `footer_html`); `sync_shared()` schreibt beides auch in die Startseite und die handgebauten
   Seiten (`HAND_PAGES`). Nie in einer einzelnen Datei aendern — bis dahin gab es vier
   Menue- und fuenf Footer-Varianten.
2. **Bei JEDEM Release `CACHE_NAME` und `RUNTIME_CACHE` in `sw.js` erhoehen.** Statische
   Dateien laufen Cache-First; ohne Erhoehung sieht ein wiederkehrender Besucher weiter die
   alte Version, obwohl der Deploy durch ist. Das ist hier schon zweimal passiert.

### Unverlinkte Seiten
`/tree/` und `/ki-arbeitsplatz-onboarding-kit/` sind **bewusst nicht verlinkt**: kein Eintrag in
Navigation, Footer oder `sitemap.xml`, `<meta name="robots" content="noindex, nofollow">` im Kopf und
`Disallow` in `robots.txt` fuer alle Crawler einschliesslich der KI-Bots. Wer den Link hat, kommt
ohne Zugangsdaten hinein — das ist so gewollt, ist aber **kein Zugriffsschutz**. Das Repo ist public,
die Dateien sind also auch ueber github.com sichtbar. Deshalb dort nur Material, das oeffentlich
unbedenklich ist: keine Kundennamen, keine Projektdaten, keine internen Notizen.

`/ki-arbeitsplatz-onboarding-kit/` ist das Arbeitsbuch zum Onboarding neuer Claude-Nutzer
(zwoelf Phasen, abhakbar, Fortschritt im localStorage des Besuchers). Downloads liegen unter
`ki-arbeitsplatz-onboarding-kit/dateien/`. Die URL bleibt **ohne Versionsnummer** stabil; die
Version steht nur in der Fusszeile, damit sich der Link jederzeit weitergeben laesst und Aenderungen
ohne neue URL moeglich sind. Nicht in den Pre-Cache von `sw.js` aufnehmen.

Weitere Konventionen: FAQ-Texte stehen doppelt (sichtbar und im FAQPage-JSON-LD) und muessen
zeichengleich bleiben; dasselbe gilt fuer die Kundenstimmen und ihre `reviewBody`-Eintraege im
LocalBusiness-Schema. Bewertungen werden **wortgetreu** zitiert — nicht kuerzen, nicht glaetten,
und die Quelle unter der Karte muss stimmen (`Google-Bewertung` nur, wenn sie dort wirklich steht). `dateModified` nur hochsetzen, wenn sich der Inhalt der Seite wirklich
geaendert hat, nicht wegen eines neuen Footer-Links.

## Stand / offen / naechster Schritt
- **Stand:** 23.09.2026 — Seite aus einem Guss: ein Menue (IT-Schnellcheck · IT-Service ·
  KI im Betrieb · Schulungen · Preise · Fernwartung · Kontakt · Anrufen) und ein Footer fuer
  alle Seiten, aktiver Punkt per `aria-current`, Brotkrumen, FAQ als Akkordeon, Buttons
  `.btn-p`/`.btn-g` ueberall, KI-Hub mit eigenem Einstieg (`hero` im SERVICES-Eintrag),
  Querverweise zwischen den KI-Seiten, Pfeil-Glyphe repariert (war Oktal-Escape), `/tree/`
  nirgends mehr verlinkt, Inhaltskorrekturen aus dem Audit (Radius 25 km, netto an Preisen,
  TDDDG, Sitemap-lastmod). Ortspille weicht zwischen 1024 und 1239 px jetzt auf allen Seiten.
  Danach Inhaber-Entscheidungen eingearbeitet: nur Geschaeftskunden, KEINE garantierten
  Reaktionszeiten, „KI datenschutzgerecht einsetzen", „planbare Monatspauschale", Anfahrt
  bis 5 km inklusive, Monatsreport nur Premium, Erreichbarkeit im Schema taeglich, KI-Modul in
  der Schulung, Art. 4 KI-VO nach Digital Omnibus (VO (EU) 2026/1744), Datenschutzerklaerung
  um Amazon-Partnerprogramm, Fernwartungs-Download, Service Worker und localStorage ergaenzt.
  `sw.js` 1.16.0 / runtime v16.
  Davor 11.09.2026 — Kundenstimmen der Startseite auf fuenf erweitert und auf den Wortlaut
  gezogen: vier Google-Rezensionen plus eine direkt uebermittelte Stimme (Blumenschein,
  Steuerberatung — dort bewusst **ohne** das Label „Google-Bewertung"). `reviewCount` im Schema
  auf 5, Testimonial-Raster auf feste Spalten. `sw.js` 1.15.0 / runtime v15.
  Davor 29.08.2026 — Unverlinkte Seite `/ki-arbeitsplatz-onboarding-kit/` gebaut: Arbeitsbuch
  zum Onboarding neuer Claude-Nutzer, zwoelf Phasen abhakbar, dazu sieben Downloads unter
  `dateien/`. `robots.txt` und `sw.js` mitgezogen, Seite bewusst nicht in `sitemap.xml`.
  Davor 22.08.2026 — KI-Bereich als zweite Saeule (Hub `/ki-fuer-kmu/` plus drei Unterseiten,
  Startseiten-Sektion, Navigation, llms.txt), inzwischen gepusht und live.
- **Offen:** Hetzner-AVV pruefen (accounts.hetzner.com/account/dpa). KI-URLs sind seit
  23.09.2026 zur Indexierung beantragt; das Arbeitsbuch dort ausdruecklich **nicht** einreichen.
- **Naechster Schritt:** siehe `STATUS.md` — dort steht der vollstaendige Arbeitsstand.

*CI 2026.01 · Grundke IT-Service · www.grundke-it.de*
