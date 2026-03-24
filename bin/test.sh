#!/bin/bash
# CommandCenter Operation
# Name: Test Specs
# Category: maintenance

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
assert_file "RulesEngine/ONESHOT_BUILD_RULES.md"
assert_file "RulesEngine/DOCUMENTATION_BRANDING.md"
assert_file "RulesEngine/BUSINESS_RULES.md"
assert_contains "RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES_START"
assert_contains "RulesEngine/CLAUDE_RULES.md" "CLAUDE_RULES_END"
assert_contains "RulesEngine/CLAUDE_RULES.md" "do not edit directly"
assert_contains "RulesEngine/BUSINESS_RULES.md" "Conformity Levels"
assert_contains "RulesEngine/BUSINESS_RULES.md" "Rule text:"
assert_contains "RulesEngine/ONESHOT_BUILD_RULES.md" "Expansion Principles"
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
assert_file "RulesEngine/spec_template/INTENT.md"
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
for script in bin/setup.sh bin/validate.sh bin/convert.sh bin/build.sh bin/generate_prompt.sh bin/summarize_rules.sh; do
    assert_file "$script"
done
# Verify CommandCenter headers
for script in bin/setup.sh bin/validate.sh bin/convert.sh bin/build.sh bin/summarize_rules.sh; do
    assert_contains "$script" "CommandCenter Operation"
    assert_contains "$script" "# Name:"
    assert_contains "$script" "# Category:"
done
echo ""

# --- Script executability ---
echo "Script executability:"
for script in bin/setup.sh bin/validate.sh bin/convert.sh bin/build.sh bin/summarize_rules.sh; do
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
assert "created INTENT.md" test -f "$TEST_DIR/INTENT.md"
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
