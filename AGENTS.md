# AGENTS.md — Specifications Repository

> **This is the source repository for platform standards. It is exempt from CLAUDE_RULES
> injection — it does not contain `CLAUDE_RULES_START` and must never receive it.**
> Read `GLOBAL_RULES/CLAUDE_RULES.md` for the agent behavior contract distributed to projects.

## Purpose

This repository has two roles:

1. **Global standards** (`GLOBAL_RULES/`) — distributing CLAUDE_RULES.md, templates
   (common.sh, common.py), stack reference patterns, and branding standards to every
   project via `bin/create_project.py`.
2. **Project specifications** (`GAME/`, `AlexaPrototypeOne/`, etc.) — detailed specs
   organized by screen/component that define what to build and how.

Tooling in `bin/` creates projects, validates compliance, propagates standards, and
generates build prompts. These are specification-conforming operations — they verify
and enforce standards. Operational tasks (push all repos, start services, etc.) live
in the GAME project, not here.

## Design Intent

The rules system exists so that any AI agent, given CLAUDE_RULES.md and a project's
spec files, can build, operate, and maintain that project without additional context.
The platform (GAME) then discovers and integrates projects automatically by reading
the same standards (METADATA.md, bin/ headers, AGENTS.md).

**What this means for changes to GLOBAL_RULES/:**
- Keep CLAUDE_RULES.md minimal — target agents follow rules, they don't need rationale
- Rules must be complete enough that an agent can act correctly without asking questions
- When rules or templates change, run `bash bin/update_projects.sh` to propagate
- Stack files are prescriptive — copy-paste patterns, not guidelines

## Directory Layout

```
Specifications/
  GLOBAL_RULES/                    Global standards distributed to all projects
    CLAUDE_RULES.md                Agent behavior contract (injected into AGENTS.md)
    DOCUMENTATION_BRANDING.md      Documentation theming and color standards
    stack/                         Prescriptive tech patterns (flask.md, sqlite.md, ...)
    templates/                     Canonical common.sh and common.py
    gitignore                      Standard .gitignore distributed to projects

  bin/                             Tooling: create, validate, update, generate prompts
    create_project.py              Scaffold new projects / update existing ones
    validate_project.py            Compliance checker per status level
    update_projects.sh             Push latest rules + templates to all set-up projects
    generate_prompt.sh             Build complete AI build prompt from specs + stack
    rebuild_index.sh               Regenerate browsable HTML indexes
    build_documentation.sh         Generate doc/ output

  GAME/                            Project specification (by screen + architecture)
  AlexaPrototypeOne/               Project specification (numbered sequence)
  archive/                         Superseded documents — not current spec
  doc/                             Generated documentation output
```

**Separation of concerns:**
- `GLOBAL_RULES/` = what standards projects must follow
- `{ProjectName}/` = what a specific project should be and do
- `bin/` = tooling that enforces standards and generates artifacts
- GAME project (separate repo) = operational tasks (push repos, start services, etc.)

## Dev Commands

```bash
# Create a new project
python3 bin/create_project.py <name>

# Update all set-up projects with latest rules and templates
bash bin/update_projects.sh

# Validate a single project against compliance rules
bash bin/validate_project.sh <name>
bash bin/validate_project.sh <name> --verbose

# Build a complete AI build prompt for a project
bash bin/generate_prompt.sh GAME > build-prompt.md

# Regenerate browsable HTML index
bash bin/rebuild_index.sh

# Scan all projects for compliance (full report)
python3 bin/validate_project.py --projects ..

# Dry-run update (preview without writing)
bash bin/update_projects.sh --dry-run
```

## Architecture

### bin/create_project.py
Creates new projects and updates existing ones.
- **Create** (`<name>`): scaffolds directory, METADATA.md, CLAUDE.md (@AGENTS.md), AGENTS.md with CLAUDE_RULES injected, bin/common.sh, bin/common.py, .env.sample, .gitignore
- **Update** (`--update`): scans all projects in `../`; updates only those with `CLAUDE_RULES_START` marker. Skips idea-phase projects (no marker) and this repo (SPEC_DIR excluded by design).
- Sources rules from `GLOBAL_RULES/CLAUDE_RULES.md`, templates from `GLOBAL_RULES/templates/`, gitignore from `GLOBAL_RULES/gitignore`
- Verifies `git_repo` from actual git remote (SSH -> HTTPS normalised) and bumps `updated` timestamp on every METADATA.md write.

### bin/validate_project.py
Applies cumulative compliance rules per status level (IDEA -> PRODUCTION). Stack file validation checks against `GLOBAL_RULES/stack/`. `validate_project.sh` is a thin wrapper for single-project use.

### bin/generate_prompt.sh
Builds a complete AI build prompt: reads `stack:` from METADATA.md, maps to `GLOBAL_RULES/stack/*.md` reference files, concatenates header + CLAUDE_RULES.md + stack files + all project `*.md` specs.

### GLOBAL_RULES/templates/
Canonical source for `common.sh` and `common.py`. Copied into `bin/` of new projects; refreshed in existing set-up projects by `--update`.

### GLOBAL_RULES/stack/
One file per technology (flask.md, sqlite.md, aws-sqs.md, etc.). Prescriptive patterns used by `generate_prompt.sh` and validated by `validate_project.py`.

## Key Conventions

- CLAUDE.md in each target project is a bare `@AGENTS.md` pointer; AGENTS.md holds the real instructions + injected CLAUDE_RULES block
- This repo's CLAUDE.md points here but carries NO injected CLAUDE_RULES block
- `archive/` holds superseded documents — do not treat as current spec
- `index.html` files are auto-generated — edit the templates (`_root_index_template.html`, `_project_index_template.html`), not the outputs
- When changing `GLOBAL_RULES/` content, run `bash bin/update_projects.sh` to propagate to all set-up projects
