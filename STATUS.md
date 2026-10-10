# STATUS – grundke-it.de Website
<!-- CI 2026.01 · Grundke IT-Service · Standard-Statusdatei, wird von Mensch+KI gepflegt -->

**Stand:** 2026-10-10 · **Status:** Live

## Was ist das
grundke-it.de Website – siehe README/CLAUDE.md im Projekt.

## Aktueller Stand
Umbau „Ein Stil, der Kümmerer, Handy zuerst“ (10.10.2026) ist bis auf `/empfehlungen/` live.

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
- **Versionen:** `sw.js` 1.26.1 / runtime v34, `ASSET_VER` 2026.10.d.
- **Prüfwerkzeuge** in `tools/checks/` (nicht im Deploy): `check_static.py` (AK1–AK14),
  `check_site.py` (Länge ≤ 8.000 px bei 390, erster Bildschirm, Überlauf), `check_seo.py`
  (Parität zu `../_intern/messungen/vorher`, Ausnahmen in `../_intern/messungen/seo-ausnahmen.json`),
  `check_visual.py` (Startseite pixelgleich). Python 3.13 mit Playwright.

## Verlauf (kurz)
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
- `/empfehlungen/` als Einrichtungs-Pauschalen (Release C2): Preise der Pauschalen stehen zur
  Freigabe aus; „Arbeitsplatz-Zubehör“ bleibt, private Produkte entfallen.
- Danach Gesamtabnahme aller Kriterien und Kontrolle in der Search Console nach zwei und vier Wochen.
- Offen: Linux-Fernwartung auf echtem Mint testen; AGB-PDF von 2024 aktualisieren.

## Blocker
- Release C2 wartet auf die Freigabe der Pauschalen-Preise.

---
*Regel: Diese Datei bei jedem Arbeitsblock aktualisieren – sie füttert Mission Control und Jarvis.*
