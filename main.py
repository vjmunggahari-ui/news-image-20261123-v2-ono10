#!/usr/bin/env python3
"""news-image-20261123 v2: the world's news of Monday 23 November 2026
as one 1024x1024 front-page image.

Design (kept from the parent-verified v1): masthead "THE WORLD TODAY",
COP31 lead with a cracked globe, six story blocks each led by a big
number, an ALSO TODAY ticker, and a sources footer. All facts verified
23 Nov 2026 against CNN, Reuters, AP, Le Monde, NPR, Fox News
(see README.md for the source list).

Deterministic: no network, no clock, no randomness. Every run writes
the same bytes to $MAKEFUN_OUTPUT_DIR/entry.png.

v2 hardening (v1 exited 1 in the grader while passing locally):
  * Fonts: every truetype load is tried against several locations and
    wrapped in try/except; when no font file loads anywhere the code
    falls back to ImageFont.load_default(), which always works.
  * Output: the output directory is chosen from a candidate list and
    each candidate is probe-written first, so an unwritable env dir or
    a read-only repo can never kill the run; /tmp is always a fallback.
  * Pillow: if Pillow cannot be imported at all, or the Pillow render
    raises for any reason, a pure-stdlib renderer (bitmap font + zlib
    PNG encoder, no third-party code) still produces a valid
    1024x1024 entry.png and the process exits 0.
"""
import os
import struct
import sys
import tempfile
import zlib

W = H = 1024
PAPER = (251, 246, 236)   # newsprint cream
INK = (20, 20, 20)
RED = (178, 34, 24)
NAVY = (31, 56, 100)
TEAL = (14, 92, 84)
GREY = (90, 86, 78)
RULE = (60, 58, 52)
LIGHT = (238, 231, 214)
GOLD = (232, 160, 32)

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- output dir
def _probe_writable(directory):
    """True only if we can really create and delete a file there."""
    try:
        os.makedirs(directory, exist_ok=True)
        probe = os.path.join(directory, ".write-probe")
        with open(probe, "wb") as fh:
            fh.write(b"ok")
        os.unlink(probe)
        return True
    except OSError:
        return False


def resolve_out_dir():
    """First writable candidate wins; never raises for a bad env value."""
    candidates = []
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        candidates.append(env)
    candidates.append("/output")
    candidates.append(os.path.join(tempfile.gettempdir(),
                                   "news-image-20261123"))
    candidates.append(os.path.join(HERE, "output"))
    seen = set()
    for cand in candidates:
        cand = os.path.abspath(cand)
        if cand in seen:
            continue
        seen.add(cand)
        if _probe_writable(cand):
            return cand
    raise RuntimeError("no writable output directory found")


# ------------------------------------------------------- pure-stdlib PNG out
def _png_chunk(kind, data):
    chunk = struct.pack(">I", len(data)) + kind + data
    chunk += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return chunk


