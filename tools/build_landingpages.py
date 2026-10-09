#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_landingpages.py
Version : 2.0
Autor   : Andreas Grundke IT-Service (Grundke IT-Service)
Datum   : 2026-10-07
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
"""

import os
import json
import re

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

# „ab"-Preise (netto) fuer Projekte auf den Seiten Software, Websites, E-Rechnung und KI.
# Auf False gesetzt verschwinden alle Projektpreise samt Offer-Schema und Preissaetzen in den
# FAQ; Stundensatz und Monatspakete bleiben. Alle Projektpreise der Seiten kommen aus PRICES.
SHOW_FROM_PRICES = True
PRICES = {
    "software_klein": 3000,         # kleine Anwendung, einmalig
    "software_pilot": 6000,         # Pilot mit Schnittstelle, einmalig
    "software_pilot_bis": 14000,    # obere Grenze, wie sie in der FAQ steht
    "software_betrieb": 79,         # Betrieb und Pflege je Monat, kleine Anwendung
    "software_pilot_betrieb": 150,  # Betrieb und Pflege je Monat, Pilot
    "ablauf_check": 690,            # Ablauf-Check vor Ort, bei Auftrag angerechnet
    "website_start": 1900,          # bis 5 Seiten
    "website_ausbau": 3900,         # bis 15 Seiten inkl. Umzug
    "website_betrieb": 49,          # laufender Betrieb je Monat
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

STYLE = """  <style>
    .lp-wrap { margin-top:var(--nav-h); padding:clamp(3rem,8vw,6rem) 0; }
    .lp-content { max-width:880px; }
    .lp-crumbs ol { display:flex; flex-wrap:wrap; gap:.35rem; list-style:none; margin:0 0 1.4rem; padding:0; font-size:.8rem; color:var(--text3); }
    .lp-crumbs li + li::before { content:"/"; margin-right:.35rem; color:var(--border); }
    .lp-crumbs a { color:var(--text2); text-decoration:none; }
    .lp-crumbs a:hover { color:var(--cyan); }
    .lp-crumbs [aria-current] { color:var(--text); }
    .lp-content h2 { font-family:var(--fh); font-size:clamp(1.3rem,3vw,1.8rem); font-weight:800; color:var(--text); letter-spacing:-.02em; margin:2.6rem 0 1rem; }
    .lp-content p { font-size:.95rem; color:var(--text2); line-height:1.8; margin-bottom:1rem; }
    .lp-content strong { color:var(--text); }
    .lp-cta-row { display:flex; flex-wrap:wrap; gap:1rem; margin:2rem 0; }
    .lp-content .faq-wrap { margin-top:1.2rem; }
    .lp-related { margin-top:2rem; }
    .lp-content p a { color:var(--cyan); text-underline-offset:.2em; }
    @media (max-width:560px) { .lp-cta-row .btn-p, .lp-cta-row .btn-g { width:100%; justify-content:center; } }
    .lp-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; margin:1.5rem 0; }
    .lp-card { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:1.3rem; }
    .lp-card h3 { font-family:var(--fh); font-size:1rem; font-weight:700; color:var(--text); margin-bottom:.4rem; }
    .lp-card p { font-size:.85rem; color:var(--text2); line-height:1.6; margin:0; }
    .lp-price-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1rem; margin:1.5rem 0; }
    .lp-price { background:var(--bg2); border:1px solid var(--border); border-radius:14px; padding:1.5rem; text-align:center; }
    .lp-price.feat { border-color:var(--cyan); box-shadow:0 8px 24px rgba(38,189,239,.10); }
    .lp-price .tier { font-family:var(--fm); font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:var(--text3); }
    .lp-price .amount { font-family:var(--fh); font-size:1.8rem; font-weight:800; color:var(--text); margin:.4rem 0; }
    .lp-price .amount span { font-size:.8rem; font-weight:500; color:var(--text3); }
    .lp-price .desc { font-size:.82rem; color:var(--text2); line-height:1.6; }
    .lp-places { display:flex; flex-wrap:wrap; gap:.5rem; margin:1rem 0; }
    .lp-place { font-family:var(--fm); font-size:.78rem; background:var(--bg2); border:1px solid var(--border); border-radius:999px; padding:.35rem .9rem; color:var(--text2); text-decoration:none; }
    .lp-place:hover { border-color:var(--cyan); color:var(--cyan); }
    .lp-place.here { border-color:var(--cyan); color:var(--cyan); }
    .lp-trust { background:var(--bg2); border:1px solid var(--border); border-radius:16px; padding:1.6rem; margin:2rem 0; font-size:.9rem; color:var(--text2); line-height:1.7; }
    .lp-author { display:flex; gap:1.1rem; align-items:flex-start; background:var(--bg2); border:1px solid var(--border); border-radius:14px; padding:1.4rem 1.5rem; margin:2.5rem 0 1rem; }
    .lp-author img { width:56px; height:56px; border-radius:50%; flex-shrink:0; background:var(--bg); object-fit:contain; border:1px solid var(--border); }
    .lp-author-body { font-size:.88rem; color:var(--text2); line-height:1.7; }
    .lp-author-name { font-family:var(--fh); font-weight:800; color:var(--text); font-size:1rem; }
    .lp-author-role { display:block; font-size:.8rem; color:var(--text3); margin:.1rem 0 .6rem; }
    .lp-author-meta { margin-top:.7rem; font-size:.78rem; color:var(--text3); }
    .lp-author-meta a { color:var(--cyan); text-decoration:none; }
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
DROPDOWN = (
    '<li class="nav-dropdown" id="fernwartungDropdown"><button class="nav-dropdown-toggle" '
    'onclick="toggleFernwartungDropdown(event)" aria-haspopup="true" aria-expanded="false">Fernwartung'
    '<svg class="nav-dropdown-arrow" xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>'
    '<ul class="nav-dropdown-menu">'
    '<li><a href="/fernwartung/" class="nav-dropdown-item nav-dropdown-item--highlight">'
    '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>Fernwartung starten</a></li></ul></li>')


def nav_html(current=None, home=False):
    """Kompletter Seitenkopf (Desktop-Leiste + Mobilmenue).
    current = (bereich, art): bereich aus NAV_ITEMS/NAV_KONTAKT, art "page" fuer die
    Bereichsseite selbst, "true" fuer Seiten darunter (aria-current)."""
    def cur(key):
        if current and current[0] == key:
            return ' aria-current="{}"'.format(current[1])
        return ""

    items = [(lbl, home_href if home else href, key) for lbl, href, home_href, key in NAV_ITEMS]
    fw_cur = cur("fernwartung")  # Fernwartungsseite: Eintrag im Dropdown und im Mobilmenue markieren
    dropdown = DROPDOWN.replace('<a href="/fernwartung/" class=', '<a href="/fernwartung/"' + fw_cur + ' class=')
    k_lbl, k_href, k_key = NAV_KONTAKT
    desk = "".join('\n      <li><a href="{h}"{c}>{l}</a></li>'.format(h=h, c=cur(k), l=l) for l, h, k in items)
    mob = "".join('\n  <a href="{h}"{c}>{l}</a>'.format(h=h, c=cur(k), l=l) for l, h, k in items)
    return """<header class="site-header">
<nav aria-label="Hauptnavigation">
  <div class="nav-inner inner">
    <a href="/" class="logo" title="Grundke IT-Service – München Ost"><picture><source srcset="/assets/img/logo-grundke-it-white-480.webp" type="image/webp"><img class="logo-img" src="/assets/img/logo-grundke-it-white-480.png" alt="Grundke IT-Service" width="180" height="60" /></picture></a>
    <a class="nav-loc" href="{maps}" target="_blank" rel="noopener" aria-label="Standort auf Google Maps anzeigen"><svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>München Ost</a>
    <ul class="nav-links">{desk}
      {dropdown}
      <li><a href="{k_href}"{k_cur}>{k_lbl}</a></li>
      <li><a href="tel:+491782584438" class="nav-cta">{phone}<span>Jetzt anrufen</span></a></li>
    </ul>
    <button class="hamburger" id="ham" aria-label="Menü öffnen" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span><span></span></button>
  </div>
</nav>
<div class="mobile-menu" id="mobileMenu">{mob}
  <a href="{k_href}"{k_cur}>{k_lbl}</a>
  <a href="/fernwartung/"{fw_cur} style="color:var(--cyan);font-weight:700;">&#9889; Fernwartung starten</a>
  <a href="tel:+491782584438" class="m-cta">Jetzt anrufen · 0178 258 44 38</a>
</div>
</header>""".format(maps=MAPS_URL, desk=desk, mob=mob, dropdown=dropdown, phone=PHONE_SVG, fw_cur=fw_cur,
                     k_href=k_href, k_lbl=k_lbl, k_cur=cur(k_key))


SECTION_PAGES = {"ki-fuer-kmu": "ki", "software-nach-mass": "software",
                 "websites-fuer-betriebe": "websites"}
SECTION_CHILDREN = {"e-rechnung": "ki"}
SECTION_NONE = ("digitalbonus-bayern", "ratgeber")


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
    "schulung/index.html": ("schulung", "page"),
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


def sync_shared(places, services):
    """Schreibt den gemeinsamen Header und Footer in die handgebauten Seiten.
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
        for rx, block in blocks:
            if "\r\n" in html:  # Zeilenenden der Datei beibehalten (404.html ist CRLF)
                block = block.replace("\n", "\r\n")
            html_new = rx.sub(lambda _m, b=block: b, html_new, count=1)
        if html_new != html:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(html_new)
            print("  Header/Footer aktualisiert: " + rel)

STICKY = """<div class="sticky-contact" id="stickyContact" role="navigation" aria-label="Kontakt-Optionen">
  <a href="tel:+491782584438" class="sc-btn sc-phone" aria-label="Anrufen">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
    <span>Anrufen</span>
  </a>
  <a href="https://wa.me/491782584438" target="_blank" rel="noopener" class="sc-btn sc-wa" aria-label="WhatsApp">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.5.5 0 0 0 .611.611l4.458-1.495A11.96 11.96 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.75c-2.278 0-4.381-.733-6.093-1.975l-.426-.307-2.645.887.887-2.645-.307-.426A9.72 9.72 0 0 1 2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75z"/></svg>
    <span>WhatsApp</span>
  </a>
  <a href="mailto:info@grundke-it.de" class="sc-btn sc-mail" aria-label="E-Mail">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
    <span>E-Mail</span>
  </a>
