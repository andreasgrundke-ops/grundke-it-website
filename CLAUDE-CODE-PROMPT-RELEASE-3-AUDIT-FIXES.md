# Claude-Code-Auftrag · Release 3 · Audit-Fixes

**Basis:** Website-Audit vom 14.04.2026 (`Audit 2026-04/Website-Audit_grundke-it.de_2026-04-14.docx`).
**Scope:** Nur die Audit-Punkte, die *im Repository* umsetzbar sind. Externe Themen
(Google Business Profile, Search Console, Branchenverzeichnisse, Reviews,
Echtgeräte-Tests) werden vom Andy ausserhalb erledigt.

---

## Kontext

Die Seite grundke-it.de ist online und technisch solide. Ein externer Audit hat
eine Reihe von Detail-Lücken gezeigt, die Sichtbarkeit (SEO + KI-Auffindbarkeit),
Rechtssicherheit (DSGVO / TMG / MStV), Barrierefreiheit und Conversion betreffen.

**Dein Auftrag:** Arbeite die unten gelisteten Aufgaben sauber ab — jeweils
mit eigenem Commit — und liefere am Ende einen kurzen Report.

## Arbeitsweise — verbindlich

1. **Erst lesen, dann ändern.** Jede Aufgabe enthält Feststellung, Begründung
   und eine Empfehlungs-Richtung. Die konkrete technische Umsetzung entscheidest
   du — du hast das Repo vor dir, ich nicht.
2. **Wo du unsicher bist, NICHT raten:** Lieber eine konservative Variante
   einbauen, im Code als `<!-- TODO: Entscheidung Andy -->` markieren und im
   Abschluss-Report erwähnen.
3. **Mobile-First bleibt.** Keine Regression auf Desktop-Layout.
4. **CI 2026.01** bleibt verbindlich — Primary Blau `#0c4da2`, Accent Cyan
   `#26bdef`, Fonts lokal gehostet (nie via Google CDN nachladen).
5. **Inhalte NICHT neu erfinden.** Bei Content-Aufgaben (FAQ, Testimonials,
   Hero-Texte): Vorschläge als HTML-Kommentar oder Platzhalter einbauen, damit
   Andy final gegenliest.
6. **Ein Commit pro Aufgabe.** Commit-Message im Muster
   `feat(seo): …` / `fix(legal): …` / `a11y: …` / `chore(meta): …`.
7. **Nicht pushen.** Review-Pflicht beim Andy.

## NICHT anfassen

- DNS, CNAME-Datei, GitHub-Pages-Config.
- Datenschutzerklärung (`/datenschutz/`) — der Text ist bewusst aktuell
  (v2026.04-r3). Keine inhaltlichen Änderungen ausser kleinen Layout-Angleichungen
  falls du dort Header/Footer semantisch umbaust.
- Farbwerte der CI.
- Bestehende Release-2-Anpassungen (Logo, Flip-Cards, FAQ-Accordion) —
  darf nur erweitert werden, nicht zurückgebaut.

---

# Aufgaben

## Aufgabe 1 — Meta-Tag-Block vervollständigen

**Feststellung:** `og:*`-Tags, `twitter:*`-Tags, `<link rel="canonical">`,
`<meta name="robots">` und `<meta name="theme-color">` sind nicht auf allen
Seiten vorhanden.

**Warum wichtig:**
- Ohne Open-Graph zeigen WhatsApp / LinkedIn / Slack nackte Links ohne Bild
  oder Beschreibung → sinkt Klickrate deutlich.
- Ohne `canonical` besteht Duplicate-Content-Risiko (z.B. `/` vs. `/index.html`,
  www vs. non-www).
- `meta robots` macht explizit, dass die Seite indexiert werden soll.
- `theme-color` färbt die Browser-Chrome auf Mobile im CI-Blau — kleiner
  Vertrauenseffekt.

**Empfehlung:**
- Einen gemeinsamen Meta-Block als Include oder als konsistentes Snippet
  auf allen 6 Seiten (Start, Kontakt, Empfehlungen, AGB, Impressum, Datenschutz)
  einbauen.
- `og:title` / `og:description` pro Seite individuell, Rest kann konstant sein.
- `og:image` fürs Erste auf `logo-grundke-it-badge.png` verweisen — ein echtes
  1200×630-OG-Image liefert Andy später nach.
- `404.html` bekommt `<meta name="robots" content="noindex, nofollow">`.

