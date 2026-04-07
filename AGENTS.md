# AGENTS.md — Prototyper (Specifications Repository)

> **This is the source repository for platform standards. It is exempt from CLAUDE_RULES
> injection — it does not contain `CLAUDE_RULES_START` and must never receive it.**
> Read `RulesEngine/CLAUDE_RULES.md` for the agent behavior contract distributed to projects.

## Purpose

This repository has two roles:

1. **Global standards** (`RulesEngine/` + `prompts/`) — distributing CLAUDE_RULES.md,
   templates (common.sh, common.py), stack reference patterns, branding standards,
   and prompt content to every project via `bin/create_project.py`.
2. **Project specifications** (`GAME/`, etc.) — concise
   specs organized by screen, feature, and component that define what to build.

Tooling in `bin/` creates projects, validates compliance, propagates standards, converts
concise specs, and generates build prompts. Operational tasks (push all repos, start
services, etc.) live in the GAME project, not here.

## Wording

Use the word specification in preference to spec except in program names

## Design Intent

The rules system exists so that any AI agent, given CLAUDE_RULES.md and a project's
specification files, can build, operate, and maintain that project without additional context.
The platform (GAME) then discovers and integrates projects automatically by reading
the same standards (METADATA.md, bin/ headers, AGENTS.md).

**Specification methodology:** You write concise specifications (tables, bullets, short descriptions).
`prompts/oneshot_build_rules.md` defines expansion rules. Stack files define technology patterns. The build
pipeline combines everything into a single prompt an AI agent can execute.

**Word choice:** Use "specification" in preference to "spec" in documentation, comments, and prose. "spec" is only acceptable in program/script names (e.g. `spec_iterate.sh`) and directory suffix conventions where brevity matters.

**What this means for changes to RulesEngine/:**
- BUSINESS_RULES.md is the source for agent behavioral rules — full rationale lives there
- CLAUDE_RULES.md is generated from BUSINESS_RULES.md via `bin/summarize_rules.sh` — never edit it directly
- Keep CLAUDE_RULES.md minimal — agents follow rules, they don't need rationale
- `prompts/oneshot_build_rules.md` defines how concise specs expand — methodology is shared, not per-project
- Stack files are prescriptive — copy-paste patterns, not guidelines
- When rules or templates change, run `bash bin/update_projects.sh` to propagate

**RulesEngine/ edit gate — REQUIRED before writing any file in `RulesEngine/`:**
Before writing or editing any file under `RulesEngine/`, you must:
1. Present the proposed change — exact wording, not a summary.
2. Surface any conflicts with existing rules.
3. Confirm that the rule is reproducible and enforceable across all projects.
4. Wait for explicit user approval before writing.

You are acting as a QA gate, not an executor. The goal is to arrive at correct, consistent business rules — not to implement what was asked verbatim. Push back if a proposed rule contradicts an existing one or cannot be uniformly enforced.

## Directory Layout

