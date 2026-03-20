# AGENTS.md — Prototyper (Specifications Repository)

> **This is the source repository for platform standards. It is exempt from CLAUDE_RULES
> injection — it does not contain `CLAUDE_RULES_START` and must never receive it.**
> Read `GLOBAL_RULES/CLAUDE_RULES.md` for the agent behavior contract distributed to projects.

## Purpose

This repository has two roles:

1. **Global standards** (`GLOBAL_RULES/`) — distributing CLAUDE_RULES.md, CONVERT.md,
   templates (common.sh, common.py), stack reference patterns, and branding standards
   to every project via `bin/create_project.py`.
2. **Project specifications** (`GAME/`, `AlexaPrototypeOne/`, etc.) — concise
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
    spec_template/                 Template files for create_spec.sh
    templates/                     Canonical common.sh and common.py (code projects)
    gitignore                      Standard .gitignore distributed to projects

  bin/                             Tooling: create, validate, convert, build, update
    create_spec.sh                 Scaffold new spec directory from templates
    validate.sh                    Validate spec completeness and correctness
    convert.sh                     Generate conversion prompt (concise → detailed)
    build.sh                       Tag commit + generate build prompt
    test.sh                        Test the specification system itself
    generate_prompt.sh             Legacy build prompt (no tagging, no CONVERT.md)
    create_project.py              Scaffold new code projects / update existing ones
    validate_project.py            Compliance checker per status level
    update_projects.sh             Push latest rules + templates to all set-up projects
    rebuild_index.sh               Regenerate browsable HTML indexes
    build_documentation.sh         Generate doc/ output

  GAME/                            Project specification (GAME dashboard)
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

| Prefix | Purpose | Required |
|--------|---------|----------|
| `METADATA.md` | Project identity (name, display_name, short_description, status) | Yes |
| `README.md` | One-line project description | Yes |
| `INTENT.md` | Why the project exists, who it's for | Yes |
| `ARCHITECTURE.md` | Modules, routes, directory layout | Yes |
| `DATABASE.md` | Tables, columns, types (schema only) | If has DB |
| `UI.md` | Shared UI patterns across screens | If has UI |
| `SCREEN-{Name}.md` | Per-screen: route, layout, interactions | If has UI |
| `FEATURE-{Name}.md` | Per-feature: trigger, sequence, reads, writes | As needed |

Spec files (DATABASE, UI, ARCHITECTURE, SCREEN-*, FEATURE-*) end with `## Open Questions`. README, METADATA, and INTENT do not.

## Dev Commands

### Specification workflow (all take `<project-name>` as $1)

```bash
# Scaffold a new spec directory from templates
bash bin/create_spec.sh <project-name> ["Short description"]

# Validate spec completeness and correctness
bash bin/validate.sh <project-name> [--verbose]

# Generate conversion prompt (concise → detailed specs)
bash bin/convert.sh <project-name> > convert-prompt.md

# Tag commit + generate complete build prompt
bash bin/build.sh <project-name> > build-prompt.md
bash bin/build.sh <project-name> --no-tag > build-prompt.md
bash bin/build.sh <project-name> --tag-only

# Test the specification system itself
bash bin/test.sh
```

### Build tag operations

```bash
git tag -l "build/GAME/*"
git diff build/GAME/2026-03-19.1..build/GAME/2026-03-20.1 -- GAME/
git show build/GAME/2026-03-19.1
git checkout build/GAME/2026-03-19.1 -- GAME/DATABASE.md
```

### Project management (code projects, not specs)

```bash
python3 bin/create_project.py <name>
bash bin/update_projects.sh [--dry-run]
bash bin/validate_project.sh <name> [--verbose]
bash bin/generate_prompt.sh <name> > build-prompt.md
bash bin/rebuild_index.sh
```

## Build Tags

Every `bin/build.sh` run creates an annotated git tag: `build/{project}/{YYYY-MM-DD.N}`.

Annotated tags are permanent git objects — never pruned by `git gc`. They preserve the exact
spec state used for each build, enabling spec-to-spec diffs between builds.

## Architecture

### bin/create_spec.sh
Scaffolds a new specification directory from `GLOBAL_RULES/spec_template/`. Substitutes
project name, slug, description, and date into template placeholders. Creates all required
and optional template files.

### bin/validate.sh
Validates a specification directory: required files, METADATA fields, naming conventions,
Open Questions sections, stack file existence, template cleanup. Exit 0 = valid, exit 1 = errors.

### bin/convert.sh
Generates a conversion prompt: CONVERT.md expansion rules + stack reference files + all
concise spec files from the project directory. Output is fed to an AI agent for expansion.

### bin/build.sh
Tags the current commit with an annotated build tag, then generates a complete build prompt:
CONVERT.md + CLAUDE_RULES.md + stack files + all project spec files. Warns if uncommitted
changes exist. Shows diff stat from previous build tag.

### bin/test.sh
Tests the specification system: verifies global rules, stack files, templates, script headers,
and runs a create+validate round-trip on a temporary project.

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
