"""Browser-Messungen (Spec §9: AK3, AK4, AK5, AK6, AK12, Anker, ohne JS).
Aufruf: PY313 tools/checks/check_site.py [--out DIR] [--pages /,/kontakt/]"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
import serve
from check_static import pages, kuemmerer_pages, legal_pages, rel, ROOT

LIMIT_HOME, LIMIT_SUB = 12000, 8000
WIDTHS = [320, 390, 768, 1024, 1440]
HOME_ANCHORS = ["referenzen", "it-betreuung", "schnellcheck", "ablauf", "ki", "websites", "leistungen", "praxis",
                "schulung", "preise", "faq", "einsatzgebiet", "kontakt", "bewertungen-herkunft"]


def url_of(p):
    r = rel(p)
    return "/" if r == "index.html" else "/" + r.replace("index.html", "")


MEASURE = """() => {
  const fs = el => el ? parseFloat(getComputedStyle(el).fontSize) : 0;
  const body = [...document.querySelectorAll('main p, main li, main dd, .faq-a')].filter(e => e.closest('nav,footer,.lp-crumbs') === null);
  const sizes = body.map(fs).filter(x => x > 0).sort((a,b)=>a-b);
  const btn = document.querySelector('main .btn-p');
  const cyan = [...document.querySelectorAll('main a, main button')].filter(e => {
    const c = getComputedStyle(e), r = e.getBoundingClientRect();
    return c.backgroundColor === 'rgb(38, 189, 239)' && r.height >= 40; }).length;
  const vis = sel => { const e = document.querySelector(sel); if (!e) return false;
    const r = e.getBoundingClientRect(); return r.height > 0 && r.top < innerHeight && r.bottom > 0; };
  // Beleg (AK6): nur sichtbar, wenn er ganz ueber der Kontaktleiste endet, sofern die Leiste unten quer liegt
  // (Handy/Tablet); am Desktop steht sie rechts am Rand und verdeckt den Kopf nicht.
  const bar = document.querySelector('.sticky-contact'), br = bar ? bar.getBoundingClientRect() : null;
  const barTop = br && br.height > 0 && br.width >= innerWidth - 1 && br.top < innerHeight ? br.top : innerHeight;
  const visAbove = sel => { const e = document.querySelector(sel); if (!e) return false;
    const r = e.getBoundingClientRect(); return r.height > 0 && r.top >= 0 && r.bottom <= barTop; };
  const top = id => { const e = document.getElementById(id); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null; };
  return { height: document.documentElement.scrollHeight, overflow: document.documentElement.scrollWidth > innerWidth + 1,
    h1: fs(document.querySelector('h1')), stitle: fs(document.querySelector('main .s-title')),
    p_median: sizes.length ? sizes[Math.floor(sizes.length/2)] : 0,
    btn_bg: btn ? getComputedStyle(btn).backgroundColor : null, cyan_buttons: cyan,
    first: { h1: vis('h1'), k: vis('.page-k'), contact: vis('.sticky-contact') || vis('main a[href^="tel:"]'), proof: visAbove('[data-proof]') },
    schnellcheck_top: top('schnellcheck'), preise_top: top('preise') };
}"""


def run(out_dir, only=None):
    srv, base = serve.start()
    res, fails = {}, []
    kp = {url_of(p) for p in kuemmerer_pages()}
    lp = {url_of(p) for p in legal_pages()}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in pages():
            u = url_of(p)
            if only and u not in only:
                continue
            r = res[u] = {}
            for w in WIDTHS:
                ctx = b.new_context(viewport={"width": w, "height": 900}, service_workers="block", reduced_motion="reduce")
                pg = ctx.new_page(); pg.goto(base + u, wait_until="networkidle")
                r[w] = pg.evaluate(MEASURE)
                if out_dir and w in (390, 1440):
                    pg.screenshot(path=str(Path(out_dir) / f"{u.strip('/').replace('/', '_') or 'start'}_{w}.png"))
                ctx.close()
            ctx = b.new_context(viewport={"width": 390, "height": 700}, service_workers="block", reduced_motion="reduce")
            pg = ctx.new_page(); pg.goto(base + u, wait_until="networkidle")
            r["first700"] = pg.evaluate(MEASURE)["first"]
            if u == "/":
                r["anchors"] = {}
                for a in HOME_ANCHORS:
                    pg.goto(base + "/#" + a, wait_until="networkidle")
                    r["anchors"][a] = pg.evaluate("id => { const e = document.getElementById(id); if (!e) return 'fehlt'; "
                                                  "if (e.closest('details:not([open])')) return 'zugeklappt'; "
                                                  "const r = e.getBoundingClientRect(); return (r.top < innerHeight && r.bottom > 0) ? 'ok' : 'nicht im Bild'; }", a)
            ctx.close()
            nojs = b.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
            pg = nojs.new_page(); pg.goto(base + u)
            r["nojs_footer_links"] = pg.evaluate("() => [...document.querySelectorAll('footer a')].filter(a => a.getBoundingClientRect().height > 0).length")
            r["nojs_legal_links"] = pg.evaluate("() => [...document.querySelectorAll('footer a[href=\"/impressum/\"], footer a[href=\"/datenschutz/\"]')].filter(a => a.getBoundingClientRect().height > 0).length")
            nojs.close()
            m390, m1440 = r[390], r[1440]
            if u not in lp:
                lim = LIMIT_HOME if u == "/" else LIMIT_SUB
                if m390["height"] > lim: fails.append(f"{u}: Laenge {m390['height']} > {lim} (AK5)")
                if m390["p_median"] < 16: fails.append(f"{u}: Fliesstext-Median {m390['p_median']} px (AK4)")
                if m1440["stitle"] and m1440["stitle"] < 28: fails.append(f"{u}: s-title {m1440['stitle']} px (AK4)")
            if u == "/":
                if (m390["schnellcheck_top"] or 99999) > 4000: fails.append(f"/: #schnellcheck bei {m390['schnellcheck_top']} (AK5)")
                if (m390["preise_top"] or 99999) > 5000: fails.append(f"/: #preise bei {m390['preise_top']} (AK5)")
                bad = {k: v for k, v in r["anchors"].items() if v != "ok"}
                if bad: fails.append(f"/: Anker {bad} (AK14)")
            if any(r[w]["overflow"] for w in WIDTHS): fails.append(f"{u}: horizontaler Ueberlauf (AK12)")
            # #0000FE = Visitenkarten-Blau (CI, Haupt-Knopf)
            if m390["btn_bg"] not in (None, "rgb(0, 0, 254)"): fails.append(f"{u}: btn-p {m390['btn_bg']} (AK3)")
            if m1440["cyan_buttons"]: fails.append(f"{u}: {m1440['cyan_buttons']} Cyan-Hauptknoepfe (AK3)")
            if u != "/" and u not in lp and (m390["h1"] < 35 or m1440["h1"] < 48): fails.append(f"{u}: h1 {m390['h1']}/{m1440['h1']} px (AK4)")
            if u in kp and not all(r["first700"].values()): fails.append(f"{u}: erster Bildschirm {r['first700']} (AK6)")
            if r["nojs_footer_links"] < 30 or r["nojs_legal_links"] < 2: fails.append(f"{u}: Fuss ohne JS nicht lesbar")
        b.close()
    srv.shutdown()
    if out_dir:
        (Path(out_dir) / "messung.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for f in fails:
        print("FEHLER", f)
    print(f"{len(res)} Seiten, {len(fails)} Fehler")
    return 1 if fails else 0


if __name__ == "__main__":
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    if out: Path(out).mkdir(parents=True, exist_ok=True)
    only = sys.argv[sys.argv.index("--pages") + 1].split(",") if "--pages" in sys.argv else None
    sys.exit(run(out, only))
