"""Statische Pruefungen (Spec §9: AK1, AK2, AK2b, AK7, AK8, AK9, AK9b, AK11a, AK13, AK13v, AK14, AK14r; R2: AKH;
2.1.1: AKK Kontakt-Reihenfolge).
Aufruf: python tools/checks/check_static.py [--only AK1,AK9] [--ci]   Exit 1 bei Fehler.
--ci: nur Pruefungen, die weder ../_intern/ noch Git-Historie brauchen (Deploy-Workflow); AK13v (Versionen gegen
origin/main) und AK14r (Rechtstexte gegen Basis-Commit und legal_hash.json) werden dann sichtbar uebersprungen.
Browser-Messungen stehen in check_site.py, nicht hier.
AKH (Stand 18.10.2026): Hero der Startseite mit dem Chat-Handy (H1, Firmenkunden-Zeile, erste Kundennachricht
statisch im HTML, Pause-Knopf, sichtbare Kennzeichnung, genau ein [data-hero-chat]) statt der frueheren Buehne;
Abschnitt IT-Betreuung wieder mit den typischen Anrufen (dl.itb-list).
AKK (Stand 18.10.2026): Kontaktwege ueberall in der Reihenfolge WhatsApp - Telefon - E-Mail; der Telefon-Knopf neben
WhatsApp ist kein Hauptknopf (.btn-p); kein Kasten .hc-direkt mehr nach dem Hero.
AKF (Stand 18.10.2026, Release 2.1.1): Film auf der Startseite als Fassade (kein <video>/<source>/<track> im
HTML, kein autoplay), KI-Hinweis am Player, Untertitelspur in main.js, VideoObject, Filmdateien nicht im Pre-Cache."""
import gzip, hashlib, html, json, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTERN = ROOT.parent / "_intern" / "messungen"
SKIP = ("tree", "ki-arbeitsplatz-onboarding-kit", "Audit 2026-04", "assets", "tools", ".impeccable", ".playwright-mcp", ".github")
LEGAL = ("impressum", "datenschutz", "agb", "barrierefreiheit")
FORBIDDEN_SELECTORS = [".btn-p", ".btn-g", ".btn-wa", ".btn-email", ".btn-tel", ".price-card", ".price-btn", ".faq-item",
                       ".cta-sec", ".lp-btn", ".lp-price", ".lp-card", ".emp-link", ".emp-card", ".k-card", ".sch-card",
                       ".topic", ".ki-case", ".ki-check", ".ki-note", ".lp-voice", ".testi-card", ".card",
                       # Task 7: Fliesstext-Bausteine und Kopf/Fuss der alten Generator-Huelle, seit Release B in style.css
                       ".ki-tbl", ".lp-steps", ".lp-checklist", ".lp-dont", ".lp-answer", ".lp-paths", ".lp-grid",
                       ".lp-hero", ".lp-cta-row", ".lp-trust", ".lp-author", ".lp-crumbs", ".more"]
OLD_WRAPPERS = ("lp-wrap", "page-wrap", "kontakt-wrap", "fw-wrap", "emp-hero", "err-wrap")
# AK8 (Fix-Runde B): Wortstaemme statt Wortgrenze am Ende, damit Beugungen auffallen („schnelle Hilfe“, „sofortige“,
# „garantierte“). Gross/klein egal, Treffer = ganzes Wort. Einzige Ausnahme im Muster: der Produktname
# „(IT-)Schnellcheck“ (kostenloser Termin, keine Zeitzusage; sonst 14 gleichartige Eintraege in der Erlaubtliste).
PROMISE_PATTERNS = [r"\w*schnell(?!check)\w*", r"\w*sofort\w*", r"\w*garanti\w*", r"\binnerhalb\b", r"\bbinnen\b",
                    r"\bjederzeit\b", r"\brund um die uhr\b", r"(?<!\d)24\s*/\s*7(?!\d)", r"\bimmer erreichbar\b",
                    r"\bich geh\w* ran\b", r"\bam selben tag\b", r"\bheute noch\b", r"\bnoch heute\b",
                    r"\bin (?:wenigen |einer |\d+ |\w+ )?(?:sekunden?|minuten?|stunden?)\b",
                    r"\bzeitnah\w*", r"\bam gleichen tag\b", r"\b24 stunden\b", r"\bzurückruf\w*", r"\bumgehend\w*",
                    r"\bkurzfristig\w*", r"\bbleib\w* dran\b", r"\berreichbar, wenn\b", r"\berreichbar, wann\b"]
