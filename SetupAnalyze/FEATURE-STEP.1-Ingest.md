# FEATURE: Ingest and Postfix

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Detect non-conformed files and rename them .imported before conversion begins. |
| Phase       | 1 |

## Trigger

`bash bin/setup.sh <ProjectName> --analyze`
OR auto-triggered by `setup.sh <ProjectName>` when the directory exists but has no METADATA.md.

## Pre-conditions

- `<spec_dir>/<ProjectName>/` exists
- Directory contains at least one `.md` file
- No METADATA.md is present (if METADATA.md exists, the directory is already conformed — skip analyze)

## Sequence

1. Resolve `SPECS_DIR` from `METADATA.md specification_directory:` (same as existing setup.sh logic).
2. List all `.md` files in `$SPECS_DIR/$ProjectName/` that do NOT already end in `.imported`.
3. For each file:
   - If it is a recognized conformed filename (METADATA.md, INTENT.md, ARCHITECTURE.md, etc.) → skip (already conformed).
   - Otherwise → rename to `<filename>.imported`.
4. Print a summary: `Ingested N file(s): file1.md.imported, file2.md.imported`.
5. Exit with error if no `.md` files are found (nothing to ingest).

## Success Criteria

- All non-conformed `.md` files in the directory are renamed `*.imported`.
- No conformed files (METADATA.md, INTENT.md, etc.) are renamed.
- Script prints a clear list of what was ingested.
- `.imported` files are not touched on a re-run.

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Directory does not exist | Error: "Directory not found: <path>. Run setup.sh <name> first." |
| No .md files found | Error: "No specification files found in <path>." |
| All files already .imported | Skip ingestion step, proceed to STEP.2 (re-analyze with existing .imported files). |

## Quality Metrics

- Zero conformed files renamed accidentally (regression test: run against a fully conformed dir, verify no renames).
- Idempotent: running twice produces identical state.

## Open Questions

- Should `.imported` files be gitignored? They are historical reference — probably no, leave committed.
