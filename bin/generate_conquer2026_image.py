#!/usr/bin/env python3
#
# Generate the conquer_2026 project card image (400x300 WebP).
#
# Usage:
#   python3 bin/generate_conquer2026_image.py
#
# Output:
#   ../GAME/static/project_images/conquer_2026.webp — portfolio card
#
# image_description: A Cartoon Table with a map on it with a human knight, orc
#   spearman, and a dwarf axe bearer looking at it and a dagger stuck into it -
#   old school d&d style
"""Generate the conquer_2026 card image (400x300 WebP)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'GAME' / 'bin'))
from generate_card_images import create_conquer2026_image


def main():
    img = create_conquer2026_image()
    dest = Path('/mnt/c/Users/barlo/projects/GAME/static/project_images/conquer_2026.webp')
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, 'WEBP', quality=90)
    print(f"Saved {dest}  ({dest.stat().st_size / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
