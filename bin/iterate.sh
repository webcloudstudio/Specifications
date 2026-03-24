#!/bin/bash
# CommandCenter Operation
# Name: Iterate
# Category: maintenance

# Generates a focused iteration prompt from pending CHANGE tickets and new specification
# files added since the last oneshot build. The agent validates each item before
# implementing — underspecified items are rejected with explanation. A scorecard is
# written after implementation. Does not rebuild from scratch.
# Run claude -p from the prototype directory so the agent can read the existing code.
#
# Usage:
#   bash bin/iterate.sh <ProjectName> > <ProjectName>/iterate-prompt.md
#
# Examples:
#   bash bin/iterate.sh GAME > GAME/iterate-prompt.md
#   cd /mnt/c/Users/barlo/projects/GAME
#   claude -p "$(cat /mnt/c/Users/barlo/projects/Specifications/GAME/iterate-prompt.md)"
#   # Uses your Claude subscription. Run from the prototype directory.
#
# Arguments:
#   $1        Project name (required) — specification directory name under Specifications/
#
# Exit codes:
#   0  Prompt written to stdout
#   1  Missing argument, specification directory, METADATA.md, or build tag

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"

POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --*) ;;
        *) [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/iterate.sh <ProjectName> > <ProjectName>/iterate-prompt.md" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"
PROTO_DIR="$PROJECTS_DIR/$PROJECT_NAME"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Specification directory not found: $SPEC_DIR" >&2
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

# --- Read build tag from .env ---
ENV_FILE="$SPEC_DIR/.env"
BUILD_TAG=""
BUILD_COMMIT=""
if [ -f "$ENV_FILE" ]; then
    BUILD_TAG=$(grep "^PROTOTYPE_BUILD_TAG=" "$ENV_FILE" 2>/dev/null | head -1 | sed 's/^PROTOTYPE_BUILD_TAG=//' | tr -d '\r' || true)
    BUILD_COMMIT=$(grep "^PROTOTYPE_BUILD_COMMIT=" "$ENV_FILE" 2>/dev/null | head -1 | sed 's/^PROTOTYPE_BUILD_COMMIT=//' | tr -d '\r' || true)
fi

if [ -z "$BUILD_TAG" ]; then
    echo "ERROR: PROTOTYPE_BUILD_TAG not found in $ENV_FILE" >&2
    echo "       Run bash bin/oneshot.sh $PROJECT_NAME first to establish a build baseline." >&2
    exit 1
fi

if ! git -C "$REPO_DIR" rev-parse "$BUILD_TAG" >/dev/null 2>&1; then
    echo "ERROR: Build tag not found in git: $BUILD_TAG" >&2
    exit 1
fi

# --- New specification files added since the build tag ---
# Only FEATURE-*, SCREEN-*, UI-* files — not context files (AC, IDEAS, GAPS)
NEW_SPECS=$(git -C "$REPO_DIR" diff --diff-filter=A --name-only "$BUILD_TAG" -- "${PROJECT_NAME}/" 2>/dev/null \
    | grep '\.md$' \
    | grep -E "^${PROJECT_NAME}/(FEATURE|SCREEN|UI)-" \
    | sed "s|^${PROJECT_NAME}/||" \
    || true)

# --- Pending CHANGE tickets ---
PENDING_TICKETS=""
if [ -d "$SPEC_DIR/changes" ]; then
    while IFS= read -r ticket; do
        if grep -q '^\*\*Status:\*\* pending' "$ticket" 2>/dev/null; then
            PENDING_TICKETS="$PENDING_TICKETS$ticket"$'\n'
        fi
    done < <(find "$SPEC_DIR/changes" -maxdepth 1 -name 'CHANGE-*.md' 2>/dev/null | sort)
fi
PENDING_TICKETS="${PENDING_TICKETS%$'\n'}"

# --- Summary ---
DISPLAY_NAME=$(get_metadata "display_name")
SHORT_COMMIT="${BUILD_COMMIT:0:8}"
NEW_COUNT=$(echo "$NEW_SPECS" | grep -c '[^[:space:]]' 2>/dev/null || echo 0)
TICKET_COUNT=$(echo "$PENDING_TICKETS" | grep -c '[^[:space:]]' 2>/dev/null || echo 0)

echo "Iterate: $PROJECT_NAME" >&2
echo "  Tag:       $BUILD_TAG ($SHORT_COMMIT)" >&2
echo "  Prototype: $PROTO_DIR" >&2
echo "  New specification files: $NEW_COUNT" >&2
if [ -n "$NEW_SPECS" ]; then
    echo "$NEW_SPECS" | while read -r f; do [ -n "$f" ] && echo "    $f" >&2; done
fi
echo "  Pending tickets: $TICKET_COUNT" >&2
if [ -n "$PENDING_TICKETS" ]; then
    echo "$PENDING_TICKETS" | while read -r f; do [ -n "$f" ] && echo "    $(basename "$f")" >&2; done
fi
echo "" >&2
echo "  Run from prototype directory:" >&2
echo "    cd $PROTO_DIR" >&2
echo "    claude -p \"\$(cat $SPEC_DIR/iterate-prompt.md)\"" >&2
echo "" >&2

if [ "$NEW_COUNT" -eq 0 ] && [ "$TICKET_COUNT" -eq 0 ]; then
    echo "WARNING: No new specification files and no pending CHANGE tickets found." >&2
    echo "         Create changes/CHANGE-NNN-description.md or add new FEATURE-*/SCREEN-* files." >&2
fi

# --- Helper ---
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

# --- Prompt header ---
cat <<HEADER
# Iterate Prompt: $PROJECT_NAME

You are applying specification changes to the existing **${DISPLAY_NAME:-$PROJECT_NAME}** prototype.
Do not rebuild from scratch. Read the work items below and apply only those changes.

Previous build: \`$BUILD_TAG\` (${SHORT_COMMIT})
Prototype directory: \`$PROTO_DIR\`

## Pending Work

HEADER

if [ -n "$NEW_SPECS" ]; then
    echo "**New specification files:**"
    echo "$NEW_SPECS" | while read -r f; do [ -n "$f" ] && echo "- $f"; done
    echo ""
fi
if [ -n "$PENDING_TICKETS" ]; then
    echo "**Pending CHANGE tickets:**"
    echo "$PENDING_TICKETS" | while read -r f; do [ -n "$f" ] && echo "- $(basename "$f")"; done
    echo ""
fi
if [ "$NEW_COUNT" -eq 0 ] && [ "$TICKET_COUNT" -eq 0 ]; then
    echo "_(no pending work detected)_"
    echo ""
fi

# --- Validation protocol ---
cat <<VALIDATION
---

## Validation Rules (apply before implementing anything)

For each new specification file and each CHANGE ticket listed above:

1. The description or Intent must be concrete and specific — not vague ("improve the UI")
2. The changes required must be specific enough to implement without guessing
3. The \`## Open Questions\` section must exist and be either empty or contain only \`None.\`
4. No placeholder text: \`TODO\`, \`TBD\`, \`[placeholder]\`

**If any check fails:**
- Do NOT implement the item
- Write: \`[UNDERSPECIFIED] <filename>: <what is missing or unresolved>\`
- In CHANGE tickets: set \`**Status:** rejected\` and add a \`## Rejection Reason\` section

**If all checks pass:** implement the item fully, then in CHANGE tickets set \`**Status:** applied\`.

---

VALIDATION

# --- Architecture context (always included) ---
echo "# ARCHITECTURE"
echo ""
emit_file "$SPEC_DIR/ARCHITECTURE.md" "ARCHITECTURE.md"

# --- New specification files ---
if [ -n "$NEW_SPECS" ]; then
    echo "# NEW SPECIFICATIONS"
    echo ""
    echo "$NEW_SPECS" | while read -r fname; do
        [ -z "$fname" ] && continue
        fpath="$SPEC_DIR/$fname"
        emit_file "$fpath" "Specification: $fname"
    done
fi

# --- Pending CHANGE tickets ---
if [ -n "$PENDING_TICKETS" ]; then
    echo "# CHANGE TICKETS"
    echo ""
    echo "$PENDING_TICKETS" | while read -r fpath; do
        [ -z "$fpath" ] && continue
        fname="$(basename "$fpath")"
        emit_file "$fpath" "Ticket: $fname"
    done
fi

# --- Context files ---
if [ -f "$SPEC_DIR/ACCEPTANCE_CRITERIA.md" ] || \
   [ -f "$SPEC_DIR/IDEAS.md" ] || \
   [ -f "$SPEC_DIR/REFERENCE_GAPS.md" ]; then
    echo "# CONTEXT"
    echo ""
fi
emit_file "$SPEC_DIR/ACCEPTANCE_CRITERIA.md" "ACCEPTANCE_CRITERIA.md — all criteria are required"
emit_file "$SPEC_DIR/IDEAS.md"               "IDEAS.md"
emit_file "$SPEC_DIR/REFERENCE_GAPS.md"      "REFERENCE_GAPS.md"

# --- Footer with scorecard instruction ---
cat <<FOOTER
---

# END OF ITERATE PROMPT

Apply accepted items only. Reject and explain any underspecified items.

## Post-Implementation Scorecard

After applying all accepted items, write or update \`SCORECARD.md\` in the prototype directory.

Format:
\`\`\`
# Iteration Scorecard: $PROJECT_NAME
**Tag:** $BUILD_TAG
**Date:** $(date '+%Y-%m-%d')

## Results
- [x] FEATURE-Example — PASS: implemented and verified
- [ ] CHANGE-001 — FAIL: route updated but template not found
- [~] SCREEN-Example — PARTIAL: layout complete, interactions pending
\`\`\`

## Session Summary Requirement
At the end of this session, print:
\`\`\`
--- Changes Applied ---
<filename>: <what changed>
--- Rejected ---
<filename>: <reason>
\`\`\`
FOOTER
