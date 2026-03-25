OneShot (build): oneshot/GAME/2026-03-22.1 → 1e7cf07

Changes since oneshot/GAME/2026-03-21.1:
 GAME/DATABASE.md      |   4 +-
 GAME/FEATURE_MAP.md   | 474 --------------------------------------------------
 GAME/FUNCTIONALITY.md | 126 +++++++++++++-
 GAME/INTENT.md        |  25 ---
 GAME/METADATA.md      |   1 +
 GAME/README.md        |   5 +-
 GAME/index.html       |   6 +-
 7 files changed, 132 insertions(+), 509 deletions(-)

# OneShot Prompt: GAME

You are building **GAME** — Dashboard for managing, monitoring, and operating AI-assisted projects.
OneShot tag: `oneshot/GAME/2026-03-22.1` (commit 1e7cf07)

## Stack
- Python
- Flask
- SQLite
- Bootstrap5
- Port: 5001

## Instructions
1. Read the CONVERSION RULES — they explain how concise specs should be interpreted
2. Read the INTEGRATION STANDARD (CLAUDE_RULES) — project structure requirements
3. Read ALL technology references — they define HOW to implement (prescriptive)
4. Read ALL specification files — they define WHAT to implement
5. Build the complete application following all patterns exactly

---

# CONVERSION RULES

---

## CONVERT.md (RulesEngine/CONVERT.md)

# Specification Conversion Rules

**Version:** 20260320 V1  
**Description:** Rules for expanding concise spec files into implementation-ready detailed specs

**How to expand concise project specs into detailed, implementation-ready specifications.**

These rules are global — they apply to all projects regardless of stack. Stack-specific expansion is handled by the corresponding `stack/*.md` file.

---

## Expansion Principles

1. **The spec author writes the WHAT.** Column names, screen layouts, triggers, sequences.
2. **The conversion expands the HOW.** Types, defaults, constraints, HTMX attributes, error handling — all inferred from stack rules and conventions.
3. **Stack implies conventions.** If METADATA.md says `stack: Python/Flask/SQLite`, apply every pattern from `stack/python.md`, `stack/flask.md`, `stack/sqlite.md` without the author restating them.
4. **Don't duplicate stack rules into specs.** If `stack/sqlite.md` says "WAL mode, FK pragma, Row factory" then DATABASE.md should NOT repeat that. The build prompt includes both.
5. **[ROADMAP] items preserve intent only.** Do not expand implementation detail for roadmap features. Keep the description and Open Questions.

---

## DATABASE.md Expansion

**Author writes:** table name, column names, types, and brief notes.

**Conversion adds:**
- `DEFAULT` clauses (infer from type: TEXT timestamps get `datetime('now')`, booleans get `0`, JSON gets `'{}'`)
- `NOT NULL` where the column is required (PKs, unique slugs, FKs)
- `UNIQUE` constraints noted in the author's comments
- FK references with `REFERENCES table(column)` syntax
- Index suggestions for columns used in WHERE/JOIN (prefix with `-- INDEX:`)
- The `_add_column_if_missing()` migration list from the column inventory
- Convention notes: WAL, FK pragma, JSON blob pattern — all from `stack/sqlite.md`

**Example — author writes:**

```markdown
## projects
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT | unique, machine slug |
| status | TEXT | IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED |
| extra | JSON | |
| created_at | TEXT | timestamp |
```

**Conversion expands to full CREATE TABLE with defaults, constraints, indexes.**

---

## SCREEN-*.md Expansion

**Author writes:** route, columns/sections, interactions, Open Questions.

**Conversion adds:**
- HTMX attributes for each interaction (`hx-post`, `hx-target`, `hx-swap`)
- Server response type (HTML fragment vs full page)
- Reference to UI.md shared components used (nav bar, standard row header, filter bar)
- Flash message patterns for success/error states
- `columns=` directive mapped to Bootstrap grid or table layout

---

## FEATURE-*.md Expansion

**Author writes:** trigger, sequence (numbered steps), reads, writes, Open Questions.

**Conversion adds:**
- Route/endpoint signatures (method, path, return type)
- Event emissions (from the platform event model)
- Error handling pattern (catch at route, flash to user, log to platform, never crash)
- Concurrency notes (one instance per project, async where noted)
- Cross-references to SCREEN-*.md files that render this feature's output

---

## UI.md Expansion

**Author writes:** component name, purpose, key visual details.

**Conversion adds:**
- Bootstrap 5 class names and markup patterns
- CSS variable references (`--cc-surface`, `--cc-border`, etc.)
- HTMX loading states and swap targets
- Responsive behavior notes (desktop-first, 1024px minimum)

---

## ARCHITECTURE.md Expansion

**Author writes:** module names, responsibilities, directory layout.

**Conversion adds:**
- Import relationships between modules
- Public function signatures (name, params, return)
- Data flow arrows showing which module calls which
- Template directory structure with partial naming conventions

---

## Naming Conventions

| Prefix | Contains | Example |
|--------|----------|---------|
| `METADATA.md` | Project identity fields | Always present |
| `README.md` | One-line project description | Always present |
| `INTENT.md` | Why the project exists | Always present |
| `DATABASE.md` | Tables and columns | If project has a database |
| `UI.md` | Shared visual patterns | If project has a UI |
| `ARCHITECTURE.md` | Code organization | Always present |
| `SCREEN-{Name}.md` | Per-screen specification | One per screen |
| `FEATURE-{Name}.md` | Cross-cutting behavior | One per major feature |

**Screen names** match the nav bar label: `SCREEN-Dashboard.md`, `SCREEN-Configuration.md`.

**Feature names** describe the capability: `FEATURE-Scan.md`, `FEATURE-Operations.md`.

---

## Open Questions Section

Spec files end with `## Open Questions` — except README.md, METADATA.md, and INTENT.md which do not have this section.

```markdown
## Open Questions
- Question about a design decision not yet resolved
- Question about scope or approach
```

Open Questions are preserved through conversion. They signal to the builder "ask the human before deciding." Agents add new questions to this section rather than creating new files.

---

## Build Tags

When `bin/build.sh` runs, it creates an annotated git tag:

```
build/{project}/{YYYY-MM-DD.N}
```

Annotated tags are permanent git objects — never pruned by `git gc`. This preserves the exact spec state used for each build. Diff between builds:

```bash
git diff build/Game-Build/2026-03-19.1..build/Game-Build/2026-03-19.2 -- Game-Build/
```

---

## Pipeline

```
setup.sh  →  (author edits)  →  validate.sh  →  convert.sh  →  build.sh
   CREATE             DRAFT            VALIDATED       CONVERTED       BUILT
```

| Step | Script | Output |
|------|--------|--------|
| CREATE | `bin/setup.sh <name> ["desc"]` | Spec directory with template files |
| DRAFT | (author edits files) | Concise specs |
| VALIDATED | `bin/validate.sh <name>` | Exit 0 = ready, exit 1 = fix issues |
| CONVERTED | `bin/convert.sh <name> > convert-prompt.md` | Detailed specs (optional — build handles inline) |
| BUILT | `bin/build.sh <name> > build-prompt.md` | Tagged commit + complete build prompt |
| PROMOTED | (copy spec dir to own repo) | Independent project |

One-shot path: skip CONVERTED, go straight from VALIDATED to BUILT. `bin/build.sh` includes CONVERT.md so the AI agent handles expansion and building in a single pass.


# PROJECT INTEGRATION STANDARD

---

## CLAUDE_RULES.md

# CLAUDE_RULES_START

> Generated by `bin/generate_claude_rules.sh` — do not edit directly.
> Edit `RulesEngine/BUSINESS_RULES.md` then regenerate.

# DEFAULT DEVELOPMENT RULES

**Version:** 20260320 V1  
**Description:** Agent behavior contract distributed to all AI agent projects — covers git, error handling, and completion standards

Full specification and methodology: `Specifications/AGENTS.md` in the Specifications repository. This condensed version covers agent behavior only.

---

## Git Workflow

1. Commit immediately after completing a task with no errors.
2. Commit messages: descriptive text, no "Claude"/"Anthropic"/"AI" mentions.
3. DO NOT push — local commits only.
4. NO co-authored-by lines.

Web server changes: print "No restart needed — browser refresh is enough." (templates/CSS/static only) or "Restart required — `./bin/start.sh`." (Python/JS server files).

---

## Project Layout

```
ProjectName/
  METADATA.md       Identity (name, port, status, stack, etc.)
  AGENTS.md         AI context: dev commands, endpoints, architecture
  CLAUDE.md         Contains only: @AGENTS.md
  .env.sample       Required env vars (committed)
  .env              Actual env vars (never committed)
  bin/              All executable scripts
    common.sh       Shared functions — sourced by all bash scripts
    common.py       Shared OperationContext — imported by Python scripts
  doc/              Generated documentation
  logs/             Log files (gitignored)
  data/             Persistent data
  tests/            Test suite
```

---

## Scripts (`bin/`)

All scripts live in `bin/` — bash (`.sh`) or Python (`.py`). The `# CommandCenter Operation` marker in the first 20 lines registers a script with the platform.

**Standard script names** (only create what the project needs):

| Script | Purpose | Name String
|--------|---------|
| `bin/start.sh` | Start service — service projects only | Stop Service |
| `bin/stop.sh` | Stop service — service projects only | Stop Service |
| `bin/build.sh` | Build / compile / package | Build |
| `bin/daily.sh` | Daily maintenance | Daily Batch |
| `bin/weekly.sh` | Weekly maintenance | Weekly Batch |
| `bin/build_documentation.sh` | Generate doc/ output | Build Doc |
| `bin/deploy.sh` | Deploy to environment | Deploy |

If the script name matches a Standard Script Name the following header should exist with a Name: field matching the Name String.  If possible
these should be the first lines of the file and there should be no other "# Name:" or "# Category:" fields.

#!/bin/bash
# CommandCenter Operation
# Name: {Name String}
# Category: Operations

**Bash** — source `common.sh` then add functionality:

```bash
#!/bin/bash
# CommandCenter Operation
# Category: service
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

# your start command — use $PORT for the service port
# e.g. Flask: export FLASK_DEBUG=1 && flask run --port "$PORT"
```

`common.sh` handles everything: `SCRIPT_NAME`, `PROJECT_DIR`, `cd`, `PROJECT_NAME`, `PORT`, venv activation, `.secrets`/`.env` loading, timestamped log file, SIGTERM trap, and the `[$PROJECT_NAME] Starting:` message. Use `$PORT` as the service port — never hardcode a port number. Override the trap after sourcing if the script needs custom cleanup.

**Python** — import `common.py` then add functionality:

```python
#!/usr/bin/env python3
# CommandCenter Operation
# Category: maintenance
import sys, os; sys.path.insert(0, os.path.dirname(__file__)); from common import op

def main(ctx):
    # ctx.project_name, ctx.port, ctx.logger available — use ctx.port as the service port
    pass

if __name__ == '__main__':
    op(__file__).run(main)
```

`op(__file__).run(main)` handles the same concerns as `common.sh`: path setup, METADATA.md parsing, env loading, logging, SIGTERM, and status messages.

Use Linux line endings (no `\r`). Run `chmod +x bin/*.sh`.

---

## METADATA.md

**Authoritative source for project identity.** Always read `name`, `display_name`, `short_description`, and `git_repo` from this file — never infer them from directory names. Present in every set-up project.

Key-value format (not YAML):

```
# AUTHORITATIVE PROJECT METADATA - THE FIELDS IN THIS FILE SHOULD BE CURRENT

name: MyProject                              # machine slug, matches directory name
display_name: My Project                     # human-readable name for UI/display
git_repo: https://github.com/org/MyProject   # full HTTPS URL, for links only
port: 8000                                   # omit if not a service
short_description: One sentence.             # shown in dashboards and indexes
health: /health                              # omit if not a service
status: PROTOTYPE                            # IDEA|PROTOTYPE|ACTIVE|PRODUCTION|ARCHIVED
stack: Python/Flask/SQLite                   # slash-separated, used by generate_prompt.sh
version: 2026-03-16.1                        # YYYY-MM-DD.N, increment on releases
updated: 20260316_120000                     # set automatically by platform scripts
```

`port`, `health`, `stack`, and `status` are platform fields — managed by GAME and platform scripts, not needed for day-to-day agent work. `git_repo` SSH remotes are normalised to HTTPS automatically.

---

## AGENTS.md Required Sections

```markdown
## Dev Commands
- Start: `./bin/start.sh`   # service projects only
- Stop: `./bin/stop.sh`     # service projects only
- Test: `./bin/test.sh`     # if tests exist

## Service Endpoints        # omit if not a service
- Local: http://localhost:PORT

## Bookmarks
- [Documentation](doc/index.html)
```

Only include commands and endpoints that actually exist for the project.

# CLAUDE_RULES_END


# TECHNOLOGY REFERENCES

---

## Common Practices (stack/common.md)

# Common Best Practices

**Version:** 20260320 V1  
**Description:** Common development patterns shared across all stack configurations

Always included regardless of technology stack. Covers project structure conventions, shell scripts, metadata files, git hygiene, and development workflow. This file does not change between projects.

---

## 1. Project Directory Layout

**Rule**: Every project follows a predictable directory structure.

