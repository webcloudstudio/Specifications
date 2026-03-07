# Routes & API Reference

All routes defined in `routes.py` as a Flask Blueprint (`bp = Blueprint('cc', ...)`).

## Context Processor (every request)

`inject_globals()` runs before every template render:
1. Calls `ops.cleanup_dead_processes()` to mark dead PIDs as 'done'
2. Injects into all templates:
   - `running_ops_count` — count of running projects
   - `running_projects` — list of `{id, title, run_id, op_id, op_name}`
   - `PROJECT_TYPES` — from models.py registry
   - `workflow_states` — from workflow.json or defaults
   - `workflow_map` — `{key: state}` dict
   - `app_name` — from config

## Workflow States

Loaded from `workflow.json` (if exists) or defaults:
```json
[
  {"key": "todo",       "label": "TODO",       "color": "#fdab3d"},
  {"key": "developing", "label": "DEVELOPING",  "color": "#0073ea"},
  {"key": "good",       "label": "GOOD",        "color": "#00c875"}
]
```

## Page Routes

### `GET /` — Projects List
- Loads all projects, enriches with `_prepare_row_project()` (operations, workflow, links, etc.)
- Sorts by `?sort=name|status_asc|status_desc`
- Renders `list.html` with type-specific row templates per project

### `GET /project-config` — Configuration Page
- Same data as project list, sorted by title
- Renders `project_config.html` with editor rows

### `GET /project/<id>` — Project Detail
- Loads single project with operations, unpushed count, endpoints, bookmarks
- Identifies server operations for live log viewer
- Renders type-specific detail template (e.g. `types/_software_detail.html`)

### `POST /project/<id>` — Update Project (form submit)
- Updates title, description, extra fields (tech_stack, port, remote_url, etc.)
- Updates card_* fields for homepage
- Redirects back to detail page

### `GET /publish` — GIT-Homepage Page
- Shows rebuild/preview/push pipeline buttons with running status
- Lists all projects with card metadata in contents table
- Sidebar form for editing selected project's card details
- Renders `publish.html`

### `GET /processes` — Process Monitor
- Lists running processes with PID, elapsed time, stop/log buttons
- Lists completed processes with status, log buttons
- Auto-refreshes while processes are running
- Renders `processes.html`

### `GET /settings` — Application Settings
- Form: app name, homepage URL
- Saves to Flask config (in-memory, not persisted to file)

### `GET /tags` — Tag Color Management
- Lists all tags with color assignments
- Add/update/delete forms
- Colors stored in `data/tag_colors.json`

### `GET /usage` — Usage Analytics
- Accepts `?days=7|14|30`
- Calls `usage_analyzer.generate_report()`
- Renders interactive Plotly charts in `usage.html`

### `GET /help` — Help Page
- Static accordion-based documentation of features

## API Routes (HTMX)

### Project Inline Editing
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/sync` | Re-run scanner, return sync count HTML |
| `POST` | `/api/stub-conventions` | Create stub CLAUDE.md files for all projects |
| `GET/POST` | `/api/project/<id>/edit-title` | Inline title edit form / save |
| `GET/POST` | `/api/project/<id>/edit-port` | Inline port edit form / save |
| `POST` | `/api/project/<id>/update` | Update single field (via `field` form param) |
| `POST` | `/api/project/<id>/update/workflow` | Update workflow status |
| `POST` | `/api/project/<id>/quick-edit` | Save workflow + project type, return updated row |
| `GET` | `/api/project/<id>/edit-row` | Return edit-mode row HTML |
| `GET` | `/api/project/<id>/row` | Return normal row HTML (cancel edit) |
| `GET` | `/api/project/<id>/git-status` | Return unpushed count badge HTML |
| `GET` | `/api/project/<id>/claude-content` | Return CLAUDE.md content for modal |

### Field Update (`/api/project/<id>/update`)

Accepts `field` form parameter to determine which field to update:
- `title`, `description` — Direct column update
- `workflow` — Stored in extra JSON
- `project_type` — Direct column update
- `tech_stack`, `port`, `remote_url`, `railway_id`, `website_url` — Stored in extra JSON
- `card_show` — Checkbox toggle (checked = present in form data)
- `card_title`, `card_type`, `card_desc`, `card_url`, `card_tags` — Direct column update

Returns 204 No Content on success.

### Operations
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/op/<id>/run` | Execute operation, return Stop button (server) or output modal (one-shot) |
| `POST` | `/api/op/<id>/stop` | Kill running operation, return Start button |
| `GET` | `/api/op/<id>/logs` | Return log viewer HTML (last 500 lines, auto-scrolled) |

### Run Operation Response Patterns

**Server started:** Returns Stop button HTML
```html
<button class="op-btn op-btn--danger" hx-post="/api/op/{id}/stop" hx-swap="outerHTML">Stop</button>
```

**One-shot completed:** Returns original button + output in modal via OOB swap
```html
<button class="op-btn op-btn--local" hx-post="/api/op/{id}/run" hx-swap="outerHTML">{name}</button>
<pre id="op-output-body" hx-swap-oob="innerHTML">{escaped output}</pre>
```
Plus `HX-Trigger: showOpModal` header to open the output modal.

### Publish Pipeline
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/publish/rebuild` | Start rebuild via spawn service |
| `POST` | `/publish/push` | Start push via spawn service |
| `POST` | `/publish/stop` | Stop rebuild or push (`target` form param) |
| `POST` | `/publish/preview/start` | Start preview server |
| `POST` | `/publish/preview/stop` | Stop preview server |
| `POST` | `/api/project/<id>/toggle-publish` | Toggle card_show flag |
| `GET` | `/publish/edit/<id>` | Publication metadata edit form |
| `POST` | `/publish/edit/<id>` | Save publication metadata |

### Process Monitor
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/processes/running` | JSON list of running processes |
| `GET` | `/api/processes/log/<id>` | Plain text log file contents |
| `POST` | `/api/processes/<id>/stop` | Stop process, redirect to processes page |

### Tags
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/tag/add` | Add new tag with color |
| `POST` | `/api/tag/update` | Update tag name and/or color |
| `POST` | `/api/tag/delete` | Delete tag |

### Settings
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/settings/save` | Save app name and homepage URL |

### Register Project (API)
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/register-project` | Register project via JSON API (used by /init skill) |

Accepts JSON: `{name, path, project_type, tech_stack, port, description}`
Returns: `{ok: true, project_id: int, created: bool}`