**Zu klären:**
- Welche Seite soll die "kanonische" Variante sein — `https://www.grundke-it.de/`
  oder ohne www? Aktuell wird `www.grundke-it.de` von Google/IONOS-DNS
  bevorzugt → setze `canonical` auf die `www.`-Variante, ausser du findest
  im Repo Hinweise auf etwas anderes.

**Gegencheck:** Nach Einbau einmal `https://www.opengraph.xyz/url/` mit der
Live-URL testen (nach Deployment), oder lokal mit einem Browser-Plugin.

---

## Aufgabe 2 — Favicon-Block im `<head>` vervollständigen

**Feststellung:** Aktuell wird nur `logo-grundke-it-badge.png` als Icon verlinkt.
Die Dateien `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`,
`apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png`
und `site.webmanifest` liegen **bereits im Repo-Root**, werden aber nicht
referenziert.

**Warum wichtig:** iOS "Zum Home-Bildschirm" und Android-Chrome zeigen sonst
einen verzerrten Screenshot. Desktop-Tabs zeigen das grosse Badge, obwohl die
16×16/32×32-Varianten optimiert sind.

**Empfehlung:** Standard-Favicon-Block auf allen Seiten setzen — `.ico`,
zwei PNG-Grössen, apple-touch-icon, manifest, theme-color. Wenn Release 2
schon einen Include-Mechanismus eingeführt hat, dort einhängen.

**Zu klären:** Wenn `site.webmanifest` vom Andy generiert wurde, dort
einmal die Werte gegenlesen — `name`, `short_name`, `theme_color`,
`background_color` sollen zur CI passen (Blau + helles BG).

---

## Aufgabe 3 — robots.txt für KI-Crawler erweitern

**Feststellung:** Die bestehende `robots.txt` enthält nur `User-agent: *`.
Moderne AI-Assistenten (ChatGPT, Claude, Perplexity, Google AI Overview)
haben eigene User-Agents und werten eine explizite Freigabe positiv.

**Warum wichtig:** Ohne explizite Erwähnung werden manche AI-Crawler
konservativ und indexieren die Seite nicht als Quelle. Ziel ist, dass
Anfragen wie "IT-Dienstleister in Grasbrunn" auch in KI-Antworten die
Grundke-IT-Seite als Quelle zitieren.

**Empfehlung:** Folgende User-Agents explizit mit `Allow: /` zulassen —
`GPTBot`, `ClaudeBot`, `anthropic-ai`, `Google-Extended`, `PerplexityBot`,
`CCBot`, `Applebot-Extended`, `Meta-ExternalAgent`. Bestehende
`User-agent: *` / `Disallow: /tree/` / Sitemap-Zeile bleibt.

**Zu klären:** `Disallow: /tree/` — ist das bewusst (vermutlich ein
Linktree-Ersatz für QR-Codes)? Falls ja: die AI-Crawler-Blöcke dürfen
diesen Pfad ebenfalls disallowen.

---

## Aufgabe 4 — Impressum rechtssicher vervollständigen

**Feststellung:** Grundangaben (Name, Anschrift, Kontakt, USt-IdNr. DE350841584)
vorhanden. Es fehlen aber:
- Rechtsform-Angabe (Einzelunternehmen).
- Verantwortlicher nach § 18 Abs. 2 MStV.
- Haftungsausschluss für Inhalte und externe Links.
- Aktualisierter Hinweis zur EU-Streitbeilegung (OS-Plattform ist seit
  20.03.2025 abgeschaltet).

**Warum wichtig:** § 5 TMG / § 18 MStV sind abmahnfähig. Der Punkt "OS-Plattform
abgeschaltet" wird aktuell von IHK und Verbraucherschützern explizit bemängelt,
wenn der Hinweis fehlt.

**Empfehlung:** Folgende Text-Bausteine in `/impressum/index.html` einbauen
(Formulierung kann stilistisch angepasst werden, Inhalte sollen aber enthalten
bleiben):

> **Rechtsform:** Einzelunternehmen.
>
> **Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV:**
> Andreas Grundke, Beethovenring 16, 85630 Grasbrunn.
>
> **Haftung für Inhalte und Links:** Trotz sorgfältiger inhaltlicher Kontrolle
> übernehmen wir keine Haftung für die Inhalte externer Links. Für den Inhalt
> der verlinkten Seiten sind ausschliesslich deren Betreiber verantwortlich.
> Bei Bekanntwerden von Rechtsverletzungen entfernen wir die Inhalte umgehend.
>
> **EU-Streitbeilegung:** Die EU-Kommission hat die Plattform zur
> Online-Streitbeilegung (OS) zum 20.03.2025 eingestellt. Wir sind nicht
> verpflichtet und nicht bereit, an Streitbeilegungsverfahren vor einer
> Verbraucherschlichtungsstelle teilzunehmen.

