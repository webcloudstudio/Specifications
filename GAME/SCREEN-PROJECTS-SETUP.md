# Screen: Project Setup

| Field | Value |
|-------|-------|
| Version | 20260325 V1 |
| Route | `GET /project-setup` |
| Parent | — |
| Main Menu | Projects |
| Sub Menu | Setup |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance · 5: Setup |
| Description | Discover unregistered GitHub repos and bring them into GAME. Own layout — does not extend SCREEN-DEFAULT (source of truth is the GitHub API, not the GAME database). |
| Depends On  | UI-GENERAL.md |

## Prerequisites

The screen requires `GITHUB_USERNAME` (and optionally `GITHUB_TOKEN`) to be set in `.env`. If not configured, the screen shows a configuration notice instead of the project list.

## Layout

Single-panel full-width table. Action bar at top. Two logical sections within the table: **Unregistered** repos (top, default visible) and **Registered** repos (bottom, collapsed by default). A filter control switches between sections.

## Action Bar

| Element | Position | Behavior |
|---------|----------|----------|
| `Refresh from GitHub` button | Left | Re-fetches GitHub repo list (calls `GET /api/github/repos`) |
| Section toggle | Center | Pills: `Unregistered (N)` / `Registered (N)` |
| Search input | Right | Client-side filter on repo name |

## Unregistered Repos Table

Repos present on GitHub but absent from `projects` table (matched by comparing `METADATA.md → git_repo` against `repo.clone_url` / `repo.ssh_url`).

| Column | Source | Content |
|--------|--------|---------|
| Repo name | GitHub API `repo.name` | Full slug (e.g. `my-app`) |
| Description | GitHub API `repo.description` | One-line, truncated |
| Language | GitHub API `repo.language` | Primary language badge |
| Last push | GitHub API `repo.pushed_at` | Relative time |
| Visibility | GitHub API `repo.private` | `Private` / `Public` pill |
| Action | — | `Make A Project` button |

### Make A Project Button

**What it does:**
1. `git clone <ssh_url> ~/Projects/<repo.name>` (uses SSH; requires SSH key configured — see SCREEN-WELCOME.md)
2. Creates a minimal `METADATA.md` in the cloned directory:
   ```
   display_name: <repo.name title-cased>
   status: PROTOTYPE
   git_repo: <ssh_url>
   ```
3. Triggers `POST /api/scan` to register the project in GAME
4. Row moves from Unregistered to Registered section

**Button states:**
- Idle: `Make A Project` (outline primary)
- In progress: spinner + `Cloning…` (disabled)
- Success: `✓ Done` (green, briefly), row disappears from this section
- Error: `Failed` (red), inline error message below the row (e.g. SSH auth error, disk full)

**Feasibility note:** Button requires SSH authentication to be configured. The Welcome screen's Git SSH Setup guide covers this. If SSH is not available, the clone step fails and surfaces the error inline — it does not crash the platform.

## Registered Repos Table

Repos where a GAME project exists with a matching `git_repo` URL. Collapsed by default; expands via the section toggle.

| Column | Source | Content |
|--------|--------|---------|
| Status badge | `projects.status` | Lifecycle status pill |
| Project name | `projects.display_name` | Display name |
| Compliance level | `heartbeats.current_state` (compliance type) | IDEA / PROTOTYPE / ACTIVE / PRODUCTION level badge |
| Issues | Validation check count | Number of failing checks at current level |
| Action | — | `Conform` button |

### Conform Button

Runs the equivalent of `bin/project_manager.py update` for this project:

1. Injects latest `CLAUDE_RULES.md` into the project's `AGENTS.md`
2. Copies missing template files (`common.sh`, `common.py`, `index.html`)
3. Adds missing `METADATA.md` default fields
4. Triggers `POST /api/scan` to refresh the project record

**Button states:**
- Idle: `Conform` (outline secondary)
- In progress: spinner + `Updating…` (disabled)
- Success: `✓ Done` (green, briefly), compliance badge refreshes
- Error: `Failed` (red), inline error below the row

**Feasibility note:** Conform requires `SPECIFICATIONS_PATH` to be set in `.env` (so GAME can locate `CLAUDE_RULES.md`). If not configured, the button is disabled with a tooltip: "Set SPECIFICATIONS_PATH in .env to enable."

## No Configuration State

If `GITHUB_USERNAME` is not set in `.env`:

```
┌────────────────────────────────────────────────────────┐
│  GitHub not configured                                  │
│  Set GITHUB_USERNAME in .env to discover repositories. │
│  Optionally add GITHUB_TOKEN for private repos.        │
└────────────────────────────────────────────────────────┘
```

## Data Flow

| Reads | Writes |
|-------|--------|
| GitHub API `GET /users/{GITHUB_USERNAME}/repos` | `git clone` to `~/Projects/{name}` |
| `projects` table (registered projects + git_repo) | New `METADATA.md` in cloned project dir |
| `heartbeats` table (compliance state) | Updated `AGENTS.md`, templates (Conform) |
| `.env` (`GITHUB_USERNAME`, `GITHUB_TOKEN`) | `POST /api/scan` (refresh on success) |

GitHub API calls are server-side (token stays in `.env`, never exposed to browser). Results are cached per session; `Refresh from GitHub` clears the cache.

## Open Questions

- Should `Make A Project` also run `setup.sh` to create a Specifications entry for the new project? Yes — if `SPECIFICATIONS_PATH` is configured, offer an optional "Also create specification directory" checkbox. Default checked.
- Should the screen support GitLab or Bitbucket as an alternative to GitHub? V1 GitHub only. Abstract the provider behind a `GIT_HOST` env var for future extension.
- Should the target clone path be configurable? Always inferred from `PROJECTS_DIR` in `.env`. No additional configuration needed.
- Should Conform show a diff preview of what will change before applying? Yes — show a collapsible diff panel before the operation runs. Blocked until `project_manager.py update --dry-run` output is parseable.
