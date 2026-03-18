# GAME Project Feature Map

**Comprehensive catalog of all project attributes, metadata fields, and runtime features.**

This document maps every capability available in GAME as a personal project management platform. Features are organized by: metadata (static), runtime state, operations (actions), and integration points.

---

## I. Project Identity & Metadata

### Core Attributes (METADATA.md)

| Attribute | Type | Source | Purpose | Example |
|-----------|------|--------|---------|---------|
| `name` | string | METADATA.md | Machine slug, unique identifier, matches directory name | `MyProject` |
| `display_name` | string | METADATA.md | Human-readable name for UI | `My Project` |
| `title` | string | METADATA.md or UI | Full display title with tagline | `My Project — Full Stack App` |
| `short_description` | string | METADATA.md | One-sentence summary for cards/lists | `Manages user workflows` |
| `description` | string | METADATA.md | Longer narrative description | Full paragraph or markdown |
| `stack` | string | METADATA.md | Technology summary, slash-separated | `Python/Flask/SQLite` |
| `port` | integer | METADATA.md or UI | Service port (if applicable) | `5001` |
| `version` | string | METADATA.md | Semantic version, YYYY-MM-DD.N format | `2026-03-16.1` |
| `git_repo` | string | METADATA.md | Full HTTPS URL to repository | `https://github.com/org/MyProject` |

### Project Status & Lifecycle

| Attribute | Type | Values | Purpose |
|-----------|------|--------|---------|
| `status` | enum | IDEA, PROTOTYPE, ACTIVE, PRODUCTION, ARCHIVED | Development phase |
| `is_active` | boolean | true/false | Removed from disk = marked ARCHIVED |
| `desired_state` | enum | running, on-demand | Service always-on vs. launch-on-use |
| `namespace` | string | development, qa, production, custom | Environment segregation |

### Project Type & Configuration

| Attribute | Type | Source | Purpose |
|-----------|------|--------|---------|
| `project_type` | enum | METADATA.md or UI | Type registry: `software`, `book`, custom | Determines UI templates and default operations |
| `extra` | JSON blob | METADATA.md | Additional type-specific fields (no schema migration needed) | Store `tech_stack`, `railway_id`, `website_url` |

### Portfolio & Visibility

| Attribute | Type | Purpose |
|-----------|------|---------|
| `card_title` | string | Title shown on portfolio card (if published) |
| `card_desc` | string | Description shown on portfolio card |
| `card_tags` | string | Comma-separated tags for card filtering |
| `card_type` | string | Type badge for card (e.g., "Software", "Book") |
| `card_url` | string | URL linked from card (overrides default) |
| `card_image` | string | Image path for card thumbnail |
| `show_on_homepage` | boolean | Include in published portfolio site |

### Infrastructure & Endpoints

| Attribute | Type | Purpose |
|-----------|------|---------|
| `health_endpoint` | string | Health check path (default: `/health`) |
| `path` | string | Absolute filesystem path to project directory |

### Environment & Runtime Flags

| Attribute | Type | Purpose |
|-----------|------|---------|
| `has_git` | boolean | Git repository detected |
| `has_venv` | boolean | Python venv detected |
| `has_node` | boolean | Node.js detected |
| `has_claude` | boolean | CLAUDE.md / AGENTS.md detected |

### Timestamps

| Attribute | Format | Purpose |
|-----------|--------|---------|
| `updated` | yyyymmdd_hhmmss | Last update timestamp (auto-set by platform) |
| `last_scanned` | yyyymmdd_hhmmss | Last scanner run timestamp |
| `created_at` | ISO 8601 | Record creation time |
| `updated_at` | ISO 8601 | Record last modified |

---

## II. Git Integration & Source Control

### Git Status Attributes

| Attribute | Type | Source | Purpose |
|-----------|------|--------|---------|
| `git_branch` | string | Scanner | Current branch name |
| `git_dirty` | boolean | Scanner | Uncommitted changes detected |
| `git_unpushed` | integer | Scanner | Count of commits not pushed to remote |
| `git_last_commit` | string | Scanner | Message from last commit |

### Git Operations

| Operation | Trigger | Result |
|-----------|---------|--------|
| Push | Dashboard button (shown when `git_unpushed > 0`) | `git push` to remote |
| Scan | Rescan button | Re-reads all METADATA.md, AGENTS.md, bin/ headers |

