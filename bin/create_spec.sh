#!/bin/bash
# CommandCenter Operation
# Name: Create Spec
# Category: maintenance

# Scaffolds a new specification directory from templates.
#
# Usage:
#   bash bin/create_spec.sh <project-name>
#
# Arguments:
#   $1  Project name (required) — becomes directory name and METADATA slug
#
# Creates:
#   <project-name>/
#     METADATA.md, README.md, INTENT.md, ARCHITECTURE.md,
#     DATABASE.md, UI.md, SCREEN-Example.md, FEATURE-Example.md
#
# Template source: GLOBAL_RULES/spec_template/

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME="${1:?Usage: bash bin/create_spec.sh <project-name>}"
SHORT_DESC="TODO: add short description"
PROJECT_DIR="$REPO_DIR/$PROJECT_NAME"
TEMPLATE_DIR="$REPO_DIR/GLOBAL_RULES/spec_template"

if [ -d "$PROJECT_DIR" ]; then
    echo "ERROR: Directory already exists: $PROJECT_DIR" >&2
    exit 1
fi

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "ERROR: Template directory not found: $TEMPLATE_DIR" >&2
    exit 1
fi

TODAY=$(date '+%Y-%m-%d')
TODAY_COMPACT=$(date '+%Y%m%d')

# Derive display name from project slug (hyphen/underscore to spaces, title case, trim)
DISPLAY_NAME=$(echo "$PROJECT_NAME" | sed 's/[-_]/ /g' | sed 's/\b\(.\)/\u\1/g' | sed 's/^ *//;s/ *$//' | sed 's/  */ /g')

mkdir -p "$PROJECT_DIR"

for tmpl_file in "$TEMPLATE_DIR"/*.md; do
    fname=$(basename "$tmpl_file")
    sed \
        -e "s|__PROJECT_NAME__|$DISPLAY_NAME|g" \
        -e "s|__PROJECT_SLUG__|$PROJECT_NAME|g" \
        -e "s|__SHORT_DESCRIPTION__|$SHORT_DESC|g" \
        -e "s|__TODAY__|$TODAY|g" \
        -e "s|__TODAY_COMPACT__|$TODAY_COMPACT|g" \
        "$tmpl_file" > "$PROJECT_DIR/$fname"
done

echo "Created: $PROJECT_DIR/"
echo "Files:"
ls -1 "$PROJECT_DIR/"
echo ""
echo "Next steps:"
echo "  1. Edit INTENT.md — why does this project exist?"
echo "  2. Edit METADATA.md — add stack, port, status fields as needed"
echo "  3. Rename SCREEN-Example.md and FEATURE-Example.md to real names"
echo "  4. Delete DATABASE.md or UI.md if not applicable"
echo "  5. Run: bash bin/validate.sh $PROJECT_NAME"
