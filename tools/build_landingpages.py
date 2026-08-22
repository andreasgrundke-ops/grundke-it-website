#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_landingpages.py
Version : 1.0
Autor   : Andreas Grundke IT-Service (Grundke IT-Service)
Datum   : 2026-06-15
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

Aufruf: python tools/build_landingpages.py
"""

import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://grundke-it.de"
PHONE = "+491782584438"
PHONE_DISP = "0178 258 44 38"
TODAY = "2026-06-18"          # dateModified (Stand der letzten Aktualisierung)
TODAY_DISP = "18. Juni 2026"  # sichtbares Datum fuer Leser (E-E-A-T-Freshness-Signal)
PUB_DATE = "2026-06-15"       # datePublished (Ersterstellung der Landingpages)
PERSON_ID = DOMAIN + "/#andreas"          # @id der Person Andreas Grundke (Startseite)
BUSINESS_ID = DOMAIN + "/#localbusiness"  # @id des Unternehmens (Startseite)
WEBSITE_ID = DOMAIN + "/#website"         # @id der Website (Startseite)
# Der KI-Bereich ist juenger als die uebrigen Landingpages und fuehrt deshalb eigene
# Datumsangaben. So bleibt dateModified der Orts-/Leistungsseiten ehrlich (kein
# kuenstliches Hochsetzen der Freshness-Signale nur wegen eines neuen Footer-Links).
KI_DATE = "2026-08-22"          # dateModified der KI-Seiten
KI_DATE_DISP = "22. August 2026"
KI_PUB_DATE = "2026-08-22"      # datePublished der KI-Seiten

# --------------------------------------------------------------------------- #
#  Gemeinsame Bausteine                                                        #
# --------------------------------------------------------------------------- #

STYLE = """  <style>
    .lp-wrap { margin-top:var(--nav-h); padding:clamp(3rem,8vw,6rem) 0; }
    .lp-content { max-width:880px; }
    .lp-content h2 { font-family:var(--fh); font-size:clamp(1.3rem,3vw,1.8rem); font-weight:800; color:var(--text); letter-spacing:-.02em; margin:2.6rem 0 1rem; }
    .lp-content p { font-size:.95rem; color:var(--text2); line-height:1.8; margin-bottom:1rem; }
    .lp-content strong { color:var(--text); }
    .lp-cta-row { display:flex; flex-wrap:wrap; gap:1rem; margin:2rem 0; }
    .lp-btn { display:inline-flex; align-items:center; gap:.6rem; padding:.9rem 1.6rem; border-radius:8px; font-family:var(--fh); font-weight:700; font-size:.95rem; text-decoration:none; transition:transform .2s,box-shadow .2s; }
    .lp-btn.primary { background:var(--cyan); color:#04263a; }
    .lp-btn.primary:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(38,189,239,.25); }
    .lp-btn.ghost { border:1px solid var(--border); color:var(--text); }
    .lp-btn.ghost:hover { border-color:var(--cyan); }
    .lp-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; margin:1.5rem 0; }
    .lp-card { background:var(--bg2); border:1px solid var(--border); border-left:3px solid var(--cyan); border-radius:12px; padding:1.3rem; }
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
    .faq-item { border-bottom:1px solid var(--border); padding:1.1rem 0; }
    .faq-item h3 { font-family:var(--fh); font-size:1rem; font-weight:700; color:var(--text); margin-bottom:.5rem; }
    .faq-item p { font-size:.9rem; color:var(--text2); line-height:1.7; margin:0; }
    .lp-trust { background:var(--bg2); border:1px solid var(--border); border-radius:16px; padding:1.6rem; margin:2rem 0; font-size:.9rem; color:var(--text2); line-height:1.7; }
    .foot-links { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1.5rem; padding:2rem 0; border-bottom:1px solid var(--border); }
    .foot-links h4 { font-family:var(--fh); font-size:.8rem; font-weight:700; color:var(--text); margin-bottom:.7rem; letter-spacing:.04em; }
    .foot-links a { display:block; font-size:.85rem; color:var(--text2); text-decoration:none; padding:.2rem 0; }
    .foot-links a:hover { color:var(--cyan); }
    .lp-author { display:flex; gap:1.1rem; align-items:flex-start; background:var(--bg2); border:1px solid var(--border); border-left:3px solid var(--accent); border-radius:14px; padding:1.4rem 1.5rem; margin:2.5rem 0 1rem; }
    .lp-author img { width:56px; height:56px; border-radius:50%; flex-shrink:0; background:var(--bg); object-fit:contain; border:1px solid var(--border); }
    .lp-author-body { font-size:.88rem; color:var(--text2); line-height:1.7; }
    .lp-author-name { font-family:var(--fh); font-weight:800; color:var(--text); font-size:1rem; }
    .lp-author-role { display:block; font-size:.8rem; color:var(--text3); margin:.1rem 0 .6rem; }
    .lp-author-meta { margin-top:.7rem; font-size:.78rem; color:var(--text3); }
    .lp-author-meta a { color:var(--cyan); text-decoration:none; }
  </style>"""

NAV = """<header class="site-header">
<nav aria-label="Hauptnavigation">
  <div class="nav-inner inner">
    <a href="/" class="logo" title="Grundke IT-Service – München Ost"><picture><source srcset="../assets/img/logo-grundke-it-white-480.webp" type="image/webp"><img class="logo-img" src="../assets/img/logo-grundke-it-white-480.png" alt="Grundke IT-Service" width="180" height="60" /></picture></a>
    <a class="nav-loc" href="https://www.google.com/maps/place/IT-Service+-+Andreas+Grundke/@48.0944159,11.7631063,17z/data=!3m1!4b1!4m6!3m5!1s0x479de3eede6923f3:0x1ad9e3b1fcbd1081!8m2!3d48.0944123!4d11.7656812!16s%2Fg%2F11j7r45y6q" target="_blank" rel="noopener" aria-label="Standort auf Google Maps anzeigen"><svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>München Ost</a>
    <ul class="nav-links">
      <li><a href="/">Startseite</a></li>
      <li><a href="/#leistungen">Leistungen</a></li>
      <li><a href="/ki-fuer-kmu/">KI im Betrieb</a></li>
      <li><a href="/#preise">Preise</a></li>
      <li><a href="/kontakt/">Kontakt</a></li>
      <li><a href="tel:+491782584438" class="nav-cta"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.62 3.4 2 2 0 0 1 3.6 1.22h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.8a16 16 0 0 0 6 6l.94-.94a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg><span>Jetzt anrufen</span></a></li>
    </ul>
    <button class="hamburger" id="ham" aria-label="Menü"><span></span><span></span><span></span></button>
  </div>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <a href="/">Startseite</a>
  <a href="/#leistungen">Leistungen</a>
  <a href="/ki-fuer-kmu/">KI im Betrieb</a>
  <a href="/kontakt/">Kontakt</a>
  <a href="/fernwartung/" style="color:var(--cyan);font-weight:700;">&#9889; Fernwartung starten</a>
  <a href="tel:+491782584438" class="m-cta">Jetzt anrufen · 0178 258 44 38</a>
