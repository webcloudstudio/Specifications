# Screen: Projects — Configuration

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /projects/configuration` |
| Parent | — |
| Main Menu | PROJECTS |
| Sub Menu | Configuration |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Batch edit local project metadata without leaving the project list. |
| Description | Inline metadata editor for common project fields across all discovered projects. |
| Depends On | UI-GENERAL.md, FEATURE-SCANNER.md |
| Provides | GET /projects/configuration |

## Header KPIs

Left column uses one `mn-hdr-count`: `{N}` Projects.

## Layout

Full-width table with search and namespace filter. Each row is one project.

## Editable Fields

| Field | Source | Input |
|-------|--------|-------|
| Display Name | `projects.display_name` | Text |
| Status | `projects.status` | Select: IDEA / PROTOTYPE / ACTIVE / PRODUCTION / ARCHIVED |
| Namespace | `projects.namespace` | Text |
| Stack | `projects.stack` | Text |
| Short Description | `projects.short_description` | Text |
| Git Repo | `projects.git_repo` | Text |

Fields save on blur. Save writes the local SQLite row and patches the project's `METADATA.md`.

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Edit field | Blur / Enter | POST /api/projects/{id}/metadata, refresh cell |
| Open full editor | Cog click | GET /projects/{id} |
| Rescan metadata | Button click | POST /api/projects/scan, reload table |

## Guardrails

- Unknown `METADATA.md` keys are not discarded.
- Unknown keys appear on the detail screen as discovered fields.
- Failed file writes leave the SQLite row unchanged and show an error toast.

## Open Questions
- None.
