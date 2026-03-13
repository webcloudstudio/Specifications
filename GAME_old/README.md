# GAME — Generic Agent Management Environment

**Status**: Specification v2 | **Updated**: 2026-03-09

AI-assisted workflow management platform that governs a portfolio of projects (~15 projects: software, books, tools) from a single web dashboard. Auto-discovers projects from the filesystem, provides one-click operations via bash scripts, monitors background processes, enforces stack governance, and publishes a GitHub Pages portfolio.

---

# Catalog

| File | Description |
|------|-------------|
| `01-OVERVIEW.md` | System purpose, scope, tech stack, dependencies, directory layout, navigation structure |
| `02-DATABASE.md` | SQLite schema, tables (projects, operations, processes, tags), relationships, migrations |
| `03-SCANNER.md` | Filesystem project discovery, metadata extraction, file conventions (CLAUDE.md, Links.md, bin/ headers) |
| `04-OPERATIONS.md` | Operation execution engine, bash script auto-registration, run history, logging, process spawning |
| `05-ROUTES-API.md` | Flask routes for all tabs and features, REST API endpoints, request/response formats |
| `06-UI-TEMPLATES.md` | Jinja2 templates structure, component reuse, conditional rendering, HTMX integration |
| `07-STYLING.md` | Single CSS file (`static/style.css`), dark theme only, Bootstrap 5 integration, responsive design |
| `08-PUBLISHER.md` | GitHub Pages pipeline, Astro integration, homepage card generation, deployment workflow |
| `09-PROCESSES.md` | Background process management, heartbeat monitoring, process log capture, alert system |
| `10-CONVENTIONS.md` | File naming, git hygiene, directory layout, CLAUDE.md standard sections, bin/ script headers |
| `11-STARTUP.md` | Application startup validation, database initialization, scanner verification, health checks |
| `STACK.yaml` | Technology selections, project config, stack rules, directories, environment variables |

---

# Stacks

## Selected Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3 | Core application, scanner, operations engine |
| **Framework** | Flask | Web server (port 5001) for dashboard |
| **Database** | SQLite (WAL mode) | Project metadata, operations log, process tracking |
| **Frontend** | Bootstrap 5.3 (CDN) | Responsive dashboard components, dark theme |
| **Templating** | Jinja2 (Flask default) | Dynamic HTML generation from project metadata |
| **Frontend Interactivity** | HTMX 2.0 (CDN) | Dynamic UI without page reloads |
| **Process Management** | `subprocess.Popen` + threading | Spawn and monitor background jobs |
| **Publishing** | Astro + GitHub Pages | Static portfolio site generation |

## When to Use Each Stack

| Technology | When to Use |
|-----------|----------|
| **Flask** | Building the dashboard, serving pages and APIs |
| **SQLite** | Storing project metadata offline, local caching |
| **Bootstrap 5** | Ensuring responsive, accessible UI across all devices |
| **Astro** | Pre-generating portfolio site for maximum performance |
| **HTMX** | Adding interactivity without full JavaScript framework |
| **subprocess.Popen** | Spawning bash scripts and monitoring long-running tasks |

---

# Prerequisites

## System Requirements

- **Python 3.8+** — Core application runs on Python 3
- **Git** — For version control and project discovery
- **Bash** — For operation scripts and spawning processes
- **Node.js 18+** (optional) — Only needed for Astro homepage building

## Python Dependencies

```
flask==2.3.0
python-dotenv==1.0.0
PyYAML==6.0
```

Install via: `pip install -r requirements.txt`

## Required Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `PROJECTS_DIR` | Root directory containing all managed projects | `/home/user/projects` |

## Optional Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `cc-dev-key-change-in-prod` | Flask session encryption key |
| `PRODUCTION_URL` | `https://webcloudstudio.github.io` | Published homepage URL |
| `APP_NAME` | `Command Center` | Displayed in navigation bar |
| `FLASK_DEBUG` | *(unset)* | Enable Flask debug mode |

## Project Discovery Requirements

Every discovered project must have:

1. **Git Repository** — `.git/` directory present
2. **CLAUDE.md** — Project conventions file with standard sections
3. **git_homepage.md** — GitHub Pages card metadata (name, description, tags, type, URL)
4. **bin/start.sh** — Script with `CommandCenter Operation` header
5. **bin/stop.sh** — Script with `CommandCenter Operation` header

If any requirement is missing, the project shows a warning in the dashboard.

---

# Usage

## Starting the Dashboard

```bash
export PROJECTS_DIR=/path/to/projects
./bin/start.sh              # Runs on http://localhost:5001
```

## Core Features

### Projects Tab
- Lists all discovered projects with auto-discovered metadata
- Shows project type (software, book), status, tech stack
- Displays git status, running processes, available operations

### Configuration Tab
- Bulk-edit project workflow states, types, and publish settings
- Assign tags and categories
- Toggle stack governance enforcement

### GIT-Homepage Tab
- Manage GitHub Pages publishing pipeline
- View and edit portfolio cards
- Rebuild and publish homepage

### Processes Tab
- Monitor running background operations
- View process output and logs in real-time
- Manage process lifecycle (start, stop, restart)

---

# Architecture at a Glance

```
┌──────────────────────────────────────────────┐
│        GAME Dashboard (Flask)                │
│  Port 5001  ·  Bootstrap 5 + HTMX           │
└────────────────────┬─────────────────────────┘
                     │
            ┌────────┴─────────┐
            │                  │
            ▼                  ▼
      ┌──────────────┐  ┌─────────────┐
      │  Scanner    │  │  Operations │
      │ (Discover)  │  │   (Spawn)   │
      └──────┬───────┘  └──────┬──────┘
             │                 │
      ┌──────▼──────────────────▼──────┐
      │   SQLite Database (cc.db)      │
      │  - projects metadata           │
      │  - operation history           │
      │  - process logs                │
      │  - tag colors                  │
      └────────────────────────────────┘
             │
      ┌──────▼────────────┐
      │   Filesystem      │
      │  - CLAUDE.md      │
      │  - git_homepage   │
      │  - bin/ scripts   │
      └───────────────────┘
```

---

# Reliability & Safety

- **Non-Destructive**: Dashboard discovers read-only; only runs explicitly authorized bash scripts
- **Git-Safe**: All operations logged with timestamps; git status preserved
- **Process Isolation**: Each operation runs in isolated subprocess with captured output
- **Offline-Friendly**: Database mirrors filesystem state; can operate without network

---

# Next Steps

1. Review `02-DATABASE.md` for schema design
2. Follow `03-SCANNER.md` to understand project discovery
3. Study `04-OPERATIONS.md` for operation spawning
4. Check `10-CONVENTIONS.md` for your own projects to ensure they're discoverable
