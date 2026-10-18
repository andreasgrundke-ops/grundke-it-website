"""Service-Worker-Pruefung im echten Browser (Spec AK-R1-15).
Titel:   check_sw.py - Routing und Upgrade des Service Workers
Version: 1.0.0
Autor:   Andreas Grundke / Grundke IT-Service
Datum:   2026-10-17
Aufruf:  PY313 tools/checks/check_sw.py [--upgrade]   Exit 1 bei Fehler.

Ablauf:
  1. Lokaler Server (Repo-Root, nur 127.0.0.1, no-store); /sw.js laesst sich fuer den Upgrade-Test austauschen.
  2. Chromium mit service_workers="allow" (Ausnahme zu den anderen Pruefungen), Startseite laden,
     /sw.js registrieren, auf den Controller warten, alle Caches leeren.
  3. Routing-Tests: Range-Anfrage, Medien-Destination (video, track) und Medien-Endung gehen am
     Service Worker vorbei (from_service_worker False) und landen in keinem Cache; ein normales
     Asset kommt beim zweiten Abruf aus dem Service Worker.
  4. --upgrade: zuerst die sw.js aus GIT_OLD_REF ausliefern und registrieren, dann die aktuelle;
     nach dem Wechsel laedt die Seite style.css?v=<neu>, keine Antwort ist 404, es bleiben nur die
     neuen Caches. Haben alte und neue sw.js dieselbe CACHE_NAME, meldet der Test SKIP.

Aenderungshistorie:
  1.0.0 / 2026-10-17 - erste Fassung (Range, Medien, Endung, Assets, Upgrade)
"""
import re, socketserver, subprocess, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
import serve

ROOT = serve.ROOT
GIT_OLD_REF = "stand-vor-relaunch-2026-10-17"
SETTLE_MS = 800      # Zeit fuer ein evtl. asynchrones cache.put, bevor "kein Eintrag" geprueft wird
WAIT_MS = 8000       # Obergrenze fuer erwartete Antworten und Cache-Eintraege

REGISTER = """async () => {
  await navigator.serviceWorker.register('/sw.js', { scope: '/' });
  if (!navigator.serviceWorker.controller)
    await new Promise(r => navigator.serviceWorker.addEventListener('controllerchange', r, { once: true }));
  return navigator.serviceWorker.controller.scriptURL;
}"""
CLEAR = "async () => { for (const k of await caches.keys()) await caches.delete(k); }"
FIND = """async u => { for (const k of await caches.keys()) {
  if (await (await caches.open(k)).match(u)) return k; } return null; }"""
FETCH = "async ([u, h]) => (await fetch(u, { headers: h || {} })).status"
KEYS = "async () => await caches.keys()"


def sw_const(src, name):
    m = re.search(r"const " + name + r"\s*=\s*'([^']+)'", src)
    return m.group(1) if m else None


