# Screen: Setup — Repositories

| Field | Value |
|-------|-------|
| Version | 20260603 V6 |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Repositories are the Git Projects you have in your various sources. |
| Route | `GET /setup/repositories` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Repositories |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Repository acquisition queue across configured sources. Shows which repositories are available, imported, or already managed, and provides one-click clone/import. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/repositories |

## Header KPIs

Left column of the page header. Component type: **Count Block** (`mn-hdr-count`).

Single count block:

```html
<div class="mn-hdr-count">
  <span class="mn-hdr-count__number">{N}</span>
  <span class="mn-hdr-count__label">Repos</span>
</div>
```

N = total row count in `github_repos` across all source accounts. If `github_repos` is empty (never scanned), shows `0` with amber colour override on the number: `color: var(--mn-hdr-warn-bg)`.

## Unconfigured State

If `gh auth status` fails, no sources are configured, or `PROJECTS_DIR` is not set, the page shows a full-panel notice instead of the repo table:

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠  GitHub not configured                                    │
│                                                              │
│  Complete these steps on the GitHub tab:                     │
│  • Authenticate: run gh auth login in a terminal             │
│  • Add at least one scan source                              │
│  • Ensure PROJECTS_DIR is set on the Summary tab             │
│                                                              │
│  [→ Go to GitHub Setup]                                      │
└──────────────────────────────────────────────────────────────┘
```

`Go to GitHub Setup` links to `/setup/github`.

## Layout

Full-width. Search bar at top, repo table below. No Refresh button — sync is triggered from the Git Scan tab only.

No pagination — all rows from `github_repos` are rendered on page load regardless of count. Navigating to this tab triggers a full page load so the table always reflects the latest `github_repos` state.

```
┌────────────────────────────────────────────────────────────────┐
│  [🔍 Search repos...]                                          │
│  ──────────────────────────────────────────────────────────── │
│  ┌──────┬──────────────────────┬──────────┬────────┬────────┐  │
│  │      │ Repository           │ Source   │ Vis    │ Action │  │
│  ├──────┼──────────────────────┼──────────┼────────┼────────┤  │
│  │ 💾   │ my-app               │ wcs      │Private │[↗ Open]│  │
│  ├──────┼──────────────────────┼──────────┼────────┼────────┤  │
│  │      │ old-experiments      │ wcs      │Private │[⬇ Get] │  │
│  └──────┴──────────────────────┴──────────┴────────┴────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## Action Bar

| Control | Behavior |
|---------|----------|
| Search input | Client-side filter on repo name. Case-insensitive substring. Instant — no server call. |
| Namespace selector | Choose the namespace assigned to a newly cloned repository. |
| Tags selector | Assign initial tags to a newly cloned repository. |

## Repo Table

One row per GitHub repository across all source accounts. Sorted: downloaded repos first (alphabetically), then not-downloaded (alphabetically).

One row per repo — compact, single line, no description sub-text. Default sort: downloaded first (alphabetical), then not-downloaded (alphabetical).

| Column | Source | Notes |
|--------|--------|-------|
| On Disk | `github_repos.is_downloaded` | 💾 disk icon (teal) if downloaded; blank if not. No text label. |
| Repository | `github_repos.name` | Repo name — bold, links to `github_repos.html_url` (opens in new browser tab). No description. |
| Source | `github_repos.source_account` | Column omitted entirely if all visible rows share the same source (single-source installs). |
| Visibility | `github_repos.private` | `Private` (amber pill, small) or `Public` (muted pill, small) |
| Last pushed | `github_repos.pushed_at` | Relative time (e.g. `3d ago`) |
| Action | Derived from `is_downloaded` | See Action Column |

### Action Column

All buttons are small pill-style (`btn-sm` + `rounded-pill`) with icons. Colors are retained in disabled state at reduced opacity — do not swap to grey.

| `is_downloaded` | Action |
|-----------------|--------|
| 1 (downloaded) | `↗ Open` — small teal pill. Opens `github_repos.html_url` in a new browser tab. |
| 0 (not downloaded) | `⬇ Clone` — small primary pill. Clones repo to disk and opens the import confirmation. |

**Clone (`⬇ Clone`) button states:**

| State | Appearance |
|-------|-----------|
| Idle | `⬇ Clone` (primary pill, small) |
| In progress | spinner only (disabled, same primary colour) |
| Success | `💾 ↗ Open` — disk icon appears in On Disk column; action button swaps to `↗ Open` teal pill — no page reload |
| Error | `!` (red pill), tooltip shows clone error |

Clone uses SSH, falling back to HTTPS when SSH is unavailable. The destination is validated as a new
child of `PROJECTS_DIR`; Marina never overwrites an existing directory. After cloning, Marina reads or
creates identity, assigns the selected namespace/tags, scans the repository, and hands it to PROJECTS.

## Empty State

If the authenticated user has no GitHub repos:
> *No repositories found for your GitHub account. Make sure `gh auth login` has been run.*

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/api/repositories` | — | Table HTML fragment (all source accounts) |
| POST | `/api/repositories/download` | `repo_name`, `clone_url`, `ssh_url`, `namespace`, `tags[]` | Clone/import status fragment |

`POST /api/repositories/sync` belongs to the Git Scan tab — not called from this screen.

## Data Flow

| Reads | Writes |
|-------|--------|
| `github_repos` table (all columns) | `github_repos` table on Refresh (upsert via sync) |
| `projects` table (`name`, `path` for `Open` links) | New project directory; `METADATA.md` only when absent |
| None | `projects` table (after download: registers the new project) |
| `PROJECTS_DIR` (env) | None |

GitHub API calls are server-side. Results cached in `github_repos` table; Refresh triggers a fresh fetch.

## Open Questions

- Should the table support multi-select + bulk download? V1: single download only.
- Should repos missing from GitHub but present on disk appear in this table? V1: no — disk-only projects appear on the Projects tab.
- Should Clone support a path outside `PROJECTS_DIR`? V1: no — managed projects remain beneath the configured directory.
