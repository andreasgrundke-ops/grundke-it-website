#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_landingpages.py
Version : 2.6
Autor   : Andreas Grundke IT-Service (Grundke IT-Service)
Datum   : 2026-10-10
Zweck   : Generiert aus einem gemeinsamen Template + Datenlisten die Orts- und
          Leistungs-Landingpages fuer grundke-it.de (statisches HTML, GitHub Pages)
          und aktualisiert die sitemap.xml.

Ablauf:
  1. Gemeinsame Bausteine (Head, Nav, Footer mit interner Verlinkung, Sticky-Bar,
     Style) als Konstanten/Funktionen.
  2. Datenlisten PLACES (Orte) und SERVICES (Leistungen).
  3. Pro Eintrag wird <slug>/index.html erzeugt (CI 2026.01, Schema.org JSON-LD
     via json.dumps -> garantiert valides JSON).
  4. sitemap.xml wird komplett neu geschrieben (statische Seiten + alle Landingpages).

  5. Der gemeinsame Seitenkopf (nav_html) wird auch in die Startseite und die
     handgebauten Seiten (HAND_PAGES) geschrieben -> ein Menue fuer die ganze Site.
  6. sync_home() schreibt in die Startseite: Kundenstimmen (REVIEWS) samt review[] im
     Schema, FAQ (HOME_FAQS) samt FAQPage-Schema, WhatsApp-Links (data-wa), Preise
     (data-price), Bewertungszahl der Belegzeile (data-proof) und das Seitendatum.

Aufruf: python tools/build_landingpages.py

Aenderungen:
  2026-09-23  Einheitliche Navigation und Fusszeile fuer alle Seiten (nav_html,
              footer_html, sync_shared), Buttons .btn-p/.btn-g, FAQ als Akkordeon,
              Einstieg (hero) fuer den KI-Hub,
              aktiver Menuepunkt per aria-current, sichtbare Brotkrumen,
              KI-Unterseiten im Schema unter dem Hub, Pfeil-Glyphe repariert.
  2026-10-07  Neue Seiten (Software nach Mass, Websites, IT-Betreuer wechseln, Lizenzen,
              E-Rechnung, Digitalbonus, Ratgeber mit Unterseiten), Menue und Fuss mit
              Bereichen, Preis-Schalter SHOW_FROM_PRICES/PRICES, Offer-Schema mit Mindestpreis,
              Service.provider als @id-Verweis, Tabellen am Handy gestapelt, Hero-H1 mit
              Leerzeichen vor der Akzentzeile, Zeitzusagen aus Orts- und Notdienstseiten entfernt.
  2026-10-10  Website-Umbau Release A (Expand): ASSET_VER/asset() fuer style.css und main.js
              aller Seiten (auch Startseite und Handseiten ueber sync_shared), ICON_SPRITE vor
              dem Kopf, REVIEW_COUNT_GOOGLE, Fuss mit aufklappbaren Spalten (<details>) und
              fester Rechtszeile, Fliesstext .lp-content p auf 16 px, Autor-Link unterstrichen.
  2026-10-10  Release A Startseite: REVIEWS und HOME_FAQS als einzige Quelle, sync_home(),
              WhatsApp mit vorbefuelltem Satz je Einstieg (WA, WA_TEXT; auch Kontaktleiste
              und Fuss), Software-Betrieb ab 80 € (vorher 79 €), HOME_DATE fuer die Startseite.
  2026-10-10  Release B, Task 5: Generator-Huelle render_shell (section, page_head, mini_chat,
              voices_html, prices_html, closing) fuer managed-it-service, it-betreuer-wechseln und
              it-notdienst (Schalter SHELL_SLUGS), K4/Antwortsatz/Chat/Stimmen aus dem Textblatt,
              schlankes STYLE fuer diese Seiten, STYLE_LEGACY fuer die uebrigen bis Task 7.
  2026-10-10  Release B, Task 6: Ortsseiten (render_place ueber render_shell, PLACE_DATE) und
              Microsoft 365, IT-Sicherheit, Netzwerk (Stimme aus REVIEWS statt lp-voice/VOICE_STYLE),
              Lizenzen, E-Rechnung, Digitalbonus in der Huelle; K4/Antwortsatz/Stimmen aus dem
              Textblatt, freigegebene Ersatzsaetze (Frage 5). Huelle: Kopf ohne Chat zweispaltig,
              FAQ und einzelne Stimme mit seitlicher Ueberschrift, tail_blocks, voices_h2,
              <!--split--> in extra, Vertrauenstext neben dem Einstieg; ico-network, ico-wifi.
  2026-10-10  Release B, Task 7: KI-Hub, KI-Seiten, Software, Websites und Ratgeber in der Huelle, damit alle
              Generator-Seiten. K4/Antwortsatz aus dem Textblatt, Hubs mit Wegen (nav.lp-paths) rechts im Kopf,
              Ratgeber ohne K4 und nur mit Anruf-Knopf, Ratgeber-Artikel in einer Lesespalte, <!--more--> fuer
              zugeklappte Teile (content_blocks, more_html). KI_STYLE/NEW_STYLE nach style.css; STYLE_LEGACY,
              SHELL_SLUGS, author_box, cards_html, die alte Huelle in render_service und RATGEBER_CTA entfernt.
              Asset-Version 2026.10.c.
              Fix-Runde 1: Abbruch beim Bauen bei falschen Marken (check_markers, Reste nach dem Ersetzen) und
              bei Feldern, die ein Ratgeber-Artikel nicht darstellen kann (check_ratgeber, RATGEBER_KEYS);
              <!--more:Beschriftung-->, intro_h2 fuer den Einstieg ohne Karten, kind "ratgeber-hub" statt "hub".
  2026-10-10  Release C1, Task 8: /schulung/ aus dem Generator (SERVICES-Eintrag statt Handseite; HAND_PAGES und
              STATIC_URLS ohne schulung, Fusslink ueber group_of). Neue Felder: h1_em (Wort der H1 als <em>), name
              (Name ohne Tags fuer Schema und og), meta_extra (eigene og/twitter-Werte, twitter:image:alt), intro
              optional; Preiskarte mit Zusatzfeld (zweite Preiszeile, Leistungen, Abzeichen, Knopf).
  2026-10-10  Release C1, Task 9: sync_shared setzt den Abschluss K5 auch auf die Handseiten (HAND_CLOSING, CLOSING_RE:
              vorhandenen <section class="cta-sec"> ersetzen, sonst vor </main> einfuegen; Startseite und empfehlungen
              ausgenommen) und den Font-Preload aus head() in deren Kopf (preload_fonts, idempotent). closing() mit
              Autorzeile ohne Datum (mod_disp None) und Knoepfen auch am Handy, wenn die Seite keine Kontaktleiste hat.
              Asset-Version 2026.10.d (Release C1).
              Fix-Runde 1: KONTAKT_DATE/KONTAKT_DATE_DISP (Abschluss-Datum und Sitemap aus einer Quelle), Preload-Pruefung
              je Schrift (nur fehlende einfuegen), Mobilmenue „Fernwartung starten“ mit Sprite-Symbol und Klasse .m-fw
              statt Blitz-Zeichen und Inline-Style.
"""

import os
import json
import re
import html as htmllib
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://grundke-it.de"
PHONE = "+491782584438"
PHONE_DISP = "0178 258 44 38"
TODAY = "2026-10-07"          # dateModified (Stand der letzten Aktualisierung)
TODAY_DISP = "7. Oktober 2026"  # sichtbares Datum fuer Leser (E-E-A-T-Freshness-Signal)
PUB_DATE = "2026-06-15"       # datePublished (Ersterstellung der Landingpages)
PERSON_ID = DOMAIN + "/#andreas"          # @id der Person Andreas Grundke (Startseite)
BUSINESS_ID = DOMAIN + "/#localbusiness"  # @id des Unternehmens (Startseite)
WEBSITE_ID = DOMAIN + "/#website"         # @id der Website (Startseite)
# Der KI-Bereich ist juenger als die uebrigen Landingpages und fuehrt deshalb eigene
# Datumsangaben. So bleibt dateModified der Orts-/Leistungsseiten ehrlich (kein
# kuenstliches Hochsetzen der Freshness-Signale nur wegen eines neuen Footer-Links).
KI_DATE = "2026-09-23"          # dateModified der KI-Seiten
KI_DATE_DISP = "23. September 2026"
KI_PUB_DATE = "2026-08-22"      # datePublished der KI-Seiten
# Seiten vom 07.10.2026 (Software, Websites, IT-Betreuer wechseln, E-Rechnung, Digitalbonus,
# Lizenzen, Ratgeber) und die dafuer inhaltlich erweiterten Seiten tragen dieses Datum.
NEW_DATE = "2026-10-07"
NEW_DATE_DISP = "7. Oktober 2026"

# Asset-Version (seit 10.10.2026): haengt als ?v= an style.css und main.js ALLER Seiten
# (generierte Seiten, Startseite und Handseiten ueber sync_shared) und steht gleichlautend
# als ASSET_VER im Pre-Cache von sw.js. Bei JEDEM Release erhoehen, zusammen mit
# CACHE_NAME/RUNTIME_CACHE in sw.js. Neue URLs laufen am alten Cache des Service Workers
# vorbei, ein wiederkehrender Besucher bekommt nie neues HTML mit altem CSS.
ASSET_VER = "2026.10.d"
# Bewertungen im Google-Unternehmensprofil (Stand 10.10.2026). Eine weitere Stimme kam
# direkt und zaehlt hier nicht mit. Einzige Quelle fuer die Zahl auf allen Seiten.
REVIEW_COUNT_GOOGLE = 5
# Startseite: Stand fuer WebPage.dateModified, Sitemap und 'Zuletzt aktualisiert' im Fuss
# (sync_home). Nur hochsetzen, wenn sich der Inhalt der Startseite wirklich aendert.
HOME_DATE = "2026-10-10"
HOME_DATE_DISP = "10.10.2026"
# Kontaktseite (Handseite): Stand fuer „Zuletzt aktualisiert“ im Abschluss (HAND_CLOSING) und lastmod der Sitemap
# (STATIC_URLS). Nur hochsetzen, wenn sich der Inhalt der Kontaktseite wirklich aendert.
KONTAKT_DATE = "2026-10-10"
KONTAKT_DATE_DISP = "10. Oktober 2026"

# WhatsApp mit vorbefuelltem Satz je Einstieg (Textblatt §4, seit 10.10.2026): Am Satz ist
# erkennbar, ueber welchen Knopf eine Anfrage kam, ohne Tracking-Skript. Auf der Startseite
# setzt sync_home() das href jedes <a data-wa="schluessel">; Kontaktleiste (STICKY) und Fuss
# nutzen WA() direkt. Neue Einstiege nur hier eintragen.
WA_NUMBER = "491782584438"
WA_TEXT = {
    "hero": "Hallo Andreas, ich komme über deine Startseite.",
    "schnellcheck": "Hallo Andreas, ich komme über den IT-Schnellcheck auf deiner Website.",
    "preise-starter": "Hallo Andreas, ich komme über deine Preise und interessiere mich für das Paket Starter.",
    "preise-business": "Hallo Andreas, ich komme über deine Preise und interessiere mich für das Paket Business.",
    "preise-premium": "Hallo Andreas, ich komme über deine Preise und interessiere mich für das Paket Premium.",
    "preise-adhoc": "Hallo Andreas, ich komme über deine Preise und brauche Hilfe ohne Vertrag.",
    "kontaktleiste": "Hallo Andreas, ich habe deine Nummer von deiner Website.",
    "faq": "Hallo Andreas, meine Frage war in deinen FAQ nicht dabei:",
    "abschluss": "Hallo Andreas, ich habe ein IT-Problem und komme über deine Website.",
    "fuss": "Hallo Andreas, ich komme über deine Website.",
}


def WA(text):
    """'Hallo Andreas, …' -> 'https://wa.me/491782584438?text=Hallo%20Andreas%2C%20…' (UTF-8, alles ausser
    Buchstaben, Ziffern und -._~ kodiert, wie die Tabelle im Textblatt)."""
    return "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(text, safe="")


def asset(path):
    """'css/style.css' -> '/assets/css/style.css?v=<ASSET_VER>' (absolut, auf jeder Seitentiefe gleich)."""
    return "/assets/" + path + "?v=" + ASSET_VER

# „ab"-Preise (netto) fuer Projekte auf den Seiten Software, Websites, E-Rechnung und KI.
# Auf False gesetzt verschwinden alle Projektpreise samt Offer-Schema und Preissaetzen in den
# FAQ; Stundensatz und Monatspakete bleiben. Alle Projektpreise der Seiten kommen aus PRICES.
SHOW_FROM_PRICES = True
PRICES = {
    "software_klein": 3000,         # kleine Anwendung, einmalig
    "software_pilot": 6000,         # Pilot mit Schnittstelle, einmalig
    "software_pilot_bis": 14000,    # obere Grenze, wie sie in der FAQ steht
    "software_betrieb": 80,         # Betrieb und Pflege je Monat, kleine Anwendung (bis 10.10.2026: 79)
    "software_pilot_betrieb": 150,  # Betrieb und Pflege je Monat, Pilot
    "ablauf_check": 690,            # Ablauf-Check vor Ort, bei Auftrag angerechnet
    "website_onepager": 800,        # eine Landingpage (Richtwert, Andreas 09.10.2026)
    "website_start": 1300,          # bis 5 Seiten
    "website_ausbau": 2000,         # bis 15 Seiten inkl. Umzug
    "website_betrieb": 40,          # laufender Betrieb je Monat, optional
    "ki_start": 1500,               # Paket KI-Start
    "erechnung": 1500,              # E-Rechnung Standardfall
    "erechnung_export": 4000,       # E-Rechnung mit eigenem Export
}


def eur_txt(n):
    """1500 -> '1.500 Euro' (fuer FAQ-Texte, die auch ins Schema gehen)."""
    return "{:,}".format(n).replace(",", ".") + " Euro"


def eur(n):
    """1500 -> '1.500 €' (deutsches Zahlenformat, geschuetztes Leerzeichen vor dem Euro)."""
    return "{:,}".format(n).replace(",", ".") + " €"

# --------------------------------------------------------------------------- #
#  Gemeinsame Bausteine                                                        #
# --------------------------------------------------------------------------- #

# Alle Generator-Seiten (Huelle render_shell, seit Task 7 ohne Ausnahme) tragen im eigenen <style> nur
# noch die Prosa-Regeln fuer den Fliesstext aus "intro" und "extra"; alle Bausteine (Kopf, Karten, Preise,
# Stimmen, FAQ, Abschluss, Kaesten aus dem KI-Bereich) kommen aus style.css (Spec AK1).
STYLE = """  <style>
    .lp-content > p, .lp-content > div { max-width:68ch; }
    .lp-content p { font-size:1.0667rem; color:var(--text2); line-height:1.75; margin:0 0 1rem; }
    .lp-content p:last-child { margin-bottom:0; }
    .lp-content strong { color:var(--text); }
    .lp-content p a, .lp-content li a { color:var(--cyan); }
    .lp-related { margin-top:2rem; }
  </style>"""

# --- Navigation: EINE Quelle fuer alle Seiten (seit 2026-09-23) ------------- #
# Vorher gab es vier Varianten (Startseite, Generator, handgebaute Unterseiten,
# Rechtsseiten) -- das Menue baute sich bei jedem Seitenwechsel um. Jetzt erzeugt
# nav_html() den kompletten <header> und sync_shared() schreibt ihn auch in die
# Startseite und die handgebauten Seiten (HAND_PAGES). Menue nur HIER aendern.
#
# (Label, Ziel auf Unterseiten, Ziel auf der Startseite, Bereichsschluessel)
# Auf der Startseite bleiben es reine #-Anker: Scroll-Spy und Lenis-Smooth-Scroll
# in main.js greifen nur auf href="#...".
# Seit 07.10.2026 folgt das Menue den vier Einstiegen der Startseite (IT, KI, Software,
# Websites). IT-Schnellcheck und Schulungen sind ueber Startseite, KI-Seiten und Fuss
# erreichbar; ein siebter Punkt liesse die Leiste zwischen 1024 und 1239 px umbrechen.
NAV_ITEMS = [
    ("IT-Service", "/#leistungen", "#leistungen", "it"),
    ("KI im Betrieb", "/ki-fuer-kmu/", "/ki-fuer-kmu/", "ki"),
    ("Software", "/software-nach-mass/", "/software-nach-mass/", "software"),
    ("Websites", "/websites-fuer-betriebe/", "/websites-fuer-betriebe/", "websites"),
    ("Preise", "/#preise", "#preise", "preise"),
]
NAV_KONTAKT = ("Kontakt", "/kontakt/", "kontakt")
# CID-Link statt Orts-URL: Die alte Adresse trug den frueheren Profilnamen
# „IT-Service - Andreas Grundke" im Pfad. Der CID-Link bleibt bei Namensaenderungen gueltig
# und ist derselbe wie hasMap/sameAs im Schema der Startseite.
MAPS_URL = "https://maps.google.com/?cid=1934827868521304193"
PHONE_SVG = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 '
             '19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.62 3.4 2 2 0 0 1 3.6 1.22h3a2 2 0 0 1 '
             '2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.8a16 16 0 0 0 6 6l.94-.94a2 2 0 0 1 2.11-.45 '
             '12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')

# Icon-Sprite fuer alle Seiten (seit 10.10.2026): die Symbole, die die gemeinsamen Bausteine
# brauchen (Belegzeile, Knoepfe, Sterne; ab ico-tools die Kacheln der Leistungszeilen in der
# Generator-Huelle). Pfade 1:1 aus dem Sprite der Startseite; ico-wifi (Task 6) aus derselben
# Lucide-Reihe wie ico-wifi-off der Startseite, die dort kein WLAN-Symbol ohne Strich hat.
# page() und sync_shared() setzen es direkt vor den <header>. Die Startseite bekommt es nicht:
# ihr eigenes Sprite enthaelt dieselben Symbole, ein zweites ergaebe doppelte IDs.
ICON_SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg" id="icon-sprite" style="display:none" aria-hidden="true">\n'
               '  <symbol id="ico-star" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></symbol>\n'
               '  <symbol id="ico-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.62 3.4 2 2 0 0 1 3.6 1.22h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.8a16 16 0 0 0 6 6l.94-.94a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></symbol>\n'
               '  <symbol id="ico-wa" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></symbol>\n'
               '  <symbol id="ico-mail" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></symbol>\n'
               '  <symbol id="ico-arrow-r" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></symbol>\n'
               '  <symbol id="ico-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></symbol>\n'
               '  <symbol id="ico-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></symbol>\n'
               '  <symbol id="ico-user-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m16 11 2 2 4-4"/></symbol>\n'
               '  <symbol id="ico-tools" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></symbol>\n'
               '  <symbol id="ico-cloud" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/></symbol>\n'
               '  <symbol id="ico-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></symbol>\n'
               '  <symbol id="ico-handshake" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/></symbol>\n'
               '  <symbol id="ico-monitor" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8m-4-4v4"/></symbol>\n'
               '  <symbol id="ico-server-crash" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M6 10H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2"/><path d="M6 14H4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-4a2 2 0 0 0-2-2h-2"/><path d="M6 6h.01"/><path d="M6 18h.01"/><path d="m13 6-4 6h6l-4 6"/></symbol>\n'
               '  <symbol id="ico-list" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/></symbol>\n'
               '  <symbol id="ico-key" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.3 9.3"/><path d="m18 5 3-3"/><path d="m15 8 3-3"/></symbol>\n'
               '  <symbol id="ico-file-text" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></symbol>\n'
               '  <symbol id="ico-search-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m8 11 2 2 4-4"/><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></symbol>\n'
               '  <symbol id="ico-network" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/></symbol>\n'
               '  <symbol id="ico-wifi" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h.01"/><path d="M2 8.82a15 15 0 0 1 20 0"/><path d="M5 12.859a10 10 0 0 1 14 0"/><path d="M8.5 16.429a5 5 0 0 1 7 0"/></symbol>\n'
               '</svg>')


def nav_html(current=None, home=False):
    """Kompletter Seitenkopf (Desktop-Leiste + Mobilmenue).
    current = (bereich, art): bereich aus NAV_ITEMS/NAV_KONTAKT, art "page" fuer die
    Bereichsseite selbst, "true" fuer Seiten darunter (aria-current)."""
    def cur(key):
        if current and current[0] == key:
            return ' aria-current="{}"'.format(current[1])
        return ""

    items = [(lbl, home_href if home else href, key) for lbl, href, home_href, key in NAV_ITEMS]
    # Fernwartung (Andreas 09.10.2026): direkter Menuepunkt statt Dropdown mit nur einem Eintrag
    fw_cur = cur("fernwartung")
    k_lbl, k_href, k_key = NAV_KONTAKT
    desk = "".join('\n      <li><a href="{h}"{c}>{l}</a></li>'.format(h=h, c=cur(k), l=l) for l, h, k in items)
    mob = "".join('\n  <a href="{h}"{c}>{l}</a>'.format(h=h, c=cur(k), l=l) for l, h, k in items)
    return """<header class="site-header">
<nav aria-label="Hauptnavigation">
  <div class="nav-inner inner">
    <a href="/" class="logo" title="Grundke IT-Service – München Ost"><picture><source srcset="/assets/img/logo-grundke-it-white-480.webp" type="image/webp"><img class="logo-img" src="/assets/img/logo-grundke-it-white-480.png" alt="Grundke IT-Service" width="180" height="60" /></picture></a>
    <a class="nav-loc" href="{maps}" target="_blank" rel="noopener" aria-label="Standort auf Google Maps anzeigen"><svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>München Ost</a>
    <ul class="nav-links">{desk}
      <li><a href="/fernwartung/"{fw_cur}>Fernwartung starten</a></li>
      <li><a href="{k_href}"{k_cur}>{k_lbl}</a></li>
      <li><a href="tel:+491782584438" class="nav-cta">{phone}<span>Jetzt anrufen</span></a></li>
    </ul>
    <button class="hamburger" id="ham" aria-label="Menü öffnen" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span><span></span></button>
  </div>
</nav>
<div class="mobile-menu" id="mobileMenu">{mob}
  <a href="{k_href}"{k_cur}>{k_lbl}</a>
  <a href="/fernwartung/"{fw_cur} class="m-fw"><svg width="18" height="18" aria-hidden="true"><use href="#ico-monitor"/></svg>Fernwartung starten</a>
  <a href="tel:+491782584438" class="m-cta">Jetzt anrufen · 0178 258 44 38</a>
</div>
</header>""".format(maps=MAPS_URL, desk=desk, mob=mob, phone=PHONE_SVG, fw_cur=fw_cur,
                     k_href=k_href, k_lbl=k_lbl, k_cur=cur(k_key))


SECTION_PAGES = {"ki-fuer-kmu": "ki", "software-nach-mass": "software",
                 "websites-fuer-betriebe": "websites"}
SECTION_CHILDREN = {"e-rechnung": "ki"}
# schulung (seit Task 8 Generator-Seite) markiert wie zuvor als Handseite keinen Menuepunkt
SECTION_NONE = ("digitalbonus-bayern", "ratgeber", "schulung")


def section_of(slug):
    """Bereich einer generierten Seite fuer Menue-Markierung und Brotkrumen."""
    if slug in SECTION_PAGES:
        return (SECTION_PAGES[slug], "page")
    if slug in SECTION_CHILDREN:
        return (SECTION_CHILDREN[slug], "true")
    if slug.startswith("ki-"):
        return ("ki", "true")
    if slug.startswith(SECTION_NONE):
        return None
    return ("it", "true")


# Handgebaute Seiten, deren <header> und <footer> sync_shared() ersetzt: Pfad -> current
HAND_PAGES = {
    "index.html": None,
    "kontakt/index.html": ("kontakt", "page"),
    "fernwartung/index.html": ("fernwartung", "page"),
    "empfehlungen/index.html": None,
    "impressum/index.html": None,
    "datenschutz/index.html": None,
    "agb/index.html": None,
    "barrierefreiheit/index.html": None,
    "404.html": None,
}
HEADER_RE = re.compile(r'<header class="site-header">.*?</header>', re.S)


FOOTER_RE = re.compile(r'<footer class="site-footer">.*?</footer>', re.S)
UPDATED_RE = re.compile(r'<span>Zuletzt aktualisiert: ([^<]+)</span>')
SPRITE_RE = re.compile(r'<svg[^>]*\bid="icon-sprite"[^>]*>.*?</svg>', re.S)
# style.css/main.js in jeder Schreibweise (relativ, ../, absolut, mit oder ohne ?v=)
STYLE_CSS_RE = re.compile(r'href="(?:\.\./)*/?assets/css/style\.css(?:\?v=[^"]*)?"')
MAIN_JS_RE = re.compile(r'src="(?:\.\./)*/?assets/js/main\.js(?:\?v=[^"]*)?"')
# Abschluss K5 auf den Handseiten (seit Task 9, Release C1): sync_shared ersetzt einen vorhandenen Abschluss
# (CLOSING_RE) oder setzt ihn vor </main>. Pfad -> (Seitenname fuer den WhatsApp-Satz nach Textblatt §4, None:
# allgemeiner Abschluss-Satz; Datum der Autorzeile, None: ohne „Zuletzt aktualisiert“). Kontakt traegt das Datum
# seiner Textaenderung, Fernwartung das der letzten Anleitung (09.10.2026); Rechtsseiten fuehren ihren Stand im
# Text, die 404 hat keinen. Nicht hier: Startseite (eigener Abschluss) und empfehlungen (Task 10).
HAND_CLOSING = {
    "kontakt/index.html": ("Kontakt", KONTAKT_DATE_DISP),
    "fernwartung/index.html": ("Fernwartung", "9. Oktober 2026"),
    "impressum/index.html": (None, None),
    "datenschutz/index.html": (None, None),
    "agb/index.html": (None, None),
    "barrierefreiheit/index.html": (None, None),
    "404.html": (None, None),
}
CLOSING_RE = re.compile(r'<section class="cta-sec".*?</section>', re.S)
# Font-Preload wie in head() der Generator-Seiten, vor dem fonts.css-Link der Handseite und mit dessen Pfad
# (../assets/… oder /assets/… bei der 404), damit die URL der des @font-face in fonts.css entspricht
FONTS_CSS_RE = re.compile(r'( *)<link rel="stylesheet" href="((?:\.\./)*|/)assets/css/fonts\.css"/?>')
FONT_PRELOADS = ("Manrope-latin.woff2", "SpaceGrotesk-latin.woff2")


def preload_fonts(html, nl):
    """Setzt die Font-Preloads vor fonts.css (Layout-Sprung beim ersten Aufruf, Release B), je Schrift nur, wenn ihr
    Preload noch fehlt (Startseite, zweiter Lauf: unveraendert)."""
    missing = [f for f in FONT_PRELOADS
               if not re.search(r'<link rel="preload" as="font"[^>]*' + re.escape(f), html)]
    if not missing:
        return html
    m = FONTS_CSS_RE.search(html)
    if not m:
        raise SystemExit("preload_fonts: fonts.css-Link fehlt")
    links = "".join('{i}<link rel="preload" as="font" type="font/woff2" crossorigin href="{p}assets/fonts/{f}"/>{nl}'
                    .format(i=m.group(1), p=m.group(2), f=f, nl=nl) for f in missing)
    return html[:m.start()] + links + html[m.start():]


def sync_shared(places, services):
    """Schreibt den gemeinsamen Header und Footer in die handgebauten Seiten, setzt dort
    style.css/main.js auf die versionierte Form (ASSET_VER) und das Icon-Sprite vor den
    Header (nicht auf der Startseite, siehe ICON_SPRITE).
    Ein vorhandenes 'Zuletzt aktualisiert' im Fuss (Startseite) bleibt erhalten."""
    for rel, current in HAND_PAGES.items():
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8", newline="") as f:
            html = f.read()
        home = rel == "index.html"
        page_path = "/" + os.path.dirname(rel) + "/" if "/" in rel else "/"
        old_footer = FOOTER_RE.search(html)
        if not old_footer or not HEADER_RE.search(html):
            raise SystemExit("Header oder Footer fehlt in " + rel)
        upd = UPDATED_RE.search(old_footer.group(0))
        blocks = [(HEADER_RE, nav_html(current, home=home)),
                  (FOOTER_RE, footer_html(places, services, page_path,
                                          upd.group(1) if upd else None, home))]
        html_new = html
        nl = "\r\n" if "\r\n" in html else "\n"
        for rx, block in blocks:
            # Zeilenenden der Datei beibehalten (404.html war CRLF)
            block = block.replace("\n", nl)
            html_new = rx.sub(lambda _m, b=block: b, html_new, count=1)
        html_new = STYLE_CSS_RE.sub(lambda _m: 'href="' + asset("css/style.css") + '"', html_new)
        html_new = MAIN_JS_RE.sub(lambda _m: 'src="' + asset("js/main.js") + '"', html_new)
        if not home:
            sprite = ICON_SPRITE.replace("\n", nl)
            if SPRITE_RE.search(html_new):
                html_new = SPRITE_RE.sub(lambda _m: sprite, html_new, count=1)
            else:
                html_new = html_new.replace('<header class="site-header">',
                                            sprite + nl + '<header class="site-header">', 1)
            html_new = preload_fonts(html_new, nl)
        if rel in HAND_CLOSING:
            name, mod = HAND_CLOSING[rel]
            wa = WA(WA_SEITE.format(nav=name)) if name else None
            # ohne Kontaktleiste (Rechtsseiten, 404) bleiben die Knoepfe des Abschlusses auch am Handy sichtbar
            sticky = 'class="sticky-contact"' in html_new
            block = closing(mod, wa, sticky=sticky).replace("\n", nl)
            if CLOSING_RE.search(html_new):
                html_new = CLOSING_RE.sub(lambda _m: block, html_new, count=1)
            elif "</main>" in html_new:
                html_new = html_new.replace("</main>", block + nl + "</main>", 1)
            else:
                raise SystemExit("Abschluss: weder cta-sec noch </main> in " + rel)
        if html_new != html:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(html_new)
            print("  Header/Footer aktualisiert: " + rel)

STICKY = """<div class="sticky-contact" id="stickyContact" role="navigation" aria-label="Kontakt-Optionen">
  <a href="tel:+491782584438" class="sc-btn sc-phone" aria-label="Anrufen">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
    <span>Anrufen</span>
  </a>
  <a href="__WA_KONTAKTLEISTE__" target="_blank" rel="noopener" class="sc-btn sc-wa" aria-label="WhatsApp">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.5.5 0 0 0 .611.611l4.458-1.495A11.96 11.96 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.75c-2.278 0-4.381-.733-6.093-1.975l-.426-.307-2.645.887.887-2.645-.307-.426A9.72 9.72 0 0 1 2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75z"/></svg>
    <span>WhatsApp</span>
  </a>
  <a href="mailto:info@grundke-it.de" class="sc-btn sc-mail" aria-label="E-Mail">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
    <span>E-Mail</span>
  </a>
</div>""".replace("__WA_KONTAKTLEISTE__", WA(WA_TEXT["kontaktleiste"]))


def esc(t):
    """Minimales HTML-Escaping fuer Textinhalte."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def schema_script(d):
    return ('  <script type="application/ld+json">\n'
            + json.dumps(d, ensure_ascii=False, indent=2)
            + "\n  </script>")


def up(slug):
    """Relativer Pfad zur Wurzel: '../' fuer /slug/, '../../' fuer /ratgeber/thema/."""
    return "../" * (slug.count("/") + 1)


def head(title, desc, slug, og_title, og_desc, og_alt, tw_desc=None, tw_alt=None):
    """<head> bis einschliesslich style.css. tw_desc/tw_alt (seit Task 8, aus meta_extra): eigene
    twitter:description und twitter:image:alt; ohne sie twitter:description = og_desc und kein Alt-Text."""
    canonical = DOMAIN + "/" + slug + "/"
    tw_alt_html = '\n  <meta name="twitter:image:alt" content="{}"/>'.format(esc(tw_alt)) if tw_alt else ""
    return """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>{title}</title>
  <meta name="description" content="{desc}"/>
  <meta name="author" content="Andreas Grundke"/>
  <meta name="robots" content="index, follow, max-image-preview:large"/>
  <link rel="canonical" href="{canonical}"/>
  <meta property="og:title" content="{og_title}"/>
  <meta property="og:description" content="{og_desc}"/>
  <meta property="og:url" content="{canonical}"/>
  <meta property="og:type" content="website"/>
  <meta property="og:locale" content="de_DE"/>
  <meta property="og:site_name" content="Grundke IT-Service"/>
  <meta property="og:image" content="{domain}/assets/img/og-image.png"/>
  <meta property="og:image:width" content="1200"/>
  <meta property="og:image:height" content="630"/>
  <meta property="og:image:alt" content="{og_alt}"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="{og_title}"/>
  <meta name="twitter:description" content="{tw_desc}"/>
  <meta name="twitter:image" content="{domain}/assets/img/og-image.png"/>{tw_alt}
  <link rel="icon" type="image/x-icon" href="/favicon.ico"/>
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png"/>
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"/>
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"/>
  <link rel="manifest" href="/site.webmanifest"/>
  <meta name="theme-color" content="#0c4da2"/>
  <meta name="apple-mobile-web-app-title" content="Grundke IT"/>
  <meta name="application-name" content="Grundke IT"/>
  <meta name="msapplication-TileColor" content="#0c4da2"/>
  <link rel="preload" as="font" type="font/woff2" crossorigin href="{up}assets/fonts/Manrope-latin.woff2"/>
  <link rel="preload" as="font" type="font/woff2" crossorigin href="{up}assets/fonts/SpaceGrotesk-latin.woff2"/>
  <link rel="stylesheet" href="{up}assets/css/fonts.css"/>
  <link rel="stylesheet" href="{css}"/>
""".format(title=esc(title), desc=esc(desc), canonical=canonical,
           og_title=esc(og_title), og_desc=esc(og_desc), og_alt=esc(og_alt),
           tw_desc=esc(tw_desc or og_desc), tw_alt=tw_alt_html,
           domain=DOMAIN, up=up(slug), css=asset("css/style.css"))


MAILTO_PREFILLED = "mailto:info@grundke-it.de?subject=Anfrage%20%C3%BCber%20grundke-it.de&amp;body=Hallo%20Andreas%2C%0A%0AMein%20Anliegen%3A%0A%0A%0A%0AAm%20besten%20erreichbar%20bin%20ich%20unter%3A%0ATelefon%3A%20%0AE-Mail%3A%20%0A%0AGew%C3%BCnschter%20R%C3%BCckruf-Zeitraum%3A%20%0A%0A---%0AMit%20dem%20Absenden%20dieser%20E-Mail%20stimme%20ich%20der%20Verarbeitung%20meiner%20Angaben%20gem%C3%A4%C3%9F%20der%20Datenschutzerkl%C3%A4rung%20zu%20(https%3A%2F%2Fgrundke-it.de%2Fdatenschutz%2F)."
LEGAL_LINKS = [("Impressum", "/impressum/"), ("Datenschutz", "/datenschutz/"),
               ("AGB", "/agb/"), ("Barrierefreiheit", "/barrierefreiheit/")]


def group_of(sv):
    """Spalte im Fuss: 'it' (IT-Betreuung), 'ki' (KI, Software & Websites) oder 'ratgeber'."""
    if sv.get("group"):
        return sv["group"]
    return "ki" if sv["slug"].startswith("ki-") else "it"


def footer_html(places, services, current_path="", updated=None, home=False):
    """Gemeinsamer Fuss fuer ALLE Seiten (seit 2026-09-23; vorher fuenf Varianten).
    Aufbau: Marke/Kontakt · IT-Betreuung · KI, Software & Websites · Standorte + Ratgeber ·
    Kontakt; darunter eine feste Zeile mit Impressum, Datenschutz, AGB, Barrierefreiheit.
    Seit 2026-10-10 sind die Spalten 2-5 <details>: ohne JS offen, am Handy klappt
    main.js (initFooter) sie zu. Die Rechtszeile klappt nie zu.
    current_path markiert den Link der aktuellen Seite (aria-current), updated zeigt
    optional 'Zuletzt aktualisiert' (nur die Startseite fuehrt das im Fuss)."""
    def cur(href):
        return ' aria-current="page"' if href == current_path else ""
    def li(label, href):
        return '\n          <li><a href="{h}"{c}>{l}</a></li>'.format(h=href, c=cur(href), l=esc(label))
    def col(title, links, indent="      "):
        return ('\n{i}<details class="foot-col" open><summary class="foot-h">{t}</summary>'
                '\n{i}  <ul class="foot-links">{l}\n{i}  </ul>\n{i}</details>').format(
                    i=indent, t=title, l=links.replace("\n", "\n" + indent[6:]))
    def group_links(group):
        return "".join(li(sv["nav"], "/" + sv["slug"] + "/") for sv in services if group_of(sv) == group)
    # IT-Sicherheitsschulung kommt seit Task 8 als SERVICES-Eintrag (group "it", nach lizenzen) ueber group_links
    it_links = group_links("it") + li("Produktempfehlungen", "/empfehlungen/")
    ki_links = group_links("ki")
    ratgeber_links = group_links("ratgeber")
    place_links = "".join(li("IT-Service " + pl["name"], "/it-service-" + pl["slug"] + "/") for pl in places)
    contact_links = (li("So arbeite ich", "#ablauf" if home else "/#ablauf")
                     + li("Kontakt", "/kontakt/") + li("Fernwartung starten", "/fernwartung/"))
    legal_html = "".join('\n        <a href="{h}"{c}>{l}</a>'.format(h=h, c=cur(h), l=l) for l, h in LEGAL_LINKS)
    updated_html = '\n      <span>Zuletzt aktualisiert: {}</span>'.format(updated) if updated else ""
    return """<footer class="site-footer">
  <div class="inner">
    <div class="foot-grid">
      <div>
        <div class="foot-brand">Grundke IT-Service</div>
        <p class="foot-desc">Deine IT-Abteilung. Nur extern.<br>IT, KI, Software und Websites für Betriebe im Münchner Osten.<br>Angebot für Unternehmen, alle Preise zzgl. MwSt.</p>
        <address class="foot-contact" style="font-style:normal;">
          <a href="tel:+491782584438"><svg class="foot-ico" width="14" height="14" aria-hidden="true"><use href="#ico-phone"/></svg>0178 258 44 38</a>
          <a href="{wa}" target="_blank" rel="noopener">WhatsApp schreiben</a>
          <a href="{mailto}">info@grundke-it.de</a>
          <a href="https://grundke-it.de">www.grundke-it.de</a>
        </address>
      </div>{col_it}{col_ki}
      <div class="foot-pair">{col_places}{col_ratgeber}
      </div>{col_contact}
    </div>
    <div class="foot-bottom">
      <nav class="foot-legal" aria-label="Rechtliches">{legal}
      </nav>
      <span>© 2026 Grundke IT-Service · Andreas Grundke · Beethovenring 16 · 85630 Grasbrunn</span>{updated}
      <span class="foot-ci">CI 2026.01 · grundke-it.de</span>
    </div>
  </div>
</footer>""".format(mailto=MAILTO_PREFILLED, wa=WA(WA_TEXT["fuss"]),
                     col_it=col("IT-Betreuung", it_links),
                     col_ki=col("KI, Software &amp; Websites", ki_links),
                     col_places=col("Standorte", place_links, "        "),
                     col_ratgeber=col("Ratgeber", ratgeber_links, "        "),
                     col_contact=col("Kontakt", contact_links),
                     legal=legal_html, updated=updated_html)


