#!/bin/bash
# CommandCenter Operation
# Name: Validate Spec
# Category: maintenance

# Validates a specification directory for completeness and correctness.
#
# Usage:
#   bash bin/validate.sh <project-name>
#   bash bin/validate.sh <project-name> --verbose
#
# Arguments:
#   $1        Project name (required) — specification directory name
#   --verbose Show passing checks too (default: errors and warnings only)
#
# Exit codes:
#   0  All checks pass
#   1  One or more errors (spec is not ready to convert/build)
#
# Checks:
#   - Required files exist (METADATA.md, README.md, INTENT.md, ARCHITECTURE.md)
#   - METADATA.md has required fields (name, display_name, short_description, status)
#   - INTENT.md is not empty / still has template placeholder
#   - Naming conventions (SCREEN-*, FEATURE-* prefixes)
#   - Open Questions section exists in applicable files (not README, METADATA, INTENT)
#   - Stack files exist in GLOBAL_RULES/stack/ if stack: is declared
#   - No example template files left (SCREEN-Example.md, FEATURE-Example.md)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME="${1:?Usage: bash bin/validate.sh <project-name>}"
PROJECT_DIR="$REPO_DIR/$PROJECT_NAME"
VERBOSE=false

shift || true
for arg in "$@"; do
    case "$arg" in
        --verbose) VERBOSE=true ;;
    esac
done

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Directory not found: $PROJECT_DIR" >&2
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

echo "Validating: $PROJECT_NAME"
echo ""

# --- Required files ---
echo "Required files:"
for required in METADATA.md README.md INTENT.md ARCHITECTURE.md; do
    if [ -f "$PROJECT_DIR/$required" ]; then
        pass "$required exists"
    else
        fail "$required missing"
    fi
done
echo ""

# --- METADATA.md fields ---
echo "METADATA.md fields:"
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

    # Stack file check (optional field)
    STACK=$(get_field "stack")
    if [ -n "$STACK" ]; then
        IFS='/' read -ra COMPONENTS <<< "$STACK"
        for comp in "${COMPONENTS[@]}"; do
            comp_lower="$(echo "$comp" | tr -d ' ' | tr '[:upper:]' '[:lower:]')"
            stack_file="$REPO_DIR/GLOBAL_RULES/stack/${comp_lower}.md"
            if [ -f "$stack_file" ]; then
                pass "stack file exists: stack/${comp_lower}.md"
            else
                warn "stack file missing: stack/${comp_lower}.md (declared in stack: $STACK)"
            fi
        done
    fi
fi
echo ""

# --- INTENT.md content check ---
echo "INTENT.md content:"
if [ -f "$PROJECT_DIR/INTENT.md" ]; then
    # Check if still has template placeholder
    if grep -q '<!-- Why does this project exist' "$PROJECT_DIR/INTENT.md" 2>/dev/null; then
        warn "INTENT.md still has template placeholder — fill it in"
    else
        # Check if has meaningful content (more than just heading)
        CONTENT_LINES=$(grep -cv '^\s*$\|^#\|^<!--' "$PROJECT_DIR/INTENT.md" 2>/dev/null || echo "0")
        if [ "$CONTENT_LINES" -gt 0 ]; then
            pass "INTENT.md has content ($CONTENT_LINES lines)"
        else
            warn "INTENT.md appears empty"
        fi
    fi
fi
echo ""

# --- Naming conventions ---
echo "Naming conventions:"
BAD_NAMES=0
for f in "$PROJECT_DIR"/*.md; do
    fname=$(basename "$f")
    case "$fname" in
        METADATA.md|README.md|INTENT.md|ARCHITECTURE.md|DATABASE.md|UI.md) ;;
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
