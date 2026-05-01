# Grundke IT-Service – Website

**© 2026 Grundke IT-Service · Andreas Grundke**
CI 2026.01 · Vanilla HTML + CSS + JS · Static Site

---

## Projektstruktur

```
grundke-it-website/
├── index.html              # Startseite
├── 404.html                # Fehlerseite
├── CNAME                   # GitHub Pages Custom Domain
├── robots.txt
├── sitemap.xml
├── assets/
│   ├── css/
│   │   └── style.css       # Shared CI 2026.01 Dark Mode Styles
│   ├── js/
│   │   └── main.js         # Shared JavaScript (Nav, Dropdown, Slider, FAQ, vCard)
│   └── agb/
│       └── AGB-Grundke-IT-Service.pdf   # ← PDF hier ablegen!
├── tree/
│   └── index.html          # QR-Code Landingpage (Visitenkarte / Geräteaufkleber)
├── empfehlungen/
│   └── index.html          # Amazon Affiliate Produktempfehlungen
├── kontakt/
│   └── index.html          # Kontaktseite
├── impressum/
│   └── index.html          # Impressum
├── datenschutz/
│   └── index.html          # Datenschutzerklärung
├── agb/
│   └── index.html          # AGB (Link zum PDF)
└── .github/
    └── workflows/
        └── deploy.yml      # GitHub Actions → auto deploy bei git push
```

---

## Setup – Einmalig

### 1. GitHub Repository anlegen
```bash
# Neues Repo auf github.com anlegen: "grundke-it-website" (Public)
# Dann lokal:
git init
git remote add origin https://github.com/DEIN-USERNAME/grundke-it-website.git
git add .
git commit -m "Initial commit – CI 2026.01"
git push -u origin main
```

### 2. GitHub Pages aktivieren
- GitHub → Repository → Settings → Pages
- Source: **GitHub Actions**
- Fertig – Deploy läuft automatisch

### 3. IONOS Domain einrichten
In IONOS DNS folgende Einträge setzen:

| Typ | Host | Ziel |
|-----|------|------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | DEIN-USERNAME.github.io |

> ⚠️ DNS-Propagation kann bis zu 24h dauern.

### 4. HTTPS aktivieren
- GitHub → Repository → Settings → Pages → "Enforce HTTPS" ✅

---

## Deployment – Täglich

```bash
# Änderung machen, dann:
git add .
git commit -m "Kurze Beschreibung der Änderung"
git push
# → GitHub Actions deployt automatisch in ~60 Sekunden
```

---

## Offene TODOs nach Go-Live

- [ ] **AGB PDF** unter `assets/agb/AGB-Grundke-IT-Service.pdf` ablegen
- [ ] **Google Review Link** in `tree/index.html` eintragen (Zeile mit `g.page/r/XXXXXXXXX`)
- [ ] **Echte Telefonnummer** überall geprüft? `+491782584438` ✅
- [ ] **Google Analytics / Search Console** einrichten
- [ ] **Kundenstimmen** in `index.html` mit echten Namen befüllen
- [ ] **Kunden-Logos** Sektion ergänzen (wenn Freigaben vorliegen)
- [ ] **Profilfoto** Binek-Foto einbauen sobald verfügbar
- [ ] **Empfehlungen-Seite** mit allen Amazon Affiliate Links befüllen
- [ ] **Alter WordPress-Stand** bei IONOS deinstallieren
- [ ] **Google Business** – alter Standort Wagingerstraße schließen

---

## Technologie

| Schicht | Technologie |
|---------|-------------|
| Markup | HTML5, Vanilla |
| Styling | CSS3, CI 2026.01 Dark Mode |
| Icons | Lucide (SVG inline, kein CDN) |
| Fonts | Google Fonts (Syne + Manrope + JetBrains Mono) |
| JS | Vanilla JS (kein Framework) |
| Hosting | GitHub Pages (kostenlos) |
| Domain | IONOS → CNAME |
| Deploy | GitHub Actions (auto bei git push) |

---

## Kontakt / Support

Andreas Grundke · info@grundke-it.de · 0178 258 44 38
