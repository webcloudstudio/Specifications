#!/bin/bash
# CommandCenter Operation
# Name: Project Validate
# Category: Global
# Args: Project
#
# Verify a promoted code project against CLAUDE_RULES compliance criteria.
# Shows pass/fail per rule grouped by level, with a next-level preview.
#
# Usage:
#   bash bin/ProjectValidate.sh <project>          # project name under projects/
#   bash bin/ProjectValidate.sh /abs/path/project  # absolute path
#   bash bin/ProjectValidate.sh <project> --verbose
#
# Arguments:
#   $1        Project name or absolute path (required)
#   --verbose Show passing checks too (default: failures only)
#
# Exit codes:
#   0  All checks pass
#   1  One or more failures

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${1:-}" ]; then
    echo "Usage: bash bin/ProjectValidate.sh <project> [--verbose]" >&2
    echo "  <project>  Project name under ../projects/, or absolute path" >&2
    exit 1
fi

exec python3 "$SCRIPT_DIR/project_manager.py" verify "$@"
