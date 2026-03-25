#!/bin/bash
# CommandCenter Operation
# Name: Convert Specs
# Category: maintenance
# Args: Spec

# Generates a conversion prompt: concise project specs + ONESHOT_BUILD_RULES.md expansion rules + stack files.
# Feed the output to an AI agent to get detailed, implementation-ready specifications.
#
# Usage:
#   bash bin/convert.sh <project-name>                     # Print to stdout
#   bash bin/convert.sh <project-name> > convert-prompt.md # Save to file
#
# Example:
#   bash bin/convert.sh Game-Build > convert-prompt.md

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -z "${1:-}" ] || [[ "${1:-}" == --* ]]; then
    echo "Usage: bash bin/convert.sh <spec-name> [> convert-prompt.md]" >&2
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="$REPO_DIR/$1"
shift

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Spec directory not found: $PROJECT_DIR" >&2
    exit 1
fi

METADATA_FILE="$PROJECT_DIR/METADATA.md"
CONVERT_FILE="$REPO_DIR/RulesEngine/ONESHOT_BUILD_RULES.md"

if [ ! -f "$METADATA_FILE" ]; then
    echo "ERROR: METADATA.md not found at $METADATA_FILE" >&2
    exit 1
fi

if [ ! -f "$CONVERT_FILE" ]; then
    echo "ERROR: ONESHOT_BUILD_RULES.md not found at $CONVERT_FILE" >&2
    exit 1
fi

# --- Parse METADATA.md ---
get_metadata() {
    grep "^${1}:" "$METADATA_FILE" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r'
}

STACK=$(get_metadata "stack")
DISPLAY_NAME=$(get_metadata "display_name")

if [ -z "$STACK" ]; then
    echo "ERROR: No 'stack:' field in METADATA.md" >&2
    exit 1
fi

IFS='/' read -ra COMPONENTS <<< "$STACK"

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

# --- Header ---
cat <<HEADER
# Conversion Prompt: $PROJECT_NAME

You are expanding concise specifications for **${DISPLAY_NAME:-$PROJECT_NAME}** into detailed, implementation-ready specifications.

## Instructions

1. Read the CONVERSION RULES below — they define how to expand each file type
2. Read the STACK REFERENCES — they define technology conventions to apply during expansion
3. Read each CONCISE SPEC file — these are the author's input
4. For each spec file, output an expanded version following the conversion rules
5. Preserve all Open Questions sections unchanged
6. Do NOT expand [ROADMAP] items beyond their current detail level

---

HEADER

# --- Conversion Rules ---
echo "# CONVERSION RULES"
echo ""
emit_file "$CONVERT_FILE" "ONESHOT_BUILD_RULES.md (RulesEngine/ONESHOT_BUILD_RULES.md)"

# --- Stack References ---
echo "# STACK REFERENCES"
echo ""
emit_file "$REPO_DIR/RulesEngine/stack/common.md" "Common Practices"

for comp in "${COMPONENTS[@]}"; do
    comp_clean="$(echo "$comp" | tr -d ' ')"
    comp_lower="$(echo "$comp_clean" | tr '[:upper:]' '[:lower:]')"
    stack_file="$REPO_DIR/RulesEngine/stack/${comp_lower}.md"
    if [ -f "$stack_file" ]; then
        emit_file "$stack_file" "$comp (stack/${comp_lower}.md)"
    fi
done

# --- Project METADATA ---
echo "---"
echo ""
echo "## Project Configuration (METADATA.md)"
echo ""
echo '```'
cat "$METADATA_FILE"
echo '```'
echo ""

# --- Concise Spec Files ---
echo ""
echo "# CONCISE SPECIFICATIONS (expand these)"
echo ""

for spec_file in $(find "$PROJECT_DIR" -maxdepth 1 -name '*.md' ! -name 'METADATA.md' | sort); do
    fname="$(basename "$spec_file")"
    emit_file "$spec_file" "Spec: $fname"
done

# --- Footer ---
cat <<FOOTER
---

# END OF CONVERSION PROMPT

Expand each specification file according to the conversion rules and stack conventions.
Output the expanded version of each file, clearly labeled.
Preserve Open Questions. Do not expand [ROADMAP] sections.
FOOTER