**Zu klären:** Die Abschnitte sauber in die bestehende Dokument-Struktur
einhängen — nicht als fremdkörpriger Block unten ankleben. Optisch konsistent
zum bestehenden Impressum-Stil.

---

## Aufgabe 5 — Schema.org LocalBusiness erweitern

**Feststellung:** Das bestehende JSON-LD ist sehr gut (LocalBusiness +
FAQPage + Service/OfferCatalog). Es fehlen aber Felder, die Google und
KI-Assistenten für Rich-Snippets und Local-Pack auswerten.

**Warum wichtig:** `priceRange`, `openingHoursSpecification`, `geo`, `sameAs`
sind typische Anreicherungen, die das Local-Pack-Ranking beeinflussen und
KI-Assistenten konkrete Antworten auf "Öffnungszeiten?" / "Preis?" /
"wo genau?" ermöglichen.

**Empfehlung:** Bestehenden LocalBusiness-Eintrag um folgende Properties
ergänzen:

```json
"priceRange": "€€",
"paymentAccepted": "Invoice, SEPA, PayPal, Cash",
"currenciesAccepted": "EUR",
"openingHoursSpecification": [{
  "@type": "OpeningHoursSpecification",
  "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
  "opens": "07:00",
  "closes": "22:00"
}],
"geo": {
  "@type": "GeoCoordinates",
  "latitude": 48.0716,
  "longitude": 11.7561
},
"sameAs": [
  "https://www.linkedin.com/in/andreas-grundke/"
]
```

**Zu klären:**
- Öffnungszeiten: bewusst als 07:00–22:00 Mo-So kommuniziert oder als
  "24/7 telefonisch"? Im Zweifel die hier genannten Zeiten verwenden und
  mit `<!-- TODO Andy: Zeiten bestätigen -->` markieren.
- LinkedIn-URL: Die genaue URL prüfen / von Andy einholen lassen. Wenn
  unklar, Zeile raus und als TODO markieren.
- Geo-Koordinaten 48.0716 / 11.7561 gelten für Grasbrunn. Wenn du präzisere
  Koordinaten für Beethovenring 16 findest, gerne feiner.