KI_HUB = ("KI im Betrieb", "ki-fuer-kmu")
RATGEBER_HUB = ("Ratgeber", "ratgeber")


def crumb_trail(name, slug):
    """Pfad Startseite > (KI-Hub) > Seite als Liste von (Name, URL-Pfad)."""
    trail = [("Startseite", "/")]
    if (slug.startswith("ki-") or SECTION_CHILDREN.get(slug) == "ki") and slug != KI_HUB[1]:
        trail.append((KI_HUB[0], "/" + KI_HUB[1] + "/"))
    if slug.startswith(RATGEBER_HUB[1] + "/"):
        trail.append((RATGEBER_HUB[0], "/" + RATGEBER_HUB[1] + "/"))
    trail.append((name, "/" + slug + "/"))
    return trail


def breadcrumb(name, slug):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + u}
            for i, (n, u) in enumerate(crumb_trail(name, slug), start=1)
        ],
    }


def crumbs_html(name, slug):
    """Sichtbare Brotkrumen, deckungsgleich mit dem BreadcrumbList-Schema."""
    trail = crumb_trail(name, slug)
    links = "".join('<li><a href="{u}">{n}</a></li>'.format(u=u, n=esc(n)) for n, u in trail[:-1])
    return ('<nav class="lp-crumbs" aria-label="Brotkrumen"><ol>{l}'
            '<li aria-current="page">{n}</li></ol></nav>').format(l=links, n=esc(trail[-1][0]))


def faq_schema(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }


def webpage_schema(title, desc, slug, pub=None, mod=None):
    """WebPage-Knoten: verknuepft Autor (Andreas Grundke, @id von Startseite),
    Herausgeber und Datumsangaben (datePublished/dateModified) -> E-E-A-T + Freshness."""
    url = DOMAIN + "/" + slug + "/"
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": title,
        "description": desc,
        "inLanguage": "de-DE",
        "isPartOf": {"@id": WEBSITE_ID},
        "datePublished": pub or PUB_DATE,
        "dateModified": mod or TODAY,
        "author": {"@type": "Person", "@id": PERSON_ID, "name": "Andreas Grundke",
                   "url": DOMAIN + "/"},
        "publisher": {"@type": "Organization", "@id": BUSINESS_ID,
                      "name": "Andreas Grundke IT-Service"},
    }


def faq_html(faqs):
    """FAQ als Akkordeon (<details>), gleiches Markup wie auf der Startseite.
    Text bleibt zeichengleich mit dem FAQPage-Schema (faq_schema)."""
    items = "".join(
        '\n        <details class="faq-item"><summary>{q} <span class="faq-ico" aria-hidden="true">+</span></summary>'
        '<div class="faq-a">{a}</div></details>'.format(q=esc(q), a=esc(a)) for q, a in faqs)
    return '\n      <div class="faq-wrap">' + items + '\n      </div>'


def page(head_html, schema_blocks, main_html, places, services, slug=""):
    """Ganze Seite: <head> mit den gemeinsamen Prosa-Regeln (STYLE) und dem Schema, Icon-Sprite, Kopfzeile,
    Inhalt, Fuss, Kontaktleiste. Seit Task 7 ohne seitenspezifischen <style> (KI_STYLE, NEW_STYLE und die
    alte Huelle STYLE_LEGACY sind nach style.css gewandert bzw. entfallen)."""
    parts = [head_html, STYLE]
    for s in schema_blocks:
        parts.append(schema_script(s))
    parts.append("</head>")
    parts.append('<body class="has-sticky-call">')
    parts.append('<a class="skip-link" href="#main">Zum Inhalt springen</a>')
    parts.append(ICON_SPRITE)
    parts.append(nav_html(section_of(slug)))
    parts.append('\n<main id="main">')
    parts.append(main_html)
    parts.append("</main>\n")
    parts.append(footer_html(places, services, "/" + slug + "/"))
    parts.append('<script src="' + asset("js/main.js") + '"></script>\n')
    parts.append(STICKY)
    parts.append("</body>\n</html>\n")
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
#  Generator-Huelle (seit 10.10.2026, Website-Umbau Release B)                 #
# --------------------------------------------------------------------------- #
# Ein Aufbau fuer alle Generator-Seiten (Spec §6): Kopf (Krumen, H1, K4, Antwortsatz, Knoepfe,
# Belegzeile, Beispiel-Chat oder Wege) -> Abschnitte im Wechsel -> Stimmen -> Preise -> FAQ -> Abschluss K5
# mit Autorzeile. Bausteine kommen nur aus style.css. Umgestellt Seite fuer Seite (Task 5: drei Kernseiten,
# Task 6: Orte und IT-Seiten, Task 7: KI-Bereich, Software, Websites, Ratgeber); seither gibt es keine
# zweite Huelle mehr. Ratgeber-Artikel (kind "ratgeber") stehen nach dem Kopf in einer Lesespalte.
# WhatsApp-Satz fuer Kopf und Abschluss einer Unterseite (Textblatt §4): die Seite ist das Merkmal
WA_SEITE = "Hallo Andreas, ich komme über deine Seite „{nav}“."
AUTHOR_ROLE = "Fachinformatiker für Systemintegration · über 20 Jahre IT"
# Beispiel-Chat: Absender -> (Blasen-Klasse wie im Hero-Chat der Startseite, Name fuer Screenreader)
CHAT_SENDER = {"kunde": ("is-me", "Kunde"), "andreas": ("is-ag", "Andreas")}
H2_SPLIT_RE = re.compile(r"\s*<h2>(.*?)</h2>\s*", re.S)
# Marke in einem extra-Abschnitt: Text davor links, danach rechts (<!--split--> 1,3 : 1; <!--split-wide-->
# 1 : 1,35 mit breiterer rechter Spalte, wenn rechts Hinweis und Kasten stehen)
SPLIT_RE = re.compile(r"<!--split(-wide)?-->")
# Marke in einem extra-Abschnitt (Task 7): Text zwischen <!--more--> und <!--/more--> steht im HTML, ist aber
# zugeklappt (<details class="more">, Baustein der Startseite). Fuer lange Abschnitte, deren Anfang reicht: KI-Hub
# (Vorgabe Release B) und KI sicher einsetzen (sonst am Handy ueber 8.000 px, AK5). Kaesten mit Handlung
# (Potenzialcheck, Website-Check) bleiben ausserhalb. Beschriftung „Mehr dazu“, mit <!--more:Text--> eine eigene
# (Bedienlabel nach dem Inhalt, z. B. wenn davor ein Doppelpunkt auf den zugeklappten Teil zeigt).
# Regeln (check_markers, Abbruch beim Bauen): paarweise, nicht ueber eine <h2> hinweg, kein <!--split--> darin.
MORE_RE = re.compile(r"<!--more(?::([^>]*?))?-->(.*?)<!--/more-->", re.S)
MORE_SUMMARY = "Mehr dazu"
MARKER_RE = re.compile(r"<!--(/?)more(?::[^>]*?)?-->|<!--split[^>]*-->|<h2>")
# Ratgeber-Artikel (kind "ratgeber") kennen nur diese Felder; alles andere (cards, prices, trust, voices, k, chat,
# Marken …) kann die Lesespalte nicht darstellen und bricht den Bau ab (check_ratgeber).
RATGEBER_KEYS = {"slug", "nav", "group", "kind", "title", "h1", "service_type", "published", "modified",
                 "modified_disp", "cta2_href", "cta2_text", "desc", "lead", "intro", "raw_intro", "extra", "faqs"}


def section(content, alt=False, label="", title="", sid="", aside=False, title_cls=""):
    """Abschnitt der Huelle: .sec (Grundflaeche) oder .sec--alt (zweite Flaeche), optional mit
    Kicker (label, Text), Ueberschrift (title, HTML aus den Daten wie bisher) und id.
    aside=True (FAQ, eine einzelne Stimme): ab 1024 px steht die Ueberschrift links, der Inhalt in
    der breiteren rechten Spalte (.sec--aside), statt einer schmalen Spalte mit leerer rechter Haelfte.
    title_cls: zusaetzliche Klasse der Ueberschrift (s-title--long fuer lange seitliche Ueberschriften)."""
    top = ""
    if label:
        top += '\n    <div class="s-label">' + esc(label) + '</div>'
    if title:
        top += '\n    <h2 class="s-title{c}">'.format(c=" " + title_cls if title_cls else "") + title + '</h2>'
    if aside:
        content = '\n    <div class="sec-aside-body">' + content + '\n    </div>'
    return '<section class="sec{a}{s}"{i}>\n  <div class="inner">{t}{c}\n  </div>\n</section>'.format(
        a=" sec--alt" if alt else "", s=" sec--aside" if aside else "", i=' id="' + sid + '"' if sid else "",
        t=top, c=content)


def mini_chat(lines):
    """Kurzer Beispielverlauf (nur it-notdienst, managed-it-service, it-betreuer-wechseln), Kopfzeile
    „Beispiel aus dem Alltag“ wie im Hero-Chat der Startseite, ohne Uhrzeiten (Textblatt §2). Die
    Kopfzeile ist die Bildunterschrift, die Liste enthaelt nur die Nachrichten (Screenreader zaehlen
    so nur diese). lines: (Absender, Text), Absender "kunde" (rechts) oder "andreas" (links)."""
    msgs = "".join('\n        <li class="hc-msg {c}"><span class="sr-only">{w}: </span>{t}</li>'.format(
        c=CHAT_SENDER[who][0], w=CHAT_SENDER[who][1], t=esc(text)) for who, text in lines)
    return ('\n    <figure class="mini-chat-box">'
            '\n      <figcaption class="mini-chat-h"><span class="ava" aria-hidden="true">AG</span>'
            '<span class="mini-chat-who">Andreas IT<small>Beispiel aus dem Alltag</small></span></figcaption>'
            '\n      <ol class="mini-chat">' + msgs + '\n      </ol>\n    </figure>')


def eur_nbsp(text):
    """Leerzeichen vor dem Eurozeichen geschuetzt (wie auf der Startseite: 149&nbsp;€)."""
    return esc(text).replace(" €", "&nbsp;€")


def page_head(s, crumbs):
    """Seitenkopf in fester Reihenfolge (Textblatt §1): Krumen, H1 (Text wie bisher, bei Hubs die
    Akzentzeile als <em>; h1_nowrap haelt einen Begriff in einer Zeile), K4 (.page-k), Antwortsatz
    (.s-sub), Knoepfe Anrufen + WhatsApp (am Handy uebernimmt die Kontaktleiste), Belegzeile: zuerst
    die Google-Bewertungen mit Link zur Herkunft, dann ein Beleg der Seite (proof2: Symbol, Text) und
    optional ein dritter (proof3, gleiches Format).
    Daneben optional der Beispiel-Chat oder bei Hubs die Wege zu den Unterseiten (nav.lp-paths), beides ab
    1024 px rechts, darunter unter dem Kopf. Ohne Chat und ohne Wege ab 1024 px ein Raster: H1 ueber beide
    Spalten, darunter links K4, rechts Antwortsatz, Knoepfe und Belegzeile; die Reihenfolge im HTML bleibt
    dieselbe (erste 300 Zeichen, Screenreader).
    Ratgeber (kind "ratgeber-hub" und "ratgeber", Task 7): kein K4, statt Antwortsatz der bisherige Vorspann ("lead"),
    nur der Anruf-Knopf, keine Belegzeile; der Kopf bleibt einspaltig (ohne K4 gaebe es keine linke Spalte)."""
    hero = s.get("hero")
    ratgeber = s.get("kind") in ("ratgeber-hub", "ratgeber")
    h1 = s["h1"]
    if s.get("h1_nowrap"):
        if s["h1_nowrap"] not in h1:
            raise SystemExit("page_head: h1_nowrap steht nicht in der H1 von " + s["slug"])
        h1 = h1.replace(s["h1_nowrap"], '<span class="nowrap">' + s["h1_nowrap"] + "</span>", 1)
    # h1_em (Task 8, schulung): ein Wort der H1 als Akzent (<em>), Text der H1 bleibt gleich
    if s.get("h1_em"):
        if s["h1_em"] not in h1:
            raise SystemExit("page_head: h1_em steht nicht in der H1 von " + s["slug"])
        h1 = h1.replace(s["h1_em"], "<em>" + s["h1_em"] + "</em>", 1)
    # Akzentzeile der Hubs in eigener Zeile wie die H1 der Startseite (<br> <em>), Text der H1 bleibt gleich
    h1 += "<br> <em>" + hero["accent"] + "</em>" if hero else ""
    # proof2: Beleg der Seite, proof3 (optional): weiterer Beleg dahinter, z. B. der Stundensatz
    proof2 = "".join('\n        <li><svg aria-hidden="true"><use href="#{i}"/></svg>{t}</li>'.format(
        i=s[key][0], t=eur_nbsp(s[key][1])) for key in ("proof2", "proof3") if s.get(key))
    side = mini_chat(s["chat"]) if s.get("chat") else ""
    if hero:
        side += ('\n    <nav class="lp-paths" aria-label="{l}">\n      <h2 class="lp-paths-h">{l}</h2>\n      <ul>{p}'
                 '\n      </ul>\n    </nav>').format(l=esc(hero["paths_label"]), p="".join(
                     '\n        <li><a href="{h}"><span class="lp-path-t">{t}</span><span class="lp-path-d">{d}</span></a></li>'
                     .format(h=h, t=esc(t), d=esc(d)) for t, d, h in hero["paths"]))
    two = not side and not ratgeber   # kein Chat, keine Wege: Kopf selbst zweispaltig
    head_a = '\n      <h1 class="page-h1">{h1}</h1>'.format(h1=h1)
    if not ratgeber:
        head_a += '\n      <p class="page-k">{k}</p>'.format(k=esc(s["k"]))
    wa_btn = "" if ratgeber else (
        '\n        <a href="{wa}" target="_blank" rel="noopener" class="hc-wa"><svg width="18" height="18" '
        'aria-hidden="true"><use href="#ico-wa"/></svg>WhatsApp</a>').format(wa=WA(WA_SEITE.format(nav=s["nav"])))
    proofs = "" if ratgeber else (
        '\n      <ul class="hc-proof">\n        <li><svg class="is-star" aria-hidden="true"><use href="#ico-star"/></svg>'
        '<a href="/#bewertungen-herkunft" data-proof>5,0 bei {n} Google-Bewertungen</a></li>{proof2}\n      </ul>'
    ).format(n=REVIEW_COUNT_GOOGLE, proof2=proof2)
    head_b = """
      <p class="s-sub measure">{answer}</p>
      <div class="hc-ctas">
        <a href="tel:{tel}" class="btn-p hc-call"><svg width="18" height="18" aria-hidden="true"><use href="#ico-phone"/></svg>Anrufen <span class="hc-num">{phone}</span></a>{wa_btn}
      </div>{proofs}""".format(answer=esc(s["lead"] if ratgeber else s["answer"]), tel=PHONE, phone=PHONE_DISP,
                               wa_btn=wa_btn, proofs=proofs)
    if two:
        # H1 und K4 bleiben direkte Kinder (Rasterflaechen h1/kum), der Rest steht in .page-head-b (antwort)
        head_b = '\n      <div class="page-head-b">' + head_b.replace("\n", "\n  ") + '\n      </div>'
    grid = " page-head-grid--chat" if s.get("chat") else (" page-head-grid--paths" if hero else "")
    return """<section class="sec sec--glow page-head">
  <div class="inner page-head-grid{grid}">
    <div class="page-head-copy{copy}">
      {crumbs}{a}{b}
    </div>{side}
  </div>
</section>""".format(grid=grid, copy=" page-head-copy--two" if two else "",
                     crumbs=crumbs, a=head_a, b=head_b, side=side)


def feat_rows(cards):
    """Leistungen als Zeilen mit Haarlinie (wie „Typische Anrufe“ der Startseite): Symbol-Kachel aus
    dem Sprite, Titel, Text; am Desktop zweispaltig, am Handy ohne Rahmen. cards: (Titel, Text[, Symbol])."""
    return '\n    <ul class="feat-rows">' + "".join(
        ('\n      <li><span class="feat-ico" aria-hidden="true"><svg><use href="#{i}"/></svg></span>'
         '<div><h3>{h}</h3><p>{t}</p></div></li>').format(i=c[2] if len(c) > 2 else "ico-check", h=esc(c[0]), t=esc(c[1]))
        for c in cards) + '\n    </ul>'


def voices_html(ids):
    """1-2 Kundenstimmen einer Unterseite aus REVIEWS, woertlich und mit Quelle auf der Karte, darunter
    der Link zur Herkunft auf der Startseite. Nur Google-Bewertungen: die direkt uebermittelte Stimme
    steht nur auf der Startseite (Andreas 10.10.2026)."""
    by_id = {r["id"]: r for r in REVIEWS}
    cards = []
    for i in ids:
        r = by_id.get(i)
        if not r or r["source"] != "Google-Bewertung":
            raise SystemExit("voices_html: '" + i + "' fehlt in REVIEWS oder ist keine Google-Bewertung")
        cards.append(voice_card(r))
    return ('\n    <div class="testi-grid testi-grid--few">\n' + "\n".join(cards) + '\n    </div>'
            '\n    <p class="testi-source testi-source--link"><a href="/#bewertungen-herkunft">Woher die Stimmen kommen</a></p>')


# Zusatzfeld einer Preiskarte (sechstes Element, dict, seit Task 8): siehe price_card
PRICE_OPT_KEYS = {"add", "feats", "badge", "btn"}


def price_card(pr, slug):
    """Ein Preis als .price-card (Baustein der Startseite). Eintrag wie bisher: (Stufe, Betrag,
    Beschreibung, hervorgehoben[, Einheit[, Zusatz]]); ohne Einheit gilt der Monatspreis der Betreuungspakete.
    Jede Einheit muss „zzgl. MwSt.“ nennen.
    Zusatz (dict, seit Task 8, Schulung): "add" zweite Preiszeile unter der Einheit (z. B. Preis je Mitarbeiter,
    ebenfalls mit „zzgl. MwSt.“), "feats" Leistungen als .price-feats, "badge" Text des Abzeichens statt „Empfohlen“
    (None: hervorgehobene Karte ohne Abzeichen), "btn" (Text, href wie im HTML, also mit &amp;) Knopf .price-btn,
    solid bei hervorgehobener Karte, sonst out.
    Leistungen und Knopf stehen unter der Beschreibung, abgesetzt durch .price-div. Andere Felder: Abbruch."""
    tier, amount, desc, feat = pr[:4]
    unit = pr[4] if len(pr) > 4 else "/Monat zzgl. MwSt."
    opt = pr[5] if len(pr) > 5 else {}
    if "zzgl. MwSt." not in unit:
        raise SystemExit("price_card: Einheit ohne 'zzgl. MwSt.' auf " + slug + ": " + unit)
    if set(opt) - PRICE_OPT_KEYS:
        raise SystemExit("price_card: unbekannte Felder " + ", ".join(sorted(set(opt) - PRICE_OPT_KEYS)) + " auf " + slug)
    if opt.get("add") and "zzgl. MwSt." not in opt["add"]:
        raise SystemExit("price_card: Zusatzpreis ohne 'zzgl. MwSt.' auf " + slug + ": " + opt["add"])
    val = (esc(amount[:-2]) + '<span class="price-cur">&nbsp;€</span>') if amount.endswith(" €") else esc(amount)
    add = '\n        <div class="price-per">{}</div>'.format(eur_nbsp(opt["add"])) if opt.get("add") else ""
    more = ""
    if opt.get("feats"):
        more += ('\n        <ul class="price-feats">' + "".join(
            '\n          <li><span class="pfy" aria-hidden="true">&#10003;</span>{}</li>'.format(esc(f))
            for f in opt["feats"]) + '\n        </ul>')
    if opt.get("btn"):
        more += '\n        <a href="{h}" class="price-btn {k}">{t}</a>'.format(
            h=opt["btn"][1], k="solid" if feat else "out", t=esc(opt["btn"][0]))
    if more:
        more = '\n        <hr class="price-div">' + more
    badge = opt.get("badge", "Empfohlen")
    return ('\n      <div class="price-card{f}">{b}\n        <h3 class="price-name">{t}</h3>'
            '\n        <div class="price-val">{v}</div>\n        <div class="price-per">{u}</div>{a}'
            '\n        <p class="price-desc">{d}</p>{m}\n      </div>').format(
                f=" feat" if feat else "", t=esc(tier), v=val, u=eur_nbsp(unit), d=esc(desc), a=add, m=more,
                b='\n        <div class="price-badge">{}</div>'.format(esc(badge)) if feat and badge else "")


def prices_html(s):
    """Alle Preise einer Unterseite als Raster aus .price-card. prices_wide (Task 8 Fix-Runde 1, Karten mit
    Leistungen und Knopf): price-grid--wide, bis 1023 px eine Spalte in Lesebreite, ab 1024 px drei, Knopf unten."""
    cards = [price_card(pr, s["slug"]) for pr in s["prices"]]
    if s.get("prices_wide"):
        grid = "price-grid price-grid--wide"
    else:
        grid = "price-grid price-grid--3" if len(cards) == 3 else "price-grid"
    return '\n    <div class="{g}">{c}\n    </div>'.format(g=grid, c="".join(cards))


def closing(mod_disp, wa=None, next_link=None, sticky=True):
    """Abschluss K5 wie auf der Startseite (Knoepfe ab 768 px, am Handy die Kontaktleiste; QR zur
    Kontaktseite ab 1025 px) mit kompakter Autorzeile und dem Datum der Seite. wa: WhatsApp-Link
    (Satz der Seite), next_link: (href, Text) als Weg zur passenden naechsten Seite.
    Seit Task 9 (Handseiten): mod_disp None = Autorzeile ohne Datum; sticky=False fuer Seiten ohne Kontaktleiste,
    dort bleiben die Knoepfe auch am Handy sichtbar."""
    nxt = ""
    if next_link:
        nxt = ('\n    <p class="cta-next"><a href="{h}">{t}<svg width="16" height="16" aria-hidden="true">'
               '<use href="#ico-arrow-r"/></svg></a></p>').format(h=next_link[0], t=esc(next_link[1]))
    date = '<br><span class="cta-date">Zuletzt aktualisiert: {}</span>'.format(mod_disp) if mod_disp else ""
    return """<section class="cta-sec">
  <div class="inner">
    <h2 class="cta-h">Problem? <em>Ich bin dran.</em></h2>
    <p class="cta-sub">Ruf an, schreib auf WhatsApp oder per Mail. Am anderen Ende bin ich, Andreas Grundke. Gerne per Du.</p>
    <div class="cta-btns{mob}">
      <a href="tel:{tel}" class="btn-tel"><svg width="20" height="20" aria-hidden="true"><use href="#ico-phone"/></svg> {phone}</a>
      <a href="{wa}" target="_blank" rel="noopener" class="btn-wa"><svg width="20" height="20" aria-hidden="true"><use href="#ico-wa"/></svg> WhatsApp</a>
      <a href="{mailto}" class="btn-email"><svg width="20" height="20" aria-hidden="true"><use href="#ico-mail"/></svg> E-Mail schreiben</a>
    </div>
    <div class="hc-qr cta-qr">
      <a href="/kontakt/" title="Alle Kontaktwege"><img src="/assets/img/qr-tree.png" alt="QR-Code: Kontaktseite aufs Handy holen" width="88" height="88"/></a>
      <p><strong>Scan mich. Dann reden wir.</strong>Alle Kontaktwege direkt aufs Handy.</p>
    </div>{nxt}
    <div class="cta-author">
      <span class="ava" aria-hidden="true">AG</span>
      <p><strong>Andreas Grundke</strong> · {role}{date}</p>
    </div>
  </div>
</section>""".format(tel=PHONE, phone=PHONE_DISP, wa=wa or WA(WA_TEXT["abschluss"]), mailto=MAILTO_PREFILLED,
                     nxt=nxt, role=AUTHOR_ROLE, date=date, mob=" inline-cta-mobile" if sticky else "")


def extra_blocks(extra):
    """Zerlegt den Zusatz-HTML-Block ("extra") an seinen <h2> in (Titel, Inhalt) fuer eigene
    Abschnitte. Text vor der ersten Ueberschrift kommt mit leerem Titel zurueck."""
    parts = H2_SPLIT_RE.split(extra.strip())
    blocks = [("", parts[0])] if parts[0].strip() else []
    return blocks + [(parts[k], parts[k + 1]) for k in range(1, len(parts), 2)]


def prose(html_part):
    """Fliesstext aus den Daten (intro, extra) mit den Prosa-Regeln aus STYLE (Absaetze in Lesebreite)."""
    return '\n    <div class="lp-content">\n      ' + html_part.strip() + '\n    </div>'


def split(left, right, wide=False):
    """Zwei Spalten nebeneinander ab 1024 px (darunter untereinander), z. B. Text und Preis.
    Standard 1,3 : 1; wide=True 1 : 1,35 (rechte Spalte mit Hinweis und Kasten, sonst deutlich laenger)."""
    return '\n    <div class="sec-split{w}">\n    <div>'.format(w=" sec-split--wide" if wide else "") + left + \
        '\n    </div>\n    <div>' + right + '\n    </div>\n    </div>'


def more_html(m):
    """<!--more-->…<!--/more--> -> zugeklappter Teil (<details class="more">, Inhalt bleibt im HTML); Beschriftung
    „Mehr dazu“ oder der Text aus <!--more:Text-->."""
    return ('<details class="more">\n        <summary>' + esc(m.group(1) or MORE_SUMMARY) + '</summary>\n        '
            + m.group(2).strip() + '\n      </details>')


def check_markers(slug, extra):
    """Marken in "extra" pruefen, bevor gebaut wird (Task 7 Fix-Runde 1): <!--more--> und <!--/more--> stehen
    paarweise, ein Paar reicht nicht ueber eine <h2> (dort wird in Abschnitte zerlegt) und enthaelt kein
    <!--split-->. Sonst Abbruch mit Seite und Grund."""
    inside = False
    for m in MARKER_RE.finditer(extra):
        tok = m.group(0)
        if tok.startswith("<!--more"):
            if inside:
                raise SystemExit("Generator: <!--more--> ohne <!--/more--> vor dem naechsten <!--more--> auf " + slug)
            inside = True
        elif tok.startswith("<!--/more"):
            if not inside:
                raise SystemExit("Generator: <!--/more--> ohne <!--more--> davor auf " + slug)
            inside = False
        elif inside and tok == "<h2>":
            raise SystemExit("Generator: <!--more--> reicht ueber eine <h2> hinweg auf " + slug)
        elif inside:
            raise SystemExit("Generator: " + tok + " steht innerhalb von <!--more--> auf " + slug)
    if inside:
        raise SystemExit("Generator: <!--more--> ohne <!--/more--> auf " + slug)


def check_ratgeber(s):
    """Ratgeber-Artikel: nur die Felder aus RATGEBER_KEYS, intro als HTML (raw_intro=True), keine Marken in intro
    und extra (die Lesespalte kennt weder <!--more--> noch <!--split-->). Sonst Abbruch mit Seite und Grund."""
    extra_keys = sorted(set(s) - RATGEBER_KEYS)
    if extra_keys:
        raise SystemExit("Generator: Ratgeber-Artikel " + s["slug"] + " mit nicht unterstuetzten Feldern: "
                         + ", ".join(extra_keys))
    if s.get("raw_intro") is not True:
        raise SystemExit("Generator: Ratgeber-Artikel " + s["slug"] + " braucht raw_intro=True (Kurzantwort als HTML)")
    for key in ("lead", "intro", "faqs"):
        if not s.get(key):
            raise SystemExit("Generator: Ratgeber-Artikel " + s["slug"] + " ohne " + key)
    if re.search(r"<!--/?(more|split)", s["intro"] + s.get("extra", "")):
        raise SystemExit("Generator: Marke <!--more--> oder <!--split--> im Ratgeber-Artikel " + s["slug"])


def content_blocks(s):
    """Abschnitte zwischen Kopf und FAQ als (Titel, HTML), dazu die Titel mit seitlicher Ueberschrift.
    Einstieg (intro, Karten), extra an seinen <h2>, Stimmen, tail_blocks, row, Preise; Darstellung siehe
    render_shell."""
    slug = s["slug"]
    # intro ist seit Task 8 optional (schulung: der bisherige Vorspann ist im Kopf durch K4 und Antwortsatz ersetzt,
    # der Abschnitt beginnt direkt mit den Zeilen)
    intro = s.get("intro", "")
    if intro and not s.get("raw_intro"):
        intro = esc(intro)
    lead = prose(intro if intro.lstrip().startswith("<div") else "<p>" + intro + "</p>") if intro else ""
    trust_box = '\n    <div class="card-box"><p>' + s["trust"] + '</p></div>' if s.get("trust") else ""
    if s.get("intro_price"):
        lead = split(lead, price_card(s["intro_price"], slug))
    elif trust_box and not s.get("prices"):
        # Vertrauenstext neben dem Einstieg statt als Kasten am Ende (Desktop zweispaltig)
        lead, trust_box = split(lead, trust_box), ""
    # Ueberschrift des Einstiegs: mit Karten cards_h2 (Standard „Das steckt drin“), sonst intro_h2 (Ratgeber-Hub)
    blocks = [(s.get("cards_h2", "Das steckt drin") if s.get("cards") else s.get("intro_h2", ""),
               lead + (feat_rows(s["cards"]) if s.get("cards") else ""))]
    for title, body in extra_blocks(s.get("extra", "")):
        body = MORE_RE.sub(more_html, body)
        mark = SPLIT_RE.search(body)
        if mark:
            body_html = split(prose(body[:mark.start()]), prose(body[mark.end():]), wide=bool(mark.group(1)))
        else:
            body_html = prose(body)
        if title:
            blocks.append((title, body_html))
        else:
            blocks[-1] = (blocks[-1][0], blocks[-1][1] + body_html)
    if not s.get("prices"):
        blocks[-1] = (blocks[-1][0], blocks[-1][1] + trust_box)
    aside = {s.get("faq_h2", "Häufige Fragen")}
    if s.get("voices"):
        voices_h2 = s.get("voices_h2", "Was andere über mich sagen")
        blocks.append((voices_h2, voices_html(s["voices"])))
        if len(s["voices"]) == 1:
            aside.add(voices_h2)   # eine einzelne Stimme: Ueberschrift links, Karte rechts
    blocks += s.get("tail_blocks", [])
    if s.get("row"):
        # zwei Abschnitte als eine Zeile, in der Reihenfolge von "row" (links, rechts)
        pos = {t: k for k, (t, _c) in enumerate(blocks)}
        if not all(t in pos for t in s["row"]):
            raise SystemExit("render_shell: row-Titel fehlen auf " + slug)
        cols = ['\n    <h2 class="s-title">' + t + '</h2>' + blocks[pos[t]][1] for t in s["row"]]
        at = min(pos[t] for t in s["row"])
        blocks = [b for b in blocks if b[0] not in s["row"]]
        blocks.insert(at, ("", split(cols[0], cols[1])))
    if s.get("prices"):
        line = ""
        if s.get("price_line"):
            line = '\n    <p class="price-line"><strong>{}</strong> {}</p>'.format(
                esc(s["price_line"][0]), eur_nbsp(s["price_line"][1]))
        # prices_after (Satz unter den Preisen, z. B. Foerderhinweis) im Fliesstext-Stil (Task 7)
        after = prose(s["prices_after"]) if s.get("prices_after") else ""
        price_block = (s.get("prices_h2", "Pakete &amp; Preise"),
                       '\n    <p class="s-sub measure">' + s.get("prices_intro", "Transparente Monatspauschalen – "
                       "welches Paket passt, klären wir im kostenlosen Erstgespräch:") + '</p>'
                       + prices_html(s) + line + after + trust_box)
        # prices_before (Task 8 Fix-Runde 1, schulung): Preise vor dem Abschnitt mit diesem Titel statt am Ende,
        # z. B. damit der Hinweis „in Vorbereitung“ bei den Preisen vor der Beschreibung des Portals steht
        if s.get("prices_before"):
            titles = [t for t, _c in blocks]
            if s["prices_before"] not in titles:
                raise SystemExit("content_blocks: prices_before '" + s["prices_before"] + "' fehlt auf " + slug)
            blocks.insert(titles.index(s["prices_before"]), price_block)
        else:
            blocks.append(price_block)
    return blocks, aside


def render_shell(s, places, services, head_schema=None):
    """Leistungs-, Orts-, KI- oder Ratgeberseite in der Huelle. Kopf (<head>) und Schema wie bisher
    (service_head_schema; Ortsseiten geben ihr eigenes Paar als head_schema mit), Inhalte aus denselben
    Daten; neu sind k, answer, chat, voices (Textblatt) und die Darstellung: proof2 (zweiter Beleg im
    Kopf), h1_nowrap, intro_price (Preis neben dem Einstieg), price_line (Zeile unter den Paketen),
    row (zwei Abschnitte nebeneinander, auch der Stimmen-Abschnitt und tail_blocks), voices_h2 (eigene
    Ueberschrift ueber den Stimmen), tail_blocks ((Titel, HTML) nach den Stimmen), "<!--split-->" bzw.
    "<!--split-wide-->" in einem extra-Abschnitt (Text links, Rest rechts), "<!--more-->…<!--/more-->"
    (zugeklappter Teil, Task 7). Ein Vertrauenskasten erscheint nur mit eigenem "trust" (ohne Preise neben dem
    Einstieg, mit Preisen unter ihnen); TRUST_DEFAULT nur, wo eine Seite ihn ausdruecklich fuehrt (KI-Seiten).
    Ratgeber-Artikel (kind "ratgeber", Task 7): nach dem Kopf Kurzantwort und "extra" mit ihren H2 unveraendert
    in einer Lesespalte (article.measure), danach FAQ und Abschluss."""
    slug = s["slug"]
    h, schema = head_schema or service_head_schema(s)
    if s.get("kind") == "ratgeber":
        check_ratgeber(s)
        blocks = [("", '\n    <article class="lp-content measure lp-article">\n      '
                   + (s["intro"] + s.get("extra", "")).strip() + '\n    </article>')]
        aside = {s.get("faq_h2", "Häufige Fragen")}
    else:
        check_markers(slug, s.get("extra", ""))
        blocks, aside = content_blocks(s)
    related = related_html(slug, services)
    blocks.append((s.get("faq_h2", "Häufige Fragen"), faq_html(s["faqs"]) + (prose(related) if related else "")))
    # Flaechen im Wechsel, der erste Abschnitt nach dem Kopf auf der zweiten Flaeche
    secs = [page_head(s, crumbs_html(s["nav"], slug))]
    # aside_long (Task 8 Fix-Runde 1): seitliche Ueberschriften mit einem langen Wort (schulung: FAQ-Titel mit
    # „IT-Sicherheitsschulung“ in .nowrap) ab 1024 px kleiner, damit sie in der linken Spalte bleiben
    long_cls = "s-title--long" if s.get("aside_long") else ""
    secs += [section(content, alt=k % 2 == 0, title=title, aside=bool(title) and title in aside,
                     title_cls=long_cls if bool(title) and title in aside else "")
             for k, (title, content) in enumerate(blocks)]
    secs.append(closing(s.get("modified_disp", TODAY_DISP), WA(WA_SEITE.format(nav=s["nav"])),
                        (s.get("cta2_href", "/it-service-grasbrunn/"), s.get("cta2_text", "IT-Service in deiner Region"))))
    main_html = "\n\n".join(secs) + "\n"
    if "<!--more" in main_html or "<!--/more" in main_html:
        raise SystemExit("Generator: nach dem Ersetzen steht noch eine Marke <!--more--> auf " + slug)
    return page(h, schema, main_html, places, services, slug=slug)


# --------------------------------------------------------------------------- #
#  Daten: Orte                                                                 #
# --------------------------------------------------------------------------- #

