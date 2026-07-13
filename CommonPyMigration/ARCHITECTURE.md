# ARCHITECTURE: Common.py Migration

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | How the migration tooling is structured and what files change across the workspace. |

## Overview

This is a cross-workspace refactor delivered as:
1. A parity audit (STEP.1)
2. A template update in `Prototyper/RulesEngine/templates/` (STEP.2)
3. A migration script `Prototyper/UpdateScripts/v1.01.sh` (STEP.3)
4. Updates to `bin/ProjectValidate.sh` (STEP.4)

## Files Changed / Created

### In Prototyper/

| File | Change |
|------|--------|
| `RulesEngine/templates/common.sh` | Updated: add Python fallback block at top |
| `bin/ProjectValidate.sh` | Updated: add `--summary` mode, `.sh` classification |
| `bin/ProjectUpdate.sh` | Updated: propagate new `common.sh` template |
| `UpdateScripts/v1.01.sh` | New: migration loop script |
| `RulesEngine/BUSINESS_RULES.md` | Updated: add Python/Bash multi-environment rule |

### In Each Project (via v1.01.sh)

| File | Change |
|------|--------|
| `bin/common.sh` | Replaced with new template (Python-check + fallback) |
| `AGENTS.md` (CLAUDE_RULES section) | Updated via `bin/ProjectUpdate.sh` |

## Python Availability Check Pattern

The new `common.sh` template opens with:

```bash
# Prefer common.py if Python 3 is available
if command -v python3 >/dev/null 2>&1; then
    # Python handles OperationContext; source only the shell-compatible vars
    _COMMON_PY_MODE=true
    # ... extract project_name, port, display_name via python3 inline
else
    _COMMON_PY_MODE=false
    # ... existing common.sh logic
fi
```

Scripts that have complex logic should check `$_COMMON_PY_MODE` and exec into Python:
```bash
if [ "$_COMMON_PY_MODE" = true ]; then
    exec python3 "$(dirname "$0")/$(basename "$0" .sh).py" "$@"
fi
```

## Module Boundaries

| Module | Where | Purpose |
|--------|-------|---------|
| Parity audit | `data/common_parity_audit.md` | Documents gap analysis between common.sh and common.py |
| Template | `RulesEngine/templates/common.sh` | Updated canonical template for all projects |
| Migration runner | `UpdateScripts/v1.01.sh` | Loops projects, replaces common.sh, runs ProjectValidate |
| Validation | `bin/ProjectValidate.sh` | CLAUDE_RULES compliance + new --summary + .sh analysis |
| Rules update | `RulesEngine/BUSINESS_RULES.md` | Global rule for Python/Bash/driver standard |

## Open Questions

- Should `v1.01.sh` run `ProjectValidate.sh` on each project after migration and abort on failures, or collect all failures and report at the end?
- What is the controlled list of "standard managed scripts" that `ProjectValidate.sh` should analyze? (The spec mentions this distinction between standard scripts and app-specific ones.)
