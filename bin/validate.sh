#!/bin/bash
# CommandCenter Operation
# Name: Validate Spec
# Category: maintenance

# Validates a specification directory inside this repo for completeness and correctness.
#
# Usage:
#   bash bin/validate.sh <project-name>           # name of a spec dir in this repo
#   bash bin/validate.sh <project-name> --verbose
#
# Arguments:
#   $1        Spec directory name (required — must exist inside this repo)
#   --verbose Show passing checks too (default: errors and warnings only)
#
# Exit codes:
#   0  All checks pass
#   1  One or more errors (spec is not ready to convert/build)
#
# Checks:
#   - Required files exist (METADATA.md, README.md, ARCHITECTURE.md)
#   - METADATA.md has required fields (name, display_name, short_description, status)
#   - Naming conventions (SCREEN-*, FEATURE-*, FUNCTIONALITY.md, UI-GENERAL.md allowed)
#   - Open Questions section exists in applicable files (not README, METADATA)
#   - Stack files exist in RulesEngine/stack/ if stack: is declared
#   - No example template files left (SCREEN-Example.md, FEATURE-Example.md)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULES_DIR="$REPO_DIR/RulesEngine"

VERBOSE=false
POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --verbose) VERBOSE=true ;;
        --*)       ;;  # ignore unknown flags
        *)         [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/validate.sh <spec-name> [--verbose]" >&2
    exit 1
fi

PROJECT_DIR="$REPO_DIR/$POSITIONAL"
PROJECT_NAME="$POSITIONAL"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Spec directory not found: $PROJECT_DIR" >&2
    exit 1
fi

ERRORS=0
WARNINGS=0

pass() {
    if [ "$VERBOSE" = true ]; then
        echo "  PASS  $1"
    fi
}

warn() {
    echo "  WARN  $1"
    WARNINGS=$((WARNINGS + 1))
}

fail() {
    echo "  FAIL  $1"
    ERRORS=$((ERRORS + 1))
}

echo "Validating: $PROJECT_NAME ($PROJECT_DIR)"
echo ""

# --- Required files ---
echo "Required files:"
for required in METADATA.md README.md ARCHITECTURE.md; do
    if [ -f "$PROJECT_DIR/$required" ]; then
        pass "$required exists"
    else
        fail "$required missing"
    fi
done
echo ""

# --- METADATA.md fields ---
echo "METADATA.md fields:"
CONF_LEVEL=0
STATUS=""
if [ -f "$PROJECT_DIR/METADATA.md" ]; then
    get_field() {
        grep "^${1}:" "$PROJECT_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r' || true
    }

    for field in name display_name short_description status; do
        val=$(get_field "$field")
        if [ -n "$val" ]; then
            pass "$field: $val"
        else
            fail "$field not set in METADATA.md"
        fi
    done

    # Status value check
    STATUS=$(get_field "status")
    if [ -n "$STATUS" ]; then
        case "$STATUS" in
            IDEA|PROTOTYPE|ACTIVE|PRODUCTION|ARCHIVED) pass "status value valid: $STATUS" ;;
            *) fail "status value invalid: $STATUS (expected IDEA|PROTOTYPE|ACTIVE|PRODUCTION|ARCHIVED)" ;;
        esac
    fi

    # --- Conformity level enforcement ---
    case "${STATUS:-}" in
        IDEA)       CONF_LEVEL=0 ;;
        PROTOTYPE)  CONF_LEVEL=1 ;;
        ACTIVE)     CONF_LEVEL=2 ;;
        PRODUCTION) CONF_LEVEL=3 ;;
        ARCHIVED)   CONF_LEVEL=-1 ;;
        *)          CONF_LEVEL=0 ;;
    esac

    # Stack file check (optional field)
    STACK=$(get_field "stack")
    if [ -n "$STACK" ]; then
        IFS='/' read -ra COMPONENTS <<< "$STACK"
        for comp in "${COMPONENTS[@]}"; do
            comp_lower="$(echo "$comp" | tr -d ' ' | tr '[:upper:]' '[:lower:]')"
            stack_file="$RULES_DIR/stack/${comp_lower}.md"
            if [ -f "$stack_file" ]; then
                pass "stack file exists: RulesEngine/stack/${comp_lower}.md"
            else
                warn "stack file missing: RulesEngine/stack/${comp_lower}.md (declared in stack: $STACK)"
            fi
        done
    fi

    # --- Build configuration (oneshot projects) ---
    TYPE=$(get_field "type")
    if [ "${TYPE:-}" = "oneshot" ]; then
        echo ""
        echo "Build configuration (type: oneshot):"
        FEATURE_BRANCH=""
        if [ -f "$PROJECT_DIR/.env" ]; then
            FEATURE_BRANCH=$(grep "^BUILD_FEATURE_BRANCH_NAME=" "$PROJECT_DIR/.env" 2>/dev/null | head -1 | sed 's/^BUILD_FEATURE_BRANCH_NAME=//' | tr -d '\r' || true)
        fi
        if [ -n "$FEATURE_BRANCH" ]; then
            pass "BUILD_FEATURE_BRANCH_NAME: $FEATURE_BRANCH"
        else
            fail "BUILD_FEATURE_BRANCH_NAME missing — add to $PROJECT_DIR/.env:
      BUILD_FEATURE_BRANCH_NAME=feature/my-feature-name"
        fi
    fi
