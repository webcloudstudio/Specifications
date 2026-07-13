# Screen: Welcome — GitHub

| Field | Value |
|-------|-------|
| Version | 20260510 V1 |
| Route | `GET /welcome/github` |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | GitHub |
| Tab Order | 1: Summary · 2: GitHub · 3: Projects |
| Description | Unified view of GitHub repos and local projects. Shows what has been downloaded to disk and provides one-click cloning (Project-Download feature). Supports fetching repos from other GitHub users. |
| Depends On  | UI-GENERAL.md, FEATURE-Project-Download.md |
| Provides    | GET /welcome/github |

## Unconfigured State

If `github_username` is not set in settings, or `gh auth status` fails, or `PROJECTS_DIR` is not set, the page shows a full-panel notice instead of the repo table:

```
┌──────────────────────────────────────────────────────────┐
│  ⚠  GitHub not configured                                 │
│                                                           │
│  Complete these steps on the Summary tab:                 │
│  • Set your GitHub Username                               │
│  • Authenticate: run gh auth login in a terminal          │
│  • Ensure PROJECTS_DIR is set in .env                     │
│                                                           │
│  [→ Go to Summary]                                        │
└──────────────────────────────────────────────────────────┘
```

The `Go to Summary` link navigates to `/welcome/summary`.

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
│  │ ✅ Local │ conquer-2026           │ Public   │ [Open ↗]   │ │
│  │          │ 2026 strategy game     │          │            │ │
│  ├──────────┼────────────────────────┼──────────┼────────────┤ │
│  │ ☁ Cloud  │ old-experiments        │ Private  │ [Download] │ │
│  │          │ Various experiments    │          │            │ │
│  ├──────────┼────────────────────────┼──────────┼────────────┤ │
│  │ ☁ Cloud  │ portfolio-site         │ Public   │ [Download] │ │
│  │          │ Personal portfolio     │          │            │ │
│  └──────────┴────────────────────────┴──────────┴────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

## Action Bar

| Control | Behavior |
|---------|----------|
| `↻ Refresh` button (left) | Re-fetches repo list from GitHub API: `POST /api/github/repos/sync`. Updates table in place via HTMX. Spinner while in progress. |
| Search input (center) | Client-side filter on repo name and description. Placeholder: `Search repos…`. Case-insensitive substring. |
| Other user input (right) | Text input with placeholder `GitHub username…`. Pressing Enter or clicking a small `Fetch` button loads that user's public repos into the table (clearly labelled). When populated, a `✕ Clear` button resets to the authenticated user's repos. Calls `GET /api/github/repos?user={username}`. |

## Repo Table

One row per GitHub repository. Rows are sorted: downloaded repos first (alphabetically), then not-downloaded repos (alphabetically).

| Column | Source | Notes |
|--------|--------|-------|
| Status badge | `github_repos.is_downloaded` | `✅ Local` (green) if downloaded; `☁ Cloud` (blue) if not downloaded |
| Repository | `github_repos.name` + `github_repos.description` | Name bold on top line; description muted below, truncated at 80 chars. Name is a link to `github_repos.html_url` (opens new tab). |
| Visibility | `github_repos.private` | `Private` pill (amber) or `Public` pill (muted). |
| Last pushed | `github_repos.pushed_at` | Relative time (e.g. `3 days ago`). |
| Action | Derived from `is_downloaded` | See Action Column below. |

### Action Column

| `is_downloaded` | Action |
|-----------------|--------|
| 1 (downloaded) | `Open ↗` — links to `/project/{matched project id}` if `project_id` is set; otherwise links to the local directory path. |
| 0 (not downloaded) | `Download` button — triggers Project-Download feature (see FEATURE-Project-Download.md). |

**Download button states:**
- Idle: `⬇ Download` (outline primary)
- In progress: spinner + `Cloning…` (disabled)
- Success: `✓ Downloaded` (green), status badge changes from `☁ Cloud` to `✅ Local`, action changes to `Open ↗` without a page reload
- Error: `Failed` (red), inline error message below the row

## Other User Mode

When the Other User input is populated with a valid GitHub username:

- A banner appears above the table: `Showing public repos for @{username}` (amber background, `✕ Back to my repos` link on the right)
- Only public repos for that user are shown (private repos are hidden — the API won't return them for unauthenticated access to another user's repos)
- The Status column still reflects whether the repo name matches a directory in `PROJECTS_DIR`
- Download button still works (clones to `PROJECTS_DIR`)

## Empty State

If the authenticated user has no GitHub repos (rare):

> *No repositories found for your GitHub account. Make sure `gh auth login` has been run.*

## Data Flow

| Reads | Writes |
|-------|--------|
| `github_repos` table (all columns) | `github_repos` table on Refresh (upsert via scanner) |
| `projects` table (`id`, `name` for `Open` links) | New project directory + METADATA.md on Download |
| `settings.github_username` | None |
| `PROJECTS_DIR` (env) | None |

GitHub API calls are server-side. Results are cached in `github_repos` table; `Refresh` triggers a fresh `gh api /user/repos` fetch.

For Other User mode, the server calls `GET /api/github/repos?user={username}` which hits `gh api /users/{username}/repos` — public repos only, not cached.

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/api/github/repos/sync` | — | Updated table HTML fragment (HTMX) |
| GET | `/api/github/repos` | — | Table HTML fragment for authenticated user's repos |
| GET | `/api/github/repos?user={username}` | — | Table HTML fragment for other user's public repos |
| POST | `/api/github/download` | `repo_name`, `clone_url`, `ssh_url` | Status fragment (Download button states) — see FEATURE-Project-Download.md |

## Open Questions

- Should the table support multi-select + bulk download? V1: single download only.
- Should there be a "Star count" or "Last commit" column? V1: omit to keep the table clean.
- Should repos missing from GitHub but present on disk appear in this table? V1: no — disk-only projects appear on the Projects tab instead.