# Ortsseiten in der Generator-Huelle (seit 10.10.2026, Task 6): k (K4) und answer (Antwortsatz) und
# voice (eine Google-Stimme ohne Ortsbezug) aus dem Textblatt §1/§3; intro und near_a von Vaterstetten,
# Haar und Baldham mit den freigegebenen Ersatzsaetzen (Textblatt, Frage 5) statt Minuten- und
# Rueckruf-Zusagen. Fix-Runde 1: Haar ohne die unbelegte Aussage „einer der gewerbestärksten Orte“,
# Grasbrunn-Einstieg beginnt nicht mehr wortgleich mit dem K4 („Mein Sitz ist im Beethovenring 16 …“).
# rows_order (Fix-Runde 2): Leistungszeilen in der Reihenfolge, in der der Antwortsatz sie nennt (place_rows);
# Baldham und Zorneding nennen keine Leistung und behalten die Grundreihenfolge.
PLACE_DATE = "2026-10-10"            # dateModified, Sitemap und „Zuletzt aktualisiert“ aller Ortsseiten
PLACE_DATE_DISP = "10. Oktober 2026"
PLACES = [
    {
        "slug": "grasbrunn", "name": "Grasbrunn", "title_name": "Grasbrunn & Neukeferloh",
        "area": ["Grasbrunn", "Neukeferloh", "Harthausen", "Haar", "Vaterstetten"],
        "k": ("Mein Sitz ist im Beethovenring 16 in Neukeferloh: Für Betriebe in Grasbrunn und Harthausen bin ich "
              "der IT-Betreuer aus der Nachbarschaft."),
        "answer": ("Als Grundke IT-Service betreue ich in Grasbrunn, Neukeferloh und Harthausen Büros, Werkstätten und "
                   "Praxen mit 5 bis 50 Arbeitsplätzen: Rechner, Server, Microsoft 365 und Datensicherung, ad hoc für "
                   "110 € netto je Stunde oder ab 149 € netto im Monat."),
        "rows_order": ("IT-Betreuung & Wartung", "Microsoft 365 & E-Mail", "Backup & IT-Sicherheit"),
        "voice": "dietz",
        "intro": ("Ich arbeite von Neukeferloh aus, also direkt in der "
                  "Gemeinde Grasbrunn. Wenn bei dir im Büro, in der Werkstatt oder in der Praxis "
                  "die IT streikt, bin ich nicht irgendein Callcenter zwei Bundesländer entfernt, "
                  "sondern dein Nachbar mit über 20 Jahren IT-Erfahrung. Kurze Anfahrt und persönliche "
                  "Betreuung."),
        "near_q": "Bietest du IT-Service direkt vor Ort in Grasbrunn an?",
        "near_a": ("Ja. Mein Sitz ist im Beethovenring 16 in Neukeferloh (Gemeinde Grasbrunn). "
                   "Grasbrunn, Neukeferloh und Harthausen liegen direkt vor meiner Tür, die Anfahrt ist kurz. "
                   "Vieles lässt sich auch per Fernwartung lösen, ohne dass ich kommen muss."),
    },
    {
        "slug": "vaterstetten", "name": "Vaterstetten", "title_name": "Vaterstetten",
        "area": ["Vaterstetten", "Baldham", "Parsdorf", "Grasbrunn"],
        "k": ("Für Büros, Praxen und Handwerksbetriebe in Vaterstetten und Parsdorf bin ich von Neukeferloh aus der "
              "feste Ansprechpartner, der eure IT kennt."),
        "answer": ("Als Grundke IT-Service aus Grasbrunn betreue ich Betriebe in Vaterstetten, Baldham und Parsdorf mit "
                   "5 bis 50 Arbeitsplätzen: Microsoft 365, Netzwerk, Datensicherung und sicherer Zugriff aus dem "
                   "Home-Office, vor Ort oder per Fernwartung."),
        "rows_order": ("Microsoft 365 & E-Mail", "Netzwerk & WLAN", "Backup & IT-Sicherheit"),
        "voice": "verena-k",
        "intro": ("Vaterstetten ist mit Baldham und Parsdorf eine der größten Gemeinden im Münchner "
                  "Osten – viele Pendler, Büros, Praxen und Handwerksbetriebe. Von meinem Sitz in "
                  "Neukeferloh ist die Anfahrt kurz. Du bekommst einen festen "
                  "Ansprechpartner statt einer anonymen Hotline – persönlich, zuverlässig und mit "
                  "über 20 Jahren IT-Erfahrung."),
        "near_q": "Kommst du für IT-Probleme nach Vaterstetten?",
        "near_a": ("Ja. Vaterstetten, Baldham und Parsdorf liegen nicht weit von meinem Sitz in Neukeferloh. "
                   "Termine vor Ort stimmen wir ab, vieles lässt sich auch "
                   "per Fernwartung lösen. Vertragskunden werden bevorzugt behandelt."),
    },
    {
        "slug": "baldham", "name": "Baldham", "title_name": "Baldham",
        "area": ["Baldham", "Vaterstetten", "Zorneding", "Grasbrunn"],
        "k": ("Für kleine Büros, Freiberufler und Selbstständige im Home-Office in Baldham rechne ich ohne "
              "Mindestbetrag im 15-Minuten-Takt ab, per Fernwartung oder nach Absprache vor Ort."),
        "answer": ("Ja. Als Grundke IT-Service aus Grasbrunn betreue ich auch kleine Betriebe in Baldham und "
                   "Vaterstetten, vom Freiberufler bis zum Büro mit 50 Arbeitsplätzen, ad hoc für 110 € netto je "
                   "Stunde oder mit Monatspauschale ab 149 € netto."),
        "voice": "fleischmann",
        "intro": ("Baldham gehört zu Vaterstetten und ist über die S-Bahn bestens angebunden – ein "
                  "Standort mit vielen kleinen Unternehmen, Freiberuflern und Home-Offices. Ich "
                  "kümmere mich persönlich um deine IT: kurze Wege, Abrechnung im 15-Minuten-Takt und ein "
                  "Ansprechpartner, der dein System kennt."),
        "near_q": "Lohnt sich IT-Service für ein kleines Büro in Baldham?",
        "near_a": ("Gerade dann. Für kleine Büros, Freiberufler und Home-Offices in Baldham biete "
                   "ich unkomplizierte Hilfe ohne teure Mindestpauschalen – per Fernwartung oder vor Ort, "
                   "je nachdem was du brauchst."),
    },
    {
        "slug": "zorneding", "name": "Zorneding", "title_name": "Zorneding",
        "area": ["Zorneding", "Pöring", "Baldham", "Vaterstetten"],
        "k": ("Für Handwerksbetriebe und kleine Firmen in Zorneding und Pöring ohne eigene IT-Abteilung bin ich die "
              "IT-Abteilung von außen."),
        "answer": ("Betriebe in Zorneding, Pöring und Wolfesing betreue ich als Grundke IT-Service aus Grasbrunn: "
                   "laufend mit Monatspauschale ab 149 € netto oder einmalig für 110 € netto je Stunde, per "
                   "Fernwartung oder vor Ort."),
        "voice": "dietz",
        "intro": ("Zorneding mit Pöring und Wolfesing liegt an der S-Bahn-Linie S4 im grünen Osten "
                  "des Landkreises Ebersberg. Viele Handwerksbetriebe und kleine Firmen hier haben "
                  "keine eigene IT-Abteilung – genau dafür bin ich da: als externer IT-Betreuer mit "
                  "kurzen Wegen und einem festen Ansprechpartner."),
        "near_q": "Betreust du auch Betriebe in Zorneding und Pöring?",
        "near_a": ("Ja. Zorneding, Pöring und Wolfesing liegen in meinem Einsatzgebiet im Münchner "
                   "Osten. Ob laufende Betreuung oder einmalige Hilfe – du erreichst mich direkt, und die "
                   "Wege sind kurz."),
    },
    {
        "slug": "haar", "name": "Haar", "title_name": "Haar",
        "area": ["Haar", "Grasbrunn", "Putzbrunn", "Vaterstetten"],
        "k": ("Für Büros, Praxen und Werkstätten in Haar, direkt an der Münchner Stadtgrenze, behalte ich Zugänge, "
              "Geräte und Datensicherung im Blick, damit bei einer Störung niemand suchen muss."),
        "answer": ("In Haar betreue ich als Grundke IT-Service aus Grasbrunn die IT von Büros, Praxen und "
                   "Handwerksbetrieben: Netzwerk und WLAN, Microsoft 365, Virenschutz und Datensicherung, laufend "
                   "mit Monatspauschale oder bei Bedarf im 15-Minuten-Takt."),
        "rows_order": ("Netzwerk & WLAN", "Microsoft 365 & E-Mail", "Backup & IT-Sicherheit"),
        "voice": "polednik",
        "intro": ("Haar grenzt direkt an München, und hier arbeiten ganz unterschiedliche Betriebe, "
                  "vom Büro über die Praxis bis zum Handwerksbetrieb. Von Neukeferloh aus ist "
                  "die Anfahrt nach Haar kurz, und ich kümmere mich persönlich um deine komplette IT."),
        "near_q": "Wie schnell bist du bei einem IT-Notfall in Haar?",
        "near_a": ("Haar ist nicht weit von meinem Sitz in Neukeferloh entfernt. Viele Störungen lassen sich "
                   "per Fernwartung lösen; ist ein Einsatz vor Ort nötig, ist die Anfahrt kurz. Eine feste "
                   "Reaktionszeit sage ich nicht zu, Vertragskunden werden bevorzugt behandelt."),
    },
    {
        "slug": "putzbrunn", "name": "Putzbrunn", "title_name": "Putzbrunn",
        "area": ["Putzbrunn", "Solalinden", "Hohenbrunn", "Grasbrunn"],
        "k": ("Für Betriebe im Gewerbegebiet Putzbrunn und in Solalinden bin ich ein Ansprechpartner, der die Arbeit "
              "selbst macht, statt Tickets zu verteilen."),
        "answer": ("Betriebe in Putzbrunn und Solalinden betreue ich als Grundke IT-Service aus Grasbrunn: "
                   "IT-Betreuung, Microsoft 365, Netzwerk, Datensicherung und IT-Sicherheit zum einheitlichen "
                   "Stundensatz von 110 € netto im 15-Minuten-Takt oder als Monatspauschale ab 149 € netto."),
        "rows_order": ("IT-Betreuung & Wartung", "Microsoft 365 & E-Mail", "Netzwerk & WLAN", "Backup & IT-Sicherheit"),
        "voice": "verena-k",
        "intro": ("Putzbrunn mit Solalinden hat ein lebhaftes Gewerbegebiet mit vielen KMU und "
                  "Handwerksbetrieben. Ich biete hier persönliche IT-Betreuung mit einem festen "
                  "Ansprechpartner – zu einem einheitlichen Stundensatz, abgerechnet im "
                  "15-Minuten-Takt und ohne versteckte Kosten."),
        "near_q": "Gibt es in Putzbrunn nicht schon genug IT-Dienstleister?",
        "near_a": ("Einige. Bei mir hast du einen einzigen Ansprechpartner, der die Arbeit selbst macht. "
                   "Du bekommst einen festen Ansprechpartner statt Ticketsystem, faire Abrechnung im "
                   "15-Minuten-Takt und kurze Wege nach Putzbrunn und Solalinden."),
    },
]

# Gemeinsame Leistungs-Zeilen fuer Ortsseiten (Titel, Text, Symbol)
PLACE_CARDS = [
    ("IT-Betreuung & Wartung", "Laufende Betreuung deiner Rechner, Server und Netzwerke – als fester Ansprechpartner.", "ico-tools"),
    ("Microsoft 365 & E-Mail", "Einrichtung, Migration und Betreuung von Outlook, Teams, SharePoint & Co.", "ico-mail"),
    ("Netzwerk & WLAN", "Stabiles WLAN und sichere Netzwerke mit professioneller UniFi-Technik.", "ico-wifi"),
    ("Backup & IT-Sicherheit", "Datensicherung nach 3-2-1-Strategie, Virenschutz und Schutz vor Ransomware.", "ico-shield"),
]
# Beleg im Kopf mit dem Stundensatz, gleicher Wortlaut ueberall: als proof2 auf Ortsseiten, it-notdienst und
# Netzwerk, als proof3 hinter dem eigenen Beleg auf Microsoft 365, IT-Sicherheit und Lizenzen (Task 6,
# Fix-Runden 1/2). Der fruehere Vertrauenskasten der Ortsseiten entfaellt (Fakten in Beleg und Abschluss).
PROOF_ADHOC = ("ico-clock", "Ad hoc 110 € netto/Std. im 15-Minuten-Takt")
PLACE_NEAR_H2 = "Auch in deiner Nähe im Einsatz"


def place_rows(p):
    """Leistungszeilen eines Orts: zuerst die Titel aus rows_order (Reihenfolge, in der der Antwortsatz des
    Orts die Leistungen nennt), danach die uebrigen in der Reihenfolge von PLACE_CARDS. Text und Symbol
    bleiben gleich; ohne rows_order gilt die Grundreihenfolge."""
    by_title = {c[0]: c for c in PLACE_CARDS}
    first = list(p.get("rows_order", ()))
    unknown = [t for t in first if t not in by_title]
    if unknown:
        raise SystemExit("place_rows: unbekannte Zeile(n) " + ", ".join(unknown) + " bei " + p["slug"])
    return [by_title[t] for t in first] + [c for c in PLACE_CARDS if c[0] not in first]


def place_faqs(p):
    return [
        (p["near_q"], p["near_a"]),
        ("Für wen ist der IT-Service in {n} gedacht?".format(n=p["name"]),
         "Für kleine und mittlere Unternehmen, Handwerksbetriebe, Praxen, Kanzleien und Büros mit "
         "etwa 5 bis 50 Arbeitsplätzen, die einen festen persönlichen Ansprechpartner statt einer "
         "anonymen Hotline möchten."),
        ("Was kostet IT-Service in {n}?".format(n=p["name"]),
         "Einzeleinsätze rechne ich transparent im 15-Minuten-Takt ab. Für laufende Betreuung gibt "
         "es planbare Monatspakete, in denen Vertragskunden bevorzugt behandelt werden."),
        ("Wie schnell bekomme ich Hilfe?",
         "Feste Reaktionszeiten sage ich nicht zu; Vertragskunden werden bevorzugt behandelt. Viele "
         "Störungen lassen sich per Fernwartung lösen, sobald wir telefoniert haben, und für Termine vor "
         "Ort sind die Wege im Münchner Osten kurz."),
    ]


def render_place(p, places, services):
    """Ortsseite in der Generator-Huelle (seit 10.10.2026): eigener <head> und LocalBusiness-Schema wie
    bisher, Inhalt ueber render_shell. Abschnitte: Leistungen (Einstieg, Zeilen), Stimme und Nachbarorte
    nebeneinander, FAQ (near_q/near_a + drei gemeinsame Fragen), Abschluss."""
    slug = "it-service-" + p["slug"]
    title = "IT-Service {tn} | Andreas Grundke IT-Service".format(tn=p["title_name"])
    # Description: „schnelle Hilfe“ durch den freigegebenen Ersatz (Textblatt, Frage 5; seo-ausnahmen.json)
    desc = ("IT-Service für {tn}: persönlicher IT-Betreuer vor Ort für KMU, Handwerk & Büros. "
            "Microsoft 365, Netzwerk, Backup, IT-Sicherheit. Kurze Wege, ein fester Ansprechpartner.").format(tn=p["title_name"])
    og_title = "IT-Service {tn} – Andreas Grundke IT-Service".format(tn=p["title_name"])
    og_desc = "Persönlicher IT-Service vor Ort in {tn}. Für KMU, Handwerk & Büros im Raum München Ost.".format(tn=p["title_name"])
    faqs = place_faqs(p)

    h = head(title, desc, slug, og_title, og_desc, "IT-Service {n} – Andreas Grundke IT-Service".format(n=p["name"]))

    lb = {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "ProfessionalService"],
        "name": "Andreas Grundke IT-Service",
        "alternateName": "Grundke IT-Service",
        "description": ("Persönlicher IT-Service für {tn}: IT-Betreuung, Microsoft 365, Netzwerk, "
                        "Backup und IT-Sicherheit für KMU, Handwerk und Büros.").format(tn=p["title_name"]),
        "url": DOMAIN + "/" + slug + "/",
        "telephone": "+49-178-2584438",
        "email": "info@grundke-it.de",
        "address": {"@type": "PostalAddress", "streetAddress": "Beethovenring 16",
                    "addressLocality": "Grasbrunn", "postalCode": "85630",
                    "addressRegion": "Bayern", "addressCountry": "DE"},
        "areaServed": [{"@type": "City", "name": a} for a in p["area"]],
        "geo": {"@type": "GeoCoordinates", "latitude": 48.0944, "longitude": 11.7657},
        "priceRange": "€€",
        "founder": {"@id": PERSON_ID},
    }
    schema = [breadcrumb("IT-Service " + p["name"], slug), lb, faq_schema(faqs),
              webpage_schema(title, desc, slug, mod=PLACE_DATE)]

    # Nachbarorte als Chips (der eigene Ort markiert, die anderen verlinkt), eigener Abschnitt
    chips = ['<span class="here">{n}</span>'.format(n=esc(p["title_name"]))]
    for o in places:
        if o["slug"] != p["slug"]:
            chips.append('<a href="/it-service-{s}/">{n}</a>'.format(s=o["slug"], n=esc(o["name"])))
    near = (PLACE_NEAR_H2,
            prose("<p>Von Neukeferloh aus betreue ich den gesamten Münchner Osten im Umkreis von rund 25&nbsp;km:</p>")
            + '\n    <div class="chips">\n      ' + "\n      ".join(chips) + '\n    </div>')
    name = esc(p["name"])
    s = {
        "slug": slug, "nav": "IT-Service " + p["name"], "h1": "IT-Service in " + esc(p["title_name"]),
        "h1_nowrap": "IT-Service", "k": p["k"], "answer": p["answer"], "proof2": PROOF_ADHOC,
        "intro": p["intro"], "cards_h2": "IT-Leistungen für " + name, "cards": place_rows(p),
        "voices": [p["voice"]], "tail_blocks": [near],
        "row": ("Was andere über mich sagen", PLACE_NEAR_H2),
        "faqs": faqs, "faq_h2": "Häufige Fragen zum IT-Service in " + name,
        "modified_disp": PLACE_DATE_DISP,
        "cta2_href": "/managed-it-service/", "cta2_text": "Mehr zur laufenden IT-Betreuung",
    }
    return slug, render_shell(s, places, services, (h, schema))


# --------------------------------------------------------------------------- #
#  Daten: Leistungen                                                           #
# --------------------------------------------------------------------------- #

# Der kostenlose KI-Potenzialcheck als eigener Service-Knoten. Steht auf dem Hub und
# macht das Einstiegsangebot fuer Suchmaschinen und KI-Antworten sichtbar (price 0).
POTENZIALCHECK_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Service",
    "@id": DOMAIN + "/ki-fuer-kmu/#potenzialcheck",
    "name": "KI-Potenzialcheck",
    "serviceType": "Kostenlose Erstanalyse zum KI-Einsatz im Unternehmen",
    "description": ("60 bis 90 Minuten im Betrieb oder per Videogespräch: Die Abläufe werden "
                    "durchgegangen und schriftlich ausgewertet – was sich automatisieren lässt, "
                    "welcher Aufwand dahintersteckt, was es einspart und was rechtlich zu "
                    "beachten ist. Kostenlos und unverbindlich."),
    "provider": {"@id": BUSINESS_ID},
    "areaServed": [{"@type": "City", "name": n} for n in
                   ["Grasbrunn", "Vaterstetten", "Haar", "Ottobrunn", "München"]],
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR",
               "availability": "https://schema.org/InStock",
               "description": "Kostenlos und unverbindlich, das schriftliche Ergebnis bleibt beim Kunden."},
}

# KI_STYLE und NEW_STYLE (bis Task 7 per "extra_style" im <style> der KI-, Software-, Websites- und
# Ratgeberseiten) stehen seit Release B in assets/css/style.css: .ki-case, .ki-check, .ki-note, .ki-tbl,
# .lp-steps, .lp-checklist, .lp-dont, .lp-answer, .lp-content > h3, .lp-paths (Spec AK1).
KI_START_TEXT = (
    '<p>Das Paket KI-Start kostet je nach Größe des Betriebs ab ' + eur(PRICES["ki_start"]) + ' netto. '
    'Microsoft 365 und Copilot bekommst du auf Wunsch über mich, ChatGPT- und Claude-Teamkonten schließt ihr '
    'direkt beim Anbieter ab, ich richte sie ein und verwalte sie. Dazu auf Wunsch jedes Jahr eine Auffrischung '
    'der Schulung. Mehr auf der Seite <a href="/lizenzen/">Lizenzen</a>.</p>'
    if SHOW_FROM_PRICES else
    '<p>Microsoft 365 und Copilot bekommst du auf Wunsch über mich, ChatGPT- und Claude-Teamkonten schließt ihr '
    'direkt beim Anbieter ab, ich richte sie ein und verwalte sie. Dazu auf Wunsch jedes Jahr eine Auffrischung '
    'der Schulung. Mehr auf der Seite <a href="/lizenzen/">Lizenzen</a>.</p>')


def offer_from(name, min_price, desc, monthly=False, approx=False):
    """Offer mit Mindestpreis ('ab ...'), netto. Monatspreise tragen die Einheit Monat (MON).
    approx=True: Richtwert ('ca. ...'), der nach Aufwand auch darunter liegen kann -> price statt minPrice."""
    spec = {"@type": "UnitPriceSpecification" if monthly else "PriceSpecification",
            "price" if approx else "minPrice": "{:.2f}".format(min_price), "priceCurrency": "EUR",
            "valueAddedTaxIncluded": False}
    if monthly:
        spec.update({"unitCode": "MON", "unitText": "Monat"})
    return {"@type": "Offer", "name": name, "description": desc, "priceSpecification": spec}


EINMALIG = "einmalig, zzgl. MwSt."

TRUST_DEFAULT = ("<strong>Einheitlicher Stundensatz von 110 € netto, Abrechnung im 15-Minuten-Takt, keine "
                 "versteckten Kosten.</strong> Kein klassischer Kundendienst, sondern ein fester persönlicher "
                 "Ansprechpartner mit über 20 Jahren IT-Erfahrung – im Raum München Ost, datenschutzgerecht und auf "
                 "Wunsch self-hosted.")
# Fuer Projekte zum Festpreis (Software, Websites, E-Rechnung): Festpreis vorne, Stundensatz nur
# fuer Einsaetze ausserhalb davon.
# Websites (Andreas 09.10.2026): Preis nach Aufwand, Betrieb nur auf Wunsch
TRUST_WEBSITE = ("<strong>Preis nach Aufwand, verbindlich im Angebot.</strong> Was eure Website kostet, klären "
                 "wir in einem unverbindlichen Telefonat, danach bekommst du ein schriftliches Angebot. Hosting und "
                 "Pflege übernehme ich auf Wunsch, sonst ziehe ich die fertige Seite zu einem Hoster eurer Wahl um. "
                 "Was außerhalb des Angebots anfällt, kostet 110 € netto je Stunde im 15-Minuten-Takt.")
TRUST_FESTPREIS = ("<strong>Festpreis für das Projekt, fester Monatsbetrag für Betrieb und Pflege.</strong> "
                   "Was außerhalb davon anfällt, kostet 110 € netto je Stunde im 15-Minuten-Takt. Du sprichst "
                   "von der ersten Frage bis zum laufenden Betrieb mit mir, Andreas Grundke.")

# Schulung (Task 8, bis 10.10.2026 Handseite): Course-Knoten unveraendert aus dem JSON-LD der Handseite, inklusive
# availability PreOrder am Portal-Angebot; Mail-Links der drei Preiskarten zeichengleich (Betreff und Text wie bisher).
SCHULUNG_COURSE = {
    "@context": "https://schema.org",
    "@type": "Course",
    "name": "IT-Sicherheitsschulung für Mitarbeiter (KMU)",
    "description": ("Praxisnahe IT-Sicherheits- und Datenschutz-Awareness-Schulung für kleine und mittlere Unternehmen: "
                    "Phishing erkennen, sichere Passwörter, sicherer Umgang mit KI-Werkzeugen, richtiges Verhalten im "
                    "Arbeitsalltag. Live per Microsoft Teams oder als Online-Portal mit Quiz und PDF-Zertifikat."),
    "provider": {
        "@type": "Organization",
        "name": "Andreas Grundke IT-Service",
        "alternateName": "Grundke IT-Service",
        "url": "https://grundke-it.de",
    },
    "inLanguage": "de-DE",
    "offers": [
        {"@type": "Offer", "name": "Live-Schulung per Microsoft Teams", "price": "135.00", "priceCurrency": "EUR",
         "category": "Pauschale"},
        {"@type": "Offer", "name": "Online-Portal (Grundpauschale/Halbjahr)", "price": "49.00", "priceCurrency": "EUR",
         "category": "Halbjahr", "availability": "https://schema.org/PreOrder"},
    ],
}
_SCHULUNG_MAIL_END = ("%0A%0AMein%20Unternehmen%20%2F%20meine%20Situation%3A%0A%0A%0AAm%20besten%20erreichbar%20bin%20ich"
                      "%20unter%3A%0ATelefon%3A%20%0AE-Mail%3A%20%0A%0AGew%C3%BCnschter%20R%C3%BCckruf-Zeitraum%3A%20%0A%0A"
                      "---%0AMit%20dem%20Absenden%20dieser%20E-Mail%20stimme%20ich%20der%20Verarbeitung%20meiner%20Angaben"
                      "%20gem%C3%A4%C3%9F%20der%20Datenschutzerkl%C3%A4rung%20zu%20(https%3A%2F%2Fgrundke-it.de%2Fdatenschutz%2F).")
MAILTO_SCHULUNG = {
    "live": ("mailto:info@grundke-it.de?subject=Anfrage%20IT-Sicherheitsschulung%20(Live)%20%C3%BCber%20grundke-it.de"
             "&amp;body=Hallo%20Andreas%2C%0A%0Aich%20interessiere%20mich%20f%C3%BCr%20eine%20pers%C3%B6nliche%20"
             "IT-Sicherheitsschulung%20per%20Teams.%0A%0AAnzahl%20Teilnehmer%3A%20%0AGew%C3%BCnschter%20Termin%3A%20"
             + _SCHULUNG_MAIL_END),
    "portal": ("mailto:info@grundke-it.de?subject=Anfrage%20Schulungs-Portal%20%C3%BCber%20grundke-it.de"
               "&amp;body=Hallo%20Andreas%2C%0A%0Aich%20interessiere%20mich%20f%C3%BCr%20den%20Zugang%20zum%20"
               "Online-Schulungsportal.%0A%0AAnzahl%20Mitarbeiter%3A%20" + _SCHULUNG_MAIL_END),
    "kombi": ("mailto:info@grundke-it.de?subject=Anfrage%20Kombi-Schulungspaket%20%C3%BCber%20grundke-it.de"
              "&amp;body=Hallo%20Andreas%2C%0A%0Aich%20interessiere%20mich%20f%C3%BCr%20das%20Kombi-Paket%20"
              "(Live-Schulung%20%2B%20Portal-Zugang).%0A%0AAnzahl%20Mitarbeiter%3A%20%0AGew%C3%BCnschter%20Termin%20"
              "f%C3%BCr%20Live-Schulung%3A%20" + _SCHULUNG_MAIL_END),
}


