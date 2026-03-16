#!/bin/bash
# Validate a single project against CLAUDE_RULES compliance standards.
# Wraps verify.py with auto-detected projects directory.
#
# Usage: bash bin/validate_project.sh <project-name> [verify.py options]
#   e.g. bash bin/validate_project.sh GAME
#        bash bin/validate_project.sh GAME --verbose

set -euo pipefail
SPEC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="$(dirname "$SPEC_DIR")"

exec python3 "$SPEC_DIR/bin/validate_project.py" \
    --projects "$PROJECTS_DIR" \
    --project "${1:?Usage: validate_project.sh <project-name>}" \
    "${@:2}"
