# CLAUDE_RULES — Integration Rules for Projects

Every rule here is a concrete requirement. If a project follows these rules, the platform orchestrator discovers and integrates it automatically.

---

## Script Rules

**SCRIPT USAGE**: The `bin/` subdirectory contains scripts. Scripts can be bash (`.sh`) or Python (`.py`). Both formats use the same `# CommandCenter Operation` header convention.

**SCRIPT REGISTRATION**: Any bin/ script intended to be run by users must have a `# CommandCenter Operation` marker and a `# Name:` field within the first 20 lines. This is how the orchestration layer discovers it.

Bash example:
```bash
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Port: 8000
# Health: /health
```

Python example:
```python
#!/usr/bin/env python3
# CommandCenter Operation
# Name: Run Pipeline
# Category: build
```

**STANDARD SCRIPT NAMES**: Not enforced, but the orchestrator recognizes these names for default behaviors (service lifecycle, CI triggers, scheduled jobs):

| Script | Purpose | Idempotent? |
|--------|---------|------------|
| `bin/start.sh` | Start the project's services | No — side effects |
| `bin/stop.sh` | Stop the project's services | Yes |
| `bin/build.sh` | Build / compile / package | Yes |
| `bin/test.sh` | Run the test suite | Yes |
| `bin/deploy.sh` | Deploy to a higher environment | No — side effects |
| `bin/daily.sh` | Daily maintenance tasks | Yes — must be safe to re-run |
| `bin/weekly.sh` | Weekly maintenance tasks | Yes — must be safe to re-run |

**SCRIPT PREAMBLE**: All executable scripts must begin with:

```bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
```

Rationale: `set -euo pipefail` catches silent failures. `PROJECT_DIR` ensures paths resolve correctly regardless of where the script is invoked from.

**SCRIPT LOGGING**: All operations log to `logs/{OperationName}_{YYYYMMDD_HHMMSS}.log`:

```bash
OP_NAME="ServiceStart"
LOG_FILE="logs/${OP_NAME}_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs
exec > >(tee -a "$LOG_FILE") 2>&1
```

**STATUS MESSAGES**: Emit `[GAME]` lines so the orchestrator tracks state transitions. These are parsed from log output — they require no other mechanism:

```
[GAME] Service Starting: <name>
[GAME] Service Started: <name>
[GAME] Service Stopped: <name>
```

**EXIT CODES**: 0 = success, non-0 = failure. Long-running services must trap SIGTERM and emit the Stopped message before exiting:

```bash
cleanup() { echo "[GAME] Service Stopped: Service Start"; exit 0; }
trap cleanup SIGTERM SIGINT
```

**IDEMPOTENCY**: `bin/daily.sh` and `bin/weekly.sh` must be safe to run multiple times. They should check state before acting (e.g. skip if already done today). Never assume a clean slate.

**ENVIRONMENT VARIABLES**: If the project requires environment variables, provide a `.env.example` file at the project root listing every required variable with a placeholder value and a comment explaining each one. Never commit a populated `.env` file.

```bash
# .env.example
DATABASE_URL=sqlite:///./data/app.db   # Path to the SQLite database
SECRET_KEY=change-me                    # Flask session encryption key
PORT=8000                               # Port the service listens on
```

---

## Metadata File Rules

**PROJECT METADATA FILE**: Every project has `METADATA.md` at its root. This is the single source of truth for project identity, portfolio card, service links, and discovery metadata. `git_homepage.md` and `Links.md` are superseded by this file.

```
name: MyProject
title: My Project — Short Tagline
description: One to two sentence description of what this project does.
port: 8000
status: ACTIVE
version: 1.0
updated: 2026-03-13
stack: Python/Flask/SQLite
image: images/myproject.webp
health: /health
show_on_homepage: true
tags: web, tool, api
links:
    Production | https://myproject.example.com | Live site
    Docs       | https://docs.example.com       | API documentation
    Staging    | https://staging.example.com    | Pre-production
```

**STATUS VALUES**: Use one of these exact values. The compliance verifier uses status to determine which rules to enforce:

| Status | Meaning | Compliance Level |
|--------|---------|-----------------|
| `IDEA` | Concept only — may have no code | Minimal: METADATA.md name + status |
| `PROTOTYPE` | Proof of concept — not stable | METADATA.md complete + CLAUDE.md stub |
| `ACTIVE` | Actively developed and used | Full script + metadata compliance |
| `PRODUCTION` | Stable, deployed, monitored | All rules including health + git + env |
| `ARCHIVED` | No longer maintained | METADATA.md only |

**METADATA REQUIRED FIELDS** (all statuses): `name`, `status`

**METADATA FULL FIELDS** (ACTIVE and above): `name`, `title`, `description`, `port`, `status`, `version`, `updated`, `stack`, `show_on_homepage`, `tags`

**CLAUDE.MD SECTIONS**: Every project at ACTIVE or above must have `CLAUDE.md` with at minimum: `## Dev Commands`, `## Service Endpoints`, `## Bookmarks`. The orchestrator parses these sections for dashboard links and AI context.

---

## Governance

**HEALTH ENDPOINT**: Declare `# Port:` in a bin/ header to enable health monitoring. Add `# Health: /path` if the health route is not `/`. Also declare `health:` in `METADATA.md` for the same purpose.

**GIT COMPLIANCE** (PRODUCTION only): Git must be initialized, a remote must be configured, working tree should not be persistently dirty. Advisory warnings, not blockers.

**SCRIPTS MUST BE EXECUTABLE**: `chmod +x bin/*.sh`. The orchestrator runs scripts directly — permission errors surface in the process log and are not retried.

**SCRIPTS RUN FROM PROJECT ROOT**: The orchestrator executes bin/ scripts with the project root as the working directory. The preamble enforces this explicitly.

**NO LEGACY CONTRACT FILES**: `git_homepage.md`, `Links.md`, and `STACK.yaml` are replaced by `METADATA.md`. New projects should not create these files. Existing projects should migrate fields to `METADATA.md` and delete the originals.