---

## III. Project-Level Tags & Filtering

### Tag System

| Feature | Details |
|---------|---------|
| **Tag Storage** | Comma-separated string in `projects.tags` |
| **Tag Colors** | Editable via UI → Settings → Tags |
| **Color Persistence** | `data/tag_colors.json` (git-committed) |
| **Filter By Tag** | Dashboard filter pill button |
| **Inline Editing** | Click tag on dashboard to edit |

---

## IV. Operations & Script Registry

### Operation Attributes (from bin/ headers)

Operations are automatically discovered from scripts in `bin/` directory. Each script header registers metadata:

| Attribute | Source | Purpose |
|-----------|--------|---------|
| `script_name` | Filename (e.g., `start.sh`) | Operation identifier |
| `script_path` | Relative path (e.g., `bin/start.sh`) | Execution path |
| `display_name` | Derived from filename | Button label (e.g., "Start Server") |
| `category` | `# Category:` header | Operation group (e.g., `service`, `maintenance`) |
| `port` | `# Port:` header | Service port override |
| `health_path` | `# Health:` header | Health endpoint path |
| `schedule` | `# Schedule:` header | Cron-style recurrence (if applicable) |
| `timeout` | `# Timeout:` header | Max execution time in seconds |

### Built-in Default Operations

For `software` project type, auto-registered based on stack detection:

| Stack | Default Operation | Command |
|-------|-------------------|---------|
| Flask | Start Server | `flask run --port {port}` |
| Django | Start Server | `python manage.py runserver {port}` |
| Node | Start Dev | `npm run dev` |
| Astro | Start Dev | `npm run dev` |
| Bash | Run Script | `./start.sh` |

### Operation Execution (Runs)

When an operation is triggered, a `run` record is created:

| Attribute | Type | Values |
|-----------|------|--------|
| `status` | enum | STARTING, RUNNING, DONE, ERROR, STOPPED |
| `pid` | integer | OS process ID (while running) |
| `exit_code` | integer | Exit status (once finished) |
| `started_at` | yyyymmdd_hhmmss | Start timestamp |
| `finished_at` | yyyymmdd_hhmmss | End timestamp (null while running) |
| `log_path` | string | Path to `logs/{project}_{script}_{yyyymmdd_hhmmss}.log` |

---

## V. Screens & Navigation

### Dashboard Screen
- **Path:** `/`
- **Purpose:** Project list with status, operations, tags, links
- **Elements per row:**
  - Status badge (IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED)
  - Project type icon
  - Display name (clickable → detail)
  - Namespace badge
  - Tags with color coding
  - Stack summary
  - Running indicator (green dot)
  - Operation buttons (dynamic, based on bin/ headers)
  - Quick links (from AGENTS.md bookmarks)
  - Settings icon (click → METADATA.md editor)
- **Filters:** By tag, status, namespace, text search
- **Actions:** Run operation, stop operation, push git, rescan projects

### Project Detail Screen
- **Trigger:** Click project name on dashboard
- **Shows:**
  - All METADATA.md fields
  - All AGENTS.md content (bookmarks, endpoints, services, dev commands)
  - All registered operations with run history
  - Git status and push button
  - Tag editing

### Processes Screen
- **Path:** `/processes`
- **Purpose:** Live monitoring of running operations
- **Shows:** Process list (most recent first), expandable log viewer
- **Columns:** Project, Operation, Status, Start time, Duration, Controls
- **Log Viewer:** Monospace output, auto-scrolls while running, stops on exit
- **Actions:** Stop operation (SIGTERM), view full log, filter/sort

### Configuration Screen
- **Path:** `/config`
- **Purpose:** Project metadata editing
- **Features:** Edit METADATA.md fields inline, save changes

### GIT-Homepage (Publisher) Screen
- **Path:** `/publisher`
- **Purpose:** Portfolio site generation and deployment
- **Features:**
  - Build portfolio from projects where `show_on_homepage = true`
  - Generate card HTML: title, short_description, tags, image
  - Add documentation links (if `doc/index.html` exists)
  - Preview generated site
  - Publish to GitHub Pages

### Monitoring Screen
- **Path:** `/monitoring`
- **Purpose:** Health check aggregation (if defined in operations)
- **Shows:** Service status, uptime, last check time

