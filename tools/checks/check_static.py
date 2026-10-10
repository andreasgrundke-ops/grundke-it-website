"""Statische Pruefungen (Spec §9: AK1, AK2, AK2b, AK7, AK8, AK9, AK9b, AK11a, AK13, AK14).
Aufruf: python tools/checks/check_static.py [--only AK1,AK9]   Exit 1 bei Fehler."""
import hashlib, html, json, re, sys
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
PROMISES = ["sofort", "immer erreichbar", "ich geh ran", "rund um die uhr", "24/7", "garantiert", "am selben tag",
            "in minuten", "heute noch", "schnell", "zurückruft", "umgehend", "kurzfristig", "bleib dran",
            "erreichbar, wenn", "erreichbar, wann"]
NEW_BLOCKS = r'class="[^"]*\b(page-k|mini-chat|cta-sec|k3-block|cta-h|cta-sub)\b'
PROTECTED = ["Angebot ausschließlich für Unternehmen", "ohne garantierte Reaktionszeit", "Warum ein Paket?"]
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
    nav.lp-paths im Kopf und die Akzentzeile als <em> in der H1. Ratgeber (kind "hub"/"ratgeber") ohne
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
        if d.get("kind") in ("hub", "ratgeber"):
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


def ak8():
    """Nur neue Bausteine pruefen; Zitate, Ratgeber, Rechtstexte, Leitzeile sind ausgenommen."""
    errs = []
    for p in pages():
        s = read(p)
        for m in re.finditer(NEW_BLOCKS + r'[^"]*"[^>]*>(.*?)</(p|div|section|ol)>', s, re.S):
            low = text_of(m.group(0)).lower().replace("dein itler geht nicht ran? ich schon.", "")
            for w in PROMISES:
                if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
                    errs.append(f"{rel(p)}: Zusage-Wort '{w}' in neuem Baustein")
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
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import build_landingpages as gen
        reviews, n_google = gen.REVIEWS, gen.REVIEW_COUNT_GOOGLE
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


def ak14():
    errs = []
    home = text_of(read(ROOT / "index.html"))
    for t in PROTECTED:
        if t not in home:
            errs.append(f"index.html: geschuetzter Satz fehlt: {t}")
    if 'id="bewertungen-herkunft"' not in read(ROOT / "index.html"):
        errs.append("index.html: #bewertungen-herkunft fehlt")
    base = INTERN / "vorher" / "legal_hash.json"
    if base.exists():
        old = json.loads(base.read_text(encoding="utf-8"))
        for p in legal_pages():
            h = hashlib.sha256(legal_text(read(p)).encode()).hexdigest()
            if old.get(rel(p)) != h:
                errs.append(f"{rel(p)}: Rechtstext geaendert")
    fw = read(ROOT / "fernwartung/index.html")
    for need in ("https://msp.grundke-it.de/dist/grundke-support.exe", "https://msp.grundke-it.de/dist/grundke-support-linux-amd64"):
        if need not in fw:
            errs.append(f"fernwartung: Download fehlt {need}")
    return errs


def ak13():
    errs = []
    for p in pages():
        for ref in re.findall(r'href="([^"]*style\.css[^"]*)"|src="([^"]*main\.js[^"]*)"', read(p)):
            r = ref[0] or ref[1]
            if "?v=" not in r:
                errs.append(f"{rel(p)}: {r} ohne Version")
    # Pre-Cache des Service Workers muss dieselbe Version tragen wie die Seiten
    vers = {v for p in pages() for v in re.findall(r'(?:style\.css|main\.js)\?v=([\w.-]+)"', read(p))}
    sw = re.search(r"const ASSET_VER\s*=\s*'([^']+)'", read(ROOT / "sw.js"))
    if not sw or vers != {sw.group(1)}:
        errs.append(f"sw.js: ASSET_VER {sw.group(1) if sw else 'fehlt'} passt nicht zu den Seiten {sorted(vers)}")
    return errs


def write_legal_baseline():
    out = {}
    for p in legal_pages():
        out[rel(p)] = hashlib.sha256(legal_text(read(p)).encode()).hexdigest()
    (INTERN / "vorher").mkdir(parents=True, exist_ok=True)
    (INTERN / "vorher" / "legal_hash.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


CHECKS = {"AK1": ak1, "AK2": ak2, "AK7": ak7, "AK8": ak8, "AK9": ak9, "AK14": ak14}
CHECKS["AK13"] = ak13
CHECKS["AK9b"] = ak9b
CHECKS["AK11a"] = ak11a
CHECKS["AK2b"] = ak2b

if __name__ == "__main__":
    if "--legal-baseline" in sys.argv:
        write_legal_baseline(); sys.exit(0)
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else list(CHECKS)
    bad = 0
    for k in only:
        errs = CHECKS[k]()
        print(f"{k}: {'OK' if not errs else 'FEHLER (' + str(len(errs)) + ')'}")
        for e in errs[:40]:
            print("   ", e)
        bad += len(errs)
    sys.exit(1 if bad else 0)
