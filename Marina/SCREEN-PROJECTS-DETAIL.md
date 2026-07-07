# Screen: Projects — Detail

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /projects/{id}` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | — |
| Tab Order | — |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Project metadata, operations, publish state, and recent activity. |
| Description | Single-project view with editable metadata, operations, links, validation, and Marina catalog state. |
| Depends On | UI-GENERAL.md, FEATURE-SCANNER.md, FEATURE-SERVICE-CATALOG.md, FEATURE-PROJECT-OPS.md |
| Provides | GET /projects/{id} |

## Header KPIs

Left column uses status lights:

| Light | Source |
|-------|--------|
| Conformed | `projects.is_conformed` |
| Published | `projects.is_published` |

## Layout

Two columns. Left: identity and metadata. Right: operations, publish state, recent activity.

## Project Navigation

Header row provides Previous, Back to Dashboard, and Next buttons. Previous and Next follow the current dashboard sort order.

## Metadata Sections

| Section | Fields |
|---------|--------|
| Identity | name, display_name, short_description, status, namespace |
| Repository | path, git_repo, upstream remote, branch |
| Runtime | stack, health endpoint, port if present |
| Marina | is_conformed, is_published, published_at, catalog errors |
| Discovered Fields | Any `METADATA.md` keys not known to Marina |

Known fields save on blur. Discovered fields are shown with a warning style and remain editable without being discarded.

## Right Panels

| Panel | Content |
|-------|---------|
| Operations | All service catalog operations for the project |
| Validation | Last validation result and `Validate` action |
| Publish | `Publish to Catalog` action and last publish time |
| Recent Activity | Last 20 Marina events for the project |
| Links | Git repo, local docs, service catalog, logs |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Edit metadata | Blur / Enter | POST /api/projects/{id}/metadata |
| Validate | Button click | Queue `project-ops.validate` |
| Publish | Button click | POST /api/catalog/publish/{project} |
| Run operation | Button click | POST /api/projects/{project}/run/{operation} |
| View log | Run link | GET /monitoring/processes?run_id={run_id} |

## Open Questions
- None.
