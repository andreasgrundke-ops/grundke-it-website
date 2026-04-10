# Claude Code · Website-Update Release 1
**Projekt:** Grundke IT-Service · `grundke-it-website`
**Datum:** 2026-04-10
**Autor:** Andreas Grundke (Konzept gemeinsam mit KI-Co-Pilot erarbeitet)
**CI:** 2026.01 · Profil „Web" · Light Mode

---

## Kontext für dich, Claude Code

Du arbeitest an der bestehenden Website `index.html` im Ordner `grundke-it-website` (VS Code Working Directory).
Die Seite ist eine Single-Page-Vanilla-HTML/CSS/JS-Website, vorbereitet für GitHub Pages + IONOS-DNS.

**Was du NICHT ändern darfst:**
- Grundstruktur der Sections-Reihenfolge — nur hinzufügen an den markierten Stellen.
- Hero-Slider-Slides (werden separat behandelt, Andreas entscheidet dort selbst).
- CI-Farben, Fonts, Grundlayout.
- Bereits existierende Texte außerhalb der hier explizit markierten Stellen.

**Was du machst:**
- Kleine, getrennte Commits pro Task (je ein Git-Branch `feature/task-X` wäre ideal).
- Nach jedem Task: kurze Zusammenfassung an Andreas, bevor du den nächsten startest.
- Kein Trial-and-Error — wenn etwas unklar ist: fragen.

**CI 2026.01 Farbreferenz (Light Mode / Profil Web):**

| Rolle | Hex |
|---|---|
| Primary Blau | `#0c4da2` |
| Accent Cyan | `#26bdef` |
| Text Primary | `#111111` |
| Text Secondary | `#555555` |
| Text Muted | `#888888` |
| Border | `#d0daea` |
| BG Light | `#f4f7fc` |
| Accent BG | `#e8f0fb` |
| Danger | `#c0392b` |
| Warning | `#cc8800` |
| Success | `#1a7a5e` |

**Fonts:** Manrope (UI), JetBrains Mono (Daten/Zahlen), Fira Code (Code).
**Sprache:** Du-Form, überall konsequent.

---

## Release 1 · Gesamtüberblick

Folgende Tasks gehören zu diesem Release. Reihenfolge ist empfohlen, aber nicht zwingend:

