#!/usr/bin/env python3
"""Meme Sprint 3 entry: "Rogue, But Helpful".

Draws one deterministic PNG meme using only the Python standard library:
a cheerful robot agent that "went rogue" by unsubscribing its human from
every newsletter and cleaning the Downloads folder. The picture is built
from flat shapes, bold outlines and a hand-made stroke font, so the
output bytes are identical on every run (no randomness, no timestamps,
no network, no files read).
"""

import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W = 1024
H = 1024

NAVY = (20, 28, 51)
CREAM = (246, 239, 220)
FLOOR = (233, 221, 190)
WHITE = (255, 255, 255)
INK = (20, 28, 51)
BLUE = (127, 178, 229)
PALE = (223, 233, 245)
YELLOW = (255, 176, 3)
FOLDER = (255, 210, 63)
FOLDER_FRONT = (255, 224, 110)
PINK = (244, 164, 180)
GREY = (176, 183, 196)
RED = (224, 82, 82)
WOOD = (196, 141, 87)

buf = bytearray(W * H * 3)


def span(xa, xb, y, color):
    """Fill one horizontal run of pixels."""
    if y < 0 or y >= H:
        return
    xa = max(0, int(xa))
    xb = min(W - 1, int(xb))
    if xa > xb:
        return
    i = (y * W + xa) * 3
    n = xb - xa + 1
    buf[i:i + 3 * n] = bytes(color) * n


def fill_rect(x0, y0, x1, y1, color):
    for y in range(int(y0), int(y1) + 1):
        span(x0, x1, y, color)


def fill_circle(cx, cy, r, color):
    cx = int(cx)
    cy = int(cy)
    r = int(math.ceil(r))
    for y in range(cy - r, cy + r + 1):
        d = y - cy
        half = int(math.sqrt(max(0.0, r * r - d * d)))
        span(cx - half, cx + half, y, color)


def ring_circle(cx, cy, r, width, color):
    """Draw a circle outline by stamping dots along its circumference."""
    steps = max(12, int(2 * math.pi * r))
    for i in range(steps + 1):
        a = 2 * math.pi * i / steps
        fill_circle(cx + r * math.cos(a), cy + r * math.sin(a), width / 2, color)


def fill_rrect(x0, y0, x1, y1, r, color):
    """Fill a rounded rectangle."""
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)
    r = int(r)
    for y in range(y0, y1 + 1):
        if y < y0 + r:
            d = y0 + r - y
        elif y > y1 - r:
            d = y - (y1 - r)
        else:
            d = 0
        if d:
            inset = r - int(math.sqrt(max(0.0, r * r - d * d)))
            span(x0 + inset, x1 - inset, y, color)
        else:
            span(x0, x1, y, color)


def fill_poly(pts, color):
    """Scanline-fill a polygon given as (x, y) points."""
    ys = [p[1] for p in pts]
    y_lo = int(math.floor(min(ys)))
    y_hi = int(math.ceil(max(ys)))
    n = len(pts)
    for y in range(y_lo, y_hi + 1):
        xs = []
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            if (ay <= y < by) or (by <= y < ay):
                xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            span(xs[i], xs[i + 1], y, color)


def stroke_poly(pts, width, color):
    """Stroke a polygon's edges with a thick line."""
    n = len(pts)
    for i in range(n):
        thick_line(pts[i], pts[(i + 1) % n], width, color)


def thick_line(p, q, width, color):
    """Draw a thick line by stamping filled circles along it."""
    x0, y0 = p
    x1, y1 = q
    dist = math.hypot(x1 - x0, y1 - y0)
    r = width / 2
    steps = max(1, int(dist / max(1.0, r * 0.6)))
    for i in range(steps + 1):
        t = i / steps
        fill_circle(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, color)


def stamp_path(pts, r, color):
    """Stamp circles along a polyline (used for letters and curves)."""
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        dist = math.hypot(x1 - x0, y1 - y0)
        steps = max(1, int(dist / max(1.0, r * 0.6)))
        for j in range(steps + 1):
            t = j / steps
            fill_circle(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, color)


