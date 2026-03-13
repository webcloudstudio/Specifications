# CLAUDE_RULES — Integration Rules for Projects

Every rule here is a concrete requirement. If a project follows these rules, the platform discovers and integrates it automatically. Rules are grouped by domain with completeness scores.

---

## Script Rules (90% complete)

**SCRIPT LOCATION**: All executable scripts live in `bin/`. Bash (`.sh`) or Python (`.py`).

**SCRIPT REGISTRATION**: Scripts intended for user execution must have a `# CommandCenter Operation` marker and `# Name:` field within the first 20 lines. This is how the platform discovers operations.

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Port: 8000
# Health: /health
# Schedule: daily 02:00
# MaxMemory: 512M
# Timeout: 300
```

Optional headers: `Port` (enables health monitoring), `Health` (custom health path), `Category` (grouping), `Schedule` (cron), `MaxMemory` (resource limit), `Timeout` (max seconds).

**STANDARD SCRIPTS**: Not enforced, but recognized for default behaviors:

| Script | Purpose | Idempotent? |
|--------|---------|------------|
| `bin/start.sh` | Start services | No |
| `bin/stop.sh` | Stop services | Yes |
| `bin/build.sh` | Build / compile / package | Yes |
| `bin/test.sh` | Run tests | Yes |
| `bin/deploy.sh` | Deploy to environment | No |
| `bin/daily.sh` | Daily maintenance | Yes |
| `bin/weekly.sh` | Weekly maintenance | Yes |

**SCRIPT PREAMBLE**: All bash scripts must begin with:

```bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
```

**SCRIPT LOGGING**: All operations log to `logs/{OperationName}_{YYYYMMDD_HHMMSS}.log`:

```bash
OP_NAME="ServiceStart"
LOG_FILE="logs/${OP_NAME}_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs
exec > >(tee -a "$LOG_FILE") 2>&1
```

**STATUS MESSAGES**: Emit `[GAME]` lines for state tracking. Parsed from log output:

```
[GAME] Service Starting: <name>
[GAME] Service Started: <name>
[GAME] Service Stopped: <name>
[GAME] Error: <name>: <message>
```

**EXIT CODES**: 0 = success, non-0 = failure. Long-running services trap SIGTERM:

```bash
cleanup() { echo "[GAME] Service Stopped: Service Start"; exit 0; }
trap cleanup SIGTERM SIGINT
```

**IDEMPOTENCY**: `daily.sh` and `weekly.sh` must be safe to re-run. Check state before acting.

**PERMISSIONS**: `chmod +x bin/*.sh`. Permission errors are not retried.

**WORKING DIRECTORY**: Scripts run from project root. The preamble enforces this.

---

## Metadata Rules (85% complete)

**METADATA.md**: Every project has `METADATA.md` at its root. Single source of truth for identity, portfolio, links, and discovery.

```yaml
name: MyProject
title: My Project — Short Tagline
description: One to two sentence description.
port: 8000
status: ACTIVE
version: 1.0
updated: 2026-03-13
stack: Python/Flask/SQLite
image: images/myproject.webp
health: /health
show_on_homepage: true
tags: web, tool, api
desired_state: running
namespace: production
links:
    Production | https://myproject.example.com | Live site
    Docs       | https://docs.example.com       | API documentation
```

**STATUS VALUES**: Determines which rules are enforced:

| Status | Meaning | Required Rules |
|--------|---------|---------------|
| `IDEA` | Concept only | METADATA.md: name + status |
| `PROTOTYPE` | Proof of concept | METADATA.md complete + CLAUDE.md stub |
| `ACTIVE` | Developed and used | Full script + metadata compliance |
| `PRODUCTION` | Stable, deployed | All rules including health + git + env |
| `ARCHIVED` | No longer maintained | METADATA.md only |

**REQUIRED FIELDS** (all statuses): `name`, `status`

**FULL FIELDS** (ACTIVE+): `name`, `title`, `description`, `port`, `status`, `version`, `updated`, `stack`, `show_on_homepage`, `tags`

**CLAUDE.md**: Every ACTIVE+ project must have `CLAUDE.md` with at minimum: `## Dev Commands`, `## Service Endpoints`, `## Bookmarks`.

**ENVIRONMENT**: If the project requires env vars, provide `.env.example` at the project root with every required variable, placeholder value, and comment. Never commit a populated `.env`.

```bash
# .env.example
DATABASE_URL=sqlite:///./data/app.db   # Path to the SQLite database
SECRET_KEY=change-me                    # Flask session encryption key
PORT=8000                               # Port the service listens on
```

**NO LEGACY FILES**: `git_homepage.md`, `Links.md`, and `STACK.yaml` are replaced by `METADATA.md`. New projects must not create these files.

---

## Governance Rules (65% complete)

**HEALTH ENDPOINT**: Declare `# Port:` in bin/ header and `health:` in METADATA.md. Default path is `/health`.

**GIT COMPLIANCE** (PRODUCTION only): Git initialized, remote configured, working tree not persistently dirty. Advisory, not blocking.

**COMPLIANCE VERIFICATION**: `verify.py` scans all projects and reports per-project pass/fail calibrated to declared status. Run: `python3 verify.py --projects /path/to/projects`.

---

## Roadmap

Features not yet covered by rules but planned:

| Feature | Rule Needed | Priority |
|---------|------------|----------|
| Scheduling | `# Schedule:` header parsing | High |
| Job Pipelines | Pipeline YAML format definition | Medium |
| Resource Limits | `# MaxMemory:` / `# Timeout:` enforcement | Medium |
| Secrets Management | Secrets store contract | Medium |
| Desired State | `desired_state:` in METADATA.md | Low |
| Namespace Isolation | `namespace:` in METADATA.md | Low |
| Service Discovery | `@project-name/api` resolution | Low |
| Event Log | Event format and retention rules | Low |
