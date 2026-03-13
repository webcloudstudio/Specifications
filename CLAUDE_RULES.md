# CLAUDE_RULES — Integration Rules for GAME Projects

Every rule here is a concrete requirement. If a project follows these rules, the GAME platform discovers and integrates it automatically.

---

## Script Rules

**SCRIPT REGISTRATION**: Every bin/ script that should appear as a dashboard button must contain a `# CommandCenter Operation` marker and a `# Name:` field within the first 20 lines.

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Port: 8000
```

**STANDARD SCRIPT NAMES**: Use `bin/start.sh`, `bin/stop.sh`, `bin/build.sh`, `bin/test.sh`, `bin/deploy.sh`. Not enforced, but the platform recognizes these for default behaviors.

**SCRIPT PREAMBLE**: All executable scripts must begin with:

```bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
```

**SCRIPT LOGGING**: All operations log to `logs/{OperationName}_{YYYYMMDD_HHMMSS}.log`. Redirect output with:

```bash
LOG_FILE="logs/${OP_NAME}_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs
exec > >(tee -a "$LOG_FILE") 2>&1
```

**STATUS MESSAGES**: Emit these `[GAME]` lines so the platform can track state transitions:

```
[GAME] Service Starting: <name>
[GAME] Service Started: <name>
[GAME] Service Stopped: <name>
```

**EXIT CODES**: 0 = success, non-0 = failure. Long-running services exit via SIGTERM; add a cleanup trap that emits the Stopped message.

---

## Metadata File Rules

**PROJECT METADATA FILE**: Every project has `METADATA.md` at its root with these fields:

```
name: MyProject
title: My Project — Short Tagline
description: One sentence.
port: 8000
status: active
version: 1.0
updated: 2026-03-13
```

**CLAUDE.MD SECTIONS**: Every project's `CLAUDE.md` must include at minimum: `## Dev Commands`, `## Service Endpoints`, `## Bookmarks`. The platform parses these sections for dashboard links.

**GIT HOMEPAGE**: Every project that should appear on the portfolio has `git_homepage.md` with YAML frontmatter:

```yaml
---
Title: Display Name
Description: What this project does.
Tags: tag1, tag2
Show on Homepage: true
---
```

**LINKS FILE**: Every project has `Links.md` as a markdown table. Each row becomes a quick link in the dashboard.

```markdown
| Name | URL | Notes |
|------|-----|-------|
| Production | https://... | Live site |
```

**STACK FILE**: Every project has `STACK.yaml` declaring `language`, `framework`, and `requires` list.

---

## Governance

**HEALTH ENDPOINT**: Declaring `# Port:` in a bin/ header enables health monitoring. Add `# Health: /health` for a custom path.

**GIT COMPLIANCE**: Projects should have git initialized, a remote configured, and no long-lived dirty state. Advisory only.

**SCRIPTS MUST BE EXECUTABLE**: `chmod +x bin/*.sh`. Run from the project root, not from bin/.
