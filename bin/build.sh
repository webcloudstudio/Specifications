#!/bin/bash
# CommandCenter Operation
# Name: Build Prompt
# Category: maintenance

# Tags the current commit with an annotated build tag and generates a complete build prompt.
# Annotated tags are permanent git objects — never pruned by git gc.
#
# Usage:
#   bash bin/build.sh <project-name>                    # Print prompt to stdout (also tags)
#   bash bin/build.sh <project-name> > build-prompt.md  # Save to file
#   bash bin/build.sh <project-name> --tag-only         # Tag without generating prompt
#   bash bin/build.sh <project-name> --no-tag           # Generate prompt without tagging
#
# Build tags:
#   build/{project}/{YYYY-MM-DD.N}
#
# Examples:
#   bash bin/build.sh Game-Build > build-prompt.md
#   git diff build/Game-Build/2026-03-19.1..build/Game-Build/2026-03-19.2 -- Game-Build/

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TAG_ONLY=false
NO_TAG=false
POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --tag-only) TAG_ONLY=true ;;
        --no-tag)   NO_TAG=true ;;
        --*)        ;;
        *)          [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/build.sh <spec-name> [--no-tag|--tag-only]" >&2
    exit 1
fi

PROJECT_DIR="$REPO_DIR/$POSITIONAL"
PROJECT_NAME="$POSITIONAL"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Spec directory not found: $PROJECT_DIR" >&2
    exit 1
fi
METADATA_FILE="$PROJECT_DIR/METADATA.md"

if [ ! -f "$METADATA_FILE" ]; then
    echo "ERROR: METADATA.md not found at $METADATA_FILE" >&2
    exit 1
fi

# --- Check for uncommitted changes in project directory ---
cd "$REPO_DIR"
REL_PATH="$(realpath --relative-to="$REPO_DIR" "$PROJECT_DIR" 2>/dev/null || echo "$PROJECT_NAME")"
if [ -n "$(git status --porcelain -- "$REL_PATH/" 2>/dev/null || true)" ]; then
    echo "WARNING: Uncommitted changes in $PROJECT_NAME/. Commit before building for a clean tag." >&2
    echo "         Proceeding anyway — tag will point to current HEAD." >&2
    echo "" >&2
fi

# --- Create build tag ---
if [ "$NO_TAG" = false ]; then
    TODAY=$(date '+%Y-%m-%d')
    # Find next build number for today
    BUILD_NUM=1
    while git tag -l "build/${PROJECT_NAME}/${TODAY}.${BUILD_NUM}" | grep -q .; do
        BUILD_NUM=$((BUILD_NUM + 1))
    done

    TAG_NAME="build/${PROJECT_NAME}/${TODAY}.${BUILD_NUM}"
    COMMIT_SHA=$(git rev-parse HEAD)
    COMMIT_MSG=$(git log -1 --format='%s')

    git tag -a "$TAG_NAME" -m "Build: ${PROJECT_NAME} ${TODAY}.${BUILD_NUM}
Commit: ${COMMIT_SHA}
Message: ${COMMIT_MSG}
Built: $(date '+%Y-%m-%d %H:%M:%S')"

    echo "Tagged: $TAG_NAME → $(git rev-parse --short HEAD)" >&2
    echo "" >&2

    # Show diff from previous build if one exists
    PREV_TAG=$(git tag -l "build/${PROJECT_NAME}/*" --sort=-version:refname | head -2 | tail -1)
    if [ -n "$PREV_TAG" ] && [ "$PREV_TAG" != "$TAG_NAME" ]; then
        DIFF_STAT=$(git diff --stat "$PREV_TAG".."$TAG_NAME" -- "$PROJECT_NAME/" 2>/dev/null || true)
        if [ -n "$DIFF_STAT" ]; then
            echo "Changes since $PREV_TAG:" >&2
            echo "$DIFF_STAT" >&2
            echo "" >&2
        fi
    fi
fi

if [ "$TAG_ONLY" = true ]; then
    exit 0
fi

# --- Generate build prompt (reuse generate_prompt.sh logic) ---
# Include CONVERT.md in the build prompt so the AI can expand concise specs inline
CONVERT_FILE="$REPO_DIR/RulesEngine/CONVERT.md"

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
BUILD_TAG_INFO=""
if [ "$NO_TAG" = false ]; then
    BUILD_TAG_INFO="Build tag: \`$TAG_NAME\` (commit $(git rev-parse --short HEAD))"
fi

cat <<HEADER
# Build Prompt: $PROJECT_NAME

You are building **${DISPLAY_NAME:-$PROJECT_NAME}** — ${DESCRIPTION:-"(no description)"}.
${BUILD_TAG_INFO}

## Stack
$(for comp in "${COMPONENTS[@]}"; do echo "- $comp"; done)
- Port: $PORT

## Instructions
1. Read the CONVERSION RULES — they explain how concise specs should be interpreted
2. Read the INTEGRATION STANDARD (CLAUDE_RULES) — project structure requirements
3. Read ALL technology references — they define HOW to implement (prescriptive)
4. Read ALL specification files — they define WHAT to implement
5. Build the complete application following all patterns exactly

---

HEADER

# --- Conversion Rules ---
if [ -f "$CONVERT_FILE" ]; then
    echo "# CONVERSION RULES"
    echo ""
    emit_file "$CONVERT_FILE" "CONVERT.md (RulesEngine/CONVERT.md)"
fi

# --- CLAUDE_RULES.md ---
if [ -f "$REPO_DIR/RulesEngine/CLAUDE_RULES.md" ]; then
    echo "# PROJECT INTEGRATION STANDARD"
    echo ""
    emit_file "$REPO_DIR/RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES.md"
fi

# --- Technology Files ---
echo "# TECHNOLOGY REFERENCES"
echo ""
emit_file "$REPO_DIR/RulesEngine/stack/common.md" "Common Practices (stack/common.md)"

for comp in "${COMPONENTS[@]}"; do
    comp_clean="$(echo "$comp" | tr -d ' ')"
    comp_lower="$(echo "$comp_clean" | tr '[:upper:]' '[:lower:]')"
    stack_file="$REPO_DIR/RulesEngine/stack/${comp_lower}.md"
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

for spec_file in $(find "$PROJECT_DIR" -maxdepth 1 -name '*.md' ! -name 'METADATA.md' | sort); do
    fname="$(basename "$spec_file")"
    emit_file "$spec_file" "Spec: $fname"
done

# --- Footer ---
cat <<FOOTER
---

# END OF BUILD PROMPT

Build this project following the conversion rules, integration standard, technology references, and specification files above.
All patterns in the technology references are prescriptive — use them exactly as shown.
Expand concise specifications inline according to the conversion rules during implementation.
FOOTER
