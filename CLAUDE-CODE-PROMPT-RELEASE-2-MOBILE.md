# Release 2 — Mobile-Optimierung + Logo-Rebrand

**Auftrag an Claude Code in VS Code**
**Projekt:** grundke-it.de (GitHub Pages Static Site)
**Datum:** 2026-04-10
**Erwartete Dauer:** 1 Durchlauf, ca. 4–6 Commits

---

## Kontext

Die Website läuft produktiv, der Desktop-Look gefällt. Auf Mobile
(iPhone, Android) ist die Seite aber **zu lang** und Elemente **zu groß**
(Abstände, Schriftgrößen, Cards). Außerdem soll das Logo im Header durch
die neue CI-konforme Variante ersetzt werden.

Die CI 2026.01 ist verbindlich:
- Primary Blau: `#0c4da2`
- Accent Cyan: `#26bdef`
- Font-Stack: Syne (Headlines), Manrope (Body), JetBrains Mono (Daten)

---

## Zieldefinition

Nach dem Release:
1. Die Mobile-Version ist ca. **40 % kürzer** als vorher (weniger Scroll-Weg)
2. Lesbarkeit und CTA-Sichtbarkeit sind besser
3. Das Header-Logo ist das neue CI-konforme PNG
4. Es gibt einen **Sticky Call-CTA** am unteren Rand (nur Mobile)
5. FAQ ist als natives Accordion umgesetzt (kein JS nötig)
6. Der Breakpoint-Ansatz ist **Mobile-First**
7. Desktop-Layout bleibt **optisch nahezu identisch** zur aktuellen Version

---

## Was **NICHT** angefasst werden darf

- `CNAME` Datei
- `favicon*`, `apple-touch-icon.png`, `android-chrome-*.png`, `site.webmanifest`
- Inhaltliche Texte (Leistungen, Preise, FAQ-Inhalte) — nur Struktur-Umbau
- Mail-Adressen, Telefonnummer, Impressum, Datenschutz, AGB (Inhalt)
- Der Ordner `zeit/` oder Zeit-Subdomain-Dateien
- `ionos-dns-vorher.md` / `ionos-dns-nachher.md` (Dokumentation)
- Preise (110 € kommunizierter Satz, nicht ändern)

---

## Schritt 1 — Header-Logo ersetzen

### Aktuell
In `index.html` und Unterseiten wird vermutlich `assets/img/logo-grundke-it.jpg`
oder `logo-grundke-it.gif` referenziert.

### Neu
Drei neue Dateien liegen bereits in `assets/img/`:
- `logo-grundke-it.png` — transparent, CI Primary Blau (für helle Header)
- `logo-grundke-it-white.png` — transparent, Weiß (für dunkle Header)
- `logo-grundke-it-badge.png` — weißer Text auf blauem Rounded-Rect (Aufkleber-Optik)

### Aufgabe
1. In allen HTML-Dateien (`index.html`, `impressum/index.html`, `datenschutz/index.html`, `agb/index.html`, `empfehlungen/index.html`, `kontakt/index.html`, `schulung/index.html`, `tree/index.html`, `404.html`) die Header-Logo-Referenz austauschen:
   - Wenn der Header hell ist → `logo-grundke-it.png`
   - Wenn der Header dunkel/farbig ist → `logo-grundke-it-white.png`
   - Wenn du ein "Badge-Look" willst (Standalone-Pille) → `logo-grundke-it-badge.png`
2. **Entscheide selbst anhand des aktuellen Header-CSS**, welche Variante passt. Dokumentiere die Wahl kurz im Commit-Message.
3. Das Logo muss folgende **Proportionen** haben, damit es zu den umgebenden Header-Elementen passt:
   - Höhe Header auf Mobile: ca. 56–64 px
   - Höhe Logo auf Mobile: ca. 36–40 px (CSS: `height: clamp(2.25rem, 8vw, 2.75rem); width: auto;`)
   - Höhe Header auf Desktop: ca. 72–80 px
   - Höhe Logo auf Desktop: ca. 44–52 px
4. `alt="Grundke IT-Service"` setzen
5. Das Logo verlinkt zur Startseite (`href="/"` bzw. `href="../"` bei Unterseiten)
6. Das alte `logo-grundke-it.jpg` und `logo-grundke-it.gif` **nicht löschen**, nur nicht mehr referenzieren

