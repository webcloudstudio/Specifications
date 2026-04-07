#!/usr/bin/env python3
#
# Generate the GAME project card image (400x300 WebP).
#
# Usage:
#   python3 bin/generate_game_image.py
#
# Output:
#   ../GAME/static/project_images/GAME.webp — used on the GAME portfolio card
#
# image_description: An Orange Cartoon turtle in a blue beret sitting on a rock
#   on a cloud playing a flute.
"""Generate the GAME card image (400x300 WebP)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'GAME' / 'bin'))
from generate_card_images import create_game_image


def main():
    img = create_game_image()
    dest = Path('/mnt/c/Users/barlo/projects/GAME/static/project_images/GAME.webp')
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, 'WEBP', quality=90)
    print(f"Saved {dest}  ({dest.stat().st_size / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
