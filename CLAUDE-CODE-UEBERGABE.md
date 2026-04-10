# Übergabe-Prompt für Claude Code / VS Code
# Diesen Text als ersten Prompt in ein neues Claude Code Projekt einfügen

---

## Kontext

Ich arbeite am **Grundke IT-Service Marketing & Go-Live Masterpaket** (Schritt 2: Website Go-Live).
Die Website wurde von CloudJet erstellt und liegt fertig als HTML/CSS/JS Projekt vor – kein Framework, Vanilla-Stack.

## Projektordner

Öffne den Ordner `grundke-it-website` in diesem Verzeichnis. Das ist ein fertiges statisches Website-Projekt für **GitHub Pages**.

## Was bereits erledigt ist (Schritt 1 – in Cowork gemacht)

- Google Business Profil bereinigt und aktualisiert (CI 2026.01)
- WISSEN4Bastler Profil gelöscht
- Gemeinde Grasbrunn ceasy-Portal aktualisiert (wartet auf Freigabe)
- 11880.com + meinestadt.de E-Mails versendet (alte Einträge korrigieren)

## Was jetzt zu tun ist (Schritt 2 – hier in VS Code)

### Phase 1: Lokal prüfen und anpassen
1. **Projekt analysieren** – lies die Struktur, index.html, CSS, alle Unterseiten
2. **Live Server starten** – damit ich die Seite lokal im Browser sehen kann
3. **Prüfen und anpassen:**
   - CNAME-Datei enthält `grundke-it.de` → prüfen
   - Alle Links intern testen (Impressum, Datenschutz, AGB, Kontakt, /tree, /empfehlungen)
   - Texte gegen CI 2026.01 prüfen (Du-Form, aktuelle Dienstleistungen, Preise **110 € netto** — 90 € ist nur historischer Bestandskundensatz, nicht kommunizieren)
   - Hero-Image: Das lizenzierte Bild liegt unter `../Support/power-digital-marketing-P_dneF5Pz_c-unsplash_1200x800.jpg`
   - Google Review Link in `tree/index.html` – Platzhalter `g.page/r/XXXXXXXXX/review` ersetzen (muss ich dir geben)
   - GA4 Mess-ID – wird später eingetragen (Platzhalter lassen oder `G-XXXXXXXXXX` markieren)
   - AGB-PDF fehlt noch → `assets/agb/` – Hinweis an mich geben

### Phase 2: Git + GitHub (erst wenn lokal alles passt)
1. `git init` + Initial Commit
2. GitHub Repo `grundke-it-website` anlegen (Public, Free Plan für GitHub Pages)
3. Push zu GitHub
4. GitHub Pages aktivieren (Source: GitHub Actions, Workflow liegt unter `.github/workflows/deploy.yml`)

### Phase 3: DNS (mache ich selbst bei IONOS)
- A-Records: 185.199.108.153 – 185.199.111.153
- CNAME www → mein-username.github.io

## CI 2026.01 Farbprofil "Web" – Light Mode

| Rolle | Hex |
|---|---|
| Primary Blau | `#0c4da2` |
| Accent Cyan | `#26bdef` |
| Text Primary | `#111111` |
| Text Secondary | `#555555` |
| BG Light | `#f4f7fc` |
| Danger | `#c0392b` |
| Warning | `#cc8800` |
| Success | `#1a7a5e` |

Fonts: Manrope (UI), JetBrains Mono (Daten), Fira Code (Code)

## Firmendaten

- **Firma:** Grundke IT-Service
- **Inhaber:** Andreas Grundke
- **Adresse:** Beethovenring 16, 85630 Grasbrunn
- **Mobil:** 0178 2584438
- **E-Mail:** info@grundke-it.de
- **Web:** https://www.grundke-it.de
- **Stundensatz (kommuniziert):** 110 € netto, 15-Minuten-Takt, kein Wochenendzuschlag
- **Stundensatz (Bestandskunden, nur intern):** 90 € netto – historischer Satz, nicht auf Website/Werbung

## Wichtig

- **Erst lokal testen, dann pushen** – ich will die Seite im Browser sehen bevor sie online geht
- Kein Trial-and-Error – zielgerichtet arbeiten
- Code-Regeln beachten: vollständige Dateien, Kommentare, nachvollziehbar
- Kein Kundenverkehr vor Ort – Termine remote oder beim Kunden