SERVICES = [
    {
        "slug": "managed-it-service", "nav": "Managed IT-Service",
        "title": "Managed IT-Service für KMU | München Ost – Andreas Grundke IT-Service",
        "h1": "Managed IT-Service für kleine &amp; mittlere Unternehmen",
        "service_type": "Managed IT-Service",
        "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "desc": ("Managed IT-Service für kleine & mittlere Unternehmen im Raum München Ost: laufende "
                 "IT-Betreuung, bevorzugter Support, ein persönlicher Ansprechpartner. Planbare "
                 "Monatspakete statt teurer Ausfälle."),
        # Kopf der Huelle (Textblatt §1-3, freigegeben 10.10.2026): K4, Antwortsatz, Beispiel-Chat, Stimmen
        "k": "Ich behalte je nach Paket Updates, Datensicherung und Virenschutz im Blick, damit seltener etwas ausfällt.",
        "answer": ("Managed IT-Service bei Grundke IT-Service in Grasbrunn heißt: Ich betreue die IT eures Betriebs "
                   "im Münchner Osten laufend zu einer planbaren Monatspauschale ab 149 € netto, mit Wartung, "
                   "bevorzugtem Support und Betreuung von Microsoft 365 und Datensicherung, monatlich kündbar."),
        "chat": [
            ("andreas", "Kurze Info: Die letzte Datensicherung ist fehlgeschlagen, eine Platte im NAS meldet Fehler."),
            ("kunde", "Muss ich etwas tun?"),
            ("andreas", "Nein. Die Ersatzplatte ist bestellt, den Einbau stimme ich mit dir ab. Bis dahin läuft die Kopie außer Haus weiter."),
        ],
        "voices": ["polednik"],
        # Darstellung in der Huelle (Fix-Runde 1, 10.10.2026)
        "h1_nowrap": "Managed IT-Service",
        "proof2": ("ico-check", "Monatspauschale ab 149 € netto"),
        "price_line": ("Ad hoc", "110 € netto je Stunde im 15-Minuten-Takt, zzgl. MwSt."),
        "intro": ("Die meisten kleinen Unternehmen rufen erst an, wenn die IT schon steht – und dann "
                  "wird es teuer. <strong>Managed IT-Service dreht das um:</strong> Ich kümmere mich "
                  "laufend um eure Rechner, Server, E-Mails und Sicherheit, bevor etwas ausfällt. "
                  "Du zahlst einen festen, planbaren Monatsbetrag statt unkalkulierbarer "
                  "Notfall-Rechnungen – und hast einen <strong>Single Point of Contact</strong> für "
                  "alles rund um IT. Wechselst du gerade von einem anderen Dienstleister, steht der "
                  "Ablauf auf der Seite <a href=\"/it-betreuer-wechseln/\">IT-Betreuer wechseln</a>."),
        "raw_intro": True,
        "cards": [
            ("Proaktive Wartung", "Updates, Monitoring und Pflege eurer Systeme – bevor Probleme entstehen.", "ico-tools"),
            ("Microsoft 365", "Postfächer, Teams, Lizenzen und Sicherheit zentral verwaltet.", "ico-mail"),
            ("Backup & Wiederherstellung", "Automatische Datensicherung nach 3-2-1 – inklusive Test der Rücksicherung.", "ico-cloud"),
            ("IT-Sicherheit", "Virenschutz, Firewall, VPN und Schutz vor Ransomware & Phishing.", "ico-shield"),
            ("Bevorzugter Support", "Vertragskunden kommen vor Ad-hoc-Anfragen dran, Premium-Kunden zuerst.", "ico-user-check"),
            ("Beratung & Einkauf", "Hardware-Empfehlungen und Beschaffung ohne Aufschlag-Spielchen.", "ico-handshake"),
            # Textblatt L9b: stand bis 10.10.2026 im Abschnitt "Leistungen" der Startseite
            ("Umstieg und Erneuerung", "Umstieg auf Windows 11, Microsoft 365 oder neue Server, Ablösung veralteter Router und Firewalls und eine IT-Dokumentation für den Notfall.", "ico-monitor"),
        ],
        "prices": [
            ("Starter", "149 €", "Laufende Betreuung für kleine Teams & Einzelplätze.", False),
            ("Business", "249 €", "Erweiterte Betreuung mit Patchmanagement.", True),
            ("Premium", "449 €", "Rundum-Betreuung mit höchster Priorität, Virenschutz und Monatsreport.", False),
        ],
        "offers": [
            ("Starter", "149.00", "Laufende IT-Betreuung für kleine Teams."),
            ("Business", "249.00", "Erweiterte Betreuung mit Patchmanagement."),
            ("Premium", "449.00", "Rundum-Betreuung mit höchster Priorität."),
        ],
        "faqs": [
            ("Was ist Managed IT-Service?",
             "Managed IT-Service bedeutet, dass ich mich laufend um eure gesamte IT kümmere – "
             "Wartung, Updates, Microsoft 365, Backup und Sicherheit – zu einem festen monatlichen "
             "Preis. Statt erst beim Ausfall zu reagieren, halte ich eure Systeme proaktiv am Laufen."),
            ("Für welche Unternehmensgröße lohnt sich das?",
             "Besonders für Betriebe mit etwa 5 bis 50 Arbeitsplätzen, die keine eigene IT-Abteilung "
             "haben, aber auf funktionierende IT angewiesen sind – Handwerk, Büros, Praxen, Kanzleien "
             "und Gastronomie."),
            ("Was kostet Managed IT-Service?",
             "Es gibt feste Monatspakete ab 149 € (Starter), 249 € (Business) und 449 € (Premium), jeweils netto. "
             "Welches Paket passt, hängt von der Anzahl der Arbeitsplätze und dem gewünschten Umfang "
             "ab – das klären wir in einem kurzen kostenlosen Erstgespräch."),
            ("Bin ich an lange Verträge gebunden?",
             "Nein. Die Monatspakete sind monatlich kündbar. "
             "Du behältst die Kontrolle und einen festen Ansprechpartner – kein Ticketsystem, keine "
             "Warteschleife."),
        ],
    },
    {
        "slug": "microsoft-365-betreuung", "nav": "Microsoft 365 Betreuung",
        "title": "Microsoft 365 Betreuung für KMU | München Ost – Andreas Grundke IT-Service",
        "h1": "Microsoft 365 Betreuung für Unternehmen",
        "service_type": "Microsoft 365 Betreuung",
        "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "desc": ("Microsoft 365 für KMU im Raum München Ost: Einrichtung, Migration und laufende "
                 "Betreuung von Exchange Online, Teams, SharePoint & OneDrive – inklusive Sicherheit "
                 "und DSGVO-konformer Datensicherung."),
        # Kopf der Huelle (Textblatt §1/§3, Task 6): K4, Antwortsatz, Stimme; Darstellung: zweiter Beleg
        "k": ("Kommt jemand ins Team oder geht, lege ich Konto, Postfach und Rechte an oder räume sie wieder weg."),
        "answer": ("Microsoft 365 betreue ich als Grundke IT-Service aus Grasbrunn für Betriebe im Münchner Osten: "
                   "Einrichtung und Umzug alter Postfächer nach Aufwand, laufende Betreuung mit Zwei-Faktor-Anmeldung "
                   "und zusätzlicher Datensicherung im Monatspaket ab 149 € netto."),
        "voices": ["fleischmann"],
        "h1_nowrap": "Microsoft 365",
        "proof2": ("ico-check", "Betreuung im Monatspaket ab 149 € netto"),
        "proof3": PROOF_ADHOC,
        "intro": ("Microsoft 365 ist schnell gebucht – aber sauber eingerichtet, abgesichert und "
                  "DSGVO-konform betrieben ist es eine andere Sache. Ich übernehme die Ersteinrichtung, "
                  "die Migration von alten Postfächern oder Servern und die laufende Betreuung deiner "
                  "M365-Umgebung. So nutzt du Outlook, Teams und SharePoint zuverlässig, ohne dich um "
                  "Lizenzen, Sicherheit oder Updates kümmern zu müssen. Die Lizenzen bekommst du auf "
                  "Wunsch über mich, mehr auf der Seite <a href=\"/lizenzen/\">Lizenzen</a>."),
        "raw_intro": True,
        "cards": [
            ("Einrichtung & Migration", "Umzug von altem Server oder Postfach nach Microsoft 365 – ohne Datenverlust.", "ico-cloud"),
            ("Exchange Online & E-Mail", "Professionelle E-Mail mit eigener Domain, Signaturen und Spam-Schutz.", "ico-mail"),
            ("Teams & SharePoint", "Zusammenarbeit, Dateifreigaben und Strukturen, die dein Team versteht.", "ico-file-text"),
            ("Sicherheit & Backup", "MFA, Rechte-Konzept und externes M365-Backup – denn Microsoft sichert deine Daten nicht vollständig.", "ico-shield"),
        ],
        "faqs": [
            ("Was kostet die Microsoft 365 Betreuung?",
             "Die Einrichtung rechne ich transparent nach Aufwand im 15-Minuten-Takt ab; die laufende "
             "Betreuung ist Teil meiner Managed-IT-Pakete ab 149 € netto im Monat. Die Microsoft-Lizenzen "
             "selbst kommen je nach Plan hinzu."),
            ("Kannst du mein altes Postfach zu Microsoft 365 migrieren?",
             "Ja. Ich migriere E-Mails, Kontakte und Kalender von einem alten Exchange-Server, von "
             "IMAP-Postfächern oder anderen Anbietern nach Microsoft 365 – geplant und ohne, dass "
             "Daten verloren gehen."),
            ("Sind meine Daten in Microsoft 365 automatisch gesichert?",
             "Nein – das ist ein verbreiteter Irrtum. Microsoft sorgt für die Verfügbarkeit, aber "
             "nicht für ein vollständiges Backup gegen versehentliches Löschen oder Ransomware. "
             "Deshalb richte ich eine zusätzliche, DSGVO-konforme Datensicherung ein."),
            ("Ist Microsoft 365 DSGVO-konform nutzbar?",
             "Mit der richtigen Konfiguration ja. Ich richte Rechte, Mehr-Faktor-Anmeldung und "
             "Datenspeicherorte so ein, dass der Betrieb den Anforderungen der DSGVO entspricht."),
        ],
    },
    {
        "slug": "it-sicherheit-backup", "nav": "IT-Sicherheit & Backup",
        "title": "IT-Sicherheit & Backup für KMU | München Ost – Andreas Grundke IT-Service",
        "h1": "IT-Sicherheit &amp; Backup für Unternehmen",
        "service_type": "IT-Sicherheit und Datensicherung",
        "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "desc": ("IT-Sicherheit & Backup für KMU im Raum München Ost: Schutz vor Ransomware und "
                 "Datenverlust mit 3-2-1-Backup, Virenschutz, Firewall und Mitarbeiter-Awareness."),
        # Kopf der Huelle (Textblatt §1/§3, Task 6)
        "k": ("Ich sichere eure Daten mit einer Kopie außer Haus und prüfe regelmäßig, ob sie sich zurückspielen "
              "lassen."),
        "answer": ("IT-Sicherheit heißt bei Grundke IT-Service in Grasbrunn für Betriebe im Münchner Osten: "
                   "Datensicherung nach 3-2-1 mit Kopie außer Haus, zentral verwalteter Virenschutz, Firewall und ein "
                   "Team, das Phishing erkennt. Ich richte das ein und betreue es weiter."),
        "voices": ["fleischmann"],
        "h1_nowrap": "IT-Sicherheit",
        "proof2": ("ico-cloud", "Datensicherung nach 3-2-1 mit Kopie außer Haus"),
        "proof3": PROOF_ADHOC,
        "intro": ("Ein einziger verschlüsselter Server oder ein gelöschtes Verzeichnis kann ein "
                  "kleines Unternehmen tagelang lahmlegen. Ich sorge dafür, dass es gar nicht erst so "
                  "weit kommt – und dass du im Ernstfall deine Daten zurückbekommst. Dazu gehören eine "
                  "saubere Backup-Strategie nach dem 3-2-1-Prinzip, aktueller Virenschutz, eine "
                  "vernünftige Firewall und Mitarbeiter, die Phishing erkennen."),
        "raw_intro": True,
        "cards": [
            ("Backup nach 3-2-1", "Drei Kopien, zwei Medien, eine außer Haus – inklusive Test der Rücksicherung.", "ico-cloud"),
            ("Virenschutz", "Zentral verwalteter Schutz (z. B. ESET) auf allen Geräten.", "ico-shield"),
            ("Firewall & VPN", "Abgesicherter Internetzugang und verschlüsselter Zugriff fürs Home-Office.", "ico-key"),
            ("Awareness-Schulung", "Deine Mitarbeiter lernen, Phishing und Betrug zu erkennen.", "ico-user-check"),
        ],
        "faqs": [
            ("Reicht OneDrive oder eine externe Festplatte als Backup?",
             "Nein. OneDrive synchronisiert nur – wird eine Datei verschlüsselt oder gelöscht, ist "
             "das auch in der Cloud so. Eine einzelne Festplatte fällt bei Diebstahl, Brand oder "
             "Ransomware mit aus. Erst ein 3-2-1-Konzept mit einer Kopie außer Haus schützt wirklich."),
            ("Was mache ich bei einem Ransomware-Befall?",
             "Sofort Gerät vom Netz trennen und mich anrufen. Mit einem funktionierenden Backup stelle "
             "ich deine Daten wieder her, statt Lösegeld zu zahlen – deshalb ist die Vorbereitung so "
             "wichtig."),
            ("Wie oft werden meine Daten gesichert?",
             "In der Regel mehrmals täglich, je nach Datenmenge und Wichtigkeit. Wichtig ist nicht nur "
             "das Sichern, sondern der regelmäßige Test, ob sich die Daten auch wirklich "
             "zurückspielen lassen."),
            ("Was kostet IT-Sicherheit für ein kleines Unternehmen?",
             "Deutlich weniger als ein einziger ernster Ausfall. Backup, Virenschutz und Firewall sind "
             "Teil meiner Managed-IT-Pakete ab 149 € netto im Monat oder als Einzelprojekt zum festen "
             "Stundensatz umsetzbar."),
        ],
    },
    {
        "slug": "netzwerk-wlan-firewall", "nav": "Netzwerk, WLAN & Firewall",
        "title": "Netzwerk, WLAN & Firewall für KMU | München Ost – Andreas Grundke IT-Service",
        "h1": "Netzwerk, WLAN &amp; Firewall für Unternehmen",
        "service_type": "Netzwerk, WLAN und Firewall",
        "desc": ("Netzwerk, WLAN & Firewall für KMU im Raum München Ost: stabiles WLAN, sichere "
                 "Netzwerke und VPN mit professioneller UniFi-Technik – geplant, eingerichtet und betreut."),
        # Kopf der Huelle (Textblatt §1/§3, Task 6)
        "k": "Ich plane das WLAN für euer Gebäude und trenne Gäste, Kasse und Betrieb in eigene Netze.",
        "answer": ("Als Grundke IT-Service aus Grasbrunn plane ich Netzwerk, WLAN und Firewall für Betriebe im "
                   "Münchner Osten, richte sie ein und betreue sie: UniFi-Technik, getrennte Netze für Gäste und "
                   "Betrieb und VPN fürs Home-Office."),
        "proof2": PROOF_ADHOC,
        "intro": ("Langsames WLAN, ständige Abbrüche oder ein Netzwerk, das mit dem Betrieb gewachsen "
                  "und unübersichtlich geworden ist – das kostet täglich Zeit und Nerven. Ich plane, "
                  "richte ein und betreue Netzwerke mit professioneller UniFi-Technik: stabiles WLAN "
                  "auf jeder Fläche, sauber getrennte Netze (VLAN) für Gäste und Betrieb sowie sichere "
                  "Zugänge per Firewall und VPN."),
        "raw_intro": True,
        "cards": [
            ("Netzwerk & VLAN", "Strukturierte, sicher getrennte Netze für Betrieb, Gäste und Kasse.", "ico-network"),
            ("WLAN (UniFi)", "Lückenloses, schnelles WLAN auf jeder Etage und im Außenbereich.", "ico-wifi"),
            ("Firewall & VPN", "Abgesicherter Internetzugang und verschlüsselter Zugriff von unterwegs.", "ico-shield"),
            ("Monitoring", "Ich sehe Störungen oft, bevor du sie bemerkst – und reagiere proaktiv.", "ico-monitor"),
        ],
        "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        # Kundenstimme Apartments Bauer (Google, 26.09.2026) seit Task 6 aus REVIEWS ueber voices_html, wortgetreu
        # wie auf der Startseite; Ueberschrift des bisherigen Abschnitts bleibt.
        "voices": ["bauer"],
        "voices_h2": "Aus der Praxis: WLAN in einem älteren Gebäude",
        "faqs": [
            ("Warum UniFi und nicht der Router vom Provider?",
             "Provider-Router sind für den Hausgebrauch gedacht. Mit professioneller UniFi-Technik "
             "bekommst du stabiles WLAN auf der ganzen Fläche, getrennte Netze für Gäste und Betrieb "
             "sowie zentrale Verwaltung und Überwachung."),
            ("Bekomme ich WLAN im ganzen Gebäude?",
             "Ja. Ich plane die Zahl und Platzierung der Access Points so, dass du auf jeder Etage und "
             "auf Wunsch auch im Außenbereich stabiles WLAN hast – ohne Funklöcher."),
            ("Können meine Mitarbeiter sicher von zu Hause arbeiten?",
             "Ja, über ein verschlüsseltes VPN (z. B. WireGuard). Der Zugriff aufs Firmennetz ist "
             "damit genauso sicher wie im Büro."),
            ("Was kostet die Einrichtung eines Firmennetzwerks?",
             "Das hängt von Größe und Anforderungen ab. Ich erstelle dir nach einem kurzen Termin ein "
             "transparentes Angebot; abgerechnet wird zum einheitlichen Stundensatz im "
             "15-Minuten-Takt, Hardware zum fairen Einkaufspreis."),
        ],
    },
    {
        "slug": "it-notdienst", "nav": "IT-Notdienst",
        "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "title": "IT-Notdienst für Firmen im Münchner Osten | Grundke IT",
        "h1": "IT-Notdienst für Unternehmen",
        "service_type": "IT-Notdienst",
        "desc": ("IT-Notdienst für Unternehmen im Münchner Osten: Hilfe bei Störungen, Viren und Datenverlust "
                 "per Fernwartung oder vor Ort. Dein ITler geht nicht ran? Ich schon."),
        "k": ("Dein ITler geht nicht ran? Ich schon. Betreue ich euch bereits, kenne ich eure Systeme und schaue "
              "per Fernwartung nach, ohne lange Erklärungen."),
        "answer": ("Im IT-Notdienst helfe ich als Grundke IT-Service aus Grasbrunn Betrieben im Münchner Osten bei "
                   "Störungen per Fernwartung oder vor Ort, ad hoc für 110 € netto je Stunde im 15-Minuten-Takt und "
                   "ohne Zuschlag am Abend oder Wochenende. Eine feste Reaktionszeit sage ich nicht zu."),
        "chat": [
            ("kunde", "Im Büro kommt keiner mehr an die Dateien, der Server reagiert nicht."),
            ("andreas", "Ich habe euren Zugang und schaue per Fernwartung auf Server, Netz und Datensicherung."),
            ("andreas", "Ein Dienst hing nach dem letzten Update. Neu gestartet, die Laufwerke sind wieder da."),
        ],
        "voices": ["polednik", "verena-k"],
        # Darstellung in der Huelle (Fix-Runde 1, 10.10.2026): Preis neben dem Einstieg statt Vertrauenskasten
        "proof2": PROOF_ADHOC,
        "intro_price": ("Ad hoc", "110 €", "Abrechnung im 15-Minuten-Takt.", False, "netto/Std. zzgl. MwSt."),
        "intro": ("Wenn die IT steht, zählt jede Minute. Viele Störungen löse ich per Fernwartung, sobald "
                  "wir telefoniert haben; bei größeren Problemen komme ich vorbei, die Wege im Münchner "
                  "Osten sind kurz. Eine feste Reaktionszeit sage ich nicht zu, Vertragskunden werden "
                  "bevorzugt behandelt. Kein Ticketsystem, keine Warteschleife – du erreichst direkt die "
                  "Person, die das Problem löst. Was du in den ersten Minuten selbst tun kannst, steht im "
                  "Ratgeber <a href=\"/ratgeber/\">Die ersten 15 Minuten</a>."),
        "raw_intro": True,
        "cards": [
            ("Hilfe per Fernwartung", "Über meine eigene Fernwartung verbinde ich mich mit deinem Bildschirm und löse das Problem direkt. Sie läuft verschlüsselt über meinen Server in Deutschland.", "ico-monitor"),
            ("Vor-Ort-Einsatz", "Lässt sich etwas nicht aus der Ferne lösen, komme ich vorbei.", "ico-tools"),
            ("Daten- & Systemrettung", "Hilfe bei Datenverlust, defekten Festplatten und nicht startenden Systemen.", "ico-server-crash"),
            ("Virenbefall & Ransomware", "Bereinigung befallener Systeme und Wiederherstellung aus dem Backup.", "ico-shield"),
        ],
        "faqs": [
            ("Wie schnell bekomme ich im Notfall Hilfe?",
             "Das hängt davon ab, woran ich gerade arbeite. Feste Reaktionszeiten sage ich nicht zu; "
             "Vertragskunden werden bevorzugt behandelt, Premium-Kunden zuerst. Viele Störungen lassen sich "
             "per Fernwartung lösen, ohne dass jemand anfahren muss."),
            ("Was kostet der IT-Notdienst?",
             "Ad hoc 110 Euro netto je Stunde im 15-Minuten-Takt, ohne Zuschlag für Abend oder Wochenende. "
             "Du zahlst nur die tatsächlich benötigte Zeit."),
            ("Wie funktioniert die Fernwartung?",
             "Auf der Seite „Fernwartung starten“ lädst du ein kleines Programm für Windows oder Linux "
             "herunter, die Anleitung führt dich Schritt für Schritt. Am Mac richten wir es beim ersten Mal "
             "zusammen am Telefon ein. Du siehst alles mit, und auf Zuruf entferne ich den Zugang wieder. Die "
             "Verbindung läuft verschlüsselt über meinen eigenen Server in Deutschland."),
            ("Hilfst du auch Privatkunden?",
             "Nein. Mein Angebot richtet sich an Unternehmen, Selbstständige und Freiberufler. "
             "Alle Preise verstehen sich zuzüglich Mehrwertsteuer."),
        ],
    },
    # ----------------------------------------------------------------------- #
    #  KI-Bereich (seit 2026-08-22): Hub + drei Vertiefungen.                  #
    #  Zweite Saeule neben dem klassischen IT-Service, eigene Datumsangaben.   #
    # ----------------------------------------------------------------------- #
    {
        "slug": "ki-fuer-kmu", "nav": "KI im Betrieb",
        "title": "KI für KMU – Anwendungen im Betrieb | Grundke IT-Service München Ost",
        "h1": "KI im Betrieb",
        "hero": {
            "accent": "für kleine &amp; mittlere Unternehmen",
            "paths_label": "Die vier Bereiche",
            "paths": [
                ("Abläufe automatisieren", "Schnittstellen, Dokumente auslesen, Berichte ohne Excel-Bastelei.", "/ki-automatisierung/"),
                ("Videoanalyse und Auswertung", "Videoüberwachung mit KI: Fahrzeuge und Kennzeichen erkennen, Vorgänge zählen.", "/ki-videoanalyse/"),
                ("KI sicher einsetzen", "Verträge, Regeln und Schulung, damit KI datenschutzgerecht läuft.", "/ki-dsgvo/"),
                ("Software nach Maß", "Kleine Anwendungen für Abläufe, die heute in Excel oder auf Zetteln laufen.", "/software-nach-mass/"),
            ],
        },
        "service_type": "KI-Beratung und Anwendungsentwicklung für KMU",
        # 10.10.2026 (Task 7): neuer Kopf mit K4 und Antwortsatz -> neues Datum
        "published": KI_PUB_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/ki-automatisierung/", "cta2_text": "Abläufe automatisieren",
        "extra_schema": [POTENZIALCHECK_SCHEMA],
        "desc": ("KI im Betrieb: Abläufe automatisieren, Auswertungen aus vorhandenen Daten, "
                 "datenschutzgerecht umgesetzt. Kostenloser Potenzialcheck im Raum München Ost."),
        # Kopf der Huelle (Textblatt §1, freigegeben 10.10.2026; ohne Stimme, Andreas 10.10.2026): K4, Antwortsatz;
        # Beleg aus dem Potenzialcheck-Kasten der Seite; Vertrauenstext wie bisher (TRUST_DEFAULT) neben dem Einstieg
        "k": ("Ich baue KI dort ein, wo bei euch jede Woche jemand Daten abtippt oder Aufnahmen durchklickt, und "
              "betreue es danach weiter."),
        "answer": ("KI im Betrieb heißt bei Grundke IT-Service in Grasbrunn: Abläufe automatisieren, vorhandene Daten "
                   "auswerten und KI-Werkzeuge datenschutzgerecht einführen, für kleine und mittlere Betriebe im "
                   "Münchner Osten. Der Einstieg ist ein kostenloser Potenzialcheck."),
        "proof2": ("ico-search-check", "Kostenloser KI-Potenzialcheck, Ergebnis schriftlich"),
        "trust": TRUST_DEFAULT,
        "intro": ("Wenn ein Betrieb heute über KI spricht, geht es meist um zwei Dinge: dass sich "
                  "alles ändern wird und dass man vorsichtig sein muss. Beides hilft nicht weiter, "
                  "solange am Montag wieder jemand Rechnungsdaten abtippt oder Kameraaufnahmen "
                  "durchklickt. <strong>Ich baue Anwendungen für genau diese Stellen</strong> und "
                  "betreue sie danach weiter. In meiner eigenen Firma läuft das seit über einem "
                  "halben Jahr täglich: Kundenverwaltung, Monitoring, Auswertungen, Rechnungsläufe. "
                  "Seit einigen Monaten entstehen die ersten Anwendungen bei Kunden. Was ich "
                  "anbiete, benutze ich selbst."),
        "raw_intro": True,
        "cards": [
            ("Abläufe automatisieren", "Wiederkehrende Handarbeit am Rechner: Daten übertragen, Listen erzeugen, Rechnungen bauen, Berichte zusammenstellen.", "ico-tools"),
            ("Auswertungen aus vorhandenen Daten", "Was in Kamera, Kasse, Zeiterfassung oder Warenwirtschaft schon steckt, wird sichtbar gemacht.", "ico-search-check"),
            ("Systeme verbinden", "Zwei Programme, die nicht miteinander reden, koppele ich über ihre Dateiformate oder ihre Schnittstelle.", "ico-network"),
            ("KI-Werkzeuge einführen", "Welches Werkzeug für welche Aufgabe taugt, wie es eingerichtet wird und was die Mitarbeiter darüber wissen müssen.", "ico-monitor"),
            ("Datenschutz vorher klären", "Lokales Modell, EU-Rechenzentrum oder Anbieter mit Auftragsverarbeitungsvertrag. Die Entscheidung fällt vor der Umsetzung.", "ico-shield"),
            ("Betrieb und Pflege", "Eine gebaute Anwendung braucht jemanden, der sie weiter betreut. Ich bleibe der Ansprechpartner.", "ico-user-check"),
        ],
        "extra": """
      <h2>KI soll bei euch niemanden ersetzen</h2>
      <p>Sie soll die Arbeit wegnehmen, die keiner gern macht: Daten von einem Programm ins andere kopieren, Rechnungen abtippen, dieselben Fragen zum zehnten Mal beantworten, Spam aussortieren. Eure Leute haben dann wieder Zeit für Kunden, Aufträge und Ideen, und du als Inhaber für das Geschäft statt für den Papierkram. Ich fange deshalb immer bei den Menschen an, die mit dem Ablauf arbeiten: Was nervt euch jede Woche? Das bauen wir zuerst weg.</p>
      <p>Wer im Betrieb arbeitet, fragt sich bei KI oft, ob der eigene Platz sicher ist. Aus der Praxis: Der Job wird nicht ersetzt, er wird leichter. Wer den Ablauf kennt, weiß am besten, wo es hakt, und genau diese Leute brauche ich, um die Lösung zu bauen.</p>

      <h2>So sieht das im Alltag aus</h2>
      <h3>Doku nach dem Einsatz per Sprache</h3>
      <p>Auf dem Rückweg von der Baustelle sind die Hände voll. Im Firmen-KI-Konto einen neuen Chat öffnen, Kunde und Vorhaben nennen, dann frei erzählen: was gemacht wurde, welches Material, was abgestimmt ist, was noch offen ist und wie lange es gedauert hat. Am Ende fasst die KI zusammen, und der Text geht per Kopieren und Einfügen in Buchhaltung oder Auftragsverwaltung. Voraussetzung ist ein bezahltes Firmenkonto mit Vertrag; unterwegs nur mit dem Handy in der Halterung und per Sprachsteuerung (§ 23 Abs. 1a StVO) oder kurz auf dem Parkplatz.</p>
      <!--more-->
      <h3>Programme reden miteinander</h3>
      <p>Lexware Office und viele Auftrags- und Rechnungsprogramme haben Schnittstellen. Kundendaten, Aufträge, Material und Angebotsentwürfe lassen sich darüber anlegen, abfragen und abgleichen, statt alles in der Oberfläche abzutippen. Mein eigener Betrieb legt Kunden und Angebotsentwürfe auf diesem Weg direkt in Lexware an.</p>
      <h3>Warnungen, die jemand liest</h3>
      <p>Meldungen der Datensicherung, Fehlermails von Geräten, volle Postfächer: Eine KI liest sie, ordnet sie ein und schickt nur das Wichtige an die richtige Person, mit einem Satz, was zu tun ist.</p>
      <p>Dazu kommen Auswertungen und Monatsberichte, Zusammenfassungen langer Mails und Dokumente, Entwürfe für Angebote und Antworten und die Abstimmung von Terminen.</p>
      <!--/more-->

      <h2>Zwei Beispiele aus der Praxis</h2>
      <p>Das erste ist ein typischer Fall für Videoauswertung, das zweite läuft in meinem eigenen Betrieb.</p>

      <!--more-->
      <div class="card-grid">
      <div class="ki-case">
        <span class="ki-case-tag">Videoüberwachung mit KI</span>
        <h3>Eine Hofzufahrt, die sich selbst protokolliert</h3>
        <p>Viele Betriebe haben an der Zufahrt eine Kameraanlage und sehen sich die Aufnahmen erst an, wenn etwas passiert ist. Dabei lassen sich einfache Fragen automatisch beantworten: Wie viele Fahrzeuge kommen pro Woche? Wann ist am meisten los? Stand nachts ein fremdes Fahrzeug auf dem Hof?</p>
        <p>Auf eine vorhandene Anlage wie UniFi Protect setze ich eine Erkennung auf. Fahrzeuge werden erkannt und, wo es dafür einen Zweck gibt, auch ihre Kennzeichen, etwa um bekannte Fahrzeuge von Lieferanten von fremden zu unterscheiden. Jedes Ereignis landet mit Zeitstempel in einer Datenbank, eine Oberfläche zeigt Verläufe und Auffälligkeiten. Die Erkennung läuft auf Hardware im Betrieb, die Aufnahmen verlassen das Haus nicht.</p>
        <p class="ki-result">Kennzeichen sind personenbezogene Daten. Erfasst wird deshalb nur, was für den Zweck nötig ist, mit Hinweisschild und festen Löschfristen, die wir vor dem Start festlegen.</p>
      </div>

      <div class="ki-case">
        <span class="ki-case-tag">Eigenbetrieb · seit über einem halben Jahr</span>
        <h3>Was ich selbst benutze</h3>
        <p>Meine Kundenverwaltung, mein Monitoring, meine Auswertungen und meine Rechnungsläufe laufen über Anwendungen, die ich selbst gebaut habe und täglich benutze. Dazu kommen Werkzeuge, die aus einer konkreten Not entstanden sind: eine Prüfung von Websites auf technische und rechtliche Mängel, ein Scanner für Netzwerkumgebungen, ein Auswertungswerkzeug für die Sichtbarkeit in Suchmaschinen.</p>
        <p class="ki-result">Der Punkt daran ist nicht die Liste. Der Punkt ist, dass ich im Erstgespräch aus eigener Erfahrung sagen kann, was funktioniert, was Zeit frisst und was sich nicht lohnt.</p>
      </div>
      </div>
      <!--/more-->

      <div class="ki-check">
        <h3>Kostenloser KI-Potenzialcheck</h3>
        <p>Der einfachste Einstieg. 60 bis 90 Minuten, bei dir im Betrieb oder per Videogespräch. Wir gehen durch, was bei euch regelmäßig Zeit kostet, und schauen, was davon eine Maschine übernehmen kann.</p>
        <ul>
          <li>Wir sehen uns die Abläufe an, die jeden Monat gleich laufen</li>
          <li>Ich sage dir, was sich automatisieren lässt und was nicht</li>
          <li>Du bekommst es schriftlich, mit Aufwand, Nutzen und den rechtlichen Punkten</li>
          <li>Das Papier gehört dir, auch wenn wir nicht weiterarbeiten</li>
        </ul>
        <div class="card-cta">
          <a href="tel:+491782584438" class="btn-p">Potenzialcheck vereinbaren</a>
          <a href="/kontakt/" class="btn-g">Lieber schreiben</a>
        </div>
      </div>

      <h2>Wann sich das nicht lohnt</h2>
      <p>Nicht jede Aufgabe verdient eine eigene Anwendung. Was dreimal im Jahr vorkommt, ist von Hand billiger als jede Automatisierung, und wenn ein Ablauf sich alle paar Monate ändert, wird die Pflege teurer als der Nutzen. Auch dort, wo es am Ende auf ein Urteil ankommt und nicht auf eine Regel, hat eine Maschine wenig verloren.</p>
      <p>Das sage ich im Erstgespräch, bevor daraus ein Projekt wird. Mir ist ein Kunde lieber, der einmal etwas Sinnvolles bekommt, als einer, der ein halbes Jahr später merkt, dass er es nie gebraucht hat.</p>

""",
        "faqs": [
            ("Was bringt KI einem Betrieb mit 15 Mitarbeitern konkret?",
             "Meistens Zeit an einer Stelle, die niemand gern macht. Typisch sind drei Fälle: Daten, "
             "die aus einem Export von Hand in ein anderes Programm übertragen werden. Auswertungen, "
             "die jemand am Monatsende in Excel zusammenbaut. Und Aufnahmen oder Protokolle, die "
             "niemand durchsieht, weil es zu lange dauert. Das sind Stunden, die jeden Monat anfallen "
             "und sich ohne zusätzliches Personal zurückholen lassen."),
            ("Ist das für einen kleinen Betrieb nicht viel zu teuer?",
             "Du bekommst vor dem Start einen Festpreis. "
             + ("Der Einstieg mit Verträgen, Regeln und Schulung (KI-Start) beginnt bei "
                + "{:,}".format(PRICES["ki_start"]).replace(",", ".") + " Euro netto, eine kleine Anwendung bei "
                + "{:,}".format(PRICES["software_klein"]).replace(",", ".") + " Euro. "
                if SHOW_FROM_PRICES else "")
             + "Ob sich eine Automatisierung rechnet, lässt sich vorher ausrechnen: Wenn eine Aufgabe "
             "monatlich vier Stunden kostet, ist die einzige Frage, nach wie vielen Monaten die Umsetzung "
             "bezahlt ist. Rechnet es sich nicht, sage ich das im Erstgespräch."),
            ("Was passiert mit unseren Daten?",
             "Das wird vor der Umsetzung entschieden, nicht danach. Drei Wege sind üblich: Das Modell "
             "läuft auf eigener Hardware im Betrieb, dann verlassen die Daten das Haus nicht. Es läuft "
             "in einem Rechenzentrum innerhalb der EU. Oder es läuft bei einem Anbieter, mit dem ein "
             "Auftragsverarbeitungsvertrag besteht und der die Daten nicht zum Training seiner Modelle "
             "verwendet. Welcher Weg passt, hängt davon ab, wie sensibel die Daten sind."),
            ("Brauchen wir dafür neue Hardware?",
             "Meistens nicht. Vieles läuft auf einem vorhandenen Server oder einem kleinen Rechner im "
             "Netzwerk. Erst wenn ein Sprachmodell wirklich lokal arbeiten soll, kommt Hardware mit "
             "Grafikkarte ins Spiel. Das ist eine überschaubare Investition, sie muss aber begründet "
             "sein, und ich sage dir vorher, ob sie sich in deinem Fall lohnt."),
            ("Wir nutzen schon ChatGPT. Reicht das nicht?",
             "Für Texte oft ja. Der Unterschied beginnt dort, wo etwas regelmäßig und ohne einen "
             "Menschen davor passieren soll: Daten aus einem System holen, verarbeiten, in ein anderes "
             "schreiben, und das jede Nacht. Dafür braucht es eine gebaute Anwendung. Dazu kommt die "
             "Frage, was Mitarbeiter überhaupt in ein Chatfenster eingeben dürfen. Artikel 4 der "
             "europäischen KI-Verordnung verlangt von jedem Unternehmen, das KI einsetzt, Maßnahmen "
             "zur Förderung der KI-Kompetenz seiner Beschäftigten."),
            ("Wie fange ich an?",
             "Mit dem kostenlosen KI-Potenzialcheck. Wir gehen 60 bis 90 Minuten durch deine Abläufe "
             "und schauen, wo Zeit verloren geht. Danach bekommst du schriftlich, was sich "
             "automatisieren lässt, was es ungefähr kostet und was rechtlich zu beachten ist. Ob du "
             "damit weiterarbeitest, entscheidest du in Ruhe."),
        ],
    },
    {
        "slug": "ki-automatisierung", "nav": "Abläufe automatisieren",
        "title": "KI-Automatisierung: Schnittstellen & Berichte | Grundke IT",
        "h1": "Abläufe automatisieren: Schnittstellen, Dokumente und Berichte",
        "service_type": "Prozessautomatisierung und Anwendungsentwicklung für KMU",
        "published": KI_PUB_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/ki-fuer-kmu/", "cta2_text": "Überblick KI im Betrieb",
        "desc": ("Schnittstellen zwischen Programmen, Dokumente automatisch auslesen, Berichte ohne "
                 "Excel-Bastelei: Prozesse mit KI automatisieren für kleine Betriebe."),
        # Kopf der Huelle (Textblatt §1, Task 7); Beleg aus der FAQ „Was kostet eine Automatisierung?“
        "k": "Ich verbinde eure Programme, damit Daten nicht mehr von Hand von einem ins andere wandern.",
        "answer": ("Als Grundke IT-Service aus Grasbrunn automatisiere ich für Betriebe im Münchner Osten, was "
                   "regelmäßig gleich abläuft und an einer Datei hängt: Exporte, Listen, Rechnungen, Berichte. Zum "
                   "Festpreis, und KI nur dort, wo eine feste Regel nicht reicht."),
        "proof2": ("ico-check", "Festpreis, bevor etwas gebaut wird"),
        "trust": TRUST_DEFAULT,
        "intro": ("In fast jedem Betrieb gibt es eine Stelle, an der Daten von Hand von einem System "
                  "ins andere wandern. Jemand exportiert eine Liste, sortiert sie, tippt sie woanders "
                  "wieder ein. Das dauert, dabei passieren Fehler, und im nächsten Monat geht es von "
                  "vorn los. <strong>Genau solche Strecken automatisiere ich</strong>, mit einem "
                  "Programm, das den Weg einmal richtig geht und danach von allein läuft. Wo KI dabei "
                  "wirklich hilft, kommt sie zum Einsatz: beim Lesen unstrukturierter Dokumente etwa, "
                  "oder beim Zuordnen von Positionen, die nie exakt gleich heißen. Wo eine feste Regel "
                  "reicht, bleibt es bei der Regel. Das ist billiger und zuverlässiger."),
        "raw_intro": True,
        "cards": [
            ("E-Rechnungen aus vorhandenen Daten", "Aus CSV-Exporten, Listen oder einem Vorsystem entstehen Rechnungen als XRechnung oder ZUGFeRD.", "ico-file-text"),
            ("Schnittstellen zwischen Programmen", "Warenwirtschaft, Zeiterfassung, Buchhaltung, Kasse. Was Daten exportieren kann, lässt sich koppeln.", "ico-network"),
            ("Dokumente auslesen", "Lieferscheine, Eingangsrechnungen, Formulare: Inhalte werden erkannt und landen strukturiert in der Datenbank.", "ico-search-check"),
            ("Auswertungen und Berichte", "Zahlen, die heute jemand am Monatsende in Excel zusammensucht, entstehen automatisch und immer gleich.", "ico-list"),
            ("Wiederkehrende Läufe", "Nächtliche Abgleiche, Erinnerungen, Prüfungen, Datenübernahmen. Einmal eingerichtet, läuft es weiter.", "ico-clock"),
            ("Meldung statt Nachsehen", "Wenn etwas schiefgeht, meldet sich die Anwendung von selbst. Per E-Mail oder Nachricht aufs Handy.", "ico-mail"),
        ],
        "extra": """
      <h2>Sonderfall E-Rechnung</h2>
      <p>Kommen eure Rechnungsdaten aus einem Vorsystem oder einer Excel-Liste, lässt sich die E-Rechnung gleich mit automatisieren, statt zweimal umzustellen. Fristen, Ausnahmen und die Wahl des passenden Programms stehen auf der Seite <a href="/e-rechnung/">E-Rechnung</a>.</p>

      <h2>Wie so ein Projekt abläuft</h2>
      <p>Am Anfang steht kein Angebot, sondern ein Blick auf den Ablauf, um den es geht. Meist zeigt sich schon dabei, ob die Sache klein oder groß ist.</p>
      <ol class="lp-steps">
        <li><strong>Ablauf ansehen:</strong> Wir gehen den Weg der Daten einmal gemeinsam durch, so wie er heute läuft. Mit den echten Dateien, nicht mit einem Beispiel.</li>
        <li><strong>Aufwand schätzen:</strong> Du bekommst eine Einschätzung, wie lange die Umsetzung dauert und wie viel Zeit sie im Monat spart. Beides schriftlich.</li>
        <li><strong>Klein anfangen:</strong> Erst läuft ein Teilstück, das nachweisbar funktioniert. Danach wird erweitert. Kein Projekt, das ein halbes Jahr im Dunkeln läuft.</li>
        <li><strong>Übergabe und Betreuung:</strong> Die Anwendung wird dokumentiert und läuft bei dir. Ich bleibe der Ansprechpartner, wenn sich etwas ändert.</li>
      </ol>

      <div class="ki-check">
        <h3>Kostenloser KI-Potenzialcheck</h3>
        <p>Wenn du nicht sicher bist, ob sich bei dir etwas lohnt: 60 bis 90 Minuten, wir gehen deine Abläufe durch, danach bekommst du schriftlich, was sich automatisieren lässt, was es kostet und was es bringt. Kostenlos und ohne Verpflichtung.</p>
        <div class="card-cta">
          <a href="tel:+491782584438" class="btn-p">Potenzialcheck vereinbaren</a>
          <a href="/kontakt/" class="btn-g">Lieber schreiben</a>
        </div>
      </div>
""",
        "faqs": [
            ("Welche Abläufe eignen sich überhaupt?",
             "Am besten alles, was regelmäßig vorkommt, immer gleich abläuft und heute an einer Datei "
             "hängt: Exporte, Listen, Formulare, Berichte. Je klarer die Regel, desto einfacher die "
             "Umsetzung. Schwieriger wird es, wenn bei jedem Durchgang jemand eine Entscheidung "
             "treffen muss, die auf Erfahrung beruht. Dann automatisiert man die Vorarbeit und lässt "
             "die Entscheidung beim Menschen."),
            ("Was kostet eine Automatisierung?",
             "Nach dem ersten Blick auf den Ablauf bekommst du einen Festpreis, bevor irgendetwas gebaut "
             "wird. Kleinere Strecken sind oft an einem Tag fertig, größere brauchen mehrere. Was später "
             "außerhalb des Auftrags anfällt, kostet 110 Euro netto je Stunde im 15-Minuten-Takt."),
            ("Was passiert, wenn sich unser Vorsystem ändert?",
             "Dann muss die Anwendung angepasst werden, das gehört dazu. Deshalb baue ich die "
             "Schnittstelle so, dass die Stelle, an der die Daten hereinkommen, sauber getrennt vom "
             "Rest liegt. Ein Formatwechsel ist dann eine überschaubare Änderung und kein neues "
             "Projekt. Und weil ich deine IT ohnehin betreue, erfahre ich von der Umstellung meist "
             "vorher."),
            ("Woher weiß ich, dass die Ergebnisse stimmen?",
             "Weil nichts ungeprüft durchläuft. Bei allem, was mit Geld oder Rechtsfolgen zu tun hat, "
             "arbeitet die Anwendung nach festen Regeln statt nach Wahrscheinlichkeiten, und die "
             "Ergebnisse werden gegen die Ausgangsdaten gegengerechnet. Wo ein Sprachmodell beteiligt "
             "ist, etwa beim Lesen eines Lieferscheins, gibt es eine Kontrollstufe: Unsichere Fälle "
             "landen zur Sichtung auf dem Bildschirm statt still in der Datenbank."),
        ],
    },
    {
        "slug": "ki-videoanalyse", "nav": "Videoanalyse & Auswertung",
        "title": "Videoüberwachung mit KI: Fahrzeuge & Kennzeichen | Grundke IT",
        "h1": "Videoanalyse und Auswertung – Kameradaten nutzbar machen",
        "service_type": "KI-gestützte Videoanalyse und Auswertung für Unternehmen",
        "published": KI_PUB_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/netzwerk-wlan-firewall/", "cta2_text": "Netzwerk & Kameratechnik",
        "desc": ("Videoüberwachung mit KI: Fahrzeuge und Kennzeichen erkennen, Vorgänge zählen, Kennzahlen "
                 "darstellen. Auf vorhandenen UniFi-Anlagen, Verarbeitung im Haus."),
        # Kopf der Huelle (Textblatt §1, Task 7); Beleg aus Hinweis und Karte der Seite (keine Gesichtserkennung,
        # Verarbeitung im Haus)
        "k": ("Ich setze auf eure vorhandene Kameraanlage eine Auswertung, die Fahrzeuge erkennt, Vorgänge zählt und "
              "Auffälligkeiten meldet."),
        "answer": ("Als Grundke IT-Service aus Grasbrunn richte ich für Betriebe im Münchner Osten eine Videoanalyse "
                   "auf vorhandenen Kameras ein, meist UniFi Protect: Fahrzeuge und Vorgänge werden gezählt, "
                   "Kennzeichen nur mit klarem Zweck gelesen, und die Aufnahmen bleiben im Haus."),
        "proof2": ("ico-shield", "Ohne Gesichtserkennung, Verarbeitung im Haus"),
        "trust": TRUST_DEFAULT,
        "intro": ("Die meisten Betriebe haben Kameras, und fast alle benutzen sie erst, wenn etwas "
                  "passiert ist. Dann sitzt jemand eine Stunde vor der Zeitleiste und sucht. "
                  "<strong>Dabei steckt in diesen Aufnahmen eine Information, die sich automatisch "
                  "herausziehen lässt:</strong> was sich bewegt hat, wann, wie oft und in welche "
                  "Richtung. Auf vorhandene UniFi-Protect-Anlagen setze ich eine Auswertung auf. Die "
                  "Erkennung läuft auf Hardware im Betrieb, die Ergebnisse landen in einer Datenbank, "
                  "und daraus entsteht eine Oberfläche mit Zahlen. Die Aufnahmen selbst verlassen das "
                  "Haus dabei nicht."),
        "raw_intro": True,
        "cards": [
            ("Fahrzeuge und Kennzeichen erkennen", "Fahrzeuge, Container, Maschinen, Paletten. Wo es einen klaren Zweck gibt, werden auch Kennzeichen gelesen, etwa um bekannte Fahrzeuge von fremden zu unterscheiden.", "ico-search-check"),
            ("Vorgänge zählen", "Zufahrten, Anlieferungen, Durchgänge, Standzeiten. Mit Zeitstempel und ohne dass jemand mitschreibt.", "ico-list"),
            ("Protokoll in der Datenbank", "Jedes Ereignis wird gespeichert und bleibt auswertbar, auch wenn die Aufnahme längst gelöscht ist.", "ico-file-text"),
            ("Kennzahlen auf einen Blick", "Eine Oberfläche zeigt Verläufe, Summen und Auffälligkeiten. Im Browser, auch vom Handy aus.", "ico-monitor"),
            ("Meldung bei Auffälligkeiten", "Bewegung außerhalb der Betriebszeit oder ungewöhnliche Häufungen melden sich von selbst.", "ico-mail"),
            ("Verarbeitung im Haus", "Erkennung und Speicherung laufen auf eigener Hardware im Netzwerk, nicht bei einem Clouddienst.", "ico-shield"),
        ],
        "extra": """
      <h2>Was dabei erlaubt ist und was nicht</h2>
      <p>Videoauswertung im Betrieb ist kein Selbstläufer. Für die Aufnahme selbst braucht es einen Grund, der sich benennen lässt, meist der Schutz von Eigentum oder die Kontrolle betrieblicher Abläufe, und dieser Grund muss schwerer wiegen als das Interesse der Aufgenommenen. Dazu kommen Hinweisschilder, festgelegte Löschfristen, ein Eintrag im Verzeichnis der Verarbeitungstätigkeiten und, sobald Beschäftigte betroffen sind, deren Beteiligung.</p>
      <p>Die Auswertung ändert an diesen Regeln nichts, sie verschiebt aber die Bewertung. Wer Fahrzeuge und Objekte zählt, verarbeitet etwas anderes als jemand, der Personen wiedererkennt.</p>
      <p>Kennzeichen liegen dazwischen: Über den Halter lassen sie sich einer Person zuordnen und sind deshalb personenbezogene Daten. Wer sie liest, braucht einen klar benannten Zweck, ein Hinweisschild und kurze Löschfristen; Kennzeichen, die zu keinem bekannten Fahrzeug gehören, werden nicht dauerhaft gespeichert.</p>
      <div class="ki-note">
        <p><strong>Gesichtserkennung und die Auswertung des Verhaltens einzelner Mitarbeiter baue ich nicht.</strong> Das ist rechtlich heikel bis unzulässig, und in einem normalen Betrieb ist es auch gar nicht nötig: Für die Fragen, um die es tatsächlich geht, reicht es, Objekte zu unterscheiden, Vorgänge zu zählen und, wo es einen Zweck gibt, Kennzeichen zu lesen. Kennzeichen von Mitarbeiterfahrzeugen werden nicht genutzt, um Arbeitszeiten oder Wege zu überwachen.</p>
        <p>Wo eine Datenschutz-Folgenabschätzung fällig wird, sage ich das vor der Umsetzung, statt es später zu entdecken. Die rechtliche Prüfung im Einzelfall bleibt Sache deines Datenschutzbeauftragten oder deines Anwalts. Ich sorge dafür, dass die Technik zu dieser Prüfung passt.</p>
      </div>

      <h2>Typische Fragen, die sich damit beantworten lassen</h2>
      <div class="card-grid card-grid--4">
        <div class="card"><h3>Wie viel ist wirklich los?</h3><p>Zufahrten, Anlieferungen und Abholungen pro Tag, Woche und Monat. Mit Tagesverlauf statt Bauchgefühl.</p></div>
        <div class="card"><h3>Wie lange steht etwas?</h3><p>Standzeiten von Fahrzeugen oder Containern, inklusive Auffälligkeiten nach oben.</p></div>
        <div class="card"><h3>War nachts jemand da?</h3><p>Bewegung außerhalb der Betriebszeiten wird erkannt und gemeldet, ohne dass jemand aufbleibt.</p></div>
        <div class="card"><h3>Stimmt die Dokumentation?</h3><p>Erfasste Vorgänge lassen sich gegen Lieferscheine oder Aufträge halten, wenn etwas unklar ist.</p></div>
      </div>

      <div class="ki-check">
        <h3>Erst ansehen, dann entscheiden</h3>
        <p>Ob sich eine Auswertung lohnt, hängt an der Anlage und an der Frage, die du beantwortet haben willst. Beim kostenlosen Potenzialcheck sehe ich mir die vorhandenen Kameras an und sage dir, was damit geht und was nicht. Ist die Anlage dafür nicht geeignet, erfährst du das an dem Tag und nicht nach dem ersten Rechnungsposten.</p>
        <div class="card-cta">
          <a href="tel:+491782584438" class="btn-p">Anlage ansehen lassen</a>
          <a href="/kontakt/" class="btn-g">Lieber schreiben</a>
        </div>
      </div>
""",
        "faqs": [
            ("Funktioniert das mit unseren vorhandenen Kameras?",
             "In der Regel ja, wenn die Kameras einen brauchbaren Bildausschnitt und eine vernünftige "
             "Auflösung liefern. Ich arbeite überwiegend mit Anlagen von Ubiquiti UniFi Protect, weil "
             "ich diese Technik ohnehin plane und betreue. Andere Systeme gehen auch, solange sie "
             "einen Videostream im Netzwerk bereitstellen. Was nicht geht, sage ich, bevor etwas "
             "gekauft wird."),
            ("Werden die Aufnahmen in die Cloud geschickt?",
             "Nein. Erkennung und Auswertung laufen auf Hardware bei dir im Netzwerk. Was das Haus "
             "verlässt, ist höchstens eine Meldung, dass etwas passiert ist, und auch nur, wenn du das "
             "so willst. Genau das ist der Grund, warum ich diesen Weg baue und keinen Clouddienst "
             "dazwischenschalte."),
            ("Dürfen wir das überhaupt?",
             "Videoüberwachung im Betrieb ist zulässig, wenn es einen berechtigten Grund gibt, die "
             "Aufnahme verhältnismäßig bleibt, Hinweisschilder vorhanden sind, Löschfristen festgelegt "
             "sind und die Verarbeitung dokumentiert ist. Sind Beschäftigte betroffen, müssen sie "
             "beteiligt werden. Die Auswertung von Objekten und Vorgängen ist dabei deutlich weniger "
             "kritisch als das Wiedererkennen von Personen, das ich bewusst nicht baue. Kennzeichen sind "
             "personenbezogene Daten; sie werden nur gelesen, wo es einen klaren Zweck gibt, und nach kurzer "
             "Frist gelöscht. Die rechtliche Prüfung im Einzelfall gehört zu deinem Datenschutzbeauftragten."),
            ("Wie zuverlässig erkennt so ein System?",
             "Bei klar unterscheidbaren Objekten wie Fahrzeugen ist die Erkennung gut genug, um "
             "belastbare Zahlen zu liefern. Fehler gibt es trotzdem, vor allem bei schlechtem Licht, "
             "Regen oder ungünstigem Kamerawinkel. Deshalb wird jede Auswertung anfangs mit der "
             "Wirklichkeit abgeglichen und nachjustiert, bevor sie in den Betrieb geht. Wer behauptet, "
             "so etwas laufe von Anfang an fehlerfrei, hat es nicht gemacht."),
            ("Was kostet eine solche Auswertung?",
             "Das hängt daran, wie viele Kameras beteiligt sind, wie klar die Fragestellung ist und ob "
             "passende Hardware für die Erkennung schon vorhanden ist. Nach dem Blick auf die Anlage "
             "bekommst du einen Festpreis. Was später außerhalb des Auftrags anfällt, kostet 110 Euro "
             "netto je Stunde im 15-Minuten-Takt."),
        ],
    },
    {
        "slug": "ki-dsgvo", "nav": "KI sicher einsetzen",
        "title": "KI sicher einsetzen: ChatGPT, Copilot & DSGVO | Grundke IT",
        "h1": "KI sicher einsetzen: Verträge, Regeln und Schulung für den Betrieb",
        "service_type": "Einführung von KI im Unternehmen, datenschutzgerecht umgesetzt",
        "published": KI_PUB_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/schulung/", "cta2_text": "Schulung für dein Team",
        "offers": ([offer_from("KI-Start", PRICES["ki_start"],
                               "Bestandsaufnahme, Werkzeug mit Vertrag, Leitplanken, Nutzungsrichtlinie, Schulung "
                               "und erste Anwendung, einmalig netto.")] if SHOW_FROM_PRICES else []),
        "desc": ("ChatGPT, Copilot & Co. datenschutzgerecht im Betrieb: Verträge, Nutzungsrichtlinie und Schulung "
                 "als Maßnahme zur KI-Kompetenz (Art. 4 KI-VO). Paket KI-Start."),
        # Kopf der Huelle (Textblatt §1, Task 7); Beleg = Preis des Pakets KI-Start (KI_START_TEXT, FAQ), ohne
        # Projektpreise der Stundensatz wie in der FAQ „Was kostet die Einführung?“
        "k": ("Ich lege mit euch fest, welche KI-Werkzeuge erlaubt sind und welche Daten hineindürfen, in einer "
              "kurzen, verständlichen Richtlinie."),
        "answer": ("Als Grundke IT-Service aus Grasbrunn führe ich KI in Betrieben im Münchner Osten datenschutzgerecht "
                   "ein: geschäftlicher Zugang mit Auftragsverarbeitungsvertrag, Nutzungsrichtlinie und Schulung als "
                   "Maßnahme zur KI-Kompetenz nach Artikel 4 der KI-Verordnung, als Paket KI-Start zum Festpreis."),
        "proof2": (("ico-check", "Paket KI-Start ab " + eur(PRICES["ki_start"]) + " netto")
                   if SHOW_FROM_PRICES else PROOF_ADHOC),
        "trust": TRUST_DEFAULT,
        "intro": ("Das häufigste Problem beim KI-Einsatz im Betrieb ist nicht die Technik. Es ist der "
                  "Mitarbeiter, der eine Kundenliste in ein kostenloses Chatfenster kopiert, weil es "
                  "schneller geht. <strong>Damit liegen personenbezogene Daten bei einem Anbieter, "
                  "mit dem kein Vertrag besteht</strong>. Das kann bereits ein Datenschutzverstoß sein "
                  "und ist kein Kavaliersdelikt. Dahinter steckt selten böse Absicht, sondern eine fehlende "
                  "Ansage. Ich kläre für deinen Betrieb, welche Werkzeuge benutzt werden dürfen, wo "
                  "sie laufen und was hineindarf, und halte das so fest, dass es im Alltag auch "
                  "jemand liest."),
        "raw_intro": True,
        "cards": [
            ("Wo das Modell läuft", "Eigene Hardware, EU-Rechenzentrum oder Anbieter mit Vertrag. Für jede Aufgabe die passende Stufe.", "ico-cloud"),
            ("Auftragsverarbeitungsvertrag", "Welcher Anbieter einen anbietet, was darin stehen muss und wo die Daten tatsächlich liegen.", "ico-file-text"),
            ("Nutzungsrichtlinie", "Eine verständliche Seite für die Belegschaft: erlaubte Werkzeuge, erlaubte Daten, Ansprechpartner.", "ico-list"),
            ("Schulung der Mitarbeiter", "Artikel 4 der KI-Verordnung verlangt Maßnahmen, die die KI-Kompetenz im Unternehmen fördern.", "ico-user-check"),
            ("Lokale KI-Server einrichten", "Ein Sprachmodell auf einem eigenen Server im Betrieb, das ohne Internetverbindung arbeitet. Für sensible Daten der sauberste Weg.", "ico-monitor"),
            ("Bestandsaufnahme", "Welche KI-Werkzeuge im Betrieb bereits benutzt werden, weiß meist niemand. Das lässt sich klären.", "ico-search-check"),
        ],
        "extra": """
      <h2>KI-Start: die Hürde nehmen wir gemeinsam</h2>
      <p>Viele Inhaber lassen die Finger von KI, während im selben Betrieb vielleicht schon jemand Kundendaten in einen privaten ChatGPT-Zugang tippt. Das Risiko verschwindet nicht, indem man KI verbietet, sondern indem man sie ordentlich einführt. Das Paket KI-Start hat sieben Schritte:</p>
      <!--more:Die sieben Schritte-->
      <ol class="lp-steps">
        <li><strong>Bestandsaufnahme:</strong> Wer nutzt heute schon welche KI, mit welchen Daten und über welche Konten?</li>
        <li><strong>Werkzeug mit Vertrag:</strong> eine bezahlte Business-Version mit Auftragsverarbeitungsvertrag und klaren Nutzungsbedingungen, etwa Microsoft 365 Copilot, ChatGPT Business oder Claude Team, möglichst mit Verarbeitung in der EU. Oder eine lokale KI im Haus, wenn die Daten den Betrieb nicht verlassen sollen.</li>
        <li><strong>Auftragsverarbeitung mit allen Dienstleistern</strong> prüfen und ablegen, nicht nur mit dem KI-Anbieter.</li>
        <li><strong>Technische Leitplanken:</strong> Zugriff nur über Firmenkonten, private KI-Konten auf Firmengeräten sperren, Rechte und Freigaben in Microsoft 365 aufräumen, bevor Copilot Dateien findet, die nie für alle gedacht waren.</li>
        <li><strong>Nutzungsrichtlinie:</strong> zwei Seiten, verständlich: was hineindarf, was nicht und wer Ansprechpartner ist.</li>
        <li><strong>Mitarbeitende befähigen:</strong> die <a href="/schulung/">Schulung</a> „KI sicher nutzen“ als Maßnahme zur KI-Kompetenz nach Artikel 4 der KI-Verordnung, mit Teilnahmenachweis.</li>
        <li><strong>Erste Anwendung im Alltag:</strong> Zusammenfassungen, Entwürfe für Dokumente und Mails, Auswertungen. Dort sieht das Team den Nutzen.</li>
      </ol>
      <!--/more-->
      """ + KI_START_TEXT + """

      <h2>Drei Wege, und wann welcher passt</h2>
      <p>Die wichtigste Entscheidung fällt vor der ersten Zeile Code: wo die Daten verarbeitet werden. Danach richtet sich alles Weitere.</p>
      <!--more:Die drei Wege im Vergleich-->
      <div class="ki-tbl-wrap">
        <table class="ki-tbl">
          <thead><tr><th scope="col">Weg</th><th scope="col">Wie es funktioniert</th><th scope="col">Wofür geeignet</th></tr></thead>
          <tbody>
            <tr><td>Lokales Modell</td><td data-label="Wie es funktioniert">Das Modell läuft auf Hardware im Betrieb. Die Daten verlassen das Netzwerk nicht, eine Internetverbindung ist nicht nötig.</td><td data-label="Wofür geeignet">Personaldaten, Patienten- und Mandantendaten, Kalkulationen, alles wirklich Vertrauliche.</td></tr>
            <tr><td>EU-Rechenzentrum</td><td data-label="Wie es funktioniert">Verarbeitung bei einem Anbieter mit Standort in der EU, mit Auftragsverarbeitungsvertrag und ohne Training auf deinen Daten.</td><td data-label="Wofür geeignet">Alltagsaufgaben mit Personenbezug, wenn die eigene Hardware dafür nicht reicht.</td></tr>
            <tr><td>Großer Anbieter mit Vertrag</td><td data-label="Wie es funktioniert">Leistungsfähige Modelle bekannter Anbieter, geschäftlich lizenziert, mit Vertrag und abgeschalteter Trainingsnutzung.</td><td data-label="Wofür geeignet">Texte, Recherche, Entwürfe, Programmierung. Alles ohne personenbezogene oder vertrauliche Inhalte.</td></tr>
          </tbody>
        </table>
      </div>
      <p>In der Praxis läuft es meist auf eine Kombination hinaus: das Bequeme für Unkritisches, das Lokale für alles, was den Betrieb nicht verlassen darf. Wichtig ist, dass die Grenze zwischen beidem klar gezogen und aufgeschrieben ist.</p>
      <!--/more-->

      <h2>Was die KI-Verordnung von einem KMU verlangt</h2>
      <p>Artikel 4 der europäischen KI-Verordnung gilt seit dem 2. Februar 2025. Mit dem sogenannten Digital Omnibus (Verordnung (EU) 2026/1744, in Kraft seit dem 27. Juli 2026) wurde er entschärft: Ein Unternehmen, das KI-Systeme einsetzt, muss nicht mehr sicherstellen, dass jeder Beschäftigte einen bestimmten Wissensstand erreicht. Es muss aber Maßnahmen ergreifen, die die KI-Kompetenz der Menschen fördern, die damit arbeiten. Das gilt für den Betrieb, in dem drei Leute ChatGPT benutzen, genauso wie für Entwickler von Hochrisiko-Anwendungen.</p>
      <p>Ein festes Schulungsprogramm schreibt die Verordnung nicht vor. Verlangt wird, dass die Maßnahmen zur Rolle und zur tatsächlichen Nutzung passen und dass das Unternehmen sie belegen kann. In Deutschland ist die Bundesnetzagentur als Aufsichtsbehörde vorgesehen. Ein eigener Bußgeldtatbestand für Artikel 4 besteht derzeit nicht, was die Sache aber nicht erledigt: Entsteht durch falsche KI-Nutzung ein Schaden, steht die Frage im Raum, ob eine angemessene Unterweisung ihn verhindert hätte.</p>
      <div class="ki-note">
        <p>Praktisch heißt das zweierlei: eine kurze, verständliche Nutzungsrichtlinie und eine Unterweisung, die dokumentiert ist. Beides mache ich zusammen mit dir. Die <a href="/schulung/">IT-Sicherheitsschulung</a> enthält ein eigenes Modul zum sicheren und datenschutzgerechten Umgang mit KI-Werkzeugen und deckt damit den Teil ab, der die Belegschaft betrifft.</p>
      </div>

      <h2>Was in eine Nutzungsrichtlinie gehört</h2>
      <div class="card-grid card-grid--4">
        <div class="card"><h3>Welche Werkzeuge</h3><p>Eine kurze Liste der freigegebenen Anwendungen. Alles andere ist damit nicht freigegeben, ohne dass man jedes Werkzeug einzeln verbieten muss.</p></div>
        <div class="card"><h3>Welche Daten</h3><p>Klar benannt, was nie in ein Chatfenster gehört: Kundendaten, Personaldaten, Zugangsdaten, Kalkulationen, Verträge.</p></div>
        <div class="card"><h3>Wer prüft das Ergebnis</h3><p>KI-Ausgaben sind Entwürfe. Wer sie verantwortet, bevor sie den Betrieb verlassen, muss benannt sein.</p></div>
        <div class="card"><h3>Wen man fragt</h3><p>Ein Ansprechpartner für den Fall, dass jemand unsicher ist. Ohne den landet im Zweifel doch wieder alles im Chatfenster.</p></div>
      </div>

      <div class="ki-note">
        <p><strong>Abgrenzung:</strong> Ich bin Fachinformatiker und kein Rechtsanwalt. Ich leiste keine Rechtsberatung. Was ich mache, ist die technische Umsetzung, die Bestandsaufnahme und die Vorbereitung der Entscheidungen, die dein Datenschutzbeauftragter, dein Steuerberater oder dein Anwalt trifft. Diese Seite gibt den allgemeinen Stand wieder und ersetzt keine Prüfung deines Einzelfalls.</p>
      </div>
""",
        "faqs": [
            ("Dürfen wir ChatGPT im Betrieb einfach so nutzen?",
             "Für allgemeine Texte ohne Personenbezug ist das meist unproblematisch. Sobald Kunden-, "
             "Personal- oder Gesundheitsdaten hineingehen, braucht es einen geschäftlichen Zugang, "
             "einen Auftragsverarbeitungsvertrag mit dem Anbieter und die Gewissheit, dass die "
             "Eingaben nicht zum Training verwendet werden. Der kostenlose Privatzugang erfüllt das "
             "nicht. Die praktikable Lösung ist meist eine kurze Richtlinie plus ein geschäftlicher "
             "Zugang für die, die ihn wirklich brauchen."),
            ("Was ist ein lokales Modell und wann lohnt es sich?",
             "Ein Sprachmodell, das auf einem Rechner im eigenen Netzwerk läuft, statt bei einem "
             "Anbieter im Internet. Die Daten verlassen das Haus nicht, es entstehen keine laufenden "
             "Nutzungskosten, dafür braucht es passende Hardware und die Leistung liegt unter der "
             "großen Modelle. Es lohnt sich überall dort, wo regelmäßig mit vertraulichen Inhalten "
             "gearbeitet wird, etwa in Kanzleien, Praxen und Personalabteilungen."),
            ("Was verlangt die KI-Verordnung konkret von uns?",
             "Artikel 4 verpflichtet jedes Unternehmen, das KI einsetzt, Maßnahmen zur Förderung der "
             "KI-Kompetenz seiner Beschäftigten zu ergreifen. Seit der Änderung durch den Digital "
             "Omnibus (in Kraft seit 27. Juli 2026) muss kein bestimmter Wissensstand mehr "
             "sichergestellt werden. Ein festes Curriculum ist nicht "
             "vorgeschrieben, die Maßnahmen müssen aber zur Rolle und zur tatsächlichen Nutzung passen "
             "und nachweisbar sein. In der "
             "Praxis genügt für einen kleinen Betrieb meist eine dokumentierte Unterweisung zusammen "
             "mit einer schriftlichen Nutzungsrichtlinie."),
            ("Wir haben keinen Datenschutzbeauftragten. Ist das ein Problem?",
             "Nicht zwangsläufig. Ein Datenschutzbeauftragter ist erst ab einer bestimmten Zahl von "
             "Personen Pflicht, die regelmäßig mit personenbezogenen Daten arbeiten, oder bei "
             "besonders sensiblen Verarbeitungen. Die Pflichten aus der DSGVO gelten aber unabhängig "
             "davon auch für kleine Betriebe. Ob dein Fall eine Bestellung erfordert, ist eine "
             "rechtliche Frage, die ich nicht beantworte. Ich sage dir, welche Verarbeitungen bei dir "
             "tatsächlich stattfinden, damit die Frage überhaupt beurteilt werden kann."),
            ("Was kostet die Einführung?",
             ("Das Paket KI-Start mit Bestandsaufnahme, Werkzeug, Leitplanken, Nutzungsrichtlinie, Schulung und "
              "erster Anwendung beginnt je nach Größe des Betriebs bei " + eur_txt(PRICES["ki_start"]) + " netto. Ein lokaler KI-Server "
              "hängt an der Hardware und bekommt einen eigenen Festpreis. Was in deinem Fall nötig ist, klären "
              "wir im kostenlosen Erstgespräch.")
             if SHOW_FROM_PRICES else
             ("Bestandsaufnahme und eine brauchbare Nutzungsrichtlinie sind für einen kleinen Betrieb meist an "
              "einem Tag zu schaffen, abgerechnet zu 110 Euro netto je Stunde im 15-Minuten-Takt. Ein lokales "
              "Modell einzurichten dauert länger und hängt an der Hardware. Was in deinem Fall nötig ist, klären "
              "wir im kostenlosen Erstgespräch.")),
            ("Reicht ChatGPT Business für den Datenschutz?",
             "Es ist eine gute Grundlage: Die Business-Version bringt einen Auftragsverarbeitungsvertrag mit, "
             "und die Eingaben werden nicht zum Training verwendet. Datenschutzgerecht wird der Einsatz aber "
             "erst mit den Regeln im Betrieb: wer welche Daten eingeben darf, welche Konten genutzt werden und "
             "wie das Team geschult ist. Wer welche Lizenz abschließt, steht auf der Seite Lizenzen."),
        ],
    },
    # ----------------------------------------------------------------------- #
    #  Seiten vom 07.10.2026                                                    #
    #  IT-Betreuer wechseln und Lizenzen (Spalte IT-Betreuung), Software nach   #
    #  Mass, Websites, E-Rechnung, Digitalbonus (Spalte KI, Software &          #
    #  Websites) und der Ratgeber „Die ersten 15 Minuten".                      #
    # ----------------------------------------------------------------------- #
    {
        "slug": "it-betreuer-wechseln", "nav": "IT-Betreuer wechseln", "group": "it",
        "title": "IT-Dienstleister wechseln: geordnete Übernahme | Grundke IT",
        "h1": "IT-Betreuer wechseln: so läuft eine geordnete Übernahme",
        "service_type": "Übernahme der IT-Betreuung von einem anderen Dienstleister",
        "published": NEW_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/managed-it-service/", "cta2_text": "Laufende IT-Betreuung",
        "desc": ("Dein IT-Dienstleister ist nicht erreichbar oder hört auf? Übernahme-Checkliste, was du "
                 "vom alten Betreuer brauchst und wie eine geordnete Übernahme läuft."),
        "k": ("Dein ITler geht nicht ran? Ich schon. Beim Wechsel sorge ich dafür, dass Kennwörter, Lizenzen und "
              "Netzwerkplan danach bei euch liegen."),
        "answer": ("Bei Grundke IT-Service in Grasbrunn läuft der Wechsel für Betriebe im Münchner Osten in vier "
                   "Schritten: kostenloser IT-Schnellcheck, Übergabe der Zugänge mit Checkliste, Datensicherung "
                   "testen und alte Zugänge abschalten, danach Betreuung ab 149 € netto im Monat."),
        "chat": [
            ("kunde", "Unser IT-Betreuer meldet sich seit Wochen nicht mehr. Kannst du übernehmen?"),
            ("andreas", "Ja. Zuerst prüfe ich, ob eure Datensicherung läuft, danach übernehmen wir die Zugänge."),
            ("andreas", "Was wir vom alten Betreuer brauchen, steht in der Checkliste unten. Meldet er sich nicht, "
                        "holen wir die Zugänge über die Hersteller zurück."),
        ],
        "voices": ["dietz"],
        # Darstellung in der Huelle (Fix-Runde 1, 10.10.2026): Ablauf links, „Und wenn …“ rechts
        "proof2": ("ico-user-check", "Über 20 Jahre IT-Erfahrung"),
        "row": ("So läuft der Wechsel", "Und wenn der alte Betreuer gar nicht mehr reagiert?"),
        "intro": ("Den IT-Dienstleister wechselt niemand aus Lust. Meistens hat sich etwas angesammelt: "
                  "Anrufe, die keiner annimmt, Rückrufe nach Tagen, Rechnungen, die keiner nachvollziehen "
                  "kann. Oder der Kollege, der die IT nebenbei gemacht hat, ist nicht mehr da. Schwierig ist "
                  "dabei nicht der Wechsel selbst, sondern das Wissen, das beim alten Betreuer liegt: "
                  "Kennwörter, Lizenzen, wie das Netzwerk aufgebaut ist und wohin die Datensicherung läuft. "
                  "<strong>Ich übernehme deine IT so, dass dieses Wissen bei dir landet</strong>, "
                  "aufgeschrieben und mit einem Ansprechpartner, der deine IT danach kennt."),
        "raw_intro": True,
        "cards_h2": "IT-Dienstleister wechseln: was bei der Übernahme passiert",
        "cards": [
            ("Bestandsaufnahme", "Welche Geräte, Programme, Lizenzen und Verträge es gibt, wer welche Zugänge hat und wo die Daten liegen. Schriftlich.", "ico-list"),
            ("Zugänge auf dich", "Administrator-Kennwörter, Microsoft-365-Konten, Domain, Router und Firewall gehören dem Betrieb, nicht dem Dienstleister. So richte ich es ein.", "ico-key"),
            ("Datensicherung prüfen", "Läuft die Sicherung, und lässt sie sich zurückspielen? Das teste ich, bevor ich irgendetwas umbaue.", "ico-search-check"),
            ("Geordneter Übergang", "Der alte Betreuer bleibt zuständig, bis die Übergabe steht. Umgestellt wird in Ruhe und nicht am Montagmorgen.", "ico-handshake"),
            ("Dokumentation", "Am Ende hast du eine Übersicht eurer IT, die auch ohne mich lesbar ist.", "ico-file-text"),
            ("Laufende Betreuung", "Danach geht es mit einer planbaren Monatspauschale weiter. Vertragskunden werden bevorzugt behandelt.", "ico-user-check"),
        ],
        "extra": """
      <h2>Übernahme-Checkliste: Was du vom alten IT-Betreuer brauchst</h2>
      <p>Diese Liste kannst du eurem bisherigen Dienstleister so weitergeben. Je mehr davon vorliegt, desto schneller und billiger wird die Übernahme.</p>
      <ul class="lp-checklist">
        <li><strong>Administrator-Zugänge</strong> zu Servern, PCs und zum Netzwerk: Router, Firewall, WLAN, Switches.</li>
        <li><strong>Microsoft 365:</strong> ein Konto mit globaler Administratorrolle und die Liste der Lizenzen.</li>
        <li><strong>Domain und Webhosting:</strong> bei welchem Anbieter, mit welchem Kundenkonto, wer die DNS-Einträge verwaltet.</li>
        <li><strong>Lizenzen und Verträge:</strong> Virenschutz, Datensicherung, Software und Wartungsverträge mit Laufzeiten.</li>
        <li><strong>Datensicherung:</strong> was wohin gesichert wird und wann zuletzt eine Rücksicherung getestet wurde.</li>
        <li><strong>Netzwerkplan</strong> oder wenigstens: welches Gerät wo steht und welche feste IP-Adresse was hat.</li>
        <li><strong>Fernwartungszugänge</strong>, die der alte Betreuer eingerichtet hat, damit sie danach abgeschaltet werden können.</li>
        <li><strong>Offene Probleme</strong> und bekannte Macken, die noch niemand behoben hat.</li>
      </ul>
      <div class="ki-note">
        <p><strong>Kennwörter nie per E-Mail.</strong> Lass dir Zugänge persönlich oder über einen Passwortmanager übergeben und ändere sie nach dem Wechsel. Sonst hat der alte Dienstleister weiter Zugriff, ob er will oder nicht.</p>
      </div>

      <h2>Und wenn der alte Betreuer gar nicht mehr reagiert?</h2>
      <p>Das kommt vor, und es ist lösbar. Die meisten Zugänge lassen sich über den Hersteller oder Anbieter zurückholen, wenn du als Inhaber nachweisen kannst, dass dir Konto, Domain oder Gerät gehören. Das dauert länger als eine geordnete Übergabe. Deshalb fange ich in so einem Fall mit der Datensicherung an, bevor irgendetwas anderes angefasst wird.</p>

      <h2>So läuft der Wechsel</h2>
      <ol class="lp-steps">
        <li><strong>Kennenlernen:</strong> Beim kostenlosen IT-Schnellcheck sehe ich mir eure IT 30 bis 45 Minuten vor Ort an. Du bekommst einen schriftlichen Bericht, auch wenn wir danach nicht zusammenarbeiten.</li>
        <li><strong>Übergabe:</strong> Mit der Checkliste oben holen wir die Zugänge und Unterlagen vom alten Betreuer. Bis das steht, bleibt er zuständig.</li>
        <li><strong>Absichern:</strong> Datensicherung testen, Zugänge auf den Betrieb umstellen, alte Fernwartungszugänge abschalten.</li>
        <li><strong>Betreuung:</strong> Danach eine planbare Monatspauschale ab 149 € netto, monatlich kündbar.</li>
      </ol>
      <p>Nicht gleich wechseln? Ich springe auch als Vertretung ein, wenn euer IT-Betreuer im Urlaub oder krank ist, abgerechnet nach Aufwand.</p>
""",
        "faqs": [
            ("Wie lange dauert ein Wechsel des IT-Betreuers?",
             "Das hängt vor allem davon ab, wie gut der alte Betreuer mitarbeitet und was dokumentiert ist. "
             "Die Bestandsaufnahme selbst ist in einem kleinen Betrieb meist an einem Termin erledigt. Danach "
             "werden Zugänge übergeben und die Datensicherung getestet; bis das geschafft ist, bleibt der alte "
             "Dienstleister zuständig."),
            ("Muss ich meinem alten IT-Dienstleister zuerst kündigen?",
             "Besser nicht. Kündige, wenn die Übergabe geklärt ist, und achte auf die Fristen in deinem Vertrag. "
             "So ist bis zum Schluss jemand zuständig. Die Vertragsfristen prüfst du selbst oder mit deinem "
             "Anwalt, ich kümmere mich um die Technik."),
            ("Was kostet die Übernahme?",
             "Der IT-Schnellcheck zum Kennenlernen ist kostenlos. Wer danach eine Monatspauschale abschließt, "
             "bekommt das ausführliche IT-Assessment im Paket. Ohne Vertrag rechne ich nach Aufwand ab, 110 Euro "
             "netto je Stunde im 15-Minuten-Takt. Die Pakete beginnen bei 149 Euro netto im Monat."),
            ("Versprichst du feste Reaktionszeiten?",
             "Nein. Ich bin Einzelunternehmer mit abgestimmter Vertretung und verspreche nur, was ich jedes Mal "
             "halten kann. Vertragskunden werden bevorzugt "
             "behandelt, Premium-Kunden zuerst; feste Zeiten lassen sich beim Premium-Paket auf Nachfrage "
             "vereinbaren. Wer anruft oder schreibt, bekommt die Antwort von mir und nicht von einem "
             "Ticketsystem."),
            ("Was ist, wenn mein alter Betreuer die Zugangsdaten nicht herausgibt?",
             "Die Konten und Geräte gehören deinem Betrieb. Meist lässt sich der Zugang über den Hersteller oder "
             "Anbieter zurückholen, wenn du nachweist, dass sie dir gehören. Ich übernehme die technische Seite. "
             "Ob und wie du rechtlich gegen den alten Dienstleister vorgehst, klärst du mit deinem Anwalt."),
        ],
    },
    {
        "slug": "lizenzen", "nav": "Lizenzen", "group": "it",
        "title": "Lizenzen für Firmen: Microsoft 365, Copilot, ChatGPT | Grundke IT",
        "h1": "Lizenzen für deinen Betrieb, eingerichtet und verwaltet",
        "service_type": "Lizenzvertrieb mit Einrichtung und Verwaltung für Unternehmen",
        "published": NEW_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/microsoft-365-betreuung/", "cta2_text": "Microsoft 365 Betreuung",
        "desc": ("Microsoft 365, Copilot, ESET-Virenschutz und Datensicherung für Unternehmen: Lizenz, "
                 "Einrichtung und Verwaltung aus einer Hand. Raum München Ost."),
        # Kopf der Huelle (Textblatt §1/§3, Task 6); Darstellung: zwei Abschnitte aus "extra" als Zeile
        "k": ("Ich behalte Laufzeiten und Nutzer im Blick, damit ihr keine Lizenz bezahlt, die niemand mehr braucht."),
        "answer": ("Lizenzen für Microsoft 365, Copilot und ESET-Virenschutz bekommen Betriebe im Münchner Osten bei "
                   "Grundke IT-Service in Grasbrunn, mit Einrichtung, Verwaltung und Datensicherung auf einer Rechnung. "
                   "ChatGPT Business und Claude Team schließt ihr direkt beim Anbieter ab, ich richte sie ein."),
        "voices": ["verena-k"],
        "proof2": ("ico-file-text", "Lizenzen und Betreuung auf einer Rechnung"),
        "proof3": PROOF_ADHOC,
        "row": ("Was kosten ChatGPT oder Copilot für Unternehmen?", "Warum nicht einfach selbst online bestellen?"),
        "intro": ("Microsoft 365 kann jeder online bestellen. Was dabei fehlt, merkt man später: Konten ohne "
                  "Zwei-Faktor-Anmeldung, Lizenzen für Leute, die längst weg sind, Virenschutz, der nur auf "
                  "einem Teil der Rechner läuft. <strong>Bei mir bekommst du die Lizenz mit Einrichtung und "
                  "Verwaltung.</strong> Ich lege Konten an, richte Sicherheit und Datensicherung ein, passe die "
                  "Zahl der Lizenzen an, wenn jemand kommt oder geht, und behalte die Laufzeiten im Blick. Du "
                  "bekommst eine Rechnung von mir, je nach Produkt monatlich oder jährlich. ChatGPT- und "
                  "Claude-Teamkonten schließt ihr direkt beim Anbieter ab; ich richte sie ein und verwalte Nutzer "
                  "und Rechte."),
        "raw_intro": True,
        "cards_h2": "Was ich besorge und betreue",
        "cards": [
            ("Microsoft 365", "E-Mail, Teams, OneDrive und Office mit Zwei-Faktor-Anmeldung und einem Rechtekonzept, das zum Betrieb passt.", "ico-mail"),
            ("Microsoft 365 Copilot", "Copilot für Firmenkonten, nachdem Rechte und Freigaben aufgeräumt sind. Sonst findet Copilot Dateien, die nie für alle gedacht waren.", "ico-search-check"),
            ("ESET Virenschutz", "Zentral verwalteter Schutz auf allen Geräten. Warnungen und auslaufende Lizenzen laufen bei mir auf, statt unbemerkt zu bleiben.", "ico-shield"),
            ("Datensicherung", "Sicherung von Microsoft 365, Servern und Rechnern, mit einer Kopie außer Haus.", "ico-cloud"),
            ("ChatGPT und Claude im Team", "Geschäftliche Konten mit Vertrag statt privater Zugänge. Den Vertrag schließt ihr direkt beim Anbieter, ich richte die Konten ein und verwalte Nutzer und Rechte.", "ico-user-check"),
            ("Laufzeiten im Blick", "Wer kommt, wer geht, was läuft wann aus. Lizenzen werden angepasst, statt ungenutzt weiterzulaufen.", "ico-clock"),
        ],
        "extra": """
      <h2>Was kosten ChatGPT oder Copilot für Unternehmen?</h2>
      <p>Die Business-Versionen von ChatGPT (ChatGPT Business), Claude (Claude Team) und Microsoft 365 Copilot werden je Nutzer und Monat abgerechnet, Copilot zusätzlich zur Microsoft-365-Lizenz. Sie kosten mehr als ein Privatzugang. Dafür gibt es einen Vertrag mit Auftragsverarbeitung, die Verwaltung im Team und nach Angabe der Anbieter keine Nutzung eurer Eingaben zum Training. Die aktuellen Listenpreise nenne ich dir im Angebot, weil die Anbieter sie regelmäßig ändern.</p>
      <p>Wichtiger als der Preis ist die Vorbereitung. Copilot sieht alles, was ein Mitarbeiter in Microsoft 365 sehen darf. Sind Freigaben über Jahre gewachsen, findet er auch die Gehaltsliste im falschen Ordner. Deshalb räume ich Rechte und Freigaben auf, bevor Copilot eingeschaltet wird.</p>
      <div class="ki-note">
        <p><strong>Private KI-Konten auf Firmengeräten</strong> sind das eigentliche Risiko: Dort landen Kundendaten bei einem Anbieter, mit dem kein Vertrag besteht. Wie man das sauber löst, steht auf der Seite <a href="/ki-dsgvo/">KI sicher einsetzen</a>.</p>
      </div>

      <h2>Warum nicht einfach selbst online bestellen?</h2>
      <p>Kannst du. Der Preis der Lizenz ist bei mir nicht der Punkt, sondern was danach passiert: Wer richtet die Zwei-Faktor-Anmeldung ein, wer merkt, dass die Sicherung seit drei Wochen nicht läuft, wer kündigt die Lizenz der Kollegin, die im Frühjahr gegangen ist? Bei mir ist das ein Ansprechpartner, der deine Umgebung kennt, statt eines Kundenportals.</p>
""",
        "faqs": [
            ("Kann ich bestehende Microsoft-365-Lizenzen zu dir umziehen?",
             "Ja. Konten, Postfächer und Daten bleiben, wo sie sind; es ändert sich nur, über wen die Lizenzen "
             "laufen. Den Zeitpunkt legen wir so, dass du keine Laufzeit doppelt bezahlst."),
            ("Was kostet Copilot für kleine Unternehmen?",
             "Microsoft rechnet Copilot je Nutzer und Monat ab, zusätzlich zur Microsoft-365-Lizenz. Den aktuellen "
             "Preis nenne ich dir im Angebot, weil Microsoft die Preise regelmäßig anpasst. Bevor Copilot "
             "eingeschaltet wird, sollten Rechte und Freigaben aufgeräumt sein, sonst findet er mehr, als er soll."),
            ("Kann ich ChatGPT Business oder Claude Team datenschutzgerecht nutzen?",
             "Die Business-Versionen bieten einen Auftragsverarbeitungsvertrag und nutzen eure Eingaben nach "
             "Angabe der Anbieter nicht zum Training. Das ist die Voraussetzung für einen datenschutzgerechten "
             "Einsatz, aber nicht alles: Dazu gehören eine Nutzungsrichtlinie und klare Regeln, welche Daten "
             "hineindürfen. Den Vertrag schließt ihr direkt beim Anbieter ab, ich richte die Konten ein. Die "
             "rechtliche Bewertung im Einzelfall gehört zu deinem Datenschutzbeauftragten."),
            ("Wie wird abgerechnet?",
             "Microsoft 365, Copilot, Virenschutz und Datensicherung über eine Rechnung von mir, je nach Produkt "
             "monatlich oder jährlich. Kommt jemand dazu oder geht, passe ich die Zahl der Lizenzen an. ChatGPT "
             "und Claude rechnet der Anbieter direkt mit euch ab."),
        ],
    },
    {
        # Task 8 (Release C1, 10.10.2026): bis dahin Handseite. Steht nach lizenzen, damit der Fusslink an derselben
        # Stelle der Spalte IT-Betreuung bleibt (group_of). H1 mit Umbruch und <em> wie bisher (Textblatt §1, Hinweis),
        # name ohne Tags fuer Schema und og. og:title, og:image:alt, twitter:image:alt wie bisher (meta_extra);
        # description, og:description und twitter:description nennen das Portal „in Vorbereitung“, Preis „Ab 135 €“
        # (Andreas 10.10.2026, seo-ausnahmen.json). K4 und Antwortsatz aus dem Textblatt (Zeile 22, Antwortsatz mit
        # Teilnahmenachweis, Andreas 10.10.2026), keine Kundenstimme (Textblatt §3). Text, Preise, FAQ und Course-Knoten
        # wortgleich aus der Handseite; Zahlen im deutschen Format, jeder Preis mit „zzgl. MwSt.“.
        "slug": "schulung", "nav": "IT-Sicherheitsschulung", "group": "it",
        "title": "IT-Sicherheitsschulung & Datenschutz – Grundke IT-Service",
        "h1": "IT-Sicherheitsschulung<br>&amp; Datenschutz", "h1_em": "Datenschutz",
        "name": "IT-Sicherheitsschulung & Datenschutz",
        "service_type": "IT-Sicherheitsschulung für Mitarbeiter",
        # published: fruehester belegter Stand der Seite (erster Commit des Repos)
        "published": "2026-04-10", "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/it-sicherheit-backup/", "cta2_text": "IT-Sicherheit & Backup",
        "desc": ("IT-Sicherheitsschulung für KMUs: Live per Teams, Online-Portal mit Quiz und Zertifikat in Vorbereitung. "
                 "Ab 135 € pauschal. Grundke IT-Service, München Ost."),
        "meta_extra": {
            "og_title": "IT-Sicherheitsschulung – Grundke IT-Service",
            "og_desc": ("IT-Sicherheitsschulung für KMUs: Live per Teams, Online-Portal mit Quiz und Zertifikat in "
                        "Vorbereitung. Ab 135 € pauschal."),
            "og_alt": "Grundke IT-Service – IT-Sicherheitsschulung",
            "tw_desc": "IT-Sicherheitsschulung für KMUs: Live per Teams, Online-Portal mit Quiz und Zertifikat in Vorbereitung.",
            "tw_alt": "Grundke IT-Service – IT-Sicherheitsschulung",
        },
        "k": ("In der Schulung lernt euer Team, Phishing-Mails zu erkennen und KI-Werkzeuge zu nutzen, ohne Kundendaten "
              "preiszugeben."),
        "answer": ("Die IT-Sicherheitsschulung von Grundke IT-Service aus Grasbrunn läuft live per Microsoft Teams, dauert "
                   "rund 1,5 Stunden, kostet 135 € netto pauschal und jeder Teilnehmer bekommt einen Teilnahmenachweis als "
                   "PDF. Das Online-Portal ist in Vorbereitung und lässt sich vormerken."),
        # Beleg der Seite aus der FAQ „Hilft die Schulung bei der DSGVO …?“ (Fix-Runde 1: „Organisatorische“ statt
        # „Anerkannte“, liest sich sonst wie eine Zertifizierung)
        "proof2": ("ico-shield", "Organisatorische Maßnahme nach Art. 32 DSGVO"),
        "cards_h2": "Was dein Team lernt",
        "cards": [
            ("Phishing erkennen", "Gefälschte E-Mails, Links und Anhänge identifizieren – mit echten Beispielen aus der Praxis.", "ico-mail"),
            ("Passwort-Sicherheit", "Sichere Passwörter erstellen, Passwort-Manager nutzen, Zwei-Faktor-Authentifizierung einrichten.", "ico-key"),
            ("Social Engineering", "Manipulationstechniken erkennen – am Telefon, per E-Mail und persönlich.", "ico-user-check"),
            ("DSGVO-Grundlagen", "Personenbezogene Daten schützen, Meldepflichten kennen, datenschutzkonform arbeiten.", "ico-file-text"),
            ("Sicherer Umgang mit Geräten", "Bildschirmsperre, USB-Sticks, öffentliches WLAN, Arbeiten unterwegs.", "ico-monitor"),
            ("Notfall-Verhalten", "Was tun bei Verdacht auf einen Angriff? Richtig reagieren, richtig melden.", "ico-shield"),
            ("KI sicher nutzen", "Was in ChatGPT, Copilot und andere KI-Werkzeuge hinein darf und was nicht, woran man falsche Antworten erkennt, was eine Nutzungsrichtlinie regelt. Zählt als Maßnahme zur KI-Kompetenz nach Artikel 4 der KI-Verordnung.", "ico-search-check"),
        ],
        "extra": """
      <h2>Das Online-Portal im Detail</h2>
      <h3>Für den Firmeninhaber</h3>
      <ul class="lp-checklist">
        <li>Eigener Admin-Zugang</li>
        <li>Mitarbeiter einladen und verwalten</li>
        <li>Teilnahmeliste mit Bestätigung herunterladen</li>
        <li>Nachweis für Versicherung und Auditierung</li>
      </ul>
      <h3>Für die Mitarbeiter</h3>
      <ul class="lp-checklist">
        <li>Schulung im eigenen Tempo durcharbeiten</li>
        <li>Verständlich, praxisnah, kein IT-Fachwissen nötig</li>
        <li>Freiwilliges Quiz am Ende</li>
        <li>PDF-Zertifikat als Teilnahmenachweis</li>
      </ul>
""",
        # Hinweis zum Portal direkt ueber den Preiskarten (wie bisher in der Naehe der Preise). Fix-Runde 1 (Design-Review):
        # Preise vor „Das Online-Portal im Detail“, damit „in Vorbereitung“ vor der Beschreibung des Portals steht;
        # Karten bis 1023 px untereinander (prices_wide); hervorgehoben ist das buchbare Angebot (Live-Schulung) ohne
        # Abzeichen, Portal und Kombi ohne Hervorhebung und ohne Abzeichen („Beste Wahl“ entfaellt).
        "prices_before": "Das Online-Portal im Detail",
        "prices_wide": True,
        "prices_intro": ("<strong>Das Online-Portal ist in Vorbereitung.</strong> Portal und Kombi-Paket kannst du schon "
                         "vormerken, ich melde mich, sobald es startet. Die Live-Schulung ist schon buchbar."),
        "prices": [
            ("Live-Schulung", "135 €",
             "Interaktive Schulung mit Präsentation, echten Beispielen und Raum für Fragen. Direkt auf dein Unternehmen "
             "zugeschnitten – für Teams jeder Größe.", True, "pauschal (1,5h) · danach 110 €/h, zzgl. MwSt.",
             {"badge": None,
              "feats": ["1:1 oder Gruppenformat per Microsoft Teams", "Phishing, Passwörter, Social Engineering, DSGVO",
                        "Empfohlene Dauer: 1,5 Stunden", "Unterlagen als PDF zum Nachschlagen"],
              "btn": ("Schulung anfragen", MAILTO_SCHULUNG["live"])}),
            ("Online-Portal (in Vorbereitung)", "49 €",
             "Deine Mitarbeiter arbeiten die Schulung eigenständig durch – wann und wo sie wollen. Inhalte werden "
             "mindestens halbjährlich an aktuelle Bedrohungen angepasst.", False, "Grundpauschale / Halbjahr, zzgl. MwSt.",
             {"add": "+ 5 € pro Mitarbeiter / Halbjahr, zzgl. MwSt.",
              "feats": ["Eigener Firmenzugang mit Mitarbeiterverwaltung", "Inhalte mindestens alle 6 Monate aktualisiert",
                        "Quiz + PDF-Zertifikat pro Teilnehmer", "Teilnahmeliste als Nachweis für den Inhaber"],
              "btn": ("Portal vormerken", MAILTO_SCHULUNG["portal"])}),
            ("Kombi-Paket (in Vorbereitung)", "ab 165 €",
             "Die Live-Schulung bringt alle auf denselben Stand, das Portal frischt das Wissen danach jedes Halbjahr auf.",
             False, "/ Halbjahr (statt 184 €), zzgl. MwSt.",
             {"add": "Inkl. Live-Schulung + Portal + 4,50 €/Mitarbeiter, zzgl. MwSt.",
              "feats": ["Live-Schulung per Teams (1,5h)", "Portal-Zugang für alle Mitarbeiter",
                        "Quiz, Zertifikate & Teilnahmeliste", "10% Rabatt auf den Gesamtpreis"],
              "btn": ("Kombi-Paket vormerken", MAILTO_SCHULUNG["kombi"])}),
        ],
        # Rechenbeispiel (bisher Kasten unter den Preisen) und der Satz aus dem frueheren Abschluss „Noch Fragen?“
        "prices_after": ('      <p><strong>Rechenbeispiel:</strong> Firma mit 8 Mitarbeitern → Live-Schulung '
                         '<strong>135&nbsp;€</strong> + Portal-Halbjahr <strong>49&nbsp;€ + 40&nbsp;€ (8×5&nbsp;€)</strong> = '
                         '<strong>224&nbsp;€</strong> für ein komplett geschultes Team mit Zertifikat. Mit Kombi-Rabatt nur '
                         '<strong>201&nbsp;€</strong>. Alle Preise zzgl. MwSt.</p>\n'
                         '      <p><strong>Noch Fragen?</strong> Schreib mir – ich berate dich gerne, welche Variante für '
                         'dein Team passt.</p>\n'),
        "extra_schema": [SCHULUNG_COURSE],
        # „IT-Sicherheitsschulung“ bricht sonst nach „IT-“ um (.s-title .nowrap); seitlich ab 1024 px kleiner (aside_long)
        "faq_h2": 'Häufige Fragen zur <span class="nowrap">IT-Sicherheitsschulung</span>',
        "aside_long": True,
        "faqs": [
            ("Was kostet eine IT-Sicherheitsschulung?",
             "Die Live-Schulung per Microsoft Teams kostet 135 € pauschal für rund 1,5 Stunden (jede weitere Stunde "
             "110 €). Das Online-Portal kostet 49 € Grundpauschale pro Halbjahr plus 5 € je Mitarbeiter und Halbjahr. "
             "Das Kombi-Paket aus Live-Schulung und Portal startet bei 165 € pro Halbjahr. Alle Preise verstehen sich "
             "zzgl. MwSt."),
            ("Wie läuft die Live-Schulung ab?",
             "Die Live-Schulung findet interaktiv per Microsoft Teams statt und dauert rund 1,5 Stunden. Inhalte sind "
             "unter anderem Phishing erkennen, sichere Passwörter, Social Engineering, DSGVO-Grundlagen und der sichere "
             "Umgang mit KI-Werkzeugen – mit echten Beispielen und Raum für Fragen. Die Unterlagen erhältst du "
             "anschließend als PDF zum Nachschlagen."),
            ("Bekommen die Mitarbeiter einen Nachweis?",
             "Ja. Jeder Teilnehmer erhält ein PDF-Zertifikat als Teilnahmenachweis. Über das Online-Portal lädst du als "
             "Inhaber zusätzlich eine Teilnahmeliste herunter – ein verwertbarer Nachweis für Versicherung und "
             "Auditierung."),
            ("Für wen ist die Schulung geeignet?",
             "Für kleine und mittlere Unternehmen, Handwerksbetriebe, Praxen, Kanzleien und Büros. Die Inhalte sind "
             "verständlich und praxisnah aufbereitet – ein IT-Fachwissen ist nicht nötig."),
            ("Wie aktuell sind die Schulungsinhalte?",
             "Die Inhalte des Online-Portals werden mindestens alle sechs Monate an aktuelle Bedrohungen angepasst, "
             "damit dein Team über neue Betrugsmaschen und Angriffswege informiert bleibt."),
            ("Findet die Schulung online oder vor Ort statt?",
             "Die Live-Schulung findet online per Microsoft Teams statt – so sind alle Teilnehmer ortsunabhängig dabei, "
             "auch aus dem Home-Office. Das Online-Portal bearbeiten deine Mitarbeiter ebenfalls ortsunabhängig im "
             "Browser, wann und wo es ihnen passt."),
            ("Wie lange dauert eine Schulung?",
             "Die Live-Schulung dauert rund 1,5 Stunden. Die Inhalte im Online-Portal bearbeiten deine Mitarbeiter im "
             "eigenen Tempo – jederzeit unterbrechbar und ohne Zeitdruck."),
            ("Hilft die Schulung bei der DSGVO und anderen Compliance-Pflichten?",
             "Ja. Die Sensibilisierung der Mitarbeiter ist eine anerkannte organisatorische Maßnahme nach Art. 32 DSGVO "
             "und ein häufig geforderter Baustein für Cyber-Versicherungen und Audits. Mit dem PDF-Zertifikat und der "
             "Teilnahmeliste hast du den Nachweis schriftlich in der Hand."),
        ],
    },
    {
        "slug": "software-nach-mass", "nav": "Software nach Maß", "group": "ki",
        "title": "Software entwickeln lassen für kleine Betriebe | Grundke IT",
        "h1": "Software nach Maß für kleine Betriebe",
        "service_type": "Individuelle Softwareentwicklung und Betrieb für kleine Unternehmen",
        # 10.10.2026: Betrieb ab 80 € statt 79 € (Inhaltsaenderung -> neues Datum), Kopf mit K4 (Task 7)
        "published": NEW_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        # Kopf der Huelle (Textblatt §1, Task 7); Beleg = Betriebspreis der kleinen Anwendung (Andreas 10.10.2026:
        # 80 € netto), ohne Projektpreise der Vertrauenssatz der Seite
        "k": ("Aus der Excel-Liste, die drei Leute pflegen, baue ich eine kleine Anwendung, in der alle denselben "
              "Stand sehen."),
        "answer": ("Als Grundke IT-Service aus Grasbrunn baue ich für Betriebe im Münchner Osten kleine Anwendungen "
                   "dort, wo Standardsoftware nicht passt: zum Festpreis, betrieben auf einem Server in Deutschland "
                   "oder im eigenen Netzwerk, danach gepflegt für einen festen Monatsbetrag."),
        "proof2": (("ico-check", "Betrieb und Pflege ab " + eur(PRICES["software_betrieb"]) + " netto im Monat")
                   if SHOW_FROM_PRICES else
                   ("ico-check", "Festpreis für das Projekt, fester Monatsbetrag für Betrieb und Pflege")),
        "trust": TRUST_FESTPREIS,
        "prices_h2": "Was das kostet",
        "prices_intro": ("Richtwerte für den Einstieg, alle Preise netto. Den Festpreis bekommst du, nachdem wir den "
                         "Ablauf zusammen angesehen haben."),
        "prices": [
            ("Kleine Anwendung", "ab " + eur(PRICES["software_klein"]),
             "Eine Liste, ein Formular, ein Ablauf. Betrieb und Pflege ab " + eur(PRICES["software_betrieb"]) + " im Monat.",
             False, EINMALIG),
            ("Pilot mit Schnittstelle", "ab " + eur(PRICES["software_pilot"]),
             "Mehrere Rollen, Anbindung an Lexware Office oder ein anderes Programm, Abbruchpunkt nach der ersten "
             "Stufe. Betrieb ab " + eur(PRICES["software_pilot_betrieb"]) + " im Monat.", False, EINMALIG),
            ("Ablauf-Check vor Ort", "ab " + eur(PRICES["ablauf_check"]),
             "Ein halber bis ganzer Tag im Betrieb: wo Zeit verloren geht und was sich automatisieren lässt, mit "
             "Festpreisangebot. Wird bei Auftrag angerechnet.", False, EINMALIG),
        ] if SHOW_FROM_PRICES else [],
        "prices_after": ('      <p>Liegen die Ausgaben bei 4.000 € oder mehr, kann der <a href="/digitalbonus-bayern/">'
                         'Digitalbonus Bayern</a> bis zur Hälfte davon übernehmen. Freie Berufe sind ausgeschlossen, und ein '
                         'Ablauf-Check allein wird nicht gefördert, nur zusammen mit der Umsetzung.</p>\n'),
        "offers": [
            offer_from("Kleine Anwendung", PRICES["software_klein"], "Eine Liste, ein Formular, ein Ablauf, einmalig netto."),
            offer_from("Pilot mit Schnittstelle", PRICES["software_pilot"], "Mehrere Rollen und eine Schnittstelle, einmalig netto."),
            offer_from("Ablauf-Check vor Ort", PRICES["ablauf_check"], "Halber bis ganzer Tag im Betrieb, bei Auftrag angerechnet."),
        ] if SHOW_FROM_PRICES else [],
        "cta2_href": "/ki-automatisierung/", "cta2_text": "Abläufe automatisieren",
        "desc": ("Excel-Listen, Zettel, doppelte Eingaben: Ich baue kleine Anwendungen für eure Abläufe und "
                 "betreibe sie weiter. Festpreis, Server in Deutschland."),
        "intro": ("In vielen Betrieben gibt es diese eine Liste. Sie liegt als Excel-Datei auf dem Server, drei "
                  "Leute pflegen sie, und keiner weiß genau, welche Fassung stimmt. Daneben ein Ordner mit "
                  "Zetteln und ein Programm, in das dieselben Daten noch einmal getippt werden. <strong>Für "
                  "solche Stellen baue ich kleine Anwendungen</strong>, also Individualsoftware für genau euren "
                  "Ablauf: eine Oberfläche im Browser, eine "
                  "Datenbank dahinter, Rechte für die, die damit arbeiten, und eine Schnittstelle dorthin, wo "
                  "die Daten weiter gebraucht werden. Mit KI-Unterstützung entwickelt, deshalb meist in Wochen "
                  "und deutlich günstiger als bei einem Softwarehaus. Danach betreibe und pflege ich die "
                  "Anwendung weiter."),
        "raw_intro": True,
        "cards": [
            ("Aus der Liste wird eine Anwendung", "Was heute in Excel oder einer alten Access-Datenbank gepflegt wird, bekommt Eingabemasken, Prüfungen und einen Verlauf. Alle sehen denselben Stand.", "ico-list"),
            ("Schnittstellen statt Abtippen", "Lexware Office und viele Auftrags- und Rechnungsprogramme haben Schnittstellen. Kunden, Aufträge und Angebotsentwürfe lassen sich darüber anlegen und abgleichen.", "ico-network"),
            ("Rechte und Rollen", "Büro, Werkstatt und Chef arbeiten mit derselben Anwendung, aber nicht mit denselben Rechten.", "ico-key"),
            ("Im Browser, auch am Handy", "Nichts zu installieren. Die Anwendung läuft im Browser, auf der Baustelle genauso wie im Büro.", "ico-monitor"),
            ("Daten in Deutschland", "Betrieben auf einem Server in Deutschland mit Auftragsverarbeitungsvertrag oder auf Hardware bei dir im Netzwerk. Eure Daten könnt ihr jederzeit exportieren.", "ico-shield"),
            ("Betrieb und Pflege", "Updates, Datensicherung und Anpassungen, wenn sich ein Ablauf ändert. Dafür gibt es einen festen Monatsbetrag.", "ico-tools"),
        ],
        "extra": """
      <h2>Drei Beispiele</h2>
      <p>Das erste läuft täglich, das zweite ist im Aufbau, das dritte ist ein typischer Fall. Kundenprojekte nenne ich ohne Namen.</p>

      <div class="card-grid">
      <div class="ki-case">
        <span class="ki-case-tag">Eigener Betrieb · läuft täglich</span>
        <h3>Eine Kundenverwaltung, die direkt mit Lexware spricht</h3>
        <p>Mein eigener Betrieb läuft über eine Anwendung, die ich selbst gebaut habe: Kunden, Aufträge, Zeiten, Material und Angebote. Neue Kunden und Angebotsentwürfe legt sie über die Schnittstelle direkt in Lexware Office an, Rechnungsentwürfe ebenso. Ich tippe nichts zweimal.</p>
        <p class="ki-result">Jede Angabe wird einmal erfasst und landet dort, wo sie gebraucht wird.</p>
      </div>

      <div class="ki-case">
        <span class="ki-case-tag">Kundenprojekt · im Aufbau</span>
        <h3>Leergut zählen ohne Liste</h3>
        <p>Ein Getränkebetrieb zählt sein Leergut auf dem Hof bisher von Hand und führt den Bestand in Listen. Die neue Anwendung soll die Bestände über eine Kamera am Hof erfassen, je Lagergut anzeigen und den Verlauf festhalten. Die Erfassung läuft im Test, die Kamera vor Ort folgt.</p>
      </div>

      <div class="ki-case">
        <span class="ki-case-tag">Typischer Fall · Gastronomie</span>
        <h3>Veranstaltungen ohne vier Listen</h3>
        <p>Anfrage per Mail, Termin im Kalender, Menüauswahl in Excel, Rechnung im Buchhaltungsprogramm: Bei Feiern und Veranstaltungen laufen dieselben Daten oft durch vier Hände. Eine kleine Anwendung führt das an einer Stelle zusammen, vom ersten Anruf bis zur Rechnung.</p>
      </div>
      </div>

      <h2>So läuft ein Projekt ab</h2>
      <ol class="lp-steps">
        <li><strong>Ablauf ansehen:</strong> Wir gehen den Weg der Daten einmal mit den echten Dateien durch. Das geht im kostenlosen KI-Potenzialcheck oder ausführlicher im Ablauf-Check vor Ort.</li>
        <li><strong>Festpreis und Abbruchpunkt:</strong> Du bekommst einen Festpreis für die erste Stufe und weißt vorher, was danach kommt. Gefällt dir die erste Stufe nicht, hörst du dort auf.</li>
        <li><strong>Erste Stufe im Betrieb:</strong> Ein Teilstück läuft und wird benutzt, bevor erweitert wird. Kein Projekt, das ein halbes Jahr im Dunkeln liegt.</li>
        <li><strong>Betrieb und Pflege:</strong> Die Anwendung ist dokumentiert, ich betreibe und pflege sie weiter.</li>
      </ol>

      <h2>Wann ich abrate</h2>
      <p>Gibt es für euren Ablauf eine Standardsoftware, die passt, empfehle ich die und richte sie ein. Eigene Software lohnt sich dort, wo der Standard nicht passt, wo drei Programme nebeneinander laufen oder wo eine Liste so wichtig geworden ist, dass ein Fehler darin Geld kostet. Das sage ich im ersten Gespräch und nicht nach der ersten Rechnung.</p>
""",
        "faqs": [
            ("Was kostet es, Software entwickeln zu lassen?",
             ("Eine kleine Anwendung mit einer Liste, einem Formular und einem Ablauf beginnt bei rund " + eur_txt(PRICES["software_klein"]) + " "
              "netto. Ein Pilot mit mehreren Rollen und einer Schnittstelle, etwa zu Lexware Office, liegt meist "
              "zwischen " + eur_txt(PRICES["software_pilot"])[:-5] + " und " + eur_txt(PRICES["software_pilot_bis"]) + ". Dazu kommt ein Monatsbetrag für Betrieb, Datensicherung und Pflege. "
              "Den Festpreis bekommst du, nachdem wir den Ablauf gemeinsam angesehen haben.")
             if SHOW_FROM_PRICES else
             ("Das hängt vom Umfang ab. Nachdem wir den Ablauf gemeinsam angesehen haben, bekommst du einen "
              "Festpreis für die Umsetzung und einen Monatsbetrag für Betrieb, Datensicherung und Pflege.")),
            ("Warum ist das günstiger als bei einem Softwarehaus?",
             "Weil ich mit KI-Unterstützung entwickle. Was früher Monate dauerte, steht jetzt oft in Wochen. Den Code "
             "prüfe und teste ich selbst, bevor etwas übergeben wird, und ich stehe dafür gerade. Dazu kommt, dass "
             "es bei mir keine Vertriebsabteilung und keine Projektleitung gibt: Du sprichst von Anfang bis Ende "
             "mit dem, der baut."),
            ("Wird die Software von einer KI geschrieben?",
             "Mit KI-Unterstützung entwickelt, ja. Das macht mich schneller. Geplant, geprüft und getestet wird jede "
             "Anwendung von mir, und ich betreibe sie danach weiter. Du kaufst also kein Programm, das niemand "
             "versteht, sondern eine Anwendung mit einem Ansprechpartner."),
            ("Was passiert, wenn du ausfällst?",
             "Eine berechtigte Frage bei einem Ein-Mann-Betrieb. Für die laufende IT gibt es eine abgestimmte "
             "Vertretung. Für die Software gilt: Jede Anwendung wird dokumentiert, und wie du im Fall der Fälle an "
             "Quellcode und Daten kommst, legen wir vor Projektbeginn schriftlich fest. Deine Daten kannst du "
             "jederzeit exportieren."),
            ("Wo liegen unsere Daten?",
             "Auf einem Server in Deutschland, mit dem ein Auftragsverarbeitungsvertrag besteht, oder auf Hardware "
             "bei dir im Netzwerk. Das entscheiden wir vor dem Bau. Ein KI-Dienst kommt nur dort zum Einsatz, wo er "
             "gebraucht wird und die Daten es zulassen."),
            ("Gibt es dafür eine Förderung?",
             "In Bayern oft ja. Der Digitalbonus Bayern übernimmt bei kleinen gewerblichen Unternehmen bis zu 50 "
             "Prozent der förderfähigen Ausgaben ab 4.000 Euro. Beantragt wird vor dem Auftrag, Freie Berufe sind "
             "ausgeschlossen, und ein Ablauf-Check allein wird nicht gefördert, nur zusammen mit der Umsetzung. "
             "Mehr dazu auf der Seite zum Digitalbonus Bayern."),
        ],
    },
    {
        "slug": "websites-fuer-betriebe", "nav": "Websites für Betriebe", "group": "ki",
        "title": "Website erstellen lassen oder modernisieren | Grundke IT",
        "h1": "Websites für Betriebe, die gefunden werden",
        "service_type": "Technische Umsetzung von Websites für kleine Unternehmen",
        # 10.10.2026 (Task 7): neuer Kopf mit K4 und Antwortsatz -> neues Datum
        "published": NEW_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        # Kopf der Huelle (Textblatt §1, Task 7); Beleg = Richtwert des One-Pagers aus den Preiskarten, ohne
        # Projektpreise der Vertrauenssatz der Seite. Der Website-Check-Kasten bleibt sichtbar (Spec §5).
        "k": ("Ich baue eure Website technisch so auf, dass sie am Handy gut funktioniert und für Google und "
              "KI-Assistenten lesbar ist."),
        "answer": ("Als Grundke IT-Service aus Grasbrunn baue ich Websites für Betriebe im Münchner Osten technisch "
                   "neu auf: fürs Handy, schlank, mit eigenen Seiten je Leistung und Ort. Die Optik kommt aus "
                   "geprüften Vorlagen, Hosting und Pflege übernehme ich auf Wunsch."),
        "proof2": (("ico-check", "Website One-Pager ca. " + eur(PRICES["website_onepager"]) + " netto")
                   if SHOW_FROM_PRICES else ("ico-check", "Preis nach Aufwand, verbindlich im Angebot")),
        "trust": TRUST_WEBSITE,
        "prices_h2": "Was das kostet",
        "prices_intro": ("Richtwerte, alle Preise netto. Was es bei euch tatsächlich kostet, hängt vom Aufwand ab: "
                         "ob die Seite ganz neu entsteht oder ob ich eine bestehende übernehme und Texte, Bilder, "
                         "Design und Technik auf den aktuellen Stand bringe. Das klären wir in einem unverbindlichen "
                         "Telefonat."),
        "prices": [
            ("Website One-Pager", "ca. " + eur(PRICES["website_onepager"]),
             "Eine einzelne Landingpage mit allem Wichtigen auf einer Seite, fürs Handy gebaut, mit Anruf- und "
             "WhatsApp-Knopf, Impressum und Datenschutzerklärung an der richtigen Stelle.", False, EINMALIG),
            ("Website Start", "ca. " + eur(PRICES["website_start"]),
             "Bis fünf Seiten auf geprüfter Vorlage, fürs Handy gebaut, Impressum und Datenschutzerklärung an der "
             "richtigen Stelle, strukturierte Daten, Google-Unternehmensprofil eingerichtet.", False, EINMALIG),
            ("Website Ausbau", "ca. " + eur(PRICES["website_ausbau"]),
             "Bis 15 Seiten mit eigenen Seiten je Leistung und Ort und Antworten auf häufige Kundenfragen. Umzug "
             "aus der alten Seite mit Weiterleitungen. Die Texte liefert ihr, ich sage euch, welche Fragen fehlen.",
             False, EINMALIG),
            ("Laufender Betrieb", eur(PRICES["website_betrieb"]),
             "Auf Wunsch: Hosting, Updates, Sicherheit, Datensicherung und ein monatlicher Bericht, wie die Seite "
             "gefunden wird. Sonst ziehe ich die fertige Seite zu einem Hoster eurer Wahl um.",
             False, "/ Monat zzgl. MwSt."),
        ] if SHOW_FROM_PRICES else [],
        "offers": [
            offer_from("Website One-Pager", PRICES["website_onepager"], "Eine Landingpage, Richtwert, einmalig netto.", approx=True),
            offer_from("Website Start", PRICES["website_start"], "Bis fünf Seiten auf geprüfter Vorlage, Richtwert, einmalig netto.", approx=True),
            offer_from("Website Ausbau", PRICES["website_ausbau"], "Bis 15 Seiten inklusive Umzug, Richtwert, einmalig netto.", approx=True),
            offer_from("Laufender Betrieb", PRICES["website_betrieb"], "Optional: Hosting, Updates, Sicherheit, Bericht; je Monat netto.", monthly=True, approx=True),
        ] if SHOW_FROM_PRICES else [],
        "cta2_href": "/kontakt/", "cta2_text": "Sichtbarkeits-Check anfragen",
        "desc": ("Website erstellen lassen oder modernisieren: schnell, fürs Handy gebaut, für Google und "
                 "KI-Assistenten lesbar aufgebaut. Technische Umsetzung, Raum München Ost."),
        "intro": ("Viele Betriebs-Websites sind irgendwann entstanden und seitdem stehen geblieben. Am Handy "
                  "rutscht alles durcheinander, Google zeigt sie auf Seite drei, und wenn jemand ChatGPT nach "
                  "einem Betrieb in der Gegend fragt, kommt sie nicht vor. <strong>Ich baue die Website "
                  "technisch neu auf</strong>, aus der alten Seite heraus oder ganz neu. Was ich nicht mache, "
                  "ist Gestaltung wie eine Agentur: Die Optik kommt aus fertigen, geprüften Vorlagen und "
                  "Designsystemen. Meine Arbeit ist alles darunter, also Aufbau, Geschwindigkeit, Handy, "
                  "Barrierefreiheit, Datenschutz-Technik und die Sichtbarkeit in Suche und KI-Assistenten. Gebaut "
                  "wird mit KI-Unterstützung, so lässt sich eine alte Website schneller modernisieren; geprüft "
                  "und betreut wird sie von mir."),
        "raw_intro": True,
        "cards": [
            ("Fürs Handy gebaut", "Die meisten Besucher kommen über das Telefon. Die Seite wird zuerst dafür gebaut, mit Anruf- und WhatsApp-Knopf im Daumenbereich.", "ico-phone"),
            ("Schlank und schnell", "Kein Baukasten mit fünfzig Erweiterungen, sondern schlankes HTML. Die Seite lädt auch im Mobilnetz schnell.", "ico-clock"),
            ("Gefunden bei Google", "Eine eigene Seite je Leistung und Ort, saubere Titel, strukturierte Daten und ein gepflegtes Google-Unternehmensprofil.", "ico-search-check"),
            ("Lesbar für KI-Assistenten", "ChatGPT, Gemini und Copilot zitieren vor allem Seiten, die klare Antworten auf echte Kundenfragen geben. Darauf ist der Aufbau ausgelegt.", "ico-file-text"),
            ("Datenschutz-Technik", "Schriften lokal, kein Tracking ohne Einwilligung, Impressum und Datenschutzerklärung an der richtigen Stelle. Die Rechtstexte selbst verantwortet ihr.", "ico-shield"),
            ("Betrieb und Updates", "Hosting, Sicherheitsupdates, Datensicherung und ein monatlicher Bericht, wie die Seite gefunden wird. Rein technisch.", "ico-tools"),
        ],
        "extra": """
      <h2>Der Beleg ist diese Website</h2>
      <p>Diese Seite habe ich selbst so gebaut. Bei der Google-Suche nach „IT Service Grasbrunn“ stand sie am 7. Oktober 2026 auf Platz eins der Ergebnisliste, die Seite für Vaterstetten bei „IT Dienstleister Vaterstetten“ auf Platz zwei. Platzierungen schwanken je nach Suchendem und Tag, aber sie zeigen, dass der Aufbau trägt.</p>

      <div class="ki-note">
        <p><strong>Ich gestalte nicht, ich baue.</strong> Logo, Fotos und Texte kommen von euch, von eurer Agentur oder einem Fotografen. Ich setze sie technisch sauber um und sage euch, welche Seiten und Antworten für Suche und KI-Assistenten fehlen.</p>
      </div>

      <div class="ki-check">
        <h3>Kostenloser Website- und KI-Sichtbarkeits-Check</h3>
        <p>Bevor wir über einen Relaunch reden, sehe ich mir eure jetzige Seite an. Ihr bekommt einen kurzen schriftlichen Bericht:</p>
        <ul>
          <li>Wie schnell die Seite am Handy lädt und wie sie dort aussieht</li>
          <li>Ob sie bei Google für eure Leistungen und euren Ort gefunden wird</li>
          <li>Ob ChatGPT, Gemini und Copilot euren Betrieb nennen</li>
          <li>Ob die Datenschutz-Technik stimmt, als technischer Befund und nicht als Rechtsberatung</li>
        </ul>
        <div class="card-cta">
          <a href="tel:+491782584438" class="btn-p">Check vereinbaren</a>
          <a href="/kontakt/" class="btn-g">Lieber schreiben</a>
        </div>
      </div>
""",
        "faqs": [
            ("Was kostet eine Website für einen kleinen Betrieb?",
             ("Als Richtwert: Eine einzelne Landingpage liegt bei rund " + eur_txt(PRICES["website_onepager"]) + " netto, eine Website "
              "mit bis zu fünf Seiten bei rund " + eur_txt(PRICES["website_start"]) + ", eine größere mit eigenen Seiten je Leistung und "
              "Ort und dem Umzug aus der alten Seite bei rund " + eur_txt(PRICES["website_ausbau"]) + ". Wie viel es genau wird, hängt "
              "davon ab, wie viel schon da ist. Hosting, Updates und Sicherheit übernehme ich auf Wunsch für "
              + eur_txt(PRICES["website_betrieb"]) + " im Monat, sonst ziehe ich die Seite zu einem Hoster eurer Wahl um. "
              "Den Preis für euch klären wir in einem unverbindlichen Telefonat.")
             if SHOW_FROM_PRICES else
             ("Das hängt von der Zahl der Seiten und vom Umzug aus der alten Seite ab. Nach dem kostenlosen Check "
              "bekommst du einen Festpreis für den Aufbau und einen Monatsbetrag für den laufenden Betrieb.")),
            ("Warum wird meine Website bei Google nicht gefunden?",
             "Meist aus einem von drei Gründen: Die Seite ist langsam oder am Handy schlecht bedienbar, es fehlen "
             "eigene Seiten für die Leistungen und Orte, nach denen gesucht wird, oder das Google-Unternehmensprofil "
             "ist leer oder veraltet. Im kostenlosen Check sehe ich nach, welcher Grund bei euch zutrifft."),
            ("Warum findet ChatGPT meinen Betrieb nicht?",
             "KI-Assistenten setzen ihre Antworten aus Suchmaschinen, Kartendiensten und Bewertungen zusammen. Ein "
             "Verzeichnis, in das man sich eintragen kann, gibt es nicht. Gemini nutzt vor allem die Google-Suche "
             "und das Google-Unternehmensprofil, ChatGPT und Copilot stützen sich stärker auf die Bing-Suche, Bing "
             "Places und Verzeichnisse wie Yelp oder Foursquare. Wer klare Antworten auf echte "
             "Kundenfragen gibt, überall dieselben Firmendaten führt und auf anderen Seiten erwähnt wird, taucht "
             "häufiger auf. Einen festen Platz in ChatGPT kann niemand versprechen, weil die Antworten bei jeder "
             "Frage anders ausfallen."),
            ("Gestaltest du die Website auch?",
             "Nein, ich gestalte nicht, ich baue. Die Optik kommt aus fertigen, geprüften Vorlagen und "
             "Designsystemen, die ich mit euren Farben und eurem Logo einrichte. Wer eine eigene Gestaltung möchte, "
             "lässt sie von einer Agentur machen, und ich setze sie technisch um."),
            ("Können wir Inhalte der alten Website behalten?",
             "Was taugt, wird übernommen: Texte, Bilder und Adressen, die Google schon kennt. Alte Adressen leite "
             "ich auf die neuen um, damit nichts verloren geht, was heute schon gefunden wird."),
            ("Wer pflegt die Website danach?",
             "Sicherheitsupdates, Datensicherung und kleine technische Änderungen gehören zum laufenden Betrieb. "
             "Neue Seiten oder größere Umbauten vereinbaren wir jeweils extra."),
        ],
    },
    {
        "slug": "e-rechnung", "nav": "E-Rechnung", "group": "ki",
        "title": "E-Rechnung Pflicht 2027/2028: Fristen & Umstellung | Grundke IT",
        "h1": "E-Rechnung: was dein Betrieb bis 2027 und 2028 tun muss",
        "service_type": "Umstellung auf die E-Rechnung für kleine Unternehmen",
        "published": NEW_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "trust": TRUST_FESTPREIS,
        # Kopf der Huelle (Textblatt §1, Task 6); Vertrauenstext steht neben dem Einstieg
        "k": ("Ich prüfe, ob euer Rechnungsprogramm E-Rechnungen kann, suche sonst mit euch ein passendes aus oder "
              "baue den fehlenden Export."),
        "answer": ("Als Grundke IT-Service aus Grasbrunn stelle ich Betriebe im Münchner Osten auf die E-Rechnung um. "
                   "Ausstellen müsst ihr sie für Rechnungen an Unternehmen im Inland ab 2027, wenn euer Gesamtumsatz "
                   "im Vorjahr über 800.000 Euro lag, sonst ab 2028."),
        "proof2": (("ico-check", "Umstellung im Standardfall ab " + eur(PRICES["erechnung"]) + " netto")
                   if SHOW_FROM_PRICES else ("ico-check", "Festpreis nach einem Blick auf eure Rechnungsstrecke")),
        "cta2_href": "/ki-automatisierung/", "cta2_text": "Abläufe automatisieren",
        "offers": ([
            offer_from("E-Rechnung umstellen", PRICES["erechnung"],
                       "Empfang, Ausstellen, Ablage und Weg zur Steuerberatung im Standardfall, einmalig netto."),
            offer_from("E-Rechnung mit eigenem Export", PRICES["erechnung_export"],
                       "Export aus Fachanwendung, Excel-Kalkulation oder Vorsystem, einmalig netto."),
        ] if SHOW_FROM_PRICES else []),
        "desc": ("E-Rechnung empfangen seit 2025, ausstellen ab 2027 oder 2028: Fristen, Ausnahmen, Check in "
                 "drei Fragen und Hilfe bei Programmwahl und Umstellung."),
        "intro": ("Eine E-Rechnung ist ein strukturierter Datensatz, den das Programm des Empfängers direkt "
                  "lesen kann, im Format XRechnung oder ZUGFeRD (ein PDF, in dem die Rechnungsdaten "
                  "zusätzlich als Datei stecken). Ein normales PDF zählt nicht dazu. Empfangen können muss "
                  "sie jedes Unternehmen in Deutschland schon seit Januar 2025. Ausstellen müsst ihr sie je nach "
                  "Umsatz ab 2027 oder 2028. In einer Umfrage von YouGov für den Rechnungsanbieter easybill "
                  "(Juni 2026) hatte ein Drittel der Unternehmen noch nie eine E-Rechnung verschickt, und rund "
                  "jedes fünfte schrieb seine Rechnungen in Word oder Excel. <strong>Für die meisten Betriebe "
                  "ist die Umstellung überschaubar</strong>, wenn sie rechtzeitig passiert."),
        "raw_intro": True,
        "cards_h2": "Was ich dabei mache",
        "cards": [
            ("Programm finden", "Kann euer Rechnungsprogramm keine E-Rechnung, oder gibt es noch gar keins, suche ich mit euch eins aus, das zu Betrieb und Steuerberatung passt.", "ico-search-check"),
            ("Empfang einrichten", "Ein Postfach für E-Rechnungen, die Anzeige der Formate und die Weitergabe an die Buchhaltung.", "ico-mail"),
            ("Ausstellen umstellen", "Euer Programm einrichten oder anpassen, oder einen Export aus eurer Fachanwendung bauen, wenn die Rechnungsdaten von dort kommen.", "ico-file-text"),
            ("Ablage und Steuerberatung", "E-Rechnungen bleiben im Originalformat abgelegt und laufen dorthin, wo eure Steuerberatung sie braucht.", "ico-list"),
        ],
        "extra": """
      <h2>Noch kein Programm, das E-Rechnungen kann?</h2>
      <p>Das ist der häufigste Fall: Rechnungen entstehen in Word oder Excel, in einem älteren Programm ohne XRechnung und ZUGFeRD oder in einer Fachanwendung, die nur ein PDF ausgibt. Dann gehe ich so vor:</p>
      <ul class="lp-checklist">
        <li><strong>Bestandsaufnahme:</strong> Wie schreibt ihr heute Rechnungen, wie kommen Eingangsrechnungen an, mit welchem Programm arbeitet eure Steuerberatung?</li>
        <li><strong>Programm auswählen:</strong> Ich schlage eins vor, das zu Größe und Ablauf passt, und sage dir, was es im Monat kostet. Wo das bisherige Programm reicht, bleibt es.</li>
        <li><strong>Einrichten oder wechseln:</strong> Kunden und Artikel übernehmen, Rechnungsvorlage anpassen, Empfang und Ablage einrichten, die erste E-Rechnung gemeinsam schreiben.</li>
        <li><strong>Anpassen statt neu kaufen:</strong> Kann euer Programm E-Rechnungen nur halb, etwa nur empfangen oder nur ein Format, passe ich es an oder baue den fehlenden Export.</li>
      </ul>

      <h2>Ab wann gilt die E-Rechnungspflicht?</h2>
      <div class="ki-tbl-wrap">
        <table class="ki-tbl">
          <thead><tr><th scope="col">Ab wann</th><th scope="col">Was gilt</th></tr></thead>
          <tbody>
            <tr><td>1. Januar 2025</td><td>Jedes inländische Unternehmen muss E-Rechnungen <strong>empfangen</strong> können. Ein E-Mail-Postfach genügt dafür.</td></tr>
            <tr><td>bis 31. Dezember 2026</td><td>Übergang beim Versand: Papier ist erlaubt, ein einfaches PDF nur mit Zustimmung des Empfängers.</td></tr>
            <tr><td>1. Januar 2027</td><td>Wer 2026 mehr als 800.000 Euro Gesamtumsatz hatte, muss im inländischen B2B-Geschäft E-Rechnungen <strong>ausstellen</strong>. Für alle anderen gilt der Übergang noch bis Ende 2027.</td></tr>
            <tr><td>1. Januar 2028</td><td>Die Pflicht zum Ausstellen gilt für alle übrigen inländischen B2B-Umsätze.</td></tr>
          </tbody>
        </table>
      </div>

      <h2>Betrifft mich das? Drei Fragen</h2>
      <ol class="lp-steps">
        <li><strong>Schreibst du Rechnungen an andere Unternehmen in Deutschland?</strong> Wenn du nur an Privatkunden verkaufst, betrifft dich die Pflicht zum Ausstellen nicht. Empfangen musst du trotzdem können.</li>
        <li><strong>Lag dein Gesamtumsatz 2026 über 800.000 Euro?</strong> Dann musst du ab 1. Januar 2027 ausstellen, sonst ab 1. Januar 2028. Die Zahl kennt deine Steuerberatung.</li>
        <li><strong>Schreibst du Rechnungen heute in Word, Excel oder einem Programm ohne E-Rechnung?</strong> Dann ist jetzt der Zeitpunkt, umzustellen, und nicht im Dezember.</li>
      </ol>
      <p>Vom Ausstellen ausgenommen sind unter anderem Kleinbetragsrechnungen bis 250 Euro brutto, Fahrausweise und Kleinunternehmer. Empfangen können müssen auch sie E-Rechnungen.</p>
<!--split-wide-->
      <div class="ki-note">
        <p><strong>Zur Einordnung:</strong> Das ist die allgemeine Rechtslage nach dem zweiten Schreiben des Bundesfinanzministeriums zur E-Rechnung vom 15. Oktober 2025, das das erste Schreiben von 2024 ersetzt, und keine Steuerberatung. Ob und ab wann die Pflicht deinen Betrieb genau trifft, klärst du mit deiner Steuerberatung. Ich baue die Umsetzung.</p>
      </div>
      {preise}
""".replace("{preise}", (
            '<div class="card-box">\n        <h3>Umstellung zum Festpreis</h3>\n'
            "        <p>Im Standardfall ab " + eur(PRICES["erechnung"]) + " netto: Bestandsaufnahme, Programm "
            "auswählen oder umstellen, Empfang und Ablage einrichten, Weg zur Steuerberatung. Kommen die "
            "Rechnungsdaten aus einer Fachanwendung, einer Excel-Kalkulation oder einem Vorsystem und braucht "
            "es einen eigenen Export, ab " + eur(PRICES["erechnung_export"]) + " netto. Die Lizenz für das "
            "Rechnungsprogramm zahlt ihr direkt beim Anbieter. Ab 4.000 Euro Ausgaben kann der "
            '<a href="/digitalbonus-bayern/">Digitalbonus Bayern</a> bis zur Hälfte übernehmen.</p>\n'
            '        <div class="card-cta">\n'
            '          <a href="tel:+491782584438" class="btn-p">Umstellung besprechen</a>\n'
            '          <a href="/kontakt/" class="btn-g">Lieber schreiben</a>\n        </div>\n      </div>')
            if SHOW_FROM_PRICES else ""),
        "faqs": [
            ("Ab wann gilt die E-Rechnungspflicht?",
             "Empfangen können müssen alle Unternehmen in Deutschland E-Rechnungen seit dem 1. Januar 2025. "
             "Ausstellen müssen sie Betriebe mit mehr als 800.000 Euro Gesamtumsatz im Vorjahr ab dem 1. Januar "
             "2027, alle übrigen ab dem 1. Januar 2028. Das gilt für Rechnungen an andere Unternehmen im Inland."),
            ("Ist ein PDF per E-Mail eine E-Rechnung?",
             "Nur, wenn die Rechnungsdaten nach der europäischen Norm EN 16931 darin stecken, wie bei ZUGFeRD. "
             "Ein normales PDF gilt als sonstige Rechnung. Mit Zustimmung des Empfängers ist es bis Ende 2026 "
             "erlaubt, für Betriebe bis 800.000 Euro Vorjahresumsatz noch bis Ende 2027."),
            ("Gilt die E-Rechnungspflicht für Kleinunternehmer?",
             "Ausstellen müssen Kleinunternehmer keine E-Rechnungen, sie dürfen weiter Papier oder PDF "
             "verschicken. Empfangen können müssen sie E-Rechnungen trotzdem, wie jedes andere Unternehmen. "
             "Dasselbe gilt für Kleinbetragsrechnungen bis 250 Euro brutto."),
            ("Mein Rechnungsprogramm kann keine E-Rechnung. Was jetzt?",
             "Es gibt drei Wege: das Programm aktualisieren, wenn der Anbieter die Funktion nachliefert, ein "
             "anderes Programm einführen oder einen Export bauen, der aus euren vorhandenen Daten eine "
             "E-Rechnung erzeugt. Welcher passt, klären wir in der Bestandsaufnahme. Beim Wechsel übernehme ich "
             "Kunden und Artikel und richte Vorlage, Empfang und Ablage ein."),
            ("Wie empfange ich E-Rechnungen, ohne neue Software zu kaufen?",
             "Für den Empfang reicht ein E-Mail-Postfach. Viele Buchhaltungsprogramme lesen E-Rechnungen schon "
             "ein, und für die Anzeige gibt es kostenlose Programme. Wichtig ist, dass die Datei im Originalformat "
             "abgelegt wird und nicht nur ein Ausdruck."),
            ("Was kostet die Umstellung?",
             ("Im Standardfall ab " + eur_txt(PRICES["erechnung"]) + " netto, mit eigenem Export aus einer Fachanwendung ab " + eur_txt(PRICES["erechnung_export"]) + ". "
              "Die Lizenz für ein Rechnungsprogramm zahlt ihr direkt beim Anbieter. Den Festpreis bekommst du "
              "nach einem kurzen Blick auf eure Rechnungsstrecke.")
             if SHOW_FROM_PRICES else
             ("Das hängt davon ab, woher eure Rechnungsdaten kommen. Nach einem kurzen Blick auf die "
              "Rechnungsstrecke bekommst du einen Festpreis.")),
        ],
    },
    {
        "slug": "digitalbonus-bayern", "nav": "Digitalbonus Bayern", "group": "ki",
        "title": "Digitalbonus Bayern: Antrag & Voraussetzungen | Grundke IT",
        "h1": "Digitalbonus Bayern: bis zur Hälfte zurück für Software und IT-Sicherheit",
        "service_type": "Umsetzung förderfähiger Digitalisierungs- und IT-Sicherheitsprojekte",
        "published": NEW_DATE, "modified": "2026-10-10", "modified_disp": "10. Oktober 2026",
        "cta2_href": "/software-nach-mass/", "cta2_text": "Software nach Maß",
        "desc": ("Digitalbonus Bayern bis Ende 2027: bis zu 50 % Zuschuss ab 4.000 € für Software, KI und "
                 "IT-Sicherheit. Voraussetzungen, Antrag über ELSTER, die Haken."),
        # Kopf der Huelle (Textblatt §1, Task 6); Darstellung: Ablauf und passende Projekte als Zeile
        "k": ("Ich liefere Projektbeschreibung und Kostenaufstellung für euren Antrag, den ihr selbst über ELSTER "
              "stellt."),
        "answer": ("Als Grundke IT-Service aus Grasbrunn setze ich für Betriebe im Münchner Osten Projekte um, die der "
                   "Digitalbonus Bayern fördern kann: bis zu 50 Prozent der förderfähigen Ausgaben ab 4.000 Euro, im "
                   "Standard bis 7.500 Euro Zuschuss, Anträge bis Ende 2027."),
        "proof2": ("ico-file-text", "Unterlagen für Antrag und Verwendungsnachweis"),
        "row": ("So läuft es mit mir", "Welche Projekte passen"),
        "intro": ("Der Digitalbonus Bayern ist ein Zuschuss des Freistaats für kleine gewerbliche Unternehmen. "
                  "Gefördert werden Leistungen externer Anbieter: Software, die für euren Betrieb gebaut oder "
                  "eingeführt wird, KI-Anwendungen und Maßnahmen für die IT-Sicherheit, dort sogar Hardware "
                  "wie Firewall und Datensicherung. <strong>Für viele Projekte heißt das: bis zu 50 Prozent "
                  "zurück.</strong> Es gibt aber Regeln, an denen die Förderung scheitert, wenn man sie nicht "
                  "kennt. Die wichtigsten stehen weiter unten."),
        "raw_intro": True,
        "cards_h2": "Wer was macht",
        "cards": [
            ("Was ich liefere", "Projektbeschreibung, Kostenaufstellung und die technischen Angaben, die ihr für den Antrag braucht.", "ico-file-text"),
            ("Was ihr macht", "Den Antrag über euer ELSTER-Unternehmenskonto stellen und die Eingangsbestätigung abwarten.", "ico-key"),
            ("Zwei Anträge möglich", "Je einer für Digitalisierung und für IT-Sicherheit, zusammen bis zu 15.000 Euro Zuschuss im Standard.", "ico-list"),
            ("Am Ende", "Projekt umsetzen, Rechnung bezahlen, Verwendungsnachweis einreichen. Die Unterlagen dafür bereite ich vor.", "ico-check"),
        ],
        "extra": """
      <h2>Die Eckdaten</h2>
      <div class="ki-tbl-wrap">
        <table class="ki-tbl">
          <thead><tr><th scope="col">Punkt</th><th scope="col">Regel</th></tr></thead>
          <tbody>
            <tr><td>Laufzeit</td><td>bis 31. Dezember 2027, Anträge in monatlichen Kontingenten</td></tr>
            <tr><td>Zuschuss</td><td>bis zu 50 Prozent der förderfähigen Ausgaben, Mindestausgaben 4.000 Euro</td></tr>
            <tr><td>Standard</td><td>höchstens 7.500 Euro Zuschuss</td></tr>
            <tr><td>Plus</td><td>höchstens 30.000 Euro Zuschuss bei besonderem Innovationsgehalt, zum Beispiel KI oder intelligente Datenanalyse; nur einmal je Unternehmen</td></tr>
            <tr><td>Wer</td><td>gewerbliche kleine Unternehmen mit weniger als 50 Beschäftigten, Umsatz oder Bilanzsumme bis 10 Millionen Euro, Betriebsstätte in Bayern</td></tr>
            <tr><td>Was</td><td>Digitalisierung (Software, Abläufe, KI) und IT-Sicherheit (auch Hardware wie Firewall und Datensicherung)</td></tr>
            <tr><td>Antrag</td><td>online über das ELSTER-Unternehmenskonto, an die Bezirksregierung, im Raum München die Regierung von Oberbayern</td></tr>
            <tr><td>Umsetzung</td><td>innerhalb von 18 Monaten nach der Bewilligung</td></tr>
          </tbody>
        </table>
      </div>

      <h2>Die Haken, die du kennen musst</h2>
      <ul class="lp-dont">
        <li><strong>Freie Berufe sind ausgeschlossen</strong>, also zum Beispiel Steuerberatung, Arzt- und Zahnarztpraxen und Architekturbüros. Ebenso Vereine, Medizinische Versorgungszentren und Kliniken sowie Unternehmen mit Beteiligung der öffentlichen Hand.</li>
        <li><strong>Erst der Antrag, dann der Auftrag.</strong> Wer vor der Eingangsbestätigung bestellt oder beauftragt, verliert die Förderung.</li>
        <li><strong>Ihr finanziert vor.</strong> Der Zuschuss kommt erst, wenn der Verwendungsnachweis geprüft ist.</li>
        <li><strong>Kein Rechtsanspruch.</strong> Anträge werden in monatlichen Kontingenten angenommen.</li>
        <li><strong>Standard ist nicht förderfähig:</strong> Standard-Hardware wie PCs und Server, Standard-Software wie Bürosoftware und Betriebssysteme, Standard-Websites und -Shops. Auch reine Ersatzbeschaffungen werden nicht gefördert.</li>
        <li><strong>Beratung und Schulung nur mit Umsetzung.</strong> Sie werden nur zusammen mit einem umgesetzten Projekt gefördert und dürfen höchstens die Hälfte der förderfähigen Ausgaben ausmachen.</li>
        <li><strong>Lizenzen höchstens für 18 Monate.</strong> Lizenz- und Servicegebühren für einen längeren Zeitraum sind nicht förderfähig.</li>
        <li><strong>Drei Jahre Zweckbindung.</strong> Was gefördert wurde, muss ab der Inbetriebnahme drei Jahre im Betrieb genutzt werden.</li>
        <li><strong>Keine Lösungen zum Weiterverkauf.</strong> Lösungen, die gegen Entgelt auch bei anderen Unternehmen eingesetzt werden sollen, schließt die Richtlinie aus. Wo das unklar ist, klären wir es vor dem Antrag schriftlich mit der Bezirksregierung.</li>
        <li><strong>Der Zuschuss ist eine De-minimis-Beihilfe.</strong> Andere De-minimis-Beihilfen der letzten drei Jahre werden darauf angerechnet.</li>
        <li><strong>Das Programm endet am 31. Dezember 2027.</strong> Wer es nutzen will, sollte nicht bis Herbst 2027 warten.</li>
      </ul>

      <h2>So läuft es mit mir</h2>
      <ol class="lp-steps">
        <li><strong>Gespräch:</strong> Wir klären, was gebaut oder abgesichert werden soll und ob euer Betrieb zu den Antragsberechtigten gehört.</li>
        <li><strong>Unterlagen:</strong> Ich schreibe Leistungsbeschreibung und Kostenaufstellung.</li>
        <li><strong>Antrag:</strong> Ihr stellt den Antrag über ELSTER und wartet auf die Eingangsbestätigung.</li>
        <li><strong>Auftrag und Umsetzung:</strong> Erst danach erteilt ihr den Auftrag, und ich setze um.</li>
        <li><strong>Nachweis:</strong> Ihr bezahlt die Rechnung, ich bereite die Unterlagen für den Verwendungsnachweis vor.</li>
      </ol>

      <h2>Welche Projekte passen</h2>
      <p>Gut geeignet sind <a href="/software-nach-mass/">Software nach Maß</a> für einen Ablauf im Betrieb, KI-Anwendungen wie ein Anfragen-Eingang, der Mails und Anrufe sortiert, eine <a href="/e-rechnung/">E-Rechnung</a> mit eigenem Export aus einer Fachanwendung und Projekte für die <a href="/it-sicherheit-backup/">IT-Sicherheit</a> wie Firewall, Datensicherung und Härtung. Eine neue Website allein ist in der Regel nicht förderfähig.</p>

      <div class="ki-note">
        <p><strong>Keine Fördermittel- oder Rechtsberatung.</strong> Ob euer Betrieb und euer Projekt gefördert werden, entscheidet die Bezirksregierung. Ich kenne die Richtlinie und bereite die technischen Unterlagen vor. Maßgeblich ist die Förderrichtlinie in ihrer gültigen Fassung auf <a href="https://www.digitalbonus.bayern/foerderprogramm/" target="_blank" rel="noopener">digitalbonus.bayern</a>.</p>
      </div>
""",
        "faqs": [
            ("Wie viel zahlt der Digitalbonus Bayern?",
             "Bis zu 50 Prozent der förderfähigen Ausgaben, wenn diese mindestens 4.000 Euro betragen. Im Standard "
             "sind es höchstens 7.500 Euro Zuschuss, im Digitalbonus Plus bei besonders innovativen Vorhaben wie "
             "KI höchstens 30.000 Euro. Je Unternehmen ist ein Antrag für Digitalisierung und einer für "
             "IT-Sicherheit möglich."),
            ("Wer kann den Digitalbonus beantragen?",
             "Gewerbliche kleine Unternehmen mit weniger als 50 Beschäftigten und höchstens 10 Millionen Euro "
             "Umsatz oder Bilanzsumme, die in Bayern eine Betriebsstätte haben. Freie Berufe wie Steuerberatung "
             "oder Arztpraxen sind ausgeschlossen, ebenso Vereine, Kliniken und Medizinische Versorgungszentren."),
            ("Darf ich den Auftrag vor dem Antrag erteilen?",
             "Nein. Die Reihenfolge ist: Antrag stellen, Eingangsbestätigung abwarten, dann beauftragen. Eine "
             "Bestellung oder ein Auftrag davor lässt die Förderung entfallen. Wer nach der Eingangsbestätigung "
             "beginnt, tut das auf eigenes Risiko, falls der Antrag später abgelehnt wird."),
            ("Wird eine neue Website gefördert?",
             "In der Regel nicht. Die Richtlinie schließt Standard-Webseiten und -Shops aus. Gefördert werden eher "
             "Anwendungen und Abläufe, die für den Betrieb gebaut werden, und Maßnahmen für die IT-Sicherheit."),
            ("Muss mein IT-Dienstleister dafür zugelassen sein?",
             "Nein. Anders als beim früheren Bundesprogramm go-digital verlangt der Digitalbonus Bayern keine "
             "Autorisierung des Anbieters. Den Antrag stellt das Unternehmen selbst."),
        ],
    },
    # ----------------------------------------------------------------------- #
    #  Ratgeber „Die ersten 15 Minuten": Hub plus je ein Artikel je Suchanlass. #
    #  Liegen unter /ratgeber/<thema>/ (eine Ebene tiefer, siehe up()).         #
    # ----------------------------------------------------------------------- #
    {
        "slug": "ratgeber", "nav": "Ratgeber", "group": "ratgeber", "kind": "ratgeber-hub",
        "title": "Ratgeber IT-Notfall: die ersten 15 Minuten | Grundke IT-Service",
        "h1": "Die ersten 15 Minuten",
        "hero": {
            "accent": "wenn im Betrieb die IT stillsteht",
            "paths_label": "Die Ratgeber",
            "paths": [
                ("Server ausgefallen", "Was du prüfen kannst, bevor du anrufst, und was du lassen solltest.", "/ratgeber/server-ausgefallen/"),
                ("Auf eine Phishing-Mail geklickt", "Nur geklickt, Passwort eingegeben oder Anhang geöffnet: jeweils der nächste Schritt.", "/ratgeber/phishing-mail-geklickt/"),
                ("E-Mails kommen nicht an", "Liegt es am Outlook, am Postfach oder an der Domain?", "/ratgeber/e-mails-kommen-nicht-an/"),
                ("NAS defekt", "Festplatte ausgefallen, Netzwerkspeicher meldet Fehler: so rettest du die Daten.", "/ratgeber/nas-defekt/"),
            ],
        },
        "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "cta2_href": "/fernwartung/", "cta2_text": "Fernwartung starten",
        "desc": ("Server ausgefallen, Phishing-Mail geklickt, E-Mails kommen nicht an, NAS defekt: was du in den "
                 "ersten 15 Minuten selbst tun kannst und wann du anrufst."),
        "lead": "Was du in den ersten Minuten selbst tun kannst, was du besser lässt, und ab wann ein Anruf schneller ist.",
        # H2 des Einstiegs (Design-Review Task 7, Fix-Runde 1): einziger Abschnitt ohne Ueberschrift
        "intro_h2": "So sind die Ratgeber aufgebaut",
        "intro": ("Die meisten Störungen beginnen mit einer Suche nach „… was tun“. Wer in dem Moment das "
                  "Richtige macht, spart oft Stunden, und wer das Falsche macht, verliert manchmal Daten. Jeder "
                  "Ratgeber hier hat denselben Aufbau: zuerst die kurze Antwort, dann die Schritte, die du "
                  "selbst gehen kannst, dann was du lassen solltest und wann es Zeit ist anzurufen."),
        "raw_intro": True,
        "extra": """
      <div class="ki-note">
        <p><strong>Steht bei euch gerade alles still?</strong> Dann lies nicht weiter, sondern ruf an: <a href="tel:+491782584438">0178 258 44 38</a>. Ich arbeite nur für Unternehmen, Vertragskunden werden bevorzugt behandelt. Ad hoc kostet ein Einsatz 110 € netto je Stunde im 15-Minuten-Takt. Wie das abläuft, steht auf der Seite <a href="/it-notdienst/">IT-Notdienst</a>.</p>
      </div>
""",
        "faqs": [
            ("Kann ich IT-Probleme per Fernwartung lösen lassen?",
             "Oft ja. Solange der betroffene Rechner startet und ins Internet kommt, verbinde ich mich nach deiner "
             "Freigabe per Fernwartung und du siehst alles mit. Ist ein Server oder das Netzwerk ganz weg, braucht "
             "es meist einen Termin vor Ort."),
            ("Hilfst du auch, wenn ich kein Vertragskunde bin?",
             "Ja, für Unternehmen. Ad hoc rechne ich 110 Euro netto je Stunde im 15-Minuten-Takt ab. "
             "Vertragskunden werden bevorzugt behandelt, deshalb kann es bei Neukunden etwas dauern."),
        ],
    },
    {
        "slug": "ratgeber/server-ausgefallen", "nav": "Server ausgefallen", "group": "ratgeber", "kind": "ratgeber",
        "title": "Server ausgefallen – was tun? Die ersten 15 Minuten | Grundke IT",
        "h1": "Server ausgefallen: was tun in den ersten 15 Minuten?",
        "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "cta2_href": "/fernwartung/", "cta2_text": "Fernwartung starten",
        "desc": ("Server ausgefallen, keiner kommt an die Daten? Was du in den ersten 15 Minuten prüfen kannst, "
                 "was du auf keinen Fall tun solltest und wann du anrufen solltest."),
        "lead": "Erst schauen, dann handeln. Die meisten Ausfälle lassen sich eingrenzen, bevor jemand kommt.",
        "intro": ("<div class=\"lp-answer\"><p>Kurz gesagt: Prüfe zuerst, ob wirklich der Server ausgefallen ist "
                  "oder nur die Verbindung dorthin. Sieh dir Lämpchen und Bildschirm an und fotografiere jede "
                  "Meldung. Ein einziger sauberer Neustart ist in Ordnung, mehrfaches Aus- und Einschalten nicht. "
                  "Erscheint eine Erpressermeldung, zieh das Netzwerkkabel, lass den Server eingeschaltet und ruf "
                  "an.</p></div>"),
        "raw_intro": True,
        "extra": """
      <h2>Die ersten 15 Minuten</h2>
      <ol class="lp-steps">
        <li><strong>Eingrenzen:</strong> Kommt keiner mehr an die Daten oder nur ein Rechner? Wenn nur ein Rechner betroffen ist, liegt es oft an diesem Rechner oder an seinem Netzwerkkabel, nicht am Server.</li>
        <li><strong>Hinsehen statt neu starten:</strong> Laufen Lüfter und Lämpchen? Steht etwas auf dem Bildschirm, falls einer angeschlossen ist? Leuchtet an einer Festplatte etwas rot oder orange? Fotografiere alles, was du siehst.</li>
        <li><strong>Strom und Netzwerk prüfen:</strong> Steckt der Stecker, ist die Steckerleiste an, piept die unterbrechungsfreie Stromversorgung? Stecken die Netzwerkkabel am Server und am Switch, und blinken dort die Lämpchen?</li>
        <li><strong>Einmal sauber neu starten</strong>, aber nur, wenn nichts piept, keine Festplatte rot leuchtet und keine Erpressermeldung zu sehen ist. Sauber heißt: über das Startmenü, oder den Einschaltknopf kurz drücken und warten, bis der Server von selbst herunterfährt. Nicht den Stecker ziehen und den Knopf nicht lange gedrückt halten. Danach nicht noch einmal.</li>
        <li><strong>Verdacht auf Verschlüsselung:</strong> Dateien mit seltsamen Endungen oder eine Textdatei mit Lösegeldforderung? Netzwerkkabel ziehen, Server eingeschaltet lassen, sofort anrufen.</li>
      </ol>

      <h2>Was du lassen solltest</h2>
      <ul class="lp-dont">
        <li>Festplatten herausziehen, tauschen oder umstecken.</li>
        <li>Den Server neu einrichten oder „reparieren lassen“, wenn er das anbietet.</li>
        <li>Datenrettungsprogramme aus dem Internet auf dem Server laufen lassen.</li>
        <li>Lösegeld zahlen oder mit den Erpressern Kontakt aufnehmen.</li>
      </ul>

      <h2>Wann du anrufen solltest</h2>
      <p>Wenn der Server nach den Schritten oben nicht in wenigen Minuten wieder erreichbar ist, wenn eine Festplatte einen Fehler meldet oder wenn auch nur der Verdacht auf Verschlüsselung besteht. Halte die Fotos bereit, das spart am Telefon viel Zeit. Ob ich mich per Fernwartung verbinden kann oder vorbeikomme, entscheiden wir dann zusammen.</p>
      <div class="ki-note">
        <p><strong>Bei Verdacht auf Verschlüsselung</strong> können Kunden- oder Mitarbeiterdaten betroffen sein. Dann kann eine Meldung an die Datenschutzaufsicht innerhalb von 72 Stunden nötig sein (Art. 33 DSGVO). Das klärst du mit deinem Datenschutzbeauftragten oder Anwalt; ich helfe, die technischen Spuren dafür zu sichern.</p>
      </div>
      <p>Damit ein Ausfall gar nicht erst zum Datenverlust wird, braucht es eine Datensicherung, die regelmäßig getestet wird. Mehr dazu auf der Seite <a href="/it-sicherheit-backup/">IT-Sicherheit &amp; Backup</a>.</p>
""",
        "faqs": [
            ("Wie schnell läuft ein ausgefallener Server wieder?",
             "Das hängt von der Ursache ab. Ein loses Kabel oder ein hängender Dienst ist in Minuten behoben, eine "
             "defekte Festplatte in einem gespiegelten System in Stunden. Fällt der ganze Server aus, entscheidet "
             "die Datensicherung: Mit einer getesteten Sicherung ist die Wiederherstellung planbar, ohne braucht "
             "es oft eine Datenrettung, und die dauert."),
            ("Kann ein Server-Problem per Fernwartung gelöst werden?",
             "Wenn der Server läuft und im Netzwerk erreichbar ist, oft ja. Ist er ganz aus oder hängt er beim "
             "Starten, muss jemand vor Ort hinsehen."),
            ("Was kostet ein Einsatz bei einem Serverausfall?",
             "Ad hoc 110 Euro netto je Stunde im 15-Minuten-Takt, ohne Zuschlag für Abend oder Wochenende. "
             "Vor Ort ist die Anfahrt bis 5 km inklusive, darüber gilt eine vereinbarte Pauschale. Vertragskunden "
             "werden bevorzugt behandelt."),
        ],
    },
    {
        "slug": "ratgeber/phishing-mail-geklickt", "nav": "Phishing-Mail geklickt", "group": "ratgeber", "kind": "ratgeber",
        "title": "Auf Phishing-Mail geklickt – was tun? | Grundke IT-Service",
        "h1": "Auf eine Phishing-Mail geklickt: was jetzt zu tun ist",
        "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "cta2_href": "/schulung/", "cta2_text": "Schulung für dein Team",
        "desc": ("Auf eine Phishing-Mail geklickt, Passwort eingegeben oder Anhang geöffnet? Was in den ersten "
                 "15 Minuten zu tun ist, je nachdem was passiert ist."),
        "lead": "Ruhe bewahren hilft mehr als Löschen. Was zu tun ist, hängt davon ab, was nach dem Klick passiert ist.",
        "intro": ("<div class=\"lp-answer\"><p>Kurz gesagt: Nichts mehr eingeben und das Fenster schließen. Hast "
                  "du nur geklickt, ist meist nichts passiert. Hast du ein Passwort eingegeben, ändere es sofort "
                  "von einem anderen Gerät aus. Hast du einen Anhang geöffnet, trenne den Rechner vom Netzwerk, "
                  "lass ihn eingeschaltet und ruf an.</p></div>"),
        "raw_intro": True,
        "extra": """
      <h2>Die ersten 15 Minuten</h2>
      <ol class="lp-steps">
        <li><strong>Nichts mehr eingeben</strong> und die Seite oder das Fenster schließen.</li>
        <li><strong>Überlegen, was passiert ist</strong>, und dem passenden Abschnitt unten folgen: nur geklickt, Zugangsdaten eingegeben oder Anhang geöffnet.</li>
        <li><strong>Die Mail nicht löschen</strong> und nicht beantworten. Weiterleiten nur, wenn dein IT-Betreuer darum bittet, und dann als Anlage. Mach einen Screenshot, sie ist der Beleg.</li>
        <li><strong>Bescheid geben:</strong> deinem IT-Betreuer und, wenn Bank- oder Kartendaten betroffen sind, sofort der Bank. Karten sperrst du über den Sperr-Notruf 116 116.</li>
        <li><strong>Kollegen warnen</strong>, falls dieselbe Mail an mehrere ging.</li>
      </ol>

      <h3>Nur geklickt, nichts eingegeben</h3>
      <p>Meistens ist dann nichts passiert. Schließ den Browser, lass einen Virenscan laufen und gib deinem IT-Betreuer Bescheid. Selten nutzen solche Seiten eine Lücke im Browser aus, deshalb sollte der Browser immer aktuell sein.</p>

      <h3>Passwort oder Zugangsdaten eingegeben</h3>
      <p>Ändere das Passwort sofort, und zwar von einem anderen Gerät aus, außerdem überall dort, wo du dasselbe Passwort benutzt. Bei Microsoft 365 sollten danach alle angemeldeten Sitzungen beendet und die Postfachregeln geprüft werden: Angreifer richten gern eine heimliche Weiterleitung ein. Prüfe auch, ob für die Zwei-Faktor-Anmeldung eine fremde Authenticator-App oder Telefonnummer eingetragen wurde. Ist die Zwei-Faktor-Anmeldung noch nicht eingerichtet, ist jetzt der Zeitpunkt.</p>

      <h3>Anhang geöffnet oder Programm ausgeführt</h3>
      <p>Trenne den Rechner vom Netzwerk: WLAN ausschalten, Netzwerkkabel ziehen. Lass ihn eingeschaltet, damit Spuren erhalten bleiben, und ruf an. Melde dich an diesem Rechner nicht mehr bei anderen Diensten an.</p>

      <h2>Was du lassen solltest</h2>
      <ul class="lp-dont">
        <li>Die Mail löschen und hoffen, dass nichts war.</li>
        <li>Das Passwort vom selben, möglicherweise befallenen Rechner aus ändern.</li>
        <li>Den Rechner ausschalten und am nächsten Tag weiterarbeiten, als wäre nichts gewesen.</li>
        <li>Aus Scham niemandem Bescheid geben. Ein früher Hinweis begrenzt den Schaden.</li>
      </ul>

      <h2>Wann du anrufen solltest</h2>
      <p>Sobald Zugangsdaten eingegeben oder ein Anhang geöffnet wurde, und immer dann, wenn du dir nicht sicher bist. Merkst du, dass aus deinem Postfach Mails verschickt wurden, die du nicht geschrieben hast, ist das Konto wahrscheinlich übernommen.</p>
      <div class="ki-note">
        <p><strong>Wenn Kundendaten betroffen sein können:</strong> Dann kann eine Meldung an die Datenschutzaufsicht innerhalb von 72 Stunden nötig sein (Art. 33 DSGVO). Ist Geld geflossen oder wurden Daten abgegriffen, kommt eine Anzeige bei der Polizei in Frage, in Bayern auch online. Beides klärst du mit deinem Datenschutzbeauftragten oder Anwalt; ich helfe, die technischen Spuren dafür zu sichern.</p>
      </div>
      <p>Die beste Vorbeugung ist ein Team, das Phishing erkennt. Dafür gibt es die <a href="/schulung/">IT-Sicherheitsschulung</a>.</p>
""",
        "faqs": [
            ("Ich habe auf einen Phishing-Link geklickt, aber nichts eingegeben. Bin ich gehackt?",
             "Meistens nicht. Gefährlich wird es in der Regel erst, wenn Zugangsdaten eingegeben oder Dateien "
             "geöffnet werden. Schließ den Browser, lass einen Virenscan laufen und gib deinem IT-Betreuer "
             "Bescheid. Halte Browser und Betriebssystem aktuell, damit seltene Angriffe über Sicherheitslücken "
             "ins Leere laufen."),
            ("Woran erkenne ich, dass mein E-Mail-Konto gehackt wurde?",
             "Typische Zeichen sind Mails im Gesendet-Ordner, die du nicht geschrieben hast, neue Weiterleitungs- "
             "oder Löschregeln, Hinweise auf Anmeldungen von fremden Orten und Kontakte, die seltsame Mails von "
             "dir bekommen. Dann sofort das Passwort von einem anderen Gerät aus ändern und alle Sitzungen beenden."),
            ("Muss ich einen Phishing-Vorfall melden?",
             "Wenn personenbezogene Daten von Kunden oder Mitarbeitenden betroffen sein können, kann eine Meldung an "
             "die Datenschutzaufsicht innerhalb von 72 Stunden nötig sein. Ob das in deinem Fall gilt, ist eine "
             "rechtliche Frage für deinen Datenschutzbeauftragten oder Anwalt."),
        ],
    },
    {
        "slug": "ratgeber/e-mails-kommen-nicht-an", "nav": "E-Mails kommen nicht an", "group": "ratgeber", "kind": "ratgeber",
        "title": "E-Mails kommen nicht an – was tun? | Grundke IT-Service",
        "h1": "E-Mails kommen nicht an: woran es liegt und was du tun kannst",
        "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "cta2_href": "/microsoft-365-betreuung/", "cta2_text": "Microsoft 365 Betreuung",
        "desc": ("E-Mails kommen nicht an oder landen beim Empfänger im Spam? So grenzt du in 15 Minuten ein, "
                 "ob es an Outlook, am Postfach oder an der Domain liegt."),
        "lead": "Erst klären, ob keine Mails hereinkommen oder ob deine nicht ankommen. Das sind zwei verschiedene Probleme.",
        "intro": ("<div class=\"lp-answer\"><p>Kurz gesagt: Melde dich im Browser am Postfach an, bei Microsoft 365 "
                  "unter outlook.office.com. Sind die Mails dort, liegt es am Outlook auf dem Rechner. Prüfe "
                  "Spam-Ordner, Quarantäne und den Speicherplatz. Kommen deine Mails beim Empfänger nicht an, lies "
                  "die Rückmeldung, die zurückkommt: Der Grund steht meist darin.</p></div>"),
        "raw_intro": True,
        "extra": """
      <h2>Die ersten 15 Minuten</h2>
      <ol class="lp-steps">
        <li><strong>Im Browser nachsehen:</strong> Melde dich direkt beim Postfach an, bei Microsoft 365 unter outlook.office.com. Sind die Mails dort zu sehen, liegt das Problem beim Outlook auf dem Rechner und nicht beim Postfach.</li>
        <li><strong>Spam, Junk und Quarantäne prüfen:</strong> Verdächtige Mails landen nicht immer im Junk-Ordner, sondern bei Microsoft 365 auch in einer Quarantäne, die nur der Administrator vollständig sieht.</li>
        <li><strong>Speicherplatz prüfen:</strong> Ist das Postfach voll, werden neue Mails abgewiesen.</li>
        <li><strong>Rückmeldung lesen:</strong> Kommt auf eine verschickte Mail eine Unzustellbarkeitsnachricht zurück, steht der Grund meist darin, oft mit einem Code wie 550 5.7.1. Leite sie deinem IT-Betreuer weiter.</li>
        <li><strong>Betrifft es alle im Betrieb?</strong> Dann liegt es meist an Domain oder Mailserver: Ist die Rechnung für die Domain bezahlt? Wurde kürzlich die Website umgezogen und dabei an den DNS-Einträgen etwas geändert?</li>
      </ol>

      <h2>Wenn deine Mails beim Empfänger im Spam landen</h2>
      <p>Große Anbieter wie Gmail prüfen inzwischen streng, ob eine Mail wirklich von der Domain stammt, die als Absender drinsteht. Dafür gibt es drei Einträge in den DNS-Einstellungen der Domain: SPF sagt, welche Server für die Domain senden dürfen, DKIM unterschreibt die Mail, DMARC legt fest, was mit Mails passiert, die beides nicht bestehen. Fehlen die Einträge oder sind sie falsch, landen Mails im Spam oder werden abgewiesen. Das lässt sich prüfen und meist in kurzer Zeit richten.</p>

      <h2>Was du lassen solltest</h2>
      <ul class="lp-dont">
        <li>Das Postfach in Outlook entfernen und neu einrichten, bevor geklärt ist, ob die Mails im Browser da sind.</li>
        <li>DNS-Einträge beim Anbieter ändern, ohne zu wissen, wofür sie da sind.</li>
        <li>Wichtige Mails an eine private Adresse umleiten, „bis es wieder geht“.</li>
      </ul>

      <h2>Wann du anrufen solltest</h2>
      <p>Wenn im Browser ebenfalls keine Mails ankommen, wenn alle im Betrieb betroffen sind oder wenn Rückmeldungen mit Fehlercodes kommen. Leg die Unzustellbarkeitsnachricht bereit, damit lässt sich die Ursache meist schnell finden.</p>
""",
        "faqs": [
            ("Warum landen meine E-Mails beim Empfänger im Spam?",
             "Meist fehlen oder stimmen die Einträge SPF, DKIM und DMARC für die eigene Domain nicht, mit denen "
             "Empfänger prüfen, ob eine Mail echt ist. Andere Gründe sind eine Absenderadresse auf einer Sperrliste "
             "oder Inhalte, die wie Werbung aussehen. Die DNS-Einträge lassen sich prüfen und richten."),
            ("Was bedeuten SPF, DKIM und DMARC?",
             "Drei Einträge in den DNS-Einstellungen der Domain. SPF nennt die Server, die für die Domain senden "
             "dürfen. DKIM unterschreibt jede Mail digital. DMARC sagt dem Empfänger, wie er mit Mails umgehen "
             "soll, die diese Prüfungen nicht bestehen."),
            ("Kommen Mails verloren, solange das Problem besteht?",
             "Meist nicht sofort. Ein sendender Server versucht es bei vielen Fehlern über Stunden bis Tage "
             "weiter. Bei einem vollen Postfach oder einer abgelaufenen Domain werden Mails aber abgewiesen, und "
             "der Absender bekommt eine Fehlermeldung."),
        ],
    },
    {
        "slug": "ratgeber/nas-defekt", "nav": "NAS defekt", "group": "ratgeber", "kind": "ratgeber",
        "title": "NAS defekt – Daten retten: die ersten Schritte | Grundke IT",
        "h1": "NAS defekt: so rettest du die Daten",
        "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "cta2_href": "/it-sicherheit-backup/", "cta2_text": "Backup richtig aufsetzen",
        "desc": ("Netzwerkspeicher meldet eine defekte Festplatte oder startet nicht mehr? Was du in den ersten 15 "
                 "Minuten tun kannst, damit die Daten nicht verloren gehen."),
        "lead": "Eine defekte Festplatte im NAS ist meist kein Datenverlust. Dazu wird sie erst durch die falschen Handgriffe danach.",
        "intro": ("<div class=\"lp-answer\"><p>Kurz gesagt: Lies zuerst, was das NAS meldet. „Beeinträchtigt“ "
                  "heißt, eine Platte ist ausgefallen, die Daten sind noch da. Sichere dann sofort die wichtigsten "
                  "Daten, bevor du irgendetwas tauschst. Tausch nur die Platte, die als defekt markiert ist. Meldet "
                  "das NAS „abgestürzt“ oder fallen zwei Platten aus, fass nichts mehr an und ruf an. Muss es aus, dann "
                  "über die Oberfläche herunterfahren, nicht am Stecker.</p></div>"),
        "raw_intro": True,
        "extra": """
      <h2>Die ersten 15 Minuten</h2>
      <ol class="lp-steps">
        <li><strong>Lesen, was das NAS meldet:</strong> Lämpchen am Gerät und die Oberfläche im Browser, bei Synology etwa der Speicher-Manager. „Beeinträchtigt“ heißt: Eine Platte ist ausgefallen, die Daten sind noch lesbar, aber mit weniger oder ohne Reserve. „Abgestürzt“ heißt: nichts mehr anfassen. Steckt nur eine Platte im NAS oder läuft es als RAID 0, gibt es gar keine Reserve; dann ist schon der erste Plattenfehler ein Fall für den Anruf.</li>
        <li><strong>Sofort sichern, was wichtig ist:</strong> Solange der Zugriff noch geht, kopiere die wichtigsten Daten auf eine externe Festplatte, bevor irgendetwas getauscht wird. Prüfe, wann die letzte Sicherung außer Haus gelaufen ist.</li>
        <li><strong>Nichts umstecken:</strong> Keine Platte ziehen, die nicht als defekt markiert ist, und die Reihenfolge der Platten nicht verändern.</li>
        <li><strong>Die richtige Ersatzplatte besorgen:</strong> gleiche oder größere Kapazität, möglichst dieselbe Bauart und eine Platte, die für den Dauerbetrieb im NAS gedacht ist. Am sichersten eine aus der Kompatibilitätsliste des Herstellers und keine SMR-Platte, die beim Wiederaufbau sehr langsam wird.</li>
        <li><strong>Tauschen nach Anleitung des Herstellers:</strong> Danach baut das NAS den Verbund neu auf. Das kann viele Stunden dauern; in der Zeit das Gerät nicht neu starten und möglichst wenig belasten.</li>
      </ol>

      <h2>Was du lassen solltest</h2>
      <ul class="lp-dont">
        <li>„Initialisieren“, „Formatieren“ oder „Neu einrichten“ bestätigen, wenn das NAS danach fragt.</li>
        <li>Die Platten in einen PC stecken, um nachzusehen, was drauf ist.</li>
        <li>Reparaturprogramme aus dem Internet ausführen oder das NAS immer wieder neu starten. Die Funktion „Reparieren“ im Speicher-Manager nach dem Plattentausch ist dagegen genau der richtige Schritt.</li>
        <li>Bei zwei ausgefallenen Platten selbst weitermachen. Jeder eigene Versuch kann eine Datenrettung im Labor erschweren.</li>
      </ul>

      <h2>Wann du anrufen solltest</h2>
      <p>Wenn das NAS „abgestürzt“ meldet, gar nicht mehr startet, zwei Platten gleichzeitig Fehler zeigen oder du dir beim Tausch nicht sicher bist. Mach vorher Fotos von den Lämpchen und Screenshots der Meldungen.</p>
      <div class="ki-note">
        <p><strong>Ein RAID ist keine Datensicherung.</strong> Es schützt vor dem Ausfall einer Platte, nicht vor Löschen, Verschlüsselung, Diebstahl oder Brand. Dafür braucht es eine Kopie außer Haus, die regelmäßig getestet wird. Mehr dazu auf der Seite <a href="/it-sicherheit-backup/">IT-Sicherheit &amp; Backup</a>.</p>
      </div>
""",
        "faqs": [
            ("Ist ein RAID im NAS ein Backup?",
             "Nein. Ein RAID verteilt die Daten so auf mehrere Platten, dass der Ausfall einer Platte überstanden "
             "wird. Gegen versehentliches Löschen, Verschlüsselung durch Schadsoftware, Diebstahl oder einen "
             "Wasserschaden hilft es nicht. Dafür braucht es eine getrennte Sicherung, am besten mit einer Kopie "
             "außer Haus."),
            ("Kann ich die defekte Festplatte im NAS selbst tauschen?",
             "Wenn das NAS „beeinträchtigt“ meldet, genau eine Platte als defekt markiert ist und die wichtigsten "
             "Daten vorher gesichert sind, meist ja, nach Anleitung des Herstellers. Unterstützt das Gerät keinen "
             "Tausch im laufenden Betrieb, vorher sauber herunterfahren. Bei mehr als einer defekten Platte nicht."),
            ("Was kostet eine Datenrettung?",
             "Das hängt vom Schaden ab und lässt sich erst nach einer Diagnose sagen. Logische Fehler sind meist "
             "günstiger zu beheben als mechanische Schäden, die ein Labor braucht. Je weniger vorher selbst "
             "versucht wurde, desto besser stehen die Chancen."),
        ],
    },
]


