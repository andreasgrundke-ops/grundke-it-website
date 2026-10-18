"""Design-Pruefungen fuer den Relaunch (Spec §5, §7, §11).
Titel:        check_design.py
Version:      0.3.0 (Task 1: AK-R1-Pruefungen, --release r1; Task 11: AK-R2-Pruefungen, --release r2)
Datum:        17.10.2026
Beschreibung: Misst Hoehen bei 390x844 (reduzierte Bewegung, Service Worker blockiert) und vergleicht sie
              mit einer gespeicherten Baseline. Dazu die Abnahmekriterien AK-R1-01a ... AK-R1-23 des Relaunchs R1
              (Spec §5, §11) als Funktionen ak_r1_*(), je Rueckgabe list[str] (leer = erfuellt).
Aufruf:       PY313 tools/checks/check_design.py --measure-baseline DIR
              PY313 tools/checks/check_design.py --heights --baseline DIR
              PY313 tools/checks/check_design.py --release r1 [--baseline DIR] [--only R1-01a,R1-08]
              PY313 tools/checks/check_design.py --release r2 --baseline DIR [--only R2-06,R2-09]
Ablauf:       1. serve.py startet den lokalen Static-Server (127.0.0.1, freier Port).
              2. Fuer jede Seite aus check_static.pages() bei 390x844 messen.
              3. --measure-baseline: DIR/hoehen.json schreiben.
              4. --heights: je Seite gegen DIR/hoehen.json vergleichen, Abweichung in px und %;
                 ueber +5 % WARNUNG, ueber Budget FEHLER; Exit 1 nur bei Fehlern."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
import serve
from check_static import pages, legal_pages, rel

VIEW = {"width": 390, "height": 844}
LIMIT_HOME, LIMIT_SUB = 12000, 8000
LIMIT_SCHNELLCHECK, LIMIT_PREISE = 4000, 5000
WARN_GROWTH = 0.05          # ueber +5 % gegen die Baseline: Warnung
WARN_SHARE = 0.95           # ab 95 % eines Budgets: Warnung (wie check_site.py)

MEASURE = """() => {
  const h = sel => { const e = document.querySelector(sel); return e ? Math.round(e.getBoundingClientRect().height) : null; };
  const top = id => { const e = document.getElementById(id); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null; };
  return { total: document.documentElement.scrollHeight, hero: h('.hero'), itb: h('#it-betreuung'),
           schnellcheck_top: top('schnellcheck'), preise_top: top('preise') };
}"""


def url_of(p):
    r = rel(p)
    return "/" if r == "index.html" else "/" + r.replace("index.html", "")


def measure_all(only=None):
    """Messung aller Seiten bei 390x844. Rueckgabe: {url: {total, hero, itb, schnellcheck_top, preise_top}}."""
    srv, base = serve.start()
    out = {}
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for p in pages():
                u = url_of(p)
                if only and u not in only:
                    continue
                ctx = b.new_context(viewport=VIEW, service_workers="block", reduced_motion="reduce")
                pg = ctx.new_page()
                pg.goto(base + u, wait_until="networkidle")
                out[u] = pg.evaluate(MEASURE)
                ctx.close()
            b.close()
    finally:
        srv.shutdown()
    return out


def baseline_doc(m):
    home = m["/"]
    return {"hero_390": home["hero"], "itb_390": home["itb"], "schnellcheck_top_390": home["schnellcheck_top"],
            "preise_top_390": home["preise_top"], "home_390": home["total"],
            "seiten_390": {u: v["total"] for u, v in m.items()}}


def measure_baseline(dir_):
    d = Path(dir_); d.mkdir(parents=True, exist_ok=True)
    doc = baseline_doc(measure_all())
    (d / "hoehen.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(doc['seiten_390'])} Seiten gemessen -> {d / 'hoehen.json'}")
    for k in ("hero_390", "itb_390", "schnellcheck_top_390", "preise_top_390", "home_390"):
        print(f"  {k}: {doc[k]}")
    return 0


def heights(dir_):
    base = json.loads((Path(dir_) / "hoehen.json").read_text(encoding="utf-8"))
    m = measure_all()
    legal = {url_of(p) for p in legal_pages()}
    fails, warns = [], []
    for u, v in sorted(m.items()):
        old = base["seiten_390"].get(u)
        now = v["total"]
        if old is None:
            warns.append(f"{u}: keine Baseline (neu), Hoehe {now}")
            continue
        diff = now - old
        pct = diff / old if old else 0
        print(f"{u}: {old} -> {now} ({diff:+d} px, {pct:+.1%})")
        if pct > WARN_GROWTH:
            warns.append(f"{u}: {diff:+d} px ({pct:+.1%}) gegen Baseline, Begruendung im Abnahmebericht")
        if u in legal or u == "/404.html":
            continue
        lim = LIMIT_HOME if u == "/" else LIMIT_SUB
        if now > lim:
            fails.append(f"{u}: Hoehe {now} > Budget {lim}")
        elif now >= WARN_SHARE * lim:
            warns.append(f"{u}: Hoehe {now} von {lim} ({now / lim:.1%})")
    home = m.get("/")
    if home:
        for key, lim, name in (("schnellcheck_top", LIMIT_SCHNELLCHECK, "#schnellcheck"), ("preise_top", LIMIT_PREISE, "#preise")):
            if home[key] is None or home[key] > lim:
                fails.append(f"/: {name} {home[key]} > {lim}")
        for key, bkey, name in (("hero", "hero_390", ".hero"), ("itb", "itb_390", "#it-betreuung")):
            if home[key] is not None and base.get(bkey) is not None and home[key] > base[bkey]:
                fails.append(f"/: {name} {home[key]} > Baseline {base[bkey]}")
    for f in fails:
        print("FEHLER", f)
    for w in warns:
        print("WARNUNG", w)
    print(f"{len(m)} Seiten, {len(fails)} Fehler, {len(warns)} Warnungen")
    return 1 if fails else 0

# ----------------------------------------------------------------------------------------------------------------------
# Task 1: Abnahmekriterien R1 (Spec §5, §11). Jede Funktion liefert list[str] (leer = erfuellt). Fehlt ein Element,
# das die Spec verlangt, ist das ein Fehler, nie ein Ueberspringen.
# ----------------------------------------------------------------------------------------------------------------------
from check_static import ROOT, read, gen, deployable

CYAN_ALLOW = ["h1 em", ".cta-h em", ".is-ag", ".hc-sys", ".hc-bar", ".zw-lane--rechts", "main p a", "main li a", ".faq-a a",
              "[aria-current]", ":focus-visible"]
# Spec §5.6: Abschnitt -> (Selektor des Abschnitts). R1 prueft bei .hero und #it-betreuung nur die Anzahl.
DOMINANT_SECTIONS = [".hero", "#it-betreuung", "#referenzen", "#praxis", "#schnellcheck", "#preise", "#ki",
                     "#einsatzgebiet"]
DOMINANT_COUNT_ONLY_R1 = [".hero", "#it-betreuung"]
NAMEN_OHNE_EINWILLIGUNG = ROOT.parent / "_intern" / "pruefdaten" / "namen-ohne-einwilligung.txt"
DOCK_H, DOCK_GAP = 52, 12
SAFE = "env(safe-area-inset-bottom)"
CHAT_EXCLUDE = ".hc-stage, [data-hero-chat] .hc-device"      # Chat-Handy: von 62ch- und Schriftgroessen-Pruefung ausgenommen
RADIUS_ROUND_OK = ".ava, .hc-ava, .hc-pause, .zw-pause"      # 50 % / 999 px nur hier (und Punkte bis 12 px)

_ENV = {}


def _env():
    """Server, Playwright und Chromium einmal je Lauf starten (Service Worker blockiert, reduzierte Bewegung)."""
    if not _ENV:
        srv, base = serve.start()
        pw = sync_playwright().start()
        _ENV.update(srv=srv, base=base, pw=pw, b=pw.chromium.launch())
    return _ENV


def close_env():
    if _ENV:
        _ENV["b"].close(); _ENV["pw"].stop(); _ENV["srv"].shutdown(); _ENV.clear()


def all_urls():
    return [url_of(p) for p in pages()]


def scan(vw, vh, js, urls=None, arg=None):
    """JS (Funktion) in jeder Seite bei vw x vh auswerten. Rueckgabe {url: Ergebnis}."""
    env = _env()
    ctx = env["b"].new_context(viewport={"width": vw, "height": vh}, service_workers="block", reduced_motion="reduce")
    out = {}
    try:
        for u in (urls or all_urls()):
            pg = ctx.new_page()
            pg.goto(env["base"] + u, wait_until="networkidle")
            out[u] = pg.evaluate(js, arg) if arg is not None else pg.evaluate(js)
            pg.close()
    finally:
        ctx.close()
    return out


def agg(msgs_by_url, limit=6):
    """{url: [Meldung]} -> je gleicher Meldung eine Zeile mit Seitenzahl (kurz statt 30 Wiederholungen)."""
    groups = {}
    for u, ms in msgs_by_url.items():
        for m in ms:
            groups.setdefault(m, []).append(u)
    out = []
    for m, us in groups.items():
        out.append(m if us == ["/"] else f"{m} [{len(us)} Seiten, z. B. {', '.join(us[:limit])}]")
    return out


def rgba(s):
    m = re.match(r"rgba?\(\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\s*\)", s or "")
    if not m:
        return None
    return float(m[1]), float(m[2]), float(m[3]), float(m[4]) if m[4] is not None else 1.0


def lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def css_rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [(m.group(1).strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]


def decls(body, prop):
    return [m.group(1).strip() for m in re.finditer(r"(?:^|[;\s])" + re.escape(prop) + r"\s*:\s*([^;]+)", body)]


def style_css():
    return read(ROOT / "assets" / "css" / "style.css")


DOCK_JS = """() => { const d = document.querySelector('.sticky-contact'); if (!d) return null;
  const r = d.getBoundingClientRect();
  return { display: getComputedStyle(d).display, left: r.left, right: innerWidth - r.right, bottom: innerHeight - r.bottom,
    width: r.width, top: r.top, btns: [...d.querySelectorAll('.sc-btn')].map(b => b.getBoundingClientRect().height) }; }"""


def _dock_pages(res, errs_home):
    """Seiten mit Dock aus einem scan()-Ergebnis; die Startseite muss ihn haben."""
    if res.get("/") is None:
        errs_home.append("/: kein .sticky-contact (Dock fehlt)")
    return {u: d for u, d in res.items() if d is not None}


def ak_r1_01a_dock_narrow():
    """AK-R1-01a: 390x844, Knopfhoehe 52 +- 1, links/rechts/unten je 12 +- 1."""
    errs = []
    res = scan(390, 844, DOCK_JS)
    per = {}
    for u, d in _dock_pages(res, errs).items():
        m = []
        if d["display"] == "none":
            m.append("Dock display:none bei 390 (soll sichtbar sein)")
        else:
            if not d["btns"] or len(d["btns"]) < 3:
                m.append(f"weniger als 3 .sc-btn ({len(d['btns'])})")
            if any(abs(h - DOCK_H) > 1 for h in d["btns"]):
                m.append(f"Knopfhoehe {[round(h, 1) for h in d['btns']]} statt {DOCK_H} +- 1")
            for k, name in (("left", "links"), ("right", "rechts"), ("bottom", "unten")):
                if abs(d[k] - DOCK_GAP) > 1:
                    m.append(f"Abstand {name} {d[k]:.1f} px statt {DOCK_GAP} +- 1")
        if m:
            per[u] = m
    return errs + agg(per)


def ak_r1_01b_dock_wide():
    """AK-R1-01b: 768x1024, 1024x768, 1279x800 Dock 52 hoch, <= 480 breit, mittig, unten 12; bei 1440 display:none."""
    errs, per = [], {}
    for vw, vh in ((768, 1024), (1024, 768), (1279, 800)):
        res = scan(vw, vh, DOCK_JS)
        for u, d in _dock_pages(res, errs).items():
            m = []
            if d["display"] == "none":
                m.append(f"{vw}: Dock display:none (soll sichtbar sein)")
            else:
                if not d["btns"] or any(abs(h - DOCK_H) > 1 for h in d["btns"]):
                    m.append(f"{vw}: Knopfhoehe {[round(h, 1) for h in d['btns']]} statt {DOCK_H} +- 1")
                if d["width"] > 480.5:
                    m.append(f"{vw}: Breite {d['width']:.0f} px > 480")
                if abs(d["left"] - d["right"]) > 1:
                    m.append(f"{vw}: nicht mittig (links {d['left']:.1f}, rechts {d['right']:.1f})")
                if abs(d["bottom"] - DOCK_GAP) > 1:
                    m.append(f"{vw}: Abstand unten {d['bottom']:.1f} px statt {DOCK_GAP} +- 1")
            if m:
                per.setdefault(u, []).extend(m)
    res = scan(1440, 900, DOCK_JS)
    for u, d in _dock_pages(res, errs).items():
        if d["display"] != "none":
            per.setdefault(u, []).append(f"1440: Dock display:{d['display']} (soll none sein)")
    return errs + agg(per)


def ak_r1_01c_safe_area():
    """AK-R1-01c: env(safe-area-inset-bottom) in Dock-bottom, body.has-sticky-call padding-bottom,
    html scroll-padding-bottom (Grep style.css); bei 390 liegt der letzte Fuss-Link nach Scroll ans Ende ueber dem Dock."""
    errs, rules = [], css_rules(style_css())

    def sel_has(sel, pat):
        return any(s.strip() == pat for s in sel.split(","))

    bottoms = [v for sel, b in rules if sel_has(sel, ".sticky-contact") for v in decls(b, "bottom")]
    if not bottoms:
        errs.append("style.css: .sticky-contact hat kein 'bottom'")
    for v in bottoms:
        if SAFE not in v:
            errs.append(f"style.css: .sticky-contact bottom: {v} ohne {SAFE}")
    pads = [v for sel, b in rules if sel_has(sel, "body.has-sticky-call") for v in decls(b, "padding-bottom")]
    if not pads or not all(SAFE in v for v in pads):
        errs.append(f"style.css: body.has-sticky-call padding-bottom {pads or 'fehlt'} ohne {SAFE}")
    sps = [v for sel, b in rules if sel_has(sel, "html") for v in decls(b, "scroll-padding-bottom")]
    if not sps or not all(SAFE in v for v in sps):
        errs.append(f"style.css: html scroll-padding-bottom {sps or 'fehlt'} ohne {SAFE}")
    js = """() => { const d = document.querySelector('.sticky-contact'); if (!d) return null;
      scrollTo(0, document.documentElement.scrollHeight);
      const links = [...document.querySelectorAll('footer.site-footer a')].filter(a => a.getBoundingClientRect().height > 0);
      if (!links.length) return {nolink: true};
      const l = links[links.length - 1].getBoundingClientRect(), t = d.getBoundingClientRect().top;
      return { bottom: l.bottom, top: t, text: links[links.length - 1].textContent.trim().slice(0, 30) }; }"""
    per = {}
    for u, r in scan(390, 844, js).items():
        if r is None:
            continue
        if r.get("nolink"):
            per[u] = ["kein sichtbarer Fuss-Link"]
        elif r["bottom"] > r["top"] + 0.5:
            per[u] = [f"letzter Fuss-Link '{r['text']}' endet bei {r['bottom']:.0f} px, Dock beginnt bei {r['top']:.0f} px"]
    return errs + agg(per)


def ak_r1_02_dock_colors():
    """AK-R1-02: Anrufen #0000FE/weiss, WhatsApp-Alpha <= 0,3, E-Mail transparent, kein background-image,
    ::before/::after ohne Inhalt, kein #b45309/#92400e/shimmer in style.css; Flaeche #141a26, Radius 16 px."""
    errs = []
    css = style_css()
    for pat in ("#b45309", "#92400e", "shimmer"):
        n = len(re.findall(pat, css, re.I))
        if n:
            errs.append(f"style.css enthaelt '{pat}' ({n}x)")
    js = """() => { const d = document.querySelector('.sticky-contact'); if (!d) return null;
      const pe = (e, p) => { const c = getComputedStyle(e, p); return { content: c.content, img: c.backgroundImage }; };
      const pick = sel => { const e = d.querySelector(sel); if (!e) return null; const c = getComputedStyle(e);
        return { bg: c.backgroundColor, color: c.color, img: c.backgroundImage, b: pe(e, '::before'), a: pe(e, '::after') }; };
      const dc = getComputedStyle(d);
      return { call: pick('a[href^="tel:"]'), wa: pick('a[href*="wa.me"]'), mail: pick('a[href^="mailto:"]'),
        dock: { bg: dc.backgroundColor, img: dc.backgroundImage, radius: dc.borderTopLeftRadius, b: pe(d, '::before'), a: pe(d, '::after') } }; }"""
    per = {}
    nocontent = ("none", "normal")
    for u, r in scan(390, 844, js).items():
        if r is None:
            continue
        m = []
        for name in ("call", "wa", "mail"):
            if r[name] is None:
                m.append(f"Dock-Knopf '{name}' fehlt")
        c, w, ma, dk = r["call"], r["wa"], r["mail"], r["dock"]
        if c:
            if rgba(c["bg"])[:3] != (0, 0, 254) or rgba(c["bg"])[3] != 1:
                m.append(f"Anrufen Hintergrund {c['bg']} statt rgb(0, 0, 254)")
            if c["color"] != "rgb(255, 255, 255)":
                m.append(f"Anrufen Schrift {c['color']} statt weiss")
        if w:
            a = rgba(w["bg"])
            if not a or a[3] > 0.3 or a[3] == 0:
                m.append(f"WhatsApp Hintergrund {w['bg']} (Alpha soll >0 und <= 0,3 sein)")
        if ma and (rgba(ma["bg"]) or (0, 0, 0, 1))[3] != 0:
            m.append(f"E-Mail Hintergrund {ma['bg']} statt transparent")
        for name, e in (("Anrufen", c), ("WhatsApp", w), ("E-Mail", ma)):
            if e:
                if e["img"] != "none":
                    m.append(f"{name} background-image {e['img'][:40]}")
                for k in ("a", "b"):
                    if e[k]["content"] not in nocontent:
                        m.append(f"{name} ::{'after' if k == 'a' else 'before'} hat Inhalt {e[k]['content']}")
        if dk["img"] != "none":
            m.append(f"Dock background-image {dk['img'][:40]}")
        if rgba(dk["bg"]) is None or rgba(dk["bg"]) != (20, 26, 38, 1.0):
            m.append(f"Dock Flaeche {dk['bg']} statt rgb(20, 26, 38) deckend")
        if dk["radius"] != "16px":
            m.append(f"Dock Radius {dk['radius']} statt 16px")
        for k, n in (("a", "after"), ("b", "before")):
            if dk[k]["content"] not in nocontent:
                m.append(f"Dock ::{n} hat Inhalt {dk[k]['content']}")
        if m:
            per[u] = m
    return errs + agg(per)


