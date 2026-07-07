# Screen: Projects — Dashboard

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /projects/dashboard`, `GET /projects` |
| Parent | — |
| Main Menu | PROJECTS |
| Sub Menu | Dashboard · default |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Local projects discovered from PROJECTS_DIR and their published Marina state. |
| Description | Project list with status, conformance, catalog publish state, operations, links, and detail navigation. |
| Depends On | UI-GENERAL.md, FEATURE-SCANNER.md, FEATURE-SERVICE-CATALOG.md |
| Provides | GET /projects/dashboard, GET /projects |

## Header KPIs

Left column uses three `mn-hdr-count` blocks:

| Count | Source |
|-------|--------|
| Total | `projects` row count |
| Conformed | `projects.is_conformed = 1` |
| Published | `projects.is_published = 1` |

## Navigation

Top tabs: SETUP · PROJECTS · WORKFLOW · MONITORING. PROJECTS sub-tabs: Dashboard, Configuration, Validation, Maintenance.

## Layout

Full-width list. Action bar above table: search, status filter, namespace filter, `Rescan Projects`.

## Columns

| Column | Source | Interaction |
|--------|--------|-------------|
| Status | `projects.status` | Badge |
| Namespace | `projects.namespace` | Hidden when empty |
| Project | `projects.display_name`, `projects.name` | Link to `/projects/{id}` |
| Conformed | `projects.is_conformed` | Check / warning icon |
| Published | `projects.is_published`, `projects.published_at` | Check / warning icon |
| Operations | service catalog | Non-maintenance operation buttons |
| Links | project metadata links | Open in new tab |
| Detail | — | Cog icon -> `/projects/{id}` |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Rescan Projects | Button click | POST /api/projects/scan, reload table |
| Publish Project | Row action | POST /api/catalog/publish/{project}, update Published column |
| Run operation | Operation button | POST /api/projects/{project}/run/{operation}, show run state |
| Open detail | Project name or cog | GET /projects/{id} |

## Empty State

If PROJECTS_DIR is unset or empty, show a single `mn-card` explaining that setup is incomplete and link to `/setup/projects`.

## Open Questions
- None.
