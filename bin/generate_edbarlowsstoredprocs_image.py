#!/usr/bin/env python3
# CommandCenter Operation
# Name: Generate EdBarlowsStoredProcs Image
# Category: maintenance
#
# Generate the EdBarlowsStoredProcs project card image (400x300 WebP).
# Composites the real Sybase and SQL Server logos side by side on a dark background.
#
# Usage:
#   python3 bin/generate_edbarlowsstoredprocs_image.py
#
# Source images (from GAME/static/project_images/):
#   sybase_logo.png
#   microsoft-sql-server.jpg
#
# Output:
#   ../GAME/static/project_images/EdBarlowsStoredProcs.webp — portfolio card
"""Composite Sybase + SQL Server logos into a 400x300 WebP card image."""

from pathlib import Path
from PIL import Image, ImageOps

WIDTH, HEIGHT = 400, 300
DEST = Path('/mnt/c/Users/barlo/projects/GAME/static/project_images/EdBarlowsStoredProcs.webp')
PROJECT_IMAGES = Path('/mnt/c/Users/barlo/projects/GAME/static/project_images')

SYBASE_CANDIDATES = [PROJECT_IMAGES / 'sybase_logo.png']
SQL_SERVER = PROJECT_IMAGES / 'microsoft-sql-server.jpg'


def fit_image(img, max_w, max_h):
    """Resize image to fit within max_w x max_h, preserving aspect ratio."""
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return img


def main():
    # Locate Sybase logo
    sybase_path = next((p for p in SYBASE_CANDIDATES if p.exists()), None)
    if sybase_path is None:
        print(f"ERROR: Sybase logo not found. Tried:")
        for p in SYBASE_CANDIDATES:
            print(f"  {p}")
        return 1
    if not SQL_SERVER.exists():
        print(f"ERROR: SQL Server logo not found: {SQL_SERVER}")
        return 1

    print(f"Sybase source : {sybase_path}")
    print(f"SQL Server src: {SQL_SERVER}")

    # Dark background
    canvas = Image.new('RGB', (WIDTH, HEIGHT), (18, 22, 42))

    # Load and resize each logo to fit in roughly half the canvas with padding
    slot_w = WIDTH // 2 - 20   # 180px per logo slot
    slot_h = HEIGHT - 40        # 260px tall slot

    sybase = Image.open(sybase_path).convert('RGBA')
    sybase = fit_image(sybase, slot_w, slot_h)

    sql = Image.open(SQL_SERVER).convert('RGBA')
    sql = fit_image(sql, slot_w, slot_h)

    # Centre each logo vertically in its half
    def paste_centred(canvas, logo, x_centre, y_centre):
        x = x_centre - logo.width // 2
        y = y_centre - logo.height // 2
        if logo.mode == 'RGBA':
            canvas.paste(logo, (x, y), logo)
        else:
            canvas.paste(logo, (x, y))

    left_cx  = WIDTH // 4          # 100
    right_cx = WIDTH * 3 // 4     # 300
    mid_y    = HEIGHT // 2         # 150

    paste_centred(canvas, sybase, left_cx, mid_y)
    paste_centred(canvas, sql,   right_cx, mid_y)

    # Subtle vertical divider
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)
    draw.line([(WIDTH // 2, 20), (WIDTH // 2, HEIGHT - 20)], fill=(60, 70, 100), width=1)

    DEST.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(DEST, 'WEBP', quality=92)
    print(f"Saved {DEST}  ({DEST.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
