# CLAUDE_RULES_START

# DEFAULT DEVELOPMENT RULES

**Version:** 2026-03-15.1

Full specification: `Specifications/CLAUDE_RULES.md`. This condensed version covers agent behavior only.

---

## Git Workflow

1. Commit immediately after completing a task with no errors.
2. Commit messages: descriptive text, no "Claude"/"Anthropic"/"AI" mentions.
3. DO NOT push — local commits only.
4. NO co-authored-by lines.

Web server changes: print "No restart needed — browser refresh is enough." (templates/CSS/static only) or "Restart required — `./bin/start.sh`." (Python/JS server files).

---

## Project Layout

```
ProjectName/
  METADATA.md       Identity (name, port, status, stack, etc.)
  AGENTS.md         AI context: dev commands, endpoints, architecture
  CLAUDE.md         Contains only: @AGENTS.md
  .env.sample       Required env vars (committed)
  .env              Actual env vars (never committed)
  bin/              All executable scripts
    common.sh       Shared functions — sourced by all scripts
  doc/              Generated documentation
  logs/             Log files (gitignored)
  data/             Persistent data
  tests/            Test suite
```

---

## Bash Scripts (`bin/`)

All scripts begin with this preamble:

```bash
#!/bin/bash
# CommandCenter Operation
set -euo pipefail
SCRIPT_NAME="$(basename "$0" .sh)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
source "$SCRIPT_DIR/common.sh"
LOG_FILE="logs/${PROJECT_NAME}_${SCRIPT_NAME}_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs
exec > >(tee -a "$LOG_FILE") 2>&1
echo "[$PROJECT_NAME] Starting: $SCRIPT_NAME"
```

- Use Linux line endings (no `\r`). Run `chmod +x bin/*.sh`.
- Emit `[$PROJECT_NAME] Started/Stopped/Error: $SCRIPT_NAME` for platform parsing.
- Long-running services: `trap 'echo "[$PROJECT_NAME] Stopped: $SCRIPT_NAME"; exit 0' SIGTERM SIGINT`

`bin/common.sh` reads METADATA.md and activates venv:

```bash
#!/bin/bash
get_metadata() { grep "^${1}:" "$PROJECT_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//"; }
PROJECT_NAME="$(get_metadata "name")"
PORT="$(get_metadata "port")"
[ -d "$PROJECT_DIR/venv" ] && source "$PROJECT_DIR/venv/bin/activate" 2>/dev/null
[ -f "$PROJECTS_DIR/.secrets" ] && set -a && source "$PROJECTS_DIR/.secrets" && set +a
[ -f "$PROJECT_DIR/.env" ] && set -a && source "$PROJECT_DIR/.env" && set +a
```

---

## METADATA.md

Key-value format (not YAML). Minimum required fields:

```
name: MyProject
display_name: My Project
port: 8000
status: ACTIVE
stack: Python,Flask,SQLite
short_description: One sentence.
health: /health
```

Status levels: `IDEA` → `PROTOTYPE` → `ACTIVE` → `PRODUCTION` → `ARCHIVED`

---

## AGENTS.md Required Sections (ACTIVE+)

```markdown
## Dev Commands
- Start: `./bin/start.sh`
- Stop: `./bin/stop.sh`
- Test: `./bin/test.sh`

## Service Endpoints
- Local: http://localhost:PORT

## Bookmarks
- [Documentation](doc/index.html)
```

# CLAUDE_RULES_END
