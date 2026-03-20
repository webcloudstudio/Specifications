#!/usr/bin/env python3
"""Generate the Prototyper mad-scientist card image (400x300 WebP).

Saves to:
  doc/images/prototyper.webp  (Specifications repo)
  ../GAME/static/images/Specifications.webp
"""

import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 400, 300
GREEN = (44, 182, 125)       # #2cb67d
GREEN_DIM = (20, 90, 60)
WHITE = (255, 255, 255)
CREAM = (240, 235, 220)
SKIN = (230, 195, 160)
DARK_SKIN = (200, 165, 130)
BRAIN_BASE = (210, 150, 160)
BRAIN_RIDGE = (170, 110, 120)
COAT_WHITE = (220, 225, 230)
COAT_SHADOW = (180, 185, 195)
GOGGLE_LENS = (100, 200, 150)
GOGGLE_FRAME = (80, 80, 80)
LIGHTNING = (255, 255, 160)


def draw_gradient(draw):
    top = (22, 32, 46)    # #16202e
    bot = (10, 16, 24)    # #0a1018
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_glow(img, cx, cy, radius, color, alpha=60):
    """Paste a soft radial glow blob onto img."""
    glow = Image.new('RGBA', (radius * 2, radius * 2), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(radius, 0, -1):
        a = int(alpha * (1 - r / radius) ** 1.5)
        gd.ellipse([radius - r, radius - r, radius + r, radius + r],
                   fill=(color[0], color[1], color[2], a))
    img.paste(glow, (cx - radius, cy - radius), glow)


def draw_brain(draw, cx, top_y):
    """Draw an oversized brain: single smooth ellipse + fissure + horizontal sulci."""
    bw, bh = 180, 120

    # Outer shape — one smooth ellipse, no bumps
    draw.ellipse([cx - bw // 2, top_y, cx + bw // 2, top_y + bh],
                 fill=BRAIN_BASE, outline=BRAIN_RIDGE, width=3)

    # Highlight on upper-left to give roundness
    draw.ellipse([cx - bw // 2 + 12, top_y + 8, cx - 10, top_y + 40],
                 fill=(225, 170, 175))

    # Central interhemispheric fissure (vertical)
    draw.line([(cx, top_y + 6), (cx, top_y + bh - 6)],
              fill=BRAIN_RIDGE, width=3)

    # Horizontal sulci — left hemisphere (drawn as concave arcs, open upward)
    for i in range(6):
        y = top_y + 18 + i * 17
        shrink = i * 3
        x1 = cx - bw // 2 + 10 + shrink
        x2 = cx - 10
        draw.arc([x1, y - 6, x2, y + 6], start=0, end=180,
                 fill=BRAIN_RIDGE, width=2)

    # Horizontal sulci — right hemisphere
    for i in range(6):
        y = top_y + 18 + i * 17
        shrink = i * 3
        x1 = cx + 10
        x2 = cx + bw // 2 - 10 - shrink
        draw.arc([x1, y - 6, x2, y + 6], start=0, end=180,
                 fill=BRAIN_RIDGE, width=2)

    return top_y + bh  # bottom of brain


def draw_sparks(img, cx, brain_top, brain_bot):
    """Draw green glowing spark particles around the brain."""
    import random
    random.seed(42)
    spark_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spark_layer)

    brain_cx = cx
    brain_cy = (brain_top + brain_bot) // 2
    rx, ry = 110, 80  # ellipse radii for spark orbit

    for i in range(30):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.8, 1.3)
        sx = int(brain_cx + math.cos(angle) * rx * dist)
        sy = int(brain_cy + math.sin(angle) * ry * dist)
        size = random.randint(2, 6)
        alpha = random.randint(120, 220)
        sd.ellipse([sx - size, sy - size, sx + size, sy + size],
                   fill=(GREEN[0], GREEN[1], GREEN[2], alpha))

    # Short spark lines
    for i in range(18):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.75, 1.15)
        sx = int(brain_cx + math.cos(angle) * rx * dist)
        sy = int(brain_cy + math.sin(angle) * ry * dist)
        ex = sx + random.randint(-10, 10)
        ey = sy + random.randint(-8, 8)
        alpha = random.randint(140, 255)
        sd.line([(sx, sy), (ex, ey)],
                fill=(GREEN[0], GREEN[1], GREEN[2], alpha), width=2)

    img.paste(spark_layer, (0, 0), spark_layer)


