"""Draw the invented passport spread for the Republic of Sorrelia.

A code-drawn open passport: the left page holds an Island League
visa and entry/exit stamps from the invented neighbours Vistria,
Carnelia and Belmar; the right page is the data page with a realistic
photographic portrait, bilingual (Sorrelian / English) labels,
consistent issue details and a machine-readable zone. Every date is
consistent and chronological: the passport was issued 14 MAR 2024,
the visa is valid through 2025, and every stamp falls after issue in
travel order (Vistria Apr 2024, Carnelia Jun 2025, Belmar Oct 2025,
home 19 Oct 2025). Sorrelia's quirk: the island has no roads at all
— travel is by cable car only, and this passport is the only valid
fare at every cable-car station.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
INK = (28, 42, 50)
INK_SOFT = (74, 88, 96)
PAPER = (243, 234, 210)
PAPER_DARK = (232, 221, 192)
COVER = (18, 38, 62)
COVER_EDGE = (176, 141, 62)
GOLD = (176, 141, 62)
BURGUNDY = (140, 32, 40)
BURGUNDY_DARK = (104, 22, 30)
NAVY = (30, 56, 92)
STAMP_BLUE = (74, 63, 140)
STAMP_RED = (163, 59, 46)
STAMP_TEAL = (46, 107, 98)
VISA_BLUE = (38, 84, 120)

PORTRAIT_PATH = Path(__file__).resolve().with_name(
    "portrait.webp")

# --- fonts ---------------------------------------------------------------
FONT_DIR = Path("/usr/share/fonts/truetype")
SERIF = FONT_DIR / "liberation/LiberationSerif-Bold.ttf"
SERIF_R = FONT_DIR / "liberation/LiberationSerif-Regular.ttf"
SERIF_I = FONT_DIR / "liberation/LiberationSerif-Italic.ttf"
SANS = FONT_DIR / "liberation/LiberationSans-Regular.ttf"
SANS_B = FONT_DIR / "liberation/LiberationSans-Bold.ttf"
MONO = FONT_DIR / "dejavu/DejaVuSansMono.ttf"
MONO_B = FONT_DIR / "dejavu/DejaVuSansMono-Bold.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def resolve_font(f, size: int) -> ImageFont.FreeTypeFont:
    if isinstance(f, ImageFont.FreeTypeFont):
        return f
    return ImageFont.truetype(str(f), size)


def text(draw: ImageDraw.ImageDraw, xy, s, f, fill, anchor="la", size=13):
    draw.text(xy, s, font=resolve_font(f, size), fill=fill, anchor=anchor)


def spaced(draw: ImageDraw.ImageDraw, xy, s, f, fill, tracking=2,
           anchor="la", size=13):
    """Draw text with letter spacing; anchor 'ma' centres on xy."""
    fnt = resolve_font(f, size)
    x, y = xy
    widths = []
    total = 0
    for ch in s:
        w = draw.textlength(ch, font=fnt)
        widths.append(w)
        total += w
    total += tracking * (len(s) - 1)
    if anchor == "ma":
        x -= total / 2
    cx = x
    for ch, w in zip(s, widths):
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += w + tracking


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# --- ICAO MRZ check digits ----------------------------------------------
def mrz_value(ch: str) -> int:
    if ch.isdigit():
        return int(ch)
    if ch == "<":
        return 0
    return ord(ch) - 55  # A=10 ... Z=35


def mrz_check(s: str) -> str:
    weights = (7, 3, 1)
    total = sum(mrz_value(ch) * weights[i % 3] for i, ch in enumerate(s))
    return str(total % 10)


def build_mrz():
    line1 = "P<SORMARCHETTI<<CHIARA<ELENA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "SR5172046"
    nat = "SOR"
    dob = "950904"
    sex = "F"
    exp = "340313"
    personal = "<" * 14
    body = (doc + mrz_check(doc) + nat + dob + mrz_check(dob) + sex
            + exp + mrz_check(exp) + personal)
    personal_cd = mrz_check(personal)
    composite = mrz_check(body + personal_cd)
    line2 = body + personal_cd + composite
    # line2 is exactly 44 chars: doc(9)+cd+nat(3)+dob(6)+cd+sex+exp(6)
    # +cd+personal(14)+cd+composite(1) = 44
    assert len(line1) == 44, len(line1)
    assert len(line2) == 44, len(line2)
    return line1, line2


# --- stamps ---------------------------------------------------------------
def make_stamp(size, color, lines, shape="oval", rotate=0):
    """A rubber stamp on its own layer, rotated slightly."""
    layer = Image.new("RGBA", (size[0] + 40, size[1] + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = layer.width // 2, layer.height // 2
    w, h = size
    ink = color + (235,)
    if shape == "oval":
        d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                  outline=ink, width=3)
        d.ellipse([cx - w // 2 + 7, cy - h // 2 + 7,
                   cx + w // 2 - 7, cy + h // 2 - 7],
                  outline=ink, width=1)
    else:
        r = w // 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=3)
        d.ellipse([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
                  outline=ink, width=1)
    f_big = font(SANS_B, 15)
    f_small = font(SANS_B, 12)
    f_tiny = font(SANS, 10)
    n = len(lines)
    y = cy - (n * 19) // 2
    for i, (s, kind) in enumerate(lines):
        f = f_big if kind == "big" else f_small if kind == "med" else f_tiny
        d.text((cx, y + i * 19), s, font=f, fill=ink, anchor="ma")
    if shape == "round":
        d.polygon(star_points(cx, cy + 34, 7, 3), fill=ink)
    return layer.rotate(rotate, resample=Image.BICUBIC, expand=False)


def stamp_rect(size, color, lines, rotate=0):
    layer = Image.new("RGBA", (size[0] + 40, size[1] + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = layer.width // 2, layer.height // 2
    w, h = size
    ink = color + (230,)
    d.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                outline=ink, width=3)
    d.rectangle([cx - w // 2 + 6, cy - h // 2 + 6,
                 cx + w // 2 - 6, cy + h // 2 - 6], outline=ink, width=1)
    n = len(lines)
    y = cy - (n * 18) // 2
    for i, (s, kind) in enumerate(lines):
        f = font(SANS_B, 13) if kind == "big" else font(SANS, 11)
        d.text((cx, y + i * 18), s, font=f, fill=ink, anchor="ma")
    return layer.rotate(rotate, resample=Image.BICUBIC, expand=False)


# --- coat of arms ---------------------------------------------------------
def draw_arms(draw: ImageDraw.ImageDraw, cx, cy, s):
    """Shield of Sorrelia: gold sun over twin peaks, a cable-car line
    crossing the shield with a gondola hanging from it."""
    w, h = int(s * 0.72), s
    x0, y0 = cx - w // 2, cy - h // 2
    shield = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h * 0.62),
              (cx, y0 + h), (x0, y0 + h * 0.62)]
    draw.polygon(shield, fill=BURGUNDY_DARK, outline=GOLD, width=3)
    # sun with rays
    sx, sy = cx, y0 + h * 0.26
    for a in range(0, 360, 45):
        r = math.radians(a)
        draw.line([(sx + 9 * math.cos(r), sy + 9 * math.sin(r)),
                   (sx + 13 * math.cos(r), sy + 13 * math.sin(r))],
                  fill=GOLD, width=2)
    draw.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=GOLD)
    # twin peaks
    draw.polygon([(x0 + 5, y0 + h * 0.84), (cx - 8, y0 + h * 0.52),
                  (cx + 2, y0 + h * 0.84)], fill=(240, 236, 220))
    draw.polygon([(cx - 2, y0 + h * 0.84), (cx + 14, y0 + h * 0.60),
                  (x0 + w - 5, y0 + h * 0.84)], fill=(214, 206, 186))
    # cable line across the shield, gondola hanging from it
    cy0 = y0 + h * 0.34
    cy1 = y0 + h * 0.48
    draw.line([(x0 + 4, cy0), (x0 + w - 4, cy1)], fill=GOLD, width=2)
    gx = cx + 8
    gy = cy0 + (cy1 - cy0) * (gx - (x0 + 4)) / (w - 8)
    draw.line([(gx, gy), (gx, gy + 9)], fill=GOLD, width=2)
    draw.rectangle([gx - 7, gy + 9, gx + 7, gy + 18], fill=INK,
                   outline=GOLD, width=1)


# --- portrait -------------------------------------------------------------
def draw_portrait(base: Image.Image, box):
    """Paste the provided photorealistic portrait into the photo box,
    cover-cropped so the face is never squeezed or covered."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    photo = Image.open(PORTRAIT_PATH).convert("RGB")
    scale = max(w / photo.width, h / photo.height)
    nw, nh = int(photo.width * scale + 0.5), int(photo.height * scale + 0.5)
    photo = photo.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    photo = photo.crop((left, top, left + w, top + h))
    # laminate shine
    shine = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    sd.polygon([(w * 0.55, 0), (w * 0.78, 0), (w * 0.28, h), (w * 0.05, h)],
               fill=(255, 255, 255, 26))
    photo = Image.alpha_composite(photo.convert("RGBA"), shine)
    base.paste(photo.convert("RGB"), (x0, y0))
    d = ImageDraw.Draw(base)
    d.rectangle(box, outline=INK, width=2)
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], outline=(120, 110, 88),
                width=1)


