#!/bin/bash
# CommandCenter Operation
# Name: Iterate
# Category: maintenance

# Generates a focused iteration prompt from numbered ticket files added to the
# specification directory since the last oneshot build. Ticket types: SCREEN-NNN-*,
# FEATURE-NNN-*, PATCH-NNN-*, AC-NNN-*, INTENT-NNN-*. The agent validates each item
# before implementing — underspecified items are rejected. A scorecard is written after.
# Does not rebuild from scratch. Run claude -p from the prototype directory.
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

# --- Numbered ticket files added since the build tag ---
# Ticket types: SCREEN-NNN-*, FEATURE-NNN-*, PATCH-NNN-*, AC-NNN-*, INTENT-NNN-*
# Any file matching PREFIX-[0-9]{3}[-.]*.md added after the build tag.
# Order is preserved by the 3-digit number prefix.
NEW_ITEMS=$(git -C "$REPO_DIR" diff --diff-filter=A --name-only "$BUILD_TAG" -- "${PROJECT_NAME}/" 2>/dev/null \
    | grep '\.md$' \
    | grep -E "^${PROJECT_NAME}/[A-Z]+-[0-9]{3}[-.]" \
    | sed "s|^${PROJECT_NAME}/||" \
    | sort \
    || true)

# --- Summary ---
DISPLAY_NAME=$(get_metadata "display_name")
SHORT_COMMIT="${BUILD_COMMIT:0:8}"
SPEC_COMMIT=$(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || true)
ITEM_COUNT=$(echo "$NEW_ITEMS" | grep -c '[^[:space:]]' 2>/dev/null || echo 0)

echo "Iterate: $PROJECT_NAME" >&2
echo "  Tag:       $BUILD_TAG ($SHORT_COMMIT)" >&2
echo "  Spec:      $SPEC_COMMIT" >&2
echo "  Prototype: $PROTO_DIR" >&2
echo "  Work items: $ITEM_COUNT" >&2
if [ -n "$NEW_ITEMS" ]; then
    echo "$NEW_ITEMS" | while read -r f; do [ -n "$f" ] && echo "    $f" >&2; done
fi
echo "" >&2
echo "  Run from prototype directory:" >&2
echo "    cd $PROTO_DIR" >&2
echo "    claude -p \"\$(cat $SPEC_DIR/iterate-prompt.md)\"" >&2
echo "" >&2

if [ "$ITEM_COUNT" -eq 0 ]; then
    echo "WARNING: No numbered ticket files found since $BUILD_TAG." >&2
    echo "         Add SCREEN-NNN-*.md, FEATURE-NNN-*.md, PATCH-NNN-*.md, AC-NNN-*.md, or INTENT-NNN-*.md files." >&2
fi

# --- Record prototype directory and spec commit in Specifications/.env ---
{
    grep -v "^PROTOTYPE_DIR=" "$ENV_FILE" 2>/dev/null || true
    echo "PROTOTYPE_DIR=$PROTO_DIR"
} > "$ENV_FILE.tmp" && mv "$ENV_FILE.tmp" "$ENV_FILE"

# --- Write spec commit to Prototype <PROJECT>/.env so prototype knows what specs it implements ---
if [ -d "$PROTO_DIR" ]; then
    PROTO_ENV="$PROTO_DIR/.env"
    {
        grep -v "^SPEC_COMMIT=\|^SPEC_TAG=" "$PROTO_ENV" 2>/dev/null || true
        echo "SPEC_COMMIT=$SPEC_COMMIT"
        echo "SPEC_TAG=$BUILD_TAG"
    } > "$PROTO_ENV.tmp" && mv "$PROTO_ENV.tmp" "$PROTO_ENV"
    echo "  Spec commit written to Prototype .env: $SPEC_COMMIT" >&2
fi

DEPLOY_LOG="$SPEC_DIR/DEPLOY_LOG.md"
if [ ! -f "$DEPLOY_LOG" ]; then
    echo "# Deploy Log: $PROJECT_NAME" > "$DEPLOY_LOG"
    echo "" >> "$DEPLOY_LOG"
fi
{
    echo "## $(date '+%Y-%m-%d %H:%M') — iterate"
    echo "- Tag:       $BUILD_TAG (baseline)"
    echo "- Spec:      $SPEC_COMMIT"
    echo "- Prototype: $PROTO_DIR"
    [ "$ITEM_COUNT" -gt 0 ] && echo "- Items:     $ITEM_COUNT"
    echo ""
} >> "$DEPLOY_LOG"

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

if [ -n "$NEW_ITEMS" ]; then
    echo "**Work items (in order):**"
    echo "$NEW_ITEMS" | while read -r f; do [ -n "$f" ] && echo "- $f"; done
    echo ""
fi
if [ "$ITEM_COUNT" -eq 0 ]; then
    echo "_(no pending work detected)_"
    echo ""
fi

# --- Validation protocol ---
cat <<VALIDATION
---

## Validation Rules (apply before implementing anything)

For each work item listed above, check:

1. Intent / description is concrete — not vague
2. Changes Required are specific enough to implement without guessing
3. \`## Open Questions\` exists and is empty or \`None.\`
4. No placeholder text: \`TODO\`, \`TBD\`, \`[placeholder]\`

**If any check fails:**
- Do NOT implement the item
- Write: \`[UNDERSPECIFIED] <filename>: <what is missing>\`
- Add a \`## Rejection Reason\` section to the file and leave it in place

**If all checks pass:** implement the item fully, then delete the ticket file.
(Canonical spec files — SCREEN-Name.md, FEATURE-Name.md — are kept; numbered tickets are deleted after apply.)

---

VALIDATION

# --- Architecture context (always included) ---
echo "# ARCHITECTURE"
echo ""
emit_file "$SPEC_DIR/ARCHITECTURE.md" "ARCHITECTURE.md"

# --- Work items (in number order) ---
if [ -n "$NEW_ITEMS" ]; then
    echo "# WORK ITEMS"
    echo ""
    echo "$NEW_ITEMS" | while read -r fname; do
        [ -z "$fname" ] && continue
        fpath="$SPEC_DIR/$fname"
        emit_file "$fpath" "Item: $fname"
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

After applying all accepted items, write or update \`docs/SCORECARD.md\` in the prototype directory.
Create \`docs/\` if it does not exist.

To compute KPIs, read these files:
- Pending tickets: count \`**Status:** pending\` in \`$SPEC_DIR/changes/CHANGE-*.md\`
- P0/P1 gaps: count lines beginning with \`P0\` or \`P1\` in \`$SPEC_DIR/REFERENCE_GAPS.md\`
- Open questions: count non-\`None.\` bullet lines in \`## Open Questions\` sections across \`$SPEC_DIR\`/*.md

Format:
\`\`\`
# Iteration Scorecard: $PROJECT_NAME
**Tag:** $BUILD_TAG  **Date:** $(date '+%Y-%m-%d')

## KPIs
| Metric | Value |
|--------|-------|
| Completion (this session) | X% (N applied / M attempted) |
| Pending tickets remaining | N |
| P0/P1 reference gaps | N |
| Unresolved open questions | N |

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
