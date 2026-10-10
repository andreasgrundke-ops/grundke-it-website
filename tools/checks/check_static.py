"""Statische Pruefungen (Spec §9: AK1, AK2, AK7, AK8, AK9, AK13, AK14).
Aufruf: python tools/checks/check_static.py [--only AK1,AK9]   Exit 1 bei Fehler."""
import hashlib, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTERN = ROOT.parent / "_intern" / "messungen"
SKIP = ("tree", "ki-arbeitsplatz-onboarding-kit", "Audit 2026-04", "assets", "tools", ".impeccable", ".playwright-mcp", ".github")
LEGAL = ("impressum", "datenschutz", "agb", "barrierefreiheit")
FORBIDDEN_SELECTORS = [".btn-p", ".btn-g", ".btn-wa", ".btn-email", ".btn-tel", ".price-card", ".price-btn", ".faq-item",
                       ".cta-sec", ".lp-btn", ".lp-price", ".lp-card", ".emp-link", ".emp-card", ".k-card", ".sch-card",
                       ".topic", ".ki-case", ".ki-check", ".ki-note", ".lp-voice", ".testi-card", ".card"]
OLD_WRAPPERS = ("lp-wrap", "page-wrap", "kontakt-wrap", "fw-wrap", "emp-hero", "err-wrap")
PROMISES = ["sofort", "immer erreichbar", "ich geh ran", "rund um die uhr", "24/7", "garantiert", "am selben tag",
            "in minuten", "heute noch", "schnell", "zurückruft", "umgehend", "kurzfristig", "bleib dran",
            "erreichbar, wenn", "erreichbar, wann"]
NEW_BLOCKS = r'class="[^"]*\b(page-k|mini-chat|cta-sec|k3-block|cta-h|cta-sub)\b'
PROTECTED = ["Angebot ausschließlich für Unternehmen", "ohne garantierte Reaktionszeit", "Warum ein Paket?"]


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


def ak1():
    errs = []
    for p in pages():
        if rel(p) == "index.html":
            continue
        css = styles(read(p))
        for sel in FORBIDDEN_SELECTORS:
            if re.search(re.escape(sel) + r"(?![\w-])", css):
                errs.append(f"{rel(p)}: eigener Stil fuer {sel}")
    return errs


def ak2():
    return [f"{rel(p)}: alte Huelle {w}" for p in pages() for w in OLD_WRAPPERS
            if re.search(r'class="[^"]*\b' + w + r'\b', read(p))]


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
    Text woertlich und ungekuerzt in <blockquote class="testi-txt">. Startseite zusaetzlich: jede Stimme
    genau einmal, review[]/reviewBody im Schema = REVIEWS, reviewCount = len(REVIEWS), Belegzeile
    [data-proof] nennt REVIEW_COUNT_GOOGLE."""
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import build_landingpages as gen
        reviews, n_google = gen.REVIEWS, gen.REVIEW_COUNT_GOOGLE
    except (ImportError, AttributeError) as e:
        return [f"Generator ohne REVIEWS/REVIEW_COUNT_GOOGLE: {e}"]
    by_name = {r["name"]: r for r in reviews}
    errs = []
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
        if rel(p) != "index.html":
            continue
        if sorted(seen) != sorted(by_name):
            errs.append(f"index.html: Stimmen sichtbar {sorted(seen)} != REVIEWS {sorted(by_name)}")
        nodes = schema_nodes(s)
        sch = [(x["author"]["name"], x["reviewBody"]) for x in nodes if x.get("@type") == "Review"]
        want = [(r["name"], "\n\n".join(r["paragraphs"])) for r in reviews]
        if sorted(sch) != sorted(want):
            errs.append("index.html: review[]/reviewBody im Schema != REVIEWS")
        counts = [x.get("reviewCount") for x in nodes if x.get("@type") == "AggregateRating"]
        if counts != [str(len(reviews))]:
            errs.append(f"index.html: reviewCount {counts} != {len(reviews)}")
        proof = re.search(r"bei (\d+) Google-Bewertungen", text_of(first(r"(<a[^>]*\bdata-proof\b.*?</a>)", s)))
        if not proof or int(proof.group(1)) != n_google:
            errs.append(f"index.html: Belegzeile [data-proof] nennt nicht {n_google} Google-Bewertungen")
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
