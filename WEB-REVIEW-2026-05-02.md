# Web-Review grundke-it.de · 2026-05-02

**Methode:** 3 parallele Subagents (UI/Code-Quality, Copywriting, SEO/GEO) · 36 Findings · 2 Doppel → **34 unique**
**Domänen:** UI/Code · Copy · SEO/GEO

---

## P1 — Kritisch (8)

### 1. UI+SEO · Fünf `<h1>` im Hero-Slider
**Datei:** `index.html:1264, 1285, 1306, 1327, 1348` · `.slide-h1`
**Problem:** Jeder Slide ist `<h1>` → 5 konkurrierende Top-Headings. SEO entwertet, Screenreader-Outline kaputt.
**Fix:** Slide 1 als `<h1>`, Slides 2–5 als `<h2 class="slide-h1">` (CSS unverändert).

### 2. SEO · Domain-Konflikt apex vs. www → Duplicate Content
**Datei:** `CNAME` (apex) vs. alle Canonicals `https://www.grundke-it.de/`
**Fix:** Bei www bleiben → IONOS-Forwarding apex→www (301) aktivieren.

### 3. Copy · Testimonials mit sichtbaren Platzhaltern
**Datei:** `index.html:2147–2158`
**Problem:** Autor-Felder zeigen `⚠ [Vorname Nachname]` und `⚠ [Branche] · [Ort]` → zerstört Glaubwürdigkeit.
**Fix:** Sektion entfernen oder durch ehrliche Variante ersetzen: „Echte Kundenstimmen folgen, sobald die Freigaben da sind."

### 4. UI · Hero-Slider ignoriert `prefers-reduced-motion`
**Datei:** `assets/js/main.js:58–61, 78` + `index.html:238`
**Fix:** `matchMedia('(prefers-reduced-motion: reduce)')` checken → Auto-Advance + Bildzoom abschalten.

### 5. UI · Sticky-Bar verdeckt Anker-Sprünge
**Datei:** `style.css:255+`
**Fix:** Global `section[id], h1, h2, h3 { scroll-margin-top: calc(var(--nav-h) + 1rem); }`.

### 6. Copy · Trust-Bar-Ticker mit Doubletten
**Datei:** `index.html:1404–1419`
**Problem:** „€110/h · 15-Min-Takt" und „20+ Jahre" jeweils 2× → Lückenfüller-Optik.
**Fix:** 8 unique Items + harte Trust-Signale: „IHK-Fachinformatiker", „BSI-konforme 3-2-1-Backups", „X dokumentierte Einsätze".

### 7. Copy · CTA-Sub „so schnell wie möglich"
**Datei:** `index.html:2232–2233` (`#kontakt`)
**Fix:** Konkrete SLA: „Telefon, WhatsApp oder Mail – Rückmeldung in der Regel binnen 1 Stunde an Werktagen. Premium-Kunden sofort."

### 8. SEO · Sitemap-Inkonsistenz Priority/Changefreq
**Datei:** `sitemap.xml:17–21`
**Fix:** Priority/Changefreq angleichen oder beide entfernen, nur `lastmod` belassen.

---

## P2 — Wichtig (14)

### 9. SEO · Hero-Bilder ohne LCP-Preload (CSS background-image)
**Datei:** `index.html:1259, 1280, 1301, 1322, 1343`
**Fix:** `<link rel="preload" as="image" fetchpriority="high">` für Slide 1; `<picture>`+WebP statt CSS-bg.

### 10. SEO · Person-Schema fehlt (E-E-A-T-Signal)
**Datei:** `index.html:113`
**Fix:** Eigenständigen `Person`-Block: `jobTitle`, `description`, `sameAs` (LinkedIn/Insta), `knowsAbout`. Über `@id` mit LocalBusiness verknüpfen.

### 11. SEO · BreadcrumbList-Schema fehlt überall
**Datei:** alle Unterseiten
**Fix:** Pro Unterseite `BreadcrumbList`-JSON-LD → SERP-CTR.

### 12. SEO · Interne `/fernwartung`-Links ohne Trailing-Slash → 301-Hop
**Datei:** `index.html:1247`, alle Subpages
**Fix:** Konsequent `href="/fernwartung/"`.

### 13. SEO · LocalBusiness zu generisch + keine Reviews
**Datei:** `index.html:64`
**Fix:** `@type:["LocalBusiness","ProfessionalService"]`. Reviews-Markup sobald Bewertungen da sind.

### 14. UI · Inline `onmouseover/onmouseout` statt CSS
**Datei:** `index.html:1904, 1927, 1951` (Schulungs-Cards)
**Fix:** `.sch-card:hover, .sch-card:focus-visible` in CSS – Inline-Handler raus.

### 15. UI · `color-scheme: dark` fehlt
**Datei:** `style.css:14` (`:root`)
**Fix:** `color-scheme: dark;` ergänzen.

### 16. UI · Touch-Optimierungen fehlen
**Fix:** `a, button { touch-action: manipulation; -webkit-tap-highlight-color: transparent; }`.

