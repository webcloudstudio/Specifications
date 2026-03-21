# Engineering Rules Framework

**Type:** Platform Infrastructure  ·  **Status:** Active  ·  **Scope:** All Projects

Global agent behavior contracts, spec templates, and technology stack patterns distributed to every project. AI agents read these rules — projects do not define their own behavior contracts.

## Contents

| File / Dir | Purpose |
|-----------|---------|
| `BUSINESS_RULES.md` | Source for agent behavior — edit here, then regenerate `CLAUDE_RULES.md` |
| `CLAUDE_RULES.md` | Generated behavior contract injected into every project's `AGENTS.md` |
| `CONVERT.md` | Expansion rules: concise spec → implementation-ready spec |
| `DOCUMENTATION_BRANDING.md` | Color palette, typography, and theme standards |
| `stack/` (14 files) | Prescriptive technology patterns (Flask, SQLite, Bootstrap5, …) |
| `spec_template/` (8 files) | New-project scaffolding used by `setup.sh` |
| `templates/` (3 files) | Canonical `common.sh`, `common.py`, `index.html` propagated to all projects |

## Update Cycle

Edit `BUSINESS_RULES.md` → run `generate_claude_rules.sh` → paste AI output over `CLAUDE_RULES.md` → run `update_projects.sh` to propagate to all projects.

## Conformity Levels

| Level | Files Required |
|-------|---------------|
| **IDEA** | `METADATA.md` |
| **PROTOTYPE** | + `AGENTS.md`, `CLAUDE.md`, `bin/common.sh`, `bin/common.py` |
| **ACTIVE** | + git initialized, health endpoint configured |
| **PRODUCTION** | + health endpoint responding, all compliance checks pass |