def ak_r1_03_desktop_box():
    """AK-R1-03: >= 1280: Dock weg (alle Seiten); .hc-direkt direkt nach .hero mit tel:-Link (>= 20 px) und
    a[data-wa="direkt"], ohne Knopfflaechen (G9); bei 390 Hoehe 0."""
    errs = []
    res = scan(1440, 900, DOCK_JS)
    per = {u: [f"Dock display:{d['display']} bei 1440 (soll none sein)"] for u, d in res.items()
           if d is not None and d["display"] != "none"}
    errs += agg(per)
    js = """() => { const hero = document.querySelector('.hero'); if (!hero) return { nohero: true };
      const n = hero.nextElementSibling, e = document.querySelector('.hc-direkt');
      if (!e) return { missing: true };
      const tel = e.querySelector('a[href^="tel:"]'), wa = e.querySelector('a[data-wa="direkt"]');
      const box = a => a ? { bg: getComputedStyle(a).backgroundColor, bw: getComputedStyle(a).borderTopWidth } : null;
      return { next: n === e, h: e.getBoundingClientRect().height, disp: getComputedStyle(e).display,
        tel: tel ? { text: tel.textContent.replace(/\\s+/g, ' ').trim(), fs: parseFloat(getComputedStyle(tel).fontSize), box: box(tel) } : null,
        wa: wa ? { text: wa.textContent.trim(), box: box(wa) } : null }; }"""
    for vw, vh in ((1440, 900), (1280, 800)):
        r = scan(vw, vh, js, ["/"])["/"]
        if r.get("nohero"):
            errs.append("/: kein .hero"); break
        if r.get("missing"):
            errs.append("/: kein .hc-direkt (Kasten nach dem Hero fehlt)"); break
        tag = f"/ bei {vw}"
        if not r["next"]:
            errs.append(f"{tag}: .hc-direkt ist nicht das naechste Element nach .hero")
        if r["h"] <= 0:
            errs.append(f"{tag}: .hc-direkt nicht sichtbar (Hoehe {r['h']})")
        if not r["tel"]:
            errs.append(f"{tag}: kein tel:-Link in .hc-direkt")
        else:
            if "0178 258 44 38" not in r["tel"]["text"]:
                errs.append(f"{tag}: tel:-Linktext '{r['tel']['text']}' ohne '0178 258 44 38'")
            if r["tel"]["fs"] < 20:
                errs.append(f"{tag}: tel:-Link {r['tel']['fs']} px < 20")
        if not r["wa"]:
            errs.append(f"{tag}: kein a[data-wa=\"direkt\"] in .hc-direkt")
        for nm in ("tel", "wa"):
            b = r[nm] and r[nm]["box"]
            if b and ((rgba(b["bg"]) or (0, 0, 0, 0))[3] > 0 or float(b["bw"][:-2]) > 0):
                errs.append(f"{tag}: {nm}-Link mit Knopffläche (Hintergrund {b['bg']}, Rand {b['bw']}), G9 verlangt Textlink")
    r390 = scan(390, 844, js, ["/"])["/"]
    if r390.get("missing"):
        errs.append("/ bei 390: .hc-direkt fehlt (Hoehe 0 nicht belegbar)")
    elif r390.get("h", 1) != 0:
        errs.append(f"/ bei 390: .hc-direkt Hoehe {r390['h']} statt 0")
    return errs


