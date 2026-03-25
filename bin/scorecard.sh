#!/bin/bash
# CommandCenter Operation
# Name: Scorecard
# Category: maintenance
# Args: Spec

# Generates SCORECARD.md in a prototype directory by checking the built code
# against its specification files. Output is a checklist of KPIs.
#
# Usage:
#   bash bin/scorecard.sh <spec-name>
#   bash bin/scorecard.sh <spec-name> --verbose
#
# Reads: Specifications/<spec>/*.md, prototype routes.py, prototype STUBS.md, tests/
# Writes: SCORECARD.md in the prototype directory

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERBOSE=false
POSITIONAL=""
for arg in "$@"; do
    case "$arg" in
        --verbose) VERBOSE=true ;;
        --*)       ;;
        *)         [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/scorecard.sh <spec-name> [--verbose]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
PROTO_DIR="$PROJECTS_DIR/${PROJECT_NAME}_prototype"

# Fall back to non-_prototype directory if prototype doesn't exist
if [ ! -d "$PROTO_DIR" ]; then
    PROTO_DIR="$PROJECTS_DIR/$PROJECT_NAME"
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Spec directory not found: $SPEC_DIR" >&2
    exit 1
fi

if [ ! -d "$PROTO_DIR" ]; then
    echo "ERROR: Prototype directory not found: $PROTO_DIR" >&2
    exit 1
fi

# --- Counters ---
PASS=0
FAIL=0
WARN=0
TOTAL=0

check() {
    local status="$1"
    local label="$2"
    TOTAL=$((TOTAL + 1))
    if [ "$status" = "PASS" ]; then
        PASS=$((PASS + 1))
        echo "- [x] $label"
    elif [ "$status" = "WARN" ]; then
        WARN=$((WARN + 1))
        echo "- [ ] $label *(warning)*"
    else
        FAIL=$((FAIL + 1))
        echo "- [ ] $label"
    fi
}

# --- Begin output ---
OUTPUT="$PROTO_DIR/SCORECARD.md"
{
    echo "# Scorecard — ${PROJECT_NAME}_prototype"
    echo ""
    echo "**Generated:** $(date '+%Y-%m-%d %H:%M')"
    echo "**Spec directory:** Specifications/$PROJECT_NAME/"
    echo "**Prototype directory:** $(basename "$PROTO_DIR")/"
    echo "**Purpose:** Checklist of KPIs comparing built prototype against specification."
    echo ""
    echo "> Regenerate: \`bash ../Specifications/bin/scorecard.sh $PROJECT_NAME\`"
    echo ""
    echo "---"
    echo ""

    # --- Route Coverage ---
    echo "## Route Coverage"
    echo ""

    ROUTES_FILE="$PROTO_DIR/routes.py"
    if [ -f "$ROUTES_FILE" ]; then
        # Extract specified routes from SCREEN-*.md files
        for screen_file in "$SPEC_DIR"/SCREEN-*.md; do
            [ -f "$screen_file" ] || continue
            screen_name="$(basename "$screen_file" .md)"
            route=$(grep -oP '(?<=Route:\s)`[^`]+`' "$screen_file" 2>/dev/null | head -1 | tr -d '`' || true)
            if [ -n "$route" ]; then
                if grep -q "route('$route'" "$ROUTES_FILE" 2>/dev/null || grep -q "route(\"$route\"" "$ROUTES_FILE" 2>/dev/null; then
                    check "PASS" "$screen_name → \`$route\` exists"
                else
                    check "FAIL" "$screen_name → \`$route\` NOT FOUND in routes.py"
                fi
            fi
        done

        # Check FUNCTIONALITY.md API routes
        if [ -f "$SPEC_DIR/FUNCTIONALITY.md" ]; then
            for api_route in $(grep -oP '(?:GET|POST|PUT|DELETE) /api/[a-z/_{}]+' "$SPEC_DIR/FUNCTIONALITY.md" 2>/dev/null | awk '{print $2}' | sort -u); do
                # Normalize route pattern for grep
                route_pattern=$(echo "$api_route" | sed 's/{[^}]*}/<[^>]*>/g' | sed 's/\//\\\//g')
                if grep -qP "route\(['\"]${route_pattern}" "$ROUTES_FILE" 2>/dev/null || grep -q "$api_route" "$ROUTES_FILE" 2>/dev/null; then
                    check "PASS" "API: \`$api_route\` exists"
                else
                    # Check if it's a ROADMAP item
                    if grep -B5 "$api_route" "$SPEC_DIR/FUNCTIONALITY.md" 2>/dev/null | grep -qi "ROADMAP"; then
                        check "WARN" "API: \`$api_route\` [ROADMAP] — not yet required"
                    else
                        check "FAIL" "API: \`$api_route\` NOT FOUND in routes.py"
                    fi
                fi
            done
        fi
    else
        check "FAIL" "routes.py does not exist"
    fi
    echo ""

    # --- Acceptance Criteria ---
    echo "## Acceptance Criteria"
    echo ""
    AC_FILE="$SPEC_DIR/ACCEPTANCE_CRITERIA.md"
    if [ -f "$AC_FILE" ]; then
        AC_COUNT=$(grep -c "^- " "$AC_FILE" 2>/dev/null || true)
        AC_COUNT=${AC_COUNT:-0}; AC_COUNT=$(echo "$AC_COUNT" | tr -d '[:space:]')
        FOLDED_COUNT=$(sed -n '/^## Folded/,$ p' "$AC_FILE" 2>/dev/null | grep -c "^- " 2>/dev/null || true)
        FOLDED_COUNT=${FOLDED_COUNT:-0}; FOLDED_COUNT=$(echo "$FOLDED_COUNT" | tr -d '[:space:]')
        ACTIVE_COUNT=$((AC_COUNT - FOLDED_COUNT))
        echo "- $ACTIVE_COUNT active criteria, $FOLDED_COUNT folded"

        # Check specific automatable criteria
        if grep -q "MUST NOT contain Windows line endings" "$AC_FILE" 2>/dev/null; then
            BAD_FILES=$(find "$PROTO_DIR/bin" -type f \( -name '*.sh' -o -name '*.py' \) -exec grep -l $'\r' {} \; 2>/dev/null | wc -l)
            if [ "$BAD_FILES" -eq 0 ]; then
                check "PASS" "No Windows line endings in bin/ scripts"
            else
                check "FAIL" "$BAD_FILES bin/ files have Windows line endings (CR+LF)"
            fi
        fi

        if grep -q "docs/" "$AC_FILE" 2>/dev/null && grep -q "no.*doc/" "$AC_FILE" 2>/dev/null; then
            if [ -d "$PROTO_DIR/docs" ] || ! [ -d "$PROTO_DIR/doc" ]; then
                check "PASS" "Documentation uses docs/ directory"
            else
                check "FAIL" "doc/ directory exists — should be docs/ only"
            fi
        fi
    else
        echo "- No ACCEPTANCE_CRITERIA.md found"
    fi
    echo ""

    # --- Stubs ---
    echo "## Stubs Remaining"
    echo ""
    STUBS_FILE="$PROTO_DIR/STUBS.md"
    if [ -f "$STUBS_FILE" ]; then
        STUB_COUNT=$(grep -c '|.*|.*|' "$STUBS_FILE" 2>/dev/null || echo 0)
        STUB_COUNT=$((STUB_COUNT - 1))  # subtract header row
        [ "$STUB_COUNT" -lt 0 ] && STUB_COUNT=0
        if [ "$STUB_COUNT" -eq 0 ]; then
            check "PASS" "No stubs remaining"
        else
            check "WARN" "$STUB_COUNT stubs remaining in STUBS.md"
        fi
    else
        # Check for TODO: [stub] comments in code
        INLINE_STUBS=$(grep -r "TODO:.*\[stub\]" "$PROTO_DIR" --include='*.py' 2>/dev/null | wc -l)
        if [ "$INLINE_STUBS" -eq 0 ]; then
            check "PASS" "No stub comments found in code"
        else
            check "WARN" "$INLINE_STUBS inline stub comments found"
        fi
    fi
    echo ""

    # --- Tests ---
    echo "## Tests"
    echo ""
    if [ -d "$PROTO_DIR/tests" ]; then
        TEST_FILES=$(find "$PROTO_DIR/tests" -name 'test_*.py' -o -name '*_test.py' 2>/dev/null | wc -l)
        if [ "$TEST_FILES" -gt 0 ]; then
            check "PASS" "$TEST_FILES test file(s) found"
        else
            check "FAIL" "tests/ exists but no test files found"
        fi
    else
        check "FAIL" "No tests/ directory"
    fi

    if [ -f "$PROTO_DIR/bin/test.sh" ]; then
        check "PASS" "bin/test.sh exists"
    else
        check "FAIL" "bin/test.sh missing"
    fi
    echo ""

    # --- Project Structure ---
    echo "## Project Structure"
    echo ""
    for required_file in METADATA.md AGENTS.md CLAUDE.md .env.sample requirements.txt; do
        if [ -f "$PROTO_DIR/$required_file" ]; then
            check "PASS" "$required_file exists"
        else
            check "FAIL" "$required_file missing"
        fi
    done

    for required_dir in bin templates static; do
        if [ -d "$PROTO_DIR/$required_dir" ]; then
            check "PASS" "$required_dir/ directory exists"
        else
            check "FAIL" "$required_dir/ directory missing"
        fi
    done

    if [ -f "$PROTO_DIR/bin/common.sh" ]; then
        check "PASS" "bin/common.sh exists"
    else
        check "FAIL" "bin/common.sh missing"
    fi

    if [ -f "$PROTO_DIR/bin/common.py" ]; then
        check "PASS" "bin/common.py exists"
    else
        check "FAIL" "bin/common.py missing"
    fi
    echo ""

    # --- Reference Gaps ---
    echo "## Reference Gaps"
    echo ""
    GAPS_FILE="$SPEC_DIR/REFERENCE_GAPS.md"
    if [ -f "$GAPS_FILE" ]; then
        OPEN_GAPS=$(grep -c '^\- \[ \]' "$GAPS_FILE" 2>/dev/null || true)
        OPEN_GAPS=${OPEN_GAPS:-0}; OPEN_GAPS=$(echo "$OPEN_GAPS" | tr -d '[:space:]')
        CLOSED_GAPS=$(grep -c '^\- \[x\]' "$GAPS_FILE" 2>/dev/null || true)
        CLOSED_GAPS=${CLOSED_GAPS:-0}; CLOSED_GAPS=$(echo "$CLOSED_GAPS" | tr -d '[:space:]')
        TOTAL_GAPS=$((OPEN_GAPS + CLOSED_GAPS))
        if [ "$TOTAL_GAPS" -gt 0 ]; then
            PCT=$((CLOSED_GAPS * 100 / TOTAL_GAPS))
            echo "- $CLOSED_GAPS / $TOTAL_GAPS gaps closed ($PCT%)"
        fi
        # Count by priority
        for p in P0 P1 P2 P3; do
            P_OPEN=$(grep '^\- \[ \]' "$GAPS_FILE" 2>/dev/null | grep -c "$p" 2>/dev/null || true)
            P_OPEN=${P_OPEN:-0}; P_OPEN=$(echo "$P_OPEN" | tr -d '[:space:]')
            if [ "$P_OPEN" -gt 0 ]; then
                echo "- $P_OPEN open $p gaps"
            fi
        done
    else
        echo "- No REFERENCE_GAPS.md found"
    fi
    echo ""

    # --- Summary ---
    echo "---"
    echo ""
    echo "## Summary"
    echo ""
    if [ "$TOTAL" -gt 0 ]; then
        PCT=$((PASS * 100 / TOTAL))
        echo "**$PASS / $TOTAL checks passing ($PCT%)**"
    else
        echo "**No checks performed**"
    fi
    echo ""
    echo "| Status | Count |"
    echo "|--------|-------|"
    echo "| Pass | $PASS |"
    echo "| Fail | $FAIL |"
    echo "| Warning | $WARN |"
    echo "| **Total** | **$TOTAL** |"

} > "$OUTPUT"

echo "Scorecard written to: $OUTPUT" >&2
echo "" >&2
echo "Results: $PASS pass / $FAIL fail / $WARN warn (total $TOTAL)" >&2
