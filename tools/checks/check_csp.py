"""CSP-Pruefung im echten Browser (Spec Hosting/Security-Header 08.11.2026, AK2).
Titel:   check_csp.py - keine CSP-Verstoesse, Film, Hero-Chat, Service Worker
Version: 1.0.0
Autor:   Andreas Grundke / Grundke IT-Service
Datum:   2026-11-08
Aufruf:  PY313 tools/checks/check_csp.py --local              lokaler Pruefserver mit derselben CSP wie der Server
         PY313 tools/checks/check_csp.py --base https://grundke-it.de
         Exit 1 bei Fehler.

Ablauf:
  1. --local: Pruefserver (nur 127.0.0.1, aufgerufen als http://localhost:<port>, damit der Service Worker
     registriert) liefert das Repo aus wie nginx: /pfad -> 301 /pfad/, 404-Seite mit Status 404, Range (206),
     interne Pfade 404, dazu die Security-Header aus CSP/HEADERS unten (gleicher Wortlaut wie das Caddy-Snippet).
  2. Jede URL aus sitemap.xml plus /tree/, /ki-arbeitsplatz-onboarding-kit/, /404.html laden; Verstoesse kommen
     aus der Konsole ("Refused to ...", "Content Security Policy") und aus dem Ereignis securitypolicyviolation.
  3. Startseite: Film-Fassade anklicken -> <video> laedt eine .mp4 (Status 200/206, readyState >= 1, wenn der
     Browser H.264 kann); Hero-Chat bekommt neue Nachrichten; Service Worker ist aktiv.
  Browser: installiertes Chrome (channel "chrome", kann H.264), sonst Playwright-Chromium; dort wird beim Film
  nur die Anfrage geprueft und das Ergebnis als HINWEIS gekennzeichnet.
"""
import argparse, mimetypes, re, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
# Muss wortgleich zum Caddy-Snippet sein (liegt ausserhalb des Repos, siehe CADDY_SNIPPET).
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "font-src 'self'; media-src 'self'; connect-src 'self'; worker-src 'self'; manifest-src 'self'; "
       "frame-ancestors 'none'; base-uri 'self'; form-action 'self' mailto:; object-src 'none'; "
       "upgrade-insecure-requests")
HEADERS = {
    "Content-Security-Policy": CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}
CADDY_SNIPPET = ROOT.parent / "_intern" / "vps" / "grundke-it-web" / "grundke-it-website.caddy"
EXTRA_PAGES = ["/tree/", "/ki-arbeitsplatz-onboarding-kit/", "/404.html"]
BLOCKED = re.compile(r"^/(tools|docs|\.git|\.github|\.impeccable|Audit 2026-04)(/|$)|/\.|^/[^/]+\.md$|\.py$")
TYPES = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
         ".css": "text/css; charset=utf-8", ".json": "application/json", ".webmanifest": "application/manifest+json",
         ".vtt": "text/vtt; charset=utf-8", ".woff2": "font/woff2", ".svg": "image/svg+xml", ".png": "image/png",
         ".jpg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif", ".ico": "image/x-icon",
         ".mp4": "video/mp4", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8", ".zip": "application/zip",
         ".md": "text/markdown; charset=utf-8"}
WAIT_MS = 15000
SPY = """(() => { window.__csp = [];
  document.addEventListener('securitypolicyviolation', e =>
    window.__csp.push(e.violatedDirective + ' ' + (e.blockedURI || '(inline)') + ' @' + e.sourceFile + ':' + e.lineNumber));
})();"""


