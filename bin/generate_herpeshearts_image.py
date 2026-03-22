#!/usr/bin/env python3
# CommandCenter Operation
# Name: Generate HerpesHearts Image
# Category: maintenance
#
# Generate the HerpesHearts project card image (400x300 WebP).
#
# Usage:
#   python3 bin/generate_herpeshearts_image.py
#
# Output:
#   ../GAME/static/project_images/HerpesHearts.webp — used on the GAME portfolio card
#
# image_description: A Red Cartoon Heart with a sparkle and cartoon flowers everywhere
"""Generate the HerpesHearts card image (400x300 WebP)."""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 400, 300


def create_herpeshearts_image():
    """Red cartoon heart with sparkle and cartoon flowers."""
    img = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Warm pink gradient background
    for y in range(HEIGHT):
        t = y / HEIGHT
        draw.line([(0, y), (WIDTH, y)], fill=(255, int(158 - t * 60), int(181 - t * 80)))

    # Scattered cartoon flowers
    flower_data = [
        (40,  40), (350, 30), (20, 200), (370, 220),
        (80, 260), (320, 270), (160, 20), (240, 15),
        (30, 130), (380, 120), (150, 275), (260, 280),
    ]
    petal_colors = [
        (255, 215,   0), (255, 105, 180), (155,  89, 182),
        (255, 140,   0), (  0, 206, 209), (173, 255,  47),
    ]
    center_colors = [
        (255, 165,   0), (255,  20, 147), (108,  52, 131),
        (255,  69,   0), (  0, 139, 139), ( 50, 205,  50),
    ]
    random.seed(99)
    for i, (fx, fy) in enumerate(flower_data):
        pc = petal_colors[i % len(petal_colors)]
        cc = center_colors[i % len(center_colors)]
        size = random.randint(12, 22)
        for p in range(5):
            angle = p * 72 * math.pi / 180
            px = fx + math.cos(angle) * size
            py = fy + math.sin(angle) * size
            r = size * 0.6
            draw.ellipse([px - r, py - r, px + r, py + r], fill=(*pc, 220))
        r2 = size * 0.4
        draw.ellipse([fx - r2, fy - r2, fx + r2, fy + r2], fill=(*cc, 255))

    # Large red heart (parametric heart curve)
    cx, cy = WIDTH // 2, HEIGHT // 2 + 10
    scale = 5.5
    heart_pts = []
    for i in range(360):
        t = math.radians(i)
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        heart_pts.append((cx + x * scale, cy + y * scale))

    # Drop shadow
    draw.polygon([(x + 5, y + 5) for x, y in heart_pts], fill=(160, 10, 30, 100))
    # Heart fill
    draw.polygon(heart_pts, fill='#FF1C2E')
    # Highlight
    hl_pts = []
    for i in range(360):
        t = math.radians(i)
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        hl_pts.append((cx - 18 + x * 2.2, cy - 22 + y * 2.2))
    draw.polygon(hl_pts, fill=(255, 160, 170, 110))
    # Outline
    draw.polygon(heart_pts, outline='#CC0022', width=3)

    # 4-pointed sparkle (upper-left of heart)
    def draw_sparkle(sx, sy, size, inner, color, alpha=255):
        pts = []
        for i in range(8):
            angle = math.radians(i * 45 - 90)
            r = size if i % 2 == 0 else inner
            pts.append((sx + math.cos(angle) * r, sy + math.sin(angle) * r))
        draw.polygon(pts, fill=(*color, alpha))

    draw_sparkle(cx - 28, cy - 38, 18, 6, (255, 255, 255))
    draw.ellipse([cx - 32, cy - 42, cx - 24, cy - 34], fill=(255, 250, 200))
    draw_sparkle(cx + 32, cy - 42, 9, 3, (255, 255, 200), 210)
    draw_sparkle(cx + 52, cy - 18, 7, 2, (255, 255, 200), 190)
    draw_sparkle(cx - 44, cy + 18, 7, 2, (255, 255, 200), 190)

    return img


def main():
    img = create_herpeshearts_image()

    dest = Path('/mnt/c/Users/barlo/projects/GAME/static/project_images/HerpesHearts.webp')
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, 'WEBP', quality=90)
    print(f"Saved {dest}  ({dest.stat().st_size / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