def related_html(slug, services):
    """Querverweise am Seitenende: KI-Unterseiten zum Hub und untereinander, Ratgeber untereinander."""
    if slug.startswith("ki-") and slug != KI_HUB[1]:
        # Rueckweg zum Hub und Querverweise zwischen den KI-Bereichen
        siblings = [sv for sv in services if sv["slug"].startswith("ki-")
                    and sv["slug"] not in (slug, KI_HUB[1])]
        links = " und ".join('<a href="/{s}/">{n}</a>'.format(s=sv["slug"], n=esc(sv["nav"])) for sv in siblings)
        return ('<p class="lp-related">Mehr aus dem Bereich <a href="/{hub}/">{hubn}</a>: '
                '{links}.</p>').format(hub=KI_HUB[1], hubn=esc(KI_HUB[0]), links=links)
    if slug.startswith(RATGEBER_HUB[1] + "/"):
        siblings = [sv for sv in services if sv["slug"].startswith(RATGEBER_HUB[1] + "/")
                    and sv["slug"] != slug]
        links = ", ".join('<a href="/{s}/">{n}</a>'.format(s=sv["slug"], n=esc(sv["nav"])) for sv in siblings)
        return ('<p class="lp-related">Weitere Ratgeber aus der Reihe <a href="/{hub}/">Die ersten '
                '15 Minuten</a>: {links}.</p>').format(hub=RATGEBER_HUB[1], links=links)
    return ""


