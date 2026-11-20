# V8 — final QA polish. Same V7 layout, same 28 verified stories.
# The hero panorama is now the AI editorial illustration (loaded as a fixed
# asset and cover-cropped into the hero box). Supporting illustrations are
# warmed to sit in the hero's palette. Small text gets stronger contrast.
# A small label marks the hero as an editorial illustration.
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "entry.png"
HERO_ASSET = "assets/media-generation-hero-summit-0-00f1d189-9a8c-4dbb-b5cb-123ea845b662.webp"

# ---------- palette: warm ivory paper, deep ink navy, crimson, gold ----------
PAPER   = (250, 244, 230)
PANEL   = (252, 249, 241)
NAVY    = (16, 32, 64)
NAVY2   = (26, 48, 92)
NAVY_D  = (10, 20, 42)
INK     = (24, 24, 26)
CRIMSON = (178, 34, 52)
GOLD    = (196, 148, 44)
GOLD_L  = (222, 182, 90)
TEAL    = (0, 110, 96)
GREY    = (70, 68, 62)      # darkened from V7 for small-text contrast
LGREY   = (140, 136, 126)
WHITE   = (255, 255, 255)
WOOD    = (104, 62, 38)
WOOD_D  = (78, 45, 27)

F_DISP_BLK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
F_DISP_B   = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf"
F_SERIF_B  = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
F_SERIF_I  = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
F_SANS     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS_BLK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
F_SANS_XB  = "/usr/share/fonts/truetype/noto/NotoSans-ExtraBold.ttf"
F_SANS_MED = "/usr/share/fonts/truetype/noto/NotoSans-Medium.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text(d, xy, s, fnt, fill=INK, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)

def para(d, x, y, lines, fnt, fill=INK, leading=None):
    lh = leading or int(fnt.size * 1.22)
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=fnt, fill=fill, anchor="la")
    return y + len(lines) * lh

def lerp(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))

def vgrad(d, x, y, w, h, c_top, c_bot):
    if h <= 1:
        d.rectangle([x, y, x + w, y + h], fill=c_top)
        return
    for i in range(h):
        d.line([(x, y + i), (x + w, y + i)], fill=lerp(c_top, c_bot, i / (h - 1)))

def hgrad(d, x, y, w, h, c_left, c_right):
    if w <= 1:
        d.rectangle([x, y, x + w, y + h], fill=c_left)
        return
    for i in range(w):
        d.line([(x + i, y), (x + i, y + h)], fill=lerp(c_left, c_right, i / (w - 1)))

def rrect(d, box, fill=None, outline=None, width=1, radius=4):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def cover_crop_hero(path, bw, bh):
    """Load the AI hero asset and cover-crop it to (bw, bh) without
    distortion: scale so the box is filled, then centre-crop."""
    hero = Image.open(path).convert("RGB")
    print("AI hero asset:", hero.size)
    scale = max(bw / hero.width, bh / hero.height)
    scaled = hero.resize((round(hero.width * scale), round(hero.height * scale)),
                         Image.LANCZOS)
    left = (scaled.width - bw) // 2
    top = (scaled.height - bh) // 2
    crop = scaled.crop((left, top, left + bw, top + bh))
    print("cover crop: scaled", scaled.size, "crop box", (left, top, left + bw, top + bh))
    return crop

# ---------- data: 28 verified stories (facts exactly as verified in v2-v7) ----------
# Hero + two main panels
HERO = ("Trump, Xi and Putin hold first three-way summit",
        "Three nuclear powers meet at APEC in Shenzhen; arms control tops the agenda.",
        "Reuters \u00b7 AP")
PANEL_ICJ = ("World Court: Myanmar committed genocide",
             "The ICJ finds Myanmar guilty of genocide against the Rohingya, 9 votes to 6.",
             "Reuters \u00b7 Al Jazeera")
PANEL_NASDAQ = ("Anthropic starts trading on Nasdaq",
                "Priced at $83, the Claude maker raised a record $81.3bn; close $97.",
                "NPR \u00b7 Bloomberg")

# Features, asymmetric rows. (place, topic, headline, deck, source)
FEAT_R1 = [
    ("ANTALYA \u00b7 CLIMATE", "COP31 draft drops fossil fuels",
     "Revised text cuts the $120bn aid goal.", "Reuters"),
    ("KYIV \u00b7 WAR", "Strikes damage two embassies",
     "Drones hit Kyiv; 1 killed, 5 hurt.", "AFP"),
]
FEAT_R2 = [
    ("CRIMEA \u00b7 WAR", "Ukraine hits Kerch Bridge again",
     "Neptune missiles halt trains again.", "Euronews"),
    ("ODISHA \u00b7 STORM", "Cyclone Akvan nears coast",
     "300,000 evacuated; landfall due Friday.", "IMD"),
    ("COPENHAGEN", "Denmark backs Arctic pact 109\u20130",
     "Approves the US deal, more bases.", "AP"),
]
FEAT_R3 = [
    ("WORLDWIDE \u00b7 GAMES", "GTA VI goes on sale at last",
     "Unlocks at midnight; $79.99.", "Rockstar"),
    ("GAZA \u00b7 WAR", "IDF ends Nuseirat raid",
     "Road reopens after the operation.", "Al Jazeera"),
    ("SHENZHEN \u00b7 TRADE", "APEC adopts Shenzhen Declaration",
     "Digital trade pact for Asia-Pacific.", "AP"),
    ("SANAA \u00b7 WAR", "Saudi strikes kill 11 in Yemen",
     "Strikes hit targets across Yemen.", "Reuters"),
    ("CANBERRA \u00b7 ECONOMY", "Australia's jobless rate hits 4.9%",
     "Highest since 2021.", "ABS"),
]

