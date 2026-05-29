# Screen: Setup — Repositories

| Field | Value |
|-------|-------|
| Version | 20260529 V1 |
| Route | `GET /setup/repositories` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Repositories |
| Tab Order | 1: Summary · 2: AWS · 3: GitHub · 4: Repositories · 5: Projects · 6: Settings |
| Description | Unified view of GitHub repositories and local projects. Shows which repos have been downloaded and provides one-click cloning. Supports browsing another GitHub user's public repos. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/repositories |

## Unconfigured State

If `github_username` is not set, or `gh auth status` fails, or `PROJECTS_DIR` is not set, the page shows a full-panel notice instead of the repo table:

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠  GitHub not configured                                    │
│                                                              │
│  Complete these steps on the GitHub tab:                     │
│  • Set your GitHub Username                                  │
│  • Authenticate: run gh auth login in a terminal             │
│  • Ensure PROJECTS_DIR is set in .env                        │
│                                                              │
│  [→ Go to GitHub Setup]                                      │
└──────────────────────────────────────────────────────────────┘
```

`Go to GitHub Setup` links to `/setup/github`.

## Layout

Full-width. Action bar at top, repo table below.

```
┌────────────────────────────────────────────────────────────────┐
│  [↻ Refresh]   [🔍 Search repos...]  [👤 Other user: _______ ]│
│  ──────────────────────────────────────────────────────────── │
│  ┌──────────┬────────────────────────┬──────────┬────────────┐ │
│  │ Status   │ Repository             │ Vis      │ Action     │ │
│  ├──────────┼────────────────────────┼──────────┼────────────┤ │
│  │ ✅ Local │ my-app                 │ Private  │ [Open ↗]   │ │
│  │          │ My web application     │          │            │ │
│  ├──────────┼────────────────────────┼──────────┼────────────┤ │
│  │ ☁ Cloud  │ old-experiments        │ Private  │ [Download] │ │
│  │          │ Various experiments    │          │            │ │
│  └──────────┴────────────────────────┴──────────┴────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

## Action Bar

| Control | Behavior |
|---------|----------|
| `↻ Refresh` (left) | Re-fetches repo list from GitHub API: `POST /api/repositories/sync`. Updates table via HTMX. Spinner while in progress. |
| Search input (center) | Client-side filter on repo name and description. Case-insensitive substring. |
| Other user input (right) | Text input, placeholder `GitHub username…`. Enter or `Fetch` loads that user's public repos (labelled clearly). `✕ Clear` resets to authenticated user's repos. Calls `GET /api/repositories?user={username}`. |

## Repo Table

One row per GitHub repository. Sorted: downloaded repos first (alphabetically), then not-downloaded (alphabetically).

| Column | Source | Notes |
|--------|--------|-------|
| Status | `github_repos.is_downloaded` | `✅ Local` (teal) if downloaded; `☁ Cloud` (muted) if not |
| Repository | `github_repos.name` + `github_repos.description` | Name bold, description muted below (truncated 80 chars). Name links to `github_repos.html_url` (new tab). |
| Visibility | `github_repos.private` | `Private` (amber pill) or `Public` (muted pill) |
| Last pushed | `github_repos.pushed_at` | Relative time (e.g. `3 days ago`) |
| Action | Derived from `is_downloaded` | See Action Column |

### Action Column

| `is_downloaded` | Action |
|-----------------|--------|
| 1 (downloaded) | `Open ↗` — links to the local directory path. |
| 0 (not downloaded) | `⬇ Download` button |

**Download button states:**

| State | Appearance |
|-------|-----------|
| Idle | `⬇ Download` (outline primary) |
| In progress | Spinner + `Cloning…` (disabled) |
| Success | `✓ Downloaded` (teal), status badge changes to `✅ Local`, action changes to `Open ↗` — no page reload |
| Error | `Failed` (red), inline error below the row |

Download clones to `{PROJECTS_DIR}/{repo.name}` via SSH, falling back to HTTPS when SSH is unavailable.

## Other User Mode

When the Other User input is populated:

- Banner above table: `Showing public repos for @{username}` (amber background, `✕ Back to my repos` on the right)
- Only public repos for that user are shown
- Status column still reflects whether the repo name matches a directory in `PROJECTS_DIR`
- Download button works (clones to `PROJECTS_DIR`)

## Empty State

If the authenticated user has no GitHub repos:
> *No repositories found for your GitHub account. Make sure `gh auth login` has been run.*

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/repositories/sync` | — | Updated table HTML fragment |
| GET | `/api/repositories` | — | Table HTML fragment (authenticated user) |
| GET | `/api/repositories?user={username}` | — | Table HTML fragment (other user, public only) |
| POST | `/api/repositories/download` | `repo_name`, `clone_url`, `ssh_url` | Row status fragment (button states) |

## Data Flow

| Reads | Writes |
|-------|--------|
| `github_repos` table (all columns) | `github_repos` table on Refresh (upsert via sync) |
| `projects` table (`name`, `path` for `Open` links) | New project directory + minimal `METADATA.md` on Download |
| `settings.github_username` | `projects` table (after download: registers the new project) |
| `PROJECTS_DIR` (env) | None |

GitHub API calls are server-side. Results cached in `github_repos` table; Refresh triggers a fresh fetch.

## Open Questions

- Should the table support multi-select + bulk download? V1: single download only.
- Should repos missing from GitHub but present on disk appear in this table? V1: no — disk-only projects appear on the Projects tab.
- Should Download also publish the project to the Marina DynamoDB catalog immediately? V1: no — publish happens via the Projects tab Conform action.
