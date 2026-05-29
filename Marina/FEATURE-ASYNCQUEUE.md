# Feature: Async Queue

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | SQS-backed store-and-forward queue — producers submit 24x7, the local agent drains when alive. Replaces GAME's JSONL file queue. |
| Depends On  | FEATURE-MARINA-LIB.md, FEATURE-ACCESS-CONTROL.md |
| Provides    | POST /queue/{queue} |

**Description:** Durable "submit now, process later" work. A producer (a remote cron job, a failed
script, a phone inside the firewall) enqueues a message at any time; the local Marina agent drains the
queue and dispatches each message to the target service/tool when it next runs.

## Trigger

- **Submit:** `mar.queue.submit(queue, service, tool, payload, priority)` → `POST /queue/{queue}`, or a
  direct producer with SigV4. Works regardless of whether the local consumer is running.
- **Drain:** the local agent calls `mar.queue.drain(queue=None)` on startup, on a schedule, or on demand.

## Sequence

**Submit:**

1. `queue_submit` Lambda gates the principal, validates the body against the message contract, assigns an
   `id` and `submitted_at`, and `SendMessage` to the SQS queue `marina-{project}-{queue}` (per
   `stack/aws-sqs.md`). Returns `{id, queue, status:"pending"}`.

**Drain (local, via the library):**

1. `ReceiveMessage` with long polling (`WaitTimeSeconds=20`, `MaxNumberOfMessages=10`).
2. For each message: resolve `service`+`tool` from the local service registry; dispatch `payload`.
3. On success: `DeleteMessage` (delete only after success — outbox pattern). On failure: do not delete;
   the visibility timeout returns it for retry; after `maxReceiveCount=3` it lands in the DLQ.
4. Honour `ttl_seconds`: expire stale messages instead of processing. Drain is idempotent — handlers key
   on message `id`.
5. Returns `{processed, succeeded, failed, expired}`.

## Message contract

```json
{ "id":"...", "queue":"voice", "service":"voiceforward", "tool":"transcribe",
  "payload":{...}, "priority":"normal", "ttl_seconds":86400, "submitted_at":"..." }
```

## Reads

- SQS messages (consumer); request body (submit); ACL via the gate.

## Writes

- SQS `SendMessage` (submit) and `DeleteMessage` (drain) via `marina.queue`; DLQ on repeated failure.

## Test

- **Script:** `bin/test_asyncqueue.sh` → submits a message to a test queue, asserts it is `pending`;
  runs a drain with a stub handler, asserts the message is processed and deleted and counts return
  `succeeded:1`; submits a poison message and asserts it lands in the DLQ after 3 receives.
- **Pass criteria:** at-least-once delivery; delete only after success; idempotent re-drain processes
  nothing; DLQ catches the poison message.
- **CloudWatch:** drain logs `{"event":"queue_drain","queue":...,"processed":N,"succeeded":N}`; SQS
  CloudWatch metrics show `ApproximateNumberOfMessagesVisible` and DLQ depth.

## Open Questions

- Retry/backoff between drains: rely solely on SQS visibility timeout + `maxReceiveCount`, or add
  application-level backoff metadata? SQS-native is simpler and sufficient — leaning that way.
- Should drain run as a local loop or a scheduled invocation? Local agent owns cadence; document a
  default (startup + every 5 minutes).
