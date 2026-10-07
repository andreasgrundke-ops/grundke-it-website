# STATUS – grundke-it.de Website
<!-- CI 2026.01 · Grundke IT-Service · Standard-Statusdatei, wird von Mensch+KI gepflegt -->

**Stand:** 2026-10-07 · **Status:** Live

## Was ist das
grundke-it.de Website – siehe README/CLAUDE.md im Projekt.

## Aktueller Stand
Letzter Arbeitsblock (07.10.2026): **Konzept „Sichtbarkeit und Wachstum“ umgesetzt**, von Andreas
freigegeben und live (ein Commit auf `main`, vorher Code- und Sicherheitsreview).

- **Startseite:** Kernsatz „Deine IT-Abteilung. Nur extern.“ als H1, vier Einstiege als Chat-Paare im Hero
  (IT-Betreuer wechseln, Software nach Maß, KI/Datenschutz/E-Rechnung, Websites). Seite gekürzt
  (Kontaktleiste, Laufband, Flip-Karten, Zielgruppen raus), Titel wieder mit „Grasbrunn“, FAQ aus einer Liste.
  impeccable-Kritik 14/32 → 21/32.
- **Neue Seiten aus dem Generator** (jetzt 26): `/software-nach-mass/`, `/websites-fuer-betriebe/`,
  `/it-betreuer-wechseln/`, `/lizenzen/`, `/e-rechnung/` (mit Hilfe bei Programmwahl und -wechsel),
  `/digitalbonus-bayern/`, Ratgeber „Die ersten 15 Minuten“ mit vier Artikeln. `/ki-dsgvo/` heißt jetzt
  „KI sicher einsetzen“ und enthält das Paket KI-Start. Menü: IT-Service · KI im Betrieb · Software ·
  Websites · Preise; Fuß in fünf Spalten.
- **Preise** der Projektseiten hängen am Schalter `SHOW_FROM_PRICES` und am Wörterbuch `PRICES` im Generator.
- **Drei Audits** (Copy, SEO/GEO, UI 15/20) eingearbeitet: keine Zeitzusagen mehr, ChatGPT Business,
  BMF-Schreiben zur E-Rechnung vom 15.10.2025, Digitalbonus-Haken laut Richtlinie, Skip-Link und
  Anker-Fokus, Kontaktleiste bis 1279 px unten, Haupt-Buttons in Visitenkarten-Blau, AA-Kontraste,
  Tabellen am Handy gestapelt. `sw.js` 1.22.0 / runtime v23. `main.js` 1.3.0.
- **Nach dem Live-Gang:** neue URLs per IndexNow gemeldet. Offene Inhaltsfragen stehen in der internen Übergabe.

Davor (02.10.2026): **Chat-Hero statt Foto-Slider** (von Andreas freigegeben, live).

- **Fix 03.10.2026** (`hero-chat.js` 1.4.0, `sw.js` 1.20.0 / runtime v21): Am Handy lief das Tippen des
  Kunden unsichtbar mit (Eingabezeile/Tastatur sind unter 768 px per CSS aus), bis zu 8 s leerer Chat,
  danach alles dicht hintereinander. Jetzt kommt die Kundennachricht dort nach 1,4 s Lesepause; der Takt
  zaehlt hoechstens 250 ms je Tick, damit gedrosselte Timer (Scrollen, Energiesparen) nichts nachholen.
- **SW-Fix 03.10.2026** (`sw.js` 1.21.0 / runtime v22): Pre-Cache zog Dateien aus dem HTTP-Cache
  (max-age=600) und gewann danach immer gegen das Background-Update - Besucher blieben bis zum
  naechsten Release auf altem JS. Jetzt `cache:'reload'` beim Install und Runtime-Cache zuerst.

- Kritik des alten Sliders (impeccable, zwei Agenten): 14/32 – anonyme Stockfotos, 5 rotierende
  Botschaften, 31 Tab-Stopps in unsichtbare Slides, kein Pause-Knopf, Unterzeile klang nach Garantie.
- Neu: Headline bleibt, Unterzeile „IT-Betreuung für Betriebe im Münchner Osten … am anderen Ende bin
  ich, Andreas Grundke", Belege (5,0 Google · 20 Jahre · ab 149 € netto), zwei Buttons, QR ruhig;
  rechts Chat-Demo mit Uhrzeit des Besuchers, einmal durchgespielt. 5 Tab-Stopps, LCP = H1, CLS ≈ 0.