# meta_extra eines SERVICES-Eintrags (Task 8): og:title, og:description, og:image:alt, twitter:description,
# twitter:image:alt (head: og_title/og_desc/og_alt/tw_desc/tw_alt)
META_EXTRA_KEYS = {"og_title", "og_desc", "og_alt", "tw_desc", "tw_alt"}


def service_head_schema(s):
    """<head> und JSON-LD einer Leistungsseite (gemeinsam fuer bisherige Huelle und render_shell)."""
    slug = s["slug"]
    # Voller Titel fuer OG und Schema: beim Hub steht der zweite Teil als Akzentzeile
    # im Einstieg, inhaltlich bleibt die Ueberschrift dieselbe wie vorher. "name" (Task 8): eigener Name ohne
    # Tags, wenn die H1 Markup traegt (schulung: <br>).
    h1_full = s["name"] if s.get("name") else (
        s["h1"] + " – " + s["hero"]["accent"] if s.get("hero") else s["h1"]).replace("&amp;", "&")
    # meta_extra (Task 8): og/twitter-Werte, die von der Regel abweichen (schulung: Werte der frueheren Handseite)
    mx = s.get("meta_extra", {})
    if set(mx) - META_EXTRA_KEYS:
        raise SystemExit("service_head_schema: unbekannte meta_extra-Felder "
                         + ", ".join(sorted(set(mx) - META_EXTRA_KEYS)) + " auf " + slug)
    og_title = mx.get("og_title", h1_full + " – Andreas Grundke IT-Service")
    h = head(s["title"], s["desc"], slug, og_title, mx.get("og_desc", s["desc"]),
             mx.get("og_alt", h1_full + " – Andreas Grundke IT-Service"), mx.get("tw_desc"), mx.get("tw_alt"))

    service_schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": s["service_type"],
        "name": h1_full,
        "description": s["desc"],
        "provider": {"@id": BUSINESS_ID},
        "areaServed": [{"@type": "City", "name": n} for n in
                       ["Grasbrunn", "Vaterstetten", "Haar", "Ottobrunn", "München"]],
    }
    if s.get("offers"):
        service_schema["offers"] = [
            o if isinstance(o, dict) else
            {"@type": "Offer", "name": o[0], "price": o[1], "priceCurrency": "EUR", "description": o[2]}
            for o in s["offers"]]
    if s.get("kind") == "ratgeber":
        # Ratgeber-Artikel: Article statt Service, Autor und Herausgeber wie auf allen Seiten
        main_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": h1_full,
            "description": s["desc"],
            "inLanguage": "de-DE",
            "mainEntityOfPage": DOMAIN + "/" + slug + "/",
            "datePublished": s.get("published", NEW_DATE),
            "dateModified": s.get("modified", NEW_DATE),
            "author": {"@type": "Person", "@id": PERSON_ID, "name": "Andreas Grundke", "url": DOMAIN + "/"},
            "publisher": {"@type": "Organization", "@id": BUSINESS_ID, "name": "Andreas Grundke IT-Service"},
            "image": DOMAIN + "/assets/img/og-image.png",
        }
    elif s.get("kind") == "ratgeber-hub":
        main_schema = None
    else:
        main_schema = service_schema
    schema = [breadcrumb(s["nav"], slug)] + ([main_schema] if main_schema else []) + [
              faq_schema(s["faqs"]),
              webpage_schema(s["title"], s["desc"], slug,
                             s.get("published"), s.get("modified"))]
    # Optionale Zusatzknoten (z. B. der kostenlose KI-Potenzialcheck als eigener Service)
    schema.extend(s.get("extra_schema", []))
    return h, schema


