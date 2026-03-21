# Engineering Rules Framework

**Type:** Platform Infrastructure  ·  **Status:** Active  ·  **Scope:** All Projects

Global agent behavior contracts, spec templates, and technology stack patterns — an agentic implementation of the GEM Enterprise Management Framework. Distribution/Observability/Control via GAME automation. Copyright © Web Cloud Studio.

## Input File / Directory

| Input File / Directory | Purpose |
|------------------------|---------|
| `BUSINESS_RULES.md` | Engineering Rules Framework — edit here, then run the workflow |
| `CONVERT.md` | Expansion rules: concise spec → implementation-ready spec |
| `DOCUMENTATION_BRANDING.md` | Color palette, typography, and theme standards |
| `stack/` (14 files) | Prescriptive technology patterns (Flask, SQLite, Bootstrap5, …) |
| `spec_template/` (8 files) | New-project scaffolding used by `bin/setup.sh` |
| `templates/` (3 files) | Canonical `common.sh`, `common.py`, `index.html` propagated to all projects |

## Update Cycle

Edit `BUSINESS_RULES.md` → run `bin/generate_claude_rules.sh` → paste AI output over `CLAUDE_RULES.md` → run `GAME/bin/update_projects.sh` to propagate to all projects.

## Output File / Directory

| Output File / Directory | Purpose |
|-------------------------|---------|
| `CLAUDE_RULES.md` | Generated behavior contract injected into every project's `AGENTS.md` |

## Conformity Levels

| Level | Files Required |
|-------|---------------|
| **IDEA** | `METADATA.md` |
| **PROTOTYPE** | + `AGENTS.md`, `CLAUDE.md`, `bin/common.sh`, `bin/common.py` |
| **ACTIVE** | + git initialized, health endpoint configured |
| **PRODUCTION** | + health endpoint responding, all compliance checks pass |