**Gegencheck:** Nach Einbau mit Google Rich Results Test
(https://search.google.com/test/rich-results) validieren — soll grüne Häkchen
für LocalBusiness liefern.

---

## Aufgabe 6 — Semantische HTML-Tags nachziehen

**Feststellung:** Die Seite arbeitet stellenweise mit `<div>`-Strukturen, wo
native HTML5-Landmark-Elemente semantisch treffender wären
(`<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`, `<address>`).

**Warum wichtig:**
- Screenreader nutzen Landmarks für Sprung-Navigation.
- Google, Claude, ChatGPT werten Landmarks als Struktur-Signal.
- Keine visuelle Änderung — rein semantische Verbesserung.

**Empfehlung:**
- Header-Bereich (Logo + Navigation) → `<header>` mit innerhalb `<nav aria-label="Hauptnavigation">`.
- Hauptinhalt der Seite → `<main id="main">` (IDs für Skip-Link, siehe Aufgabe 7).
- FAQ-Abschnitte / Blog-Artikel → `<article>`.
- Footer-Bereich → `<footer>` mit `<address>` für den Kontakt-Block.

**Zu klären:** Aktuelle Struktur zuerst lesen, dann entscheiden ob ein
simples Rename (`<div class="header">` → `<header>`) reicht oder ob tiefere
Umstrukturierung nötig ist. Im Zweifel: konservatives Rename, keine
CSS-Selektor-Brüche riskieren (d.h. falls CSS auf `.header {}` zielt, das
zusätzlich als Klasse am neuen `<header>`-Tag stehen lassen).

---

## Aufgabe 7 — Barrierefreiheit (Quick-Wins)

**Feststellung:** Basis-A11y ist OK (Alt-Texte, sprechende Button-Texte,
`aria-expanded` bei Flip-Cards). Es fehlen aber einige Punkte, die für
WCAG 2.1 AA Standard sind und Google/Bing explizit bewerten.

**Warum wichtig:**
- BFSG (seit 28.06.2025) für B2C relevant — Andy ist B2B, also nicht direkt
  verpflichtet. Aber Google belohnt barrierefreie Seiten, und die Zielgruppe
  (Gastro/Hotel-Inhaber > 55 Jahre) profitiert.
- Schlecht sichtbare Fokus-Indikatoren machen die Seite für
  Tastatur-Nutzer unbenutzbar.
- Animationen ohne `prefers-reduced-motion`-Fallback lösen bei
  vestibulär empfindlichen Nutzern Unwohlsein aus.

**Empfehlung — vier konkrete CSS/HTML-Ergänzungen:**

1. **Fokus-Indikator CI-konform:**
   ```css
   *:focus-visible {
     outline: 3px solid #26bdef;
     outline-offset: 2px;
     border-radius: 4px;
   }
   ```
   Prüfe, ob irgendwo `outline: none` gesetzt ist — das ist der häufigste
   A11y-Bug.

2. **Reduced Motion respektieren** (einmal ans Ende der Haupt-CSS):
   ```css
   @media (prefers-reduced-motion: reduce) {
     *, *::before, *::after {
       animation-duration: 0.01ms !important;
       animation-iteration-count: 1 !important;
       transition-duration: 0.01ms !important;
       scroll-behavior: auto !important;
     }
   }
   ```

3. **Skip-Link zum Hauptinhalt** (direkt nach `<body>`):
   ```html
   <a class="skip-link" href="#main">Zum Inhalt springen</a>
   ```
   Im CSS per `:not(:focus)` visuell verstecken, per `:focus` prominent
   einblenden (CI-Blau-Hintergrund, 12px Padding, links oben, z-index hoch).

4. **ARIA-Labels auf Icon-only Buttons:**
   Alle Buttons, die nur ein Icon zeigen (Burger-Menü, Close, WhatsApp-Floater
   falls vorhanden), bekommen `aria-label="Menü öffnen"` etc.

**Zu klären:**
- Kontrast-Check: Der graue Sekundär-Text (`#888` / `#555`) auf weissem BG
  ist OK. Prüfe gezielt grauer Text auf farbigem BG (Info-Boxen,
  CTA-Hintergründe) mit Chrome DevTools → Contrast-Panel. Bei < 4.5:1
  nachdunkeln oder weiss setzen.
- Gibt es in der Seite `<button>`-Elemente ohne Text und ohne `aria-label`?
  Grep nach `<button` ohne folgenden Text-Node finden.

---

## Aufgabe 8 — Sticky Call-CTA Mobile (Audit-P0)

**Feststellung:** Der Audit hat im Live-Zustand keinen Sticky-Call-CTA auf Mobile
gefunden — nur einen Scroll-to-Top-Button. Das war Teil von
Release 2 (`CLAUDE-CODE-PROMPT-RELEASE-2-MOBILE.md`, Schritt 6), offenbar
aber nicht umgesetzt oder wieder entfernt.

**Warum wichtig:** Erfahrungswert zeigt 20–40 % mehr Anrufe, wenn die
Telefon-CTA auf Mobile permanent am unteren Viewport-Rand klebt. Bei
grundke-it.de ist der Anruf der primäre Conversion-Pfad.

**Empfehlung:** Exakt nach Spec aus Release-2-Prompt, Schritt 6. Kurz:
- Nur sichtbar `@media (max-width: 1023px)`.
- Fixiert am unteren Rand, volle Breite, CI Primary Blau.
- `<a href="tel:+4917825844 38">` mit Telefon-Icon.
- Safe-Area-Inset für iPhone-Home-Indicator: `padding-bottom: env(safe-area-inset-bottom)`.
- Body-Bottom-Padding, damit Content nicht verdeckt wird.

**Zu klären:** Falls der Scroll-to-Top-Button unten rechts kollidiert →
Layout so anpassen, dass beide koexistieren (Scroll-Top über dem Call-CTA,
oder Scroll-Top nur auf Desktop sichtbar lassen).

---

## Aufgabe 9 — FAQ-Ausbau

**Feststellung:** Das FAQ-Accordion (Release 2) enthält aktuell 5 Fragen.
Das JSON-LD `FAQPage` referenziert dieselben 5.

**Warum wichtig:** KI-Assistenten und Google AI Overview lieben
FAQ-strukturierten Content — je mehr hochwertige Fragen, desto mehr
Einstiegspunkte für Long-Tail-Suchen ("Was kostet IT-Dienstleister in
München Ost?", "Wie schnell kommt ein Notdienst?" etc.).

**Empfehlung:** 5 auf 10–12 Fragen erweitern. Themen-Richtungen, die aus
dem Website-Content selbst abgeleitet werden können:
- Preis (Festpreis vs. Stundenabrechnung, 15-Minuten-Takt)
- Verfügbarkeit (24/7, Wochenende, Notfall-Reaktionszeit)
- Einsatzgebiet (Radius 15 km, welche Orte)
- Zielgruppen (Branchen, Unternehmensgrösse)
- Erstkontakt-Ablauf (Schnellcheck, Probeeinsatz)
- Datenschutz (lokale Daten, Backups)
- Vertrag (Kündigungsfrist, Laufzeit)

**Zu klären:** Die neuen Fragen **nicht frei erfinden** — stattdessen
pro Frage einen 2-3-Zeilen-Platzhalter als `<!-- TODO Andy: Antwort -->`
einbauen. Andy liefert die Final-Texte nach. Das `FAQPage`-JSON-LD dann
in einem zweiten Durchgang synchronisieren.

**Alternative:** Wenn Andy die Antworten lieber direkt in diesem Chat
schreibt, diese Aufgabe komplett überspringen und im Report erwähnen.

---

## Aufgabe 10 — 404-Seite im CI-Look

**Feststellung:** `404.html` existiert im Repo. Unklar ob sie die aktuellen
CI-Elemente (Header, Footer, Logo, Farben) verwendet und ob `<meta robots
noindex>` gesetzt ist.

**Warum wichtig:** Eine CI-konforme 404-Seite mit klarer "Zurück zur
Startseite"-CTA fängt Fehl-Klicks ab (z.B. von alten WordPress-URLs, die
Google noch im Index hat). `noindex` verhindert, dass 404-Seiten selbst
in die Google-Suche geraten.

**Empfehlung:**
- 404-Seite aufmachen, prüfen ob Header + Footer konsistent mit dem Rest
  sind (falls nicht: angleichen).
- `<meta name="robots" content="noindex, nofollow">` ins `<head>`.
- Klare H1 ("Seite nicht gefunden"), kurzer Erklärtext, Hauptbutton
  "Zurück zur Startseite" + kleinere Sekundär-Aktion "Direkt anrufen"
  (Telefon-Link).

**Zu klären:** Wenn die 404-Seite bereits komplett sauber ist — nur das
`noindex`-Meta prüfen und Report-Notiz "404 war schon sauber".

---

# Abschluss

## Commit-Strategie

Pro Aufgabe ein eigener Commit, in dieser Reihenfolge:

```
chore(meta):   Meta-Tag-Block (OG, Twitter, canonical, robots, theme-color)
chore(icons):  Favicon-Block im <head> aller Seiten vervollständigen
chore(robots): robots.txt um AI-Crawler-Freigabe erweitern
fix(legal):    Impressum um Rechtsform, §18 MStV, Haftung, EU-Schlichtung
feat(seo):     Schema.org LocalBusiness erweitern (geo, priceRange, openingHours, sameAs)
refactor(html): Semantische HTML5-Landmarks (header/nav/main/article/footer/address)
a11y:          Focus-Visible + Reduced-Motion + Skip-Link + ARIA-Labels
feat(mobile):  Sticky Call-CTA am Viewport-Boden (<1024px)
content(faq):  FAQ-Accordion auf 10-12 Fragen erweitern (Platzhalter-Antworten)
fix(404):      404-Seite CI-angleichen + noindex
```

Jeder Commit für sich lauffähig — Desktop-Layout unverändert, Site baut.

## Verifikation vor Abschluss-Commit

1. Lokal aufrufen — Startseite, Impressum, Kontakt, 404 durchklicken.
2. Chrome DevTools → Device Mode → iPhone 14, iPad, Desktop → visuell prüfen.
3. Chrome DevTools → Lighthouse → mobiler Run → Scores notieren
   (Performance / Accessibility / Best Practices / SEO).
4. Chrome DevTools → Console → keine neuen JS-Fehler.
5. View-Source auf Startseite → OG- / Canonical- / Robots-Tags sichtbar.
6. `/site.webmanifest` direkt aufrufen → validiert.
7. `/robots.txt` direkt aufrufen → enthält AI-Crawler-Block + Sitemap-Zeile.

## Abschluss-Report am Ende

1. `git log --oneline` der neuen Commits.
2. Max. 15 Zeilen Bericht:
   - Welche Aufgaben komplett erledigt.
   - Welche mit TODO-Kommentaren markiert wurden (wo Andy noch ran muss).
   - Lighthouse-Scores vorher / nachher falls messbar.
   - Unerwartete Entdeckungen (falls etwas im Code aufgefallen ist).
3. Liste aller berührten Dateien.
4. Offene Fragen an Andy (am Ende).
5. **Nicht pushen.** Warten auf Review.

---

**Kein Trial-and-Error. Erst verstehen, dann umsetzen. Bei Unsicherheit: TODO statt Rateversuch.**
