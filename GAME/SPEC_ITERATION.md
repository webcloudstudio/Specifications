# Spec Iteration Prompt: GAME

**Target gaps:**
- [P0] CLI/Bash Gateway — `bin/game-cli.sh` has no spec file
- [P1] has_tests / has_specs flags — missing from `projects` table schema in DATABASE.md

**Run from:** /mnt/c/Users/barlo/projects/Specifications
**Command:** `claude -p "$(cat GAME/SPEC_ITERATION.md)"`

## What This Prompt Does

This prompt creates `FEATURE-CLI-GATEWAY.md`, which specifies the `bin/game-cli.sh` bash wrapper that makes GAME's REST API usable from other project scripts without raw curl. It also updates `DATABASE.md` to add `has_tests` and `has_specs` columns to the `projects` table schema and Field Source Mapping table — these fields are referenced by `SCREEN-PROJECTS-VALIDATION.md` and `FUNCTIONALITY.md` Flow 1 but have no schema definition. Together these close the two remaining P0/P1 spec gaps.

## Context

### Existing API endpoints (from ARCHITECTURE.md routes table)

| Method | Path | Returns | Purpose |
|--------|------|---------|---------|
| GET | `/api/catalog` | JSON | All projects + their bin/ scripts, ports, health paths |
| POST | `/api/{name}/run/{script}` | JSON 202 + run_id | Fire a bin/ script headlessly |
| GET | `/api/runs/{run_id}` | JSON | Poll run status (running / done / error / stopped) |
| GET | `/api/runs/{run_id}/log` | JSON | Fetch log lines for a run |
| POST | `/api/runs/{run_id}/stop` | JSON | Stop a running operation |
| GET | `/api/health/{name}` | JSON | Current health state for one project |
| POST | `/api/heartbeat` | JSON 200 | Record a heartbeat from a script |
| POST | `/api/events` | JSON 200 | Record an event from a script |

GAME port is resolved from `$GAME_PORT` env var, then `~/.game_port`, then defaults to `5000`.

### Fire-and-poll pattern (from FEATURE-SERVICE-CATALOG.md)

`POST /api/{name}/run/{script}` returns HTTP 202 immediately with:
```json
{"run_id": 42, "status": "running"}
```
The caller must then poll `GET /api/runs/{run_id}` until `status` is not `running`. Log is available at `GET /api/runs/{run_id}/log`.

### has_tests / has_specs (from DATABASE.md Open Questions)

> **`has_tests` flag**: Scanned from `tests/` directory or `bin/test.sh` presence. Add to scanner and `projects` table schema in same pass as `has_specs`.
>
> **`has_specs` flag**: Scanned from `{SPECIFICATIONS_PATH}/{project.name}/` existence. Requires `SPECIFICATIONS_PATH` to be set; defaults to `false` when not configured.

`SPECIFICATIONS_PATH` is already a documented environment variable in ARCHITECTURE.md (absolute path to the Specifications repo).

### Database Field Source Mapping format (from DATABASE.md)

```
| DB Column | Source File / Method | Read On | Notes |
|-----------|---------------------|---------|-------|
| `has_git` | `.git/` directory present | Scan | Boolean flag |
| `has_docs` | Any subdir starting with `doc` containing `index.html` | Scan | Boolean flag; enables Help button |
```

### projects table schema format (from DATABASE.md)

```
| has_git | INTEGER | 0 | .git/ present |
| has_venv | INTEGER | 0 | venv/ present |
| has_docs | INTEGER | 0 | doc[s]/index.htm[l] present |
```

### Script header conventions (from ARCHITECTURE.md / SCRIPTS rules)

Standard script header for a tool in `bin/`:
```bash
#!/bin/bash
# CommandCenter Operation
# Name: {Name String}
# Category: Operations
```

`common.sh` in `bin/` provides: `SCRIPT_NAME`, `PROJECT_DIR`, env loading, venv activation, SIGTERM trap, and standardized exit logging. Scripts should source it with `source "$(cd "$(dirname "$0")" && pwd)/common.sh"`.

## Files to Create

### File 1: FEATURE-CLI-GATEWAY.md

Create `/mnt/c/Users/barlo/projects/Specifications/GAME/FEATURE-CLI-GATEWAY.md`.

This file specifies `bin/game-cli.sh` — a bash script shipped with GAME that wraps the REST API for use from other project scripts, CI hooks, and the terminal without raw curl.

The file must contain these sections in order:

**Header:**
```
# Feature: CLI Gateway

**Version:** 2026-03-26 V1
**Description:** bin/game-cli.sh — bash wrapper for GAME REST API
```

**Overview paragraph:** Explains that `game-cli.sh` is a thin bash client for GAME's REST API. Other project `bin/` scripts can call it to report status, fire operations, or check health without constructing raw curl commands. It resolves the GAME server URL from `$GAME_PORT` env var, then `~/.game_port`, then falls back to port 5000 on localhost.

**Section: Command Reference**

A table with columns: Command | API call | Description, covering these commands:

| Command | API Call | Description |
|---------|----------|-------------|
| `game-cli catalog` | `GET /api/catalog` | Print all projects and their registered scripts as JSON |
| `game-cli catalog --names` | `GET /api/catalog` | Print only project names, one per line |
| `game-cli run {name} {script}` | `POST /api/{name}/run/{script}` | Fire a script and wait for completion; exit 0 on success, 1 on error |
| `game-cli run {name} {script} --no-wait` | `POST /api/{name}/run/{script}` | Fire and return immediately; prints run_id |
| `game-cli status {run_id}` | `GET /api/runs/{run_id}` | Print current status of a run |
| `game-cli log {run_id}` | `GET /api/runs/{run_id}/log` | Print log lines for a run |
| `game-cli stop {run_id}` | `POST /api/runs/{run_id}/stop` | Stop a running operation |
| `game-cli health` | `GET /api/catalog` | Print health state for all projects with ports |
| `game-cli health {name}` | `GET /api/health/{name}` | Print health state for one project |
| `game-cli heartbeat {state} [{msg}]` | `POST /api/heartbeat` | Record a heartbeat from the calling script (state: OK/WARNING/ERROR/CRITICAL) |
| `game-cli event {severity} {msg}` | `POST /api/events` | Record an event (severity: INFORMATION/WARNING/ERROR/CRITICAL) |

**Section: URL Resolution**

Describe how the GAME base URL is resolved in order:
1. `$GAME_URL` env var (full URL, e.g. `http://localhost:5001`) — takes precedence if set
2. `$GAME_PORT` env var → `http://localhost:$GAME_PORT`
3. `~/.game_port` file (single integer) → `http://localhost:{port}`
4. Default: `http://localhost:5000`

**Section: Exit Codes**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error or non-zero script exit |
| 2 | Usage error (wrong arguments) |
| 3 | GAME server unreachable |

**Section: wait-for-completion behaviour**

`game-cli run` without `--no-wait` polls `GET /api/runs/{run_id}` every 2 seconds until status is not `running`. On completion: prints final status and exits with code 0 if status is `done`, 1 if `error` or `stopped`. Timeout: 30 minutes (configurable via `$GAME_CLI_TIMEOUT` env var, default 1800s). Prints a dot `.` to stderr every 10 seconds while waiting so the caller knows it is alive.

**Section: Script Header**

The script must begin with:
```bash
#!/bin/bash
# CommandCenter Operation
# Name: GAME CLI
# Category: Operations
```

It must NOT source `common.sh` — it is a client script that runs in other project contexts, not in the GAME project directory. It uses only standard bash builtins and `curl`.

**Section: Usage in project scripts**

Show a short example of how a project's `bin/daily.sh` calls the CLI:
```bash
# Report status to GAME at start
game-cli heartbeat OK "Daily batch starting"

# Run another project's script and wait
game-cli run SomeProject daily.sh

# Report completion
game-cli heartbeat OK "Daily batch complete"
```

**Section: Installation**

`game-cli.sh` lives in `GAME/bin/game-cli.sh`. To use it from other projects, the user adds `GAME/bin/` to their `PATH` in `.bashrc` or `.zshrc`:
```bash
export PATH="$PATH:/path/to/GAME/bin"
```
Alternatively, `common.sh` in each project may add `$GAME_BIN` to PATH if the `GAME_BIN` env var is set.

**Section: Open Questions**

- Should `game-cli` support JSON output mode (`--json`) for all commands so callers can parse structured data? Default is human-readable; --json flag would return raw API response.
- Should `game-cli heartbeat` auto-detect the calling project name from the current directory's METADATA.md, or require it as an explicit argument?

---

### File 2: DATABASE.md — add has_tests and has_specs to projects table

Do NOT create a new file. Instead, edit the existing file at `/mnt/c/Users/barlo/projects/Specifications/GAME/DATABASE.md`.

Make two changes:

**Change 1 — Field Source Mapping table:** Add these two rows after the `has_claude` row (which reads "CLAUDE.md file present"):

```
| `has_tests` | `tests/` directory or `bin/test.sh` present | Scan | Boolean flag; used by Validation screen |
| `has_specs` | `{SPECIFICATIONS_PATH}/{project.name}/` exists | Scan | Boolean flag; requires SPECIFICATIONS_PATH env var; defaults to 0 if not configured |
```

**Change 2 — projects schema table:** Add these two rows after the `has_docs` row (which reads "doc[s]/index.htm[l] present"):

```
| has_tests | INTEGER | 0 | tests/ directory or bin/test.sh present |
| has_specs | INTEGER | 0 | Matching spec directory exists in SPECIFICATIONS_PATH |
```

**Change 3 — Open Questions section:** Remove the two bullet points about `has_tests` and `has_specs` from the Open Questions section, since they will now be resolved by the schema additions above.

## Conventions

- Follow existing spec file format (see ARCHITECTURE.md, DATABASE.md as reference)
- All spec files end with `## Open Questions`
- Use the same table styles and column layouts as neighboring sections
- FEATURE files describe behavior and contracts; they do not contain implementation code
- Boolean flags in the schema are INTEGER (0/1), not BOOLEAN — match DATABASE.md convention

Write these files to: /mnt/c/Users/barlo/projects/Specifications/GAME/