- Nachschärfung nach Andreas: **Kundensicht** (Kontakt „Andreas IT", Messenger-Optik), Tastatur fährt
  beim Tippen des Kunden ein, Tasten leuchten, Tipptempo menschlich (~115 ms/Taste). Fünf Fälle: Kasse/EC,
  E-Mail beim Anbieter, IT-Kollege hört auf, defekter Netzwerkspeicher, Buchungsseite (bleibt stehen).
  Durchlauf ~2:20 min, danach Endzustand. Uhrzeit nur in der Statusleiste, CTAs zierlicher. Ad hoc 110 € netto/Std.
- Code-Review: freigegeben (2 MEDIUM behoben). Finish-Review: Nacharbeiten eingebaut.
- **Offen:** Laufband- und Kontaktleisten-Texte gegen Angebotsfakten
  („Remote-Hilfe in Minuten", „Flatrate", „erreichbar. Jetzt.") – Andreas entscheidet; Foto-Shooting.

Davor (27.09.2026): **sechste Kundenstimme + Sichtbarkeits-Check.**

- Google-Rezension **Apartments Bauer** (26.09.2026, WLAN auf Ubiquiti im Altbau) wortgetreu
  als breite Karte oben in `#referenzen` und als Praxisbeispiel auf `/netzwerk-wlan-firewall/`
  (Generator: `extra` + `VOICE_STYLE`). Schema `reviewCount` 6. Google-Profil: 5,0 bei 5.
- Schema `hasMap`/`sameAs` auf den CID-Link (`maps.google.com/?cid=1934827868521304193`),
  ProvenExpert in `sameAs`, `llms.txt` nachgezogen. `sw.js` 1.17.1 / runtime v18.
- Sichtbarkeit (WebSearch, nicht Google): bei „Grasbrunn"-Suchen auf der ersten Seite, bei
  Haar, München Ost, Notdienst und KI nicht. Verzeichnisse: Name in drei Varianten,
  meinestadt/bedirect mit falscher Telefonnummer (0178 258448), 11880 ohne Hausnummer,
  Das Örtliche/Gelbe Seiten/Bing Places fehlen. ProvenExpert: kein Logo, Beschreibung und
  Angebote leer, Website-Link mit www, 0 Bewertungen.

Davor (23.09.2026): **Seite aus einem Guss, Inhalte bereinigt** (Commit 462a594 ff., live).

- **Ein Menü und ein Footer für alle Seiten.** Beides erzeugt `tools/build_landingpages.py`
  (`nav_html`, `footer_html`); `sync_shared()` schreibt es auch in Startseite und handgebaute
  Seiten. Vorher gab es vier Menü- und fünf Footer-Varianten, die KI-Seite wirkte angestückelt.
- Aktiver Menüpunkt per `aria-current`, Brotkrumen, FAQ als Akkordeon, Buttons `.btn-p/.btn-g`
  überall, KI-Hub mit eigenem Einstieg, Querverweise zwischen den KI-Seiten.
- **Inhalte nach Andreas' Vorgaben**: nur
  Geschäftskunden, keine garantierten Reaktionszeiten, planbare Monatspauschale, Anfahrt bis
  5 km inklusive, Monatsreport nur Premium, „KI datenschutzgerecht einsetzen", Art. 4 KI-VO nach
  Digital Omnibus, KI-Modul in der Schulung, Floskeln raus.
- Datenschutzerklärung um Amazon-Partnerprogramm, Fernwartungs-Download (Hetzner),
  Service Worker und localStorage ergänzt; Barrierefreiheit: § 3 Abs. 3 BFSG, Grau-Kontrast als
  bekannte Einschränkung.
- IndexNow-Schlüssel im Root, geänderte URLs an Bing/IndexNow gemeldet.
- `sw.js` 1.16.0 / runtime v16. Code-Review ohne kritische Befunde.

Davor (11.09.2026): **Kundenstimmen auf der Startseite überarbeitet.**

Anlass war eine direkt übermittelte Bewertung von Janine Blumenschein (Steuerberatung). Beim
Gegenlesen des Google-Profils kam heraus, dass dort **vier** Rezensionen stehen, die Website aber
nur drei zeigte und zwei davon nicht wörtlich zitierte.

- **Fünf Stimmen** stehen jetzt auf der Seite: vier Google-Rezensionen (Fleischmann, Dietz,
  Verena K., **Martina Polednik – war neu**) plus Blumenschein als direkt übermittelte Stimme.
- **Zitate auf den Wortlaut gezogen.** Fleischmann stand gekürzt und umformuliert da
  („Schnell, zuverlässig…" statt „Ich bin sehr zufrieden mit der Arbeit der Firma. Die Umsetzung
  erfolgte schnell…"), bei Dietz war aus „Service...perfekte" ein Gedankenstrich geworden. In
  Anführungszeichen gesetzte Kundenaussagen müssen wörtlich sein — sonst angreifbar.
- **Quellenangabe ehrlich halten:** Blumenschein trägt „Steuerberatung", nicht
  „Google-Bewertung" — sie hat dort (noch) nicht bewertet. Label erst angleichen, wenn die
  Google-Rezension wirklich steht.
- **Schema:** `reviewCount` 3 → 5 (vier Google + eine direkt), fünf `Review`-Objekte, alle
  `reviewBody` zeichengleich mit dem sichtbaren Text. `dateModified` auf 2026-09-11.
- **Layout:** `.testi-grid` von `auto-fit` auf feste Spalten (1 / 2 ab 680px / 4 ab 1150px) —
  mit fünf Karten blieb sonst je nach Fensterbreite eine Zelle leer. Die lange Blumenschein-Stimme
  läuft als `.testi-wide` über die volle Reihe, Zitat auf 66ch begrenzt, Signatur daneben. Karten
  sind Flex-Spalten, damit Name und Rolle einer Reihe auf gleicher Höhe sitzen.
- `sw.js` auf **1.15.0 / runtime v15**.
- Geprüft bei 390/768/1440/1920: kein horizontaler Scroll, keine leeren Rasterzellen, JSON-LD
  valide. Offen aus dem Code-Review: die Sterne sind Deko-SVGs ohne Textalternative (alle fünf
  Karten), und `reviewCount` 5 steht gegen die Google-Zahl 4 — bewusst, weil Blumenschein echt,
  aber nicht bei Google ist.

Davor (29.08.2026): **Unverlinktes Arbeitsbuch `/ki-arbeitsplatz-onboarding-kit/`.**

Zweck: Wer jemanden mit Claude arbeitsfaehig machen will, schickt kuenftig einen Link statt eines
ZIP-Anhangs. Die Person hakt zwoelf Phasen direkt im Browser ab (Stand im localStorage) und laedt
sich darunter die Vorlagen — Muster-MDs, zwei Projektvorlagen, zwoelf Skills,
Konnektoren-Checkliste, dazu das Komplettpaket mit einer Offline-Fassung des Arbeitsbuchs.

- **Nicht auffindbar, aber ohne Zugangsdaten erreichbar:** `noindex, nofollow` im Kopf,
  `Disallow` in `robots.txt` fuer alle Crawler einschliesslich der KI-Bots, kein Eintrag in
  `sitemap.xml`, von keiner Seite verlinkt. Wer den Link hat, kommt hinein — genau so gewollt.
- **URL ohne Versionsnummer**, damit sie stabil bleibt und weitergegebene Links immer den
  aktuellen Stand zeigen. Die Version steht klein in der Fusszeile (Arbeitsbuch v1.1.1).
- **`sw.js` auf 1.14.1 / runtime v14.** Die Seite bewusst **nicht** im Pre-Cache: sie gehoert
  nicht auf jedes Geraet, sondern nur zu denen, die den Link bekommen haben.
- **Kein Kunden- oder Projektbezug im Inhalt.** Das Repo ist public, die Dateien sind damit auch
  ueber github.com sichtbar — ein Link ohne Zugangsdaten ist kein Zugriffsschutz. Wer echten
  Schutz braucht, nimmt Basic Auth auf dem VPS statt GitHub Pages.
- Commits `e7927fb` (Seite) und `f875d3f` (Verweisfarbe im Dunkelmodus, Sprungziele). Der
  Farbfehler fiel erst im Screenshot-Test auf: Verweise erbten das Standardblau des Browsers und
  waren auf dunklem Grund praktisch unlesbar. Lehre: bei neuen Seiten beide Themen ansehen, nicht
  nur den Quelltext pruefen.
- Live geprueft: 200 auf Seite und allen sieben Downloads, `noindex` vorhanden, 17
  `Disallow`-Zeilen, kein Sitemap- und kein Startseiten-Link, Abhaken und Fortschrittsbalken
  funktionieren in hell und dunkel.

Davor (22.08.2026): **KI als zweite Saeule aufgebaut** — inzwischen gepusht und live.

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
  immer im Bild.
  **Nachgezogen auf Andreas' Wunsch:** Im Bereich 1024-1239 px weicht jetzt die Ortspille
  statt des Menues. Ohne die Pille passt das volle Menue schon ab 1024 px (gemessen 23 px
  Abstand zum Logo), die Navigation bleibt also auf Laptop-Breiten vollstaendig lesbar. Der
  Ortsbezug steht weiter im Quelltext (nur `display:none`, kein Entfernen) und ist ab 1240 px
  wieder sichtbar. sw.js auf v1.13.0/runtime-v12.

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
- Erledigt 23.09.2026: Sitemap in der Search Console neu eingereicht, die vier KI-URLs zur
  Indexierung beantragt (Property `https://grundke-it.de/`;
  alle vier waren Google bis dahin unbekannt). In ein paar Tagen unter „Seiten" nachsehen.
- Erledigt 23.09.2026: AVV mit Hetzner besteht, Unterlagen liegen intern.
- Offen aus dem Inhalts-Audit: AGB-PDF von 2024 aktualisieren; Kombi-Paket Schulung klarstellen
  (Live-Schulung jedes Halbjahr enthalten?); Datenschutzerklärung durchgehend „wir".
- Search Console + Bing: non-www-Property prüfen; GBP/Verzeichnisse auf non-www ziehen
  (Cowork/Browser-Arbeit).
- Offen zur Entscheidung: Hero-Karussell → statisches Hero, Cyan-Kontrast, DSGVO-Statistik.
- Geklaert (22.08.2026): **110 EUR netto ist der Stundensatz fuer Anfragen ueber die Website.**

## Blocker
(keine)

---
*Regel: Diese Datei bei jedem Arbeitsblock aktualisieren – sie füttert Mission Control und Jarvis.*