def render_service(s, places, services):
    """Leistungs-, KI- und Ratgeberseite: seit Task 7 alle in der Huelle (render_shell)."""
    return s["slug"], render_shell(s, places, services)


# --------------------------------------------------------------------------- #
#  Startseite: Kundenstimmen, FAQ, WhatsApp, Preise (sync_home, seit 10.10.2026) #
# --------------------------------------------------------------------------- #
# REVIEWS: Kundenstimmen woertlich und ungekuerzt (Regel kundenstimmen-quellen), einzige Quelle
# fuer die Karten der Startseite und fuer review[]/reviewBody/reviewCount im Schema; Unterseiten
# holen ihre Stimmen ab Release B ebenfalls hier. source: "Google-Bewertung" oder "direkt" (die
# Karte zeigt dann Rolle + "direkt übermittelt", nie "Google"). Per Skript aus index.html
# (Stand 83f8e74) uebernommen, nicht abgetippt.
# HOME_FAQS: (Frage, Antwort-HTML) der Startseite, Reihenfolge laut Textblatt. Sichtbares
# Akkordeon und FAQPage-Schema (Antwort ohne Tags) kommen aus dieser Liste; die ersten
# HOME_FAQ_SHOWN stehen in der Liste, der Rest unter "Weitere Fragen" (im HTML, ohne JS lesbar).
REVIEWS = [
    {
        'id': 'bauer',
        'name': 'Apartments Bauer',
        'who': 'Apartments Bauer',
        'role': '',
        'source': 'Google-Bewertung',
        'author_type': 'Organization',
        'paragraphs': [
            'Andy hat das WLAN in unserem Haus modernisiert und auf Ubiquiti umgestellt, damit unsere Gäste eine bessere Internetverbindung genießen können. Die Zusammenarbeit hat sehr viel Spaß gemacht – auch wenn wir aufgrund des älteren Gebäudes die eine oder andere Hürde zu bewältigen hatten.',
            'Besonders beeindruckt hat uns Andys hoher Anspruch an die Qualität seiner Arbeit. Dazu kommt seine herzliche und unkomplizierte Art, die die Zusammenarbeit auch menschlich sehr angenehm gemacht hat.',
            'Über den eigentlichen Auftrag hinaus hat Andy uns wertvolle Tipps zum Einsatz von KI gegeben und hilfreiche Analysen erstellt, für die wir ihm sehr dankbar sind.',
            'Rundum eine tolle Erfahrung. Ich kann Andy mit bestem Gewissen weiterempfehlen!',
        ],
        'date': '2026-09-26',
        'ctx': 'WLAN-Modernisierung auf Ubiquiti im Altbau',
    },
    {
        'id': 'fleischmann',
        'name': 'Christian Fleischmann',
        'who': 'Christian Fleischmann',
        'role': '',
        'source': 'Google-Bewertung',
        'author_type': 'Person',
        'paragraphs': [
            'Ich bin sehr zufrieden mit der Arbeit der Firma. Die Umsetzung erfolgte schnell, zuverlässig und in sehr guter Qualität. Alle meine Anliegen wurden professionell gelöst. Klare Empfehlung!',
        ],
    },
    {
        'id': 'dietz',
        'name': 'Sebastian Dietz',
        'who': 'Sebastian Dietz',
        'role': '',
        'source': 'Google-Bewertung',
        'author_type': 'Person',
        'paragraphs': [
            'Sehr guter Service...perfekte Zusammenarbeit! Jederzeit wieder!',
        ],
    },
    {
        'id': 'verena-k',
        'name': 'Verena K.',
        'who': 'Verena K.',
        'role': '',
        'source': 'Google-Bewertung',
        'author_type': 'Person',
        'paragraphs': [
            'Sehr nette und kompetente Unterstützung! Empfehle ich uneingeschränkt.',
        ],
    },
    {
        'id': 'polednik',
        'name': 'Martina Polednik',
        'who': 'Martina Polednik',
        'role': '',
        'source': 'Google-Bewertung',
        'author_type': 'Person',
        'paragraphs': [
            'Man merkt gar nicht, dass man selber überhaupt keine Ahnung hat. Perfekt',
        ],
    },
    {
        'id': 'blumenschein',
        'name': 'Janine Blumenschein',
        'who': 'Janine Blumenschein',
        'role': 'Steuerberatung',
        'source': 'direkt',
        'author_type': 'Person',
        'paragraphs': [
            'Ich kann Grundke IT Service uneingeschränkt empfehlen. Andreas zeichnet sich durch eine äußerst zeitnahe und zuverlässige Betreuung aus. Er ist fachlich hervorragend aufgestellt und setzt gezielt moderne Technologien wie Künstliche Intelligenz ein, um optimale Lösungen zu erarbeiten. Ich fühle mich in allen IT-Angelegenheiten bestens betreut und schätze die professionelle Zusammenarbeit sehr.',
        ],
    },
]