```
Specifications/
  RulesEngine/                    Governance standards distributed to all projects
    BUSINESS_RULES.md              Source for agent behavior rules — edit this, not CLAUDE_RULES.md
    CLAUDE_RULES.md                Generated agent behavior contract (injected into AGENTS.md)
    BRANDING.md                    Color variables, typography, and layout standards
    PROTOTYPE_PROCESS.md           Lifecycle state machine (build and iteration workflow)
    stack/                         Prescriptive tech patterns (flask.md, sqlite.md, ...)
    spec_template/                 Template files for setup.sh
    templates/                     Canonical common.sh and common.py (code projects)
    gitignore                      Standard .gitignore distributed to projects

  bin/                             Tooling — specification scripts work on this repo only; Project* scripts push to code projects
    setup.sh                       Scaffold new specification directory (or update existing) from templates
    validate.sh                    Validate a specification directory for completeness and correctness
    convert.sh                     Generate conversion prompt (concise → detailed)
    oneshot.sh                     Validate + detect mode + generate build prompt (canonical build command)
    iterate.sh                     Generate iteration prompt from pending tickets and specification diffs
    merge.sh                       Squash-merge Feature Branch → base branch (called by GAME)
    tran_logger.sh                 Extract bugs and ideas from AI session transaction logs
    spec_iterate.sh                AI-powered specification gap analysis and quality scoring
    scorecard.sh                   Generate SCORECARD.md — comprehensive project health dashboard
    update_reference_gaps.sh       Update REFERENCE_GAPS.md from specification vs prototype comparison
    decompose.sh                   Reverse-engineer an existing project into specification files
    summarize_rules.sh             Generate prompt to regenerate CLAUDE_RULES.md
    test.sh                        Test the specification system itself
    document.sh                    Generate project documentation from specifications (AI + assembler)
    build_documentation.sh         Build docs/index.html (Prototyper docs only)
    build_project_docs.py          Assemble project docs HTML from DOC-*.md files (called by document.sh)
    project_manager.py             Python backend for project verify/update operations
    ProjectValidate.sh             Verify a promoted code project against CLAUDE_RULES compliance
    ProjectUpdate.sh               Update a promoted code project with latest rules and templates

  GAME/                            Project specification (GAME dashboard)
  archive/                         Superseded documents — not current spec
  docs/                            Generated documentation (index.html, Features.html, white-paper.html)
  prompts/                         All prompt content consumed by bin/ scripts (templates + rules embedded in AI prompts)
```

**Reference standards in RulesEngine/ (not auto-distributed):**
- `BRANDING.md` — color variables, typography, theme standards. Not auto-distributed; projects copy patterns from here manually. Authoritative for all documentation styling.
- `BUSINESS_RULES.md` — source of truth for agent behavioral rules. Edit here, then regenerate CLAUDE_RULES.md.

**Separation of concerns:**
- `RulesEngine/` = governance standards projects must follow (rules, branding, process)
- `prompts/` = all content embedded in AI prompts by bin/ scripts (expansion rules, templates)
- `{ProjectName}/` = what a specific prototype specification should be and do
- `bin/` specification scripts = work on prototype directories inside this repo only
- `bin/` Project* scripts = push standards to promoted code projects (absolute path or project name)
- `docs/` = documentation about the specification system itself
- GAME project (`../GAME/bin/`) = create_project.py (scaffold new projects); wrappers delegate validate/update to project_manager.py

## Specification File Types

