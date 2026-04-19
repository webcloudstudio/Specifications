# Feature: AsyncQueue Service

**Version:** 2026-04-06 V1
**Description:** File-based store-and-forward message queue — works when the GAME server is down, drained on startup or on demand

## Design Intent

Not everything can wait for the GAME server to be running. A phone app sends a voice note at 2 AM. A cron job on another machine finishes and wants to notify the platform. A script fails and wants to enqueue a retry. These producers need a queue that accepts work regardless of whether the consumer is alive.

**File-based, dead simple:** The queue is a JSONL file. Producers append a line. That is the entire write path — no server, no socket, no protocol. Any language that can append to a file can enqueue work. When GAME starts (or on demand), it drains the queue: reads each line, dispatches to the appropriate handler, and marks it processed.

**Why not a real message broker:** This platform is for a single developer or a small team running local services. RabbitMQ or Redis Streams are correct at scale but wrong here — they add infrastructure, configuration, and failure modes that a JSONL file does not have. If the developer outgrows file queues, the service interface stays the same and the transport changes to a broker behind the config.

**The VoiceForward example:** Today VoiceForward (FEATURE-VOICEFORWARD.md) posts directly to the GAME server via `POST /api/voice/upload`. If the server is down, the recording is lost. With AsyncQueue, the phone app (or a lightweight relay) writes a queue message. When GAME starts, it drains the queue, transcribes the audio, and appends the text — no recording lost, no timing dependency.

**The general pattern:** Any service that benefits from "submit now, process later" can use AsyncQueue as a transport. The service manifest (FEATURE-ServiceInterfaces.md) declares `async: true`, and the platform generates the queue file and drain logic automatically.

---

## Queue File Format

Each queue is a JSONL file at `data/queues/{queue-name}.queue.jsonl`. One line per message:

```jsonl
{"id":"a1b2c3","queue":"voice","service":"voiceforward","tool":"transcribe","payload":{"audio_path":"/tmp/rec_001.webm","label":"BOOK IDEAS"},"submitted_at":"2026-04-06T02:15:00Z","status":"pending","priority":"normal"}
{"id":"d4e5f6","queue":"voice","service":"voiceforward","tool":"transcribe","payload":{"audio_path":"/tmp/rec_002.webm","label":"GAME SPEC"},"submitted_at":"2026-04-06T02:17:00Z","status":"pending","priority":"normal"}
```

