#!/usr/bin/env python3
"""IndexNow-Ping fuer grundke-it.de (Bing, Yandex u. a.).

Meldet URLs aus sitemap.xml an api.indexnow.org. Der Schluessel ist der Dateiname der
<key>.txt im Wurzelverzeichnis und muss live unter https://grundke-it.de/<key>.txt liegen.

Aufruf (nach dem Deploy, nicht vorher, sonst holt Bing alte Seiten):
  python tools/indexnow.py --dry-run          # nur anzeigen
  python tools/indexnow.py                    # alle URLs der Sitemap melden
  python tools/indexnow.py /ratgeber/x/ /     # nur diese Pfade melden

Kein Teil des Builds: der Build bleibt ohne Netzwerkzugriff.
"""
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "grundke-it.de"
BASE = "https://" + HOST
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_RE = re.compile(r"^[0-9a-f]{32}\.txt$")


def find_key() -> str:
    keys = [os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.txt"))
            if KEY_RE.match(os.path.basename(p))]
    if len(keys) != 1:
        raise SystemExit("IndexNow: genau eine <key>.txt im Wurzelverzeichnis erwartet, gefunden: %s" % keys)
    key = keys[0][:-4]
    with open(os.path.join(ROOT, keys[0]), encoding="utf-8") as f:
        if f.read().strip() != key:
            raise SystemExit("IndexNow: Inhalt der Schluesseldatei stimmt nicht mit dem Dateinamen ueberein")
    return key


def sitemap_urls() -> list[str]:
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    paths = [a for a in argv if not a.startswith("--")]
    urls = [BASE + (p if p.startswith("/") else "/" + p) for p in paths] if paths else sitemap_urls()
    if not urls:
        raise SystemExit("IndexNow: keine URLs")
    key = find_key()
    payload = {"host": HOST, "key": key, "keyLocation": "%s/%s.txt" % (BASE, key), "urlList": urls}
    print("%d URLs, Schluessel %s..." % (len(urls), key[:6]))
    if dry:
        print("\n".join(urls))
        return 0
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("IndexNow antwortet HTTP %d" % r.status)
    except urllib.error.HTTPError as e:
        print("IndexNow Fehler HTTP %d: %s" % (e.code, e.read()[:200]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