# Digest: 15 more stories, one line each. (place, headline)
DIGEST = [
    ("GULF", "IEA warns of energy threat."),
    ("BAGHDAD", "Iraq, Kataib Hezbollah standoff eases."),
    ("PORT SUDAN", "Hemedti's 2nd death sentence."),
    ("ULAANBAATAR", "President quits; vote 96\u2013104."),
    ("PESHAWAR", "Pakistan kills 22 militants in raids."),
    ("AIR FORCE 1", "Trump presses allies on Ukraine."),
    ("BRUSSELS", "EU summons Russia envoy over Kyiv."),
    ("PARIS", "IEA: data-centre CO2 up 70% by 2030."),
    ("BOGOT\u00c1", "Unions halt Colombia strike."),
    ("RIYADH", "Houthi missile strikes Riyadh tower."),
    ("HANOI", "Vietnam, Russia deepen energy ties."),
    ("GAZA", "Israeli forces cross ceasefire line."),
    ("KYIV", "Ukrainian strikes hit Russia's fuel supply."),
    ("NASSAU", "Cat-5 eases to Cat 4; 300 shelter."),
    ("NUKU'ALOFA", "Tonga drought emergency."),
]

# CUT from the 37 (least newsworthy, to keep text readable at 28 stories):
# 14 MOGADISHU (envoy expelled), 15 JOBURG (cricket result), 18 NAIROBI
# (doping ban), 20 MOSCOW (envoy summoned), 22 ALASKA (lawsuit dropped),
# 27 LONDON (mayoral run), 28 MIAMI (cruise outbreak), 29 FLORIDA (school
# floods), 35 WASHINGTON (Trump frustrated by Vance).

# Map: 8 biggest stories, with short labels. (label, (x, y) in map box, colour, (dx, dy))
MAP_MARKERS = [
    ("New York \u00b7 IPO", (62, 22), GOLD, (-58, -18)),
    ("The Hague \u00b7 court", (198, 14), NAVY2, (-78, 6)),
    ("Kyiv \u00b7 war", (222, 14), CRIMSON, (6, -14)),
    ("Shenzhen \u00b7 summit", (330, 30), CRIMSON, (-38, -14)),
    ("Gaza \u00b7 war", (232, 34), CRIMSON, (-62, 14)),
    ("Odisha \u00b7 cyclone", (305, 32), TEAL, (-5, 18)),
    ("Riyadh \u00b7 missile", (248, 36), CRIMSON, (2, 30)),
    ("Sanaa \u00b7 strikes", (245, 44), CRIMSON, (-105, 24)),
]
REGION_COUNTS = "Asia 7 \u00b7 Europe 7 \u00b7 Middle East 6 \u00b7 Americas 4 \u00b7 Oceania 2 \u00b7 Africa 1 \u00b7 Global 1"

FOOTER_SRC = "Sources: Reuters, AP, AFP, Al Jazeera, Euronews, Africanews, AIU, ICC, CUT, RNZ, APEC, CDC, CBS, IMD, IEA, ABS, NPR, Bloomberg, Rockstar."
FOOTER_DATE = ("DATE CHECK \u2014 left out because they were other days' news:  18 NOV: EU's \u20ac45bn Ukraine loan \u00b7 Iran strikes Kuwait & Bahrain \u00b7 Nvidia results \u00b7 Jeffries for speaker \u00b7 Russian bombers in Vietnam.  20 NOV: COP31 close \u00b7 Akvan landfall \u00b7 UK\u2013EU deal.")
FOOTER_NOTE = "Every story here happened, or was first reported, on Thursday 19 November 2026. Disputed claims are attributed, not stated as fact."

# ---------- small flags ----------
def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=(178, 34, 52) if i % 2 == 0 else WHITE)
    cw, ch = int(w * 0.42), int(h * 0.54)
    d.rectangle([x, y, x + cw, y + ch], fill=(30, 50, 110))
    for r in range(4):
        for c in range(5):
            px = x + 4 + c * (cw - 8) / 4
            py = y + 3 + r * (ch - 6) / 3
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=WHITE)

