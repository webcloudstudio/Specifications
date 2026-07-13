# Screen: Projects — Dashboard

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Route | `GET /projects`, `GET /projects/dashboard` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | Dashboard · default |
| Tab Order | 1: Dashboard · 2: Capabilities · 3: Workflow · 4: Configuration · 5: Validation · 6: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Organize, expose, and operate the projects Marina manages. |
| Description | Primary project registry with namespace/tag filters, lifecycle state, conformance, capabilities, and recent operations. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-REGISTRATION.md, FEATURE-PROJECT-ORGANIZATION.md, FEATURE-SCANNER.md, FEATURE-SERVICE-CATALOG.md |
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
| Registration | Managed / discovered / conflict | Open registration review |
| Source | local / cloned / imported and remote owner | Filter |
| Namespace | project organization | Filter |
| Tags | project tags | Filter or edit from row |
| Lifecycle | project status | Filter; edit from row |
| Conformance | current standard result | Open Validation |
| Capabilities | service catalog count and exposure state | Open Detail |
| Health | latest local/cloud health | Open Monitoring |
| Last Activity | latest run/event timestamp | Open activity |
| Actions | registration, detail, and discovery actions | Review or rediscover; invocation is deferred |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Rescan | Button click | Reconcile local repositories and refresh organization/catalog projections |
| Create namespace | Filter/action menu | Add a user-defined namespace and optionally assign visible projects |
| Manage tags | Tag action | Create, rename, merge, or assign reusable tags |
| Rediscover | Project action | Refresh repository identity and capability discovery |
| Publish | Project action | Publish the project capability projection when AWS integration is configured |
| Open project | Name or row | GET `/projects/{id}` |

## Empty State

If no projects are registered, explain that repositories are added from Setup → Repositories or
discovered from `PROJECTS_DIR`, then offer links to registration. Show discovered-but-unregistered
repositories in a separate callout so they are not mistaken for managed projects.

## Open Questions

- None.
