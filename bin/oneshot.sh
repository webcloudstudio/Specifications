#!/bin/bash
# CommandCenter Operation
# Name: OneShot
# Category: maintenance
# Args: Spec

# Validates the Specification, detects build mode, and generates a complete AI build prompt.
# Tags the current commit as a permanent build reference (oneshot/{spec}/{YYYY-MM-DD.N}).
#
# Usage:
#   bash bin/oneshot.sh <ProjectName>                              # New build — stdout
#   bash bin/oneshot.sh <ProjectName> > <ProjectName>/prompt.md   # New build — save to file
#   bash bin/oneshot.sh <ProjectName> --update > prompt.md        # Update existing prototype
#   bash bin/oneshot.sh <ProjectName> --tag-only                  # Tag only, no prompt
#   bash bin/oneshot.sh <ProjectName> --no-tag                    # Prompt only, no tag
#
# Modes:
#   New project    No git_repo or BUILD_FEATURE_BRANCH_NAME not set in .env
#                  mkdir <ProjectName> && cd <ProjectName> && git init && git checkout -b main
#                  Open Claude Code and paste the prompt.
#   Feature Branch git_repo + BUILD_FEATURE_BRANCH_NAME both set in .env
#                  Clones or fetches the project, creates the branch, then generates the prompt.
#   Update         --update flag: generates a prompt to apply spec changes to existing code.
#                  Open Claude Code in the existing prototype directory and paste the prompt.
#
# Examples:
#   bash bin/oneshot.sh GAME > GAME/prompt.md
#   bash bin/oneshot.sh GAME --update > GAME/prompt.md
#   git diff oneshot/GAME/2026-03-19.1..oneshot/GAME/2026-03-20.1 -- GAME/

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TAG_ONLY=false
NO_TAG=false
UPDATE=false
POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --tag-only) TAG_ONLY=true ;;
        --no-tag)   NO_TAG=true ;;
        --update)   UPDATE=true ;;
        --*)        ;;
        *)          [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/oneshot.sh <ProjectName> [--no-tag|--tag-only|--update]" >&2
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

get_metadata() {
    grep "^${1}:" "$METADATA_FILE" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r'
}

# --- Validate spec first ---
echo "Validating spec..." >&2
if ! bash "$REPO_DIR/bin/validate.sh" "$PROJECT_NAME" >&2; then
    echo "" >&2
    echo "ERROR: Spec validation failed — fix errors before running oneshot" >&2
    exit 1
fi
echo "" >&2

# --- Detect build mode ---
GIT_REPO=$(get_metadata "git_repo")
FEATURE_BRANCH=""
ENV_FILE="$PROJECT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    FEATURE_BRANCH=$(grep "^BUILD_FEATURE_BRANCH_NAME=" "$ENV_FILE" 2>/dev/null | head -1 | sed 's/^BUILD_FEATURE_BRANCH_NAME=//' | tr -d '\r' || true)
fi

PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
TARGET_DIR="$PROJECTS_DIR/$PROJECT_NAME"

GIT_MODE=false
if [ -n "$GIT_REPO" ] && [[ "$GIT_REPO" == *"/"* ]] && [ -n "$FEATURE_BRANCH" ]; then
    GIT_MODE=true
fi

# --- Check for uncommitted changes in spec directory ---
cd "$REPO_DIR"
REL_PATH="$(realpath --relative-to="$REPO_DIR" "$PROJECT_DIR" 2>/dev/null || echo "$PROJECT_NAME")"
if [ -n "$(git status --porcelain -- "$REL_PATH/" 2>/dev/null || true)" ]; then
    echo "WARNING: Uncommitted changes in $PROJECT_NAME/. Commit before running oneshot for a clean tag." >&2
    echo "         Proceeding anyway — tag will point to current HEAD." >&2
    echo "" >&2
fi

# --- Numbered ticket files belong to iterate, not oneshot ---
NUMBERED_FILES=$(find "$PROJECT_DIR" -maxdepth 1 \( -name '*-[0-9][0-9][0-9]-*.md' -o -name '*-[0-9][0-9][0-9].md' \) 2>/dev/null | head -5 || true)
if [ -n "$NUMBERED_FILES" ]; then
    echo "WARNING: Numbered ticket files found in $PROJECT_NAME/ — these are iterate territory." >&2
    echo "         Numbered files (PREFIX-NNN-*.md) are processed by iterate.sh, not oneshot.sh." >&2
    echo "         Remove or rename them before running oneshot if you want a clean build." >&2
    echo "$NUMBERED_FILES" | while read -r f; do echo "         - $(basename "$f")" >&2; done
    echo "" >&2
fi

# --- Feature Branch mode: clone/fetch project and create feature branch ---
if [ "$GIT_MODE" = true ]; then
    BASE_BRANCH=$(get_metadata "base_branch")
    echo "Feature Branch mode: $FEATURE_BRANCH" >&2
    if [ ! -d "$TARGET_DIR/.git" ]; then
        echo "  Cloning $GIT_REPO..." >&2
        git clone "$GIT_REPO" "$TARGET_DIR" --quiet
        echo "  Cloned to: $TARGET_DIR" >&2
    else
        git -C "$TARGET_DIR" fetch --quiet 2>/dev/null || true
        echo "  Fetched: $TARGET_DIR" >&2
    fi
    if [ -z "$BASE_BRANCH" ]; then
        BASE_BRANCH=$(git -C "$TARGET_DIR" symbolic-ref --short HEAD 2>/dev/null || echo "main")
    fi
    if git -C "$TARGET_DIR" rev-parse --verify "$FEATURE_BRANCH" >/dev/null 2>&1; then
        echo "  WARNING: Branch '$FEATURE_BRANCH' already exists — switching to it" >&2
        git -C "$TARGET_DIR" checkout "$FEATURE_BRANCH" --quiet
    else
        git -C "$TARGET_DIR" checkout "$BASE_BRANCH" --quiet 2>/dev/null || true
        git -C "$TARGET_DIR" checkout -b "$FEATURE_BRANCH" --quiet
        echo "  Feature Branch Created: $FEATURE_BRANCH" >&2
    fi
    echo "" >&2
    echo "  Open Claude Code in: $TARGET_DIR" >&2
    echo "  Branch: $FEATURE_BRANCH" >&2
    echo "" >&2
fi

# --- Create oneshot tag ---
if [ "$NO_TAG" = false ]; then
    TODAY=$(date '+%Y-%m-%d')
    # Find next sequence number for today
    BUILD_NUM=1
    while git tag -l "oneshot/${PROJECT_NAME}/${TODAY}.${BUILD_NUM}" | grep -q .; do
        BUILD_NUM=$((BUILD_NUM + 1))
    done

    TAG_NAME="oneshot/${PROJECT_NAME}/${TODAY}.${BUILD_NUM}"
    COMMIT_SHA=$(git rev-parse HEAD)
    COMMIT_MSG=$(git log -1 --format='%s')

    ONESHOT_MODE="build"
    if [ "$UPDATE" = true ]; then ONESHOT_MODE="update"; fi

    git tag -a "$TAG_NAME" -m "OneShot (${ONESHOT_MODE}): ${PROJECT_NAME} ${TODAY}.${BUILD_NUM}
Commit: ${COMMIT_SHA}
Message: ${COMMIT_MSG}
Run: $(date '+%Y-%m-%d %H:%M:%S')"

    echo "OneShot (${ONESHOT_MODE}): $TAG_NAME → $(git rev-parse --short HEAD)" >&2

    # Record prototype build tag, commit, and directory in .env
    {
        grep -v "^PROTOTYPE_BUILD_TAG=\|^PROTOTYPE_BUILD_COMMIT=\|^PROTOTYPE_DIR=" "$PROJECT_DIR/.env" 2>/dev/null || true
        echo "PROTOTYPE_BUILD_TAG=$TAG_NAME"
        echo "PROTOTYPE_BUILD_COMMIT=$COMMIT_SHA"
        echo "PROTOTYPE_DIR=$TARGET_DIR"
    } > "$PROJECT_DIR/.env.tmp" && mv "$PROJECT_DIR/.env.tmp" "$PROJECT_DIR/.env"
    echo "  Prototype tag: $TAG_NAME → $PROJECT_DIR/.env" >&2
    echo "" >&2

    # Append deploy log entry
    DEPLOY_LOG="$PROJECT_DIR/DEPLOY_LOG.md"
    if [ ! -f "$DEPLOY_LOG" ]; then
        echo "# Deploy Log: $PROJECT_NAME" > "$DEPLOY_LOG"
        echo "" >> "$DEPLOY_LOG"
    fi
    {
        echo "## $(date '+%Y-%m-%d %H:%M') — oneshot ($ONESHOT_MODE)"
        echo "- Tag:       $TAG_NAME"
        echo "- Commit:    $(git rev-parse --short HEAD)"
        echo "- Prototype: $TARGET_DIR"
        echo ""
    } >> "$DEPLOY_LOG"

    # Show diff from previous oneshot if one exists
    PREV_TAG=$(git tag -l "oneshot/${PROJECT_NAME}/*" --sort=-version:refname | head -2 | tail -1)
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

# --- Generate one-shot build prompt ---
# Include ONESHOT_BUILD_RULES.md so the AI can expand concise specs inline during implementation
CONVERT_FILE="$REPO_DIR/RulesEngine/ONESHOT_BUILD_RULES.md"

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
    BUILD_TAG_INFO="OneShot tag: \`$TAG_NAME\` (commit $(git rev-parse --short HEAD))"
fi

if [ "$UPDATE" = true ]; then
cat <<HEADER
# OneShot Prompt: $PROJECT_NAME (update)

You are UPDATING **${DISPLAY_NAME:-$PROJECT_NAME}** — do not start from scratch.
Read the spec changes and apply them to the existing code in this directory.
${BUILD_TAG_INFO}

## Stack
$(for comp in "${COMPONENTS[@]}"; do echo "- $comp"; done)
- Port: $PORT

## Instructions
1. Read the CONVERSION RULES — they explain how concise specs should be interpreted
2. Read the INTEGRATION STANDARD (CLAUDE_RULES) — project structure requirements
3. Read ALL technology references — they define HOW to implement (prescriptive)
4. Read ALL specification files — they define WHAT has changed
5. Apply changes to the existing application; do not rebuild from scratch

---

HEADER
else
cat <<HEADER
# OneShot Prompt: $PROJECT_NAME

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

## Stub Policy
For any feature that is underspecified or marked [ROADMAP]:
- Implement a minimal functional stub (a real route/function returning a placeholder — not dead code)
- Add a comment: \`# TODO: [stub] <what is needed to complete this feature>\`
- After build completes, write \`STUBS.md\` at the project root listing every stub: file, line, description

---

HEADER
fi

# --- Conversion Rules ---
if [ -f "$CONVERT_FILE" ]; then
    echo "# CONVERSION RULES"
    echo ""
    emit_file "$CONVERT_FILE" "ONESHOT_BUILD_RULES.md (RulesEngine/ONESHOT_BUILD_RULES.md)"
fi

# --- CLAUDE_RULES.md ---
if [ -f "$REPO_DIR/RulesEngine/CLAUDE_RULES.md" ]; then
    echo "# PROJECT INTEGRATION STANDARD"
    echo ""
    emit_file "$REPO_DIR/RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES.md"
fi

# --- CLAUDE_PROTOTYPE.md (iteration rules for oneshot-built prototypes) ---
if [ -f "$REPO_DIR/RulesEngine/CLAUDE_PROTOTYPE.md" ]; then
    echo "# PROTOTYPE ITERATION RULES"
    echo ""
    echo "These rules MUST be injected into the prototype's AGENTS.md under an ## Iteration Rules section."
    echo "They are ONLY active when working in this prototype directory."
    echo ""
    emit_file "$REPO_DIR/RulesEngine/CLAUDE_PROTOTYPE.md" "CLAUDE_PROTOTYPE.md"
fi

# --- Additional RulesEngine .md files (drop-in) ---
for rules_file in "$REPO_DIR"/RulesEngine/*.md; do
    fname="$(basename "$rules_file")"
    case "$fname" in
        CLAUDE_RULES.md|CLAUDE_PROTOTYPE.md|ONESHOT_BUILD_RULES.md|BUSINESS_RULES.md|DOCUMENTATION_BRANDING.md) continue ;;
    esac
    emit_file "$rules_file" "Rules: $fname"
done

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

# --- Iteration artifacts (if they exist) ---
HAS_ITERATION=false
for iter_file in ACCEPTANCE_CRITERIA.md REFERENCE_GAPS.md IDEAS.md; do
    if [ -f "$PROJECT_DIR/$iter_file" ]; then
        if [ "$HAS_ITERATION" = false ]; then
            echo ""
            echo "# ITERATION FEEDBACK"
            echo ""
            echo "These files capture feedback from previous prototype iterations."
            echo "Address acceptance criteria as hard requirements. Close gaps where specified. Process ideas if time permits."
            echo ""
            HAS_ITERATION=true
        fi
        emit_file "$PROJECT_DIR/$iter_file" "Iteration: $iter_file"
    fi
done

# --- Footer ---
if [ "$UPDATE" = true ]; then
cat <<FOOTER
---

# END OF ONESHOT PROMPT

Update this project following the conversion rules, integration standard, technology references, and specification files above.
Apply spec changes to the existing codebase — do not rebuild from scratch.
All patterns in the technology references are prescriptive — use them exactly as shown.

## Session Summary Requirement
At the end of this session, print a summary of all specification files written or modified:
\`\`\`
--- Specification Updates ---
<filename>: <what changed>
\`\`\`
FOOTER
else
cat <<FOOTER
---

# END OF ONESHOT PROMPT

Build this project following the conversion rules, integration standard, technology references, and specification files above.
All patterns in the technology references are prescriptive — use them exactly as shown.
Expand concise specifications inline according to the conversion rules during implementation.

## Session Summary Requirement
At the end of this session, print a summary of all files written:
\`\`\`
--- Build Summary ---
<filename>: <what was created>
\`\`\`
FOOTER
fi
