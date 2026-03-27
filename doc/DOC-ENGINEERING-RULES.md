# Engineering Rules Framework

**Type:** Platform Infrastructure  ·  **Status:** Active  ·  **Scope:** All Projects

Global agent behavior contracts, spec templates, and technology stack patterns — an agentic implementation of the GEM Enterprise Management Framework. Distribution/Observability/Control via Prototyper automation. Copyright © Web Cloud Studio.

## Input File / Directory

| Input File / Directory | Purpose |
|------------------------|---------|
| `BUSINESS_RULES.md` | Engineering Rules Framework — edit here, then run the workflow |
| `ONESHOT_BUILD_RULES.md` | Build and expansion rules: concise spec → implementation-ready spec |
| `DOCUMENTATION_BRANDING.md` | Color palette, typography, and theme standards |
| `stack/` | Prescriptive technology patterns (Flask, SQLite, Bootstrap5, …) |
| `spec_template/`  | New-project scaffolding used by `bin/setup.sh` |
| `templates/` | Canonical `common.sh`, `common.py`, `index.html` propagated to all code projects |

## Update Cycle

Edit `BUSINESS_RULES.md` → run `bin/summarize_rules.sh` → paste AI output over `CLAUDE_RULES.md` → run `GAME/bin/update_projects.sh` to propagate to all projects.

## Output File / Directory

| Output File / Directory | Purpose |
|-------------------------|---------|
| `CLAUDE_RULES.md` | Generated behavior contract injected into every project's `AGENTS.md` |
| `CLAUDE_PROTOTYPE.md` | Prototype iteration rules injected into every prototype's `AGENTS.md` |

## Conformity Levels

| Level | Files Required |
|-------|---------------|
| **IDEA** | `METADATA.md` |
| **PROTOTYPE** | + `AGENTS.md`, `CLAUDE.md`, `bin/common.sh`, `bin/common.py` |
| **ACTIVE** | + git initialized, health endpoint configured |
| **PRODUCTION** | + health endpoint responding, all compliance checks pass |

## bin/ProjectValidate.sh

Verifies a promoted code project against CLAUDE_RULES compliance. Shows the project's current conformity level, which checks pass or fail at each level, and a preview of what the next level requires.

Operates on promoted code projects only — not Specification directories inside this repo.

```bash
# Verify by project name (looks up under ../projects/)
bash bin/ProjectValidate.sh <project-name>

# Verify by absolute path
bash bin/ProjectValidate.sh /abs/path/to/project

# Verbose output — shows all checks, not just failures
bash bin/ProjectValidate.sh <project-name> --verbose
```

Output groups checks by conformity level (IDEA → PROTOTYPE → ACTIVE → PRODUCTION), marks each check PASS or FAIL, and indicates where the project currently sits. Thin wrapper over `bin/project_manager.py verify`.

## ProjectUpdate.sh

Updates a promoted code project with the latest rules and templates from this repository. Injects the current `CLAUDE_RULES.md` into the project's `AGENTS.md`, copies canonical templates (`common.sh`, `common.py`, `index.html`), and adds any missing `METADATA.md` default fields.

The project must already have a `CLAUDE_RULES_START` marker in its `AGENTS.md`. Use `--dry-run` to preview changes before writing.

```bash
# Update by project name (looks up under ../projects/)
bash ProjectUpdate.sh <project-name>

# Update by absolute path
bash ProjectUpdate.sh /abs/path/to/project

# Preview without writing
bash ProjectUpdate.sh <project-name> --dry-run
```

To propagate to all set-up projects at once, run `bash bin/update_projects.sh` from `../GAME/bin/`. Thin wrapper over `bin/project_manager.py update`.
