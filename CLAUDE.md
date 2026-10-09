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
   und KI-Seiten sowie die Angebots- und Ratgeberseiten (aktuell 26 Stueck) und fuer `sitemap.xml`. Diese `index.html`-Dateien
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
- **09.10.2026 (live):** Hero nur noch mit dem Chat (vier Einstiege raus), `/fernwartung/` mit
  Umschalter Windows/Linux/macOS, TeamViewer ueberall raus, Website-Preise neu (One-Pager ca. 800,
  Start ca. 1.300, Ausbau ca. 2.000 €, Betrieb optional 40 €/Monat). `sw.js` 1.22.5.
- **07.10.2026 (live):** Konzept „Sichtbarkeit und
  Wachstum“ umgesetzt. Startseite mit Kernsatz „Deine IT-Abteilung. Nur extern.“,
  elf neue Seiten aus dem Generator (Software, Websites, IT-Betreuer wechseln, Lizenzen, E-Rechnung,
  Digitalbonus, Ratgeber mit vier Artikeln), Menue IT-Service · KI im Betrieb · Software · Websites ·
  Preise, drei Audits eingearbeitet. Preise der Projektseiten am Schalter `SHOW_FROM_PRICES`.
- **Laeuft (ab 10.10.2026):** Umbau „Ein Stil, der Kuemmerer, Handy zuerst“ – alle Unterseiten im
  Stil der Startseite, Startseite am Handy <= 12.000 px. Spec und Uebergabe in `../_intern/specs/` und
  `../_intern/handoffs/2026-10-10-website-umbau.md`; naechster Schritt dort §8 (Plan, Pruefung, OK).
- **Offen:** Linux-Fernwartung auf echtem Mint testen (oeffentlich verlinkt, nie getestet).
  Geplant nach ATG: Musterbeispiele auf Websites/Software (Gehirn `musterbeispiele-websites-software`).
- **Naechster Schritt:** offene Inhaltsfragen aus der internen Uebergabe mit Andreas klaeren
  (`../_intern/`), danach eigener Durchgang fuer Titel der alten Leistungsseiten und Tippflaechen.
  Details in `STATUS.md`, Fachwissen im Wiki ausserhalb des Repos (`../_intern/wiki/`, weil das
  Repo oeffentlich ist).

*CI 2026.01 · Grundke IT-Service · www.grundke-it.de*