### 17. UI · Modal: kein `overscroll-behavior: contain`
**Datei:** `index.html:536–540`
**Fix:** `.modal-body, .modal-dialog { overscroll-behavior: contain; }`.

### 18. UI · Logo `<img>` ohne `width`/`height` → CLS
**Datei:** `index.html:1223`, `kontakt:88` u.a.
**Fix:** `width="180" height="46"` (oder reale Maße).

### 19. Copy · Services-Sub: „ich finde eine Lösung" (CLAUDE.md-Verbot)
**Datei:** `index.html:1712`
**Fix:** „Von der akuten Störung bis zur Vollbetreuung – ein Ansprechpartner für Netzwerk, M365, Sicherheit und Hardware."

### 20. Copy · Service-Karte „Drucker"
**Datei:** `index.html:1719`
**Fix:** „… auch herstellerübergreifend (Brother, HP, Epson, Vectron, ready2order)."

### 21. Copy · Zielgruppen-Hero
**Datei:** `index.html:2099–2100`
**Fix:** „Acht Branchen, ein Betreuer. Raum München Ost, 5 bis 50 Arbeitsplätze."

### 22. Copy · About-Section fehlt komplett
**Datei:** `index.html` (zwischen Ablauf und Testimonials)
**Fix:** Eigene Sektion „Wer das hier macht" mit Andreas Grundke, 20+ Jahre IT, Fachinformatiker, parallel BI bei Bank.

---

## P3 — Nice-to-have (12)

| # | Domain | Datei:Zeile | Finding · Fix |
|---|---|---|---|
| 23 | SEO | `index.html:6` | Title 99 Zeichen → SERP-Truncation. Kürzen: „IT-Service München Ost · Grasbrunn & Ottobrunn \| Grundke IT" (~58) |
| 24 | SEO | `index.html:8` | `meta name="keywords"` → entfernen (seit 2009 ignoriert) |
| 25 | SEO | `index.html:2168` vs `:2294` | FAQPage-Schema (12 Q&A) ≠ sichtbares FAQ → angleichen |
| 26 | SEO | `index.html:23–27` | `og:image:type` + `twitter:site` + `logo` als `ImageObject` mit width/height |
| 27 | UI | `index.html:1550, 1882, 2147` | Mix aus „…" und "…" → konsequent deutsche Quotes |
| 28 | UI | `style.css:914` (`.testi-role`) | `--text3` auf `--bg2` mit .65rem nahe WCAG-AA → auf `--text2` heben |
| 29 | UI | `index.html:1997, 2020, 2044, 2067` | Preisspalten ohne `tabular-nums` → springen optisch |
| 30 | UI | `assets/js/main.js:133–161` | Lenis ignoriert reduced-motion → matchMedia-Guard vor `new Lenis()` |
| 31 | UI | global, 11 Stellen | `transition: all` durch property-spezifische Transitions ersetzen |
| 32 | Copy | `kontakt/index.html:114` | „so schnell wie möglich" → „Rückmeldung in der Regel binnen 1 Stunde an Werktagen" |
| 33 | Copy | `fernwartung/index.html:233` | Tonbruch: siezt während Site duzt → auf Du-Form |
| 34 | Copy | `404.html:51–52` | Generisch → persönlich: „Tippfehler, alter Link, oder ich hab umgebaut. Ruf an, dann führ ich dich zum Richtigen." |

---

## Quick Wins (Hebel/Aufwand-Ranking)

**Sofort (≤ 5 Min, hoher Hebel):** #3, #1, #33, #24, #15, #5
**Kurz (15–30 Min, sehr hoher Hebel):** #2, #6, #7, #10, #9
**Mittel (≥ 1 Std, hoher Hebel):** #22, #11, #19/20/21

**Top 3 wenn nur Zeit für drei:** #3 (Testimonials-Platzhalter), #1 (H1-Multiplexing), #2 (apex→www Forwarding).

---

## Implementiert in diesem Pass (2026-05-02)

Siehe `git log --oneline` ab Commit dieser Datei.

**Offen (benötigt Rückfrage / Inhaltsentscheidung):**
- #2 IONOS DNS-Forwarding (kein Code)
- #3 Testimonials: löschen oder ersetzen?
- #6 Trust-Bar: welche 8 Items, welche Trust-Signale?
- #7 #19 #20 #21 #22 Copy-Pass: Wortlaut-Entscheidungen
- #9 LCP-Preload: WebP-Konvertierung der Hero-Bilder
- #10 Person-Schema: LinkedIn-/Instagram-URLs, Bio-Text
- #11 BreadcrumbList: Strukturentscheidung pro Page
- #13 Reviews-Markup: erste echte Bewertung erforderlich
- #23 Title rewrite: Branding-Entscheidung
- #25 FAQ-Schema vs. sichtbar: 8 zusätzliche Q&A formulieren
- #26 Twitter-Handle nicht verifiziert
