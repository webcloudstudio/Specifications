#!/bin/bash
# CommandCenter Operation
# Name: Update Projects
# Category: maintenance
#
# Update all set-up projects with the latest CLAUDE_RULES and templates.
# Skips projects in the idea phase (those without CLAUDE_RULES_START).
#
# Usage: bash bin/update_projects.sh [--dry-run]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/create_project.py" --update "$@"
