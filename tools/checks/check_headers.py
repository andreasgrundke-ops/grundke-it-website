"""Live-Pruefung der Auslieferung (Spec Hosting/Security-Header 08.11.2026: AK1, AK4, AK5).
Aufruf: python tools/checks/check_headers.py [--base https://grundke-it.de]   Exit 1 bei Fehler.
Version 1.0.0 · Autor Andreas Grundke · Datum 2026-11-08
Ablauf:
  1. AK1 Security-Header auf der Startseite (HSTS, nosniff, X-Frame-Options, Referrer-Policy, Permissions-Policy,
     COOP, CSP mit frame-ancestors 'none' und script-src 'self' ohne unsafe-*), kein Server-Header.
  2. AK4 Verhalten wie GitHub Pages: /pfad -> 301 /pfad/, 404-Seite mit Status 404, http:// und www -> 301 auf
     https://<host>/..., Range auf den Film -> 206, Cache-Control (sw.js no-cache, HTML max-age=600),
     Content-Types fuer .vtt, .webmanifest, .woff2.
  3. AK5 interne Pfade -> 404, Positivliste -> 200 (llms.txt, robots.txt, sitemap.xml, Kit-Dateien, Verifizierungs-
     dateien im Wurzelordner; die Dateilisten kommen aus dem Repo).
Nur Standardbibliothek. Folgt keinen Weiterleitungen (jede Antwort wird einzeln bewertet).
http:// und www werden nur geprueft, wenn --base https:// ist."""
import argparse, http.client, re, ssl, sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
TIMEOUT = 20
UA = "grundke-it-check-headers/1.0"
CSP_NEED = ("frame-ancestors 'none'", "default-src 'self'", "object-src 'none'", "base-uri 'self'")
EXPECT_HEADERS = {
    "strict-transport-security": lambda v: re.search(r"max-age=(\d+)", v) and int(re.search(r"max-age=(\d+)", v).group(1)) >= 31536000,
    "x-content-type-options": lambda v: v.strip().lower() == "nosniff",
    "x-frame-options": lambda v: v.strip().upper() == "DENY",
    "referrer-policy": lambda v: v.strip().lower() == "strict-origin-when-cross-origin",
    "permissions-policy": lambda v: "camera=()" in v and "microphone=()" in v and "geolocation=()" in v,
    "cross-origin-opener-policy": lambda v: v.strip().lower() == "same-origin",
}
NEG_PATHS = ["/tools/build_landingpages.py", "/tools/checks/check_static.py", "/CLAUDE.md", "/README.md", "/STATUS.md",
             "/.git/HEAD", "/.git/config", "/.github/workflows/deploy.yml", "/.gitignore", "/docs/",
             "/assets/img/og/og-image-generate.py"]


def request(url, method="GET", headers=None, body_limit=200_000):
    """Eine Anfrage ohne Weiterleitung. Rueckgabe (status, headers-dict klein, body-bytes gekuerzt)."""
    u = urlsplit(url)
    path = (u.path or "/") + (f"?{u.query}" if u.query else "")
    conn_cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    kw = {"timeout": TIMEOUT}
    if u.scheme == "https":
        kw["context"] = ssl.create_default_context()
    conn = conn_cls(u.hostname, u.port, **kw)
    try:
        conn.request(method, path, headers={"User-Agent": UA, "Accept-Encoding": "identity", **(headers or {})})
        r = conn.getresponse()
        body = r.read(body_limit) if method != "HEAD" else b""
        hdrs = {}
        for k, v in r.getheaders():
            k = k.lower()
            hdrs[k] = f"{hdrs[k]}, {v}" if k in hdrs else v
        return r.status, hdrs, body
    finally:
        conn.close()


class Report:
    def __init__(self):
        self.bad = 0

    def check(self, ak, name, ok, detail=""):
        print(f"{'OK    ' if ok else 'FEHLER'} {ak} {name}{'' if ok or not detail else ' - ' + detail}")
        self.bad += 0 if ok else 1

    def safe(self, ak, name, fn):
        try:
            fn()
        except Exception as e:  # Netzfehler je Pruefung melden, nicht abbrechen
            self.check(ak, name, False, f"{type(e).__name__}: {e}")


def csp_directives(csp):
    out = {}
    for part in csp.split(";"):
        bits = part.strip().split()
        if bits:
            out[bits[0].lower()] = bits[1:]
    return out


def ak1(rep, base):
    st, h, _ = request(base + "/")
    rep.check("AK1", f"Startseite Status 200 ({st})", st == 200)
    for name, test in EXPECT_HEADERS.items():
        v = h.get(name)
        rep.check("AK1", f"Header {name}", bool(v) and bool(test(v)), f"Wert {v!r}")
    csp = h.get("content-security-policy", "")
    rep.check("AK1", "Content-Security-Policy vorhanden", bool(csp))
    for need in CSP_NEED:
        rep.check("AK1", f"CSP enthaelt {need}", need in csp)
    d = csp_directives(csp)
    script = d.get("script-src", d.get("default-src"))
    # Positivliste: nur 'self'. Auch https:, *, data:, blob: oder fremde Hosts gelten als Fehler (Review 08.11.2026).
    rep.check("AK1", "CSP script-src nur 'self'",
              script is not None and set(script) == {"'self'"}, f"script-src {script}")
    rep.check("AK1", "kein Server-Header", "server" not in h, f"Server: {h.get('server')}")


