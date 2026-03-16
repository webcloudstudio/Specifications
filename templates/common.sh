#!/bin/bash
# Common functions — sourced by all bin/ scripts. Never run directly.
# Provides: SCRIPT_NAME, PROJECT_DIR, PROJECT_NAME, PORT, DISPLAY_NAME,
#           venv activation, env loading, timestamped logging, SIGTERM trap.

SCRIPT_NAME="$(basename "$0" .sh)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

get_metadata() { grep "^${1}:" "$PROJECT_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//"; }
PROJECT_NAME="$(get_metadata "name")"
PORT="$(get_metadata "port")"
DISPLAY_NAME="$(get_metadata "display_name")"

[ -d "$PROJECT_DIR/venv" ] && source "$PROJECT_DIR/venv/bin/activate" 2>/dev/null
PROJECTS_DIR="$(dirname "$PROJECT_DIR")"
[ -f "$PROJECTS_DIR/.secrets" ] && set -a && source "$PROJECTS_DIR/.secrets" && set +a
[ -f "$PROJECT_DIR/.env" ] && set -a && source "$PROJECT_DIR/.env" && set +a

mkdir -p logs
LOG_FILE="logs/${PROJECT_NAME}_${SCRIPT_NAME}_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

trap 'echo "[$PROJECT_NAME] Stopped: $SCRIPT_NAME"; exit 0' SIGTERM SIGINT
echo "[$PROJECT_NAME] Starting: $SCRIPT_NAME"