```
project-name/
├── bin/                # Operation scripts (see Shell Scripts section)
├── data/               # Runtime data (DB, logs, backups) — gitignored
│   ├── logs/           # Script and process output logs
│   └── backups/        # Database and file backups
├── docs/               # Project documentation
├── tests/              # Test suite
├── PROJECT/            # Build specification (optional, for spec-driven projects)
├── .env                # Environment config — gitignored
├── .env.example        # Template with placeholder values — committed
├── .gitignore
├── CLAUDE.md           # AI agent instructions
└── Links.md            # External links
```

Additional directories depend on the stack (e.g., `templates/`, `static/`, `migrations/`).

**Why**: Consistent layout lets any developer or AI agent locate files instantly.

---

## 2. Shell Scripts (bin/ Directory)

**Rule**: All user-facing operations live in `bin/` as bash scripts with standardized headers, logging, and error handling.

### Script Template

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Human Readable Name
# Type: daemon|batch
# Port: 8000

# --- Standard Preamble ---
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_DIR/data/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
SCRIPT_NAME=$(basename "$0" .sh)
LOG_FILE="$LOG_DIR/${SCRIPT_NAME}_${TIMESTAMP}.log"

echo "=== $SCRIPT_NAME started at $(date '+%Y-%m-%d %H:%M:%S') ===" | tee "$LOG_FILE"
echo "Arguments: $*" | tee -a "$LOG_FILE"
echo "Working dir: $PROJECT_DIR" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

cd "$PROJECT_DIR"

# --- Your Commands Here ---
# All output goes to both console and log file via tee
your_command 2>&1 | tee -a "$LOG_FILE"

echo "=== $SCRIPT_NAME finished at $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$LOG_FILE"
```

### Header Fields

The first comment block is parsed by Command Center's scanner for auto-discovery:

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `# CommandCenter Operation` | Yes | literal | Marks script as discoverable |
| `# Name:` | Yes | free text | Display name in UI |
| `# Type:` | No | `daemon` or `batch` | Default: `batch`. Daemons stay running. |
| `# Port:` | No | integer | Port number for daemon services |

Scripts without the `# CommandCenter Operation` header are still valid scripts but won't appear in Command Center's UI.

### Standard Scripts

Every project should have these scripts (where applicable):

| Script | Type | Purpose |
|--------|------|---------|
| `bin/start.sh` | daemon | Start the dev server |
| `bin/stop.sh` | batch | Stop the dev server |
| `bin/test.sh` | batch | Run test suite |
| `bin/build.sh` | batch | Build/compile the project |
| `bin/deploy.sh` | batch | Deploy to production |
| `bin/backup.sh` | batch | Backup data/database |

### Logging Pattern

- All stdout and stderr captured via `tee` to `data/logs/`
- Log filename includes script name and timestamp: `start_2026-03-07_143022.log`
- First lines of log always record: timestamp, arguments, working directory
- These logs are viewable from Command Center's Process Monitor

**Why**: Standardized scripts make every project operable the same way. Log capture enables monitoring, alerting, and post-mortem analysis.

---

## 3. External Links (Links.md)

**Rule**: Every project maintains a `Links.md` file at its root with a markdown table of relevant URLs.

```markdown
| Label | URL |
|-------|-----|
| Local Dev | http://localhost:5001 |
| Production | https://example.com |
| Docs | https://docs.example.com |
| GitHub | https://github.com/user/repo |
```

Rules:
- One table, two columns: Label and URL
- Labels are short and descriptive
- Command Center's scanner reads this on startup and stores links in the project's `extra` JSON
- Links appear in the project's configuration page

**Why**: Centralizes all project URLs in one discoverable, parseable location. Both AI agents and Command Center consume it.

---

## 4. CLAUDE.md Convention

**Rule**: Every project has a `CLAUDE.md` at its root following this section structure:

1. `## Project Overview` — What the project does, key features
2. `## Architecture` — Tech stack, key files, patterns
3. `## Dev Commands` — Bash commands to run the project (in a code block)
4. `## Service Endpoints` — URLs: `- Label: https://url`
5. `## Bookmarks` — Grouped links: `### Group` then `- [Title](URL)`

Section rename rules — always use the standard name:
- `## Commands` / `## Development Commands` / `## Build Commands` → `## Dev Commands`
- `## Overview` / `## Project Purpose` → `## Project Overview`
- `## Stack` → `## Architecture`

**Why**: Consistent structure lets AI agents parse project context reliably.

---

## 5. Git Hygiene

**Rule**: Maintain a comprehensive `.gitignore`. Never commit secrets, generated files, or runtime data.

```gitignore
# Runtime
data/
*.db
*.log

# Environment
.env
venv/
node_modules/

# Python
__pycache__/
*.pyc
*.egg-info/
dist/
build/

# OS
.DS_Store
Thumbs.db
```

Rules:
- `data/` — runtime databases, logs, backups, uploads
- `.env` — secrets and local config
- Commit `.env.example` with placeholder values
- Write imperative commit messages: "Add health endpoint" not "Added health endpoint"

**Why**: Clean repos are cloneable and runnable. No secrets in history.

---

## 6. Development Workflow

**Rule**: Follow these rules when working in any git-managed project.

1. **Always commit changes immediately** after completing a task if the task has no errors
2. **Commit messages** should have descriptive text (no AI/tool mentions)
3. **DO NOT push** — only commit to local git
4. **NO co-authored-by lines** in commits
5. **Always end code change responses with a restart notice** for any project that runs a web server:
   - If only templates/CSS/static files changed: "No restart needed — browser refresh is enough."
   - If any Python/JS server files changed: "Restart required — run the start script or equivalent."

**Why**: Consistent workflow prevents accidental pushes, keeps commit history clean, and ensures developers know when to restart.

---

## Summary Checklist

- [ ] Standard directory layout with `bin/`, `data/`, `docs/`, `tests/`
- [ ] Shell scripts in `bin/` with CommandCenter headers and tee logging
- [ ] `Links.md` for external URLs
- [ ] `CLAUDE.md` following section convention
- [ ] `.env.example` committed, `.env` gitignored
- [ ] Comprehensive `.gitignore`
- [ ] Commit immediately, don't push, no AI mentions


---

## Python (stack/python.md)

# Python Best Practices

**Version:** 20260320 V1  
**Description:** Python language conventions and patterns for spec-driven projects

Technology reference for Python development. Framework-agnostic — applies to any Python project. This file does not change between projects.

Prerequisite: `stack/common.md`

---

## 1. Configuration Management

**Rule**: Use environment variables loaded via `python-dotenv`. Never hardcode secrets, ports, or paths.

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-me')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/app.db')
    DEBUG = False

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']  # Crash if missing in prod

class TestConfig(Config):
    DATABASE_PATH = ':memory:'
    TESTING = True
```

```bash
# .env
SECRET_KEY=your-secret-here
DATABASE_PATH=data/app.db
APP_PORT=5001
```

**Why**: Config classes make environment switching explicit. Crashing on missing secrets in prod prevents silent misconfiguration.

---

## 2. Logging

**Rule**: Use Python's `logging` module with named loggers, never `print()`. Configure formatters and handlers at startup.

```python
import logging
import os

def setup_logging(level=None):
    level = level or ('DEBUG' if os.getenv('APP_DEBUG') else 'INFO')

    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console)

    # File handler
    os.makedirs('data/logs', exist_ok=True)
    file_handler = logging.FileHandler('data/logs/app.log')
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)
```

```python
# In any module
import logging
logger = logging.getLogger(__name__)

logger.info('Server starting on port %s', port)
logger.error('Failed to connect: %s', err)
```

**Why**: Named loggers trace messages to source modules. Structured format enables log parsing.

---

## 3. Environment Separation

**Rule**: Maintain distinct configs for dev/test/prod. Never run debug mode in production.

| Setting | Dev | Test | Prod |
|---------|-----|------|------|
| DEBUG | True | False | False |
| DATABASE | data/app.db | :memory: | data/app.db |
| SECRET_KEY | hardcoded default | hardcoded default | env var (required) |
| LOGGING | DEBUG | WARNING | INFO |

**Why**: Environment separation prevents dev shortcuts from reaching production.

---

## 4. Testing

**Rule**: Use `pytest` with fixtures. Isolate each test with a fresh database. Test at the boundary, not internals.

```python
# tests/conftest.py
import pytest

@pytest.fixture
def db():
    """Provide a clean in-memory database for each test."""
    from db import get_db, init_db
    init_db(':memory:')
    yield get_db()
```

```python
# tests/test_ops.py
def test_create_project(db):
    from ops import create_project
    project = create_project(db, title='Test')
    assert project is not None
    row = db.execute('SELECT * FROM projects WHERE title = ?', ('Test',)).fetchone()
    assert row is not None
```

**Why**: Fixtures ensure clean state per test. In-memory DB makes tests fast.

---

## 5. Security Basics

**Rule**: Validate all user input. Use parameterized queries exclusively. Never trust client data.

Checklist:
- Parameterized queries for all DB operations (`?` placeholders, never f-strings)
- `secure_filename()` for any file path from user input
- Length and type validation on inputs
- Secret key loaded from environment, not hardcoded in prod
- Never expose stack traces to end users

**Why**: These basics prevent the most common attack vectors with minimal effort.

---

## 6. Dependency Management

**Rule**: Pin exact versions in `requirements.txt`. Always use virtual environments. Keep dependencies minimal.

```bash
python -m venv venv
source venv/bin/activate
pip install flask python-dotenv
pip freeze > requirements.txt
```

```
# requirements.txt — pin exact versions
Flask==3.1.0
python-dotenv==1.0.1
```

Rules:
- One `requirements.txt` at project root
- Pin exact versions (`==`), not ranges
- `pip freeze > requirements.txt` after any install
- Keep it small — prefer stdlib over third-party
- `venv/` directory is always gitignored

**Why**: Pinned versions ensure reproducible builds. Fewer dependencies mean fewer security vulnerabilities.

---

## 7. Health Check and Startup Validation

**Rule**: Validate required config and DB connectivity at startup. Crash early on misconfiguration.

```python
def validate_startup():
    """Crash early if critical config is missing."""
    required_vars = ['PROJECTS_DIR']
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        raise RuntimeError(f'Missing required env vars: {", ".join(missing)}')

    from db import get_db
    try:
        get_db().execute('SELECT 1')
    except Exception as e:
        raise RuntimeError(f'Database not accessible: {e}')

    logger.info('Startup validation passed')
```

**Why**: Startup validation catches misconfigurations immediately rather than at first user request.

---

## 8. Project Directory Layout (Python-specific)

Python web projects extend the common layout:

```
project-name/
├── app.py              # Entry point / app factory
├── routes.py           # Route handlers
├── models.py           # Data models and type registries
├── db.py               # Database connection, schema, migrations
├── ops.py              # Business logic and operations
├── config.py           # Config classes (Dev/Prod/Test)
├── templates/          # Jinja2 or Django templates
│   ├── base.html
│   └── types/          # Type-specific partials
├── static/
│   ├── css/
│   └── js/
├── tests/
│   ├── conftest.py
│   └── test_*.py
├── bin/                # (from common.md)
├── data/               # (from common.md)
├── requirements.txt
├── .env
├── .gitignore
├── CLAUDE.md
└── Links.md
```

---

## Summary Checklist

- [ ] Config via env vars with `python-dotenv`, no hardcoded secrets
- [ ] Logging with named loggers, not `print()`
- [ ] Distinct dev/test/prod configs
- [ ] pytest with fixtures and isolated test DB
- [ ] Input validation, parameterized queries
- [ ] Pinned dependencies in requirements.txt, venv gitignored
- [ ] Startup validation for required config


---

## Flask (stack/flask.md)

# Flask Best Practices

**Version:** 20260320 V1  
**Description:** Flask web framework patterns: routes, blueprints, templates, and error handling

Technology reference for Flask web applications. This file does not change between projects.

Prerequisites: `stack/common.md`, `stack/python.md`

---

## 1. Application Factory

**Rule**: Use a `create_app()` factory function. Initialize extensions and register blueprints inside it.

```python
# app.py
from flask import Flask

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or 'config.DevConfig')

    # Initialize database
    from db import init_db
    with app.app_context():
        init_db()

    # Register routes
    from routes import bp
    app.register_blueprint(bp)

    # Register error handlers
    from errors import register_error_handlers
    register_error_handlers(app)

    # Startup validation
    from startup import validate_startup
    validate_startup(app)

    return app

if __name__ == '__main__':
    import os
    app = create_app()
    app.run(port=int(os.environ.get('APP_PORT', 5001)))
```

**Why**: Factory pattern enables creating multiple app instances with different configs — essential for testing. Deferred imports prevent circular dependencies.

---

## 2. Blueprints and Route Organization

**Rule**: Keep route handlers thin. Extract business logic into separate modules. Group related routes with Blueprints.

```python
# routes.py
from flask import Blueprint, render_template, request, jsonify
import ops

bp = Blueprint('main', __name__)

@bp.route('/projects')
def projects_list():
    projects = ops.get_all_projects()
    return render_template('projects.html', projects=projects)

@bp.route('/api/project/<int:project_id>/start', methods=['POST'])
def start_project(project_id):
    result = ops.start_service(project_id)  # Logic in ops.py, not here
    return jsonify(result)
```

```python
# ops.py — business logic, no Flask imports needed
from db import get_db

def get_all_projects():
    db = get_db()
    return db.execute('SELECT * FROM projects ORDER BY title').fetchall()

