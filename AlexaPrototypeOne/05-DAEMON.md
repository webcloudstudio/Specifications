# 05 — SQS Polling Daemon

The daemon is a long-running Python process (not a Flask app — no HTTP server).
It polls SQS, matches routing rules, dispatches to destinations, and manages the
message lifecycle. It is started and stopped via `bin/start-daemon.sh` / `bin/stop-daemon.sh`.

---

## Process Model

**Single-threaded, synchronous dispatch.** The daemon processes one SQS batch
at a time. It does not run parallel dispatches. This keeps state simple and
avoids concurrent writes to SQLite.

**Implication for slow scripts:** If a `run_script` destination takes 25 seconds,
the next SQS poll is delayed by 25 seconds. This is acceptable for a personal
prototype. The SQS message's visibility timeout (30s default) must exceed the
longest expected dispatch time — if it doesn't, SQS re-delivers before dispatch
completes, causing a duplicate. See "Visibility Timeout" section below.

**Concurrency upgrade path:** Add a `ThreadPoolExecutor` with max 4 workers in a
later iteration if slow dispatches become a problem. Not in scope for v1.

---

## Main Loop

```python
# daemon.py
import json
import logging
import os
import signal
import sys
import time

import boto3
from dotenv import load_dotenv

from db import get_db, init_db
from dispatcher import dispatch
from routing import match_rule, load_rules
from confirmations import handle_pending_confirmations

load_dotenv()
logger = logging.getLogger(__name__)

QUEUE_URL = os.environ['SQS_QUEUE_URL']
POLL_INTERVAL = int(os.environ.get('DAEMON_POLL_INTERVAL', '5'))
PID_FILE = 'data/daemon.pid'

sqs = boto3.client('sqs', region_name=os.environ['AWS_REGION'])
running = True


def handle_signal(signum, frame):
    global running
    logger.info(f"[GAME] Service Stopped: SQS Daemon")
    running = False


def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Write PID file
    os.makedirs('data', exist_ok=True)
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    init_db()
    logger.info(f"[GAME] Service Starting: SQS Daemon")
    logger.info(f"[GAME] Service Started: SQS Daemon polling {QUEUE_URL}")

    try:
        while running:
            poll_and_dispatch()
            handle_pending_confirmations()
            time.sleep(POLL_INTERVAL)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        logger.info("[GAME] Service Stopped: SQS Daemon")


def poll_and_dispatch():
    """Receive up to 10 messages, process each, delete on success."""
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20,     # Long polling — reduces empty receive API calls
        MessageAttributeNames=['All'],
    )
    messages = response.get('Messages', [])
    if not messages:
        return

    rules = load_rules()    # Re-read from SQLite on every cycle

    for msg in messages:
        receipt = msg['ReceiptHandle']
        try:
            body = json.loads(msg['Body'])
        except json.JSONDecodeError as e:
            logger.error(f"Invalid SQS message body: {e}")
            _delete_message(receipt)    # Malformed — discard
            continue

        _process_message(body, receipt, rules)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    main()
```

---

## Message Processing

```python
def _process_message(body: dict, receipt: str, rules: list):
    message_id = body['message_id']
    utterance = body['keyword_raw']

    # 1. Write to message_log (received state)
    with get_db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO message_log
            (id, sqs_receipt_handle, keyword_raw, status, received_at)
            VALUES (?, ?, ?, 'received', datetime('now'))
        """, (message_id, receipt, utterance))

    # 2. Match routing rule
    rule = match_rule(utterance, rules)
    if rule is None:
        logger.info(f"No rule matched for: {utterance!r}")
        _update_status(message_id, 'completed', error_msg='No rule matched')
        _delete_message(receipt)    # Discard unmatched messages
        _audit(message_id, 'rule_unmatched', success=True)
        return

    # 3. Log rule match
    with get_db() as conn:
        conn.execute("""
            UPDATE message_log SET matched_rule_id=?, destination_type=?,
            destination_config=?, requires_confirmation=?
            WHERE id=?
        """, (rule['id'], rule['destination_type'],
              rule['destination_config'], rule['requires_confirmation'], message_id))
    _audit(message_id, 'rule_matched', rule_id=rule['id'], success=True)

    # 4. Check confirmation requirement
    if rule['requires_confirmation']:
        _hold_for_confirmation(message_id, receipt, rule)
        return

    # 5. Dispatch
    _do_dispatch(message_id, receipt, body, rule)
```

