# Business Rules

**Version:** 20260323 V2
**Description:** Source for CLAUDE_RULES.md — edit here, then regenerate via `bin/summarize_rules.sh`.

---

## Conformity Levels

Conformity levels define what a project must have before it is treated as ready for a given stage.
`bin/validate.sh` enforces the level matching the project's `status:` field.

### IDEA
Requires: METADATA.md with `name` and `status: IDEA`

### PROTOTYPE
Requires: IDEA + all METADATA required fields + AGENTS.md with required sections

### ACTIVE
Requires: PROTOTYPE + tests exist (`tests/` directory) + `docs/` exists

### PRODUCTION
Requires: ACTIVE + `bin/deploy.sh` exists + `health` endpoint declared in METADATA.md

### Documentation Directory
All projects MUST use `docs/` (not `doc/`) for generated documentation. There is no `doc/` directory.

### ARCHIVED
No enforcement — read-only historical record.

---

## Git

### GIT_COMMIT_IMMEDIATELY
**Scope:** git
**Applies at:** PROTOTYPE
**Requirement:** Commit immediately after completing a task with no errors.
**Rationale:** Prevents loss of working increments between agent operations. Keeping commits small and frequent makes it easy to identify regressions and roll back individual changes.
**Rule text:**
Commit immediately after completing a task with no errors.

### GIT_COMMIT_MESSAGE
**Scope:** git
**Applies at:** PROTOTYPE
**Requirement:** Commit messages must be descriptive text with no "Claude", "Anthropic", or "AI" mentions.
**Rationale:** Commit history is read by humans and tools alike. Attribution noise degrades readability and makes automated parsing harder.
**Rule text:**
Commit messages: descriptive text, no "Claude"/"Anthropic"/"AI" mentions.

### GIT_NO_PUSH
**Scope:** git
**Applies at:** PROTOTYPE
**Requirement:** Do not push to remote — local commits only.
**Rationale:** Push is a destructive, shared-state operation. The user controls when code reaches the remote.
**Rule text:**
DO NOT push — local commits only.

### GIT_NO_COAUTHOR
**Scope:** git
**Applies at:** PROTOTYPE
**Requirement:** No co-authored-by lines in commit messages.
**Rationale:** Co-authored-by lines add noise and may expose agent identity in ways the user has not opted into.
**Rule text:**
NO co-authored-by lines.

### GIT_RESTART_NOTICE
**Scope:** git
**Applies at:** PROTOTYPE
**Requirement:** After any commit that changes a web server project, print whether a restart is required.
**Rationale:** Developers need to know immediately whether they must restart a service or can simply refresh. Getting this wrong wastes time or causes confusion.
**Rule text:**
Web server changes: print "No restart needed — browser refresh is enough." (templates/CSS/static only) or "Restart required — `./bin/start.sh`." (Python/JS server files).

---

## Project Layout

### PROJECT_LAYOUT
**Scope:** project-layout
**Applies at:** PROTOTYPE
**Requirement:** Every project must follow the standard directory structure.
**Rationale:** Uniform layout lets agents, scripts, and the GAME platform find files without configuration.
**Rule text:**

```
ProjectName/
  METADATA.md       Identity (name, port, status, stack, etc.)
  AGENTS.md         AI context: dev commands, endpoints, architecture
  CLAUDE.md         Contains only: @AGENTS.md
  .env.sample       Required env vars (committed)
  .env              Actual env vars (never committed)
  bin/              All executable scripts
    common.sh       Shared functions — sourced by all bash scripts
    common.py       Shared OperationContext — imported by Python scripts
  docs/             Generated documentation
  logs/             Log files (gitignored)
  data/             Persistent data
  tests/            Test suite
```

---

## Scripts

### SCRIPTS_IN_BIN
**Scope:** scripts
**Applies at:** PROTOTYPE
**Requirement:** All scripts live in `bin/` — bash (`.sh`) or Python (`.py`).
**Rationale:** A single well-known location makes scripts discoverable by agents and the GAME platform.
**Rule text:**
All scripts live in `bin/` — bash (`.sh`) or Python (`.py`). The `# CommandCenter Operation` marker in the first 20 lines registers a script with the platform.