def start_service(project_id):
    ...
    return {'status': 'started', 'pid': pid}
```

Rules:
- Route handlers do: parse request, call business logic, return response
- Route handlers don't: contain SQL, file I/O, subprocess calls, or complex logic
- One Blueprint per feature area for larger apps
- API routes return JSON; page routes return rendered templates

**Why**: Thin routes are testable and readable. Business logic in separate modules can be reused without Flask context.

---

## 3. Error Handling

**Rule**: Register Flask error handlers for 404/500. Return JSON for API routes, HTML for page routes. Never expose stack traces.

```python
# errors.py
from flask import render_template, jsonify, request

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error('Internal error: %s', e, exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled exception: %s', e, exc_info=True)
        return render_template('500.html'), 500
```

**Why**: Dual response format (JSON/HTML) keeps API clients and browsers happy.

---

## 4. Templates (Jinja2)

**Rule**: Use template inheritance with `base.html`. Prefix partials with `_`. Keep logic out of templates.

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    {% include '_nav.html' %}
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    {% block scripts %}{% endblock %}
</body>
</html>
```

```html
<!-- templates/projects.html -->
{% extends 'base.html' %}
{% block title %}Projects{% endblock %}
{% block content %}
  <h1>Projects</h1>
  {% for p in projects %}
    {% include 'types/_project_row.html' %}
  {% endfor %}
{% endblock %}
```

Rules:
- All pages extend `base.html`
- Partials prefixed with `_` (e.g., `_nav.html`, `_project_row.html`)
- Type-specific partials in `templates/types/`
- No Python logic in templates — pass ready-to-render data from routes
- Use `url_for('static', filename=...)` for all static file references
- Auto-escaping is enabled by default — don't disable it

**Why**: Template inheritance eliminates duplication. Partial naming conventions make includes discoverable.

---

## 5. Context Processors

**Rule**: Use context processors to inject global data into all templates.

```python
@app.context_processor
def inject_globals():
    return {
        'app_name': app.config.get('APP_NAME', 'My App'),
        'running_count': ops.get_running_count(),
    }
```

**Why**: Avoids passing the same variables to every `render_template()` call.

---

## 6. HTMX Integration

**Rule**: Use HTMX for dynamic UI updates. Return HTML fragments from API endpoints. Use `HX-Trigger` headers for cross-component updates.

```python
@bp.route('/api/project/<int:project_id>/toggle', methods=['POST'])
def toggle_status(project_id):
    new_status = ops.toggle_status(project_id)
    project = ops.get_project(project_id)
    return render_template('types/_project_row.html', project=project)
```

```html
<button hx-post="/api/project/{{ p.id }}/toggle"
        hx-swap="outerHTML"
        hx-target="closest tr">
    Toggle
</button>
```

### OOB (Out-of-Band) Swaps

```python
html = render_template('types/_project_row.html', project=project)
html += render_template('_nav_badge.html', count=running_count)
response = make_response(html)
response.headers['HX-Trigger'] = 'projectUpdated'
return response
```

```html
<span id="running-badge" hx-swap-oob="true">{{ count }}</span>
```

**Why**: HTMX eliminates JavaScript for common interactions. HTML fragments are simpler than JSON APIs for server-rendered apps.

---

## 7. Testing with Flask Test Client

**Rule**: Test through the Flask test client. Use fixtures for app, client, and database.

```python
# tests/conftest.py
import pytest
from app import create_app
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    from db import get_db, init_db
    with app.app_context():
        init_db()
        yield get_db()
```

```python
# tests/test_routes.py
def test_projects_page(client):
    response = client.get('/projects')
    assert response.status_code == 200
    assert b'Projects' in response.data

def test_api_returns_json(client):
    response = client.get('/api/projects')
    assert response.content_type == 'application/json'

def test_htmx_endpoint(client):
    response = client.post('/api/project/1/toggle',
                          headers={'HX-Request': 'true'})
    assert response.status_code == 200
```

**Why**: Test client exercises the full stack without a running server.

---

## 8. Security

**Rule**: Set secure headers. Validate all input. Debug mode off in production.

```python
@app.after_request
def set_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response
```

Flask security checklist:
- Jinja2 auto-escaping enabled (default — don't disable)
- `SECRET_KEY` set from environment variable in production
- `secure_filename()` from werkzeug for file uploads
- Input validation on all form data (length, type, allowed values)
- Debug mode disabled in production (`FLASK_DEBUG=0`)

---

## 9. Health Check

**Rule**: Expose a `/health` endpoint that verifies database connectivity.

```python
@bp.route('/health')
def health():
    try:
        db = get_db()
        db.execute('SELECT 1')
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500
```

---

## 10. Debug Mode and Reloading

**Rule**: Use Flask's debug mode in development only. Understand the reloader behavior.

```bash
# Development
FLASK_DEBUG=1 flask run --port 5001

# Production
gunicorn app:create_app()
```

Key behaviors in debug mode:
- **Auto-reloader**: Restarts server on Python file changes
- **Double startup**: `WERKZEUG_RUN_MAIN` check needed to avoid running startup code twice
- **Interactive debugger**: Shows in browser on errors (never expose in prod)

```python
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
    run_scanner()
```

---

## Standard bin/ Scripts for Flask

```bash
# bin/start.sh
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Type: daemon
# Port: 5001

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source venv/bin/activate
FLASK_DEBUG=1 flask run --port 5001 2>&1
```

```bash
# bin/stop.sh
#!/bin/bash
# CommandCenter Operation
# Name: Service Stop
# Type: batch

pkill -f "flask run --port 5001" || echo "No Flask process found"
```

```bash
# bin/test.sh
#!/bin/bash
# CommandCenter Operation
# Name: Run Tests
# Type: batch

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source venv/bin/activate
python -m pytest tests/ -v 2>&1
```

---

## Summary Checklist

- [ ] Application factory with `create_app()`
- [ ] Blueprints with thin route handlers
- [ ] Error handlers for 404/500 (JSON + HTML)
- [ ] Template inheritance from `base.html`, partials prefixed with `_`
- [ ] Context processors for global template data
- [ ] HTMX for dynamic UI (HTML fragments, OOB swaps)
- [ ] Test client fixtures in conftest.py
- [ ] Secure headers and input validation
- [ ] `/health` endpoint
- [ ] Debug mode only in dev, `WERKZEUG_RUN_MAIN` guard
- [ ] Standard `bin/` scripts: start.sh, stop.sh, test.sh


---

## SQLite (stack/sqlite.md)

# SQLite Best Practices

**Version:** 20260320 V1  
**Description:** SQLite database patterns: schema, queries, migrations, and connection management

Technology reference for SQLite in Python applications. This file does not change between projects.

Prerequisites: `stack/python.md`

---

## Connection Setup

**Rule**: Always enable WAL mode, foreign keys, and use Row factory.

```python
import sqlite3
import os

def get_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn
```

### PRAGMAs

| PRAGMA | Value | Why |
|--------|-------|-----|
| `journal_mode=WAL` | Write-Ahead Logging | Allows concurrent reads during writes |
| `foreign_keys=ON` | Enforce FK constraints | SQLite disables FK enforcement by default |

---

## Schema Design

**Rule**: Use `TEXT` for dates (ISO 8601), `INTEGER` for booleans, and a JSON `TEXT` column for extensible fields.

```sql
CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    status      TEXT DEFAULT 'active',
    extra       TEXT DEFAULT '{}',        -- JSON for extensible fields
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);
```

### JSON Column Pattern

```python
import json

def get_extra(row):
    return json.loads(row['extra'] or '{}')

def set_extra(db, item_id, key, value):
    row = db.execute('SELECT extra FROM items WHERE id = ?', (item_id,)).fetchone()
    extra = json.loads(row['extra'] or '{}')
    extra[key] = value
    db.execute('UPDATE items SET extra = ? WHERE id = ?', (json.dumps(extra), item_id))
    db.commit()
```

**Why**: JSON columns let you add fields without migrations.

---

## Queries

**Rule**: Always use parameterized queries. Never interpolate user input into SQL.

```python
# CORRECT — parameterized
db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
db.execute('INSERT INTO items (name, status) VALUES (?, ?)', (name, status))

# NEVER — string interpolation
db.execute(f"SELECT * FROM items WHERE id = {item_id}")  # SQL INJECTION
```

### Helper Patterns

```python
def row_to_dict(row):
    """Convert sqlite3.Row to dict, parsing JSON columns."""
    if row is None:
        return None
    d = dict(row)
    if 'extra' in d:
        d['extra'] = json.loads(d['extra'] or '{}')
    return d

def query(db, sql, params=(), one=False):
    rows = db.execute(sql, params).fetchall()
    if one:
        return row_to_dict(rows[0]) if rows else None
    return [row_to_dict(r) for r in rows]

def execute(db, sql, params=()):
    cursor = db.execute(sql, params)
    db.commit()
    return cursor.lastrowid
```

---

## Migrations

**Rule**: Run migrations at startup using `PRAGMA table_info()` to detect missing columns.

```python
def _run_migrations(db):
    """Add columns that don't exist yet. Runs on every startup."""
    columns = {r['name'] for r in db.execute('PRAGMA table_info(items)').fetchall()}

    migrations = [
        ('new_field', 'ALTER TABLE items ADD COLUMN new_field TEXT DEFAULT ""'),
        ('priority',  'ALTER TABLE items ADD COLUMN priority INTEGER DEFAULT 0'),
    ]

    for col_name, sql in migrations:
        if col_name not in columns:
            db.execute(sql)

    db.commit()
```

### New Table Detection

```python
def _table_exists(db, table_name):
    row = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    ).fetchone()
    return row is not None
```

**Why**: Startup migrations avoid manual schema management. `PRAGMA table_info` is idempotent.

---

## Limitations

| Scenario | SQLite OK? | Alternative |
|----------|-----------|-------------|
| Single-server web app | Yes | — |
| Local tool / CLI | Yes | — |
| Multiple concurrent writers | No | PostgreSQL |
| Multi-server deployment | No | PostgreSQL |
| Dataset > 1GB | Maybe | PostgreSQL |
| Full-text search (heavy) | Maybe | PostgreSQL + pg_trgm |

---

## Backup

**Rule**: Use file copy with WAL checkpoint first.

```python
import shutil

def backup_database(db_path, backup_dir='data/backups'):
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')

    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    conn.close()

    shutil.copy2(db_path, backup_path)
    return backup_path
```

**Why**: WAL checkpoint flushes pending writes before copying.


---

## Bootstrap5 (stack/bootstrap5.md)

# Bootstrap 5 Best Practices

**Version:** 20260320 V1  
**Description:** Bootstrap 5 frontend patterns: layout, components, and form conventions

Technology reference for Bootstrap 5 frontend styling. This file does not change between projects.

Prerequisites: `stack/common.md`

---

## 1. Setup

**Rule**: Load Bootstrap from CDN. Use a single project stylesheet for overrides and custom components.

```html
<!-- In base.html <head> -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-..."
      crossorigin="anonymous">
<link rel="stylesheet" href="/static/css/style.css">
```

```html
<!-- Before </body> -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-..."
        crossorigin="anonymous"></script>
```

Rules:
- CDN for Bootstrap CSS and JS bundle (includes Popper)
- Single `static/css/style.css` for all custom styles
- No build step required — no Sass compilation
- Pin a specific Bootstrap version via CDN URL

**Why**: CDN avoids bundling complexity. Single custom stylesheet keeps overrides organized.

---

## 2. Dark Theme

**Rule**: Use `data-bs-theme="dark"` on `<html>` for Bootstrap's native dark mode. Override with CSS custom properties.

```html
<html data-bs-theme="dark">
```

```css
/* static/css/style.css */
:root {
    --cc-bg: #1a1a2e;
    --cc-surface: #16213e;
    --cc-text: #e0e0e0;
    --cc-border: #2a2a4a;
    --cc-accent: #4fc3f7;
}

body {
    background-color: var(--cc-bg);
    color: var(--cc-text);
}
```

**Why**: Bootstrap 5.3+ has native dark mode. Custom properties let you extend it with project-specific colors.

---

## 3. Layout

**Rule**: Use Bootstrap's container and grid system. Stick to `container` or `container-fluid`.

```html
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">App Name</a>
        </div>
    </nav>

    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
</body>
```

### Grid

```html
<div class="row">
    <div class="col-md-8">Main content</div>
    <div class="col-md-4">Sidebar</div>
</div>
```

Rules:
- Use responsive breakpoints (`col-md-*`, `col-lg-*`)
- `mt-4`, `mb-3`, `p-3` for spacing (Bootstrap utility classes)
- Don't fight the grid — use it or skip it, don't half-use it

---

## 4. Components

**Rule**: Use Bootstrap's built-in components. Style with utility classes first, custom CSS second.

### Cards

```html
<div class="card bg-dark border-secondary">
    <div class="card-header text-uppercase text-muted small">Section Title</div>
    <div class="card-body">
        <p class="card-text">Content here</p>
    </div>
</div>
```

### Tables

```html
<table class="table table-dark table-hover">
    <thead>
        <tr>
            <th>Name</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        {% for item in items %}
        <tr>
            <td>{{ item.name }}</td>
            <td><span class="badge bg-success">Active</span></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Badges

```html
<span class="badge bg-primary">Primary</span>
<span class="badge bg-success">Active</span>
<span class="badge bg-danger">Error</span>
<span class="badge bg-warning text-dark">Warning</span>
```

### Buttons

```html
<button class="btn btn-sm btn-outline-primary">Action</button>
<button class="btn btn-sm btn-outline-danger">Delete</button>
```

---

## 5. Modals

**Rule**: Use Bootstrap modals for dialogs. For HTMX-loaded content, use custom overlays.

```html
<!-- Bootstrap modal -->
<div class="modal fade" id="confirmModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content bg-dark">
            <div class="modal-header border-secondary">
                <h5 class="modal-title">Confirm</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">Are you sure?</div>
            <div class="modal-footer border-secondary">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button class="btn btn-danger">Confirm</button>
            </div>
        </div>
    </div>
</div>
```

```html
<!-- Custom overlay for dynamic content (HTMX-friendly) -->
<div id="log-overlay" class="position-fixed top-0 start-0 w-100 h-100 d-none"
     style="background: rgba(0,0,0,0.8); z-index: 1050;">
    <div class="container mt-5">
        <pre id="log-content" class="p-3 text-success" style="font-family: monospace;"></pre>
        <button onclick="closeOverlay()" class="btn btn-outline-light mt-2">Close</button>
    </div>
</div>
```

**Why**: Bootstrap modals work for static dialogs. Custom overlays are simpler for HTMX-fetched content.

---

## 6. Custom Component Patterns

**Rule**: Define reusable component classes in your stylesheet using CSS custom properties.

```css
/* Operation buttons — consistent sizing */
.op-btn {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.65rem;
    border-radius: 4px;
    white-space: nowrap;
}

.op-btn--local { background: var(--btn-local, #4fc3f7); color: #000; }
.op-btn--remote { background: var(--btn-remote, #81c784); color: #000; }
.op-btn--danger { background: var(--btn-danger, #ef5350); color: #fff; }

/* Card headers */
.cc-card-header {
    font-size: 0.85rem;
    text-transform: uppercase;
    color: var(--cc-text-muted, #888);
    letter-spacing: 0.05em;
}
```

Rules:
- Use BEM-like naming: `.component--modifier`
- Define colors as CSS custom properties in `:root`
- Keep custom CSS minimal — use Bootstrap utilities first
- Document component classes in a BRANDING.md or style guide

**Why**: Custom properties make theming consistent. BEM naming prevents class collision.

---

## 7. HTMX + Bootstrap Integration

**Rule**: HTMX and Bootstrap coexist without conflict. Use Bootstrap for layout/style, HTMX for behavior.

```html
<!-- HTMX button with Bootstrap styling -->
<button class="btn btn-sm btn-outline-primary op-btn op-btn--local"
        hx-post="/api/project/1/start"
        hx-swap="outerHTML"
        hx-target="closest tr">
    Start
</button>

<!-- HTMX form inside Bootstrap card -->
<div class="card bg-dark border-secondary">
    <div class="card-body">
        <form hx-post="/api/project/1/update" hx-swap="outerHTML">
            <input type="text" class="form-control form-control-sm bg-dark text-light"
                   name="title" value="{{ project.title }}">
        </form>
    </div>
</div>
```

**Why**: Bootstrap handles visual structure. HTMX handles dynamic behavior. No JavaScript framework needed.

---

## Summary Checklist

- [ ] Bootstrap 5.3+ loaded from CDN (CSS + JS bundle)
- [ ] Single `static/css/style.css` for custom styles
- [ ] Dark theme via `data-bs-theme="dark"` + CSS custom properties
- [ ] Container-based layout with responsive grid
- [ ] Standard Bootstrap components (cards, tables, badges, buttons)
- [ ] Custom component classes with BEM naming and CSS variables
- [ ] HTMX attributes on Bootstrap-styled elements


---

## Project Configuration (METADATA.md)

```
# GAME

Dashboard for managing AI-assisted projects and prototypes.

name: GAME
display_name: GAME
title: GAME — Generic AI Management Environment
git_repo: GAME
short_description: Dashboard for managing, monitoring, and operating AI-assisted projects
port: 5001
status: ACTIVE
type: oneshot
version: 2026-03-20.1
updated: 20260320
stack: Python/Flask/SQLite/Bootstrap5
health: /health
show_on_homepage: true
tags: dashboard, tool, platform
desired_state: on-demand
namespace: development
description: Project owners use GAME to manage, monitor, and operate their prototypes. Conformed projects expose operations, health, documentation, and self-discovery out of the box.
```


# PROJECT SPECIFICATION

---

## Spec: ARCHITECTURE.md

# Architecture

**Version:** 20260320 V1  
**Description:** Module layout, routes, and directory structure

**Flask app with blueprints.** App factory pattern. Scanner, process engine, and publisher are backend modules that feed data to the screen routes.

---

## App Factory

`create_app()` in `app.py`. Returns a configured Flask instance.

1. Load config from environment and `.env`
2. Initialize SQLite database (create tables if missing, run migrations)
3. Register blueprints
4. Start async project scan on first request

## Blueprints

Single blueprint `cc` registered on `/`. All routes live in `routes.py`.

## Backend Modules

### Scanner (`scanner.py`)

Scans `$PROJECTS_DIR` for project directories. For each:
1. Read METADATA.md → parse key:value fields
2. Read AGENTS.md / CLAUDE.md → extract endpoints, bookmarks
3. Read bin/ scripts → parse CommandCenter headers (any language: sh, py, js, pl)
4. Upsert into `projects` and `operations` tables

Runs asynchronously on startup (not blocking first page load). Triggered manually by rescan button.

**Script header detection:** The scanner reads the first 20 lines of every executable file in `bin/`. Any script containing `# CommandCenter Operation` is registered as an operation. Supported languages: Bash, Python, Perl, JavaScript, Ruby — any language using `#` comments. This enables self-documentation as a core platform feature.

### Process Engine (`ops.py` + `spawn.py`)

Launches bin/ scripts as background subprocesses.

1. Receive launch request (project_id, operation_id)
2. Create `runs` record with status STARTING
3. Fork subprocess: execute script from project root
4. Capture stdout/stderr to log file: `logs/{project}_{script}_{yyyymmdd_hhmmss}.log`
5. Parse `[$PROJECT_NAME]` lines from output for status transitions
6. Update `runs` record on exit (status, exit_code, finished_at)

Provides: `launch(project_id, operation_id)`, `stop(run_id)`, `get_running()`, `get_log(run_id)`.

### Publisher (`publisher.py`)

Builds static portfolio site from METADATA.md fields.

1. Query projects where `show_on_homepage = true`
2. Generate card HTML from title, short_description, tags, image
3. If project has `doc/index.html`, add documentation link
4. Write static site to output directory
5. Optionally push to GitHub Pages

## Routes (HTMX)

All screen interactions use HTMX for partial page updates. Server returns HTML fragments, not JSON.

| Method | Path | Returns | Trigger |
|--------|------|---------|---------|
| GET | `/` | Full dashboard page | Page load |
| POST | `/api/scan` | Status message | Rescan button |
| POST | `/api/run/{op_id}` | Updated button state | Operation click |
| POST | `/api/stop/{run_id}` | Updated button state | Stop click |
| POST | `/api/push/{project_id}` | Git status fragment | Push button |
| GET | `/project/{id}` | Project detail page | Name/cog click |
| GET | `/processes` | Process list page | Nav link |
| GET | `/processes/{run_id}/log` | Log content fragment | View Log click |
| GET | `/publisher` | Publisher page | Nav link |
| POST | `/publisher/build` | Build status | Rebuild button |
| POST | `/publisher/publish` | Publish status | Publish button |
| GET | `/project-config` | Configuration list | Nav link |
| GET | `/monitoring` | Monitoring page | Nav link |
| GET | `/workflow` | Workflow board | Nav link |
| GET | `/health` | `{"status":"ok"}` | Health check |

## Directory Layout

```
GAME/
  app.py                 App factory (create_app)
  routes.py              All routes (single blueprint: cc)
  scanner.py             Project discovery
  ops.py                 Operation launch/stop/status
  spawn.py               Subprocess management
  publisher.py           Portfolio builder
  models.py              PROJECT_TYPES registry
  db.py                  Database access helpers
  claude_convention.py   CLAUDE.md / AGENTS.md parsing
  templates/             Flask/Jinja2 templates
    base.html            Layout with nav bar
    partials/            HTMX response fragments
  static/
    style.css            Custom styles (Bootstrap 5 dark theme)
  bin/
    common.sh            Shared script functions
    common.py            Shared Python functions
    start.sh             Start Flask dev server
    stop.sh              Stop server
    build_documentation.sh  Generate docs/
  data/
    game.db        SQLite database
  docs/                  Generated documentation
  logs/                  Operation log files
```

## Open Questions

- Should routes.py be split into per-screen blueprint modules as the app grows?


---

## Spec: DATABASE.md

# Database

**Version:** 20260320 V1  
**Description:** Database schema: tables, columns, and types

**SQLite with WAL mode.** Single file at `data/game.db`.

---

## Source-of-Truth Model

| Layer | Role |
|-------|------|
| **Project files** (`METADATA.md`, `bin/`, filesystem) | Authoritative source of truth — committed to git, editable by developer |
| **SQLite database** | Runtime cache — the sole source of data for all UI page renders |
| **Startup scan** | Runs automatically in a background thread every time Flask starts; populates the DB from disk |
| **Refresh button** | Re-runs the same scan without restarting; useful when files changed mid-session |

**Page rendering reads the database only.** No template, route, or partial reads a file from disk during a normal page load.

**Writes go to both.** When the UI changes a value (status badge click, port inline edit, etc.), Prototyper writes to the DB immediately and then patches the same value into the project's `METADATA.md`. This keeps the file current so git history tracks changes.

```
Startup / Refresh (slow path — filesystem I/O)
───────────────────────────────────────────────
scan_projects()
  └─ for each project directory:
       detect_project()          → reads METADATA.md, bin/ headers, filesystem flags
       parse_metadata_md()       → reads METADATA.md key-values and ## Links table
       scan_bin_operations()     → reads first 20 lines of each bin/*.sh / bin/*.py
       upsert_project()          → INSERT or UPDATE into SQLite

Normal page load (fast path — DB only)
───────────────────────────────────────
Route handler
  └─ db.get_all_projects()           → SELECT * FROM projects
  └─ db.get_all_operations_keyed()   → SELECT * FROM operations (one query, all projects)
  └─ render_template()               → Jinja renders from dicts; no file I/O

UI write (status click, port edit, etc.)
─────────────────────────────────────────
  └─ UPDATE projects SET ...     (SQLite)
  └─ patch METADATA.md           (file — keeps disk in sync)
```

---

## Field Source Mapping

Every field stored in the `projects` table, its source, and when it is read.

| DB Column | Source File / Method | Read On | Notes |
|-----------|---------------------|---------|-------|
| `name` | Directory name | Scan | Machine slug; must match directory name |
| `display_name` | `METADATA.md` → `display_name:` | Scan | Human-readable name for UI |
| `title` | CamelCase split of directory name | Scan | Legacy; prefer `display_name` |
| `path` | Filesystem (`os.path.abspath`) | Scan | Absolute path to project directory |
| `status` | `METADATA.md` → `status:` | Scan | IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED; also writable from UI |
| `port` | `METADATA.md` → `port:` or auto-detected from `app.py` | Scan | Integer; also writable inline from UI |
| `stack` | `METADATA.md` → `stack:` | Scan | Slash-separated tech summary |
| `namespace` | `METADATA.md` → `namespace:` | Scan | Default: `development`; hidden in UI when default |
| `tags` | `METADATA.md` → `tags:` | Scan | Comma-separated string |
| `health_endpoint` | `METADATA.md` → `health:` | Scan | Default: `/health` |
| `desired_state` | `METADATA.md` → `desired_state:` | Scan | `running` or `on-demand` |
| `version` | `METADATA.md` → `version:` | Scan | Format: `YYYY-MM-DD.N` |
| `project_type` | `METADATA.md` → `project_type:` or heuristic | Scan | `software` / `book` |
| `has_git` | `.git/` directory present | Scan | Boolean flag |
| `has_venv` | `venv/` or `.venv/` directory present | Scan | Boolean flag |
| `has_node` | `node_modules/` directory present | Scan | Boolean flag |
| `has_claude` | `CLAUDE.md` file present | Scan | Boolean flag; enables CLAUDE.md modal |
| `has_docs` | Any subdir starting with `doc` containing `index.html` or `index.htm` (glob: `*/doc*/index.htm*`) | Scan | Boolean flag; enables 📖 Help button |
| `card_title` | `METADATA.md` → `title:` (card section) | Scan | Portfolio card; overrides `display_name` if set |
| `card_desc` | `METADATA.md` → `short_description:` or `description:` | Scan | Portfolio card description |
| `card_tags` | `METADATA.md` → `tags:` | Scan | Portfolio card tags |
| `card_type` | `METADATA.md` → `card_type:` | Scan | Portfolio category label |
| `card_url` | `METADATA.md` → `card_url:` | Scan | Portfolio card link |
| `card_image` | `METADATA.md` → `image:` | Scan | Portfolio card image filename |
| `card_show` | `METADATA.md` → `show_on_homepage:` | Scan | Boolean; include in generated portfolio |
| `extra` (JSON) | Various | Scan | Stores: `links`, `bookmarks`, `doc_path`, `tech_stack`, `has_start_sh`, etc. |
| `last_scanned` | System clock | Scan | Timestamp of last successful scan |
| `created_at` | System clock | Insert only | Set once on first discovery |
| `updated_at` | System clock | Scan + UI writes | Updated on every upsert |

### `extra` JSON sub-fields

| Key | Source | Notes |
|-----|--------|-------|
| `links` | `METADATA.md` → `## Links` table | List of `{label, url}` shown in Links column |
| `bookmarks` | `AGENTS.md` / `CLAUDE.md` → `## Bookmarks` | Quick-access links for AI context |
| `doc_path` | Filesystem detection | Relative path to doc index (e.g., `doc/index.html`); used to build Flask proxy URL `/project/{id}/doc/index.html` |
| `tech_stack` | Auto-detected from `app.py`, `package.json`, etc. | Fallback for `stack` column |
| `has_start_sh` | `bin/start.sh` present | Legacy flag; bin operations supersede this |

### Operations table field sources

| DB Column | Source | Read On |
|-----------|--------|---------|
| `project_id` | FK to projects | Scan |
| `name` | `# Name:` header in bin script | Scan |
| `category` | `# Category:` header; default `local` | Scan |
| `cmd` | Derived from filename (`bin/start.sh`) | Scan |
| `cwd` | Project path | Scan |
| `default_port` | `# Port:` header | Scan |
| `health_path` | `# Health:` header | Scan |
| `schedule` | `# Schedule:` header | Scan |
| `timeout` | `# Timeout:` header | Scan |

Operations are deleted and re-seeded on every scan (only `bin/` operations — custom operations survive).

---

## Startup / Refresh Sequence

Both server startup and the Refresh button execute the same `scan_projects()` function in `scanner.py`. `scanner.py` is a library module — it has no entry point; it is called by `app.py` (startup) and by the `/api/sync` route (Refresh button).

On startup, the scan runs in a **background thread** so the server is immediately ready to serve requests; the DB will be fully populated within a few seconds. After a restart, the Refresh button is redundant — the startup scan has already run. Use Refresh only when project files change *while the server is running* and you want to pick up those changes without restarting.

```
1. cleanup_orphaned()        Remove DB rows for projects no longer on disk
2. for each directory in PROJECTS_DIR:
   a. detect_project()
      - Read filesystem flags (has_git, has_venv, has_node, has_claude, has_docs)
      - Detect doc_path by checking doc/ and docs/ for index.html / index.htm
      - Auto-detect tech stack from known files (app.py, package.json, manage.py, etc.)
      - Auto-detect port from app.py or METADATA.md
   b. parse_metadata_md()
      - Parse key:value lines → display_name, status, port, stack, namespace,
        health_endpoint, desired_state, version, project_type, tags
      - Parse ## Links table → extra.links
      - Parse card metadata → card_* columns
   c. scan_bin_operations()
      - Read first 20 lines of each bin/*.sh and bin/*.py
      - Look for `# CommandCenter Operation` marker
      - Extract Name, Category, Port, Schedule, Timeout, Health headers
   d. parse claude/agents if has_claude → extra.bookmarks
   e. upsert_project()
      - UPDATE if exists (preserves user-edited fields via COALESCE)
      - INSERT if new
      - DELETE + re-seed operations table for this project
3. Log scan duration per project and total
```

**User-edited fields are preserved on re-scan** via SQL `COALESCE(?, column)` — if the scan value is NULL, the existing DB value is kept. Fields where METADATA.md is authoritative (status, port, stack) overwrite the DB.

---

## Schema

### projects

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| name | TEXT UNIQUE | — | Machine slug; matches directory name |
| display_name | TEXT | NULL | Human-readable name from METADATA.md |
| title | TEXT | — | CamelCase-split fallback (legacy) |
| path | TEXT | NULL | Absolute path to project directory |
| status | TEXT | 'template' | Lifecycle status |
| port | INTEGER | NULL | Service port |
| stack | TEXT | NULL | Technology summary |
| health_endpoint | TEXT | '/health' | Health check path |
| desired_state | TEXT | 'on-demand' | running / on-demand |
| namespace | TEXT | 'development' | Deployment namespace |
| tags | TEXT | NULL | Comma-separated tags |
| project_type | TEXT | 'software' | software / book / etc. |
| description | TEXT | NULL | Short description |
| has_git | INTEGER | 0 | .git/ present |
| has_venv | INTEGER | 0 | venv/ present |
| has_node | INTEGER | 0 | node_modules/ present |
| has_claude | INTEGER | 0 | CLAUDE.md present |
| has_docs | INTEGER | 0 | doc[s]/index.htm[l] present |
| card_title | TEXT | NULL | Portfolio card title |
| card_desc | TEXT | NULL | Portfolio card description |
| card_tags | TEXT | NULL | Portfolio card tags |
| card_type | TEXT | NULL | Portfolio card category |
| card_url | TEXT | NULL | Portfolio card URL |
| card_image | TEXT | NULL | Portfolio card image filename |
| card_show | INTEGER | 0 | Include in portfolio page |
| version | TEXT | NULL | YYYY-MM-DD.N from METADATA.md |
| extra | TEXT | '{}' | JSON blob (links, bookmarks, doc_path, etc.) |
| is_active | INTEGER | 1 | 0 if removed from disk |
| last_scanned | TEXT | NULL | Timestamp of last scan |
| created_at | TEXT | datetime('now') | First discovery |
| updated_at | TEXT | datetime('now') | Last scan or UI write |

### operations

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| name | TEXT | Display name from `# Name:` header |
| category | TEXT | `local` / `service` / `maintenance` / custom |
| cmd | TEXT | Command string (e.g., `bin/start.sh`) |
| cwd | TEXT | Working directory (project path) |
| needs_venv | INTEGER | Activate venv before running |
| is_url | INTEGER | Open URL rather than run command |
| default_port | INTEGER | From `# Port:` header |
| health_path | TEXT | From `# Health:` header |
| schedule | TEXT | From `# Schedule:` header (cron expression) |
| last_scheduled_run | TEXT | Last time the scheduler fired this operation |
| next_scheduled_run | TEXT | Calculated next fire time |
| schedule_enabled | INTEGER | 1 = active; allows pausing without removing the header |
| timeout | INTEGER | From `# Timeout:` header |
| sort_order | INTEGER | Display order |

### op_runs

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| op_id | INTEGER FK | References operations.id |
| project_id | INTEGER FK | References projects.id |
| status | TEXT | running / done / error / stopped |
| pid | INTEGER | OS process ID |
| started_at | TEXT | datetime |
| finished_at | TEXT | datetime or NULL while running |
| exit_code | INTEGER | NULL while running |
| log_path | TEXT | Path to log file |
| cmd | TEXT | Actual command executed |
| name | TEXT | Operation name at time of run |

### tickets

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| title | TEXT | Ticket title |
| description | TEXT | Detail text |
| state | TEXT | idea / proposed / ready / in_development / testing / done |
| tags | TEXT | Comma-separated |
| sort_order | INTEGER | Column position |
| created_at | TEXT | datetime |
| updated_at | TEXT | datetime |

### heartbeats

One row per project per heartbeat type. Overwritten on each poll (no history; rolling window only).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| heartbeat_type | TEXT | service_health / process_state / git_state / compliance |
| current_state | TEXT | Current state value (e.g. UP, DOWN, RUNNING, CLEAN, COMPLIANT) |
| last_checked | TEXT | Timestamp of last poll (yyyymmdd_hhmmss) |
| response_ms | INTEGER | Response time in ms (service_health only; NULL otherwise) |
| uptime_pct | REAL | Rolling 24h uptime percentage (service_health only; NULL otherwise) |

### events

Append-only log. Rows are never updated or deleted.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id; NULL for platform-level events |
| event_type | TEXT | Valid values: `operation_started`, `operation_completed`, `operation_failed`, `state_transition`, `git_push`, `git_commit`, `schedule_fired`, `schedule_missed`, `build_completed`, `deploy_completed`, `scan_completed`, `ticket_transition`, `metadata_changed`, `alert_fired`, `spec_updated` |
| timestamp | TEXT | When it happened (yyyymmdd_hhmmss) |
| summary | TEXT | Human-readable one-liner |
| detail | TEXT | JSON event-specific payload |
| source | TEXT | Subsystem that generated the event |

### transaction_log

Spec decision log. One row per decision, change, question, or rationale entry.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Sequential entry number |
| project_id | INTEGER FK | References projects.id |
| timestamp | TEXT | When the decision was made (yyyymmdd_hhmmss) |
| category | TEXT | decision / change / question / rationale |
| title | TEXT | One-line summary |
| body | TEXT | Full description, context, alternatives considered |
| files_affected | TEXT | JSON array of spec file paths modified |
| ticket_id | INTEGER FK | Optional link to tickets.id |

### ai_decisions

Per-ticket AI decision log. Written when a ticket enters IN DEVELOPMENT.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| ticket_id | INTEGER FK | References tickets.id |
| timestamp | TEXT | When the work happened (yyyymmdd_hhmmss) |
| decision | TEXT | What was decided and why |
| alternatives | TEXT | What was considered but rejected |
| files_changed | TEXT | JSON array of files modified |

---

## Conventions

- WAL mode: set once in `init_db()` (persistent on the file); not repeated per connection
- Foreign keys: `PRAGMA foreign_keys=ON` per connection (required for FK enforcement)
- Schema changes: `_add_column_if_missing()` in `db.py` — additive only, no migration files
- JSON blobs: stored as TEXT, parsed by application; changes do not require schema migration
- DB created automatically on first startup if missing

---

## Open Questions / Design Decisions

- **`title` column**: Duplicated by `display_name`. Candidate for removal once all templates consistently use `display_name`.
- **WAL PRAGMA per connection**: Harmless (WAL is persistent) but wasteful — should move to `init_db()` only.
- **Tag colors**: Currently in `data/tag_colors.json` (file, not DB). Should be promoted to a `tag_colors` table to stay consistent with the DB-as-UI-source model.
- **`has_docs`, `has_tests`, `has_specs` flags**: `has_docs` is implemented. `has_tests` and `has_specs` are roadmap items for contract-earns-capability.
- **`git_last_commit_date`**: Not yet implemented. Would replace `version` date as the `LastUpdate` source — requires running `git log` during scan and storing the result.


---

## Spec: FUNCTIONALITY.md

# Functionality: End-to-End Flows

**Version:** 20260320 V1  
**Description:** Core functionality specification

**How things actually work, step by step.** This document bridges ARCHITECTURE (how code is organized) with DATABASE (what is stored) by describing the major workflows from trigger to completion.

Each flow shows: what triggers it, what happens in sequence, what gets read, what gets written, and what the user sees.

---

## 1. Project Scan

**Trigger:** Platform startup (first request), or user clicks Rescan button.

```
User clicks Rescan (or first page load)
  |
  v
POST /api/scan
  |
  v
Scanner reads $PROJECTS_DIR
  |
  +---> For each directory:
  |       |
  |       +---> Read METADATA.md --> parse key:value fields
  |       |       name, display_name, status, stack, port, version, tags, ...
  |       |
  |       +---> Read AGENTS.md --> extract sections
  |       |       ## Bookmarks --> quick links
  |       |       ## Service Endpoints --> service URLs
  |       |       ## Dev Commands --> context (not stored, displayed on demand)
  |       |
  |       +---> Read bin/ scripts --> parse first 20 lines for headers
  |       |       # CommandCenter Operation --> register operation
  |       |       # Category: --> operation category
  |       |       # Schedule: --> cron expression
  |       |       # Port: / # Health: / # Timeout: --> operation metadata
  |       |
  |       +---> Check filesystem flags
  |       |       .git/ --> has_git, then: git status, git log, git rev-list
  |       |       venv/ --> has_venv
  |       |       package.json --> has_node
  |       |       CLAUDE.md --> has_claude
  |       |       tests/ or bin/test.sh --> has_tests
  |       |       doc/index.html --> has_docs
  |       |       Specifications/{name}/ --> has_specs
  |       |
  |       +---> Upsert into `projects` table
  |       +---> Replace rows in `operations` table for this project
  |
  +---> Mark projects not found on disk as is_active = false
  |
  v
Dashboard refreshes with updated project list
```

**Reads:** Filesystem ($PROJECTS_DIR), METADATA.md, AGENTS.md, bin/ scripts, .git/
**Writes:** `projects` table, `operations` table
**Event emitted:** `scan_completed`

**Key behaviors:**
- Non-blocking on startup — first page load returns immediately, scan runs async
- Missing files produce compliance gaps, not errors — a project with only METADATA.md still appears
- Projects removed from disk are marked `is_active = false`, not deleted
- Git operations (status, log) run per-project — can be slow with many repos

---

## 2. Run Operation

**Trigger:** User clicks an operation button on the dashboard or project detail.

```
User clicks operation button (e.g., "Start Server")
  |
  v
POST /api/run/{op_id}
  |
  v
Load operation record from DB
  |  --> script_path, cwd, needs_venv, category
  |
  v
Create op_runs record
  |  status = STARTING
  |  log_path = logs/{project}_{script}_{yyyymmdd_hhmmss}.log
  |
  v
Fork subprocess
  |  cd to project directory
  |  Activate venv if needs_venv
  |  Execute: bash bin/{script}.sh (or python bin/{script}.py)
  |  Redirect stdout+stderr to log_path
  |
  v
Update op_runs: status = RUNNING, pid = process.pid
  |
  v
Dashboard button changes to running state (green pulse)
Nav bar shows running badge for this project
  |
  v
Background: monitor subprocess
  |
  +---> Parse log output for [$PROJECT_NAME] status lines
  |       [$PROJECT_NAME] Starting: ... --> STARTING
  |       [$PROJECT_NAME] Running: ...  --> RUNNING
  |       [$PROJECT_NAME] Error: ...    --> flag
  |
  +---> On process exit:
          |
          +---> exit_code = 0 --> status = DONE
          +---> exit_code != 0 --> status = ERROR
          |
          v
        Update op_runs: finished_at, exit_code, status
        Remove running badge from nav
```

**Reads:** `operations` table, project path
**Writes:** `op_runs` table, log file
**Events emitted:** `operation_started`, then `operation_completed` or `operation_failed`

**Key behaviors:**
- Process runs in a process group (enables clean SIGTERM of child processes)
- Log file is append-only, named for sorting by project then time
- common.sh/common.py in the script handles venv, PORT, env loading, SIGTERM trap
- The platform does NOT parse or understand what the script does — it just runs it and watches exit codes

---

## 3. Stop Operation

**Trigger:** User clicks Stop on a running operation.

```
User clicks Stop button
  |
  v
POST /api/stop/{run_id}
  |
  v
Load op_runs record --> get pid
  |
  v
Send SIGTERM to process group (-pid)
  |  This triggers the trap in common.sh/common.py
  |  Script performs cleanup, then exits
  |
  v
Process exits (caught by monitor from Flow 2)
  |
  v
Update op_runs: status = STOPPED, finished_at = now
  |
  v
Dashboard button reverts to idle state
Running badge removed from nav
```

**Reads:** `op_runs` table
**Writes:** `op_runs` table (status update)
**Event emitted:** `operation_completed` (with STOPPED status)

---

## 4. Git Push

**Trigger:** User clicks Push button (visible only when `git_unpushed > 0`).

```
User clicks Push on project row
  |
  v
POST /api/push/{project_id}
  |
  v
Load project record --> get path
  |
  v
Execute: git -C {path} push
  |
  +---> Success:
  |       Update project: git_unpushed = 0
  |       Flash success message
  |       Push button disappears
  |
  +---> Failure:
          Flash error with git output
          Button remains visible
```

**Reads:** `projects` table, git remote config
**Writes:** Remote repository, `projects` table
**Event emitted:** `git_push` (success or failure)

---

## 5. Portfolio Publish

**Trigger:** User clicks Rebuild or Publish on the Publisher screen.

```
BUILD:
  User clicks Rebuild
    |
    v
  POST /publisher/build
    |
    v
  Query projects WHERE show_on_homepage = true
    |
    v
  For each published project:
    |
    +---> Resolve card fields (with defaults):
    |       card_title    --> fallback to display_name
    |       card_desc     --> fallback to short_description
    |       card_image    --> fallback to logo
    |       card_tags     --> fallback to tags
    |       card_type     --> fallback to project_type
    |       card_url      --> fallback to deploy_url or git_repo
    |
    +---> Check for doc/index.html --> add Documentation link if exists
    |
    +---> Generate card HTML fragment
    |
    v
  Load config/site_config.md
    |  YAML frontmatter --> site title, branding
    |  Markdown body --> home page content
    |
    v
  Assemble static site: card grid + home page + resume page
    |
    v
  Write output files
  Flash "Build complete" with timestamp

PUBLISH:
  User clicks Publish
    |
    v
  POST /publisher/publish
    |
    v
  Execute PushAndPublish.sh
    |  git add, commit, push to GitHub Pages branch
    |
    v
  Flash publish status
```

**Reads:** `projects` table (card fields), `config/site_config.md`, `doc/` directories, `static/images/`
**Writes:** Static site output files, GitHub Pages branch
**Events emitted:** `build_completed`, `deploy_completed`

---

## 6. Heartbeat Poll [ROADMAP]

**Trigger:** Timer-based (configurable interval, e.g., every 60 seconds). Also on-demand from Monitoring screen.

```
Timer fires (or user clicks Refresh on Monitoring)
  |
  v
Query projects WHERE port IS NOT NULL AND health_endpoint IS NOT NULL
  |
  v
For each monitored project:
  |
  +---> HTTP GET http://localhost:{port}{health_endpoint}
  |       |
  |       +---> 200 OK (within timeout):
  |       |       state = UP
  |       |       response_ms = elapsed
  |       |
  |       +---> Connection refused / timeout / error:
  |               state = DOWN
  |               response_ms = null
  |
  +---> Compare new state vs previous state
  |       |
  |       +---> Same state: update last_checked, response_ms
  |       |
  |       +---> State changed:
  |               Record state_transition event
  |               Update heartbeat record
  |               If DOWN: fire alert (unless SNOOZED)
  |               If UP (after DOWN): fire recovery alert
  |
  +---> Update rolling uptime_pct (24h window)
  |
  v
Monitoring screen updates health table
Dashboard running indicators reflect combined state
```

**Reads:** `projects` table, HTTP endpoints
**Writes:** `heartbeats` table, `events` table
**Events emitted:** `state_transition` (on change), `alert_fired` (on DOWN)

**States:** `UNKNOWN --> UP --> DOWN --> UP` (cycle). `SNOOZED` suppresses alerts but continues polling.

---

## 7. Schedule Fire [ROADMAP]

**Trigger:** Cron expression match (checked every minute by scheduler loop).

```
Scheduler tick (every 60 seconds)
  |
  v
Query operations WHERE schedule IS NOT NULL AND schedule_enabled = true
  |
  v
For each scheduled operation:
  |
  +---> Evaluate cron expression against current time
  |       |
  |       +---> No match: skip
  |       |
  |       +---> Match:
  |               |
  |               +---> Check last_scheduled_run
  |               |       Already ran this minute? Skip (dedup)
  |               |
  |               +---> Execute Run Operation flow (Flow 2)
  |               |
  |               +---> Update last_scheduled_run = now
  |               +---> Calculate next_scheduled_run
  |
  v
(silent — no UI update unless user is watching Processes screen)

STARTUP CATCH-UP:
  On platform start:
    |
    v
  For each scheduled operation:
    |
    +---> Compare last_scheduled_run against cron expression
    |       |
    |       +---> Missed run(s) detected:
    |               Fire ONE immediate run (most recent missed, no backfill cascade)
    |               Record schedule_missed event
    |
    v
  Resume normal tick loop
```

**Reads:** `operations` table (schedule, last_scheduled_run)
**Writes:** `op_runs` table (via Flow 2), `operations` table (last/next scheduled run)
**Events emitted:** `schedule_fired`, `schedule_missed` (on catch-up)

---

## 8. Ticket Lifecycle [ROADMAP]

**Trigger:** User creates or moves a ticket on the Workflow screen.

```
CREATE:
  User clicks New Ticket (on Workflow or project detail)
    |
    v
  Enter title, description, tags, priority
    |
    v
  Insert into tickets: state = IDEA
    |
    v
  Card appears in IDEA column on Kanban board

TRANSITION:
  User drags ticket to new column (or clicks state button)
    |
    v
  Validate transition is allowed:
    IDEA --> PROPOSED (needs: summary and plan)
    PROPOSED --> READY (needs: acceptance criteria)
    READY --> IN DEVELOPMENT
    IN DEVELOPMENT --> TESTING (needs: work completed)
    TESTING --> DONE (needs: human validation)
    TESTING --> READY (rework)
    IN DEVELOPMENT --> PROPOSED (redesign)
    |
    v
  Update ticket state
  Record state change in ticket history
    |
    v
  If entering IN DEVELOPMENT:
    |  Begin collecting AI transaction log entries
    |  (decisions, files changed, rationale)
    |
  If entering DONE:
    |  Freeze transaction log
    |  Ticket archived after configurable period
    |
    v
  Kanban board updates, card moves to new column
```

**Reads:** `tickets` table, `workflow.json` (state definitions)
**Writes:** `tickets` table, ticket history, transaction log
**Events emitted:** `ticket_transition`

---

## 9. Configuration Edit

**Trigger:** User clicks cog icon on Configuration screen, or edits inline fields.

```
User opens field editor for a project
  |
  v
GET /config or project detail editor
  |  Load current values from DB
  |
  v
User edits field(s) and tabs out / saves
  |
  v
POST update
  |
  v
Update `projects` table in database
  |
  v
Write changes back to METADATA.md on disk
  |  Read current file
  |  Find matching key: line
  |  Replace value (or append if new key)
  |  Write file
  |
  v
Flash confirmation
```

**Reads:** `projects` table, METADATA.md file
**Writes:** `projects` table, METADATA.md file (bidirectional sync)
**Events emitted:** `metadata_changed`

**Key behavior:** Database and METADATA.md are kept in sync. DB is the working copy (fast reads for dashboard). METADATA.md is the source of truth (survives database rebuild via rescan).

---

## 10. Specification Management [ROADMAP]

**Trigger:** User edits spec content via the platform, or agent commits spec changes during ticket work.

```
VIEWING:
  User clicks Specs link on project with has_specs = true
    |
    v
  Load file list from Specifications/{project_name}/
    |
    v
  Display spec index with file names, last modified, sizes

EDITING (via platform):
  User opens a spec file for editing
    |
    v
  Load file content, render in editor
    |
    v
  User saves changes
    |
    v
  Write file to Specifications/{project_name}/
    |
    v
  Git commit in Specifications repo
    |  Message: "Update {filename} for {project_name}"
    |
    v
  Record transaction log entry:
    |  category = change
    |  files_affected = [{filename}]
    |  linked to ticket (if in context)

AI AGENT FLOW (during ticket IN DEVELOPMENT):
  Agent modifies spec file as part of ticket work
    |
    v
  Agent commits with descriptive message
    |
    v
  On next scan: transaction log entry auto-created
    |  Linked to active ticket for this project
    |  Files detected via git diff
```

**Reads:** Specifications/{name}/ directory, git log
**Writes:** Spec files, Specifications repo commits, transaction log
**Events emitted:** `spec_updated`

---

## 11. Script Endpoint API [ROADMAP]

**Trigger:** External caller (agent, tool, or another service) POSTs to the script endpoint by project name and script name.

```
POST /api/{name}/run/{script}
  |
  v
Resolve project by name slug --> projects.name == {name}
  |  --> 404 if project not found or is_active = false
  |
  v
Resolve operation by script name --> operations.cmd LIKE '%{script}%'
  |  --> 404 if operation not registered (script missing # CommandCenter Operation header)
  |
  v
Delegate to Run Operation flow (Flow 2)
  |  Identical execution: subprocess, log file, op_runs record
  |
  v
Return JSON: { "run_id": N, "status": "started", "log": "/api/{name}/runs/{run_id}/log" }

GET /api/{name}/runs
  |
  v
Query op_runs WHERE project_id = (SELECT id FROM projects WHERE name = {name})
ORDER BY started_at DESC LIMIT 20
  |
  v
Return JSON array of run records: run_id, script, status, started_at, finished_at, exit_code
```

**Reads:** `projects` table, `operations` table
**Writes:** `op_runs` table, log file (via Flow 2)
**Events emitted:** `operation_started`, `operation_completed` or `operation_failed`

**Why MVP:** Reuses the entire operation engine — only new code is route parsing and the JSON response wrapper. Enables agents and external tools to trigger scripts without the UI. Required for "AI Agent Submission" (trigger build/test from a ticket).

---

## 12. Service Catalog API [ROADMAP]

**Trigger:** External caller (another project, agent, or portfolio page) GETs the catalog.

```
GET /api/catalog
  |
  v
SELECT name, display_name, short_description, status, port, health_endpoint,
       stack, has_docs, card_show, deploy_url, git_repo
FROM projects
WHERE is_active = true
ORDER BY display_name
  |
  v
Return JSON array of project summaries

GET /api/catalog/{name}
  |
  v
Same fields for a single project
  |  --> 404 if not found
  |
  v
Return JSON object
```

**Reads:** `projects` table
**Writes:** None
**Events emitted:** None

**Why MVP:** One SELECT, no logic. Makes the dashboard's project knowledge available to agents and inter-service calls. Backs the "Full Service Catalog" feature — a running service can discover what other services exist, their ports, and their health endpoints without any shared config.

---

## 13. Project Health API [ROADMAP]

**Trigger:** External caller polls per-project health; also used by dashboard to render health badges without a full page load.

```
GET /api/{name}/health
  |
  v
Resolve project by name slug
  |  --> 404 if not found
  |
  v
Query heartbeats WHERE project_id = {id}
  |  One row per heartbeat_type: service_health, process_state, git_state, compliance
  |
  v
Compute aggregate status:
  |  ALL UP/CLEAN/COMPLIANT --> "healthy"
  |  ANY DOWN/ERROR         --> "degraded"
  |  ANY UNKNOWN            --> "unknown"
  |
  v
Return JSON:
{
  "name": "MyProject",
  "aggregate": "healthy" | "degraded" | "unknown",
  "heartbeats": {
    "service_health":  { "state": "UP", "uptime_pct": 99.8, "response_ms": 42 },
    "process_state":   { "state": "RUNNING" },
    "git_state":       { "state": "CLEAN" },
    "compliance":      { "state": "COMPLIANT" }
  },
  "checked_at": "20260321_143000"
}
```

**Reads:** `heartbeats` table, `projects` table
**Writes:** None
**Events emitted:** None

**Why MVP:** Zero logic beyond a join — heartbeat poller already writes these rows (Flow 6). Feeds "Project Health KPIs" on the portfolio page and lets external monitors check project health without scraping the dashboard HTML.

---

## Flow Summary

| # | Flow | Trigger | Implemented |
|---|------|---------|-------------|
| 1 | Project Scan | Startup / Rescan button | Yes |
| 2 | Run Operation | Operation button click | Yes |
| 3 | Stop Operation | Stop button click | Yes |
| 4 | Git Push | Push button click | Yes |
| 5 | Portfolio Publish | Rebuild / Publish buttons | Yes |
| 6 | Heartbeat Poll | Timer / Monitoring refresh | ROADMAP |
| 7 | Schedule Fire | Cron tick / startup catch-up | ROADMAP |
| 8 | Ticket Lifecycle | Create / drag ticket | Partial |
| 9 | Configuration Edit | Cog icon / inline edit | Yes |
| 10 | Specification Management | Spec link / agent commit | ROADMAP |
| 11 | Script Endpoint API | External POST to /api/{name}/run/{script} | ROADMAP |
| 12 | Service Catalog API | External GET /api/catalog | ROADMAP |
| 13 | Project Health API | External GET /api/{name}/health | ROADMAP |

---

## Cross-Cutting Concerns

### Event Emission

Every flow emits events (see DATABASE.md → events). Events are written to the `events` table and surfaced on:
- Monitoring screen (platform-wide timeline)
- Project detail (per-project event log)

### Error Handling

All flows follow the same pattern:
- Catch exceptions at the route level
- Flash error message to user
- Log to platform log (not project log)
- Never crash the platform — a single project failure must not affect others

### HTMX Partial Updates

Flows that change UI state return HTML fragments, not full pages:
- Run/Stop --> updated button state fragment
- Push --> updated git status fragment
- Scan --> status message fragment
- Config edit --> updated row fragment

The browser replaces the targeted DOM element. No full page reload unless navigating to a different screen.

### Concurrency

- Only one instance of a given operation can run per project at a time
- Multiple different operations can run simultaneously across projects
- Scanner runs async — dashboard is usable during scan
- Heartbeat poller runs on its own timer, independent of user actions
- Scheduler runs on its own timer, independent of heartbeat poller


---

## Spec: README.md

# GAME — Generic AI Management Environment

A dashboard for project owners managing AI-assisted prototypes.

Common built-in standards provide enterprise features out of the box. Projects conform to a simple set of development best practices which your agent implements for you. Each project has a minimal configured set of instructions in its rules which expose operations, endpoints, capabilities, documentation, and command-and-control in a standard way.

## Intent

**Purpose 1: Dashboard for the Project Owner**

Manage projects you want to keep around and update — software, books, or any project type. See everything in one place: status, health, operations, logs, documentation.

**Purpose 2: Conform projects to standards**

Standard workflow benefits any Technical Product Owner:
- One-shot project creation from templates
- Project conformity via CLAUDE_RULES injection
- Conformed projects expose: Start/Stop, Operations, Health, Logging, Documentation, Testing
- Exposed capabilities appear automatically in the dashboard

**Purpose 3: Prototype workflow**

- Feature tickets tracked from idea to done
- AI transaction logs capture decisions and rationale
- Specification management links specs to running code

## The Prototyper Application

- Flask UI with configurable snap-in screens
- Best-practice screens for managing all project features
- Filter and sort by project, status, tags, namespace
- Simple elegant design — form follows function, less is more

## Stack

- **Language:** Python
- **Framework:** Flask (app factory, blueprints, HTMX for partial updates)
- **Database:** SQLite (WAL mode, single file at `data/prototyper.db`)
- **Frontend:** Bootstrap 5 (dark theme, CDN)
- **Port:** 5001

Each stack component maps to a prescriptive reference file in `../RulesEngine/stack/`.

## Specifications

All project integration standards are defined in `../RulesEngine/CLAUDE_RULES.md`.

| Document | Answers |
|----------|---------|
| **FUNCTIONALITY.md** | End-to-end flows: trigger → sequence → result |
| **ARCHITECTURE.md** | How is code organized? Modules, routes, data flow |
| **DATABASE.md** | Tables, columns, constraints, field sources |
| **UI-GENERAL.md** | Shared UI patterns: nav bar, headers, dark theme, HTMX |
| **SCREEN-*.md** | Per-screen: route, layout, interactions |

**Flow:** ARCHITECTURE describes modules → DATABASE defines storage → UI-GENERAL defines shared patterns → SCREEN-* defines per-screen layout.

## Building From This Specification

```bash
bash ../bin/validate.sh GAME
bash ../bin/build.sh GAME > build-prompt.md
```

The generated prompt includes all stack reference files followed by all specification files. An AI agent reading this prompt has everything needed to build GAME from scratch.


---

## Spec: SCREEN-CONFIGURATION.md

# Screen: Configuration

**Version:** 20260320 V1  
**Description:** Spec for the Configuration screen

A Baseline screen for editing project metadata across all projects in a single list.

## Route

```
GET /project-config
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Configuration`.

## Configuration Column

Three editable fields per project row:

| Field | Label | Source | Input |
|-------|-------|--------|-------|
| Port | `port:` | `projects.port` | number |
| Show on homepage | `show:` | `projects.card_show` | checkbox |
| Tags | `tags:` | `projects.tags` | text |

Fields persist on change per DATABASE.md rules. Each field saves independently — no Save button.

## Single-Project Editor

Clicking the cog icon navigates to SCREEN-PROJECT for full metadata editing organized by source.

## Open Questions

- Should the batch Configuration column include additional fields (namespace, desired_state)?


---

## Spec: SCREEN-DASHBOARD.md

# Screen: Dashboard

**Version:** 20260320 V1  
**Description:** Spec for the Dashboard screen

**The main view.** Shows every discovered project with status, operations, and quick links. This is the landing page.

## Route

```
GET /
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Links,Actions,Help`.

## Layout

Full-width project list. One row per project. Nav bar at top per UI-GENERAL. Filter bar below nav.

## Per-Project Row

Uses the Baseline fixed columns (status badge, namespace, icon + name, cog) plus:

| Column | Source | Interaction |
|--------|--------|-------------|
| Links | `extra.links`, server link from `port` | Click → open URL in new tab |
| Actions | `operations` (category != maintenance) | Operation buttons per UI-GENERAL |
| Help | `has_docs`, `extra.doc_path` | Green Documentation button → `/project/{id}/doc/` in new tab |

Running projects show a green dot indicator in the project name cell.

## Project Detail (click project name or cog)

Navigates to SCREEN-PROJECT for the selected project.

## Actions

| Action | Trigger | Effect |
|--------|---------|--------|
| Run operation | Click button | Launches script, button shows running state |
| Stop operation | Click running button | Sends SIGTERM |
| Filter | Text/tag/status/namespace controls | Client-side row filtering |
| Rescan | Nav bar button | POST `/api/scan`, refreshes project list |
| Push | Per-project (shown when `git_unpushed > 0`) | POST `/api/push/{id}` |

## Startup Behavior

Scanner reads METADATA.md, AGENTS.md, and bin/ headers. Missing files produce compliance gaps, not errors. Projects removed from disk are marked inactive.

## Data Flow

| Reads | Writes |
|-------|--------|
| Project scanner results | Operation launch requests |
| Process engine run states | Git push commands |
| Tag color config | |

## Open Questions

- Should the dashboard auto-refresh running project status on a timer, or only on explicit action?


---

## Spec: SCREEN-DEFAULT.md

# Screen: Baseline

**Version:** 20260320 V1  
**Description:** Spec for the Baseline screen

A sortable, filterable, configurable project list. Middle columns are passed as arguments, making this a reusable base for named views.

## Route

```
GET /default?title=DEFAULT&columns=Links,Actions,Help&filter=normal&sort=name
```

| Param | Default | Purpose |
|-------|---------|---------|
| `title` | DEFAULT | Section header and nav label |
| `columns` | Links,Actions,Help | Comma-separated middle column keys |
| `filter` | normal | Filter state: `normal` / `all` / `idea` / `archive` |
| `sort` | name | `name`, `status_asc`, `status_desc` |

## Layout

Full viewport width — no max-width cap. Sortable table. Column header click sorts; current direction shown with arrows.

## Filter Button

Single cycling button in the section header:

```
normal → all → idea → archive → normal
```

| State | Shows |
|-------|-------|
| `normal` | All except IDEA and ARCHIVED |
| `all` | All projects |
| `idea` | Status = IDEA only |
| `archive` | Status = ARCHIVED only |

State is a URL query param; clicking generates a link with the next state.

## Table Structure

### Fixed Columns (every row)

| Position | Content | Source | Interaction |
|----------|---------|--------|-------------|
| First | Status badge | `projects.status` | Click → cycle IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED; writes DB + METADATA.md |
| Second | Namespace badge | `projects.namespace` | Hidden when value is `development` |
| Third | Icon + project name | `projects.project_type`, `projects.display_name` | Name links to `/project/{id}`; nowrap |
| Last | Settings cog | — | Links to `/project/{id}` |

### Middle Columns

| Column Key | Header | Source | Renders |
|------------|--------|--------|---------|
| `Tags` | Tags | `projects.tags` | Colored tag pills |
| `Port` | Port | `projects.port` | Port number; clickable inline edit |
| `Stack` | Stack | `projects.stack` | Monospace string |
| `Actions` | Actions | `operations` (category != maintenance) | Operation buttons per UI-GENERAL |
| `Links` | Links | `projects.extra.links` | Link buttons; fallback to server link if port set |
| `Claude` | CLAUDE.md | `projects.has_claude` | Opens AGENTS.md content in modal |
| `Help` | Help | `projects.has_docs` + `extra.doc_path` | Green Documentation button → proxy route → new tab |
| `Maintenance` | Maintenance | `operations` (category = maintenance) | Operation buttons |
| `LastUpdate` | Updated | `projects.version` | Date portion only; strips `.N` suffix |
| `Configuration` | Configuration | `projects.port`, `card_show`, `tags` | Inline-editable fields per SCREEN-CONFIGURATION |

## Open Questions

- Should column selection be persisted per-user (localStorage) or always from URL params?


---

## Spec: SCREEN-MONITORING.md

# Screen: Monitoring

**Version:** 20260320 V1  
**Description:** Spec for the Monitoring screen

**Service health dashboard and event timeline.** Polls running services, shows status, alerts on failure.

## Route

```
GET /monitoring
```

## Layout

Two sections: Health Table (top), Event Timeline (bottom).

## Health Table

| Column | Source | Content |
|--------|--------|---------|
| Project name | `projects.display_name` | Standard row header |
| Endpoint | `port` + `health_endpoint` | e.g., `localhost:5001/health` |
| Status | Heartbeat poller | UP (green) / DOWN (red) / UNKNOWN (gray) badge |
| Last checked | `heartbeats.last_checked` | Timestamp |
| Response time | `heartbeats.response_ms` | Milliseconds |
| Uptime | `heartbeats.uptime_pct` | Rolling 24h percentage |

Only projects with both `port` and `health_endpoint` appear.

## Event Timeline

Chronological list of platform events from the `events` table. Each row:

| Column | Content |
|--------|---------|
| Timestamp | When it happened |
| Project | Which project (or "Platform") |
| Event | Type + summary (e.g., "operation_completed: Start Server exited 0") |

Filter by project or event type. Most recent events first.

## Alerts

Banner notification when a service changes state (UP→DOWN or DOWN→UP). Links to the affected project.

**States:** `UNKNOWN → UP → DOWN → UP` (cycle). SNOOZED suppresses alerts but continues polling.

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Refresh | Button or auto-timer | Re-polls all health endpoints |
| Snooze | Click on alert | Suppresses alerts for that service |
| Filter events | Dropdown/text | Filters timeline |
| Click project | Name link | Navigates to SCREEN-PROJECT |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` (port, health) | `heartbeats` table |
| HTTP health endpoints | `events` table (state transitions) |
| Process engine (running state) | Alert notifications |

## Open Questions

- What should the polling interval be? Configurable per-project or global?
- Should alerts use browser notifications or just in-page banners?


---

## Spec: SCREEN-PROCESSES.md

# Screen: Processes

**Version:** 20260320 V1  
**Description:** Spec for the Processes screen

**Live log viewer and process control.** Shows what is running, what ran, and the output.

## Route

```
GET /processes
```

## Layout

Project list with expandable rows. If a project has running processes, they show inline with a View Log button. Expand a row to see prior run history.

## Process List

Standard header per SCREEN-DEFAULT (status badge, icon, name). Each row expands to show:

| Column | Source | Content |
|--------|--------|---------|
| Operation | `op_runs.name` | Derived from script filename |
| Status | `op_runs.status` | RUNNING / DONE / ERROR / STOPPED badge |
| Started | `op_runs.started_at` | Timestamp |
| Duration | Calculated | Elapsed (if running) or total |
| View Log | Button | Opens log viewer |
| Stop | Button | Sends SIGTERM (shown only when RUNNING) |

The list is sortable and filterable. Short names only — no full pathnames since project and script are known.

## Log Viewer

Monospace output area. Auto-scrolls while process is running. Stops on exit.

Header: project name, operation name, status badge, start time.

Controls: Stop (if running), Back to list.

## State Machine

```
IDLE → STARTING → RUNNING → DONE
                           → ERROR (non-zero exit)
                           → STOPPED (user cancelled)
```

Platform parses `[$PROJECT_NAME]` status lines from output to track transitions.

## Log Files

Named per CLAUDE_RULES: `logs/{project}_{script}_{yyyymmdd_hhmmss}.log`. Project name prepended for sorting.

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Expand row | Click project | Shows run history |
| View log | Click button | Opens log viewer panel |
| Stop process | Click Stop | SIGTERM to process group |
| Filter | Text/status | Client-side filtering |

## Data Flow

| Reads | Writes |
|-------|--------|
| `op_runs` table | Stop signal → process |
| Log files | Running count → nav bar badges |

## Open Questions

- Should log viewer support text search within output?


---

## Spec: SCREEN-PROJECT.md

# Screen: Project Detail

**Version:** 20260320 V1  
**Description:** Spec for the Project Detail screen

**Single-project deep view.** Shows all metadata, operations, run history, links, and events for one project. Also serves as the metadata editor for that project.

## Route

```
GET /project/{id}
```

## Layout

Two-column layout. Left: project info card + metadata editor. Right: operations + recent activity.

## Project Info Card (top-left)

| Field | Source | Editable |
|-------|--------|----------|
| Display name | `projects.display_name` | Yes |
| Status badge | `projects.status` | Yes (click to cycle) |
| Short description | `projects.description` | Yes |
| Stack | `projects.stack` | Yes |
| Port | `projects.port` | Yes |
| Namespace | `projects.namespace` | Yes |
| Tags | `projects.tags` | Yes (inline tag editor) |
| Version | `projects.version` | Display only |
| Health endpoint | `projects.health_endpoint` | Yes |
| Desired state | `projects.desired_state` | Yes (toggle) |

Fields save on blur/tab-out. Writes go to both database and METADATA.md per DATABASE.md rules.

## Metadata Editor (below info card)

Organized by source:

**From METADATA.md** — editable key:value fields, grouped by category (Identity, Technology, Portfolio).

**From Scanner** — read-only detected flags: `has_git`, `has_venv`, `has_node`, `has_claude`, `has_docs`, `has_tests`, `has_specs`. Shown as boolean indicators.

**From bin/ scripts** — read-only operations list with script name, category, schedule, timeout.

## Operations Panel (top-right)

All registered operations for this project. Each shows:

| Element | Content |
|---------|---------|
| Button | Operation name, styled by category per UI-GENERAL |
| Status | Running indicator if active |
| Last run | Timestamp and exit status of most recent run |

## Recent Activity (bottom-right)

Last 20 events for this project from the `events` table. Each row: timestamp, event type, summary.

## Quick Links

| Link | Source | Behavior |
|------|--------|----------|
| Server | `port` | Opens `localhost:{port}` in new tab |
| Documentation | `extra.doc_path` | Opens doc index in new tab |
| CLAUDE.md | `has_claude` | Opens AGENTS.md content in modal |
| Git repo | `extra.links` | Opens repo URL in new tab |
| Specifications | `has_specs` | Opens spec directory index in new tab |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Edit field | Tab out / blur | Saves to DB + METADATA.md |
| Run operation | Click button | Launches script |
| View log | Click last-run link | Navigates to log in SCREEN-PROCESSES |
| Back to list | Back button or nav | Returns to Dashboard |

## Open Questions

- Should the metadata editor support adding new custom fields not in the METADATA.md template?


---

## Spec: SCREEN-PUBLISHER.md

# Screen: Portfolio

**Version:** 20260320 V1  
**Description:** Spec for the Portfolio screen

**Portfolio site management.** Builds and publishes a static GitHub Pages portfolio from project METADATA.md fields.

## Route

```
GET /publisher
```

## Layout

Four sections stacked vertically: Build, Preview, Publish, Homepage.

## Build Section

- Rebuild button
- Last build timestamp and status
- Error output panel below (clearly labeled, shown only on failure)

## Preview Section

- Start/Stop toggle button (starts local preview server if not running, stops if running)
- Preview URL button (always visible, opens localhost preview in new tab)

## Publish Section

- Push to GitHub Pages button
- Last publish timestamp

## Homepage Section

- Link to live site (opens in new tab)

## How It Works

1. Scan all projects where `show_on_homepage = true`
2. Parse card fields: `card_title` (fallback: `display_name`), `card_desc` (fallback: `short_description`), `card_tags` (fallback: `tags`), `card_image` (fallback: `logo`)
3. If project has `doc/index.html`, add documentation link to card
4. Generate static site from `config/site_config.md` branding
5. Serve locally or push to GitHub Pages

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Rebuild | Click button | POST `/publisher/build`, regenerates site |
| Toggle preview | Click button | Starts/stops local server |
| Publish | Click button | POST `/publisher/publish`, pushes to GitHub Pages |
| View live | Click link | Opens production URL in new tab |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (card fields) | Static site output files |
| `config/site_config.md` | GitHub Pages branch (git push) |
| Project `doc/` directories | |

## Open Questions

- Should the preview section show a card grid preview inline, or only via the external URL?


---

## Spec: SCREEN-WORKFLOW.md

# Screen: Workflow

**Version:** 20260320 V1  
**Description:** Spec for the Workflow screen

**Kanban board for prototype lifecycle management.** Tracks features and prototypes from idea through implementation to completion.

## Route

```
GET /workflow
```

## Layout

Kanban columns (one per state) spanning the viewport. Filter bar at top: filter by project, tag, priority. New Ticket button.

## States

| State | Meaning |
|-------|---------|
| IDEA | First capture, not reviewed |
| PROPOSED | Has summary and plan |
| READY | Has acceptance criteria, scheduled for work |
| IN DEVELOPMENT | AI session running or recently finished |
| TESTING | Work complete, human validating |
| DONE | Accepted |

States are configurable via `workflow.json`. New states can be added.

## Ticket Card

Each card shows:

| Field | Content |
|-------|---------|
| Title | Ticket title, clickable to open detail |
| Project | Project badge (colored by project) |
| Priority | Low / Medium / High / Critical indicator |
| Tags | Ticket-level tag pills |
| Age | Time since creation or last transition |

## Ticket Detail (modal or slide-out)

| Section | Content |
|---------|---------|
| Title + description | Editable text |
| State | Current state with transition buttons |
| Acceptance criteria | Required at READY state |
| AI Transaction Log | What was decided, what was built, why (populated during IN DEVELOPMENT) |
| Test notes | Human validation notes (at TESTING) |
| History | State transition timeline |

## Transitions

```
IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE
                               ↑                |
                             READY ←────────────┘ (rework)
                           PROPOSED ←──────────── (redesign)
```

Drag ticket between columns or click state buttons. Validation enforced:
- IDEA → PROPOSED requires summary
- PROPOSED → READY requires acceptance criteria
- IN DEVELOPMENT → TESTING requires work completed

## Prototype Lifecycle View

Filter to a single project to see its prototype lifecycle:
- All tickets for that project across all states
- Progress bar showing tickets by state
- Links to specification files if `has_specs = true`

## AI Integration

Tickets in READY state can be submitted to an AI agent for automated implementation. The agent:
1. Reads ticket description + acceptance criteria
2. Implements changes
3. Logs decisions to the AI Transaction Log
4. Moves ticket to TESTING when done

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Create ticket | New Ticket button | Opens creation form |
| Move ticket | Drag to column | Validates and transitions state |
| Open detail | Click card | Shows ticket detail |
| Filter | Project/tag/priority controls | Filters visible cards |
| Submit to AI | Button on READY tickets | Queues for automated implementation |

## Data Flow

| Reads | Writes |
|-------|--------|
| `tickets` table | Ticket state transitions |
| `workflow.json` (state definitions) | AI transaction log entries |
| Project spec files | `events` table (ticket_transition) |

## Open Questions

- Should DONE tickets auto-archive after a configurable period?
- How should the AI agent integration be triggered — queue, webhook, or manual?


---

## Spec: UI-GENERAL.md

# UI General Standards

**Version:** 20260320 V1  
**Description:** Shared UI patterns and conventions across all screens

**Shared UI patterns, components, and conventions used across all screens.**

All SCREEN-*.md files reference this document for shared elements. Screen specs define only what is unique to that screen.

---

## Theme

Dark theme using Bootstrap 5 `data-bs-theme="dark"`. Custom CSS in `static/style.css` extends Bootstrap with platform-specific variables:

| Variable | Purpose | Value |
|----------|---------|-------|
| `--cc-surface` | Card/panel background | Dark surface |
| `--cc-border` | Border color | Subtle dark border |
| `--cc-muted` | Secondary text | Muted gray |

No JS build step. Bootstrap 5 via CDN. HTMX via CDN.

---

## Navigation Bar

Fixed top bar present on all screens. Components left to right:

| Element | Behavior |
|---------|----------|
| **Brand** (`cc-brand`) | App name with command icon. Click --> project list. |
| **Tab links** | Projects, Configuration, Processes, Publisher, Monitoring, Workflow. Active tab highlighted. |
| **Documentation button** | Opens `doc/index.html` in new tab. |
| **Settings dropdown** | Hamburger icon. Contains: Settings, Tags, Help. |
| **Running badges** | Green pill badges for each currently-running project. Click --> project detail. |

---

## Standard Row Header

Several screens share a standard row header pattern for project rows:

| Column | Content | Width |
|--------|---------|-------|
| Status badge | Colored pill: IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED | Fixed |
| Project icon | Emoji or type icon | Fixed |
| Display name | `display_name` from METADATA.md, clickable | Flex |

This pattern appears on: Dashboard, Configuration, Processes (as project column), Publisher.

Status badge colors:

| Status | Color | Hex |
|--------|-------|-----|
| IDEA | Slate | `#94a3b8` |
| PROTOTYPE | Amber | `#fdab3d` |
| ACTIVE | Blue | `#0073ea` |
| PRODUCTION | Green | `#00c875` |
| ARCHIVED | Gray | `#4a5568` |

---

## Settings Icon (Cog)

Used on multiple screens. The cog icon opens a detail/edit view for the project's METADATA.md fields. Context-dependent behavior:

| Screen | Cog Action |
|--------|------------|
| Dashboard | Opens project detail with inline editing |
| Configuration | Opens full METADATA.md field editor |
| Publisher | Opens publication field editor |

---

## Tag Pills

Tags render as small colored pills. Color from `tag_colors` table/config. Inline editable on some screens.

```html
<span class="badge" style="background: {tag_color}">{tag_name}</span>
```

---

## Cards

Content panels use a card pattern:

```html
<div class="cc-card">
    <div class="cc-card-header">Section Title</div>
    <div style="padding: 1rem">
        <!-- content -->
    </div>
</div>
```

---

## Modals

Two global modals defined in `base.html`:

| Modal | ID | Purpose |
|-------|----|---------|
| CLAUDE.md Viewer | `claudeModal` | Shows AGENTS.md content for a project |
| Command Output | `opOutputModal` | Shows operation stdout/stderr output |

Modals use dark surface background with themed borders.

---

## HTMX Conventions

All screen interactions use HTMX partial page updates:

| Pattern | Usage |
|---------|-------|
| `hx-get` | Load fragments (project detail, log content) |
| `hx-post` | Trigger actions (run op, stop, push, scan) |
| `hx-target` | Replace specific DOM element with response |
| `hx-swap` | Usually `innerHTML` or `outerHTML` |
| `hx-trigger` | Click (default), or custom events |

Server returns HTML fragments, never JSON (except `/health`).

---

## Operation Buttons

Rendered per-operation on dashboard rows and project detail:

| State | Appearance | Action |
|-------|------------|--------|
| Idle | `op-btn` styled button with operation name | Click --> run |
| Running | Green pulsing indicator, "Stop" label | Click --> SIGTERM |
| Recently completed | Brief success/error flash | Auto-reverts to idle |

Category determines button style:

| Category | Style Class |
|----------|-------------|
| `service` | `op-btn--service` |
| `local` | `op-btn--local` |
| `maintenance` | `op-btn--maintenance` |

---

## Filter Bar

Dashboard and other list screens share a filter pattern:

| Filter | Type | Behavior |
|--------|------|----------|
| Text search | Input field | Filters rows by name/description match |
| Status filter | Pill buttons | Toggle visibility by status |
| Tag filter | Pill buttons | Filter by selected tags |
| Namespace filter | Dropdown | Filter by namespace |

Filters are client-side (no server round-trip) for responsiveness.

---

## Flash Messages

Standard Bootstrap 5 alert dismissible pattern. Categories: `success`, `danger`, `warning`, `info`.

---

## Typography

System font stack (no web fonts). Monospace for logs and code output.

| Element | Font | Size |
|---------|------|------|
| Body | System sans-serif | 14px |
| Headings | System sans-serif | 16-20px |
| Log output | System monospace | 13px |
| Badges/pills | System sans-serif | 11px |

---

## Responsive Behavior

Designed for desktop use (operations center). Minimum supported width: 1024px. Nav bar scrolls horizontally on smaller screens. No mobile-first breakpoints.


---

# END OF ONESHOT PROMPT

Build this project following the conversion rules, integration standard, technology references, and specification files above.
All patterns in the technology references are prescriptive — use them exactly as shown.
Expand concise specifications inline according to the conversion rules during implementation.
