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
   und KI-Seiten sowie die Angebots- und Ratgeberseiten (aktuell 27 Stueck, seit 10.10.2026 inkl. Schulung) und fuer `sitemap.xml`. Diese `index.html`-Dateien
   niemals von Hand aendern, sondern die Datenlisten `PLACES`/`SERVICES` pflegen und
   `python tools/build_landingpages.py` laufen lassen. Handgebaut sind nur: Startseite,
   kontakt, fernwartung, empfehlungen, tree, ki-arbeitsplatz-onboarding-kit,
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
- **Release 2.0.0:** ruhigere Optik, Dock neu, Version im Fuss, Stundensatz-Wortlaut. Umbau "Ein Stil, der Kuemmerer, Handy zuerst":
  Startseite am Handy rund 10.300 px, alle Generator-Seiten in der Huelle `render_shell` (Kopf, Abschnitte im Wechsel,
  Abschluss `closing()`), Schulung/Kontakt/Fernwartung/Rechtsseiten/404 in der neuen Huelle, Empfehlungen mit
  Einrichtungs-Pauschalen, Barrierefreiheitserklaerung neu.
- **Release 2.0.1 (in 2.1.0 enthalten):** im Abschnitt IT-Betreuung „So arbeite ich“ (`ul.itb-how`, sechs Punkte)
  statt Systemhaus-Vergleich, FAQ-Passungsfrage, KI-Kennzeichnung `p.cta-ki` im Abschluss (`closing()`, Startseite von Hand).
- **Startseite Hero "Ein Weg"** (H1 „IT hängt? Ruf mich an.“): Bühne „So läuft das bei mir“, vier Fälle mit je drei
  Bildern, sichtbare Kennzeichnung als nachgestellte Beispiele, darunter eine echte Google-Stimme; gesteuert von
  `assets/js/hero-wege.js`. Kein Vergleich mit anderen Anbietern. Der Endstand ist der HTML-Grundzustand (ohne JS sichtbar),
  Pause-Knopf, bei reduzierter Bewegung bleibt es beim Endstand. Direkt unter dem Hero der Link zu /it-betreuer-wechseln/. Das Chat-Handy steht im Abschnitt IT-Betreuung
  (`[data-hero-chat]`, `assets/js/hero-chat.js`) und startet erst bei Sichtbarkeit; abends 20-40 Min. bis zur Antwort.
- **Versionen jetzt:** `sw.js` `CACHE_NAME` `grundke-it-v2.1.0`, `RUNTIME_CACHE` `runtime-v39`,
  `ASSET_VER` 2026.10.i, `SITE_VERSION` 2.1.0 (Fuss "Version x.y.z · Stand TT.MM.JJJJ" aus dem Generator).
  `SITE_VERSION` bei jedem Release mit dem `CACHE_NAME`-Suffix gleichziehen, `check_static.py` prueft das.
  `check_static.py --ci` laeuft im Deploy und stoppt ihn bei Fehlern.
- **Kontaktleiste (Dock):** kommt aus einer Quelle im Generator (`STICKY`-Marken), nur bis 1279 px sichtbar,
  ab 1280 px ausgeblendet; nie in einzelnen Dateien aendern.
- **Typo:** `body.is-home` traegt die groessere Schriftskala der Startseite; Unterseiten bewusst ohne.
- **Stundensatz:** Wortlaut einheitlich „110 € netto zzgl. MwSt.“ (`HOME_PRICE_LINES` in `check_static.py`).
- **Pruefen vor jedem Release:** `tools/checks/` (check_static, check_site, check_seo mit
  `--allow ../_intern/messungen/seo-ausnahmen.json`, check_visual, `check_design.py` mit `--release r1`
  und `--heights --baseline`, `check_sw.py` mit `--upgrade`), Python 3.13 mit Playwright.
  check_static vergleicht die Rechtstexte je Seite mit ihrem Basis-Commit (`LEGAL_BASE_COMMITS`);
  Rechtstext nur mit Andreas' OK aendern und dann Basis-Commit und `legal_hash.json` nachziehen.
- **Offen:** Ortsseiten-Fakten (Entwurf in `../_intern/o5-ortsfakten.md`), Linux-Fernwartung auf echtem
  Mint testen, Search Console um den 24.10. und 07.11.2026, Laengenbudgets fast voll (`#preise` bei 390 px: 4.983 von 5.000, siehe STATUS).
- Details in `STATUS.md`; Spec, Plan, Textblatt, Messungen und Fachwissen ausserhalb des Repos in
  `../_intern/` (Repo ist oeffentlich).

*CI 2026.01 · Grundke IT-Service · www.grundke-it.de*
