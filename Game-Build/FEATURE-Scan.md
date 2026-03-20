# Feature: Project Scan

**Version:** 20260320 V1
**Description:** Spec for the Project Scan feature

Discovers projects on disk and populates the database.

## Trigger

- Platform startup (background thread, non-blocking)
- User clicks Refresh button on Dashboard

## Sequence

1. `cleanup_orphaned()` — mark DB rows for projects no longer on disk as `is_active=false`
2. For each directory in `$PROJECTS_DIR`:
   a. `detect_project()` — read filesystem flags (has_git, has_venv, has_node, has_claude, has_docs), detect doc_path, auto-detect stack and port
   b. `parse_metadata_md()` — parse key:value lines → identity fields, parse `## Links` → extra.links, parse card fields
   c. `scan_bin_operations()` — read first 20 lines of each bin/*.sh and bin/*.py, extract CommandCenter headers (Name, Category, Port, Schedule, Timeout, Health)
   d. Parse AGENTS.md if present → extra.bookmarks
   e. `upsert_project()` — UPDATE existing (COALESCE preserves user-edited nulls), INSERT new, DELETE+re-seed operations for this project
3. Log scan duration per project and total

## Reads

Filesystem ($PROJECTS_DIR), METADATA.md, AGENTS.md, bin/ scripts, .git/

## Writes

`projects` table, `operations` table

## Key Behaviors

- Non-blocking on startup — first page load returns immediately
- Missing files produce compliance gaps, not errors
- Projects removed from disk are marked inactive, not deleted
- Git operations (status, log) run per-project — can be slow with many repos
- User-edited fields preserved on re-scan via COALESCE

## Open Questions

- Scan timeout per project to prevent slow git repos from blocking?
- Parallel scanning of multiple projects?
