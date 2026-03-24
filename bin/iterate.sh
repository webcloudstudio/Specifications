#!/bin/bash
# CommandCenter Operation
# Name: Iterate
# Category: maintenance

# Generates a focused iteration prompt from spec changes since the last oneshot build.
# Reads PROTOTYPE_BUILD_TAG from .env, diffs spec files against that tag, and emits
# only the changed spec files plus ACCEPTANCE_CRITERIA.md. The agent applies the
# changes to the existing prototype — it does not rebuild from scratch.
#
# Usage:
#   bash bin/iterate.sh <ProjectName>
#   bash bin/iterate.sh <ProjectName> > <ProjectName>/iterate-prompt.md
#   cd /mnt/c/Users/barlo/projects/<ProjectName>
#   claude -p "$(cat /mnt/c/Users/barlo/projects/Specifications/<ProjectName>/iterate-prompt.md)"
#
# Note: claude -p runs non-interactively using your Claude subscription (not API tokens).
#
# Requires: PROTOTYPE_BUILD_TAG in <ProjectName>/.env (written by oneshot.sh)
# Reads:    spec .md files changed since the build tag, ACCEPTANCE_CRITERIA.md
# Excludes: IDEAS.md, REFERENCE_GAPS.md, SCORECARD.md
#
# Arguments:
#   $1  ProjectName (required)
#
# Exit codes:
#   0  Prompt written to stdout
#   1  Missing argument, spec directory, METADATA.md, or build tag

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --*) ;;
        *) [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/iterate.sh <ProjectName> [> <ProjectName>/iterate-prompt.md]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Spec directory not found: $SPEC_DIR" >&2
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

# --- Find changed spec files since the build tag ---
# Compares tag to current working tree (includes uncommitted changes)
SKIP_PATTERN="^${PROJECT_NAME}/\(METADATA\|IDEAS\|REFERENCE_GAPS\|ACCEPTANCE_CRITERIA\)\.md$"
CHANGED_NAMES=$(git -C "$REPO_DIR" diff --name-only "$BUILD_TAG" -- "${PROJECT_NAME}/" 2>/dev/null \
    | grep '\.md$' \
    | grep -v "$SKIP_PATTERN" \
    | sed "s|^${PROJECT_NAME}/||" \
    || true)

# --- Helpers ---
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

DISPLAY_NAME=$(get_metadata "display_name")
STACK=$(get_metadata "stack")
SHORT_COMMIT="${BUILD_COMMIT:0:8}"

echo "Iterate: $PROJECT_NAME" >&2
echo "  Tag:   $BUILD_TAG ($SHORT_COMMIT)" >&2
if [ -n "$CHANGED_NAMES" ]; then
    echo "  Changed spec files:" >&2
    echo "$CHANGED_NAMES" | while read -r f; do echo "    $f" >&2; done
else
    echo "  WARNING: No spec changes detected since $BUILD_TAG — emitting all spec files." >&2
fi
echo "" >&2

# --- Header ---
cat <<HEADER
# Iterate Prompt: $PROJECT_NAME

You are applying spec changes to the existing **${DISPLAY_NAME:-$PROJECT_NAME}** prototype.
Do not rebuild from scratch. Read the changed spec files and apply only those changes.

Previous build: \`$BUILD_TAG\` (${SHORT_COMMIT})

## Changed Spec Files
HEADER

if [ -n "$CHANGED_NAMES" ]; then
    echo "$CHANGED_NAMES" | while read -r f; do echo "- $f"; done
else
    echo "_(no diff detected — all spec files included)_"
fi

cat <<INSTRUCTIONS

## Instructions

1. Read ACCEPTANCE_CRITERIA.md — these are hard requirements, all must pass
2. Read the changed spec files — these define what has changed since the last build
3. Apply changes to the existing code; do not rebuild from scratch
4. Follow all patterns in CLAUDE_RULES.md exactly

---

INSTRUCTIONS

# --- Rules ---
emit_file "$REPO_DIR/RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES.md"

# --- Stack files ---
if [ -n "$STACK" ]; then
    IFS='/' read -ra COMPONENTS <<< "$STACK"
    emit_file "$REPO_DIR/RulesEngine/stack/common.md" "Common Practices (stack/common.md)"
    for comp in "${COMPONENTS[@]}"; do
        comp_lower="$(echo "$comp" | tr -d ' ' | tr '[:upper:]' '[:lower:]')"
        stack_file="$REPO_DIR/RulesEngine/stack/${comp_lower}.md"
        [ -f "$stack_file" ] && emit_file "$stack_file" "$comp (stack/${comp_lower}.md)"
    done
fi

# --- Project config ---
echo "---"
echo ""
echo "## Project Configuration (METADATA.md)"
echo ""
echo '```'
cat "$METADATA_FILE"
echo '```'
echo ""
echo ""

# --- Changed spec files (or all if no diff detected) ---
echo "# CHANGED SPECIFICATIONS"
echo ""

if [ -n "$CHANGED_NAMES" ]; then
    echo "$CHANGED_NAMES" | while read -r fname; do
        fpath="$SPEC_DIR/$fname"
        [ -f "$fpath" ] && emit_file "$fpath" "Spec: $fname"
    done
else
    for spec_file in $(find "$SPEC_DIR" -maxdepth 1 -name '*.md' \
            ! -name 'METADATA.md' ! -name 'IDEAS.md' \
            ! -name 'REFERENCE_GAPS.md' ! -name 'ACCEPTANCE_CRITERIA.md' | sort); do
        fname="$(basename "$spec_file")"
        emit_file "$spec_file" "Spec: $fname"
    done
fi

# --- Acceptance Criteria (always included) ---
if [ -f "$SPEC_DIR/ACCEPTANCE_CRITERIA.md" ]; then
    echo "# ACCEPTANCE CRITERIA"
    echo ""
    emit_file "$SPEC_DIR/ACCEPTANCE_CRITERIA.md" "ACCEPTANCE_CRITERIA.md — all criteria are required"
fi

# --- Footer ---
cat <<FOOTER
---

# END OF ITERATE PROMPT

Apply the changed specifications to the existing prototype.
All listed acceptance criteria are hard requirements — all must pass.

## Session Summary Requirement
At the end of this session, print:
\`\`\`
--- Changes Applied ---
<filename>: <what changed>
\`\`\`
FOOTER
