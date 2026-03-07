#!/bin/bash
# Validate that all specification files referenced in a project's STACK.yaml exist
# and that the project directory is complete and consistent.
#
# Usage: bash validate.sh <project-name>
#   e.g. bash validate.sh GAME

set -euo pipefail

# Get the repository root (where this script lives)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get project name from argument
PROJECT_NAME="${1:?Usage: bash validate.sh <project-name>}"
PROJECT_DIR="$REPO_DIR/$PROJECT_NAME"
STACK_FILE="$PROJECT_DIR/STACK.yaml"
ERRORS=0
WARNINGS=0

echo "=== PROJECT Specification Validator ==="
echo "Repository: $REPO_DIR"
echo "Project: $PROJECT_NAME"
echo "Directory: $PROJECT_DIR"
echo ""

# --- Check STACK.yaml exists ---
if [ ! -f "$STACK_FILE" ]; then
    echo "FAIL: STACK.yaml not found at $STACK_FILE"
    exit 1
fi
echo "OK: STACK.yaml found"

# --- Parse STACK.yaml (simple grep-based, no yq dependency) ---
get_yaml_value() {
    grep "^${1}:" "$STACK_FILE" | head -1 | sed 's/^[^:]*: *//' | tr -d '"' | tr -d "'" | tr -d '\r'
}

LANGUAGE=$(get_yaml_value "language")
FRAMEWORK=$(get_yaml_value "framework")
DATABASE=$(get_yaml_value "database")
FRONTEND=$(get_yaml_value "frontend")

echo ""
echo "Stack: language=$LANGUAGE framework=$FRAMEWORK database=$DATABASE frontend=$FRONTEND"
echo ""

# --- Validate stack/ technology files (at repo root) ---
echo "--- Technology Files (stack/) ---"

# common.md is always required
if [ -f "$REPO_DIR/stack/common.md" ]; then
    echo "  OK: stack/common.md"
else
    echo "  FAIL: stack/common.md (always required)"
    ERRORS=$((ERRORS + 1))
fi

# Check each declared technology
for TECH in "$LANGUAGE" "$FRAMEWORK" "$DATABASE" "$FRONTEND"; do
    if [ -z "$TECH" ]; then
        continue
    fi
    TECH_FILE="$REPO_DIR/stack/${TECH}.md"
    if [ -f "$TECH_FILE" ]; then
        echo "  OK: stack/${TECH}.md"
    else
        echo "  FAIL: stack/${TECH}.md (declared in STACK.yaml but file missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

# --- Validate numbered spec files (in project directory) ---
echo ""
echo "--- Specification Files ---"

# Extract spec file list from STACK.yaml
SPECS=$(grep '^\s*- [0-9]' "$STACK_FILE" | sed 's/^\s*- //' | tr -d '\r')

if [ -z "$SPECS" ]; then
    echo "  WARN: No spec files listed in STACK.yaml specs: section"
    WARNINGS=$((WARNINGS + 1))
else
    while IFS= read -r SPEC; do
        if [ -f "$PROJECT_DIR/$SPEC" ]; then
            echo "  OK: $SPEC"
        else
            echo "  FAIL: $SPEC (listed in STACK.yaml but file missing)"
            ERRORS=$((ERRORS + 1))
        fi
    done <<< "$SPECS"
fi

# --- Check for orphaned stack files (files in stack/ not referenced) ---
echo ""
echo "--- Orphan Check ---"

DECLARED_TECHS="common $LANGUAGE $FRAMEWORK $DATABASE $FRONTEND"
for STACK_MD in "$REPO_DIR"/stack/*.md; do
    if [ ! -f "$STACK_MD" ]; then
        continue
    fi
    BASENAME=$(basename "$STACK_MD" .md)
    FOUND=0
    for TECH in $DECLARED_TECHS; do
        if [ "$BASENAME" = "$TECH" ]; then
            FOUND=1
            break
        fi
    done
    if [ $FOUND -eq 0 ]; then
        echo "  INFO: stack/$BASENAME.md exists but is not referenced in STACK.yaml (available for other projects)"
    fi
done

# --- Check supporting files (at repo root) ---
echo ""
echo "--- Supporting Files (repo root) ---"

for SUPPORT_FILE in README.md SPEC_STANDARD.md; do
    if [ -f "$REPO_DIR/$SUPPORT_FILE" ]; then
        echo "  OK: $SUPPORT_FILE"
    else
        echo "  WARN: $SUPPORT_FILE missing"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# --- Summary ---
echo ""
echo "=== Results ==="
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
    echo "FAILED — fix errors above before building"
    exit 1
else
    echo "PASSED — all referenced files exist"
    exit 0
fi
