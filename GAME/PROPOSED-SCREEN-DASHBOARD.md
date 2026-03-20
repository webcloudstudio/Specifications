# Screen: Dashboard

**The main view.** Shows every discovered project with status, operations, and metadata.

---

## Layout

Full-width project list. One row per project. Nav bar at top 

## Per-Project Row

| Element | Source | Interaction |
|---------|--------|-------------|
| Project name | METADATA.md `display_name` | Click → project detail |
| Status badge | METADATA.md `status` | Display only |
| Namespace badge | METADATA.md `namespace` | Display only |
| Tags | METADATA.md | tags |
| Tag Colors | Database Table | 
| Stack summary | METADATA.md `stack` | Display only |
| Running indicator | Process engine state | Green dot if running |
| Operation buttons | bin/ headers (one per registered script) | Click → run script |
| Quick links | AGENTS.md bookmarks | Click → open URL |
| Settings | Operation Icon | Click -> Open page enabling editing of markdown.md

The Settings Icon is used on several pages

The Initial Columns Status Badge, An Icon indicating Project Type, and Project name are a standard header for several pages

## Project Detail (click into a project)

- All operations with run status
- All endpoints and bookmarks from AGENTS.md
- METADATA.md fields
- AGENTS.md content (expandable)

## Actions

- **Run operation**: Click button → operations engine launches script, button shows running state
- **Stop operation**: Click running button → sends SIGTERM
- **Filter**: By tag, status, namespace, or text search
- **Rescan**: Button to re-scan project directories
- **Push**: Per-project, shown only when unpushed commits exist

## Startup Behavior

Scan reads: METADATA.md, AGENTS.md, and the headers from the files in bin/. Missing files produce compliance gaps, not errors. 
Projects removed from disk are marked ARCHIVED.

## Tag Management

Tag colors stored in a JSON config file in the platform data directory (git committed). Tags assigned from METADATA.md `tags:` field. Inline tag editing from dashboard. Color picker in settings.

## Data Flow

| Reads | Writes |
|-------|--------|
| Project scanner results | Operation launch requests |
| Process engine run states | Git push commands |
| Tag color config | |