def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    d.polygon([(x + 8, y + 5), (x + 11, y + 12), (x + 18, y + 12), (x + 13, y + 16),
               (x + 15, y + 23), (x + 8, y + 19), (x + 1, y + 23), (x + 3, y + 16),
               (x - 2, y + 12), (x + 5, y + 12)], fill=(255, 222, 0))
    for sx, sy in [(x + w - 12, y + 5), (x + w - 9, y + 12), (x + w - 12, y + 19), (x + w - 18, y + 15)]:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 222, 0))

def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=WHITE)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 60, 160))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(210, 30, 30))

def flag_nl(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(174, 28, 40))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=WHITE)
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(0, 50, 140))

def flag_dk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(198, 12, 48))
    d.rectangle([x + w * 0.32, y, x + w * 0.44, y + h], fill=WHITE)
    d.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=WHITE)

def pole_flag(d, cx, top, h, draw_flag, fw=64, fh=42):
    d.line([(cx, top), (cx, top + h)], fill=(60, 50, 40), width=3)
    d.ellipse([cx - 3, top - 4, cx + 3, top + 2], fill=GOLD)
    draw_flag(d, cx + 2, top + 2, fw, fh)

def skyline(d, x0, y_base, x1, h_max, col, seed):
    """Deterministic building silhouettes with lit windows."""
    import random
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        bw = rnd.randint(22, 46)
        bh = rnd.randint(int(h_max * 0.35), h_max)
        d.rectangle([x, y_base - bh, x + bw, y_base], fill=col)
        if rnd.random() < 0.4:  # antenna
            d.line([(x + bw // 2, y_base - bh), (x + bw // 2, y_base - bh - 10)],
                   fill=col, width=2)
        for wy in range(y_base - bh + 6, y_base - 6, 12):
            for wx in range(x + 5, x + bw - 4, 10):
                if rnd.random() < 0.35:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
        x += bw + rnd.randint(2, 8)

# ---------- supporting illustrations (warmed to the hero's palette) ----------
def ill_icj(d, x, y, w, h):
    """Peace Palace, The Hague: brick hall, tower, scales of justice.
    Warmed sky (was cool grey-blue) to match the hero's dusk warmth."""
    vgrad(d, x, y, w, h, (233, 223, 206), (242, 236, 222))
    # ground
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(132, 124, 100))
    # palace body
    bx, by, bw, bh = x + w * 0.12, y + h * 0.34, w * 0.76, h * 0.52
    d.rectangle([bx, by, bx + bw, by + bh], fill=(168, 84, 62))
    d.rectangle([bx, by, bx + bw, by + 8], fill=(120, 58, 44))
    # central tower
    tx = x + w * 0.46
    d.rectangle([tx, y + h * 0.10, tx + w * 0.08, by], fill=(150, 70, 52))
    d.polygon([(tx - 6, y + h * 0.10), (tx + w * 0.08 + 6, y + h * 0.10),
               (tx + w * 0.04, y + h * 0.02)], fill=(90, 44, 36))
    pole_flag(d, tx + w * 0.04, y + h * 0.02, 16, flag_nl, fw=20, fh=13)
    # arched windows
    for i in range(7):
        wx = bx + 12 + i * (bw - 24) / 7
        d.pieslice([wx, by + 16, wx + 16, by + 34], start=180, end=360, fill=(40, 60, 90))
        d.rectangle([wx, by + 25, wx + 16, by + 52], fill=(40, 60, 90))
    # steps
    for i in range(3):
        d.rectangle([x + w * 0.30 + i * 8, by + bh + i * 5, x + w * 0.70 - i * 8,
                     by + bh + (i + 1) * 5], fill=(150, 148, 140))
    # scales of justice, foreground right
    sx, sy = x + w * 0.82, y + h * 0.62
    d.line([(sx, sy - 34), (sx, sy + 10)], fill=GOLD, width=3)
    d.line([(sx - 26, sy - 34), (sx + 26, sy - 34)], fill=GOLD, width=3)
    d.ellipse([sx - 4, sy - 40, sx + 4, sy - 32], fill=GOLD)
    for ex in (-26, 26):
        d.line([(sx + ex, sy - 34), (sx + ex, sy - 14)], fill=GOLD, width=2)
        d.pieslice([sx + ex - 12, sy - 16, sx + ex + 12, sy + 2], start=0, end=180,
                   fill=GOLD_L)
    # vote badge
    d.ellipse([x + 10, y + 8, x + 52, y + 50], fill=CRIMSON)
    text(d, (x + 31, y + 29), "9\u20136", font(F_SANS_BLK, 16), fill=WHITE, anchor="mm")

def ill_nasdaq(d, x, y, w, h):
    """Nasdaq IPO: dark chart panel, rising gold line, +17% badge.
    The line is bounded to stay inside the panel."""
    vgrad(d, x, y, w, h, NAVY_D, NAVY)
    # grid (warmed slightly)
    for gy in range(y + 14, y + h - 10, 18):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(52, 58, 88), width=1)
    # bounded rising line: from bottom-left to top-right, fixed steps
    lo, hi = y + h - 30, y + 34
    n = 9
    xs = [x + 14 + i * (w - 90) / (n - 1) for i in range(n)]
    ys = [lo - (lo - hi) * (i / (n - 1)) ** 1.15 + (4 if i % 2 else -3) for i in range(n)]
    pts = list(zip(xs, ys))
    # candles under the line
    for i, (px, py) in enumerate(pts[:-1]):
        cw = 7
        d.rectangle([px, py - 4, px + cw, py + 8], fill=(70, 160, 110))
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=GOLD_L, width=3)
    for p in pts:
        d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=GOLD_L)
    # arrow tip
    d.polygon([(pts[-1][0], pts[-1][1] - 10), (pts[-1][0] + 12, pts[-1][1] + 2),
               (pts[-1][0], pts[-1][1] + 6)], fill=GOLD_L)
    # ANT label
    text(d, (x + 14, y + 12), "ANT", font(F_SANS_BLK, 30), fill=WHITE, anchor="la")
    text(d, (x + 96, y + 20), "NASDAQ \u00b7 IPO DAY", font(F_SANS_B, 11), fill=GOLD_L, anchor="la")
    # +17% badge
    rrect(d, [x + w - 78, y + 10, x + w - 10, y + 34], fill=(34, 120, 60), radius=5)
    text(d, (x + w - 44, y + 22), "+17%", font(F_SANS_BLK, 13), fill=WHITE, anchor="mm")
    # price line
    text(d, (x + 14, y + h - 26), "$83.00 \u2192 $111.50", font(F_SANS_B, 13), fill=WHITE, anchor="la")
    text(d, (x + w - 12, y + h - 26), "CLOSE $97", font(F_SANS_BLK, 13), fill=(110, 220, 130), anchor="ra")