PROMISE_RE = re.compile("|".join("(?:" + p + ")" for p in PROMISE_PATTERNS), re.I)
# Geprueft wird (Fix-Runde B) der ganze sichtbare Text in <main> jeder Seite ausser den Rechtsseiten, also jeder
# Baustein bis zu seinem Ende (K4, Kopf, Mini-Chat, K3, Abschluss K5, FAQ-<summary>, Hero-Chat der Startseite),
# dazu die <summary> im Fuss, Meta-, og- und twitter-Description und die Texte aus assets/js/hero-chat.js.
# Ausgenommen (Spec AK8): Kundenzitate (blockquote.testi-txt), die Lesespalte der Ratgeber-Artikel
# (article.lp-article), Rechtstexte und die Leitzeile.
AK8_HERO_JS = "assets/js/hero-chat.js"   # Texte des Hero-Chats (CASES, NIGHT_REPLY, updateClock)
AK8_LEITZEILE = "Dein ITler geht nicht ran? Ich schon."   # = H1_TEXT (Stand 18.10.2026, Release 2.1.1)
# Erlaubte Treffer: (Seite, exakter Ausschnitt um den Treffer, Grund). Ein Treffer ist erlaubt, wenn der Ausschnitt
# auf dieser Seite im geprueften Text steht und den Treffer enthaelt. Ein Eintrag ohne Treffer ist ein Fehler (Liste
# bleibt genau). Seite = Pfad wie rel(), fuer den Hero-Chat AK8_HERO_JS.
AK8_ALLOW = [
    ("index.html", "„Es muss heute noch laufen.“", "typischer Anruf in Worten des Kunden (Typische Anrufe)"),
    ("index.html", "„Ich muss heute noch fertig werden!“", "Ueberschrift der Praxisgeschichte, zitiert den Kunden"),
    ("index.html", "Er muss heute noch ein wichtiges Projekt abgeben.", "Praxisgeschichte: Lage des Kunden"),
    ("index.html", "ohne Garantie, dass es klappt", "verneint eine Garantie"),
    ("index.html", "Top-3-Handlungsempfehlungen Sofort: Externes Backup", "Beispiel-Bericht: Dringlichkeit einer Empfehlung"),
    ("index.html", "Innerhalb 3 Monate: FritzBox 7490 tauschen", "Beispiel-Bericht: Frist einer Empfehlung an den Kunden"),
    ("index.html", "Wie schnell bist du bei einem IT-Notfall erreichbar? + Feste Reaktionszeiten sage ich nicht zu",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("index.html", "Websites, die am Handy schnell laden", "Ladezeit der Website"),
    ("index.html", "wer hilft mir kurzfristig?",
     "FAQ-Frage in Worten des Besuchers; die Antwort nennt keine Zeit (Controller 11.10.2026, Hinweis an Andreas)"),
    ("index.html", "ohne garantierte Reaktionszeit", "verneint eine Reaktionszeit (geschuetzter Satz, Spec §5)"),
    ("index.html", "Die Umsetzung erfolgte schnell, zuverlässig und in sehr guter Qualität.",
     "woertliches Kundenzitat (Google-Bewertung Christian F.) im Text zum Film, Wortlaut wie im Film"),
    ("index.html", "einen 24/7-Vertrag mit festen Reaktionszeiten braucht",
     "FAQ Passungsfrage: nennt, wann ein Systemhaus passt (Stand 18.10.2026), keine eigene Zusage"),
    ("digitalbonus-bayern/index.html", "Umsetzung innerhalb von 18 Monaten nach der Bewilligung",
     "Frist des Foerderprogramms"),
    ("fernwartung/index.html", "beendest du die Sitzung jederzeit selbst", "der Kunde beendet die Sitzung selbst"),
    ("it-betreuer-wechseln/index.html", "desto schneller und billiger wird die Übernahme",
     "haengt an den Unterlagen des Kunden, keine Zusage"),
    ("it-notdienst/index.html", "Wie schnell bekomme ich im Notfall Hilfe? + Das hängt davon ab",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("it-service-baldham/index.html", "Wie schnell bekomme ich Hilfe? + Feste Reaktionszeiten sage ich nicht zu",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("it-service-grasbrunn/index.html", "Wie schnell bekomme ich Hilfe? + Feste Reaktionszeiten sage ich nicht zu",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("it-service-haar/index.html", "Wie schnell bekomme ich Hilfe? + Feste Reaktionszeiten sage ich nicht zu",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("it-service-haar/index.html", "Wie schnell bist du bei einem IT-Notfall in Haar?",
     "FAQ-Frage, die Antwort sagt „Eine feste Reaktionszeit sage ich nicht zu“"),
    ("it-service-putzbrunn/index.html", "Wie schnell bekomme ich Hilfe? + Feste Reaktionszeiten sage ich nicht zu",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("it-service-vaterstetten/index.html", "Wie schnell bekomme ich Hilfe? + Feste Reaktionszeiten sage ich nicht zu",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("it-service-zorneding/index.html", "Wie schnell bekomme ich Hilfe? + Feste Reaktionszeiten sage ich nicht zu",
     "FAQ-Frage, die Antwort verneint feste Reaktionszeiten"),
    ("it-sicherheit-backup/index.html", "Sofort Gerät vom Netz trennen und mich anrufen.",
     "Anweisung an den Kunden im Notfall"),
    ("ki-dsgvo/index.html", "weil es schneller geht", "beschreibt das Verhalten von Mitarbeitern"),
    ("ki-fuer-kmu/index.html", "Rechenzentrum innerhalb der EU", "Ort, keine Zeit"),
    ("kontakt/index.html", "Wie schnell antwortest du auf eine Anfrage? + Vertragskunden werden bevorzugt behandelt",
     "FAQ-Frage, die Antwort verneint pauschale Reaktionszeiten"),
    ("microsoft-365-betreuung/index.html", "Microsoft 365 ist schnell gebucht – aber sauber eingerichtet",
     "Buchung des Produkts beim Hersteller, keine Zusage"),
    ("netzwerk-wlan-firewall/index.html", "Lückenloses, schnelles WLAN", "Eigenschaft des WLANs"),
    ("ratgeber/e-mails-kommen-nicht-an/index.html", "Meist nicht sofort.", "Verhalten von Mailservern"),
    ("ratgeber/e-mails-kommen-nicht-an/index.html", "So grenzt du in 15 Minuten ein",
     "Reihe „Die ersten 15 Minuten“: Zeit des Lesers fuer die eigene Eingrenzung (Meta-Texte)"),
    ("ratgeber/index.html", "ab wann ein Anruf schneller ist", "Ratgeber: ab wann Anrufen schneller ist als Selbsthilfe"),
    ("ratgeber/phishing-mail-geklickt/index.html", "Dann sofort das Passwort von einem anderen Gerät aus ändern",
     "Ratgeber-Anweisung an den Leser"),
    ("ratgeber/phishing-mail-geklickt/index.html", "Datenschutzaufsicht innerhalb von 72 Stunden",
     "Meldefrist nach Art. 33 DSGVO"),
    ("ratgeber/server-ausgefallen/index.html", "Wie schnell läuft ein ausgefallener Server wieder? + Das hängt von der "
     "Ursache ab.", "FAQ-Frage, die Antwort nennt keine Zusage"),
    ("ratgeber/server-ausgefallen/index.html", "ein hängender Dienst ist in Minuten behoben, eine defekte Festplatte in "
     "einem gespiegelten System in Stunden", "typische Reparaturdauer je Ursache, keine Reaktionszeit"),
    ("schulung/index.html", "jederzeit unterbrechbar und ohne Zeitdruck", "Eigenschaft des Portals (Lerntempo)"),
    ("software-nach-mass/index.html", "Eure Daten könnt ihr jederzeit exportieren.", "Datenhoheit des Kunden"),
    ("software-nach-mass/index.html", "Deine Daten kannst du jederzeit exportieren.", "Datenhoheit des Kunden"),
    ("software-nach-mass/index.html", "Das macht mich schneller.", "KI-Unterstuetzung beim Entwickeln, keine Lieferzusage"),
    ("websites-fuer-betriebe/index.html", "so lässt sich eine alte Website schneller modernisieren",
     "KI-Unterstuetzung beim Modernisieren, keine Lieferzusage"),
    ("websites-fuer-betriebe/index.html", "Schlank und schnell Kein Baukasten", "Ladezeit der Seite (Leistungszeile)"),
    ("websites-fuer-betriebe/index.html", "Die Seite lädt auch im Mobilnetz schnell.", "Ladezeit der Seite"),
    ("websites-fuer-betriebe/index.html", "Wie schnell die Seite am Handy lädt", "Pruefpunkt im Website-Check (Ladezeit)"),
]
# Offene Zusagen: Treffer, die eine Zusage sind oder so gelesen werden koennen, Entscheidung bei Andreas (Text in
# dieser Runde nicht geaendert). Sie halten AK8 nicht rot, werden aber bei jedem Lauf als WARNUNG gemeldet.
# Gleiches Format wie AK8_ALLOW; nach Andreas' Entscheidung Text aendern und Eintrag loeschen (oder nach AK8_ALLOW).
AK8_OPEN = []
# Startseite, Hero „Der Chat“ (Stand 18.10.2026, Release 2.1.1): Texte zeichengleich; AKH prueft sie im HTML der
# Startseite. Der Hero zeigt wieder das Chat-Handy, der Abschnitt IT-Betreuung wieder die typischen Anrufe.
H1_TEXT = "Dein ITler geht nicht ran? Ich schon."   # Andreas 18.10.2026: H1 zurueck
H1_EM = "Ich schon."
PAGE_K_HERO = "Deine IT-Abteilung. Nur extern."
SCHUTZSATZ = "Keine Öffnungszeiten. Vertragskunden zuerst, ohne garantierte Reaktionszeit."
FIRMENKUNDEN_HERO = "Für Selbstständige, Praxen, Handwerk und Büros bis 50 Mitarbeiter."
HERO_WER = "Andreas Grundke · IT-Service für Betriebe im Münchner Osten"
HERO_PROOF = ["5,0 bei {n} Google-Bewertungen", "Über 20 Jahre IT-Erfahrung"]   # A16: nur diese zwei Zeilen
KENNZEICHNUNG_HERO = "Beispiel-Chat, nachgestellt nach typischen Einsätzen."
ITB_H2 = "Typische Anrufe. Und was ich dann mache."   # H2 von #it-betreuung (Text mit <br>)
ITB_ANRUFE = 4                                    # Eintraege in dl.itb-list
WECHSEL_LINK = ("/it-betreuer-wechseln/", "IT-Betreuer nicht mehr da? So übernehme ich.")   # direkt nach dem Hero
# Kein Vergleich, kein Gegenueber im Hero. Gross/klein egal, Teilstring in .hero.
HERO_VERBOTEN = ["Ohne feste Betreuung", "Ticket", "#20871", "Ansage", "Systemhaus", "Dienstleister", "Mitbewerber",
                 "Büro ab Montag", "#4711"]
HERO_CHAT_JS_MAX_GZIP = 8 * 1024
ENTFALLEN_JS = "assets/js/hero-wege.js"           # Skript der frueheren Hero-Buehne, darf nirgends mehr stehen
PROTECTED = ["Angebot ausschließlich für Unternehmen", "ohne garantierte Reaktionszeit", "Warum ein Paket?",
             "Alle Preise zzgl. MwSt.", SCHUTZSATZ, KENNZEICHNUNG_HERO, FIRMENKUNDEN_HERO]
# AK14 seit Fix-Runde B (M10, Spec §5): Herkunftshinweis wortgleich ({n} = Zahlwort + Verb aus dem Generator,
# review_count_phrase(REVIEW_COUNT_GOOGLE)), alle price-per-Zeilen der Startseite mit Betrag (Pakete und ad hoc stehen
# nicht in PRICES, deshalb hier), die Preissaetze mit data-price aus PRICES abgeleitet, Orte (mit PLZ) des Einsatzgebiets.
HERKUNFT = ("Woher die Stimmen kommen: {n} aus meinem Google-Unternehmensprofil, eine hat mir eine Kundin direkt "
            "geschickt. Ich gebe sie wörtlich und ungekürzt wieder. Hier stehen nur Stimmen von Betrieben und Menschen, "
            "für die ich gearbeitet habe. Die Bewertungen bei Google prüft Google nach eigenen Regeln; ändern oder löschen "
            "kann ich sie dort nicht. Alle Google-Bewertungen stehen im Google-Profil.")
HOME_PRICE_LINES = ["110 € netto/Stunde zzgl. MwSt.", "149 € /Monat zzgl. MwSt.", "249 € /Monat zzgl. MwSt.",
                    "449 € /Monat zzgl. MwSt."]
HOME_PRICE_SENTENCES = [("Website-Betrieb {} netto im Monat", "website_betrieb"),
                        ("Betrieb einer eigenen Anwendung ab {} netto im Monat", "software_betrieb"),
                        ("Festpreis für den Bau, Betrieb ab {} netto im Monat", "software_betrieb"),
                        ("Betrieb auf Wunsch {} netto im Monat", "website_betrieb")]
GEO_PLACES = [("Grasbrunn", "85630"), ("Ottobrunn", "85521"), ("Vaterstetten", "85591"), ("Haar", "85540"),
              ("Neubiberg", "85579"), ("Putzbrunn", "85640"), ("Hohenbrunn", "85662"), ("Baldham", ""),
              ("Parsdorf", ""), ("Zorneding", ""), ("Eglharting", "")]
# AK11a (Spec §7, Textblatt §1): Region und Anbieter in den ersten 300 Zeichen ab <main>
REGIONS = ("münchner osten", "münchen ost", "grasbrunn")
PROVIDERS = ("grundke it-service", "andreas grundke")
VOICE_MAX_PAGES = 4   # je Person hoechstens auf 4 Unterseiten (Textblatt §3, Startseite zaehlt nicht)


def pages():
    out = [ROOT / "index.html", ROOT / "404.html"]
    for p in sorted(ROOT.rglob("index.html")):
        rel = p.relative_to(ROOT).as_posix()
        if rel == "index.html" or rel.split("/")[0] in SKIP:
            continue
        out.append(p)
    return out


def rel(p):
    return p.relative_to(ROOT).as_posix()


def legal_pages():
    return [p for p in pages() if rel(p).split("/")[0] in LEGAL]


def kuemmerer_pages():
    skip = LEGAL + ("ratgeber", "fernwartung", "kontakt", "empfehlungen", "404.html")
    return [p for p in pages() if rel(p).split("/")[0] not in skip]


def read(p):
    return p.read_text(encoding="utf-8")


def text_of(fragment):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S)
    # Inline-Tags ohne Leerzeichen entfernen ("wechseln</a>." -> "wechseln."), alle anderen Tags als Trenner
    t = re.sub(r"</?(a|b|strong|em|i|span|code|small|mark|abbr)(\s[^>]*)?>", "", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def styles(s):
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", s, re.S))


_GEN = []


def gen():
    """Generator-Modul (Daten PLACES/SERVICES, STYLE, REVIEWS), einmal importiert."""
    if not _GEN:
        sys.path.insert(0, str(ROOT / "tools"))
        import build_landingpages
        _GEN.append(build_landingpages)
    return _GEN[0]


def generator_pages():
    """(Pfad, Daten) aller Seiten, die tools/build_landingpages.py erzeugt (Orte und SERVICES)."""
    g = gen()
    out = [(ROOT / ("it-service-" + p["slug"]) / "index.html", p) for p in g.PLACES]
    return out + [(ROOT / s["slug"] / "index.html", s) for s in g.SERVICES]


def ak1():
    errs = []
    for p in pages():
        if rel(p) == "index.html":
            continue
        css = styles(read(p))
        for sel in FORBIDDEN_SELECTORS:
            if re.search(re.escape(sel) + r"(?![\w-])", css):
                errs.append(f"{rel(p)}: eigener Stil fuer {sel}")
    # Generator-Seiten: kein seitenspezifischer <style> (KI_STYLE, NEW_STYLE, STYLE_LEGACY), nur die
    # gemeinsamen Prosa-Regeln aus STYLE (Task 7)
    shared = styles(gen().STYLE)
    for p, _d in generator_pages():
        if styles(read(p)) != shared:
            errs.append(f"{rel(p)}: eigener <style> neben den gemeinsamen Prosa-Regeln")
    return errs


def ak2():
    errs = [f"{rel(p)}: alte Huelle {w}" for p in pages() for w in OLD_WRAPPERS
            if re.search(r'class="[^"]*\b' + w + r'\b', read(p))]
    # Eine Huelle fuer alle Generator-Seiten: Kopf .page-head und Abschluss .cta-sec (Task 7)
    for p, _d in generator_pages():
        s = read(p)
        for need, what in (('<section class="sec sec--glow page-head">', "Kopf .page-head"),
                           ('<section class="cta-sec">', "Abschluss .cta-sec")):
            if need not in s:
                errs.append(f"{rel(p)}: {what} fehlt")
    return errs


def ak2b():
    """Kopf je Seitenart (Task 7): Hubs (Daten mit "hero") zeigen die Wege zu allen Unterseiten als
    nav.lp-paths im Kopf und die Akzentzeile als <em> in der H1. Ratgeber (kind "ratgeber-hub"/"ratgeber") ohne
    K4 (.page-k) und im Kopf nur den Anruf-Knopf (kein WhatsApp, keine Belegzeile); Ratgeber-Artikel in
    einer Lesespalte (.measure) mit der Kurzantwort (.lp-answer). Kaesten mit Handlung (.ki-check:
    Potenzialcheck, Website-Check) stehen nie in einem zugeklappten <details>."""
    errs = []
    for p, d in generator_pages():
        s = read(p)
        head = first(r'(<section class="sec sec--glow page-head">.*?</section>)', s)
        if d.get("hero"):
            nav = first(r'(<nav class="lp-paths".*?</nav>)', head)
            missing = [h for _t, _d, h in d["hero"]["paths"] if 'href="' + h + '"' not in nav]
            if not nav or missing:
                errs.append(f"{rel(p)}: Wege (nav.lp-paths) im Kopf fehlen {missing or ''}")
            if "<em>" not in first(r"(<h1[^>]*>.*?</h1>)", head):
                errs.append(f"{rel(p)}: Akzentzeile der H1 nicht als <em>")
        if d.get("kind") in ("ratgeber-hub", "ratgeber"):
            if "page-k" in s:
                errs.append(f"{rel(p)}: Ratgeber mit K4 (.page-k)")
            if "hc-call" not in head or "hc-wa" in head or "hc-proof" in head:
                errs.append(f"{rel(p)}: Ratgeber-Kopf nicht nur mit Anruf-Knopf")
        if d.get("kind") == "ratgeber" and not re.search(r'class="[^"]*\bmeasure\b[^"]*"[^>]*>\s*<div class="lp-answer">', s):
            errs.append(f"{rel(p)}: Artikel nicht in der Lesespalte (.measure) mit Kurzantwort")
    for p in pages():
        for blk in re.findall(r"<details\b(?![^>]*\bopen\b)[^>]*>.*?</details>", read(p), re.S):
            if 'class="ki-check"' in blk:
                errs.append(f"{rel(p)}: Kasten .ki-check steht zugeklappt in <details>")
    return errs


def ak7():
    errs = []
    for p in kuemmerer_pages():
        m = re.search(r'class="[^"]*\bpage-k\b[^"]*"[^>]*>(.*?)</p>', read(p), re.S)
        if not m or len(text_of(m.group(1))) < 30:
            errs.append(f"{rel(p)}: Kuemmerer-Satz (.page-k) fehlt")
    return errs


VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class _Elements(HTMLParser):
    """Ganze Elemente (Start- bis End-Tag, verschachtelte eingeschlossen), die want(tag, attrs) benennt.
    Liefert (Name, HTML-Ausschnitt); in einem gefundenen Element wird nicht weiter gesucht."""

    def __init__(self, src, want):
        super().__init__(convert_charrefs=True)
        self.src, self.want, self.stack, self.cap, self.out = src, want, [], None, []
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", src)]

    def _off(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID_TAGS:
            return
        self.stack.append(tag)
        if self.cap is None:
            name = self.want(tag, dict(attrs))
            if name:
                self.cap = (name, self._off(), len(self.stack))

    def handle_endtag(self, tag):
        if tag in VOID_TAGS or tag not in self.stack:
            return
        while self.stack:
            t = self.stack.pop()
            if self.cap and len(self.stack) < self.cap[2]:
                end = self.src.index(">", self._off()) + 1
                self.out.append((self.cap[0], self.src[self.cap[1]:end]))
                self.cap = None
            if t == tag:
                break


def elements(src, want):
    parser = _Elements(src, want)
    parser.feed(src)
    parser.close()
    return parser.out


def _has_class(attrs, cls):
    return cls in (attrs.get("class") or "").split()


def ak8_sources(p):
    """(Quelle, Text) einer Seite fuer AK8: sichtbarer Text in <main> (ohne Kundenzitate und Ratgeber-Lesespalte),
    die <summary> im Fuss, <title>, Meta-, og- und twitter-Description sowie og/twitter:title."""
    s = re.sub(r'<blockquote class="testi-txt".*?</blockquote>', " ", read(p), flags=re.S)
    main = first(r"(<main\b.*?</main>)", s)
    for _n, frag in elements(main, lambda tag, a: tag == "article" and _has_class(a, "lp-article") and "Lesespalte"):
        main = main.replace(frag, " ")
    out = [("main", text_of(main).replace(AK8_LEITZEILE, " "))]
    foot = first(r'(<footer class="site-footer">.*?</footer>)', s)
    out += [("Fuss summary", text_of(f)) for _n, f in elements(foot, lambda tag, a: tag == "summary" and "summary")]
    for m in re.finditer(r"<title>(.*?)</title>", s, re.S):
        out.append(("title", html.unescape(m.group(1))))
    for attr, name in (("name", "description"), ("property", "og:description"), ("name", "twitter:description"),
                       ("property", "og:title"), ("name", "twitter:title")):
        for m in re.finditer(r'<meta\s+' + attr + r'="' + re.escape(name) + r'"\s+content="([^"]*)"', s):
            out.append(("meta " + name, html.unescape(m.group(1))))
    return out


def hero_chat_texts():
    """Zeichenketten aus assets/js/hero-chat.js (Faelle, Nachtantwort, Saetze ueber der Uhr), ohne Kommentare."""
    js = re.sub(r"/\*.*?\*/|(?<![:'\\])//[^\n]*", " ", read(ROOT / AK8_HERO_JS), flags=re.S)
    return [("JS-Text", re.sub(r"\\(.)", r"\1", m.group(1)))
            for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'", js)]


def ak8_hits():
    """Alle Treffer der Wortliste: (Seite, Quelle, Wort, Text, Start, Ende). Rechtsseiten ausgenommen (Spec AK8)."""
    hits = []
    sources = [(rel(p), ak8_sources(p)) for p in pages() if rel(p).split("/")[0] not in LEGAL]
    sources.append((AK8_HERO_JS, hero_chat_texts()))
    for page, items in sources:
        for src, text in items:
            text = re.sub(r"\s+", " ", text.replace("\u00ad", "")).strip()
            for m in PROMISE_RE.finditer(text):
                hits.append((page, src, m.group(0), text, m.start(), m.end()))
    return hits


def ak8_allowed(hit, allow):
    page, _src, _w, text, a, b = hit
    for k, (pg, snip, _why) in enumerate(allow):
        if pg != page:
            continue
        i = text.find(snip)
        while i >= 0:
            if i <= a and b <= i + len(snip):
                return k
            i = text.find(snip, i + 1)
    return None


WARNINGS = []   # Hinweise, die keine Pruefung rot machen (am Ende ausgegeben)


def ak8(allow=None, open_=None):
    """Keine Zusagen (Spec AK8, Umfang siehe Kommentar ueber AK8_HERO_JS). Jeder Treffer der Wortliste ist ein Fehler, ausser er steht
    in AK8_ALLOW (erlaubt) oder AK8_OPEN (offene Zusage, nur WARNUNG). Eintraege ohne Treffer sind ein Fehler."""
    allow = AK8_ALLOW if allow is None else allow
    open_ = AK8_OPEN if open_ is None else open_
    errs, used_a, used_o = [], set(), set()
    for hit in ak8_hits():
        page, src, word, text, a, b = hit
        where = f"{page}: Zusage-Wort '{word}' ({src}): …{text[max(0, a - 60):b + 60]}…"
        k = ak8_allowed(hit, allow)
        if k is not None:
            used_a.add(k)
            continue
        k = ak8_allowed(hit, open_)
        if k is not None:
            used_o.add(k)
            WARNINGS.append(f"AK8 offene Zusage (Entscheidung Andreas): {where}")
            continue
        errs.append(where)
    for name, lst, used in (("AK8_ALLOW", allow, used_a), ("AK8_OPEN", open_, used_o)):
        errs += [f"{name} ohne Treffer (veraltet): {pg}: {snip!r}" for k, (pg, snip, _w) in enumerate(lst)
                 if k not in used]
    return errs


def faq_schema(s):
    out = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        stack = [json.loads(blk)]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if x.get("@type") == "Question":
                    out.append((x["name"].strip(), re.sub(r"\s+", " ", x["acceptedAnswer"]["text"]).strip()))
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return out


def faq_visible(s):
    vis = []
    for q, a in re.findall(r'<details class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*<div class="faq-a">(.*?)</div>\s*</details>', s, re.S):
        q = re.sub(r'<span class="faq-ico".*?</span>', "", q, flags=re.S)
        vis.append((text_of(q), text_of(a)))
    return vis


def ak9():
    errs = []
    for p in pages():
        s = read(p)
        sch, vis = sorted(faq_schema(s)), sorted(faq_visible(s))
        if sch != vis:
            errs.append(f"{rel(p)}: FAQ sichtbar ({len(vis)}) != Schema ({len(sch)}) oder Text weicht ab")
    return errs


def schema_nodes(s):
    """Alle JSON-LD-Knoten (dict) einer Seite, verschachtelte eingeschlossen."""
    out = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        stack = [json.loads(blk)]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                out.append(x)
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return out


def first(rx, s):
    m = re.search(rx, s, re.S)
    return m.group(1) if m else ""


def ak9b():
    """Kundenstimmen aus einer Quelle (REVIEWS im Generator). Jede Karte <figure class="testi-card">
    traegt Name (testi-who), Quelle (testi-role: "Google-Bewertung" nur bei Google-Stimmen) und den
    Text woertlich und ungekuerzt in <blockquote class="testi-txt">; Sterne (.stars) nur bei
    Google-Stimmen. Startseite zusaetzlich: jede Stimme genau einmal, review[]/reviewBody im Schema =
    REVIEWS, reviewRating nur bei Google-Stimmen, aggregateRating reviewCount = ratingCount =
    REVIEW_COUNT_GOOGLE, Belegzeile [data-proof] nennt REVIEW_COUNT_GOOGLE.
    Unterseiten: nur Google-Stimmen (die direkt uebermittelte steht nur auf der Startseite), jede
    Person auf hoechstens VOICE_MAX_PAGES Unterseiten."""
    try:
        reviews, n_google = gen().REVIEWS, gen().REVIEW_COUNT_GOOGLE
    except (ImportError, AttributeError) as e:
        return [f"Generator ohne REVIEWS/REVIEW_COUNT_GOOGLE: {e}"]
    by_name = {r["name"]: r for r in reviews}
    errs = []
    sub_pages = {}
    if sum(r["source"] == "Google-Bewertung" for r in reviews) > n_google:
        errs.append("REVIEWS: mehr Google-Stimmen als REVIEW_COUNT_GOOGLE")
    for p in pages():
        s = read(p)
        seen = []
        for c in re.findall(r'<figure class="testi-card[^"]*"[^>]*>(.*?)</figure>', s, re.S):
            who = text_of(first(r'class="testi-who"[^>]*>(.*?)</', c))
            role = text_of(first(r'class="testi-role"[^>]*>(.*?)</', c))
            txt = text_of(first(r'<blockquote class="testi-txt"[^>]*>(.*?)</blockquote>', c))
            r = by_name.get(who)
            if not r:
                errs.append(f"{rel(p)}: Stimme '{who}' steht nicht in REVIEWS")
                continue
            seen.append(who)
            if txt != "„" + " ".join(r["paragraphs"]) + "“":
                errs.append(f"{rel(p)}: Text von {who} weicht von REVIEWS ab")
            if ("Google" in role) != (r["source"] == "Google-Bewertung"):
                errs.append(f"{rel(p)}: Quelle von {who} falsch beschriftet ('{role}')")
            if r["source"] != "Google-Bewertung" and re.search(r'class="stars\b', c):
                errs.append(f"{rel(p)}: Sterne bei {who}, die Stimme ist keine Google-Bewertung")
        if rel(p) != "index.html":
            for who in set(seen):
                sub_pages.setdefault(who, []).append(rel(p))
                if by_name[who]["source"] != "Google-Bewertung":
                    errs.append(f"{rel(p)}: {who} ist keine Google-Bewertung und steht nur auf der Startseite")
            continue
        if sorted(seen) != sorted(by_name):
            errs.append(f"index.html: Stimmen sichtbar {sorted(seen)} != REVIEWS {sorted(by_name)}")
        nodes = schema_nodes(s)
        sch = [(x["author"]["name"], x["reviewBody"]) for x in nodes if x.get("@type") == "Review"]
        want = [(r["name"], "\n\n".join(r["paragraphs"])) for r in reviews]
        if sorted(sch) != sorted(want):
            errs.append("index.html: review[]/reviewBody im Schema != REVIEWS")
        for x in nodes:
            if x.get("@type") == "Review" and x["author"]["name"] in by_name:
                google = by_name[x["author"]["name"]]["source"] == "Google-Bewertung"
                if google != ("reviewRating" in x):
                    errs.append(f"index.html: reviewRating bei {x['author']['name']} "
                                + ("fehlt" if google else "gesetzt, ist aber keine Google-Bewertung"))
        agg = [(x.get("reviewCount"), x.get("ratingCount")) for x in nodes if x.get("@type") == "AggregateRating"]
        if agg != [(str(n_google), str(n_google))]:
            errs.append(f"index.html: aggregateRating reviewCount/ratingCount {agg} != {n_google}")
        proof = re.search(r"bei (\d+) Google-Bewertungen", text_of(first(r"(<a[^>]*\bdata-proof\b.*?</a>)", s)))
        if not proof or int(proof.group(1)) != n_google:
            errs.append(f"index.html: Belegzeile [data-proof] nennt nicht {n_google} Google-Bewertungen")
    for who, where in sub_pages.items():
        if len(where) > VOICE_MAX_PAGES:
            errs.append(f"{who} steht auf {len(where)} Unterseiten (hoechstens {VOICE_MAX_PAGES}): {where}")
    # llms.txt schreibt der Generator nicht; die Zahl dort muss trotzdem REVIEW_COUNT_GOOGLE sein (Fix-Runde B, M14)
    m = re.search(r"Google-Bewertung: [\d,]+ / 5 bei (\d+) Rezensionen", read(ROOT / "llms.txt"))
    if not m or int(m.group(1)) != n_google:
        errs.append(f"llms.txt: nennt {m.group(1) if m else 'keine'} Google-Rezensionen, REVIEW_COUNT_GOOGLE = {n_google}")
    return errs


def ak11a():
    """Die ersten 300 Zeichen Text ab <main> (Dokumentreihenfolge: Krumen, H1, K4, Antwortsatz)
    nennen Leistung, Region und Anbieter (Spec §7, AK11). Leistung = aktuelle Brotkrume (sonst H1),
    Region = REGIONS oder auf Ortsseiten der Ort, Anbieter = PROVIDERS. Startseite ausgenommen."""
    errs = []
    for p in kuemmerer_pages():
        if rel(p) == "index.html":
            continue
        main = first(r"(<main.*?</main>)", read(p))
        text = text_of(main)[:300].lower()
        service = text_of(first(r'<li aria-current="page">(.*?)</li>', main) or first(r"<h1[^>]*>(.*?)</h1>", main))
        slug = rel(p).split("/")[0]
        regions = REGIONS + ((slug[len("it-service-"):],) if slug.startswith("it-service-") else ())
        missing = [name for name, ok in (("Leistung", bool(service) and service.lower() in text),
                                         ("Region", any(r in text for r in regions)),
                                         ("Anbieter", any(a in text for a in PROVIDERS))) if not ok]
        if missing:
            errs.append(f"{rel(p)}: erste 300 Zeichen ohne {', '.join(missing)}")
    return errs


def legal_text(page_html):
    """Rechtstext einer Seite: <main> ohne nav/header/cta-sec-Huelle. Fuer Baseline UND Vergleich."""
    col = re.search(r"<main.*?</main>", page_html, re.S).group(0)
    col = re.sub(r"<nav[^>]*>.*?</nav>", " ", col, flags=re.S)
    col = re.sub(r"<header[^>]*>.*?</header>", " ", col, flags=re.S)
    col = re.sub(r"<section[^>]*\bcta-sec\b[^>]*>.*?</section>", " ", col, flags=re.S)
    return text_of(col)


# AK14 seit Task 9 (Fix-Runde 1): legal_hash.json speichert nur Hashes. Verglichen wird deshalb der Text des Stands der
# Vorher-Messung (Commit 865b00a, dessen legal_text() genau diese Hashes ergibt) mit dem Text jetzt, beide nach
# legal_norm(). Die Hashes bleiben die Pruefung, dass die Basis die gemessene ist; keine neue Baseline.
LEGAL_BASE_COMMIT = "865b00a"
# Basis je Seite. Ausnahme: Die Barrierefreiheitserklaerung wurde von Andreas freigegeben inhaltlich geaendert,
# zuerst am 12.10.2026 (Bild-Slider -> Beispiel-Chat, Wischleiste, Fuss, Stand-Datum; Sicherung
# ../_intern/messungen/vorher/legal_hash_vor_2026-10-12.json), dann am 18.10.2026 (Hero-Buehne, Chat-Abschnitt,
# Kontraste, Kontaktleiste, Stand-Datum; Sicherung ../_intern/messungen/vorher/legal_hash_vor_2026-10-18.json),
# danach am 18.10.2026 der Film-Absatz (Sicherung legal_hash_vor_2026-10-18-film.json).
# Ihre Basis ist der Commit mit dem freigegebenen Text, legal_hash.json traegt fuer sie den rohen Hash dieses Stands.
# Alle anderen Rechtstexte bleiben bei 865b00a.
LEGAL_BASE_COMMITS = {"barrierefreiheit/index.html": "8867f42"}
# Nur diese Zeichen zaehlen nicht zum Rechtstext: weiches Trennzeichen (U+00AD, H1 der Huelle), Emoji-Variantenwahl
# (U+FE0F) und Bildzeichen U+1F300-U+1FAFF (AGB-Symbol, jetzt SVG). ©, ®, ™, Pfeile, § und Striche bleiben Text.
LEGAL_DROP_RE = re.compile("[\u00ad\ufe0f\U0001F300-\U0001FAFF]")


def legal_norm(t):
    """Text ohne LEGAL_DROP_RE; Leerraum danach wieder einfach (ein entferntes Symbol vor einem Wort hinterliesse
    sonst ein fuehrendes oder doppeltes Leerzeichen)."""
    return re.sub(r"\s+", " ", LEGAL_DROP_RE.sub("", t)).strip()


def legal_diff(before, now):
    """None, wenn beide Texte nach legal_norm() gleich sind, sonst die erste Abweichung mit Kontext."""
    a, b = legal_norm(before), legal_norm(now)
    if a == b:
        return None
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    return f"erste Abweichung bei Zeichen {i}: vorher {a[max(0, i - 30):i + 30]!r} jetzt {b[max(0, i - 30):i + 30]!r}"


def legal_base(rel_path):
    """Basis-Commit der Rechtsseite (LEGAL_BASE_COMMITS, sonst LEGAL_BASE_COMMIT)."""
    return LEGAL_BASE_COMMITS.get(rel_path, LEGAL_BASE_COMMIT)


def legal_base_html(rel_path):
    """Seite im Stand ihres Basis-Commits (git show)."""
    out = subprocess.run(["git", "-C", str(ROOT), "show", legal_base(rel_path) + ":" + rel_path], capture_output=True)
    if out.returncode:
        raise RuntimeError(out.stderr.decode("utf-8", "replace").strip())
    return out.stdout.decode("utf-8")


def ak14():
    """Geschuetzte Inhalte der Startseite (Spec §5, seit Fix-Runde B mit M10): PROTECTED, Herkunftshinweis wortgleich
    (Zahl aus REVIEW_COUNT_GOOGLE), alle price-per-Zeilen samt Betrag, die Preissaetze aus PRICES (data-price),
    Orte und PLZ des Einsatzgebiets; dazu die Fernwartungs-Downloads. Die Rechtstexte prueft AK14r."""
    errs = []
    raw = read(ROOT / "index.html")
    home = text_of(raw)
    for t in PROTECTED:
        if t not in home:
            errs.append(f"index.html: geschuetzter Satz fehlt: {t}")
    herkunft = [text_of(f) for _n, f in elements(raw, lambda tag, a: a.get("id") == "bewertungen-herkunft" and "h")]
    want = HERKUNFT.format(n=gen().review_count_phrase(gen().REVIEW_COUNT_GOOGLE))
    if herkunft != [want]:
        errs.append(f"index.html: Herkunftshinweis #bewertungen-herkunft nicht wortgleich ({len(herkunft)}x): "
                    f"{herkunft[0][:90] if herkunft else 'fehlt'}… statt {want[:90]}…")
    per = re.findall(r'class="price-per"', raw)
    if len(per) != len(HOME_PRICE_LINES):
        errs.append(f"index.html: {len(per)} price-per-Zeilen statt {len(HOME_PRICE_LINES)}")
    for line in HOME_PRICE_LINES:
        if line not in home:
            errs.append(f"index.html: Preiszeile fehlt: {line}")
    prices, eur = gen().PRICES, gen().eur
    spans = re.findall(r'<span data-price="(\w+)">([^<]*)</span>', raw)
    for key, val in spans:
        if key not in prices or val != eur(prices[key]):
            errs.append(f"index.html: data-price {key} zeigt {val!r}, PRICES ergibt {eur(prices.get(key, 0))!r}")
    for tpl, key in HOME_PRICE_SENTENCES:
        line = tpl.format(eur(prices[key])).replace(" ", " ")
        if line not in home:
            errs.append(f"index.html: Preissatz aus PRICES fehlt: {line}")
    geo = text_of(first(r'(<section[^>]*id="einsatzgebiet".*?</section>)', raw))
    chips = text_of(first(r'(<div class="chips geo-chips">.*?</div>)', raw))
    for name, plz in GEO_PLACES:
        need = f"{name} (PLZ {plz})" if plz else name
        if need not in geo:
            errs.append(f"index.html: Einsatzgebiet ohne {need}")
        if name not in chips.split():
            errs.append(f"index.html: Orte-Chips ohne {name}")
    fw = read(ROOT / "fernwartung/index.html")
    for need in ("https://msp.grundke-it.de/dist/grundke-support.exe", "https://msp.grundke-it.de/dist/grundke-support-linux-amd64"):
        if need not in fw:
            errs.append(f"fernwartung: Download fehlt {need}")
    return errs


def ak14r():
    """Rechtstexte zeichengleich zum Basis-Commit (braucht ../_intern/ und Git-Historie, nicht in --ci)."""
    errs = []
    base = INTERN / "vorher" / "legal_hash.json"
    if not base.exists():
        errs.append(f"Rechtstexte: Baseline {base} fehlt, AK14 nicht pruefbar")
    else:
        old = json.loads(base.read_text(encoding="utf-8"))
        for p in legal_pages():
            try:
                before = legal_text(legal_base_html(rel(p)))
            except RuntimeError as e:
                errs.append(f"{rel(p)}: Basis {legal_base(rel(p))} nicht lesbar ({e})")
                continue
            # (a) Konsistenz: die Basis ist der gemessene Stand (roher Hash wie in legal_hash.json)
            if old.get(rel(p)) != hashlib.sha256(before.encode()).hexdigest():
                errs.append(f"{rel(p)}: Basis {legal_base(rel(p))} passt nicht zu legal_hash.json")
            # (b) Gleichheit: Rechtstext jetzt = Basis, nach legal_norm()
            diff = legal_diff(before, legal_text(read(p)))
            if diff:
                errs.append(f"{rel(p)}: Rechtstext geaendert, {diff}")
    return errs


VERSIONED_ASSETS = r"(?:style\.css|main\.js|fernwartung\.js|fonts\.css|lenis\.min\.js|hero-chat\.js)"


def precache_urls():
    """Eintraege aus PRECACHE_URLS in sw.js (nur die Zeichenketten; '… + ASSET_VER' bleibt als ?v= erkennbar)."""
    block = re.search(r"const PRECACHE_URLS\s*=\s*\[(.*?)\];", read(ROOT / "sw.js"), re.S)
    if not block:
        return None
    return re.findall(r"'([^']*)'", block.group(1))


def precache_target(url):
    """URL aus dem Pre-Cache -> Datei im Repo: ?v= ab, '/' = index.html, Verzeichnis-URL = index.html darin."""
    path = url.split("?", 1)[0].lstrip("/")
    if path == "" or path.endswith("/"):
        path += "index.html"
    return ROOT / path


def ak13(urls=None, root_check=None):
    """style.css, main.js, fernwartung.js, fonts.css, lenis.min.js und hero-chat.js tragen ueberall ?v=, alle dieselbe
    Version wie ASSET_VER in sw.js. Dazu: jede Datei im Pre-Cache von sw.js muss im Repo existieren (sonst wirft
    cache.addAll beim Install und jedes spaetere Service-Worker-Update bleibt still haengen)."""
    errs = []
    for p in pages():
        for ref in re.findall(r'href="([^"]*' + VERSIONED_ASSETS + r'[^"]*)"|src="([^"]*' + VERSIONED_ASSETS + r'[^"]*)"',
                              read(p)):
            r = ref[0] or ref[1]
            if "?v=" not in r:
                errs.append(f"{rel(p)}: {r} ohne Version")
    # Pre-Cache des Service Workers muss dieselbe Version tragen wie die Seiten
    vers = {v for p in pages() for v in re.findall(VERSIONED_ASSETS + r'\?v=([\w.-]+)"', read(p))}
    sw = re.search(r"const ASSET_VER\s*=\s*'([^']+)'", read(ROOT / "sw.js"))
    if not sw or vers != {sw.group(1)}:
        errs.append(f"sw.js: ASSET_VER {sw.group(1) if sw else 'fehlt'} passt nicht zu den Seiten {sorted(vers)}")
    urls = precache_urls() if urls is None else urls
    if not urls:
        errs.append("sw.js: PRECACHE_URLS nicht gefunden oder leer")
    exists = root_check or (lambda f: f.is_file())
    for u in urls or []:
        if not exists(precache_target(u)):
            errs.append(f"sw.js: Pre-Cache-Eintrag {u!r} hat keine Datei im Repo (Install wuerfe, Updates blockiert)")
    return errs


# AK13v (Fix-Runde B, M5): Versionen gegen den Stand, der live ist (ORIGIN_REF). Ausgeliefert wird alles ausser dem,
# was deploy.yml vor dem Hochladen entfernt (tools, .impeccable, Audit 2026-04, Markdown im Wurzelordner, .github,
# .gitignore).
ORIGIN_REF = "origin/main"
DEPLOY_DROPPED = ("tools/", ".impeccable/", "Audit 2026-04/", ".github/")


def deployable(path):
    if path.startswith(DEPLOY_DROPPED) or path == ".gitignore":
        return False
    return not ("/" not in path and path.endswith(".md"))


def git(*args):
    out = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True)
    if out.returncode:
        raise RuntimeError(out.stderr.decode("utf-8", "replace").strip() or "git " + " ".join(args))
    return out.stdout.decode("utf-8")


def _const(rx, text):
    m = re.search(rx, text, re.M)
    return m.group(1) if m else None


def ak13v():
    """Geaenderte Dateien gegen ORIGIN_REF (Arbeitsbaum inkl. nicht versionierter Dateien): Aendert sich etwas unter
    assets/css/ oder assets/js/, muss ASSET_VER im Generator und in sw.js anders sein als dort. Aendert sich irgendeine
    ausgelieferte Datei, muessen CACHE_NAME und RUNTIME_CACHE in sw.js anders sein. Ohne git oder ORIGIN_REF: rot."""
    try:
        git("rev-parse", "--verify", "--quiet", ORIGIN_REF + "^{commit}")
        changed = [f for f in git("diff", "--name-only", "-z", ORIGIN_REF, "--").split("\0") if f]
        changed += [f for f in git("ls-files", "--others", "--exclude-standard", "-z").split("\0") if f]
        old_gen = git("show", ORIGIN_REF + ":tools/build_landingpages.py")
        old_sw = git("show", ORIGIN_REF + ":sw.js")
    except (OSError, RuntimeError) as e:
        return [f"AK13v nicht pruefbar: git oder {ORIGIN_REF} fehlt ({e}). Ohne Vergleich mit dem Live-Stand ist "
                "nicht belegt, dass Asset- und Cache-Versionen erhoeht sind; 'git fetch origin' und erneut pruefen."]
    errs, sw = [], read(ROOT / "sw.js")
    assets = sorted(f for f in changed if f.startswith(("assets/css/", "assets/js/")))
    if assets:
        for where, old, new in (("Generator", _const(r'^ASSET_VER = "([^"]+)"', old_gen), gen().ASSET_VER),
                                ("sw.js", _const(r"const ASSET_VER\s*=\s*'([^']+)'", old_sw),
                                 _const(r"const ASSET_VER\s*=\s*'([^']+)'", sw))):
            if old == new:
                errs.append(f"{where}: ASSET_VER {new} wie auf {ORIGIN_REF}, obwohl geaendert: {', '.join(assets)}")
    deploy = sorted(f for f in set(changed) if deployable(f))
    if deploy:
        for name in ("CACHE_NAME", "RUNTIME_CACHE"):
            rx = r"const " + name + r"\s*=\s*'([^']+)'"
            if _const(rx, old_sw) == _const(rx, sw):
                errs.append(f"sw.js: {name} {_const(rx, sw)} wie auf {ORIGIN_REF}, obwohl {len(deploy)} ausgelieferte "
                            f"Datei(en) geaendert sind, z. B. {', '.join(deploy[:3])}")
    return errs


def ak13s():
    """Seit 17.10.2026 (Relaunch R1, Spec D15/G6): Die sichtbare Website-Version haengt am Cache. SITE_VERSION (Generator)
    muss dem Suffix von CACHE_NAME in sw.js gleichen ('grundke-it-v2.0.0' -> '2.0.0'); SITE_DATE_DISP hat die Form
    TT.MM.JJJJ; jede Seite traegt im <footer> 'Version {SITE_VERSION} · Stand {SITE_DATE_DISP}'."""
    g, errs = gen(), []
    ver, disp = getattr(g, "SITE_VERSION", None), getattr(g, "SITE_DATE_DISP", None)
    if not ver:
        errs.append("Generator: SITE_VERSION fehlt")
    if not disp:
        errs.append("Generator: SITE_DATE_DISP fehlt")
    elif not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", disp):
        errs.append(f"Generator: SITE_DATE_DISP '{disp}' nicht in der Form TT.MM.JJJJ")
    cache = _const(r"const CACHE_NAME\s*=\s*'grundke-it-v([^']+)'", read(ROOT / "sw.js"))
    if cache is None:
        errs.append("sw.js: CACHE_NAME nicht im Format 'grundke-it-v<Version>'")
    elif ver and cache != ver:
        errs.append(f"SITE_VERSION {ver} weicht vom Suffix von CACHE_NAME ({cache}) ab")
    if not ver or not disp:
        return errs
    want = f"Version {ver} · Stand {disp}"
    for p in pages():
        m = re.search(r"<footer\b[^>]*>.*?</footer>", read(p), re.S)
        if not m:
            errs.append(f"{rel(p)}: kein <footer>")
        elif want not in html.unescape(re.sub(r"<[^>]+>", "", m.group(0))).replace(" ", " "):
            errs.append(f"{rel(p)}: Fuss ohne '{want}'")
    return errs


# ----------------------------------------------------------------------------------------------------------------------
# AKH (Stand 18.10.2026, Hero mit Chat-Handy): Hero-Kopf mit Firmenkunden-Zeile, Chat-Handy mit erster Kundennachricht
# im HTML, Pause-Knopf und sichtbarer Kennzeichnung, Link nach dem Hero, Abschnitt IT-Betreuung mit den typischen
# Anrufen und das Skript hero-chat.js gegen den Markup-Vertrag. Eigener kleiner DOM-Baum, weil Vorfahren (aria-hidden,
# Handy, Abschnitt) ueber die Bewertung eines Elements entscheiden.
# ----------------------------------------------------------------------------------------------------------------------
_INLINE = {"a", "b", "strong", "em", "i", "span", "code", "small", "mark", "abbr", "time", "sub", "sup"}


class _N:
    __slots__ = ("tag", "attrs", "parent", "kids")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.kids = tag, attrs, parent, []

    def has(self, c):
        return c in (self.attrs.get("class") or "").split()

    def walk(self):
        yield self
        for k in self.kids:
            if isinstance(k, _N):
                yield from k.walk()

    def up(self, pred):
        """Naechster Vorfahre oder das Element selbst, auf das pred zutrifft."""
        n = self
        while n is not None:
            if n.tag != "#root" and pred(n):
                return n
            n = n.parent
        return None

    def text(self):
        parts = []

        def rec(n):
            for k in n.kids:
                if isinstance(k, str):
                    parts.append(k)
                elif k.tag in ("script", "style", "svg"):
                    continue
                elif k.tag in _INLINE:
                    rec(k)
                else:
                    parts.append(" ")
                    rec(k)
                    parts.append(" ")
        rec(self)
        return re.sub(r"\s+", " ", "".join(parts).replace(" ", " ")).strip()


class _Dom(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = _N("#root", {}, None)
        self.feed(src)
        self.close()

    def handle_starttag(self, tag, attrs):
        n = _N(tag, {k: (v if v is not None else "") for k, v in attrs}, self.cur)
        self.cur.kids.append(n)
        if tag not in VOID_TAGS:
            self.cur = n

    def handle_endtag(self, tag):
        n = self.cur
        while n.parent is not None and n.tag != tag:
            n = n.parent
        if n.parent is not None:
            self.cur = n.parent

    def handle_data(self, d):
        self.cur.kids.append(d)


def _norm(t):
    return re.sub(r"\s+", " ", t.replace(" ", " ")).strip()


def hero_chat_first_me():
    """Erste Kundennachricht des ersten Falls in assets/js/hero-chat.js (CASES[0].me)."""
    m = re.search(r"var CASES = \[\s*\{\s*me:\s*'((?:[^'\\]|\\.)*)'", read(ROOT / AK8_HERO_JS))
    return re.sub(r"\\(.)", r"\1", m.group(1)) if m else None


def _own_text(n):
    """Text eines Knotens ohne seine Kind-Elemente (Chat-Blase ohne <time>)."""
    return _norm("".join(k for k in n.kids if isinstance(k, str)))


def akh():
    errs = []
    raw = read(ROOT / "index.html")
    dom = _Dom(raw).root
    nodes = [n for n in dom.walk() if n.tag != "#root"]
    pos = {id(n): i for i, n in enumerate(nodes)}

    def q(pred, within=None):
        return [n for n in (within or dom).walk() if n.tag != "#root" and pred(n)]

    def hidden_up(n):
        return n.up(lambda x: x.has("sr-only") or x.attrs.get("aria-hidden") == "true" or "hidden" in x.attrs)

    hero = next((n for n in nodes if n.tag == "section" and n.has("hero")), None)
    if hero is None:
        return ["index.html: kein <section class=\"hero\">"]
    # Kopf: genau eine H1, Text, <em>
    h1s = q(lambda n: n.tag == "h1")
    if len(h1s) != 1:
        errs.append(f"index.html: {len(h1s)} <h1> statt genau 1")
    h1 = h1s[0] if h1s else None
    if h1 is not None:
        if h1.attrs.get("id") != "hero-h1" or not h1.has("hc-h1"):
            errs.append("index.html: H1 ohne id=\"hero-h1\" und class hc-h1")
        if h1.up(lambda n: n is hero) is None:
            errs.append("index.html: H1 steht nicht in .hero")
        if h1.text() != H1_TEXT:
            errs.append(f"index.html: H1 '{h1.text()}' statt '{H1_TEXT}'")
        ems = [e.text() for e in q(lambda n: n.tag == "em", h1)]
        if ems != [H1_EM]:
            errs.append(f"index.html: <em> in der H1 {ems} statt ['{H1_EM}']")
    # H1 -> .page-k -> .hc-schutz -> .hc-fuer, direkt hintereinander
    ks, sc = q(lambda n: n.has("page-k"), hero), q(lambda n: n.has("hc-schutz"), hero)
    fu = q(lambda n: n.has("hc-fuer"), hero)
    if len(ks) != 1 or ks[0].tag != "p" or not ks[0].has("hc-k"):
        errs.append(f"index.html: p.page-k.hc-k in .hero {len(ks)}x statt genau 1")
    elif ks[0].text() != PAGE_K_HERO:
        errs.append(f"index.html: .page-k '{ks[0].text()}' statt '{PAGE_K_HERO}'")
    if len(sc) != 1 or sc[0].tag != "p":
        errs.append(f"index.html: p.hc-schutz in .hero {len(sc)}x statt genau 1")
    elif sc[0].text() != SCHUTZSATZ:
        errs.append(f"index.html: .hc-schutz '{sc[0].text()}' statt '{SCHUTZSATZ}'")
    # Firmenkunden-Zeile: sichtbar, direkt unter dem Schutzsatz
    if len(fu) != 1 or fu[0].tag != "p":
        errs.append(f"index.html: p.hc-fuer (Firmenkunden-Zeile) in .hero {len(fu)}x statt genau 1")
    elif fu[0].text() != FIRMENKUNDEN_HERO:
        errs.append(f"index.html: .hc-fuer '{fu[0].text()}' statt '{FIRMENKUNDEN_HERO}'")
    elif hidden_up(fu[0]):
        errs.append("index.html: Firmenkunden-Zeile ist versteckt (sr-only/aria-hidden/hidden)")
    if h1 is not None and len(ks) == 1 and len(sc) == 1 and len(fu) == 1:
        sib = [k for k in h1.parent.kids if isinstance(k, _N)]
        i = next((k for k, x in enumerate(sib) if x is h1), -1)
        if not (pos[id(h1)] < pos[id(ks[0])] < pos[id(sc[0])] < pos[id(fu[0])]) or sib[i + 1:i + 4] != [ks[0], sc[0], fu[0]]:
            errs.append("index.html: Reihenfolge H1 -> .page-k -> .hc-schutz -> .hc-fuer (direkt hintereinander) verletzt")
    wer = q(lambda n: n.has("hc-wer"), hero)
    if len(wer) != 1 or wer[0].text() != HERO_WER:
        errs.append(f"index.html: .hc-wer {[w.text() for w in wer]} statt ['{HERO_WER}']")
    # A16: genau zwei Belegzeilen, keine Preise im Hero
    proof_ul = q(lambda n: n.has("hc-proof"), hero)
    proof = q(lambda n: n.tag == "li", proof_ul[0]) if proof_ul else []
    want_proof = [HERO_PROOF[0].format(n=gen().REVIEW_COUNT_GOOGLE), HERO_PROOF[1]]
    if [p.text() for p in proof] != want_proof:
        errs.append(f"index.html: Belegzeilen im Hero {[p.text() for p in proof]} statt {want_proof}")
    if not q(lambda n: n.tag == "a" and "data-proof" in n.attrs, hero):
        errs.append("index.html: Beleg mit data-proof fehlt im Hero")
    htext = hero.text()
    if "€" in htext or re.search(r"Monatspauschale|Ad hoc", htext):
        errs.append("index.html: Preiszeile im Hero (A16: Preise nur in #preise)")
    if not q(lambda n: n.tag == "a" and n.attrs.get("href", "").startswith("tel:"), hero) or not q(lambda n: n.has("hc-wa"), hero):
        errs.append("index.html: Anrufen-/WhatsApp-Knopf im Hero fehlt")

    # Chat-Handy: genau ein [data-hero-chat] auf der Seite, im Hero
    chats = q(lambda n: "data-hero-chat" in n.attrs)
    chat = chats[0] if len(chats) == 1 else None
    if chat is None or chat.up(lambda n: n is hero) is None:
        errs.append(f"index.html: [data-hero-chat] {len(chats)}x, soll genau 1 und in .hero stehen")
    if chat is not None:
        phones = q(lambda n: n.has("hc-phone"), chat)
        if len(phones) != 1 or phones[0].attrs.get("aria-hidden") != "true":
            errs.append("index.html: .hc-phone im Chat fehlt oder ohne aria-hidden=\"true\"")
        for a in q(lambda n: n.attrs.get("aria-hidden") == "true", chat):
            foc = q(lambda n: n.tag in ("a", "button", "input", "select", "textarea", "summary", "iframe") or "tabindex" in n.attrs, a)
            if foc:
                errs.append(f"index.html: {len(foc)} fokussierbare Elemente in einem aria-hidden-Bereich des Chats")
        # Erste Kundennachricht statisch im HTML (Chat nie leer beim Laden), gleich dem ersten Fall im Skript
        threads = q(lambda n: "data-hc-thread" in n.attrs, chat)
        msgs = q(lambda n: n.has("hc-msg"), threads[0]) if threads else []
        want_me = hero_chat_first_me()
        if want_me is None:
            errs.append(f"{AK8_HERO_JS}: erster Fall (CASES[0].me) nicht gefunden")
        if not msgs or not msgs[0].has("is-me"):
            errs.append("index.html: erste Chat-Nachricht (Kundenblase .hc-msg.is-me) fehlt im HTML")
        elif want_me is not None and _own_text(msgs[0]) != want_me:
            errs.append(f"index.html: erste Kundenblase '{_own_text(msgs[0])}' statt '{want_me}' (CASES[0].me)")
        # Pause-Knopf im Chat, ausserhalb des aria-hidden-Handys
        btns = q(lambda n: n.tag == "button" and "data-hc-pause" in n.attrs, chat)
        if len(btns) != 1 or btns[0].attrs.get("type") != "button" or not btns[0].has("hc-pause"):
            errs.append(f"index.html: button.hc-pause[data-hc-pause][type=button] im Chat {len(btns)}x statt genau 1")
        elif btns[0].up(lambda n: n.attrs.get("aria-hidden") == "true"):
            errs.append("index.html: Pause-Knopf steht in einem aria-hidden-Bereich")
        # Kennzeichnung sichtbar am Chat (nicht im Handy, nicht versteckt)
        kz = q(lambda n: n.tag == "p" and n.has("hc-kennz"), chat)
        if len(kz) != 1:
            errs.append(f"index.html: p.hc-kennz (Kennzeichnung) am Chat {len(kz)}x statt genau 1")
        else:
            if kz[0].text() != KENNZEICHNUNG_HERO:
                errs.append(f"index.html: Kennzeichnung '{kz[0].text()}' statt '{KENNZEICHNUNG_HERO}'")
            if hidden_up(kz[0]) or kz[0].up(lambda n: n.has("hc-phone")):
                errs.append("index.html: Kennzeichnung ist versteckt oder steht im aria-hidden-Handy, soll sichtbar am Chat stehen")
    # Kein Vergleich, kein Gegenueber
    for w in HERO_VERBOTEN:
        if w.lower() in htext.lower():
            errs.append(f"index.html: '{w}' im Hero")
    tickets = sorted(set(re.findall(r"#\d+", htext)))
    if tickets:
        errs.append(f"index.html: Ticketnummern im Hero {tickets}")
    if re.search(r"\b(?:GmbH|mbH|OHG|GbR|e\.K\.)", htext):
        errs.append("index.html: Firmenname mit Rechtsform im Hero")
    for el in q(lambda n: n.tag in ("img", "svg", "use", "div", "span") and "logo" in " ".join(str(v) for v in n.attrs.values()).lower(), hero):
        errs.append(f"index.html: Logo im Hero (<{el.tag}>), AK-R2-04")
    # Link /it-betreuer-wechseln/ direkt nach der Hero-Section (seit 18.10.2026 ohne den Kasten .hc-direkt dazwischen;
    # dass es ihn nirgends mehr gibt, prueft AKK). Sichtbarkeit: check_design.py R2-LINK.
    sib = [k for k in hero.parent.kids if isinstance(k, _N)]
    i = next((k for k, x in enumerate(sib) if x is hero), -1)
    cand = sib[i + 1] if 0 <= i < len(sib) - 1 else None
    links = q(lambda n: n.tag == "a" and n.attrs.get("href") == WECHSEL_LINK[0], cand) if cand is not None else []
    if cand is None or not cand.has("hc-weiter") or [a.text() for a in links] != [WECHSEL_LINK[1]]:
        errs.append(f"index.html: Link {WECHSEL_LINK[0]} '{WECHSEL_LINK[1]}' steht nicht direkt nach dem Hero (.hc-weiter)")

    # Abschnitt IT-Betreuung: typische Anrufe, kein zweites Chat-Handy
    itb = next((n for n in nodes if n.attrs.get("id") == "it-betreuung"), None)
    if itb is None:
        errs.append("index.html: #it-betreuung fehlt")
    else:
        if q(lambda n: "data-hero-chat" in n.attrs or n.has("hc-phone"), itb):
            errs.append("index.html: Chat-Handy steht (auch) in #it-betreuung")
        h2s = q(lambda n: n.tag == "h2", itb)
        if not h2s or h2s[0].text() != ITB_H2:
            errs.append(f"index.html: H2 von #it-betreuung '{h2s[0].text() if h2s else None}' statt '{ITB_H2}'")
        dls = q(lambda n: n.tag == "dl" and n.has("itb-list"), itb)
        if len(dls) != 1:
            errs.append(f"index.html: dl.itb-list (Typische Anrufe) in #it-betreuung {len(dls)}x statt genau 1")
        else:
            n_dt = len(q(lambda n: n.tag == "dt", dls[0]))
            if n_dt != ITB_ANRUFE:
                errs.append(f"index.html: dl.itb-list mit {n_dt} Anrufen statt {ITB_ANRUFE}")
            if "data-dominant" not in dls[0].attrs:
                errs.append("index.html: dl.itb-list ohne data-dominant (dominantes Element des Abschnitts)")
        if not q(lambda n: n.tag == "a" and n.attrs.get("href") == "/ratgeber/server-ausgefallen/", itb):
            errs.append("index.html: Link /ratgeber/server-ausgefallen/ fehlt in #it-betreuung")
    # Skript hero-chat.js: defer, ?v= = ASSET_VER, Pre-Cache, Groesse; das Skript der frueheren Buehne ist weg
    tags = re.findall(r"<script\b[^>]*\bsrc=\"[^\"]*hero-chat\.js[^\"]*\"[^>]*>", raw)
    if len(tags) != 1:
        errs.append(f"index.html: <script src=…hero-chat.js> {len(tags)}x statt genau 1")
    else:
        if not re.search(r"\bdefer\b", tags[0]):
            errs.append("index.html: hero-chat.js ohne defer")
        ver = _const(r"const ASSET_VER\s*=\s*'([^']+)'", read(ROOT / "sw.js"))
        if f"hero-chat.js?v={ver}" not in tags[0]:
            errs.append(f"index.html: hero-chat.js ohne ?v={ver} (ASSET_VER aus sw.js)")
    pre = precache_urls() or []
    if not any("hero-chat.js" in u for u in pre):
        errs.append("sw.js: hero-chat.js fehlt im Pre-Cache (PRECACHE_URLS)")
    js_path = ROOT / AK8_HERO_JS
    if not js_path.is_file():
        errs.append(f"{AK8_HERO_JS} fehlt")
    elif len(gzip.compress(js_path.read_bytes(), 9)) > HERO_CHAT_JS_MAX_GZIP:
        errs.append(f"{AK8_HERO_JS} groesser als {HERO_CHAT_JS_MAX_GZIP // 1024} KB gzip")
    alt = ENTFALLEN_JS.rsplit("/", 1)[1]
    if alt in raw or any(alt in u for u in pre) or (ROOT / ENTFALLEN_JS).exists():
        errs.append(f"{ENTFALLEN_JS}: Skript der frueheren Hero-Buehne steht noch in index.html, im Pre-Cache oder im Repo")
    return errs


# ----------------------------------------------------------------------------------------------------------------------
# AKK (Stand 18.10.2026, Release 2.1.1): Kontakt-Reihenfolge ueberall WhatsApp - Telefon - E-Mail. Je Kontaktgruppe
# (Kopfzeile, Mobilmenue, Seitenkopf, Abschluss, Preise, Schnellcheck, Fernwartungshilfe, Kontaktseite, Fuss, Dock)
# stehen die Links in dieser Reihenfolge; steht WhatsApp in der Gruppe, ist der Telefon-Link kein Hauptknopf (.btn-p,
# volle #0000FE-Flaeche). Ratgeber-Kopf mit nur dem Anruf-Knopf bleibt erlaubt. Kein .hc-direkt mehr.
# Farben und Hauptaktion im gerenderten Zustand: check_design.py AK-R1-03.
# ----------------------------------------------------------------------------------------------------------------------
AKK_GROUPS = ("nav-links", "mobile-menu", "hc-ctas", "cta-btns", "pkg-btns", "sc-cta-row", "fw-help-actions", "k-ways",
              "foot-contact", "sticky-contact")
AKK_RANK = {"wa": 0, "tel": 1, "mail": 2}


def _kind(a):
    h = a.attrs.get("href", "")
    return "wa" if "wa.me/" in h else "tel" if h.startswith("tel:") else "mail" if h.startswith("mailto:") else None


def akk():
    errs = []
    for p in pages():
        dom = _Dom(read(p)).root
        if any(n.has("hc-direkt") for n in dom.walk()):
            errs.append(f"{rel(p)}: .hc-direkt vorhanden (Kasten nach dem Hero ist seit 18.10.2026 entfernt)")
        for g in (n for n in dom.walk() if n.tag != "#root" and any(n.has(c) for c in AKK_GROUPS)):
            links = [(a, _kind(a)) for a in g.walk() if a.tag == "a" and _kind(a)]
            order = [k for _a, k in links]
            if order != sorted(order, key=AKK_RANK.get):
                name = next(c for c in AKK_GROUPS if g.has(c))
                errs.append(f"{rel(p)}: .{name} Reihenfolge {order} statt WhatsApp - Telefon - E-Mail")
            if "wa" in order:
                for a, k in links:
                    if k == "tel" and a.has("btn-p"):
                        errs.append(f"{rel(p)}: Telefon neben WhatsApp als Hauptknopf (.btn-p) in "
                                    f"{(g.attrs.get('class') or '').split()[0]}")
    return errs


# ----------------------------------------------------------------------------------------------------------------------
# AKF (Stand 18.10.2026, Release 2.1.1): Film auf der Startseite. Statisch geprueft: Abschnitt #film mit Titel und
# Zusatz, Fassade (Link mit Posterbild, Name „Film abspielen, 1:31“, ohne JS auf die 720p-Datei), kein <video>, <source>,
# <track> oder <iframe> im HTML und nirgends autoplay, KI-Hinweis in derselben <figure> direkt nach dem Player, die
# Dateien hinter den data-Attributen existieren, main.js setzt die Untertitelspur (subtitles, de, default), VideoObject
# mit Pflichtfeldern und absoluten non-www-URLs auf vorhandene Dateien, sw.js laesst Filmdateien aus dem Pre-Cache und
# reicht .mp4/.vtt durch, Textlink „Film ansehen (1:31)“ in der Zeile nach dem Hero. Im Browser (Netzwerk vor dem Klick,
# Spur und Fokus nach dem Klick, Sichtbarkeit des Hinweises): check_design.py R2-FILM.
# ----------------------------------------------------------------------------------------------------------------------
FILM_TITLE = "Lieber schauen statt lesen?"
FILM_META = "1:31 · mit Untertiteln"
FILM_KI = "Sprecherstimme und Illustrationen mit KI erstellt. Inhalte von Andreas Grundke geprüft."
FILM_LABEL = "Film abspielen, 1:31"
FILM_LINK = ("#film", "Film ansehen (1:31)")
FILM_FILES = {"film-sd": "/assets/video/werbefilm_v2.1_2026-10-18_720p.mp4",
              "film-hd": "/assets/video/werbefilm_v2.1_2026-10-18_1080p.mp4",
              "film-vtt": "/assets/video/werbefilm_v2.1.de.vtt"}
FILM_POSTER = "/assets/video/werbefilm_v2.1_vorschau.webp"
FILM_VIDEO_LD = {"name": str, "description": str, "thumbnailUrl": FILM_POSTER, "uploadDate": "2026-10-18",
                 "duration": "PT1M31S", "contentUrl": FILM_FILES["film-hd"], "inLanguage": "de"}


def akf():
    errs, src = [], read(ROOT / "index.html")
    dom = _Dom(src).root
    nodes = list(dom.walk())
    for tag in ("video", "source", "track", "iframe"):
        # <source> in <picture> (Logo) ist ein Bild, kein Film
        if any(n.tag == tag and not (tag == "source" and n.parent.tag == "picture") for n in nodes):
            errs.append(f"index.html: <{tag}> im HTML (Film nur als Fassade, das Video setzt main.js beim Klick)")
    if re.search(r"\bautoplay\b", src, re.I) or re.search(r"\bautoplay\b", read(ROOT / "assets/js/main.js"), re.I):
        errs.append("index.html/main.js: 'autoplay' gefunden (Start nur durch Klick)")
    sec = next((n for n in nodes if n.attrs.get("id") == "film"), None)
    if sec is None:
        return errs + ["index.html: Abschnitt #film fehlt"]
    h2 = next((n for n in sec.walk() if n.tag == "h2"), None)
    if h2 is None or h2.text() != FILM_TITLE:
        errs.append(f"#film: H2 '{h2.text() if h2 else None}' statt '{FILM_TITLE}'")
    meta = next((n for n in sec.walk() if n.has("film-meta")), None)
    if meta is None or meta.text() != FILM_META:
        errs.append(f"#film: Zusatz '{meta.text() if meta else None}' statt '{FILM_META}'")
    box = next((n for n in sec.walk() if "data-film" in n.attrs), None)
    if box is None:
        return errs + ["#film: [data-film] fehlt"]
    for key, want in FILM_FILES.items():
        got = box.attrs.get("data-" + key)
        if got != want:
            errs.append(f"#film: data-{key} '{got}' statt '{want}'")
        elif not (ROOT / want.lstrip("/")).is_file():
            errs.append(f"#film: Datei {want} fehlt im Repo")
    a = next((n for n in box.walk() if n.tag == "a" and n.has("film-start")), None)
    if a is None:
        errs.append("#film: Fassade a.film-start fehlt")
    else:
        if a.attrs.get("href") != FILM_FILES["film-sd"]:
            errs.append(f"#film: Fassade ohne JS verlinkt '{a.attrs.get('href')}' statt der 720p-Datei")
        if a.attrs.get("aria-label") != FILM_LABEL:
            errs.append(f"#film: Name der Fassade '{a.attrs.get('aria-label')}' statt '{FILM_LABEL}'")
        img = next((n for n in a.walk() if n.tag == "img"), None)
        if img is None or img.attrs.get("src") != FILM_POSTER or img.attrs.get("loading") != "lazy" \
                or not img.attrs.get("width") or not img.attrs.get("height"):
            errs.append("#film: Posterbild fehlt oder ohne loading=lazy/width/height")
        elif not (ROOT / FILM_POSTER.lstrip("/")).is_file():
            errs.append(f"#film: Posterbild {FILM_POSTER} fehlt im Repo")
    fig = box.up(lambda n: n.tag == "figure")
    cap = [k for k in (fig.kids if fig else []) if isinstance(k, _N)]
    i = cap.index(box) if box in cap else -1
    if fig is None or i < 0 or i + 1 >= len(cap) or cap[i + 1].tag != "figcaption" or cap[i + 1].text() != FILM_KI:
        errs.append(f"#film: KI-Hinweis '{FILM_KI}' steht nicht als <figcaption> direkt nach dem Player")
    js = read(ROOT / "assets/js/main.js")
    for need in ("t.kind = 'subtitles'", "t.srclang = 'de'", "t.default = true", "v.preload = 'none'",
                 "v.controls = true", "playsinline", "v.focus()", "matchMedia('(min-width: 1024px)')"):
        if need not in js:
            errs.append(f"main.js: initFilm ohne {need!r}")
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)]
    vids = [b for b in blocks if isinstance(b, dict) and b.get("@type") == "VideoObject"]
    if len(vids) != 1:
        errs.append(f"index.html: {len(vids)} VideoObject statt 1")
    for v in vids:
        for k, want in FILM_VIDEO_LD.items():
            got = v.get(k)
            if want is str:
                if not isinstance(got, str) or not got.strip():
                    errs.append(f"VideoObject: {k} fehlt")
            elif k in ("thumbnailUrl", "contentUrl"):
                if got != "https://grundke-it.de" + want:
                    errs.append(f"VideoObject: {k} '{got}' statt 'https://grundke-it.de{want}'")
            elif got != want:
                errs.append(f"VideoObject: {k} '{got}' statt '{want}'")
    sw = read(ROOT / "sw.js")
    if any("/assets/video/" in u or re.search(r"\.(mp4|webm|vtt)$", u.split("?")[0]) for u in (precache_urls() or [])):
        errs.append("sw.js: Filmdatei im Pre-Cache")
    if "req.headers.has('range')" not in sw or "mp4|webm|m4v|vtt" not in sw:
        errs.append("sw.js: Durchreichen von Range-Anfragen bzw. .mp4/.vtt fehlt")
    weiter = next((n for n in nodes if n.has("hc-weiter")), None)
    links = [(x.attrs.get("href"), x.text()) for x in (weiter.walk() if weiter else []) if x.tag == "a"]
    if FILM_LINK not in links:
        errs.append(f"index.html: Textlink {FILM_LINK} fehlt in .hc-weiter (gefunden {links})")
    return errs


def write_legal_baseline():
    out = {}
    for p in legal_pages():
        out[rel(p)] = hashlib.sha256(legal_text(read(p)).encode()).hexdigest()
    (INTERN / "vorher").mkdir(parents=True, exist_ok=True)
    (INTERN / "vorher" / "legal_hash.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


# Name -> (Pruefung, braucht). braucht: "intern" = ../_intern/ (ausserhalb des Repos), "git" = Historie oder
# origin/main. --ci laesst alles mit einer solchen Abhaengigkeit sichtbar aus (Deploy-Workflow, Fix-Runde B M16).
CHECKS = {
    "AK1": (ak1, ()), "AK2": (ak2, ()), "AK2b": (ak2b, ()), "AK7": (ak7, ()), "AK8": (ak8, ()), "AK9": (ak9, ()),
    "AK9b": (ak9b, ()), "AK11a": (ak11a, ()), "AK13": (ak13, ()), "AK13v": (ak13v, ("git",)), "AK14": (ak14, ()),
    "AK14r": (ak14r, ("intern", "git")), "AK13s": (ak13s, ()), "AKH": (akh, ()), "AKK": (akk, ()),
    "AKF": (akf, ()),
}

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--legal-baseline" in sys.argv:
        write_legal_baseline(); sys.exit(0)
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else list(CHECKS)
    unknown = [k for k in only if k not in CHECKS]
    if unknown:
        print(f"Unbekannte Pruefung(en): {', '.join(unknown)}; vorhanden: {', '.join(CHECKS)}"); sys.exit(2)
    skipped = [k for k in only if "--ci" in sys.argv and CHECKS[k][1]]
    bad = 0
    for k in only:
        if k in skipped:
            continue
        errs = CHECKS[k][0]()
        print(f"{k}: {'OK' if not errs else 'FEHLER (' + str(len(errs)) + ')'}")
        for e in errs[:40]:
            print("   ", e)
        bad += len(errs)
    if skipped:
        print(f"uebersprungen (--ci, braucht ../_intern/ oder Git-Historie): {', '.join(skipped)}")
    for w in WARNINGS:
        print("WARNUNG", w)
    sys.exit(1 if bad else 0)
