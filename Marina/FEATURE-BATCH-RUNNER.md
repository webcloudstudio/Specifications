# Feature: Batch Runner

| Field       | Value |
|-------------|-------|
| Version     | 20260707 V1 |
| Description | Controlled local runner for project operations with run state, logs, stop control, and schedule integration. |
| Depends On  | FEATURE-SERVICE-CATALOG.md, FEATURE-REPORT-INGEST.md |
| Provides    | POST /api/projects/{project}/run/{operation}, GET /api/runs/{run_id}, POST /api/runs/{run_id}/stop |

**Description:** Runs allow-listed local project operations, captures logs, tracks run state, and reports
terminal outcomes into Marina events.

## Trigger

- Project Dashboard operation button.
- Project Maintenance operation button.
- Scheduler fire.
- Project Ops queue drain.

## Sequence

1. Resolve project and operation from the service catalog.
2. Reject unknown operations or paths outside the project directory.
3. Start the process in a controlled process group.
4. Capture stdout/stderr to a run log.
5. Track state: STARTING, RUNNING, DONE, ERROR, STOPPED.
6. Emit Marina events on start and terminal state.

## Reads

- Service catalog operation definition.
- Project path.
- Run log files.

## Writes

- Run state cache.
- Log files.
- Marina events.

## Open Questions
- None.