---

## Schritt 2 — CSS Custom Properties für Spacing + Typo

In der globalen CSS-Datei (`assets/css/main.css` oder wie auch immer sie heißt)
ganz oben im `:root`-Block **folgende Variablen ergänzen oder überschreiben**:

```css
:root {
  /* Spacing Scale (Mobile-First, skaliert nach oben via clamp) */
  --space-3xs: 0.25rem;
  --space-2xs: 0.5rem;
  --space-xs:  0.75rem;
  --space-sm:  1rem;
  --space-md:  1.5rem;
  --space-lg:  2rem;
  --space-xl:  3rem;
  --space-2xl: 4rem;
  --space-3xl: 6rem;

  /* Section Padding (vertikal) — der größte Hebel */
  --section-pad-y: clamp(2.5rem, 8vw, 6rem);
  --section-pad-x: clamp(1rem, 4vw, 2rem);

  /* Typography Scale */
  --fs-hero:  clamp(1.875rem, 7vw, 3.75rem);  /* H1 Hero */
  --fs-h1:    clamp(1.625rem, 5.5vw, 2.75rem);
  --fs-h2:    clamp(1.375rem, 4.5vw, 2.25rem);
  --fs-h3:    clamp(1.125rem, 3.5vw, 1.5rem);
  --fs-body:  clamp(0.9375rem, 2.6vw, 1.0625rem);
  --fs-sm:    clamp(0.8125rem, 2.2vw, 0.9375rem);

  /* Line Heights */
  --lh-tight: 1.15;
  --lh-snug:  1.35;
  --lh-body:  1.6;

  /* Container */
  --container-max: 1200px;
}

/* Verhindert ungewolltes iOS-Font-Upscaling */
html { -webkit-text-size-adjust: 100%; }
body { font-size: var(--fs-body); line-height: var(--lh-body); }
```

Dann **alle Stellen im CSS** finden, an denen hart-codierte Werte wie
`padding: 80px 0;`, `font-size: 48px;`, `margin-bottom: 60px;` vorkommen,
und sie **schrittweise** durch die Custom Properties ersetzen. Das ist der
Hauptteil der Arbeit.

---

## Schritt 2.5 — Highlight-Effekt für Primary-Sektionen (CI-konform)

Auf der aktuellen Seite gibt es bereits einen CTA-Block mit einem subtilen
radialen Highlight in der Mitte (die Mitte wirkt minimal heller als die
Ränder, als würde das Blau "aufgehen"). Dieser Effekt soll als **wieder-
verwendbares Utility-Pattern** etabliert werden und auf allen Sektionen
mit `background-color: var(--accent)` (Primary Blau) anwendbar sein.

### CSS-Variable ergänzen

Im `:root`-Block ergänzen:

```css
:root {
  /* Radialer Highlight-Overlay (subtil, CI-konform) */
  --section-highlight:
    radial-gradient(
      ellipse 75% 65% at 50% 50%,
      rgba(255, 255, 255, 0.14) 0%,
      rgba(255, 255, 255, 0.07) 35%,
      rgba(255, 255, 255, 0.00) 60%,
      rgba(0, 0, 0, 0.10) 100%
    );
}
```

**Erklärung:**
- Der Overlay liegt über der CI-Primärfarbe, ändert sie aber nicht
- Mitte: 14 % weiß → leichter Glow
- Rand (60 %): neutral
- Ecken: 10 % schwarz → minimal dunkler
- Das Ergebnis ist ein subtiler "aufgehender" Effekt, der sich automatisch
  an jede Sektionsbreite anpasst (Ellipse skaliert mit Container)

### Utility-Class

```css
.section-primary {
  background-color: var(--accent, #0c4da2);
  background-image: var(--section-highlight);
  color: #ffffff;
}
```

Diese Klasse überall dort einsetzen, wo aktuell eine flächige Primary-Blau-
Section ist — konkret mindestens:
- CTA-Banner "Du hast eine Frage oder ein Problem?"
- Eventuell: Hero-Section (falls Primary-Blau)
- Pricing-Highlight-Karte (falls Primary-Blau)
- Footer-Top-Bereich (falls Primary-Blau)

### Ältere harte Backgrounds ersetzen

Suchen nach:
```
grep -rn "background: *#0c4da2\|background-color: *#0c4da2" assets/css/
```

