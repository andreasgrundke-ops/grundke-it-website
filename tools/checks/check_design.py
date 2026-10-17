"""Design-Pruefungen fuer den Relaunch (Spec §5, §7, §11).
Titel:        check_design.py
Version:      0.1.0 (Task 0: Baseline-Modi; AK-Funktionen folgen in Task 1)
Datum:        17.10.2026
Beschreibung: Misst Hoehen bei 390x844 (reduzierte Bewegung, Service Worker blockiert) und vergleicht sie
              spaeter mit einer gespeicherten Baseline. Die AK-Pruefungen (--release r1, --only ...) werden
              in diese Datei ergaenzt (AK_CHECKS).
Aufruf:       PY313 tools/checks/check_design.py --measure-baseline DIR
              PY313 tools/checks/check_design.py --heights --baseline DIR
Ablauf:       1. serve.py startet den lokalen Static-Server (127.0.0.1, freier Port).
              2. Fuer jede Seite aus check_static.pages() bei 390x844 messen.
              3. --measure-baseline: DIR/hoehen.json schreiben.
              4. --heights: je Seite gegen DIR/hoehen.json vergleichen, Abweichung in px und %;
                 ueber +5 % WARNUNG, ueber Budget FEHLER; Exit 1 nur bei Fehlern."""
import json, sys
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


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


if __name__ == "__main__":
    if "--measure-baseline" in sys.argv:
        sys.exit(measure_baseline(arg("--measure-baseline")))
    if "--heights" in sys.argv:
        if not arg("--baseline"):
            print("--heights braucht --baseline DIR"); sys.exit(2)
        sys.exit(heights(arg("--baseline")))
    print(__doc__); sys.exit(2)