---

## Dispatch

```python
def _do_dispatch(message_id, receipt, body, rule):
    _update_status(message_id, 'dispatching')
    try:
        result = dispatch(rule['destination_type'], rule['destination_config'], body)
        _update_status(message_id, 'completed', result=result)
        _delete_message(receipt)
        _audit(message_id, 'dispatched', rule_id=rule['id'], success=True)
    except Exception as e:
        logger.error(f"Dispatch failed for {message_id}: {e}")
        _increment_retry(message_id, str(e))
        _audit(message_id, 'dispatch_failed', success=False,
               details={'error': str(e)})
        # Do NOT delete from SQS — visibility timeout causes re-delivery
```

---

## Visibility Timeout and Retry

When dispatch fails, the message is **not deleted from SQS**. SQS will re-deliver
it after the visibility timeout (30s by default).

**If retry_count reaches max_retries (3):**
- Mark `message_log.status = 'failed'` permanently
- Delete from SQS to prevent infinite re-delivery
- Log to audit_log

This requires the daemon to track retries in `message_log` and check them:

```python
def _increment_retry(message_id, error_msg):
    with get_db() as conn:
        row = conn.execute(
            "SELECT retry_count, max_retries FROM message_log WHERE id=?",
            (message_id,)
        ).fetchone()
        if row and row['retry_count'] + 1 >= row['max_retries']:
            conn.execute("""
                UPDATE message_log SET status='failed', retry_count=retry_count+1,
                error_msg=? WHERE id=?
            """, (error_msg, message_id))
            # Caller must also delete from SQS in this case
        else:
            conn.execute("""
                UPDATE message_log SET retry_count=retry_count+1, error_msg=?
                WHERE id=?
            """, (error_msg, message_id))
```

---

## Confirmation Hold

When a rule has `requires_confirmation=1`:

```python
def _hold_for_confirmation(message_id, receipt, rule):
    # 1. Extend SQS visibility timeout to 12 hours
    sqs.change_message_visibility(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt,
        VisibilityTimeout=43200     # 12 hours in seconds
    )
    # 2. Update message_log
    _update_status(message_id, 'pending_confirm')
    # 3. Insert confirmation record
    with get_db() as conn:
        conn.execute("""
            INSERT INTO confirmations (message_id, status, created_at)
            VALUES (?, 'pending', datetime('now'))
        """, (message_id,))
    _audit(message_id, 'confirm_requested', rule_id=rule['id'], success=True)
    logger.info(f"Holding message {message_id} for confirmation")
```

See 07-CONFIRMATION-FLOW.md for the full approval lifecycle.

---

## bin/start-daemon.sh

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Start Daemon
# Description: Start the SQS polling daemon

export PORT=${PORT:-5002}
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/data/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/StartDaemon_$(date +%Y%m%d_%H%M%S).log"

cd "$PROJECT_ROOT"
source venv/bin/activate 2>/dev/null || true

echo "[GAME] Service Starting: SQS Daemon" | tee -a "$LOG_FILE"
python daemon.py >> "$LOG_FILE" 2>&1 &
echo "[GAME] Service Started: SQS Daemon (PID $!)" | tee -a "$LOG_FILE"
```

## bin/stop-daemon.sh

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Stop Daemon

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/data/daemon.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Daemon not running (no PID file)."
    exit 0
fi

PID=$(cat "$PID_FILE")
kill "$PID" 2>/dev/null && echo "Sent SIGTERM to PID $PID" || echo "PID $PID not found."
```
