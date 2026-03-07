# Command Center — Complete Project Specification System

This  **two-tier specification system** specification will rebuild AiManagmentstudio from scratch

Specification Files are prefixed with a numeric - the remaining files specify implemntation.

## Overview

The spec system separates **what to build** (project-specific) from **how to build it** 

```
STACK.yaml  ← Declares your stack selections
    ↓
stack/          ← Technology files (reusable, don't change per project)
├── common.md    (always included)
├── python.md    (if language: python)
├── flask.md     (if framework: flask)
├── django.md    (if framework: django)
├── sqlite.md    (if database: sqlite)
├── postgres.md  (if database: postgres)
└── bootstrap5.md (if frontend: bootstrap5)
    ↓
01-OVERVIEW.md ... 11-STARTUP.md  ← Spec files (project-specific)
    ↓
generate-prompt.sh  ← Creates a complete build prompt
```

## Key Files

### STACK.yaml — The Manifest

Declares technology selections and project configuration:

```yaml
language: python       # → stack/python.md
framework: flask       # → stack/flask.md
database: sqlite       # → stack/sqlite.md
frontend: bootstrap5   # → stack/bootstrap5.md

project:
  name: commandcenter
  port: 5001
  output_dir: ..

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

**Key insight**: The `language`, `framework`, `database`, and `frontend` values map directly to **filenames in stack/**. This is the mapping system — no lookup table needed.

### stack/ — Technology Reference Files

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

### Numbered Spec Files (01-11) — Project Specification

Project-specific descriptions of **what to build**. These reference technology files for implementation details.

| # | File | Covers |
|---|------|--------|
| 01 | [OVERVIEW](01-OVERVIEW.md) | Purpose, tech stack, dependencies, directory layout, navigation |
| 02 | [DATABASE](02-DATABASE.md) | SQLite schema, tables, extra JSON column, migrations, data access |
| 03 | [SCANNER](03-SCANNER.md) | Project discovery, tech stack detection, git operations, metadata parsing |
| 04 | [OPERATIONS](04-OPERATIONS.md) | ops.py server/one-shot execution, spawn.py generic process service |
| 05 | [ROUTES-API](05-ROUTES-API.md) | All Flask routes, HTMX API endpoints, request/response patterns |
| 06 | [UI-TEMPLATES](06-UI-TEMPLATES.md) | Template hierarchy, page layouts, component structure |
| 07 | [STYLING](07-STYLING.md) | CSS custom properties, component classes, design system |
| 08 | [PUBLISHER](08-PUBLISHER.md) | GitHub Pages pipeline, card rendering, Astro generation |
| 09 | [PROCESSES](09-PROCESSES.md) | Process monitor, bin/ scripts, ETL, scheduling |
| 10 | [CONVENTIONS](10-CONVENTIONS.md) | CLAUDE.md standard, project types, workflow states, metadata files |
| 11 | [STARTUP](11-STARTUP.md) | App factory, startup sequence, configuration, debug mode |

These files will differ between projects. They describe **this specific project's** features and behavior.

## Tooling

### validate.sh — Verify Completeness

Checks that all files referenced in STACK.yaml actually exist.

```bash
bash PROJECT/validate.sh
```

Output:
- ✅ `OK` for each file found
- ❌ `FAIL` for missing files (exits with code 1)
- ℹ️ `INFO` for stack files that exist but aren't referenced (available for other projects)

Example run:
```
=== PROJECT Specification Validator ===
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
bash PROJECT/generate-prompt.sh

# Save to file
bash PROJECT/generate-prompt.sh > build-prompt.md
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

1. Create `PROJECT/` directory with:
   - Copy of `STACK.yaml` (edit to declare your stack)
   - Copy of `stack/` directory (shared between projects)
   - Your numbered spec files (`01-*.md` through `NN-*.md`)
   - `validate.sh` and `generate-prompt.sh` scripts

2. Edit `STACK.yaml` with your selections:
   ```yaml
   language: python
   framework: flask      # or django
   database: sqlite      # or postgres
   frontend: bootstrap5
   ```

3. Write numbered spec files describing your project features

4. Validate:
   ```bash
   bash PROJECT/validate.sh
   ```

5. Generate the build prompt:
   ```bash
   bash PROJECT/generate-prompt.sh > build-prompt.md
   ```

6. Feed `build-prompt.md` to an AI agent to build from scratch

### Process To Reverse-Engineer an Existing Project

1. Have an AI agent read the codebase
2. Generate numbered spec files describing current behavior. Rules 
3. Create STACK.yaml with the detected stack
4. Run `validate.sh` to check completeness
5. Use `generate-prompt.sh` to create a rebuild prompt

### Switching Stacks

To rebuild the same project in a different framework:

1. Change `framework: flask` to `framework: django` in STACK.yaml
2. Update spec files where framework-specific details appear
3. Run `validate.sh` and `generate-prompt.sh`
4. Technology files handle the implementation patterns automatically

## Design Principles

### 1. Filename = Convention

Technology selections in STACK.yaml directly map to filenames:
- `language: python` → `stack/python.md`
- `framework: flask` → `stack/flask.md`
- `database: sqlite` → `stack/sqlite.md`

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

Numbered spec files describe **this project's** unique features. They reference technology files for implementation details, not duplicating them.

### 5. Tooling is Generic

`validate.sh` and `generate-prompt.sh` don't know about Command Center specifically. They work with any STACK.yaml and any set of spec files. You can reuse them for all your projects.

## Adding New Technologies

To support a new language/framework/database/frontend:

1. Create `stack/<name>.md` where `<name>` is what you'll put in STACK.yaml
2. Follow the Rule/Implementation/Why pattern
3. Include a Summary Checklist
4. Update STACK.yaml of any project using that technology

Example: adding Django support
- Add `stack/django.md` ✓ (already exists)
- Change STACK.yaml: `framework: django`
- Run `validate.sh` and `generate-prompt.sh`

## SPEC_STANDARD.md

For detailed documentation of how the spec system itself works, see [SPEC_STANDARD.md](SPEC_STANDARD.md).

This document covers:
- Architecture and file organization
- Writing specification files
- STACK.yaml format
- Tooling details
- Workflows for different use cases

## Current Stack (Command Center)

| Layer | Selection | File |
|-------|-----------|------|
| Common | *(always)* | `stack/common.md` |
| Language | Python | `stack/python.md` |
| Framework | Flask | `stack/flask.md` |
| Database | SQLite | `stack/sqlite.md` |
| Frontend | Bootstrap 5 | `stack/bootstrap5.md` |
| Port | 5001 | `STACK.yaml` |

## Build Order

To rebuild from this specification:

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
bash PROJECT/validate.sh

# Generate a complete build prompt
bash PROJECT/generate-prompt.sh > build-prompt.md

# Feed the prompt to an AI agent
# (or use it as reference when rebuilding manually)
```

## Out of Scope for the Command Center Rebuild

- **"Your Claude" tab** — Environment/config management (`config_engine` module)
- `claude_snippets/` and `project_specifications/` directories
