# Screen: Setup — Git Scan

| Field | Value |
|-------|-------|
| Version | 20260602 V4 |
| Header Background | `mn-hdr-bg--git` |
| Route | `GET /setup/scan` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Git Scan |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Scans all configured GitHub source accounts for repositories and reconciles them with local projects. Displays project counts grouped by source account. Unlocked after GitHub is configured and at least one source account has readable repositories. |
| Depends On | UI-GENERAL.md, SCREEN-SETUP-GITHUB.md |
| Provides | GET /setup/scan |

## Header KPIs

Left column of the page header. Component type: **Header Action Button** (`mn-hdr-btn`).

```html
<button class="mn-hdr-btn" hx-post="/api/repositories/sync" hx-target="#scan-results" hx-swap="innerHTML">
  <i class="bi bi-arrow-clockwise"></i> Scan GitHub Now
</button>
```

The button is disabled and shows a spinner while a scan is in progress. No timestamp or text label in the header KPI area — only the action button. The last scan time is displayed in the page body below.

## Purpose

Fetches the repository list from every source account in `github_sources` and reconciles it against projects on disk in `PROJECTS_DIR`. After a scan, the Repositories and Projects tabs reflect the updated data. This screen is the single entry point for refreshing the GitHub repo list.

## Prerequisites

- GitHub must be configured (GitHub Auth ✅ and GitHub SSH ✅).
- At least one source account must have at least one readable repository (enforced by the tab disable gate in UI-GENERAL).
- PROJECTS_DIR must be set.

If unconfigured, the tab is disabled (not hidden) — see UI-GENERAL tab gates.

## Layout

Single-column, max-width 900px, centered. Last scan timestamp, then the results table. The Scan action button lives in the page header KPI (not repeated here).

```
┌──────────────────────────────────────────────────────────────┐
│  Last scan: 2026-06-01 09:12  (server startup)               │
│                                                              │
│  ┌────────────────┬─────────────────┬──────────┬───────────┐ │
│  │                │ webcloudstudio  │ acme-org │ Other     │ │
│  ├────────────────┼─────────────────┼──────────┼───────────┤ │
│  │ Project Count  │       42        │    8     │     5     │ │
│  │ Git Projects   │       38        │    8     │     0     │ │
│  │ Conformed      │       21        │    3     │     1     │ │
│  │ Not Downloaded │       24        │    5     │    n/a    │ │
│  └────────────────┴─────────────────┴──────────┴───────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Scan Action

The `[Scan GitHub Now]` button lives in the page header KPI (see Header KPIs). The page body shows the last scan timestamp and results only.

| Element | Behaviour |
|---------|-----------|
| Last scan timestamp | The time of the most recent scan. Initialised at Marina startup. Persisted in `platform_stats.last_scan`. Shown as absolute datetime with relative label (e.g. `2026-06-01 09:12 · server startup`). Element ID `scan-timestamp`. |

When the header button triggers a scan it targets both `#scan-timestamp` and `#scan-results` via HTMX for independent inline updates.

The button is always enabled when the tab is accessible.

## Results Table

Displayed after a scan has been run (table is absent before first scan; replaced with "No scan yet — click SCAN GITHUB NOW.").

Columns — one per entry in `github_sources`, plus an **Other** column (always last):

| Column | Content |
|--------|---------|
| `{source_account}` | Repos fetched from that GitHub account |
| Other | Projects in `PROJECTS_DIR` whose `git_repo` field is blank, unrecognised, or missing |

Rows — four fixed rows, one per metric:

| Row | Description | Source |
|-----|-------------|--------|
| Project Count | Total repositories known for this source | `github_repos` count WHERE `source_account = {col}` |
| Git Projects | Count of local projects (in `PROJECTS_DIR`) whose `git_repo` matches a repo from this source | `projects.git_repo` JOIN `github_repos` |
| Conformed | Count of local projects with a valid `METADATA.md` (conformed to Marina standards) | `projects.is_conformed = 1` |
| Not Downloaded | Repos in `github_repos` for this source that have no matching directory in `PROJECTS_DIR` | `github_repos.is_downloaded = 0` |

**Other column:** For the "Other" column, "Project Count" = count of `projects` with no `git_repo` or a `git_repo` not matching any known source. "Git Projects" and "Not Downloaded" are not applicable (show `—`). "Conformed" = count of those projects with `is_conformed = 1`.

No "Catalog Last Published" row.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/repositories/sync` | — | Updated scan timestamp + results table HTML fragment |
| GET | `/api/setup/scan/status` | — | JSON: `{ last_scan, sources: [{ account, repo_count, git_project_count, conformed_count, not_downloaded }], other: { project_count, conformed_count } }` |

## Data Flow

| Reads | Writes |
|-------|--------|
| `github_sources` table (column headings) | `platform_stats.last_scan` (on sync) |
| `github_repos` table | `github_repos` table (upsert on sync) |
| `projects` table (`git_repo`, `is_conformed`) | None |
| `PROJECTS_DIR` (env) | None |

## Open Questions

- Should Marina always run a scan at startup (even if `github_repos` is populated), or only when the table is empty? V1: scan at startup always, persist the startup time as `last_scan`.
- Should the table show a diff (new/removed repos since last scan)? V2.
