# STATUS – grundke-it.de Website
<!-- CI 2026.01 · Grundke IT-Service · Standard-Statusdatei, wird von Mensch+KI gepflegt -->

**Stand:** 2026-08-01 · **Status:** Live

## Was ist das
grundke-it.de Website – siehe README/CLAUDE.md im Projekt.

## Aktueller Stand
Live. Letzter Arbeitsblock (01.08.2026):

- **Seitenkopf war auf JEDER Seite kaputt** – aufgefallen an /fernwartung, betraf aber alle
  21 Seiten. Ursache: `nav { position:fixed }` in `style.css` war ein blanker Element-Selektor
  und traf damit auch `<nav class="foot-legal">` im Fuss (seit Commit dc4eb51 semantisch als
  `nav` ausgezeichnet) sowie `<nav class="tree-legal">` auf /tree/. Die Rechtslinks wurden
  dadurch oben festgepinnt und haben Logo und Hauptmenue verdeckt. Regel auf
  `.site-header nav` eingegrenzt. Gegengeprueft: Kopf fix, Fuss im Fluss, /tree/ in Ordnung.
- **/fernwartung neu aufgebaut** in der Bildsprache der uebrigen Seiten: Eyebrow + `s-title` +
  `s-sub`, Download als eigene Handlungs-Karte statt versteckt im ersten Schritt, Schritte als
  nummerierte Liste mit Verbindungslinie, Hilfe-Karte mit Telefon/WhatsApp, Vertrauens-Pillen,
  Sticky-Kontaktleiste wie ueberall. Emoji-Icons durch SVG ersetzt.
- **Inhaltlich korrigiert:** die Zusagen „Sitzung endet automatisch" und „kein dauerhafter
  Zugriff" stimmen nicht mehr – der Helper installiert RustDesk seit v3.24 als Dienst, der
  Zugang bleibt bestehen. Ersetzt durch „Du siehst die ganze Sitzung mit" und „Zugang wird auf
  Zuruf wieder entfernt".
- Geprueft bei 390 und 1440: kein horizontaler Scroll, Download-Knopf 293x56 px auf Mobil.

Davor (27.07.2026, Commit f331e57):

- **Kanonische Domain = non-www** (`https://grundke-it.de`). Vorher zeigten canonical, og:url,
  sitemap.xml, robots.txt, llms.txt und die vCard auf `www.`, das per 301 auf die Apex-Domain
  weiterleitet. 292 URLs umgestellt, `tools/build_landingpages.py` mitgezogen.
- **Hero-Slider lädt nur noch Slide 1** (60 KB statt 967 KB). Slides 2–5 tragen `data-bg`,
  `loadBg()` in `assets/js/main.js` lädt beim Wechsel, Slide 2 im Leerlauf nach dem load-Event.
  Alle Hero-WebPs neu encodiert: 967 KB → 581 KB gesamt.
- **Logo** 97 KB PNG → 17 KB WebP mit PNG-Fallback (`<picture>`), auf allen 21 Seiten.
- **Touch-Ziele 44 px**: Hamburger, Slider-Punkte (Trefferfläche via `::before`), Info-Buttons.
- Geprüft bei 390/768/1440: kein horizontaler Scroll, keine Konsolenfehler, live verifiziert.

## Nächster Schritt
- Search Console + Bing: non-www-Property prüfen, Sitemap `https://grundke-it.de/sitemap.xml`
  neu einreichen; GBP/Verzeichnisse auf non-www ziehen (Cowork/Browser-Arbeit).
- Offen zur Entscheidung: Hero-Karussell → statisches Hero, Cyan-Kontrast, DSGVO-Statistik.

## Blocker
(keine)

---
*Regel: Diese Datei bei jedem Arbeitsblock aktualisieren – sie füttert Mission Control und Jarvis.*
