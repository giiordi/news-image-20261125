#!/usr/bin/env python3
"""The World Today - Wednesday 25 November 2026.

A front-page newspaper poster summing up 25 November 2026 world news
in one image: a big lead story (Pakistan reaches orbit aboard
Shenzhou-24), five more stories in a grid, and a day-in-numbers box.

Stdlib only. Own Canvas class, own 5x7 bitmap font, own PNG writer.
main.py copies the committed entry.png into $MAKEFUN_OUTPUT_DIR, and
renders the same image from code if entry.png is ever missing.
"""

import math
import os
import shutil
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 241, 222)
INK = (26, 26, 26)
RED = (178, 34, 34)
NAVY = (31, 58, 95)
GOLD = (201, 162, 39)
GREY = (112, 106, 90)
WHITE = (255, 255, 255)
EARTH = (46, 92, 150)
SKY = (96, 140, 190)
GREEN = (52, 110, 64)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, written by hand for this entry. '#' is on, '.' is off.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.clip = None  # optional (x0, y0, x1, y1) clip box
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, c):
        r, g, b = c
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            if self.clip is not None:
                cx0, cy0, cx1, cy1 = self.clip
                if not (cx0 <= x < cx1 and cy0 <= y < cy1):
                    return
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for deg in range(0, 360):
            a = math.radians(deg)
            self.set(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), c)
            self.set(int(cx + rx * math.cos(a)) + 1, int(cy + ry * math.sin(a)), c)

    def triangle(self, p0, p1, p2, c):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]
        for yy in range(min(ys), max(ys) + 1):
            row = []
            for (ax, ay), (bx, by) in ((p0, p1), (p1, p2), (p2, p0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    row.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(row) >= 2:
                for xx in range(int(min(row)), int(max(row)) + 1):
                    self.set(xx, yy, c)

    # ------------------------------------------------------------ text
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == '#':
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def wrap(self, text, maxw, scale):
        words = text.split(' ')
        lines = []
        cur = ''
        for word in words:
            trial = (cur + ' ' + word).strip()
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, text, scale, maxw, leading, c):
        for line in self.wrap(text, maxw, scale):
            self.text(x, y, line, scale, c)
            y += leading
        return y


# ---------------------------------------------------------------- poster
def draw_space_panel(cv, x, y, w, h):
    """Navy panel with Earth, orbit and a rocket for the lead story."""
    cv.rect(x, y, w, h, NAVY)
    cv.clip = (x, y, x + w, y + h)
    # caption at the top
    cv.text(x + 14, y + 12, "SHENZHOU-24 - TIANGONG", 2, WHITE)
    # stars
    for sx, sy in ((x + 20, y + 40), (x + 60, y + 56), (x + 110, y + 38),
                   (x + 160, y + 52), (x + 210, y + 40), (x + 260, y + 58),
                   (x + 300, y + 44), (x + 90, y + 70), (x + 240, y + 78),
                   (x + 40, y + 84), (x + 290, y + 88)):
        cv.rect(sx, sy, 3, 3, WHITE)
    # Earth rising at the bottom right (clipped to the panel)
    cv.circle(x + w - 25, y + h + 60, 95, EARTH)
    cv.circle(x + w - 50, y + h + 35, 16, GREEN)
    cv.circle(x + w, y + h + 50, 12, GREEN)
    # orbit ellipse
    cv.ellipse(x + 150, y + 92, 130, 44, GOLD)
    # rocket on the orbit, nose up-right
    rx, ry = x + 232, y + 58
    cv.triangle((rx, ry - 22), (rx - 11, ry + 8), (rx + 11, ry + 8), WHITE)
    cv.rect(rx - 8, ry + 8, 16, 16, RED)
    cv.triangle((rx - 8, ry + 24), (rx, ry + 40), (rx + 8, ry + 24), GOLD)
    cv.clip = None


def story_cell(cv, x, y, w, kicker, headline, summary):
    cv.text(x, y, kicker, 2, RED)
    y += 26
    y = cv.para(x, y, headline, 3, w, 24, INK)
    y += 6
    cv.para(x, y, summary, 2, w, 16, INK)


def render():
    cv = Canvas(W, H, PAPER)
    # double outer border
    cv.rect(8, 8, W - 16, 3, INK)
    cv.rect(8, H - 11, W - 16, 3, INK)
    cv.rect(8, 8, 3, H - 16, INK)
    cv.rect(W - 11, 8, 3, H - 16, INK)
    cv.rect(16, 16, W - 32, 1, INK)
    cv.rect(16, H - 17, W - 32, 1, INK)
    cv.rect(16, 16, 1, H - 32, INK)
    cv.rect(W - 17, 16, 1, H - 32, INK)

    # masthead
    title = "THE WORLD TODAY"
    cv.text((W - cv.text_w(title, 9)) // 2, 34, title, 9, INK)
    cv.hline(24, 116, W - 48, INK, 2)
    date = "WEDNESDAY 25 NOVEMBER 2026"
    cv.text((W - cv.text_w(date, 4)) // 2, 126, date, 4, RED)
    cv.text(24, 132, "EST. 2026", 2, GREY)
    right = "SIX STORIES"
    cv.text(W - 24 - cv.text_w(right, 2), 132, right, 2, GREY)
    cv.hline(24, 160, W - 48, INK, 3)
    cv.hline(24, 166, W - 48, INK, 1)

    # ---- lead story: space
    cv.text(24, 182, "SPACE - CHINA  |  LEAD STORY", 3, RED)
    cv.text(24, 212, "PAKISTAN REACHES ORBIT", 5, INK)
    cv.text(24, 252, "FIRST FOREIGNER ON TIANGONG", 5, INK)
    lead = ("Shenzhou-24 launched Wednesday carrying Muhammad "
            "Zeeshan Ali, 40, a Pakistan Air Force pilot - the first "
            "Pakistani in orbit and the first foreign astronaut aboard "
            "China's Tiangong station. The crew spends a week in orbit "
            "on four Pakistani biotech tests.")
    cv.para(24, 296, lead, 3, 620, 20, INK)
    draw_space_panel(cv, 664, 296, 336, 152)

    cv.hline(24, 462, W - 48, INK, 2)

    # ---- grid of five stories + day in numbers
    col_w = 476
    xs = (24, 524)
    rows = (478, 642, 806)
    # vertical divider between the two columns
    for ry in rows:
        cv.vline(512, ry, 152, GREY, 1)
    cv.hline(24, 634, W - 48, GREY, 1)
    cv.hline(24, 798, W - 48, GREY, 1)

    story_cell(cv, xs[0], rows[0], col_w,
               "YEMEN - RED SEA",
               "HOUTHIS THREATEN JEDDAH AND SAUDI RED SEA PORTS",
               "Houthis hit Riyadh's tallest tower, wounding 11, and "
               "vowed to strike Jeddah if Hodeidah is attacked. The "
               "Saudi-led coalition hit Hodeidah, Saada and Amran.")
    story_cell(cv, xs[1], rows[0], col_w,
               "UKRAINE - WAR",
               "KYIV SAYS IT HIT A RUSSIAN CARGO SHIP IN THE GULF OF FINLAND",
               "Zelenskiy confirmed the strike. A Russian strike killed "
               "two in Odesa and drones hit Kyiv. Norway urged caution.")
    story_cell(cv, xs[0], rows[1], col_w,
               "MARKETS - STOCKS",
               "AI REBOUND STUMBLES AS CHIP STOCKS TUMBLE",
               "Nasdaq fell 1.5% on Tuesday; Nvidia -6%, Micron -11%, "
               "chip index -8%. Washington is preparing tariff hikes on "
               "China, the EU and 14 other economies.")
    story_cell(cv, xs[1], rows[1], col_w,
               "CHINA - POLITICS",
               "SHANGHAI PARTY CHIEF CHEN JINING UNDER INVESTIGATION",
               "The fourth Politburo member probed since 2025. "
               "Shanghai's leadership pledged loyalty to Beijing.")
    story_cell(cv, xs[0], rows[2], col_w,
               "BANGLADESH - WORKERS",
               "GARMENT WAGE UP 36% TO $139 AFTER WEEKS OF PROTESTS",
               "The new minimum takes effect on 1 December after "
               "protests shut factories across the country.")

    # day in numbers box
    bx, by = xs[1], rows[2]
    cv.text(bx, by, "THE DAY IN NUMBERS", 2, RED)
    numbers = [
        ("1", "first Pakistani in orbit"),
        ("11", "wounded in the Riyadh tower strike"),
        ("1.5%", "Nasdaq fall on Tuesday"),
        ("36%", "garment wage rise in Bangladesh"),
        ("$139", "new monthly garment minimum"),
        ("4", "Politburo members probed since 2025"),
    ]
    ny = by + 26
    for num, label in numbers:
        cv.text(bx, ny, num, 2, INK)
        cv.text(bx + 64, ny, label, 2, INK)
        ny += 18

    # footer
    cv.hline(24, 972, W - 48, INK, 2)
    foot = "SOURCES: REUTERS - AP - WSJ  |  ALL EVENTS FIRST REPORTED 24-25 NOVEMBER 2026"
    cv.text((W - cv.text_w(foot, 2)) // 2, 986, foot, 2, GREY)
    return cv


def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def to_png(cv):
    raw = b"".join(
        b"\x00" + bytes(cv.px[y * W * 3:(y + 1) * W * 3])
        for y in range(H)
    )
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(raw, 9))
            + _chunk(b"IEND", b""))


def render_bytes():
    return to_png(render())


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
    else:
        with open(dst, "wb") as f:
            f.write(render_bytes())


if __name__ == "__main__":
    main()