### Workflow Screen
- **Path:** `/workflow`
- **Purpose:** Kanban-style task board (if tickets enabled)
- **States:** Configurable from `workflow.json` (defaults: IDEA, PROPOSED, READY, IN_DEVELOPMENT, TESTING, DONE)
- **Features:** Drag-drop tickets between states, add/edit tickets per project

### Settings Screen
- **Path:** `/settings`
- **Purpose:** Global platform settings
- **Features:** Tag color management, workflow state editor, environment config

---

## VI. Endpoints & Integration Points

### Bookmarks/Quick Links (from AGENTS.md)

Projects can define bookmarks in `AGENTS.md` under `## Bookmarks`:

```markdown
## Bookmarks
- [Documentation](doc/index.html)
- [Live Site](https://example.com)
```

These appear as clickable links in the dashboard and project detail.

### Service Endpoints (from AGENTS.md)

Projects can define live service endpoints:

```markdown
## Service Endpoints
- Local: http://localhost:5001
```

Endpoints are clickable and can trigger health checks.

### API Routes (for HTMX)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/scan` | Re-scan projects directory |
| POST | `/api/run/{op_id}` | Launch operation |
| POST | `/api/stop/{run_id}` | Stop running operation |
| POST | `/api/push/{project_id}` | Git push |
| GET | `/api/project/{id}` | Fetch project detail fragment |
| GET | `/health` | Health check endpoint |

---

## VII. Integration with AGENTS.md & CLAUDE.md

### Scanner Extraction

On scan, GAME reads:

| File | Extracted Data |
|------|----------------|
| `METADATA.md` | All key:value fields (name, display_name, status, stack, etc.) |
| `AGENTS.md` | Dev commands, service endpoints, bookmarks |
| `bin/` script headers | Operation metadata (category, port, health, schedule, timeout) |

### CLAUDE.md / AGENTS.md Content Viewer

- Dashboard settings icon → opens modal showing full AGENTS.md content
- Displays project context, dev commands, architecture, etc.

---

## VIII. Type Registry & Custom Fields

### Project Types

Defined in `models.py` `PROJECT_TYPES` dict:

| Type | Template | Fields | Default Ops |
|------|----------|--------|-------------|
| `software` | `types/_software_detail.html` | tech_stack, port, railway_id, website_url | Stack-based (Flask, Django, Node, etc.) |
| `book` | `types/_book_detail.html` | (none) | (none) |

### Extensibility

- Add new type to `PROJECT_TYPES` dict
- Create two HTML partials: `_yourtype_detail.html`, `_yourtype_row.html`
- Type-specific fields stored in `extra` JSON column (no migration)

---

## IX. Data Persistence & Lifecycle

### Database Tables

| Table | Purpose | Lifecycle |
|-------|---------|-----------|
| `projects` | Project records | Upserted on scan, marked ARCHIVED if removed from disk |
| `operations` | Registered scripts | Repopulated on scan from bin/ headers |
| `op_runs` | Operation execution history | Permanent record, never deleted |
| `tickets` | Workflow tasks (if enabled) | User-created, lifecycle managed in UI |
| `tag_colors` | Tag color map | User-edited, persistent |
| `config_deployments` | Config rollback history | Auto-created on deploy |

### Log Files

- Stored in `logs/` directory (gitignored)
- Named: `{project}_{script}_{yyyymmdd_hhmmss}.log`
- Captured from operation stdout/stderr
- Parsed for `[$PROJECT_NAME]` status lines

### Configuration Files (git-committed)

- `workflow.json` — Workflow state definitions
- `data/tag_colors.json` — Tag color mappings
- `config/site_config.md` — Site branding for publisher
- `git_homepage.md` — GAME card metadata for portfolio

---

## X. Run-Time State & Monitoring

### Process State Machine

```
IDLE → STARTING → RUNNING → DONE
                          → ERROR (non-zero exit)
                          → STOPPED (user cancelled)
```

### Running Operations Indicator

- Dashboard nav bar shows green badges for running projects
- Per-project green dot on dashboard row
- Aggregated count in nav

### Health Checks

- If operation defines `# Health:` header, platform can poll endpoint
- Status displayed on Monitoring screen
- Integrated with process state machine

---

## XI. Publisher & Portfolio Generation

### Portfolio Site Generation

From projects where `show_on_homepage = true`:

