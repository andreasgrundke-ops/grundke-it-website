"""SEO-Paritaet je Seite: title, description, robots, canonical, og/twitter, H1-Text, H2-Liste, Schema-@type, interne Links.
--baseline DIR schreibt seo.json; --compare DIR vergleicht; --allow FILE erlaubt freigegebene Abweichungen:
  {"/pfad/": {"description": "Grund",                         Textfelder: Grund genuegt
              "links": ["/verlorener-link/", ...],             nur diese Links duerfen fehlen
              "h2": {"grund": "...", "weg": [...], "neu": [...], "reihenfolge": [...]},
              "schema": {"grund": "...", "weg": [...], "neu": [...]}}}
h2 und schema (seit Fix-Runde B, I3): erlaubt ist genau die genannte Aenderung, verlorene ("weg") und hinzugekommene
("neu") Eintraege; jede weitere Aenderung ist ein Fehler. "reihenfolge" (nur h2, optional): die gebliebenen H2 in der
erlaubten Reihenfolge, wenn sich diese geaendert hat; ohne den Schluessel muss sie der Basis entsprechen. Eine
Ausnahme fuer h2/schema nur als Text oder Feldname (Altformat) ist nicht mehr zulaessig.
Schema-@type wird seit Fix-Runde B per json.loads gelesen, auch @type als Liste (["LocalBusiness", ...])."""
import json, re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from check_static import pages, read, rel, text_of

LIST_FIELDS = ("h2", "schema")   # nur mit granularer Ausnahme (weg/neu)


def meta(s, attr, name):
    m = re.search(r'<meta\s+' + attr + r'="' + re.escape(name) + r'"\s+content="([^"]*)"', s)
    return m.group(1) if m else None


def types(s):
    """Alle @type-Werte aller JSON-LD-Bloecke, verschachtelte Knoten und @type-Listen eingeschlossen."""
    out = set()
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        stack = [json.loads(blk)]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                t = x.get("@type")
                out.update([t] if isinstance(t, str) else [v for v in (t or []) if isinstance(v, str)])
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return sorted(out)


def list_diff(before, now):
    """(weg, neu) als sortierte Listen (mit Wiederholungen) und die gebliebenen Eintraege in der Reihenfolge von jetzt
    und von vorher."""
    b, n = Counter(before), Counter(now)
    weg, neu = sorted((b - n).elements()), sorted((n - b).elements())

    def kept(seq, drop):
        drop, out = Counter(drop), []
        for x in seq:
            if drop[x]:
                drop[x] -= 1
            else:
                out.append(x)
        return out
    return weg, neu, kept(now, neu), kept(before, weg)


def check_list_field(u, k, before, now, allowed):
    """Fehlertexte fuer h2/schema einer Seite; allowed = Eintrag aus der Ausnahmeliste oder None."""
    if before == now:
        return []
    weg, neu, kept_now, kept_before = list_diff(before, now)
    if allowed is None:
        return [f"{u}: {k} geaendert (weg {weg}, neu {neu}"
                + (", Reihenfolge" if kept_now != kept_before else "") + "), keine Ausnahme"]
    if not isinstance(allowed, dict) or "weg" not in allowed or "neu" not in allowed:
        return [f"{u}: Ausnahme fuer {k} ohne Listen weg/neu (Altformat, seit Fix-Runde B nicht mehr zulaessig)"]
    errs = []
    if sorted(allowed["weg"]) != weg or sorted(allowed["neu"]) != neu:
        errs.append(f"{u}: {k} weicht von der Ausnahme ab: weg {weg} (erlaubt {sorted(allowed['weg'])}), "
                    f"neu {neu} (erlaubt {sorted(allowed['neu'])})")
    if kept_now != allowed.get("reihenfolge", kept_before):
        errs.append(f"{u}: {k} Reihenfolge der gebliebenen Eintraege {kept_now} nicht freigegeben")
    return errs


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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
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
        a = allow.get(u, {})
        # Altformat ["h2", "description", …]: Feldnamen; fuer h2/schema nicht mehr zulaessig (check_list_field)
        a = a if isinstance(a, dict) else {k: True for k in a}
        for k in o:
            if k == "links":
                lost = set(o[k]) - set(n[k])
                # "links": ["/pfad/", …] erlaubt genau diese verlorenen Links; Altformat (Text/true) erlaubt alle
                ok = a.get(k)
                lost -= set(ok) if isinstance(ok, list) else (lost if ok else set())
                if lost:
                    print(f"{u}: interne Links weg: {sorted(lost)[:5]}"); bad += 1
            elif k in LIST_FIELDS:
                for e in check_list_field(u, k, o[k], n[k], a.get(k)):
                    print(e); bad += 1
            elif o[k] != n[k] and k not in a:
                print(f"{u}: {k} geaendert"); bad += 1
    sys.exit(1 if bad else 0)