class Handler(BaseHTTPRequestHandler):
    """Statische Auslieferung wie nginx (siehe nginx.conf ausserhalb des Repos), mit den Headern von Caddy."""

    def log_message(self, *a):
        pass

    def _head(self, status, ctype=None, length=None, extra=None):
        self.send_response(status)
        for k, v in {**HEADERS, **(extra or {})}.items():
            self.send_header(k, v)
        if ctype:
            self.send_header("Content-Type", ctype)
        if length is not None:
            self.send_header("Content-Length", str(length))
        self.end_headers()

    def _not_found(self):
        body = (ROOT / "404.html").read_bytes()
        self._head(404, TYPES[".html"], len(body))
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if BLOCKED.search(path) or ".." in path:
            return self._not_found()
        fs = ROOT / path.lstrip("/")
        if fs.is_dir():
            if not path.endswith("/"):
                self._head(301, extra={"Location": path + "/"}, length=0)
                return
            fs = fs / "index.html"
        if not fs.is_file():
            return self._not_found()
        data = fs.read_bytes()
        ctype = TYPES.get(fs.suffix.lower()) or mimetypes.guess_type(fs.name)[0] or "application/octet-stream"
        cache = "no-cache" if path in ("/sw.js", "/site.webmanifest") else "no-store"
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if m and (m.group(1) or m.group(2)):
            size = len(data)
            start = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2)))
            end = min(int(m.group(2)), size - 1) if m.group(1) and m.group(2) else size - 1
            part = data[start:end + 1]
            self._head(206, ctype, len(part), {"Content-Range": f"bytes {start}-{end}/{size}",
                                               "Accept-Ranges": "bytes", "Cache-Control": cache})
            if self.command != "HEAD":
                self.wfile.write(part)
            return
        self._head(200, ctype, len(data), {"Accept-Ranges": "bytes", "Cache-Control": cache})
        if self.command != "HEAD":
            try:
                self.wfile.write(data)
            except (ConnectionResetError, BrokenPipeError):
                pass


def start_local():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://localhost:{srv.server_address[1]}"


def snippet_matches():
    """None, wenn das Caddy-Snippet nicht da ist (z. B. in der Action), sonst True/False (CSP wortgleich)."""
    if not CADDY_SNIPPET.exists():
        return None
    m = re.search(r'Content-Security-Policy\s+"([^"]+)"', CADDY_SNIPPET.read_text(encoding="utf-8"))
    return bool(m) and m.group(1) == CSP


def page_paths():
    xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    paths = [urlsplit(u).path or "/" for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)]
    return list(dict.fromkeys(paths + EXTRA_PAGES))


def launch(pw):
    try:
        return pw.chromium.launch(channel="chrome"), True
    except Exception:
        return pw.chromium.launch(), False


def watch(page, sink):
    page.add_init_script(SPY)
    page.on("console", lambda m: sink.append(f"Konsole: {m.text[:300]}")
            if ("Refused to" in m.text or "Content Security Policy" in m.text) else None)


def collect(page, sink):
    try:
        sink += [f"Ereignis: {v}" for v in page.evaluate("window.__csp || []")]
    except Exception:
        pass


def check_pages(b, base):
    errs = []
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, service_workers="block")
    for p in page_paths():
        pg, hits = ctx.new_page(), []
        watch(pg, hits)
        r = pg.goto(base + p, wait_until="networkidle")
        pg.mouse.wheel(0, 20000)
        pg.wait_for_timeout(400)
        collect(pg, hits)
        if r is None or r.status != 200:   # /404.html direkt aufgerufen ist 200 (wie bei nginx und Pages)
            errs.append(f"{p}: Status {r.status if r else 'keine Antwort'}")
        errs += [f"{p}: {h}" for h in dict.fromkeys(hits)]
        pg.close()
    ctx.close()
    return errs, len(page_paths())


