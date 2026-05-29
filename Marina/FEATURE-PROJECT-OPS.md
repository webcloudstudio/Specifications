# Feature: Project Operations

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | Expose Prototyper's project-conformance scripts (Validate, Update, Initialize, Document) as a queue-dispatched local capability, so a member can conform a project from anywhere and see the result in CloudWatch. |
| Depends On  | FEATURE-ASYNCQUEUE.md, FEATURE-REPORT-INGEST.md, FEATURE-ACCESS-CONTROL.md, FEATURE-MARINA-LIB.md |
| Provides    | — |

**Description:** Prototyper holds the code that makes a project conform to platform standards —
`bin/ProjectValidate.sh`, `bin/ProjectUpdate.sh`, `bin/ProjectInitialize.sh`, `bin/ProjectDocument.sh`.
Prototyper runs on the **same box** as the local Marina agent, so these are exposed as a local-plane
capability dispatched through the **existing AsyncQueue** — not a new cloud endpoint. A member submits a
conformance job from anywhere (24×7); the local agent drains it, shells out to the matching Prototyper
script, and reports the exit code and output as a Marina event. There is no public inbound path and no
new cloud surface — the cloud only carries the job request and the result report.

## Trigger

- **Submit:** `mar.queue.submit(queue="project-ops", service="prototyper", tool="<op>",
  payload={"project": "<name>", "args": [...]})` → `POST /queue/project-ops` (reuses ASYNCQUEUE).
  `<op>` is one of a fixed allow-list: `validate`, `update`, `initialize`, `document`.
- **Drain:** the local agent drains `project-ops` on its normal cadence and dispatches to the
  `prototyper` service handler.

## Sequence

**Submit (cloud):**

1. `queue_submit` Lambda gates the principal (`authz.gate(..., "readwrite")`) and enqueues the message
   exactly as any other AsyncQueue job. No Prototyper code runs in the cloud — the cloud never sees the
   filesystem.

**Drain (local agent):**

1. The agent resolves the `prototyper` service to `PROTOTYPER_DIR` (from its local config /
   `prototyper_directory:` in METADATA.md).
2. It maps `tool` through the **allow-list** to exactly one script — no free-form command:
   | `tool` | Script |
   |--------|--------|
   | `validate` | `bin/ProjectValidate.sh` |
   | `update` | `bin/ProjectUpdate.sh` |
   | `initialize` | `bin/ProjectInitialize.sh` |
   | `document` | `bin/ProjectDocument.sh` |
3. It validates `project` against `^[A-Za-z0-9_-]+$` and rejects any shell metacharacters in `args`;
   then runs `bash "$PROTOTYPER_DIR/<script>" <project> [args]`, capturing stdout/stderr and exit code.
4. It reports the outcome via `mar.report.event(severity, message)` — `INFORMATION` on success,
   `ERROR` on non-zero exit — with the project, tool, exit code, and a truncated tail of the output.
5. On success the message is deleted; on failure it retries via SQS, then DLQs (standard AsyncQueue
   semantics).

## Reads

- SQS `project-ops` message (drain); the local Prototyper checkout; the service→`PROTOTYPER_DIR` mapping.
- ACL via the access-control gate (at submit time).

## Writes

- The target project's repository (whatever the Prototyper script writes — rules injection, templates,
  generated docs). These writes are local, by the Prototyper script, exactly as if run by hand.
- A Marina event recording the run (via `marina.report`); SQS `DeleteMessage` on success / DLQ on failure.

## Guardrails

- Only the four allow-listed `tool` values dispatch; an unknown `tool` is rejected (event, not executed).
- `tool` never carries a path or command — it indexes a fixed table. `project`/`args` are sanitised
  before they reach the shell. This is the guardrailed-direct-invocation perimeter the platform wants
  for non-`start` scripts, scoped here to Prototyper's capital-letter (Global) conformance scripts only.
- The handler runs **only** on the box where `prototyper_directory` resolves; submission is otherwise a
  no-op job that waits in the queue.

## Test

- **Script:** `bin/test_project_ops.sh` → submits a `validate` job for a known conformed project, runs a
  local drain, and asserts: the matching `ProjectValidate.sh` ran, its exit code was captured, a Marina
  event carries the result, and the message was deleted; submits an unknown `tool` and asserts it is
  rejected (event emitted, no script executed).
- **Pass criteria:** allow-list enforced; exit code and output captured; result observable as an event;
  poison/unknown jobs do not execute and land in the DLQ or are rejected; nothing runs in the cloud.
- **CloudWatch:** the `report_ingest` log group shows `{"event":"event_ingest","project":...}` carrying
  `{"tool":"validate","exit":0}`; the `project-ops` SQS metrics show enqueue/drain depth — the
  screen-less verification surface for a run kicked off remotely.

## Open Questions

- Should long-running ops (`initialize`, `document`) stream incremental progress events, or just a single
  terminal event? Leaning terminal-only for Phase 2; add progress events if a run is slow enough to need
  a heartbeat.
- Should the result also write a `report.event` against the **target** project (so its health view shows
  "last conformed at …"), in addition to the operator-facing event? Likely yes — cheap and useful.
- `args` passthrough: keep it to a tight allow-list of known flags (e.g. `--dry-run`) rather than
  arbitrary strings, even after sanitisation? Leaning allow-list of flags.
