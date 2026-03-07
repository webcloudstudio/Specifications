# GAME - Generic AI Management Environment

## Complete System Specification

This **two-tier specification system** is a repository for managing multiple projects from unified specifications.

* **Shared**: Reusable technology files (language, framework, database, frontend patterns)
* **Project-specific**: Each project in its own directory with STACK.yaml and numbered spec files

## Overview

The spec system separates **what to build** (project-specific) from **how to build it** (technology patterns):

```
GAME_Spec/                           ← Repository root
├── stack/                           ← Technology files (shared, reusable)
│   ├── common.md
│   ├── python.md
│   ├── flask.md
│   ├── django.md
│   ├── sqlite.md
│   ├── postgres.md
│   └── bootstrap5.md
├── validate.sh                      ← Generic validation tool
├── generate-prompt.sh               ← Generic prompt generator
├── README.md
└── GAME/                            ← First project
    ├── STACK.yaml                   ← Declares your stack selections
    ├── 01-OVERVIEW.md
    ├── 02-DATABASE.md
    ├── ... through ...
    └── 11-STARTUP.md                ← Spec files (project-specific)
```

Additional projects would follow the same pattern:
```
├── OTHER_PROJECT/
│   ├── STACK.yaml
│   ├── 01-*.md
│   └── ... more spec files ...
```

## Key Files

### Repository Root