1. Read `card_title`, `card_desc`, `card_image`, `card_tags`, `card_type`
2. Generate HTML card with title, tags, thumbnail, type badge
3. Add "Documentation" link if `doc/index.html` exists
4. Output static site (location configurable)
5. Push to GitHub Pages via `PushAndPublish.sh`

### Source Metadata

- `git_homepage.md` — Metadata for GAME card (stored per-project)
- `config/site_config.md` — Global site branding (YAML frontmatter + markdown body)

---

## XII. Templating & UI Customization

### Template Hierarchy

| Template | Purpose |
|----------|---------|
| `base.html` | Layout with nav bar, modals, global styles |
| `dashboard.html` | Project list and filters |
| `project_detail.html` | Single project expanded view |
| `processes.html` | Process monitor and log viewer |
| `config.html` | Metadata editor |
| `publisher.html` | Portfolio builder controls |
| `settings.html` | Tag colors, workflow editor |
| `help.html` | Documentation viewer |

### Reusable Components

- `components/` — Partials (operation button, tag, badge, etc.)
- `types/` — Type-specific partials (software detail, book detail, etc.)

### HTMX Integration

- All interactions are partial page updates (no full page reloads)
- Server returns HTML fragments, not JSON
- Modals for operation output and CLAUDE.md viewer

---

## XIII. Inventory of Project Attributes

### Complete Attribute Matrix

| Category | Attribute | Type | Mutable | Source |
|----------|-----------|------|---------|--------|
| **Identity** | name | string | ✗ | METADATA.md |
| | display_name | string | ✓ | METADATA.md |
| | title | string | ✓ | UI |
| | description | string | ✓ | METADATA.md |
| **Status** | status | enum | ✓ | METADATA.md |
| | is_active | boolean | Auto | Scanner |
| | desired_state | enum | ✓ | UI |
| | namespace | string | ✓ | METADATA.md |
| **Technology** | stack | string | ✓ | METADATA.md |
| | port | int | ✓ | METADATA.md |
| | project_type | enum | ✓ | UI |
| | health_endpoint | string | ✓ | Operation |
| **Infrastructure** | has_git | boolean | Auto | Scanner |
| | has_venv | boolean | Auto | Scanner |
| | has_node | boolean | Auto | Scanner |
| | has_claude | boolean | Auto | Scanner |
| **Portfolio** | show_on_homepage | boolean | ✓ | UI |
| | card_title | string | ✓ | UI |
| | card_desc | string | ✓ | UI |
| | card_tags | string | ✓ | UI |
| | card_type | string | ✓ | UI |
| | card_image | string | ✓ | UI |
| | card_url | string | ✓ | UI |
| **Git** | git_branch | string | Auto | Scanner |
| | git_dirty | boolean | Auto | Scanner |
| | git_unpushed | int | Auto | Scanner |
| | git_last_commit | string | Auto | Scanner |
| **Metadata** | git_repo | string | ✓ | METADATA.md |
| | version | string | ✓ | METADATA.md |
| | tags | string | ✓ | UI |
| | extra | JSON | ✓ | METADATA.md |
| **Timestamps** | created_at | ISO8601 | ✗ | DB |
| | updated_at | ISO8601 | Auto | DB |
| | last_scanned | yyyymmdd_hhmmss | Auto | Scanner |

---

## XIV. Summary: What Makes a Project Manageable

A "complete" GAME project has:

1. **Identity** → METADATA.md with name, display_name, status, stack, version
2. **Context** → AGENTS.md with dev commands, endpoints, bookmarks, architecture
3. **Operations** → bin/ scripts with CommandCenter headers (category, port, health, etc.)
4. **Git** → Active git repository with branches and commit history
5. **Type** → Project type enum (software, book, custom) determining UI and defaults
6. **Visibility** → Tags, namespace, status badge, portfolio inclusion settings
7. **Health** → Health endpoint (if service) for monitoring
8. **Documentation** → `doc/index.html` for the portfolio and project detail

---

## References

- **Architecture Spec**: `ARCHITECTURE.md`
- **Database Schema**: `DATABASE.md`
- **Screen Specs**: `SCREEN-*.md` (Dashboard, Processes, Publisher, Monitoring, Workflow, Configuration)
- **Rules & Conventions**: `CLAUDE_RULES.md` (project layout, scripts, METADATA.md format)