def draw_hair(draw, cx, head_top, head_r):
    """Wild spiky hair radiating from the sides of the head."""
    hair_color = (210, 180, 50)
    dark_hair = (160, 130, 20)
    # Spikes radiate from the left and right sides
    spike_params = [
        # (angle_deg, length, base_width)
        (150, 55, 12),
        (165, 65, 14),
        (180, 50, 10),
        (195, 62, 13),
        (210, 48, 11),
        (225, 42, 9),
        (30,  55, 12),
        (15,  65, 14),
        (0,   50, 10),
        (345, 62, 13),
        (330, 48, 11),
        (315, 42, 9),
    ]
    head_cy = head_top + head_r
    for angle_deg, length, bw in spike_params:
        rad = math.radians(angle_deg)
        # Spike tip
        tip_x = cx + math.cos(rad) * (head_r + length)
        tip_y = head_cy + math.sin(rad) * (head_r + length)
        # Base corners (perpendicular to spike direction)
        perp = math.radians(angle_deg + 90)
        base_x = cx + math.cos(rad) * (head_r - 5)
        base_y = head_cy + math.sin(rad) * (head_r - 5)
        b1x = base_x + math.cos(perp) * bw
        b1y = base_y + math.sin(perp) * bw
        b2x = base_x - math.cos(perp) * bw
        b2y = base_y - math.sin(perp) * bw
        draw.polygon([(tip_x, tip_y), (b1x, b1y), (b2x, b2y)],
                     fill=hair_color, outline=dark_hair)


def draw_face(draw, cx, face_cy, face_r):
    """Tiny face: skin circle, goggles, tiny mouth."""
    # Head
    draw.ellipse([cx - face_r, face_cy - face_r, cx + face_r, face_cy + face_r],
                 fill=SKIN, outline=DARK_SKIN, width=2)

    # Goggles — two small circles
    g_y = face_cy - 3
    g_r = 10
    gap = 14
    for gx in [cx - gap, cx + gap]:
        # Lens glow
        draw.ellipse([gx - g_r - 2, g_y - g_r - 2, gx + g_r + 2, g_y + g_r + 2],
                     fill=(GOGGLE_LENS[0], GOGGLE_LENS[1], GOGGLE_LENS[2]))
        # Rim
        draw.ellipse([gx - g_r, g_y - g_r, gx + g_r, g_y + g_r],
                     outline=GOGGLE_FRAME, width=3, fill=None)
        # Highlight
        draw.ellipse([gx - 4, g_y - 5, gx - 1, g_y - 2], fill=WHITE)
    # Bridge
    draw.line([(cx - gap + g_r, g_y), (cx + gap - g_r, g_y)],
              fill=GOGGLE_FRAME, width=2)

    # Tiny mouth (open, excited)
    draw.arc([cx - 8, face_cy + 4, cx + 8, face_cy + 14],
             start=0, end=180, fill=(140, 80, 80), width=2)


