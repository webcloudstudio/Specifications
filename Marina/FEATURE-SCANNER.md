# Feature: Scanner

| Field       | Value |
|-------------|-------|
| Version     | 20260707 V1 |
| Description | Local scan that populates Marina's project registry, GitHub repository cache, and platform statistics. |
| Depends On  | DATABASE.md |
| Provides    | POST /api/projects/scan, POST /api/repositories/sync |

**Description:** Discovers local projects and GitHub repositories, then refreshes Marina's local registry
and aggregate setup/project counters.

## Trigger

- Application startup.
- Setup Git Scan button.
- Projects Dashboard `Rescan Projects` button.

## Sequence

1. Read PROJECTS_DIR.
2. Discover child directories with `METADATA.md`.
3. Parse project identity, status, namespace, git repo, stack, and health metadata.
4. Detect conformance flags.
5. Refresh `projects` and `platform_stats`.
6. When requested, fetch configured `github_sources` and refresh `github_repos`.
7. Cross-link GitHub repos to downloaded projects.

## Reads

- PROJECTS_DIR.
- Project `METADATA.md`.
- Project git remote.
- `github_sources`.

## Writes

- `projects`.
- `github_repos`.
- `platform_stats`.

## Open Questions
- None.