| File | Purpose | Required |
|------|---------|----------|
| `METADATA.md` | Project identity (name, display_name, short_description, status) | Yes |
| `README.md` | One-line description + `## Intent` section (why it exists, who it's for) | Yes |
| `INTENT.md` | Standalone intent document — goals, constraints, success criteria | Yes |
| `ARCHITECTURE.md` | Modules, routes, directory layout | Yes |
| `FUNCTIONALITY.md` | What the application does — high-level feature summary | Yes |
| `DATABASE.md` | Tables, columns, types (schema only) | If has DB |
| `UI-GENERAL.md` | Shared UI patterns across screens | If has UI |
| `SCREEN-{Name}.md` | Per-screen: route, layout, interactions | If has UI |
| `FEATURE-{Name}.md` | Per-feature: trigger, sequence, reads, writes | As needed |
| `HOMEPAGE.md` | Portfolio homepage: branding, contact, bio, diagram links | If publishes a portfolio |
| `HOMEPAGE-PUBLISHER.md` | Template-based homepage publishing configuration | If publishes a portfolio |
| `IDEAS.md` | Feature ideas and backlog (written by tran_logger.sh or manually) | No |
| `ACCEPTANCE_CRITERIA.md` | Acceptance criteria for the current build | No |
| `REFERENCE_GAPS.md` | Specification completeness gaps (written by spec_iterate.sh) | No |
| `SPEC_SCORECARD.md` | 7-dimension quality rating (written by spec_iterate.sh) | No |

**Numbered ticket files** (applied in NNN order by iterate.sh):

| Pattern | Purpose |
|---------|---------|
| `SCREEN-NNN-{Name}.md` | Screen change ticket |
| `FEATURE-NNN-{Name}.md` | Feature change ticket |
| `PATCH-NNN-{Name}.md` | Targeted code patch ticket |
| `AC-NNN-{Name}.md` | Acceptance criteria ticket |

Specification files (DATABASE, UI-GENERAL, ARCHITECTURE, SCREEN-*, FEATURE-*, FUNCTIONALITY) end with `## Open Questions`. README, METADATA, and generated files (IDEAS, REFERENCE_GAPS, SPEC_SCORECARD) do not.

## Dev Commands

### CLAUDE_RULES regeneration

```bash
bash bin/summarize_rules.sh > rules-prompt.md
# Feed rules-prompt.md to an AI agent — paste output over RulesEngine/CLAUDE_RULES.md
```

### Specification workflow (specification names only — directories inside this repo)

```bash
# Scaffold a new specification directory from templates (or update an existing one)
bash bin/setup.sh <ProjectName>              # creates Specifications/<name>/
bash bin/setup.sh <ProjectName> --update     # add new template files to existing dir

# Validate specification completeness and correctness
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
#   Update mode (apply specification changes to existing code):
#     bash bin/oneshot.sh <ProjectName> --update > oneshot-prompt.md

# Iterate: generate iteration prompt from pending tickets and specification diffs
bash bin/iterate.sh <ProjectName> > iterate-prompt.md

# Merge: squash-merge Feature Branch into base branch (GAME calls this automatically)
bash bin/merge.sh <ProjectName>
bash bin/merge.sh <ProjectName> --feature feature/name --base main --dry-run

# Test the specification system itself
bash bin/test.sh
```

### Iteration and quality tools

```bash
# Extract bugs and ideas from AI session transaction log
bash bin/tran_logger.sh <ProjectName>
bash bin/tran_logger.sh <ProjectName> --model=claude-haiku-4-5-20251001

# AI-powered specification gap analysis and quality scoring
bash bin/spec_iterate.sh <ProjectName>
bash bin/spec_iterate.sh <ProjectName> --model opus

# Generate SCORECARD.md — comprehensive project health dashboard
bash bin/scorecard.sh <ProjectName>
bash bin/scorecard.sh <ProjectName> --run-tests
bash bin/scorecard.sh <ProjectName> --target=/path/to/prototype

# Update REFERENCE_GAPS.md from specification vs prototype comparison
bash bin/update_reference_gaps.sh <ProjectName>

# Reverse-engineer an existing project into specification files
bash bin/decompose.sh /path/to/project > decompose-prompt.md
bash bin/decompose.sh /path/to/project --spec-name MyProject > decompose-prompt.md
```

### Promoted project management (code projects outside this repo)

```bash
# Verify a project against CLAUDE_RULES compliance (shows current status + next level preview)
bash bin/ProjectValidate.sh <project-name>          # project name under ../projects/
bash bin/ProjectValidate.sh /abs/path/to/project    # absolute path
bash bin/ProjectValidate.sh <project-name> --verbose

# Update a project with latest rules and templates
bash ProjectUpdate.sh <project-name>            # project name under ../projects/
bash ProjectUpdate.sh /abs/path/to/project      # absolute path
bash ProjectUpdate.sh <project-name> --dry-run  # preview without writing
```

### Project documentation (generates docs for a promoted project from its specs)

```bash
# Generate documentation for a project from its specification files
bash bin/document.sh <ProjectName>
bash bin/document.sh <ProjectName> --theme=slate --target=../GAME_p2
bash bin/document.sh <ProjectName> --model=opus

# Phase 1: AI (claude -p) reads specs, writes DOC-*.md summaries into target docs/
# Phase 2: build_project_docs.py assembles DOC-*.md + bin/ scripts into docs/index.html
# Also installs bin/build_documentation.sh in the target project for rebuilds
```

### Build tag operations

```bash
git tag -l "oneshot/GAME/*"
git diff oneshot/GAME/2026-03-19.1..oneshot/GAME/2026-03-20.1 -- GAME/
git show oneshot/GAME/2026-03-19.1
git checkout oneshot/GAME/2026-03-19.1 -- GAME/DATABASE.md
```

### Specification viewer

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
specification state used for each build, enabling specification-to-specification diffs between builds.

## Architecture

### bin/setup.sh
Scaffolds a new specification directory from `RulesEngine/spec_template/`, or updates an existing one. Accepts a specification name (created as `Specifications/<name>/`). `--update` copies only new template files; `--force` overwrites all. Substitutes project name, slug, description, and date into template placeholders.

### bin/validate.sh
Validates a specification directory inside this repo: required files, METADATA fields, conformity level, naming conventions, Open Questions sections, stack file existence, template cleanup. Accepts a specification name only. Exit 0 = valid, exit 1 = errors.

### bin/convert.sh
Generates a conversion prompt: `prompts/oneshot_build_rules.md` expansion rules + stack reference files + all
concise specification files from the project directory. Output is fed to an AI agent for expansion.

### bin/oneshot.sh
The canonical build command. Validates the spec, detects build mode, then generates a
complete one-shot build prompt: prompt files + CLAUDE_RULES.md + stack files + all specification files.

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

### bin/iterate.sh
Generates an iteration prompt from pending change tickets (SCREEN-NNN-*, FEATURE-NNN-*, PATCH-NNN-*, AC-NNN-*) and modified specification diffs. The agent validates each ticket before implementing. Does not rebuild from scratch — applies targeted changes to the existing codebase.

### bin/merge.sh
Squash-merges a feature branch into the base branch and deletes it. Reads feature branch from `.env` and base branch from `METADATA.md`. Accepts `--feature`, `--base`, and `--dry-run` overrides. Called by GAME UI — can also be run directly.

### bin/project_manager.py
Python backend for promoted project operations. Two subcommands:
- `verify <project>` — runs CLAUDE_RULES compliance checks grouped by level (IDEA → PROTOTYPE → ACTIVE → PRODUCTION), shows "you are here" status from METADATA.md, and previews the next level's requirements. Accepts project name or absolute path.
- `update <project>` — injects latest CLAUDE_RULES.md into AGENTS.md, copies template files (common.sh, common.py, index.html), adds missing METADATA.md default fields, and updates git_repo from the git remote. Supports `--dry-run`. Project must already have CLAUDE_RULES_START marker.

### bin/tran_logger.sh
Reads the Claude Code session transaction log (JSONL), analyzes git history plus session logs, and extracts bugs and ideas via an AI model. Writes PATCH-NNN-tl-*.md (mutations), AC-NNN-tl-*.md (acceptance criteria), and updates IDEAS.md. Default model: claude-haiku-4-5-20251001.

### bin/spec_iterate.sh
AI-powered specification gap analysis using `claude -p` (subscription, not API tokens). Updates REFERENCE_GAPS.md, writes SPEC_SCORECARD.md (7-dimension quality rating), and SPEC_ITERATION.md (focused prompt targeting 1-2 highest-priority gaps). Accepts `--model opus|sonnet|haiku`.

### bin/scorecard.sh
Comprehensive project health dashboard. Computes deterministic metrics across six dimensions: specification completeness, route coverage, test health, acceptance criteria, project structure, and deployment status. Reads specification files, prototype source, REFERENCE_GAPS.md, and SPEC_SCORECARD.md. Detects spec drift (files changed since last build tag), counts pending tickets, flags demerits for missing artifacts (no tests, no AC, etc.). Writes SCORECARD.md to the specification directory by default, or `--target` for the prototype. Supports `--run-tests` to execute tests and capture results. Multiple scripts can trigger regeneration — the output is structured markdown with parseable sections and summary table.

### bin/update_reference_gaps.sh
Compares specification files against the prototype and optionally a reference implementation. Uses `claude -p` to identify gaps. Writes REFERENCE_GAPS.md in the specification directory.

### bin/document.sh
Generates project documentation from specification files. Two-phase pipeline: (1) calls `claude -p` (sonnet by default) to read specs and write curated `DOC-*.md` summaries into the target project's `docs/`, (2) calls `build_project_docs.py` to assemble those summaries + bin/ script headers into `docs/index.html`. Also copies CSS theme files and installs `bin/build_documentation.sh` in the target for rebuilds. Accepts `--theme`, `--target`, `--model`.

### bin/build_project_docs.py
HTML assembler called by `document.sh`. Reads `DOC-*.md` from the target's `docs/`, discovers CommandCenter scripts from the target's `bin/`, and generates a single-page documentation app matching the Prototyper docs look and feel (sidebar, nav sections, man-pages, marked.js rendering). Output: `docs/index.html` with versioned footer.

### bin/decompose.sh
Reverse-engineers an existing project into specification files. Reads source code, detects stack, and generates a prompt for an AI agent to produce structured specification files (METADATA, ARCHITECTURE, DATABASE, SCREEN-*, FEATURE-*, etc.). Output to stdout — pipe to a file and feed to an AI agent.

### bin/ProjectValidate.sh
Thin wrapper calling `project_manager.py verify`. Operates on promoted code projects only — not specification directories in this repo.

### ProjectUpdate.sh
Thin wrapper calling `project_manager.py update`. Operates on promoted code projects only — not specification directories in this repo.

### prompts/oneshot_build_rules.md
Global specification expansion rules. Defines how each file type (DATABASE, SCREEN, FEATURE, UI, ARCHITECTURE) should be expanded from concise author input to detailed implementation-ready specs. Stack-specific expansion defers to `stack/*.md` files.

### RulesEngine/stack/
One file per technology (flask.md, sqlite.md, etc.). Prescriptive patterns included in oneshot prompts and used during specification conversion.

## Standard Files in Every Code Project

| File | Source | Purpose |
|------|--------|---------|
| `index.html` | `RulesEngine/templates/index.html` | Redirect to `docs/index.html` — entry point for browsers |
| `bin/common.sh` | `RulesEngine/templates/common.sh` | Shared shell utilities |
| `bin/common.py` | `RulesEngine/templates/common.py` | Shared Python utilities |
| `CLAUDE.md` | Generated by `create_project.py` | `@AGENTS.md` pointer |
| `AGENTS.md` | Generated + injected | Dev commands + CLAUDE_RULES block |

Propagated to a single project: `bash ProjectUpdate.sh <project>`.
Propagated to all set-up projects: `bash bin/update_projects.sh` (in `../GAME/bin/`).
Validated at PROTOTYPE level: `bash bin/ProjectValidate.sh <project>`.

## Adding a New Standard Feature

The pattern for adding any new contract/file that all projects should have:

1. **Add the template** — put the file in `RulesEngine/templates/`
2. **Generate it** — in `../GAME/bin/create_project.py` `create_project()`, call `copy_template('myfile', dest)`
3. **Propagate it** — in `bin/project_manager.py` `cmd_update()`, add to the template copy loop
4. **Validate it** — add a rule name to `RULES_BY_LEVEL` in `bin/project_manager.py` and implement its `check()` case
5. **Document it** — add a row to the table above in this file

## Adding a New Service Endpoint

The pattern for adding a new bin/ script that uses AI prompts or RulesEngine standards:

1. Create `bin/<name>.sh` with CommandCenter header including `# Prompt:` and/or `# Rules:` fields
2. If the script uses an AI prompt template, create `prompts/<name>.md` with standard header
3. Run `bash bin/test.sh` — it auto-validates all declared dependencies exist

Service endpoint headers declare dependencies — no manifest to maintain:

```bash
#!/bin/bash
# CommandCenter Operation
# Name: My Script
# Category: maintenance
# Args: Spec
# Prompt: prompts/my_script.md
# Rules: RulesEngine/BUSINESS_RULES.md, RulesEngine/stack/*.md
```

## Key Conventions

- CLAUDE.md in each target project is a bare `@AGENTS.md` pointer; AGENTS.md holds the real instructions + injected CLAUDE_RULES block
- This repo's CLAUDE.md points here but carries NO injected CLAUDE_RULES block
- `archive/` holds superseded documents — do not treat as current spec
- `index.html` files are auto-generated — edit the templates, not the outputs
- When changing `RulesEngine/` content: run `bash ProjectUpdate.sh <project>` per project, or `bash bin/update_projects.sh` from `../GAME/` for all
- oneshot_build_rules.md is global (in prompts/), not per-project — methodology is shared
- BUSINESS_RULES.md is the source of truth for agent behavioral rules; CLAUDE_RULES.md is generated — never edit CLAUDE_RULES.md directly
