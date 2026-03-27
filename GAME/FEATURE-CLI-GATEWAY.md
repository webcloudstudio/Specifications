# Feature: CLI Gateway

**Version:** 2026-03-26 V1
**Description:** bin/game-cli.sh — bash wrapper for GAME REST API

`game-cli.sh` is a thin bash client for GAME's REST API. Other project `bin/` scripts can call it to report status, fire operations, or check health without constructing raw curl commands. It resolves the GAME server URL from `$GAME_URL` env var, then `$GAME_PORT`, then `~/.game_port`, then falls back to port 5000 on localhost.

---

## Command Reference

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

---

## URL Resolution

The GAME base URL is resolved in this order:

1. `$GAME_URL` env var (full URL, e.g. `http://localhost:5001`) — takes precedence if set
2. `$GAME_PORT` env var → `http://localhost:$GAME_PORT`
3. `~/.game_port` file (single integer) → `http://localhost:{port}`
4. Default: `http://localhost:5000`

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error or non-zero script exit |
| 2 | Usage error (wrong arguments) |
| 3 | GAME server unreachable |

---

## Wait-for-Completion Behaviour

`game-cli run` without `--no-wait` polls `GET /api/runs/{run_id}` every 2 seconds until status is not `running`. On completion:

- Prints final status
- Exits 0 if status is `done`
- Exits 1 if status is `error` or `stopped`

Timeout: 30 minutes, configurable via `$GAME_CLI_TIMEOUT` env var (default: 1800 seconds). Prints a dot `.` to stderr every 10 seconds while waiting so the caller knows it is alive.

---

## Script Header

The script must begin with:

```bash
#!/bin/bash
# CommandCenter Operation
# Name: GAME CLI
# Category: Operations
```

`game-cli.sh` must **not** source `common.sh` — it is a client script that runs in other project contexts, not in the GAME project directory. It uses only standard bash builtins and `curl`.

---

## Usage in Project Scripts

A project's `bin/daily.sh` calling the CLI:

```bash
# Report status to GAME at start
game-cli heartbeat OK "Daily batch starting"

# Run another project's script and wait
game-cli run SomeProject daily.sh

# Report completion
game-cli heartbeat OK "Daily batch complete"
```

---

## Installation

`game-cli.sh` lives in `GAME/bin/game-cli.sh`. To use it from other projects, add `GAME/bin/` to `PATH` in `.bashrc` or `.zshrc`:

```bash
export PATH="$PATH:/path/to/GAME/bin"
```

Alternatively, `common.sh` in each project may add `$GAME_BIN` to PATH if the `GAME_BIN` env var is set.

---

## Open Questions

- Should `game-cli` support a JSON output mode (`--json`) for all commands so callers can parse structured data? Default is human-readable; `--json` would return the raw API response.
- Should `game-cli heartbeat` auto-detect the calling project name from the current directory's `METADATA.md`, or require it as an explicit argument?
