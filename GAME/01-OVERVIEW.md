# GAME — Generic Agent Management Environment
## Project Specification v2  ·  Updated 2026-03-09

> Visual architecture diagrams: `GAME/project_specifications/spec_v2/*.excalidraw`
> v1 spec preserved in `Version 1/` in this directory.

## Purpose

GAME is a personal AI-assisted workflow management platform for managing ~15 projects (software, books, tools) from a single web dashboard. It auto-discovers projects from the filesystem, provides one-click operations via bash scripts with standard `CommandCenter Operation` headers, monitors background processes, enforces stack governance, and publishes a GitHub Pages portfolio.

GAME is also an **Agent Assist platform**: it manages its own specification, categorizes projects, generates per-project Claude configurations via `config_engine/`, and guides feature development through a structured prompt-driven lifecycle (Idea → Checklist → Proposal → Iteration → Agent Developed → Testing → Done).

## Scope

This specification covers the full system:
- Project discovery and metadata (filesystem-driven via CLAUDE.md, Links.md, git_homepage.md, bin/ headers)
- Operations engine (bin/ auto-registration → UI buttons → spawn.py → log capture)
- Process management and observability (heartbeats, alerts, process logs)
- GitHub Pages publishing pipeline (publisher.py + Astro + My_Github repo)
- Config engine (YAML profiles → staged Claude configs → ~/.claude/)
- Feature workflow (Idea → Done with Agent Assist at each stage)
- External skill integration (Excalidraw, daily summary, etc.)

## Tech Stack

| Layer      | Technology                                  |
|------------|---------------------------------------------|
| Backend    | Python 3 / Flask                            |
| Database   | SQLite (WAL mode, `data/cc.db`)             |
| Frontend   | Bootstrap 5.3 (CDN) + HTMX 2.0 (CDN)       |
| Styling    | Single `static/style.css`, dark theme only  |
| Templates  | Jinja2 (Flask default)                      |
| Process Mgmt | `subprocess.Popen` + background threads   |
| No build step | No webpack/vite/npm for the app itself   |

## Dependencies

```
flask
python-dotenv
PyYAML
```

## Environment Variables

| Variable       | Required | Default                              | Purpose                        |
|----------------|----------|--------------------------------------|--------------------------------|
| `PROJECTS_DIR` | Yes      | Parent of app directory              | Root directory containing projects |
| `SECRET_KEY`   | No       | `cc-dev-key-change-in-prod`          | Flask session key              |
| `PRODUCTION_URL` | No     | `https://webcloudstudio.github.io`   | Live homepage URL              |
| `APP_NAME`     | No       | `Command Center`                     | Displayed in nav bar           |

## Directory Layout

```
commandcenter/
  app.py                  # Flask app factory, startup scanner
  db.py                   # SQLite schema, helpers, migrations
  models.py               # Project type registry
  scanner.py              # Filesystem project discovery
  routes.py               # All Flask routes (Blueprint)
  ops.py                  # Operation execution engine
  spawn.py                # Generic process spawning service
  publisher.py            # GitHub Pages rebuild/publish
  claude_convention.py    # CLAUDE.md parsing & stubbing
  usage_analyzer.py       # Token usage analytics
  static/
    style.css             # Full stylesheet (dark theme)
  templates/
    base.html             # Layout: nav, modals, flash messages
    list.html             # Projects tab
    project_config.html   # Configuration tab
    publish.html          # GIT-Homepage tab
    processes.html        # Processes tab
    settings.html         # Settings page (hamburger)
    tags.html             # Tag colors page (hamburger)
    usage.html            # Usage analytics page (hamburger)
    help.html             # Help page (hamburger)
    types/
      _software_row.html      # Software project row
      _software_detail.html   # Software project detail page
      _book_row.html          # Book project row
      _book_detail.html       # Book project detail page
    components/
      _project_standard_columns.html  # Shared first 2 columns
      _project_editor_row.html        # Config page row
  bin/
    RebuildYourHomepage.sh  # npm build for homepage
    LocalPreview.sh         # npm preview server
    PushAndPublish.sh       # git add/commit/push
  data/                     # Runtime data (gitignored)
    cc.db                   # SQLite database
    logs/                   # Process log files
    tag_colors.json         # Tag color mappings
    publish_clicks.json     # Last button click timestamps
  workflow.json             # Optional custom workflow states
```

## Navigation Structure

### Top Tabs
1. **Projects** — Main project list with operations
2. **Configuration** — Bulk project settings (workflow, type, publish)
3. **GIT-Homepage** — GitHub Pages publish pipeline
4. **Processes** — Running/completed process monitor

### Hamburger Menu (top-right)
- Settings — App name, homepage URL
- Usage — Claude Code token analytics
- Tags — Tag color management
- Help — Feature documentation

### Running Projects Bar
- Shows green badges in nav for any project with a running server process
