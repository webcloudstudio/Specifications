# Specification System Standard

How to use the PROJECT/ directory to specify, validate, and build any project. This document is the meta-standard — it describes the spec system itself.

---

## Architecture

The spec system has two tiers:

### Tier 1: Technology Files (`stack/`)

Reusable best practices that **do not change between projects**. Each file maps to a STACK.yaml key:

| STACK.yaml Key | File | Covers |
|----------------|------|--------|
| *(always)* | `stack/common.md` | Directory layout, bin/ scripts, Links.md, CLAUDE.md, git, dev workflow |
| `language: python` | `stack/python.md` | Config, logging, testing, dependencies, startup validation |
| `framework: flask` | `stack/flask.md` | App factory, blueprints, Jinja2, HTMX, test client |
| `framework: django` | `stack/django.md` | Settings, ORM, migrations, admin, django-htmx |
| `database: sqlite` | `stack/sqlite.md` | Connection, PRAGMAs, JSON columns, migrations, backup |
| `database: postgres` | `stack/postgres.md` | Pooling, JSONB, numbered migrations, indexing, backup |
| `frontend: bootstrap5` | `stack/bootstrap5.md` | CDN setup, dark theme, components, HTMX integration |

### Tier 2: Specification Files (numbered, `NN-NAME.md`)

Project-specific files that describe **what to build**. These reference technology files for implementation details.

```
01-OVERVIEW.md       # Purpose, features, dependencies
02-DATABASE.md       # Schema, tables, data patterns
03-SCANNER.md        # Feature: project discovery
...
11-STARTUP.md        # App initialization sequence
```

---

## STACK.yaml

The manifest file that ties everything together. Every project has one.

```yaml
# --- Technology Stack ---
language: python          # → stack/python.md
framework: flask          # → stack/flask.md
database: sqlite          # → stack/sqlite.md
frontend: bootstrap5      # → stack/bootstrap5.md

# --- Project Configuration ---
project:
  name: myproject
  title: My Project
  description: What it does
  port: 5001
  output_dir: ..          # Where to write generated code (relative to PROJECT/)
  venv: true              # Whether to use a Python venv

# --- Standard Directories ---
directories:
  data: data
  logs: data/logs
  backups: data/backups
  tests: tests
  static: static
  templates: templates
  scripts: bin
  docs: docs

# --- Environment Variables ---
env:
  required:
    - PROJECTS_DIR
  optional:
    - SECRET_KEY

# --- Database Config ---
database_config:
  path: data/app.db
  wal_mode: true
  foreign_keys: true

# --- Spec Files ---
specs:
  - 01-OVERVIEW.md
  - 02-DATABASE.md
  # ... all numbered spec files
```

### Key Naming Convention

The `language`, `framework`, `database`, and `frontend` values must exactly match filenames in `stack/` (without `.md`). This is how the tooling resolves files.

---

## File Organization

The spec system lives in a repository root that hosts multiple projects:

```
GAME_Spec/                  ← Repository root
├── stack/                  # Technology files (shared, reusable)
│   ├── common.md           # Always included
│   ├── python.md           # language: python
│   ├── flask.md            # framework: flask
│   ├── django.md           # framework: django
│   ├── sqlite.md           # database: sqlite
│   ├── postgres.md         # database: postgres
│   └── bootstrap5.md       # frontend: bootstrap5
├── validate.sh             # Generic validation tool (takes project name)
├── generate-prompt.sh      # Generic prompt generator (takes project name)
├── README.md               # Repository overview
├── SPEC_STANDARD.md        # This document
│
└── GAME/                   ← First project (PROJECT_NAME)
    ├── STACK.yaml          # Manifest: declares stack + config
    ├── 01-OVERVIEW.md      # Spec files (project-specific)
    ├── 02-DATABASE.md
    ├── ...
    └── 11-STARTUP.md

└── OTHER_PROJECT/         ← Another project (same structure)
    ├── STACK.yaml
    ├── 01-*.md
    └── ... more specs ...
```

