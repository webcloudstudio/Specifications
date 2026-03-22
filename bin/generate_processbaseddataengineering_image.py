#!/usr/bin/env python3
# CommandCenter Operation
# Name: Generate ProcessBasedDataEngineering Image
# Category: maintenance
#
# Generate the ProcessBasedDataEngineering project card image (400x300 WebP).
#
# Usage:
#   python3 bin/generate_processbaseddataengineering_image.py
#
# Output:
#   ../GAME/static/project_images/ProcessBasedDataEngineering.webp — portfolio card
#
# image_description: A Brown cartoon book winking at the user - wears a yellow hat
#   and waving a paintbrush next to an easel on a cloud playing a flute.
"""Generate the ProcessBasedDataEngineering card image (400x300 WebP)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'GAME' / 'bin'))
from generate_card_images import create_processbaseddataengineering_image


def main():
    img = create_processbaseddataengineering_image()
    dest = Path('/mnt/c/Users/barlo/projects/GAME/static/project_images/ProcessBasedDataEngineering.webp')
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, 'WEBP', quality=90)
    print(f"Saved {dest}  ({dest.stat().st_size / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