def ill_globe(d, x, y, w, h):
    d.ellipse([x + 4, y + 2, x + w - 4, y + h - 2], fill=(70, 125, 175))
    d.ellipse([x + 14, y + 10, x + w - 22, y + h - 18], fill=(95, 160, 105))
    d.ellipse([x + w - 26, y + h - 22, x + w - 8, y + h - 6], fill=(95, 160, 105))
    d.arc([x + 4, y + 2, x + w - 4, y + h - 2], start=200, end=340, fill=(190, 222, 235), width=2)
    # thermometer
    d.rectangle([x + w - 12, y + 6, x + w - 6, y + h - 8], fill=WHITE)
    d.ellipse([x + w - 14, y + h - 12, x + w - 4, y + h - 2], fill=CRIMSON)
    d.rectangle([x + w - 10, y + h - 16, x + w - 8, y + h - 8], fill=CRIMSON)

def ill_kyiv(d, x, y, w, h):
    vgrad(d, x, y, w, h, (233, 221, 201), (212, 192, 172))
    skyline(d, x + 4, y + h - 8, x + w - 4, int(h * 0.55), (78, 68, 66), seed=3)
    # smoke plume
    for i, (sx, sy, r) in enumerate([(w * 0.62, h * 0.30, 12), (w * 0.70, h * 0.18, 15), (w * 0.78, h * 0.08, 11)]):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(150, 148, 144))
    # drone
    dx, dy = x + w * 0.30, y + h * 0.22
    d.line([(dx - 12, dy - 6), (dx + 12, dy + 6)], fill=(30, 30, 30), width=2)
    d.line([(dx - 12, dy + 6), (dx + 12, dy - 6)], fill=(30, 30, 30), width=2)
    d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(30, 30, 30))

def ill_kerch(d, x, y, w, h):
    # warmed: dusk sky and warm water instead of cool blue
    vgrad(d, x, y, w, h, (228, 214, 188), (150, 150, 135))
    # bridge
    d.rectangle([x + 6, y + h * 0.42, x + w - 6, y + h * 0.50], fill=(60, 64, 72))
    d.arc([x + w * 0.2, y + h * 0.10, x + w * 0.8, y + h * 0.55], start=180, end=360,
          fill=(60, 64, 72), width=4)
    for px in (0.25, 0.5, 0.75):
        d.line([(x + w * px, y + h * 0.50), (x + w * px, y + h * 0.78)], fill=(60, 64, 72), width=3)
    # water
    for i in range(3):
        d.line([(x + 8, y + h * (0.66 + i * 0.10)), (x + w - 8, y + h * (0.66 + i * 0.10))],
               fill=(240, 232, 210), width=2)
    # explosion flash
    fx, fy = x + w * 0.68, y + h * 0.34
    d.polygon([(fx, fy - 14), (fx + 5, fy - 4), (fx + 14, fy - 6), (fx + 7, fy + 2),
               (fx + 12, fy + 10), (fx + 2, fy + 8), (fx, fy + 16), (fx - 3, fy + 7),
               (fx - 12, fy + 10), (fx - 6, fy + 1), (fx - 14, fy - 4), (fx - 5, fy - 5)],
              fill=(255, 190, 60))
    d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(255, 240, 180))

