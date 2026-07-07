# Feature: Health Check

| Field       | Value |
|-------------|-------|
| Version     | 20260707 V1 |
| Description | Polls project health endpoints and merges local results with Marina heartbeat/event reporting. |
| Depends On  | FEATURE-REPORT-INGEST.md, FEATURE-SCANNER.md |
| Provides    | POST /api/health/poll |

**Description:** Combines local endpoint polling with Marina heartbeat/event state so the Monitoring
screens can show current and last-known project health.

## Trigger

- Monitoring Health refresh.
- Scheduler interval.
- Project operation start/finish.
- Remote heartbeat/event ingest through Marina.

## Sequence

1. Select projects with a health endpoint or latest Marina heartbeat.
2. Poll local HTTP health endpoints when reachable.
3. Read latest cloud/local heartbeat and event state.
4. Compute health: UP, WARN, DOWN, or UNKNOWN.
5. Record state changes as events.
6. Render the Monitoring Health table and event log.

## Reads

- `projects`.
- Health endpoints.
- Marina heartbeat/event records.

## Writes

- Local health cache.
- Marina events for state changes.

## Open Questions
- None.