**stack/** — Technology Reference Files

Reusable best practices that **never change between projects**. Each one is prescriptive, with concrete code examples.

| File | Maps to STACK.yaml | Covers |
|------|-------------------|--------|
| `stack/common.md` | *(always)* | Directory layout, bin/ scripts, Links.md, CLAUDE.md convention, git hygiene, dev workflow |
| `stack/python.md` | `language: python` | Config classes, logging, testing with pytest, dependencies, startup validation |
| `stack/flask.md` | `framework: flask` | App factory, blueprints, Jinja2, HTMX, test client, security |
| `stack/django.md` | `framework: django` | Settings package, ORM, migrations, admin, django-htmx |
| `stack/sqlite.md` | `database: sqlite` | Connection setup, PRAGMAs, JSON columns, migrations, backup |
| `stack/postgres.md` | `database: postgres` | Connection pooling, JSONB, numbered migrations, indexing |
| `stack/bootstrap5.md` | `frontend: bootstrap5` | CDN setup, dark theme, components, HTMX integration |

Each technology file follows a consistent structure:
- **Rule**: Prescriptive one-liner (e.g., "Always enable WAL mode")
- **Implementation**: Concrete code snippets
- **Why**: Brief rationale
- **Summary Checklist**: Items to verify

### Project Directory (e.g., GAME/)

**STACK.yaml** — The Manifest

Declares technology selections and project configuration:

```yaml
language: python       # → ../stack/python.md
framework: flask       # → ../stack/flask.md
database: sqlite       # → ../stack/sqlite.md
frontend: bootstrap5   # → ../stack/bootstrap5.md

project:
  name: commandcenter
  port: 5001
  output_dir: ../..

directories:
  data: data
  logs: data/logs
  tests: tests

env:
  required:
    - PROJECTS_DIR
  optional:
    - SECRET_KEY
```

**Key insight**: The `language`, `framework`, `database`, and `frontend` values map directly to **filenames in ../stack/**. This is the mapping system — no lookup table needed.

**Numbered Spec Files (01-11)** — Project Specification

Project-specific descriptions of **what to build**. These reference technology files for implementation details.

| # | File | Covers |
|---|------|--------|
| 01 | [OVERVIEW](GAME/01-OVERVIEW.md) | Purpose, tech stack, dependencies, directory layout, navigation |
| 02 | [DATABASE](GAME/02-DATABASE.md) | SQLite schema, tables, extra JSON column, migrations, data access |
| 03 | [SCANNER](GAME/03-SCANNER.md) | Project discovery, tech stack detection, git operations, metadata parsing |
| 04 | [OPERATIONS](GAME/04-OPERATIONS.md) | ops.py server/one-shot execution, spawn.py generic process service |
| 05 | [ROUTES-API](GAME/05-ROUTES-API.md) | All Flask routes, HTMX API endpoints, request/response patterns |
| 06 | [UI-TEMPLATES](GAME/06-UI-TEMPLATES.md) | Template hierarchy, page layouts, component structure |
| 07 | [STYLING](GAME/07-STYLING.md) | CSS custom properties, component classes, design system |
| 08 | [PUBLISHER](GAME/08-PUBLISHER.md) | GitHub Pages pipeline, card rendering, Astro generation |
| 09 | [PROCESSES](GAME/09-PROCESSES.md) | Process monitor, bin/ scripts, ETL, scheduling |
| 10 | [CONVENTIONS](GAME/10-CONVENTIONS.md) | CLAUDE.md standard, project types, workflow states, metadata files |
| 11 | [STARTUP](GAME/11-STARTUP.md) | App factory, startup sequence, configuration, debug mode |

These files differ between projects. They describe **each project's** unique features and behavior.

## Tooling

### validate.sh — Verify Completeness

Checks that all files referenced in a project's STACK.yaml actually exist.

```bash
bash validate.sh <project-name>
```

Example:
```bash
bash validate.sh GAME
```

Output:
- ✅ `OK` for each file found
- ❌ `FAIL` for missing files (exits with code 1)
- ℹ️ `INFO` for stack files that exist but aren't referenced (available for other projects)

Example run:
```
=== PROJECT Specification Validator ===
Repository: /c/Users/barlo/projects/GAME_Spec
Project: GAME
Directory: /c/Users/barlo/projects/GAME_Spec/GAME

Stack: language=python framework=flask database=sqlite frontend=bootstrap5

--- Technology Files (stack/) ---
  OK: stack/common.md
  OK: stack/python.md
  OK: stack/flask.md
  OK: stack/sqlite.md
  OK: stack/bootstrap5.md

--- Specification Files ---
  OK: 01-OVERVIEW.md
  OK: 02-DATABASE.md
  ... (all 11 files)

--- Orphan Check ---
  INFO: stack/django.md exists but not referenced (available for other projects)
  INFO: stack/postgres.md exists but not referenced (available for other projects)

=== Results ===
Errors:   0
Warnings: 0
PASSED — all referenced files exist
```

### generate-prompt.sh — Create a Build Prompt

Concatenates all technology files and spec files into a single complete prompt for an AI agent.

```bash
# Print to stdout
bash generate-prompt.sh <project-name>

# Save to file
bash generate-prompt.sh <project-name> > build-prompt.md
```

Example:
```bash
bash generate-prompt.sh GAME > build-prompt.md
```

Output structure:
1. **Header** with stack summary and instructions
2. **Technology references** in dependency order:
   - `stack/common.md`
   - `stack/python.md` (if selected)
   - `stack/flask.md` (if selected)
   - `stack/sqlite.md` (if selected)
   - `stack/bootstrap5.md` (if selected)
3. **STACK.yaml** configuration
4. **All numbered spec files** in order (01 through 11)
5. **Footer** with build instructions

Total: ~2972 lines — complete, self-contained build specification.

## How to Use

### Building a New Project

1. Create a new directory at the repo root:
   ```bash
   mkdir GAME_Spec/NEW_PROJECT
   ```

2. Create `NEW_PROJECT/STACK.yaml` with your stack selections:
   ```yaml
   language: python
   framework: flask      # or django
   database: sqlite      # or postgres
   frontend: bootstrap5

   project:
     name: myproject
     port: 5000
     output_dir: ../..

   specs:
     - 01-OVERVIEW.md
     - 02-DATABASE.md
     # ... etc
   ```

3. Write numbered spec files describing your project features (in `NEW_PROJECT/`)

4. Validate:
   ```bash
   bash validate.sh NEW_PROJECT
   ```

5. Generate the build prompt:
   ```bash
   bash generate-prompt.sh NEW_PROJECT > build-prompt.md
   ```

6. Feed `build-prompt.md` to an AI agent to build from scratch

### Process To Reverse-Engineer an Existing Project

1. Have an AI agent read the codebase
2. Generate numbered spec files describing current behavior
3. Create STACK.yaml with the detected stack
4. Run `validate.sh PROJECT` to check completeness
5. Use `generate-prompt.sh PROJECT` to create a rebuild prompt

### Switching Stacks

To rebuild the same project in a different framework:

1. Change `framework: flask` to `framework: django` in `PROJECT/STACK.yaml`
2. Update spec files where framework-specific details appear
3. Run `validate.sh PROJECT` and `generate-prompt.sh PROJECT`
4. Technology files handle the implementation patterns automatically

## Design Principles

### 1. Filename = Convention

Technology selections in STACK.yaml directly map to filenames:
- `language: python` → `../stack/python.md`
- `framework: flask` → `../stack/flask.md`
- `database: sqlite` → `../stack/sqlite.md`

No lookup tables. The naming IS the configuration.

### 2. Common Always Included

`stack/common.md` contains language-agnostic practices:
- Directory layout (bin/, data/, tests/)
- Shell script standard (headers, logging, tee)
- Links.md format
- CLAUDE.md convention
- Git hygiene
- Development workflow rules

These apply to every project, regardless of language or framework.

### 3. Prescriptive, Not Descriptive

Technology files are **prescriptive** — they tell you exactly how to do things with code examples. No ambiguity about patterns or conventions. When an AI agent reads them, it knows exactly what to build.

### 4. Project-Specific Specs

Numbered spec files describe **each project's** unique features. They reference technology files for implementation details, not duplicating them.

### 5. Tooling is Generic

`validate.sh` and `generate-prompt.sh` don't know about any specific project. They work with any project directory and any set of spec files. You can reuse them for all your projects.

## Adding New Technologies

To support a new language/framework/database/frontend:

1. Create `stack/<name>.md` where `<name>` is what you'll put in STACK.yaml
2. Follow the Rule/Implementation/Why pattern
3. Include a Summary Checklist
4. Update STACK.yaml of any project using that technology

Example: adding Django support
- Add `stack/django.md` ✓ (already exists)
- Change STACK.yaml: `framework: django`
- Run `validate.sh PROJECT` and `generate-prompt.sh PROJECT`

## SPEC_STANDARD.md

For detailed documentation of how the spec system itself works, see [SPEC_STANDARD.md](SPEC_STANDARD.md).

This document covers:
- Architecture and file organization
- Writing specification files
- STACK.yaml format
- Tooling details
- Workflows for different use cases

## Current Projects

### GAME (Command Center)

| Layer | Selection | File |
|-------|-----------|------|
| Common | *(always)* | `stack/common.md` |
| Language | Python | `stack/python.md` |
| Framework | Flask | `stack/flask.md` |
| Database | SQLite | `stack/sqlite.md` |
| Frontend | Bootstrap 5 | `stack/bootstrap5.md` |
| Port | 5001 | `GAME/STACK.yaml` |

To rebuild this project:
```bash
bash validate.sh GAME
bash generate-prompt.sh GAME > build-prompt.md
```

## Build Order for GAME

To rebuild the Command Center from this specification:

1. **Database** (02) — Create schema and helpers
2. **Models** (10) — Project type registry
3. **Scanner** (03) — Project discovery
4. **Operations** (04) — Process execution
5. **Spawn Service** (04) — Generic process spawning
6. **Publisher** (08) — Homepage generation
7. **Conventions** (10) — CLAUDE.md parsing
8. **Usage Analyzer** (10) — Token analytics
9. **Routes** (05) — All Flask routes
10. **Templates** (06) — UI pages
11. **Styling** (07) — CSS
12. **App Factory** (11) — Wire everything together

## Quick Start

```bash
# Validate all referenced files exist
bash validate.sh GAME

# Generate a complete build prompt
bash generate-prompt.sh GAME > build-prompt.md

# Feed the prompt to an AI agent
# (or use it as reference when rebuilding manually)
```

## Out of Scope for the Command Center Rebuild

- **"Your Claude" tab** — Environment/config management (`config_engine` module)
- `claude_snippets/` and `project_specifications/` directories
