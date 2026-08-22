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
   kontakt, schulung, fernwartung, empfehlungen, tree, 404 und die Rechtsseiten.
2. **Bei JEDEM Release `CACHE_NAME` und `RUNTIME_CACHE` in `sw.js` erhoehen.** Statische
   Dateien laufen Cache-First; ohne Erhoehung sieht ein wiederkehrender Besucher weiter die
   alte Version, obwohl der Deploy durch ist. Das ist hier schon zweimal passiert.

Weitere Konventionen: FAQ-Texte stehen doppelt (sichtbar und im FAQPage-JSON-LD) und muessen
zeichengleich bleiben. `dateModified` nur hochsetzen, wenn sich der Inhalt der Seite wirklich
geaendert hat, nicht wegen eines neuen Footer-Links.

## Stand / offen / naechster Schritt
- **Stand:** 22.08.2026 — KI-Bereich als zweite Saeule gebaut (Hub `/ki-fuer-kmu/` plus drei
  Unterseiten, Startseiten-Sektion, Navigation, llms.txt). Committet, **noch nicht gepusht**.
- **Offen:** Andreas liest den KI-Bereich gegen, dann Push. Danach die vier URLs in der Search
  Console zur Indexierung einreichen.
- **Naechster Schritt:** siehe `STATUS.md` — dort steht der vollstaendige Arbeitsstand.

*CI 2026.01 · Grundke IT-Service · www.grundke-it.de*
