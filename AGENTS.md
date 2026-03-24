# AGENTS.md — Prototyper (Specifications Repository)

> **This is the source repository for platform standards. It is exempt from CLAUDE_RULES
> injection — it does not contain `CLAUDE_RULES_START` and must never receive it.**
> Read `RulesEngine/CLAUDE_RULES.md` for the agent behavior contract distributed to projects.

## Purpose

This repository has two roles:

1. **Global standards** (`RulesEngine/`) — distributing CLAUDE_RULES.md, ONESHOT_BUILD_RULES.md,
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
ONESHOT_BUILD_RULES.md defines expansion rules. Stack files define technology patterns. The build
pipeline combines everything into a single prompt an AI agent can execute.

**What this means for changes to RulesEngine/:**
- BUSINESS_RULES.md is the source for agent behavioral rules — full rationale lives there
- CLAUDE_RULES.md is generated from BUSINESS_RULES.md via `bin/summarize_rules.sh` — never edit it directly
- Keep CLAUDE_RULES.md minimal — agents follow rules, they don't need rationale
- ONESHOT_BUILD_RULES.md defines how concise specs expand — methodology lives here, not in project dirs
- Stack files are prescriptive — copy-paste patterns, not guidelines
- When rules or templates change, run `bash bin/update_projects.sh` to propagate

## Directory Layout

```
Specifications/
  RulesEngine/                    Global standards distributed to all projects
    BUSINESS_RULES.md              Source for agent behavior rules — edit this, not CLAUDE_RULES.md
    CLAUDE_RULES.md                Generated agent behavior contract (injected into AGENTS.md)
    ONESHOT_BUILD_RULES.md                     Specification expansion rules (global methodology)
    DOCUMENTATION_BRANDING.md      Documentation theming and color standards
    stack/                         Prescriptive tech patterns (flask.md, sqlite.md, ...)
    spec_template/                 Template files for setup.sh
    templates/                     Canonical common.sh and common.py (code projects)
    gitignore                      Standard .gitignore distributed to projects

  bin/                             Tooling — spec scripts work on this repo only; Project* scripts push to code projects
    setup.sh                       Scaffold new spec directory (or update existing) from templates
    validate.sh                    Validate a spec directory for completeness and correctness
    convert.sh                     Generate conversion prompt (concise → detailed)
    merge.sh                       Squash-merge Feature Branch → base branch (called by GAME)
    oneshot.sh                     Validate + detect mode + generate build prompt (canonical build command)
    summarize_rules.sh       Generate prompt to regenerate CLAUDE_RULES.md
    test.sh                        Test the specification system itself
    build_documentation.sh         Build doc/index.html
    project_manager.py             Python backend for project verify/update operations
    ProjectValidate.sh             Verify a promoted code project against CLAUDE_RULES compliance
    ProjectUpdate.sh               Update a promoted code project with latest rules and templates

  GAME/                            Project specification (GAME dashboard)
  AlexaPrototypeOne/               Project specification (numbered sequence)
  archive/                         Superseded documents — not current spec
  doc/                             Documentation: process guide, project setup guide
```

**Reference standards in RulesEngine/ (not auto-distributed):**
- `DOCUMENTATION_BRANDING.md` — color variables, typography, theme standards. Not auto-distributed; projects copy patterns from here manually. Authoritative for all documentation styling.
- `BUSINESS_RULES.md` — source of truth for agent behavioral rules. Edit here, then regenerate CLAUDE_RULES.md.

**Separation of concerns:**
- `RulesEngine/` = what standards projects must follow + how specs expand
- `{ProjectName}/` = what a specific prototype spec should be and do
- `bin/` spec scripts = work on prototype directories inside this repo only
- `bin/` Project* scripts = push standards to promoted code projects (absolute path or project name)
- `doc/` = documentation about the specification system itself
- GAME project (`../GAME/bin/`) = create_project.py (scaffold new projects); wrappers delegate validate/update to project_manager.py

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

### CLAUDE_RULES regeneration

```bash
bash bin/summarize_rules.sh > rules-prompt.md
# Feed rules-prompt.md to an AI agent — paste output over RulesEngine/CLAUDE_RULES.md
```

### Specification workflow (spec names only — directories inside this repo)

