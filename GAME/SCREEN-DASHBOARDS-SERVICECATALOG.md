# Screen: Service Catalog

**Version:** 20260407 V4
**Description:** Surface area reference for every project and prototype. Shows all callable endpoints grouped by type — scripts, links, REST routes, and MCP tools. Read-only reference with script viewer.

## Menu Navigation

`Catalog` — top-level tab ("Service / Catalog" two-line label). Single screen, no sub-bar.

## Route

```
GET /servicecatalog
```

---

## What the Catalog Tracks

For each project (discovered via `PROJECTS_DIR`) and each prototype (discovered via `SPECIFICATIONS_PATH`), the platform maps its complete callable surface area at startup:

| Surface type | Source | Stored as |
|-------------|--------|-----------|
| **Operations scripts** | `bin/*.sh` / `bin/*.py` with `# Category: Operations` | `operations` table |
| **Workflow scripts** | `bin/*.sh` / `bin/*.py` with `# Category: Workflow` | `operations` table |
| **Global scripts** | `bin/*.sh` / `bin/*.py` with `# Category: Global` | `operations` table |
| **Links** | `METADATA.md → ## Links` table | `extra.links` JSON |
| **REST endpoints** | `AGENTS.md → ## Endpoints` table | `extra.endpoints` JSON |
| **MCP tools** | `mcp/*.service.yaml` or `.mcp.json` | `service_tools` table |

All sources are read during the startup scan and on every rescan. Page rendering reads the database only — no file I/O at display time.

### REST Endpoints Standard (AGENTS.md)

Each project documents its REST API in AGENTS.md under a standard `## Endpoints` section:

```markdown
## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET    | /health           | Health check |
| POST   | /api/items        | Create item  |
| GET    | /api/items/{id}   | Get item     |
```

The scanner parses this table and stores the rows in `extra.endpoints`. Projects without an `## Endpoints` section show no REST rows in the catalog. The section is optional — omit it when the project has no HTTP API.

### Script Run Endpoints (Gateway)

Every registered script is also callable via the platform REST gateway:

```
POST /api/{project_name}/run/{script_stem}
```

Examples:
- `POST /api/conquer_2026/run/start` → runs `bin/start.sh` in the conquer_2026 project
- `POST /api/ezdocs/run/photo_scan` → runs `bin/photo_scan.sh` in ezdocs

These gateway routes are derived at runtime from the `operations` table — no AGENTS.md entry needed.

---

## Layout

Single-column list. Action bar at top. One card per project/prototype below, sorted alphabetically.

```
┌──────────────────────────────────────────────────────────┐
│  [🔍 Filter...]   [All Sources ▼]   [All Types ▼]        │
│  ──────────────────────────────────────────────────────  │
│                                                          │
│  Conquer 2026  ·  2026 strategy game                     │
│  ─────────────────────────────────────────────────────   │
│  [▶ Start]  [■ Stop]  [⚙ Build]  [🧪 Test]               │  ← Operations buttons
│  [→ Scorecard]  [→ Photo Scan]                           │  ← Workflow buttons
│  Links    GitHub →  ·  Live Site →                       │
│  REST     GET /health  ·  POST /api/game/move            │
│  MCP      get_state  ·  make_move  ·  list_players       │
│                                                          │
│  ezdocs  ·  Document and photo management                │
│  ─────────────────────────────────────────────────────   │
│  [▶ Start]  [■ Stop]  [⚙ Build]                          │  ← Operations
│  [→ Photo Analyze]  [→ Photo Dedup]  [→ Photo Scan]      │  ← Workflow
│  Links    Docs →                                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Action Bar

| Control | Type | Behavior |
|---------|------|----------|
| Text filter | Input (`🔍 Filter…`) | Client-side substring match on project name, description, script names, endpoint paths. |
| Source filter | Dropdown | All / Projects / Prototypes |
| Type filter | Dropdown | All / Operations / Workflow / Global / Links / REST / MCP |

All filters are client-side.

---

## Card Layout

### Header

One line:

```
{display_name}  ·  {short_description}
```

`display_name` bold. Separator `·` muted. `short_description` normal weight, truncated at 100 chars.

No status badge. No stack. No port.

### Script Buttons (Operations, Workflow, Global)

Scripts are rendered as **buttons**, not text labels. Button style per category — see UI-GENERAL Category Button Styles.

All three categories appear on the same card, in separate rows if multiple categories are present. Row order: Operations first, then Workflow, then Global.

Each button label is the script's `# Name:` header value (fallback: filename stem without extension).

