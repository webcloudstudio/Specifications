# Screen: Service Catalog

**Version:** 20260407 V3
**Description:** Simple flat list of all projects and prototypes with their endpoints grouped by type.

## Menu Navigation

`Catalog` — top-level tab ("Service / Catalog" two-line label). Single screen, no sub-bar.

## Route

```
GET /servicecatalog
```

## Layout

Single-column list. Action bar at top. One card per project/prototype below.

```
┌──────────────────────────────────────────────────────────┐
│  [🔍 Filter...]    [Projects ▼]    [Endpoint type ▼]     │
│  ──────────────────────────────────────────────────────  │
│                                                          │
│  MyApp  ·  My application short description              │
│  ─────────────────────────────────────────────────────   │
│  REST          GET /api/health                           │
│                POST /api/data                            │
│                POST /api/data/{id}                       │
│  Service       start  ·  stop                            │
│  Maintenance   backup  ·  cleanup  ·  rebuild            │
│  MCP           get_data  ·  run_analysis                 │
│                                                          │
│  CoreService  ·  Core platform service                   │
│  ─────────────────────────────────────────────────────   │
│  REST          GET /api/status                           │
│  Local         build  ·  test                            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Action Bar

| Control | Type | Behavior |
|---------|------|----------|
| Text filter | Input (`🔍 Filter…`) | Client-side substring match on project name, description, endpoint names. |
| Source filter | Dropdown | All / Projects / Prototypes |
| Endpoint type filter | Dropdown | All / REST / Service / Maintenance / Local / MCP |

All filters are client-side. No round-trip.

---

## Project / Prototype Card

One card per project (from scanner) and per prototype (from `SPECIFICATIONS_PATH`). Cards sorted alphabetically by display name. Projects and prototypes are interleaved in the same list.

### Card Header

One line only:

```
{display_name}  ·  {short_description}
```

- `display_name` — bold
- Separator `·` — muted
- `short_description` — normal weight, truncated at 100 chars

No status badge. No stack. No port. No AGENTS.md link.

### Endpoint Rows

Below the header, endpoints are grouped by type. Each type is a labeled row:

```
{Type}    {endpoint1}  ·  {endpoint2}  ·  ...
```

The type label is left-aligned in a fixed-width column (~120px). Endpoints listed inline, separated by `·`. Types with no endpoints for this project are omitted entirely.

**Endpoint types and their sources:**

| Type label | Source | What is listed |
|-----------|--------|----------------|
| `REST` | Project's route specifications (ARCHITECTURE.md route table, or `## Route` sections in SCREEN-*.md files) | HTTP method + path for each route, e.g. `GET /api/health`, `POST /api/items` |
| `Gateway` | Platform internal routes for calling this project's operations via the REST gateway | `POST /api/run/{project_id}/{op_name}` per operation; shown only when project has operations |
| `Service` | `bin/` scripts with `# Category: service` header | Script `# Name:` value (or filename stem) |
| `Maintenance` | `bin/` scripts with `# Category: maintenance` header | Script `# Name:` value (or filename stem) |
| `Local` | `bin/` scripts with `# Category: local` header | Script `# Name:` value (or filename stem) |
| `MCP` | `.mcp.json` tool list, or service manifest | Tool name |
| `{Other}` | `bin/` scripts with any other `# Category:` value | Script name; category label used verbatim |

If a project has no discoverable endpoints of any type, the card shows:

> *No endpoints discovered.*

in muted text below the header.

---

## Data Sources

### REST Endpoints

Server scans each project's linked specification directory for route definitions:
1. `ARCHITECTURE.md` — route table (rows matching `GET|POST|PUT|DELETE|PATCH` patterns)
2. `SCREEN-*.md` files — `## Route` sections

For projects without a linked specification directory, REST endpoints are not shown (no source of truth).

### Script Endpoints

Server reads `bin/` headers for each project. Parses:
- `# Category:` — determines type label
- `# Name:` — display name for the endpoint (fallback: filename stem)

### MCP Endpoints

Server reads `.mcp.json` (if present) for tool names. Falls back to service manifest if registered.

### Gateway Routes

Derived from the operations table for each project. One route per operation:
`POST /api/run/{project_id}/{op_name}`

---

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Filter | Type in search | Hides cards / endpoint rows not matching; real-time |
| Filter by source | Dropdown | Shows only projects or only prototypes |
| Filter by type | Dropdown | Shows only cards that have endpoints of that type |
| Copy endpoint | Click endpoint | Copies to clipboard; brief "Copied" tooltip |

No run buttons. No detail panel. No status controls. This screen is read-only reference.

---

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (display_name, short_description) | None |
| `operations` table (name, category per project) | None |
| Specification files (ARCHITECTURE.md, SCREEN-*.md, route parsing) | None |
| `bin/` script headers (Category, Name) | None |
| `.mcp.json` per project (tool list) | None |

---

## Open Questions

- Should REST endpoint discovery parse specification files server-side on page load, or be pre-computed by the scanner and stored in a `project_routes` table?
- Should clicking a REST endpoint open a simple "try it" panel (method + path + body textarea)?
