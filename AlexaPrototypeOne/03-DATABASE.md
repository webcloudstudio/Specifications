# 03 — Database Schema

SQLite database at `data/alexa.db`. WAL mode enabled. Foreign keys enforced.
Initialized by `init_db.py` on first run; safe to re-run (idempotent).

See `stack/sqlite.md` for connection patterns and query conventions.

---

## Tables

### routing_rules

The core configuration table. Each row maps a keyword pattern to a destination.
Seeded with defaults by `init_db.py`. User-editable via the config UI.

```sql
CREATE TABLE IF NOT EXISTS routing_rules (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword             TEXT NOT NULL,
    match_type          TEXT NOT NULL DEFAULT 'contains',
    -- 'exact' | 'contains' | 'startswith'
    destination_type    TEXT NOT NULL,
    -- 'game_ticket' | 'file_append' | 'api_endpoint' | 'run_script' | 'slack_webhook'
    destination_config  TEXT NOT NULL DEFAULT '{}',
    -- JSON object; schema varies by destination_type (see 06-ROUTING-RULES.md)
    requires_confirmation INTEGER NOT NULL DEFAULT 0,  -- boolean
    priority            INTEGER NOT NULL DEFAULT 100,
    -- Lower integer = higher priority. First matching rule wins.
    enabled             INTEGER NOT NULL DEFAULT 1,    -- boolean
    description         TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_rules_enabled_priority
    ON routing_rules (enabled, priority);
CREATE UNIQUE INDEX IF NOT EXISTS idx_rules_keyword_type
    ON routing_rules (keyword, match_type);
```

**destination_config JSON schemas** (see 06-ROUTING-RULES.md for full detail):

| destination_type | Required keys |
|-----------------|---------------|
| `game_ticket`   | `project_keyword` |
| `file_append`   | `path`, `format` |
| `api_endpoint`  | `url`, `method` |
| `run_script`    | `script` |
| `slack_webhook` | `webhook_url` |

---

### message_log

Records every message received from SQS — its lifecycle from receipt through dispatch.
This is the primary audit trail and the source of truth for the config UI's message view.

```sql
CREATE TABLE IF NOT EXISTS message_log (
    id                  TEXT PRIMARY KEY,
    -- SQS message ID (UUID, set by AWS)
    sqs_receipt_handle  TEXT,
    -- SQS receipt handle; required to delete message after processing
    keyword_raw         TEXT NOT NULL,
    -- Full utterance text as received from Alexa (lowercase normalized)
    matched_rule_id     INTEGER REFERENCES routing_rules(id) ON DELETE SET NULL,
    alexa_session_id    TEXT,
    user_id             TEXT,
    device_id           TEXT,
    status              TEXT NOT NULL DEFAULT 'received',
    -- State machine:
    --   received → dispatching → completed
    --   received → pending_confirm → confirmed → dispatching → completed
    --   received → pending_confirm → rejected
    --   dispatching → failed (on dispatch error)
    destination_type    TEXT,
    destination_config  TEXT,           -- JSON snapshot of rule config at dispatch time
    requires_confirmation INTEGER DEFAULT 0,
    retry_count         INTEGER NOT NULL DEFAULT 0,
    max_retries         INTEGER NOT NULL DEFAULT 3,
    error_msg           TEXT,
    received_at         TEXT NOT NULL DEFAULT (datetime('now')),
    dispatching_at      TEXT,
    completed_at        TEXT,
    result              TEXT            -- JSON response from destination (if any)
);

CREATE INDEX IF NOT EXISTS idx_msg_status     ON message_log (status);
CREATE INDEX IF NOT EXISTS idx_msg_received   ON message_log (received_at DESC);
CREATE INDEX IF NOT EXISTS idx_msg_rule       ON message_log (matched_rule_id);
```

---

### confirmations

Tracks approval decisions for messages where `requires_confirmation = 1`.

```sql
CREATE TABLE IF NOT EXISTS confirmations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id  TEXT NOT NULL REFERENCES message_log(id) ON DELETE CASCADE,
    status      TEXT NOT NULL DEFAULT 'pending',
    -- 'pending' | 'approved' | 'rejected' | 'timed_out'
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    decided_at  TEXT,
    decided_by  TEXT        -- 'user' | 'auto_timeout'
);

CREATE INDEX IF NOT EXISTS idx_conf_message  ON confirmations (message_id);
CREATE INDEX IF NOT EXISTS idx_conf_status   ON confirmations (status);
```

---

### audit_log

Append-only event log. Written by daemon and Flask UI for every significant
state transition. Never modified after insert.

```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,
    -- 'sqs_received' | 'rule_matched' | 'rule_unmatched' | 'dispatched'
    -- | 'dispatch_failed' | 'confirm_requested' | 'confirm_approved'
    -- | 'confirm_rejected' | 'confirm_timed_out' | 'sqs_deleted'
    message_id  TEXT,
    rule_id     INTEGER,
    details     TEXT,       -- JSON with event-specific data
    success     INTEGER,    -- boolean
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_audit_message   ON audit_log (message_id);
CREATE INDEX IF NOT EXISTS idx_audit_event     ON audit_log (event_type);
CREATE INDEX IF NOT EXISTS idx_audit_created   ON audit_log (created_at DESC);
```

---

## Default Seed Data

Inserted by `init_db.py` if `routing_rules` is empty:

```sql
INSERT INTO routing_rules (keyword, match_type, destination_type, destination_config, description)
VALUES
    ('game ticket',  'contains', 'game_ticket',  '{"project_keyword": "GAME", "auto_approve": false}',
     'Create a GAME workflow ticket'),
    ('book idea',    'contains', 'file_append',  '{"path": "data/ideas/book.txt", "format": "[{timestamp}] {utterance}\n"}',
     'Append to book ideas file'),
    ('note',         'startswith','file_append', '{"path": "data/notes.txt", "format": "[{timestamp}] {utterance}\n"}',
     'Append to general notes'),
    ('end',          'exact',    'session_close', '{}',
     'Close Alexa session (no external dispatch)');
```

---

## db.py — Initialization Pattern

```python
import sqlite3, os
from contextlib import contextmanager

DB_PATH = os.environ.get('DB_PATH', 'data/alexa.db')

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        with open('schema.sql') as f:
            conn.executescript(f.read())
        # Seed defaults if empty
        row = conn.execute("SELECT COUNT(*) FROM routing_rules").fetchone()
        if row[0] == 0:
            _seed_defaults(conn)
```
