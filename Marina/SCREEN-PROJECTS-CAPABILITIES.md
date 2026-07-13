# Screen: Projects — Capabilities

| Field | Value |
|-------|-------|
| Version | 20260713 V1 |
| Route | `GET /projects/capabilities` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | Capabilities |
| Tab Order | 1: Dashboard · 2: Capabilities · 3: Workflow · 4: Configuration · 5: Validation · 6: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Explore the services, data, resources, and operations discovered from managed repositories. |
| Description | Cross-project capability explorer backed by the current discovery projection. |
| Depends On | UI-GENERAL.md, FEATURE-SERVICE-CATALOG.md, FEATURE-CAPABILITY-DISCOVERY.md |
| Provides | GET /projects/capabilities |

## Header KPIs

Projects, Capabilities, Operations, and Warnings. Counts follow the active filters.

## Layout

Filter bar followed by a grouped capability table. The default group is project; alternate grouping is
capability kind or category.

## Filters

Project, namespace, tags, kind, category, transport, valid/invalid, and search across name, description,
source path, and endpoint path.

## Capability Table

| Column | Content |
|--------|---------|
| Project | Project name, namespace, and lifecycle |
| Capability | Display name and stable key |
| Kind | Service, data, shared resource, operation, endpoint, or MCP tool |
| Category | Operations, Workflow, Global, or documented |
| Transport | Local process, HTTP, MCP, or documentation |
| Description | Discovered description |
| Evidence | Source path and locator |
| State | Valid, warning, invalid, or stale |
| Last Seen | Discovery timestamp |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Open project | Project link | GET `/projects/{id}` |
| Open evidence | Source action | Show the declaring file, header/section, and parsed fields |
| Filter warning | Warning badge | Limit view to the affected discovery records |
| Rediscover | Button click | POST `/api/projects/scan`; refresh projection |
| Copy identifier | Capability key click | Copy stable project/capability identifier |

## Initial-Build Boundary

This screen catalogs and explains discovered capabilities. It does not execute operations or expose them
to other users. Invocation and exposure are later features consuming this same projection.

## Open Questions

- None.
