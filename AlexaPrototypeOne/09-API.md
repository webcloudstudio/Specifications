# 09 — API Reference

All JSON API endpoints for the Flask config UI. Used by HTMX partials and
can be called by external tools (curl, GAME integration, etc.).

Authentication: `Authorization: Bearer {SECRET_KEY}` header on all `/api/` routes.
Omit auth for HTMX-triggered endpoints (they originate from the same origin).

---

## Routing Rules

### GET /api/rules

Returns all routing rules ordered by priority ASC.

**Response 200:**
```json
{
  "rules": [
    {
      "id": 1,
      "keyword": "game ticket",
      "match_type": "contains",
      "destination_type": "game_ticket",
      "destination_config": {"project_keyword": "GAME", "auto_approve": false},
      "requires_confirmation": false,
      "priority": 100,
      "enabled": true,
      "description": "Create a GAME workflow ticket",
      "created_at": "2026-03-11T14:00:00",
      "updated_at": "2026-03-11T14:00:00"
    }
  ],
  "total": 4
}
```

---

### POST /api/rules

Create a new routing rule.

**Request:**
```json
{
  "keyword": "slack note",
  "match_type": "startswith",
  "destination_type": "slack_webhook",
  "destination_config": {
    "webhook_url": "https://hooks.slack.com/services/...",
    "template": "{utterance}"
  },
  "requires_confirmation": false,
  "priority": 50,
  "description": "Post to Slack dev channel",
  "enabled": true
}
```

**Response 201:**
```json
{"id": 5, "status": "created"}
```

**Response 400** (validation failure):
```json
{"error": "destination_config missing required key: webhook_url"}
```

---

### PUT /api/rules/<id>

Update an existing rule. Accepts same body as POST. Returns 200 `{"status": "updated"}`.

---

### DELETE /api/rules/<id>

Delete a rule. Returns 200 `{"status": "deleted"}`.

---

### POST /api/rules/<id>/toggle

Toggle `enabled` flag. Returns 200 `{"enabled": true}`.

---

### GET /api/rules/test?utterance=<text>

Test which rule would match a given utterance.

**Response 200:**
```json
{
  "matched": true,
  "rule": {
    "id": 2,
    "keyword": "book idea",
    "match_type": "contains",
    "destination_type": "file_append"
  }
}
```

```json
{"matched": false, "rule": null}
```

---

## Confirmations

### GET /api/confirmations

Returns all pending confirmations with message details.

**Response 200:**
```json
{
  "confirmations": [
    {
      "id": 3,
      "message_id": "uuid-...",
      "utterance": "deploy production server",
      "rule_description": "Run deploy script",
      "destination_type": "run_script",
      "destination_summary": "bin/deploy.sh",
      "created_at": "2026-03-11T14:00:00",
      "age_minutes": 12
    }
  ],
  "total": 1
}
```

---

### POST /api/confirmations/<id>/approve

Approve a pending confirmation. Daemon dispatches on next poll.

**Response 200:** `{"status": "approved"}`
**Response 404:** `{"error": "Not found or already decided"}`

---

### POST /api/confirmations/<id>/reject

Reject a pending confirmation. Deletes from SQS immediately.

**Response 200:** `{"status": "rejected"}`

---

## Messages

### GET /api/messages

Returns recent messages. Query params: `status`, `limit` (default 50), `offset`.

**Response 200:**
```json
{
  "messages": [
    {
      "id": "uuid-...",
      "keyword_raw": "book idea about machine learning",
      "status": "completed",
      "matched_rule_id": 2,
      "destination_type": "file_append",
      "retry_count": 0,
      "received_at": "2026-03-11T14:23:01",
      "completed_at": "2026-03-11T14:23:03"
    }
  ],
  "total": 142,
  "has_more": true
}
```

---

## Daemon Status

### GET /api/daemon/status

Checks if daemon process is running.

```python
import os, psutil

@bp.route('/api/daemon/status')
def daemon_status():
    pid_file = 'data/daemon.pid'
    if not os.path.exists(pid_file):
        return jsonify({'running': False, 'pid': None})
    pid = int(open(pid_file).read().strip())
    running = psutil.pid_exists(pid)
    return jsonify({'running': running, 'pid': pid if running else None})
```

**Response 200:**
```json
{"running": true, "pid": 12345}
```
```json
{"running": false, "pid": null}
```

---

## Queue Depth

### GET /api/queue/depth

Returns current SQS queue message counts.

```python
@bp.route('/api/queue/depth')
def queue_depth():
    sqs = boto3.client('sqs', region_name=os.environ['AWS_REGION'])
    attrs = sqs.get_queue_attributes(
        QueueUrl=os.environ['SQS_QUEUE_URL'],
        AttributeNames=[
            'ApproximateNumberOfMessages',
            'ApproximateNumberOfMessagesNotVisible',
        ]
    )['Attributes']
    return jsonify({
        'available': int(attrs['ApproximateNumberOfMessages']),
        'in_flight': int(attrs['ApproximateNumberOfMessagesNotVisible']),
    })
```

**Response 200:**
```json
{"available": 3, "in_flight": 1}
```

---

## Partials (HTMX fragments)

These routes return HTML fragments, not JSON. Used for auto-refresh.

| Route | Returns |
|-------|---------|
| `GET /partials/queue-stats` | Queue stats card grid HTML |
| `GET /partials/pending-confirmations` | Confirmations section HTML (empty string if none) |
| `GET /partials/recent-messages` | Recent messages table body HTML |
| `GET /partials/daemon-status` | Daemon status badge HTML |

---

## Health

### GET /health

Returns 200 if Flask is up and SQLite is reachable.

```json
{"status": "ok", "db": "ok", "daemon": true}
```

Returns 503 if DB is unreachable.

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid request body / missing required field |
| 404 | Resource not found |
| 409 | Conflict (e.g., duplicate keyword+match_type) |
| 500 | Unhandled server error |
| 503 | Database or SQS unavailable |