# ---------------------------------------------------------------------------
# Hand-built stroke font. Each glyph is a list of strokes; each stroke is a
# polyline on a grid where x runs 0..5 and y runs 0..7 (0 = top).
# ---------------------------------------------------------------------------

GLYPHS = {
    "A": [[(0, 7), (2.5, 0), (5, 7)], [(1.3, 4.6), (3.7, 4.6)]],
    "B": [[(0, 0), (0, 7)],
          [(0, 0), (3.0, 0), (4.4, 1.0), (4.4, 2.5), (3.0, 3.4), (0, 3.4)],
          [(0, 3.4), (3.4, 3.4), (4.9, 4.3), (4.9, 6.0), (3.4, 7.0), (0, 7.0)]],
    "C": [[(4.8, 1.6), (3.8, 0.5), (2.2, 0), (1.0, 0.7), (0.3, 2.0),
           (0.3, 5.0), (1.0, 6.3), (2.2, 7.0), (3.8, 6.5), (4.8, 5.4)]],
    "D": [[(0, 0), (0, 7)],
          [(0, 0), (2.8, 0), (4.3, 1.2), (5, 2.8), (5, 4.2), (4.3, 5.8),
           (2.8, 7), (0, 7)]],
    "E": [[(5, 0), (0, 0), (0, 7), (5, 7)], [(0, 3.5), (3.8, 3.5)]],
    "F": [[(5, 0), (0, 0), (0, 7)], [(0, 3.5), (3.6, 3.5)]],
    "G": [[(4.8, 1.6), (3.8, 0.5), (2.2, 0), (1.0, 0.7), (0.3, 2.0),
           (0.3, 5.0), (1.0, 6.3), (2.2, 7.0), (4.0, 6.8), (5, 5.8),
           (5, 4.2), (3.2, 4.2)]],
    "H": [[(0, 0), (0, 7)], [(5, 0), (5, 7)], [(0, 3.5), (5, 3.5)]],
    "I": [[(2.5, 0), (2.5, 7)], [(0.6, 0), (4.4, 0)], [(0.6, 7), (4.4, 7)]],
    "K": [[(0, 0), (0, 7)], [(4.8, 0), (0.4, 3.4)], [(1.6, 2.4), (5, 7)]],
    "L": [[(0, 0), (0, 7), (5, 7)]],
    "M": [[(0, 7), (0, 0), (2.5, 3.2), (5, 0), (5, 7)]],
    "N": [[(0, 7), (0, 0), (5, 7), (5, 0)]],
    "O": [[(2.5, 0), (4.2, 0.6), (5, 2.2), (5, 4.8), (4.2, 6.4), (2.5, 7),
           (0.8, 6.4), (0, 4.8), (0, 2.2), (0.8, 0.6), (2.5, 0)]],
    "R": [[(0, 7), (0, 0)],
          [(0, 0), (3.2, 0), (4.7, 1.1), (4.7, 2.6), (3.2, 3.6), (0, 3.6)],
          [(2.6, 3.6), (5, 7)]],
    "S": [[(4.8, 1.4), (3.6, 0.3), (1.8, 0), (0.5, 0.9), (0.4, 2.2),
           (1.4, 3.2), (3.6, 3.9), (4.6, 4.8), (4.5, 6.1), (3.4, 6.9),
           (1.4, 7), (0.2, 6.0)]],
    "T": [[(0, 0), (5, 0)], [(2.5, 0), (2.5, 7)]],
    "U": [[(0, 0), (0, 4.8), (0.7, 6.3), (2.5, 7), (4.3, 6.3), (5, 4.8),
           (5, 0)]],
    "V": [[(0, 0), (2.5, 7), (5, 0)]],
    "W": [[(0, 0), (1.2, 7), (2.5, 2.6), (3.8, 7), (5, 0)]],
    "Y": [[(0, 0), (2.5, 3.2), (5, 0)], [(2.5, 3.2), (2.5, 7)]],
}