</div>"""


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


def head(title, desc, slug, og_title, og_desc, og_alt):
    canonical = DOMAIN + "/" + slug + "/"
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
  <meta name="twitter:description" content="{og_desc}"/>
  <meta name="twitter:image" content="{domain}/assets/img/og-image.png"/>
  <link rel="icon" type="image/x-icon" href="/favicon.ico"/>
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png"/>
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"/>
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"/>
  <link rel="manifest" href="/site.webmanifest"/>
  <meta name="theme-color" content="#0c4da2"/>
  <meta name="apple-mobile-web-app-title" content="Grundke IT"/>
  <meta name="application-name" content="Grundke IT"/>
  <meta name="msapplication-TileColor" content="#0c4da2"/>
  <link rel="stylesheet" href="{up}assets/css/fonts.css"/>
  <link rel="stylesheet" href="{up}assets/css/style.css"/>
""".format(title=esc(title), desc=esc(desc), canonical=canonical,
           og_title=esc(og_title), og_desc=esc(og_desc), og_alt=esc(og_alt),
           domain=DOMAIN, up=up(slug))


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
    Aufbau wie auf der Startseite: Marke/Kontakt · Leistungen · Standorte · Rechtliches.
    current_path markiert den Link der aktuellen Seite (aria-current), updated zeigt
    optional 'Zuletzt aktualisiert' (nur die Startseite fuehrt das im Fuss)."""
    def li(label, href):
        cur = ' aria-current="page"' if href == current_path else ""
        return '\n          <li><a href="{h}"{c}>{l}</a></li>'.format(h=href, c=cur, l=esc(label))
    def group_links(group):
        return "".join(li(sv["nav"], "/" + sv["slug"] + "/") for sv in services if group_of(sv) == group)
    it_links = group_links("it") + li("IT-Sicherheitsschulung", "/schulung/") + li("Produktempfehlungen", "/empfehlungen/")
    ki_links = group_links("ki")
    ratgeber_links = group_links("ratgeber")
    place_links = "".join(li("IT-Service " + pl["name"], "/it-service-" + pl["slug"] + "/") for pl in places)
    legal_links = (li("So arbeite ich", "#ablauf" if home else "/#ablauf")
                   + li("Kontakt", "/kontakt/") + li("Fernwartung starten", "/fernwartung/")
                   + "".join(li(l, h) for l, h in LEGAL_LINKS))
    updated_html = '\n      <span>Zuletzt aktualisiert: {}</span>'.format(updated) if updated else ""
    return """<footer class="site-footer">
  <div class="inner">
    <div class="foot-grid">
      <div>
        <div class="foot-brand">Grundke IT-Service</div>
        <p class="foot-desc">Deine IT-Abteilung. Nur extern.<br>IT, KI, Software und Websites für Betriebe im Münchner Osten.<br>Angebot für Unternehmen, alle Preise zzgl. MwSt.</p>
        <address class="foot-contact" style="font-style:normal;">
          <a href="tel:+491782584438">☎ 0178 258 44 38</a>
          <a href="https://wa.me/491782584438" target="_blank" rel="noopener">WhatsApp schreiben</a>
          <a href="{mailto}">info@grundke-it.de</a>
          <a href="https://grundke-it.de">www.grundke-it.de</a>
        </address>
      </div>
      <div>
        <div class="foot-h">IT-Betreuung</div>
        <ul class="foot-links">{it_links}
        </ul>
      </div>
      <div>
        <div class="foot-h">KI, Software &amp; Websites</div>
        <ul class="foot-links">{ki_links}
        </ul>
      </div>
      <div>
        <div class="foot-h">Standorte</div>
        <ul class="foot-links">{place_links}
        </ul>
        <div class="foot-h foot-h--next">Ratgeber</div>
        <ul class="foot-links">{ratgeber_links}
        </ul>
      </div>
      <div>
        <div class="foot-h">Kontakt &amp; Rechtliches</div>
        <ul class="foot-links">{legal_links}
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© 2026 Grundke IT-Service · Andreas Grundke · Beethovenring 16 · 85630 Grasbrunn</span>{updated}
      <span class="foot-ci">CI 2026.01 · grundke-it.de</span>
    </div>
  </div>
