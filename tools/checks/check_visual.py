"""Startseite 390/1440 gegen Basis (<= 0,5 % Pixel). Uhr auf Werktag 10:00, Hero-Chat ausgeblendet."""
import datetime, sys
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
import serve

FREEZE = "*{animation:none!important;transition:none!important} [data-hc-thread],[data-hc-clock]{visibility:hidden!important}"


def shots(dirpath):
    srv, base = serve.start()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in (390, 1440):
            ctx = b.new_context(viewport={"width": w, "height": 900}, service_workers="block", reduced_motion="reduce")
            pg = ctx.new_page()
            pg.clock.set_fixed_time(datetime.datetime(2026, 10, 7, 10, 0))
            pg.goto(base + "/", wait_until="networkidle"); pg.add_style_tag(content=FREEZE)
            pg.screenshot(path=str(Path(dirpath) / f"start_{w}.png"), full_page=True)
            ctx.close()
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    mode, d = sys.argv[1], Path(sys.argv[2]); d.mkdir(parents=True, exist_ok=True)
    if mode == "--baseline":
        shots(d); sys.exit(0)
    cur = d / "neu"; cur.mkdir(exist_ok=True); shots(cur)
    bad = 0
    for f in sorted(d.glob("start_*.png")):
        a, b = Image.open(f).convert("RGB"), Image.open(cur / f.name).convert("RGB")
        if a.size != b.size:
            print(f"{f.name}: Groesse {a.size} -> {b.size}"); bad += 1; continue
        diff = ImageChops.difference(a, b).convert("L").point(lambda x: 255 if x > 24 else 0)
        ratio = sum(1 for px in diff.getdata() if px) / (a.size[0] * a.size[1])
        print(f"{f.name}: {ratio:.3%}"); bad += ratio > 0.005
    sys.exit(1 if bad else 0)
