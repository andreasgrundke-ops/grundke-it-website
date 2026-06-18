# Offene Punkte – SEO/GEO-Optimierung grundke-it.de

**Stand:** 2026-06-18 · **Letzter Commit:** `dc4eb51` (gepusht/deployed auf `main`)

Dieses Dokument hält fest, was in der GEO/E-E-A-T/Recht-Runde umgesetzt wurde und
welche Punkte noch offen sind. Ziel der Runde: beim nächsten Sichtbarkeits-Scan in
**allen** Kategorien (SEO, GEO/KI-Suche, DSGVO, Barrierefreiheit) „sehr gut" (≥ 90).

---

## ✅ Erledigt (Commit `dc4eb51`, deployed)

- **E-E-A-T:** WebPage-Schema (`author` → Person `#andreas`, `datePublished`/`dateModified`),
  sichtbare Autor-Box + „Zuletzt aktualisiert" auf allen 11 Landingpages + index.
- **Impressumspflicht-Fix:** Legal-Footer-Nav (Impressum/Datenschutz/AGB/Barrierefreiheit)
  auf allen Seiten – Impressum jetzt von **22/22** Seiten erreichbar (war 3).
- **Neue Seite** `/barrierefreiheit/` (freiwillige BFSG-Erklärung, WCAG 2.1 AA, Selbstbewertung).
- **FAQ + FAQPage-Schema:** `/schulung/` (8 Fragen), `/kontakt/` (5 Fragen) – sichtbarer Text
  deckungsgleich mit dem Schema. index-FAQ-Schema an sichtbaren Text angeglichen + Grammatikfix.
- **robots.txt** `Claude-User` ergänzt · **llms.txt** Stand + alle Landingpages · **sitemap.xml** regeneriert (16 URLs).
- **Verifiziert:** 57/57 JSON-LD valide; jede FAQ-Aussage sichtbar auf der Seite; alle 4 Legal-Links
  auf jeder Seite + Ziele existieren; genau 1 Person-Volldefinition; jede indexierte Seite genau 1 H1.

---

## 🔜 A) Sofort: Re-Scan (Beweis der Wirkung)

- Nach CDN-Cache (~10 Min nach Deploy) grundke-it.de **neu scannen** – eigener Scanner **und**
  geo-tool.com zum Vergleich.
- **Vorher/Nachher** gegenüberstellen (GEO-Ausgangswert war **54**); prüfen, ob noch Onpage-Lücken offen sind.

## 📌 B) Off-Page (nicht im Code lösbar – größter externer Hebel, ~91 % der KI-Antworten zitieren Drittseiten)

1. **Google Business Profil** vollständig pflegen; NAP exakt „Andreas Grundke IT-Service",
   Beethovenring 16, 85630 Grasbrunn, +49 178 258 44 38; Kategorien, Zeiten, Leistungen, Fotos, Beiträge.
2. **NAP-Konsistenz** byte-genau in allen Verzeichnissen (11880, Das Örtliche, Gelbe Seiten, Cylex, Yelp).
3. **LinkedIn-Unternehmensseite** anlegen (bisher nur Personenprofil) und als zweites `sameAs` ins Schema.
4. **Bewertungen**: Google (läuft, 5,0) + **ProvenExpert**-Profil aufbauen.
5. **Search Console**: neue Sitemap einreichen, `/barrierefreiheit/` + Landingpages zur Indexierung;
   **Bing Webmaster Tools** ebenso (Copilot/ChatGPT nutzen Bing-Index).
6. **Rich Results Test** je Seitentyp (LocalBusiness/FAQ/WebPage) einmal live prüfen.
7. Lokale/branchenbezogene Erwähnungen (HWK, lokale Netzwerke, Sponsoring) als zitierfähige Drittquellen.

## 🛠️ C) Optionale Onpage-Follow-ups (niedrige Priorität)

- `/tree/` hat **keine H1** (QR-vCard, `Disallow: /tree/`, vom Scan ausgeschlossen) – bewusst nicht angefasst.
- **Phase-2-Ortsseiten** (Eintrag in `PLACES` in `tools/build_landingpages.py`, dann Generator laufen lassen):
  Ottobrunn, Neubiberg, Kirchheim/Heimstetten, Aschheim/Feldkirchen (gesamt ≤ ~10 Ortsseiten – sonst Kannibalisierung).
- Optional: Branchenseiten (Handwerk/Gastro/Praxis) – stark für GEO/KI-Zitate.

---

## ℹ️ Hinweise

- **Single Source of Truth** für die 11 Landingpages + `sitemap.xml`: `tools/build_landingpages.py`.
  Änderungen dort vornehmen, dann `python tools/build_landingpages.py` ausführen – **nicht** die
  generierten `index.html` direkt editieren.
- **Deploy:** statisches HTML, GitHub Pages, Auto-Deploy bei `git push` auf `main`; Live-Verifikation
  erst nach Build + CDN-Cache (~10 Min).

---

CI 2026.01 · Grundke IT-Service · www.grundke-it.de