def check_home(b, base, h264):
    errs, notes = [], []
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, service_workers="allow")
    pg, hits = ctx.new_page(), []
    watch(pg, hits)
    mp4 = []
    pg.on("response", lambda r: mp4.append(r.status) if r.url.split("?")[0].endswith(".mp4") else None)
    pg.goto(base + "/", wait_until="networkidle")

    # Hero-Chat: es kommen Nachrichten zur ersten (statischen) hinzu
    n0 = pg.locator("[data-hero-chat] [data-hc-thread] > *").count()
    try:
        # Funktion statt Ausdruck: einen Ausdruck wertet Playwright per eval aus, das die CSP (richtig) sperrt
        pg.wait_for_function("n => document.querySelectorAll('[data-hero-chat] [data-hc-thread] > *').length > n",
                             arg=n0, timeout=WAIT_MS)
    except Exception:
        errs.append(f"Hero-Chat: nach {WAIT_MS} ms keine neue Nachricht (Start {n0})")

    # Service Worker aktiv
    try:
        state = pg.evaluate("""() => Promise.race([
            navigator.serviceWorker.ready.then(r => r.active ? r.active.state : 'ohne active'),
            new Promise(res => setTimeout(() => res('Zeitlimit'), 10000))])""")
        if state not in ("activated", "activating"):
            errs.append(f"Service Worker: {state}")
    except Exception as e:
        errs.append(f"Service Worker: {e}")

    # Film: Fassade anklicken
    # main.js ersetzt den Link a.film-start durch einen gleichnamigen Knopf; bleibt der Link, lief main.js nicht
    link = pg.locator("[data-film] button.film-start")
    if link.count() != 1:
        errs.append("Film: Knopf [data-film] button.film-start fehlt (main.js nicht gelaufen?)")
    else:
        link.scroll_into_view_if_needed()
        link.click()
        try:
            pg.wait_for_selector("[data-film] video", timeout=WAIT_MS)
            pg.wait_for_function("() => { const v = document.querySelector('[data-film] video'); "
                                 "return v && (v.readyState >= 1 || v.error); }", timeout=WAIT_MS)
            ready, err = pg.evaluate("() => { const v = document.querySelector('[data-film] video'); "
                                     "return [v.readyState, v.error ? v.error.code : 0]; }")
            if not any(s in (200, 206) for s in mp4):
                errs.append(f"Film: keine .mp4-Antwort 200/206 ({mp4})")
            if h264 and (ready < 1 or err):
                errs.append(f"Film: readyState {ready}, Fehlercode {err}")
            elif not h264:
                notes.append(f"Film: Playwright-Chromium ohne H.264, nur Anfrage geprueft ({mp4})")
        except Exception as e:
            if not h264 and any(s in (200, 206) for s in mp4):
                notes.append(f"Film: Playwright-Chromium ohne H.264, Anfrage {mp4} ok")
            else:
                errs.append(f"Film: {type(e).__name__}: {str(e)[:200]} (mp4 {mp4})")
    pg.wait_for_timeout(800)
    collect(pg, hits)
    errs += [f"/ (Interaktion): {h}" for h in dict.fromkeys(hits)]
    ctx.close()
    return errs, notes


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--local", action="store_true")
    g.add_argument("--base")
    a = ap.parse_args()
    srv = None
    if a.local:
        srv, base = start_local()
        same = snippet_matches()
        if same is False:
            print("FEHLER CSP in check_csp.py weicht vom Caddy-Snippet ab")
            sys.exit(1)
        print(f"lokal: {base} (CSP {'wortgleich zum Caddy-Snippet' if same else 'Snippet nicht gefunden'})")
    else:
        base = a.base.rstrip("/")
    try:
        with sync_playwright() as pw:
            b, h264 = launch(pw)
            print(f"Browser: {'Chrome' if h264 else 'Playwright-Chromium'}")
            perrs, n = check_pages(b, base)
            herrs, notes = check_home(b, base, h264)
            b.close()
    finally:
        if srv:
            srv.shutdown()
            srv.server_close()
    for name, errs in (("AK2 Seiten (" + str(n) + ")", perrs), ("AK2 Startseite Film/Chat/SW", herrs)):
        print(f"{name}: {'OK' if not errs else 'FEHLER (' + str(len(errs)) + ')'}")
        for e in errs[:60]:
            print("   ", e)
    for x in notes:
        print("HINWEIS", x)
    sys.exit(1 if perrs or herrs else 0)


if __name__ == "__main__":
    main()