Jeder Treffer prüfen, ob es sich um einen Block handelt, bei dem der
Highlight-Effekt passen würde. Wenn ja: die Klasse `.section-primary`
zusätzlich am HTML-Element ergänzen **oder** das `background-image: var(--section-highlight);`
an Ort und Stelle im CSS ergänzen (ohne `background-color` zu entfernen).

**Wichtig:**
- Der Effekt muss **subtil** bleiben — kein Disco-Effekt, kein Drama
- Auf sehr kleinen Viewports (< 480 px) ist der radiale Verlauf fast
  unsichtbar und das ist auch gut so
- Keine zweite Farbe reinmischen (kein Cyan, kein Helles Blau aus der
  Palette) — es soll wirken wie natürliches Licht auf einer blauen Fläche
- Bei Texten auf der Sektion muss der Kontrast (WCAG AA) gewahrt bleiben.
  Falls Text auf dem hellsten Punkt liegt, ggf. `text-shadow: 0 1px 2px rgba(0,0,0,0.2);`
  als dezenten Lift ergänzen

### Optional: Gleicher Effekt auf Accent-Cyan-Flächen

Falls es Sektionen mit Accent-Cyan-Hintergrund (`#26bdef`) gibt:

```css
.section-accent {
  background-color: var(--accent-cyan, #26bdef);
  background-image: var(--section-highlight);
  color: #ffffff;
}
```

Gleiche Overlay-Variable, passt auf beide Farben, weil sie nur
transparent-weiß/schwarz mischt.

**Regeln dabei:**
- Keine Custom Property in eine Rule einfügen, bei der sie nicht passt —
  wenn du unsicher bist, behalte den Originalwert und markiere mit
  `/* TODO: scale */` für einen späteren Durchgang.
- Media Queries, die nur auf Desktop greifen (`@media (min-width: 1024px)`),
  brauchen meist keine Änderung.
- Mobile-Styles (alles außerhalb von Media Queries oder in `@media (max-width: 768px)`) → hier vorher **immer** prüfen ob die Mobile-First-Logik (siehe Schritt 6) greift.

---

## Schritt 3 — Hero-Sektion entschlacken

In der Hero-Sektion (erste Section nach dem Header):

1. `min-height: 100vh;` → `min-height: auto;` für Mobile
2. Ab `@media (min-width: 768px)` wieder `min-height: 70svh;` (oder 80svh)
3. H1 muss `font-size: var(--fs-hero);` bekommen
4. Padding: `padding: var(--section-pad-y) var(--section-pad-x);`
5. CTA-Buttons Full-Width auf Mobile:
   ```css
   .hero .btn {
     display: block;
     width: 100%;
     max-width: 420px;
     margin-inline: auto;
   }
   @media (min-width: 640px) {
     .hero .btn { display: inline-block; width: auto; }
   }
   ```
6. Der Hintergrund-Image (falls vorhanden) sollte `background-position: center;` und `background-size: cover;` haben.

---

## Schritt 4 — Cards / Kacheln kompakter

Alle Card-Komponenten (Leistungen, Tarife, FAQ-Vorschau, etc.):

- Innen-Padding: `padding: clamp(1rem, 3vw, 1.75rem);` statt hartkodiert
- Icons innen: `width/height: clamp(2.25rem, 6vw, 3rem);` statt 64–80 px
- H3 innen: `font-size: var(--fs-h3);`
- Gap zwischen Cards: `gap: clamp(1rem, 3vw, 2rem);`
- Auf Mobile 1-spaltig, auf Tablet 2-spaltig, auf Desktop 3-spaltig:
  ```css
  .card-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: clamp(1rem, 3vw, 2rem);
  }
  @media (min-width: 640px) {
    .card-grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (min-width: 1024px) {
    .card-grid { grid-template-columns: repeat(3, 1fr); }
  }
  ```

---

## Schritt 4.5 — Flip-Cards Mobile-Fix (Pain/Solution-Kacheln)

**Kontext:** Die Pain-/Solution-Kacheln (aktuell 4×2-Grid, Beispiele: *"Mein ITler ist nicht erreichbar"*, *"Es muss heute noch laufen"*, *"MEINE LÖSUNG"* auf der Rückseite) drehen sich aktuell per **`:hover`**. Auf Touch-Geräten funktioniert Hover nicht zuverlässig — iOS simuliert einen ersten "Fake-Tap", der zweite Tap löst dann den Link aus. Das Ergebnis: User wissen nicht, ob sie gerade geflippt haben oder gleich navigieren. Unbrauchbar.

