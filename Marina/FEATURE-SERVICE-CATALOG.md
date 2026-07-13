# Feature: Service Catalog Projection

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Description | Presents the current capability-discovery projection for project screens, operations, scheduling, and future publication. |
| Depends On | FEATURE-CAPABILITY-DISCOVERY.md, FEATURE-SCANNER.md, DATABASE.md |
| Provides | GET /api/service-catalog, GET /api/projects/{project}/capabilities, GET /api/projects/{project}/operations |

**Description:** The service catalog is a read model over `project_capabilities`. Discovery owns the
source contract; this feature owns query, filtering, grouping, and projection for Marina consumers.

## Trigger

- Project Explorer load.
- Project Detail load.
- Capability catalog load.
- Manual scan completion.
- Catalog publication request.

## Sequence

1. Read only current discovery records for registered projects.
2. Group records as Services, Data, Shared Resources, Operations, Endpoints, Links, and MCP Tools.
3. Include source evidence, validity, last-seen time, and discovery warnings.
4. Join current project identity, namespace, tags, git state, and health summary.
5. Return a stable projection for UI and API consumers.

## Project Catalog Response

```json
{
  "project": {
    "name": "market",
    "display_name": "Market Downloader",
    "remote_url": "https://github.com/acme/market.git",
    "current_branch": "main",
    "working_tree_status": "CLEAN"
  },
  "capabilities": {
    "operations": [
      {
        "key": "bin/test.sh",
        "name": "Test",
        "category": "Operations",
        "description": "Run project tests",
        "type": "batch",
        "args": [],
        "source_path": "bin/test.sh",
        "valid": true
      }
    ],
    "endpoints": [],
    "services": [],
    "data": [],
    "shared_resources": [],
    "mcp_tools": []
  },
  "warnings": [],
  "discovery": {"last_run_at": "2026-07-13T12:00:00Z"}
}
```

## Filters

Support project, namespace, tag, capability kind, category, transport, validity, source path, and text
search. Default views show current valid records and a visible warning count; invalid and historical
records are available through an explicit filter.

## Reads

- `projects` and organization tables.
- Current `project_capabilities` and `project_discovery_warnings`.
- Latest health and activity summaries when requested.

## Writes

- None. Discovery and registration own writes.

## Initial-Build Boundary

- Catalog listing is included.
- Script content viewing may be included as a source-evidence action.
- Capability invocation, exposure approval, and remote publication are not required for the initial build.
- A discovered operation with invalid headers is displayed but cannot be run by Marina.

## Open Questions

- None.
