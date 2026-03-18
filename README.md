# Specifications

Platform standards and project specifications for AI-orchestrated development.

## Purpose

This repository has two distinct roles:

1. **Global standards** (`GLOBAL_RULES/`) — the behavior contract, templates, tech patterns, and branding rules that every project consumes. Distributed to projects via `bin/create_project.py` and `bin/update_projects.sh`.
2. **Project specifications** (`GAME/`, `AlexaPrototypeOne/`, etc.) — detailed specs for individual projects, organized by screen/component/architecture.

Tooling in `bin/` enforces standards: creating projects, validating compliance, propagating rule changes, and generating build prompts. These are **specification-conforming operations** — they verify and shape projects against the global rules.

**Operational tasks** (pushing git repos, starting services, monitoring health) live in the GAME project, not here. GAME is the runtime dashboard; this repo is the standards authority.

## How It Works

`GLOBAL_RULES/CLAUDE_RULES.md` is the distributed behavior contract. Any AI agent given that file plus a project's spec files can build, operate, and maintain the project without additional context. Stack files in `GLOBAL_RULES/stack/` are prescriptive copy-paste patterns. GAME discovers and integrates all conforming projects by reading their METADATA.md and AGENTS.md.

## Structure

```
Specifications/
  GLOBAL_RULES/                    Global standards (distributed to all projects)
    CLAUDE_RULES.md                Agent behavior contract
    DOCUMENTATION_BRANDING.md      Documentation theming and color system
    stack/                         Prescriptive tech patterns (flask.md, sqlite.md, ...)
    templates/                     Canonical common.sh and common.py
    gitignore                      Standard .gitignore for new projects

  bin/                             Specification tooling
    create_project.py              Scaffold new projects / update existing ones
    validate_project.py            Compliance checker per status level
    update_projects.sh             Push latest rules + templates to all set-up projects
    generate_prompt.sh             Build complete AI build prompt from specs + stack
    rebuild_index.sh               Regenerate browsable HTML indexes
    build_documentation.sh/.py     Generate doc/ output

  GAME/                            GAME project spec (SCREEN-*.md + ARCHITECTURE + DATABASE)
  AlexaPrototypeOne/               Alexa prototype spec (01-OVERVIEW.md ... 11-STARTUP.md)
  archive/                         Superseded documents — not current spec
  doc/                             Generated documentation output
```

## Quick Start

```bash
# Create a new project
python3 bin/create_project.py <name>

# Push latest rules and templates to all set-up projects
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
- **GLOBAL_RULES/templates/** — Canonical `common.sh` and `common.py` distributed to all projects. Reads PORT and PROJECT_NAME from METADATA.md.
- **$PROJECTS_DIR/.secrets** — Global API keys. Per-project overrides in `.env`.
- **Version format** — `YYYY-MM-DD.N` (e.g., `2026-03-13.2`).
