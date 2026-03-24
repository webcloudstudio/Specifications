#!/bin/bash
# CommandCenter Operation
# Name: Project Update
# Category: maintenance
#
# Update a promoted code project with the latest CLAUDE_RULES and templates.
# Injects CLAUDE_RULES.md, copies template files, updates METADATA.md defaults.
# Project must already be set up (CLAUDE_RULES_START marker required).
#
# Usage:
#   bash ProjectUpdate.sh <project>            # project name under projects/
#   bash ProjectUpdate.sh /abs/path/project    # absolute path
#   bash ProjectUpdate.sh <project> --dry-run  # preview without writing
#
# Arguments:
#   $1        Project name or absolute path (required)
#   --dry-run Show what would change without writing any files
#
# Exit codes:
#   0  Success
#   1  Project not found or not set up

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${1:-}" ]; then
    echo "Usage: bash ProjectUpdate.sh <project> [--dry-run]" >&2
    echo "  <project>  Project name under ../projects/, or absolute path" >&2
    exit 1
fi

exec python3 "$SCRIPT_DIR/project_manager.py" update "$@"
