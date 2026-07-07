# Feature: Service Catalog

| Field       | Value |
|-------------|-------|
| Version     | 20260707 V1 |
| Description | Discovers each local project's callable surface area for screens, operations, scheduling, and catalog publish. |
| Depends On  | FEATURE-SCANNER.md, DATABASE.md |
| Provides    | GET /api/service-catalog, GET /api/projects/{project}/operations |

**Description:** Builds the local callable-surface map that Projects, Monitoring, Scheduler, and Catalog
Publish use to know what each project exposes.

## Trigger

- Startup scan.
- Manual project rescan.
- Project detail load when cached data is stale.

## Sequence

1. For each discovered project, read `AGENTS.md`, `METADATA.md`, and eligible `bin/` script headers.
2. Register operations, links, endpoints, schedules, and capability metadata.
3. Classify operations as primary, maintenance, scheduled, or workflow-facing.
4. Provide the operation list to Projects, Monitoring, Scheduler, and Catalog Publish.

## Reads

- `projects.path`.
- Project `AGENTS.md`.
- Project `METADATA.md`.
- Project `bin/` script headers.

## Writes

- Local service catalog cache.
- `platform_stats.catalog_last_published` when publish succeeds.

## Open Questions
- None.