# --- page helpers ---------------------------------------------------------
def guilloche(draw: ImageDraw.ImageDraw, box, color):
    x0, y0, x1, y1 = box
    for k in range(3):
        off = 8 + k * 5
        pts = []
        for t in range(0, 200):
            px = x0 + off + (x1 - x0 - 2 * off) * t / 199
            py = y0 + off + 2.5 * math.sin(t * math.pi / 12)
            pts.append((px, py))
        draw.line(pts, fill=color, width=1)
        pts = []
        for t in range(0, 200):
            px = x0 + off + (x1 - x0 - 2 * off) * t / 199
            py = y1 - off + 2.5 * math.sin(t * math.pi / 12)
            pts.append((px, py))
        draw.line(pts, fill=color, width=1)


def paper_texture(img: Image.Image, box, seed=7):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    for _ in range(2600):
        x = rnd.randint(x0, x1)
        y = rnd.randint(y0, y1)
        a = rnd.randint(5, 16)
        c = (120, 100, 60, a) if rnd.random() < 0.5 else (255, 255, 255, a)
        d.point((x, y), fill=c)


def field(draw: ImageDraw.ImageDraw, x, y, label, value, width=230):
    text(draw, (x, y), label, SANS, (120, 110, 88), anchor="la", size=10)
    text(draw, (x, y + 13), value, SANS_B, INK, anchor="la", size=15)


