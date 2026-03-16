# AGENTS.md — Specifications Repository

> **This is the source repository for platform standards. It is exempt from CLAUDE_RULES
> injection — it does not contain `CLAUDE_RULES_START` and must never receive it.**
> Read `CLAUDE_RULES.md` for the condensed agent-facing version that is distributed to projects.

## Purpose

This repository has two roles:
1. **Managing the core infrastructure of other projects** — distributing standards,
   templates, and tooling (CLAUDE_RULES.md, common.sh, common.py) that every project
   consumes via `bin/create_project.py`.
2. **Acting as a specification repository** — housing detailed specs (GAME/, AlexaPrototypeOne/,
   stack/) that define what to build and how.

## Design Intent

The rules system exists so that any AI agent, given CLAUDE_RULES.md and a project's
spec files, can build, operate, and maintain that project without additional context.
The platform (GAME) then discovers and integrates projects automatically by reading
the same standards (METADATA.md, bin/ headers, AGENTS.md).

**What this means for changes to CLAUDE_RULES.md:**
- Keep the distributed file minimal — target agents follow rules, they don't need rationale
- Rules must be complete enough that an agent can act correctly without asking questions
- When a rule changes here, run `bash bin/update_projects.sh` to propagate to all projects
- Stack files in `stack/` are prescriptive — copy-paste patterns, not guidelines

## What This Repo Is

The platform specification and standards repository. It defines:
- **CLAUDE_RULES.md** — condensed agent behavior contract, distributed to all projects
- **templates/** — canonical `common.sh` and `common.py` distributed to all projects
- **stack/** — prescriptive, copy-paste-ready tech reference files per technology
- **GAME/** and **AlexaPrototypeOne/** — project specifications organized by screen/component

## Dev Commands

```bash
# Create a new project
python3 bin/create_project.py <name>

# Update all set-up projects with latest CLAUDE_RULES and templates
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
- Verifies `git_repo` from actual git remote (SSH → HTTPS normalised) and bumps `updated` timestamp on every METADATA.md write.

### bin/validate_project.sh / bin/validate_project.py
`validate_project.sh` is a thin wrapper around `validate_project.py` for a single named project. `validate_project.py` applies cumulative compliance rules per status level (IDEA → PRODUCTION). Requires `--projects <dir>`.

### bin/generate_prompt.sh
Builds a complete AI build prompt: reads `stack:` from METADATA.md, maps to `stack/*.md` reference files, concatenates header + CLAUDE_RULES.md + stack files + all project `*.md` specs.

### templates/
Canonical source for `common.sh` and `common.py`. Copied into `bin/` of new projects; refreshed in existing set-up projects by `--update`.

### METADATA.md format
Line-based key-value (not YAML). See CLAUDE_RULES.md for field reference.

### Project spec organization
- **GAME/** — by screen (SCREEN-*.md) + ARCHITECTURE.md + DATABASE.md
- **AlexaPrototypeOne/** — numerically (01-OVERVIEW.md … 11-STARTUP.md)
- **stack/** — one file per technology (flask.md, sqlite.md, aws-sqs.md, etc.)

## Key Conventions

- CLAUDE.md in each target project is a bare `@AGENTS.md` pointer; AGENTS.md holds the real instructions + injected CLAUDE_RULES block
- This repo's CLAUDE.md points here but carries NO injected CLAUDE_RULES block
- `archive/` holds superseded documents — do not treat as current spec
- `index.html` files are auto-generated — edit the templates (`_root_index_template.html`, `_project_index_template.html`), not the outputs
- When changing CLAUDE_RULES.md or templates/, run `bash bin/update_projects.sh` to propagate to all set-up projects