1. **Preis-Korrektur global** — 90 € → 110 € überall auf der Website
2. **IT-Schnellcheck-Section** mit Report-Vorschau-Modal („Blick ins Buch")
3. **Leistungen-Kachel „Sicherheits-Updates & Handlungsbedarf"** (neu)
4. **Leistungen-Kachel „Firewall, VPN & Netzwerkschutz"** (neu, mit Zahlen)
5. **„Aus der Praxis"-Story-Block** (Backup-Notfall-Beispiel)
6. **Neue Section „Projekte & Beratung"** inkl. Zweitmeinungs-Service
7. **FAQ-Erweiterung** um die Zweitmeinungs-Frage
8. **Managed-Service-Positionierung** — Kachel „Rund-um-Betreuung" + Pricing-Tabelle verbessern

---

## Task 1 · Preis-Korrektur global auf 110 €

**Warum:** Neupositionierung. Bestandskunden behalten intern weiterhin 90 €, das wird aber nirgendwo öffentlich kommuniziert. Die Website und alle Werbemittel zeigen ab sofort **110 € netto / Stunde · 15-Minuten-Takt**.

**Was zu tun ist:**
- Grep die komplette Website (`index.html`, `schulung/`, `kontakt/`, `impressum/`, `tree/`, `assets/` etc.) nach `90` im Zahlenkontext.
- Alle Vorkommnisse prüfen und dort ersetzen, wo es um den Stundensatz geht.
- Sei vorsichtig: „90" kann auch in anderen Kontexten vorkommen (Jahreszahlen, Versionsnummern, Prozentangaben). Nur Stundensatz-Bezüge ändern.
- Auch in `schulung/` prüfen — die Schulungspreise bleiben wie sie sind (135 €, 49 €, 165 €), aber der reguläre Stundensatz „danach" muss auf 110 € angepasst werden, falls dort 90 € stand.

**Wichtig:** Einheitliche Schreibweise: `110 € netto/Stunde` oder `110 €/h` — konsistent halten.

---

## Task 2 · IT-Schnellcheck-Section mit Report-Vorschau

### Warum das so wichtig ist

Der IT-Schnellcheck ist der **stärkste Lead-Magnet** der neuen Website. Ein kostenloser Termin ohne Verkaufsgespräch, bei dem der Kunde **etwas Konkretes in der Hand behält** (den Report), senkt die Eintrittshürde massiv. Gleichzeitig ist der Schnellcheck-Report die **Basis für die monatlichen Zustandsberichte im Business- und Premium-Paket** — es ist kein neuer Baustein, sondern ein Auszug aus einem ohnehin existierenden Modul. Das muss der Besucher spüren, damit er die Wertigkeit erkennt.

Die Herausforderung: „Kostenlos" klingt schnell nach Lockangebot. Dagegen hilft **Transparenz und Vorschau**: Der Besucher sieht, *was* geprüft wird und *wie* das Ergebnis aussieht — ähnlich wie die „Blick ins Buch"-Funktion bei Amazon.

### Platzierung

Neue Section `#schnellcheck` zwischen `#probleme` und `#leistungen`.

### Struktur (HTML/Layout)

```
<section id="schnellcheck" class="schnellcheck-section">
  <div class="container">
    <div class="schnellcheck-card">
      <div class="schnellcheck-icon">[Lucide: search-check, 48px, Cyan #26bdef]</div>
      <h2>Kostenloser IT-Schnellcheck</h2>
      <p class="sub">
        Bevor ich dir irgendwas verkaufe, schau ich's mir an. 30 bis 45 Minuten
        bei dir vor Ort. Danach bekommst du einen schriftlichen Kurz-Bericht mit
        den wichtigsten Handlungsempfehlungen — per Mail, in deinem Namen, zum Behalten.
      </p>

      <!-- Prüfpunkte-Liste mit Info-Icons -->
      <div class="schnellcheck-checklist">
        <h3>Was ich mir anschaue:</h3>
        <ul>
          <li>
            <span class="check-icon">[Lucide: check]</span>
            Netzwerk & WLAN
            <button class="info-btn" data-info="netzwerk" aria-label="Mehr Infos">
              [Lucide: info]
            </button>
          </li>
          <li>Arbeitsplätze & Server <button data-info="clients">ⓘ</button></li>
          <li>Microsoft 365 / E-Mail <button data-info="m365">ⓘ</button></li>
          <li>Virenschutz & Firewall <button data-info="security">ⓘ</button></li>
          <li>Datensicherung (Backup) <button data-info="backup">ⓘ</button></li>
          <li>Router & Internet-Anschluss <button data-info="router">ⓘ</button></li>
          <li>Drucker, Kameras, Peripherie <button data-info="peripherie">ⓘ</button></li>
          <li>Software-Aktualität (EOL, BSI) <button data-info="eol">ⓘ</button></li>
          <li>Benutzer, Passwörter, Dokumentation <button data-info="doku">ⓘ</button></li>
        </ul>
      </div>

      <!-- Was du bekommst -->
      <div class="schnellcheck-deliverable">
        <h3>Was du danach in der Hand hast:</h3>
        <p>
          Einen schriftlichen Kurz-Bericht (4–6 Seiten PDF) mit:
        </p>
        <ul class="deliverable-list">
          <li>Bestandsaufnahme deiner IT in Stichpunkten</li>
          <li>3 bis 5 konkrete Handlungsempfehlungen — priorisiert nach Dringlichkeit</li>
          <li>Ampel-Bewertung je Bereich (grün / gelb / rot)</li>
          <li>Offene Punkte, um die du dich kümmern solltest</li>
          <li>Unverbindliche Grob-Kostenschätzung, falls was ansteht</li>
        </ul>
        <button class="btn-secondary preview-btn" id="preview-report">
          [Lucide: file-text] Blick in einen Beispiel-Bericht
        </button>
      </div>

      <!-- Versprechen -->
      <div class="schnellcheck-promise">
        <span>✓ Kein Verkaufsgespräch</span>
        <span>✓ Keine Folgekosten</span>
        <span>✓ Bericht bleibt bei dir</span>
        <span>✓ Wiederverwendbar als Baseline</span>
      </div>

      <a href="#kontakt?betreff=schnellcheck" class="btn-primary btn-large">
        Jetzt Termin anfragen →
      </a>

      <p class="schnellcheck-hint">
        <small>
          Der Schnellcheck ist auch die Basis für die monatlichen Zustandsberichte
          in den <a href="#pricing">Business- und Premium-Paketen</a>.
        </small>
      </p>
    </div>
  </div>
</section>

<!-- Modal 1: Info-Popups (9 Stück, für die 9 Prüfpunkte) -->
<div class="info-modal" id="info-modal" hidden>
  <div class="info-modal-content">
    <button class="modal-close">×</button>
    <h3 id="info-modal-title"></h3>
    <div id="info-modal-body"></div>
  </div>
</div>

<!-- Modal 2: Report-Vorschau („Blick ins Buch") -->
<div class="preview-modal" id="preview-modal" hidden>
  <div class="preview-modal-content">
    <button class="modal-close">×</button>
    <h3>Auszug aus einem Beispiel-Bericht</h3>
    <p class="preview-note">
      Anonymisiertes Beispiel. So sieht dein Schnellcheck-Bericht aus.
    </p>
    <div class="report-preview">
      [visuelle Darstellung — siehe unten]
    </div>
    <p class="preview-footer">
      Möchtest du deinen eigenen Bericht bekommen?
      <a href="#kontakt?betreff=schnellcheck">Termin anfragen →</a>
    </p>
  </div>
</div>
```

### Inhalt der 9 Info-Popups (Text zum Einbauen)

Kurz, konkret, ohne Floskeln. Je Popup 2–3 Sätze.

**Netzwerk & WLAN**
> Ich schau mir die Ausleuchtung an, die Auslastung, wie viele Geräte drin sind, wo es klemmt. Bei Bedarf mit Mess-App. Wenn das WLAN instabil ist, weißt du danach warum.

**Arbeitsplätze & Server**
> Welche Rechner laufen, wie alt sind sie, wie voll sind sie, welcher Windows-Stand, welche Software ist drauf. Kurzcheck auf offensichtliche Bremsen und Risiken.

**Microsoft 365 / E-Mail**
> Welche Lizenzen hast du, wofür zahlst du zu viel oder zu wenig, wie ist die E-Mail konfiguriert, sind Spam und Phishing abgedeckt. Falls du noch bei POP3 oder einem alten Provider bist: ehrlicher Blick drauf.

**Virenschutz & Firewall**
> Läuft ein aktiver Virenschutz oder nur die Windows-Basisausstattung? Ist die Firewall richtig konfiguriert oder hängt alles offen im Netz? Gefahrenpunkte werden benannt, nicht dramatisiert.

**Datensicherung (Backup)**
> Hast du überhaupt ein Backup? Wo liegt es? Wann wurde es zuletzt getestet? Die 3-2-1-Regel ist der Maßstab — ich bewerte, wie weit du davon weg bist und was der einfachste Weg dahin wäre.

**Router & Internet-Anschluss**
> FritzBox? Speedport? Alter? Firmware aktuell? Wird der Router noch mit Sicherheits-Updates versorgt oder ist er End-of-Life? Welche Anschlussgeschwindigkeit kommt bei dir wirklich an.

**Drucker, Kameras, Peripherie**
> Was hängt alles mit drin, wo gibt's kleine Stolperfallen. Netzwerk-Drucker ohne Passwort? Unbekannte IP-Kameras? Ich prüfe, ob da was sichtbar wird, das später zum Problem werden kann.

**Software-Aktualität (EOL, BSI)**
> Welche Software hast du im Einsatz, läuft davon etwas auf End-of-Life? Gibt es aktuelle BSI-Warnungen, die dich betreffen? Beispiel: TP-Link-Router, bestimmte Exchange-Stände, alte FritzBox-Firmwares.

**Benutzer, Passwörter, Dokumentation**
> Gibt es eine saubere Benutzerstruktur, nutzen alle eigene Konten, gibt es einen Passwortmanager, existiert überhaupt eine Dokumentation für deine Vertretung oder den Notfall? Das ist oft der meistvergessene Punkt.

### Report-Vorschau („Blick ins Buch")

**Technische Umsetzung:** Zeig im Modal einen **gestylten Beispiel-Bericht** als HTML-Vorschau (kein PDF, keine Bilder — direkt im DOM gerendert, sieht dadurch scharf und editierbar aus).

Die Vorschau zeigt:

1. **Deckblatt** (oben, klein): Logo-Platzhalter, „IT-Schnellcheck · Beispielbetrieb GmbH · Stand 2026-04-01", blauer Streifen `#1F3864`
2. **„Management Summary"** (kurzer Absatz, 3 Sätze): Was wurde geprüft, was ist der Gesamtzustand, was sind die dringendsten Themen.
3. **Ampel-Übersicht** als 3-Spalten-Grid:
   - Netzwerk: 🟢 Grün — „Stabil, gut ausgelastet"
   - Backup: 🔴 Rot — „Kein externes Backup vorhanden"
   - Windows-Stand: 🟡 Gelb — „2 Rechner noch auf Windows 10 (EOL)"
   - Virenschutz: 🟢 Grün — „ESET aktiv"
   - Router: 🟡 Gelb — „FritzBox 7490 — keine Sicherheits-Updates mehr"
   - M365: 🟢 Grün — „Business Standard, Konfiguration sauber"
4. **Top-3-Handlungsempfehlungen** (nummeriert):
   1. **Sofort:** Externes Backup einführen (Synology NAS + Cloud-Sync). Geschätzte Kosten: ~900–1.200 €.
   2. **In den nächsten 4 Wochen:** Windows 10 Rechner auf Windows 11 migrieren oder ersetzen. 2× Migration je ca. 2 h.
   3. **Innerhalb 3 Monate:** FritzBox 7490 tauschen, da EOL. Alternative: UniFi Dream Router.
5. **Blur-Effekt** am unteren Rand der Preview: Der letzte Abschnitt verschwimmt langsam, mit Overlay-Text „Vollständiger Bericht nach deinem Schnellcheck". Das ist der „Teaser"-Effekt.

**Styling-Hinweise:**
- Report-Preview nutzt **Profil „Dokument"** aus CI 2026.01 (Navy `#1F3864` Header, Light-Blau `#D6E4F0` Zeilen), damit es wie ein echter Bericht aussieht — anders als die restliche Website.
- Monospace-Font (JetBrains Mono) für Datums- und Zahl-Angaben.
- Das Modal sollte auf Mobile auch funktionieren — `max-width: 720px`, scrollbar innerhalb des Modals.

### JavaScript-Logik

```javascript
// Info-Popups
document.querySelectorAll('.info-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const key = e.currentTarget.dataset.info;
    showInfoModal(key); // lädt Titel + Text aus einem Objekt
  });
});

// Report-Vorschau
document.getElementById('preview-report').addEventListener('click', () => {
  document.getElementById('preview-modal').hidden = false;
});

// ESC-Taste und Klick außerhalb schließt Modals
```

**Wichtig:** Alle Texte in JS-Objekte, nicht ins DOM hart reingeschrieben, damit sie leicht wartbar sind.

---

## Task 3 · Leistungen-Kachel „Sicherheits-Updates & Handlungsbedarf"

**Warum:** Proaktive Watchdog-Positionierung. Du willst rüberbringen: „Ich beobachte regelmäßig den Markt und informiere meine Kunden, bevor es brennt." Differenzierung zu allen reinen Break-Fix-Anbietern.

**Wohin:** Als **neue 9. Kachel** in der bestehenden `#leistungen`-Section. Das Grid muss ggf. von `repeat(4, 1fr)` auf `repeat(3, 1fr)` umgestellt werden, damit 9 Kacheln sauber umbrechen (3×3 statt 4+4+1).

**Icon:** Lucide `alert-triangle`, Farbe **Warning `#cc8800`** (gelb, nicht rot — beruhigend, nicht alarmierend). Bewusster Bruch mit dem Primary-Blau der anderen Kacheln, um Aufmerksamkeit zu erzeugen.

**Text (ready to copy):**

> **Sicherheits-Updates & Handlungsbedarf**
>
> Ich beobachte regelmäßig den Markt und werde proaktiv informiert, wenn End-of-Life-Themen, Sicherheitslücken oder BSI-Warnungen relevant werden — bei Software, Hardware oder ganzen Produktlinien. Sobald etwas für dich wichtig ist, meldest du dich nicht bei mir. Ich melde mich bei dir.
>
> Du kannst dich zurücklehnen. Ich halte dir den Rücken frei.

**Darunter als kleine Bullet-Liste:**
- Windows 10 / 11 Migration
- Router- und Firewall-Checks (FritzBox, TP-Link, UniFi)
- BSI-Warnungen im Blick
- Software mit auslaufendem Support

---

## Task 4 · Leistungen-Kachel „Firewall, VPN & Netzwerkschutz"

**Warum:** Firewall betrifft jeden — auch Einzelunternehmer. Eine FritzBox ist **keine Firewall**, sie schützt nur rudimentär. Das ist vielen nicht bewusst. Wir bauen darum eine **eigene Kachel** mit **konkreten Zahlen** zur Bedrohungslage — dezent, nicht panisch.

**Wohin:** Als weitere **neue Kachel** in `#leistungen` (damit sind es dann 10 — Grid dann 3×4 oder 5×2 je nach Screen).
Alternative: Wenn das Grid zu voll wird, kann der Backup-Gedanke aus Task 5 mit dieser Kachel verschmolzen werden.

**Icon:** Lucide `shield` oder `shield-alert`, Primary Blau `#0c4da2`.

**Text (ready to copy):**

> **Firewall, VPN & Netzwerkschutz**
>
> Eine FritzBox ist kein Schutz. Sie ist ein Router mit Grundabsicherung — mehr nicht. Im Internet laufen jeden Tag automatisierte Scans, die jede öffentliche IP-Adresse im Minutentakt abklopfen. Für dich unsichtbar, aber ständig aktiv.
>
> Ich baue dir ein richtiges Netzwerk auf Basis von UniFi: echte Firewall, Gäste-WLAN getrennt vom internen Netz, VPN für mobiles Arbeiten (WireGuard), klar definierte Zonen (VLAN). Die Hardware kostet nicht mehr als eine neue FritzBox — aber du bekommst mehr Sicherheit, mehr Stabilität und ein WLAN, das einfach funktioniert.

**Kleine Stichpunkte:**
- UniFi Dream Router / Gateway
- Gäste-WLAN mit Captive Portal
- WireGuard-VPN für mobiles Arbeiten
- VLAN-Trennung (Büro / Gast / Kameras / IoT)
- Zentrale Übersicht, klar dokumentiert

**WICHTIG zum Zahlen-Einsatz:**

Sei vorsichtig mit exakten Zahlen zu Cyber-Angriffen — BSI-Zahlen ändern sich und jede Behauptung ohne Quelle wirkt unseriös. Ich schlage vor, **keine konkrete Zahl** in die Kachel zu schreiben, sondern stattdessen in einem Info-Badge darunter:

> **Info-Box (BG `#e8f0fb`, Border-Left 4px `#26bdef`):**
> „Laut aktuellem BSI-Lagebericht finden täglich Millionen automatisierter Angriffsversuche auf Netzwerke im deutschsprachigen Raum statt — überwiegend vollautomatisch. Eine richtig konfigurierte Firewall filtert davon den Großteil weg, bevor dein Rechner sie überhaupt bemerkt."

Dann eine externe Quelle als kleiner Link: „→ BSI Lagebericht zur IT-Sicherheit". Wenn wir Zahlen nennen, dann verlinken wir auf die Quelle — das ist professionell.

---

## Task 5 · „Aus der Praxis"-Story-Block

**Warum:** Echte Geschichten wirken stärker als abstrakte Warnungen. Andreas hatte heute (2026-04-10) einen Kundenanruf: Rechner startet nicht mehr, keine Datensicherung, Festplatte fest verbaut, dringender Termin, Panik. Solche Geschichten gehören auf die Website — aber als **Lehrbeispiel**, nicht als Angstmache.

**Wohin:** Neuer kleiner Block **innerhalb der Leistungen-Section**, direkt unterhalb der Kachel „IT-Sicherheit & Backup" (oder als Info-Card dazwischen). Alternativ: als neues Element zwischen `#leistungen` und `#schulung`.

**Layout:** Querformat, 2-spaltig:
- Links: Icon `alert-octagon` in **Danger `#c0392b`** oder ein dezenter Illustrationsplatzhalter
- Rechts: Headline + Story-Text + CTA

**Text (ready to copy, anonymisiert):**

> **Aus der Praxis: „Ich muss heute noch fertig werden!"**
>
> Ein Kunde ruft an: Sein Rechner startet plötzlich nicht mehr. Er arbeitet für seine eigenen Kunden und muss heute noch ein wichtiges Projekt abgeben. Keine Datensicherung. Festplatte fest verbaut. Nicht austauschbar.
>
> Wir haben es an dem Tag gelöst — mit viel Aufwand und ohne Garantie, dass es klappt. Solche Situationen wünscht sich niemand. Und sie sind auch komplett vermeidbar.
>
> **Die Regel ist einfach:** Wenn dein Rechner heute kaputtgeht, musst du morgen weiterarbeiten können. Dafür braucht es keine teure Lösung — aber eine, die funktioniert, automatisch läuft und regelmäßig getestet wird.
>
> [Button: „Lass uns drüber reden" → scrollt zu `#schnellcheck`]

**Wichtig:** Die Story darf nicht wie ein Verkaufsmonolog klingen. Sie darf eine echte, nachvollziehbare Alltagssituation beschreiben — und dann elegant zum Schnellcheck überleiten.

---

## Task 6 · Neue Section „Projekte & Beratung"

**Warum:** Positionierung über den täglichen Betrieb hinaus. Kunden mit größeren Vorhaben (Migration, Umzug, Aufbau) müssen sehen, dass du das auch kannst. **Neu und wichtig:** Andreas wurde mehrfach gefragt, Angebote anderer IT-Dienstleister, Systemhäuser oder Elektriker zu prüfen und zu plausibilisieren. Das ist ein eigenes, wertvolles Angebot — die **Zweitmeinung**.

**Wohin:** Neue Section `#projekte` zwischen `#leistungen` und `#schulung`.

**Visueller Unterschied zur Leistungen-Section:** Etwas dunklerer Hintergrund `#f4f7fc`, damit der Besucher merkt: „Das ist was anderes — das ist der nächste Schritt."

### Struktur

```
<section id="projekte" class="projekte-section">
  <div class="container">
    <h2>Wenn's größer wird: Projekte & Beratung</h2>
    <p class="section-sub">
      Nicht jede IT-Frage ist ein Notfall. Manchmal ist sie ein Projekt.
      Dann plane ich mit dir — und setze es auch um.
    </p>

    <div class="projekt-grid">
      <!-- Card 1: Bestandsaufnahme & Risikoanalyse -->
      <!-- Card 2: Migrationen -->
      <!-- Card 3: Netzwerk-Neuaufbau -->
      <!-- Card 4: Zweitmeinung zu fremden Angeboten -->
      <!-- Card 5: IT-Dokumentation für den Notfall -->
    </div>

    <p class="projekte-cta">
      Interesse? Fang am besten mit dem
      <a href="#schnellcheck">kostenlosen IT-Schnellcheck</a> an.
    </p>
  </div>
</section>
```

### Die 5 Cards

**Card 1 · Bestandsaufnahme & Risikoanalyse**
Icon: `clipboard-list`
> Was hast du, was fehlt, was brennt? Ich mach eine strukturierte Aufnahme deiner IT — Hardware, Software, Verträge, Passwörter, Risiken. Du bekommst einen Gesamtüberblick, an dem du Entscheidungen festmachen kannst.

**Card 2 · Migrationen**
Icon: `arrow-right-left`
> Windows 10 → 11, alter Server → Cloud, neues M365 einführen, Mail-Umzug zu einem anderen Provider. Ich plane die Schritte, setze sie um und behalte den Zeitplan im Blick. Kein Stress mit Ausfällen.

**Card 3 · Netzwerk-Neuaufbau**
Icon: `network`
> UniFi, VLAN, VPN, Gäste-WLAN. Sauber aufgebaut, sauber dokumentiert. Auch für verteilte Standorte (Filiale, Home-Office, Baustelle).

**Card 4 · Zweitmeinung zu fremden Angeboten** ⭐ NEU
Icon: `file-search`
> Du hast ein Angebot von einem Systemhaus, einem Elektriker oder einem anderen IT-Dienstleister bekommen und bist dir nicht sicher, ob es passt? Schick es mir vertrauensvoll oder ruf mich an. Ich bewerte es fachlich, erkläre, was sinnvoll ist und was nicht — und mache dir bei Bedarf ein eigenes Gegenangebot. In der Regel bin ich günstiger. Und du weißt hinterher, worauf du dich einlässt.
>
> **[Button: „Angebot prüfen lassen" → mailto oder Kontaktformular mit Betreff „Zweitmeinung"]**

**Card 5 · IT-Dokumentation für den Notfall**
Icon: `file-text`
> Passwörter, Lizenzen, Verträge, Netzplan, Kontakte — an einem Ort, verschlüsselt, versioniert. Damit deine Vertretung weiß, wo sie im Ernstfall anfangen muss. Und damit du dich nicht selbst im Notfall durch dein eigenes System graben musst.

### Card-Styling

- Jede Card: Lucide-Icon (40×40px, Primary Blau `#0c4da2`), H3-Titel, Teaser-Absatz
- „Beispiel"-Box mit BG `#e8f0fb`, Border-Left 4px `#26bdef`, optional bei Card 1 und 4
- Grid: Mobile 1 Spalte, Tablet 2 Spalten, Desktop ab 1024px 3 Spalten, bei 5 Cards bleibt die letzte ggf. in der 2. Reihe alleine — das ist OK, wirkt sogar wie ein gewollter Akzent.

---

## Task 7 · FAQ-Erweiterung: Zweitmeinung

**Warum:** Die Zweitmeinung ist ein so konkretes, greifbares Thema, dass es **auch im FAQ** auftauchen sollte. Viele Besucher überfliegen die Section-Überschriften und schauen dann direkt ins FAQ, wenn sie konkrete Fragen haben.

**Wohin:** Neue Frage in der bestehenden `#faq`-Section einfügen — ideal als eine der **ersten 3 Fragen** (Sichtbarkeit).

**Frage + Antwort (ready to copy):**

> **Ich habe ein Angebot von einem anderen IT-Dienstleister bekommen. Kannst du das für mich prüfen?**
>
> Klar — das mache ich öfter. Schick mir das Angebot einfach per Mail oder ruf mich an. Ich schau mir an, was dort angeboten wird, ob die Positionen sinnvoll sind, ob die Preise marktüblich sind, und ob etwas fehlt oder überflüssig ist. Du bekommst eine unabhängige Einschätzung — und wenn du möchtest, mache ich dir ein eigenes Angebot. In der Regel bin ich deutlich günstiger und transparenter. Am Ende entscheidest du. Und wenn das andere Angebot das bessere ist, sage ich dir das auch.

---

## Task 8 · Managed-Service-Positionierung verbessern

**Warum:** Das Thema „Rund-um-Betreuung" ist aktuell nur in der Pricing-Tabelle sichtbar — versteckt. Es ist aber der **Kern des Recurring-Revenue-Modells**. Muss auf der Ebene der Leistungen sichtbar werden, mit einem klaren Nutzen-Versprechen: **„Du musst nicht mehr dran denken."**

### 8a · Leistungen-Kachel „Rund-um-Betreuung"

Neue Kachel (die 11.) in `#leistungen`, oder alternativ die bestehende Kachel „IT-Sicherheit & Backup" erweitern und umbenennen zu **„Rund-um-Betreuung (Managed Service)"**.

Empfehlung: **Neue Kachel**, damit die bestehende „IT-Sicherheit & Backup" weiterhin einzeln buchbar bleibt für Kunden, die keinen Service-Vertrag wollen.

**Icon:** `shield-check` oder `monitor-check`, Primary Blau `#0c4da2`.

**Text:**

> **Rund-um-Betreuung (Managed Service)**
>
> Updates, Patches, Monitoring, Backup-Kontrolle, Virenschutz, Microsoft 365 — alles läuft automatisch im Hintergrund. Du merkst nur, dass nichts kaputtgeht. Ab einem festen monatlichen Betrag, kein Ticket-System, direkt bei mir.
>
> → [Preise ansehen](#pricing)

### 8b · Pricing-Tabelle: Technische Begriffe entschärfen

In der Vergleichstabelle in `#pricing` die technischen Begriffe für normale Menschen übersetzen:

| Alt | Neu |
|---|---|
| Patchmanagement | Automatische Updates (Windows, Office, Browser) |
| RMM / Remote Monitoring | Fernüberwachung — ich sehe Probleme, bevor du sie merkst |
| Monitoring | 24/7 Betriebsüberwachung |
| ESET Endpoint | Professioneller Virenschutz (ESET) |
| M365 Backup | Microsoft-365-Daten-Sicherung |

**Wichtig:** Die technischen Begriffe dürfen in Klammern bleiben für die, die sie kennen — z.B. „Automatische Updates *(Patchmanagement)*".

---

## Anhang A · Responsive Verhalten

Alle neuen Elemente müssen auf **Mobile (≤ 768px)**, **Tablet (≤ 1024px)** und **Desktop** sauber funktionieren:

- Modals: Vollbild auf Mobile, zentriert mit `max-width: 720px` auf Desktop
- Schnellcheck-Card: Padding 24px auf Mobile, 48px auf Desktop
- Projekt-Grid: 1 Spalte → 2 Spalten → 3 Spalten
- Leistungen-Grid: Check, dass 9–11 Kacheln auf allen Breakpoints sauber aussehen
- Info-Popups: Touch-freundliche Hit-Area (min. 44×44px)

## Anhang B · Accessibility

- Alle Buttons haben `aria-label`
- Modals haben `role="dialog"`, `aria-modal="true"`, Focus-Trap
- ESC schließt Modals
- Fokus-Outline bleibt sichtbar (nicht `outline: none` ohne Ersatz)
- Farb-Kontraste mindestens AA-konform (WCAG 2.1)

## Anhang C · Commit-Strategie

Empfohlene Reihenfolge und Commits:

```bash
git checkout -b feature/release-1

# Commit 1: Preise global
git add -A && git commit -m "fix: Stundensatz global auf 110 € korrigiert"

# Commit 2: Schnellcheck inkl. Modals
git commit -m "feat: IT-Schnellcheck-Section mit Report-Vorschau-Modal"

# Commit 3: Neue Leistungen-Kacheln
git commit -m "feat: Kacheln Sicherheit/Handlungsbedarf und Firewall/VPN"

# Commit 4: Praxis-Story
git commit -m "feat: Aus-der-Praxis-Story-Block zum Thema Backup"

# Commit 5: Projekte-Section inkl. Zweitmeinung
git commit -m "feat: Neue Section Projekte & Beratung"

# Commit 6: FAQ-Erweiterung
git commit -m "feat: FAQ um Zweitmeinungs-Frage erweitert"

# Commit 7: Managed Service
git commit -m "feat: Rund-um-Betreuung als Kachel + Pricing-Tabelle verbessert"
```

## Anhang D · Was du NICHT tun sollst

- **Keinen** Hero-Slider anfassen (macht Andreas selbst)
- **Keine** neuen Farben einführen — alles nach CI 2026.01
- **Keine** bestehenden Texte ändern, die nicht explizit im Auftrag stehen
- **Keinen** neuen JavaScript-Library einbinden ohne Rückfrage (Lucide Icons sind bereits da)
- **Keine** externen Links ohne `rel="noopener"` bei `target="_blank"`
- **Keine** Bilder hochladen — wir arbeiten nur mit Icons, bis Andreas eigene Fotos liefert

---

## Rückmeldung an Andreas nach jedem Task

Nach jedem Commit kurze Zusammenfassung:
- Was wurde geändert (1-2 Sätze)
- Welche Dateien betroffen
- Gab es überraschende Anpassungen?
- Gibt's offene Fragen für den nächsten Task?

---

**Viel Erfolg. Wenn was unklar ist: frag Andreas direkt. Kein Trial-and-Error.**

*© 2026 Grundke IT-Service · CI 2026.01*
