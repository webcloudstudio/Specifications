# Project Scanner

`scanner.py` — Discovers projects from the filesystem and syncs to the database.

## Overview

The scanner reads a configured `PROJECTS_DIR` directory, detects attributes for each subdirectory, and upserts them into the database. It runs automatically at startup and on-demand via the Refresh button.

## Discovery Algorithm

```
scan_projects(projects_dir):
    for each subdirectory in projects_dir (sorted):
        skip: .git, __pycache__, hidden dirs (starting with .)
        detect_project(name, path)  →  info dict
        upsert_project(info)        →  insert or update DB
    return discovered list
```

## Detection Logic (`detect_project`)

### Tech Stack Detection (priority order)
1. `manage.py` exists → `django` (port 8000)
2. `astro.config.mjs` or `astro.config.ts` → `astro`
3. `app.py` exists → `flask` (port parsed from `app.run(port=N)`)
4. `package.json` exists → `node`
5. `setup.py` or `pyproject.toml` → `python`

### Project Type Detection
- Default: `software`
- If no tech stack detected AND directory contains `chapters/`, `manuscript/`, `Book/`, or `drafts/` → `book`

### Filesystem Flags
- `has_git` — `.git/` directory exists
- `has_venv` — `venv/` or `.venv/` directory exists
- `has_node` — `node_modules/` directory exists
- `has_claude` — `CLAUDE.md` file exists
- `has_start_sh`, `has_build_sh`, `has_deploy_sh`, `has_test_sh` — standard script detection

### Git Operations (Pure Python, No Subprocess)
- **Remote URL**: Parsed from `.git/config` using `configparser`
- **Unpushed Count**: BFS walk of commit graph comparing local HEAD to `refs/remotes/origin/{branch}`
  - Reads loose objects via `zlib.decompress`
  - Falls back to `packed-refs` for ref resolution
  - Safety cap at 50 commits

### Metadata File Parsing

#### `Links.md` — Project endpoint links
```markdown
| Label | URL |
|-------|-----|
| Local Dev | http://localhost:8000 |
| Production | https://example.com |
```
Returns: `[{label: "Local Dev", url: "http://..."}]`

#### `git_homepage.md` — GitHub homepage card metadata
```markdown
| Field | Value |
|-------|-------|
| Title | My Project |
| Description | Project description |
| Card Type | Software |
| Card URL | https://example.com |
| Tags | tag1, tag2 |
| Show on Homepage | true |
```
Returns: `{card_title, card_desc, card_type, card_url, card_tags, card_show}`

#### `CLAUDE.md` — Bookmarks extraction
Parses `## Bookmarks` section for `### Group` headings and `- [Title](URL)` links.

### `bin/` Directory Operations
Scans `bin/*.sh` files for `CommandCenter Operation` headers:
```bash
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Port: 8000
```
Returns: `[{name, port, script_path, script_name}]`

## Title Generation

Directory names are converted to display titles via `camel_to_title()`:
- `HerpesHearts` → `Herpes Hearts`
- `command_center` → `Command Center`
- `My_Github` → `My Github`

## Upsert Logic (`upsert_project`)

### Existing project (update):
- **Always overwrite**: title (from dir name), has_git/venv/node/claude, card_* fields (from git_homepage.md)
- **Always overwrite in extra**: links, bookmarks, unpushed, has_*_sh flags (live data)
- **Never overwrite**: user-edited extra fields (workflow, etc.) — only set if empty
- **Sync operations**: Delete bin/ and git ops, re-seed from current filesystem

### New project (insert):
- Insert with all detected fields
- Seed operations from bin/ scripts and git status

## Operation Seeding (`_seed_operations`)

1. Delete all existing operations where `cmd LIKE 'bin/%'` or `name = 'Git Push'`
2. Insert one operation per `bin/*.sh` file with `CommandCenter Operation` header
   - Category: `local`
   - Cmd: `bin/{script_name}`
   - Includes `default_port` if specified in header
3. If project has git: insert `Git Push` operation (category: `remote`, cmd: `git push`)

## Orphan Cleanup (`cleanup_orphaned`)

Removes DB entries whose `name` doesn't match any actual directory in `PROJECTS_DIR`. Uses `os.listdir()` for case-sensitive comparison (critical on WSL where `os.path.isdir()` is case-insensitive). Cascades: deletes operations and op_runs for orphaned projects.