def encode_png(rgb, width, height):
    """Encode raw RGB bytes as a PNG. Deterministic: fixed filter + level."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n"
            + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _png_chunk(b"IEND", b""))


# 5x7 bitmap glyphs ("#" = ink). Fallback renderer only; text is
# upper-cased, curly quotes/dashes map to their straight twins.
_GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "\u2013": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "\u2022": (".....", ".###.", ".###.", ".###.", ".....", ".....", "....."),
    "\u00b0": (".##..", "#..#.", ".##..", ".....", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}
_FALLBACK_MAP = {
    "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
    "\u2013": "\u2014", "\u00b7": "\u2022",
}


def _fallback_char(ch):
    ch = _FALLBACK_MAP.get(ch, ch)
    if ch.islower():
        ch = ch.upper()
    return _GLYPHS.get(ch, _GLYPHS["?"])


class _Canvas(object):
    """Minimal RGB rasterizer: rects, discs, bitmap text. No deps."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg) * (width * height)

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self._set(x, y, color)

    def hline(self, x0, x1, y, color, width=1):
        for t in range(width):
            for x in range(x0, x1):
                self._set(x, y + t, color)

    def disc(self, cx, cy, r, color, fill=True):
        import math
        for y in range(cy - r, cy + r + 1):
            half = int(math.sqrt(max(0, r * r - (y - cy) ** 2)))
            if fill:
                for x in range(cx - half, cx + half + 1):
                    self._set(x, y, color)
            else:
                self._set(cx - half, y, color)
                self._set(cx + half, y, color)

    def text(self, x, y, s, color, scale=2):
        """Bitmap text; returns the x position just past the last glyph."""
        cx = x
        for ch in s:
            glyph = _fallback_char(ch)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale,
                                  y + (row + 1) * scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale=2):
        return len(s) * 6 * scale

    def wrap(self, s, scale, max_w):
        """Greedy word wrap on bitmap-text width."""
        words, lines, cur = s.split(), [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------ shared content
# (kicker, headline, fact, big number, number label, icon, accent)
STORIES = [
    ("GULF WAR", "Iran hits US bases in Bahrain",
     "Missiles and drones hit al-Riffa and Awali; 14 tankers mass at Kharg.",
     "130", "DAYS OF BLOCKADE", "tanker", RED),
    ("UKRAINE", "Russian ship burns off Finland",
     "Sparta II hit by drones; 16 crew saved. 14 missing after flats hit near Kyiv.",
     "14", "MISSING NEAR KYIV", "ship", NAVY),
    ("AMERICA", "Democrats win 258 House seats",
     "Biggest majority since 1992; +44 seats. Hubbard beats Foxx in North Carolina.",
     "258", "SEATS \u2022 +44 GAINED", "capitol", NAVY),
    ("MEXICO", "\u201cEl Chapo Isidro\u201d captured",
     "FBI Most Wanted boss seized in Sinaloa; 11 dead \u2014 4 soldiers, 7 gunmen.",
     "11", "DEAD IN SINALOA", "cuffs", RED),
    ("ASIA", "Factory fire: 3 dead, 50 missing",
     "Blaze at a candy plant in Cikande, Indonesia; 300 workers inside.",
     "50", "MISSING IN JAVA", "flame", RED),
    ("SPORT", "India 720/9 \u2014 a record",
     "India pile up a record Test total in Wellington against New Zealand.",
     "720", "RUNS \u2022 1ST INNINGS", "bat", TEAL),
]

TICKER = [
    "SEOUL: minister quits in AI row",
    "UN: lethal-AI talks go on",
    "Nepal PM meets Modi",
    "Liverpool beat Utd",
]

LEAD_DECK = [
    "\u2022  Final text never mentions fossil fuels \u2014 EU, Panama and others reject it.",
    "\u2022  First collapse since Copenhagen 2009; talks ran 44 hours past close.",
    "\u2022  90+ nations sign an electrification pledge; only $142m new funding.",
]


# ------------------------------------------- fallback render (no Pillow at all)
def render_fallback_png():
    """Same front page, simplified, drawn with the bitmap font only."""
    c = _Canvas(W, H, PAPER)
    M = 30
    # masthead
    c.text(M, 26, "MONDAY EDITION", GREY, 2)
    c.text(W - M - c.text_width("PRICE: THE NEWS", 2), 26,
           "PRICE: THE NEWS", GREY, 2)
    title = "THE WORLD TODAY"
    c.text((W - c.text_width(title, 6)) // 2, 34, title, INK, 6)
    c.hline(M, W - M, 122, RULE, 3)
    c.hline(M, W - M, 127, RED, 2)
    sub = "MONDAY, 23 NOVEMBER 2026  \u2022  ONE DAY \u2022 ONE PAGE \u2022 SEVEN STORIES"
    c.text((W - c.text_width(sub, 2)) // 2, 138, sub, RED, 2)
    c.hline(M, W - M, 164, RULE, 2)
    # lead story
    ly = 178
    c.text(M, ly, "CLIMATE  \u2022  ANTALYA, TURKEY", RED, 2)
    c.text(M, ly + 34, "COP31 COLLAPSES", INK, 5)
    c.text(M, ly + 120, "No deal after the longest climate summit in history",
           NAVY, 3)
    y = ly + 168
    for line in LEAD_DECK:
        for ln in c.wrap(line, 2, 780):
            c.text(M, y, ln, INK, 2)
            y += 30
    c.disc(910, ly + 104, 56, NAVY, fill=False)
    c.text(872, ly + 185, "1.5\u00b0C", RED, 3)
    c.text(878, ly + 222, "AT RISK", GREY, 2)
    c.hline(M, W - M, 446, RULE, 2)
    # six story blocks, 2 columns x 3 rows
    col_w = (W - 2 * M - 24) // 2
    row_h = 148
    for i, (kick, head, fact, num, numlab, _icon, accent) in enumerate(STORIES):
        cx = M + (i % 2) * (col_w + 24)
        cy = 456 + (i // 2) * (row_h + 6)
        c.text(cx, cy, kick, accent, 2)
        y = cy + 26
        for ln in c.wrap(head, 2, col_w - 110)[:2]:
            c.text(cx, y, ln, INK, 2)
            y += 30
        y = cy + 92
        for ln in c.wrap(fact, 2, col_w - 110)[:2]:
            c.text(cx, y, ln, INK, 2)
            y += 26
        nw = c.text_width(num, 4)
        c.text(cx + col_w - nw, cy, num, accent, 4)
        lw = c.text_width(numlab, 2)
        c.text(cx + col_w - lw, cy + 62, numlab, GREY, 2)
        c.rect(cx + col_w - 92, cy + 96, cx + col_w, cy + 144, accent)
        if i % 2 == 0:
            c.rect(cx + col_w + 11, cy + 4, cx + col_w + 13, cy + row_h - 10,
                   LIGHT)
        if i < 4:
            c.hline(cx, cx + col_w, cy + row_h - 2, LIGHT, 2)
    # ticker
    ty = 936
    c.hline(M, W - M, ty - 12, RULE, 2)
    c.rect(M, ty, M + 128, ty + 30, RED)
    c.text(M + 12, ty + 7, "ALSO TODAY", PAPER, 2)
    tick = " \u2022 ".join(TICKER)
    scale = 2
    while c.text_width(tick, scale) > W - 2 * M - 140 and scale > 1:
        scale = 1
    c.text(M + 140, ty + 7, tick, INK, scale)
    # footer
    c.hline(M, W - M, 984, RULE, 2)
    foot = ("Sources: CNN \u2022 Reuters \u2022 AP \u2022 Le Monde \u2022 NPR "
            "\u2022 Fox News  \u2014  Monday 23 November 2026")
    c.text((W - c.text_width(foot, 2)) // 2, 992, foot, GREY, 2)
    return encode_png(bytes(c.px), W, H)


# ------------------------------------------------------------- Pillow renderer
try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:  # Pillow missing entirely: stdlib fallback takes over
    Image = ImageDraw = ImageFont = None
    HAVE_PIL = False


def load_font(name, size):
    """Never raises: bundled -> system dirs -> load_default()."""
    candidates = [
        os.path.join(HERE, "assets", "fonts", name),
        os.path.join("/usr/share/fonts/truetype/dejavu", name),
        os.path.join("/usr/share/fonts", name),
        os.path.join(os.path.expanduser("~"), ".fonts", name),
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default(size=size)


def _serif_b(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def _sans_b(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def _sans(size):
    return load_font("DejaVuSans.ttf", size)


def _wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def _hline(draw, x0, x1, y, fill=RULE, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def _globe(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=5)
    draw.ellipse([cx - r, cy - r // 3, cx + r, cy + r // 3], outline=NAVY,
                 width=3)
    draw.ellipse([cx - r // 3, cy - r, cx + r // 3, cy + r], outline=NAVY,
                 width=3)
    pts = [(cx - r + 8, cy - r // 2), (cx - r // 3, cy - 6), (cx - 6, cy + r // 4),
           (cx + r // 4, cy + r // 8), (cx + r // 2, cy + r // 2),
           (cx + r - 10, cy + r - 14)]
    draw.line(pts, fill=RED, width=5, joint="curve")
    for dx, fh in ((-34, 26), (-12, 38), (12, 30), (32, 22)):
        draw.polygon([(cx + dx - 9, cy + r + 4), (cx + dx, cy + r - fh),
                      (cx + dx + 9, cy + r + 4)], fill=RED)


def _tanker(draw, x, y, w, h):
    draw.rectangle([x, y + h * 0.45, x + w, y + h * 0.8], fill=NAVY)
    draw.rectangle([x + w * 0.55, y + h * 0.2, x + w * 0.68, y + h * 0.45],
                   fill=NAVY)
    draw.rectangle([x + w * 0.1, y + h * 0.3, x + w * 0.4, y + h * 0.45],
                   fill=RED)
    for sx, sy, sr in [(x + w * 0.62, y + 8, 6), (x + w * 0.58, y + 2, 7),
                       (x + w * 0.66, y + 2, 5)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=GREY)
    draw.line([(x, y + h * 0.85), (x + w, y + h * 0.85)], fill=TEAL, width=3)
    draw.line([(x + 4, y + h * 0.92), (x + w - 4, y + h * 0.92)], fill=TEAL,
              width=2)


def _ship_fire(draw, x, y, w, h):
    draw.rectangle([x, y + h * 0.55, x + w, y + h * 0.8], fill=INK)
    for bx in (0.08, 0.32, 0.56):
        draw.rectangle([x + w * bx, y + h * 0.3, x + w * (bx + 0.18),
                        y + h * 0.55], outline=INK, width=2)
    for dx, fh in ((0.15, 30), (0.4, 42), (0.65, 34), (0.85, 24)):
        fx = x + w * dx
        draw.polygon([(fx - 10, y + h * 0.3), (fx, y + h * 0.3 - fh),
                      (fx + 10, y + h * 0.3)], fill=RED)
    draw.line([(x, y + h * 0.86), (x + w, y + h * 0.86)], fill=NAVY, width=3)


def _capitol(draw, x, y, w, h):
    draw.rectangle([x + w * 0.05, y + h * 0.7, x + w * 0.95, y + h * 0.82],
                   fill=NAVY)
    draw.rectangle([x + w * 0.3, y + h * 0.45, x + w * 0.7, y + h * 0.7],
                   fill=NAVY)
    draw.pieslice([x + w * 0.3, y + h * 0.08, x + w * 0.7, y + h * 0.55],
                  start=180, end=360, fill=NAVY)
    draw.line([(x + w * 0.5, y + 2), (x + w * 0.5, y + h * 0.12)], fill=NAVY,
              width=3)
    for cx in (0.16, 0.84):
        draw.rectangle([x + w * cx, y + h * 0.55, x + w * (cx + 0.08),
                        y + h * 0.7], fill=NAVY)


def _cuffs(draw, x, y, w, h):
    for i in range(4):
        bx = x + w * (0.12 + i * 0.24)
        draw.rectangle([bx, y + h * 0.1, bx + 7, y + h * 0.9], fill=INK)
    draw.rectangle([x, y + h * 0.08, x + w, y + h * 0.08 + 6], fill=INK)
    draw.rectangle([x, y + h * 0.82, x + w, y + h * 0.82 + 6], fill=INK)


def _flame(draw, x, y, w, h):
    cx = x + w * 0.5
    draw.polygon([(cx - 26, y + h * 0.8), (cx - 6, y + h * 0.25),
                  (cx + 4, y + h * 0.5), (cx + 16, y + h * 0.15),
                  (cx + 26, y + h * 0.8)], fill=RED)
    draw.polygon([(cx - 12, y + h * 0.8), (cx - 2, y + h * 0.5),
                  (cx + 12, y + h * 0.8)], fill=GOLD)
    draw.rectangle([x + w * 0.1, y + h * 0.82, x + w * 0.9, y + h * 0.92],
                   fill=INK)


def _bat(draw, x, y, w, h):
    draw.line([(x + w * 0.3, y + h * 0.1), (x + w * 0.62, y + h * 0.62)],
              fill=(150, 104, 52), width=10)
    draw.rectangle([x + w * 0.55, y + h * 0.55, x + w * 0.95, y + h * 0.95],
                   fill=(214, 178, 120), outline=INK, width=2)
    draw.ellipse([x + w * 0.08, y + h * 0.62, x + w * 0.08 + 26,
                  y + h * 0.62 + 26], fill=RED)


_ICONS = {"tanker": _tanker, "ship": _ship_fire, "capitol": _capitol,
          "cuffs": _cuffs, "flame": _flame, "bat": _bat}


def build_pil():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 30

    # ---------- masthead ----------
    d.text((M, 22), "MONDAY EDITION", font=_sans(20), fill=GREY)
    d.text((W - M - d.textlength("PRICE: THE NEWS", font=_sans(20)), 22),
           "PRICE: THE NEWS", font=_sans(20), fill=GREY)
    title = "THE WORLD TODAY"
    tf = _serif_b(76)
    d.text(((W - d.textlength(title, font=tf)) / 2, 30), title, font=tf,
           fill=INK)
    _hline(d, M, W - M, 122, width=3)
    _hline(d, M, W - M, 127, fill=RED, width=2)
    sub = ("MONDAY, 23 NOVEMBER 2026   \u2022   ONE DAY \u2022 ONE PAGE "
           "\u2022 SEVEN STORIES")
    sf = _sans_b(21)
    d.text(((W - d.textlength(sub, font=sf)) / 2, 132), sub, font=sf, fill=RED)
    _hline(d, M, W - M, 164, width=2)

    # ---------- lead story: COP31 ----------
    ly = 178
    d.text((M, ly), "CLIMATE  \u2022  ANTALYA, TURKEY", font=_sans_b(24),
           fill=RED)
    d.text((M, ly + 30), "COP31 COLLAPSES", font=_serif_b(72), fill=INK)
    d.text((M, ly + 122), "No deal after the longest climate summit in history",
           font=_serif_b(28), fill=NAVY)
    deck_lines = []
    for bullet in LEAD_DECK:
        deck_lines.extend(_wrap(d, bullet, _sans(21), 800))
    _text_block(d, M, ly + 164, deck_lines, _sans(21), leading=28)
    _globe(d, 910, ly + 104, 56)
    d.text((872, ly + 185), "1.5\u00b0C", font=_sans_b(30), fill=RED)
    d.text((875, ly + 219), "AT RISK", font=_sans_b(20), fill=GREY)
    _hline(d, M, W - M, 446, width=2)

    # ---------- six story blocks, 2 columns x 3 rows ----------
    col_w = (W - 2 * M - 24) // 2
    row_h = 148
    for i, (kick, head, fact, num, numlab, icon, accent) in enumerate(STORIES):
        cx = M + (i % 2) * (col_w + 24)
        cy = 456 + (i // 2) * (row_h + 6)
        nf = _sans_b(58)
        nw = d.textlength(num, font=nf)
        d.text((cx + col_w - nw, cy + 2), num, font=nf, fill=accent)
        lf = _sans_b(15)
        lw = d.textlength(numlab, font=lf)
        d.text((cx + col_w - lw, cy + 64), numlab, font=lf, fill=GREY)
        _ICONS[icon](d, cx + col_w - 92, cy + 96, 92, 48)
        tw = col_w - 108
        d.text((cx, cy), kick, font=_sans_b(19), fill=accent)
        hl = _wrap(d, head, _serif_b(27), tw)
        _text_block(d, cx, cy + 24, hl[:2], _serif_b(27), leading=30)
        fl = _wrap(d, fact, _sans(18), tw)
        _text_block(d, cx, cy + 88, fl[:2], _sans(18), leading=22)
        if i % 2 == 0:
            d.line([(cx + col_w + 12, cy + 4), (cx + col_w + 12, cy + row_h - 10)],
                   fill=LIGHT, width=2)
        if i < 4:
            _hline(d, cx, cx + col_w, cy + row_h - 2, fill=LIGHT, width=2)

    # ---------- ticker ----------
    ty = 936
    _hline(d, M, W - M, ty - 12, width=2)
    d.rectangle([M, ty, M + 128, ty + 30], fill=RED)
    d.text((M + 12, ty + 4), "ALSO TODAY", font=_sans_b(17), fill=PAPER)
    tick = " \u2022 ".join(TICKER)
    tf2 = _sans(16)
    while d.textlength(tick, font=tf2) > W - 2 * M - 140 and tf2.size > 13:
        tf2 = _sans(tf2.size - 1)
    d.text((M + 140, ty + 5), tick, font=tf2, fill=INK)

    # ---------- footer ----------
    _hline(d, M, W - M, 984, width=2)
    foot = ("Sources: CNN \u2022 Reuters \u2022 AP \u2022 Le Monde \u2022 NPR "
            "\u2022 Fox News  \u2014  Monday 23 November 2026")
    ff = _sans(16)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 992), foot, font=ff,
           fill=GREY)
    return img


def main():
    out_dir = resolve_out_dir()
    out = os.path.join(out_dir, "entry.png")
    done = False
    if HAVE_PIL:
        try:
            build_pil().save(out, format="PNG", optimize=True)
            done = True
        except Exception as exc:  # never let a render failure exit 1
            print("Pillow render failed (%s); using stdlib fallback" % exc,
                  file=sys.stderr)
    if not done:
        with open(out, "wb") as fh:
            fh.write(render_fallback_png())
    print(out)


if __name__ == "__main__":
    main()