### Ziel

- **Desktop (Pointer + Hover vorhanden):** Flip wie bisher per Hover.
- **Mobile / Touch:** Tap auf die Karte toggelt die `.is-flipped`-Klasse. Zweiter Tap auf den jetzt sichtbaren "LÖSUNG ANSEHEN"-Link navigiert.
- **Accessibility:** Karten sind per Keyboard erreichbar (`Enter`/`Space`), `aria-expanded` spiegelt den Zustand, kein Layout-Sprung.

### HTML — Karte als Button-Wrapper

Jede Karte bekommt einen umschließenden `<button>` bzw. ein Element mit `role="button"`. Der Link auf der Rückseite bleibt ein normaler `<a>`, ist aber nur klickbar wenn die Karte geflippt ist (per `pointer-events`).

```html
<article class="flip-card" data-flip>
  <button type="button" class="flip-card__inner"
          aria-expanded="false"
          aria-label="Pain anzeigen / Lösung ansehen">
    <div class="flip-card__face flip-card__face--front">
      <h3>Mein ITler ist nicht erreichbar</h3>
      <span class="flip-card__hint">LÖSUNG ANSEHEN</span>
    </div>
    <div class="flip-card__face flip-card__face--back">
      <span class="flip-card__badge">MEINE LÖSUNG</span>
      <p>Passwort vergessen, Account gesperrt … Meld dich. Ich löse das schnell und sicher.</p>
      <a href="tel:+4917825844 38" class="flip-card__cta">Jetzt anrufen</a>
    </div>
  </button>
</article>
```

> **Wichtig:** Der `<button>` umschließt beide Faces. Der `<a>` auf der Back-Seite ist ein *echtes* Link-Element — bitte `event.stopPropagation()` im JS, damit ein Klick auf den Link **nicht** auch noch die Karte toggelt.

### CSS — Hover für Desktop, Class-Toggle für Touch

```css
.flip-card {
  perspective: 1000px;
}

.flip-card__inner {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  transform-style: preserve-3d;
  transition: transform 0.55s cubic-bezier(0.4, 0.0, 0.2, 1);
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
  text-align: left;
}

.flip-card__face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: 12px;
  padding: clamp(1rem, 3vw, 1.5rem);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.flip-card__face--front {
  background: var(--bg-card);
  color: var(--text-primary);
}

.flip-card__face--back {
  background: var(--accent);
  color: #ffffff;
  transform: rotateY(180deg);
}

/* Flipped-Zustand (JS setzt aria-expanded="true") */
.flip-card__inner[aria-expanded="true"] {
  transform: rotateY(180deg);
}

/* Desktop-Hover NUR wenn Pointer+Hover vorhanden */
@media (hover: hover) and (pointer: fine) {
  .flip-card:hover .flip-card__inner {
    transform: rotateY(180deg);
  }
}

/* Link auf Back-Seite erst klickbar wenn sichtbar */
.flip-card__cta {
  pointer-events: none;
}
.flip-card__inner[aria-expanded="true"] .flip-card__cta,
.flip-card:hover .flip-card__cta {
  pointer-events: auto;
}
```

> **`@media (hover: hover) and (pointer: fine)`** ist der saubere Weg um Hover **nur** für Maus-Geräte zu aktivieren. Touch-Devices ignorieren diesen Block komplett — genau was wir wollen.

### JavaScript — minimaler Toggle-Handler

Eine einzige IIFE am Ende von `main.js` (oder als separate `flip-cards.js`):

```javascript
/* Flip-Cards: Tap-to-Toggle für Touch, Accessibility für Keyboard */
(() => {
  const cards = document.querySelectorAll('[data-flip] .flip-card__inner');
  cards.forEach(btn => {
    btn.addEventListener('click', (e) => {
      // Klicks auf den internen Link nicht abfangen
      if (e.target.closest('a')) {
        e.stopPropagation();
        return;
      }
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
    });
  });
})();
```

Keine externe Library, kein Framework. ~15 Zeilen, funktioniert überall.

