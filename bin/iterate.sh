#!/bin/bash
# CommandCenter Operation
# Name: Iterate
# Category: maintenance

# Generates an iteration prompt for a oneshot-built prototype.
# Reads IDEAS.md, REFERENCE_GAPS.md, ACCEPTANCE_CRITERIA.md from the spec directory
# and current SCORECARD.md from the prototype. Outputs a prompt to paste into
# Claude Code in the prototype directory.
#
# Usage:
#   bash bin/iterate.sh <ProjectName>
#   bash bin/iterate.sh <ProjectName> > <ProjectName>/iterate-prompt.md
#   bash bin/iterate.sh <ProjectName> --no-scorecard   # skip scorecard regeneration
#
# Reads:  Specifications/<ProjectName>/*.md, IDEAS.md, REFERENCE_GAPS.md, ACCEPTANCE_CRITERIA.md
# Writes: <ProjectName>_prototype/SCORECARD.md (via scorecard.sh), then iterate-prompt.md to stdout

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NO_SCORECARD=false
POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --no-scorecard) NO_SCORECARD=true ;;
        --*)            ;;
        *)              [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/iterate.sh <ProjectName> [--no-scorecard]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
PROTO_DIR="$PROJECTS_DIR/${PROJECT_NAME}_prototype"

# Fall back to non-_prototype directory
if [ ! -d "$PROTO_DIR" ]; then
    PROTO_DIR="$PROJECTS_DIR/$PROJECT_NAME"
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Spec directory not found: $SPEC_DIR" >&2
    exit 1
fi

if [ ! -d "$PROTO_DIR" ]; then
    echo "ERROR: Prototype directory not found: $PROTO_DIR" >&2
    echo "       Expected: ${PROJECT_NAME}_prototype/ or ${PROJECT_NAME}/" >&2
    exit 1
fi

METADATA_FILE="$SPEC_DIR/METADATA.md"
if [ ! -f "$METADATA_FILE" ]; then
    echo "ERROR: METADATA.md not found: $METADATA_FILE" >&2
    exit 1
fi

get_metadata() {
    grep "^${1}:" "$METADATA_FILE" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r'
}

DISPLAY_NAME=$(get_metadata "display_name")

# --- Run scorecard to update SCORECARD.md ---
SCORECARD_FILE="$PROTO_DIR/SCORECARD.md"
if [ "$NO_SCORECARD" = false ]; then
    echo "Running scorecard..." >&2
    bash "$REPO_DIR/bin/scorecard.sh" "$PROJECT_NAME" >/dev/null 2>&1 || true
fi

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

# --- Summarize what needs doing ---
OPEN_GAPS=0
HAS_IDEAS=false
P0_COUNT=0
P1_COUNT=0

if [ -f "$SPEC_DIR/REFERENCE_GAPS.md" ]; then
    OPEN_GAPS=$(grep -c '^\- \[ \]' "$SPEC_DIR/REFERENCE_GAPS.md" 2>/dev/null || echo 0)
    OPEN_GAPS=$(echo "$OPEN_GAPS" | tr -d '[:space:]')
    P0_COUNT=$(grep '^\- \[ \]' "$SPEC_DIR/REFERENCE_GAPS.md" 2>/dev/null | grep -c '\[P0\]' || echo 0)
    P0_COUNT=$(echo "$P0_COUNT" | tr -d '[:space:]')
    P1_COUNT=$(grep '^\- \[ \]' "$SPEC_DIR/REFERENCE_GAPS.md" 2>/dev/null | grep -c '\[P1\]' || echo 0)
    P1_COUNT=$(echo "$P1_COUNT" | tr -d '[:space:]')
fi

if [ -f "$SPEC_DIR/IDEAS.md" ]; then
    IDEAS_LINES=$(grep -c '^-' "$SPEC_DIR/IDEAS.md" 2>/dev/null || echo 0)
    IDEAS_LINES=$(echo "$IDEAS_LINES" | tr -d '[:space:]')
    [ "$IDEAS_LINES" -gt 0 ] && HAS_IDEAS=true
fi

SCORE_SUMMARY=""
if [ -f "$SCORECARD_FILE" ]; then
    SCORE_SUMMARY=$(grep '^\*\*[0-9]' "$SCORECARD_FILE" 2>/dev/null | head -1 | tr -d '*' || true)
fi

echo "Iterate: $PROJECT_NAME" >&2
echo "  Proto: $PROTO_DIR" >&2
[ -n "$SCORE_SUMMARY" ] && echo "  Score: $SCORE_SUMMARY" >&2
[ "$OPEN_GAPS" -gt 0 ] && echo "  Gaps:  $OPEN_GAPS open ($P0_COUNT P0, $P1_COUNT P1)" >&2
[ "$HAS_IDEAS" = true ] && echo "  Ideas: unprocessed entries in IDEAS.md" >&2
echo "" >&2

# --- Header ---
cat <<HEADER
# Iterate Prompt: $PROJECT_NAME

You are ITERATING **${DISPLAY_NAME:-$PROJECT_NAME}** — the prototype already exists.
Do not rebuild from scratch. Apply targeted changes only.

## Session Goals

HEADER

[ "$HAS_IDEAS" = true ] && echo "- Unprocessed ideas in IDEAS.md — **process these first**"
[ "$OPEN_GAPS" -gt 0 ]  && echo "- $OPEN_GAPS open gaps ($P0_COUNT P0, $P1_COUNT P1) in REFERENCE_GAPS.md"
[ -n "$SCORE_SUMMARY" ] && echo "- Current scorecard: $SCORE_SUMMARY"
echo ""

cat <<INSTRUCTIONS
## Instructions

1. **Process IDEAS.md first** (if entries exist): route each idea to ACCEPTANCE_CRITERIA.md,
   REFERENCE_GAPS.md, or a spec file. Delete each idea after routing.
2. **Fix SCORECARD failures** — every `[ ]` in SCORECARD.md is a failing check
3. **Implement P0 gaps** from REFERENCE_GAPS.md, then P1 if time permits
4. **For every code change**: update the corresponding spec file in Specifications/${PROJECT_NAME}/
5. **When a gap is closed**: check the box in REFERENCE_GAPS.md
6. **Print session summary** at the end

---

INSTRUCTIONS

# --- Rules ---
emit_file "$REPO_DIR/RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES.md"
emit_file "$REPO_DIR/RulesEngine/CLAUDE_PROTOTYPE.md" "CLAUDE_PROTOTYPE.md"

# --- Core spec files ---
echo "# SPECIFICATION"
echo ""
for spec_file in \
    "$SPEC_DIR/FUNCTIONALITY.md" \
    "$SPEC_DIR/ARCHITECTURE.md" \
    "$SPEC_DIR/DATABASE.md"; do
    fname="$(basename "$spec_file")"
    emit_file "$spec_file" "Spec: $fname"
done

for spec_file in "$SPEC_DIR"/SCREEN-*.md "$SPEC_DIR"/FEATURE-*.md; do
    [ -f "$spec_file" ] || continue
    fname="$(basename "$spec_file")"
    emit_file "$spec_file" "Spec: $fname"
done

# --- Iteration artifacts ---
echo "# ITERATION TARGETS"
echo ""
emit_file "$SPEC_DIR/IDEAS.md" "IDEAS.md — process each entry and delete after routing"
emit_file "$SPEC_DIR/ACCEPTANCE_CRITERIA.md" "ACCEPTANCE_CRITERIA.md — all criteria are required"
emit_file "$SPEC_DIR/REFERENCE_GAPS.md" "REFERENCE_GAPS.md — implement P0 and P1 gaps"

# --- Scorecard ---
echo "# CURRENT SCORECARD"
echo ""
emit_file "$SCORECARD_FILE" "SCORECARD.md (as of this run)"

# --- Footer ---
cat <<FOOTER
---

# END OF ITERATE PROMPT

Iterate this prototype: fix scorecard failures, close P0/P1 gaps, process ideas.
For every code change, update the corresponding spec file in Specifications/${PROJECT_NAME}/.

## Session Summary Requirement
At the end of this session, print:
\`\`\`
--- Specification Updates ---
<filename>: <what changed>
\`\`\`
FOOTER
