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

# --- Global rules ---
echo "Global rules:"
assert_file "GLOBAL_RULES/CLAUDE_RULES.md"
assert_file "GLOBAL_RULES/CONVERT.md"
assert_file "GLOBAL_RULES/DOCUMENTATION_BRANDING.md"
assert_contains "GLOBAL_RULES/CLAUDE_RULES.md" "CLAUDE_RULES_START"
assert_contains "GLOBAL_RULES/CLAUDE_RULES.md" "CLAUDE_RULES_END"
assert_contains "GLOBAL_RULES/CONVERT.md" "Expansion Principles"
echo ""

# --- Stack files ---
echo "Stack files:"
assert_file "GLOBAL_RULES/stack/common.md"
assert_file "GLOBAL_RULES/stack/python.md"
assert_file "GLOBAL_RULES/stack/flask.md"
assert_file "GLOBAL_RULES/stack/sqlite.md"
assert_file "GLOBAL_RULES/stack/bootstrap5.md"
echo ""

# --- Spec templates ---
echo "Spec templates:"
assert_file "GLOBAL_RULES/spec_template/METADATA.md"
assert_file "GLOBAL_RULES/spec_template/README.md"
assert_file "GLOBAL_RULES/spec_template/INTENT.md"
assert_file "GLOBAL_RULES/spec_template/ARCHITECTURE.md"
assert_file "GLOBAL_RULES/spec_template/DATABASE.md"
assert_file "GLOBAL_RULES/spec_template/UI.md"
assert_file "GLOBAL_RULES/spec_template/SCREEN-Example.md"
assert_file "GLOBAL_RULES/spec_template/FEATURE-Example.md"
assert_contains "GLOBAL_RULES/spec_template/METADATA.md" "__PROJECT_NAME__"
assert_contains "GLOBAL_RULES/spec_template/METADATA.md" "__PROJECT_SLUG__"
echo ""

# --- Bin scripts ---
echo "Bin scripts:"
for script in bin/create_spec.sh bin/validate.sh bin/convert.sh bin/build.sh bin/generate_prompt.sh bin/rebuild_index.sh; do
    assert_file "$script"
done
# Verify CommandCenter headers
for script in bin/create_spec.sh bin/validate.sh bin/convert.sh bin/build.sh; do
    assert_contains "$script" "CommandCenter Operation"
    assert_contains "$script" "# Name:"
    assert_contains "$script" "# Category:"
done
echo ""

# --- Script executability ---
echo "Script executability:"
for script in bin/create_spec.sh bin/validate.sh bin/convert.sh bin/build.sh; do
    assert "$script is executable" test -x "$script"
done
echo ""

# --- Create + validate round-trip ---
echo "Create + validate round-trip:"
TEST_DIR="$REPO_DIR/__test_project__"
if [ -d "$TEST_DIR" ]; then
    rm -rf "$TEST_DIR"
fi

# Create a test project
bash bin/create_spec.sh __test_project__ "Test project for validation" > /dev/null 2>&1
assert "create_spec.sh creates directory" test -d "$TEST_DIR"
assert "created METADATA.md" test -f "$TEST_DIR/METADATA.md"
assert "created README.md" test -f "$TEST_DIR/README.md"
assert "created INTENT.md" test -f "$TEST_DIR/INTENT.md"
assert "created ARCHITECTURE.md" test -f "$TEST_DIR/ARCHITECTURE.md"
assert_contains "$TEST_DIR/METADATA.md" "name: __test_project__"
assert_contains "$TEST_DIR/METADATA.md" "display_name: Test Project"
assert_contains "$TEST_DIR/README.md" "Test Project"

# Validate should pass (with warnings for template placeholders)
assert "validate.sh runs without error" bash bin/validate.sh __test_project__

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