def deployed_html():
    skip = (".playwright-mcp/", ".superpowers/", "node_modules/", ".git/")
    return [p for p in sorted(ROOT.rglob("*.html"))
            if deployable(rel(p)) and not rel(p).startswith(skip)]


def ak_r1_04_nav_loc():
    """AK-R1-04: .nav-loc in keiner ausgelieferten HTML-Datei, Generator erzeugt sie nicht."""
    hits = [rel(p) for p in deployed_html() if re.search(r'class="[^"]*\bnav-loc\b', read(p))]
    errs = []
    if hits:
        errs.append(f".nav-loc in {len(hits)} HTML-Dateien, z. B. {', '.join(hits[:5])}")
    n = read(ROOT / "tools" / "build_landingpages.py").count("nav-loc")
    if n:
        errs.append(f"tools/build_landingpages.py erzeugt .nav-loc ({n} Fundstellen)")
    return errs


def ak_r1_05_kicker():
    """AK-R1-05: .s-label Startseite <= 3, alle anderen Seiten 0."""
    per = {}
    rx = re.compile(r'class="[^"]*\bs-label\b')
    for p in pages():
        n = len(rx.findall(read(p)))
        lim = 3 if rel(p) == "index.html" else 0
        if n > lim:
            per[url_of(p)] = [f".s-label {n}x (erlaubt {lim})"]
    return agg(per)


def ak_r1_06_typo():
    """AK-R1-06 (Startseite): body.is-home; .s-title >= 30 px bei 390 und >= 46 px bei 1440; Fliesstext-Median
    16-17,5 bei 1440; <= 8 Schriftgroessen in <main> bei 1440 (Chat-Handy und Tabellen ausgenommen).
    Unterseiten: AK4 in check_site.py."""
    errs = []
    js = """(excl) => { const fs = e => parseFloat(getComputedStyle(e).fontSize);
      const titles = [...document.querySelectorAll('main .s-title')].map(fs);
      const body = [...document.querySelectorAll('main p, main li, main dd, .faq-a')]
        .filter(e => !e.closest('nav,footer,.lp-crumbs') && !e.closest(excl) && !e.closest('table') && e.getBoundingClientRect().height > 0).map(fs).sort((a, b) => a - b);
      const sizes = new Set();
      const w = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT);
      while (w.nextNode()) { const t = w.currentNode, e = t.parentElement;
        if (!t.textContent.trim() || e.closest(excl) || e.closest('table,svg,script,style') || e.closest('[hidden]')) continue;
        if (!e.getClientRects().length) continue;
        sizes.add(Math.round(fs(e) * 10) / 10); }
      return { home: document.body.classList.contains('is-home'), titles, median: body.length ? body[Math.floor(body.length / 2)] : 0,
        nbody: body.length, sizes: [...sizes].sort((a, b) => a - b) }; }"""
    r390 = scan(390, 844, js, ["/"], CHAT_EXCLUDE)["/"]
    r1440 = scan(1440, 900, js, ["/"], CHAT_EXCLUDE)["/"]
    if not r390["home"]:
        errs.append("/: body hat nicht die Klasse is-home")
    if not r390["titles"]:
        errs.append("/: kein 'main .s-title'")
    low = [t for t in r390["titles"] if t < 30]
    if low:
        errs.append(f"/ bei 390: {len(low)} von {len(r390['titles'])} .s-title unter 30 px (kleinster {min(low)})")
    low = [t for t in r1440["titles"] if t < 46]
    if low:
        errs.append(f"/ bei 1440: {len(low)} von {len(r1440['titles'])} .s-title unter 46 px (kleinster {min(low)})")
    if not 16 <= r1440["median"] <= 17.5:
        errs.append(f"/ bei 1440: Fliesstext-Median {r1440['median']} px (soll 16 bis 17,5; {r1440['nbody']} Absaetze)")
    if len(r1440["sizes"]) > 8:
        errs.append(f"/ bei 1440: {len(r1440['sizes'])} Schriftgroessen in <main> (max 8): {r1440['sizes']}")
    return errs


def ak_r1_07_measure_62ch():
    """AK-R1-07: kein p/li in <main> der Startseite (ausgenommen nur Tabellen, Chat, Karten-Raster) breiter als 62ch bei 1440;
    FAQ-Antworten und Zitattexte werden gemessen."""
    js = """(excl) => { const bad = [], skip = excl + ', table, .pkg-grid, .price-card, .k3-card, .testi-card .testi-who, .testi-card .testi-role';
      document.querySelectorAll('details').forEach(d => { d.open = true; });
      let n = 0;
      for (const e of document.querySelectorAll('main p, main li')) {
        if (e.closest(skip)) continue;
        const r = e.getBoundingClientRect(); if (r.height <= 0) continue;
        n++;
        const probe = document.createElement('span'); probe.style.cssText = 'display:inline-block;width:1ch;visibility:hidden;position:absolute';
        e.appendChild(probe); const ch = probe.getBoundingClientRect().width; probe.remove();
        const cs = getComputedStyle(e), inner = r.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        if (inner / ch > 62.5) bad.push((e.className ? e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0] : e.tagName.toLowerCase()) + ' ' + (inner / ch).toFixed(0) + 'ch: ' + e.textContent.trim().slice(0, 30)); }
      return { n, bad }; }"""
    r = scan(1440, 900, js, ["/"], CHAT_EXCLUDE)["/"]
    errs = []
    if r["n"] < 5:
        errs.append(f"/: nur {r['n']} messbare Absaetze (Selektoren pruefen)")
    if r["bad"]:
        errs.append(f"/ bei 1440: {len(r['bad'])} von {r['n']} Absaetzen breiter als 62ch, z. B. {'; '.join(r['bad'][:4])}")
    return errs


CYAN_JS = """(allow) => { const RX = /38,\\s*189,\\s*239/, found = {};
  const sig = (e, ps) => { let s = e.tagName.toLowerCase(); const c = typeof e.className === 'string' ? e.className.trim().split(/\\s+/).filter(Boolean).slice(0, 2) : [];
    if (c.length) s += '.' + c.join('.'); const p = e.parentElement; if (p) { s = (p.tagName.toLowerCase() + (typeof p.className === 'string' && p.className.trim() ? '.' + p.className.trim().split(/\\s+/)[0] : '')) + ' > ' + s; }
    return s + (ps || ''); };
  const allowed = e => allow.some(a => { try { return e.closest(a) !== null; } catch (x) { return false; } });
  const roots = [...document.querySelectorAll('main, footer.site-footer, header.site-header')];
  const hit = (e, ps, prop, val) => { if (!val || !RX.test(val)) return; if (allowed(e)) return;
    const k = sig(e, ps) + ' ' + prop; found[k] = (found[k] || 0) + 1; };
  for (const root of roots) for (const e of [root, ...root.querySelectorAll('*')]) {
    if (!e.getClientRects().length && !(e instanceof SVGElement)) continue;
    const c = getComputedStyle(e);
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own) hit(e, '', 'color', c.color);
    hit(e, '', 'background-color', c.backgroundColor); hit(e, '', 'background-image', c.backgroundImage);
    hit(e, '', 'box-shadow', c.boxShadow);
    for (const s of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(c['border' + s + 'Width']) > 0 && c['border' + s + 'Style'] !== 'none') hit(e, '', 'border-color', c['border' + s + 'Color']);
    if (e instanceof SVGElement) { hit(e, '', 'fill', c.fill); hit(e, '', 'stroke', c.stroke); }
    // Sprite-Icons (<use>) und Pfade mit currentColor malen in der Schriftfarbe des <svg>; fill/stroke am <svg> selbst
    // zeigen das nicht, deshalb hier die Farbe werten, die das Icon tatsaechlich traegt (nur sichtbare Icons, wie beim Text)
    if (e.tagName.toLowerCase() === 'svg' && e.getClientRects().length && (e.querySelector('use, [fill="currentColor" i], [stroke="currentColor" i]') ||
        /currentcolor/i.test((e.getAttribute('fill') || '') + (e.getAttribute('stroke') || '')))) hit(e, '', 'color (currentColor)', c.color);
    for (const ps of ['::before', '::after']) { const pc = getComputedStyle(e, ps); if (pc.content === 'none' || pc.content === 'normal') continue;
      hit(e, ps, 'color', pc.color); hit(e, ps, 'background-color', pc.backgroundColor); hit(e, ps, 'background-image', pc.backgroundImage);
      hit(e, ps, 'box-shadow', pc.boxShadow);
      for (const s of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(pc['border' + s + 'Width']) > 0 && pc['border' + s + 'Style'] !== 'none') hit(e, ps, 'border-color', pc['border' + s + 'Color']); } }
  return found; }"""


def ak_r1_08_cyan():
    """AK-R1-08: Cyan (38, 189, 239 als Schrift-, Flaechen-, Rand-, Schatten-, Verlaufs-, SVG-Farbe, auch mit Alpha und
    an ::before/::after) in <main>, footer.site-footer und header.site-header nur an CYAN_ALLOW; alle Seiten, 390 und 1440."""
    per = {}
    for vw, vh in ((390, 844), (1440, 900)):
        for u, found in scan(vw, vh, CYAN_JS, None, CYAN_ALLOW).items():
            for k, n in found.items():
                per.setdefault(u, []).append(f"{vw}: Cyan an {k} ({n}x)")
    return agg(per, 3)