### Was explizit NICHT passieren darf

- **Kein `onclick`-Attribut im HTML** — Separation of Concerns.
- **Kein `:focus`-Hack** für das Flippen auf Touch — das bricht Tastatur-Navigation.
- **Keine Doppel-Navigation:** Klick auf den inneren `<a>` darf nur den Link auslösen, nicht zusätzlich toggeln.
- **Kein Layout-Sprung:** Die Karte muss auf beiden Seiten die gleiche Höhe haben (`aspect-ratio` + absolute Faces erledigen das).

### Verifikation

1. **Desktop (Chrome DevTools → Device Mode aus):** Mauszeiger auf Karte → flippt. Klick auf "Jetzt anrufen" → wählt Nummer.
2. **Mobile (Device Mode an, iPhone 14):** Tap auf Karte → flippt sanft. Zweiter Tap auf den Link → navigiert.
3. **Keyboard:** Tab auf Karte → Enter → flippt, `aria-expanded="true"`. Tab weiter → Link fokussiert → Enter → navigiert.
4. **`prefers-reduced-motion`:** Transition-Duration bei `@media (prefers-reduced-motion: reduce)` auf `0.01ms` setzen (generell für die Site).

---

## Schritt 5 — FAQ als natives Accordion

**Vorher:** Vermutlich H3 + P untereinander.
**Nachher:** Jede FAQ-Frage als `<details>`-Element.

```html
<section class="faq">
  <h2>Häufig gestellte Fragen</h2>
  <div class="faq-list">

    <details class="faq-item">
      <summary>
        <span class="faq-question">Was kostet eine Stunde IT-Support?</span>
        <span class="faq-icon" aria-hidden="true">+</span>
      </summary>
      <div class="faq-answer">
        <p>110 € netto pro Stunde im 15-Minuten-Takt, ohne Wochenendzuschlag.</p>
      </div>
    </details>

    <!-- weitere Items -->

  </div>
</section>
```

**CSS dazu:**
```css
.faq-list { display: flex; flex-direction: column; gap: var(--space-xs); }
.faq-item {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: var(--space-sm) var(--space-md);
  transition: background 0.2s ease;
}
.faq-item summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  list-style: none;
  font-weight: 600;
  font-size: var(--fs-body);
  min-height: 44px;  /* Touch-Target */
}
.faq-item summary::-webkit-details-marker { display: none; }
.faq-icon {
  font-size: 1.5rem;
  line-height: 1;
  transition: transform 0.2s ease;
  color: var(--accent-cyan, #26bdef);
}
.faq-item[open] .faq-icon { transform: rotate(45deg); }
.faq-answer {
  padding-top: var(--space-sm);
  color: var(--text-secondary, #555);
  line-height: var(--lh-body);
}
```

**Wichtig:** Die inhaltlichen FAQ-Texte **nicht verändern**, nur die HTML-Struktur
umbauen. Inhalte aus dem bestehenden FAQ-Bereich 1:1 übernehmen.

---

## Schritt 6 — Sticky Call-CTA (nur Mobile)

Direkt vor dem schließenden `</body>`-Tag einfügen:

```html
<a href="tel:+4917825844 38"
   class="sticky-call"
   aria-label="Anrufen 0178/258 44 38">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="2" stroke-linecap="round"
       stroke-linejoin="round" aria-hidden="true">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
  </svg>
  <span>Jetzt anrufen · 0178/258 44 38</span>
</a>
```

**CSS:**
```css
.sticky-call {
  display: none;  /* default: hidden */
}
@media (max-width: 767px) {
  .sticky-call {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-xs);
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    padding: 0.875rem 1rem calc(0.875rem + env(safe-area-inset-bottom));
    background: var(--accent, #0c4da2);
    color: #ffffff;
    font-weight: 600;
    font-size: var(--fs-body);
    text-decoration: none;
    box-shadow: 0 -2px 12px rgba(0,0,0,0.15);
    min-height: 52px;
  }
  .sticky-call:hover { background: #0a4290; }
  /* Body bekommt unten extra Padding, damit Inhalte nicht vom Sticky verdeckt werden */
  body { padding-bottom: 64px; }
}
```

