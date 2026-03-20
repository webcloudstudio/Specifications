#!/bin/bash
# CommandCenter Operation
# Name: Build Doc
# Category: Operations
set -euo pipefail
SCRIPT_NAME="$(basename "$0" .sh)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Minimal preamble — Specifications has no common.sh
PROJECT_NAME="$(grep '^name:' METADATA.md | head -1 | sed 's/^name:[[:space:]]*//')"

LOG_FILE="logs/${PROJECT_NAME}_${SCRIPT_NAME}_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs doc/styles/themes
exec > >(tee -a "$LOG_FILE") 2>&1

# Parse --theme=<name> argument (default: slate)
THEME="slate"
for arg in "$@"; do
  case "$arg" in
    --theme=*) THEME="${arg#--theme=}" ;;
  esac
done

STYLES_DIR="$PROJECT_DIR/doc/styles"
THEME_FILE="$STYLES_DIR/themes/${THEME}.css"

if [ ! -f "$THEME_FILE" ]; then
  echo "ERROR: Theme not found: $THEME_FILE" >&2
  echo "Available themes: $(ls "$STYLES_DIR/themes/" | sed 's/\.css//' | tr '\n' ' ')"
  exit 1
fi

echo "[$PROJECT_NAME] Starting: $SCRIPT_NAME (theme: $THEME)"

# Build gem.css = theme variables + base structural rules
cat "$THEME_FILE" "$STYLES_DIR/gem-base.css" > "$STYLES_DIR/gem.css"
echo "  CSS: themes/${THEME}.css + gem-base.css → styles/gem.css"

python3 "$SCRIPT_DIR/build_documentation.py"
echo "[$PROJECT_NAME] Done: $SCRIPT_NAME"
echo "Output: doc/index.html"