</div>
</header>"""

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
  <link rel="stylesheet" href="../assets/css/fonts.css"/>
  <link rel="stylesheet" href="../assets/css/style.css"/>
""".format(title=esc(title), desc=esc(desc), canonical=canonical,
           og_title=esc(og_title), og_desc=esc(og_desc), og_alt=esc(og_alt),
           domain=DOMAIN)


def footer(places, services):
    place_links = "".join(
        '\n        <a href="/it-service-{slug}/">IT-Service {name}</a>'.format(slug=p["slug"], name=esc(p["name"]))
        for p in places)
    service_links = "".join(
        '\n        <a href="/{slug}/">{name}</a>'.format(slug=s["slug"], name=esc(s["nav"]))
        for s in services)
    return """<footer class="site-footer">
  <div class="inner">
    <div class="foot-links">
      <div>
        <h4>Standorte</h4>{place_links}
      </div>
      <div>
        <h4>Leistungen</h4>{service_links}
      </div>
      <div>
        <h4>Kontakt</h4>
        <a href="tel:+491782584438">0178 258 44 38</a>
        <a href="mailto:info@grundke-it.de">info@grundke-it.de</a>
        <a href="/kontakt/">Kontaktseite</a>
        <a href="/fernwartung/">Fernwartung starten</a>
      </div>
    </div>
    <nav class="foot-legal" aria-label="Rechtliche Hinweise">
      <a href="/impressum/">Impressum</a>
      <a href="/datenschutz/">Datenschutz</a>
      <a href="/agb/">AGB</a>
      <a href="/barrierefreiheit/">Barrierefreiheit</a>
    </nav>
    <div class="foot-bottom">
      <span>© 2026 Grundke IT-Service · Andreas Grundke · Beethovenring 16 · 85630 Grasbrunn</span>
      <span class="foot-ci">CI 2026.01 · grundke-it.de</span>
    </div>
  </div>
</footer>""".format(place_links=place_links, service_links=service_links)


def breadcrumb(name, slug):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Startseite", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": DOMAIN + "/" + slug + "/"},
        ],
    }


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
        '        <img src="/assets/img/logo-grundke-it-badge.png" alt="Logo Andreas Grundke IT-Service" width="56" height="56" loading="lazy"/>\n'
        '        <div class="lp-author-body">\n'
        '          <span class="lp-author-name">Andreas Grundke</span>\n'
        '          <span class="lp-author-role">Inhaber · Fachinformatiker für Systemintegration</span>\n'
        '          Persönlicher IT-Betreuer mit über 20 Jahren Erfahrung in der IT-Branche. Single Point of Contact für KMU, Handwerk und Büros im Raum München Ost – von Microsoft 365 über Netzwerktechnik (Ubiquiti UniFi) bis zur Datensicherung nach der 3-2-1-Strategie.\n'
        '          <div class="lp-author-meta">Zuletzt aktualisiert: ' + (mod_disp or TODAY_DISP) + ' · <a href="/kontakt/">Kontakt aufnehmen</a></div>\n'
        '        </div>\n'
        '      </div>')


def faq_html(faqs):
    items = "".join(
        '\n      <div class="faq-item">\n        <h3>{q}</h3>\n        <p>{a}</p>\n      </div>'.format(
            q=esc(q), a=esc(a)) for q, a in faqs)
    return items


def cards_html(cards):
    return "".join(
        '\n        <div class="lp-card"><h3>{h}</h3><p>{t}</p></div>'.format(h=esc(h), t=esc(t))
        for h, t in cards)


def page(head_html, schema_blocks, main_html, places, services, extra_style=""):
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
    parts.append(NAV)
    parts.append('\n<main id="main">')
    parts.append(main_html)
    parts.append("</main>\n")
    parts.append(footer(places, services))
    parts.append('<script src="../assets/js/main.js"></script>\n')
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
                  "sondern dein Nachbar mit über 20 Jahren IT-Erfahrung. Kurze Anfahrt, persönliche "
                  "Betreuung und im Notfall oft Hilfe noch am selben Tag."),
        "near_q": "Bietest du IT-Service direkt vor Ort in Grasbrunn an?",
        "near_a": ("Ja. Mein Sitz ist im Beethovenring 16 in Neukeferloh (Gemeinde Grasbrunn). "
                   "Für Kunden in Grasbrunn, Neukeferloh und Harthausen bin ich in wenigen Minuten "
                   "vor Ort – oder helfe sofort per Fernwartung."),
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
                   "meinem Sitz in Neukeferloh entfernt – Vor-Ort-Termine sind meist am selben oder "
                   "nächsten Tag möglich, akute Störungen löse ich oft sofort per Fernwartung."),
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
                   "ich unkomplizierte Hilfe ohne teure Mindestpauschalen – per Fernwartung sofort "
                   "oder vor Ort, je nachdem was du brauchst."),
    },
    {
        "slug": "zorneding", "name": "Zorneding", "title_name": "Zorneding",
        "area": ["Zorneding", "Pöring", "Baldham", "Vaterstetten"],
        "intro": ("Zorneding mit Pöring und Wolfesing liegt an der S-Bahn-Linie S4 im grünen Osten "
                  "des Landkreises Ebersberg. Viele Handwerksbetriebe und kleine Firmen hier haben "
                  "keine eigene IT-Abteilung – genau dafür bin ich da: als externer IT-Betreuer mit "
                  "kurzen Wegen und festen Reaktionszeiten."),
        "near_q": "Betreust du auch Betriebe in Zorneding und Pöring?",
        "near_a": ("Ja. Zorneding, Pöring und Wolfesing liegen in meinem Einsatzgebiet im Münchner "
                   "Osten. Ob laufende Betreuung oder einmalige Hilfe – ich bin schnell erreichbar "
                   "und im Notfall zügig vor Ort."),
    },
    {
        "slug": "haar", "name": "Haar", "title_name": "Haar",
        "area": ["Haar", "Grasbrunn", "Putzbrunn", "Vaterstetten"],
        "intro": ("Haar grenzt direkt an München und ist einer der gewerbestärksten Orte im Münchner "
                  "Osten – vom Büro über die Praxis bis zum Handwerksbetrieb. Von Neukeferloh aus bin "
                  "ich in wenigen Minuten in Haar und kümmere mich persönlich um deine komplette IT."),
        "near_q": "Wie schnell bist du bei einem IT-Notfall in Haar?",
        "near_a": ("Haar ist nur wenige Minuten von meinem Sitz entfernt. Akute Störungen löse ich "
                   "oft sofort per Fernwartung; ist ein Vor-Ort-Einsatz nötig, bin ich durch die "
                   "kurze Anfahrt meist am selben Tag da."),
    },
    {
        "slug": "putzbrunn", "name": "Putzbrunn", "title_name": "Putzbrunn",
        "area": ["Putzbrunn", "Solalinden", "Hohenbrunn", "Grasbrunn"],
        "intro": ("Putzbrunn mit Solalinden hat ein lebhaftes Gewerbegebiet mit vielen KMU und "
                  "Handwerksbetrieben. Ich biete hier persönliche IT-Betreuung mit einem festen "
                  "Ansprechpartner – zu einem einheitlichen Stundensatz, abgerechnet im "
                  "15-Minuten-Takt und ohne versteckte Kosten."),
        "near_q": "Gibt es in Putzbrunn nicht schon genug IT-Dienstleister?",
        "near_a": ("Einige – aber kaum einen, der so persönlich und transparent arbeitet wie ich. "
                   "Du bekommst einen festen Ansprechpartner statt Ticketsystem, faire Abrechnung im "
                   "15-Minuten-Takt und schnelle Hilfe für Putzbrunn und Solalinden."),
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
         "es feste Monatspakete mit garantierten Reaktionszeiten – planbar und ohne versteckte Kosten."),
        ("Wie schnell bekomme ich Hilfe?",
         "Akute Störungen löse ich oft sofort per Fernwartung. Vor-Ort-Termine sind durch die kurzen "
         "Wege meist am selben oder nächsten Tag möglich; Managed-Kunden haben Priorität."),
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
      <div class="s-label">IT-Service vor Ort</div>
      <h1 class="s-title">IT-Service in {tn}</h1>
      <p class="s-sub">Dein persönlicher IT-Betreuer für {name} – kurze Wege, schnelle Hilfe, ein fester Ansprechpartner statt anonymer Hotline.</p>

      <div class="lp-cta-row">
        <a href="tel:+491782584438" class="lp-btn primary">Jetzt anrufen · 0178 258 44 38</a>
        <a href="/kontakt/" class="lp-btn ghost">Kontakt &amp; Anfrage</a>
      </div>

      <p>{intro}</p>

      <h2>IT-Leistungen für {name}</h2>
      <div class="lp-grid">{cards}
      </div>

      <div class="lp-trust">
        <strong>Warum Unternehmen aus {name} mit mir arbeiten:</strong> Ein einheitlicher Stundensatz, Abrechnung im 15-Minuten-Takt, keine versteckten Kosten – und ein Ansprechpartner, der zurückruft. Genau das, was meine Kunden in den Google-Bewertungen mit „schnell, zuverlässig und in sehr guter Qualität" beschreiben.
      </div>

      <h2>Auch in deiner Nähe im Einsatz</h2>
      <p>Von Neukeferloh aus betreue ich den gesamten Münchner Osten im Umkreis von rund 10&nbsp;km:</p>
      <div class="lp-places">
        {chips}
      </div>

      <h2>Häufige Fragen zum IT-Service in {name}</h2>{faqs}
{author}
      <div class="lp-cta-row" style="margin-top:2.5rem;">
        <a href="tel:+491782584438" class="lp-btn primary">IT-Problem? Jetzt anrufen</a>
        <a href="/managed-it-service/" class="lp-btn ghost">Mehr zur laufenden IT-Betreuung</a>
      </div>
    </div>
  </div>