HOME_FAQS = [
    ('Was kostet eine IT-Betreuung für meinen Betrieb?',
     'Ohne Vertrag 110 € netto je Stunde im 15-Minuten-Takt, ohne Wochenendzuschlag. Vor Ort ist die Anfahrt bis 5 km inklusive, darüber gilt eine vereinbarte Pauschale. Mit Betreuungsvertrag ab 149 € netto im Monat, inklusive IT-Assessment, Fernwartung und bevorzugtem Support.'),
    ('Wie schnell bist du bei einem IT-Notfall erreichbar?',
     'Feste Reaktionszeiten sage ich nicht zu. Vertragskunden werden bevorzugt behandelt, Premium-Kunden zuerst. Ohne Vertrag melde ich mich, sobald ich kann, und viele Störungen lassen sich dann per Fernwartung lösen.'),
    ('Was unterscheidet dich von einem großen IT-Systemhaus?',
     'Kein Ticketsystem und kein wechselndes Team. Du hast einen festen Ansprechpartner, mich. Ich kenne deine Umgebung und sage dir, was demnächst ansteht, bevor es zum Problem wird.'),
    ('Was passiert, wenn du im Urlaub oder krank bist?',
     'Für Urlaub und Krankheit gibt es eine abgestimmte Vertretung: einen selbstständigen IT-Kollegen, der im Notfall einspringt.'),
    ('Mein IT-Betreuer ist nicht mehr erreichbar – wer hilft mir kurzfristig?',
     'Das ist einer der häufigsten Gründe, warum Betriebe bei mir anrufen. Zuerst kümmere ich mich um das, was gerade nicht läuft, danach kommt die geordnete Übernahme: Zugänge, Datensicherung, Dokumentation. Wie das abläuft, steht unter <a href="/it-betreuer-wechseln/">IT-Betreuer wechseln</a>. Ruf an: 0178 258 44 38.'),
    ('Welche Region betreust du?',
     'Vor Ort bin ich in Grasbrunn, Ottobrunn, Vaterstetten, Haar, Neubiberg, Putzbrunn und Hohenbrunn, etwa 25 km im Umkreis. Remote helfe ich deutschlandweit. Für Einsätze vor Ort bleibe ich bewusst im Münchner Osten: Auf der anderen Seite Münchens stehe ich im Stau, und das hilft dir nicht.'),
    ('Welche IT-Services gibt es in Grasbrunn und Ottobrunn?',
     'Ich bin die externe IT-Abteilung für kleine Betriebe: Netzwerk, WLAN, Microsoft 365, IT-Sicherheit, Datensicherung, Kassen und Kameras, dazu KI im Betrieb, Software nach Maß und Websites. Vor Ort in Grasbrunn, Ottobrunn, Vaterstetten, Haar, Neubiberg und Umgebung.'),
    ('Kannst du auch bei KI und Automatisierung helfen?',
     'Ja, das ist inzwischen einer meiner Schwerpunkte. Ich baue Anwendungen, die wiederkehrende Arbeit übernehmen: Schnittstellen zwischen Programmen, Auswertungen von Kameraaufnahmen, Daten, die heute jemand abtippt. Dazu kommt die Frage, welche KI-Werkzeuge im Betrieb überhaupt benutzt werden dürfen und wo die Daten dabei landen. Bei der E-Rechnung helfe ich, ein passendes Programm zu finden und umzustellen. In der eigenen Firma setze ich das seit über einem halben Jahr täglich ein, die ersten Kundenanwendungen entstehen gerade. Mehr unter <a href="/ki-fuer-kmu/">KI im Betrieb</a> und <a href="/e-rechnung/">E-Rechnung</a>.'),
    ('Baust du auch Software und Websites?',
     'Ja. Kleine Anwendungen für Abläufe, die heute in Excel oder auf Zetteln laufen, und Websites, die am Handy schnell laden, bei Google gefunden werden und für KI-Assistenten lesbar aufgebaut sind. Beides zum Festpreis, mit einem Monatsbetrag für Betrieb und Pflege. Gestaltet wird nicht: Die Optik kommt aus geprüften Vorlagen, ich setze technisch um. Mehr unter <a href="/software-nach-mass/">Software nach Maß</a> und <a href="/websites-fuer-betriebe/">Websites für Betriebe</a>.'),
    ('Mein WLAN funktioniert nicht mehr – was kann ich tun?',
     'Ruf mich an oder schreib auf WhatsApp. Viele WLAN-Probleme lassen sich per Fernwartung lösen: Ich greife auf deinen Router oder Rechner zu und behebe den Fehler, ohne dass ich vorbeikommen muss. Ist Hardware kaputt, komme ich vorbei. Einsatzgebiet: Grasbrunn, Ottobrunn, Vaterstetten, Haar, Neubiberg und Umgebung München Ost.'),
    ('Gibt es IT-Support auch abends, am Wochenende oder an Feiertagen?',
     'Ja, ich habe keine klassischen Öffnungszeiten. Schreib mir auf WhatsApp oder ruf an, wann das Problem auftritt. Vertragskunden werden bevorzugt behandelt. Alle anderen bekommen eine Antwort, sobald ich kann, auch außerhalb der üblichen Bürozeiten.'),
    ('Kann ich IT-Support auch remote bekommen ohne dass jemand vorbeikommt?',
     'Ja, das ist mein Alltag. Per Fernwartung greife ich auf deinen Rechner, dein Netzwerk oder deine Server zu und löse das Problem live, du siehst dabei zu oder arbeitest weiter. Remote helfe ich deutschlandweit.'),
    ('Was kostet ein einmaliger IT-Notfall-Einsatz?',
     '110 € netto je Stunde, abgerechnet im 15-Minuten-Takt. Kein Mindestbetrag, kein Wochenendzuschlag, keine versteckten Kosten. Vor Ort ist die Anfahrt bis 5 km inklusive. Du bekommst nach dem Einsatz eine transparente Rechnung mit genauen Zeiten.'),
]

HOME_FAQ_SHOWN = 6
HOME_VOICES_SHOWN = ("blumenschein", "polednik")   # sichtbar; der Rest steht in der Wischleiste

HOME_REVIEWS_RE = re.compile(r"(<!-- HOME_REVIEWS:START[^>]*-->\n).*?([ \t]*<!-- HOME_REVIEWS:END -->)", re.S)
HOME_FAQ_RE = re.compile(r"(<!-- HOME_FAQ:START[^>]*-->\n).*?([ \t]*<!-- HOME_FAQ:END -->)", re.S)
FAQPAGE_RE = re.compile(r'  <script type="application/ld\+json">\n\{\n  "@context": "https://schema.org",\n'
                        r'  "@type": "FAQPage",.*?\n  </script>', re.S)
REVIEW_ARRAY_RE = re.compile(r'("review":\[\n).*?(\n        \])', re.S)
REVIEW_COUNT_RE = re.compile(r'"reviewCount":"\d+"')
RATING_COUNT_RE = re.compile(r'"ratingCount":"\d+"')
PROOF_RE = re.compile(r'(<a\b[^>]*\bdata-proof\b[^>]*>)5,0 bei \d+ Google-Bewertungen(</a>)')
WA_LINK_RE = re.compile(r'<a\b[^>]*\bdata-wa="([\w-]+)"[^>]*>')
PRICE_SPAN_RE = re.compile(r'(<span data-price="(\w+)">)[^<]*(</span>)')
HOME_MODIFIED_RE = re.compile(r'("dateModified":")[0-9-]+(")')
STARS = ('<div class="stars" role="img" aria-label="5 von 5 Sternen">'
         + '<svg aria-hidden="true"><use href="#ico-star"/></svg>' * 5 + '</div>')


def review_label(r):
    """Quelle auf der Karte: 'Google-Bewertung' nur bei Google, sonst Rolle + 'direkt übermittelt'."""
    if r["source"] == "Google-Bewertung":
        return "Google-Bewertung"
    return (r["role"] + " · " if r["role"] else "") + "direkt übermittelt"


def voice_card(r, ind="      "):
    """Eine Stimme als <figure class="testi-card">, Text woertlich mit „…“ um das ganze Zitat.
    Sterne nur bei Google-Bewertungen (eine direkt uebermittelte Stimme hat keine Sternebewertung)."""
    ps = r["paragraphs"]
    body = "".join("\n{i}    <p>{a}{t}{z}</p>".format(i=ind, t=esc(t), a="„" if k == 0 else "",
                                                     z="“" if k == len(ps) - 1 else "")
                   for k, t in enumerate(ps))
    ctx = '\n{i}    <div class="testi-ctx">{c}</div>'.format(i=ind, c=esc(r["ctx"])) if r.get("ctx") else ""
    cls = "testi-card testi-card--long" if len(ps) > 2 else "testi-card"
    stars = "\n{i}  {s}".format(i=ind, s=STARS) if r["source"] == "Google-Bewertung" else ""
    return ('{i}<figure class="{cls}">{stars}\n{i}  <blockquote class="testi-txt">{body}\n{i}  </blockquote>\n'
            '{i}  <figcaption>\n{i}    <div class="testi-who">{who}</div>\n{i}    <div class="testi-role">{lbl}</div>{ctx}\n'
            '{i}  </figcaption>\n{i}</figure>').format(i=ind, cls=cls, stars=stars, body=body, who=esc(r["who"]),
                                                     lbl=esc(review_label(r)), ctx=ctx)


def home_reviews_html():
    """Startseite: zwei Stimmen sichtbar (HOME_VOICES_SHOWN), der Rest vollstaendig in der Wischleiste."""
    by_id = {r["id"]: r for r in REVIEWS}
    shown = [by_id[i] for i in HOME_VOICES_SHOWN]
    rest = [r for r in REVIEWS if r["id"] not in HOME_VOICES_SHOWN]
    return ('    <div class="testi-top">\n{top}\n    </div>\n'
            '    <p class="testi-row-h">{n} weitere Stimmen<span class="testi-pos" data-testi-pos aria-hidden="true"></span></p>\n'
            '    <div class="testi-row" tabindex="0" role="region" aria-label="Weitere Kundenstimmen">\n{row}\n    </div>').format(
                top="\n".join(voice_card(r) for r in shown), n=len(rest), row="\n".join(voice_card(r) for r in rest))


def faq_item(q, a, ind):
    return ('{i}<details class="faq-item"><summary>{q} <span class="faq-ico" aria-hidden="true">+</span></summary>'
            '<div class="faq-a">{a}</div></details>').format(i=ind, q=esc(q), a=a)


def home_faq_html():
    """Sichtbares FAQ der Startseite: HOME_FAQ_SHOWN Fragen, der Rest unter "Weitere Fragen"."""
    top = "\n".join(faq_item(q, a, "      ") for q, a in HOME_FAQS[:HOME_FAQ_SHOWN])
    rest = "\n".join(faq_item(q, a, "        ") for q, a in HOME_FAQS[HOME_FAQ_SHOWN:])
    return ('    <div class="faq-wrap">\n{top}\n    </div>\n'
            '    <details class="more faq-rest">\n      <summary>Weitere Fragen</summary>\n'
            '      <div class="faq-wrap">\n{rest}\n      </div>\n    </details>').format(top=top, rest=rest)


def plain(answer_html):
    """Antwort-HTML -> Text fuers Schema (Tags weg, Entities aufgeloest)."""
    return htmllib.unescape(re.sub(r"<[^>]+>", "", answer_html))


def home_faq_schema():
    return schema_script({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": DOMAIN + "/#faqpage",
        "inLanguage": "de-DE",
        "isPartOf": {"@id": WEBSITE_ID},
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
                       for q, a in HOME_FAQS],
    })


def home_review_json():
    """review[] im LocalBusiness-Knoten, im kompakten Format des handgeschriebenen Schemas.
    reviewRating nur bei Google-Bewertungen; die direkt uebermittelte Stimme steht ohne Bewertung."""
    def js(v):
        return json.dumps(v, ensure_ascii=False)
    out = []
    for r in REVIEWS:
        date = '\n            "datePublished":{},'.format(js(r["date"])) if r.get("date") else ""
        rating = ('\n            "reviewRating":{"@type":"Rating","ratingValue":"5","bestRating":"5"},'
                  if r["source"] == "Google-Bewertung" else "")
        out.append('          {{\n            "@type":"Review",{rt}\n'
                   '            "author":{{"@type":{t},"name":{n}}},{d}\n'
                   '            "reviewBody":{b}\n          }}'.format(rt=rating, t=js(r["author_type"]), n=js(r["name"]),
                                                                    d=date, b=js("\n\n".join(r["paragraphs"]))))
    return ",\n".join(out)


def sync_home():
    """Schreibt die generierten Teile der Startseite (siehe Kopf, Punkt 6). Zeilenenden der Datei bleiben."""
    path = os.path.join(ROOT, "index.html")
    with open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    s = raw.replace("\r\n", "\n")

    def one(rx, repl, text, what):
        new, n = rx.subn(repl, text)
        if n != 1:
            raise SystemExit("sync_home: " + what + " " + str(n) + "x gefunden statt 1x")
        return new

    def wa_href(m):
        key = m.group(1)
        if key not in WA_TEXT:
            raise SystemExit("sync_home: unbekannter WhatsApp-Einstieg data-wa=" + key)
        return re.sub(r'href="[^"]*"', lambda _m: 'href="' + WA(WA_TEXT[key]) + '"', m.group(0), count=1)

    def price(m):
        if m.group(2) not in PRICES:
            raise SystemExit("sync_home: unbekannter Preis data-price=" + m.group(2))
        return m.group(1) + eur(PRICES[m.group(2)]) + m.group(3)

    s = one(HOME_REVIEWS_RE, lambda m: m.group(1) + home_reviews_html() + "\n" + m.group(2), s, "HOME_REVIEWS-Marken")
    s = one(HOME_FAQ_RE, lambda m: m.group(1) + home_faq_html() + "\n" + m.group(2), s, "HOME_FAQ-Marken")
    s = one(FAQPAGE_RE, lambda m: home_faq_schema(), s, "FAQPage-Schema")
    s = one(REVIEW_ARRAY_RE, lambda m: m.group(1) + home_review_json() + m.group(2), s, "review[] im Schema")
    # aggregateRating zaehlt nur die Google-Bewertungen (Controller-Entscheid 10.10.2026)
    s = one(REVIEW_COUNT_RE, lambda m: '"reviewCount":"{}"'.format(REVIEW_COUNT_GOOGLE), s, "reviewCount")
    s = one(RATING_COUNT_RE, lambda m: '"ratingCount":"{}"'.format(REVIEW_COUNT_GOOGLE), s, "ratingCount")
    s = one(PROOF_RE, lambda m: m.group(1) + "5,0 bei {} Google-Bewertungen".format(REVIEW_COUNT_GOOGLE) + m.group(2),
            s, "Belegzeile data-proof")
    s = one(HOME_MODIFIED_RE, lambda m: m.group(1) + HOME_DATE + m.group(2), s, "dateModified")
    s = one(UPDATED_RE, lambda m: "<span>Zuletzt aktualisiert: " + HOME_DATE_DISP + "</span>", s,
            "'Zuletzt aktualisiert' im Fuss")
    s = WA_LINK_RE.sub(wa_href, s)
    s = PRICE_SPAN_RE.sub(price, s)
    n_google = sum(r["source"] == "Google-Bewertung" for r in REVIEWS)
    if n_google != REVIEW_COUNT_GOOGLE:
        print("  Hinweis: REVIEWS hat {} Google-Stimmen, REVIEW_COUNT_GOOGLE = {}".format(n_google, REVIEW_COUNT_GOOGLE))
    s = s.replace("\n", nl)
    if s != raw:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(s)
        print("  Startseite aktualisiert (sync_home)")


# --------------------------------------------------------------------------- #
#  Sitemap                                                                     #
# --------------------------------------------------------------------------- #

STATIC_URLS = [   # (Pfad, Prioritaet, lastmod) -- lastmod der Startseite = ihr dateModified
    ("/", "1.0", HOME_DATE),
    ("/kontakt/", "0.7", KONTAKT_DATE),   # Task 9: Erreichbarkeit, Untertitel und FAQ nach Textblatt-Anhang
    ("/empfehlungen/", "0.7", "2026-05-01"),
]   # /schulung/ steht seit Task 8 ueber SERVICES in der Sitemap


def write_sitemap(places, services):
    urls = []
    for loc, prio, mod in STATIC_URLS:
        urls.append((loc, mod, prio))
    urls.append(("/barrierefreiheit/", TODAY, "0.3"))
    for s in services:
        urls.append(("/" + s["slug"] + "/", s.get("modified", TODAY), "0.8"))
    for p in places:
        urls.append(("/it-service-" + p["slug"] + "/", PLACE_DATE, "0.8"))
    body = []
    body.append('<?xml version="1.0" encoding="UTF-8"?>')
    body.append("<!--")
    body.append("  Sitemap · Grundke IT-Service · grundke-it.de")
    body.append("  Stand: " + TODAY + " (generiert via tools/build_landingpages.py)")
    body.append("  Enthalten sind ausschliesslich Seiten mit robots index, follow.")
    body.append("  /agb/, /impressum/, /datenschutz/ sind bewusst noindex und NICHT gelistet.")
    body.append("-->")
    body.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, mod, prio in urls:
        body.append("  <url>")
        body.append("    <loc>" + DOMAIN + loc + "</loc>")
        body.append("    <lastmod>" + mod + "</lastmod>")
        body.append("    <changefreq>monthly</changefreq>")
        body.append("    <priority>" + prio + "</priority>")
        body.append("  </url>")
    body.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(body) + "\n")


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #

def main():
    written = []
    for p in PLACES:
        slug, html = render_place(p, PLACES, SERVICES)
        d = os.path.join(ROOT, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        written.append(slug)
    for s in SERVICES:
        slug, html = render_service(s, PLACES, SERVICES)
        d = os.path.join(ROOT, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        written.append(slug)
    write_sitemap(PLACES, SERVICES)
    print("Generiert:", len(written), "Seiten")
    for w in written:
        print("  -", w)
    print("sitemap.xml aktualisiert")
    sync_shared(PLACES, SERVICES)
    sync_home()


if __name__ == "__main__":
    main()