def ill_cyclone(d, x, y, w, h):
    vgrad(d, x, y, w, h, (32, 44, 74), (68, 88, 122))
    cx, cy = x + w * 0.5, y + h * 0.52
    for r in (34, 26, 18, 10):
        d.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], start=200, end=500,
              fill=(205, 212, 228), width=4)
    d.ellipse([cx - 6, cy - 5, cx + 6, cy + 5], fill=(240, 240, 240))
    # rain
    for i in range(8):
        rx = x + 8 + i * (w - 16) / 7
        d.line([(rx, y + h - 18), (rx - 4, y + h - 6)], fill=(195, 200, 220), width=2)

def ill_denmark(d, x, y, w, h):
    vgrad(d, x, y, w, h, (232, 226, 212), (205, 205, 200))
    # Greenland shape
    d.polygon([(x + w * 0.18, y + h * 0.30), (x + w * 0.42, y + h * 0.14),
               (x + w * 0.72, y + h * 0.22), (x + w * 0.78, y + h * 0.48),
               (x + w * 0.58, y + h * 0.72), (x + w * 0.34, y + h * 0.66),
               (x + w * 0.20, y + h * 0.50)], fill=(245, 245, 242))
    d.polygon([(x + w * 0.18, y + h * 0.30), (x + w * 0.42, y + h * 0.14),
               (x + w * 0.72, y + h * 0.22), (x + w * 0.78, y + h * 0.48),
               (x + w * 0.58, y + h * 0.72), (x + w * 0.34, y + h * 0.66),
               (x + w * 0.20, y + h * 0.50)], outline=(120, 130, 140))
    flag_dk(d, x + w - 34, y + h - 30, 28, 19)
    rrect(d, [x + 6, y + 6, x + 74, y + 26], fill=NAVY, radius=4)
    text(d, (x + 40, y + 16), "109\u20130", font(F_SANS_BLK, 12), fill=WHITE, anchor="mm")

def ill_gta(d, x, y, w, h):
    vgrad(d, x, y, w, h, (90, 50, 110), (240, 130, 80))
    d.ellipse([x + w * 0.62, y + h * 0.12, x + w * 0.62 + 26, y + h * 0.12 + 26],
              fill=(255, 210, 120))
    skyline(d, x + 4, y + h - 6, x + w - 4, int(h * 0.6), (30, 20, 45), seed=5)
    text(d, (x + 8, y + h - 22), "VI", font(F_SANS_BLK, 16), fill=WHITE, anchor="la")
    d.line([(x + 8, y + h - 6), (x + 28, y + h - 6)], fill=GOLD_L, width=2)

def ill_gaza(d, x, y, w, h):
    vgrad(d, x, y, w, h, (240, 205, 140), (220, 160, 100))
    # road in perspective
    d.polygon([(x + w * 0.42, y + h * 0.30), (x + w * 0.58, y + h * 0.30),
               (x + w * 0.95, y + h), (x + w * 0.05, y + h)], fill=(90, 88, 84))
    d.line([(x + w * 0.5, y + h * 0.32), (x + w * 0.5, y + h)], fill=(250, 220, 130), width=3)
    # barrier
    d.rectangle([x + w * 0.30, y + h * 0.24, x + w * 0.70, y + h * 0.32], fill=(200, 60, 50))
    d.line([(x + w * 0.32, y + h * 0.24), (x + w * 0.32, y + h * 0.18)], fill=(60, 60, 60), width=2)
    d.line([(x + w * 0.68, y + h * 0.24), (x + w * 0.68, y + h * 0.18)], fill=(60, 60, 60), width=2)
    # sun
    d.ellipse([x + w * 0.70, y + 4, x + w * 0.70 + 20, y + 24], fill=(255, 240, 180))

def ill_apec(d, x, y, w, h):
    vgrad(d, x, y, w, h, (242, 238, 228), (215, 212, 200))
    # declaration scroll
    d.rectangle([x + w * 0.18, y + h * 0.18, x + w * 0.82, y + h * 0.82], fill=WHITE)
    d.rectangle([x + w * 0.18, y + h * 0.18, x + w * 0.82, y + h * 0.82],
                outline=(150, 140, 120), width=2)
    for i in range(4):
        ly = y + h * (0.34 + i * 0.13)
        d.line([(x + w * 0.28, ly), (x + w * 0.72, ly)], fill=(120, 120, 115), width=2)
    d.ellipse([x + w * 0.44, y + h * 0.26, x + w * 0.56, y + h * 0.26 + 10], fill=CRIMSON)
    # small flags row
    flag_us(d, x + 6, y + h - 18, 18, 12)
    flag_cn(d, x + 28, y + h - 18, 18, 12)
    flag_ru(d, x + 50, y + h - 18, 18, 12)