def ak_r1_09_radius():
    """AK-R1-09: Tokens --r-s/-m/-l/-xl (6/10/16/28 px) definiert und je >= 1x verwendet; haeufigster Radius <= 60 %
    der gerundeten Elemente in <main> der Startseite; 50 %/999 px nur an .ava/.hc-ava/.hc-pause/.zw-pause/Punkten."""
    errs, css = [], style_css()
    for tok, val in (("--r-s", "6px"), ("--r-m", "10px"), ("--r-l", "16px"), ("--r-xl", "28px")):
        if not re.search(re.escape(tok) + r"\s*:\s*" + val, css):
            errs.append(f"style.css: {tok}: {val} nicht definiert")
        if not re.search(r"var\(\s*" + re.escape(tok) + r"\s*[,)]", css):
            errs.append(f"style.css: var({tok}) wird nirgends verwendet")
    js = """(ok) => { const cnt = {}, bad = []; let n = 0;
      for (const e of document.querySelectorAll('main, main *')) {
        const r = e.getBoundingClientRect(); if (r.height <= 0 || e instanceof SVGElement) continue;
        const v = getComputedStyle(e).borderTopLeftRadius; if (v === '0px' || v === '') continue;
        n++; cnt[v] = (cnt[v] || 0) + 1;
        const px = parseFloat(v), round = v.endsWith('%') ? px >= 50 : px >= 500;
        if (round && !e.matches(ok) && !(Math.abs(r.width - r.height) <= 1 && r.width <= 12))
          bad.push(e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : '') + ' ' + v); }
      return { n, cnt, bad }; }"""
    r = scan(1440, 900, js, ["/"], RADIUS_ROUND_OK)["/"]
    if r["n"] < 10:
        errs.append(f"/: nur {r['n']} gerundete Elemente gemessen")
    else:
        top, c = max(r["cnt"].items(), key=lambda kv: kv[1])
        if c / r["n"] > 0.6:
            errs.append(f"/ bei 1440: Radius {top} an {c} von {r['n']} gerundeten Elementen ({c / r['n']:.0%} > 60 %), Verteilung {r['cnt']}")
    if r["bad"]:
        errs.append(f"/: {len(r['bad'])} runde Elemente (50 %/999 px) ausserhalb der Ausnahmen: {', '.join(sorted(set(r['bad']))[:6])}")
    return errs


def ak_r1_10_light_section():
    """AK-R1-10: genau ein heller Abschnitt (Luminanz > 0,8): #schnellcheck (.sec--light); Text darin >= 4,5:1."""
    js = """() => { const eff = e => { let layers = []; for (let n = e; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; layers.push(c); if (/^rgb\\(/.test(c) || /, 1\\)$/.test(c)) break; } return layers; };
      const secs = [...document.querySelectorAll('main > section, main > div > section, body > section')];
      const out = secs.map(s => ({ id: s.id || s.className, cls: s.className, bg: eff(s) }));
      const sc = document.getElementById('schnellcheck'), texts = [];
      if (sc) { const w = document.createTreeWalker(sc, NodeFilter.SHOW_TEXT);
        while (w.nextNode()) { const t = w.currentNode, e = t.parentElement; if (!t.textContent.trim() || e.closest('svg,script,style,[hidden]') || !e.getClientRects().length) continue;
          texts.push({ txt: t.textContent.trim().slice(0, 28), color: getComputedStyle(e).color, bg: eff(e), el: e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : '') }); } }
      return { secs: out, texts, scCls: sc ? sc.className : null }; }"""
    errs = []
    r = scan(1440, 900, js, ["/"])["/"]

    def flat(layers):                       # Schichten von innen nach aussen ueber Schwarz mischen
        base = (0.0, 0.0, 0.0)
        for c in reversed(layers):
            a = rgba(c) or (0, 0, 0, 0)
            base = tuple(a[i] * a[3] + base[i] * (1 - a[3]) for i in range(3))
        return base
    light = [s["id"] for s in r["secs"] if lum(flat(s["bg"])) > 0.8]
    if not r["secs"]:
        errs.append("/: keine Abschnitte (main > section) gefunden")
    if light != ["schnellcheck"]:
        errs.append(f"/: helle Abschnitte {light or 'keine'} statt genau ['schnellcheck']")
    if r["scCls"] is None:
        errs.append("/: #schnellcheck fehlt")
    elif "sec--light" not in r["scCls"].split():
        errs.append(f"/: #schnellcheck traegt nicht die Klasse sec--light (hat: {r['scCls']})")
    bad = []
    for t in r["texts"]:
        fg = rgba(t["color"])
        bg = flat(t["bg"])
        if fg is None:
            continue
        fgc = tuple(fg[i] * fg[3] + bg[i] * (1 - fg[3]) for i in range(3))
        c = contrast(fgc, bg)
        if c < 4.5:
            bad.append(f"{t['el']} '{t['txt']}' {c:.1f}:1")
    if r["scCls"] is not None and not r["texts"]:
        errs.append("/: #schnellcheck ohne Textknoten")
    if bad:
        errs.append(f"/: #schnellcheck {len(bad)} Textknoten unter 4,5:1, z. B. {'; '.join(bad[:4])}")
    return errs


def ak_r1_11_dominant():
    """AK-R1-11: je Abschnitt aus §5.6 genau ein [data-dominant]; ausser .hero/#it-betreuung (R1: nur Anzahl) hat es bei
    1440 die groesste Flaeche unter den sichtbaren Geschwistern (ohne Ueberschriften-Wrapper)."""
    js = """(secs) => secs.map(sel => { const s = document.querySelector(sel); if (!s) return { sel, missing: true };
      const d = [...s.querySelectorAll('[data-dominant]')], res = { sel, count: d.length };
      if (d.length !== 1) return res;
      const e = d[0], area = x => { const r = x.getBoundingClientRect(); return r.width * r.height; };
      const isHead = x => /^H[1-6]$/.test(x.tagName) || x.matches('.s-label,.s-title,.s-sub') ||
        (x.querySelector('h1,h2,h3,h4') && !x.querySelector('p,figure,img,table,ul,ol,a.btn-p,blockquote'));
      const sib = [...e.parentElement.children].filter(x => x !== e && getComputedStyle(x).display !== 'none' && area(x) > 0 && !isHead(x));
      res.area = Math.round(area(e)); res.sib = sib.map(x => ({ n: x.tagName.toLowerCase() + (x.className ? '.' + String(x.className).split(' ')[0] : ''), a: Math.round(area(x)) }));
      return res; })"""
    errs = []
    for r in scan(1440, 900, js, ["/"], DOMINANT_SECTIONS)["/"]:
        if r.get("missing"):
            errs.append(f"{r['sel']}: Abschnitt fehlt"); continue
        if r["count"] != 1:
            errs.append(f"{r['sel']}: {r['count']} Elemente mit [data-dominant] (soll genau 1)"); continue
        if r["sel"] in DOMINANT_COUNT_ONLY_R1:
            continue
        if not r["sib"]:
            errs.append(f"{r['sel']}: [data-dominant] hat keine sichtbaren Geschwister zum Vergleich"); continue
        bigger = [s for s in r["sib"] if s["a"] >= r["area"]]
        if bigger:
            errs.append(f"{r['sel']}: [data-dominant] ({r['area']} px²) nicht groesser als Geschwister {bigger[0]['n']} ({bigger[0]['a']} px²)")
    return errs


def _norm_quote(t):
    return re.sub(r"\s+", " ", re.sub(r"[„“”\"']", "", t)).strip()


def ak_r1_12_featured_quote():
    """AK-R1-12 (DOM-Teil): .testi-card--featured genau einmal, Quelle 'Google-Bewertung', Text = REVIEWS; Herkunftshinweis
    nicht in <details>; Icon (::before) schneidet kein Textrechteck. Wortgleichheit mit reviewBody: AK9, Hinweis: AK14."""
    js = """() => { const f = [...document.querySelectorAll('.testi-card--featured')], h = document.getElementById('bewertungen-herkunft');
      const res = { count: f.length, herkunft: h ? { indetails: !!h.closest('details') } : null };
      if (f.length !== 1) return res;
      const c = f[0], r = c.getBoundingClientRect(), cs = getComputedStyle(c);
      res.pseudo = [];
      for (const ps of ['::before', '::after']) { const q = getComputedStyle(c, ps);
        if (q.content === 'none' || q.content === 'normal') continue;
        if (q.position !== 'absolute') { res.pseudo.push(ps + ' hat Inhalt, ist aber position:' + q.position + ' (soll absolute)'); continue; }
        const w = parseFloat(q.width) || parseFloat(q.fontSize) * 0.6, hh = parseFloat(q.height) || parseFloat(q.lineHeight) || parseFloat(q.fontSize);
        const left = q.left !== 'auto' ? r.left + parseFloat(q.left) : r.right - parseFloat(q.right) - w, top = q.top !== 'auto' ? r.top + parseFloat(q.top) : r.bottom - parseFloat(q.bottom) - hh;
        (res.icons = res.icons || []).push({ ps, l: left, t: top, r: left + w, b: top + hh }); }
      res.who = (c.querySelector('.testi-who') || {}).textContent; res.role = (c.querySelector('.testi-role') || {}).textContent;
      res.text = (c.querySelector('blockquote') || {}).textContent;
      {
        res.lines = [];
        for (const t of c.querySelectorAll('blockquote, .testi-who, .testi-role, .stars')) { const rg = document.createRange(); rg.selectNodeContents(t);
          for (const k of rg.getClientRects()) res.lines.push({ l: k.left, t: k.top, r: k.right, b: k.bottom }); } }
      return res; }"""
    errs = []
    r = scan(1440, 900, js, ["/"])["/"]
    if r["count"] != 1:
        errs.append(f"/: .testi-card--featured {r['count']}x (soll genau 1)")
    else:
        if (r.get("role") or "").strip() != "Google-Bewertung":
            errs.append(f"/: Quelle der grossen Karte '{(r.get('role') or '').strip()}' statt 'Google-Bewertung'")
        rv = [x for x in gen().REVIEWS if x["who"] == (r.get("who") or "").strip()]
        if not rv:
            errs.append(f"/: grosse Karte '{r.get('who')}' nicht in REVIEWS (Namen koennen anonymisiert sein, dann who angleichen)")
        else:
            want = _norm_quote(" ".join(rv[0]["paragraphs"]))
            if _norm_quote(r.get("text") or "") != want:
                errs.append(f"/: Text der grossen Karte weicht von REVIEWS ab ('{_norm_quote(r.get('text') or '')[:40]}')")
            if rv[0]["source"] != "Google-Bewertung":
                errs.append(f"REVIEWS-Quelle der grossen Karte '{rv[0]['source']}' statt 'Google-Bewertung'")
        errs.extend(f"/: grosse Karte {m}" for m in r.get("pseudo", []))
        for ic in r.get("icons", []):
            for ln in r["lines"]:
                if ic["l"] < ln["r"] and ic["r"] > ln["l"] and ic["t"] < ln["b"] and ic["b"] > ln["t"]:
                    errs.append(f"/: Zitat-Icon ({ic['ps']}) schneidet ein Textrechteck der grossen Karte"); break
    if r["herkunft"] is None:
        errs.append("/: #bewertungen-herkunft fehlt")
    elif r["herkunft"]["indetails"]:
        errs.append("/: #bewertungen-herkunft steht in <details> (soll sichtbar sein)")
    return errs


