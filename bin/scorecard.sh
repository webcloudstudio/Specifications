#!/bin/bash
# CommandCenter Operation
# Name: Scorecard
# Category: maintenance
# Args: Spec
# Rules: RulesEngine/BUSINESS_RULES.md

# Generates SCORECARD.md — a comprehensive project dashboard comparing the
# built prototype against its specification files. Computes deterministic
# metrics across six dimensions, runs tests if available, and flags demerits.
#
# Output is structured markdown that other scripts can parse (grep sections,
# read the Summary table). Multiple programs can trigger a regeneration.
#
# Usage:
#   bash bin/scorecard.sh <spec-name>
#   bash bin/scorecard.sh <spec-name> --target /path/to/prototype
#   bash bin/scorecard.sh <spec-name> --run-tests
#   bash bin/scorecard.sh <spec-name> --verbose
#
# Reads:  Specifications/<spec>/*.md, prototype source, SPEC_SCORECARD.md
# Writes: SCORECARD.md in the specification directory (or --target)
#
# Exit codes:
#   0  Scorecard generated
#   1  Missing spec directory or prototype

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERBOSE=false
RUN_TESTS=false
TARGET_DIR=""
POSITIONAL=""

for arg in "$@"; do
    case "$arg" in
        --verbose)    VERBOSE=true ;;
        --run-tests)  RUN_TESTS=true ;;
        --target=*)   TARGET_DIR="${arg#--target=}" ;;
        --*)          ;;
        *)            [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/scorecard.sh <spec-name> [--target=DIR] [--run-tests] [--verbose]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"

# --- Locate prototype directory ---
if [ -n "$TARGET_DIR" ]; then
    PROTO_DIR="$TARGET_DIR"
elif [ -d "$PROJECTS_DIR/${PROJECT_NAME}_prototype" ]; then
    PROTO_DIR="$PROJECTS_DIR/${PROJECT_NAME}_prototype"
else
    PROTO_DIR="$PROJECTS_DIR/$PROJECT_NAME"
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Specification directory not found: $SPEC_DIR" >&2
    exit 1
fi

PROTO_EXISTS=true
if [ ! -d "$PROTO_DIR" ]; then
    PROTO_EXISTS=false
    echo "WARNING: Prototype directory not found: $PROTO_DIR" >&2
    echo "  Scorecard will include specification metrics only." >&2
fi

# --- Metadata helpers ---
get_metadata() {
    grep "^${1}:" "$SPEC_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r' || true
}

DISPLAY_NAME=$(get_metadata "display_name")
SHORT_DESC=$(get_metadata "short_description")
STATUS=$(get_metadata "status")
STACK=$(get_metadata "stack")
GIT_REPO=$(get_metadata "git_repo")
PORT=$(get_metadata "port")
HEALTH_PATH=$(get_metadata "health")

# --- Section counters ---
# Each section tracks its own pass/fail for per-section percentages
SEC_PASS=0; SEC_FAIL=0; SEC_WARN=0
TOT_PASS=0; TOT_FAIL=0; TOT_WARN=0; TOT_TOTAL=0
DEMERITS=""
DEMERIT_COUNT=0

section_reset() { SEC_PASS=0; SEC_FAIL=0; SEC_WARN=0; }

section_pct() {
    local total=$((SEC_PASS + SEC_FAIL + SEC_WARN))
    if [ "$total" -eq 0 ]; then echo "0"; return; fi
    echo $((SEC_PASS * 100 / total))
}

check() {
    local status="$1"
    local label="$2"
    TOT_TOTAL=$((TOT_TOTAL + 1))
    if [ "$status" = "PASS" ]; then
        SEC_PASS=$((SEC_PASS + 1)); TOT_PASS=$((TOT_PASS + 1))
        echo "- [x] $label"
    elif [ "$status" = "WARN" ]; then
        SEC_WARN=$((SEC_WARN + 1)); TOT_WARN=$((TOT_WARN + 1))
        echo "- [ ] $label *(warning)*"
    else
        SEC_FAIL=$((SEC_FAIL + 1)); TOT_FAIL=$((TOT_FAIL + 1))
        echo "- [ ] $label"
    fi
}

add_demerit() {
    local points="$1"
    local reason="$2"
    DEMERITS="${DEMERITS}- **-${points} pts:** ${reason}\n"
    DEMERIT_COUNT=$((DEMERIT_COUNT + points))
}

# --- Output location ---
if [ -n "$TARGET_DIR" ]; then
    OUTPUT_DIR="$TARGET_DIR"
else
    OUTPUT_DIR="$SPEC_DIR"
fi
OUTPUT="$OUTPUT_DIR/SCORECARD.md"

# --- Collect section scores for dashboard ---
declare -A SECTION_SCORES

# Buffer sections to a temp file, then assemble with summary at top
SECTIONS_TMP=$(mktemp)
trap 'rm -f "$SECTIONS_TMP"' EXIT

# =====================================================================
# Generate sections into temp file
# =====================================================================
{

    # =================================================================
    # 1. SPECIFICATION COMPLETENESS
    # =================================================================
    section_reset
    echo "---"
    echo ""
    echo "## Specification Completeness"
    echo ""

    # Required files for any project
    for req in METADATA.md README.md ARCHITECTURE.md FUNCTIONALITY.md INTENT.md; do
        if [ -f "$SPEC_DIR/$req" ]; then
            # Check for template placeholders
            if grep -q '__PROJECT_NAME__\|__PROJECT_SLUG__\|__SHORT_DESCRIPTION__' "$SPEC_DIR/$req" 2>/dev/null; then
                check "WARN" "$req exists but contains template placeholders"
            else
                check "PASS" "$req"
            fi
        else
            check "FAIL" "$req missing"
        fi
    done

    # Conditional files
    if echo "$STACK" | grep -qi 'sqlite\|postgres\|mysql\|database' 2>/dev/null; then
        if [ -f "$SPEC_DIR/DATABASE.md" ]; then
            check "PASS" "DATABASE.md"
        else
            check "FAIL" "DATABASE.md missing (stack declares database)"
        fi
    fi

    if echo "$STACK" | grep -qi 'bootstrap\|react\|vue\|ui\|html' 2>/dev/null; then
        if [ -f "$SPEC_DIR/UI-GENERAL.md" ]; then
            check "PASS" "UI-GENERAL.md"
        else
            check "FAIL" "UI-GENERAL.md missing (stack declares UI)"
        fi
    fi

    # Screen and feature coverage
    SCREEN_COUNT=$(find "$SPEC_DIR" -maxdepth 1 -name 'SCREEN-*.md' 2>/dev/null | wc -l)
    FEATURE_COUNT=$(find "$SPEC_DIR" -maxdepth 1 -name 'FEATURE-*.md' 2>/dev/null | wc -l)
    if [ "$SCREEN_COUNT" -gt 0 ]; then
        check "PASS" "$SCREEN_COUNT screen specification(s)"
    else
        check "WARN" "No SCREEN-*.md files"
    fi
    if [ "$FEATURE_COUNT" -gt 0 ]; then
        check "PASS" "$FEATURE_COUNT feature specification(s)"
    else
        check "WARN" "No FEATURE-*.md files"
    fi

    # REFERENCE_GAPS.md
    if [ -f "$SPEC_DIR/REFERENCE_GAPS.md" ]; then
        check "PASS" "REFERENCE_GAPS.md"
    else
        check "WARN" "REFERENCE_GAPS.md missing — run spec_iterate.sh"
        add_demerit 3 "No REFERENCE_GAPS.md — specification gap tracking not established"
    fi

    # ACCEPTANCE_CRITERIA.md
    if [ -f "$SPEC_DIR/ACCEPTANCE_CRITERIA.md" ]; then
        check "PASS" "ACCEPTANCE_CRITERIA.md"
    else
        check "WARN" "ACCEPTANCE_CRITERIA.md missing"
        add_demerit 3 "No ACCEPTANCE_CRITERIA.md — acceptance criteria not defined"
    fi

    echo ""
    SECTION_SCORES[spec_completeness]=$(section_pct)

    # =================================================================
    # 2. ROUTE COVERAGE
    # =================================================================
    section_reset
    echo "---"
    echo ""
    echo "## Route Coverage"
    echo ""

    if [ "$PROTO_EXISTS" = true ]; then
        # Find the main routes file
        ROUTES_FILE=""
        for candidate in "$PROTO_DIR/routes.py" "$PROTO_DIR/app.py" "$PROTO_DIR/main.py"; do
            if [ -f "$candidate" ]; then
                ROUTES_FILE="$candidate"
                break
            fi
        done

        if [ -n "$ROUTES_FILE" ]; then
            # Extract specified routes from SCREEN-*.md files
            # Supports two formats:
            #   1. Inline: Route: `/path`
            #   2. Section: ## Route\n```\nGET /path\n```
            for screen_file in "$SPEC_DIR"/SCREEN-*.md; do
                [ -f "$screen_file" ] || continue
                screen_name="$(basename "$screen_file" .md)"

                # Try inline format first
                route=$(grep -oP '(?<=Route:\s)`[^`]+`' "$screen_file" 2>/dev/null | head -1 | tr -d '`' || true)

                # Try ## Route section format (GET /path or POST /path in code block)
                if [ -z "$route" ]; then
                    route=$(tr -d '\r' < "$screen_file" \
                        | awk '/^## Route/{found=1; next} found && /^```/{toggle=!toggle; next} found && toggle{print; exit}' \
                        | grep -oP '(?:GET|POST|PUT|DELETE|PATCH)\s+\K/[^\s?]*' | head -1 || true)
                fi

                if [ -n "$route" ]; then
                    if grep -q "$route" "$ROUTES_FILE" 2>/dev/null; then
                        check "PASS" "$screen_name: \`$route\`"
                    else
                        check "FAIL" "$screen_name: \`$route\` NOT FOUND"
                    fi
                fi
            done

            # API routes from FUNCTIONALITY.md
            if [ -f "$SPEC_DIR/FUNCTIONALITY.md" ]; then
                while IFS= read -r api_line; do
                    api_route=$(echo "$api_line" | awk '{print $2}')
                    if [ -n "$api_route" ]; then
                        if grep -q "$api_route" "$ROUTES_FILE" 2>/dev/null; then
                            check "PASS" "API: \`$api_route\`"
                        else
                            # Check if ROADMAP
                            if grep -B5 "$api_route" "$SPEC_DIR/FUNCTIONALITY.md" 2>/dev/null | grep -qi "ROADMAP" 2>/dev/null; then
                                check "WARN" "API: \`$api_route\` [ROADMAP]"
                            else
                                check "FAIL" "API: \`$api_route\` NOT FOUND"
                            fi
                        fi
                    fi
                done < <(grep -oP '(?:GET|POST|PUT|DELETE) /api/[a-z/_{}]+' "$SPEC_DIR/FUNCTIONALITY.md" 2>/dev/null | sort -u || true)
            fi
        else
            check "FAIL" "No routes file found (routes.py, app.py, main.py)"
        fi
    else
        echo "- *Prototype not available — skipped*"
    fi

    echo ""
    SECTION_SCORES[route_coverage]=$(section_pct)

    # =================================================================
    # 3. TEST HEALTH
    # =================================================================
    section_reset
    echo "---"
    echo ""
    echo "## Test Health"
    echo ""

    if [ "$PROTO_EXISTS" = true ]; then
        TEST_DIR_EXISTS=false
        TEST_FILE_COUNT=0
        TEST_SH_EXISTS=false
        TEST_RESULT="not run"
        TEST_OUTPUT=""

        # Check tests/ directory
        if [ -d "$PROTO_DIR/tests" ]; then
            TEST_DIR_EXISTS=true
            TEST_FILE_COUNT=$(find "$PROTO_DIR/tests" -name 'test_*.py' -o -name '*_test.py' 2>/dev/null | wc -l)
            TEST_FILE_COUNT=$(echo "$TEST_FILE_COUNT" | tr -d '[:space:]')
        fi

        # Check bin/test.sh
        if [ -f "$PROTO_DIR/bin/test.sh" ]; then
            TEST_SH_EXISTS=true
        fi

        if [ "$TEST_DIR_EXISTS" = true ]; then
            check "PASS" "tests/ directory exists"
        else
            check "FAIL" "tests/ directory missing"
            add_demerit 10 "No tests/ directory — no automated test coverage"
        fi

        if [ "$TEST_FILE_COUNT" -gt 0 ]; then
            check "PASS" "$TEST_FILE_COUNT test file(s)"
        elif [ "$TEST_DIR_EXISTS" = true ]; then
            check "FAIL" "tests/ exists but no test files"
            add_demerit 5 "Empty tests/ directory — test files not written"
        fi

        if [ "$TEST_SH_EXISTS" = true ]; then
            check "PASS" "bin/test.sh exists"
        else
            check "FAIL" "bin/test.sh missing"
            add_demerit 5 "No bin/test.sh — no standard test runner"
        fi

        # Run tests if requested and possible
        if [ "$RUN_TESTS" = true ]; then
            echo ""
            echo "### Test Execution"
            echo ""
            if [ "$TEST_SH_EXISTS" = true ]; then
                echo '```'
                if (cd "$PROTO_DIR" && bash bin/test.sh 2>&1); then
                    TEST_RESULT="pass"
                    check "PASS" "bin/test.sh exited 0"
                else
                    TEST_RESULT="fail"
                    check "FAIL" "bin/test.sh exited non-zero"
                fi | tail -30
                echo '```'
            elif [ "$TEST_FILE_COUNT" -gt 0 ]; then
                echo '```'
                if (cd "$PROTO_DIR" && python3 -m pytest tests/ -q --tb=short 2>&1); then
                    TEST_RESULT="pass"
                    check "PASS" "pytest exited 0"
                else
                    TEST_RESULT="fail"
                    check "FAIL" "pytest exited non-zero"
                fi | tail -30
                echo '```'
            else
                echo "- *No tests to run*"
                TEST_RESULT="none"
            fi
        fi
    else
        echo "- *Prototype not available — skipped*"
    fi

    echo ""
    SECTION_SCORES[test_health]=$(section_pct)

    # =================================================================
    # 4. ACCEPTANCE CRITERIA
    # =================================================================
    section_reset
    echo "---"
    echo ""
    echo "## Acceptance Criteria"
    echo ""

    AC_FILE="$SPEC_DIR/ACCEPTANCE_CRITERIA.md"
    AC_ACTIVE=0
    AC_FOLDED=0
    if [ -f "$AC_FILE" ]; then
        AC_COUNT=$(grep -c "^- " "$AC_FILE" 2>/dev/null || true)
        AC_COUNT=${AC_COUNT:-0}; AC_COUNT=$(echo "$AC_COUNT" | tr -d '[:space:]')
        FOLDED_COUNT=$(sed -n '/^## Folded/,$ p' "$AC_FILE" 2>/dev/null | grep -c "^- " 2>/dev/null || true)
        FOLDED_COUNT=${FOLDED_COUNT:-0}; FOLDED_COUNT=$(echo "$FOLDED_COUNT" | tr -d '[:space:]')
        AC_ACTIVE=$((AC_COUNT - FOLDED_COUNT))
        AC_FOLDED=$FOLDED_COUNT

        echo "| Criteria | Count |"
        echo "|----------|-------|"
        echo "| Active | $AC_ACTIVE |"
        echo "| Folded (completed) | $AC_FOLDED |"
        echo "| Total | $AC_COUNT |"
        echo ""

        if [ "$AC_ACTIVE" -gt 0 ]; then
            check "PASS" "$AC_ACTIVE active acceptance criteria defined"
        fi
        if [ "$AC_FOLDED" -gt 0 ]; then
            check "PASS" "$AC_FOLDED criteria folded (met)"
        fi

        # Check automatable criteria against prototype
        if [ "$PROTO_EXISTS" = true ]; then
            if grep -q "Windows line endings" "$AC_FILE" 2>/dev/null; then
                BAD_FILES=$(find "$PROTO_DIR/bin" -type f \( -name '*.sh' -o -name '*.py' \) -exec grep -l $'\r' {} \; 2>/dev/null | wc -l || true)
                BAD_FILES=$(echo "$BAD_FILES" | tr -d '[:space:]')
                if [ "$BAD_FILES" -eq 0 ]; then
                    check "PASS" "No Windows line endings in bin/ scripts"
                else
                    check "FAIL" "$BAD_FILES file(s) have Windows line endings"
                fi
            fi
        fi
    else
        echo "- No ACCEPTANCE_CRITERIA.md found"
    fi

    # Numbered AC tickets
    AC_TICKETS=$(find "$SPEC_DIR" -maxdepth 1 -name 'AC-*.md' 2>/dev/null | wc -l)
    AC_TICKETS=$(echo "$AC_TICKETS" | tr -d '[:space:]')
    if [ "$AC_TICKETS" -gt 0 ]; then
        echo ""
        echo "**Pending AC tickets:** $AC_TICKETS"
    fi

    echo ""
    SECTION_SCORES[acceptance]=$(section_pct)

    # =================================================================
    # 5. PROJECT STRUCTURE
    # =================================================================
    section_reset
    echo "---"
    echo ""
    echo "## Project Structure"
    echo ""

    if [ "$PROTO_EXISTS" = true ]; then
        # Required files
        for req in METADATA.md AGENTS.md CLAUDE.md; do
            if [ -f "$PROTO_DIR/$req" ]; then
                check "PASS" "$req"
            else
                check "FAIL" "$req missing"
            fi
        done

        for req in .env.sample requirements.txt; do
            if [ -f "$PROTO_DIR/$req" ]; then
                check "PASS" "$req"
            else
                check "WARN" "$req missing"
            fi
        done

        # Required dirs
        for dir in bin templates static; do
            if [ -d "$PROTO_DIR/$dir" ]; then
                check "PASS" "$dir/"
            else
                check "FAIL" "$dir/ missing"
            fi
        done

        # Standard files
        for std in bin/common.sh bin/common.py; do
            if [ -f "$PROTO_DIR/$std" ]; then
                check "PASS" "$std"
            else
                check "FAIL" "$std missing"
            fi
        done

        # CLAUDE_RULES injection
        if [ -f "$PROTO_DIR/AGENTS.md" ]; then
            if grep -q "CLAUDE_RULES_START" "$PROTO_DIR/AGENTS.md" 2>/dev/null; then
                check "PASS" "CLAUDE_RULES injected in AGENTS.md"
            else
                check "WARN" "CLAUDE_RULES not injected in AGENTS.md"
            fi
        fi

        # Health endpoint configured
        if [ -n "$HEALTH_PATH" ]; then
            check "PASS" "Health endpoint configured: $HEALTH_PATH"
        else
            check "WARN" "No health endpoint in METADATA.md"
        fi

        # Stubs remaining
        STUBS_FILE="$PROTO_DIR/STUBS.md"
        if [ -f "$STUBS_FILE" ]; then
            STUB_COUNT=$(grep -c '|.*|.*|' "$STUBS_FILE" 2>/dev/null || echo 0)
            STUB_COUNT=$((STUB_COUNT - 1))
            [ "$STUB_COUNT" -lt 0 ] && STUB_COUNT=0
            if [ "$STUB_COUNT" -eq 0 ]; then
                check "PASS" "No stubs remaining"
            else
                check "WARN" "$STUB_COUNT stubs in STUBS.md"
            fi
        else
            INLINE_STUBS=$(grep -r "TODO:.*\[stub\]" "$PROTO_DIR" --include='*.py' 2>/dev/null | wc -l || true)
            INLINE_STUBS=$(echo "$INLINE_STUBS" | tr -d '[:space:]')
            if [ "$INLINE_STUBS" -eq 0 ]; then
                check "PASS" "No stub markers in code"
            else
                check "WARN" "$INLINE_STUBS inline stub markers"
            fi
        fi
    else
        echo "- *Prototype not available — skipped*"
    fi

    echo ""
    SECTION_SCORES[structure]=$(section_pct)

    # =================================================================
    # 6. DEPLOYMENT STATUS
    # =================================================================
    section_reset
    echo "---"
    echo ""
    echo "## Deployment Status"
    echo ""

    # Git repo
    if [ -n "$GIT_REPO" ]; then
        check "PASS" "git_repo: $GIT_REPO"
    else
        check "WARN" "git_repo not set in METADATA.md"
    fi

    # Build tags
    LAST_TAG=$(cd "$REPO_DIR" && git tag -l "oneshot/${PROJECT_NAME}/*" 2>/dev/null | sort -V | tail -1 || true)
    if [ -n "$LAST_TAG" ]; then
        TAG_DATE=$(echo "$LAST_TAG" | grep -oP '\d{4}-\d{2}-\d{2}' || true)
        check "PASS" "Last build tag: \`$LAST_TAG\`"

        # Spec drift — check if spec files changed since last tag
        CHANGED_SPECS=$(cd "$REPO_DIR" && git diff --name-only "$LAST_TAG" -- "$PROJECT_NAME/" 2>/dev/null | wc -l)
        CHANGED_SPECS=$(echo "$CHANGED_SPECS" | tr -d '[:space:]')
        if [ "$CHANGED_SPECS" -gt 0 ]; then
            check "WARN" "Spec drift: $CHANGED_SPECS file(s) changed since last build"
            echo ""
            echo "**Changed since \`$LAST_TAG\`:**"
            cd "$REPO_DIR" && git diff --name-only "$LAST_TAG" -- "$PROJECT_NAME/" 2>/dev/null | while read -r f; do
                echo "  - $(basename "$f")"
            done
        else
            check "PASS" "No spec drift — specifications match last build"
        fi
    else
        check "WARN" "No build tags found"
    fi

    # Prototype .env tracking
    if [ "$PROTO_EXISTS" = true ] && [ -f "$PROTO_DIR/.env" ]; then
        SPEC_TAG_ENV=$(grep '^SPEC_TAG=' "$PROTO_DIR/.env" 2>/dev/null | cut -d= -f2 || true)
        SPEC_COMMIT_ENV=$(grep '^SPEC_COMMIT=' "$PROTO_DIR/.env" 2>/dev/null | cut -d= -f2 || true)
        if [ -n "$SPEC_TAG_ENV" ]; then
            echo ""
            echo "**Prototype tracks:** \`$SPEC_TAG_ENV\`"
            if [ -n "$LAST_TAG" ] && [ "$SPEC_TAG_ENV" != "$LAST_TAG" ]; then
                check "WARN" "Prototype .env tag (\`$SPEC_TAG_ENV\`) differs from latest (\`$LAST_TAG\`)"
            fi
        fi
    fi

    # Pending tickets (unbuilt changes)
    PATCH_TICKETS=$(find "$SPEC_DIR" -maxdepth 1 -name 'PATCH-*.md' 2>/dev/null | wc -l)
    SCREEN_TICKETS=$(find "$SPEC_DIR" -maxdepth 1 -name 'SCREEN-[0-9]*-*.md' 2>/dev/null | wc -l)
    FEATURE_TICKETS=$(find "$SPEC_DIR" -maxdepth 1 -name 'FEATURE-[0-9]*-*.md' 2>/dev/null | wc -l)
    PATCH_TICKETS=$(echo "$PATCH_TICKETS" | tr -d '[:space:]')
    SCREEN_TICKETS=$(echo "$SCREEN_TICKETS" | tr -d '[:space:]')
    FEATURE_TICKETS=$(echo "$FEATURE_TICKETS" | tr -d '[:space:]')
    PENDING_TICKETS=$((PATCH_TICKETS + SCREEN_TICKETS + FEATURE_TICKETS + AC_TICKETS))

    if [ "$PENDING_TICKETS" -gt 0 ]; then
        echo ""
        echo "**Pending tickets:** $PENDING_TICKETS (${PATCH_TICKETS} patch, ${SCREEN_TICKETS} screen, ${FEATURE_TICKETS} feature, ${AC_TICKETS} AC)"
    fi

    echo ""
    SECTION_SCORES[deployment]=$(section_pct)

    # =================================================================
    # 7. REFERENCE GAPS
    # =================================================================
    echo "---"
    echo ""
    echo "## Reference Gaps"
    echo ""

    GAPS_FILE="$SPEC_DIR/REFERENCE_GAPS.md"
    GAPS_OPEN=0
    GAPS_CLOSED=0
    GAPS_TOTAL=0
    GAPS_PCT=0
    if [ -f "$GAPS_FILE" ]; then
        GAPS_OPEN=$(grep -c '^\- \[ \]' "$GAPS_FILE" 2>/dev/null || true)
        GAPS_OPEN=${GAPS_OPEN:-0}; GAPS_OPEN=$(echo "$GAPS_OPEN" | tr -d '[:space:]')
        GAPS_CLOSED=$(grep -c '^\- \[x\]' "$GAPS_FILE" 2>/dev/null || true)
        GAPS_CLOSED=${GAPS_CLOSED:-0}; GAPS_CLOSED=$(echo "$GAPS_CLOSED" | tr -d '[:space:]')
        GAPS_TOTAL=$((GAPS_OPEN + GAPS_CLOSED))

        if [ "$GAPS_TOTAL" -gt 0 ]; then
            GAPS_PCT=$((GAPS_CLOSED * 100 / GAPS_TOTAL))
        fi

        echo "| Priority | Open | Closed | Total |"
        echo "|----------|------|--------|-------|"
        for p in P0 P1 P2 P3; do
            P_OPEN=$(grep '^\- \[ \]' "$GAPS_FILE" 2>/dev/null | grep -c "$p" 2>/dev/null || true)
            P_OPEN=${P_OPEN:-0}; P_OPEN=$(echo "$P_OPEN" | tr -d '[:space:]')
            P_CLOSED=$(grep '^\- \[x\]' "$GAPS_FILE" 2>/dev/null | grep -c "$p" 2>/dev/null || true)
            P_CLOSED=${P_CLOSED:-0}; P_CLOSED=$(echo "$P_CLOSED" | tr -d '[:space:]')
            P_TOTAL=$((P_OPEN + P_CLOSED))
            if [ "$P_TOTAL" -gt 0 ]; then
                echo "| $p | $P_OPEN | $P_CLOSED | $P_TOTAL |"
            fi
        done
        # P4+ lumped
        P4_OPEN=$(grep '^\- \[ \]' "$GAPS_FILE" 2>/dev/null | grep -cE 'P[4-9]|P10' 2>/dev/null || true)
        P4_OPEN=${P4_OPEN:-0}; P4_OPEN=$(echo "$P4_OPEN" | tr -d '[:space:]')
        P4_CLOSED=$(grep '^\- \[x\]' "$GAPS_FILE" 2>/dev/null | grep -cE 'P[4-9]|P10' 2>/dev/null || true)
        P4_CLOSED=${P4_CLOSED:-0}; P4_CLOSED=$(echo "$P4_CLOSED" | tr -d '[:space:]')
        P4_TOTAL=$((P4_OPEN + P4_CLOSED))
        if [ "$P4_TOTAL" -gt 0 ]; then
            echo "| P4+ | $P4_OPEN | $P4_CLOSED | $P4_TOTAL |"
        fi
        echo "| **Total** | **$GAPS_OPEN** | **$GAPS_CLOSED** | **$GAPS_TOTAL** |"
        echo ""
        echo "**Gap closure: ${GAPS_PCT}%**"
    else
        echo "- No REFERENCE_GAPS.md — run \`bash bin/spec_iterate.sh $PROJECT_NAME\`"
    fi

    echo ""

    # =================================================================
    # 8. SPEC QUALITY (from SPEC_SCORECARD.md if available)
    # =================================================================
    echo "---"
    echo ""
    echo "## Specification Quality"
    echo ""

    SPEC_SC="$SPEC_DIR/SPEC_SCORECARD.md"
    SPEC_QUALITY_SCORE=""
    if [ -f "$SPEC_SC" ]; then
        # Extract overall score
        SPEC_QUALITY_SCORE=$(grep -i '^\| \*\*Overall\*\*' "$SPEC_SC" 2>/dev/null \
            | grep -oP '\d+\.?\d*/10' 2>/dev/null | head -1 || true)
        if [ -n "$SPEC_QUALITY_SCORE" ]; then
            echo "**Overall quality: $SPEC_QUALITY_SCORE** *(from SPEC_SCORECARD.md)*"
            echo ""
        fi

        # Extract dimension scores table only (header + data rows + Overall)
        if grep -q '| Dimension' "$SPEC_SC" 2>/dev/null; then
            sed -n '/^| Dimension/p' "$SPEC_SC"
            sed -n '/^|---/p' "$SPEC_SC" | head -1
            sed -n '/^| Dimension/,/^$/{ /^| Dimension/d; /^|---/d; /^$/d; p; }' "$SPEC_SC" 2>/dev/null
            echo ""
        fi

        echo ""
        echo "> Source: \`$PROJECT_NAME/SPEC_SCORECARD.md\` — regenerate with \`bash bin/spec_iterate.sh $PROJECT_NAME\`"
    else
        echo "- No SPEC_SCORECARD.md — run \`bash bin/spec_iterate.sh $PROJECT_NAME\`"
        add_demerit 2 "No SPEC_SCORECARD.md — specification quality not assessed"
    fi

    echo ""

    # =================================================================
    # 9. DEMERITS
    # =================================================================
    echo "---"
    echo ""
    echo "## Demerits"
    echo ""

    if [ -n "$DEMERITS" ]; then
        echo -e "$DEMERITS"
        echo "**Total demerits: -${DEMERIT_COUNT} pts**"
    else
        echo "None — all expected artifacts are present."
    fi

    echo ""

} > "$SECTIONS_TMP"

# =====================================================================
# Calculate scores
# =====================================================================
BASE_PCT=0
if [ "$TOT_TOTAL" -gt 0 ]; then
    BASE_PCT=$((TOT_PASS * 100 / TOT_TOTAL))
fi

DEMERIT_REDUCTION=$DEMERIT_COUNT
if [ "$DEMERIT_REDUCTION" -gt 30 ]; then DEMERIT_REDUCTION=30; fi

OVERALL=$((BASE_PCT - DEMERIT_REDUCTION))
if [ "$OVERALL" -lt 0 ]; then OVERALL=0; fi

SC_SPEC=${SECTION_SCORES[spec_completeness]:-0}
SC_ROUTE=${SECTION_SCORES[route_coverage]:-0}
SC_TEST=${SECTION_SCORES[test_health]:-0}
SC_AC=${SECTION_SCORES[acceptance]:-0}
SC_STRUCT=${SECTION_SCORES[structure]:-0}
SC_DEPLOY=${SECTION_SCORES[deployment]:-0}

# =====================================================================
# Assemble final output: header + summary + sections
# =====================================================================
{
    echo "# SCORECARD — ${DISPLAY_NAME:-$PROJECT_NAME}"
    echo ""
    echo "**Generated:** $(date '+%Y-%m-%d %H:%M')"
    echo "**Status:** ${STATUS:-unknown} | **Stack:** ${STACK:-unknown}"
    echo "**Specification:** Specifications/$PROJECT_NAME/ | **Prototype:** $(basename "$PROTO_DIR")/"
    echo ""
    echo "> Regenerate: \`bash bin/scorecard.sh $PROJECT_NAME\`"
    echo ""

    # --- Dashboard summary at top ---
    echo "## Summary"
    echo ""
    echo "| Metric | Score |"
    echo "|--------|-------|"
    echo "| **Overall Health** | **${OVERALL}%** |"
    echo "| Spec Completeness | ${SC_SPEC}% |"
    echo "| Route Coverage | ${SC_ROUTE}% |"
    echo "| Test Health | ${SC_TEST}% |"
    echo "| Acceptance Criteria | ${SC_AC}% |"
    echo "| Project Structure | ${SC_STRUCT}% |"
    echo "| Deployment Status | ${SC_DEPLOY}% |"
    if [ "$GAPS_TOTAL" -gt 0 ]; then
        echo "| Gap Closure | ${GAPS_PCT}% |"
    fi
    if [ -n "$SPEC_QUALITY_SCORE" ]; then
        echo "| Spec Quality | ${SPEC_QUALITY_SCORE} |"
    fi
    echo ""
    echo "| | Count |"
    echo "|--------|-------|"
    echo "| Checks passed | $TOT_PASS |"
    echo "| Checks failed | $TOT_FAIL |"
    echo "| Warnings | $TOT_WARN |"
    echo "| **Total checks** | **$TOT_TOTAL** |"
    echo "| Demerits | -$DEMERIT_COUNT pts |"
    echo ""

    # --- Detailed sections ---
    cat "$SECTIONS_TMP"

} > "$OUTPUT"

echo "Scorecard written to: $OUTPUT" >&2
echo "" >&2
echo "  Overall: ${OVERALL}% ($TOT_PASS/$TOT_TOTAL passing, $DEMERIT_COUNT demerit pts)" >&2
echo "  Spec: ${SC_SPEC}% | Routes: ${SC_ROUTE}% | Tests: ${SC_TEST}% | Structure: ${SC_STRUCT}%" >&2
