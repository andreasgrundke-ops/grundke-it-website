"""SEO-Paritaet je Seite: title, description, robots, canonical, og/twitter, H1-Text, H2-Liste, Schema-@type, interne Links.
--baseline DIR schreibt seo.json; --compare DIR vergleicht; --allow FILE erlaubt freigegebene Abweichungen {"/pfad/": ["h2", ...]}."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from check_static import pages, read, rel, text_of


def meta(s, attr, name):
    m = re.search(r'<meta\s+' + attr + r'="' + re.escape(name) + r'"\s+content="([^"]*)"', s)
    return m.group(1) if m else None


def types(s):
    out = set()
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        out.update(re.findall(r'"@type":\s*"([^"]+)"', blk))
    return sorted(out)


def extract(s):
    main = (re.search(r"<main.*?</main>", s, re.S) or [s])[0] if re.search(r"<main.*?</main>", s, re.S) else s
    return {
        "title": (re.search(r"<title>(.*?)</title>", s, re.S) or [None, None])[1],
        "description": meta(s, "name", "description"), "robots": meta(s, "name", "robots"),
        "canonical": (re.search(r'<link rel="canonical" href="([^"]+)"', s) or [None, None])[1],
        "og": sorted(re.findall(r'<meta property="og:[^"]+" content="[^"]*"', s)),
        "twitter": sorted(re.findall(r'<meta name="twitter:[^"]+" content="[^"]*"', s)),
        "h1": text_of((re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S) or [None, ""])[1]),
        "h2": [text_of(h) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", main, re.S)],
        "schema": types(s),
        "links": sorted(set(h for h in re.findall(r'href="(/[^"#]*)', main))),
    }


if __name__ == "__main__":
    mode, d = sys.argv[1], Path(sys.argv[2]); d.mkdir(parents=True, exist_ok=True)
    cur = {"/" + rel(p).replace("index.html", ""): extract(read(p)) for p in pages()}
    if mode == "--baseline":
        (d / "seo.json").write_text(json.dumps(cur, indent=1, ensure_ascii=False), encoding="utf-8"); sys.exit(0)
    old = json.loads((d / "seo.json").read_text(encoding="utf-8"))
    allow = json.loads(Path(sys.argv[sys.argv.index("--allow") + 1]).read_text(encoding="utf-8")) if "--allow" in sys.argv else {}
    bad = 0
    for u, o in old.items():
        n = cur.get(u)
        if n is None:
            print(f"{u}: Seite fehlt"); bad += 1; continue
        for k in o:
            if k == "links":
                lost = set(o[k]) - set(n[k])
                if lost and k not in allow.get(u, []):
                    print(f"{u}: interne Links weg: {sorted(lost)[:5]}"); bad += 1
            elif o[k] != n[k] and k not in allow.get(u, []):
                print(f"{u}: {k} geaendert"); bad += 1
    sys.exit(1 if bad else 0)