def ill_sanaa(d, x, y, w, h):
    vgrad(d, x, y, w, h, (60, 50, 80), (190, 110, 70))
    skyline(d, x + 4, y + h - 6, x + w - 4, int(h * 0.5), (25, 20, 35), seed=9)
    # smoke columns
    for i, (sx, sy, r) in enumerate([(w * 0.30, h * 0.28, 10), (w * 0.36, h * 0.16, 13), (w * 0.62, h * 0.22, 11)]):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(120, 112, 108))
    # flash
    fx, fy = x + w * 0.72, y + h * 0.42
    d.polygon([(fx, fy - 12), (fx + 4, fy - 3), (fx + 12, fy - 5), (fx + 6, fy + 2),
               (fx + 10, fy + 9), (fx + 1, fy + 7), (fx, fy + 14), (fx - 3, fy + 6),
               (fx - 10, fy + 9), (fx - 5, fy + 1), (fx - 12, fy - 3), (fx - 4, fy - 4)],
              fill=(255, 190, 60))
    rrect(d, [x + 2, y + 4, x + w - 2, y + 22], fill=CRIMSON, radius=4)
    text(d, (x + w / 2, y + 13), "11 KILLED", font(F_SANS_BLK, 8), fill=WHITE, anchor="mm")

def ill_canberra(d, x, y, w, h):
    vgrad(d, x, y, w, h, (230, 224, 210), (200, 200, 195))
    # parliament building
    d.rectangle([x + w * 0.14, y + h * 0.48, x + w * 0.86, y + h * 0.86], fill=(245, 245, 242))
    d.polygon([(x + w * 0.30, y + h * 0.48), (x + w * 0.70, y + h * 0.48),
               (x + w * 0.50, y + h * 0.28)], fill=(230, 228, 222))
    d.line([(x + w * 0.50, y + h * 0.28), (x + w * 0.50, y + h * 0.10)], fill=(80, 80, 80), width=2)
    d.rectangle([x + w * 0.46, y + h * 0.10, x + w * 0.54, y + h * 0.20], fill=(30, 60, 120))
    for i in range(4):
        cx = x + w * (0.26 + i * 0.16)
        d.rectangle([cx, y + h * 0.56, cx + 8, y + h * 0.86], fill=(120, 130, 140))
    # rising bar chart
    for i, bh in enumerate((8, 14, 20, 28)):
        bx = x + w * 0.14 + i * 12
        d.rectangle([bx, y + h * 0.44 - bh, bx + 8, y + h * 0.44], fill=TEAL)
    rrect(d, [x + w - 52, y + 6, x + w - 6, y + 26], fill=NAVY, radius=4)
    text(d, (x + w - 29, y + 16), "4.9%", font(F_SANS_BLK, 11), fill=WHITE, anchor="mm")

ILL = {"COP31": ill_globe, "KYIV": ill_kyiv, "KERCH": ill_kerch, "CYCLONE": ill_cyclone,
       "DENMARK": ill_denmark, "GTA": ill_gta, "GAZA": ill_gaza, "APEC": ill_apec,
       "SANAA": ill_sanaa, "CANBERRA": ill_canberra}

# ---------- informative world map (own simplified continents) ----------
def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_D)
    # simplified continents (rough shapes, drawn from scratch)
    land = (222, 205, 160)
    d.polygon([(x + 18, y + 18), (x + 60, y + 8), (x + 95, y + 14), (x + 88, y + 30),
               (x + 70, y + 42), (x + 45, y + 48), (x + 30, y + 38), (x + 16, y + 30)], fill=land)
    d.polygon([(x + 78, y + 52), (x + 100, y + 50), (x + 108, y + 62),
               (x + 96, y + 82), (x + 82, y + 70)], fill=land)
    d.polygon([(x + 185, y + 12), (x + 215, y + 6), (x + 230, y + 14), (x + 222, y + 26),
               (x + 200, y + 28), (x + 188, y + 20)], fill=land)
    d.polygon([(x + 190, y + 34), (x + 225, y + 32), (x + 240, y + 44), (x + 228, y + 66),
               (x + 208, y + 72), (x + 196, y + 52)], fill=land)
    d.polygon([(x + 235, y + 8), (x + 300, y + 4), (x + 340, y + 12), (x + 360, y + 24),
               (x + 340, y + 36), (x + 300, y + 40), (x + 270, y + 34), (x + 245, y + 28),
               (x + 232, y + 18)], fill=land)
    d.polygon([(x + 330, y + 62), (x + 355, y + 60), (x + 362, y + 70), (x + 340, y + 74)], fill=land)
    # graticule
    for gx in range(x + 40, x + w - 20, 40):
        d.line([(gx, y + 4), (gx, y + h - 4)], fill=(38, 48, 74), width=1)
    for gy in range(y + 20, y + h - 10, 22):
        d.line([(x + 4, gy), (x + w - 4, gy)], fill=(38, 48, 74), width=1)
    # markers with labels (leader line from dot to label pill)
    fnt = font(F_SANS_B, 10)
    rects = []
    for label, (mx, my), col, (dx, dy) in MAP_MARKERS:
        px, py = x + mx, y + my
        tw = d.textlength(label, font=fnt)
        lx, ly = px + dx, py + dy
        rects.append((lx - 3, ly - 2, lx + tw + 3, ly + 12, label))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                print(f"WARN map labels overlap: {a[4]} vs {b[4]}")
    for label, (mx, my), col, (dx, dy) in MAP_MARKERS:
        px, py = x + mx, y + my
        tw = d.textlength(label, font=fnt)
        lx, ly = px + dx, py + dy
        d.line([(px, py), (lx + tw / 2, ly + 12 if dy > 0 else ly - 2)],
               fill=(200, 210, 225), width=1)
        d.rectangle([lx - 3, ly - 2, lx + tw + 3, ly + 12], fill=(8, 16, 34))
        d.text((lx, ly), label, font=fnt, fill=WHITE, anchor="la")
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=col)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], outline=WHITE, width=1)

