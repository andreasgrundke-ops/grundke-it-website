# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Inhaberinnen, Inhaber und Büroleitungen kleiner Betriebe mit 5 bis 50 Arbeitsplätzen im Münchner
Osten: Handwerk, Praxen, Kanzleien, Gastronomie, Hotels, Büros. Nur Geschäftskunden (Unternehmen,
Selbstständige, Freiberufler).

Typische Lage beim Besuch: Etwas funktioniert gerade nicht (Drucker, Internet, Outlook, gesperrtes
Konto, Server), der bisherige IT-Dienstleister ist nicht erreichbar, oder der Kollege, der die IT
nebenbei gemacht hat, fällt weg. Oft am Handy, oft außerhalb üblicher Bürozeiten. Der Job: schnell
einen verlässlichen Menschen finden und sicher sein, dass es ein echter, lokaler Ansprechpartner ist.

## Product Purpose

Website von Grundke IT-Service (Einzelunternehmen von Andreas Grundke, Grasbrunn). Sie soll passende
Betriebe zum Anruf oder zur WhatsApp-Nachricht bringen und daraus Vertragskunden mit planbarer
Monatspauschale machen. Zweite Säule seit 08/2026: KI-Anwendungen im Betrieb. Dazu
IT-Sicherheitsschulungen. Erfolg heißt: Kontaktaufnahmen von Betrieben aus der Zielgruppe und
wachsende wiederkehrende Umsätze.

## Positioning

Ein Mensch statt Ticketsystem. Andreas ist der erste Ansprechpartner für jedes technische Problem im
Betrieb und entscheidet selbst, ob zusätzlich ein Fachtechniker aus einem anderen Gewerk gebraucht
wird. Keine klassischen Öffnungszeiten, ein einheitlicher Stundensatz, Beratung, Betrieb und
Automatisierung aus einer Hand. Vor Ort im Münchner Osten (Radius 25 km), remote bundesweit.

## Operating Context

- Kontaktwege: Telefon 0178 258 44 38, WhatsApp, E-Mail info@grundke-it.de, Kontaktseite `/kontakt/`
  (QR-Code auf Visitenkarten und Website führt dorthin).
- Fernwartung per Download (`/fernwartung/`), kostenloser IT-Schnellcheck mit schriftlichem Bericht.
- Google-Unternehmensprofil mit Bewertungen, ProvenExpert-Profil.

## Capabilities and Constraints

- Ohne Vertrag 110 € netto pro Stunde im 15-Minuten-Takt. Betreuungspakete ab 149 € netto im Monat
  („planbare Monatspauschale", nicht „Festpreis"). Anfahrt bis 5 km inklusive. IT-Assessment in
  jedem Paket, Monatsreport nur im Premium-Paket.
- **Keine garantierten Reaktionszeiten oder Erreichbarkeiten.** Vertragskunden werden bevorzugt
  behandelt. Texte dürfen keine Garantie versprechen.
- KI-Themen: „KI datenschutzgerecht einsetzen", nie „rechtssicher" (keine Rechtsberatung).
- Technik: statisches HTML, Vanilla CSS und JS, kein Framework, GitHub Pages. Orts-, Leistungs- und
  KI-Seiten sowie Navigation und Footer erzeugt `tools/build_landingpages.py`. Bei jedem Release
  `CACHE_NAME` und `RUNTIME_CACHE` in `sw.js` erhöhen. Das Repo ist öffentlich.

## Brand Commitments

- Name „Grundke IT-Service" (offiziell „Andreas Grundke IT-Service"). Du-Form, direkt,
  umgangssprachlich, erste Person. Bestätigte Leitzeile: „Dein ITler geht nicht ran? Ich schon."
- CI 2026.01: Blau `#0c4da2`, Cyan `#26bdef`; Visitenkarten-Blau `#0000FE` für Haupt-Buttons mit
  weißer Schrift; WhatsApp-Grün für WhatsApp. Logo unter `assets/img/logo-grundke-it*`.
  Fußzeile „CI 2026.01 · Grundke IT-Service · www.grundke-it.de".
- Keine Stockfotos von Menschen, die man für Andreas halten könnte. Figuren und Illustrationen
  werden selbst gezeichnet.

## Evidence on Hand

- Sechs Kundenstimmen, fünf davon bei Google (Bewertung 5,0), eine direkt übermittelt. Immer
  wortgetreu zitieren, Quelle nur als „Google-Bewertung" labeln, wenn sie dort steht.
- Über 20 Jahre IT-Erfahrung, Fachinformatiker für Systemintegration.
- **Fehlt:** ein echtes Foto von Andreas (Shooting geplant), Fallstudien mit Zahlen. Nichts davon
  erfinden; Beispielabläufe als Beispiel kennzeichnen.

## Product Principles

1. Name und Gesicht statt Anonymität: Der Besucher soll wissen, mit wem er es zu tun hat.
2. Zeigen, was der Kunde bekommt, nicht wie IT aussieht.
3. Nur versprechen, was immer hält.
4. Kontakt mit einem Klick, am Handy im Daumenbereich.
5. Schlank und schnell: nichts, was die Seite langsamer macht, ohne dass es dem Besucher nützt.

## Accessibility & Inclusion

WCAG 2.1 AA als Ziel. Bewegung respektiert `prefers-reduced-motion`; alles, was länger als fünf
Sekunden von selbst läuft, lässt sich anhalten (WCAG 2.2.2). Bekannte Einschränkung laut
Barrierefreiheitserklärung: Grau-Kontraste.
