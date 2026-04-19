# Feature: Batch Runner Service


| Field       | Value |
|-------------|-------|
| Provides    | POST /api/{project}/run/{script}, GET /api/runs/{run_id}, GET /api/runs/{run_id}/log, POST /api/runs/{run_id}/stop, GET /api/{project}/runs, POST /api/services/batch-runner/{tool} |
| Depends On  | FEATURE-SERVICE-CATALOG.md |
| Version     | (set version) |
| Description |  |

**Version:** 2026-04-06 V1
**Description:** Long-running script execution exposed as a platform service — wraps the process engine with a service interface

## Design Intent

GAME already has a process engine (`ops.py`/`spawn.py`) that launches bin/ scripts, captures logs, and tracks lifecycle. The Service Catalog API (FEATURE-SERVICE-CATALOG.md) already exposes this via REST with fire-and-poll. The Batch Runner service wraps this same engine with a service manifest (FEATURE-ServiceInterfaces.md) so it is available through all five transports: REST, CLI, MCP, async queue, and web UI.

**Why a separate service feature:** The existing process engine is internal plumbing. The Batch Runner is the user-facing service built on top of it. The distinction matters because:
- The service manifest describes what an agent or developer can do (run a script, check status, get logs)
- The process engine describes how it works internally (fork, log capture, SIGTERM)
- Other services (workflow, async queue) also use the process engine — Batch Runner is just one consumer

**The "needs a way to run scripts" requirement:** Every other service ultimately needs to execute work. The workflow service transitions state then fires a script. The async queue drains items by running handlers. Batch Runner is the primitive they all delegate to. It must be reliable, well-described, and available without the GAME web server being up for the CLI transport.

---

## Service Manifest

```yaml
name: batch-runner
description: Execute project scripts as background jobs with log capture and lifecycle management
version: 1.0.0

transports:
  rest: true
  cli: true
  mcp: true
  async: false

tools:
  - name: run_script
    description: >
      Launch a project bin/ script as a background job. Returns a run_id
      for tracking. The script runs in the project directory with its venv
      activated if present. stdout and stderr are captured to a log file.
    inputs:
      project:
        type: string
        required: true
        description: Project name slug (matches directory name)
      script:
        type: string
        required: true
        description: Script basename without bin/ prefix or extension (e.g. "deploy", "test")
      env:
        type: object
        required: false
        description: Additional environment variables to inject into the script
    output:
      run_id: { type: integer, description: "Unique run identifier for polling" }
      status: { type: string, description: "Initial status (running)" }
      log_path: { type: string, description: "Path to log file" }

  - name: run_status
    description: Check the current status of a running or completed job
    inputs:
      run_id:
        type: integer
        required: true
        description: Run identifier from run_script
    output:
      run_id: { type: integer }
      status: { type: string, enum: [running, done, error, stopped] }
      exit_code: { type: integer, nullable: true }
      started_at: { type: string }
      finished_at: { type: string, nullable: true }
      duration_seconds: { type: integer }

  - name: run_log
    description: Fetch log output from a running or completed job
    inputs:
      run_id:
        type: integer
        required: true
      tail:
        type: integer
        required: false
        description: Return only the last N lines (default returns full log)
    output:
      run_id: { type: integer }
      status: { type: string }
      log: { type: string, description: "Log content text" }
      line_count: { type: integer }

  - name: run_stop
    description: Cancel a running job by sending SIGTERM to its process group
    inputs:
      run_id:
        type: integer
        required: true
    output:
      run_id: { type: integer }
      status: { type: string, description: "New status (stopped)" }

  - name: list_runs
    description: List recent runs for a project, optionally filtered by script name
    inputs:
      project:
        type: string
        required: true
      script:
        type: string
        required: false
        description: Filter to runs of a specific script
      limit:
        type: integer
        required: false
        description: Maximum number of runs to return (default 20)
    output:
      runs:
        type: array
        items:
          run_id: integer
          script: string
          status: string
          started_at: string
          duration_seconds: integer
```

---

## Transport Details

### REST (existing, formalized)

Maps directly to existing FEATURE-SERVICE-CATALOG.md endpoints:

| Tool | Endpoint |
|------|----------|
| `run_script` | `POST /api/{project}/run/{script}` |
| `run_status` | `GET /api/runs/{run_id}` |
| `run_log` | `GET /api/runs/{run_id}/log` |
| `run_stop` | `POST /api/runs/{run_id}/stop` |
| `list_runs` | `GET /api/{project}/runs` (new) |

Also available via the generic service route: `POST /api/services/batch-runner/{tool}`

### CLI (via game-cli.sh)

Extends FEATURE-CLI-GATEWAY.md with service-aware commands:

```bash
game-cli batch-runner run_script --project=myapp --script=deploy
game-cli batch-runner run_status --run-id=42
game-cli batch-runner run_log --run-id=42 --tail=50
game-cli batch-runner run_stop --run-id=42
```

The existing shorthand commands (`game-cli run myapp deploy`) remain as aliases.

### MCP

When MCP transport is enabled, an MCP server wraps the Batch Runner tools. The agent calls:

```
tool: batch_runner_run_script
args: { project: "myapp", script: "deploy" }
```

The MCP server calls the GAME REST API internally (same as game-cli). It does not embed the process engine — it is a thin client.

---

## Implementation Notes

| Concern | Approach |
|---------|----------|
| No new process management code | All tools delegate to existing `ops.py` functions |
| Manifest file location | `GAME/services/batch-runner.service.yaml` |
| List runs endpoint | New route: `GET /api/{project}/runs` — simple SELECT from `op_runs` |
| MCP server | `GAME/mcp/batch_runner.py` — thin wrapper calling GAME REST API |

---

## Open Questions

- Should `run_script` accept a `timeout` override, or always use the operation's configured timeout? An override would be useful for ad-hoc runs where the default is too short.
- Should `list_runs` support filtering by status (e.g., only running jobs)? Useful for "show me what's active" queries.
- Should the MCP server for batch-runner be auto-started by GAME, or only started when the developer enables it in settings?