```bash
# Scaffold a new spec directory from templates (or update an existing one)
bash bin/setup.sh <ProjectName>              # creates Specifications/<name>/
bash bin/setup.sh <ProjectName> --update     # add new template files to existing dir

# Validate spec completeness and correctness
bash bin/validate.sh <ProjectName> [--verbose]

# Generate conversion prompt (concise → detailed specs) — optional intermediate step
bash bin/convert.sh <ProjectName> > convert-prompt.md

# OneShot: validate + detect mode + generate build prompt (canonical command)
#
#   New project mode (no git_repo or no BUILD_FEATURE_BRANCH_NAME):
#     bash bin/oneshot.sh <ProjectName> > <ProjectName>/oneshot-prompt.md
#     mkdir -p /mnt/c/Users/barlo/projects/<name> && cd /mnt/c/Users/barlo/projects/<name>
#     git init && git checkout -b main
#     claude .   # paste prompt
#
#   Feature Branch mode (git_repo + BUILD_FEATURE_BRANCH_NAME set in .env):
#     → clone/fetch + create branch, then generate prompt
#     bash bin/oneshot.sh <ProjectName> > oneshot-prompt.md
#     cd /path/to/projects/<name> && claude .   # paste prompt
#
#   Update mode (apply spec changes to existing code):
#     bash bin/oneshot.sh <ProjectName> --update > oneshot-prompt.md

# Merge: squash-merge Feature Branch into base branch (GAME calls this automatically)
bash bin/merge.sh <ProjectName>
bash bin/merge.sh <ProjectName> --feature feature/name --base main --dry-run

# Test the specification system itself
bash bin/test.sh
```

### Promoted project management (code projects outside this repo)

```bash
# Verify a project against CLAUDE_RULES compliance (shows current status + next level preview)
bash bin/ProjectValidate.sh <project-name>          # project name under ../projects/
bash bin/ProjectValidate.sh /abs/path/to/project    # absolute path
bash bin/ProjectValidate.sh <project-name> --verbose

# Update a project with latest rules and templates
bash bin/ProjectUpdate.sh <project-name>            # project name under ../projects/
bash bin/ProjectUpdate.sh /abs/path/to/project      # absolute path
bash bin/ProjectUpdate.sh <project-name> --dry-run  # preview without writing
```

### Build tag operations

```bash
git tag -l "oneshot/GAME/*"
git diff oneshot/GAME/2026-03-19.1..oneshot/GAME/2026-03-20.1 -- GAME/
git show oneshot/GAME/2026-03-19.1
git checkout oneshot/GAME/2026-03-19.1 -- GAME/DATABASE.md
```

### Spec viewer

```bash
bash bin/build_documentation.sh
```

### Scaffold a new code project (runs from GAME)

```bash
# These scripts live in ../GAME/bin/ — run from there
python3 bin/create_project.py <name>          # scaffold new project with standard structure
bash bin/update_projects.sh [--dry-run]       # push rules/templates to all set-up projects
```

## OneShot Tags

Every `bin/oneshot.sh` run creates an annotated git tag: `oneshot/{spec}/{YYYY-MM-DD.N}`.

Annotated tags are permanent git objects — never pruned by `git gc`. They preserve the exact
spec state used for each build, enabling spec-to-spec diffs between builds.

## Architecture

### bin/setup.sh
Scaffolds a new specification directory from `RulesEngine/spec_template/`, or updates an existing one. Accepts a spec name (created as `Specifications/<name>/`). `--update` copies only new template files; `--force` overwrites all. Substitutes project name, slug, description, and date into template placeholders.

### bin/validate.sh
Validates a specification directory inside this repo: required files, METADATA fields, conformity level, naming conventions, Open Questions sections, stack file existence, template cleanup. Accepts a spec name only. Exit 0 = valid, exit 1 = errors.

### bin/convert.sh
Generates a conversion prompt: ONESHOT_BUILD_RULES.md expansion rules + stack reference files + all
concise spec files from the project directory. Output is fed to an AI agent for expansion.

### bin/oneshot.sh
The canonical build command. Validates the spec, detects build mode, then generates a
complete one-shot build prompt: ONESHOT_BUILD_RULES.md + CLAUDE_RULES.md + stack files + all spec files.

**New project mode** (no `git_repo` or no `BUILD_FEATURE_BRANCH_NAME`): generates
the prompt only. Create the target directory manually (`mkdir` + `git init`), then open
Claude Code and paste the prompt.

**Feature Branch mode** (`git_repo` + `BUILD_FEATURE_BRANCH_NAME` both set): clones or
fetches the project into `../<Name>/`, creates the feature branch, generates the prompt.