**Wichtig:**
- `env(safe-area-inset-bottom)` ist für iPhones mit Home-Indicator
- Die Telefonnummer **exakt** `+4917825844 38` als `tel:`-Link (Leerzeichen sind erlaubt)
- Auf Tablet/Desktop (`min-width: 768px`) wird das Element komplett versteckt

---

## Schritt 7 — Mobile-First Breakpoints etablieren

Der aktuelle CSS-Stil ist vermutlich Desktop-First (`@media (max-width: X)`
als Override). Die neue Logik:

**Alles außerhalb von Media Queries = Mobile-Default.**
**Dann nach oben skalieren mit:**

```css
/* Tablet */
@media (min-width: 640px)  { ... }
/* Large Tablet / Small Desktop */
@media (min-width: 1024px) { ... }
/* Desktop / Full Layout */
@media (min-width: 1280px) { ... }
```

**Vorgehen:**
1. **Nicht pauschal** das ganze CSS umbauen — das Risiko, das Desktop-Layout
   zu zerschießen, ist zu hoch.
2. **Punktuell** vorgehen: Grid-Layouts, Hero-Höhe, Typografie, Cards, Nav-Toggle.
3. Jeder Bereich bekommt einen eigenen Commit.
4. Zwischen den Commits **jeweils lokal testen**:
   - Chrome DevTools Mobile-View (375×667 iPhone SE, 390×844 iPhone 13, 768×1024 iPad)
   - Desktop (1280, 1440, 1920)

---

## Schritt 8 — Verifikation

Nach allen Änderungen:

1. `grep -rn "min-height: 100vh" assets/css/` → sollte leer sein oder nur noch in Dark-Hero
2. `grep -rn "padding: 80px\|padding: 100px" assets/css/` → sollte leer sein
3. `grep -rn "font-size: 48px\|font-size: 56px\|font-size: 64px" assets/css/` → sollte leer sein (ersetzt durch clamp())
4. `grep -rn "logo-grundke-it.jpg\|logo-grundke-it.gif" .` → sollte nur noch in alten Backup-Dateien auftauchen, nicht in aktiven HTML
5. Alle HTML-Dateien müssen validiert sein (W3C Validator, falls CLI verfügbar: `vnu`)
6. Lighthouse-Audit (mobile) — Performance sollte mindestens gleich bleiben, Accessibility 95+

---

## Schritt 9 — Commit-Strategie

Ein sauberer Commit pro Thema (nicht alles in einen Mega-Commit):

```
feat(logo): CI-konformes PNG-Logo im Header aller Seiten
feat(css): Spacing/Typography Custom Properties + clamp() Skalierung
refactor(hero): min-height auto auf Mobile, CTA full-width
refactor(cards): kompakte Padding/Icon-Größen mit clamp()
fix(flip-cards): Tap-to-Toggle für Touch, Hover nur auf Pointer:fine
feat(faq): FAQ als natives details/summary Accordion
feat(mobile): Sticky Call-CTA für Mobile-Viewports
refactor(css): Mobile-First Breakpoints (640/1024/1280)
```

Jeder Commit sollte für sich allein lauffähig sein — Rollback möglich.

---

## Schritt 10 — Abschluss & Report

Nach dem letzten Commit:
1. `git log --oneline -10` in die Response
2. Kurzer Bericht was geändert wurde (max. 10 Zeilen)
3. Hinweis wenn etwas übersprungen wurde oder Unsicherheit besteht
4. Liste der Dateien die berührt wurden
5. **Nicht selbständig pushen** — Andy macht das manuell nach Review

---

## Notfall-Regel

Wenn du an irgendeiner Stelle unsicher bist ob eine Änderung das
Desktop-Layout zerschießt → **stoppe, dokumentiere im Kommentar, mache
eine konservative Alternative**, und melde es am Ende im Bericht.

**Kein Trial-and-Error. Erst verstehen, dann umsetzen.**

---

## CI-Farbreferenz

| Rolle | Hex |
|---|---|
| Primary Blau | `#0c4da2` |
| Accent Cyan | `#26bdef` |
| BG Light | `#f4f7fc` |
| Accent BG | `#e8f0fb` |
| Text Primary | `#111111` |
| Text Secondary | `#555555` |
| Border | `#d0daea` |
| Danger | `#c0392b` |
| Warning | `#cc8800` |
| Success | `#1a7a5e` |

---

**CI 2026.01 · Grundke IT-Service · www.grundke-it.de**
