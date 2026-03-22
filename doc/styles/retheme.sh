#!/bin/bash
# Apply a documentation theme to this project.
# Usage: doc/styles/retheme.sh [theme-name]
# Default: slate
# Available: slate  midnight  green  purple  midnight-green  mughal  rainforest  ivory  clean
#
# Works for any project that has doc/styles/ — independent of the documentation
# build process.  Run any time to switch themes without rebuilding documentation.

THEME=${1:-slate}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
THEME_FILE="$SCRIPT_DIR/themes/$THEME.css"
BASE_FILE="$SCRIPT_DIR/spec-base.css"
OUT_FILE="$SCRIPT_DIR/spec.css"

if [ ! -f "$THEME_FILE" ]; then
  echo "Unknown theme '$THEME'. Available:"
  ls "$SCRIPT_DIR/themes/" | sed 's/\.css//' | sed 's/^/  /'
  exit 1
fi

cat "$THEME_FILE" "$BASE_FILE" > "$OUT_FILE"
echo "Theme applied: $THEME  →  doc/styles/spec.css"
