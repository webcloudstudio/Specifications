#!/bin/bash
# CommandCenter Operation
# Name: Test Specs
# Category: Operations

# Runs unit tests on the specification system itself.
# Verifies that templates, scripts, and global rules are intact.
#
# Usage:
#   bash bin/test.sh
#
# Arguments:
#   (none)
#
# Exit codes:
#   0  All tests pass
#   1  One or more failures

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

PASS=0
FAIL=0

assert() {
    local desc="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  PASS  $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $desc"
        FAIL=$((FAIL + 1))
    fi
}

assert_file() {
    assert "file exists: $1" test -f "$1"
}

assert_contains() {
    assert "$1 contains '$2'" grep -q "$2" "$1"
}

echo "=== Specification System Tests ==="
echo ""

# --- Rules Engine ---
echo "Rules Engine:"
assert_file "RulesEngine/CLAUDE_RULES.md"
assert_file "RulesEngine/BRANDING.md"
assert_file "RulesEngine/BUSINESS_RULES.md"
assert_file "RulesEngine/PROTOTYPE_PROCESS.md"
assert_contains "RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES_START"
assert_contains "RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES_END"
assert_contains "RulesEngine/CLAUDE_RULES.md" "do not edit directly"
assert_contains "RulesEngine/BUSINESS_RULES.md" "Conformity Levels"
assert_contains "RulesEngine/BUSINESS_RULES.md" "Rule text:"
echo ""

# --- Prompt files ---
echo "Prompt files:"
assert_file "prompts/oneshot_build_rules.md"
assert_file "prompts/oneshot_prototype_rules.md"
assert_file "prompts/oneshot_documentation.md"
assert_file "prompts/document.md"
assert_file "prompts/spec_iterate.md"
assert_file "prompts/update_reference_gaps.md"
assert_contains "prompts/oneshot_build_rules.md" "Expansion Principles"
assert_contains "prompts/oneshot_prototype_rules.md" "Prototype Iteration Rules"
assert_contains "prompts/oneshot_documentation.md" "Documentation Build Standard"
echo ""

# --- Service endpoint validation ---
echo "Service endpoints:"
for script in bin/*.sh; do
    # Extract Prompt: and Rules: declarations from CommandCenter headers
    PROMPT_DECL=$(grep '^# Prompt:' "$script" 2>/dev/null | sed 's/^# Prompt:[[:space:]]*//' || true)
    RULES_DECL=$(grep '^# Rules:' "$script" 2>/dev/null | sed 's/^# Rules:[[:space:]]*//' || true)
    if [ -n "$PROMPT_DECL" ]; then
        IFS=',' read -ra DEPS <<< "$PROMPT_DECL"
        for dep in "${DEPS[@]}"; do
            dep="$(echo "$dep" | xargs)"  # trim whitespace
            # Skip glob patterns (e.g. RulesEngine/stack/*.md)
            case "$dep" in *\**) continue ;; esac
            assert "$(basename "$script") declares $dep" test -f "$dep"
        done
    fi
    if [ -n "$RULES_DECL" ]; then
        IFS=',' read -ra DEPS <<< "$RULES_DECL"
        for dep in "${DEPS[@]}"; do
            dep="$(echo "$dep" | xargs)"
            case "$dep" in *\**) continue ;; esac
            assert "$(basename "$script") declares $dep" test -f "$dep"
        done
    fi
done
echo ""

# --- Stack files ---
echo "Stack files:"
assert_file "RulesEngine/stack/common.md"
assert_file "RulesEngine/stack/python.md"
assert_file "RulesEngine/stack/flask.md"
assert_file "RulesEngine/stack/sqlite.md"
assert_file "RulesEngine/stack/bootstrap5.md"
echo ""

# --- Spec templates ---
echo "Spec templates:"
assert_file "RulesEngine/spec_template/METADATA.md"
assert_file "RulesEngine/spec_template/README.md"
assert_file "RulesEngine/spec_template/ARCHITECTURE.md"
assert_file "RulesEngine/spec_template/DATABASE.md"
assert_file "RulesEngine/spec_template/UI.md"
assert_file "RulesEngine/spec_template/SCREEN-Example.md"
assert_file "RulesEngine/spec_template/FEATURE-Example.md"
assert_contains "RulesEngine/spec_template/METADATA.md" "__PROJECT_NAME__"
assert_contains "RulesEngine/spec_template/METADATA.md" "__PROJECT_SLUG__"
echo ""

# --- Bin scripts ---
echo "Bin scripts:"
for script in bin/setup.sh bin/validate.sh bin/convert.sh bin/oneshot.sh bin/summarize_rules.sh bin/scorecard.sh; do
    assert_file "$script"
done
# Verify CommandCenter headers
for script in bin/setup.sh bin/validate.sh bin/convert.sh bin/oneshot.sh bin/summarize_rules.sh bin/scorecard.sh; do
    assert_contains "$script" "CommandCenter Operation"
    assert_contains "$script" "# Name:"
    assert_contains "$script" "# Category:"
done
echo ""

# --- Script executability ---
echo "Script executability:"
for script in bin/setup.sh bin/validate.sh bin/convert.sh bin/oneshot.sh bin/summarize_rules.sh bin/scorecard.sh; do
    assert "$script is executable" test -x "$script"
done
echo ""

# --- Generate Claude Rules ---
echo "Generate Claude Rules:"
assert "summarize_rules.sh runs without error" bash bin/summarize_rules.sh
assert "output contains CLAUDE_RULES_START" bash -c 'bash bin/summarize_rules.sh | grep -q "CLAUDE_RULES_START"'
assert "output references BUSINESS_RULES" bash -c 'bash bin/summarize_rules.sh | grep -q "BUSINESS_RULES"'
echo ""

# --- Create + validate round-trip ---
echo "Create + validate round-trip:"
TEST_DIR="$REPO_DIR/__test_project__"
if [ -d "$TEST_DIR" ]; then
    rm -rf "$TEST_DIR"
fi

# Create a test project
bash bin/setup.sh __test_project__ > /dev/null 2>&1
assert "setup.sh creates directory" test -d "$TEST_DIR"
assert "created METADATA.md" test -f "$TEST_DIR/METADATA.md"
assert "created README.md" test -f "$TEST_DIR/README.md"
assert "created ARCHITECTURE.md" test -f "$TEST_DIR/ARCHITECTURE.md"
assert_contains "$TEST_DIR/METADATA.md" "name: __test_project__"
assert_contains "$TEST_DIR/METADATA.md" "display_name: Test Project"
assert_contains "$TEST_DIR/README.md" "Test Project"

# Validate should pass (with warnings for template placeholders)
assert "validate.sh runs without error" bash bin/validate.sh __test_project__

# Test --update mode on existing directory
assert "setup.sh --update on existing dir succeeds" bash bin/setup.sh __test_project__ --update

# Clean up
rm -rf "$TEST_DIR"
assert "cleanup succeeded" test ! -d "$TEST_DIR"
echo ""

# --- Summary ---
TOTAL=$((PASS + FAIL))
echo "─────────────────────────────"
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL ($PASS/$TOTAL passed, $FAIL failed)"
    exit 1
else
    echo "RESULT: PASS ($PASS/$TOTAL passed)"
    exit 0
fi
