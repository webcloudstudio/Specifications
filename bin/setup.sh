#!/bin/bash
# CommandCenter Operation
# Name: Setup Spec
# Category: maintenance

# Scaffolds a new specification directory from templates, or updates an existing one.
# Works on any directory — not limited to Specifications subdirectories.
#
# Usage:
#   bash bin/setup.sh <project-name>              # create in Specifications/<name>/
#   bash bin/setup.sh /abs/path/to/project        # create or update absolute path
#   bash bin/setup.sh ./relative/path             # create or update relative path
#   bash bin/setup.sh <project-name> --update     # copy new template files into existing dir
#   bash bin/setup.sh <project-name> --force      # overwrite existing files
#
# Arguments:
#   $1        Project name or directory path (required)
#   --update  If directory exists, copy template files that are not yet present (no overwrite)
#   --force   If directory exists, overwrite all template files
#
# Creates:
#   <project-dir>/
#     METADATA.md, README.md, INTENT.md, ARCHITECTURE.md,
#     DATABASE.md, UI.md, SCREEN-Example.md, FEATURE-Example.md
#
# Template source: RulesEngine/spec_template/

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$REPO_DIR/RulesEngine/spec_template"

ARG="${1:?Usage: bash bin/setup.sh <project-name-or-path> [--update|--force]}"
UPDATE=false
FORCE=false
for a in "$@"; do
    case "$a" in
        --update) UPDATE=true ;;
        --force)  FORCE=true ;;
    esac
done

# Resolve project directory
if [[ "$ARG" == /* ]]; then
    PROJECT_DIR="$ARG"
elif [[ "$ARG" == ./* || "$ARG" == ../* ]]; then
    PROJECT_DIR="$(cd "$ARG" 2>/dev/null && pwd || echo "$(pwd)/${ARG#./}")"
elif [ -d "$ARG" ]; then
    PROJECT_DIR="$(cd "$ARG" && pwd)"
else
    PROJECT_DIR="$REPO_DIR/$ARG"
fi

PROJECT_SLUG="$(basename "$PROJECT_DIR")"

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "ERROR: Template directory not found: $TEMPLATE_DIR" >&2
    exit 1
fi

TODAY=$(date '+%Y-%m-%d')
TODAY_COMPACT=$(date '+%Y%m%d')

# Derive display name from project slug (hyphen/underscore to spaces, title case, trim)
DISPLAY_NAME=$(echo "$PROJECT_SLUG" | sed 's/[-_]/ /g' | sed 's/\b\(.\)/\u\1/g' | sed 's/^ *//;s/ *$//' | sed 's/  */ /g')

if [ -d "$PROJECT_DIR" ]; then
    if [ "$UPDATE" = false ] && [ "$FORCE" = false ]; then
        echo "ERROR: Directory already exists: $PROJECT_DIR" >&2
        echo "  Use --update to add missing template files, or --force to overwrite all." >&2
        exit 1
    fi
    if [ "$FORCE" = true ]; then
        echo "Updating (force): $PROJECT_DIR/"
    else
        echo "Updating (new files only): $PROJECT_DIR/"
    fi
else
    mkdir -p "$PROJECT_DIR"
    echo "Created: $PROJECT_DIR/"
fi

COPIED=0
SKIPPED=0
for tmpl_file in "$TEMPLATE_DIR"/*.md; do
    fname=$(basename "$tmpl_file")
    dest="$PROJECT_DIR/$fname"
    if [ -f "$dest" ] && [ "$FORCE" = false ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi
    sed \
        -e "s|__PROJECT_NAME__|$DISPLAY_NAME|g" \
        -e "s|__PROJECT_SLUG__|$PROJECT_SLUG|g" \
        -e "s|__SHORT_DESCRIPTION__|TODO: add short description|g" \
        -e "s|__TODAY__|$TODAY|g" \
        -e "s|__TODAY_COMPACT__|$TODAY_COMPACT|g" \
        "$tmpl_file" > "$dest"
    COPIED=$((COPIED + 1))
done

echo "Files:"
ls -1 "$PROJECT_DIR/"
if [ "$SKIPPED" -gt 0 ]; then
    echo ""
    echo "  ($SKIPPED existing files skipped — use --force to overwrite)"
fi
echo ""
echo "Next steps:"
echo "  1. Edit INTENT.md — why does this project exist?"
echo "  2. Edit METADATA.md — add stack, port, status fields as needed"
echo "  3. Rename SCREEN-Example.md and FEATURE-Example.md to real names"
echo "  4. Delete DATABASE.md or UI.md if not applicable"
echo "  5. Run: bash bin/validate.sh $PROJECT_SLUG"