# --- left page: visas -----------------------------------------------------
def draw_left_page(img: Image.Image, draw: ImageDraw.ImageDraw):
    x0, y0, x1, y1 = 56, 116, 500, 888
    draw.rectangle([x0, y0, x1, y1], fill=PAPER)
    guilloche(draw, (x0 + 4, y0 + 4, x1 - 4, y1 - 4), (190, 172, 130))
    spaced(draw, (278, y0 + 16), "VISTI / VISAS", SANS_B, INK, tracking=6,
           anchor="ma", size=14)
    draw.line([(x0 + 24, y0 + 44), (x1 - 24, y0 + 44)], fill=INK, width=1)
    text(draw, (x1 - 26, y0 + 14), "12", SANS, INK_SOFT, anchor="ra",
         size=12)

    # Island League multiple-entry visa sticker
    vx0, vy0, vx1, vy1 = 78, 168, 478, 296
    draw.rectangle([vx0, vy0, vx1, vy1], fill=(226, 236, 240),
                   outline=VISA_BLUE, width=2)
    draw.rectangle([vx0 + 5, vy0 + 5, vx1 - 5, vy1 - 5],
                   outline=VISA_BLUE, width=1)
    # little flag bars
    for i, c in enumerate(((140, 32, 40), (176, 141, 62), (30, 56, 92))):
        draw.rectangle([vx0 + 16 + i * 26, vy0 + 14, vx0 + 36 + i * 26,
                        vy0 + 26], fill=c)
    spaced(draw, ((vx0 + vx1) // 2, vy0 + 14), "ISLAND LEAGUE",
           SANS_B, VISA_BLUE, tracking=3, anchor="ma", size=13)
    text(draw, ((vx0 + vx1) // 2, vy0 + 44), "MULTIPLE ENTRY VISA",
         SANS_B, INK, anchor="ma")
    text(draw, ((vx0 + vx1) // 2, vy0 + 66),
         "90 DAYS PER STAY  ·  No. AL-5520-2025", SANS, INK, anchor="ma")
    text(draw, ((vx0 + vx1) // 2, vy0 + 86),
         "VALID  01 JAN 2025 — 31 DEC 2025", SANS_B, INK, anchor="ma")
    text(draw, ((vx0 + vx1) // 2, vy0 + 106),
         "Issued at Porto Verde  ·  19 DEC 2024", SANS, INK_SOFT,
         anchor="ma")

    # Vistria arrival / departure ovals
    s1 = make_stamp((168, 108), STAMP_BLUE,
                    [("VISTRIA", "big"), ("ARRIVAL", "med"),
                     ("02 APR 2024", "med")], "oval", -8)
    img.paste(s1, (84, 330), s1)
    s2 = make_stamp((168, 108), STAMP_RED,
                    [("VISTRIA", "big"), ("DEPARTURE", "med"),
                     ("09 APR 2024", "med")], "oval", 6)
    img.paste(s2, (300, 330), s2)
    # Carnelia entry / exit rounds
    s3 = make_stamp((128, 128), STAMP_TEAL,
                    [("CARNELIA", "big"), ("ENTRY", "med"),
                     ("17 JUN 2025", "med"), ("PORTO CARNE", "tiny")],
                    "round", -12)
    img.paste(s3, (86, 500), s3)
    s4 = make_stamp((128, 128), STAMP_BLUE,
                    [("CARNELIA", "big"), ("EXIT", "med"),
                     ("30 JUN 2025", "med"), ("PORTO CARNE", "tiny")],
                    "round", 10)
    img.paste(s4, (286, 500), s4)
    # Belmar entry round
    s5 = make_stamp((116, 116), STAMP_RED,
                    [("BELMAR", "big"), ("ENTRY", "med"),
                     ("11 OCT 2025", "med")], "round", -5)
    img.paste(s5, (216, 660), s5)
    # Cable-car fare stamp
    s6 = stamp_rect((132, 64), STAMP_TEAL,
                    [("CABLE-CAR PAID", "big"),
                     ("12 SR · 17 JUN 2025", "med")], 4)
    img.paste(s6, (330, 700), s6)
    # Return home to Sorrelia oval
    s7 = make_stamp((150, 92), STAMP_BLUE,
                    [("SORRELIA", "big"), ("ARRIVAL", "med"),
                     ("19 OCT 2025", "med")], "oval", 3)
    img.paste(s7, (76, 748), s7)


# --- right page: data page ------------------------------------------------
def draw_right_page(img: Image.Image, draw: ImageDraw.ImageDraw):
    x0, y0, x1, y1 = 524, 116, 968, 888
    draw.rectangle([x0, y0, x1, y1], fill=PAPER)
    guilloche(draw, (x0 + 4, y0 + 4, x1 - 4, y1 - 4), (190, 172, 130))

    draw_arms(draw, (x0 + x1) // 2, y0 + 46, 56)
    spaced(draw, ((x0 + x1) // 2, y0 + 86), "REPUBBLICA DI SORRELIA",
           SERIF, INK, tracking=1, anchor="ma", size=22)
    spaced(draw, ((x0 + x1) // 2, y0 + 114), "REPUBLIC OF SORRELIA",
           SERIF, INK, tracking=1, anchor="ma", size=12)
    spaced(draw, ((x0 + x1) // 2, y0 + 134), "P A S S A P O R T O",
           SANS_B, INK, tracking=2, anchor="ma", size=17)
    draw.line([(x0 + 24, y0 + 160), (x1 - 24, y0 + 160)], fill=INK, width=1)

    # type / code / number line
    ty = y0 + 172
    text(draw, (x0 + 24, ty), "TIPO / TYPE", SANS, (120, 110, 88))
    text(draw, (x0 + 24, ty + 13), "P", SANS_B, INK)
    text(draw, (x0 + 120, ty), "CODICE / CODE", SANS, (120, 110, 88))
    text(draw, (x0 + 120, ty + 13), "SOR", SANS_B, INK)
    text(draw, (x0 + 240, ty), "PASSAPORTO / PASSPORT No.", SANS,
         (120, 110, 88), size=12)
    text(draw, (x0 + 240, ty + 13), "SR 5172046", SANS_B, INK)
    draw.line([(x0 + 24, ty + 36), (x1 - 24, ty + 36)],
              fill=(190, 172, 130), width=1)

    # portrait (realistic photo)
    draw_portrait(img, (x0 + 24, y0 + 226, x0 + 176, y0 + 416))
    text(draw, (x0 + 24, y0 + 422), "FOTOGRAFIA / PHOTOGRAPH", SANS,
         (120, 110, 88), anchor="la", size=10)

    # data fields beside the portrait
    fx = x0 + 196
    fy = y0 + 226
    field(draw, fx, fy, "COGNOME / SURNAME", "MARCHETTI")
    field(draw, fx, fy + 46, "NOME / GIVEN NAMES", "CHIARA ELENA")
    field(draw, fx, fy + 92, "NAZIONALITÀ / NATIONALITY", "SORRELIAN")
    field(draw, fx, fy + 138, "DATA DI NASCITA / DATE OF BIRTH",
          "04 SEP 1995")
    field(draw, fx, fy + 184, "LUOGO DI NASCITA / PLACE OF BIRTH",
          "PORTO VERDE")
    field(draw, fx, fy + 230, "SESSO / SEX", "F")

    # issue / expiry / authority row
    iy = y0 + 512
    draw.line([(x0 + 24, iy - 12), (x1 - 24, iy - 12)],
              fill=(190, 172, 130), width=1)
    field(draw, x0 + 24, iy, "RILASCIO / ISSUE",
          "14 MAR 2024")
    field(draw, x0 + 170, iy, "SCADENZA / EXPIRY",
          "13 MAR 2034")
    field(draw, x0 + 310, iy, "AUTORITÀ / AUTHORITY", "PORTO VERDE", 120)

    # telling detail: conditions box (the cable-car quirk)
    cx0, cy0, cx1, cy1 = x0 + 24, iy + 58, x1 - 24, iy + 146
    draw.rectangle([cx0, cy0, cx1, cy1], outline=BURGUNDY, width=2)
    draw.rectangle([cx0 + 4, cy0 + 4, cx1 - 4, cy1 - 4], outline=BURGUNDY,
                   width=1)
    text(draw, (cx0 + 12, cy0 + 8), "CONDIZIONI / CONDITIONS", SANS_B,
         BURGUNDY, size=12)
    text(draw, (cx0 + 12, cy0 + 24),
         "Holder must present this passport at every cable-car",
         SANS, INK, size=12)
    text(draw, (cx0 + 12, cy0 + 40),
         "station — it is the only valid fare on the island.",
         SANS, INK, size=12)
    text(draw, (cx0 + 12, cy0 + 56),
         "No roads on Sorrelia: travel is by cable car only.",
         SANS, INK, size=12)
    text(draw, (cx0 + 12, cy0 + 72),
         "Languages: SORRELIAN — ENGLISH — FRANÇAIS", SANS, INK_SOFT,
         size=12)

    # signature
    sy = iy + 154
    sig_f = font(SERIF_I, 24)
    draw.text((x0 + 24, sy), "Chiara Marchetti", font=sig_f, fill=INK)
    draw.line([(x0 + 24, sy + 32), (x0 + 220, sy + 32)], fill=INK, width=1)
    text(draw, (x0 + 24, sy + 38), "FIRMA DEL TITOLARE / SIGNATURE OF BEARER",
         SANS, (120, 110, 88), size=10)
    text(draw, (x1 - 24, sy + 38), "PAGE 1", SANS, INK_SOFT, anchor="ra",
         size=10)

    # machine-readable zone
    line1, line2 = build_mrz()
    mrz_f = font(MONO, 15)
    my = y1 - 48
    draw.rectangle([x0 + 12, my - 8, x1 - 12, my + 44], fill=(238, 230, 205))
    draw.text((x0 + 24, my), line1, font=mrz_f, fill=INK)
    draw.text((x0 + 24, my + 20), line2, font=mrz_f, fill=INK)


# --- whole image ----------------------------------------------------------
def build() -> Image.Image:
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # desk gradient
    for yy in range(H):
        t = yy / H
        d.line([(0, yy), (W, yy)],
               fill=tuple(int(a + (b - a) * t) for a, b in
                          zip((10, 28, 44), (20, 48, 66))))
    # vignette
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for r in range(60):
        a = int(70 * (r / 60) ** 2)
        vd.rectangle([r, r, W - r, H - r], outline=(0, 0, 0, a))
    img = Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")
    d = ImageDraw.Draw(img)

    # book cover
    d.rounded_rectangle([40, 100, 984, 904], radius=18, fill=COVER,
                        outline=COVER_EDGE, width=2)
    d.rounded_rectangle([48, 108, 976, 896], radius=14, outline=GOLD,
                        width=1)
    # spine shadow at the gutter
    gutter = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gutter)
    for i in range(24):
        a = int(90 * (1 - i / 24))
        gd.line([(512 - 12 + i, 116), (512 - 12 + i, 888)],
                fill=(0, 0, 0, a))
        gd.line([(512 + 12 - i, 116), (512 + 12 - i, 888)],
                fill=(0, 0, 0, a))
    img = Image.alpha_composite(img.convert("RGBA"), gutter).convert("RGB")
    d = ImageDraw.Draw(img)

    draw_left_page(img, d)
    draw_right_page(img, d)

    # soft drop shadow under the book
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([52, 906, 984, 918], radius=8, fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")

    paper_texture(img, (56, 116, 968, 888))
    return img


def main():
    out = Path(__file__).resolve().with_name("entry.png")
    img = build()
    img.save(out, format="JPEG", quality=88, optimize=True)
    size = out.stat().st_size
    print(f"wrote {out} {img.size[0]}x{img.size[1]} {size} bytes")
    assert img.size == (1024, 1024)
    assert size <= 1_048_576, f"over 1 MiB: {size}"


if __name__ == "__main__":
    main()