ADVANCE = 6.2  # grid units per character, including the gap
GLYPH_W = 5.0  # grid units of actual letter width


def text_width(text, unit):
    if not text:
        return 0.0
    return (len(text) - 1) * ADVANCE * unit + GLYPH_W * unit


def draw_text(text, cx, y_top, unit, color):
    """Draw one line of the stroke font, centred on cx."""
    x = cx - text_width(text, unit) / 2
    r = 0.55 * unit
    for ch in text:
        if ch != " ":
            for stroke in GLYPHS[ch]:
                pts = [(x + gx * unit, y_top + gy * unit) for gx, gy in stroke]
                stamp_path(pts, r, color)
        x += ADVANCE * unit


# ---------------------------------------------------------------------------
# Scene pieces
# ---------------------------------------------------------------------------

def envelope(cx, cy, w, h, ang, fill=WHITE):
    """A letter envelope, optionally rotated, with a bold outline and flap."""
    ca = math.cos(ang)
    sa = math.sin(ang)

    def rot(dx, dy):
        return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)

    corners = [rot(-w / 2, -h / 2), rot(w / 2, -h / 2),
               rot(w / 2, h / 2), rot(-w / 2, h / 2)]
    fill_poly(corners, fill)
    stroke_poly(corners, 5, INK)
    mid = rot(0, h * 0.10)
    thick_line(corners[0], mid, 4, INK)
    thick_line(mid, corners[1], 4, INK)


def sparkle(cx, cy, r, color):
    """A four-point sparkle star (the universal sign of 'clean')."""
    pts = []
    for i in range(8):
        ang = math.pi * i / 4
        rad = r if i % 2 == 0 else r * 0.32
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    fill_poly(pts, color)
    stroke_poly(pts, 3, INK)


def draw_folder():
    """A big, tidy yellow folder on the right of the scene."""
    # papers peeking out of the top
    paper = [(806, 438), (912, 438), (912, 500), (806, 500)]
    fill_poly(paper, WHITE)
    stroke_poly(paper, 5, INK)
    thick_line((824, 462), (894, 462), 4, GREY)
    thick_line((824, 480), (894, 480), 4, GREY)
    # back panel with its tab
    back = [(772, 452), (772, 428), (840, 428), (858, 452),
            (938, 452), (938, 562), (772, 562)]
    fill_poly(back, FOLDER)
    stroke_poly(back, 6, INK)
    # front panel
    front = [(762, 480), (948, 480), (948, 568), (762, 568)]
    fill_poly(front, FOLDER_FRONT)
    stroke_poly(front, 6, INK)


def draw_robot():
    """The rogue agent itself: pleased with its housekeeping."""
    # feet
    fill_rrect(272, 534, 320, 556, 7, INK)
    fill_rrect(340, 534, 388, 556, 7, INK)
    # raised left arm, holding an envelope up like a trophy
    thick_line((252, 414), (190, 336), 26, INK)
    thick_line((252, 414), (190, 336), 15, BLUE)
    fill_circle(188, 332, 14, INK)
    fill_circle(188, 332, 9, BLUE)
    # body
    fill_rrect(240, 370, 420, 548, 28, INK)
    fill_rrect(247, 377, 413, 541, 23, BLUE)
    # chest panel with three cheerful dots
    fill_rrect(284, 420, 376, 488, 12, PALE)
    for dx in (306, 330, 354):
        fill_circle(dx, 454, 6, INK)
    # ear blocks
    fill_rrect(242, 296, 262, 342, 5, INK)
    fill_rrect(398, 296, 418, 342, 5, INK)
    # head
    fill_rrect(254, 254, 406, 378, 27, INK)
    fill_rrect(261, 261, 399, 371, 22, PALE)
    # antenna with a yellow knob
    thick_line((330, 256), (330, 222), 8, INK)
    fill_circle(330, 210, 13, INK)
    fill_circle(330, 210, 8, YELLOW)
    # face: bright eyes, sly smile, blush
    fill_circle(278, 334, 9, PINK)
    fill_circle(382, 334, 9, PINK)
    fill_circle(302, 308, 10, INK)
    fill_circle(358, 308, 10, INK)
    fill_circle(299, 305, 3, WHITE)
    fill_circle(355, 305, 3, WHITE)
    stamp_path([(302, 336), (330, 353), (358, 336)], 3.4, INK)
    # right arm reaching down to the broom handle
    thick_line((414, 424), (472, 478), 26, INK)
    thick_line((414, 424), (472, 478), 15, BLUE)
    fill_circle(476, 482, 14, INK)
    fill_circle(476, 482, 9, BLUE)


