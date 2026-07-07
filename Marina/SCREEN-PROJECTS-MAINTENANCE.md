# Screen: Projects — Maintenance

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /projects/maintenance` |
| Parent | — |
| Main Menu | PROJECTS |
| Sub Menu | Maintenance |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Run maintenance operations for local projects through Marina's controlled runner. |
| Description | Maintenance operation list for cleanup, rebuild, documentation, and other non-primary project actions. |
| Depends On | UI-GENERAL.md, FEATURE-BATCH-RUNNER.md, FEATURE-SERVICE-CATALOG.md |
| Provides | GET /projects/maintenance |

## Header KPIs

Left column uses two `mn-hdr-count` blocks: `{N}` Operations and `{N}` Running.

## Layout

Full-width table with search, project filter, and `Hide empty projects` toggle.

## Columns

| Column | Source | Interaction |
|--------|--------|-------------|
| Project | `projects.display_name` | Link to detail |
| Maintenance Operations | service catalog category `maintenance` | Operation buttons |
| Last Run | latest `op_runs` row | Link to log |
| Last Status | latest `op_runs.status` | Badge |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Run operation | Button click | POST /api/projects/{project}/run/{operation} |
| Stop running operation | Stop button | POST /api/runs/{run_id}/stop |
| View log | Last run link | GET /monitoring/processes?run_id={run_id} |

## Empty State

If no maintenance operations are discovered, show `No maintenance operations discovered.`

## Open Questions
- None.