Each project directory (`GAME/`, `OTHER_PROJECT/`, etc.) contains:
- One `STACK.yaml` manifest
- Numbered spec files (`01-*.md` through `11-*.md` or more)
- No local copies of scripts or stack files (these are shared at the repo root)

---

## Writing Specification Files

### Numbered Spec Files (Tier 2)

Rules:
- Prefix with two-digit number: `01-`, `02-`, etc.
- Use ALL CAPS hyphenated names: `02-DATABASE.md`, `05-ROUTES-API.md`
- Each file covers one aspect of the system
- Reference technology files for implementation patterns: `> See stack/sqlite.md`
- Include concrete details: schema DDL, route paths, template names, config values
- These files describe **this project** — they will differ between projects

### Technology Files (Tier 1)

Rules:
- Live in `stack/` directory
- Filename matches the STACK.yaml value: `flask.md`, `sqlite.md`, `bootstrap5.md`
- Each section follows the pattern: **Rule** → **Implementation** (code) → **Why**
- Include a **Summary Checklist** at the end
- State prerequisites: `Prerequisites: stack/common.md, stack/python.md`
- **Never contain project-specific details** — these must work for any project

---

## Tooling

Scripts live at the repository root and take a project name as an argument.

### validate.sh

Checks that all files referenced in a project's STACK.yaml actually exist.

```bash
bash validate.sh <project-name>
```

Example:
```bash
bash validate.sh GAME
```

Output:
- `OK` for each file found
- `FAIL` for missing files (exits with code 1)
- `INFO` for stack files that exist but aren't referenced (available for other projects)
- `WARN` for missing supporting files (README, SPEC_STANDARD)

### generate-prompt.sh

Concatenates technology files and a project's spec files into a single build prompt.

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

The generated prompt includes:
1. Project header with stack summary
2. All referenced technology files (in dependency order)
3. STACK.yaml configuration
4. All numbered spec files (in order)

Feed this prompt to an AI agent to build the project from scratch.

---

## Workflows

### Building a New Project

1. Create a new project directory at the repo root: `mkdir PROJECT_NAME`
2. Create `PROJECT_NAME/STACK.yaml` with your technology selections
3. Set `output_dir: ../..` to output code to the repo parent directory
4. Write numbered spec files (`01-*.md`, `02-*.md`, etc.) describing your features
5. Run `bash validate.sh PROJECT_NAME` to check completeness
6. Run `bash generate-prompt.sh PROJECT_NAME > build-prompt.md` to create the prompt
7. Feed `build-prompt.md` to an AI agent

### Reverse-Engineering an Existing Project

1. Have an AI agent read the codebase
2. Generate numbered spec files describing current behavior
3. Create `PROJECT_NAME/STACK.yaml` with the detected stack
4. Run `bash validate.sh PROJECT_NAME` to verify completeness
5. Use `bash generate-prompt.sh PROJECT_NAME > build-prompt.md` to create a rebuild prompt
6. Build into the same or different stack by swapping technology files

### Switching Stacks

To rebuild the same project in a different framework:
1. Change `framework: flask` to `framework: django` in `PROJECT_NAME/STACK.yaml`
2. Update spec files where framework-specific details appear (routes, templates)
3. Run `bash validate.sh PROJECT_NAME` and `bash generate-prompt.sh PROJECT_NAME`
4. Technology files handle the implementation patterns automatically

---

## Adding New Technology Files

To support a new technology:

1. Create `stack/<name>.md` where `<name>` matches what you'll put in STACK.yaml
2. Follow the template: prerequisites, numbered sections, Rule/Implementation/Why, summary checklist
3. Add standard bin/ scripts for the technology
4. The file should be complete enough to implement any project using that technology

Example: adding Node.js support

```
stack/node.md           # language: node
stack/express.md        # framework: express
stack/astro.md          # framework: astro
```

---

## Summary

| What | Where | Changes per project? |
|------|-------|---------------------|
| Stack selection | STACK.yaml | Yes — pick your technologies |
| How to implement | stack/*.md | No — reusable standards |
| What to build | NN-*.md | Yes — project features |
| Validation | validate.sh | No — generic tool |
| Prompt generation | generate-prompt.sh | No — generic tool |
