# AGENTS.md — Specifications Repository

> **This is the source repository for platform standards. It is exempt from CLAUDE_RULES
> injection — it does not contain `CLAUDE_RULES_START` and must never receive it.**
> Read `GLOBAL_RULES/CLAUDE_RULES.md` for the agent behavior contract distributed to projects.

## Purpose

This repository has two roles:

1. **Global standards** (`GLOBAL_RULES/`) — distributing CLAUDE_RULES.md, CONVERT.md,
   templates (common.sh, common.py), stack reference patterns, and branding standards
   to every project via `bin/create_project.py`.
2. **Project specifications** (`Game-Build/`, `GAME/`, `AlexaPrototypeOne/`, etc.) — concise
   specs organized by screen, feature, and component that define what to build.

Tooling in `bin/` creates projects, validates compliance, propagates standards, converts
concise specs, and generates build prompts. Operational tasks (push all repos, start
services, etc.) live in the GAME project, not here.

## Design Intent

The rules system exists so that any AI agent, given CLAUDE_RULES.md and a project's
spec files, can build, operate, and maintain that project without additional context.
The platform (GAME) then discovers and integrates projects automatically by reading
the same standards (METADATA.md, bin/ headers, AGENTS.md).

**Specification methodology:** You write concise specs (tables, bullets, short descriptions).
CONVERT.md defines expansion rules. Stack files define technology patterns. The build
pipeline combines everything into a single prompt an AI agent can execute.

**What this means for changes to GLOBAL_RULES/:**
- Keep CLAUDE_RULES.md minimal — agents follow rules, they don't need rationale
- CONVERT.md defines how concise specs expand — methodology lives here, not in project dirs
- Stack files are prescriptive — copy-paste patterns, not guidelines
- When rules or templates change, run `bash bin/update_projects.sh` to propagate

## Directory Layout

```
Specifications/
  GLOBAL_RULES/                    Global standards distributed to all projects
    CLAUDE_RULES.md                Agent behavior contract (injected into AGENTS.md)
    CONVERT.md                     Specification expansion rules (global methodology)
    DOCUMENTATION_BRANDING.md      Documentation theming and color standards
    stack/                         Prescriptive tech patterns (flask.md, sqlite.md, ...)
    templates/                     Canonical common.sh and common.py
    gitignore                      Standard .gitignore distributed to projects

  bin/                             Tooling: create, validate, convert, build, update
    convert.sh                     Generate conversion prompt (concise → detailed)
    build.sh                       Tag commit + generate build prompt
    generate_prompt.sh             Legacy build prompt (no tagging, no CONVERT.md)
    create_project.py              Scaffold new projects / update existing ones
    validate_project.py            Compliance checker per status level
    update_projects.sh             Push latest rules + templates to all set-up projects
    rebuild_index.sh               Regenerate browsable HTML indexes
    build_documentation.sh         Generate doc/ output

  Game-Build/                      Project specification (new format)
  GAME/                            Project specification (legacy format)
  AlexaPrototypeOne/               Project specification (numbered sequence)
  archive/                         Superseded documents — not current spec
  doc/                             Documentation: process guide, project setup guide
```

**Separation of concerns:**
- `GLOBAL_RULES/` = what standards projects must follow + how specs expand
- `{ProjectName}/` = what a specific project should be and do
- `bin/` = tooling that enforces standards and generates artifacts
- `doc/` = documentation about the specification system itself
- GAME project (separate repo) = operational tasks (push repos, start services, etc.)

## Specification File Types

| Prefix | Purpose |
|--------|---------|
| `METADATA.md` | Project identity (name, stack, port, status) |
| `README.md` | Intent, stack summary, build instructions |
| `DATABASE.md` | Tables, columns, types (schema only) |
| `UI.md` | Shared UI patterns across screens |
| `ARCHITECTURE.md` | Modules, routes, directory layout |
| `SCREEN-{Name}.md` | Per-screen: route, layout, interactions |
| `FEATURE-{Name}.md` | Per-feature: trigger, sequence, reads, writes |

Every spec file ends with `## Open Questions` for unresolved decisions.

## Dev Commands

```bash
# Convert concise specs → AI expansion prompt
bash bin/convert.sh Game-Build > convert-prompt.md

# Build: tag commit + generate complete build prompt
bash bin/build.sh Game-Build > build-prompt.md

# Build without tagging
bash bin/build.sh Game-Build --no-tag > build-prompt.md

# Tag only (no prompt output)
bash bin/build.sh Game-Build --tag-only

# List build tags for a project
git tag -l "build/Game-Build/*"

# Diff between builds
git diff build/Game-Build/2026-03-19.1..build/Game-Build/2026-03-19.2 -- Game-Build/

# Legacy: generate prompt without CONVERT.md or tagging
bash bin/generate_prompt.sh GAME > build-prompt.md

# Create a new project
python3 bin/create_project.py <name>

# Update all set-up projects with latest rules and templates
bash bin/update_projects.sh

# Validate a single project against compliance rules
bash bin/validate_project.sh <name>

# Regenerate browsable HTML index
bash bin/rebuild_index.sh
```

## Build Tags

Every `bin/build.sh` run creates an annotated git tag: `build/{project}/{YYYY-MM-DD.N}`.

Annotated tags are permanent git objects — never pruned by `git gc`. They preserve the exact
spec state used for each build, enabling spec-to-spec diffs between builds.

## Architecture

### bin/convert.sh
Generates a conversion prompt: CONVERT.md expansion rules + stack reference files + all
concise spec files from the project directory. Output is fed to an AI agent for expansion.

### bin/build.sh
Tags the current commit with an annotated build tag, then generates a complete build prompt:
CONVERT.md + CLAUDE_RULES.md + stack files + all project spec files. Warns if uncommitted
changes exist. Shows diff stat from previous build tag.

### bin/create_project.py
Creates new projects and updates existing ones.
- **Create** (`<name>`): scaffolds directory, METADATA.md, CLAUDE.md, AGENTS.md with CLAUDE_RULES injected, bin/common.sh, bin/common.py, .env.sample, .gitignore
- **Update** (`--update`): scans all projects in `../`; updates only those with `CLAUDE_RULES_START` marker.

### bin/validate_project.py
Applies cumulative compliance rules per status level (IDEA -> PRODUCTION). Stack file validation checks against `GLOBAL_RULES/stack/`.

### bin/generate_prompt.sh
Legacy build prompt generator. Reads `stack:` from METADATA.md, concatenates CLAUDE_RULES + stack files + spec files. Does not include CONVERT.md or create build tags. Use `bin/build.sh` instead for new projects.

### GLOBAL_RULES/CONVERT.md
Global specification expansion rules. Defines how each file type (DATABASE, SCREEN, FEATURE, UI, ARCHITECTURE) should be expanded from concise author input to detailed implementation-ready specs. Stack-specific expansion defers to `stack/*.md` files.

### GLOBAL_RULES/stack/
One file per technology (flask.md, sqlite.md, etc.). Prescriptive patterns included in build prompts and used during spec conversion.

## Key Conventions

- CLAUDE.md in each target project is a bare `@AGENTS.md` pointer; AGENTS.md holds the real instructions + injected CLAUDE_RULES block
- This repo's CLAUDE.md points here but carries NO injected CLAUDE_RULES block
- `archive/` holds superseded documents — do not treat as current spec
- `index.html` files are auto-generated — edit the templates, not the outputs
- When changing `GLOBAL_RULES/` content, run `bash bin/update_projects.sh` to propagate
- CONVERT.md is global (in GLOBAL_RULES/), not per-project — methodology is shared