### Message Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique message ID (UUID or short hash) |
| `queue` | string | Yes | Queue name (determines which file and which drain handler) |
| `service` | string | Yes | Target service name from the service registry |
| `tool` | string | Yes | Tool name within the service to invoke |
| `payload` | object | Yes | Tool inputs (must match the tool's input schema) |
| `submitted_at` | string | Yes | ISO 8601 timestamp |
| `status` | string | Yes | `pending` / `processing` / `done` / `error` / `expired` |
| `priority` | string | No | `low` / `normal` / `high` / `critical` (default: `normal`) |
| Description |  |
| Version     | (set version) |
| Depends On  | FEATURE-VOICEFORWARD.md |
| Provides    | POST /api/voice/upload, POST /api/services/async-queue/submit, POST /api/services/async-queue/drain |
| `ttl_seconds` | integer | No | Message expires if not processed within this many seconds after submission |
| `result` | object | No | Set by drain handler on completion |
| `error` | string | No | Set by drain handler on failure |
| `processed_at` | string | No | Timestamp when processing completed |

---

## Queue Operations

### Submit (Producer Side)

Producers write to the queue by appending a JSONL line. Three ways to submit:

**1. Direct file append (works without GAME running):**

```bash
echo '{"id":"'$(uuidgen)'","queue":"voice","service":"voiceforward","tool":"transcribe","payload":{"audio_path":"/tmp/rec.webm","label":"BOOK IDEAS"},"submitted_at":"'$(date -Iseconds)'","status":"pending","priority":"normal"}' >> data/queues/voice.queue.jsonl
```

**2. Python helper in common.py:**

```python
from common import services
services.async_queue.submit(
    queue="voice",
    service="voiceforward",
    tool="transcribe",
    payload={"audio_path": "/tmp/rec.webm", "label": "BOOK IDEAS"}
)
```

The helper generates the ID, timestamp, and appends to the file. Works without GAME running.

**3. REST API (requires GAME running):**

```
POST /api/services/async-queue/submit
{
  "queue": "voice",
  "service": "voiceforward",
  "tool": "transcribe",
  "payload": {"audio_path": "/tmp/rec.webm", "label": "BOOK IDEAS"}
}
```

### Drain (Consumer Side)

Draining processes pending messages in priority then submission order:

1. Read the queue file
2. Filter for `status = pending` (skip done/error/expired)
3. Check TTL — mark expired messages as `expired`
4. For each pending message (highest priority first, then oldest first):
   a. Set status to `processing`
   b. Resolve the target service and tool from the service registry
   c. Call the tool (via internal Python dispatch, not REST — no network dependency)
   d. On success: set status to `done`, record `result` and `processed_at`
   e. On failure: set status to `error`, record `error` message
5. Rewrite the queue file with updated statuses

**Drain triggers:**
- **Startup:** GAME drains all queues on startup (after scan completes)
- **On demand:** `POST /api/services/async-queue/drain` or `game-cli async-queue drain`
- **Periodic:** Optional scheduler job (e.g., drain every 5 minutes)
- **File watch (future):** inotify/fswatch on the queues directory for immediate processing

### Queue Rotation

Processed messages (done/error/expired) accumulate in the queue file. Rotation moves them to an archive:

- After drain, if the queue file exceeds 1000 lines or 1 MB, rotate:
  - Move completed messages to `data/queues/archive/{queue-name}.{date}.jsonl`
  - Rewrite the active file with only pending/processing messages
- Archive files are kept for 30 days (configurable), then deleted

---

## Service Manifest

```yaml
name: async-queue
description: File-based store-and-forward message queue — submit work when the server is down, drain on startup
version: 1.0.0

transports:
  rest: true
  cli: true
  mcp: false
  async: false    # The queue itself is not async-backed (it IS the async mechanism)

tools:
  - name: submit
    description: >
      Submit a message to a named queue. The message will be processed when
      the queue is next drained (on server startup, on schedule, or on demand).
      Works without the GAME server running if called via common.py or direct file append.
    inputs:
      queue:
        type: string
        required: true
        description: Queue name (determines file and handler)
      service:
        type: string
        required: true
        description: Target service to invoke when processing
      tool:
        type: string
        required: true
        description: Tool within the target service
      payload:
        type: object
        required: true
        description: Tool inputs (passed directly to the service tool)
      priority:
        type: string
        required: false
        description: Message priority (low/normal/high/critical)
      ttl_seconds:
        type: integer
        required: false
        description: Expire if not processed within this many seconds
    output:
      id: { type: string, description: "Assigned message ID" }
      queue: { type: string }
      status: { type: string, description: "pending" }

  - name: status
    description: Check the status of a submitted message
    inputs:
      id:
        type: string
        required: true
        description: Message ID from submit
      queue:
        type: string
        required: true
        description: Queue name to search
    output:
      id: { type: string }
      status: { type: string }
      result: { type: object, nullable: true }
      error: { type: string, nullable: true }
      submitted_at: { type: string }
      processed_at: { type: string, nullable: true }

  - name: list
    description: List messages in a queue, optionally filtered by status
    inputs:
      queue:
        type: string
        required: true
      status:
        type: string
        required: false
        description: Filter by message status (pending/processing/done/error/expired)
      limit:
        type: integer
        required: false
    output:
      messages:
        type: array
        items:
          id: string
          service: string
          tool: string
          status: string
          priority: string
          submitted_at: string

  - name: drain
    description: Process all pending messages in a queue (or all queues if queue is omitted)
    inputs:
      queue:
        type: string
        required: false
        description: Specific queue to drain (omit for all queues)
    output:
      processed: { type: integer, description: "Number of messages processed" }
      succeeded: { type: integer }
      failed: { type: integer }
      expired: { type: integer }

  - name: list_queues
    description: List all known queues with message counts
    inputs: {}
    output:
      queues:
        type: array
        items:
          name: string
          pending: integer
          processing: integer
          done: integer
          error: integer
          last_drained: string
```

---

## Queue Configuration

Queues are auto-created when the first message is submitted. No pre-registration needed. GAME discovers all `data/queues/*.queue.jsonl` files on startup.

Optional configuration per queue in `data/queues/queue_config.yaml`:

```yaml
queues:
  voice:
    drain_on_startup: true
    drain_interval_minutes: 5
    max_retries: 3
    ttl_default_seconds: 86400    # 24 hours
    archive_retention_days: 30
  default:
    drain_on_startup: true
    drain_interval_minutes: 0     # 0 = no periodic drain
    max_retries: 1
    ttl_default_seconds: 0        # 0 = no expiry
    archive_retention_days: 30
```

---

## New Routes

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/services/async-queue/submit` | Submit a message to a queue |
| GET | `/api/services/async-queue/status?id=X&queue=Y` | Check message status |
| GET | `/api/services/async-queue/list?queue=Y` | List queue messages |
| POST | `/api/services/async-queue/drain` | Drain pending messages |
| GET | `/api/services/async-queue/list_queues` | List all queues with counts |

---

## Directory Layout

```
GAME/
  data/
    queues/
      voice.queue.jsonl          # Active queue file
      default.queue.jsonl        # Default queue for unrouted messages
      queue_config.yaml          # Per-queue configuration
      archive/                   # Rotated completed messages
        voice.2026-04-06.jsonl
```

---

## Open Questions

- Should failed messages be automatically retried? If so, how many times and with what backoff? The config supports `max_retries` but the retry mechanism (immediate vs. exponential backoff vs. next drain cycle) needs design.
- Should the queue support dead-letter routing — messages that fail all retries go to a separate `{queue}.dead.jsonl` for manual inspection?
- Should `common.py` file append use file locking (`fcntl.flock`) to prevent corruption from concurrent writers? Probably yes for safety, but JSONL append is mostly atomic on Linux for reasonable line lengths.
- Should there be a UI component on the Service Catalog or a dedicated Queues screen showing queue depths and drain status? Probably a tab or section on the Service Catalog screen.
