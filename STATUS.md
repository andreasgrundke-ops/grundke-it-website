# STATUS – grundke-it.de Website
<!-- CI 2026.01 · Grundke IT-Service · Standard-Statusdatei, wird von Mensch+KI gepflegt -->

**Stand:** 2026-10-18 · **Status:** Live

## Was ist das
grundke-it.de Website – siehe README/CLAUDE.md im Projekt.

## Aktueller Stand
18.10.2026: Release 2.1.0 „Hero“ (Hero „Ein Weg“: vier Beispiele, echte Stimme, Link Betreuerwechsel; Chat-Handy im Abschnitt IT-Betreuung), enthält 2.0.1 (Abschnitt „So arbeite ich“ statt Systemhaus-Vergleich, FAQ-Passungsfrage, KI-Kennzeichnung im Abschluss); davor 2.0.0 (ruhigere Optik, Dock neu, Version im Fuß, Stundensatz-Wortlaut).

- **Versionen:** `sw.js` `CACHE_NAME` `grundke-it-v2.1.0`, `RUNTIME_CACHE` `runtime-v39`, `ASSET_VER` 2026.10.i,
  `SITE_VERSION` 2.1.0 (Fuß „Version x.y.z · Stand TT.MM.JJJJ“ aus dem Generator). `SITE_VERSION` bei jedem
  Release mit dem `CACHE_NAME`-Suffix gleichziehen; `check_static.py` prüft das.
- **Kontaktleiste (Dock):** eine Quelle im Generator (`STICKY`-Marken), nur bis 1279 px sichtbar, ab 1280 px
  ausgeblendet; nie in einzelnen Dateien ändern.
- **Typo:** `body.is-home` trägt die größere Schriftskala der Startseite; Unterseiten bewusst ohne.
- **Stundensatz:** Wortlaut einheitlich „110 € netto zzgl. MwSt.“ (`HOME_PRICE_LINES` in `check_static.py`).
- **Struktur seit 10.–12.10.2026:** Startseite am Handy rund 10.300 px (Lighthouse 100/100/100/100, LCP 828 ms,
  CLS 0,01). Alle 26 Generator-Seiten in einer Hülle (`render_shell` in `tools/build_landingpages.py`: Kopf,
  Abschnitte im Wechsel, FAQ seitlich, Abschluss `closing()`), Seitenstile in `style.css`, Font-Preload gegen
  Layout-Shift. Schulung, Kontakt, Fernwartung, Rechtsseiten und 404 in der neuen Hülle; `sync_shared()`
  schreibt Abschluss und Font-Preload auch in die Handseiten. Interne Dateien (`tools/`, `*.md`, `Audit 2026-04/`)
  gehen nicht ins Pages-Artefakt (`deploy.yml`).
- **Inhalte:** `/empfehlungen/` mit Einrichtungs-Pauschalen (Richtwerte „ca.“); Hero-Chat zeigt abends und am
  Wochenende 20–40 Minuten bis zur Antwort; Barrierefreiheitserklärung beschreibt Chat, Pause-Knopf und
  Wischleiste. Service Worker cached nur erfolgreiche Antworten und leitet offline auf die Startseite.
- **Prüfwerkzeuge** in `tools/checks/` (Verzeichnis nicht im Deploy, `check_static.py --ci` läuft vor dem
  Upload und stoppt den Deploy bei Fehlern): `check_static.py` (Zusagewörter, Seitendaten, Pre-Cache,
  Rechtstexte gegen Basis-Commit, Versionen), `check_site.py` (Länge ≤ 8.000 px bei 390, erster Bildschirm,
  Überlauf), `check_seo.py` (Parität zu `../_intern/messungen/vorher`, Ausnahmen in
  `../_intern/messungen/seo-ausnahmen.json`), `check_visual.py` (Startseite pixelgleich), neu
  `check_design.py` (`--release r1`, `--heights --baseline`) und `check_sw.py` (`--upgrade`).
  Python 3.13 mit Playwright.

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
- KI-Sichtbarkeit (Recherche 17.10.2026, `../_intern/reports/Gelbe Seiten KI Check Vergleich.md`): Lücken liegen off-site. 1) Google-Unternehmensprofil vervollständigen, 2) mehr Bewertungen mit Text, 3) Bing Places + einheitliche NAP in Gelbe Seiten, Das Örtliche, 11880, Apple Business Connect, LinkedIn, 4) Erwähnungen auf Drittseiten (Partner, Referenzen, lokale Presse), 5) eigene Messung: festes Fragenset, mehrere Läufe je KI (ChatGPT, Google AI, Gemini, Copilot, Perplexity), Nennungsanteil vierteljährlich. Prüfmodul dafür im MSP Manager geplant.
- Medien: Motion Graphics und Erklärvideo über `motion-video`/Higgsfield möglich, Credits vorher freigeben lassen (Gehirn-Regel medien-motion-higgsfield-elevenlabs).
- Bing Webmaster Tools (Andreas, im Browser): Seite verifiziert? Sitemap `https://grundke-it.de/sitemap.xml` eingereicht? Startseite per URL-Prüfung testen. Stand im Repo nicht sichtbar.
- Search Console prüfen: um den 24.10. und den 07.11.2026 (zwei und vier Wochen nach dem Umbau).
- Ortsseiten: eigene Fakten und FAQ, sobald die Angaben vorliegen (Entwurf intern).
- Längenbudgets sind fast voll (`#preise` bei 390 px: 4.983 von 5.000; Startseite `#schnellcheck`,
  software-nach-mass, ki-dsgvo, empfehlungen > 96 %): neue Texte dort nur mit Kürzung an anderer Stelle.
- GitHub Actions auf Versionen ohne Node-20-Warnung heben.
- Offen: Linux-Fernwartung auf echtem Mint testen; AGB-PDF von 2024 aktualisieren.

## Blocker
(keine)

---
*Regel: Diese Datei bei jedem Arbeitsblock aktualisieren – sie füttert Mission Control und Jarvis.*