def draw_coat(draw, cx, neck_y):
    """Small white lab coat body below the face."""
    body_w = 70
    body_h = 80
    body_top = neck_y
    body_bot = neck_y + body_h

    # Coat body (trapezoid, wider at bottom)
    coat_pts = [
        (cx - body_w // 2 + 5, body_top),
        (cx + body_w // 2 - 5, body_top),
        (cx + body_w // 2 + 10, body_bot),
        (cx - body_w // 2 - 10, body_bot),
    ]
    draw.polygon(coat_pts, fill=COAT_WHITE, outline=COAT_SHADOW, width=2)

    # Lapel lines
    draw.line([(cx - 5, body_top + 5), (cx - 12, body_top + 30)],
              fill=COAT_SHADOW, width=2)
    draw.line([(cx + 5, body_top + 5), (cx + 12, body_top + 30)],
              fill=COAT_SHADOW, width=2)

    # Pocket
    draw.rectangle([cx + 15, body_top + 35, cx + 32, body_top + 55],
                   outline=COAT_SHADOW, width=1)

    # Arms
    # Left arm
    draw.polygon([
        (cx - body_w // 2 + 5, body_top + 5),
        (cx - body_w // 2 - 10, body_top + 50),
        (cx - body_w // 2 - 28, body_top + 45),
        (cx - body_w // 2 - 15, body_top),
    ], fill=COAT_WHITE, outline=COAT_SHADOW, width=2)

    # Right arm (holding beaker)
    draw.polygon([
        (cx + body_w // 2 - 5, body_top + 5),
        (cx + body_w // 2 + 10, body_top + 50),
        (cx + body_w // 2 + 28, body_top + 45),
        (cx + body_w // 2 + 15, body_top),
    ], fill=COAT_WHITE, outline=COAT_SHADOW, width=2)

    return body_bot


def draw_beaker(draw, bx, by):
    """Small beaker with green glowing liquid."""
    # Glass body
    beaker_pts = [
        (bx - 10, by - 30),
        (bx + 10, by - 30),
        (bx + 14, by),
        (bx - 14, by),
    ]
    draw.polygon(beaker_pts, fill=(180, 220, 200, 180), outline=(140, 180, 160), width=2)

    # Liquid (green, fills bottom ~60%)
    liquid_pts = [
        (bx - 9, by - 14),
        (bx + 9, by - 14),
        (bx + 13, by - 1),
        (bx - 13, by - 1),
    ]
    draw.polygon(liquid_pts, fill=(GREEN[0], GREEN[1], GREEN[2], 200))

    # Neck
    draw.rectangle([bx - 6, by - 42, bx + 6, by - 30], fill=(180, 220, 200), outline=(140, 180, 160), width=1)

    # Bubble in liquid
    draw.ellipse([bx - 3, by - 20, bx + 3, by - 14], fill=(160, 255, 200, 180))


def draw_lightning(draw, cx, brain_top):
    """Small decorative lightning bolts near the brain."""
    bolts = [
        # left side
        [(cx - 115, brain_top + 30),
         (cx - 100, brain_top + 50),
         (cx - 108, brain_top + 50),
         (cx - 93,  brain_top + 70)],
        # right side
        [(cx + 115, brain_top + 30),
         (cx + 100, brain_top + 50),
         (cx + 108, brain_top + 50),
         (cx + 93,  brain_top + 70)],
    ]
    for bolt in bolts:
        draw.line(bolt, fill=LIGHTNING, width=3)


def create_prototyper_image():
    """Create a mad-scientist cartoon for the Specifications/Prototyper project."""
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Background gradient
    draw_gradient(draw)

    cx = WIDTH // 2     # 200
    brain_top = 10      # brain starts near top

    # Green glow behind brain
    draw_glow(img, cx, brain_top + 70, 130, GREEN, alpha=55)

    # Draw the brain (returns bottom y of brain)
    brain_bot = draw_brain(draw, cx, brain_top)

    # Sparks / aura
    draw_sparks(img, cx, brain_top, brain_bot)

    # Lightning bolts
    draw_lightning(draw, cx, brain_top)

    # Face sits just below brain
    face_r = 22
    face_cy = brain_bot + face_r + 4

    # Hair radiates from the sides of the face
    draw_hair(draw, cx, face_cy - face_r, face_r)

    # Face
    draw_face(draw, cx, face_cy, face_r)

    # Neck
    neck_y = face_cy + face_r + 2
    draw.rectangle([cx - 8, neck_y, cx + 8, neck_y + 10],
                   fill=SKIN, outline=DARK_SKIN, width=1)

    # Lab coat
    coat_bot = draw_coat(draw, cx, neck_y + 10)

    # Beaker in right hand
    beaker_x = cx + 62
    beaker_y = neck_y + 60
    draw_beaker(draw, beaker_x, beaker_y)

    # Convert to RGB for WebP
    result = img.convert('RGB')
    return result


def main():
    img = create_prototyper_image()

    # Destination 1: Specifications/doc/images/
    dest1 = Path('/mnt/c/Users/barlo/projects/Specifications/doc/images/prototyper.webp')
    os.makedirs(dest1.parent, exist_ok=True)
    img.save(dest1, 'WEBP', quality=90)
    print(f"Saved {dest1}  ({dest1.stat().st_size / 1024:.1f} KB)")

    # Destination 2: GAME/static/images/
    dest2 = Path('/mnt/c/Users/barlo/projects/GAME/static/images/Specifications.webp')
    os.makedirs(dest2.parent, exist_ok=True)
    img.save(dest2, 'WEBP', quality=90)
    print(f"Saved {dest2}  ({dest2.stat().st_size / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
