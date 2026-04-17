"""
================================================================================
 OG-Image Generator · Grundke IT-Service
 Version:     V5 (2026-04-17)
 Autor:       Andreas Grundke
 Zweck:       Rendert assets/img/og-image.png (1200 x 630) aus Code —
              reproduzierbar, kein SVG-Renderer-Tool noetig (nur PIL + numpy).

 Aenderungen V5 gegenueber V4:
   - Vertikale Cyan-Stripes auf BEIDEN Seiten (links + rechts gespiegelt)
   - "JETZT ANRUFEN"-Button entfernt (fuer OG irrelevant)
   - Kein weisser Rand: Canvas 100% gefuellt, RGB ohne Alpha
   - Layout zentral vertikal ausgeglichener

 Ausfuehren:
   python assets/img/og/og-image-generate.py
 Output:
   assets/img/og-image.png
================================================================================
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ─── Pfade ────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent.parent.parent  # Repo-Root
IMG_DIR  = ROOT / "assets" / "img"
LOGO     = IMG_DIR / "logo-grundke-it-white.png"
OUT      = IMG_DIR / "og-image.png"

# ─── Canvas ───────────────────────────────────────────────────────────────
W, H = 1200, 630

# ─── Farben (CI 2026.01 Dark) ─────────────────────────────────────────────
BG_TOP_LEFT   = (15, 17, 23)     # #0f1117
BG_MID        = (20, 24, 38)     # #141826
BG_BOT_RIGHT  = (26, 31, 46)     # #1a1f2e
CYAN          = (38, 189, 239)   # #26bdef
DEEP_BLUE     = (0, 0, 254)      # #0000FE
TEXT_MAIN     = (241, 245, 249)  # #f1f5f9
TEXT_MUTED    = (148, 163, 184)  # #94a3b8
TEXT_FAINT    = (100, 116, 139)  # #64748b

# ─── Fonts (Windows Standard) ─────────────────────────────────────────────
FONT_DIR = Path("C:/Windows/Fonts")
F_BLACK  = str(FONT_DIR / "ariblk.ttf")   # Arial Black
F_BOLD   = str(FONT_DIR / "arialbd.ttf")  # Arial Bold
F_REG    = str(FONT_DIR / "arial.ttf")    # Arial Regular


# ─── 1) Hintergrund: Diagonaler Gradient ─────────────────────────────────
def make_background():
    """Erzeugt diagonalen Gradient von top-left (dark) nach bottom-right."""
    # Diagonaler Gradient: t = (x/W + y/H) / 2 ∈ [0,1]
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (x / W + y / H) / 2.0

    # 3-Stop Linear Interpolation
    def lerp3(t, c1, c2, c3):
        t2 = np.clip(t * 2, 0, 2)
        low  = t2 < 1
        high = ~low
        r = np.where(low, c1[0] + (c2[0]-c1[0])*t2,       c2[0] + (c3[0]-c2[0])*(t2-1))
        g = np.where(low, c1[1] + (c2[1]-c1[1])*t2,       c2[1] + (c3[1]-c2[1])*(t2-1))
        b = np.where(low, c1[2] + (c2[2]-c1[2])*t2,       c2[2] + (c3[2]-c2[2])*(t2-1))
        return r, g, b

    r, g, b = lerp3(t, BG_TOP_LEFT, BG_MID, BG_BOT_RIGHT)
    img = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return img


# ─── 2) Radialer Glow (additive Ueberlagerung) ───────────────────────────
def add_radial_glow(arr, cx, cy, radius, color, max_alpha):
    """Addiert einen weichen radialen Glow auf ein RGB-Array (in-place)."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # Normalisierte Distanz vom Mittelpunkt (cx, cy), Radius = radius
    d = np.sqrt(((x - cx) / radius) ** 2 + ((y - cy) / radius) ** 2)
    # Weicher Abfall: smoothstep-aehnlich
    a = np.clip(1.0 - d, 0, 1) ** 2 * max_alpha  # 0..max_alpha
    a = a[..., None]  # (H, W, 1)
    color_arr = np.array(color, dtype=np.float32)
    # Screen blend (heller): out = 1 - (1-base)*(1-overlay*a)
    base = arr.astype(np.float32) / 255.0
    ov   = color_arr / 255.0
    out  = 1.0 - (1.0 - base) * (1.0 - ov * a)
    arr[:] = np.clip(out * 255.0, 0, 255).astype(np.uint8)