**Standard script names** (only create what the project needs):

| Script | Purpose | Name String
|--------|---------|
| `bin/start.sh` | Start service — service projects only | Stop Service |
| `bin/stop.sh` | Stop service — service projects only | Stop Service |
| `bin/build.sh` | Build / compile / package | Build |
| `bin/daily.sh` | Daily maintenance | Daily Batch |
| `bin/weekly.sh` | Weekly maintenance | Weekly Batch |
| `bin/build_documentation.sh` | Generate docs/ output | Build Doc |
| `bin/deploy.sh` | Deploy to environment | Deploy |
| `bin/test.sh` | Run project tests — stub is acceptable | Test |

If the script name matches a Standard Script Name the following header should exist with a Name: field matching the Name String.  If possible
these should be the first lines of the file and there should be no other "# Name:" or "# Category:" fields.

#!/bin/bash
# CommandCenter Operation
# Name: {Name String}
# Category: Operations

### HAS_TEST_SCRIPT
**Scope:** scripts
**Applies at:** ACTIVE
**Requirement:** Every project must have `bin/test.sh`.
**Rationale:** A test entry point is required for CI and GAME to validate project health, even if initially empty.
**Rule text:**
All projects must have `bin/test.sh`. A minimal stub (`#!/bin/bash` + `exit 0`) is sufficient until real tests exist. The script must exist — GAME and the validation system check for it.

### SCRIPTS_BASH_PATTERN
**Scope:** scripts
**Applies at:** PROTOTYPE
**Requirement:** Bash scripts must source `common.sh` before adding functionality.
**Rationale:** `common.sh` provides consistent path setup, env loading, logging, and signal handling — reinventing these per-script creates drift.
**Rule text:**

```bash
#!/bin/bash
# CommandCenter Operation
# Category: service
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

# your start command — use $PORT for the service port
# e.g. Flask: export FLASK_DEBUG=1 && flask run --port "$PORT"
```

`common.sh` handles: `SCRIPT_NAME`, `PROJECT_DIR`, `cd`, `PROJECT_NAME`, `PORT`, venv activation, `.secrets`/`.env` loading, timestamped log file, SIGTERM trap, standardized exit logging, and the `[$PROJECT_NAME] Starting:` message. Use `$PORT` as the service port — never hardcode a port number. Override the trap after sourcing if the script needs custom cleanup.

### SCRIPTS_PYTHON_PATTERN
**Scope:** scripts
**Applies at:** PROTOTYPE
**Requirement:** Python scripts must import `common.py` before adding functionality.
**Rationale:** `common.py` provides the same operational guarantees as `common.sh` for Python scripts.
**Rule text:**

```python
#!/usr/bin/env python3
# CommandCenter Operation
# Category: maintenance
import sys, os; sys.path.insert(0, os.path.dirname(__file__)); from common import op

def main(ctx):
    # ctx.project_name, ctx.port, ctx.logger available — use ctx.port as the service port
    pass

if __name__ == '__main__':
    op(__file__).run(main)
```

`op(__file__).run(main)` handles the same concerns as `common.sh`: path setup, METADATA.md parsing, env loading, logging, SIGTERM, and standardized exit logging. On clean exit it logs `EXIT - OK`; on unhandled exception it logs `EXIT - ERROR: <message>` and exits 1.

Use Linux line endings (no `\r`). Run `chmod +x bin/*.sh`.

### SCRIPTS_EXIT_LOGGING
**Scope:** scripts
**Applies at:** PROTOTYPE
**Requirement:** Every script must log a standardized exit line on completion.
**Rationale:** The log ingestor and operators need a single unambiguous token to know whether a script succeeded or failed without parsing arbitrary output.
**Rule text:**
Every script must emit one of these lines as its final log output:

