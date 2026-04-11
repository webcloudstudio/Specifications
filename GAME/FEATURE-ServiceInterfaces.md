# Feature: Service Interfaces

**Version:** 2026-04-06 V1
**Description:** Unified service descriptor framework — MCP-shaped metadata for transport-agnostic service discovery and consumption

## Design Intent

The platform needs a single way to describe, discover, and consume services regardless of how they are delivered. Today GAME exposes capabilities through REST endpoints, bash scripts (CLI), and the web UI. Adding MCP and async queues creates five transports for the same underlying capabilities. Without a unifying descriptor, each transport is a silo.

**The core idea:** every service is described using an MCP-shaped manifest — name, description, and typed tool definitions — but the service does NOT speak the MCP protocol unless it is an actual MCP server. The manifest is a **metadata format**, not a transport. GAME reads these manifests to populate the Service Catalog, generate CLI wrappers, expose REST endpoints, and optionally start real MCP servers.

**Why MCP-shaped:** MCP already solved the "how do you describe a tool so an AI agent can call it" problem. By adopting the same shape (name, description, input schema, output schema) for ALL services — not just MCP ones — we get a uniform interface that works for humans (Service Catalog UI), scripts (CLI gateway), agents (MCP or REST), and async consumers (queue). Developers learn one descriptor format. Claude reads one format. The platform renders one format.

**What this enables:**
- A developer writes a service manifest once. GAME exposes it via whichever transports are enabled.
- Projects declare service dependencies in `services.yaml`. `common.py` reads this config and dispatches calls to the correct transport without the application knowing how the service is hosted.
- Swapping implementations (e.g., platform logging vs. external logging) is a config change, not a code change.
- The same descriptor that tells Claude what tools are available also tells the application code at runtime how to call them. One source of truth for both build-time (agent) and run-time (application).

**What this is NOT:** This is not a mandate that all services speak MCP protocol. stdio MCP is one transport option. Most platform services will be consumed via REST or CLI. The descriptor format is borrowed from MCP because it is a good format, not because everything must be an MCP server.

---

## Service Manifest Format

Each service is described by a manifest file: `services/{service-name}.service.yaml`

```yaml
name: batch-runner
description: Execute project scripts as background jobs with log capture and lifecycle management
version: 1.0.0

transports:
  rest: true          # Exposed via GAME REST API
  cli: true           # Accessible via game-cli.sh
  mcp: false          # Not an MCP server (unless developer enables it)
  async: false        # Not queue-backed

tools:
  - name: run_script
    description: Launch a project script as a background job
    inputs:
      project:
        type: string
        required: true
        description: Project name slug
      script:
        type: string
        required: true
        description: Script basename (no bin/, no extension)
      env:
        type: object
        required: false
        description: Environment variables to inject
    output:
      run_id: integer
      status: string
      poll_url: string

  - name: run_status
    description: Check if a job is still running
    inputs:
      run_id:
        type: integer
        required: true
    output:
      status: string
      exit_code: integer
      duration: integer
```

---

## Transport Mapping

Each transport maps the same tool definition to its native invocation pattern:

| Transport | How a tool is called | Response format |
|-----------|---------------------|-----------------|
| **REST** | `POST /api/services/{service}/{tool}` with JSON body matching `inputs` | JSON matching `output` |
| **CLI** | `game-cli {service} {tool} --project=X --script=Y` | Printed text or `--json` for structured output |
| **MCP** | Agent calls tool via stdio MCP protocol (tool name = `{service}_{tool}`) | MCP tool response |
| **Async** | Message written to `data/queues/{service}.queue.jsonl` with `tool` and `inputs` fields | Result written to `data/queues/{service}.results.jsonl` |
| **Web UI** | Button/form on Service Catalog screen triggers REST call | HTMX fragment update |

The platform generates the REST routes and CLI commands automatically from the manifest. MCP servers are only started when `mcp: true` and the developer has enabled MCP hosting for that service.

---

## Service Registry

