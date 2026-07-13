# Screen: Projects — Dashboard

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Route | `GET /projects`, `GET /projects/dashboard` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | Dashboard · default |
| Tab Order | 1: Dashboard · 2: Workflow · 3: Configuration · 4: Validation · 5: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Organize, expose, and operate the projects Marina manages. |
| Description | Primary project registry with namespace/tag filters, lifecycle state, conformance, capabilities, and recent operations. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-ORGANIZATION.md, FEATURE-SCANNER.md, FEATURE-SERVICE-CATALOG.md |
| Provides | GET /projects, GET /projects/dashboard |

## Header KPIs

Total visible, Conformed, Running, and Attention Required. Counts follow the active namespace, tag, and
status filters.

## Layout

Action bar, active filter summary, and one row per registered project. The dashboard is the canonical
entry point for project management; setup screens hand projects to this registry after import.

## Filters

Search name/description, namespace, one or more tags, lifecycle status, conformance state, and source
(created locally, cloned, or imported). Filters are combinable and persist in the URL.

## Project Table

| Column | Source | Interaction |
|--------|--------|-------------|
| Project | display name and repository name | Open Detail |
| Namespace | project organization | Filter |
| Tags | project tags | Filter or edit from row |
| Lifecycle | project status | Filter; edit from row |
| Conformance | current standard result | Open Validation |
| Capabilities | service catalog count and exposure state | Open Detail |
| Health | latest local/cloud health | Open Monitoring |
| Last Activity | latest run/event timestamp | Open activity |
| Actions | project operations | Run an allow-listed operation |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Rescan | Button click | Reconcile local repositories and refresh organization/catalog projections |
| Create namespace | Filter/action menu | Add a user-defined namespace and optionally assign visible projects |
| Manage tags | Tag action | Create, rename, merge, or assign reusable tags |
| Run operation | Operation action | Start a controlled run and link it to Monitoring |
| Publish | Project action | Publish the project capability projection when AWS integration is configured |
| Open project | Name or row | GET `/projects/{id}` |

## Empty State

If no projects are registered, explain that projects are added from Setup → Repositories or by placing a
git repository under `PROJECTS_DIR`, then offer links to those screens.

## Open Questions

- None.
