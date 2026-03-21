#!/bin/bash
# CommandCenter Operation
# Name: Build
# Category: maintenance
#
# Creates a Feature Branch from the base code and generates a build prompt for an AI agent.
# Clones the project repository if it does not exist locally.
#
# Usage:
#   bash bin/build.sh <spec-name>                    # Write prompt to stdout
#   bash bin/build.sh <spec-name> > build-prompt.md  # Save to file
#   bash bin/build.sh <spec-name> --dry-run          # Preview without git operations
#
# Requires in Specifications/<spec-name>/.env:
#   BUILD_FEATURE_BRANCH_NAME=feature/my-feature-name
#
# Exit codes:
#   0  Success
#   1  Configuration error or git failure

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
BIN_DIR="$REPO_DIR/bin"

DRY_RUN=false
POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --*)       ;;
        *)         [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/build.sh <spec-name> [--dry-run]" >&2
    exit 1
fi

SPEC_DIR="$REPO_DIR/$POSITIONAL"
SPEC_NAME="$POSITIONAL"
ENV_FILE="$SPEC_DIR/.env"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Spec directory not found: $SPEC_DIR" >&2
    exit 1
fi

# --- Read spec METADATA ---
get_field() {
    grep "^${1}:" "$SPEC_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r' || true
}

GIT_REPO=$(get_field "git_repo")
BASE_BRANCH=$(get_field "base_branch")
SPEC_TYPE=$(get_field "type")

# --- Read BUILD_FEATURE_BRANCH_NAME from .env ---
FEATURE_BRANCH=""
if [ -f "$ENV_FILE" ]; then
    FEATURE_BRANCH=$(grep "^BUILD_FEATURE_BRANCH_NAME=" "$ENV_FILE" 2>/dev/null | head -1 | sed 's/^BUILD_FEATURE_BRANCH_NAME=//' | tr -d '\r' || true)
fi

if [ -z "$FEATURE_BRANCH" ]; then
    echo "" >&2
    echo "  Feature Branch Name Missing" >&2
    echo "  Add to $ENV_FILE:" >&2
    echo "    BUILD_FEATURE_BRANCH_NAME=feature/my-feature-name" >&2
    echo "" >&2
    exit 1
fi

# --- Validate git_repo ---
if [ -z "$GIT_REPO" ] || [[ "$GIT_REPO" != *"/"* ]]; then
    echo "ERROR: git_repo not set or not a valid URL in METADATA.md" >&2
    echo "       Set: git_repo: https://github.com/user/${SPEC_NAME}.git" >&2
    exit 1
fi

PROJECT_DIR="$PROJECTS_DIR/$SPEC_NAME"

echo "" >&2
echo "Build: $SPEC_NAME" >&2
echo "  Feature Branch : $FEATURE_BRANCH" >&2
echo "  Project Dir    : $PROJECT_DIR" >&2

if [ "$DRY_RUN" = true ]; then
    echo "  dry-run — no git operations will be performed" >&2
    echo "" >&2
fi

if [ "$DRY_RUN" = false ]; then
    # --- Clone or fetch project ---
    if [ ! -d "$PROJECT_DIR/.git" ]; then
        echo "" >&2
        echo "  Cloning $GIT_REPO..." >&2
        git clone "$GIT_REPO" "$PROJECT_DIR" --quiet
        echo "  Cloned to: $PROJECT_DIR" >&2
    else
        git -C "$PROJECT_DIR" fetch --quiet 2>/dev/null || true
        echo "  Fetched: $PROJECT_DIR" >&2
    fi

    # --- Detect base branch if not configured ---
    if [ -z "$BASE_BRANCH" ]; then
        BASE_BRANCH=$(git -C "$PROJECT_DIR" symbolic-ref --short HEAD 2>/dev/null || echo "main")
        echo "  Base Branch    : $BASE_BRANCH (auto-detected)" >&2
    else
        echo "  Base Branch    : $BASE_BRANCH" >&2
    fi

    # --- Create feature branch ---
    if git -C "$PROJECT_DIR" rev-parse --verify "$FEATURE_BRANCH" >/dev/null 2>&1; then
        echo "" >&2
        echo "  WARNING: Branch '$FEATURE_BRANCH' already exists — switching to it" >&2
        git -C "$PROJECT_DIR" checkout "$FEATURE_BRANCH" --quiet
    else
        git -C "$PROJECT_DIR" checkout "$BASE_BRANCH" --quiet 2>/dev/null || true
        git -C "$PROJECT_DIR" checkout -b "$FEATURE_BRANCH" --quiet
        echo "" >&2
        echo "  Feature Branch Created: $FEATURE_BRANCH" >&2
    fi
else
    if [ -z "$BASE_BRANCH" ]; then BASE_BRANCH="main (auto-detected)"; fi
    echo "  Base Branch    : $BASE_BRANCH" >&2
    echo "  Would create branch: $FEATURE_BRANCH from $BASE_BRANCH in $PROJECT_DIR" >&2
fi

echo "" >&2
echo "  Open Claude Code in: $PROJECT_DIR" >&2
echo "  Branch: $FEATURE_BRANCH" >&2
echo "" >&2

# --- Generate build prompt via oneshot.sh ---
exec bash "$BIN_DIR/oneshot.sh" "$SPEC_NAME" --no-tag
