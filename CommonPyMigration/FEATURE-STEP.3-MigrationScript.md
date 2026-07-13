# FEATURE: Migration Script v1.01.sh

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | UpdateScripts/v1.01.sh — loops through all projects and updates common.sh to the new Python-fallback template. |
| Phase       | 3 |

## Trigger

`bash UpdateScripts/v1.01.sh [--dry-run] [--project <name>]`

One-time migration script. Safe to re-run (idempotent).

## Restricted List

v1.01.sh operates only on scripts that are owned/managed by the Prototyper standards:
- `bin/common.sh` (the template-managed file)
- `bin/start.sh`, `bin/stop.sh`, `bin/test.sh` (standard scripts)
- Any script carrying `# CommandCenter Operation` in its first 20 lines

App-specific scripts (not on the restricted list) are not modified.

## Sequence

1. Read the list of project directories from `$PROJECTS_DIR` (one level up from Prototyper).
2. For each directory that has a `bin/common.sh` AND a `METADATA.md`:
   a. Check if `common.sh` already has the Python fallback block (idempotency check: look for `_COMMON_PY_MODE`).
   b. If not: copy the new `RulesEngine/templates/common.sh` to `bin/common.sh`.
   c. Run `bin/ProjectValidate.sh <project>` — collect pass/fail.
   d. Print per-project result: `[OK]`, `[UPDATED]`, `[ALREADY CURRENT]`, `[FAILED]`.
3. Print a summary: N updated, N already current, N failed.
4. Exit non-zero if any project fails validation.

## --dry-run Mode

Prints what would be changed per project without writing any files. Useful for previewing scope before committing.

## CommandCenter Header

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Common.py Migration v1.01
# Category: Global
# Description: Migrate all managed projects to Python-fallback common.sh template.
```

## Success Criteria

- `--dry-run` correctly identifies all projects with old `common.sh` (no `_COMMON_PY_MODE`).
- Full run updates all identified projects without corrupting any `common.sh`.
- `ProjectValidate.sh` passes for every updated project.
- Script is idempotent: running twice produces the same output (N already current on second run).

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Project has no `bin/common.sh` | Skip with note: "No common.sh — skipping." |
| ProjectValidate fails after update | Print `[FAILED] <project>` and continue; exit 1 at the end |
| File write permission denied | Print error per project; continue |

## Open Questions

- Should v1.01.sh also update `bin/ProjectUpdate.sh` calls to propagate the new template on future runs? Or is that handled by the normal `bin/ProjectUpdate.sh` workflow?
- Should the restricted list be hardcoded in v1.01.sh or read from a config file?
