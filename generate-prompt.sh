#!/bin/bash
# Generate a complete build prompt from a project's METADATA.md, stack files, and spec files.
#
# Reads METADATA.md for stack components, collects technology files from stack/,
# collects all .md spec files from the project directory, and concatenates them
# into a single prompt suitable for an AI agent.
#
# Also prepends CLAUDE_RULES.md as the integration standard.
#
# Usage:
#   bash generate-prompt.sh <project-name>                    # Print to stdout
#   bash generate-prompt.sh <project-name> > build-prompt.md  # Save to file
#
# Example:
#   bash generate-prompt.sh GAME > build-prompt.md

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="${1:?Usage: bash generate-prompt.sh <project-name>}"
PROJECT_DIR="$REPO_DIR/$PROJECT_NAME"
METADATA_FILE="$PROJECT_DIR/METADATA.md"

if [ ! -f "$METADATA_FILE" ]; then
    echo "ERROR: METADATA.md not found at $METADATA_FILE" >&2
    exit 1
fi

# --- Parse METADATA.md (line-based key: value) ---
get_metadata() {
    grep "^${1}:" "$METADATA_FILE" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r'
}

STACK=$(get_metadata "stack")
PORT=$(get_metadata "port")
DISPLAY_NAME=$(get_metadata "display_name")
DESCRIPTION=$(get_metadata "short_description")

if [ -z "$STACK" ]; then
    echo "ERROR: No 'stack:' field in METADATA.md" >&2
    exit 1
fi

# Parse stack components (slash-separated, case-insensitive file match)
IFS='/' read -ra COMPONENTS <<< "$STACK"

# --- Header ---
cat <<HEADER
# Build Prompt: $PROJECT_NAME

You are building a project called **${DISPLAY_NAME:-$PROJECT_NAME}** — ${DESCRIPTION:-"(no description)"}.

## Stack
$(for comp in "${COMPONENTS[@]}"; do echo "- $comp"; done)
- Port: $PORT

## Instructions
1. Read the CLAUDE_RULES section below — it defines project integration standards
2. Read ALL technology reference files — they define HOW to implement
3. Read ALL specification files — they define WHAT to implement
4. Follow the technology patterns exactly (they are prescriptive standards)
5. Build in the order implied by the specification files

---

HEADER

# --- CLAUDE_RULES.md ---
if [ -f "$REPO_DIR/CLAUDE_RULES.md" ]; then
    echo "# PROJECT INTEGRATION STANDARD"
    echo ""
    echo "---"
    echo ""
    echo "## CLAUDE_RULES.md"
    echo ""
    cat "$REPO_DIR/CLAUDE_RULES.md"
    echo ""
    echo ""
fi

# --- Technology Files ---
echo "# TECHNOLOGY REFERENCES"
echo ""

emit_file() {
    local filepath="$1"
    local label="$2"
    if [ -f "$filepath" ]; then
        echo "---"
        echo ""
        echo "## $label"
        echo ""
        cat "$filepath"
        echo ""
        echo ""
    fi
}

# Always include common.md first
emit_file "$REPO_DIR/stack/common.md" "Common Practices (stack/common.md)"

# Emit each stack component's reference file
for comp in "${COMPONENTS[@]}"; do
    comp_clean="$(echo "$comp" | tr -d ' ')"
    comp_lower="$(echo "$comp_clean" | tr '[:upper:]' '[:lower:]')"
    stack_file="$REPO_DIR/stack/${comp_lower}.md"
    if [ -f "$stack_file" ]; then
        emit_file "$stack_file" "$comp (stack/${comp_lower}.md)"
    else
        echo "<!-- WARNING: No stack file for '$comp' (expected stack/${comp_lower}.md) -->"
        echo ""
    fi
done

# --- METADATA.md ---
echo "---"
echo ""
echo "## Project Configuration (METADATA.md)"
echo ""
echo '```'
cat "$METADATA_FILE"
echo '```'
echo ""

# --- Specification Files ---
echo ""
echo "# PROJECT SPECIFICATION"
echo ""

# Emit all .md files in the project directory (sorted, excluding METADATA.md)
for spec_file in $(find "$PROJECT_DIR" -maxdepth 1 -name '*.md' ! -name 'METADATA.md' | sort); do
    fname="$(basename "$spec_file")"
    emit_file "$spec_file" "Spec: $fname"
done

# --- Footer ---
cat <<FOOTER
---

# END OF BUILD PROMPT

Build this project following the integration standard, technology references, and specification files above.
All patterns in the technology references are prescriptive — use them exactly as shown.
FOOTER