**Clicking a script button:** Opens the Script Viewer modal — see Script Viewer below.

> Run actions are NOT on this screen. The Service Catalog is a reference view. To run a script, use the Dashboard or call `POST /api/{name}/run/{script}` directly.

### Links Row

If the project has entries in `extra.links` (from `METADATA.md → ## Links`):

```
Links    GitHub →  ·  Live Site →  ·  Docs →
```

Each link is a small anchor tag opening in a new tab. No label prefix needed — the link label comes from the `## Links` table.

### REST Row

If the project has entries in `extra.endpoints` (from `AGENTS.md → ## Endpoints`):

```
REST     GET /health  ·  POST /api/items  ·  GET /api/items/{id}
```

Each entry shows `METHOD /path`. Clicking an entry copies it to clipboard with a brief "Copied" tooltip.

### MCP Row

If the project has MCP tools registered in `service_tools`:

```
MCP      tool_name  ·  another_tool  ·  third_tool
```

Each tool name is shown. Clicking copies the tool name to clipboard.

### Empty State

If a project has no surface area of any type:

> *No endpoints discovered. Add `# CommandCenter Operation` headers to bin/ scripts, or add an `## Endpoints` section to AGENTS.md.*

---

## Script Viewer Modal

Clicking any script button opens a modal showing the full script content.

```
┌─────────────────────────────────────────────────────────┐
│  start.sh — Start Server                          [×]   │
│  Category: Operations  ·  conquer_2026                  │
│  ─────────────────────────────────────────────────────  │
│  #!/bin/bash                                            │
│  # CommandCenter Operation                              │
│  # Name: Start Server                                   │
│  # Category: Operations                                 │
│  source "$(cd "$(dirname "$0")" && pwd)/common.sh"      │
│  ...                                                    │
│  ─────────────────────────────────────────────────────  │
│  Gateway endpoint:  POST /api/conquer_2026/run/start    │
│                                        [Copy endpoint]  │
└─────────────────────────────────────────────────────────┘
```

| Element | Content |
|---------|---------|
| Title | `{filename} — {# Name:}` |
| Subtitle | `Category: {category}  ·  {project display_name}` |
| Body | Full script content in a monospace scrollable code block. Syntax highlighted (Bash or Python). |
| Footer | Gateway endpoint: `POST /api/{project_name}/run/{script_stem}` + `[Copy endpoint]` button |

Modal fetched via `GET /api/{project_name}/script/{script_stem}` which returns `{ "filename": "start.sh", "content": "...", "name": "Start Server", "category": "Operations", "run_endpoint": "POST /api/..." }`.

Modal is dismissable by clicking ×, clicking outside, or pressing Escape.

---

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (display_name, short_description) | None — read-only screen |
| `operations` table (name, category, cmd per project) | |
| `extra.links` (from `projects.extra` JSON) | |
| `extra.endpoints` (from `projects.extra` JSON) | |
| `service_tools` table (MCP tool names) | |
| Script file content (on demand, for modal only) | |

---

## Startup Scan Integration

The catalog is fully populated at server startup via `scanner.py`. No additional scan steps needed. Page rendering reads only from the database.

Rescan (Rescan button on Dashboard, or server restart) refreshes all surface area data including new scripts, updated links, and modified `## Endpoints` tables.

---

## Open Questions

- Should the Script Viewer modal support a "Run" button (fire the script via the gateway endpoint) for Operations and Workflow scripts?
- Should REST endpoints be click-to-try (open a simple form with method + path + body) rather than click-to-copy?
- Should Global scripts show a warning in the modal: "This script modifies other repositories"?
