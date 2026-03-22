#!/usr/bin/env python3
# CommandCenter Operation
# Name: Generate EdBarlowsStoredProcs Image
# Category: maintenance
#
# Generate the EdBarlowsStoredProcs project card image (400x300 WebP).
#
# Usage:
#   python3 bin/generate_edbarlowsstoredprocs_image.py
#
# Output:
#   ../GAME/static/project_images/EdBarlowsStoredProcs.webp — portfolio card
#
# image_description: A Sybase Server Logo next to a Sql Server Logo
"""Generate the EdBarlowsStoredProcs card image (400x300 WebP)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'GAME' / 'bin'))
from generate_card_images import create_edbarlowsstoredprocs_image


def main():
    img = create_edbarlowsstoredprocs_image()
    dest = Path('/mnt/c/Users/barlo/projects/GAME/static/project_images/EdBarlowsStoredProcs.webp')
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, 'WEBP', quality=90)
    print(f"Saved {dest}  ({dest.stat().st_size / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
