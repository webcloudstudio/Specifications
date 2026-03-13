# Screen: Dashboard

**The main view.** Shows every discovered project with status, operations, and metadata.

---

## Layout

Full-width project list. One row per project. Nav bar at top with running process count and today's AI cost.

## Per-Project Row

| Element | Source | Interaction |
|---------|--------|-------------|
| Project name | METADATA.md `display_name` | Click → project detail |
| Status badge | METADATA.md `status` | Display only |
| Namespace badge | METADATA.md `namespace` | Display only |
| Tags (colored) | METADATA.md `tags` + color config | Click tag → filter |
| Stack summary | METADATA.md `stack` | Display only |
| Running indicator | Process engine state | Green dot if running |
| Operation buttons | bin/ headers (one per registered script) | Click → run script |
| Push button | Git: shown only if unpushed commits | Click → git push |
| Quick links | AGENTS.md bookmarks | Click → open URL |

## Project Detail (click into a project)

- All operations with run status
- All endpoints and bookmarks from AGENTS.md
- Git status: branch, uncommitted count, unpushed count, last commit
- METADATA.md fields
- AGENTS.md content (expandable)

## Actions

- **Run operation**: Click button → operations engine launches script, button shows running state
- **Stop operation**: Click running button → sends SIGTERM
- **Filter**: By tag, status, namespace, or text search
- **Rescan**: Button to re-scan project directories
- **Push**: Per-project, shown only when unpushed commits exist

## Startup Behavior

On web server startup, the platform scans the projects directory **asynchronously**. The dashboard renders immediately with cached data; scan results update the view when complete. This avoids blocking on 30+ `git status` calls.

Scan reads: METADATA.md, AGENTS.md, bin/ headers, git status per project. Missing files produce compliance gaps, not errors. Projects removed from disk are marked inactive.

## Tag Management

Tag colors stored in a JSON config file in the platform data directory (git committed). Tags assigned from METADATA.md `tags:` field. Inline tag editing from dashboard. Color picker in settings.

## Data Flow

| Reads | Writes |
|-------|--------|
| Project scanner results | Operation launch requests |
| Process engine run states | Git push commands |
| Tag color config | |