fi
echo ""

# --- Conformity level announcement ---
echo "Conformity level:"
if [ "${CONF_LEVEL}" -eq -1 ]; then
    echo "  INFO  status: ARCHIVED — no enforcement"
else
    echo "  INFO  conformity level: ${STATUS:-UNKNOWN} (${CONF_LEVEL})"
fi

# PROTOTYPE+ checks
if [ "${CONF_LEVEL}" -ge 1 ]; then
    if [ -f "$PROJECT_DIR/AGENTS.md" ]; then
        pass "AGENTS.md exists (required at PROTOTYPE+)"
    else
        warn "AGENTS.md missing (expected at PROTOTYPE+)"
    fi
fi
echo ""

# --- Naming conventions ---
echo "Naming conventions:"
BAD_NAMES=0
for f in "$PROJECT_DIR"/*.md; do
    fname=$(basename "$f")
    case "$fname" in
        METADATA.md|README.md|INTENT.md|ARCHITECTURE.md|DATABASE.md|UI.md|FUNCTIONALITY.md|UI-GENERAL.md) ;;
        SCREEN-*.md) pass "$fname (screen)" ;;
        FEATURE-*.md) pass "$fname (feature)" ;;
        *)
            warn "Unexpected file name: $fname (expected SCREEN-* or FEATURE-* prefix for spec files)"
            BAD_NAMES=$((BAD_NAMES + 1))
            ;;
    esac
done
if [ "$BAD_NAMES" -eq 0 ]; then
    pass "All file names follow conventions"
fi
echo ""

# --- Template leftovers ---
echo "Template cleanup:"
if [ -f "$PROJECT_DIR/SCREEN-Example.md" ]; then
    warn "SCREEN-Example.md still exists — rename or delete"
fi
if [ -f "$PROJECT_DIR/FEATURE-Example.md" ]; then
    warn "FEATURE-Example.md still exists — rename or delete"
fi
if [ ! -f "$PROJECT_DIR/SCREEN-Example.md" ] && [ ! -f "$PROJECT_DIR/FEATURE-Example.md" ]; then
    pass "No template example files remaining"
fi
echo ""

# --- Open Questions sections ---
echo "Open Questions sections:"
for f in "$PROJECT_DIR"/*.md; do
    fname=$(basename "$f")
    # These files don't need Open Questions
    case "$fname" in
        METADATA.md|README.md|INTENT.md) continue ;;
    esac
    if grep -q '## Open Questions' "$f" 2>/dev/null; then
        pass "$fname has Open Questions"
    else
        warn "$fname missing ## Open Questions section"
    fi
done
echo ""

# --- Summary ---
echo "─────────────────────────────"
if [ "$ERRORS" -gt 0 ]; then
    echo "RESULT: FAIL ($ERRORS errors, $WARNINGS warnings)"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo "RESULT: PASS with warnings ($WARNINGS warnings)"
    exit 0
else
    echo "RESULT: PASS"
    exit 0
fi