Tags the current commit with an annotated oneshot tag. Warns if uncommitted changes exist.
Shows diff stat from previous oneshot tag. Includes stub policy in build prompts.

### bin/test.sh
Tests the specification system: verifies global rules, stack files, templates, script headers,
and runs a create+validate round-trip on a temporary project.

### bin/summarize_rules.sh
Generates a prompt for an AI agent to regenerate `RulesEngine/CLAUDE_RULES.md` from `RulesEngine/BUSINESS_RULES.md`. Auto-increments the version (date + sequence). Output is fed to an AI agent; the agent produces the new CLAUDE_RULES.md content.


Use `bin/oneshot.sh` directly — it handles both Bootstrap and Feature Branch modes automatically.

### bin/merge.sh
Squash-merges a feature branch into the base branch and deletes it. Reads feature branch from `.env` and base branch from `METADATA.md`. Accepts `--feature`, `--base`, and `--dry-run` overrides. Called by GAME UI — can also be run directly.

### bin/project_manager.py
Python backend for promoted project operations. Two subcommands:
- `verify <project>` — runs CLAUDE_RULES compliance checks grouped by level (IDEA → PROTOTYPE → ACTIVE → PRODUCTION), shows "you are here" status from METADATA.md, and previews the next level's requirements. Accepts project name or absolute path.
- `update <project>` — injects latest CLAUDE_RULES.md into AGENTS.md, copies template files (common.sh, common.py, index.html), adds missing METADATA.md default fields, and updates git_repo from the git remote. Supports `--dry-run`. Project must already have CLAUDE_RULES_START marker.

### bin/ProjectValidate.sh
Thin wrapper calling `project_manager.py verify`. Operates on promoted code projects only — not spec directories in this repo.

### bin/ProjectUpdate.sh
Thin wrapper calling `project_manager.py update`. Operates on promoted code projects only — not spec directories in this repo.

### RulesEngine/ONESHOT_BUILD_RULES.md
Global specification expansion rules. Defines how each file type (DATABASE, SCREEN, FEATURE, UI, ARCHITECTURE) should be expanded from concise author input to detailed implementation-ready specs. Stack-specific expansion defers to `stack/*.md` files.

### RulesEngine/stack/
One file per technology (flask.md, sqlite.md, etc.). Prescriptive patterns included in oneshot prompts and used during spec conversion.

## Standard Files in Every Code Project

| File | Source | Purpose |
|------|--------|---------|
| `index.html` | `RulesEngine/templates/index.html` | Redirect to `doc/index.html` — entry point for browsers |
| `bin/common.sh` | `RulesEngine/templates/common.sh` | Shared shell utilities |
| `bin/common.py` | `RulesEngine/templates/common.py` | Shared Python utilities |
| `CLAUDE.md` | Generated by `create_project.py` | `@AGENTS.md` pointer |
| `AGENTS.md` | Generated + injected | Dev commands + CLAUDE_RULES block |

Propagated to a single project: `bash bin/ProjectUpdate.sh <project>`.
Propagated to all set-up projects: `bash bin/update_projects.sh` (in `../GAME/bin/`).
Validated at PROTOTYPE level: `bash bin/ProjectValidate.sh <project>`.

## Adding a New Standard Feature

The pattern for adding any new contract/file that all projects should have:

1. **Add the template** — put the file in `RulesEngine/templates/`
2. **Generate it** — in `../GAME/bin/create_project.py` `create_project()`, call `copy_template('myfile', dest)`
3. **Propagate it** — in `bin/project_manager.py` `cmd_update()`, add to the template copy loop
4. **Validate it** — add a rule name to `RULES_BY_LEVEL` in `bin/project_manager.py` and implement its `check()` case
5. **Document it** — add a row to the table above in this file

## Key Conventions

- CLAUDE.md in each target project is a bare `@AGENTS.md` pointer; AGENTS.md holds the real instructions + injected CLAUDE_RULES block
- This repo's CLAUDE.md points here but carries NO injected CLAUDE_RULES block
- `archive/` holds superseded documents — do not treat as current spec
- `index.html` files are auto-generated — edit the templates, not the outputs
- When changing `RulesEngine/` content: run `bash bin/ProjectUpdate.sh <project>` per project, or `bash bin/update_projects.sh` from `../GAME/` for all
- ONESHOT_BUILD_RULES.md is global (in RulesEngine/), not per-project — methodology is shared
- BUSINESS_RULES.md is the source of truth for agent behavioral rules; CLAUDE_RULES.md is generated — never edit CLAUDE_RULES.md directly