def ak_r1_13_prices():
    """AK-R1-13: Abzeichen 'Meine Empfehlung' (text-transform:none), .price-name-Reihenfolge Starter, Business, Premium
    auf / und /managed-it-service/. Preiszeilen: AK14 (check_static)."""
    js = """() => ({ badges: [...document.querySelectorAll('.price-badge')].map(b => ({ t: b.textContent.trim(), tt: getComputedStyle(b).textTransform })),
      names: [...document.querySelectorAll('.price-name')].map(n => n.textContent.trim()) })"""
    errs = []
    for u, r in scan(1440, 900, js, ["/", "/managed-it-service/"]).items():
        if len(r["badges"]) != 1:
            errs.append(f"{u}: {len(r['badges'])} .price-badge (soll genau 1)")
        for b in r["badges"]:
            if b["t"] != "Meine Empfehlung":
                errs.append(f"{u}: Abzeichen '{b['t']}' statt 'Meine Empfehlung'")
            if b["tt"] != "none":
                errs.append(f"{u}: Abzeichen text-transform:{b['tt']} statt none")
        if r["names"] != ["Starter", "Business", "Premium"]:
            errs.append(f"{u}: .price-name-Reihenfolge {r['names']} statt ['Starter', 'Business', 'Premium']")
    return errs


def ak_r1_14_geo_chips():
    """AK-R1-14: Orte-Chips (.geo-chips > *) opacity 1 (auch Vorfahren), Kontrast >= 4,5:1, keine Pille."""
    js = """() => { const eff = e => { let layers = []; for (let n = e; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; layers.push(c); if (/^rgb\\(/.test(c)) break; } return layers; };
      return [...document.querySelectorAll('.geo-chips > *')].map(e => { const r = e.getBoundingClientRect(), c = getComputedStyle(e);
        let op = 1; for (let n = e; n; n = n.parentElement) op *= parseFloat(getComputedStyle(n).opacity);
        return { t: e.textContent.trim(), op, color: c.color, bg: eff(e), rad: c.borderTopLeftRadius, w: r.width, h: r.height }; }); }"""
    chips = scan(1440, 900, js, ["/"])["/"]
    if not chips:
        return ["/: keine .geo-chips > * gefunden"]

    def flat(layers):
        base = (0.0, 0.0, 0.0)
        for c in reversed(layers):
            a = rgba(c) or (0, 0, 0, 0)
            base = tuple(a[i] * a[3] + base[i] * (1 - a[3]) for i in range(3))
        return base
    ops, lows, pills = [], [], []
    for c in chips:
        if c["op"] < 0.999:
            ops.append(f"{c['t']} {c['op']:.2f}")
        fg, bg = rgba(c["color"]), flat(c["bg"])
        fgc = tuple(fg[i] * fg[3] + bg[i] * (1 - fg[3]) for i in range(3))
        k = contrast(fgc, bg)
        if k < 4.5:
            lows.append(f"{c['t']} {k:.1f}:1")
        rad = float(c["rad"].rstrip("px%") or 0)
        if c["rad"].endswith("%") or rad >= min(c["w"], c["h"]) / 2 - 0.5 or rad >= 100:
            pills.append(f"{c['t']} {c['rad']}")
    errs = []
    if ops:
        errs.append(f"/: {len(ops)} von {len(chips)} Chips nicht voll deckend: {', '.join(ops[:4])}")
    if lows:
        errs.append(f"/: {len(lows)} von {len(chips)} Chips unter 4,5:1: {', '.join(lows[:4])}")
    if pills:
        errs.append(f"/: {len(pills)} von {len(chips)} Chips als Pille (Radius): {', '.join(pills[:3])}")
    return errs