</article>""".format(tn=esc(p["title_name"]), name=esc(p["name"]), intro=esc(p["intro"]),
                     cards=cards_html(PLACE_CARDS), chips=chips_html, faqs=faq_html(faqs),
                     author=author_box())

    return slug, page(h, schema, main, places, services)


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
    "description": ("60 bis 90 Minuten im Betrieb oder per Videogespraech: Die Ablaeufe werden "
                    "durchgegangen und schriftlich ausgewertet - was sich automatisieren laesst, "
                    "welcher Aufwand dahintersteckt, was es einspart und was rechtlich zu "
                    "beachten ist. Kostenlos und unverbindlich."),
    "provider": {"@id": BUSINESS_ID},
    "areaServed": [{"@type": "City", "name": n} for n in
                   ["Grasbrunn", "Vaterstetten", "Haar", "Ottobrunn", "Muenchen"]],
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR",
               "availability": "https://schema.org/InStock",
               "description": "Kostenlos und unverbindlich, das schriftliche Ergebnis bleibt beim Kunden."},
}

# Zusatz-CSS ausschliesslich fuer die KI-Seiten. Wird ueber das Feld "extra_style"
# eingehaengt, damit Orts- und uebrige Leistungsseiten unveraendert bleiben.
KI_STYLE = '''  <style>
    /* Bausteine nur fuer den KI-Bereich (via extra_style, damit die uebrigen Seiten unveraendert bleiben) */
    .ki-case { background:var(--bg2); border:1px solid var(--border); border-left:3px solid var(--cyan); border-radius:14px; padding:1.5rem 1.6rem; margin:1.1rem 0; }
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
    .ki-note { background:var(--bg2); border:1px solid var(--border); border-left:3px solid var(--accent); border-radius:12px; padding:1.3rem 1.5rem; margin:1.8rem 0; }
    .ki-note strong { color:var(--text); }
    .ki-note p { font-size:.88rem; color:var(--text2); line-height:1.75; margin:0 0 .7rem; }
    .ki-note p:last-child { margin-bottom:0; }
    .ki-tbl-wrap { overflow-x:auto; margin:1.4rem 0; }
    .ki-tbl { width:100%; border-collapse:collapse; font-size:.86rem; min-width:520px; }
    .ki-tbl th { font-family:var(--fh); font-size:.78rem; letter-spacing:.03em; text-transform:uppercase; color:var(--text3); text-align:left; padding:.7rem .9rem; border-bottom:1px solid var(--border); }
    .ki-tbl td { padding:.85rem .9rem; border-bottom:1px solid var(--border); color:var(--text2); line-height:1.65; vertical-align:top; }
    .ki-tbl td:first-child { color:var(--text); font-weight:600; white-space:nowrap; }
    .ki-tbl tr:last-child td { border-bottom:none; }
    .ki-link { display:block; text-decoration:none; transition:border-color .2s,transform .2s; }
    .ki-link:hover { border-color:var(--cyan); transform:translateY(-2px); }
    .ki-link h3 { color:var(--text); }
    .ki-link .ki-more { display:inline-block; margin-top:.7rem; font-family:var(--fh); font-size:.82rem; font-weight:700; color:var(--cyan); }
    .ki-link .ki-more::after { content:" 92"; }
  </style>'''


SERVICES = [
    {
        "slug": "managed-it-service", "nav": "Managed IT-Service",
        "title": "Managed IT-Service für KMU | München Ost – Andreas Grundke IT-Service",
        "h1": "Managed IT-Service für kleine &amp; mittlere Unternehmen",
        "label": "Laufende IT-Betreuung", "service_type": "Managed IT-Service",
        "desc": ("Managed IT-Service für kleine & mittlere Unternehmen im Raum München Ost: laufende "
                 "IT-Betreuung, feste Reaktionszeiten, ein persönlicher Ansprechpartner. Planbare "
                 "Monatspakete statt teurer Ausfälle."),
        "sub": "Deine komplette IT in einer Hand – proaktiv betreut, mit festen Reaktionszeiten und einem persönlichen Ansprechpartner, der zurückruft.",
        "intro": ("Die meisten kleinen Unternehmen rufen erst an, wenn die IT schon steht – und dann "
                  "wird es teuer. <strong>Managed IT-Service dreht das um:</strong> Ich kümmere mich "
                  "laufend um deine Rechner, Server, E-Mails und Sicherheit, bevor etwas ausfällt. "
                  "Du zahlst einen festen, planbaren Monatsbetrag statt unkalkulierbarer "
                  "Notfall-Rechnungen – und hast einen <strong>Single Point of Contact</strong> für "
                  "alles rund um IT."),
        "raw_intro": True,
        "cards": [
            ("Proaktive Wartung", "Updates, Monitoring und Pflege deiner Systeme – bevor Probleme entstehen."),
            ("Microsoft 365", "Postfächer, Teams, Lizenzen und Sicherheit zentral verwaltet."),
            ("Backup & Wiederherstellung", "Automatische Datensicherung nach 3-2-1 – inklusive Test der Rücksicherung."),
            ("IT-Sicherheit", "Virenschutz, Firewall, VPN und Schutz vor Ransomware & Phishing."),
            ("Schneller Support", "Feste Reaktionszeiten – Premium-Kunden in unter 1 Stunde."),
            ("Beratung & Einkauf", "Hardware-Empfehlungen und Beschaffung ohne Aufschlag-Spielchen."),
        ],
        "prices": [
            ("Starter", "149 €", "Laufende Betreuung für kleine Teams & Einzelplätze.", False),
            ("Business", "249 €", "Erweiterte Betreuung mit kürzeren Reaktionszeiten.", True),
            ("Premium", "449 €", "Rundum-Betreuung mit höchster Priorität (unter 1 Std.).", False),
        ],
        "offers": [
            ("Starter", "149.00", "Laufende IT-Betreuung für kleine Teams."),
            ("Business", "249.00", "Erweiterte Betreuung mit kürzeren Reaktionszeiten."),
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
             "Es gibt feste Monatspakete ab 149 € (Starter), 249 € (Business) und 449 € (Premium). "
             "Welches Paket passt, hängt von Anzahl der Arbeitsplätze und gewünschter Reaktionszeit "
             "ab – das klären wir in einem kurzen kostenlosen Erstgespräch."),
            ("Bin ich an lange Verträge gebunden?",
             "Nein. Die Betreuung ist fair und planbar kalkuliert, ohne überlange Mindestlaufzeiten. "
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
                  "Lizenzen, Sicherheit oder Updates kümmern zu müssen."),
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
             "Betreuung ist Teil meiner Managed-IT-Pakete ab 149 € im Monat. Die Microsoft-Lizenzen "
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
             "Teil meiner Managed-IT-Pakete ab 149 € im Monat oder als Einzelprojekt zum festen "
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
        "title": "IT-Notdienst & schnelle IT-Hilfe | München Ost – Andreas Grundke IT-Service",
        "h1": "IT-Notdienst &amp; schnelle IT-Hilfe",
        "label": "Soforthilfe", "service_type": "IT-Notdienst",
        "desc": ("IT-Notdienst für KMU & Privat im Raum München Ost: schnelle Hilfe bei IT-Störungen, "
                 "Virenbefall und Datenverlust – sofort per Fernwartung oder vor Ort. Dein ITler geht "
                 "nicht ran? Ich schon."),
        "sub": "Dein ITler geht nicht ran? Ich schon. Schnelle Hilfe bei IT-Störungen – sofort per Fernwartung oder vor Ort.",
        "intro": ("Wenn die IT steht, zählt jede Minute. Ich helfe schnell und unkompliziert: akute "
                  "Störungen löse ich oft sofort per Fernwartung, bei größeren Problemen komme ich "
                  "durch die kurzen Wege im Münchner Osten meist noch am selben Tag vorbei. Kein "
                  "Ticketsystem, keine Warteschleife – du erreichst direkt die Person, die das "
                  "Problem löst."),
        "raw_intro": True,
        "cards": [
            ("Soforthilfe per Fernwartung", "Über TeamViewer bin ich in Sekunden auf deinem Bildschirm und löse das Problem direkt."),
            ("Vor-Ort-Einsatz", "Lässt sich etwas nicht aus der Ferne lösen, komme ich schnell vorbei."),
            ("Daten- & Systemrettung", "Hilfe bei Datenverlust, defekten Festplatten und nicht startenden Systemen."),
            ("Virenbefall & Ransomware", "Bereinigung befallener Systeme und Wiederherstellung aus dem Backup."),
        ],
        "faqs": [
            ("Wie schnell bekomme ich im Notfall Hilfe?",
             "Per Fernwartung meist sofort, sobald wir telefoniert haben. Ist ein Vor-Ort-Einsatz "
             "nötig, bin ich durch die kurzen Wege im Münchner Osten in der Regel am selben Tag bei dir."),
            ("Was kostet der IT-Notdienst?",
             "Ad-hoc-Hilfe rechne ich transparent zum einheitlichen Stundensatz im 15-Minuten-Takt ab "
             "– du zahlst nur die tatsächlich benötigte Zeit, ohne Pauschal-Abzocke."),
            ("Wie funktioniert die Fernwartung?",
             "Du lädst ein kleines Programm (TeamViewer) und nennst mir die Verbindungs-ID. Ich "
             "verbinde mich, du siehst alles mit und kannst die Sitzung jederzeit beenden – "
             "DSGVO-konform und sicher."),
            ("Hilfst du auch Privatkunden?",
             "Ja. Neben Unternehmen helfe ich auch Privatpersonen im Raum München Ost bei IT-Problemen "
             "– vom langsamen PC bis zum Virenbefall."),
        ],
    },
    # ----------------------------------------------------------------------- #
    #  KI-Bereich (seit 2026-08-22): Hub + drei Vertiefungen.                  #
    #  Zweite Saeule neben dem klassischen IT-Service, eigene Datumsangaben.   #
    # ----------------------------------------------------------------------- #
    {
        "slug": "ki-fuer-kmu", "nav": "KI im Betrieb",
        "title": "KI für KMU – Anwendungen im Betrieb | Grundke IT-Service München Ost",
        "h1": "KI im Betrieb – für kleine &amp; mittlere Unternehmen",
        "label": "KI in der Praxis", "service_type": "KI-Beratung und Anwendungsentwicklung für KMU",
        "published": KI_PUB_DATE, "modified": KI_DATE, "modified_disp": KI_DATE_DISP,
        "extra_style": KI_STYLE,
        "cta2_href": "/ki-automatisierung/", "cta2_text": "Abläufe automatisieren",
        "extra_schema": [POTENZIALCHECK_SCHEMA],
        "desc": ("KI im Betrieb: Abläufe automatisieren, Auswertungen aus vorhandenen Daten, "
                 "DSGVO-konform umgesetzt. Kostenloser Potenzialcheck im Raum München Ost."),
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
      <h2>Drei Anwendungen aus der Praxis</h2>
      <p>Alle drei laufen. Die Kundenfälle sind anonymisiert, weil Betriebsabläufe niemanden etwas angehen außer dem Betrieb selbst.</p>

      <div class="ki-case">
        <span class="ki-case-tag">Kundenprojekt · Videoauswertung</span>
        <h3>Eine Hofzufahrt, die sich selbst protokolliert</h3>
        <p>Ein Betrieb im Landkreis München hatte eine vollständig aufgebaute UniFi-Protect-Anlage und trotzdem keine Antwort auf einfache Fragen: Wie viele Fahrzeuge kommen pro Woche? Wann ist am meisten los? Die Aufnahmen lagen vor, sie hätte nur jemand ansehen müssen.</p>
        <p>Auf die vorhandenen Kameras habe ich eine Objekterkennung aufgesetzt. Fahrzeuge und Objekte werden automatisch erkannt, jedes Ereignis landet mit Zeitstempel in einer Datenbank, und eine Oberfläche zeigt daraus Verläufe und Summen. Die Erkennung läuft auf Hardware im Betrieb, die Aufnahmen verlassen das Haus nicht.</p>
        <p class="ki-result">Statt Videomaterial zu sichten, gibt es jetzt Zahlen. Die Auswertung, für die vorher niemand Zeit hatte, steht beim Öffnen der Seite da.</p>
      </div>

      <div class="ki-case">
        <span class="ki-case-tag">Kundenprojekt · Rechnungsstellung</span>
        <h3>E-Rechnungen ohne Abtippen</h3>
        <p>Die Leistungsdaten lagen als CSV-Export aus einem Vorsystem vor, die Rechnungen entstanden daraus von Hand. Jeden Monat dieselbe Strecke, jedes Mal einige Stunden, und gelegentlich ein Zahlendreher, den erst der Kunde bemerkt.</p>
        <p>Heute liest ein Programm den Export ein, ordnet die Positionen zu und erzeugt daraus normgerechte E-Rechnungen im Format XRechnung beziehungsweise ZUGFeRD. Gerechnet wird gegen die Ausgangsdaten gegengeprüft, damit nichts ungesehen durchläuft.</p>
        <p class="ki-result">Aus einem halben Arbeitstag im Monat sind ein paar Minuten geworden. Die Umstellung auf die kommende E-Rechnungspflicht ist damit nebenbei erledigt, statt kurz vor der Frist anzustehen.</p>
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
          <a href="tel:+491782584438" class="lp-btn primary">Potenzialcheck vereinbaren</a>
          <a href="/kontakt/" class="lp-btn ghost">Lieber schreiben</a>
        </div>
      </div>

      <h2>Wann sich das nicht lohnt</h2>
      <p>Nicht jede Aufgabe verdient eine eigene Anwendung. Was dreimal im Jahr vorkommt, ist von Hand billiger als jede Automatisierung, und wenn ein Ablauf sich alle paar Monate ändert, wird die Pflege teurer als der Nutzen. Auch dort, wo es am Ende auf ein Urteil ankommt und nicht auf eine Regel, hat eine Maschine wenig verloren.</p>
      <p>Das sage ich im Erstgespräch, bevor daraus ein Projekt wird. Mir ist ein Kunde lieber, der einmal etwas Sinnvolles bekommt, als einer, der ein halbes Jahr später merkt, dass er es nie gebraucht hat.</p>

      <h2>Die drei Bereiche im Einzelnen</h2>
      <div class="lp-grid">
        <a class="lp-card ki-link" href="/ki-automatisierung/"><h3>Abläufe automatisieren</h3><p>E-Rechnungen aus vorhandenen Daten, Schnittstellen zwischen Programmen, Dokumente auslesen, Berichte ohne Excel-Bastelei.</p><span class="ki-more">Ansehen</span></a>
        <a class="lp-card ki-link" href="/ki-videoanalyse/"><h3>Videoanalyse und Auswertung</h3><p>Objekte erkennen, Vorgänge zählen, Ereignisse protokollieren, Kennzahlen darstellen. Auf Basis der vorhandenen Kameras.</p><span class="ki-more">Ansehen</span></a>
        <a class="lp-card ki-link" href="/ki-dsgvo/"><h3>KI rechtssicher betreiben</h3><p>Wo das Modell läuft, welcher Anbieter einen Auftragsverarbeitungsvertrag bietet, was in eine Nutzungsrichtlinie gehört.</p><span class="ki-more">Ansehen</span></a>
      </div>
""",
        "faqs": [
            ("Was bringt KI einem Betrieb mit 15 Mitarbeitern konkret?",
             "Meistens Zeit an einer Stelle, die niemand gern macht. Typisch sind drei Fälle: Daten, "
             "die aus einem Export von Hand in ein anderes Programm übertragen werden. Auswertungen, "
             "die jemand am Monatsende in Excel zusammenbaut. Und Aufnahmen oder Protokolle, die "
             "niemand durchsieht, weil es zu lange dauert. Das sind Stunden, die jeden Monat anfallen "
             "und sich ohne zusätzliches Personal zurückholen lassen."),
            ("Ist das für einen kleinen Betrieb nicht viel zu teuer?",
             "Abgerechnet wird nach Aufwand, zu 110 Euro netto je Stunde im 15-Minuten-Takt wie bei "
             "jeder anderen Leistung auch. Eine überschaubare Automatisierung ist oft an einem Tag "
             "fertig. Ob sie sich rechnet, lässt sich vorher ausrechnen: Wenn eine Aufgabe monatlich "
             "vier Stunden kostet, ist die einzige Frage, nach wie vielen Monaten die Umsetzung "
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
             "Frage, was Mitarbeiter überhaupt in ein Chatfenster eingeben dürfen. Seit dem 2. Februar "
             "2025 verlangt Artikel 4 der europäischen KI-Verordnung von jedem Unternehmen, das KI "
             "einsetzt, ausreichende KI-Kompetenz bei den Beschäftigten."),
            ("Wie fange ich an?",
             "Mit dem kostenlosen KI-Potenzialcheck. Wir gehen 60 bis 90 Minuten durch deine Abläufe "
             "und schauen, wo Zeit verloren geht. Danach bekommst du schriftlich, was sich "
             "automatisieren lässt, was es ungefähr kostet und was rechtlich zu beachten ist. Ob du "
             "damit weiterarbeitest, entscheidest du in Ruhe."),
        ],
    },
    {
        "slug": "ki-automatisierung", "nav": "Abläufe automatisieren",
        "title": "Abläufe automatisieren: E-Rechnung & Schnittstellen | Grundke IT-Service",
        "h1": "Abläufe automatisieren – von der E-Rechnung bis zur Schnittstelle",
        "label": "Weniger Handarbeit", "service_type": "Prozessautomatisierung und Anwendungsentwicklung für KMU",
        "published": KI_PUB_DATE, "modified": KI_DATE, "modified_disp": KI_DATE_DISP,
        "extra_style": KI_STYLE,
        "cta2_href": "/ki-fuer-kmu/", "cta2_text": "Überblick KI im Betrieb",
        "desc": ("E-Rechnungen aus vorhandenen Daten, Schnittstellen zwischen Programmen, Berichte "
                 "ohne Excel-Bastelei. Automatisierung für KMU im Raum München Ost."),
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
            ("E-Rechnungen aus vorhandenen Daten", "Aus CSV-Exporten, Listen oder einem Vorsystem entstehen normgerechte Rechnungen als XRechnung oder ZUGFeRD."),
            ("Schnittstellen zwischen Programmen", "Warenwirtschaft, Zeiterfassung, Buchhaltung, Kasse. Was Daten exportieren kann, lässt sich koppeln."),
            ("Dokumente auslesen", "Lieferscheine, Eingangsrechnungen, Formulare: Inhalte werden erkannt und landen strukturiert in der Datenbank."),
            ("Auswertungen und Berichte", "Zahlen, die heute jemand am Monatsende in Excel zusammensucht, entstehen automatisch und immer gleich."),
            ("Wiederkehrende Läufe", "Nächtliche Abgleiche, Erinnerungen, Prüfungen, Datenübernahmen. Einmal eingerichtet, läuft es weiter."),
            ("Meldung statt Nachsehen", "Wenn etwas schiefgeht, meldet sich die Anwendung von selbst. Per E-Mail oder Nachricht aufs Handy."),
        ],
        "extra": """
      <h2>Der aktuelle Anlass: die E-Rechnung</h2>
      <p>Die E-Rechnung ist gerade für viele Betriebe der konkrete Grund, sich mit Automatisierung zu beschäftigen, weil eine Frist im Raum steht. Der Stand der gesetzlichen Regelung in Deutschland:</p>
      <div class="ki-tbl-wrap">
        <table class="ki-tbl">
          <thead><tr><th>Ab wann</th><th>Was gilt</th></tr></thead>
          <tbody>
            <tr><td>1. Januar 2025</td><td>Jedes inländische Unternehmen muss E-Rechnungen <strong>empfangen</strong> können. Das gilt bereits.</td></tr>
            <tr><td>bis 31. Dezember 2026</td><td>Übergangsfrist beim Versand: Papier ist weiterhin zulässig, ein einfaches PDF nur mit Zustimmung des Empfängers.</td></tr>
            <tr><td>1. Januar 2027</td><td>Unternehmen mit mehr als 800.000 Euro Vorjahresumsatz müssen im inländischen B2B-Geschäft E-Rechnungen <strong>ausstellen</strong>.</td></tr>
            <tr><td>1. Januar 2028</td><td>Die Ausstellungspflicht gilt für alle übrigen inländischen B2B-Umsätze.</td></tr>
          </tbody>
        </table>
      </div>
      <p>Für Betriebe über der Umsatzgrenze bleiben damit noch wenige Monate. Wer seine Rechnungen ohnehin aus einem Vorsystem oder einer Excel-Liste heraus erstellt, kann diesen Schritt gleich mit der Automatisierung verbinden, statt zweimal umzustellen.</p>
      <div class="ki-note">
        <p><strong>Zur Einordnung:</strong> Das ist die technische Seite. Ob und ab wann die Pflicht deinen Betrieb genau trifft, welche Umsätze darunterfallen und wie das steuerlich zu behandeln ist, gehört zu deinem Steuerberater. Ich baue die Umsetzung, nicht die steuerliche Bewertung.</p>
      </div>

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
          <a href="tel:+491782584438" class="lp-btn primary">Potenzialcheck vereinbaren</a>
          <a href="/kontakt/" class="lp-btn ghost">Lieber schreiben</a>
        </div>
      </div>
""",
        "faqs": [
            ("Ab wann muss unser Betrieb E-Rechnungen verschicken können?",
             "Empfangen muss sie seit dem 1. Januar 2025 jedes inländische Unternehmen. Beim Versand "
             "gilt eine Staffel: Bis Ende 2026 darf noch auf Papier gestellt werden, ein einfaches PDF "
             "nur mit Zustimmung des Empfängers. Ab dem 1. Januar 2027 müssen Unternehmen mit mehr als "
             "800.000 Euro Vorjahresumsatz E-Rechnungen ausstellen, ab dem 1. Januar 2028 alle übrigen "
             "im inländischen B2B-Geschäft. Das ist die allgemeine Rechtslage und keine "
             "Steuerberatung. Für die Bewertung deines konkreten Falls ist dein Steuerberater da."),
            ("Welche Abläufe eignen sich überhaupt?",
             "Am besten alles, was regelmäßig vorkommt, immer gleich abläuft und heute an einer Datei "
             "hängt: Exporte, Listen, Formulare, Berichte. Je klarer die Regel, desto einfacher die "
             "Umsetzung. Schwieriger wird es, wenn bei jedem Durchgang jemand eine Entscheidung "
             "treffen muss, die auf Erfahrung beruht. Dann automatisiert man die Vorarbeit und lässt "
             "die Entscheidung beim Menschen."),
            ("Was kostet eine Automatisierung?",
             "Sie wird nach Aufwand abgerechnet, zu 110 Euro netto je Stunde im 15-Minuten-Takt. "
             "Kleinere Strecken sind oft an einem Tag fertig, größere brauchen mehrere. Nach dem "
             "ersten Blick auf den Ablauf bekommst du eine Schätzung, mit der du rechnen kannst, "
             "bevor irgendetwas gebaut wird."),
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
        "title": "KI-Videoanalyse für Betriebe – Objekterkennung | Grundke IT-Service",
        "h1": "Videoanalyse und Auswertung – Kameradaten nutzbar machen",
        "label": "Kamera plus Auswertung", "service_type": "KI-gestützte Videoanalyse und Auswertung für Unternehmen",
        "published": KI_PUB_DATE, "modified": KI_DATE, "modified_disp": KI_DATE_DISP,
        "extra_style": KI_STYLE,
        "cta2_href": "/netzwerk-wlan-firewall/", "cta2_text": "Netzwerk & Kameratechnik",
        "desc": ("Aus Kameraaufnahmen werden Zahlen: Objekte erkennen, Vorgänge zählen, Kennzahlen "
                 "darstellen. Auf Basis vorhandener UniFi-Anlagen, Verarbeitung im Haus."),
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
            ("Objekte erkennen", "Fahrzeuge, Container, Maschinen, Paletten. Was regelmäßig vorkommt, lässt sich zuverlässig unterscheiden."),
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
      <div class="ki-note">
        <p><strong>Gesichtserkennung und die Auswertung des Verhaltens einzelner Mitarbeiter baue ich nicht.</strong> Das ist rechtlich heikel bis unzulässig, und in einem normalen Betrieb ist es auch gar nicht nötig: Für die Fragen, um die es tatsächlich geht, reicht es, Objekte zu unterscheiden und Vorgänge zu zählen.</p>
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
          <a href="tel:+491782584438" class="lp-btn primary">Anlage ansehen lassen</a>
          <a href="/kontakt/" class="lp-btn ghost">Lieber schreiben</a>
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
             "kritisch als das Wiedererkennen von Personen, das ich bewusst nicht baue. Die rechtliche "
             "Prüfung im Einzelfall gehört zu deinem Datenschutzbeauftragten."),
            ("Wie zuverlässig erkennt so ein System?",
             "Bei klar unterscheidbaren Objekten wie Fahrzeugen ist die Erkennung gut genug, um "
             "belastbare Zahlen zu liefern. Fehler gibt es trotzdem, vor allem bei schlechtem Licht, "
             "Regen oder ungünstigem Kamerawinkel. Deshalb wird jede Auswertung anfangs mit der "
             "Wirklichkeit abgeglichen und nachjustiert, bevor sie in den Betrieb geht. Wer behauptet, "
             "so etwas laufe von Anfang an fehlerfrei, hat es nicht gemacht."),
            ("Was kostet eine solche Auswertung?",
             "Abgerechnet wird nach Aufwand zu 110 Euro netto je Stunde im 15-Minuten-Takt. Der "
             "Aufwand hängt daran, wie viele Kameras beteiligt sind, wie klar die Fragestellung ist "
             "und ob passende Hardware für die Erkennung schon vorhanden ist. Nach dem Blick auf die "
             "Anlage bekommst du eine Schätzung, mit der du rechnen kannst."),
        ],
    },
    {
        "slug": "ki-dsgvo", "nav": "KI rechtssicher betreiben",
        "title": "KI im Unternehmen: DSGVO, AVV & KI-Verordnung | Grundke IT-Service",
        "h1": "KI im Unternehmen einsetzen, ohne rechtliches Risiko",
        "label": "Rechtssicher betrieben", "service_type": "Beratung zum datenschutzkonformen KI-Einsatz in Unternehmen",
        "published": KI_PUB_DATE, "modified": KI_DATE, "modified_disp": KI_DATE_DISP,
        "extra_style": KI_STYLE,
        "cta2_href": "/schulung/", "cta2_text": "Schulung für dein Team",
        "desc": ("KI im Betrieb rechtssicher nutzen: lokales Modell oder Cloud, "
                 "Auftragsverarbeitungsvertrag, Nutzungsrichtlinie und Schulung nach Artikel 4."),
        "sub": "Die Frage ist selten, ob KI hilft. Die Frage ist, welche Daten hineindürfen und wer dafür geradesteht.",
        "intro": ("Das häufigste Problem beim KI-Einsatz im Betrieb ist nicht die Technik. Es ist der "
                  "Mitarbeiter, der eine Kundenliste in ein kostenloses Chatfenster kopiert, weil es "
                  "schneller geht. <strong>Damit liegen personenbezogene Daten bei einem Anbieter, "
                  "mit dem kein Vertrag besteht</strong>, und das ist ein Datenschutzvorfall und kein "
                  "Kavaliersdelikt. Dahinter steckt selten böse Absicht, sondern eine fehlende "
                  "Ansage. Ich kläre für deinen Betrieb, welche Werkzeuge benutzt werden dürfen, wo "
                  "sie laufen und was hineindarf, und halte das so fest, dass es im Alltag auch "
                  "jemand liest."),
        "raw_intro": True,
        "cards": [
            ("Wo das Modell läuft", "Eigene Hardware, EU-Rechenzentrum oder Anbieter mit Vertrag. Für jede Aufgabe die passende Stufe."),
            ("Auftragsverarbeitungsvertrag", "Welcher Anbieter einen anbietet, was darin stehen muss und wo die Daten tatsächlich liegen."),
            ("Nutzungsrichtlinie", "Eine verständliche Seite für die Belegschaft: erlaubte Werkzeuge, erlaubte Daten, Ansprechpartner."),
            ("Schulung der Mitarbeiter", "Artikel 4 der KI-Verordnung verlangt seit Februar 2025 ausreichende KI-Kompetenz im Unternehmen."),
            ("Lokale Modelle einrichten", "Ein Sprachmodell auf eigener Hardware, das ohne Internetverbindung arbeitet. Für sensible Daten der sauberste Weg."),
            ("Bestandsaufnahme", "Welche KI-Werkzeuge im Betrieb bereits benutzt werden, weiß meist niemand. Das lässt sich klären."),
        ],
        "extra": """
      <h2>Drei Wege, und wann welcher passt</h2>
      <p>Die wichtigste Entscheidung fällt vor der ersten Zeile Code: wo die Daten verarbeitet werden. Danach richtet sich alles Weitere.</p>
      <div class="ki-tbl-wrap">
        <table class="ki-tbl">
          <thead><tr><th>Weg</th><th>Wie es funktioniert</th><th>Wofür geeignet</th></tr></thead>
          <tbody>
            <tr><td>Lokales Modell</td><td>Das Modell läuft auf Hardware im Betrieb. Die Daten verlassen das Netzwerk nicht, eine Internetverbindung ist nicht nötig.</td><td>Personaldaten, Patienten- und Mandantendaten, Kalkulationen, alles wirklich Vertrauliche.</td></tr>
            <tr><td>EU-Rechenzentrum</td><td>Verarbeitung bei einem Anbieter mit Standort in der EU, mit Auftragsverarbeitungsvertrag und ohne Training auf deinen Daten.</td><td>Alltagsaufgaben mit Personenbezug, wenn die eigene Hardware dafür nicht reicht.</td></tr>
            <tr><td>Großer Anbieter mit Vertrag</td><td>Leistungsfähige Modelle bekannter Anbieter, geschäftlich lizenziert, mit Vertrag und abgeschalteter Trainingsnutzung.</td><td>Texte, Recherche, Entwürfe, Programmierung. Alles ohne personenbezogene oder vertrauliche Inhalte.</td></tr>
          </tbody>
        </table>
      </div>
      <p>In der Praxis läuft es meist auf eine Kombination hinaus: das Bequeme für Unkritisches, das Lokale für alles, was den Betrieb nicht verlassen darf. Wichtig ist, dass die Grenze zwischen beidem klar gezogen und aufgeschrieben ist.</p>

      <h2>Was die KI-Verordnung von einem KMU verlangt</h2>
      <p>Seit dem 2. Februar 2025 gilt Artikel 4 der europäischen KI-Verordnung. Er verpflichtet jedes Unternehmen, das KI-Systeme einsetzt, dafür zu sorgen, dass die Menschen, die damit arbeiten, ausreichend KI-Kompetenz besitzen. Das betrifft ausdrücklich nicht nur Entwickler von Hochrisiko-Anwendungen, sondern auch den Betrieb, in dem drei Leute ChatGPT benutzen.</p>
      <p>Ein festes Schulungsprogramm schreibt die Verordnung nicht vor. Verlangt wird, dass die Maßnahmen zur Rolle und zur tatsächlichen Nutzung passen und dass das Unternehmen sie belegen kann. Die nationale Marktüberwachung dazu läuft seit dem 2. August 2026. Ein eigener Bußgeldtatbestand für Artikel 4 besteht derzeit nicht, was die Sache aber nicht erledigt: Entsteht durch falsche KI-Nutzung ein Schaden, steht die Frage im Raum, ob eine angemessene Unterweisung ihn verhindert hätte.</p>
      <div class="ki-note">
        <p>Praktisch heißt das zweierlei: eine kurze, verständliche Nutzungsrichtlinie und eine Unterweisung, die dokumentiert ist. Beides mache ich zusammen mit dir. Die <a href="/schulung/">IT-Sicherheitsschulung</a> deckt den Teil ab, der die Belegschaft betrifft.</p>
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
             "Seit dem 2. Februar 2025 verpflichtet Artikel 4 jedes Unternehmen, das KI einsetzt, für "
             "ausreichende KI-Kompetenz der Beschäftigten zu sorgen. Ein festes Curriculum ist nicht "
             "vorgeschrieben, die Maßnahmen müssen aber zur Rolle und zur tatsächlichen Nutzung passen "
             "und nachweisbar sein. Die nationale Durchsetzung läuft seit dem 2. August 2026. In der "
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
             "Sie wird nach Aufwand abgerechnet, zu 110 Euro netto je Stunde im 15-Minuten-Takt. "
             "Bestandsaufnahme und eine brauchbare Nutzungsrichtlinie sind für einen kleinen Betrieb "
             "meist an einem Tag zu schaffen. Ein lokales Modell einzurichten dauert länger und hängt "
             "an der Hardware. Was in deinem Fall nötig ist, klären wir im kostenlosen Erstgespräch."),
        ],
    },
]


def render_service(s, places, services):
    slug = s["slug"]
    og_title = s["h1"].replace("&amp;", "&") + " – Andreas Grundke IT-Service"
    h = head(s["title"], s["desc"], slug, og_title, s["desc"],
             s["h1"].replace("&amp;", "&") + " – Andreas Grundke IT-Service")

    service_schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": s["service_type"],
        "name": s["h1"].replace("&amp;", "&"),
        "description": s["desc"],
        "provider": {"@type": "LocalBusiness", "name": "Andreas Grundke IT-Service",
                     "alternateName": "Grundke IT-Service", "telephone": "+49-178-2584438",
                     "url": DOMAIN},
        "areaServed": [{"@type": "City", "name": n} for n in
                       ["Grasbrunn", "Vaterstetten", "Haar", "Ottobrunn", "München"]],
    }
    if s.get("offers"):
        service_schema["offers"] = [
            {"@type": "Offer", "name": n, "price": pr, "priceCurrency": "EUR", "description": d}
            for n, pr, d in s["offers"]]
    schema = [breadcrumb(s["nav"], slug), service_schema, faq_schema(s["faqs"]),
              webpage_schema(s["title"], s["desc"], slug,
                             s.get("published"), s.get("modified"))]
    # Optionale Zusatzknoten (z. B. der kostenlose KI-Potenzialcheck als eigener Service)
    schema.extend(s.get("extra_schema", []))

    price_html = ""
    if s.get("prices"):
        cells = "".join(
            '\n        <div class="lp-price{feat}">\n          <div class="tier">{t}</div>\n'
            '          <div class="amount">{a}<span> / Monat</span></div>\n'
            '          <div class="desc">{d}</div>\n        </div>'.format(
                feat=" feat" if feat else "", t=esc(t), a=esc(a), d=esc(d))
            for t, a, d, feat in s["prices"])
        price_html = ("\n      <h2>Pakete &amp; Preise</h2>\n"
                      "      <p>Transparente Monatspauschalen – welches Paket passt, klären wir im "
                      "kostenlosen Erstgespräch:</p>\n"
                      '      <div class="lp-price-grid">{cells}\n      </div>\n').format(cells=cells)

    intro = s["intro"] if s.get("raw_intro") else esc(s["intro"])

    main = """<article class="lp-wrap">
  <div class="inner">
    <div class="lp-content">
      <div class="s-label">{label}</div>
      <h1 class="s-title">{h1}</h1>
      <p class="s-sub">{sub}</p>

      <div class="lp-cta-row">
        <a href="tel:+491782584438" class="lp-btn primary">Kostenloses Erstgespräch</a>
        <a href="/kontakt/" class="lp-btn ghost">Anfrage senden</a>
      </div>

      <p>{intro}</p>

      <h2>Das steckt drin</h2>
      <div class="lp-grid">{cards}
      </div>
{extra}{prices}
      <div class="lp-trust">
        <strong>Einheitlicher Stundensatz, Abrechnung im 15-Minuten-Takt, keine versteckten Kosten.</strong> Kein klassischer Kundendienst, sondern ein fester persönlicher Ansprechpartner mit über 20 Jahren IT-Erfahrung – im Raum München Ost, DSGVO-konform und auf Wunsch self-hosted.
      </div>

      <h2>Häufige Fragen</h2>{faqs}
{author}
      <div class="lp-cta-row" style="margin-top:2.5rem;">
        <a href="tel:+491782584438" class="lp-btn primary">Jetzt anrufen · 0178 258 44 38</a>
        <a href="{cta2_href}" class="lp-btn ghost">{cta2_text}</a>
      </div>
    </div>
  </div>
</article>""".format(label=esc(s["label"]), h1=s["h1"], sub=esc(s["sub"]), intro=intro,
                     cards=cards_html(s["cards"]), prices=price_html, faqs=faq_html(s["faqs"]),
                     author=author_box(s.get("modified_disp")),
                     extra=s.get("extra", ""),
                     cta2_href=s.get("cta2_href", "/it-service-grasbrunn/"),
                     cta2_text=esc(s.get("cta2_text", "IT-Service in deiner Region")))

    return slug, page(h, schema, main, places, services, s.get("extra_style", ""))


# --------------------------------------------------------------------------- #
#  Sitemap                                                                     #
# --------------------------------------------------------------------------- #

STATIC_URLS = [
    ("/", "1.0"),
    ("/kontakt/", "0.7"),
    ("/schulung/", "0.8"),
    ("/empfehlungen/", "0.7"),
]


def write_sitemap(places, services):
    urls = []
    for loc, prio in STATIC_URLS:
        urls.append((loc, "2026-05-01", prio))
    urls.append(("/barrierefreiheit/", TODAY, "0.3"))
    for s in services:
        urls.append(("/" + s["slug"] + "/", TODAY, "0.8"))
    for p in places:
        urls.append(("/it-service-" + p["slug"] + "/", TODAY, "0.8"))
    body = []
    body.append('<?xml version="1.0" encoding="UTF-8"?>')
    body.append("<!--")
    body.append("  Sitemap · Grundke IT-Service · www.grundke-it.de")
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


if __name__ == "__main__":
    main()
