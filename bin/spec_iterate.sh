#!/bin/bash
# CommandCenter Operation
# Name: Spec Iterate
# Category: maintenance
# Args: Spec
# Prompt: prompts/spec_iterate.md
# Rules: RulesEngine/BUSINESS_RULES.md

# AI-powered specification gap analysis and iteration planning.
# Calls claude -p (subscription, not API tokens) to:
#   1. Update <Spec>/REFERENCE_GAPS.md with current gap state
#   2. Write <Spec>/SPEC_SCORECARD.md — spec quality rating across 7 dimensions
#   3. Write <Spec>/SPEC_ITERATION.md — a focused prompt that creates 1-2 spec files
#      targeting the highest-priority open gaps
#
# Workflow:
#   Step 1:  bash bin/spec_iterate.sh <ProjectName>
#            Claude updates REFERENCE_GAPS.md, writes SPEC_SCORECARD.md and SPEC_ITERATION.md
#   Step 2:  Review and edit <ProjectName>/SPEC_ITERATION.md
#   Step 3:  cd /path/to/Specifications && claude -p "$(cat <ProjectName>/SPEC_ITERATION.md)"
#            Claude creates the targeted spec files inside the spec directory
#   Step 4:  Run iterate.sh or oneshot.sh to push spec changes to the prototype
#
# Usage:
#   bash bin/spec_iterate.sh <ProjectName>
#   bash bin/spec_iterate.sh <ProjectName> --model opus
#
# Arguments:
#   $1           Project name (required) — specification directory name
#   --model      Model override: sonnet (default) | opus | haiku
#
# Exit codes:
#   0  Completed
#   1  Missing argument, missing spec directory, or claude CLI not found

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Argument parsing ---
POSITIONAL=""
MODEL="sonnet"
for arg in "$@"; do
    case "$arg" in
        --model=*) MODEL="${arg#--model=}" ;;
        --model)   shift; MODEL="${1:-sonnet}" ;;
        --*)       ;;
        *)         [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/spec_iterate.sh <ProjectName> [--model sonnet|opus|haiku]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Specification directory not found: $SPEC_DIR" >&2
    exit 1
fi

if [ ! -f "$SPEC_DIR/METADATA.md" ]; then
    echo "ERROR: METADATA.md not found in $SPEC_DIR" >&2
    exit 1
fi

if ! command -v claude &>/dev/null; then
    echo "ERROR: claude CLI not found. Install Claude Code to use this script." >&2
    exit 1
fi

# --- Metadata ---
get_metadata() {
    grep "^${1}:" "$SPEC_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r'
}
DISPLAY_NAME=$(get_metadata "display_name")
SHORT_DESC=$(get_metadata "short_description")
STATUS=$(get_metadata "status")

echo "Spec Iterate: $PROJECT_NAME" >&2
echo "  Spec:    $SPEC_DIR" >&2
echo "  Model:   $MODEL" >&2
echo "  Status:  ${STATUS:-unknown}" >&2
echo "" >&2

# --- Collect spec files ---
SPEC_FILES=$(find "$SPEC_DIR" -maxdepth 1 -name "*.md" \
    ! -name "SPEC_SCORECARD.md" \
    ! -name "SPEC_ITERATION.md" \
    | sort)

SPEC_FILE_COUNT=$(echo "$SPEC_FILES" | grep -c '.' 2>/dev/null || true)
echo "  Spec files: $SPEC_FILE_COUNT" >&2
echo "" >&2

# --- Rules files ---
RULES_DIR="$REPO_DIR/RulesEngine"
BUSINESS_RULES=""
if [ -f "$RULES_DIR/BUSINESS_RULES.md" ]; then
    BUSINESS_RULES="$(cat "$RULES_DIR/BUSINESS_RULES.md")"
fi

# --- Build the prompt ---
CURRENT_DATE=$(date '+%Y-%m-%d')
CURRENT_GAPS=""
if [ -f "$SPEC_DIR/REFERENCE_GAPS.md" ]; then
    CURRENT_GAPS="$(cat "$SPEC_DIR/REFERENCE_GAPS.md")"
fi

# --- Assemble prompt from template ---
# Escape & and \ in SHORT_DESC so sed doesn't misinterpret them in the replacement
SHORT_DESC_SAFE=$(printf '%s' "${SHORT_DESC:-}" | sed 's/[&\]/\\&/g')
PROMPT=$(tr -d '\r' < "$REPO_DIR/prompts/spec_iterate.md" | sed \
    -e "s|{{DISPLAY_NAME}}|${DISPLAY_NAME:-$PROJECT_NAME}|g" \
    -e "s|{{SHORT_DESC}}|$SHORT_DESC_SAFE|g" \
    -e "s|{{STATUS}}|${STATUS:-PROTOTYPE}|g" \
    -e "s|{{SPEC_DIR}}|$SPEC_DIR|g" \
    -e "s|{{CURRENT_DATE}}|$CURRENT_DATE|g" \
    -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" \
    -e "s|{{REPO_DIR}}|$REPO_DIR|g")

# Append dynamic content as appendices
PROMPT="$PROMPT

$BUSINESS_RULES

---

## Appendix: Current REFERENCE_GAPS.md

$CURRENT_GAPS"


# --- Run ---
echo "Running claude -p (model: $MODEL)..." >&2
echo "This may take 30–60 seconds." >&2
echo "" >&2

cd "$SPEC_DIR" && claude -p "$PROMPT" \
    --model "$MODEL" \
    --allowedTools "Read,Write,Glob,Grep" \
    --add-dir "$REPO_DIR/RulesEngine"

echo "" >&2
echo "Done. Output files:" >&2
echo "  $SPEC_DIR/REFERENCE_GAPS.md" >&2
echo "  $SPEC_DIR/SPEC_SCORECARD.md" >&2
echo "  $SPEC_DIR/SPEC_ITERATION.md" >&2
