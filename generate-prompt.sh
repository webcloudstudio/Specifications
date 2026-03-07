#!/bin/bash
# Generate a complete build prompt from STACK.yaml and all referenced files.
#
# Reads STACK.yaml, collects all technology files and spec files,
# and concatenates them into a single prompt suitable for an AI agent.
#
# Usage:
#   bash PROJECT/generate-prompt.sh                  # Print to stdout
#   bash PROJECT/generate-prompt.sh > build-prompt.md  # Save to file

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_FILE="$PROJECT_DIR/STACK.yaml"

if [ ! -f "$STACK_FILE" ]; then
    echo "ERROR: STACK.yaml not found in $PROJECT_DIR" >&2
    exit 1
fi

# --- Parse STACK.yaml ---
get_yaml_value() {
    grep "^${1}:" "$STACK_FILE" | head -1 | sed 's/^[^:]*: *//' | tr -d '"' | tr -d "'" | tr -d '\r'
}

LANGUAGE=$(get_yaml_value "language")
FRAMEWORK=$(get_yaml_value "framework")
DATABASE=$(get_yaml_value "database")
FRONTEND=$(get_yaml_value "frontend")

PROJECT_NAME=$(grep '^\s*name:' "$STACK_FILE" | head -1 | sed 's/^[^:]*: *//' | tr -d '"' | tr -d "'" | tr -d '\r')
PROJECT_DESC=$(grep '^\s*description:' "$STACK_FILE" | head -1 | sed 's/^[^:]*: *//' | tr -d '"' | tr -d "'" | tr -d '\r')
PROJECT_PORT=$(grep '^\s*port:' "$STACK_FILE" | head -1 | sed 's/^[^:]*: *//' | tr -d '"' | tr -d "'" | tr -d '\r')
OUTPUT_DIR=$(grep '^\s*output_dir:' "$STACK_FILE" | head -1 | sed 's/^[^:]*: *//' | tr -d '"' | tr -d "'" | tr -d '\r')

# --- Header ---
cat <<HEADER
# Build Prompt: $PROJECT_NAME

You are building a project called **$PROJECT_NAME** — $PROJECT_DESC.

## Stack
- Language: $LANGUAGE
- Framework: $FRAMEWORK
- Database: $DATABASE
- Frontend: $FRONTEND
- Port: $PROJECT_PORT

## Output Directory
Write all generated code to: \`$OUTPUT_DIR\` (relative to this spec directory)

## Instructions
1. Read ALL technology reference files below — they define HOW to implement
2. Read ALL specification files below — they define WHAT to implement
3. Follow the technology patterns exactly (they are prescriptive standards)
4. Build in the order specified in the specification files

---

HEADER

# --- Technology Files ---
# Always include common.md first
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

emit_file "$PROJECT_DIR/stack/common.md" "Common Practices (stack/common.md)"

# Language
if [ -n "$LANGUAGE" ] && [ -f "$PROJECT_DIR/stack/${LANGUAGE}.md" ]; then
    emit_file "$PROJECT_DIR/stack/${LANGUAGE}.md" "Language: ${LANGUAGE} (stack/${LANGUAGE}.md)"
fi

# Framework
if [ -n "$FRAMEWORK" ] && [ -f "$PROJECT_DIR/stack/${FRAMEWORK}.md" ]; then
    emit_file "$PROJECT_DIR/stack/${FRAMEWORK}.md" "Framework: ${FRAMEWORK} (stack/${FRAMEWORK}.md)"
fi

# Database
if [ -n "$DATABASE" ] && [ -f "$PROJECT_DIR/stack/${DATABASE}.md" ]; then
    emit_file "$PROJECT_DIR/stack/${DATABASE}.md" "Database: ${DATABASE} (stack/${DATABASE}.md)"
fi

# Frontend
if [ -n "$FRONTEND" ] && [ -f "$PROJECT_DIR/stack/${FRONTEND}.md" ]; then
    emit_file "$PROJECT_DIR/stack/${FRONTEND}.md" "Frontend: ${FRONTEND} (stack/${FRONTEND}.md)"
fi

# --- STACK.yaml itself ---
echo "---"
echo ""
echo "## Project Configuration (STACK.yaml)"
echo ""
echo '```yaml'
cat "$STACK_FILE"
echo '```'
echo ""

# --- Specification Files ---
echo ""
echo "# PROJECT SPECIFICATION"
echo ""

SPECS=$(grep '^\s*- [0-9]' "$STACK_FILE" | sed 's/^\s*- //' | tr -d '\r')

if [ -n "$SPECS" ]; then
    while IFS= read -r SPEC; do
        SPEC_PATH="$PROJECT_DIR/$SPEC"
        if [ -f "$SPEC_PATH" ]; then
            emit_file "$SPEC_PATH" "Spec: $SPEC"
        else
            echo "<!-- WARNING: $SPEC listed in STACK.yaml but file not found -->"
            echo ""
        fi
    done <<< "$SPECS"
fi

# --- Footer ---
cat <<FOOTER
---

# END OF BUILD PROMPT

Build this project following the technology references above for implementation patterns
and the specification files for the specific features and behavior.
FOOTER
