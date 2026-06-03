# Screen: Setup — Git Scan

| Field | Value |
|-------|-------|
| Version | 20260603 V5 |
| Header Background | `mn-hdr-bg--git` |
| Route | `GET /setup/scan` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Git Scan |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Scans configured GitHub source accounts for repositories and reconciles them with PROJECTS_DIR. Results table shows On GitHub, Downloaded, Conformed, and Not Downloaded counts per source — all from the same counting domain so numbers always add up. |
| Depends On | UI-GENERAL.md, SCREEN-SETUP-GITHUB.md |
| Provides | GET /setup/scan |

## Header KPIs

Left column of the page header. Component type: **Header Action Button** (`mn-hdr-btn`).

```html
<button class="mn-hdr-btn" hx-post="/api/repositories/sync" hx-target="#scan-results" hx-swap="innerHTML">
  <i class="bi bi-arrow-clockwise"></i> Scan GitHub Now
</button>
```

Disabled with spinner while a scan is in progress. Last scan time is in the page body.

## Purpose

Fetches the repository list from every configured source account and reconciles it against `PROJECTS_DIR`. After a scan, the Repositories and Projects tabs reflect the updated data. This is the only entry point for refreshing the GitHub repo list.

## Prerequisites

- GitHub configured (Auth ✅ and ≥1 source in `github_sources`)
- `PROJECTS_DIR` set

If unconfigured, the tab is disabled — see UI-GENERAL tab gates.

## Counting Domain

All numeric rows in the results table count from the same domain: **`github_repos` for each source account**. This ensures rows always add up correctly.

| Term | Counts |
|------|--------|
| **On GitHub** | Repos returned by the GitHub API for this source — the full set Marina knows about |
| **Downloaded** | Subset of On GitHub that have a matching directory in `PROJECTS_DIR` |
| **Not Downloaded** | On GitHub minus Downloaded — repos not yet cloned locally |
| **Conformed** | Subset of Downloaded that pass `bin/ProjectValidate.sh` |

Invariants that must always hold:
- `Downloaded + Not Downloaded = On GitHub`
- `Conformed ≤ Downloaded`

**Other column** is the exception: it counts local projects in `PROJECTS_DIR` whose GitHub remote URL does not match any configured source. For Other, "Downloaded" = total Other projects (all are local by definition); "On GitHub" and "Not Downloaded" are not applicable.

## Layout

Single-column, max-width 900px, centered. Timestamp line, then results table.

```
┌──────────────────────────────────────────────────────────────────┐
│  Last scan: 2026-06-03 09:12  (server startup)                   │
│                                                                  │
│  ┌──────────────────────────┬──────────────────┬───────────────┐ │
│  │                          │ webcloudstudio   │ Other         │ │
│  ├──────────────────────────┼──────────────────┼───────────────┤ │
│  │ On GitHub          ℹ️    │        42        │      —        │ │
│  │ Downloaded         ℹ️    │        18        │       5       │ │
│  │ Conformed          ℹ️    │        12        │       3       │ │
│  │ Not Downloaded     ℹ️    │        24        │      —        │ │
│  │ ──────────────────────── │ ──────────────── │ ───────────── │ │
│  │ Total Visible      ℹ️    │        18        │       5       │ │
│  └──────────────────────────┴──────────────────┴───────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

Numbers in this example: 18 + 24 = 42 ✓. Conformed 12 ≤ Downloaded 18 ✓.

## Scan Action

`[Scan GitHub Now]` lives in the page header KPI. On click, HTMX targets both `#scan-timestamp` and `#scan-results` independently.

| Element | Behaviour |
|---------|-----------|
| Timestamp | Absolute datetime + relative label (e.g. `2026-06-03 09:12 · server startup`). Persisted in `platform_stats.last_scan`. Element ID `scan-timestamp`. |
| No scan yet | Table absent; replaced with: `No scan yet — click Scan GitHub Now to begin.` |

## Results Table

One column per entry in `github_sources`, plus **Other** (always last). Columns appear in the order sources were added.

### Row Definitions

Each row label has a `ℹ️` icon. Hovering the icon shows the tooltip.

| Row | Tooltip | Source query | Other column |
|-----|---------|-------------|--------------|
| **On GitHub** | Repos found on GitHub for this source account during the last scan | `COUNT(*) FROM github_repos WHERE source_account = {col}` | `—` (N/A) |
| **Downloaded** | Repos cloned into PROJECTS_DIR (present on disk) | `COUNT(*) FROM github_repos WHERE source_account = {col} AND is_downloaded = 1` | `COUNT(*) FROM projects WHERE source_account IS NULL` |
| **Conformed** | Downloaded repos that pass Marina standards (valid METADATA.md) | `COUNT(*) FROM github_repos WHERE source_account = {col} AND is_downloaded = 1 AND is_conformed = 1` | same filter on `projects` |
| **Not Downloaded** | Repos on GitHub not yet cloned locally (On GitHub − Downloaded) | `COUNT(*) FROM github_repos WHERE source_account = {col} AND is_downloaded = 0` | `—` (N/A) |
| **Total Visible** | Total projects visible for this source (= Downloaded for named sources) | Same as Downloaded | Same as Downloaded |

`Total Visible` is a summary row separated by a thin rule. It equals `Downloaded` for named source columns and `Downloaded` for Other. It exists to make the total clear at a glance.

### Other Column

Projects in `PROJECTS_DIR` with a `.git/` folder and a `github.com` remote, but whose remote URL owner does not match any entry in `github_sources`. These are valid GitHub projects Marina can manage but has not scanned from a configured source.

| Row | Value |
|-----|-------|
| On GitHub | `—` |
| Downloaded | Count of `projects` with `source_account IS NULL` |
| Conformed | Count of those with `is_conformed = 1` |
| Not Downloaded | `—` |
| Total Visible | = Downloaded |

### Cell Styling

| Value | Style |
|-------|-------|
| Zero in a meaningful row | Amber text (`var(--mn-hdr-warn-bg)`) to signal attention |
| `—` (N/A) | Muted, centered |
| Positive number | Normal weight |
| Conformed = Downloaded (100%) | Teal text |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/repositories/sync` | — | Updated `#scan-timestamp` + `#scan-results` HTML fragments |
| GET | `/api/setup/scan/status` | — | JSON: `{ last_scan, sources: [{ account, on_github, downloaded, conformed, not_downloaded }], other: { downloaded, conformed } }` |

## Data Flow

| Reads | Writes |
|-------|--------|
| `github_sources` table (column headings) | `platform_stats.last_scan` (on sync) |
| GitHub API `/users/{name}/repos` or `/orgs/{name}/repos` per source | `github_repos` table (upsert on sync) |
| `projects` table (`source_account`, `is_conformed`) | `github_repos.is_downloaded` (updated if local dir found) |
| `PROJECTS_DIR` filesystem | None |

## Open Questions

- Should the table show a diff (new / removed repos since last scan)? V2.
- Should Marina auto-scan at startup if `github_repos` is empty? V1: yes — scan once on startup.
