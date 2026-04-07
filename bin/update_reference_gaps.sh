#!/bin/bash
# CommandCenter Operation
# Name: Gap Analysis
# Category: maintenance
# Args: Spec

# Runs gap analysis comparing spec vs prototype vs reference implementation.
# Uses claude -p (subscription, not API tokens).
#
# Usage:
#   bash bin/update_reference_gaps.sh <spec-name>
#
# Reads: Specifications/<spec>/*.md, prototype code, reference implementation
# Writes: Specifications/<spec>/REFERENCE_GAPS.md

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="$REPO_DIR/prompts/update_reference_gaps.md"

POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --*) ;;
        *)   [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/update_reference_gaps.sh <spec-name>" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
PROTO_DIR="$PROJECTS_DIR/${PROJECT_NAME}_prototype"
REF_DIR="$PROJECTS_DIR/$PROJECT_NAME"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Spec directory not found: $SPEC_DIR" >&2
    exit 1
fi

if [ ! -d "$PROTO_DIR" ]; then
    echo "WARNING: Prototype directory not found at $PROTO_DIR" >&2
    echo "         Trying $REF_DIR as prototype..." >&2
    PROTO_DIR="$REF_DIR"
fi

if [ ! -f "$PROMPT_FILE" ]; then
    echo "ERROR: Prompt file not found: $PROMPT_FILE" >&2
    exit 1
fi

echo "Gap Analysis: $PROJECT_NAME" >&2
echo "  Spec:      $SPEC_DIR" >&2
echo "  Prototype: $PROTO_DIR" >&2
echo "  Reference: $REF_DIR" >&2
echo "" >&2

# --- Assemble context ---
PROMPT="$(tr -d '\r' < "$PROMPT_FILE")

---

## Context

### Specification Directory
Location: $SPEC_DIR

### Prototype Directory
Location: $PROTO_DIR

### Reference Implementation
Location: $REF_DIR (READ-ONLY — do not modify)

### Current REFERENCE_GAPS.md
$(cat "$SPEC_DIR/REFERENCE_GAPS.md" 2>/dev/null || echo "(does not exist yet)")
"

# --- Check for claude CLI ---
if ! command -v claude &>/dev/null; then
    echo "ERROR: claude CLI not found. Install Claude Code first." >&2
    echo "" >&2
    echo "Alternatively, copy the prompt below and paste into a Claude Code session" >&2
    echo "in the prototype directory ($PROTO_DIR):" >&2
    echo "" >&2
    echo "--- PROMPT START ---" >&2
    echo "$PROMPT" >&2
    echo "--- PROMPT END ---" >&2
    exit 1
fi

echo "Running claude -p with subscription..." >&2
echo "" >&2

cd "$PROTO_DIR" && claude -p "$PROMPT" \
    --add-dir "$SPEC_DIR" \
    --add-dir "$REF_DIR" \
    --allowedTools "Read,Write,Glob,Grep"

echo "" >&2
echo "Gap analysis complete. Check: $SPEC_DIR/REFERENCE_GAPS.md" >&2