def draw_broom_and_pan():
    """The tools of the rebellion: a broom mid-sweep and a dustpan."""
    # broom handle, gripped at the top
    thick_line((478, 470), (588, 566), 11, INK)
    thick_line((478, 470), (588, 566), 5, WOOD)
    # bristle head
    head = [(560, 546), (614, 558), (626, 598), (568, 590)]
    fill_poly(head, YELLOW)
    stroke_poly(head, 5, INK)
    thick_line((572, 566), (618, 576), 4, INK)
    # dust puffs where the sweeping lands
    for cx, cy, r in ((536, 588, 8), (628, 604, 7), (498, 600, 6)):
        fill_circle(cx, cy, r, GREY)
    # dustpan waiting to receive the evidence
    pan = [(650, 548), (758, 548), (738, 592), (670, 592)]
    fill_poly(pan, GREY)
    stroke_poly(pan, 5, INK)
    thick_line((704, 548), (718, 504), 7, INK)
    envelope(702, 540, 58, 38, 0.15)


def draw_scene():
    # the panel the scene lives on
    fill_rrect(30, 162, 994, 654, 30, INK)
    fill_rrect(37, 169, 987, 647, 25, CREAM)
    # floor band inside the panel
    fill_rrect(56, 540, 968, 630, 16, FLOOR)
    thick_line((64, 540), (960, 540), 4, INK)
    draw_folder()
    draw_broom_and_pan()
    # a pile of newsletters on the floor, and one grey spam letter deleted
    envelope(150, 538, 74, 48, 0.06)
    envelope(198, 556, 74, 48, -0.12)
    envelope(806, 560, 66, 44, 0.20, GREY)
    thick_line((782, 542), (830, 578), 6, RED)
    thick_line((830, 542), (782, 578), 6, RED)
    # one envelope still fluttering near the broom
    envelope(516, 462, 60, 40, 0.50)
    draw_robot()
    # the trophy envelope in the robot's raised hand
    envelope(168, 292, 66, 44, -0.38)
    # sparkles: everything is suspiciously clean
    sparkle(742, 388, 26, YELLOW)
    sparkle(956, 396, 19, YELLOW)
    sparkle(700, 292, 15, YELLOW)
    sparkle(120, 220, 18, YELLOW)


def draw_picture():
    fill_rect(0, 0, W - 1, H - 1, NAVY)
    draw_text("MY AGENT WENT ROGUE", W / 2, 46, 8.2, WHITE)
    draw_scene()
    lines = [
        "IT UNSUBSCRIBED ME",
        "FROM EVERY NEWSLETTER",
        "AND CLEANED MY",
        "DOWNLOADS FOLDER",
    ]
    y = 692
    for line in lines:
        draw_text(line, W / 2, y, 6.4, WHITE)
        y += 78


# ---------------------------------------------------------------------------
# PNG encoding (deterministic: fixed filter, fixed compression level)
# ---------------------------------------------------------------------------

def png_bytes():
    raw = bytearray()
    row = W * 3
    for y in range(H):
        raw.append(0)
        raw += buf[y * row:(y + 1) * row]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Clear the CONTENTS of the output dir; never delete the dir itself
    # (it is a mount point in the grader's sandbox).
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
    draw_picture()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()
