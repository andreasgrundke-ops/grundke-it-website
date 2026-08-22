# STATUS – grundke-it.de Website
<!-- CI 2026.01 · Grundke IT-Service · Standard-Statusdatei, wird von Mensch+KI gepflegt -->

**Stand:** 2026-08-22 · **Status:** Live (KI-Bereich committet, noch nicht gepusht)

## Was ist das
grundke-it.de Website – siehe README/CLAUDE.md im Projekt.

## Aktueller Stand
Letzter Arbeitsblock (22.08.2026): **KI als zweite Saeule aufgebaut.**

KI kam auf der Website bisher nur als eine von zehn Leistungskacheln vor, ohne eigene Seite und
ohne Substanz – fuer Suche und KI-Antworten also unsichtbar, obwohl das Thema laengst
Schwerpunkt ist (eigene Anwendungen seit ueber einem halben Jahr im Einsatz, erste
Kundenprojekte laufen).

- **Vier neue Seiten** ueber `tools/build_landingpages.py`: `/ki-fuer-kmu/` (Hub mit drei
  anonymisierten Praxisfaellen, Potenzialcheck und dem Abschnitt „wann sich das nicht lohnt"),
  `/ki-automatisierung/` (E-Rechnung mit den Fristen 2025/2027/2028, Schnittstellen, Dokumente),
  `/ki-videoanalyse/` (Objekterkennung auf UniFi Protect, Verarbeitung im Haus, klare Absage an
  Gesichtserkennung und Verhaltensauswertung), `/ki-dsgvo/` (lokal vs. EU-Cloud vs. AVV,
  KI-Verordnung Art. 4, Nutzungsrichtlinie, RDG-Abgrenzung).
- **Generator minimal erweitert** um optionale Felder `extra`, `extra_style`, `extra_schema`,
  `published`/`modified`/`modified_disp`, `cta2`. Ohne diese Felder rendert alles wie vorher –
  die 11 Bestandsseiten aendern sich nur um sechs Zeilen Navigation und Footer.
- **Eigene Datumsangaben fuer den KI-Bereich** (`KI_DATE`), damit `dateModified` der Orts- und
  Leistungsseiten bei 2026-06-18 bleibt. Ein neuer Footer-Link ist keine inhaltliche
  Aktualisierung; die Freshness-Signale bleiben ehrlich.
- **Startseite:** neue Sektion `#ki` weit oben (zwischen den acht Situationen und der
  USP-Sektion), Leistungskachel als Link, FAQ-Antwort mit Substanz (sichtbar und FAQPage-Schema
  zeichengleich), Footer-Spalte, Service-Offer im Schema praezisiert.
- **Navigation:** FAQ raus, „KI im Betrieb" rein – auf allen 20 indexierten Seiten inklusive der
  vier handgebauten (empfehlungen, fernwartung, kontakt, schulung). Ein neunter Nav-Punkt haette
  die Leiste um 1200 px umbrechen lassen; FAQ steht ohnehin weiter unten auf der Startseite.
- **llms.txt:** eigener Abschnitt „KI im Betrieb" mit den drei Anwendungsfeldern – der Teil, den
  zitierende KI-Systeme lesen.
- **sw.js auf v1.11.0 / runtime-v10**, sonst behaelt jeder wiederkehrende Besucher die alte
  Navigation ohne den KI-Punkt.
- **Rechtsangaben vorher geprueft** (Websuche, nicht aus dem Gedaechtnis): E-Rechnung
  Empfangspflicht seit 01.01.2025, Uebergangsfrist bis 31.12.2026, Ausstellungspflicht ab
  01.01.2027 (>800.000 EUR Vorjahresumsatz) bzw. 01.01.2028 fuer alle. EU AI Act Art. 4 seit
  02.02.2025, nationale Durchsetzung seit 02.08.2026. Auf beiden Seiten steht eine Abgrenzung:
  keine Steuer-, keine Rechtsberatung.
- Geprueft: 74 JSON-LD-Bloecke valide, je eine H1, Sitemap 20 URLs non-www, Darstellung bei
  1440/1280/390 px.

- **Kopfzeile der Startseite: Umschaltpunkt korrigiert.** Andreas' Screenshot zeigte den ersten
  Menuepunkt direkt an der Ortspille klebend. Gemessen: Das Hauptmenue der Startseite ist mit
  acht Punkten 816-852 px breit und passt neben Logo und Ortspille erst ab rund 1240 px, der
  globale Umschaltpunkt lag aber bei 1024 px. Bei 1100 px betrug der Abstand 0 px, bei 1024 px
  lief der Anruf-Knopf 114 px aus dem Bild. **Der Fehler bestand schon vor dem KI-Punkt**
  (gegengemessen: 3 px Abstand ohne ihn), der neue Eintrag hat ihn nur sichtbar gemacht.
  Fix: Vollmenue auf der Startseite erst ab 1240 px (seitenspezifisch, damit die Unterseiten
  ihren 1024er-Punkt behalten - dort sind es nur fuenf Punkte und 125 px Luft), dazu
  `margin-left:1.5rem` auf `.nav-links` als Mindestabstand zur Ortspille. Nachgemessen bei
  1239/1280/1366/1400/1440/1512/1600/1920: Abstand ueberall 22 px oder mehr, Anruf-Knopf
  immer im Bild. sw.js auf v1.12.0/runtime-v11, weil style.css sich geaendert hat.

Davor (01.08.2026):

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
- **Ortspille „Muenchen Ost"** steht jetzt auf allen Seiten gleich weit hinter dem Logo.
  `justify-content:space-between` haengt am Menue: Startseite sieben Eintraege, Unterseiten
  vier – die Pille stand dadurch 75 px bzw. 227 px hinter dem Logo. `.nav-loc` bekommt
  `margin-right:auto` + festen Abstand; Startseite bleibt unveraendert.
- **Service-Worker-Cache:** `CACHE_NAME`/`RUNTIME_CACHE` standen seit April still, deshalb kam
  der Kopfzeilen-Fix trotz Deploy nicht beim Besucher an. Jetzt v1.10.0/v9.
  **Regel: bei JEDEM Release beide Namen erhoehen** – steht im Kopf von `sw.js`.
- Geprueft bei 390, 768 und 1440: kein horizontaler Scroll, Download-Knopf 293x56 px auf Mobil.

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
- **Andreas liest den KI-Bereich gegen** (vier Seiten + Startseiten-Sektion), dann `git push`.
  Bis dahin ist alles committet, aber nicht live.
- Danach Search Console: die vier KI-URLs zur Indexierung einreichen, Sitemap neu einreichen.
- Search Console + Bing: non-www-Property prüfen; GBP/Verzeichnisse auf non-www ziehen
  (Cowork/Browser-Arbeit).
- Offen zur Entscheidung: Hero-Karussell → statisches Hero, Cyan-Kontrast, DSGVO-Statistik.
- Geklaert (Andreas, 22.08.2026): **110 EUR netto ist der gewollte Website-Preis.** Wer sich
  ueber die Website meldet, wird mit 110 EUR abgerechnet; die 90 EUR im Workspace-CLAUDE.md
  sind der Bestandskundensatz. Beide Zahlen sind richtig, die Abweichung ist Absicht. Die
  KI-Seiten nennen daher jetzt ebenfalls 110 EUR netto im 15-Minuten-Takt.
- Vorschlag für später: auf `/schulung/` einen Absatz zur KI-Kompetenzpflicht nach Artikel 4
  ergänzen. `/ki-dsgvo/` verlinkt bereits dorthin, ein Rückverweis fehlt noch.

## Blocker
(keine)

---
*Regel: Diese Datei bei jedem Arbeitsblock aktualisieren – sie füttert Mission Control und Jarvis.*
