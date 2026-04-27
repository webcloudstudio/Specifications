# FEATURE: Startup Scanner

| Field       | Value |
|-------------|-------|
| Version     | 20260427 V1 |
| Description | Async startup scan that populates projects, github_repos, and platform_stats from local disk and GitHub. |
| Depends On  | DATABASE.md, DATABASE-001-github-repos.md |
| Provides    | — |

Runs once at application startup in a background thread. Three phases: local disk scan → GitHub sync → cross-link. Writes results to `projects`, `github_repos`, and `platform_stats`. All phases are non-fatal — failure in one does not abort the others.

---

## Trigger

| Event | Handler |
|-------|---------|
| Application startup (factory `create_app()`) | `start_async_scan(app)` — daemon thread |

No HTTP endpoint triggers the scan in normal operation. Triggered once per process lifetime.

---

## Phase 1: Local Disk Scan

Function: `_do_scan(db, projects_dir)`

1. `os.scandir(PROJECTS_DIR)` — sorted alphabetically, skip hidden dirs.
2. For each directory entry:
   - `has_metadata = METADATA.md exists`
   - `has_git = .git/ directory exists`
   - If neither → skip.
   - If `has_metadata` → call `_scan_project(db, entry.path)` — full upsert to `projects`, scan `bin/` for operations. Returns `status` string.
   - If `has_git` only (no METADATA.md) → insert minimal row: `name=dirname, display_name=dirname, path=entry.path, status='UNKNOWN', is_active=1`. No bin scan.
3. Accumulate `state_counts` dict (`{'ACTIVE': 3, 'PROTOTYPE': 6, 'UNKNOWN': 2, ...}`).

### `_scan_project` behaviour (unchanged)

Reads `METADATA.md` fields: `name`, `display_name`, `status`, `port`, `stack`, `health`, `short_description`, `show_on_homepage`. Reads `AGENTS.md` or `CLAUDE.md` for bookmarks and endpoints. Upserts one row in `projects`. Scans `bin/` for `# CommandCenter Operation` headers → upserts `operations` rows.

---

## Phase 2: GitHub Sync

Function: `_sync_github_repos(db, projects_dir)`

1. Run: `gh api --paginate /user/repos --jq '.[]'` (subprocess, timeout 60s).
   - Uses `gh` CLI authentication — no `GITHUB_TOKEN` or `GITHUB_USERNAME` env var required.
   - If `gh` is not installed or not authenticated: log warning, return 0. Scan continues.
2. Parse output as NDJSON (one JSON object per line).
3. Build `local_names` set: lowercased names of all non-hidden subdirectories in `PROJECTS_DIR`.
4. For each repo from GitHub API:
   - `is_downloaded = 1` if `repo.name.lower()` in `local_names`, else `0`.
   - `INSERT INTO github_repos ... ON CONFLICT(name) DO UPDATE SET ...` — upsert all fields.
5. Return `len(repos)`.

### Error handling

| Condition | Behaviour |
|-----------|-----------|
| `gh` not found (`FileNotFoundError`) | Log warning, return 0 |
| `gh` auth failure (non-zero exit) | Log warning with stderr, return 0 |
| `subprocess.TimeoutExpired` | Log warning, return 0 |
| Individual JSON parse error | Skip line, continue |

---

## Phase 3: Cross-Link

After Phase 1 and Phase 2 complete:

1. For each row in `github_repos`: find `projects` row where `lower(projects.name) = lower(github_repos.name)`.
2. If match: set `github_repos.project_id = projects.id` and `projects.github_repo_id = github_repos.id`.
3. Commit all changes in one transaction.

---

## Phase 4: platform_stats Update

Function: `_update_platform_stats(db, state_counts, github_repo_count)`

```
INSERT OR REPLACE INTO platform_stats
  (id, github_repo_count, scan_projects_total, projects_by_state, scan_last_completed)
  VALUES (1, <github_repo_count>, <sum(state_counts)>, <json(state_counts)>, datetime('now'))
```

`github_repo_count` = return value from `_sync_github_repos` (0 if `gh` unavailable).

---

## Reads

| Source | Data |
|--------|------|
| `PROJECTS_DIR` (env) | Directory listing for local scan |
| `METADATA.md` per project | Project identity fields |
| `AGENTS.md` / `CLAUDE.md` per project | Bookmarks, endpoints |
| `bin/` scripts (first 20 lines) | CommandCenter Operation headers |
| `gh api /user/repos` | Full GitHub repo list (paginated) |

## Writes

| Table | Operation |
|-------|-----------|
| `projects` | UPSERT per scanned directory |
| `operations` | UPSERT per bin/ script with CC header |
| `github_repos` | UPSERT per GitHub repo |
| `projects.github_repo_id` | UPDATE after cross-link |
| `github_repos.project_id` | UPDATE after cross-link |
| `platform_stats` | INSERT OR REPLACE (single row, id=1) |

## .env changes

Remove `GITHUB_USERNAME` and `GITHUB_TOKEN` from `.env.sample` — authentication is via `gh auth login`, not token.

---

## Open Questions
- None.