</footer>""".format(mailto=MAILTO_PREFILLED, it_links=it_links, ki_links=ki_links,
                     ratgeber_links=ratgeber_links, place_links=place_links,
                     legal_links=legal_links, updated=updated_html)


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


def author_box(mod_disp=None):
    """Sichtbare Inhaber-/Autorenangabe (E-E-A-T) inkl. 'Zuletzt aktualisiert'-Datum.
    Deckungsgleich mit dem Person-Schema (#andreas) und der WebPage-dateModified."""
    return (
        '\n      <div class="lp-author">\n'
        '        <img src="/assets/img/logo-grundke-it-badge-112.webp" alt="Logo Andreas Grundke IT-Service" width="56" height="56" loading="lazy"/>\n'
        '        <div class="lp-author-body">\n'
        '          <span class="lp-author-name">Andreas Grundke</span>\n'
        '          <span class="lp-author-role">Inhaber · Fachinformatiker für Systemintegration</span>\n'
        '          Die externe IT-Abteilung für kleine und mittlere Betriebe im Münchner Osten: IT-Betreuung, KI im Betrieb, Software nach Maß und Websites. Über 20 Jahre in der IT, ein Ansprechpartner für alles Technische.\n'
        '          <div class="lp-author-meta">Zuletzt aktualisiert: ' + (mod_disp or TODAY_DISP) + ' · <a href="/kontakt/">Kontakt aufnehmen</a></div>\n'
        '        </div>\n'
        '      </div>')


def faq_html(faqs):
    """FAQ als Akkordeon (<details>), gleiches Markup wie auf der Startseite.
    Text bleibt zeichengleich mit dem FAQPage-Schema (faq_schema)."""
    items = "".join(
        '\n        <details class="faq-item"><summary>{q} <span class="faq-ico" aria-hidden="true">+</span></summary>'
        '<div class="faq-a">{a}</div></details>'.format(q=esc(q), a=esc(a)) for q, a in faqs)
    return '\n      <div class="faq-wrap">' + items + '\n      </div>'


def cards_html(cards):
    return "".join(
        '\n        <div class="lp-card"><h3>{h}</h3><p>{t}</p></div>'.format(h=esc(h), t=esc(t))
        for h, t in cards)


def page(head_html, schema_blocks, main_html, places, services, extra_style="", slug=""):
    """extra_style wird nur von Seiten genutzt, die eigene Bausteine mitbringen
    (KI-Bereich). Alle uebrigen Seiten bleiben dadurch unveraendert."""
    parts = [head_html, STYLE]
    if extra_style:
        parts.append(extra_style)
    for s in schema_blocks:
        parts.append(schema_script(s))
    parts.append("</head>")
    parts.append('<body class="has-sticky-call">')
    parts.append('<a class="skip-link" href="#main">Zum Inhalt springen</a>')
    parts.append(nav_html(section_of(slug)))
    parts.append('\n<main id="main">')
    parts.append(main_html)
    parts.append("</main>\n")
    parts.append(footer_html(places, services, "/" + slug + "/"))
    parts.append('<script src="' + up(slug) + 'assets/js/main.js"></script>\n')
    parts.append(STICKY)
    parts.append("</body>\n</html>\n")
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
#  Daten: Orte                                                                 #
# --------------------------------------------------------------------------- #

PLACES = [
    {
        "slug": "grasbrunn", "name": "Grasbrunn", "title_name": "Grasbrunn & Neukeferloh",
        "area": ["Grasbrunn", "Neukeferloh", "Harthausen", "Haar", "Vaterstetten"],
        "intro": ("Mein Sitz ist im Beethovenring 16 in Neukeferloh – also direkt in der "
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
        "intro": ("Vaterstetten ist mit Baldham und Parsdorf eine der größten Gemeinden im Münchner "
                  "Osten – viele Pendler, Büros, Praxen und Handwerksbetriebe. Von meinem Sitz in "
                  "Neukeferloh bin ich in wenigen Minuten bei dir. Du bekommst einen festen "
                  "Ansprechpartner statt einer anonymen Hotline – persönlich, zuverlässig und mit "
                  "über 20 Jahren IT-Erfahrung."),
        "near_q": "Kommst du für IT-Probleme nach Vaterstetten?",
        "near_a": ("Ja, sehr gerne. Vaterstetten, Baldham und Parsdorf sind nur wenige Minuten von "
                   "meinem Sitz in Neukeferloh entfernt. Termine vor Ort stimmen wir ab, vieles lässt sich auch "
                   "per Fernwartung lösen. Vertragskunden werden bevorzugt behandelt."),
    },
    {
        "slug": "baldham", "name": "Baldham", "title_name": "Baldham",
        "area": ["Baldham", "Vaterstetten", "Zorneding", "Grasbrunn"],
        "intro": ("Baldham gehört zu Vaterstetten und ist über die S-Bahn bestens angebunden – ein "
                  "Standort mit vielen kleinen Unternehmen, Freiberuflern und Home-Offices. Ich "
                  "kümmere mich persönlich um deine IT: schnelle Hilfe, kurze Wege und ein "
                  "Ansprechpartner, der zurückruft."),
        "near_q": "Lohnt sich IT-Service für ein kleines Büro in Baldham?",
        "near_a": ("Gerade dann. Für kleine Büros, Freiberufler und Home-Offices in Baldham biete "
                   "ich unkomplizierte Hilfe ohne teure Mindestpauschalen – per Fernwartung oder vor Ort, "
                   "je nachdem was du brauchst."),
    },
    {
        "slug": "zorneding", "name": "Zorneding", "title_name": "Zorneding",
        "area": ["Zorneding", "Pöring", "Baldham", "Vaterstetten"],
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
        "intro": ("Haar grenzt direkt an München und ist einer der gewerbestärksten Orte im Münchner "
                  "Osten – vom Büro über die Praxis bis zum Handwerksbetrieb. Von Neukeferloh aus bin "
                  "ich in wenigen Minuten in Haar und kümmere mich persönlich um deine komplette IT."),
        "near_q": "Wie schnell bist du bei einem IT-Notfall in Haar?",
        "near_a": ("Haar ist nur wenige Minuten von meinem Sitz entfernt. Viele Störungen lassen sich "
                   "per Fernwartung lösen; ist ein Einsatz vor Ort nötig, ist die Anfahrt kurz. Eine feste "
                   "Reaktionszeit sage ich nicht zu, Vertragskunden werden bevorzugt behandelt."),
    },
    {
        "slug": "putzbrunn", "name": "Putzbrunn", "title_name": "Putzbrunn",
        "area": ["Putzbrunn", "Solalinden", "Hohenbrunn", "Grasbrunn"],
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

# Gemeinsame Leistungs-Karten fuer Ortsseiten
PLACE_CARDS = [
    ("IT-Betreuung & Wartung", "Laufende Betreuung deiner Rechner, Server und Netzwerke – als fester Ansprechpartner."),
    ("Microsoft 365 & E-Mail", "Einrichtung, Migration und Betreuung von Outlook, Teams, SharePoint & Co."),
    ("Netzwerk & WLAN", "Stabiles WLAN und sichere Netzwerke mit professioneller UniFi-Technik."),
    ("Backup & IT-Sicherheit", "Datensicherung nach 3-2-1-Strategie, Virenschutz und Schutz vor Ransomware."),
]


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
    slug = "it-service-" + p["slug"]
    title = "IT-Service {tn} | Andreas Grundke IT-Service".format(tn=p["title_name"])
    desc = ("IT-Service für {tn}: persönlicher IT-Betreuer vor Ort für KMU, Handwerk & Büros. "
            "Microsoft 365, Netzwerk, Backup, IT-Sicherheit. Kurze Wege, schnelle Hilfe.").format(tn=p["title_name"])
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
              webpage_schema(title, desc, slug)]

    # Nachbarorte-Chips (verlinken zu den anderen Ortsseiten)
    chips = ['<a class="lp-place here">{n}</a>'.format(n=esc(p["title_name"]))]
    for o in places:
        if o["slug"] != p["slug"]:
            chips.append('<a class="lp-place" href="/it-service-{s}/">{n}</a>'.format(s=o["slug"], n=esc(o["name"])))
    chips_html = "\n        ".join(chips)

    main = """<article class="lp-wrap">
  <div class="inner">
    <div class="lp-content">
      {crumbs}
      <div class="s-label">IT-Service vor Ort</div>
      <h1 class="s-title">IT-Service in {tn}</h1>
      <p class="s-sub">Dein persönlicher IT-Betreuer für {name} – kurze Wege, schnelle Hilfe, ein fester Ansprechpartner statt anonymer Hotline.</p>

      <div class="lp-cta-row">
        <a href="tel:+491782584438" class="btn-p">Jetzt anrufen · 0178 258 44 38</a>
        <a href="/kontakt/" class="btn-g">Kontakt &amp; Anfrage</a>
      </div>

      <p>{intro}</p>

      <h2>IT-Leistungen für {name}</h2>
      <div class="lp-grid">{cards}
      </div>

      <div class="lp-trust">
        <strong>Warum Unternehmen aus {name} mit mir arbeiten:</strong> Ein einheitlicher Stundensatz, Abrechnung im 15-Minuten-Takt, keine versteckten Kosten – und ein Ansprechpartner, der zurückruft. Genau das, was meine Kunden in den Google-Bewertungen mit „schnell, zuverlässig und in sehr guter Qualität“ beschreiben.
      </div>

      <h2>Auch in deiner Nähe im Einsatz</h2>
      <p>Von Neukeferloh aus betreue ich den gesamten Münchner Osten im Umkreis von rund 25&nbsp;km:</p>
      <div class="lp-places">
        {chips}
      </div>

      <h2>Häufige Fragen zum IT-Service in {name}</h2>{faqs}
{author}
      <div class="lp-cta-row" style="margin-top:2.5rem;">
        <a href="tel:+491782584438" class="btn-p">IT-Problem? Jetzt anrufen</a>
        <a href="/managed-it-service/" class="btn-g">Mehr zur laufenden IT-Betreuung</a>
      </div>
    </div>
  </div>
</article>""".format(crumbs=crumbs_html("IT-Service " + p["name"], slug), tn=esc(p["title_name"]), name=esc(p["name"]), intro=esc(p["intro"]),
                     cards=cards_html(PLACE_CARDS), chips=chips_html, faqs=faq_html(faqs),
                     author=author_box())

    return slug, page(h, schema, main, places, services, slug=slug)


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

# Kundenstimme auf einer Leistungsseite (bisher nur Netzwerk). Eigener Baustein statt der
# Startseiten-Karte, weil die Leistungsseiten deren CSS und Stern-Sprite nicht laden.
VOICE_STYLE = '''  <style>
    .lp-voice { margin:1.5rem 0 2.5rem; padding:1.6rem 1.8rem; background:var(--bg2); border:1px solid var(--border); border-radius:16px; }
    .lp-voice blockquote { margin:0; max-width:66ch; font-style:italic; color:var(--text2); line-height:1.7; }
    .lp-voice blockquote p { margin:0; }
    .lp-voice blockquote p + p { margin-top:.85em; }
    .lp-voice figcaption { margin-top:1.2rem; padding-top:1rem; border-top:1px solid var(--border); font-size:.85rem; color:var(--text2); }
    .lp-voice figcaption strong { color:var(--text); }
    .lp-voice figcaption a { color:var(--cyan); text-decoration:underline; text-underline-offset:3px; }
  </style>
'''

# Zusatz-CSS ausschliesslich fuer die KI-Seiten. Wird ueber das Feld "extra_style"
# eingehaengt, damit Orts- und uebrige Leistungsseiten unveraendert bleiben.
KI_STYLE = '''  <style>
    /* Bausteine nur fuer den KI-Bereich (via extra_style, damit die uebrigen Seiten unveraendert bleiben) */
    .lp-wrap--hero { padding-top:0; }
    .lp-hero { background:var(--bg2); border-bottom:1px solid var(--border); padding:clamp(2.5rem,7vw,5.5rem) 0 clamp(2.5rem,6vw,4.5rem); margin-bottom:clamp(2.5rem,6vw,4rem); position:relative; overflow:hidden; }
    .lp-hero::before { content:''; position:absolute; inset:0; background:radial-gradient(ellipse 55% 70% at 85% 15%, rgba(12,77,162,.28), transparent 70%); pointer-events:none; }
    .lp-hero-grid { position:relative; display:grid; gap:clamp(2rem,5vw,4rem); align-items:center; }
    @media (min-width:1024px) { .lp-hero-grid { grid-template-columns:minmax(0,1.35fr) minmax(0,1fr); } }
    .lp-hero-h1 { font-family:var(--fh); font-size:clamp(2.1rem,5.2vw,3.6rem); font-weight:800; line-height:1.07; letter-spacing:-.035em; color:var(--text); margin-bottom:1.1rem; text-wrap:balance; }
    .lp-hero-accent { display:block; color:var(--cyan); }
    .lp-hero .lp-cta-row { margin-bottom:0; }
    .lp-paths { background:var(--bg); border:1px solid var(--border); border-radius:14px; padding:.6rem; }
    .lp-paths-h { font-family:var(--fh); font-size:1.1rem; font-weight:700; color:var(--text); padding:.8rem .9rem .5rem; }
    .lp-paths ul { list-style:none; margin:0; padding:0; }
    .lp-paths li + li { border-top:1px solid var(--border); }
    .lp-paths a { display:block; padding:.95rem .9rem; border-radius:10px; text-decoration:none; transition:background .2s; }
    .lp-paths a:hover { background:var(--bg3); }
    .lp-paths a:focus-visible { outline:2px solid var(--cyan); outline-offset:2px; }
    .lp-path-t { display:block; font-family:var(--fh); font-weight:700; font-size:1rem; color:var(--text); }
    .lp-path-t::after { content:" →"; color:var(--cyan); transition:margin .2s; }
    .lp-paths a:hover .lp-path-t::after { margin-left:.25rem; }
    .lp-path-d { display:block; font-size:.85rem; color:var(--text2); line-height:1.55; margin-top:.25rem; }
    .ki-case { background:var(--bg2); border:1px solid var(--border); border-radius:14px; padding:1.5rem 1.6rem; margin:1.1rem 0; }
    .ki-case-tag { font-family:var(--fm); font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:var(--cyan); display:block; margin-bottom:.5rem; }
    .ki-case h3 { font-family:var(--fh); font-size:1.05rem; font-weight:800; color:var(--text); margin:0 0 .6rem; letter-spacing:-.01em; }
    .ki-case p { font-size:.9rem; color:var(--text2); line-height:1.75; margin:0 0 .7rem; }
    .ki-case p:last-child { margin-bottom:0; }
    .ki-case .ki-result { font-size:.86rem; color:var(--text); background:rgba(38,189,239,.07); border-radius:8px; padding:.7rem .9rem; }
    .ki-check { background:var(--bg2); border:1px solid var(--cyan); border-radius:16px; padding:1.8rem; margin:2.2rem 0; box-shadow:0 8px 28px rgba(38,189,239,.10); }
    .ki-check h3 { font-family:var(--fh); font-size:1.2rem; font-weight:800; color:var(--text); margin:0 0 .7rem; }
    .ki-check p { font-size:.92rem; color:var(--text2); line-height:1.75; margin:0 0 1rem; }
    .ki-check ul { list-style:none; margin:0 0 1.2rem; padding:0; }
    .ki-check li { font-size:.9rem; color:var(--text2); line-height:1.6; padding:.35rem 0 .35rem 1.5rem; position:relative; }
    .ki-check li::before { content:""; position:absolute; left:0; top:.85rem; width:7px; height:7px; border-radius:50%; background:var(--cyan); }
    .ki-note { background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:1.3rem 1.5rem; margin:1.8rem 0; }
    .ki-note strong { color:var(--text); }
    .ki-note p { font-size:.88rem; color:var(--text2); line-height:1.75; margin:0 0 .7rem; }
    .ki-note p:last-child { margin-bottom:0; }
    .ki-tbl-wrap { overflow-x:auto; margin:1.4rem 0; }
    .ki-tbl { width:100%; border-collapse:collapse; font-size:.86rem; min-width:520px; }
    .ki-tbl th { font-family:var(--fh); font-size:.78rem; letter-spacing:.03em; text-transform:uppercase; color:var(--text3); text-align:left; padding:.7rem .9rem; border-bottom:1px solid var(--border); }
    .ki-tbl td { padding:.85rem .9rem; border-bottom:1px solid var(--border); color:var(--text2); line-height:1.65; vertical-align:top; }
    .ki-tbl td:first-child { color:var(--text); font-weight:600; white-space:nowrap; }
    .ki-tbl tr:last-child td { border-bottom:none; }
    @media (max-width:600px) {
      .ki-tbl { min-width:0; }
      .ki-tbl thead { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
      .ki-tbl tbody, .ki-tbl tr, .ki-tbl td { display:block; width:100%; }
      .ki-tbl tr { border-bottom:1px solid var(--border); padding:.75rem 0; }
      .ki-tbl tr:last-child { border-bottom:none; }
      .ki-tbl td { border-bottom:none; padding:.2rem 0; }
      .ki-tbl td:first-child { white-space:normal; }
      .ki-tbl td[data-label]::before { content:attr(data-label) ": "; color:var(--text); font-weight:600; }
    }
  </style>'''



# Zusatz-CSS fuer die Seiten vom 07.10.2026 (Schritte, Checklisten, Kurzantwort
# im Ratgeber). Wird zusammen mit KI_STYLE ueber "extra_style" eingehaengt, die uebrigen Seiten
# bleiben unveraendert. Nummern nur dort, wo die Reihenfolge zaehlt (Ablauf, erste Minuten).
NEW_STYLE = '''  <style>
    .lp-steps { counter-reset:st; list-style:none; margin:1.2rem 0 1.8rem; padding:0; }
    .lp-steps > li { counter-increment:st; position:relative; padding:.15rem 0 1.1rem 2.9rem; font-size:.93rem; color:var(--text2); line-height:1.75; }
    .lp-steps > li::before { content:counter(st); position:absolute; left:0; top:.05rem; width:1.9rem; height:1.9rem; border-radius:50%; border:1px solid var(--cyan); color:var(--cyan); font-family:var(--fh); font-weight:700; font-size:.85rem; display:grid; place-items:center; }
    .lp-steps > li + li::after { content:""; position:absolute; left:.95rem; top:-1.05rem; width:1px; height:1.05rem; background:var(--border); }
    .lp-steps strong { color:var(--text); }
    .lp-checklist { list-style:none; margin:1rem 0 1.4rem; padding:0; }
    .lp-checklist li { position:relative; padding:.35rem 0 .35rem 1.9rem; font-size:.92rem; color:var(--text2); line-height:1.65; }
    .lp-checklist li::before { content:""; position:absolute; left:.35rem; top:.62rem; width:.4rem; height:.75rem; border:solid var(--cyan); border-width:0 2px 2px 0; transform:rotate(45deg); }
    .lp-checklist strong, .lp-dont strong { color:var(--text); }
    .lp-dont { list-style:none; margin:1rem 0 1.4rem; padding:0; }
    .lp-dont li { position:relative; padding:.35rem 0 .35rem 1.9rem; font-size:.92rem; color:var(--text2); line-height:1.65; }
    .lp-dont li::before, .lp-dont li::after { content:""; position:absolute; left:.2rem; top:1rem; width:.85rem; height:2px; border-radius:1px; background:#e8806f; transform:rotate(45deg); }
    .lp-dont li::after { transform:rotate(-45deg); }
    .lp-answer { background:var(--bg2); border:1px solid var(--border); border-radius:14px; padding:1.3rem 1.5rem; margin:1.6rem 0 2rem; }
    .lp-answer p { margin:0; color:var(--text); font-size:.98rem; line-height:1.75; }
    .lp-answer p + p { margin-top:.7rem; color:var(--text2); font-size:.92rem; }
    .lp-content h3 { font-family:var(--fh); font-size:1.08rem; font-weight:700; color:var(--text); margin:1.8rem 0 .6rem; }
  </style>'''
NEW_PAGE_STYLE = KI_STYLE + "\n" + NEW_STYLE
KI_START_TEXT = (
    '<p>Das Paket KI-Start kostet je nach Größe des Betriebs ab ' + eur(PRICES["ki_start"]) + ' netto. '
    'Microsoft 365 und Copilot bekommst du auf Wunsch über mich, ChatGPT- und Claude-Teamkonten schließt ihr '
    'direkt beim Anbieter ab, ich richte sie ein und verwalte sie. Dazu auf Wunsch jedes Jahr eine Auffrischung '
    'der Schulung. Mehr auf der Seite <a href="/lizenzen/">Lizenzen</a>.</p>'
    if SHOW_FROM_PRICES else
    '<p>Microsoft 365 und Copilot bekommst du auf Wunsch über mich, ChatGPT- und Claude-Teamkonten schließt ihr '
    'direkt beim Anbieter ab, ich richte sie ein und verwalte sie. Dazu auf Wunsch jedes Jahr eine Auffrischung '
    'der Schulung. Mehr auf der Seite <a href="/lizenzen/">Lizenzen</a>.</p>')


def offer_from(name, min_price, desc, monthly=False):
    """Offer mit Mindestpreis ('ab ...'), netto. Monatspreise tragen die Einheit Monat (MON)."""
    spec = {"@type": "UnitPriceSpecification" if monthly else "PriceSpecification",
            "minPrice": "{:.2f}".format(min_price), "priceCurrency": "EUR", "valueAddedTaxIncluded": False}
    if monthly:
        spec.update({"unitCode": "MON", "unitText": "Monat"})
    return {"@type": "Offer", "name": name, "description": desc, "priceSpecification": spec}


EINMALIG = "einmalig, zzgl. MwSt."
RATGEBER_CTA = [("tel:+491782584438", "Anrufen · 0178 258 44 38", "btn-p"),
                ("/fernwartung/", "Fernwartung starten", "btn-g")]

TRUST_DEFAULT = ("<strong>Einheitlicher Stundensatz von 110 € netto, Abrechnung im 15-Minuten-Takt, keine "
                 "versteckten Kosten.</strong> Kein klassischer Kundendienst, sondern ein fester persönlicher "
                 "Ansprechpartner mit über 20 Jahren IT-Erfahrung – im Raum München Ost, datenschutzgerecht und auf "
                 "Wunsch self-hosted.")
# Fuer Projekte zum Festpreis (Software, Websites, E-Rechnung): Festpreis vorne, Stundensatz nur
# fuer Einsaetze ausserhalb davon.
TRUST_FESTPREIS = ("<strong>Festpreis für das Projekt, fester Monatsbetrag für Betrieb und Pflege.</strong> "
                   "Was außerhalb davon anfällt, kostet 110 € netto je Stunde im 15-Minuten-Takt. Du sprichst "
                   "von der ersten Frage bis zum laufenden Betrieb mit mir, Andreas Grundke.")


SERVICES = [
    {
        "slug": "managed-it-service", "nav": "Managed IT-Service",
        "title": "Managed IT-Service für KMU | München Ost – Andreas Grundke IT-Service",
        "h1": "Managed IT-Service für kleine &amp; mittlere Unternehmen",
        "label": "Laufende IT-Betreuung", "service_type": "Managed IT-Service",
        "desc": ("Managed IT-Service für kleine & mittlere Unternehmen im Raum München Ost: laufende "
                 "IT-Betreuung, bevorzugter Support, ein persönlicher Ansprechpartner. Planbare "
                 "Monatspakete statt teurer Ausfälle."),
        "sub": "Deine komplette IT in einer Hand – proaktiv betreut, mit bevorzugtem Support und einem persönlichen Ansprechpartner, der zurückruft.",
        "intro": ("Die meisten kleinen Unternehmen rufen erst an, wenn die IT schon steht – und dann "
                  "wird es teuer. <strong>Managed IT-Service dreht das um:</strong> Ich kümmere mich "
                  "laufend um deine Rechner, Server, E-Mails und Sicherheit, bevor etwas ausfällt. "
                  "Du zahlst einen festen, planbaren Monatsbetrag statt unkalkulierbarer "
                  "Notfall-Rechnungen – und hast einen <strong>Single Point of Contact</strong> für "
                  "alles rund um IT. Wechselst du gerade von einem anderen Dienstleister, steht der "
                  "Ablauf auf der Seite <a href=\"/it-betreuer-wechseln/\">IT-Betreuer wechseln</a>."),
        "raw_intro": True,
        "cards": [
            ("Proaktive Wartung", "Updates, Monitoring und Pflege deiner Systeme – bevor Probleme entstehen."),
            ("Microsoft 365", "Postfächer, Teams, Lizenzen und Sicherheit zentral verwaltet."),
            ("Backup & Wiederherstellung", "Automatische Datensicherung nach 3-2-1 – inklusive Test der Rücksicherung."),
            ("IT-Sicherheit", "Virenschutz, Firewall, VPN und Schutz vor Ransomware & Phishing."),
            ("Bevorzugter Support", "Vertragskunden kommen vor Ad-hoc-Anfragen dran, Premium-Kunden zuerst."),
            ("Beratung & Einkauf", "Hardware-Empfehlungen und Beschaffung ohne Aufschlag-Spielchen."),
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
             "Managed IT-Service bedeutet, dass ich mich laufend um deine gesamte IT kümmere – "
             "Wartung, Updates, Microsoft 365, Backup und Sicherheit – zu einem festen monatlichen "
             "Preis. Statt erst beim Ausfall zu reagieren, halte ich deine Systeme proaktiv am Laufen."),
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
        "label": "Microsoft 365", "service_type": "Microsoft 365 Betreuung",
        "desc": ("Microsoft 365 für KMU im Raum München Ost: Einrichtung, Migration und laufende "
                 "Betreuung von Exchange Online, Teams, SharePoint & OneDrive – inklusive Sicherheit "
                 "und DSGVO-konformer Datensicherung."),
        "sub": "Outlook, Teams, SharePoint & OneDrive – richtig eingerichtet, sicher betrieben und persönlich betreut.",
        "intro": ("Microsoft 365 ist schnell gebucht – aber sauber eingerichtet, abgesichert und "
                  "DSGVO-konform betrieben ist es eine andere Sache. Ich übernehme die Ersteinrichtung, "
                  "die Migration von alten Postfächern oder Servern und die laufende Betreuung deiner "
                  "M365-Umgebung. So nutzt du Outlook, Teams und SharePoint zuverlässig, ohne dich um "
                  "Lizenzen, Sicherheit oder Updates kümmern zu müssen. Die Lizenzen bekommst du auf "
                  "Wunsch über mich, mehr auf der Seite <a href=\"/lizenzen/\">Lizenzen</a>."),
        "raw_intro": True,
        "cards": [
            ("Einrichtung & Migration", "Umzug von altem Server oder Postfach nach Microsoft 365 – ohne Datenverlust."),
            ("Exchange Online & E-Mail", "Professionelle E-Mail mit eigener Domain, Signaturen und Spam-Schutz."),
            ("Teams & SharePoint", "Zusammenarbeit, Dateifreigaben und Strukturen, die dein Team versteht."),
            ("Sicherheit & Backup", "MFA, Rechte-Konzept und externes M365-Backup – denn Microsoft sichert deine Daten nicht vollständig."),
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
        "label": "IT-Sicherheit", "service_type": "IT-Sicherheit und Datensicherung",
        "desc": ("IT-Sicherheit & Backup für KMU im Raum München Ost: Schutz vor Ransomware und "
                 "Datenverlust mit 3-2-1-Backup, Virenschutz, Firewall und Mitarbeiter-Awareness."),
        "sub": "Schutz vor Ransomware, Datenverlust und Ausfall – mit einer Datensicherung, die im Ernstfall wirklich funktioniert.",
        "intro": ("Ein einziger verschlüsselter Server oder ein gelöschtes Verzeichnis kann ein "
                  "kleines Unternehmen tagelang lahmlegen. Ich sorge dafür, dass es gar nicht erst so "
                  "weit kommt – und dass du im Ernstfall deine Daten zurückbekommst. Dazu gehören eine "
                  "saubere Backup-Strategie nach dem 3-2-1-Prinzip, aktueller Virenschutz, eine "
                  "vernünftige Firewall und Mitarbeiter, die Phishing erkennen."),
        "raw_intro": True,
        "cards": [
            ("Backup nach 3-2-1", "Drei Kopien, zwei Medien, eine außer Haus – inklusive Test der Rücksicherung."),
            ("Virenschutz", "Zentral verwalteter Schutz (z. B. ESET) auf allen Geräten."),
            ("Firewall & VPN", "Abgesicherter Internetzugang und verschlüsselter Zugriff fürs Home-Office."),
            ("Awareness-Schulung", "Deine Mitarbeiter lernen, Phishing und Betrug zu erkennen."),
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
        "label": "Netzwerktechnik", "service_type": "Netzwerk, WLAN und Firewall",
        "desc": ("Netzwerk, WLAN & Firewall für KMU im Raum München Ost: stabiles WLAN, sichere "
                 "Netzwerke und VPN mit professioneller UniFi-Technik – geplant, eingerichtet und betreut."),
        "sub": "Stabiles WLAN im ganzen Gebäude, sichere Netze und verschlüsselter Zugriff fürs Home-Office.",
        "intro": ("Langsames WLAN, ständige Abbrüche oder ein Netzwerk, das mit dem Betrieb gewachsen "
                  "und unübersichtlich geworden ist – das kostet täglich Zeit und Nerven. Ich plane, "
                  "richte ein und betreue Netzwerke mit professioneller UniFi-Technik: stabiles WLAN "
                  "auf jeder Fläche, sauber getrennte Netze (VLAN) für Gäste und Betrieb sowie sichere "
                  "Zugänge per Firewall und VPN."),
        "raw_intro": True,
        "cards": [
            ("Netzwerk & VLAN", "Strukturierte, sicher getrennte Netze für Betrieb, Gäste und Kasse."),
            ("WLAN (UniFi)", "Lückenloses, schnelles WLAN auf jeder Etage und im Außenbereich."),
            ("Firewall & VPN", "Abgesicherter Internetzugang und verschlüsselter Zugriff von unterwegs."),
            ("Monitoring", "Ich sehe Störungen oft, bevor du sie bemerkst – und reagiere proaktiv."),
        ],
        "modified": "2026-09-27", "modified_disp": "27.09.2026",
        # Kundenstimme wortgetreu wie auf Google (Apartments Bauer, 26.09.2026). Nicht kuerzen,
        # nicht glaetten; identisch mit der Karte und dem reviewBody auf der Startseite.
        "extra": """
      <h2>Aus der Praxis: WLAN in einem älteren Gebäude</h2>
      <figure class="lp-voice">
        <blockquote>
          <p>„Andy hat das WLAN in unserem Haus modernisiert und auf Ubiquiti umgestellt, damit unsere Gäste eine bessere Internetverbindung genießen können. Die Zusammenarbeit hat sehr viel Spaß gemacht – auch wenn wir aufgrund des älteren Gebäudes die eine oder andere Hürde zu bewältigen hatten.</p>
          <p>Besonders beeindruckt hat uns Andys hoher Anspruch an die Qualität seiner Arbeit. Dazu kommt seine herzliche und unkomplizierte Art, die die Zusammenarbeit auch menschlich sehr angenehm gemacht hat.</p>
          <p>Über den eigentlichen Auftrag hinaus hat Andy uns wertvolle Tipps zum Einsatz von KI gegeben und hilfreiche Analysen erstellt, für die wir ihm sehr dankbar sind.</p>
          <p>Rundum eine tolle Erfahrung. Ich kann Andy mit bestem Gewissen weiterempfehlen!“</p>
        </blockquote>
        <figcaption><strong>Apartments Bauer</strong> · Google-Bewertung, 5 von 5 Sternen, wörtlich übernommen · <a href="/#referenzen">weitere Kundenstimmen</a> · <a href="/#bewertungen-herkunft">woher die Stimmen kommen</a></figcaption>
      </figure>
""",
        "extra_style": VOICE_STYLE,
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
        "title": "IT-Notdienst für Firmen im Münchner Osten | Grundke IT",
        "h1": "IT-Notdienst für Unternehmen",
        "label": "Wenn die IT steht", "service_type": "IT-Notdienst",
        "desc": ("IT-Notdienst für Unternehmen im Münchner Osten: Hilfe bei Störungen, Viren und Datenverlust "
                 "per Fernwartung oder vor Ort. Dein ITler geht nicht ran? Ich schon."),
        "sub": "Dein ITler geht nicht ran? Ich schon. Hilfe bei IT-Störungen, per Fernwartung oder vor Ort.",
        "intro": ("Wenn die IT steht, zählt jede Minute. Viele Störungen löse ich per Fernwartung, sobald "
                  "wir telefoniert haben; bei größeren Problemen komme ich vorbei, die Wege im Münchner "
                  "Osten sind kurz. Eine feste Reaktionszeit sage ich nicht zu, Vertragskunden werden "
                  "bevorzugt behandelt. Kein Ticketsystem, keine Warteschleife – du erreichst direkt die "
                  "Person, die das Problem löst. Was du in den ersten Minuten selbst tun kannst, steht im "
                  "Ratgeber <a href=\"/ratgeber/\">Die ersten 15 Minuten</a>."),
        "raw_intro": True,
        "cards": [
            ("Hilfe per Fernwartung", "Über TeamViewer verbinde ich mich nach deiner Freigabe mit deinem Bildschirm und löse das Problem direkt."),
            ("Vor-Ort-Einsatz", "Lässt sich etwas nicht aus der Ferne lösen, komme ich vorbei."),
            ("Daten- & Systemrettung", "Hilfe bei Datenverlust, defekten Festplatten und nicht startenden Systemen."),
            ("Virenbefall & Ransomware", "Bereinigung befallener Systeme und Wiederherstellung aus dem Backup."),
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
             "Du lädst ein kleines Programm (TeamViewer) und nennst mir die Verbindungs-ID. Ich "
             "verbinde mich, du siehst alles mit und kannst die Sitzung jederzeit beenden. Ohne deine "
             "Freigabe komme ich nicht auf deinen Rechner."),
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
        "label": "KI in der Praxis", "service_type": "KI-Beratung und Anwendungsentwicklung für KMU",
        "published": KI_PUB_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
        "cta2_href": "/ki-automatisierung/", "cta2_text": "Abläufe automatisieren",
        "extra_schema": [POTENZIALCHECK_SCHEMA],
        "desc": ("KI im Betrieb: Abläufe automatisieren, Auswertungen aus vorhandenen Daten, "
                 "datenschutzgerecht umgesetzt. Kostenloser Potenzialcheck im Raum München Ost."),
        "sub": "Keine Folien über Künstliche Intelligenz, sondern Anwendungen, die bei dir laufen. Gebaut von jemandem, der deine IT ohnehin betreut.",
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
            ("Abläufe automatisieren", "Wiederkehrende Handarbeit am Rechner: Daten übertragen, Listen erzeugen, Rechnungen bauen, Berichte zusammenstellen."),
            ("Auswertungen aus vorhandenen Daten", "Was in Kamera, Kasse, Zeiterfassung oder Warenwirtschaft schon steckt, wird sichtbar gemacht."),
            ("Systeme verbinden", "Zwei Programme, die nicht miteinander reden, koppele ich über ihre Dateiformate oder ihre Schnittstelle."),
            ("KI-Werkzeuge einführen", "Welches Werkzeug für welche Aufgabe taugt, wie es eingerichtet wird und was die Mitarbeiter darüber wissen müssen."),
            ("Datenschutz vorher klären", "Lokales Modell, EU-Rechenzentrum oder Anbieter mit Auftragsverarbeitungsvertrag. Die Entscheidung fällt vor der Umsetzung."),
            ("Betrieb und Pflege", "Eine gebaute Anwendung braucht jemanden, der sie weiter betreut. Ich bleibe der Ansprechpartner."),
        ],
        "extra": """
      <h2>KI soll bei euch niemanden ersetzen</h2>
      <p>Sie soll die Arbeit wegnehmen, die keiner gern macht: Daten von einem Programm ins andere kopieren, Rechnungen abtippen, dieselben Fragen zum zehnten Mal beantworten, Spam aussortieren. Eure Leute haben dann wieder Zeit für Kunden, Aufträge und Ideen, und du als Inhaber für das Geschäft statt für den Papierkram. Ich fange deshalb immer bei den Menschen an, die mit dem Ablauf arbeiten: Was nervt euch jede Woche? Das bauen wir zuerst weg.</p>
      <p>Wer im Betrieb arbeitet, fragt sich bei KI oft, ob der eigene Platz sicher ist. Aus der Praxis: Der Job wird nicht ersetzt, er wird leichter. Wer den Ablauf kennt, weiß am besten, wo es hakt, und genau diese Leute brauche ich, um die Lösung zu bauen.</p>

      <h2>So sieht das im Alltag aus</h2>
      <h3>Doku nach dem Einsatz per Sprache</h3>
      <p>Auf dem Rückweg von der Baustelle sind die Hände voll. Im Firmen-KI-Konto einen neuen Chat öffnen, Kunde und Vorhaben nennen, dann frei erzählen: was gemacht wurde, welches Material, was abgestimmt ist, was noch offen ist und wie lange es gedauert hat. Am Ende fasst die KI zusammen, und der Text geht per Kopieren und Einfügen in Buchhaltung oder Auftragsverwaltung. Voraussetzung ist ein bezahltes Firmenkonto mit Vertrag; unterwegs nur mit dem Handy in der Halterung und per Sprachsteuerung (§ 23 Abs. 1a StVO) oder kurz auf dem Parkplatz.</p>
      <h3>Programme reden miteinander</h3>
      <p>Lexware Office und viele Auftrags- und Rechnungsprogramme haben Schnittstellen. Kundendaten, Aufträge, Material und Angebotsentwürfe lassen sich darüber anlegen, abfragen und abgleichen, statt alles in der Oberfläche abzutippen. Mein eigener Betrieb legt Kunden und Angebotsentwürfe auf diesem Weg direkt in Lexware an.</p>
      <h3>Warnungen, die jemand liest</h3>
      <p>Meldungen der Datensicherung, Fehlermails von Geräten, volle Postfächer: Eine KI liest sie, ordnet sie ein und schickt nur das Wichtige an die richtige Person, mit einem Satz, was zu tun ist.</p>
      <p>Dazu kommen Auswertungen und Monatsberichte, Zusammenfassungen langer Mails und Dokumente, Entwürfe für Angebote und Antworten und die Abstimmung von Terminen.</p>

      <h2>Zwei Beispiele aus der Praxis</h2>
      <p>Das erste ist ein typischer Fall für Videoauswertung, das zweite läuft in meinem eigenen Betrieb.</p>

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

      <div class="ki-check">
        <h3>Kostenloser KI-Potenzialcheck</h3>
        <p>Der einfachste Einstieg. 60 bis 90 Minuten, bei dir im Betrieb oder per Videogespräch. Wir gehen durch, was bei euch regelmäßig Zeit kostet, und schauen, was davon eine Maschine übernehmen kann.</p>
        <ul>
          <li>Wir sehen uns die Abläufe an, die jeden Monat gleich laufen</li>
          <li>Ich sage dir, was sich automatisieren lässt und was nicht</li>
          <li>Du bekommst es schriftlich, mit Aufwand, Nutzen und den rechtlichen Punkten</li>
          <li>Das Papier gehört dir, auch wenn wir nicht weiterarbeiten</li>
        </ul>
        <div class="lp-cta-row" style="margin:0;">
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
        "label": "Weniger Handarbeit", "service_type": "Prozessautomatisierung und Anwendungsentwicklung für KMU",
        "published": KI_PUB_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": KI_STYLE,
        "cta2_href": "/ki-fuer-kmu/", "cta2_text": "Überblick KI im Betrieb",
        "desc": ("Schnittstellen zwischen Programmen, Dokumente automatisch auslesen, Berichte ohne "
                 "Excel-Bastelei: Prozesse mit KI automatisieren für kleine Betriebe."),
        "sub": "Alles, was jeden Monat gleich abläuft und trotzdem jemand von Hand macht, lässt sich meistens automatisieren.",
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
            ("E-Rechnungen aus vorhandenen Daten", "Aus CSV-Exporten, Listen oder einem Vorsystem entstehen Rechnungen als XRechnung oder ZUGFeRD."),
            ("Schnittstellen zwischen Programmen", "Warenwirtschaft, Zeiterfassung, Buchhaltung, Kasse. Was Daten exportieren kann, lässt sich koppeln."),
            ("Dokumente auslesen", "Lieferscheine, Eingangsrechnungen, Formulare: Inhalte werden erkannt und landen strukturiert in der Datenbank."),
            ("Auswertungen und Berichte", "Zahlen, die heute jemand am Monatsende in Excel zusammensucht, entstehen automatisch und immer gleich."),
            ("Wiederkehrende Läufe", "Nächtliche Abgleiche, Erinnerungen, Prüfungen, Datenübernahmen. Einmal eingerichtet, läuft es weiter."),
            ("Meldung statt Nachsehen", "Wenn etwas schiefgeht, meldet sich die Anwendung von selbst. Per E-Mail oder Nachricht aufs Handy."),
        ],
        "extra": """
      <h2>Sonderfall E-Rechnung</h2>
      <p>Kommen eure Rechnungsdaten aus einem Vorsystem oder einer Excel-Liste, lässt sich die E-Rechnung gleich mit automatisieren, statt zweimal umzustellen. Fristen, Ausnahmen und die Wahl des passenden Programms stehen auf der Seite <a href="/e-rechnung/">E-Rechnung</a>.</p>

      <h2>Wie so ein Projekt abläuft</h2>
      <p>Am Anfang steht kein Angebot, sondern ein Blick auf den Ablauf, um den es geht. Meist zeigt sich schon dabei, ob die Sache klein oder groß ist.</p>
      <div class="lp-grid">
        <div class="lp-card"><h3>1. Ablauf ansehen</h3><p>Wir gehen den Weg der Daten einmal gemeinsam durch, so wie er heute läuft. Mit den echten Dateien, nicht mit einem Beispiel.</p></div>
        <div class="lp-card"><h3>2. Aufwand schätzen</h3><p>Du bekommst eine Einschätzung, wie lange die Umsetzung dauert und wie viel Zeit sie im Monat spart. Beides schriftlich.</p></div>
        <div class="lp-card"><h3>3. Klein anfangen</h3><p>Erst läuft ein Teilstück, das nachweisbar funktioniert. Danach wird erweitert. Kein Projekt, das ein halbes Jahr im Dunkeln läuft.</p></div>
        <div class="lp-card"><h3>4. Übergabe und Betreuung</h3><p>Die Anwendung wird dokumentiert und läuft bei dir. Ich bleibe der Ansprechpartner, wenn sich etwas ändert.</p></div>
      </div>

      <div class="ki-check">
        <h3>Kostenloser KI-Potenzialcheck</h3>
        <p>Wenn du nicht sicher bist, ob sich bei dir etwas lohnt: 60 bis 90 Minuten, wir gehen deine Abläufe durch, danach bekommst du schriftlich, was sich automatisieren lässt, was es kostet und was es bringt. Kostenlos und ohne Verpflichtung.</p>
        <div class="lp-cta-row" style="margin:0;">
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
        "label": "Kamera plus Auswertung", "service_type": "KI-gestützte Videoanalyse und Auswertung für Unternehmen",
        "published": KI_PUB_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": KI_STYLE,
        "cta2_href": "/netzwerk-wlan-firewall/", "cta2_text": "Netzwerk & Kameratechnik",
        "desc": ("Videoüberwachung mit KI: Fahrzeuge und Kennzeichen erkennen, Vorgänge zählen, Kennzahlen "
                 "darstellen. Auf vorhandenen UniFi-Anlagen, Verarbeitung im Haus."),
        "sub": "Eine Kamera zeichnet auf. Ausgewertet wird sie selten, weil niemand die Zeit hat, Aufnahmen durchzusehen.",
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
            ("Fahrzeuge und Kennzeichen erkennen", "Fahrzeuge, Container, Maschinen, Paletten. Wo es einen klaren Zweck gibt, werden auch Kennzeichen gelesen, etwa um bekannte Fahrzeuge von fremden zu unterscheiden."),
            ("Vorgänge zählen", "Zufahrten, Anlieferungen, Durchgänge, Standzeiten. Mit Zeitstempel und ohne dass jemand mitschreibt."),
            ("Protokoll in der Datenbank", "Jedes Ereignis wird gespeichert und bleibt auswertbar, auch wenn die Aufnahme längst gelöscht ist."),
            ("Kennzahlen auf einen Blick", "Eine Oberfläche zeigt Verläufe, Summen und Auffälligkeiten. Im Browser, auch vom Handy aus."),
            ("Meldung bei Auffälligkeiten", "Bewegung außerhalb der Betriebszeit oder ungewöhnliche Häufungen melden sich von selbst."),
            ("Verarbeitung im Haus", "Erkennung und Speicherung laufen auf eigener Hardware im Netzwerk, nicht bei einem Clouddienst."),
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
      <div class="lp-grid">
        <div class="lp-card"><h3>Wie viel ist wirklich los?</h3><p>Zufahrten, Anlieferungen und Abholungen pro Tag, Woche und Monat. Mit Tagesverlauf statt Bauchgefühl.</p></div>
        <div class="lp-card"><h3>Wie lange steht etwas?</h3><p>Standzeiten von Fahrzeugen oder Containern, inklusive Auffälligkeiten nach oben.</p></div>
        <div class="lp-card"><h3>War nachts jemand da?</h3><p>Bewegung außerhalb der Betriebszeiten wird erkannt und gemeldet, ohne dass jemand aufbleibt.</p></div>
        <div class="lp-card"><h3>Stimmt die Dokumentation?</h3><p>Erfasste Vorgänge lassen sich gegen Lieferscheine oder Aufträge halten, wenn etwas unklar ist.</p></div>
      </div>

      <div class="ki-check">
        <h3>Erst ansehen, dann entscheiden</h3>
        <p>Ob sich eine Auswertung lohnt, hängt an der Anlage und an der Frage, die du beantwortet haben willst. Beim kostenlosen Potenzialcheck sehe ich mir die vorhandenen Kameras an und sage dir, was damit geht und was nicht. Ist die Anlage dafür nicht geeignet, erfährst du das an dem Tag und nicht nach dem ersten Rechnungsposten.</p>
        <div class="lp-cta-row" style="margin:0;">
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
        "label": "Datenschutzgerecht eingesetzt", "service_type": "Einführung von KI im Unternehmen, datenschutzgerecht umgesetzt",
        "published": KI_PUB_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
        "cta2_href": "/schulung/", "cta2_text": "Schulung für dein Team",
        "offers": ([offer_from("KI-Start", PRICES["ki_start"],
                               "Bestandsaufnahme, Werkzeug mit Vertrag, Leitplanken, Nutzungsrichtlinie, Schulung "
                               "und erste Anwendung, einmalig netto.")] if SHOW_FROM_PRICES else []),
        "desc": ("ChatGPT, Copilot & Co. datenschutzgerecht im Betrieb: Verträge, Nutzungsrichtlinie und Schulung "
                 "als Maßnahme zur KI-Kompetenz (Art. 4 KI-VO). Paket KI-Start."),
        "sub": "Viele lassen die Finger von KI, weil sie Datenschutz und Haftung nicht durchschauen. Die Hürde nehmen wir gemeinsam, danach nutzt ihr KI sauber und mit gutem Gewissen.",
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
            ("Wo das Modell läuft", "Eigene Hardware, EU-Rechenzentrum oder Anbieter mit Vertrag. Für jede Aufgabe die passende Stufe."),
            ("Auftragsverarbeitungsvertrag", "Welcher Anbieter einen anbietet, was darin stehen muss und wo die Daten tatsächlich liegen."),
            ("Nutzungsrichtlinie", "Eine verständliche Seite für die Belegschaft: erlaubte Werkzeuge, erlaubte Daten, Ansprechpartner."),
            ("Schulung der Mitarbeiter", "Artikel 4 der KI-Verordnung verlangt Maßnahmen, die die KI-Kompetenz im Unternehmen fördern."),
            ("Lokale KI-Server einrichten", "Ein Sprachmodell auf einem eigenen Server im Betrieb, das ohne Internetverbindung arbeitet. Für sensible Daten der sauberste Weg."),
            ("Bestandsaufnahme", "Welche KI-Werkzeuge im Betrieb bereits benutzt werden, weiß meist niemand. Das lässt sich klären."),
        ],
        "extra": """
      <h2>KI-Start: die Hürde nehmen wir gemeinsam</h2>
      <p>Viele Inhaber lassen die Finger von KI, während im selben Betrieb vielleicht schon jemand Kundendaten in einen privaten ChatGPT-Zugang tippt. Das Risiko verschwindet nicht, indem man KI verbietet, sondern indem man sie ordentlich einführt. Das Paket KI-Start hat sieben Schritte:</p>
      <ol class="lp-steps">
        <li><strong>Bestandsaufnahme:</strong> Wer nutzt heute schon welche KI, mit welchen Daten und über welche Konten?</li>
        <li><strong>Werkzeug mit Vertrag:</strong> eine bezahlte Business-Version mit Auftragsverarbeitungsvertrag und klaren Nutzungsbedingungen, etwa Microsoft 365 Copilot, ChatGPT Business oder Claude Team, möglichst mit Verarbeitung in der EU. Oder eine lokale KI im Haus, wenn die Daten den Betrieb nicht verlassen sollen.</li>
        <li><strong>Auftragsverarbeitung mit allen Dienstleistern</strong> prüfen und ablegen, nicht nur mit dem KI-Anbieter.</li>
        <li><strong>Technische Leitplanken:</strong> Zugriff nur über Firmenkonten, private KI-Konten auf Firmengeräten sperren, Rechte und Freigaben in Microsoft 365 aufräumen, bevor Copilot Dateien findet, die nie für alle gedacht waren.</li>
        <li><strong>Nutzungsrichtlinie:</strong> zwei Seiten, verständlich: was hineindarf, was nicht und wer Ansprechpartner ist.</li>
        <li><strong>Mitarbeitende befähigen:</strong> die <a href="/schulung/">Schulung</a> „KI sicher nutzen“ als Maßnahme zur KI-Kompetenz nach Artikel 4 der KI-Verordnung, mit Teilnahmenachweis.</li>
        <li><strong>Erste Anwendung im Alltag:</strong> Zusammenfassungen, Entwürfe für Dokumente und Mails, Auswertungen. Dort sieht das Team den Nutzen.</li>
      </ol>
      """ + KI_START_TEXT + """

      <h2>Drei Wege, und wann welcher passt</h2>
      <p>Die wichtigste Entscheidung fällt vor der ersten Zeile Code: wo die Daten verarbeitet werden. Danach richtet sich alles Weitere.</p>
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

      <h2>Was die KI-Verordnung von einem KMU verlangt</h2>
      <p>Artikel 4 der europäischen KI-Verordnung gilt seit dem 2. Februar 2025. Mit dem sogenannten Digital Omnibus (Verordnung (EU) 2026/1744, in Kraft seit dem 27. Juli 2026) wurde er entschärft: Ein Unternehmen, das KI-Systeme einsetzt, muss nicht mehr sicherstellen, dass jeder Beschäftigte einen bestimmten Wissensstand erreicht. Es muss aber Maßnahmen ergreifen, die die KI-Kompetenz der Menschen fördern, die damit arbeiten. Das gilt für den Betrieb, in dem drei Leute ChatGPT benutzen, genauso wie für Entwickler von Hochrisiko-Anwendungen.</p>
      <p>Ein festes Schulungsprogramm schreibt die Verordnung nicht vor. Verlangt wird, dass die Maßnahmen zur Rolle und zur tatsächlichen Nutzung passen und dass das Unternehmen sie belegen kann. In Deutschland ist die Bundesnetzagentur als Aufsichtsbehörde vorgesehen. Ein eigener Bußgeldtatbestand für Artikel 4 besteht derzeit nicht, was die Sache aber nicht erledigt: Entsteht durch falsche KI-Nutzung ein Schaden, steht die Frage im Raum, ob eine angemessene Unterweisung ihn verhindert hätte.</p>
      <div class="ki-note">
        <p>Praktisch heißt das zweierlei: eine kurze, verständliche Nutzungsrichtlinie und eine Unterweisung, die dokumentiert ist. Beides mache ich zusammen mit dir. Die <a href="/schulung/">IT-Sicherheitsschulung</a> enthält ein eigenes Modul zum sicheren und datenschutzgerechten Umgang mit KI-Werkzeugen und deckt damit den Teil ab, der die Belegschaft betrifft.</p>
      </div>

      <h2>Was in eine Nutzungsrichtlinie gehört</h2>
      <div class="lp-grid">
        <div class="lp-card"><h3>Welche Werkzeuge</h3><p>Eine kurze Liste der freigegebenen Anwendungen. Alles andere ist damit nicht freigegeben, ohne dass man jedes Werkzeug einzeln verbieten muss.</p></div>
        <div class="lp-card"><h3>Welche Daten</h3><p>Klar benannt, was nie in ein Chatfenster gehört: Kundendaten, Personaldaten, Zugangsdaten, Kalkulationen, Verträge.</p></div>
        <div class="lp-card"><h3>Wer prüft das Ergebnis</h3><p>KI-Ausgaben sind Entwürfe. Wer sie verantwortet, bevor sie den Betrieb verlassen, muss benannt sein.</p></div>
        <div class="lp-card"><h3>Wen man fragt</h3><p>Ein Ansprechpartner für den Fall, dass jemand unsicher ist. Ohne den landet im Zweifel doch wieder alles im Chatfenster.</p></div>
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
        "label": "Wechsel und Übernahme", "service_type": "Übernahme der IT-Betreuung von einem anderen Dienstleister",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
        "cta2_href": "/managed-it-service/", "cta2_text": "Laufende IT-Betreuung",
        "desc": ("Dein IT-Dienstleister ist nicht erreichbar oder hört auf? Übernahme-Checkliste, was du "
                 "vom alten Betreuer brauchst und wie eine geordnete Übernahme läuft."),
        "sub": "Dein ITler geht nicht ran? Ich schon. Und wenn du wechseln willst, sorge ich für eine geordnete Übernahme.",
        "intro": ("Den IT-Dienstleister wechselt niemand aus Lust. Meistens hat sich etwas angesammelt: "
                  "Anrufe, die keiner annimmt, Rückrufe nach Tagen, Rechnungen, die keiner nachvollziehen "
                  "kann. Oder der Kollege, der die IT nebenbei gemacht hat, ist nicht mehr da. Schwierig ist "
                  "dabei nicht der Wechsel selbst, sondern das Wissen, das beim alten Betreuer liegt: "
                  "Kennwörter, Lizenzen, wie das Netzwerk aufgebaut ist und wohin die Datensicherung läuft. "
                  "<strong>Ich übernehme deine IT so, dass dieses Wissen bei dir landet</strong>, "
                  "aufgeschrieben und mit einem Ansprechpartner, der zurückruft."),
        "raw_intro": True,
        "cards_h2": "IT-Dienstleister wechseln: was bei der Übernahme passiert",
        "cards": [
            ("Bestandsaufnahme", "Welche Geräte, Programme, Lizenzen und Verträge es gibt, wer welche Zugänge hat und wo die Daten liegen. Schriftlich."),
            ("Zugänge auf dich", "Administrator-Kennwörter, Microsoft-365-Konten, Domain, Router und Firewall gehören dem Betrieb, nicht dem Dienstleister. So richte ich es ein."),
            ("Datensicherung prüfen", "Läuft die Sicherung, und lässt sie sich zurückspielen? Das teste ich, bevor ich irgendetwas umbaue."),
            ("Geordneter Übergang", "Der alte Betreuer bleibt zuständig, bis die Übergabe steht. Umgestellt wird in Ruhe und nicht am Montagmorgen."),
            ("Dokumentation", "Am Ende hast du eine Übersicht deiner IT, die auch ohne mich lesbar ist."),
            ("Laufende Betreuung", "Danach geht es mit einer planbaren Monatspauschale weiter. Vertragskunden werden bevorzugt behandelt."),
        ],
        "extra": """
      <h2>Übernahme-Checkliste: Was du vom alten IT-Betreuer brauchst</h2>
      <p>Diese Liste kannst du deinem bisherigen Dienstleister so weitergeben. Je mehr davon vorliegt, desto schneller und billiger wird die Übernahme.</p>
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
        <li><strong>Kennenlernen:</strong> Beim kostenlosen IT-Schnellcheck sehe ich mir deine IT 30 bis 45 Minuten vor Ort an. Du bekommst einen schriftlichen Bericht, auch wenn wir danach nicht zusammenarbeiten.</li>
        <li><strong>Übergabe:</strong> Mit der Checkliste oben holen wir die Zugänge und Unterlagen vom alten Betreuer. Bis das steht, bleibt er zuständig.</li>
        <li><strong>Absichern:</strong> Datensicherung testen, Zugänge auf den Betrieb umstellen, alte Fernwartungszugänge abschalten.</li>
        <li><strong>Betreuung:</strong> Danach eine planbare Monatspauschale ab 149 € netto, monatlich kündbar.</li>
      </ol>
      <p>Nicht gleich wechseln? Ich springe auch als Vertretung ein, wenn dein IT-Betreuer im Urlaub oder krank ist, abgerechnet nach Aufwand.</p>
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
        "label": "Microsoft 365, Copilot, Virenschutz", "service_type": "Lizenzvertrieb mit Einrichtung und Verwaltung für Unternehmen",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
        "cta2_href": "/microsoft-365-betreuung/", "cta2_text": "Microsoft 365 Betreuung",
        "desc": ("Microsoft 365, Copilot, ESET-Virenschutz und Datensicherung für Unternehmen: Lizenz, "
                 "Einrichtung und Verwaltung aus einer Hand. Raum München Ost."),
        "sub": "Eine Lizenz zu kaufen ist der kleinste Teil. Richtig eingerichtet, abgesichert und verwaltet wird sie bei mir gleich mit.",
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
            ("Microsoft 365", "E-Mail, Teams, OneDrive und Office mit Zwei-Faktor-Anmeldung und einem Rechtekonzept, das zum Betrieb passt."),
            ("Microsoft 365 Copilot", "Copilot für Firmenkonten, nachdem Rechte und Freigaben aufgeräumt sind. Sonst findet Copilot Dateien, die nie für alle gedacht waren."),
            ("ESET Virenschutz", "Zentral verwalteter Schutz auf allen Geräten. Warnungen und auslaufende Lizenzen laufen bei mir auf, statt unbemerkt zu bleiben."),
            ("Datensicherung", "Sicherung von Microsoft 365, Servern und Rechnern, mit einer Kopie außer Haus."),
            ("ChatGPT und Claude im Team", "Geschäftliche Konten mit Vertrag statt privater Zugänge. Den Vertrag schließt ihr direkt beim Anbieter, ich richte die Konten ein und verwalte Nutzer und Rechte."),
            ("Laufzeiten im Blick", "Wer kommt, wer geht, was läuft wann aus. Lizenzen werden angepasst, statt ungenutzt weiterzulaufen."),
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
        "slug": "software-nach-mass", "nav": "Software nach Maß", "group": "ki",
        "title": "Software entwickeln lassen für kleine Betriebe | Grundke IT",
        "h1": "Software nach Maß für kleine Betriebe",
        "label": "Das nervt jede Woche?", "service_type": "Individuelle Softwareentwicklung und Betrieb für kleine Unternehmen",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
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
        "sub": "Doppelt erfasste Daten, Excel-Listen, Zettel am Monitor: Daraus wird eine kleine Anwendung, die ich baue und weiter betreue.",
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
            ("Aus der Liste wird eine Anwendung", "Was heute in Excel oder einer alten Access-Datenbank gepflegt wird, bekommt Eingabemasken, Prüfungen und einen Verlauf. Alle sehen denselben Stand."),
            ("Schnittstellen statt Abtippen", "Lexware Office und viele Auftrags- und Rechnungsprogramme haben Schnittstellen. Kunden, Aufträge und Angebotsentwürfe lassen sich darüber anlegen und abgleichen."),
            ("Rechte und Rollen", "Büro, Werkstatt und Chef arbeiten mit derselben Anwendung, aber nicht mit denselben Rechten."),
            ("Im Browser, auch am Handy", "Nichts zu installieren. Die Anwendung läuft im Browser, auf der Baustelle genauso wie im Büro."),
            ("Daten in Deutschland", "Betrieben auf einem Server in Deutschland mit Auftragsverarbeitungsvertrag oder auf Hardware bei dir im Netzwerk. Eure Daten könnt ihr jederzeit exportieren."),
            ("Betrieb und Pflege", "Updates, Datensicherung und Anpassungen, wenn sich ein Ablauf ändert. Dafür gibt es einen festen Monatsbetrag."),
        ],
        "extra": """
      <h2>Drei Beispiele</h2>
      <p>Das erste läuft täglich, das zweite ist im Aufbau, das dritte ist ein typischer Fall. Kundenprojekte nenne ich ohne Namen.</p>

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
        "label": "Eure Website bringt keine Anfragen?", "service_type": "Technische Umsetzung von Websites für kleine Unternehmen",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
        "trust": TRUST_FESTPREIS,
        "prices_h2": "Was das kostet",
        "prices_intro": ("Richtwerte, alle Preise netto. Den Festpreis bekommst du nach dem kostenlosen Check. Zu jeder "
                         "Website gehört der laufende Betrieb, damit sie sicher bleibt und gefunden wird."),
        "prices": [
            ("Website Start", "ab " + eur(PRICES["website_start"]),
             "Bis fünf Seiten auf geprüfter Vorlage, fürs Handy gebaut, Impressum und Datenschutzerklärung an der "
             "richtigen Stelle, strukturierte Daten, Google-Unternehmensprofil eingerichtet.", False, EINMALIG),
            ("Website Ausbau", "ab " + eur(PRICES["website_ausbau"]),
             "Bis 15 Seiten mit eigenen Seiten je Leistung und Ort und Antworten auf häufige Kundenfragen. Umzug "
             "aus der alten Seite mit Weiterleitungen. Die Texte liefert ihr, ich sage euch, welche Fragen fehlen.",
             False, EINMALIG),
            ("Laufender Betrieb", "ab " + eur(PRICES["website_betrieb"]),
             "Hosting, Updates, Sicherheit, Datensicherung und ein monatlicher Bericht, wie die Seite gefunden wird.",
             False, "/ Monat zzgl. MwSt."),
        ] if SHOW_FROM_PRICES else [],
        "offers": [
            offer_from("Website Start", PRICES["website_start"], "Bis fünf Seiten auf geprüfter Vorlage, einmalig netto."),
            offer_from("Website Ausbau", PRICES["website_ausbau"], "Bis 15 Seiten inklusive Umzug, einmalig netto."),
            offer_from("Laufender Betrieb", PRICES["website_betrieb"], "Hosting, Updates, Sicherheit, Bericht; je Monat netto.", monthly=True),
        ] if SHOW_FROM_PRICES else [],
        "cta2_href": "/kontakt/", "cta2_text": "Sichtbarkeits-Check anfragen",
        "desc": ("Website erstellen lassen oder modernisieren: schnell, fürs Handy gebaut, für Google und "
                 "KI-Assistenten lesbar aufgebaut. Technische Umsetzung, Raum München Ost."),
        "sub": "Eine Website, die am Handy schnell lädt, bei Google gefunden wird und so aufgebaut ist, dass ChatGPT und Co. sie lesen und zitieren können. Ich setze sie technisch um, die Optik kommt aus geprüften Vorlagen.",
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
            ("Fürs Handy gebaut", "Die meisten Besucher kommen über das Telefon. Die Seite wird zuerst dafür gebaut, mit Anruf- und WhatsApp-Knopf im Daumenbereich."),
            ("Schlank und schnell", "Kein Baukasten mit fünfzig Erweiterungen, sondern schlankes HTML. Die Seite lädt auch im Mobilnetz schnell."),
            ("Gefunden bei Google", "Eine eigene Seite je Leistung und Ort, saubere Titel, strukturierte Daten und ein gepflegtes Google-Unternehmensprofil."),
            ("Lesbar für KI-Assistenten", "ChatGPT, Gemini und Copilot zitieren vor allem Seiten, die klare Antworten auf echte Kundenfragen geben. Darauf ist der Aufbau ausgelegt."),
            ("Datenschutz-Technik", "Schriften lokal, kein Tracking ohne Einwilligung, Impressum und Datenschutzerklärung an der richtigen Stelle. Die Rechtstexte selbst verantwortet ihr."),
            ("Betrieb und Updates", "Hosting, Sicherheitsupdates, Datensicherung und ein monatlicher Bericht, wie die Seite gefunden wird. Rein technisch."),
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
        <div class="lp-cta-row" style="margin:0;">
          <a href="tel:+491782584438" class="btn-p">Check vereinbaren</a>
          <a href="/kontakt/" class="btn-g">Lieber schreiben</a>
        </div>
      </div>
""",
        "faqs": [
            ("Was kostet eine Website für einen kleinen Betrieb?",
             ("Eine Website mit bis zu fünf Seiten beginnt bei rund " + eur_txt(PRICES["website_start"]) + " netto, eine größere mit eigenen "
              "Seiten je Leistung und Ort und dem Umzug aus der alten Seite bei rund " + eur_txt(PRICES["website_ausbau"]) + ". Für Hosting, "
              "Updates, Sicherheit und den monatlichen Sichtbarkeitsbericht kommen ab " + eur_txt(PRICES["website_betrieb"]) + " im Monat dazu. Den "
              "Festpreis bekommst du nach dem kostenlosen Check.")
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
        "label": "E-Rechnung", "service_type": "Umstellung auf die E-Rechnung für kleine Unternehmen",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
        "trust": TRUST_FESTPREIS,
        "cta2_href": "/ki-automatisierung/", "cta2_text": "Abläufe automatisieren",
        "offers": ([
            offer_from("E-Rechnung umstellen", PRICES["erechnung"],
                       "Empfang, Ausstellen, Ablage und Weg zur Steuerberatung im Standardfall, einmalig netto."),
            offer_from("E-Rechnung mit eigenem Export", PRICES["erechnung_export"],
                       "Export aus Fachanwendung, Excel-Kalkulation oder Vorsystem, einmalig netto."),
        ] if SHOW_FROM_PRICES else []),
        "desc": ("E-Rechnung empfangen seit 2025, ausstellen ab 2027 oder 2028: Fristen, Ausnahmen, Check in "
                 "drei Fragen und Hilfe bei Programmwahl und Umstellung."),
        "sub": "Empfangen müsst ihr sie schon. Ausstellen müsst ihr sie ab 2027 oder 2028. Hier steht, was das für euren Betrieb heißt, und wie ihr zu einem Programm kommt, das beides kann.",
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
            ("Programm finden", "Kann euer Rechnungsprogramm keine E-Rechnung, oder gibt es noch gar keins, suche ich mit euch eins aus, das zu Betrieb und Steuerberatung passt."),
            ("Empfang einrichten", "Ein Postfach für E-Rechnungen, die Anzeige der Formate und die Weitergabe an die Buchhaltung."),
            ("Ausstellen umstellen", "Euer Programm einrichten oder anpassen, oder einen Export aus eurer Fachanwendung bauen, wenn die Rechnungsdaten von dort kommen."),
            ("Ablage und Steuerberatung", "E-Rechnungen bleiben im Originalformat abgelegt und laufen dorthin, wo eure Steuerberatung sie braucht."),
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
      <div class="ki-note">
        <p><strong>Zur Einordnung:</strong> Das ist die allgemeine Rechtslage nach dem zweiten Schreiben des Bundesfinanzministeriums zur E-Rechnung vom 15. Oktober 2025, das das erste Schreiben von 2024 ersetzt, und keine Steuerberatung. Ob und ab wann die Pflicht deinen Betrieb genau trifft, klärst du mit deiner Steuerberatung. Ich baue die Umsetzung.</p>
      </div>
      {preise}
""".replace("{preise}", (
            '<div class="ki-check">\n        <h3>Umstellung zum Festpreis</h3>\n'
            "        <p>Im Standardfall ab " + eur(PRICES["erechnung"]) + " netto: Bestandsaufnahme, Programm "
            "auswählen oder umstellen, Empfang und Ablage einrichten, Weg zur Steuerberatung. Kommen die "
            "Rechnungsdaten aus einer Fachanwendung, einer Excel-Kalkulation oder einem Vorsystem und braucht "
            "es einen eigenen Export, ab " + eur(PRICES["erechnung_export"]) + " netto. Die Lizenz für das "
            "Rechnungsprogramm zahlt ihr direkt beim Anbieter. Ab 4.000 Euro Ausgaben kann der "
            '<a href="/digitalbonus-bayern/">Digitalbonus Bayern</a> bis zur Hälfte übernehmen.</p>\n'
            '        <div class="lp-cta-row" style="margin:0;">\n'
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
        "label": "Förderung", "service_type": "Umsetzung förderfähiger Digitalisierungs- und IT-Sicherheitsprojekte",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE,
        "trust": None,
        "cta2_href": "/software-nach-mass/", "cta2_text": "Software nach Maß",
        "desc": ("Digitalbonus Bayern bis Ende 2027: bis zu 50 % Zuschuss ab 4.000 € für Software, KI und "
                 "IT-Sicherheit. Voraussetzungen, Antrag über ELSTER, die Haken."),
        "sub": "Bis Ende 2027 übernimmt der Freistaat bei kleinen Unternehmen bis zur Hälfte vieler Software- und Sicherheitsprojekte, im Standard bis 7.500 Euro. Ich liefere die Unterlagen, den Antrag stellt ihr selbst.",
        "intro": ("Der Digitalbonus Bayern ist ein Zuschuss des Freistaats für kleine gewerbliche Unternehmen. "
                  "Gefördert werden Leistungen externer Anbieter: Software, die für euren Betrieb gebaut oder "
                  "eingeführt wird, KI-Anwendungen und Maßnahmen für die IT-Sicherheit, dort sogar Hardware "
                  "wie Firewall und Datensicherung. <strong>Für viele Projekte heißt das: bis zu 50 Prozent "
                  "zurück.</strong> Es gibt aber Regeln, an denen die Förderung scheitert, wenn man sie nicht "
                  "kennt. Die wichtigsten stehen weiter unten."),
        "raw_intro": True,
        "cards_h2": "Wer was macht",
        "cards": [
            ("Was ich liefere", "Projektbeschreibung, Kostenaufstellung und die technischen Angaben, die ihr für den Antrag braucht."),
            ("Was ihr macht", "Den Antrag über euer ELSTER-Unternehmenskonto stellen und die Eingangsbestätigung abwarten."),
            ("Zwei Anträge möglich", "Je einer für Digitalisierung und für IT-Sicherheit, zusammen bis zu 15.000 Euro Zuschuss im Standard."),
            ("Am Ende", "Projekt umsetzen, Rechnung bezahlen, Verwendungsnachweis einreichen. Die Unterlagen dafür bereite ich vor."),
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
        "slug": "ratgeber", "nav": "Ratgeber", "group": "ratgeber", "kind": "hub",
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
        "label": "Ratgeber", "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE, "trust": None,
        "cta_top": RATGEBER_CTA,
        "cta2_href": "/fernwartung/", "cta2_text": "Fernwartung starten",
        "desc": ("Server ausgefallen, Phishing-Mail geklickt, E-Mails kommen nicht an, NAS defekt: was du in den "
                 "ersten 15 Minuten selbst tun kannst und wann du anrufst."),
        "sub": "Was du in den ersten Minuten selbst tun kannst, was du besser lässt, und ab wann ein Anruf schneller ist.",
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
        "label": "Die ersten 15 Minuten", "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE, "trust": None,
        "cta_top": RATGEBER_CTA,
        "cta2_href": "/fernwartung/", "cta2_text": "Fernwartung starten",
        "desc": ("Server ausgefallen, keiner kommt an die Daten? Was du in den ersten 15 Minuten prüfen kannst, "
                 "was du auf keinen Fall tun solltest und wann du anrufen solltest."),
        "sub": "Erst schauen, dann handeln. Die meisten Ausfälle lassen sich eingrenzen, bevor jemand kommt.",
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
        "label": "Die ersten 15 Minuten", "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE, "trust": None,
        "cta_top": RATGEBER_CTA,
        "cta2_href": "/schulung/", "cta2_text": "Schulung für dein Team",
        "desc": ("Auf eine Phishing-Mail geklickt, Passwort eingegeben oder Anhang geöffnet? Was in den ersten "
                 "15 Minuten zu tun ist, je nachdem was passiert ist."),
        "sub": "Ruhe bewahren hilft mehr als Löschen. Was zu tun ist, hängt davon ab, was nach dem Klick passiert ist.",
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
        "label": "Die ersten 15 Minuten", "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE, "trust": None,
        "cta_top": RATGEBER_CTA,
        "cta2_href": "/microsoft-365-betreuung/", "cta2_text": "Microsoft 365 Betreuung",
        "desc": ("E-Mails kommen nicht an oder landen beim Empfänger im Spam? So grenzt du in 15 Minuten ein, "
                 "ob es an Outlook, am Postfach oder an der Domain liegt."),
        "sub": "Erst klären, ob keine Mails hereinkommen oder ob deine nicht ankommen. Das sind zwei verschiedene Probleme.",
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
        "label": "Die ersten 15 Minuten", "service_type": "Ratgeber",
        "published": NEW_DATE, "modified": NEW_DATE, "modified_disp": NEW_DATE_DISP,
        "extra_style": NEW_PAGE_STYLE, "trust": None,
        "cta_top": RATGEBER_CTA,
        "cta2_href": "/it-sicherheit-backup/", "cta2_text": "Backup richtig aufsetzen",
        "desc": ("Netzwerkspeicher meldet eine defekte Festplatte oder startet nicht mehr? Was du in den ersten 15 "
                 "Minuten tun kannst, damit die Daten nicht verloren gehen."),
        "sub": "Eine defekte Festplatte im NAS ist meist kein Datenverlust. Dazu wird sie erst durch die falschen Handgriffe danach.",
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


def render_service(s, places, services):
    slug = s["slug"]
    # Voller Titel fuer OG und Schema: beim Hub steht der zweite Teil als Akzentzeile
    # im Einstieg, inhaltlich bleibt die Ueberschrift dieselbe wie vorher.
    h1_full = (s["h1"] + " – " + s["hero"]["accent"] if s.get("hero") else s["h1"]).replace("&amp;", "&")
    og_title = h1_full + " – Andreas Grundke IT-Service"
    h = head(s["title"], s["desc"], slug, og_title, s["desc"],
             h1_full + " – Andreas Grundke IT-Service")

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
    elif s.get("kind") == "hub":
        main_schema = None
    else:
        main_schema = service_schema
    schema = [breadcrumb(s["nav"], slug)] + ([main_schema] if main_schema else []) + [
              faq_schema(s["faqs"]),
              webpage_schema(s["title"], s["desc"], slug,
                             s.get("published"), s.get("modified"))]
    # Optionale Zusatzknoten (z. B. der kostenlose KI-Potenzialcheck als eigener Service)
    schema.extend(s.get("extra_schema", []))

    price_html = ""
    if s.get("prices"):
        # Eintrag: (Stufe, Betrag, Beschreibung, hervorgehoben[, Einheit]). Ohne Einheit gilt
        # der Monatspreis der Betreuungspakete.
        cells = "".join(
            '\n        <div class="lp-price{feat}">\n          <div class="tier">{t}</div>\n'
            '          <div class="amount">{a}<span> {u}</span></div>\n'
            '          <div class="desc">{d}</div>\n        </div>'.format(
                feat=" feat" if pr[3] else "", t=esc(pr[0]), a=esc(pr[1]), d=esc(pr[2]),
                u=esc(pr[4] if len(pr) > 4 else "/ Monat zzgl. MwSt."))
            for pr in s["prices"])
        price_html = ("\n      <h2>{h}</h2>\n"
                      "      <p>{i}</p>\n"
                      '      <div class="lp-price-grid">{cells}\n      </div>\n{after}').format(
                          cells=cells,
                          h=s.get("prices_h2", "Pakete &amp; Preise"),
                          i=s.get("prices_intro", "Transparente Monatspauschalen – welches Paket passt, "
                                                  "klären wir im kostenlosen Erstgespräch:"),
                          after=s.get("prices_after", ""))

    intro = s["intro"] if s.get("raw_intro") else esc(s["intro"])

    cta_row = """<div class="lp-cta-row">
        <a href="tel:+491782584438" class="btn-p">Kostenloses Erstgespräch</a>
        <a href="/kontakt/" class="btn-g">Anfrage senden</a>
      </div>"""
    if s.get("cta_top"):
        cta_row = ('<div class="lp-cta-row">' + "".join(
            '\n        <a href="{h}" class="{c}">{t}</a>'.format(h=h, c=c, t=esc(t))
            for h, t, c in s["cta_top"]) + "\n      </div>")
    hero = s.get("hero")
    if hero:
        # Eigener Einstieg fuer Bereichs-Hubs (KI im Betrieb): grosse Ueberschrift wie auf
        # der Startseite und daneben die Unterseiten als direkte Wege.
        paths = "".join(
            '\n          <li><a href="{h}"><span class="lp-path-t">{t}</span>'
            '<span class="lp-path-d">{d}</span></a></li>'.format(h=h, t=esc(t), d=esc(d))
            for t, d, h in hero["paths"])
        top = """<article class="lp-wrap lp-wrap--hero">
  <div class="lp-hero">
    <div class="inner lp-hero-grid">
      <div>
        {crumbs}
        <h1 class="lp-hero-h1">{h1} <span class="lp-hero-accent">{accent}</span></h1>
        <p class="s-sub">{sub}</p>
        {cta_row}
      </div>
      <nav class="lp-paths" aria-label="{paths_label}">
        <h2 class="lp-paths-h">{paths_label}</h2>
        <ul>{paths}
        </ul>
      </nav>
    </div>
  </div>
  <div class="inner">
    <div class="lp-content">
""".format(crumbs=crumbs_html(s["nav"], slug), h1=s["h1"], accent=hero["accent"], sub=esc(s["sub"]),
           cta_row=cta_row, paths_label=esc(hero["paths_label"]), paths=paths)
    else:
        top = """<article class="lp-wrap">
  <div class="inner">
    <div class="lp-content">
      {crumbs}
      <div class="s-label">{label}</div>
      <h1 class="s-title">{h1}</h1>
      <p class="s-sub">{sub}</p>

      {cta_row}
""".format(crumbs=crumbs_html(s["nav"], slug), label=esc(s["label"]), h1=s["h1"], sub=esc(s["sub"]),
           cta_row=cta_row)

    related = ""
    if slug.startswith("ki-") and slug != KI_HUB[1]:
        # Rueckweg zum Hub und Querverweise zwischen den KI-Bereichen
        siblings = [sv for sv in services if sv["slug"].startswith("ki-")
                    and sv["slug"] not in (slug, KI_HUB[1])]
        links = " und ".join('<a href="/{s}/">{n}</a>'.format(s=sv["slug"], n=esc(sv["nav"])) for sv in siblings)
        related = ('\n      <p class="lp-related">Mehr aus dem Bereich <a href="/{hub}/">{hubn}</a>: '
                   '{links}.</p>\n').format(hub=KI_HUB[1], hubn=esc(KI_HUB[0]), links=links)
    elif slug.startswith(RATGEBER_HUB[1] + "/"):
        siblings = [sv for sv in services if sv["slug"].startswith(RATGEBER_HUB[1] + "/")
                    and sv["slug"] != slug]
        links = ", ".join('<a href="/{s}/">{n}</a>'.format(s=sv["slug"], n=esc(sv["nav"])) for sv in siblings)
        related = ('\n      <p class="lp-related">Weitere Ratgeber aus der Reihe <a href="/{hub}/">Die ersten '
                   '15 Minuten</a>: {links}.</p>\n').format(hub=RATGEBER_HUB[1], links=links)

    cards_block = ""
    if s.get("cards"):
        cards_block = ('\n      <h2>{h}</h2>\n      <div class="lp-grid">{c}\n      </div>\n').format(
            h=s.get("cards_h2", "Das steckt drin"), c=cards_html(s["cards"]))
    trust = s.get("trust", TRUST_DEFAULT)
    trust_block = ('\n      <div class="lp-trust">\n        ' + trust + '\n      </div>\n') if trust else ""
    intro_html = intro if intro.lstrip().startswith("<div") else "<p>" + intro + "</p>"
    main = top + """
      {intro}
{cards_block}{extra}{prices}{trust_block}
      <h2>{faq_h2}</h2>{faqs}
{related}{author}
      <div class="lp-cta-row" style="margin-top:2.5rem;">
        <a href="tel:+491782584438" class="btn-p">Jetzt anrufen · 0178 258 44 38</a>
        <a href="{cta2_href}" class="btn-g">{cta2_text}</a>
      </div>
    </div>
  </div>
</article>""".format(intro=intro_html, cards_block=cards_block, trust_block=trust_block,
                     prices=price_html, faqs=faq_html(s["faqs"]),
                     author=author_box(s.get("modified_disp")), related=related,
                     faq_h2=s.get("faq_h2", "Häufige Fragen"),
                     extra=s.get("extra", ""),
                     cta2_href=s.get("cta2_href", "/it-service-grasbrunn/"),
                     cta2_text=esc(s.get("cta2_text", "IT-Service in deiner Region")))

    return slug, page(h, schema, main, places, services, s.get("extra_style", ""), slug=slug)


# --------------------------------------------------------------------------- #
#  Sitemap                                                                     #
# --------------------------------------------------------------------------- #

STATIC_URLS = [   # (Pfad, Prioritaet, lastmod) -- lastmod der Startseite = ihr dateModified
    ("/", "1.0", NEW_DATE),
    ("/kontakt/", "0.7", "2026-09-23"),
    ("/schulung/", "0.8", "2026-05-01"),
    ("/empfehlungen/", "0.7", "2026-05-01"),
]


def write_sitemap(places, services):
    urls = []
    for loc, prio, mod in STATIC_URLS:
        urls.append((loc, mod, prio))
    urls.append(("/barrierefreiheit/", TODAY, "0.3"))
    for s in services:
        urls.append(("/" + s["slug"] + "/", s.get("modified", TODAY), "0.8"))
    for p in places:
        urls.append(("/it-service-" + p["slug"] + "/", TODAY, "0.8"))
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


if __name__ == "__main__":
    main()
