#!/bin/bash
# CommandCenter Operation
# Name: Merge
# Category: maintenance
#
# Squash-merges a Feature Branch into the base branch and deletes the feature branch.
# Typically called by GAME via automation. Can be run directly with explicit args.
#
# Usage:
#   bash bin/merge.sh <spec-name>                           # read .env and METADATA
#   bash bin/merge.sh <spec-name> --feature <branch>        # override feature branch
#   bash bin/merge.sh <spec-name> --base <branch>           # override base branch
#   bash bin/merge.sh <spec-name> --dry-run                 # preview without merging
#
# Exit codes:
#   0  Success
#   1  Configuration error or git failure

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"

DRY_RUN=false
FEATURE_ARG=""
BASE_ARG=""
POSITIONAL=""
i=0
args=("$@")
while [ $i -lt ${#args[@]} ]; do
    arg="${args[$i]}"
    case "$arg" in
        --dry-run)   DRY_RUN=true ;;
        --feature)   i=$((i+1)); FEATURE_ARG="${args[$i]}" ;;
        --base)      i=$((i+1)); BASE_ARG="${args[$i]}" ;;
        --*)         ;;
        *)           [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
    i=$((i+1))
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/merge.sh <spec-name> [--feature <branch>] [--base <branch>] [--dry-run]" >&2
    exit 1
fi

SPEC_DIR="$REPO_DIR/$POSITIONAL"
SPEC_NAME="$POSITIONAL"
ENV_FILE="$SPEC_DIR/.env"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Spec directory not found: $SPEC_DIR" >&2
    exit 1
fi

get_field() {
    grep "^${1}:" "$SPEC_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r' || true
}

# --- Resolve feature branch ---
FEATURE_BRANCH="$FEATURE_ARG"
if [ -z "$FEATURE_BRANCH" ] && [ -f "$ENV_FILE" ]; then
    FEATURE_BRANCH=$(grep "^BUILD_FEATURE_BRANCH_NAME=" "$ENV_FILE" 2>/dev/null | head -1 | sed 's/^BUILD_FEATURE_BRANCH_NAME=//' | tr -d '\r' || true)
fi
if [ -z "$FEATURE_BRANCH" ]; then
    echo "ERROR: Feature branch not set. Pass --feature or set BUILD_FEATURE_BRANCH_NAME in $ENV_FILE" >&2
    exit 1
fi

# --- Resolve base branch ---
BASE_BRANCH="$BASE_ARG"
if [ -z "$BASE_BRANCH" ]; then
    BASE_BRANCH=$(get_field "base_branch")
fi

PROJECT_DIR="$PROJECTS_DIR/$SPEC_NAME"

if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "ERROR: Project directory not found or not a git repo: $PROJECT_DIR" >&2
    exit 1
fi

if [ -z "$BASE_BRANCH" ]; then
    BASE_BRANCH=$(git -C "$PROJECT_DIR" symbolic-ref --short HEAD 2>/dev/null || echo "main")
fi

# Get latest oneshot tag for commit message
ONESHOT_TAG=$(git -C "$REPO_DIR" tag -l "oneshot/${SPEC_NAME}/*" --sort=-version:refname 2>/dev/null | head -1 || true)
COMMIT_MSG="Merge: $SPEC_NAME"
if [ -n "$ONESHOT_TAG" ]; then
    COMMIT_MSG="Merge: $SPEC_NAME from $ONESHOT_TAG"
fi

echo "" >&2
echo "Merge: $SPEC_NAME" >&2
echo "  Feature Branch : $FEATURE_BRANCH" >&2
echo "  Base Branch    : $BASE_BRANCH" >&2
echo "  Project Dir    : $PROJECT_DIR" >&2
echo "  Commit message : $COMMIT_MSG" >&2
if [ "$DRY_RUN" = true ]; then
    echo "  dry-run — no git operations will be performed" >&2
    echo "" >&2
    echo "─────────────────────────────" >&2
    echo "RESULT: dry-run — would squash-merge $FEATURE_BRANCH → $BASE_BRANCH" >&2
    exit 0
fi

# --- Verify feature branch exists ---
if ! git -C "$PROJECT_DIR" rev-parse --verify "$FEATURE_BRANCH" >/dev/null 2>&1; then
    echo "ERROR: Feature branch '$FEATURE_BRANCH' not found in $PROJECT_DIR" >&2
    exit 1
fi

# --- Squash merge ---
git -C "$PROJECT_DIR" checkout "$BASE_BRANCH" --quiet
git -C "$PROJECT_DIR" merge --squash "$FEATURE_BRANCH" --quiet
git -C "$PROJECT_DIR" commit -m "$COMMIT_MSG"

# --- Delete feature branch ---
git -C "$PROJECT_DIR" branch -d "$FEATURE_BRANCH"

echo "" >&2
echo "─────────────────────────────" >&2
echo "RESULT: Merged to $BASE_BRANCH — push when ready" >&2
echo "        git -C $PROJECT_DIR push" >&2