class _Handler(serve._Quiet):
    """Wie serve.py, nur /sw.js kann durch einen anderen Inhalt ersetzt werden (Upgrade-Test)."""
    sw_body = None

    def do_GET(self):
        if self.path.split("?")[0] == "/sw.js" and _Handler.sw_body is not None:
            body = _Handler.sw_body
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def start_server():
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), lambda *a: _Handler(*a, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def controlled_page(browser, base):
    """Neue Seite, deren Startseite vom Service Worker kontrolliert wird; Caches leer."""
    ctx = browser.new_context(service_workers="allow", reduced_motion="reduce")
    pg = ctx.new_page()
    pg.goto(base + "/", wait_until="networkidle")
    pg.evaluate(REGISTER)
    pg.reload(wait_until="networkidle")
    pg.wait_for_timeout(SETTLE_MS)
    pg.evaluate(CLEAR)
    return ctx, pg


def response_for(pg, path, action):
    """Fuehrt action aus und liefert die Antwort, deren URL auf path endet."""
    with pg.expect_response(lambda r: r.url.endswith(path), timeout=WAIT_MS) as info:
        action()
    return info.value


def bypass_check(pg, path, action, what):
    """Gemeinsame Pruefung: nicht vom Service Worker beantwortet, danach in keinem Cache."""
    errs = []
    try:
        res = response_for(pg, path, action)
    except Exception as e:
        return [f"{what}: keine Antwort fuer {path} ({type(e).__name__})"]
    if res.from_service_worker:
        errs.append(f"{what}: {path} kam vom Service Worker (soll am SW vorbei)")
    pg.wait_for_timeout(SETTLE_MS)
    hit = pg.evaluate(FIND, path)
    if hit:
        errs.append(f"{what}: {path} liegt im Cache {hit}")
    return errs


def test_range_bypasses_sw(pg):
    path = "/assets/img/qr-tree.png?t=range"
    return bypass_check(pg, path, lambda: pg.evaluate(FETCH, [path, {"Range": "bytes=0-99"}]), "Range")


def test_media_not_cached(pg):
    vpath = "/assets/img/og-image.png?t=video"
    errs = bypass_check(pg, vpath, lambda: pg.evaluate(
        """u => { const v = document.createElement('video'); v.preload = 'auto'; v.muted = true;
                  v.src = u; document.body.appendChild(v); }""", vpath), "Medien (video)")
    tpath = "/assets/img/wa-qr-code.png?t=track"
    errs += bypass_check(pg, tpath, lambda: pg.evaluate(
        """u => { const v = document.createElement('video'); const t = document.createElement('track');
                  t.kind = 'subtitles'; t.srclang = 'de'; t.default = true; t.src = u; v.appendChild(t);
                  document.body.appendChild(v); t.track.mode = 'hidden'; }""", tpath), "Medien (track)")
    return errs


def test_media_ext_bypasses_sw(pg):
    errs = []
    for path in ("/x.vtt", "/x.mp4"):
        errs += bypass_check(pg, path, lambda p=path: pg.evaluate(FETCH, [p, None]), "Endung")
    return errs


def test_assets_cache_first(pg, asset_ver):
    path = "/assets/js/main.js?v=" + asset_ver
    first = response_for(pg, path, lambda: pg.evaluate(FETCH, [path, None]))
    if first.status != 200:
        return [f"Assets: {path} Status {first.status}"]
    for _ in range(WAIT_MS // 200):
        if pg.evaluate(FIND, path):
            break
        pg.wait_for_timeout(200)
    else:
        return [f"Assets: {path} nach dem ersten Abruf in keinem Cache"]
    second = response_for(pg, path, lambda: pg.evaluate(FETCH, [path, None]))
    return [] if second.from_service_worker else [f"Assets: {path} kam beim zweiten Abruf nicht aus dem Service Worker"]


def test_upgrade_no_mixed_state(browser, base, new_src):
    """Alte sw.js (GIT_OLD_REF) aktiv, dann Wechsel auf die aktuelle: kein Mischstand. Rueckgabe (status, fehler)."""
    try:
        old_src = subprocess.run(["git", "show", GIT_OLD_REF + ":sw.js"], cwd=ROOT, capture_output=True,
                                 check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        return "FEHLER", [f"Upgrade: alte sw.js aus {GIT_OLD_REF} nicht lesbar ({e})"]
    old_txt = old_src.decode("utf-8")
    old_cache, new_cache = sw_const(old_txt, "CACHE_NAME"), sw_const(new_src, "CACHE_NAME")
    if old_cache == new_cache:
        return "SKIP", [f"Upgrade: CACHE_NAME {new_cache} unveraendert gegenueber {GIT_OLD_REF}"]
    new_ver = sw_const(new_src, "ASSET_VER")
    new_keep = {new_cache, sw_const(new_src, "RUNTIME_CACHE")}
    errs = []
    ctx = browser.new_context(service_workers="allow", reduced_motion="reduce")
    pg = ctx.new_page()
    try:
        _Handler.sw_body = old_src
        pg.goto(base + "/", wait_until="networkidle")
        pg.evaluate(REGISTER)
        if old_cache not in pg.evaluate(KEYS):
            return "FEHLER", [f"Upgrade: alter Service Worker ohne Cache {old_cache} (Install gescheitert?)"]
        _Handler.sw_body = None
        pg.evaluate("""async () => {
          const reg = await navigator.serviceWorker.getRegistration('/');
          const changed = new Promise(r => navigator.serviceWorker.addEventListener('controllerchange', r, { once: true }));
          await reg.update();
          await changed;
        }""")
        bad = []
        pg.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)
        seen = []
        pg.on("response", lambda r: seen.append(r) if "/assets/css/style.css" in r.url else None)
        pg.reload(wait_until="networkidle")
        pg.wait_for_timeout(SETTLE_MS)
        errs += [f"Upgrade: Antwort {b}" for b in bad]
        want = "/assets/css/style.css?v=" + str(new_ver)
        if not any(r.url.endswith(want) and r.status == 200 for r in seen):
            errs.append(f"Upgrade: {want} nicht mit 200 geladen ({[f'{r.status} {r.url}' for r in seen]})")
        href = pg.evaluate("() => [...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.href)"
                           ".filter(h => h.includes('/assets/css/style.css'))")
        if not href or not all(h.endswith(want) for h in href):
            errs.append(f"Upgrade: Seite verweist auf {href}, erwartet {want}")
        script = pg.evaluate("() => navigator.serviceWorker.controller && navigator.serviceWorker.controller.scriptURL")
        if not script:
            errs.append("Upgrade: Seite nach dem Wechsel ohne Service Worker")
        left = set(pg.evaluate(KEYS)) - new_keep
        if left:
            errs.append(f"Upgrade: alte Caches nicht entfernt: {sorted(left)}")
    finally:
        _Handler.sw_body = None
        ctx.close()
    return ("FEHLER" if errs else "OK"), errs


def main(argv):
    sw_src = (ROOT / "sw.js").read_text(encoding="utf-8")
    asset_ver = sw_const(sw_src, "ASSET_VER")
    srv, base = start_server()
    results = []
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            ctx, pg = controlled_page(b, base)
            for name, fn in (("Range", lambda: test_range_bypasses_sw(pg)),
                             ("Medien", lambda: test_media_not_cached(pg)),
                             ("Endung", lambda: test_media_ext_bypasses_sw(pg)),
                             ("Assets", lambda: test_assets_cache_first(pg, asset_ver))):
                errs = fn()
                results.append((name, "FEHLER" if errs else "OK", errs))
            ctx.close()
            if "--upgrade" in argv:
                status, errs = test_upgrade_no_mixed_state(b, base, sw_src)
                results.append(("Upgrade", status, errs))
            b.close()
    finally:
        srv.shutdown()
    for name, status, errs in results:
        print(f"{name}: {status}")
        for e in errs:
            print("   ", e)
    fails = sum(1 for _, s, _ in results if s == "FEHLER")
    print(f"{len(results)} Tests, {fails} Fehler")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
