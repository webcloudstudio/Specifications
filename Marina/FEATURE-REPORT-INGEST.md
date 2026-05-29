# Feature: Report Ingest

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | Heartbeat and event ingestion plus per-project health aggregation, so project state is reportable 24x7 even when the source machine is off. |
| Depends On  | FEATURE-MARINA-LIB.md, FEATURE-ACCESS-CONTROL.md |
| Provides    | POST /heartbeat, POST /events, GET /health/{project} |

**Description:** Projects and remote jobs report operational state to the cloud; the catalog then answers
"what is the last-known health of project X" 24×7 without scraping any machine.

## Trigger

- A conformed project's `bin/` script calls `mar.report.heartbeat(state, message)` at start/finish and
  `mar.report.event(severity, message)` on notable events. Both are best-effort (never crash the job).
- A member calls `mar.report` read or `GET /health/{project}` to see last-known health.

## Sequence

**Ingest (`POST /heartbeat`, `POST /events`):**

1. `report_ingest` Lambda reads the principal, resolves the `project` (from body, matched to a known
   project), and calls `authz.gate(principal, org, project, "readwrite")`.
2. Heartbeat → upsert `PK=ORG#{org}, SK=PROJECT#{project}#HB#{program}` with `state`, `message`,
   `updated_at` (DATABASE.md pattern 7) — latest-only per program.
3. Event → put `PK=ORG#{org}, SK=PROJECT#{project}#EVT#{ulid}` (pattern 8), append-only; a DynamoDB TTL
   attribute expires events after the configured window.
4. Always returns 200; the library swallows transport errors so reporting never breaks the caller.

**Health read (`GET /health/{project}`):**

1. Gate checks read access.
2. Query latest heartbeats (pattern 9) and recent events (pattern 10).
3. Compute aggregate: all `OK` → `healthy`; any `ERROR`/`CRITICAL` → `degraded`; none → `unknown`.
4. Return `{project, aggregate, heartbeats[], recent_events[], checked_at}`.

## Reads

- DynamoDB heartbeat/event items (patterns 9, 10).
- ACL via the access-control gate.

## Writes

- DynamoDB heartbeat (upsert) and event (append, TTL-bounded) items via `marina.report`.

## Test

- **Script:** `bin/test_report_ingest.sh` → posts an `OK` then an `ERROR` heartbeat for program `daily`
  and an event; asserts `GET /health/{project}` returns `degraded` with the latest heartbeat and the
  event present.
- **Pass criteria:** latest-only heartbeat semantics hold; events append and carry a TTL; aggregate
  computed correctly; ingest returns 200 even when the caller lacks the project (logged, not errored —
  matches best-effort contract) — except a hard 403 when the principal is known-but-unauthorised.
- **CloudWatch:** `report_ingest` log group shows `{"event":"heartbeat","project":...,"state":...}` and
  `{"event":"event_ingest",...}`; these log lines are the primary screen-less verification surface.

## Open Questions

- Event TTL window: 30 days default — confirm. Too short loses debugging history; too long grows item
  count and read cost.
- Should a degraded transition also enqueue an alert message to SQS (Phase 2) for downstream
  notification, or is read-on-demand health sufficient for now? Read-on-demand for Phase 1.
