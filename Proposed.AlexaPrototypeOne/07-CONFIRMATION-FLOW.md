# 07 — Confirmation Flow

Some routing rules are flagged `requires_confirmation = 1`. These messages are
held in a pending state until the user approves or rejects them in the config UI.
Messages are not dispatched until explicitly approved.

---

## State Transitions

```
SQS message received
        ↓
  rule matched
        ↓
requires_confirmation = 1?
   YES ↓              NO → dispatch immediately
pending_confirm
   ↓           ↓
approved    rejected (or timed_out)
   ↓               ↓
dispatching      sqs_deleted (no dispatch)
   ↓
completed
```

---

## Hold Flow (Daemon)

When the daemon encounters a message whose matched rule has `requires_confirmation = 1`:

1. **Extend SQS visibility timeout to 12 hours**
   - Prevents SQS from re-delivering the message before the user acts
   - SQS default (30s) would cause re-delivery and duplicate confirmation requests
   - 12 hours = `VisibilityTimeout=43200`

2. **Update `message_log.status = 'pending_confirm'`**

3. **Insert row into `confirmations` table** with `status='pending'`

4. **Do not delete from SQS** — the receipt handle must be retained in
   `message_log.sqs_receipt_handle` for deletion after approval

The daemon emits no Alexa response at confirmation time — Alexa has already
received "Got it" from Lambda. The Lambda response may optionally say
"Got it, that needs your approval." if the `ALEXA_SKILL_ID` hint is set, but
this requires Lambda to query the routing rules (adds latency and complexity —
not in scope for v1).

---

## Approval Flow (Config UI → Daemon)

**User action:** Clicks "Approve" button in the Pending Confirmations section.

**Flask route:** `POST /api/confirmations/<confirmation_id>/approve`

```python
@bp.route('/api/confirmations/<int:conf_id>/approve', methods=['POST'])
def approve_confirmation(conf_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM confirmations WHERE id=?", (conf_id,)
        ).fetchone()
        if not row or row['status'] != 'pending':
            return jsonify({'error': 'Not found or already decided'}), 404

        conn.execute("""
            UPDATE confirmations SET status='approved', decided_at=datetime('now'),
            decided_by='user' WHERE id=?
        """, (conf_id,))
        conn.execute("""
            UPDATE message_log SET status='confirmed' WHERE id=?
        """, (row['message_id'],))
    return jsonify({'status': 'approved'})
```

**Daemon side** (called in `handle_pending_confirmations()` each poll cycle):

```python
def handle_pending_confirmations():
    """Find confirmed messages and dispatch them."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT ml.*, c.id as conf_id
            FROM message_log ml
            JOIN confirmations c ON c.message_id = ml.id
            WHERE ml.status = 'confirmed' AND c.status = 'approved'
        """).fetchall()

    for row in rows:
        rule = _get_rule_by_id(row['matched_rule_id'])
        if rule:
            body = {
                'message_id': row['id'],
                'keyword_raw': row['keyword_raw'],
            }
            _do_dispatch(row['id'], row['sqs_receipt_handle'],
                         body, rule)
```

---

## Rejection Flow (Config UI → Daemon)

**Flask route:** `POST /api/confirmations/<confirmation_id>/reject`

```python
@bp.route('/api/confirmations/<int:conf_id>/reject', methods=['POST'])
def reject_confirmation(conf_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM confirmations WHERE id=?", (conf_id,)
        ).fetchone()
        if not row or row['status'] != 'pending':
            return jsonify({'error': 'Not found or already decided'}), 404

        # Get the SQS receipt to delete the message
        msg = conn.execute(
            "SELECT sqs_receipt_handle FROM message_log WHERE id=?",
            (row['message_id'],)
        ).fetchone()

        conn.execute("""
            UPDATE confirmations SET status='rejected', decided_at=datetime('now'),
            decided_by='user' WHERE id=?
        """, (conf_id,))
        conn.execute("""
            UPDATE message_log SET status='rejected', completed_at=datetime('now')
            WHERE id=?
        """, (row['message_id'],))

    # Delete from SQS so it's not re-delivered
    if msg and msg['sqs_receipt_handle']:
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg['sqs_receipt_handle'])

    return jsonify({'status': 'rejected'})
```

---

## Auto-Timeout

A background check (run inside `handle_pending_confirmations()`) auto-rejects
confirmations older than 24 hours:

```python
def auto_timeout_confirmations():
    """Reject pending confirmations older than 24 hours."""
    with get_db() as conn:
        stale = conn.execute("""
            SELECT c.id, c.message_id, ml.sqs_receipt_handle
            FROM confirmations c
            JOIN message_log ml ON ml.id = c.message_id
            WHERE c.status = 'pending'
              AND c.created_at < datetime('now', '-24 hours')
        """).fetchall()

        for row in stale:
            conn.execute("""
                UPDATE confirmations SET status='timed_out',
                decided_at=datetime('now'), decided_by='auto_timeout'
                WHERE id=?
            """, (row['id'],))
            conn.execute("""
                UPDATE message_log SET status='rejected',
                error_msg='auto_timeout', completed_at=datetime('now')
                WHERE id=?
            """, (row['message_id'],))
            if row['sqs_receipt_handle']:
                sqs.delete_message(QueueUrl=QUEUE_URL,
                                   ReceiptHandle=row['sqs_receipt_handle'])
```

---

## Config UI Display

The config UI homepage (`GET /`) shows a **Pending Confirmations** section at the
top of the page when any confirmations have `status='pending'`. The section is
visually highlighted (orange border / warning color in Bootstrap5).

Per confirmation row:
- Utterance text (what was said)
- Matched rule description
- Time received (relative: "5 minutes ago")
- Destination preview (e.g., "→ game_ticket: GAME")
- **Approve** button (green) — `hx-post="/api/confirmations/{id}/approve"`
- **Reject** button (red) — `hx-post="/api/confirmations/{id}/reject"`

Both buttons use HTMX to update in-place without page reload. On action, the
row fades out and the count in the section header decrements.

If no pending confirmations, the section is not rendered (hidden, not empty).

---

## Rules That Should Use requires_confirmation

Suggested defaults (user-configurable):
- Any rule that sends to an external API (`api_endpoint`) — default ON
- Any rule that runs a script (`run_script`) — default ON
- GAME ticket creation — default OFF (fast feedback loop preferred)
- File append — default OFF (low stakes)
- Slack webhook — default OFF (informational)
