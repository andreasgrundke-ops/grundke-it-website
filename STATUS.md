# STATUS – grundke-it.de Website
<!-- CI 2026.01 · Grundke IT-Service · Standard-Statusdatei, wird von Mensch+KI gepflegt -->

**Stand:** 2026-10-12 · **Status:** Live

## Was ist das
grundke-it.de Website – siehe README/CLAUDE.md im Projekt.

## Aktueller Stand
Umbau „Ein Stil, der Kümmerer, Handy zuerst“ (10.–12.10.2026) ist vollständig live, Gesamtabnahme
mit Auflagen bestanden, Auflagen erledigt.

- **Release A – Startseite:** am Handy 10.316 px statt rund 20.000, Lighthouse 100/100/100/100
  (vorher 96/100/100/67). Interne Dateien (`tools/`, `*.md`,
  `Audit 2026-04/`) gehen nicht mehr mit ins Pages-Artefakt (`deploy.yml`).
- **Release B – 26 Generator-Seiten in einer Hülle** (`render_shell` in `tools/build_landingpages.py`):
  Kopf in fester Reihenfolge (Krumen, H1, K4, Antwortsatz, Knöpfe, Belege), Abschnitte im Wechsel,
  FAQ seitlich, Abschluss `closing()`. Alter Seitenweg (`SHELL_SLUGS`, `STYLE_LEGACY`, KI-/NEW-Styles,
  `author_box`, `cards_html`) entfernt, Seitenstile in `style.css`. Font-Preload (Manrope, Space
  Grotesk) gegen Layout-Shift beim ersten Aufruf.
- **Release C1 – Schulung, Kontakt, Fernwartung, Rechtsseiten, 404:** Schulung kommt aus dem
  Generator (Course-Schema unverändert, Portal „in Vorbereitung“, Sätze zum Portal als „geplant“).
  `sync_shared()` schreibt Abschluss und Font-Preload auch in die Handseiten. Fernwartung: Knöpfe
  `.btn-p/.btn-g`, Seitenspalte ab 1100 px, Platz des Umschalters vor dem Skript reserviert
  (CLS 0,103 → 0). Rechtsseiten nur neue Hülle, Text per AK14 gegen Commit 865b00a geprüft.
- **Release C2 (live 12.10.):** `/empfehlungen/` mit Einrichtungs-Pauschalen
  (Richtwerte „ca.“, Beispiele und Erfahrungswerte), Zubehör für den Arbeitsplatz, private Produkte entfallen.
  Dazu Fix-Runden aus dem Gesamt-Review: schärfere Prüfungen (Zusagewörter, Schlüssel der Seitendaten,
  H2-Ausnahmen je Seite, Pre-Cache-Dateien), ein Unternehmensknoten im Schema, Service Worker cached nur
  erfolgreiche Antworten und leitet offline auf die Startseite, `check_static.py --ci` läuft im Deploy.
- **Release C3 (live 12.10.):** Hero-Chat zeigt abends und am Wochenende 20–40 Minuten bis zur Antwort;
  Barrierefreiheitserklärung beschreibt Chat, Pause-Knopf und Wischleiste statt des alten Sliders.
- **Versionen:** `sw.js` 1.28.0 / runtime v36, `ASSET_VER` 2026.10.f. Messung live: Startseite LCP 828 ms,
  CLS 0,01 (vor dem Umbau 1.329 ms); Lighthouse-Stichproben 100/100/100/100.
- **Prüfwerkzeuge** in `tools/checks/` (Verzeichnis nicht im Deploy, `check_static.py --ci` läuft vor dem Upload): `check_static.py` (AK1–AK14),
  `check_site.py` (Länge ≤ 8.000 px bei 390, erster Bildschirm, Überlauf), `check_seo.py`
  (Parität zu `../_intern/messungen/vorher`, Ausnahmen in `../_intern/messungen/seo-ausnahmen.json`),
  `check_visual.py` (Startseite pixelgleich). Python 3.13 mit Playwright.

## Verlauf (kurz)
- 17.10.2026: Bing/IndexNow: `BingSiteAuth.xml` und IndexNow-Schlüsseldatei liegen live; `tools/indexnow.py` meldet die Sitemap-URLs (31) an IndexNow, erster Ping HTTP 200. Nach jedem Deploy mit neuen oder geänderten Seiten erneut laufen lassen (`python tools/indexnow.py`, nicht Teil des Builds).
- 09.10.2026: Hero nur noch Chat, Fernwartung mit Umschalter Windows/Linux/macOS, TeamViewer raus,
  Website-Preise neu (ca. 800 / 1.300 / 2.000 €, Betrieb optional 40 €/Monat).
- 07.10.2026: Konzept „Sichtbarkeit und Wachstum“: Software, Websites, IT-Betreuer wechseln,
  Lizenzen, E-Rechnung, Digitalbonus, Ratgeber; Preise über `PRICES`/`SHOW_FROM_PRICES`.
- 02./03.10.2026: Chat-Hero statt Slider; SW-Fix (`cache:'reload'` beim Install).
- 23.09.2026: ein Menü und ein Fuß für alle Seiten über den Generator (`sync_shared()`).
- 22.08.2026: KI als zweite Säule (vier KI-Seiten, `llms.txt`).
- 29.08.2026: unverlinktes Arbeitsbuch `/ki-arbeitsplatz-onboarding-kit/` (noindex, nicht im Pre-Cache).
- 01.08.2026: Regel eingeführt – bei jedem Release `CACHE_NAME` und `RUNTIME_CACHE` in `sw.js` erhöhen.
- 27.07.2026: kanonische Domain non-www.

## Nächster Schritt
- Bing Webmaster Tools (Andreas, im Browser): Seite verifiziert? Sitemap `https://grundke-it.de/sitemap.xml` eingereicht? Startseite per URL-Prüfung testen. Stand im Repo nicht sichtbar.
- Search Console prüfen: um den 24.10. und den 07.11.2026 (zwei und vier Wochen nach Release B).
- Ortsseiten: eigene Fakten und FAQ, sobald die Angaben vorliegen (Entwurf intern).
- Längenbudgets sind fast voll (Startseite `#schnellcheck`, `#preise`, software-nach-mass, ki-dsgvo,
  empfehlungen > 96 %): neue Texte dort nur mit Kürzung an anderer Stelle.
- GitHub Actions auf Versionen ohne Node-20-Warnung heben.
- Offen: Linux-Fernwartung auf echtem Mint testen; AGB-PDF von 2024 aktualisieren.

## Blocker
(keine)

---
*Regel: Diese Datei bei jedem Arbeitsblock aktualisieren – sie füttert Mission Control und Jarvis.*
