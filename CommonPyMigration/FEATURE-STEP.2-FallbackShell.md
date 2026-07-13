# FEATURE: Fallback Shell Template

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Update RulesEngine/templates/common.sh to test for Python and defer to common.py when available, with full fallback for Python-absent environments. |
| Phase       | 2 |

## Trigger

After STEP.1 parity audit is approved. Updates `RulesEngine/templates/common.sh`.

## New common.sh Structure

```bash
#!/bin/bash
# Common functions — sourced by all bin/ scripts. Never run directly.
# When Python 3 is available, complex logic defers to common.py.
# This file remains the authoritative fallback for Python-absent environments.

SCRIPT_NAME="$(basename "$0" .sh)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# ── Python availability check ─────────────────────────────────────────────
if command -v python3 >/dev/null 2>&1; then
    _COMMON_PY_MODE=true
    # Extract identity fields via python3 for consistency
    PROJECT_NAME=$(python3 -c "
import os, sys
md = os.path.join('$PROJECT_DIR', 'METADATA.md')
for line in open(md) if os.path.exists(md) else []:
    if line.startswith('name:'):
        print(line[5:].strip()); sys.exit()
" 2>/dev/null || grep "^name:" "$PROJECT_DIR/METADATA.md" 2>/dev/null | head -1 | sed 's/^name:[[:space:]]*//')
    PORT=$(python3 -c "
import os, sys
md = os.path.join('$PROJECT_DIR', 'METADATA.md')
for line in open(md) if os.path.exists(md) else []:
    if line.startswith('port:'):
        print(line[5:].strip()); sys.exit()
" 2>/dev/null || grep "^port:" "$PROJECT_DIR/METADATA.md" 2>/dev/null | head -1 | sed 's/^port:[[:space:]]*//')
else
    _COMMON_PY_MODE=false
    # Fallback: pure bash metadata extraction
    get_metadata() { grep "^${1}:" "$PROJECT_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//"; }
    PROJECT_NAME="$(get_metadata "name")"
    PORT="$(get_metadata "port")"
    DISPLAY_NAME="$(get_metadata "display_name")"
fi

# ── Remainder: venv, env loading, logging, signals ────────────────────────
# (identical to existing common.sh — Python mode uses same shell vars)
if [ -d "$PROJECT_DIR/.venv" ]; then
    source "$PROJECT_DIR/.venv/bin/activate" 2>/dev/null || true
elif [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate" 2>/dev/null || true
fi
PROJECTS_DIR="$(dirname "$PROJECT_DIR")"
[ -f "$PROJECTS_DIR/.secrets" ] && set -a && source "$PROJECTS_DIR/.secrets" && set +a
[ -f "$PROJECT_DIR/.env" ] && set -a && source "$PROJECT_DIR/.env" && set +a

mkdir -p logs
LOG_FILE="logs/${SCRIPT_NAME}_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

_on_exit() { local c=$?; [ $c -eq 0 ] && echo "[$PROJECT_NAME] EXIT - OK" || echo "[$PROJECT_NAME] EXIT - ERROR (code=$c)"; }
trap '_on_exit' EXIT
trap 'exit 0' SIGTERM SIGINT
echo "[$PROJECT_NAME] Starting: $SCRIPT_NAME"

_game_port() { echo "${GAME_PORT:-$(cat ~/.game_port 2>/dev/null || echo 5000)}"; }
heartbeat() { ... }  # unchanged
log_event()  { ... }  # unchanged

# ── Python exec helper ─────────────────────────────────────────────────────
# Call from any .sh script that has a .py equivalent:
#   exec_if_python "$@"
exec_if_python() {
    local py="${SCRIPT_DIR}/${SCRIPT_NAME}.py"
    if [ "$_COMMON_PY_MODE" = true ] && [ -f "$py" ]; then
        exec python3 "$py" "$@"
    fi
}
```

## Script Usage Pattern After Migration

Scripts that have a `.py` equivalent add one line after sourcing:
```bash
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
exec_if_python "$@"
# fallback bash logic below...
```

Scripts that are pure drivers (no `.py` needed) just source `common.sh` normally.

## common.sh Demarking Comment

Add at the top of `common.sh`:
```bash
# NOTE: This file is the Python-absent fallback.
# In environments with Python 3, common.py handles OperationContext.
# Do not add computational logic here — keep it a driver only.
```

## Success Criteria

- New template deployed to `RulesEngine/templates/common.sh`.
- A test project using the new template runs correctly in both Python-present and Python-absent mode.
- `exec_if_python` correctly delegates to `common.py` when `python3` is on the PATH.
- Existing scripts that do NOT have a `.py` equivalent are unaffected.

## Open Questions

- Should `_COMMON_PY_MODE` be exported so child processes can see it?
- Is the inline Python3 metadata extraction in the fallback block too fragile? Alternative: always use `grep` for METADATA parsing even in Python mode, and let `common.py` be imported only by full Python scripts.