```
[ProjectName] EXIT - OK
[ProjectName] EXIT - ERROR: <reason>
```

`common.sh` emits these automatically via the `EXIT` trap (code 0 → OK; non-zero → ERROR with code).
`common.py`'s `run()` emits them automatically: clean exit → OK; unhandled exception → ERROR with message.
Do not print additional "done" or "completed" lines after these — they are the canonical terminal tokens.

### SCRIPTS_HEARTBEAT
**Scope:** scripts
**Applies at:** PROTOTYPE
**Requirement:** Scripts may report operational state and log events to GAME using `heartbeat()` and `log_event()`.
**Rationale:** Centralised health state and event history in GAME enables monitoring across all projects without per-project instrumentation.
**Rule text:**
Both `common.sh` and `common.py` provide two helpers:

**Bash:**
```bash
heartbeat <state> [message]
# state: OK | WARNING | ERROR | CRITICAL
# Resolves GAME port from $GAME_PORT env var, then ~/.game_port, then 5000.
# Silent no-op if GAME is unreachable — never aborts the script.

log_event <severity> <message>
# severity: INFORMATION | WARNING | ERROR | CRITICAL
```

**Python:**
```python
ctx.heartbeat(state, message='')
ctx.log_event(severity, message)
# state / severity: OK WARNING ERROR CRITICAL (heartbeat); INFORMATION WARNING ERROR CRITICAL (log_event)
# Silent no-op if GAME unreachable.
```

Call `heartbeat('OK')` at script start after `run()` if using long-running loops. Call `heartbeat('ERROR', msg)` before exiting on known failure conditions. These calls are advisory — never gate script logic on their success.

---

## METADATA.md

### METADATA_FORMAT
**Scope:** metadata
**Applies at:** IDEA
**Requirement:** METADATA.md must use the key-value format with required fields.
**Rationale:** METADATA.md is the authoritative identity source for GAME platform discovery. Field names and format must be stable so scripts can parse them without configuration.
**Rule text:**
**Authoritative source for project identity.** Always read `name`, `display_name`, `short_description`, and `git_repo` from this file — never infer them from directory names. Present in every set-up project.

Key-value format (not YAML):

```
# AUTHORITATIVE PROJECT METADATA - THE FIELDS IN THIS FILE SHOULD BE CURRENT

name: MyProject                              # machine slug, matches directory name
display_name: My Project                     # human-readable name for UI/display
git_repo: https://github.com/org/MyProject   # full HTTPS URL, for links only
port: 8000                                   # omit if not a service
short_description: One sentence.             # shown in dashboards and indexes
health: /health                              # omit if not a service
status: PROTOTYPE                            # IDEA|PROTOTYPE|ACTIVE|PRODUCTION|ARCHIVED
stack: Python/Flask/SQLite                   # slash-separated, used by generate_prompt.sh
version: 2026-03-16.1                        # YYYY-MM-DD.N, increment on releases
updated: 20260316_120000                     # set automatically by platform scripts
```

`port`, `health`, `stack`, and `status` are platform fields — managed by GAME and platform scripts, not needed for day-to-day agent work. `git_repo` SSH remotes are normalised to HTTPS automatically.

---

## AGENTS.md

### AGENTS_REQUIRED_SECTIONS
**Scope:** agents-md
**Applies at:** PROTOTYPE
**Requirement:** AGENTS.md must include Dev Commands, Service Endpoints (if service), and Bookmarks sections.
**Rationale:** Agents discover how to operate a project by reading AGENTS.md. Missing sections mean agents must guess or ask, which is unreliable.
**Rule text:**

```markdown
## Dev Commands
- Start: `./bin/start.sh`   # service projects only
- Stop: `./bin/stop.sh`     # service projects only
- Test: `./bin/test.sh`     # if tests exist

## Service Endpoints        # omit if not a service
- Local: http://localhost:PORT

## Bookmarks
- [Documentation](docs/index.html)
```

Only include commands and endpoints that actually exist for the project.

---

## Open Questions
