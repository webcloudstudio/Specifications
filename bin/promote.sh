#!/bin/bash
# CommandCenter Operation
# Name: Promote
# Category: maintenance
# Promotes a _Build prototype to the project directory and commits.
# Usage: bash bin/promote.sh <project-name> [--dry-run]
#   <project-name>  Spec name (METADATA.md must have git_repo: set and type: oneshot)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${1:-}" ]; then
    echo "Usage: bash bin/promote.sh <project-name> [--dry-run]" >&2
    exit 1
fi

exec python3 "$SCRIPT_DIR/project_manager.py" promote "$@"
