# DATABASE: GitHub Repos Table

| Field       | Value |
|-------------|-------|
| Version     | 20260427 V1 |
| Description | Adds github_repos table and projects.github_repo_id FK for project inventory cross-linking. |
| Patches     | DATABASE.md |

## github_repos

Persists the full list of GitHub repositories fetched during startup scan. One row per repo. Upserted on each sync; never deleted (stale rows reflect history). Cross-linked to `projects` via `project_id` when a matching local project is found.

### Schema

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | INTEGER PK | — | Auto-increment |
| `name` | TEXT UNIQUE NOT NULL | — | Short repo name; matches `projects.name` for cross-linking |
| `full_name` | TEXT | — | `owner/repo` slug |
| `html_url` | TEXT | — | GitHub web URL |
| `clone_url` | TEXT | — | HTTPS clone URL |
| `private` | INTEGER | 0 | 1 = private repo |
| `description` | TEXT | — | Repo description from GitHub |
| `is_downloaded` | INTEGER | 0 | 1 if repo name matches a directory in `PROJECTS_DIR` |
| `project_id` | INTEGER FK→`projects(id)` | NULL | Set after local scan cross-link; NULL if not downloaded |
| `synced_at` | TEXT | — | ISO-8601 UTC timestamp of last sync |

### Source

Populated by `_sync_github_repos()` in `scanner.py` during startup scan. Uses `gh api --paginate /user/repos` (authenticated via `gh` CLI — no token in `.env`).

---

## projects table — new column

Add via `_add_column_if_missing` in `_run_migrations()`:

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `github_repo_id` | INTEGER FK→`github_repos(id)` | NULL | Set after GitHub sync cross-link; NULL if repo not in GitHub |

---

## Field Source Mapping additions

| Table | Column | Source | Notes |
|-------|--------|--------|-------|
| `github_repos` | all columns | GitHub API via `gh api /user/repos` | Fetched at startup |
| `github_repos.is_downloaded` | Derived | Scanner cross-reference | 1 if `name` matches a PROJECTS_DIR subdirectory |
| `github_repos.project_id` | Derived | Scanner cross-reference | Matched by `lower(name)` after local scan |
| `projects.github_repo_id` | Derived | Scanner cross-reference | Matched by `lower(name)` after GitHub sync |

---

## Open Questions
- None.