GAME maintains a service registry in the `services` database table (see below). On startup, GAME scans:

1. **Platform services** — manifests in `services/*.service.yaml` within the GAME project
2. **Project services** — manifests in `{project}/services/*.service.yaml` for each managed project
3. **MCP servers** — registered MCP server configurations (see FEATURE-MCP-Hosting.md)

The Service Catalog screen (SCREEN-CATALOG.md) displays all registered services grouped by source (platform vs. project).

---

## Project Service Consumption

Projects declare which platform services they use in `services.yaml` at the project root:

```yaml
services:
  batch-runner: game_platform
  workflow: game_platform
  async-queue: game_platform
```

Values: `game_platform` (call GAME's REST API), `disabled` (no-op), or a custom URL for external implementations.

`common.py` (distributed to all projects) includes a `ServiceClient` class that reads `services.yaml` and provides a Python API:

```python
from common import services

# Calls GAME REST API under the hood
run = services.batch_runner.run_script(project="myapp", script="deploy")
status = services.batch_runner.run_status(run_id=run["run_id"])
```

The client resolves the GAME URL using the same logic as `game-cli.sh` (GAME_URL > GAME_PORT > ~/.game_port > localhost:5000).

---

## New Database Table: `services`

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| name | TEXT UNIQUE | — | Service name slug (e.g. `batch-runner`) |
| display_name | TEXT | — | Human-readable name |
| description | TEXT | — | One-line description from manifest |
| source | TEXT | — | `platform` / `project:{name}` / `mcp:{name}` |
| source_project_id | INTEGER FK | NULL | References projects.id if source is a project |
| manifest_path | TEXT | — | Path to the .service.yaml file |
| transports | TEXT | '{}' | JSON: which transports are enabled |
| tool_count | INTEGER | 0 | Number of tools defined |
| version | TEXT | NULL | Service version from manifest |
| is_active | INTEGER | 1 | 0 if removed from disk |
| created_at | TEXT | datetime('now') | First discovery |
| updated_at | TEXT | datetime('now') | Last scan |

### `service_tools`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| service_id | INTEGER FK | References services.id |
| name | TEXT | Tool name |
| description | TEXT | Tool description (shown to agents and in UI) |
| input_schema | TEXT | JSON schema for inputs |
| output_schema | TEXT | JSON schema for outputs |
| sort_order | INTEGER | Display order |

---

## CLAUDE_RULES Integration

When a project is built or updated, the platform services available to it are listed in a `## Platform Services` section injected into AGENTS.md alongside the CLAUDE_RULES block. This tells the AI agent what services exist and how to call them:

```markdown
## Platform Services

The following services are available via the platform client (`common.py`):

- **batch-runner** — Execute project scripts as background jobs
  - `services.batch_runner.run_script(project, script)` → `{run_id, status}`
  - `services.batch_runner.run_status(run_id)` → `{status, exit_code}`
- **workflow** — Generic state machine for task lifecycle
  - `services.workflow.create(workflow_name, workflow_type, payload)` → `{workflow_id}`
  - `services.workflow.transition(workflow_id, to_state)` → `{new_state}`
```

This section is generated from the service manifests. The agent reads it and knows how to wire up service calls in application code. Same descriptor, different audience.

---

## New Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/services` | List all registered services with their tools |
| GET | `/api/services/{name}` | Get one service manifest with full tool definitions |
| POST | `/api/services/{name}/{tool}` | Invoke a service tool (generic dispatch) |

These complement — not replace — the existing `/api/catalog` and `/api/{name}/run/{script}` endpoints. The service routes provide the generic interface; existing endpoints remain as shortcuts.

---

## Open Questions

- Should service manifests support a `health` field (endpoint to check if the service is operational)? Useful for the monitoring screen to show service health alongside project health.
- Should `common.py` ServiceClient support async (non-blocking) calls natively, or should async always go through the queue transport?
- Should the generic `/api/services/{name}/{tool}` route replace the existing per-feature routes over time, or should both coexist permanently?