# ---------- layout ----------
def feature_strip(d, x, y, w, h, key, place_topic, headline, deck, source,
                  ill_w, hl_size=13, deck_size=10.5, show_source=True):
    rrect(d, [x, y, x + w, y + h], fill=PANEL, outline=(205, 198, 182), width=1, radius=3)
    ILL[key](d, x + 4, y + 4, ill_w, h - 8)
    tx = x + ill_w + 12
    tw = x + w - 10 - tx
    cy = y + 7
    text(d, (tx, cy), place_topic, font(F_SANS_B, 9), fill=CRIMSON, anchor="la")
    cy += 13
    hl = wrap(d, headline, font(F_DISP_B, hl_size), tw)
    if len(hl) > 2:
        print(f"WARN headline wraps to {len(hl)}: {headline}")
    cy = para(d, tx, cy, hl, font(F_DISP_B, hl_size), fill=NAVY, leading=int(hl_size * 1.15))
    cy += 2
    dk = wrap(d, deck, font(F_SANS, deck_size), tw)
    if len(dk) > 2:
        print(f"WARN deck wraps to {len(dk)}: {deck}")
    cy = para(d, tx, cy, dk, font(F_SANS, deck_size), fill=INK, leading=int(deck_size * 1.2))
    if show_source:
        text(d, (tx, y + h - 13), source, font(F_SANS, 9), fill=GREY, anchor="la")
    return cy

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # border
    d.rectangle([6, 6, W - 6, H - 6], outline=CRIMSON, width=2)
    # ---- top bar: small masthead, small date, scope in the middle ----
    text(d, (14, 14), "THE WORLD IN ONE DAY", font(F_SANS_BLK, 19), fill=CRIMSON, anchor="la")
    text(d, (512, 24), "28 STORIES", font(F_SANS_B, 11), fill=GREY, anchor="ma")
    text(d, (1010, 15), "THURSDAY 19 NOVEMBER 2026", font(F_SERIF_B, 18), fill=NAVY, anchor="ra")
    d.line([(14, 42), (1010, 42)], fill=GOLD, width=2)
    # ---- ONE big hero: the AI editorial illustration ----
    hero = cover_crop_hero(HERO_ASSET, 996, 244)
    img.paste(hero, (14, 48))
    d.rectangle([14, 48, 1010, 292], outline=(150, 120, 80), width=1)
    # small label so the AI picture is not mistaken for a real photograph:
    # a dark tag with a thin gold outline, so it reads as a deliberate
    # editorial tag, not a stray dark blob on the picture
    lx0, ly0, lx1, ly1 = 808, 259, 1003, 285
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=4, fill=NAVY_D,
                        outline=GOLD_L, width=1)
    text(d, ((lx0 + lx1) / 2, (ly0 + ly1) / 2), "EDITORIAL ILLUSTRATION",
         font(F_SANS_B, 10), fill=WHITE, anchor="mm")
    text(d, (14, 298), HERO[0], font(F_DISP_B, 27), fill=NAVY, anchor="la")
    text(d, (14, 330), HERO[1] + "  \u2014  " + HERO[2], font(F_SANS, 13), fill=GREY, anchor="la")
    # ---- two main panels: ICJ wide, Nasdaq narrow and dark ----
    py, ph = 356, 182
    # ICJ (light, wide)
    rrect(d, [14, py, 600, py + ph], fill=PANEL, outline=(205, 198, 182), width=1, radius=3)
    ill_icj(d, 18, py + 4, 578, 92)
    text(d, (24, py + 104), "THE HAGUE \u00b7 JUSTICE", font(F_SANS_B, 10), fill=CRIMSON, anchor="la")
    text(d, (24, py + 120), PANEL_ICJ[0], font(F_DISP_B, 22), fill=NAVY, anchor="la")
    text(d, (24, py + 148), PANEL_ICJ[1], font(F_SANS, 12), fill=INK, anchor="la")
    text(d, (24, py + 166), PANEL_ICJ[2], font(F_SANS, 9), fill=GREY, anchor="la")
    # Nasdaq (dark, narrow)
    rrect(d, [608, py, 1010, py + ph], fill=NAVY_D, outline=NAVY_D, width=1, radius=3)
    ill_nasdaq(d, 612, py + 4, 394, 92)
    text(d, (620, py + 104), "NEW YORK \u00b7 MARKETS", font(F_SANS_B, 10), fill=GOLD_L, anchor="la")
    text(d, (620, py + 120), PANEL_NASDAQ[0], font(F_DISP_B, 19), fill=WHITE, anchor="la")
    text(d, (620, py + 148), PANEL_NASDAQ[1], font(F_SANS, 11), fill=(205, 220, 235), anchor="la")
    text(d, (620, py + 166), PANEL_NASDAQ[2], font(F_SANS, 9), fill=GOLD_L, anchor="la")
    # ---- asymmetric features: 2, then 3, then 5 ----
    # row 1: COP31 wide + Kyiv
    feature_strip(d, 14, 546, 546, 80, "COP31", *FEAT_R1[0], ill_w=120, hl_size=14)
    feature_strip(d, 568, 546, 442, 80, "KYIV", *FEAT_R1[1], ill_w=120, hl_size=14)
    # row 2: Kerch + Cyclone + Denmark
    feature_strip(d, 14, 634, 326, 80, "KERCH", *FEAT_R2[0], ill_w=88, hl_size=13)
    feature_strip(d, 348, 634, 326, 80, "CYCLONE", *FEAT_R2[1], ill_w=88, hl_size=13)
    feature_strip(d, 682, 634, 328, 80, "DENMARK", *FEAT_R2[2], ill_w=88, hl_size=13)
    # row 3: five compact strips, uneven widths, no per-strip source line
    # (sources are in the footer); smaller headline so nothing wraps past 2 lines
    r3 = [(14, 184, "GTA", FEAT_R3[0]), (206, 210, "GAZA", FEAT_R3[1]),
          (424, 200, "APEC", FEAT_R3[2]), (632, 190, "SANAA", FEAT_R3[3]),
          (830, 180, "CANBERRA", FEAT_R3[4])]
    for fx, fw, key, feat in r3:
        feature_strip(d, fx, 722, fw, 76, key, *feat, ill_w=50, hl_size=11,
                      deck_size=10, show_source=False)
    # ---- bottom: informative map + digest ----
    # map panel
    rrect(d, [14, 806, 430, 954], fill=NAVY_D, outline=NAVY_D, width=1, radius=3)
    text(d, (24, 812), "WHERE THE DAY HAPPENED", font(F_SANS_BLK, 12), fill=WHITE, anchor="la")
    text(d, (420, 814), "8 biggest stories", font(F_SANS, 9), fill=(170, 185, 205), anchor="ra")
    draw_map(d, 22, 830, 400, 88)
    text(d, (222, 926), REGION_COUNTS, font(F_SANS, 9.5), fill=(190, 200, 215), anchor="ma")
    # digest panel
    text(d, (438, 812), "THE DAY IN BRIEF \u2014 15 MORE STORIES", font(F_SANS_BLK, 12), fill=NAVY, anchor="la")
    d.line([(438, 830), (1010, 830)], fill=GOLD, width=2)
    col_x = [438, 728]
    col_w = [282, 282]
    for i, (place, head) in enumerate(DIGEST):
        cx = col_x[i // 8]
        cy = 838 + (i % 8) * 15
        line = place + " \u2014 " + head
        lw = d.textlength(line, font=font(F_SANS, 11))
        if lw > col_w[i // 8]:
            print(f"WARN digest too long ({lw:.0f} > {col_w[i // 8]}): {line}")
        text(d, (cx, cy), place, font(F_SANS_B, 11), fill=CRIMSON, anchor="la")
        pw = d.textlength(place + " \u2014 ", font=font(F_SANS_B, 11))
        text(d, (cx + pw, cy), head, font(F_SANS, 11), fill=INK, anchor="la")
    # ---- footer ----
    fy = 958
    text(d, (14, fy), FOOTER_SRC, font(F_SANS, 10), fill=GREY, anchor="la")
    fy += 14
    fdl = wrap(d, FOOTER_DATE, font(F_SANS, 10), 996)
    fy = para(d, 14, fy, fdl, font(F_SANS, 10), fill=GREY, leading=12)
    fy += 2
    text(d, (14, fy), FOOTER_NOTE, font(F_SERIF_I, 9.5), fill=GREY, anchor="la")
    fy += 12
    print(f"final_y={fy}")
    img.save(OUT)
    print(f"saved {OUT} ({img.size[0]}, {img.size[1]})")

if __name__ == "__main__":
    main()