def ak_r1_22_voice_consent():
    """AK-R1-22: Namen ohne Einwilligung duerfen auf keiner Seite (sichtbar oder im Schema) stehen. Die Namensliste liegt
    ausserhalb des Repos (NAMEN_OHNE_EINWILLIGUNG, eine Zeile je Name, Kleinschreibung egal)."""
    if not NAMEN_OHNE_EINWILLIGUNG.is_file():
        return ["Namensliste ausserhalb des Repos fehlt, Pruefung nicht moeglich"]
    names = [x.strip().lower() for x in NAMEN_OHNE_EINWILLIGUNG.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not names:
        return ["Namensliste ausserhalb des Repos ist leer, Pruefung nicht moeglich"]
    hits = [url_of(p) for p in pages() if any(n in read(p).lower() for n in names)]
    if hits:
        return [f"Name ohne Einwilligung sichtbar oder im Schema ({len(hits)} Seite(n): {', '.join(hits[:4])}); "
                f"soll abgekuerzt (Initialen) oder entfernt sein"]
    return []


FOCUS_JS = """() => { document.documentElement.style.scrollBehavior = 'auto';
  const d = document.querySelector('.sticky-contact');
  const dockTop = () => d && getComputedStyle(d).display !== 'none' ? d.getBoundingClientRect().top : innerHeight;
  const sel = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  const els = [...document.querySelectorAll(sel)].filter(e => !e.disabled && !e.closest('.sticky-contact') && e.checkVisibility && e.checkVisibility() && e.getBoundingClientRect().height > 0);
  const bad = []; let n = 0;
  for (const e of els) { if (getComputedStyle(e).position === 'fixed' || e.closest('header.site-header')) continue;
    e.focus(); const r = e.getBoundingClientRect(), t = dockTop(); n++;
    const tall = r.height > t - 80;
    const ok = tall ? (r.top >= -0.5 && r.top < t - 44) : r.bottom <= t + 0.5;
    if (!ok) bad.push((e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : '') + ' "' + (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 20) + '"') + ' Unterkante ' + Math.round(r.bottom) + ' > Dock ' + Math.round(t)); }
  return { n, bad, hasDock: !!d }; }"""


def ak_r1_23_focus_not_obscured():
    """AK-R1-23: 390x844, alle fokussierbaren Elemente der Startseite per focus(): Unterkante liegt danach ueber der
    Dock-Oberkante (zu hohe Elemente: Oberkante sichtbar)."""
    r = scan(390, 844, FOCUS_JS, ["/"])["/"]
    errs = []
    if not r["hasDock"]:
        errs.append("/: kein Dock (Vergleichsgrundlage fehlt)")
    if r["n"] < 10:
        errs.append(f"/: nur {r['n']} fokussierbare Elemente geprueft")
    if r["bad"]:
        errs.append(f"/: {len(r['bad'])} von {r['n']} fokussierten Elementen vom Dock verdeckt, z. B. {'; '.join(r['bad'][:4])}")
    return errs


AK_R1 = {
    "R1-01a": ak_r1_01a_dock_narrow, "R1-01b": ak_r1_01b_dock_wide, "R1-01c": ak_r1_01c_safe_area,
    "R1-02": ak_r1_02_dock_colors, "R1-03": ak_r1_03_desktop_box, "R1-04": ak_r1_04_nav_loc, "R1-05": ak_r1_05_kicker,
    "R1-06": ak_r1_06_typo, "R1-07": ak_r1_07_measure_62ch, "R1-08": ak_r1_08_cyan, "R1-09": ak_r1_09_radius,
    "R1-10": ak_r1_10_light_section, "R1-11": ak_r1_11_dominant, "R1-12": ak_r1_12_featured_quote,
    "R1-13": ak_r1_13_prices, "R1-14": ak_r1_14_geo_chips, "R1-22": ak_r1_22_voice_consent,
    "R1-23": ak_r1_23_focus_not_obscured,
}
# Nicht hier: AK-R1-15 (Service Worker, check_sw.py), AK-R1-17 (Lighthouse/Trace per MCP), 16/18-21 (andere Skripte/Chat).


# ----------------------------------------------------------------------------------------------------------------------
# Task 11: Abnahmekriterien R2 (Spec §4.2, §4.4, §5.8, §6; AK-R2-06 ... AK-R2-16). Rot, bis die Buehne (Task 12) und der
# Umzug des Chats (Task 13) gebaut sind. Zeit laeuft ueber page.clock (Zeit steht, bis run_for sie weiterdreht); CSS-
# Uebergaenge laufen in echter Zeit und werden deshalb vor dem Messen abgewartet oder beendet.
# ----------------------------------------------------------------------------------------------------------------------
import datetime
from check_static import HERO_WEGE, FUSSZEILE_HERO

BASELINE = {}   # hoehen.json der Vorher-Messung; run_release setzt sie aus --baseline
ZW_BTN = "button.zw-pause[data-zw-pause]"
ZW_LABELS = {"laeuft": "Beispiele anhalten", "pause": "Beispiele weiter abspielen", "ende": "Nochmal abspielen"}
ZW_MAX_MS = 40000          # Spec §5.8: Gesamtdauer <= 40 s
CLOCK_T0 = datetime.datetime(2026, 10, 19, 10, 0, 0)

# Zeichenketten der Fall-Bildtexte in Lesereihenfolge (Fall 1..4; links 1, links 2, rechts 1, rechts 2)
def _fall_texts(n):
    f = HERO_WEGE["faelle"][n - 1]
    return list(f["links"]) + list(f["rechts"])


def _open(vw, vh, reduced="no-preference", clock=True, js=True):
    """Startseite in einem frischen Kontext; mit clock steht die Zeit bis run_for still. Rueckgabe (ctx, page)."""
    env = _env()
    ctx = env["b"].new_context(viewport={"width": vw, "height": vh}, service_workers="block", reduced_motion=reduced,
                               java_script_enabled=js)
    pg = ctx.new_page()
    if clock:
        pg.clock.install(time=CLOCK_T0)
        pg.clock.pause_at(CLOCK_T0 + datetime.timedelta(seconds=1))
    pg.goto(env["base"] + "/", wait_until="load")
    pg.wait_for_timeout(400)     # erster Zeichenvorgang in echter Zeit
    return ctx, pg


def _run(pg, ms, step=250):
    """Uhr um ms weiterdrehen, in Schritten (Timer und rAF feuern wie im Betrieb)."""
    for _ in range(max(1, ms // step)):
        pg.clock.run_for(step)


def _settle(pg, ms=650):
    pg.wait_for_timeout(ms)      # echte Zeit: laufende CSS-Uebergaenge (200-400 ms) auslaufen lassen


STAGE_SNAP = """() => { const s = document.querySelector('.zw-stage'); if (!s) return null;
  const p = [s.getAttribute('data-zustand'), s.getAttribute('data-fall'), s.outerHTML];
  for (const e of s.querySelectorAll('*')) { const c = getComputedStyle(e);
    p.push((e.getAttribute('class') || '') + '|' + c.transform + '|' + c.opacity + '|' + c.visibility + '|' + c.display); }
  return p.join('\\n'); }"""

SCROLL_STAGE = "() => { const s = document.querySelector('.zw-stage'); if (s) s.scrollIntoView({block: 'center'}); return !!s; }"


def _stage_to_view(pg):
    """Unter 1024 px liegt die Buehne unter dem Falz; sie pausiert, solange weniger als 20 % sichtbar sind (Spec §5.8)."""
    ok = pg.evaluate(SCROLL_STAGE)
    pg.wait_for_timeout(250)
    return ok


def _btn_label(pg):
    return pg.evaluate("(sel) => { const b = document.querySelector(sel); return b ? b.getAttribute('aria-label') : null; }", ZW_BTN)


PAUSE_JS = """(sel) => { const bs = [...document.querySelectorAll(sel)], b = bs[0];
  if (!b) return { n: 0 };
  const r = b.getBoundingClientRect();
  return { n: bs.length, inStage: !!b.closest('.zw-stage'), inHero: !!b.closest('.hero'), w: r.width, h: r.height,
           visible: b.checkVisibility({ visibilityProperty: true, opacityProperty: true }) && r.width > 0 && r.height > 0,
           disabled: b.disabled, hidden: b.hidden, label: b.getAttribute('aria-label') }; }"""


def ak_r2_06_pause():
    """AK-R2-06: Pause-Knopf (WCAG 2.2.2) sichtbar, >= 44x44, per Tab erreichbar, ausserhalb der Buehne; nach dem Klick
    3 s keine Aenderung an DOM/transform/opacity; Beschriftung wechselt; Ablauf endet nach <= 40 s im Endstand mit
    'Nochmal abspielen'."""
    errs = []
    ctx, pg = _open(1440, 900)
    try:
        if pg.evaluate("() => !document.querySelector('.zw-stage')"):
            return ["/: .zw-stage fehlt (Buehne nicht gebaut)"]
        _run(pg, 1500)
        i = pg.evaluate(PAUSE_JS, ZW_BTN)
        if i["n"] != 1:
            return [f"/: {i['n']}x {ZW_BTN} (soll genau 1)"]
        if i["inStage"]:
            errs.append("/: Pause-Knopf steht in der aria-hidden-Buehne (soll ausserhalb)")
        if not i["inHero"]:
            errs.append("/: Pause-Knopf steht nicht in .hero")
        if not i["visible"] or i["hidden"]:
            errs.append("/: Pause-Knopf nicht sichtbar")
        if i["w"] < 44 or i["h"] < 44:
            errs.append(f"/: Pause-Knopf {i['w']:.0f}x{i['h']:.0f} px, soll >= 44x44")
        if i["label"] != ZW_LABELS["laeuft"]:
            errs.append(f"/: Beschriftung im Lauf '{i['label']}' statt '{ZW_LABELS['laeuft']}'")
        # Tastatur: per Tab erreichbar
        pg.evaluate("() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); }")
        hit = False
        for _ in range(80):
            pg.keyboard.press("Tab")
            if pg.evaluate("(sel) => !!document.activeElement && document.activeElement.matches(sel)", ZW_BTN):
                hit = True
                break
        if not hit:
            errs.append("/: Pause-Knopf per Tab nicht erreichbar (80 Tab-Schritte)")
        # Klick: 3 s Stillstand
        pg.click(ZW_BTN)
        _settle(pg)
        a = pg.evaluate(STAGE_SNAP)
        _run(pg, 3000)
        _settle(pg, 150)
        b = pg.evaluate(STAGE_SNAP)
        if a != b:
            errs.append("/: nach dem Klick auf Pause aendern sich in 3 s DOM/transform/opacity der Buehne")
        if pg.evaluate("() => document.querySelector('.zw-stage').getAttribute('data-zustand')") != "pause":
            errs.append("/: nach dem Klick steht data-zustand nicht auf 'pause'")
        if _btn_label(pg) != ZW_LABELS["pause"]:
            errs.append(f"/: Beschriftung in Pause '{_btn_label(pg)}' statt '{ZW_LABELS['pause']}'")
    finally:
        ctx.close()
    # Ablauf bis zum Ende
    ctx, pg = _open(1440, 900)
    try:
        if pg.evaluate("() => !document.querySelector('.zw-stage')"):
            return errs or ["/: .zw-stage fehlt (Buehne nicht gebaut)"]
        _run(pg, ZW_MAX_MS)
        _settle(pg, 300)
        z = pg.evaluate("() => document.querySelector('.zw-stage').getAttribute('data-zustand')")
        if z != "ende":
            errs.append(f"/: nach {ZW_MAX_MS // 1000} s steht data-zustand auf '{z}' statt 'ende'")
        if _btn_label(pg) != ZW_LABELS["ende"]:
            errs.append(f"/: Beschriftung am Ende '{_btn_label(pg)}' statt '{ZW_LABELS['ende']}'")
        else:
            pg.click(ZW_BTN)
            _run(pg, 500)
            z2 = pg.evaluate("() => document.querySelector('.zw-stage').getAttribute('data-zustand')")
            if z2 != "laeuft":
                errs.append(f"/: 'Nochmal abspielen' startet nicht neu (data-zustand '{z2}')")
    finally:
        ctx.close()
    return errs


MUTATION_JS = """() => { window.__mut = 0;
  const h = document.querySelector('.hero'); if (!h) return false;
  new MutationObserver(m => { window.__mut += m.length; }).observe(h, { subtree: true, childList: true, attributes: true, characterData: true });
  return true; }"""


def ak_r2_07_reduced_motion():
    """AK-R2-07: reduced_motion=reduce: Endstand beim Laden, getAnimations() in .hero leer, 5 s keine DOM-Aenderung."""
    errs = []
    ctx, pg = _open(1440, 900, reduced="reduce")
    try:
        if pg.evaluate("() => !document.querySelector('.zw-stage')"):
            return ["/: .zw-stage fehlt (Buehne nicht gebaut)"]
        pg.evaluate(MUTATION_JS)
        z = pg.evaluate("() => document.querySelector('.zw-stage').getAttribute('data-zustand')")
        if z != "ende":
            errs.append(f"/: bei reduzierter Bewegung steht data-zustand beim Laden auf '{z}' statt 'ende'")
        r = pg.evaluate("""() => { const off = [...document.querySelectorAll('.zw-case[data-fall="4"]')].filter(c => !c.classList.contains('is-on')).length;
          const sch = document.querySelector('.zw-schluss');
          return { off, n4: document.querySelectorAll('.zw-case[data-fall="4"]').length,
                   schluss: sch ? sch.checkVisibility({ visibilityProperty: true, opacityProperty: true }) && parseFloat(getComputedStyle(sch).opacity) > 0.99 : null,
                   anims: document.querySelector('.hero').getAnimations({ subtree: true }).filter(a => a.playState === 'running').length }; }""")
        if r["n4"] == 0 or r["off"]:
            errs.append(f"/: Endstand: Fall 4 nicht sichtbar (is-on fehlt an {r['off']} von {r['n4']} Faellen)")
        if not r["schluss"]:
            errs.append("/: Endstand: .zw-schluss nicht voll sichtbar")
        if r["anims"]:
            errs.append(f"/: bei reduzierter Bewegung laufen {r['anims']} Animationen in .hero")
        _run(pg, 5000)
        m = pg.evaluate("() => window.__mut")
        if m:
            errs.append(f"/: bei reduzierter Bewegung {m} DOM-Aenderungen in 5 s (soll 0)")
        if pg.evaluate("() => document.querySelector('.hero').getAnimations({ subtree: true }).length"):
            errs.append("/: getAnimations() in .hero nach 5 s nicht leer")
    finally:
        ctx.close()
    return errs


FOCUSABLE = "a[href], button, input, select, textarea, summary, iframe, [tabindex], [contenteditable]"


def ak_r2_08_text_alternative():
    """AK-R2-08: Buehne aria-hidden=true ohne fokussierbares Element; der Accessibility-Snapshot von .hero enthaelt alle
    Bildtexte der Faelle in Lesereihenfolge (Liste 'Vier Beispiele aus dem Alltag', .zw-alt.sr-only)."""
    errs = []
    ctx, pg = _open(1440, 900)
    try:
        _run(pg, 1000)
        i = pg.evaluate("""(foc) => { const s = document.querySelector('.zw-stage'), a = document.querySelector('.zw-alt');
          return { stage: !!s, hidden: s ? s.getAttribute('aria-hidden') : null, foc: s ? s.querySelectorAll(foc).length : 0,
                   alt: !!a, altSr: a ? a.classList.contains('sr-only') : false, altHidden: a ? !!a.closest('[aria-hidden="true"]') : false,
                   altInStage: a ? !!a.closest('.zw-stage') : false }; }""", FOCUSABLE)
        if not i["stage"]:
            return ["/: .zw-stage fehlt (Buehne nicht gebaut)"]
        if i["hidden"] != "true":
            errs.append(f"/: .zw-stage aria-hidden='{i['hidden']}' statt 'true'")
        if i["foc"]:
            errs.append(f"/: {i['foc']} fokussierbare Elemente in der aria-hidden-Buehne")
        if not i["alt"]:
            errs.append("/: .zw-alt (Textalternative) fehlt")
        else:
            if not i["altSr"]:
                errs.append("/: .zw-alt ohne Klasse sr-only")
            if i["altHidden"] or i["altInStage"]:
                errs.append("/: .zw-alt steht in aria-hidden oder in der Buehne (Screenreader sehen sie nicht)")
        try:
            snap = pg.locator(".hero").aria_snapshot()
        except Exception as e:                      # Playwright-Fehler sichtbar machen, nie still ueberspringen
            return errs + [f"/: aria_snapshot von .hero nicht lesbar ({str(e).splitlines()[0][:80]})"]
        snap = re.sub(r"\s+", " ", snap.replace(" ", " "))
        head = snap.find("Vier Beispiele aus dem Alltag")
        if head < 0:
            errs.append("/: Snapshot ohne 'Vier Beispiele aus dem Alltag'")
        prev = head
        for n in range(1, 5):
            pos = [snap.find(t, max(head, 0)) for t in _fall_texts(n)]
            miss = [t for t, p in zip(_fall_texts(n), pos) if p < 0]
            if miss:
                errs.append(f"/: Snapshot ohne Bildtexte von Fall {n}: {miss}")
                continue
            if min(pos) <= prev:
                errs.append(f"/: Snapshot: Fall {n} steht nicht hinter Fall {n - 1} (Lesereihenfolge)")
            prev = min(pos)
    finally:
        ctx.close()
    return errs


FOCUS_HIDDEN_JS = """(foc) => [...document.querySelectorAll(foc)].filter(e => e.closest('[aria-hidden="true"]') &&
    !e.disabled && e.checkVisibility && e.checkVisibility()).map(e => e.tagName.toLowerCase() +
    (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : '') + ' "' +
    (e.textContent || e.getAttribute('aria-label') || e.getAttribute('href') || '').trim().slice(0, 24) + '"')"""


def test_no_focusable_in_aria_hidden():
    """Spec §6: kein fokussierbares, sichtbares Element in einem aria-hidden="true"-Bereich der Startseite (Buehne, Chat-
    Handy, Deko), bei 390 und 1440."""
    errs = []
    for vw, vh in ((390, 844), (1440, 900)):
        ctx, pg = _open(vw, vh, clock=False)
        try:
            bad = pg.evaluate(FOCUS_HIDDEN_JS, FOCUSABLE)
            if bad:
                errs.append(f"/ bei {vw}: {len(bad)} fokussierbare Elemente in aria-hidden, z. B. {'; '.join(bad[:4])}")
        finally:
            ctx.close()
    return errs


LANES_JS = """() => { const eff = e => { let o = 1; for (let n = e; n; n = n.parentElement) o *= parseFloat(getComputedStyle(n).opacity); return o; };
  const f = sel => { const e = document.querySelector(sel); if (!e) return null;
    document.getAnimations().forEach(a => { if (a instanceof CSSTransition) { try { a.finish(); } catch (x) {} } });
    const r = e.getBoundingClientRect();
    const vis = e.checkVisibility({ visibilityProperty: true, opacityProperty: true }) && r.width > 0 && r.height > 0 &&
                r.right > 0 && r.left < innerWidth && eff(e) > 0.5;
    return { vis, top: r.top }; };
  return { l: f('.zw-lane--links'), r: f('.zw-lane--rechts') }; }"""


def ak_r2_09_lanes():
    """AK-R2-09: unter 1024 px (390, 1023) sind nie beide Spuren sichtbar (Stichprobe alle 250 ms ueber 15 s, beide Spuren
    kommen nacheinander vor); ab 1024 (1024, 1440) sind beide sichtbar, Oberkanten +-4 px."""
    errs = []
    for vw, narrow in ((390, True), (1023, True), (1024, False), (1440, False)):
        ctx, pg = _open(vw, 900)
        try:
            if not _stage_to_view(pg):
                return ["/: .zw-stage fehlt (Buehne nicht gebaut)"]
            seen_l = seen_r = both = single_gap = 0
            tops = []
            for _ in range(60):
                pg.clock.run_for(250)
                s = pg.evaluate(LANES_JS)
                if s["l"] is None or s["r"] is None:
                    return errs + [f"/ bei {vw}: .zw-lane--links oder .zw-lane--rechts fehlt"]
                seen_l += s["l"]["vis"]; seen_r += s["r"]["vis"]
                both += s["l"]["vis"] and s["r"]["vis"]
                single_gap += not (s["l"]["vis"] and s["r"]["vis"])
                tops.append(abs(s["l"]["top"] - s["r"]["top"]))
            if narrow:
                if both:
                    errs.append(f"/ bei {vw}: beide Spuren gleichzeitig sichtbar in {both} von 60 Stichproben")
                if not seen_l or not seen_r:
                    errs.append(f"/ bei {vw}: Spuren laufen nicht nacheinander (links {seen_l}x, rechts {seen_r}x sichtbar)")
            else:
                if single_gap:
                    errs.append(f"/ bei {vw}: in {single_gap} von 60 Stichproben nicht beide Spuren sichtbar")
                if max(tops) > 4:
                    errs.append(f"/ bei {vw}: Oberkanten der Spuren weichen bis {max(tops):.1f} px ab (> 4)")
        finally:
            ctx.close()
    return errs


def ak_r2_10_hero_height():
    """AK-R2-10: Hoehe .hero bei 390x844 <= Vorher-Wert (Baseline hero_390); Buehnenhoehe ueber 15 s konstant
    (390 und 1440)."""
    errs = []
    base = BASELINE.get("hero_390")
    if base is None:
        errs.append("keine Baseline (--baseline DIR mit hoehen.json): Vorher-Wert der Hero-Hoehe fehlt")
    ctx, pg = _open(390, 844, reduced="reduce", clock=False)
    try:
        h = pg.evaluate("() => { const e = document.querySelector('.hero'); return e ? Math.round(e.getBoundingClientRect().height) : null; }")
        if h is None:
            errs.append("/: .hero fehlt")
        elif base is not None and h > base:
            errs.append(f"/: .hero bei 390x844 {h} px > Vorher-Wert {base} px")
    finally:
        ctx.close()
    for vw in (390, 1440):
        ctx, pg = _open(vw, 900)
        try:
            if not _stage_to_view(pg):
                errs.append("/: .zw-stage fehlt (Buehne nicht gebaut)")
                break
            hs = []
            for _ in range(60):
                pg.clock.run_for(250)
                hs.append(pg.evaluate("() => document.querySelector('.zw-stage').getBoundingClientRect().height"))
            if max(hs) - min(hs) > 0.5:
                errs.append(f"/ bei {vw}: Buehnenhoehe aendert sich ueber 15 s ({min(hs):.1f} bis {max(hs):.1f} px)")
        finally:
            ctx.close()
    return errs


THREAD_JS = """() => { const t = document.querySelector('#it-betreuung [data-hero-chat] [data-hc-thread]'); return t ? t.innerHTML : null; }"""
PHONE_ANIMS_JS = """() => { const p = document.querySelector('#it-betreuung [data-hero-chat] .hc-phone'); if (!p) return null;
  const a = [p, ...p.querySelectorAll('*')].flatMap(e => e.getAnimations()); return { n: a.length, running: a.filter(x => x.playState === 'running').length }; }"""


def ak_r2_11_chat_below():
    """AK-R2-11: Chat in section#it-betreuung [data-hero-chat], keine dl.itb-list; erste Kundenblase auch ohne JS; ohne
    Scrollen 3 s keine Thread-Aenderung, ab >= 40 % Sichtbarkeit Start; Pause setzt [data-hero-chat].is-paused und alle
    Animationen im Handy stehen auf paused; Hoehe #it-betreuung <= Vorher-Wert."""
    errs = []
    sel = "section#it-betreuung [data-hero-chat]"
    # ohne JS
    ctx, pg = _open(390, 700, clock=False, js=False)
    try:
        r = pg.evaluate("""(sel) => { const c = document.querySelector(sel);
          const first = c ? c.querySelector('[data-hc-thread] .is-me') : null;
          return { chat: !!c, dl: !!document.querySelector('dl.itb-list'), itbList: !!document.querySelector('.itb-list'),
                   first: first ? first.textContent.trim().length : 0,
                   link: !!document.querySelector('#it-betreuung a[href="/ratgeber/server-ausgefallen/"]'),
                   heroChat: !!document.querySelector('.hero [data-hero-chat], .hero[data-hero-chat]') }; }""", sel)
        if not r["chat"]:
            return [f"/: {sel} fehlt (Chat nicht in #it-betreuung)"]
        if r["dl"] or r["itbList"]:
            errs.append("/: .itb-list (Typische Anrufe) steht noch auf der Seite")
        if not r["first"]:
            errs.append("/: erste Kundenblase fehlt im HTML (ohne JS)")
        if not r["link"]:
            errs.append("/: Link /ratgeber/server-ausgefallen/ fehlt in #it-betreuung")
        if r["heroChat"]:
            errs.append("/: [data-hero-chat] steht noch in .hero")
    finally:
        ctx.close()
    # Höhe
    ctx, pg = _open(390, 844, reduced="reduce", clock=False)
    try:
        h = pg.evaluate("() => { const e = document.getElementById('it-betreuung'); return e ? Math.round(e.getBoundingClientRect().height) : null; }")
        base = BASELINE.get("itb_390")
        if base is None:
            errs.append("keine Baseline (--baseline DIR mit hoehen.json): Vorher-Wert von #it-betreuung fehlt")
        elif h is None or h > base:
            errs.append(f"/: #it-betreuung bei 390x844 {h} px > Vorher-Wert {base} px")
    finally:
        ctx.close()
    # Ablauf
    ctx, pg = _open(390, 700)
    try:
        top = pg.evaluate("(sel) => { const c = document.querySelector(sel); return c ? c.getBoundingClientRect().top : null; }", sel)
        if top is None:
            return errs
        if top < 700:
            errs.append(f"/: Chat liegt bei 390x700 schon im Bild (Oberkante {top:.0f} px), Test 'ohne Scrollen' nicht aussagekraeftig")
        _run(pg, 500)
        a = pg.evaluate(THREAD_JS)
        _run(pg, 3000)
        if pg.evaluate(THREAD_JS) != a:
            errs.append("/: Thread aendert sich in 3 s, ohne dass der Chat im Bild ist")
        pg.evaluate("(sel) => document.querySelector(sel).scrollIntoView({ block: 'center' })", sel)
        pg.wait_for_timeout(300)
        changed, anim = False, False
        for _ in range(60):
            pg.clock.run_for(250)
            if pg.evaluate(THREAD_JS) != a:
                changed = True
            n = pg.evaluate(PHONE_ANIMS_JS)
            if n and n["running"]:
                anim = True
                break
        if not changed:
            errs.append("/: Chat startet nicht, obwohl er im Bild steht (15 s keine Thread-Aenderung)")
        if not anim:
            errs.append("/: keine laufende Animation im Chat-Handy gefunden (Pausentest nicht aussagekraeftig)")
        else:
            pg.click(sel + " [data-hc-pause]")
            pg.wait_for_timeout(200)
            paused = pg.evaluate("(sel) => document.querySelector(sel).classList.contains('is-paused')", sel)
            n = pg.evaluate(PHONE_ANIMS_JS)
            if not paused:
                errs.append("/: Pause-Klick setzt [data-hero-chat].is-paused nicht")
            if n and n["running"]:
                errs.append(f"/: nach Pause laufen noch {n['running']} Animationen im Handy (playState nicht 'paused')")
    finally:
        ctx.close()
    return errs


HERO_TEXT_JS = """() => { const eff = e => { let L = []; for (let n = e; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; L.push(c); if (/^rgb\\(/.test(c) || /, 1\\)$/.test(c)) break; } return L; };
  const hero = document.querySelector('.hero'); if (!hero) return null;
  const texts = [], w = document.createTreeWalker(hero, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const t = w.currentNode, e = t.parentElement;
    if (!t.textContent.trim() || e.closest('svg,script,style,[hidden]') || !e.getClientRects().length || !e.checkVisibility({ visibilityProperty: true })) continue;
    const c = getComputedStyle(e); let o = 1; for (let n = e; n; n = n.parentElement) o *= parseFloat(getComputedStyle(n).opacity);
    if (o < 0.5) continue;
    texts.push({ txt: t.textContent.trim().slice(0, 28), color: c.color, bg: eff(e), size: parseFloat(c.fontSize), weight: parseInt(c.fontWeight, 10) || 400,
                 el: e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : '') }); }
  const b = document.querySelector('button.zw-pause'); let pause = null;
  if (b) { const ic = b.querySelector('svg path, svg line, svg circle, svg'); const s = ic ? getComputedStyle(ic) : null;
    pause = { color: getComputedStyle(b).color, stroke: s ? s.stroke : null, fill: s ? s.fill : null, border: getComputedStyle(b).borderTopColor,
              borderW: parseFloat(getComputedStyle(b).borderTopWidth), bg: eff(b), parentBg: eff(b.parentElement) }; }
  const left = []; const lane = document.querySelector('.zw-lane--links');
  if (lane) for (const e of [lane, ...lane.querySelectorAll('*')]) { const c = getComputedStyle(e);
    left.push({ el: e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : ''),
                v: [c.color, c.backgroundColor, c.borderTopColor, c.outlineColor, c.stroke, c.fill] }); }
  return { texts, pause, left }; }"""

DANGER_WARN = [(192, 57, 43), (239, 68, 68), (192, 0, 0), (204, 136, 0), (245, 158, 11), (180, 83, 9), (146, 64, 14), (255, 242, 204),
               (253, 236, 234)]


def _flat(layers):
    base = (0.0, 0.0, 0.0)
    for c in reversed(layers):
        a = rgba(c) or (0, 0, 0, 0)
        base = tuple(a[i] * a[3] + base[i] * (1 - a[3]) for i in range(3))
    return base


def _over(fg, bg):
    a = rgba(fg)
    if a is None or a[3] == 0:
        return None
    return tuple(a[i] * a[3] + bg[i] * (1 - a[3]) for i in range(3))


def _is_alarm(c):
    """True fuer die CI-Farben Danger/Warning und rote oder orange Toene (Farbton 0-50 Grad, kraeftig)."""
    a = rgba(c)
    if a is None or a[3] < 0.3:
        return False
    rgb = tuple(round(v) for v in a[:3])
    if rgb in DANGER_WARN:
        return True
    r, g, b = (v / 255 for v in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 0.25 or mx < 0.35:
        return False
    if mx == r:
        h = (60 * ((g - b) / (mx - mn))) % 360
    else:
        return False
    return h <= 50 or h >= 345


def ak_r2_16_contrast():
    """AK-R2-16: Kontrast in .hero >= 4,5:1 (grosse Schrift >= 3:1) bei 390 und 1440 im Endstand; Pause-Knopf >= 3:1;
    die linke Spur nutzt keine Danger-/Warning-Farben."""
    errs = []
    for vw in (390, 1440):
        ctx, pg = _open(vw, 900, reduced="reduce", clock=False)
        try:
            r = pg.evaluate(HERO_TEXT_JS)
        finally:
            ctx.close()
        if r is None:
            return ["/: .hero fehlt"]
        if not r["texts"]:
            errs.append(f"/ bei {vw}: .hero ohne sichtbare Textknoten")
        bad = []
        for t in r["texts"]:
            fg, bg = rgba(t["color"]), _flat(t["bg"])
            if fg is None:
                continue
            fgc = tuple(fg[i] * fg[3] + bg[i] * (1 - fg[3]) for i in range(3))
            need = 3.0 if (t["size"] >= 24 or (t["size"] >= 18.66 and t["weight"] >= 700)) else 4.5
            c = contrast(fgc, bg)
            if c < need:
                bad.append(f"{t['el']} '{t['txt']}' {c:.1f}:1 (soll >= {need})")
        if bad:
            errs.append(f"/ bei {vw}: {len(bad)} Textknoten in .hero unter Soll-Kontrast, z. B. {'; '.join(bad[:4])}")
        p = r["pause"]
        if p is None:
            errs.append(f"/ bei {vw}: button.zw-pause fehlt (Kontrast nicht pruefbar)")
        else:
            bg = _flat(p["bg"])
            cand = []
            for col in (p["stroke"], p["fill"], p["color"]):
                c = _over(col, bg) if col else None
                if c:
                    cand.append(contrast(c, bg))
            if p["borderW"] > 0:
                c = _over(p["border"], _flat(p["parentBg"]))
                if c:
                    cand.append(contrast(c, _flat(p["parentBg"])))
            if not cand or max(cand) < 3.0:
                errs.append(f"/ bei {vw}: Pause-Knopf Kontrast {max(cand) if cand else 0:.1f}:1 < 3:1")
        if vw == 1440:
            if not r["left"]:
                errs.append("/: .zw-lane--links fehlt (Farbpruefung nicht moeglich)")
            alarm = sorted({f"{e['el']} {v}" for e in r["left"] for v in e["v"] if _is_alarm(v)})
            if alarm:
                errs.append(f"/: linke Spur nutzt Danger-/Warning-Toene: {'; '.join(alarm[:4])}")
    return errs


def test_hidden_tab_pauses():
    """Spec §5.8: Tab im Hintergrund (document.hidden) haelt die Buehne an; sichtbar laeuft sie weiter."""
    errs = []
    ctx, pg = _open(1440, 900)
    try:
        if not _stage_to_view(pg):
            return ["/: .zw-stage fehlt (Buehne nicht gebaut)"]
        _run(pg, 2000)
        set_vis = """(h) => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => h });
          Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => h ? 'hidden' : 'visible' });
          document.dispatchEvent(new Event('visibilitychange')); }"""
        pg.evaluate(set_vis, True)
        _settle(pg)
        a = pg.evaluate(STAGE_SNAP)
        _run(pg, 8000)
        _settle(pg, 150)
        if pg.evaluate(STAGE_SNAP) != a:
            errs.append("/: bei document.hidden laeuft die Buehne weiter (DOM/transform/opacity aendern sich in 8 s)")
        pg.evaluate(set_vis, False)
        _settle(pg, 150)
        b = pg.evaluate(STAGE_SNAP)
        _run(pg, 10000)
        _settle(pg, 150)
        if pg.evaluate(STAGE_SNAP) == b:
            errs.append("/: nach Rueckkehr in den Vordergrund laeuft die Buehne nicht weiter")
    finally:
        ctx.close()
    return errs


AK_R2 = {
    "R2-06": ak_r2_06_pause, "R2-07": ak_r2_07_reduced_motion, "R2-08": ak_r2_08_text_alternative,
    "R2-09": ak_r2_09_lanes, "R2-10": ak_r2_10_hero_height, "R2-11": ak_r2_11_chat_below,
    "R2-16": ak_r2_16_contrast, "R2-FOKUS": test_no_focusable_in_aria_hidden, "R2-TAB": test_hidden_tab_pauses,
}
RELEASES = {"r1": AK_R1, "r2": AK_R2}
# Nicht hier: AK-R2-01..05, 18, 21 (check_static AKH, AK8, AK13), AK-R2-12 (check_site), AK-R2-13 (check_seo),
# AK-R2-14/15 (Trace und Lighthouse per MCP), AK-R2-17 (AK14r), AK-R2-19/20 (Abnahme, Live).


def run_release(release, only=None, baseline=None):
    table = RELEASES.get(release)
    if table is None:
        print(f"Unbekannter Release '{release}' (vorhanden: {', '.join(RELEASES)})"); return 2
    if baseline:
        BASELINE.update(json.loads((Path(baseline) / "hoehen.json").read_text(encoding="utf-8")))
    keys = list(table)
    if only:
        unknown = [k for k in only if k not in table and k != "HOEHEN"]
        if unknown:
            print(f"Unbekannte AK(s): {', '.join(unknown)}; vorhanden: {', '.join(table)}, HOEHEN"); return 2
        keys = [k for k in keys if k in only]
    bad = 0
    try:
        for k in keys:
            errs = table[k]()
            print(f"AK-{k}: {'OK' if not errs else 'FEHLER (' + str(len(errs)) + ')'}")
            for e in errs[:30]:
                print("    ", e)
            bad += len(errs)
    finally:
        close_env()
    if baseline and (not only or "HOEHEN" in only):
        print("HOEHEN (gegen Baseline):")
        bad += heights(baseline)
    print(f"{len(keys)} Kriterien, {'FEHLER' if bad else 'alles OK'}")
    return 1 if bad else 0


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


if __name__ == "__main__":
    if "--measure-baseline" in sys.argv:
        sys.exit(measure_baseline(arg("--measure-baseline")))
    if "--heights" in sys.argv:
        if not arg("--baseline"):
            print("--heights braucht --baseline DIR"); sys.exit(2)
        sys.exit(heights(arg("--baseline")))
    if "--release" in sys.argv:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        only = arg("--only")
        sys.exit(run_release(arg("--release"), only.split(",") if only else None, arg("--baseline")))
    print(__doc__); sys.exit(2)