def location_is(h, current_url, want):
    loc = h.get("location")
    return loc is not None and urljoin(current_url, loc) == want, loc


def ak4(rep, base):
    u = base + "/fernwartung"
    st, h, _ = request(u)
    ok, loc = location_is(h, u, base + "/fernwartung/")
    rep.check("AK4", "/fernwartung -> 301 /fernwartung/", st == 301 and ok, f"{st} Location {loc!r}")

    title = re.search(r"<title>(.*?)</title>", (ROOT / "404.html").read_text(encoding="utf-8"), re.S).group(1).strip()
    st, h, body = request(base + "/gibtsnicht/")
    rep.check("AK4", "/gibtsnicht/ -> 404 mit 404-Seite", st == 404 and title.encode() in body,
              f"Status {st}, Titel {'gefunden' if title.encode() in body else 'fehlt'}")

    host = urlsplit(base).hostname
    if base.startswith("https://"):
        for src in (f"http://{host}/kontakt/", f"http://www.{host}/kontakt/", f"https://www.{host}/kontakt/"):
            st, h, _ = request(src)
            ok, loc = location_is(h, src, base + "/kontakt/")
            rep.check("AK4", f"{src} -> 301 {base}/kontakt/", st == 301 and ok, f"{st} Location {loc!r}")
    else:
        print("HINWEIS AK4 http/www-Weiterleitung uebersprungen (--base ist nicht https)")

    videos = sorted((ROOT / "assets" / "video").glob("*.mp4"))
    if videos:
        vu = f"{base}/assets/video/{videos[0].name}"
        st, h, body = request(vu, headers={"Range": "bytes=0-99"}, body_limit=1000)
        rep.check("AK4", f"Range auf {videos[0].name} -> 206", st == 206 and len(body) == 100,
                  f"Status {st}, {len(body)} Bytes, Content-Range {h.get('content-range')!r}")
    else:
        rep.check("AK4", "Film unter assets/video/ im Repo", False, "keine .mp4 gefunden")

    st, h, _ = request(base + "/sw.js")
    rep.check("AK4", "sw.js Cache-Control no-cache", st == 200 and "no-cache" in h.get("cache-control", ""),
              f"{st} {h.get('cache-control')!r}")
    st, h, _ = request(base + "/")
    rep.check("AK4", "HTML Cache-Control max-age=600", st == 200 and "max-age=600" in h.get("cache-control", ""),
              f"{h.get('cache-control')!r}")

    types = {".vtt": "text/vtt", ".webmanifest": "application/manifest+json", ".woff2": "font/woff2"}
    samples = {
        ".vtt": next((ROOT / "assets" / "video").glob("*.vtt"), None),
        ".webmanifest": ROOT / "site.webmanifest",
        ".woff2": next((ROOT / "assets" / "fonts").glob("*.woff2"), None),
    }
    for ext, want in types.items():
        p = samples[ext]
        if p is None or not p.exists():
            rep.check("AK4", f"Content-Type {ext}", False, "keine Beispieldatei im Repo")
            continue
        path = "/" + p.relative_to(ROOT).as_posix()
        st, h, _ = request(base + path, body_limit=10)
        ct = h.get("content-type", "")
        rep.check("AK4", f"Content-Type {ext} = {want}", st == 200 and ct.split(";")[0].strip() == want,
                  f"{path}: {st} {ct!r}")


def positive_paths():
    out = ["/llms.txt", "/robots.txt", "/sitemap.xml"]
    kit = ROOT / "ki-arbeitsplatz-onboarding-kit" / "dateien"
    out += ["/" + p.relative_to(ROOT).as_posix() for p in sorted(kit.glob("*.md"))]
    for pat in ("google*.html", "BingSiteAuth.xml", "*.txt"):
        out += ["/" + p.name for p in sorted(ROOT.glob(pat)) if "/" + p.name not in out]
    return out


def status_is(rep, base, path, want):
    st = request(base + path, body_limit=10)[0]
    rep.check("AK5", f"{path} -> {want}", st == want, f"Status {st}")


def ak5(rep, base):
    for path, want in [(p, 404) for p in NEG_PATHS] + [(p, 200) for p in positive_paths()]:
        rep.safe("AK5", f"{path} -> {want}", lambda path=path, want=want: status_is(rep, base, path, want))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="https://grundke-it.de")
    ap.add_argument("--only", default="AK1,AK4,AK5")
    a = ap.parse_args()
    base = a.base.rstrip("/")
    rep = Report()
    fns = {"AK1": ak1, "AK4": ak4, "AK5": ak5}
    for k in a.only.split(","):
        rep.safe(k, "Pruefung", lambda k=k: fns[k](rep, base))
    print(f"\n{'Alles OK' if not rep.bad else str(rep.bad) + ' Fehler'} ({base})")
    sys.exit(1 if rep.bad else 0)


if __name__ == "__main__":
    main()
