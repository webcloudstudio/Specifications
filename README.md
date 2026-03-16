# Specifications

Platform standards and project specifications for AI-orchestrated development.

## Purpose

This repository has two roles:
1. **Managing the core infrastructure of other projects** — distributing CLAUDE_RULES.md, common.sh, and common.py to every project via `bin/create_project.py`.
2. **Acting as a specification repository** — housing detailed specs (GAME/, AlexaPrototypeOne/, stack/) that define what to build and how.

## How It Works

CLAUDE_RULES.md is the distributed behavior contract. Any AI agent given that file plus a project's spec files can build, operate, and maintain the project without additional context. Stack files in `stack/` are prescriptive copy-paste patterns. GAME is the dashboard that discovers and integrates all conforming projects by reading their METADATA.md and AGENTS.md.

## Structure

```
Specifications/
  CLAUDE_RULES.md              Agent behavior contract (distributed to all projects)
  AGENTS.md                    Instructions for agents working in this repo
  templates/                   Canonical common.sh and common.py
  bin/                         Tooling: create_project.py, validate_project.py, generate_prompt.sh, update_projects.sh
  stack/                       Technology reference files (flask.md, sqlite.md, aws-sqs.md, …)
  GAME/                        GAME dashboard spec (by screen: SCREEN-*.md + ARCHITECTURE.md + DATABASE.md)
  AlexaPrototypeOne/           Alexa prototype spec (01-OVERVIEW.md … 11-STARTUP.md)
  archive/                     Superseded documents — not current spec
```

## Quick Start

```bash
# Create a new project
python3 bin/create_project.py <name>

# Push latest CLAUDE_RULES and templates to all set-up projects
bash bin/update_projects.sh

# Validate a project against compliance rules
bash bin/validate_project.sh <name> --verbose

# Build a complete AI build prompt for a project
bash bin/generate_prompt.sh GAME > build-prompt.md

# Scan all projects for compliance
python3 bin/validate_project.py --projects ..

# Regenerate browsable HTML index
bash bin/rebuild_index.sh
```

## Key Conventions

- **METADATA.md** — Line-based `key: value` format (not YAML). Single source of project identity.
- **AGENTS.md** — AI context file. Each project's CLAUDE.md is a bare pointer: `@AGENTS.md`.
- **bin/common.sh / bin/common.py** — Shared helpers distributed from `templates/`. Reads PORT and PROJECT_NAME from METADATA.md.
- **$PROJECTS_DIR/.secrets** — Global API keys. Per-project overrides in `.env`.
- **Version format** — `YYYY-MM-DD.N` (e.g., `2026-03-13.2`).