# ─── 3) Vertikale Cyan-Stripes (beidseitig, gespiegelt) ──────────────────
def add_vertical_stripes(arr):
    """Zeichnet prominente vertikale Cyan-Stripes links und rechts mit vertikalem Alpha-Gradient."""
    stripe_width = 8
    stripe_top   = 60
    stripe_bot   = 570
    stripe_h     = stripe_bot - stripe_top

    # Vertikales Alpha-Profil: 0 -> 1 (Mitte) -> 0
    ys = np.arange(stripe_h, dtype=np.float32)
    alpha_profile = np.sin(np.pi * ys / stripe_h) ** 1.6  # weich glocken-foermig
    alpha_profile = np.clip(alpha_profile, 0, 1)

    color_arr = np.array(CYAN, dtype=np.float32)

    for x_start in [0, W - stripe_width]:
        for xi in range(stripe_width):
            # Stripe leicht horizontal fading zur Mitte des Stripes hin
            x_fade = 1.0 - abs((xi - stripe_width/2 + 0.5) / (stripe_width/2)) * 0.3
            for yi in range(stripe_h):
                y = stripe_top + yi
                a = alpha_profile[yi] * x_fade * 0.95  # max ~0.95
                if a < 0.02:
                    continue
                base = arr[y, x_start + xi].astype(np.float32) / 255.0
                ov   = color_arr / 255.0
                blended = 1.0 - (1.0 - base) * (1.0 - ov * a)
                arr[y, x_start + xi] = np.clip(blended * 255.0, 0, 255).astype(np.uint8)

    # Zusaetzlicher weicher Seiten-Glow (breit) — links und rechts gespiegelt
    # Beide zentren liegen exakt am linken/rechten Rand (x=0 bzw. x=W),
    # damit die sichtbaren Haelften links und rechts identisch wirken.
    add_radial_glow(arr, 0, H * 0.5, 280, CYAN, max_alpha=0.22)
    add_radial_glow(arr, W, H * 0.5, 280, CYAN, max_alpha=0.22)


# ─── 4) Text + Logo via Pillow (nach Background-Rendering) ───────────────
def render_foreground(bg_np):
    img = Image.fromarray(bg_np, mode="RGB")
    draw = ImageDraw.Draw(img)

    # ── Logo zentriert oben ────────────────────────────────────────────
    logo = Image.open(LOGO).convert("RGBA")
    # Proportional auf 300px Breite skalieren
    logo_w = 300
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    logo_y = 70
    img.paste(logo, ((W - logo_w) // 2, logo_y), logo)

    # ── Tag: — IT-NOTDIENST · MÜNCHEN OST — ────────────────────────────
    tag_y = logo_y + logo_h + 35
    tag_font = ImageFont.truetype(F_BOLD, 22)
    tag_text = "IT-NOTDIENST  ·  MÜNCHEN OST"
    # Spacing-Hack: zusaetzliche Leerzeichen statt letter-spacing
    tag_bbox = draw.textbbox((0, 0), tag_text, font=tag_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_x = (W - tag_w) // 2
    draw.text((tag_x, tag_y), tag_text, font=tag_font, fill=CYAN)
    # Flankierende Striche
    bar_len = 32
    bar_gap = 18
    bar_y = tag_y + 13
    draw.rectangle(
        [tag_x - bar_gap - bar_len, bar_y, tag_x - bar_gap, bar_y + 2],
        fill=CYAN,
    )
    draw.rectangle(
        [tag_x + tag_w + bar_gap, bar_y, tag_x + tag_w + bar_gap + bar_len, bar_y + 2],
        fill=CYAN,
    )

    # ── Headline: 3 Zeilen zentriert ───────────────────────────────────
    h1_font   = ImageFont.truetype(F_BLACK, 66)
    hhi_font  = ImageFont.truetype(F_BLACK, 92)

    # y-Positionen sind TOP der jeweiligen Zeile (nicht Center) — vermeidet Bbox-Jitter
    lines_top = [
        ("Dein ITler geht", h1_font,  TEXT_MAIN, 228),
        ("nicht ran?",      h1_font,  TEXT_MAIN, 298),
        ("Ich schon.",      hhi_font, CYAN,      378),
    ]
    for text, font, color, y_top in lines_top:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(((W - text_w) // 2, y_top), text, font=font, fill=color)

    # ── Subline ────────────────────────────────────────────────────────
    sub_font = ImageFont.truetype(F_REG, 22)
    sub_text = "Kein Ticket  ·  kein Warten  ·  gerne per Du"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(((W - sub_w) // 2, 518), sub_text, font=sub_font, fill=TEXT_MUTED)

    # ── URL unten ─────────────────────────────────────────────────────
    url_font = ImageFont.truetype(F_BOLD, 22)
    url_text = "GRUNDKE-IT.DE"
    url_bbox = draw.textbbox((0, 0), url_text, font=url_font)
    url_w = url_bbox[2] - url_bbox[0]
    draw.text(((W - url_w) // 2, 580), url_text, font=url_font, fill=TEXT_FAINT)

    return img


# ─── Main ─────────────────────────────────────────────────────────────────
def main():
    print("[1/4] Hintergrund-Gradient ...")
    bg = make_background()

    print("[2/4] Radiale Glows ...")
    add_radial_glow(bg, W * 0.5, H * 0.30, 520, CYAN,      max_alpha=0.28)
    add_radial_glow(bg, W * 0.5, H * 0.95, 480, DEEP_BLUE, max_alpha=0.22)

    print("[3/4] Vertikale Stripes + Seiten-Glow (beidseitig) ...")
    add_vertical_stripes(bg)

    print("[4/4] Foreground (Logo, Text, URL) ...")
    img = render_foreground(bg)

    # RGB ohne Alpha speichern, max Qualitaet
    img = img.convert("RGB")
    img.save(OUT, format="PNG", optimize=True)
    print(f"Fertig: {OUT}  ({OUT.stat().st_size // 1024} KB, {W}x{H})")


if __name__ == "__main__":
    main()
